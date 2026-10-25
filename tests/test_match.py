from aeri.match import any_term_matches, find_terms, normalize, term_matches


def test_normalize_lowercases_and_collapses_whitespace():
    assert normalize("  Economic   CRISIS \n deepens  ") == "economic crisis deepens"


def test_normalize_folds_apostrophes_and_dashes():
    assert normalize("Nigeria’s economy") == "nigeria's economy"
    assert normalize("coup—d'etat") == "coup-d'etat"


def test_normalize_handles_none_and_empty():
    assert normalize(None) == ""
    assert normalize("") == ""


def test_term_matches_is_word_boundary_aware_not_substring():
    normalized = normalize("Analysts issued a warning about the forward outlook.")
    assert not term_matches(normalized, "war")
    assert term_matches(normalized, "warning")


def test_term_matches_handles_hyphen_space_equivalence():
    assert term_matches(normalize("a cost-of-living crisis"), "cost of living")
    assert term_matches(normalize("a cost of living crisis"), "cost-of-living")


def test_term_matches_handles_short_terms_like_abbreviations():
    assert term_matches(normalize("the IMF approved a loan"), "imf")
    assert not term_matches(normalize("confirmed information"), "imf")


def test_any_term_matches_true_and_false():
    assert any_term_matches("The central bank raised rates.", ["central bank", "famine"])
    assert not any_term_matches("The local team won the match.", ["central bank", "famine"])


def test_find_terms_returns_distinct_matches_in_order():
    text = "Inflation and currency devaluation triggered a crisis; the crisis deepened."
    found = find_terms(text, ["inflation", "devaluation", "crisis", "famine"])
    assert found == ["inflation", "devaluation", "crisis"]
