"""Wide daily and monthly tables of share returns, shared by every portfolio."""

from pathlib import Path

import numpy as np
import pandas as pd

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.market_data import (
    MarketData,
)


class ReturnPanel:
    """Holds daily returns, traded value and the market on one calendar.

    The calendar is every day on which NSE has a bhavcopy and the market
    index a level. A month's last trading day is the formation day of the
    portfolio held through the next month.

    Attributes:
        returns: Adjusted daily simple total returns, days by shares.
        traded_value: Rupees traded each day, NaN when the share did not
            trade.
        close: Raw closing prices.
        market: The market's daily simple return.
        risk_free: The daily risk-free return.
        log_excess: Daily log excess returns of the shares.
        market_log_excess: Daily log excess returns of the market.
    """

    def __init__(
        self,
        daily: pd.DataFrame,
        market: pd.Series,
        risk_free_monthly: pd.Series,
    ) -> None:
        """Pivots a long table and lines it up with the market.

        Args:
            daily (pd.DataFrame): Columns date, symbol, close, traded_value
                and ret, one row per symbol and date.
            market (pd.Series): The market's daily simple returns.
            risk_free_monthly (pd.Series): Monthly risk-free returns by
                month (a PeriodIndex).

        Returns:
            None.
        """
        wide = {}
        for column in ('ret', 'close', 'traded_value'):
            wide[column] = daily.pivot(
                index='date', columns='symbol', values=column
            ).astype('float32')
        calendar = wide['ret'].index.intersection(market.index).sort_values()
        self.returns = wide['ret'].reindex(calendar)
        self.close = wide['close'].reindex(calendar)
        self.traded_value = wide['traded_value'].reindex(calendar)
        self.market = market.reindex(calendar)
        self.risk_free_monthly = risk_free_monthly
        self.risk_free = self._daily_risk_free(calendar)
        self.log_excess = MarketData.log_excess(
            self.returns.astype('float64'), self.risk_free
        ).astype('float32')
        self.market_log_excess = MarketData.log_excess(
            self.market, self.risk_free
        )

    @classmethod
    def from_files(cls, data: Path, derived: Path) -> ReturnPanel:
        """Loads the saved daily returns and the market files.

        Args:
            data (Path): The study's data folder.
            derived (Path): The folder with daily_returns.parquet.

        Returns:
            ReturnPanel: The panel.
        """
        loader = MarketData(data)
        daily = pd.read_parquet(Path(derived) / 'daily_returns.parquet')
        return cls(daily, loader.market_returns(), loader.risk_free_monthly())

    def _daily_risk_free(self, calendar: pd.DatetimeIndex) -> pd.Series:
        """Spreads each month's risk-free return over its trading days.

        Args:
            calendar (pd.DatetimeIndex): The trading days.

        Returns:
            pd.Series: The daily return by day.
        """
        months = pd.period_range(calendar.min(), calendar.max(), freq='M')
        monthly = self.risk_free_monthly.reindex(months).ffill().bfill()
        periods = calendar.to_period('M')
        days = pd.Series(1, index=calendar).groupby(periods).transform('sum')
        values = monthly.reindex(periods).to_numpy()
        return pd.Series(values / days.to_numpy(), index=calendar)

    def month_ends(self) -> pd.DatetimeIndex:
        """Gives the last trading day of every month.

        Returns:
            pd.DatetimeIndex: One date per month.
        """
        dates = pd.Series(self.returns.index, index=self.returns.index)
        last = dates.groupby(self.returns.index.to_period('M')).max()
        return pd.DatetimeIndex(last.to_numpy())

    def monthly_returns(self) -> pd.DataFrame:
        """Compounds the daily returns within each month.

        A share with no return on any day of a month has NaN for it.

        Returns:
            pd.DataFrame: Simple returns, one row per month (a PeriodIndex)
                and one column per share.
        """
        logs = np.log1p(self.returns.astype('float64').clip(lower=-0.999))
        periods = self.returns.index.to_period('M')
        summed = logs.groupby(periods).sum(min_count=1)
        return np.expm1(summed)

    def monthly_market(self) -> pd.Series:
        """Compounds the market's daily returns within each month.

        Returns:
            pd.Series: The market's monthly simple return by month.
        """
        logs = np.log1p(self.market)
        periods = self.returns.index.to_period('M')
        return np.expm1(logs.groupby(periods).sum())
