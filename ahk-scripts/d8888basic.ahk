; ============================================================================
; HIS 介面函數 (chk060.exe)
; ============================================================================

CopyReportHIS(byref output)
{
	text:= ""
	ControlGetText, text, ThunderRT6TextBox14, ahk_exe chk060.exe
	if ErrorLevel
	{
		return false
	}
	output:=text
	return true
}

SetReportHIS(input)
{
	ControlSetText,ThunderRT6TextBox14,%input%, ahk_exe chk060.exe
}

SetReportImpression(input)
{
	ControlSetText,ThunderRT6TextBox5,%input%, ahk_exe chk060.exe
}

; ============================================================================
; StoredText 文字緩衝區 (用於 BMD 報告組裝)
; ============================================================================

StoredText := ""

StoredTextClear()
{
	global StoredText
	StoredText := ""
}

StoredTextAdd(s)
{
	global StoredText
	StoredText := StoredText . s
}

StoredTextNewLine()
{
	global StoredText
	ent := Chr(13) . Chr(10)
	StoredText := StoredText . ent
}
