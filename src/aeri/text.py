"""Text normalization utilities."""

from __future__ import annotations

import html
import re
import unicodedata

_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def strip_html(text: str) -> str:
    """Remove HTML tags and unescape HTML entities."""
    if not text:
        return ""
    without_tags = _TAG_RE.sub(" ", text)
    return html.unescape(without_tags)


def normalize_text(text: str) -> str:
    """Strip HTML, then standardise case, whitespace and Unicode.

    Unicode is decomposed (NFKD) and combining marks (accents, Arabic
    tashkeel, etc.) are dropped so that keyword matching is accent- and
    diacritic-insensitive across languages.
    """
    if not text:
        return ""
    cleaned = strip_html(text)
    decomposed = unicodedata.normalize("NFKD", cleaned)
    without_marks = "".join(
        ch for ch in decomposed if unicodedata.category(ch) != "Mn"
    )
    lowered = without_marks.lower()
    return _WHITESPACE_RE.sub(" ", lowered).strip()


def word_count(text: str) -> int:
    """Word count of already-normalized (or raw) text."""
    if not text:
        return 0
    return len(text.split())
