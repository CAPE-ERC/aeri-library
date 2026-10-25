import json

import pytest

from aeri.dictionary import load, validate, fingerprint

SAMPLE = {
    "Nigeria": {
        "ECONOMY_TERMS": ["inflation", "naira", "economy"],
        "POLICY_TERMS": ["monetary policy", "budget"],
        "UNCERTAINTY_TERMS": ["uncertainty", "unclear"],
    },
    "Cabo Verde": {
        "ECONOMY_TERMS": ["economy", "escudo"],
        "POLICY_TERMS": ["budget"],
        "UNCERTAINTY_TERMS": ["uncertainty"],
    },
    "Ghana": {
        "ECONOMY_TERMS": [],
        "POLICY_TERMS": ["budget"],
        "UNCERTAINTY_TERMS": ["uncertainty"],
    },
}


@pytest.fixture
def sample_path(tmp_path):
    path = tmp_path / "sample_keywords.json"
    path.write_text(json.dumps(SAMPLE), encoding="utf-8")
    return path


def test_load_reads_country_entries(sample_path):
    dictionary = load(sample_path)
    assert "Nigeria" in dictionary
    entry = dictionary["Nigeria"]
    assert entry.economic == ("inflation", "naira", "economy")
    assert entry.policy == ("monetary policy", "budget")
    assert entry.uncertainty == ("uncertainty", "unclear")
    assert len(dictionary) == 3


def test_load_canonicalizes_country_keys(sample_path):
    dictionary = load(sample_path)
    assert "Cabo Verde" not in dictionary
    assert "Cape Verde" in dictionary
    assert dictionary["Cape Verde"].economic == ("economy", "escudo")


def test_validate_flags_empty_economic_terms(sample_path):
    dictionary = load(sample_path)
    issues = validate(dictionary)
    assert any(i["country"] == "Ghana" and i["issue"] == "empty_economic_terms" for i in issues)
    assert not any(i["country"] == "Nigeria" for i in issues)


def test_fingerprint_is_stable_and_order_independent(sample_path):
    dictionary_a = load(sample_path)

    reordered = {
        "Ghana": SAMPLE["Ghana"],
        "Nigeria": SAMPLE["Nigeria"],
        "Cabo Verde": SAMPLE["Cabo Verde"],
    }
    reordered_path = sample_path.parent / "reordered.json"
    reordered_path.write_text(json.dumps(reordered), encoding="utf-8")
    dictionary_b = load(reordered_path)

    assert fingerprint(dictionary_a) == fingerprint(dictionary_b)


def test_fingerprint_changes_when_terms_change(sample_path):
    dictionary_a = load(sample_path)

    changed = json.loads(json.dumps(SAMPLE))
    changed["Nigeria"]["ECONOMY_TERMS"].append("recession")
    changed_path = sample_path.parent / "changed.json"
    changed_path.write_text(json.dumps(changed), encoding="utf-8")
    dictionary_b = load(changed_path)

    assert fingerprint(dictionary_a) != fingerprint(dictionary_b)
