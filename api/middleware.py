import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

from logging_config import log_with_context

logger = logging.getLogger(__name__)


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request tracing and metrics collection.
    Adds request ID, logs request/response details, and tracks latency.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.perf_counter()

        log_with_context(
            logger,
            logging.INFO,
            f"Request started: {request.method} {request.url.path}",
            request_id=request_id,
            extra_data={
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
            },
        )

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            log_with_context(
                logger,
                logging.INFO,
                f"Request completed: {request.method} {request.url.path}",
                request_id=request_id,
                duration_ms=round(duration_ms, 2),
                status_code=response.status_code,
            )

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time-Ms"] = str(round(duration_ms, 2))

            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            log_with_context(
                logger,
                logging.ERROR,
                f"Request failed: {request.method} {request.url.path} - {str(e)}",
                request_id=request_id,
                duration_ms=round(duration_ms, 2),
                status_code=500,
            )
            raise
