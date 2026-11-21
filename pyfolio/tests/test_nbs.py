#!/usr/bin/env python
"""
Execute the offline example notebooks and report cell errors.

Each notebook is submitted to a kernel and any cell raising an
exception fails the test (nbclient's default behavior, equivalent
to the original runipy `skip_exceptions=False` check).

Only the self-contained examples are executed: they load bundled
test data and need no network or external platform. The remaining
example notebooks cannot run in any current environment:

- ``full_tear_sheet_example`` calls the Quantopian platform's
  ``get_backtest`` API (the platform shut down in 2020).
- ``bayesian`` / ``fama_french_benchmark`` / ``single_stock_example``
  need live market data (``utils.get_symbol_rets``) and the
  ``pyfolio.bayesian``/pymc3 stack, which pyfolio no longer ships.
- ``zipline_algo_example`` / ``pyfolio_talk_slides`` need a local
  zipline installation and data bundle.

This mirrors the notebook selection in
stefan-jansen/pyfolio-reloaded's ``tests/check_notebooks.py``.
"""

import os

import nbformat
import pytest
from nbclient import NotebookClient

import pyfolio

EXAMPLES = [
    "round_trip_tear_sheet_example",
    "sector_mappings_example",
    "slippage_example",
]


@pytest.mark.parametrize("name", EXAMPLES)
def test_nbs(name):
    examples_dir = os.path.join(
        os.path.dirname(os.path.abspath(pyfolio.__file__)), "examples")
    path = os.path.join(examples_dir, name + ".ipynb")
    with open(path) as f:
        nb = nbformat.read(f, as_version=4)
    client = NotebookClient(nb, timeout=600, kernel_name="python3")
    # Notebooks reference ../tests/test_data, so run them from the
    # examples directory.
    client.execute(cwd=examples_dir)
