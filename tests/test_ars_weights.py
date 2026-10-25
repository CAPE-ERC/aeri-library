import numpy as np
import pandas as pd
import pytest

from aeri._pca import MixedSignLoadingsError
from aeri.ars.weights import BENCHMARK_ARS_WEIGHTS, DEFAULT_ARS_PCA_WEIGHTS, calibrate_ars_weights


def test_benchmark_weights_match_proposal():
    assert BENCHMARK_ARS_WEIGHTS == {
        "Intensity": 0.40,
        "Breadth": 0.25,
        "Severity": 0.20,
        "Structure": 0.15,
    }
    assert sum(BENCHMARK_ARS_WEIGHTS.values()) == pytest.approx(1.0)


def test_default_pca_weights_match_table_3_and_sum_to_one():
    assert DEFAULT_ARS_PCA_WEIGHTS["Intensity"] == pytest.approx(0.2625)
    assert DEFAULT_ARS_PCA_WEIGHTS["Breadth"] == pytest.approx(0.2722)
    assert DEFAULT_ARS_PCA_WEIGHTS["Severity"] == pytest.approx(0.3223)
    assert DEFAULT_ARS_PCA_WEIGHTS["Structure"] == pytest.approx(0.1430)
    assert sum(DEFAULT_ARS_PCA_WEIGHTS.values()) == pytest.approx(1.0)


def test_calibrate_ars_weights_returns_positive_weights_summing_to_one():
    rng = np.random.default_rng(1)
    n = 200
    common_trend = np.linspace(0, 1, n)
    df = pd.DataFrame(
        {
            component: common_trend + rng.normal(0, 0.01, n)
            for component in ("Intensity", "Breadth", "Severity", "Structure")
        }
    )
    weights = calibrate_ars_weights(df)
    assert set(weights) == {"Intensity", "Breadth", "Severity", "Structure"}
    assert sum(weights.values()) == pytest.approx(1.0)
    assert all(w > 0 for w in weights.values())


def test_calibrate_ars_weights_raises_for_mixed_sign_loadings():
    n = 50
    t = np.linspace(0, 1, n)
    df = pd.DataFrame({"Intensity": t, "Breadth": t, "Severity": 1.0 - t, "Structure": 1.0 - t})
    with pytest.raises(MixedSignLoadingsError):
        calibrate_ars_weights(df)
