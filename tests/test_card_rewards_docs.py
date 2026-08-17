from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.validate_card_rewards_docs import (
    EXPECTED_CARD_FILES,
    EXPECTED_PAYMENT_FILES,
    parse_frontmatter,
    validate_corpus,
    validate_document,
)


ROOT = Path(__file__).parents[1]
UTF8_SUBPROCESS_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


class CardRewardsDocsTests(unittest.TestCase):
    def _write_document(
        self,
        root: Path,
        body: str,
        *,
        coverage: str = "complete",
        customer_scope: str = "existing",
    ) -> Path:
        path = root / "cards" / "first-ileo.md"
        path.parent.mkdir(parents=True)
        path.write_text(
            "---\n"
            "product: Test Card\nissuer: Test Bank\nproduct_type: credit\n"
            f"customer_scope: {customer_scope}\ntarget_from: 2026-08-01\n"
            "target_to: 2026-12-31\nverified_at: 2026-08-17\n"
            f"coverage_status: {coverage}\n---\n{body}",
            encoding="utf-8",
        )
        return path

    @staticmethod
    def _valid_body(*, conclusion: str = "摘要", uncertainty: str = "待人工確認活動有效期間。") -> str:
        return f"""## 結論摘要
{conclusion}
## 一般回饋
無
## 特殊回饋
無
## 行動支付相容性
無
## 排除交易
無
## 來源證據
官方規則：https://firstbank.com.tw/card
## 不確定事項
{uncertainty}
"""

    def _write_complete_corpus(self, root: Path) -> None:
        expected = sorted(EXPECTED_CARD_FILES | EXPECTED_PAYMENT_FILES)
        for index, relative in enumerate(expected, start=1):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            product_type = "payment" if relative.startswith("payments/") else "credit"
            path.write_text(
                "---\n"
                f"product: Fixture Product {index}\n"
                "issuer: Fixture Issuer\n"
                f"product_type: {product_type}\n"
                "customer_scope: existing\n"
                "target_from: 2026-08-01\n"
                "target_to: 2026-12-31\n"
                "verified_at: 2026-08-17\n"
                "coverage_status: complete\n"
                "---\n"
                + self._valid_body(),
                encoding="utf-8",
            )

    @staticmethod
    def _comparison_row(
        product_id: str,
        *,
        footnote_id: str | None = None,
        column_count: int = 10,
    ) -> str:
        footnote_id = footnote_id or product_id
        cells = [
            f"Fixture {product_id}[^{footnote_id}] "
            f"<!-- product-id: {product_id} -->"
        ] + ["fixture"] * 9
        return "| " + " | ".join(cells[:column_count]) + " |"

    def _valid_comparison(
        self,
        *,
        rows: list[str] | None = None,
        footnote_targets: dict[str, str] | None = None,
        detached: list[str] | None = None,
    ) -> str:
        product_ids = [Path(relative).stem for relative in sorted(EXPECTED_CARD_FILES)]
        rows = rows or [self._comparison_row(product_id) for product_id in product_ids]
        footnote_targets = footnote_targets or {
            product_id: f"cards/{product_id}.md" for product_id in product_ids
        }
        detached_text = "".join(
            f"<!-- product-id: {product_id} -->\n" for product_id in (detached or [])
        )
        definitions = "".join(
            f"[^{footnote_id}]: [Fixture evidence]({target})\n"
            for footnote_id, target in footnote_targets.items()
        )
        return (
            "# 比較表\n\n"
            + detached_text
            + "## 15 項產品總表\n\n"
            + "| 產品 | 國內一般 | 國外一般 | 最佳特殊回饋 | 條件 | "
            "上限／推導可刷額 | LINE Pay | iPASS MONEY | 全支付 | 覆蓋狀態 |\n"
            + "|---|---|---|---|---|---|---|---|---|---|\n"
            + "\n".join(rows)
            + "\n\n"
            + definitions
        )

    def _issues_for_first_ileo(self, root: Path) -> set[str]:
        return {
            issue.code
            for issue in validate_corpus(root)
            if issue.path == "cards/first-ileo.md"
        }

    def test_parse_frontmatter_returns_metadata_and_body(self) -> None:
        metadata, body = parse_frontmatter(
            "---\nproduct: Test Card\ncustomer_scope: existing\n---\n# Test Card\n"
        )
        self.assertEqual(metadata["product"], "Test Card")
        self.assertEqual(metadata["customer_scope"], "existing")
        self.assertIn("# Test Card", body)

    def test_empty_corpus_reports_every_expected_product(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            issues = validate_corpus(Path(tmp))
        missing = {issue.path for issue in issues if issue.code == "missing_file"}
        self.assertTrue(EXPECTED_CARD_FILES <= missing)
        self.assertTrue(EXPECTED_PAYMENT_FILES <= missing)

    def test_cli_writes_json_and_fails_for_incomplete_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "corpus"
            report = Path(tmp) / "report.json"
            root.mkdir()
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_card_rewards_docs.py"),
                    "--root",
                    str(root),
                    "--json-report",
                    str(report),
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=UTF8_SUBPROCESS_ENV,
            )
            self.assertEqual(result.returncode, 1)
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual({"root", "issue_count", "issues"}, set(payload))
            self.assertGreater(payload["issue_count"], 0)
            self.assertEqual({"code", "path", "message"}, set(payload["issues"][0]))

    def test_unavailable_requires_query_scope_and_concrete_uncertainty(self) -> None:
        body = """## 結論摘要
摘要
## 一般回饋
無
## 特殊回饋
無
## 行動支付相容性
無
## 排除交易
無
## 來源證據
查無官方資料。
## 不確定事項
無
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_document(root, body, coverage="unavailable")
            self.assertIn("missing_official_url", self._issues_for_first_ileo(root))

    def test_unavailable_without_url_passes_with_query_scope_and_uncertainty(self) -> None:
        body = """## 結論摘要
摘要
## 一般回饋
無
## 特殊回饋
無
## 行動支付相容性
無
## 排除交易
無
## 來源證據
查詢範圍：2026-08-17 檢索發卡銀行官方產品頁、公告與權益 PDF。
## 不確定事項
截至查證日，官方尚未公告涵蓋研究期間的可用回饋方案。
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_document(root, body, coverage="unavailable")
            self.assertNotIn("missing_official_url", self._issues_for_first_ileo(root))

    def test_official_url_outside_source_evidence_does_not_count(self) -> None:
        body = """## 結論摘要
官方頁面：https://firstbank.com.tw/card
## 一般回饋
無
## 特殊回饋
無
## 行動支付相容性
無
## 排除交易
無
## 來源證據
查詢範圍：2026-08-17 檢索官方資料。
## 不確定事項
待人工確認活動有效期間。
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_document(root, body)
            self.assertIn("missing_official_url", self._issues_for_first_ileo(root))

    def test_validate_document_accepts_absolute_path_and_corpus_root(self) -> None:
        body = """## 結論摘要
摘要
## 一般回饋
無
## 特殊回饋
無
## 行動支付相容性
無
## 排除交易
無
## 來源證據
官方規則：https://firstbank.com.tw/card
## 不確定事項
待人工確認活動有效期間。
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_document(root, body)
            issues = validate_document(path.resolve(), root.resolve())
            self.assertEqual([], issues)

    def test_existing_customer_scope_is_mandatory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_document(
                root,
                self._valid_body(),
                customer_scope="new",
            )
            codes = {issue.code for issue in validate_document(path, root)}
        self.assertIn("wrong_scope", codes)

    def test_partial_requires_exact_uncovered_period_statement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_document(root, self._valid_body(), coverage="partial")
            codes = {issue.code for issue in validate_document(path, root)}
        self.assertIn("partial_without_gap", codes)

    def test_partial_accepts_exact_uncovered_period_statement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_document(
                root,
                self._valid_body(
                    uncertainty="未覆蓋期間：2026-09-01 至 2026-12-31；官方尚未公告。"
                ),
                coverage="partial",
            )
            codes = {issue.code for issue in validate_document(path, root)}
        self.assertNotIn("partial_without_gap", codes)

    def test_unavailable_rejects_numeric_recommendation_in_conclusion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_document(
                root,
                self._valid_body(conclusion="建議使用本卡取得 5% 回饋。"),
                coverage="unavailable",
            )
            codes = {issue.code for issue in validate_document(path, root)}
        self.assertIn("unavailable_numeric_claim", codes)

    def test_unavailable_allows_percentage_only_outside_conclusion(self) -> None:
        body = self._valid_body(conclusion="目前無法提出定量建議。").replace(
            "官方規則：https://firstbank.com.tw/card",
            "官方規則：https://firstbank.com.tw/card\n查詢頁曾出現 5%，但不作推薦。",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_document(root, body, coverage="unavailable")
            codes = {issue.code for issue in validate_document(path, root)}
        self.assertNotIn("unavailable_numeric_claim", codes)

    def test_comparison_requires_every_product_identifier(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_complete_corpus(root)
            (root / "comparison.md").write_text("# 比較表\n", encoding="utf-8")
            issues = validate_corpus(root)
        self.assertEqual(
            15,
            sum(issue.code == "comparison_missing_product" for issue in issues),
        )

    def test_comparison_rejects_duplicate_product_row(self) -> None:
        product_ids = [Path(relative).stem for relative in sorted(EXPECTED_CARD_FILES)]
        rows = [self._comparison_row(product_id) for product_id in product_ids]
        rows.append(self._comparison_row("first-ileo"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_complete_corpus(root)
            (root / "comparison.md").write_text(
                self._valid_comparison(rows=rows), encoding="utf-8"
            )
            issues = validate_corpus(root)
        codes = {issue.code for issue in issues}
        self.assertIn("comparison_duplicate_product", codes)
        self.assertIn("comparison_row_count", codes)

    def test_comparison_rejects_detached_identifier_when_row_is_deleted(self) -> None:
        product_ids = [Path(relative).stem for relative in sorted(EXPECTED_CARD_FILES)]
        rows = [
            self._comparison_row(product_id)
            for product_id in product_ids
            if product_id != "first-ileo"
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_complete_corpus(root)
            (root / "comparison.md").write_text(
                self._valid_comparison(rows=rows, detached=["first-ileo"]),
                encoding="utf-8",
            )
            issues = validate_corpus(root)
        codes = {issue.code for issue in issues}
        self.assertIn("comparison_missing_product", codes)
        self.assertIn("comparison_detached_product", codes)
        self.assertIn("comparison_row_count", codes)

    def test_comparison_rejects_swapped_product_identifiers(self) -> None:
        product_ids = [Path(relative).stem for relative in sorted(EXPECTED_CARD_FILES)]
        rows = []
        for product_id in product_ids:
            row_id = {
                "first-green": "first-ileo",
                "first-ileo": "first-green",
            }.get(product_id, product_id)
            rows.append(self._comparison_row(row_id, footnote_id=product_id))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_complete_corpus(root)
            (root / "comparison.md").write_text(
                self._valid_comparison(rows=rows), encoding="utf-8"
            )
            codes = {issue.code for issue in validate_corpus(root)}
        self.assertIn("comparison_footnote_mismatch", codes)

    def test_comparison_rejects_extra_unknown_product_row(self) -> None:
        product_ids = [Path(relative).stem for relative in sorted(EXPECTED_CARD_FILES)]
        rows = [self._comparison_row(product_id) for product_id in product_ids]
        rows.append(self._comparison_row("not-a-card"))
        targets = {
            product_id: f"cards/{product_id}.md" for product_id in product_ids
        }
        targets["not-a-card"] = "cards/not-a-card.md"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_complete_corpus(root)
            (root / "comparison.md").write_text(
                self._valid_comparison(rows=rows, footnote_targets=targets),
                encoding="utf-8",
            )
            codes = {issue.code for issue in validate_corpus(root)}
        self.assertIn("comparison_unknown_product", codes)
        self.assertIn("comparison_row_count", codes)

    def test_comparison_rejects_wrong_column_count(self) -> None:
        product_ids = [Path(relative).stem for relative in sorted(EXPECTED_CARD_FILES)]
        rows = [
            self._comparison_row(
                product_id,
                column_count=9 if product_id == "first-ileo" else 10,
            )
            for product_id in product_ids
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_complete_corpus(root)
            (root / "comparison.md").write_text(
                self._valid_comparison(rows=rows), encoding="utf-8"
            )
            codes = {issue.code for issue in validate_corpus(root)}
        self.assertIn("comparison_column_count", codes)

    def test_comparison_rejects_footnote_target_mismatch(self) -> None:
        targets = {
            Path(relative).stem: f"cards/{Path(relative).stem}.md"
            for relative in sorted(EXPECTED_CARD_FILES)
        }
        targets["first-ileo"] = "cards/first-green.md"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_complete_corpus(root)
            (root / "comparison.md").write_text(
                self._valid_comparison(footnote_targets=targets),
                encoding="utf-8",
            )
            codes = {issue.code for issue in validate_corpus(root)}
        self.assertIn("comparison_footnote_mismatch", codes)

    def test_comparison_requires_one_identifier_in_each_row(self) -> None:
        product_ids = [Path(relative).stem for relative in sorted(EXPECTED_CARD_FILES)]
        rows = [self._comparison_row(product_id) for product_id in product_ids]
        first_ileo_index = product_ids.index("first-ileo")
        rows[first_ileo_index] = rows[first_ileo_index].replace(
            "<!-- product-id: first-ileo -->", ""
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_complete_corpus(root)
            (root / "comparison.md").write_text(
                self._valid_comparison(rows=rows), encoding="utf-8"
            )
            codes = {issue.code for issue in validate_corpus(root)}
        self.assertIn("comparison_row_product_id", codes)

    def test_payment_matrix_requires_exactly_fifteen_product_rows(self) -> None:
        rows = "\n".join(
            f"| Product {index} | supported | path | reward | bonus | stacking | source |"
            for index in range(1, 15)
        )
        body = self._valid_body().replace(
            "## 行動支付相容性\n無",
            "## 行動支付相容性\n\n"
            "| 使用者產品 | 可綁／可連結 | 支付方式 | 原卡／帳戶回饋 | "
            "支付服務加碼 | 可否疊加 | 官方證據 |\n"
            "|---|---|---|---|---|---|---|\n"
            + rows,
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "payments" / "line-pay.md"
            path.parent.mkdir(parents=True)
            path.write_text(
                "---\n"
                "product: LINE Pay\nissuer: LINE Pay\nproduct_type: payment\n"
                "customer_scope: existing\ntarget_from: 2026-08-01\n"
                "target_to: 2026-12-31\nverified_at: 2026-08-18\n"
                "coverage_status: complete\n---\n"
                + body,
                encoding="utf-8",
            )
            codes = {issue.code for issue in validate_document(path, root)}
        self.assertIn("payment_matrix_row_count", codes)

    def test_validate_document_rejects_path_outside_corpus_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "corpus"
            root.mkdir()
            outside = base / "first-ileo.md"
            outside.write_text("not corpus data\n", encoding="utf-8")
            issues = validate_document(outside, root)
        self.assertEqual("unreadable", issues[0].code)

    def test_validate_document_rejects_unknown_path_inside_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            unknown = root / "cards" / "unknown.md"
            unknown.parent.mkdir()
            unknown.write_text("not corpus data\n", encoding="utf-8")
            issues = validate_document(unknown, root)
        self.assertEqual("unreadable", issues[0].code)

    def test_validate_document_reports_missing_expected_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            issues = validate_document(Path("cards/first-ileo.md"), root)
        self.assertEqual("missing_file", issues[0].code)

    def test_official_subdomain_url_is_accepted(self) -> None:
        body = self._valid_body().replace(
            "https://firstbank.com.tw/card",
            "https://card.firstbank.com.tw/sites/card/zh_TW/example",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_document(root, body)
            codes = self._issues_for_first_ileo(root)
        self.assertNotIn("missing_official_url", codes)

    def test_validate_corpus_only_reports_selected_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            issues = validate_corpus(Path(tmp), {"cards/first-ileo.md"})
        self.assertEqual(
            [("missing_file", "cards/first-ileo.md")],
            [(issue.code, issue.path) for issue in issues],
        )

    def test_cli_only_existing_task_two_documents_passes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate_card_rewards_docs.py"),
                "--root",
                "docs/card-rewards/2026-h2",
                "--only",
                " cards/first-ileo.md, cards/first-green.md ,cards/taishin-richart-gogo.md ",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=UTF8_SUBPROCESS_ENV,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_cli_rejects_unknown_only_path(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate_card_rewards_docs.py"),
                "--root",
                str(ROOT / "docs" / "card-rewards" / "2026-h2"),
                "--only",
                "cards/not-a-product.md",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=UTF8_SUBPROCESS_ENV,
        )
        self.assertEqual(2, result.returncode)

    def test_cli_accepts_backslash_only_path(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate_card_rewards_docs.py"),
                "--root",
                str(ROOT / "docs" / "card-rewards" / "2026-h2"),
                "--only",
                r"cards\first-ileo.md",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=UTF8_SUBPROCESS_ENV,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_cli_rejects_empty_only_item(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate_card_rewards_docs.py"),
                "--root",
                str(ROOT / "docs" / "card-rewards" / "2026-h2"),
                "--only",
                "cards/first-ileo.md,",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=UTF8_SUBPROCESS_ENV,
        )
        self.assertEqual(2, result.returncode)

    def test_cli_rejects_only_path_that_escapes_root(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate_card_rewards_docs.py"),
                "--root",
                str(ROOT / "docs" / "card-rewards" / "2026-h2"),
                "--only",
                "cards/../cards/first-ileo.md",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=UTF8_SUBPROCESS_ENV,
        )
        self.assertEqual(2, result.returncode)

    def test_cli_rejects_unreadable_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_card_rewards_docs.py"),
                    "--root",
                    str(missing_root),
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=UTF8_SUBPROCESS_ENV,
            )
        self.assertEqual(2, result.returncode)

    def test_cli_rejects_root_that_is_not_a_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root_file = Path(tmp) / "corpus.md"
            root_file.write_text("not a directory\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "validate_card_rewards_docs.py"),
                    "--root",
                    str(root_file),
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=UTF8_SUBPROCESS_ENV,
            )
        self.assertEqual(2, result.returncode)
