import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

from app.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

# backend/
# ├── app/
# │   └── auth/
# │       └── router.py
# └── data/
#
# This resolves the database location reliably on both
# local development and deployment platforms such as Render.

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DATABASE_PATH = DATA_DIR / "users.db"


def get_connection():

    connection = sqlite3.connect(
        str(DATABASE_PATH)
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_database():

    # Make absolutely sure the directory exists
    # before SQLite attempts to create/open the file.

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = get_connection()

    try:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.commit()

    finally:

        connection.close()


initialize_database()


# =========================================================
# REGISTER
# =========================================================

@router.post(
    "/register",
    response_model=UserResponse,
)
async def register_user(
    request: RegisterRequest,
):

    email = request.email.lower().strip()

    full_name = request.full_name.strip()

    if len(request.password) < 8:

        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 8 characters.",
        )

    if not full_name:

        raise HTTPException(
            status_code=400,
            detail="Full name cannot be empty.",
        )

    connection = get_connection()

    try:

        existing_user = connection.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

        if existing_user:

            raise HTTPException(
                status_code=409,
                detail="An account with this email already exists.",
            )

        user_id = str(uuid.uuid4())

        created_at = datetime.now(
            timezone.utc
        ).isoformat()

        password_hash_value = hash_password(
            request.password
        )

        connection.execute(
            """
            INSERT INTO users (
                id,
                email,
                password_hash,
                full_name,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                email,
                password_hash_value,
                full_name,
                created_at,
            ),
        )

        connection.commit()

        return UserResponse(
            id=user_id,
            email=email,
            full_name=full_name,
        )

    finally:

        connection.close()


# =========================================================
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login_user(
    request: LoginRequest,
):

    email = request.email.lower().strip()

    connection = get_connection()

    try:

        user = connection.execute(
            """
            SELECT
                id,
                email,
                password_hash,
                full_name
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

    finally:

        connection.close()

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    if not verify_password(
        request.password,
        user["password_hash"],
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(
        user["id"]
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
        ),
    )


# =========================================================
# CURRENT USER
# =========================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: UserResponse = Depends(
        get_current_user
    ),
):

    return current_user