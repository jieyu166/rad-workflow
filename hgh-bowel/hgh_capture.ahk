; ============================================================================
; 高醫腸阻塞資料擷取（一次性專案，收工後可整包移除）
;
; 依賴 test.ahk 的：ActivateHISLight()、GetDICOMData()、CallDICOMWin
; 由「簡碼 jai.ahk」在 test.ahk 之後 #include。
;
; 用法：按 Win+Shift+G 開啟置頂小視窗（載入時不會自己跳出來）。
;       在試算表點選申請單號那一格（OpenOffice Calc / Excel 都支援；Office 365
;       網頁版沒有 COM，請改按 Ctrl+C），視窗會即時顯示抓到的單號與來源，
;       確認無誤再按按鈕。
;         按鈕1 / Win+Shift+H：該單號 -> HIS(chk060) 開啟檢查
;         按鈕2 / Win+Shift+J：讀「目前 INFINITT 顯示中」的影像檔頭，組成一整列
;                              （拍攝年/年齡/性別/空/空/解析度/廠牌/型號）複製到剪貼簿
;         按鈕3 / Win+Shift+F1：除錯，列出 chk060 控件
;       視窗關掉後再按 Win+Shift+G 叫回來。
;
; 醫院電腦不能跑 Python，所以這裡「只擷取、不解析」：檔頭原文存進 work\raw\，
; 回家後再用 parse_all_raw.py 解析、fill_mapping.py 回填 xlsx。
; work\ 在 OneDrive 底下，會自己同步回家。
; ============================================================================

; ---------------------------------------------------------------------------
; 需要校正的設定（第一次在醫院電腦跑之前先確認）
;
; 寫成函式而不是 global 變數，是因為本檔被 #include 的位置已經在 auto-execute
; 段之後（test.ahk 開頭就有熱鍵，auto-exec 在那裡就停了），頂層的賦值根本不會
; 執行。函式回傳值沒有這個問題。
; ---------------------------------------------------------------------------

; 本資料夾路徑。用 A_LineFile 取本檔自身位置推導，不要硬編——家用機是
; C:\Users\jai16\OneDrive\...，醫院機是 D:\jai166\Onedrive\...，硬編必錯一邊。
; （A_LineFile 在 #include 進來的檔案裡回傳的是「本檔」路徑，不是主腳本路徑。）
HGH_Dir() {
    SplitPath, A_LineFile, , thisDir
    return thisDir
}

; chk060 上「查詢/確定」按鈕的控件名。用按鈕3 查出來後填這裡。
; 留空則改用送 {Enter} 觸發查詢。
HGH_QueryBtn() {
    return ""
}

; 匯出圖片解析度。「解析度」欄指的是交付給高醫的 JPG 尺寸，不是 CT 矩陣——
; 實測本機 250 個 Case 資料夾、抽樣 500 張 JPG，全部是 512x512。
; 刻意不從 DICOM 的 Rows/Columns 取：兩者這次都是 512，但若某案矩陣是 768，
; DICOM 會給 768 而匯出的 JPG 仍是 512，那就填錯了。
; 範例檔用 * 不是 x（150*150）。
HGH_ExportResolution() {
    return "512*512"
}

HGH_Total() {
    return 368
}


; ============================================================================
; GUI
; ============================================================================
HGH_BuildGUI() {
    ; Gui Add 的 v 變數必須是 global 或 static，否則在函式裡會被當成區域變數，
    ; 載入時就報 "A control's variable must be global or static"。
    global HGH_StatusText, HGH_ProgressText

    Gui, HGH:New, +AlwaysOnTop +ToolWindow, 高醫腸阻塞擷取
    Gui, HGH:Font, s10, Microsoft JhengHei
    Gui, HGH:Add, Text, x12 y10 w300 vHGH_StatusText, 單號：(點選單號那格，或 Ctrl+C)
    Gui, HGH:Add, Text, x12 y34 w300 vHGH_ProgressText, 進度：--
    Gui, HGH:Add, Button, x12 y62 w300 h38 gHGH_Btn1, 1. 用此單號開 HIS 檢查
    Gui, HGH:Add, Button, x12 y104 w300 h38 gHGH_Btn2, 2. 讀目前影像 DICOM，複製整列
    Gui, HGH:Font, s9
    Gui, HGH:Add, Button, x12 y146 w300 h28 gHGH_Btn3, 3. 除錯：列出 chk060 控件
    Gui, HGH:Show, w324 h186, 高醫腸阻塞擷取
    SetTimer, HGH_UpdateStatus, 1000
    Gosub, HGH_UpdateStatus
}

; 重建而不是只 Show：視窗可能還沒被建立過（例如 auto-exec 那行被拿掉時）
<#+g::
    HGH_BuildGUI()
return

HGHGuiClose:
HGHGuiEscape:
    SetTimer, HGH_UpdateStatus, Off
    Gui, HGH:Hide
return

; 每秒把 Excel 目前選取格的單號與擷取進度顯示出來，按下按鈕前就能看出抓的對不對
HGH_UpdateStatus:
    hghSource := ""
    hghExam := HGH_GetExamNo(false, hghSource)
    if (hghExam = "")
        hghLine := "單號：(點選單號那格，或 Ctrl+C)"
    else
        hghLine := "單號：" . hghExam . "（" . hghSource . "）" . (HGH_IsCaptured(hghExam) ? "  [已擷取]" : "")
    GuiControl, HGH:, HGH_StatusText, %hghLine%
    GuiControl, HGH:, HGH_ProgressText, % "進度：" . HGH_CapturedCount() . " / " . HGH_Total()
return


; ============================================================================
; 功能一：申請單號 -> HIS 開啟檢查
; ============================================================================
HGH_Btn1:
<#+h::
    examNo := HGH_GetExamNo(true)
    if (examNo = "")
        return

    ; 單號要打在 TextBox12（不是 XB1_Summary 用的 TextBox9，那格是另一個用途）
    ActivateHISLight()
    ControlSetText, ThunderRT6TextBox12, %examNo%, ahk_exe chk060.exe
    if (HGH_QueryBtn() != "") {
        ControlClick, % HGH_QueryBtn(), ahk_exe chk060.exe
    } else {
        ControlFocus, ThunderRT6TextBox12, ahk_exe chk060.exe
        ControlSend, ThunderRT6TextBox12, {Enter}, ahk_exe chk060.exe
    }
    TrayTip, HIS, 已帶入單號 %examNo%, 2, 1
return


; ============================================================================
; 功能二：申請單號 -> PACS 開影像 -> 抓 DICOM 檔頭 -> 存成原始檔
; ============================================================================
; 不再自己開 PACS（那個連結目前不通）。請自行在 INFINITT 叫出該檢查的影像，
; 再按這顆按鈕，它讀「目前顯示中」的影像檔頭。
HGH_Btn2:
<#+j::
    header := GetDICOMData()
    if (Trim(header) = "") {
        TrayTip, 高醫擷取, 抓不到 DICOM 檔頭`n影像有顯示嗎？滑鼠座標對嗎？, 5, 3
        return
    }

    hdrAcc := RegExReplace(HGH_Tag(header, "0008,0050"), "\D")

    ; 若試算表那邊有選到單號，比對一下——這是取代「自動開圖」後僅存的防呆，
    ; 專門擋「試算表停在 Case 005，但 INFINITT 上顯示的是別案」。
    sheetSource := ""
    sheetAcc := HGH_GetExamNo(false, sheetSource)
    if (sheetAcc != "" && hdrAcc != "" && sheetAcc != hdrAcc) {
        MsgBox, 262196, 單號不符, 試算表選的是 %sheetAcc%（%sheetSource%）`n但影像檔頭是 %hdrAcc%`n`n仍要複製這筆嗎？
        IfMsgBox, No
            return
    }

    row := HGH_BuildRow(header)
    Clipboard := row
    ClipWait, 2

    if (hdrAcc != "")
        HGH_SaveHeader(hdrAcc, header)

    ; 解析度欄填的是匯出 JPG 尺寸（512*512，實測得來），這裡把 DICOM 的矩陣
    ; 一併顯示當交叉檢查——若矩陣不是 512，代表這案的 CT 與匯出尺寸不同，值得留意。
    matrix := HGH_Matrix(header)
    TrayTip, 已複製整列（可直接貼 C 欄）, %row%`n`nDICOM 矩陣 %matrix%（應為 512x512）, 10, 1

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

; 取申請單號。不讀滑鼠位置——按鈕一按滑鼠就離開儲存格了；選取狀態不受焦點轉移影響。
;
; 依序試三個來源，因為三台環境不一樣：
;   1. OpenOffice / LibreOffice Calc（醫院）— 走 UNO
;   2. Excel（家用）— 走 COM
;   3. 剪貼簿 — Office 365 網頁版沒有 COM，只能靠 Ctrl+C
; source 會帶回實際來源，顯示在狀態列上。剪貼簿的內容可能是舊的，
; 標示來源才看得出這個數字能不能信。
HGH_GetExamNo(complain := true, ByRef source := "") {
    source := ""

    examNo := HGH_FirstCellDigits(HGH_ReadCalcCell())
    if (StrLen(examNo) >= 8) {
        source := "Calc"
        return examNo
    }

    examNo := HGH_FirstCellDigits(HGH_ReadExcelCell())
    if (StrLen(examNo) >= 8) {
        source := "Excel"
        return examNo
    }

    examNo := HGH_FirstCellDigits(Clipboard)
    if (StrLen(examNo) >= 8) {
        source := "剪貼簿"
        return examNo
    }

    if (complain)
        TrayTip, 高醫擷取, 取不到申請單號`n請點選單號那一格；網頁版試算表請先 Ctrl+C, 4, 3
    return ""
}

; 只取第一格：選到整列時 getString() 會用 Tab/換行串起多格，
; 直接抽數字會把好幾格黏成一個假單號。
HGH_FirstCellDigits(text) {
    StringReplace, text, text, `r, `n, All
    firstLine := StrSplit(text, "`n")[1]
    firstCell := StrSplit(firstLine, A_Tab)[1]
    return RegExReplace(firstCell, "\D")
}

; OpenOffice / LibreOffice Calc（需要 Calc 正在執行且開著該檔）
HGH_ReadCalcCell() {
    try {
        sm := ComObjActive("com.sun.star.ServiceManager")
        desktop := sm.createInstance("com.sun.star.frame.Desktop")
        doc := desktop.getCurrentComponent()
        return doc.getCurrentSelection().getString()
    } catch e {
        return ""
    }
}

HGH_ReadExcelCell() {
    try {
        xl := ComObjActive("Excel.Application")
        return xl.ActiveCell.Value
    } catch e {
        return ""
    }
}

; 依 DICOM tag 取單一值。不能用 GetDICOMLineData("Manufacturer")——它用 InStr
; 比對且不 break，"Manufacturer" 會同時命中 "Manufacturer Model Name"，
; 最後一筆勝出，結果拿到型號而不是廠牌。用 tag 就沒有這個歧義。
HGH_Tag(header, tag) {
    lines := StrSplit(StrReplace(header, "`r", ""), "`n")
    for i, line in lines {
        if (!InStr(line, tag))
            continue
        ; 值可能在同一行的 |...|，也可能在下一行（INFINITT 版面）
        if (RegExMatch(line, "\|([^|]*)\|", same))
            return Trim(same1)
        if (i < lines.Length() && RegExMatch(lines[i + 1], "\|([^|]*)\|", next))
            return Trim(next1)
        return ""
    }
    return ""
}

; DICOM 影像矩陣，只用來當交叉檢查顯示，不填進表格
HGH_Matrix(header) {
    rows := RegExReplace(HGH_Tag(header, "0028,0010"), "\D")
    cols := RegExReplace(HGH_Tag(header, "0028,0011"), "\D")
    return (rows != "" && cols != "") ? rows . "x" . cols : "(無)"
}

; 組出可直接貼進試算表 C 欄的一整列（Tab 分隔）：
; 拍攝年 / 年齡 / 性別 / 種族(空) / 就醫來源(空) / 解析度 / CT廠牌 / CT型號
HGH_BuildRow(header) {
    studyDate := RegExReplace(HGH_Tag(header, "0008,0020"), "\D")
    year := (StrLen(studyDate) >= 4) ? SubStr(studyDate, 1, 4) : ""

    ; PatientAge 形如 065Y，去掉前導零；沒有就用出生日期跟檢查日期推算
    age := ""
    rawAge := HGH_Tag(header, "0010,1010")
    if (RegExMatch(rawAge, "0*(\d{1,3})\s*[YyMmWwDd]?", a))
        age := (InStr(rawAge, "Y") || !RegExMatch(rawAge, "[MmWwDd]")) ? a1 + 0 : 0
    else {
        birth := RegExReplace(HGH_Tag(header, "0010,0030"), "\D")
        if (StrLen(birth) = 8 && StrLen(studyDate) = 8) {
            age := SubStr(studyDate, 1, 4) - SubStr(birth, 1, 4)
            if (SubStr(studyDate, 5, 4) < SubStr(birth, 5, 4))
                age -= 1
        }
    }

    ; 性別填「1.男」/「2.女」完整字串——依最終目標檔（紀錄資料之確認.xlsx）
    ; Case 002 那筆已填好的實例，儲存格內容就是「1.男」，不是數字 1。
    sexRaw := SubStr(Trim(HGH_Tag(header, "0010,0040")), 1, 1)
    StringUpper, sexRaw, sexRaw
    sex := (sexRaw = "M") ? "1.男" : (sexRaw = "F") ? "2.女" : ""

    maker := Trim(HGH_Tag(header, "0008,0070"))
    model := Trim(HGH_Tag(header, "0008,1090"))

    ; 種族與就醫來源留空（手動填），所以中間是兩個連續 Tab
    line := year . A_Tab . age . A_Tab . sex . A_Tab . A_Tab . A_Tab
    line .= HGH_ExportResolution() . A_Tab . maker . A_Tab . model
    return line
}

HGH_RawPath(examNo) {
    return HGH_Dir() . "\work\raw\" . examNo . ".txt"
}

HGH_IsCaptured(examNo) {
    return FileExist(HGH_RawPath(examNo)) ? true : false
}

HGH_CapturedCount() {
    count := 0
    rawDir := HGH_Dir() . "\work\raw"
    Loop, %rawDir%\*.txt
        count += 1
    return count
}

; 存檔頭原文。解析留到家裡做——醫院電腦沒有 Python，而且原文留著才能在
; 解析規則改動後重跑，不必再進 PACS 一次。
HGH_SaveHeader(examNo, header) {
    rawDir := HGH_Dir() . "\work\raw"
    FileCreateDir, %rawDir%
    rawFile := HGH_RawPath(examNo)

    FileDelete, %rawFile%
    FileAppend, %header%, %rawFile%, UTF-8
    if ErrorLevel {
        TrayTip, 高醫擷取, 檔頭寫檔失敗：%rawFile%`n（HGH_Dir() 的路徑設定對嗎？）, 6, 3
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
