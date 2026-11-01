"""Tests of the hand-off brief's HTML builder."""

from pathlib import Path

import pandas as pd

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.brief_page import (
    BriefPage,
)

MARKDOWN = """# A strategy

## Summary

Some **bold** text, `code` and a link https://example.com/page.

- first
- second

| | a | b |
|---|---|---|
| row | 1 | 2 |

## Risks and caveats

Careful.
"""


def test_the_page_is_self_contained(tmp_path):
    page = BriefPage(tmp_path).build(MARKDOWN)
    assert page.startswith('<!doctype html>')
    assert '<script' not in page
    assert '<h2>Summary</h2>' in page
    assert '<b>bold</b>' in page and '<code>code</code>' in page
    assert '<li>first</li>' in page
    assert '<th>a</th>' in page and '<td>1</td>' in page


def test_the_chart_goes_before_the_risks_section(tmp_path: Path):
    months = pd.period_range('2000-01', periods=24, freq='M').astype(str)
    pd.DataFrame({'L1_net': 0.01}, index=months).to_csv(
        tmp_path / 'tradeable_monthly.csv'
    )
    pd.DataFrame({'NIFTY 500 TRI': 0.008}, index=months).to_csv(
        tmp_path / 'benchmarks_monthly.csv'
    )
    page = BriefPage(tmp_path).build(MARKDOWN)
    assert page.index('<svg') < page.index('<h2>Risks and caveats</h2>')
    assert page.count('<polyline') == 2
