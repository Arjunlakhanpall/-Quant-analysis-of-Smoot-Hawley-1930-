"""
Data preparation for Smoot-Hawley / Great Depression analysis (1925-1935).
Produces clean dataset: aligned frequency, log returns, Post_1930 dummy, YoY % changes.
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple

# Default paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_raw_macro(data_dir: Path = None) -> pd.DataFrame:
    """Load raw macroeconomic CSV. Expects columns: date, imports, exports, gdp, ind_prod, unemployment."""
    data_dir = data_dir or DATA_DIR
    path = data_dir / "macro_1925_1935.csv"
    if not path.exists():
        raise FileNotFoundError(f"Place macro data in {path}. See README for variable definitions.")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date").sort_index()


def load_raw_market(data_dir: Path = None) -> pd.DataFrame:
    """Load raw market CSV. Expects columns: date, dow_jones (or close)."""
    data_dir = data_dir or DATA_DIR
    path = data_dir / "dow_1925_1935.csv"
    if not path.exists():
        raise FileNotFoundError(f"Place Dow Jones data in {path}.")
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    col = "dow_jones" if "dow_jones" in df.columns else "close"
    return df[["date", col]].rename(columns={col: "dow_jones"}).set_index("date").sort_index()


def add_post_1930_dummy(df: pd.DataFrame, date_col: str = None) -> pd.DataFrame:
    """Post_1930 = 1 after June 1930, else 0."""
    df = df.copy()
    if date_col:
        dates = pd.to_datetime(df[date_col])
    else:
        dates = df.index if isinstance(df.index, pd.DatetimeIndex) else pd.to_datetime(df.index)
    df["Post_1930"] = (dates >= "1930-06-01").astype(int)
    return df


def add_log_returns(df: pd.DataFrame, columns: list, suffix: str = "_log_return") -> pd.DataFrame:
    """Add log returns for given price/level columns."""
    df = df.copy()
    for col in columns:
        if col not in df.columns:
            continue
        df[col + suffix] = np.log(df[col] / df[col].shift(1))
    return df


def add_yoy_pct(df: pd.DataFrame, columns: list, freq: str = "AS") -> pd.DataFrame:
    """Add YoY % change. For annual data use freq='AS'; for monthly, resample or use 12-period diff."""
    df = df.copy()
    for col in columns:
        if col not in df.columns:
            continue
        if freq == "AS" or (isinstance(df.index, pd.DatetimeIndex) and df.index.freq == "AS"):
            df[col + "_yoy"] = df[col].pct_change(periods=1) * 100
        else:
            # monthly: 12-period change
            df[col + "_yoy"] = df[col].pct_change(periods=12) * 100
    return df


def prepare_analysis_dataset(
    macro_path: Path = None,
    market_path: Path = None,
    data_dir: Path = None,
) -> pd.DataFrame:
    """
    Build single analysis dataset: macro + market, Post_1930 dummy,
    log returns for Dow, YoY for macro variables. Aligns to monthly or annual.
    """
    data_dir = data_dir or DATA_DIR
    macro_path = macro_path or data_dir / "macro_1925_1935.csv"
    market_path = market_path or data_dir / "dow_1925_1935.csv"

    if not macro_path.exists():
        raise FileNotFoundError(f"Macro data required at {macro_path}")

    macro = load_raw_macro(data_dir) if macro_path.exists() else pd.DataFrame()
    if macro_path.exists():
        macro = add_post_1930_dummy(macro)
        level_cols = [c for c in ["imports", "exports", "gdp", "ind_prod"] if c in macro.columns]
        macro = add_yoy_pct(macro, level_cols)

    if market_path.exists():
        market = load_raw_market(data_dir)
        market = add_log_returns(market, ["dow_jones"])
        market["dow_volatility"] = market["dow_jones_log_return"].rolling(12, min_periods=1).std()
        if not macro.empty and isinstance(macro.index, pd.DatetimeIndex):
            combined = macro.join(market, how="outer").sort_index()
            combined["Post_1930"] = (combined.index >= pd.Timestamp("1930-06-01")).astype(int)
            return combined
        return add_post_1930_dummy(market)

    return macro.sort_index()


def generate_synthetic_data(
    start: str = "1925-01-01",
    end: str = "1935-12-31",
    freq: str = "MS",
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate synthetic macro and market series for 1925-1935 with a structural break in 1930.
    For demonstration only; replace with real data for actual research.
    """
    np.random.seed(seed)
    dates = pd.date_range(start=start, end=end, freq=freq)
    n = len(dates)
    post = (dates >= "1930-06-01").astype(int)

    # Trend + break: levels fall after 1930
    t = np.arange(n, dtype=float)
    break_drop = -0.4 * post * (t - np.where(post)[0].min() if post.any() else 0)
    trend = -0.002 * t + 0.02 * np.sin(t / 6)
    gdp = 100 * np.exp(np.cumsum(0.001 + trend + break_drop * 0.1 + np.random.normal(0, 0.01, n)))
    ind_prod = 80 * np.exp(np.cumsum(0.0005 + trend * 1.2 + break_drop * 0.15 + np.random.normal(0, 0.012, n)))
    imports = 30 * np.exp(np.cumsum(-0.001 + trend * 0.8 + break_drop * 0.2 + np.random.normal(0, 0.02, n)))
    exports = 28 * np.exp(np.cumsum(-0.0015 + trend * 0.9 + break_drop * 0.25 + np.random.normal(0, 0.02, n)))
    unemployment = np.clip(3 + 0.05 * t + 8 * post * (1 - np.exp(-(t - np.where(post)[0].min()) / 24)) + np.random.normal(0, 0.5, n), 0, 30)

    macro = pd.DataFrame(
        {
            "date": dates,
            "gdp": gdp,
            "ind_prod": ind_prod,
            "imports": imports,
            "exports": exports,
            "unemployment": unemployment,
        }
    )

    # Dow: level drop and volatility increase post-1930
    dow_level = 300 * np.exp(np.cumsum(-0.002 + 0.015 * post + np.random.normal(0, 0.04 + 0.02 * post, n)))
    market = pd.DataFrame({"date": dates, "dow_jones": dow_level})

    return macro, market


def generate_control_series(
    dates: pd.DatetimeIndex,
    seed: int = 123,
) -> pd.DataFrame:
    """
    Generate a synthetic 'control' series (e.g. rest-of-world trade) with NO structural break in 1930.
    Same trend/volatility as pre-1930 but no post-1930 drop. For DiD robustness.
    """
    np.random.seed(seed)
    n = len(dates)
    t = np.arange(n, dtype=float)
    trend = -0.002 * t + 0.02 * np.sin(t / 6)
    # No post dummy - smooth continuation
    control_imports = 28 * np.exp(np.cumsum(-0.001 + trend * 0.8 + np.random.normal(0, 0.02, n)))
    control_exports = 26 * np.exp(np.cumsum(-0.0015 + trend * 0.9 + np.random.normal(0, 0.02, n)))
    return pd.DataFrame(
        {"date": dates, "control_imports": control_imports, "control_exports": control_exports}
    )
