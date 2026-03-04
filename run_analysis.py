"""Run the full Smoot-Hawley analysis (all notebook code)."""
import os
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import matplotlib
matplotlib.use("Agg")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from src.data_prep import prepare_analysis_dataset, generate_synthetic_data, DATA_DIR

print("=" * 60)
print("1. Data")
print("=" * 60)
if not (DATA_DIR / "macro_1925_1935.csv").exists():
    macro, market = generate_synthetic_data()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    macro.to_csv(DATA_DIR / "macro_1925_1935.csv", index=False)
    market.to_csv(DATA_DIR / "dow_1925_1935.csv", index=False)
df = prepare_analysis_dataset(data_dir=DATA_DIR)
df.index = pd.to_datetime(df.index)
df = df.sort_index()
print("Post_1930 dummy: 1 after June 1930.")
print(df.head(10))
print()
print(df.describe())

print("\n" + "=" * 60)
print("2. EDA - Mean before vs after 1930")
print("=" * 60)
pre = df[df["Post_1930"] == 0]
post = df[df["Post_1930"] == 1]
trade_cols = [c for c in ["imports", "exports"] if c in df.columns]
for c in trade_cols + ["ind_prod", "gdp", "dow_volatility"]:
    if c not in df.columns:
        continue
    m_pre, m_post = pre[c].mean(), post[c].mean()
    pct = (m_post - m_pre) / m_pre * 100 if m_pre != 0 else 0
    print(f"  {c}: pre={m_pre:.2f}, post={m_post:.2f}, % chg={pct:.1f}%")
print("Variance (post/pre ratio)")
for c in trade_cols + ["ind_prod", "dow_jones_log_return"]:
    if c not in df.columns:
        continue
    v_pre, v_post = pre[c].var(), post[c].var()
    if v_pre > 0:
        print(f"  {c}: {v_post/v_pre:.2f}")

print("\n" + "=" * 60)
print("3. Structural break (Chow test)")
print("=" * 60)
def chow_test(y, X, break_idx):
    n = len(y)
    if break_idx <= 2 or break_idx >= n - 2:
        return None
    X1, y1 = X.iloc[:break_idx], y.iloc[:break_idx]
    X2, y2 = X.iloc[break_idx:], y.iloc[break_idx:]
    X1, X2, X_all = sm.add_constant(X1), sm.add_constant(X2), sm.add_constant(X)
    m1, m2 = sm.OLS(y1, X1).fit(), sm.OLS(y2, X2).fit()
    m_pooled = sm.OLS(y, X_all).fit()
    RSS_p, RSS_u = m1.ssr + m2.ssr, m_pooled.ssr
    k = X.shape[1] + 1
    F = (RSS_u - RSS_p) / RSS_p * (n - 2 * k) / k
    from scipy.stats import f as f_dist
    pval = 1 - f_dist.cdf(F, k, n - 2 * k)
    return {"F": F, "pvalue": pval}

work = df.dropna(subset=["gdp", "imports", "exports", "Post_1930"])
if len(work) > 10:
    y, X = work["gdp"], work[["imports", "exports", "Post_1930"]]
    break_idx = max(1, (work.index < "1930-06-01").sum())
    chow = chow_test(y, X, break_idx)
    if chow:
        print(f"Chow test (break at Jun 1930): F = {chow['F']:.3f}, p-value = {chow['pvalue']:.4f}")
        print("Reject H0 (no break) at 5%:", chow["pvalue"] < 0.05)
else:
    print("Insufficient data for Chow test.")

print("\n" + "=" * 60)
print("4. Regression: GDP on Imports, Exports, Post_1930")
print("=" * 60)
work = df.dropna(subset=["gdp", "imports", "exports", "Post_1930"])
if len(work) > 5:
    m1 = sm.OLS(work["gdp"], sm.add_constant(work[["imports", "exports", "Post_1930"]])).fit()
    print(m1.summary())

print("\n" + "=" * 60)
print("5. Regression: Industrial Production on Imports, Exports, Post_1930")
print("=" * 60)
work = df.dropna(subset=["ind_prod", "imports", "exports", "Post_1930"])
if len(work) > 5:
    m2 = sm.OLS(work["ind_prod"], sm.add_constant(work[["imports", "exports", "Post_1930"]])).fit()
    print(m2.summary())

print("\n" + "=" * 60)
print("6. Granger causality (imports -> gdp)")
print("=" * 60)
from statsmodels.tsa.stattools import grangercausalitytests
gc_data = df[["gdp", "imports"]].dropna()
if len(gc_data) > 24:
    try:
        out = grangercausalitytests(gc_data[["gdp", "imports"]], maxlag=3, verbose=False)
        for lag, val in out.items():
            # val can be (ssr_ftest, ssr_chi2, lrt, params_ftest) or (dict, dict) in newer statsmodels
            if isinstance(val, (list, tuple)):
                if len(val) >= 4:
                    pval = val[3][1]  # params_ftest = (f, pval, ...)
                elif len(val) >= 2 and isinstance(val[1], (list, tuple)):
                    pval = val[1][1]
                else:
                    pval = None
            else:
                pval = None
            if pval is not None:
                print(f"  Lag {lag}: F_pval = {pval:.4f}")
    except Exception as e:
        print("Granger:", e)
else:
    print("Insufficient observations.")

# Save EDA plots
sns.set_style("whitegrid")
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
if "imports" in df.columns and "exports" in df.columns:
    axes[0, 0].plot(df.index, df["imports"], label="Imports")
    axes[0, 0].plot(df.index, df["exports"], label="Exports")
    axes[0, 0].axvline(pd.Timestamp("1930-06-01"), color="red", linestyle="--", alpha=0.7)
    axes[0, 0].set_title("Trade (1925–1935)")
    axes[0, 0].legend()
if "ind_prod" in df.columns:
    axes[0, 1].plot(df.index, df["ind_prod"], color="green")
    axes[0, 1].axvline(pd.Timestamp("1930-06-01"), color="red", linestyle="--", alpha=0.7)
    axes[0, 1].set_title("Industrial Production")
if "dow_jones" in df.columns:
    axes[1, 0].plot(df.index, df["dow_jones"], color="blue")
    axes[1, 0].axvline(pd.Timestamp("1930-06-01"), color="red", linestyle="--", alpha=0.7)
    axes[1, 0].set_title("Dow Jones")
if "dow_volatility" in df.columns:
    axes[1, 1].plot(df.index, df["dow_volatility"], color="purple")
    axes[1, 1].axvline(pd.Timestamp("1930-06-01"), color="red", linestyle="--", alpha=0.7)
    axes[1, 1].set_title("Market Volatility")
plt.tight_layout()
out_path = ROOT / "notebooks" / "eda_output.png"
fig.savefig(out_path, dpi=100, bbox_inches="tight")
plt.close()
print(f"\nPlots saved to {out_path}")

print("\n" + "=" * 60)
print("Done.")
print("=" * 60)
