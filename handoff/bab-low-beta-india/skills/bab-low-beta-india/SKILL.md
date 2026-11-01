---
name: bab-low-beta-india
description: Use when building or rebalancing the monthly long-only low-beta sleeve in Indian shares, which holds the fifth of the 500 most traded NSE shares with the lowest beta against the NIFTY 500, equally weighted, for one month at a time, with an optional NIFTY futures overlay that lifts its beta to one. Gives the strategy, the command that builds each month's target weights, suggested risk limits, the capital minimum and the backtest results.
---

# Betting against beta, long leg only: low-beta NSE shares

## Strategy

Frazzini and Pedersen (2014) found that high-beta assets earn less than their risk deserves, because investors who cannot borrow buy high-beta assets to get more return. Their betting-against-beta (BAB) factor is long levered low-beta assets and short de-levered high-beta assets. A study recreating it on NSE shares from 1999 to 2026 found the same pattern before costs, but also that the long-short factor cannot be held in India after costs: cash shorts need securities lending, which covers a few hundred shares thinly, and stock futures cost about as much a month in rolling as the factor earns. What an Indian delivery investor can hold is the long leg, and that is what this skill builds.

- **Universe:** the 500 NSE company shares with the highest median daily traded value over the last 252 trading days, among those with a last close of at least 2 rupees that traded on at least half of those days and in each of the last 5 days. Funds and rights entitlements are removed. About 420 of them have enough history to get a beta.
- **Signal:** each share's beta against the NIFTY 500, as in the paper: the correlation of overlapping three-day log returns over the last 60 months, times the ratio of the share's volatility to the market's over the last 12 months (daily log returns), shrunk towards one, 0.6 times beta plus 0.4.
- **Portfolio:** at each month-end, take the fifth of the ranked shares with the lowest beta, about 85, in equal weights, about 1.2% each. Hold them for the next month.
- **Rebalance:** once a month, on the first trading day after a month ends. About 11% of the portfolio is sold and 11% bought each month.
- **Optional overlay (portfolio L3):** buy NIFTY futures worth (1 / the holdings' average beta minus 1) of capital, capped at 1.5, which lifts the portfolio's beta to about one. The script prints the number. The study found the overlay raises the return but not the risk-adjusted return after costs, so it is the user's choice.
- **Long only, delivery (CNC) only** for the shares. The paper's short leg is not used.

The full explanation, with the formulas, risks and sources, is in `references/strategy_brief.md` (the same as a page in `references/strategy_brief.html`). The paper is Frazzini and Pedersen (2014), *Journal of Financial Economics* 111(1), 1-25. The study, its code and its results are at https://github.com/pramodathani/Research-Paper-Frazzini-Pedersen-Betting-Against-Beta-India, with an interactive page at https://tradingmachine.co.in/papers/frazzini-pedersen-betting-against-beta-india/.

**What to expect, plainly.** This is a lower-risk way to hold Indian equity, not an extra-return strategy. Over 1999 to 2026 it earned about the market's return (14.7% a year after costs against 14.6% for the NIFTY 500 total return index) with a beta of 0.77 and 12% less volatility, and its alpha was not significantly different from zero. NSE's own low-volatility indices did as well or better from 2006. A desk should compare this sleeve with those indices before building it.

## Monthly target command

```
python scripts/build_targets.py targets_2026-11.csv --previous targets_2026-10.csv --capital 1000000
```

- **Needs:** Python with pandas and numpy, and `tradingmachine` configured for UBI, which trading-agent's sandbox has. The script reads UBI's NSE equity master and the daily candles of every listed share in batches, adjusted for splits and bonuses, for about 5.5 years, and the NIFTY 500 index.
- **When:** on the first trading day after a month ends, after UBI holds that month's last prices. The script refuses to run if the data stops more than four days before the end of the last completed month, and says so. Use `--as-of YYYY-MM-DD` to rebuild a past month.
- **Writes:** the CSV named first, with columns `symbol,weight`, sorted by symbol, with weights adding up to 1.
- **Prints:** the formation date, the number of ranked shares, the number of holdings, the largest weight, the holdings' average beta, the optional overlay, price moves dropped as adjustment errors, the joiners and leavers against `--previous`, and the one-way turnover. With `--capital` it also prints how much of that capital whole shares can invest and how many targets round to zero shares.
- **Options:** `--prices-file` and `--index-file` read parquet or CSV files (symbol,date,close,volume and date,close) instead of UBI, for testing; `--exclude SYMBOL ...` keeps shares out.
- **Time:** about 2 seconds to build the targets from a file of 2.9 million candles; the fetch from UBI comes on top and was not timed, because UBI cannot be reached from the research sandbox where the script was written.
- **It never places, modifies or cancels orders.** Trading-agent's desks decide what to trade.

Check the first run by hand: around 70 to 100 holdings, each weight near 1.2%, an average beta near 0.8 and a one-way turnover of 10% to 20% against last month's file. UBI prices are adjusted for splits and bonuses but not dividends, and its split factors are sometimes misdated (the study's gap 32), so the script drops any one-day move below -45% or above +100% and lists the shares; the build for October 2026 dropped one move, in VEDL on 30 April 2026.

## Risk limits

These are suggestions for the user to put into trading-agent's TradingRules.md; the study did not impose them.

- **Per share:** at most 2.5% of the portfolio. The equal weight is about 1.2%.
- **Per sector:** at most 30%. The study had no sector data and imposed no limit; check sector weights by hand the first few months.
- **Holdings:** expect 70 to 100. Treat fewer than 40 or more than 130 as a data fault and stop.
- **Order size:** at most 2% of a share's median daily traded value. The holdings' median daily traded value starts at about Rs 20 crore, so this is rarely binding.
- **Turnover:** at most 40% two-way in a month; the backtest average is 23%.
- **Leverage:** none for the shares. The NIFTY futures overlay is optional and needs the user's explicit approval; cap it at 0.5 of capital in a first run.
- **Drawdown:** the portfolio lost 60% from December 2007 to February 2009, as the market did, and returned -26% in 2000, -17% in 2001, -55% in 2008 and -24% in 2011. Suggest a review with the user at 25% below its previous peak. It is a market-like portfolio, not a hedge.

## Capital minimum

About 84 shares are held in the October 2026 build, each near 1.2% of capital. Whole shares then decide the minimum, because some of the lowest-beta shares trade at very high prices (the median price of the holdings is about Rs 1,500; the highest is above Rs 1 lakh):

- **Rs 5 lakh:** the smallest position is about Rs 6,000, 10 of 84 targets round to zero shares, and 77% of the money is invested.
- **Rs 10 lakh:** the smallest position is about Rs 12,000, 6 targets round to zero, and 86% is invested. This is the lowest workable capital.
- **Rs 25 lakh:** 2 targets round to zero and 93% is invested. This is the suggested starting capital.
- **Costs that do not scale:** depository charges of about Rs 15 plus GST on each share sold, about 10 sales a month, come to roughly Rs 150 a month, which the study's cost model does not include.

Below Rs 10 lakh the whole-share rounding makes the portfolio different from the one backtested. With the overlay, add the margin for one NIFTY futures lot per roughly Rs 20 lakh of overlay notional.

## Backtest summary

Universe B (liquid 500), long only, beta rank, equal weights, one-month holding, after Indian delivery costs (STT, stamp duty, exchange and SEBI charges, GST, market impact 0.1% per side, zero brokerage). Holding months April 1999 to October 2026, 331 months, delisted shares included.

| | Low-beta fifth (L1) | NIFTY 500 TRI |
|---|---|---|
| Compound annual return, total return | 14.7% | 14.6% |
| Mean excess return a month (Newey-West t) | 0.81% (1.99) | 0.86% (2.08) |
| Volatility a year, excess returns | 20.9% | 23.9% |
| Sharpe ratio | 0.46 | 0.43 |
| CAPM beta | 0.77 | 0.99 |
| Four-factor alpha a month (t) | 0.27% (1.99) | 0.06% (0.98) |
| Worst drawdown, total return | -59.7% (Dec 2007 to Feb 2009) | -60.4% |
| Turnover a month, two-way | 0.23 | |
| Costs a month | 0.05% | |
| Holdings | 85 on average | |

From 2006 the Sharpe ratios are 0.38 for L1 after costs against 0.36 for the NIFTY 500, and 0.52 to 0.53 for NSE's two low-volatility indices. With a loss of 100% charged to every share the month it stopped trading, L1's mean excess return falls from 0.81% to 0.65% a month (t 1.62).

With the NIFTY futures overlay (L3, beta 1.13) the mean excess return after costs is 1.05% a month (t 1.90), the Sharpe ratio 0.44, the four-factor alpha 0.26% (t 1.74), the CAPM alpha about zero and the worst drawdown about -76%. The overlay is charged futures costs and a monthly roll.

**Reviewer's verdict.** The backtest_reviewer subagent confirmed that the factor reproduces exactly, has no look-ahead and holds up in both halves of the sample; its findings on costs, liquidity and the benchmark comparison were fixed before these numbers were produced. Longer tables are in `references/backtest_summary.md`.

**Main caveats:**
- The low-beta fifth earns the market's return with less risk. The study found no significant alpha after costs, so this is a risk choice, not an edge.
- The long-short BAB factor, which carries the paper's result, is not what this skill holds; it did not survive costs in India.
- Returns before 2006 are close to price-only, because NSE's corporate action list lacks early dividends, and the beta estimates before 2005 use fewer shares.
- The script's prices come from UBI, which has no dividends and some wrong split adjustments; its portfolio for a past month matched the study's NSE-based portfolio on most, but not all, shares (see `references/backtest_summary.md`).
- Costs assume 0.1% market impact a side; the liquid 500 can cost more in stress.
