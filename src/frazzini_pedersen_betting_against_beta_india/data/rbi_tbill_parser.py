"""Reads RBI's T-Bill auction result pages."""

import re
from pathlib import Path

import pandas as pd


class RbiTbillParser:
    """Turns saved auction pages into a table of 91-day cut-off yields."""

    DATE = re.compile(r'Date\s*:\s*([A-Z][a-z]{2} \d{1,2}, \d{4})')
    CUTOFF = re.compile(r'Cut-off Price[^<]*?\(YTM:\s*([\d.]+)%\)')

    def parse_folder(self, folder: Path) -> pd.DataFrame:
        """Reads every saved page.

        Args:
            folder (Path): The folder of saved pages.

        Returns:
            pd.DataFrame: Columns date and yield_91d (percent a year), sorted
                by date, one row per auction page with a cut-off yield.
        """
        rows = []
        for path in sorted(folder.glob('*.html')):
            text = re.sub(r'<[^>]*>', ' ', path.read_text(errors='ignore'))
            text = re.sub(r'\s+', ' ', text)
            date = self.DATE.search(text)
            cutoff = self.CUTOFF.search(text)
            if date and cutoff:
                rows.append({
                    'date': pd.to_datetime(date.group(1), format='%b %d, %Y'),
                    'yield_91d': float(cutoff.group(1)),
                })
        return pd.DataFrame(rows).sort_values('date').reset_index(drop=True)
