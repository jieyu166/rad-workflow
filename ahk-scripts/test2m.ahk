; ============================================================================
; test2m.ahk - 批量報告擷取工具（簡化版 - 只使用 IE 方法）
; 功能：從 Excel 批量讀取檢查單號並自動填入報告
; ============================================================================

#NoEnv
SetWorkingDir %A_ScriptDir%
SetBatchLines -1
#Persistent

; 確保包含必要的檔案（如果需要全局變數）
; #Include 簡碼 jai.ahk  ; 取得 LOGI 等全局變數

; 從設定檔讀取登入ID
IniRead, LOGI, %A_ScriptDir%\radiologist_settings.ini, Login, Username
if (LOGI = "ERROR" or LOGI = "") {
    MsgBox, 無法從 radiologist_settings.ini 讀取登入ID，請確認設定檔存在且包含 [Login] Username 欄位。
    ExitApp
}
global vExamLoc := 1     ; 1: 佳里, 0: 永康

; ============================================================================
; 主要熱鍵：Ctrl+Alt+R - 批量擷取報告
; ============================================================================

^!r::
BatchFetchReports:
    ; 輸入要處理的行數
    InputBox, numRows, 輸入行數, 請輸入需要處理的行數（最多100行）:, , 300, 150
    if (ErrorLevel or numRows = "" or numRows < 1 or numRows > 100) {
        return
    }
    
    ; 詢問伺服器位置
    InputBox, tempLoc, 伺服器位置, 請選擇伺服器位置`n永康 = 0`n佳里 = 1, , 300, 150, , , , 1
    if (ErrorLevel) {
        return
    }
    
    ; 設定伺服器位置
    vExamLoc := tempLoc
    
    ; 處理統計
    successCount := 0
    failCount := 0
    failList := ""
    
    ; 開始批量處理
    Loop, %numRows%
    {
        rowNum := A_Index
        
        ; 顯示進度
        ToolTip, 處理中... %rowNum%/%numRows%
        
        ; 取得 A 欄的檢查單號
        Send, {Home}
        Sleep, 100
        Send, ^c
        ClipWait, 2
        
        if ErrorLevel {
            failCount++
            failList .= "第 " . rowNum . " 行: 無法複製內容`n"
            Send, {Down}
            continue
        }
        
        examNo := Trim(Clipboard)
        
        ; 檢查檢查單號格式
        if (StrLen(examNo) < 8) {
            failCount++
            failList .= "第 " . rowNum . " 行: 無效的檢查單號 (" . examNo . ")`n"
            Send, {Down}
            continue
        }
        
        ; 只保留前15碼
        examNo := SubStr(examNo, 1, 15)
        
        ; 使用 IE 方法取得報告
        report := GetReportViaIE_Simple(examNo)
        
        ; 移動到 B 欄（往右兩欄）
        Send, {Right}{Right}
        Sleep, 100
        
        ; 填入報告內容
        Send, {F2}
        Sleep, 100
        
        if (report != "" && SubStr(report, 1, 5) != "Error") {
            ; 成功取得報告
            Clipboard := report
            Send, ^v
            Sleep, 10
            Send, {Enter}
            successCount++
        } else {
            ; 處理錯誤
            if (report = "") {
                Clipboard := "無法取得報告"
            } else {
                Clipboard := report
            }
            Send, ^v
            Sleep, 10
            Send, {Enter}
            failCount++
            failList .= "第 " . rowNum . " 行: " . examNo . " - 取得報告失敗`n"
        }
        
        ; 移動到下一行的 A 欄
        ;Send, {Tab}  ; 移到下一行
        Send, {Home}  ;{Down}
        Sleep, 10
    }
    ToolTip 	; 隱藏進度提示
    
    ; 顯示結果統計
    resultMsg := "處理完成！`n`n"
    resultMsg .= "成功: " . successCount . " 筆`n"
    resultMsg .= "失敗: " . failCount . " 筆 "
    
    if (failCount > 0 && failList != "") {
        resultMsg .= "`n`n 失敗詳情：`n" . failList
        
        ; 選擇性儲存失敗記錄
        MsgBox, 4, 儲存記錄, 是否要儲存失敗記錄到桌面？
        IfMsgBox Yes
        {
            FormatTime, logTime, , yyyyMMdd_HHmmss
            logFile := A_Desktop . "\批量報告失敗記錄_" . logTime . ".txt"
            FileAppend, %failList%, %logFile%
            MsgBox, 64, 儲存成功, 失敗記錄已儲存至：`n %logFile%
        }
    }
    
    MsgBox, 64, 處理結果, %resultMsg%
return

; ============================================================================
; 簡化的 IE 方法取得報告（唯一可用的方法）
; ============================================================================

GetReportViaIE_Simple(examNo) {
    global LOGI, vExamLoc
    
    ; 建立 URL
    if (vExamLoc = 1) {
        webUrl := "http://intranet.chimei.org.tw/intranet/chilin/rptdiff/demo_diff.asp?ihost=14&ichkcode=" . examNo . "&iitemseq=01&iuser=" . LOGI
    } else {
        webUrl := "http://intranet.chimei.org.tw/intranet/chilin/rptdiff/demo_diff.asp?ihost=10&ichkcode=" . examNo . "&iitemseq=01&iuser=" . LOGI
    }
    
    try {
        ; 創建 IE 物件
        wb := ComObjCreate("InternetExplorer.Application")
        wb.Visible := false  ; 隱藏瀏覽器視窗
        wb.Navigate(webUrl)
        
        ; 等待頁面載入完成（最多10秒）
        timeout := A_TickCount + 10000
        while (wb.ReadyState != 4 && A_TickCount < timeout) {
            Sleep 100
        }
        
        if (wb.ReadyState != 4) {
            wb.Quit()
            return "Error: 網頁載入超時"
        }
        
        ; 取得 HTML Document
        html := wb.Document
        
        ; 取得報告內容
        reportContent := ""
        
        ; 嘗試取得 text2 元素
        try {
            element := html.getElementById("text2")
            if (element) {
                reportContent := element.innerText
                if (reportContent = "") {
                    reportContent := element.value  ; 如果是 textarea
                }
            }
        }
        
        wb.Quit()
        
        ; 處理報告內容
        if (reportContent != "") {
            ; 移除第一行（通常是標題）
            pos := InStr(reportContent, "`n")
            if (pos) {
                reportContent := SubStr(reportContent, pos + 1)
            }
            
            ; 清理 HTML 實體
            reportContent := CleanHTMLEntities(reportContent)
            
            return reportContent
        } else {
            return " Error: 無法從網頁取得報告內容 "
        }
        
    } catch {
        ; 錯誤處理
        return "Error: IE 方法執行失敗"
    }
}

; ============================================================================
; HTML 實體清理函數
; ============================================================================

CleanHTMLEntities(text) {
    text := StrReplace(text, "&nbsp;", " ")
    text := StrReplace(text, "&lt;", "<")
    text := StrReplace(text, "&gt;", ">")
    text := StrReplace(text, "&amp;", "&")
    text := StrReplace(text, "&quot;", """")
    text := StrReplace(text, "&#13;&#10;", "`r`n")
    text := StrReplace(text, "&#13;", "`r")
    text := StrReplace(text, "&#10;", "`n")
    text := StrReplace(text, "&#x0D;&#x0A;", "`r`n")
    return text
}

; ============================================================================
; 輔助功能
; ============================================================================

; Ctrl+Alt+T：測試單一檢查單號
^!t::
TestSingleReport:
    InputBox, testExamNo, 測試報告擷取, 請輸入檢查單號:, , 300, 130
    if (ErrorLevel or testExamNo = "") {
        return
    }
    
    ; 詢問伺服器位置
    MsgBox, 4, 選擇伺服器, 使用佳里伺服器？`n`n是 = 佳里`n否 = 永康
    IfMsgBox Yes
        vExamLoc := 1
    else
        vExamLoc := 0
    
    ; 清理檢查單號
    testExamNo := SubStr(testExamNo, 1, 15)
    
    ; 顯示處理中
    ToolTip, 正在取得報告...
    
    ; 取得報告
    report := GetReportViaIE_Simple(testExamNo)
    
    ToolTip  ; 隱藏提示
    
    ; 顯示結果
    if (report != "" && SubStr(report, 1, 5) != "Error") {
        ; 成功取得報告
        reportPreview := SubStr(report, 1, 200)
        MsgBox, 64, 成功取得報告, 檢查單號: %testExamNo%`n`n報告內容（前200字）：`n%reportPreview%...`n`n是否要複製完整報告到剪貼簿？
        IfMsgBox OK
        {
            Clipboard := report
            MsgBox, 64, 複製成功, 報告已複製到剪貼簿！
        }
    } else {
        ; 顯示錯誤
        MsgBox, 48, 取得失敗, 檢查單號: %testExamNo%`n`n錯誤訊息：`n%report%
    }
return

; Ctrl+Alt+H：顯示說明
^!h::
ShowHelp:
    helpText := "批量報告擷取工具 使用說明`n"
    helpText .= "================================`n`n"
    helpText .= "功能：`n"
    helpText .= "從 Excel 批量讀取檢查單號並自動填入報告`n`n"
    helpText .= "使用方式：`n"
    helpText .= "1. 在 Excel 中，將檢查單號放在 A 欄`n"
    helpText .= "2. 選擇第一個要處理的儲存格（A欄）`n"
    helpText .= "3. 按 Ctrl+Alt+R 開始批量處理`n"
    helpText .= "4. 輸入要處理的行數（最多100行）`n"
    helpText .= "5. 選擇伺服器位置（0=永康, 1=佳里）`n"
    helpText .= "6. 程式會自動將報告填入 C 欄`n`n"
    helpText .= "其他熱鍵：`n"
    helpText .= "Ctrl+Alt+T - 測試單一檢查單號`n"
    helpText .= "Ctrl+Alt+H - 顯示此說明`n`n"
    helpText .= "注意事項：`n"
    helpText .= "- 確保已登入內部網路`n"
    helpText .= "- 處理大量資料時請耐心等待`n"
    helpText .= "- 每個報告需要約2-3秒處理時間 "
    
    MsgBox, 64, 使用說明, %helpText%
return

; ============================================================================
; 程式結束
; ============================================================================

; Esc 鍵：緊急停止
#IfWinActive, ahk_exe EXCEL.EXE
Esc::
    MsgBox, 4, 確認, 是否要停止批量處理？
    IfMsgBox Yes
    {
        Reload  ; 重新載入腳本以停止所有處理
    }
return
#IfWinActive