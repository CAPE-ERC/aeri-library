"""Shared first-principal-component weight calibration (equation 11).

Used by both `aeri.pillars.weights.calibrate_pillar_weights()` and
`aeri.ars.weights.calibrate_ars_weights()` -- the same standardise -> PCA
-> orient -> rescale -> normalise -> reject-mixed-sign procedure, applied
to different inputs (the 8 transformed pillars, or the 4 ARS components).
"""

from __future__ import annotations

import numpy as np


class MixedSignLoadingsError(ValueError):
    """The first principal component's loadings aren't (after orientation)
    all one sign, so the calibration panel doesn't support a single
    coherent weighting."""


def first_principal_component_weights(
    matrix: np.ndarray, labels: list[str], max_negative_share: float = 0.0
) -> dict[str, float]:
    """First-principal-component weights for the columns of `matrix`.

    Standardises each column, takes the leading eigenvector of the
    covariance matrix (oriented so higher component values mean a higher
    reading, i.e. the loadings sum positive), converts the standardised
    loadings back to the original (bounded-input) scale, and normalises
    the result to sum to 1.

    Raises `MixedSignLoadingsError` if any column has zero variance (can't
    be standardised), or if more than `max_negative_share` of the oriented
    loadings are negative -- the default (0.0) tolerates none, matching
    the documented "rejects mixed-sign loadings" rule: a calibration panel
    whose components don't move in a single coherent direction can't be
    collapsed into one weighting.
    """
    mu = matrix.mean(axis=0)
    sigma = matrix.std(axis=0, ddof=0)
    zero_variance = [label for label, s in zip(labels, sigma) if s == 0]
    if zero_variance:
        raise MixedSignLoadingsError(
            f"columns with zero variance in the calibration panel: {zero_variance}"
        )

    standardized = (matrix - mu) / sigma
    covariance = np.cov(standardized, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    loadings = eigenvectors[:, int(np.argmax(eigenvalues))]
    if loadings.sum() < 0:
        loadings = -loadings

    negative_share = float(np.mean(loadings < 0))
    if negative_share > max_negative_share:
        raise MixedSignLoadingsError(
            f"{negative_share:.0%} of PC1 loadings are negative after orientation; "
            "calibration panel does not support a single coherent weighting"
        )

    raw_weights = loadings / sigma
    normalized = raw_weights / raw_weights.sum()
    return dict(zip(labels, (float(w) for w in normalized)))
