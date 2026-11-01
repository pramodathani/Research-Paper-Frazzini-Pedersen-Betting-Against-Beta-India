"""Tests of the rank weights and the BAB return."""

import pandas as pd
import pytest

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.rank_weights import (
    RankWeights,
)


def test_five_shares_match_a_hand_calculation():
    betas = pd.Series([0.5, 0.8, 1.0, 1.2, 1.6], index=list('abcde'))
    low, high = RankWeights().split(betas)
    # ranks 1..5, centred -2,-1,0,1,2, sum |.| = 6, k = 1/3
    assert low['a'] == pytest.approx(2 / 3)
    assert low['b'] == pytest.approx(1 / 3)
    assert high['d'] == pytest.approx(1 / 3)
    assert high['e'] == pytest.approx(2 / 3)
    assert low['c'] == 0 and high['c'] == 0
    assert low.sum() == pytest.approx(1.0)
    assert high.sum() == pytest.approx(1.0)


def test_ties_share_the_average_rank():
    betas = pd.Series([1.0, 1.0, 2.0, 3.0], index=list('abcd'))
    low, _ = RankWeights().split(betas)
    assert low['a'] == pytest.approx(low['b'])
    assert low.sum() == pytest.approx(1.0)


def test_bab_return_with_constant_returns():
    betas = pd.Series([0.5, 0.8, 1.0, 1.2, 1.6], index=list('abcde'))
    returns = pd.Series([0.01, 0.02, 0.03, 0.04, 0.05], index=list('abcde'))
    weights = RankWeights()
    low, high = weights.split(betas)
    beta_low = (low * betas).sum()
    beta_high = (high * betas).sum()
    expected = (0.01 * 2 / 3 + 0.02 / 3 - 0.001) / beta_low - (
        0.04 / 3 + 0.05 * 2 / 3 - 0.001
    ) / beta_high
    assert weights.bab_return(returns, betas, 0.001) == pytest.approx(expected)


def test_the_factor_is_beta_neutral():
    betas = pd.Series([0.5, 0.8, 1.0, 1.2, 1.6], index=list('abcde'))
    weights = RankWeights()
    low, high = weights.split(betas)
    beta_low, beta_high = weights.bab_leverage(betas, low, high)
    assert beta_low / beta_low - beta_high / beta_high == 0
    assert 1 / beta_low * beta_low == pytest.approx(1 / beta_high * beta_high)


def test_groups_cut_evenly():
    betas = pd.Series(
        range(20), index=[f's{i}' for i in range(20)], dtype=float
    )
    groups = RankWeights().groups(betas, 10)
    assert groups.value_counts().eq(2).all()
    assert groups['s0'] == 1 and groups['s19'] == 10
