from aeri.config import PILLARS
from aeri.pillars import active_pillar_count, assign_pillars


def test_assign_pillars_flags_all_eight_keys():
    flags = assign_pillars("Nothing economically relevant here.")
    assert set(flags.keys()) == set(PILLARS)


def test_assign_pillars_single_pillar():
    flags = assign_pillars("The central bank raised the lending rate to curb a credit crunch.")
    assert flags["financial_sector"] is True
    assert flags["climate_and_disaster"] is False


def test_assign_pillars_multiple_pillars_and_active_count():
    text = (
        "Inflation surged as the currency devaluation deepened, while a "
        "drought hit agriculture and the harvest failed."
    )
    flags = assign_pillars(text)
    assert flags["inflation"] is True
    assert flags["fx_and_external"] is True
    assert flags["climate_and_disaster"] is True
    assert active_pillar_count(flags) >= 3
