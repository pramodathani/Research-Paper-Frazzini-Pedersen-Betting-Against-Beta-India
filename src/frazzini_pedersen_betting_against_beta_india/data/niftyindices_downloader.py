"""Downloads daily index history from niftyindices.com."""

import datetime
import json
import re
import time
from pathlib import Path
from typing import ClassVar

import requests


class NiftyIndicesDownloader:
    """Saves price and total-return history in five-year chunks.

    Each response is saved as served, as JSON, under
    folder/<endpoint>/<index>_<first>_<last>.json. A chunk already on disk
    is skipped, except one that reaches today, which is fetched again. An
    empty answer is saved too, so a rerun does not ask again.

    Attributes:
        folder: Where the chunks are saved.
        pause_seconds: Seconds to wait between requests.
        session: The HTTP session holding NSE's cookies.
    """

    HOME = 'https://www.niftyindices.com/reports/historical-data'
    BASE = 'https://www.niftyindices.com/BackPage/'
    ENDPOINTS: ClassVar[dict[str, str]] = {
        'price': 'getHistoricaldatatabletoString',
        'total_return': 'getTotalReturnIndexString',
    }

    def __init__(self, folder: Path, pause_seconds: float = 1.0) -> None:
        """Describes the download.

        Args:
            folder (Path): Where to save.
            pause_seconds (float): Seconds to wait between requests.

        Returns:
            None.
        """
        self.folder = folder
        self.pause_seconds = pause_seconds
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/130.0 Safari/537.36'
            ),
            'Content-Type': 'application/json; charset=utf-8',
            'Referer': self.HOME,
            'Origin': 'https://www.niftyindices.com',
        })
        self._warmed = False

    def run(
        self,
        kind: str,
        index_name: str,
        first_year: int,
        last_year: int,
    ) -> dict[str, int]:
        """Downloads every missing five-year chunk of one series.

        Args:
            kind (str): 'price' or 'total_return'.
            index_name (str): The index's name in upper case.
            first_year (int): First calendar year.
            last_year (int): Last calendar year.

        Returns:
            dict[str, int]: Chunks saved, present and failed, and rows saved.
        """
        target_folder = self.folder / kind
        target_folder.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r'[^A-Za-z0-9]+', '_', index_name).strip('_')
        counts = {'saved': 0, 'present': 0, 'failed': 0, 'rows': 0}
        today = datetime.date.today()
        for year in range(first_year, last_year + 1, 5):
            end_year = min(year + 4, last_year)
            first = datetime.date(year, 1, 1)
            last = min(datetime.date(end_year, 12, 31), today)
            target = target_folder / (
                f'{slug}_{first.isoformat()}_{datetime.date(end_year, 12, 31).isoformat()}.json'
            )
            if target.exists() and datetime.date(end_year, 12, 31) < today:
                counts['present'] += 1
                continue
            rows = self._fetch(kind, index_name, first, last)
            if rows is None:
                counts['failed'] += 1
                continue
            target.write_text(json.dumps(rows))
            counts['saved'] += 1
            counts['rows'] += len(rows)
        return counts

    def _fetch(
        self,
        kind: str,
        index_name: str,
        first: datetime.date,
        last: datetime.date,
    ) -> list | None:
        """Asks for one chunk.

        Args:
            kind (str): The series kind.
            index_name (str): The index name.
            first (datetime.date): First day.
            last (datetime.date): Last day.

        Returns:
            list | None: The rows, or None when the request failed.
        """
        if not self._warmed:
            self.session.get(self.HOME, timeout=60)
            self._warmed = True
        start = first.strftime('%d-%b-%Y')
        end = last.strftime('%d-%b-%Y')
        cinfo = (
            f"{{'name':'{index_name}','startDate':'{start}',"
            f"'endDate':'{end}','indexName':'{index_name}'}}"
        )
        body = json.dumps({'cinfo': cinfo})
        for attempt in range(3):
            time.sleep(self.pause_seconds)
            try:
                response = self.session.post(
                    self.BASE + self.ENDPOINTS[kind], data=body, timeout=90
                )
                payload = response.json()
                text = payload['d'] if isinstance(payload, dict) else payload
                if text in ('false', 'False'):
                    return []
                return json.loads(text) if isinstance(text, str) else text
            except (requests.RequestException, ValueError, KeyError):
                time.sleep(5 * (attempt + 1))
        return None
