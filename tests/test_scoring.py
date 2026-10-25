import pandas as pd
import pytest

from aeri.config import PILLARS
from aeri.dictionary import CountryDictionary, Dictionary
from aeri.scoring import article_score, score_articles

NIGERIA = CountryDictionary(
    country="Nigeria",
    languages=("en",),
    economic=("inflation", "devaluation", "naira"),
    policy=(),
    uncertainty=(),
)
GHANA = CountryDictionary(
    country="Ghana",
    languages=("en",),
    economic=("inflation", "cedi"),
    policy=(),
    uncertainty=(),
)
DICTIONARY = Dictionary(countries={"Nigeria": NIGERIA, "Ghana": GHANA})


def test_article_score_is_product_of_inputs():
    assert article_score(True, 3, 1.5) == 4.5
    assert article_score(False, 3, 1.5) == 0.0


def test_score_articles_adds_expected_columns():
    df = pd.DataFrame(
        {
            "country": ["Nigeria", "Nigeria"],
            "title": ["Inflation crisis deepens", "Local football results"],
            "text": [
                "<p>Inflation and currency devaluation have triggered an economic crisis.</p>",
                "The home team won 2-1 on Saturday afternoon.",
            ],
        }
    )

    scored = score_articles(df, DICTIONARY)

    assert "relevant" in scored.columns
    assert "severity" in scored.columns
    assert "confidence" in scored.columns
    assert "article_score" in scored.columns
    for pillar in PILLARS:
        assert pillar in scored.columns

    assert scored.loc[0, "relevant"] == True  # noqa: E712
    assert scored.loc[0, "article_score"] > 0

    assert scored.loc[1, "relevant"] == False  # noqa: E712
    assert scored.loc[1, "severity"] == 0
    assert scored.loc[1, "article_score"] == 0.0


def test_score_articles_relevance_is_scoped_to_the_article_country():
    # "naira" is only a Nigeria economic term; the same word in a Ghana
    # row must not flag relevance.
    df = pd.DataFrame({"country": ["Ghana"], "title": ["t"], "text": ["naira talk"]})
    scored = score_articles(df, DICTIONARY)
    assert scored.loc[0, "relevant"] == False  # noqa: E712


def test_score_articles_scores_title_and_text_together():
    # The relevance term only appears in the title, not the body.
    df = pd.DataFrame({"country": ["Nigeria"], "title": ["Inflation worries"], "text": ["Nothing else notable."]})
    scored = score_articles(df, DICTIONARY)
    assert scored.loc[0, "relevant"] == True  # noqa: E712


def test_score_articles_raises_for_unknown_country():
    df = pd.DataFrame({"country": ["Atlantis"], "title": ["t"], "text": ["inflation"]})
    with pytest.raises(KeyError):
        score_articles(df, DICTIONARY)


def test_score_articles_does_not_mutate_input():
    df = pd.DataFrame({"country": ["Nigeria"], "title": ["t"], "text": ["inflation"]})
    original_columns = list(df.columns)
    score_articles(df, DICTIONARY)
    assert list(df.columns) == original_columns
