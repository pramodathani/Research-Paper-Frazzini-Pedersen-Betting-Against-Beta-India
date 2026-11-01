"""Point-in-time share universes: all NSE, liquid 500 and F&O."""

import numpy as np
import pandas as pd

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.return_panel import (
    ReturnPanel,
)


class Universes:
    """Decides which shares are eligible on each formation day.

    Universe A holds every company share whose last close is at least the
    minimum price and which traded on at least half the days of the past
    year. Universe B keeps the 500 of those with the highest median daily
    traded value over the past year, days without trading counting as zero.
    Universe C holds the shares of A that had a stock future that day.

    Attributes:
        panel: The return panel.
        minimum_price: The lowest last close allowed.
        window_days: Trading days in the past year.
        minimum_share_of_days: The share of days a share must have traded.
        liquid_count: The size of universe B.
    """

    def __init__(
        self,
        panel: ReturnPanel,
        minimum_price: float = 2.0,
        window_days: int = 252,
        minimum_share_of_days: float = 0.5,
        liquid_count: int = 500,
    ) -> None:
        """Sets the rules.

        Args:
            panel (ReturnPanel): The return panel.
            minimum_price (float): Lowest last close in rupees.
            window_days (int): Trading days in the look-back window.
            minimum_share_of_days (float): Fraction of days that must have a
                return.
            liquid_count (int): The size of universe B.

        Returns:
            None.
        """
        self.panel = panel
        self.minimum_price = minimum_price
        self.window_days = window_days
        self.minimum_share_of_days = minimum_share_of_days
        self.liquid_count = liquid_count

    def build(
        self,
        dates: pd.DatetimeIndex,
        futures: pd.DataFrame | None = None,
    ) -> dict[str, pd.DataFrame]:
        """Builds the three universes on the formation days.

        Args:
            dates (pd.DatetimeIndex): Formation days, all trading days.
            futures (pd.DataFrame | None): Columns date and symbol, one row
                per share per day with a stock future, or None for no F&O
                universe.

        Returns:
            dict[str, pd.DataFrame]: Boolean tables named A, B and C (C only
                when futures is given), one row per date and one column per
                share.
        """
        panel = self.panel
        positions = panel.returns.index.get_indexer(dates)
        returns = panel.returns.to_numpy()
        values = panel.traded_value.to_numpy()
        closes = panel.close.ffill(limit=10).to_numpy()
        shape = (len(dates), returns.shape[1])
        all_shares = np.zeros(shape, dtype=bool)
        liquid = np.zeros(shape, dtype=bool)
        needed = self.minimum_share_of_days * self.window_days
        for row, position in enumerate(positions):
            start = max(position - self.window_days + 1, 0)
            traded_days = np.sum(
                ~np.isnan(returns[start : position + 1]), axis=0
            )
            price = closes[position]
            eligible = (
                (traded_days >= needed)
                & ~np.isnan(price)
                & (price >= self.minimum_price)
                & ~np.isnan(returns[position - 4 : position + 1]).all(axis=0)
            )
            all_shares[row] = eligible
            window = np.nan_to_num(values[start : position + 1], nan=0.0)
            median = np.median(window, axis=0)
            score = np.where(eligible, median, -1.0)
            top = np.argsort(-score)[: self.liquid_count]
            top = top[score[top] >= 0.0]
            liquid[row, top] = True
        columns = panel.returns.columns
        result = {
            'A': pd.DataFrame(all_shares, index=dates, columns=columns),
            'B': pd.DataFrame(liquid, index=dates, columns=columns),
        }
        if futures is not None:
            result['C'] = self._futures_universe(dates, futures, result['A'])
        return result

    def median_traded_value(self, dates: pd.DatetimeIndex) -> pd.DataFrame:
        """Gives each share's median daily traded value over the past year.

        Args:
            dates (pd.DatetimeIndex): Formation days.

        Returns:
            pd.DataFrame: Rupees, days without trading counting as zero.
        """
        positions = self.panel.returns.index.get_indexer(dates)
        values = self.panel.traded_value.to_numpy()
        rows = np.zeros((len(dates), values.shape[1]))
        for row, position in enumerate(positions):
            start = max(position - self.window_days + 1, 0)
            window = np.nan_to_num(values[start : position + 1], nan=0.0)
            rows[row] = np.median(window, axis=0)
        return pd.DataFrame(
            rows, index=dates, columns=self.panel.returns.columns
        )

    def _futures_universe(
        self,
        dates: pd.DatetimeIndex,
        futures: pd.DataFrame,
        eligible: pd.DataFrame,
    ) -> pd.DataFrame:
        """Marks the shares that had a stock future on each date.

        Args:
            dates (pd.DatetimeIndex): Formation days.
            futures (pd.DataFrame): Columns date and symbol.
            eligible (pd.DataFrame): Universe A on the same dates.

        Returns:
            pd.DataFrame: Universe C, a subset of A.
        """
        flags = pd.DataFrame(
            {'date': futures['date'], 'symbol': futures['symbol'], 'flag': True}
        )
        flags = flags[flags['date'].isin(dates)]
        table = flags.pivot_table(
            index='date', columns='symbol', values='flag', aggfunc='first'
        )
        table = table.reindex(index=dates, columns=eligible.columns)
        return table.fillna(False).astype(bool) & eligible
