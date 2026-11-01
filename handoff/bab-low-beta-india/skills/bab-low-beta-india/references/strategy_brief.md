# Low-beta NSE shares, long only: the betting-against-beta long leg (Frazzini and Pedersen, 2014)

## Summary

Hold the fifth of the 500 most traded NSE shares with the lowest beta, equally weighted, rebuilt every month, in delivery (CNC) only. The idea comes from Frazzini and Pedersen's betting-against-beta (BAB) factor, which is long low-beta and short high-beta assets and earns positive risk-adjusted returns because investors who cannot borrow overpay for high beta. Recreated on NSE shares from April 1999 to October 2026, the paper's long-short factor earns 0.78% a month before costs (Newey-West t 3.60) in all NSE shares, but its tradeable forms (stock futures, or cash shorts through securities lending) earn about nothing after Indian costs. The long-only low-beta fifth earns the market's return with less risk: 14.7% a year after costs against 14.6% for the NIFTY 500 total return index, with a beta of 0.77 and volatility 12% lower. Its four-factor alpha is 0.27% a month (t 1.99), which is marginal evidence, not proof, of an edge. Treat it as a lower-risk way to hold Indian equity and compare it with NSE's own low-volatility indices, which did as well or better from 2006.

## Universe

- **Eligible shares:** NSE company shares in series EQ, BE or BZ (funds, exchange traded funds and rights entitlements are removed) with a last close of at least 2 rupees, a close on at least half of the last 252 trading days, and a close on each of the last 5 days.
- **Ranked universe:** among those, the 500 with the highest median daily traded value (close times volume) over the last 252 trading days, counting days without trading as zero. It is rebuilt each month.
- **Size:** 500 shares, of which about 420 had enough history for a beta in October 2026.
- **Delisted shares** are included in the backtest. In live use the universe is whatever UBI lists.

## Signal

Each ranked share gets a beta against the NIFTY 500 at the last trading day of the month, using only data up to and including that day:

1. **Returns:** daily log returns from closes adjusted for splits and bonuses. A return on the day a share trades again is measured from its last close. One-day moves below -45% or above +100% are dropped as adjustment errors.
2. **Volatilities:** the standard deviation of each share's daily log returns, and of the market's, over the last 252 trading days; at least 120 share returns are required.
3. **Correlation:** the correlation between the share's and the market's overlapping three-day log returns (sums of three consecutive daily log returns) over the last 1,260 trading days, about 60 months; at least 756 three-day returns are required. Three-day returns allow for shares that trade late.
4. **Raw beta:** correlation times share volatility divided by market volatility.
5. **Shrunk beta:** 0.6 times raw beta plus 0.4 (the paper's weight; any weight above zero gives the same ranking).

The data needed are daily closes and volumes of every NSE share and the NIFTY 500 index's daily close, for about 5.5 years.

## Portfolio construction

- Rank the shares that have a beta, from the lowest to the highest.
- Hold the lowest-beta fifth, rounded to the nearest whole share count (84 of 420 in October 2026), each at weight 1 divided by the count, about 1.2%.
- No sector or single-share caps were imposed in the study. Suggested caps are in the skill.
- **Optional overlay (L3):** a long NIFTY 50 or NIFTY futures position of (1 divided by the holdings' average shrunk beta, minus 1) times capital, capped at 1.5 times capital, so that the portfolio's beta is about one. In October 2026 the holdings' average beta is 0.82, which gives 0.22. After costs the overlay raised the return to 1.05% a month but not the Sharpe ratio, and the portfolio's CAPM alpha was about zero.

## Rebalancing

- **When:** on the first trading day after each month ends, using the last trading day's prices of the month. The study forms the portfolio at that close and holds it through the next month; a live desk trades at the next day's prices, which the study's robustness check found barely changes the result (skipping the first day gave 0.75% against 0.78% for the long-short factor).
- **How:** rebalance every share to its new equal weight. About 11% of the portfolio is sold and 11% bought each month (two-way turnover 0.23).
- **A share that stops trading:** the study keeps its last return and charges nothing more. With a further 100% loss charged to every share in the month it stopped trading, the mean excess return falls from 0.81% to 0.65% a month.
- **No overlapping holdings:** each month's portfolio replaces the last.

## Backtest results

Universe: the 500 most traded NSE shares. Long only, delivery, equal weights, one-month holding, after Indian delivery costs (brokerage 0, securities transaction tax 0.1% each side, stamp duty, exchange and SEBI charges, GST, market impact 0.1% a side). 331 months, April 1999 to October 2026. Excess returns are over the 91-day Treasury bill; t-statistics use Newey-West standard errors with six lags.

| | Low-beta fifth (L1) | Rank-weighted half (L2) | L1 plus NIFTY futures (L3) | NIFTY 500 TRI |
|---|---|---|---|---|
| Months | 331 | 331 | 331 | 331 |
| Compound annual return | 14.7% | 15.7% | 15.8% | 14.6% |
| Mean excess return a month | 0.81% | 0.91% | 1.05% | 0.86% |
| Newey-West t | 1.99 | 2.07 | 1.90 | 2.08 |
| Volatility a year | 20.9% | 22.5% | 28.8% | 23.9% |
| Sharpe ratio | 0.46 | 0.48 | 0.44 | 0.43 |
| CAPM beta | 0.77 | 0.84 | 1.13 | 0.99 |
| Four-factor alpha a month (t) | 0.27% (1.99) | 0.31% (2.36) | 0.26% (1.74) | 0.06% (0.98) |
| Worst drawdown, total return | -59.7% | -63.6% | -75.7% | -60.4% |
| Turnover a month, two-way | 0.23 | 0.18 | 0.23 | |
| Costs a month | 0.05% | 0.04% | 0.10% | |

From 2006 (250 months): L1 after costs earns 0.62% a month (t 1.46) with a Sharpe ratio of 0.38, the NIFTY 500 TRI 0.66% (t 1.56) and 0.36, NSE's Low Volatility 50 TRI 0.77% (t 2.20) and 0.52, and the NIFTY100 Low Volatility 30 TRI 0.76% (t 2.32) and 0.53.

The study tried 864 variants of the long-short factor, 18 beta-window settings for each of three universes, and the screens and stress tests listed in the results; this long-only portfolio is one of five tradeable portfolios fixed in the plan before any run, and its settings are the paper's own. Drawdowns for L2 and L3 are computed on total returns from the monthly series.

## Risks and caveats

- **It is a market-like portfolio.** It fell 60% from December 2007 to February 2009, as the market did, and returned -26% in 2000, -17% in 2001, -55% in 2008 and -24% in 2011. A low beta does not protect in a crash that hits everything.
- **The evidence for an edge is modest.** The alpha of 0.27% a month (t 1.99) is borderline and falls to 0.12% (t 0.88) if every share that stopped trading loses 100% the month it vanishes. The equity return is the market's, within noise.
- **The long-short factor is not what is held.** It earns 0.78% a month before costs, but its legs cannot be held in India after costs, and it comes mostly from thinly traded shares and from the highest-beta decile's poor returns.
- **Betas are noisy and move.** The portfolio's realised beta over the sample is 0.77, and its estimated beta in any one month differs from that (0.82 in October 2026). Betas bunch towards one in volatile months, so the protection varies.
- **Data limits.** UBI prices have no dividends and some misdated split adjustments; the script drops one-day moves beyond -45% and +100%. Returns before 2006 are close to price-only because NSE's corporate action list lacks early dividends. Market capitalisation is not available before 2024, so the universe uses traded value.
- **Costs are assumed.** Market impact is 0.1% a side for the liquid 500. The 2026 futures transaction tax rate used for the overlay is unverified in the cost model.
- **Sample.** 27 years, with two crashes (2000 to 2001 and 2008). One more crash of that size is not in the sample.
- **Funding liquidity** was not tested: there is no downloadable Indian certificate-of-deposit rate.

## Sources

- **Paper:** Frazzini, A., and Pedersen, L. H. (2014). Betting against beta. *Journal of Financial Economics*, 111(1), 1-25. https://doi.org/10.1016/j.jfineco.2013.10.005 (equations 14 and 15, pages 16 to 18 of the May 2013 draft, give the beta).
- **Earlier Indian study:** Agarwalla, S. K., Jacob, J., Varma, J. R., and Vasudevan, E. (2014). Betting against beta in the Indian market. IIMA Working Paper 2014-07-01.
- **Study repository:** https://github.com/pramodathani/Research-Paper-Frazzini-Pedersen-Betting-Against-Beta-India; interactive page: https://tradingmachine.co.in/papers/frazzini-pedersen-betting-against-beta-india/.
- **Data:** NSE bhavcopies and corporate actions (backtest); UBI daily candles through tradingmachine (the target script); niftyindices.com total-return indices; IIMA factor library; RBI Treasury bill auctions.
