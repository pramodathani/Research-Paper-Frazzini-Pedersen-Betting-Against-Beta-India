# Betting Against Beta in India

A recreation of Frazzini and Pedersen's *Betting Against Beta* (Journal of Financial Economics, 2014) for shares listed on the National Stock Exchange of India, as a long-short factor and as a long-only portfolio that can be traded in India.

**In one line:** the study is in progress; results will appear here.

## The paper in brief

Frazzini and Pedersen argue that investors who cannot or will not borrow buy high-beta assets to reach the risk they want, which bids those assets up. High-beta assets therefore earn less than the capital asset pricing model predicts, and a betting-against-beta (BAB) factor that is long leveraged low-beta assets and short high-beta assets, each scaled to a beta of one, earns positive risk-adjusted returns.

## Status

Build and test is done: the tested package exists, the grid of 864 variants has run, and the results stage will report and review the numbers. Nothing is published yet.

## How the code is laid out

All code is in `src/frazzini_pedersen_betting_against_beta_india/`.

- `data/`: downloaders and parsers for NSE bhavcopies, corporate actions, F&O files, index files, RBI T-bill pages and SLB files.
- `betting_against_beta/`: the study.
  - Returns: `daily_return_builder.py`, `action_parser.py`, `symbol_changes.py`, `security_filter.py`, `return_panel.py`, `market_data.py`.
  - Beta and portfolios: `beta_estimator.py`, `beta_tables.py`, `universes.py`, `rank_weights.py`, `portfolio_builder.py`.
  - Scoring: `strategy_runner.py` (the shared backtest engine, before and after costs), `factor_alphas.py`, `decile_table.py`, `tradeable_portfolios.py`, `extra_tables.py`, `grid_runner.py`.
- `scripts/`: `build_returns.py`, `build_fno_membership.py`, `build_india_vix.py` and `run_grid.py`.

Run the tests with `python -m pytest`. They need no network.

## Citation

See `CITATION.cff`. Please also cite the original paper:

Frazzini, A., and Pedersen, L. H. (2014). Betting against beta. *Journal of Financial Economics*, 111(1), 1–25. https://doi.org/10.1016/j.jfineco.2013.10.005
