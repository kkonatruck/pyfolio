# Slippage analysis

Converted from the `slippage_example.ipynb` notebook. All data comes
from the test fixtures bundled in this repository, so the code runs
as-is from the repository root.

When evaluating a strategy using backtest results, we often want to
know how sensitive its performance is to implementation shortfall or
slippage. pyfolio's transactions tear sheet can create "slippage sweep"
plots that display strategy performance under various slippage
assumptions.

Additional per-dollar slippage can be applied to returns before running
a tear sheet by providing `create_full_tear_sheet` with a level of
slippage in basis points (1% == 100 basis points) as the `slippage`
keyword argument. The slippage plots in the transactions tear sheet
display returns with slippage applied.

```python
import gzip

import pandas as pd
import pyfolio as pf

transactions = pd.read_csv(
    gzip.open('pyfolio/tests/test_data/test_txn.csv.gz'),
    index_col=0, parse_dates=True)
positions = pd.read_csv(
    gzip.open('pyfolio/tests/test_data/test_pos.csv.gz'),
    index_col=0, parse_dates=True)
returns = pd.read_csv(
    gzip.open('pyfolio/tests/test_data/test_returns.csv.gz'),
    index_col=0, parse_dates=True, header=None)[1]
```

Run the full tear sheet with no extra slippage; increase `slippage`
(for example to `10` basis points) to see performance degrade in the
slippage sweep plots:

```python
pf.create_full_tear_sheet(returns, positions, transactions, slippage=0)
```
