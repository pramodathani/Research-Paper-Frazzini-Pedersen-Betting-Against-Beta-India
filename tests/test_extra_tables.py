"""Tests of the extra tables on a made-up market."""

import numpy as np
import pandas as pd

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.extra_tables import (
    ExtraTables,
)
from tests.test_end_to_end import make_study


def make_tables():
    study, _ = make_study(shares=60, years=9)
    return ExtraTables(study), study


def test_calendar_years_compound_the_months():
    tables, _ = make_tables()
    years = tables.calendar_years()
    series = tables.bab_series()
    first_year = series.index[0].year
    expected = (1 + series[series.index.year == first_year]).prod() - 1
    assert (
        years.loc[first_year, 'BAB'] == np.float64(expected)
        or abs(years.loc[first_year, 'BAB'] - expected) < 1e-12
    )


def test_sub_periods_need_a_year_of_months():
    tables, _ = make_tables()
    series = tables.bab_series()
    result = tables.sub_periods(series, ('2014-01', '2016-01'))
    assert len(result) == 2
    assert (result['months'] >= 12).all()


def test_size_terciles_give_three_rows():
    tables, _ = make_tables()
    assert len(tables.size_terciles('A')) == 3


def test_beta_windows_cover_every_setting():
    tables, _ = make_tables()
    result = tables.beta_windows('A', (12,), (12, 36), (3, 1))
    assert len(result) == 4


def test_stress_is_known_before_the_month_it_is_used_in():
    tables, study = make_tables()
    stress = tables.realised_market_stress()
    assert stress.index[0] > study.dates[0].to_period('M')


def test_vix_stress_is_labelled_by_the_next_month():
    dates = pd.bdate_range('2020-01-01', '2020-03-31')
    vix = pd.Series(np.arange(len(dates), dtype=float), index=dates)
    result = ExtraTables.vix_stress(vix)
    assert result.index[0] == pd.Period('2020-02')
    assert result.iloc[0] == vix[dates.month == 1].iloc[-1]
