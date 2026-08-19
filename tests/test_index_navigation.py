from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).parents[1]


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href is not None:
            self.links.append((self._href, "".join(self._text).strip()))
            self._href = None
            self._text = []


class IndexNavigationTests(unittest.TestCase):
    def test_index_links_to_image_stack_mpr_viewer(self) -> None:
        parser = LinkParser()
        parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))

        self.assertIn(
            ("tool/image-stack-mpr.html", "影像序列 Crosslink 與 MPR"),
            parser.links,
        )
        self.assertTrue((ROOT / "tool" / "image-stack-mpr.html").is_file())

    def test_index_links_to_local_card_rewards_tool(self) -> None:
        parser = LinkParser()
        parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))

        self.assertIn(
            ("tool/card-rewards.html", "2026 下半年舊戶卡片回饋查詢"), parser.links
        )
        self.assertNotIn(
            "https://claude.ai/public/artifacts/aa39410d-a1c4-4e5d-8259-df094c2238b8",
            (ROOT / "index.html").read_text(encoding="utf-8"),
        )
        self.assertSetEqual(
            {
                "https://claude.ai/public/artifacts/08ec2586-8eb9-4342-9058-5b47ba606e82",
                "https://claude.ai/public/artifacts/f1880892-1b49-4e64-8af3-938a22f80738",
                "https://claude.ai/public/artifacts/621529ec-0b8c-4573-8b0e-12999b5cae30",
                "https://claude.ai/public/artifacts/9ccf7b5e-9fa6-4e33-ba86-ee3b385de6c2",
            },
            {
                href
                for href, _ in parser.links
                if href.startswith("https://claude.ai/public/artifacts/")
            },
        )
        self.assertTrue((ROOT / "tool/card-rewards.html").is_file())

    def test_readme_links_to_local_card_rewards_snapshot(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(
            "[2026 下半年舊戶卡片回饋查詢](tool/card-rewards.html)", readme
        )
        card_rewards_row = next(
            line
            for line in readme.splitlines()
            if "[2026 下半年舊戶卡片回饋查詢](tool/card-rewards.html)" in line
        )
        for required_text in (
            "既有持卡人／既有帳戶",
            "2026-08-01 至 12-31",
            "查證基準日 2026-08-18",
            "離線回饋快照",
            "非即時銀行資料",
        ):
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, card_rewards_row)


if __name__ == "__main__":
    unittest.main()
