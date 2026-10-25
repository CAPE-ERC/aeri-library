import pandas as pd
import pytest

from aeri.ars.score import ars_benchmark, ars_pca


def _real_algeria_components():
    return pd.DataFrame(
        {
            "Country": ["Algeria"],
            "Period": ["2015-01"],
            "Intensity": [0.3037780524144629],
            "Breadth": [0.2909090909090909],
            "Severity": [0.4161931818181818],
            "Structure": [1.0],
        }
    )


def test_ars_benchmark_matches_real_algeria_2015_01_row():
    result = ars_benchmark(_real_algeria_components())
    assert list(result.columns) == ["Country", "Period", "ARS"]
    # Real ARS for Algeria 2015-01 is 42.75.
    assert result.loc[0, "ARS"] == pytest.approx(42.75, abs=0.01)


def test_ars_pca_uses_default_weights_summing_correctly():
    df = pd.DataFrame(
        {"Country": ["X"], "Period": ["2026-01"], "Intensity": [1.0], "Breadth": [1.0], "Severity": [1.0], "Structure": [1.0]}
    )
    result = ars_pca(df)
    # All components = 1 -> ARS = 100 * sum(weights) = 100 (weights sum to 1).
    assert result.loc[0, "ARS"] == pytest.approx(100.0)


def test_ars_pca_accepts_custom_weights():
    df = pd.DataFrame(
        {"Country": ["X"], "Period": ["2026-01"], "Intensity": [0.5], "Breadth": [0.0], "Severity": [0.0], "Structure": [0.0]}
    )
    result = ars_pca(df, weights={"Intensity": 1.0, "Breadth": 0.0, "Severity": 0.0, "Structure": 0.0})
    assert result.loc[0, "ARS"] == pytest.approx(50.0)
