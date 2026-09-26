import pandas as pd

from app.analysis.duckdb_engine import DuckDBEngine


def test_duckdb_basic_query():

    df = pd.DataFrame(
        {
            "product": [
                "Laptop",
                "Phone",
                "Laptop",
            ],
            "revenue": [
                5000,
                3000,
                4000,
            ],
        }
    )

    engine = DuckDBEngine()

    table_name = engine.register_dataframe(
        df,
        "sales",
    )

    result = engine.execute_query(
        f"""
        SELECT
            product,
            SUM(revenue) AS total_revenue
        FROM {table_name}
        GROUP BY product
        ORDER BY total_revenue DESC
        """
    )

    assert len(result) == 2
    assert result[0]["product"] == "Laptop"

    engine.close()