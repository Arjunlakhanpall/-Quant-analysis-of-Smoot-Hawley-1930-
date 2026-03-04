# Data Sources (1925–1935)

For **replicable research**, replace the synthetic series with real data. Suggested sources:

## Macroeconomic (US)

| Variable | Source | Notes |
|----------|--------|------|
| GDP | NBER Macrohistory, FRED (GDPC1 if long series) | Annual or quarterly |
| Industrial Production | FRED INDPRO (or NBER) | Monthly from 1919 |
| Imports / Exports | NBER, Census (Historical Statistics of the US) | Trade value or volume |
| Unemployment | NBER, BLS historical | Annual or monthly |

## Market

| Variable | Source |
|----------|--------|
| Dow Jones | Yahoo Finance (^DJI), NBER, Global Financial Data |

## Optional

- Global trade volume (League of Nations / historical reconstructions).
- Trade of major partners: Canada, UK, Germany (for robustness / comparison with lower-tariff countries).

## Preparation Checklist

- Align frequency (monthly vs annual).
- Create **Post_1930** = 1 after June 1930, else 0.
- Create log returns for Dow; YoY % changes for macro levels.
- Save as `data/macro_1925_1935.csv` and `data/dow_1925_1935.csv` (see `src/data_prep.py` for expected column names).
