"""Tests of the hand-off package's target script on a made-up market."""

import datetime
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SCRIPT = Path(
    'handoff/bab-low-beta-india/skills/bab-low-beta-india/scripts/build_targets.py'
)


def load_module():
    spec = importlib.util.spec_from_file_location('build_targets', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_market(shares=40, years=7, seed=2):
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range('2019-12-02', periods=years * 252)
    market = pd.Series(rng.normal(0.0004, 0.01, len(dates)), index=dates)
    true_beta = np.linspace(0.3, 1.7, shares)
    rows = []
    for number, beta in enumerate(true_beta):
        returns = beta * market.to_numpy() + rng.normal(0, 0.012, len(dates))
        close = 100 * np.exp(np.cumsum(np.log1p(np.clip(returns, -0.4, 0.9))))
        rows.append(
            pd.DataFrame(
                {
                    'symbol': f'S{number:02d}',
                    'date': dates,
                    'close': close,
                    'volume': 1_000_000 + 50_000 * number,
                }
            )
        )
    prices = pd.concat(rows, ignore_index=True)
    index_prices = pd.DataFrame(
        {'date': dates, 'close': 10_000 * np.exp(np.cumsum(np.log1p(market)))}
    )
    return prices, index_prices, true_beta


def test_targets_are_the_lowest_beta_shares_and_sum_to_one():
    module = load_module()
    prices, index_prices, _ = make_market()
    builder = module.LowBetaTargets(prices, index_prices)
    weights, details = builder.targets(datetime.date(2026, 1, 5))
    assert weights.sum() == pytest.approx(1.0)
    assert len(weights) == round(0.2 * details['ranked'])
    assert all(int(name[1:]) < 15 for name in weights.index)
    assert details['average_beta'] < 0.8


def test_the_targets_do_not_see_prices_after_the_month_end():
    module = load_module()
    prices, index_prices, _ = make_market()
    as_of = datetime.date(2026, 1, 5)
    first, _ = module.LowBetaTargets(prices, index_prices).targets(as_of)
    changed = prices.copy()
    late = pd.to_datetime(changed['date']) > pd.Timestamp('2025-12-31')
    changed.loc[late, 'close'] *= 3.0
    again, _ = module.LowBetaTargets(changed, index_prices).targets(as_of)
    pd.testing.assert_series_equal(first, again)


def test_stale_data_is_refused():
    module = load_module()
    prices, index_prices, _ = make_market()
    cut = pd.Timestamp('2025-12-20')
    builder = module.LowBetaTargets(
        prices[pd.to_datetime(prices['date']) <= cut],
        index_prices[pd.to_datetime(index_prices['date']) <= cut],
    )
    with pytest.raises(ValueError, match='wait for the last prices'):
        builder.targets(datetime.date(2026, 1, 5))


def test_a_bad_adjustment_is_dropped_not_held_against_a_share():
    module = load_module()
    prices, index_prices, _ = make_market()
    broken = prices.copy()
    mask = (broken['symbol'] == 'S05') & (
        pd.to_datetime(broken['date']) >= pd.Timestamp('2025-06-02')
    )
    broken.loc[mask, 'close'] *= 0.1
    builder = module.LowBetaTargets(broken, index_prices)
    _, _, dropped = builder.log_returns()
    assert set(dropped['symbol']) == {'S05'}
    assert len(dropped) == 1
    weights, _ = builder.targets(datetime.date(2026, 1, 5))
    assert weights.sum() == pytest.approx(1.0)


def test_overlay_lifts_beta_to_one_with_a_cap():
    module = load_module()
    prices, index_prices, _ = make_market(shares=20)
    builder = module.LowBetaTargets(prices, index_prices)
    assert builder.overlay(0.8) == pytest.approx(0.25)
    assert builder.overlay(1.2) == 0.0
    assert builder.overlay(0.3) == 1.5


def test_the_script_places_no_orders():
    text = SCRIPT.read_text()
    for word in ('place_order', 'modify_order', 'cancel_order', 'flatten'):
        assert word not in text
