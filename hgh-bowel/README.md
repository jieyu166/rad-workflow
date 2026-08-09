# 高醫腸阻塞資料擷取

一次性專案：把 368 筆檢查的 DICOM metadata 填進高醫的對照表。收工後整包移除即可（記得同時拿掉 `ahk-scripts/簡碼 jai.ahk` 的 `#include`）。

## 資料與保密

- 對照表本體在 OneDrive `00 放射科\高醫腸阻塞判讀資料\`，**不在本 repo**，也不該進來
- **申請單號可連結回個資**，因此 `work/`（queue、result、raw 檔頭）已列入 `.gitignore`
- `tests/` 的檔頭範例是合成資料，單號 `999999999999999` 為假號

## 要填的欄位

| 欄 | 內容 | 來源 |
|---|---|---|
| C | 拍攝年（西元） | StudyDate (0008,0020) 前四碼 |
| D | 年齡 | PatientAge (0010,1010)；缺則由 PatientBirthDate 與 StudyDate 推算 |
| E | 性別 | PatientSex (0010,0040)，填 **M / F** |
| F | 種族 | **不填** |
| G | 就醫來源 | **不填** |
| H | 解析度 | 常數 **`512*512`**（匯出 JPG 尺寸，非 DICOM） |
| I | CT廠牌 | Manufacturer (0008,0070) |
| J | CT型號 | ManufacturerModelName (0008,1090) |

### 兩個格式決定的依據

高醫範例檔 `翁國勛填寫範例.xlsx` 有 11 筆**實際填好**的資料：

```
2024  62  M  亞洲人  急診  150*150  Siemens  SOMATOM Definition Edge
```

**性別填 M/F**，不是該檔「工作表1」圖例寫的 1/2 —— 實填資料比圖例可信。

**解析度是匯出 JPG 的尺寸，不是 CT 矩陣。** 實測本機 250 個 Case 資料夾、抽樣 500 張 JPG，全部是 512×512，所以本批填 `512*512`（範例用 `*` 不是 `x`）。刻意不從 DICOM `Rows`/`Columns` 取：兩者這次都是 512，但若某案矩陣是 768，DICOM 會給 768 而匯出的 JPG 仍是 512，那就填錯了。解析器仍會比對矩陣，不符時示警。

> 範例的 `150*150` 是翁國勛那批的匯出尺寸，與本批無關。

## 分工：醫院端擷取，家裡端解析

**醫院電腦不能跑 Python**，所以擷取端是純 AHK，只把 DICOM 檔頭原文存進 `work/raw/<單號>.txt`。解析與回填都在家裡做。這樣切還有一個好處：解析規則之後要改，直接重跑原文即可，不必再進 PACS 一次。

`work/` 在 OneDrive 底下，會自己同步回家。

### 醫院端（AHK，無需 Python）

**執行方式：跑 `ahk-scripts/簡碼 jai.ahk`，不要單獨執行 `hgh_capture.ahk`。**

單獨跑會出現 `Call to nonexistent function`，而且不是加一個 `#include` 就能解決——相依是連鎖的：本檔需要 `test.ahk` 的 `ActivateHISLight()`/`OpenPACSImage()`/`GetDICOMData()`，而 `test.ahk` 又需要 `簡碼 jai.ahk` 的 `CopyCXRtoHISWithParam()`、`Xray.ahk` 的 `OutputFinish()`、以及 `LOGI`/`PWD`/`vExamLoc`/`varWhere` 等全域。硬拉進來等於載入整包，還會和你日常那份搶熱鍵。

按 **`Win+Shift+G`** 開啟置頂小視窗（載入時不會自己跳出來，不干擾日常作業）。**點選**申請單號那一格，視窗會即時顯示抓到的單號、來源與是否已擷取過，確認無誤再按按鈕。

單號來源依序嘗試三種，因為三邊環境不同：

| 來源 | 適用 | 取得方式 |
|---|---|---|
| `Calc` | 醫院 OpenOffice / LibreOffice | UNO 讀目前選取格 |
| `Excel` | 家用 Excel | COM 讀 `ActiveCell` |
| `剪貼簿` | Office 365 網頁版（無 COM） | 請先 `Ctrl+C` |

狀態列會標出實際來源，例如 `單號：100210580275101（Calc）`。**剪貼簿的內容可能是舊的**，標示來源就是為了讓你看得出這個數字能不能信。

| 按鈕 | 熱鍵 | 動作 |
|---|---|---|
| — | `Win+Shift+G` | 開啟／叫回擷取視窗 |
| 1 | `Win+Shift+H` | 把單號帶進 HIS(chk060) 開啟該檢查 |
| 2 | `Win+Shift+J` | 讀**目前 INFINITT 顯示中**的影像檔頭，組成整列複製到剪貼簿 |
| 3 | `Win+Shift+F1` | 除錯：列出 chk060 控件 |

按鈕2 **不會自己開 PACS**（那個連結目前不通）。請自行在 INFINITT 叫出影像後再按。複製到剪貼簿的是 Tab 分隔的一整列，直接貼在該列的 **C 欄**即可填滿 C 到 J：

```
2024	65	M			512*512	SIEMENS	SOMATOM Definition AS+
```

中間兩個連續 Tab 就是留空的種族與就醫來源，貼上去不會覆蓋你手填的內容。

按鈕2 仍會比對試算表選取的單號與影像檔頭的單號，不符會跳出確認——這是取代「自動開圖」後僅存的防呆，專門擋「試算表停在 Case 005，但 INFINITT 上顯示的是別案」。

單號是讀 Excel 的 `ActiveCell`，不是讀滑鼠位置——按鈕一按滑鼠就離開儲存格了，選取狀態才不受焦點轉移影響。讀不到 Excel 時退回剪貼簿。

按鈕2 會**比對抓到的單號與要求的單號**，不符就中止且不寫入——這道防線是為了擋「影像還沒切換就抓到上一案」，這種錯會靜默污染資料，比漏掉一筆難查得多。已擷取過的會先問要不要重抓。

### 家裡端（Python）

```bash
python parse_all_raw.py
```

把 `work/raw/` 全部重新解析成 `work/result.csv`，並列出缺漏欄位與單號不符的檔案。每次都是整份重建，重跑安全。

```bash
python export_queue.py --xlsx "<對照表路徑>" --status --next 10
```

```bash
python fill_mapping.py --xlsx "<對照表路徑>" --dry-run
```

確認無誤後拿掉 `--dry-run` 實寫。回填會自動備份原檔，且**不覆蓋已有值**（要覆蓋加 `--overwrite`），F/G 兩欄永不觸碰。

## 第一次在醫院電腦要做的校正

`hgh_capture.ahk` 最上面兩個設定：

1. `HGH_QueryBtn()` — chk060 查詢按鈕控件名，用按鈕3 查出來後填入；留空則改送 `{Enter}`
2. `HGH_PacsWait()` — INFINITT 載入等待秒數，網路慢就調大

路徑不必設定：`HGH_Dir()` 由 `A_LineFile` 推導本檔自身位置。家用機是 `C:\Users\jai16\OneDrive\...`、醫院機是 `D:\jai166\Onedrive\...`，硬編必錯一邊。

另外 `test.ahk` 的 `OpenPACSImage()` 內，**佳里院區的 host `jlweb15`/`MX=14` 尚未實測**（永康 `ykweb15`/`MX=10` 是舊版實測值）。

## 檔頭格式若對不上

`parse_dicom_header.py` 已容忍 INFINITT 的「標籤行 + 下一行 `|值|`」、`標籤: 值`、Tab 分隔等格式。若仍解析不出來：

```bash
python parse_dicom_header.py --inspect
```

`--inspect` 只印偵測到的**欄位標籤、不印任何值**，可以安全貼給我調整解析規則。原始檔頭都留在 `work/raw/<單號>.txt`，改完解析規則可直接重跑，不必再進 PACS。

## 測試

```bash
python -m unittest discover -s tests -v
```

解析器有 10 個測試（合成資料）。AHK 端無法在開發機測試——需要 INFINITT 桌面版與院內網路。
