import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from ai_agent import AIAgent
from database import DatabaseService
from storage import StorageService
from logging_config import setup_logging, get_logger, log_with_context
from middleware import RequestTracingMiddleware

setup_logging(os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

app = FastAPI(title="AI Agent Database Query API")
app.add_middleware(RequestTracingMiddleware)

db_service = DatabaseService()
storage_service = StorageService()
ai_agent = AIAgent(db_service=db_service, storage_service=storage_service)


class QueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    response: str
    data: Optional[Dict[str, Any]] = None
    query_id: str
    timestamp: str


@app.get("/")
async def root():
    return {"message": "AI Agent Database Query API", "status": "running"}


@app.get("/health")
async def health_check():
    try:
        db_healthy = await db_service.health_check()
        storage_healthy = storage_service.health_check()

        return {
            "status": "healthy" if db_healthy and storage_healthy else "degraded",
            "database": "ok" if db_healthy else "error",
            "storage": "ok" if storage_healthy else "error",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.post("/query", response_model=QueryResponse)
async def process_query(request_body: QueryRequest, request: Request):
    """
    Process user query through AI agent and return results from database
    """
    request_id = getattr(request.state, "request_id", "unknown")

    try:
        log_with_context(
            logger,
            logging.INFO,
            f"Processing query: {request_body.query[:100]}...",
            request_id=request_id,
            user_id=request_body.user_id,
        )

        result = await ai_agent.process_query(
            query=request_body.query,
            user_id=request_body.user_id,
            context=request_body.context
        )

        await storage_service.log_query(
            query=request_body.query,
            response=result["response"],
            user_id=request_body.user_id
        )

        log_with_context(
            logger,
            logging.INFO,
            "Query processed successfully",
            request_id=request_id,
            user_id=request_body.user_id,
            extra_data={"query_id": result["query_id"], "result_count": result.get("data", {}).get("count", 0)},
        )

        return QueryResponse(
            response=result["response"],
            data=result.get("data"),
            query_id=result["query_id"],
            timestamp=result["timestamp"]
        )

    except ValueError as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Validation error: {str(e)}",
            request_id=request_id,
            user_id=request_body.user_id,
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log_with_context(
            logger,
            logging.ERROR,
            f"Error processing query: {str(e)}",
            request_id=request_id,
            user_id=request_body.user_id,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/queries/{query_id}")
async def get_query_result(query_id: str):
    """
    Retrieve a previously executed query result
    """
    try:
        result = await storage_service.get_query_log(query_id)
        if not result:
            raise HTTPException(status_code=404, detail="Query not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
