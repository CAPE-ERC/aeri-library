"""Economic relevance flagging."""

from __future__ import annotations

from .config import DEFAULT_CONFIG, AERIConfig
from .text import normalize_text


def is_relevant(text: str, config: AERIConfig = DEFAULT_CONFIG) -> bool:
    """Economic relevance flag R_i from the multilingual keyword dictionary.

    `text` may be raw (HTML-containing) or already normalized; it is
    re-normalized defensively so the function is safe to call directly on
    raw article text or titles.
    """
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in config.relevance_keywords)
