from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse
from app.services.dataset_registry import DatasetRegistry
from app.services.query_history_service import QueryHistoryService
from app.services.query_service import QueryService
from app.services.sql_generation_service import SQLGenerationService


router = APIRouter(
    prefix="/api/datasets",
    tags=["AI Analyst"],
)


class AskRequest(BaseModel):
    question: str


@router.post("/{dataset_id}/ask")
async def ask_dataset(
    dataset_id: str,
    request: AskRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Convert a natural-language question into SQL,
    execute it only against a dataset owned by the
    authenticated user, save the result, and return
    the analytical answer.
    """

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    # -------------------------------------------------
    # Verify dataset ownership before any AI processing
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

    sql_service = SQLGenerationService()
    query_service = QueryService()
    history_service = QueryHistoryService()

    try:
        generated_sql = await sql_service.generate_sql(
            dataset_id=dataset_id,
            question=question,
        )

        result = query_service.execute_query(
            dataset_id=dataset_id,
            query=generated_sql,
            user_id=current_user.id,
        )

        history_service.save_query(
            dataset_id=dataset_id,
            question=question,
            sql=generated_sql,
            row_count=result["row_count"],
            results=result["results"],
        )

        return {
            "success": True,
            "dataset_id": dataset_id,
            "question": question,
            "sql": generated_sql,
            "row_count": result["row_count"],
            "results": result["results"],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(exc)}",
        )