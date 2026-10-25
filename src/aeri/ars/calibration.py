"""Freeze a weight calibration as a dated version, and reload it.

Mirrors the sibling `newsindex` library's frozen-baseline pattern
(`newsindex.index.Baseline`). Works with either `calibrate_ars_weights()`
or `calibrate_pillar_weights()` output -- both are plain `dict[str, float]`
weightings -- so a project can freeze and version-control whichever
calibration it recomputes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .._version import __version__


@dataclass(frozen=True)
class Calibration:
    """A frozen, dated set of weights plus the library version that
    produced them."""

    weights: dict[str, float]
    calibrated_on: str = ""
    library_version: str = field(default_factory=lambda: __version__)

    def save(self, path: str | Path) -> None:
        payload = {
            "weights": self.weights,
            "calibrated_on": self.calibrated_on,
            "library_version": self.library_version,
        }
        Path(path).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    @classmethod
    def load(cls, path: str | Path) -> "Calibration":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            weights=dict(payload["weights"]),
            calibrated_on=payload.get("calibrated_on", ""),
            library_version=payload.get("library_version", ""),
        )


def save_calibration(weights: dict[str, float], path: str | Path, calibrated_on: str = "") -> None:
    """Freeze `weights` (e.g. from `calibrate_ars_weights()` or
    `calibrate_pillar_weights()`) as a dated calibration file, so a
    later, differently-calibrated run can't silently replace it."""
    Calibration(weights=weights, calibrated_on=calibrated_on).save(path)


def load_calibration(path: str | Path) -> dict[str, float]:
    """Load a frozen calibration's weights (see `save_calibration()`)."""
    return Calibration.load(path).weights
