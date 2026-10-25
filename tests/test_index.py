import pandas as pd
import pytest

from aeri.index import compute_aeri, coverage_filter, diagnostics


def _scored_df():
    return pd.DataFrame(
        {
            "country": ["Nigeria", "Nigeria", "Nigeria", "Ghana"],
            "date": ["2026-03-01", "2026-03-15", "2026-04-01", "2026-03-10"],
            "relevant": [True, True, False, True],
            "severity": [3, 2, 0, 4],
            "confidence": [1.5, 1.0, 1.0, 2.0],
            "article_score": [4.5, 2.0, 0.0, 8.0],
        }
    )


def test_compute_aeri_groups_by_country_and_period():
    result = compute_aeri(_scored_df())
    assert list(result.columns) == ["Country", "Period", "AERI"]

    nigeria_march = result[(result["Country"] == "Nigeria") & (result["Period"] == "2026-03")]
    assert nigeria_march["AERI"].iloc[0] == pytest.approx(100 * (4.5 + 2.0) / 2)

    ghana_march = result[(result["Country"] == "Ghana") & (result["Period"] == "2026-03")]
    assert ghana_march["AERI"].iloc[0] == pytest.approx(100 * 8.0 / 1)


def test_diagnostics_reports_counts_shares_and_averages():
    result = diagnostics(_scored_df())
    nigeria_march = result[(result["Country"] == "Nigeria") & (result["Period"] == "2026-03")]
    row = nigeria_march.iloc[0]
    assert row["TotalArticles"] == 2
    assert row["RelevantArticles"] == 2
    assert row["RelevantSharePct"] == pytest.approx(100.0)
    assert row["AvgConfidence"] == pytest.approx(1.25)
    # Averaged over relevant articles only.
    assert row["AvgSeverityAmongRelevant"] == pytest.approx(2.5)


def test_diagnostics_severity_average_excludes_irrelevant_rows():
    df = pd.DataFrame(
        {
            "country": ["Nigeria", "Nigeria"],
            "date": ["2026-05-01", "2026-05-02"],
            "relevant": [True, False],
            "severity": [4, 0],
            "confidence": [2.0, 1.0],
            "article_score": [8.0, 0.0],
        }
    )
    result = diagnostics(df)
    row = result.iloc[0]
    assert row["RelevantSharePct"] == pytest.approx(50.0)
    # If the irrelevant row's 0 leaked into the average, this would be 2.0.
    assert row["AvgSeverityAmongRelevant"] == pytest.approx(4.0)


def test_coverage_filter_keeps_only_periods_above_threshold():
    aeri_df = pd.DataFrame(
        {
            "Country": ["Nigeria", "Ghana", "Togo"],
            "Period": ["2026-03", "2026-03", "2026-03"],
            "AERI": [10.0, 5.0, 3.0],
        }
    )
    diagnostics_df = pd.DataFrame(
        {
            "Country": ["Nigeria", "Ghana", "Togo"],
            "Period": ["2026-03", "2026-03", "2026-03"],
            "TotalArticles": [150, 99, 100],
        }
    )
    filtered = coverage_filter(aeri_df, diagnostics_df)
    assert set(filtered["Country"]) == {"Nigeria", "Togo"}


def test_coverage_filter_accepts_custom_threshold():
    aeri_df = pd.DataFrame({"Country": ["Nigeria", "Ghana"], "Period": ["2026-03", "2026-03"], "AERI": [10.0, 5.0]})
    diagnostics_df = pd.DataFrame(
        {"Country": ["Nigeria", "Ghana"], "Period": ["2026-03", "2026-03"], "TotalArticles": [40, 10]}
    )
    filtered = coverage_filter(aeri_df, diagnostics_df, min_articles=20)
    assert list(filtered["Country"]) == ["Nigeria"]
