"""
Tests the functions in the ``downsampler`` module.  The functions here were written a good
2+ years ago; can you modernize them and improve their robustness?  This is a form of
maintaining tests, make sure they can be extended in future!

Implemented Tests
-----------------

A grid full of 1s should downsample to a grid of 1s.

A grid where every Nth cell is the value of N (where N = input gridsize/output gridsize)
should downsample to a grid of 1s.

A grid of random numbers, generated using a specified seed, should downsample to the
saved output.

Your Tasks
----------

``unit_tests`` checks some basic properties.  However, I haven't written a test to ensure
if any of the errors raised by this function are actually hit :O!  Use
``pytest.mark.parameterize`` to write a test for ``unit_tests``.  There are multiple
errors that can be raised, ensure that you've written enough tests to test EVERY ``if`
condition.  This is a form of ensuring your code has good **coverage**.

Update the random numbers test (``test_random``) to use ``pytest.mark.parameterize``
instead. See ``test_galaxy`` module for an example of this.  Reframing the function with
this method makes it easier to extend and ensure tests are more robust in future.

``np.where`` is a clumsy way to check closeness.  Update this to use ``np.allclose``.  See
``test_galaxy`` module for an example of this.

In my ``test_random`` function, I have a ``save_output`` flag.  Is this a good idea?
Should it be EASY to update the tests? If it is, why?  If it's not, remove the flag.
Should it be replaced by something else?
"""

from __future__ import print_function
import numpy as np
import itertools
from os import path

from example_scripts.downsampler import downsample_grid

# Save the path to this directory
dirpath = path.dirname(__file__)

# Set the tolerance of the tests.
tol = 1e-16


def unit_tests(grid, expected_gridsize, expected_datatype=np.float64):
    """
    Tests some fundamental properties of the grids output by `downsample`.

    Parameters
    ----------

    grid : `~numpy.ndarray`
        The 3D downsampled array created by `downsample`.

    expected_gridsize : int, optional
        The expected 1D size of output grid.  Default : 128 and 64.

    Returns
    ----------

    None.

    Errors
    ----------

    RuntimeError
        Raised if the output grid is not in the expected shape specified when
        `subample` was called.
        Raised if any values in the output grid are not `np.float64` types.
    """

    # Check that the grid is cubic with the expected gridsize.
    if not grid.shape == (expected_gridsize,
                          expected_gridsize,
                          expected_gridsize):
        print("The output grid shape was expected to be ({0}, {0}, {0})" \
              .format(expected_gridsize))
        print("However the shape was {0}".format(grid.shape))
        raise RuntimeError

    # Check that every element is of the expected datatype.
    for (i, j, k) in itertools.product(range(expected_gridsize),
                                       range(expected_gridsize),
                                       range(expected_gridsize)):
        if not type(grid[i,j,k]) == expected_datatype:
            print("The input data format was a `{4}`.  The output "
                  "data type should be identical however for element "
                  "({0},{1},{2}) it was {3}".format(i,j,k,type(grid[i,j,k]),
                    expected_datatype))
            raise RuntimeError


def test_homogenous_input(input_gridsize=128, output_gridsize=64):
    """
    Tests that passing a homogenous input grid will produce a homogenous
    output.

    The test will fail if the output grid is not homogenously filled with
    values of 1.0.

    We also run a suite of unit tests (see `unit_tests` function) that will
    return a RuntimeError if they're not passed.

    Parameters
    ----------

    input_gridsize, output_gridsize : int, optional
        1D size of the input/output grids.  Default : 128 and 64.

        ..note::
            `output_gridsize` must be an integer multiple (and smaller) than
            `input_gridsize`.  If not, a `RuntimeError` will be raised by
            `downsample.downsample_grid`.

    Returns
    ----------

    None.

    Errors
    ----------

    RuntimeError
        Raised if the output grid contains values that are not within the range
        0.99999 to 1.00001.
    """

    # Generate a homogenous input grid filled with 1.
    input_grid = np.ones((input_gridsize, input_gridsize, input_gridsize),
                         dtype=np.float64)

    # Perform the downsampling.
    output_grid = downsample_grid(input_grid, output_gridsize)

    # Find any instances where the output grid is not 1.
    w = np.where((output_grid <= 1.0-tol) & (output_grid >= 1.0+tol))[0]

    # Raise error.
    if len(w) > 0:
        print("We tested a homogenous input grid with every cell containing a "
              "value of 1.0. We expected the output grid to contain values of "
              "1.0 as well.")
        print("However cells {0} had values {1}".format(w, output_grid[w]))
        raise RuntimeError

    # Now run some unit tests that check some properties.
    unit_tests(output_grid, output_gridsize)


def test_multiple_input(input_gridsize=128, output_gridsize=64):
    """
    Tests that passing an input grid where every input_gridsize/output_gridsize
    cell is filled will a value of (input_gridsize/output_gridsize)^3 produces
    a grid that is homogenously filled with values of 1.0.

    The test will fail if the output grid is not homogenously filled with
    values of 1.0.

    We also run a suite of unit tests (see `unit_tests` function) that will
    return a RuntimeError if they're not passed.

    Parameters
    ----------

    input_gridsize, output_gridsize : int, optional
        1D size of the input/output grids.  Default : 128 and 64.

        ..note::
            `output_gridsize` must be an integer multiple (and smaller) than
            `input_gridsize`.  If not, a `RuntimeError` will be raised by
            `downsample.downsample_grid`.

    Returns
    ----------

    None.

    Errors
    ----------

    RuntimeError
        Raised if the output grid contains values that are not close to 1
        (within tolerance defined by the global variable `tol`).
    """

    # Ratio in grid size.
    conversion = int(input_gridsize / output_gridsize)

    input_grid = np.zeros((input_gridsize, input_gridsize, input_gridsize))

    # We fill every conversion-th cell with a value of conversion cubed.
    for (i, j, k) in itertools.product(range(output_gridsize),
                                       range(output_gridsize),
                                       range(output_gridsize)):
        input_grid[i*conversion, j*conversion, k*conversion] = conversion**3

    # Run the downsampler.
    output_grid = downsample_grid(input_grid, output_gridsize)


    # Find any instances where the output grid is not 1.
    w = np.where((output_grid <= 1.0-tol) & (output_grid >= 1.0+tol))[0]
    if len(w) > 0:
        print("We tested an input grid with every {0} cell containing a value "
              "of {1}. We expected the output grid to contain values of 1.0 "
              "as well.".format(conversion, conversion**3))
        print("However cells {0} had values {1}".format(w, output_grid[w]))
        raise RuntimeError

    # Now run some unit tests that check some properties.
    unit_tests(output_grid, output_gridsize)


def test_random(input_gridsize=128, output_gridsize=64,
                seed=12, save_output=False):
    """
    Generates an input grid of random numbers.  This is then checked against a
    saved output grid generated using the same seed.

    Parameters
    ----------

    input_gridsize, output_gridsize : int, optional
        1D size of the input/output grids.  Default : 128 and 64.

        ..note::
            `output_gridsize` must be an integer multiple (and smaller) than
            `input_gridsize`.  If not, a `RuntimeError` will be raised by
            `downsample.downsample_grid`.

    seed : int, optional
        Seed used for the random number generator. Default : 12.

    save_output : boolean, optional
        Dictates if we want to save the output grid as the 'correct' code.  If
        you want to test a random grid with different gridsizes/seed than the
        default, this will need to be set to `True` for the first time.

        ..warning::
            Ensure that the code is running 100% correct before turning this
            variable on.  Please run the tests using default parameters first.

    Returns
    ----------

    None.

    Errors
    ----------

    RuntimeError
        Raised if the randomly generated input grid does not match (to a
        tolerance defined by the global variable `tol`) the saved grid.
    """

    # Set the RNG seed and generate an input grid.
    np.random.seed(seed)

    input_grid = np.random.rand(input_gridsize,
                                input_gridsize,
                                input_gridsize)

    # Run the code with the randomly generated input grid.
    output_grid = downsample_grid(input_grid, output_gridsize)

    # Now we want to set up the known grid.
    known_grid_name = "{0}/data/known_grid_in{1}_out{2}_" \
                      "seed{3}.npz".format(dirpath, input_gridsize, output_gridsize, seed)

    # If we're saving a new 'correct' output grid, do so and exit.
    if save_output:
        np.savez(known_grid_name, output_grid)
        return

    # Otherwise read in the known grid and shape it properly.
    known_grid = (np.load(known_grid_name))["arr_0"]
    known_grid.shape = (output_gridsize, output_gridsize, output_gridsize)

    # Find any instances where the grids disagree.
    w = np.where(abs(known_grid - output_grid) > tol)[0]

    # Raise error.
    if len(w) > 0:
        print("We compared an input grid with randomly generated data with "
              "random seed {0}.  Reading the known input grid ({1}), we had "
              "cells that contained different values.".format(seed,
              known_grid_name))
        print("These were cells {0} with difference {1}".format(w,
              known_grid-output_grid[w]))
        raise RuntimeError

    # Now run some unit tests that check some properties.
    unit_tests(output_grid, output_gridsize)
