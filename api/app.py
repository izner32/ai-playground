from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from ai_agent import AIAgent
from database import DatabaseService
from storage import StorageService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Agent Database Query API")

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
async def process_query(request: QueryRequest):
    """
    Process user query through AI agent and return results from database
    """
    try:
        logger.info(f"Processing query: {request.query[:100]}...")

        result = await ai_agent.process_query(
            query=request.query,
            user_id=request.user_id,
            context=request.context
        )

        await storage_service.log_query(
            query=request.query,
            response=result["response"],
            user_id=request.user_id
        )

        return QueryResponse(
            response=result["response"],
            data=result.get("data"),
            query_id=result["query_id"],
            timestamp=result["timestamp"]
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
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
