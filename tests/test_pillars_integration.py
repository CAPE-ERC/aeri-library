import pandas as pd

from aeri.config import PILLARS
from aeri.dictionary import CountryDictionary, Dictionary
from aeri.pillars import active_pillars, pillar_composite, pillar_indices, rank_pillars, transform_pillars
from aeri.scoring import score_articles

NIGERIA = CountryDictionary(
    country="Nigeria",
    languages=("en",),
    economic=("inflation", "devaluation", "naira", "drought"),
    policy=(),
    uncertainty=(),
)
DICTIONARY = Dictionary(countries={"Nigeria": NIGERIA})


def test_pillar_pipeline_end_to_end():
    df = pd.DataFrame(
        {
            "country": ["Nigeria", "Nigeria", "Nigeria"],
            "date": ["2026-03-01", "2026-03-05", "2026-03-10"],
            "title": [
                "Inflation crisis deepens",
                "Currency devaluation hits naira",
                "Local football result",
            ],
            "text": [
                "Inflation and rising prices triggered an economic crisis across the country.",
                "The naira weakened sharply after the central bank's devaluation announcement.",
                "The home team won 2-1 on Saturday afternoon.",
            ],
        }
    )

    scored = score_articles(df, DICTIONARY)
    pillars_df = pillar_indices(scored)
    assert list(pillars_df.columns) == ["Country", "Period", *PILLARS]
    assert pillars_df.loc[0, "InflationRisk"] > 0

    coverage = active_pillars(pillars_df)
    assert coverage.loc[0, "ActivePillars"] >= 1

    transformed = transform_pillars(pillars_df)
    for pillar in PILLARS:
        assert (transformed[pillar] >= 0).all() and (transformed[pillar] <= 1).all()

    composite = pillar_composite(transformed)
    assert composite.loc[0, "PillarComposite"] >= 0

    ranked = rank_pillars(pillars_df.iloc[0])
    assert len(ranked) == len(PILLARS)
    assert ranked[0][1] >= ranked[-1][1]
