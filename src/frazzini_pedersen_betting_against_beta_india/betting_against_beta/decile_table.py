"""The beta-decile table and the BAB row, after Frazzini and Pedersen's Table III."""

import pandas as pd

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.bab_study import (
    BabStudy,
)


class DecileTable:
    """Scores beta-sorted portfolios and the BAB factor.

    After costs, universes A and B are cash portfolios: both legs pay
    delivery costs and the short leg a yearly borrow fee through SLB, which
    few shares can actually be borrowed in (a paper portfolio). Universe C
    is held through stock futures: futures costs on the rebalance plus the
    monthly roll, and no borrow fee.

    The decile portfolios are long only, each fully invested in the shares
    of one beta group, so their returns are in excess of the risk-free rate
    after taking it off. The BAB row uses the leveraged weights.

    Attributes:
        study: The study's inputs.
        borrow_fee_annual: A yearly fee charged on the short leg's notional
            in the after-cost BAB row, as a fraction.
    """

    def __init__(
        self,
        study: BabStudy,
        borrow_fee_annual: float = 0.0,
        roll_impact: float = 0.0005,
    ) -> None:
        """Keeps the study.

        Args:
            study (BabStudy): The study's inputs.
            borrow_fee_annual (float): The yearly short fee as a fraction.
            roll_impact (float): Market impact per side of the monthly
                futures roll in universe C.

        Returns:
            None.
        """
        self.study = study
        self.borrow_fee_annual = borrow_fee_annual
        self.roll_impact = roll_impact

    def run(
        self,
        universe: str = 'A',
        weighting: str = 'equal',
        groups: int = 10,
        volatility_months: int = 12,
        correlation_months: int = 60,
        shrinkage: float = 0.6,
        holding_months: int = 1,
        impact_cost: float = 0.003,
        start: str | None = None,
    ) -> tuple[pd.DataFrame, dict[str, pd.Series]]:
        """Builds and scores the groups and the BAB factor.

        Args:
            universe (str): 'A', 'B' or 'C'.
            weighting (str): 'equal' or 'value' inside each group.
            groups (int): The number of beta groups.
            volatility_months (int): Months for the volatilities.
            correlation_months (int): Months for the correlation.
            shrinkage (float): The weight on the raw beta.
            holding_months (int): K, the months a cohort is held.
            impact_cost (float): Market impact per side for the after-cost
                BAB row.
            start (str | None): First holding month to score, YYYY-MM.

        Returns:
            tuple[pd.DataFrame, dict[str, pd.Series]]: The table, one row
                per group and one for BAB (before and after costs), and the
                monthly excess return series by name.
        """
        builder = self.study.builder(
            universe, volatility_months, correlation_months, shrinkage
        )
        excess = self.study.excess_returns()
        runner = self.study.runner(impact_cost)
        runner.returns = excess
        series: dict[str, pd.Series] = {}
        rows = {}
        group_weights = builder.groups(groups, holding_months, weighting)
        for number, weights in group_weights.items():
            run = runner.run(weights, 'none')
            name = f'P{number}'
            series[name] = self._cut(run['gross'], start)
            rows[name] = runner.score(series[name], True)
            rows[name]['ex_ante_beta'] = self._ex_ante(builder, weights, start)
        bab_weights, _ = builder.bab(holding_months)
        gross = runner.run(bab_weights, 'none')
        if universe == 'C':
            net = runner.run(
                bab_weights, 'futures', roll_impact=self.roll_impact
            )
        else:
            net = runner.run(bab_weights, 'delivery')
        series['BAB'] = self._cut(gross['gross'], start)
        rows['BAB'] = runner.score(series['BAB'], True)
        rows['BAB']['ex_ante_beta'] = 0.0
        short = -bab_weights.clip(upper=0).sum(axis=1)
        long = bab_weights.clip(lower=0).sum(axis=1)
        active = (long > 0) & (short > 0)
        fee = 0.0 if universe == 'C' else self.borrow_fee_annual
        drag = short * fee / 12.0
        after = net['net'] - drag.reindex(net.index).fillna(0.0)
        series['BAB after costs'] = self._cut(after, start)
        rows['BAB after costs'] = runner.score(series['BAB after costs'], True)
        rows['BAB']['long'] = float(long[active].mean())
        rows['BAB']['short'] = float(short[active].mean())
        rows['BAB']['turnover'] = float(gross['turnover'].mean())
        rows['BAB after costs']['borrow_fee'] = fee
        return pd.DataFrame(rows).T, series

    def _cut(self, series: pd.Series, start: str | None) -> pd.Series:
        """Drops months before a start month.

        Args:
            series (pd.Series): Monthly returns by month.
            start (str | None): The first month to keep, or None.

        Returns:
            pd.Series: The kept months.
        """
        if start is None:
            return series
        return series[series.index >= pd.Period(start, freq='M')]

    def _ex_ante(
        self,
        builder,
        weights: pd.DataFrame,
        start: str | None,
    ) -> float:
        """Averages a portfolio's weighted beta at formation.

        Args:
            builder: The portfolio builder holding the betas.
            weights (pd.DataFrame): The portfolio's weights by holding month.
            start (str | None): The first month to include.

        Returns:
            float: The mean over months of the weighted average beta.
        """
        betas = builder.betas.copy()
        betas.index = builder.holding_periods()
        weighted = (weights * betas.reindex_like(weights)).sum(axis=1)
        total = weights.sum(axis=1).replace(0.0, float('nan'))
        value = (weighted / total).dropna()
        return float(self._cut(value, start).mean())
