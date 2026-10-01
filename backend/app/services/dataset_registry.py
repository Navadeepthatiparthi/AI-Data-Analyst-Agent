import sqlite3
from pathlib import Path
from typing import Optional


DATABASE_PATH = Path("data/datasets.db")


class DatasetRegistry:
    """
    Persistent registry for uploaded datasets.

    Every dataset belongs to one authenticated user.
    """

    def __init__(
        self,
        database_path: str = str(DATABASE_PATH),
    ):
        self.database_path = Path(database_path)

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._create_table()

    def _connect(self):
        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    def _create_table(self):

        with self._connect() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS datasets (
                    dataset_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    rows INTEGER NOT NULL,
                    columns INTEGER NOT NULL,
                    uploaded_at TEXT NOT NULL
            )
            """
        )

        columns = connection.execute(
            """
            PRAGMA table_info(datasets)
            """
        ).fetchall()

        column_names = {
            column["name"]
            for column in columns
        }

        if "user_id" not in column_names:

            connection.execute(
                """
                ALTER TABLE datasets
                ADD COLUMN user_id TEXT
                """
            )

        connection.commit()

    def register_dataset(
        self,
        dataset_id: str,
        user_id: str,
        filename: str,
        file_path: str,
        table_name: str,
        rows: int,
        columns: int,
        uploaded_at: str,
    ) -> dict:
        """
        Register a dataset and associate it
        with the authenticated user.
        """

        with self._connect() as connection:

            connection.execute(
                """
                INSERT INTO datasets (
                    dataset_id,
                    user_id,
                    filename,
                    file_path,
                    table_name,
                    rows,
                    columns,
                    uploaded_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dataset_id,
                    user_id,
                    filename,
                    file_path,
                    table_name,
                    rows,
                    columns,
                    uploaded_at,
                ),
            )

            connection.commit()

        return self.get_dataset(
            dataset_id
        )

    def get_dataset(
        self,
        dataset_id: str,
    ) -> Optional[dict]:
        """
        Retrieve a dataset by dataset_id.
        """

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT
                    dataset_id,
                    user_id,
                    filename,
                    file_path,
                    table_name,
                    rows,
                    columns,
                    uploaded_at
                FROM datasets
                WHERE dataset_id = ?
                """,
                (dataset_id,),
            ).fetchone()

        if row is None:
            return None

        return dict(row)

    def get_user_dataset(
        self,
        dataset_id: str,
        user_id: str,
    ) -> Optional[dict]:
        """
        Retrieve a dataset only when it belongs
        to the authenticated user.
        """

        with self._connect() as connection:

            row = connection.execute(
                """
                SELECT
                    dataset_id,
                    user_id,
                    filename,
                    file_path,
                    table_name,
                    rows,
                    columns,
                    uploaded_at
                FROM datasets
                WHERE dataset_id = ?
                  AND user_id = ?
                """,
                (
                    dataset_id,
                    user_id,
                ),
            ).fetchone()

        if row is None:
            return None

        return dict(row)

    def list_datasets(
        self,
        user_id: Optional[str] = None,
    ) -> list[dict]:
        """
        Return datasets.

        If user_id is provided, only datasets
        belonging to that user are returned.
        """

        with self._connect() as connection:

            if user_id is None:

                rows = connection.execute(
                    """
                    SELECT
                        dataset_id,
                        user_id,
                        filename,
                        file_path,
                        table_name,
                        rows,
                        columns,
                        uploaded_at
                    FROM datasets
                    ORDER BY uploaded_at DESC
                    """
                ).fetchall()

            else:

                rows = connection.execute(
                    """
                    SELECT
                        dataset_id,
                        user_id,
                        filename,
                        file_path,
                        table_name,
                        rows,
                        columns,
                        uploaded_at
                    FROM datasets
                    WHERE user_id = ?
                    ORDER BY uploaded_at DESC
                    """,
                    (user_id,),
                ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def delete_dataset(
        self,
        dataset_id: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Delete a dataset.

        If user_id is provided, deletion is allowed
        only when the dataset belongs to that user.
        """

        with self._connect() as connection:

            if user_id is None:

                cursor = connection.execute(
                    """
                    DELETE FROM datasets
                    WHERE dataset_id = ?
                    """,
                    (dataset_id,),
                )

            else:

                cursor = connection.execute(
                    """
                    DELETE FROM datasets
                    WHERE dataset_id = ?
                      AND user_id = ?
                    """,
                    (
                        dataset_id,
                        user_id,
                    ),
                )

            connection.commit()

        return cursor.rowcount > 0