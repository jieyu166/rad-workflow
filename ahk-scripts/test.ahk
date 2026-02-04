; 方法2: 使用 #If 指令 (更優雅的方式)
#If (varWhere = 5 or varWhere = 8)
F5::LWin
#If


; 系統提示訊息
TrayTip, 快速鍵, [Win]+[R]病歷彙總`n[Win]+[A]按暫存`n[Win]+[S]下一個`n[Win]+[D]Copy報告/比較(佳里)`n[Win]+[F]Copy報告/比較`n[Win]+[Z]Copy 上次檢查日期(DICOM)`n[Win]+[X]抓上次報告(佳里)`n[Win]+[V]開影像`n[Win]+[M]Copy 上次檢查日期`n[Win]+[P]比較兩column, 20, 17

; ============================================================================
; 基礎功能函數區
; ============================================================================

; --- 視窗啟動函數 ---
ActivateHIS() {
    WinActivate ahk_exe chk060.exe
}

ActivatePACS() {
    WinGet, id, list, INFINITT PACS
    num := 2
    this_id := id%num%
    WinActivate, ahk_id %this_id%
}

; ============================================================================
; DICOM 相關函數區
; ============================================================================

; --- DICOM 資料取得函數 ---
GetDICOMData() {
    ; 取得 DICOM 檔頭資訊並返回
    gosub CallDICOMWin
    return clipboard
}
GetDICOMLineData(Attrib := "", text := ""){
    tmp := StrSplit(text, "`n")
	res := ""
    for index, textline in tmp 
        if (InStr(textline, Attrib))
             res:= tmp[index+1]
	 if (res != "") {
        tmp2 := StrSplit(res, "|")
			return tmp2[2]
    }
}

; 取得 DICOM 日期（不影響 HIS）
GetDICOMDateOnly(text := "") {
    ClipboardBackup := Clipboard
    if (text = ""){
		text := GetDICOMData()
	}

    dateStr := GetDICOMLineData("Study Date", text)
    timeStr := GetDICOMLineData("Acquisition Time", text)

    
    ; 格式化日期和時間
    if (dateStr != "") {
        RegExMatch(dateStr , "(\d+)", tmp3)
        formattedDate := SubStr(tmp3, 1, 4) . "." . SubStr(tmp3, 5, 2) . "." . SubStr(tmp3, 7, 2)
    }
    
    if (timeStr != "") {
        RegExMatch(timeStr, "(\d+)", tmp3T)
        formattedTime := SubStr(tmp3T, 1, 2) . ":" . SubStr(tmp3T, 3, 2)
    }
    
    Clipboard := ClipboardBackup
    
    result := {}
    result.date := formattedDate
    result.time := formattedTime
    result.full := formattedDate . " " . formattedTime
    
    return result
}

; 取得 Accession Number
GetAccessionNumber(text := "") {
    ClipboardBackup := Clipboard
	if(text = ""){
		text := GetDICOMData()
	}
	accessionNum:=GetDICOMLineData("accession number", clipboard)
    accessionNum := RegExReplace(accessionNum, "\D")  ; \D = 非數字
    Clipboard := ClipboardBackup
    return accessionNum
}

; ============================================================================
; 報告相關函數區
; ============================================================================

; 取得舊報告（透過網頁，不開啟瀏覽器）; ============================================================================
; 修正版本的 GetOldReportContent 函數
; ============================================================================

; 取得舊報告內容（加強版，含除錯）
GetOldReportContent(examNo := "", showDebug := false) {
    ; Step 1: 取得 Accession Number
    if (examNo = "") {
        examNo := GetAccessionNumber()
        if (showDebug) {
            MsgBox, 0, Debug Step 1, Accession Number: %examNo%
        }
    }
    
    ; 檢查 examNo 是否有效
    if (examNo = "" || examNo = 0) {
        if (showDebug) {
            MsgBox, 0, Debug Error, 無法取得 Accession Number
        }
        return ""
    }
    
    ; Step 2: 建立網址
    if(vExamLoc = 1) {
        webUrl := "http://intranet.chimei.org.tw/intranet/chilin/rptdiff/demo_diff.asp?ihost=14&ichkcode=" examNo "&iitemseq=01&iuser=" . LOGI
    } else {
        webUrl := "http://intranet.chimei.org.tw/intranet/chilin/rptdiff/demo_diff.asp?ihost=10&ichkcode=" examNo "&iitemseq=01&iuser=" . LOGI
    }
    
    if (showDebug) {
        MsgBox, 0, Debug Step 2, URL: %webUrl%
    }
    
    
    ; Step 4: 嘗試方法2 - 使用 WinHttpRequest
    reportContent := GetReportViaHTTP(webUrl, showDebug)
    
    if (reportContent != "") {
        if (showDebug) {
            MsgBox, 0, Debug Success, 成功使用 HTTP 取得報告
        }
        return reportContent
    }
    
    ; Step 5: 嘗試方法3 - 使用 MSXML2
    reportContent := GetReportViaMSXML(webUrl, showDebug)
    
    if (reportContent != "") {
        if (showDebug) {
            MsgBox, 0, Debug Success, 成功使用 MSXML 取得報告
        }
        return reportContent
    }
    
    ; Step 3: 嘗試方法1 - 使用 IE COM Object
    reportContent := GetReportViaIE(webUrl, showDebug)
    
    if (reportContent != "") {
        if (showDebug) {
            MsgBox, 0, Debug Success, 成功使用 IE 取得報告
        }
        return reportContent
    }
	
	
    if (showDebug) {
        MsgBox, 0, Debug Failed, 所有方法都失敗了
    }
    
    return ""
}

; 方法1：使用 IE COM Object（最可靠）
GetReportViaIE(webUrl, showDebug := false) {
    try {
        ; 創建 IE 物件
        wb := ComObjCreate("InternetExplorer.Application")
        wb.Visible := false  ; 隱藏瀏覽器
        wb.Navigate(webUrl)
        
        ; 等待載入完成（加入超時機制）
        timeout := A_TickCount + 10000  ; 10秒超時
        while (wb.ReadyState != 4 && A_TickCount < timeout) {
            Sleep 100
        }
        
        if (wb.ReadyState != 4) {
            if (showDebug) {
                MsgBox, 0, Debug IE, IE 載入超時
            }
            wb.Quit()
            return ""
        }
        
        ; 取得 HTML Document
        html := wb.Document
        
        ; 嘗試多種方式取得 text2 內容
        reportContent := ""
        
        ; 方法A: getElementById
        try {
            element := html.getElementById("text2")
            if (element) {
                reportContent := element.innerText
                if (reportContent = "") {
                    reportContent := element.value  ; 如果是 textarea
                }
            }
        }
        
        ; 方法B: 如果方法A失敗，嘗試用 getElementsByName
        if (reportContent = "") {
            try {
                elements := html.getElementsByName("text2")
                if (elements.length > 0) {
                    reportContent := elements[0].innerText
                    if (reportContent = "") {
                        reportContent := elements[0].value
                    }
                }
            }
        }
        
        ; 方法C: 嘗試解析整個 HTML
        if (reportContent = "") {
            try {
                htmlText := html.documentElement.outerHTML
                if RegExMatch(htmlText, "id=['""]text2['""][^>]*>([^<]+)", match) {
                    reportContent := match1
                } else if RegExMatch(htmlText, "<textarea[^>]*id=['""]text2['""][^>]*>(.*?)</textarea>", match) {
                    reportContent := match1
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
            
            ; 移除 HTML 實體
            reportContent := StrReplace(reportContent, "&nbsp;", " ")
            reportContent := StrReplace(reportContent, "&lt;", "<")
            reportContent := StrReplace(reportContent, "&gt;", ">")
            reportContent := StrReplace(reportContent, "&amp;", "&")
            
            if (showDebug) {
                ; 修正：先計算長度再顯示
                contentLength := StrLen(reportContent)
                MsgBox, 0, Debug IE Content, 取得內容長度: %contentLength%
            }
        }
        
        return reportContent
        
    } catch e {
        if (showDebug) {
            ; 修正：先取得錯誤訊息再顯示
            errorMsg := e.message
            MsgBox, 0, Debug IE Error, IE 錯誤: %errorMsg%
        }
        return ""
    }
}

; 方法2：使用 WinHttpRequest
GetReportViaHTTP(webUrl, showDebug := false) {
    try {
        whr := ComObjCreate("WinHttp.WinHttpRequest.5.1")
        whr.Open("GET", webUrl, false)
        whr.SetRequestHeader("User-Agent", "Mozilla/5.0")
        whr.Send()
        
        ; 修正：先取得 Status
        httpStatus := whr.Status
        if (httpStatus != 200) {
            if (showDebug) {
                MsgBox, 0, Debug HTTP, HTTP Status: %httpStatus%
            }
            return ""
        }
        
        htmlContent := whr.ResponseText
        
        ; 解析 HTML 內容
        reportContent := ""
        
        ; 嘗試多種正則表達式
        if RegExMatch(htmlContent, "id=['""]text2['""][^>]*>([^<]+)", match) {
            reportContent := match1
        } else if RegExMatch(htmlContent, "<textarea[^>]*id=['""]text2['""][^>]*>(.*?)</textarea>", match) {
            reportContent := match1
        } else if RegExMatch(htmlContent, "name=['""]text2['""][^>]*>([^<]+)", match) {
            reportContent := match1
        } else if RegExMatch(htmlContent, "<textarea[^>]*name=['""]text2['""][^>]*>(.*?)</textarea>", match) {
            reportContent := match1
        }
        
        if (reportContent != "") {
            ; 處理 HTML 實體
            reportContent := StrReplace(reportContent, "&nbsp;", " ")
            reportContent := StrReplace(reportContent, "&lt;", "<")
            reportContent := StrReplace(reportContent, "&gt;", ">")
            reportContent := StrReplace(reportContent, "&amp;", "&")
            reportContent := StrReplace(reportContent, "&#13;&#10;", "`r`n")
            reportContent := StrReplace(reportContent, "&#13;", "`r")
            reportContent := StrReplace(reportContent, "&#10;", "`n")
            
            ; 移除第一行
            pos := InStr(reportContent, "`n")
            if (pos) {
                reportContent := SubStr(reportContent, pos + 1)
            }
            
            if (showDebug) {
                ; 修正：先計算長度再顯示
                contentLength := StrLen(reportContent)
                MsgBox, 0, Debug HTTP Content, 取得內容長度: %contentLength%
            }
        }
        
        return reportContent
        
    } catch e {
        if (showDebug) {
            ; 修正：先取得錯誤訊息再顯示
            errorMsg := e.message
            MsgBox, 0, Debug HTTP Error, HTTP 錯誤: %errorMsg%
        }
        return ""
    }
}

; 方法3：使用 MSXML2
GetReportViaMSXML(webUrl, showDebug := false) {
    try {
        xmlhttp := ComObjCreate("MSXML2.XMLHTTP")
        xmlhttp.Open("GET", webUrl, false)
        xmlhttp.Send()
        
        ; 修正：先取得 Status
        xmlStatus := xmlhttp.Status
        if (xmlStatus != 200) {
            if (showDebug) {
                MsgBox, 0, Debug MSXML, MSXML Status: %xmlStatus%
            }
            return ""
        }
        
        htmlContent := xmlhttp.ResponseText
        
        ; 解析內容
        reportContent := ""
        
        ; 嘗試多種正則表達式
        if RegExMatch(htmlContent, "s)id=['""]text2['""][^>]*>([^<]+)", match) {
            reportContent := match1
        } else if RegExMatch(htmlContent, "s)<textarea[^>]*id=['""]text2['""][^>]*>(.*?)</textarea>", match) {
            reportContent := match1
        } else if RegExMatch(htmlContent, "s)name=['""]text2['""][^>]*>([^<]+)", match) {
            reportContent := match1
        } else if RegExMatch(htmlContent, "s)<textarea[^>]*name=['""]text2['""][^>]*>(.*?)</textarea>", match) {
            reportContent := match1
        }
        
        if (reportContent != "") {
            ; 處理 HTML 實體
            reportContent := StrReplace(reportContent, "&nbsp;", " ")
            reportContent := StrReplace(reportContent, "&lt;", "<")
            reportContent := StrReplace(reportContent, "&gt;", ">")
            reportContent := StrReplace(reportContent, "&amp;", "&")
            
            ; 移除第一行
            pos := InStr(reportContent, "`n")
            if (pos) {
                reportContent := SubStr(reportContent, pos + 1)
            }
            
            if (showDebug) {
                ; 修正：先計算長度再顯示
                contentLength := StrLen(reportContent)
                MsgBox, 0, Debug MSXML Content, 取得內容長度: %contentLength%
            }
        }
        
        return reportContent
        
    } catch e {
        if (showDebug) {
            ; 修正：先取得錯誤訊息再顯示
            errorMsg := e.message
            MsgBox, 0, Debug MSXML Error, MSXML 錯誤: %errorMsg%
        }
        return ""
    }
}

; 開啟報告比對網頁
OpenReportComparison(examNo := "") {
    if (examNo = "") {
        examNo := GetAccessionNumber()
    }
    
    if(vExamLoc = 1) {
        url := "http://intranet.chimei.org.tw/intranet/chilin/rptdiff/demo_diff.asp?ihost=14&ichkcode=" examNo "&iitemseq=01&iuser=" . LOGI
    } else {
        url := "http://intranet.chimei.org.tw/intranet/chilin/rptdiff/demo_diff.asp?ihost=10&ichkcode=" examNo "&iitemseq=01&iuser=" . LOGI
    }
    
    Run, msedge.exe %url%
}

; ============================================================================
; 滑鼠位置函數區（根據不同工作地點）
; ============================================================================

; DICOM 左螢幕位置
PosDICOMLU:
    if(varWhere=1) {
        MouseMove 3286, 986     ; 佳里學姊
    } else if(varWhere=2) {
        MouseMove 3000,150        ; 佳里座位
		;MouseMove 3200,120        ; 佳里座位125%
    } else if(varWhere=3) {
        MouseMove 0,0           ; 第三VS辦公室(佳里)
    } else if(varWhere=4) {
        MouseMove 3000,-400     ; 第三VS辦公室(柳營)
    } else if(varWhere=5) {
        MouseMove -2100,170     ; 遠端
    } else if(varWhere=6) {
        MouseMove 50,30         ; R小房間(Win7)
    } else if(varWhere=7) {
        MouseMove 4300,-1000      ; 乳醫(Win12)
    } else if(varWhere=8) {
        MouseMove 3360,370           ; 遠端(租屋)
    } else {
        MouseMove 620,40        ; 預設位置
    }
return

; DICOM 右螢幕位置
PosDICOMRU:
    if(varWhere=1) {
        MouseMove 4793, 940     ; 佳里學姊
    } else if(varWhere=2) {
        MouseMove 4400,150        ; 佳里座位
		;MouseMove 4800,140        ; 佳里座位125%
    } else if(varWhere=3) {
        MouseMove 4450,700      ; 第三VS佳里
    } else if(varWhere=4) {
        MouseMove 4400,-200     ; 第三VS希城
    } else if(varWhere=5) {
        MouseMove -300,250     ; 遠端
    } else if(varWhere=6) {
        MouseMove 4400,500      ; R小房間
    } else if(varWhere=7) {
        MouseMove 7350,-1000      ; 12F乳醫
    } else if(varWhere=8) {
        MouseMove 4350,380      ; 遠端(租屋)
    }
return

; DICOM 按鈕位置
PosDICOMButton:
    if(varWhere=1) {
        MouseMove 4400,150     ; 佳里學姊
    } else if(varWhere=2) {
        ;MouseMove 4400,-310     ; 佳里100%
		MouseMove 4400,-305     ; 佳里
    } else if(varWhere=3) {
        MouseMove 4400,150      ; 第三VS佳里
    } else if(varWhere=4) {
        MouseMove 4400,-800     ; 第三VS希城
    } else if(varWhere=5) {
        MouseMove -3760,550      ; 遠端
    } else if(varWhere=6) {
        MouseMove 4400,145      ; 小房間
    } else if(varWhere=7) {
        MouseMove 6560,-1890      ; 12F乳醫
    } else if(varWhere=8) {
        MouseMove 2650,700      ; 3F學長座位
    }
return

; ============================================================================
; 核心操作子程序
; ============================================================================

; 呼叫 DICOM 視窗並複製內容（右螢幕）
CallDICOMWin:
    MouseGetPos, tmpX2, tmpY2
    gosub PosDICOMRU
    Send {LButton}
    gosub PosDICOMButton
    Send {LButton}
    gosub PosDICOMRU
    Send {LButton}
    Send {LButton}{LButton}
    WinWaitActive, DICOM 檔頭訊息, , 2
    ControlGetText, clipboard, Edit3, DICOM 檔頭訊息
    ClipWait
    Sleep 10
    Send {Esc}{Esc}
    DllCall("SetCursorPos", "int", tmpX2, "int", tmpY2)
return

; 呼叫 DICOM 視窗並複製內容（左螢幕）
CallDICOMWinL:
    MouseGetPos, tmpX, tmpY
    gosub PosDICOMLU
    Send {LButton}
    gosub PosDICOMButton
    Send {LButton}
    gosub PosDICOMLU
    Send {LButton}
    Send {LButton}{LButton}
    WinWaitActive, DICOM 檔頭訊息, , 2
    ControlGetText, clipboard, Edit3, DICOM 檔頭訊息
    ClipWait
    Sleep, 120
    Send {Esc}{Esc}
    DllCall("SetCursorPos", "int", tmpX, "int", tmpY)
return

; ============================================================================
; 熱鍵定義區
; ============================================================================

; --- 視窗置頂 ---
^#SPACE::Winset, Alwaysontop, , A

; --- 送出檢查並開啟下一個 ---
*F12::
<#a::
    ActivateHIS()
    Send !t
    Send !a
    
    MsgBox, 262180, NEXT EXAM, "Would you like to continue next exam?"
    IfMsgBox, No
        return
    
    ActivateHIS()
    MouseGetPos, tmpX, tmpY
    CoordMode, Mouse, Window
    
    ; 根據不同地點調整滑鼠位置
    if(varWhere=1) {
        MouseMove 770, 43       ; R辦公室
    } else if(varWhere=3 or varWhere=4) {
        MouseMove 780,50       ; 第三VS
    } else if(varWhere=2) {
        ;MouseMove 620,40       ; 佳里100%
		MouseMove 770,50       ; 佳里125%
    } else if(varWhere=5) {
        MouseMove 1245,80       ; 遠端
    } else if(varWhere=6) {
        MouseMove 580,30       ; R小房間
    } else if(varWhere=7) {
        MouseMove 770,50       ; 乳醫
    } else if(varWhere=8) {
        MouseMove 1250,80       ; 第三VS(國勳)
    }
    
    Send {LButton}
    CoordMode, Mouse, Screen
    DllCall("SetCursorPos", "int", tmpX, "int", tmpY)
return

; --- 查看病歷彙總 ---
<#r::
    ControlGetText, ExamNo, ThunderRT6TextBox9, ahk_exe chk060.exe
    ChartNo := SubStr(ExamNo, 1, 8)
    url := "http://jlmrs.chimei.org.tw/EPR/sub_entry.asp?ihosp=14&ipatient=" . ChartNo . "&imode=&ftype=&iclass=0&from=4130&multiscreen="
    Run, msedge.exe %url%
return


; --- 查看舊報告（開瀏覽器）---
<#x::
    MsgBox, 262180, NEXT EXAM, "Open browser and see result?"
    IfMsgBox, No
        goto CopyOld
    gosub SeeOld
return

; --- 複製舊報告到 HIS ---
<#2::
CopyOld:
	dicom := GetDICOMData()
	accessionNum := GetAccessionNumber(dicom)
    dateInfo := GetDICOMDateOnly(dicom)	
    desc := "Comparison with previous study: " . dateInfo.full . ". _`r"
    CopyCXRtoHISWithParam(1)
	
	desc :=  GetOldReportContent(accessionNum, false) 
    desc := RegExReplace(desc, "(\r\n|\n|\r)", "`n")
    CopyCXRtoHISWithParam(1)
return

; --- 查看 AI 報告 ---
<#1::
SeeCXRAI:
    MouseGetPos, tmpX, tmpY
    gosub PosDICOMLU
	gosub PosDICOMLU
    Send {LButton}
    Sleep, 10
    Send g
    Sleep, 10
    Send 2
    DllCall("SetCursorPos", "int", tmpX, "int", tmpY)
return


; --- 複製舊報告日期 ---
<#c::
^F3::
calldate:
	dicomData := GetDICOMData()
    dateInfo := GetDICOMDateOnly(dicomData)
    desc := "Comparison with previous study: " . dateInfo.full . ". _`r"
    CopyCXRtoHISWithParam(1)
return

; --- 查看舊報告網頁 ---
SeeOld:
    OpenReportComparison(GetAccessionNumber())
return

; --- 複製影像序列資訊 ---
<#q::
    MsgBox, 262180, NEXT EXAM, "Open Left or Right?"
    IfMsgBox, No
        gosub CallDICOMWin
    IfMsgBox, Yes
        gosub CallDICOMWinL
    
	text := clipboard
	tmp2:=GetDICOMLineData("Series Number", text)
	tmp3:=GetDICOMLineData("Instance Number", text)
    
    desc := "(Srs/Img:" . tmp2 . "/" . tmp3 . ")"
    CopyCXRtoHISWithParam(0)
return


; --- 切換視窗快捷鍵 ---
^+a::ActivateHIS()
^+s::ActivatePACS()

; --- 視窗置頂開關 ---
<#t::Winset, Alwaysontop, , A

; --- 顯示滑鼠座標（除錯用）---
*F11::
    MouseGetPos, X, Y
    Msgbox, Your Cursor is at X: %X% Y: %Y% Mode %A_CoordModeMouse%
return

; --- 複製報告（透過網頁比對）---
<#d::
    clipboard := ""
    Send ^c
    ClipWait
    ExamNo := clipboard
    clipboard := GetOldReportContent(ExamNo, 0)
	ClipWait, 100
	Send {Right}{Right}
	Send {F2}
	Send ^v
	Send {Enter}
	Send {Home}
return
; ============================================================================
; 輔助子程序（保留用於 gosub）
; ============================================================================


; 僅用於從 DICOM 複製 Accession Number
DICOMCopyNum:
    tmp2 := StrSplit(tmp2, "|")
    RegExMatch(tmp2[2], "(\d+)", tmp3)
    ExamNo := tmp3
    
    if(vExamLoc = 1) {
        tmp := "http://intranet.chimei.org.tw/intranet/chilin/rptdiff/demo_diff.asp?ihost=14&ichkcode=" ExamNo "&iitemseq=01&iuser=" . LOGI
    } else {
        tmp := "http://intranet.chimei.org.tw/intranet/chilin/rptdiff/demo_diff.asp?ihost=10&ichkcode=" ExamNo "&iitemseq=01&iuser=" . LOGI
    }
    
    wb := ComObjCreate("InternetExplorer.Application")
    wb.Visible := true
    wb.Navigate(tmp)
    
    while wb.ReadyState <> 4
        Sleep 10
    
    html := wb.Document
    clipboard := html.getElementById("text2").innerText
    pos := InStr(clipboard, "`n")
    if pos
        clipboard := SubStr(clipboard, pos + 1)
    
    ComObjConnect(wb)
    wb.Quit()
return

::tescp::  
; 主要熱鍵：開啟*下面的檢查
    SortAndOpenNextExam()
return

; 簡化版檢查切換腳本 - 點擊檢查敘述然後開啟*下面那列檢查

SortAndOpenNextExam() {
    WinTitle := "ahk_class #32770"
    
	; 開啟選單
	gosub PosDICOMButton
	MouseMove, 400, 40, 0, R  ; R = Relative 相對移動
	Send {LButton}
	Sleep, 200
	
    ; 檢查窗口是否存在
    if !WinExist(WinTitle) {
        MsgBox, 16, 錯誤, 找不到檢查列表窗口
        return false
    }
    
    ; 激活窗口
    WinActivate, %WinTitle%
    Sleep, 200
    
    ; 先進行排序
    SortListView(WinTitle)
    Sleep, 500  ; 等待排序完成
    
    ; 找到標有*的當前開啟檢查
    CurrentRow := GetCurrentOpenExam(WinTitle)
    
    if (CurrentRow = 0) {
        MsgBox, 48, 提示, 找不到當前開啟的檢查項目（沒有找到*標記）
        return false
    }
    
    ; 計算下一行的行號
    NextRow := CurrentRow + 1
    
    ; 檢查下一行是否存在
    ControlGet, TotalRows, List, Count, SysListView321, %WinTitle%
    
    if (NextRow > TotalRows) {
        MsgBox, 48, 提示, 這已經是最後一個檢查項目了
        return false
    }
    
    ; 獲取下一行的資料
    ControlGet, NextItemText, List, %NextRow%, SysListView321, %WinTitle%
    
    if (NextItemText = "") {
        MsgBox, 48, 提示, 無法獲取下一個檢查項目的資料
        return false
    }
    
    ; 點擊下一行來選中它
    ClickRow(WinTitle, NextRow)
    
    return true
}

; ListView 排序函數
SortListView(WinTitle) {
    ; 方法1: 點擊日期欄位標題進行排序
    ; 假設日期欄位在第3欄，點擊欄位標題
    ControlClick, x800 y30, %WinTitle%,, Left, 1  ; 調整x座標到日期欄位標題
    Sleep, 100
    
    return true
}
; 主要函數：開啟*標記下面的檢查

; 找到標有*的當前開啟檢查行號
GetCurrentOpenExam(WinTitle) {
    ControlGet, AllItems, List,, SysListView321, %WinTitle%
    
    LineNumber := 1
    Loop, Parse, AllItems, `n
    {
        ; 檢查行首是否有*符號
        if (SubStr(A_LoopField, 1, 1) = "*") {
            return LineNumber
        }
        LineNumber++
    }
    
    return 0  ; 沒找到
}

; 除錯：顯示當前開啟項目信息
::tescp2:: ; 顯示所有項目（用於除錯）
    WinTitle := "ahk_class #32770"
    if !WinExist(WinTitle) {
        MsgBox, 窗口不存在
        return
    }
    
    CurrentRow := GetCurrentOpenExam(WinTitle)
    
    if (CurrentRow = 0) {
        MsgBox, 找不到標有*的當前開啟檢查
        return
    }
    
    ControlGet, CurrentItemText, List, %CurrentRow%, SysListView321, %WinTitle%
    ControlGet, TotalRows, List, Count, SysListView321, %WinTitle%
    
    NextRow := CurrentRow + 1
    NextItemText := ""
    if (NextRow <= TotalRows) {
        ControlGet, NextItemText, List, %NextRow%, SysListView321, %WinTitle%
    }
    
    MsgBox, 除錯資訊:`n`n當前行號: %CurrentRow%`n總行數: %TotalRows%`n`n當前項目:`n%CurrentItemText%`n`n下一個項目:`n%NextItemText%
return



; 手動排序（點擊不同欄位）
::tescp4::
    WinTitle := "ahk_class #32770"
    if WinExist(WinTitle) {
        WinActivate, %WinTitle%
        Sleep, 100
        
        ; 顯示選擇對話框
        MsgBox, 4, 選擇排序方式, 請選擇排序方式:`n`n是(Y) = 依日期排序`n否(N) = 依檢查敘述排序
        IfMsgBox Yes
        {
            SortByDate(WinTitle)
            MsgBox, 64, 完成, 已依日期排序
        }
        IfMsgBox No  
        {
            SortByExamType(WinTitle)
            MsgBox, 64, 完成, 已依檢查敘述排序
        }
    } else {
        MsgBox, 找不到檢查列表窗口
    }
return


; 依日期排序的函數（點擊欄位標題）
SortByDate(WinTitle) {
    ; 點擊日期欄位的標題來排序
    ; 根據你的截圖，日期欄位大約在 x=200-300 的位置
    ControlClick, x250 y30, %WinTitle%,, Left, 1
    Sleep, 300
    
    ; 再點一次確保是降序排列（最新的在上面）
    ControlClick, x500 y30, %WinTitle%,, Left, 1
    Sleep, 300
}

; 依檢查敘述排序的函數
SortByExamType(WinTitle) {
    ; 點擊檢查敘述欄位的標題來排序
    ; 根據截圖，檢查敘述欄位大約在最右邊
    ControlClick, x800 y30, %WinTitle%,, Left, 1
    Sleep, 300
}


; 點擊指定行號的函數
ClickRow(WinTitle, RowNumber) {
    ; 方法1: 使用 Control Choose
    ;Control, Choose, %RowNumber%, SysListView321, %WinTitle%
    ;Sleep, 100
    
    ; 方法2: 座標點擊（估計每行高度20像素） 雙擊開啟
    ClickY := 50 + (RowNumber - 1) * 28
    ClickX := 400  ; 檢查敘述欄位位置
    
    ControlClick, x%ClickX% y%ClickY%, %WinTitle%,, Left, 2
    Sleep, 100
    
}
; ============================================================================
; 座標收集工具 - 用於設定不同工作地點的滑鼠位置
; 使用方法：按 Win+Shift+C 啟動座標收集精靈
; ============================================================================

; Win+Shift+C 啟動座標收集精靈
#+c::
    StartCoordinateWizard()
return

; 主要的座標收集精靈函數
StartCoordinateWizard() {
    ; 先詢問工作地點
    Gui, LocSelect:New, +AlwaysOnTop, 選擇工作地點
    Gui, LocSelect:Font, s12
    
    Gui, LocSelect:Add, Text, x10 y10, 請選擇您的工作地點：
    Gui, LocSelect:Add, Radio, x10 y40 w200 vLoc1, 1: R辦公室(Win11)
    Gui, LocSelect:Add, Radio, x10 y70 w200 vLoc2 Checked, 2: 佳里座位
    Gui, LocSelect:Add, Radio, x10 y100 w200 vLoc3, 3: 第三VS辦公室(佳里)
    Gui, LocSelect:Add, Radio, x10 y130 w200 vLoc4, 4: 第三VS辦公室(柳營)
    Gui, LocSelect:Add, Radio, x10 y160 w200 vLoc5, 5: 遠端從家
    Gui, LocSelect:Add, Radio, x10 y190 w200 vLoc6, 6: R小房間(Win7)
    Gui, LocSelect:Add, Radio, x10 y220 w200 vLoc7, 7: 12F乳醫(Win7)
    Gui, LocSelect:Add, Radio, x10 y250 w200 vLoc8, 8: 永康3樓(國勳)
    Gui, LocSelect:Add, Radio, x10 y280 w200 vLoc9, 9: 新增位置
    
    Gui, LocSelect:Add, Button, x10 y320 w100 h30 gStartCollection, 開始收集
    Gui, LocSelect:Add, Button, x120 y320 w100 h30 gLocSelectCancel, 取消
    
    Gui, LocSelect:Show, w240 h370
}
return

StartCollection:
    Gui, LocSelect:Submit
    
    ; 判斷選擇的位置
    Loop, 9 {
        if (Loc%A_Index% = 1) {
            CurrentLocation := A_Index
            break
        }
    }
    
    ; 初始化收集的座標
    CollectedCoords := {Location: CurrentLocation
        , DICOMLU: {x: 0, y: 0}
        , DICOMRU: {x: 0, y: 0}
        , DICOMButton: {x: 0, y: 0}
        , NextExamBase: {x: 0, y: 0}
        , NextExamButton: {x: 0, y: 0}}
    
    ; 開始收集座標流程
    CollectDICOMLU()
return

; 收集 DICOM 左螢幕位置
CollectDICOMLU() {
    MsgBox, 0, 收集 DICOM 左螢幕座標, 
    (
請將滑鼠移到 DICOM 左螢幕的位置
(通常是左側影像顯示區域的中心)

移到位置後按「確定」
    ), 10
    
    MouseGetPos, x, y
    CollectedCoords.DICOMLU.x := x
    CollectedCoords.DICOMLU.y := y
    
    TrayTip, 座標已記錄, DICOM左螢幕: X=%x% Y=%y%, 3
    Sleep, 1000
    
    ; 繼續下一個
    CollectDICOMRU()
}

; 收集 DICOM 右螢幕位置
CollectDICOMRU() {
    MsgBox, 0, 收集 DICOM 右螢幕座標, 
    (
請將滑鼠移到 DICOM 右螢幕的位置
(通常是右側影像顯示區域的中心)

移到位置後按「確定」
    ), 10
    
    MouseGetPos, x, y
    CollectedCoords.DICOMRU.x := x
    CollectedCoords.DICOMRU.y := y
    
    TrayTip, 座標已記錄, DICOM右螢幕: X=%x% Y=%y%, 3
    Sleep, 1000
    
    ; 繼續下一個
    CollectDICOMButton()
}

; 收集 DICOM 按鈕位置
CollectDICOMButton() {
    MsgBox, 0, 收集 DICOM 按鈕座標, 
    (
請將滑鼠移到 DICOM 檔頭訊息按鈕的位置
(用於開啟 DICOM 資訊的按鈕)

移到位置後按「確定」
    ), 10
    
    MouseGetPos, x, y
    CollectedCoords.DICOMButton.x := x
    CollectedCoords.DICOMButton.y := y
    
    TrayTip, 座標已記錄, DICOM按鈕: X=%x% Y=%y%, 3
    Sleep, 1000
    
    ; 繼續下一個
    CollectNextExamCoords()
}

; 收集下一個檢查的座標（相對座標）
CollectNextExamCoords() {
    ; 先確認HIS視窗存在
    if !WinExist("ahk_exe chk060.exe") {
        MsgBox, 48, 錯誤, 請先開啟 HIS 系統 (chk060.exe)
        return
    }
    
    ; 啟動HIS視窗
    WinActivate, ahk_exe chk060.exe
    WinWaitActive, ahk_exe chk060.exe
    
    ; 步驟1：取得視窗基準點
    MsgBox, 0, 收集視窗基準點, 
    (
請將滑鼠移到 HIS 視窗的左上角
(視窗標題列的最左邊)

這將作為相對座標的基準點(0,0)

移到位置後按「確定」
    ), 10
    
    MouseGetPos, baseX, baseY
    CollectedCoords.NextExamBase.x := baseX
    CollectedCoords.NextExamBase.y := baseY
    
    TrayTip, 座標已記錄, 基準點: X=%baseX% Y=%baseY%, 3
    Sleep, 1000
    
    ; 步驟2：取得按鈕位置
    MsgBox, 0, 收集下一個檢查按鈕座標, 
    (
現在請將滑鼠移到「下一個檢查」按鈕的位置
(通常在 HIS 視窗的上方工具列)

移到位置後按「確定」
    ), 10
    
    MouseGetPos, btnX, btnY
    
    ; 計算相對座標
    relX := btnX - baseX
    relY := btnY - baseY
    
    CollectedCoords.NextExamButton.x := relX
    CollectedCoords.NextExamButton.y := relY
    
    TrayTip, 座標已記錄, 下一個檢查按鈕 (相對): X=%relX% Y=%relY%, 3
    Sleep, 1000
    
    ; 顯示結果
    ShowCollectedResults()
}

; 顯示收集的結果
ShowCollectedResults() {
    locationNames := {1: "R辦公室(Win11)"
        , 2: "佳里座位"
        , 3: "第三VS辦公室(佳里)"
        , 4: "第三VS辦公室(柳營)"
        , 5: "遠端從家"
        , 6: "R小房間(Win7)"
        , 7: "12F乳醫(Win7)"
        , 8: "永康3樓(國勳)"
        , 9: "新增位置"}
    
    locName := locationNames[CurrentLocation]
    
    ; 建立結果顯示GUI
    Gui, Results:New, +AlwaysOnTop, 座標收集結果
    Gui, Results:Font, s10, Consolas
    
    Gui, Results:Add, Text, x10 y10, % "工作地點: " . locName
    Gui, Results:Add, Text, x10 y30, % "====================================="
    
    resultText := "收集的座標數據：`r`n`r`n"
    resultText .= "PosDICOMLU:`r`n"
    resultText .= "    MouseMove " . CollectedCoords.DICOMLU.x . ", " . CollectedCoords.DICOMLU.y . "`r`n`r`n"
    resultText .= "PosDICOMRU:`r`n"
    resultText .= "    MouseMove " . CollectedCoords.DICOMRU.x . ", " . CollectedCoords.DICOMRU.y . "`r`n`r`n"
    resultText .= "PosDICOMButton:`r`n"
    resultText .= "    MouseMove " . CollectedCoords.DICOMButton.x . ", " . CollectedCoords.DICOMButton.y . "`r`n`r`n"
    resultText .= "下一個檢查按鈕 (相對座標):`r`n"
    resultText .= "    MouseMove " . CollectedCoords.NextExamButton.x . ", " . CollectedCoords.NextExamButton.y . "`r`n"
    
    Gui, Results:Add, Edit, x10 y60 w500 h250 vResultEdit ReadOnly, %resultText%
    
    ; 產生程式碼
    codeText := GenerateCode()
    Gui, Results:Add, Text, x10 y320, 產生的程式碼：
    Gui, Results:Add, Edit, x10 y340 w500 h200 vCodeEdit ReadOnly, %codeText%
    
    Gui, Results:Add, Button, x10 y550 w100 h30 gCopyResults, 複製程式碼
    Gui, Results:Add, Button, x120 y550 w100 h30 gSaveResults, 儲存到檔案
    Gui, Results:Add, Button, x230 y550 w100 h30 gTestCoords, 測試座標
    Gui, Results:Add, Button, x340 y550 w100 h30 gResultsClose, 關閉
    
    Gui, Results:Show, w520 h590
}

; 產生程式碼片段
GenerateCode() {
    loc := CurrentLocation
    LU_X := CollectedCoords.DICOMLU.x
    LU_Y := CollectedCoords.DICOMLU.y
    RU_X := CollectedCoords.DICOMRU.x
    RU_Y := CollectedCoords.DICOMRU.y
    Btn_X := CollectedCoords.DICOMButton.x
    Btn_Y := CollectedCoords.DICOMButton.y
    Next_X := CollectedCoords.NextExamButton.x
    Next_Y := CollectedCoords.NextExamButton.y
    
    code = 
(
`; 位置 %loc% 的座標設定
else if(varWhere=%loc%) {
    `; PosDICOMLU
    MouseMove %LU_X%, %LU_Y%
    `; PosDICOMRU
    `; MouseMove %RU_X%, %RU_Y%
    `; PosDICOMButton
    `; MouseMove %Btn_X%, %Btn_Y%
    `; 下一個檢查 (F12)
    `; MouseMove %Next_X%, %Next_Y%
}
)
    
    return code
}

; 複製結果到剪貼簿
CopyResults:
    Gui, Results:Submit, NoHide
    Clipboard := CodeEdit
    MsgBox, 64, 完成, 程式碼已複製到剪貼簿！
return

; 儲存結果到檔案
SaveResults:
    FormatTime, timeStr, , yyyyMMdd_HHmmss
    fileName := "座標收集_位置" . CurrentLocation . "_" . timeStr . ".txt"
    
    FileSelectFile, savePath, S16, %fileName%, 儲存座標資料, Text Files (*.txt)
    if (savePath = "")
        return
    
    Gui, Results:Submit, NoHide
    
    FileDelete, %savePath%
    FileAppend, %ResultEdit%`r`n`r`n, %savePath%
    FileAppend, %CodeEdit%, %savePath%
    
    MsgBox, 64, 完成, 座標資料已儲存到：`n%savePath%
return

; 測試收集的座標
TestCoords:
    MsgBox, 4, 測試座標, 即將測試收集的座標。`n滑鼠會依序移動到各個位置。`n`n要繼續嗎？
    IfMsgBox No
        return
    
    ; 測試各個座標
    TrayTip, 測試中, 移動到 DICOM 左螢幕..., 2
    MouseMove, % CollectedCoords.DICOMLU.x, % CollectedCoords.DICOMLU.y
    Sleep, 1500
    
    TrayTip, 測試中, 移動到 DICOM 右螢幕..., 2
    MouseMove, % CollectedCoords.DICOMRU.x, % CollectedCoords.DICOMRU.y
    Sleep, 1500
    
    TrayTip, 測試中, 移動到 DICOM 按鈕..., 2
    MouseMove, % CollectedCoords.DICOMButton.x, % CollectedCoords.DICOMButton.y
    Sleep, 1500
    
    TrayTip, 測試完成, 座標測試完成！, 3
return

; 關閉視窗
LocSelectCancel:
LocSelectGuiClose:
    Gui, LocSelect:Destroy
return

ResultsClose:
ResultsGuiClose:
    Gui, Results:Destroy
return

; 快速測試現在滑鼠位置 (Win+Shift+M)
#+m::
    CoordMode, Mouse, Screen
    MouseGetPos, xScreen, yScreen
    
    CoordMode, Mouse, Window
    MouseGetPos, xWindow, yWindow
    
    CoordMode, Mouse, Client
    MouseGetPos, xClient, yClient
    
    MsgBox, 0, 滑鼠座標資訊,
    (
螢幕座標 (Screen): X=%xScreen%, Y=%yScreen%
視窗座標 (Window): X=%xWindow%, Y=%yWindow%
客戶區座標 (Client): X=%xClient%, Y=%yClient%

按 Win+Shift+C 啟動完整座標收集精靈
    )
return

; ============================================================================
; XButton1 多功能選單（增強版）
; ============================================================================

XButton1::
    ; 安全地建立/重建選單
    Menu, XB1Menu, UseErrorLevel  ; 啟用錯誤處理
    Menu, XB1Menu, DeleteAll      ; 清空選單（如果存在）
    
    ; 建立選單項目
	; === 第一區：影像相關 ===
    Menu, XB1Menu, Add, 右側影像編號 (&R), XB1_RightDICOM
    Menu, XB1Menu, Add, 左側影像編號 (&L), XB1_LeftDICOM
    Menu, XB1Menu, Add  ; 分隔線
	; === 第二區：日期與報告 ===
    Menu, XB1Menu, Add, 複製檢查日期 (&D), XB1_CopyDate
    Menu, XB1Menu, Add, 日期 + 舊報告 (&O), XB1_CopyOldReport
    Menu, XB1Menu, Add  ; 分隔線
	; === 第三區：查詢功能 ===
    Menu, XB1Menu, Add, 開啟舊報告網頁 (&W), XB1_OpenWeb
    Menu, XB1Menu, Add, 病歷彙總 (&S), XB1_Summary
    Menu, XB1Menu, Add  ; 分隔線
    ; === 第五區：系統功能 ===
	Menu, XB1Menu, Add, 腹部US AI (&A), AI_FindOpen
	Menu, XB1Menu, Add, 乳房US AI (&B), ShowUSAIGUI
    Menu, XB1Menu, Add, 設定管理器 (&G), XB1_OpenConfig
    Menu, XB1Menu, Add, 重新載入腳本 (&E), XB1_Reload
    
    ; 顯示選單
    Menu, XB1Menu, Show
return


; ============================================================================
; 選單功能處理
; ============================================================================

; 功能 1：右側影像編號
XB1_RightDICOM:
    Gosub, CallDICOMWin
    
    ; 處理 DICOM 資料並輸出編號
    text := clipboard
    tmp2 := GetDICOMLineData("Series Number", text)
    tmp3 := GetDICOMLineData("Instance Number", text)
    
    desc := "(Srs/Img:" . tmp2 . "/" . tmp3 . ")"
    CopyCXRtoHISWithParam(0)
    
    TrayTip, XButton1, 右側影像編號已輸出, 2, 1
return

; 功能 2：左側影像編號
XB1_LeftDICOM:
    Gosub, CallDICOMWinL
    
    ; 處理 DICOM 資料並輸出編號
    text := clipboard
    tmp2 := GetDICOMLineData("Series Number", text)
    tmp3 := GetDICOMLineData("Instance Number", text)
    
    desc := "(Srs/Img:" . tmp2 . "/" . tmp3 . ")"
    CopyCXRtoHISWithParam(0)
    
    TrayTip, XButton1, 左側影像編號已輸出, 2, 1
return

; 功能 3：複製檢查日期
XB1_CopyDate:
    Gosub, calldate
    TrayTip, XButton1, 檢查日期已輸出, 2, 1
return

; 功能 4：日期 + 舊報告
XB1_CopyOldReport:
    Gosub, CopyOld
    TrayTip, XButton1, 日期和舊報告已輸出, 2, 1
return

; 功能 5：開啟舊報告網頁
XB1_OpenWeb:
    OpenReportComparison(GetAccessionNumber())
    TrayTip, XButton1, 已開啟舊報告網頁, 2, 1
return

; 功能 6：病歷彙總
XB1_Summary:
    ControlGetText, ExamNo, ThunderRT6TextBox9, ahk_exe chk060.exe
    ChartNo := SubStr(ExamNo, 1, 8)
    url := "http://jlmrs.chimei.org.tw/EPR/sub_entry.asp?ihosp=14&ipatient=" . ChartNo . "&imode=&ftype=&iclass=0&from=4130&multiscreen="
    Run, msedge.exe %url%
    TrayTip, XButton1, 已開啟病歷彙總, 2, 1
return

; 新增功能 7：開啟設定管理器
XB1_OpenConfig:
    CreateConfigManager()
return

; 新增功能 8：重新載入腳本
XB1_Reload:
    Reload
return

