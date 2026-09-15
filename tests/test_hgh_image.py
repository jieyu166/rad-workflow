"""病歷號檔名與真實 PNG 編碼；不操作 PACS。"""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from test_usai_models import ROOT, function

class HGHImageTests(unittest.TestCase):
    def test_filename_and_png_export(self):
        source=(ROOT/'hgh-bowel/hgh_capture.ahk').read_text(encoding='utf-8-sig')
        helpers='\n'.join(function(source,n) for n in ['HGH_ImagePath','HGH_SaveClipboardPNG'])
        us=(ROOT/'ahk-scripts/US.ahk').read_text(encoding='utf-8-sig')
        helpers+='\n'+function(us,'SavePBitmapToPNG')
        # Clipboard boundary only: use a real synthetic HBITMAP without changing the desktop clipboard.
        helpers=helpers.replace('HGH_SaveClipboardPNG(path, ByRef error) {', 'HGH_SaveClipboardPNG(path, ByRef error) {\n    global hbitmap')
        helpers=helpers.replace('DllCall("OpenClipboard", "Ptr", A_ScriptHwnd)', 'true').replace('DllCall("CloseClipboard")', 'DllCall("GetCurrentProcessId")').replace('DllCall("GetClipboardData", "UInt", 2, "Ptr")', 'hbitmap')
        with tempfile.TemporaryDirectory(prefix='hgh-image-') as td:
            code=r'''#NoEnv
#NoTrayIcon
#SingleInstance Off

try {
    module := DllCall("LoadLibrary", "Str", "gdiplus.dll", "Ptr")
    VarSetCapacity(si, A_PtrSize = 8 ? 24 : 16, 0)
    NumPut(1, si, 0, "UInt")
    DllCall("gdiplus\GdiplusStartup", "Ptr*", token, "Ptr", &si, "Ptr", 0)
    DllCall("gdiplus\GdipCreateBitmapFromScan0", "Int", 8, "Int", 6, "Int", 0, "Int", 0x26200A, "Ptr", 0, "Ptr*", bitmap)
    DllCall("gdiplus\GdipCreateHBITMAPFromBitmap", "Ptr", bitmap, "Ptr*", hbitmap, "UInt", 0xffffffff)

    path := HGH_ImagePath("001234", "TMP", err)
    ok := HGH_SaveClipboardPNG(path, err)
    duplicate := HGH_ImagePath("001234", "TMP", err)
    invalid := HGH_ImagePath("../bad", "TMP", err)
    reserved := HGH_ImagePath("CON", "TMP", err)
    DllCall("DeleteObject", "Ptr", hbitmap)
    hbitmap := 0
    missing := HGH_SaveClipboardPNG("TMP\missing.png", err)
    FileAppend, % ok . "," . duplicate . "," . invalid . "," . reserved . "," . missing, TMP\result.txt, UTF-8
} finally {
    DllCall("gdiplus\GdipDisposeImage", "Ptr", bitmap)
    DllCall("gdiplus\GdiplusShutdown", "Ptr", token)


}
ExitApp
'''.replace('TMP',td)
            script=Path(td)/'test.ahk'
            script.write_text(code+'\n'+helpers,encoding='utf-8-sig')
            try:
                run=subprocess.run([os.environ['AHK_V1_EXE'],'/ErrorStdOut',str(script)],capture_output=True,timeout=10)
            except subprocess.TimeoutExpired as e:
                self.fail('CHECKPOINTS: '+str(e.stdout))
            self.assertEqual(run.returncode,0,(run.stdout+run.stderr).decode(errors='replace'))
            self.assertEqual((Path(td)/'result.txt').read_text(encoding='utf-8-sig'),'1,,,,0')
            data=(Path(td)/'001234.png').read_bytes()
            self.assertEqual(data[:8],b'\x89PNG\r\n\x1a\n')
            self.assertEqual(int.from_bytes(data[16:20],'big'),8)
            self.assertEqual(int.from_bytes(data[20:24],'big'),6)
            self.assertFalse((Path(td)/'missing.png').exists())
