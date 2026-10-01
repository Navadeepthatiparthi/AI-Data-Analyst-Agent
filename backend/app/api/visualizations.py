from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
from app.services.dataset_registry import DatasetRegistry
from app.services.visualization_service import VisualizationService


router = APIRouter(
    prefix="/api/datasets",
    tags=["Visualizations"],
)


@router.get("/{dataset_id}/visualizations")
def get_dataset_visualizations(
    dataset_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Automatically generate chart-ready
    visualizations for a dataset.

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

    service = VisualizationService()

    try:
        return service.generate_visualizations(
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
                "Visualization generation failed: "
                f"{str(exc)}"
            ),
        )