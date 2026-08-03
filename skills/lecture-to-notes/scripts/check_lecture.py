#!/usr/bin/env python3
"""check_lecture.py — 分段 JSON + V4 筆記的機械稽核。

整條管線之前沒有任何自動檢查，半成品要靠人眼發現：
JSON 併好了但截圖沒抓、改名後筆記引用的圖不存在、時間碼重疊或不單調。
這支腳本把「機器查得出來的錯」一次查完，不做任何內容品質判斷。

檢查項目
  [結構] 必要 key、segments 非空、index 連號
  [時間] start_sec < end_sec、單調遞增、不重疊、start_time/end_time 與秒數一致
  [內容] title / summary_zh 非空；bullets_zh 數量（警告）
  [截圖] 每段至少一張 frame（當該 JSON 已併入截圖時）、frame 檔案實際存在
  [筆記] V4 筆記引用的圖片（Markdown 與 wikilink 兩種寫法）實際存在

用法
  python check_lecture.py "<某.json>"
  python check_lecture.py "<某.json>" --note "<某.v4.md>"
  python check_lecture.py "<資料夾>"                # 批次，自動配對同名 .v4.md
  python check_lecture.py "<資料夾>" --strict       # 警告也算失敗

離開碼：0 全過 / 1 只有警告 / 2 有錯誤
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

VIDEO_EXT = (".mp4", ".mkv", ".mov", ".webm", ".m4v", ".avi")
# 排除非分段 JSON：slide_frames 的 manifest 與底線開頭的暫存
SKIP_JSON = re.compile(r"\.frames\.json$|^_")

MD_IMG = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
WIKI_IMG = re.compile(r"!\[\[([^\]|]+?)(?:\|[^\]]*)?\]\]")
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif")


class Report:
    def __init__(self, label: str):
        self.label = label
        self.errors: list[str] = []
        self.warns: list[str] = []
        self.infos: list[str] = []

    def err(self, msg: str):
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warns.append(msg)

    def info(self, msg: str):
        self.infos.append(msg)

    def print(self):
        mark = "FAIL" if self.errors else ("WARN" if self.warns else "OK")
        print(f"[{mark}] {self.label}")
        for m in self.errors:
            print(f"   ERROR  {m}")
        for m in self.warns:
            print(f"   WARN   {m}")
        for m in self.infos:
            print(f"   info   {m}")


def parse_clock(s) -> float | None:
    """'mm:ss' 或 'hh:mm:ss'（可帶小數秒）-> 秒。無法解析回 None。"""
    if not isinstance(s, str):
        return None
    parts = s.strip().split(":")
    if not 2 <= len(parts) <= 3:
        return None
    try:
        vals = [float(p) for p in parts]
    except ValueError:
        return None
    total = 0.0
    for v in vals:
        total = total * 60 + v
    return total


def check_json(path: Path, rep: Report) -> dict | None:
    raw = path.read_bytes()
    if raw[:3] == b"\xef\xbb\xbf":
        rep.err("檔案有 UTF-8 BOM，web player 會解析失敗（Task 6 規定不得有 BOM）")
        raw = raw[3:]
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        rep.err(f"JSON 無法解析：{e}")
        return None

    for key in ("overall_summary_zh", "takeaways_zh", "segments"):
        if key not in data:
            rep.err(f"缺少必要欄位 {key}")

    summary = data.get("overall_summary_zh", "")
    if isinstance(summary, str) and summary and not 100 <= len(summary) <= 180:
        rep.warn(f"overall_summary_zh {len(summary)} 字（規格 100-180）")

    takeaways = data.get("takeaways_zh")
    if isinstance(takeaways, list) and not 6 <= len(takeaways) <= 12:
        rep.warn(f"takeaways_zh {len(takeaways)} 點（規格 6-12）")

    segs = data.get("segments")
    if not isinstance(segs, list) or not segs:
        rep.err("segments 不存在或為空")
        return data

    check_segments(segs, path.parent, rep)
    return data


def check_segments(segs: list, base: Path, rep: Report):
    prev_end = None
    # 只有「已併入截圖」的 JSON 才要求每段有圖；完全沒圖的是尚未跑 slide_frames，不算錯
    any_frame = any(s.get("frame") or s.get("frames") for s in segs if isinstance(s, dict))

    for i, seg in enumerate(segs, 1):
        tag = f"seg#{i}"
        if not isinstance(seg, dict):
            rep.err(f"{tag} 不是物件")
            continue
        if seg.get("index") != i:
            rep.err(f"{tag} index={seg.get('index')!r}，應為連號 {i}")

        start, end = seg.get("start_sec"), seg.get("end_sec")
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            rep.err(f"{tag} start_sec/end_sec 缺漏或非數值：{start!r} / {end!r}")
        else:
            if start >= end:
                rep.err(f"{tag} start_sec {start} >= end_sec {end}")
            if prev_end is not None:
                if start < prev_end:
                    rep.err(f"{tag} 與前一段重疊（start {start} < 前段 end {prev_end}）")
                elif start - prev_end > 60:
                    rep.warn(f"{tag} 與前一段中間空了 {start - prev_end:.0f} 秒，是否漏段？")
            prev_end = end
            # 時間碼字串與秒數必須一致，否則 web player 與 .pbf 會各跳各的
            for field, sec in (("start_time", start), ("end_time", end)):
                parsed = parse_clock(seg.get(field))
                if parsed is None:
                    rep.err(f"{tag} {field}={seg.get(field)!r} 無法解析為 mm:ss / hh:mm:ss")
                elif abs(parsed - sec) > 1:
                    rep.err(f"{tag} {field}={seg.get(field)} 與 {field[:-5]}_sec={sec} 不符")

        for field in ("title", "summary_zh"):
            if not str(seg.get(field) or "").strip():
                rep.err(f"{tag} {field} 空白")
        bullets = seg.get("bullets_zh")
        if not isinstance(bullets, list) or len(bullets) < 2:
            rep.warn(f"{tag} bullets_zh 少於 2 點（規格 2-6）")

        frames = seg.get("frames") or ([seg["frame"]] if seg.get("frame") else [])
        if any_frame and not frames:
            rep.err(f"{tag} 沒有任何 frame（同一檔其他段有截圖，可能是 slide_frames 沒跑完）")
        for fr in frames:
            if not (base / unquote(str(fr))).exists():
                rep.err(f"{tag} frame 不存在：{fr}")


def check_note(note: Path, rep: Report):
    text = note.read_text(encoding="utf-8", errors="replace")
    base = note.parent
    refs: list[str] = []
    for m in MD_IMG.finditer(text):
        target = unquote(m.group(1).split(" ")[0].strip("<>"))
        if target.lower().endswith(IMG_EXT) and "://" not in target:
            refs.append(target)
    for m in WIKI_IMG.finditer(text):
        target = m.group(1).strip()
        if target.lower().endswith(IMG_EXT):
            refs.append(target)

    if not refs:
        rep.warn(f"{note.name} 沒有引用任何圖片")
        return
    missing = []
    for r in refs:
        # wikilink 只有檔名，依 Obsidian 慣例在筆記同層 / frames / images 找
        if (base / r).exists():
            continue
        name = Path(r).name
        if any((base / sub / name).exists() for sub in ("", "frames", "images")):
            continue
        missing.append(r)
    for r in sorted(set(missing)):
        rep.err(f"{note.name} 引用的圖片不存在：{r}")
    rep.info(f"{note.name} 引用 {len(refs)} 張圖，缺 {len(set(missing))} 張")


def collect_targets(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(p for p in target.iterdir()
                  if p.suffix.lower() == ".json" and not SKIP_JSON.search(p.name))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="分段 JSON 檔或資料夾")
    ap.add_argument("--note", help="要一併檢查的 V4 筆記（單檔模式）")
    ap.add_argument("--strict", action="store_true", help="警告也視為失敗")
    args = ap.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"[FAIL] 路徑不存在：{target}", file=sys.stderr)
        sys.exit(2)

    jsons = collect_targets(target)
    if not jsons:
        print(f"[FAIL] {target} 底下沒有分段 JSON", file=sys.stderr)
        sys.exit(2)

    reports = []
    for j in jsons:
        rep = Report(j.name)
        data = check_json(j, rep)
        if data is not None:
            note = Path(args.note) if args.note else None
            if note is None and target.is_dir():
                stem = j.stem
                cand = j.with_name(f"{stem}.v4.md")
                note = cand if cand.exists() else None
            if note:
                if note.exists():
                    check_note(note, rep)
                else:
                    rep.err(f"指定的筆記不存在：{note}")
        rep.print()
        reports.append(rep)

    n_err = sum(len(r.errors) for r in reports)
    n_warn = sum(len(r.warns) for r in reports)
    print("-" * 44)
    print(f"檢查 {len(reports)} 個檔案：{n_err} 個錯誤、{n_warn} 個警告")
    if n_err:
        sys.exit(2)
    if n_warn:
        sys.exit(2 if args.strict else 1)
    sys.exit(0)


if __name__ == "__main__":
    main()
