#!/usr/bin/env python3
"""json_to_pbf.py — 把 Task 6 分段 JSON 轉成 PotPlayer 章節書籤檔（.pbf）。

PotPlayer 會自動載入與影片「同目錄、同主檔名」的 .pbf，於進度條顯示可點擊章節，
Ctrl+PgUp / PgDn 在章節間跳轉。本腳本用 JSON 各段的 start_sec + title 產生章節。

.pbf 格式（INI，UTF-8）：
    [Bookmark]
    0=<毫秒>*<章節標題>*
    1=<毫秒>*<章節標題>*
（第三段為縮圖二進位，可留空；時間單位毫秒；星號分隔）

用法：
  python json_to_pbf.py <資料夾>                 # 批次：資料夾內所有分段 JSON
  python json_to_pbf.py <某.json>                # 單檔
  python json_to_pbf.py <資料夾> --bom           # 輸出 UTF-8 with BOM（少數版本中文較穩）
  python json_to_pbf.py <某.json> -o out.pbf     # 指定輸出（僅單檔）

規則：
- 自動排除 *.frames.json、以底線開頭（_meta 之類）、以及沒有 segments 的 JSON。
- .pbf 主檔名會「對齊實際影片檔」：若同目錄找到同名或前綴相符的影片
  （.mp4/.mkv/.mov/.webm/.avi/.m4v/.ts），就以影片主檔名命名；找不到才用 JSON 主檔名。
- 標題內的 '*' 會被換成全形 '＊'，避免破壞 .pbf 欄位分隔。
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

VIDEO_EXTS = (".mp4", ".mkv", ".mov", ".webm", ".avi", ".m4v", ".ts")


def match_video_stem(json_path: Path) -> tuple[str, str]:
    """回傳 (輸出主檔名, 說明)。優先對齊同目錄影片檔名。"""
    jstem = json_path.stem
    vids = [p for p in json_path.parent.iterdir()
            if p.is_file() and p.suffix.lower() in VIDEO_EXTS]
    vstems = [p.stem for p in vids]
    # 完全相同 > 前綴相符（任一方為另一方前綴）
    exact = [v for v in vstems if v == jstem]
    if exact:
        return exact[0], "mp4:同名"
    pref = [v for v in vstems if v.startswith(jstem) or jstem.startswith(v)]
    if len(pref) == 1:
        return pref[0], f"mp4:前綴對應({pref[0]})"
    if len(pref) > 1:
        return jstem, f"警告:多個影片前綴相符{pref}，改用JSON主檔名"
    return jstem, "無同名影片，用JSON主檔名"


def json_to_pbf_lines(data: dict) -> list[str]:
    segs = data.get("segments") or []
    lines = ["[Bookmark]"]
    for i, s in enumerate(segs):
        ms = int(round(float(s["start_sec"]) * 1000))
        title = str(s.get("title", "")).replace("*", "＊").replace("\n", " ").strip()
        lines.append(f"{i}={ms}*{title}*")
    return lines


def convert_one(json_path: Path, out: Path | None, bom: bool) -> str | None:
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        return f"[skip] {json_path.name} 解析失敗：{e}"
    segs = data.get("segments") or []
    if not segs:
        return f"[skip] {json_path.name} 無 segments"
    if out is None:
        out_stem, note = match_video_stem(json_path)
        out = json_path.parent / (out_stem + ".pbf")
    else:
        note = "指定輸出"
    text = "\n".join(json_to_pbf_lines(data)) + "\n"
    enc = "utf-8-sig" if bom else "utf-8"
    out.write_text(text, encoding=enc, newline="\n")
    return f"[ok] {out.name}  {len(segs)} 章  ({note})"


def iter_jsons(target: Path):
    if target.is_file():
        yield target
        return
    for p in sorted(target.glob("*.json")):
        if p.name.endswith(".frames.json") or p.name.startswith("_"):
            continue
        yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="分段 JSON 檔，或含多個 JSON 的資料夾")
    ap.add_argument("-o", "--out", help="輸出 .pbf 路徑（僅單檔有效）")
    ap.add_argument("--bom", action="store_true", help="輸出 UTF-8 with BOM")
    args = ap.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"ERROR: 找不到 {target}", file=sys.stderr)
        sys.exit(1)

    jsons = list(iter_jsons(target))
    if not jsons:
        print("沒有可處理的分段 JSON（已排除 *.frames.json 與 _ 開頭）。")
        return
    if args.out and len(jsons) > 1:
        print("ERROR: -o 只能用於單一 JSON 檔。", file=sys.stderr)
        sys.exit(1)

    done = 0
    for jp in jsons:
        msg = convert_one(jp, Path(args.out) if args.out else None, args.bom)
        print(msg)
        if msg and msg.startswith("[ok]"):
            done += 1
    print(f"\n完成 {done}/{len(jsons)} 個 .pbf")


if __name__ == "__main__":
    main()
