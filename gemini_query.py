import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
import pandas as pd
import logging
from typing import Dict, Any, Optional
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiQueryEngine:
    def __init__(self, database_manager):
        self.db_manager = database_manager
        self.api_key = os.getenv('GEMINI_API_KEY', '')

        if not self.api_key:
            logger.warning("Gemini API key not found in environment variables")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')

        self.schema_info = self.db_manager.get_schema_info()

    def process_query(self, user_query: str) -> Dict[str, Any]:
        try:
            sql_query = self._generate_sql_query(user_query)

            if not sql_query:
                return {
                    'error': 'Failed to generate SQL query',
                    'sql_query': None,
                    'data': None,
                    'insights': None
                }

            data = self.db_manager.execute_query(sql_query)
            insights = self._generate_insights(user_query, data, sql_query)

            return {
                'sql_query': sql_query,
                'data': data,
                'insights': insights,
                'error': None
            }

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'error': str(e),
                'sql_query': None,
                'data': None,
                'insights': None
            }

    def _generate_sql_query(self, user_query: str) -> Optional[str]:
        try:
            schema_context = self._create_schema_context()

            prompt = f"""
You are a senior PostgreSQL data analyst. Convert the user's query into a precise, valid SQL SELECT query.

Database Schema:
{schema_context}

Instructions:
- Only return a single SQL SELECT query. Do not return explanations, markdown, or code formatting.
- You can use multiple tables if necessary. Use JOINs when columns across tables are related (e.g., foreign keys or shared IDs).
- Prefer INNER JOIN unless the logic clearly needs LEFT JOIN.
- Use aggregations (SUM, AVG, COUNT, MAX, MIN) where appropriate.
- Use WHERE clauses, GROUP BY, ORDER BY, and LIMIT as needed.
- Always select human-readable fields (e.g., campaign name) alongside IDs where available.
- Use aliases to improve readability (e.g., `c.name AS campaign_name`).
- When filtering by month or year, assume timestamp fields are stored as strings in the format 'YYYY-MM-DDTHH:MI:SS' or 'YYYY-MM-DD'.

    ✅ For campaign or ad timestamps like `created_time`, `start_time`, `stop_time`:
    Use: 
        DATE_PART('month', TO_TIMESTAMP(field, 'YYYY-MM-DD"T"HH24:MI:SS')) = MM
        DATE_PART('year', TO_TIMESTAMP(field, 'YYYY-MM-DD"T"HH24:MI:SS')) = YYYY

    ✅ For ad_insights fields like `date_start` or `date_stop` (which are already stored as DATE type):
    Use:
        DATE_PART('month', date_start) = MM
        DATE_PART('year', date_start) = YYYY

- Do not use UPDATE, DELETE, INSERT, or CREATE statements — SELECT only.

User Query: {user_query}

SQL Query:
"""

            if hasattr(self, 'model'):
                response = self.model.generate_content(prompt)
                return self._clean_sql_response(response.text)
            else:
                return None

        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            return None

    def _create_schema_context(self) -> str:
        context = ""
        for table_name, table_info in self.schema_info.items():
            context += f"\nTable: {table_info['table']}\n"
            context += f"Description: {table_info['description']}\n"
            context += f"Columns: {', '.join(table_info['columns'])}\n"
        return context

    def _clean_sql_response(self, response: str) -> str:
        response = re.sub(r'```sql\n?', '', response)
        response = re.sub(r'```\n?', '', response)
        response = response.strip()
        if not response.endswith(';'):
            response += ';'

        # Remove incorrect TO_DATE usage on DATE columns
        response = re.sub(r"TO_DATE\((date_start|date_stop),\s*'YYYY-MM-DD'\)", r"\1", response)

        return response

    def _generate_insights(self, user_query: str, data: pd.DataFrame, sql_query: str) -> str:
        try:
            if data is None or data.empty:
                return "No data found for the given query."

            data_summary = self._create_data_summary(data)

            prompt = f"""
Analyze the following SQL output and give business-focused insights.

User Query: {user_query}
SQL Query: {sql_query}

Data Summary:
{data_summary}

Instructions:
- Focus on key findings, patterns, or concerns
- Keep it under 200 words
- Mention trends, totals, averages, or outliers
"""

            if hasattr(self, 'model'):
                response = self.model.generate_content(prompt)
                return response.text
            else:
                return "AI insights unavailable (Gemini model not initialized)."

        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return "Error generating insights."

    def _create_data_summary(self, data: pd.DataFrame) -> str:
        summary = f"Rows: {len(data)}, Columns: {len(data.columns)}\n"
        summary += f"Columns: {', '.join(data.columns)}\n"
        numeric_cols = data.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary += "Numeric Columns Summary:\n"
            for col in numeric_cols[:3]:
                summary += f"{col}: min={data[col].min()}, max={data[col].max()}, mean={data[col].mean():.2f}\n"
        return summary
