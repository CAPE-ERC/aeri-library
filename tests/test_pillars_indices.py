import pandas as pd
import pytest

from aeri.config import PILLARS
from aeri.pillars import active_pillars, pillar_indices


def _scored_df():
    # Two Nigeria articles in 2026-03: one activates InflationRisk and
    # FXExternalRisk, the other activates nothing.
    rows = {
        "country": ["Nigeria", "Nigeria"],
        "date": ["2026-03-01", "2026-03-15"],
        "article_score": [4.0, 0.0],
    }
    for pillar in PILLARS:
        rows[pillar] = [False, False]
    rows["InflationRisk"] = [True, False]
    rows["FXExternalRisk"] = [True, False]
    return pd.DataFrame(rows)


def test_pillar_indices_formula_and_columns():
    result = pillar_indices(_scored_df())
    assert list(result.columns) == ["Country", "Period", *PILLARS]

    row = result.iloc[0]
    assert row["Country"] == "Nigeria"
    assert row["Period"] == "2026-03"
    # Pillar_p = 100 * sum(A_i * I_p,i) / N, N = 2 total articles.
    assert row["InflationRisk"] == pytest.approx(100 * 4.0 / 2)
    assert row["FXExternalRisk"] == pytest.approx(100 * 4.0 / 2)
    assert row["DebtFiscalRisk"] == pytest.approx(0.0)


def test_active_pillars_counts_positive_indices():
    pillars_df = pillar_indices(_scored_df())
    result = active_pillars(pillars_df)
    assert list(result.columns) == ["Country", "Period", "ActivePillars"]
    assert result.loc[0, "ActivePillars"] == 2


def test_active_pillars_matches_real_algeria_2015_01_row():
    # Real production row (aeri_pillars_country_period.csv, Algeria 2015-01):
    # all 8 pillars are > 0, and the real aeri_risk_score_country_period.csv
    # reports ActivePillars=8 for that same country-period.
    real_row = {
        "Country": "Algeria",
        "Period": "2015-01",
        "InflationRisk": 5.088547816,
        "FXExternalRisk": 0.873671794,
        "DebtFiscalRisk": 7.948051957,
        "FinancialSectorRisk": 7.421487388,
        "GrowthRealEconomyRisk": 7.182998792,
        "CommoditySupplyRisk": 1.558441558,
        "PoliticalEconomyRisk": 12.81227938,
        "ClimateDisasterRisk": 0.873671811,
    }
    pillars_df = pd.DataFrame([real_row])
    result = active_pillars(pillars_df)
    assert result.loc[0, "ActivePillars"] == 8
