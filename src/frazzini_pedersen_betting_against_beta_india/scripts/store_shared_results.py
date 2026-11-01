"""Command-line program that writes the study's returns and findings to the shared databases."""

import datetime
import os
from pathlib import Path
from urllib import parse

import chromadb
import pandas as pd
import psycopg
import pymongo

PROJECT = 'betting-against-beta-research-paper'
PAPER = 'Frazzini and Pedersen (2014), Betting Against Beta'

FINDINGS = [
    (
        'bab-strong-before-costs',
        'result',
        'BAB earns 0.78% a month on all NSE shares before costs',
        'With the paper settings (1-year volatility, 5-year 3-day correlation, shrink 0.6), the BAB factor over all NSE shares earns 0.78% a month, Newey-West t 3.60, Sharpe 0.77, 331 months 1999-04 to 2026-10. The US figure is 0.70% with Sharpe 0.78. Alphas fall from the lowest to the highest beta decile.',
        ['results/deciles_A_equal.csv', 'results/bab_summary.csv'],
    ),
    (
        'bab-driven-by-illiquid-shares',
        'difference from the paper',
        'Indian BAB comes mostly from thinly traded shares',
        'BAB earns 1.02% a month in the least-traded third of NSE shares but 0.45% in the most-traded third; 0.47% (t 2.02) in the liquid 500 and 0.39% (t 1.59) in F&O shares.',
        ['results/size_terciles_A.csv', 'results/bab_summary.csv'],
    ),
    (
        'long-short-fails-after-costs',
        'result',
        'Long-short BAB does not survive Indian trading costs',
        'Through stock futures in the F&O universe, BAB falls from 0.39% to -0.02% a month after futures costs and a monthly roll at 0.05% impact. As cash portfolios with a 3.25% SLB fee, all-NSE BAB keeps 0.40% (t 1.82) and liquid-500 BAB 0.18% (t 0.78), but few shares can be borrowed.',
        [
            'results/tradeable.csv',
            'results/roll_sensitivity.csv',
            'results/borrow_sensitivity.csv',
        ],
    ),
    (
        'long-only-low-beta-is-low-risk',
        'result',
        'Long-only low-beta shares give market returns with less risk',
        'The lowest-beta 20% of the liquid 500 (L1) earns 0.81% a month after costs against the NIFTY 500 TRI 0.86% over the same months, with 21% volatility against 24%, beta 0.77 and Sharpe 0.46 against 0.43. NSE low-volatility indices did better from 2006 (Sharpe 0.52 to 0.53).',
        ['results/tradeable_vs_benchmarks.csv'],
    ),
    (
        'engine-no-futures-roll',
        'data problem',
        'The shared backtest engine never charges the futures roll',
        'Futures positions roll monthly, but the engine charges only rebalancing trades. The study adds (gross notional - turnover) x (buy + sell rate) per month (gap 35).',
        [
            'src/frazzini_pedersen_betting_against_beta_india/betting_against_beta/strategy_runner.py'
        ],
    ),
    (
        'slb-fee-median',
        'data problem',
        'Annualised SLB lending fees: median 3.3%, value-weighted 36%',
        'From NSE SLB bhavcopies on month-end days 2010-2026 (10,823 contracts), the annualised fee is median 3.25% a year, but the value-weighted mean is 36% because hard-to-borrow names dominate trading. Only a few hundred shares trade in SLB.',
        ['results/borrow_fee_by_year.csv'],
    ),
]


class StoreSharedResultsApplication:
    """Upserts monthly strategy returns and findings."""

    def run(self) -> None:
        """Writes everything.

        Returns:
            None.
        """
        results = Path('results')
        rows = []
        bench = pd.read_csv(results / 'benchmarks_monthly.csv', index_col=0)[
            'NIFTY 500 TRI'
        ]
        for universe in ('A', 'B', 'C'):
            frame = pd.read_csv(
                results / f'monthly_series_{universe}.csv', index_col=0
            )
            for month, row in frame.iterrows():
                rows.append(
                    (
                        month,
                        'BAB factor',
                        universe,
                        row['BAB'],
                        row['BAB after costs'],
                    )
                )
        tradeable = pd.read_csv(results / 'tradeable_monthly.csv', index_col=0)
        universes = {'T1': 'C', 'T2': 'C', 'L1': 'B', 'L2': 'B', 'L3': 'B'}
        for month, row in tradeable.iterrows():
            for name, universe in universes.items():
                if pd.isna(row[f'{name}_gross']):
                    continue
                rows.append(
                    (
                        month,
                        name,
                        universe,
                        row[f'{name}_gross'],
                        row[f'{name}_net'],
                    )
                )
        self._returns(rows, bench)
        self._findings()

    def _returns(self, rows, bench) -> None:
        """Upserts the monthly returns.

        Args:
            rows: Tuples of month, strategy, universe, before and after costs.
            bench: The NIFTY 500 TRI monthly return by month.

        Returns:
            None.
        """
        with psycopg.connect(
            os.environ['RESEARCH_ANALYST_TIMESCALEDB_URL']
        ) as connection:
            connection.execute('CREATE SCHEMA IF NOT EXISTS results')
            connection.execute(
                'CREATE TABLE IF NOT EXISTS results.strategy_returns ('
                'month date NOT NULL, project text NOT NULL, strategy text NOT NULL, '
                'universe text NOT NULL, return_before_costs double precision, '
                'return_after_costs double precision, benchmark_return double precision, '
                'updated_at timestamptz NOT NULL DEFAULT now(), '
                'PRIMARY KEY (project, strategy, universe, month))'
            )
            connection.execute(
                "SELECT create_hypertable('results.strategy_returns', "
                "by_range('month'), if_not_exists => TRUE)"
            )
            with connection.cursor() as cursor:
                cursor.executemany(
                    'INSERT INTO results.strategy_returns (month, project, strategy, '
                    'universe, return_before_costs, return_after_costs, benchmark_return) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s) '
                    'ON CONFLICT (project, strategy, universe, month) DO UPDATE SET '
                    'return_before_costs = EXCLUDED.return_before_costs, '
                    'return_after_costs = EXCLUDED.return_after_costs, '
                    'benchmark_return = EXCLUDED.benchmark_return, updated_at = now()',
                    [
                        (
                            pd.Period(month, freq='M').start_time.date(),
                            PROJECT,
                            strategy,
                            universe,
                            None if pd.isna(gross) else float(gross),
                            None if pd.isna(net) else float(net),
                            None
                            if pd.isna(bench.get(month))
                            else float(bench.get(month)),
                        )
                        for month, strategy, universe, gross, net in rows
                    ],
                )
        print(f'{len(rows)} monthly returns stored')

    def _findings(self) -> None:
        """Upserts the findings in MongoDB and ChromaDB.

        Returns:
            None.
        """
        client = pymongo.MongoClient(os.environ['RESEARCH_ANALYST_MONGODB_URL'])
        collection = client['research_analysts']['findings']
        address = parse.urlparse(os.environ['RESEARCH_ANALYST_CHROMADB_URL'])
        chroma = chromadb.HttpClient(host=address.hostname, port=address.port)
        searchable = chroma.get_or_create_collection('findings')
        for slug, kind, title, text, evidence in FINDINGS:
            finding_id = f'{PROJECT}:{slug}'
            collection.update_one(
                {'_id': finding_id},
                {
                    '$set': {
                        'project': PROJECT,
                        'paper': PAPER,
                        'stage': 'results',
                        'kind': kind,
                        'title': title,
                        'text': text,
                        'evidence': evidence,
                        'recorded_at': datetime.datetime.now(datetime.UTC),
                    }
                },
                upsert=True,
            )
            searchable.upsert(
                ids=[finding_id],
                documents=[f'{title}. {text}'],
                metadatas=[
                    {'project': PROJECT, 'stage': 'results', 'kind': kind}
                ],
            )
        print(f'{len(FINDINGS)} findings stored')


if __name__ == '__main__':
    StoreSharedResultsApplication().run()
