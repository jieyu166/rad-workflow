; ============================================================================
; 高醫腸阻塞資料擷取（一次性專案，收工後可整包移除）
;
; 依賴 test.ahk 的：ActivateHISLight()、OpenPACSImage()、GetDICOMData()、
;                   GetDICOMLineData()、CallDICOMWin
; 由「簡碼 jai.ahk」在 test.ahk 之後 #include。
;
; 功能一 Win+Shift+H：剪貼簿的申請單號 -> HIS(chk060) 開啟該檢查
; 功能二 Win+Shift+J：剪貼簿的申請單號 -> PACS 開影像 -> 抓 DICOM 檔頭 -> 存檔解析
; 除錯   Win+Shift+F1：列出 chk060 所有控件（第一次校正用）
; ============================================================================

; --- 需要校正的設定（第一次在醫院電腦跑之前先確認）---
global HGH_DIR := "C:\Users\jai16\OneDrive\00 放射科\5工作\rad-workflow-main\hgh-bowel"
global HGH_PYTHON := "python"
; chk060 上「查詢/確定」按鈕的控件名。用 Win+Shift+F1 確認後改這裡。
; 留空則改用送 {Enter} 觸發查詢。
global HGH_HIS_QUERY_BTN := ""
; INFINITT 載入影像的等待秒數，網路慢就調大
global HGH_PACS_WAIT := 6


; ============================================================================
; 功能一：申請單號 -> HIS 開啟檢查
; ============================================================================
<#+h::
    examNo := HGH_GetExamNoFromClipboard()
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
; 功能二：申請單號 -> PACS 開影像 -> 抓 DICOM 檔頭 -> 解析寫入 result.csv
; ============================================================================
<#+j::
    examNo := HGH_GetExamNoFromClipboard()
    if (examNo = "")
        return

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

    HGH_SaveAndParse(examNo, header)
return


; ============================================================================
; 除錯：列出 chk060 控件，用來確認查詢按鈕叫什麼
; ============================================================================
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

; 從剪貼簿取申請單號；剪貼簿沒有就對目前選取處按一次 Ctrl+C
HGH_GetExamNoFromClipboard() {
    examNo := RegExReplace(Clipboard, "\D")
    if (StrLen(examNo) < 8) {
        Clipboard := ""
        Send ^c
        ClipWait, 3
        examNo := RegExReplace(Clipboard, "\D")
    }
    if (StrLen(examNo) < 8) {
        TrayTip, 高醫擷取, 剪貼簿沒有可用的申請單號, 3, 3
        return ""
    }
    return examNo
}

; 存檔頭原文並呼叫 Python 解析（原文留著，之後改解析規則可重跑，不必再進 PACS）
HGH_SaveAndParse(examNo, header) {
    rawDir := HGH_DIR . "\work\raw"
    FileCreateDir, %rawDir%
    rawFile := rawDir . "\" . examNo . ".txt"

    FileDelete, %rawFile%
    FileAppend, %header%, %rawFile%, UTF-8
    if ErrorLevel {
        TrayTip, 高醫擷取, 檔頭寫檔失敗：%rawFile%, 4, 3
        return false
    }

    script := HGH_DIR . "\parse_dicom_header.py"
    RunWait, %ComSpec% /c ""%HGH_PYTHON%" "%script%" --file "%rawFile%"" > "%rawFile%.log" 2>&1, , Hide, pid
    exitCode := ErrorLevel

    if (exitCode = 0) {
        TrayTip, 高醫擷取, %examNo% 已擷取完成, 2, 1
    } else if (exitCode = 1) {
        TrayTip, 高醫擷取, %examNo% 已寫入但有缺漏欄位`n請看 %rawFile%.log, 5, 2
    } else {
        TrayTip, 高醫擷取, %examNo% 解析失敗（exit %exitCode%）`n請看 %rawFile%.log, 5, 3
    }
    return (exitCode <= 1)
}
