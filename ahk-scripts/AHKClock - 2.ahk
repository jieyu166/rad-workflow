#SingleInstance force
#include d8888basic.ahk

;
; Global
;

TotalFilms := 0
TotalTimepassed := 0 
TotalIdle := 0
TotalFilmsToolong := 0 ; 幾片超時
ExceedTime := 150 ; 超過幾秒不行
ExceedIdleTime := 600 ; idle超過幾秒不行

TimerOn := 1

LastStudyID := 0

NowText := ""

LastTick := A_TickCount

;
; Creating GUI
;

IfWinExist ahk_id %MyGuiHwnd%
{
    gosub move_GUI
    return
}

Gui +HwndMyGuiHwnd
initSecs := 0 ; number of seconds 
idleSecs := 0 ; number of idle seconds
HelpMsg := "Ready to engage" ; Messages

Gui, +AlwaysOnTop +Resize

; Row 1
Gui, font, s09 normal, Verdana
Gui, Add, Progress, x53 y8 w170 h43 vExamColorIndicator, 100
Gui, Add, Progress, x285 y8 w170 h43 vColorIndicator, 100
Gui, Add, Text, x10 y10 w180 h40 BackgroundTrans, Active`rTime
Gui, Add, Text, x245 y10 w180 h40 BackgroundTrans, Idle`rTime

; Row 2
Gui, font, s24 bold, Verdana
Gui, Add, Text, x58 y10 w170 h35 BackgroundTrans vActiveTime, 00:00:00
Gui, Add, Text, x290 y10 w170 h35 BackgroundTrans vIdleTime, 00:00:00

; Row 3
Gui, font, s12 normal, Verdana
Gui, Add, Button, x10 y57 w95 h30 vButton gSwitchTimer, Start/Stop
Gui, Add, Button, x115 yp w90 h30 vButton2 gResetCal, Reset
Gui, Add, Button, x215 yp w90 h30 vButton3 gChangeToIdle, Idle
Gui, Add, Button, x315 yp w100 h30 vButton4 gChangeExceedTime, Limit: %ExceedTime%
Gui, Add, Slider, x10 y90 w390 h15 vTransparencySlider gUpdateTransparency Range0-255 TickInterval10, 255


Gui, Show, w460 h105 x1220 y0, %HelpMsg%

SetTimer, TimerCountDown, 1000
SetTimer, DetectXRayChange, 1000
WinSet, Transparent, 255, ahk_id %MyGuiHwnd%

return

DetectXRayChange:	
    ; Detect text input
    ControlGetText, nowreport, ThunderRT6TextBox14, ahk_exe chk060.exe
    if (NowText <> nowreport)
    {
        TimerOn := 1
        NowText := nowreport
    }
    
    ; Detect change in patient ID
    ControlGetText, text, ThunderRT6TextBox12, ahk_exe chk060.exe
    FoundPos := RegExMatch(text, "[a-zA-Z0-9][0-9]{14}", StudyID)
    if (FoundPos = 0)
    {
        return
    }

    ; Special fix for barcode machine
    ControlGetText, nowPatientId, ThunderRT6TextBox9, ahk_exe chk060.exe
    if (SubStr(nowPatientId, 1, 8) != SubStr(StudyID, 1, 8))
    {
        return
    }
    
    if (LastStudyID <> StudyID && initSecs > 2)
    {
        TimerOn := 1
    }

    if (LastStudyID <> StudyID && initSecs > 5)
    {
        TotalTimepassed += initSecs  ; Update TotalTimepassed here
        OldTime%LastStudyID% := initSecs
        
        if (OldTime%StudyID%)
        {
            initSecs := OldTime%StudyID%
        }
        else
        {
            TotalFilms++
            if (initSecs > ExceedTime) {
                TotalFilmsToolong++
            }
            initSecs := 0
        }
    
        LastStudyID := StudyID
    }
    return

ChangeToIdle:
    idleSecs += initSecs
    initSecs := 0
    GuiControl,, ActiveTime, 00:00:00
    GuiControl,, IdleTime, % Frmt(idleSecs)
    return

TimerCountDown:
    elapsedTime := (A_TickCount - LastTick) / 1000
    if (TimerOn == 1)
    {
        initSecs += elapsedTime
    }
    else
    {
        idleSecs += elapsedTime
    }
    
    LastTick := A_TickCount

    if (initSecs > ExceedTime) {
        GuiControl, +c0xEEAA99, ExamColorIndicator  
    } else {
        GuiControl, +c0xEEEEEE, ExamColorIndicator  
    }
    if (idleSecs > ExceedIdleTime) {
        GuiControl, +c0xEEAA00, ColorIndicator  
    } else {
        GuiControl, +c0xEEEEEE, ColorIndicator  
    }    
    GuiControl,, ActiveTime, % Frmt(initSecs)
    GuiControl,, IdleTime, % Frmt(idleSecs)
    HelpMsg := GetMsg(initSecs)
    WinSetTitle, ahk_id %MyGuiHwnd%,, %HelpMsg%
    return

move_gui:
    i++
    if (i = 1)
        GUI, show, x0 y0
    else if (i = 2)
        GUI, show, % "x" A_ScreenWidth - 410 "y" 0
    else if (i = 3)
        GUI, show, % "x" A_ScreenWidth - 410 "y" A_ScreenHeight - 140
    else if (i = 4)
        GUI, show, % "x" 0 "y" A_ScreenHeight - 140
    else
    {
        GUI, show, center
        i := 0	; reset the counter
    }
    return

GuiClose:
    ExitApp
    return

SwitchTimer:
    TimerOn := !TimerOn
    return

ResetCal:
    TotalFilms := 0
    TotalTimepassed := 0
    TimerOn := 1
    initSecs := 0
    idleSecs := 0
    TotalFilmsToolong := 0
    GuiControl,, ActiveTime, 00:00:00
    GuiControl,, IdleTime, 00:00:00
    return

ChangeExceedTime:
    InputBox, NewExceedTime, "Change Time Limit", "New time limit (seconds)",, 400, 150, , , , , %ExceedTime%
    if (NewExceedTime != "")
    {
        ExceedTime := NewExceedTime
        GuiControl,, Button4, Limit: %ExceedTime%
    }
    return

UpdateTransparency:
    GuiControlGet, TransparencyValue,, TransparencySlider
    WinSet, Transparent, %TransparencyValue%, ahk_id %MyGuiHwnd%
return
	
GetMsg(val)
{
    global TotalFilms, TotalTimepassed, TimerOn, TotalFilmsToolong, TotalIdle, ExceedTime
    
    rst := TimerOn ? "Running | " : "Stopped | "
    
    if (TotalFilms > 0)
    {
        Xrate := Round(TotalFilms * 3600 / (TotalTimepassed - TotalIdle), 1)
        rst .= "Rate: " . Xrate . "/h | "
        rst .= "Total: " . TotalFilms . " | "
        rst .= "Exceed: " . TotalFilmsToolong . " | "
    }
    
    ;rst .= "Limit: " . ExceedTime . "s"
    return rst
}

Frmt(secs) {
    secs := Floor(secs)
    time = 20000101
    time += %secs%, seconds
    FormatTime, mmss, %time%, HH:mm:ss
    return mmss
}