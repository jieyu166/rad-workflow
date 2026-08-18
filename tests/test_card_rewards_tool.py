from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from contextlib import redirect_stderr
from unittest import mock

from scripts.build_card_rewards_tool import (
    DATA_END,
    DATA_START,
    BuildError,
    build_output,
    build_dataset,
    main,
    parse_document,
    read_embedded_dataset,
    replace_embedded_dataset,
    serialize_dataset,
)


ROOT = Path(__file__).parents[1]
UTF8_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


class ToolPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: dict[str, dict[str, str]] = {}
        self.external_assets: list[str] = []
        self.core_source = ""
        self.runtime_source = ""
        self._script_id: str | None = None
        self._script_parts: list[str] = []
        self._is_runtime_script = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value or "" for name, value in attrs}
        if element_id := attributes.get("id"):
            self.elements[element_id] = attributes
        for name in ("src", "href"):
            value = attributes.get(name, "")
            if value and (value.startswith(("http://", "https://", "//")) or tag == "script" and name == "src"):
                self.external_assets.append(value)
        if tag == "script":
            self._script_id = attributes.get("id")
            self._script_parts = []
            self._is_runtime_script = (
                self._script_id != "card-rewards-core"
                and attributes.get("type") != "application/json"
            )

    def handle_data(self, data: str) -> None:
        if self._script_id == "card-rewards-core" or self._is_runtime_script:
            self._script_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._script_id == "card-rewards-core":
            self.core_source = "".join(self._script_parts)
        if tag == "script" and self._is_runtime_script:
            self.runtime_source = "".join(self._script_parts)
        if tag == "script":
            self._script_id = None
            self._script_parts = []
            self._is_runtime_script = False


def parse_tool_page() -> ToolPageParser:
    parser = ToolPageParser()
    parser.feed((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"))
    return parser


def run_core(expression: str, filter_fixtures: dict[str, dict[str, object]] | None = None) -> object:
    parser = parse_tool_page()
    dataset = json.loads(read_embedded_dataset((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")))
    payload = json.dumps(
        {
            "core": parser.core_source,
            "cards": dataset["cards"],
            "expression": expression,
            "filterFixtures": filter_fixtures or {},
        },
        ensure_ascii=False,
    )
    runner = r'''
const fs = require("fs");
const vm = require("vm");
const payload = JSON.parse(fs.readFileSync(0, "utf8"));
if (!payload.core) throw new Error("missing card-rewards-core script");
const asFilterState = (filters) => ({
  ...filters,
  facets: new Set(filters.facets || []),
  coverage: new Set(filters.coverage || []),
  productTypes: new Set(filters.productTypes || [])
});
const filterFixtures = Object.fromEntries(
  Object.entries(payload.filterFixtures).map(([name, filters]) => [name, asFilterState(filters)])
);
const context = vm.createContext({ CARDS: payload.cards, FILTER_FIXTURES: filterFixtures, Set, String, Object, Array, JSON });
vm.runInContext(payload.core, context, { filename: "card-rewards-core.js" });
process.stdout.write(JSON.stringify(vm.runInContext(payload.expression, context, { filename: "card-rewards-expression.js" })));
'''
    result = subprocess.run(
        ["node", "-e", runner],
        input=payload,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=UTF8_ENV,
        check=False,
    )
    if result.returncode:
        raise AssertionError(result.stderr.strip())
    return json.loads(result.stdout)


def run_runtime(dataset: dict[str, object]) -> dict[str, object]:
    parser = parse_tool_page()
    payload = json.dumps(
        {"core": parser.core_source, "runtime": parser.runtime_source, "dataset": dataset},
        ensure_ascii=False,
    )
    runner = r'''
const fs = require("fs");
const vm = require("vm");
const payload = JSON.parse(fs.readFileSync(0, "utf8"));
class FakeElement {
  constructor(id) {
    this.id = id;
    this.children = [];
    this.textContent = "";
    this.hidden = false;
    this.value = "";
    this.disabled = false;
    this.mutations = 0;
    this.classList = { values: new Set(), add: value => this.classList.values.add(value), contains: value => this.classList.values.has(value) };
  }
  append(...children) { this.children.push(...children); this.mutations += 1; }
  replaceChildren(...children) { this.children = children; this.mutations += 1; }
  setAttribute() {}
  addEventListener() {}
  focus() {}
}
const ids = ["app", "fatal-error", "search", "result-count", "clear-filters", "facet-controls", "coverage-controls", "type-controls", "card-grid", "empty-state", "empty-clear", "compare-tray", "card-rewards-data"];
const elements = Object.fromEntries(ids.map(id => [id, new FakeElement(id)]));
elements["fatal-error"].hidden = true;
elements["card-rewards-data"].textContent = JSON.stringify(payload.dataset);
const document = {
  getElementById: id => elements[id] || null,
  createElement: tag => new FakeElement(tag)
};
const context = vm.createContext({ document, Set, String, Object, Array, JSON });
vm.runInContext(payload.core, context, { filename: "card-rewards-core.js" });
vm.runInContext(payload.runtime, context, { filename: "card-rewards-runtime.js" });
const fatalText = elements["fatal-error"].children.map(child => child.textContent).join(" ");
process.stdout.write(JSON.stringify({
  fatalText,
  fatalHidden: elements["fatal-error"].hidden,
  controlsHidden: elements.app.classList.contains("is-fatal"),
  facetControlMutations: elements["facet-controls"].mutations
}));
'''
    result = subprocess.run(
        ["node", "-e", runner],
        input=payload,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=UTF8_ENV,
        check=False,
    )
    if result.returncode:
        raise AssertionError(result.stderr.strip())
    return json.loads(result.stdout)


class CardRewardsInterfaceTests(unittest.TestCase):
    def test_page_has_required_discovery_controls(self) -> None:
        parser = parse_tool_page()
        for element_id in (
            "app", "fatal-error", "search", "result-count", "clear-filters", "facet-controls",
            "coverage-controls", "type-controls", "card-grid", "empty-state", "compare-tray",
        ):
            self.assertIn(element_id, parser.elements)
        self.assertEqual("search", parser.elements["search"]["type"])

    def test_page_has_no_runtime_asset_or_network_dependency(self) -> None:
        parser = parse_tool_page()
        self.assertEqual([], parser.external_assets)
        source = (ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")
        self.assertNotRegex(source, r"\bfetch\s*\(")
        self.assertNotIn("XMLHttpRequest", source)

    def test_core_search_matches_bank_alias_merchant_and_payment(self) -> None:
        self.assertTrue(run_core("cardMatchesQuery(CARDS.find(c => c.id === 'taishin-richart-gogo'), '@gogo')"))
        self.assertTrue(run_core("cardMatchesQuery(CARDS.find(c => c.id === 'sinopac-daway'), '路易莎')"))
        self.assertTrue(run_core("cardMatchesQuery(CARDS.find(c => c.id === 'esun-unicard'), '全支付')"))
        self.assertFalse(run_core("cardMatchesQuery(CARDS.find(c => c.id === 'esun-pi'), 'Costco')"))

    def test_filter_groups_are_or_within_group_and_and_across_groups(self) -> None:
        expression = """
        filterCards(CARDS, {
          query: '',
          facets: new Set(['line-pay', 'ipass-money']),
          coverage: new Set(['complete']),
          productTypes: new Set()
        }).map(card => card.id)
        """
        result = run_core(expression)
        self.assertIn("esun-unicard", result)
        self.assertNotIn("esun-pi", result)

    def test_malformed_card_shape_shows_fatal_before_filter_controls_render(self) -> None:
        dataset = json.loads(read_embedded_dataset((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")))
        dataset["cards"][0].pop("facetIds")

        result = run_runtime(dataset)

        self.assertFalse(result["fatalHidden"])
        self.assertTrue(result["controlsHidden"])
        self.assertIn("資料無法載入", result["fatalText"])
        self.assertEqual(0, result["facetControlMutations"])

    def test_malformed_comparison_render_field_shows_fatal_before_render(self) -> None:
        dataset = json.loads(read_embedded_dataset((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")))
        dataset["cards"][0]["comparison"]["domestic"] = {"not": "renderable text"}

        result = run_runtime(dataset)

        self.assertFalse(result["fatalHidden"])
        self.assertTrue(result["controlsHidden"])
        self.assertIn("資料無法載入", result["fatalText"])
        self.assertEqual(0, result["facetControlMutations"])

    def test_non_string_badge_shows_fatal_before_render(self) -> None:
        dataset = json.loads(read_embedded_dataset((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")))
        dataset["cards"][0]["badges"][0] = {"not": "a badge label"}

        result = run_runtime(dataset)

        self.assertFalse(result["fatalHidden"])
        self.assertTrue(result["controlsHidden"])
        self.assertIn("資料無法載入", result["fatalText"])
        self.assertEqual(0, result["facetControlMutations"])


class CardRewardsDatasetTests(unittest.TestCase):
    def test_dataset_card_product_types_match_phase_one_frontmatter(self) -> None:
        cards = build_dataset(ROOT)["cards"]
        corpus_root = ROOT / "docs/card-rewards/2026-h2"
        expected = [
            parse_document(corpus_root / "cards" / f"{card['id']}.md", corpus_root=corpus_root)["metadata"]["product_type"]
            for card in cards
        ]

        self.assertEqual(expected, [card.get("productType") for card in cards])

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
                "有效期間",
                "場景／通路",
                "總回饋",
                "組成",
                "舊戶條件",
                "回饋上限／推導可刷額",
                "登錄／名額",
            ],
            fallback["headers"],
        )
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

    def test_non_ctbc_section_row_width_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "repo"
            shutil.copytree(ROOT / "docs", fixture / "docs")
            card = fixture / "docs/card-rewards/2026-h2/cards/first-ileo.md"
            lines = card.read_text(encoding="utf-8").splitlines()
            start = lines.index("## 特殊回饋")
            end = lines.index("## 行動支付相容性")
            data_rows_started = False
            for index in range(start + 1, end):
                cells = lines[index].strip()[1:-1].split("|") if lines[index].strip().startswith("|") else []
                if cells and all(cell.strip(" -:") == "" for cell in cells):
                    data_rows_started = True
                    continue
                if data_rows_started and len(cells) == 8:
                    lines[index] = "|" + "|".join(cells[:-1]) + "|"
                    break
            else:
                self.fail("fixture did not contain a special-reward data row")
            card.write_text("\n".join(lines) + "\n", encoding="utf-8")

            with self.assertRaisesRegex(BuildError, "cards/first-ileo.md: .*fixed row width"):
                build_dataset(fixture)

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


class CardRewardsBuildTests(unittest.TestCase):
    def test_replace_embedded_dataset_changes_only_marked_block(self) -> None:
        source = f"before\n{DATA_START}\nold\n{DATA_END}\nafter\n"
        updated = replace_embedded_dataset(source, '{"schemaVersion": "1"}\n')

        self.assertTrue(updated.startswith(f"before\n{DATA_START}\n"))
        self.assertTrue(updated.endswith(f"{DATA_END}\nafter\n"))
        self.assertEqual(serialize_dataset({"schemaVersion": "1"}), read_embedded_dataset(updated))

    def test_replace_rejects_missing_or_duplicate_markers(self) -> None:
        with self.assertRaisesRegex(BuildError, "exactly one data marker pair"):
            replace_embedded_dataset("<html></html>", "{}\n")
        duplicate = f"{DATA_START}x{DATA_END}{DATA_START}y{DATA_END}"
        with self.assertRaisesRegex(BuildError, "exactly one data marker pair"):
            replace_embedded_dataset(duplicate, "{}\n")

    def test_read_rejects_duplicate_data_scripts(self) -> None:
        source = (
            f"{DATA_START}\n"
            '<script id="card-rewards-data" type="application/json">\n{}\n</script>\n'
            '<script id="card-rewards-data" type="application/json">\n{}\n</script>\n'
            f"{DATA_END}"
        )

        with self.assertRaisesRegex(BuildError, "exactly one card-rewards-data JSON script"):
            read_embedded_dataset(source)

    def test_read_rejects_raw_script_closer_or_invalid_json_payload(self) -> None:
        raw_closer = (
            f"{DATA_START}\n"
            '<script id="card-rewards-data" type="application/json">\n'
            '{"value": "</script>"}\n</script>\n'
            f"{DATA_END}"
        )
        invalid_json = (
            f"{DATA_START}\n"
            '<script id="card-rewards-data" type="application/json">\nnot JSON\n</script>\n'
            f"{DATA_END}"
        )

        with self.assertRaisesRegex(BuildError, "raw closing script token"):
            read_embedded_dataset(raw_closer)
        with self.assertRaisesRegex(BuildError, "valid JSON"):
            read_embedded_dataset(invalid_json)

    def test_read_allows_json_with_a_non_closing_script_token(self) -> None:
        source = (
            f"{DATA_START}\n"
            '<script id="card-rewards-data" type="application/json">\n'
            '{"value": "<script>"}\n</script>\n'
            f"{DATA_END}"
        )

        self.assertEqual(serialize_dataset({"value": "<script>"}), read_embedded_dataset(source))

    def test_checked_in_html_matches_generated_dataset(self) -> None:
        expected = serialize_dataset(build_dataset(ROOT))
        actual = read_embedded_dataset((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"))
        self.assertEqual(expected, actual)

    def test_cli_check_detects_one_byte_of_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "card-rewards.html"
            output.write_text((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"), encoding="utf-8")
            output.write_text(output.read_text(encoding="utf-8").replace('"schemaVersion": "1"', '"schemaVersion": "9"', 1), encoding="utf-8")
            before_check = output.read_bytes()
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_card_rewards_tool.py"), "--check", "--output", str(output)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=UTF8_ENV,
                check=False,
            )
            after_check = output.read_bytes()

        self.assertEqual(1, result.returncode)
        self.assertIn("embedded dataset drift", result.stderr)
        self.assertEqual(before_check, after_check)

    def test_build_then_check_canonicalizes_script_safe_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "repo"
            shutil.copytree(ROOT / "docs", fixture / "docs")
            card = fixture / "docs/card-rewards/2026-h2/cards/first-ileo.md"
            card.write_text(
                card.read_text(encoding="utf-8").replace(
                    "## 不確定事項", "## 不確定事項\n\n</script>", 1
                ),
                encoding="utf-8",
            )
            output = Path(tmp) / "card-rewards.html"
            output.write_text((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"), encoding="utf-8")

            self.assertIn("</script>", serialize_dataset(build_dataset(fixture)))
            self.assertTrue(build_output(fixture, output, check=False))
            self.assertIn(r"<\/script>", output.read_text(encoding="utf-8"))
            self.assertTrue(build_output(fixture, output, check=True))

    def test_build_then_check_escapes_mixed_case_closing_script_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "repo"
            shutil.copytree(ROOT / "docs", fixture / "docs")
            card = fixture / "docs/card-rewards/2026-h2/cards/first-ileo.md"
            card.write_text(
                card.read_text(encoding="utf-8").replace(
                    "## 不確定事項", "## 不確定事項\n\n</ScRiPt>", 1
                ),
                encoding="utf-8",
            )
            output = Path(tmp) / "card-rewards.html"
            output.write_text((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"), encoding="utf-8")

            self.assertIn("</ScRiPt>", serialize_dataset(build_dataset(fixture)))
            self.assertTrue(build_output(fixture, output, check=False))
            embedded = output.read_text(encoding="utf-8")
            self.assertNotIn("</ScRiPt>", embedded)
            self.assertIn(r"<\/ScRiPt>", embedded)
            self.assertTrue(build_output(fixture, output, check=True))

    def test_build_output_wraps_replace_errors_as_build_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "card-rewards.html"
            output.write_text((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"), encoding="utf-8")

            with mock.patch.object(Path, "replace", side_effect=OSError("replace blocked")):
                with self.assertRaisesRegex(BuildError, "cannot write HTML output"):
                    build_output(ROOT, output, check=False)

            self.assertEqual([], list(Path(tmp).glob("*.tmp")))

    def test_main_reports_temporary_cleanup_errors_as_build_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "card-rewards.html"
            output.write_text((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"), encoding="utf-8")
            stderr = io.StringIO()

            with (
                mock.patch.object(Path, "exists", return_value=True),
                mock.patch.object(Path, "unlink", side_effect=OSError("cleanup blocked")),
                redirect_stderr(stderr),
            ):
                self.assertEqual(1, main(["--output", str(output)]))

        self.assertIn("card rewards build: cannot clean temporary HTML output", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())
