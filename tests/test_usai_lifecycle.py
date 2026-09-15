"""AHK v1 isolated lifecycle regression; no API or PACS interaction."""
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from test_usai_models import function, ROOT, SOURCE

class LifecycleTests(unittest.TestCase):
    def test_reopen_ocr_failure_and_multiblock(self):
        source = SOURCE.read_text(encoding='utf-8-sig')
        gui = source[source.index('ShowUSAIGUI:'):source.index('\nUSAIExamTypeChanged:')].replace('Gui, USAIG:Show, w900 h707', 'Gui, USAIG:Show, Hide w900 h707')
        ocr = source[source.index('USAIExecuteOCR1:\n'):source.index('; 執行 OCR (前次影像)')]
        ocr = ocr.replace('if (!FileExist(A_Temp . "\\usai_current.png"))', 'if (false)')
        labels = set(re.findall(r'\bg(USAI\w+)\b', gui)) - {'USAIExecuteOCR1'}
        helpers = '\n'.join(function(source, n) for n in ['ParseOpenAIResponse', 'RegGet', 'JsonUnescape', 'DecodeUnicodeEscapes', 'HexToInt', 'UnicodeChar'])
        for name in ['USAICancelJob', 'USAIResetSession']:
            if re.search(r'^'+name+r'\(', source, re.M):
                helpers += '\n'+function(source, name)
        stubs = '\n'.join(x+':\nreturn' for x in sorted(labels))+'\nCheckOpenAIResult:\nreturn\n'
        for name in ['CropImage', 'PerformOCR', 'MatchBreastLocation_method2', 'MatchDimension', 'MatchImageNumber', 'FormatOCRToReport']:
            stubs += name+'(args*) {\n return false\n}\n'
        with tempfile.TemporaryDirectory(prefix='usai-lifecycle-') as td:
            out = Path(td)/'out.txt'
            (Path(td)/'openai_usai_response.txt').write_text('{"status":"completed","output":[{"content":[{"type":"output_text","text":"OLD_RESULT"}]}]}', encoding='utf-8')
            code = r'''#NoEnv
#NoTrayIcon
#SingleInstance Off
Gosub, ShowUSAIGUI
USAI_CurrentOCRText := "OLD_25mm"
Gosub, USAIExecuteOCR1
FileAppend, % "OCR=" . USAI_CurrentOCRText . "`n", OUTPUT, UTF-8
USAI_CurrentImage := "OLD_IMAGE"
Gosub, ShowUSAIGUI
FileAppend, % "IMAGE=" . USAI_CurrentImage . "`n", OUTPUT, UTF-8
payload := "{""status"":""completed"",""output"":[{""content"":[{""type"":""output_text"",""text"":""FIRST""},{""type"":""output_text"",""text"":""SECOND""}]}]}"
parsed := StrReplace(ParseOpenAIResponse(payload), "`n", "|")
FileAppend, % "PARSED=" . parsed . "`n", OUTPUT, UTF-8
ExitApp
'''.replace('OUTPUT', str(out))
            script = Path(td)/'test.ahk'
            helpers = helpers.replace('A_Temp', '"' + td + '"')
            script.write_text("\n".join([code, gui, ocr, helpers, stubs]), encoding='utf-8-sig')
            result = subprocess.run([os.environ['AHK_V1_EXE'], '/ErrorStdOut', str(script)], capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, (result.stdout+result.stderr).decode(errors='replace'))
            rows = dict(line.split('=',1) for line in out.read_text(encoding='utf-8-sig').splitlines())
        with self.subTest('OCR failure'): self.assertEqual(rows['OCR'], '')
        with self.subTest('reopen'): self.assertEqual(rows['IMAGE'], '')
        with self.subTest('multiblock'): self.assertEqual(rows['PARSED'], 'FIRST|SECOND')

    def test_late_legacy_response_is_not_accepted_by_new_job(self):
        source = SOURCE.read_text(encoding='utf-8-sig')
        callback = source[source.index('CheckOpenAIResult:\n'):source.index('\nUSAIPromptFileName(')]
        helpers = '\n'.join(function(source,n) for n in ['ParseOpenAIResponse','RegGet','JsonUnescape','DecodeUnicodeEscapes','HexToInt','UnicodeChar'])
        if re.search(r'^USAICancelJob\(', source, re.M): helpers += '\n'+function(source,'USAICancelJob')
        with tempfile.TemporaryDirectory(prefix='usai-late-') as td:
            out = Path(td)/'out.txt'
            (Path(td)/'openai_usai_response.txt').write_text('{"status":"completed","output":[{"content":[{"type":"output_text","text":"OLD_RESULT"}]}]}', encoding='utf-8')
            code = r'''#NoEnv
#NoTrayIcon
#SingleInstance Off
Gui, USAIG:New
Gui, USAIG:Add, Edit, vUSAIResult, NEW_PENDING
Gui, USAIG:Add, Text, vUSAIStatus
Gui, USAIG:Add, Button, vUSAIAnalyzeBtn, Analyze
g_USAI_StartTick := A_TickCount
g_USAI_Job := {prefix: "TMP\new", result: "TMP\new_response.txt", pid: 0}
Gosub, CheckOpenAIResult
SetTimer, CheckOpenAIResult, Off
GuiControlGet, result, USAIG:, USAIResult
FileAppend, %result%, OUTPUT, UTF-8
ExitApp
'''.replace('TMP',td).replace('OUTPUT',str(out))
            # Redirect all filesystem effects, including legacy fixed paths, into sandbox.
            callback = callback.replace('%A_Temp%',td).replace('A_Temp', '"'+td+'"')
            script=Path(td)/'late.ahk'
            script.write_text('\n'.join([code,callback,helpers]),encoding='utf-8-sig')
            result=subprocess.run([os.environ['AHK_V1_EXE'],'/ErrorStdOut',str(script)],capture_output=True,timeout=20)
            self.assertEqual(result.returncode,0,(result.stdout+result.stderr).decode(errors='replace'))
            self.assertEqual(out.read_text(encoding='utf-8-sig'),'NEW_PENDING')

    def test_worker_replacement_timeout_and_close_kill_process_and_remove_files(self):
        source=SOURCE.read_text(encoding='utf-8-sig')
        start=function(source,'StartOpenAIBackgroundJob')
        # Only transport is substituted. Real worker generation, Run, handles,
        # cancellation, timeout callback and close handler execute unchanged.
        start=start.replace('whr := ComObjCreate("WinHttp.WinHttpRequest.5.1")', 'whr := new SyntheticHTTP()')
        fake=r'''    class SyntheticHTTP {
        Open(args*) {
        }
        SetRequestHeader(args*) {
        }
        SetTimeouts(args*) {
        }
        Send(args*) {
            if InStr(args[1], "COMPLETE")
                Sleep, 50
            else
                Sleep, 10000
            this.Status := 200
            this.ResponseText := "{""status"":""completed"",""output"":[{""content"":[{""type"":""output_text"",""text"":""COMPLETE_OK""}]}]}"
        }
    }
'''
        start=start.replace('    ExitApp\n    )','    ExitApp\n'+fake+'    )')
        callback=source[source.index('CheckOpenAIResult:\n'):source.index('\nUSAIPromptFileName(')]
        close=source[source.index('USAIGGuiClose:\n'):source.index('\nUSAICancelJob() {')]
        helpers='\n'.join(function(source,n) for n in ['USAICancelJob','USAIResetSession','BuildOpenAIResponsesJSON','JEscape','ParseOpenAIResponse','RegGet','JsonUnescape','DecodeUnicodeEscapes','HexToInt','UnicodeChar'])
        with tempfile.TemporaryDirectory(prefix='usai-worker-') as td:
            out=Path(td)/'out.txt'
            code=r'''#NoEnv
#NoTrayIcon
#SingleInstance Off
Gui, USAIG:New
Gui, USAIG:Add, Edit, vUSAIResult
Gui, USAIG:Add, Text, vUSAIStatus
Gui, USAIG:Add, Button, vUSAIAnalyzeBtn, Analyze
ok1 := StartOpenAIBackgroundJob("TEST_KEY", "test-model", "SYNTHETIC", [])
first := g_USAI_Job
ok2 := StartOpenAIBackgroundJob("TEST_KEY", "test-model", "SYNTHETIC", [])
second := g_USAI_Job
Process, Exist, % first.pid
alive1 := ErrorLevel
unique := first.prefix != second.prefix
g_USAI_StartTick := A_TickCount - 181000
Gosub, CheckOpenAIResult
Process, Exist, % second.pid
alive2 := ErrorLevel
ok3 := StartOpenAIBackgroundJob("TEST_KEY", "test-model", "SYNTHETIC", [])
third := g_USAI_Job
Gosub, USAIGGuiClose
Process, Exist, % third.pid
alive3 := ErrorLevel
remains := 0
for _, job in [first,second,third] {
    for _, suffix in ["_request.json","_worker.ahk","_response.txt","_response.txt.part"] {
        if FileExist(job.prefix . suffix)
            remains += 1
    }
}
Gui, USAIG:New
Gui, USAIG:Add, Edit, vUSAIResult
Gui, USAIG:Add, Text, vUSAIStatus
Gui, USAIG:Add, Button, vUSAIAnalyzeBtn, Analyze
ok4 := StartOpenAIBackgroundJob("TEST_KEY", "test-model", "COMPLETE", [])
fourth := g_USAI_Job
g_USAI_StartTick := A_TickCount
Loop, 60 {
    if FileExist(fourth.result)
        break
    Sleep, 50
}
Gosub, CheckOpenAIResult
GuiControlGet, completed, USAIG:, USAIResult
USAICancelJob()
FileAppend, % ok4 . "," . completed . ",", OUTPUT, UTF-8
FileAppend, % ok1 . "," . ok2 . "," . ok3 . "," . unique . "," . alive1 . "," . alive2 . "," . alive3 . "," . remains, OUTPUT, UTF-8
ExitApp
'''.replace('OUTPUT',str(out))
            parts='\n'.join([start,callback,close,helpers]).replace('A_Temp','"'+td+'"')
            script=Path(td)/'worker-test.ahk'
            script.write_text(code+parts,encoding='utf-8-sig')
            result=subprocess.run([os.environ['AHK_V1_EXE'],'/ErrorStdOut',str(script)],capture_output=True,timeout=20)
            self.assertEqual(result.returncode,0,(result.stdout+result.stderr).decode(errors='replace'))
            self.assertEqual(out.read_text(encoding='utf-8-sig'),'1,COMPLETE_OK,1,1,1,1,0,0,0,0')

if __name__ == '__main__':
    unittest.main()

