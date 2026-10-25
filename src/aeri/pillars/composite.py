"""Combined cross-pillar composite and per-country-period pillar ranking."""

from __future__ import annotations

import pandas as pd

from ..config import PILLARS
from .weights import DEFAULT_PILLAR_WEIGHTS


def pillar_composite(
    transformed_df: pd.DataFrame, weights: dict[str, float] | None = None
) -> pd.DataFrame:
    """H_t = sum_p(100 * u_p * Q_p), the combined cross-pillar measure.

    `transformed_df` should be `transform_pillars()` output (Q in [0, 1]).
    `weights` defaults to the frozen calibration (`DEFAULT_PILLAR_WEIGHTS`);
    pass `calibrate_pillar_weights()` output to use a different calibration.
    Returns `Country`, `Period`, `PillarComposite`.
    """
    weights = DEFAULT_PILLAR_WEIGHTS if weights is None else weights
    out = transformed_df[["Country", "Period"]].copy()
    contribution = sum(100.0 * weights[pillar] * transformed_df[pillar] for pillar in PILLARS)
    out["PillarComposite"] = contribution
    return out


def rank_pillars(pillar_row: pd.Series) -> list[tuple[str, float]]:
    """Rank one country-period's pillars by raw `pillar_indices()` value,
    descending -- e.g. `[("PoliticalEconomyRisk", 12.81), ("DebtFiscalRisk",
    7.95), ...]`.

    `pillar_row` is a single row of `pillar_indices()` output. For every
    row of a multi-row DataFrame, apply this per-row, e.g.
    `pillar_df.apply(rank_pillars, axis=1)`.
    """
    values = [(pillar, float(pillar_row[pillar])) for pillar in PILLARS]
    return sorted(values, key=lambda item: item[1], reverse=True)
