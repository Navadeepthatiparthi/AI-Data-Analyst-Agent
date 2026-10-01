from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
from app.services.dataset_registry import DatasetRegistry
from app.services.insight_service import InsightService


router = APIRouter(
    prefix="/api/datasets",
    tags=["Insights"],
)


@router.get("/{dataset_id}/insights")
def get_dataset_insights(
    dataset_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Generate automatic analytical insights
    only for a dataset owned by the authenticated user.
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

    service = InsightService()

    try:
        return service.generate_insights(
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
                f"Insight generation failed: {str(exc)}"
            ),
        )
    