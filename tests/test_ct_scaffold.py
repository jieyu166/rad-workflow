"""AHK v1: I2F_FixCTScaffold in US.ahk forces the CT protocol lines after the LLM reply. No API.

Run with AHK_V1_EXE set:  python -m pytest -q tests/test_ct_scaffold.py
"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_usai_models import function, SOURCE

METHOD_C = "METHOD: (1) HRCT (2) Noncontrast survey (3) contrast enhancement were performed"
METHOD_NC = "METHOD: (1) HRCT (2) Noncontrast survey were performed"
NOTE_C = "Before and after the administration of intravenous contrast there was no adverse effect."
LIMIT_NC = ("*This is a Non contrast medium injection image.\n"
            "Limited evaluation for lymphadenopathy, vascular structure, soft tissue density organs and soft tissue lesions survey;")

DRAFT_WRONG_CONTRAST = """Other details are mentioned as followings:
----------------------------------------------------------------------
CT study of the thorax was performed with a multi-slice CT scanner.
METHOD: (1) HRCT (2) Noncontrast survey (3) contrast enhancement were performed
SCAN RANGE: lower neck to adrenal gland
INDICATION: _
Before and after the administration of intravenous contrast there was no adverse effect.
Comparison with previous study: nil.

Imaging findings :
1. Lung, airway, pleura :
- A <6mm solid nodule in RUL.(Srs/Img:5/40)
9. Others               :
"""


def esc(text):
    return text.replace('"', '""').replace("\n", "`n")


def fix(text, method, note, limit):
    exe = os.environ.get("AHK_V1_EXE")
    if not exe or not Path(exe).is_file():
        raise unittest.SkipTest("AHK_V1_EXE not set")
    helper = function(SOURCE.read_text(encoding="utf-8-sig"), "I2F_FixCTScaffold")
    with tempfile.TemporaryDirectory(prefix="ctscaffold-") as td:
        out = Path(td) / "out.txt"
        body = 'FileAppend, %% I2F_FixCTScaffold("%s", "%s", "%s", "%s"), %s, UTF-8' % (
            esc(text), esc(method), esc(note), esc(limit), out)
        script = Path(td) / "t.ahk"
        script.write_text("#NoEnv\n#NoTrayIcon\n#SingleInstance Off\n" + body + "\nExitApp\n\n" + helper,
                          encoding="utf-8-sig")
        r = subprocess.run([exe, "/ErrorStdOut", str(script)], capture_output=True, timeout=20)
        if r.returncode != 0:
            raise AssertionError((r.stdout + r.stderr).decode(errors="replace"))
        return out.read_text(encoding="utf-8-sig")


class CTScaffoldTests(unittest.TestCase):
    def test_noncontrast_overrides_wrong_contrast_method(self):
        out = fix(DRAFT_WRONG_CONTRAST, METHOD_NC, "", LIMIT_NC)
        self.assertIn(METHOD_NC + "\n", out)
        self.assertNotIn("contrast enhancement were performed", out)
        self.assertNotIn("administration of intravenous contrast", out)

    def test_noncontrast_appends_limitation_note_at_end_once(self):
        out = fix(DRAFT_WRONG_CONTRAST + "\n" + LIMIT_NC + "\n\n", METHOD_NC, "", LIMIT_NC)
        self.assertTrue(out.endswith("9. Others               :\n\n" + LIMIT_NC), out[-300:])
        self.assertEqual(out.count("Non contrast medium injection image"), 1)
        self.assertEqual(out.count("Limited evaluation for lymphadenopathy"), 1)

    def test_contrast_removes_stray_limitation_note(self):
        draft = DRAFT_WRONG_CONTRAST.replace(METHOD_C, METHOD_NC) + "\n- This is a Non contrast medium injection image.\nLimited evalution for lymphadenopathy, vascular structure\n"
        out = fix(draft, METHOD_C, NOTE_C, "")
        self.assertIn(METHOD_C + "\n", out)
        self.assertNotIn("Non contrast medium injection", out)
        self.assertNotIn("Limited evalution", out)
        self.assertEqual(out.count(NOTE_C), 1)

    def test_contrast_note_inserted_after_indication_when_missing(self):
        draft = DRAFT_WRONG_CONTRAST.replace(NOTE_C + "\n", "")
        out = fix(draft, METHOD_C, NOTE_C, "")
        self.assertIn("INDICATION: _\n" + NOTE_C + "\nComparison with previous study: nil.", out)

    def test_method_inserted_after_scaffold_line_when_missing(self):
        draft = DRAFT_WRONG_CONTRAST.replace(METHOD_C + "\n", "")
        out = fix(draft, METHOD_NC, "", LIMIT_NC)
        self.assertIn("multi-slice CT scanner.\n" + METHOD_NC + "\nSCAN RANGE:", out)

    def test_duplicate_method_lines_collapse_to_one(self):
        draft = DRAFT_WRONG_CONTRAST.replace(METHOD_C, METHOD_C + "\n" + METHOD_NC)
        out = fix(draft, METHOD_NC, "", LIMIT_NC)
        self.assertEqual(out.count("METHOD:"), 1)

    def test_findings_untouched(self):
        out = fix(DRAFT_WRONG_CONTRAST, METHOD_NC, "", LIMIT_NC)
        self.assertIn("1. Lung, airway, pleura :\n- A <6mm solid nodule in RUL.(Srs/Img:5/40)\n9. Others", out)
        self.assertIn("INDICATION: _\nComparison with previous study: nil.", out)


if __name__ == "__main__":
    unittest.main()
