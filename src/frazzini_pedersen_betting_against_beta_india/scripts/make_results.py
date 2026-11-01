"""Command-line program that runs every table of the study and saves it."""

import argparse
import json
import warnings
from pathlib import Path

import pandas as pd

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.bab_study import (
    BabStudy,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.decile_table import (
    DecileTable,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.delisting_stress import (
    DelistingStress,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.extra_tables import (
    ExtraTables,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.market_data import (
    MarketData,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.tradeable_portfolios import (
    TradeablePortfolios,
)

BORROW_BASE = 0.0325
IMPACT = {'A': 0.003, 'B': 0.001, 'C': 0.001}


class MakeResultsApplication:
    """Runs the tables and writes them as csv files in the results folder."""

    def run(self) -> None:
        """Runs every table.

        Returns:
            None.
        """
        warnings.simplefilter('ignore')
        parser = argparse.ArgumentParser()
        parser.add_argument('--data', default='data')
        parser.add_argument('--derived', default='data/derived')
        parser.add_argument('--out', default='results')
        arguments = parser.parse_args()
        self.out = Path(arguments.out)
        self.out.mkdir(parents=True, exist_ok=True)
        self.data = Path(arguments.data)
        study = BabStudy.from_files(self.data, Path(arguments.derived))
        self.study = study
        self.deciles(study)
        self.extra(study)
        self.tradeable(study)
        self.stress(study)
        self.ubi_check(study)

    def save(self, table: pd.DataFrame, name: str) -> None:
        """Saves and prints a table.

        Args:
            table (pd.DataFrame): The table.
            name (str): The file stem.

        Returns:
            None.
        """
        table.to_csv(self.out / f'{name}.csv')
        print(f'saved {name} ({len(table)} rows)', flush=True)

    def deciles(self, study: BabStudy) -> None:
        """Runs the decile tables and the borrow-fee sensitivity.

        Args:
            study (BabStudy): The study.

        Returns:
            None.
        """
        summary = {}
        for universe, weighting in (
            ('A', 'equal'),
            ('A', 'value'),
            ('B', 'equal'),
            ('B', 'value'),
            ('C', 'equal'),
        ):
            table, series = DecileTable(study, BORROW_BASE).run(
                universe, weighting, impact_cost=IMPACT[universe]
            )
            self.save(table, f'deciles_{universe}_{weighting}')
            if weighting == 'equal':
                frame = pd.DataFrame(series)
                frame.index = frame.index.astype(str)
                self.save(frame, f'monthly_series_{universe}')
                summary[universe] = table.loc[['BAB', 'BAB after costs']].copy()
        self.save(pd.concat(summary, names=['universe']), 'bab_summary')
        rows = {}
        for fee in (0.0, BORROW_BASE, 0.10):
            for universe in ('A', 'B', 'C'):
                table, _ = DecileTable(study, fee).run(
                    universe, 'equal', impact_cost=IMPACT[universe]
                )
                rows[f'{universe} fee {fee:.2%}'] = table.loc['BAB after costs']
        self.save(pd.DataFrame(rows).T, 'borrow_sensitivity')

    def extra(self, study: BabStudy) -> None:
        """Runs the calendar-year, window, size, sub-period and stress tables.

        Args:
            study (BabStudy): The study.

        Returns:
            None.
        """
        tables = ExtraTables(study)
        years = tables.calendar_years('A')
        years.index = years.index.astype(str)
        self.save(years, 'calendar_years_A')
        self.save(tables.beta_windows('A'), 'beta_windows_A')
        self.save(tables.beta_windows('B'), 'beta_windows_B')
        self.save(tables.size_terciles('A'), 'size_terciles_A')
        self.save(tables.size_terciles('B'), 'size_terciles_B')
        for universe in ('A', 'B', 'C'):
            series = tables.bab_series(universe)
            edges = ('2000-01', '2006-01', '2013-01', '2020-01')
            if universe == 'C':
                edges = ('2005-01', '2010-01', '2015-01', '2020-01')
            self.save(
                tables.sub_periods(series, edges), f'sub_periods_{universe}'
            )
        self.save(
            tables.beta_compression(tables.realised_market_stress()),
            'compression_realised_vol',
        )
        closes = pd.read_parquet(Path('data/derived/index_closes.parquet'))
        vix = closes[closes['index_name'].str.lower() == 'india vix']
        vix = vix.set_index('date')['close']
        self.save(
            tables.beta_compression(tables.vix_stress(vix), minimum_history=36),
            'compression_india_vix',
        )

    def tradeable(self, study: BabStudy) -> None:
        """Runs T1, T2, L1 to L3 and the benchmarks.

        Args:
            study (BabStudy): The study.

        Returns:
            None.
        """
        portfolios = TradeablePortfolios(study)
        table, runs = portfolios.run_all()
        self.save(table, 'tradeable')
        frame = pd.concat(
            {name: run[['gross', 'net']] for name, run in runs.items()},
            axis=1,
        )
        frame.columns = ['_'.join(c) for c in frame.columns]
        frame.index = frame.index.astype(str)
        self.save(frame, 'tradeable_monthly')
        loader = MarketData(self.data)
        runner = study.runner(0.0)
        rows = {}
        monthly = {}
        for label, name in (
            ('NIFTY 500 TRI', 'NIFTY_500'),
            ('NIFTY 50 TRI', 'NIFTY_50'),
            ('NIFTY Low Volatility 50 TRI', 'NIFTY_LOW_VOLATILITY_50'),
            ('NIFTY100 Low Volatility 30 TRI', 'NIFTY100_LOW_VOLATILITY_30'),
        ):
            level = loader.total_return_index(name)
            ends = level.groupby(level.index.to_period('M')).last()
            returns = ends.pct_change().dropna()
            monthly[label] = returns
            rows[label] = runner.score(returns, False)
        self.save(pd.DataFrame(rows).T, 'benchmarks')
        bench = pd.DataFrame(monthly)
        bench.index = bench.index.astype(str)
        self.save(bench, 'benchmarks_monthly')
        common = {}
        for name, run in runs.items():
            excess = name in ('T1', 'T2')
            start = pd.Period('2006-01', freq='M')
            series = run['net'][run['net'].index >= start]
            common[f'{name} after costs, 2006 on'] = runner.score(
                series, excess
            )
        for label, returns in monthly.items():
            series = returns[returns.index >= pd.Period('2006-01', freq='M')]
            common[f'{label}, 2006 on'] = runner.score(series, False)
        self.save(pd.DataFrame(common).T, 'tradeable_vs_benchmarks_2006')

    def stress(self, study: BabStudy) -> None:
        """Runs the delisting stress.

        Args:
            study (BabStudy): The study.

        Returns:
            None.
        """
        stress = DelistingStress(study.panel)
        gone = stress.vanished()
        self.save(
            gone.assign(last_date=gone['last_date'].astype(str)),
            'vanished_shares',
        )
        original = study.monthly
        rows = {}
        try:
            for shock in (0.0, -0.3, -1.0):
                study.monthly = (
                    original if shock == 0.0 else stress.monthly_returns(shock)
                )
                table, _ = DecileTable(study, BORROW_BASE).run(
                    'A', 'equal', impact_cost=IMPACT['A']
                )
                rows[f'BAB A, shock {shock:.0%}'] = table.loc['BAB']
                rows[f'BAB A after costs, shock {shock:.0%}'] = table.loc[
                    'BAB after costs'
                ]
                tradeable, _ = TradeablePortfolios(study).run_all()
                for name in ('T1', 'L1'):
                    rows[f'{name} after costs, shock {shock:.0%}'] = (
                        tradeable.loc[f'{name} after costs']
                    )
        finally:
            study.monthly = original
        self.save(pd.DataFrame(rows).T, 'delisting_stress')

    def ubi_check(self, study: BabStudy) -> None:
        """Compares our monthly price returns with UBI's for liquid shares.

        Args:
            study (BabStudy): The study.

        Returns:
            None.
        """
        path = self.data / 'ubi/prices_nse_equities_day_adjusted.parquet'
        prices = pd.read_parquet(path)
        date_column = 'date' if 'date' in prices.columns else prices.columns[0]
        prices[date_column] = pd.to_datetime(prices[date_column])
        wide = prices.pivot_table(
            index=date_column, columns='symbol', values='close', aggfunc='last'
        )
        ends = wide.groupby(wide.index.to_period('M')).last()
        ubi = ends.pct_change()
        ours = study.monthly
        common = ubi.columns.intersection(ours.columns)
        months = ubi.index.intersection(ours.index)
        months = months[months >= pd.Period('2020-02', freq='M')]
        difference = (
            ours.loc[months, common] - ubi.loc[months, common]
        ).stack()
        difference = difference.dropna()
        liquid = study.universes['B']
        liquid.index = liquid.index.to_period('M') + 1
        mask = liquid.reindex(index=months, columns=common).stack()
        mask = mask.reindex(difference.index).fillna(False).astype(bool)
        report = {}
        for label, values in (
            ('all shares in both', difference),
            ('liquid 500 only', difference[mask]),
        ):
            report[label] = {
                'share_months': len(values),
                'median_abs_difference': float(values.abs().median()),
                'within_1pct': float((values.abs() < 0.01).mean()),
                'within_3pct': float((values.abs() < 0.03).mean()),
                'beyond_10pct': float((values.abs() > 0.10).mean()),
            }
        self.save(pd.DataFrame(report).T, 'ubi_crosscheck')
        (self.out / 'run_info.json').write_text(
            json.dumps(
                {
                    'first_formation': str(study.dates[0].date()),
                    'last_formation': str(study.dates[-1].date()),
                    'borrow_fee_base': BORROW_BASE,
                }
            )
        )


if __name__ == '__main__':
    MakeResultsApplication().run()
