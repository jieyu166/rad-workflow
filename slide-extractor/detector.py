"""Slide change detection from video (rebuilt 2026-05-28).

Wraps PySceneDetect (preferred) with ffmpeg scene-detect as fallback.
Detects scene boundaries (slide transitions) and returns timestamp metadata.

Original detector.py was lost; rebuilt from .pyc strings + PySceneDetect API.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Optional


def detect_scenes(
    video_path: str,
    detector_type: str = "adaptive",
    threshold: Optional[float] = None,
    min_scene_len: float = 1.5,
) -> List[Dict]:
    """Detect scene boundaries in a video.

    Args:
        video_path: Path to video file.
        detector_type: 'adaptive', 'content', or 'ffmpeg'.
        threshold: Detection threshold (type-dependent). None = use defaults.
        min_scene_len: Minimum scene length in seconds.

    Returns:
        List of dicts with timestamp_sec, timestamp_display, timestamp_file.
        Each dict represents the START of a detected slide.
    """
    if detector_type == "ffmpeg":
        return detect_scenes_ffmpeg(video_path, threshold or 0.3)
    return detect_scenes_scenedetect(
        video_path, detector_type=detector_type,
        threshold=threshold, min_scene_len=min_scene_len,
    )


def detect_scenes_scenedetect(
    video_path: str,
    detector_type: str = "adaptive",
    threshold: Optional[float] = None,
    min_scene_len: float = 1.5,
) -> List[Dict]:
    """Detect scenes using PySceneDetect.

    detector_type: 'adaptive' or 'content'.
    threshold: Scene change threshold (type-dependent). Lower = more sensitive.
    """
    try:
        from scenedetect import SceneManager, open_video
        from scenedetect.detectors import AdaptiveDetector, ContentDetector
    except ImportError as e:
        raise RuntimeError(
            "PySceneDetect not installed. `pip install scenedetect[opencv]` "
            "or use detector_type='ffmpeg'."
        ) from e

    video = open_video(video_path)
    fps = video.frame_rate
    min_scene_len_frames = max(int(round(min_scene_len * fps)), 1)

    sm = SceneManager()
    if detector_type == "content":
        thr = threshold if threshold is not None else 27.0
        sm.add_detector(ContentDetector(threshold=thr, min_scene_len=min_scene_len_frames))
    else:  # adaptive (default)
        thr = threshold if threshold is not None else 3.0
        sm.add_detector(AdaptiveDetector(adaptive_threshold=thr, min_scene_len=min_scene_len_frames))

    sm.detect_scenes(video=video)
    scene_list = sm.get_scene_list()

    results = []
    for start, _end in scene_list:
        sec = start.get_seconds()
        results.append({
            "timestamp_sec": round(sec, 3),
            "timestamp_display": _fmt_display(sec),
            "timestamp_file": _fmt_file(sec),
        })
    # Always include t=0 (first frame) if not present
    if not results or results[0]["timestamp_sec"] > 0.5:
        results.insert(0, {
            "timestamp_sec": 0.0,
            "timestamp_display": "00:00:00",
            "timestamp_file": "0000",
        })
    return results


def detect_scenes_ffmpeg(video_path: str, threshold: float = 0.3) -> List[Dict]:
    """Fallback: ffmpeg `select='gt(scene,threshold)'` filter.

    threshold: 0.0-1.0. Lower = more sensitive (more cuts).
    Requires ffmpeg on PATH.
    """
    cmd = [
        "ffmpeg", "-hide_banner", "-i", video_path,
        "-filter:v", f"select='gt(scene,{threshold})',showinfo",
        "-f", "null", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    # showinfo prints "pts_time:NNN.NNN" per matching frame on stderr
    pattern = re.compile(r"pts_time:([\d.]+)")
    results = [{
        "timestamp_sec": 0.0,
        "timestamp_display": "00:00:00",
        "timestamp_file": "0000",
    }]
    for line in proc.stderr.splitlines():
        m = pattern.search(line)
        if m:
            sec = float(m.group(1))
            results.append({
                "timestamp_sec": round(sec, 3),
                "timestamp_display": _fmt_display(sec),
                "timestamp_file": _fmt_file(sec),
            })
    return results


def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds (via ffprobe)."""
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", video_path]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8").stdout.strip()
        return float(out)
    except Exception:
        return 0.0


def extract_frame(video_path: str, timestamp_sec: float, output_path: str,
                  width: Optional[int] = None) -> bool:
    """Extract a single frame at the given timestamp using ffmpeg.

    width: optional resize width (keeps aspect). None = original.
    Returns True on success.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
           "-ss", f"{timestamp_sec:.3f}", "-i", video_path, "-vframes", "1"]
    if width:
        cmd += ["-vf", f"scale={width}:-1"]
    cmd += [output_path]
    proc = subprocess.run(cmd, capture_output=True)
    return proc.returncode == 0 and os.path.exists(output_path)


def _fmt_display(sec: float) -> str:
    """Seconds → HH:MM:SS for display."""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _fmt_file(sec: float) -> str:
    """Seconds → MMSS for filename (4 digits)."""
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02d}{s:02d}"


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--detector", default="adaptive", choices=["adaptive", "content", "ffmpeg"])
    ap.add_argument("--threshold", type=float)
    ap.add_argument("--min-scene-len", type=float, default=1.5)
    args = ap.parse_args()
    dur = get_video_duration(args.video)
    print(f"Video duration: {_fmt_display(dur)} ({dur:.1f}s)")
    scenes = detect_scenes(args.video, args.detector, args.threshold, args.min_scene_len)
    print(f"Detected {len(scenes)} scene(s):")
    for s in scenes:
        print(f"  {s['timestamp_display']}  ({s['timestamp_sec']:.2f}s)  file={s['timestamp_file']}")
