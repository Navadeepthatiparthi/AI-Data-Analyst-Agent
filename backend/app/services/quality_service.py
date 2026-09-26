import pandas as pd


class QualityService:
    """Analyze dataset quality and detect potential issues."""

    @staticmethod
    def analyze_missing_values(
        df: pd.DataFrame,
    ) -> dict:
        """Analyze missing values by column."""

        results = {}

        for column in df.columns:

            missing_count = int(
                df[column].isna().sum()
            )

            total_count = len(df)

            percentage = (
                (missing_count / total_count) * 100
                if total_count > 0
                else 0
            )

            results[str(column)] = {
                "missing_count": missing_count,
                "missing_percentage": round(
                    percentage,
                    2,
                ),
            }

        return results

    @staticmethod
    def detect_constant_columns(
        df: pd.DataFrame,
    ) -> list[str]:
        """Find columns containing one unique value."""

        constant_columns = []

        for column in df.columns:

            unique_count = df[column].nunique(
                dropna=False
            )

            if unique_count <= 1:
                constant_columns.append(
                    str(column)
                )

        return constant_columns

    @staticmethod
    def detect_high_cardinality(
        df: pd.DataFrame,
        threshold: float = 0.90,
    ) -> list[dict]:
        """
        Detect high-cardinality categorical/text columns.

        Datetime columns are intentionally excluded because
        unique dates are normally expected in time-series data.
        """

        results = {}

        row_count = len(df)

        if row_count == 0:
            return results

        for column in df.columns:

            series = df[column]

            # Datetime columns are not treated as
            # high-cardinality problems.
            if pd.api.types.is_datetime64_any_dtype(
                series
            ):
                continue

            # Numeric columns are also excluded from
            # generic cardinality warnings.
            if pd.api.types.is_numeric_dtype(
                series
            ):
                continue

            unique_count = series.nunique(
                dropna=True
            )

            ratio = unique_count / row_count

            if ratio >= threshold:

                results[str(column)] = {
                    "unique_values": int(
                        unique_count
                    ),
                    "unique_ratio": round(
                        ratio,
                        4,
                    ),
                    "severity": (
                        "medium"
                        if ratio < 0.99
                        else "high"
                    ),
                }

        return results

    @staticmethod
    def detect_outliers(
        df: pd.DataFrame,
    ) -> dict:
        """
        Detect numerical outliers using the IQR method.
        """

        results = {}

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns

        for column in numeric_columns:

            series = df[column].dropna()

            if series.empty:
                continue

            q1 = float(
                series.quantile(0.25)
            )

            q3 = float(
                series.quantile(0.75)
            )

            iqr = q3 - q1

            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            outliers = series[
                (series < lower_bound)
                | (series > upper_bound)
            ]

            results[str(column)] = {
                "outlier_count": int(
                    len(outliers)
                ),
                "lower_bound": round(
                    lower_bound,
                    4,
                ),
                "upper_bound": round(
                    upper_bound,
                    4,
                ),
                "outlier_percentage": round(
                    (
                        len(outliers)
                        / len(series)
                    )
                    * 100,
                    2,
                ),
            }

        return results

    @staticmethod
    def calculate_quality_score(
        df: pd.DataFrame,
    ) -> float:
        """
        Calculate an initial dataset quality score.

        Score ranges from 0 to 100.

        Missing values and duplicate rows affect
        the score. Outliers are reported separately
        because an outlier is not automatically an error.
        """

        if df.empty:
            return 0.0

        total_cells = (
            df.shape[0] * df.shape[1]
        )

        if total_cells == 0:
            return 0.0

        missing_cells = int(
            df.isna().sum().sum()
        )

        duplicate_rows = int(
            df.duplicated().sum()
        )

        rows = len(df)

        missing_ratio = (
            missing_cells / total_cells
        )

        duplicate_ratio = (
            duplicate_rows / rows
            if rows > 0
            else 0
        )

        score = 100.0

        # Missing-value penalty
        score -= missing_ratio * 40

        # Duplicate-row penalty
        score -= duplicate_ratio * 30

        return round(
            max(0.0, min(100.0, score)),
            2,
        )

    @staticmethod
    def generate_warnings(
        df: pd.DataFrame,
        missing_values: dict,
        constant_columns: list[str],
        high_cardinality: dict,
        outliers: dict,
    ) -> list[dict]:
        """Generate human-readable quality warnings."""

        warnings = []

        # Missing-value warnings
        for column, info in missing_values.items():

            percentage = info[
                "missing_percentage"
            ]

            if percentage > 20:

                warnings.append(
                    {
                        "type": "missing_values",
                        "column": column,
                        "severity": "high",
                        "message": (
                            f"{column} has "
                            f"{percentage}% missing values."
                        ),
                    }
                )

            elif percentage > 5:

                warnings.append(
                    {
                        "type": "missing_values",
                        "column": column,
                        "severity": "medium",
                        "message": (
                            f"{column} has "
                            f"{percentage}% missing values."
                        ),
                    }
                )

        # Constant columns
        for column in constant_columns:

            warnings.append(
                {
                    "type": "constant_column",
                    "column": column,
                    "severity": "medium",
                    "message": (
                        f"{column} contains "
                        "only one unique value."
                    ),
                }
            )

        # High cardinality
        for column, info in high_cardinality.items():

            warnings.append(
                {
                    "type": "high_cardinality",
                    "column": column,
                    "severity": info["severity"],
                    "message": (
                        f"{column} contains "
                        f"{info['unique_ratio'] * 100:.1f}% "
                        "unique values."
                    ),
                }
            )

        # Outliers
        for column, info in outliers.items():

            if info["outlier_count"] > 0:

                warnings.append(
                    {
                        "type": "outlier",
                        "column": column,
                        "severity": "low",
                        "message": (
                            f"{column} contains "
                            f"{info['outlier_count']} "
                            "potential outlier(s)."
                        ),
                    }
                )

        return warnings

    @staticmethod
    def analyze_quality(
        df: pd.DataFrame,
    ) -> dict:
        """Run the complete data-quality analysis."""

        missing_values = (
            QualityService.analyze_missing_values(
                df
            )
        )

        constant_columns = (
            QualityService.detect_constant_columns(
                df
            )
        )

        high_cardinality = (
            QualityService.detect_high_cardinality(
                df
            )
        )

        outliers = (
            QualityService.detect_outliers(
                df
            )
        )

        warnings = (
            QualityService.generate_warnings(
                df,
                missing_values,
                constant_columns,
                high_cardinality,
                outliers,
            )
        )

        return {
            "quality_score": (
                QualityService.calculate_quality_score(
                    df
                )
            ),
            "missing_values": missing_values,
            "duplicate_rows": int(
                df.duplicated().sum()
            ),
            "constant_columns": (
                constant_columns
            ),
            "high_cardinality_columns": (
                high_cardinality
            ),
            "outliers": outliers,
            "warnings": warnings,
        }