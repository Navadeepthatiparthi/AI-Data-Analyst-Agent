from app.services.dataset_context_service import (
    DatasetContextService,
)


def test_dataset_context_real_dataset():
    service = DatasetContextService()

    datasets = service.registry.list_datasets()

    assert len(datasets) > 0

    dataset_id = datasets[0]["dataset_id"]

    context = service.get_context(
        dataset_id
    )

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


def test_dataset_context_dataset_not_found():
    service = DatasetContextService()

    try:

        service.get_context(
            "00000000-0000-0000-0000-000000000000"
        )

        assert False, (
            "Expected ValueError for missing dataset."
        )

    except ValueError as exc:

        assert str(exc) == (
            "Dataset not found."
        )