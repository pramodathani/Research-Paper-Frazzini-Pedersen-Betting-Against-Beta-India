"""Command-line program that downloads RBI's T-Bill auction results."""

import argparse
from pathlib import Path

from frazzini_pedersen_betting_against_beta_india.data.rbi_tbill_downloader import (
    RbiTbillDownloader,
)


class DownloadTbillsApplication:
    """Scans a range of RBI press release numbers."""

    def run(self) -> None:
        """Parses the arguments and scans.

        Returns:
            None.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument('--first', type=int, default=61900)
        parser.add_argument('--last', type=int, default=63900)
        arguments = parser.parse_args()
        folder = Path('data/rbi/tbill_auctions')
        print(RbiTbillDownloader(folder, arguments.first, arguments.last).run())


if __name__ == '__main__':
    DownloadTbillsApplication().run()
