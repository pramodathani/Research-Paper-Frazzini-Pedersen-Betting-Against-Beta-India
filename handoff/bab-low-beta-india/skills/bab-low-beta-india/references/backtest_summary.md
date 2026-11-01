# Backtest summary: low-beta NSE shares, long only

Source: the study's `results/` folder (`tradeable_vs_benchmarks.csv`, `delisting_stress.csv`, `tradeable_monthly.csv`). Universe: the 500 most traded NSE shares. Excess returns are over the 91-day Treasury bill; t-statistics are Newey-West with six lags; alphas use the IIMA market, size, value and momentum factors (to December 2025). Costs: delivery costs and 0.1% market impact a side; the NIFTY futures overlay in L3 pays futures costs and a monthly roll. Drawdowns in the tables are on excess returns; on total returns the worst drawdowns are -59.7% (L1), -63.6% (L2), -75.7% (L3) and -60.4% (NIFTY 500 TRI), all from December 2007 to February 2009 (the market's trough was November 2008).

L1 is the equal-weighted lowest-beta fifth, L2 the rank-weighted low-beta half, L3 is L1 plus a NIFTY futures position that lifts its beta to about one.

## April 1999 to October 2026 (331 months)

| | Excess return %/month | NW t | 4-factor α %/month | t | Volatility %/yr | Sharpe | Worst drawdown % (excess returns) | Months |
|---|---|---|---|---|---|---|---|---|
| L1 before costs | 0.86 | 2.11 | 0.32 | 2.34 | 20.9 | 0.49 | -63 | 331 |
| L1 after costs | 0.81 | 1.99 | 0.27 | 1.99 | 20.9 | 0.46 | -63 | 331 |
| L2 before costs | 0.95 | 2.16 | 0.35 | 2.65 | 22.5 | 0.50 | -66 | 331 |
| L2 after costs | 0.91 | 2.07 | 0.31 | 2.36 | 22.5 | 0.48 | -67 | 331 |
| L3 before costs | 1.15 | 2.07 | 0.36 | 2.40 | 28.8 | 0.48 | -77 | 331 |
| L3 after costs | 1.05 | 1.90 | 0.26 | 1.74 | 28.8 | 0.44 | -78 | 331 |
| NIFTY 500 TRI | 0.86 | 2.08 | 0.06 | 0.98 | 23.9 | 0.43 | -65 | 331 |

## 2006 to October 2026 (250 months), with NSE's low-volatility indices

| | Excess return %/month | NW t | 4-factor α %/month | t | Volatility %/yr | Sharpe | Worst drawdown % (excess returns) | Months |
|---|---|---|---|---|---|---|---|---|
| L1 before costs | 0.67 | 1.57 | 0.25 | 2.66 | 19.8 | 0.40 | -63 | 250 |
| L1 after costs | 0.62 | 1.46 | 0.21 | 2.19 | 19.8 | 0.38 | -63 | 250 |
| L2 after costs | 0.67 | 1.45 | 0.24 | 2.50 | 21.5 | 0.38 | -67 | 250 |
| L3 after costs | 0.82 | 1.42 | 0.27 | 2.26 | 26.8 | 0.37 | -78 | 250 |
| NIFTY 500 TRI | 0.66 | 1.56 | 0.12 | 1.48 | 21.8 | 0.36 | -63 | 250 |
| NIFTY 50 TRI | 0.60 | 1.58 | 0.13 | 1.19 | 20.5 | 0.35 | -58 | 250 |
| NIFTY Low Volatility 50 TRI | 0.77 | 2.20 | 0.33 | 3.15 | 17.8 | 0.52 | -52 | 250 |
| NIFTY100 Low Volatility 30 TRI | 0.76 | 2.32 | 0.33 | 2.99 | 17.4 | 0.53 | -49 | 250 |

## Delisting stress (L1)

Every share that stopped trading is charged an extra loss in the month it vanishes (1,685 shares).

| | Excess return %/month | NW t | 4-factor α %/month | t | Sharpe |
|---|---|---|---|---|---|
| L1 after costs, shock 0% | 0.81 | 1.99 | 0.27 | 1.99 | 0.46 |
| L1 after costs, shock -30% | 0.76 | 1.89 | 0.22 | 1.68 | 0.44 |
| L1 after costs, shock -100% | 0.65 | 1.62 | 0.12 | 0.88 | 0.38 |

## Calendar years

L1 beat the NIFTY 500 TRI in 52% of months.

| Year | Months | L1 after costs % | NIFTY 500 TRI % |
|---|---|---|---|
| 1999 | 9 | 44.5 | 61.1 |
| 2000 | 12 | -26.5 | -23.5 |
| 2001 | 12 | -16.8 | -21.6 |
| 2002 | 12 | 21.1 | 13.9 |
| 2003 | 12 | 112.3 | 104.9 |
| 2004 | 12 | 17.4 | 21.1 |
| 2005 | 12 | 46.0 | 38.8 |
| 2006 | 12 | 15.9 | 36.2 |
| 2007 | 12 | 33.8 | 64.6 |
| 2008 | 12 | -54.9 | -56.5 |
| 2009 | 12 | 107.2 | 91.0 |
| 2010 | 12 | 18.0 | 15.3 |
| 2011 | 12 | -23.6 | -26.4 |
| 2012 | 12 | 31.2 | 33.5 |
| 2013 | 12 | 5.7 | 4.8 |
| 2014 | 12 | 49.4 | 39.3 |
| 2015 | 12 | 10.0 | 0.2 |
| 2016 | 12 | 5.4 | 5.1 |
| 2017 | 12 | 31.5 | 37.7 |
| 2018 | 12 | -4.7 | -2.1 |
| 2019 | 12 | 2.8 | 9.0 |
| 2020 | 12 | 33.8 | 17.9 |
| 2021 | 12 | 33.8 | 31.6 |
| 2022 | 12 | -3.3 | 4.2 |
| 2023 | 12 | 33.3 | 26.9 |
| 2024 | 12 | 18.4 | 16.2 |
| 2025 | 12 | 1.4 | 7.8 |
| 2026 | 10 | 0.8 | -7.5 |

## The script against the study

For four past months, the script's holdings built from UBI's candles were compared with the study's portfolio for the same month, built from NSE data with dividends: 93% to 98% of the script's 82 to 84 holdings were in the study's 86 to 87 (October 2026 build: 80 of 84; study 87). The differences come from dividends, from shares UBI does not hold (UBI's equity file lacks 914 of the symbols NSE lists, and the script ranked 420 shares against the study's 500), and from UBI's split-adjustment errors, which the script handles by dropping one-day moves beyond -45% and +100% (one move was dropped in the October 2026 build, in VEDL).

## What the study could not test

- A funding-liquidity (TED spread) test: no downloadable Indian certificate-of-deposit rate.
- The hedged long-short factor after costs: stock futures cost about as much each month in rolling as the factor earns, and cash shorts need securities lending that covers few shares.
- Market capitalisation weights: not available before 2024.
