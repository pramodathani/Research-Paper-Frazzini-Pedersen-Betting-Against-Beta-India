"""Alphas and factor loadings with Newey-West standard errors."""

import math
from typing import ClassVar

import pandas as pd
import statsmodels.api as sm


class FactorAlphas:
    """Regresses monthly excess returns on the Indian factor models.

    The factors come from the IIMA library: MF (market excess return), SMB,
    HML and WML. The CAPM uses MF; the three-factor model adds SMB and HML;
    the four-factor model adds WML. t-statistics use Newey-West standard
    errors with a fixed number of lags.

    Attributes:
        factors: Monthly factor returns, decimals, by month.
        lags: The Newey-West lags.
    """

    MODELS: ClassVar[dict[str, list[str]]] = {
        'capm': ['MF'],
        'ff3': ['MF', 'SMB', 'HML'],
        'carhart': ['MF', 'SMB', 'HML', 'WML'],
    }

    def __init__(self, factors: pd.DataFrame, lags: int = 6) -> None:
        """Keeps the factors.

        Args:
            factors (pd.DataFrame): Columns MF, SMB, HML and WML by month.
            lags (int): The Newey-West lags.

        Returns:
            None.
        """
        self.factors = factors
        self.lags = lags

    def fit(self, excess: pd.Series, model: str) -> dict[str, float]:
        """Fits one model.

        Args:
            excess (pd.Series): Monthly excess returns by month.
            model (str): 'capm', 'ff3' or 'carhart'.

        Returns:
            dict[str, float]: alpha, alpha_t, the loading on each factor
                (named by factor) and months used; NaN with fewer than 24
                common months.

        Raises:
            ValueError: The model is unknown.
        """
        if model not in self.MODELS:
            raise ValueError(f'unknown model: {model}')
        names = self.MODELS[model]
        joined = pd.concat(
            [excess.rename('y'), self.factors[names]], axis=1, join='inner'
        ).dropna()
        result = {'alpha': math.nan, 'alpha_t': math.nan, 'months': len(joined)}
        for name in names:
            result[f'beta_{name}'] = math.nan
        if len(joined) < 24:
            return result
        design = sm.add_constant(joined[names])
        fitted = sm.OLS(joined['y'], design).fit(
            cov_type='HAC', cov_kwds={'maxlags': self.lags}
        )
        result['alpha'] = float(fitted.params['const'])
        result['alpha_t'] = float(fitted.tvalues['const'])
        for name in names:
            result[f'beta_{name}'] = float(fitted.params[name])
        return result
