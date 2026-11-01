"""Turns the hand-off strategy brief from Markdown into one HTML page."""

import html
import math
import re
from pathlib import Path

import pandas as pd


class BriefPage:
    """Builds strategy_brief.html from strategy_brief.md and the results.

    The page keeps its styles inside it, loads nothing from other sites and
    carries an inline SVG chart of the growth of one rupee in the portfolio
    and in its benchmark, so it cannot disagree with the Markdown.

    Attributes:
        results: The results folder, for the chart's monthly returns.
    """

    STYLE = """
body{font-family:'Times New Roman',Tinos,'Liberation Serif',serif;max-width:800px;margin:32px auto;padding:0 16px;color:#202124;line-height:1.55;font-size:17px}
h1{font-size:28px;text-align:center}h2{font-size:21px;margin-top:34px;border-bottom:1px solid #dadce0;padding-bottom:4px}
table{border-collapse:collapse;width:100%;font-size:15px;border-top:2px solid #202124;border-bottom:2px solid #202124;margin:14px 0}
th{border-bottom:1px solid #202124;font-weight:normal;font-style:italic;padding:5px 7px;text-align:right}th:first-child,td:first-child{text-align:left}
td{padding:3px 7px;text-align:right;font-variant-numeric:tabular-nums}code{font-family:'JetBrains Mono',monospace;font-size:14px}
li{margin:4px 0}.chart{margin:18px 0}.colour-bar{height:4px;display:flex;width:160px;margin:0 auto 24px}.colour-bar span{flex:1}
@media (max-width:600px){body{font-size:16px}table{display:block;overflow-x:auto}}
"""

    def __init__(self, results: Path) -> None:
        """Keeps the results folder.

        Args:
            results (Path): The folder with tradeable_monthly.csv and
                benchmarks_monthly.csv.

        Returns:
            None.
        """
        self.results = Path(results)

    def inline(self, text: str) -> str:
        """Formats bold, italic and code spans and links in one line.

        Args:
            text (str): A line of Markdown.

        Returns:
            str: HTML.
        """
        text = html.escape(text, quote=False)
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)
        return re.sub(
            r'(https?://[^\s)<,;]+[^\s)<,;.])', r'<a href="\1">\1</a>', text
        )

    def convert(self, markdown: str) -> str:
        """Converts headings, paragraphs, bullets, numbered lists and tables.

        Args:
            markdown (str): The brief in Markdown.

        Returns:
            str: The page's body HTML.
        """
        lines = markdown.splitlines()
        out = []
        index = 0
        while index < len(lines):
            line = lines[index]
            if line.startswith('# '):
                out.append(f'<h1>{self.inline(line[2:])}</h1>')
            elif line.startswith('## '):
                out.append(f'<h2>{self.inline(line[3:])}</h2>')
            elif line.startswith('|'):
                block = []
                while index < len(lines) and lines[index].startswith('|'):
                    block.append(lines[index])
                    index += 1
                out.append(self.table(block))
                continue
            elif re.match(r'^(- |\d+\. )', line):
                ordered = bool(re.match(r'^\d+\. ', line))
                items = []
                while index < len(lines) and re.match(
                    r'^(- |\d+\. )', lines[index]
                ):
                    items.append(re.sub(r'^(- |\d+\. )', '', lines[index]))
                    index += 1
                tag = 'ol' if ordered else 'ul'
                body = ''.join(f'<li>{self.inline(i)}</li>' for i in items)
                out.append(f'<{tag}>{body}</{tag}>')
                continue
            elif line.strip():
                out.append(f'<p>{self.inline(line)}</p>')
            index += 1
        return '\n'.join(out)

    def table(self, block: list[str]) -> str:
        """Converts a Markdown table.

        Args:
            block (list[str]): The table's lines.

        Returns:
            str: HTML.
        """
        rows = [
            [cell.strip() for cell in row.strip('|').split('|')]
            for row in block
            if not re.match(r'^\|[\s:|-]+\|$', row)
        ]
        head = ''.join(f'<th>{self.inline(c)}</th>' for c in rows[0])
        body = ''.join(
            '<tr>'
            + ''.join(f'<td>{self.inline(c)}</td>' for c in row)
            + '</tr>'
            for row in rows[1:]
        )
        return f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'

    def growth_chart(self) -> str:
        """Draws the growth of one rupee, log scale, as an inline SVG.

        Returns:
            str: An svg element, or an empty string when the monthly files
                are missing.
        """
        tradeable = self.results / 'tradeable_monthly.csv'
        bench = self.results / 'benchmarks_monthly.csv'
        if not tradeable.exists() or not bench.exists():
            return ''
        own = pd.read_csv(tradeable, index_col=0)['L1_net'].sort_index()
        market = pd.read_csv(bench, index_col=0)['NIFTY 500 TRI'].sort_index()
        months = own.dropna().index.intersection(market.dropna().index)
        series = {
            'Low-beta fifth (L1), after costs': (1 + own[months]).cumprod(),
            'NIFTY 500 total return': (1 + market[months]).cumprod(),
        }
        colours = ['#4285f4', '#9aa0a6']
        width, height, left, bottom, top = 760, 300, 46, 26, 14
        low = min(s.min() for s in series.values())
        high = max(s.max() for s in series.values())
        lo, hi = math.log10(low * 0.9), math.log10(high * 1.1)
        x = lambda i: left + (width - left - 10) * i / (len(months) - 1)
        y = lambda v: (
            top
            + (height - top - bottom) * (1 - (math.log10(v) - lo) / (hi - lo))
        )
        parts = [
            f'<svg class="chart" viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="Growth of one rupee">'
        ]
        tick = math.ceil(lo)
        while tick <= hi:
            ypos = y(10**tick)
            parts.append(
                f'<line x1="{left}" x2="{width - 10}" y1="{ypos:.1f}" y2="{ypos:.1f}" stroke="#e8eaed"/>'
                f'<text x="{left - 6}" y="{ypos + 4:.1f}" font-size="12" text-anchor="end" fill="#5f6368">{10**tick:g}</text>'
            )
            tick += 1
        for number in range(0, len(months), 60):
            parts.append(
                f'<text x="{x(number):.1f}" y="{height - 8}" font-size="12" text-anchor="middle" fill="#5f6368">{months[number][:4]}</text>'
            )
        for (name, values), colour in zip(series.items(), colours):
            points = ' '.join(
                f'{x(i):.1f},{y(v):.1f}' for i, v in enumerate(values)
            )
            parts.append(
                f'<polyline fill="none" stroke="{colour}" stroke-width="1.8" points="{points}"/>'
            )
        parts.append(
            f'<text x="{left + 8}" y="{top + 12}" font-size="13" fill="#4285f4">Low-beta fifth (L1), after costs</text>'
            f'<text x="{left + 8}" y="{top + 28}" font-size="13" fill="#5f6368">NIFTY 500 total return</text>'
        )
        parts.append('</svg>')
        return ''.join(parts)

    def build(self, markdown: str) -> str:
        """Builds the whole page.

        Args:
            markdown (str): The brief in Markdown.

        Returns:
            str: A complete HTML document.
        """
        body = self.convert(markdown)
        chart = self.growth_chart()
        if chart:
            marker = '<h2>Risks and caveats</h2>'
            caption = (
                '<p><i>Growth of one rupee, log scale, April 1999 to October 2026, '
                'after costs for the portfolio; total returns for both.</i></p>'
            )
            body = body.replace(marker, chart + caption + marker, 1)
        title = html.escape(markdown.splitlines()[0].lstrip('# ').strip())
        bar = (
            '<div class="colour-bar"><span style="background:#4285f4"></span>'
            '<span style="background:#ea4335"></span><span style="background:#fbbc05">'
            '</span><span style="background:#34a853"></span></div>'
        )
        return (
            '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{title}</title><style>{self.STYLE}</style></head>'
            f'<body>{bar}{body}</body></html>\n'
        )
