#SingleInstance force
CoordMode, Mouse, Screen
SetTitleMatchMode 2
; SetTitleMatchMode 1: 預設. 視窗標題必須以指定的 WinTitle "開頭"才能符合. 2: 視窗標題的"任意位置"包含 WinTitle 才能符合. 3: 視窗標題必須和 WinTitle "完全一致"才能符合.

; 全局變數設定
global LOGI := ""
global PWD := ""
global varWhere := 2
global vExamLoc := 1  ; 0: 永康, 1: 佳里
global ServerLoc0 := 0  ; 新增這行
global ServerLoc1 := 1  ; 新增這行
global skipMoveDown := false
global desc := ""
global API_KEY := ""
global API_KEY2 := ""

global ExamNo, varCopyOld
global WB, lastUSAIResult := "", currentUSAIImage := "", previousUSAIImage := ""

; 全域變數
global USAI_CurrentImage := ""
global USAI_PreviousImage := ""
global USAI_APIKey := API_KEY
global USAI_CurrentOCRText := ""
global USAI_PreviousOCRText := ""
global g_USAI_StartTick := 0
global g_USAI_LastModel := ""

; --- AI Findings (I2F) globals — 必須在 auto-exec 內初始化（被 #include 的 US.ahk 內部已過 auto-exec） ---
global g_I2F_Whr := ""
global g_I2F_StartTick := 0
global g_I2F_RequestActive := false
global g_I2F_LastScenario := ""
global g_I2F_LastImpression := ""
global g_I2F_LastModel := ""
global g_I2F_LastTokens := {prompt: 0, completion: 0, total: 0}
global g_I2F_History := []
global g_I2F_HistoryMax := 10
global g_I2F_PromptDir := A_ScriptDir "\prompts"

; OCR 設定
global OCRAppsRoot := "D:\ahk"  ; 請根據實際路徑調整
global irfan_dir_p := "\IrfanViewPortable\App\IrfanView"
global tess_dir_p := ""
global nircmd_dir_p := "\nircmd"

global irfan_dir := OCRAppsRoot . irfan_dir_p
global tess_dir := OCRAppsRoot . tess_dir_p
global nircmd_dir := OCRAppsRoot . nircmd_dir_p

global tess_exe := OCRAppsRoot . "\Tesseract-OCR-v5\tesseract.exe"
global irfan_exe := OCRAppsRoot . "\IrfanViewPortable\App\IrfanView\i_view32.exe"
global nircmd_exe := OCRAppsRoot . "\nircmd\nircmd.exe"


; 全域變數用於儲存收集的座標
global CollectedCoords := {}
global CurrentLocation := ""
global RelativeBase := {x: 0, y: 0}

; GUI 變數也需要宣告為全域
global Loc1, Loc2, Loc3, Loc4, Loc5, Loc6, Loc7, Loc8, Loc9
global ResultEdit, CodeEdit

global MenuItemTexts := {}
global CurrentTextForMenu := ""

; 設定共享檔案路徑（請改成實際的網路共享路徑）
RemoteFile := A_ScriptDir . "\remote.txt"
LastStudyID := ""



; 載入設定檔案
LoadSettingsFromFile()

; 高醫腸阻塞擷取視窗（一次性專案）。必須放在 #include 之前：test.ahk 開頭就是
; 熱鍵定義，auto-execute 段在那裡就結束了，之後 include 進來的頂層程式碼不會執行。
HGH_BuildGUI()

FileEncoding, UTF-8

#include HotstringMenu.ahk
#include Abbr.ahk
#include test.ahk
#include US.ahk 
#include Xray.ahk 
#include Mammo.ahk 
#include IR.ahk
#include CT.ahk
; 高醫腸阻塞資料擷取（一次性專案，收工後連同 hgh-bowel/ 一起移除）
#include ..\hgh-bowel\hgh_capture.ahk

; ----------------------------------------------------------------------

:O:````::(Srs/Img:_/_)
:O:srs::(Arrows in Srs:_)
:O:imp::Impression:

; -------------------------------------------------------------------------------------------
; Status post 
; -------------------------------------------------------------------------------------------

:O:sp;::
SendInput Status post{Space}
HotstringMenuMulti("A","MenuShortcut"
    ,"nasogastric tube insertion with tip in stomach"
    ,"nasogastric tube insertion with tip not seen"
    ,"BRK"
    ,"central venous catheter insertion via _"
    ,"central venous catheter insertion via _, tip in SVC"
    ,"permcath catheter insertion at _right chest"
    ,"BRK"
    ,"pacemaker implantation over _left chest"
    ,"BRK"
    ,"Port-A implantation via {LtRt} subclavian vein, _internal jugular vein, with tip in _SVC_atriocaval junction"
    ,"Port-A implantation over {LtRt} chest"
    ,"BRK"
    ,"sternotomy with metallic wire fixation"
    ,"sternotomy with metallic wire fixation, _valvular replacement _CABG"
    ,"_coronary stenting"
    ,"BRK"
    ,"endotracheal tube insertion, tip to carina _cm"
    ,"endotracheal tube insertion with tip in appropriate location"
    ,"endotracheal tube insertion and tip at _"
    ,"tracheostomy"
    ,"BRK"
    ,"Ventriculoperitoneal Shunt(VP shunt)"
    ,"Foley insertion.","_"
    ,"pigtail insertion with tip at _"
    ,"double J stent implantation in {LtRt} urotract.")
return

:O:sp2;::
SendInput Status post{Space}
HotstringMenuMulti("A","MenuShortcut"
    ,"total knee replacement, with acceptable alignment, without evidence of loosening"
    ,"medial unicompartmental knee arthroplasty"
    ,"BRK"
    ,"{LtRt} hip bipolar hemiarthroplasty"
    ,"{LtRt} total hip replacement"
    ,"{LtRt} total hip replacement, with acceptable alignment"
    ,"BRK"
    ,"_ vertebroplasty"
    ,"transpedicular screws fixation between _"
    ,"interbody cage fixation at _"
    ,"internal fixation at _"
    ,"BRK"
    ,"{LtRt} partial mastectomy with clips"
    ,"{LtRt} mastectomy"
    ,"cholecystectomy, with clips in right upper abdomen")
return

:O:spi;::
HotstringMenuMulti("A","MenuShortcut2"
    ,"Loss lordosis of spine"
    ,"No obvious hypermobility"
    ,"Suspect L5 short pedicle"
    ,"_ pars defect can not be excluded. DDx. facet arthrosis"
    ,"Facet arthrosis, Baastrup disease/kissing spinal processes of lower L-spine"
    ,"Facet arthrosis of lower L-spine"
    ,"Baastrup disease or kissing spinal processes of lower L-spine"
    ,"_ anterior wedging"
    ,"BRK"
    ,"C-spine(AP+Flex.+Ext.):"
    ,"L-spine(AP+Flex.+Ext.):")
return



; ----------------------------------------------------------------------
; Chest, 常見
; -------------------------------------------------------------------------------------------


:O:adds::
HotstringMenuV("A","MenuShortcut"
    ,"Occult entities can not be excluded"
    ,"Tumor growth can not be excluded"
    ,"Superimposed pneumonia or other occult entities can not be excluded"
    ,"Lesions may be obscured"
    ,"Motion artifact may interfere with interpretation."
    ,"*Poor inspiration. Lesion may be obscured"
    ,"BRK"
    ,"*Subtle fracture may not be visible under one view, suggest follow up or correlate with other views if clinical indicated"
    ,"*Acute fracture may be obscured at initial exam. Suggest OPD follow up"
    ,"*Neuroforainal evaluation limited because bone overlapping."
    ,"BRK"
    ,"*Unsatisified posture, lesion may be obscured"
    ,"*Poor image contrast, lesion may be obscured"
    ,"BRK"
    ,"*Lesions may be obscured due to limited US penetration"
    ,"Prominent skin folds, lesion may be obscured"
    ,"BRK"
    ,"*Small stone may be obscured"
    ,"*Urotract stone evaluation limited because bowel interference")
return


:O:cxrm;::
HotstringMenuMulti("A","MenuShortcut"
    ,"心肺無明顯異常."
    ,"心肺無其他明顯異常."
    ,"BRK"
    ,"主動脈弓鈣化."
    ,"冠狀動脈鈣化或支架."
    ,"瓣膜鈣化."
    ,"心臟擴大."
    ,"邊緣心臟擴大."
    ,"縱膈腔擴大."
    ,"雙側肺門擴大."
    ,"右側肺門擴大."
    ,"BRK"
    ,"疑似骨密度降低."
    ,"疑似骨質疏鬆."
    ,"_輕微胸腰椎脊柱側彎."
    ,"BRK"
    ,"肺氣腫樣變化."
    ,"疑似肺水腫."
    ,"雙側輕微肋膜積液."
    ,"BRK"
    ,"無法排除藏有其他病灶之可能."
    ,"無法排除合併肺炎或其他病灶之可能."
    ,"宜追蹤."
    ,"與舊片比較無明顯變化.")
return


:O:emphy;::
HotstringMenuV("A","MenuShortcut2"
    ,"Emphysematous change of both lungs"
    ,"Paraseptal, centrilobular emphysema of both lungs"
    ,"Centrilobular emphysema of both lungs."
    ,"Panlobar, paraseptal, centrilobular emphysema of both lungs. ")
return

:O:athero;::
:O:ath;::
HotstringMenuV("A","MenuShortcut"
    ,"Atherosclerotic change of abdominal aorta and its major branches"
    ,"Atherosclerotic change of coronary arteries, abdominal aorta, and its major branches"
    ,"BRK"
    ,"Atherosclerotic change of aorta and its major branches"
    ,"Atherosclerotic change of coronary arteries, aorta and its major branches"
    ,"BRK"
    ,"Intimal calcification of aorta"
    ,"Tortuous aorta with intimal calcification"
    ,"Atherosclerosis of arteries"
    ,"Elongation of aorta with intimal calcification."
    ,"BRK"
    ,"abdominal total hysterectomy")
return

:O:car;::
HotstringMenuV("A","MenuShortcut2","Normal heart size.","Borderline cardiomegaly.","Cardiomegaly.")
return

:O:med;::
HotstringMenuV("A","MenuShortcut2"
    ,"Mild mediastinal widening."
    ,"Obvious mediastinal widening."
    ,"Mediastinal widening, could be related to elongated aorta or others"
    ,"Mediastinal widening, nature unknown.")
return

:O:hilar;::
HotstringMenuV("A","MenuShortcut"
    ,"Bilateral hilar fullness, could be vascular shadows or others"
    ,"Bilateral hilar fullness, could be vessels but _lymphadenopathy can not be excluded"
    ,"Bilateral hilar fullness, could be vessels but lymphadenopathy or other lesions can not be excluded"
    ,"BRK"
    ,"{LtRt} hilar fullness, could be vascular shadow or others"
    ,"{LtRt} hilar fullness, could be vessels but lymphadenopathy or other lesions can not be excluded"
    ,"Bilateral hilar calcified LNs or vessels.")
return


:O:eff;::
HotstringMenuV("A","MenuShortcut"
    ,"_Mild suprapatellar effusion"
    ,"BRK"
    ,"{LtRt} pleural effusion"
    ,"{LtRt} minimal pleural effusion or pleural changes."
    ,"Bilateral pleural effusion, {LtRt} more severe."
    ,"Pericardial effusion can not be excluded.")
return


:O:osteo;::
:O:ost;::
HotstringMenuV("A","MenuShortcut"
    ,"Suspect osteopenia."
    ,"Suspect osteoporosis."
    ,"Disuse osteoporosis."
    ,"Grade _ wedging compression fracture over _"
    ,"Grade _ _biconcave compression fracture over _"
    ,"_ anterior wedging"
    ,"_ crushing deformity"
    ,"BRK"
    ,"*Nondisplaced fracture may be obscured under osteoporosis background."
    ,"Bilateral ribs insufficiency fracture cnanot be excluded.")
return

:O:comp::
HotstringMenuV("A","MenuShortcut"
    ,"* Compared with prior film on"
    ,"* Limited interval change compared with prior film on"
    ,"No previous exams can be compared"
    ,"BRK"
    ,"Comparison with previous CT on "
    ,"Comparison with previous ([_])CT"
    ,"No previous CT could be compared"
    ,"BRK"
    ,"* Compared with prior US on")
return


:O:bow;::
HotstringMenuV("A","MenuShortcut2"
    ,"Unremarkable bowel gas"
    ,"Mild increased bowel gas"
    ,"Increased bowel gas"
    ,"Increased bowel gas or mild ileus"
    ,"Suspect ileus or bowel obstruction"
    ,"Suspect ileus."
    ,"BRK"
    ,"BRK"
    ,"Nonspecific bowel gas. Further evaluation if ileus suspected"
    ,"Due to gaseous bowel overlapping, pneumoperitoneum can not be excluded"
    ,"No x-ray evidence of pneumoperitoneum. However, x-ray sensitivity is about 75%, further evaluation if clinical condition indicates.")
return

:O:no;::
HotstringMenuV("A","MenuShortcut"
    ,"No significant >3mm lung nodules found in both lungs."
    ,"No obvious radiopaque urotract stones."
    ,"No aortic dissection."
    ,"No definite CT evidence of major pulmonary embolism was noted. *However, small branches embolism may be obscured."
    ,"BRK", "No corresponding lesion found at breast US.","No x-ray evidence of pneumoperitoneum.","BRK"
    ,"No clavicular displaced fracture"
    ,"No tibial, fibular shaft fracture noted.")
return


:O:lc;::Limited change.

:O:nl;::No active lung lesions.

; --- 高頻短語 hotstring (新增 2026-05-03，依 keylog 統計) ---
:O:oro;::or others.
:O:cb;::could be
:O:pif;::post internal fixation.
:O:ofr;::old fracture of _
:O:old;::
HotstringMenuV("A","MenuShortcut2","old fracture of _","old fracture of {LtRt} ribs.")
return

:O:cx;::
HotstringMenuV("A","MenuShortcut2"
    ,"Chronic/post infection/inflammatory changes or others in both lungs."
    ,"suspect post infection/inflammatory changes or others."
	,"post infection/inflammatory changes or others."
    ,"suspect chronic infection/inflammatory changes or others."
	,"chronic infection/inflammatory changes or others."
    ,"")
return

:O:post;::
HotstringMenuV("A","MenuShortcut2"
    ,"Posterior"
    ,"post infection/inflammatory changes or others."
    ,"chronic infection/inflammatory changes or others."
    ,"")
return

:O:cann::can not be excluded. 



:O:bos;::
HotstringMenuV("A","MenuShortcut"
    ,"Bosniak classification category I"
    ,"Bilateral renal cysts. Bosniak classification category _I"
    ,"Bilateral renal cysts and hemorrhagic cysts. Bosniak classification category I-II.")
return
; "hypodense lesion without post-contrast enhancement _, about _cm in diameter, favor _cyst","hypodense lesions without post-contrast enhancement in _, up to _cm in diameter, favor _cysts."

:O:cyst;::
HotstringMenuV("A","MenuShortcut"
    ,"Left renal cyst"
    ,"Right renal cyst"
    ,"BRK"
    ,"Bilateral renal cysts"
    ,"{LtRt} renal cysts, up to _ cm"
    ,"BRK"
    ,"Bilateral breast cysts"
    ,"{LtRt} breast cysts"
    ,"BRK"
    ,"_Bilateral thyroid cysts"
    ,"{LtRt} thyroid cysts"
    ,"BRK"
	,"Hepatic cyst or hypodense lesion in _ of liver.(Srs/Img:_/_)"
    ,"Hepatic cysts or hypodense lesions in _both lobes of liver.(Srs/Img:_/_)"
	,"Hepatic cysts or hypodense lesions in _both lobes of liver."
	,"Hepatic cysts in both lobes of liver."
    ,"Hepatic cysts in both lobes of liver, up to _ cm. "
    ,"Hepatic cysts"
    ,"BRK"
    ,"A midline neck cyst, _cm, could be thyroglossal duct cyst or other.(Srs/Img:1/_)"
    ,"A midline prostate cyst, _cm, could be utricle cyst, Mullerian duct cyst or others.(Srs/Img:1/_)")
return

:O:stone;::
HotstringMenuV("A","MenuShortcut"
    ,"Left renal stone, _ cm"
    ,"Right renal stone, _ cm"
    ,"Bilateral renal stones, up to _cm"
    ,"{LtRt} renal stones, up to _ cm"
    ,"{LtRt} renal stone(s)."
    ,"BRK"
    ,"Gallstone or right renal stone or other."
    ,"{LtRt} renal stone or bowel content or other."
    ,"BRK"
    ,"A right _upper_middle_lower third ureteral stone, _ cm. "
    ,"_Right/_Left _ third ureteral stone, about _cm in diameter, complicated with hydronephrosis_hydroureteronephrosis and perinephric_periureteric infiltration"
    ,"No obvious radiopaque urotract stones"
    ,"{LtRt} upper ureteral stone at _ level can not be excluded.")
return

:O:title;::
HotstringMenuV("A","MenuShortcut","{LtRt} ankle and foot:","-spine(AP+Flex.+Ext.):")
return

:O:sug;::
HotstringMenuV("A","MenuShortcut2"
    ,"Suggest follow up"
    ,"Suggest clinical correlation"
    ,"Suggest short-term follow up"
    ,"Suggest _ for further evaluation"
    ,"Suggest correlate with other studies"
    ,"BRK"
    ,"Suggest thyroid US follow-up."
    ,"Suggest breast US correlation."
    ,"Suggest diagnostic mammography for further evaluation."
    ,"Suggest diagnostic mammography with spot magnification for further evaluation."
    ,"Suggest 6-month follow-up mammography."
    ,"Diagnostic mammo(_ breast, spot magnification)")
return

:O:nodule;::
HotstringMenuV("A","MenuShortcut"
    ,"A _hyperechoic nodule in _left lobe of liver, _ cm.(Srs/Img:_/_)"
    ,"A _hypoechoic nodule in _left lobe of liver, _ cm.(Srs/Img:_/_)"
    ,"A _hyperechoic nodule in _left kidney, _ cm.(Srs/Img:_/_)"
    ,"A hypoechoic nodule in _ peripheral zone of prostate , _ cm. (Srs/Img:1/_) ")
return


:O:fatty;::
HotstringMenuV("A","MenuShortcut"
    ,"Mild fatty liver"
    ,"Mild to moderate fatty liver"
    ,"Moderate fatty liver"
    ,"Severe fatty liver. *Deeper lesions may be obscured because limited US penetration"
    ,"BRK"
    ,"decreased attenuation of liver parenchyma as compared with spleen, suggesting fatty liver, _.")
return

:O:pan;::
HotstringMenuV("A","MenuShortcut"
    ,"pancreatic"
    ,"BRK"
    ,"pancreatic cyst at _, _cm.(Srs/Img:_/_)"
    ,"pancreatic cysts in _, up to _cm."
    ,"BRK"
    ,"pancreatic ductal dilation, up to _mm."
    ,"Pancreatic duct dilation with intraductal stones, could be chronic pancreatitis or others."
    ,"BRK"
    ,"A solid lesion in _, _cm, nature uncertain.(Srs/Img:_/_)"
    ,"A hypoechoic lesion in _, _cm, DDx: pancreatic adenocarcinoma or others.(Srs/Img:_/_)"
    ,"BRK"
    ,"IPMN or mucinous cyst at _, _cm. Suggest MRI correlation."
    ,"Side-branch IPMN at _, _cm.(Srs/Img:_/_)")
return

:O:pe;::
(
* No definite CT evidence of major pulmonary embolism was noted.
  However, correlation to clinical S/S and V/Q scan still recommended to  exclude small branches embolism.
)

:O:recist;::
SendInput Overall,{Space}
HotstringMenuV("A","MenuShortcut","complete response(CR)","partial response(PR)","stable disease(SD)","progressive disease(PD)")
SendInput (RECIST 1.1) is considered.
return

::rev::
(
Revision Date: _

The TNM staging is revised according to pathological proven _ cancer(_).
)

:O:tumor;::
(
- A lesion in _, _cm, favor _(Srs/Img:_/_), with _intermediate/high/low T2 signal, _water restriction in DWI, _perfusion defect/high signal intensity in hepatobiliary phase, _arterial phase hyperenhancement, _portal phase hyperenhancement, _central scar, _washout, _capsule.
)



:O:aipdf::
(
請先讀取此pdf，根據檔案中的標題將內容切分後，
直接根據標題所對應的內容區塊逐一仔細閱讀後 整理成詳盡的筆記 
-若其中涉及較複雜的觀念，都應向下拆解說明 並給予子標題以方便閱讀 
-若有涉及方程式，請以LaTeX表示
-若有涉及專有名詞，以中英對照表示
-若有包含數據的表格，則需要根據其中數據指標 解讀基本數據走勢，以及思考有無更深層的洞察。
-你是一位放射科醫師，影像相關的概念，檢查操作細節，參數為重點。
若無法一次讀完可以分批次閱讀，但請完成全部 的內容區塊筆記整理後才可終止，無須請示是否要繼續，請用繁體中文撰寫
)


<#z::
gosub MergeExams
return

;============================================================================================
; 少用
;============================================================================================

:O:ica;::
HotstringMenuV("A","MenuShortcut2"
    ,"_Mild intracranial atherosclerosis change"
    ,"_Moderate intracranial atherosclerosis change"
    ,"_Severe intracranial atherosclerosis change"
    ,"_Moderate to severe intracranial atherosclerosis change.")
return

:O:edema;::
HotstringMenuV("A","MenuShortcut", "pulmonary congestion pattern","pulmonary edema")
return


; 主要的設定管理器GUI函數
CreateConfigManager() {
    ; GUI 設定
	
	global USAI_APIKey := API_KEY
    Gui, ConfigManager:New, +AlwaysOnTop, 放射科工具設定管理器
    Gui, ConfigManager:Font, s12, 微軟正黑體
    
    ; 添加控件
    Gui, ConfigManager:Add, GroupBox, x10 y10 w380 h190, 系統設定
    
    ; 電腦位置
    Gui, ConfigManager:Add, Text, x20 y35 w150 h25, 電腦位置 (varWhere):
    Gui, ConfigManager:Add, DropDownList, x180 y35 w200 h75 vSelectedLocation, 1:佳里學姊||2:佳里|3:永康3樓-佳里|4:永康3樓-LY|5:遠端從家|6:R(win7)|7:12F(win7)|8:永康3樓-Wong
    
    ; 登入資訊
    Gui, ConfigManager:Add, Text, x20 y70 w150 h25, 登入帳號 (LOGI):
    Gui, ConfigManager:Add, Edit, x180 y70 w200 h25 vLoginID, %LOGI%
    
    Gui, ConfigManager:Add, Text, x20 y105 w150 h25, 登入密碼 (PWD):
    Gui, ConfigManager:Add, Edit, x180 y105 w200 h25 vLoginPwd, %PWD%
    
    ; 伺服器位置
    Gui, ConfigManager:Add, Text, x20 y140 w150 h25, 伺服器位置 (vExamLoc):
    Gui, ConfigManager:Add, Radio, x180 y140 w90 h25 vServerLoc1 Checked%vExamLoc%, 佳里 (1)
    Gui, ConfigManager:Add, Radio, x280 y140 w90 h25 vServerLoc0, 永康 (0)
    
    ; 儲存與取消按鈕
    Gui, ConfigManager:Add, Button, x20 y400 w170 h40 gSaveConfig, 儲存設定
    Gui, ConfigManager:Add, Button, x200 y400 w170 h40 gConfigGuiClose, 取消
    
	; 添加 AI 設定區塊 (修改後)
    Gui, ConfigManager:Add, GroupBox, x10 y220 w380 h100, AI 設定 ; 高度增加
    
    ; GPT Key 欄位
    Gui, ConfigManager:Add, Text, x20 y240 w100 h25, GPT Key:
    Gui, ConfigManager:Add, Edit, x130 y240 w240 h25 vConfigGPTKey Password, %API_KEY%
    
    ; Gemini Key 欄位 (新增)
    Gui, ConfigManager:Add, Text, x20 y270 w100 h25, Gemini Key:
    Gui, ConfigManager:Add, Edit, x130 y270 w240 h25 vConfigGeminiKey Password, %API_KEY2%
	
    ; 顯示GUI
    Gui, ConfigManager:Show, w400 h500
    
    ; 設定下拉選單預設值
    GuiControl, ConfigManager:Choose, SelectedLocation, %varWhere%
    
}

; 儲存設定
SaveConfig:
    Gui, ConfigManager:Submit, NoHide
    
    ; 更新全局變數
    LOGI := LoginID
    PWD := LoginPwd
    API_KEY := ConfigGPTKey       ; 更新 GPT Key
    API_KEY2 := ConfigGeminiKey   ; 更新 Gemini Key
    
    ; 處理下拉選單
    varWhere := SubStr(SelectedLocation, 1, 1)
    
    ; 處理伺服器位置單選按鈕
    if (ServerLoc1) {
        vExamLoc := 1
    } else {
        vExamLoc := 0
    }
    
    ; 儲存設定到檔案 (可選)
    SaveSettingsToFile()
    
    MsgBox, 64, 設定已更新, 設定已儲存！`nGPT Key: 已更新`nGemini Key: 已更新
    Gui, ConfigManager:Destroy
return

; 關閉GUI
ConfigGuiClose:
ConfigGuiEscape:
    Gui, ConfigManager:Destroy
return


; 儲存設定到檔案 (實際應用時可自行實作)
SaveSettingsToFile() {
    settingsFile := A_ScriptDir . "\radiologist_settings.ini"
    IniWrite, %LOGI%, %settingsFile%, Login, Username
    IniWrite, %PWD%, %settingsFile%, Login, Password
    IniWrite, %varWhere%, %settingsFile%, Location, ComputerLocation
    IniWrite, %vExamLoc%, %settingsFile%, Server, ExamLocation
    IniWrite, %API_KEY%, %settingsFile%, AI, APIKey      ; 存 GPT Key
    IniWrite, %API_KEY2%, %settingsFile%, AI, APIKey2    ; 存 Gemini Key
}

; 從檔案載入設定 (實際應用時可自行實作)
LoadSettingsFromFile() {
    settingsFile := A_ScriptDir . "\radiologist_settings.ini"
    if (FileExist(settingsFile)) {
        IniRead, LOGI, %settingsFile%, Login, Username, %LOGI%
        IniRead, PWD, %settingsFile%, Login, Password, %PWD%
        IniRead, varWhere, %settingsFile%, Location, ComputerLocation, %varWhere%
        IniRead, vExamLoc, %settingsFile%, Server, ExamLocation, %vExamLoc%
        IniRead, API_KEY, %settingsFile%, AI, APIKey, %API_KEY%
        IniRead, API_KEY2, %settingsFile%, AI, APIKey2, %API_KEY2% ; 讀取 Gemini Key
    }
}

; 新增熱鍵來開啟設定管理器
#\::  ; Win+\ 開啟設定管理器
    CreateConfigManager()
return


; ==========================================
; 方法2: 使用帶參數的函數 (推薦)
; ==========================================
; ✅ 推薦：使用數字參數，語意清晰
;CopyCXRtoHISWithParam(0)  ; 不移動不換行
;CopyCXRtoHISWithParam(1)  ; 只換行
;CopyCXRtoHISWithParam(2)  ; 完整移動

; ⚠️ 可以但不推薦：使用 true/false
; CopyCXRtoHISWithParam(false)  ; = 0
; CopyCXRtoHISWithParam(true)   ; = 1

CopyCXRtoHISWithParam(moveDown := 2) {
    if (moveDown = 2)
        ActivateHIS()
    else
        ActivateHISLight()

    ; 開頭的移動（只在模式 2 時）
    if (moveDown = 3) {
        SendInput {End}{Down}
        SendInput {End}{Down}
    }
    
    ; 清理 desc 末尾的多餘空白
    desc := RTrim(desc, " `t`r`n")
    
    SendInput %desc%
    desc := ""

    ; 最後的換行（模式 1 或 2）
    if (moveDown) {  ; 只要非零就換行
        SendInput `r
    }
}



; ============================================================================
; XButton2 多功能切換
; ============================================================================

XButton2::
    ; 優先檢查 USAIGUI 視窗
    if WinExist("超音波 AI 分析") {
        Gosub, XButton2_USAIGUI
        return
    }
    
    ; 檢查 AI Findings 視窗
    if WinExist("Impression → Findings") {
        Gosub, XButton2_AIFindings
        return
    }
    
    ; 預設功能：查看舊報告
    OpenReportComparison(GetAccessionNumber())
return

; ============================================================================
; 巨集 A：USAIGUI - 自動擷取並貼上影像
; ============================================================================
XButton2_USAIGUI:
    ; 記錄原始滑鼠位置
    MouseGetPos, origX, origY

    ; 移動到 DICOM 左螢幕位置
    Gosub, PosDICOMLU
    Sleep, 100

    ; 複製影像（Ctrl+C）
    Send, ^c
    Sleep, 300  ; 等待影像複製完成

    ; --- 自動取得 DICOM Series/Instance Number ---
    ; 注意：不使用 clipboard 變數，以免覆蓋剛複製的影像
    Gosub, PosDICOMLU
    Send, {LButton}
    Gosub, PosDICOMButton
    Send, {LButton}
    Gosub, PosDICOMLU
    Send, {LButton}
    Send, {LButton}{LButton}
    WinWaitActive, DICOM 檔頭訊息, , 2
    if (ErrorLevel = 0) {
        ControlGetText, USAI_DICOMText, Edit3, DICOM 檔頭訊息
        Sleep, 120
        Send, {Esc}{Esc}
        USAI_DICOMSeries := GetDICOMLineData("Series Number", USAI_DICOMText)
        USAI_DICOMInstance := GetDICOMLineData("Instance Number", USAI_DICOMText)
    } else {
        USAI_DICOMSeries := ""
        USAI_DICOMInstance := ""
    }
    ; --- END DICOM ---

    ; 恢復滑鼠位置
    MouseMove, %origX%, %origY%

    ; 啟動 USAIGUI 視窗
    WinActivate, 超音波 AI 分析
    Sleep, 100

    ; 執行貼上影像1
    Gosub, USAIPasteImage1

    ; 提示
    TrayTip, XButton2, 影像已自動擷取並貼上, 2, 1
return

; ============================================================================
; 巨集 B：AI Findings - 自動填入 Impression
; ============================================================================
XButton2_AIFindings:
    ; 從 HIS 取得 Impression 內容
    impressionText := ""
    ControlGetText, impressionText, ThunderRT6TextBox14, ahk_exe chk060.exe
    
    ; 檢查是否成功取得內容
    if (impressionText = "") {
        MsgBox, 48, 提示, 無法從 HIS 取得 Impression 內容`n請確認：`n1. HIS 視窗已開啟`n2. Impression 欄位有內容
        return
    }
    
    ; 啟動 AI Findings 視窗
    WinActivate, Impression → Findings (AI)
    Sleep, 100
    
    ; 清空原有內容
    GuiControl, I2F:, I2F_Impression, 
    
    ; 填入 Impression 內容
    GuiControl, I2F:, I2F_Impression, %impressionText%
    
    ; 提示使用者
    TrayTip, AI Findings, Impression 已自動填入`n請檢查內容後按 Generate, 3, 1
    
    ; 可選：自動聚焦到 Generate 按鈕（讓使用者可以直接按 Enter）
    ControlFocus, Button1, Impression → Findings (AI)
return

GetSideSelection:
    ; 初始化變數，避免殘留舊值
    tSideCap := "_"
    tSideLow := "_"
    
    ; 建立 GUI
    Gui, GenSide:Destroy
    Gui, GenSide:New, +AlwaysOnTop +ToolWindow +Owner, 選擇方向
    Gui, GenSide:Font, s12, 微軟正黑體
    Gui, GenSide:Add, Text, x10 y15 w200 Center, 請選擇方向
    
    ; 設定按鈕
    Gui, GenSide:Add, Button, x10 y50 w95 h40 gGenSelectLeft, 左側 (&L)
    Gui, GenSide:Add, Button, x115 y50 w95 h40 gGenSelectRight, 右側 (&R)
    
    ; 顯示視窗
    Gui, GenSide:Show, w220 h110
    
    ; [關鍵] 等待這個視窗關閉後，程式才會繼續往下執行
    WinWaitClose, 選擇方向
return

; --- 通用左側按鈕邏輯 ---
GenSelectLeft:
    tSideCap := "Left"
    tSideLow := "left"
    Gui, GenSide:Destroy
return

; --- 通用右側按鈕邏輯 ---
GenSelectRight:
    tSideCap := "Right"
    tSideLow := "right"
    Gui, GenSide:Destroy
return

; --- 如果使用者直接按 X 關閉，給予預設值或保持空白 ---
GenSideGuiClose:
GenSideGuiEscape:
    Gui, GenSide:Destroy
return

; ============================================================================
; chk060 RIS 行交換快捷鍵 (Ctrl+Up / Ctrl+Down)
; ============================================================================
#IfWinActive, ahk_class ThunderRT6FormDC

^Up::   ; Ctrl+Up: 將目前行往上移，游標跟隨
    Send, {Home}+{Down}^x{Up}{Home}^v{Up}
return

^Down:: ; Ctrl+Down: 將目前行往下移，游標跟隨
    Send, {Home}+{Down}^x{Down}{Home}^v{Down}
return

#IfWinActive
