"""Country-month pillar indices and the active-pillar count.

Equations (8)-(9) of the CAPE AERI/ARS methodology (Main_AERI_ARS_Paper):
Pillar_p = 100 * sum(A_i * I_p,i) / N, and K_ct = sum_p 1{Pillar_p > 0}.
"""

from __future__ import annotations

import pandas as pd

from ..config import PILLARS


def pillar_indices(
    scored: pd.DataFrame,
    country_col: str = "country",
    date_col: str = "date",
    score_col: str = "article_score",
) -> pd.DataFrame:
    """Pillar_p = 100 * sum(A_i * I_p,i) / N for each of the 8 pillars.

    `scored` must already have the per-article score column and the 8
    pillar flag columns (see `aeri.scoring.score_articles`). `N` is the
    total article count for the country-month -- the same denominator
    `compute_aeri()` uses, not just the pillar-active articles. Returns one
    row per (Country, Period) with one column per pillar (see
    `aeri.config.PILLARS`), matching the production
    `aeri_pillars_country_period.csv` schema.
    """
    working = scored.copy()
    working["Period"] = working[date_col].astype(str).str.slice(0, 7)

    rows: list[dict] = []
    for (country, period), group in working.groupby([country_col, "Period"]):
        n = len(group)
        row: dict = {"Country": country, "Period": period}
        for pillar in PILLARS:
            weighted = (group[score_col] * group[pillar].astype(float)).sum()
            row[pillar] = 100.0 * weighted / n if n else 0.0
        rows.append(row)

    columns = ["Country", "Period", *PILLARS]
    result = pd.DataFrame(rows, columns=columns)
    return result.sort_values(["Country", "Period"]).reset_index(drop=True)


def active_pillars(pillar_df: pd.DataFrame) -> pd.DataFrame:
    """K_ct = number of the 8 pillars with a positive index, per country-month.

    `pillar_df` is `pillar_indices()` output. Matches the `ActivePillars`
    column of the production `aeri_risk_score_country_period.csv` (used
    there as the ARS Structure component, `ActivePillars / 8`).
    """
    out = pillar_df[["Country", "Period"]].copy()
    out["ActivePillars"] = (pillar_df[list(PILLARS)] > 0).sum(axis=1)
    return out
