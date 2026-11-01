"""Command-line program that estimates a pooled yearly SLB lending fee."""

import argparse
from pathlib import Path

import pandas as pd

from frazzini_pedersen_betting_against_beta_india.data.slb_fee_parser import (
    SlbFeeParser,
)


class EstimateBorrowFeeApplication:
    """Annualises SLB fees against share prices and summarises them by year."""

    def run(self) -> None:
        """Runs the estimate.

        Returns:
            None.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('--data', default='data')
        parser.add_argument('--out', default='results/borrow_fee_by_year.csv')
        arguments = parser.parse_args()
        data = Path(arguments.data)
        fees = SlbFeeParser().parse_folder(data / 'nse/slb_bhavcopy')
        prices = pd.read_parquet(
            data / 'derived/prices_raw.parquet',
            columns=['date', 'symbol', 'close'],
        ).drop_duplicates(['date', 'symbol'])
        table = fees.merge(prices, on=['date', 'symbol'], how='left')
        table = table.dropna(subset=['close'])
        table = table[table['close'] > 0]
        table['annual_fee'] = (
            table['close_fee']
            / table['close']
            * 365.0
            / table['days_to_expiry']
        )
        table['year'] = table['date'].dt.year
        rows = {}
        for year, group in table.groupby('year'):
            weight = group['value']
            rows[year] = {
                'contracts': len(group),
                'shares': group['symbol'].nunique(),
                'value_weighted_fee': float(
                    (group['annual_fee'] * weight).sum() / weight.sum()
                ),
                'median_fee': float(group['annual_fee'].median()),
                'p90_fee': float(group['annual_fee'].quantile(0.9)),
            }
        result = pd.DataFrame(rows).T
        result.index.name = 'year'
        result.to_csv(arguments.out)
        print(result.round(4).to_string())
        weight = table['value']
        print(
            'overall value-weighted',
            round(
                float((table['annual_fee'] * weight).sum() / weight.sum()), 4
            ),
            'median',
            round(float(table['annual_fee'].median()), 4),
        )


if __name__ == '__main__':
    EstimateBorrowFeeApplication().run()
