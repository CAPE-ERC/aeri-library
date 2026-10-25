"""Economic relevance flagging, per the article's country dictionary."""

from __future__ import annotations

from .config import DEFAULT_CONFIG, AERIConfig
from .dictionary import CountryDictionary
from .match import term_matches
from .text import normalize_text


def relevance_terms(
    entry: CountryDictionary, config: AERIConfig = DEFAULT_CONFIG
) -> tuple[str, ...]:
    """The terms that count toward R_i for one country, per `config.relevance_components`."""
    terms: list[str] = []
    for component in config.relevance_components:
        terms.extend(getattr(entry, component))
    return tuple(terms)


def is_relevant(
    text: str, entry: CountryDictionary, config: AERIConfig = DEFAULT_CONFIG
) -> bool:
    """Economic relevance flag R_i: does `text` contain one of the country's
    relevance terms (see `config.relevance_components`)?

    `text` may be raw (HTML-containing) title/body text; it is normalized
    (HTML stripped, Unicode/case standardised) and matched against each
    term as a whole word/phrase, not a substring (see `aeri.match`).
    """
    normalized = normalize_text(text)
    if not normalized:
        return False
    terms = relevance_terms(entry, config)
    return any(term_matches(normalized, term) for term in terms if str(term).strip())
