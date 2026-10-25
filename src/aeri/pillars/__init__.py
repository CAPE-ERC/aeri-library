"""aeri.pillars: per-article pillar flags and the pillar-composite pipeline.

Libraries 1 and 2 from the AERI/ARS proposal live together here: `flags`
(per-article pillar flagging, feeding `aeri.scoring`) and `indices` /
`transform` / `weights` / `composite` (the country-month pillar indices,
their [0, 1] transform, PCA-calibrated weights, and the combined
cross-pillar composite).
"""

from __future__ import annotations

from .composite import pillar_composite, rank_pillars
from .flags import active_pillar_count, assign_pillars
from .indices import active_pillars, pillar_indices
from .transform import DEFAULT_LOG_LOWER, DEFAULT_LOG_UPPER, fit_transform_bounds, transform_pillars
from .weights import DEFAULT_PILLAR_WEIGHTS, MixedSignLoadingsError, calibrate_pillar_weights

__all__ = [
    "assign_pillars",
    "active_pillar_count",
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
]
