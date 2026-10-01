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


def test_duckdb_persistent_table():
    engine = DuckDBEngine(
        database_path=":memory:"
    )

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

    table_name = engine.register_dataframe(
        df,
        "sales_test",
    )

    assert table_name == "sales_test"

    assert engine.table_exists(
        "sales_test"
    )

    schema = engine.get_schema(
        "sales_test"
    )

    assert len(schema) == 2

    result = engine.execute_query(
        """
        SELECT
            product,
            SUM(revenue) AS total_revenue
        FROM sales_test
        GROUP BY product
        ORDER BY total_revenue DESC
        """
    )

    assert len(result) == 2
    assert result[0]["product"] == "Laptop"
    assert result[0]["total_revenue"] == 9000

    engine.close()