"""Tests of the RBI T-Bill auction page parser on a made-up page."""

from pathlib import Path

from frazzini_pedersen_betting_against_beta_india.data.rbi_tbill_parser import (
    RbiTbillParser,
)

PAGE = (
    '<html><body><td> Date : Oct 28, 2026 </td><p>91-Day, 182-Day and 364-Day '
    'T-Bill Auction Result: Cut-off</p><td>II. Cut-off Price (&#8377;) and '
    'Implicit Yield at Cut-Off Price</td><td>98.5422 (YTM: 5.9337%)</td>'
    '<td>96.8376 (YTM: 6.5493%)</td></body></html>'
)


def test_parses_the_91_day_yield(tmp_path: Path) -> None:
    (tmp_path / '1.html').write_text(PAGE)
    (tmp_path / '2.html').write_text('<html>nothing</html>')
    table = RbiTbillParser().parse_folder(tmp_path)
    assert len(table) == 1
    assert table['yield_91d'].iloc[0] == 5.9337
    assert str(table['date'].iloc[0].date()) == '2026-10-28'
