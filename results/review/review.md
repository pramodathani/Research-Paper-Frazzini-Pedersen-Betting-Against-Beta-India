# Backtest review: BAB for NSE India (backtest_reviewer, 2026-11-01)

## Progress log
- Tests: `.venv/bin/python -m pytest -q` -> 76 passed in 4.5 s.
- Code read: portfolio_builder, rank_weights, strategy_runner, universes, beta_estimator, return_panel, bab_study, decile_table, tradeable_portfolios, daily_return_builder (cleaning), extra_tables (calendar years, size terciles), factor_alphas.
- Closes used in the universe price filter are raw (return_panel.py:24 `close: Raw closing prices`), so the Rs 2 filter has no look-ahead from back-adjustment.
- Return flags: 1,523 flagged days in total (inferred_action 495, kept_real_fall 375, zeroed 321, previous_close_repaired 245, zeroed_misprint 87).
- make_results.py:30 IMPACT = {'A': 0.003, 'B': 0.001, 'C': 0.001}; TradeablePortfolios.run_all defaults impact_futures=0.001, so T1 "after costs" uses 0.1% impact, not 0.3%.
- extra_tables.py:140 `compounded.where(counts == 12) if False else compounded` is dead code: part years (1999 Apr-Dec, 2026 Jan-Oct) are compounded as if they were whole years.

## Check results (scratch/review/check.py -> scratch/review/out.json)
- Reproduction: engine rerun of BAB A gross = 0.777%/month, NW t 3.60, max abs diff vs results/monthly_series_A.csv = 0.0.
- Hand check 2010-06: sum(w x excess, NaN->0) over 972 names = 0.025274 = periods value 0.025274 (2 names NaN that month).
- Weights (active months): long 1.234, short 0.757, net 0.477. That fits BAB on excess returns (not meant to sum to 1). Unpriced weight: mean 0.12% of gross, max 4.5%, 130 of 332 months > 0 (run_backtest warns the same).
- Costs, A, futures model: impact 0.003 net 0.62% (t 2.87), less 3.25% borrow 0.42% (t 1.92). Impact 0.006 (run_backtest, results/review/bab_A_futures_impact_0.006): net 0.49% (t 2.27), less borrow 0.29% (t 1.32). Turnover 0.427/month, one way 256%/yr, costs 3.40%/yr at 0.006. Unverified rates: futures STT on sells, exchange transaction charge.
- Implementability: after 2005-02 only 19.4% of A's short weight and 13.5% of its long weight are in F&O (universe C) names.
- Futures roll: C BAB gross notional ~1.88 (long 1.17, short 0.71). Reopening the full notional each expiry at the engine's 0.001 futures rate costs ~0.31%/month, or ~0.61% if both sides of the roll are charged. The engine charges only rebalancing: T1 gross 0.39 -> net 0.33 = 0.06%/month. Expiries and rolls are not modelled anywhere (grep 'expir|roll' in betting_against_beta/: none).
- Halves: 1999-04..2013 0.75% (t 2.07), 2013..2026-10 0.81% (t 3.41). From 2006 on: 0.72% (t 3.38). Dropping the best 5 months: 0.58% (t 2.80); best 10: 0.45% (t 2.21).
- Fragility (gross, A): price < Rs 10 excluded 0.70% (t 3.41); bottom third of traded value excluded 0.56% (t 2.62); bottom half excluded 0.48% (t 2.11); first trading day of the holding month skipped 0.75% (t 3.61); first 5 days skipped 0.51% (t 3.00; ~0.59 if returns were spread evenly over the month). Size terciles: least traded 1.02% (t 3.56), most traded 0.45% (t 1.77).
- Legs: median 252-day traded value of the low-beta half is Rs 2.47m against Rs 5.86m for the high-beta half. Rank correlation of beta with traded value is +0.13. Traded-day share ~99% in both halves, so the min-observation rules do not favour illiquid names after the A screen.
- Look-ahead in cleaning: flagged days inside held share-months are 5 zeroed_misprint (sum |w| 0.017) and 7 zeroed (0.012), so a -50% error on all of them moves the mean < 0.003%/month. Immaterial.
- IIMA factors: PeriodIndex 1993-10..2025-12, MF std 0.071 (decimals), corr with NIFTY 500 TRI excess 0.98. Aligned. Alphas leave out 2026-01..10.
- Grid: 864 variants, all means > 0, 646 with t > 2, 217 with t > 3, 29 with t > 3.85 (Bonferroni 5%/864). Median t by universe: A 3.21, B 2.21, C 2.09. Best: A, vol 6, corr 36, shrink 0.6, K 1, equal, t 4.73. The headline uses FP's own default specification, not the grid's best.
- L1 vs market over the same window 1999-04..2026-10: NIFTY 500 TRI excess 0.86%/month, Sharpe 0.43; L1 net 0.81%, Sharpe 0.47. From 2006 (tradeable_vs_benchmarks_2006.csv): L1 net Sharpe 0.38, NIFTY 500 TRI 0.36, NIFTY Low Vol 50 TRI 0.52. L1 CAPM alpha 0.13% (t 0.77), and -0.03% under the -100% delisting shock.
- Deciles A: excess returns are hump-shaped (P1 1.14%, P6 1.50%, P10 0.73%). CAPM alphas fall from +0.47% to -0.69%, so BAB comes mostly from the high-beta decile.

## Verdict: sound with caveats
The gross BAB construction is correct, has no look-ahead and holds up in both halves. The after-cost and tradeable claims (A after costs, T1, L1 vs market) are not yet reliable.

## Findings (most serious first)
1. MATERIAL (could be critical for T1): futures roll is not charged. T1 is charged only for rebalancing (0.06%/month). The ~1.88 gross notional must be reopened at every expiry, which costs ~0.31-0.61%/month at the 0.001 rate. T1 net 0.33% would then fall to about 0.0-0.1%. T1 also earns total-return (dividend-inclusive) excess returns, which a stock future does not pay (not quantified). Fix: model the monthly roll (rebalance at expiry), and use price-only returns plus the futures basis, or real futures closes from fno_members.
2. MATERIAL: "BAB A after costs" (0.42%, t 1.92) is not a tradeable portfolio. Since 2005 only 19% of its short weight and 14% of its long weight are in F&O names, yet it is charged futures costs and a 3.25% borrow fee as if SLB covered every name. At double impact it is 0.29% (t 1.32). Fix: present A after costs as a paper portfolio only; make T1 the tradeable headline.
3. MATERIAL: the premium sits in thinly traded shares. Least-traded tercile 1.02%, most-traded 0.45% (t 1.77). Dropping A's bottom third by traded value gives 0.56%; dropping the bottom half gives 0.48%, the same as B (0.47%). The low-beta half's median traded value is 42% of the high-beta half's. Fix: lead with B/C; report A with the liquidity screens.
4. MATERIAL: the L1 "beats the market" claim compares different windows (NIFTY 500 TRI from 1996-01). Over the same window, NIFTY 500 TRI excess is 0.86% with Sharpe 0.43, against L1 net 0.81% with Sharpe 0.47. CAPM alpha is 0.13% (t 0.77), and since 2006 L1 trails NIFTY Low Vol 50 TRI (Sharpe 0.38 vs 0.52). Fix: compare on the same window and report alpha and the low-vol index.
5. MINOR: the C "BAB after costs" row (bab_summary.csv) charges the 3.25% borrow fee on a futures portfolio and uses impact 0.001, while T1 uses 0.001 with no fee. Same strategy, two nets (0.14% vs 0.33%). Fix: one cost treatment for C.
6. MINOR: decile_table.py:93-96 averages long/short over all rows, including months with no position, so C shows 0.92/0.56 instead of ~1.17/0.71.
7. MINOR: extra_tables.py:140 dead code `... if False else compounded`: 1999 and 2026 part years are shown as full calendar years.
8. MINOR: unpriced weight in 130 months (mean 0.12%, max 4.5%) earns rf. The delisting stress (-100%) bounds the effect at 0.68%.
9. MINOR: IIMA factors end 2025-12, so the alphas leave out the 10 months of 2026. Futures STT 0.05% (2026 rate, unverified) is applied to all history, which is conservative.
10. MINOR: before 2006 NSE's corporate-action list is sparse (gaps register #31), so 1999-2005 returns are close to price-only. First-half t is 2.07.
No issue: look-ahead (raw closes for the Rs 2 filter, betas, universes, traded value and F&O on the formation day, held month t+1), the cleaning's 5-day lookahead (<0.003%/month), rank weights, K-overlap, the factor alignment, the hand-checked month and the tests (76 pass).
