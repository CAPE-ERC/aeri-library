"""PCA-calibrated pillar weights for pillar_composite().

Equation (11) of the CAPE AERI/ARS methodology (Main_AERI_ARS_Paper): the
first principal component of the standardised, transformed pillars,
converted back to the bounded scale and normalised to sum to 1. The same
procedure (on different inputs) also calibrates the ARS component weights.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import PILLARS

#: Frozen first-principal-component weights (Table 4, Main_AERI_ARS_Paper),
#: calibrated on 6,238 country-months with >=100 articles, Jan 2015-Jul
#: 2025 (PC1 explains 52.50% of standardised variance across the 8
#: transformed pillars).
DEFAULT_PILLAR_WEIGHTS: dict[str, float] = {
    "InflationRisk": 0.1295,
    "FXExternalRisk": 0.1321,
    "DebtFiscalRisk": 0.1729,
    "FinancialSectorRisk": 0.1730,
    "GrowthRealEconomyRisk": 0.1190,
    "CommoditySupplyRisk": 0.0648,
    "PoliticalEconomyRisk": 0.0992,
    "ClimateDisasterRisk": 0.1095,
}


class MixedSignLoadingsError(ValueError):
    """The first principal component's loadings aren't (after orientation)
    all one sign, so the calibration panel doesn't support a single
    coherent "overall risk" weighting."""


def calibrate_pillar_weights(
    transformed_df: pd.DataFrame, max_negative_share: float = 0.0
) -> dict[str, float]:
    """First-principal-component weights for the 8 pillars.

    `transformed_df` should be `transform_pillars()` output (Q in [0, 1])
    for the calibration panel. Standardises each pillar, takes the leading
    eigenvector of the covariance matrix (oriented so higher component
    values mean higher pillar risk, i.e. the loadings sum positive),
    converts the standardised loadings back to the bounded-input scale, and
    normalises the result to sum to 1.

    Raises `MixedSignLoadingsError` if more than `max_negative_share` of the
    oriented loadings are negative, or if any pillar has zero variance in
    the panel (can't be standardised) -- the calibration panel doesn't
    support a single coherent weighting. The default (0.0) matches the
    "rejects mixed-sign loadings" rule documented for this calibration
    procedure: no negative loadings are tolerated.
    """
    values = transformed_df[list(PILLARS)].to_numpy(dtype=float)
    mu = values.mean(axis=0)
    sigma = values.std(axis=0, ddof=0)
    zero_variance = [pillar for pillar, s in zip(PILLARS, sigma) if s == 0]
    if zero_variance:
        raise MixedSignLoadingsError(
            f"pillars with zero variance in the calibration panel: {zero_variance}"
        )

    standardized = (values - mu) / sigma
    covariance = np.cov(standardized, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    loadings = eigenvectors[:, int(np.argmax(eigenvalues))]
    if loadings.sum() < 0:
        loadings = -loadings

    negative_share = float(np.mean(loadings < 0))
    if negative_share > max_negative_share:
        raise MixedSignLoadingsError(
            f"{negative_share:.0%} of PC1 loadings are negative after orientation; "
            "calibration panel does not support a single coherent weighting"
        )

    raw_weights = loadings / sigma
    normalized = raw_weights / raw_weights.sum()
    return dict(zip(PILLARS, (float(w) for w in normalized)))
