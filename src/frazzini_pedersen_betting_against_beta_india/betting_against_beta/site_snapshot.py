"""Turns the saved results into the companion page's compact JSON snapshot."""

import json
import math
from pathlib import Path

import pandas as pd


class SiteSnapshot:
    """Writes snapshot.json and one grid file per universe from results/.

    Monthly returns are stored as integers in hundredths of a percent
    (basis points), with null for a month without a return, so the files
    stay small; the page divides by 10,000. Only derived results are
    written, never exchange data.

    Attributes:
        results: The results folder.
    """

    TABLES = (
        'deciles_A_equal',
        'deciles_A_value',
        'deciles_B_equal',
        'deciles_B_value',
        'deciles_C_equal',
        'bab_summary',
        'tradeable',
        'tradeable_vs_benchmarks',
        'beta_windows_A',
        'beta_windows_B',
        'size_terciles_A',
        'size_terciles_B',
        'liquidity_screens_A',
        'sub_periods_A',
        'sub_periods_B',
        'sub_periods_C',
        'borrow_sensitivity',
        'roll_sensitivity',
        'delisting_stress',
        'compression_realised_vol',
        'compression_india_vix',
        'ubi_crosscheck',
        'calendar_years_A',
        'borrow_fee_by_year',
    )

    def __init__(self, results: Path) -> None:
        """Keeps the folder.

        Args:
            results (Path): The results folder.

        Returns:
            None.
        """
        self.results = Path(results)

    @staticmethod
    def basis_points(values) -> list:
        """Rounds returns to whole basis points.

        Args:
            values: Decimal returns.

        Returns:
            list: Integers, or None where a value is missing.
        """
        out = []
        for value in values:
            if value is None or (
                isinstance(value, float) and math.isnan(value)
            ):
                out.append(None)
            else:
                out.append(round(float(value) * 10000))
        return out

    @staticmethod
    def clean(value):
        """Makes a value JSON-safe, rounding floats to six places.

        Args:
            value: Any table value.

        Returns:
            A float, int, str or None.
        """
        if isinstance(value, float):
            return None if math.isnan(value) else round(value, 6)
        if hasattr(value, 'item'):
            return SiteSnapshot.clean(value.item())
        return value

    def table(self, name: str) -> dict:
        """Reads one results table.

        Args:
            name (str): The csv's stem.

        Returns:
            dict: rows (the index labels), columns and values.
        """
        frame = pd.read_csv(self.results / f'{name}.csv', index_col=0)
        if name == 'bab_summary':
            frame = pd.read_csv(self.results / f'{name}.csv', index_col=[0, 1])
            frame.index = [f'{u} {r}' for u, r in frame.index]
        return {
            'rows': [str(r) for r in frame.index],
            'columns': list(frame.columns),
            'values': [
                [self.clean(v) for v in row]
                for row in frame.to_numpy().tolist()
            ],
        }

    def series(self) -> dict:
        """Collects the headline monthly series.

        Returns:
            dict: months and series of basis points by name.
        """
        frames = []
        for universe in ('A', 'B', 'C'):
            frame = pd.read_csv(
                self.results / f'monthly_series_{universe}.csv', index_col=0
            )
            frames.append(
                frame[['BAB', 'BAB after costs']].rename(
                    columns={
                        'BAB': f'BAB {universe}',
                        'BAB after costs': f'BAB {universe} after costs',
                    }
                )
            )
            if universe == 'A':
                frames.append(
                    frame[[f'P{n}' for n in range(1, 11)]].add_prefix('A ')
                )
        frames.append(
            pd.read_csv(self.results / 'tradeable_monthly.csv', index_col=0)
        )
        frames.append(
            pd.read_csv(self.results / 'benchmarks_monthly.csv', index_col=0)
        )
        joined = pd.concat(frames, axis=1).sort_index()
        return {
            'months': [str(m) for m in joined.index],
            'values': {c: self.basis_points(joined[c]) for c in joined.columns},
        }

    def risk_free(self, months: list[str], data: Path) -> list:
        """Gives the monthly risk-free return on the given months.

        Args:
            months (list[str]): Months as YYYY-MM.
            data (Path): The study's data folder.

        Returns:
            list: Basis points by month.
        """
        from frazzini_pedersen_betting_against_beta_india.betting_against_beta.market_data import (
            MarketData,
        )

        rf = MarketData(data).risk_free_monthly()
        rf.index = rf.index.astype(str)
        return self.basis_points(rf.reindex(months).ffill())

    def grid(self) -> tuple[list[dict], dict[str, dict]]:
        """Splits the grid into a summary list and one series file per universe.

        BAB series are stored per variant as the return before costs (g)
        and the cost (c, before minus after). The long-only leg does not
        depend on the shrinkage (it only rescales the BAB legs), so it is
        stored once per window, holding period and weighting, under a key
        such as 12-60-1-rank.

        Returns:
            tuple[list[dict], dict[str, dict]]: The variants as lists of
                id, universe, volatility months, correlation months,
                shrinkage, holding months and weighting (the page computes
                every statistic from the series), and for each universe the
                months, the BAB series by variant id and the long-only
                series by key.
        """
        summary = pd.read_parquet(self.results / 'grid_summary.parquet')
        series = pd.read_parquet(self.results / 'grid_series.parquet')
        variants = []
        for number, row in summary.iterrows():
            variants.append(
                [
                    int(number),
                    row['universe'],
                    int(row['volatility_months']),
                    int(row['correlation_months']),
                    float(row['shrinkage']),
                    int(row['holding_months']),
                    row['weighting'],
                ]
            )
        files = {}
        for universe, group in summary.groupby('universe'):
            part = series[series['variant'].isin(list(group.index))]
            months = sorted(part['month'].unique())
            bab = {}
            long = {}
            for number, rows in part.groupby('variant'):
                rows = rows.set_index('month').reindex(months)
                settings = group.loc[number]
                bab[str(int(number))] = {
                    'g': self.basis_points(rows['bab_gross']),
                    'c': self.basis_points(rows['bab_gross'] - rows['bab_net']),
                }
                key = (
                    f'{int(settings.volatility_months)}-'
                    f'{int(settings.correlation_months)}-'
                    f'{int(settings.holding_months)}-{settings.weighting}'
                )
                if key not in long:
                    long[key] = {
                        'g': self.basis_points(rows['long_gross']),
                        'c': self.basis_points(
                            rows['long_gross'] - rows['long_net']
                        ),
                    }
            files[universe] = {'months': months, 'bab': bab, 'long': long}
        return variants, files

    def write(self, site: Path, data: Path) -> dict[str, int]:
        """Writes every file.

        Args:
            site (Path): The site folder; files go into site/data.
            data (Path): The study's data folder, for the risk-free rate.

        Returns:
            dict[str, int]: The size in bytes of each file written.
        """
        folder = Path(site) / 'data'
        folder.mkdir(parents=True, exist_ok=True)
        series = self.series()
        variants, grids = self.grid()
        all_months = sorted(
            set(series['months']).union(
                *[set(g['months']) for g in grids.values()]
            )
        )
        info = json.loads((self.results / 'run_info.json').read_text())
        snapshot = {
            'info': info,
            'tables': {name: self.table(name) for name in self.TABLES},
            'series': series,
            'risk_free': {
                'months': all_months,
                'values': self.risk_free(all_months, data),
            },
            'variants': variants,
        }
        sizes = {}
        files = {'snapshot.json': snapshot} | {
            f'grid_{u}.json': body for u, body in grids.items()
        }
        for name, body in files.items():
            text = json.dumps(body, separators=(',', ':'))
            (folder / name).write_text(text)
            sizes[name] = len(text)
        return sizes
