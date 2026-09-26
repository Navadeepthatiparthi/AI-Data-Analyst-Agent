from pathlib import Path

import pandas as pd


ALLOWED_EXTENSIONS = {".csv", ".xlsx"}


class DatasetService:
    """Handles loading and profiling uploaded datasets."""

    @staticmethod
    def load_dataset(file_path: str) -> pd.DataFrame:
        """Load a CSV or Excel file."""

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                "Dataset file does not exist."
            )

        extension = path.suffix.lower()

        if extension == ".csv":
            return pd.read_csv(path)

        if extension == ".xlsx":
            return pd.read_excel(path)

        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    @staticmethod
    def detect_semantic_type(series: pd.Series) -> str:
        """Detect the semantic type of a column."""

        non_null = series.dropna()

        if non_null.empty:
            return "unknown"

        # Boolean
        if pd.api.types.is_bool_dtype(series):
            return "boolean"

        # Numeric
        if pd.api.types.is_numeric_dtype(series):
            return "numeric"

        # Already datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"

        # Pandas categorical dtype
        if isinstance(series.dtype, pd.CategoricalDtype):
            return "categorical"

        # String columns
        if pd.api.types.is_string_dtype(series):

            # Try datetime detection
            try:
                parsed = pd.to_datetime(
                    non_null,
                    errors="coerce",
                    format="mixed",
                )

                parse_success_rate = parsed.notna().mean()

                if parse_success_rate >= 0.90:
                    return "datetime"

            except (ValueError, TypeError):
                pass

            # Categorical vs text
            unique_count = non_null.nunique()
            total_count = len(non_null)

            unique_ratio = unique_count / total_count

            if unique_ratio <= 0.50:
                return "categorical"

            return "text"

        return "text"

    @staticmethod
    def profile_dataset(df: pd.DataFrame) -> dict:
        """Generate a structured profile of the dataset."""

        columns = []

        for column in df.columns:

            series = df[column]

            semantic_type = (
                DatasetService.detect_semantic_type(series)
            )

            column_info = {
                "name": str(column),
                "dtype": str(series.dtype),
                "semantic_type": semantic_type,
                "missing_values": int(
                    series.isna().sum()
                ),
                "missing_percentage": round(
                    float(
                        series.isna().mean() * 100
                    ),
                    2,
                ),
                "unique_values": int(
                    series.nunique(dropna=True)
                ),
            }

            # Numeric statistics
            if semantic_type == "numeric":

                column_info["statistics"] = {
                    "minimum": float(series.min()),
                    "maximum": float(series.max()),
                    "mean": round(
                        float(series.mean()),
                        4,
                    ),
                    "median": float(
                        series.median()
                    ),
                }

            # Datetime range
            elif semantic_type == "datetime":

                parsed_dates = pd.to_datetime(
                    series,
                    errors="coerce",
                    format="mixed",
                )

                valid_dates = parsed_dates.dropna()

                if not valid_dates.empty:

                    column_info["date_range"] = {
                        "minimum": (
                            valid_dates.min().isoformat()
                        ),
                        "maximum": (
                            valid_dates.max().isoformat()
                        ),
                    }

            columns.append(column_info)

        return {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "duplicate_rows": int(
                df.duplicated().sum()
            ),
            "total_missing_values": int(
                df.isna().sum().sum()
            ),
            "columns_info": columns,
        }