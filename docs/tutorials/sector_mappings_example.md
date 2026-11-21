# Sector mappings

Converted from the `sector_mappings_example.ipynb` notebook. All data
comes from the test fixtures bundled in this repository, so the code
runs as-is from the repository root.

To generate sector allocation plots in the positions tear sheet and PnL
by sector in the round-trips tear sheet, pass pyfolio a dictionary (or
dict-like structure) of symbol-sector mappings, where symbols are keys
and sectors are values. `create_full_tear_sheet` also takes the
mappings as the keyword argument `sector_mappings`.

```python
import gzip

import pandas as pd
import pyfolio as pf

returns = pd.read_csv(
    gzip.open('pyfolio/tests/test_data/test_returns.csv.gz'),
    index_col=0, parse_dates=True, header=None)[1]
positions = pd.read_csv(
    gzip.open('pyfolio/tests/test_data/test_pos.csv.gz'),
    index_col=0, parse_dates=True)
transactions = pd.read_csv(
    gzip.open('pyfolio/tests/test_data/test_txn.csv.gz'),
    index_col=0, parse_dates=True)
```

Define the sector mappings:

```python
sect_map = {'COST': 'Consumer Goods',
            'INTC': 'Technology',
            'CERN': 'Healthcare',
            'GPS': 'Technology',
            'MMM': 'Construction',
            'DELL': 'Technology',
            'AMD': 'Technology'}
```

Generate the positions tear sheet and the round-trip tear sheet with
sector mappings:

```python
pf.create_position_tear_sheet(returns, positions,
                              sector_mappings=sect_map)
pf.create_round_trip_tear_sheet(returns, positions, transactions,
                                sector_mappings=sect_map)
```

See [Round trip analysis](round_trip_tear_sheet_example.md) for more on
round trips.
