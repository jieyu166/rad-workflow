"""AHK v1: Claude request/response helpers used by AI_FindOpen (US.ahk). No API.

Run with AHK_V1_EXE set:  python -m pytest -q tests/test_i2f_claude.py
"""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_usai_models import function, SOURCE

HELPERS = ("I2F_BuildClaudeJSON", "I2F_ExtractClaudeText", "I2F_StripTags", "ParseTokenUsage", "JEscape",
           "JsonUnescape", "DecodeUnicodeEscapes", "HexToInt", "UnicodeChar")


def esc(text):
    return text.replace('"', '""').replace("\n", "`n")


def run_ahk(body):
    exe = os.environ.get("AHK_V1_EXE")
    if not exe or not Path(exe).is_file():
        raise unittest.SkipTest("AHK_V1_EXE not set")
    source = SOURCE.read_text(encoding="utf-8-sig")
    helpers = "\n".join(function(source, n) for n in HELPERS)
    with tempfile.TemporaryDirectory(prefix="i2fclaude-") as td:
        out = Path(td) / "out.txt"
        code = ("#NoEnv\n#NoTrayIcon\n#SingleInstance Off\nglobal g_I2F_LastTokens := {}\n"
                + body.replace("OUTPUT", str(out)) + "\nExitApp\n")
        script = Path(td) / "t.ahk"
        script.write_text(code + "\n" + helpers, encoding="utf-8-sig")
        r = subprocess.run([exe, "/ErrorStdOut", str(script)], capture_output=True, timeout=20)
        if r.returncode != 0:
            raise AssertionError((r.stdout + r.stderr).decode(errors="replace"))
        return out.read_text(encoding="utf-8")


def fileappend(expr):
    return 'f := FileOpen("OUTPUT", "w", "UTF-8-RAW"), f.Write(%s), f.Close()' % expr


class BuildRequestTests(unittest.TestCase):
    def test_body_is_valid_json_with_expected_settings(self):
        sys_prompt = 'You are a "radiology" assistant.\nRule \\ one.'
        user = "Impression:\n左腎結石 0.7cm (Srs/Img:1/3)"
        out = run_ahk(fileappend('I2F_BuildClaudeJSON("claude-sonnet-5-5", "%s", "%s")' % (esc(sys_prompt), esc(user))))
        body = json.loads(out)
        self.assertEqual(body["model"], "claude-sonnet-5-5")
        self.assertEqual(body["max_tokens"], 8000)
        self.assertEqual(body["system"], [{"type": "text", "text": sys_prompt, "cache_control": {"type": "ephemeral"}}])
        self.assertEqual(body["messages"], [{"role": "user", "content": user}])
        self.assertEqual(body["output_config"], {"effort": "low"})
        self.assertEqual(body["thinking"], {"type": "between_tools"})
        self.assertEqual(body["fallbacks"], "default")
        self.assertNotIn("temperature", body)


class ExtractTextTests(unittest.TestCase):
    def extract(self, resp_obj):
        resp = json.dumps(resp_obj, ensure_ascii=True)
        return run_ahk(fileappend('I2F_ExtractClaudeText("%s")' % esc(resp)))

    def test_joins_text_blocks_and_unescapes(self):
        text = '<<FINDINGS>>\nUrotract sonography:\n\nOthers:\n- Left inguinal hernia.(Srs/Img:1/3)\n- "quoted" \\ 中文'
        out = self.extract({"type": "message", "stop_reason": "end_turn", "content": [
            {"type": "thinking", "thinking": "", "signature": "x"},
            {"type": "text", "text": text[:20]}, {"type": "text", "text": text[20:]}],
            "usage": {"input_tokens": 10, "output_tokens": 5}})
        self.assertEqual(out, text)

    def test_no_text_block_returns_empty(self):
        self.assertEqual(self.extract({"type": "message", "stop_reason": "refusal", "content": []}), "")


class StripTagsTests(unittest.TestCase):
    def strip(self, text):
        return run_ahk(fileappend('I2F_StripTags("%s")' % esc(text)))

    def test_trailing_end_tag_removed(self):
        self.assertEqual(self.strip("Others:\n- Left inguinal hernia.\n<<END>>"), "Others:\n- Left inguinal hernia.")

    def test_inline_brackets_kept(self):
        text = "Liver:\n- A <6mm nodule <<not a tag line\n- Ratio <<1"
        self.assertEqual(self.strip(text), text)

    def test_stray_findings_tag_mid_text_removed(self):
        self.assertEqual(self.strip("<<FINDINGS>>\nLiver:\n- Normal\n\n<<END>>\n"), "Liver:\n- Normal")


class TokenUsageTests(unittest.TestCase):
    def tokens(self, resp_obj):
        resp = json.dumps(resp_obj)
        return run_ahk('ParseTokenUsage("%s")\n' % esc(resp)
                       + fileappend('g_I2F_LastTokens.prompt "/" g_I2F_LastTokens.completion "/" g_I2F_LastTokens.total'))

    def test_claude_usage_includes_cache(self):
        out = self.tokens({"usage": {"input_tokens": 12, "cache_read_input_tokens": 3800,
                                     "cache_creation_input_tokens": 0, "output_tokens": 310}})
        self.assertEqual(out, "3812/310/4122")

    def test_openai_usage_unchanged(self):
        out = self.tokens({"usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120}})
        self.assertEqual(out, "100/20/120")


if __name__ == "__main__":
    unittest.main()
