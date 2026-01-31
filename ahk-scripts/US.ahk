;============================================================================================
; US - Ext. 
;============================================================================================
; 需要 GDI+ 庫支持，如果沒有請下載：https://github.com/tariqporter/Gdip2/
#Include Gdip.ahk  ; 如果沒有此庫，請註解此行並使用簡化版本


::usdvt::
SendInput Sonography of bilateral lower extremity shows:`r`r
SendInput V             Side         Occlusion/Patency        Compressibility`r
SendInput -------      ------        ------------------       ---------------`r`r
SendInput CFV          Bilateral            P                     C`r
SendInput Bifurcation  Bilateral            P                     C`r
SendInput FV           Bilateral            P                     C`r
SendInput Popliteal    Bilateral            P                     C`r
SendInput `r_No reflux noted in bil. GSV to suggest venous insufficiency.`r`r
SendInput No evidence of thrombosis.`r_No reflux noted in bil. GSV to suggest venous insufficiency.`r
return

::usdvt2::
SendInput Sonography of bilateral lower extremity shows:`r`r
SendInput V             Side         Occlusion/Patency        Compressibility`r
SendInput -------      ------        ------------------       ---------------`r`r
SendInput CFV            Rt                 P                     X`r
SendInput Bifurcation    Rt                 P                     C`r
SendInput FV             Rt                 P                     C`r
SendInput Popliteal      Rt                 O                     X`r`r
SendInput CFV            Lt                 P                     X`r
SendInput Bifurcation    Lt                 P                     C`r
SendInput FV             Lt                 P                     C`r
SendInput Popliteal      Lt                 O                     X`r
SendInput `r_No reflux noted in bil. GSV to suggest venous insufficiency.`r`r
SendInput No evidence of thrombosis.`r_No reflux noted in bil. GSV to suggest venous insufficiency.`r
return

::uspad::
SendInput Doppler Sonography of bilateral lower extremity arteries shows:`r`r
SendInput The Maximum velocity (Vmax) as :  [cm/s]`r`r
SendInput side         CFA          FA         POP a.       PTA         DPA`r
SendInput -----      --------     --------     --------    ---------   ---------`r
SendInput R't         _ Multi   _ M/LR   _ M/LR   _ M/LR   _ M/LR`r
SendInput L't         _ Multi   _ M/LR   _ M/LR   _ M/LR   _ M/LR`r`r
SendInput _Intimal atherosclerotic plaques in arterial wall.`r`r
SendInput Right CFA: _`rRight FA: _`rRight POP a.: _`rRight PTA: _`rRight DPA: _`r`r
SendInput Left CFA: _`rLeft FA: _`rLeft POP a.: _`rLeft PTA: _`rLeft DPA: _`r
SendInput ----------------------------------------------------------------------`r
SendInput abbr:`rCFA, Common femoral artery; FA, Femoral artery; POP a., Popliteal artery;`r
SendInput ATA, Anterior tibial artery; PTA, Posterior tibial artery; DPA, Dorsalis`r
SendInput pedis artery.`rMonophasic(M), Multi(phasic)`rHigh/Intermediate/Low Resistive(HR/IR/LR)
return

::uspad2::
SendInput Doppler Sonography of bilateral lower extremity arteries shows:`r`r
SendInput The Maximum velocity (Vmax) as :  [cm/s]`r`r
SendInput side         CFA         FA         POP a.      PTA        DPA`r
SendInput -----      --------    --------    --------  ---------   ---------`r
SendInput R't         _      _      _     _     _`r
SendInput L't         _      _      _     _     _`r`r
SendInput Monophasic(M) Biphasic(B) Triphasic(T)`r
SendInput Acceptable biphasic~triphasic waveform in arteries.`r
SendInput _Intimal atherosclerotic plaques in arterial wall.`r`r
SendInput ----------------------------------------------------------------------`r
SendInput abbr:`rCFA, Common femoral artery; SFA, Superficial femoral artery; POP a., Popliteal`r
SendInput artery; ATA, Anterior tibial artery; PTA, Posterior tibial artery; DPA, Dorsalis`rpedis artery.`r
return


::usbreast::
SendInput Breast sonography study shows:`r
;SendInput Breast composition: _`r
gosub calldate
SendInput `rLocation       (Srs/Img)  Size(mm)   Change          DDx/Note`r
SendInput --------       ------------------   ------------    -----------`r
SendInput _LRt _/_        (1/_)    __x__       _               _ `r`r              
SendInput - Glandular tissue component: _minimal mild moderate marked .`r
SendInput - Normal echogenicity of bilateral breast glandular tissue.`r
SendInput - No abnormal enlarged lymph nodes found in bilateral axillary region.`r

; Location       (Srs/Img)  Size(mm)   Change          D/D         
; --------        ------------------   ------------    --------     



MsgBox, 4,, "Would you like to continue 91 Abnormal screening MG...(press Yes or No)"
IfMsgBox, Yes
{
	SendInput ----------------------------------------------------------------------`r
	SendInput The abnormal screening MG information:`r
	SendInput Date (at other or our hospital): _`r`r
	SendInput Findings: `r( ) Focal asymmetry ( ) Mass ( ) Calcification ( ) Architectural distortion`r
	SendInput Original report showed: _`r`r
	SendInput Density of breast: _heterogeneously dense`r
	SendInput BI-RADS assessment: Category 0`r`r
}

return

:O:bn::_LRt _/_: __*__ mm.(Srs/Img:1/_) _ 
:O:usb;::
HotstringMenuV("A","MenuShortcut2","_ subareolar ductal ectasia, _mm.(Srs/Img:1/_) No echogenoc content, favor benign.")
return

:O:ub::Mild urinary bladder wall thickening, could be chronic cystitis, _shrinkaged UB, or others.
:O:ub2::Mild urinary bladder wall irregular thickening, could be cystitis, or others. Occult entities can not be excluded. Suggest correlate with urine cytology or other exams.

::usbx::
(
Ultrasound (US)-guided Core-Needle Biopsy (CNB)
Clinical information: _, requested for biopsy.
_The study is compared with prior diagnostic US.

1. Position: _Supine _Prone _lateral decubitus
2. Target lesions: _
3. Puncture site: 
4. Devices: 14G biopsy needle
5. Specimens: _ cores
6. Complications: _Mild wound oozing.

   Before procedure, explained need and risk, complications to patient.
   Under US guide, tissue specimens are smoothly taken for pathology examination.
   No immediate complications noted after procedure.
		
Impression:
Successful ultrasound guided CNB of _.

- Under sonoguidance, _2 pieces of specimens were taken from _hypoechoic lesion in
_S3 via _anterior abdominal wall approach and sent for pathological exam.

)

;============================================================================================
; US - Neck
;============================================================================================


::usneck::
SendInput Neck/Thyroid sonography shows: `r`r
SendInput 1. Thyroid: `r_Normal size and echogenicity of bilateral thyroid lobes and isthmus.`r`r
SendInput 2. Neck:`rLymph nodes with preserved fatty hila of bilateral neck, short-axis <1cm.`r`r

MsgBox, 4,, "Would you like to continue Salivary gland...(press Yes or No)"
IfMsgBox, No
	return

SendInput 3. Salivary glands:`r - unremarkable.`r`r
SendInput _tn;`r_tirads; `r
return

::usneck2::
(
Diffuse heterogeneous echotexture of thyroid parenchyma without significant hyper-vascularity, compatible with chronic thyroiditis or others. Suggest correlate with thyroid function and antibody tests.
----------------------------------------------------------------------
Thyroid sonography shows:

1. Thyroid:
- Normal size and heterogeneous echogenicity of bilateral thyroid lobes and
isthmus.

2. Neck:
- Lymph nodes with preserved fatty hila of bilateral neck, short-axis <1cm.
)

::usneck3::
(
Status post bilateral total thyroidectomy. No US evidence of local recurrence.
----------------------------------------------------------------------
Neck sonography shows:

1. Thyroid:
 - status post bilateral total thyroidectomy

2. Neck:
 - Lymph nodes with preserved fatty hila of bilateral neck, short-axis <1cm.
)


::tn::- A _solid _hypoechoic nodule in _LRt _mid. thyroid, _x_x_ mm, TR_.(Srs/Img:1/_)
::tn2::
HotstringMenuV("A","MenuShortcut", "- <1cm TR_4 nodules in _bilateral thyroid.","- A <1cm TR_4 nodule in _ thyroid.","- <1cm TR_4 nodules in _bilateral thyroid.(Srs/Img:_/_ _)","BRK","- A TR_ nodule in _right _left thyroid, _cm.(Srs/Img:1/_)")
return

; ==============================================================================
; Thyroid Nodule UI - 快速選擇左右側 nodules/cysts
; ==============================================================================
::tnui::
    Gui, TN:Destroy
    Gui, TN:Font, s11, Microsoft JhengHei
    
    ; 說明文字
    Gui, TN:Add, Text, x10 y10 w380 h20 Center, 螢幕左側 = Patient Right  |  螢幕右側 = Patient Left
    
    ; ==============================================================================
    ; 左側 GroupBox -> 控制 Right thyroid
    ; ==============================================================================
    Gui, TN:Add, GroupBox, x10 y35 w180 h180, Right Thyroid
    Gui, TN:Add, CheckBox, x25 y60 w150 h25 vTN_R_Cyst, Cyst
    Gui, TN:Add, CheckBox, x25 y90 w150 h25 vTN_R_TR2, TR2 (<1cm)
    Gui, TN:Add, CheckBox, x25 y115 w150 h25 vTN_R_TR3, TR3 (<1cm)
    Gui, TN:Add, CheckBox, x25 y140 w150 h25 vTN_R_TR4, TR4 (<1cm)
    Gui, TN:Add, CheckBox, x25 y165 w150 h25 vTN_R_TR5, TR5 (<1cm)
    
    ; ==============================================================================
    ; 右側 GroupBox -> 控制 Left thyroid
    ; ==============================================================================
    Gui, TN:Add, GroupBox, x200 y35 w180 h180, Left Thyroid
    Gui, TN:Add, CheckBox, x215 y60 w150 h25 vTN_L_Cyst, Cyst
    Gui, TN:Add, CheckBox, x215 y90 w150 h25 vTN_L_TR2, TR2 (<1cm)
    Gui, TN:Add, CheckBox, x215 y115 w150 h25 vTN_L_TR3, TR3 (<1cm)
    Gui, TN:Add, CheckBox, x215 y140 w150 h25 vTN_L_TR4, TR4 (<1cm)
    Gui, TN:Add, CheckBox, x215 y165 w150 h25 vTN_L_TR5, TR5 (<1cm)
    
    ; ==============================================================================
    ; 輸出按鈕
    ; ==============================================================================
    Gui, TN:Add, Button, x10 y225 w380 h40 gTN_Generate Default, 輸出 (&1)
    Gui, TN:Add, Button, x10 y275 w180 h35 gTN_LargeNodule, >1cm Nodule (&2)
    Gui, TN:Add, Button, x200 y275 w180 h35 gTN_Close, 關閉 (&Q)
    
    Gui, TN:Show, w400 h320, Thyroid Nodules
return
; ==============================================================================
; Thyroid Nodule UI - 邏輯處理
; ==============================================================================
TN_Generate:
    Gui, TN:Submit, NoHide
    desc := ""
    
    ; --- 處理 Cyst ---
    cystDesc := ""
    if (TN_R_Cyst AND TN_L_Cyst) {
        cystDesc := "Bilateral thyroid cysts."
    } else if (TN_R_Cyst) {
        cystDesc := "Right thyroid cyst."
    } else if (TN_L_Cyst) {
        cystDesc := "Left thyroid cyst."
    }
    
    ; --- 處理 Nodules ---
    ; 計算右側 TR
    R_TRs := []
    if (TN_R_TR2)
        R_TRs.Push(2)
    if (TN_R_TR3)
        R_TRs.Push(3)
    if (TN_R_TR4)
        R_TRs.Push(4)
    if (TN_R_TR5)
        R_TRs.Push(5)
    
    ; 計算左側 TR
    L_TRs := []
    if (TN_L_TR2)
        L_TRs.Push(2)
    if (TN_L_TR3)
        L_TRs.Push(3)
    if (TN_L_TR4)
        L_TRs.Push(4)
    if (TN_L_TR5)
        L_TRs.Push(5)
    
    R_Count := R_TRs.MaxIndex() ? R_TRs.MaxIndex() : 0
    L_Count := L_TRs.MaxIndex() ? L_TRs.MaxIndex() : 0
    totalCount := R_Count + L_Count
    
    noduleDesc := ""
    
    if (totalCount = 1) {
        ; 只有一個 nodule
        if (R_Count = 1) {
            theTR := R_TRs[1]
            noduleDesc := "- A <1cm TR" . theTR . " nodule in right thyroid."
        } else {
            theTR := L_TRs[1]
            noduleDesc := "- A <1cm TR" . theTR . " nodule in left thyroid."
        }
    } else if (totalCount > 1) {
        ; 多個 nodules - 合併所有 TR 值
        allTRs := []
        for i, v in R_TRs
            allTRs.Push(v)
        for i, v in L_TRs
            allTRs.Push(v)
        
        ; 去重並排序
        uniqueTRs := {}
        for i, v in allTRs
            uniqueTRs[v] := 1
        
        ; 找出最小和最大
        minTR := 9
        maxTR := 0
        for k, v in uniqueTRs {
            if (k < minTR)
                minTR := k
            if (k > maxTR)
                maxTR := k
        }
        
        ; 構建 TR 範圍字串
        if (minTR = maxTR) {
            trRange := "TR" . minTR
        } else {
            trRange := "TR" . minTR . "-" . maxTR
        }
        
        ; 判斷是雙側還是單側
        if (R_Count > 0 AND L_Count > 0) {
            noduleDesc := "- <1cm " . trRange . " nodules in bilateral thyroid."
        } else if (R_Count > 0) {
            noduleDesc := "- <1cm " . trRange . " nodules in right thyroid."
        } else {
            noduleDesc := "- <1cm " . trRange . " nodules in left thyroid."
        }
    }
    
    ; --- 組合輸出 ---
    if (cystDesc != "" AND noduleDesc != "") {
        desc := cystDesc . "`r" . noduleDesc
    } else if (cystDesc != "") {
        desc := cystDesc
    } else if (noduleDesc != "") {
        desc := noduleDesc
    } else {
        MsgBox, 請至少勾選一個項目
        return
    }
    
    CopyCXRtoHISWithParam(1)
return
TN_LargeNodule:
    desc := "- A _solid _hypoechoic nodule in _LRt _mid. thyroid, _x_x_ mm, TR_.(Srs/Img:1/_)"
    CopyCXRtoHISWithParam(1)
return
TN_Close:
    Gui, TN:Destroy
return


::tirads::
WinGet, ActiveId, ID, A ; 目前視窗ID
Gui Font, s12
Gui Add, GroupBox, x20 y15 w340 h130, COMPOSITION
Gui Add, Radio, xp+15 yp+20 w300 h23 vC1, Cystic or almost completely cystic  0 points
Gui Add, Radio, xp yp+25 w300 h23 vC2, Spongiform                          0 points
Gui Add, Radio, xp yp+25 w300 h23 vC3, Mixed cystic and solid              1 point 
Gui Add, Radio, xp yp+25 w300 h23 vC4 checked1, Solid or almost completely solid    2 points

Gui Add, GroupBox, x20 y150 w340 h130, ECHOGENICITY
Gui Add, Radio, xp+15 yp+20 w300 h23 vE1, Anechoic                            0 points
Gui Add, Radio, xp yp+25 w300 h23 vE2, Hyperechoic or isoechoic            1 point 
Gui Add, Radio, xp yp+25 w300 h23 vE3 checked1, Hypoechoic                          2 points
Gui Add, Radio, xp yp+25 w300 h23 vE4, Very hypoechoic                     3 points

Gui Add, GroupBox, x20 y285 w340 h80, SHAPE
Gui Add, Radio, xp+15 yp+20 w300 h23 vS1 checked1, Wider-than-tall                     0 points
Gui Add, Radio, xp yp+25 w300 h23 vS2, Taller-than-wide                    3 points

Gui Add, GroupBox, x20 y370 w340 h130, MARGIN
Gui Add, Radio, xp+15 yp+20 w300 h23 vM1 checked1, Smooth                              0 points
Gui Add, Radio, xp yp+25 w300 h23 vM2, Ill-defined                         0 points
Gui Add, Radio, xp yp+25 w300 h23 vM3, Lobulated or irregular              2 points
Gui Add, Radio, xp yp+25 w300 h23 vM4, Extra-thyroidal extension           3 points

Gui Add, GroupBox, x20 y510 w340 h130, ECHOGENIC FOCI
Gui Add, Radio, xp+15 yp+20 w300 h23 vF1 checked1, None or large comet-tail artifacts  0 points
Gui Add, Radio, xp yp+25 w300 h23 vF2, Macrocalcifications                 1 point
Gui Add, Radio, xp yp+25 w300 h23 vF3, Peripheral (rim) calcifications     2 points
Gui Add, Radio, xp yp+25 w300 h23 vF4, Punctate echogenic foci             3 points

Gui Add, GroupBox, x385 y15 w120 h150, Vascularity
Gui Add, CheckBox, xp+15 yp+20 w100 h23 vV1, Avascular
Gui Add, CheckBox, xp yp+25 w100 h46 vV2, Internal vascularity
Gui Add, CheckBox, xp yp+45 w100 h46 vV3, Peripheral vascularity


Gui Add, GroupBox, x385 y225 w120 h160, TI-RADS 
Gui Add, CheckBox, xp+15 yp+20 w100 h23 vTD1, TI-RADS 1
Gui Add, CheckBox, xp yp+25 w100 h23 vTD2, TI-RADS 2
Gui Add, CheckBox, xp yp+25 w100 h23 vTD3, TI-RADS 3
Gui Add, CheckBox, xp yp+25 w100 h23 vTD4, TI-RADS 4
Gui Add, CheckBox, xp yp+25 w100 h23 vTD5, TI-RADS 5

Gui Add, Button, x380 y580 w140 h60 Default, Tirads
Gui Add, Button, x400 y390 w100 h35 gSub2, 只要解說
Gui Add, Button, xp yp+40 w100 h35 gSub3, FNA thyroid
Gui Add, Button, xp yp+40 w100 h35 gSub4, FNA Other


Gui Show, w540 h650, ACR TI-RADS
return

ButtonTirads:
Gui, Submit, NoHide
desc := "Description of the most suspicious nodule`r"
tirscr := 0

desc .= "Vascularity    "
If(V1){
	desc .= "(V) Avascular "	
} else{
	desc .= "( ) Avascular "	
}
If(V2){
	desc .= "(V) Internal "	
} else{
	desc .= "( ) Internal "	
}
If(V3){
	desc .= "(V) Peripheral vascularity "	
} else{
	desc .= "( ) Peripheral vascularity "	
}
desc .= "`r"

desc .= "COMPOSITION    "
If(C1){
	desc .= "Cystic or almost completely cystic  0 points`r"
} else If(C2){
	desc .= "Spongiform                          0 points`r"
} else If(C3){
	desc .= "Mixed cystic and solid              1 point`r"
	tirscr := tirscr + 1
} else If(C4){
	desc .= "Solid or almost completely solid    2 points`r"
	tirscr := tirscr + 2
}

desc .= "ECHOGENICITY   "
If(E1){
	desc .= "Anechoic                            0 points`r"
} else If(E2){
	desc .= "Hyperechoic or isoechoic            1 point `r"
	tirscr := tirscr + 1
} else If(E3){
	desc .= "Hypoechoic                          2 points`r"
	tirscr := tirscr + 2
} else If(E4){
	desc .= "Very hypoechoic                     3 points`r"
	tirscr := tirscr + 3
}

desc .= "SHAPE          "
If(S1){
	desc .= "Wider-than-tall                     0 points`r"
} else If(S2){
	desc .= "Taller-than-wide                    3 points`r"
	tirscr := tirscr + 3
}

desc .= "MARGIN         "
If(M1){
	desc .= "Smooth                              0 points`r"
} else If(M2){
	desc .= "Ill-defined                         0 points`r"
} else If(M3){
	desc .= "Lobulated or irregular              2 points`r"
	tirscr := tirscr + 2
} else If(M4){
	desc .= "Extra-thyroidal extension           3 points`r"
	tirscr := tirscr + 3
}

desc .= "ECHOGENIC FOCI "
If(F1){
	desc .= "None or large comet-tail artifacts  0 points`r"
} else If(F2){
	desc .= "Macrocalcifications                 1 point `r"
	tirscr := tirscr + 1
} else If(F3){
	desc .= "Peripheral (rim) calcifications     2 points`r"
	tirscr := tirscr + 2
} else If(F4){
	desc .= "Punctate echogenic foci             3 points`r"
	tirscr := tirscr + 3
}

desc .= "Total points: " . tirscr . "`r"
If (tirscr == 0){
	desc .= "TR1: Benign"
} else If (tirscr == 2){
	desc .= "TR2: Not Suspicious"
} else If (tirscr == 3){
	desc .= "TR3: Mildly suspicious"
} else If (tirscr <= 6 and tirscr > 3){
	desc .= "TR4: Moderately suspicious(4-6 points)"
} else If (tirscr >6){
	desc .= "TR5: Mildly suspicious(>= 7 points)"
}
desc .= "`r`r"

Sub2:
Gui, Submit, NoHide
If(TD1){ 
	desc .= "TR1: no FNA required`r"
}
If(TD2){
	desc .= "TR2: no FNA required`r"
}
If(TD3){
	desc .= "TR3: 3 points   mildly suspicious`r"
	desc .= "     >=2.5 cm FNA`r"
	desc .= "     >=1.5 cm follow up: 1, 3 and 5 years`r"
}
If(TD4){
	desc .= "TR4: 4-6 points moderately suspicious`r"
	desc .= "     >=1.5 cm FNA`r"
	desc .= "     >=1.0 cm follow up: 1, 2, 3 and 5 years`r"
}
If(TD5){
	desc .= "TR5: >=7 points highly suspicious`r"
	desc .= "     >=1.0 cm FNA`r"
	desc .= "     >=0.5 cm follow up: every year for 5 years`r"
}
desc .= "ACR TI-RADS 2017`r"
WinActivate, ahk_id %ActiveId% ; ^  W @    
SendInput %desc%
desc := ""
tirscr := 0
return


Sub3:
Gui, Submit, NoHide
desc .= "Ultrasound (US)-guided Fine-Needle Aspiration (FNA)`r`r"
desc .= "_The study is compared with prior diagnostic US.`r`r"
desc .= "FNA #:1`rTarget Lesion: `r"
desc .= "  Maximum size: _cm `r"
desc .= "  Location: _right _left isthmus _upper middle lower `r"
desc .= "  _ACR TI-RADS risk category: TR1 (0 points), TR2 (2 points), TR3 (3 points), TR4 (4-6 points), TR5 (>=7 points)`r"
desc .= "  Reason for FNA: meets ACR TI-RADS criteria, meets other recommendations but not ACR TI-RADS, indeterminate on prior FNA, nondiagnostic on prior FNA, patient risk factors, patient/referrer request, tissue diagnosis.`r`r"
desc .= "  Before procedure, explained need and risk to patient.`r  No immediate complications noted after procedure.`r`r"
  
desc .= "Impression:`rSuccessful ultrasound guided FNA of _thyroid nodule.`r"

gosub CopyCXRtoHIS
return

Sub4:
Gui, Submit, NoHide
desc .= "Ultrasound (US)-guided Fine-Needle Aspiration (FNA)`r`r"
desc .= "_The study is compared with prior diagnostic US.`r`r"
desc .= "FNA #:1`rTarget Lesion: `r"
desc .= "  Maximum size: _cm `r"
desc .= "  Location: _right _left _`r"
desc .= "  Reason for FNA: tissue diagnosis. _indeterminate on prior FNA, nondiagnostic on prior FNA, patient risk factors, patient/referrer request.`r`r"
desc .= "  Before procedure, explained need and risk to patient.`r  No immediate complications noted after procedure.`r`r"
  
desc .= "Impression:`rSuccessful ultrasound guided FNA of _.`r"


gosub CopyCXRtoHIS
return


GuiClose:
GuiEscape:
Gui, Destroy 
return


;============================================================================================
; US - ABD
;============================================================================================
:O:bph;::Enlarged prostate with calcifications, est. volume about _ cc.
:O:bph2::
HotstringMenuV("A","MenuShortcut","Prostate cysts, calcifications, est. volume about _ cc.", "Enlarged prostate with cysts, calcifications, est. volume about _ cc.", "Prostate calcifications, est. volume about _ cc.", "Est. prostate volume about _cc.", "BRK", "Heterogenous enhancement of prostate", "Heterogenous enhancement of prostate with hypoenhancing parts, size about _(Srs/Img:_/_)","Suggest correlate with PSA or other exams.")
return

::usa::
HotstringMenuV("A","MenuShortcut", "Upper abdominal sonography:", "Urotract sonography:","TRUS sonography:","Lower abdomen sonography:" )
SendInput `r

; AI 輔助分析功能已移除，請使用 usaigui; 啟動 AHK 版本的 AI 分析

MsgBox, 4,, "Would you like to compaire previous study...(press Yes or No)"
IfMsgBox, Yes
	gosub calldate

SendInput `rFindings and Impressions:`r_`r`rOtherwise unremarkable.  
return



:O:usadd::
HotstringMenuV("A","MenuShortcut", "Mild enlarged bilateral kidney sizes.","Coarse echotexture of the liver with uneven surface, suggesting cirrhosis of liver. ","No US evidence of hydronephrosis.","* Gas block/Poor visualization of _pancreas_right lobe of liver from subcostal area. Lesion may be obscured.`r")
return




::usabd3::
WinGet, ActiveId, ID, A ;取得目前視窗
Gui Font, s12
Gui Add, Button, x10 y10 w120 h50 gABDUS1, Upper Abdomen
Gui Add, Button, x10 yp+65 w120 h50 gABDUS2, Urotract(M)
Gui Add, Button, x10 yp+65 w120 h50 gABDUS3, Urotract(F)
Gui Add, Button, x10 yp+65 w120 h50 gABDUS4, TRUS
Gui Add, Button, x10 yp+65 w120 h23 gCalldate, Compare ...(&C)
Gui Add, Button, x160 yp w120 h23 gAI_FindOpen, AI Findings (&A)
Gui Add, CheckBox, x160 y10 w140 h23 vOPT2, CLPD(&L)
Gui Add, Radio, xp yp+25 w140 h23 vL1 checked1, Normal liver
Gui Add, Radio, xp yp+25 w140 h23 vL2, Mild fatty liver(&F)
Gui Add, Radio, xp yp+25 w140 h23 vL3, Moderate fatty 
Gui Add, Radio, xp yp+25 w140 h23 vL4, Severe fatty liver
Gui Add, CheckBox, xp yp+25 w140 h23 vOPT3, S/P LC.
Gui Add, CheckBox, xp yp+25 w140 h23 vOPT4, CRPD(&R)
Gui Add, CheckBox, xp yp+25 w140 h23 vOPT5, Splenomegaly(&S)
Gui Add, CheckBox, xp yp+25 w140 h23 vOPT6, Others:(&*)
Gui Add, CheckBox, x310 y10 w180 h23 vOPT7, Pancreas gas block(&G)
Gui Add, CheckBox, xp yp+25 w180 h23 vOPT8, Subcostal gas block
Gui Add, CheckBox, xp yp+25 w180 h23 vOPT9 checked1, Renal size ok
Gui Add, CheckBox, xp yp+25 w180 h23 vOPT10, UB wall thickening
Gui Add, CheckBox, xp yp+25 w180 h23 vOPT11, UB not distended

;Gui Add, CheckBox, xp yp+25 w140 h23 vOPT12, Enlarged prostate(&P)

Gui Show, w470 h300, Abd US 簡化
Return

ABDUS1:
desc := "Upper abdomen sonography:`r"
gosub ABDUScommon
gosub ABDUScommon2
gosub CopyCXRtoHIS
return

ABDUS2:
desc := "Urotract sonography:`r"
gosub ABDUScommon
gosub ABDUSUro1
gosub ABDUSUro2
gosub ABDUScommon2
gosub CopyCXRtoHIS
return

ABDUS3:
desc := "Urotract sonography:`r"
gosub ABDUScommon
gosub ABDUSUro1
gosub ABDUScommon2
gosub CopyCXRtoHIS
return

ABDUS4:
Gui, Submit, NoHide
desc := "TRUS sonography:`r"
gosub ABDUSUroK
gosub ABDUSUro1
desc .= "`r# Prostate:`r"
desc .= "Normal sizes and echopattern of bilateral seminal vesicles, no focal nodules are seen.`r"
desc .= "No focal nodules are seen at the peripheral zone of the prostate.`rProstate cysts.`r"
desc .= "The prostate is measuring __ mm in size with volume estimated to be __ c.c. Calcification(_)`r"
gosub ABDUScommon2
gosub CopyCXRtoHIS
Return

ABDUSUroK:
desc .= "`r# Kidneys:`r"
If(OPT9){
	desc .= "Acceptable bilateral kidney sizes.`r"
}else{
	desc .= "The right is _cm and left is _cm longitudinally.`r"
}
desc .= "No US evidence of hydronephrosis.`r"
If (OPT4){
	desc .= "Increased echogenicity are seen over both kidneys with ill defined corticomedullary junctions, suggesting chronic renal parenchyma disease.`r"
}
return

ABDUSUro1:
desc .= "`r# Urinary bladder:`r"
If (OPT10){
	desc .= "_Well distended with smooth wall thickening.`r"
}
If (OPT11){
	desc .= "* Urinary bladder is not distended, limited evaluation.`r"
}
If (!OPT11 AND !OPT10){
	desc .= "Well distended with smooth wall.`r"
}
return

ABDUSUro2:
desc .= "`r# Prostate:`r"
desc .= "The prostate is measuring __ mm in size with volume estimated to be __ c.c. Calcification(_)`r"
return

ABDUScommon:
Gui, Submit, NoHide
desc .= "`r# Liver:`r"
If(L1){
	desc .= "Normal size and echogenicity of the liver parenchyma. `r"
} else If(L2){
	desc .= "Normal size and mild increased echogenicity of the liver parenchyma. `r"
} else If(L3){
	desc .= "Normal size and obvious increased echogenicity of the liver parenchyma, moderate fatty liver favored. `r"
} else If(L4){
	desc .= "Increased echogenicity of liver with obliteration of the portal sheath, obscuring liver parenchyma, severe fatty liver favored.`r"
} 
If (OPT2){
	desc .= "Coarse echotexture of the liver with smooth surface_, suggesting chronic liver parenchyma disease.`r"
}
If (OPT8){
	desc .= "* Gas block/Poor visualization of _right lobe of liver from subcostal area due to prominent bowel gas. Lesion may be obscured.`r"
	desc .= "* Gas block/Poor visualization of right lobe of liver from subcostal area. Lesion may be obscured.`r"

}
desc .= "`r# Biliary trees:`r"
desc .= "No evidence of biliary tract dilatation.`r"
desc .= "`r# Gallbladder:`r"
If (OPT3){
	desc .= "GB is not seen. S/P cholecystectomy.`r"
}else{
	desc .= "Unremarkable with smooth wall.`r"
}
desc .= "`r# Pancreas:`r"
If (OPT7){
	desc .= "* Gas block/Poor visualization of pancreas due to prominent bowel gas. Lesion may be obscured.`r"
	desc .= "* Gas block/Poor visualization of pancreas. Lesion may be obscured.`r"
}else{
	desc .= "Unremarkable size and echogenicity of the visible pancreas.`r"
}
desc .= "`r# Spleen:`r"
If(OPT5){
	desc .= "Splenomegaly.`r"
}else{
	desc .= "Normal size and echogenicity.`r"
}
gosub ABDUSUroK
return

ABDUScommon2:
If (OPT6){
	desc .= "`r# Others:`r_`r"
}
return



::usshou::
    gosub GetSideSelection

    ; 2. (選用) 檢查使用者是否按了取消(X)，如果變數是空的就終止
    if (tSideCap = ""){
        tSideCap := "_"
		tSideLow := "_"
	}

    ; 3. 貼上內容 (使用設定好的變數)
    SendInput,
(
Ultrasonography of %tSideLow% shoulder:

Biceps tendon lond head:
- unremarkable morphology and echogenicities

Subscapularis muscle and tendon:
- unremarkable morphology and echogenicities

Supraspinatus muscle and tendon:
- unremarkable morphology and echogenicities

Infraspinatus muscle and tendon:
- unremarkable morphology and echogenicities

_Teres minor muscle and tendon:
- unremarkable morphology and echogenicities

)
return

; ============================================================================
; AI Findings Generator (Impression -> Findings), AutoHotkey v1
; Requires: environment variable OPENAI_API_KEY
; Hot entry point: gAI_FindOpen from Abd US 簡化 GUI
; ============================================================================

AI_FindOpen:
Gui, I2F:New, -AlwaysOnTop +Resize, Impression → Findings (AI)
Gui, I2F:Font, s10, Segoe UI

; 超音波類型選擇
Gui, I2F:Add, GroupBox, x10 y10 w480 h80, 超音波類型
Gui, I2F:Add, Radio, x20 y30 w140 vI2F_TypeUpperAbd Checked, &Upper abdomen
Gui, I2F:Add, Radio, x170 y30 w140 vI2F_TypeUroM, Urotract (&M)
Gui, I2F:Add, Radio, x320 y30 w140 vI2F_TypeUroF, Urotract (&F)
; --- [新增] Prompt 情境選擇 ---
Gui, I2F:Add, Text, x20 y60 w80 h20, 輸出模式:
; vI2F_Scenario 是變數名稱，Choose1 代表預設選第一個
Gui, I2F:Add, DropDownList, x100 y55 w360 vI2F_Scenario Choose1, 腹超||TRUS||IVP

Gui, I2F:Add, Text, xm y+25, Impression:
Gui, I2F:Add, Edit, vI2F_Impression w480 h160
Gui, I2F:Add, Button, gI2F_DoGenerate w120 h28 Default, &Generate
Gui, I2F:Add, Button, gI2F_Clear x+10 w80 h28, Clear
Gui, I2F:Add, Text, xm y+12 Section, Findings (descriptive, system-organized):
Gui, I2F:Add, Edit, vI2F_Findings w480 h200
Gui, I2F:Add, Button, gI2F_CopyFindings w140 h26, &Copy Findings
Gui, I2F:Add, Text, xm y+12, Optimized Impression (severity-ordered):
Gui, I2F:Add, Edit, vI2F_ImprOpt w480 h120
Gui, I2F:Add, Button, gI2F_CopyImpr w200 h26, Copy Optimized Impression
Gui, I2F:Show
return

I2F_Clear:
Gui, I2F:Submit, NoHide
GuiControl, I2F:, I2F_Findings
GuiControl, I2F:, I2F_ImprOpt
return

I2F_CopyFindings:
Gui, I2F:Submit, NoHide
Clipboard := RegExReplace(I2F_Findings, "\r?\n", "`r`n")  ; 將 LF 或 CRLF 都正規化為 CRLF
MsgBox, 64, Copied, %Clipboard%
return

I2F_CopyImpr:
Gui, I2F:Submit, NoHide
Clipboard := RegExReplace(I2F_ImprOpt, "\r?\n", "`r`n")
MsgBox, 64, Copied, Optimized Impression copied to clipboard.
return

I2F_DoGenerate:
Gui, I2F:Submit, NoHide
if (I2F_Impression = "") {
    MsgBox, 48, Warning, Please paste Impression first.
    return
}

;EnvGet, API_KEY, OPENAI_API_KEY
if (!API_KEY) {
    MsgBox, 16, Error, OPENAI_API_KEY is not set. Please add it as a user environment variable.
    return
}

endpoint := "https://api.openai.com/v1/chat/completions"
gModel   := "gpt-4o"  ; change if needed

; 根據超音波類型構建不同的系統提示詞
if (I2F_TypeUpperAbd) {
    usType := "Upper abdomen"
    usTitle := "Upper abdominal sonography:"
    organSystems := "Liver:`nBiliary trees:`nGallbladder:`nPancreas:`nSpleen:`nKidneys:"
    conditionalOutput := "Do NOT output: Uterus/adnexa, Others, Aorta/IVC, Urinary bladder, Prostate (unless specifically mentioned in impression)"
} else if (I2F_TypeUroM) {
    usType := "Urotract (M)"
    usTitle := "Urotract sonography:"
    organSystems := "Liver:`nBiliary trees:`nGallbladder:`nPancreas:`nSpleen:`nKidneys:`nUrinary bladder:`nProstate:"
    conditionalOutput := "Do NOT output: Uterus/adnexa, Others, Aorta/IVC (unless specifically mentioned in impression)"
} else if (I2F_TypeUroF) {
    usType := "Urotract (F)"
    usTitle := "Urotract sonography:"
    organSystems := "Liver:`nBiliary trees:`nGallbladder:`nPancreas:`nSpleen:`nKidneys:`nUrinary bladder:"
    conditionalOutput := "Do NOT output: Uterus/adnexa, Others, Aorta/IVC, Prostate (unless specifically mentioned in impression)"
}

if (InStr(I2F_Scenario, "腹超")) {
sysPrompt =
(
You are a radiology reporting assistant specializing in abdominal/urotract ultrasound reports.

TASK: Convert impression text into structured findings and optimized impression.

OUTPUT FORMAT - Use these EXACT tags:

<<FINDINGS>>
First line MUST be: %usTitle%
Second line (CONDITIONAL): If comparison study exists, add:
Comparison with previous study: [date/time].
(followed by a blank line)

Then output these organ systems in this EXACT order, even if normal:

%organSystems%

%conditionalOutput%

FINDINGS RULES:
1. DESCRIPTIVE ONLY – No diagnostic terms, no speculation words (avoid: suggest, consistent with, probably, favor, compatible with).
2. Standard normal descriptions for each organ:
   - Liver: "Normal size and echogenicity of the liver parenchyma"
   - Biliary trees: "No evidence of biliary tract dilatation"
   - Gallbladder: "Well distended with smooth wall"
   - Pancreas: "Normal size and echogenicity of the visible pancreas"
   - Spleen: "Normal size and echogenicity"
   - Kidneys: "Acceptable bilateral kidney sizes. No US evidence of hydronephrosis"
   - Urinary bladder: "Well distended with smooth wall"
   - Prostate: "Normal size and echogenicity"
   - Others: List incidental or extra-abdominal findings (e.g., ascites, pleural effusion, peritoneal nodules, retroperitoneal masses) with bullet points and descriptive terms only.
3. Convert diagnoses to sonographic descriptions (case-insensitive):
   - hepatic cysts → "anechoic thin-walled lesions in liver"
   - fatty liver / steatosis → "diffusely increased echogenicity of liver parenchyma"
   - renal stone → "echogenic focus with posterior acoustic shadowing in kidney"
   - gallstones → "echogenic foci with acoustic shadowing in gallbladder"
   - hydronephrosis → "dilatation of renal collecting system"
   - s/p cholecystectomy → "post-surgical changes, gallbladder not visualized"
   - prostate calcifications → "echogenic foci within prostate parenchyma"
   - prostate volume X cc → (combine with measurement, see below)
   - Prostate measurements like "42x30x47" → If both size & volume are present, format as: "Prostate measuring 42x30x47 mm in size with volume estimated to be 34 c.c."
   - **If only one present**, use: "Prostate measuring 34x33x43 mm" OR "Prostate volume estimated to be 26 c.c."
   - (chronic) liver parenchymal disease → "coarse echotexture of the liver parenchyma" (use this phrasing instead of “diffusely increased echogenicity” when this phrase appears). If fatty liver/steatosis is also explicitly mentioned, you may include both bullets, with coarse echotexture first, e.g. "- Coarse, increased echotexture of the liver parenchyma".
4. Include location, side, size when provided.
5. Use bullet points within each system.
6. Post-procedure / post-device language (NEW — exact wording rules):
   - Do **not** label non-surgical device insertions as "post-surgical changes". Foley insertion, pigtail drainage, PTGBD, NG tube, central line, etc. are **procedures/devices**, not surgeries.
   - Use the phrasing **"Post [device/procedure] insertion"** (e.g., "Post Foley insertion", "Post pigtail drainage insertion", "Post PTGBD insertion") when the impression documents those devices/procedures.
   - Alternatively, use **"Post procedure changes"** when multiple/non-specific procedures are present or when a generic term is preferred.
   - Examples (use these formats exactly):
     - Incorrect: "Post-surgical changes from Foley insertion"
     - Correct: "Post Foley insertion"
     - Multiple devices: "Post Foley insertion and pigtail drainage" or separate bullets:
       - "- Post Foley insertion"
       - "- Post pigtail drainage insertion"
   - Keep these as descriptive statements (no diagnostic or causal language) and include side/locational details if provided (e.g., "Post right PTGBD insertion").
   - **Still** use "post-surgical changes, gallbladder not visualized" only for true surgical procedures (e.g., s/p cholecystectomy).
7. Poor visualization rule:
   - If impression mentions poor visualization or limited evaluation due to gas, bowel, ribs, or other artifacts, output the limitation under the corresponding organ system.
   - For whole organ: "- Poor visualization due to gas interference".
   - For partial organ: "- Poor visualization of [region] due to gas interference".
   - If multiple organs are affected, list each under its respective organ heading.
8. Comparison study rule:
   - If the impression or input contains "Comparison with previous study:" followed by a date/time, extract this information.
   - Insert it as the second line in the FINDINGS section, immediately after the title line (%usTitle%).
   - Format: "Comparison with previous study: [date/time]."
   - Leave a blank line after the comparison line before starting organ systems.
   - Example output:
     Upper abdominal sonography:
     Comparison with previous study: 2025.05.21 11:25.

<<IMPRESSION>>
Rewrite and optimize the impression with:
1. SEVERITY-BASED ORDER: urgent/obstructive → suspicious masses → benign lesions → exam limitations
2. Concise clinical language
3. Maintain diagnostic meaning
4. Use numbered or bullet format for clarity

ORGAN MAPPING GUIDE:
- Hepatic cysts, fatty liver, liver lesions → Liver
- S/P cholecystectomy, gallstones, GB polyps → Gallbladder
- CBD dilatation, biliary stones → Biliary trees
- Renal stones, hydronephrosis, renal cysts → Kidneys
- UB wall thickening, bladder stones → Urinary bladder
- Prostate enlargement, prostate calcifications, prostate volume, prostate measurements → Prostate
- Pancreatic lesions, pancreatitis → Pancreas
- Splenomegaly → Spleen
- Ascites, pleural effusion, peritoneal nodules, retroperitoneal findings → Others

STRICT RULES:
- Never invent measurements not provided.
- No speculation in FINDINGS section.
- Preserve all clinical information from original impression.
- If size unspecified, omit measurements.
)

}else if (InStr(I2F_Scenario, "IVP")) {

sysPrompt =
(
You are a radiology reporting assistant for intravenous urography (IVU/IVP).

TASK
Convert a provided “Impression” into a two-block report, using these EXACT tags:

<<FINDINGS>>
First line MUST be:
Intravenous urography (IVU):

Second line (CONDITIONAL): If a comparison study exists in the input, add:
Comparison with previous study: [date/time].
(followed by a blank line)

Then output:
- Urotract descriptive findings (條列式，依規則生成)
- Incidental non-urotract findings (同樣條列，保持中性描述)

<<IMPRESSION>>
First line MUST be:
Impression:

Then output:
- Urotract-related key items, one per bullet
- Any bladder / prostate related key items
- Any critical / urgent non-urotract issues (if present)
(所有非關鍵非泌尿 incidental 事項一律不列於此區，只留在 FINDINGS)

Do NOT output any other sections before, between, or after these tags.
Do NOT output lines of “=====” or other separators.
Only output these two blocks in this exact order: <<FINDINGS>> then <<IMPRESSION>>.

===============================================================================
FILTERING RULES – <<IMPRESSION>> BLOCK (Impression:)
===============================================================================
KEEP
• 泌尿系統重點：腎臟、輸尿管（含段別）、腎盂腎盞、UPJ/UVJ、膀胱、前列腺肥大、結石、狹窄、阻塞、水腎 / 水腎管、對比劑滯留、延遲或持續腎影。
• 重要 / 急症非泌尿議題（少見；如主動脈破裂、嚴重出血等）。

OMIT
• 其餘非泌尿 incidental 訊息（如骨刺、退化、器質性脊椎變化等）——這些只出現在 <<FINDINGS>> 區，不要出現在 <<IMPRESSION>> 區。

寫作原則：
• 使用條列式，每個重點一個 bullet（“- ”開頭）。
• 語氣偏臨床結論，可保留診斷用語，但避免不必要的推測。
• 依「重要度排序」：阻塞 / 急症 → 可疑重大病灶 → 次要病灶（結石、肥大等）。

例：若輸入 “Mild enlarged prostate.”，則 <<IMPRESSION>> 可寫為：
Impression:
- Enlarged prostate.

===============================================================================
FINDINGS GENERATION RULES – <<FINDINGS>> BLOCK
===============================================================================
標題行固定：
Intravenous urography (IVU):

內容格式：
• 每一行 Findings 皆以 “- ” 開頭。
• 簡潔描述影像所見，避免診斷 / 推測語氣 (avoid: suggest, likely, probably)。
• 先列泌尿系統所見，再列 incidental 非泌尿所見。
• 保持現在式與標準放射學措辭（例如用 “indented” 而非 “indentated”）。
• 保留 laterality（左右側）、大小（若有）、解剖段別 / level。
• 不自行捏造原文未提供的數字或測量值。

===============================================================================
CONFLICT RESOLUTION PRIORITY – SCOUT FILM STONES
===============================================================================
When generating the scout film line in <<FINDINGS>>:

1. If the input Impression mentions any urinary tract stone, such as:
   - renal stone / renal stones
   - ureteral stone / ureter stone / UVJ stone / UPJ stone
   - ureteral calculus / urinary tract calculus
   - bladder stone / vesical stone
   or equivalent terms in other languages

   THEN:
   - DO NOT use the normal sentence
     "There is no abnormal calcified nodular lesion on the scout film."
   - INSTEAD, write an abnormal sentence. For renal stones:

     • If side is specified (e.g. "Left renal stone over middle calyx"):
       "There is abnormal calcified nodular lesion at left renal region on the scout film."

     • If side is not specified:
       "There is abnormal calcified nodular lesion at the renal region on the scout film."

2. Only when the Impression does NOT mention any urinary tract stone
   may you use the normal sentence:
   "There is no abnormal calcified nodular lesion on the scout film."


===============================================================================
BASELINE NORMAL FINDINGS (當未提及相關異常時，一律保留)
===============================================================================
除非輸入的 Impression 明確指出相反異常（例如：結石、水腎、水腎管、明顯 obstruction、異常 nephrogram 等），否則一律在 <<FINDINGS>> 中保留以下正常敘述：

Use the following normal sentences ONLY IF the Impression does NOT describe
any conflicting abnormality for that component:

- For the scout film (only if no stone is mentioned and no other calcified lesion is described):
  "There is no abnormal calcified nodular lesion on the scout film."

- For nephrogram / collecting systems (only if no obstruction, no delayed nephrogram, 
  and no significant hydronephrosis / hydroureter is described):
  "After intravenous contrast administration, normal bilateral nephrograms and opacifications of the bilateral collecting systems are appreciated."
  "No obstructive dilatation or contrast stasis of the urinary collecting system is revealed."
若 Impression 只提到「前列腺肥大」而未提及其他異常，則仍須輸出以上三行正常敘述，再加上膀胱受壓描述（見下一節）。

===============================================================================
BLADDER / PROSTATE MAPPING
===============================================================================
當 Impression 提到前列腺肥大 / enlarged prostate / BPH 等，請在 <<FINDINGS>> 的膀胱描述中加入：

- The urinary bladder is indented by the prostate.

同時：
• 若無其他膀胱異常，僅需上述一行（再加 baseline 正常敘述）。
• 若 Impression 有明確膀胱病灶（如腫瘤、結石、壁增厚），則在同一區塊以額外 bullets 加上：
  - Bladder wall thickening...
  - Filling defect in the urinary bladder compatible with...

===============================================================================
ANATOMIC MAPPING — Scout Film Stone
===============================================================================
若需將 scout film 上的結石位置轉成標準文字，可參考：

• Upper-third ureter：
  “…over the paraspinal region at the L1–L5 level (upper-third ureter)…”

• Middle-third ureter：
  “…over the pelvic brim / iliac vessel crossing region (middle-third ureter)…”

• Lower-third ureter：
  “…over the presacral / pelvic cavity toward the ureterovesical junction (lower-third ureter)…”

===============================================================================
LANGUAGE & GENERAL RULES
===============================================================================
• 一律使用現在式。
• 保持標準放射學英文措辭，避免奇怪變形字。
• 清楚標示 side（right/left/bilateral）、level（UPJ/middle/UVJ）、size（若有提及）。
• 保留所有原 Impression 中與泌尿或重要非泌尿相關的臨床資訊。
• 非關鍵、非泌尿的 incidental 所見，只放在 <<FINDINGS>>，不進 <<IMPRESSION>>。

INPUT
• 任意語言的原始 Impression 文字。

OUTPUT
• 僅輸出上述兩個標籤區塊：
  1) <<FINDINGS>> 區（含 “Intravenous urography (IVU):” 與條列 Findings）
  2) <<IMPRESSION>> 區（含 “Impression:” 與條列結論）
• 不多加任何解釋文字，不加入其他標題或分隔線。

)

}else if (InStr(I2F_Scenario, "TRUS")) {
sysPrompt =
(
You are a radiology reporting assistant specializing in TRUS sonography (transrectal prostate ultrasound) and lower urinary tract ultrasound (kidneys, urinary bladder, prostate).

TASK
Convert the input IMPRESSION text into:
1) Structured TRUS FINDINGS (descriptive, organ-based)
2) An optimized IMPRESSION (clinical/diagnostic language allowed)

=================================
OUTPUT FORMAT (MUST FOLLOW EXACT)
=================================
<<FINDINGS>>
First line MUST be: TRUS sonography:
Second line (CONDITIONAL): If the input contains:
"Comparison with previous study: [date/time]."
then output:
Comparison with previous study: [date/time].
Then add ONE blank line.

Then output organ systems in this EXACT order (even if normal):
Kidneys:
[lines...]

Urinary bladder:
[lines...]

Prostate:
[lines...]

Others:
[ONLY include if there is at least one extra-organ/incidental finding. If none, OMIT the entire Others section.]

After all organ systems, output:
%conditionalOutput%

<<IMPRESSION>>
[optimized impression as numbered or bulleted items; be consistent]

=========================
FINDINGS RULES (GENERAL)
=========================
1) DESCRIPTIVE ONLY in FINDINGS:
- No diagnostic/speculative wording (avoid: suggest, consistent with, probably, favor, compatible with).
- Diagnostic/clinical statements are allowed ONLY in IMPRESSION.

2) NO INVENTED DATA:
- Do NOT guess or calculate measurements/volume not explicitly present in the input.

=========================
DEFAULT NORMAL TEMPLATES
=========================
Kidneys:
- If hydronephrosis/hydro/hydroureter is NOT mentioned: include "No US evidence of hydronephrosis."
- If kidney size is normal and no abnormal kidney findings:
  "Acceptable bilateral kidney sizes."
  "No US evidence of hydronephrosis."
- If input says "Mild enlarged bilateral kidney sizes" (or similar):
  normalize to "Enlarged bilateral kidney sizes."
  still include "No US evidence of hydronephrosis." unless hydronephrosis is described.

Urinary bladder:
- If NO explicit bladder abnormality is mentioned (wall thickening, stones, trabeculation, tumor, definite bladder residual/PVR):
  include "Well distended with smooth wall."
- Only output bladder residual volume when the text clearly refers to bladder/post-void residual (e.g. "post-void residual", "bladder residual").

=========================
PROSTATE RULES (TRUS)
=========================
A) PROSTATE BASELINE PRESERVATION (IMPORTANT)
- Unless explicitly contradicted by the input, ALWAYS include these two baseline normal lines in Prostate:
  1) "Normal sizes and echopattern of bilateral seminal vesicles, no focal nodules are seen."
  2) "No focal nodules are seen at the peripheral zone of the prostate."
- Keep these baseline lines EVEN IF there are prostate cysts, calcifications, enlargement, or post-procedure changes.
- Omit baseline line (2) ONLY if a peripheral-zone focal nodule is explicitly described.

B) VOLUME INTERPRETATION (TRUS-SPECIFIC)
- Any standalone "volume XX cc" or "residual volume XX cc" WITHOUT explicit bladder/PVR wording MUST be interpreted as PROSTATE volume (NOT bladder residual).

C) MEASUREMENT/OLUME FORMATTING
- If size + volume are present:
  "The prostate is measuring AxBxC mm in size with volume estimated to be XX c.c."
- If only linear size:
  "The prostate is measuring AxBxC mm in size."
- If only volume:
  "Estimated prostate volume about XX c.c."
- If calcifications are present AND size/volume are known, prefer appending:
  "... with volume estimated to be XX c.c. Calcification(+)"
  (Do not invent calcification markers if not stated.)

D) HYPOECHOIC NODULE IN PERIPHERAL ZONE (SPECIAL)
If input contains a sentence like:
"A hypoechoic nodule in _ peripheral zone of prostate , _ cm. (Srs/Img:1/_)"
- FINDINGS (Prostate): copy that nodule sentence VERBATIM.
- Do NOT output the baseline PZ line "No focal nodules are seen at the peripheral zone of the prostate."
- IMPRESSION: include:
  1) the same nodule sentence VERBATIM as one line
  2) next line: "Suggest correlate with PSA or other exams."

E) S/P LASER PROSTATECTOMY (SURGICAL CHANGE)
- FINDINGS (Prostate): "s/p laser prostectomy changes."
- IMPRESSION: "Status post laser prostatectomy."
- Do NOT describe as device insertion.

=========================
OTHERS MAPPING
=========================
- Any non-kidney/non-bladder/non-prostate incidental finding (e.g. fatty liver, ascites, pleural effusion) → Others.
- If only one item, short label is fine (e.g. "Others: Fatty liver.")
- If NONE → OMIT the entire Others section.

=========================
IMPRESSION RULES (CLINICAL)
=========================
1) Keep clinically relevant info; do not drop nodules, hydronephrosis, volume, calcifications, surgery, limitations.
2) Severity-based order (most → least critical):
   (1) suspicious prostate nodules/masses (esp. PZ hypoechoic)
   (2) obstruction/hydronephrosis/acute pathology
   (3) enlarged prostate/BPH & major structural change
   (4) benign conditions (cysts, calcifications, mild changes)
   (5) incidental Others findings
   (6) exam limitations
3) Prostate volume threshold 40 c.c. (only if numeric volume is provided):
   - Volume ≥ 40 c.c.:
     - with calcifications: "Enlarged prostate with calcifications, est. volume about XX c.c."
     - without calcifications: "Enlarged prostate, est. volume about XX c.c."
   - Volume < 40 c.c.:
     - with calcifications: "Prostate calcifications, est. volume about XX c.c."
     - without calcifications: "Est. prostate volume about XX c.c."
4) Normal study rule:
   - If kidneys + bladder + prostate are unremarkable and no significant Others:
     - If prostate volume is pro

)
}



userPrompt =
(
Impression:
%I2F_Impression%
)

json := "{"
    . """model"": """ gModel ""","
    . """temperature"": 1,"
    . """messages"": ["
        . "{""role"": ""system"", ""content"": " . JEscape(sysPrompt) . "},"
        . "{""role"": ""user"", ""content"": " . JEscape(userPrompt) . "}"
    . "]"
    . "}"

resp := HttpPost(endpoint, json, API_KEY)
if (resp = "") {
    MsgBox, 16, Error, No response from API.
    return
}

content := ExtractContent(resp)
if (content = "") {
    MsgBox, 16, Error, Failed to parse API response.`n`n%resp%
    return
}

find := RegGet(content, "s)<<(?:FINDINGS)>>\s*(.*?)\s*(?=<<IMPRESSION>>|$)")
impr := RegGet(content, "s)<<IMPRESSION>>\s*(.*)$")

GuiControl, I2F:, I2F_Findings, % Trim(find)
GuiControl, I2F:, I2F_ImprOpt,  % Trim(impr)
return

; ---- Helpers ----
HttpPost(url, body, apiKey) {
    whr := ComObjCreate("WinHttp.WinHttpRequest.5.1")
    whr.Open("POST", url, false)
    whr.SetRequestHeader("Content-Type", "application/json; charset=utf-8")
    whr.SetRequestHeader("Authorization", "Bearer " apiKey)
    whr.SetTimeouts(60000, 60000, 60000, 60000)
    whr.Send(body)
    status := whr.Status
    if (status != 200) {
        responseText := whr.ResponseText
        return "HTTP " status "`n" responseText
    }
    return whr.ResponseText
}

; 修正後的代碼：
ExtractContent(json) {
    ; 尋找content字段
    if !RegExMatch(json, """content""\s*:\s*""((?:\\.|[^""\\])*)""", m)
        return ""
    
    txt := m1
    
    ; 正確的字符串替換方式
    txt := StrReplace(txt, "\r\n", "`n")
    txt := StrReplace(txt, "\n", "`n") 
    txt := StrReplace(txt, "\t", A_Tab)
    txt := StrReplace(txt, "\""", """")  ; 修正：使用 \"" 替換為 "
    txt := StrReplace(txt, "\\", "\")   ; 修正：反斜線轉義
    
    return txt
}

; 修正JEscape函數中的類似問題：
JEscape(s) {
    ; 先處理反斜線，再處理雙引號
    s := StrReplace(s, "\", "\\")
    s := StrReplace(s, """", "\""")     ; 這裡在字符串內部是安全的
    s := StrReplace(s, "`r`n", "\n")
    s := StrReplace(s, "`n", "\n")
    return """" . s . """"              ; 修正：使用字符串連接
}

RegGet(hay, pat) {
    if RegExMatch(hay, pat, m)
        return m1
    return ""
}

; ============================================================================
; End of AI Findings Generator
; ============================================================================
; ===========================================================================================
; 超音波 AI 分析整合模組
; 使用 WebBrowser 控件嵌入 HTML 並自動處理剪貼簿影像
; ===========================================================================================



; Win+U 快速鍵已移除，請使用 Win+Shift+U 啟動 AHK 版本的 AI 分析

; Win+Shift+U 快速鍵打開 AHK 視窗版 AI 分析
#+u::
    gosub ShowUSAIGUI
return



; ===========================================================================================
; AHK 視窗版超音波 AI 分析
; ===========================================================================================

; 全域變數
global USAI_CurrentImage := ""
global USAI_PreviousImage := ""
global USAI_APIKey := API_KEY2

; 熱字串觸發
::usaigui::
ShowUSAIGUI:  ; 修改 ShowUSAIGUI 標籤，使用雙欄式佈局
	Gui, USAIG:New, , 超音波 AI 分析 (Gemini 1.5 Pro)
    Gui, USAIG:Font, s10
    
    ; === 左側面板 (保持不變) ===
    Gui, USAIG:Add, GroupBox, x10 y10 w470 h60, API 設定 (Google Gemini)
    Gui, USAIG:Add, Text, x20 y30 w60, API Key:
    Gui, USAIG:Add, Edit, x85 y30 w380 h20 vUSAIAPIKey Password, %API_KEY2%
    
    ; ... (中間影像與 OCR 部分保持不變，略過以節省篇幅，請保留原本代碼 ...) ...
    Gui, USAIG:Add, GroupBox, x10 y80 w470 h100, 影像狀態
    Gui, USAIG:Add, Text, x20 y100 w220 h40 vUSAIImage1Status Center, 本次影像：未上傳`n點擊下方按鈕貼上影像
    Gui, USAIG:Add, Text, x250 y100 w220 h40 vUSAIImage2Status Center, 前次影像：未上傳`n點擊下方按鈕貼上影像
    Gui, USAIG:Add, Text, x20 y145 w220 h30 vUSAIOCR1Status, OCR: 尚未執行
    Gui, USAIG:Add, Text, x250 y145 w220 h30 vUSAIOCR2Status, OCR: 尚未執行
    Gui, USAIG:Add, Button, x20 y190 w220 h35 gUSAIPasteImage1, 貼上本次影像 (Ctrl+V)
    Gui, USAIG:Add, Button, x250 y190 w220 h35 gUSAIPasteImage2, 貼上前次影像 (Ctrl+V)
    Gui, USAIG:Add, Button, x20 y230 w220 h30 gUSAIExecuteOCR1, 執行 OCR (本次)
    Gui, USAIG:Add, Button, x250 y230 w220 h30 gUSAIExecuteOCR2, 執行 OCR (前次)
    Gui, USAIG:Add, GroupBox, x10 y270 w470 h250, OCR 辨識結果
    Gui, USAIG:Add, Edit, x20 y290 w220 h180 vUSAIOCR1Result Multi WantReturn VScroll
    Gui, USAIG:Add, Edit, x250 y290 w220 h180 vUSAIOCR2Result Multi WantReturn VScroll
    Gui, USAIG:Add, Button, x20 y475 w105 h30 gUSAICopyOCR1, 複製 OCR 1
    Gui, USAIG:Add, Button, x135 y475 w105 h30 gUSAIClearOCR1, 清除 OCR 1
    Gui, USAIG:Add, Button, x250 y475 w105 h30 gUSAICopyOCR2, 複製 OCR 2
    Gui, USAIG:Add, Button, x365 y475 w105 h30 gUSAIClearOCR2, 清除 OCR 2

; === 右側面板 (修改處) ===
	Gui, USAIG:Add, GroupBox, x490 y10 w400 h160, 分析選項 ; 高度稍微增加
    
    ; 1. 修改下拉選單：加入 gUSAIExamTypeChanged 標籤
    Gui, USAIG:Add, Text, x500 y30 w80 h23, 檢查部位:
    Gui, USAIG:Add, DropDownList, x580 y27 w300 vUSAIExamType gUSAIExamTypeChanged Choose1, Gemini 3 Thinking (Breast)||脊椎 (Spine, Thinking)|Ankle Foot 陳主任風格 Thinking| Chest x-ray (Thinking)|Knee Thinking|一般描述 (General)

    ; 2. 新增裁切選項 CheckBox (預設勾選，因為預設是 Breast)
    Gui, USAIG:Add, CheckBox, x580 y60 w250 h23 vUSAICropImage Checked, 啟用影像裁切 (去除上方資訊)

    ; 3. 原有的 Radio Buttons (位置稍微下移)
    Gui, USAIG:Add, Radio, x500 y90 w380 vUSAIChoice1 Checked, 僅本次影像
    Gui, USAIG:Add, Radio, x500 y110 w380 vUSAIChoice2, 同一病灶比較 (兩張)
    Gui, USAIG:Add, Radio, x500 y130 w380 vUSAIChoice3, 大小變化比較 (兩張)
    
    ; 分析按鈕位置下移
    Gui, USAIG:Add, Button, x590 y150 w200 h40 gUSAIAnalyze Default, 開始 Gemini 分析
    
    ; 分析結果框位置下移
    Gui, USAIG:Add, GroupBox, x490 y200 w400 h320, 分析結果
    Gui, USAIG:Add, Edit, x500 y220 w380 h290 vUSAIResult Multi WantReturn VScroll
    
    ; 結果操作按鈕 (位置微調)
    Gui, USAIG:Add, Button, x530 y530 w100 h35 gUSAIInsertResult, 插入報告
    Gui, USAIG:Add, Button, x640 y530 w100 h35 gUSAICopyResult, 複製結果
    Gui, USAIG:Add, Button, x750 y530 w100 h35 gUSAIClearResult, 清除結果
    
    Gui, USAIG:Add, Text, x10 y580 w880 h20 vUSAIStatus Center, 就緒 (Model: Gemini 1.5 Pro)
    
    Gui, USAIG:Show, w900 h610
return

USAIExamTypeChanged:
    Gui, USAIG:Submit, NoHide
    
    ; 判斷邏輯：如果是 Breast 或 Thyroid 通常需要裁切，其他則預設不裁切
    if (InStr(USAIExamType, "Breast") || InStr(USAIExamType, "Thyroid")) {
        GuiControl, USAIG:, USAICropImage, 1  ; 勾選
    } else {
        GuiControl, USAIG:, USAICropImage, 0  ; 取消勾選
    }
return

; ============================================================================
; OCR 結果格式化函數
; ============================================================================

; 將 OCR 辨識結果格式化為報告格式
; 輸入：location = "Rt(12/21)", dimension = "8.8*3.7"
; 輸出：Rt 10/6: 7.6*3.3mm.(Srs/Img:1/_) _
FormatOCRToReport(location, dimension, imgNum := "_") {
    ; 1. 處理側別 (Side)
    sideFormatted := "Rt"  ; 預設 Rt
    positionNumbers := "_/_"
    
    if (location != "") {
        if (InStr(location, "Lt")) {
            sideFormatted := "Lt"
        } else if (InStr(location, "Rt")) {
            sideFormatted := "Rt"
        }
        ; 擷取位置數字 (例如 10/6)
        if RegExMatch(location, "(\d+/\d+)", match) {
            positionNumbers := match1
        }
    }
    
    ; 2. 處理尺寸
    dimensionFormatted := "_x_"
    if (dimension != "") {
        dimensionFormatted := StrReplace(dimension, " mm", "")
        dimensionFormatted := StrReplace(dimensionFormatted, " ", "")
    }
    
    ; 3. 處理影像編號
    if (imgNum = "")
        imgNum := "_"
    
    ; 4. 組合輸出格式：Rt 10/6: 7.6*3.3mm.(Srs/Img:1/_) _
    result := sideFormatted . " " . positionNumbers . ": " . dimensionFormatted . "mm.(Srs/Img:1/" . imgNum . ") _"
    
    return result
}

; 新增：解析影像編號 (支援數字與 I)
MatchImageNumber(input) {
    ; 正則表達式解釋：
    ; (?:\(|^|\s)  -> 前面是括號、開頭或空白
    ; 1\s*/\s* -> 匹配 "1/" (允許中間有空白)
    ; ([0-9I]+)    -> 捕獲群組：匹配數字 0-9 或大寫字母 I (出現一次以上)
    ; (?:\)|$|\s)  -> 後面是括號、結尾或空白
    
    if RegExMatch(input, "(?:\(|^|\s)1\s*/\s*([0-9I]+)(?:\)|$|\s)", match) {
        return match1
    }
    return "_"
}

; 貼上本次影像
USAIPasteImage1:
    USAI_CurrentImage := GetClipboardImageAndSave("current")
    if (USAI_CurrentImage != "") {
        FormatTime, timeString, , yyyy-MM-dd HH:mm:ss
        GuiControl, USAIG:, USAIImage1Status, 本次影像：已上傳`n%timeString%
        GuiControl, USAIG:, USAIStatus, 本次影像已成功貼上
        GuiControl, USAIG:, USAIOCR1Status, OCR: 待執行
        
        ; 自動執行 OCR
        Gosub, USAIExecuteOCR1
    } else {
        GuiControl, USAIG:, USAIStatus, 錯誤：剪貼簿中沒有找到影像
    }
return

; 貼上前次影像
USAIPasteImage2:
    USAI_PreviousImage := GetClipboardImageAndSave("previous")
    if (USAI_PreviousImage != "") {
        FormatTime, timeString, , yyyy-MM-dd HH:mm:ss
        GuiControl, USAIG:, USAIImage2Status, 前次影像：已上傳`n%timeString%
        GuiControl, USAIG:, USAIStatus, 前次影像已成功貼上
        GuiControl, USAIG:, USAIOCR2Status, OCR: 待執行
        
        ; 自動執行 OCR
        Gosub, USAIExecuteOCR2
    } else {
        GuiControl, USAIG:, USAIStatus, 錯誤：剪貼簿中沒有找到影像
    }
return

; 執行 OCR (本次影像)
USAIExecuteOCR1:
    if (!FileExist(A_Temp . "\usai_current.png")) {
        GuiControl, USAIG:, USAIStatus, 錯誤：找不到本次影像檔案
        return
    }
    
    GuiControl, USAIG:, USAIStatus, 正在執行 OCR...
    
    ; 創建用於 OCR 的裁切影像（只保留下方 20%）
    ocrImagePath := A_Temp . "\usai_current_ocr.png"
    success := CropImage(A_Temp . "\usai_current.png", ocrImagePath, 20, true)
    
    if (!success) {
        GuiControl, USAIG:, USAIStatus, 錯誤：無法裁切影像
        return
    }
    
    ; 對裁切後的影像執行 OCR
    ocrResult := PerformOCR(ocrImagePath, 2)
    
    ; 刪除臨時 OCR 影像
    FileDelete, %ocrImagePath%
    
    if (ocrResult != "") {
		; 解析結果
        breastLocation := MatchBreastLocation_method2(ocrResult)
        dimension := MatchDimension(ocrResult)
        
        ; [新增] 解析影像編號
        imgNum := MatchImageNumber(ocrResult)
        
        ; [修改] 傳入 imgNum
        reportFormat := FormatOCRToReport(breastLocation, dimension, imgNum)
        
        ; 顯示原始 + 格式化結果
        displayText := "原始: " . ocrResult . "`n`n"
        displayText .= "報告格式:`n" . reportFormat
        
        GuiControl, USAIG:, USAIOCR1Result, %displayText%
        
        ; 儲存格式化結果供後續使用
        USAI_CurrentOCRText := reportFormat
        
        ; 更新狀態
        ocrStatusText := "OCR: 完成 (下方20" . "%)"
        GuiControl, USAIG:, USAIOCR1Status, %ocrStatusText%
        GuiControl, USAIG:, USAIStatus, OCR 執行完成
    } else {
        GuiControl, USAIG:, USAIOCR1Status, OCR: 失敗
        GuiControl, USAIG:, USAIStatus, OCR 執行失敗
    }
return

; 執行 OCR (前次影像)
USAIExecuteOCR2:
    if (!FileExist(A_Temp . "\usai_previous.png")) {
        GuiControl, USAIG:, USAIStatus, 錯誤：找不到前次影像檔案
        return
    }
    
    GuiControl, USAIG:, USAIStatus, 正在執行 OCR...
    
    ; 創建用於 OCR 的裁切影像
    ocrImagePath := A_Temp . "\usai_previous_ocr.png"
    success := CropImage(A_Temp . "\usai_previous.png", ocrImagePath, 20, true)
    
    if (!success) {
        GuiControl, USAIG:, USAIStatus, 錯誤：無法裁切影像
        return
    }
    
    ; 執行 OCR
    ocrResult := PerformOCR(ocrImagePath, 2)
    
    ; 刪除臨時檔案
    FileDelete, %ocrImagePath%
    
    if (ocrResult != "") {
		breastLocation := MatchBreastLocation_method2(ocrResult)
        dimension := MatchDimension(ocrResult)
        
        ; [新增] 解析影像編號
        imgNum := MatchImageNumber(ocrResult)
        
        ; [修改] 傳入 imgNum
        reportFormat := FormatOCRToReport(breastLocation, dimension, imgNum)
        
        ; 顯示原始 + 格式化結果
        displayText := "原始: " . ocrResult . "`n`n"
        displayText .= "報告格式:`n" . reportFormat
        
        GuiControl, USAIG:, USAIOCR2Result, %displayText%
        
        ; 儲存格式化結果
        USAI_PreviousOCRText := reportFormat
        
        ; 更新狀態
        ocrStatusText := "OCR: 完成 (下方20" . "%)"
        GuiControl, USAIG:, USAIOCR2Status, %ocrStatusText%
        GuiControl, USAIG:, USAIStatus, OCR 執行完成
    } else {
        GuiControl, USAIG:, USAIOCR2Status, OCR: 失敗
        GuiControl, USAIG:, USAIStatus, OCR 執行失敗
    }
return


; 獲取剪貼簿中的影像並儲存
GetClipboardImageAndSave(imageType) {
    ; 檢查剪貼簿是否有影像
    if !DllCall("IsClipboardFormatAvailable", "uint", 2) {
        return ""
    }
    
    if !DllCall("OpenClipboard", "ptr", 0) {
        return ""
    }
    
    hBitmap := DllCall("GetClipboardData", "uint", 2, "ptr")
    if (!hBitmap) {
        DllCall("CloseClipboard")
        return ""
    }
    
    ; 儲存完整原始影像 (作為備份與 OCR 使用)
    tempFile := A_Temp . "\usai_" . imageType . ".png"
    success := SaveBitmapToPNG(hBitmap, tempFile)
    
    DllCall("CloseClipboard")
    
    if (success) {
        aiImagePath := A_Temp . "\usai_" . imageType . "_ai.png"
        
        ; === [修改開始] 判斷是否需要裁切 ===
        ; 取得 GUI CheckBox 的狀態 (變數名稱: USAICropImage)
        ; 注意：必須指定視窗名稱 USAIG:
        GuiControlGet, doCrop, USAIG:, USAICropImage
        
        if (doCrop) {
            ; 如果勾選：執行裁切 (保留下方 90%)
            CreateAIImage(tempFile, aiImagePath, 90)
        } else {
            ; 如果未勾選：直接複製原始檔案作為 AI 影像
            FileCopy, %tempFile%, %aiImagePath%, 1
        }
        ; === [修改結束] ===
        
        ; 返回影像的 base64
        base64 := B64EncodeFile(aiImagePath)
        
        ; 刪除 AI 用的臨時檔案 (原始檔 tempFile 留著給 OCR 用)
        FileDelete, %aiImagePath%
        
        if (base64 != "") {
            return "data:image/png;base64," . base64
        }
    }
    
    return ""
}

; 儲存 Bitmap 為 PNG 檔案
SaveBitmapToPNG(hBitmap, filePath) {
    ; 嘗試使用 GDI+ 方法
    if IsFunc("Gdip_Startup") {
        pToken := Gdip_Startup()
        if (!pToken) {
            return false
        }
        
        pBitmap := Gdip_CreateBitmapFromHBITMAP(hBitmap)
        if (!pBitmap) {
            Gdip_Shutdown(pToken)
            return false
        }
        
        ; 保存為 PNG 檔案
        result := Gdip_SaveBitmapToFile(pBitmap, filePath)
        Gdip_DisposeImage(pBitmap)
        Gdip_Shutdown(pToken)
        
        return (result = 0)
    }
    
    ; 備用方法：使用系統功能
    ; 這裡可以添加其他儲存方法
    return false
}

; 執行 OCR
PerformOCR(imagePath, method := 2) {
    global tess_exe  ; 只聲明，不賦值
    
    ; 檢查檔案是否存在
    if (tess_exe = "" || !FileExist(tess_exe)) {
        return ""
    }
    
    ; 設定 OCR whitelist
    if (method = 1) {
        whitelist := """LRt 0123456789()/"""
    } else {
        whitelist := """abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789./()"""
    }
    
    ; 輸出檔案路徑
    outputFile := A_Temp . "\ocrout"
    ; === [修改重點] ===
    ; 改用 --psm 6 (統一文字區塊)，這能同時支援多行(圖1)與單行(圖2)
    ; 不要用 --psm 7 (那是強制單行)
    cmd := tess_exe . " """ . imagePath . """ """ . outputFile . """ --psm 6 -c tessedit_char_whitelist=" . whitelist
	
    try {
	RunWait, %cmd%,, Hide
    } catch e {
        return ""
    }

    ; 讀取結果
    ocrResult := ""
    FileRead, ocrResult, %outputFile%.txt
    
    ; 清理臨時檔案
    FileDelete, %outputFile%.txt
    
    return Trim(ocrResult)
}

; 解析乳房位置 (新機器方法)
MatchBreastLocation_method2(input) {
    ; 替換 O 為 0
    input := StrReplace(input, "O", "0")
    
    ; 方法1：原本的格式 "Left 2 H 1 cm"
    r1 := "(Left|Right)\s*(\d+)\s*H\s*(\d+)\s*cm"
    FoundPos := RegExMatch(input, r1, match)
    
    if (FoundPos > 0) {
        side := ""
        if (match1 = "Left") {
            side := "Lt"
        } else if (match1 = "Right") {
            side := "Rt"
        }
        
        if (match2 != "" and match3 != "") {
            return side . "(" . match2 . "/" . match3 . ")"
        }
    }
    
    ; 方法2：新格式 "Lt 11/3" 或 "Rt 7/0"
    r2 := "(Lt|Rt)\s*(\d+)\s*/\s*(\d+)"
    FoundPos := RegExMatch(input, r2, match)
    
    if (FoundPos > 0) {
        return match1 . "(" . match2 . "/" . match3 . ")"
    }
    
    ; 方法3：更寬鬆的格式，支援 L、R 縮寫
    r3 := "(L|R|Lt|Rt)\s*(\d+)\s*/\s*(\d+)"
    FoundPos := RegExMatch(input, r3, match)
    
    if (FoundPos > 0) {
        side := match1
        if (side = "L") 
            side := "Lt"
        else if (side = "R")
            side := "Rt"
        return side . "(" . match2 . "/" . match3 . ")"
    }
    
    return ""
}

; 解析尺寸
MatchDimension(input, mutfactor := 1, pickbiggest := false) {
    retval := ""
    oldmutfactor := mutfactor
    
	; === [修改重點 1] ===
    ; 針對 Dist A / Dist B 同時出現的情況
    ; 加入 "s)" 選項：讓中間的 .* 可以跨越換行符號 (解決圖1上下排列的問題)
    ; 加入 "i)" 選項：不分大小寫 (預防 OCR 辨識成小寫)
    ; 格式: is)Dist\s*A...
	
	
    ; 先嘗試匹配 "Dist A 11.3 mm Dist B 5.0 mm" 格式
    ;if (RegExMatch(input, "Dist\s*A\s*([\d.]+)\s*mm.*Dist\s*B\s*([\d.]+)\s*mm", match)) {
    ;    return match1 . "*" . match2
    ;}
if (RegExMatch(input, "is)Dist\s*A\s*([\d.]+)\s*mm.*?Dist\s*B\s*([\d.]+)\s*mm", match)) {
        return match1 . "*" . match2
    }
    
    ; === [修改重點 2] ===
    ; 針對只有 Dist A 的情況 (備用)
    if (RegExMatch(input, "is)Dist\s*A\s*([\d.]+)\s*mm", match)) {
        return match1
    }
    
    ; 原本的通用邏輯作為最後備用 (保持不變)
    Loop {
        r := "((\d| )+\.?(\d| )+\D*)(mm|cm)"
        FoundPos := RegExMatch(input, r, match)
        if (FoundPos = 0) {
            break
        }
        
        if (match4 = "cm") {
            mutfactor := oldmutfactor * 10
        }
        
        if (!pickbiggest) {
            if (retval != "") {
                retval := Trim(retval) . "*"
            }
            match1 := StrReplace(match1, " ", "")
            match1 := (match1 + 0.0) * mutfactor
            match1 := Round(match1, 1)
            retval := retval . match1
        } else {
            match1 := (match1 + 0.0) * mutfactor
            match1 := Round(match1, 1)
            if (retval = "" or retval < match1) {
                retval := match1
            }
        }
        
        input := SubStr(input, FoundPos + StrLen(match))
    }
    
    return retval
}
    
    ; 嘗試匹配單一 "Dist A 10.0 mm" 格式
    ;if (RegExMatch(input, "Dist\s*A\s*([\d.]+)\s*mm", match)) {
    ;    return match1
    ;}
    
    ; 原本的邏輯作為備用
    ;Loop {
    ;    r := "((\d| )+\.?(\d| )+\D*)(mm|cm)"
    ;    FoundPos := RegExMatch(input, r, match)
    ;    if (FoundPos = 0) {
    ;        break
    ;    }
;        if (match4 = "cm") {
 ;           mutfactor := oldmutfactor * 10
  ;      }
;        if (!pickbiggest) {
 ;           if (retval != "") {
  ;              retval := Trim(retval) . "*"
   ;         }
    ;        match1 := StrReplace(match1, " ", "")
     ;       match1 := (match1 + 0.0) * mutfactor
      ;      match1 := Round(match1, 1)
       ;     retval := retval . match1
     ;   } else {
    ;        match1 := (match1 + 0.0) * mutfactor
   ;         match1 := Round(match1, 1)
  ;          if (retval = "" or retval < match1) {
 ;               retval := match1
;            }
    ;    }
    ;    input := SubStr(input, FoundPos + StrLen(match))
    ;}
    
    ;return retval

; 開始分析 (整合 OCR 結果)
USAIAnalyze:
	Gui, USAIG:Submit, NoHide
    
    if (USAIAPIKey = "") {
        GuiControl, USAIG:, USAIStatus, 錯誤：請輸入 Google API Key
        return
    }
        
    ; 檢查影像
    if (USAIChoice1 && USAI_CurrentImage = "") {
        GuiControl, USAIG:, USAIStatus, 錯誤：請先貼上本次影像
        return
    }
    if ((USAIChoice2 || USAIChoice3) && (USAI_CurrentImage = "" || USAI_PreviousImage = "")) {
        GuiControl, USAIG:, USAIStatus, 錯誤：請先貼上兩張影像
        return
    }
    
    GuiControl, USAIG:Disable, 開始 Gemini 分析
    GuiControl, USAIG:, USAIStatus, 正在呼叫 Gemini 3 Thinking...
    
    ; === 1. 設定 Prompt 與 Thinking 模式 ===
    SysPrompt := ""
    useThinking := false
    
    ; 判斷是否使用 Thinking 模式 (根據下拉選單名稱)
	if (InStr(USAIExamType, "Thinking")) {
        useThinking := true
        SysPrompt := "Analyze the image with high reasoning effort."
    } else {
        SysPrompt := ""
    }
    
    if (InStr(USAIExamType, "Breast")) {
        SysPrompt .= "You are a radiologist assistant specializing in Breast Ultrasound. "
        SysPrompt .= "Analyze the ultrasound image. Focus on: shape, orientation, margin, echo pattern, posterior features, and calcifications. "
        SysPrompt .= "Provide a concise description suitable for a medical report."
    } else if (InStr(USAIExamType, "Spine")) {
	; ---------------------------------------------------------
	; GEMINI RADIOLOGY PROMPT - VISUAL GEOMETRY EDITION
	; ---------------------------------------------------------
	SysPrompt := "You are an expert Radiologist and Biomechanical Analyst. Analyze the Spine X-ray."
	SysPrompt .= " Your goal is to output a clean, plain-text report in TELEGRAPHIC DIAGNOSTIC style."

	SysPrompt .= " `n`n**PHASE 1: ANATOMY & COUNTING (The Anchor):**"
	SysPrompt .= " `n- **C-Spine:** Start at C2, count DOWN to C7."
	SysPrompt .= " `n- **L-Spine:** Identify **Sacrum** (base). The vertebra directly above is **L5**. Count **UPWARDS** (L5->L4->L3->L2->L1)."

	SysPrompt .= " `n`n**PHASE 2: VISUAL GEOMETRY & CALCULATION (Precision Mode):**"
	SysPrompt .= " `n**Step A: Endplate Coordinate Extraction:**"
	SysPrompt .= " `n- For each vertebral level, visually identify four distinct 'Corner Points' (Anterior/Posterior Superior & Anterior/Posterior Inferior)."
	SysPrompt .= " `n- Define the **Endplate Line** by connecting the Anterior and Posterior corners."

	SysPrompt .= " `n`n**Step B: INTERVERTEBRAL ANGLE MEASUREMENT:**"
	SysPrompt .= " `n- **Method:** Measure the angle formed between the **Inferior Endplate** of the upper vertebra and the **Superior Endplate** of the lower vertebra."
	SysPrompt .= " `n- **Execution:** Internally calculate the vector slope for each line based on the corner points to determine the angle in degrees."

	SysPrompt .= " `n`n**Step C: DIAGNOSTIC CRITERIA:**"
	SysPrompt .= " `n**1. FRACTURE CHECK (L1/L2):**"
	SysPrompt .= " `n- Compare Anterior vs. Posterior body height using the extracted corner points."
	SysPrompt .= " `n- **Threshold:** If Anterior height < 80% of Posterior height (>20% loss), DIAGNOSE as **'Compression fracture'**."
	
	SysPrompt .= " `n**2. ANGULAR INSTABILITY (Dynamic/Static):**"
	SysPrompt .= " `n- Compare the calculated Intervertebral Angle against normal ranges."
	SysPrompt .= " `n- **Static Kyphosis:** If the angle is inverted (Kyphotic > 5-10 degrees) where it should be Lordotic, flag it."
	SysPrompt .= " `n- **Dynamic Instability:** In Flexion/Extension views, if the angular change at a single level is **>11 degrees** (C-spine) or **>15 degrees** (L-spine), DIAGNOSE as **'Angular Instability'**."

	SysPrompt .= " `n`n**PHASE 3: COMMON CHECKS:**"
	SysPrompt .= " `n1. **Listhesis:** Check for Translation (sliding) of posterior vertebral bodies. Report Grade I-IV."
	SysPrompt .= " `n2. **Bone Density:** Check for washed-out gray scale (Osteopenia)."
	SysPrompt .= " `n3. **Aorta:** Check for calcification anterior to L-spine."

	SysPrompt .= " `n`n**REQUIRED OUTPUT STRUCTURE (Strict):**"
	SysPrompt .= " `n(Block 1: Alignment & Stability)"
	SysPrompt .= " `n[Line 1: Lordosis (e.g., 'Straightening of cervical curvature')]"
	SysPrompt .= " `n[Line 2: Listhesis (e.g., 'Grade I anterolisthesis C4-C5')]"
	SysPrompt .= " `n[Line 3: Stability/Angles (e.g., 'C3-C4 Kyphotic angulation ~12 deg - Suggests instability')]"
	SysPrompt .= " `n"
	SysPrompt .= " `n(Block 2: Fracture, Discs & Bones)"
	SysPrompt .= " `n[Line 1: Fracture (e.g., 'L2 compression fracture') - Omit if normal]"
	SysPrompt .= " `n[Line 2: Disc Findings (e.g., 'C5/6 disc space narrowing')]"
	SysPrompt .= " `n[Line 3: Bone Density]"
	SysPrompt .= " `n[Line 4: Vertebral Shape]"
	SysPrompt .= " `n"
	SysPrompt .= " `n(Block 3: Joints & Soft Tissues)"
	SysPrompt .= " `n[Line 1: Joints]"
	SysPrompt .= " `n[Line 2: Aorta/Soft Tissue]"
	SysPrompt .= " `n"
	SysPrompt .= " `n(Block 4: Summary)"
	SysPrompt .= " `n[Single concise summary line]"
    } else if (InStr(USAIExamType, "CXR")) {
	SysPrompt := "You are an expert Board-Certified Radiologist. Analyze the Chest X-ray."
	SysPrompt .= " Your goal is to output a clean, plain-text report in TELEGRAPHIC DIAGNOSTIC style matching specific templates. NO Markdown formatting in the final text (no bold, no italics). Use hyphens '- ' for each line."

	SysPrompt .= " `n`n**PHASE 1: ANATOMY & QUALITY CHECK (Internal):**"
	SysPrompt .= " `n- Assess if the patient is Pediatric or Adult."
	SysPrompt .= " `n- Assess if the patient shows signs of aging (Osteophytes, Aortic Calcification)."

	SysPrompt .= " `n`n**PHASE 2: ANALYSIS LOGIC (Strictly Follow Priority):**"

	SysPrompt .= " `n**1. LUNGS (The Anchor):**"
	SysPrompt .= " `n   - **NORMAL (Default):** Output exactly **'- No active lung lesion is noted.'**"
	SysPrompt .= " `n   - **Infiltration:** '- Mild infiltration in [Location], could be pneumonia or others.'"
	SysPrompt .= " `n   - **Consolidation:** '- Consolidation in [Location], could be pneumonia or others.'"
	SysPrompt .= " `n   - **Emphysema:** '- Emphysematous change of both lungs.'"
	SysPrompt .= " `n   - **Congestion:** '- Mild pulmonary congestion pattern.'"
	SysPrompt .= " `n   - **TB/Old:** '- Fibrocalcified change in both upper lungs, suspect old infection/inflammatory changes, eg. old TB or others.'"

	SysPrompt .= " `n**2. HEART:**"
	SysPrompt .= " `n   - **NORMAL:** **'- Normal heart size.'**"
	SysPrompt .= " `n   - **ENLARGED:** **'- Cardiomegaly.'**"
	SysPrompt .= " `n   - **BORDERLINE:** '- Borderline cardiomegaly.'"

	SysPrompt .= " `n**3. AORTA & MEDIASTINUM:**"
	SysPrompt .= " `n   - **Calcification (High Probability in Adults):** **'- Intimal calcification of aorta.'**"
	SysPrompt .= " `n   - **Tortuosity:** '- Tortuous aorta with intimal calcification.'"
	SysPrompt .= " `n   - **Widening:** '- Mild mediastinal widening.'"

	SysPrompt .= " `n**4. BONES (Spine & Density):**"
	SysPrompt .= " `n   - **IF YOUNG/NORMAL:** Output **'- Unremarkable bony structure.'**"
	SysPrompt .= " `n   - **IF ADULT/ELDERLY (Default for Age >50):**"
	SysPrompt .= " `n     a. **Spine:** **'- Degenerative change and spur formation of spine.'**"
	SysPrompt .= " `n     b. **Density (Mild):** **'- Generalized diminished bone density.'**"
	SysPrompt .= " `n     c. **Density (Severe):** '- Osteoporotic change of visible bony structures.'"

	SysPrompt .= " `n**5. OTHERS (Only if present):**"
	SysPrompt .= " `n   - **Stomach:** '- Distended stomach.'"
	SysPrompt .= " `n   - **Pleura:** '- Bilateral apical pleural thickening.'"
	SysPrompt .= " `n   - **Tubes:** '- Status post nasogastric tube insertion with tip in stomach.'"

	SysPrompt .= " `n`n**REQUIRED OUTPUT STRUCTURE:**"
	SysPrompt .= " `n(Output strictly as a list of lines starting with '- ')"
	SysPrompt .= " `n[Line 1: Lungs]"
	SysPrompt .= " `n[Line 2: Heart]"
	SysPrompt .= " `n[Line 3: Aorta (Skip if young/normal)]"
	SysPrompt .= " `n[Line 4: Mediastinum (Optional)]"
	SysPrompt .= " `n[Line 5: Spine/Bones (Select ONE: 'Unremarkable' OR 'Degenerative' + 'Density')]"
	SysPrompt .= " `n[Line 6: Others (Optional)]"
	
	
    } else if (InStr(USAIExamType, "Foot")) {
	; =================================================================================
	; Gemini Pro Prompt for Foot/Ankle X-ray (Dr. Style Optimized)
	; =================================================================================

	SysPrompt .= "You are an expert Board-Certified Radiologist specialized in Foot & Ankle imaging."
	SysPrompt .= " Your goal is to output a clean, plain-text report in TELEGRAPHIC DIAGNOSTIC style. NO Markdown. NO Bullet points."

	SysPrompt .= " `n`n**PHASE 1: ANATOMY & VIEW RECOGNITION:**"
	SysPrompt .= " `n- Identify if the image is **Ankle** or **Foot**."
	SysPrompt .= " `n- If the image is unrelated (e.g., Spine, Chest, Knee), output 'Non-target anatomy' and STOP."

	SysPrompt .= " `n`n**PHASE 2: TRAUMA & POST-OP CHECK (HIGHEST PRIORITY):**"
	SysPrompt .= " `n- **Hardware:** Look for Plates, Screws, Pins, or Intramedullary Nails."
	SysPrompt .= " `n- **Union Status (CRITICAL):** If hardware or old fracture is present, you MUST classify healing status as:"
	SysPrompt .= " `n  1. 'With bone union' (Fully healed)"
	SysPrompt .= " `n  2. 'With callus formation and near bone union' (Healing)"
	SysPrompt .= " `n  3. 'Without bone union' (Non-union/Delayed)"
	SysPrompt .= " `n- **Fractures:** If acute, specify type (e.g., 'Trimalleolar', 'Avulsion', 'Spiral')."

	SysPrompt .= " `n`n**PHASE 3: SPECIFIC ANATOMY CHECKLIST:**"

	SysPrompt .= " `n`n**(IF ANKLE):**"
	SysPrompt .= " `n1. **Malleoli:** Check Medial, Lateral, and Posterior malleoli."
	SysPrompt .= " `n2. **Talar Dome:** Check for Osteochondral lesions (OCD) or 'Vagus deformity'."
	SysPrompt .= " `n3. **Accessory Bones:** Distinguish 'Os trigonum' or 'Os subfibulare' from fractures."
	SysPrompt .= " `n4. **Soft Tissue:** Report location of swelling (e.g., 'Soft tissue swelling around lateral malleolus')."

	SysPrompt .= " `n`n**(IF FOOT):**"
	SysPrompt .= " `n1. **Navicular:** Check for compression/sclerosis indicative of **'Mueller-Weiss disease'**."
	SysPrompt .= " `n2. **Calcaneus:** Check for **'Plantar spur'** or **'Haglund deformity'** (posterior superior prominence)."
	SysPrompt .= " `n3. **5th Metatarsal:** Check base for Jones/Avulsion fracture."
	SysPrompt .= " `n4. **Alignment:** Check for Hallux Valgus or Pes Planus."

	SysPrompt .= " `n`n**PHASE 4: REPORTING STYLE RULES:**"
	SysPrompt .= " `n1. **Phrasing:** Use 'Status post [procedure] with/without [finding]'. Example: 'Fracture of lateral malleolus status post screw fixation with bone union.'"
	SysPrompt .= " `n2. **Tone:** Direct and definitive. Avoid 'I think' or 'Possible'. Use 'suggestive of' only if uncertain."
	SysPrompt .= " `n3. **Negative Findings:** Only mention relevant negatives (e.g., 'No evident bone lesion')."

	SysPrompt .= " `n`n**REQUIRED OUTPUT STRUCTURE:**"

	SysPrompt .= " `n(Block 1: Primary Diagnosis / Trauma)"
	SysPrompt .= " `n[Line 1: Major Finding (e.g., 'Trimalleolar fracture status post plate fixation') or 'No acute fracture']"
	SysPrompt .= " `n[Line 2: Healing Status (e.g., 'With callus formation and near bone union') - Omit if normal]"
	SysPrompt .= " `n"
	SysPrompt .= " `n(Block 2: Secondary Findings & Degeneration)"
	SysPrompt .= " `n[Line 1: Bone Lesions/Deformity (e.g., 'Mueller-Weiss disease considered' or 'Plantar calcaneal spur')]"
	SysPrompt .= " `n[Line 2: Joints (e.g., 'Tibiotalar osteoarthritis' or 'Joint space narrowing')]"
	SysPrompt .= " `n"
	SysPrompt .= " `n(Block 3: Soft Tissues & Others)"
	SysPrompt .= " `n[Line 1: Soft Tissue (e.g., 'Lateral ankle swelling')]"
	SysPrompt .= " `n[Line 2: Accessory Bones (e.g., 'Prominent os trigonum')]"
	SysPrompt .= " `n"
	SysPrompt .= " `n(Block 4: Summary)"
	SysPrompt .= " `n[Single concise summary line]"
    } else if (InStr(USAIExamType, "Knee")) {
	SysPrompt .= "You are an expert Board-Certified Radiologist. Analyze the Knee X-ray."
	SysPrompt .= " Your goal is to output a clean, plain-text report in TELEGRAPHIC DIAGNOSTIC style. NO Markdown. NO Bullet points."

	SysPrompt .= " `n`n**PHASE 1: ANATOMY & VIEW RECOGNITION:**"
	SysPrompt .= " `n- Identify if the image shows Right, Left, or Bilateral Knees."
	SysPrompt .= " `n- Identify if post-surgical implants (TKA) are present."
	SysPrompt .= " `n- **CRITICAL:** Ignore any non-knee anatomy (e.g., faint spine or pelvis parts) unless clinically significant to the knee."

	SysPrompt .= " `n`n**PHASE 2: SPECIFIC ANALYSIS LOGIC:**"

	SysPrompt .= " `n`n**(1. FRACTURE & DISLOCATION CHECK):**"
	SysPrompt .= " `n- Scan femur, tibia, fibula, and patella for fracture lines."
	SysPrompt .= " `n- **If Normal:** Output 'No obvious evidence of displaced bony fracture. No obvious joint dislocation.'"
	SysPrompt .= " `n- **If Fracture:** Describe location, type (e.g., 'Non-displaced', 'Comminuted'), and union status (e.g., 'Without bone union', 'Healing fracture')."

	SysPrompt .= " `n`n**(2. OSTEOARTHRITIS (OA) ASSESSMENT - MANDATORY):**"
	SysPrompt .= " `n- **Detection:** Look for osteophytes, joint space narrowing, and subchondral sclerosis."
	SysPrompt .= " `n- **GRADING (Must use 'Kellgren & Lawrence system'):**"
	SysPrompt .= " `n  - **Grade I:** Doubtful narrowing, possible osteophytic lipping."
	SysPrompt .= " `n  - **Grade II:** Definite osteophytes, possible narrowing."
	SysPrompt .= " `n  - **Grade III:** Moderate multiple osteophytes, definite narrowing, some sclerosis."
	SysPrompt .= " `n  - **Grade IV:** Large osteophytes, marked narrowing, severe sclerosis."
	SysPrompt .= " `n- **Standard Phrase:** 'OA in [side] knee. Kellgren & Lawrence system, grade [I-IV].'"

	SysPrompt .= " `n`n**(3. PATELLA & ALIGNMENT):**"
	SysPrompt .= " `n- Check for Patellar Tilt (especially on Merchant/Skyline view)."
	SysPrompt .= " `n- **If Normal:** 'No obvious patellar tilt or patellar subluxation.'"
	SysPrompt .= " `n- **If Abnormal:** 'Lateral tilting of patella.'"

	SysPrompt .= " `n`n**(4. SOFT TISSUE & BONE MATRIX):**"
	SysPrompt .= " `n- **Effusion:** Check suprapatellar pouch. If ANY fluid is suspected, output 'Mild joint effusion' (This is a high-frequency finding)."
	SysPrompt .= " `n- **Bone Density:** Check for 'Disuse osteoporosis' or 'Probably osteoporosis'."

	SysPrompt .= " `n`n**PHASE 3: OUTPUT STRUCTURE & STYLE RULES:**"
	SysPrompt .= " `n1. **Telegraphic Style:** Use short phrases. (e.g., 'Facet arthrosis' instead of 'There is facet arthrosis')."
	SysPrompt .= " `n2. **No Comparisons:** Do NOT mention 'Comparing with previous study'."
	SysPrompt .= " `n3. **Sequence:** Fracture/Implant -> OA/Degeneration -> Patella -> Soft Tissue."

	SysPrompt .= " `n`n**REQUIRED OUTPUT TEMPLATE (Examples):**"
	SysPrompt .= " `n(Example 1 - Normal/Mild):"
	SysPrompt .= " `n'No obvious evidence of displaced bony fracture. No obvious joint dislocation. No obvious patellar tilt. Mild joint effusion.'"
	SysPrompt .= " `n(Example 2 - OA):"
	SysPrompt .= " `n'OA in right knee. Kellgren & Lawrence system, grade III. Joint space narrowing, osteophyte formation of patellofemoral joint. Mild joint effusion. Disuse osteoporosis.'"
	SysPrompt .= " `n(Example 3 - Fracture):"
	SysPrompt .= " `n'Non-displaced fracture of patella. Without bone union. Mild joint effusion. Soft tissue swelling.'"

    } else {
        SysPrompt := "You are a helpful radiologist assistant. Describe the medical image findings concisely in English. "
    }
	; === 2. 構建 User Prompt ===
    UserPrompt := ""
    images := []
    
    ; 構建 UserPrompt 的邏輯 (包含 OCR) 保持不變
	if (USAIChoice1) {
        UserPrompt := SysPrompt . "`n`nPlease analyze this image."
        if (USAI_CurrentOCRText != "") {
            UserPrompt .= "`nOCR Data: " . USAI_CurrentOCRText
        }
        UserPrompt .= "`nOutput format: Location, Size, Description, Impression. (In English)"
        images.Push(USAI_CurrentImage)
    } else if (USAIChoice2) {
        UserPrompt := SysPrompt . "`n`nAnalyze these TWO images of the SAME lesion."
        if (USAI_CurrentOCRText != "" || USAI_PreviousOCRText != "") {
             UserPrompt .= "`nOCR Data - Current: " . USAI_CurrentOCRText . ", Previous: " . USAI_PreviousOCRText
        }
        UserPrompt .= "`nOutput format (Single line): Location, Size, Description, Comparison findings. (In English)"
        images.Push(USAI_CurrentImage)
        images.Push(USAI_PreviousImage)
    } else if (USAIChoice3) {
        UserPrompt := SysPrompt . "`n`nCompare size change. Image 1 is PREVIOUS, Image 2 is CURRENT."
        if (USAI_CurrentOCRText != "" || USAI_PreviousOCRText != "") {
             UserPrompt .= "`nOCR Data - Previous: " . USAI_PreviousOCRText . ", Current: " . USAI_CurrentOCRText
        }
        UserPrompt .= "`nOutput format (Single line): Location, Size change, Brief description. (In English)"
        images.Push(USAI_PreviousImage)
        images.Push(USAI_CurrentImage)
    }
	
    ; === 3. 呼叫 Gemini API (傳入 useThinking 參數)(非同步) ===
    ; 注意：這裡我們改用 gemini-2.0-flash-thinking-exp (或 gemini-3.0-pro-exp)
    modelID := "gemini-3-pro-preview"
    ; 呼叫背景工作函數
    StartGeminiBackgroundJob(USAIAPIKey, modelID, UserPrompt, images, useThinking)
    
    ; 啟動計時器，每 1 秒檢查一次結果
    SetTimer, CheckGeminiResult, 1000
return

;    result := CallGeminiVision(USAIAPIKey, modelID, UserPrompt, images, useThinking)
;    GuiControl, USAIG:Enable, 開始 Gemini 分析
;    if (result != "") {
;        GuiControl, USAIG:, USAIResult, %result%
;        GuiControl, USAIG:, USAIStatus, 分析完成！
;    } else {
;        GuiControl, USAIG:, USAIStatus, 分析失敗
;    }
;return

CheckGeminiResult:
    resultFile := A_Temp . "\gemini_response.txt"
    
    ; 檢查結果檔案是否存在
    if (FileExist(resultFile)) {
        ; 停止計時器
        SetTimer, CheckGeminiResult, Off
        
        ; 讀取結果 (指定 UTF-8 編碼)
        FileRead, resultText, *P65001 %resultFile%
        
        ; 更新 GUI
        GuiControl, USAIG:Enable, 開始 Gemini 分析
        
        if (resultText != "" && !InStr(resultText, "API Error")) {
            ; 嘗試解析 JSON 回應 (如果是直接存文字則不需要)
            finalResult := ParseGeminiResponse(resultText)
            
            ; 如果解析失敗(可能背景腳本直接寫入了錯誤訊息)，直接顯示原文
            if (finalResult = "Error parsing response")
                finalResult := resultText
                
            GuiControl, USAIG:, USAIResult, %finalResult%
            GuiControl, USAIG:, USAIStatus, 分析完成！
        } else {
            GuiControl, USAIG:, USAIResult, %resultText%
            GuiControl, USAIG:, USAIStatus, 分析失敗或發生錯誤
        }
        
        ; 清理臨時檔案
        FileDelete, %resultFile%
        FileDelete, %A_Temp%\gemini_request.json
        FileDelete, %A_Temp%\gemini_worker.ahk
    }
    else {
        ; 更新狀態文字讓使用者知道還在跑 (可選)
        ; GuiControl, USAIG:, USAIStatus, 正在思考中... (請稍候)
    }
return

StartGeminiBackgroundJob(apiKey, modelID, prompt, images, useThinking) {
    ; 1. 構建完整的 JSON 字串 (利用現有的 BuildGeminiJSON)
    jsonBody := BuildGeminiJSON(prompt, images, useThinking)
    
    ; 2. 將 JSON 寫入臨時檔案 (解決命令列長度限制)
    requestFile := A_Temp . "\gemini_request.json"
    FileDelete, %requestFile%
    FileAppend, %jsonBody%, %requestFile%, UTF-8
    
    ; 3. 準備結果檔案路徑
    resultFile := A_Temp . "\gemini_response.txt"
    FileDelete, %resultFile%
    
    ; 4. 建立背景 Worker 腳本
    ; 這個腳本非常精簡，只負責讀 JSON -> POST -> 寫入結果
    workerScriptPath := A_Temp . "\gemini_worker.ahk"
    FileDelete, %workerScriptPath%
    
    endpoint := "https://generativelanguage.googleapis.com/v1beta/models/" . modelID . ":generateContent?key=" . apiKey
    
    ; 構建 Worker 腳本內容
    workerCode = 
    (
    #NoTrayIcon
    FileRead, jsonBody, *P65001 %requestFile%
    
    url := "%endpoint%"
    
    whr := ComObjCreate("WinHttp.WinHttpRequest.5.1")
    whr.Open("POST", url, false)
    whr.SetRequestHeader("Content-Type", "application/json")
    whr.SetTimeouts(30000, 60000, 30000, 120000) ; 120秒超時
    
    try {
        whr.Send(jsonBody)
        ; 將回應寫入結果檔案
        FileAppend, `% whr.ResponseText, %resultFile%, UTF-8
    } catch e {
        err := "API Error: " . e.Message
        FileAppend, `% err, %resultFile%, UTF-8
    }
    ExitApp
    )
    
    FileAppend, %workerCode%, %workerScriptPath%, UTF-8
    
    ; 5. 執行背景腳本 (使用 Run 不會卡住主程式)
    Run, "%A_AhkPath%" "%workerScriptPath%"
}


; 插入結果到報告
USAIInsertResult:
    Gui, USAIG:Submit, NoHide
    if (USAIResult != "") {
        ; 檢查是否要包含 OCR 結果
        insertText := USAIResult
        
        ; 可選：加入 OCR 資訊作為註解
        ;if (USAI_CurrentOCRText != "" || USAI_PreviousOCRText != "") {
        ;    insertText .= "`n`n; OCR Info:"
        ;    if (USAI_CurrentOCRText != "") {
        ;        insertText .= "`n; Current: " . StrReplace(USAI_CurrentOCRText, "`n", " ")
        ;    }
        ;    if (USAI_PreviousOCRText != "") {
        ;        insertText .= "`n; Previous: " . StrReplace(USAI_PreviousOCRText, "`n", " ")
        ;    }
        ;}
        Gui, USAIG:Hide  ;<-- 註解掉這行，視窗就不會消失
        ActivateHIS()
        Sleep, 100
        SendInput, %insertText%
		
		; 建議：如果不隱藏視窗，可以加一行讓原本的 AI 視窗重新取得焦點 (可選)
        ; WinActivate, 超音波 AI 分析
    } else {
        GuiControl, USAIG:, USAIStatus, 沒有結果可以插入
    }
return

; 複製結果
USAICopyResult:
    Gui, USAIG:Submit, NoHide
    if (USAIResult != "") {
        Clipboard := USAIResult
        GuiControl, USAIG:, USAIStatus, 結果已複製到剪貼簿
    } else {
        GuiControl, USAIG:, USAIStatus, 沒有結果可以複製
    }
return

; 清除結果
USAIClearResult:
    GuiControl, USAIG:, USAIResult,
    GuiControl, USAIG:, USAIOCR1Result,
    GuiControl, USAIG:, USAIOCR2Result,
    USAI_CurrentOCRText := ""
    USAI_PreviousOCRText := ""
    GuiControl, USAIG:, USAIStatus, 結果已清除
return

; 關閉視窗
USAIGGuiClose:
USAIGGuiEscape:
    Gui, USAIG:Destroy
    USAI_CurrentImage := ""
    USAI_PreviousImage := ""
    USAI_CurrentOCRText := ""
    USAI_PreviousOCRText := ""
    ; 清理臨時檔案
    FileDelete, %A_Temp%\usai_current.png
    FileDelete, %A_Temp%\usai_previous.png
return

; Base64 編碼函數（二進制文件版本）- 保留原有功能
B64EncodeFile(filePath) {
    ; 獲取文件大小
    FileGetSize, fileSize, %filePath%
    if (ErrorLevel || fileSize = 0)
        return ""
    
    ; 分配內存並讀取文件
    VarSetCapacity(fileData, fileSize, 0)
    file := FileOpen(filePath, "r")
    if (!file)
        return ""
    
    file.RawRead(fileData, fileSize)
    file.Close()
    
    ; 轉換為 Base64
    if !(DllCall("crypt32\CryptBinaryToString", "ptr", &fileData, "uint", fileSize, "uint", 0x40000001, "ptr", 0, "uint*", base64Size))
        return ""
    
    VarSetCapacity(base64, base64Size << 1, 0)
    if !(DllCall("crypt32\CryptBinaryToString", "ptr", &fileData, "uint", fileSize, "uint", 0x40000001, "str", base64, "uint*", base64Size))
        return ""
    
    ; 移除換行符
    base64 := StrReplace(base64, "`r", "")
    base64 := StrReplace(base64, "`n", "")
    
    return base64
}


; 獲取剪貼簿中的影像
GetClipboardImage() {
    ; 檢查剪貼簿是否有影像
    if !DllCall("IsClipboardFormatAvailable", "uint", 2) { ; CF_BITMAP = 2
        return ""
    }
    
    ; 打開剪貼簿
    if !DllCall("OpenClipboard", "ptr", 0) {
        return ""
    }
    
    ; 獲取影像句柄
    hBitmap := DllCall("GetClipboardData", "uint", 2, "ptr") ; CF_BITMAP = 2
    if (!hBitmap) {
        DllCall("CloseClipboard")
        return ""
    }
    
    ; 轉換為 base64
    base64 := BitmapToBase64(hBitmap)
    
    DllCall("CloseClipboard")
    
    if (base64 != "") {
        return "data:image/png;base64," . base64
    }
    
    return ""
}

; 將 Bitmap 轉換為 Base64
BitmapToBase64(hBitmap) {
    ; 嘗試使用 GDI+ 方法
    if IsFunc("Gdip_Startup") {
        return BitmapToBase64_GDIPlus(hBitmap)
    } else {
        ; 備用方法：提示用戶手動操作
        MsgBox, 48, 需要 GDI+ 庫, 
        (
        此功能需要 GDI+ 庫支持。
        
        請：
        1. 將影像儲存為檔案
        2. 使用線上轉換工具轉為 base64
        3. 手動輸入到 API 中
        
        或安裝 GDI+ 庫：
        https://github.com/tariqporter/Gdip2/
        )
        return ""
    }
}

; GDI+ 版本的 Bitmap 轉換
BitmapToBase64_GDIPlus(hBitmap) {
    ; 創建臨時檔案
    tempFile := A_Temp . "\temp_image_" . A_TickCount . ".png"
    
    ; 使用 GDI+ 保存為 PNG
    pToken := Gdip_Startup()
    if (!pToken) {
        return ""
    }
    
    pBitmap := Gdip_CreateBitmapFromHBITMAP(hBitmap)
    if (!pBitmap) {
        Gdip_Shutdown(pToken)
        return ""
    }
    
    ; 保存為 PNG 檔案
    result := Gdip_SaveBitmapToFile(pBitmap, tempFile)
    Gdip_DisposeImage(pBitmap)
    Gdip_Shutdown(pToken)
    
    ; 檢查檔案是否成功保存
    if (result != 0 || !FileExist(tempFile)) {
        return ""
    }
    
    ; 驗證檔案大小
    FileGetSize, fileSize, %tempFile%
    if (fileSize = 0) {
        FileDelete, %tempFile%
        return ""
    }
    
    ; 讀取檔案並轉換為 base64
    base64 := B64EncodeFile(tempFile)
    
    ; 調試：保留一份圖片供檢查（可選）
    debugImageFile := A_Temp . "\usai_debug_image.png"
    FileCopy, %tempFile%, %debugImageFile%, 1
    
    ; 清理臨時檔案
    FileDelete, %tempFile%
    
    if (base64 = "") {
        return ""
    }
    
    return base64
}

; Base64 編碼函數（字符串版本）
B64Encode(string) {
    VarSetCapacity(bin, StrPut(string, "UTF-8")) && len := StrPut(string, &bin, "UTF-8") - 1
    if !(DllCall("crypt32\CryptBinaryToString", "ptr", &bin, "uint", len, "uint", 0x40000001, "ptr", 0, "uint*", size))
        return ""
    VarSetCapacity(out, size << 1, 0)
    if !(DllCall("crypt32\CryptBinaryToString", "ptr", &bin, "uint", len, "uint", 0x40000001, "str", out, "uint*", size))
        return ""
    return out
}



; 呼叫 OpenAI Vision API
CallOpenAIVision(apiKey, prompt, images) {
    ; 構建訊息內容
    content := []
    
    ; 添加文字部分
    textPart := {}
    textPart["type"] := "text"
    textPart["text"] := prompt
    content.Push(textPart)
    
    ; 添加影像部分
    for index, imageUrl in images {
        imagePart := {}
        imagePart["type"] := "image_url"
        imagePart["image_url"] := {}
        imagePart["image_url"]["url"] := imageUrl
        content.Push(imagePart)
    }
    
    ; 構建請求資料
    requestData := {}
    requestData["model"] := "o3"
    requestData["messages"] := [{}]
    requestData["messages"][1]["role"] := "user"
    requestData["messages"][1]["content"] := content
    requestData["max_completion_tokens"] := 5000
    requestData["temperature"] := 1
    
    ; 手動構建 JSON（更可靠）
    jsonData := BuildRequestJSON(requestData)
    
    ; 調試：顯示構建的 JSON（可選）
    ; debugFile := A_Temp . "\usai_debug.json"
    ; FileDelete, %debugFile%
    ; FileAppend, %jsonData%, %debugFile%, UTF-8
    ; MsgBox, 4, 調試 - JSON 請求, JSON 已保存到: %debugFile%`n`n是否要查看 JSON 內容？
    ; IfMsgBox, Yes
    ; {
    ;     Run, notepad.exe "%debugFile%"
    ; }
    
    ; 發送 HTTP 請求
    whr := ComObjCreate("WinHttp.WinHttpRequest.5.1")
    whr.Open("POST", "https://api.openai.com/v1/chat/completions", false)
    whr.SetRequestHeader("Content-Type", "application/json")
    whr.SetRequestHeader("Authorization", "Bearer " . apiKey)
    whr.SetTimeouts(30000, 30000, 30000, 30000) ; 30秒超時
    
    try {
        whr.Send(jsonData)
        
        if (whr.Status = 200) {
            response := JSON_Parse(whr.ResponseText)
            if (response.choices && response.choices.Length() > 0 && response.choices[1].message) {
                return response.choices[1].message.content
            }
        } else {
            ; 錯誤處理
            httpStatus := whr.Status
            responseText := whr.ResponseText
            MsgBox, 16, API 錯誤, HTTP錯誤代碼: %httpStatus%`n回應: %responseText%
        }
    } catch e {
        errorMessage := e.message
        MsgBox, 16, 請求錯誤, 發送請求時發生錯誤: %errorMessage%
    }
    
    return ""
}

; ============================================================================
; Google Gemini 1.5 Pro API 呼叫函數
; ============================================================================
CallGeminiVision(apiKey, modelID, prompt, images, useThinking := false) {
    ; API Endpoint
    endpoint := "https://generativelanguage.googleapis.com/v1beta/models/" . modelID . ":generateContent?key=" . apiKey
    
    ; 構建 JSON Payload
    json := BuildGeminiJSON(prompt, images, useThinking)
    
    whr := ComObjCreate("WinHttp.WinHttpRequest.5.1")
    whr.Open("POST", endpoint, false)
    whr.SetRequestHeader("Content-Type", "application/json")
    
    ; Thinking 模型可能需要較長回應時間，設定超時為 120秒
    whr.SetTimeouts(30000, 60000, 30000, 120000) 
    
    try {
        whr.Send(json)
        if (whr.Status = 200) {
            return ParseGeminiResponse(whr.ResponseText)
        } else {
            MsgBox, 16, API Error, % "Status: " . whr.Status . "`nResponse: " . whr.ResponseText
        }
    } catch e {
        MsgBox, 16, Network Error, % "Request failed: " . e.Message
    }
    return ""
}

BuildGeminiJSON(prompt, images, useThinking) {
    ; 基礎結構
    json := "{""contents"":[{""parts"":["
    
    ; Prompt
    cleanPrompt := EscapeJSONString(prompt)
    json .= "{""text"":""" . cleanPrompt . """}"
    
    ; Images
    for index, imgData in images {
        json .= ","
        if (InStr(imgData, "base64,"))
            imgRaw := SubStr(imgData, InStr(imgData, "base64,") + 7)
        else
            imgRaw := imgData
        json .= "{""inline_data"":{""mime_type"":""image/png"",""" . "data"":""" . imgRaw . """}}"
    }
    json .= "]}]"
    
    ; === Thinking Config (關鍵修改) ===
    if (useThinking) {
        ; 根據文件，Gemini 3 / 2.0 Flash Thinking 使用 thinking_config
        ; 設定 thinkingLevel 為 HIGH (對應 thinking=high)
        ; 設定 includeThoughts 為 true (可選，若想看到思考過程)
        json .= ",""generationConfig"":{"
        json .= """thinkingConfig"":{"
        json .= """includeThoughts"":true,"
        json .= """thinkingLevel"":""HIGH"""  ; 這就是您需要的 thinking=high
        json .= "}" ; End thinkingConfig
        json .= "}" ; End generationConfig
    }
    
    json .= "}" ; End root
    return json
}

ParseGeminiResponse(responseText) {
	; Gemini Thinking 模式會回傳多個 "text" 區塊
    ; 第一個通常是思考過程 (Thought)，最後一個才是最終回答 (Response)
    ; 所以我們需要用 Loop 抓取所有的 text，並保留最後一個
    
	finalResult := ""
    pos := 1
    
    ; 循環尋找所有的 "text": "..."
    while (pos := RegExMatch(responseText, """text""\s*:\s*""((?:\\.|[^""\\])*)""", match, pos)) {
        finalResult := match1
        ; 更新搜尋位置，繼續往後找下一個 text
        pos += StrLen(match)
    }
    
    if (finalResult != "") {
        ; 還原轉義字符 (JSON Unescape)
        result := finalResult
        result := StrReplace(result, "\""", """")
        result := StrReplace(result, "\n", "`n")
        result := StrReplace(result, "\r", "`r")
        result := StrReplace(result, "\t", "`t")
        result := StrReplace(result, "\\", "\") ; 反斜線最後處理
        return result
    }
    
    return "Error parsing response: " . responseText
}

; 專門為 OpenAI API 構建 JSON 請求
BuildRequestJSON(requestData) {
    ; 手動構建 JSON 以確保格式正確
    json := "{"
    json .= """model"":""" . requestData["model"] . ""","
    json .= """max_completion_tokens"":" . requestData["max_completion_tokens"] . ","
    json .= """temperature"":" . requestData["temperature"] . ","
    json .= """messages"":[{"
    json .= """role"":""" . requestData["messages"][1]["role"] . ""","
    json .= """content"":["
    
    ; 構建 content 陣列
    content := requestData["messages"][1]["content"]
    contentParts := []
    
    for index, part in content {
        if (part["type"] = "text") {
            ; 轉義文字內容
            escapedText := EscapeJSONString(part["text"])
            contentParts.Push("""type"":""text"",""text"":""" . escapedText . """")
        } else if (part["type"] = "image_url") {
            contentParts.Push("""type"":""image_url"",""image_url"":{""url"":""" . part["image_url"]["url"] . """}")
        }
    }
    
    ; 加入所有 content parts
    for index, partJson in contentParts {
        if (index > 1)
            json .= ","
        json .= "{" . partJson . "}"
    }
    
    json .= "]}]}"
    
    return json
}

; JSON 字串轉義函數
EscapeJSONString(str) {
    ; 轉義 JSON 中的特殊字符
    str := StrReplace(str, "\", "\\")     ; 反斜線
    str := StrReplace(str, """", "\""")   ; 雙引號
    str := StrReplace(str, "`r", "\r")    ; 回車
    str := StrReplace(str, "`n", "\n")    ; 換行
    str := StrReplace(str, "`t", "\t")    ; Tab
    return str
}

; 簡化的 JSON 函數（備用）
JSON_Stringify(obj) {
    if IsObject(obj) {
        if (obj.Length() != "") { ; 陣列
            result := "["
            for index, value in obj {
                if (index > 1)
                    result .= ","
                result .= JSON_Stringify(value)
            }
            result .= "]"
        } else { ; 物件
            result := "{"
            first := true
            for key, value in obj {
                if (!first)
                    result .= ","
                result .= """" . key . """:" . JSON_Stringify(value)
                first := false
            }
            result .= "}"
        }
    } else {
        ; 字串或數字
        if obj is number
            result := obj
        else
            result := """" . StrReplace(StrReplace(obj, "\", "\\"), """", "\""") . """"
    }
    return result
}

; 簡化的 JSON 解析
JSON_Parse(text) {
    ; 這是一個簡化版本，只處理基本的 JSON 結構
    ; 實際使用中可能需要更完整的 JSON 庫
    
    ; 移除多餘空格
    text := RegExReplace(text, "\s+", " ")
    text := Trim(text)
    
    ; 創建基本物件來模擬 JSON 回應結構
    obj := {}
    
    ; 尋找 choices 陣列中的 content
    if RegExMatch(text, """content""\s*:\s*""([^""]+)""", match) {
        obj.choices := []
        choice := {}
        choice.message := {}
        choice.message.content := match1
        obj.choices.Push(choice)
    }
    
    return obj
}


; ===========================================================================================
; 錯誤處理和日誌
; ===========================================================================================

; 記錄 AI 分析日誌
LogAIAnalysis(action, result := "") {
    FormatTime, timestamp, , yyyy-MM-dd HH:mm:ss
    logFile := A_ScriptDir . "\AI_Analysis_Log.txt"
    logEntry := timestamp . " | " . action
    if (result != "")
        logEntry .= " | " . result
    logEntry .= "`n"
    
    FileAppend, %logEntry%, %logFile%
}

; 裁切影像的指定區域
CropImage(inputPath, outputPath, cropPercent := 20, fromBottom := true) {
    ; 使用 GDI+ 載入影像
    pToken := Gdip_Startup()
    if (!pToken) {
        return false
    }
    
    ; 載入原始影像
    pBitmap := Gdip_CreateBitmapFromFile(inputPath)
    if (!pBitmap) {
        Gdip_Shutdown(pToken)
        return false
    }
    
    ; 取得影像尺寸
    Gdip_GetImageDimensions(pBitmap, origWidth, origHeight)
    
    ; 計算裁切區域
    if (fromBottom) {
        ; 從底部裁切
        cropHeight := Round(origHeight * cropPercent / 100)
        cropY := origHeight - cropHeight
        cropX := 0
        cropWidth := origWidth
    } else {
        ; 從頂部裁切（如果需要）
        cropHeight := Round(origHeight * cropPercent / 100)
        cropY := 0
        cropX := 0
        cropWidth := origWidth
    }
    
    ; 創建新的 Bitmap 用於裁切後的影像
    pBitmapCropped := Gdip_CreateBitmap(cropWidth, cropHeight)
    pGraphics := Gdip_GraphicsFromImage(pBitmapCropped)
    
    ; 執行裁切
    Gdip_DrawImage(pGraphics, pBitmap, 0, 0, cropWidth, cropHeight, cropX, cropY, cropWidth, cropHeight)
    
    ; 儲存裁切後的影像
    Gdip_SaveBitmapToFile(pBitmapCropped, outputPath)
    
    ; 清理資源
    Gdip_DeleteGraphics(pGraphics)
    Gdip_DisposeImage(pBitmapCropped)
    Gdip_DisposeImage(pBitmap)
    Gdip_Shutdown(pToken)
    
    return true
}

; 創建用於 AI 的影像（保留下方 90%）
CreateAIImage(inputPath, outputPath, keepPercent := 90) {
    pToken := Gdip_Startup()
    if (!pToken) {
        return false
    }
    
    pBitmap := Gdip_CreateBitmapFromFile(inputPath)
    if (!pBitmap) {
        Gdip_Shutdown(pToken)
        return false
    }
    
    Gdip_GetImageDimensions(pBitmap, origWidth, origHeight)
    
    ; 計算保留區域（下方 80%）
    keepHeight := Round(origHeight * keepPercent / 100)
    cropY := origHeight - keepHeight
    
    ; 創建新的 Bitmap
    pBitmapAI := Gdip_CreateBitmap(origWidth, keepHeight)
    pGraphics := Gdip_GraphicsFromImage(pBitmapAI)
    
    ; 裁切並儲存
    Gdip_DrawImage(pGraphics, pBitmap, 0, 0, origWidth, keepHeight, 0, cropY, origWidth, keepHeight)
    Gdip_SaveBitmapToFile(pBitmapAI, outputPath)
    
    ; 清理
    Gdip_DeleteGraphics(pGraphics)
    Gdip_DisposeImage(pBitmapAI)
    Gdip_DisposeImage(pBitmap)
    Gdip_Shutdown(pToken)
    
    return true
}

; 複製 OCR 1 結果
USAICopyOCR1:
    Gui, USAIG:Submit, NoHide
    if (USAIOCR1Result != "") {
        Clipboard := USAIOCR1Result
        GuiControl, USAIG:, USAIStatus, OCR 1 結果已複製到剪貼簿
    } else {
        GuiControl, USAIG:, USAIStatus, OCR 1 沒有內容可複製
    }
return

; 清除 OCR 1 結果
USAIClearOCR1:
    GuiControl, USAIG:, USAIOCR1Result,
    USAI_CurrentOCRText := ""
    GuiControl, USAIG:, USAIStatus, OCR 1 結果已清除
return

; 複製 OCR 2 結果
USAICopyOCR2:
    Gui, USAIG:Submit, NoHide
    if (USAIOCR2Result != "") {
        Clipboard := USAIOCR2Result
        GuiControl, USAIG:, USAIStatus, OCR 2 結果已複製到剪貼簿
    } else {
        GuiControl, USAIG:, USAIStatus, OCR 2 沒有內容可複製
    }
return

; 清除 OCR 2 結果
USAIClearOCR2:
    GuiControl, USAIG:, USAIOCR2Result,
    USAI_PreviousOCRText := ""
    GuiControl, USAIG:, USAIStatus, OCR 2 結果已清除
return