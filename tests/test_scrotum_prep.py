"""AHK v1: scrotal US helpers in US.ahk (testis volume precompute + input-line strip). No API.

Run with AHK_V1_EXE set:  python -m pytest -q tests/test_scrotum_prep.py
"""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_usai_models import function, SOURCE


def run_ahk(body):
    exe = os.environ.get("AHK_V1_EXE")
    if not exe or not Path(exe).is_file():
        raise unittest.SkipTest("AHK_V1_EXE not set")
    source = SOURCE.read_text(encoding="utf-8-sig")
    helpers = "\n".join(function(source, n) for n in ("I2F_ScrotumPrep", "I2F_ScrotumStrip"))
    with tempfile.TemporaryDirectory(prefix="scrotum-") as td:
        out = Path(td) / "out.txt"
        code = "#NoEnv\n#NoTrayIcon\n#SingleInstance Off\n" + body.replace("OUTPUT", str(out)) + "\nExitApp\n"
        script = Path(td) / "t.ahk"
        script.write_text(code + "\n" + helpers, encoding="utf-8-sig")
        r = subprocess.run([exe, "/ErrorStdOut", str(script)], capture_output=True, timeout=20)
        if r.returncode != 0:
            raise AssertionError((r.stdout + r.stderr).decode(errors="replace"))
        return out.read_text(encoding="utf-8-sig")


def prep(text):
    esc = text.replace('"', '""').replace("\n", "`n")
    return run_ahk('FileAppend, %% I2F_ScrotumPrep("%s"), OUTPUT, UTF-8' % esc)


def strip(text):
    esc = text.replace('"', '""').replace("\n", "`n")
    return run_ahk('FileAppend, %% I2F_ScrotumStrip("%s"), OUTPUT, UTF-8' % esc)


class ScrotumPrepTests(unittest.TestCase):
    def test_adult_volumes_and_asymmetry(self):
        out = prep("Varicocele, bilateral sides.\nright 2.9x2.2x4.1 left 3.0x2.0x3.9\nRt reflux +")
        self.assertIn("Right testis: size = 2.9x2.2x4.1 cm; volume about 18.6 mL", out)
        self.assertIn("Left testis: size = 3.0x2.0x3.9 cm; volume about 16.6 mL", out)
        self.assertIn("Volume asymmetry: 11%", out)
        self.assertNotIn("<12 mL", out)
        self.assertNotIn(">20%", out)

    def test_mm_input_is_converted_to_cm(self):
        out = prep("right 29x22x41mm\nleft 30x20x39 mm")
        self.assertIn("Right testis: size = 2.9x2.2x4.1 cm; volume about 18.6 mL", out)
        self.assertIn("Left testis: size = 3.0x2.0x3.9 cm", out)

    def test_small_testis_flag_and_significant_asymmetry(self):
        out = prep("right 1.7x1.0x2.4\nleft 1.6x0.8x2.3")
        self.assertIn("Right testis: size = 1.7x1.0x2.4 cm; volume about 2.9 mL (<12 mL)", out)
        self.assertIn("Left testis: size = 1.6x0.8x2.3 cm; volume about 2.1 mL (<12 mL)", out)
        self.assertIn("Volume asymmetry: 28% (>20%)", out)

    def test_pediatric_age_skips_adult_cutoff(self):
        out = prep("right 1.7x1.0x2.4\nleft 1.6x0.8x2.3\nage 12")
        self.assertNotIn("mL (<12 mL)", out)
        self.assertIn("age 12", out)

    def test_single_side_has_no_asymmetry(self):
        out = prep("Left testis not found.\nright 4.2x3.1x2.1")
        self.assertIn("Right testis: size = 4.2x3.1x2.1 cm", out)
        self.assertNotIn("Left testis: size", out)
        self.assertNotIn("asymmetry", out)

    def test_no_sizes_returns_empty(self):
        self.assertEqual(prep("Right epididymitis\nRight testicular appendix, 0.8x0.6cm."), "")


class ScrotumStripTests(unittest.TestCase):
    def test_removes_measurement_and_reflux_lines_only(self):
        src = ("Varicocele, bilateral sides.\n"
               "right 2.9x2.2x4.1 left 3.0x2.0x3.9\n"
               "Rt reflux +\n"
               "reflux Rt + Lt +\n"
               "bil. reflux +\n"
               "age 45\n"
               "Right testicular appendix, 0.8x0.6cm.\n"
               "Left testicular cyst, 0.3cm.")
        self.assertEqual(strip(src),
                         "Varicocele, bilateral sides.\n"
                         "Right testicular appendix, 0.8x0.6cm.\n"
                         "Left testicular cyst, 0.3cm.")

    def test_separate_side_lines(self):
        self.assertEqual(strip("Hydrocele.\nright: 2.8x2.9x4.0\nleft = 2.6x3.0x3.7\nreflux -"), "Hydrocele.")


class ScrotumWiringTests(unittest.TestCase):
    """Static checks: GUI option, prompt routing, prompt file and copy-strip are wired."""

    def setUp(self):
        self.src = SOURCE.read_text(encoding="utf-8-sig")

    def test_scenario_and_prompt_routing(self):
        self.assertIn("||Scrotum", self.src)
        self.assertIn('promptFile := g_I2F_PromptDir "\\us_scrotum.md"', self.src)
        self.assertTrue((SOURCE.parent / "prompts" / "us_scrotum.md").is_file())

    def test_precompute_and_strip_are_called(self):
        self.assertIn("I2F_ScrotumPrep(I2F_Impression)", self.src)
        self.assertIn("I2F_ScrotumStrip(I2F_Impression)", self.src)


if __name__ == "__main__":
    unittest.main()
