"""aeri.ars: the ARS composite score and early-warning alerts.

Libraries 3 and 4 from the AERI/ARS proposal live together here (the
proposal names Library 4 "riskalert, or part of ars"): `components` /
`weights` / `score` / `bands` / `calibration` (ARS itself), and `alerts`
(level/spike/structural/persistence early-warning flags).
"""

from __future__ import annotations

from .alerts import alert_table, level_alert, persistence_alert, spike_alert, structural_alert
from .bands import risk_band
from .calibration import Calibration, load_calibration, save_calibration
from .components import ARS_COMPONENTS, components
from .score import ars_benchmark, ars_pca
from .weights import BENCHMARK_ARS_WEIGHTS, DEFAULT_ARS_PCA_WEIGHTS, calibrate_ars_weights

__all__ = [
    "ARS_COMPONENTS",
    "components",
    "BENCHMARK_ARS_WEIGHTS",
    "DEFAULT_ARS_PCA_WEIGHTS",
    "calibrate_ars_weights",
    "ars_benchmark",
    "ars_pca",
    "risk_band",
    "Calibration",
    "save_calibration",
    "load_calibration",
    "level_alert",
    "spike_alert",
    "persistence_alert",
    "structural_alert",
    "alert_table",
]
