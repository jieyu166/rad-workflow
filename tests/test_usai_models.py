"""以 AHK v1 隱藏 GUI 實跑模型路由；只替換網路 worker，不呼叫 API。

設定 AHK_V1_EXE 後執行：python -m unittest discover -s tests -p test_usai_models.py
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'ahk-scripts' / 'US.ahk'
MODELS = ['gpt-6-astra', 'gpt-5.6-terra', 'gpt-5.6-luna']


def function(source, name):
    match = re.search(rf'^{name}\([^\n]*\) \{{\n.*?^\}}', source, re.M | re.S)
    if not match:
        raise AssertionError(f'找不到函式 {name}')
    return match.group()


class USAIModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        exe = os.environ.get('AHK_V1_EXE')
        if not exe or not Path(exe).is_file():
            raise RuntimeError('需設定 AHK_V1_EXE 指向 AutoHotkey v1 可攜版執行檔')
        source = SOURCE.read_text(encoding='utf-8-sig')
        gui = source[source.index('ShowUSAIGUI:'):source.index('\nUSAIExamTypeChanged:')]
        gui = gui.replace('Gui, USAIG:Show, w900 h707', 'Gui, USAIG:Show, Hide w900 h707')
        analyze = source[source.index('\nUSAIAnalyze:'):source.index('\nCheckOpenAIResult:')]
        labels = set(re.findall(r'\bg(USAI\w+)\b', gui)) - {'USAIAnalyze'}
        helpers = function(source, 'BuildOpenAIResponsesJSON') + '\n' + function(source, 'JEscape')
        if re.search(r'^USAIIsSupportedModel\(', source, re.M):
            helpers += '\n' + function(source, 'USAIIsSupportedModel')
        for name in ['USAIPromptFileName', 'USAILoadPrompt', 'USAICancelJob', 'USAIResetSession']:
            if re.search(rf'^{name}\(', source, re.M):
                helpers += '\n' + function(source, name)
        with tempfile.TemporaryDirectory(prefix='usai-model-test-') as temp:
            out = Path(temp) / 'results.jsonl'
            script = Path(temp) / 'test.ahk'
            package = Path(temp) / 'included-package'
            package.mkdir()
            if (ROOT / 'ahk-scripts/usai-prompts').exists():
                shutil.copytree(ROOT / 'ahk-scripts/usai-prompts', package / 'usai-prompts')
            prelude = r'''
#NoEnv
#NoTrayIcon
#SingleInstance Off
SetBatchLines, -1
API_KEY := "SYNTHETIC_TEST_KEY"
Gosub, ShowUSAIGUI
USAI_CurrentImage := "data:image/png;base64,TEST_CURRENT"
USAI_PreviousImage := "data:image/png;base64,TEST_PREVIOUS"
GuiControlGet, initialModel, USAIG:, USAIModel
header := "{""initialModel"":" . JEscape(initialModel) . "}"
FileAppend, % header . "`n", OUTPUT_PATH, UTF-8
for _, wantedModel in ["gpt-6-astra", "gpt-5.6-terra", "gpt-5.6-luna"] {
    GuiControl, USAIG:ChooseString, USAIModel, %wantedModel%
    Loop, 6 {
        GuiControl, USAIG:Choose, USAIExamType, %A_Index%
        Loop, 3 {
            testImageMode := A_Index
            Loop, 3 {
                control := "USAIChoice" . A_Index
                GuiControl, USAIG:, %control%, % A_Index = testImageMode
            }
            Gosub, USAIAnalyze
            SetTimer, CheckOpenAIResult, Off
        }
    }
}
; 更新外部檔案必須立即生效；缺檔/空檔不得送出任何請求。
if IsFunc("USAILoadPrompt") {
    FileAppend, `nRELOAD_SENTINEL, PROMPT_PATH\general.md, UTF-8
    GuiControl, USAIG:Choose, USAIExamType, 6
    testImageMode := 1
    GuiControl, USAIG:, USAIChoice1, 1
    GuiControl, USAIG:, USAIChoice2, 0
    GuiControl, USAIG:, USAIChoice3, 0
    Gosub, USAIAnalyze
    SetTimer, CheckOpenAIResult, Off
    for _, missingFile in ["general.md", "common.md", "modes\current.md"] {
        path := "PROMPT_PATH\" . missingFile
        FileRead, savedText, *P65001 %path%
        FileDelete, %path%
        Loop, 2 {
            Gosub, USAIAnalyze
            GuiControlGet, status, USAIG:, USAIStatus
            GuiControlGet, enabled, USAIG:Enabled, USAIAnalyzeBtn
            record := "{""failureFile"":" . JEscape(missingFile) . ",""status"":" . JEscape(status) . ",""enabled"":" . enabled . "}"
            FileAppend, % record . "`n", OUTPUT_PATH, UTF-8
            FileAppend, % " `n ", %path%, UTF-8
        }
        FileDelete, %path%
        FileAppend, %savedText%, %path%, UTF-8
    }
}
Gui, USAIG:Destroy
ExitApp
'''.replace('OUTPUT_PATH', str(out)).replace('PROMPT_PATH', str(package / 'usai-prompts'))
            worker = r'''
StartOpenAIBackgroundJob(apiKey, modelID, prompt, images, unused*) {
    global wantedModel, USAIExamType, testImageMode
    payload := BuildOpenAIResponsesJSON(modelID, prompt, images)
    line := "{""wantedModel"":" . JEscape(wantedModel) . ",""exam"":" . JEscape(USAIExamType) . ",""testImageMode"":" . testImageMode . ",""payload"":" . payload . "}"
    FileAppend, % line . "`n", OUTPUT_PATH, UTF-8
    GuiControl, USAIG:Enable, USAIAnalyzeBtn
    return true
}
CheckOpenAIResult:
return
'''.replace('OUTPUT_PATH', str(out))
            stubs = '\n'.join(f'{label}:\nreturn' for label in sorted(labels))
            include = package / 'usai-extracted.ahk'
            helpers = helpers.replace('A_Temp', '"' + temp + '"')
            include.write_text(gui + analyze + helpers + worker + stubs, encoding='utf-8-sig')
            script.write_text(prelude + '\n#Include ' + str(include), encoding='utf-8-sig')
            result = subprocess.run([exe, '/ErrorStdOut', str(script)], cwd=ROOT, capture_output=True, timeout=20)
            if result.returncode:
                raise AssertionError(result.stdout.decode(errors='replace') + result.stderr.decode(errors='replace'))
            records = [json.loads(line.lstrip('\ufeff')) for line in out.read_text(encoding='utf-8-sig').splitlines()]
        cls.initial = records[0]
        cls.records = [r for r in records[1:] if 'payload' in r][:54]
        cls.reloads = [r for r in records[1:] if 'payload' in r][54:]
        cls.failures = [r for r in records[1:] if 'failureFile' in r]

    def test_default_model(self):
        self.assertEqual(self.initial['initialModel'], 'gpt-6-astra')

    def test_selected_model_reaches_request_for_every_exam(self):
        self.assertEqual(len(self.records), 54)
        for row in self.records:
            with self.subTest(model=row['wantedModel'], exam=row['exam']):
                self.assertEqual(row['payload']['model'], row['wantedModel'])

    def test_no_thinking_options_and_explicit_medium_reasoning(self):
        for row in self.records:
            self.assertNotIn('Thinking', row['exam'])
            self.assertNotIn('GPT-5.4', row['exam'])
            self.assertEqual(row['payload']['reasoning'], {'effort': 'medium'})
            text = row['payload']['input'][0]['content'][0]['text']
            self.assertNotIn('Analyze the image with high reasoning effort.', text)

    def test_image_and_breast_output_contract_preserved(self):
        for row in self.records:
            content = row['payload']['input'][0]['content']
            expected = ['TEST_PREVIOUS', 'TEST_CURRENT'] if row['testImageMode'] == 3 else ['TEST_CURRENT']
            if row['testImageMode'] == 2:
                expected.append('TEST_PREVIOUS')
            self.assertEqual(content[1:], [{'type': 'input_image', 'image_url': 'data:image/png;base64,' + image, 'detail': 'high'} for image in expected])
            if 'Breast' in row['exam']:
                self.assertIn('## 主要鑑別診斷', content[0]['text'])
                self.assertIn('## BI-RADS 判斷', content[0]['text'])

    def test_chest_option_uses_chest_prompt(self):
        rows = [r for r in self.records if 'Chest' in r['exam'] or 'CXR' in r['exam']]
        self.assertEqual(len(rows), 9)
        for row in rows:
            self.assertIn('No active lung lesion is noted.', row['payload']['input'][0]['content'][0]['text'])

    def test_mode_does_not_override_exam_report_format(self):
        for row in self.records:
            text = row['payload']['input'][0]['content'][0]['text']
            self.assertNotIn('Output format (Single line): Location', text)
            self.assertNotIn('Output format: Location, Size, Description, Impression.', text)
            if row['testImageMode'] != 3:
                self.assertNotIn('Compare size change.', text)

    def test_external_edit_reloaded_without_restarting_and_include_path_resolves(self):
        self.assertEqual(len(self.reloads), 1)
        self.assertIn('RELOAD_SENTINEL', self.reloads[0]['payload']['input'][0]['content'][0]['text'])

    def test_missing_and_blank_files_stop_before_worker_and_keep_button_enabled(self):
        self.assertEqual(len(self.failures), 6)
        for row in self.failures:
            self.assertIn(row['failureFile'], row['status'])
            self.assertEqual(row['enabled'], 1)


if __name__ == '__main__':
    unittest.main()
