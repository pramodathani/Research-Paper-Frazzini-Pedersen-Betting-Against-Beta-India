# Betting Against Beta — structured summary

Frazzini, A., and Pedersen, L. H. (2014). Betting against beta. *Journal of Financial Economics* 111(1), 1–25. DOI 10.1016/j.jfineco.2013.10.005.

**Pages cited** are from the user's copy, the draft of 10 May 2013 (80 pages):

| Part | Footer | PDF pages |
|---|---|---|
| Main text | p.1–34 | 1–34 |
| Tables | T1–T11 | 39–49 |
| Figures | F1–F2 | 50–51 |
| Appendix A (proofs) | A1–A9 | 52–60 |
| Appendix B (robustness) | B1–B17 | 61–77 |
| Appendix C (calibration) | C1–C3 | 78–80 |

**Checked by hand:** eq. 14–17 (p.16–19) and Table III (T3).

**Units:** returns and alphas are in % a month; volatilities and Sharpe ratios are annualised.

## 1. Hypothesis

Many investors are barred from using leverage or limited in it: mutual funds, pension funds and individuals. To get more expected return, they overweight risky high-beta assets instead of levering up safe ones. This bids up high-beta assets, so the security market line is flatter than the CAPM says. An investor who can use leverage gains by holding leveraged low-beta assets against high-beta ones (p.2–3).

**Model (p.7–14).** Overlapping-generations mean–variance agents face the margin constraint m_t^i Σ x^s P^s ≤ W^i (eq. 2). ψ̄_t is the risk-tolerance-weighted average Lagrange multiplier on that constraint.

**The five propositions:**
1. **High beta, low alpha** (p.9–10). E(r^s) = r^f + ψ̄ + β^s λ (eq. 8). Alpha is α^s = ψ̄(1 − β^s), which falls as beta rises.
2. **BAB earns a positive expected return** (p.12). E(r^BAB) = (β^H − β^L)/(β^L β^H) · ψ̄ > 0 (eq. 10).
3. **Funding shocks hurt BAB** (p.12–13). When constraints tighten, BAB's realised return is low and its future required return rises (eq. 11–12).
4. **Beta compression** (p.13). Higher funding-liquidity risk compresses betas toward 1, and the BAB factor's conditional beta turns positive.
5. **Constrained investors hold high beta** (p.14). Constrained investors hold riskier assets; unconstrained ones hold portfolios with beta below 1.

## 2. Data (p.14–16, Table I T1, Table II T2)

### US equities
- CRSP common stocks (share codes 10 and 11), January 1926 to March 2012.
- 23,538 stocks in all, 3,182 in an average month.
- Market: CRSP value-weighted index. Risk-free rate: 1-month US T-bill.
- Factors: Fama–French SMB and HML, Carhart UMD, and the Pastor–Stambaugh liquidity factor (available 1968–2011).

### International equities
- Source: Xpressfeed Global, 19 MSCI developed markets.
- Period: mostly 1989–2012, Canada from 1984. The text says the sample starts in 1989 (p.15), but Tables IV and V say 1984.
- Returns are in US dollars and unhedged, in excess of the US T-bill.
- Betas are taken against the MSCI local index.
- Factors: Asness–Frazzini SMB, HML and UMD.
- 55,600 stocks in all, US and international together (p.14).

### Other assets
- US Treasuries: CRSP Fama bond portfolios, 1952–2012.
- Credit: Barclays indices by maturity and by rating, 1973–2012.
- Futures (AQR data): 13 equity indices, 9 government bonds, 9 currencies and 27 commodities, 1963–2012.
- TED spread: 1984–2012.
- Holdings: mutual funds, a discount brokerage, LBOs and Berkshire Hathaway's 13F filings.

**No India in the sample.** The 19 international markets are all developed.

## 3. Method

### 3.1 Ex-ante betas (p.16–18)

| Step | Paper |
|---|---|
| Beta formula | β̂^TS_i = ρ̂ · σ̂_i / σ̂_m (eq. 14) |
| Volatility | 1-year rolling standard deviation of daily 1-day **log** returns; at least 120 trading days |
| Correlation | 5-year rolling window of **overlapping 3-day log returns**, r^3d_t = Σ_{k=0..2} ln(1 + r_{t+k}); at least 750 trading days. The 3-day returns handle non-synchronous trading. |
| Shrinkage | β̂_i = w β̂^TS_i + (1 − w) β^XS, with **w = 0.6** and **β^XS = 1** for every asset and period (eq. 15). Footnote 14: the Vasicek w averages 0.61 in US data. |
| Market | Asset-class market: CRSP VW for the US, the MSCI local index abroad (p.18) |
| Monthly-only assets | 1-year and 5-year windows, with at least 12 and 36 observations (p.17) |

**Shrinkage changes the leverage, not the ranks** (p.17–18). The BAB legs are scaled by 1/β, so w matters for returns even though it doesn't reorder stocks. Inference uses realised loadings, which are not shrunk.

### 3.2 BAB factor (p.18–19, eq. 16–17)

1. **Rank.** Each calendar month, rank all securities by β̂. Below-median securities form the low-beta leg and above-median the high-beta leg. Abroad, the median is the country median.
2. **Weight by rank** (eq. 16). With z = rank(β) and z̄ the mean rank:
   - w_H = k (z − z̄)⁺ and w_L = k (z − z̄)⁻;
   - k = 2 / 1′|z − z̄|, so each leg's weights sum to 1.
3. **Scale each leg to beta 1** (eq. 17):
   - r^BAB_{t+1} = (1/β^L_t)(r^L_{t+1} − r^f) − (1/β^H_t)(r^H_{t+1} − r^f);
   - β^L_t = β′w_L and β^H_t = β′w_H are the shrunk ex-ante betas.
4. **Typical sizes.** The factor is self-financing and zero-beta at formation. The US BAB averages long $1.4 and short $0.7 (p.19). International averages long $1.40 and short $0.89 (p.22).
5. **Rebalance monthly.** Betas are measured at the end of month t−1 and held through month t (T3 caption).

### 3.3 Beta-sorted deciles (T3, T4)
Stocks are put into 10 deciles on the previous month-end beta, using NYSE breakpoints in the US. Each decile is equal-weighted and rebalanced monthly.

### 3.4 Tests
- **Alphas:** time-series intercepts of monthly excess returns on CAPM, Fama–French 3-factor, Carhart 4-factor, and 4-factor plus Pastor–Stambaugh liquidity.
- **Standard errors:** the return tables don't say which they use. Table IX uses White standard errors; Table X uses Newey–West with 60 lags.
- **Sharpe ratio:** never defined in the paper. The numbers fit (mean × 12) / (sd × √12); for US BAB, 0.70 × 12 / 10.7 ≈ 0.78.

## 4. Tables to reproduce for India

### Table III (T3, PDF 41): US beta deciles and BAB, 1926–2012. Checked against the page image.

| | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 | BAB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Excess return | 0.91 | 0.98 | 1.00 | 1.03 | 1.05 | 1.10 | 1.05 | 1.08 | 1.06 | 0.97 | **0.70** (7.12) |
| CAPM α | 0.52 | 0.48 | 0.42 | 0.39 | 0.34 | 0.34 | 0.22 | 0.21 | 0.10 | −0.10 | **0.73** (7.44) |
| 3-factor α | 0.40 | 0.35 | 0.26 | 0.21 | 0.13 | 0.11 | −0.03 | −0.06 | −0.22 | −0.49 | **0.73** (7.39) |
| 4-factor α | 0.40 | 0.37 | 0.30 | 0.25 | 0.18 | 0.20 | 0.09 | 0.11 | 0.01 | −0.13 | **0.55** (5.59) |
| 5-factor α | 0.37 | 0.37 | 0.33 | 0.30 | 0.17 | 0.20 | 0.11 | 0.14 | 0.02 | 0.00 | **0.55** (4.09) |
| β ex ante | 0.64 | 0.79 | 0.88 | 0.97 | 1.05 | 1.12 | 1.21 | 1.31 | 1.44 | 1.70 | 0.00 |
| β realised | 0.67 | 0.87 | 1.00 | 1.10 | 1.22 | 1.32 | 1.42 | 1.51 | 1.66 | 1.85 | −0.06 |
| Volatility (%/yr) | 15.7 | 18.7 | 21.1 | 23.1 | 25.6 | 27.6 | 29.8 | 31.6 | 35.5 | 41.7 | 10.7 |
| Sharpe | 0.70 | 0.63 | 0.57 | 0.54 | 0.49 | 0.48 | 0.42 | 0.41 | 0.36 | 0.28 | **0.78** |

**The shape to look for in India:**
- Excess returns are roughly flat across deciles.
- Alphas and Sharpe ratios fall steadily from P1 to P10.
- Realised betas rise more than ex-ante betas.
- BAB has a beta near 0 and a Sharpe ratio of about 0.8.

### Table IV (T4, PDF 42): international deciles pooled, 1984–2012
- BAB earns 0.64 (t 4.66).
- Its CAPM α is 0.64 (4.68), 3-factor α 0.65 (4.81), and 4-factor α 0.30 (2.20).
- Volatility is 8.1% and the Sharpe ratio 0.95.
- From P1 to P10, the Sharpe ratio falls from 0.50 to 0.13 and the CAPM α from 0.45 to 0.00.

### Table V (T5, PDF 43): BAB by country
- BAB has a positive Sharpe ratio in 18 of 19 countries; Austria is the exception at −0.02 (p.22).
- Long and short sizes are typically about $1.4 long and $0.9 short.
- Sharpe ratios range from 0.08 (Australia) to 1.05 (Canada).
- The reader's count differs from the text: 12 positive 4-factor alphas, not the 13 the text gives. **An Indian BAB would add one row to this table.**

### Robustness tables relevant to India (Appendix B)
- **B2, beta windows** (PDF 67).
  - With a 5-year correlation window, US BAB earns 0.70 (t 7.12) with a Sharpe ratio of 0.78.
  - With a 3-year or 1-year window, it earns 0.76 (7.60) with a Sharpe ratio of 0.83.
  - This supports shorter correlation windows, which India's short UBI history would need.
- **B3, size** (PDF 68).
  - BAB works in every US size decile.
  - Small stocks: 1.11 a month, Sharpe ratio 0.65.
  - Large stocks: 0.25 a month, Sharpe ratio 0.25.
  - This matters for a tradeable large-cap Indian version.
- **B4, sub-periods** (PDF 69). BAB is positive in every US sub-period. In 1926–45 it was weak: 0.26, t 1.00.
- **B5, idiosyncratic volatility** (PDF 70). The US alpha survives within every idiosyncratic-volatility decile.
- **B6, risk-free rate** (PDF 71). Results barely change when T-bills are replaced with Libor, OIS or repo: US BAB goes from 0.70 to 0.66.
- **B9, value-weighted BAB** (PDF 74).
  - The beta-neutral US version earns 0.51 (t 5.22), with a 4-factor α of 0.45 and a Sharpe ratio of 0.57.
  - The dollar-neutral US version earns only 0.03 (t 0.20), although its 4-factor α is 0.45.
  - **The leverage to beta 1 is what makes the excess return.** This is central to a long-only Indian version, which cannot lever.

### Other tables (not planned for India)

| Table | What it shows | Headline |
|---|---|---|
| VI–VIII | BAB in Treasuries, credit, futures and combinations | Positive everywhere. Treasury BAB Sharpe 0.81; equity-index futures 0.51; all-asset combination 0.76. |
| IX | Funding liquidity | Lagged TED coefficient on US BAB −0.025 (t −5.24); ΔTED −0.019 (−2.58). |
| X | Beta compression | Cross-sectional beta dispersion falls when TED volatility is high: US P3−P1 standard deviation −0.05 (t −2.71). BAB's conditional beta rises in the high-TED-volatility regime: US P3−P1 0.45 (t 3.01). |
| XI | Holdings | Mutual fund betas 1.08; individual investors 1.25; LBO targets 0.83–0.96; Berkshire 0.77–0.91. |

## 5. Conclusions (p.33–34)
- High-beta assets have lower alphas and Sharpe ratios. The finding holds in US equities, 18 of 19 international markets, Treasuries, credit and futures.
- BAB factors earn significant risk-adjusted returns, comparable to value, momentum and size.
- Tighter funding (a higher TED spread) causes BAB losses, and higher funding-liquidity risk compresses betas toward 1.
- Constrained investors (mutual funds, individuals) hold high-beta portfolios. Leverage users (LBO funds, Berkshire) hold low-beta stocks and lever them: "Buffett bets against beta."

## 6. What a replication must decide (carried to the Adapt to India plan)

1. **Beta windows.**
   - The paper uses a 1-year volatility window and a 5-year correlation window.
   - UBI's daily history starts around December 2019. That allows a 5-year correlation from about end-2024, or a 3-year one from end-2022.
   - B2 supports a 3-year correlation window. NSE bhavcopies would allow the full 5 years from the mid-1990s.
2. **Market index and risk-free rate.**
   - Candidates for the market: NIFTY 500 TRI, or a value-weighted index built from the universe.
   - Candidates for the risk-free rate: the 91-day T-bill or overnight MIBOR. B6 suggests the choice matters little.
3. **Long-short in India.**
   - The short high-beta leg can only be stock futures or SLB, and both cover only F&O stocks.
   - The long leg is levered to beta 1, about 1.4×. That leverage needs futures or margin.
4. **Long-only.** Without leverage, the dollar-neutral result in B9 (0.03 a month) warns that a plain low-beta portfolio may not beat the market on raw return, only on risk-adjusted return. The comparison benchmark is the NIFTY100 Low Volatility 30.
5. **Factor models.** Fama–French and momentum factors for India are available from the IIMA library (Agarwalla, Jacob and Varma). India has no Pastor–Stambaugh liquidity factor.
6. **"J and K" for the companion site.**
   - J and K are the momentum paper's names; BAB has no direct equivalent.
   - J would map to the beta-estimation windows (volatility and correlation, in months).
   - K would map to the holding or rebalancing period, which the paper sets at 1 month.
   - Other settings to expose: the shrinkage weight w, the 1-day versus 3-day correlation returns, the universe size, and equal versus rank weighting.
