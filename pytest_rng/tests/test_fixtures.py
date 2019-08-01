"""Test the `~.rng` and `~.seed` fixtures.

To test that the values are consistent across multiple test runs, we require the
tests to be run twice. On the first test run, we cache randomly generated values.
On the second test run, we check that the previously cached values match the
values generated on this test run.
"""

import numpy as np
import pytest

from pytest_rng.plugin import Seed


@pytest.mark.parametrize("param", ["a", "b"])
def test_seed(cache, param, seed):
    fmt = "test_seed[{param}]:{salt}"
    key = fmt.format(param=param, salt=Seed.salt)

    cached = cache.get(key, None)
    if cached is not None:
        # Seed should be the same across test runs
        assert seed == cached

        # Different parametrizations should result in different seeds
        other_key = fmt.format(param="a" if param == "b" else "b", salt=Seed.salt)
        assert seed != cache.get(other_key, seed)

    else:
        cache.set(key, seed)
        assert cached, "Value was not yet cached, run again to test newly cached value"


@pytest.mark.parametrize("param", ["a", "b"])
def test_seed_across_tests(cache, param, seed):
    cached = cache.get(
        "test_seed[{param}]:{salt}".format(param=param, salt=Seed.salt), None
    )
    if cached is not None:
        # This seed should not be the same as test_seed
        assert seed != cached

    else:
        assert cached, "Value was not yet cached, run again to test newly cached value"


@pytest.mark.parametrize("param", ["a", "b"])
def test_rng(cache, param, rng):
    fmt = "test_rng[{param}]:{salt}"
    key = fmt.format(param=param, salt=Seed.salt)
    vals = rng.rand(3).tolist()  # Cache requires normal Python objects

    cached = cache.get(key, None)
    if cached is not None:

        # Generated values should be the same across test runs
        assert all(x == y for x, y in zip(vals, cached))

        # Different parametrizations should result in different seeds
        other_key = fmt.format(param="a" if param == "b" else "b", salt=Seed.salt)
        assert not all(x == y for x, y in zip(vals, cache.get(other_key, vals)))

    else:
        cache.set(key, vals)
        assert cached, "Value was not yet cached, run again to test newly cached value"


def test_seed_rng(rng, seed):
    manual_rng = np.random.RandomState(seed)
    assert not np.all(rng.rand(3) == manual_rng.rand(3))
