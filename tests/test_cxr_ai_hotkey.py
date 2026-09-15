from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
TEST_AHK = ROOT / "ahk-scripts" / "test.ahk"


def see_cxr_ai_block() -> str:
    source = TEST_AHK.read_text(encoding="utf-8-sig")
    start = source.index("SeeCXRAI:")
    end = source.index("; --- 複製舊報告日期 ---", start)
    return source[start:end]


class SeeCxrAiHotkeyTests(unittest.TestCase):
    def assert_in_order(self, text: str, *needles: str) -> None:
        for needle in needles:
            self.assertIn(needle, text)
        positions = [text.index(needle) for needle in needles]
        self.assertEqual(positions, sorted(positions))

    def test_captures_dicom_before_copying_lunit_findings(self) -> None:
        block = see_cxr_ai_block()

        self.assert_in_order(
            block,
            "Send g",
            "Send 2",
            "ClipboardBackup := ClipboardAll",
            'Clipboard := ""',
            "gosub CallDICOMWinL",
            "aiDicomText := Clipboard",
            "aiSummary := ExtractLunitSummary(aiDicomText)",
            "Clipboard := aiSummary",
            "ClipWait, 1",
            "Lunit findings 已複製到剪貼簿",
        )

    def test_restores_original_clipboard_when_findings_are_missing(self) -> None:
        block = see_cxr_ai_block()

        self.assertIn("Clipboard := aiSummary", block)
        self.assertIn("Clipboard := ClipboardBackup", block)
        self.assertIn("DICOM header 中找不到 Lunit findings", block)
        success_copy = block.index("Clipboard := aiSummary")
        restore_copy = block.index("Clipboard := ClipboardBackup")
        missing_notice = block.index("DICOM header 中找不到 Lunit findings")

        self.assertLess(success_copy, restore_copy)
        self.assertLess(restore_copy, missing_notice)
        self.assertIn('if (aiSummary != "")', block)

    def test_does_not_prompt_or_paste_findings_into_his(self) -> None:
        block = see_cxr_ai_block()

        self.assertNotIn("Copy AI report to chk060?", block)
        self.assertNotIn("CopyCXRtoHISWithParam", block)


if __name__ == "__main__":
    unittest.main()
