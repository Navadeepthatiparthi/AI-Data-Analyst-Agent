from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
from app.services.dataset_registry import DatasetRegistry
from app.services.query_history_service import QueryHistoryService


router = APIRouter(
    prefix="/api/datasets",
    tags=["Query History"],
)


@router.get("/{dataset_id}/history")
def get_query_history(
    dataset_id: str,
    limit: int = 20,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Return recent analytical queries for a dataset
    owned by the authenticated user.
    """

    registry = DatasetRegistry()

    # -------------------------------------------------
    # Verify dataset ownership
    # -------------------------------------------------

    dataset = registry.get_user_dataset(
        dataset_id=dataset_id,
        user_id=current_user.id,
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found.",
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100.",
        )

    history_service = QueryHistoryService()

    history = history_service.get_history(
        dataset_id=dataset_id,
        limit=limit,
    )

    return {
        "success": True,
        "dataset_id": dataset_id,
        "count": len(history),
        "history": history,
    }