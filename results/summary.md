# Results: Betting Against Beta in India

Frazzini and Pedersen (2014), recreated on NSE shares, April 1999 to October 2026. Every number comes from `results/*.csv`, made by `scripts/make_results.py` and `scripts/run_grid.py`. FP page numbers are those of the May 2013 draft in `paper/`. AJVV is Agarwalla, Jacob, Varma and Vasudevan (2014), the earlier Indian study on BSE shares.

## In plain words

1. **The low-beta anomaly is clearly there in India, before costs.**
   - Across all NSE shares, the BAB factor earns 0.78% a month (Newey-West t 3.60, Sharpe 0.77, 331 months).
   - That is about what the paper finds in the US: 0.70%, Sharpe 0.78 (FP Table III, p.41).
   - Alphas fall almost steadily from the lowest-beta decile to the highest, and the highest-beta decile has a significantly negative four-factor alpha.
2. **Most of the gross return comes from small, thinly traded shares and from shorting the highest-beta decile.**
   - In the 500 most traded shares, BAB earns 0.47% a month (t 2.02).
   - In shares with stock futures it earns 0.39% (t 1.59).
   - Within the least-traded third of all NSE shares it earns 1.02%.
3. **After realistic Indian costs, the long-short versions do not survive.**
   - **F&O universe, through stock futures (T1):** the monthly roll and rebalancing take the return to about zero (−0.02% a month).
   - **All NSE (A) and liquid 500 (B), as cash portfolios:** they keep 0.40% (t 1.82) and 0.18% (t 0.78) after delivery costs and a 3.25% a year borrow fee. Neither can actually be built, because India's SLB market lends only a few hundred shares, thinly.
4. **The long-only low-beta portfolios work as low-risk equity, not as a source of extra return.**
   - **L1** (the lowest-beta fifth of the liquid 500) earns the same excess return as the NIFTY 500 TRI over the same 331 months: 0.81% after costs against 0.86% before.
   - It does so with 21% volatility against 24%, a beta of 0.77, a slightly higher Sharpe ratio (0.46 against 0.43) and about the same worst drawdown (−63% against −65%).
   - Its four-factor alpha is 0.27% a month (t 1.99) after costs.
   - From 2006, NSE's own low-volatility indices did better than L1: Sharpe 0.52 to 0.53 against 0.38.
5. **Levering the low-beta portfolio to a beta of 1 with NIFTY futures (L3) does not add alpha after costs.** It raises the return to 1.05% a month but also the volatility, and its CAPM alpha is about zero.

## 1. Beta deciles and BAB, all NSE shares (universe A), equal-weighted (FP Table III; AJVV Table 2)

Returns are in % a month and in excess of the 91-day T-bill. Alphas come from IIMA's Indian factors (market, SMB, HML, WML), which end in December 2025. t-statistics use Newey-West errors with 6 lags.

| | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 | BAB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Excess return | 1.14 | 1.20 | 1.44 | 1.49 | 1.43 | 1.50 | 1.39 | 1.29 | 1.11 | 0.73 | 0.78 |
| NW t | 2.54 | 2.48 | 2.67 | 2.58 | 2.41 | 2.39 | 2.16 | 1.90 | 1.60 | 1.01 | 3.60 |
| CAPM α | 0.47 | 0.41 | 0.57 | 0.54 | 0.42 | 0.42 | 0.23 | 0.08 | -0.14 | -0.69 | 0.78 |
| 3-factor α | 0.39 | 0.29 | 0.42 | 0.38 | 0.22 | 0.19 | -0.02 | -0.21 | -0.42 | -1.01 | 0.83 |
| 4-factor α | 0.50 | 0.48 | 0.60 | 0.61 | 0.42 | 0.42 | 0.18 | 0.01 | -0.15 | -0.68 | 0.80 |
| 4-factor t | 2.54 | 2.98 | 3.95 | 3.75 | 2.96 | 2.55 | 1.27 | 0.10 | -0.90 | -2.69 | 3.62 |
| β ex ante | 0.70 | 0.83 | 0.90 | 0.97 | 1.02 | 1.08 | 1.14 | 1.21 | 1.31 | 1.53 | 0.00 |
| β realised | 0.78 | 0.90 | 1.01 | 1.09 | 1.14 | 1.23 | 1.30 | 1.34 | 1.40 | 1.55 | 0.04 |
| Volatility %/yr | 23.9 | 26.5 | 29.1 | 31.3 | 32.8 | 34.5 | 36.3 | 38.5 | 39.8 | 45.7 | 12.1 |
| Sharpe | 0.57 | 0.54 | 0.59 | 0.57 | 0.53 | 0.52 | 0.46 | 0.40 | 0.33 | 0.19 | 0.77 |
| Worst drawdown % | -65 | -65 | -71 | -73 | -74 | -76 | -76 | -80 | -85 | -95 | -30 |

**Against the paper.**
- **FP US (p.41):**
  - BAB 0.70 (t 7.12), Sharpe 0.78, volatility 10.7%.
  - Alphas fall from P1 0.52 to P10 −0.10 (CAPM).
  - Excess returns are flat across deciles.
- **India:**
  - The shape is the same. Excess returns are flat to falling (1.14 to 0.73), CAPM alpha falls from 0.47 to −0.69, and the Sharpe ratio from 0.57 to 0.19.
  - BAB is about as large, with a lower t because the sample is shorter and more volatile.
  - Realised betas run from 0.78 to 1.55, compressed relative to ex ante (0.70 to 1.53) at the low end, as in the paper.
- **AJVV (BSE, 1998–2013, Table 2 p.18):**
  - BAB 1.70% a month, Sharpe 0.86, long ₹1.32 and short ₹0.91.
  - We get 0.78%, long ₹1.23 and short ₹0.76.
  - The gap is consistent with BSE's many tiny shares, which our ₹2 price floor and 50% trading-days rule exclude, and with our least-traded tercile alone earning 1.02%.
  - Unlike AJVV, our low-beta decile alphas are positive.

### Liquid 500 (universe B), equal-weighted

| | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 | BAB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Excess return | 0.78 | 0.93 | 1.15 | 1.09 | 0.99 | 1.34 | 1.39 | 1.13 | 0.94 | 0.55 | 0.47 |
| NW t | 2.03 | 2.12 | 2.26 | 2.04 | 1.78 | 2.26 | 2.26 | 1.77 | 1.41 | 0.73 | 2.02 |
| CAPM α | 0.16 | 0.18 | 0.32 | 0.19 | 0.02 | 0.27 | 0.23 | -0.07 | -0.39 | -0.98 | 0.58 |
| 3-factor α | 0.12 | 0.12 | 0.23 | 0.08 | -0.13 | 0.10 | -0.02 | -0.30 | -0.62 | -1.19 | 0.63 |
| 4-factor α | 0.31 | 0.33 | 0.45 | 0.36 | 0.17 | 0.38 | 0.24 | 0.06 | -0.25 | -0.53 | 0.53 |
| 4-factor t | 2.02 | 2.20 | 2.48 | 2.27 | 1.17 | 2.20 | 1.33 | 0.38 | -1.40 | -1.64 | 2.25 |
| β ex ante | 0.71 | 0.84 | 0.91 | 0.97 | 1.04 | 1.10 | 1.17 | 1.24 | 1.34 | 1.58 | 0.00 |
| β realised | 0.70 | 0.84 | 0.97 | 1.01 | 1.10 | 1.20 | 1.29 | 1.32 | 1.44 | 1.65 | -0.07 |
| Volatility %/yr | 19.6 | 23.1 | 26.2 | 27.9 | 29.8 | 32.4 | 34.6 | 35.9 | 39.4 | 46.3 | 12.9 |
| Sharpe | 0.47 | 0.49 | 0.53 | 0.47 | 0.40 | 0.50 | 0.48 | 0.38 | 0.29 | 0.14 | 0.44 |
| Worst drawdown % | -61 | -65 | -69 | -78 | -75 | -74 | -74 | -78 | -89 | -97 | -36 |

### All NSE, weighted by traded value (the value-weighted analogue; no market-cap history before 2024)

| | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 | BAB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Excess return | 0.39 | 0.28 | 0.62 | 0.77 | 1.08 | 1.40 | 0.38 | 0.66 | 0.81 | 0.08 | 0.78 |
| NW t | 1.08 | 0.79 | 1.46 | 1.66 | 2.14 | 2.67 | 0.76 | 1.27 | 1.28 | 0.10 | 3.60 |
| CAPM α | -0.12 | -0.30 | -0.09 | 0.01 | 0.30 | 0.57 | -0.65 | -0.39 | -0.38 | -1.44 | 0.78 |
| 3-factor α | -0.16 | -0.37 | -0.04 | -0.06 | 0.19 | 0.54 | -0.76 | -0.52 | -0.36 | -1.52 | 0.83 |
| 4-factor α | -0.06 | -0.23 | -0.11 | 0.21 | 0.22 | 0.63 | -0.54 | -0.25 | -0.10 | -1.09 | 0.80 |
| 4-factor t | -0.24 | -1.07 | -0.47 | 0.94 | 0.66 | 2.04 | -1.31 | -0.98 | -0.31 | -2.33 | 3.62 |
| β ex ante | 0.70 | 0.83 | 0.90 | 0.97 | 1.02 | 1.08 | 1.14 | 1.21 | 1.32 | 1.58 | 0.00 |
| β realised | 0.63 | 0.65 | 0.80 | 0.88 | 0.90 | 0.94 | 1.12 | 1.14 | 1.29 | 1.63 | 0.04 |
| Volatility %/yr | 21.1 | 20.9 | 25.9 | 26.6 | 27.9 | 27.5 | 33.5 | 32.7 | 36.5 | 49.0 | 12.1 |
| Sharpe | 0.22 | 0.16 | 0.29 | 0.35 | 0.47 | 0.61 | 0.13 | 0.24 | 0.27 | 0.02 | 0.77 |
| Worst drawdown % | -70 | -68 | -75 | -68 | -59 | -70 | -86 | -76 | -82 | -100 | -30 |

With traded-value weights, the P1 to P10 alpha pattern is noisy and only P10 is clearly negative. This matches FP Table B9: the low-beta effect is weaker in large shares, and the factor's return comes mostly from the leverage on the low-beta side.

## 2. BAB by universe, before and after costs (FP Table V row)

| | Excess return %/mo | NW t | 4-factor α %/mo | t | Volatility %/yr | Sharpe | Worst drawdown % | Months |
|---|---|---|---|---|---|---|---|---|
| A BAB | 0.78 | 3.60 | 0.80 | 3.62 | 12.1 | 0.77 | -30 | 331 |
| A BAB after costs | 0.40 | 1.82 | 0.42 | 1.89 | 12.1 | 0.39 | -39 | 331 |
| B BAB | 0.47 | 2.02 | 0.53 | 2.25 | 12.9 | 0.44 | -36 | 331 |
| B BAB after costs | 0.18 | 0.78 | 0.24 | 1.02 | 12.9 | 0.17 | -44 | 331 |
| C BAB | 0.39 | 1.59 | 0.44 | 2.44 | 12.8 | 0.36 | -45 | 261 |
| C BAB after costs | -0.02 | -0.07 | 0.04 | 0.20 | 12.9 | -0.02 | -51 | 261 |

**Cost treatment** (the shared engine's Indian costs: brokerage, STT, stamp duty, exchange charges, SEBI fee, GST and impact):
- **A and B, cash portfolios:**
  - Delivery costs on both legs: impact 0.30% a side in A, 0.10% in B.
  - A borrow fee of 3.25% a year on the short leg. That is the median annualised SLB fee across 10,823 SLB contracts traded on month-end days, 2010 to 2026 (`borrow_fee_by_year.csv`). The value-weighted mean is 36%, driven by hard-to-borrow names.
  - Few of these shares can actually be borrowed, so A and B after costs are paper portfolios.
- **C, stock futures:** futures costs on rebalancing plus the monthly roll of every position kept, at 0.05% impact a side. There is no borrow fee.
- **Leverage and turnover:** the BAB legs average ₹1.22 to ₹1.23 long and ₹0.74 to ₹0.76 short (₹1.18 and ₹0.71 in C). Turnover is about 0.42 of capital a month.

## 3. Tradeable portfolios (plan §4.2–4.3)

| | Excess return %/mo | NW t | 4-factor α %/mo | t | Volatility %/yr | Sharpe | Worst drawdown % | Months |
|---|---|---|---|---|---|---|---|---|
| T1 before costs | 0.39 | 1.59 | 0.44 | 2.44 | 12.8 | 0.36 | -45 | 261 |
| T1 after costs | -0.02 | -0.07 | 0.04 | 0.20 | 12.9 | -0.02 | -51 | 261 |
| T2 before costs | 0.46 | 1.49 | 0.54 | 2.37 | 16.5 | 0.33 | -52 | 261 |
| T2 after costs | 0.05 | 0.15 | 0.13 | 0.57 | 16.5 | 0.03 | -60 | 261 |
| L1 before costs | 0.86 | 2.11 | 0.32 | 2.34 | 20.9 | 0.49 | -63 | 331 |
| L1 after costs | 0.81 | 1.99 | 0.27 | 1.99 | 20.9 | 0.46 | -63 | 331 |
| L2 before costs | 0.95 | 2.16 | 0.35 | 2.65 | 22.5 | 0.50 | -66 | 331 |
| L2 after costs | 0.91 | 2.07 | 0.31 | 2.36 | 22.5 | 0.48 | -67 | 331 |
| L3 before costs | 1.15 | 2.07 | 0.36 | 2.40 | 28.8 | 0.48 | -77 | 331 |
| L3 after costs | 1.05 | 1.90 | 0.26 | 1.74 | 28.8 | 0.44 | -78 | 331 |

**The portfolios:**
- **T1:** BAB in the F&O universe, through stock futures.
- **T2:** the lowest against the highest beta quintile there, each side scaled to beta 1.
- **L1:** the lowest-beta 20% of the liquid 500, equal-weighted, delivery.
- **L2:** the rank-weighted low-beta half of the liquid 500.
- **L3:** L1 plus a NIFTY futures overlay of (1/β − 1), capped at 1.5, rolled monthly at 0.02% impact.

### Against benchmarks over the same months

| | Excess return %/mo | NW t | 4-factor α %/mo | t | Volatility %/yr | Sharpe | Worst drawdown % | Months |
|---|---|---|---|---|---|---|---|---|
| from 1999-04: L1 before costs | 0.86 | 2.11 | 0.32 | 2.34 | 20.9 | 0.49 | -63 | 331 |
| from 1999-04: L1 after costs | 0.81 | 1.99 | 0.27 | 1.99 | 20.9 | 0.46 | -63 | 331 |
| from 1999-04: L2 before costs | 0.95 | 2.16 | 0.35 | 2.65 | 22.5 | 0.50 | -66 | 331 |
| from 1999-04: L2 after costs | 0.91 | 2.07 | 0.31 | 2.36 | 22.5 | 0.48 | -67 | 331 |
| from 1999-04: L3 before costs | 1.15 | 2.07 | 0.36 | 2.40 | 28.8 | 0.48 | -77 | 331 |
| from 1999-04: L3 after costs | 1.05 | 1.90 | 0.26 | 1.74 | 28.8 | 0.44 | -78 | 331 |
| from 1999-04: NIFTY 500 TRI | 0.86 | 2.08 | 0.06 | 0.98 | 23.9 | 0.43 | -65 | 331 |
| from 2006-01: T1 before costs | 0.36 | 1.45 | 0.41 | 2.21 | 12.8 | 0.34 | -45 | 250 |
| from 2006-01: T1 after costs | -0.05 | -0.19 | -0.00 | -0.01 | 12.8 | -0.04 | -51 | 250 |
| from 2006-01: T2 before costs | 0.45 | 1.42 | 0.52 | 2.23 | 16.5 | 0.32 | -52 | 250 |
| from 2006-01: T2 after costs | 0.04 | 0.12 | 0.11 | 0.48 | 16.5 | 0.03 | -60 | 250 |
| from 2006-01: L1 before costs | 0.67 | 1.57 | 0.25 | 2.66 | 19.8 | 0.40 | -63 | 250 |
| from 2006-01: L1 after costs | 0.62 | 1.46 | 0.21 | 2.19 | 19.8 | 0.38 | -63 | 250 |
| from 2006-01: L2 before costs | 0.71 | 1.52 | 0.27 | 2.88 | 21.5 | 0.40 | -66 | 250 |
| from 2006-01: L2 after costs | 0.67 | 1.45 | 0.24 | 2.50 | 21.5 | 0.38 | -67 | 250 |
| from 2006-01: L3 before costs | 0.91 | 1.58 | 0.36 | 3.01 | 26.9 | 0.41 | -77 | 250 |
| from 2006-01: L3 after costs | 0.82 | 1.42 | 0.27 | 2.26 | 26.8 | 0.37 | -78 | 250 |
| from 2006-01: NIFTY 500 TRI | 0.66 | 1.56 | 0.12 | 1.48 | 21.8 | 0.36 | -63 | 250 |
| from 2006-01: NIFTY 50 TRI | 0.60 | 1.58 | 0.13 | 1.19 | 20.5 | 0.35 | -58 | 250 |
| from 2006-01: NIFTY Low Volatility 50 TRI | 0.77 | 2.20 | 0.33 | 3.15 | 17.8 | 0.52 | -52 | 250 |
| from 2006-01: NIFTY100 Low Volatility 30 TRI | 0.76 | 2.32 | 0.33 | 2.99 | 17.4 | 0.53 | -49 | 250 |

## 4. Robustness

### Beta windows (FP Table B2): universe A; 3-day and 1-day correlation returns

| | Excess return %/mo | NW t | 4-factor α %/mo | t | Volatility %/yr | Sharpe | Worst drawdown % | Months |
|---|---|---|---|---|---|---|---|---|
| vol 6m, corr 12m, 3-day | 1.25 | 4.61 | 1.02 | 3.62 | 16.4 | 0.92 | -34 | 331 |
| vol 6m, corr 36m, 3-day | 1.11 | 4.79 | 1.01 | 4.25 | 13.6 | 0.98 | -30 | 331 |
| vol 6m, corr 60m, 3-day | 1.02 | 4.65 | 1.02 | 4.51 | 12.8 | 0.96 | -28 | 331 |
| vol 12m, corr 12m, 3-day | 1.02 | 3.81 | 0.80 | 2.81 | 15.5 | 0.79 | -39 | 331 |
| vol 12m, corr 36m, 3-day | 0.89 | 3.89 | 0.81 | 3.37 | 13.1 | 0.81 | -31 | 331 |
| vol 12m, corr 60m, 3-day | 0.78 | 3.60 | 0.80 | 3.62 | 12.1 | 0.77 | -30 | 331 |
| vol 24m, corr 12m, 3-day | 0.95 | 3.40 | 0.68 | 2.35 | 15.8 | 0.72 | -39 | 331 |
| vol 24m, corr 36m, 3-day | 0.82 | 3.51 | 0.74 | 2.97 | 13.4 | 0.74 | -32 | 331 |
| vol 24m, corr 60m, 3-day | 0.73 | 3.27 | 0.74 | 3.17 | 12.4 | 0.71 | -34 | 331 |
| vol 6m, corr 12m, 1-day | 1.56 | 4.61 | 1.25 | 3.81 | 19.5 | 0.96 | -37 | 331 |
| vol 6m, corr 36m, 1-day | 1.58 | 5.04 | 1.28 | 4.45 | 17.1 | 1.11 | -32 | 331 |
| vol 6m, corr 60m, 1-day | 1.46 | 5.01 | 1.26 | 4.63 | 15.9 | 1.10 | -33 | 331 |
| vol 12m, corr 12m, 1-day | 1.32 | 4.01 | 1.05 | 3.25 | 18.3 | 0.87 | -39 | 331 |
| vol 12m, corr 36m, 1-day | 1.33 | 4.33 | 1.08 | 3.74 | 16.2 | 0.99 | -35 | 331 |
| vol 12m, corr 60m, 1-day | 1.19 | 4.15 | 1.04 | 3.86 | 15.0 | 0.95 | -35 | 331 |
| vol 24m, corr 12m, 1-day | 1.27 | 3.77 | 0.98 | 3.06 | 18.9 | 0.81 | -40 | 331 |
| vol 24m, corr 36m, 1-day | 1.29 | 4.32 | 1.04 | 3.54 | 16.3 | 0.95 | -33 | 331 |
| vol 24m, corr 60m, 1-day | 1.16 | 4.18 | 1.01 | 3.68 | 15.0 | 0.93 | -34 | 331 |

- Shorter windows and 1-day returns give larger BAB returns in India, more so than in FP B2.
- One-day correlations understate the betas of thinly traded shares, which sit on the low-beta side. That is the non-synchronous trading the paper's 3-day returns are meant to avoid. The 3-day, 60-month setting is the pre-registered headline.

### Size (FP Table B3): BAB within terciles of median traded value

All NSE:

| | Excess return %/mo | NW t | 4-factor α %/mo | t | Volatility %/yr | Sharpe | Worst drawdown % | Months |
|---|---|---|---|---|---|---|---|---|
| tercile 1 | 1.02 | 3.56 | 0.96 | 3.75 | 15.6 | 0.78 | -41 | 330 |
| tercile 2 | 0.59 | 2.72 | 0.69 | 3.09 | 12.9 | 0.55 | -43 | 331 |
| tercile 3 | 0.45 | 1.77 | 0.41 | 1.51 | 13.2 | 0.41 | -40 | 331 |

Liquid 500:

| | Excess return %/mo | NW t | 4-factor α %/mo | t | Volatility %/yr | Sharpe | Worst drawdown % | Months |
|---|---|---|---|---|---|---|---|---|
| tercile 1 | 0.36 | 1.42 | 0.54 | 2.25 | 15.5 | 0.28 | -54 | 331 |
| tercile 2 | 0.48 | 2.13 | 0.60 | 2.58 | 14.1 | 0.41 | -39 | 331 |
| tercile 3 | 0.39 | 1.32 | 0.27 | 0.96 | 16.2 | 0.29 | -46 | 331 |

### Liquidity and price screens on universe A

| | Excess return %/mo | NW t | 4-factor α %/mo | t | Volatility %/yr | Sharpe | Worst drawdown % | Months |
|---|---|---|---|---|---|---|---|---|
| drop bottom 0% by traded value, price >= Rs 2 | 0.78 | 3.60 | 0.80 | 3.62 | 12.1 | 0.77 | -30 | 331 |
| drop bottom 0% by traded value, price >= Rs 10 | 0.70 | 3.41 | 0.67 | 2.90 | 10.6 | 0.80 | -34 | 331 |
| drop bottom 33% by traded value, price >= Rs 2 | 0.56 | 2.62 | 0.58 | 2.54 | 11.5 | 0.59 | -39 | 331 |
| drop bottom 33% by traded value, price >= Rs 10 | 0.52 | 2.43 | 0.52 | 2.21 | 11.2 | 0.55 | -39 | 331 |
| drop bottom 50% by traded value, price >= Rs 2 | 0.48 | 2.11 | 0.48 | 2.05 | 12.3 | 0.46 | -35 | 331 |
| drop bottom 50% by traded value, price >= Rs 10 | 0.45 | 1.99 | 0.43 | 1.79 | 12.2 | 0.44 | -36 | 331 |

### Sub-periods (FP Table B4)

All NSE:

| | Excess return %/mo | NW t | 4-factor α %/mo | t | Volatility %/yr | Sharpe | Worst drawdown % | Months |
|---|---|---|---|---|---|---|---|---|
| 2000-2005 | 1.32 | 2.53 | 1.30 | 2.27 | 15.5 | 1.02 | -15 | 72 |
| 2006-2012 | 0.54 | 1.29 | 0.33 | 1.43 | 10.8 | 0.60 | -30 | 84 |
| 2013-2019 | 0.84 | 3.88 | 0.63 | 4.27 | 6.3 | 1.60 | -4 | 84 |
| 2020-2026 | 0.77 | 1.82 | 0.47 | 1.19 | 12.9 | 0.71 | -14 | 82 |

Liquid 500:

| | Excess return %/mo | NW t | 4-factor α %/mo | t | Volatility %/yr | Sharpe | Worst drawdown % | Months |
|---|---|---|---|---|---|---|---|---|
| 2000-2005 | 1.30 | 2.13 | 0.99 | 1.54 | 18.3 | 0.85 | -23 | 72 |
| 2006-2012 | 0.24 | 0.54 | 0.25 | 0.89 | 11.8 | 0.25 | -36 | 84 |
| 2013-2019 | 0.87 | 2.74 | 0.51 | 2.59 | 9.3 | 1.12 | -14 | 84 |
| 2020-2026 | -0.17 | -0.77 | 0.30 | 1.37 | 10.0 | -0.21 | -24 | 82 |

F&O:

| | Excess return %/mo | NW t | 4-factor α %/mo | t | Volatility %/yr | Sharpe | Worst drawdown % | Months |
|---|---|---|---|---|---|---|---|---|
| 2005-2009 | -0.04 | -0.06 | -0.02 | -0.04 | 13.1 | -0.04 | -45 | 59 |
| 2010-2014 | 0.95 | 2.36 | 0.42 | 1.14 | 14.4 | 0.79 | -22 | 60 |
| 2015-2019 | 0.82 | 1.79 | 0.46 | 1.57 | 10.7 | 0.92 | -16 | 60 |
| 2020-2026 | -0.03 | -0.09 | 0.46 | 1.66 | 12.7 | -0.03 | -23 | 82 |

- BAB is positive in every sub-period in A.
- In B and C it is weak or negative from 2020. In C it was also flat in 2005–2009, a period that includes the 2008 crash, when BAB lost 25% (`calendar_years_A.csv`).

### Beta compression (FP Table X)

Each month is placed in a tercile of stress seen up to then, using an expanding window. The table gives the cross-sectional standard deviation of betas.

| Stress measure | Low | Middle | High | High − low (NW t) | BAB market beta, low → high |
|---|---|---|---|---|---|
| NIFTY 500 3-month realised volatility (1999–2026) | 0.253 | 0.220 | 0.175 | −0.078 (−6.80) | 0.12 → 0.11 |
| India VIX (2017–2026) | 0.250 | 0.244 | 0.207 | −0.043 (−2.07) | 0.16 → 0.20 |

- Betas compress towards 1 in stressed months, as FP find (US P3−P1 −0.05, t −2.71).
- BAB's conditional market beta rises only a little with India VIX, and not with realised volatility. FP found a clearer rise (US 0.45, t 3.01).
- The TED-spread funding test (FP Table IX) was not done: there is no scriptable Indian certificate-of-deposit series (gap 34).

## 5. Stress tests

### Delisting

1,685 shares stop trading more than 45 days before the data end. Each is charged an extra return in the month it disappears.

| | Excess return %/mo | NW t | 4-factor α %/mo | t | Volatility %/yr | Sharpe | Worst drawdown % | Months |
|---|---|---|---|---|---|---|---|---|
| BAB A, shock 0% | 0.78 | 3.60 | 0.80 | 3.62 | 12.1 | 0.77 | -30 | 331 |
| BAB A after costs, shock 0% | 0.40 | 1.82 | 0.42 | 1.89 | 12.1 | 0.39 | -39 | 331 |
| T1 after costs, shock 0% | -0.02 | -0.07 | 0.04 | 0.20 | 12.9 | -0.02 | -51 | 261 |
| L1 after costs, shock 0% | 0.81 | 1.99 | 0.27 | 1.99 | 20.9 | 0.46 | -63 | 331 |
| BAB A, shock -30% | 0.75 | 3.51 | 0.78 | 3.60 | 12.1 | 0.74 | -31 | 331 |
| BAB A after costs, shock -30% | 0.37 | 1.72 | 0.39 | 1.83 | 12.1 | 0.36 | -40 | 331 |
| T1 after costs, shock -30% | -0.02 | -0.07 | 0.03 | 0.18 | 12.9 | -0.02 | -51 | 261 |
| L1 after costs, shock -30% | 0.76 | 1.89 | 0.22 | 1.68 | 20.8 | 0.44 | -63 | 331 |
| BAB A, shock -100% | 0.68 | 3.24 | 0.72 | 3.49 | 12.2 | 0.67 | -34 | 331 |
| BAB A after costs, shock -100% | 0.30 | 1.43 | 0.34 | 1.64 | 12.2 | 0.30 | -42 | 331 |
| T1 after costs, shock -100% | -0.02 | -0.08 | 0.02 | 0.13 | 13.0 | -0.02 | -52 | 261 |
| L1 after costs, shock -100% | 0.65 | 1.62 | 0.12 | 0.88 | 20.8 | 0.38 | -64 | 331 |

### Borrow fee (cash short, A and B)

| | Excess return %/mo | NW t | 4-factor α %/mo | t | Volatility %/yr | Sharpe | Worst drawdown % | Months |
|---|---|---|---|---|---|---|---|---|
| A fee 0.00% | 0.60 | 2.77 | 0.62 | 2.82 | 12.1 | 0.60 | -34 | 331 |
| B fee 0.00% | 0.38 | 1.63 | 0.44 | 1.87 | 12.9 | 0.36 | -39 | 331 |
| A fee 3.25% | 0.40 | 1.82 | 0.42 | 1.89 | 12.1 | 0.39 | -39 | 331 |
| B fee 3.25% | 0.18 | 0.78 | 0.24 | 1.02 | 12.9 | 0.17 | -44 | 331 |
| A fee 10.00% | -0.03 | -0.13 | -0.01 | -0.03 | 12.1 | -0.03 | -52 | 331 |
| B fee 10.00% | -0.23 | -0.98 | -0.17 | -0.73 | 12.9 | -0.22 | -67 | 331 |

### Futures roll impact (T1, T2)

| | Excess return %/mo | NW t | 4-factor α %/mo | t | Volatility %/yr | Sharpe | Worst drawdown % | Months |
|---|---|---|---|---|---|---|---|---|
| T1 after costs, roll impact 0.00% | 0.14 | 0.55 | 0.19 | 1.04 | 12.8 | 0.13 | -49 | 261 |
| T2 after costs, roll impact 0.00% | 0.19 | 0.62 | 0.28 | 1.20 | 16.5 | 0.14 | -57 | 261 |
| T1 after costs, roll impact 0.05% | -0.02 | -0.07 | 0.04 | 0.20 | 12.9 | -0.02 | -51 | 261 |
| T2 after costs, roll impact 0.05% | 0.05 | 0.15 | 0.13 | 0.57 | 16.5 | 0.03 | -60 | 261 |
| T1 after costs, roll impact 0.10% | -0.17 | -0.69 | -0.12 | -0.64 | 12.9 | -0.16 | -55 | 261 |
| T2 after costs, roll impact 0.10% | -0.10 | -0.32 | -0.02 | -0.07 | 16.5 | -0.07 | -62 | 261 |

## 6. Data checks

- **Adjusted returns:** 10.26 million daily returns for 4,318 shares, built from NSE bhavcopies. Splits, bonuses and dividends come from NSE's action list, and 1,523 days are flagged or fixed (`data/derived/return_flags.parquet`).
- **UBI cross-check** (December 2019 on, `ubi_crosscheck.csv`):
  - 87.7% of share-months agree within 1% and 94.9% within 3%; the median difference is 0.
  - Differences beyond 10% occur in 0.78% of share-months, or 0.41% for the liquid 500.
  - Expected sources of difference are dividends (ours include them) and UBI's misdated split factors (gap 32).
- **Survivorship:** delisted shares are included, because the NSE files keep every share that ever traded. Their final losses are not recorded, hence the stress test above.

## 7. How many variants were tried

- **The grid:** 864 BAB variants, all saved in `grid_summary.parquet` and `grid_series.parquet`:
  - 3 universes;
  - volatility windows of 6, 12 and 24 months;
  - correlation windows of 12, 36 and 60 months;
  - shrinkage 0.4, 0.6, 0.8 and 1.0. Shrinkage 0 sets every beta to 1 and cannot rank, so 1.0 replaces it; for w > 0 the ranking is the same and w changes only leverage;
  - K = 1, 3, 6 and 12;
  - rank or equal weights.
- **Before costs:** all 864 are positive, 646 have t > 2, and 29 pass a Bonferroni cut of t > 3.85. The share with t > 2 is 99% in A, 64% in B and 61% in C.
- **After costs:** the median variant earns 0.44% a month in A, 0.23% in B and 0.08% in C.
- **Best variant:** universe A, 6-month volatility, 36-month correlation, equal weights, K = 1, at 0.80% a month and t 4.73. It is not reported as a finding. The headline is the paper's own setting, fixed in the plan before any run.
- **Extra variants in the tables:** the tables above add 18 beta-window settings per universe, 3 borrow fees, 3 roll impacts, 6 liquidity screens and 3 delisting shocks.

## 8. Review

The `backtest_reviewer` subagent checked the backtests; its report is in `review/review.md`.

**What it confirmed:**
- The gross factor reproduces exactly, and a hand check of one month matches.
- There is no look-ahead. Lagging formation by a day gives 0.75% (t 3.61). The cleaning step's 5-day look-forward touches only about 0.03% of portfolio weight.
- The stability checks pass: halves of 0.75% and 0.81%, and 0.45% (t 2.21) after dropping the best 10 months.

**What it found, and what was done:**
1. **No futures roll was charged.** A monthly roll is now charged on futures positions (gap 35). T1 after costs fell from 0.33% to about zero.
2. **A after costs is not tradeable.** It is now labelled a paper portfolio, with a delivery-cost and SLB-fee treatment; the tradeable rows are B, C and L.
3. **A's result is driven by thinly traded shares.** Size terciles and liquidity screens were added, and the tradeable conclusions rest on B and C.
4. **The L1 and benchmark comparison used different windows.** It now uses the same months.
5. **Two cost treatments for C.** C now has one: futures with the roll, no borrow fee.
6. **Leg sizes were diluted by empty months.** They are now averaged over active months only.
7. **The calendar-year table had dead code and part years.** The dead code is removed, and a months column shows part years (1999: 9 months, 2026: 10).

**Noted, not changed:**
- About 0.12% of weight sits on shares with no return in some months; the −100% delisting stress bounds its effect.
- Dividends before 2006 are mostly missing (gap 31), so early returns are close to price-only.
- STT at the 2026 rate is applied to the whole history, which is conservative.

## 9. Where India cannot match the paper

- **Shorting:** outside about 200 F&O shares, cash shorts need SLB, which lends a few hundred shares thinly. So the paper's factor in A and B is a research factor.
- **History:** 27 years, about a third of the US sample, at roughly twice the volatility.
- **Market cap:** none before 2024. Size groups and value weights use traded value.
- **Factor models:** IIMA factors end in December 2025, and there is no liquidity factor.
- **Funding liquidity:** the TED-spread test is not done (gap 34).
- **Futures returns:** approximated by share excess returns, with the roll charged but basis noise ignored.
