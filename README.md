# Smoot–Hawley Tariff Act & the Great Depression: A Quantitative Analysis

A **quant portfolio project** that tests whether the Smoot–Hawley Tariff Act (June 1930) amplified the Great Depression through trade contraction, structural breaks, and market reactions—using econometric and time-series methods.

---

## Table of Contents

- [Overview](#overview)
- [Research Question & Hypotheses](#research-question--hypotheses)
- [Historical & Theoretical Foundation](#historical--theoretical-foundation)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Data](#data)
- [How to Run](#how-to-run)
- [Run on Google Colab](#run-on-google-colab)
- [Methodology Summary](#methodology-summary)
- [File Descriptions](#file-descriptions)
- [Outputs & Deliverables](#outputs--deliverables)
- [Interpreting Results](#interpreting-results)
- [Data Sources for Real Research](#data-sources-for-real-research)
- [Optional Extensions](#optional-extensions)
- [How This Positions You](#how-this-positions-you)
- [References & Further Reading](#references--further-reading)
- [License & Contact](#license--contact)

---

## Overview

This repository contains a **complete, reproducible analysis** of the link between the Smoot–Hawley Tariff Act and the Great Depression. It combines:

- **Data preparation** (macro + market, 1925–1935)
- **Exploratory data analysis** (trade trends, pre vs post 1930, volatility)
- **Econometric testing** (structural break, regression, event study)
- **Causality & robustness** (Granger causality, variance shift)
- **Advanced (Section 8):** CUSUM stability test, Newey–West HAC standard errors, VAR + Granger + impulse response, placebo event study, difference-in-differences (treatment vs synthetic control)

The project can be run with **synthetic data** (for demo) or **real historical data** (see [Data](#data) and [Data Sources](#data-sources-for-real-research)).

---

## Research Question & Hypotheses

### Primary research question

**Did the Smoot–Hawley Tariff Act amplify the Great Depression?**

Supporting questions:

- Did trade contraction significantly impact GDP and industrial output?
- Did markets anticipate or react to tariff implementation?
- Was there a structural break in trade after 1930?

### Testable hypotheses

| ID   | Hypothesis |
|------|------------|
| **H1** | Trade volume declined significantly after June 1930. |
| **H2** | Industrial production decline correlates with trade contraction. |
| **H3** | Stock market volatility increased post-enactment. |

### Economic transmission channel

**Tariff ↑ → Imports ↓ → Retaliation ↑ → Exports ↓ → Output ↓ → Unemployment ↑**

The analysis tests whether this channel shows up in the data as a **regime change** around June 1930.

---

## Historical & Theoretical Foundation

- **Post–WWI:** Agricultural overproduction; protectionist political climate in the US and abroad.
- **Policy:** President Herbert Hoover signed the Smoot–Hawley Tariff Act in **June 1930**, raising tariffs on thousands of goods.
- **International retaliation:** Trading partners (e.g. Canada, UK) raised their own tariffs; global trade collapsed.
- **Collapse in global trade:** The project asks whether 1930 represents a **structural break** and whether **trade** is associated with **output** and **market volatility**.

The discussion section in the notebook addresses: Did tariffs **cause** the trade collapse, **amplify** an existing one, or were they largely **reactive**?

---

## Project Structure

```
Quant/
├── README.md                          # This file (A–Z documentation)
├── requirements.txt                  # Python dependencies
├── run_analysis.py                   # One-shot script to run full analysis
│
├── data/                             # Data directory
│   ├── macro_1925_1935.csv           # US macro (or synthetic)
│   └── dow_1925_1935.csv             # Dow Jones (or synthetic)
│
├── notebooks/
│   ├── smoot_hawley_analysis.ipynb   # Main analysis notebook
│   └── eda_output.png                # Generated EDA plots (after run)
│
├── src/
│   ├── data_prep.py                  # Data loading, Post_1930, returns, YoY, control series
│   └── advanced_analysis.py          # CUSUM, HAC, VAR, placebo, DiD
│
├── scripts/
│   └── generate_demo_data.py        # Write synthetic data to data/
│
└── docs/
    └── data_sources.md               # Data sources for real research
```

---

## Prerequisites

- **Python:** 3.9 or higher (tested on 3.11, 3.13)
- **OS:** Windows, macOS, or Linux
- **Optional:** Jupyter (for interactive notebook); otherwise use `run_analysis.py`

---

## Installation

### 1. Clone or download the project

```bash
cd path/to/Quant
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Generate demo data

If `data/macro_1925_1935.csv` and `data/dow_1925_1935.csv` do not exist, the **notebook** will generate synthetic data automatically. To pre-generate via script:

```bash
python scripts/generate_demo_data.py
```

---

## Data

### Variables (1925–1935)

| Category    | Variables |
|------------|-----------|
| **Macro**  | US imports, exports, GDP, industrial production, unemployment |
| **Market** | Dow Jones index, log returns, 12-month rolling volatility |
| **Constructed** | `Post_1930` (1 after June 1930, else 0), YoY % changes for macro series |

### Expected CSV format

- **`data/macro_1925_1935.csv`**  
  Columns: `date`, `imports`, `exports`, `gdp`, `ind_prod`, `unemployment`  
  `date` in a standard format (e.g. `YYYY-MM-DD`).

- **`data/dow_1925_1935.csv`**  
  Columns: `date`, `dow_jones` (or `close`).

### Synthetic vs real data

- **Synthetic:** Used for demonstration; generated by `generate_synthetic_data()` in `src/data_prep.py` (structural break and volatility increase post-1930).  
- **Real:** For actual research, replace the CSVs with historical series; see [Data Sources for Real Research](#data-sources-for-real-research) and `docs/data_sources.md`.

---

## How to Run

### Option A: Interactive notebook (recommended for exploration)

```bash
jupyter notebook notebooks/smoot_hawley_analysis.ipynb
```

Or with Jupyter Lab:

```bash
jupyter lab notebooks/smoot_hawley_analysis.ipynb
```

Run all cells from top to bottom. If the data files are missing, the first code block will create synthetic data in `data/`.

### Option B: One-shot script (reproducible run + saved plots)

From the **project root** (`Quant/`):

```bash
python run_analysis.py
```

This will:

- Load or generate data
- Print EDA (means, variances, pre vs post 1930)
- Run Chow test, regressions, and Granger causality
- Save EDA plots to `notebooks/eda_output.png`

### Run on Google Colab

1. **Upload the project** to Google Drive (zip the `Quant` folder so it includes `src/data_prep.py` and `src/advanced_analysis.py`, plus `data/`, `notebooks/`; upload, then unzip so you have `My Drive/Quant/` with `src/`, `data/`, `notebooks/` inside).
2. Open **[colab.research.google.com](https://colab.research.google.com)** → **File → Open notebook → Google Drive** → open `Quant/notebooks/smoot_hawley_analysis.ipynb`.
3. **Run the first code cell.** It will mount Drive (approve when prompted), set the project root to `/content/drive/MyDrive/Quant`, and install dependencies. If your folder is elsewhere (e.g. `My Drive/Projects/Quant`), edit the `ROOT = Path(...)` line in that cell.
4. **Run all** (or run each cell in order). The notebook runs Sections 1–7 and **Section 8 (Advanced)**. If `data/` has no CSVs, synthetic data will be generated.

**If you use GitHub instead of Drive:** open the notebook from GitHub in Colab, then replace the first code cell with the “clone repo” version in **[COLAB.md](COLAB.md)** so Colab has the full repo (including `src/advanced_analysis.py`).

Full step-by-step and troubleshooting: **[COLAB.md](COLAB.md)**.

---

## Methodology Summary

| Step | Content |
|------|--------|
| **1. Data prep** | Load macro + market CSVs; add `Post_1930`, log returns, YoY % changes, rolling volatility. |
| **2. EDA** | Trade and industrial production trends; Dow level and volatility; pre vs post 1930 means/variances and % contraction. |
| **3. Structural break** | Chow test at June 1930; variance shift (residual variance post/pre); rolling regression (e.g. GDP on imports). |
| **4. Regression** | GDP and industrial production on imports, exports, `Post_1930`. |
| **5. Event study** | Dow returns and volatility around June 1930. |
| **6. Causality** | Granger causality (e.g. imports → GDP). |
| **7. Discussion** | Interpret cause vs amplification vs reactive policy; link to modern trade wars. |
| **8. Advanced** | CUSUM (parameter stability); Newey–West HAC SEs; VAR + Granger + IRF; placebo event (non-event date); DiD (US vs synthetic control). |

---

## File Descriptions

| File | Purpose |
|------|--------|
| `README.md` | Full project documentation (this file). |
| `requirements.txt` | Python package list (pandas, numpy, scipy, matplotlib, seaborn, statsmodels, jupyter). |
| `run_analysis.py` | Runs full pipeline and saves EDA figure; no Jupyter required. |
| `notebooks/smoot_hawley_analysis.ipynb` | Main analysis: hypotheses, data, EDA, econometrics, discussion. |
| `src/data_prep.py` | `prepare_analysis_dataset()`, `generate_synthetic_data()`, `generate_control_series()` (for DiD), loaders, Post_1930, returns, YoY. |
| `src/advanced_analysis.py` | CUSUM test, OLS with Newey–West HAC, VAR + Granger + IRF, placebo event study, DiD estimation. |
| `scripts/generate_demo_data.py` | Writes synthetic macro and Dow CSVs to `data/`. |
| `docs/data_sources.md` | Suggested sources (NBER, FRED, etc.) and prep checklist for real data. |

---

## Outputs & Deliverables

- **Notebook:** Clean, sectioned analysis with hypothesis, EDA, structural break tests, regressions, event study, Granger, and discussion.
- **Figures:** EDA plots (trade, industrial production, Dow, volatility) with June 1930 vertical line; saved as `notebooks/eda_output.png` when using `run_analysis.py`.
- **Console/notebook output:** Descriptive statistics, Chow test (F, p-value), OLS regression tables, Granger p-values.
- **Discussion template:** Section 7 in the notebook for your narrative (cause vs amplification, reactive vs destructive, modern parallels).

---

## Interpreting Results

- **Chow test:** Rejecting H0 (no break) at 5% suggests a significant regime change at June 1930. With synthetic data, the result is illustrative only.
- **Regressions:** Significant coefficients on imports/exports support a link between trade and output; significant `Post_1930` captures a level shift after the tariff.
- **Event study:** Negative abnormal returns or higher volatility around June 1930 support market reaction to the policy.
- **Granger:** Low p-values for “imports → GDP” suggest trade helps predict output (consistent with the transmission channel).

Always interpret in light of **real data** and **identification** (e.g. confounding factors, endogeneity).

---

## Data Sources for Real Research

For replicable research, replace synthetic data with historical series. Summary:

| Variable | Suggested source |
|----------|-------------------|
| GDP | NBER Macrohistory, FRED (e.g. GDPC1 if long series) |
| Industrial production | FRED INDPRO, NBER |
| Imports / Exports | NBER, Census (Historical Statistics of the United States) |
| Unemployment | NBER, BLS historical |
| Dow Jones | Yahoo Finance (^DJI), NBER, Global Financial Data |

See **`docs/data_sources.md`** for details and a preparation checklist (frequency alignment, column names, `Post_1930`, log returns, YoY).

---

## Optional Extensions

- **FRED/yfinance:** Use `fredapi` or `yfinance` to pull series programmatically (see commented lines in `requirements.txt`).
- **More countries:** Compare with a country with lower tariff escalation for robustness.
- **Lagged trade effects:** Add lags of exports/imports in regressions.
- **Academic format:** Turn the notebook narrative into an abstract, literature review, methodology, results, and policy implications.

---

## How This Positions You

- **Quant roles:** Macro regime thinking, structural break analysis, time-series modeling, policy shock propagation.
- **MSc / applied stats:** Applied econometrics, hypothesis-driven empirical work.
- **Interviews:** Clear story on how policy shocks propagate, how trade wars affect markets, and how structural breaks change risk regimes.

---

## References & Further Reading

- Smoot–Hawley Tariff Act (1930); Great Depression history and trade collapse.
- NBER Macrohistory Database; FRED (Federal Reserve Economic Data).
- Structural break tests (Chow, CUSUM); event study methods; Granger causality.

---

## License & Contact

- **License:** Use and adapt as needed for portfolio and academic work; cite data sources when using real data.
- **Contact:** Add your name, email, or GitHub profile here if you wish.

---

*End of README — project documentation A–Z.*
