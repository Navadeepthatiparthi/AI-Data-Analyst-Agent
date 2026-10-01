import re

import duckdb
import pandas as pd


class DuckDBEngine:
    """
    Analytical query engine built on DuckDB.

    Stores uploaded datasets as persistent DuckDB tables.
    """

    def __init__(
        self,
        database_path: str = "data/analytics.duckdb",
    ):
        self.connection = duckdb.connect(
            database=database_path
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

    @staticmethod
    def quote_identifier(
        value: str,
    ) -> str:
        """
        Safely quote a SQL identifier.
        """

        safe_value = DuckDBEngine.sanitize_identifier(
            value
        )

        return f'"{safe_value}"'

    def register_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str = "dataset",
    ) -> str:
        """
        Store a Pandas DataFrame as a persistent DuckDB table.
        """

        safe_table_name = (
            self.sanitize_identifier(
                table_name
            )
        )

        quoted_table_name = (
            self.quote_identifier(
                safe_table_name
            )
        )

        temporary_view = "__uploaded_dataframe"

        self.connection.register(
            temporary_view,
            df,
        )

        try:
            self.connection.execute(
                f"""
                CREATE OR REPLACE TABLE
                {quoted_table_name}
                AS
                SELECT *
                FROM "{temporary_view}"
                """
            )

        finally:
            self.connection.unregister(
                temporary_view
            )

        return safe_table_name

    def table_exists(
        self,
        table_name: str,
    ) -> bool:
        """
        Check whether a table exists.
        """

        safe_table_name = (
            self.sanitize_identifier(
                table_name
            )
        )

        result = self.connection.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = ?
            """,
            [safe_table_name],
        ).fetchone()

        return bool(result[0])

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

        quoted_table_name = (
            self.quote_identifier(
                safe_table_name
            )
        )

        result = self.connection.execute(
            f"DESCRIBE {quoted_table_name}"
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

        if not normalized_query:
            raise ValueError(
                "Query cannot be empty."
            )

        if not (
            normalized_query.startswith("select")
            or normalized_query.startswith("with")
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
        """
        Close the DuckDB connection.
        """

        self.connection.close()