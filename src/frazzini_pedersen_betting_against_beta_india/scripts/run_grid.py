"""Command-line program that runs the 864-variant grid and saves it."""

import argparse
import warnings
from pathlib import Path

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.bab_study import (
    BabStudy,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.grid_runner import (
    GridRunner,
)


class RunGridApplication:
    """Builds the study and runs the grid."""

    def run(self) -> None:
        """Runs the grid.

        Returns:
            None.
        """
        warnings.simplefilter('ignore')
        parser = argparse.ArgumentParser()
        parser.add_argument('--data', default='data')
        parser.add_argument('--derived', default='data/derived')
        parser.add_argument('--out-folder', default='results')
        parser.add_argument('--universes', default='A,B,C')
        arguments = parser.parse_args()
        study = BabStudy.from_files(
            Path(arguments.data), Path(arguments.derived)
        )
        summary, series = GridRunner(study).run(
            universes=arguments.universes.split(','), progress=True
        )
        folder = Path(arguments.out_folder)
        folder.mkdir(parents=True, exist_ok=True)
        summary.to_parquet(folder / 'grid_summary.parquet')
        series.to_parquet(folder / 'grid_series.parquet')
        print(f'{len(summary)} variants saved to {folder}')


if __name__ == '__main__':
    RunGridApplication().run()
