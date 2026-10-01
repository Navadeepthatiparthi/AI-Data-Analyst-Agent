import sqlite3

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.schemas import UserResponse
from app.auth.security import decode_access_token


DATABASE_PATH = "data/users.db"


security_scheme = HTTPBearer()


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security_scheme
    ),
) -> UserResponse:

    token = credentials.credentials

    try:

        payload = decode_access_token(token)

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    user_id = payload.get("sub")

    if not user_id:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    connection = get_connection()

    try:

        user = connection.execute(
            """
            SELECT
                id,
                email,
                full_name
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

    finally:

        connection.close()

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
    )