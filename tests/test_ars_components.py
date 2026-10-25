import pandas as pd
import pytest

from aeri.ars.components import components


def test_components_formula_matches_real_algeria_2015_01_row():
    # Real production rows for Algeria 2015-01 (aeri_country_period.csv,
    # aeri_diagnostics.csv, aeri_pillars_country_period.csv), combined.
    aeri_df = pd.DataFrame({"Country": ["Algeria"], "Period": ["2015-01"], "AERI": [60.75561048289257]})
    diagnostics_df = pd.DataFrame(
        {
            "Country": ["Algeria"],
            "Period": ["2015-01"],
            "TotalArticles": [4235],
            "RelevantArticles": [1232],
            "RelevantSharePct": [29.09090909090909],
            "AvgConfidence": [1.156198278424872],
            "AvgSeverityAmongRelevant": [1.6647727272727273],
        }
    )
    active_pillars_df = pd.DataFrame({"Country": ["Algeria"], "Period": ["2015-01"], "ActivePillars": [8]})

    result = components(aeri_df, diagnostics_df, active_pillars_df)
    row = result.iloc[0]

    # Real IntensityScore/BreadthScore/SeverityScore/StructureScore values.
    assert row["Intensity"] == pytest.approx(0.3037780524144629)
    assert row["Breadth"] == pytest.approx(0.2909090909090909)
    assert row["Severity"] == pytest.approx(0.4161931818181818)
    assert row["Structure"] == pytest.approx(1.0)


def test_components_are_clipped_to_zero_one():
    aeri_df = pd.DataFrame({"Country": ["X"], "Period": ["2026-01"], "AERI": [500.0]})
    diagnostics_df = pd.DataFrame(
        {
            "Country": ["X"],
            "Period": ["2026-01"],
            "RelevantSharePct": [150.0],
            "AvgSeverityAmongRelevant": [10.0],
        }
    )
    active_pillars_df = pd.DataFrame({"Country": ["X"], "Period": ["2026-01"], "ActivePillars": [20]})

    row = components(aeri_df, diagnostics_df, active_pillars_df).iloc[0]
    assert row["Intensity"] == pytest.approx(1.0)
    assert row["Breadth"] == pytest.approx(1.0)
    assert row["Severity"] == pytest.approx(1.0)
    assert row["Structure"] == pytest.approx(1.0)
