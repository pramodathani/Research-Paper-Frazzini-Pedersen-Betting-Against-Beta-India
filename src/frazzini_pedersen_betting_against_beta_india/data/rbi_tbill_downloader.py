"""Downloads RBI's 91-day Treasury Bill auction results from its press releases."""

import time
from pathlib import Path

import requests


class RbiTbillDownloader:
    """Scans RBI press release numbers and keeps the T-Bill auction results.

    RBI numbers its press releases in sequence. This asks for each number
    in a range, keeps the raw page of every one titled as a T-Bill auction
    result, and records the numbers that were something else in
    scanned.txt, so a stopped scan resumes where it stopped.

    Attributes:
        folder: Where pages and scanned.txt are saved.
        first_id: First press release number.
        last_id: Last press release number.
        pause_seconds: Seconds to wait between requests.
    """

    URL = 'https://www.rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid='
    MARK = '91-Day, 182-Day and 364-Day T-Bill Auction Result'

    def __init__(
        self,
        folder: Path,
        first_id: int,
        last_id: int,
        pause_seconds: float = 0.3,
    ) -> None:
        """Describes the scan.

        Args:
            folder (Path): Where to save.
            first_id (int): First press release number.
            last_id (int): Last press release number.
            pause_seconds (float): Seconds to wait between requests.

        Returns:
            None.
        """
        self.folder = folder
        self.first_id = first_id
        self.last_id = last_id
        self.pause_seconds = pause_seconds

    def run(self) -> dict[str, int]:
        """Scans every number not scanned before.

        Returns:
            dict[str, int]: Counts of pages saved, skipped and failed.
        """
        self.folder.mkdir(parents=True, exist_ok=True)
        scanned_path = self.folder / 'scanned.txt'
        scanned = set(scanned_path.read_text().split()) if scanned_path.exists() else set()
        counts = {'saved': 0, 'skipped': 0, 'failed': 0}
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Chrome/130.0'}
        session = requests.Session()
        for number in range(self.first_id, self.last_id + 1):
            if str(number) in scanned or (self.folder / f'{number}.html').exists():
                counts['skipped'] += 1
                continue
            time.sleep(self.pause_seconds)
            try:
                response = session.get(self.URL + str(number), headers=headers, timeout=60)
            except requests.RequestException:
                counts['failed'] += 1
                continue
            if response.status_code != 200:
                counts['failed'] += 1
                continue
            if self.MARK in response.text and 'Cut-off Price' in response.text:
                (self.folder / f'{number}.html').write_text(response.text)
                counts['saved'] += 1
            else:
                with scanned_path.open('a') as handle:
                    handle.write(f'{number}\n')
        return counts
