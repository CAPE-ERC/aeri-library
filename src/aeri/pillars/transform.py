"""Pillar transform: log(1+P) scaled to [0,1] via frozen 1st/99th-percentile bounds.

Q_p = clip((log(1 + P_p) - a_p) / (b_p - a_p), 0, 1) -- equation (9) of the
CAPE AERI/ARS methodology (Main_AERI_ARS_Paper, Table 4).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import PILLARS

#: Frozen log(1+P) 1st/99th-percentile bounds, calibrated on 6,238
#: country-months with >=100 articles, Jan 2015-Jul 2025. Every pillar's
#: lower bound is 0: at least 1% of country-months sit at zero intensity
#: for each pillar.
DEFAULT_LOG_LOWER: dict[str, float] = {pillar: 0.0 for pillar in PILLARS}
DEFAULT_LOG_UPPER: dict[str, float] = {
    "InflationRisk": 2.9629,
    "FXExternalRisk": 4.2958,
    "DebtFiscalRisk": 4.3550,
    "FinancialSectorRisk": 4.5177,
    "GrowthRealEconomyRisk": 2.6486,
    "CommoditySupplyRisk": 1.0248,
    "PoliticalEconomyRisk": 2.9873,
    "ClimateDisasterRisk": 2.3585,
}


def fit_transform_bounds(pillar_df: pd.DataFrame) -> tuple[dict[str, float], dict[str, float]]:
    """Fit log(1+P) 1st/99th-percentile bounds (lower, upper) from a
    calibration panel -- typically `pillar_indices()` output pooled across
    many country-months.

    Recalibrating changes every subsequent `transform_pillars()` output, so
    treat the result as a new, separately-tracked measurement vintage
    (matching the paper's own frozen-bounds convention) rather than
    recalibrating casually.
    """
    lower: dict[str, float] = {}
    upper: dict[str, float] = {}
    for pillar in PILLARS:
        log_values = np.log1p(pillar_df[pillar].to_numpy(dtype=float))
        lower[pillar] = float(np.percentile(log_values, 1))
        upper[pillar] = float(np.percentile(log_values, 99))
    return lower, upper


def transform_pillars(
    pillar_df: pd.DataFrame,
    lower: dict[str, float] | None = None,
    upper: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Q_p = clip((log(1 + P_p) - a_p) / (b_p - a_p), 0, 1) for each pillar.

    `pillar_df` is `pillar_indices()` output. `lower`/`upper` default to the
    frozen calibration bounds (`DEFAULT_LOG_LOWER`/`DEFAULT_LOG_UPPER`); pass
    `fit_transform_bounds()` output to use a different calibration panel.
    Returns a new DataFrame with `Country`/`Period` plus each pillar column
    replaced by its [0, 1]-scaled value.
    """
    lower = DEFAULT_LOG_LOWER if lower is None else lower
    upper = DEFAULT_LOG_UPPER if upper is None else upper

    out = pillar_df.copy()
    for pillar in PILLARS:
        log_values = np.log1p(out[pillar].astype(float))
        a, b = lower[pillar], upper[pillar]
        span = b - a
        scaled = (log_values - a) / span if span else log_values * 0.0
        out[pillar] = scaled.clip(lower=0.0, upper=1.0)
    return out
