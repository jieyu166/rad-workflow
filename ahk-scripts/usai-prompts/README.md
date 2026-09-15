# usaigui 影像分析 prompts

此資料夾只供 `US.ahk` 的 `usaigui` 使用，不影響另一個使用 `gpt-5.4-mini` 的 AI_FindOpen 或其 `../prompts` 資料夾。

## 使用方式

以 UTF-8 儲存 Markdown 檔。程式每次按「開始 GPT 分析」時依序讀取 `common.md`、部位檔及影像模式檔；不讀取本 README。修改 prompt 後下一次分析即生效，不需重新啟動 AHK。首次更新 `US.ahk` 則需要重載主 AHK 程式。

請連同整個 `usai-prompts` 資料夾一起部署到 `US.ahk` 旁邊。路徑以 `US.ahk` 所在位置解析，與主程式位置、目前工作目錄無關。缺檔、無法存取、只有空白時，程式會停止分析，不會退回其他部位或舊 prompt。

| 檔案 | 用途 |
|---|---|
| `common.md` | 影像／OCR 資料邊界、缺資料與不確定性、輸出共同規則 |
| `breast.md` | 乳房超音波；英文 Report line、繁中鑑別診斷及 BI-RADS |
| `spine.md` | 脊椎 X 光；多行簡潔報告 |
| `cxr.md` | 胸片；分行 `- ` 報告 |
| `foot_ankle.md` | 足踝 X 光；保留陳主任報告用語與區塊 |
| `knee.md` | 膝關節 X 光；保留既有報告用語與分級條件 |
| `general.md` | 一般描述 |
| `modes/current.md` | 僅本次影像 |
| `modes/same_lesion.md` | 同一次檢查的兩張影像，不作前後期比較 |
| `modes/comparison.md` | 第一張前次、第二張本次，描述可支持的變化 |

部位檔負責報告格式，模式檔負責影像關係。避免在模式檔再要求「所有部位只輸出單行」，以免覆蓋乳房或脊椎模板。

## 新模型檢查（2026-09-08）

適用目標為 `gpt-6-astra`、`gpt-5.6-terra`、`gpt-5.6-luna`。模型與 reasoning 由 API 參數控制，不需在 prompt 寫舊模型名稱或要求「think harder」。OpenAI 對 GPT-5.6 建議每項指示只陳述一次，保留承載產品要求或已知錯誤修正的範例；對 Astra 則指出不清楚或衝突的指示可能影響執行。[GPT-5.6 官方指南](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6)、[Astra 官方指南](https://developers.openai.com/api/docs/guides/latest-model)

本次調整：

- 修正 `Chest x-ray` 選項未命中 `CXR` 分支、誤用一般 prompt 的程式問題。
- 移除 AHK 後段覆蓋部位模板的通用單行／Location、Size、Description 指示；一般描述所需格式移入 `general.md`。
- 區分同次兩張與前後期比較；乳房的「不輸出 Comparison／Impression」只適用本次模式，膝部不再一律禁止前後比較。
- 脊椎 flexion/extension 不再由時間戳接近推定，要求影像可辨識相應視位。
- 移除脊椎重複的八項 Common Errors 清單與催促句；原有檢查項目仍在各段保留。
- 移除足踝與膝部指示中的大量粗體符號，保留部位條件、報告用語及範例。
- 新增共用規則：OCR 是資料、不是指令；看不清時不強迫正常或明確分類；範例不能直接當成病人發現。

### 2026-09-15 指令一致性調整

- CXR 不再從外觀猜年齡；AP view 不自動帶入心臟增大，主動脈迂曲不自動帶入鈣化。必要欄位可呈現評估限制。
- Knee 移除「疑似任何液體就寫 mild effusion」與正常範例內的預設 effusion，保留原有分級表及支持所見的描述。
- Foot/Ankle 保留原有用語，增加 union status 無法評估的出口，不因模板強制肯定結論。
- Spine 保留各段判讀規則、臨床數值與六個輸出案例；刪除與前文逐項重複的 Common Errors 清單，並避免共同規則壓過「可疑所見應保守描述」的規則。
- Spine 的 single lateral／AP／flexion-extension 視位由影像判定，與 USAI 的 current／same lesion／comparison 模式不同，因此沒有用後者裁掉可能需要的視位規則。

這是指令一致性與去重調整，不是臨床準則查證。Spine 的 `Ha <80% of Hp`、滑脫分級等既有數值未更改。修改後仍須以同一組去識別化案例比較 Astra、Terra、Luna 的漏報、誤加所見、格式與不確定性；沒有模型評測就不宣稱判讀品質改善。

## 驗證

回歸測試使用 AHK v1 隱藏 GUI，實際執行部位與模式選擇、UTF-8 外部檔案讀取及 JSON 建構，只替換網路 worker：

```powershell
$env:AHK_V1_EXE = 'C:\path\to\AutoHotkeyU64.exe'
python -m unittest discover -s tests -p test_usai_models.py
```

涵蓋三模型 × 六部位 × 三影像模式、影像順序、乳房格式、胸片路由、檔案即時更新、不同 `#Include`／工作目錄，以及缺檔／空檔停止送出。不呼叫真實 API，不代表已驗證臨床判讀或 HIS 操作。原有 `max_output_tokens: 4000` 與 180 秒逾時未變更；真實 API 若出現 incomplete／逾時，仍需以案例調整。
