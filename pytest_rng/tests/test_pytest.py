"""The main test file that should be run on a regular basis.

The goal of this file is to test pytest_rng internals and run all other
test files with various invocations of pytest to ensure that all possible
ways of using this plugin are tested.

By default, if you call ``pytest`` while in this repository, only this
file will be run due to configuration in ``setup.cfg``. However, other
test files can be run manually by passing them to ``pytest``.
"""

import os
from textwrap import dedent

pytest_plugins = ["pytester"]


def assert_all_passed(result):
    """Assert that all outcomes are 0 except for 'passed'.

    Also returns the number of passed tests.
    """
    outcomes = result.parseoutcomes()
    for outcome in outcomes:
        if outcome not in ("passed", "seconds"):
            assert outcomes[outcome] == 0
    return outcomes.get("passed", 0)


def copy_all_tests(testdir, path):
    parts = path.strip("/").split("/")
    for i in range(1, len(parts) + 1):
        testdir.mkpydir("/".join(parts[:i]))

    # Find all test files in the current folder, not including this one.
    # NB: If we add additional directories, this needs to change
    tests = [
        p
        for p in os.listdir(os.path.dirname(__file__))
        if p.startswith("test_") and p != "test_pytest.py"
    ]
    for test in tests:
        test_path = testdir.copy_example(test)
        test_path.rename("%s/%s" % (path, test))


def check_consistency(testdir, *pytest_args):
    """Run all tests twice to check seed consistency across runs."""

    # The first pass fills up the cache
    result = testdir.runpytest_subprocess("--cache-clear", *pytest_args)

    # The second pass should all pass
    result = testdir.runpytest_subprocess(*pytest_args)
    assert assert_all_passed(result) > 0


def get_seeds_from_cache(testdir, salt):
    """Run ``pytest --cache-show`` and parse the outcome to get cached seeds."""

    result = testdir.runpytest("--cache-show")
    fmt = "test_seed[{param}]:{salt} contains:"

    ix_a = result.outlines.index(fmt.format(param="a", salt=salt))
    seed_a = int(result.outlines[ix_a + 1].strip())

    ix_b = result.outlines.index(fmt.format(param="b", salt=salt))
    seed_b = int(result.outlines[ix_b + 1].strip())

    return seed_a, seed_b


def test_fixture_consistency(testdir):
    copy_all_tests(testdir, "packages/tests")
    check_consistency(testdir)


def test_salt(testdir):
    copy_all_tests(testdir, "packages/tests")

    # First, test passing in a salt value via command line
    check_consistency(testdir, "--rng-salt", "cli-salt")

    # Look at the cache to make sure the salt is being used
    cli_seed_a, cli_seed_b = get_seeds_from_cache(testdir, salt="cli-salt")
    assert cli_seed_a != cli_seed_b

    # Second, set up an ini config value
    testdir.makeini(
        dedent(
            """\
            [pytest]
            rng_salt = ini-salt
            """
        )
    )
    # Check consistency without passing a salt
    check_consistency(testdir)

    # Look at the cache to make sure the salt is being used
    ini_seed_a, ini_seed_b = get_seeds_from_cache(testdir, salt="ini-salt")
    assert ini_seed_a != ini_seed_b
    assert ini_seed_a != cli_seed_a

    # Third, try passing the CLI salt again to test overriding
    check_consistency(testdir, "--rng-salt", "cli-salt")
    override_seed_a, override_seed_b = get_seeds_from_cache(testdir, salt="cli-salt")
    assert override_seed_a != override_seed_b
    assert override_seed_a != ini_seed_a
    assert override_seed_a == cli_seed_a
