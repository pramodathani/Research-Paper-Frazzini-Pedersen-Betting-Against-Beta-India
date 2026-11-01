# Betting Against Beta in India

A recreation of Frazzini and Pedersen's *Betting Against Beta* (Journal of Financial Economics, 2014) for shares listed on the National Stock Exchange of India, as a long-short factor and as a long-only portfolio that can be traded in India.

**In one line:** the low-beta anomaly is strong in India before costs, but the long-short factor does not survive Indian trading costs, and long-only low-beta portfolios give market-like returns with less risk rather than extra return.

## Results (April 1999 to October 2026, details in `results/summary.md`)

| Portfolio | Excess return before costs, %/month (NW t) | After costs | Sharpe after costs | Worst drawdown |
|---|---|---|---|---|
| BAB factor, all NSE shares (paper portfolio) | 0.78 (3.60) | 0.40 (1.82) | 0.39 | −39% |
| BAB factor, liquid 500 (paper portfolio) | 0.47 (2.02) | 0.18 (0.78) | 0.17 | −44% |
| T1: BAB through stock futures, F&O shares, from 2005 | 0.39 (1.59) | −0.02 (−0.07) | −0.02 | −51% |
| L1: lowest-beta 20% of the liquid 500, long only | 0.86 (2.11) | 0.81 (1.99) | 0.46 | −63% |
| NIFTY 500 TRI, same months | 0.86 (2.08) | | 0.43 | −65% |

- The paper's BAB factor in the US earns 0.70% a month with a Sharpe ratio of 0.78. Over all NSE shares, India's version is about as large before costs.
- The factor's return comes mostly from small, thinly traded shares and from the highest-beta decile's negative alpha.
- Of 864 variants tried, all are positive before costs. The headline is the paper's own setting, not the best variant.

**Caveats:**
- Short selling in cash shares is barely possible in India (thin SLB), so the factor in the first two rows cannot actually be built.
- Futures costs include a monthly roll, at an assumed 0.05% impact a side.
- Market cap is unavailable before 2024, so traded value stands in for size.
- Dividends are incomplete before 2006.
- The IIMA factors end in December 2025.
- A backtest reviewer checked the results; its findings and the fixes are in `results/summary.md` §8.

## The paper in brief

Frazzini and Pedersen argue that investors who cannot or will not borrow buy high-beta assets to reach the risk they want, which bids those assets up. High-beta assets therefore earn less than the capital asset pricing model predicts, and a betting-against-beta (BAB) factor that is long leveraged low-beta assets and short high-beta assets, each scaled to a beta of one, earns positive risk-adjusted returns.

## Status

The results are done and reviewed (`results/summary.md`). The interactive companion page is at https://tradingmachine.co.in/papers/frazzini-pedersen-betting-against-beta-india/.

## How the code is laid out

All code is in `src/frazzini_pedersen_betting_against_beta_india/`.

- `data/`: downloaders and parsers for NSE bhavcopies, corporate actions, F&O files, index files, RBI T-bill pages and SLB files.
- `betting_against_beta/`: the study.
  - Returns: `daily_return_builder.py`, `action_parser.py`, `symbol_changes.py`, `security_filter.py`, `return_panel.py`, `market_data.py`.
  - Beta and portfolios: `beta_estimator.py`, `beta_tables.py`, `universes.py`, `rank_weights.py`, `portfolio_builder.py`.
  - Scoring: `strategy_runner.py` (the shared backtest engine, before and after costs), `factor_alphas.py`, `decile_table.py`, `tradeable_portfolios.py`, `extra_tables.py`, `grid_runner.py`.
- `scripts/`: `build_returns.py`, `build_fno_membership.py`, `build_india_vix.py` and `run_grid.py`.

Run the tests with `python -m pytest`. They need no network.

## How to reproduce

```bash
python -m venv .venv && .venv/bin/pip install -e ".[test]"
.venv/bin/pip install -e /path/to/data-and-analytics --no-deps   # the shared backtesting engine
python -m frazzini_pedersen_betting_against_beta_india.scripts.download_nse      # NSE bhavcopies, F&O, corporate actions
python -m frazzini_pedersen_betting_against_beta_india.scripts.download_indices  # niftyindices.com total-return indices
python -m frazzini_pedersen_betting_against_beta_india.scripts.download_tbills   # RBI 91-day T-bill auctions
python -m frazzini_pedersen_betting_against_beta_india.scripts.download_slb      # SLB lists and bhavcopies
python -m frazzini_pedersen_betting_against_beta_india.scripts.build_returns
python -m frazzini_pedersen_betting_against_beta_india.scripts.build_fno_membership
python -m frazzini_pedersen_betting_against_beta_india.scripts.build_india_vix
python -m frazzini_pedersen_betting_against_beta_india.scripts.estimate_borrow_fee
python -m frazzini_pedersen_betting_against_beta_india.scripts.make_results
python -m frazzini_pedersen_betting_against_beta_india.scripts.run_grid
python -m frazzini_pedersen_betting_against_beta_india.scripts.build_snapshot
bab-india-app   # serves the companion page locally
```

Exchange data are downloaded into the git-ignored `data/` folder and are not redistributed. The IIMA factor file is fetched by `download_nse` (see `data/README.md`).

## Shared databases

`scripts/store_shared_results.py` writes to the Research Analysts' shared places only. It upserts, so it is safe to run again.
- **TimescaleDB `results.strategy_returns`:** monthly returns before and after costs for the BAB factor (universes A, B, C) and T1, T2, L1, L2 and L3, with the NIFTY 500 TRI as benchmark. They come from `results/monthly_series_*.csv` and `results/tradeable_monthly.csv`.
- **MongoDB and ChromaDB `findings`:** six findings with ids `betting-against-beta-research-paper:<slug>`.

The study keeps no private schema or collection; everything can be rebuilt from `results/`.

## Citation

See `CITATION.cff`. Please also cite the original paper:

Frazzini, A., and Pedersen, L. H. (2014). Betting against beta. *Journal of Financial Economics*, 111(1), 1–25. https://doi.org/10.1016/j.jfineco.2013.10.005
