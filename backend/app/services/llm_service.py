import json
import os
import re

import httpx


class LLMService:
    def __init__(self):
        self.api_key = os.getenv(
            "LLM_API_KEY",
            "local",
        )

        self.base_url = os.getenv(
            "LLM_BASE_URL",
            "http://localhost:11434/v1",
        ).rstrip("/")

        self.model = os.getenv(
            "LLM_MODEL",
            "qwen3:4b",
        )

    async def generate(self, prompt: str) -> str:
        if not isinstance(prompt, str):
            raise ValueError("Prompt must be a string.")

        prompt = prompt.strip()

        if not prompt:
            raise ValueError("Prompt cannot be empty.")

        if self._is_ollama():
            return await self._generate_ollama(prompt)

        return await self._generate_openai_compatible(prompt)

    def _is_ollama(self) -> bool:
        return (
            "localhost:11434" in self.base_url
            or "127.0.0.1:11434" in self.base_url
        )

    async def _generate_ollama(
        self,
        prompt: str,
    ) -> str:

        url = "http://localhost:11434/api/chat"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an SQL generation engine.\n\n"
                        "Your ONLY job is to generate one valid "
                        "DuckDB SELECT query.\n\n"
                        "You MUST return JSON in exactly this format:\n"
                        '{"sql":"SELECT ..."}\n\n'
                        "Rules:\n"
                        "- Never explain anything.\n"
                        "- Never provide reasoning.\n"
                        "- Never describe the table.\n"
                        "- Never answer in natural language.\n"
                        "- Never use markdown.\n"
                        "- Never include <think> tags.\n"
                        "- The sql value must contain ONLY SQL.\n"
                        "- The SQL must be a single read-only query.\n"
                        "- Use only the table and columns provided "
                        "in the user prompt."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "stream": False,
            "think": False,
            "keep_alive": "10m",
            "format": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                    }
                },
                "required": ["sql"],
            },
            "options": {
                "temperature": 0,
                "num_predict": 256,
            },
        }

        try:
            async with httpx.AsyncClient(
                timeout=120.0
            ) as client:

                response = await client.post(
                    url,
                    json=payload,
                )

        except httpx.ConnectError as exc:
            raise RuntimeError(
                "Unable to connect to Ollama. "
                "Make sure Ollama is running."
            ) from exc

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "LLM request timed out."
            ) from exc

        if response.status_code >= 400:
            raise RuntimeError(
                "LLM request failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        try:
            data = response.json()

            content = data["message"]["content"]

        except (
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            raise RuntimeError(
                "Ollama returned an invalid response."
            ) from exc

        if not isinstance(content, str):
            raise RuntimeError(
                "Ollama returned non-text content."
            )

        return self._extract_sql_from_json(content)

    async def _generate_openai_compatible(
        self,
        prompt: str,
    ) -> str:

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a precise analytical "
                        "SQL assistant. "
                        "Return only one valid SQL query. "
                        "Do not explain your answer. "
                        "Do not show reasoning. "
                        "Do not use markdown."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0,
        }

        headers = {
            "Authorization": (
                f"Bearer {self.api_key}"
            ),
            "Content-Type": "application/json",
        }

        url = (
            f"{self.base_url}"
            "/chat/completions"
        )

        try:
            async with httpx.AsyncClient(
                timeout=120.0
            ) as client:

                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                )

        except httpx.ConnectError as exc:
            raise RuntimeError(
                "Unable to connect to the LLM."
            ) from exc

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "LLM request timed out."
            ) from exc

        if response.status_code >= 400:
            raise RuntimeError(
                "LLM request failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        try:
            data = response.json()

            content = (
                data["choices"][0]
                ["message"]["content"]
            )

        except (
            KeyError,
            IndexError,
            TypeError,
            ValueError,
        ) as exc:
            raise RuntimeError(
                "LLM returned an invalid response."
            ) from exc

        if not isinstance(content, str):
            raise RuntimeError(
                "LLM returned non-text content."
            )

        return self._clean_plain_sql(content)

    @staticmethod
    def _extract_sql_from_json(
        content: str,
    ) -> str:

        content = content.strip()

        # Remove ANSI terminal escape sequences.
        content = re.sub(
            r"\x1b\[[0-9;]*[A-Za-z]",
            "",
            content,
        )

        # Remove accidental thinking blocks.
        content = re.sub(
            r"<think>.*?</think>",
            "",
            content,
            flags=re.IGNORECASE | re.DOTALL,
        ).strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "LLM did not return the required SQL JSON format."
            ) from exc

        if not isinstance(data, dict):
            raise RuntimeError(
                "LLM returned an invalid SQL response."
            )

        sql = data.get("sql")

        if not isinstance(sql, str):
            raise RuntimeError(
                "LLM response does not contain a SQL query."
            )

        sql = sql.strip()

        if not sql:
            raise RuntimeError(
                "LLM returned an empty SQL query."
            )

        return LLMService._validate_sql_shape(sql)

    @staticmethod
    def _clean_plain_sql(
        content: str,
    ) -> str:

        content = content.strip()

        content = re.sub(
            r"\x1b\[[0-9;]*[A-Za-z]",
            "",
            content,
        )

        content = re.sub(
            r"<think>.*?</think>",
            "",
            content,
            flags=re.IGNORECASE | re.DOTALL,
        ).strip()

        content = re.sub(
            r"```sql",
            "",
            content,
            flags=re.IGNORECASE,
        )

        content = content.replace(
            "```",
            "",
        ).strip()

        return LLMService._validate_sql_shape(content)

    @staticmethod
    def _validate_sql_shape(
        sql: str,
    ) -> str:

        sql = sql.strip()

        # Remove a trailing semicolon temporarily.
        sql_without_semicolon = sql.rstrip(";").strip()

        # SQL generation must start with SELECT or WITH.
        if not re.match(
            r"^(SELECT|WITH)\b",
            sql_without_semicolon,
            flags=re.IGNORECASE,
        ):
            raise RuntimeError(
                "LLM did not return a valid SQL SELECT query."
            )

        # A real analytical SELECT should contain FROM.
        if not re.search(
            r"\bFROM\b",
            sql_without_semicolon,
            flags=re.IGNORECASE,
        ):
            raise RuntimeError(
                "LLM returned incomplete SQL: missing FROM clause."
            )

        # Reject obvious natural-language responses.
        natural_language_phrases = (
            "since it's",
            "since it is",
            "i need to",
            "the answer is",
            "the table name",
            "where revenue is the maximum",
            "generated the highest",
        )

        lowered = sql_without_semicolon.lower()

        for phrase in natural_language_phrases:
            if phrase in lowered:
                raise RuntimeError(
                    "LLM returned natural-language reasoning "
                    "instead of SQL."
                )

        return sql_without_semicolon + ";"