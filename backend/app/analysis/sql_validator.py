import re

import sqlglot
from sqlglot import exp


class SQLValidator:
    """
    Validates analytical SQL before it reaches DuckDB.

    Only read-only analytical queries are allowed.
    """

    FORBIDDEN_FUNCTIONS = {
        "read_csv",
        "read_csv_auto",
        "read_parquet",
        "parquet_scan",
        "glob",
        "httpfs",
    }

    @staticmethod
    def validate(query: str) -> str:
        """
        Validate and normalize a SQL query.

        Returns:
            Clean SQL query.

        Raises:
            ValueError: If the query is unsafe or unsupported.
        """

        
        # 0. Validate input

        if not isinstance(query, str):
            raise ValueError(
                "SQL query must be a string."
            )

        query = query.strip()

        if not query:
            raise ValueError(
                "SQL query cannot be empty."
            )

        
        # 1. Reject multiple SQL statements
        

        try:
            statements = sqlglot.parse(
                query,
                read="duckdb",
            )

        except sqlglot.errors.ParseError as exc:
            raise ValueError(
                f"Invalid SQL syntax: {exc}"
            ) from exc

        if len(statements) != 1:
            raise ValueError(
                "Only one SQL statement is allowed."
            )

        expression = statements[0]

        
        # 2. Only analytical SELECT queries are allowed
        

        allowed_roots = (
            exp.Select,
            exp.Union,
        )

        if not isinstance(
            expression,
            allowed_roots,
        ):
            raise ValueError(
                "Only SELECT queries are allowed."
            )

        
        # 3. Reject dangerous SQL operations
        

        forbidden_nodes = (
            exp.Insert,
            exp.Update,
            exp.Delete,
            exp.Drop,
            exp.Create,
            exp.Alter,
            exp.Command,
        )

        for node_type in forbidden_nodes:

            if expression.find(node_type):
                raise ValueError(
                    "Query contains a forbidden "
                    f"SQL operation: "
                    f"{node_type.__name__}."
                )

        
        # 4. Reject external file access

        normalized_sql = re.sub(
            r"\s+",
            " ",
            query.lower(),
        )

        for function_name in (
            SQLValidator.FORBIDDEN_FUNCTIONS
        ):

            pattern = (
                rf"\b{re.escape(function_name)}\s*\("
            )

            if re.search(
                pattern,
                normalized_sql,
            ):
                raise ValueError(
                    "External file access is "
                    "not allowed."
                )

      
        # 5. Reject dangerous keywords

        forbidden_keywords = (
            "attach ",
            "detach ",
            "install ",
            "load ",
            "pragma ",
            "copy ",
            "call ",
        )

        for keyword in forbidden_keywords:

            if normalized_sql.startswith(
                keyword
            ):
                raise ValueError(
                    f"Forbidden SQL operation: "
                    f"{keyword.strip()}."
                )

        # 6. Return normalized SQL
       
        return expression.sql(
            dialect="duckdb"
        )