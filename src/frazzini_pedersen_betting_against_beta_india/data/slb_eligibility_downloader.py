"""Downloads NSE's list of shares eligible for securities lending and borrowing."""

import calendar
import datetime
from pathlib import Path

from frazzini_pedersen_betting_against_beta_india.data.nse_session import (
    NseSession,
)


class SlbEligibilityDownloader:
    """Saves one eligibility file per month, from the month's last trading day.

    Each month tries its last weekday and then up to six days earlier until
    NSE serves a file. A month already saved or already known to have no
    file (written to not_available.txt as YYYY-MM) is skipped.

    Attributes:
        folder: Where files and not_available.txt are saved.
        first_month: First month, as a date on its first day.
        last_month: Last month, as a date on its first day.
        session: The NSE session.
    """

    URL = 'https://nsearchives.nseindia.com/archives/slbs/seclist/SLB_ELG_SEC_{stamp}.csv'
    FILE_GLOB = 'SLB_ELG_SEC_*{month:02d}{year}.csv'

    def __init__(
        self,
        folder: Path,
        first_month: datetime.date,
        last_month: datetime.date,
        session: NseSession | None = None,
    ) -> None:
        """Describes the download.

        Args:
            folder (Path): Where to save.
            first_month (datetime.date): First month.
            last_month (datetime.date): Last month.
            session (NseSession | None): A session, or None to make one.

        Returns:
            None.
        """
        self.folder = folder
        self.first_month = first_month
        self.last_month = last_month
        self.session = session or NseSession()

    def run(self) -> dict[str, int]:
        """Downloads every missing month.

        Returns:
            dict[str, int]: Counts of files saved, present, missing and failed.
        """
        self.folder.mkdir(parents=True, exist_ok=True)
        missing_path = self.folder / 'not_available.txt'
        missing = set(missing_path.read_text().split()) if missing_path.exists() else set()
        counts = {'saved': 0, 'present': 0, 'not_available': 0, 'failed': 0}
        year, month = self.first_month.year, self.first_month.month
        while (year, month) <= (self.last_month.year, self.last_month.month):
            key = f'{year}-{month:02d}'
            if any(self.folder.glob(self.FILE_GLOB.format(month=month, year=year))):
                counts['present'] += 1
            elif key in missing:
                counts['not_available'] += 1
            else:
                counts[self._fetch_month(year, month, key, missing_path)] += 1
            month += 1
            if month == 13:
                year, month = year + 1, 1
        return counts

    def _fetch_month(self, year: int, month: int, key: str, missing_path: Path) -> str:
        """Tries the month's last days until a file is served.

        Args:
            year (int): The year.
            month (int): The month.
            key (str): The month as YYYY-MM.
            missing_path (Path): The not_available.txt file.

        Returns:
            str: 'saved', 'not_available' or 'failed'.
        """
        day = datetime.date(year, month, calendar.monthrange(year, month)[1])
        for _ in range(7):
            if day.weekday() < 5 and day <= datetime.date.today():
                url = self.URL.format(stamp=day.strftime('%d%m%Y'))
                response = self.session.get(url)
                if response is None or response.status_code not in (200, 404):
                    return 'failed'
                if response.status_code == 200 and len(response.content) > 500:
                    target = self.folder / url.rsplit('/', 1)[-1]
                    target.write_bytes(response.content)
                    return 'saved'
            day -= datetime.timedelta(days=1)
        with missing_path.open('a') as handle:
            handle.write(key + '\n')
        return 'not_available'
