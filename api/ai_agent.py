import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class AIAgent:
    """
    AI Agent that processes user queries and retrieves data from database
    """

    def __init__(self, db_service, storage_service):
        self.db_service = db_service
        self.storage_service = storage_service
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = "gemini-2.0-flash"

    async def process_query(
        self,
        query: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process user query through AI agent workflow:
        1. Understand user intent
        2. Generate database query
        3. Execute query
        4. Format response
        """
        query_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        try:
            sql_query = await self._generate_sql_query(query, context)
            logger.info(f"Generated SQL: {sql_query}")

            db_results = await self.db_service.execute_query(sql_query)
            logger.info(f"Database returned {len(db_results)} results")

            response_text = await self._generate_response(
                original_query=query, sql_query=sql_query, db_results=db_results
            )

            return {
                "query_id": query_id,
                "timestamp": timestamp,
                "response": response_text,
                "data": {
                    "results": db_results,
                    "count": len(db_results),
                    "sql_query": sql_query,
                },
            }

        except Exception as e:
            logger.error(f"Error in AI agent processing: {str(e)}")
            raise

    async def _generate_sql_query(
        self, user_query: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Use Gemini to convert natural language query to SQL
        """
        schema_info = await self.db_service.get_schema_info()

        system_prompt = f"""You are a SQL expert. Convert user queries to valid SQL.

Database Schema:
{json.dumps(schema_info, indent=2)}

Rules:
- Only generate SELECT queries (no INSERT, UPDATE, DELETE)
- Use proper SQL syntax for the database type
- Return ONLY the SQL query, no explanations
- Use appropriate WHERE clauses for filtering
- Limit results to 100 rows unless specified otherwise
"""

        user_prompt = f"""Convert this user query to SQL:

Query: {user_query}

{f"Additional context: {json.dumps(context)}" if context else ""}

Return only the SQL query."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=f"{system_prompt}\n\n{user_prompt}",
                config=types.GenerateContentConfig(
                    max_output_tokens=1024,
                ),
            )

            sql_query = response.text.strip()
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

            return sql_query

        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            raise ValueError(f"Failed to generate SQL query: {str(e)}")

    async def _generate_response(
        self, original_query: str, sql_query: str, db_results: List[Dict[str, Any]]
    ) -> str:
        """
        Use Gemini to generate natural language response from database results
        """
        system_prompt = """You are a helpful AI assistant that explains database query results to users in a clear, conversational way.

Your task:
- Summarize the key findings from the database results
- Present data in a readable format
- Highlight important insights
- Keep responses concise but informative
"""

        user_prompt = f"""User asked: "{original_query}"

SQL query executed: {sql_query}

Results ({len(db_results)} rows):
{json.dumps(db_results[:10], indent=2, default=str)}
{f"... and {len(db_results) - 10} more rows" if len(db_results) > 10 else ""}

Provide a natural language response to the user's question based on these results."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=f"{system_prompt}\n\n{user_prompt}",
                config=types.GenerateContentConfig(
                    max_output_tokens=2048,
                ),
            )

            return response.text

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Query executed successfully. Found {len(db_results)} results."
