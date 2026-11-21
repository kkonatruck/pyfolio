# Round trip tear sheet

Converted from the `round_trip_tear_sheet_example.ipynb` notebook. All
data comes from the test fixtures bundled in this repository, so the
code runs as-is from the repository root.

When evaluating the performance of an investing strategy, it is helpful
to quantify the frequency, duration, and profitability of its
independent bets, or "round trip" trades. A round trip trade is started
when a new long or short position is opened and then later completely
or partially closed out.

The intent of the round trip tear sheet is to help differentiate
strategies that profited off a few lucky trades from strategies that
profited repeatedly from genuine alpha. Breaking down round trip
profitability by traded name and sector can also help inform universe
selection and identify exposures.

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

Sector mappings may optionally be passed in as a dict or `pd.Series`.
If a mapping is provided, PnL from symbols with mappings will be summed
to display profitability by sector (see
[Sector analysis](sector_mappings_example.md)).

```python
sect_map = {'COST': 'Consumer Goods', 'INTC': 'Technology',
            'CERN': 'Healthcare', 'GPS': 'Technology',
            'MMM': 'Construction', 'DELL': 'Technology',
            'AMD': 'Technology'}
```

The easiest way to run the analysis is to call
`pyfolio.create_round_trip_tear_sheet()`. Passing in a sector map is
optional. You can also pass `round_trips=True` to
`pyfolio.create_full_tear_sheet()` to have it created along with all
the other analyses.

```python
pf.create_round_trip_tear_sheet(returns, positions, transactions,
                                sector_mappings=sect_map)
```

Under the hood, several functions are being called.
`extract_round_trips()` does the portfolio reconstruction and creates
the round-trip trades:

```python
rts = pf.round_trips.extract_round_trips(
    transactions,
    portfolio_value=positions.sum(axis='columns') / (returns + 1))
rts.head()
pf.round_trips.print_round_trip_stats(rts)
```

See [Round trips](../api/round_trips.md) for the full API.
