from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.build_card_rewards_tool import BuildError, build_dataset, serialize_dataset


ROOT = Path(__file__).parents[1]


class CardRewardsDatasetTests(unittest.TestCase):
    def test_dataset_contains_exact_approved_products_and_payments(self) -> None:
        dataset = build_dataset(ROOT)
        cards = dataset["cards"]
        payments = dataset["payments"]

        self.assertEqual("1", dataset["schemaVersion"])
        self.assertEqual("2026-08-18", dataset["auditDate"])
        self.assertEqual("2026-08-01", dataset["targetFrom"])
        self.assertEqual("2026-12-31", dataset["targetTo"])
        self.assertEqual({"complete": 9, "partial": 9, "unavailable": 0}, dataset["coverageCounts"])
        self.assertEqual(15, len(cards))
        self.assertEqual(15, len({card["id"] for card in cards}))
        self.assertEqual(["line-pay", "ipass-money", "px-pay"], [item["id"] for item in payments])
        self.assertTrue(all(len(item["rows"]) == 15 for item in payments))

    def test_card_record_preserves_comparison_sections_sources_and_badges(self) -> None:
        dataset = build_dataset(ROOT)
        cards = {card["id"]: card for card in dataset["cards"]}
        cube = cards["cathay-cube"]

        self.assertEqual("國泰世華 CUBE 卡", cube["product"])
        self.assertEqual("partial", cube["coverageStatus"])
        self.assertIn("8/3", cube["comparison"]["domestic"])
        self.assertIn("2.5%", cube["comparison"]["overseas"])
        self.assertIn("partial", cube["badges"])
        self.assertIn("overseas", cube["facetIds"])
        self.assertIn("CUBE", cube["searchAliases"])
        self.assertTrue(cube["sections"]["uncertainties"]["blocks"])
        self.assertTrue(all(source["url"].startswith("https://") for source in cube["sources"]))

    def test_payment_names_map_back_to_stable_product_ids(self) -> None:
        dataset = build_dataset(ROOT)
        line_pay = next(item for item in dataset["payments"] if item["id"] == "line-pay")
        rows = {row["productId"]: row for row in line_pay["rows"]}

        self.assertEqual("supported", rows["sinopac-daway"]["supported"])
        self.assertIn("26.5%", rows["sinopac-daway"]["stacking"])
        self.assertEqual("not officially confirmed", rows["esun-pi"]["supported"])

    def test_serialized_dataset_is_deterministic_and_utf8_readable(self) -> None:
        first = serialize_dataset(build_dataset(ROOT))
        second = serialize_dataset(build_dataset(ROOT))

        self.assertEqual(first, second)
        self.assertIn("國泰世華 CUBE 卡", first)
        self.assertNotIn(str(ROOT), first)
        self.assertNotIn("generatedAt", first)
        self.assertEqual(json.loads(first), json.loads(second))

    def test_malformed_card_section_table_preserves_short_row_as_fallback(self) -> None:
        dataset = build_dataset(ROOT)
        cards = {card["id"]: card for card in dataset["cards"]}
        blocks = cards["ctbc-line-pay"]["sections"]["specialRewards"]["blocks"]
        fallback = next(block for block in blocks if block["type"] == "table-fallback")
        short_row = next(row for row in fallback["rows"] if len(row["cells"]) == 6)

        self.assertTrue(fallback["sourceRowWidthMismatch"])
        self.assertEqual(
            [
                "2026-01-01 至 2026-12-31",
                "Hotels.com 臺灣網站指定「LINE Pay卡」網頁，代碼 `CTBCLP16`",
                "16% LINE POINTS",
                "已含一般 1%；不與 Hotels.com Rewards™ 併用 [來源 6]",
                "線上以 LINE Pay 卡付款、新臺幣，1-28 晚；2026 年預訂、2027-06-30 前完成入住，僅線上付款飯店，Pay at hotel 不適用；每筆 1,800 點 [來源 6]",
                "詳細頁稱每月首 450 次預訂；但官方總表稱每月 400 組，兩頁衝突，不選一方為完整名額 [來源 3][來源 6]",
            ],
            short_row["cells"],
        )

    def test_unknown_payment_product_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "repo"
            shutil.copytree(ROOT / "docs", fixture / "docs")
            payment = fixture / "docs/card-rewards/2026-h2/payments/line-pay.md"
            text = payment.read_text(encoding="utf-8").replace(
                "| 第一銀行 iLEO 卡 |", "| 不存在的產品 |", 1
            )
            payment.write_text(text, encoding="utf-8")

            with self.assertRaisesRegex(BuildError, "payment product.*不存在的產品"):
                build_dataset(fixture)

    def test_missing_required_card_section_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "repo"
            shutil.copytree(ROOT / "docs", fixture / "docs")
            card = fixture / "docs/card-rewards/2026-h2/cards/first-ileo.md"
            text = card.read_text(encoding="utf-8").replace("## 排除交易", "## 其他事項", 1)
            card.write_text(text, encoding="utf-8")

            with self.assertRaisesRegex(BuildError, "排除交易"):
                build_dataset(fixture)
