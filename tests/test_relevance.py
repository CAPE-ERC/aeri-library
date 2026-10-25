from aeri.config import AERIConfig
from aeri.dictionary import CountryDictionary
from aeri.relevance import is_relevant, relevance_terms

NIGERIA = CountryDictionary(
    country="Nigeria",
    languages=("en",),
    economic=("inflation", "naira", "central bank"),
    policy=("monetary policy", "budget"),
    uncertainty=("uncertainty",),
)


def test_is_relevant_true_for_economic_keyword():
    assert is_relevant("The central bank raised its key interest rate today.", NIGERIA)


def test_is_relevant_false_for_unrelated_text():
    assert not is_relevant("The local football team won their match on Sunday.", NIGERIA)


def test_is_relevant_is_word_boundary_not_substring():
    # "naira" should not match inside an unrelated longer word.
    assert not is_relevant("The painaira festival drew large crowds.", NIGERIA)


def test_is_relevant_false_for_empty_text():
    assert not is_relevant("", NIGERIA)


def test_is_relevant_can_include_policy_terms_via_config():
    config = AERIConfig(relevance_components=("economic", "policy"))
    assert is_relevant("The budget was presented to parliament.", NIGERIA, config)
    assert not is_relevant("The budget was presented to parliament.", NIGERIA)


def test_relevance_terms_default_is_economic_only():
    assert relevance_terms(NIGERIA) == NIGERIA.economic
