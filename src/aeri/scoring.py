"""Per-article scoring and DataFrame-level scoring pipeline."""

from __future__ import annotations

import pandas as pd

from .confidence import confidence_weight
from .config import DEFAULT_CONFIG, PILLARS, AERIConfig
from .pillars import active_pillar_count, assign_pillars
from .relevance import is_relevant
from .severity import severity_tier


def article_score(relevant: bool, severity: int, weight: float) -> float:
    """A_i = R_i * S_i * W_i."""
    return float(relevant) * float(severity) * float(weight)


def score_dataframe(
    df: pd.DataFrame,
    title_col: str = "title",
    text_col: str = "text",
    config: AERIConfig = DEFAULT_CONFIG,
) -> pd.DataFrame:
    """Score every article in `df` and append the scoring columns.

    Adds: `relevant` (R_i), `severity` (S_i), `confidence` (W_i),
    `article_score` (A_i), `active_pillars`, and one boolean column per
    pillar (`pillar_<name>`).

    Does not mutate `df`; returns a new DataFrame.
    """
    out = df.copy()

    titles = out[title_col].fillna("").astype(str)
    texts = out[text_col].fillna("").astype(str)

    relevant = texts.apply(lambda t: is_relevant(t, config))
    severity = texts.apply(lambda t: severity_tier(t, config))
    pillar_flags = texts.apply(lambda t: assign_pillars(t, config))
    active_pillars = pillar_flags.apply(active_pillar_count)

    confidence = [
        confidence_weight(title, text, flags, config)
        for title, text, flags in zip(titles, texts, pillar_flags)
    ]

    out["relevant"] = relevant
    out["severity"] = severity
    out["confidence"] = confidence
    out["article_score"] = [
        article_score(r, s, w) for r, s, w in zip(relevant, severity, confidence)
    ]
    out["active_pillars"] = active_pillars
    for pillar in PILLARS:
        out[f"pillar_{pillar}"] = pillar_flags.apply(lambda flags: flags[pillar])

    return out
