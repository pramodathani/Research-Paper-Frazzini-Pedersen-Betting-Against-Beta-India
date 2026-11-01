"""Runs the BAB factor and its long leg over a grid of settings."""

import itertools
from collections.abc import Iterable

import pandas as pd

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.bab_study import (
    BabStudy,
)


class GridRunner:
    """Scores every combination of universe, windows, shrinkage, K and weighting.

    For each combination it records the BAB factor before and after futures
    costs, and the BAB long leg held unlevered in delivery shares before and
    after delivery costs, with their monthly series, so a reader can score
    any sub-period or cost choice afterwards.

    Shrinkage w = 0 is left out: it sets every beta to 1, so the shares tie
    and nothing can be ranked. For any w above 0 the ranking is the raw
    beta's, and w only changes the leverage 1 / beta_L and 1 / beta_H.

    Attributes:
        study: The study's inputs.
        impacts: Market impact per side for each universe.
    """

    IMPACTS = {'A': 0.003, 'B': 0.001, 'C': 0.001}

    def __init__(self, study: BabStudy) -> None:
        """Keeps the study.

        Args:
            study (BabStudy): The study's inputs.

        Returns:
            None.
        """
        self.study = study

    def variant_count(
        self,
        universes: Iterable[str],
        volatility_months: Iterable[int],
        correlation_months: Iterable[int],
        shrinkages: Iterable[float],
        holdings: Iterable[int],
        weightings: Iterable[str],
    ) -> int:
        """Counts the variants in a grid.

        Args:
            universes (Iterable[str]): Universe names.
            volatility_months (Iterable[int]): Volatility windows.
            correlation_months (Iterable[int]): Correlation windows.
            shrinkages (Iterable[float]): Shrinkage weights.
            holdings (Iterable[int]): Holding periods K.
            weightings (Iterable[str]): Weightings.

        Returns:
            int: The number of combinations.
        """
        return len(
            list(
                itertools.product(
                    universes,
                    volatility_months,
                    correlation_months,
                    shrinkages,
                    holdings,
                    weightings,
                )
            )
        )

    def run(
        self,
        universes: Iterable[str] = ('A', 'B', 'C'),
        volatility_months: Iterable[int] = (6, 12, 24),
        correlation_months: Iterable[int] = (12, 36, 60),
        shrinkages: Iterable[float] = (0.4, 0.6, 0.8, 1.0),
        holdings: Iterable[int] = (1, 3, 6, 12),
        weightings: Iterable[str] = ('rank', 'equal'),
        progress: bool = False,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Runs the grid.

        Args:
            universes (Iterable[str]): Universe names.
            volatility_months (Iterable[int]): Volatility windows.
            correlation_months (Iterable[int]): Correlation windows.
            shrinkages (Iterable[float]): Shrinkage weights.
            holdings (Iterable[int]): Holding periods K.
            weightings (Iterable[str]): Weightings.
            progress (bool): Whether to print a line per variant.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]: A summary with one row per
                variant, and the monthly series (columns variant, month,
                bab_gross, bab_net, long_gross, long_net).
        """
        study = self.study
        rows = []
        series = []
        excess = study.excess_returns()
        number = 0
        for universe in universes:
            impact = self.IMPACTS[universe]
            bab_runner = study.runner(impact)
            bab_runner.returns = excess
            long_runner = study.runner(impact)
            for vol, corr, shrink in itertools.product(
                volatility_months, correlation_months, shrinkages
            ):
                builder = study.builder(universe, vol, corr, shrink)
                for holding, weighting in itertools.product(
                    holdings, weightings
                ):
                    number += 1
                    row, frame = self._one(
                        builder,
                        bab_runner,
                        long_runner,
                        holding,
                        weighting,
                    )
                    row.update(
                        {
                            'variant': number,
                            'universe': universe,
                            'volatility_months': vol,
                            'correlation_months': corr,
                            'shrinkage': shrink,
                            'holding_months': holding,
                            'weighting': weighting,
                        }
                    )
                    frame['variant'] = number
                    rows.append(row)
                    series.append(frame.reset_index(names='month'))
                    if progress:
                        print(
                            number,
                            universe,
                            vol,
                            corr,
                            shrink,
                            holding,
                            weighting,
                            flush=True,
                        )
        summary = pd.DataFrame(rows).set_index('variant')
        series_table = pd.concat(series, ignore_index=True)
        series_table['month'] = series_table['month'].astype(str)
        return summary, series_table

    def _one(
        self,
        builder,
        bab_runner,
        long_runner,
        holding: int,
        weighting: str,
    ) -> tuple[dict, pd.DataFrame]:
        """Runs one variant.

        Args:
            builder: The portfolio builder for the beta setting.
            bab_runner: The runner over excess returns.
            long_runner: The runner over total returns.
            holding (int): K.
            weighting (str): 'rank' or 'equal'.

        Returns:
            tuple[dict, pd.DataFrame]: The variant's statistics and its
                monthly series.
        """
        bab_weights, _ = builder.bab(holding, weighting)
        if not (bab_weights != 0.0).any(axis=None):
            return {}, pd.DataFrame(
                columns=['bab_gross', 'bab_net', 'long_gross', 'long_net']
            )
        gross = bab_runner.run(bab_weights, 'none')
        net = bab_runner.run(bab_weights, 'futures')
        long_weights, _ = builder.low_beta_half(holding, weighting)
        long_run = long_runner.run(long_weights, 'delivery')
        frame = pd.DataFrame(
            {
                'bab_gross': gross['gross'],
                'bab_net': net['net'],
                'long_gross': long_run['gross'],
                'long_net': long_run['net'],
            }
        )
        row = {}
        score = bab_runner.score(gross['gross'], True)
        for key in (
            'months',
            'excess_mean',
            'newey_west_t',
            'volatility',
            'sharpe',
            'max_drawdown',
            'capm_alpha',
            'capm_alpha_t',
            'carhart_alpha',
            'carhart_alpha_t',
        ):
            row[f'bab_{key}'] = score.get(key)
        net_score = bab_runner.score(net['net'], True)
        row['bab_net_mean'] = net_score['excess_mean']
        row['bab_net_sharpe'] = net_score['sharpe']
        row['bab_turnover'] = float(gross['turnover'].mean())
        long_score = long_runner.score(long_run['gross'], False)
        row['long_excess_mean'] = long_score['excess_mean']
        row['long_sharpe'] = long_score['sharpe']
        row['long_volatility'] = long_score['volatility']
        row['long_max_drawdown'] = long_score['max_drawdown']
        long_net_score = long_runner.score(long_run['net'], False)
        row['long_net_mean'] = long_net_score['excess_mean']
        row['long_net_sharpe'] = long_net_score['sharpe']
        return row, frame
