"""Command-line program that writes the companion page's data files."""

import argparse
from pathlib import Path

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.site_snapshot import (
    SiteSnapshot,
)


class BuildSnapshotApplication:
    """Writes site/data from results/."""

    def run(self) -> None:
        """Writes the snapshot.

        Returns:
            None.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('--results', default='results')
        parser.add_argument('--data', default='data')
        parser.add_argument(
            '--site',
            default=str(Path(__file__).resolve().parents[1] / 'site'),
        )
        arguments = parser.parse_args()
        sizes = SiteSnapshot(Path(arguments.results)).write(
            Path(arguments.site), Path(arguments.data)
        )
        for name, size in sizes.items():
            print(f'{name}: {size / 1024:.0f} KB')


if __name__ == '__main__':
    BuildSnapshotApplication().run()
