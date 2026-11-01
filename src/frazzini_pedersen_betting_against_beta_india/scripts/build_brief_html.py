"""Command-line program that builds the hand-off brief's HTML page from its Markdown."""

import argparse
from pathlib import Path

from frazzini_pedersen_betting_against_beta_india.betting_against_beta.brief_page import (
    BriefPage,
)


class BuildBriefHtmlApplication:
    """Writes strategy_brief.html next to strategy_brief.md."""

    def run(self) -> None:
        """Writes the page.

        Returns:
            None.
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--references',
            default='handoff/bab-low-beta-india/skills/bab-low-beta-india/references',
        )
        parser.add_argument('--results', default='results')
        parser.add_argument(
            '--site',
            default=str(Path(__file__).resolve().parents[1] / 'site'),
            help='folder that also gets a copy as trading-agent-brief.html',
        )
        arguments = parser.parse_args()
        folder = Path(arguments.references)
        markdown = (folder / 'strategy_brief.md').read_text()
        page = BriefPage(Path(arguments.results)).build(markdown)
        (folder / 'strategy_brief.html').write_text(page)
        print(f'wrote {folder / "strategy_brief.html"} ({len(page)} bytes)')
        site = Path(arguments.site)
        if site.exists():
            (site / 'trading-agent-brief.html').write_text(page)
            print(f'wrote {site / "trading-agent-brief.html"}')


if __name__ == '__main__':
    BuildBriefHtmlApplication().run()
