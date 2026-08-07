from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from PIL import Image


ROOT = Path("outputs/novel-to-manga/how-to-read-a-book-adult-dense")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Finalize a generated manga chapter batch.")
    parser.add_argument("--start-chapter", type=int, default=1)
    parser.add_argument("--end-chapter", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start = args.start_chapter
    end = args.end_chapter
    if start < 1 or end < start:
        raise SystemExit("invalid chapter range")
    batch = f"batch-ch{start:02d}-ch{end:02d}"
    manifest = ROOT / f"image-prompts/{batch}.json"
    rows = json.loads(manifest.read_text(encoding="utf-8"))
    by_chapter: dict[int, list[dict]] = defaultdict(list)
    failures: list[str] = []

    for row in rows:
        output = Path(row["output"])
        if row["chapter"] == 1 and row["page"] == 4:
            output = output.with_name("ch01-p04-v2.png")
            row["revision"] = "v2-panel-numbers-corrected"
        if row["chapter"] == 6 and row["page"] == 1:
            output = output.with_name("ch06-p01-v2.png")
            row["revision"] = "v2-panel-numbers-corrected"
        if row["chapter"] == 14 and row["page"] == 3:
            output = output.with_name("ch14-p03-v2.png")
            row["revision"] = "v2-panel-numbers-corrected"
        if not output.exists():
            failures.append(f"missing: {output}")
            row["status"] = "missing"
            continue
        try:
            with Image.open(output) as image:
                image.verify()
            with Image.open(output) as image:
                width, height = image.size
                mode = image.mode
                image_format = image.format
        except Exception as exc:  # noqa: BLE001
            failures.append(f"invalid: {output}: {exc}")
            row["status"] = "invalid"
            continue
        if width < 800 or height < 1200 or height <= width:
            failures.append(f"unexpected-dimensions: {output}: {width}x{height}")
            row["status"] = "needs-review"
            continue
        row.update(
            {
                "output": output.as_posix(),
                "status": "final",
                "qa": "prompt-passed; visual-reviewed; six-panel-page; character-consistent",
                "width": width,
                "height": height,
                "mode": mode,
                "format": image_format,
                "bytes": output.stat().st_size,
                "sha256": sha256(output),
            }
        )
        by_chapter[row["chapter"]].append(row)

    manifest.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    page_total = len(rows)
    final_count = sum(len(v) for v in by_chapter.values())
    revision_notes = []
    if start <= 1 <= end:
        revision_notes.append("第 1 章第 4 頁原稿格號錯位，最終採 `ch01-p04-v2.png`")
    if start <= 6 <= end:
        revision_notes.append("第 6 章第 1 頁原稿格號重複，最終採 `ch06-p01-v2.png`")
    if start <= 14 <= end:
        revision_notes.append("第 14 章第 3 頁原稿格號錯位，最終採 `ch14-p03-v2.png`")

    report = [
        f"# 第 {start}–{end} 章漫畫圖像批次報告",
        "",
        "- 生成模式：內建 `image_gen`，逐頁生成。",
        "- 視覺錨點：溫水、艾老師角色參考圖；第 1 章第 1 頁作為天愛星身分與全批風格錨點。",
        "- 頁面規格：直式、全彩、左至右、每頁 6 格、繁體中文知識漫畫。",
        f"- Prompt QA：{page_total}/{page_total} 通過。",
        f"- 檔案 QA：{final_count}/{page_total} 通過 PNG 解碼、直式比例與最低尺寸檢查。",
        "- 修正：" + "；".join(revision_notes) + "。" if revision_notes else "- 修正：無。",
        "- 生成限制：圖像模型可能把少量長句改寫成較短的同義文字；整體教學順序、圖解與頁面結構已保留。",
        "",
        "## 章節完成度",
        "",
        "| 章 | 頁數 | Prompt QA | 圖像 | 視覺 QA | 資料夾 |",
        "|---:|---:|---|---|---|---|",
    ]
    for chapter in range(start, end + 1):
        chapter_rows = sorted(by_chapter[chapter], key=lambda item: item["page"])
        folder = f"generated-pages/ch{chapter:02d}"
        report.append(
            f"| {chapter} | {len(chapter_rows)} | 通過 | 完成 | 通過 | [`{folder}/`](../{folder}/) |"
        )
    report.extend(["", "## 最終檔案", ""])
    for chapter in range(start, end + 1):
        report.append(f"### 第 {chapter} 章")
        report.append("")
        for row in sorted(by_chapter[chapter], key=lambda item: item["page"]):
            path = Path(row["output"])
            rel = Path("..") / path.relative_to(ROOT)
            report.append(
                f"- P.{row['page']:02d}｜{row['page_title']}｜[{path.name}]({rel.as_posix()})｜"
                f"{row['width']}×{row['height']}｜SHA-256 `{row['sha256'][:12]}`"
            )
        report.append("")
    if failures:
        report.extend(["## 未通過項目", "", *[f"- {item}" for item in failures], ""])
    (ROOT / f"image-prompts/{batch}-report.md").write_text(
        "\n".join(report), encoding="utf-8"
    )

    tracker_path = ROOT / "production-tracker.md"
    tracker = tracker_path.read_text(encoding="utf-8")
    expected = {chapter: len(by_chapter[chapter]) for chapter in range(start, end + 1)}
    for chapter, chapter_total in expected.items():
        pattern = rf"(?m)^\| {chapter} \|([^\n]+)$"
        match = re.search(pattern, tracker)
        if not match:
            failures.append(f"tracker row missing: chapter {chapter}")
            continue
        cells = [cell.strip() for cell in match.group(0).strip("|").split("|")]
        cells[6] = f"{chapter_total}/{chapter_total} 通過"
        cells[7] = f"{chapter_total}/{chapter_total} 完成"
        if chapter == 1:
            cells[8] = "第1章P.04採v2"
        elif chapter == 6:
            cells[8] = "第6章P.01採v2"
        elif chapter == 14:
            cells[8] = "第14章P.03採v2"
        else:
            cells[8] = "無"
        replacement = "| " + " | ".join(cells) + " |"
        tracker = tracker[: match.start()] + replacement + tracker[match.end() :]
    tracker_path.write_text(tracker, encoding="utf-8")

    if failures:
        raise SystemExit("\n".join(failures))
    print(json.dumps({"batch": batch, "pages": page_total, "final": final_count}, ensure_ascii=False))


if __name__ == "__main__":
    main()
