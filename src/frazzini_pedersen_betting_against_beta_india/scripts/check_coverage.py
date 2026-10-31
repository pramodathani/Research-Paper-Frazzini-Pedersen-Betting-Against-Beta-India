"""Counts what the downloaded data covers and writes data/coverage.json."""

import json
from pathlib import Path

import pandas as pd

from frazzini_pedersen_betting_against_beta_india.data.bhavcopy_parser import (
    BhavcopyParser,
)


class CoverageApplication:
    """Parses every bhavcopy and counts shares by year."""

    def run(self) -> None:
        """Writes data/coverage.json and prints it.

        Returns:
            None.
        """
        parser = BhavcopyParser()
        rows = []
        files = sorted(Path('data/nse/bhavcopy').glob('*.zip'))
        for path in files:
            table = parser.parse_file(path)
            table = table[table['series'].isin(['EQ', 'BE', 'BZ'])]
            rows.append(table[['date', 'symbol', 'isin']])
        frame = pd.concat(rows)
        frame['year'] = pd.to_datetime(frame['date']).dt.year
        by_year = frame.groupby('year').agg(
            symbols=('symbol', 'nunique'),
            days=('date', 'nunique'),
            with_isin=('isin', lambda s: s.notna().mean()),
        )
        result = {
            'files': len(files),
            'rows': len(frame),
            'symbols': int(frame['symbol'].nunique()),
            'first_date': str(frame['date'].min()),
            'last_date': str(frame['date'].max()),
            'by_year': by_year.round(3).reset_index().to_dict('records'),
        }
        Path('data/coverage.json').write_text(json.dumps(result, indent=1, default=str))
        print(by_year.to_string())
        print({k: v for k, v in result.items() if k != 'by_year'})


if __name__ == '__main__':
    CoverageApplication().run()
