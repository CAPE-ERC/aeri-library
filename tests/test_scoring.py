import pandas as pd

from aeri.config import PILLARS
from aeri.scoring import article_score, score_dataframe


def test_article_score_is_product_of_inputs():
    assert article_score(True, 3, 1.5) == 4.5
    assert article_score(False, 3, 1.5) == 0.0


def test_score_dataframe_adds_expected_columns():
    df = pd.DataFrame(
        {
            "title": [
                "Inflation crisis deepens",
                "Local football results",
            ],
            "text": [
                "<p>Inflation and currency devaluation have triggered an economic crisis.</p>",
                "The home team won 2-1 on Saturday afternoon.",
            ],
        }
    )

    scored = score_dataframe(df)

    assert "relevant" in scored.columns
    assert "severity" in scored.columns
    assert "confidence" in scored.columns
    assert "article_score" in scored.columns
    for pillar in PILLARS:
        assert f"pillar_{pillar}" in scored.columns

    assert scored.loc[0, "relevant"] == True  # noqa: E712
    assert scored.loc[0, "article_score"] > 0

    assert scored.loc[1, "relevant"] == False  # noqa: E712
    assert scored.loc[1, "article_score"] == 0.0


def test_score_dataframe_does_not_mutate_input():
    df = pd.DataFrame({"title": ["t"], "text": ["inflation"]})
    original_columns = list(df.columns)
    score_dataframe(df)
    assert list(df.columns) == original_columns
