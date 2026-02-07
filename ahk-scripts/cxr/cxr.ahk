#NoEnv
SendMode Input
SetWorkingDir %A_ScriptDir%

::cxr3;::
; 初始化變數
selectedItems := {}  ; 儲存已選擇的項目
currentFile := ""    ; 當前選擇的檔案
 
; 記錄目前視窗
WinGet, ActiveId, ID, A

; 搜尋同目錄下的所有txt檔案
FileList := ""
Loop, *.txt
{
    FileList .= A_LoopFileName . "|"
}
StringTrimRight, FileList, FileList, 1  ; 移除最後的 |
 
; 如果沒有找到txt檔案，使用預設
if (FileList = "")
{
    MsgBox, 沒有找到txt檔案！
    return
}
 
; 取得第一個檔案作為預設
StringSplit, FileArray, FileList, |
currentFile := FileArray1
 
; 初始建立GUI
Gosub, CXR3CreateGUI
 
Return
 
; 建立新的GUI
CXR3CreateGUI:
; 先銷毀舊的GUI（如果存在）
Gui, CXR3:Destroy
 
; 重置變數
selectedItems := {}
desc := ""
opt_multi := []
abbr_str := []
buttonTexts := {}  ; 儲存按鈕的完整文字
hotkeys := ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
 
; GUI基本設置
Gui, CXR3:Font, s12
 
; 上方控制區
Gui, CXR3:Add, Text, x10 y10 w80 h30, 選擇模板:
Gui, CXR3:Add, DropDownList, x90 y10 w150 h90 vSelectedFile gCXR3FileChanged, %FileList%
GuiControl, CXR3:, SelectedFile, %currentFile%
Gui, CXR3:Add, Button, x250 y10 w80 h30 gCXR3LockFile, 鎖定(&L)
Gui, CXR3:Add, Button, x340 y10 w100 h30 gCXR3out, Copy代碼(&S)
Gui, CXR3:Add, Button, x450 y10 w80 h30 gCXR3ClearAll, 清空(&C)
 
; 計算頁籤數量
tabcount_total := 1
tab_str := "Tab 1"

Loop, read, %currentFile%
{
    if (InStr(A_LoopReadLine, "--Page--", false)){
        tabcount_total := tabcount_total + 1
        tab_str .= "|Tab "
        tab_str .= tabcount_total
    }
}

; 創建Tab控件 (左側)
Gui Add, Tab3, x10 y50 w360 h600 vtaba, % tab_str

tabcount := 1
Gui, CXR3:Tab, %tabcount%
Gui, CXR3:Add, Text, x1 y90, " " ; 定位用
yPos := 90
buttonIndex := 0
pageButtonIndex := 1  ; 修正：從1開始，不是0
 
; 讀取檔案並生成按鈕
Loop, read, %currentFile%
{
    if (InStr(A_LoopReadLine, "--Page--", false)){
        ; 換頁
        tabcount := tabcount + 1
        Gui, CXR3:Tab, %tabcount%
        opt_multi[tabcount] := 0
        Gui, CXR3:Add, Text, x1 y90, " " ; 定位用
        yPos := 90
        buttonIndex := 0
        pageButtonIndex := 1  ; 重置每頁的按鈕索引，從1開始
    }
    else if(InStr(A_LoopReadLine, "TEXT::", false)){
        ; 顯示文字標籤
        yPos += 35
        Gui, Add, Text, x20 y%yPos% w340 h20, % Substr(A_LoopReadLine, 7)
    }
    else if(InStr(A_LoopReadLine, "MULTI", true)){
        ; 設定多選模式
        opt_multi[tabcount] := 1
    }
    else if(InStr(A_LoopReadLine, "NEXT", true)){
        ; 下一頁按鈕 - 使用特殊熱鍵
        yPos += 35
        Gui, Add, Button, x20 y%yPos% w340 h30 gCXR3ButtonNext, 下一頁(&N)
    }
    else if(InStr(A_LoopReadLine, "::", false)){
        ; 縮寫按鈕
        tmpstr := StrSplit(A_LoopReadLine, "::")
        abbr_str[tmpstr[1]] := tmpstr[2]
        buttonIndex++
        buttonName := "Button" . tabcount . "_" . buttonIndex
        yPos += 35
        
        ; 加入快捷鍵
        if (pageButtonIndex <= hotkeys.MaxIndex()){
            hotkeyLabel := "(&" . hotkeys[pageButtonIndex] . ")"
            pageButtonIndex++
        }
        else {
            hotkeyLabel := ""
        }
        buttonLabel := tmpstr[1] . " " . hotkeyLabel
        
        ; 檢查是否包含 {LtRt} 或類似的選擇標記
        if (InStr(tmpstr[2], "{LtRt}") || InStr(tmpstr[2], "{LungSel}") || InStr(tmpstr[2], "{LungDxSel}")){
            Gui, Add, Button, x20 y%yPos% w340 h30 v%buttonName% gCXR3ButtonClickWithMenu, %buttonLabel%
            buttonTexts[buttonName] := tmpstr[2]
        }
        else {
            Gui, Add, Button, x20 y%yPos% w340 h30 v%buttonName% gCXR3ButtonClick2, %buttonLabel%
            buttonTexts[buttonName] := tmpstr[2]
        }
    }
    else if(A_LoopReadLine != ""){
        ; 普通按鈕
        buttonIndex++
        buttonName := "Button" . tabcount . "_" . buttonIndex
        yPos += 35
        
        ; 加入快捷鍵
        if (pageButtonIndex <= hotkeys.MaxIndex()){
            hotkeyLabel := "(&" . hotkeys[pageButtonIndex] . ")"
            pageButtonIndex++
        }
        else {
            hotkeyLabel := ""
        }
        buttonLabel := A_LoopReadLine . " " . hotkeyLabel
        
        ; 檢查是否包含選擇標記
        if (InStr(A_LoopReadLine, "{LtRt}") || InStr(A_LoopReadLine, "{LungSel}") || InStr(A_LoopReadLine, "{LungDxSel}")){
            Gui, Add, Button, x20 y%yPos% w340 h30 v%buttonName% gCXR3ButtonClickWithMenu, %buttonLabel%
            buttonTexts[buttonName] := A_LoopReadLine
        }
        else {
            Gui, Add, Button, x20 y%yPos% w340 h30 v%buttonName% gCXR3ButtonClick, %buttonLabel%
            buttonTexts[buttonName] := A_LoopReadLine
        }
    }
}

Gui Tab  ; 結束Tab控件

; 右側已選擇項目顯示區
Gui, Add, GroupBox, x380 y50 w250 h600, 已選擇項目
Gui, Add, Edit, x390 y70 w230 h570 vSelectedDisplay +Multi +ReadOnly +VScroll

; 設定焦點到第一個Tab
GuiControl, CXR3:Focus, taba
 
; 顯示GUI
Gui, Show, w640 h660, X-ray Report Assistant - %currentFile%

; 啟用數字鍵切換Tab的熱鍵
Hotkey, IfWinActive, X-ray Report Assistant
Loop, 9
{
    Hotkey, %A_Index%, CXR3TabSwitch
}
Hotkey, IfWinActive
 
Return
 
; Tab切換熱鍵處理
CXR3TabSwitch:
    tabNum := A_ThisHotkey
    GuiControl, CXR3:Choose, taba, %tabNum%
return
 
; 鎖定/解鎖檔案選擇
CXR3LockFile:
GuiControlGet, isEnabled, CXR3:Enabled, SelectedFile
if (isEnabled) {
    GuiControl, CXR3:Disable, SelectedFile
    GuiControl, CXR3:, CXR3LockFile, 解鎖(&U)
    ; 設定焦點到Tab控件
    GuiControl, CXR3:Focus, taba
} else {
    GuiControl, CXR3:Enable, SelectedFile
    GuiControl, CXR3:, CXR3LockFile, 鎖定(&L)
}
return
 
; 清空所有選擇
CXR3ClearAll:
desc := ""
selectedItems := {}
GuiControl, CXR3:, SelectedDisplay,
return
 
; 檔案選擇變更事件
CXR3FileChanged:
Gui, CXR3:Submit, NoHide
currentFile := SelectedFile
; 重新建立整個GUI
Gosub, CXR3CreateGUI
Return
 
; 下一頁按鈕
CXR3ButtonNext:
GuiControlGet, selectedTab, CXR3:, taba
tabNum := RegExReplace(selectedTab, "Tab ", "")
nextTab := tabNum + 1
if (nextTab <= tabcount_total) {
    GuiControl, CXR3:Choose, taba, %nextTab%
}
return
 
; 普通按鈕點擊
CXR3ButtonClick:
buttonName := A_GuiControl
GuiControlGet, ButtonText, CXR3:, %buttonName%
 
; 移除快捷鍵標記
ButtonText := RegExReplace(ButtonText, " \(&[A-Z]\)$", "")
 
; 如果buttonTexts中有儲存的文字，使用儲存的，否則使用按鈕文字
if (buttonTexts[buttonName])
    fullText := buttonTexts[buttonName]
else
    fullText := ButtonText
 
desc .= fullText
desc .= "`r"
 
; 更新已選擇顯示
selectedItems[buttonName] := fullText
CXR3UpdateSelectedDisplay()
 
; 檢查是否自動跳到下一頁
GuiControlGet, selectedTab, CXR3:, taba
tabNum := RegExReplace(selectedTab, "Tab ", "")
if(!opt_multi[tabNum]){
    nextTab := tabNum + 1
    if (nextTab <= tabcount_total) {
        GuiControl, CXR3:Choose, taba, %nextTab%
    }
}
Return
 
; 縮寫按鈕點擊
CXR3ButtonClick2:
buttonName := A_GuiControl
GuiControlGet, ButtonText, CXR3:, %buttonName%
 
; 移除快捷鍵標記
ButtonText := RegExReplace(ButtonText, " \(&[A-Z]\)$", "")
 
; 優先使用buttonTexts中儲存的完整文字
if (buttonTexts[buttonName])
    fullText := buttonTexts[buttonName]
else if (abbr_str[ButtonText])
    fullText := abbr_str[ButtonText]
else
    fullText := ButtonText
 
desc .= fullText
desc .= "`r"
 
; 更新已選擇顯示
selectedItems[buttonName] := ButtonText . " → " . fullText
CXR3UpdateSelectedDisplay()
 
; 檢查是否自動跳到下一頁
GuiControlGet, selectedTab, CXR3:, taba
tabNum := RegExReplace(selectedTab, "Tab ", "")
if(!opt_multi[tabNum]){
    nextTab := tabNum + 1
    if (nextTab <= tabcount_total) {
        GuiControl, CXR3:Choose, taba, %nextTab%
    }
}
Return
 
; 帶有選單的按鈕點擊
CXR3ButtonClickWithMenu:
currentButton := A_GuiControl
GuiControlGet, ButtonText, CXR3:, %currentButton%
 
; 移除快捷鍵標記
ButtonText := RegExReplace(ButtonText, " \(&[A-Z]\)$", "")
 
; 獲取按鈕的完整文字
if (buttonTexts[currentButton])
    fullText := buttonTexts[currentButton]
else if (abbr_str[ButtonText])
    fullText := abbr_str[ButtonText]
else
    fullText := ButtonText
 
; 儲存當前按鈕和文字供MenuHandler使用
currentButtonForMenu := currentButton
currentFullTextForMenu := fullText
currentButtonTextForMenu := ButtonText
 
; 建立並顯示選單
if (InStr(fullText, "{LtRt}")){
    ; 建立LtRt選單
    Try Menu, LtRtMenu, DeleteAll
    Menu, LtRtMenu, Add, Left(&L), CXR3MenuHandlerLtRt
    Menu, LtRtMenu, Add, Right(&R), CXR3MenuHandlerLtRt
    Menu, LtRtMenu, Add, Bilateral(&B), CXR3MenuHandlerLtRt
    Menu, LtRtMenu, Show
}
else if (InStr(fullText, "{LungSel}")){
    ; 建立Lung選單
    Try Menu, LungMenu, DeleteAll
    Menu, LungMenu, Add, right upper lung(&1), CXR3MenuHandlerLung
    Menu, LungMenu, Add, right middle lung(&2), CXR3MenuHandlerLung
    Menu, LungMenu, Add, right lower lung(&3), CXR3MenuHandlerLung
    Menu, LungMenu, Add, left upper lung(&4), CXR3MenuHandlerLung
    Menu, LungMenu, Add, left lower lung(&5), CXR3MenuHandlerLung
    Menu, LungMenu, Add, bilateral lung(&6), CXR3MenuHandlerLung
    Menu, LungMenu, Add, bilateral lower lung(&7), CXR3MenuHandlerLung
    Menu, LungMenu, Show
}
else if (InStr(fullText, "{LungDxSel}")){
    ; 建立Dx選單
    Try Menu, DxMenu, DeleteAll
    Menu, DxMenu, Add, DDx: pneumonia(&P), CXR3MenuHandlerDx
    Menu, DxMenu, Add, DDx: pulmonary edema(&E), CXR3MenuHandlerDx
    Menu, DxMenu, Add, DDx: atelectasis(&A), CXR3MenuHandlerDx
    Menu, DxMenu, Add, DDx: tumor(&T), CXR3MenuHandlerDx
    Menu, DxMenu, Add, Clinical correlation is needed(&C), CXR3MenuHandlerDx
    Menu, DxMenu, Show
}
Return
 
; LtRt選單處理
CXR3MenuHandlerLtRt:
buttonName := currentButtonForMenu
fullText := currentFullTextForMenu
ButtonText := currentButtonTextForMenu
 
; 移除選單快捷鍵標記並取得實際選項
selectedOption := RegExReplace(A_ThisMenuItem, "\(&[A-Z0-9]\)$", "")
 
; 替換佔位符
StringReplace, fullText, fullText, {LtRt}, %selectedOption%
 
; 添加到描述
desc .= fullText
desc .= "`r"
 
; 更新已選擇顯示
selectedItems[buttonName] := ButtonText . " → " . fullText
CXR3UpdateSelectedDisplay()
 
; 檢查是否自動跳到下一頁
GuiControlGet, selectedTab, CXR3:, taba
tabNum := RegExReplace(selectedTab, "Tab ", "")
if(!opt_multi[tabNum]){
    nextTab := tabNum + 1
    if (nextTab <= tabcount_total) {
        GuiControl, CXR3:Choose, taba, %nextTab%
    }
}
Return
 
; Lung選單處理
CXR3MenuHandlerLung:
buttonName := currentButtonForMenu
fullText := currentFullTextForMenu
ButtonText := currentButtonTextForMenu
 
; 移除選單快捷鍵標記並取得實際選項
selectedOption := RegExReplace(A_ThisMenuItem, "\(&[A-Z0-9]\)$", "")
 
; 替換佔位符
StringReplace, fullText, fullText, {LungSel}, %selectedOption%
 
; 添加到描述
desc .= fullText
desc .= "`r"
 
; 更新已選擇顯示
selectedItems[buttonName] := ButtonText . " → " . fullText
CXR3UpdateSelectedDisplay()
 
; 檢查是否自動跳到下一頁
GuiControlGet, selectedTab, CXR3:, taba
tabNum := RegExReplace(selectedTab, "Tab ", "")
if(!opt_multi[tabNum]){
    nextTab := tabNum + 1
    if (nextTab <= tabcount_total) {
        GuiControl, CXR3:Choose, taba, %nextTab%
    }
}
Return
 
; Dx選單處理
CXR3MenuHandlerDx:
buttonName := currentButtonForMenu
fullText := currentFullTextForMenu
ButtonText := currentButtonTextForMenu
 
; 移除選單快捷鍵標記並取得實際選項
selectedOption := RegExReplace(A_ThisMenuItem, "\(&[A-Z0-9]\)$", "")
 
; 替換佔位符
StringReplace, fullText, fullText, {LungDxSel}, %selectedOption%
 
; 添加到描述
desc .= fullText
desc .= "`r"
 
; 更新已選擇顯示
selectedItems[buttonName] := ButtonText . " → " . fullText
CXR3UpdateSelectedDisplay()
 
; 檢查是否自動跳到下一頁
GuiControlGet, selectedTab, CXR3:, taba
tabNum := RegExReplace(selectedTab, "Tab ", "")
if(!opt_multi[tabNum]){
    nextTab := tabNum + 1
    if (nextTab <= tabcount_total) {
        GuiControl, CXR3:Choose, taba, %nextTab%
    }
}
Return
 
; 更新已選擇項目的顯示
CXR3UpdateSelectedDisplay(){
    global selectedItems
    displayText := ""
    count := 0
    for key, value in selectedItems {
        count++
        if (count > 1)
            displayText .= "`r`n"
        displayText .= count . ". " . value
    }
    GuiControl, CXR3:, SelectedDisplay, %displayText%
}

; 輸出結果
CXR3out:
if (desc = ""){
    MsgBox, 沒有選擇任何項目！
    return
}
 
desc := StrReplace(desc, "`r", "`r`n")
 
; 使用COM物件(中文可用)
clipboardData := ComObjCreate("htmlfile")
clipboardData.parentWindow.clipboardData.setData("text", desc)
 
WinActivate, ahk_id %ActiveId%
Sleep, 100
Send, ^v
Sleep, 50
Send, {Enter}
 
desc := ""
selectedItems := {}
GuiControl, CXR3:, SelectedDisplay,
return
 
; GUI關閉 (命名GUI: CXR3GuiClose)
CXR3GuiClose:
; 清理熱鍵
Hotkey, IfWinActive, X-ray Report Assistant
Loop, 9
{
    Hotkey, %A_Index%, Off
}
Hotkey, IfWinActive
ExitApp

; 按Escape關閉GUI
GuiEscape:
; 清理熱鍵
Hotkey, IfWinActive, X-ray Report Assistant
Loop, 9
{
    Hotkey, %A_Index%, Off
}
Hotkey, IfWinActive
ExitApp
