"""Configuration and dictionary loading for AERI scoring."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib import resources
from typing import Mapping, Sequence

PILLARS: tuple[str, ...] = (
    "inflation",
    "fx_and_external",
    "debt_and_fiscal",
    "financial_sector",
    "growth_and_real_economy",
    "commodity_supply",
    "political_economy",
    "climate_and_disaster",
)


def _load_json(filename: str) -> dict:
    with resources.files("aeri.data").joinpath(filename).open(
        "r", encoding="utf-8"
    ) as fh:
        return json.load(fh)


def _flatten_relevance(raw: Mapping[str, Sequence[str]]) -> frozenset[str]:
    keywords: set[str] = set()
    for terms in raw.values():
        keywords.update(term.lower() for term in terms)
    return frozenset(keywords)


def _flatten_severity(
    raw: Mapping[str, Mapping[str, Sequence[str]]],
) -> dict[int, frozenset[str]]:
    tiers: dict[int, set[str]] = {1: set(), 2: set(), 3: set(), 4: set()}
    for lang_tiers in raw.values():
        for tier_str, terms in lang_tiers.items():
            tier = int(tier_str)
            tiers.setdefault(tier, set()).update(term.lower() for term in terms)
    return {tier: frozenset(terms) for tier, terms in tiers.items()}


@dataclass(frozen=True)
class AERIConfig:
    """Bundles the dictionaries and thresholds used across the pipeline.

    All fields can be overridden to plug in a different (or expanded)
    keyword dictionary without touching the scoring logic.
    """

    relevance_keywords: frozenset[str]
    severity_keywords: Mapping[int, frozenset[str]]
    pillar_keywords: Mapping[str, frozenset[str]]
    long_text_word_threshold: int = 300
    coverage_min_articles: int = 100
    confidence_bounds: tuple[float, float] = (1.0, 2.0)
    multi_pillar_threshold: int = 2

    @classmethod
    def default(cls) -> "AERIConfig":
        relevance_raw = _load_json("relevance_keywords.json")
        severity_raw = _load_json("severity_keywords.json")
        pillar_raw = _load_json("pillar_keywords.json")
        pillar_keywords = {
            pillar: frozenset(term.lower() for term in terms)
            for pillar, terms in pillar_raw.items()
        }
        return cls(
            relevance_keywords=_flatten_relevance(relevance_raw),
            severity_keywords=_flatten_severity(severity_raw),
            pillar_keywords=pillar_keywords,
        )


DEFAULT_CONFIG = AERIConfig.default()
