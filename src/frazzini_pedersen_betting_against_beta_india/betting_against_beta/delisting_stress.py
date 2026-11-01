"""A stress test for shares that stop trading while a portfolio holds them."""

import numpy as np
import pandas as pd

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.return_panel import (
    ReturnPanel,
)


class DelistingStress:
    """Charges a loss to shares that vanish from the price files.

    The returns keep a share's last return and nothing after it, so the
    engine treats a vanished share as earning nothing. Here every share
    whose last price is more than gap_days before the end of the data gets
    an extra return, the shock, in the first month in which it can no
    longer be traded: the next month when its last trade is in the last
    five trading days of its month, otherwise its last month, compounded
    onto the return it already has. Shares that were merged or renamed
    without a link also get the shock, so the test is conservative.

    Attributes:
        panel: The return panel.
        gap_days: How long before the end of the data a last price must be
            for the share to count as gone.
        tail_days: Trading days at the end of a month that count as the
            month end.
    """

    def __init__(
        self,
        panel: ReturnPanel,
        gap_days: int = 45,
        tail_days: int = 5,
    ) -> None:
        """Keeps the panel.

        Args:
            panel (ReturnPanel): The return panel.
            gap_days (int): Days before the data end for a share to count
                as gone.
            tail_days (int): Trading days that count as the month end.

        Returns:
            None.
        """
        self.panel = panel
        self.gap_days = gap_days
        self.tail_days = tail_days

    def vanished(self) -> pd.DataFrame:
        """Finds the shares that stopped trading.

        Returns:
            pd.DataFrame: Columns symbol, last_date and shock_month (the
                month the loss is charged in).
        """
        returns = self.panel.returns
        has_return = returns.notna()
        positions = np.where(
            has_return.to_numpy().any(axis=0),
            len(returns) - 1 - np.argmax(has_return.to_numpy()[::-1], axis=0),
            -1,
        )
        last_dates = pd.Series(
            [returns.index[p] if p >= 0 else pd.NaT for p in positions],
            index=returns.columns,
        ).dropna()
        end = returns.index[-1]
        gone = last_dates[last_dates < end - pd.Timedelta(days=self.gap_days)]
        index = returns.index
        month_last_position = (
            pd.Series(np.arange(len(index)), index=index)
            .groupby(index.to_period('M'))
            .max()
        )
        rows = []
        for symbol, last in gone.items():
            period = last.to_period('M')
            position = index.get_loc(last)
            near_end = month_last_position[period] - position < self.tail_days
            rows.append(
                {
                    'symbol': symbol,
                    'last_date': last,
                    'shock_month': period + 1 if near_end else period,
                }
            )
        return pd.DataFrame(rows)

    def monthly_returns(self, shock: float) -> pd.DataFrame:
        """Gives the monthly returns with the shock charged.

        Args:
            shock (float): The extra return, such as -0.3 or -1.0.

        Returns:
            pd.DataFrame: Monthly returns, with each vanished share's shock
                month changed.
        """
        monthly = self.panel.monthly_returns().copy()
        for row in self.vanished().itertuples(index=False):
            if row.shock_month not in monthly.index:
                continue
            current = monthly.at[row.shock_month, row.symbol]
            if np.isnan(current):
                monthly.at[row.shock_month, row.symbol] = shock
            else:
                monthly.at[row.shock_month, row.symbol] = (1.0 + current) * (
                    1.0 + shock
                ) - 1.0
        return monthly
