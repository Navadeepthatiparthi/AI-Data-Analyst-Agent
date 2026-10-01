from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
from app.services.anomaly_service import AnomalyService
from app.services.dataset_registry import DatasetRegistry


router = APIRouter(
    prefix="/api/datasets",
    tags=["Anomaly Detection"],
)


@router.get("/{dataset_id}/anomalies")
def get_dataset_anomalies(
    dataset_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Detect numerical anomalies in a dataset
    using the IQR statistical method.

    Access is restricted to the authenticated
    user's own dataset.
    """

    registry = DatasetRegistry()

    dataset = registry.get_user_dataset(
        dataset_id=dataset_id,
        user_id=current_user.id,
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    service = AnomalyService()

    try:
        return service.detect_anomalies(
            dataset_id=dataset_id,
            user_id=current_user.id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Anomaly detection failed: "
                f"{str(exc)}"
            ),
        )