"""Tests of the beta estimator."""

import numpy as np
import pandas as pd
import pytest

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.beta_estimator import (
    BetaEstimator,
)


def make_market(days: int, seed: int = 0):
    rng = np.random.default_rng(seed)
    index = pd.bdate_range('2020-01-01', periods=days)
    market = pd.Series(rng.normal(0, 0.01, days), index=index)
    return index, market


def test_exact_beta_when_share_is_a_multiple_of_the_market():
    index, market = make_market(400)
    shares = pd.DataFrame({'A': 1.5 * market, 'B': 0.5 * market})
    estimator = BetaEstimator(shares, market, 100, 200)
    beta = estimator.beta(index[-1:], 252, 300, 1, shrinkage=1.0)
    assert beta['A'].iloc[0] == pytest.approx(1.5, abs=1e-5)
    assert beta['B'].iloc[0] == pytest.approx(0.5, abs=1e-5)


def test_three_day_returns_are_overlapping_sums():
    index, market = make_market(30)
    shares = pd.DataFrame({'A': market * 2})
    estimator = BetaEstimator(shares, market, 5, 5)
    summed, market_sum = estimator._overlapping_returns(3)
    assert market_sum[5] == pytest.approx(market.iloc[3:6].sum())
    assert np.isnan(market_sum[1])
    assert summed[5, 0] == pytest.approx(2 * market.iloc[3:6].sum())


def test_shrinkage_pulls_towards_one():
    index, market = make_market(400)
    shares = pd.DataFrame({'A': 2.0 * market})
    estimator = BetaEstimator(shares, market, 100, 200)
    beta = estimator.beta(index[-1:], 252, 300, 1, shrinkage=0.6)
    assert beta['A'].iloc[0] == pytest.approx(0.6 * 2.0 + 0.4, abs=1e-5)


def test_too_few_observations_give_nan():
    index, market = make_market(400)
    shares = pd.DataFrame({'A': 1.0 * market, 'B': 1.0 * market})
    shares.iloc[:350, 1] = np.nan
    estimator = BetaEstimator(shares, market, 100, 200)
    beta = estimator.beta(index[-1:], 252, 300, 1)
    assert not np.isnan(beta['A'].iloc[0])
    assert np.isnan(beta['B'].iloc[0])


def test_changing_later_prices_does_not_change_an_earlier_estimate():
    index, market = make_market(500)
    rng = np.random.default_rng(3)
    shares = pd.DataFrame({'A': market + rng.normal(0, 0.01, 500)})
    date = index[399:400]
    first = BetaEstimator(shares, market, 100, 200).beta(date, 252, 300, 3)
    changed = shares.copy()
    changed.iloc[420:] = 0.5
    again = BetaEstimator(changed, market, 100, 200).beta(date, 252, 300, 3)
    pd.testing.assert_frame_equal(first, again)


def test_mismatched_dates_are_refused():
    index, market = make_market(50)
    with pytest.raises(ValueError):
        BetaEstimator(pd.DataFrame({'A': market}).iloc[1:], market)
