import hashlib

import numpy as np
import pytest


class Seed:

    salt = ""

    @classmethod
    def generate(cls, uniqueid, extra_salt=""):
        """Generate a unique seed for the given identifier.

        The seed should be the same across all machines/platforms.
        """
        tohash = uniqueid + cls.salt + extra_salt
        sha1 = hashlib.sha1(tohash.encode("utf-8"))
        return int(sha1.hexdigest()[:8], 16)


def pytest_addoption(parser):
    help_msg = "Specify string to salt `rng` and `seed` fixtures"
    parser.addoption("--rng-salt", nargs=1, type=str, help=help_msg)
    parser.addini("rng_salt", help=help_msg)


def pytest_configure(config):
    cli_salt = config.getoption("--rng-salt", None)
    ini_salt = config.getini("rng_salt")
    if cli_salt is not None:
        Seed.salt = cli_salt[0]
    elif ini_salt is not None:
        Seed.salt = ini_salt


@pytest.fixture
def rng(request):
    """A seeded random number generator (RNG).

    An instance of `~numpy.random.mtrand.RandomState`. It is preferable
    to the unseeded `numpy.random` because it is consistent from one
    test run to the next when using the same salt value, and preferable to
    a fixed seed RNG because changing the salt checks that tests
    are not dependent on a specific seed.
    """
    return np.random.RandomState(Seed.generate(request.node.nodeid, extra_salt="rng"))


@pytest.fixture
def seed(request):
    """An integer random number generator seed in the range [0, 2**32 - 1].

    The seed is consistent from one test run to the next
    when using the same salt value.
    It is preferable to a completely fixed seed because changing the salt
    checks that tests are not dependent on a specific seed.
    """
    return Seed.generate(request.node.nodeid)
