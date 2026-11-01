"""Tests of the companion page's snapshot builder."""

import json

import pandas as pd

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.site_snapshot import (
    SiteSnapshot,
)


def test_basis_points_round_and_keep_gaps():
    assert SiteSnapshot.basis_points([0.01234, float('nan'), -0.5]) == [
        123,
        None,
        -5000,
    ]


def test_clean_drops_nan_and_rounds():
    assert SiteSnapshot.clean(float('nan')) is None
    assert SiteSnapshot.clean(0.123456789) == 0.123457
    assert SiteSnapshot.clean('x') == 'x'


def test_grid_files_split_by_universe_and_share_the_long_leg(tmp_path):
    summary = pd.DataFrame(
        {
            'universe': ['A', 'A', 'B'],
            'volatility_months': [12, 12, 12],
            'correlation_months': [60, 60, 60],
            'shrinkage': [0.6, 0.8, 0.6],
            'holding_months': [1, 1, 1],
            'weighting': ['rank', 'rank', 'rank'],
        },
        index=pd.Index([1, 2, 3], name='variant'),
    )
    rows = []
    for variant in (1, 2, 3):
        for month in ('2020-01', '2020-02'):
            rows.append(
                {
                    'month': month,
                    'variant': variant,
                    'bab_gross': 0.01 * variant,
                    'bab_net': 0.01 * variant - 0.002,
                    'long_gross': 0.02,
                    'long_net': 0.019,
                }
            )
    summary.to_parquet(tmp_path / 'grid_summary.parquet')
    pd.DataFrame(rows).to_parquet(tmp_path / 'grid_series.parquet')
    variants, files = SiteSnapshot(tmp_path).grid()
    assert [v[0] for v in variants] == [1, 2, 3]
    assert set(files) == {'A', 'B'}
    assert files['A']['bab']['2']['g'] == [200, 200]
    assert files['A']['bab']['2']['c'] == [20, 20]
    assert list(files['A']['long']) == ['12-60-1-rank']
    assert json.dumps(files['A'])
