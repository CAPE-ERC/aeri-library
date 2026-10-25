import numpy as np
import pandas as pd
import pytest

from aeri.config import PILLARS
from aeri.pillars import DEFAULT_PILLAR_WEIGHTS, MixedSignLoadingsError, calibrate_pillar_weights


def test_default_pillar_weights_match_table_4_and_sum_to_one():
    assert set(DEFAULT_PILLAR_WEIGHTS) == set(PILLARS)
    assert sum(DEFAULT_PILLAR_WEIGHTS.values()) == pytest.approx(1.0, abs=1e-4)
    assert DEFAULT_PILLAR_WEIGHTS["DebtFiscalRisk"] == pytest.approx(0.1729)
    assert DEFAULT_PILLAR_WEIGHTS["FinancialSectorRisk"] == pytest.approx(0.1730)
    assert DEFAULT_PILLAR_WEIGHTS["CommoditySupplyRisk"] == pytest.approx(0.0648)


def test_calibrate_pillar_weights_returns_positive_weights_summing_to_one():
    rng = np.random.default_rng(0)
    n = 200
    common_trend = np.linspace(0, 1, n)
    data = {
        pillar: common_trend + rng.normal(0, 0.01, n) for pillar in PILLARS
    }
    df = pd.DataFrame(data)

    weights = calibrate_pillar_weights(df)

    assert set(weights) == set(PILLARS)
    assert sum(weights.values()) == pytest.approx(1.0)
    assert all(w > 0 for w in weights.values())


def test_calibrate_pillar_weights_raises_for_zero_variance_pillar():
    n = 20
    data = {pillar: np.linspace(0, 1, n) for pillar in PILLARS}
    data[PILLARS[0]] = np.zeros(n)
    df = pd.DataFrame(data)

    with pytest.raises(MixedSignLoadingsError):
        calibrate_pillar_weights(df)


def test_calibrate_pillar_weights_raises_for_mixed_sign_loadings():
    n = 50
    t = np.linspace(0, 1, n)
    data = {}
    for i, pillar in enumerate(PILLARS):
        data[pillar] = t if i < 4 else (1.0 - t)
    df = pd.DataFrame(data)

    with pytest.raises(MixedSignLoadingsError):
        calibrate_pillar_weights(df)
