from aeri.relevance import is_relevant


def test_is_relevant_true_for_economic_keyword():
    assert is_relevant("The central bank raised its key interest rate today.")


def test_is_relevant_false_for_unrelated_text():
    assert not is_relevant("The local football team won their match on Sunday.")


def test_is_relevant_matches_accented_french_term():
    assert is_relevant("L'inflation et la dévaluation inquiètent les ménages.")


def test_is_relevant_false_for_empty_text():
    assert not is_relevant("")
