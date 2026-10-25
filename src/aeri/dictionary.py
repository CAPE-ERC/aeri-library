"""Load and validate country keyword dictionaries for relevance classification.

The on-disk format is the EPTU schema shared across CAPE's EPU, ETU, TPU
and AERI work: one JSON document mapping each country to Economic /
Policy / Uncertainty (/ Trade) term lists. AERI's economic-relevance flag
``R_i`` is driven by the Economic component; Policy and Uncertainty are
carried along for libraries (such as ``newsindex``) that need all three.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from .countries import canonicalize
from .match import normalize

_FIELD_MAP = {
    "economic": "ECONOMY_TERMS",
    "policy": "POLICY_TERMS",
    "uncertainty": "UNCERTAINTY_TERMS",
    "trade": "TRADE_TERMS",
}


@dataclass(frozen=True)
class CountryDictionary:
    """One country's keyword lists."""

    country: str
    languages: tuple[str, ...]
    economic: tuple[str, ...]
    policy: tuple[str, ...]
    uncertainty: tuple[str, ...]
    trade: tuple[str, ...] = ()


@dataclass(frozen=True)
class Dictionary:
    """A loaded, country-keyed keyword dictionary."""

    countries: dict[str, CountryDictionary]
    schema: str = ""
    source: Path | None = None
    meta: dict = field(default_factory=dict)

    def __getitem__(self, country: str) -> CountryDictionary:
        return self.countries[country]

    def __contains__(self, country: str) -> bool:
        return country in self.countries

    def __iter__(self):
        return iter(self.countries)

    def __len__(self) -> int:
        return len(self.countries)


def load(path: str | Path) -> Dictionary:
    """Load a country keyword dictionary from an EPTU-schema JSON file.

    Country keys are canonicalized with :func:`aeri.countries.canonicalize`
    (so the dictionary's own ``"Cabo Verde"`` resolves under the canonical
    ``"Cape Verde"``, matching :mod:`aeri.countries`).
    """
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    rows = raw.get("countries", raw) if isinstance(raw, dict) else {}
    countries: dict[str, CountryDictionary] = {}
    for country, payload in rows.items():
        canonical = canonicalize(country)
        countries[canonical] = CountryDictionary(
            country=canonical,
            languages=tuple(payload.get("languages", [])),
            economic=tuple(payload.get(_FIELD_MAP["economic"], [])),
            policy=tuple(payload.get(_FIELD_MAP["policy"], [])),
            uncertainty=tuple(payload.get(_FIELD_MAP["uncertainty"], [])),
            trade=tuple(payload.get(_FIELD_MAP["trade"], [])),
        )
    meta = raw.get("_meta", {}) if isinstance(raw, dict) else {}
    return Dictionary(countries=countries, schema=meta.get("schema", ""), source=path, meta=meta)


def validate(dictionary: Dictionary) -> list[dict]:
    """Audit a dictionary for countries with an empty Economic term list."""
    issues: list[dict] = []
    for country, entry in dictionary.countries.items():
        if not entry.economic:
            issues.append({"country": country, "issue": "empty_economic_terms"})
    return issues


def fingerprint(dictionary: Dictionary) -> str:
    """Return a stable hash identifying the exact dictionary contents.

    Two dictionaries with the same country and term content hash
    identically regardless of key order; any change to a term list or the
    set of countries changes the fingerprint.
    """
    canonical = {
        country: {
            "languages": sorted(entry.languages),
            "economic": sorted(normalize(t) for t in entry.economic),
            "policy": sorted(normalize(t) for t in entry.policy),
            "uncertainty": sorted(normalize(t) for t in entry.uncertainty),
            "trade": sorted(normalize(t) for t in entry.trade),
        }
        for country, entry in sorted(dictionary.countries.items())
    }
    blob = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
