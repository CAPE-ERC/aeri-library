"""ARS component scores: Intensity, Breadth, Severity, Structure.

Verified against the real `aeri_risk_score_country_period.csv` (Algeria
2015-01: IntensityScore=0.303778..., BreadthScore=0.290909...,
SeverityScore=0.416193..., StructureScore=1.0), each reproducing exactly
from that period's real AERI / RelevantSharePct / AvgSeverityAmongRelevant
/ ActivePillars values.
"""

from __future__ import annotations

import pandas as pd

#: The 4 ARS components, in the order used throughout `aeri.ars`.
ARS_COMPONENTS: tuple[str, ...] = ("Intensity", "Breadth", "Severity", "Structure")


def components(
    aeri_df: pd.DataFrame,
    diagnostics_df: pd.DataFrame,
    active_pillars_df: pd.DataFrame,
) -> pd.DataFrame:
    """Intensity / Breadth / Severity / Structure per country-month.

    - `Intensity = clip(AERI / 200, 0, 1)`
    - `Breadth = clip(RelevantSharePct / 100, 0, 1)`
    - `Severity = clip(AvgSeverityAmongRelevant / 4, 0, 1)`
    - `Structure = clip(ActivePillars / 8, 0, 1)`

    `aeri_df` is `compute_aeri()` output, `diagnostics_df` is
    `diagnostics()` output, `active_pillars_df` is
    `aeri.pillars.active_pillars()` output -- all three merged on
    `(Country, Period)`, the same merge-by-key pattern `coverage_filter()`
    already uses.
    """
    merged = aeri_df.merge(diagnostics_df, on=["Country", "Period"], how="inner").merge(
        active_pillars_df, on=["Country", "Period"], how="inner"
    )
    out = merged[["Country", "Period"]].copy()
    out["Intensity"] = (merged["AERI"] / 200.0).clip(lower=0.0, upper=1.0)
    out["Breadth"] = (merged["RelevantSharePct"] / 100.0).clip(lower=0.0, upper=1.0)
    out["Severity"] = (merged["AvgSeverityAmongRelevant"] / 4.0).clip(lower=0.0, upper=1.0)
    out["Structure"] = (merged["ActivePillars"] / 8.0).clip(lower=0.0, upper=1.0)
    return out
