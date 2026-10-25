"""Per-article scoring and DataFrame-level scoring pipeline."""

from __future__ import annotations

import pandas as pd

from .confidence import confidence_weight
from .config import DEFAULT_CONFIG, PILLARS, AERIConfig
from .dictionary import Dictionary
from .pillars import active_pillar_count, assign_pillars
from .relevance import is_relevant
from .severity import severity_tier


def article_score(relevant: bool, severity: int, weight: float) -> float:
    """A_i = R_i * S_i * W_i."""
    return float(relevant) * float(severity) * float(weight)


def score_articles(
    articles: pd.DataFrame,
    dictionary: Dictionary,
    *,
    country_col: str = "country",
    title_col: str = "title",
    text_col: str = "text",
    config: AERIConfig = DEFAULT_CONFIG,
) -> pd.DataFrame:
    """Score every article in `articles` and append the scoring columns.

    Relevance, severity and pillar matching run on the article's title and
    body concatenated (``x_i = title + " " + text``), per the AERI
    methodology -- not on the body alone.

    Adds: `relevant` (R_i), `severity` (S_i), `confidence` (W_i),
    `article_score` (A_i), `active_pillars`, and one boolean column per
    pillar (see `aeri.config.PILLARS`).

    Every value in `articles[country_col]` must be a key of `dictionary`
    (see `aeri.dictionary.load` and `aeri.countries.canonicalize`); a
    missing country raises `KeyError` naming it, since silently skipping a
    country would produce an undercount rather than a visible failure.

    Does not mutate `articles`; returns a new DataFrame.
    """
    missing = sorted(set(articles[country_col]) - set(dictionary.countries))
    if missing:
        raise KeyError(f"countries missing from dictionary: {missing}")

    out = articles.copy()

    titles = out[title_col].fillna("").astype(str)
    texts = out[text_col].fillna("").astype(str)
    combined = titles + " " + texts

    relevant: list[bool] = []
    severity: list[int] = []
    confidence: list[float] = []
    pillar_flags_list: list[dict[str, bool]] = []

    for country, title, text, full_text in zip(out[country_col], titles, texts, combined):
        entry = dictionary[country]
        flags = assign_pillars(full_text, config)
        pillar_flags_list.append(flags)
        is_r = is_relevant(full_text, entry, config)
        relevant.append(is_r)
        # S_i = 0 when R_i = 0: non-economic articles carry no severity.
        severity.append(severity_tier(full_text, config) if is_r else 0)
        confidence.append(confidence_weight(title, text, entry, flags, config))

    out["relevant"] = relevant
    out["severity"] = severity
    out["confidence"] = confidence
    out["article_score"] = [
        article_score(r, s, w) for r, s, w in zip(relevant, severity, confidence)
    ]
    out["active_pillars"] = [active_pillar_count(flags) for flags in pillar_flags_list]
    for pillar in PILLARS:
        out[pillar] = [flags[pillar] for flags in pillar_flags_list]

    return out
