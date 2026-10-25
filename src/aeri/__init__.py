"""aeri: AERI article scoring and country-month index library."""

from .config import DEFAULT_CONFIG, PILLARS, AERIConfig
from .confidence import confidence_weight
from .index import coverage_filter, compute_aeri, diagnostics
from .io import load_articles_csv, load_articles_tree
from .pillars import active_pillar_count, assign_pillars
from .relevance import is_relevant
from .scoring import article_score, score_dataframe
from .severity import severity_tier
from .text import normalize_text

__version__ = "0.1.0"

__all__ = [
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
    "score_dataframe",
    "compute_aeri",
    "diagnostics",
    "coverage_filter",
    "load_articles_csv",
    "load_articles_tree",
    "__version__",
]
