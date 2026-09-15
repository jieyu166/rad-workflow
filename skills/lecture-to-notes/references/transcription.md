# 路徑約定

`<skill>`／`<lecture-skill>` 是目前載入的 lecture-to-notes 根目錄；`<whisper-skill>` 從技能目錄取得，先確認 `scripts/transcribe.py` 存在。命令中的相對腳本路徑均以相應 skill 根目錄為基準。

## Step 1 — 轉錄（whisper-srt-zh）

```bash
python <whisper-skill>/scripts/transcribe.py "<影片或資料夾>" --lang zh
```

本機 GPU ASR + 錯字對照表校正，產 `<stem>.srt`（原始留 `<stem>.raw.srt`、
取代紀錄留 `<stem>.corrections.json`）。細節與對照表維護見 whisper-srt-zh。

==預設引擎是 Breeze-ASR-25==（聯發創新基地的台灣口音/中英夾雜模型）。教學講座實測
precision **92.5% vs turbo 的 78.1%**，關鍵在它不會亂拼術語——turbo 把 mammogram
拼成七種變體，那些全要人回頭對講義改。速度約 **0.13 倍實時**（獨佔 GPU 實測，264 分鐘
影片 31 分鐘轉完），==不是先前寫的「慢十倍」，那是 GPU 被別的工作占用時量錯的==。
所以==走完整管線的講座不要改用 turbo==；只想快速拿字幕才加 `--engine whisper.cpp`。

已經有字幕就跳過這步。

