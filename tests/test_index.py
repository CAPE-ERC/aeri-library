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


def test_compute_aeri_groups_by_country_and_month():
    result = compute_aeri(_scored_df())
    nigeria_march = result[(result["country"] == "Nigeria") & (result["month"] == "2026-03")]
    assert nigeria_march["n_articles"].iloc[0] == 2
    assert nigeria_march["aeri"].iloc[0] == pytest.approx(100 * (4.5 + 2.0) / 2)

    ghana_march = result[(result["country"] == "Ghana") & (result["month"] == "2026-03")]
    assert ghana_march["n_articles"].iloc[0] == 1
    assert ghana_march["aeri"].iloc[0] == pytest.approx(100 * 8.0 / 1)


def test_diagnostics_reports_shares_and_averages():
    result = diagnostics(_scored_df())
    nigeria_march = result[(result["country"] == "Nigeria") & (result["month"] == "2026-03")]
    assert nigeria_march["relevant_share"].iloc[0] == pytest.approx(1.0)
    assert nigeria_march["avg_severity"].iloc[0] == pytest.approx(2.5)
    assert nigeria_march["avg_confidence"].iloc[0] == pytest.approx(1.25)


def test_coverage_filter_keeps_only_country_months_above_threshold():
    aeri_df = pd.DataFrame(
        {
            "country": ["Nigeria", "Ghana", "Togo"],
            "month": ["2026-03", "2026-03", "2026-03"],
            "n_articles": [150, 99, 100],
            "aeri": [10.0, 5.0, 3.0],
        }
    )
    filtered = coverage_filter(aeri_df)
    assert set(filtered["country"]) == {"Nigeria", "Togo"}


def test_coverage_filter_accepts_custom_threshold():
    aeri_df = pd.DataFrame(
        {
            "country": ["Nigeria", "Ghana"],
            "month": ["2026-03", "2026-03"],
            "n_articles": [40, 10],
            "aeri": [10.0, 5.0],
        }
    )
    filtered = coverage_filter(aeri_df, min_articles=20)
    assert list(filtered["country"]) == ["Nigeria"]
