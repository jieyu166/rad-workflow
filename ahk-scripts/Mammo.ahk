#include d8888basic.ahk
; BMD相關全局變數
global useChinese := 0
global BMDStyle:=1
global StoredText

;============================================================================================
; Mammo
;============================================================================================

:*:bd::
Input, key, L1 T2
if (key == "a")
    SendInput, BIRADS density A - The breasts are almost entirely fatty.
else if (key == "b" )
    SendInput, BIRADS density B - There are scattered areas of fibroglandular density.
else if (key == "c")
    SendInput, BIRADS density C - heterogeneously dense breasts, which may obscure small masses.
else if (key == "d" )
    SendInput, BIRADS density D - The breasts are extremely dense, which lowers the sensitivity of mammography.
else
    SendInput, fing%key%
return


::mca;::
HotstringMenuV("A","MenuShortcut", "Benign calcification of _ breast_s.","Round calcifications with lucent center of _ breast_s, typically mammographic benign due to fat necrosis.","Scattered microcalcifications of bilateral breasts, relatively monomorphic pattern, concluded as benign finding.`r_Benign scattered microcalcifications of bilateral breasts.")
return

::mno;::
HotstringMenuV("A","MenuShortcut", "Multiple equal density circumscribed masses of both breasts, typical mammographic appearance of cysts, fibroadenomas, asymmetric glands, concluded as benign.","_However, some lesion may have normal mammographic appearance, regular follow up is still suggested.")
return

;=====================================================================
; 日期格式轉換功能
; 將選取的 2021-9-2 轉換為 2021.9.2.
;=====================================================================
^!d::  ; 熱鍵: Ctrl + Alt + D
    ; 1. 備份目前的剪貼簿內容，以免覆蓋掉原本複製的東西
    ClipboardBackup := ClipboardAll
    Clipboard := "" ; 清空剪貼簿以進行檢測

    ; 2. 送出複製指令 (Ctrl+C)
    Send, ^c
    ClipWait, 0.3 ; 等待複製完成，最多等 0.3 秒
    if ErrorLevel ; 如果複製失敗(沒選到字)，就結束
    {
        Clipboard := ClipboardBackup
        return
    }

    ; 3. 取得文字並進行處理
    CurrentText := Clipboard
    
    ; --- 正規表示式說明 ---
    ; (\d{4})   : 抓取 4 個數字 (年份)，存為變數 $1
    ; -         : 抓取連字號
    ; (\d{1,2}) : 抓取 1 到 2 個數字 (月份)，存為變數 $2
    ; -         : 抓取連字號
    ; (\d{1,2}) : 抓取 1 到 2 個數字 (日期)，存為變數 $3
    ; 替換成    : $1.$2.$3. (注意最後面有點)
    
    NewText := RegExReplace(CurrentText, "(\d{4})-(\d{1,2})-(\d{1,2})", "$1.$2.$3.")

    ; 4. 將處理好的文字放入剪貼簿並貼上
    Clipboard := NewText
    Send, ^v
    
    ; 等待一下確保貼上完成，再還原剪貼簿
    Sleep, 200
    Clipboard := ClipboardBackup
return


::mammo;::
WinGet, ActiveId, ID, A ;紀錄目前視窗
Gui Font, s12
Gui Add, GroupBox, x20 y15 w150 h100, Title

Gui Add, Radio, xp+15 yp+20 w130 h23 vmammoT1 checked1, Screening(&S)
Gui Add, Radio, xp yp+25 w130 h23 vmammoT2, Diagnostic(&X)
Gui Add, Radio, xp yp+25 w130 h23 vmammoT3, S+D

Gui Add, GroupBox, x20 y120 w150 h100, 舊片
Gui Add, Radio, xp+15 yp+20 w130 h23 vmammoO1, Not(&First)
Gui Add, Radio, xp yp+25 w130 h23 vmammoO2, Not(&Other)
Gui Add, Radio, xp yp+25 w130 h23 vmammoO3 checked1, 有舊片(&Z)

Gui Add, GroupBox, x180 y15 w170 h108, Density

Gui Add, Radio, xp+15 yp+20 w150 h23 vmammoD1, Density &A
Gui Add, Radio, xp yp+20 w150 h23 vmammoD2, Density &B
Gui Add, Radio, xp yp+20 w150 h23 vmammoD3 checked1, Density &C
Gui Add, Radio, xp yp+20 w150 h23 vmammoD4, Density &D


Gui Add, GroupBox, x180 y125 w170 h180, BI-RADS
Gui Add, Radio, xp+15 yp+20 w150 h23 vmammoB0, BI-RADS &0
Gui Add, Radio, xp yp+20 w150 h23 vmammoB1 checked1, BI-RADS &1
Gui Add, Radio, xp yp+20 w150 h23 vmammoB2, BI-RADS &2
Gui Add, Radio, xp yp+20 w150 h23 vmammoB3, BI-RADS &3
Gui Add, Radio, xp yp+20 w150 h23 vmammoB4, BI-RADS &4_
Gui Add, Radio, xp yp+20 w150 h23 vmammoB5, BI-RADS &5
Gui Add, Radio, xp yp+20 w150 h23 vmammoB6, BI-RADS &6


Gui Add, Button, x25 y230 w140 h60 gMammo Default, 輸出(&`)

Gui Show, w380 h400, Mammo

SetTimer, WriteStudyID, 1000

return


Mammo:
Gui, Submit, NoHide
desc := ""

If (mammoT1){
	desc .= "Screening mammography of bilateral breast with CC and MLO views:"
}else if (mammoT2){
	desc .= "Diagnostic mammography of _ breast with spot maginification ML, CC views:"
}else if (mammoT3){
	desc .= "Screening with subsequently immediate diagnostic mammography of bilateral breasts with CC, MLO, spot maginification views:"
}else{
	desc .= "Special screening mammography of _bilateral breast with CC and MLO views:`rScreening 3D mammography (DBT) of bilateral breasts with CC and MLO views:\nBoth 2D (synthesized) images and 3D thin slices are reviewed."
}
desc .= "`r`rComparison of previous mammography(date): "
If (mammoO1){
	desc .= "not available(first mammogram)."
}else if (mammoO2){
	desc .= "not available(other hospital)."
}else{
	desc .= "__"
}
desc .= "`r`rBreast composition: "
If (mammoD1){
	desc .= "BIRADS density A - The breasts are almost entirely fatty."
}else if (mammoD2){
	desc .= "BIRADS density B - There are scattered areas of fibroglandular density."
}else if (mammoD3){
	desc .= "BIRADS density C - heterogeneously dense breasts, which may obscure small masses."
}else{
	desc .= "BIRADS density D - The breasts are extremely dense, which lowers the sensitivity of mammography."
}
desc .= "`r`rFindings:`r"

If (mammoB1){
	If (mammoT2){ 
		desc .= "There is no visible lesion corresponding to the clinically mentioned location at __.`r"
		desc .= "The study is thus concluded as normal, there is no clustered microcalcification, nor architectural distortion noted by this study.`r`r"
	}else{
		desc .= "The screen is normal, there is no clustered microcalcification, nor `rarchitectural distortion noted by this study.`r`r"
	}
	desc .= "BI-RADS assessment:`rCategory 1, negative`r`r"
	desc .= "Recommendation: Annual screening mammography`r`rIMP: No mammographic evidence of malignancy`r`r"
}else if(mammoB2){
	desc .= "___`rThere is no clustered microcalcification, nor architectural distortion `rbilaterally.`r`r"
	desc .= "BI-RADS assessment:`r(BI-RADS category 2, benign)`r`rRecommendation: Annual screening mammography`r`rIMP: __`r`r"
}else if(mammoB3){
	If (mammoT1){ 
		desc .= "Screening mammo is not suitble for BI-RADS3."
	}else{
		desc .= "___`r`rBI-RADS assessment:`r(BI-RADS category 3, probably benign, suggest 6 months follow up)`r`r"
		desc .= "Recommendation: 6-months follow up with mammography.`r`r"
		desc .= "IMP: Probably benign lesion of __ breast, suggest short-interval follow `r     up with mammogram (6 months).`r`r"
	}
}else if(mammoB4){
	If (mammoT1){ 
		desc .= "Screening mammo is not suitble for BI-RADS4."
	}else{
		desc .= "___`r`rBI-RADS assessment:`r__`r`r"
		desc .= "Recommendation: tissue proof by __`r`r"
		desc .= "IMP: Lesion of __ breast, the possibility of malignancy is suspected, `r     suggest tissue proof.`r`r"
	}
}else if(mammoB5){
	If (mammoT1){ 
		desc .= "Screening mammo is not suitble for BI-RADS5."
	}else{
		desc .= "___`r`rBI-RADS assessment:`r(BI-RADS category 5, highly suggestive of malignancy, recommend tissue proof)`r`r"
		desc .= "Recommendation: tissue proof by __`r`r"
		desc .= "IMP: Lesion of __ breast, highly suspected as malignancy, suggest tissue proof.`r`r"
	}
}else if(mammoB6){
	If (mammoT1 OR mammoT3){ 
		desc .= "Screening mammo is not suitble for BI-RADS6."
	}else{
		desc .= "___, compatible with ___ by previous core biopsy.`r___`r`rBI-RADS assessment:`r(BI-RADS category 6, known biopsy proven cancer)`r`r"
		desc .= "Recommendation: appropriate treatment should be taken`r`r"
		desc .= "IMP: __ `r`r"
	}
}else if(mammoB0){
	If (mammoT1){
		desc .= "The screen is not normal, and I stronly suggest further diagnostic `rexamination. Additional recommended imaging studies are listed below.`rAbnormalities:`r__`r`r"
		desc .= "Recommended additional studies: __`r`r"
		desc .= "BI-RADS assessment:`r(BI-RADS category 0, need additional imaging evaluation)`r`r"
		desc .= "IMP: Abnormal screening mammography on __ breast, suggest __."
	}else{
		desc .= "Diagnostic mammo is not suitble for BI-RADS0."
	}
}

If (mammoB1 OR mammoB2 OR mammo B3){
	desc .= "Addendum: Although this report follows the standard lexicon of ACR BI-RADS, `r          small cancers maybe invisible within dense fibroglandular tissue, `r          Adjunct ultrasound screening is always recommended for dense breast."
}

gosub CopyCXRtoHIS
return




;============================================================================================
; BMD
;============================================================================================


::tba;::
WinGet, ActiveId, ID, A ;紀錄目前視窗
Gui Font, s16
Gui Add, Radio, x20 y25 w80 h23 vS1, 男性(&M)
Gui Add, Radio, xp yp+30 w80 h23 vS2, 女性(&F)
Gui Add, Text, x120 y25 w180 h30 +0x200, Total body fat (`%)
Gui Add, Text, xp yp+40 w180 h30 +0x200, Est. VAT area (cm2)
Gui Add, Text, xp yp+40 w180 h30 +0x200, Appen. Lean/Height
Gui Add, Edit, x310 y25 w80 h30 vtbaf
Gui Add, Edit, xp yp+40 w80 h30 vtbavat
Gui Add, Edit, xp yp+40 w80 h30 vtbaa

Gui Add, Button, xp-60 yp+50 w140 h60 gTBA Default, 身體組成分析
Gui Show, w410 h235, Body Composition Assessment
return

TBA:
Gui, Submit, NoHide
tba_m_ob := 35 ;mcufob
tba_m_ow := 23
tba_f_ob := tba_m_ob+3 ;Female: Normal:<25%; Overweight: 25%-38%; Obesity: >38%
tba_f_ow := tba_m_ow+2
tba_m_lean := 7.0
tba_f_lean := 5.4

desc := ""
desc .= "Body Composition Assessment:`r"
if(S1){ ;男性 Male: Normal:<23%; Overweight: 23%-35%; Obesity: >35%
	if(tbaf>tba_m_ob){
		desc .= ". Obesity `r"
	}else if(tbaf>tba_m_ow or tbaf = tba_m_ow){
		desc .= ". Overweight (according to body fat percentage)`r"
	}else{
		desc .= ". Normal body fat percentage`r"
	}
}
else{ ;女性
	if(tbaf>tba_f_ob){
		desc .= ". Obesity `r"
	}else if(tbaf>tba_f_ow or tbaf = tba_f_ow){
		desc .= ". Overweight (according to body fat percentage)`r"
	}else{
		desc .= ". Normal body fat percentage`r"
	}
}
desc .= "     # According to 2018成人肥胖防治實證指引(台灣衛福部): `r"
desc .= "       Male: Normal:<23%; Overweight: 23%-35%; Obesity: >35%`r"
desc .= "       Female: Normal:<25%; Overweight: 25%-38%; Obesity: >38%`r`r"


if(S1){
	if(tbaa<tba_m_lean){
		desc .= ". Low Lean Mass`r"
	}else{
		desc .= ". Normal Lean Mass`r"
	}
}else{
	if(tbaa<tba_f_lean){
		desc .= ". Low Lean Mass`r"
	}else{
		desc .= ". Normal Lean Mass`r"
	}
}
desc .= "      # According to 2019 Asia Sarcopenia Guideline:`r"
desc .= "        Male: 7.0kg/m2`r"
desc .= "        Female: 5.4 kg/m2`r`r"
desc .= "------------------------------------------------------------------------------`r"
desc .= "Body Composition Assessment:`r`r"
desc .= "TECHNIQUE:`r  The examination was performed of the total body composition using the dual x-ray technique (HOLOGIC, Horizon W).`r`r"
desc .= "COMPARISON:`r  None.`r`r"
desc .= "Body Composition Results:`r"
desc .= "  Total body fat percentage: "
desc .= tbaf
desc .= " %`r  Estimated visceral adipose tissue: "
desc .= tbavat
desc .= " cm2`r  Appendicular muscle mass index: "
desc .= tbaa
desc .= " kg/m2`r"

gosub CopyCXRtoHIS
return


::bmd;::
WinGet, ActiveId, ID, A ;紀錄目前視窗
Gui Font, s12
Gui Add, GroupBox, x20 y15 w340 h100, T-score

Gui Add, Radio, xp+15 yp+20 w300 h23 vbmdT1, Normal bone density(&1)
Gui Add, Radio, xp yp+25 w300 h23 vbmdT2, Low bone density (osteopenia)(&2)
Gui Add, Radio, xp yp+25 w300 h23 vbmdT3, Osteoporosis(&3)

Gui Add, Radio, xp yp+55 w300 h23 vbmdZ1, Within the expected range for age(&4)
Gui Add, Radio, xp yp+25 w300 h23 vbmdZ2, Below the expected range for age(&5)

Gui Add, GroupBox, x20 y120 w340 h80, Z-score

Gui Add, GroupBox, x20 y205 w340 h80, 性別
Gui Add, Radio, xp+15 yp+20 w300 h23 vS1 checked1, 男性(&M)
Gui Add, Radio, xp yp+25 w300 h23 vS2, 女性(&F)

Gui Add, CheckBox, xp yp+40 w100 h23 vbmdold, 比較舊片(&C)
Gui Add, CheckBox, xp yp+25 w150 h23 vbmdex, Spine有排除(&S)
Gui Add, CheckBox, xp yp+25 w100 h23 vbmdf, Forearm

Gui Add, Button, xp+180 yp-20 w140 h60 gBMD Default, 輸出範本(&G)

Gui Show, w380 h400, BMD
return

BMD:
Gui, Submit, NoHide
desc := ""

If (bmdold){
		desc .= "Serial Densitometric assessment:`r"
}else{
		desc .= "Baseline Densitometric assessment:`r"
}

desc .= "Based on the WHO densitometric classification, the BMD is "

	IF(bmdT1){
		desc .= """Normal bone density"""
	} else if (bmdT2) {
		desc .= """Low bone density (osteopenia)"""
	} else if (bmdT3) {
		desc .= """Osteoporosis"""
	} else if (bmdZ1) {
		desc .= """Within the expected range for age"""
	} else if (bmdZ2) {
		desc .= """Below the expected range for age"""
	}

If (bmdold){
	desc .= ".`rThe interval change of BMD is statistically stationary.`rThe interval change of BMD is statistically significantly increased at __.`rThe interval change of BMD is statistically significantly decreased at __"
}

	desc .=  ".`r`r"
	desc .= "# According to 2019 ISCD Official Position`r==============================================================================`rINDICATION and HISTORY: `rThe patient is a _ year old asian "

If(S1){
	IF(bmdT1 OR bmdT2 OR bmdT3){
		desc .= "male with risk factors for low bone mineral density.`r"
	} else if (bmdZ1 OR bmdZ2) {
		desc .= "male.`r"
	}
} else {
	IF(bmdT1 OR bmdT2 OR bmdT3){
		desc .= "female with risk factors for low bone mineral density including post-menopausal status.`r"
	} else if (bmdZ1 OR bmdZ2) {
		desc .= "female before menopause.`r"
	}
}
	desc .= "`rTECHNIQUE:`rThe examination was performed of the lumbar spine (L1-4) and left proximal femur " 
	if (bmdf){
		desc .= "and _ forearm "
	}
	desc .= "using the dual x-ray technique (Hologic, Horizon W). `r`rCOMPARISON:`r"
if(bmdold){
	desc .= "Previous BMD: 20__/__/__.`r"
}else{
	desc .= "None.`r"
}
	desc .= "`rBMD results:`r"
if (bmdex){
	desc .= "Spine: `r- The mean BMD measurement in the lumbar spine, L_, is _ g/cm2.`r"
	desc .= "* L_ is excluded because T-score >1SD different from adjacent vertebra.`r* L_ is excluded because severe osteophyte.`r* L_ is excluded because compression fracture.`r"
}else{
	desc .= "Spine: `r- The mean BMD measurement in the lumbar spine, L1-L4, is _ g/cm2.`r"
}
	desc .= "Hip: `r- The BMD measurement in the femoral neck is _ g/cm2.`r- The BMD measurement in the total proximal femur is _ g/cm2.`r"
if (bmdf){
	desc .= "Forearm: `r- The BMD measurement in the distal 33% radius is _ g/cm2.`r"
}
	
	IF(bmdT1 OR bmdT2 OR bmdT3){
		desc .= "`rThe lowest T-score: _`r- compared to the expected BMD for young adult (BMDCS/NHANES White Female).`r"
	} else if (bmdZ1 OR bmdZ2) {
		desc .= "`rThe lowest Z-score: _`r- compared to the expected BMD for age and gender matched asian adult.`r"
	}

gosub CopyCXRtoHIS
return




; ============================================================================================
; BMD 整合部分 - 從 autobmdv2.ahk
; ============================================================================================

factor()
{
	global useChinese
	if(useChinese=0)
	{
		return 1
	}else
	{
		return 2
	}
}

Translate(english)
{
	global useChinese
	
	if(useChinese=0)
	{
		if(english="lspine")
		{		   
			return "Lumbar spine"
		}
		if(english="fneck")
		{
			return "Femoral neck"
		}
		if(english="thip")
		{
			return "Total hip"
		}
		if(english="bmdlh")
		{
			return "Bone Mineral Density (BMD) of lumbar spine and hip was performed by Dual-energy`nX-ray Absorptiometry (DXA)"
		}
		if(english="bmdl")
		{
			return "Bone Mineral Density (BMD) of lumbar spine was performed by Dual-energy`nX-ray Absorptiometry (DXA)"
		}
		if(english="bmdh")
		{
			return "Bone Mineral Density (BMD) of hip was performed by Dual-energy`nX-ray Absorptiometry (DXA)"
		}
		if(english="t0m")
		{
			return "Assessment: Based on ISCD critieria, the BMD of the patient is normal (T >= -1)"
		}
		if(english="t1m")
		{
			return "Assessment: Based on ISCD critieria, the patient has low bone mass (osteopenia) (-2.5<T<-1)"
		}
		if(english="t2m")
		{
			return "Assessment: Based on ISCD critieria, the patient has osteoporosis (T <= -2.5)."
		}
		
		if(english="t0f")
		{
			return "Assessment: Based on WHO critieria, the BMD of the patient is normal (T >= -1)."
		}
		if(english="t1f")
		{
			return "Assessment: Based on WHO critieria, the patient has low bone mass (osteopenia) (-2.5<T<-1)."
		}
		if(english="t2f")
		{
			return "Assessment: Based on WHO critieria, the patient has osteoporosis (T <= -2.5)."
		}
		if(english="z0")
		{
			return "Assessment: Based on ISCD critieria, the BMD is within the expected range of age (Z >-2)."
		}
		if(english="z1")
		{
			return "Assessment: Based on ISCD critieria, the BMD is below the expected range of age (Z <= -2)."
		}
		
		if(english="tfx")
		{
			return "Note: Although the T score is not within range of 'osteoporosis', however osteoporosis is still favored due to presence of compression fracture."
		}
		if(english="zfx")
		{
			return "Note: Although the Z score is not within range of 'osteoporosis', however BMD below normal range is still favored due to presence of compression fracture."
		}
		
		
		if(english="thead")
		{
			return "                   BMD(g/cm2)      T-score"
		}
		if(english="zhead")
		{
			return "                   BMD(g/cm2)      Z-score"
		}
		if(english="finding")
		{
			return "Findings:"
		}
	}else
	{
		if(english="lspine")
		{		   
			return "腰椎"
		}
		if(english="fneck")
		{
			return "股骨頸"
		}
		if(english="thip")
		{
			return "髖部"
		}
		if(english="bmdlh")
		{
			return "雙能量 X 光吸收儀腰椎及髖部骨質密度檢查"
		}
		if(english="bmdl")
		{
			return "雙能量 X 光吸收儀腰椎骨質密度檢查"
		}
		if(english="bmdh")
		{
			return "雙能量 X 光吸收儀髖部骨質密度檢查"
		}
		if(english="t0m")
		{
			return "評估結果：根據國際臨床骨密度學會（ISCD）診斷標準：此骨質與一般人無異 (T 值 >= -1)"
		}
		if(english="t1m")
		{
			return "評估結果：根據國際臨床骨密度學會（ISCD）診斷標準：骨質缺乏症 (-2.5<T 值<-1)"
		}
		if(english="t2m")
		{
			return "評估結果：根據國際臨床骨密度學會（ISCD）診斷標準：骨質疏鬆症 (T 值 <= -2.5)"
		}
		
		if(english="t0f")
		{
			return "評估結果：根據世界衛生組織（WHO）診斷標準：此骨質與一般人無異 (T 值 >= -1)"
		}
		if(english="t1f")
		{
			return "評估結果：根據世界衛生組織（WHO）診斷標準：骨質缺乏症 (-2.5<T 值<-1)"
		}
		if(english="t2f")
		{
			return "評估結果：根據世界衛生組織（WHO）診斷標準：骨質疏鬆症 (T 值 <= -2.5)"
		}
		if(english="z0")
		{
			return "評估結果：根據國際臨床骨密度學會（ISCD）診斷標準：此骨質與同年齡一般人無異 (Z 值>-2)"
		}
		if(english="z1")
		{
			return "評估結果：根據國際臨床骨密度學會（ISCD）診斷標準：此骨質低於同年齡一般人 (Z 值<= -2)."
		}
		
		if(english="tfx")
		{
			return "附註：雖然 T 值未到達「骨質疏鬆症」之診斷標準，但由於腰椎出現疑似壓迫性骨折，所以診斷應為「骨質疏鬆症」"
		}
		if(english="zfx")
		{
			return "附註：雖然 Z 值未到達「骨質疏鬆症」之診斷標準，但由於腰椎出現疑似壓迫性骨折，所以診斷應為「骨質疏鬆症」"
		}
		
		if(english="thead")
		{
			return "            骨密度（公克/平方公分）  T 值"
		}
		if(english="zhead")
		{
			return "            骨密度（公克/平方公分）  Z 值"
		}
		if(english="finding")
		{
			return "影像檢查發現："
		}
	}
	

	msg:="參數錯誤：" english
	MsgBox %msg%
}

; BMD熱鍵 - 英文版
::bmd2::
useChinese:=0
GetBMD()
return

; BMD熱鍵 - 中文版 (如需要可以取消註解)
::bmd3::
useChinese:=1
GetBMD()
return

GetBMD()
{
	;global BMDStyle:=1. ; 用舊版還是新版的 BMD form，全部改為新版 已不需要 全設為1 新版代表nloop=5 有5張影像 舊版nloop=2
	global StoredText
	
	; Global initialize
	StoredTextClear()
	Hip_Z:=100
	Hip_T:=100
	Lspine_Z:=100
	Lspine_T:=100
	Neck_Z:=100
	Neck_T:=100
	Radius_Z:=100
	Radius_T:=100
	Radius_BMD:=99999

	; Click the DICOM button in G3
	ActivatePACS()
	gosub PosDICOMLU  ; 使用 PosDICOMRU 替換原本的 MouseMove 500,1000
	Send {LButton}
	
	nloop:=5  ;新版代表nloop=5 有5張影像
	
	Loop,%nloop%
	{
		data := GetClipBoardData()
		sleep 700
		gosub PosDICOMLU  ; 使用 PosDICOMRU 替換原本的 MouseMove 500,1000
		Send {LButton}
		Send {Down}
		sleep 1000
		
		GetResultsTable(data, "Neck", z, t, bmd)
		GetResultsTable(data, "L1-L4", z2, t2, bmd2)
		GetResultsTable(data, "1/3", z5, t5, bmd5)
		
		if(z!=100) ; 代表Neck有取得資料，影像包含hip
		{
			Neck_Z:=z
			Neck_T:=t
			Neck_BMD:=bmd
			GetResultsTable(data, "Total", Hip_Z, Hip_T, Hip_BMD) ;取得hip的total
		}else if(z5!=100){ ; Radius 有成功取得資料
			Radius_Z:=z5
			Radius_T:=t5
			Radius_BMD:=bmd5
		
		}else{
			; L spine total or L spine 各測量值
			GetResultsTable(data, "Total", lz, lt, lbmd)
			if(lbmd!=99999)
			{
				Lspine_Z:=lz
				Lspine_T:=lt
				Lspine_BMD:=lbmd
				
				GetResultsTable(data, "L1", z1, t1, bmd1)
				GetResultsTable(data, "L2", z2, t2, bmd2)
				GetResultsTable(data, "L3", z3, t3, bmd3)
				GetResultsTable(data, "L4", z4, t4, bmd4)
				
				LspineStr:=GetLSpineStr2(t1, t2, t3, t4) ;輸出共有哪幾節spine
				;desc .= "* L_ is excluded because T-score >1SD different from adjacent vertebra.`r* L_ is excluded because severe osteophyte.`r* L_ is excluded because compression fracture.`r"
			}			
		}
	
		;ActivatePACS()
	}
	
	Gender:=""
	MP:=0		; MenoPause
	PtAge:=0
	PtGender=""
	useT := CheckUseTScore(Gender, data, MP, PtAge, PtGender)
	
	; Send Data
	ActivateHIS()
	sleep 200
	
	haslspine:=0
	hasfneck:=0
	hasthip:=0
	hasrad:=0
	if(Lspine_Z!=100 and Lspine_T!=100)
	{
		haslspine:=1
	}
	if(Neck_T!=100 and Neck_Z!=100)
	{
		hasfneck:=1
	}
	if(Hip_Z!=100 and Hip_T!=100)
	{
		hasthip:=1
	}
	if(Radius_Z!=100 and Radius_T!=100)
	{
		hasrad:=1
	}
	
	SendBMDJudge2(Gender, useT, Lspine_Z, Lspine_T, Neck_Z, Neck_T, Hip_Z, Hip_T, Radius_Z, Radius_T)
	SendBMDFormHead2(useT, PtAge, PtGender, MP, haslspine, hasfneck, hasthip, hasrad)
	SendBMDResult2(PtGender, useT, LspineStr, Lspine_Z, Lspine_T, Lspine_BMD, Neck_Z, Neck_T, Neck_BMD, Hip_Z, Hip_T, Hip_BMD, Radius_Z, Radius_T, Radius_BMD, haslspine, hasfneck, hasthip, hasrad)  ; 傳入 has 變數
	
	; Send output
	ActivateHIS()
	SetReportHIS(StoredText)  ;some hacks
	StoredTextClear()
}

; 修改後的 GetClipBoardData 函數
GetClipBoardData()
{
	;ActivatePACS()
	
	; 使用 PosDICOMButton 替換原本的 MouseMove Panel_X, Panel_Y
	gosub CallDICOMWinL
	
	c1 = %clipboard%
	if (c1 = "")  ; 檢查剪貼簿是否有內容
    {
        MsgBox, 錯誤：無法取得 DICOM 資料
        return ""
    }
	p1 := InStr(c1, "0019,1000")
	p2 := InStr(c1, "0020,000D")
	
	raw := SubStr(c1, p1, p2 - p1)
		
	data := MergeStr(raw)
	
	return data
}

; 其他 BMD 相關函數
GetLSpineStr2(t1, t2, t3, t4)  ;產生腰椎測量範圍的文字描述，將有測量數據的腰椎編號轉換成易讀的字串格式。
{
	Array := Object()
	now:=0

	if(t1!=100)
	{
		Array[now]:=1
		now:=now+1
	}
	if(t2!=100)
	{
		Array[now]:=2
		now:=now+1
	}
	if(t3!=100)
	{
		Array[now]:=3
		now:=now+1
	}
	if(t4!=100)
	{
		Array[now]:=4
		now:=now+1
	}
	
	;只有 T-score 不等於 100（初始值）的腰椎會被加入陣列Array
	str:=""
	iter:=0
	flag:=0
	while(iter<now)
	{
		if(str!="")
		{
			if(flag=1)
			{
				str:=str "-" ;連續的腰椎：使用連字號 - 連接
			}else
			{
				str:=str "," ;不連續的腰椎：使用逗號 , 分隔
			}
			flag:=0
		}		
		str:= str "L" Array[iter]
		
		iter:=iter+1
		
		while(iter>0 && iter<now && Array[iter]-Array[iter-1]=1) ;連續性檢測
		{
			flag:=1
			iter:=iter+1
		}
		if(flag=1)
		{
			iter:=iter-1
		}
	}
	return str
}


GetLow3(scores*)
{
    low := 100
    for index, score in scores
    {
        if(score != 100 and score < low)
            low := score
    }
    return low
}

SendBMDResult2(Gender, useT, LspineStr, Lspine_Z, Lspine_T, Lspine_BMD, Neck_Z, Neck_T, Neck_BMD, Hip_Z, Hip_T, Hip_BMD,Radius_Z, Radius_T, Radius_BMD, haslspine, hasfneck, hasthip, hasrad)  ; 傳入 has 變數
{
	StoredTextAdd("BMD results:")
	StoredTextNewLine()
	; 腰椎結果（如果有）
    if(haslspine)  ; 直接使用 has 變數
    {
        StoredTextAdd("Spine:")
        StoredTextNewLine()
        StoredTextAdd("- The mean BMD measurement in the lumbar spine, " LspineStr ", is " Lspine_BMD " g/cm2.")
        StoredTextNewLine()
		if(LspineStr !="L1-L4"){
			StoredTextAdd("* L_ is excluded because T-score >1SD different from adjacent vertebra.")
			StoredTextNewLine()
			StoredTextAdd("* L_ is excluded because severe osteophyte.")
			StoredTextNewLine()
			StoredTextAdd("* L_ is excluded because compression fracture.")
			StoredTextNewLine()
		}
    }
    
    ;髖部結果
    if(hasfneck or hasthip)  ;直接使用 has 變數
    {
        StoredTextAdd("Hip:")
        StoredTextNewLine()
        if(hasfneck)
        {
            StoredTextAdd("- The BMD measurement in the femoral neck is " Neck_BMD " g/cm2.")
            StoredTextNewLine()
        }
        if(hasthip)
        {
            StoredTextAdd("- The BMD measurement in the total proximal femur is " Hip_BMD " g/cm2.")
            StoredTextNewLine()
        }
    }
    
    ; 橈骨結果（新增）
    if(hasrad)  ; 直接使用 has 變數
    {
        StoredTextAdd("Forearm:")
        StoredTextNewLine()
        StoredTextAdd("- The BMD measurement in the 1/3 radius is " Radius_BMD " g/cm2.")
        StoredTextNewLine()
    }
	
	StoredTextNewLine()
	if(useT)
	{
		low:=GetLow3(Lspine_T, Neck_T, Hip_T, Radius_T)		
		StoredTextAdd("The lowest T-score: ")
		StoredTextAdd(Round(low, 1))
		StoredTextNewLine()
		StoredTextAdd("- compared to the expected BMD for young adult (BMDCS/NHANES White Female).")
		StoredTextNewLine()
	}else
	{
		low:=GetLow3(Lspine_Z, Neck_Z, Hip_Z, Radius_Z)
		StoredTextAdd("The lowest Z-score: ")
		StoredTextAdd(Round(low, 1))
		StoredTextNewLine()
		StoredTextAdd("- compared to the expected BMD for age and gender matched Asian adult.")
		StoredTextNewLine()
	}
}

SendBMDJudge2(Gender, useT, Lspine_Z, Lspine_T, Neck_Z, Neck_T, Hip_Z, Hip_T, Radius_Z, Radius_T)
{
	; ScoreRange: T 0: normal, 1: -1.0~-2.5 2: <-2.5 Z: 0: >-2 1:<=-2
    ScoreRange := 0
    
    if(useT)
    {
        ; 檢查腰椎
        if(Lspine_T!=100)
        {
            if(Lspine_T <= -2.5)
            {
                if(ScoreRange < 2)
                    ScoreRange := 2
            }
            else if(Lspine_T < -1.0)
            {
                if(ScoreRange < 1)
                    ScoreRange := 1
            }
        }
        
        ; 檢查股骨頸
        if(Neck_T!=100)
        {
            if(Neck_T <= -2.5)
            {
                if(ScoreRange < 2)
                    ScoreRange := 2
            }
            else if(Neck_T < -1.0)
            {
                if(ScoreRange < 1)
                    ScoreRange := 1
            }
        }
        
        ; 檢查髖部
        if(Hip_T!=100)
        {
            if(Hip_T <= -2.5)
            {
                if(ScoreRange < 2)
                    ScoreRange := 2
            }
            else if(Hip_T < -1.0)
            {
                if(ScoreRange < 1)
                    ScoreRange := 1
            }
        }
        
        ; 檢查橈骨
        if(Radius_T!=100)
        {
            if(Radius_T <= -2.5)
            {
                if(ScoreRange < 2)
                    ScoreRange := 2
            }
            else if(Radius_T < -1.0)
            {
                if(ScoreRange < 1)
                    ScoreRange := 1
            }
        }
    }
    else
    {
        ; Z-score 的判斷
        if(Lspine_Z!=100 and Lspine_Z <= -2.0)
        {
            if(ScoreRange < 1)
                ScoreRange := 1
        }
        if(Neck_Z!=100 and Neck_Z <= -2.0)
        {
            if(ScoreRange < 1)
                ScoreRange := 1
        }
        if(Hip_Z!=100 and Hip_Z <= -2.0)
        {
            if(ScoreRange < 1)
                ScoreRange := 1
        }
        if(Radius_Z!=100 and Radius_Z <= -2.0)
        {
            if(ScoreRange < 1)
                ScoreRange := 1
        }
    }
	
	StoredTextAdd("Baseline Densitometric assessment:")
	StoredTextNewLine()
	if(useT)
	{
		if(Gender = "Male")
		{
			if(ScoreRange = 0)
			{
				StoredTextAdd("Based on the WHO densitometric classification, the BMD is ""Normal bone density"".")
				StoredTextNewLine()
				
				return
			}
			if(ScoreRange = 1)
			{
				StoredTextAdd("Based on the WHO densitometric classification, the BMD is ""Low bone density (Osteopenia)"".")
				StoredTextNewLine()
				
				return
			}
			if(ScoreRange = 2)
			{
				StoredTextAdd("Based on the WHO densitometric classification, the BMD is ""Osteoporosis"".")
				StoredTextNewLine()
				return
			}
		}else
		{
			if(ScoreRange = 0)
			{
				StoredTextAdd("Based on the WHO densitometric classification, the BMD is ""Normal bone density"".")
				StoredTextNewLine()
				
				return
			}
			if(ScoreRange = 1)
			{
				StoredTextAdd("Based on the WHO densitometric classification, the BMD is ""Low bone density (Osteopenia)"".")
				StoredTextNewLine()
				
				return
			}
			if(ScoreRange = 2)
			{
				StoredTextAdd("Based on the WHO densitometric classification, the BMD is ""Osteoporosis"".")
				StoredTextNewLine()
				return
			}
		}
	}else
	{
		if(ScoreRange = 0)
		{
			StoredTextAdd("Based on the ISCD densitometric classification, the BMD is ""Within the expected range for age"".")
			StoredTextNewLine()
			return
		}else
		{
			StoredTextAdd("Based on the ISCD densitometric classification, the BMD is ""Below the expected range for age"".")
			StoredTextNewLine()
			return
		}
	}
	
	return
}


SendBMDFormHead2(useT, PtAge, gender, MP, haslspine, hasfneck, hasthip, hasrad)
{
	StoredTextNewLine()
	StoredTextAdd("# According to 2019 ISCD Official Position")
	StoredTextNewLine()
	StoredTextAdd("==============================================================================")
	StoredTextNewLine()
	StoredTextAdd("INDICATION and HISTORY:")
	StoredTextNewLine()
	
	str:="The patient is a "
	str:=str PtAge
	str:=str " year old Asian "
	StringLower, gender, gender
	str:=str gender
	
	if(gender="female")
	{
		if(MP=1)
		{
			str:=str " with risk factors for low bone mineral density"
			str:=str " including post-menopausal status"
		}else
		{
			str:=str " before menopause"
		}
	}else
	{
		if(PtAge>=50)
		{
			str:=str " with risk factors for low bone mineral density"
		}
	}
	str:= str "."
	StoredTextAdd(str)
	StoredTextNewLine()
	StoredTextNewLine()
	
	StoredTextAdd("TECHNIQUE:")
	StoredTextNewLine()
	StoredTextAdd("The examination was performed of the ")
	parts := ""
    if(haslspine)
        parts := parts . "lumbar spine (L1-4)"
    
    if(hasfneck or hasthip)
    {
        if(parts != "")
            parts := parts . ", "
        parts := parts . "proximal femur"
    }
    
    if(hasrad)  ; 新增
    {
        if(parts != "")
            parts := parts . ", "
        parts := parts . "forearm"
    }
	techniqueStr := techniqueStr . parts
    StoredTextAdd(techniqueStr)
	StoredTextNewLine()
	StoredTextAdd("using the dual x-ray technique (Hologic, Discovery Wi).")
	StoredTextNewLine()
	StoredTextNewLine()
	
	StoredTextAdd("COMPARISON:")
	StoredTextNewLine()
	StoredTextAdd("None.")
	StoredTextNewLine()
	StoredTextNewLine()
}

SendSpace(n)
{
	loop ,%n%
	{
		StoredTextAdd(" ")
	}
}

CheckUseTScore(byref Gender, data, byref MP, byref PtAge, byref PtGender)
{
	; return 1 if use T score
	str = PatientSex = "
	p1:= InStr(data, str)
	Gender := GetBetweenQuote(data, p1 + 13)
	PtGender:=Gender
	
	str = MenopauseAge = "
	p1:= InStr(data, str)
	MenoPause := GetBetweenQuote(data, p1 + 15)
	
	str = Age = "
	p1:= InStr(data, str)
	PatientAge := GetBetweenQuote(data, p1 + 6)
	PtAge:=PatientAge
	
	if (Gender = "Male" ){
		if(PatientAge < 50){
			return 0
		}else{
			return 1
		}
	}else if(Gender = "Female")
	{
		if(Trim(MenoPause) != "" and MenoPause != " "){
			MP:=1
		}else{
			MP:=0
		}
		if(MP=1){
			;menopause female
			return 1
		}else{
			return 0
		}
		
	}
	; Shouldn't reach here
	return 0
}

MoveMouseScr( x,y ) {
	return DllCall( "SetCursorPos", Int,x, Int,y )
}

KillScript()
{
	msg=
(
Atypical DICOM tag detected. This may due to patient-related personalized BMD DICOM settings. The execution of this script for this patient cannot be continued. Advise sent the Chart No. of patient to Kung Hsun, Weng if clinically indicated.
)
	MsgBox %msg%
	Reload
}

GetResultsTable(input, key, ByRef z_score, ByRef t_score, ByRef bmd)
{
	z_score:=100
	t_score:=100
	bmd:=99999
	
	while(PeekNext(input, row, col, val)>0)
	{
		if(val=key)
		{
			PeekNext(input, r, c, v) 		; Area
			PeekNext(input, r, c, v) 		; BMC
			PeekNext(input, r, c, bmd) 		; BMD
			PeekNext(input, r, c, t_score) 	; T score
			PeekNext(input, r, c, v)	 	; PR
			PeekNext(input, r, c, z_score)	; Z score
		}
	}
}

PeekNext(ByRef input, ByRef row, ByRef col, ByRef val)
{
	r=ResultsTable1\[\s*(\d+)\]\[\s*(\d+)\]\s*=\s*"([^"]*)"
	FoundPos := RegExMatch(input, r , match)
	if(FoundPos=0)
	{
		return 0
	}else
	{
		; match is found
		; truncate input
		input:=SubStr(input, FoundPos+StrLen(match))
		
		row:=match1
		col:=match2
		val:=match3
		
		dbg:= FoundPos ":" row ":" col ":" val 
		;MsgBox %dbg%
		
		return FoundPos
	}
}

GetBetweenQuote(str, pos)
{
	; pos MUST points to "
	q = "
	p2 := InStr(str,q,false,pos+1)
	rst :=SubStr(str, pos+1, p2-pos-1)
	return rst
}

MergeStr(raw)
{
	StringSplit, dataray, raw , |
	Loop, %dataray0%
	{
		if Mod(a_index, 2) = 0
		{
			rst.=dataray%a_index%
		}
	}
	return rst
}

::bmdwin::
ShowBMDWindow:
    WinGet, ActiveId, ID, A ; 記錄目前視窗ID
    
    ; 建立GUI視窗
    Gui, BMDWin:New, +AlwaysOnTop, BMD 工具視窗
    Gui, BMDWin:Font, s12, 微軟正黑體
    
    ; 標題
    Gui, BMDWin:Add, Text, x10 y10 w300 h30 Center, BMD 報告工具
    
    ; 按鈕1: 執行 bmd2
    Gui, BMDWin:Add, Button, x20 y50 w260 h60 gBMDWin_RunBMD2, 執行 BMD 分析`n(自動抓取 DICOM 資料)
    
    ; 按鈕2: 輸出比較舊片文字
    Gui, BMDWin:Add, Button, x20 y120 w260 h60 gBMDWin_CompareOld, 輸出比較舊片文字`n(Serial Densitometric)
    
    ; 按鈕3: L-spine 排除原因
    Gui, BMDWin:Add, Button, x20 y190 w260 h60 gBMDWin_SpineExclusion, L-spine 排除原因`n(未全部納入說明)
    
    ; 分隔線
    Gui, BMDWin:Add, Text, x10 y260 w280 h2 0x10
    
  
    ; 關閉按鈕
    Gui, BMDWin:Add, Button, x20 y320 w260 h40 gBMDWin_Close, 關閉視窗 (ESC)
    
    ; 顯示視窗
    Gui, BMDWin:Show, w300 h380
return

; 按鈕1: 執行 bmd2
BMDWin_RunBMD2:
    Gui, BMDWin:Submit, NoHide
    useChinese := 0
    GetBMD()  ; 呼叫 bmd2 的主要函數
return

; 按鈕2: 輸出比較舊片文字
BMDWin_CompareOld:
    Gui, BMDWin:Submit, NoHide
    
    ; 建立比較舊片的標準文字
    compareText := "Serial Densitometric assessment:`r"
    compareText .= "The interval change of BMD is statistically stationary.`r"
    compareText .= "_The interval change of BMD is statistically significantly increased at __.`r"
    compareText .= "_The interval change of BMD is statistically significantly decreased at __.`r"
    compareText .= "`r"
    compareText .= "COMPARISON:`r"
    compareText .= "Previous BMD: 20__/__/__.`r"
    
    ; 輸出到 HIS
    ActivateHIS()
    Sleep, 100
    SendInput, %compareText%
    
    ; 提示訊息
    MsgBox, 64, 完成, 已輸出比較舊片文字到報告中, 2
return

; 按鈕3: L-spine 排除原因
BMDWin_SpineExclusion:
    Gui, BMDWin:Submit, NoHide
    ; 建立子選單視窗
    compareText := "* L_ is excluded because T-score >1SD different from adjacent vertebra.`r"
    compareText .= "* L_ is excluded because severe osteophyte.`r"
    compareText .= "* L_ is excluded because compression fracture.`r"
    
    ; 輸出到 HIS
    ActivateHIS()
    Sleep, 100
    SendInput, %compareText%
    
    ; 提示訊息
    MsgBox, 64, 完成, 已輸出排除原因到報告中, 2
return

; 關閉視窗
BMDWin_Close:
BMDWinGuiClose:
BMDWinGuiEscape:
    Gui, BMDWin:Destroy
return


WriteStudyID:
    ; 讀取 HIS 系統的 Study ID
    ControlGetText, text, ThunderRT6TextBox9, ahk_exe chk060.exe
    
    ; 擷取 Study ID（8位數字）
    FoundPos := RegExMatch(text, "[0-9]{8}", StudyID)
    if (FoundPos = 0)
        return
    
    ; 只有 ID 變更時才寫入，避免頻繁寫檔
    if (StudyID != LastStudyID)
    {
        FileDelete, %RemoteFile%
        FileAppend, %StudyID%, %RemoteFile%
        LastStudyID := StudyID
        
        ; 可選：顯示通知
        ; ToolTip, 已寫入: %StudyID%
        ; SetTimer, RemoveToolTip, -1500
    }
    return