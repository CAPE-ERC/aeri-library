"""Ordinal severity tiering."""

from __future__ import annotations

from .config import DEFAULT_CONFIG, AERIConfig
from .text import normalize_text


def severity_tier(text: str, config: AERIConfig = DEFAULT_CONFIG) -> int:
    """Ordinal severity S_i from 0 to 4; the highest tier matched wins."""
    normalized = normalize_text(text)
    if not normalized:
        return 0
    for tier in sorted(config.severity_keywords, reverse=True):
        keywords = config.severity_keywords[tier]
        if any(keyword in normalized for keyword in keywords):
            return tier
    return 0
