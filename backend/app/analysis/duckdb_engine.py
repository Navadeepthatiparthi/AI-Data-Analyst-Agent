from pathlib import Path
import re

import duckdb
import pandas as pd


class DuckDBEngine:
    """
    Analytical query engine built on DuckDB.

    The engine manages temporary analytical tables
    for uploaded datasets.
    """

    def __init__(self):
        self.connection = duckdb.connect(
            database=":memory:"
        )

    @staticmethod
    def sanitize_identifier(
        value: str,
    ) -> str:
        """
        Convert arbitrary text into a safe SQL identifier.
        """

        value = str(value)

        value = re.sub(
            r"[^a-zA-Z0-9_]",
            "_",
            value,
        )

        if not value:
            value = "dataset"

        if value[0].isdigit():
            value = f"table_{value}"

        return value.lower()

    def register_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str = "dataset",
    ) -> str:
        """
        Register a Pandas DataFrame as a DuckDB table.
        """

        safe_table_name = (
            self.sanitize_identifier(
                table_name
            )
        )

        self.connection.register(
            safe_table_name,
            df,
        )

        return safe_table_name

    def get_schema(
        self,
        table_name: str,
    ) -> list[dict]:
        """
        Return table schema information.
        """

        safe_table_name = (
            self.sanitize_identifier(
                table_name
            )
        )

        result = self.connection.execute(
            f"DESCRIBE {safe_table_name}"
        ).fetchall()

        columns = []

        for row in result:

            columns.append(
                {
                    "column_name": row[0],
                    "column_type": row[1],
                }
            )

        return columns

    def execute_query(
        self,
        query: str,
    ) -> list[dict]:
        """
        Execute a read-only analytical SQL query.

        Only SELECT and WITH queries are allowed.
        """

        normalized_query = (
            query.strip()
            .lower()
        )

        if not (
            normalized_query.startswith(
                "select"
            )
            or normalized_query.startswith(
                "with"
            )
        ):
            raise ValueError(
                "Only SELECT and WITH queries "
                "are allowed."
            )

        forbidden_keywords = [
            "insert ",
            "update ",
            "delete ",
            "drop ",
            "alter ",
            "create ",
            "truncate ",
            "attach ",
            "copy ",
            "install ",
            "load ",
        ]

        for keyword in forbidden_keywords:

            if keyword in normalized_query:

                raise ValueError(
                    "Query contains a forbidden "
                    f"SQL operation: {keyword.strip()}"
                )

        result = self.connection.execute(
            query
        ).fetchdf()

        return result.to_dict(
            orient="records"
        )

    def close(self):
        """Close the DuckDB connection."""

        self.connection.close()