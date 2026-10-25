"""PCA-calibrated pillar weights for pillar_composite().

Equation (11) of the CAPE AERI/ARS methodology (Main_AERI_ARS_Paper): the
first principal component of the standardised, transformed pillars,
converted back to the bounded scale and normalised to sum to 1. The same
procedure (on different inputs) also calibrates the ARS component weights
(see `aeri.ars.weights.calibrate_ars_weights`).
"""

from __future__ import annotations

import pandas as pd

from .._pca import MixedSignLoadingsError, first_principal_component_weights
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


def calibrate_pillar_weights(
    transformed_df: pd.DataFrame, max_negative_share: float = 0.0
) -> dict[str, float]:
    """First-principal-component weights for the 8 pillars.

    `transformed_df` should be `transform_pillars()` output (Q in [0, 1])
    for the calibration panel. See
    `aeri._pca.first_principal_component_weights` for the procedure and
    the meaning of `max_negative_share`; raises `MixedSignLoadingsError`
    under the same conditions.
    """
    matrix = transformed_df[list(PILLARS)].to_numpy(dtype=float)
    return first_principal_component_weights(matrix, list(PILLARS), max_negative_share)
