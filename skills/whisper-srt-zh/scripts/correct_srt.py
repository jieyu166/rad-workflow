#!/usr/bin/env python3
"""correct_srt.py — 對 .srt / .txt 套用 ASR 錯字對照表（deterministic + radiology）。

context_sensitive 清單不盲改（交給 LLM 判斷）。長鍵優先，避免部分字串先被改掉。
原檔備份為 <name>.raw.<ext>；輸出覆寫原檔（或 --out 另存）。

每次實際寫檔會另存稽核 sidecar `<name>.corrections.json`（wrong / right / count /
source），因為「自動取代」本質上是有風險的操作：正確詞常常根本不在對照表的語境裡，
一次錯誤取代會把原始證據抹掉且事後查不到。留下 sidecar 才能比對、回溯、回滾。

用法：
  python correct_srt.py INPUT.srt
  python correct_srt.py INPUT.txt --out INPUT.fixed.txt
  python correct_srt.py INPUT.srt --report      # 只印會改哪些、不寫檔
  python correct_srt.py INPUT.srt --no-sidecar  # 不產稽核檔
  python correct_srt.py INPUT.srt --corrections /path/to/corrections.json
"""
from __future__ import annotations
import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CORR = HERE.parent / "references" / "corrections.json"


def load_pairs(corr_path: Path):
    """回傳 [(wrong, right, source), ...]，長鍵優先。source 用於 sidecar 稽核。"""
    data = json.loads(corr_path.read_text(encoding="utf-8"))
    pairs = {}
    for source in ("deterministic", "radiology"):
        for wrong, right in data.get(source, {}).items():
            pairs[wrong] = (right, source)  # 後者覆蓋前者，與原行為一致
    # 長鍵優先（避免短鍵先吃掉長鍵的一部分）
    return sorted(((w, r, s) for w, (r, s) in pairs.items()),
                  key=lambda t: len(t[0]), reverse=True)


def apply_corrections(text: str, pairs):
    hits = []
    for wrong, right, source in pairs:
        if wrong in text:
            n = text.count(wrong)
            text = text.replace(wrong, right)
            hits.append((wrong, right, n, source))
    return text, hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--out", help="輸出路徑（預設覆寫原檔，原檔備份為 .raw.<ext>）")
    ap.add_argument("--corrections", default=str(DEFAULT_CORR))
    ap.add_argument("--report", action="store_true", help="只報告會改哪些，不寫檔")
    ap.add_argument("--no-s2t", action="store_true", help="跳過簡→繁轉換")
    ap.add_argument("--no-backup", action="store_true")
    ap.add_argument("--no-sidecar", action="store_true",
                    help="不產 <name>.corrections.json 稽核檔")
    args = ap.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        print(f"ERROR: 找不到 {inp}", file=sys.stderr); sys.exit(1)
    pairs = load_pairs(Path(args.corrections))

    # 編碼偵測：依 BOM 判 UTF-16，否則一律 UTF-8（容錯 replace）。
    # 不可用「strict utf-8 失敗就 fallthrough utf-16」——whisper 偶爾吐 1 個壞位元組，
    # 會讓整個 UTF-8 檔被誤當 UTF-16 解成亂碼。
    raw = inp.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw.decode("utf-16")
    elif raw[:3] == b"\xef\xbb\xbf":
        text = raw.decode("utf-8-sig")
    else:
        text = raw.decode("utf-8", "replace")
        nbad = text.count("�")
        if nbad:
            print(f"  (注意：{nbad} 個壞位元組已以 U+FFFD 取代——whisper 偶發)", file=sys.stderr)

    # 正規化換行：whisper main.exe 會輸出 '\r\r\n'，移除所有 CR 避免結構錯亂/寫檔加倍
    text = text.replace("\r", "")
    original = text  # 比較基準（含 s2t 與錯字表的總變更）
    # 簡→繁（台灣用語）先轉，再套錯字表
    s2t_done = False
    if not args.no_s2t:
        try:
            from opencc import OpenCC
            text = OpenCC("s2twp").convert(text)
            s2t_done = True
        except ImportError:
            print("  (opencc 未安裝 → 跳過簡轉繁；`pip install opencc-python-reimplemented`)", file=sys.stderr)

    fixed, hits = apply_corrections(text, pairs)
    if s2t_done:
        print("已套用 簡→繁（台灣用語 s2twp）")
    print(f"套用 {len(hits)} 種修正（共 {sum(h[2] for h in hits)} 處）：")
    for wrong, right, n, source in hits[:60]:
        print(f"  {wrong} -> {right}  x{n}  [{source}]")
    if len(hits) > 60:
        print(f"  ...另 {len(hits)-60} 種")

    if args.report:
        print("(--report：未寫檔)")
        return
    if fixed == original:
        print("無變更，不寫檔。")
        return

    out = Path(args.out) if args.out else inp
    bak = None
    if out == inp and not args.no_backup:
        bak = inp.with_suffix(f".raw{inp.suffix}")
        if not bak.exists():
            shutil.copy2(inp, bak)
            print(f"原檔備份 -> {bak.name}")
    out.write_text(fixed, encoding="utf-8", newline="\n")  # 固定 \n，避免 OS 換行轉換把 CR 加倍
    print(f"已寫出 -> {out}")

    if not args.no_sidecar:
        write_sidecar(out, inp, bak, hits, s2t_done, Path(args.corrections))


def write_sidecar(out: Path, inp: Path, bak, hits, s2t_done: bool, corr_path: Path):
    """留下可稽核、可回滾的取代紀錄。與 .raw.<ext> 備份互補：
    備份告訴你「原本長什麼樣」，sidecar 告訴你「哪一條規則改了它、改了幾處」。"""
    side = out.with_suffix(".corrections.json")
    payload = {
        "input": inp.name,
        "output": out.name,
        "backup": bak.name if bak else None,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "corrections_table": str(corr_path),
        "s2t": {"applied": s2t_done, "converter": "s2twp" if s2t_done else None},
        "total_kinds": len(hits),
        "total_hits": sum(h[2] for h in hits),
        "applied": [{"wrong": w, "right": r, "count": n, "source": s}
                    for w, r, n, s in hits],
    }
    side.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")
    print(f"稽核紀錄 -> {side.name}")


if __name__ == "__main__":
    main()
