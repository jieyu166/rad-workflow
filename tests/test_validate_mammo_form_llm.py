"""Unit tests for radtracker/validate_mammo_form_llm.py (no network)."""
import contextlib
import csv
import datetime as dt
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "radtracker"))
import validate_mammo_form_llm as v  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "mammo_form"
HTML = ROOT / "tool" / "mammo-suspicious-form.html"


def claude_message(obj_or_text, stop_reason="end_turn"):
    text = obj_or_text if isinstance(obj_or_text, str) else json.dumps(obj_or_text)
    content = [] if stop_reason == "refusal" else [{"type": "text", "text": text}]
    return json.dumps({"type": "message", "stop_reason": stop_reason, "content": content})


class ExtractionTests(unittest.TestCase):
    def test_prompt_and_model_from_real_html(self):
        html = HTML.read_text(encoding="utf-8")
        prompt, model = v.extract_prompt_and_model(html)
        self.assertTrue(prompt.startswith("You extract the SUSPICIOUS findings"))
        self.assertTrue(prompt.rstrip().endswith('otherwise null.'))
        self.assertIn('"multiple_bilateral"', prompt)
        self.assertNotIn("MAMMO-PROMPT", prompt)
        self.assertNotIn("`", prompt)
        expected_model = html.split("const MODEL_ID = '", 1)[1].split("'", 1)[0]
        self.assertEqual(model, expected_model)
        self.assertIn(model, v.CLAUDE_MODEL_SETTINGS)

    def test_model_settings_mirror_page(self):
        html = HTML.read_text(encoding="utf-8")
        for model, cfg in v.CLAUDE_MODEL_SETTINGS.items():
            with self.subTest(model=model):
                thinking = "null" if cfg["thinking"] is None else "{ type: '%s' }" % cfg["thinking"]["type"]
                line = "'%s': { thinking: %s, fallbacks: %s }" % (model, thinking, str(cfg["fallbacks"]).lower())
                self.assertIn(line, html)
        self.assertIn("const ANTHROPIC_VERSION = '%s';" % v.ANTHROPIC_VERSION, html)
        self.assertIn("const FALLBACK_BETA = '%s';" % v.FALLBACK_BETA, html)

    def test_missing_markers_raise(self):
        with self.assertRaises(v.ConfigError):
            v.extract_prompt_and_model("<script>const MODEL_ID = 'x';</script>")

    def test_template_literal_unescape(self):
        html = ("/* MAMMO-PROMPT-START */\nconst MAMMO_SYSTEM_PROMPT = `a \\` b \\\\ c`;\n"
                "/* MAMMO-PROMPT-END */\nconst MODEL_ID = 'm1';")
        prompt, model = v.extract_prompt_and_model(html)
        self.assertEqual(prompt, "a ` b \\ c")
        self.assertEqual(model, "m1")


class CategoryRegexTests(unittest.TestCase):
    def test_table(self):
        cases = [
            ("BI-RADS assessment:\nCategory 4C (Suspicious Abnormality)", (4, "c")),
            ("(BI-RADS category 0, need additional imaging evaluation)", (0, None)),
            ("BIRADS density C - heterogeneously dense breasts", (None, None)),
            ("BI-RADS Category 4", (4, None)),
            ("BI-RADS category: 5, highly suggestive", (5, None)),
            ("BI-RADS category 2, benign", (2, None)),
            ("Category 3b", (3, None)),  # letter only kept for category 4
            ("Category 4Ab", (None, None)),  # letter followed by letter: no match
            ("no assessment line", (None, None)),
            ("", (None, None)),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(v.detect_category(text), expected)

    def test_first_match_wins(self):
        self.assertEqual(v.detect_category("BI-RADS category 0 ... prior category 4"), (0, None))

    def test_fixture_categories(self):
        for name in ("cat0_benign_calc", "cat0_bilateral", "cat0_unilateral", "cat2", "cat4", "cat5"):
            text = (FIXTURES / f"{name}.txt").read_text(encoding="utf-8")
            exp = json.loads((FIXTURES / f"{name}.expected.json").read_text(encoding="utf-8"))
            with self.subTest(name=name):
                self.assertEqual(v.detect_category(text)[0], exp["category"])


class SchemaTests(unittest.TestCase):
    def test_valid_fixture_is_strict_ok(self):
        exp = json.loads((FIXTURES / "cat0_bilateral.expected.json").read_text(encoding="utf-8"))
        out, dropped = v.validate_parsed(exp)
        self.assertEqual(dropped, 0)
        self.assertEqual([l["type"] for l in out["lesions"]], ["mass", "calcification"])

    def test_unknown_enums_dropped(self):
        obj = {"cat4Sub": "d", "lesions": [{
            "type": "nodule", "side": "R", "location": ["UOQ", "center", "UOQ"],
            "oneView": ["upper", "middle"], "size": "5", "shape": "oval", "margin": "fuzzy",
            "density": None, "otherText": "  ", "extraKey": 1}]}
        out, dropped = v.validate_parsed(obj)
        les = out["lesions"][0]
        self.assertIsNone(out["cat4Sub"])
        self.assertIsNone(les["type"])
        self.assertEqual(les["side"], "R")
        self.assertEqual(les["location"], ["UOQ"])
        self.assertEqual(les["oneView"], ["upper"])
        self.assertIsNone(les["size"])
        self.assertEqual(les["shape"], "oval")
        self.assertIsNone(les["margin"])
        self.assertIsNone(les["otherText"])
        self.assertNotIn("extraKey", les)
        # cat4Sub, type, center, middle, size, margin
        self.assertEqual(dropped, 6)

    def test_structural_failures(self):
        for obj in (None, [], "x", {"lesions": "no"}, {}, {"lesions": [1]}, {"lesions": [[]]}):
            with self.subTest(obj=obj):
                self.assertEqual(v.validate_parsed(obj), (None, 0))

    def test_empty_lesions_ok(self):
        self.assertEqual(v.validate_parsed({"cat4Sub": None, "lesions": []}),
                         ({"cat4Sub": None, "lesions": []}, 0))


class SideHeuristicTests(unittest.TestCase):
    def test_header_line_ignored(self):
        text = "Screening mammography of bilateral breast with CC and MLO views:\nFindings:\nMass in right UOQ."
        self.assertEqual(v.report_sides(text), {"R"})

    def test_bilateral_words(self):
        self.assertEqual(v.report_sides("Findings:\nBenign calcification of both breasts."), {"R", "L"})
        self.assertEqual(v.report_sides("Findings:\nLt. axilla and Rt. breast"), {"R", "L"})

    def test_consistency(self):
        text = (FIXTURES / "cat0_unilateral.txt").read_text(encoding="utf-8")
        self.assertTrue(v.side_consistency(text, [{"side": "R"}]))
        self.assertFalse(v.side_consistency(text, [{"side": "L"}]))
        self.assertFalse(v.side_consistency(text, [{"side": "multiple_bilateral"}]))
        self.assertIsNone(v.side_consistency(text, []))
        self.assertIsNone(v.side_consistency(text, [{"side": "multiple_unilateral"}]))
        self.assertIsNone(v.side_consistency("Findings: mass.", [{"side": "R"}]))

    def test_benign_bilateral_still_consistent(self):
        text = (FIXTURES / "cat0_benign_calc.txt").read_text(encoding="utf-8")
        self.assertTrue(v.side_consistency(text, [{"side": "R"}]))


class EnvTests(unittest.TestCase):
    def test_parse_months(self):
        self.assertEqual(v.parse_months("202602-202606"),
                         ["202602", "202603", "202604", "202605", "202606"])
        self.assertEqual(v.parse_months("202611-202702"), ["202611", "202612", "202701", "202702"])
        self.assertEqual(v.parse_months("202602,202604"), ["202602", "202604"])
        for bad in ("2026-02", "202606-202602", "202613"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                v.parse_months(bad)

    def test_key_from_env_file(self):
        with tempfile.TemporaryDirectory() as td:
            Path(td, ".env").write_text("# c\nOTHER=1\nexport ANTHROPIC_API_KEY='abc123'\n", encoding="utf-8")
            self.assertEqual(v.load_api_key({}, Path(td)), "abc123")
            self.assertEqual(v.load_api_key({"ANTHROPIC_API_KEY": "envkey"}, Path(td)), "envkey")

    def test_key_from_ahk_ini_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            ini = Path(td, "ahk-scripts", "radiologist_settings.ini")
            ini.parent.mkdir()
            ini.write_text("[AI]\nAPIKey=gpt\nAPIKey2=gem\nAPIKey3=claudekey\n", encoding="utf-16")
            self.assertEqual(v.load_api_key({}, Path(td)), "claudekey")
            Path(td, ".env").write_text("OTHER=1\n", encoding="utf-8")
            self.assertEqual(v.load_api_key({}, Path(td)), "claudekey")
            self.assertEqual(v.load_api_key({"ANTHROPIC_API_KEY": "envkey"}, Path(td)), "envkey")

    def test_missing_key_exits_2(self):
        with tempfile.TemporaryDirectory() as td:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = v.main(["--months", "202602"], repo_root=Path(td), env={},
                            http_post=lambda *a: self.fail("no request expected"))
            self.assertEqual(rc, 2)
            self.assertIn("ANTHROPIC_API_KEY", buf.getvalue())


class RetryTests(unittest.TestCase):
    def test_retry_then_success(self):
        calls, sleeps = [], []
        responses = [(429, "rate"), (503, "busy"), (200, claude_message({"lesions": []}))]

        def post(url, headers, body, timeout):
            calls.append(1)
            return responses[len(calls) - 1]

        text, err = v.call_claude("p", "m", "k", "r", post, sleeps.append)
        self.assertIsNone(err)
        self.assertEqual(json.loads(text), {"lesions": []})
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleeps, [2.0, 4.0])

    def test_gives_up_after_three(self):
        calls = []

        def post(*a):
            calls.append(1)
            return 500, "err"

        self.assertEqual(v.call_claude("p", "m", "k", "r", post, lambda s: None), (None, "http_500"))
        self.assertEqual(len(calls), 3)

    def test_no_retry_on_400(self):
        calls = []

        def post(*a):
            calls.append(1)
            return 400, "bad"

        self.assertEqual(v.call_claude("p", "m", "k", "r", post, lambda s: None), (None, "http_400"))
        self.assertEqual(len(calls), 1)

    def test_refusal_is_an_error(self):
        self.assertEqual(v.call_claude("p", "claude-haiku-5-5", "k", "r",
                                       lambda *a: (200, claude_message("", "refusal")), lambda s: None),
                         (None, "refusal"))

    def test_json_fence_stripped(self):
        text, err = v.call_claude("p", "claude-haiku-5-5", "k", "r",
                                  lambda *a: (200, claude_message('```json\n{"lesions": []}\n```')), lambda s: None)
        self.assertIsNone(err)
        self.assertEqual(json.loads(text), {"lesions": []})

    def test_request_settings_per_model(self):
        h, b = v.build_request("P", " R ", "claude-haiku-5-5", "K")
        self.assertEqual(b["thinking"], {"type": "disabled"})
        self.assertNotIn("anthropic-beta", h)
        self.assertNotIn("fallbacks", b)
        h, b = v.build_request("P", "R", "claude-sonnet-5-5", "K")
        self.assertEqual(b["thinking"], {"type": "between_tools"})
        self.assertEqual((h["anthropic-beta"], b["fallbacks"]), (v.FALLBACK_BETA, "default"))
        h, b = v.build_request("P", "R", "claude-opus-5-5", "K")
        self.assertNotIn("thinking", b)
        self.assertEqual(b["fallbacks"], "default")
        for body in (b,):
            self.assertNotIn("temperature", body)

    def test_network_error_retried(self):
        def post(*a):
            raise OSError("down")

        self.assertEqual(v.call_claude("p", "m", "k", "r", post, lambda s: None)[1], "network_OSError")


class EndToEndTests(unittest.TestCase):
    FAKE_CHART = "ZZTESTCHART9"
    FAKE_CASE = "ZZTESTCASE77"
    NAMES = ["cat0_unilateral", "cat2", "cat0_bilateral", "cat4", "cat0_benign_calc", "cat5"]

    def test_full_run_with_mock_http(self):
        html = HTML.read_text(encoding="utf-8")
        prompt, model = v.extract_prompt_and_model(html)
        texts = {n: (FIXTURES / f"{n}.txt").read_text(encoding="utf-8") for n in self.NAMES}
        expected = {n: json.loads((FIXTURES / f"{n}.expected.json").read_text(encoding="utf-8"))
                    for n in self.NAMES}
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "tool").mkdir()
            shutil.copy(HTML, root / "tool" / HTML.name)
            out = root / "radtracker" / "output"
            out.mkdir(parents=True)
            reports = [{"case_id": self.FAKE_CASE, "chart_no": self.FAKE_CHART, "report_date": "",
                        "status": "ok", "birads_category": expected[n]["category"],
                        "report_text": texts[n], "error": None} for n in self.NAMES]
            (out / "mammo_202602_reports.json").write_text(
                json.dumps({"month": "2026-02", "reports": reports}), encoding="utf-8")

            requests = []

            def post(url, headers, body, timeout):
                req = json.loads(body.decode("utf-8"))
                requests.append((url, headers, req))
                user = req["messages"][0]["content"]
                for n in self.NAMES:
                    if texts[n].strip() in user:
                        if n == "cat5":
                            return 200, claude_message("not json at all")
                        payload = {k: expected[n][k] for k in ("cat4Sub", "lesions")}
                        return 200, claude_message(payload)
                return 500, "unexpected"

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = v.main(["--months", "202602", "--sleep", "0"], repo_root=root,
                            env={"ANTHROPIC_API_KEY": "SECRET-KEY-XYZ"}, http_post=post,
                            sleep=lambda s: None, today=dt.date(2026, 10, 6))
            console = buf.getvalue()
            self.assertEqual(rc, 0, console)

            # Request shape mirrors the page.
            self.assertEqual(len(requests), 5)  # cat2 excluded
            url, headers, req = requests[0]
            self.assertEqual(url, "https://api.anthropic.com/v1/messages")
            self.assertEqual(headers["x-api-key"], "SECRET-KEY-XYZ")
            self.assertEqual(headers["anthropic-version"], "2026-10-21")
            self.assertEqual(req["model"], model)
            self.assertEqual(req["system"], prompt)
            self.assertEqual(req["output_config"], {"effort": "low"})
            self.assertNotIn("temperature", req)
            self.assertTrue(req["messages"][0]["content"].startswith("MAMMOGRAPHY REPORT:\n"))

            # Console: ASCII only, no key / PII / report text.
            console.encode("ascii")
            console.encode("cp950")
            self.assertIn("[1/5] ok lesions=1", console)
            self.assertIn("[5/5] FAIL json_error", console)
            self.assertIn("JSON-valid rate         : 4/5 (80.0%)", console)
            self.assertIn("Schema-valid rate       : 4/5 (80.0%)", console)
            self.assertIn("Category 0 with >=1 lesion: 3/3 (100.0%)", console)
            self.assertIn("Side consistency rate   : 4/4 (100.0%)", console)
            for secret in ("SECRET-KEY-XYZ", self.FAKE_CHART, self.FAKE_CASE, "Screening mammography"):
                self.assertNotIn(secret, console)

            csv_path = out / "mammo_form_llm_validation_20261006.csv"
            raw = csv_path.read_bytes()
            self.assertTrue(raw.startswith(b"\xef\xbb\xbf"))
            content = raw.decode("utf-8-sig")
            for secret in (self.FAKE_CHART, self.FAKE_CASE, "SECRET-KEY-XYZ"):
                self.assertNotIn(secret, content)
            for n in self.NAMES:
                for line in texts[n].splitlines():
                    if len(line.strip()) >= 20:
                        self.assertNotIn(line.strip(), content)
            rows = list(csv.DictReader(io.StringIO(content)))
            self.assertEqual(list(rows[0].keys()), v.CSV_FIELDS)
            self.assertEqual([r["row_index"] for r in rows], ["0", "2", "3", "4", "5"])
            bil = rows[1]
            self.assertEqual((bil["regex_category"], bil["json_ok"], bil["schema_ok"], bil["n_lesions"]),
                             ("0", "1", "1", "2"))
            self.assertEqual(bil["types"], "mass|calcification")
            self.assertEqual(bil["sides"], "R|L")
            self.assertEqual(bil["side_consistent"], "1")
            self.assertEqual(rows[2]["regex_category"], "4")
            self.assertEqual(rows[4]["error"], "json_error")

    def test_model_override(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "tool").mkdir()
            shutil.copy(HTML, root / "tool" / HTML.name)
            out = root / "radtracker" / "output"
            out.mkdir(parents=True)
            text = (FIXTURES / "cat0_unilateral.txt").read_text(encoding="utf-8")
            (out / "mammo_202603_reports.json").write_text(json.dumps({"reports": [{"report_text": text}]}), encoding="utf-8")
            seen = []

            def post(url, headers, body, timeout):
                seen.append(json.loads(body.decode("utf-8"))["model"])
                return 200, claude_message({"cat4Sub": None, "lesions": []})

            with contextlib.redirect_stdout(io.StringIO()):
                rc = v.main(["--months", "202603", "--sleep", "0", "--model", "claude-opus-5-5"], repo_root=root,
                            env={"ANTHROPIC_API_KEY": "k"}, http_post=post, sleep=lambda s: None,
                            today=dt.date(2026, 10, 6))
                bad = v.main(["--months", "202603", "--model", "gpt-x"], repo_root=root,
                             env={"ANTHROPIC_API_KEY": "k"}, http_post=post)
            self.assertEqual((rc, seen), (0, ["claude-opus-5-5"]))
            self.assertEqual(bad, 1)

    def test_limit(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "tool").mkdir()
            shutil.copy(HTML, root / "tool" / HTML.name)
            out = root / "radtracker" / "output"
            out.mkdir(parents=True)
            text = (FIXTURES / "cat0_unilateral.txt").read_text(encoding="utf-8")
            (out / "mammo_202603_reports.json").write_text(
                json.dumps({"reports": [{"report_text": text}] * 4}), encoding="utf-8")
            calls = []

            def post(*a):
                calls.append(1)
                return 200, claude_message({"cat4Sub": None, "lesions": []})

            with contextlib.redirect_stdout(io.StringIO()):
                rc = v.main(["--months", "202602-202603", "--limit", "2", "--sleep", "0"], repo_root=root,
                            env={"ANTHROPIC_API_KEY": "k"}, http_post=post, sleep=lambda s: None,
                            today=dt.date(2026, 10, 6))
            self.assertEqual(rc, 0)
            self.assertEqual(len(calls), 2)


if __name__ == "__main__":
    unittest.main()
