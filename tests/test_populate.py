"""Run each populate command - for computed/imported tables
"""

import logging
from .conftest import find_full_path, get_opto_root_data_dir

import pytest
import logging


def test_get_trajectory(feature):
    data = feature
    assert data.shape[1] == 12, f"Expected 12 columns. Found\n{data.columns}"

    names = ["x mean", "y mean", "z mean", "liklihood mean"]
    means = data.mean(axis=0)
    expected = [231, 250, 0, 1]
    delta = [10, 10, 0, 0.01]
    # averaging across body parts: zip x/y coords, means, and permissible delta
    for n, m, e, d in zip(names, means, expected, delta):
        assert m == pytest.approx(  # assert mean is within delta of expected value
            e, d
        ), f"Issues with data for {n}. Expected {e} ±{d}, Found {m}"
