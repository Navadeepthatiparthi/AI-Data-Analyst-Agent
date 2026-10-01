from app.services.dataset_registry import DatasetRegistry


def test_dataset_registry():
    registry = DatasetRegistry(
        database_path="data/test_datasets.db"
    )

    dataset = registry.register_dataset(
        dataset_id="test-123",
        user_id="test-user-123",
        filename="sale_samples.csv",
        file_path="data/uploads/test-123.csv",
        table_name="dataset_test123",
        rows=15,
        columns=7,
        uploaded_at="2026-09-26T21:00:00",
    )

    assert dataset["dataset_id"] == "test-123"
    assert dataset["user_id"] == "test-user-123"
    assert dataset["filename"] == "sale_samples.csv"
    assert dataset["rows"] == 15
    assert dataset["columns"] == 7

    retrieved = registry.get_dataset(
        "test-123"
    )

    assert retrieved is not None
    assert retrieved["table_name"] == "dataset_test123"
    assert retrieved["user_id"] == "test-user-123"

    user_dataset = registry.get_user_dataset(
        dataset_id="test-123",
        user_id="test-user-123",
    )

    assert user_dataset is not None
    assert user_dataset["dataset_id"] == "test-123"

    wrong_user_dataset = registry.get_user_dataset(
        dataset_id="test-123",
        user_id="another-user",
    )

    assert wrong_user_dataset is None

    datasets = registry.list_datasets(
        user_id="test-user-123"
    )

    assert len(datasets) >= 1

    deleted = registry.delete_dataset(
        dataset_id="test-123",
        user_id="test-user-123",
    )

    assert deleted is True

    assert registry.get_dataset(
        "test-123"
    ) is None