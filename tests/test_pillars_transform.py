import math

import pandas as pd
import pytest

from aeri.config import PILLARS
from aeri.pillars import DEFAULT_LOG_LOWER, DEFAULT_LOG_UPPER, fit_transform_bounds, transform_pillars


def test_default_bounds_cover_all_eight_pillars():
    assert set(DEFAULT_LOG_LOWER) == set(PILLARS)
    assert set(DEFAULT_LOG_UPPER) == set(PILLARS)
    assert all(v == 0.0 for v in DEFAULT_LOG_LOWER.values())
    # Table 4, Main_AERI_ARS_Paper-10-09-2026.pdf.
    assert DEFAULT_LOG_UPPER["InflationRisk"] == pytest.approx(2.9629)
    assert DEFAULT_LOG_UPPER["FinancialSectorRisk"] == pytest.approx(4.5177)
    assert DEFAULT_LOG_UPPER["CommoditySupplyRisk"] == pytest.approx(1.0248)


def test_transform_pillars_at_lower_bound_is_zero():
    row = {"Country": "X", "Period": "2026-01"}
    row.update({pillar: 0.0 for pillar in PILLARS})  # log(1+0) = 0 = lower bound
    df = pd.DataFrame([row])
    result = transform_pillars(df)
    for pillar in PILLARS:
        assert result.loc[0, pillar] == pytest.approx(0.0)


def test_transform_pillars_at_upper_bound_is_one():
    row = {"Country": "X", "Period": "2026-01"}
    for pillar in PILLARS:
        row[pillar] = math.expm1(DEFAULT_LOG_UPPER[pillar])  # log(1+P) = upper bound
    df = pd.DataFrame([row])
    result = transform_pillars(df)
    for pillar in PILLARS:
        assert result.loc[0, pillar] == pytest.approx(1.0)


def test_transform_pillars_clips_beyond_bounds():
    row = {"Country": "X", "Period": "2026-01"}
    for pillar in PILLARS:
        row[pillar] = math.expm1(DEFAULT_LOG_UPPER[pillar]) * 100  # way above upper bound
    df = pd.DataFrame([row])
    result = transform_pillars(df)
    for pillar in PILLARS:
        assert result.loc[0, pillar] == pytest.approx(1.0)


def test_fit_transform_bounds_recovers_percentiles():
    import numpy as np

    raw = np.linspace(0, 10, 101)  # 1st percentile ~= 0.1, 99th ~= 9.9
    df = pd.DataFrame({"Country": "X", "Period": "2026-01", **{p: raw for p in PILLARS}})
    lower, upper = fit_transform_bounds(df)
    for pillar in PILLARS:
        assert lower[pillar] == pytest.approx(math.log1p(0.1), abs=0.01)
        assert upper[pillar] == pytest.approx(math.log1p(9.9), abs=0.01)


def test_transform_pillars_uses_custom_bounds():
    df = pd.DataFrame([{"Country": "X", "Period": "2026-01", **{p: 1.0 for p in PILLARS}}])
    lower = {p: 0.0 for p in PILLARS}
    upper = {p: math.log1p(1.0) for p in PILLARS}  # P=1 sits exactly at the upper bound
    result = transform_pillars(df, lower=lower, upper=upper)
    for pillar in PILLARS:
        assert result.loc[0, pillar] == pytest.approx(1.0)
