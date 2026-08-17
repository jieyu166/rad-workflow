;============================================================================================
; X-ray
;============================================================================================

; -------------------------------------------------------------------------------------------
; MSK
; -------------------------------------------------------------------------------------------

::limb::The length of lower extremities measures _ cm on the right side, and _ cm on the left side.


:O:os::
HotstringMenuV("A","MenuShortcut", "os triangulare","BRK","os trigonum","os subfibulare","os peroneum","Osgood-Schlatter disease","os")
return


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
HotstringMenuV("A","MenuShortcut2"
    ,"Cspine|AP and lateral views of C-spine show:`r_Below C_ couldn't be evaluated.`rThe atlantoaxial distance is within normal limit.`rNo widening of retropharyngeal and retrotracheal space."
    ,"Lspine|AP and lateral views of L-spine show:"
    ,"T/L|AP and lateral views of T/L-spine show:"
    ,"L/S|AP and lateral views of L/S-spine show:"
    ,"BRK"
    ,"4 views of C-spine:"
    ,"Flexion and Extension views of C-spine:`r_Below C_ couldn't be evaluated.`rThe atlantoaxial distance is within normal limit.`rNo widening of retropharyngeal and retrotracheal space.`rNo obvious hypermobility."
    ,"Flexion and Extension views of L-spine:`rNo obvious hypermobility.")
SendInput `rNo definite bony fracture.`rNo joint subluxation or dislocation.`r
SendInput Normal alignment.`rNormal disc spaces.`r
SendInput ___Uncovertebral joint hypertrophy and facet joint arthrosis of ___lower cervical __lumbar spine.
return	


:O:sco;::
HotstringMenuV("A","MenuShortcut2"
    ,"Mild scoliosis."
    ,"Mild scoliosis, convex to _{LtRt}"
    ,"_Mild _scoliosis of thoracolumbar spine, with major and compensatory curvature."
    ,"BRK"
    ,"Mild rotatory asymmetry of the _upper _thoracic _lumbar spine, convex to {LtRt}, measuring _ degree."
    ,"_Mild _scoliosis of the _upper _thoracic _thoracolumbar _lumbar spine, _, apex at _, convex to {LtRt}, measuring _ degree.")
return


:O:pelvis;::
(
Degenerative change and spur formation of spine. 
Generalized diminished bone density. 

The S-I and hip joints are well preserved.
Fracture or dislocation is not seen.
)


:O:ba;::The bone age of left hand and wrist is between _ years _ months and _ years _ months. 
:O:nb;::
(
No definite bony fracture.
No joint dislocation or subluxation.
)



:*:fing::
Input, key, L1 T2
if (key == "a" or key == "1" )
    SendInput, thumb
else if (key == "b" or key == "2" )
    SendInput, index finger
else if (key == "c" or key == "3" )
    SendInput, middle finger
else if (key == "d" or key == "4" )
    SendInput, ring finger
else if (key == "e" or key == "5" )
    SendInput, little finger
else
    SendInput, fing%key%
return


:O:wou::Without union.
:O:wu::With union.

:O:pec::
HotstringMenuV("A","MenuShortcut", "pectus excavatum ", "pectus carinatum", "_Mild pectus excavatum, Haller index _.")
return

:O:ankle;::Plantar calcaneal spur.`rAchilles tendon insertional enthesophyte.
:O:cast;::Status post splint/cast fixation causing difficult evaluation of subtle lesions.

:O:acc;::
HotstringMenuV("A","MenuShortcut", "Accessory navicular"
  , "An accessory spleen, _cm.(Srs/Img:_/_)","An accessory spleen.(Srs/Img:_/_)"
  , "Accessory spleens.(Srs/Img:_/_)")
return


; -------------------------------------------------------------------------------------------
; Sinus, face, neck
; -------------------------------------------------------------------------------------------

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
HotstringMenuV("A","MenuShortcut"
  , "Mild clouding of _ sinus_es, could be sinusitis, bony overlapping or others."
  , "Air-fluid levels in _ sinus_es, could be sinusitis or others."
  , "Mild enlarged bilateral _inferior nasal turbinates."
  , "Sphenoid sinus pneumatization")
return


:O:skull;::
(
Skull AP and lateral views:

- The calvarium is intact.
- There is normal sella turcica.
- The facial bone is unremarkable.
- The sinuses are essentially clear.
)


:O:water2::
(
Mild enlarged bilateral inferior nasal turbinates
Mild clouding of _ sinus_es, could be sinusitis, bony overlapping or others.

The facial bone is unremarkable. 
)

:O:water1::
(
Mild enlarged bilateral _inferior nasal turbinates.

The facial bone is unremarkable. 
Bilateral paranasal sinuses are clear.
)


:O:pano;::
(
- No significant bony fracture or dislocation.
- Bilateral TMJs are intact.
Mild TMJ anterior subluxation.
Mixed dentition
Periapical lucency, could be periodontitis or others.
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


:O:nono;::
SendInput No active lung lesion is noted.`r
SendInput Normal heart size.`r
SendInput _Unremarkable bony structure.`r
return


:O:kub;::
HotstringMenuV("A","MenuShortcut"
    ,"Mild sclerotic change around bilateral SI joints, could be related to arthritis or others."
    ,"Gallstone or right renal stone or other."
    ,"Suspect right renal stones"
    ,"BRK"
    ,"Mild both hips osteoarthritis (OA)")
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



:O:cxr;::
HotstringMenuV("A","MenuShortcut2"
    ,"Mild infiltration in {LungSel}_, could be pneumonia, _or others."
    ,"Consolidation in {LungSel}_, could be pneumonia, _or others."
    ,"Focal atelectasis in {LungSel} ."
    ,"BRK"
    ,"Emphysematous change or hyperaerated appearance of both lungs. "
    ,"Pulmonary congestion pattern _or emphysematous change of both lungs."
    ,"Mild increased hazy bronchovascular marking over bilateral lung.`r  DDx: _edema, inflammatory process or others."
    ,"Patchy consolidations in {LungSel} , could be pneumonia or others.`r  Occult entities growth can not be excluded."
    ,"Suspect chronic inflammatory/ infection changes or others in both lungs."
    ,"Reticulations/Infiltrations in both lungs, could be related to emphysema, interstitial lung disease, pulmonary edema or others."
    ,"BRK"
    ,"Fibrocalcified change in both upper lungs, more prominent at {LtRt} side. Suspect old infection/inflammatory changes, eg. old TB or others."
    ,"Fibrocalcified change in both upper lungs, suspect old infection/inflammatory changes, eg. old TB or others."
    ,"Bilateral apical pleural thickening."
    ,"Mild pulmonary congestion pattern."
    ,"Emphysematous change of both lungs."
    ,"BRK"
    ,"{LtRt} pleural effusion or pleural changes."
    ,"minimal pleural effusion or pleural changes.")
return

:O:cxra;::
HotstringMenuMulti("A","MenuShortcut"
    ,"Normal heart size."
    ,"Borderline cardiomegaly."
    ,"Cardiomegaly."
    ,"BRK"
    ,"Intimal calcification of aorta."
    ,"Tortuous aorta with intimal calcification."
    ,"Mild mediastinal widening."
    ,"Mediastinum widening."
    ,"BRK"
    ,"Bilateral hilar fullness, could be vascular shadows or others."
    ,"Bilateral hilar fullness, could be vessels but lymphadenopathy or other lesions can not be excluded."
    ,"BRK"
    ,"Emphysematous change of both lungs."
    ,"Pulmonary congestion pattern or emphysematous change of both lungs."
	,"Mild infiltration in both lungs, could be pneumonia, _or others."
    ,"Mild increased hazy bronchovascular marking over bilateral lung.`r  DDx: inflammatory process or others."
    ,"Superimposed pneumonia or other occult entities can not be excluded."
    ,"Occult entities can not be excluded.")
return

:O:cxrb;::
HotstringMenuMulti("A","MenuShortcut"
    ,"Degenerative change and spur formation of spine"
    ,"Degenerative and osteoporotic change of spine"
    ,"Suspect osteopenia"
    ,"Suspect osteoporosis"
    ,"Mild scoliosis"
    ,"BRK"
    ,"{LtRt} ribs old fracture"
    ,"Suspect _ rib old fracture"
    ,"{LtRt} clavicular old fracture"
    ,"Suspect _ clavicular old fracture"
	,"Fracture of _"
    ,"BRK"
    ,"T_ compression fracture" ,"L_ compression fracture"
    ,"Mild T_ collapse" ,"Mild L_ collapse"
    ,"Multiple vertebral compression fracture","Multiple vertebral collapse")
return

:O:cxrc;::
HotstringMenuMulti("A","MenuShortcut"
    ,"Emphysematous change of both lungs."
    ,"Emphysematous change or hyperaerated appearance of both lungs."
    ,"Pulmonary congestion pattern or emphysematous change of both lungs."
    ,"Mild increased hazy bronchovascular marking over bilateral lung.`r  DDx: inflammatory process or others."
    ,"BRK"
    ,"Mild infiltration in {LungSel}, could be pneumonia, or others."
    ,"Mild infiltration in bilateral lower lungs, could be pneumonia, or others."
    ,"Mild infiltration in bilateral lungs, could be pneumonia, edema or others."
    ,"Patchy consolidations in bilateral lungs, could be pneumonia or others.`r  Occult entities growth can not be excluded." 
    ,"Superimposed pneumonia or other occult entities can not be excluded."
    ,"BRK"
    ,"Focal atelectasis in bilateral lower lung ."
    ,"{LungSel} focal atelectasis."
    ,"Insufficient inspiration and focal atelectasis of both lungs."
    ,"BRK"
    ,"Fibrocalcified change in both upper lungs, suspect old infection/inflammatory changes, eg. old TB or others."
    ,"Bilateral apical pleural thickening."
    ,"Chronic/post infection/inflammatory changes or others in both lungs."
    ,"BRK"
    ,"Bilateral minimal pleural effusion or pleural changes."
    ,"{LtRt} minimal pleural effusion or pleural changes.")
return

;============================================================================================
; CXR, spine, knee UI 程式
;============================================================================================

:O:cxr2;::
WinCXR:
WinGet, ActiveId, ID, A ;記錄目前視窗
; 重置每次開啟時的緩衝（仿 spine2：先暫存，按「一次輸出全部」才合併貼出）
CXRBuffer := []
desc := ""
Gui, Font, s14
Gui Add, Text, x10 y-25, " " ;定位用

; === 肺部發現按鈕 (最上方) ===
Gui Add, Button, x10 y10 w140 h35 gBtnApicalPleural, Apical pleural(&A)
Gui Add, Button, x160 yp w140 h35 gBtnEmphysema, Emphysema(&E)
Gui Add, Button, x310 yp w140 h35 gBtnHilarFullness, Hilar fullness(&H)
Gui Add, Button, x10 yp+40 w140 h35 gBtnMediastinal, Mediastinal(&M)
Gui Add, Button, x160 yp w140 h35 gBtnEff, 積液(&W)
Gui Add, Button, x310 yp w140 h35 gBtnCongestion, Congestion(&R)
Gui Add, Button, x10 yp+40 w140 h35 gCXR8, 吸氣不足(&I)
Gui Add, Button, x160 yp w140 h35 gCXR11, Edema通殺(&4)

; === 分隔線 ===
Gui Add, Text, x10 yp+40 w440 h2 0x10

; === CheckBox 和 Radio ===
Gui Add, CheckBox, x10 yp+5 w200 h23 vL1 checked1, &No active lung lesions
Gui Add, CheckBox, x220 yp w130 h23 vC1, 比較舊片
Gui Add, Radio, x10 yp+30 w140 h23 vL3, Cardiomegaly(&C)
Gui Add, Radio, xp+150 yp w140 h23 vL5, 邊緣擴大(&B)
Gui Add, Radio, xp+150 yp w100 h23 vL7 checked1, 心臟正常

; === 範本按鈕區 ===
Gui Add, Button, x10 yp+30 w140 h45 gCXR1, 正常(&N)
Gui Add, Button, x160 yp w140 h45 gCXR3, 硬化+輕退化
Gui Add, Button, x310 yp w140 h45 gCXR4, 硬化+骨密低(&D)
Gui Add, Button, xp yp+50 w140 h45 gCXR5, 硬化+骨鬆(&F)

Gui Add, Button, x10 yp+5 w140 h45 gCXR6, 洗腎(&J)
Gui Add, Button, x160 yp w140 h45 gCXR10, 心臟手術術後(&L)
Gui Add, Button, x10 yp+50 w140 h45 gCXR7, 小孩(&K)

; === 分隔線 ===
Gui Add, Text, x10 yp+50 w440 h2 0x10
Gui Add, Button, x10 yp+5 w120 h30 gMergeExams, 合併標題(&Z)
Gui Add, Button, x140 yp w120 h30 gCXRClean, 清除選項(&Q)
Gui Add, Button, x270 yp w120 h30 gCXRclose, 切換&Spine
Gui Add, Button, x10 yp+40 w120 h30 gSeeCXRAI, 看AI報告(&1)
Gui Add, Button, x140 yp w120 h30 gCopyOld2, 顯示舊報告(&2)
Gui Add, Button, x270 yp w120 h30 gCopyOldSmart, 複製舊報告(&3)

; === 緩衝輸出區（仿 spine2）===
Gui Add, Text, x10 yp+42 w120 h32 +0x200 vCXRStatus, 已選 0 項
Gui Add, Button, x140 yp w250 h34 Default gFlushCXRBuffer, 一次輸出全部(&G)

Gui Show, w460 h500, CXR 範例
Return

; ============================================
; CXR 緩衝機制（仿 spine2）：每個發現按鈕先暫存，按「一次輸出全部」才合併貼到 HIS
; ============================================
; 將目前 desc 推入 CXRBuffer（依點擊順序），不立即貼上
CXROutput:
    if (desc != "")
        CXRBuffer.Push(desc)
    desc := ""
    GuiControl, , CXRStatus, % "已選 " . CXRBuffer.Length() . " 項"
return

; 異常發現按鈕專用：先取消「No active lung lesion」勾選（有發現即非 clear），再暫存
CXRFindingOutput:
    GuiControl, , L1, 0
    gosub CXROutput
return

; 依點擊順序一次合併貼到 HIS
FlushCXRBuffer:
    if (!IsObject(CXRBuffer) || CXRBuffer.Length() = 0) {
        MsgBox, 48, , 緩衝為空，請先選擇任一發現項目。
        return
    }
    desc := ""
    for _, item in CXRBuffer
        desc .= item
    CXRBuffer := []
    GuiControl, , CXRStatus, % "已選 0 項"
    ; 輸出後重設 GUI（resetCXR=true → Gosub CXRClean：重勾 No active lung lesion + 心臟正常）
    OutputFinish(2, "CXR 範例", false, true, false)
return

; CXR 共用報告函式
; pL2: 0=無硬化, 1=有硬化
; pL3: 0=無骨鬆, 1=骨密低(osteopenia), 2=骨鬆(osteoporosis)
CXRCommon(pL2 := 0, pL3 := 0) {
    global desc, L1, L3, L5, L7, C1
    Gui, 1:Default          ; <-- 加這行確保操作正確的 GUI
    Gui, Submit, NoHide
    If(C1){
        Gosub, calldate
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

    If(pL2){
        desc .= "Intimal calcification of aorta.`r"
        If(pL3){
            desc .= "Degenerative change and spur formation of spine. "
            If(pL3=1){
                desc .= "Suspect osteopenia.`r"
            }else if(pL3=2){
                desc .= "Suspect osteoporosis.`r"
            }
        } else{
            desc .= "Mild degenerative change of spine.`r"
        }
    }else{
        desc .= "Unremarkable bony structure.`r"
    }
}

CXR1:
CXRCommon(0, 0)
gosub CXROutput
gosub FlushCXRBuffer
return

CXR3:
CXRCommon(1, 0)
gosub CXROutput
gosub FlushCXRBuffer
return


CXR4:
CXRCommon(1, 1)
gosub CXROutput
gosub FlushCXRBuffer
return

CXR5:
CXRCommon(1, 2)
gosub CXROutput
gosub FlushCXRBuffer
return

CXR6:
GuiControl,, L1, 0
GuiControl,, L5, 1
CXRCommon(1, 1)
desc .= "Mild mediastinal widening.`r"
desc .= "Status post permcath catheter insertion at _right_left _chest.`r"
gosub CXROutput
return


CXRClean:
GuiControl,, C1, 0
GuiControl,, L1, 1
GuiControl,, L3, 0
GuiControl,, L5, 0
GuiControl,, L7, 1
desc := ""
CXRBuffer := []
GuiControl, , CXRStatus, % "已選 0 項"
GuiControl,, OldReportContent, %desc% ; 清空 Edit 內容
return


; ============================================
; 肺部發現按鈕 (單獨輸出文字，類似 spine2)
; ============================================
CXR7:
desc .= "Mild increased lung markings in bilateral perihilar region.`r"
desc .= "No cardiomegaly.`r"
desc .= "The bony structure is unremarkable.`r"
gosub CXRFindingOutput
return

CXR8:
desc .= "Insufficient inspiration _and focal atelectasis of both lungs.`r"
gosub CXRFindingOutput
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
gosub CXRFindingOutput
return

CXR11:
desc .= "Pulmonary congestion pattern or emphysematous change of both lungs.`r"
desc .= "Superimposed pneumonia or other occult entities can not be excluded.`r"
desc .= "_Bilateral minimal pleural effusion or pleural changes. `r"
desc .= "Bilateral hilar fullness, could be vascular shadows or others. `r"
gosub CXRFindingOutput
return

BtnApicalPleural:
    desc := "Bilateral apical pleural thickening.`r"
    gosub CXRFindingOutput
return

BtnEmphysema:
    desc := "Emphysematous change of both lungs.`r"
    gosub CXRFindingOutput
return

BtnHilarFullness:
    desc := "Bilateral hilar fullness, could be vascular shadows or others.`r"
    gosub CXRFindingOutput
return

BtnMediastinal:
    desc := "Mild mediastinal widening.`r"
    gosub CXRFindingOutput
return

BtnCongestion:
    desc := "Mild pulmonary congestion pattern.`r"
    gosub CXRFindingOutput
return

BtnEff:
    desc := "Bilateral _minimal pleural effusion or pleural changes.`r"
    gosub CXRFindingOutput
return


CXRclose:
Gui, Destroy
goto WinSpine
return


; CopyOld2：彈出新視窗顯示舊報告
CopyOld2:
Gui, 1:Submit, NoHide

ClipboardBackup := Clipboard ; 保存當前剪貼簿內容

; 取得舊報告內容
dicom := GetDICOMData()
accessionNum := GetAccessionNumber(dicom)
dateInfo := GetDICOMDateOnly(dicom)
dateInfo := "Comparison with previous study: " . dateInfo.full . ". _`r"
oldReport := dateInfo
oldReport .= GetOldReportContent(accessionNum, false)
; 清理報告格式
oldReport := RegExReplace(oldReport, "(\r\n|\n|\r)", "`r`n")

; 恢復原始剪貼簿內容
Clipboard := ClipboardBackup

; 建立彈出視窗顯示舊報告
Gui, OldReport:Destroy
Gui, OldReport:Font, s14
Gui, OldReport:Add, Edit, x10 y10 w500 h400 vOldReportText ReadOnly Multi VScroll, %oldReport%
Gui, OldReport:Add, Button, x10 y420 w200 h40 gOldReportCopy, 複製舊報告(&1)
Gui, OldReport:Add, Button, x220 yp w200 h40 gOldReportCopyDate, 複製日期&2)
Gui, OldReport:Show, w520 h470, 舊報告
return

; 主視窗的複製舊報告按鈕（無彈出視窗時 fallback）
CopyOldSmart:
Gui, 1:Submit, NoHide
gosub CopyOld
return

; 彈出視窗的複製舊報告按鈕
OldReportCopy:
Gui, OldReport:Submit, NoHide
if (OldReportText != "") {
    desc := OldReportText
    desc := RegExReplace(desc, "(\r\n|\n|\r)", "`n")
    Gui, OldReport:Destroy
    CopyCXRtoHISWithParam(2)
} else {
    Gui, OldReport:Destroy
    gosub CopyOld
}
return

OldReportCopyDate:
Gui, OldReport:Submit, NoHide
if (dateInfo != "") {
    desc := dateInfo
    desc := RegExReplace(desc, "(\r\n|\n|\r)", "`n")
    Gui, OldReport:Destroy
    CopyCXRtoHISWithParam(0)
} else {
    Gui, OldReport:Destroy
    gosub CopyOld
}
return


OldReportGuiClose:
OldReportGUIEscape:
Gui, OldReport:Destroy
return

CXRFinish:
   OutputFinish(2, "CXR 範例", false, true, false)
return

; 統一輸出函式（CXR2 / spine2 共用收尾）
; outputMode: 1=只換行, 2=完整移動 呼叫 CopyCXRtoHISWithParam 的參數
; windowName: 視窗名稱 ("CXR 範例" 或 "Spine phases")
; applyDash : 保留以維持呼叫端相容；目前所有呼叫端皆傳 false（項目符號已移除）
; resetCXR  : 是否呼叫 CXRClean 重置
; backWindow: 輸出後是否回原視窗
OutputFinish(outputMode := 2, windowName := "", applyDash := false, resetCXR := false, backWindow := true) {
    global desc

    ; 1. 輸出到 HIS
    CopyCXRtoHISWithParam(outputMode)

    ; 2. 重置 CXR GUI (如果需要)
    if (resetCXR) {
        Gosub, CXRClean
    }

    ; 3. 清空 desc
    desc := ""

    ; 4. 返回原視窗
    if (backWindow) {
        Sleep, 100
        WinActivate, %windowName%
    }
}


:O:spine2;::
WinSpine:
WinGet, ActiveId, ID, A ;紀錄目前視窗
; 重置每次開啟時的緩衝（buffer 為陣列，元素為 {sev: int, text: str}）
SpineBuffer := []
desc := ""
desc_sev := ""
Gui Font, s14

; 移除所有 CheckBox，改為按鈕配置

; 第一排 - 標題選項
Gui Add, CheckBox, x10 y10 w120 h23 vLTitle, 包含標題(&5)
; [新增] 部位選擇 Radio Button
; 預設不勾選，保留彈性；若選了就會固定輸出該部位
Gui Add, Radio, x140 y10 w90 h23 vSpineLoc1, C-spine(&1)
Gui Add, Radio, x240 y10 w90 h23 checked1 vSpineLoc2, L-spine(&2)

; 第二排按鈕
Gui Add, Button, x10 yp+50 w150 h50 gLspineDefault, &L-spine 預設
Gui Add, Button, xp+160 yp w150 h50 gCspineDefault, &C-spine 預設
Gui Add, Button, xp+160 yp w150 h50 gBtnInsertTitle, 輸出標題(&T)

; 第三排按鈕
Gui Add, Button, x10 yp+60 w150 h50 gBoneDensity1, 骨密低(&A)
Gui Add, Button, xp+160 yp w150 h50 gBoneDensity2, 骨質疏鬆(&D)
Gui Add, Button, xp+160 yp w150 h50 gBtnWedging, Ant. &Wedging


; 第四排按鈕 - 原有功能
Gui Add, Button, x10 yp+60 w150 h50 gSpondylolisthesis, &Spondylolisthesis
Gui Add, Button, xp+160 yp w150 h50 gRetrolisthesis, &Retrolisthesis
Gui Add, Button, xp+160 yp w150 h50 gHypermobility, &Hypermobility

; 第五排按鈕
Gui Add, Button, x10 yp+60 w150 h50 gFacetArthrosis, &Facet arthrosis
Gui Add, Button, xp+160 yp w150 h50 gUncovertebralJoint, &Uncovertebral
Gui Add, Button, xp+160 yp w150 h50 gNoHypermobility, &No hypermobility

Gui Add, Button, x10 yp+60 w150 h50 gUFJoint, Facet+Unco(&B)
Gui Add, Button, xp+160 yp w150 h50 gC1C2OA, C1-C2 OA(&6)
Gui Add, Button, xp+160 yp w150 h50 gPostOP, 術後組套(&P)

; 右側控制按鈕
Gui Add, Button, x500 y10 w120 h40 gSpineClose, 切換到 C&XR
Gui Add, Button, xp yp+50 w120 h40 gMergeExams, 合併檢查(&Z)
Gui Add, Button, xp yp+50 w120 h40 gCopyOldFromSpine, 複製舊報告(&3)
Gui Add, Button, xp yp+50 w120 h40 gOpenForamenWeb, 裂孔網頁(&O)

; 緩衝排序輸出區（永遠先收集，按 [輸出全部] 才依嚴重度排序貼出）
Gui Font, s10, Segoe UI
Gui Add, Text, x500 yp+55 w120 h18 vSpineStatus, 已選 0 項
Gui Font, s14
Gui Add, Button, x500 yp+22 w120 h44 Default gFlushSpineBuffer, 輸出全部(&G)
Gui Add, Button, xp yp+50 w120 h32 gClearSpineBuffer, 清空緩衝(&Q)

; 常用非 spine finding
Gui Add, Text, x10 y370 w470 h2 0x10
Gui Add, Button, x10 y385 w150 h50 gBowelGasFinding, 腸氣增加
Gui Add, Button, xp+230 yp w150 h50 gAortaCalcFinding, 動脈鈣化(&E)

Gui Show, w640 h470, Spine phases
; 記錄視窗標題，用於後續 focus 回來
WinGet, SpineWinID, ID, Spine phases
return

; 將目前的 desc + desc_sev 推入 SpineBuffer，不立即貼上
SpineOutput:
    Gui, Submit, NoHide
    if (desc_sev = "")
        desc_sev := 5  ; 未指定 severity 視為中等優先（介於結構問題與退化背景之間）
    SpineBuffer.Push({sev: desc_sev + 0, text: desc})
    desc := ""
    desc_sev := ""
    GuiControl, , SpineStatus, % "已選 " . SpineBuffer.Length() . " 項"
return

; 依 severity 排序後一次貼出（穩定排序：同 severity 維持點擊順序）
FlushSpineBuffer:
    if (!IsObject(SpineBuffer) || SpineBuffer.Length() = 0) {
        MsgBox, 48, , 緩衝為空，請先選擇任一發現項目。
        return
    }
    Gui, Submit, NoHide
    desc := ""
    Loop, 11 {
        sev := A_Index - 1   ; 0..10
        for _, item in SpineBuffer {
            if (item.sev = sev)
                desc .= item.text
        }
    }
    SpineBuffer := []
    GuiControl, , SpineStatus, % "已選 0 項"
    OutputFinish(1, "Spine phases", false, false, false)
return

; 清空緩衝但不貼出
ClearSpineBuffer:
    SpineBuffer := []
    desc := ""
    desc_sev := ""
    GuiControl, , SpineStatus, % "已選 0 項"
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
	MsgBox, 4,, (AP+Flex.+Ext.)?
	IfMsgBox, Yes
	{
		desc .= "(AP{+}Flex.{+}Ext.)"
	}
	desc .=":`r"
    CopyCXRtoHISWithParam(1)
    WinActivate, Spine phases
return

; [按鈕 2] Anterior Wedging
BtnWedging:
    desc := "_ anterior wedging.`r"
    desc_sev := 1   ; 壓迫性骨折，最高優先
    gosub SpineOutput
return

; L-spine 預設組套
LspineDefault:
    ; 先取得 CheckBox 的值
    Gui, Submit, NoHide
    desc := ""

    ; 標題需單獨進 buffer，才能永遠排在其他 findings 前面
    if(LTitle) {
        desc := "L-spine:`r"
        desc_sev := 0
        gosub SpineOutput
    }

    desc := "Degenerative disc disease with _ disc space narrowing.`r"
    desc .= "Loss of lordosis of spine.`r"
    desc .= "Spondylosis of spine.`r"
    desc_sev := 6   ; 退化背景組套
    gosub SpineOutput
return

; C-spine 預設組套
CspineDefault:
    ; 先取得 CheckBox 的值
    Gui, Submit, NoHide
    desc := ""


    ; 標題需單獨進 buffer，才能永遠排在其他 findings 前面
    if(LTitle) {
        desc := "C-spine:`r"
        desc_sev := 0
        gosub SpineOutput
    }

    desc := "Degenerative disc disease with _ disc space narrowing.`r"
    desc .= "Loss of lordosis of spine.`r"
    desc .= "Spondylosis of spine.`r"
    desc_sev := 6   ; 退化背景組套
	gosub SpineOutput

    ; C-spine lateral/soft tissue 補充段固定最後輸出
    desc := "`r*Below C_ couldn't be evaluated at lateral view.`r"
    desc .= "The atlantoaxial distance is within normal limit.`r"
    desc .= "No widening of retropharyngeal and retrotracheal space.`r"
    desc_sev := 10
    gosub SpineOutput
return


; 術後組套按鈕
PostOP:
    Gui, Submit, NoHide
    desc := ""
    desc .= "Status post _ vertebroplasty.`r"
    desc .= "Status post transpedicular screws fixation at _.`r"
    desc .= "Status post interbody cage fixation between _.`r"
	if (SpineLoc1) {
		desc .= "Status post anterior cervical corpectomy between _.`r"
	}
    desc_sev := 3   ; 術後病史，使用者指定
	gosub SpineOutput
return

; 骨密低按鈕
BoneDensity1:
    desc := "Generalized diminished bone density.`r"
    desc_sev := 4   ; 全身性骨質
    gosub SpineOutput
return

; 骨質疏鬆按鈕
BoneDensity2:
    desc := "Osteoporotic change of visible bony structures.`r"
    desc_sev := 4   ; 全身性骨質
    gosub SpineOutput
return

; 常用非 spine finding
BowelGasFinding:
    desc := "Mild increased bowel gas _or mild ileus.`r"
    desc_sev := 9
    gosub SpineOutput
return

AortaCalcFinding:
    desc := "Intimal calcification of aorta.`r"
    desc_sev := 9
    gosub SpineOutput
return


; Hypermobility 按鈕
Hypermobility:
    desc := "Mild _ hypermobility, angle change about _ degree.`r"
    desc_sev := 1   ; 使用者指定
    gosub SpineOutput
return

; NoHypermobility 按鈕
NoHypermobility:
    desc := "No obvious hypermobility.`r"
    desc_sev := 1   ; 使用者指定
    gosub SpineOutput
return

; === 保留原有的功能按鈕 ===

C1C2OA:
    desc := "C1-C2 osteoarthritis.`r"
    desc_sev := 5   ; 局部 OA
    gosub SpineOutput
return

FacetArthrosis:
; 根據 Radio Button 選擇改變輸出內容
    Gui, Submit, NoHide
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
    desc_sev := 7   ; 退化局部
	gosub SpineOutput
return

UncovertebralJoint:
    desc := "Uncovertebral joint hypertrophy of cervical spine.`r"
    desc_sev := 8   ; 退化局部
	gosub SpineOutput
return

UFJoint:
    desc := "Uncovertebral joint hypertrophy and facet joint arthrosis of cervical spine.`r"
    desc_sev := 7   ; 退化局部組合
    gosub SpineOutput
return

Spondylolisthesis:
    desc := "Grade _I spondylolisthesis of _.`r"
    desc_sev := 1   ; 結構問題（同 Retrolisthesis）
    gosub SpineOutput
return

Retrolisthesis:
    desc := "Mild retrolisthesis of _.`r"
    desc_sev := 1   ; 使用者指定
    gosub SpineOutput
return

; 複製舊報告（從 Spine2 視窗呼叫）
CopyOldFromSpine:
    Gui, Submit, NoHide
    if(LTitle) {
		if (SpineLoc1) {   ; 選擇了 C-spine
			desc := "C-spine:`r`r"
		} else if (SpineLoc2) { 	; 選擇了 L-spine
			desc := "L-spine:`r`r"
		}
		CopyCXRtoHISWithParam(2)
    }
    dicom := GetDICOMData()
    accessionNum := GetAccessionNumber(dicom)
    dateInfo := GetDICOMDateOnly(dicom)	
    
    ; 先輸出比較日期
    desc := "Comparison with previous study: " . dateInfo.full . ". _`r"
    CopyCXRtoHISWithParam(1)
    
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
    foramenPath := scriptDir . "\..\tool\spinal-foramen.html"
    Run, msedge.exe "%foramenPath%"
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
    Gui, Knee:Add, Button, x20 y165 w145 h35 gBtnEffusion, 積液 (&E)
    Gui, Knee:Add, Button, x175 y165 w145 h35 gBtnNormal, 正常 (&N)

    ; Row 2
    Gui, Knee:Add, Button, x20 y205 w145 h35 gBtnPatellaTilt, 髕骨傾斜 (&P)
    Gui, Knee:Add, Button, x175 y205 w145 h35 gBtnOsteoporosis, 骨質疏鬆 (&O)

    ; Row 3
    Gui, Knee:Add, Button, x20 y245 w145 h35 gBtnSwelling, 軟組織腫脹 (&S)
    Gui, Knee:Add, Button, x175 y245 w145 h35 gBtnVarum, 膝內翻 (&V)

    ; Row 4
    Gui, Knee:Add, Button, x20 y285 w145 h35 gBtnChondro, 軟骨鈣化 CPPD
    Gui, Knee:Add, Button, x175 y285 w145 h35 gBtnEnthesopathy, 肌腱鈣化

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
    
    desc := "Joint space narrowing in favor of osteoarthritis with or without meniscal tear. Kellgren and Lawrence grade " . K_Roman . ".(1-4)"
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
