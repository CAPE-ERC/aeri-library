"""Text normalization utilities."""

from __future__ import annotations

import html
import re

from .match import normalize as _match_normalize

_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(text: str) -> str:
    """Remove HTML tags and unescape HTML entities."""
    if not text:
        return ""
    without_tags = _TAG_RE.sub(" ", text)
    return html.unescape(without_tags)


def normalize_text(text: str) -> str:
    """Strip HTML, then standardise case, whitespace and Unicode.

    Delegates the Unicode/case/whitespace step to :func:`aeri.match.normalize`
    so scoring text and dictionary terms are normalized identically.
    """
    return _match_normalize(strip_html(text) if text else "")


def word_count(text: str) -> int:
    """Word count of already-normalized (or raw) text."""
    if not text:
        return 0
    return len(text.split())
