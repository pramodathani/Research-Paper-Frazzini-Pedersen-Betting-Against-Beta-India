"""The portfolios that can be traded in India: futures long-short and long-only."""

import pandas as pd

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.bab_study import (
    BabStudy,
)


class TradeablePortfolios:
    """Builds and scores T1, T2 and L1 to L3 from the plan.

    T1 is the BAB factor in the F&O universe, held through stock futures.
    T2 is the lowest against the highest beta quintile there. L1 holds the
    lowest-beta fifth of the liquid 500, L2 the rank-weighted low-beta half
    of the liquid 500, and L3 is L1 plus a NIFTY futures overlay that lifts
    its beta to about one. Futures legs are charged futures costs and are
    taken to earn their share's excess return, which is the paper's own
    treatment of leverage; long-only legs pay delivery costs and earn total
    returns.

    Attributes:
        study: The study's inputs.
        market_name: The overlay's column name.
        maximum_overlay: The most overlay notional allowed, as a multiple of
            capital.
    """

    market_name = 'NIFTY'

    def __init__(self, study: BabStudy, maximum_overlay: float = 1.5) -> None:
        """Keeps the study.

        Args:
            study (BabStudy): The study's inputs.
            maximum_overlay (float): Cap on the overlay's notional.

        Returns:
            None.
        """
        self.study = study
        self.maximum_overlay = maximum_overlay

    def run_all(
        self,
        volatility_months: int = 12,
        correlation_months: int = 60,
        shrinkage: float = 0.6,
        holding_months: int = 1,
        long_fraction: float = 0.2,
        impact_liquid: float = 0.001,
        impact_futures: float = 0.001,
        roll_impact: float = 0.0005,
    ) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
        """Runs all five portfolios.

        Args:
            volatility_months (int): Months for the volatilities.
            correlation_months (int): Months for the correlation.
            shrinkage (float): The weight on the raw beta.
            holding_months (int): K, the months a cohort is held.
            long_fraction (float): The share of the liquid 500 in L1.
            impact_liquid (float): Market impact per side for the long-only
                portfolios.
            impact_futures (float): Market impact per side for futures legs.
            roll_impact (float): Market impact per side of the monthly roll
                of the stock futures in T1 and T2.

        Returns:
            tuple[pd.DataFrame, dict[str, pd.DataFrame]]: A summary table
                with a before-cost and an after-cost row for each portfolio,
                and each portfolio's monthly run (gross, cost, net,
                turnover, holdings).
        """
        study = self.study
        runs: dict[str, pd.DataFrame] = {}
        excess_runner = study.runner(impact_futures)
        excess_runner.returns = study.excess_returns()
        total_runner = study.runner(impact_liquid)
        futures = study.builder(
            'C', volatility_months, correlation_months, shrinkage
        )
        liquid = study.builder(
            'B', volatility_months, correlation_months, shrinkage
        )
        weights, _ = futures.bab(holding_months)
        runs['T1'] = excess_runner.run(
            weights, 'futures', roll_impact=roll_impact
        )
        weights, _ = futures.quintile_spread(holding_months)
        runs['T2'] = excess_runner.run(
            weights, 'futures', roll_impact=roll_impact
        )
        weights, _ = liquid.lowest_beta(long_fraction, holding_months)
        runs['L1'] = total_runner.run(weights, 'delivery')
        weights2, _ = liquid.low_beta_half(holding_months)
        runs['L2'] = total_runner.run(weights2, 'delivery')
        weights3, betas = liquid.lowest_beta(long_fraction, holding_months)
        overlay_weight = (1.0 / betas - 1.0).clip(
            lower=0.0, upper=self.maximum_overlay
        )
        overlay_weight = overlay_weight.fillna(0.0)
        market_excess = study.market - study.risk_free
        extra = pd.DataFrame({self.market_name: market_excess})
        extra_weights = pd.DataFrame({self.market_name: overlay_weight})
        runs['L3'] = total_runner.run(
            weights3, 'delivery', extra, extra_weights.reindex(extra.index)
        )
        rows = {}
        for name, run in runs.items():
            excess = name in ('T1', 'T2')
            runner = excess_runner if excess else total_runner
            for label, column in (
                ('before costs', 'gross'),
                ('after costs', 'net'),
            ):
                row = runner.score(run[column], excess)
                row['turnover'] = float(run['turnover'].mean())
                row['holdings'] = float(run['holdings'].mean())
                rows[f'{name} {label}'] = row
        return pd.DataFrame(rows).T, runs

    def benchmarks(self) -> dict[str, pd.Series]:
        """Gives the benchmark's monthly total returns.

        Returns:
            dict[str, pd.Series]: The market index's monthly returns, by
                name.
        """
        return {'NIFTY 500 TRI': self.study.market}
