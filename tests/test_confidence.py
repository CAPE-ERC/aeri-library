import pytest

from aeri.confidence import confidence_weight


def test_confidence_weight_minimum_for_plain_short_text():
    weight = confidence_weight(
        title="Local news roundup",
        text="A short, unrelated news item with nothing notable in it.",
    )
    assert weight == pytest.approx(1.0)


def test_confidence_weight_title_hint_adds_half():
    weight = confidence_weight(
        title="Inflation worries grip the nation",
        text="A short unrelated filler paragraph without further signal.",
    )
    assert weight == pytest.approx(1.5)


def test_confidence_weight_is_clipped_to_two():
    long_text = "inflation currency devaluation drought harvest bank rate " * 60
    weight = confidence_weight(
        title="Inflation and devaluation crisis deepens amid drought",
        text=long_text,
    )
    assert weight == pytest.approx(2.0)
