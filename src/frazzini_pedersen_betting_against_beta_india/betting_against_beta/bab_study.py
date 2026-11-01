"""The whole study's inputs, built once: panel, universes, betas, returns."""

from pathlib import Path

import pandas as pd

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.beta_tables import (
    BetaTables,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.factor_alphas import (
    FactorAlphas,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.market_data import (
    MarketData,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.portfolio_builder import (
    PortfolioBuilder,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.return_panel import (
    ReturnPanel,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.strategy_runner import (
    StrategyRunner,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.universes import (
    Universes,
)


class BabStudy:
    """Holds everything the portfolios need and builds them on request.

    Attributes:
        panel: The daily return panel.
        dates: Formation days, the month ends from the first date with
            enough history.
        universes: Boolean tables for A, B and C.
        betas: The beta tables.
        monthly: Monthly simple returns by month.
        risk_free: Monthly risk-free returns by month.
        market: The market's monthly simple returns by month.
        median_value: Median daily traded value over the past year.
        factors: The IIMA factors by month.
    """

    def __init__(
        self,
        data: Path,
        derived: Path,
        first_formation: str = '1998-12-01',
    ) -> None:
        """Builds the panel, universes and monthly returns.

        Args:
            data (Path): The study's data folder.
            derived (Path): The folder with the derived tables.
            first_formation (str): The earliest formation day to consider.

        Returns:
            None.
        """
        self.panel = ReturnPanel.from_files(data, derived)
        ends = self.panel.month_ends()
        self.dates = ends[ends >= pd.Timestamp(first_formation)]
        futures_path = Path(derived) / 'fno_members.parquet'
        futures = (
            pd.read_parquet(futures_path) if futures_path.exists() else None
        )
        builder = Universes(self.panel)
        self.universes = builder.build(self.dates, futures)
        self.median_value = builder.median_traded_value(self.dates)
        self.betas = BetaTables(self.panel, self.dates)
        self.monthly = self.panel.monthly_returns()
        self.risk_free = self.panel.risk_free_monthly.reindex(
            self.monthly.index
        ).ffill()
        self.market = self.panel.monthly_market()
        self.factors = MarketData(data).iima_factors()

    def builder(
        self,
        universe: str = 'A',
        volatility_months: int = 12,
        correlation_months: int = 60,
        shrinkage: float = 0.6,
        horizon_days: int = 3,
    ) -> PortfolioBuilder:
        """Gives a portfolio builder for one beta setting and universe.

        Args:
            universe (str): 'A', 'B' or 'C'.
            volatility_months (int): Months for the volatilities.
            correlation_months (int): Months for the correlation.
            shrinkage (float): The weight on the raw beta.
            horizon_days (int): Days in each correlation return.

        Returns:
            PortfolioBuilder: The builder.
        """
        betas = self.betas.beta(
            volatility_months, correlation_months, shrinkage, horizon_days
        )
        return PortfolioBuilder(
            betas, self.universes[universe], self.median_value
        )

    def runner(self, impact_cost: float = 0.001) -> StrategyRunner:
        """Gives a runner over the monthly returns.

        Args:
            impact_cost (float): Market impact per side.

        Returns:
            StrategyRunner: The runner, set up to score with factor alphas.
        """
        return StrategyRunner(
            self.monthly,
            self.risk_free,
            FactorAlphas(self.factors),
            impact_cost,
        )

    def excess_returns(self) -> pd.DataFrame:
        """Gives the shares' monthly excess returns.

        Returns:
            pd.DataFrame: Monthly simple returns minus the risk-free return.
        """
        return self.monthly.sub(self.risk_free, axis=0)
