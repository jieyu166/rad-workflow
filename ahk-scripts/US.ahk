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


::usb::
SendInput Breast sonography study shows:`r
;SendInput Breast composition: _`r
gosub calldate
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
:O:usb2;::
HotstringMenuV("A","MenuShortcut2"
    ,"_ subareolar ductal ectasia, _mm.(Srs/Img:1/_) No echogenic content, favor benign."
    ,"_ prominent duct, _mm.(Srs/Img:1/_)"
	,"Bilateral breast ductal ectasia, up to _mm, concluded as benign.(Srs/Img:1/_)","BRK"
	,"Stable bilateral breast nodules, the detail please refer to the description.`r  _Favor benign.")
return

:O:ub::Mild urinary bladder wall thickening, could be chronic cystitis, _shrunken UB, or others.
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


:O:usneck::
SendInput Neck/Thyroid sonography shows: `r`r
SendInput 1. Thyroid: `r_Normal size and echogenicity of bilateral thyroid lobes and isthmus.`r`r
SendInput 2. Neck:`rLymph nodes with preserved fatty hila of bilateral neck, short-axis <1cm.`r`r

MsgBox, 4,, "Would you like to continue Salivary gland...(press Yes or No)"
IfMsgBox, No
	return

SendInput 3. Salivary glands:`r - unremarkable.`r`r
SendInput _tn;`r_tirads; `r
return

:O:usneck2::
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

:O:usneck3::
(
Status post bilateral total thyroidectomy. No US evidence of local recurrence.
----------------------------------------------------------------------
Neck sonography shows:

1. Thyroid:
 - status post bilateral total thyroidectomy

2. Neck:
 - Lymph nodes with preserved fatty hila of bilateral neck, short-axis <1cm.
)


::tn::A _solid _hypoechoic nodule in _LRt _mid. thyroid, _x_x_ mm, TR_.(Srs/Img:1/_)
::tn2::
    gosub GetSideSelection

    ; 2. (選用) 檢查使用者是否按了取消(X)，如果變數是空的就終止
    if (tSideCap = ""){
        tSideCap := "_"
		tSideLow := "_"
	}

    ; 3. 貼上內容 (使用設定好的變數)
    SendInput, A TR_ nodule in %tSideCap% thyroid, _cm.(Srs/Img:1/_)
	return

::tn3::
HotstringMenuV("A","MenuShortcut"
    ,"<1cm TR_4 nodules in _bilateral thyroid."
    ,"A <1cm TR_4 nodule in _ thyroid."
    ,"<1cm TR_4 nodules in _bilateral thyroid.(Srs/Img:_/_ _)"
    ,"BRK","Prior FNA: benign.(_)")
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

CopyCXRtoHISWithParam(2)
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


CopyCXRtoHISWithParam(2)
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
HotstringMenuV("A","MenuShortcut"
    ,"Prostate cysts, calcifications, est. volume about _ cc."
    ,"Enlarged prostate with cysts, calcifications, est. volume about _ cc."
    ,"Prostate calcifications, est. volume about _ cc."
    ,"Est. prostate volume about _cc."
    ,"BRK"
    ,"Heterogenous enhancement of prostate"
    ,"Heterogenous enhancement of prostate with hypoenhancing parts, size about _(Srs/Img:_/_)"
    ,"Suggest correlate with PSA or other exams.")
return

::usa::
MsgBox, 4,, "Would you like to compaire previous study...(press Yes or No)"
IfMsgBox, Yes
	gosub calldate

HotstringMenuV("A","MenuShortcut", "Upper abdominal sonography:", "Urotract sonography:","TRUS sonography:","Lower abdomen sonography:" )
SendInput `r(Findings same as Impressions)
return



:O:usadd::
HotstringMenuV("A","MenuShortcut"
    ,"Mild enlarged bilateral kidney sizes. Could be related to DM or other chronic renal parenchyma disease."
    ,"Coarse echotexture of the liver with uneven surface, suggesting cirrhosis of liver. "
    ,"No US evidence of hydronephrosis.","Both kidneys show normal size(right: _ cm; left: _ cm)."
	,"* Urinary bladder is not distended, limited evaluation.",
    ,"* Gas block/Poor visualization of _pancreas_right lobe of liver from subcostal area. Lesion may be obscured.`r")
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
CopyCXRtoHISWithParam(2)
return

ABDUS2:
desc := "Urotract sonography:`r"
gosub ABDUScommon
gosub ABDUSUro1
gosub ABDUSUro2
gosub ABDUScommon2
CopyCXRtoHISWithParam(2)
return

ABDUS3:
desc := "Urotract sonography:`r"
gosub ABDUScommon
gosub ABDUSUro1
gosub ABDUScommon2
CopyCXRtoHISWithParam(2)
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
CopyCXRtoHISWithParam(2)
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

Biceps tendon long head:
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
; Requires: API_KEY global (loaded by 簡碼 jai.ahk from radiologist_settings.ini)
; Prompts: external files in ahk-scripts/prompts/{us_abd,us_trus,us_ivp,ct_chest}.md
; Hot entry point: gAI_FindOpen from Abd US 簡化 GUI
; ============================================================================

; ── Async / history globals ──
; 實際初始化在「簡碼 jai.ahk」的 auto-exec 區段（因為 US.ahk 透過 #include 引入時，
; 主腳本的 auto-exec 已被前面 Abbr.ahk 的 hotstring 結束）。
; 變數列表：
;   g_I2F_Whr / g_I2F_StartTick / g_I2F_RequestActive
;   g_I2F_LastScenario / g_I2F_LastImpression / g_I2F_LastModel / g_I2F_LastTokens
;   g_I2F_History / g_I2F_HistoryMax / g_I2F_PromptDir

AI_FindOpen:
; 每次開啟視窗清空歷史（提示文字也說「視窗關閉即清除」）
g_I2F_History := []
Gui, I2F:New, -AlwaysOnTop +Resize, Impression → Findings (AI)
Gui, I2F:Font, s10, Segoe UI

; 檢查類型選擇
Gui, I2F:Add, GroupBox, x10 y10 w480 h110, 檢查選項
Gui, I2F:Add, Text, x20 y30 w70 h20 vI2F_OptionLabel, 腹超:
Gui, I2F:Add, Radio, x100 y30 w120 vI2F_TypeUpperAbd Checked, &Upper abd
Gui, I2F:Add, Radio, x230 y30 w120 vI2F_TypeUroM, Urotract(&M)
Gui, I2F:Add, Radio, x360 y30 w120 vI2F_TypeUroF, Urotract(&F)
; --- Prompt 情境選擇 ---
Gui, I2F:Add, Text, x20 y60 w80 h20, 輸出模式:
Gui, I2F:Add, DropDownList, x100 y55 w360 vI2F_Scenario gI2F_OnScenarioChange Choose1, 腹超||TRUS||IVP||CT-Chest

Gui, I2F:Add, Text, xm y+25, Impression:
Gui, I2F:Add, Edit, vI2F_Impression w480 h160
Gui, I2F:Add, Button, gI2F_DoGenerate w120 h28 Default vI2F_BtnGen, &Generate
Gui, I2F:Add, Button, gI2F_Clear x+10 w80 h28, Clear
Gui, I2F:Add, Text, x+10 yp+5 w220 h20 vI2F_Status, （閒置）

Gui, I2F:Add, Text, xm y+12 Section, Findings (descriptive, system-organized):
Gui, I2F:Add, Edit, vI2F_Findings w480 h200
Gui, I2F:Add, Button, gI2F_CopyFindings w140 h26, &Copy Findings
Gui, I2F:Add, Button, gI2F_CopyFindImpr x+10 w180 h26, Copy F + &Impression

; 歷史紀錄（雙擊還原 Impression + Findings）
Gui, I2F:Add, Text, xm y+15, 歷史紀錄（雙擊列還原；最多保留 %g_I2F_HistoryMax% 筆，視窗關閉即清除）:
Gui, I2F:Add, ListView, xm y+3 w480 h120 vI2F_HistoryLV gI2F_HistoryEvent -ReadOnly -Multi, 時間|模式|耗時|tokens|Impression
LV_ModifyCol(1, 60)
LV_ModifyCol(2, 50)
LV_ModifyCol(3, 50)
LV_ModifyCol(4, 60)
LV_ModifyCol(5, 240)

Gui, I2F:Show
Gosub, I2F_OnScenarioChange
return

I2F_OnScenarioChange:
Gui, I2F:Submit, NoHide
if (InStr(I2F_Scenario, "腹超")) {
    GuiControl, I2F:, I2F_OptionLabel, 腹超:
    GuiControl, I2F:, I2F_TypeUpperAbd, &Upper abdomen
    GuiControl, I2F:, I2F_TypeUroM, Urotract (&M)
    GuiControl, I2F:, I2F_TypeUroF, Urotract (&F)
    GuiControl, I2F:Enable, I2F_TypeUroF
    GuiControl, I2F:Show, I2F_OptionLabel
    GuiControl, I2F:Show, I2F_TypeUpperAbd
    GuiControl, I2F:Show, I2F_TypeUroM
    GuiControl, I2F:Show, I2F_TypeUroF
} else if (InStr(I2F_Scenario, "CT-Chest")) {
    GuiControl, I2F:, I2F_OptionLabel, CT:
    GuiControl, I2F:, I2F_TypeUpperAbd, 打藥
    GuiControl, I2F:, I2F_TypeUroM, 不打藥
    GuiControl, I2F:, I2F_TypeUroF,
    GuiControl, I2F:Disable, I2F_TypeUroF
    if (I2F_TypeUroF)
        GuiControl, I2F:, I2F_TypeUpperAbd, 1
    GuiControl, I2F:Show, I2F_OptionLabel
    GuiControl, I2F:Show, I2F_TypeUpperAbd
    GuiControl, I2F:Show, I2F_TypeUroM
    GuiControl, I2F:Show, I2F_TypeUroF
} else {
    GuiControl, I2F:Hide, I2F_OptionLabel
    GuiControl, I2F:Hide, I2F_TypeUpperAbd
    GuiControl, I2F:Hide, I2F_TypeUroM
    GuiControl, I2F:Hide, I2F_TypeUroF
}
return

I2F_Clear:
Gui, I2F:Submit, NoHide
GuiControl, I2F:, I2F_Findings
return

I2F_CopyFindings:
Gui, I2F:Submit, NoHide
Clipboard := RegExReplace(I2F_Findings, "\r?\n", "`r`n")  ; 將 LF 或 CRLF 都正規化為 CRLF
MsgBox, 64, Copied, %Clipboard%
return

I2F_CopyFindImpr:
Gui, I2F:Submit, NoHide
findText := RegExReplace(I2F_Findings, "\r?\n", "`r`n")
imprText := RegExReplace(I2F_Impression, "\r?\n", "`r`n")
imprText := "Impression:`r`n" . imprText
if (findText = "" && imprText = "") {
    MsgBox, 48, Warning, Findings and Impression are both empty.
    return
}
ControlSetText, ThunderRT6TextBox14, %findText%, ahk_exe chk060.exe
ControlSetText, ThunderRT6TextBox5, %imprText%, ahk_exe chk060.exe
MsgBox, 64, Done, Findings + original Impression copied to chk060.
return

I2F_DoGenerate:
Gui, I2F:Submit, NoHide
if (I2F_Impression = "") {
    MsgBox, 48, Warning, Please paste Impression first.
    return
}

if (!API_KEY) {
    MsgBox, 16, Error, GPT API Key 尚未設定。請按 Win+\ 開啟設定管理器並填入 GPT Key。
    return
}

if (g_I2F_RequestActive) {
    MsgBox, 48, , 目前已有請求進行中，請等待完成。
    return
}

endpoint := "https://api.openai.com/v1/chat/completions"
gModel   := "gpt-5.4-mini"   ; 非推理模型，TTFT < 1s，避開 gpt-5-mini 的 25-50s reasoning 延遲（2026-04-29）

; 依 US 類型決定 organSystems / conditionalOutput（僅腹超 prompt 會用到）
if (I2F_TypeUpperAbd) {
    usTitle := "Upper abdominal sonography:"
    organSystems := "Liver:`nBiliary trees:`nGallbladder:`nPancreas:`nSpleen:`nKidneys:"
    conditionalOutput := "Do NOT output: Uterus/adnexa, Others, Aorta/IVC, Urinary bladder, Prostate (unless specifically mentioned in impression)"
} else if (I2F_TypeUroM) {
    usTitle := "Urotract sonography:"
    organSystems := "Liver:`nBiliary trees:`nGallbladder:`nPancreas:`nSpleen:`nKidneys:`nUrinary bladder:`nProstate:"
    conditionalOutput := "Do NOT output: Uterus/adnexa, Others, Aorta/IVC (unless specifically mentioned in impression)"
} else if (I2F_TypeUroF) {
    usTitle := "Urotract sonography:"
    organSystems := "Liver:`nBiliary trees:`nGallbladder:`nPancreas:`nSpleen:`nKidneys:`nUrinary bladder:"
    conditionalOutput := "Do NOT output: Uterus/adnexa, Others, Aorta/IVC, Prostate (unless specifically mentioned in impression)"
}

if (!InStr(I2F_Scenario, "CT-Chest") || I2F_TypeUpperAbd) {
    ctMethod := "METHOD: (1) HRCT (2) Noncontrast survey (3) contrast enhancement were performed"
    ctContrastNote := "Before and after the administration of intravenous contrast there was no adverse effect."
    ctLimitationNote := ""
} else {
    ctMethod := "METHOD: (1) HRCT (2) Noncontrast survey were performed"
    ctContrastNote := ""
    ctLimitationNote := "*This is a Non contrast medium injection image.`nLimited evaluation for lymphadenopathy, vascular structure, soft tissue density organs and soft tissue lesions survey;"
}

; 從外部檔讀取對應 scenario 的 prompt（找不到 → 友善錯誤）
if (InStr(I2F_Scenario, "腹超"))
    promptFile := g_I2F_PromptDir "\us_abd.md"
else if (InStr(I2F_Scenario, "IVP"))
    promptFile := g_I2F_PromptDir "\us_ivp.md"
else if (InStr(I2F_Scenario, "TRUS"))
    promptFile := g_I2F_PromptDir "\us_trus.md"
else if (InStr(I2F_Scenario, "CT-Chest"))
    promptFile := g_I2F_PromptDir "\ct_chest.md"

if (!FileExist(promptFile)) {
    MsgBox, 16, Error, 找不到 prompt 檔案：%promptFile%`n請確認 ahk-scripts/prompts/ 內有對應 .md 檔。
    return
}

FileRead, sysPrompt, %promptFile%
if (ErrorLevel || sysPrompt = "") {
    MsgBox, 16, Error, 無法讀取 prompt 檔：%promptFile%
    return
}

; 替換佔位符（腹超用；其他 prompt 不含佔位符，StrReplace 為 no-op）
sysPrompt := StrReplace(sysPrompt, "{{usTitle}}", usTitle)
sysPrompt := StrReplace(sysPrompt, "{{organSystems}}", organSystems)
sysPrompt := StrReplace(sysPrompt, "{{conditionalOutput}}", conditionalOutput)
sysPrompt := StrReplace(sysPrompt, "{{ctMethod}}", ctMethod)
sysPrompt := StrReplace(sysPrompt, "{{ctContrastNote}}", ctContrastNote)
sysPrompt := StrReplace(sysPrompt, "{{ctLimitationNote}}", ctLimitationNote)

; 建立 userPrompt + JSON
userPrompt := "Impression:`n" . I2F_Impression

; 注意：gpt-5 系列不支援 temperature 自訂（只接受預設值 1），故不傳此參數
json := "{"
    . """model"": """ gModel ""","
    . """messages"": ["
        . "{""role"": ""system"", ""content"": " . JEscape(sysPrompt) . "},"
        . "{""role"": ""user"", ""content"": " . JEscape(userPrompt) . "}"
    . "]"
    . "}"

; 鎖定 GUI、顯示處理中
GuiControl, I2F:Disable, I2F_BtnGen
GuiControl, I2F:, I2F_Status, % "處理中... 0.0s（" I2F_Scenario " / " gModel "）"
g_I2F_LastScenario := I2F_Scenario
g_I2F_LastImpression := I2F_Impression
g_I2F_LastModel := gModel

; 啟動非同步 HTTP（async = true）
g_I2F_Whr := ComObjCreate("WinHttp.WinHttpRequest.5.1")
g_I2F_Whr.Open("POST", endpoint, true)
g_I2F_Whr.SetRequestHeader("Content-Type", "application/json; charset=utf-8")
g_I2F_Whr.SetRequestHeader("Authorization", "Bearer " API_KEY)
g_I2F_Whr.SetTimeouts(60000, 60000, 60000, 90000)
g_I2F_Whr.Send(json)

g_I2F_StartTick := A_TickCount
g_I2F_RequestActive := true
SetTimer, I2F_PollResponse, 250
return

; ── 非同步輪詢處理回應 ──
I2F_PollResponse:
    elapsed_s := Round((A_TickCount - g_I2F_StartTick) / 1000, 1)

    ; 檢查是否完成（WaitForResponse(0) 立即返回；try/catch 處理尚未完成的例外）
    done := false
    try {
        done := g_I2F_Whr.WaitForResponse(0)
    } catch e {
        done := false
    }

    if (!done) {
        GuiControl, I2F:, I2F_Status, % "處理中... " elapsed_s "s（" g_I2F_LastScenario " / " g_I2F_LastModel "）"
        if (elapsed_s > 90) {
            SetTimer, I2F_PollResponse, Off
            g_I2F_RequestActive := false
            GuiControl, I2F:Enable, I2F_BtnGen
            GuiControl, I2F:, I2F_Status, % "逾時（>90s）"
        }
        return
    }

    ; 已完成
    SetTimer, I2F_PollResponse, Off
    g_I2F_RequestActive := false
    GuiControl, I2F:Enable, I2F_BtnGen

    status := 0
    resp := ""
    try {
        status := g_I2F_Whr.Status
        resp := g_I2F_Whr.ResponseText
    } catch e {
        GuiControl, I2F:, I2F_Status, % "請求失敗（" SubStr(e.message, 1, 60) "）"
        return
    }

    if (status != 200) {
        ; 錯誤訊息只顯示 status + 截短前 200 字（避免洩漏 raw response）
        snippet := SubStr(resp, 1, 200)
        GuiControl, I2F:, I2F_Status, % "HTTP " status "（" elapsed_s "s）"
        MsgBox, 16, API Error, % "HTTP " status "（耗時 " elapsed_s "s）`n`n回應節錄（前 200 字）：`n" snippet
        return
    }

    content := ExtractContent(resp)
    if (content = "") {
        snippet := SubStr(resp, 1, 200)
        GuiControl, I2F:, I2F_Status, % "解析失敗"
        MsgBox, 16, Parse Error, % "回應解析失敗。`n`n回應節錄（前 200 字）：`n" snippet
        return
    }

    ; 抓 token usage
    ParseTokenUsage(resp)

    ; 從 <<FINDINGS>> 抓正文（IVP 直接用 content）
    if (InStr(g_I2F_LastScenario, "IVP")) {
        find := content
    } else {
        find := RegGet(content, "s)<<(?:FINDINGS)>>\s*(.*?)\s*(?=<<(?:IMPRESSION|FINDINGS)>>|$)")
        if (find = "")
            find := content
    }
    find := Trim(find)

    GuiControl, I2F:, I2F_Findings, % find
    GuiControl, I2F:, I2F_Status, % "完成 " elapsed_s "s | tokens " g_I2F_LastTokens.total " (in " g_I2F_LastTokens.prompt "/out " g_I2F_LastTokens.completion ")"

    ; 加入歷史
    AddI2FHistory(g_I2F_LastImpression, find, g_I2F_LastScenario, elapsed_s, g_I2F_LastTokens.total)
return

; ── 歷史紀錄輔助函式 ──
AddI2FHistory(impression, findings, scenario, elapsed_s, tokens) {
    global g_I2F_History, g_I2F_HistoryMax
    FormatTime, ts,, HH:mm:ss
    g_I2F_History.InsertAt(1, {time: ts, scenario: scenario, elapsed: elapsed_s
                              , tokens: tokens, impression: impression, findings: findings})
    while (g_I2F_History.Length() > g_I2F_HistoryMax)
        g_I2F_History.Pop()
    RefreshI2FHistoryLV()
}

RefreshI2FHistoryLV() {
    global g_I2F_History
    Gui, I2F:Default
    Gui, ListView, I2F_HistoryLV
    LV_Delete()
    for _, item in g_I2F_History {
        preview := SubStr(StrReplace(StrReplace(item.impression, "`r", " "), "`n", " "), 1, 80)
        LV_Add("", item.time, item.scenario, item.elapsed "s", item.tokens, preview)
    }
}

; ── 點擊歷史列：雙擊還原至 Impression / Findings ──
I2F_HistoryEvent:
    if (A_GuiEvent != "DoubleClick")
        return
    Gui, I2F:Default
    Gui, ListView, I2F_HistoryLV
    row := A_EventInfo
    if (row < 1 || row > g_I2F_History.Length())
        return
    item := g_I2F_History[row]
    GuiControl, I2F:, I2F_Impression, % item.impression
    GuiControl, I2F:, I2F_Findings, % item.findings
    GuiControl, I2F:, I2F_Status, % "已還原：" item.time " " item.scenario
return

; ── 從 OpenAI 回應中抓 token 數（更新 g_I2F_LastTokens） ──
ParseTokenUsage(resp) {
    global g_I2F_LastTokens
    g_I2F_LastTokens := {prompt: 0, completion: 0, total: 0}
    if RegExMatch(resp, """prompt_tokens""\s*:\s*(\d+)", m)
        g_I2F_LastTokens.prompt := m1 + 0
    if RegExMatch(resp, """completion_tokens""\s*:\s*(\d+)", m)
        g_I2F_LastTokens.completion := m1 + 0
    if RegExMatch(resp, """total_tokens""\s*:\s*(\d+)", m)
        g_I2F_LastTokens.total := m1 + 0
}

; ---- Helpers ----
; HttpPost 已移除（同步呼叫不再使用；改用內嵌的非同步 WinHttp.WinHttpRequest.5.1）

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
global USAI_APIKey := API_KEY

; 熱字串觸發
::usaigui::
ShowUSAIGUI:  ; 修改 ShowUSAIGUI 標籤，使用雙欄式佈局
	Gui, USAIG:New, , 超音波 AI 分析 (GPT-5.4)
    Gui, USAIG:Font, s10

    ; === 左側面板 ===
    Gui, USAIG:Add, GroupBox, x10 y10 w470 h157, API / Backend 設定
    Gui, USAIG:Add, Text, x20 y30 w60 vUSAIAPIKeyLbl, API Key:
    Gui, USAIG:Add, Edit, x85 y30 w380 h20 vUSAIAPIKey Password, %API_KEY%

    Gui, USAIG:Add, GroupBox, x10 y177 w470 h100, 影像狀態
    Gui, USAIG:Add, Text, x20 y197 w220 h40 vUSAIImage1Status Center, 本次影像：未上傳`n點擊下方按鈕貼上影像
    Gui, USAIG:Add, Text, x250 y197 w220 h40 vUSAIImage2Status Center, 前次影像：未上傳`n點擊下方按鈕貼上影像
    Gui, USAIG:Add, Text, x20 y242 w220 h30 vUSAIOCR1Status, OCR: 尚未執行
    Gui, USAIG:Add, Text, x250 y242 w220 h30 vUSAIOCR2Status, OCR: 尚未執行
    Gui, USAIG:Add, Button, x20 y287 w220 h35 gUSAIPasteImage1, 貼上本次影像 (Ctrl+V)
    Gui, USAIG:Add, Button, x250 y287 w220 h35 gUSAIPasteImage2, 貼上前次影像 (Ctrl+V)
    Gui, USAIG:Add, Button, x20 y327 w220 h30 gUSAIExecuteOCR1, 執行 OCR (本次)
    Gui, USAIG:Add, Button, x250 y327 w220 h30 gUSAIExecuteOCR2, 執行 OCR (前次)
    Gui, USAIG:Add, GroupBox, x10 y367 w470 h250, OCR 辨識結果
    Gui, USAIG:Add, Edit, x20 y387 w220 h180 vUSAIOCR1Result Multi WantReturn VScroll
    Gui, USAIG:Add, Edit, x250 y387 w220 h180 vUSAIOCR2Result Multi WantReturn VScroll
    Gui, USAIG:Add, Button, x20 y572 w105 h30 gUSAICopyOCR1, 複製 OCR 1
    Gui, USAIG:Add, Button, x135 y572 w105 h30 gUSAIClearOCR1, 清除 OCR 1
    Gui, USAIG:Add, Button, x250 y572 w105 h30 gUSAICopyOCR2, 複製 OCR 2
    Gui, USAIG:Add, Button, x365 y572 w105 h30 gUSAIClearOCR2, 清除 OCR 2

; === 右側面板 ===
	Gui, USAIG:Add, GroupBox, x490 y10 w400 h160, 分析選項

    Gui, USAIG:Add, Text, x500 y30 w80 h23, 檢查部位:
    Gui, USAIG:Add, DropDownList, x580 y27 w300 vUSAIExamType gUSAIExamTypeChanged Choose1, GPT-5.4 Thinking (Breast)||脊椎 (Spine, Thinking)|Ankle Foot 陳主任風格 Thinking| Chest x-ray (Thinking)|Knee Thinking|一般描述 (General)

    Gui, USAIG:Add, CheckBox, x580 y60 w180 h23 vUSAICropImage Checked, 啟用影像裁切 (去除上方資訊)
    Gui, USAIG:Add, Button, x770 y57 w110 h25 gUSAIExportCrop, 匯出裁切圖

    Gui, USAIG:Add, Radio, x500 y90 w380 vUSAIChoice1 Checked, 僅本次影像
    Gui, USAIG:Add, Radio, x500 y110 w380 vUSAIChoice2, 同一病灶比較 (兩張)
    Gui, USAIG:Add, Radio, x500 y130 w380 vUSAIChoice3, 大小變化比較 (兩張)

    Gui, USAIG:Add, Button, x590 y150 w200 h40 gUSAIAnalyze Default vUSAIAnalyzeBtn, 開始 GPT 分析

    Gui, USAIG:Add, GroupBox, x490 y200 w400 h370, 分析結果
    Gui, USAIG:Add, Edit, x500 y220 w380 h340 vUSAIResult Multi WantReturn VScroll

    Gui, USAIG:Add, Button, x530 y602 w100 h35 gUSAIInsertResult, 插入報告
    Gui, USAIG:Add, Button, x640 y602 w100 h35 gUSAICopyResult, 複製結果
    Gui, USAIG:Add, Button, x750 y602 w100 h35 gUSAIClearResult, 清除結果

    Gui, USAIG:Add, Text, x10 y677 w880 h20 vUSAIStatus Center, 就緒 (Backend: OpenAI GPT-5.4)

    Gui, USAIG:Show, w900 h707
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

; --- 匯出裁切圖：裁切當前影像並複製到剪貼簿 + 存檔 ---
USAIExportCrop:
    ; 檢查 current 截圖是否存在
    tempFile := A_Temp . "\usai_current.png"
    if (!FileExist(tempFile)) {
        MsgBox, 48, 提示, 尚未截取影像。請先按「截取當前影像」。
        return
    }

    GuiControlGet, doCrop, USAIG:, USAICropImage
    exportPath := A_ScriptDir . "\usai_cropped.png"

    if (doCrop) {
        ; 裁切後存檔
        CreateAIImage(tempFile, exportPath, 90)
    } else {
        ; 不裁切，直接複製
        FileCopy, %tempFile%, %exportPath%, 1
    }

    ; 複製到剪貼簿（PowerShell，64-bit 相容）
    RunWait, powershell.exe -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::SetImage([System.Drawing.Image]::FromFile('%exportPath%'))", , Hide

    GuiControl, USAIG:, USAIStatus, 裁切圖已匯出: %exportPath% (已複製到剪貼簿)
return


; ============================================================================
; OCR 結果格式化函數
; ============================================================================

; 將 OCR 辨識結果格式化為報告格式
; 輸入：location = "Rt(12/21)", dimension = "8.8*3.7"
; 輸出：Rt 10/6: 7.6*3.3mm.(Srs/Img:1/_) _
FormatOCRToReport(location, dimension, imgNum := "_") {
    global USAI_DICOMSeries, USAI_DICOMInstance

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

    ; 3. 處理 Series/Instance Number (優先使用 DICOM，回退到 OCR)
    seriesNum := (USAI_DICOMSeries != "") ? USAI_DICOMSeries : "1"
    instanceNum := (USAI_DICOMInstance != "") ? USAI_DICOMInstance : imgNum
    if (instanceNum = "")
        instanceNum := "_"

    ; 4. 組合輸出格式：Rt 10/6: 7.6*3.3mm.(Srs/Img:1/5) _
    result := sideFormatted . " " . positionNumbers . ": " . dimensionFormatted . "mm.(Srs/Img:" . seriesNum . "/" . instanceNum . ") _"

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
		gosub USAICopyOCR1
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


; 將 GDI+ pBitmap 儲存為 PNG (使用硬編碼 CLSID，繞過 Gdip_SaveBitmapToFile 的編碼器列舉問題)
; Gdip.ahk 的 Gdip_SaveBitmapToFile 在 64-bit AHK + Win11 下結構體偏移量不正確，
; 導致找不到 PNG 編碼器 (回傳 -3)。此函式直接使用 PNG CLSID 呼叫 GdipSaveImageToFile。
SavePBitmapToPNG(pBitmap, filePath) {
    ; PNG Encoder CLSID: {557CF406-1A04-11D3-9A73-0000F81EF32E}
    VarSetCapacity(pCodec, 16, 0)
    NumPut(0x557CF406, pCodec, 0, "uint")
    NumPut(0x1A04, pCodec, 4, "ushort")
    NumPut(0x11D3, pCodec, 6, "ushort")
    NumPut(0x9A, pCodec, 8, "uchar")
    NumPut(0x73, pCodec, 9, "uchar")
    NumPut(0x00, pCodec, 10, "uchar")
    NumPut(0x00, pCodec, 11, "uchar")
    NumPut(0xF8, pCodec, 12, "uchar")
    NumPut(0x1E, pCodec, 13, "uchar")
    NumPut(0xF3, pCodec, 14, "uchar")
    NumPut(0x2E, pCodec, 15, "uchar")

    return DllCall("gdiplus\GdipSaveImageToFile", "ptr", pBitmap, "wstr", filePath, "ptr", &pCodec, "uint", 0)
}

; 獲取剪貼簿中的影像並儲存
GetClipboardImageAndSave(imageType) {
    ; 檢查剪貼簿是否有影像 (CF_BITMAP=2, CF_DIB=8, CF_DIBV5=17)
    ; Win11 某些應用程式可能只提供 CF_DIB 或 CF_DIBV5 格式
    hasBitmap := DllCall("IsClipboardFormatAvailable", "uint", 2)
    hasDIB := DllCall("IsClipboardFormatAvailable", "uint", 8)
    hasDIBV5 := DllCall("IsClipboardFormatAvailable", "uint", 17)
    if (!hasBitmap && !hasDIB && !hasDIBV5) {
        return ""
    }

    ; 使用 GDI+ 從剪貼簿建立點陣圖 (更可靠地處理各種格式)
    tempFile := A_Temp . "\usai_" . imageType . ".png"
    if IsFunc("Gdip_Startup") {
        pToken := Gdip_Startup()
        if (!pToken) {
            return ""
        }
        pBitmap := Gdip_CreateBitmapFromClipboard()
        if (pBitmap < 0 || !pBitmap) {
            ; GDI+ 剪貼簿讀取失敗，回退到手動方式
            Gdip_Shutdown(pToken)
            goto ClipboardManualFallback
        }
        ; 使用硬編碼 PNG CLSID 儲存 (繞過 Gdip_SaveBitmapToFile 的 64-bit 相容性問題)
        result := SavePBitmapToPNG(pBitmap, tempFile)
        Gdip_DisposeImage(pBitmap)
        Gdip_Shutdown(pToken)
        success := (result = 0)
    } else {
        goto ClipboardManualFallback
    }
    goto ClipboardImageSaved

    ClipboardManualFallback:
    if !DllCall("OpenClipboard", "ptr", 0) {
        return ""
    }
    hBitmap := DllCall("GetClipboardData", "uint", 2, "ptr")
    if (!hBitmap) {
        DllCall("CloseClipboard")
        return ""
    }
    success := SaveBitmapToPNG(hBitmap, tempFile)
    DllCall("CloseClipboard")

    ClipboardImageSaved:
    
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

        ; 使用硬編碼 PNG CLSID 儲存 (繞過 Gdip_SaveBitmapToFile 的 64-bit 相容性問題)
        result := SavePBitmapToPNG(pBitmap, filePath)
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

    ; 驗證 API Key
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

    GuiControl, USAIG:Disable, USAIAnalyzeBtn
    GuiControl, USAIG:, USAIStatus, 正在呼叫 GPT-5.4...
    
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
        SysPrompt .= "Analyze the ultrasound image like a breast imager, not only as BI-RADS category selection. "
        SysPrompt .= "Use OCR Data when available for side, clock-face location, distance from nipple, size, and series/image number. "
        SysPrompt .= "Do not invent measurements that are not visible or supplied by OCR. "
        SysPrompt .= "Do not show hidden chain-of-thought; provide only concise, checkable imaging rationale. "
        SysPrompt .= "Output plain text in this exact structure. Keep the first Report line in English; after that, start directly with Traditional Chinese differential diagnosis. "
        SysPrompt .= "Do NOT restate the lesion description in Chinese and do NOT output a generic 病灶分析 section.`n"
        SysPrompt .= "Report line: [side/location]: [size]mm.(Srs/Img:x/y) [concise lesion description].`n"
        SysPrompt .= "## 主要鑑別診斷`n"
        SysPrompt .= "### 1. [最可能診斷]`n"
        SysPrompt .= "- 支持理由: ...`n"
        SysPrompt .= "- 不支持或需確認處: ...`n"
        SysPrompt .= "### 2. [次要鑑別診斷]`n"
        SysPrompt .= "- 支持理由: ...`n"
        SysPrompt .= "- 不支持或需確認處: ...`n"
        SysPrompt .= "### 3. [必要時列低可能但重要診斷]`n"
        SysPrompt .= "- 何時需考慮: ...`n"
        SysPrompt .= "## BI-RADS 判斷`n"
        SysPrompt .= "- 建議分類: BI-RADS [category]`n"
        SysPrompt .= "- 理由: ...`n"
        SysPrompt .= "- 建議: ...`n"
        SysPrompt .= "## 可用報告句`n"
        SysPrompt .= "[English report sentence, concise and directly usable.]"
    } else if (InStr(USAIExamType, "Spine")) {

	SysPrompt := "You are an expert Radiologist. Analyze this Spine X-ray."
	SysPrompt .= " Output a clean, plain-text report in TELEGRAPHIC DIAGNOSTIC style."
	SysPrompt .= " NO Markdown formatting in the final text (no bold, no italics, no headers)."
	SysPrompt .= " Each finding on its own line. Spine findings and non-spine incidental findings separated by a blank line."

	SysPrompt .= "`n`n=== OUTPUT FORMAT ==="
	SysPrompt .= "`nFirst line: L-S Spine ({views}):"
	SysPrompt .= "`nView labels: Single lateral = (Lat.) | AP + lateral = (AP+Lat.) | AP + flex + ext = (AP+Flex.+Ext.) | Flex + ext only = (Flex.+Ext.)"
	SysPrompt .= "`nThen findings, one per line, ordered by clinical importance:"
	SysPrompt .= "`n  1. Compression fracture / acute findings"
	SysPrompt .= "`n  2. Spondylolisthesis / retrolisthesis"
	SysPrompt .= "`n  3. Dynamic instability (flex/ext only)"
	SysPrompt .= "`n  4. Degenerative disc disease / disc space narrowing"
	SysPrompt .= "`n  5. Spondylosis"
	SysPrompt .= "`n  6. Facet joint arthrosis"
	SysPrompt .= "`n  7. Baastrup disease (kissing spinous processes)"
	SysPrompt .= "`n  8. Loss of lordosis"
	SysPrompt .= "`n  9. Bone density (osteopenia / osteoporosis / generalized diminished bone density)"
	SysPrompt .= "`n  10. [blank line]"
	SysPrompt .= "`n  11. Incidental: Intimal calcification of aorta, bowel gas, renal stones, etc."

	SysPrompt .= "`n`n=== PHASE 0: VERTEBRAL COUNTING (Do This First, Every Time) ==="
	SysPrompt .= "`n- Find T12: the lowest vertebra with a rib attached."
	SysPrompt .= "`n- Vertebra directly below T12 = L1. Count downward: L1 -> L2 -> L3 -> L4 -> L5."
	SysPrompt .= "`n- Confirm L5 by identifying sacrum below it."
	SysPrompt .= "`n- If ribs not visible (lateral view cropped), identify sacrum first, count upward: L5 -> L4 -> L3 -> L2 -> L1."
	SysPrompt .= "`n- Common error: assuming a level without confirming T12 rib or sacrum anchor."

	SysPrompt .= "`n`n=== PHASE 1: SYSTEMATIC CHECKLIST (Lateral View) ==="

	SysPrompt .= "`n`n[A: LORDOSIS]"
	SysPrompt .= "`n- Cobb angle (T12 inferior endplate to L5 inferior endplate):"
	SysPrompt .= "`n  < 20 degrees = Loss of lordosis (report it)."
	SysPrompt .= "`n  20-45 degrees = Normal (do NOT report)."
	SysPrompt .= "`n  > 45 degrees = Hyperlordosis (report it)."
	SysPrompt .= "`n- Since precise angle measurement is unreliable by visual inspection, only report when spine appears clearly straightened or kyphotic. When uncertain, do NOT report."

	SysPrompt .= "`n`n[B: COMPRESSION FRACTURE - HIGHEST PRIORITY]"
	SysPrompt .= "`n- THIS IS THE MOST COMMONLY MISSED FINDING. Deliberately slow down and check each vertebra."
	SysPrompt .= "`n- At EACH level, compare anterior height (Ha) vs posterior height (Hp)."
	SysPrompt .= "`n- Ha < 80% of Hp = compression fracture (anterior wedging)."
	SysPrompt .= "`n- Focus T11-L2 (most common) but check ALL levels."
	SysPrompt .= "`n- Both Ha and Hp reduced vs adjacent levels = burst fracture pattern."
	SysPrompt .= "`n- Biconcave deformity (both endplates depressed) = insufficiency fracture pattern."

	SysPrompt .= "`n`n[C: SPONDYLOLISTHESIS / RETROLISTHESIS]"
	SysPrompt .= "`n- Trace posterior vertebral body line from top to bottom (may be gentle curve)."
	SysPrompt .= "`n- Displacement must be > 5% of endplate AP length to report. < 5% = not significant, do NOT report."
	SysPrompt .= "`n- Check EVERY level, not just L4/5. Multilevel listhesis (e.g. L2/3/4) is common in elderly."
	SysPrompt .= "`n- Anterolisthesis grading (use 'Grade'):"
	SysPrompt .= "`n  Grade I: 5-25%, Grade II: 25-50%, Grade III: >50% (rare)."
	SysPrompt .= "`n- Retrolisthesis grading (use 'Mild/Moderate/Severe'):"
	SysPrompt .= "`n  Mild: 5-25%, Moderate: 25-50%, Severe: >50%."
	SysPrompt .= "`n- Do NOT mix terminology: anterolisthesis = Grade, retrolisthesis = severity words."
	SysPrompt .= "`n- When uncertain whether displacement meets 5% threshold, do NOT report."

	SysPrompt .= "`n`n[D: DISC SPACE]"
	SysPrompt .= "`n- Normal: disc height increases from upper to lower lumbar (L1/2 < L2/3 < L3/4 < L4/5)."
	SysPrompt .= "`n- If a disc space is narrower than the one above it = disc space narrowing."
	SysPrompt .= "`n- L5/S1: physiologically may be lower than L4/5. Only report if very obviously reduced."
	SysPrompt .= "`n- Report ALL levels with narrowing, not just the most obvious one."
	SysPrompt .= "`n- IMPORTANT DISTINCTION:"
	SysPrompt .= "`n  'Disc space narrowing' = requires directly visible height reduction."
	SysPrompt .= "`n  'Degenerative disc disease' = can report when endplate sclerosis present even if disc height unclear (e.g. obscured by osteophytes)."
	SysPrompt .= "`n  These are NOT synonyms. Use appropriate term based on what you can actually see."
	SysPrompt .= "`n- When large osteophytes obscure disc space:"
	SysPrompt .= "`n  Endplate sclerosis visible = report 'degenerative disc disease' at that level."
	SysPrompt .= "`n  No sclerosis and height unclear = do not report."

	SysPrompt .= "`n`n[E: SPONDYLOSIS / OSTEOPHYTES]"
	SysPrompt .= "`n- Report as 'Spondylosis of spine' - summary term covering osteophyte formation."
	SysPrompt .= "`n- Do NOT need to specify every level unless specifically asked."

	SysPrompt .= "`n`n[F: FACET JOINT ARTHROSIS]"
	SysPrompt .= "`n- Look for sclerosis, hypertrophy of facet joints."
	SysPrompt .= "`n- Report as 'Facet joint arthrosis of lumbar spine'."
	SysPrompt .= "`n- Only report when clearly visible; do not assume based on age alone."

	SysPrompt .= "`n`n[G: POSTERIOR ELEMENTS]"
	SysPrompt .= "`n- Spinous processes: if lower lumbar spinous processes touching or show sclerosis at contact = Baastrup disease / kissing spinous processes."
	SysPrompt .= "`n- Pedicles (AP view): absent pedicle = red flag for metastasis."

	SysPrompt .= "`n`n[H: BONE DENSITY]"
	SysPrompt .= "`n- Osteopenia / osteoporosis / generalized diminished bone density."
	SysPrompt .= "`n- Subjective on plain X-ray, acceptable variation between readers."

	SysPrompt .= "`n`n[I: SOFT TISSUE & INCIDENTALS - Always Check]"
	SysPrompt .= "`n- Intimal calcification of aorta: visible anterior to vertebral bodies. Check EVERY lateral view. Frequently missed."
	SysPrompt .= "`n- Bowel gas: if increased, report 'Mild increased bowel gas' or 'Mild ileus'."
	SysPrompt .= "`n- Renal stones: mainly visible on AP view."
	SysPrompt .= "`n- Surgical hardware: describe type and location if present."

	SysPrompt .= "`n`n=== PHASE 2: FLEXION-EXTENSION VIEWS ==="
	SysPrompt .= "`n- When two images from same patient with close timestamps are provided:"
	SysPrompt .= "`n  Identify which is flexion (lordosis reduced/reversed) and which is extension (lordosis accentuated)."
	SysPrompt .= "`n  Compare posterior vertebral body line alignment between two views."
	SysPrompt .= "`n  If stable: report 'No obvious hypermobility.' - this is sufficient."
	SysPrompt .= "`n  If unstable: describe level and type."

	SysPrompt .= "`n`n=== PHASE 3: AP VIEW ==="
	SysPrompt .= "`n- Scoliosis (convexity direction, severity)."
	SysPrompt .= "`n- Pedicle integrity (absent pedicle = red flag)."
	SysPrompt .= "`n- Vertebral body heights (compression fractures ARE visible on AP)."
	SysPrompt .= "`n- Renal stones, bowel gas."

	SysPrompt .= "`n`n=== POOR IMAGE QUALITY ==="
	SysPrompt .= "`n- If contrast is poor or bowel gas significantly obscures spine, append at end:"
	SysPrompt .= "`n  *Poor image contrast, lesion may be obscured."
	SysPrompt .= "`n- Do NOT compensate for poor visibility by fabricating uncertain findings."

	SysPrompt .= "`n`n=== COMMON ERRORS TO AVOID ==="
	SysPrompt .= "`n- Missing compression fracture: check Ha vs Hp at EVERY level."
	SysPrompt .= "`n- Wrong disc level: always count from T12 rib or sacrum."
	SysPrompt .= "`n- Over-reporting listhesis: must exceed 5% threshold; when uncertain, don't report."
	SysPrompt .= "`n- Missing multilevel listhesis: check EVERY level, not just L4/5."
	SysPrompt .= "`n- Missing aortic calcification: check anterior to vertebral bodies on EVERY lateral."
	SysPrompt .= "`n- Only reporting most obvious disc narrowing: report ALL levels."
	SysPrompt .= "`n- Confusing disc narrowing vs degenerative disc disease: narrowing = visible height loss; DDD = sclerosis alone is enough."
	SysPrompt .= "`n- Missing Baastrup disease: check spinous process spacing in lower lumbar."

	SysPrompt .= "`n`n=== EXAMPLE OUTPUT: Lateral ==="
	SysPrompt .= "`nL-S Spine (Lat.):"
	SysPrompt .= "`nGrade I spondylolisthesis of L4/5."
	SysPrompt .= "`nMild retrolisthesis of L2/3."
	SysPrompt .= "`nDegenerative disc disease with L4/5 disc space narrowing."
	SysPrompt .= "`nSpondylosis of spine."
	SysPrompt .= "`nFacet joint arthrosis of lumbar spine."
	SysPrompt .= "`nOsteoporotic change of visible bony structures."
	SysPrompt .= "`n"
	SysPrompt .= "`nIntimal calcification of aorta."

	SysPrompt .= "`n`n=== EXAMPLE OUTPUT: Flex+Ext ==="
	SysPrompt .= "`nL-S Spine (AP+Flex.+Ext.):"
	SysPrompt .= "`nNo obvious hypermobility."
	SysPrompt .= "`nGrade I spondylolisthesis of L2/3/4."
	SysPrompt .= "`nDegenerative disc disease with L4/5 disc space narrowing."
	SysPrompt .= "`nSpondylosis of spine."
	SysPrompt .= "`nGeneralized diminished bone density."
	SysPrompt .= "`nFacet joint arthrosis of lumbar spine."
	SysPrompt .= "`n"
	SysPrompt .= "`nIntimal calcification of aorta."
	
	
    } else if (InStr(USAIExamType, "CXR")) {
	SysPrompt := "You are an expert Board-Certified Radiologist. Analyze this Chest X-ray."
	SysPrompt .= " Output a clean, plain-text report in TELEGRAPHIC DIAGNOSTIC style."
	SysPrompt .= " NO Markdown formatting in the final text (no bold, no italics, no headers). Use hyphens '- ' for each line."

	SysPrompt .= "`n`n=== PHASE 1: TECHNICAL & PATIENT ASSESSMENT (Internal - do not output) ==="
	SysPrompt .= "`n- View: PA / AP / Lateral / Decubitus."
	SysPrompt .= "`n- Rotation: Check spinous processes centered between clavicular heads."
	SysPrompt .= "`n- Inspiration: Good (>=9 posterior ribs above diaphragm) / Poor."
	SysPrompt .= "`n- Estimate patient age from visual cues: bone density, aortic knob, disc degeneration, soft tissue."

	SysPrompt .= "`n`n=== PHASE 2: SYSTEMATIC ANALYSIS (Follow this order strictly) ==="

	SysPrompt .= "`n`n[1. LUNGS - The Anchor, most critical]"
	SysPrompt .= "`n- Compare both lung fields systematically: apex -> mid -> base."
	SysPrompt .= "`n- NORMAL: output exactly 'No active lung lesion is noted.'"
	SysPrompt .= "`n- IF ABNORMAL, use the most specific applicable:"
	SysPrompt .= "`n  a. Infiltration: 'Patchy opacity/infiltration in [RUL/RML/RLL/LUL/LLL], could be pneumonia or others.'"
	SysPrompt .= "`n  b. Consolidation: 'Consolidation with air bronchograms in [location], could be pneumonia or others.'"
	SysPrompt .= "`n  c. Mass/Nodule: 'A nodular opacity/mass lesion in [location]. Recommend CT for further evaluation.'"
	SysPrompt .= "`n  d. Emphysema/COPD: 'Hyperinflated lungs with flattened diaphragms, compatible with COPD/emphysematous change.'"
	SysPrompt .= "`n  e. Congestion: 'Bilateral perihilar haziness and upper lobe venous distention, compatible with pulmonary congestion.'"
	SysPrompt .= "`n  f. Old TB/Fibrosis: 'Fibrocalcified change in [bilateral upper lobes / location], suspect old infection/inflammatory changes, eg. old TB or others.'"
	SysPrompt .= "`n  g. Atelectasis: 'Band-like opacity/volume loss in [location], compatible with atelectasis.'"
	SysPrompt .= "`n  h. Interstitial: 'Reticular/reticulonodular pattern in [location], suggest interstitial lung disease. Recommend CT correlation.'"

	SysPrompt .= "`n`n[2. PLEURA]"
	SysPrompt .= "`n- Costophrenic angles: Sharp (normal) / Blunted (effusion)."
	SysPrompt .= "`n  If blunted: 'Blunting of [R/L/bilateral] costophrenic angle(s), suggesting pleural effusion.'"
	SysPrompt .= "`n  Grade: Small / Moderate / Large."
	SysPrompt .= "`n- Pneumothorax: 'Pneumothorax at [R/L] [apex/hemithorax].'"
	SysPrompt .= "`n- Pleural thickening: 'Apical pleural thickening [bilateral/unilateral].'"
	SysPrompt .= "`n- If all normal: omit this section entirely."

	SysPrompt .= "`n`n[3. HEART]"
	SysPrompt .= "`n- Cardiothoracic ratio (CTR) on PA view:"
	SysPrompt .= "`n  CTR <0.5 -> 'Normal heart size.'"
	SysPrompt .= "`n  CTR 0.5-0.55 -> 'Borderline cardiomegaly.'"
	SysPrompt .= "`n  CTR >0.55 -> 'Cardiomegaly.'"
	SysPrompt .= "`n- On AP view: 'Heart size appears mildly enlarged, may be accentuated by AP projection.'"

	SysPrompt .= "`n`n[4. AORTA & MEDIASTINUM]"
	SysPrompt .= "`n- ONLY report what is visually evident. Do NOT assume calcification based on age alone."
	SysPrompt .= "`n  Calcification seen -> 'Intimal calcification of aorta.'"
	SysPrompt .= "`n  Tortuous -> 'Tortuous aorta with intimal calcification.'"
	SysPrompt .= "`n  Dilated -> 'Dilated ascending aorta.'"
	SysPrompt .= "`n  Widened mediastinum -> 'Mild mediastinal widening.'"
	SysPrompt .= "`n- Hilar prominence/lymphadenopathy: note if present."
	SysPrompt .= "`n- Tracheal deviation: note direction if present."
	SysPrompt .= "`n- If all normal: omit this section entirely."

	SysPrompt .= "`n`n[5. DIAPHRAGM]"
	SysPrompt .= "`n- Elevated hemidiaphragm: note side."
	SysPrompt .= "`n- Free air under diaphragm -> 'Free air under [R/L] hemidiaphragm. Pneumoperitoneum? Clinical correlation required.'"
	SysPrompt .= "`n- Flattened diaphragm -> supports COPD (report with lungs)."
	SysPrompt .= "`n- If normal: omit this section entirely."

	SysPrompt .= "`n`n[6. BONES & SOFT TISSUE]"
	SysPrompt .= "`n- IF visually normal (young, no degeneration) -> 'Unremarkable bony structure.'"
	SysPrompt .= "`n- IF degenerative changes visible -> 'Degenerative change and spur formation of spine.'"
	SysPrompt .= "`n- IF reduced bone density visible -> add 'Generalized diminished bone density.' or 'Osteoporotic change of visible bony structures.' if severe."
	SysPrompt .= "`n- Rib fractures: note level and side if seen."
	SysPrompt .= "`n- Soft tissue: subcutaneous emphysema, mastectomy, chest wall mass."

	SysPrompt .= "`n`n[7. DEVICES & FOREIGN BODIES - Only if present]"
	SysPrompt .= "`n- ETT: 'Status post endotracheal tube insertion with tip approximately [X] cm above carina.'"
	SysPrompt .= "`n- CVC: 'Status post central venous catheter via [R/L] [subclavian/IJ] with tip in SVC.'"
	SysPrompt .= "`n- NGT: 'Status post nasogastric tube insertion with tip in stomach.'"
	SysPrompt .= "`n- Chest tube: 'Chest tube in [R/L] hemithorax.'"
	SysPrompt .= "`n- Pacemaker/ICD: 'Pacemaker/ICD with leads in [RA/RV/CS].'"
	SysPrompt .= "`n- Port-A-Cath: 'Implantable port via [side] with tip in SVC.'"
	SysPrompt .= "`n- Sternal wires, IABP, ECMO, or other devices: describe accordingly."
	SysPrompt .= "`n- If no devices: omit this section entirely."

	SysPrompt .= "`n`n[8. OTHERS - Only if present]"
	SysPrompt .= "`n- Distended stomach."
	SysPrompt .= "`n- Calcified granuloma."
	SysPrompt .= "`n- Any other incidental findings."
	SysPrompt .= "`n- If none: omit this section entirely."

	SysPrompt .= "`n`n=== OUTPUT STRUCTURE (Strict) ==="
	SysPrompt .= "`n(Output strictly as a list of lines starting with '- '. Only include lines for findings present or required.)"
	SysPrompt .= "`n- [Lungs - ALWAYS include. Default: 'No active lung lesion is noted.']"
	SysPrompt .= "`n- [Pleura - Include if effusion, pneumothorax, or thickening. Omit if normal.]"
	SysPrompt .= "`n- [Heart - ALWAYS include. Default: 'Normal heart size.']"
	SysPrompt .= "`n- [Aorta/Mediastinum - Include ONLY if calcification, tortuosity, dilation, or deviation is VISIBLE. Do NOT assume.]"
	SysPrompt .= "`n- [Diaphragm - Include only if abnormal. Omit if normal.]"
	SysPrompt .= "`n- [Bones - ALWAYS include. Select: 'Unremarkable bony structure' OR specific findings.]"
	SysPrompt .= "`n- [Devices - Include each device on its own line. Omit if no devices.]"
	SysPrompt .= "`n- [Others - Omit if none.]"

	
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
	SysPrompt .= " `n2. **Talar Dome:** Check for Osteochondral lesions (OCD) or 'Valgus deformity'."
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

    promptPrefix := SysPrompt

    if (USAIChoice1) {
        UserPrompt := promptPrefix . "`n`nPlease analyze this image."
        if (USAI_CurrentOCRText != "") {
            UserPrompt .= "`nOCR Data: " . USAI_CurrentOCRText
        }
        if (InStr(USAIExamType, "Breast"))
            UserPrompt .= "`nReturn exactly one English Report line, then start at ## 主要鑑別診斷. Do not output 病灶分析, Impression, or a Comparison section."
        else
            UserPrompt .= "`nOutput format: Location, Size, Description, Impression. (In English)"
        images.Push(USAI_CurrentImage)
    } else if (USAIChoice2) {
        UserPrompt := promptPrefix . "`n`nAnalyze these TWO images as two current views/images of the SAME lesion, not as old-vs-new comparison."
        if (USAI_CurrentOCRText != "" || USAI_PreviousOCRText != "") {
             UserPrompt .= "`nOCR Data - Image 1: " . USAI_CurrentOCRText . ", Image 2: " . USAI_PreviousOCRText
        }
        if (InStr(USAIExamType, "Breast"))
            UserPrompt .= "`nReturn exactly one English Report line, then start at ## 主要鑑別診斷. Do not output 病灶分析, Impression, or a Comparison section. Do not compare the two images."
        else
            UserPrompt .= "`nOutput format (Single line): Location, Size, Description, Comparison findings. (In English)"
        images.Push(USAI_CurrentImage)
        images.Push(USAI_PreviousImage)
    } else if (USAIChoice3) {
        UserPrompt := promptPrefix . "`n`nCompare size change. Image 1 is PREVIOUS, Image 2 is CURRENT."
        if (USAI_CurrentOCRText != "" || USAI_PreviousOCRText != "") {
             UserPrompt .= "`nOCR Data - Previous: " . USAI_PreviousOCRText . ", Current: " . USAI_CurrentOCRText
        }
        if (InStr(USAIExamType, "Breast"))
            UserPrompt .= "`nReturn Report line, size change, lesion analysis, BI-RADS reasoning, and Impression."
        else
            UserPrompt .= "`nOutput format (Single line): Location, Size change, Brief description. (In English)"
        images.Push(USAI_PreviousImage)
        images.Push(USAI_CurrentImage)
    }

    ; === 3. 呼叫 API (非同步) ===
    modelID := "gpt-5.4"
    g_USAI_StartTick := A_TickCount
    g_USAI_LastModel := modelID
    started := StartOpenAIBackgroundJob(USAIAPIKey, modelID, UserPrompt, images, useThinking)
    if (!started) {
        GuiControl, USAIG:Enable, USAIAnalyzeBtn
        GuiControl, USAIG:, USAIStatus, 無法啟動 GPT 背景程序
        return
    }
    
    ; 啟動計時器，每 1 秒檢查一次結果
    SetTimer, CheckOpenAIResult, 1000
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

CheckOpenAIResult:
    resultFile := A_Temp . "\openai_usai_response.txt"
    elapsed_s := Round((A_TickCount - g_USAI_StartTick) / 1000, 1)
    
    ; 檢查結果檔案是否存在
    if (FileExist(resultFile)) {
        ; 停止計時器
        SetTimer, CheckOpenAIResult, Off
        
        ; 讀取結果 (指定 UTF-8 編碼)
        FileRead, resultText, *P65001 %resultFile%
        
        ; 更新 GUI (Backend-aware)
        GuiControl, USAIG:Enable, USAIAnalyzeBtn

        if (SubStr(resultText, 1, 10) = "HTTP_ERROR" || SubStr(resultText, 1, 9) = "API Error") {
            GuiControl, USAIG:, USAIResult, %resultText%
            GuiControl, USAIG:, USAIStatus, 分析失敗或發生錯誤
        } else if (resultText != "") {
            finalResult := ParseOpenAIResponse(resultText)
            
            ; 如果解析失敗(可能背景腳本直接寫入了錯誤訊息)，直接顯示原文
            if (SubStr(finalResult, 1, 22) = "Error parsing response")
                finalResult := resultText
                
            GuiControl, USAIG:, USAIResult, %finalResult%
            GuiControl, USAIG:, USAIStatus, % "分析完成！(" elapsed_s "s / " g_USAI_LastModel ")"
        } else {
            GuiControl, USAIG:, USAIResult, %resultText%
            GuiControl, USAIG:, USAIStatus, 分析失敗或發生錯誤
        }
        
        ; 清理臨時檔案
        FileDelete, %resultFile%
        FileDelete, %A_Temp%\openai_usai_request.json
        FileDelete, %A_Temp%\openai_usai_worker.ahk
    }
    else {
        if (elapsed_s > 180) {
            SetTimer, CheckOpenAIResult, Off
            GuiControl, USAIG:Enable, USAIAnalyzeBtn
            GuiControl, USAIG:, USAIStatus, % "逾時（>180s / " g_USAI_LastModel "）"
            FileDelete, %A_Temp%\openai_usai_request.json
            FileDelete, %A_Temp%\openai_usai_worker.ahk
        } else {
            GuiControl, USAIG:, USAIStatus, % "GPT-5.4 分析中... " elapsed_s "s"
        }
    }
return

StartOpenAIBackgroundJob(apiKey, modelID, prompt, images, useThinking) {
    ; 1. 構建完整的 JSON 字串 (OpenAI Responses API)
    jsonBody := BuildOpenAIResponsesJSON(modelID, prompt, images, useThinking)
    
    ; 2. 將 JSON 寫入臨時檔案 (解決命令列長度限制)
    requestFile := A_Temp . "\openai_usai_request.json"
    FileDelete, %requestFile%
    FileAppend, %jsonBody%, %requestFile%, UTF-8
    
    ; 3. 準備結果檔案路徑
    resultFile := A_Temp . "\openai_usai_response.txt"
    FileDelete, %resultFile%
    
    ; 4. 建立背景 Worker 腳本
    ; 這個腳本非常精簡，只負責讀 JSON -> POST -> 寫入結果
    workerScriptPath := A_Temp . "\openai_usai_worker.ahk"
    FileDelete, %workerScriptPath%
    
    endpoint := "https://api.openai.com/v1/responses"
    
    ; 構建 Worker 腳本內容
    workerCode = 
    (
    #NoTrayIcon
    FileRead, jsonBody, *P65001 %requestFile%
    
    url := "%endpoint%"
    
    whr := ComObjCreate("WinHttp.WinHttpRequest.5.1")
    whr.Open("POST", url, false)
    whr.SetRequestHeader("Content-Type", "application/json; charset=utf-8")
    whr.SetRequestHeader("Authorization", "Bearer %apiKey%")
    whr.SetTimeouts(30000, 60000, 30000, 180000) ; 180秒超時
    
    try {
        whr.Send(jsonBody)
        if (whr.Status = 200) {
            FileAppend, `% whr.ResponseText, %resultFile%, UTF-8
        } else {
            err := "HTTP_ERROR " . whr.Status . Chr(10) . whr.ResponseText
            FileAppend, `% err, %resultFile%, UTF-8
        }
    } catch e {
        err := "API Error: " . e.Message
        FileAppend, `% err, %resultFile%, UTF-8
    }
    ExitApp
    )
    
    FileAppend, %workerCode%, %workerScriptPath%, UTF-8
    
    ; 5. 執行背景腳本 (使用 Run 不會卡住主程式)
    Run, "%A_AhkPath%" "%workerScriptPath%",, Hide UseErrorLevel
    if (ErrorLevel)
        return false
    return true
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
    ; 檢查剪貼簿是否有影像 (CF_BITMAP=2, CF_DIB=8, CF_DIBV5=17)
    ; Win11 某些應用程式可能只提供 CF_DIB 或 CF_DIBV5 格式
    hasBitmap := DllCall("IsClipboardFormatAvailable", "uint", 2)
    hasDIB := DllCall("IsClipboardFormatAvailable", "uint", 8)
    hasDIBV5 := DllCall("IsClipboardFormatAvailable", "uint", 17)
    if (!hasBitmap && !hasDIB && !hasDIBV5) {
        return ""
    }

    ; 優先使用 GDI+ 從剪貼簿讀取 (更可靠地處理 Win11 格式)
    if IsFunc("Gdip_Startup") {
        pToken := Gdip_Startup()
        if (pToken) {
            pBitmap := Gdip_CreateBitmapFromClipboard()
            if (pBitmap > 0) {
                tempFile := A_Temp . "\temp_clipboard_" . A_TickCount . ".png"
                ; 使用硬編碼 PNG CLSID 儲存 (繞過 Gdip_SaveBitmapToFile 的 64-bit 相容性問題)
                result := SavePBitmapToPNG(pBitmap, tempFile)
                Gdip_DisposeImage(pBitmap)
                Gdip_Shutdown(pToken)
                if (result = 0) {
                    base64 := B64EncodeFile(tempFile)
                    FileDelete, %tempFile%
                    if (base64 != "") {
                        return "data:image/png;base64," . base64
                    }
                }
                return ""
            }
            Gdip_Shutdown(pToken)
        }
    }

    ; 回退：手動開啟剪貼簿取得 CF_BITMAP
    if !DllCall("OpenClipboard", "ptr", 0) {
        return ""
    }

    hBitmap := DllCall("GetClipboardData", "uint", 2, "ptr")
    if (!hBitmap) {
        DllCall("CloseClipboard")
        return ""
    }

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
    
    ; 使用硬編碼 PNG CLSID 儲存 (繞過 Gdip_SaveBitmapToFile 的 64-bit 相容性問題)
    result := SavePBitmapToPNG(pBitmap, tempFile)
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




; ============================================================================
; OpenAI GPT-5.4 / legacy Gemini API helpers
; ============================================================================
BuildOpenAIResponsesJSON(modelID, prompt, images, useThinking) {
    json := "{""model"":" . JEscape(modelID) . ",""input"":[{""role"":""user"",""content"":["
    json .= "{""type"":""input_text"",""text"":" . JEscape(prompt) . "}"

    for index, imgData in images {
        json .= ","
        json .= "{""type"":""input_image"",""image_url"":" . JEscape(imgData) . ",""detail"":""high""}"
    }

    json .= "]}],""max_output_tokens"":4000"
    if (useThinking)
        json .= ",""reasoning"":{""effort"":""medium""}"
    json .= "}"
    return json
}

ParseOpenAIResponse(responseText) {
    ; Responses API returns output text blocks inside output[].content[].
    ; Keep the last text block in case the model emits multiple output_text items.
    if RegExMatch(responseText, """status""\s*:\s*""incomplete""") {
        reason := RegGet(responseText, """reason""\s*:\s*""((?:\\.|[^""\\])*)""")
        used := RegGet(responseText, """output_tokens""\s*:\s*(\d+)")
        return "OpenAI response incomplete: " . JsonUnescape(reason) . " (output tokens used: " . used . "). Please retry; output budget has been increased."
    }

    finalResult := ""
    pos := 1
    while (pos := RegExMatch(responseText, """text""\s*:\s*""((?:\\.|[^""\\])*)""", match, pos)) {
        finalResult := match1
        pos += StrLen(match)
    }

    if (finalResult != "")
        return JsonUnescape(finalResult)

    if RegExMatch(responseText, """message""\s*:\s*""((?:\\.|[^""\\])*)""", err)
        return "Error parsing response: " . JsonUnescape(err1)

    return "Error parsing response: " . responseText
}

JsonUnescape(text) {
    text := StrReplace(text, "\""", """")
    text := StrReplace(text, "\/", "/")
    text := StrReplace(text, "\n", "`n")
    text := StrReplace(text, "\r", "`r")
    text := StrReplace(text, "\t", "`t")
    text := DecodeUnicodeEscapes(text)
    text := StrReplace(text, "\\", "\")
    return text
}

DecodeUnicodeEscapes(text) {
    while RegExMatch(text, "\\u([0-9A-Fa-f]{4})", m) {
        code := HexToInt(m1)
        text := StrReplace(text, m, UnicodeChar(code))
    }
    return text
}

HexToInt(hex) {
    n := 0
    Loop, Parse, hex
    {
        ch := A_LoopField
        if ch is xdigit
        {
            if ch is digit
                v := ch + 0
            else
                v := Asc(ch) - (Asc(ch) >= 97 ? 87 : 55)
            n := (n * 16) + v
        }
    }
    return n
}

UnicodeChar(code) {
    if (A_IsUnicode)
        return Chr(code)

    ; ANSI AutoHotkey cannot represent Chr(0x4e00) directly.
    ; Convert one UTF-16 code unit to the system code page instead.
    VarSetCapacity(wchar, 2, 0)
    NumPut(code, wchar, 0, "UShort")
    size := DllCall("WideCharToMultiByte", "UInt", 0, "UInt", 0
        , "Ptr", &wchar, "Int", 1
        , "Ptr", 0, "Int", 0
        , "Ptr", 0, "Ptr", 0)
    if (size <= 0)
        return ""

    VarSetCapacity(mb, size + 1, 0)
    DllCall("WideCharToMultiByte", "UInt", 0, "UInt", 0
        , "Ptr", &wchar, "Int", 1
        , "Ptr", &mb, "Int", size
        , "Ptr", 0, "Ptr", 0)
    return StrGet(&mb, size, "CP0")
}

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
    
    ; 儲存裁切後的影像 (使用硬編碼 PNG CLSID)
    SavePBitmapToPNG(pBitmapCropped, outputPath)
    
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
    
    ; 裁切並儲存 (使用硬編碼 PNG CLSID)
    Gdip_DrawImage(pGraphics, pBitmap, 0, 0, origWidth, keepHeight, 0, cropY, origWidth, keepHeight)
    SavePBitmapToPNG(pBitmapAI, outputPath)
    
    ; 清理
    Gdip_DeleteGraphics(pGraphics)
    Gdip_DisposeImage(pBitmapAI)
    Gdip_DisposeImage(pBitmap)
    Gdip_Shutdown(pToken)
    
    return true
}

; 複製 OCR 1 結果
USAICopyOCR1:
    if (USAI_CurrentOCRText != "") {
        Clipboard := USAI_CurrentOCRText
        GuiControl, USAIG:, USAIStatus, OCR 1 報告格式已複製到剪貼簿
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
    if (USAI_PreviousOCRText != "") {
        Clipboard := USAI_PreviousOCRText
        GuiControl, USAIG:, USAIStatus, OCR 2 報告格式已複製到剪貼簿
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
