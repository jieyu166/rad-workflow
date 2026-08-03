#!/usr/bin/env python3
"""batch_course.py — 對整個課程資料夾跑完 Task 6 的下游：截圖 → OCR → viewer → 稽核。

一場講座手動跑要四道指令，一個系列十場就是四十道，中間任何一步漏掉都只會在最後看到
半成品。這支把整條鏈包起來，==可重跑==：已經有截圖的跳過抓圖、已經有 OCR 的跳過 OCR，
所以中斷後再跑一次就好，不會重做已完成的工作。

它不做轉錄，也不做分段 JSON——那兩步需要人決定語言與段落切點。開跑前每場都要先有
`<stem>.json`（Task 6 產物）、同名影片與字幕。

用法
  python batch_course.py "<課程資料夾>"
  python batch_course.py "<資料夾>" --force-frames     # 重抓截圖（換了偵測參數時）
  python batch_course.py "<資料夾>" --only 09          # 只跑檔名含 09 的那場
  python batch_course.py "<資料夾>" --skip-ocr         # 只要截圖與 viewer
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
VIDEO_EXT = (".mp4", ".mkv", ".mov", ".webm", ".m4v", ".avi")


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8-sig"))


def lectures(folder: Path, only: str | None) -> list[dict]:
    out = []
    for j in sorted(folder.glob("*.json")):
        if j.name.startswith("_") or j.name.endswith((".frames.json", ".frames_ocr.json")):
            continue
        if only and only not in j.name:
            continue
        try:
            data = load(j)
        except json.JSONDecodeError as e:
            print(f"  [略過] {j.name}：JSON 無法解析（{e}）")
            continue
        segs = data.get("segments")
        if not isinstance(segs, list) or not segs:
            continue
        video = next((p for p in sorted(folder.iterdir())
                      if p.suffix.lower() in VIDEO_EXT and p.stem.startswith(j.stem)), None)
        srt = next((p for p in sorted(folder.glob(j.stem + "*.srt"))
                    if ".raw." not in p.name), None)
        out.append({
            "json": j, "video": video, "srt": srt, "data": data,
            "has_frames": any(s.get("frames") or s.get("frame") for s in segs),
            "has_ocr": any(s.get("frame_ocr") for s in segs),
            "segments": len(segs),
        })
    return out


def run_code(cmd: list[str], label: str) -> int:
    """前景同步跑，把子行程輸出直接透傳——長跑的步驟必須看得到進度。回傳離開碼。"""
    print(f"    $ {label}")
    t0 = time.time()
    r = subprocess.run([sys.executable, *cmd])
    print(f"      ({time.time()-t0:.0f}s, exit={r.returncode})")
    return r.returncode


def run(cmd: list[str], label: str) -> bool:
    return run_code(cmd, label) in (0, 1)  # 1 = 稽核只有警告，不算失敗


def main():
    ap = argparse.ArgumentParser(description="整個課程資料夾跑完截圖/OCR/viewer/稽核")
    ap.add_argument("folder")
    ap.add_argument("--only", help="只跑檔名含此字串的講座")
    ap.add_argument("--width", type=int, default=1280, help="截圖寬度")
    ap.add_argument("--force-frames", action="store_true", help="即使已有截圖也重抓")
    ap.add_argument("--skip-frames", action="store_true")
    ap.add_argument("--skip-ocr", action="store_true")
    ap.add_argument("--skip-viewer", action="store_true")
    args = ap.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"[錯誤] 不是資料夾：{folder}", file=sys.stderr)
        sys.exit(2)

    items = lectures(folder, args.only)
    if not items:
        print("[錯誤] 找不到任何含 segments 的分段 JSON", file=sys.stderr)
        sys.exit(2)

    print(f"課程資料夾：{folder}")
    print(f"找到 {len(items)} 場講座\n" + "=" * 60)
    t_all = time.time()
    report = []
    for i, it in enumerate(items, 1):
        stem = it["json"].stem
        print(f"\n[{i}/{len(items)}] {stem}")
        print(f"    {it['segments']} 段｜影片 {'有' if it['video'] else '無'}"
              f"｜字幕 {'有' if it['srt'] else '無'}"
              f"｜截圖 {'有' if it['has_frames'] else '無'}"
              f"｜OCR {'有' if it['has_ocr'] else '無'}")
        status = []
        if not it["video"]:
            print("    [略過] 沒有對應影片檔")
            report.append((stem, "無影片"))
            continue

        if not args.skip_frames and (args.force_frames or not it["has_frames"]):
            ok = run([str(HERE / "slide_frames.py"), str(it["video"]),
                      "--json", str(it["json"]), "--width", str(args.width)], "slide_frames")
            status.append("截圖" + ("" if ok else "失敗"))
        elif it["has_frames"]:
            status.append("截圖(已有)")

        if not args.skip_ocr:
            fresh = load(it["json"])
            if args.force_frames or not any(s.get("frame_ocr") for s in fresh.get("segments", [])):
                ok = run([str(HERE / "ocr_frames.py"), str(it["json"])], "ocr_frames")
                status.append("OCR" + ("" if ok else "失敗"))
            else:
                status.append("OCR(已有)")

        if not args.skip_viewer:
            cmd = [str(HERE / "build_lecture_viewer.py"), str(it["json"])]
            if it["srt"]:
                cmd += ["--srt", str(it["srt"])]
            cmd += ["--video", str(it["video"])]
            ok = run(cmd, "build_lecture_viewer")
            status.append("viewer" + ("" if ok else "失敗"))

        code = run_code([str(HERE / "check_lecture.py"), str(it["json"])], "check_lecture")
        status.append("稽核" + {0: "通過", 1: "有警告"}.get(code, "有錯"))
        report.append((stem, "、".join(status)))

    print("\n" + "=" * 60)
    print(f"完成 {len(report)} 場，總耗時 {(time.time()-t_all)/60:.1f} 分")
    for stem, s in report:
        print(f"  {stem[:44]:46s} {s}")
    bad = [r for r in report if "失敗" in r[1] or "有錯" in r[1] or "有警告" in r[1] or r[1] == "無影片"]
    if bad:
        print(f"\n需要處理 {len(bad)} 場：" + "、".join(b[0][:24] for b in bad))
    print("\n下一步：python build_course_hub.py \"<資料夾>\"  產生課程首頁")


if __name__ == "__main__":
    main()
