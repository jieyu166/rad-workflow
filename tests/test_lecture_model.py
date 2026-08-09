import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "lecture-to-notes" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lecture_model import (
    assert_times_unchanged,
    load_lecture,
    normalize_lecture,
    time_signature,
    validate_lecture_schema,
    write_json_atomic,
)


class LectureModelTests(unittest.TestCase):
    def valid_segment(self, **overrides):
        segment = {
            "index": 1,
            "start_sec": 0.0,
            "end_sec": 5.0,
            "title": "Focused title",
            "summary_zh": "Valid summary",
            "takeaways_zh": ["one", "two", "three", "four"],
            "editorial_notes_zh": [],
            "frames": [{"time": 1.0, "ocr": "Slide text", "path": "frames/f001.jpg"}],
        }
        segment.update(overrides)
        return segment

    def test_normalize_migrates_aliases_bullets_frames_and_segment_ocr(self):
        source = {
            "title": "Synthetic lecture",
            "segments": [{
                "index": 3,
                "start": 10.0,
                "end": 20.0,
                "title": "Focused title",
                "summary_zh": "Organized content",
                "bullets_zh": ["one", "two", "three", "four"],
                "frames": ["frames/f001.jpg"],
                "frame_ocr": [{"frame": "frames/f001.jpg", "text": "Slide text"}],
            }],
        }

        result = normalize_lecture(source)
        segment = result["segments"][0]

        self.assertEqual((segment["start_sec"], segment["end_sec"]), (10.0, 20.0))
        self.assertEqual(segment["index"], 3)
        self.assertNotIn("start", segment)
        self.assertNotIn("end", segment)
        self.assertEqual(segment["takeaways_zh"], ["one", "two", "three", "four"])
        self.assertEqual(segment["editorial_notes_zh"], [])
        self.assertEqual(segment["frames"], [{
            "time": 0.0,
            "ocr": "Slide text",
            "path": "frames/f001.jpg",
        }])
        self.assertNotIn("frame_ocr", segment)
        self.assertNotIn("bullets_zh", segment)
        self.assertEqual(source["segments"][0]["start"], 10.0)

    def test_normalize_uses_top_level_ocr_map_and_preserves_malformed_values(self):
        source = {
            "frame_ocr": {"frames/legacy_12-5.jpg": "Top OCR"},
            "segments": [{
                "index": 1,
                "start_sec": 10.0,
                "end_sec": 20.0,
                "title": "Focused title",
                "summary_zh": "Organized content",
                "takeaways_zh": ["one", "two", "three", "four"],
                "editorial_notes_zh": [],
                "frames": [
                    "frames/legacy_12-5.jpg",
                    {"time": "bad", "ocr": None, "path": "frames/bad.jpg"},
                ],
            }],
        }

        result = normalize_lecture(source)

        self.assertNotIn("frame_ocr", result)
        self.assertEqual(result["segments"][0]["frames"], [
            {"time": 12.5, "ocr": "Top OCR", "path": "frames/legacy_12-5.jpg"},
            {"time": "bad", "ocr": None, "path": "frames/bad.jpg"},
        ])

    def test_schema_accepts_existing_safe_relative_frame(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            frame = root / "frames" / "f001.jpg"
            frame.parent.mkdir()
            frame.write_bytes(b"image")

            findings = validate_lecture_schema(
                {"segments": [self.valid_segment()]},
                root,
            )

        self.assertEqual(findings, [])

    def test_schema_rejects_zero_frames_and_wrong_takeaway_count(self):
        with tempfile.TemporaryDirectory() as td:
            data = {"segments": [self.valid_segment(
                takeaways_zh=["one", "two", "three"],
                frames=[],
            )]}
            findings = validate_lecture_schema(data, Path(td))

        codes = {item.code for item in findings}
        self.assertTrue({"takeaway_count", "frame_count"}.issubset(codes))

    def test_schema_rejects_absolute_parent_and_unc_paths_without_accessing_them(self):
        unsafe_paths = [
            "/absolute/a.jpg",
            "C:/absolute/b.jpg",
            "C:\\absolute\\c.jpg",
            "\\\\server\\share\\d.jpg",
            "//server/share/e.jpg",
            "../outside/f.jpg",
            "frames/../../outside/g.jpg",
        ]
        frames = [
            {"time": 1.0, "ocr": "text", "path": value}
            for value in unsafe_paths
        ]
        with tempfile.TemporaryDirectory() as td:
            findings = validate_lecture_schema(
                {"segments": [self.valid_segment(frames=frames)]},
                Path(td),
            )

        rejected = {item.path for item in findings if item.code == "frame_path"}
        self.assertEqual(rejected, set(unsafe_paths))

    def test_schema_rejects_nul_and_non_string_paths(self):
        frames = [
            {"time": 1.0, "ocr": "text", "path": "frames/\x00bad.jpg"},
            {"time": 1.0, "ocr": "text", "path": Path("frames/path-object.jpg")},
        ]
        with tempfile.TemporaryDirectory() as td:
            findings = validate_lecture_schema(
                {"segments": [self.valid_segment(frames=frames)]},
                Path(td),
            )

        self.assertEqual(
            {item.path for item in findings if item.code == "frame_path"},
            {"frames/\x00bad.jpg", "frames\\path-object.jpg"},
        )

    def test_malformed_nonfinite_and_out_of_range_frame_times_are_findings(self):
        bad_times = ["not-a-time", None, -1.0, float("nan"), float("inf"), float("-inf"), 9.0]
        frames = [
            {"time": value, "ocr": "text", "path": f"frames/f{index}.jpg"}
            for index, value in enumerate(bad_times)
        ]
        frames[1]["ocr"] = None
        with tempfile.TemporaryDirectory() as td:
            findings = validate_lecture_schema(
                {"segments": [self.valid_segment(frames=frames)]},
                Path(td),
            )

        expected_paths = {f"frames/f{index}.jpg" for index in range(len(bad_times))}
        self.assertEqual(
            {item.path for item in findings if item.code == "frame_time"},
            expected_paths,
        )
        self.assertEqual(
            {item.path for item in findings if item.code == "frame_missing"},
            expected_paths,
        )
        self.assertEqual(
            [item.path for item in findings if item.code == "frame_ocr_type"],
            ["frames/f1.jpg"],
        )

    def test_malformed_frame_objects_are_structured_and_validation_continues(self):
        frames = [None, "frames/not-canonical.jpg", 42]
        with tempfile.TemporaryDirectory() as td:
            findings = validate_lecture_schema(
                {"segments": [self.valid_segment(frames=frames)]},
                Path(td),
            )

        self.assertEqual(
            [item.code for item in findings if item.code == "frame_type"],
            ["frame_type", "frame_type", "frame_type"],
        )

    def test_invalid_segment_time_is_structured_instead_of_crashing(self):
        segments = [
            self.valid_segment(start_sec="bad"),
            self.valid_segment(start_sec=float("nan")),
            self.valid_segment(end_sec=float("inf")),
        ]
        with tempfile.TemporaryDirectory() as td:
            findings = validate_lecture_schema({"segments": segments}, Path(td))

        self.assertEqual(
            [item.segment_index for item in findings if item.code == "time_range"],
            [0, 1, 2],
        )

    def test_assert_times_unchanged_rejects_count_time_and_segment_index_changes(self):
        before = {"segments": [
            {"index": 1, "start_sec": 0.0, "end_sec": 5.0},
            {"index": 2, "start_sec": 5.0, "end_sec": 10.0},
            {"index": 3, "start_sec": 10.0, "end_sec": 120.0},
        ]}

        with self.assertRaisesRegex(ValueError, "segment count changed"):
            assert_times_unchanged(before, {"segments": before["segments"][:-1]})

        changed_time = json.loads(json.dumps(before))
        changed_time["segments"][2]["end_sec"] = 120.1
        with self.assertRaisesRegex(ValueError, "segment 3 time changed"):
            assert_times_unchanged(before, changed_time)

        changed_index = json.loads(json.dumps(before))
        changed_index["segments"][1]["index"] = 7
        with self.assertRaisesRegex(ValueError, "segment 2 index changed"):
            assert_times_unchanged(before, changed_index)

        self.assertEqual(time_signature(before), ((0.0, 5.0), (5.0, 10.0), (10.0, 120.0)))

    def test_atomic_writer_writes_utf8_json_and_leaves_no_temp(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "lecture.json"
            write_json_atomic(target, {"title": "臺灣", "segments": []})

            raw = target.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
            self.assertIn("臺灣".encode("utf-8"), raw)
            self.assertEqual(json.loads(raw.decode("utf-8"))["segments"], [])
            self.assertEqual(list(Path(td).glob("*.tmp")), [])

    def test_atomic_writer_failure_keeps_target_and_removes_temp(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "lecture.json"
            target.write_text('{"old": true}\n', encoding="utf-8")

            with patch("lecture_model.os.replace", side_effect=OSError("replace failed")):
                with self.assertRaisesRegex(OSError, "replace failed"):
                    write_json_atomic(target, {"new": True})

            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"old": True})
            self.assertEqual(list(Path(td).glob("*.tmp")), [])

    def test_load_lecture_accepts_utf8_bom_and_normalizes(self):
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "lecture.json"
            source.write_text(
                json.dumps({"segments": [{
                    "index": 1,
                    "start": 0,
                    "end": 1,
                    "title": "Title",
                    "summary_zh": "Summary",
                    "bullets_zh": ["a", "b", "c", "d"],
                    "frames": [],
                }]}, ensure_ascii=False),
                encoding="utf-8-sig",
            )

            loaded = load_lecture(source)

        self.assertEqual((loaded["segments"][0]["start_sec"], loaded["segments"][0]["end_sec"]), (0.0, 1.0))


if __name__ == "__main__":
    unittest.main()
