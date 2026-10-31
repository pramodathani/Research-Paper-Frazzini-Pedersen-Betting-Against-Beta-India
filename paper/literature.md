# Literature around Betting Against Beta

**How this was compiled:** by the literature_scout subagent and checked by hand on 2026-10-31.
- **Confirmed:** the item exists (IDEAS/RePEc, publisher, Crossref or the author's page).
- **Abstract read:** a finding is stated only when its abstract was actually read.

## India: closest benchmarks

1. **Agarwalla, Jacob, Varma and Vasudevan (2014)**, "Betting Against Beta in the Indian Market".
   - Published as IIMA Working Paper WP2014-07-01 and on SSRN as 10.2139/SSRN.2464097. Later printed in Mishra et al. (eds), *The Financial Landscape of Emerging Economies*, Springer 2020, pp. 29–44.
   - **Abstract read** (jrvarma.in): an FP-style BAB factor "earns significant positive returns in India". Its returns "dominate the returns on the size, value and momentum factors", and higher-volatility stocks earn lower returns.
   - **This is the direct Indian benchmark.** Its full text could not be downloaded: the IIMA link returns 404 and SSRN returns 403.
2. **Tulsyan, Joshipura and Mishra (2025)**, "Does profitability explain the low-risk anomaly in India?", *QREF* 104:102060.
   - Abstract read, via the literature scout. Sample: NIFTY 500 stocks, March 2003 to June 2022.
   - The low-risk anomaly is present. Profitability moderates it but does not explain it.
3. **Khandelwal and Chotia (2022)**, "Is there a beta anomaly? Evidence from the India", *Annals of Financial Economics* 17:2250020, doi 10.1142/S2010495222500208.
   - From search snippets only: 265 firms, 2000–2019, and it finds no beta anomaly. **Contrary evidence**, from a small sample.
4. **Sehgal, Rakhyani and Deisting (2022)**, "Does betting against beta strategy work in major Asian markets?", *Pacific-Basin Finance Journal* 75:101824.
   - Confirmed on IDEAS; it cites Agarwalla et al. (2014).
   - Its five markets, and whether India is one of them, are **not verified**.
5. **Rakhyani, Sehgal and Deisting (2025)**, "Time-varying performance of betting against beta (BAB) and other …", *Journal of Behavioral and Experimental Finance* (ScienceDirect pii S2214845025000778).
   - Found by search. It covers beta, IVOL, MAX, skewness and tail-risk strategies. **Market coverage not verified.**
6. **IIMA Indian Fama–French–Momentum library** (Agarwalla, Jacob and Varma): https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/
   - Holds market, SMB, HML, WML and the risk-free rate from October 1993, with survivorship-bias-adjusted files.
   - **No BAB factor.** It is useful for the 3- and 4-factor alphas.
7. **NIFTY100 Low Volatility 30.**
   - Methodology: volatility is the standard deviation of daily log returns over the last year, and the 30 least volatile NIFTY 100 stocks are chosen (niftyindices.com factsheet; AMFI methodology document).
   - ETFs track it (Mirae, HDFC, ICICI and others).
   - **A natural long-only benchmark.** NIFTY Alpha Low-Volatility 30 is a related index.

## Replications and critiques
These are confirmed to exist; their abstracts were not read unless stated.
- **Novy-Marx and Velikov (2022)**, "Betting against betting against beta", *JFE* 143(1):80–106 (SSRN 3300965). The main construction critique: it targets the non-standard BAB construction, meaning the betas, the rank weights and the leverage, and its effective small-cap tilt and costs.
- **Cederburg and O'Doherty (2016)**, "Does it pay to bet against beta?", *JF* 71(2):737–774. On conditional betas.
- **Liu, Stambaugh and Yuan (2018)**, "Absolving beta of volatility's effects", *JFE* 128(1):1–15. Beta versus idiosyncratic volatility.
- **Schneider, Wagner and Zechner (2020)**, "Low-risk anomalies?", *JF* 75(5):2673–2718.
- **Bali, Brown, Murray and Tang (2017)**, "A lottery-demand-based explanation of the beta anomaly", *JFQA* 52(6):2369–2397. Relevant to India's large retail lottery demand.
- **Asness, Frazzini, Gormsen and Pedersen (2020)**, "Betting against correlation", *JFE* 135(3):629–652.
- **Novy-Marx and Velikov (2016)**, "A taxonomy of anomalies and their trading costs", *RFS* 29(1).
- **Barroso, Detzel and Maio (2025)**, "The volatility puzzle of the beta anomaly", *JFE* 165.
- **Xu (2025)**, "Market neutrality and beta crashes", *Journal of Empirical Finance* 80.
- **Traut (2023)**, "What we know about the low-risk anomaly: a literature review", *FMPM* 37(3):297–324. A survey.

## Background
- **Black, Jensen and Scholes (1972)**, "The capital asset pricing model: some empirical tests", in Jensen (ed.), *Studies in the Theory of Capital Markets*, 79–121.
- **Black (1972)**, "Capital market equilibrium with restricted borrowing", *Journal of Business* 45(3):444–455.
- **Vasicek (1973)**, *JF* 28(5):1233–1239. Beta shrinkage.
- **Ang, Hodrick, Xing and Zhang (2006)**, *JF* 61(1):259–299.
- **Baker, Bradley and Wurgler (2011)**, *FAJ* 67(1), doi 10.2469/faj.v67.n1.4.

## Short selling in India (for the Adapt to India stage)
- **Shorting overnight in cash equities:**
  - Not possible without borrowing the stock through SEBI's Securities Lending and Borrowing (SLB) scheme, which is limited to F&O stocks and often thinly traded.
  - Single-stock futures on the roughly 200 F&O stocks are the practical short leg.
- These are to be checked against primary SEBI and NSE sources at the next stage.
