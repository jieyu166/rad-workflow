from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "lecture-to-notes" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import rewrite_evidence
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
            "title": "後顱窩腫瘤影像判讀策略",
            "summary_zh": self.valid_summary(),
            "takeaways_zh": [
                "先由病灶位置與邊界建立判讀方向",
                "整合增強水腫擴散與灌流表現",
                "鑑別時逐項核對課堂已提供證據",
                "病例結論不可超出講者陳述範圍",
            ],
            "editorial_notes_zh": ["編輯補充：新版分類資訊僅供延伸閱讀。"],
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
            [{
                "identity": "frame-017",
                "time": 12.0,
                "ocr": "影像文字",
                "path": "frames/f012.jpg",
                "asset_sha256": "1" * 64,
            }],
            self.valid_segment(),
        )

    def trusted_frame_sources(self):
        source = {
            "identity": "frame-017",
            "path": "frames/f012.jpg",
            "time": 12.0,
            "ocr": "影像文字",
            "asset_sha256": "1" * 64,
        }
        source["source_sha256"] = hashlib.sha256(
            canonical_packet_bytes(source)
        ).hexdigest()
        return [source]

    def valid_review(self, packet):
        return {
            "packet_sha256": packet["packet_sha256"],
            "reviewer": "A80748",
            "source_faithful": True,
            "case_details_verified": True,
            "editorial_separated": True,
        }

    def rehash_packet(self, packet):
        without_hash = {key: value for key, value in packet.items() if key != "packet_sha256"}
        packet["packet_sha256"] = hashlib.sha256(canonical_packet_bytes(without_hash)).hexdigest()

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
        for editorial in ("補充", [""], [True]):
            with self.subTest(editorial=editorial):
                codes = {item.code for item in validate_segment_content(self.valid_segment(editorial_notes_zh=editorial), "")}
                self.assertIn("editorial_type", codes)

    def test_rejects_unfinished_and_template_markers_even_with_separators(self):
        markers = ("TODO", "T B D", "FIXME", "PLACEHOLDER", "請補充", "待確認", "待​確認", "請⁠補充", "此處填入", "內容待補", "尚未完成")
        for marker in markers:
            with self.subTest(marker=marker):
                codes = {item.code for item in validate_segment_content(self.valid_segment(editorial_notes_zh=[marker]), "")}
                self.assertIn("unfinished_marker", codes)

    def test_opencc_gate_rejects_simplified_text_and_preserves_taiwan_terms(self):
        simplified_controls = (
            "脑肿瘤影像显示强化与水肿，医生需要结合扩散、灌注与临床资料进行鉴别。" * 9,
            "该患者检查显示脑部肿块并伴随明显水肿，需要结合临床资料判断。" * 10,
        )
        for summary in simplified_controls:
            with self.subTest(summary=summary[:12]):
                self.assertIn("simplified_chinese", {item.code for item in validate_segment_content(self.valid_segment(summary_zh=summary), "")})
        traditional_controls = (
            "臺灣常用的神經放射學術語與影像判讀內容，著重病灶位置與鑑別。" * 12,
            "金屬干擾偽影會影響影像品質，判讀時需整合不同序列與臨床資訊。" * 12,
            "病灶距離中線約一公里的說法僅為語境測試，內容仍使用繁體中文。" * 12,
        )
        for summary in traditional_controls:
            with self.subTest(summary=summary[:12]):
                self.assertNotIn("simplified_chinese", {item.code for item in validate_segment_content(self.valid_segment(summary_zh=summary), "")})

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
        segment = self.valid_segment(summary_zh=(copied * 6), takeaways_zh=[copied, "乙重點", "丙重點", "丁重點"])
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
        self.assertEqual(contains_sensitive_data(text), ["medical_record_number", "patient_name", "birth_date", "phone", "identifier"])

    def test_sensitive_scanner_does_not_flag_unlabelled_teaching_metadata(self):
        for text in (
            "王小明教授於 1980-01-02 發表文章，圖號 PT-998877，肺癌病史為一般教學主題。",
            "MRN protocol demonstrates peripheral nerve signal abnormality.",
        ):
            with self.subTest(text=text):
                self.assertEqual(contains_sensitive_data(text), [])

    def test_sensitive_scanner_rejects_non_string_and_oversized_input_without_echoing_content(self):
        with self.assertRaisesRegex(TypeError, "text must be a string"):
            contains_sensitive_data(Path("secret"))
        with self.assertRaisesRegex(ValueError, "text exceeds maximum length"):
            contains_sensitive_data("甲" * 2_000_001)

    def test_evidence_packet_derives_stable_frame_identity_when_missing(self):
        packet = build_evidence_packet(
            "lecture-01",
            2,
            10.0,
            20.0,
            "內容",
            [{
                "time": 12.0,
                "ocr": "影像文字",
                "path": "frames/f012.jpg",
                "asset_sha256": "1" * 64,
            }],
            self.valid_segment(),
        )
        self.assertEqual(packet["frame_sources"][0]["identity"], "frame-0001")

    def test_evidence_packet_is_canonical_deterministic_and_hashes_sources(self):
        first = self.packet()
        second = self.packet()
        self.assertEqual(first, second)
        self.assertRegex(first["packet_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual([item["identity"] for item in first["paragraph_evidence"]], ["p-0001", "p-0002"])
        self.assertTrue(all(re.fullmatch(r"[0-9a-f]{64}", item["source_sha256"]) for item in first["paragraph_evidence"]))
        self.assertEqual(first["frame_evidence"][0]["identity"], "frame-017")
        self.assertIn("editorial_notes_zh", first["existing_content"])

    def test_packet_hash_changes_for_source_timing_case_or_editorial_evidence(self):
        base = self.packet()
        variants = [
            {"transcript_text": "不同來源內容"},
            {"end": 20.1},
            {"frames": [{"identity": "frame-017", "time": 12.0, "ocr": "不同病例影像文字", "path": "frames/f012.jpg", "asset_sha256": "1" * 64}]},
            {"existing_segment": self.valid_segment(editorial_notes_zh=["不同編輯補充"])},
        ]
        for changes in variants:
            args = {
                "lecture_id": "lecture-01", "segment_index": 2, "start": 10.0, "end": 20.0,
                "transcript_text": "第一段講者內容。\n\n第二段講者內容。",
                "frames": [{"identity": "frame-017", "time": 12.0, "ocr": "影像文字", "path": "frames/f012.jpg", "asset_sha256": "1" * 64}],
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
        for bad_path in ("C:/secret/f.jpg", "/secret/f.jpg", "../secret/f.jpg", Path("frames/f.jpg"), "frames/\x00f.jpg"):
            with self.subTest(path=repr(bad_path)):
                with self.assertRaisesRegex((TypeError, ValueError), "frame path"):
                    build_evidence_packet(
                        "lecture-01", 2, 10.0, 20.0, "內容",
                        [{"identity": "frame-017", "time": 12.0, "ocr": "影像文字", "path": bad_path, "asset_sha256": "1" * 64}],
                        self.valid_segment(),
                    )

    def transcript_citation(self, packet, index=0):
        source = packet["paragraph_evidence"][index]
        return {"identity": source["identity"], "type": "transcript", "source_sha256": source["source_sha256"]}

    def frame_citation(self, packet):
        source = packet["frame_sources"][0]
        return {
            "identity": source["identity"], "type": "frame",
            "source_sha256": source["source_sha256"], "asset_sha256": source["asset_sha256"],
        }

    def reviewed(
        self,
        packet,
        candidate=None,
        citations=None,
        reviewer="reviewer-001",
        title_kind="topical",
    ):
        candidate = candidate or self.valid_segment()
        default_citation = self.transcript_citation(packet)
        units = ["summary_zh", *(f"takeaways_zh[{index}]" for index in range(4))]
        citation_map = []
        attestations = []
        for unit in units:
            unit_citations = copy.deepcopy((citations or {}).get(unit, [default_citation]))
            citation_map.append({"content_unit": unit, "citations": unit_citations})
            attestations.append({
                "content_unit": unit,
                "citations": copy.deepcopy(unit_citations),
                "support_confirmed": True,
            })
        title_citations = copy.deepcopy((citations or {}).get("title", []))
        if title_citations:
            citation_map.append({
                "content_unit": "title",
                "citations": title_citations,
            })
            attestations.append({
                "content_unit": "title",
                "citations": copy.deepcopy(title_citations),
                "support_confirmed": True,
            })
        review = {
            "evidence_packet_sha256": packet["packet_sha256"],
            "reviewer_id": reviewer,
            "source_support_confirmed": True,
            "case_facts_confirmed": True,
            "editorial_separation_confirmed": True,
            "review_schema": "lecture-content-review",
            "review_version": 1,
            "title_kind": title_kind,
            "topical_title_confirmed": title_kind == "topical",
            "citation_map": citation_map,
            "claim_attestations": attestations,
        }
        review = rewrite_evidence.finalize_review_record(packet, candidate, review)
        approved_run = {
            "approved_candidate_sha256": review["approved_candidate_sha256"],
            "review_attestation_sha256": review["review_attestation_sha256"],
        }
        return review, approved_run

    def validate_approved(
        self,
        packet,
        candidate,
        review,
        approved_run,
        trusted_frames=None,
        approved_packet_sha256=None,
    ):
        return validate_review_record(
            packet,
            candidate,
            review,
            trusted_frame_sources=(self.trusted_frame_sources() if trusted_frames is None else trusted_frames),
            approved_run=approved_run,
            approved_packet_sha256=(
                packet["packet_sha256"]
                if approved_packet_sha256 is None
                else approved_packet_sha256
            ),
        )

    def test_supported_paraphrase_and_topical_title_pass(self):
        packet = self.packet()
        candidate = self.valid_segment(title="後顱窩腫瘤影像判讀策略")
        review, approved_run = self.reviewed(packet, candidate)
        self.assertEqual(self.validate_approved(packet, candidate, review, approved_run), [])

    def test_unchanged_legacy_content_without_claim_attestations_fails(self):
        packet = self.packet()
        findings = validate_review_record(packet, self.valid_segment(), self.valid_review(packet))
        codes = {item.code for item in findings}
        self.assertIn("missing_citation", codes)
        self.assertIn("missing_attestation", codes)

    def test_case_specific_title_requires_and_accepts_trusted_attestation(self):
        packet = self.packet()
        candidate = self.valid_segment(title="本病例為左側小腦轉移瘤")
        review, approved_run = self.reviewed(packet, candidate)
        codes = {item.code for item in self.validate_approved(packet, candidate, review, approved_run)}
        self.assertTrue({"missing_citation", "missing_attestation"}.issubset(codes))
        citation = self.transcript_citation(packet)
        review, approved_run = self.reviewed(
            packet,
            candidate,
            citations={"title": [citation]},
            title_kind="case_claim",
        )
        codes = {item.code for item in self.validate_approved(packet, candidate, review, approved_run)}
        self.assertNotIn("missing_citation", codes)
        self.assertNotIn("missing_attestation", codes)

    def test_generic_diagnosis_title_is_a_topical_label(self):
        packet = self.packet()
        candidate = self.valid_segment(title="腦膜瘤")
        review, approved_run = self.reviewed(packet, candidate)
        self.assertEqual(
            self.validate_approved(packet, candidate, review, approved_run),
            [],
        )

    def test_demographic_case_context_overrides_topical_title_suffix(self):
        packet = self.packet()
        citation = self.transcript_citation(packet)
        for title in (
            "68歲女性左側小腦轉移瘤影像判讀策略",
            "68歲男性之右額葉腫瘤診斷原則",
        ):
            with self.subTest(title=title):
                candidate = self.valid_segment(title=title)
                review, approved_run = self.reviewed(packet, candidate)
                codes = {
                    item.code
                    for item in self.validate_approved(
                        packet,
                        candidate,
                        review,
                        approved_run,
                    )
                }
                self.assertTrue({
                    "missing_citation",
                    "missing_attestation",
                }.issubset(codes))

                review, approved_run = self.reviewed(
                    packet,
                    candidate,
                    citations={"title": [citation]},
                    title_kind="case_claim",
                )
                codes = {
                    item.code
                    for item in self.validate_approved(
                        packet,
                        candidate,
                        review,
                        approved_run,
                    )
                }
                self.assertNotIn("missing_citation", codes)
                self.assertNotIn("missing_attestation", codes)

    def test_factual_titles_require_reviewed_case_classification_and_support(self):
        packet = self.packet()
        citation = self.transcript_citation(packet)
        for title in (
            "病理證實膠質母細胞瘤",
            "術後追蹤顯示腫瘤復發",
            "既往接受放射治療後腫瘤縮小",
        ):
            with self.subTest(title=title):
                candidate = self.valid_segment(title=title)

                review, _ = self.reviewed(packet, candidate)
                review.pop("title_kind")
                review.pop("topical_title_confirmed")
                review = rewrite_evidence.finalize_review_record(
                    packet,
                    candidate,
                    review,
                )
                approved_run = {
                    key: review[key]
                    for key in (
                        "approved_candidate_sha256",
                        "review_attestation_sha256",
                    )
                }
                codes = {
                    item.code
                    for item in self.validate_approved(
                        packet,
                        candidate,
                        review,
                        approved_run,
                    )
                }
                self.assertIn("title_kind_invalid", codes)

                review, approved_run = self.reviewed(
                    packet,
                    candidate,
                    title_kind="case_claim",
                )
                codes = {
                    item.code
                    for item in self.validate_approved(
                        packet,
                        candidate,
                        review,
                        approved_run,
                    )
                }
                self.assertTrue({
                    "missing_citation",
                    "missing_attestation",
                }.issubset(codes))

                review, approved_run = self.reviewed(
                    packet,
                    candidate,
                    citations={"title": [citation]},
                    title_kind="case_claim",
                )
                self.assertEqual(
                    self.validate_approved(
                        packet,
                        candidate,
                        review,
                        approved_run,
                    ),
                    [],
                )

    def test_title_kind_rejects_wrong_types_and_out_of_enum_values(self):
        packet = self.packet()
        candidate = self.valid_segment(title="腦膜瘤")
        for title_kind in (None, True, 1, "case"):
            with self.subTest(title_kind=title_kind):
                review, approved_run = self.reviewed(
                    packet,
                    candidate,
                    title_kind=title_kind,
                )
                codes = {
                    item.code
                    for item in self.validate_approved(
                        packet,
                        candidate,
                        review,
                        approved_run,
                    )
                }
                self.assertIn("title_kind_invalid", codes)

    def test_implicit_case_titles_require_trusted_title_support(self):
        packet = self.packet()
        for title in (
            "左側小腦轉移瘤",
            "術後追蹤無復發",
            "肺癌病史併新發腦病灶",
            "左側小腦轉移瘤伴周邊水腫",
            "左側小腦轉移瘤（68歲女性）",
        ):
            with self.subTest(title=title):
                candidate = self.valid_segment(title=title)
                review, approved_run = self.reviewed(packet, candidate)
                codes = {
                    item.code
                    for item in self.validate_approved(
                        packet,
                        candidate,
                        review,
                        approved_run,
                    )
                }
                self.assertTrue({
                    "missing_citation",
                    "missing_attestation",
                }.issubset(codes))

    def test_title_classification_tamper_breaks_both_digests(self):
        packet = self.packet()
        candidate = self.valid_segment(title="腦膜瘤")
        review, approved_run = self.reviewed(packet, candidate)
        tampered = copy.deepcopy(review)
        tampered["title_kind"] = "case_claim"
        codes = {
            item.code
            for item in self.validate_approved(
                packet,
                candidate,
                tampered,
                approved_run,
            )
        }
        self.assertIn("candidate_digest_mismatch", codes)
        self.assertIn("review_attestation_mismatch", codes)

    def test_title_confirmation_tamper_breaks_only_review_digest(self):
        packet = self.packet()
        candidate = self.valid_segment(title="腦膜瘤")
        review, approved_run = self.reviewed(packet, candidate)
        for value in (False, 1):
            with self.subTest(value=value):
                tampered = copy.deepcopy(review)
                tampered["topical_title_confirmed"] = value
                codes = {
                    item.code
                    for item in self.validate_approved(
                        packet,
                        candidate,
                        tampered,
                        approved_run,
                    )
                }
                self.assertNotIn("candidate_digest_mismatch", codes)
                self.assertIn("review_attestation_mismatch", codes)

    def test_topical_title_rejects_evidence_and_requires_exact_confirmation(self):
        packet = self.packet()
        candidate = self.valid_segment(title="腦膜瘤")
        citation = self.transcript_citation(packet)
        review, approved_run = self.reviewed(
            packet,
            candidate,
            citations={"title": [citation]},
        )
        codes = {
            item.code
            for item in self.validate_approved(
                packet,
                candidate,
                review,
                approved_run,
            )
        }
        self.assertIn("topical_title_evidence_invalid", codes)

        review, approved_run = self.reviewed(packet, candidate)
        review["topical_title_confirmed"] = 1
        review = rewrite_evidence.finalize_review_record(packet, candidate, review)
        approved_run = {
            key: review[key]
            for key in (
                "approved_candidate_sha256",
                "review_attestation_sha256",
            )
        }
        codes = {
            item.code
            for item in self.validate_approved(
                packet,
                candidate,
                review,
                approved_run,
            )
        }
        self.assertIn("topical_title_confirmation", codes)

    def test_missing_speaker_claim_coverage_fails_with_unit_identity(self):
        packet = self.packet()
        candidate = self.valid_segment()
        review, _ = self.reviewed(packet, candidate)
        review["citation_map"] = [item for item in review["citation_map"] if item["content_unit"] != "takeaways_zh[3]"]
        review["claim_attestations"] = [item for item in review["claim_attestations"] if item["content_unit"] != "takeaways_zh[3]"]
        review = rewrite_evidence.finalize_review_record(packet, candidate, review)
        approved_run = {key: review[key] for key in ("approved_candidate_sha256", "review_attestation_sha256")}
        missing = [item for item in self.validate_approved(packet, candidate, review, approved_run) if item.path == "takeaways_zh[3]"]
        self.assertTrue({"missing_citation", "missing_attestation"}.issubset({item.code for item in missing}))

    def test_attestation_citation_set_must_match_candidate_citation_map(self):
        packet = self.packet()
        candidate = self.valid_segment()
        review, _ = self.reviewed(packet, candidate)
        review["claim_attestations"][0]["citations"] = [self.transcript_citation(packet, 1)]
        review = rewrite_evidence.finalize_review_record(packet, candidate, review)
        approved_run = {key: review[key] for key in ("approved_candidate_sha256", "review_attestation_sha256")}
        findings = self.validate_approved(packet, candidate, review, approved_run)
        self.assertIn("citation_binding_mismatch", {item.code for item in findings})

    def test_packet_chapter_identity_types_fail_closed_after_coherent_reapproval(self):
        candidate = self.valid_segment()
        for field, value in (("lecture_id", True), ("segment_index", "2")):
            with self.subTest(field=field):
                packet = self.packet()
                packet[field] = value
                self.rehash_packet(packet)
                review, approved_run = self.reviewed(packet, candidate)
                codes = {
                    item.code
                    for item in self.validate_approved(
                        packet,
                        candidate,
                        review,
                        approved_run,
                    )
                }
                self.assertIn("packet_identity_invalid", codes)

    def test_trusted_external_frame_citation_passes_and_packet_only_frame_fails(self):
        packet = self.packet()
        candidate = self.valid_segment()
        citation = self.frame_citation(packet)
        citations = {"summary_zh": [citation], **{f"takeaways_zh[{index}]": [citation] for index in range(4)}}
        review, approved_run = self.reviewed(packet, candidate, citations=citations)
        self.assertNotIn("untrusted_citation", {item.code for item in self.validate_approved(packet, candidate, review, approved_run)})
        forged = self.validate_approved(packet, candidate, review, approved_run, trusted_frames=[])
        self.assertIn("untrusted_citation", {item.code for item in forged})

        tampered_manifest = self.trusted_frame_sources()
        tampered_manifest[0]["source_sha256"] = "9" * 64
        tampered = self.validate_approved(
            packet,
            candidate,
            review,
            approved_run,
            trusted_frames=tampered_manifest,
        )
        self.assertIn("untrusted_citation", {item.code for item in tampered})

    def test_citation_reordering_preserves_both_digests(self):
        packet = self.packet()
        candidate = self.valid_segment()
        citations = [self.transcript_citation(packet, 0), self.transcript_citation(packet, 1)]
        by_unit = {"summary_zh": citations, **{f"takeaways_zh[{index}]": citations for index in range(4)}}
        review, approved_run = self.reviewed(packet, candidate, citations=by_unit)
        reordered = copy.deepcopy(review)
        for record in reordered["citation_map"]:
            record["citations"].reverse()
        for record in reordered["claim_attestations"]:
            record["citations"].reverse()
        self.assertEqual(self.validate_approved(packet, candidate, reordered, approved_run), [])

    def test_full_candidate_replay_changes_fail_candidate_digest(self):
        packet = self.packet()
        candidate = self.valid_segment()
        review, approved_run = self.reviewed(packet, candidate)
        variants = (
            self.valid_segment(title="腦膜瘤影像判讀策略"),
            self.valid_segment(editorial_notes_zh=["另一則編輯補充"]),
            self.valid_segment(summary_zh=self.valid_summary() + "補充句。"),
            self.valid_segment(takeaways_zh=["修改後第一項重點", *candidate["takeaways_zh"][1:]]),
        )
        for changed in variants:
            with self.subTest(field=next(key for key in candidate if candidate[key] != changed[key])):
                codes = {item.code for item in self.validate_approved(packet, changed, review, approved_run)}
                self.assertIn("candidate_digest_mismatch", codes)

    def test_chapter_identity_time_and_citation_changes_fail_replay(self):
        packet = self.packet()
        candidate = self.valid_segment()
        review, approved_run = self.reviewed(packet, candidate)
        for field, value in (("lecture_id", "lecture-02"), ("start_sec", 10.1)):
            with self.subTest(field=field):
                tampered = copy.deepcopy(packet)
                tampered[field] = value
                self.rehash_packet(tampered)
                codes = {item.code for item in self.validate_approved(tampered, candidate, review, approved_run)}
                self.assertIn("candidate_digest_mismatch", codes)
        changed_review = copy.deepcopy(review)
        changed_review["citation_map"][0]["citations"] = [self.transcript_citation(packet, 1)]
        codes = {item.code for item in self.validate_approved(packet, candidate, changed_review, approved_run)}
        self.assertIn("candidate_digest_mismatch", codes)

    def test_evidence_packet_and_claim_hash_tamper_fail_attestation_binding(self):
        packet = self.packet()
        candidate = self.valid_segment()
        review, approved_run = self.reviewed(packet, candidate)

        packet_tamper = copy.deepcopy(review)
        packet_tamper["evidence_packet_sha256"] = "9" * 64
        codes = {
            item.code
            for item in self.validate_approved(
                packet,
                candidate,
                packet_tamper,
                approved_run,
            )
        }
        self.assertTrue({
            "review_packet_mismatch",
            "review_attestation_mismatch",
        }.issubset(codes))

        claim_tamper = copy.deepcopy(review)
        claim_tamper["claim_attestations"][0]["normalized_claim_sha256"] = "8" * 64
        codes = {
            item.code
            for item in self.validate_approved(
                packet,
                candidate,
                claim_tamper,
                approved_run,
            )
        }
        self.assertIn("claim_hash_mismatch", codes)

    def test_coherent_packet_remint_cannot_replace_approved_transcript(self):
        approved_packet = self.packet()
        candidate = self.valid_segment()
        replaced_packet = build_evidence_packet(
            "lecture-01",
            2,
            10.0,
            20.0,
            "替換後第一段。\n\n替換後第二段。",
            [{
                "identity": "frame-017",
                "time": 12.0,
                "ocr": "影像文字",
                "path": "frames/f012.jpg",
                "asset_sha256": "1" * 64,
            }],
            candidate,
        )
        review, approved_run = self.reviewed(replaced_packet, candidate)
        codes = {
            item.code
            for item in self.validate_approved(
                replaced_packet,
                candidate,
                review,
                approved_run,
                approved_packet_sha256=approved_packet["packet_sha256"],
            )
        }
        self.assertTrue({
            "approved_packet_mismatch",
            "untrusted_citation",
        }.issubset(codes))

    def test_missing_external_packet_anchor_rejects_transcript_support(self):
        packet = self.packet()
        candidate = self.valid_segment()
        review, approved_run = self.reviewed(packet, candidate)
        codes = {
            item.code
            for item in validate_review_record(
                packet,
                candidate,
                review,
                trusted_frame_sources=self.trusted_frame_sources(),
                approved_run=approved_run,
            )
        }
        self.assertTrue({
            "approved_packet_mismatch",
            "untrusted_citation",
        }.issubset(codes))

    def test_reviewer_confirmation_schema_and_attestation_tamper_fail(self):
        packet = self.packet()
        candidate = self.valid_segment()
        review, approved_run = self.reviewed(packet, candidate)
        cases = (
            ("reviewer_id", "reviewer-002", "review_attestation_mismatch"),
            ("source_support_confirmed", False, "source_support_confirmation"),
            ("case_facts_confirmed", 1, "case_facts_confirmation"),
            ("editorial_separation_confirmed", None, "editorial_confirmation"),
            ("review_schema", "other", "review_schema_invalid"),
            ("review_version", True, "review_version_invalid"),
            ("review_version", 1.0, "review_version_invalid"),
        )
        for field, value, expected in cases:
            with self.subTest(field=field):
                tampered = copy.deepcopy(review)
                tampered[field] = value
                codes = {item.code for item in self.validate_approved(packet, candidate, tampered, approved_run)}
                self.assertIn(expected, codes)
                self.assertIn("review_attestation_mismatch", codes)
        tampered = copy.deepcopy(review)
        tampered["claim_attestations"][0]["support_confirmed"] = False
        codes = {item.code for item in self.validate_approved(packet, candidate, tampered, approved_run)}
        self.assertTrue({"attestation_invalid", "review_attestation_mismatch"}.issubset(codes))

    def test_approved_run_requires_both_digests(self):
        packet = self.packet()
        candidate = self.valid_segment()
        review, approved_run = self.reviewed(packet, candidate)
        for missing in ("approved_candidate_sha256", "review_attestation_sha256"):
            with self.subTest(missing=missing):
                incomplete = dict(approved_run)
                incomplete.pop(missing)
                codes = {item.code for item in self.validate_approved(packet, candidate, review, incomplete)}
                self.assertIn("approved_run_digest_missing", codes)

    def test_arbitrary_editorial_and_out_of_range_review_units_fail_closed(self):
        packet = self.packet()
        candidate = self.valid_segment()
        citation = self.transcript_citation(packet)
        for unit in ("editorial_notes_zh[0]", "takeaways_zh[4]", "unknown"):
            with self.subTest(unit=unit):
                review, _ = self.reviewed(packet, candidate)
                review["citation_map"].append({
                    "content_unit": unit,
                    "citations": [citation],
                })
                review["claim_attestations"].append({
                    "content_unit": unit,
                    "citations": [citation],
                    "support_confirmed": True,
                    "normalized_claim_sha256": "7" * 64,
                })
                review = rewrite_evidence.finalize_review_record(
                    packet,
                    candidate,
                    review,
                )
                approved_run = {
                    key: review[key]
                    for key in (
                        "approved_candidate_sha256",
                        "review_attestation_sha256",
                    )
                }
                codes = {
                    item.code
                    for item in self.validate_approved(
                        packet,
                        candidate,
                        review,
                        approved_run,
                    )
                }
                self.assertIn("review_unit_invalid", codes)

    def test_invalid_content_unit_never_leaks_through_findings(self):
        secret = "SECRET_CLAIM_TEXT"
        packet = self.packet()
        candidate = self.valid_segment()
        citation = self.transcript_citation(packet)
        review, _ = self.reviewed(packet, candidate)
        review["citation_map"].append({
            "content_unit": secret,
            "citations": [{**citation, "type": "invalid"}],
        })
        review["claim_attestations"].append({
            "content_unit": secret,
            "citations": [citation],
            "support_confirmed": True,
        })
        review = rewrite_evidence.finalize_review_record(packet, candidate, review)
        approved_run = {
            key: review[key]
            for key in (
                "approved_candidate_sha256",
                "review_attestation_sha256",
            )
        }
        findings = self.validate_approved(
            packet,
            candidate,
            review,
            approved_run,
        )
        self.assertIn("review_unit_invalid", {item.code for item in findings})
        serialized = json.dumps(
            [item.__dict__ for item in findings],
            ensure_ascii=False,
            sort_keys=True,
        )
        self.assertNotIn(secret, serialized)

    def test_editorial_notes_cannot_support_claims_or_assert_case_facts(self):
        packet = self.packet()
        candidate = self.valid_segment()
        editorial_citation = {"identity": "editorial:0", "type": "editorial", "source_sha256": "3" * 64}
        review, approved_run = self.reviewed(packet, candidate, citations={"summary_zh": [editorial_citation]})
        codes = {item.code for item in self.validate_approved(packet, candidate, review, approved_run)}
        self.assertIn("citation_type_invalid", codes)
        changed = self.valid_segment(editorial_notes_zh=["編輯補充：本病例確診為轉移瘤。"])
        review, approved_run = self.reviewed(packet, changed)
        codes = {item.code for item in self.validate_approved(packet, changed, review, approved_run)}
        self.assertIn("editorial_case_assertion", codes)

    def test_type_confusion_and_cf_only_reviewer_fail_closed(self):
        packet = self.packet()
        candidate = self.valid_segment()
        review, approved_run = self.reviewed(packet, candidate)
        cases = (
            ("reviewer_id", "​⁠", "reviewer_missing"),
            ("claim_attestations", "not-a-list", "missing_attestation"),
            ("citation_map", True, "missing_citation"),
        )
        for field, value, expected in cases:
            with self.subTest(field=field):
                tampered = copy.deepcopy(review)
                tampered[field] = value
                codes = {item.code for item in self.validate_approved(packet, candidate, tampered, approved_run)}
                self.assertIn(expected, codes)

    def test_findings_never_echo_claim_or_source_text(self):
        sensitive_claim = "本病例為左側小腦轉移瘤"
        packet = self.packet()
        candidate = self.valid_segment(title=sensitive_claim)
        review, approved_run = self.reviewed(packet, candidate)
        findings = self.validate_approved(packet, candidate, review, approved_run)
        self.assertTrue(findings)
        source_texts = [item["text"] for item in packet["paragraph_evidence"]]
        self.assertTrue(all(
            sensitive_claim not in finding.message
            and all(text not in finding.message for text in source_texts)
            for finding in findings
        ))

    def test_review_record_rejects_sensitive_packet_without_exposing_sensitive_value(self):
        packet = build_evidence_packet("lecture-01", 2, 10.0, 20.0, "病歷號：AB-12345678", [], self.valid_segment())
        findings = validate_review_record(packet, self.valid_segment(), {})
        self.assertIn("sensitive_evidence", {item.code for item in findings})
        self.assertTrue(all("AB-12345678" not in item.message for item in findings))


if __name__ == "__main__":
    unittest.main()
