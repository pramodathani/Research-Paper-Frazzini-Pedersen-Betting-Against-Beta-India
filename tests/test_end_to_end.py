"""An end-to-end run on a made-up market, with no files and no network."""

import numpy as np
import pandas as pd
import pytest

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.bab_study import (
    BabStudy,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.decile_table import (
    DecileTable,
)
from frazzini_pedersen_betting_against_beta_india.betting_against_beta.return_panel import (
    ReturnPanel,
)


def make_study(shares=60, years=9, seed=5):
    """Shares with true betas from 0.3 to 1.7 and a market with noise."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range('2010-01-01', periods=years * 250)
    market = pd.Series(rng.normal(0.0004, 0.01, len(dates)), index=dates)
    betas = np.linspace(0.3, 1.7, shares)
    rows = []
    for number, beta in enumerate(betas):
        noise = rng.normal(0, 0.012, len(dates))
        returns = beta * market.to_numpy() + noise
        rows.append(
            pd.DataFrame(
                {
                    'date': dates,
                    'symbol': f'S{number:02d}',
                    'close': 100.0,
                    'traded_value': 1e7 * (1 + number % 7),
                    'ret': returns,
                }
            )
        )
    daily = pd.concat(rows, ignore_index=True)
    months = pd.period_range('2010-01', periods=years * 12 + 3, freq='M')
    rf = pd.Series(0.004, index=months)
    panel = ReturnPanel(daily, market, rf)
    monthly = panel.monthly_market()
    factors = pd.DataFrame(
        {
            'MF': monthly - 0.004,
            'SMB': rng.normal(0, 0.02, len(monthly)),
            'HML': rng.normal(0, 0.02, len(monthly)),
            'WML': rng.normal(0, 0.02, len(monthly)),
        },
        index=monthly.index,
    )
    return BabStudy(panel, factors, None, '2013-12-01'), betas


def test_estimated_betas_are_ordered_like_the_true_betas():
    study, true = make_study()
    betas = study.betas.beta(12, 36, 1.0)
    last = betas.iloc[-1].dropna()
    assert len(last) == len(true)
    assert last.rank().corr(pd.Series(true, index=last.index).rank()) > 0.95


def test_decile_returns_rise_with_beta_and_bab_is_beta_neutral():
    study, _ = make_study()
    table, series = DecileTable(study).run(
        'A', 'equal', groups=5, volatility_months=12, correlation_months=36
    )
    capm = table['capm_beta_MF']
    assert capm['P1'] < capm['P3'] < capm['P5']
    assert abs(capm['BAB']) < capm['P5'] - capm['P1']
    assert len(series['BAB']) > 50


def test_costs_lower_the_return():
    study, _ = make_study()
    table, _ = DecileTable(study).run(
        'A', 'equal', groups=5, volatility_months=12, correlation_months=36
    )
    assert (
        table.loc['BAB after costs', 'excess_mean']
        < table.loc['BAB', 'excess_mean']
    )


def test_holding_longer_lowers_turnover():
    study, _ = make_study()
    quick, _ = DecileTable(study).run(
        'A', groups=5, volatility_months=12, correlation_months=36
    )
    slow, _ = DecileTable(study).run(
        'A',
        groups=5,
        volatility_months=12,
        correlation_months=36,
        holding_months=6,
    )
    assert slow.loc['BAB', 'turnover'] < quick.loc['BAB', 'turnover']


def test_no_look_ahead_in_formation():
    study, _ = make_study()
    builder = study.builder('A', 12, 36)
    weights, _ = builder.bab()
    assert weights.index[0] > study.dates[0].to_period('M')
