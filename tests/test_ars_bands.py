import pytest

from aeri.ars.bands import risk_band


@pytest.mark.parametrize(
    "ars,expected",
    [
        (0.0, "Low"),
        (19.99, "Low"),
        (20.0, "Moderate"),
        (39.99, "Moderate"),
        (40.0, "Elevated"),
        (42.75, "Elevated"),  # Real Algeria 2015-01 row.
        (59.99, "Elevated"),
        (60.0, "High"),
        (79.99, "High"),
        (80.0, "Severe"),
        (100.0, "Severe"),
    ],
)
def test_risk_band_cut_points(ars, expected):
    assert risk_band(ars) == expected
