# Data

Everything here except this file is git-ignored. Raw files are exactly as the source served them, fetched on 2026-10-31 and 2026-11-01. NSE and RBI files are never published; only derived results are. The downloaders are in `src/frazzini_pedersen_betting_against_beta_india/data/` and run through `scripts/download_*.py`; each skips files already on disk, so a stopped download is simply started again. The NSE bhavcopy, F&O, index, corporate action and IIMA files were copied from the Jegadeesh and Titman study's `data/nse/` (fetched on 2026-10-31 with the same downloader code, unchanged), so they were not downloaded twice.

| Path | What | Source | Period | Count |
|---|---|---|---|---|
| `ubi/instruments_nse_equities.parquet` | UBI instrument master, NSE shares | `export_instruments` (nse, equities) | listed today | 3,543 instruments |
| `ubi/prices_nse_equities_day_adjusted.parquet` | Daily candles adjusted for splits and bonuses, not dividends. Cross-check only (gap 32) | `export_prices` (nse, equities, day) | 2019-12-03 to 2026-10-29 | 2,962,743 candles, 2,607 shares; 914 of 3,521 asked-for symbols have none |
| `nse/bhavcopy/` | Daily cash-market bhavcopy zips (old format to 2024-07-05, UDiFF after). The price source | `nsearchives.nseindia.com/content/historical/EQUITIES/...`, `/content/cm/BhavCopy_NSE_CM_...` | 1996-01-01 to 2026-10-30 | 7,628 files, 10,735,705 EQ/BE/BZ rows, 5,723 symbols; weekdays without a file are in `not_available.txt` |
| `nse/fno/` | Daily F&O bhavcopy zips (stock futures for the futures overlay and the F&O universe) | `.../historical/DERIVATIVES/...`, `/content/fo/BhavCopy_NSE_FO_...` | 2005-01-03 to 2026-10-30 | 5,387 files |
| `nse/index/` | `ind_close_all`: every NSE index's close, P/E, P/B, dividend yield (includes India VIX) | `.../content/indices/ind_close_all_DDMMYYYY.csv` | 2012-02-21 to 2026-10-30 | 3,612 files |
| `nse/corporate_actions/` | NSE corporate actions API, one JSON per year (splits, bonuses, dividends) | `nseindia.com/api/corporates-corporateActions` | 2000 to 2026 (ex-dates to Nov 2026) | 27 files, 42,899 rows |
| `nse/iima/` | IIMA four-factor monthly file (SMB, HML, WML, MF, RF in percent), survivorship-bias adjusted, release 2025-12 | `faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/DATA/` | 1993-10 to 2025-12 | 387 months |
| `nse/fo_lot_sizes/fo_mktlots_2026-10-31.csv` | Today's F&O lot sizes by contract month. A snapshot only (gap 33); past lot sizes come from the `NewBrdLotQty` column of UDiFF F&O bhavcopies (July 2024 on) | `nsearchives.nseindia.com/content/fo/fo_mktlots.csv` | 2026-10-31 | 225 data rows |
| `nse/slb_eligibility/` | List of shares and series eligible for securities lending and borrowing (SLB), one file from each month's last trading day | `.../archives/slbs/seclist/SLB_ELG_SEC_DDMMYYYY.csv` | 2008-04-30 to 2026-10-30 | 223 monthly files; 2008-01 to 2008-03 not served |
| `nse/slb_bhavcopy/` | SLB bhavcopy, one per month: trades, fee in rupees per share to series expiry, open positions | `.../archives/slbs/bhavcopy/SLBM_BC_DDMMYYYY.DAT` | 2010-09-29 to 2026-10-30 | 190 monthly files; 2010-12, 2011-03, 2011-07 and 2011-08 not served. Few shares trade (gap 33) |
| `niftyindices/total_return/` | Total-return index levels (`TotalReturnsIndex`; `NTR_Value` for the NIFTY 500 from some date), five-year JSON chunks | niftyindices.com `getTotalReturnIndexString` | see below | 8 indices |
| `niftyindices/price/` | Price index OHLC, five-year JSON chunks | niftyindices.com `getHistoricaldatatabletoString` | see below | 4 indices |
| `rbi/tbill_auctions/` | RBI press release pages for the weekly 91-, 182- and 364-day T-Bill auction result; `RbiTbillParser` reads the 91-day cut-off yield | `rbi.org.in/scripts/BS_PressReleaseDisplay.aspx?prid=N`, numbers 61900 to 63900 scanned | 2026-01-07 to 2026-10-28 | 40 auctions. Missing weeks: 2026-03-25, 2026-04-01 and 2026-10-21 (no 91-day yield on the page) |
| `fred/IRSTCI01INM156N.csv` | India immediate (call money) rate, monthly. Low quality: flat 5.5000 for months in 2026, looks like the repo rate. Kept only as a fallback | FRED | 1968-01 to 2026-09 | 705 months |
| `nse/symbol_changes/symbolchange.csv` | NSE list of symbol renames, to link shares across renames before ISINs exist | `nsearchives.nseindia.com/content/equities/symbolchange.csv` | 2026-10-31 snapshot | 1,078 rows |
| `coverage.json` | Shares, trading days and ISIN share of rows per year, from the bhavcopies; made by `scripts/check_coverage.py` | derived | 1996 to 2026 | |

## Index history (niftyindices.com)

Dates counted from the saved chunks; all run to 2026-10-30.

| Index | Total return from | Total return rows | Price from |
|---|---|---|---|
| NIFTY 500 | 1995-01-01 | 7,888 | 1995-01-01 |
| NIFTY 50 | 1999-06-30 | 6,800 | 1995-01-01 |
| NIFTY 100 | 2003-01-01 | 5,922 | not downloaded |
| NIFTY 200 | 2004-01-01 | 5,668 | not downloaded |
| NIFTY MIDCAP 100 | 2003-01-01 | 5,922 | not downloaded |
| NIFTY SMALLCAP 100 | 2004-01-01 | 5,668 | not downloaded |
| NIFTY LOW VOLATILITY 50 | 2003-12-31 | 5,669 | 2003-12-31 |
| NIFTY100 LOW VOLATILITY 30 | 2005-04-01 | 5,353 | 2005-04-01 |

The NIFTY 500 total return index is the plan's market benchmark for the whole sample. The two low-volatility indices are real-world comparisons for the long-only portfolios (their pre-launch history is back-calculated by NSE). India VIX is not downloaded from niftyindices.com (its endpoint returned an HTML page for every payload tried); `ind_close_all` carries India VIX from 2012.

## Coverage (from the bhavcopies)

Shares trading with series EQ, BE or BZ, by year. This includes ETFs and other funds in EQ (the Build stage removes them by ISIN prefix INF and name patterns) and shares later delisted. Full table in `coverage.json`.

| Year | Shares | Days | | Year | Shares | Days |
|---|---|---|---|---|---|---|
| 1996 | 1,456 | 249 | | 2012 | 1,628 | 247 |
| 2000 | 1,263 | 250 | | 2016 | 1,708 | 246 |
| 2005 | 957 | 249 | | 2020 | 1,865 | 250 |
| 2008 | 1,340 | 246 | | 2023 | 2,313 | 245 |
| 2010 | 1,520 | 251 | | 2026 | 3,086 | 204 |

ISINs are in every row from 2012 (53% of 2011 rows, none before), so renamed shares before 2011 are not linked by ISIN. NSE has every session in the 2022 gap that UBI lacks (15 Feb to 7 Mar 2022). SLB-eligible symbols: 221 on 2008-04-30, 185 on 2010-02-26, 361 on 2015-12-31, 458 on 2020-12-31, 1,135 on 2026-10-30.

## Known problems

1. **UBI prices are a cross-check, not the source.** The Jegadeesh and Titman study measured (Dec 2019 to Oct 2026, 2,530 shares in both) 189 persistent steps in the UBI/NSE price ratio in 72 shares that match no NSE action, and 121 of 591 NSE splits and bonuses with no UBI step (gap 32). Returns are built from NSE bhavcopies adjusted with NSE's corporate action list. UBI also lists today's symbols only (survivorship bias) and starts in December 2019.
2. **Corporate actions before 2006 are too thin to adjust prices** (2005: 1 bonus, no splits; gap 31). Extreme one-day moves are screened in the Build stage, and early years are reported as a less reliable extension.
3. **Total returns need dividends.** Bhavcopy and UBI prices exclude them; dividends come from the corporate action list's text. NSE total-return indices are used for benchmarks only.
4. **Risk-free rate.** IIMA `RF` covers 1993-10 to 2025-12. The 2026 months use the mean of the month's RBI 91-day cut-off yields from the scraped auction pages, divided by 12 (the same simple approach, to be checked against IIMA's RF in the overlap before use). There is no scriptable earlier T-bill series other than IIMA's.
5. **Funding-liquidity test (approved by the user).** The certificate-of-deposit rate is not scriptable (gap 34), so the CD-minus-T-bill spread cannot be built yet. The Build stage will either find a source or report the test as not done; the FRED call-money fallback is poor.
6. **SLB is thin.** Eligible symbols grew from 221 (2008) to 1,135 (2026), but few trade in SLB, so the data tell what could be borrowed, not that it could be borrowed in size. The fee is in rupees per share to expiry; annualise as fee / price * 365 / days to expiry.
7. **Lot sizes** are today's only; earlier ones are in the UDiFF F&O bhavcopy from July 2024 (gap 33).
8. **Market capitalisation** is not downloaded; size groups use median traded value.
9. **Delisted shares** are in the NSE files (5,723 distinct symbols against about 3,100 trading in 2026), but their final-trade losses are not recorded; the Build stage states its delisting assumption.
