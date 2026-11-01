"""Builds the month's target portfolio for the India low-beta strategy.

The strategy is the long leg of Frazzini and Pedersen's (2014) betting-against-beta idea, long only. At the close of each month the 500 most traded NSE shares are ranked on their beta against the NIFTY 500, and the fifth with the lowest beta is bought in equal weights and held for the next month. Beta follows the paper: the correlation of overlapping three-day log returns over 60 months times the ratio of share to market volatility over 12 months, shrunk towards one with weight 0.6.

This program only reads prices and writes a CSV of targets. It never places, modifies or cancels an order.

Typical usage example:

  python build_targets.py targets_2026-11.csv --previous targets_2026-10.csv --capital 1000000
"""

import argparse
import datetime
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

UNIVERSE_SIZE = 500
MINIMUM_PRICE = 2.0
LOW_BETA_FRACTION = 0.2
SHRINKAGE = 0.6
VOLATILITY_DAYS = 252
CORRELATION_DAYS = 1260
HORIZON_DAYS = 3
MINIMUM_VOLATILITY_OBS = 120
MINIMUM_CORRELATION_OBS = 756
LIQUIDITY_DAYS = 252
MINIMUM_TRADING_SHARE = 0.5
RECENT_DAYS = 5
STALE_DAYS = 10
DROP_LIMIT = -0.45
RISE_LIMIT = 1.0
MAXIMUM_OVERLAY = 1.5
FUND_PATTERN = re.compile(
    r'(-RE\d*$|BEES$|ETF|^LIQUID|^GILT|IETF$|^NIFTY|^SENSEX)',
    re.IGNORECASE,
)


class LowBetaTargets:
    """Turns daily closes and volumes into the target weights.

    Attributes:
        close: Daily closes, trading days by share, adjusted for splits and
            bonuses.
        traded_value: Close times volume, NaN when a share did not trade.
        market: The NIFTY 500's daily close on the same days.
        universe_size: How many shares are ranked.
        fraction: The share of the ranked shares that is held.
    """

    def __init__(
        self,
        prices: pd.DataFrame,
        index_prices: pd.DataFrame,
        universe_size: int = UNIVERSE_SIZE,
        fraction: float = LOW_BETA_FRACTION,
    ) -> None:
        """Pivots the prices and lines them up with the market.

        Args:
            prices (pd.DataFrame): Columns symbol, date, close and volume.
            index_prices (pd.DataFrame): Columns date and close of the
                NIFTY 500.
            universe_size (int): Size of the ranked universe.
            fraction (float): The share of ranked shares held.

        Returns:
            None.
        """
        frame = prices.copy()
        frame['date'] = pd.to_datetime(frame['date']).dt.normalize()
        frame = frame.drop_duplicates(['symbol', 'date'], keep='last')
        close = frame.pivot(
            index='date', columns='symbol', values='close'
        ).sort_index()
        volume = frame.pivot(
            index='date', columns='symbol', values='volume'
        ).reindex(index=close.index, columns=close.columns)
        market = index_prices.copy()
        market['date'] = pd.to_datetime(market['date']).dt.normalize()
        market = market.drop_duplicates('date', keep='last').set_index('date')[
            'close'
        ]
        days = close.index.intersection(market.index)
        self.close = close.reindex(days).sort_index(axis=1)
        self.traded_value = (self.close * volume.reindex(days)).sort_index(
            axis=1
        )
        self.market = market.reindex(days)
        self.universe_size = universe_size
        self.fraction = fraction

    def month_ends(self) -> pd.DatetimeIndex:
        """Gives the last trading day in the data of every month.

        Returns:
            pd.DatetimeIndex: One date per month, in order.
        """
        dates = pd.Series(self.close.index, index=self.close.index)
        grouped = dates.groupby(self.close.index.to_period('M')).max()
        return pd.DatetimeIndex(grouped.to_numpy())

    def formation_date(self, as_of: datetime.date) -> pd.Timestamp:
        """Gives the month-end the targets are built at.

        Args:
            as_of (datetime.date): The day the targets are built.

        Returns:
            pd.Timestamp: The last trading day of the last completed month.

        Raises:
            ValueError: There is no completed month in the data, or the data
                stops more than four days before that month ended.
        """
        ends = self.month_ends()
        month = pd.Period(as_of, freq='M')
        done = ends[ends.to_period('M') < month]
        if len(done) == 0:
            raise ValueError('No completed month in the data')
        last = done[-1]
        month_last_day = last.to_period('M').end_time.normalize()
        if (month_last_day - last).days > 4:
            raise ValueError(
                f'The data reaches {last.date()} but the month ended on '
                f'{month_last_day.date()}; wait for the last prices'
            )
        return last

    def log_returns(self) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
        """Builds daily log returns, dropping moves too big to believe.

        A share's return on the day it trades again is measured from its
        last close, so a gap is one return. A fall of more than 45% or a
        rise of more than 100% in a day is treated as a price-adjustment
        error and set to missing; the days are listed in the third result.

        Returns:
            tuple[pd.DataFrame, pd.Series, pd.DataFrame]: The shares' log
                returns, the market's, and a table of the dropped moves.
        """
        logs = np.log(self.close.where(self.close > 0))
        returns = logs.ffill().diff().where(logs.notna())
        simple = np.expm1(returns)
        bad = (simple < DROP_LIMIT) | (simple > RISE_LIMIT)
        dropped = simple.where(bad).stack().dropna().rename('move').reset_index()
        returns = returns.mask(bad)
        market = np.log(self.market).diff()
        return returns, market, dropped

    def eligible(self, position: int) -> pd.Series:
        """Finds the shares in the ranked universe at one day.

        A share needs a close of at least 2 rupees, a close in each of the
        last 5 days, and a close on at least half of the last 252 days. The
        500 with the highest median daily traded value, counting days
        without trading as zero, are kept.

        Args:
            position (int): The row of the formation day.

        Returns:
            pd.Series: A boolean for every share.
        """
        first = max(position - LIQUIDITY_DAYS + 1, 0)
        window = self.close.iloc[first : position + 1]
        traded_days = window.notna().sum(axis=0).to_numpy()
        recent = self.close.iloc[position - RECENT_DAYS + 1 : position + 1]
        last_close = self.close.ffill(limit=STALE_DAYS).iloc[position]
        allowed = (
            (traded_days >= MINIMUM_TRADING_SHARE * LIQUIDITY_DAYS)
            & recent.notna().all(axis=0).to_numpy()
            & (last_close.to_numpy() >= MINIMUM_PRICE)
        )
        value = self.traded_value.iloc[first : position + 1]
        median = value.fillna(0.0).median(axis=0).to_numpy()
        score = np.where(allowed, median, -1.0)
        top = np.argsort(-score, kind='stable')[: self.universe_size]
        top = top[score[top] >= 0.0]
        chosen = np.zeros(len(self.close.columns), dtype=bool)
        chosen[top] = True
        return pd.Series(chosen, index=self.close.columns)

    def betas(self, position: int) -> pd.Series:
        """Estimates every share's shrunk beta at one day.

        Args:
            position (int): The row of the formation day.

        Returns:
            pd.Series: Betas by symbol, NaN where there are too few returns.
        """
        returns, market, _ = self.log_returns()
        first = max(position - VOLATILITY_DAYS + 1, 0)
        window = returns.iloc[first : position + 1]
        count = window.notna().sum(axis=0)
        share_vol = window.std(axis=0, ddof=1).where(
            count >= MINIMUM_VOLATILITY_OBS
        )
        market_vol = market.iloc[first : position + 1].std(ddof=1)
        shares3 = returns.rolling(HORIZON_DAYS).sum()
        market3 = market.rolling(HORIZON_DAYS).sum()
        first = max(position - CORRELATION_DAYS + 1, 0)
        x = shares3.iloc[first : position + 1].to_numpy()
        y = market3.iloc[first : position + 1].to_numpy()
        valid = ~np.isnan(x) & ~np.isnan(y)[:, None]
        n = valid.sum(axis=0)
        with np.errstate(all='ignore'):
            mean_x = np.where(valid, x, 0.0).sum(axis=0) / n
            mean_y = np.where(valid, y[:, None], 0.0).sum(axis=0) / n
            dx = np.where(valid, x - mean_x, 0.0)
            dy = np.where(valid, y[:, None] - mean_y, 0.0)
            rho = (dx * dy).sum(axis=0) / np.sqrt(
                (dx * dx).sum(axis=0) * (dy * dy).sum(axis=0)
            )
        rho = pd.Series(
            np.where(n >= MINIMUM_CORRELATION_OBS, rho, np.nan),
            index=self.close.columns,
        )
        raw = rho * share_vol / market_vol
        return SHRINKAGE * raw + (1.0 - SHRINKAGE)

    def targets(
        self,
        as_of: datetime.date,
        excluded: set[str] | None = None,
    ) -> tuple[pd.Series, dict[str, Any]]:
        """Builds the target weights.

        Args:
            as_of (datetime.date): The day the targets are built.
            excluded (set[str] | None): Symbols never to hold.

        Returns:
            tuple[pd.Series, dict[str, Any]]: Weights by symbol, summing to
                1, and details: the formation date, the number of ranked
                shares, the portfolio's average beta, and the dropped moves.

        Raises:
            ValueError: The data is too short or stops too early.
        """
        excluded = excluded or set()
        formation = self.formation_date(as_of)
        position = self.close.index.get_loc(formation)
        if position < CORRELATION_DAYS // 2:
            raise ValueError('Not enough history for the correlation window')
        ranked = self.eligible(position)
        beta = self.betas(position)
        usable = ranked & beta.notna()
        usable &= ~pd.Series(
            [name in excluded for name in beta.index], index=beta.index
        )
        beta = beta[usable]
        count = round(self.fraction * len(beta))
        if count < 5:
            raise ValueError(f'Only {len(beta)} shares have a beta')
        chosen = beta.sort_values(kind='stable').iloc[:count]
        weights = pd.Series(1.0 / count, index=chosen.index)
        _, _, dropped = self.log_returns()
        window_start = self.close.index[max(position - VOLATILITY_DAYS + 1, 0)]
        dropped = dropped[
            (dropped['date'] >= window_start)
            & (dropped['date'] <= formation)
            & dropped['symbol'].isin(beta.index)
        ]
        details = {
            'formation': formation,
            'ranked': len(beta),
            'average_beta': float(chosen.mean()),
            'dropped': dropped,
        }
        return weights.sort_index(), details

    def overlay(self, average_beta: float) -> float:
        """Gives the NIFTY futures notional that lifts the beta to one.

        Args:
            average_beta (float): The portfolio's average shrunk beta.

        Returns:
            float: Notional as a fraction of capital, 0 when the beta is
                already one or more, and at most 1.5.
        """
        if average_beta <= 0:
            return 0.0
        return float(min(max(1.0 / average_beta - 1.0, 0.0), MAXIMUM_OVERLAY))


class UbiPrices:
    """Reads daily NSE share and index prices from UBI through tradingmachine."""

    BATCH = 100

    def load(
        self,
        as_of: datetime.date,
        days: int = 2000,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Fetches adjusted daily closes and volumes.

        Args:
            as_of (datetime.date): The day the targets are built.
            days (int): How many calendar days of history to fetch; 2,000
                reaches back more than five years.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: Columns symbol, date, close
                and volume for every listed share, and columns date and
                close for the NIFTY 500.

        Raises:
            RuntimeError: UBI returned no prices.
        """
        from tradingmachine.unified_broker_interface import client

        ubi = client.UnifiedBrokerInterface()
        start = (as_of - datetime.timedelta(days=days)).isoformat()
        master = ubi.get(
            '/api/instruments/master',
            params={'exchange': 'nse', 'segment': 'equities'},
        )
        funds = self._symbols(ubi, 'funds')
        listed = [
            (row['instrument_id'], row['symbol'])
            for row in master
            if row['symbol'] not in funds
            and not FUND_PATTERN.search(row['symbol'])
        ]
        shares = self._candles(ubi, listed, start, as_of)
        indices = self._symbols_with_ids(ubi, 'equity_indices')
        if 'NIFTY 500' not in indices:
            raise RuntimeError('UBI has no NIFTY 500 index')
        market = self._candles(
            ubi, [(indices['NIFTY 500'], 'NIFTY 500')], start, as_of
        )
        return shares, market[['date', 'close']]

    def _candles(
        self,
        ubi: Any,
        listed: list[tuple[str, str]],
        start: str,
        as_of: datetime.date,
    ) -> pd.DataFrame:
        """Fetches candles in batches.

        Args:
            ubi (Any): The UBI client.
            listed (list[tuple[str, str]]): Pairs of instrument id and symbol.
            start (str): The first date.
            as_of (datetime.date): The last date.

        Returns:
            pd.DataFrame: Columns symbol, date, close and volume.

        Raises:
            RuntimeError: UBI returned no prices.
        """
        frames = []
        for first in range(0, len(listed), self.BATCH):
            batch = listed[first : first + self.BATCH]
            body = {
                'instruments': [{'instrument_id': item[0]} for item in batch],
                'interval': 'day',
                'adjusted': True,
                'from': start,
                'to': as_of.isoformat(),
            }
            answer = ubi.post('/api/instruments/prices', body=body)
            for result in answer['results']:
                if result['status'] != 200 or not result['data']['candles']:
                    continue
                data = result['data']
                frame = pd.DataFrame(data['candles'], columns=data['columns'])
                frame['symbol'] = batch[result['request_index']][1]
                frames.append(frame)
        if not frames:
            raise RuntimeError('UBI returned no prices')
        table = pd.concat(frames, ignore_index=True)
        table['date'] = (
            pd.to_datetime(table['time'], utc=True)
            .dt.tz_convert('Asia/Kolkata')
            .dt.tz_localize(None)
            .dt.normalize()
        )
        return table[['symbol', 'date', 'close', 'volume']]

    def _symbols(self, ubi: Any, segment: str) -> set[str]:
        """Reads the symbols of a segment, empty if UBI has none.

        Args:
            ubi (Any): The UBI client.
            segment (str): The segment's name.

        Returns:
            set[str]: Symbols.
        """
        return set(self._symbols_with_ids(ubi, segment))

    def _symbols_with_ids(self, ubi: Any, segment: str) -> dict[str, str]:
        """Reads symbols and instrument ids of a segment.

        Args:
            ubi (Any): The UBI client.
            segment (str): The segment's name.

        Returns:
            dict[str, str]: Instrument id by symbol, empty if UBI has no
                such segment.
        """
        from tradingmachine.unified_broker_interface import exceptions

        try:
            rows = ubi.get(
                '/api/instruments/master',
                params={'exchange': 'nse', 'segment': segment},
            )
        except exceptions.UnifiedBrokerInterfaceError:
            return {}
        return {row['symbol']: row['instrument_id'] for row in rows}


class BuildTargetsApplication:
    """Reads prices, builds the targets and writes the CSV."""

    def run(self) -> None:
        """Parses the command line, builds the targets and prints a summary.

        Returns:
            None.

        Raises:
            ValueError: The data is too short or stops too early.
        """
        parser = argparse.ArgumentParser(
            description="Build the month's target weights."
        )
        parser.add_argument('output', help='CSV of symbol,weight to write')
        parser.add_argument('--previous', help="last month's CSV, for changes")
        parser.add_argument(
            '--as-of', help='date to build for, YYYY-MM-DD; default today'
        )
        parser.add_argument(
            '--prices-file',
            help='parquet or CSV of symbol,date,close,volume instead of UBI',
        )
        parser.add_argument(
            '--index-file',
            help='parquet or CSV of date,close of the NIFTY 500 instead of UBI',
        )
        parser.add_argument(
            '--exclude', nargs='*', default=[], help='symbols never to hold'
        )
        parser.add_argument(
            '--capital', type=float, help='rupees, to show whole-share fit'
        )
        arguments = parser.parse_args()
        as_of = datetime.date.today()
        if arguments.as_of:
            as_of = datetime.date.fromisoformat(arguments.as_of)
        if arguments.prices_file and arguments.index_file:
            prices = self._read_file(arguments.prices_file)
            index_prices = self._read_file(arguments.index_file)
        else:
            prices, index_prices = UbiPrices().load(as_of)
        builder = LowBetaTargets(prices, index_prices)
        weights, details = builder.targets(as_of, set(arguments.exclude))
        output = Path(arguments.output)
        weights.rename('weight').rename_axis('symbol').reset_index().to_csv(
            output, index=False, float_format='%.8f'
        )
        self._print_summary(builder, weights, details, arguments.previous)
        if arguments.capital:
            self._print_fit(weights, builder, details, arguments.capital)

    def _read_file(self, path: str) -> pd.DataFrame:
        """Reads a prices file.

        Args:
            path (str): A parquet or CSV file.

        Returns:
            pd.DataFrame: The prices.
        """
        if path.endswith('.csv'):
            return pd.read_csv(path)
        return pd.read_parquet(path)

    def _print_summary(
        self,
        builder: LowBetaTargets,
        weights: pd.Series,
        details: dict[str, Any],
        previous: str | None,
    ) -> None:
        """Prints what was built.

        Args:
            builder (LowBetaTargets): The builder.
            weights (pd.Series): The targets.
            details (dict[str, Any]): The build's details.
            previous (str | None): Last month's CSV, or None.

        Returns:
            None.
        """
        print(f'Formation month-end: {details["formation"].date()}')
        print(f'Ranked shares with a beta: {details["ranked"]}')
        print(f'Holdings: {len(weights)}')
        print(f'Largest weight: {weights.max():.4%}')
        print(f'Average shrunk beta of the holdings: {details["average_beta"]:.3f}')
        overlay = builder.overlay(details['average_beta'])
        print(
            'Optional NIFTY futures overlay to lift beta to 1 '
            f'(portfolio L3): {overlay:.2f} of capital, long'
        )
        dropped = details['dropped']
        if len(dropped):
            names = sorted(dropped['symbol'].unique())
            print(
                f'Price moves dropped as adjustment errors in the last year: '
                f'{len(dropped)} in {len(names)} holdings or ranked shares'
            )
        if previous:
            old = pd.read_csv(previous).set_index('symbol')['weight']
            joiners = sorted(set(weights.index) - set(old.index))
            leavers = sorted(set(old.index) - set(weights.index))
            combined = pd.concat([weights, old], axis=1).fillna(0.0)
            turnover = (combined.iloc[:, 0] - combined.iloc[:, 1]).abs().sum() / 2
            print(f'Joiners ({len(joiners)}): {", ".join(joiners)}')
            print(f'Leavers ({len(leavers)}): {", ".join(leavers)}')
            print(f'One-way turnover against last month: {turnover:.1%}')

    def _print_fit(
        self,
        weights: pd.Series,
        builder: LowBetaTargets,
        details: dict[str, Any],
        capital: float,
    ) -> None:
        """Prints how well whole shares fit the weights.

        Args:
            weights (pd.Series): The targets.
            builder (LowBetaTargets): The builder, holding the closes.
            details (dict[str, Any]): The build's details.
            capital (float): Rupees to invest.

        Returns:
            None.
        """
        prices = builder.close.loc[details['formation'], weights.index]
        shares = np.floor(weights * capital / prices)
        invested = float((shares * prices).sum())
        print(
            f'With Rs {capital:,.0f}: {invested / capital:.1%} invested in '
            f'whole shares, {int((shares == 0).sum())} of {len(weights)} '
            'targets round to zero shares'
        )


if __name__ == '__main__':
    BuildTargetsApplication().run()
