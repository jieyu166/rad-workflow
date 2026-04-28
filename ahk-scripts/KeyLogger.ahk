#SingleInstance force
#NoEnv
SetWorkingDir %A_ScriptDir%
SetBatchLines, -1

; ============================================================
; KeyLogger.ahk — Personal keystroke logger for hotkey optimization
; Toggle: Ctrl+F12 to pause/resume
; Log file: ahk-scripts/logs/keylog_YYYYMMDD.log
; Format: TSV (timestamp, key, window_title, window_class)
; Auto-rotates daily, auto-cleans logs older than 14 days
; Skips password fields for safety
; ============================================================

; --- Config ---
global LogDir := A_ScriptDir "\logs"
global LogFile := ""
global IsLogging := true
global LastLogDate := ""
global LogRetainDays := 14

; Create log directory
FileCreateDir, %LogDir%

; Initialize log file
UpdateLogFile()

; Clean old logs on startup
CleanOldLogs()

; --- Tray menu ---
Menu, Tray, Tip, KeyLogger (ON)
Menu, Tray, NoStandard
Menu, Tray, Add, Toggle Logging (Ctrl+F12), ToggleLogging
Menu, Tray, Add, Open Log Folder, OpenLogFolder
Menu, Tray, Add, Show Stats, ShowStats
Menu, Tray, Add,
Menu, Tray, Add, Exit, ExitLogger

; --- Register all printable keys + modifiers ---
; Letters
Loop, 26
{
    key := Chr(A_Index + 64)  ; A-Z
    Hotkey, ~%key%, LogKey
    Hotkey, ~+%key%, LogKey    ; Shift+letter
    Hotkey, ~^%key%, LogKey    ; Ctrl+letter
    Hotkey, ~!%key%, LogKey    ; Alt+letter
    Hotkey, ~^+%key%, LogKey   ; Ctrl+Shift+letter
}

; Numbers 0-9
Loop, 10
{
    key := A_Index - 1
    Hotkey, ~%key%, LogKey
    Hotkey, ~+%key%, LogKey
    Hotkey, ~^%key%, LogKey
}

; Function keys F1-F12
Loop, 12
{
    Hotkey, ~F%A_Index%, LogKey
    Hotkey, ~^F%A_Index%, LogKey
    Hotkey, ~+F%A_Index%, LogKey
    Hotkey, ~!F%A_Index%, LogKey
}

; Special keys
specialKeys := "Space,Enter,Tab,Backspace,Delete,Escape"
    . ",Up,Down,Left,Right"
    . ",Home,End,PgUp,PgDn"
    . ",Insert,PrintScreen"
    . ",CapsLock,NumLock,ScrollLock"
    . ",-,=,[,],\,;,',``,.,/,,"

Loop, Parse, specialKeys, `,
{
    if (A_LoopField = "")
        continue
    try {
        Hotkey, ~%A_LoopField%, LogKey
    }
}

; Numpad
Loop, 10
{
    key := "Numpad" (A_Index - 1)
    Hotkey, ~%key%, LogKey
}
numpadExtra := "NumpadDot,NumpadDiv,NumpadMult,NumpadAdd,NumpadSub,NumpadEnter"
Loop, Parse, numpadExtra, `,
{
    try {
        Hotkey, ~%A_LoopField%, LogKey
    }
}

return

; ============================================================
; Core logging handler
; ============================================================
LogKey:
    if (!IsLogging)
        return

    ; Skip password fields
    ControlGetFocus, focusedCtrl, A
    if (focusedCtrl != "") {
        ; Check if it's a password input (style has ES_PASSWORD = 0x20)
        ControlGet, style, Style,, %focusedCtrl%, A
        if (style & 0x20)
            return
    }

    ; Rotate log file if date changed
    UpdateLogFile()

    ; Get key name from hotkey
    keyName := RegExReplace(A_ThisHotkey, "^~", "")

    ; Get active window info
    WinGetTitle, winTitle, A
    WinGetClass, winClass, A

    ; Truncate long titles
    if (StrLen(winTitle) > 80)
        winTitle := SubStr(winTitle, 1, 80) "..."

    ; Format timestamp
    FormatTime, ts,, yyyy-MM-dd HH:mm:ss

    ; Write log line (TSV)
    line := ts "`t" keyName "`t" winTitle "`t" winClass "`n"
    FileAppend, %line%, %LogFile%, UTF-8

return

; ============================================================
; Helper functions
; ============================================================

UpdateLogFile() {
    FormatTime, today,, yyyyMMdd
    if (today != LastLogDate) {
        LastLogDate := today
        LogFile := LogDir "\keylog_" today ".log"
        ; Write header if new file
        if (!FileExist(LogFile)) {
            header := "timestamp`tkey`twindow_title`twindow_class`n"
            FileAppend, %header%, %LogFile%, UTF-8
        }
    }
}

CleanOldLogs() {
    cutoff := A_Now
    EnvAdd, cutoff, -%LogRetainDays%, Days
    Loop, Files, %LogDir%\keylog_*.log
    {
        ; Extract date from filename: keylog_YYYYMMDD.log
        RegExMatch(A_LoopFileName, "keylog_(\d{8})\.log", m)
        if (m1 != "") {
            fileDate := m1 "000000"
            if (fileDate < cutoff) {
                FileDelete, %A_LoopFileFullPath%
            }
        }
    }
}

; ============================================================
; Toggle hotkey
; ============================================================
^F12::
ToggleLogging:
    IsLogging := !IsLogging
    state := IsLogging ? "ON" : "OFF"
    Menu, Tray, Tip, KeyLogger (%state%)
    TrayTip, KeyLogger, Logging %state%, 1
return

; ============================================================
; Menu actions
; ============================================================
OpenLogFolder:
    Run, explorer.exe "%LogDir%"
return

ShowStats:
    ; Quick stats from today's log
    if (!FileExist(LogFile)) {
        MsgBox, No log for today yet.
        return
    }

    totalKeys := 0
    topKeys := {}

    Loop, Read, %LogFile%
    {
        if (A_Index = 1)  ; skip header
            continue
        totalKeys++
        ; Parse key column (2nd field)
        fields := StrSplit(A_LoopReadLine, "`t")
        k := fields[2]
        if (topKeys.HasKey(k))
            topKeys[k]++
        else
            topKeys[k] := 1
    }

    ; Sort by frequency (collect into array)
    sorted := []
    for k, v in topKeys
        sorted.Push({key: k, count: v})

    ; Bubble sort top 15
    Loop % sorted.Length() - 1
    {
        i := A_Index
        Loop % sorted.Length() - i
        {
            j := A_Index
            if (sorted[j].count < sorted[j+1].count) {
                tmp := sorted[j]
                sorted[j] := sorted[j+1]
                sorted[j+1] := tmp
            }
        }
    }

    ; Build display
    msg := "Today's keystroke stats:`n"
    msg .= "Total: " totalKeys " keys`n`n"
    msg .= "Top 15 keys:`n"
    msg .= "----------------------------`n"

    limit := sorted.Length() < 15 ? sorted.Length() : 15
    Loop, %limit%
    {
        entry := sorted[A_Index]
        pct := Round(entry.count / totalKeys * 100, 1)
        msg .= entry.key "`t" entry.count "`t(" pct "%)`n"
    }

    MsgBox, 0, KeyLogger Stats, %msg%
return

ExitLogger:
    ExitApp
return
