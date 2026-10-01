import re

import sqlglot
from sqlglot import exp

from app.analysis.sql_validator import SQLValidator
from app.services.conversation_context_service import (
    ConversationContextService,
)
from app.services.dataset_context_service import (
    DatasetContextService,
)
from app.services.llm_service import LLMService


class SQLGenerationService:
    """
    Converts a natural-language question into safe,
    dataset-specific analytical SQL.

    Supports conversational follow-up questions
    using recent query history.
    """

    def __init__(self):
        self.context_service = DatasetContextService()
        self.conversation_service = (
            ConversationContextService()
        )
        self.llm_service = LLMService()

    def build_prompt(
        self,
        dataset_id: str,
        question: str,
        conversation_context: str = "",
    ) -> str:
        """
        Build an LLM prompt using dataset context
        and recent conversation history.
        """

        if not isinstance(question, str):
            raise ValueError(
                "Question must be a string."
            )

        question = question.strip()

        if not question:
            raise ValueError(
                "Question cannot be empty."
            )

        context = self.context_service.get_context(
            dataset_id
        )

        schema_lines = []

        for column in context["schema"]:
            schema_lines.append(
                f'- {column["column_name"]}: '
                f'{column["column_type"]}'
            )

        schema = "\n".join(
            schema_lines
        )

        if not conversation_context:
            conversation_context = (
                "No previous analytical questions "
                "are available."
            )

        return f"""
You are a precise analytical SQL generation assistant.

Generate ONE read-only DuckDB SQL query that answers
the user's current question using ONLY the dataset
provided below.

IMPORTANT:
The table name below is the ONLY table you are allowed to use.

Dataset:
{context["filename"]}

EXACT TABLE NAME:
{context["table_name"]}

Rows:
{context["rows"]}

Columns:
{context["columns"]}

Schema:
{schema}

RECENT CONVERSATION HISTORY:
{conversation_context}

CONVERSATIONAL RULES:
- Use previous questions and results to understand
  follow-up references such as:
  "it", "its", "that product", "the second one",
  "the previous result", or "compare it".
- Resolve references using the most recent relevant
  conversation result.
- Do NOT blindly copy the previous SQL.
- Generate a new SQL query that answers the CURRENT question.
- If the current question refers to a product or value
  from a previous result, use that value in the new query.
- The current question has priority over previous questions.

STRICT SQL RULES:
- Generate exactly ONE SQL statement.
- Generate SELECT-based analytical SQL only.
- You MUST use this exact table name:
  {context["table_name"]}
- Do NOT invent, modify, shorten, or replace the table name.
- Do NOT reference any other table.
- Use ONLY columns from the provided schema.
- Do NOT use external files.
- Do NOT use read_csv.
- Do NOT use read_csv_auto.
- Do NOT use read_parquet.
- Do NOT use parquet_scan.
- Do NOT use glob.
- Do NOT use httpfs.
- Do NOT use INSERT.
- Do NOT use UPDATE.
- Do NOT use DELETE.
- Do NOT use DROP.
- Do NOT use CREATE.
- Do NOT use ALTER.
- Do NOT use ATTACH.
- Do NOT use DETACH.
- Do NOT use INSTALL.
- Do NOT use LOAD.
- Do NOT use COPY.
- Do NOT use CALL.
- Do NOT use PRAGMA.
- Do NOT modify the dataset.
- Use DuckDB-compatible SQL.
- Return ONLY the SQL query.
- Do NOT explain the SQL.
- Do NOT provide reasoning.
- Do NOT write natural language.
- Do NOT use markdown code fences.

Example:
SELECT Product
FROM {context["table_name"]}
ORDER BY Revenue DESC
LIMIT 1;

User's current question:
{question}
""".strip()

    async def generate_sql(
        self,
        dataset_id: str,
        question: str,
    ) -> str:
        """
        Generate and validate SQL for a real registered dataset.
        """

        context = self.context_service.get_context(
            dataset_id
        )

        conversation_context = (
            self.conversation_service.get_context(
                dataset_id=dataset_id,
                limit=5,
            )
        )

        prompt = self.build_prompt(
            dataset_id=dataset_id,
            question=question,
            conversation_context=conversation_context,
        )

        generated_sql = await self.llm_service.generate(
            prompt
        )

        sql = self._clean_sql(
            generated_sql
        )

        validated_sql = SQLValidator.validate(
            sql
        )

        self._validate_dataset_table(
            validated_sql,
            context["table_name"],
        )

        return validated_sql

    @staticmethod
    def _clean_sql(
        sql: str,
    ) -> str:
        """
        Remove common LLM formatting without
        changing the SQL itself.
        """

        if not isinstance(sql, str):
            raise ValueError(
                "Generated SQL must be a string."
            )

        sql = sql.strip()

        if not sql:
            raise ValueError(
                "LLM returned empty SQL."
            )

        sql = re.sub(
            r"^```(?:sql|duckdb)?\s*",
            "",
            sql,
            flags=re.IGNORECASE,
        )

        sql = re.sub(
            r"\s*```$",
            "",
            sql,
        )

        sql = sql.strip()

        if not sql:
            raise ValueError(
                "Generated SQL is empty."
            )

        return sql

    @staticmethod
    def _validate_dataset_table(
        sql: str,
        expected_table: str,
    ) -> None:
        """
        Ensure the generated SQL references only
        the actual registered dataset table.
        """

        try:
            expression = sqlglot.parse_one(
                sql,
                read="duckdb",
            )

        except sqlglot.errors.ParseError as exc:
            raise ValueError(
                f"Generated SQL could not be parsed: {exc}"
            ) from exc

        expected_table = (
            expected_table.strip().lower()
        )

        tables = list(
            expression.find_all(exp.Table)
        )

        if not tables:
            raise ValueError(
                "Generated SQL does not reference "
                "the registered dataset table."
            )

        for table in tables:
            actual_table = (
                table.name.strip().lower()
            )

            if actual_table != expected_table:
                raise ValueError(
                    "Generated SQL references "
                    "an unauthorized dataset table. "
                    f"Expected: '{expected_table}', "
                    f"Generated: '{actual_table}'. "
                    f"SQL: {sql}"
                )