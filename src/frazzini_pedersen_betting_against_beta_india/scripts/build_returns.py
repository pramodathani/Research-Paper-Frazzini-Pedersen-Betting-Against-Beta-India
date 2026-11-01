"""Command-line program that builds adjusted daily returns from the files."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.daily_return_builder import (
    DailyReturnBuilder,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.symbol_changes import (
    SymbolChanges,
)
from frazzini_pedersen_betting_against_beta_india.data.bhavcopy_parser import (
    BhavcopyParser,
)
from frazzini_pedersen_betting_against_beta_india.data.corporate_actions_parser import (
    CorporateActionsParser,
)


def parse_one(path: str) -> pd.DataFrame:
    """Reads one bhavcopy zip.

    Args:
        path (str): The zip's path.

    Returns:
        pd.DataFrame: The day's rows, empty if the file cannot be read.
    """
    try:
        return BhavcopyParser().parse_file(Path(path))
    except ValueError, OSError, KeyError:
        return pd.DataFrame()


class BuildReturnsApplication:
    """Reads bhavcopies and actions, builds returns and saves them."""

    def run(self) -> None:
        """Runs the build.

        Returns:
            None.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('--data', default='data')
        parser.add_argument('--out-folder', default='data/derived')
        arguments = parser.parse_args()
        data = Path(arguments.data)
        folder = Path(arguments.out_folder)
        folder.mkdir(parents=True, exist_ok=True)
        raw_path = folder / 'prices_raw.parquet'
        if raw_path.exists():
            prices = pd.read_parquet(raw_path)
        else:
            files = sorted(
                str(p) for p in (data / 'nse/bhavcopy').glob('*.zip')
            )
            print(f'{len(files)} bhavcopy files')
            with ProcessPoolExecutor() as pool:
                frames = list(pool.map(parse_one, files, chunksize=50))
            prices = pd.concat(
                [f for f in frames if not f.empty], ignore_index=True
            )
            prices.to_parquet(raw_path)
        print(f'{len(prices)} raw rows')
        actions = CorporateActionsParser().parse_folder(
            data / 'nse/corporate_actions'
        )
        changes = SymbolChanges.from_nse_file(
            str(data / 'nse/symbol_changes/symbolchange.csv')
        )
        prices = changes.apply(prices, 'date')
        actions = changes.apply(actions, 'ex_date')
        returns, flags = DailyReturnBuilder().build(prices, actions)
        returns.to_parquet(folder / 'daily_returns.parquet')
        flags.to_parquet(folder / 'return_flags.parquet')
        print(f'{len(returns)} daily returns, {len(flags)} flagged days')
        print(flags['kind'].value_counts().to_string())


if __name__ == '__main__':
    BuildReturnsApplication().run()
