; CXR3 - X-ray Report Assistant (模板式報告產生器)
; 此檔案放在 ahk-scripts 目錄下，範本 .txt 檔案存放於 cxr\ 子資料夾

::cxr3;::
; 初始化變數
selectedItems := {}  ; 儲存已選擇的項目
currentFile := ""    ; 當前選擇的檔案

; 記錄目前視窗
WinGet, ActiveId, ID, A

; 搜尋 cxr 子目錄下的所有txt檔案
cxrDir := A_ScriptDir . "\cxr\"
FileList := ""
Loop, %cxrDir%*.txt
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
Gosub, CreateGUI

Return

; 建立新的GUI
CreateGUI:
; 先銷毀舊的GUI（如果存在）
Gui, Destroy

; 重置變數
selectedItems := {}
desc := ""
opt_multi := []
abbr_str := []
buttonTexts := {}  ; 儲存按鈕的完整文字
hotkeys := ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]

; GUI基本設置
Gui, Font, s12

; 上方控制區
Gui, Add, Text, x10 y10 w80 h30, 選擇模板:
Gui, Add, DropDownList, x90 y10 w150 h90 vSelectedFile gFileChanged, %FileList%
GuiControl,, SelectedFile, %currentFile%
Gui, Add, Button, x250 y10 w80 h30 gLockFile, 鎖定(&L)
Gui, Add, Button, x340 y10 w100 h30 gCXRout, Copy代碼(&S)
Gui, Add, Button, x450 y10 w80 h30 gClearAll, 清空(&C)

; 計算頁籤數量
tabcount_total := 1
tab_str := "Tab 1"
cxrFilePath := cxrDir . currentFile

Loop, read, %cxrFilePath%
{
    if (InStr(A_LoopReadLine, "--Page--", false)){
        tabcount_total := tabcount_total + 1
        tab_str .= "|Tab "
        tab_str .= tabcount_total
    }
}

; 創建Tab控件 (左側) - 減少寬度
Gui Add, Tab3, x10 y50 w300 h600 vtaba, % tab_str

tabcount := 1
Gui Tab, %tabcount%
Gui Add, Text, x1 y90, " " ; 定位用
yPos := 90
buttonIndex := 0
pageButtonIndex := 1  ; 修正：從1開始，不是0

; 讀取檔案並生成按鈕
Loop, read, %cxrFilePath%
{
    if (InStr(A_LoopReadLine, "--Page--", false)){
        ; 換頁
        tabcount := tabcount + 1
        Gui Tab, %tabcount%
        opt_multi[tabcount] := 0
        Gui Add, Text, x1 y90, " " ; 定位用
        yPos := 90
        buttonIndex := 0
        pageButtonIndex := 1  ; 重置每頁的按鈕索引，從1開始
    }
    else if(InStr(A_LoopReadLine, "TEXT::", false)){
        ; 顯示文字標籤
        yPos += 35
        Gui, Add, Text, x20 y%yPos% w280 h20, % Substr(A_LoopReadLine, 7)
    }
    else if(InStr(A_LoopReadLine, "MULTI", true)){
        ; 設定多選模式
        opt_multi[tabcount] := 1
    }
    else if(InStr(A_LoopReadLine, "NEXT", true)){
        ; 下一頁按鈕 - 使用特殊熱鍵
        yPos += 35
        Gui, Add, Button, x20 y%yPos% w280 h30 gButtonNext, 下一頁(&N)
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
            Gui, Add, Button, x20 y%yPos% w280 h30 v%buttonName% gButtonClickWithMenu, %buttonLabel%
            buttonTexts[buttonName] := tmpstr[2]
        }
        else {
            Gui, Add, Button, x20 y%yPos% w280 h30 v%buttonName% gButtonClick2, %buttonLabel%
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
            Gui, Add, Button, x20 y%yPos% w280 h30 v%buttonName% gButtonClickWithMenu, %buttonLabel%
            buttonTexts[buttonName] := A_LoopReadLine
        }
        else {
            Gui, Add, Button, x20 y%yPos% w280 h30 v%buttonName% gButtonClick, %buttonLabel%
            buttonTexts[buttonName] := A_LoopReadLine
        }
    }
}

Gui Tab  ; 結束Tab控件

; 右側已選擇項目顯示區 - 高度砍半
Gui, Add, GroupBox, x320 y50 w220 h280, 已選擇項目
Gui, Add, Edit, x330 y70 w200 h250 vSelectedDisplay +Multi +ReadOnly +VScroll

; 右側舊報告顯示區
Gui, Add, Button, x320 y340 w220 h30 gShowOldReport3, 顯示舊報告(&2)
Gui, Add, GroupBox, x320 y375 w220 h275, 舊報告
Gui, Add, Edit, x330 y395 w200 h245 vOldReportDisplay3 +Multi +ReadOnly +VScroll

; 設定焦點到第一個Tab
GuiControl, Focus, taba

; 顯示GUI
Gui, Show, w550 h660, X-ray Report Assistant - %currentFile%

; 啟用數字鍵切換Tab的熱鍵
Hotkey, IfWinActive, X-ray Report Assistant
Loop, 9
{
    Hotkey, %A_Index%, TabSwitch
}
Hotkey, IfWinActive

Return

; Tab切換熱鍵處理
TabSwitch:
    tabNum := A_ThisHotkey
    GuiControl, Choose, taba, %tabNum%
return

; 鎖定/解鎖檔案選擇
LockFile:
GuiControlGet, isEnabled, Enabled, SelectedFile
if (isEnabled) {
    GuiControl, Disable, SelectedFile
    GuiControl,, LockFile, 解鎖(&U)
    ; 設定焦點到Tab控件
    GuiControl, Focus, taba
} else {
    GuiControl, Enable, SelectedFile
    GuiControl,, LockFile, 鎖定(&L)
}
return

; 清空所有選擇
ClearAll:
desc := ""
selectedItems := {}
GuiControl,, SelectedDisplay,
return

; 檔案選擇變更事件
FileChanged:
Gui, Submit, NoHide
currentFile := SelectedFile
; 重新建立整個GUI
Gosub, CreateGUI
Return

; 下一頁按鈕
ButtonNext:
GuiControlGet, selectedTab,, taba
tabNum := RegExReplace(selectedTab, "Tab ", "")
nextTab := tabNum + 1
if (nextTab <= tabcount_total) {
    GuiControl, Choose, taba, %nextTab%
}
return

; 普通按鈕點擊
ButtonClick:
buttonName := A_GuiControl
GuiControlGet, ButtonText,, %buttonName%

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
UpdateSelectedDisplay()

; 檢查是否自動跳到下一頁
GuiControlGet, selectedTab,, taba
tabNum := RegExReplace(selectedTab, "Tab ", "")
if(!opt_multi[tabNum]){
    nextTab := tabNum + 1
    if (nextTab <= tabcount_total) {
        GuiControl, Choose, taba, %nextTab%
    }
}
Return

; 縮寫按鈕點擊
ButtonClick2:
buttonName := A_GuiControl
GuiControlGet, ButtonText,, %buttonName%

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
UpdateSelectedDisplay()

; 檢查是否自動跳到下一頁
GuiControlGet, selectedTab,, taba
tabNum := RegExReplace(selectedTab, "Tab ", "")
if(!opt_multi[tabNum]){
    nextTab := tabNum + 1
    if (nextTab <= tabcount_total) {
        GuiControl, Choose, taba, %nextTab%
    }
}
Return

; 帶有選單的按鈕點擊
ButtonClickWithMenu:
currentButton := A_GuiControl
GuiControlGet, ButtonText,, %currentButton%

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
    Menu, LtRtMenu, Add, Left(&L), MenuHandlerLtRt
    Menu, LtRtMenu, Add, Right(&R), MenuHandlerLtRt
    Menu, LtRtMenu, Add, Bilateral(&B), MenuHandlerLtRt
    Menu, LtRtMenu, Show
}
else if (InStr(fullText, "{LungSel}")){
    ; 建立Lung選單
    Try Menu, LungMenu, DeleteAll
    Menu, LungMenu, Add, right upper lung(&1), MenuHandlerLung
    Menu, LungMenu, Add, right middle lung(&2), MenuHandlerLung
    Menu, LungMenu, Add, right lower lung(&3), MenuHandlerLung
    Menu, LungMenu, Add, left upper lung(&4), MenuHandlerLung
    Menu, LungMenu, Add, left lower lung(&5), MenuHandlerLung
    Menu, LungMenu, Add, bilateral lung(&6), MenuHandlerLung
    Menu, LungMenu, Add, bilateral lower lung(&7), MenuHandlerLung
    Menu, LungMenu, Show
}
else if (InStr(fullText, "{LungDxSel}")){
    ; 建立Dx選單
    Try Menu, DxMenu, DeleteAll
    Menu, DxMenu, Add, DDx: pneumonia(&P), MenuHandlerDx
    Menu, DxMenu, Add, DDx: pulmonary edema(&E), MenuHandlerDx
    Menu, DxMenu, Add, DDx: atelectasis(&A), MenuHandlerDx
    Menu, DxMenu, Add, DDx: tumor(&T), MenuHandlerDx
    Menu, DxMenu, Add, Clinical correlation is needed(&C), MenuHandlerDx
    Menu, DxMenu, Show
}
Return

; LtRt選單處理
MenuHandlerLtRt:
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
UpdateSelectedDisplay()

; 檢查是否自動跳到下一頁
GuiControlGet, selectedTab,, taba
tabNum := RegExReplace(selectedTab, "Tab ", "")
if(!opt_multi[tabNum]){
    nextTab := tabNum + 1
    if (nextTab <= tabcount_total) {
        GuiControl, Choose, taba, %nextTab%
    }
}
Return

; Lung選單處理
MenuHandlerLung:
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
UpdateSelectedDisplay()

; 檢查是否自動跳到下一頁
GuiControlGet, selectedTab,, taba
tabNum := RegExReplace(selectedTab, "Tab ", "")
if(!opt_multi[tabNum]){
    nextTab := tabNum + 1
    if (nextTab <= tabcount_total) {
        GuiControl, Choose, taba, %nextTab%
    }
}
Return

; Dx選單處理
MenuHandlerDx:
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
UpdateSelectedDisplay()

; 檢查是否自動跳到下一頁
GuiControlGet, selectedTab,, taba
tabNum := RegExReplace(selectedTab, "Tab ", "")
if(!opt_multi[tabNum]){
    nextTab := tabNum + 1
    if (nextTab <= tabcount_total) {
        GuiControl, Choose, taba, %nextTab%
    }
}
Return

; 更新已選擇項目的顯示
UpdateSelectedDisplay(){
    global selectedItems
    displayText := ""
    count := 0
    for key, value in selectedItems {
        count++
        if (count > 1)
            displayText .= "`r`n"
        displayText .= count . ". " . value
    }
    GuiControl,, SelectedDisplay, %displayText%
}

; 顯示舊報告
ShowOldReport3:
Gui, Submit, NoHide

ClipboardBackup := Clipboard

; 取得舊報告內容
dicom := GetDICOMData()
accessionNum := GetAccessionNumber(dicom)
oldReport := GetOldReportContent(accessionNum, false)

; 清理報告格式
oldReport := RegExReplace(oldReport, "(\r\n|\n|\r)", "`r`n")

; 顯示在舊報告 Edit 控件中
GuiControl,, OldReportDisplay3, %oldReport%

; 恢復原始剪貼簿內容
Clipboard := ClipboardBackup
return

; 輸出結果
CXRout:
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
GuiControl,, SelectedDisplay,
return

; GUI關閉
GuiClose:
; 清理熱鍵
Hotkey, IfWinActive, X-ray Report Assistant
Loop, 9
{
    Hotkey, %A_Index%, Off
}
Hotkey, IfWinActive
Gui, Destroy
return

; 按Escape關閉GUI
GuiEscape:
; 清理熱鍵
Hotkey, IfWinActive, X-ray Report Assistant
Loop, 9
{
    Hotkey, %A_Index%, Off
}
Hotkey, IfWinActive
Gui, Destroy
return
