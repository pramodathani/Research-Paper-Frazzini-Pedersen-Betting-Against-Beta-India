"""Tests of the portfolio builder."""

import numpy as np
import pandas as pd
import pytest

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.portfolio_builder import (
    PortfolioBuilder,
)


def make_builder(months=4, shares=20, seed=1):
    rng = np.random.default_rng(seed)
    dates = pd.date_range('2020-01-31', periods=months, freq='ME')
    columns = [f's{i}' for i in range(shares)]
    betas = pd.DataFrame(
        rng.uniform(0.3, 1.8, (months, shares)), index=dates, columns=columns
    )
    eligible = pd.DataFrame(True, index=dates, columns=columns)
    value = pd.DataFrame(
        rng.uniform(1, 100, (months, shares)), index=dates, columns=columns
    )
    return PortfolioBuilder(betas, eligible, value), betas


def test_holding_month_is_the_month_after_formation():
    builder, _ = make_builder()
    assert builder.holding_periods()[0] == pd.Period('2020-02')


def test_bab_weights_are_beta_neutral_and_levered():
    builder, betas = make_builder()
    weights, summary = builder.bab()
    row = weights.iloc[0]
    assert (row * betas.iloc[0]).sum() == pytest.approx(0.0, abs=1e-9)
    assert row.clip(lower=0).sum() == pytest.approx(
        1 / summary['beta_low'].iloc[0]
    )
    assert -row.clip(upper=0).sum() == pytest.approx(
        1 / summary['beta_high'].iloc[0]
    )


def test_groups_sum_to_one_and_cover_everything():
    builder, _ = make_builder()
    groups = builder.groups(5, weighting='equal')
    total = sum(g.iloc[0] for g in groups.values())
    assert (total > 0).all()
    assert all(g.iloc[0].sum() == pytest.approx(1.0) for g in groups.values())


def test_value_weights_follow_the_value_table():
    builder, _ = make_builder()
    equal = builder.groups(5, weighting='equal')[1].iloc[0]
    valued = builder.groups(5, weighting='value')[1].iloc[0]
    assert not np.allclose(equal, valued)
    assert valued.sum() == pytest.approx(1.0)


def test_value_weighting_without_values_is_refused():
    builder, betas = make_builder()
    plain = PortfolioBuilder(betas, builder.eligible)
    with pytest.raises(ValueError):
        plain.groups(5, weighting='value')


def test_holding_period_averages_cohorts():
    builder, _ = make_builder(months=4)
    one, _ = builder.lowest_beta(0.25, holding_months=1)
    three, _ = builder.lowest_beta(0.25, holding_months=3)
    expected = one.iloc[:3].mean()
    assert three.iloc[2].to_numpy() == pytest.approx(expected.to_numpy())
    assert three.iloc[0].to_numpy() == pytest.approx(one.iloc[0].to_numpy())


def test_a_share_outside_the_universe_gets_no_weight():
    builder, betas = make_builder()
    eligible = builder.eligible.copy()
    eligible['s0'] = False
    limited = PortfolioBuilder(betas, eligible)
    weights, _ = limited.bab()
    assert (weights['s0'] == 0).all()


def test_the_weights_at_a_month_ignore_later_betas():
    builder, betas = make_builder()
    first, _ = builder.bab()
    changed = betas.copy()
    changed.iloc[2:] = 1.0
    other = PortfolioBuilder(changed, builder.eligible)
    second, _ = other.bab()
    pd.testing.assert_series_equal(first.iloc[0], second.iloc[0])
    pd.testing.assert_series_equal(first.iloc[1], second.iloc[1])
