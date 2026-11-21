from unittest import TestCase, expectedFailure
from parameterized import parameterized
from collections import OrderedDict
import os
import gzip

from pandas import (
    Series,
    DataFrame,
    date_range,
    to_datetime,
    Timestamp,
    read_csv
)
from pandas.testing import assert_frame_equal

from numpy import (
    arange,
    zeros_like,
    nan,
)

import warnings

from pyfolio.utils import (to_utc, to_series, check_intraday,
                           detect_intraday, estimate_intraday)
from pyfolio.pos import (get_percent_alloc,
                         extract_pos,
                         get_sector_exposures,
                         get_max_median_position_concentration)


class PositionsTestCase(TestCase):
    dates = date_range(start='2015-01-01', freq='D', periods=20)

    def test_get_percent_alloc(self):
        raw_data = arange(15, dtype=float).reshape(5, 3)
        # Make the first column negative to test absolute magnitudes.
        raw_data[:, 0] *= -1

        frame = DataFrame(
            raw_data,
            index=date_range('01-01-2015', freq='D', periods=5),
            columns=['A', 'B', 'C']
        )

        result = get_percent_alloc(frame)
        expected_raw = zeros_like(raw_data)
        for idx, row in enumerate(raw_data):
            expected_raw[idx] = row / row.sum()

        expected = DataFrame(
            expected_raw,
            index=frame.index,
            columns=frame.columns,
        )

        assert_frame_equal(result, expected)

    def test_extract_pos(self):
        index_dup = [Timestamp('2015-06-08', tz='UTC'),
                     Timestamp('2015-06-08', tz='UTC'),
                     Timestamp('2015-06-09', tz='UTC'),
                     Timestamp('2015-06-09', tz='UTC')]
        index = [Timestamp('2015-06-08', tz='UTC'),
                 Timestamp('2015-06-09', tz='UTC')]

        positions = DataFrame(
            {'amount': [100., 200., 300., 400.],
             'last_sale_price': [10., 20., 30., 40.],
             'sid': [1, 2, 1, 2]},
            index=index_dup
        )
        cash = Series([100., 200.], index=index)

        result = extract_pos(positions, cash)

        expected = DataFrame(OrderedDict([
            (1, [100.*10., 300.*30.]),
            (2, [200.*20., 400.*40.]),
            ('cash', [100., 200.])]),
            index=index
        )
        expected.index.name = 'index'
        expected.columns.name = 'sid'

        assert_frame_equal(result, expected)

    @parameterized.expand([
        (DataFrame([[1.0, 2.0, 3.0, 10.0]]*len(dates),
                   columns=[0, 1, 2, 'cash'], index=dates),
         {0: 'A', 1: 'B', 2: 'A'},
         DataFrame([[4.0, 2.0, 10.0]]*len(dates),
                   columns=['A', 'B', 'cash'], index=dates),
         False),
        (DataFrame([[1.0, 2.0, 3.0, 10.0]]*len(dates),
                   columns=[0, 1, 2, 'cash'], index=dates),
         Series(index=[0, 1, 2], data=['A', 'B', 'A']),
         DataFrame([[4.0, 2.0, 10.0]]*len(dates),
                   columns=['A', 'B', 'cash'], index=dates),
         False),
        (DataFrame([[1.0, 2.0, 3.0, 10.0]]*len(dates),
                   columns=[0, 1, 2, 'cash'], index=dates),
         {0: 'A', 1: 'B'},
         DataFrame([[1.0, 2.0, 10.0]]*len(dates),
                   columns=['A', 'B', 'cash'], index=dates),
         True)
    ])
    def test_sector_exposure(self, positions, mapping,
                             expected_sector_exposure,
                             warning_expected):
        """
        Tests sector exposure mapping and rollup.

        """
        with warnings.catch_warnings(record=True) as w:
            result_sector_exposure = get_sector_exposures(positions,
                                                          mapping)

            assert_frame_equal(result_sector_exposure,
                               expected_sector_exposure)
            if warning_expected:
                self.assertEqual(len(w), 1)
            else:
                self.assertEqual(len(w), 0)

    @parameterized.expand([
        (DataFrame([[1.0, 2.0, 3.0, 14.0]]*len(dates),
                   columns=[0, 1, 2, 'cash'], index=dates),
         DataFrame([[0.15, 0.1, nan, nan]]*len(dates),
                   columns=['max_long', 'median_long',
                            'median_short', 'max_short'], index=dates)),
        (DataFrame([[1.0, -2.0, -13.0, 15.0]]*len(dates),
                   columns=[0, 1, 2, 'cash'], index=dates),
         DataFrame([[1.0, 1.0, -7.5, -13.0]]*len(dates),
                   columns=['max_long', 'median_long',
                            'median_short', 'max_short'], index=dates)),
        (DataFrame([[nan, 2.0, nan, 8.0]]*len(dates),
                   columns=[0, 1, 2, 'cash'], index=dates),
         DataFrame([[0.2, 0.2, nan, nan]]*len(dates),
                   columns=['max_long', 'median_long',
                            'median_short', 'max_short'], index=dates))
    ])
    def test_max_median_exposure(self, positions, expected):
        alloc_summary = get_max_median_position_concentration(positions)
        assert_frame_equal(expected, alloc_summary)

    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    test_returns = read_csv(
        gzip.open(
            __location__ + '/test_data/test_returns.csv.gz'),
        index_col=0, parse_dates=True)
    test_returns = to_series(to_utc(test_returns))
    test_txn = to_utc(read_csv(
        gzip.open(
            __location__ + '/test_data/test_txn.csv.gz'),
        index_col=0, parse_dates=True))
    test_pos = to_utc(read_csv(
        gzip.open(__location__ + '/test_data/test_pos.csv.gz'),
        index_col=0, parse_dates=True))

    @parameterized.expand([
        (test_pos, test_txn, False),
        (test_pos.resample('1W').last(), test_txn, True)
    ])
    def test_detect_intraday(self, positions, transactions, expected):
        detected = detect_intraday(positions, transactions, threshold=0.25)
        assert detected == expected

    @parameterized.expand([
        ('infer', test_returns, test_pos, test_txn, test_pos),
        (False, test_returns, test_pos, test_txn, test_pos)
    ])
    def test_check_intraday(self, estimate, returns,
                            positions, transactions, expected):
        detected = check_intraday(estimate, returns, positions, transactions)
        assert_frame_equal(detected, expected)

    @parameterized.expand([
        (test_returns, test_pos, test_txn, (1506, 8)),
        (test_returns, test_pos.resample('1W').last(), test_txn, (1819, 8))
    ])
    def test_estimate_intraday(self, returns, positions,
                               transactions, expected):
        intraday_pos = estimate_intraday(returns, positions, transactions)
        assert intraday_pos.shape == expected

    # --- estimate_intraday edge cases (issue #711) ---

    # Hand-checkable example: start each day flat with 1000 cash; each
    # day's peak exposure is right after the morning buy.
    intraday_txns = (
        ('2022-03-01 09:30', 10., 10.), ('2022-03-01 15:00', -10., 11.),
        ('2022-03-02 09:30', 5., 20.), ('2022-03-02 15:00', -5., 19.))

    def make_estimate_frames(self, pos_tz='UTC', txn_tz='UTC',
                             txns=None):
        if txns is None:
            txns = self.intraday_txns
        pos_index = date_range('2022-03-01', periods=3, freq='D',
                               tz=pos_tz)
        returns = Series([0.] * 3, index=pos_index)
        positions = DataFrame({'A': [0.] * 3, 'cash': [1000.] * 3},
                              index=pos_index)
        txn_index = to_datetime([t[0] for t in txns])
        if txn_tz is not None:
            txn_index = txn_index.tz_localize(txn_tz)
        transactions = DataFrame(
            {'amount': [t[1] for t in txns],
             'price': [t[2] for t in txns],
             'symbol': ['A'] * len(txns)},
            index=txn_index)
        return returns, positions, transactions

    def expected_estimate(self, index, rows):
        expected = DataFrame(rows, columns=['A', 'cash'], index=index)
        expected.index.name = 'period_close'
        expected.columns.name = 'sid'
        return expected

    canonical_rows = [[100., 900.], [100., 900.], [0., 1000.]]

    @parameterized.expand([('UTC',), ('US/Eastern',), (None,)])
    def test_estimate_intraday_values(self, tz):
        returns, positions, transactions = self.make_estimate_frames(
            pos_tz=tz, txn_tz=tz)
        result = estimate_intraday(returns, positions, transactions)
        assert_frame_equal(
            result,
            self.expected_estimate(positions.index, self.canonical_rows),
            check_freq=False)
        self.assertEqual(str(getattr(result.index, 'tz', None)),
                         str(getattr(positions.index, 'tz', None)))

    @parameterized.expand([('UTC',), ('US/Eastern',), (None,)])
    def test_estimate_intraday_with_date_column(self, tz):
        # Issue #711: backtrader-style adapters emit a 'date' column
        # alongside the DatetimeIndex; it must not collide with the
        # index name estimate_intraday imposes.
        returns, positions, transactions = self.make_estimate_frames(
            pos_tz=tz, txn_tz=tz)
        clean = estimate_intraday(returns, positions, transactions)
        transactions['date'] = transactions.index
        result = estimate_intraday(returns, positions, transactions)
        assert_frame_equal(result, clean)
        assert_frame_equal(
            result,
            self.expected_estimate(positions.index, self.canonical_rows),
            check_freq=False)

    def test_estimate_intraday_date_column_conflicting(self):
        # When both are present the DatetimeIndex is the documented
        # timestamp source, so a disagreeing 'date' column is ignored.
        returns, positions, transactions = self.make_estimate_frames()
        clean = estimate_intraday(returns, positions, transactions)
        transactions['date'] = to_datetime(
            ['1999-01-01'] * len(transactions)).tz_localize('UTC')
        assert_frame_equal(
            estimate_intraday(returns, positions, transactions), clean)

    @parameterized.expand([('UTC', True), (None, False)])
    def test_estimate_intraday_date_column_only(self, tz, datetimes):
        # Timestamps carried only by a 'date' column (RangeIndex) are
        # promoted to the index. The naive case passes parseable
        # strings, as a CSV-shaped adapter would.
        returns, positions, transactions = self.make_estimate_frames(
            pos_tz=tz, txn_tz=tz)
        clean = estimate_intraday(returns, positions, transactions)
        column_only = transactions.reset_index(drop=True)
        if datetimes:
            column_only['date'] = transactions.index
        else:
            column_only['date'] = [t[0] for t in self.intraday_txns]
        assert_frame_equal(
            estimate_intraday(returns, positions, column_only), clean)

    def test_estimate_intraday_eastern_evening_trade(self):
        # 20:00 US/Eastern is 01:00 UTC the next day; the trade must
        # stay on its local (Eastern) day, not be stripped/converted.
        returns, positions, transactions = self.make_estimate_frames(
            pos_tz='US/Eastern', txn_tz='US/Eastern',
            txns=(('2022-03-01 20:00', 10., 10.),))
        result = estimate_intraday(returns, positions, transactions)
        assert_frame_equal(
            result,
            self.expected_estimate(
                positions.index,
                [[100., 900.], [0., 1000.], [0., 1000.]]),
            check_freq=False)

    @parameterized.expand([('UTC', None), (None, 'UTC')])
    def test_estimate_intraday_mixed_timezones(self, pos_tz, txn_tz):
        # Mismatched tz-awareness is an error, never silently repaired
        # by stripping or localizing (either would move trades across
        # day boundaries when the offset is non-zero).
        returns, positions, transactions = self.make_estimate_frames(
            pos_tz=pos_tz, txn_tz=txn_tz)
        with self.assertRaises(TypeError):
            estimate_intraday(returns, positions, transactions)

    @parameterized.expand([(False,), (True,)])
    def test_estimate_intraday_empty_transactions(self, with_date_col):
        returns, positions, transactions = self.make_estimate_frames()
        transactions = transactions.iloc[0:0]
        if with_date_col:
            transactions['date'] = transactions.index
        result = estimate_intraday(returns, positions, transactions)
        assert_frame_equal(
            result,
            self.expected_estimate(positions.index, [[0., 1000.]] * 3),
            check_freq=False)
        # The result must not alias the caller's positions frame.
        self.assertIsNot(result, positions)
        result.iloc[0, 0] = -12345.
        self.assertEqual(positions.iloc[0, 0], 0.)

    @parameterized.expand([('positions',), ('returns',)])
    def test_estimate_intraday_empty_positions_or_returns(self, empty):
        returns, positions, transactions = self.make_estimate_frames()
        if empty == 'positions':
            positions = positions.iloc[0:0]
        else:
            returns = returns.iloc[0:0]
        with self.assertRaisesRegex(ValueError, 'non-empty'):
            estimate_intraday(returns, positions, transactions)

    def test_estimate_intraday_input_not_mutated(self):
        returns, positions, transactions = self.make_estimate_frames()
        transactions['date'] = transactions.index
        columns = list(transactions.columns)
        index = transactions.index.copy()
        estimate_intraday(returns, positions, transactions)
        self.assertEqual(list(transactions.columns), columns)
        self.assertTrue(transactions.index.equals(index))
        self.assertEqual(transactions.index.names, index.names)

    def test_check_intraday_infer_with_date_column(self):
        # The actual #711 call path: 'infer' detects the intraday
        # strategy (flat at every day end) and routes into
        # estimate_intraday with a 'date'-column transactions frame.
        returns, positions, transactions = self.make_estimate_frames()
        transactions['date'] = transactions.index
        with self.assertWarns(UserWarning):
            result = check_intraday('infer', returns, positions,
                                    transactions)
        assert_frame_equal(
            result,
            self.expected_estimate(positions.index, self.canonical_rows),
            check_freq=False)

    @expectedFailure
    def test_estimate_intraday_midnight_crossing(self):
        # Pre-existing limitation, not part of #711: the daily cumsum
        # resets at calendar midnight and rows tied at the daily peak
        # all survive, so a position carried over midnight yields a
        # duplicated day (here also a spurious short row). Fixing this
        # needs the currently unused EOD_hour parameter to govern day
        # assignment; until then this pins the desired invariants.
        returns, positions, transactions = self.make_estimate_frames(
            txns=(('2022-03-01 23:30', 10., 10.),
                  ('2022-03-02 00:30', 10., 10.),
                  ('2022-03-02 01:00', -20., 10.)))
        result = estimate_intraday(returns, positions, transactions)
        self.assertTrue(result.index.is_unique)
        self.assertTrue((result['A'] >= 0).all())
