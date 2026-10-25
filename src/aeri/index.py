"""Country-month AERI aggregation, diagnostics and coverage filtering."""

from __future__ import annotations

import pandas as pd

from .config import DEFAULT_CONFIG, AERIConfig


def _month_period(scored_df: pd.DataFrame, date_col: str) -> pd.Series:
    return pd.to_datetime(scored_df[date_col]).dt.to_period("M").astype(str)


def compute_aeri(
    scored_df: pd.DataFrame,
    country_col: str = "country",
    date_col: str = "date",
    score_col: str = "article_score",
) -> pd.DataFrame:
    """AERI = 100 * sum(A_i) / N_t for each country and month.

    `scored_df` must already have a score column (see `score_dataframe`).
    Returns one row per (country, month) with `n_articles` and `aeri`.
    """
    working = scored_df.copy()
    working["month"] = _month_period(working, date_col)

    grouped = working.groupby([country_col, "month"], as_index=False).agg(
        n_articles=(score_col, "size"),
        total_score=(score_col, "sum"),
    )
    grouped["aeri"] = 100 * grouped["total_score"] / grouped["n_articles"]
    return grouped.drop(columns="total_score")


def diagnostics(
    scored_df: pd.DataFrame,
    country_col: str = "country",
    date_col: str = "date",
) -> pd.DataFrame:
    """Total articles, relevant share, average severity, average confidence.

    Grouped by country and month.
    """
    working = scored_df.copy()
    working["month"] = _month_period(working, date_col)

    grouped = working.groupby([country_col, "month"], as_index=False).agg(
        n_articles=("relevant", "size"),
        relevant_share=("relevant", "mean"),
        avg_severity=("severity", "mean"),
        avg_confidence=("confidence", "mean"),
    )
    return grouped


def coverage_filter(
    aeri_df: pd.DataFrame,
    min_articles: int | None = None,
    count_col: str = "n_articles",
    config: AERIConfig = DEFAULT_CONFIG,
) -> pd.DataFrame:
    """Keeps country-months with at least `min_articles` (default: 100)."""
    threshold = config.coverage_min_articles if min_articles is None else min_articles
    return aeri_df[aeri_df[count_col] >= threshold].reset_index(drop=True)
