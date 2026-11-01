"""Calendar-year, sub-period, size and beta-window tables, and beta compression."""

import numpy as np
import pandas as pd
import statsmodels.api as sm

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.bab_study import (
    BabStudy,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.portfolio_builder import (
    PortfolioBuilder,
)


class ExtraTables:
    """Tables that look at the BAB factor from other sides.

    Attributes:
        study: The study's inputs.
        lags: Newey-West lags for every t-statistic.
    """

    def __init__(self, study: BabStudy, lags: int = 6) -> None:
        """Keeps the study.

        Args:
            study (BabStudy): The study's inputs.
            lags (int): Newey-West lags.

        Returns:
            None.
        """
        self.study = study
        self.lags = lags

    def bab_series(
        self,
        universe: str = 'A',
        volatility_months: int = 12,
        correlation_months: int = 60,
        shrinkage: float = 0.6,
        horizon_days: int = 3,
        holding_months: int = 1,
        eligible: pd.DataFrame | None = None,
    ) -> pd.Series:
        """Gives the BAB factor's monthly excess return before costs.

        Args:
            universe (str): 'A', 'B' or 'C'.
            volatility_months (int): Months for the volatilities.
            correlation_months (int): Months for the correlation.
            shrinkage (float): The weight on the raw beta.
            horizon_days (int): Days in each correlation return.
            holding_months (int): K.
            eligible (pd.DataFrame | None): A replacement universe table.

        Returns:
            pd.Series: Returns by month.
        """
        study = self.study
        builder = study.builder(
            universe,
            volatility_months,
            correlation_months,
            shrinkage,
            horizon_days,
        )
        if eligible is not None:
            builder = PortfolioBuilder(
                builder.betas, eligible, study.median_value
            )
        weights, _ = builder.bab(holding_months)
        runner = study.runner(0.0)
        runner.returns = study.excess_returns()
        return runner.run(weights, 'none')['gross']

    def calendar_years(self, universe: str = 'A') -> pd.DataFrame:
        """Compounds the BAB factor and the Indian factors by calendar year.

        Args:
            universe (str): The universe of the BAB factor.

        Returns:
            pd.DataFrame: One row per year with columns BAB, MKT, SMB, HML
                and WML as decimal returns; the factor columns are NaN after
                IIMA's last month.
        """
        bab = self.bab_series(universe)
        table = pd.concat(
            [
                bab.rename('BAB'),
                self.study.factors[['MF', 'SMB', 'HML', 'WML']].rename(
                    columns={'MF': 'MKT'}
                ),
            ],
            axis=1,
        ).loc[bab.index.min() :]
        years = table.index.year
        compounded = (1.0 + table).groupby(years).prod(min_count=1) - 1.0
        counts = table.groupby(years).count()
        return compounded.where(counts == 12) if False else compounded

    def sub_periods(
        self,
        series: pd.Series,
        edges: tuple[str, ...] = ('2000-01', '2006-01', '2013-01', '2020-01'),
    ) -> pd.DataFrame:
        """Scores a series in consecutive sub-periods.

        Args:
            series (pd.Series): Monthly excess returns by month.
            edges (tuple[str, ...]): The first month of each sub-period.

        Returns:
            pd.DataFrame: One row per sub-period.
        """
        runner = self.study.runner(0.0)
        bounds = [pd.Period(e, freq='M') for e in edges]
        ends = [*bounds[1:], series.index.max() + 1]
        rows = {}
        for start, end in zip(bounds, ends):
            part = series[(series.index >= start) & (series.index < end)]
            if len(part) < 12:
                continue
            label = f'{start.year}-{(end - 1).year}'
            rows[label] = runner.score(part, True)
        return pd.DataFrame(rows).T

    def beta_windows(
        self,
        universe: str = 'A',
        volatility_months: tuple[int, ...] = (6, 12, 24),
        correlation_months: tuple[int, ...] = (12, 36, 60),
        horizons: tuple[int, ...] = (3, 1),
    ) -> pd.DataFrame:
        """Scores the BAB factor for every beta window setting.

        Args:
            universe (str): The universe.
            volatility_months (tuple[int, ...]): Volatility windows.
            correlation_months (tuple[int, ...]): Correlation windows.
            horizons (tuple[int, ...]): Days per correlation return.

        Returns:
            pd.DataFrame: One row per setting, scored over the months that
                every setting has.
        """
        runner = self.study.runner(0.0)
        series = {}
        for horizon in horizons:
            for vol in volatility_months:
                for corr in correlation_months:
                    series[(vol, corr, horizon)] = self.bab_series(
                        universe, vol, corr, 0.6, horizon
                    )
        common = pd.concat(series.values(), axis=1).dropna().index
        rows = {}
        for key, values in series.items():
            score = runner.score(values.loc[common], True)
            label = f'vol {key[0]}m, corr {key[1]}m, {key[2]}-day'
            rows[label] = score
        return pd.DataFrame(rows).T

    def size_terciles(self, universe: str = 'A') -> pd.DataFrame:
        """Scores BAB within terciles of median traded value.

        Args:
            universe (str): The universe the terciles are cut from.

        Returns:
            pd.DataFrame: One row per tercile, 1 being the least traded.
        """
        study = self.study
        base = study.universes[universe]
        value = study.median_value.where(base)
        ranks = value.rank(axis=1, pct=True)
        runner = study.runner(0.0)
        rows = {}
        for number, (low, high) in enumerate(
            ((0.0, 1 / 3), (1 / 3, 2 / 3), (2 / 3, 1.0)), start=1
        ):
            inside = (ranks > low) & (ranks <= high)
            series = self.bab_series(universe, eligible=inside & base)
            rows[f'tercile {number}'] = runner.score(series, True)
        return pd.DataFrame(rows).T

    def beta_compression(
        self,
        stress: pd.Series,
        universe: str = 'A',
        minimum_history: int = 60,
    ) -> pd.DataFrame:
        """Tests whether betas compress towards one in stressed months.

        Each month's stress is placed in a tercile of the stress seen so far
        (an expanding window, so nothing later is used). For each tercile the
        table gives the mean cross-sectional standard deviation of betas and
        the BAB factor's market beta in those months.

        Args:
            stress (pd.Series): A stress measure by month, such as India VIX.
            universe (str): The universe.
            minimum_history (int): Months of stress before terciles start.

        Returns:
            pd.DataFrame: Rows low, middle, high and high minus low, with
                columns dispersion, dispersion_t, bab_beta, bab_beta_t and
                months.
        """
        study = self.study
        builder = study.builder(universe)
        betas = builder.betas.copy()
        betas.index = builder.holding_periods()
        dispersion = betas.std(axis=1).dropna()
        stress = stress.reindex(dispersion.index).dropna()
        lower = stress.expanding(minimum_history).quantile(1 / 3).shift(1)
        upper = stress.expanding(minimum_history).quantile(2 / 3).shift(1)
        regime = pd.Series(np.nan, index=stress.index)
        regime[stress <= lower] = 0
        regime[(stress > lower) & (stress <= upper)] = 1
        regime[stress > upper] = 2
        bab = self.bab_series(universe)
        market = study.market - study.risk_free
        rows = {}
        names = ['low', 'middle', 'high']
        for number, name in enumerate(names):
            months = regime.index[regime == number]
            rows[name] = self._regime_row(dispersion, bab, market, months)
        table = pd.DataFrame(rows).T
        gap = self._dispersion_gap(dispersion, regime)
        table.loc['high minus low', 'dispersion'] = gap[0]
        table.loc['high minus low', 'dispersion_t'] = gap[1]
        table.loc['high minus low', 'bab_beta'] = (
            table.loc['high', 'bab_beta'] - table.loc['low', 'bab_beta']
        )
        return table

    def _regime_row(self, dispersion, bab, market, months) -> dict:
        """Summarises the months in one stress regime.

        Args:
            dispersion (pd.Series): Beta dispersion by month.
            bab (pd.Series): BAB returns by month.
            market (pd.Series): Market excess returns by month.
            months: The months in the regime.

        Returns:
            dict: Dispersion, BAB's market beta and t, and the month count.
        """
        row = {
            'dispersion': float(dispersion.reindex(months).mean()),
            'months': len(months),
            'dispersion_t': np.nan,
            'bab_beta': np.nan,
            'bab_beta_t': np.nan,
        }
        joined = pd.concat(
            [
                bab.reindex(months).rename('y'),
                market.reindex(months).rename('x'),
            ],
            axis=1,
        ).dropna()
        if len(joined) >= 12:
            fit = sm.OLS(joined['y'], sm.add_constant(joined['x'])).fit(
                cov_type='HAC', cov_kwds={'maxlags': self.lags}
            )
            row['bab_beta'] = float(fit.params['x'])
            row['bab_beta_t'] = float(fit.tvalues['x'])
        return row

    def _dispersion_gap(
        self,
        dispersion: pd.Series,
        regime: pd.Series,
    ) -> tuple[float, float]:
        """Tests dispersion in high-stress months against low-stress ones.

        Args:
            dispersion (pd.Series): Beta dispersion by month.
            regime (pd.Series): 0, 1 or 2 by month, NaN before terciles.

        Returns:
            tuple[float, float]: The difference and its Newey-West t.
        """
        joined = pd.concat(
            [dispersion.rename('d'), regime.rename('r')], axis=1
        ).dropna()
        joined = joined[joined['r'].isin([0, 2])]
        if len(joined) < 12:
            return float('nan'), float('nan')
        design = sm.add_constant((joined['r'] == 2).astype(float))
        fit = sm.OLS(joined['d'], design).fit(
            cov_type='HAC', cov_kwds={'maxlags': self.lags}
        )
        name = design.columns[1]
        return float(fit.params[name]), float(fit.tvalues[name])
