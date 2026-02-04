;============================================================================================
; X-ray
;============================================================================================

::cxr2;::
WinCXR:
WinGet, ActiveId, ID, A ;記錄目前視窗
Gui, Font, s14
Gui Add, Text, x10 y-25, " " ;定位用

; === 肺部發現按鈕 (最上方) ===
Gui Add, Button, x10 y10 w140 h35 gBtnApicalPleural, Apical pleural(&A)
Gui Add, Button, x160 yp w140 h35 gBtnEmphysema, Emphysema(&E)
Gui Add, Button, x310 yp w140 h35 gBtnHilarFullness, Hilar fullness(&H)
Gui Add, Button, x10 yp+40 w140 h35 gBtnMediastinal, Mediastinal(&M)
Gui Add, Button, x160 yp w140 h35 gBtnEff, 積液(&F)
Gui Add, Button, x310 yp w140 h35 gBtnCongestion, Congestion(&G)
Gui Add, Button, x10 yp+40 w140 h35 gCXR8, 吸氣不足(&I)
Gui Add, Button, x160 yp w140 h35 gCXR11, Edema通殺(&D)

; === 分隔線 ===
Gui Add, Text, x10 yp+40 w440 h2 0x10

; === CheckBox 和 Radio ===
Gui Add, CheckBox, x10 yp+5 w200 h23 vL1 checked1, &No active lung lesions
Gui Add, CheckBox, x220 yp w130 h23 vC1, 比較舊片
Gui Add, Radio, x10 yp+30 w140 h23 vL3, Cardiomegaly(&C)
Gui Add, Radio, xp+150 yp w140 h23 vL5, 邊緣擴大(&B)
Gui Add, Radio, xp+150 yp w100 h23 vL7 checked1, 心臟正常

; === 範本按鈕區 ===
Gui Add, Button, x10 yp+30 w140 h45 gCXR1, 正常(&7)
Gui Add, Button, x160 yp w140 h45 gCXR3, 硬化+輕退化
Gui Add, Button, x310 yp w140 h45 gCXR4, 硬化+骨密低(&8)
Gui Add, Button, xp yp+50 w140 h45 gCXR5, 硬化+骨鬆(&9)

Gui Add, Button, x10 yp+5 w140 h45 gCXR6, 洗腎
Gui Add, Button, x160 yp w140 h45 gCXR10, 心臟手術術後
Gui Add, Button, x10 yp+50 w140 h45 gCXR7, 小孩(&K)
Gui Add, Button, x10 yp+50 w120 h30 gMergeExams, 合併標題(&Z)
Gui Add, Button, x140 yp w120 h30 gCXR9, 清除選項(&R)
Gui Add, Button, x270 yp w120 h30 gCXRclose, 切換&Spine
Gui Add, Button, x10 yp+40 w120 h30 gSeeCXRAIforCXR, 看AI報告(&1)
Gui Add, Button, x140 yp w120 h30 gCopyOld2, 顯示舊報告(&2)
Gui Add, Button, x270 yp w120 h30 gCopyOldSmart, 複製舊報告(&3)

; === 舊報告顯示區 (右側) ===
Gui Add, Edit, x460 y10 w200 h300 vOldReportContent Multi VScroll

Gui Show, w680 h440, CXR 範例
Return

CXRcommon:
Gui, Submit, NoHide
If(C1){
	gosub calldate
	desc := "`r"
}

; 只檢查 L1 (No active lung lesion) 和心臟大小選項 (L3/L5/L7)
If(L1){
	desc .= "No active lung lesion is noted.`r"
}

If(L3){
	desc .= "Cardiomegaly.`r"
}else if(L5){
    desc .= "Borderline cardiomegaly.`r"
}else if(L7){
	desc .= "Normal heart size.`r"
}
If(varL1){
	desc .= "Intimal calcification of aorta.`r"
}

If(varL2){
	desc .= "Degenerative change and spur formation of spine.`r"
}else{
	desc .= "Unremarkable bony structure.`r"
}
If(varL3=1){
	desc .= "Generalized diminished bone density.`r"
}else if(varL3=2){
	desc .= "Osteoporotic change of visible bony structures.`r"
}
return

CXR1:
varL1:=0
varL2:=0
varL3:=0
gosub CXRcommon
gosub CXRFinish
return

CXR3:
varL1:=1
varL2:=1
varL3:=0
gosub CXRcommon
gosub CXRFinish
return

SeeCXRAIforCXR:
gosub SeeCXRAI
return

CXR4:
varL1:=1
varL2:=1
varL3:=1
gosub CXRcommon
gosub CXRFinish
return

CXR5:
varL1:=1
varL2:=1
varL3:=2
gosub CXRcommon
gosub CXRFinish
return

CXR6:
GuiControl,, L1, 0
GuiControl,, L5, 1

varL1:=1
varL2:=1
varL3:=1
gosub CXRcommon
desc .= "Mild mediastinal widening.`r"
desc .= "Status post permcath catheter insertion at _right_left _chest.`r"
gosub CXRFinish
return


CXR9:
GuiControl,, C1, 0
GuiControl,, L1, 1
GuiControl,, L3, 0
GuiControl,, L5, 0
GuiControl,, L7, 1
GuiControl,, OldReportContent,
return


CXR7:
desc .= "Mild increased lung markings in bilateral perihilar region.`r"
desc .= "No cardiomegaly.`r"
desc .= "The bony structure is unremarkable.`r"
CopyCXRtoHISWithParam(1)
return

CXR8:
desc .= "Insufficient inspiration _and focal atelectasis of both lungs.`r"
CopyCXRtoHISWithParam(1)
return

CXR10:
desc .= "Status post endotracheal tube insertion, tip to carina _cm.`r"
desc .= "Pulmonary congestion pattern or emphysematous change of both lungs."
desc .= "Chest tubes in mediastinum.`r"
desc .= "Retained pacemaker wired noted.`r"
desc .= "Cardiomegaly.`rIntimal calcification of aorta.`rMild mediastinal widening.`r"
desc .= "Status post sternotomy with metallic wire fixation, _CABG, _valvular replacement.`r"
desc .= "Status post nasogastric tube insertion with tip in stomach.`r"
desc .= "Status post central venous catheter insertion via right neck.`r"
CopyCXRtoHISWithParam(1)
return

CXR11:
desc .= "Pulmonary congestion pattern or emphysematous change of both lungs.`r"
desc .= "Superimposed pneumonia or other occult entities can not be excluded.`r"
desc .= "_Bilateral minimal pleural effusion or pleural cahnges. `r"
desc .= "Bilateral hilar fullness, could be vascular shadows or others. `r"
CopyCXRtoHISWithParam(1)
return

; ============================================
; 肺部發現按鈕 (單獨輸出文字，類似 spine2)
; ============================================
BtnApicalPleural:
    desc := "Bilateral apical pleural thickening.`r"
    gosub CXRFinish
return

BtnEmphysema:
    desc := "Emphysematous change of both lungs.`r"
    gosub CXRFinish
return

BtnHilarFullness:
    desc := "Bilateral hilar fullness, could be vascular shadows or others.`r"
    gosub CXRFinish
return

BtnMediastinal:
    desc := "Mild mediastinal widening.`r"
    gosub CXRFinish
return

BtnCongestion:
    desc := "Mild pulmonary congestion pattern.`r"
    gosub CXRFinish
return

BtnEff:
    desc := "Bilateral _minimal pleural effusion or pleural cahnges.`r"
    gosub CXRFinish
return

CXRFinish:
CopyCXRtoHISWithParam(2)
WinActivate, CXR 範例
gosub CXR9
return

CXRclose:
Gui, Destroy
goto WinSpine
return


; 新增 CopyOld2 子程序
CopyOld2:
Gui, Submit, NoHide

ClipboardBackup := Clipboard ; 保存當前剪貼簿內容

; 取得舊報告內容
dicom := GetDICOMData()
accessionNum := GetAccessionNumber(dicom)
oldReport := GetOldReportContent(accessionNum, false) 

; 清理報告格式
oldReport := RegExReplace(oldReport, "(\r\n|\n|\r)", "`r`n")

; 顯示在 Edit 控件中
GuiControl,, OldReportContent, %oldReport%

; 恢復原始剪貼簿內容
Clipboard := ClipboardBackup

varCopyOld = 0
return

CopyOldSmart:
; 檢查 OldReportContent 是否有內容
if (OldReportContent != "") {
    ; 有內容：先輸出日期，再輸出內容
    gosub calldate
    desc := OldReportContent
    desc := RegExReplace(desc, "(\r\n|\n|\r)", "`n")
    CopyCXRtoHISWithParam(1)
} else {
    ; 無內容：呼叫原本的 CopyOld
    gosub CopyOld
}
return

::spine2;::
WinSpine:
WinGet, ActiveId, ID, A ;紀錄目前視窗
Gui Font, s14

; 移除所有 CheckBox，改為按鈕配置

; 第一排 - 標題選項
Gui Add, CheckBox, x10 y10 w120 h23 vLTitle, 包含標題(&T)
; [新增] 部位選擇 Radio Button
; 預設不勾選，保留彈性；若選了就會固定輸出該部位
Gui Add, Radio, x140 y10 w90 h23 vSpineLoc1, C-spine
Gui Add, Radio, x240 y10 w90 h23 vSpineLoc2, L-spine
Gui Add, CheckBox, x340 y10 w120 h23 vAddDash Checked1, 項目符號(-)

; 第二排按鈕
Gui Add, Button, x10 yp+50 w150 h50 gLspineDefault, L-spine 預設(&L)
Gui Add, Button, xp+160 yp w150 h50 gCspineDefault, C-spine 預設(&C)
Gui Add, Button, xp+160 yp w150 h50 gBtnInsertTitle, 輸出標題(&T)

; 第三排按鈕
Gui Add, Button, x10 yp+60 w150 h50 gBoneDensity1, 骨密低(&A)
Gui Add, Button, xp+160 yp w150 h50 gBoneDensity2, 骨質疏鬆(&O)
Gui Add, Button, xp+160 yp w150 h50 gBtnWedging, Ant. Wedging(&W)


; 第四排按鈕 - 原有功能
Gui Add, Button, x10 yp+60 w150 h50 gSpondylolisthesis, &Spondylolisthesis
Gui Add, Button, xp+160 yp w150 h50 gRetrolisthesis, &Retrolisthesis
Gui Add, Button, xp+160 yp w150 h50 gHypermobility, Hypermobility(&H)

; 第五排按鈕
Gui Add, Button, x10 yp+60 w150 h50 gFacetArthrosis, Facet arthrosis(&F)
Gui Add, Button, xp+160 yp w150 h50 gUncovertebralJoint, Uncovertebral(&U)
Gui Add, Button, xp+160 yp w150 h50 gNoHypermobility, &No hypermobility

Gui Add, Button, x10 yp+60 w150 h50 gUFJoint, Facet+Unco(&B)
Gui Add, Button, xp+160 yp w150 h50 gC1C2OA, C1-C2 OA(&1)
Gui Add, Button, xp+160 yp w150 h50 gPostOP, 術後組套(&P)

; 右側控制按鈕
Gui Add, Button, x500 y10 w120 h40 gSpineClose, 切換到 CXR(&Q)
Gui Add, Button, xp yp+50 w120 h40 gSpineClear, 清除內容
Gui Add, Button, xp yp+60 w120 h40 gMergeExams, 合併檢查(&Z)
Gui Add, Button, xp yp+60 w120 h40 gCopyOldFromSpine, 複製舊報告(&X)
Gui Add, Button, xp yp+50 w120 h40 gOpenForamenWeb, 裂孔網頁(&V)

Gui Show, w640 h400, Spine phases
; 記錄視窗標題，用於後續 focus 回來
WinGet, SpineWinID, ID, Spine phases
return

SpineOutput:
    Gui, Submit, NoHide
    
    ; 1. 處理 Dash (原本 AddDashPrefix 的邏輯)
    ;if (AddDash) {
        ; 如果勾選，且字串開頭不是 "- "，就加上去
    ;    if (SubStr(desc, 1, 2) != "- ")
    ;        desc := "- " . desc
    ;}
	finalDesc := ""
    
    ; 使用 Loop Parse 逐行讀取 desc 內容
    ; `n 是換行符號，`r 是回車符號 (忽略它以確保乾淨)
    Loop, Parse, desc, `n, `r
    {
        thisLine := Trim(A_LoopField) ; 去除前後空白
        
        ; 如果是空行，直接保留換行並跳過
        if (thisLine = "") {
            ; 這裡不加東西，因為最後組合時會補換行
            continue 
        }
        
        ; 判斷是否需要加 Dash
        ; 條件：
        ; 1. AddDash 被勾選
        ; 2. 這一行開頭還沒有 "- "
        ; 3. 這一行不是標題 (標題通常以 ":" 結尾，如 "L-spine:") -> 標題通常不加 Dash
        
        if (AddDash && SubStr(thisLine, 1, 2) != "- " && SubStr(thisLine, 0) != ":") {
            thisLine := "- " . thisLine
        }
        
        ; 重新組合 (每一行後面補一個 Enter)
        finalDesc .= thisLine . "`r"
    }
    
    ; 更新要輸出的變數
    desc := finalDesc

    ; 2. 執行輸出 (原本分散在各按鈕的邏輯)
    CopyCXRtoHISWithParam(1)
    
    ; 3. 視窗控制
    Sleep, 100
    WinActivate, Spine phases
	desc := ""
return

BtnInsertTitle:
    Gui, Submit, NoHide
    desc := ""
    
    if (SpineLoc1) {
        desc := "C-spine"
    } else if (SpineLoc2) {
        desc := "L-spine"
    } else {
        ; 如果都沒選，預設輸出 Spine: 或是提示
        desc := "Spine" 
    }    
	MsgBox, 4,, "(AP+Flex.+Ext.)?"
	IfMsgBox, Yes
	{
		desc .= "(AP{+}Flex.{+}Ext.)"
	}
	desc .=":`r"
    gosub SpineOutput 
return

; [按鈕 2] Anterior Wedging
BtnWedging:
    desc := "_ anterior wedging.`r"
    gosub SpineOutput 
return

; L-spine 預設組套
LspineDefault:
    ; 先取得 CheckBox 的值
    Gui, Submit, NoHide
    desc := ""
    
    ; 根據 CheckBox 決定是否加入標題
    if(LTitle) {
        desc := "L-spine:`r`r"
    }
    
    desc .= "Degenerative disc disease with _ disc space narrowing.`r"
    desc .= "Loss lordosis of spine.`r"
    desc .= "Spondylosis of spine.`r"
    gosub SpineOutput 
return

; C-spine 預設組套
CspineDefault:
    ; 先取得 CheckBox 的值
    Gui, Submit, NoHide
    
    
    ; 根據 CheckBox 決定是否加入標題
    if(LTitle) {
        desc := "C-spine:`r`r"
    }
    
    desc .= "Degenerative disc disease with _ disc space narrowing.`r"
    desc .= "Loss lordosis of spine.`r"
    desc .= "Spondylosis of spine.`r"
    desc .= "`r*Below C_ couldn't be evaluated at lateral view.`r"
    desc .= "The atlantoaxial distance is within normal limit.`r"
    desc .= "No widening of retropharngeal and retrotracheal space.`r"
	gosub SpineOutput     
return


; 術後組套按鈕
PostOP:
    desc .= "Status post _ vertebroplasty.`r"
    desc .= "Status post transpedicular screws fixation at _.`r"
    desc .= "Status post interbody cage fixation between _.`r"
	if (SpineLoc1) {
		desc .= "Status post anterior cervical corpectomy between _.`r"
	}
	gosub SpineOutput 
return

; 骨密低按鈕
BoneDensity1:
    desc := "Generalized diminished bone density.`r"
    gosub SpineOutput 
return

; 骨質疏鬆按鈕
BoneDensity2:
    desc := "Osteoporotic change of visible bony structures.`r"
    gosub SpineOutput 
return


; Hypermobility 按鈕
Hypermobility:
    desc := "Mild _ hypermobility, angle change about _ degree.`r"
    gosub SpineOutput 
return

; NoHypermobility 按鈕
NoHypermobility:
    desc := "No obvious hypermobility.`r"
    gosub SpineOutput 
return

; === 保留原有的功能按鈕 ===

C1C2OA:
    desc := "C1-C2 osteoarthritis.`r"
    gosub SpineOutput 
return

FacetArthrosis:
; 根據 Radio Button 選擇改變輸出內容
    if (SpineLoc1) {
        ; 選擇了 C-spine
        desc := "Facet joint arthrosis of cervical spine.`r"
    } else if (SpineLoc2) {
        ; 選擇了 L-spine
        desc := "Facet joint arthrosis of lumbar spine.`r"
    } else {
        ; 兩者皆未選 (保持原本行為，讓使用者自己選)
        desc := "Facet joint arthrosis of _cervical _lumbar spine.`r"
    }
	gosub SpineOutput 
return

UncovertebralJoint:
    desc := "Uncovertebral joint hypertrophy of cervical spine.`r"
	gosub SpineOutput 
return

UFJoint:
    desc := "Uncovertebral joint hypertrophy and facet joint arthrosis of cervical spine.`r"
    gosub SpineOutput 
return

Spondylolisthesis:
    desc := "Grade _I spondylolisthesis of _.`r"
    gosub SpineOutput 
return

Retrolisthesis:
    desc := "Mild retrolisthesis of _.`r"
    gosub SpineOutput 
return

; 複製舊報告（從 Spine2 視窗呼叫）
CopyOldFromSpine:
    if(LTitle) {
		if (SpineLoc1) {   ; 選擇了 C-spine
			desc := "C-spine:`r`r"
		} else if (SpineLoc2) { 	; 選擇了 L-spine
			desc := "L-spine:`r`r"
		}
		CopyCXRtoHISWithParam(0)
    }
    dicom := GetDICOMData()
    accessionNum := GetAccessionNumber(dicom)
    dateInfo := GetDICOMDateOnly(dicom)	
    
    ; 先輸出比較日期
    desc := "Comparison with previous study: " . dateInfo.full . ". _`r"
    CopyCXRtoHISWithParam(0)
    
    ; 取得舊報告內容
    desc := GetOldReportContent(accessionNum, false) 
    desc := RegExReplace(desc, "(\r\n|\n|\r)", "`n")
    CopyCXRtoHISWithParam(1)
    
    Sleep, 100
    WinActivate, Spine phases  ; Focus 回 Spine2
return

; 開啟裂孔網頁
OpenForamenWeb:
    ; 取得腳本所在目錄
    SplitPath, A_ScriptFullPath,, scriptDir
    foramenPath := scriptDir . "\spinal-foramen.html"
    Run, msedge.exe "%foramenPath%"
return

SpineClear:
    ; 清除目前的文字內容
    desc := ""
return

; 合併多行檢查項目為單行
MergeExams:
    ; 從 HIS 取得現有報告內容
    currentReport := ""
    if (!CopyReportHIS(currentReport)) {
        MsgBox, 48, 錯誤, 無法取得報告內容
        return
    }
    
    ; 處理報告內容
    mergedReport := ""
    examItems := []
    otherContent := ""
    
    ; 分析每一行
    Loop, Parse, currentReport, `n, `r
    {
        trimmedLine := Trim(A_LoopField)
        
        ; 跳過空行，但保留在其他內容中
        if (trimmedLine = "") {
            if (otherContent != "")
                otherContent .= "`r`n"
            continue
        }
        
        ; 檢查是否為檢查項目行（包含冒號且不是以空格開頭）
        if (InStr(trimmedLine, ":") > 0 && SubStr(trimmedLine, 1, 1) != " " && SubStr(trimmedLine, 1, 1) != "-") {
            ; 移除行尾的冒號
            item := RTrim(trimmedLine, ":")
            examItems.Push(item)
        } else {
            ; 非檢查項目行，加入其他內容
            if (otherContent != "")
                otherContent .= "`r`n"
            otherContent .= A_LoopField
        }
    }
    
    ; 如果有找到檢查項目，合併它們
    if (examItems.Length() > 0) {
        mergedLine := ""
        for index, item in examItems {
            if (index > 1)
                mergedLine .= ", "
            mergedLine .= item
        }
        mergedLine .= ":`r"
        
        ; 組合最終報告：合併的檢查項目 + 其他內容
        if (otherContent != "")
            mergedReport := mergedLine . "`r`n" . otherContent
        else
            mergedReport := mergedLine
    } else {
        ; 沒有找到檢查項目，保持原樣
        mergedReport := currentReport
    }
    
    ; 將修改後的內容寫回 HIS
    SetReportHIS(mergedReport)
    
    ; 顯示完成訊息
    TrayTip, 完成, 檢查項目已合併為單行, 2
return

SpineClose:
    Gui, Destroy
    goto WinCXR
return


:O:sinus;::
(
- The sinuses are essentially clear.
- The calvarium is intact.  
- There is normal sella turcica.  
- The facial bone is unremarkable.

Mild clouding of _ sinus_es, could be sinusitis, bony overlapping or others.
Air-fluid levels in _ sinuses, could be sinusitis or others.
Mild enlarged bilateral _inferior nasal turbinates.
)

:O:sin;::
HotstringMenuV("A","MenuShortcut","Mild clouding of _ sinus_es, could be sinusitis, bony overlapping or others.","Air-fluid levels in _ sinuses, could be sinusitis or others.","Mild enlarged bilateral _inferior nasal turbinates.")
return


:O:skull;::
(
Skull AP and lateral views:

- The calvarium is intact.
- There is normal sella turcica.
- The facial bone is unremarkable.
- The sinuses are essentially clear.
)


:O:pano;::
(
- No significant bony fracture or dislocation.
- Bilateral TMJs are intact.
mixed dentition
Periapical lucency, could be periodontitis or others.
Mild TMJ anterior subluxation.
Multiple teeth loss.
Mild clouding of bilateral maxillary sinuses, could be sinusitis, bony overlapping or others.

Suggest clinical correlation and follow up.

)



:O:neck;::
(
_AP and lateral views of neck show:

- Prevertebral space is not widened.
- Normal epiglottis.
- The soft tissue is unremarkable.
- The spinal alignment is normal.
- The disc spaces are preserved.
- No evidence of radiopaque foreign body.
)

:O:wrist;::
    gosub GetSideSelection

    ; 2. (選用) 檢查使用者是否按了取消(X)，如果變數是空的就終止
    if (tSideCap = ""){
        tSideCap := "_"
		tSideLow := "_"
	}

    ; 3. 貼上內容 (使用設定好的變數)
    SendInput,
(
%tSideCap% wrist:

_Healing _complex _comminuted _intra-articular fracture of _distal radius _extending to _radiocarpal compartment _and DRUJ _with mild articular step-off, _status post butress plate fixation, _without _with bone union, _with callus formation
 _with ulnar impaction syndrome. 
_Positive _Negative ulnar variance.  
_Avulsion fracture of tip of the ulnar styloid process _without bone union. 
_Osteoarthrosis of basal joint.
)
return

:O:nono;::
SendInput No active lung lesion is noted.`r
SendInput Normal heart size.`r
SendInput _Unremarkable bony structure.`r
return

:O:kub2::
(
- No obvious abnormal radiopaque density can be depicted.
- Bilateral renal and psoas muscle shadows are unremarkable.
- Unremarkable bowel gas pattern.
- _Pelvic phleboliths.
- Unremarkable bony structure.
)
:O:kub3::
(
- No obvious abnormal radiopaque density can be depicted.
- Bilateral renal and psoas muscle shadows are unremarkable.
- Unremarkable bowel gas pattern.
- _Pelvic phleboliths.
- Degenerative change and spur formation of spine.
- Generalized diminished bone density. 
)

:O:shou;::
(
Degenerative joint disease of acromio-clavicular joint.
Generalized diminished bone density. 
Lateral downsloping of acromion, predisposing to subacromial impingement.
Humeral ROM acceptable.
)

:O:knee;::
subknee1:
  SendInput,
(
Joint space narrowing in favor of osteoarthritis with or without meniscal tear. Kellgren and Lawrence grade _.(1-4)
_Degenerative joint disease of patellofemoral joint.
No patellar malalignment.
_Mild lateral tilting of patella.
_Mild suprapatellar effusion.
)
return

:O:knee2;::
SendInput Genu varum._valgus.`rGeneralized diminished bone density.`r_Atherosclerosis of arteries.`r`rRight`r
MsgBox, 4,, "簡化版? 完整版?(press Yes or No)"
IfMsgBox, No
{
	gosub subknee1
	SendInput `r`rLeft`r
	gosub subknee1
	return
}

gosub subknee2
SendInput `r`rLeft`r
gosub subknee2
return

:O:knee3;::
subknee2:
  SendInput,
(
Joint space narrowing in favor of osteoarthritis with or without meniscal tear. Kellgren and Lawrence grade _.(1-4)
No patellar malalignment.
)
return

:O:mdeg::Mild degenerative change of spine.
:O:deg::Degenerative change and spur formation of spine.
:O:dego::Degenerative and osteoporotic change of spine.`

:O:spine;::
HotstringMenuV("A","MenuShortcut2","Cspine|AP and lateral views of C-spine show:`r_Below C_ couldn't be evaluated.`rThe atlantoaxial distance is within normal limit.`rNo widening of retropharngeal and retrotracheal space.","Lspine|AP and lateral views of L-spine show:","T/L|AP and lateral views of T/L-spine show:","L/S|AP and lateral views of L/S-spine show:","BRK","4 views of C-spine:","Flexion and Extension views of C-spine:`r_Below C_ couldn't be evaluated.`rThe atlantoaxial distance is within normal limit.`rNo widening of retropharngeal and retrotracheal space.`rNo obvious hypermobility.", "Flexion and Extension views of L-spine:`rNo obvious hypermobility.")
SendInput `rNo definite bony fracture.`rNo joint subluxation or dislocation.`r
SendInput Normal alignment.`rNormal disc spaces.`r
SendInput ___Uncovertebral joint hypertrophy and facet joint arthrosis of ___lower cervical __lumbar spine.
return	


::sco;::
HotstringMenuV("A","MenuShortcut2","Mild scoliosis.","Mild scoliosis, convex to _{LtRt}","_Mild _scoliosis of thoracolumbar spine, with major and compensatory curvature.","BRK","Mild rotatory asymmetry of the _upper _thoracic _lumbar spine, convex to {LtRt}, measuring _ degree.","_Mild _scoliosis of the _upper _thoracic _thoracolumbar _lumbar spine, _, apex at _, convex to {LtRt}, measuring _ degree.")
return

:O:cxr;::
HotstringMenuV("A","MenuShortcut2","Mild infiltration in {LungSel} , could be pneumonia, or others.", "Consolidation in {LungSel}_, could be pneumonia or others.", "Focal atelectasis in {LungSel} .", "BRK","Emphysematous change or hyperaerated appearance of both lungs. ","Pulmonary congestion pattern _or emphysematous change of both lungs.","Emphysematous change of both lungs.","BRK","Patchy consolidations in {LungSel} , could be pneumonia or others.`r  Occult entities growth can not be excluded.","Mild increased hazy bronchovascular marking over bilateral lung.`r DDx: inflammatory process or others.", "Reticulations/Infiltrations in both lungs, could be related to emphysema, interstitial lung disease, pulmonary edema or others.", "BRK", "Fibrocalcified change in both upper lungs, more prominent at {LtRt} side. Suspect old infection/inflammatory changes, eg. old TB or others.","Fibrocalcified change in both upper lungs, suspect old infection/inflammatory changes, eg. old TB or others.", "Bilateral apical pleural thickening.","Mild pulmonary congestion pattern.","BRK","Suspect chronic inflammatory/ infection changes or others.","{LtRt} pleural effusion or pleural changes.","minimal pleural effusion or pleural cahnges.") 
return


::pelvis;::
(
Degenerative change and spur formation of spine. 
Generalized diminished bone density. 

The S-I and hip joints are well preserved.
Fracture or dislocation is not seen.
)

;============================================================================================
; Knee Assistant GUI (Designed for Gemini 3 Pro Context)
; Knee Assistant V2 (Designed for Hanging Protocol: Rt on Screen Left)
;============================================================================================

::kneeui::
    Gui, Knee:Font, s11, Microsoft JhengHei
    
    ; ==============================================================================
    ; OA Grade 選擇區
    ; ==============================================================================
    Gui, Knee:Add, GroupBox, x10 y10 w320 h70, OA Grade (Kellgren && Lawrence)
    Gui, Knee:Add, Radio, x20 y35 w70 h30 vGradeK1, II
    Gui, Knee:Add, Radio, x95 y35 w70 h30 vGradeK2 Checked1, II-III
    Gui, Knee:Add, Radio, x170 y35 w70 h30 vGradeK3, III
    Gui, Knee:Add, Radio, x245 y35 w70 h30 vGradeK4, IV

    ; ==============================================================================
    ; 輸出 OA 按鈕
    ; ==============================================================================
    Gui, Knee:Add, Button, x10 y90 w320 h40 gBtnGenerateOA Default, 輸出 OA 描述 (&1)

    ; ==============================================================================
    ; 其他發現按鈕
    ; ==============================================================================
    Gui, Knee:Add, GroupBox, x10 y140 w320 h250, 其他發現
    
    ; Row 1
    Gui, Knee:Add, Button, x20 y165 w145 h35 gBtnNormal, 正常 (&N)
    Gui, Knee:Add, Button, x175 y165 w145 h35 gBtnEffusion, 積液 (&E)

    ; Row 2
    Gui, Knee:Add, Button, x20 y205 w145 h35 gBtnOsteoporosis, 骨質疏鬆 (&O)
    Gui, Knee:Add, Button, x175 y205 w145 h35 gBtnPatellaTilt, 髕骨傾斜 (&P)

    ; Row 3
    Gui, Knee:Add, Button, x20 y245 w145 h35 gBtnSwelling, 軟組織腫脹 (&S)
    Gui, Knee:Add, Button, x175 y245 w145 h35 gBtnVarum, 膝內翻 (&V)

    ; Row 4
    Gui, Knee:Add, Button, x20 y285 w145 h35 gBtnEnthesopathy, 肌腱鈣化
    Gui, Knee:Add, Button, x175 y285 w145 h35 gBtnChondro, 軟骨鈣化 CPPD

    ; Row 5
    Gui, Knee:Add, Button, x20 y325 w145 h35 gBtnTKA, TKA (&T)
    Gui, Knee:Add, Button, x175 y325 w145 h35 gBtnSide, Right / Left (&R)

    ; 關閉按鈕
    Gui, Knee:Add, Button, x230 y400 w100 h35 gKneeClose, 關閉 (&Q)

    Gui, Knee:Show, w340 h445, Knee OA
return

; ==============================================================================
; 邏輯處理區
; ==============================================================================

; --- 核心功能：生成 OA 報告 (不含左右邊) ---
BtnGenerateOA:
    Gui, Knee:Submit, NoHide
    desc := ""
    
    ; 根據 Radio 按鈕決定 Grade
    if (GradeK1)
        K_Roman := "II"
    else if (GradeK2)
        K_Roman := "II-III"
    else if (GradeK3)
        K_Roman := "III"
    else if (GradeK4)
        K_Roman := "IV"
    else
        K_Roman := "II-III"
    
    desc := "OA in _ knee. Kellgren & Lawrence system, grade " . K_Roman . ". _Osteophyte formation of patellofemoral joint."
    CopyCXRtoHISWithParam(1)
return

; --- 其他發現按鈕 ---

BtnEffusion:
    desc := "Mild joint effusion."
    CopyCXRtoHISWithParam(1)
return

BtnNormal:
    desc := "No obvious evidence of displaced bony fracture. No obvious joint dislocation. No obvious patellar tilt."
    CopyCXRtoHISWithParam(1)
return

BtnOsteoporosis:
    desc := "Disuse osteoporosis."
    CopyCXRtoHISWithParam(1)
return

BtnPatellaTilt:
    desc := "Mild tilting of patella."
    CopyCXRtoHISWithParam(1)
return

BtnSwelling:
    desc := "Soft tissue swelling."
    CopyCXRtoHISWithParam(1)
return

BtnVarum:
    desc := "Genu varum._valgus."
    CopyCXRtoHISWithParam(1)
return

BtnEnthesopathy:
    desc := "Enthesopathy of quadricep tendon."
    CopyCXRtoHISWithParam(1)
return

BtnChondro:
    desc := "_ meniscal chondrocalcinosis."
    CopyCXRtoHISWithParam(1)
return

BtnTKA:
    desc := "Status post total knee arthroplasty. Without obvious loosening."
    CopyCXRtoHISWithParam(1)
return

BtnSide:
    desc := "Right`r_`r`rLeft`r_"
    CopyCXRtoHISWithParam(1)
return

KneeClose:
    Gui, Knee:Destroy
return
