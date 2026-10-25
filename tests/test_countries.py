from aeri.countries import ALIASES, COUNTRY_REGION, ISO3, canonicalize


def test_covers_54_countries():
    assert len(ISO3) == 54
    assert len(COUNTRY_REGION) == 54


def test_canonicalize_maps_known_aliases():
    assert canonicalize("Burkina Faso") == "Burkina-Faso"
    assert canonicalize("Cabo Verde") == "Cape Verde"
    assert canonicalize("DR Congo") == "Congo DRC"


def test_canonicalize_passes_through_canonical_and_unknown_names():
    assert canonicalize("Nigeria") == "Nigeria"
    assert canonicalize("Morocco_new") == "Morocco_new"


def test_all_alias_targets_are_canonical_countries():
    assert set(ALIASES.values()) <= set(ISO3)
