import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from app.auth.dependencies import get_current_user
from app.auth.schemas import UserResponse

from app.analysis.duckdb_engine import DuckDBEngine
from app.services.dataset_registry import DatasetRegistry
from app.services.dataset_service import DatasetService
from app.services.quality_service import QualityService


router = APIRouter(
    prefix="/api/datasets",
    tags=["Datasets"],
)


UPLOAD_DIRECTORY = Path("data/uploads")

ALLOWED_EXTENSIONS = {
    ".csv",
    ".xlsx",
}

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(
        get_current_user
    ),
):
    """
    Upload, profile, validate, register,
    and prepare a dataset for analytical queries.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Only CSV and XLSX files are supported."
            ),
        )


    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataset_id = str(
        uuid.uuid4()
    )

    safe_filename = (
        f"{dataset_id}{extension}"
    )

    file_path = (
        UPLOAD_DIRECTORY /
        safe_filename
    )

    duckdb_engine = None

    try:

        with file_path.open("wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer,
            )

        df = DatasetService.load_dataset(
            str(file_path)
        )

        profile = DatasetService.profile_dataset(
            df
        )

        quality = QualityService.analyze_quality(
            df
        )

       

        duckdb_engine = DuckDBEngine(
            database_path="data/analytics.db"
        )

        table_name = duckdb_engine.register_dataframe(
            df,
            table_name=f"dataset_{dataset_id}",
        )

        registry = DatasetRegistry()

        uploaded_at = datetime.now(
            timezone.utc
        ).isoformat()

        registry.register_dataset(
            dataset_id=dataset_id,
            filename=file.filename,
            file_path=str(file_path),
            table_name=table_name,
            rows=int(df.shape[0]),
            columns=int(df.shape[1]),
            uploaded_at=uploaded_at,
            user_id=current_user.id,
        )

        schema = duckdb_engine.get_schema(
            table_name
        )

        # --------------------------------------------------
        # 4.8 Return complete response
        # --------------------------------------------------

        return {
            "success": True,
            "dataset_id": dataset_id,
            "filename": file.filename,

            "profile": profile,

            "quality": quality,

            "storage": {
                "file_path": str(file_path),
                "table_name": table_name,
            },

            "schema": schema,
        }

    except Exception as exc:

        # Remove uploaded file if processing fails.
        if file_path.exists():
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to process dataset: {str(exc)}"
            ),
        )

    finally:

        # Always close DuckDB connection.
        if duckdb_engine is not None:
            duckdb_engine.close()


@router.get("")
async def list_datasets(
    current_user: UserResponse = Depends(
        get_current_user
    ),
):
    """
    Return all registered datasets.
    """

    registry = DatasetRegistry()

    datasets = registry.list_datasets(
    user_id=current_user.id
)

    return {
        "success": True,
        "count": len(datasets),
        "datasets": datasets,
    }
@router.get("/{dataset_id}")
async def get_dataset(
    dataset_id: str,
    current_user: UserResponse = Depends(
        get_current_user
    ),
):
    """
    Retrieve dataset metadata by dataset_id.
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

    return {
        "success": True,
        "dataset": dataset,
    }