from aeri.text import normalize_text, strip_html, word_count


def test_strip_html_removes_tags_and_unescapes_entities():
    raw = "<p>Naira &amp; the economy</p>"
    assert strip_html(raw) == " Naira & the economy "


def test_normalize_text_lowercases_and_collapses_whitespace():
    assert normalize_text("  Economic   CRISIS \n deepens  ") == "economic crisis deepens"


def test_normalize_text_strips_accents_and_diacritics():
    assert normalize_text("Économie en crise") == "economie en crise"
    assert normalize_text("Inflação em alta") == "inflacao em alta"


def test_normalize_text_handles_empty_input():
    assert normalize_text("") == ""
    assert normalize_text(None) == ""


def test_word_count():
    assert word_count("one two three") == 3
    assert word_count("") == 0
