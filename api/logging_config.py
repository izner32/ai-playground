import logging
import json
import sys
from datetime import datetime
from typing import Any


class StructuredFormatter(logging.Formatter):
    """
    JSON structured logging formatter for Cloud Logging compatibility.
    Cloud Logging automatically parses JSON logs and extracts fields.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id

        if hasattr(record, "duration_ms"):
            log_entry["duration_ms"] = record.duration_ms

        if hasattr(record, "status_code"):
            log_entry["status_code"] = record.status_code

        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structured logging for the application."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    request_id: str = None,
    user_id: str = None,
    duration_ms: float = None,
    status_code: int = None,
    extra_data: dict[str, Any] = None,
) -> None:
    """Log a message with additional context fields."""
    extra = {}
    if request_id:
        extra["request_id"] = request_id
    if user_id:
        extra["user_id"] = user_id
    if duration_ms is not None:
        extra["duration_ms"] = duration_ms
    if status_code is not None:
        extra["status_code"] = status_code
    if extra_data:
        extra["extra_data"] = extra_data

    logger.log(level, message, extra=extra)
