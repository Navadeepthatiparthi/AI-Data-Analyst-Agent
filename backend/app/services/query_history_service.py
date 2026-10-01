import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class QueryHistoryService:
    """
    Stores analytical question, SQL, result, and execution history.

    Each history record belongs to a dataset.
    """

    def __init__(
        self,
        database_path: str = "data/query_history.db",
    ):
        self.database_path = database_path

        Path(database_path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._create_table()
        self._migrate_table()

    def _connect(self):
        return sqlite3.connect(
            self.database_path
        )

    def _create_table(self):
        connection = self._connect()

        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    sql TEXT NOT NULL,
                    row_count INTEGER NOT NULL,
                    result_json TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )

            connection.commit()

        finally:
            connection.close()

    def _migrate_table(self):
        """
        Add result_json to existing databases
        created before result storage was introduced.
        """

        connection = self._connect()

        try:
            columns = connection.execute(
                """
                PRAGMA table_info(query_history)
                """
            ).fetchall()

            column_names = {
                column[1]
                for column in columns
            }

            if "result_json" not in column_names:
                connection.execute(
                    """
                    ALTER TABLE query_history
                    ADD COLUMN result_json TEXT
                    """
                )

                connection.commit()

        finally:
            connection.close()

    def save_query(
        self,
        dataset_id: str,
        question: str,
        sql: str,
        row_count: int,
        results: list,
    ) -> dict:

        created_at = datetime.now(
            timezone.utc
        ).isoformat()

        result_json = json.dumps(
            results,
            default=str,
        )

        connection = self._connect()

        try:
            cursor = connection.execute(
                """
                INSERT INTO query_history (
                    dataset_id,
                    question,
                    sql,
                    row_count,
                    result_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    dataset_id,
                    question,
                    sql,
                    row_count,
                    result_json,
                    created_at,
                ),
            )

            connection.commit()

            return {
                "id": cursor.lastrowid,
                "dataset_id": dataset_id,
                "question": question,
                "sql": sql,
                "row_count": row_count,
                "results": results,
                "created_at": created_at,
            }

        finally:
            connection.close()

    def get_history(
        self,
        dataset_id: str,
        limit: int = 20,
    ) -> list[dict]:

        connection = self._connect()

        try:
            cursor = connection.execute(
                """
                SELECT
                    id,
                    dataset_id,
                    question,
                    sql,
                    row_count,
                    result_json,
                    created_at
                FROM query_history
                WHERE dataset_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    dataset_id,
                    limit,
                ),
            )

            rows = cursor.fetchall()

            history = []

            for row in rows:
                result_json = row[5]

                if result_json:
                    try:
                        results = json.loads(
                            result_json
                        )
                    except json.JSONDecodeError:
                        results = []
                else:
                    results = []

                history.append(
                    {
                        "id": row[0],
                        "dataset_id": row[1],
                        "question": row[2],
                        "sql": row[3],
                        "row_count": row[4],
                        "results": results,
                        "created_at": row[6],
                    }
                )

            return history

        finally:
            connection.close()