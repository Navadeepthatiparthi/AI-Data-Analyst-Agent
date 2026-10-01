import pytest

from app.analysis.sql_validator import SQLValidator


def test_valid_select_query():

    query = """
        SELECT
            Product,
            SUM(Revenue) AS total_revenue
        FROM dataset_sales
        GROUP BY Product
        ORDER BY total_revenue DESC
    """

    result = SQLValidator.validate(query)

    assert "SELECT" in result.upper()
    assert "FROM" in result.upper()


def test_valid_with_query():

    query = """
        WITH revenue_summary AS (
            SELECT
                Product,
                SUM(Revenue) AS total_revenue
            FROM dataset_sales
            GROUP BY Product
        )
        SELECT *
        FROM revenue_summary
    """

    result = SQLValidator.validate(query)

    assert "WITH" in result.upper()
    assert "SELECT" in result.upper()


def test_reject_insert():

    query = """
        INSERT INTO dataset_sales
        VALUES ('Laptop', 1000)
    """

    with pytest.raises(
        ValueError,
        match="Only SELECT queries are allowed",
    ):
        SQLValidator.validate(query)


def test_reject_delete():

    query = """
        DELETE FROM dataset_sales
    """

    with pytest.raises(
        ValueError,
        match="Only SELECT queries are allowed",
    ):
        SQLValidator.validate(query)


def test_reject_drop():

    query = """
        DROP TABLE dataset_sales
    """

    with pytest.raises(
        ValueError,
        match="Only SELECT queries are allowed",
    ):
        SQLValidator.validate(query)


def test_reject_multiple_statements():

    query = """
        SELECT * FROM dataset_sales;

        DROP TABLE dataset_sales;
    """

    with pytest.raises(
        ValueError,
        match="Only one SQL statement is allowed",
    ):
        SQLValidator.validate(query)


def test_reject_external_file_access():

    query = """
        SELECT *
        FROM read_csv_auto('secret.csv')
    """

    with pytest.raises(
        ValueError,
        match="External file access is not allowed",
    ):
        SQLValidator.validate(query)