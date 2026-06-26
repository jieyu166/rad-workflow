#!/usr/bin/env python3
"""collect_note_images.py — 把一篇（或多篇）筆記實際「引用到」的圖片，從一堆原始圖中挑出、複製到獨立資料夾。

用途：V4 影片筆記常只嵌入 frames/ 裡眾多截圖的一小部分（例：12 / 155 張）。
要把筆記搬進 Obsidian 時，只需要「用到的那幾張」。本腳本解析筆記中的圖片引用，
複製對應檔到輸出夾，方便連同筆記一起搬。

支援兩種引用語法：
  - Markdown：![alt](frames/xxx.png) 或 ![alt](xxx.png)（路徑可含 %20）
  - Obsidian wikilink：![[xxx.png]]

用法：
  python collect_note_images.py NOTE.v4.md                 # 預設找同層 frames/，輸出到 ./_note_images/
  python collect_note_images.py NOTE.v4.md --frames DIR    # 指定原始圖來源夾
  python collect_note_images.py NOTE.v4.md -o OUTDIR       # 指定輸出夾
  python collect_note_images.py DIR                        # 資料夾內所有 *.v4.md（各自輸出到 OUT/<note-stem>/）
"""
from __future__ import annotations
import argparse, os, re, shutil, sys, urllib.parse
from pathlib import Path

IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif")
PAT = re.compile(r'!\[[^\]]*\]\(([^)]+?)\)|!\[\[([^\]]+?)\]\]')


def refs_in(md_text: str):
    out = []
    for m in PAT.finditer(md_text):
        raw = m.group(1) or m.group(2)
        raw = urllib.parse.unquote(raw.strip())
        if raw.lower().endswith(IMG_EXT):
            out.append(os.path.basename(raw))
    # 去重保序
    return list(dict.fromkeys(out))


def collect(md_path: Path, frames_dir: Path, out_dir: Path) -> tuple[int, list[str]]:
    refs = refs_in(md_path.read_text(encoding="utf-8"))
    out_dir.mkdir(parents=True, exist_ok=True)
    ok, missing = 0, []
    for fn in refs:
        src = frames_dir / fn
        if src.exists():
            shutil.copy2(src, out_dir / fn); ok += 1
        else:
            missing.append(fn)
    return len(refs), missing if missing else []  # noqa


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="筆記 .md，或含多篇 *.v4.md 的資料夾")
    ap.add_argument("--frames", help="原始圖來源夾（預設：筆記同層的 frames/）")
    ap.add_argument("-o", "--out", default="_note_images", help="輸出夾（預設 ./_note_images）")
    args = ap.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"ERROR: 找不到 {target}", file=sys.stderr); sys.exit(1)

    notes = [target] if target.is_file() else sorted(target.glob("*.v4.md"))
    if not notes:
        print("沒有可處理的筆記。"); return

    total = 0
    for md in notes:
        frames_dir = Path(args.frames) if args.frames else (md.parent / "frames")
        out_dir = Path(args.out) if len(notes) == 1 else (Path(args.out) / md.stem.replace(".v4", ""))
        if not frames_dir.is_dir():
            print(f"[skip] {md.name}：找不到來源夾 {frames_dir}"); continue
        n, missing = collect(md, frames_dir, out_dir)
        total += n - len(missing)
        msg = f"[{md.name}] 引用 {n} 張 → 複製 {n - len(missing)} 張到 {out_dir}"
        if missing:
            msg += f"；缺 {len(missing)}：{missing}"
        print(msg)
    print(f"\n合計複製 {total} 張")


if __name__ == "__main__":
    main()
