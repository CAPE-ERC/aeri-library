import pandas as pd

from aeri.ars import alert_table, ars_benchmark, components, risk_band
from aeri.config import PILLARS
from aeri.dictionary import CountryDictionary, Dictionary
from aeri.index import compute_aeri, diagnostics
from aeri.pillars import active_pillars, pillar_indices
from aeri.scoring import score_articles

NIGERIA = CountryDictionary(
    country="Nigeria",
    languages=("en",),
    economic=("inflation", "devaluation", "naira", "drought", "crisis"),
    policy=(),
    uncertainty=(),
)
DICTIONARY = Dictionary(countries={"Nigeria": NIGERIA})


def test_full_pipeline_from_articles_to_alerts():
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
    aeri_df = compute_aeri(scored)
    diag = diagnostics(scored)
    pillars_df = pillar_indices(scored)
    coverage = active_pillars(pillars_df)

    comps = components(aeri_df, diag, coverage)
    assert list(comps.columns) == ["Country", "Period", "Intensity", "Breadth", "Severity", "Structure"]
    for col in ("Intensity", "Breadth", "Severity", "Structure"):
        assert (comps[col] >= 0).all() and (comps[col] <= 1).all()

    ars_df = ars_benchmark(comps)
    assert (ars_df["ARS"] >= 0).all() and (ars_df["ARS"] <= 100).all()

    band = risk_band(ars_df.loc[0, "ARS"])
    assert band in {"Low", "Moderate", "Elevated", "High", "Severe"}

    alerts = alert_table(ars_df, diag, coverage)
    assert list(alerts.columns) == [
        "Country", "Period", "ARS", "Alert_Level", "Alert_Spike",
        "Alert_Structural", "Alert_Persistent",
    ]
    assert len(alerts) == 1
