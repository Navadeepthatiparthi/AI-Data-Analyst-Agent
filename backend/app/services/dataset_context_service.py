from app.analysis.duckdb_engine import DuckDBEngine
from app.services.dataset_registry import DatasetRegistry


class DatasetContextService:
    """
    Builds a dynamic analytical context for a registered dataset.

    The context is generated from the actual dataset stored in
    DuckDB and the persistent dataset registry.

    No dataset IDs, table names, or column names are hardcoded.
    """

    def __init__(self):
        self.registry = DatasetRegistry()

    def get_context(
        self,
        dataset_id: str,
    ) -> dict:
        """
        Build AI-ready context for a specific dataset.

        The dataset_id is resolved through the persistent registry.
        """

        dataset = self.registry.get_dataset(
            dataset_id
        )

        if dataset is None:
            raise ValueError(
                "Dataset not found."
            )

        table_name = dataset["table_name"]

        engine = DuckDBEngine(
            database_path="data/analytics.db"
        )

        try:
            schema = engine.get_schema(
                table_name
            )

            return {
                "dataset_id": dataset["dataset_id"],
                "filename": dataset["filename"],
                "table_name": table_name,
                "rows": dataset["rows"],
                "columns": dataset["columns"],
                "uploaded_at": dataset["uploaded_at"],
                "schema": schema,
            }

        finally:
            engine.close()