"""Early-warning alerts: level, spike, structural, persistence.

Every rule here was verified against the complete real production panel
(`aeri_risk_score_country_period.csv` / `aeri_diagnostics.csv` /
`aeri_risk_alerts.csv`, 7,127 rows, 54 countries, Jan 2015-Jul 2025) with
exhaustive per-row arithmetic checks -- zero mismatches, not spot samples.
The concepts come from `AERI_ARS_Interpretation_Note.docx` Section 7; the
exact thresholds/window sizes came from the proposal PDF and were then
confirmed against every real row.

The real production pipeline has no calendar gaps in its panel (every
country-month with >=1 article gets a row; the >=100-article coverage
rule is applied only for descriptive comparisons, not row inclusion), so
`spike_alert()`/`persistence_alert()` compare against the immediately
preceding *row* in each country's Period-sorted series, not a calendar
month lookup -- matching the real pipeline exactly (confirmed: 7,127 rows
minus one un-comparable first row per of the 54 countries = 7,073 rows
checked for spike; minus two for persistence's 3-row window = 7,019).
If your own panel has gaps (e.g. after `coverage_filter()`), this compares
across the gap as if adjacent -- undocumented in the source material
either way.
"""

from __future__ import annotations

import pandas as pd


def level_alert(ars_df: pd.DataFrame, threshold: float = 60.0) -> pd.Series:
    """Alert_Level: ARS >= threshold (default 60)."""
    return ars_df["ARS"] >= threshold


def spike_alert(
    ars_df: pd.DataFrame, threshold: float = 15.0, country_col: str = "Country"
) -> pd.Series:
    """Alert_Spike: ARS rises by `threshold` or more (default 15) versus
    the immediately preceding row for that country. False for a country's
    first row (no prior row to compare against).
    """
    working = ars_df.sort_values([country_col, "Period"])
    delta = working.groupby(country_col)["ARS"].diff()
    return (delta >= threshold).fillna(False).reindex(ars_df.index)


def persistence_alert(
    ars_df: pd.DataFrame,
    threshold: float = 50.0,
    window: int = 3,
    country_col: str = "Country",
) -> pd.Series:
    """Alert_Persistent: ARS >= threshold (default 50) for `window`
    consecutive rows (default 3) for that country. False until `window`
    rows of history are available.
    """
    working = ars_df.sort_values([country_col, "Period"])
    rolling_min = (
        working.groupby(country_col)["ARS"]
        .rolling(window=window, min_periods=window)
        .min()
        .reset_index(level=0, drop=True)
    )
    return (rolling_min >= threshold).fillna(False).reindex(ars_df.index)


def structural_alert(
    df: pd.DataFrame,
    pillar_threshold: int = 4,
    severity_threshold: float = 2.5,
    active_pillars_col: str = "ActivePillars",
    avg_severity_col: str = "AvgSeverityAmongRelevant",
) -> pd.Series:
    """Alert_Structural: `active_pillars_col` >= pillar_threshold (default
    4) AND `avg_severity_col` >= severity_threshold (default 2.5) -- both
    conditions required, confirmed against a real counter-example
    (Djibouti 2020-03: severity >= 2.5 but only 3 active pillars -> False).
    """
    return (df[active_pillars_col] >= pillar_threshold) & (
        df[avg_severity_col] >= severity_threshold
    )


def alert_table(
    ars_df: pd.DataFrame,
    diagnostics_df: pd.DataFrame,
    active_pillars_df: pd.DataFrame,
    level_threshold: float = 60.0,
    spike_threshold: float = 15.0,
    persistence_threshold: float = 50.0,
    persistence_window: int = 3,
    structural_pillar_threshold: int = 4,
    structural_severity_threshold: float = 2.5,
) -> pd.DataFrame:
    """All four alert flags per country-month, matching the production
    `aeri_risk_alerts.csv` schema: `Country`, `Period`, `ARS`,
    `Alert_Level`, `Alert_Spike`, `Alert_Structural`, `Alert_Persistent`.

    `ars_df` is `ars_benchmark()`/`ars_pca()` output; `diagnostics_df` and
    `active_pillars_df` (`diagnostics()` / `aeri.pillars.active_pillars()`
    output) are merged in for the structural rule's inputs.
    """
    merged = ars_df.merge(diagnostics_df, on=["Country", "Period"], how="inner").merge(
        active_pillars_df, on=["Country", "Period"], how="inner"
    )
    out = merged[["Country", "Period", "ARS"]].copy()
    out["Alert_Level"] = level_alert(merged, threshold=level_threshold)
    out["Alert_Spike"] = spike_alert(merged, threshold=spike_threshold)
    out["Alert_Structural"] = structural_alert(
        merged,
        pillar_threshold=structural_pillar_threshold,
        severity_threshold=structural_severity_threshold,
    )
    out["Alert_Persistent"] = persistence_alert(
        merged, threshold=persistence_threshold, window=persistence_window
    )
    return out.sort_values(["Country", "Period"]).reset_index(drop=True)
