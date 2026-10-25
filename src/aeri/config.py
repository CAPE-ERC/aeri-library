"""Configuration and default keyword sets for AERI scoring.

The economic-relevance dictionary is real production data loaded
separately via :mod:`aeri.dictionary` (country-specific, see
``data/aeri_country_keywords.json``). The severity-tier and pillar
keyword sets below have **no equivalent production source** -- no
dictionary for them was found anywhere in the underlying research
materials -- so these are a first-pass, hand-curated starting point that
needs calibration against real coverage before being treated as final.
Every scoring function accepts an `AERIConfig` so a project can supply
its own keyword sets without forking the library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

#: The 8 AERI risk pillars, named to match the production AERI Pillar API
#: catalog (`InflationRisk`, `FXExternalRisk`, ...) and the
#: `aeri_pillars_country_period.csv` column headers it publishes.
PILLARS: tuple[str, ...] = (
    "InflationRisk",
    "FXExternalRisk",
    "DebtFiscalRisk",
    "FinancialSectorRisk",
    "GrowthRealEconomyRisk",
    "CommoditySupplyRisk",
    "PoliticalEconomyRisk",
    "ClimateDisasterRisk",
)

DEFAULT_SEVERITY_KEYWORDS: dict[int, tuple[str, ...]] = {
    1: (
        "concern", "warning", "pressure", "risk", "slowdown", "softening",
        "worry", "caution", "uncertainty",
    ),
    2: (
        "falling", "decline", "drop", "shortage", "strain", "weakening",
        "job losses", "cutbacks", "downgrade", "rising prices", "protest",
        "strike",
    ),
    3: (
        "crisis", "collapse", "plunge", "default", "devaluation", "emergency",
        "unrest", "shutdown", "severe shortage", "mass layoffs", "coup",
        "credit downgrade",
    ),
    4: (
        "catastrophe", "famine", "hyperinflation", "economic collapse",
        "state of emergency", "war", "coup d'etat", "humanitarian crisis",
        "bankruptcy", "sovereign default", "civil war", "mass starvation",
        "currency collapse",
    ),
}

DEFAULT_PILLAR_KEYWORDS: dict[str, tuple[str, ...]] = {
    "InflationRisk": (
        "inflation", "deflation", "consumer price", "cost of living",
        "price hike", "price increase", "food price", "fuel price", "cpi",
        "disinflation", "hyperinflation", "rising prices",
    ),
    "FXExternalRisk": (
        "exchange rate", "devaluation", "depreciation", "currency", "forex",
        "foreign reserves", "balance of payments", "current account",
        "trade deficit", "capital flight", "remittance", "export", "import",
    ),
    "DebtFiscalRisk": (
        "public debt", "sovereign debt", "fiscal deficit", "budget deficit",
        "treasury", "government spending", "austerity", "imf", "world bank",
        "bailout", "credit rating", "default", "bond", "eurobond",
        "tax revenue",
    ),
    "FinancialSectorRisk": (
        "bank", "banking sector", "interest rate", "central bank",
        "monetary policy", "non-performing loan", "liquidity",
        "credit crunch", "stock exchange", "bond market", "financial sector",
        "lending rate",
    ),
    "GrowthRealEconomyRisk": (
        "gdp", "economic growth", "recession", "unemployment", "job losses",
        "manufacturing", "industrial output", "retail sales",
        "consumer spending", "business confidence", "economic slowdown",
    ),
    "CommoditySupplyRisk": (
        "commodity price", "oil price", "gas price", "mining", "agriculture",
        "harvest", "food supply", "supply chain", "shortage",
        "import dependency", "wheat", "maize", "fertilizer",
    ),
    "PoliticalEconomyRisk": (
        "election", "coup", "protest", "strike", "sanctions", "corruption",
        "policy reform", "political instability", "government shutdown",
        "regulation", "nationalization", "unrest",
    ),
    "ClimateDisasterRisk": (
        "drought", "flood", "famine", "climate change", "natural disaster",
        "cyclone", "locust", "food insecurity", "humanitarian crisis",
        "displacement", "crop failure",
    ),
}


@dataclass(frozen=True)
class AERIConfig:
    """Bundles the thresholds and (non-relevance) keyword sets used across
    the pipeline. Severity and pillar keywords default to the first-pass
    sets above; relevance is intentionally not part of this config -- it
    comes from a country-keyed :class:`aeri.dictionary.Dictionary`.
    """

    severity_keywords: Mapping[int, Sequence[str]] = field(
        default_factory=lambda: DEFAULT_SEVERITY_KEYWORDS
    )
    pillar_keywords: Mapping[str, Sequence[str]] = field(
        default_factory=lambda: DEFAULT_PILLAR_KEYWORDS
    )
    long_text_word_threshold: int = 300
    multi_pillar_threshold: int = 2
    confidence_bounds: tuple[float, float] = (1.0, 2.0)
    coverage_min_articles: int = 100
    #: Which dictionary component(s) count toward R_i. Defaults to the
    #: Economic component alone; add "policy" to also count policy terms.
    #: Unverified against source -- see README.
    relevance_components: tuple[str, ...] = ("economic",)


DEFAULT_CONFIG = AERIConfig()
