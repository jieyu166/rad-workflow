from __future__ import annotations

import json
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
)


ROOT = Path(__file__).parents[1]


class CardRewardsDocsTests(unittest.TestCase):
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
            )
            self.assertEqual(result.returncode, 1)
            self.assertGreater(json.loads(report.read_text(encoding="utf-8"))["issue_count"], 0)

