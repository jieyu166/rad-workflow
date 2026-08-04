#!/usr/bin/env python3
"""transcribe.py — 本機 GPU Whisper 批次轉錄（取代 bat.bat），含錯字修正。

對資料夾內（或指定）影片/音檔：
  ffmpeg → 16kHz mono WAV → ASR → .srt
  → correct_srt.py 套用錯字對照表 → 校正後 .srt（原始保留為 .raw.srt）

引擎預設 faster-whisper + Breeze-ASR-25：教學/醫學講座實測 precision 92.5% vs
ggml-large-v3-turbo 的 78.1%（3 場乳房影像講座，見 SKILL.md）。turbo 快很多但會把
mammogram 拼成七種變體，術語要拿去對講義時那個代價比時間貴。趕時間就 --engine
whisper.cpp。
全本機、用 GPU（CUDA），不需網路、不上傳雲端。

預設路徑沿用使用者 bat.bat（可用環境變數 / CLI 覆寫）：
  WHISPER  WHISPER_SRT_BIN     PotPlayer 的 whisper main.exe
  MODEL    WHISPER_SRT_MODEL   ggml-large-v3-turbo.bin
  FFMPEG   WHISPER_SRT_FFMPEG  ffmpeg（預設找 PATH，再退 bat 的 FormatFactory 版）

--lang 是必填，沒有預設值。猜錯語言時 Whisper 會把「帶口音的英文」幻覺成流暢
中文，而且讀起來完全正常、看不出壞掉——寧可多問一句，也不要產出一份看似沒問題
的假逐字稿。轉錄階段忠實記錄講者原本的語言，翻譯成繁體中文是後續處理的事。

用法：
  python transcribe.py --lang zh                  # 當前資料夾所有影片
  python transcribe.py VIDEO.mp4 --lang en        # 單檔
  python transcribe.py DIR --lang auto            # 讓 whisper 自己偵測
  python transcribe.py VIDEO.mp4 --lang zh --no-correct
  python transcribe.py --lang zh --force          # 已存在 .srt 也重跑
"""
from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORRECT = HERE / "correct_srt.py"

DEFAULT_WHISPER = r"C:\Program Files\DAUM\PotPlayer\Module\Whisper\CUDA\main.exe"
DEFAULT_MODEL = r"C:\Users\jai16\AppData\Roaming\PotPlayerMini64\Model\ggml-large-v3-turbo.bin"
FALLBACK_FFMPEG = r"C:\Users\jai16\OneDrive\Portable 應用程式\FormatFactoryPortable\App\ProgramFiles\ffmpeg.exe"
VIDEO_EXT = (".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v")
AUDIO_EXT = (".mp3", ".m4a", ".wav", ".flac")
# Breeze-ASR-25 等 HF 模型轉成 CTranslate2 後放這裡（--engine faster-whisper 用）
DEFAULT_CT2_MODEL = str(Path.home() / "AppData/Local/whisper-models/breeze-asr-25-ct2")


def resolve_ffmpeg(cli):
    for c in (cli, os.environ.get("WHISPER_SRT_FFMPEG"), shutil.which("ffmpeg"), FALLBACK_FFMPEG):
        if c and Path(c).exists() if c and ("\\" in str(c) or "/" in str(c)) else (c and shutil.which(c)):
            return c
    # last resort: trust 'ffmpeg' on PATH
    return shutil.which("ffmpeg") or FALLBACK_FFMPEG


def fmt_ts(sec: float) -> str:
    h, rem = divmod(max(0.0, sec), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round(s % 1 * 1000)):03d}"


def run_faster_whisper(wav: Path, srt: Path, args) -> bool:
    """faster-whisper 引擎（給 Breeze-ASR-25 之類的 HF/CT2 模型用）。

    預設關 VAD 與 condition_on_previous_text：VAD 會默默吃掉停頓邊緣的輕聲，
    conditioning 會把聽錯的內容往後傳染。兩者都是 drpwchen/asr-benchmark 實測
    出來的設定，不是猜的。
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("  [失敗] 未安裝 faster-whisper：pip install faster-whisper", file=sys.stderr)
        return False
    model_dir = args.ct2_model or os.environ.get("WHISPER_SRT_CT2_MODEL", DEFAULT_CT2_MODEL)
    if not Path(model_dir).exists():
        print(f"  [失敗] 找不到 CT2 模型目錄：{model_dir}", file=sys.stderr)
        print("    ct2-transformers-converter --model MediaTek-Research/Breeze-ASR-25 \\",
              file=sys.stderr)
        print(f"      --output_dir \"{model_dir}\" --quantization float16", file=sys.stderr)
        return False
    model = WhisperModel(model_dir, device=args.device, compute_type=args.compute_type)
    segments, info = model.transcribe(
        str(wav),
        language=None if args.lang.lower() == "auto" else args.lang,
        beam_size=args.beam_size,
        vad_filter=args.vad,
        condition_on_previous_text=args.condition,
    )
    lines, n = [], 0
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        n += 1
        lines.append(f"{n}\n{fmt_ts(seg.start)} --> {fmt_ts(seg.end)}\n{text}\n")
        if n % 50 == 0:
            print(f"      {n} 段，已到 {seg.end/60:.1f} 分")
    if not lines:
        print("  [失敗] 沒有辨識出任何內容", file=sys.stderr)
        return False
    srt.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"      偵測語言 {info.language} (p={info.language_probability:.2f})，共 {n} 段")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", default=".", help="影片檔或資料夾（預設當前資料夾）")
    ap.add_argument("--whisper", default=os.environ.get("WHISPER_SRT_BIN", DEFAULT_WHISPER))
    ap.add_argument("--model", default=os.environ.get("WHISPER_SRT_MODEL", DEFAULT_MODEL))
    ap.add_argument("--ffmpeg")
    # 刻意「沒有預設值」：語言猜錯會產生看不出壞掉的幻覺逐字稿，見模組 docstring。
    ap.add_argument("--lang", help="講者語言：zh / en / ja / auto ...（必填，無預設）")
    ap.add_argument("--engine", default="faster-whisper",
                    choices=["faster-whisper", "whisper.cpp"],
                    help="faster-whisper = Breeze-ASR-25（預設，術語精確率高）；"
                         "whisper.cpp = PotPlayer CUDA + ggml-turbo（快很多，術語較差）")
    ap.add_argument("--ct2-model", help="faster-whisper 的模型目錄（預設 breeze-asr-25-ct2）")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--compute-type", default="float16")
    ap.add_argument("--beam-size", type=int, default=5)
    ap.add_argument("--vad", action="store_true",
                    help="開 VAD（預設關：實測會吃掉停頓邊緣的輕聲）")
    ap.add_argument("--condition", action="store_true",
                    help="開 condition_on_previous_text（預設關：會把聽錯的往後傳染）")
    ap.add_argument("--force", action="store_true", help="已有 .srt 也重跑")
    ap.add_argument("--no-correct", action="store_true", help="跳過錯字修正")
    ap.add_argument("--keep-wav", action="store_true")
    args = ap.parse_args()

    if not args.lang:
        print("[錯誤] --lang 是必填，沒有預設值。", file=sys.stderr)
        print("  講者說的是哪一種語言？zh（華語）/ en（英語）/ ja / auto（讓 whisper 偵測）", file=sys.stderr)
        print("  為什麼不給預設：猜成 zh 去轉一段英文演講時，whisper 會把帶口音的英文", file=sys.stderr)
        print("  幻覺成一份流暢通順的中文逐字稿——讀起來完全正常，錯得看不出來。", file=sys.stderr)
        print("  例：python transcribe.py \"<檔或資料夾>\" --lang zh", file=sys.stderr)
        sys.exit(2)

    ffmpeg = resolve_ffmpeg(args.ffmpeg)
    # faster-whisper 不需要 PotPlayer 的 main.exe 與 ggml 檔，別拿它們的存在當前提
    needed = [("FFmpeg", ffmpeg)]
    if args.engine == "whisper.cpp":
        needed = [("Whisper", args.whisper), ("Model", args.model)] + needed
    else:
        needed = [("CT2 模型", args.ct2_model or DEFAULT_CT2_MODEL)] + needed
    for label, p in needed:
        if not p or not Path(p).exists():
            print(f"[錯誤] 找不到 {label}: {p}", file=sys.stderr)
            if label == "CT2 模型":
                print("  這台機器還沒有 Breeze-ASR-25，轉一次即可（約 3 GB 下載）：", file=sys.stderr)
                print("    ct2-transformers-converter --model MediaTek-Research/Breeze-ASR-25 "
                      f"--output_dir \"{p}\" --quantization float16", file=sys.stderr)
                print("  或改用較快的舊引擎：--engine whisper.cpp", file=sys.stderr)
            else:
                print("  用 --whisper/--model/--ffmpeg 或環境變數指定路徑", file=sys.stderr)
            sys.exit(1)

    tgt = Path(args.target)
    if tgt.is_dir():
        files = sorted(f for f in tgt.iterdir() if f.suffix.lower() in VIDEO_EXT + AUDIO_EXT)
    elif tgt.exists():
        files = [tgt]
    else:
        print(f"[錯誤] 路徑不存在: {tgt}", file=sys.stderr); sys.exit(1)
    if not files:
        print("[錯誤] 沒有影片/音檔"); sys.exit(1)

    shown = (args.ct2_model or DEFAULT_CT2_MODEL) if args.engine == "faster-whisper" else args.model
    print(f"引擎: {args.engine}" + chr(10) + f"Model: {Path(shown).name}" + chr(10) + f"語言: {args.lang}")
    print(f"找到 {len(files)} 個檔案\n" + "=" * 44)
    done = 0
    for i, f in enumerate(files, 1):
        srt = f.with_suffix(".srt")
        print(f"[{i}/{len(files)}] {f.name}")
        if srt.exists() and not args.force:
            print(f"  [跳過] 已有 {srt.name}")
            continue
        wav = f.with_suffix(".wav")
        if f.suffix.lower() in AUDIO_EXT and f.suffix.lower() == ".wav":
            wav = f
        else:
            print("  [1/3] ffmpeg → 16kHz mono wav")
            r = subprocess.run([ffmpeg, "-i", str(f), "-ar", "16000", "-ac", "1", "-y",
                                str(wav), "-loglevel", "error"], capture_output=True)
            if not wav.exists():
                print(f"  [失敗] 音訊轉換：{r.stderr.decode('utf-8','replace')[:200]}"); continue
        print(f"  [2/3] {args.engine} (CUDA) 辨識中...")
        if args.engine == "faster-whisper":
            ok = run_faster_whisper(wav, srt, args)
            if not ok:
                if wav != f and not args.keep_wav:
                    wav.unlink(missing_ok=True)
                continue
        else:
            subprocess.run([args.whisper, "-m", args.model, "-l", args.lang,
                            "-osrt", "-of", str(f.with_suffix("")), "-f", str(wav)])
        if wav != f and not args.keep_wav:
            wav.unlink(missing_ok=True)
        if not srt.exists():
            print("  [失敗] 未產生字幕"); continue
        print(f"  [完成] {srt.name}")
        if not args.no_correct and CORRECT.exists():
            print("  [3/3] 錯字修正...")
            cmd = [sys.executable, str(CORRECT), str(srt)]
            # s2twp 只對中文安全：對日文會把漢字轉成台灣用字，對英文是 no-op。
            if args.lang.lower() not in ("zh", "auto"):
                cmd.append("--no-s2t")
            subprocess.run(cmd)
        done += 1
    print("=" * 44 + f"\n完成 {done} 個（共 {len(files)}）")


if __name__ == "__main__":
    main()
