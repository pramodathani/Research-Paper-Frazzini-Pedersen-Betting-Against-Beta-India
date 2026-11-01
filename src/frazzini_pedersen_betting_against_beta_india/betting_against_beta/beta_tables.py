"""Beta estimates for every window setting, at every month end."""

import pandas as pd

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.beta_estimator import (
    BetaEstimator,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.return_panel import (
    ReturnPanel,
)


class BetaTables:
    """Computes the parts of a beta once per window and combines them.

    Volatility windows are counted in months (about 21 trading days each).
    The minimum number of observations scales with the window: 48% of the
    days for volatilities (120 of 252, as in the paper) and 60% of the days
    for correlations (750 of about 1,250).

    Attributes:
        estimator: The beta estimator over the panel's log excess returns.
        dates: The month-end formation days.
    """

    DAYS_PER_MONTH = 21

    def __init__(self, panel: ReturnPanel, dates: pd.DatetimeIndex) -> None:
        """Builds the estimator.

        Args:
            panel (ReturnPanel): The return panel.
            dates (pd.DatetimeIndex): Formation days.

        Returns:
            None.
        """
        self.dates = dates
        self.estimator = BetaEstimator(
            panel.log_excess, panel.market_log_excess
        )
        self._volatility: dict[int, tuple[pd.DataFrame, pd.Series]] = {}
        self._correlation: dict[tuple[int, int], pd.DataFrame] = {}

    def volatility(self, months: int) -> tuple[pd.DataFrame, pd.Series]:
        """Gives volatilities over a window of months.

        Args:
            months (int): The window in months.

        Returns:
            tuple[pd.DataFrame, pd.Series]: The shares' and the market's.
        """
        if months not in self._volatility:
            days = months * self.DAYS_PER_MONTH
            self.estimator.minimum_volatility_obs = int(0.48 * days)
            self._volatility[months] = self.estimator.volatility(
                self.dates, days
            )
        return self._volatility[months]

    def correlation(self, months: int, horizon_days: int = 3) -> pd.DataFrame:
        """Gives correlations over a window of months.

        Args:
            months (int): The window in months.
            horizon_days (int): Days in each return.

        Returns:
            pd.DataFrame: The correlations.
        """
        key = (months, horizon_days)
        if key not in self._correlation:
            days = months * self.DAYS_PER_MONTH
            self.estimator.minimum_correlation_obs = int(0.6 * days)
            self._correlation[key] = self.estimator.correlation(
                self.dates, days, horizon_days
            )
        return self._correlation[key]

    def beta(
        self,
        volatility_months: int = 12,
        correlation_months: int = 60,
        shrinkage: float = 0.6,
        horizon_days: int = 3,
    ) -> pd.DataFrame:
        """Gives the shrunk betas.

        Args:
            volatility_months (int): Months for the volatilities.
            correlation_months (int): Months for the correlation.
            shrinkage (float): The weight on the raw beta.
            horizon_days (int): Days in each correlation return.

        Returns:
            pd.DataFrame: Betas by formation day and share.
        """
        shares, market = self.volatility(volatility_months)
        rho = self.correlation(correlation_months, horizon_days)
        return BetaEstimator.combine(shares, market, rho, shrinkage)
