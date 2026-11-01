"""Tests of the factor regressions."""

import numpy as np
import pandas as pd
import pytest

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.factor_alphas import (
    FactorAlphas,
)


def make_factors(months=120, seed=0):
    rng = np.random.default_rng(seed)
    index = pd.period_range('2010-01', periods=months, freq='M')
    return pd.DataFrame(
        rng.normal(0, 0.04, (months, 4)),
        index=index,
        columns=['MF', 'SMB', 'HML', 'WML'],
    )


def test_recovers_a_known_alpha_and_loadings():
    factors = make_factors()
    excess = 0.01 + 0.8 * factors['MF'] - 0.3 * factors['HML']
    fit = FactorAlphas(factors).fit(excess, 'ff3')
    assert fit['alpha'] == pytest.approx(0.01, abs=1e-9)
    assert fit['beta_MF'] == pytest.approx(0.8)
    assert fit['beta_HML'] == pytest.approx(-0.3)
    assert fit['beta_SMB'] == pytest.approx(0.0, abs=1e-9)


def test_too_few_months_give_nan():
    factors = make_factors(months=20)
    fit = FactorAlphas(factors).fit(factors['MF'], 'capm')
    assert np.isnan(fit['alpha'])
    assert fit['months'] == 20


def test_unknown_model_is_refused():
    with pytest.raises(ValueError):
        FactorAlphas(make_factors()).fit(make_factors()['MF'], 'x')
