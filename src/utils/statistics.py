"""Shared statistical utilities."""

from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np


def pearson_correlation(x: Sequence[float] | np.ndarray, y: Sequence[float] | np.ndarray) -> float:
    """Compute Pearson correlation coefficient, returning 0 on degenerate input."""
    x_arr = np.asarray(x)
    y_arr = np.asarray(y)

    if x_arr.size < 2 or y_arr.size < 2 or x_arr.size != y_arr.size:
        return 0.0

    if float(np.std(x_arr)) == 0.0 or float(np.std(y_arr)) == 0.0:
        return 0.0

    r = np.corrcoef(x_arr, y_arr)[0, 1]
    if math.isnan(r):
        return 0.0
    return float(r)
