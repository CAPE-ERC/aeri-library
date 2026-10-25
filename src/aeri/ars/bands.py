"""ARS risk-band classification: Low / Moderate / Elevated / High / Severe.

Cut points at 20/40/60/80 (Main_AERI_ARS_Paper), left-closed: a band's
lower bound belongs to that band (e.g. ARS=40.0 is "Elevated", not
"Moderate"). Verified against the real `aeri_risk_score_country_period.csv`
row for Algeria 2015-01 (ARS=42.75 -> RiskLevel="Elevated").
"""

from __future__ import annotations


def risk_band(ars: float) -> str:
    """Low (< 20), Moderate (< 40), Elevated (< 60), High (< 80), else Severe."""
    if ars < 20.0:
        return "Low"
    if ars < 40.0:
        return "Moderate"
    if ars < 60.0:
        return "Elevated"
    if ars < 80.0:
        return "High"
    return "Severe"
