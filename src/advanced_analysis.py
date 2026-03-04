"""
Advanced econometric methods for Smoot-Hawley / Great Depression analysis.
- CUSUM stability test (recursive residuals)
- Newey-West HAC standard errors
- VAR + Granger causality + impulse response
- Placebo event study (fake event date)
- Difference-in-differences (treatment vs control series)
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Optional, Tuple
import warnings

try:
    import statsmodels.api as sm
    from statsmodels.regression.linear_model import OLS
    from statsmodels.stats.diagnostic import recursive_olsresiduals
    from statsmodels.tsa.api import VAR
    from statsmodels.tsa.vector_ar.irf import IRAnalysis
except ImportError:
    sm = None


def cusum_test(y: pd.Series, X: pd.DataFrame, alpha: float = 0.05) -> dict:
    """
    CUSUM test for parameter stability (Brown-Durbin-Evans).
    H0: coefficients are stable over time.
    Returns dict with recursive residuals, CUSUM, and whether test rejects at alpha.
    """
    if sm is None:
        return {"error": "statsmodels required"}
    X_const = sm.add_constant(X)
    model = OLS(y, X_const).fit()
    try:
        # recursive_olsresiduals returns: rresid, rparams, rypred, rresid_standardized,
        # rresid_scaled, rcusum, rcusumci (confidence interval for CUSUM)
        res = recursive_olsresiduals(model, alpha=alpha)
        rec_resid = res[0]
        cusum = np.asarray(res[5])
        rcusumci = res[6]  # shape (n, 2) for lower, upper
        band_low = rcusumci[:, 0] if rcusumci.ndim >= 2 else rcusumci
        band_upp = rcusumci[:, 1] if rcusumci.ndim >= 2 else rcusumci
        rejects = np.any(cusum <= band_low) or np.any(cusum >= band_upp)
        return {
            "recursive_residuals": rec_resid,
            "cusum": cusum,
            "band_lower": band_low,
            "band_upper": band_upp,
            "rejects_stability": rejects,
            "alpha": alpha,
        }
    except Exception as e:
        return {"error": str(e), "rejects_stability": None}


def ols_hac(
    y: pd.Series,
    X: pd.DataFrame,
    maxlags: Optional[int] = None,
) -> "sm.regression.linear_model.RegressionResultsWrapper":
    """
    OLS with Newey-West HAC standard errors (robust to autocorrelation and heteroskedasticity).
    """
    if sm is None:
        raise ImportError("statsmodels required")
    X_const = sm.add_constant(X)
    model = OLS(y, X_const)
    # maxlags: rule of thumb T^(1/4) if None
    if maxlags is None:
        maxlags = int(len(y) ** 0.25)
    return model.fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})


def var_granger_irf(
    data: pd.DataFrame,
    variables: list,
    maxlags: int = 3,
    irf_periods: int = 12,
) -> dict:
    """
    Fit VAR on selected variables; run Granger causality and (optionally) impulse response.
    data: DataFrame with DatetimeIndex; variables: list of column names.
    """
    if sm is None:
        return {"error": "statsmodels required"}
    df = data[variables].dropna()
    if len(df) < maxlags + 10:
        return {"error": "Insufficient observations for VAR"}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        var = VAR(df)
        var_fit = var.fit(maxlags=maxlags)
    # Granger: for each pair (cause -> caused)
    granger = {}
    for cause in variables:
        for caused in variables:
            if cause == caused:
                continue
            try:
                test = var_fit.test_causality(caused, cause, kind="f")
                granger[f"{cause} -> {caused}"] = {"pvalue": test.pvalue, "reject": test.pvalue < 0.05}
            except Exception:
                pass
    # Impulse response (orthogonalized, variable order = variables)
    try:
        irf = var_fit.irf(irf_periods)
        irf_vals = {v: irf.irfs[:, i] for i, v in enumerate(variables)}
    except Exception as e:
        irf_vals = {"error": str(e)}
    return {
        "var_model": var_fit,
        "granger": granger,
        "irf": irf_vals,
        "irf_periods": irf_periods,
    }


def placebo_event_study(
    returns: pd.Series,
    event_date: str,
    window_months: int = 6,
) -> Tuple[float, float, pd.Series]:
    """
    Event study around a (possibly placebo) event date.
    Returns: mean return in window, volatility in window, series of returns in window.
    """
    event = pd.Timestamp(event_date)
    start = event - pd.DateOffset(months=window_months)
    end = event + pd.DateOffset(months=window_months)
    r = returns.loc[(returns.index >= start) & (returns.index <= end)]
    return r.mean(), r.std(), r


def did_estimate(
    df: pd.DataFrame,
    outcome: str,
    treat_dummy: str,
    post_dummy: str,
    control_vars: Optional[list] = None,
) -> "sm.regression.linear_model.RegressionResultsWrapper":
    """
    Difference-in-differences: outcome ~ treat_dummy + post_dummy + treat_dummy * post_dummy [+ controls].
    DiD coefficient = interaction term (effect of treatment in post period).
    """
    if sm is None:
        raise ImportError("statsmodels required")
    df = df.copy().reset_index(drop=True)
    df["_did"] = df[treat_dummy].astype(float) * df[post_dummy].astype(float)
    X_cols = [treat_dummy, post_dummy, "_did"]
    if control_vars:
        X_cols = X_cols + control_vars
    X = df[X_cols].dropna(how="any")
    y = df.loc[X.index, outcome]
    X = sm.add_constant(X)
    return OLS(y, X).fit()
