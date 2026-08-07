from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from tool.extract_epub_chapters import split_epub_by_chapter


class SplitEpubByChapterTests(unittest.TestCase):
    def test_groups_nested_toc_entries_without_duplicating_shared_xhtml(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd() / "tmp") as temp_dir:
            work = Path(temp_dir)
            epub = work / "sample.epub"
            output = work / "chapters"
            with zipfile.ZipFile(epub, "w") as book:
                book.writestr(
                    "OEBPS/content.opf",
                    """<?xml version='1.0' encoding='utf-8'?>
                    <package xmlns='http://www.idpf.org/2007/opf'>
                      <metadata xmlns:dc='http://purl.org/dc/elements/1.1/'>
                        <dc:title>測試書名</dc:title><dc:language>zh-TW</dc:language>
                      </metadata>
                    </package>""",
                )
                book.writestr(
                    "OEBPS/toc.ncx",
                    """<?xml version='1.0' encoding='utf-8'?>
                    <ncx xmlns='http://www.daisy.org/z3986/2005/ncx/'>
                      <navMap>
                        <navPoint><navLabel><text>前言</text></navLabel><content src='preface.xhtml'/></navPoint>
                        <navPoint><navLabel><text>第一章　起點</text></navLabel><content src='c1-title.xhtml'/>
                          <navPoint><navLabel><text>甲節</text></navLabel><content src='c1.xhtml#s1'/></navPoint>
                          <navPoint><navLabel><text>乙節</text></navLabel><content src='c1.xhtml#s2'/></navPoint>
                        </navPoint>
                        <navPoint><navLabel><text>第二章　終點</text></navLabel><content src='c2.xhtml'/></navPoint>
                      </navMap>
                    </ncx>""",
                )
                book.writestr("OEBPS/preface.xhtml", "<html><body><p>略過前言</p></body></html>")
                book.writestr("OEBPS/c1-title.xhtml", "<html><body><h1>第一章 起點</h1></body></html>")
                book.writestr(
                    "OEBPS/c1.xhtml",
                    "<html><body><h2 id='s1'>甲節</h2><p>唯一內容</p><h2 id='s2'>乙節</h2><p>後續內容</p></body></html>",
                )
                book.writestr("OEBPS/c2.xhtml", "<html><body><h1>第二章 終點</h1><p>第二章內容</p></body></html>")

            manifest = split_epub_by_chapter(epub, output)

            self.assertEqual(manifest["title"], "測試書名")
            self.assertEqual(manifest["language"], "zh-TW")
            self.assertEqual([item["title"] for item in manifest["entries"]], ["第一章　起點", "第二章　終點"])
            first = (output / manifest["entries"][0]["output_file"]).read_text(encoding="utf-8")
            self.assertEqual(first.count("唯一內容"), 1)
            self.assertIn("甲節", first)
            self.assertIn("乙節", first)
            saved = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["entries"], manifest["entries"])


if __name__ == "__main__":
    unittest.main()
