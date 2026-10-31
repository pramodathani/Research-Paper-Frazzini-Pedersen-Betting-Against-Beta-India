"""Downloads NSE's securities lending and borrowing bhavcopy."""

from frazzini_pedersen_betting_against_beta_india.data.slb_eligibility_downloader import (
    SlbEligibilityDownloader,
)


class SlbBhavcopyDownloader(SlbEligibilityDownloader):
    """Saves one SLB bhavcopy (trades, fees and open positions) per month.

    It works like the eligibility downloader, with the bhavcopy's address.
    Files are small because few shares trade in the scheme.
    """

    URL = 'https://nsearchives.nseindia.com/archives/slbs/bhavcopy/SLBM_BC_{stamp}.DAT'
    FILE_GLOB = 'SLBM_BC_*{month:02d}{year}.DAT'
