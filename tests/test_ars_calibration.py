from aeri.ars.calibration import Calibration, load_calibration, save_calibration


def test_save_and_load_calibration_round_trips(tmp_path):
    weights = {"Intensity": 0.4, "Breadth": 0.25, "Severity": 0.2, "Structure": 0.15}
    path = tmp_path / "ars_2026-10.json"

    save_calibration(weights, path, calibrated_on="2015-01:2025-07")
    loaded = load_calibration(path)

    assert loaded == weights


def test_calibration_records_library_version(tmp_path):
    path = tmp_path / "cal.json"
    Calibration(weights={"a": 1.0}, calibrated_on="test").save(path)
    restored = Calibration.load(path)

    assert restored.weights == {"a": 1.0}
    assert restored.calibrated_on == "test"
    assert restored.library_version  # non-empty
