from aeri.config import PILLARS
from aeri.pillars import active_pillar_count, assign_pillars


def test_assign_pillars_flags_all_eight_keys():
    flags = assign_pillars("Nothing economically relevant here.")
    assert set(flags.keys()) == set(PILLARS)
    assert PILLARS == (
        "InflationRisk",
        "FXExternalRisk",
        "DebtFiscalRisk",
        "FinancialSectorRisk",
        "GrowthRealEconomyRisk",
        "CommoditySupplyRisk",
        "PoliticalEconomyRisk",
        "ClimateDisasterRisk",
    )


def test_assign_pillars_single_pillar():
    flags = assign_pillars("The central bank raised the lending rate to curb a credit crunch.")
    assert flags["FinancialSectorRisk"] is True
    assert flags["ClimateDisasterRisk"] is False


def test_assign_pillars_multiple_pillars_and_active_count():
    text = (
        "Inflation surged as the currency devaluation deepened, while a "
        "drought hit agriculture and the harvest failed."
    )
    flags = assign_pillars(text)
    assert flags["InflationRisk"] is True
    assert flags["FXExternalRisk"] is True
    assert flags["ClimateDisasterRisk"] is True
    assert active_pillar_count(flags) >= 3


def test_assign_pillars_is_word_boundary_not_substring():
    # "import" (FXExternalRisk) must not match inside "important".
    flags = assign_pillars("The decision was important for local politics.")
    assert flags["FXExternalRisk"] is False
