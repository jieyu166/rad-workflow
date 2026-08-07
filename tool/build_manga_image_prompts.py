from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path("outputs/novel-to-manga/how-to-read-a-book-adult-dense")
SCRIPTS = ROOT / "manga-scripts"
PROMPTS = ROOT / "image-prompts"
GENERATED = ROOT / "generated-pages"

CHARACTER_ANCHOR = """Character reference mapping (visual source of truth):
- Reference Image 1 = WEN_SHUI / 溫水: young man, short black hair with one curved ahoge, large brown eyes, no glasses, white shirt with pale-blue collar/shoulder panels, solid green tie, dark trousers, navy reading notebook.
- Reference Image 2 = MENTOR_AI / 艾老師: adult woman, long straight side-parted blonde hair, blue-green eyes, slender face, white lab-coat-style jacket over a dark navy blouse, calm slightly tired expression.
- Reference Image 3 = TIAN_AI_XING / 天愛星: young woman, dark navy low twin tails, straight bangs, blue eyes, pale-blue ribbon ties, white long-sleeve blouse, oversized pale-blue bow, pale-blue pleated skirt, playful confident expression, tablet.
Treat the three reference images as identity anchors. Preserve face, hair, eye color, clothing silhouette, palette, apparent age, and gender. Do not swap identities or redesign outfits."""

STYLE_ANCHOR = """Use case: illustration-story
Asset type: complete interior educational manga page
Style/medium: polished full-color Japanese educational manga, clean cel shading, crisp line art, expressive but restrained adult-learning tone, accurate hands, detailed recurring workshop background, precise infographic inserts.
Composition/framing: vertical portrait complete manga page, left-to-right reading, exactly 6 clearly separated panels with unambiguous flow; one panel may be a larger infographic panel; top header shows chapter and page title; small page number in lower outside corner.
Color palette: deep teal and warm cream base; reading-level accents use gray, yellow, blue, and purple.
Text: render only the supplied Traditional Chinese text, verbatim, in clean high-contrast balloons or caption cards; no extra dialogue.
Constraints: complete manga page, not a poster and not a single illustration; all six panels present; no merged or missing panel; preserve character identities and outfits; neutral knowledge-comic camera language; no voyeuristic angles, visible underwear, sexualized framing, logos, signatures, or watermarks."""


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"---\n(.*?)\n---", text, flags=re.S)
    if not match:
        raise ValueError("missing frontmatter")
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            result[key] = value
    return result


def parse_pages(text: str) -> list[dict]:
    body = text.split("## Panel Script", 1)[1].split("## 本章連戲檢查", 1)[0]
    blocks = re.split(r"(?m)^### 第 (\d+) 頁｜(.+?)\r?$", body)
    pages: list[dict] = []
    for i in range(1, len(blocks), 3):
        page_no = int(blocks[i])
        title = blocks[i + 1].strip()
        block = blocks[i + 2]
        function = re.search(r"(?m)^- 頁面功能：(.+?)\r?$", block).group(1).strip()
        core = re.search(r"(?m)^- 核心命題：(.+?)\r?$", block).group(1).strip()
        hook = re.search(r"(?m)^- 頁尾鉤子：(.+?)\r?$", block).group(1).strip()
        panels = []
        for line in block.splitlines():
            if not re.match(r"^\| [1-6] \|", line):
                continue
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) != 6:
                raise ValueError(f"malformed panel row: {line}")
            panels.append({
                "number": int(cells[0]),
                "shot": cells[1],
                "visual": cells[2],
                "speaker": cells[3],
                "text": cells[4],
                "continuity": cells[5],
            })
        if len(panels) != 6:
            raise ValueError(f"page {page_no} has {len(panels)} panels")
        pages.append({"page": page_no, "title": title, "function": function, "core": core, "hook": hook, "panels": panels})
    return pages


def build_prompt(chapter: int, chapter_title: str, page: dict, previous: str) -> str:
    panel_lines = []
    for panel in page["panels"]:
        panel_lines.append(
            f"Panel {panel['number']}:\n"
            f"- Shot/function: {panel['shot']}\n"
            f"- Visual/action: {panel['visual']}\n"
            f"- Speaker: {panel['speaker']}\n"
            f"- Exact Traditional Chinese text: {panel['text']}\n"
            f"- Continuity: {panel['continuity']}"
        )
    return f"""Create Chapter {chapter}, Page {page['page']:02d} of the complete manga adaptation 《如何閱讀一本書》.

{STYLE_ANCHOR}

{CHARACTER_ANCHOR}

Page identity:
- Required header text: "第{chapter}章｜{chapter_title}"
- Required page-title text: "{page['title']}"
- Required page-number text: "P.{page['page']:02d}"
- Page function: {page['function']}
- Core proposition: {page['core']}
- Previous-page context: {previous}

Panel plan — exactly six panels, in this order:

{chr(10).join(panel_lines)}

Final panel emphasis: {page['hook']}

Prompt QA requirements:
- exactly 6 panels: PASS required
- dense adult-teaching profile with diagram/case/contrast/review card: PASS required
- stable IDs WEN_SHUI, MENTOR_AI, TIAN_AI_XING mapped to the three reference images: PASS required
- full-color, vertical portrait, left-to-right, complete manga page: PASS required
- all visible text in readable Traditional Chinese exactly as supplied: PASS required
- no blank balloons, pseudo-text, extra text, poster layout, merged panels, unrelated people, sexualized framing, watermark, signature, or logo.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Build page-by-page manga image prompts.")
    parser.add_argument("--start-chapter", type=int, default=1)
    parser.add_argument("--end-chapter", type=int, default=5)
    args = parser.parse_args()
    if args.start_chapter < 1 or args.end_chapter < args.start_chapter:
        parser.error("chapter range must be positive and ordered")

    PROMPTS.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    scripts: list[Path] = []
    for script in sorted(SCRIPTS.glob("*.md")):
        text = script.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        chapter = int(fm["chapter"])
        if not args.start_chapter <= chapter <= args.end_chapter:
            continue
        scripts.append(script)
        chapter_title = fm["title"]
        pages = parse_pages(text)
        chapter_dir = PROMPTS / f"ch{chapter:02d}"
        output_dir = GENERATED / f"ch{chapter:02d}"
        chapter_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        previous = "Opening page; establish the reading workshop and the current learning problem."
        for page in pages:
            prompt = build_prompt(chapter, chapter_title, page, previous)
            prompt_path = chapter_dir / f"ch{chapter:02d}-p{page['page']:02d}.txt"
            output_path = output_dir / f"ch{chapter:02d}-p{page['page']:02d}.png"
            prompt_path.write_text(prompt, encoding="utf-8")
            manifest.append({
                "chapter": chapter,
                "chapter_title": chapter_title,
                "page": page["page"],
                "page_title": page["title"],
                "prompt": str(prompt_path).replace("\\", "/"),
                "output": str(output_path).replace("\\", "/"),
                "status": "pending",
                "qa": "prompt-passed",
            })
            previous = f"Previous page taught “{page['title']}” and ended with: {page['hook']}"
    manifest_path = PROMPTS / f"batch-ch{args.start_chapter:02d}-ch{args.end_chapter:02d}.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "chapters": len(scripts),
                "pages": len(manifest),
                "manifest": str(manifest_path),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
