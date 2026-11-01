"""Turns betas and universes into monthly target weights."""

import numpy as np
import pandas as pd

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.rank_weights import (
    RankWeights,
)


class PortfolioBuilder:
    """Builds the weights of the beta-sorted portfolios.

    Every table has one row per holding month (a PeriodIndex) and one column
    per share. A row is the target at the start of that month, made from the
    betas and universe on the last trading day of the month before. With a
    holding period of K months, the row is the average of the last K
    formation months' weights, which is the overlapping cohort portfolio of
    Jegadeesh and Titman with each cohort given 1/K of the capital.

    Attributes:
        betas: Betas at each formation day, NaN where unknown.
        eligible: True where a share may be held after that formation day.
        weights: The rank weight calculator.
        value: Traded value used for value weighting, or None.
    """

    def __init__(
        self,
        betas: pd.DataFrame,
        eligible: pd.DataFrame,
        value: pd.DataFrame | None = None,
    ) -> None:
        """Keeps the tables, lined up on the formation days.

        Args:
            betas (pd.DataFrame): Betas by formation day and share.
            eligible (pd.DataFrame): The universe on the same days.
            value (pd.DataFrame | None): Weights for value weighting, such as
                median traded value, on the same days.

        Returns:
            None.
        """
        self.betas = betas.where(eligible.reindex_like(betas).fillna(False))
        self.eligible = eligible
        self.value = value
        self.weights = RankWeights()

    def holding_periods(self) -> pd.PeriodIndex:
        """Gives the month each formation day's portfolio is held in.

        Returns:
            pd.PeriodIndex: One month per formation day, the month after.
        """
        return self.betas.index.to_period('M') + 1

    def bab(self, holding_months: int = 1) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Builds the BAB factor's weights.

        Args:
            holding_months (int): K, the months a cohort is held.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: The weights, long side
                1/beta_L times the low-beta rank weights and short side
                minus 1/beta_H times the high-beta rank weights, for excess
                returns; and a table with beta_low and beta_high per month.
        """
        rows = np.zeros(self.betas.shape)
        ex_ante = []
        for row, (_, betas) in enumerate(self.betas.iterrows()):
            present = betas.dropna()
            if len(present) < 10:
                ex_ante.append((np.nan, np.nan))
                continue
            low, high = self.weights.split(present)
            beta_low, beta_high = self.weights.bab_leverage(present, low, high)
            ex_ante.append((beta_low, beta_high))
            if beta_low <= 0 or beta_high <= 0:
                continue
            target = low / beta_low - high / beta_high
            rows[row, self.betas.columns.get_indexer(present.index)] = (
                target.to_numpy()
            )
        table = self._overlap(rows, holding_months)
        summary = pd.DataFrame(
            ex_ante,
            index=self.holding_periods(),
            columns=['beta_low', 'beta_high'],
        )
        return table, summary

    def groups(
        self,
        count: int = 10,
        holding_months: int = 1,
        weighting: str = 'equal',
    ) -> dict[int, pd.DataFrame]:
        """Builds the weights of the beta-sorted groups.

        Args:
            count (int): The number of groups, 10 for deciles.
            holding_months (int): K, the months a cohort is held.
            weighting (str): 'equal' or 'value'.

        Returns:
            dict[int, pd.DataFrame]: Weights for each group number, 1 being
                the lowest beta.

        Raises:
            ValueError: The weighting is unknown, or value weighting was
                asked for without a value table.
        """
        if weighting not in ('equal', 'value'):
            raise ValueError(f'unknown weighting: {weighting}')
        if weighting == 'value' and self.value is None:
            raise ValueError('value weighting needs a value table')
        shape = self.betas.shape
        rows = {g: np.zeros(shape) for g in range(1, count + 1)}
        for row, (date, betas) in enumerate(self.betas.iterrows()):
            present = betas.dropna()
            if len(present) < count * 2:
                continue
            numbers = self.weights.groups(present, count)
            if weighting == 'value':
                size = self.value.loc[date].reindex(present.index).fillna(0.0)
            else:
                size = pd.Series(1.0, index=present.index)
            for group in range(1, count + 1):
                members = size[numbers == group]
                total = members.sum()
                if total <= 0:
                    continue
                positions = self.betas.columns.get_indexer(members.index)
                rows[group][row, positions] = (members / total).to_numpy()
        return {
            g: self._overlap(values, holding_months)
            for g, values in rows.items()
        }

    def lowest_beta(
        self,
        fraction: float = 0.2,
        holding_months: int = 1,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """Builds the equal-weighted lowest-beta shares, long only.

        Args:
            fraction (float): The share of the universe held.
            holding_months (int): K, the months a cohort is held.

        Returns:
            tuple[pd.DataFrame, pd.Series]: The weights, summing to one, and
                the weighted beta of each formation month's cohort, by
                holding month.
        """
        rows = np.zeros(self.betas.shape)
        betas_out = []
        for row, (_, betas) in enumerate(self.betas.iterrows()):
            present = betas.dropna()
            count = int(round(fraction * len(present)))
            if count < 5:
                betas_out.append(np.nan)
                continue
            chosen = present.nsmallest(count)
            positions = self.betas.columns.get_indexer(chosen.index)
            rows[row, positions] = 1.0 / count
            betas_out.append(float(chosen.mean()))
        series = pd.Series(betas_out, index=self.holding_periods())
        return self._overlap(rows, holding_months), series

    def low_beta_half(
        self,
        holding_months: int = 1,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """Builds the BAB long leg alone, unlevered, long only.

        Args:
            holding_months (int): K, the months a cohort is held.

        Returns:
            tuple[pd.DataFrame, pd.Series]: The rank weights of the
                low-beta half and its weighted beta.
        """
        rows = np.zeros(self.betas.shape)
        betas_out = []
        for row, (_, betas) in enumerate(self.betas.iterrows()):
            present = betas.dropna()
            if len(present) < 10:
                betas_out.append(np.nan)
                continue
            low, high = self.weights.split(present)
            rows[row, self.betas.columns.get_indexer(present.index)] = (
                low.to_numpy()
            )
            betas_out.append(float((low * present).sum()))
        series = pd.Series(betas_out, index=self.holding_periods())
        return self._overlap(rows, holding_months), series

    def quintile_spread(
        self,
        holding_months: int = 1,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Builds the equal-weighted lowest against highest beta fifth.

        Each side is scaled to a beta of one, as in the BAB factor.

        Args:
            holding_months (int): K, the months a cohort is held.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: The weights, for excess
                returns, and the two sides' betas by holding month.
        """
        rows = np.zeros(self.betas.shape)
        ex_ante = []
        for row, (_, betas) in enumerate(self.betas.iterrows()):
            present = betas.dropna()
            count = len(present) // 5
            if count < 3:
                ex_ante.append((np.nan, np.nan))
                continue
            low = present.nsmallest(count)
            high = present.nlargest(count)
            beta_low = float(low.mean())
            beta_high = float(high.mean())
            ex_ante.append((beta_low, beta_high))
            if beta_low <= 0 or beta_high <= 0:
                continue
            rows[row, self.betas.columns.get_indexer(low.index)] = (
                1.0 / count / beta_low
            )
            rows[row, self.betas.columns.get_indexer(high.index)] = (
                -1.0 / count / beta_high
            )
        summary = pd.DataFrame(
            ex_ante,
            index=self.holding_periods(),
            columns=['beta_low', 'beta_high'],
        )
        return self._overlap(rows, holding_months), summary

    def _overlap(self, rows: np.ndarray, holding_months: int) -> pd.DataFrame:
        """Averages the last K formation months' weights.

        Args:
            rows (np.ndarray): Weights by formation day and share.
            holding_months (int): K.

        Returns:
            pd.DataFrame: The weights by holding month.
        """
        table = pd.DataFrame(
            rows, index=self.holding_periods(), columns=self.betas.columns
        )
        if holding_months > 1:
            table = table.rolling(holding_months, min_periods=1).mean()
        return table
