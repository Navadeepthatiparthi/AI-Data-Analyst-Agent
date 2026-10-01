from app.services.dataset_context_service import (
    DatasetContextService,
)
from app.services.query_service import QueryService


class AnomalyService:
    """
    Detects numerical anomalies using the
    Interquartile Range (IQR) method.
    """

    def __init__(self):
        self.context_service = DatasetContextService()
        self.query_service = QueryService()

    @staticmethod
    def _quote_identifier(
        identifier: str,
    ) -> str:
        """
        Safely quote a DuckDB identifier.
        """

        escaped = identifier.replace(
            '"',
            '""',
        )

        return f'"{escaped}"'

    def detect_anomalies(
        self,
        dataset_id: str,
        user_id: str,
    ) -> dict:

        context = self.context_service.get_context(
            dataset_id
        )

        table_name = context["table_name"]

        numeric_columns = []

        for column in context["schema"]:

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
                    "SMALLINT",
                    "HUGEINT",
                )
            ):
                numeric_columns.append(
                    column["column_name"]
                )

        anomalies = []

        for column in numeric_columns:

            quoted_column = (
                self._quote_identifier(column)
            )

            statistics_query = f"""
            SELECT
                quantile_cont(
                    {quoted_column},
                    0.25
                ) AS q1,
                quantile_cont(
                    {quoted_column},
                    0.75
                ) AS q3,
                MIN({quoted_column}) AS minimum,
                MAX({quoted_column}) AS maximum
            FROM {table_name}
            """

            statistics_result = (
                self.query_service.execute_query(
                    dataset_id=dataset_id,
                    query=statistics_query,
                    user_id=user_id,
                )
            )

            rows = statistics_result[
                "results"
            ]

            if not rows:
                continue

            statistics = rows[0]

            q1 = statistics["q1"]
            q3 = statistics["q3"]

            if q1 is None or q3 is None:
                continue

            iqr = q3 - q1

            lower_bound = q1 - (
                1.5 * iqr
            )

            upper_bound = q3 + (
                1.5 * iqr
            )

            anomaly_query = f"""
            SELECT
                {quoted_column} AS value
            FROM {table_name}
            WHERE
                {quoted_column} < {lower_bound}
                OR
                {quoted_column} > {upper_bound}
            ORDER BY {quoted_column}
            """

            anomaly_result = (
                self.query_service.execute_query(
                    dataset_id=dataset_id,
                    query=anomaly_query,
                    user_id=user_id,
                )
            )

            anomaly_rows = (
                anomaly_result["results"]
            )

            if anomaly_rows:

                anomalies.append(
                    {
                        "column": column,
                        "q1": q1,
                        "q3": q3,
                        "iqr": iqr,
                        "lower_bound": lower_bound,
                        "upper_bound": upper_bound,
                        "anomaly_count": len(
                            anomaly_rows
                        ),
                        "anomalies": anomaly_rows,
                    }
                )

        return {
            "success": True,
            "dataset_id": dataset_id,
            "dataset": context["filename"],
            "anomaly_count": sum(
                item["anomaly_count"]
                for item in anomalies
            ),
            "anomalies": anomalies,
        }