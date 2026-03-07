#NoEnv
#SingleInstance Force
SendMode Input
SetWorkingDir %A_ScriptDir%
SetTitleMatchMode, 2
DetectHiddenText, On
DetectHiddenWindows, On

global TEST3_LOG := A_ScriptDir . "\test3_name_debug.txt"

global TEST3_PREFERRED_CONTROLS := ["ComboBox49", "ComboBox2", "RichEdit20W2", "AfxWnd140u22"]

global TEST3_EXCLUDE_WORDS := ["醫師", "主治", "住院醫師", "總醫師", "DR", "DOCTOR", "REPORT", "放射", "RADIATION"]

^!h::
    chartNo := OpenHISSummaryForCurrentCase()
    if (chartNo = "") {
        MsgBox, 48, test3, Unable to open HIS summary from current case.`nNo chart number found from HIS or DICOM.
        return
    }
    MsgBox, 64, test3, HIS summary opened for chart no: %chartNo%
return

^!p::
    result := InspectActiveWindowForChineseName()
    ShowInspectResult(result)
return

^!l::
    result := InspectActiveWindowForChineseName()
    SaveInspectLog(result)
    MsgBox, 64, test3, Window inspection log saved:`n%TEST3_LOG%
return

^!c::
    result := InspectActiveWindowForChineseName()
    if (result.bestName = "") {
        MsgBox, 48, test3, No Chinese patient name candidate found.
        return
    }
    bestName := result.bestName
    Clipboard := bestName
    MsgBox, 64, test3, Copied candidate name:`n%bestName%
return

OpenHISSummaryForCurrentCase() {
    ActivateHISLight()
    ControlGetText, examNo, ThunderRT6TextBox9, ahk_exe chk060.exe
    chartNo := ExtractChartNo(examNo)
    if (chartNo = "") {
        dicomData := GetDICOMData()
        chartNo := GetChartNoFromDICOM(dicomData)
    }
    if (chartNo = "")
        return ""

    ControlSetText, ThunderRT6TextBox9, %chartNo%, ahk_exe chk060.exe
    Sleep, 100
    ControlClick, ThunderRT6CommandButton31, ahk_exe chk060.exe
    return chartNo
}

ExtractChartNo(text) {
    text := Trim(text)
    if (text = "")
        return ""
    if RegExMatch(text, "\d{8}", m)
        return m
    return ""
}

GetChartNoFromDICOM(text) {
    patientId := GetDICOMLineData("Patient ID", text)
    chartNo := ExtractChartNo(patientId)
    if (chartNo != "")
        return chartNo

    patientId := GetDICOMLineData("Patient's ID", text)
    chartNo := ExtractChartNo(patientId)
    if (chartNo != "")
        return chartNo

    accessionNum := GetAccessionNumber(text)
    if (StrLen(accessionNum) >= 8)
        return SubStr(accessionNum, 1, 8)

    return ""
}

ActivateHISLight() {
    WinActivate, ahk_exe chk060.exe
    WinWaitActive, ahk_exe chk060.exe,, 1
    ControlFocus, ThunderRT6TextBox14, ahk_exe chk060.exe
}

GetDICOMData() {
    gosub CallDICOMWin
    return clipboard
}

GetDICOMLineData(attrib := "", text := "") {
    tmp := StrSplit(text, "`n")
    res := ""
    for index, textline in tmp {
        if (InStr(textline, attrib)) {
            res := tmp[index + 1]
            break
        }
    }
    if (res != "") {
        tmp2 := StrSplit(res, "|")
        return tmp2[2]
    }
    return ""
}

GetAccessionNumber(text := "") {
    clipboardBackup := Clipboard
    if (text = "")
        text := GetDICOMData()
    accessionNum := GetDICOMLineData("accession number", text)
    accessionNum := RegExReplace(accessionNum, "\D")
    Clipboard := clipboardBackup
    return accessionNum
}

InspectActiveWindowForChineseName() {
    result := {}
    result.bestName := ""
    result.bestSource := ""
    result.summary := ""
    result.windowTitle := ""
    result.windowClass := ""
    result.controls := []
    result.matches := []

    WinGetTitle, winTitle, A
    WinGetClass, winClass, A
    result.windowTitle := winTitle
    result.windowClass := winClass

    WinGet, controlList, ControlList, A
    prioritized := []
    others := []
    Loop, Parse, controlList, `n
    {
        ctrl := A_LoopField
        if (ctrl = "")
            continue
        if IsPreferredControl(ctrl)
            prioritized.Push(ctrl)
        else
            others.Push(ctrl)
    }

    for _, ctrl in prioritized
        InspectOneControl(ctrl, result)

    if (!result.matches.MaxIndex()) {
        WinGetText, winText, A
        if (winText != "")
            CollectChineseCandidates("WINDOW_TEXT", winText, result)
    }

    if (!result.matches.MaxIndex()) {
        for _, ctrl in others
            InspectOneControl(ctrl, result)
    }

    if (result.matches.MaxIndex()) {
        best := result.matches[1]
        result.bestName := best.name
        result.bestSource := best.source
    }

    result.summary := BuildSummary(result)
    return result
}

InspectOneControl(ctrl, ByRef result) {
    ControlGetText, ctrlText, %ctrl%, A
    if (ctrlText = "")
        return

    item := {}
    item.control := ctrl
    item.text := ctrlText
    result.controls.Push(item)
    CollectChineseCandidates(ctrl, ctrlText, result)
}

IsPreferredControl(ctrl) {
    global TEST3_PREFERRED_CONTROLS
    for _, name in TEST3_PREFERRED_CONTROLS {
        if (ctrl = name)
            return true
    }
    return false
}

CollectChineseCandidates(source, text, ByRef result) {
    normalized := NormalizeWhitespace(text)
    lines := StrSplit(normalized, "`n")
    for _, line in lines {
        line := Trim(line)
        if (line = "")
            continue
        candidate := ExtractChineseName(line)
        if (candidate = "")
            continue
        if IsExcludedCandidate(candidate, line)
            continue

        item := {}
        item.source := source
        item.line := line
        item.name := candidate
        result.matches.Push(item)
    }
}

ExtractChineseName(text) {
    cleaned := Trim(text)
    cleaned := RegExReplace(cleaned, "[`r`n`t]", " ")
    cleaned := RegExReplace(cleaned, "\s+", " ")

    if RegExMatch(cleaned, "(姓名|病人|患者|Name)\s*[:：]?\s*([一-龥]{2,6})", m)
        return m2

    if RegExMatch(cleaned, "([一-龥]{2,6})", m2)
        return m21

    return ""
}

IsExcludedCandidate(name, line) {
    global TEST3_EXCLUDE_WORDS
    upperLine := line
    StringUpper, upperLine, upperLine
    for _, word in TEST3_EXCLUDE_WORDS {
        if (InStr(upperLine, word))
            return true
    }
    if (name = "醫師" || name = "主治醫師")
        return true
    return false
}

NormalizeWhitespace(text) {
    text := StrReplace(text, "`r`n", "`n")
    text := StrReplace(text, "`r", "`n")
    return text
}

BuildSummary(result) {
    out := ""
    out .= "Window Title: " . result.windowTitle . "`r`n"
    out .= "Window Class: " . result.windowClass . "`r`n"
    out .= "Best Name: " . result.bestName . "`r`n"
    out .= "Best Source: " . result.bestSource . "`r`n"
    out .= "`r`nMatches:`r`n"

    for _, item in result.matches
        out .= "- " . item.name . " | " . item.source . " | " . item.line . "`r`n"

    out .= "`r`nControls:`r`n"
    for _, ctrl in result.controls
        out .= "[" . ctrl.control . "] " . ctrl.text . "`r`n"

    return out
}

SaveInspectLog(result) {
    FileDelete, %TEST3_LOG%
    FileAppend, % result.summary, %TEST3_LOG%, UTF-8
}

ShowInspectResult(result) {
    msg := "Title: " . result.windowTitle . "`n"
    msg .= "Class: " . result.windowClass . "`n`n"
    if (result.bestName != "") {
        msg .= "Best candidate: " . result.bestName . "`n"
        msg .= "Source: " . result.bestSource . "`n`n"
    } else {
        msg .= "No Chinese name candidate found.`n`n"
    }
    msg .= "Raw log saved to:`n" . TEST3_LOG
    SaveInspectLog(result)
    MsgBox, 64, test3, %msg%
}

CallDICOMWin:
    clipboardBackup := Clipboard
    Clipboard :=
    MouseGetPos, tmpX, tmpY
    gosub PosDICOMLU
    Send {LButton}
    Sleep, 20
    Send g
    Sleep, 20
    Send 3
    WinWaitActive, DICOM 檔頭訊息,, 1
    ControlGetText, clipboard, Edit3, DICOM 檔頭訊息
    WinClose, DICOM 檔頭訊息
    DllCall("SetCursorPos", "int", tmpX, "int", tmpY)
return

PosDICOMLU:
    CoordMode, Mouse, Screen
    MouseMove, 71, 534, 0
return
