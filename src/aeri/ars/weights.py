"""Fixed and PCA-calibrated ARS component weights.

`ars_benchmark()` uses the fixed 40/25/20/15 weights already used in the
production output CSVs; `ars_pca()` uses the first-principal-component
weights from the paper (Table 3). `calibrate_ars_weights()` recomputes
PCA weights from a different calibration panel, via the same procedure
(equation 11) as `aeri.pillars.weights.calibrate_pillar_weights`.
"""

from __future__ import annotations

import pandas as pd

from .._pca import MixedSignLoadingsError, first_principal_component_weights
from .components import ARS_COMPONENTS

#: Fixed benchmark weights used in the production output CSVs.
BENCHMARK_ARS_WEIGHTS: dict[str, float] = {
    "Intensity": 0.40,
    "Breadth": 0.25,
    "Severity": 0.20,
    "Structure": 0.15,
}

#: Frozen first-principal-component weights (Table 3, Main_AERI_ARS_Paper),
#: PC1 explains 62.22% of standardised variance across the 4 components.
DEFAULT_ARS_PCA_WEIGHTS: dict[str, float] = {
    "Intensity": 0.2625,
    "Breadth": 0.2722,
    "Severity": 0.3223,
    "Structure": 0.1430,
}


def calibrate_ars_weights(
    components_df: pd.DataFrame, max_negative_share: float = 0.0
) -> dict[str, float]:
    """First-principal-component weights for the 4 ARS components.

    `components_df` should be `components()` output for the calibration
    panel. See `aeri._pca.first_principal_component_weights` for the
    procedure and the meaning of `max_negative_share`; raises
    `MixedSignLoadingsError` under the same conditions.
    """
    matrix = components_df[list(ARS_COMPONENTS)].to_numpy(dtype=float)
    return first_principal_component_weights(matrix, list(ARS_COMPONENTS), max_negative_share)
