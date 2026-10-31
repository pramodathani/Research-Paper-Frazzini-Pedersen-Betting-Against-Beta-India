"""Command-line program that downloads NSE's monthly SLB eligibility lists."""

import datetime
from pathlib import Path

from frazzini_pedersen_betting_against_beta_india.data.slb_bhavcopy_downloader import (
    SlbBhavcopyDownloader,
)
from frazzini_pedersen_betting_against_beta_india.data.slb_eligibility_downloader import (
    SlbEligibilityDownloader,
)


class DownloadSlbApplication:
    """Downloads monthly eligibility lists since 2008 and SLB bhavcopies since 2010."""

    def run(self) -> None:
        """Fetches every missing month and prints the counts.

        Returns:
            None.
        """
        downloader = SlbEligibilityDownloader(
            Path('data/nse/slb_eligibility'),
            datetime.date(2008, 1, 1),
            datetime.date.today().replace(day=1),
        )
        print(downloader.run())
        bhavcopy = SlbBhavcopyDownloader(
            Path('data/nse/slb_bhavcopy'),
            datetime.date(2010, 9, 1),
            datetime.date.today().replace(day=1),
        )
        print(bhavcopy.run())


if __name__ == '__main__':
    DownloadSlbApplication().run()
