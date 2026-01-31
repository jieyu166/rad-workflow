/*
Hotstring Menu Function HotstringMenu(TextList) and Subroutine HotstringMenuAction:
=============================================
Found at:
http://www.computoredge.com/AutoHotkey/Free_AutoHotkey_Scripts_and_Apps_for_Learning_and_Generating_Ideas.html#HotstringMenu

Originally, discussed the in the book, "Beginning AutoHotkey Hotstrings: 
A Practical Guide for Creative AutoCorrection, Text Expansion and Text Replacement", found at:
https://www.computoredgebooks.com/Beginning-AutoHotkey-Hotstrings-All-File-Formats_c40.htm?sourceCode=AHKScript

The following function and subroutine creates a menu of replacement option when
activating the a Hotstring. Call the function in the form:
:x:flux::TextMenu("Flux | &0,Flux #&1,Flux #&2")
The vertical bar delimiter | allows the addition of descriptive tags and single-key
shortcuts (e.g. &0 for the zero key) which will not appear in the replacement text.

November 22, 2019, Now includes the three-parameter variadic function 
HotstringMenuV(MenuType,Handle,MenuArray*) for using simple and associative
arrays.
*/

; Examples of arrays set up in the auto-execute section:

; Original HotstringMenu() function:

; 全域變數用於儲存項目文字
;global MenuItemTexts := {}
;global CurrentTextForMenu := ""

; 擴展版的 HotstringMenuV - 支援子選單和選擇標記

; Variadic function HotstringMenuV(MenuType,Handle,MenuArray*)
; 修改 HotstringMenuV 函數以支援選擇標記
HotstringMenuV(MenuType,Handle,MenuArray*)
{
  global MenuItemTexts := {}  ; 儲存原始文字
  submen := 0
  cnt := 1
  
  For Each, Item in MenuArray
  {
    ; 檢查特殊標記
    hasLtRt := InStr(Item, "{LtRt}")
    hasLungSel := InStr(Item, "{LungSel}")
    hasLungDxSel := InStr(Item, "{LungDxSel}")
    hasSelection := hasLtRt || hasLungSel || hasLungDxSel
    
    If InStr(Item,"BRK",true){
      Menu, MyMenu, Add  ; 添加分隔线
      Continue 
    }
    Else if InStr(Item,"SUBMENU",true)
    {
        submen := mod(submen + 1,2)
        Continue 
    }
    Else if InStr(Item,"SUBNAME",true)
    {   
        Item := SubStr(Item,8)
        If (MenuType = "A")
            Menu, MyMenu, Add, % "&" Chr(cnt+96) " " Item, :MySub
        Else If (MenuType = "N")
            Menu, MyMenu, Add, % "&" cnt " " Item, :MySub
        Else
            Menu, MySub, Add, % Item, % Handle
        cnt := cnt +1
        Continue
    }
    
    ; 根據是否有選擇標記決定使用哪個處理器
    handlerLabel := hasSelection ? "MenuItemWithSelection" : Handle
    
    ; 如果有選擇標記，儲存原始文字
    if (hasSelection) {
        menuKey := "Item_" . cnt
        MenuItemTexts[menuKey] := Item
        
        ; 移除標記用於顯示
        displayItem := Item
        displayItem := StrReplace(displayItem, "{LtRt}", "[選擇]")
        displayItem := StrReplace(displayItem, "{LungSel}", "[肺葉]")
        displayItem := StrReplace(displayItem, "{LungDxSel}", "[診斷]")
    } else {
        displayItem := Item
    }
    
    If(submen){
        If (MenuType = "A")
            Menu, MySub, Add, % "&" Chr(cnt+96) " " displayItem, % handlerLabel
        Else If (MenuType = "N")
            Menu, MySub, Add, % "&" cnt "  " displayItem, % handlerLabel
        Else
            Menu, MySub, Add, % displayItem , % handlerLabel
    }Else{
        If (MenuType = "A")
            Menu, MyMenu, Add, % "&" Chr(cnt+96) " " displayItem, % handlerLabel
        Else If (MenuType = "N")
            Menu, MyMenu, Add, % "&" cnt "  " displayItem, % handlerLabel
        Else
            Menu, MyMenu, Add, % displayItem , % handlerLabel
    }
    cnt := cnt +1
  }
  
  Menu, MyMenu, Show
  Menu, MyMenu, DeleteAll
  Try Menu, MySub, DeleteAll
}

; 確保所有需要的標籤都存在且正確定義

; MenuShortcut 標籤
MenuShortcut:
  TextOut := SubStr(A_ThisMenuItem, 4)
  SendInput {raw}%TextOut%
Return

; MenuShortcut2 標籤 - 用 | 分隔簡寫跟輸入文字
MenuShortcut2:
  TextOut := SubStr(A_ThisMenuItem, 4)
  If(InStr(TextOut,"|")){
    InsertText := StrSplit(TextOut, "|") 
    TextOut:= StrReplace(RTrim(InsertText[2]), "&")
  }
  SendInput {raw}%TextOut%
Return

; HotstringMenuAction 標籤
HotstringMenuAction:
  InsertText := StrSplit(A_ThisMenuItem, "|")
  TextOut := StrReplace(RTrim(InsertText[1]), "&")
  SendInput {raw}%TextOut%
Return

; 處理包含選擇標記的項目
MenuItemWithSelection:
    ; 從點擊的項目找回原始文字
    clickedItem := A_ThisMenuItem
    originalText := ""
    
    ; 移除快捷鍵前綴
    cleanText := RegExReplace(clickedItem, "^&[a-zA-Z0-9]\s+", "")
    
    ; 在儲存的文字中尋找
    for key, value in MenuItemTexts {
        testValue := value
        testValue := StrReplace(testValue, "{LtRt}", "[選擇]")
        testValue := StrReplace(testValue, "{LungSel}", "[肺葉]")
        testValue := StrReplace(testValue, "{LungDxSel}", "[診斷]")
        
        if (testValue = cleanText) {
            originalText := value
            break
        }
    }
    
    ; 根據標記類型顯示子選單
    if (InStr(originalText, "{LtRt}")) {
        ShowLtRtSubMenu(originalText)
    }
    else if (InStr(originalText, "{LungSel}")) {
        ShowLungSubMenu(originalText)
    }
    else if (InStr(originalText, "{LungDxSel}")) {
        ShowDxSubMenu(originalText)
    }
    else {
        ; 沒有找到標記，直接輸出
        SendInput {raw}%originalText%%A_EndChar%
    }
Return

; LtRt 子選單
ShowLtRtSubMenu(text) {
    global SelectedMenuText := text
    
    Menu, LtRtSub, Add, &Left, LtRtSubHandler
    Menu, LtRtSub, Add, &Right, LtRtSubHandler  
    Menu, LtRtSub, Add, &Bilateral, LtRtSubHandler
    Menu, LtRtSub, Show
    Menu, LtRtSub, Delete
}

LtRtSubHandler:
    selection := RegExReplace(A_ThisMenuItem, "&", "")
    output := StrReplace(SelectedMenuText, "{LtRt}", selection)
    SendInput {raw}%output%%A_EndChar%
Return

; Lung 子選單
ShowLungSubMenu(text) {  ; 右側 REW 左側 UIO 雙側 BN
    global SelectedMenuText := text
    
    Menu, LungSub, Add, righ&t upper lung(RUL), LungSubHandler
    Menu, LungSub, Add, right middl&e lung(RML), LungSubHandler
    Menu, LungSub, Add, right lo&wer lung(RLL), LungSubHandler
	Menu, LungSub, Add, &right lung, LungSubHandler
    Menu, LungSub, Add, left &upper lung(LUL), LungSubHandler
    Menu, LungSub, Add, left upper lung(LUL) l&ingula, LungSubHandler
    Menu, LungSub, Add, left l&ower lung(LLL), LungSubHandler
    Menu, LungSub, Add, &left lung, LungSubHandler
	Menu, LungSub, Add, &bilateral lung, LungSubHandler
    Menu, LungSub, Add, bilateral lower lu&ng, LungSubHandler
    Menu, LungSub, Add, 右側 REW 左側 UIO 雙側 BN, LungSubHandler
    Menu, LungSub, Add, _, LungSubHandler
    Menu, LungSub, Show
    Menu, LungSub, Delete
}

LungSubHandler:
    selection := RegExReplace(A_ThisMenuItem, "&", "")
    output := StrReplace(SelectedMenuText, "{LungSel}", selection)
    SendInput {raw}%output%%A_EndChar%
Return

; Dx 子選單
ShowDxSubMenu(text) {
    global SelectedMenuText := text
    
    Menu, DxSub, Add, DDx: &pneumonia, DxSubHandler
    Menu, DxSub, Add, DDx: pulmonary &edema, DxSubHandler
    Menu, DxSub, Add, DDx: &atelectasis, DxSubHandler
    Menu, DxSub, Add, DDx: &tumor, DxSubHandler
    Menu, DxSub, Add, &Clinical correlation is needed, DxSubHandler
    Menu, DxSub, Show
    Menu, DxSub, Delete
}

DxSubHandler:
    selection := RegExReplace(A_ThisMenuItem, "&", "")
    output := StrReplace(SelectedMenuText, "{LungDxSel}", selection)
    SendInput {raw}%output%%A_EndChar%
Return