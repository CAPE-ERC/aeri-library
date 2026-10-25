"""ARS = 100 * sum(weight_c * component_c), under a benchmark or PCA weighting.

Verified against the real `aeri_risk_score_country_period.csv` row for
Algeria 2015-01 (ARS=42.75): `100 * (0.40*0.303778 + 0.25*0.290909 +
0.20*0.416193 + 0.15*1.0)` reproduces 42.75 to the row's precision.
"""

from __future__ import annotations

import pandas as pd

from .components import ARS_COMPONENTS
from .weights import BENCHMARK_ARS_WEIGHTS, DEFAULT_ARS_PCA_WEIGHTS


def _weighted_ars(components_df: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    out = components_df[["Country", "Period"]].copy()
    contribution = sum(100.0 * weights[c] * components_df[c] for c in ARS_COMPONENTS)
    out["ARS"] = contribution
    return out


def ars_benchmark(components_df: pd.DataFrame) -> pd.DataFrame:
    """ARS under the fixed 40/25/20/15 (Intensity/Breadth/Severity/Structure)
    weights used in the production output CSVs. `components_df` is
    `components()` output. Returns `Country`, `Period`, `ARS`.
    """
    return _weighted_ars(components_df, BENCHMARK_ARS_WEIGHTS)


def ars_pca(
    components_df: pd.DataFrame, weights: dict[str, float] | None = None
) -> pd.DataFrame:
    """ARS under PCA-calibrated weights -- `DEFAULT_ARS_PCA_WEIGHTS`
    (Intensity 26.25%, Breadth 27.22%, Severity 32.23%, Structure 14.30%)
    by default, matching the paper's reported calibration. Pass
    `calibrate_ars_weights()` output to use a different calibration.
    Returns `Country`, `Period`, `ARS`.
    """
    weights = DEFAULT_ARS_PCA_WEIGHTS if weights is None else weights
    return _weighted_ars(components_df, weights)
