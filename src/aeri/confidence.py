"""Confidence weighting for article scores."""

from __future__ import annotations

from .config import DEFAULT_CONFIG, AERIConfig
from .pillars import active_pillar_count, assign_pillars
from .relevance import is_relevant
from .text import normalize_text, word_count


def confidence_weight(
    title: str,
    text: str,
    pillar_flags: dict[str, bool] | None = None,
    config: AERIConfig = DEFAULT_CONFIG,
) -> float:
    """W_i = clip(1 + 0.5*TitleHint + 0.2*LongText + 0.3*MultiPillar, 1, 2).

    - TitleHint: the title itself carries an economic-relevance signal.
    - LongText: the article body is at least `long_text_word_threshold`
      words (normalized word count).
    - MultiPillar: the article activates `multi_pillar_threshold` or more
      of the 8 pillars.

    `pillar_flags` can be passed in to reuse an `assign_pillars()` result
    already computed for this article; otherwise it is derived from `text`.
    """
    title_hint = 1.0 if is_relevant(title, config) else 0.0

    normalized_text = normalize_text(text)
    long_text = 1.0 if word_count(normalized_text) >= config.long_text_word_threshold else 0.0

    if pillar_flags is None:
        pillar_flags = assign_pillars(text, config)
    multi_pillar = (
        1.0 if active_pillar_count(pillar_flags) >= config.multi_pillar_threshold else 0.0
    )

    weight = 1.0 + 0.5 * title_hint + 0.2 * long_text + 0.3 * multi_pillar
    low, high = config.confidence_bounds
    return min(max(weight, low), high)
