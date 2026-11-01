"""Runs target weights through the shared backtest engine and scores them."""

from typing import Any

import pandas as pd
from data_and_analytics.backtesting.backtest import Backtest
from data_and_analytics.backtesting.costs.delivery_costs import DeliveryCosts
from data_and_analytics.backtesting.costs.futures_costs import FuturesCosts
from data_and_analytics.backtesting.costs.no_costs import NoCosts
from data_and_analytics.backtesting.performance_report import (
    PerformanceReport,
)

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.factor_alphas import (
    FactorAlphas,
)


class StrategyRunner:
    """Backtests a weights table before and after Indian trading costs.

    Returns passed in are monthly simple returns by month. For a portfolio
    that holds shares with borrowed or margin-funded legs (the BAB factor,
    the futures long-short) the shares' excess returns are passed, so no
    separate cash return is needed; for a long-only portfolio the total
    returns are passed and the risk-free rate is taken off afterwards.

    Attributes:
        returns: Monthly returns of the shares by month.
        risk_free: The monthly risk-free return by month.
        alphas: The factor regressions.
        impact_cost: The assumed market impact per side.
        lags: Newey-West lags for every t-statistic.
    """

    def __init__(
        self,
        returns: pd.DataFrame,
        risk_free: pd.Series,
        alphas: FactorAlphas | None,
        impact_cost: float = 0.001,
        lags: int = 6,
    ) -> None:
        """Keeps the inputs.

        Args:
            returns (pd.DataFrame): Monthly returns, months by shares.
            risk_free (pd.Series): Monthly risk-free returns by month.
            alphas (FactorAlphas | None): The factor regressions, or None
                to skip alphas.
            impact_cost (float): Market impact per side, as a fraction.
            lags (int): Newey-West lags.

        Returns:
            None.
        """
        self.returns = returns
        self.risk_free = risk_free.reindex(returns.index)
        self.alphas = alphas
        self.impact_cost = impact_cost
        self.lags = lags

    def cost_model(self, kind: str):
        """Gives the cost model for a kind of trade.

        Args:
            kind (str): 'delivery', 'futures' or 'none'.

        Returns:
            CostModel: The engine's cost model.

        Raises:
            ValueError: The kind is unknown.
        """
        if kind == 'delivery':
            return DeliveryCosts(self.impact_cost)
        if kind == 'futures':
            return FuturesCosts(self.impact_cost)
        if kind == 'none':
            return NoCosts()
        raise ValueError(f'unknown cost kind: {kind}')

    def run(
        self,
        weights: pd.DataFrame,
        cost_kind: str,
        extra: pd.DataFrame | None = None,
        extra_weights: pd.DataFrame | None = None,
        roll_impact: float | None = None,
        overlay_roll_impact: float = 0.0002,
    ) -> pd.DataFrame:
        """Runs the portfolio.

        Args:
            weights (pd.DataFrame): Target weights by holding month.
            cost_kind (str): 'delivery', 'futures' or 'none' for the shares.
            extra (pd.DataFrame | None): Returns of a futures overlay
                (columns such as NIFTY), months by overlay.
            extra_weights (pd.DataFrame | None): The overlay's weights.
            roll_impact (float | None): Market impact per side of the
                monthly futures roll of the shares' positions, or None when
                the shares are not held through futures.
            overlay_roll_impact (float): Market impact per side of the
                overlay's monthly roll (NIFTY futures are very liquid).

        Returns:
            pd.DataFrame: Columns gross, net, cost, turnover and holdings by
                month, for the months with a position.
        """
        held = weights.columns[(weights != 0.0).any(axis=0)]
        columns = held.intersection(self.returns.columns)
        months = weights.index.intersection(self.returns.index)
        result = Backtest(
            self.returns.loc[months, columns],
            weights.loc[months, columns],
            self.cost_model(cost_kind),
        ).run()
        frame = pd.DataFrame(
            {
                'gross': result.gross_returns,
                'cost': result.costs,
                'turnover': result.turnover(),
                'holdings': result.holding_counts,
            }
        )
        if extra is not None and extra_weights is not None:
            overlay = Backtest(
                extra.loc[months],
                extra_weights.loc[months],
                self.cost_model('futures'),
            ).run()
            frame['gross'] = frame['gross'] + overlay.gross_returns.fillna(0.0)
            frame['cost'] = (
                frame['cost']
                + overlay.costs.fillna(0.0)
                + self.roll_cost(
                    extra_weights.loc[months],
                    overlay.turnover().fillna(0.0),
                    overlay_roll_impact,
                ).fillna(0.0)
            )
        if roll_impact is not None:
            frame['cost'] = frame['cost'] + self.roll_cost(
                weights.loc[months, columns], frame['turnover'], roll_impact
            )
        frame['net'] = frame['gross'] - frame['cost']
        return frame.dropna(subset=['gross'])

    def roll_cost(
        self,
        weights: pd.DataFrame,
        turnover: pd.Series,
        impact_cost: float,
    ) -> pd.Series:
        """Charges the monthly roll of futures positions that are kept.

        Stock and index futures expire every month, so a position held from
        one month to the next is closed and opened again. The part of the
        gross notional not already traded in the rebalance, gross notional
        minus turnover, pays a sell and a buy at the futures rates.

        Args:
            weights (pd.DataFrame): The futures weights by month.
            turnover (pd.Series): Bought plus sold by month.
            impact_cost (float): Market impact per side of the roll, lower
                than an outright trade because a roll is one calendar
                spread.

        Returns:
            pd.Series: The roll cost by month, as a fraction of capital.
        """
        model = FuturesCosts(impact_cost)
        gross = weights.abs().sum(axis=1)
        kept = (gross - turnover.reindex(gross.index).fillna(0.0)).clip(
            lower=0.0
        )
        return kept * (model.buy_rate() + model.sell_rate())

    def score(
        self,
        series: pd.Series,
        excess: bool,
        benchmark: pd.Series | None = None,
    ) -> dict[str, Any]:
        """Scores one return series.

        Args:
            series (pd.Series): Monthly returns by month.
            excess (bool): True if already in excess of the risk-free rate.
            benchmark (pd.Series | None): A benchmark's monthly total
                returns, used for the information about beating it.

        Returns:
            dict[str, Any]: months, mean excess return, Newey-West t, annual
                volatility, Sharpe, worst drawdown, CAPM, three- and
                four-factor alphas with t-statistics, and the compound
                annual return of the series.
        """
        series = series.dropna()
        excess_series = series if excess else series - self.risk_free
        excess_series = excess_series.dropna()
        report = PerformanceReport(excess_series, None, 12, self.lags).summary()
        output = {
            'months': report['periods'],
            'first': report['first_period'],
            'last': report['last_period'],
            'excess_mean': report['mean'],
            'newey_west_t': report['newey_west_t'],
            'volatility': report['volatility_annual'],
            'sharpe': report['sharpe'],
            'max_drawdown': report['maximum_drawdown'],
            'compound_annual': report['compound_annual'],
            'worst_month': report['worst_period'],
        }
        if self.alphas is not None:
            for model in FactorAlphas.MODELS:
                fit = self.alphas.fit(excess_series, model)
                output[f'{model}_alpha'] = fit['alpha']
                output[f'{model}_alpha_t'] = fit['alpha_t']
                output[f'{model}_beta_MF'] = fit['beta_MF']
        return output
