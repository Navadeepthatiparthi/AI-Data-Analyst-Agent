import os
import shutil
import uuid
from pathlib import Path
from app.services.quality_service import QualityService

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.dataset_service import DatasetService


router = APIRouter(prefix="/api/datasets", tags=["Datasets"])

UPLOAD_DIRECTORY = Path("data/uploads")

ALLOWED_EXTENSIONS = {".csv", ".xlsx"}


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload and profile a CSV or Excel dataset.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only CSV and XLSX files are supported.",
        )

    UPLOAD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataset_id = str(uuid.uuid4())

    safe_filename = (
        f"{dataset_id}{extension}"
    )

    file_path = UPLOAD_DIRECTORY / safe_filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        df = DatasetService.load_dataset(
            str(file_path)
        )

        profile = DatasetService.profile_dataset(df)
        quality = QualityService.analyze_quality(df)

        return {
            "success": True,
            "dataset_id": dataset_id,
            "filename": file.filename,
            "profile": profile,
            "quality": quality,
        }

    except Exception as exc:

        if file_path.exists():
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process dataset: {str(exc)}",
        )