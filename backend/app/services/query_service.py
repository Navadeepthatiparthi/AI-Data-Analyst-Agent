import sqlglot
from sqlglot import exp

from app.analysis.duckdb_engine import DuckDBEngine
from app.analysis.sql_validator import SQLValidator
from app.services.dataset_registry import DatasetRegistry


class QueryService:
    """
    Executes analytical queries against a registered dataset.

    The service:
    1. Resolves dataset_id to the registered DuckDB table.
    2. Verifies dataset ownership.
    3. Validates the SQL query.
    4. Ensures the query only accesses the selected dataset.
    5. Executes the validated query.
    """

    def __init__(self):
        self.registry = DatasetRegistry()

    @staticmethod
    def _validate_dataset_scope(
        query: str,
        table_name: str,
    ) -> None:
        """
        Ensure the query does not access another
        registered or external DuckDB table.

        CTE names are allowed because they are
        temporary query aliases, not physical tables.
        """

        try:
            expression = sqlglot.parse_one(
                query,
                read="duckdb",
            )

        except sqlglot.errors.ParseError as exc:
            raise ValueError(
                f"Invalid SQL syntax: {exc}"
            ) from exc

        cte_names = {
            cte.alias_or_name.lower()
            for cte in expression.find_all(exp.CTE)
            if cte.alias_or_name
        }

        allowed_table = table_name.lower()

        referenced_tables = set()

        for table in expression.find_all(exp.Table):
            referenced_name = table.name.lower()

            if referenced_name in cte_names:
                continue

            referenced_tables.add(
                referenced_name
            )

        unauthorized_tables = (
            referenced_tables - {allowed_table}
        )

        if unauthorized_tables:
            raise ValueError(
                "Query can only access the selected dataset."
            )

    def execute_query(
        self,
        dataset_id: str,
        query: str,
        user_id: str,
    ) -> dict:
        """
        Execute a validated read-only SQL query
        only against a dataset owned by the
        authenticated user.
        """

        
        # 1. Resolve dataset and verify ownership
        
        dataset = self.registry.get_user_dataset(
            dataset_id=dataset_id,
            user_id=user_id,
        )

        if dataset is None:
            raise ValueError(
                "Dataset not found."
            )

        table_name = dataset["table_name"]

        
        # 2. Validate SQL
        
        validated_query = SQLValidator.validate(
            query
        )

        # 3. Enforce dataset isolation
        
        self._validate_dataset_scope(
            validated_query,
            table_name,
        )

        
        # 4. Execute validated query

        engine = DuckDBEngine(
            database_path="data/analytics.db"
        )

        try:
            result = engine.execute_query(
                validated_query
            )

            return {
                "success": True,
                "dataset_id": dataset_id,
                "table_name": table_name,
                "row_count": len(result),
                "results": result,
            }

        finally:
            engine.close()