"""The 54 African countries covered by AERI: regions, ISO3 codes and aliases.

Matches the canonical country list used by the production AERI Pillar API
(``app/catalog.py``) and the ``newsindex`` sibling library, so a country
name produced by one CAPE library is understood by the others.
"""

from __future__ import annotations

REGIONS: dict[str, list[str]] = {
    "Central": [
        "Cameroon",
        "Central African Republic",
        "Chad",
        "Congo",
        "Congo DRC",
        "Equatorial Guinea",
        "Gabon",
    ],
    "East": [
        "Burundi",
        "Comoros",
        "Djibouti",
        "Eritrea",
        "Ethiopia",
        "Kenya",
        "Rwanda",
        "Seychelles",
        "Somalia",
        "South Sudan",
        "Sudan",
        "Tanzania",
        "Uganda",
    ],
    "North": ["Algeria", "Egypt", "Libya", "Mauritania", "Morocco", "Tunisia"],
    "Southern": [
        "Angola",
        "Botswana",
        "Eswatini",
        "Lesotho",
        "Madagascar",
        "Malawi",
        "Mauritius",
        "Mozambique",
        "Namibia",
        "Sao Tome and Principe",
        "South Africa",
        "Zambia",
        "Zimbabwe",
    ],
    "West": [
        "Benin",
        "Burkina-Faso",
        "Cape Verde",
        "Gambia",
        "Ghana",
        "Guinea",
        "Guinea-Bissau",
        "Ivory Coast",
        "Liberia",
        "Mali",
        "Niger",
        "Nigeria",
        "Senegal",
        "Sierra Leone",
        "Togo",
    ],
}

ISO3: dict[str, str] = {
    "Algeria": "DZA", "Angola": "AGO", "Benin": "BEN", "Botswana": "BWA",
    "Burkina-Faso": "BFA", "Burundi": "BDI", "Cameroon": "CMR", "Cape Verde": "CPV",
    "Central African Republic": "CAF", "Chad": "TCD", "Comoros": "COM", "Congo": "COG",
    "Congo DRC": "COD", "Djibouti": "DJI", "Egypt": "EGY", "Equatorial Guinea": "GNQ",
    "Eritrea": "ERI", "Eswatini": "SWZ", "Ethiopia": "ETH", "Gabon": "GAB",
    "Gambia": "GMB", "Ghana": "GHA", "Guinea": "GIN", "Guinea-Bissau": "GNB",
    "Ivory Coast": "CIV", "Kenya": "KEN", "Lesotho": "LSO", "Liberia": "LBR",
    "Libya": "LBY", "Madagascar": "MDG", "Malawi": "MWI", "Mali": "MLI",
    "Mauritania": "MRT", "Mauritius": "MUS", "Morocco": "MAR", "Mozambique": "MOZ",
    "Namibia": "NAM", "Niger": "NER", "Nigeria": "NGA", "Rwanda": "RWA",
    "Sao Tome and Principe": "STP", "Senegal": "SEN", "Seychelles": "SYC",
    "Sierra Leone": "SLE", "Somalia": "SOM", "South Africa": "ZAF",
    "South Sudan": "SSD", "Sudan": "SDN", "Tanzania": "TZA", "Togo": "TGO",
    "Tunisia": "TUN", "Uganda": "UGA", "Zambia": "ZMB", "Zimbabwe": "ZWE",
}

COUNTRY_REGION: dict[str, str] = {c: r for r, cs in REGIONS.items() for c in cs}
assert len(COUNTRY_REGION) == 54 and set(COUNTRY_REGION) == set(ISO3)

#: Common spellings (and the production keyword dictionary's own spelling
#: quirks, e.g. "Cabo Verde") mapped to the canonical names above.
ALIASES: dict[str, str] = {
    "Burkina Faso": "Burkina-Faso",
    "Cote d'Ivoire": "Ivory Coast",
    "Côte d'Ivoire": "Ivory Coast",
    "Cabo Verde": "Cape Verde",
    "DR Congo": "Congo DRC",
    "Democratic Republic of the Congo": "Congo DRC",
    "Republic of the Congo": "Congo",
    "Swaziland": "Eswatini",
    "The Gambia": "Gambia",
    "São Tomé and Príncipe": "Sao Tome and Principe",
    "Sao Tome & Principe": "Sao Tome and Principe",
}


def canonicalize(name: str) -> str:
    """Map a country spelling to its canonical AERI name via :data:`ALIASES`.

    Names already in :data:`ISO3` and unrecognized names both pass through
    unchanged -- this does not raise, so an unexpected folder name (for
    example a re-scrape variant like ``"Morocco_new"``) stays distinct
    rather than being silently merged into an existing country. Decide
    deliberately (e.g. by renaming the source folder, or extending
    :data:`ALIASES`) before treating it as the same country.
    """
    return ALIASES.get(name, name)
