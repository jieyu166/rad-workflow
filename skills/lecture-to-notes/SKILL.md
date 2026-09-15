---
name: lecture-to-notes
description: 將講座影片或課程資料夾整理成筆記、分段導航與同步 viewer；僅需字幕時用 whisper-srt-zh。
---

# 講座影片整理

將使用者指定的影片或課程資料夾完成為字幕、分段導航、來源可追溯的 V4 筆記與同步 viewer。只做要求的產物；已有可用 SRT／JSON 就從缺少的階段繼續。

| 本次工作 | 按需讀取 |
|---|---|
| 需要轉錄／字幕校正 | [轉錄](references/transcription.md)，執行已配置的 whisper-srt-zh |
| 已有字幕，要切分導航章節 | [分段與 JSON schema](references/segmentation.md) |
| 擷取投影片、OCR 或寫筆記 | [截圖與來源筆記](references/frames-and-notes.md) |
| 建立 viewer、PotPlayer 章節、批次課程或首頁 | [輸出與批次](references/outputs-and-batch.md) |

只有音檔時完成轉錄、分段與來源筆記，不要求投影片或截圖；已有手動投影片截圖時沿用它們，跳過自動抓換頁截圖。有官方講義時優先作為來源。

只要字幕時使用 whisper-srt-zh；純文字筆記整理、PDF 深讀或新知查核使用 obsidian-v4-cleanup。

## HARD RULES

1. ==轉錄前確認語言；使用者已指定就沿用，尚未指定才詢問==。`transcribe.py --lang` 沒有預設值。猜錯時 Whisper 不會報錯，
   而是把帶口音的英文**幻覺成一份流暢通順的中文逐字稿**——讀起來完全正常，錯得看不出來，
   一路污染到分段 JSON 與筆記才會發現。
2. ==逐字稿不自動改寫==。錯字用對照表取代時必留 `*.raw.srt` 與 `*.corrections.json`；
   語境校正由人／LLM 判斷，不做自動套用。
3. ==來源優先序：官方講義 > 投影片截圖（人眼看的）> ASR 逐字稿 > OCR 文字==。
   ASR 常把專有名詞、數字、甚至因果關係聽錯；OCR 會把「分類與追蹤」讀成「分類興追蹦」。
   ==OCR 只用來決定「要不要打開那張圖」，不可直接抄進筆記。==
4. ==`slide_frames.py` 完成後才執行相依步驟==。可用可追蹤的背景程序，但須持續回報進度、等待 exit code 並確認截圖已併入 JSON；不能啟動後就結束任務。
5. ==院內／病患相關影片一律本機轉錄==，不得用雲端 ASR。不確定就當作是。
6. 使用者介面文字用繁體中文台灣用語；專有名詞保留英文原文。


## 完成條件

- 按請求完成相應產物與引用；保留原始字幕及錯字更動紀錄。
- 等待相依程序完成再建構下游；可追蹤的背景執行須持續追蹤到完成。
- JSON／筆記產生或變更後，執行本 skill 的 `scripts/check_lecture.py <stem>.json --note <stem>.v4.md`；若本次不產生筆記則不加 `--note`。回報警告、錯誤與尚未覆核內容。
- 原始影片與 ASR 本機處理不代表後續 LLM 步驟自動獲准接收病患資料；不超出使用者授權的資料處理範圍。
