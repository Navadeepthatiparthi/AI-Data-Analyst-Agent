from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
from app.services.dataset_context_service import DatasetContextService
from app.services.dataset_registry import DatasetRegistry


router = APIRouter(
    prefix="/api/datasets",
    tags=["Dataset Context"],
)


@router.get("/{dataset_id}/context")
async def get_dataset_context(
    dataset_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Return dynamic analytical context for a dataset
    owned by the authenticated user.

    No dataset information is hardcoded.
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

    service = DatasetContextService()

    try:
        context = service.get_context(
            dataset_id
        )

        return {
            "success": True,
            "context": context,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to build dataset context: "
                f"{str(exc)}"
            ),
        )