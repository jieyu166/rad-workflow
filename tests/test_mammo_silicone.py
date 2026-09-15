"""Mammo 小針美容按鈕：隱藏 GUI 實跑，不操作 HIS。"""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from test_usai_models import ROOT

class MammoSiliconeTests(unittest.TestCase):
    def test_preset_and_normal_output(self):
        source=(ROOT/'ahk-scripts/Mammo.ahk').read_text(encoding='utf-8-sig')
        self.assertTrue('MammoSilicone:' in source, 'Missing silicone button handler')
        block=source[source.index(':O:mammo;::'):source.index(':O:tba;::')]
        block=block.replace(':O:mammo;::','ShowMammo:').replace('Gui Show, w380 h400, Mammo','Gui Show, Hide w380 h400, Mammo')
        with tempfile.TemporaryDirectory(prefix='mammo-silicone-') as td:
            code=r'''#NoEnv
#NoTrayIcon
#SingleInstance Off
Gosub, ShowMammo
GuiControl,, mammoT1, 0
GuiControl,, mammoT2, 1
GuiControl,, mammoO3, 0
GuiControl,, mammoO2, 1
Gosub, MammoSilicone
FileAppend, %desc%, TMP\preset.txt, UTF-8
GuiControlGet, density,, mammoD4
GuiControlGet, birads,, mammoB2
FileAppend, % density . "," . birads, TMP\selected.txt, UTF-8
Gosub, Mammo
FileAppend, %desc%, TMP\normal.txt, UTF-8
ExitApp
'''.replace('TMP',td)
            stubs='\nWriteStudyID:\nreturn\nCopyCXRtoHISWithParam(mode) {\n return\n}\n'
            script=Path(td)/'test.ahk'
            script.write_text(code+block+stubs,encoding='utf-8-sig')
            result=subprocess.run([os.environ['AHK_V1_EXE'],'/ErrorStdOut',str(script)],capture_output=True,timeout=15)
            self.assertEqual(result.returncode,0,(result.stdout+result.stderr).decode(errors='replace'))
            preset=(Path(td)/'preset.txt').read_text(encoding='utf-8-sig')
            normal=(Path(td)/'normal.txt').read_text(encoding='utf-8-sig')
            self.assertEqual((Path(td)/'selected.txt').read_text(encoding='utf-8-sig'),'1,1')
        for text in ['Diagnostic mammography', 'not available(other hospital).', 'BIRADS density D', 's/p bilateral multifocal liquid silicone injection throughout both breasts with', 'multiple silicone cysts of various sizes.', 'The normal fibroglandular tissue is obscured and cannot be well evaluated.', 'Fibrotic changes are also noted in the breast parenchyma. No visible mass lesions', 'could be identified.', '(BI-RADS category 2, benign)', 'Recommendation: Annual screening mammography', 'IMP: Bilateral silicone injection mammoplasty with poor visualization of the', 'breast parenchyma and architectural structures.']:
            self.assertIn(text,preset)
        self.assertNotIn('There is no clustered microcalcification',preset)
        self.assertEqual(preset.split('Addendum:')[1],normal.split('Addendum:')[1])
        self.assertNotIn('silicone',normal)
        self.assertIn('There is no clustered microcalcification',normal)
