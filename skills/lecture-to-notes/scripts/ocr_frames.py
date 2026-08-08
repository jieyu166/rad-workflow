#!/usr/bin/env python3
"""ocr_frames.py — 把換頁截圖的 OCR 文字併回 Task 6 分段 JSON。

`slide_frames.py` 讓每段有了 `frame`/`frames`，但寫 V4 筆記時仍得逐張 Read 圖才知道
投影片上寫了什麼；長片（100+ 張）光讀圖就吃掉大量往返。這支腳本先把每張截圖 OCR 一次、
結果寫進 segment，之後寫筆記直接讀 JSON 就有該段投影片的文字。

==OCR 文字是「定位用的線索」，不是 ground truth。== Task 4/6 的來源優先序不變：
官方講義 > 投影片截圖（人眼看的）> ASR 逐字稿。OCR 會把 Lung-RADS 讀成 LungRADS、
把數值讀錯、把表格讀成一串亂序文字。用它決定「這段在講哪張投影片、大概講什麼」，
術語與數值仍要回頭看圖或對講義。

輸出
  1. `<stem>.frames_ocr.json`  每張截圖的 OCR 快取（含檔案大小指紋，重跑只補新圖）
  2. 併入分段 JSON：每個 segment 加 `frame_ocr`（[{frame, text}]）與頂層 `ocr_meta`

用法
  python ocr_frames.py "<分段.json>"                  # 依 JSON 內的 frames 逐張 OCR
  python ocr_frames.py "<分段.json>" --force          # 忽略快取全部重跑
  python ocr_frames.py "<分段.json>" --min-conf 0.7   # 丟掉低信心行（預設 0.5）
  python ocr_frames.py "<frames 資料夾>" --no-merge   # 只建快取，不動 JSON
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")
ENGINE = "rapidocr-onnxruntime"


# 線上會議錄影的畫面上永遠有一層工具列，OCR 會把它當成投影片內容讀進來。
# 實測一批 Zoom 錄影：6880 行 OCR 裡 543 行（7.9%）是這種雜訊，而且 OCR 每次
# 拼錯的方式都不同（螢幕→蜜幕/童幕/瑩幕/策幕/蟹幕），所以用模糊樣式而不是字串清單。
# 這些字會讓跨場搜尋每一張投影片都命中，等於把搜尋廢掉。
UI_NOISE = [
    re.compile(r"正在[觀翻檢][看著].{0,4}[幕募]"),      # 您正在觀看○○的螢幕
    re.compile(r"檢[視祝現].{0,2}[選避逛]項"),           # 檢視選項
    re.compile(r"^\W{0,2}(REC|EC)\W{0,2}$", re.I),      # 錄影指示燈
    re.compile(r"分享音訊.{0,6}靜音"),                    # 注意：當分享音訊時您將自被靜音
    re.compile(r"^(靜音|取消靜音|停止視訊|參加者|聊天|分享畫面|結束會議)$"),
]


def strip_ui(text: str) -> str:
    """去掉會議軟體工具列的文字。整行比對，不動投影片本身的內容。"""
    keep = [ln for ln in text.split(chr(10))
            if ln.strip() and not any(rx.search(ln.strip()) for rx in UI_NOISE)]
    return chr(10).join(keep)


def load_engine():
    """缺套件就大聲失敗，不要默默跳過——沉默降級會產出「少了東西但看起來正常」的 JSON。"""
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        print("[錯誤] 找不到 rapidocr-onnxruntime，無法做 OCR。", file=sys.stderr)
        print("  pip install rapidocr-onnxruntime", file=sys.stderr)
        print("  （CPU 版即可，自帶中英 PP-OCR 模型，不需要另外下載）", file=sys.stderr)
        sys.exit(3)
    return RapidOCR()


def load_s2t(enabled: bool):
    """OCR 模型常把繁體字讀成簡體（結->结）。轉繁只是讓文字更好比對講義，
    不會讓辨識更準——錯字還是錯字。"""
    if not enabled:
        return None
    try:
        from opencc import OpenCC
        return OpenCC("s2twp").convert
    except ImportError:
        print("  (opencc 未安裝 -> OCR 文字保持原樣；pip install opencc-python-reimplemented)",
              file=sys.stderr)
        return None


def fingerprint(p: Path) -> str:
    st = p.stat()
    return f"{st.st_size}:{int(st.st_mtime)}"


def ocr_one(engine, path: Path, min_conf: float) -> str:
    result, _ = engine(str(path))
    if not result:
        return ""
    lines = []
    for item in result:
        # RapidOCR 回 [box, text, score]
        if len(item) < 3:
            continue
        text, score = str(item[1]).strip(), float(item[2])
        if text and score >= min_conf:
            lines.append(text)
    return "\n".join(lines)


def collect_frames(target: Path, data: dict | None) -> list[str]:
    """回傳相對於 base 的截圖路徑清單（去重、保持出現順序）。"""
    seen, out = set(), []
    if data is not None:
        for seg in data.get("segments", []):
            if not isinstance(seg, dict):
                continue
            frames = seg.get("frames") or ([seg["frame"]] if seg.get("frame") else [])
            for fr in frames:
                fr = str(fr)
                if fr not in seen:
                    seen.add(fr)
                    out.append(fr)
    else:
        for p in sorted(target.iterdir()):
            if p.suffix.lower() in IMG_EXT:
                out.append(f"{target.name}/{p.name}")
    return out


def main():
    ap = argparse.ArgumentParser(description="把換頁截圖的 OCR 文字併回分段 JSON")
    ap.add_argument("target", help="Task 6 分段 JSON，或 frames 資料夾")
    ap.add_argument("--min-conf", type=float, default=0.5, help="低於此信心的行丟棄（預設 0.5）")
    ap.add_argument("--force", action="store_true", help="忽略快取，全部重新 OCR")
    ap.add_argument("--no-merge", action="store_true", help="只建 OCR 快取，不寫回分段 JSON")
    ap.add_argument("--cache", help="快取檔路徑（預設 <stem>.frames_ocr.json）")
    ap.add_argument("--no-s2t", action="store_true", help="不把 OCR 文字轉繁體")
    ap.add_argument("--keep-ui", action="store_true",
                    help="保留會議軟體工具列文字（預設濾掉：檢視選項／正在觀看○○的螢幕／REC）")
    args = ap.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"[錯誤] 路徑不存在：{target}", file=sys.stderr)
        sys.exit(2)

    if target.is_dir():
        base, data, json_path = target.parent, None, None
        stem = target.name
    else:
        json_path = target
        base = target.parent
        stem = target.stem
        data = json.loads(target.read_text(encoding="utf-8-sig"))

    frames = collect_frames(target, data)
    if not frames:
        print("[錯誤] 沒有任何截圖可以 OCR（先跑 slide_frames.py？）", file=sys.stderr)
        sys.exit(2)

    cache_path = Path(args.cache) if args.cache else base / f"{stem}.frames_ocr.json"
    cache = {}
    if cache_path.exists() and not args.force:
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  (快取 {cache_path.name} 壞了，重建)", file=sys.stderr)

    s2t = load_s2t(not args.no_s2t)
    engine = None
    todo = []
    for fr in frames:
        p = base / unquote(fr)
        if not p.exists():
            print(f"  [略過] 檔案不存在：{fr}")
            continue
        hit = cache.get(fr)
        if hit and not args.force and hit.get("fingerprint") == fingerprint(p):
            continue
        todo.append((fr, p))

    print(f"截圖 {len(frames)} 張，需要 OCR {len(todo)} 張"
          f"（{len(frames) - len(todo)} 張命中快取）")
    if todo:
        engine = load_engine()
        t0 = time.time()
        for i, (fr, p) in enumerate(todo, 1):
            text = ocr_one(engine, p, args.min_conf)
            if s2t:
                text = s2t(text)
            if not args.keep_ui:
                text = strip_ui(text)
            cache[fr] = {"fingerprint": fingerprint(p), "chars": len(text), "text": text}
            elapsed = time.time() - t0
            eta = elapsed / i * (len(todo) - i)
            # 長片動輒上百張，靜默長跑會讓人以為當掉了
            print(f"  [{i}/{len(todo)}] {Path(fr).name}  {len(text)} 字"
                  f"  已花 {elapsed:.0f}s / 預估剩 {eta:.0f}s")
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8", newline="\n")
        print(f"OCR 快取 -> {cache_path.name}")

    if args.no_merge or data is None or json_path is None:
        return

    merged = 0
    for seg in data.get("segments", []):
        if not isinstance(seg, dict):
            continue
        seg_frames = seg.get("frames") or ([seg["frame"]] if seg.get("frame") else [])
        entries = []
        for fr in seg_frames:
            hit = cache.get(str(fr))
            if hit and hit.get("text"):
                entries.append({"frame": str(fr), "text": hit["text"]})
        if entries:
            seg["frame_ocr"] = entries
            merged += 1
        else:
            seg.pop("frame_ocr", None)

    data["ocr_meta"] = {
        "engine": ENGINE,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "min_conf": args.min_conf,
        "s2t": bool(s2t),
        "frames_total": len(frames),
        "frames_with_text": sum(1 for f in frames if cache.get(f, {}).get("text")),
        "note": "OCR 文字含辨識誤差，僅供定位與對照；術語、數值、分類標準仍以官方講義為準，"
                "必要時回頭看原圖。來源優先序：官方講義 > 投影片截圖 > ASR 逐字稿。",
    }
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8", newline="\n")
    print(f"併入 {merged}/{len(data.get('segments', []))} 段 -> {json_path.name}")


if __name__ == "__main__":
    main()
