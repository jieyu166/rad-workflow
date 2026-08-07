from __future__ import annotations

import argparse
import html
import json
import re
import zipfile
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET


@dataclass
class TocEntry:
    order: int
    depth: int
    title: str
    href: str
    kind: str
    output_file: str = ""
    characters: int = 0


class TextExtractor(HTMLParser):
    BLOCKS = {
        "address", "article", "aside", "blockquote", "br", "div", "figcaption",
        "footer", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "li",
        "main", "nav", "ol", "p", "pre", "section", "table", "td", "th", "tr", "ul",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.ignored = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.ignored += 1
        elif not self.ignored and tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.ignored:
            self.ignored -= 1
        elif not self.ignored and tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.ignored:
            self.parts.append(data)

    def text(self) -> str:
        raw = html.unescape("".join(self.parts)).replace("\u3000", " ")
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw.splitlines()]
        return "\n\n".join(line for line in lines if line).strip() + "\n"


def classify(title: str) -> str:
    if re.search(r"第[一二三四五六七八九十百]+章", title):
        return "chapter"
    if title.startswith("第") and "篇" in title:
        return "part"
    if title.startswith("附錄"):
        return "appendix"
    return "frontmatter"


def safe_name(index: int, title: str) -> str:
    cleaned = re.sub(r"[<>:\"/\\|?*]", "-", title)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    return f"{index:02d}-{cleaned}.txt"


def walk_navpoints(node: ET.Element, ns: dict[str, str], depth: int = 0):
    for point in node.findall("ncx:navPoint", ns):
        label = point.findtext("ncx:navLabel/ncx:text", default="", namespaces=ns).strip()
        content = point.find("ncx:content", ns)
        href = content.attrib.get("src", "") if content is not None else ""
        yield depth, label, href
        yield from walk_navpoints(point, ns, depth + 1)


def metadata(book: zipfile.ZipFile) -> tuple[str, str]:
    opf_path = next(name for name in book.namelist() if name.lower().endswith(".opf"))
    root = ET.fromstring(book.read(opf_path))
    dc = {"dc": "http://purl.org/dc/elements/1.1/"}
    title = root.findtext(".//dc:title", default="", namespaces=dc).strip()
    language = root.findtext(".//dc:language", default="", namespaces=dc).strip()
    return title, language


def child_sources(point: ET.Element, ns: dict[str, str]) -> list[str]:
    sources: list[str] = []
    for node in [point, *point.findall(".//ncx:navPoint", ns)]:
        content = node.find("ncx:content", ns)
        if content is None:
            continue
        source = content.attrib.get("src", "").split("#", 1)[0]
        if source and source not in sources:
            sources.append(source)
    return sources


def split_epub_by_chapter(epub: Path, output: Path) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    entries: list[TocEntry] = []
    with zipfile.ZipFile(epub) as book:
        title, language = metadata(book)
        ncx_path = next(name for name in book.namelist() if name.lower().endswith("toc.ncx"))
        root = ET.fromstring(book.read(ncx_path))
        ns = {"ncx": "http://www.daisy.org/z3986/2005/ncx/"}
        nav_map = root.find("ncx:navMap", ns)
        if nav_map is None:
            raise RuntimeError("EPUB NCX has no navMap")

        base = PurePosixPath(ncx_path).parent
        chapter_points = [
            point
            for point in nav_map.findall("ncx:navPoint", ns)
            if classify(point.findtext("ncx:navLabel/ncx:text", default="", namespaces=ns).strip()) == "chapter"
        ]
        for order, point in enumerate(chapter_points, start=1):
            chapter_title = point.findtext("ncx:navLabel/ncx:text", default="", namespaces=ns).strip()
            sources = child_sources(point, ns)
            bodies: list[str] = []
            for source in sources:
                archive_path = str(base / source)
                parser_html = TextExtractor()
                parser_html.feed(book.read(archive_path).decode("utf-8", errors="replace"))
                body = parser_html.text().strip()
                if body:
                    bodies.append(body)
            chapter_body = "\n\n".join(bodies).strip() + "\n"
            filename = safe_name(order, chapter_title)
            (output / filename).write_text(chapter_body, encoding="utf-8")
            entries.append(
                TocEntry(
                    order=order,
                    depth=0,
                    title=chapter_title,
                    href=", ".join(str(base / source) for source in sources),
                    kind="chapter",
                    output_file=filename,
                    characters=len(re.sub(r"\s+", "", chapter_body)),
                )
            )

    manifest: dict[str, object] = {
        "source": str(epub),
        "title": title,
        "language": language,
        "entries": [asdict(entry) for entry in entries],
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Split an EPUB by NCX table-of-contents entries.")
    parser.add_argument("epub", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    manifest = split_epub_by_chapter(args.epub, args.output)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
