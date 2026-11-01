"""Loads the market index, the risk-free rate and the Indian factors."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from frazzini_pedersen_betting_against_beta_india.data.rbi_tbill_parser import (
    RbiTbillParser,
)


class MarketData:
    """Reads the saved total-return index, risk-free rate and factor files.

    Attributes:
        data: The study's data folder.
    """

    def __init__(self, data: Path) -> None:
        """Keeps the data folder.

        Args:
            data (Path): The study's data folder.

        Returns:
            None.
        """
        self.data = Path(data)

    def total_return_index(self, name: str = 'NIFTY_500') -> pd.Series:
        """Reads an index's daily total-return levels.

        Args:
            name (str): The file prefix, such as NIFTY_500 or NIFTY_50.

        Returns:
            pd.Series: The level by date, sorted, from the earliest saved.
        """
        rows = []
        folder = self.data / 'niftyindices/total_return'
        for path in sorted(folder.glob(f'{name}_[0-9]*.json')):
            rows.extend(json.loads(path.read_text()))
        table = pd.DataFrame(rows)
        if table.empty:
            return pd.Series(dtype='float64')
        dates = pd.to_datetime(table['Date'], format='%d %b %Y')
        levels = pd.to_numeric(table['TotalReturnsIndex'], errors='coerce')
        series = pd.Series(levels.to_numpy(), index=dates).dropna()
        series = series[~series.index.duplicated()]
        return series.sort_index()

    def market_returns(self, name: str = 'NIFTY_500') -> pd.Series:
        """Gives the index's daily simple returns.

        Args:
            name (str): The file prefix.

        Returns:
            pd.Series: Returns by date, from the second level on.
        """
        return self.total_return_index(name).pct_change().dropna()

    def iima_factors(self) -> pd.DataFrame:
        """Reads IIMA's monthly factors, in decimal returns.

        Returns:
            pd.DataFrame: Columns SMB, HML, WML, MF and RF by month, with
                market excess return MF; empty values are NaN.
        """
        path = next((self.data / 'nse/iima').glob('*.csv'))
        table = pd.read_csv(path, na_values=['NA'])
        table['month'] = pd.PeriodIndex(table['Date'], freq='M')
        table = table.drop(columns=['Date']).set_index('month')
        return table / 100.0

    def tbill_yields(self) -> pd.DataFrame:
        """Reads the scraped RBI 91-day yields.

        Returns:
            pd.DataFrame: Columns date and yield_91d in percent a year.
        """
        return RbiTbillParser().parse_folder(self.data / 'rbi/tbill_auctions')

    def risk_free_monthly(self) -> pd.Series:
        """Gives the monthly risk-free return in decimals.

        IIMA's RF is used where it exists. Later months use the mean of the
        month's 91-day cut-off yields divided by 12.

        Returns:
            pd.Series: The return by month.
        """
        iima = self.iima_factors()['RF'].dropna()
        bills = self.tbill_yields()
        extra = pd.Series(dtype='float64')
        if not bills.empty:
            monthly = bills.groupby(bills['date'].dt.to_period('M'))[
                'yield_91d'
            ].mean()
            extra = monthly / 100.0 / 12.0
            extra = extra[extra.index > iima.index.max()]
        combined = pd.concat([iima, extra])
        combined.name = 'rf'
        return combined

    def risk_free_daily(self, dates: pd.DatetimeIndex) -> pd.Series:
        """Spreads each month's risk-free return evenly over its days.

        Months with no risk-free value carry the last one forward.

        Args:
            dates (pd.DatetimeIndex): Trading days.

        Returns:
            pd.Series: The daily simple return by date.
        """
        monthly = self.risk_free_monthly().reindex(
            pd.period_range(dates.min(), dates.max(), freq='M')
        )
        monthly = monthly.ffill().bfill()
        periods = dates.to_period('M')
        days = pd.Series(1, index=dates).groupby(periods).transform('sum')
        values = monthly.reindex(periods).to_numpy()
        return pd.Series(values / days.to_numpy(), index=dates)

    @staticmethod
    def log_excess(simple: pd.Series | pd.DataFrame, rf_daily: pd.Series):
        """Turns simple returns into log excess returns.

        Args:
            simple (pd.Series | pd.DataFrame): Daily simple returns.
            rf_daily (pd.Series): Daily risk-free returns on the same index.

        Returns:
            pd.Series | pd.DataFrame: log(1 + r) - log(1 + rf), with returns
                at or below -100% set to NaN.
        """
        clean = simple.where(simple > -0.999)
        logs = np.log1p(clean)
        if isinstance(simple, pd.DataFrame):
            return logs.sub(np.log1p(rf_daily), axis=0)
        return logs - np.log1p(rf_daily)
