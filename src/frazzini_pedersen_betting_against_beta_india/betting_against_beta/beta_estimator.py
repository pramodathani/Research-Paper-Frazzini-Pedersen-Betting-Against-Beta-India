"""Estimates betas the way Frazzini and Pedersen (2014) do, page 9 of the draft."""

import numpy as np
import pandas as pd


class BetaEstimator:
    """Estimates each share's beta at chosen dates from daily log returns.

    A share's beta is rho * sigma_i / sigma_m. The volatilities come from
    daily log excess returns over a short window (the paper uses 1 year) and
    the correlation from overlapping multi-day log returns over a longer
    window (the paper uses 5 years of 3-day returns). The estimate is then
    shrunk towards 1: w * beta + (1 - w) * 1 with w = 0.6.

    Every estimate at a date uses only returns up to and including that
    date, so a portfolio formed on the date can hold the share from the day
    after.

    Attributes:
        returns: Daily log excess returns, one row per trading day and one
            column per share, NaN where the share did not trade.
        market: The market's daily log excess return on the same days.
        minimum_volatility_obs: Fewest daily returns for a volatility.
        minimum_correlation_obs: Fewest multi-day returns for a correlation.
    """

    def __init__(
        self,
        returns: pd.DataFrame,
        market: pd.Series,
        minimum_volatility_obs: int = 120,
        minimum_correlation_obs: int = 750,
    ) -> None:
        """Keeps the return tables.

        Args:
            returns (pd.DataFrame): Daily log excess returns of the shares.
            market (pd.Series): Daily log excess returns of the market, on
                the same index as the shares.
            minimum_volatility_obs (int): Fewest returns for a volatility.
            minimum_correlation_obs (int): Fewest returns for a correlation.

        Returns:
            None.

        Raises:
            ValueError: The market and the shares have different dates.
        """
        if not returns.index.equals(market.index):
            raise ValueError('market and returns must share one date index')
        self.returns = returns.astype('float32')
        self.market = market.astype('float64')
        self.minimum_volatility_obs = minimum_volatility_obs
        self.minimum_correlation_obs = minimum_correlation_obs
        self._overlapping: dict[int, tuple[np.ndarray, np.ndarray]] = {}

    def volatility(
        self,
        dates: pd.DatetimeIndex,
        window_days: int,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """Gives each share's and the market's volatility of daily returns.

        Args:
            dates (pd.DatetimeIndex): Trading days at which to estimate.
            window_days (int): Trading days in the window.

        Returns:
            tuple[pd.DataFrame, pd.Series]: The shares' standard deviations
                (NaN with too few returns) and the market's, one row per date.
        """
        values = self.returns.to_numpy(dtype='float64')
        market = self.market.to_numpy()
        positions = self.returns.index.get_indexer(dates)
        shares = np.full((len(dates), values.shape[1]), np.nan)
        market_vol = np.full(len(dates), np.nan)
        for row, position in enumerate(positions):
            start = max(position - window_days + 1, 0)
            window = values[start : position + 1]
            count = np.sum(~np.isnan(window), axis=0)
            with np.errstate(all='ignore'):
                deviation = np.nanstd(window, axis=0, ddof=1)
            deviation[count < self.minimum_volatility_obs] = np.nan
            shares[row] = deviation
            market_vol[row] = np.nanstd(market[start : position + 1], ddof=1)
        return (
            pd.DataFrame(shares, index=dates, columns=self.returns.columns),
            pd.Series(market_vol, index=dates),
        )

    def correlation(
        self,
        dates: pd.DatetimeIndex,
        window_days: int,
        horizon_days: int = 3,
    ) -> pd.DataFrame:
        """Gives each share's correlation with the market.

        The returns are overlapping sums of horizon_days daily log returns,
        and a sum is missing when any of its days is. Only days on which the
        share has a sum are used, for both the share and the market.

        Args:
            dates (pd.DatetimeIndex): Trading days at which to estimate.
            window_days (int): Trading days in the window.
            horizon_days (int): Days in each return; 1 uses daily returns.

        Returns:
            pd.DataFrame: Correlations, NaN with too few returns, one row
                per date.
        """
        shares, market = self._overlapping_returns(horizon_days)
        positions = self.returns.index.get_indexer(dates)
        result = np.full((len(dates), shares.shape[1]), np.nan)
        for row, position in enumerate(positions):
            start = max(position - window_days + 1, 0)
            window = shares[start : position + 1]
            result[row] = self._correlate(window, market[start : position + 1])
        return pd.DataFrame(result, index=dates, columns=self.returns.columns)

    def beta(
        self,
        dates: pd.DatetimeIndex,
        volatility_days: int = 252,
        correlation_days: int = 1260,
        horizon_days: int = 3,
        shrinkage: float = 0.6,
    ) -> pd.DataFrame:
        """Gives the shrunk betas.

        Args:
            dates (pd.DatetimeIndex): Trading days at which to estimate.
            volatility_days (int): Trading days for the volatilities.
            correlation_days (int): Trading days for the correlation.
            horizon_days (int): Days in each correlation return.
            shrinkage (float): The weight w on the raw estimate; 1 gives
                the raw beta and 0 gives 1.

        Returns:
            pd.DataFrame: Betas, NaN where either estimate is missing.
        """
        shares, market = self.volatility(dates, volatility_days)
        rho = self.correlation(dates, correlation_days, horizon_days)
        return self.combine(shares, market, rho, shrinkage)

    @staticmethod
    def combine(
        share_volatility: pd.DataFrame,
        market_volatility: pd.Series,
        correlation: pd.DataFrame,
        shrinkage: float,
    ) -> pd.DataFrame:
        """Joins the parts into a shrunk beta.

        Args:
            share_volatility (pd.DataFrame): Each share's volatility.
            market_volatility (pd.Series): The market's volatility.
            correlation (pd.DataFrame): Each share's correlation.
            shrinkage (float): The weight w on the raw estimate.

        Returns:
            pd.DataFrame: w * rho * sigma_i / sigma_m + (1 - w).
        """
        raw = correlation * share_volatility.div(market_volatility, axis=0)
        return shrinkage * raw + (1.0 - shrinkage)

    def _overlapping_returns(
        self,
        horizon_days: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Sums log returns over horizon_days, once per horizon.

        Args:
            horizon_days (int): Days in each return.

        Returns:
            tuple[np.ndarray, np.ndarray]: The shares' and the market's
                overlapping returns, NaN until a full window exists.
        """
        if horizon_days not in self._overlapping:
            shares = self.returns.rolling(horizon_days).sum()
            market = self.market.rolling(horizon_days).sum()
            self._overlapping[horizon_days] = (
                shares.to_numpy(dtype='float64'),
                market.to_numpy(),
            )
        return self._overlapping[horizon_days]

    def _correlate(self, window: np.ndarray, market: np.ndarray) -> np.ndarray:
        """Correlates every column of a window with the market.

        Args:
            window (np.ndarray): Rows are days, columns are shares.
            market (np.ndarray): The market's returns on those days.

        Returns:
            np.ndarray: One correlation per share, NaN with too few days.
        """
        valid = ~np.isnan(window) & ~np.isnan(market)[:, None]
        count = valid.sum(axis=0)
        x = np.where(valid, window, 0.0)
        y = np.where(valid, market[:, None], 0.0)
        with np.errstate(all='ignore'):
            mean_x = x.sum(axis=0) / count
            mean_y = y.sum(axis=0) / count
            dx = np.where(valid, window - mean_x, 0.0)
            dy = np.where(valid, market[:, None] - mean_y, 0.0)
            covariance = (dx * dy).sum(axis=0)
            spread = np.sqrt((dx * dx).sum(axis=0) * (dy * dy).sum(axis=0))
            correlation = covariance / spread
        correlation[count < self.minimum_correlation_obs] = np.nan
        return correlation
