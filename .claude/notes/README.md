# Notes

One note per source file, mirroring the source tree, holding the reasoning behind it.

- Package name `frazzini_pedersen_betting_against_beta_india` follows the study-template rule `<first-author>_<second-author>_<topic>_india`; repository `Research-Paper-Frazzini-Pedersen-Betting-Against-Beta-India`.
- The user's PDF is the 10 May 2013 accepted draft (80 pages); the published version is JFE 111(1) 2014, pp. 1–25, DOI checked against Crossref on 2026-10-31. Page citations in this study refer to the draft's page numbers.
- The `bab-app` console script and site server are added at the Companion site stage, not now, so the package installs cleanly.
- `[tool.pytest.ini_options]` pins the rootdir to the project; without it pytest climbs to the read-only research-agent folder for its cache.
