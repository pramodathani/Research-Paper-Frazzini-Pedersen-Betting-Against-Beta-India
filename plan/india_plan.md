# Betting Against Beta for India: adaptation and data plan

**Status:** draft for the user's approval (Adapt to India gate), 2026-10-31.

**Sources:**
- Frazzini and Pedersen (FP), May 2013 draft. Pages are those of `paper/summary.md`.
- Agarwalla, Jacob, Varma and Vasudevan (AJVV), IIMA WP 2014-07-01, `paper/AgarwallaJacobVarmaVasudevan2014_BAB_India.pdf`.

## 1. What we are recreating, in one paragraph

**The paper's idea.** Each month, estimate every share's beta to the market using the paper's recipe:
- the volatility of 1 year of daily log returns;
- the correlation of 5 years of overlapping 3-day log returns;
- shrinkage 0.6 × β + 0.4 × 1.

Then split the shares at the median beta, weight each half by beta rank, and lever the low-beta half and de-lever the high-beta half to a beta of 1 each. The difference, net of the risk-free rate, is the BAB factor.

**What we add for India.** We build the paper's factor and the paper's beta deciles for NSE shares, then two families of portfolios that can actually be traded in India:
- **long-short:** through stock futures;
- **long-only:** delivery shares, optionally with a NIFTY futures overlay.

## 2. The Indian benchmark we must meet

AJVV used all BSE shares from Prowess, January 1998 to June 2013, with the Sensex as the market, the 91-day T-bill as the risk-free rate, and the same w = 0.6. Their Table 2 (p.18), read from the page image:

| | P1 (low β) | P10 (high β) | BAB |
|---|---|---|---|
| Excess return, %/month, equal-weighted | 0.01 | −1.97 | **1.70*** |
| CAPM α / 4-factor α | −0.44 / −0.97*** | −2.89*** / −3.09*** | 1.67*** / **1.08**** |
| β ex ante / realised | 0.56 / 0.70 | 1.38 / 1.44 | 0.00 / 0.09 |
| Volatility (%/yr) / Sharpe | 31.4 / 0.00 | 54.7 / −0.43 | 23.8 / **0.86** |

- BAB was on average long ₹1.32 and short ₹0.91 (p.9).
- Yearly returns (Table 3, p.19) include −34.2% in 2008 and +126.4% in 2007.
- AJVV's decile alphas are all negative because thousands of tiny BSE shares did badly (p.9). That is a warning to filter the universe.

## 3. What changes for India, and why

| Item | Paper (US) | India plan | Why |
|---|---|---|---|
| **Universe** | All CRSP common stocks | Three universes, all point-in-time: **(A) All NSE** (series EQ/BE/BZ, company shares only, price ≥ ₹2, traded on ≥ 50% of days in the past year); **(B) Liquid 500**, the 500 shares with the highest median daily traded value over the past 12 months, standing in for the NIFTY 500; **(C) F&O**, shares with stock futures that month | (A) is closest to the paper. (B) is what a fund can hold. (C) is what can be shorted overnight. No point-in-time NIFTY 500 lists exist before about 2018 (scout: PDF press releases only). |
| **Dates** | 1926–2012 | Daily prices from January 1996. The first betas come once 750 days of correlation data exist (about early 1999). **Main sample: BAB returns January 2000 to October 2026**, about 322 months. **Clean subsample from 2006**, when the corporate action list becomes complete (gap 31). F&O universe from 2005. | Bhavcopies start in 1996, and NSE's corporate actions are thin before 2006. |
| **Prices** | CRSP total returns | NSE bhavcopy raw closes, adjusted by us for splits, bonuses and **dividends** from NSE's corporate action list. Before 2006, round-ratio jumps are detected as splits. Daily moves beyond −50% or +100% are flagged and listed. | UBI starts in December 2019 (too short for 5-year correlations), lacks delisted shares and dividends, and has misdated split factors (gap 32: 189 unexplained steps in 72 shares). |
| **Market** | CRSP value-weighted index | **NIFTY 500 TRI, daily, 1995–2026**, from niftyindices.com's historical-data endpoint (measured today). NIFTY 50 TRI as a robustness check. | The closest broad value-weighted total-return market. AJVV used the Sensex (30 shares). |
| **Risk-free rate** | 1-month US T-bill | **91-day T-bill** from the IIMA factor library RF column (1993-10 to 2025-12). For 2026, RBI/FBIL 91-day yields, source to be fixed at the Data stage. | Same choice as AJVV. FP Table B6 shows the choice barely matters. |
| **Factor models** | CAPM, FF3, Carhart 4, plus Pastor–Stambaugh liquidity | CAPM, FF3 and 4-factor using IIMA's MF, SMB, HML and WML (to 2025-12). **No 5-factor model.** | India has no Pastor–Stambaugh factor. |
| **Size / value weights** | NYSE breakpoints, market cap | Market cap exists only from February 2024 (NSE MCAP files). Before that, **median traded value is the size proxy**. Value-weighted deciles use the traded-value proxy and are labelled as such. | Gap 10: no shares outstanding history. |
| **Trading hours and timing** | Month-end close | Betas computed from data up to the last trading day of month t−1; portfolios formed at that close and held through month t. **Every signal lagged one month.** | No look-ahead. |
| **Settlement** | n/a | T+1 for cash shares since 2023. Stock and index futures are cash-settled monthly and rolled before expiry. | Affects funding of buys in the live version only. |
| **Short selling** | Costless short of any stock | Overnight cash shorts need SLB, which is thin: 9–141 symbols trade on a given day (scout, 2011–2026). **The tradeable short leg is stock futures**, available only for the F&O universe (52 shares in 2005, 218 today). | This is the main way India cannot match the paper. |
| **Leverage** | Long about $1.4, short about $0.7, financed at T-bill | Leverage comes from futures: notional 1/β_L long, 1/β_H short, with margin of about 15–25% posted from cash that earns roughly the T-bill. | Futures embed financing at roughly the risk-free rate. |
| **Costs** | None | Shared engine's Indian costs: brokerage, STT, stamp duty, exchange, SEBI, GST. Delivery costs for cash shares, futures costs for futures legs. Impact 0.001 a side for Liquid 500 and F&O, 0.003 for All NSE. Borrow fee for any cash short: a pooled SLB fee estimate. **Every result is shown before and after costs.** | ResearchRules. The engine has no borrow fee and no cash return (gaps 27, 28), so we pass excess returns as gap 28 describes and add a stated borrow-fee drag. |
| **Delisting** | CRSP delisting returns | A share that stops trading keeps its last return, with a stress test at −30% and −100% the next month. | The engine drops leavers silently (gap 27). |

## 4. Portfolios we will run

### 4.1 Paper replication (research only; the short leg can't be traded as built)
- **R1, BAB factor** as FP eq. 16–17 in universes A, B and C. Gross, and after costs plus the borrow drag.
- **R2, beta deciles P1…P10**, equal-weighted (FP Table III, AJVV Panel A) and traded-value-weighted (AJVV Panel B analogue).

### 4.2 Tradeable long-short (F&O universe, stock futures)
- **T1, BAB with futures.** Each month:
  - rank F&O shares by beta;
  - go long the low-beta half through stock futures at notional w_L/β_L;
  - go short the high-beta half at notional w_H/β_H, rank-weighted as in the paper.
- Futures returns are approximated by the share's excess return, because the futures' cost of carry is close to the risk-free rate; the basis error is noted.
- Lot sizes make small accounts lumpy, so the hand-off will state a minimum capital from current lot sizes in `fo_mktlots.csv`.
- **T2, BAB with futures, equal-weighted quintiles.** Bottom against top beta quintile, the simpler version a desk would run, as a robustness check.

### 4.3 Tradeable long-only (delivery, rebalanced monthly or every K months)
- **L1, low-beta portfolio.** Universe B; the lowest-beta 20% (about 100 shares), equal-weighted. Versus the NIFTY 500 TRI.
- **L2, rank-weighted low-beta half.** The BAB long leg without leverage (FP p.19 weights).
- **L3, low-beta with beta 1 through NIFTY futures.** L1 plus a NIFTY 50 futures overlay of (1/β_L − 1) × capital, so the portfolio's beta is about 1. This is the BAB long leg made tradeable: only shares are held long, and no shares are shorted.
- **Benchmarks:** NIFTY 500 TRI and **NIFTY100 Low Volatility 30 TRI**, the investable low-risk index (same endpoint; history depth to be measured).
- **Why this matters:** FP Table B9 shows that a dollar-neutral, unlevered BAB earns only 0.03% a month (t 0.20) against 0.51% beta-neutral. Expect L1 and L2 to win mainly on risk (lower volatility, smaller drawdown, higher Sharpe), not on raw return. L3 tests whether the leverage brings the return back.

## 5. Tables and figures we will reproduce

| India table | Paper analogue | Content |
|---|---|---|
| T1 | FP Table III; AJVV Table 2 | Ten beta deciles and BAB, excess return, CAPM / 3-factor / 4-factor α with Newey–West t, β ex ante and realised, volatility, Sharpe, max drawdown, number of months. Universes A and B; equal- and traded-value-weighted. |
| T2 | FP Table V row; AJVV p.9 | BAB summary per universe: excess return, α, long ₹ and short ₹ sizes, volatility, Sharpe, before and after costs. |
| T3 | AJVV Table 3 | BAB, MKT, SMB, HML, WML by calendar year, 2000–2026. |
| T4 | FP Table B2 | Beta windows: volatility 6/12/24 months × correlation 12/36/60 months, plus 1-day versus 3-day returns. |
| T5 | FP Table B3 | BAB within size (traded-value) terciles. |
| T6 | FP Table B4 | Subperiods: 2000–05, 2006–12, 2013–19, 2020–26. |
| T7 | FP Table X, Panels A–C | **Beta compression.** Cross-sectional dispersion of betas in India VIX-volatility terciles (India VIX from 2008, same endpoint). TED volatility replaced by India VIX volatility, with **expanding-window terciles** so nothing is seen early (FP used full-sample terciles). |
| T8 | — | Tradeable portfolios T1, T2, L1, L2 and L3, before and after costs, against the benchmarks. |
| F1 | FP Fig. 1 | Alpha against beta decile. |
| F2 | AJVV Fig. 1 | Beta percentiles over time. |
| F3 | AJVV Fig. 2 | Cumulative BAB against market, SMB, HML and WML. |

**Not reproduced:**
- FP's other asset classes (Tables VI–VIII).
- The TED-spread regressions (Table IX). There is no clean Indian funding-liquidity series. A CD-minus-T-bill spread could stand in, but its data is not in hand; offered as optional.
- The holdings tests (Table XI): no fund-holdings data.

**Every average return** comes with Newey–West t (6 lags), the number of months and the worst drawdown.

**Variants counted.**
- **Grid size:** 3 universes × 3 volatility windows × 3 correlation windows × 4 shrinkage weights (0, 0.4, 0.6, 0.8) × 4 holding periods (K = 1, 3, 6, 12) × 2 weightings = **864**, published so readers can explore.
- **Pre-registered headline:** universe A, the paper's exact settings, K = 1.
- Any best variant from the grid is labelled as such and treated with suspicion.

## 6. The companion site's J and K
BAB has no J and K. On the site:
- **J** is the estimation window: volatility months and correlation months.
- **K** is the holding period: rebalance every 1, 3, 6 or 12 months, with overlapping cohorts for K > 1 as in Jegadeesh–Titman.
- **Other settings:** shrinkage w, universe, rank versus equal weighting, number of beta groups (deciles or quintiles), long-only versus long-short, costs on or off, and start year.
- The site reads a precomputed grid (§5). It does not run code in the browser.

## 7. Data plan (UBI first)

| Need | Source | Status |
|---|---|---|
| Daily raw share prices, 1996–2026, with delisted shares | NSE bhavcopies | On disk in the J&T study (7,628 files). Our own downloader seeds `data/nse/bhavcopy` by copying them, then fetches only what is missing. |
| Corporate actions (splits, bonuses, dividends) | NSE corporate actions API, 2000–2026 | Same: copy, then top up. |
| F&O membership, 2005–2026 | NSE F&O bhavcopies (gap 30 recipe) | Same. |
| NIFTY 500 TRI, NIFTY 50 TRI, NIFTY 500 price, NIFTY100 Low Vol 30 TRI, India VIX, daily | niftyindices.com `/BackPage/getTotalReturnIndexString`, `/getHistoricaldatatabletoString`, `/BindHistoricalIndiaVixData` | **New downloader**; measured today: NIFTY 500 TRI from 1995-01-01, about 5 years per request. |
| Risk-free rate, MF, SMB, HML, WML | IIMA library, 1993-10 to 2025-12 | Copy, then refresh. 2026 RF from RBI/FBIL (to be fixed). |
| Current F&O lot sizes | `nsearchives.nseindia.com/content/fo/fo_mktlots.csv` | For the hand-off's capital minimum. |
| SLB lending fees | `nsearchives.nseindia.com/archives/slbs/bhavcopy/SLBM_BC_{DDMMYYYY}.DAT`, 2011– | Sampled monthly to estimate a pooled borrow fee. |
| **UBI** (`export_prices` nse/equities, day, adjusted) | tradingmachine | **Used for:** (1) a cross-check of our adjusted returns for liquid shares from 2019; (2) the hand-off's live monthly target script, which needs about 5 years of daily candles and will pass every factor through the gap-32 check. **Not the main history**, because of its December 2019 start and survivorship bias. |

**Gaps to record:**
- No total-return index in tradingmachine, with the niftyindices endpoint as the workaround (an update to gap 12).
- No SLB data (already raised by the scout as gap 33).
- No beta or risk-free utility.

All data stays in the git-ignored `data/` folder; only derived results are published.

## 8. Tests (no network)
1. **Beta estimator.** On a made-up series with a known ρ and σ ratio, β = ρσ_i/σ_m to 1e-9. Also:
   - it refuses fewer than 120 or 750 observations;
   - the 3-day overlapping log sums are correct;
   - shrinkage at w = 0.6 gives 0.6β + 0.4.
2. **Rank weights.** For five shares with known betas, w_H and w_L match a hand calculation, each sums to 1, ties get average ranks, and an odd count leaves the median share at zero.
3. **BAB return.** With constant returns, the hand-computed (r_L − r_f)/β_L − (r_H − r_f)/β_H matches, and the ex-ante beta at formation is 0.
4. **No look-ahead.** Changing any price after month-end t−1 leaves month t's weights unchanged.
5. **Corporate actions.** A 1:1 bonus, a split from ₹10 to ₹2, and a ₹5 dividend on the ex-date give the correct adjusted returns. A −60% day with no action is flagged.
6. **Universe edges.** A share that stops trading, a missing month, the first and last sample month, an empty F&O month, and duplicate EQ/BE rows on one day.
7. **Parsers.** Old and UDiFF bhavcopy samples, a niftyindices JSON sample, and an IIMA CSV sample.
8. **End to end.** A 40-share, 8-year made-up market runs the whole pipeline in seconds.

## 9. Where India cannot match the paper, and what that may do

1. **Shorting.** Outside about 200 F&O shares, cash shorts are impractical. The paper-style BAB in universes A and B is a **research factor**, not a tradeable one. The tradeable long-short is limited to large F&O shares. FP Table B3 found BAB much weaker in large US stocks (Sharpe 0.25 against 0.65 in small), so **expect T1 to earn less than the full factor.**
2. **Shorter, noisier history.** About 27 years of BAB returns against 86 in the US. Indian volatility is about twice as high (AJVV BAB volatility 23.8% against FP 10.7%), so t-statistics will be lower for the same Sharpe ratio.
3. **No market cap before 2024.** Size groups and value weights use traded value. This may tilt towards active, high-beta shares.
4. **Corporate actions before 2006** are partly detected rather than listed. Dividends before about 2000 are missing, which understates low-beta returns slightly, as dividend payers are often low-beta.
5. **Factor models.** IIMA factors end in December 2025, and there is no liquidity factor. The 3- and 4-factor alphas for 2026 months are unavailable.
6. **Futures approximation.** The tradeable long-short uses share returns minus the risk-free rate as the futures return. The basis and roll costs differ by a few basis points a month; the error is noted.
7. **Market proxy.** NIFTY 500 is free-float weighted, while the paper's market is full-cap. Betas will differ slightly.

## 10. Tradeable?

**Yes.** BAB is a portfolio rule rebalanced on a schedule: monthly betas from daily prices, then rank-based target weights. trading-agent can run:
- **(a) the long-only low-beta portfolio (L1 or L2):** delivery shares, monthly, the simplest;
- **(b) L3:** the same plus a NIFTY futures overlay;
- **(c) the F&O long-short (T1)**, if its after-cost results hold up.

Which of these is handed off will be decided on the Results evidence. The hand-off's monthly target script will build betas from UBI daily candles through tradingmachine and place no orders.
