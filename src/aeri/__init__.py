"""aeri: AERI article scoring and country-month economic-risk index library."""

from __future__ import annotations

from . import config, countries, dictionary, match
from .articles import read_articles
from .config import DEFAULT_CONFIG, PILLARS, AERIConfig
from .confidence import confidence_weight
from .index import compute_aeri, coverage_filter, diagnostics
from .pillars import active_pillar_count, assign_pillars
from .relevance import is_relevant
from .scoring import article_score, score_articles
from .severity import severity_tier
from .text import normalize_text

__version__ = "0.1.0"

__all__ = [
    "config",
    "countries",
    "dictionary",
    "match",
    "AERIConfig",
    "DEFAULT_CONFIG",
    "PILLARS",
    "normalize_text",
    "is_relevant",
    "severity_tier",
    "confidence_weight",
    "assign_pillars",
    "active_pillar_count",
    "article_score",
    "score_articles",
    "compute_aeri",
    "diagnostics",
    "coverage_filter",
    "read_articles",
    "__version__",
]
