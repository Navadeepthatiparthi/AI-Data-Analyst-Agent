from app.services.dataset_context_service import (
    DatasetContextService,
)
from app.services.query_service import QueryService


class VisualizationService:
    """
    Automatically generates chart-ready analytical
    data based on the structure of a dataset.
    """

    NUMERIC_TYPES = (
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

    TEXT_TYPES = (
        "VARCHAR",
        "TEXT",
        "STRING",
    )

    DATE_TYPES = (
        "DATE",
        "TIMESTAMP",
        "DATETIME",
    )

    def __init__(self):
        self.context_service = DatasetContextService()
        self.query_service = QueryService()

    @staticmethod
    def _quote_identifier(
        identifier: str,
    ) -> str:
        escaped = identifier.replace(
            '"',
            '""',
        )

        return f'"{escaped}"'

    @staticmethod
    def _looks_like_date_column(
        column_name: str,
    ) -> bool:
        """
        Detect common date/time column names even when
        CSV ingestion represents them as VARCHAR.
        """

        name = column_name.lower().strip()

        date_keywords = (
            "date",
            "time",
            "timestamp",
            "datetime",
            "created_at",
            "updated_at",
            "order_date",
            "sale_date",
            "transaction_date",
        )

        return any(
            keyword in name
            for keyword in date_keywords
        )

    def _get_column_types(
        self,
        schema: list,
    ) -> tuple:
        """
        Separate dataset columns into
        categorical, numeric, and date columns.
        """

        categorical_columns = []
        numeric_columns = []
        date_columns = []

        for column in schema:

            name = column["column_name"]

            column_type = column[
                "column_type"
            ].upper()

            if any(
                data_type in column_type
                for data_type in self.NUMERIC_TYPES
            ):
                numeric_columns.append(name)

            elif any(
                data_type in column_type
                for data_type in self.DATE_TYPES
            ):
                date_columns.append(name)

            elif self._looks_like_date_column(name):
                date_columns.append(name)

            elif any(
                data_type in column_type
                for data_type in self.TEXT_TYPES
            ):
                categorical_columns.append(name)

        return (
            categorical_columns,
            numeric_columns,
            date_columns,
        )

    def generate_visualizations(
        self,
        dataset_id: str,
        user_id: str,
    ) -> dict:
        """
        Generate automatic chart specifications
        for a registered dataset.
        """

        context = self.context_service.get_context(
            dataset_id
        )

        table_name = context["table_name"]
        schema = context["schema"]

        (
            categorical_columns,
            numeric_columns,
            date_columns,
        ) = self._get_column_types(schema)

        charts = []

        
        # 1. Categorical + Numeric → Bar Charts
        

        if categorical_columns and numeric_columns:

            category_column = (
                categorical_columns[0]
            )

            quoted_category = (
                self._quote_identifier(
                    category_column
                )
            )

            for numeric_column in numeric_columns[:3]:

                quoted_numeric = (
                    self._quote_identifier(
                        numeric_column
                    )
                )

                query = f"""
                SELECT
                    {quoted_category} AS category,
                    SUM({quoted_numeric}) AS value
                FROM {table_name}
                WHERE
                    {quoted_category} IS NOT NULL
                    AND {quoted_numeric} IS NOT NULL
                GROUP BY {quoted_category}
                ORDER BY value DESC
                LIMIT 10
                """

                result = (
                    self.query_service.execute_query(
                        dataset_id=dataset_id,
                        query=query,
                        user_id=user_id,
                    )
                )

                rows = result["results"]

                charts.append(
                    {
                        "chart_id": (
                            f"{numeric_column.lower()}"
                            "_by_"
                            f"{category_column.lower()}"
                        ),
                        "type": "bar",
                        "title": (
                            f"{numeric_column} by "
                            f"{category_column}"
                        ),
                        "x_axis": category_column,
                        "y_axis": numeric_column,
                        "data": rows,
                    }
                )

        
        # 2. Date + Numeric → Line Charts
        

        if date_columns and numeric_columns:

            date_column = date_columns[0]

            quoted_date = (
                self._quote_identifier(
                    date_column
                )
            )

            for numeric_column in numeric_columns[:3]:

                quoted_numeric = (
                    self._quote_identifier(
                        numeric_column
                    )
                )

                query = f"""
                SELECT
                    TRY_CAST(
                        {quoted_date} AS DATE
                    ) AS date,
                    SUM({quoted_numeric}) AS value
                FROM {table_name}
                WHERE
                    {quoted_date} IS NOT NULL
                    AND {quoted_numeric} IS NOT NULL
                    AND TRY_CAST(
                        {quoted_date} AS DATE
                    ) IS NOT NULL
                GROUP BY
                    TRY_CAST(
                        {quoted_date} AS DATE
                    )
                ORDER BY date
                LIMIT 100
                """

                result = (
                    self.query_service.execute_query(
                        dataset_id=dataset_id,
                        query=query,
                        user_id=user_id,
                    )
                )

                rows = result["results"]

                charts.append(
                    {
                        "chart_id": (
                            f"{numeric_column.lower()}"
                            "_over_time"
                        ),
                        "type": "line",
                        "title": (
                            f"{numeric_column} over time"
                        ),
                        "x_axis": date_column,
                        "y_axis": numeric_column,
                        "data": rows,
                    }
                )

        return {
            "success": True,
            "dataset_id": dataset_id,
            "dataset": context["filename"],
            "chart_count": len(charts),
            "charts": charts,
        }