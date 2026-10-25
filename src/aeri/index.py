"""Country-month AERI aggregation, diagnostics and coverage filtering.

Output column names (`Country`, `Period`, `AERI`, `TotalArticles`, ...)
match the production `aeri_country_period.csv` / `aeri_diagnostics.csv`
schema already consumed by the AERI Pillar API, rather than inventing a
new naming convention.
"""

from __future__ import annotations

import pandas as pd

from .config import DEFAULT_CONFIG, AERIConfig


def _year_month(df: pd.DataFrame, date_col: str) -> pd.Series:
    return df[date_col].astype(str).str.slice(0, 7)


def compute_aeri(
    scored: pd.DataFrame,
    country_col: str = "country",
    date_col: str = "date",
    score_col: str = "article_score",
) -> pd.DataFrame:
    """AERI = 100 * sum(A_i) / N_t for each country and month.

    `scored` must already have a score column (see
    `aeri.scoring.score_articles`). Returns one row per (Country, Period).
    """
    working = scored.copy()
    working["Period"] = _year_month(working, date_col)

    grouped = working.groupby([country_col, "Period"], as_index=False).agg(
        n_articles=(score_col, "size"),
        total_score=(score_col, "sum"),
    )
    grouped["AERI"] = 100 * grouped["total_score"] / grouped["n_articles"]
    grouped = grouped.rename(columns={country_col: "Country"})
    return (
        grouped[["Country", "Period", "AERI"]]
        .sort_values(["Country", "Period"])
        .reset_index(drop=True)
    )


def diagnostics(
    scored: pd.DataFrame,
    country_col: str = "country",
    date_col: str = "date",
) -> pd.DataFrame:
    """Total articles, relevant share, average confidence, and average
    severity among relevant articles, grouped by country and month.
    """
    working = scored.copy()
    working["Period"] = _year_month(working, date_col)

    rows: list[dict] = []
    for (country, period), group in working.groupby([country_col, "Period"]):
        total = len(group)
        relevant_mask = group["relevant"].astype(bool)
        relevant_n = int(relevant_mask.sum())
        rows.append(
            {
                "Country": country,
                "Period": period,
                "TotalArticles": total,
                "RelevantArticles": relevant_n,
                "RelevantSharePct": 100.0 * relevant_n / total if total else 0.0,
                "AvgConfidence": float(group["confidence"].mean()) if total else 0.0,
                "AvgSeverityAmongRelevant": (
                    float(group.loc[relevant_mask, "severity"].mean()) if relevant_n else 0.0
                ),
            }
        )

    columns = [
        "Country", "Period", "TotalArticles", "RelevantArticles",
        "RelevantSharePct", "AvgConfidence", "AvgSeverityAmongRelevant",
    ]
    result = pd.DataFrame(rows, columns=columns)
    return result.sort_values(["Country", "Period"]).reset_index(drop=True)


def coverage_filter(
    aeri_df: pd.DataFrame,
    diagnostics_df: pd.DataFrame,
    min_articles: int | None = None,
    config: AERIConfig = DEFAULT_CONFIG,
) -> pd.DataFrame:
    """Keeps rows of `aeri_df` whose (Country, Period) has at least
    `min_articles` (default: 100) in `diagnostics_df["TotalArticles"]`.
    """
    threshold = config.coverage_min_articles if min_articles is None else min_articles
    keep = diagnostics_df.loc[
        diagnostics_df["TotalArticles"] >= threshold, ["Country", "Period"]
    ]
    return aeri_df.merge(keep, on=["Country", "Period"], how="inner").reset_index(drop=True)
