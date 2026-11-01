"""Tests of the strategy runner's futures roll charge."""

import pandas as pd
import pytest
from data_and_analytics.backtesting.costs.futures_costs import FuturesCosts

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.strategy_runner import (
    StrategyRunner,
)


def make_runner():
    months = pd.period_range('2020-01', periods=4, freq='M')
    returns = pd.DataFrame({'A': 0.0, 'B': 0.0}, index=months)
    rf = pd.Series(0.0, index=months)
    return StrategyRunner(returns, rf, None, impact_cost=0.001), months


def test_a_position_kept_pays_a_sell_and_a_buy_each_month():
    runner, months = make_runner()
    weights = pd.DataFrame({'A': 1.2, 'B': -0.8}, index=months)
    cost = runner.roll_cost(weights, pd.Series(0.0, index=months), 0.001)
    model = FuturesCosts(0.001)
    assert cost.iloc[1] == pytest.approx(
        2.0 * (model.buy_rate() + model.sell_rate())
    )


def test_traded_notional_is_not_rolled_again():
    runner, months = make_runner()
    weights = pd.DataFrame({'A': 1.0, 'B': -1.0}, index=months)
    cost = runner.roll_cost(weights, pd.Series(2.0, index=months), 0.001)
    assert (cost == 0).all()


def test_futures_runs_cost_more_than_without_roll():
    runner, months = make_runner()
    weights = pd.DataFrame({'A': 1.0, 'B': -1.0}, index=months)
    run = runner.run(weights, 'futures', roll_impact=0.001)
    model = FuturesCosts(0.001)
    rebalance_only = run['cost'] - runner.roll_cost(
        weights, run['turnover'], 0.001
    )
    assert run['cost'].iloc[2] > rebalance_only.iloc[2]
    assert run['cost'].iloc[2] == pytest.approx(
        2.0 * (model.buy_rate() + model.sell_rate())
    )


def test_no_roll_without_a_roll_impact():
    runner, months = make_runner()
    weights = pd.DataFrame({'A': 1.0, 'B': -1.0}, index=months)
    run = runner.run(weights, 'futures')
    assert run['cost'].iloc[2] == pytest.approx(0.0, abs=1e-12)
