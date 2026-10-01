from app.services.dataset_context_service import (
    DatasetContextService,
)
from app.services.query_service import QueryService


class InsightService:
    """
    Generates deterministic analytical insights
    from a registered dataset.
    """

    def __init__(self):
        self.context_service = DatasetContextService()
        self.query_service = QueryService()

    def generate_insights(
        self,
        dataset_id: str,
        user_id: str,
    ) -> dict:

        context = self.context_service.get_context(
            dataset_id
        )

        table_name = context["table_name"]

        schema = context["schema"]

        numeric_columns = []

        for column in schema:

            column_type = column[
                "column_type"
            ].upper()

            if any(
                numeric_type in column_type
                for numeric_type in (
                    "INTEGER",
                    "BIGINT",
                    "DOUBLE",
                    "DECIMAL",
                    "FLOAT",
                    "REAL",
                    "NUMERIC",
                )
            ):
                numeric_columns.append(
                    column["column_name"]
                )

        if not numeric_columns:
            return {
                "success": True,
                "dataset_id": dataset_id,
                "insights": [],
                "message": (
                    "No numeric columns were found "
                    "for automatic analysis."
                ),
            }

        insights = []

        for column in numeric_columns:

            query = f"""
            SELECT
                SUM("{column}") AS total,
                AVG("{column}") AS average,
                MIN("{column}") AS minimum,
                MAX("{column}") AS maximum
            FROM {table_name}
            """

            result = self.query_service.execute_query(
                dataset_id=dataset_id,
                query=query,
                user_id=user_id,
            )

            rows = result["results"]

            if not rows:
                continue

            row = rows[0]

            insights.append(
                {
                    "column": column,
                    "total": row["total"],
                    "average": row["average"],
                    "minimum": row["minimum"],
                    "maximum": row["maximum"],
                }
            )

        return {
            "success": True,
            "dataset_id": dataset_id,
            "dataset": context["filename"],
            "insights": insights,
        }