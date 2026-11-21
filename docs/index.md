# pyfolio

pyfolio is a Python library for performance and risk analysis of
financial portfolios developed by
[Quantopian Inc](https://www.quantopian.com). It works well with the
[Zipline](https://www.zipline.io/) open source backtesting library.

At the core of pyfolio is a so-called tear sheet that consists of
various individual plots that provide a comprehensive image of the
performance of a trading algorithm. Here's an example of a simple tear
sheet analyzing a strategy:

![simple tear 0](simple_tear_0.png "Example tear sheet")
![simple tear 1](simple_tear_1.png "Example tear sheet")

## Installation

To install pyfolio, run:

```bash
pip install pyfolio
```

For development, clone this git repository and install it in editable
mode inside a virtual environment:

```bash
pip install -e .
```

## Usage

Start with the tutorials, which run on data bundled with this
repository:

- [Single strategy returns](tutorials/single_stock_example.md)
- [Sector analysis](tutorials/sector_mappings_example.md)
- [Round trip analysis](tutorials/round_trip_tear_sheet_example.md)
- [Slippage analysis](tutorials/slippage_example.md)

The full function reference is in the API pages, starting with
[Tear sheets](api/tears.md). Release notes are on the
[Releases](whatsnew.md) page.

### Removed notebook tutorials

The documentation previously converted Jupyter notebooks under
`docs/notebooks/` to pages at build time. During the MkDocs restore
the runnable notebooks were converted to the Markdown tutorials above,
and the following were dropped because they can no longer run:

- **Zipline algorithm** (`zipline_algo_example.ipynb`): requires
  Zipline and an ingested pricing bundle. Zipline is unmaintained and
  does not support current Python/pandas, so the notebook cannot
  execute. `pyfolio.utils.extract_rets_pos_txn_from_zipline` remains
  available for users who still have Zipline results; see
  [Utilities](api/utils.md).
- **Full tear sheet** (`full_tear_sheet_example.ipynb`): a two-cell
  notebook that only called Quantopian Research's `get_backtest()`
  builtin. The Quantopian platform shut down in 2020, so there is
  nothing left to run. The [Slippage analysis](tutorials/slippage_example.md)
  tutorial covers `create_full_tear_sheet` on local data instead.
- **Fama-French benchmark** (`fama_french_benchmark.ipynb`): called
  `pyfolio.tears.create_bayesian_tear_sheet`, which was removed from
  the codebase (it depended on PyMC3), and fetched live prices over
  the network. Neither dependency exists any more.
- **Single stock** (`single_stock_example.ipynb`): fetched live `FB`
  prices via `get_symbol_rets`, which needs the optional
  `empyrical-reloaded[yfinance]` extra and network access. It was
  converted, using bundled test returns instead of a live download;
  see [Single strategy returns](tutorials/single_stock_example.md).

The original notebooks remain under `pyfolio/examples/` for reference.

## Building these docs

```bash
make docs
```

This installs the documentation dependencies, builds the site with
`mkdocs build --strict` (any warning fails the build), and checks that
every internal link in the built site resolves. See the README in the
repository root for details.

## Questions?

If you find a bug, feel free to
[open an issue](https://github.com/quantopian/pyfolio/issues) in this
repository.

## Support

Please [open an issue](https://github.com/quantopian/pyfolio/issues/new)
for support.

## Contributing

If you'd like to contribute, a great place to look is the
[issues marked with help-wanted](https://github.com/quantopian/pyfolio/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22).

For a list of core developers and outside collaborators, see
[the GitHub contributors list](https://github.com/quantopian/pyfolio/graphs/contributors).
