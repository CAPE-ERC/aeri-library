import pandas as pd
import pytest

from aeri.config import PILLARS
from aeri.pillars import pillar_composite, rank_pillars


def test_pillar_composite_formula_with_custom_weights():
    row = {"Country": "Nigeria", "Period": "2026-03"}
    row.update({pillar: 0.5 for pillar in PILLARS})
    df = pd.DataFrame([row])

    weights = {pillar: 1.0 / len(PILLARS) for pillar in PILLARS}
    result = pillar_composite(df, weights=weights)

    assert list(result.columns) == ["Country", "Period", "PillarComposite"]
    # H = sum_p(100 * (1/8) * 0.5) = 8 * 100/8 * 0.5 = 50
    assert result.loc[0, "PillarComposite"] == pytest.approx(50.0)


def test_pillar_composite_uses_default_weights_when_omitted():
    row = {"Country": "Nigeria", "Period": "2026-03"}
    row.update({pillar: 1.0 for pillar in PILLARS})
    df = pd.DataFrame([row])

    result = pillar_composite(df)
    # All Q_p = 1 -> H = sum_p(100 * u_p * 1) = 100 * sum(u_p) = 100.
    assert result.loc[0, "PillarComposite"] == pytest.approx(100.0)


def test_rank_pillars_sorts_descending():
    row = pd.Series({pillar: float(i) for i, pillar in enumerate(PILLARS)})
    ranked = rank_pillars(row)

    assert [name for name, _ in ranked] == list(reversed(PILLARS))
    assert ranked[0][1] > ranked[-1][1]


def test_rank_pillars_applies_per_row_over_a_dataframe():
    df = pd.DataFrame(
        [
            {pillar: float(i) for i, pillar in enumerate(PILLARS)},
            {pillar: float(len(PILLARS) - i) for i, pillar in enumerate(PILLARS)},
        ]
    )
    ranked = df.apply(rank_pillars, axis=1)
    assert ranked.iloc[0][0][0] == PILLARS[-1]
    assert ranked.iloc[1][0][0] == PILLARS[0]
