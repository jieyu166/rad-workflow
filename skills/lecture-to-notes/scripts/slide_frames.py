#!/usr/bin/env python3
"""slide_frames.py — 從影片自動抓「換頁截圖」，供 Task 4/Task 6 使用。

設計（2026-06-24 新增）：
  Task 4/6 原本依賴「使用者預先手動備好的投影片截圖資料夾」。本 helper 直接從
  影片檔用『場景偵測』抓真正換頁的那一張，補掉手動那一步。偵測邏輯鏡像專案內
  slide-extractor（PySceneDetect adaptive，無則退 ffmpeg scene filter），但自
  足、不硬綁 slide-extractor 路徑，保持技能可攜。

輸出：
  1. <video_dir>/frames/<stem>-<MMSS>.png   每個換頁點一張（預設 1280px 寬）
  2. <video_dir>/<stem>.frames.json         frame 清單（含 timestamp_sec / display / file / frame 相對路徑）
  3. 若給 --json SEGMENTS.json：把每個 frame 依時間併入對應 segment
        segment["frames"] = [該段時間範圍內的所有換頁截圖]
        segment["frame"]  = 代表圖（該段第一張；若該段無換頁則取「段落開始時螢幕上那張」=前一張）
     就地寫回（或 --json-out 另存）。

用法：
  python slide_frames.py VIDEO.mp4
  python slide_frames.py VIDEO.mp4 --json lecture.json            # 併入分段 JSON
  python slide_frames.py VIDEO.mp4 --width 1920 --detector content --threshold 27
  python slide_frames.py VIDEO.mp4 --detector ffmpeg --threshold 0.3   # 無 PySceneDetect 時

依賴：ffmpeg / ffprobe（必）；PySceneDetect（adaptive/content 模式）。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional


# ─────────── 場景偵測（鏡像 slide-extractor/detector.py）───────────
def detect_scenes(video_path: str, detector_type: str = "adaptive",
                  threshold: Optional[float] = None, min_scene_len: float = 1.5) -> List[Dict]:
    if detector_type == "ffmpeg":
        return _detect_ffmpeg(video_path, threshold or 0.3)
    try:
        from scenedetect import SceneManager, open_video
        from scenedetect.detectors import AdaptiveDetector, ContentDetector
    except ImportError:
        print("  (PySceneDetect 未安裝 → 改用 ffmpeg scene filter)", file=sys.stderr)
        return _detect_ffmpeg(video_path, 0.3)

    video = open_video(video_path)
    fps = video.frame_rate
    msl = max(int(round(min_scene_len * fps)), 1)
    sm = SceneManager()
    if detector_type == "content":
        sm.add_detector(ContentDetector(threshold=threshold if threshold is not None else 27.0, min_scene_len=msl))
    else:
        sm.add_detector(AdaptiveDetector(adaptive_threshold=threshold if threshold is not None else 3.0, min_scene_len=msl))
    sm.detect_scenes(video=video)
    out = []
    for start, _end in sm.get_scene_list():
        out.append(_mk(start.get_seconds()))
    if not out or out[0]["timestamp_sec"] > 0.5:
        out.insert(0, _mk(0.0))
    return out


def _detect_ffmpeg(video_path: str, threshold: float = 0.3) -> List[Dict]:
    cmd = ["ffmpeg", "-hide_banner", "-i", video_path,
           "-filter:v", f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = [_mk(0.0)]
    for line in proc.stderr.splitlines():
        m = re.search(r"pts_time:([\d.]+)", line)
        if m:
            out.append(_mk(float(m.group(1))))
    return out


def _mk(sec: float) -> Dict:
    sec = round(sec, 3)
    h, m, s = int(sec // 3600), int((sec % 3600) // 60), int(sec % 60)
    return {"timestamp_sec": sec, "timestamp_display": f"{h:02d}:{m:02d}:{s:02d}",
            "timestamp_file": f"{int(sec // 60):02d}{int(sec % 60):02d}"}


def get_duration(video_path: str) -> float:
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", video_path]
    try:
        return float(subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8").stdout.strip())
    except Exception:
        return 0.0


def extract_frame(video_path: str, sec: float, out_path: str, width: int = 1280) -> bool:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-ss", f"{sec:.3f}", "-i", video_path, "-vframes", "1",
           "-vf", f"scale={width}:-1", out_path]
    subprocess.run(cmd, capture_output=True)
    return os.path.exists(out_path)


def find_video(base: Path) -> Optional[Path]:
    """Given an SRT/JSON base path, find a same-stem video file beside it."""
    stem = base.stem
    # strip common subtitle suffixes (.zh, .en, .zh-TW)
    stem = re.sub(r"\.(zh(-TW)?|en|orig)$", "", stem)
    for ext in (".mp4", ".mkv", ".mov", ".webm", ".avi", ".m4v"):
        for cand in (base.parent / f"{stem}{ext}", base.parent / f"{base.stem}{ext}"):
            if cand.exists():
                return cand
    return None


def main():
    ap = argparse.ArgumentParser(description="抓換頁截圖並（可選）併入分段 JSON")
    ap.add_argument("video", help="影片檔（.mp4/.mkv/...）")
    ap.add_argument("--json", help="Task 6 分段 JSON，將把 frame 併入各 segment")
    ap.add_argument("--json-out", help="併入後另存路徑（預設就地寫回 --json）")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--detector", default="adaptive", choices=["adaptive", "content", "ffmpeg"])
    ap.add_argument("--threshold", type=float)
    ap.add_argument("--min-scene-len", type=float, default=1.5)
    ap.add_argument("--out-dir", help="截圖輸出資料夾（預設 <影片同層>/frames）")
    args = ap.parse_args()

    video = Path(args.video)
    if not video.exists():
        print(f"ERROR: 影片不存在 {video}", file=sys.stderr); sys.exit(1)
    out_dir = Path(args.out_dir) if args.out_dir else video.parent / "frames"
    stem = re.sub(r"\.(zh(-TW)?|en|orig)$", "", video.stem)

    dur = get_duration(str(video))
    print(f"影片長度 {_mk(dur)['timestamp_display']} ({dur:.0f}s)；偵測換頁（{args.detector}）...")
    scenes = detect_scenes(str(video), args.detector, args.threshold, args.min_scene_len)
    print(f"偵測到 {len(scenes)} 個換頁點，抓圖 @ {args.width}px ...")

    frames = []
    for sc in scenes:
        fname = f"{stem}-{sc['timestamp_file']}.png"
        fpath = out_dir / fname
        # seek 比換頁點晚 0.4s，避開過場動畫/淡入
        if extract_frame(str(video), sc["timestamp_sec"] + 0.4, str(fpath), args.width):
            rel = os.path.relpath(fpath, video.parent).replace("\\", "/")
            frames.append({**sc, "frame": rel, "filename": fname})
    print(f"  完成 {len(frames)} 張 → {out_dir}")

    # frame 清單 manifest
    manifest = video.parent / f"{stem}.frames.json"
    manifest.write_text(json.dumps(frames, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  manifest → {manifest.name}")

    # 併入分段 JSON
    if args.json:
        jp = Path(args.json)
        data = json.loads(jp.read_text(encoding="utf-8"))
        segs = data.get("segments", [])
        for seg in segs:
            s0, s1 = seg.get("start_sec", 0), seg.get("end_sec", 10**9)
            inside = [f["frame"] for f in frames if s0 <= f["timestamp_sec"] < s1]
            seg["frames"] = inside
            if inside:
                seg["frame"] = inside[0]
            else:
                # 該段無換頁 → 取段落開始時「螢幕上那張」（最近的前一張）
                prior = [f for f in frames if f["timestamp_sec"] <= s0]
                seg["frame"] = prior[-1]["frame"] if prior else (frames[0]["frame"] if frames else None)
        outp = Path(args.json_out) if args.json_out else jp
        outp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        covered = sum(1 for s in segs if s.get("frames"))
        print(f"  併入 {len(segs)} 段（{covered} 段含換頁）→ {outp.name}")


if __name__ == "__main__":
    main()
