"""Command-line program that saves India VIX and a few index closes by day."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

from frazzini_pedersen_betting_against_beta_india.data.index_close_parser import (
    IndexCloseParser,
)

KEEP = ('India VIX', 'Nifty 50', 'Nifty 500')


def parse_one(path: str) -> pd.DataFrame:
    """Reads one ind_close_all file and keeps the indices of interest.

    Args:
        path (str): The csv's path.

    Returns:
        pd.DataFrame: Columns date, index_name and close.
    """
    try:
        table = IndexCloseParser().parse_file(Path(path))
    except ValueError, KeyError, OSError:
        return pd.DataFrame()
    names = table['index_name'].str.lower()
    kept = table[names.isin([n.lower() for n in KEEP])]
    return kept[['date', 'index_name', 'close']]


class BuildIndiaVixApplication:
    """Saves the daily India VIX."""

    def run(self) -> None:
        """Runs the build.

        Returns:
            None.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('--data', default='data')
        parser.add_argument(
            '--out', default='data/derived/index_closes.parquet'
        )
        arguments = parser.parse_args()
        files = sorted(
            str(p) for p in (Path(arguments.data) / 'nse/index').glob('*.csv')
        )
        with ProcessPoolExecutor() as pool:
            frames = list(pool.map(parse_one, files, chunksize=50))
        table = pd.concat([f for f in frames if not f.empty], ignore_index=True)
        table.to_parquet(arguments.out)
        vix = table[table['index_name'].str.lower() == 'india vix']
        print(
            f'{len(table)} rows; VIX {vix.date.min()} to {vix.date.max()}, {len(vix)} days'
        )


if __name__ == '__main__':
    BuildIndiaVixApplication().run()
