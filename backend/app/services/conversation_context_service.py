import json

from app.services.query_history_service import (
    QueryHistoryService,
)


class ConversationContextService:
    """
    Builds compact conversational context from
    recent analytical query history.
    """

    def __init__(self):
        self.history_service = QueryHistoryService()

    def get_context(
        self,
        dataset_id: str,
        limit: int = 5,
    ) -> str:
        """
        Return recent query history in chronological
        order so the LLM can understand follow-up questions.
        """

        history = self.history_service.get_history(
            dataset_id=dataset_id,
            limit=limit,
        )

        if not history:
            return (
                "No previous analytical questions "
                "are available."
            )

        history = list(reversed(history))

        context_items = []

        for index, item in enumerate(
            history,
            start=1,
        ):
            results = item.get(
                "results",
                [],
            )

            if len(results) > 10:
                results = results[:10]

            result_text = json.dumps(
                results,
                ensure_ascii=False,
                default=str,
            )

            context_items.append(
                f"""
Conversation {index}:
User question:
{item["question"]}

Generated SQL:
{item["sql"]}

Result:
{result_text}
""".strip()
            )

        return "\n\n".join(
            context_items
        )