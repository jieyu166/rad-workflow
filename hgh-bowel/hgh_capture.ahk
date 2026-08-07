; ============================================================================
; 高醫腸阻塞資料擷取（一次性專案，收工後可整包移除）
;
; 依賴 test.ahk 的：ActivateHISLight()、OpenPACSImage()、GetDICOMData()、
;                   GetDICOMLineData()、CallDICOMWin
; 由「簡碼 jai.ahk」在 test.ahk 之後 #include。
;
; 用法：腳本載入後會跳出一個置頂小視窗。在 Excel 點選申請單號那一格，
;       視窗會即時顯示它抓到的單號，確認無誤再按按鈕。
;         按鈕1 / Win+Shift+H：該單號 -> HIS(chk060) 開啟檢查
;         按鈕2 / Win+Shift+J：該單號 -> PACS 開影像 -> 抓 DICOM 檔頭 -> 存原始檔
;         按鈕3 / Win+Shift+F1：除錯，列出 chk060 控件
;       視窗關掉後用 Win+Shift+G 叫回來。
;
; 醫院電腦不能跑 Python，所以這裡「只擷取、不解析」：檔頭原文存進 work\raw\，
; 回家後再用 parse_all_raw.py 解析、fill_mapping.py 回填 xlsx。
; work\ 在 OneDrive 底下，會自己同步回家。
; ============================================================================

; --- 需要校正的設定（第一次在醫院電腦跑之前先確認）---
global HGH_DIR := "C:\Users\jai16\OneDrive\00 放射科\5工作\rad-workflow-main\hgh-bowel"
; chk060 上「查詢/確定」按鈕的控件名。用按鈕3 確認後改這裡。
; 留空則改用送 {Enter} 觸發查詢。
global HGH_HIS_QUERY_BTN := ""
; INFINITT 載入影像的等待秒數，網路慢就調大
global HGH_PACS_WAIT := 6
global HGH_TOTAL := 368

HGH_BuildGUI()


; ============================================================================
; GUI
; ============================================================================
HGH_BuildGUI() {
    Gui, HGH:New, +AlwaysOnTop +ToolWindow, 高醫腸阻塞擷取
    Gui, HGH:Font, s10, Microsoft JhengHei
    Gui, HGH:Add, Text, x12 y10 w300 vHGH_StatusText, 單號：(在 Excel 點選申請單號)
    Gui, HGH:Add, Text, x12 y34 w300 vHGH_ProgressText, 進度：--
    Gui, HGH:Add, Button, x12 y62 w300 h38 gHGH_Btn1, 1. 用此單號開 HIS 檢查
    Gui, HGH:Add, Button, x12 y104 w300 h38 gHGH_Btn2, 2. 開 PACS 並擷取 DICOM 檔頭
    Gui, HGH:Font, s9
    Gui, HGH:Add, Button, x12 y146 w300 h28 gHGH_Btn3, 3. 除錯：列出 chk060 控件
    Gui, HGH:Show, w324 h186, 高醫腸阻塞擷取
    SetTimer, HGH_UpdateStatus, 1000
    Gosub, HGH_UpdateStatus
}

<#+g::
    Gui, HGH:Show, , 高醫腸阻塞擷取
    SetTimer, HGH_UpdateStatus, 1000
return

HGHGuiClose:
HGHGuiEscape:
    SetTimer, HGH_UpdateStatus, Off
    Gui, HGH:Hide
return

; 每秒把 Excel 目前選取格的單號與擷取進度顯示出來，按下按鈕前就能看出抓的對不對
HGH_UpdateStatus:
    hghExam := HGH_GetExamNo(false)
    if (hghExam = "")
        GuiControl, HGH:, HGH_StatusText, % "單號：(在 Excel 點選申請單號)"
    else
        GuiControl, HGH:, HGH_StatusText, % "單號：" . hghExam . (HGH_IsCaptured(hghExam) ? "  [已擷取]" : "")
    GuiControl, HGH:, HGH_ProgressText, % "進度：" . HGH_CapturedCount() . " / " . HGH_TOTAL
return


; ============================================================================
; 功能一：申請單號 -> HIS 開啟檢查
; ============================================================================
HGH_Btn1:
<#+h::
    examNo := HGH_GetExamNo(true)
    if (examNo = "")
        return

    ActivateHISLight()
    ControlSetText, ThunderRT6TextBox9, %examNo%, ahk_exe chk060.exe
    if (HGH_HIS_QUERY_BTN != "") {
        ControlClick, %HGH_HIS_QUERY_BTN%, ahk_exe chk060.exe
    } else {
        ControlFocus, ThunderRT6TextBox9, ahk_exe chk060.exe
        ControlSend, ThunderRT6TextBox9, {Enter}, ahk_exe chk060.exe
    }
    TrayTip, HIS, 已帶入單號 %examNo%, 2, 1
return


; ============================================================================
; 功能二：申請單號 -> PACS 開影像 -> 抓 DICOM 檔頭 -> 存成原始檔
; ============================================================================
HGH_Btn2:
<#+j::
    examNo := HGH_GetExamNo(true)
    if (examNo = "")
        return

    if (HGH_IsCaptured(examNo)) {
        MsgBox, 262148, 高醫擷取, %examNo% 已經擷取過了，要重抓嗎？
        IfMsgBox, No
            return
    }

    TrayTip, PACS, 開啟 %examNo% 影像中..., 3, 1
    if (!OpenPACSImage("arg", examNo))
        return

    ; 等 INFINITT 起來並把新檢查載進來
    WinWait, INFINITT PACS, , 30
    if ErrorLevel {
        TrayTip, PACS, INFINITT 視窗未出現，已中止, 4, 3
        return
    }
    Sleep, % HGH_PACS_WAIT * 1000

    ; 抓檔頭，並確認抓到的就是這一筆（避免影像還沒換就抓到上一案）
    header := GetDICOMData()
    got := RegExReplace(GetDICOMLineData("accession number", header), "\D")

    if (got != examNo) {
        ; 再等一輪重抓，仍不符就中止，寧可漏也不要寫錯列
        Sleep, % HGH_PACS_WAIT * 1000
        header := GetDICOMData()
        got := RegExReplace(GetDICOMLineData("accession number", header), "\D")
    }
    if (got = "") {
        TrayTip, PACS, 抓不到 DICOM 檔頭，已中止, 4, 3
        return
    }
    if (got != examNo) {
        TrayTip, PACS, 單號不符！要 %examNo% 但抓到 %got%`n已中止，未寫入, 6, 3
        return
    }

    HGH_SaveHeader(examNo, header)
    Gosub, HGH_UpdateStatus
return


; ============================================================================
; 除錯：列出 chk060 控件，用來確認查詢按鈕叫什麼
; ============================================================================
HGH_Btn3:
<#+F1::
    WinGet, ctrls, ControlList, ahk_exe chk060.exe
    if (ctrls = "") {
        MsgBox, 0, 除錯, 找不到 chk060.exe 視窗
        return
    }
    Clipboard := ctrls
    MsgBox, 0, chk060 控件清單（已複製到剪貼簿）, %ctrls%
return


; ============================================================================
; 輔助函數
; ============================================================================

; 取申請單號。優先讀 Excel 目前選取格——按鈕一按滑鼠就離開儲存格了，
; 靠滑鼠位置會抓不到；選取狀態則不受焦點轉移影響。
; 讀不到 Excel 才退回剪貼簿。complain=false 供每秒輪詢用，不要跳訊息。
HGH_GetExamNo(complain := true) {
    examNo := ""
    try {
        xl := ComObjActive("Excel.Application")
        examNo := RegExReplace(xl.ActiveCell.Value, "\D")
    } catch e {
        examNo := ""
    }

    if (StrLen(examNo) < 8)
        examNo := RegExReplace(Clipboard, "\D")

    if (StrLen(examNo) < 8) {
        if (complain)
            TrayTip, 高醫擷取, 取不到申請單號`n請在 Excel 點選單號那一格, 3, 3
        return ""
    }
    return examNo
}

HGH_RawPath(examNo) {
    return HGH_DIR . "\work\raw\" . examNo . ".txt"
}

HGH_IsCaptured(examNo) {
    return FileExist(HGH_RawPath(examNo)) ? true : false
}

HGH_CapturedCount() {
    count := 0
    rawDir := HGH_DIR . "\work\raw"
    Loop, %rawDir%\*.txt
        count += 1
    return count
}

; 存檔頭原文。解析留到家裡做——醫院電腦沒有 Python，而且原文留著才能在
; 解析規則改動後重跑，不必再進 PACS 一次。
HGH_SaveHeader(examNo, header) {
    rawDir := HGH_DIR . "\work\raw"
    FileCreateDir, %rawDir%
    rawFile := HGH_RawPath(examNo)

    FileDelete, %rawFile%
    FileAppend, %header%, %rawFile%, UTF-8
    if ErrorLevel {
        TrayTip, 高醫擷取, 檔頭寫檔失敗：%rawFile%`n（HGH_DIR 路徑對嗎？）, 6, 3
        return false
    }

    ; 家裡才做完整解析，這裡只做能便宜檢查的健全性判斷，避免存進一份沒用的檔頭
    missing := ""
    if (!InStr(header, "Manufacturer"))
        missing .= "廠牌 "
    if (!InStr(header, "Rows"))
        missing .= "解析度 "
    if (!InStr(header, "Study Date"))
        missing .= "拍攝日 "

    if (missing != "") {
        TrayTip, 高醫擷取, %examNo% 已存檔，但檔頭似乎缺：%missing%`n請確認抓的是完整檔頭, 6, 2
        return true
    }

    TrayTip, 高醫擷取, %examNo% 已擷取, 2, 1
    return true
}
