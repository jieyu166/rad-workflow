#SingleInstance force

; 設定共享檔案路徑（需與電腦1相同）
RemoteFile := A_ScriptDir . "\..\remote.txt"
; 或本機測試用：RemoteFile := A_ScriptDir . "\..\remote.txt"

; 設定滑鼠點擊座標
ClickX := 277
ClickY := 159

#a::
    ; 讀取檔案內容
    FileRead, StudyID, %RemoteFile%
    if (ErrorLevel || StudyID = "")
    {
        MsgBox, 48, 錯誤, 無法讀取 remote.txt 或檔案為空
        return
    }
    
    ; 移動滑鼠並點擊
    MouseMove, %ClickX%, %ClickY%
    Sleep, 50
    Click
    Sleep, 100
    
    ; 寫入剪貼簿並貼上
    Clipboard := StudyID
    Sleep, 50
    Send, ^v
	Send {Enter}
    
    ; 可選：顯示已貼上的內容
    ToolTip, 已貼上: %StudyID%
    SetTimer, RemoveToolTip, -1500
    return

RemoveToolTip:
    ToolTip
    return
	
	
#s::
    MouseMove, -500, 1000
	Sleep, 50
	Click
	ToolTip
