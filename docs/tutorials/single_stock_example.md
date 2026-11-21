# Single strategy returns analysis

This tutorial produces a returns tear sheet for a single return series.

It was converted from the old `single_stock_example.ipynb` notebook. The
notebook fetched live prices with `pf.utils.get_symbol_rets('FB')`, which
needs the optional `empyrical-reloaded[yfinance]` extra and network
access (and the `FB` ticker no longer exists), so it cannot run offline
or in CI. This version uses the return series bundled with the test
suite instead, so every step below runs as-is from the repository root.

## Import pyfolio

```python
import gzip

import pandas as pd
import pyfolio as pf
```

## Load a return series

```python
returns = pd.read_csv(
    gzip.open('pyfolio/tests/test_data/test_returns.csv.gz'),
    index_col=0, parse_dates=True, header=None)[1]
```

## Create a returns tear sheet

This shows charts and statistics about the returns: cumulative returns,
drawdowns, rolling volatility and Sharpe ratio, and monthly/annual
return breakdowns. See [Tear sheets](../api/tears.md) for the full
`create_returns_tear_sheet` signature.

```python
pf.create_returns_tear_sheet(returns)
```

To analyse your own strategy, replace `returns` with any daily
`pandas.Series` of simple returns indexed by date.
