import os
import logging
from typing import List, Dict, Any
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.pool import NullPool
from google.cloud.sql.connector import Connector

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Database service supporting both Cloud SQL and direct connections
    """

    def __init__(self):
        self.db_type = os.getenv("DB_TYPE", "cloudsql")  # cloudsql or postgres
        self.engine = None
        self.connector = None
        self._initialize_connection()

    def _initialize_connection(self):
        """
        Initialize database connection based on configuration
        """
        try:
            if self.db_type == "cloudsql":
                self._init_cloud_sql()
            else:
                self._init_postgres()

            logger.info(f"Database connection initialized: {self.db_type}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def _init_cloud_sql(self):
        """
        Initialize Cloud SQL connection using Cloud SQL Python Connector
        """
        instance_connection_name = os.getenv("CLOUD_SQL_INSTANCE")
        db_user = os.getenv("DB_USER", "postgres")
        db_pass = os.getenv("DB_PASS")
        db_name = os.getenv("DB_NAME", "postgres")

        if not instance_connection_name:
            raise ValueError("CLOUD_SQL_INSTANCE environment variable required")

        self.connector = Connector()

        def getconn():
            conn = self.connector.connect(
                instance_connection_name,
                "pg8000",
                user=db_user,
                password=db_pass,
                db=db_name,
            )
            return conn

        self.engine = create_engine(
            "postgresql+pg8000://",
            creator=getconn,
            poolclass=NullPool,
        )

    def _init_postgres(self):
        """
        Initialize direct PostgreSQL connection
        """
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable required")

        self.engine = create_engine(database_url, poolclass=NullPool)

    async def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results as list of dictionaries
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql_query))

                if result.returns_rows:
                    columns = result.keys()
                    rows = [dict(zip(columns, row)) for row in result.fetchall()]
                    return rows
                else:
                    return []

        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            raise ValueError(f"Failed to execute query: {str(e)}")

    async def get_schema_info(self) -> Dict[str, Any]:
        """
        Get database schema information for AI agent
        """
        try:
            inspector = inspect(self.engine)
            schemas = {}

            for table_name in inspector.get_table_names():
                columns = []
                for column in inspector.get_columns(table_name):
                    columns.append(
                        {
                            "name": column["name"],
                            "type": str(column["type"]),
                            "nullable": column["nullable"],
                        }
                    )

                schemas[table_name] = {
                    "columns": columns,
                    "primary_key": inspector.get_pk_constraint(table_name),
                }

            return schemas

        except Exception as e:
            logger.error(f"Error getting schema: {str(e)}")
            return {}

    async def health_check(self) -> bool:
        """
        Check database connection health
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

    def close(self):
        """
        Close database connections
        """
        if self.engine:
            self.engine.dispose()
        if self.connector:
            self.connector.close()
