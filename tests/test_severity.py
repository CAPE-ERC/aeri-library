from aeri.severity import severity_tier


def test_severity_tier_zero_for_neutral_text():
    assert severity_tier("The market opened as usual this morning.") == 0


def test_severity_tier_one_for_mild_concern():
    assert severity_tier("Analysts express concern about a possible slowdown.") == 1


def test_severity_tier_three_for_serious_language():
    assert severity_tier("The currency crisis triggered a default.") == 3


def test_severity_tier_four_for_extreme_language():
    assert severity_tier("The region is facing famine and a humanitarian crisis.") == 4


def test_severity_tier_highest_match_wins():
    text = "There is concern over a looming economic collapse and catastrophe."
    assert severity_tier(text) == 4
