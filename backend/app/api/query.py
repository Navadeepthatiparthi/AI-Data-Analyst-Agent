from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
from app.services.dataset_registry import DatasetRegistry
from app.services.query_service import QueryService


router = APIRouter(
    prefix="/api/datasets",
    tags=["Dataset Queries"],
)


class QueryRequest(BaseModel):
    query: str


@router.post("/{dataset_id}/query")
async def execute_dataset_query(
    dataset_id: str,
    request: QueryRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Execute a read-only analytical query
    only against a dataset owned by the
    authenticated user.
    """

    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    # -------------------------------------------------
    # Verify dataset ownership before SQL execution
    # -------------------------------------------------

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

    service = QueryService()

    try:
        result = service.execute_query(
            dataset_id=dataset_id,
            query=request.query,
            user_id=current_user.id,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {str(exc)}",
        )