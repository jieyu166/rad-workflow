"""Mammo 疑陽表單擷取：切出 Mammo.ahk 的核心函式，以 stub 取代視窗/DICOM/Run 後實跑。"""
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
AHK = os.environ.get('AHK_V1_EXE', '')
BEGIN = '; ==== BEGIN mammo-form-core'
END = '; ==== END mammo-form-core ===='
NATIONAL_ID_SENTINEL = 'A123456789'


def read_ahk(name):
    return (ROOT / 'ahk-scripts' / name).read_text(encoding='utf-8-sig')


def slice_function(source, name):
    """Return a top-level AHK function definition (from its header to the first column-0 '}')."""
    match = re.search(r'^' + re.escape(name) + r'\(.*?^\}[ \t]*$', source, re.S | re.M)
    if not match:
        raise AssertionError('function not found: ' + name)
    return match.group(0)


def core_block():
    source = read_ahk('Mammo.ahk')
    start = source.index(BEGIN)
    return source[start:source.index(END, start) + len(END)]


def button_label():
    source = read_ahk('Mammo.ahk')
    start = source.index('\nMammoSuspiciousForm:\n') + 1
    end = source.index('\nreturn\n', start) + len('\nreturn\n')
    return source[start:end]


def dicom_text(patient_id):
    lines = [
        '0008,0020 Study Date  VR: DA  VM: 1', '          (0000008) |20260915|',
        '0008,0050 Accession Number  VR: SH  VM: 1', '          (0000010) |9876543210|',
        "0010,0010 Patient's Name  VR: PN  VM: 1", '          (0000013) |CHEN^MEI LING|',
        '0010,0020 Patient ID  VR: LO  VM: 1', '          (0000008) |%s|' % patient_id,
        "0010,0030 Patient's Birth Date  VR: DA  VM: 1", '          (0000008) |19700102|',
        '0010,1000 Other Patient IDs  VR: LO  VM: 1', '          (0000010) |%s|' % NATIONAL_ID_SENTINEL,
    ]
    return '`r`n'.join(line.replace('%', '`%') for line in lines)


STUBS = r'''
; ---- test stubs ----
MammoFormGetReportText() {
    global
    return T_Report
}
MammoFormGetExamNo() {
    global
    return T_Exam
}
MammoFormPACSExists() {
    global
    return T_PACS
}
MammoFormOpenPage(url) {
    global
    T_OpenCalls += 1
    T_URL := url
}
MammoFormAlert(msg) {
    global
    T_Alerts .= msg . " / "
}
ActivatePACSForLDCT() {
    return true
}
GetPACSPatientChineseName() {
    global
    return T_NameZh
}
GetDICOMData() {
    global
    T_DicomCalls += 1
    T_Clip := T_DICOM  ; the real helper overwrites the clipboard
    return T_DICOM
}
; Same logic as test.ahk GetAccessionNumber minus its clipboard save/restore.
GetAccessionNumber(text := "") {
    if (text = "")
        text := GetDICOMData()
    return RegExReplace(GetDICOMLineData("accession number", text), "\D")
}
; Simulated clipboard so the test never touches the user's real clipboard.
MammoFormClipSave(ByRef saved) {
    global
    saved := T_Clip
}
MammoFormClipRestore(ByRef saved) {
    global
    T_Clip := saved
    T_Restores += 1
}
MammoFormClipSet(text) {
    global
    T_Clip := text
    return true
}
Mammo:
MammoBuildReport:
FileAppend, called, TMP\output_called.txt, UTF-8
return
'''

RUNNER = r'''#NoEnv
#NoTrayIcon
#SingleInstance Off
global T_Report, T_Exam, T_PACS, T_NameZh, T_DICOM, T_DicomCalls, T_OpenCalls, T_URL, T_Alerts, T_Clip, T_Restores
okDicom := "DICOM_OK"
badDicom := "DICOM_BAD"
report := "Screening mammography:`r`nA mass 1"" in size at C:\a`r`n`tBI-RADS category 0`r`n中文"

; name, report, exam, pacs, dicom, useLabel
RunCase("success", report, "12345678001", true, okDicom, true)
RunCase("empty_report", " `r`n`t ", "12345678001", true, okDicom, false)
RunCase("no_pacs", report, "12345678001", false, okDicom, false)
RunCase("bad_chart", report, "1234-567", true, okDicom, false)
RunCase("mismatch", report, "12345678001", true, badDicom, false)

; escaping round-trip via the pure builder
f := {}
f.chartNo := "12345678"
f.nameZh := "陳美玲"
f.nameEn := "CHEN^MEI LING"
f.birthDate := "1970-01-02"
f.studyDate := "20260915"
f.accession := "9876543210"
f.reportText := "size 1"" C:\a\b`r`nline2`tTAB " . Chr(1) . " 中文 ""end"""
FileAppend, % MammoFormBuildJSON(f), *TMP\escape.json, UTF-8
ExitApp

RunCase(name, report, exam, pacs, dicomKey, useLabel) {
    global
    T_Report := report
    T_Exam := exam
    T_PACS := pacs
    T_NameZh := "陳美玲"
    T_DICOM := (dicomKey = "DICOM_OK") ? "DICOM_OK_TEXT" : "DICOM_BAD_TEXT"
    T_DicomCalls := 0
    T_OpenCalls := 0
    T_URL := ""
    T_Alerts := ""
    T_Restores := 0
    orig := "ORIGINAL-CLIP-" . name
    T_Clip := orig
    if (useLabel) {
        ret := "label"
        Gosub, MammoSuspiciousForm
    } else {
        ret := MammoFormCapture()
    }
    clipNow := T_Clip
    restored := (clipNow == orig && T_Restores = 1) ? 1 : 0
    out := ret . "`n" . T_DicomCalls . "`n" . T_OpenCalls . "`n" . restored . "`n" . T_URL . "`n" . T_Alerts
    FileAppend, %out%, *TMP\%name%.txt, UTF-8
    if (name = "success")
        FileAppend, %clipNow%, *TMP\success_clip.json, UTF-8
}
'''


@unittest.skipUnless(AHK, 'AHK_V1_EXE not set')
class MammoFormCaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='mammo-form-')
        td = cls.tmp.name
        helpers = '\n'.join([
            slice_function(read_ahk('test.ahk'), 'GetDICOMLineData'),
            slice_function(read_ahk('CT.ahk'), 'LDCTUriEncodeUTF8'),
        ])
        runner = (RUNNER.replace('TMP', td)
                  .replace('"DICOM_OK_TEXT"', '"' + dicom_text('12345678') + '"')
                  .replace('"DICOM_BAD_TEXT"', '"' + dicom_text('87654321') + '"'))
        code = runner + '\n' + button_label() + core_block() + '\n' + STUBS.replace('TMP', td) + '\n' + helpers + '\n'
        script = Path(td) / 'mammo_form_test.ahk'
        script.write_text(code, encoding='utf-8-sig')
        cls.run_result = subprocess.run([AHK, '/ErrorStdOut', str(script)], capture_output=True, timeout=30)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        r = self.run_result
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr).decode(errors='replace'))

    def read(self, name):
        return (Path(self.tmp.name) / name).read_text(encoding='utf-8-sig')

    def case(self, name):
        ret, dicom_calls, open_calls, restored, url, alerts = self.read(name + '.txt').split('\n', 5)
        return dict(ret=ret, dicom=int(dicom_calls), open=int(open_calls), restored=restored, url=url, alerts=alerts)

    def test_escape_round_trip_and_key_order(self):
        raw = self.read('escape.json')
        data = json.loads(raw)
        self.assertEqual(list(data), ['source', 'version', 'chartNo', 'nameZh', 'nameEn',
                                      'birthDate', 'studyDate', 'accession', 'reportText'])
        self.assertEqual(data['reportText'], 'size 1" C:\\a\\b\r\nline2\tTAB \x01 中文 "end"')
        self.assertEqual(data['source'], 'rad-workflow/mammo-form')
        self.assertEqual(data['version'], '1')
        self.assertEqual(data['birthDate'], '19700102')
        self.assertTrue(all(isinstance(v, str) for v in data.values()))
        self.assertIn('\\r\\n', raw)
        self.assertIn('\\t', raw)
        self.assertIn('\\u0001', raw)
        self.assertIn('中文', raw)  # non-ASCII stays literal

    def test_success_flow(self):
        c = self.case('success')
        self.assertEqual(c['dicom'], 1, 'GetDICOMData must be called exactly once')
        self.assertEqual(c['open'], 1)
        self.assertEqual(c['alerts'], '')
        self.assertNotIn('?', c['url'])
        self.assertNotIn('#', c['url'])
        self.assertTrue(c['url'].startswith('file:///'))
        self.assertTrue(c['url'].endswith('/tool/mammo-suspicious-form.html'), c['url'])
        raw = self.read('success_clip.json')
        self.assertNotIn(NATIONAL_ID_SENTINEL, raw)
        data = json.loads(raw)
        self.assertEqual(data, {
            'source': 'rad-workflow/mammo-form', 'version': '1', 'chartNo': '12345678',
            'nameZh': '陳美玲', 'nameEn': 'CHEN^MEI LING', 'birthDate': '19700102',
            'studyDate': '20260915', 'accession': '9876543210',
            'reportText': 'Screening mammography:\r\nA mass 1" in size at C:\\a\r\n\tBI-RADS category 0\r\n中文',
        })
        self.assertFalse((Path(self.tmp.name) / 'output_called.txt').exists(), 'existing output routine must not run')

    def test_abort_cases(self):
        expectations = {
            'empty_report': ('報告', 0),
            'no_pacs': ('INFINITT PACS', 0),
            'bad_chart': ('8 碼', 0),
            'mismatch': ('HIS 與 PACS 病人不同', 1),
        }
        for name, (msg, dicom_calls) in expectations.items():
            with self.subTest(name):
                c = self.case(name)
                self.assertEqual(c['ret'], '0')
                self.assertEqual(c['open'], 0, 'page must not open on abort')
                self.assertEqual(c['restored'], '1', 'clipboard must be restored')
                self.assertEqual(c['dicom'], dicom_calls)
                self.assertIn(msg, c['alerts'])
                self.assertEqual(c['url'], '')
        self.assertFalse((Path(self.tmp.name) / 'output_called.txt').exists())

    def test_gui_button_and_no_other_patient_ids_lookup(self):
        source = read_ahk('Mammo.ahk')
        self.assertIn('gMammoSuspiciousForm, 疑陽表單', source)
        # code lines only (comments may mention the forbidden attribute)
        core = '\n'.join(re.sub(r'(^|\s);.*$', '', line) for line in (button_label() + core_block()).splitlines())
        self.assertNotIn('Other Patient', core)
        self.assertNotIn('Patient ID', core)
        self.assertNotIn('0010,1000', core)
        self.assertNotIn('Gosub, Mammo', core)
        self.assertNotIn('CopyCXRtoHIS', core)
        # real clipboard handling: ClipboardAll backup passed ByRef
        self.assertRegex(source, r'MammoFormClipSave\(ByRef saved\) \{\s+saved := ""\s+try saved := ClipboardAll')
        self.assertIn('MammoFormClipRestore(ByRef saved)', source)
        self.assertIn('MammoFormClipSave(clipSaved)', core)
        self.assertIn('MammoFormClipRestore(clipSaved)', core)


if __name__ == '__main__':
    unittest.main()
