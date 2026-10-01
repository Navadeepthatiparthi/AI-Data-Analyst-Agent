import sqlite3

from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
from app.main import app
from app.services.dataset_registry import DatasetRegistry


client = TestClient(app)

TEST_USER_ID = "test-context-user"


def test_dataset_context_api_real_dataset():
    registry = DatasetRegistry()

    datasets = registry.list_datasets()

    assert len(datasets) > 0

    dataset_id = datasets[0]["dataset_id"]

    # Temporarily assign the dataset to the test user.
    connection = sqlite3.connect(
        "data/datasets.db"
    )

    try:
        connection.execute(
            """
            UPDATE datasets
            SET user_id = ?
            WHERE dataset_id = ?
            """,
            (
                TEST_USER_ID,
                dataset_id,
            ),
        )

        connection.commit()

        def override_current_user():
            return UserResponse(
                id=TEST_USER_ID,
                email="test-context@example.com",
                full_name="Context Test User",
            )

        app.dependency_overrides[
            get_current_user
        ] = override_current_user

        response = client.get(
            f"/api/datasets/{dataset_id}/context"
        )

        assert response.status_code == 200

        body = response.json()

        assert body["success"] is True

        context = body["context"]

        assert context["dataset_id"] == dataset_id

        assert context["filename"]

        assert context["table_name"]

        assert context["rows"] > 0

        assert context["columns"] > 0

        assert isinstance(
            context["schema"],
            list,
        )

        assert len(context["schema"]) > 0

    finally:
        # Restore the original pre-authentication state.
        connection.execute(
            """
            UPDATE datasets
            SET user_id = NULL
            WHERE dataset_id = ?
            """,
            (dataset_id,),
        )

        connection.commit()
        connection.close()

        app.dependency_overrides.pop(
            get_current_user,
            None,
        )


def test_dataset_context_api_missing_dataset():
    def override_current_user():
        return UserResponse(
            id=TEST_USER_ID,
            email="test-context@example.com",
            full_name="Context Test User",
        )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user

    try:
        response = client.get(
            "/api/datasets/"
            "00000000-0000-0000-0000-000000000000"
            "/context"
        )

        assert response.status_code == 404

        body = response.json()

        assert body["detail"] == (
            "Dataset not found."
        )

    finally:
        app.dependency_overrides.pop(
            get_current_user,
            None,
        )