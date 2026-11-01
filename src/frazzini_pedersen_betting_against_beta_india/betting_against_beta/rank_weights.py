"""Rank-based portfolio weights from Frazzini and Pedersen (2014), eq. 16-17."""

import numpy as np
import pandas as pd


class RankWeights:
    """Turns one month's betas into low-beta and high-beta weights.

    With z the rank of each beta (ties share the average rank) and zbar the
    mean rank, the high-beta weights are k * (z - zbar)+ and the low-beta
    weights k * (z - zbar)-, where k = 2 / sum(|z - zbar|). Each side then
    sums to one, and the share at the median has zero weight.
    """

    def split(self, betas: pd.Series) -> tuple[pd.Series, pd.Series]:
        """Gives the two sides' weights.

        Args:
            betas (pd.Series): Betas of the shares in the universe, indexed
                by symbol, with no NaN.

        Returns:
            tuple[pd.Series, pd.Series]: The low-beta weights and the
                high-beta weights, each summing to one (all zero when
                fewer than two shares or every beta is tied).
        """
        ranks = betas.rank(method='average')
        centred = ranks - ranks.mean()
        total = centred.abs().sum()
        if len(betas) < 2 or total == 0:
            zero = pd.Series(0.0, index=betas.index)
            return zero, zero.copy()
        scale = 2.0 / total
        high = scale * centred.clip(lower=0.0)
        low = scale * (-centred).clip(lower=0.0)
        return low, high

    def bab_leverage(
        self,
        betas: pd.Series,
        low: pd.Series,
        high: pd.Series,
    ) -> tuple[float, float]:
        """Gives the two sides' betas.

        Args:
            betas (pd.Series): The shares' betas.
            low (pd.Series): The low-beta weights.
            high (pd.Series): The high-beta weights.

        Returns:
            tuple[float, float]: The low side's beta and the high side's.
        """
        return float((low * betas).sum()), float((high * betas).sum())

    def bab_return(
        self,
        returns: pd.Series,
        betas: pd.Series,
        risk_free: float,
    ) -> float:
        """Gives the BAB factor's return for one month.

        Args:
            returns (pd.Series): The month's total returns of the shares.
            betas (pd.Series): Betas at formation, same index.
            risk_free (float): The month's risk-free return.

        Returns:
            float: (r_L - rf) / beta_L - (r_H - rf) / beta_H, or NaN when
                either side's beta is not positive.
        """
        low, high = self.split(betas)
        beta_low, beta_high = self.bab_leverage(betas, low, high)
        if beta_low <= 0 or beta_high <= 0:
            return float('nan')
        filled = returns.reindex(betas.index).fillna(0.0)
        r_low = float((low * filled).sum())
        r_high = float((high * filled).sum())
        return (r_low - risk_free) / beta_low - (r_high - risk_free) / beta_high

    def groups(self, betas: pd.Series, count: int) -> pd.Series:
        """Cuts shares into equally sized groups by beta.

        Args:
            betas (pd.Series): The shares' betas.
            count (int): The number of groups, 10 for deciles.

        Returns:
            pd.Series: Group numbers from 1 (lowest beta) to count.
        """
        ranks = betas.rank(method='first')
        edges = np.linspace(0, len(betas), count + 1)
        numbers = np.searchsorted(edges[1:-1], ranks - 0.5, side='right') + 1
        return pd.Series(numbers, index=betas.index)
