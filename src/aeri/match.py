"""Unicode-aware literal term matching.

Terms are matched as complete lexical units, not arbitrary substrings. A
naive ``term in text`` check lets short or common terms match inside
unrelated words -- the severity term "war" would otherwise match inside
"warning", "warehouse", "forward" and "reward", silently inflating scores
on ordinary articles. Word boundaries are determined from the Unicode
general category of each character (letters, numbers and combining marks
count as word characters), so the same logic works for scripts that do
not use ASCII word-boundary conventions (Arabic, Ethiopic, etc.).

This mirrors the matching behaviour of the sibling ``newsindex`` package
so the two libraries agree on what "a term occurs in this article" means.
"""

from __future__ import annotations

import functools
import re
import unicodedata
from typing import Iterable, Mapping, Sequence

_APOSTROPHES = str.maketrans({"’": "'", "‘": "'", "`": "'", "´": "'"})
_DASHES = str.maketrans(
    {
        "‐": "-",
        "‑": "-",
        "‒": "-",
        "–": "-",
        "—": "-",
        "−": "-",
    }
)


def normalize(value: object) -> str:
    """Return stable Unicode text used for both dictionary terms and articles.

    Applies Unicode NFKC normalization, folds apostrophe and dash variants
    to a single form, collapses whitespace, and case-folds the result.
    """
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKC", text).translate(_APOSTROPHES).translate(_DASHES)
    return re.sub(r"\s+", " ", text).casefold().strip()


def _is_word_character(character: str) -> bool:
    if not character:
        return False
    return unicodedata.category(character)[0] in {"L", "N", "M"}


@functools.lru_cache(maxsize=32768)
def _compiled_term(term: str) -> re.Pattern[str]:
    normalized = normalize(term)
    if not normalized:
        return re.compile(r"(?!x)x")
    pieces = re.split(r"([\s-]+)", normalized)
    body_parts: list[str] = []
    for piece in pieces:
        if not piece:
            continue
        if re.fullmatch(r"[\s-]+", piece):
            body_parts.append(r"(?:-|\s)+")
        else:
            body_parts.append(re.escape(piece))
    body = "".join(body_parts)
    left = r"(?<![^\W_])" if _is_word_character(normalized[0]) else ""
    right = r"(?![^\W_])" if _is_word_character(normalized[-1]) else ""
    return re.compile(left + body + right, flags=re.UNICODE)


def term_matches(normalized_text: str, term: str) -> bool:
    """Match one term against text already returned by :func:`normalize`."""
    return bool(_compiled_term(term).search(normalized_text))


def find_terms(text: object, terms: Iterable[str]) -> list[str]:
    """Return each distinct term found in ``text``, in input order."""
    normalized = normalize(text)
    seen: set[str] = set()
    matches: list[str] = []
    for value in terms:
        term = str(value).strip()
        key = normalize(term)
        if term and key not in seen and term_matches(normalized, term):
            seen.add(key)
            matches.append(term)
    return matches


def any_term_matches(text: object, terms: Iterable[str]) -> bool:
    """True if at least one of ``terms`` occurs in ``text``."""
    normalized = normalize(text)
    return any(term_matches(normalized, str(term)) for term in terms if str(term).strip())


def component_matches(
    text: object, components: Mapping[str, Sequence[str]]
) -> dict[str, bool]:
    """Return, for each named component, whether any of its terms occur in ``text``."""
    normalized = normalize(text)
    return {
        name: any(term_matches(normalized, str(term)) for term in terms if str(term).strip())
        for name, terms in components.items()
    }
