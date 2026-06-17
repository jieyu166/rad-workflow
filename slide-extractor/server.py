"""Local HTTP server for reviewing/exporting detected slides (rebuilt 2026-05-28).

Endpoints:
  GET  /                → index.html (slide review UI)
  GET  /api/videos      → list .mp4 / .mkv in cwd
  GET  /api/frames?video=NAME[&detector=...&threshold=...&min_scene_len=...]
                        → detect slides, generate thumbnails into _thumbs/,
                          return JSON list
  POST /api/export      → body: {"video": "...", "timestamps": [sec,...],
                                  "output_dir": "output", "width": 1920}
                        → export full-res PNGs

Rebuilt from .pyc strings + standard library only (http.server, json, os).
"""
from __future__ import annotations

import http.server
import json
import os
import socket
import socketserver
import sys
import threading
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

# Local detector
sys.path.insert(0, str(Path(__file__).parent))
from detector import detect_scenes, extract_frame, get_video_duration  # noqa: E402

BASE_DIR = Path(__file__).parent.resolve()
THUMBS_DIR = BASE_DIR / "_thumbs"
OUTPUT_DIR = BASE_DIR / "output"
THUMB_WIDTH = 320

VIDEO_EXTS = (".mp4", ".mkv", ".mov", ".avi", ".webm")


class SlideHandler(http.server.BaseHTTPRequestHandler):
    server_version = "slide-extractor/1.0"

    # ---- routing ----
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/" or u.path == "/index.html":
            return self._serve_file(BASE_DIR / "index.html", "text/html; charset=utf-8")
        if u.path.startswith("/_thumbs/"):
            # u.path 是 percent-encoded（中文檔名會變 %E7%AC%AC...），需手動 decode
            decoded = unquote(u.path)
            return self._serve_file(BASE_DIR / decoded.lstrip("/"), "image/png")
        if u.path == "/api/videos":
            return self._handle_list_videos()
        if u.path == "/api/frames":
            return self._handle_get_frames(parse_qs(u.query))
        return self._send(404, b"Not Found", "text/plain")

    def do_POST(self):
        u = urlparse(self.path)
        if u.path == "/api/export":
            return self._handle_export()
        return self._send(404, b"Not Found", "text/plain")

    def log_message(self, format, *args):  # quieter
        sys.stderr.write(f"  {self.address_string()} - {format % args}\n")

    # ---- handlers ----
    def _handle_list_videos(self):
        videos = sorted(
            f.name for f in BASE_DIR.iterdir()
            if f.is_file() and f.suffix.lower() in VIDEO_EXTS
        )
        self._json({"videos": videos})

    def _handle_get_frames(self, qs):
        video = qs.get("video", [""])[0]
        detector = qs.get("detector", ["adaptive"])[0]
        try:
            threshold = float(qs["threshold"][0]) if qs.get("threshold") else None
        except (TypeError, ValueError):
            threshold = None
        try:
            min_scene_len = float(qs.get("min_scene_len", ["1.5"])[0])
        except ValueError:
            min_scene_len = 1.5

        video_path = BASE_DIR / unquote(video)
        if not video_path.exists() or video_path.suffix.lower() not in VIDEO_EXTS:
            return self._json({"error": "video not found"}, status=404)

        try:
            scenes = detect_scenes(str(video_path), detector, threshold, min_scene_len)
        except Exception as e:
            return self._json({"error": f"detect failed: {e}"}, status=500)

        # Generate thumbnails (skip if already exists)
        THUMBS_DIR.mkdir(exist_ok=True)
        for s in scenes:
            thumb_name = f"{video_path.stem}-{s['timestamp_file']}.png"
            thumb_path = THUMBS_DIR / thumb_name
            if not thumb_path.exists():
                extract_frame(str(video_path), s["timestamp_sec"], str(thumb_path), width=THUMB_WIDTH)
            s["thumb"] = f"/_thumbs/{thumb_name}"

        duration = get_video_duration(str(video_path))
        self._json({
            "video": video,
            "duration": duration,
            "duration_display": _fmt_dur(duration),
            "detector": detector,
            "frames": scenes,
        })

    def _handle_export(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))
        except Exception as e:
            return self._json({"error": f"bad body: {e}"}, status=400)

        video = data.get("video", "")
        timestamps = data.get("timestamps", []) or []
        out_dir_name = data.get("output_dir", "output")
        width = data.get("width") or None

        video_path = BASE_DIR / unquote(video)
        if not video_path.exists():
            return self._json({"error": "video not found"}, status=404)

        out_dir = BASE_DIR / out_dir_name
        out_dir.mkdir(parents=True, exist_ok=True)

        exported = []
        for ts in timestamps:
            try:
                sec = float(ts)
            except (TypeError, ValueError):
                continue
            fn = f"{video_path.stem}-{_fmt_file(sec)}.png"
            target = out_dir / fn
            ok = extract_frame(str(video_path), sec, str(target), width=width)
            if ok:
                exported.append(fn)
        print(f"  Exported {len(exported)} frame(s) to: {out_dir}")
        self._json({"exported_count": len(exported), "exported": exported, "directory": str(out_dir)})

    # ---- helpers ----
    def _serve_file(self, path: Path, content_type: str):
        if not path.exists() or not path.is_file():
            return self._send(404, b"Not Found", "text/plain")
        data = path.read_bytes()
        self._send(200, data, content_type)

    def _json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _send(self, status: int, body: bytes, content_type: str):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if body:
            self.wfile.write(body)


def _fmt_dur(sec: float) -> str:
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = int(sec % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _fmt_file(sec: float) -> str:
    m = int(sec // 60); s = int(sec % 60)
    return f"{m:02d}{s:02d}"


def find_available_port(start=8000, end=8050):
    for p in range(start, end):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", p))
            return p
        except OSError:
            continue
    raise RuntimeError(f"[Error] Cannot find available port ({start}-{end})")


def run(host="127.0.0.1", port=None):
    port = port or find_available_port()
    THUMBS_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    httpd = socketserver.ThreadingTCPServer((host, port), SlideHandler)
    httpd.daemon_threads = True
    print(f"  Server running at: http://{host}:{port}/")
    print(f"  Working directory: {BASE_DIR}")
    print("  Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down...")
        httpd.shutdown()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    run(host=args.host, port=args.port)
