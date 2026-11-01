"""Reads the SLB bhavcopy and turns lending fees into yearly rates."""

from pathlib import Path

import pandas as pd


class SlbFeeParser:
    """Turns an SLB bhavcopy into a table of fees per share to expiry.

    Each row of the file is one SLB contract: a share, a series that ends on
    an expiry date, then the fee in rupees per share for lending until that
    expiry (previous close, open, high, low, close), the quantity and the
    value traded. The yearly rate is the fee divided by the share price,
    scaled from the days to expiry to 365 days.
    """

    COLUMNS = (
        'name',
        'symbol',
        'series',
        'expiry',
        'flag',
        'previous_fee',
        'open_fee',
        'high_fee',
        'low_fee',
        'close_fee',
        'blank',
        'quantity',
        'value',
        'last_fee',
        'reference_fee',
        'date',
        'trades',
    )

    def parse_file(self, path: Path) -> pd.DataFrame:
        """Reads one file.

        Args:
            path (Path): The SLBM_BC_DDMMYYYY.DAT file.

        Returns:
            pd.DataFrame: Columns date, symbol, expiry, close_fee, quantity,
                value and days_to_expiry, one row per contract with trades.
        """
        raw = pd.read_csv(
            path,
            header=None,
            names=list(self.COLUMNS),
            dtype=str,
            skipinitialspace=True,
            index_col=False,
        )
        table = pd.DataFrame()
        table['symbol'] = raw['symbol'].str.strip()
        table['date'] = pd.to_datetime(
            raw['date'].str.strip(), format='%d-%b-%Y', errors='coerce'
        )
        table['expiry'] = pd.to_datetime(
            raw['expiry'].str.strip(), format='%d-%b-%Y', errors='coerce'
        )
        for column in ('close_fee', 'quantity', 'value'):
            table[column] = pd.to_numeric(
                raw[column].str.strip(), errors='coerce'
            )
        table['days_to_expiry'] = (table['expiry'] - table['date']).dt.days
        table = table.dropna()
        return table[(table['quantity'] > 0) & (table['days_to_expiry'] > 0)]

    def parse_folder(self, folder: Path) -> pd.DataFrame:
        """Reads every file in a folder.

        Args:
            folder (Path): The folder of .DAT files.

        Returns:
            pd.DataFrame: The rows of all files together.
        """
        frames = [self.parse_file(p) for p in sorted(folder.glob('*.DAT'))]
        return pd.concat(frames, ignore_index=True)
