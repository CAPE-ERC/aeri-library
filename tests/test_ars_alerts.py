import pandas as pd
import pytest

from aeri.ars.alerts import alert_table, level_alert, persistence_alert, spike_alert, structural_alert

# Real production sequence for Djibouti, 2019-01 through 2019-08
# (aeri_risk_score_country_period.csv / aeri_diagnostics.csv /
# aeri_pillars_country_period.csv), illustrating every alert firing at
# least once, including the coverage-threshold-free 2019-08 row
# (TotalArticles=7, still a full row with ARS=0).
PERIODS = [
    "2019-01", "2019-02", "2019-03", "2019-04",
    "2019-05", "2019-06", "2019-07", "2019-08",
]
ARS_VALUES = [33.09, 62.75, 57.22, 56.64, 77.71, 56.10, 66.36, 0.00]
ACTIVE_PILLARS = [3, 5, 6, 5, 5, 5, 5, 0]
AVG_SEVERITY = [1.69, 2.25, 1.67, 2.00, 3.17, 1.70, 2.25, 0.00]

EXPECTED_LEVEL = [False, True, False, False, True, False, True, False]
EXPECTED_SPIKE = [False, True, False, False, True, False, False, False]
EXPECTED_STRUCTURAL = [False, False, False, False, True, False, False, False]
EXPECTED_PERSISTENT = [False, False, False, True, True, True, True, False]


def _ars_df():
    return pd.DataFrame({"Country": ["Djibouti"] * 8, "Period": PERIODS, "ARS": ARS_VALUES})


def _diagnostics_df():
    return pd.DataFrame(
        {
            "Country": ["Djibouti"] * 8,
            "Period": PERIODS,
            "AvgSeverityAmongRelevant": AVG_SEVERITY,
        }
    )


def _active_pillars_df():
    return pd.DataFrame({"Country": ["Djibouti"] * 8, "Period": PERIODS, "ActivePillars": ACTIVE_PILLARS})


def test_level_alert_matches_real_djibouti_2019_sequence():
    result = level_alert(_ars_df())
    assert list(result) == EXPECTED_LEVEL


def test_spike_alert_matches_real_djibouti_2019_sequence():
    result = spike_alert(_ars_df())
    assert list(result) == EXPECTED_SPIKE


def test_persistence_alert_matches_real_djibouti_2019_sequence():
    result = persistence_alert(_ars_df())
    assert list(result) == EXPECTED_PERSISTENT


def test_structural_alert_matches_real_djibouti_2019_sequence():
    merged = _active_pillars_df().merge(_diagnostics_df(), on=["Country", "Period"])
    result = structural_alert(merged)
    assert list(result) == EXPECTED_STRUCTURAL


def test_structural_alert_requires_both_conditions_not_either():
    # Real counter-example: Djibouti 2020-03 has severity >= 2.5 but only
    # 3 active pillars (< 4) -> False. AND, not OR.
    df = pd.DataFrame(
        {
            "ActivePillars": [3, 4, 3, 4],
            "AvgSeverityAmongRelevant": [3.0, 1.0, 1.0, 3.0],
        }
    )
    result = structural_alert(df)
    assert list(result) == [False, False, False, True]


def test_spike_and_persistence_false_for_first_rows_of_each_country():
    # Confirms "insufficient history -> False", not NaN/error, and that
    # per-country grouping doesn't leak across countries.
    df = pd.DataFrame(
        {
            "Country": ["A", "B"],
            "Period": ["2026-01", "2026-01"],
            "ARS": [90.0, 90.0],
        }
    )
    assert list(spike_alert(df)) == [False, False]
    assert list(persistence_alert(df)) == [False, False]


def test_alert_table_matches_real_djibouti_2019_sequence_end_to_end():
    result = alert_table(_ars_df(), _diagnostics_df(), _active_pillars_df())

    assert list(result.columns) == [
        "Country", "Period", "ARS", "Alert_Level", "Alert_Spike",
        "Alert_Structural", "Alert_Persistent",
    ]
    assert list(result["Alert_Level"]) == EXPECTED_LEVEL
    assert list(result["Alert_Spike"]) == EXPECTED_SPIKE
    assert list(result["Alert_Structural"]) == EXPECTED_STRUCTURAL
    assert list(result["Alert_Persistent"]) == EXPECTED_PERSISTENT


def test_alert_table_respects_custom_thresholds():
    result = alert_table(_ars_df(), _diagnostics_df(), _active_pillars_df(), level_threshold=1000.0)
    assert not result["Alert_Level"].any()
