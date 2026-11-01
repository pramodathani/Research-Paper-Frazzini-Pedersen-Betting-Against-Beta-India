"""Command-line program that downloads index history from niftyindices.com."""

import datetime
from pathlib import Path

from frazzini_pedersen_betting_against_beta_india.data.niftyindices_downloader import (
    NiftyIndicesDownloader,
)

TOTAL_RETURN = (
    'NIFTY 500',
    'NIFTY 50',
    'NIFTY 100',
    'NIFTY 200',
    'NIFTY MIDCAP 100',
    'NIFTY SMALLCAP 100',
    'NIFTY100 LOW VOLATILITY 30',
    'NIFTY LOW VOLATILITY 50',
)
PRICE = (
    'NIFTY 500',
    'NIFTY 50',
    'NIFTY100 LOW VOLATILITY 30',
    'NIFTY LOW VOLATILITY 50',
)


class DownloadIndicesApplication:
    """Downloads the benchmark and low-volatility index histories."""

    def run(self) -> None:
        """Fetches every missing chunk and prints the counts.

        Returns:
            None.
        """
        downloader = NiftyIndicesDownloader(Path('data/niftyindices'))
        last_year = datetime.date.today().year
        for kind, names in (('total_return', TOTAL_RETURN), ('price', PRICE)):
            for name in names:
                counts = downloader.run(kind, name, 1995, last_year)
                print(kind, name, counts, flush=True)


if __name__ == '__main__':
    DownloadIndicesApplication().run()
