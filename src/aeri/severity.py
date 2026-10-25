"""Ordinal severity tiering."""

from __future__ import annotations

from .config import DEFAULT_CONFIG, AERIConfig
from .match import term_matches
from .text import normalize_text


def severity_tier(text: str, config: AERIConfig = DEFAULT_CONFIG) -> int:
    """Ordinal severity S_i from 0 to 4; the highest tier matched wins.

    Matches whole words/phrases (see `aeri.match`), not substrings -- so
    the tier-4 term "war" does not match inside "warning" or "forward".
    """
    normalized = normalize_text(text)
    if not normalized:
        return 0
    for tier in sorted(config.severity_keywords, reverse=True):
        keywords = config.severity_keywords[tier]
        if any(term_matches(normalized, keyword) for keyword in keywords):
            return tier
    return 0
