**********
pytest-rng
**********

``pytest-rng`` provides fixtures for
ensuring "randomness" in your tests is reproducible
from one run to the next.
It also allows the seed for all tests to be changed if requested,
to help ensure that test successes are not dependent on
particular random number seeds.

- Use the ``rng`` fixture to get a pre-seeded random number generator (RNG)
  that exposes NumPy's `~numpy.random.mtrand.RandomState` interface.

- Use the ``seed`` fixture to get an integer seed
  that can be used to initialize your own RNG.

The following example prints the same four random numbers
every time the test is run.

.. code-block:: python

   import numpy as np

   def test_rectification(rng, seed):
       print(rng.uniform(-1, 1, size=3))
       print(seed)

To use these fixtures, install with

.. code-block:: bash

   pip install pytest-rng

Once installed, you can use these fixtures like any other fixture:
add ``rng`` or ``seed`` to the arguments of a test function or class.

Seed generation
===============

For the ``seed`` fixture, we generate a seed by doing the following:

1. Concatenate the test's ``nodeid`` and a ``salt`` value, if provided.
2. Hash that string to yield an integer seed.

For the ``rng`` fixture, we also add the string ``"rng"`` to the ``salt``
value before generating the seed as above.
The seed is used to instantiate a `~numpy.random.mtrand.RandomState`,
which is returned.

.. note:: We add ``"rng"`` to the salt to ensure that random numbers
          are different when using the ``rng`` fixture
          and when manually instantiating a ``RandomState``
          with the ``seed`` fixture.

salt
====

``salt`` is a string that is added to the test's ``nodeid``
in order to change the seed for all tests.
It is advantageous to change seeds regularly to ensure that
your test suite is robust to different seeds.

The salt value can be specified in a configuration file
like ``setup.cfg`` or ``pytest.ini``.

.. code-block:: ini

   [tool:pytest]

   rng_salt = v0.3.0

The salt value can also be specified through the command line.

.. code-block:: bash

   pytest --rng-salt "v0.4.0"

The salt value passed through the command line takes precedence
over the value set in the configuration file
so that you can change seeds on-the-fly.

~~~~~

See the full
`documentation <https://www.nengo.ai/pytest-rng>`__
for more details.
