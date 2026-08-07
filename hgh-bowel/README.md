# 高醫腸阻塞資料擷取

一次性專案：把 368 筆檢查的 DICOM metadata 填進高醫的對照表。收工後整包移除即可（記得同時拿掉 `ahk-scripts/簡碼 jai.ahk` 的 `#include`）。

## 資料與保密

- 對照表本體在 OneDrive `00 放射科\高醫腸阻塞判讀資料\`，**不在本 repo**，也不該進來
- **申請單號可連結回個資**，因此 `work/`（queue、result、raw 檔頭）已列入 `.gitignore`
- `tests/` 的檔頭範例是合成資料，單號 `999999999999999` 為假號

## 要填的欄位

| 欄 | 內容 | DICOM 來源 |
|---|---|---|
| C | 拍攝年（西元） | StudyDate (0008,0020) 前四碼 |
| D | 年齡 | PatientAge (0010,1010)；缺則由 PatientBirthDate 與 StudyDate 推算 |
| E | 性別 | PatientSex (0010,0040)，M=1、F=2（依高醫範例檔「工作表1」代碼） |
| F | 種族 | **不填** |
| G | 就醫來源 | **不填** |
| H | 解析度 | Rows x Columns (0028,0010 / 0028,0011)，如 `512x512` |
| I | CT廠牌 | Manufacturer (0008,0070) |
| J | CT型號 | ManufacturerModelName (0008,1090) |

## 操作流程

在 Excel 選取該列的申請單號、`Ctrl+C`，然後：

| 熱鍵 | 動作 |
|---|---|
| `Win+Shift+H` | 功能一：把單號帶進 HIS(chk060) 開啟該檢查 |
| `Win+Shift+J` | 功能二：開 PACS 影像、抓 DICOM 檔頭、解析後追加到 `work/result.csv` |
| `Win+Shift+F1` | 除錯：列出 chk060 控件（第一次校正查詢按鈕用） |

功能二會**比對抓到的單號與要求的單號**，不符就中止且不寫入——這道防線是為了擋「影像還沒切換就抓到上一案」。

### 進度與回填

```bash
python export_queue.py --xlsx "<對照表路徑>" --status --next 10
```

```bash
python fill_mapping.py --xlsx "<對照表路徑>" --dry-run
```

確認無誤後拿掉 `--dry-run` 實寫。回填會自動備份原檔，且**不覆蓋已有值**（要覆蓋加 `--overwrite`），F/G 兩欄永不觸碰。

## 第一次在醫院電腦要做的校正

`hgh_capture.ahk` 最上面四個設定：

1. `HGH_DIR` — 本資料夾絕對路徑
2. `HGH_PYTHON` — python 執行檔（不在 PATH 就填絕對路徑）
3. `HGH_HIS_QUERY_BTN` — chk060 查詢按鈕控件名，用 `Win+Shift+F1` 查出來後填入；留空則改送 `{Enter}`
4. `HGH_PACS_WAIT` — INFINITT 載入等待秒數，網路慢就調大

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
