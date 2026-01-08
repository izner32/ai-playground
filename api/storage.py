import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from google.cloud import storage

logger = logging.getLogger(__name__)


class StorageService:
    """
    GCS storage service for logging queries and storing artifacts
    """

    def __init__(self):
        self.bucket_name = os.getenv("GCS_BUCKET")
        if not self.bucket_name:
            logger.warning("GCS_BUCKET not set, storage features disabled")
            self.client = None
            self.bucket = None
        else:
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)

    def health_check(self) -> bool:
        """
        Check GCS connection health
        """
        if not self.client:
            return False

        try:
            self.bucket.exists()
            return True
        except Exception as e:
            logger.error(f"GCS health check failed: {str(e)}")
            return False

    async def log_query(
        self, query: str, response: str, user_id: Optional[str] = None
    ) -> str:
        """
        Log query and response to GCS
        """
        if not self.bucket:
            logger.warning("GCS not configured, skipping log")
            return ""

        try:
            timestamp = datetime.utcnow()
            log_id = timestamp.strftime("%Y%m%d_%H%M%S_%f")

            log_data = {
                "log_id": log_id,
                "timestamp": timestamp.isoformat(),
                "user_id": user_id,
                "query": query,
                "response": response,
            }

            blob_name = f"query_logs/{timestamp.strftime('%Y/%m/%d')}/{log_id}.json"
            blob = self.bucket.blob(blob_name)

            blob.upload_from_string(
                json.dumps(log_data, indent=2), content_type="application/json"
            )

            logger.info(f"Query logged to GCS: {blob_name}")
            return log_id

        except Exception as e:
            logger.error(f"Failed to log query to GCS: {str(e)}")
            return ""

    async def get_query_log(self, log_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a query log from GCS
        """
        if not self.bucket:
            return None

        try:
            prefix = "query_logs/"
            blobs = self.bucket.list_blobs(prefix=prefix)

            for blob in blobs:
                if log_id in blob.name:
                    content = blob.download_as_string()
                    return json.loads(content)

            return None

        except Exception as e:
            logger.error(f"Failed to retrieve query log: {str(e)}")
            return None

    async def store_artifact(
        self,
        artifact_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Store arbitrary artifacts in GCS
        """
        if not self.bucket:
            raise ValueError("GCS not configured")

        try:
            blob_name = f"artifacts/{artifact_name}"
            blob = self.bucket.blob(blob_name)

            blob.upload_from_string(data, content_type=content_type)

            logger.info(f"Artifact stored: {blob_name}")
            return blob.public_url

        except Exception as e:
            logger.error(f"Failed to store artifact: {str(e)}")
            raise
