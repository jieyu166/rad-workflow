from __future__ import annotations

import copy
import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "lecture-to-notes" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lecture_content_rules import validate_segment_content
from rewrite_evidence import (
    build_evidence_packet,
    canonical_packet_bytes,
    contains_sensitive_data,
    validate_review_record,
)


class LectureContentRuleTests(unittest.TestCase):
    def valid_summary(self) -> str:
        sentence = (
            "講者先依病灶位置與邊界建立判讀方向，再比較訊號、增強、水腫、擴散及灌流表現，"
            "並把影像特徵與課堂提供的臨床背景逐項核對；遇到彼此重疊的表現時，應回到已呈現的證據，"
            "說明支持與不支持各診斷的線索，避免把一般知識直接當成本病例事實。"
        )
        return sentence * 3

    def valid_segment(self, **overrides):
        segment = {
            "title": "膠質母細胞瘤的影像判讀",
            "summary_zh": self.valid_summary(),
            "takeaways_zh": [
                "先由病灶位置與邊界建立判讀方向",
                "整合增強水腫擴散與灌流表現",
                "鑑別時逐項核對課堂已提供證據",
                "病例結論不可超出講者陳述範圍",
            ],
            "editorial_notes_zh": ["編輯補充：新版分類資訊僅供延伸閱讀，不代表本病例診斷。"],
        }
        segment.update(overrides)
        return segment

    def packet(self):
        return build_evidence_packet(
            "lecture-01",
            2,
            10.0,
            20.0,
            "第一段講者內容。\n\n第二段講者內容。",
            [{"time": 12.0, "ocr": "影像文字", "path": "frames/f012.jpg"}],
            self.valid_segment(),
        )

    def valid_review(self, packet):
        return {
            "packet_sha256": packet["packet_sha256"],
            "reviewer": "A80748",
            "source_faithful": True,
            "case_details_verified": True,
            "editorial_separated": True,
        }

    def test_valid_focused_traditional_chinese_segment_has_no_errors(self):
        findings = validate_segment_content(self.valid_segment(), "講者原始逐字稿")
        self.assertEqual([finding for finding in findings if finding.severity == "error"], [])

    def test_rejects_generic_empty_multiline_and_overlong_titles(self):
        titles = ("", "Focused", "Overview", "Summary", "Chapter 3", "重點", "介紹", "病例", "第一章", "診斷\n補充", "腦" * 121)
        for title in titles:
            with self.subTest(title=title[:20]):
                codes = {item.code for item in validate_segment_content(self.valid_segment(title=title), "")}
                self.assertIn("title_focus", codes)

    def test_summary_requires_string_250_to_600_han_and_one_or_two_paragraphs(self):
        cases = (
            (None, {"summary_type"}),
            ("短摘要", {"summary_length"}),
            ("甲" * 601, {"summary_length"}),
            (("甲" * 100) + "\n\n" + ("乙" * 100) + "\n\n" + ("丙" * 100), {"summary_paragraphs"}),
        )
        for summary, expected in cases:
            with self.subTest(summary_type=type(summary).__name__):
                codes = {item.code for item in validate_segment_content(self.valid_segment(summary_zh=summary), "")}
                self.assertTrue(expected.issubset(codes))

    def test_unicode_whitespace_only_lines_count_as_paragraph_boundaries(self):
        summary = ("甲" * 100) + "\n　\n" + ("乙" * 100) + "\r\n \r\n" + ("丙" * 100)
        codes = {item.code for item in validate_segment_content(self.valid_segment(summary_zh=summary), "")}
        self.assertIn("summary_paragraphs", codes)

    def test_takeaways_must_be_exactly_four_nonempty_distinct_concise_strings(self):
        cases = (
            (["甲", "乙", "丙"], "takeaway_count"),
            (["甲", "乙", "丙", ""], "takeaway_empty"),
            (["甲", "乙", "丙", True], "takeaway_type"),
            (["相同重點", "相 同，重 點", "丙", "丁"], "takeaway_duplicate"),
            (["甲" * 81, "乙", "丙", "丁"], "takeaway_length"),
        )
        for takeaways, expected in cases:
            with self.subTest(expected=expected):
                codes = {item.code for item in validate_segment_content(self.valid_segment(takeaways_zh=takeaways), "")}
                self.assertIn(expected, codes)

    def test_editorial_notes_must_be_a_list_of_nonempty_strings(self):
        cases = ("補充", [""], [True])
        for editorial in cases:
            with self.subTest(editorial=editorial):
                codes = {item.code for item in validate_segment_content(self.valid_segment(editorial_notes_zh=editorial), "")}
                self.assertIn("editorial_type", codes)

    def test_rejects_unfinished_and_template_markers_even_with_separators(self):
        markers = ("TODO", "T B D", "FIXME", "PLACEHOLDER", "請補充", "待確認", "待​確認", "請⁠補充", "此處填入", "內容待補", "尚未完成")
        for marker in markers:
            with self.subTest(marker=marker):
                segment = self.valid_segment(editorial_notes_zh=[marker])
                codes = {item.code for item in validate_segment_content(segment, "")}
                self.assertIn("unfinished_marker", codes)

    def test_opencc_gate_rejects_simplified_text_and_preserves_taiwan_terms(self):
        simplified_controls = (
            "脑肿瘤影像显示强化与水肿，医生需要结合扩散、灌注与临床资料进行鉴别。" * 9,
            "该患者检查显示脑部肿块并伴随明显水肿，需要结合临床资料判断。" * 10,
        )
        for summary in simplified_controls:
            with self.subTest(summary=summary[:12]):
                segment = self.valid_segment(summary_zh=summary)
                self.assertIn("simplified_chinese", {item.code for item in validate_segment_content(segment, "")})

        traditional_controls = (
            "臺灣常用的神經放射學術語與影像判讀內容，著重病灶位置與鑑別。" * 12,
            "金屬干擾偽影會影響影像品質，判讀時需整合不同序列與臨床資訊。" * 12,
            "病灶距離中線約一公里的說法僅為語境測試，內容仍使用繁體中文。" * 12,
        )
        for summary in traditional_controls:
            with self.subTest(summary=summary[:12]):
                segment = self.valid_segment(summary_zh=summary)
                self.assertNotIn("simplified_chinese", {item.code for item in validate_segment_content(segment, "")})

    def test_opencc_missing_or_conversion_failure_fails_closed_as_structured_finding(self):
        with patch("lecture_content_rules._load_opencc_converter", side_effect=ImportError("missing")):
            codes = {item.code for item in validate_segment_content(self.valid_segment(), "")}
        self.assertIn("opencc_unavailable", codes)

        class BrokenConverter:
            def convert(self, _text):
                raise RuntimeError("conversion failed")

        with patch("lecture_content_rules._load_opencc_converter", return_value=BrokenConverter()):
            findings = validate_segment_content(self.valid_segment(), "")
        self.assertIn("opencc_failure", {item.code for item in findings})
        self.assertTrue(all("conversion failed" not in item.message for item in findings))

    def test_rejects_excessive_summary_and_takeaway_transcript_copy(self):
        copied = "講者逐字說明病灶位於深部白質並呈現不規則增強與中央壞死，周邊另有明顯水腫。"
        transcript = copied + "\n" + copied + "\n" + copied
        segment = self.valid_segment(
            summary_zh=(copied * 6),
            takeaways_zh=[copied, "乙重點", "丙重點", "丁重點"],
        )
        codes = {item.code for item in validate_segment_content(segment, transcript)}
        self.assertTrue({"transcript_copy", "takeaway_transcript_copy"}.issubset(codes))

    def test_sensitive_scanner_catches_all_configured_kinds_without_returning_values(self):
        text = (
            "病歷號：AB-12345678；姓名：王小明；生日：1980/01/02；電話：0912-345-678；"
            "身分證：A123456789；email：patient@example.org；病人識別碼：PT-998877"
        )
        self.assertEqual(
            contains_sensitive_data(text),
            ["medical_record_number", "patient_name", "birth_date", "phone", "national_id", "email", "identifier"],
        )

    def test_sensitive_scanner_normalizes_fullwidth_zero_width_and_obfuscated_separators(self):
        text = "ＭＲＮ​：ＡＢ－１２３４５６；姓 名：陳 小 華；電 話：０９１２ ３４５ ６７８；Ｅ－ｍａｉｌ：a . b + x ＠ e x a m p l e ． t w"
        kinds = set(contains_sensitive_data(text))
        self.assertTrue({"medical_record_number", "patient_name", "phone", "email"}.issubset(kinds))

    def test_sensitive_scanner_canonicalizes_unicode_dashes_and_name_punctuation(self):
        text = "病歷號 AB‑12345678；姓名 王・小明；生日 1980‑01‑02；電話 0912‑345‑678；病人識別碼 PT‑998877"
        self.assertEqual(
            contains_sensitive_data(text),
            ["medical_record_number", "patient_name", "birth_date", "phone", "identifier"],
        )

    def test_sensitive_scanner_does_not_flag_unlabelled_teaching_metadata(self):
        texts = (
            "王小明教授於 1980-01-02 發表文章，圖號 PT-998877，肺癌病史為一般教學主題。",
            "MRN protocol demonstrates peripheral nerve signal abnormality.",
        )
        for text in texts:
            with self.subTest(text=text):
                self.assertEqual(contains_sensitive_data(text), [])

    def test_sensitive_scanner_rejects_non_string_and_oversized_input_without_echoing_content(self):
        with self.assertRaisesRegex(TypeError, "text must be a string"):
            contains_sensitive_data(Path("secret"))
        with self.assertRaisesRegex(ValueError, "text exceeds maximum length"):
            contains_sensitive_data("甲" * 2_000_001)

    def test_evidence_packet_is_canonical_deterministic_and_contains_paragraph_evidence(self):
        first = self.packet()
        second = self.packet()
        self.assertEqual(first, second)
        self.assertRegex(first["packet_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual([item["source"] for item in first["paragraph_evidence"]], ["transcript", "transcript"])
        self.assertEqual(first["frame_evidence"][0]["source"], "frame_ocr")
        self.assertIn("editorial_notes_zh", first["existing_content"])

    def test_packet_hash_changes_for_source_timing_case_or_editorial_evidence(self):
        base = self.packet()
        variants = [
            {"transcript_text": "不同來源內容"},
            {"end": 20.1},
            {"frames": [{"time": 12.0, "ocr": "不同病例影像文字", "path": "frames/f012.jpg"}]},
            {"existing_segment": self.valid_segment(editorial_notes_zh=["不同編輯補充"])}
        ]
        for changes in variants:
            args = {
                "lecture_id": "lecture-01", "segment_index": 2, "start": 10.0, "end": 20.0,
                "transcript_text": "第一段講者內容。\n\n第二段講者內容。",
                "frames": [{"time": 12.0, "ocr": "影像文字", "path": "frames/f012.jpg"}],
                "existing_segment": self.valid_segment(),
            }
            args.update(changes)
            with self.subTest(changes=tuple(changes)):
                self.assertNotEqual(build_evidence_packet(**args)["packet_sha256"], base["packet_sha256"])

    def test_build_evidence_packet_rejects_type_confusion_bool_nonfinite_empty_and_long_values(self):
        bad_cases = (
            ({"lecture_id": ""}, "lecture_id"),
            ({"lecture_id": "x" * 257}, "lecture_id"),
            ({"segment_index": True}, "segment_index"),
            ({"start": True}, "start"),
            ({"end": float("inf")}, "end"),
            ({"frames": "frames/f.jpg"}, "frames"),
            ({"existing_segment": []}, "existing_segment"),
        )
        base = {
            "lecture_id": "lecture-01", "segment_index": 2, "start": 10.0, "end": 20.0,
            "transcript_text": "內容", "frames": [], "existing_segment": self.valid_segment(),
        }
        for changes, message in bad_cases:
            args = dict(base)
            args.update(changes)
            with self.subTest(changes=changes):
                with self.assertRaisesRegex((TypeError, ValueError), message):
                    build_evidence_packet(**args)

    def test_evidence_packet_rejects_absolute_parent_path_object_and_nul_paths(self):
        bad_paths = ("C:/secret/f.jpg", "/secret/f.jpg", "../secret/f.jpg", Path("frames/f.jpg"), "frames/\x00f.jpg")
        for bad_path in bad_paths:
            with self.subTest(path=repr(bad_path)):
                with self.assertRaisesRegex((TypeError, ValueError), "frame path"):
                    build_evidence_packet(
                        "lecture-01",
                        2,
                        10.0,
                        20.0,
                        "內容",
                        [{"time": 12.0, "ocr": "影像文字", "path": bad_path}],
                        self.valid_segment(),
                    )

    def test_review_record_accepts_matching_hash_identity_and_all_exact_confirmations(self):
        packet = self.packet()
        findings = validate_review_record(packet, self.valid_segment(), self.valid_review(packet))
        self.assertEqual(findings, [])

    def test_review_boole_cannot_approve_unsupported_case_claims(self):
        packet = self.packet()
        claim = "病人有肺癌病史，影像顯示腦轉移並合併出血。"
        rewritten = self.valid_segment(summary_zh=self.valid_summary() + claim)
        findings = validate_review_record(packet, rewritten, self.valid_review(packet))
        unsupported = [item for item in findings if item.code == "unsupported_case_claim"]
        self.assertEqual([item.path for item in unsupported], ["summary_zh"])
        self.assertTrue(all("肺癌" not in item.message and "出血" not in item.message for item in unsupported))

    def test_case_claim_requires_valid_packet_citation_with_supporting_evidence_span(self):
        claim = "病人有肺癌病史，影像顯示腦轉移並合併出血。"
        packet = build_evidence_packet(
            "lecture-01", 2, 10.0, 20.0, "此段只討論正常腦部解剖與掃描參數。", [], self.valid_segment()
        )
        review = self.valid_review(packet)
        review["case_claim_citations"] = [{
            "path": "summary_zh",
            "claim": claim,
            "citations": ["transcript:p1"],
        }]
        rewritten = self.valid_segment(summary_zh=self.valid_summary() + claim)
        self.assertIn(
            "unsupported_case_claim",
            {item.code for item in validate_review_record(packet, rewritten, review)},
        )

        supported_packet = build_evidence_packet(
            "lecture-01", 2, 10.0, 20.0, claim, [], self.valid_segment()
        )
        supported_review = self.valid_review(supported_packet)
        supported_review["case_claim_citations"] = [{
            "path": "summary_zh",
            "claim": claim,
            "citations": ["transcript:p1"],
        }]
        supported_codes = {
            item.code
            for item in validate_review_record(supported_packet, rewritten, supported_review)
        }
        self.assertNotIn("unsupported_case_claim", supported_codes)

    def test_negated_evidence_cannot_support_positive_case_claim(self):
        claim = "病人有肺癌病史，影像顯示腦轉移並合併出血。"
        packet = build_evidence_packet(
            "lecture-01",
            2,
            10.0,
            20.0,
            "病人沒有肺癌病史，影像未顯示腦轉移，也沒有出血。",
            [],
            self.valid_segment(),
        )
        review = self.valid_review(packet)
        review["case_claim_citations"] = [{
            "path": "summary_zh",
            "claim": claim,
            "citations": ["transcript:p1"],
        }]
        rewritten = self.valid_segment(summary_zh=self.valid_summary() + claim)
        codes = {item.code for item in validate_review_record(packet, rewritten, review)}
        self.assertIn("unsupported_case_claim", codes)

    def test_implicit_case_assertion_without_subject_requires_evidence(self):
        claim = "可見多發腦轉移並合併出血。"
        packet = self.packet()
        rewritten = self.valid_segment(summary_zh=self.valid_summary() + claim)
        findings = validate_review_record(packet, rewritten, self.valid_review(packet))
        self.assertEqual(
            [item.path for item in findings if item.code == "unsupported_case_claim"],
            ["summary_zh"],
        )

    def test_contradictory_clause_cannot_be_masked_by_supported_clause(self):
        claim = "可見多發腦轉移並合併出血。"
        packet = build_evidence_packet(
            "lecture-01", 2, 10.0, 20.0, "可見多發腦轉移，但未見出血。", [], self.valid_segment()
        )
        review = self.valid_review(packet)
        review["case_claim_citations"] = [{
            "path": "summary_zh",
            "claim": claim,
            "citations": ["transcript:p1"],
        }]
        rewritten = self.valid_segment(summary_zh=self.valid_summary() + claim)
        findings = validate_review_record(packet, rewritten, review)
        self.assertIn("unsupported_case_claim", {item.code for item in findings})
        self.assertTrue(all("出血" not in item.message for item in findings))

    def test_uncited_case_assertions_fail_closed_without_diagnosis_vocabulary(self):
        claims = (
            "可見左額葉腫塊伴顯著水腫。",
            "呈現左側顳葉病灶與周邊水腫。",
            "右額葉有不規則增強腫塊。",
        )
        packet = self.packet()
        for claim in claims:
            with self.subTest(claim=claim):
                rewritten = self.valid_segment(summary_zh=self.valid_summary() + claim)
                codes = {
                    item.code
                    for item in validate_review_record(packet, rewritten, self.valid_review(packet))
                }
                self.assertIn("unsupported_case_claim", codes)

    def test_non_editorial_diagnostic_and_location_assertions_require_citations(self):
        claims = (
            "最終診斷為惡性腫瘤。",
            "病理證實為高級別腫瘤。",
            "病灶位於左額葉深部白質。",
        )
        packet = self.packet()
        for claim in claims:
            with self.subTest(claim=claim):
                rewritten = self.valid_segment(summary_zh=self.valid_summary() + claim)
                codes = {
                    item.code
                    for item in validate_review_record(packet, rewritten, self.valid_review(packet))
                }
                self.assertIn("unsupported_case_claim", codes)

    def test_diagnostic_and_location_assertions_accept_matching_clause_evidence(self):
        claims = (
            "最終診斷為惡性腫瘤。",
            "病理證實為高級別腫瘤。",
            "病灶位於左額葉深部白質。",
        )
        for claim in claims:
            with self.subTest(claim=claim):
                packet = build_evidence_packet(
                    "lecture-01", 2, 10.0, 20.0, claim, [], self.valid_segment()
                )
                review = self.valid_review(packet)
                review["case_claim_citations"] = [{
                    "path": "summary_zh",
                    "claim": claim,
                    "citations": ["transcript:p1"],
                }]
                rewritten = self.valid_segment(summary_zh=self.valid_summary() + claim)
                codes = {item.code for item in validate_review_record(packet, rewritten, review)}
                self.assertNotIn("unsupported_case_claim", codes)

    def test_diagnostic_assertion_rejects_opposite_clause_evidence(self):
        claim = "最終診斷為惡性腫瘤。"
        packet = build_evidence_packet(
            "lecture-01", 2, 10.0, 20.0, "最終診斷不是惡性腫瘤。", [], self.valid_segment()
        )
        review = self.valid_review(packet)
        review["case_claim_citations"] = [{
            "path": "summary_zh",
            "claim": claim,
            "citations": ["transcript:p1"],
        }]
        rewritten = self.valid_segment(summary_zh=self.valid_summary() + claim)
        codes = {item.code for item in validate_review_record(packet, rewritten, review)}
        self.assertIn("unsupported_case_claim", codes)

    def test_same_polarity_categorical_mismatch_fails_closed(self):
        cases = (
            ("病灶位於左額葉深部白質。", "病灶位於右額葉深部白質。"),
            ("最終診斷為惡性腫瘤。", "最終診斷為良性腫瘤。"),
            ("病理證實為肺癌轉移。", "病理證實為乳癌轉移。"),
        )
        for claim, evidence_text in cases:
            with self.subTest(claim=claim, evidence=evidence_text):
                packet = build_evidence_packet(
                    "lecture-01", 2, 10.0, 20.0, evidence_text, [], self.valid_segment()
                )
                review = self.valid_review(packet)
                review["case_claim_citations"] = [{
                    "path": "summary_zh",
                    "claim": claim,
                    "citations": ["transcript:p1"],
                }]
                rewritten = self.valid_segment(summary_zh=self.valid_summary() + claim)
                findings = validate_review_record(packet, rewritten, review)
                self.assertIn("unsupported_case_claim", {item.code for item in findings})
                self.assertTrue(all(claim not in item.message for item in findings))

    def test_supported_multiclause_claim_requires_support_for_each_clause(self):
        claim = "可見左額葉腫塊伴顯著水腫。"
        packet = build_evidence_packet(
            "lecture-01", 2, 10.0, 20.0, "可見左額葉腫塊，伴有顯著水腫。", [], self.valid_segment()
        )
        review = self.valid_review(packet)
        review["case_claim_citations"] = [
            {
                "path": "summary_zh",
                "claim": "可見左額葉腫塊",
                "citations": ["transcript:p1"],
            },
            {
                "path": "summary_zh",
                "claim": "顯著水腫",
                "citations": ["transcript:p1"],
            },
        ]
        rewritten = self.valid_segment(summary_zh=self.valid_summary() + claim)
        codes = {item.code for item in validate_review_record(packet, rewritten, review)}
        self.assertNotIn("unsupported_case_claim", codes)

    def test_mixed_polarity_claim_is_bound_clause_by_clause(self):
        claim = "可見左額葉腫塊但未見出血。"
        packet = build_evidence_packet(
            "lecture-01", 2, 10.0, 20.0, "可見左額葉腫塊，未見出血。", [], self.valid_segment()
        )
        review = self.valid_review(packet)
        review["case_claim_citations"] = [
            {
                "path": "summary_zh",
                "claim": "可見左額葉腫塊",
                "citations": ["transcript:p1"],
            },
            {
                "path": "summary_zh",
                "claim": "未見出血",
                "citations": ["transcript:p1"],
            },
        ]
        rewritten = self.valid_segment(summary_zh=self.valid_summary() + claim)
        codes = {item.code for item in validate_review_record(packet, rewritten, review)}
        self.assertNotIn("unsupported_case_claim", codes)

    def test_case_claim_citations_fail_closed_on_empty_wrong_and_type_confused_values(self):
        claim = "可見左額葉腫塊。"
        packet = build_evidence_packet(
            "lecture-01", 2, 10.0, 20.0, claim, [], self.valid_segment()
        )
        bad_records = (
            [],
            [{"path": "summary_zh", "claim": claim, "citations": []}],
            [{"path": "summary_zh", "claim": claim, "citations": ["transcript:p999"]}],
            [{"path": "summary_zh", "claim": claim, "citations": "transcript:p1"}],
            [{"path": "summary_zh", "claim": claim, "citations": True}],
            [{"path": "summary_zh", "claim": claim, "citations": [True]}],
            [{"path": True, "claim": claim, "citations": ["transcript:p1"]}],
            [{"path": "summary_zh", "claim": True, "citations": ["transcript:p1"]}],
            [{"path": ["summary_zh"], "claim": claim, "citations": ["transcript:p1"]}],
            [True],
            "not-a-list",
            True,
        )
        rewritten = self.valid_segment(summary_zh=self.valid_summary() + claim)
        for records in bad_records:
            with self.subTest(records_type=type(records).__name__, records=repr(records)):
                review = self.valid_review(packet)
                review["case_claim_citations"] = records
                codes = {item.code for item in validate_review_record(packet, rewritten, review)}
                self.assertIn("unsupported_case_claim", codes)

    def test_unicode_punctuation_splits_case_claims_without_cross_clause_masking(self):
        claim = "可見多發腦轉移，合併出血；另見左額葉腫塊。"
        packet = build_evidence_packet(
            "lecture-01", 2, 10.0, 20.0, "可見多發腦轉移、未見出血；另見左額葉腫塊。", [], self.valid_segment()
        )
        review = self.valid_review(packet)
        review["case_claim_citations"] = [{
            "path": "summary_zh",
            "claim": claim,
            "citations": ["transcript:p1"],
        }]
        rewritten = self.valid_segment(summary_zh=self.valid_summary() + claim)
        self.assertIn(
            "unsupported_case_claim",
            {item.code for item in validate_review_record(packet, rewritten, review)},
        )

    def test_general_medical_editorial_is_not_treated_as_a_case_claim(self):
        packet = self.packet()
        rewritten = self.valid_segment(editorial_notes_zh=[
            "編輯補充：肺癌可能轉移至腦部並造成出血，此為一般醫學背景，不代表本病例診斷。"
        ])
        codes = {item.code for item in validate_review_record(packet, rewritten, self.valid_review(packet))}
        self.assertNotIn("unsupported_case_claim", codes)

    def test_review_record_recomputes_packet_hash_and_rejects_tampering(self):
        packet = self.packet()
        review = self.valid_review(packet)
        tampered = copy.deepcopy(packet)
        tampered["transcript_text"] = "竄改內容"
        codes = {item.code for item in validate_review_record(tampered, self.valid_segment(), review)}
        self.assertIn("packet_hash_invalid", codes)

    def test_recomputed_hash_cannot_authenticate_invented_paragraph_evidence(self):
        claim = "最終診斷為惡性腫瘤。"
        packet = self.packet()
        tampered = copy.deepcopy(packet)
        tampered["paragraph_evidence"] = [{
            "source": "transcript",
            "paragraph_index": 999,
            "text": claim,
        }]
        tampered["source_citations"] = ["transcript:p999"]
        without_hash = {key: value for key, value in tampered.items() if key != "packet_sha256"}
        tampered["packet_sha256"] = hashlib.sha256(canonical_packet_bytes(without_hash)).hexdigest()
        review = self.valid_review(tampered)
        review["case_claim_citations"] = [{
            "path": "summary_zh",
            "claim": claim,
            "citations": ["transcript:p999"],
        }]
        rewritten = self.valid_segment(summary_zh=self.valid_summary() + claim)
        findings = validate_review_record(tampered, rewritten, review)
        self.assertIn("packet_evidence_mismatch", {item.code for item in findings})
        self.assertIn("unsupported_case_claim", {item.code for item in findings})
        self.assertTrue(all(claim not in item.message for item in findings))

    def test_derived_packet_evidence_validates_against_source_fields(self):
        packet = self.packet()
        findings = validate_review_record(packet, self.valid_segment(), self.valid_review(packet))
        self.assertNotIn("packet_evidence_mismatch", {item.code for item in findings})

    def test_review_record_rejects_wrong_hash_empty_or_nonstring_reviewer_and_missing_confirmations(self):
        packet = self.packet()
        cases = (
            ({**self.valid_review(packet), "packet_sha256": "0" * 64}, "review_packet_mismatch"),
            ({**self.valid_review(packet), "reviewer": ""}, "reviewer_missing"),
            ({**self.valid_review(packet), "reviewer": "​⁠"}, "reviewer_missing"),
            ({**self.valid_review(packet), "reviewer": "　​ "}, "reviewer_missing"),
            ({**self.valid_review(packet), "reviewer": True}, "reviewer_missing"),
            ({**self.valid_review(packet), "source_faithful": 1}, "source_faithful_missing"),
            ({**self.valid_review(packet), "case_details_verified": False}, "case_detail_check_missing"),
            ({**self.valid_review(packet), "editorial_separated": None}, "editorial_check_missing"),
        )
        for review, expected in cases:
            with self.subTest(expected=expected):
                codes = {item.code for item in validate_review_record(packet, self.valid_segment(), review)}
                self.assertIn(expected, codes)

    def test_review_record_rejects_sensitive_packet_without_exposing_sensitive_value(self):
        packet = build_evidence_packet(
            "lecture-01", 2, 10.0, 20.0, "病歷號：AB12345678", [], self.valid_segment()
        )
        findings = validate_review_record(packet, self.valid_segment(), self.valid_review(packet))
        self.assertIn("sensitive_evidence", {item.code for item in findings})
        self.assertTrue(all("AB12345678" not in item.message for item in findings))

    def test_review_record_rejects_mapping_type_confusion(self):
        packet = self.packet()
        for packet_value, rewritten, review in (([], self.valid_segment(), {}), (packet, [], {}), (packet, self.valid_segment(), [])):
            with self.subTest(packet_type=type(packet_value).__name__, rewritten_type=type(rewritten).__name__, review_type=type(review).__name__):
                findings = validate_review_record(packet_value, rewritten, review)
                self.assertTrue(any(item.severity == "error" for item in findings))


if __name__ == "__main__":
    unittest.main()
