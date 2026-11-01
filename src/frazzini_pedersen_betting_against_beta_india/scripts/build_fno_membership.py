"""Command-line program that lists which shares had stock futures each day."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.symbol_changes import (
    SymbolChanges,
)
from frazzini_pedersen_betting_against_beta_india.data.fno_bhavcopy_parser import (
    FnoBhavcopyParser,
)


def parse_one(path: str) -> pd.DataFrame:
    """Reads one derivatives bhavcopy zip.

    Args:
        path (str): The zip's path.

    Returns:
        pd.DataFrame: Columns date, symbol, close and open_interest, empty
            when the file cannot be read.
    """
    try:
        table = FnoBhavcopyParser().parse_file(Path(path))
    except ValueError, OSError, KeyError, IndexError:
        return pd.DataFrame()
    return table[['date', 'symbol', 'close', 'open_interest']]


class BuildFnoMembershipApplication:
    """Saves one row per share per day that had a stock future."""

    def run(self) -> None:
        """Runs the build.

        Returns:
            None.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('--data', default='data')
        parser.add_argument('--out', default='data/derived/fno_members.parquet')
        arguments = parser.parse_args()
        data = Path(arguments.data)
        files = sorted(str(p) for p in (data / 'nse/fno').glob('*.zip'))
        print(f'{len(files)} files')
        with ProcessPoolExecutor() as pool:
            frames = list(pool.map(parse_one, files, chunksize=50))
        table = pd.concat([f for f in frames if not f.empty], ignore_index=True)
        changes = SymbolChanges.from_nse_file(
            str(data / 'nse/symbol_changes/symbolchange.csv')
        )
        table = changes.apply(table, 'date').reset_index(drop=True)
        table.to_parquet(arguments.out)
        print(f'{len(table)} rows, {table.symbol.nunique()} shares')


if __name__ == '__main__':
    BuildFnoMembershipApplication().run()
