"""Pillar flagging: which of the 8 economic-risk pillars an article touches."""

from __future__ import annotations

from ..config import DEFAULT_CONFIG, PILLARS, AERIConfig
from ..match import term_matches
from ..text import normalize_text


def assign_pillars(
    text: str, config: AERIConfig = DEFAULT_CONFIG
) -> dict[str, bool]:
    """Flags for the 8 pillars; one article can activate several.

    Returns a dict keyed by pillar name (see `aeri.config.PILLARS`) with
    boolean values. Matches whole words/phrases, not substrings.
    """
    normalized = normalize_text(text)
    flags: dict[str, bool] = {}
    for pillar in PILLARS:
        keywords = config.pillar_keywords.get(pillar, ())
        flags[pillar] = bool(normalized) and any(
            term_matches(normalized, keyword) for keyword in keywords
        )
    return flags


def active_pillar_count(flags: dict[str, bool]) -> int:
    """Number of pillars flagged as active for a single article."""
    return sum(1 for active in flags.values() if active)
