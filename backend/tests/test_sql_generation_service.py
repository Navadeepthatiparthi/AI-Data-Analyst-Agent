import pytest

from app.services.sql_generation_service import (
    SQLGenerationService,
)


DATASET_ID = (
    "dff3ce8d-f503-47cc-8bea-0d64a4b63526"
)


def test_sql_generation_build_prompt_uses_real_dataset():
    service = SQLGenerationService()

    prompt = service.build_prompt(
        dataset_id=DATASET_ID,
        question="Which product generated the highest revenue?",
    )

    assert "sale_samples.csv" in prompt

    assert (
        "dataset_dff3ce8d_f503_47cc_8bea_0d64a4b63526"
        in prompt
    )

    assert "Product" in prompt
    assert "Revenue" in prompt
    assert "Profit" in prompt


def test_sql_generation_rejects_empty_question():
    service = SQLGenerationService()

    with pytest.raises(
        ValueError,
        match="Question cannot be empty.",
    ):
        service.build_prompt(
            dataset_id=DATASET_ID,
            question="   ",
        )


def test_sql_generation_cleans_markdown_sql():
    result = SQLGenerationService._clean_sql(
        """
        ```sql
        SELECT Product
        FROM dataset_dff3ce8d_f503_47cc_8bea_0d64a4b63526
        ```
        """
    )

    assert result.startswith(
        "SELECT Product"
    )

    assert "```" not in result


def test_sql_generation_rejects_other_dataset_table():
    with pytest.raises(
        ValueError,
        match="unauthorized dataset table",
    ):
        SQLGenerationService._validate_dataset_table(
            """
            SELECT *
            FROM another_dataset
            """,
            "dataset_dff3ce8d_f503_47cc_8bea_0d64a4b63526",
        )


def test_sql_generation_accepts_real_dataset_table():
    SQLGenerationService._validate_dataset_table(
        """
        SELECT Product, SUM(Revenue) AS total_revenue
        FROM dataset_dff3ce8d_f503_47cc_8bea_0d64a4b63526
        GROUP BY Product
        """,
        "dataset_dff3ce8d_f503_47cc_8bea_0d64a4b63526",
    )


@pytest.mark.asyncio
async def test_sql_generation_generates_real_dataset_sql(
    monkeypatch,
):
    monkeypatch.setenv(
        "LLM_API_KEY",
        "test-key",
    )

    service = SQLGenerationService()

    async def fake_generate(prompt):
        assert (
            "Which product generated the highest revenue?"
            in prompt
        )

        return """
        SELECT
            Product,
            SUM(Revenue) AS total_revenue
        FROM dataset_dff3ce8d_f503_47cc_8bea_0d64a4b63526
        GROUP BY Product
        ORDER BY total_revenue DESC
        LIMIT 1
        """

    monkeypatch.setattr(
        service.llm_service,
        "generate",
        fake_generate,
    )

    result = await service.generate_sql(
        dataset_id=DATASET_ID,
        question=(
            "Which product generated "
            "the highest revenue?"
        ),
    )

    assert "SELECT" in result
    assert "Product" in result
    assert "Revenue" in result

    assert (
        "dataset_dff3ce8d_f503_47cc_8bea_0d64a4b63526"
        in result
    )