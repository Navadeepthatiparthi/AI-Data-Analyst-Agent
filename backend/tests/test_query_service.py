import pytest

from app.services.dataset_registry import DatasetRegistry
from app.services.query_service import QueryService


REAL_TABLE_NAME = (
    "dataset_dff3ce8d_f503_47cc_8bea_0d64a4b63526"
)

TEST_DATASET_ID = "test-query-dataset"
TEST_USER_ID = "test-user-123"


@pytest.fixture
def query_service(tmp_path):
    """
    Create a QueryService using an isolated temporary
    dataset registry.

    The registry points to the existing real DuckDB table,
    so the tests still execute against real dataset data.
    """

    registry_path = tmp_path / "test_query_datasets.db"

    registry = DatasetRegistry(
        database_path=str(registry_path)
    )

    registry.register_dataset(
        dataset_id=TEST_DATASET_ID,
        user_id=TEST_USER_ID,
        filename="sale_samples.csv",
        file_path="data/uploads/test-query-dataset.csv",
        table_name=REAL_TABLE_NAME,
        rows=15,
        columns=7,
        uploaded_at="2026-09-26T21:00:00",
    )

    service = QueryService()

    # Use the isolated test registry instead of
    # the production datasets.db.
    service.registry = registry

    return service


def test_query_service_real_dataset(query_service):

    query = f"""
        SELECT
            Product,
            SUM(Revenue) AS total_revenue
        FROM {REAL_TABLE_NAME}
        GROUP BY Product
        ORDER BY total_revenue DESC
    """

    result = query_service.execute_query(
        dataset_id=TEST_DATASET_ID,
        query=query,
        user_id=TEST_USER_ID,
    )

    assert result["success"] is True

    assert result["dataset_id"] == TEST_DATASET_ID

    assert result["row_count"] == 4

    assert result["results"][0]["Product"] == "Laptop"

    assert result["results"][0]["total_revenue"] == 26000


def test_query_service_dataset_not_found(query_service):

    try:

        query_service.execute_query(
            dataset_id="00000000-0000-0000-0000-000000000000",
            query="SELECT 1",
            user_id=TEST_USER_ID,
        )

        assert False, "Expected ValueError"

    except ValueError as exc:

        assert str(exc) == "Dataset not found."


def test_query_service_rejects_other_dataset(query_service):

    query = """
        SELECT *
        FROM another_dataset
    """

    try:

        query_service.execute_query(
            dataset_id=TEST_DATASET_ID,
            query=query,
            user_id=TEST_USER_ID,
        )

        assert False, (
            "Expected ValueError for "
            "unauthorized dataset access."
        )

    except ValueError as exc:

        assert str(exc) == (
            "Query can only access the "
            "selected dataset."
        )


def test_query_service_rejects_empty_query(query_service):

    try:

        query_service.execute_query(
            dataset_id=TEST_DATASET_ID,
            query="   ",
            user_id=TEST_USER_ID,
        )

        assert False, (
            "Expected ValueError for empty query."
        )

    except ValueError as exc:

        assert str(exc) == (
            "SQL query cannot be empty."
        )


def test_query_service_rejects_external_file_access(
    query_service
):

    query = """
        SELECT *
        FROM read_csv_auto('secret.csv')
    """

    try:

        query_service.execute_query(
            dataset_id=TEST_DATASET_ID,
            query=query,
            user_id=TEST_USER_ID,
        )

        assert False, (
            "Expected ValueError for external file access."
        )

    except ValueError as exc:

        assert str(exc) == (
            "External file access is not allowed."
        )