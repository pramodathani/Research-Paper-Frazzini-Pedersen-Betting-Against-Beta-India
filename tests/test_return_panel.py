"""Tests of the return panel."""

import numpy as np
import pandas as pd
import pytest

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.return_panel import (
    ReturnPanel,
)


def make_panel():
    dates = pd.bdate_range('2020-01-01', '2020-03-31')
    rows = []
    for symbol, drift in (('AAA', 0.001), ('BBB', 0.002)):
        for date in dates:
            rows.append(
                {
                    'date': date,
                    'symbol': symbol,
                    'close': 100.0,
                    'traded_value': 1e6,
                    'ret': drift,
                }
            )
    daily = pd.DataFrame(rows)
    daily = daily[~((daily.symbol == 'BBB') & (daily.date.dt.month == 2))]
    market = pd.Series(0.0005, index=dates)
    rf = pd.Series(0.004, index=pd.period_range('2020-01', '2020-03', freq='M'))
    return ReturnPanel(daily, market, rf), dates


def test_monthly_returns_compound_the_days():
    panel, dates = make_panel()
    monthly = panel.monthly_returns()
    january = (dates.month == 1).sum()
    assert monthly.loc[pd.Period('2020-01'), 'AAA'] == pytest.approx(
        1.001**january - 1
    )


def test_a_month_without_trading_is_nan():
    panel, _ = make_panel()
    assert np.isnan(panel.monthly_returns().loc[pd.Period('2020-02'), 'BBB'])


def test_month_ends_are_last_trading_days():
    panel, dates = make_panel()
    ends = panel.month_ends()
    assert ends[0] == dates[dates.month == 1].max()
    assert len(ends) == 3


def test_daily_risk_free_adds_up_to_the_month():
    panel, _ = make_panel()
    january = panel.risk_free[panel.risk_free.index.month == 1]
    assert january.sum() == pytest.approx(0.004)


def test_delisting_stress_charges_a_vanished_share():
    from frazzini_pedersen_betting_against_beta_india.betting_against_beta.delisting_stress import (
        DelistingStress,
    )

    dates = pd.bdate_range('2020-01-01', '2020-12-31')
    rows = []
    for symbol, last in (
        ('LIVE', dates[-1]),
        ('GONE', pd.Timestamp('2020-03-31')),
    ):
        for date in dates[dates <= last]:
            rows.append(
                {
                    'date': date,
                    'symbol': symbol,
                    'close': 100.0,
                    'traded_value': 1e6,
                    'ret': 0.001,
                }
            )
    market = pd.Series(0.0005, index=dates)
    rf = pd.Series(0.004, index=pd.period_range('2020-01', '2020-12', freq='M'))
    panel = ReturnPanel(pd.DataFrame(rows), market, rf)
    stress = DelistingStress(panel)
    gone = stress.vanished()
    assert list(gone['symbol']) == ['GONE']
    assert gone['shock_month'].iloc[0] == pd.Period('2020-04')
    monthly = stress.monthly_returns(-0.3)
    assert monthly.loc[pd.Period('2020-04'), 'GONE'] == pytest.approx(-0.3)
    assert np.isnan(monthly.loc[pd.Period('2020-05'), 'GONE'])
    assert monthly.loc[pd.Period('2020-04'), 'LIVE'] > 0
