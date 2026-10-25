"""aeri: AERI article scoring and country-month economic-risk index library."""

from __future__ import annotations

from . import ars, config, countries, dictionary, match, pillars
from .ars import (
    ARS_COMPONENTS,
    BENCHMARK_ARS_WEIGHTS,
    DEFAULT_ARS_PCA_WEIGHTS,
    Calibration,
    alert_table,
    ars_benchmark,
    ars_pca,
    calibrate_ars_weights,
    components,
    level_alert,
    load_calibration,
    persistence_alert,
    risk_band,
    save_calibration,
    spike_alert,
    structural_alert,
)
from .articles import read_articles
from .config import DEFAULT_CONFIG, PILLARS, AERIConfig
from .confidence import confidence_weight
from .index import compute_aeri, coverage_filter, diagnostics
from .pillars import (
    DEFAULT_LOG_LOWER,
    DEFAULT_LOG_UPPER,
    DEFAULT_PILLAR_WEIGHTS,
    MixedSignLoadingsError,
    active_pillar_count,
    active_pillars,
    assign_pillars,
    calibrate_pillar_weights,
    fit_transform_bounds,
    pillar_composite,
    pillar_indices,
    rank_pillars,
    transform_pillars,
)
from .relevance import is_relevant
from .scoring import article_score, score_articles
from .severity import severity_tier
from .text import normalize_text
from ._version import __version__

__all__ = [
    "config",
    "countries",
    "dictionary",
    "match",
    "pillars",
    "ars",
    "AERIConfig",
    "DEFAULT_CONFIG",
    "PILLARS",
    "normalize_text",
    "is_relevant",
    "severity_tier",
    "confidence_weight",
    "assign_pillars",
    "active_pillar_count",
    "article_score",
    "score_articles",
    "compute_aeri",
    "diagnostics",
    "coverage_filter",
    "read_articles",
    "pillar_indices",
    "active_pillars",
    "transform_pillars",
    "fit_transform_bounds",
    "DEFAULT_LOG_LOWER",
    "DEFAULT_LOG_UPPER",
    "calibrate_pillar_weights",
    "DEFAULT_PILLAR_WEIGHTS",
    "MixedSignLoadingsError",
    "pillar_composite",
    "rank_pillars",
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
    "__version__",
]
