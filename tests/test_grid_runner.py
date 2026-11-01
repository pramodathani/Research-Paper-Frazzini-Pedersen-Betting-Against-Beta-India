"""Tests of the grid runner on a made-up market."""

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.grid_runner import (
    GridRunner,
)
from tests.test_end_to_end import make_study


def test_grid_counts_and_columns():
    study, _ = make_study(shares=50, years=8)
    runner = GridRunner(study)
    count = runner.variant_count(
        ['A'], [6, 12], [12, 36], [0.6], [1, 3], ['rank', 'equal']
    )
    assert count == 16
    summary, series = runner.run(
        ['A'], [12], [36], [0.6, 1.0], [1, 3], ['rank']
    )
    assert len(summary) == 4
    assert set(series['variant']) == {1, 2, 3, 4}
    assert {'bab_gross', 'bab_net', 'long_gross', 'long_net'} <= set(
        series.columns
    )
    assert (summary['bab_net_mean'] < summary['bab_excess_mean']).all()


def test_the_paper_grid_has_864_variants():
    study, _ = make_study(shares=50, years=8)
    runner = GridRunner(study)
    assert (
        runner.variant_count(
            ['A', 'B', 'C'],
            [6, 12, 24],
            [12, 36, 60],
            [0.4, 0.6, 0.8, 1.0],
            [1, 3, 6, 12],
            ['rank', 'equal'],
        )
        == 864
    )
