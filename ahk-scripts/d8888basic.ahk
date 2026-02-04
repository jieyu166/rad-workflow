

IfHISExist()
{
	IfWinExist ahk_exe chk060.exe
	{
		return true
	}
	return false
}

CopyReportHIS(byref output)
{
	text:= ""
	ControlGetText, text, ThunderRT6TextBox14, ahk_exe chk060.exe
	if ErrorLevel
	{
		;something wrong when getting text
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




_Strup(word)
{
	StringUpper, word, word
	return word
}

Capitalize(input)
{
	reg=Om)^((\d+\s*\.*)\s*)([a-z])(.*)
	While(1)
	{
		FoundPos := RegExMatch(input, reg , match)
		if(FoundPos=0)
		{
			break
		}
		
		newsubstr:= match.Value(1) _Strup(match.Value(3)) match.Value(4)
		
		input:=SubStr(input,1,match.Pos(0)-1) newsubstr SubStr(input,match.Pos(0)+match.Len(0))
	}

	return input
}

PadLines(input)
{
	; pad spaces from 2nd line
		

	reg=Om)(^\d+\s*\.\s*[^\n]*\n)(\s{0,2}(?!(\d+\s*\.))[^\s][^\n]*\n)+
	While(1)
	{
		FoundPos := RegExMatch(input, reg , match)
		if(FoundPos=0)
		{
			break
		}
		
		newsubstr:= "   " trim(match.Value(2))
		
		input:=SubStr(input,1,match.Pos(2)-1) newsubstr SubStr(input,match.Pos(2)+match.Len(2))
		
	}

	return input
	
}

RepeatChar(num, char)
{
	rst:=""
	Loop, %num%
	{
		rst:=rst char
	}
		
	return rst
}

_dbgMsg(str)
{
	str:="|" str "|"
	MsgBox %str%
}


BatchFormatBlock(text, reg, nspace, removenewline=1)
{
	
	rsttext:=""
	while(1)
	{
		FoundPos := RegExMatch(text, reg , match)
		if(FoundPos=0)
		{
			break
		}
	
		
		pretext:=SubStr(text, 1, match.Pos(0)-1)
		newsubstr:=FormatBlock(match.Value(0),nspace, removenewline)
		
		rsttext:=rsttext pretext newsubstr	
		;_dbgMsg(pretext)
		;_dbgMsg(newsubstr)
		;_dbgMsg(rsttext)
		;if(InStr(rsttext,"`r`n")>0)
		;{
		;	rsttext:= rsttext "`r`n"
		;}
		
		rsttext:=rtrim(rsttext,"`r`n") "`r`n"
		
		text:=SubStr(text, match.Pos(0)+match.Len(0))	
		
	}
	rsttext:=rsttext text
	return rsttext
}

RemoveNewline(input)
{
	input:=StrReplace(input,"`n"," ")
	input:=StrReplace(input,"`r","")
	return input
}

ImpressionPadSpace(text)
{
	; match all first line of impressions 
	
	reg=Om)^\d+\.(?!\d)\s?((^\d(?!\d*\.(?!\d))|^\D|(?<!^).|\n|\r))*
	return BatchFormatBlock(text, reg,3,0)
}


BreastPadSpace(text)
{
	; match all breast nodule description
	reg=Om)^((Lt)|(Rt))\(\d+\/\d+\)((?!(((Lt)|(Rt))\(\d+\/\d+\))).|\n|\r)*
	return BatchFormatBlock(text, reg,29)

}

BreastFirstLine(text)
{
	; 參考 BreastPadSpace 修改
	reg=Om)^(((Lt)|(Rt))\(\d+\/\d+\))\s*([0-9.*]+)\s*(((?!(((Lt)|(Rt))\(\d+\/\d+\))).|\n|\r)*)
	
	
	pos1:=23
	pos2:=29

	rsttext:=""
	while(1)
	{
		FoundPos := RegExMatch(text, reg , match)
		if(FoundPos=0)
		{
			break
		}
		
		;_dbgMsg(match.Value(0))
		;_dbgMsg(match.Len(1))
		;_dbgMsg(match.Len(5))
		;_dbgMsg(match.Len(6))
		;_dbgMsg(pos1-match.Len(1)-match.Len(5))
		;_dbgMsg(RepeatChar(pos1-match.Len(1)-match.Len(5)," "))
		
		newstr:= match.Value(1) RepeatChar(pos1-match.Len(1)-match.Len(5)," ")
		
		newstr:= newstr match.Value(5) RepeatChar(pos2-StrLen(newstr)-match.Len(5)," ")
		newstr:= newstr match.Value(6)
						
		pretext:=SubStr(text, 1, match.Pos(0)-1)
		rsttext:=rsttext pretext newstr	
		text:=SubStr(text, match.Pos(0)+match.Len(0))	
	}
	rsttext:=rsttext text
	return rsttext
}

_IsFirstWord(input, blankln, spacestr)
{
	/*
	if(input=blankln)
	{
		return true
	}
	tmpstr:=blankln spacestr
	if(input=tmpstr)
	{
		return true
	}
	*/
	
	if(trim(input, " `r`n`t`b")="")
	{
		return true
	}
	
	return false
}

_msgrst(rst)
{
	dbg:="|" rst "|"
	MsgBox %dbg%
}


FormatBlock(input, nspace, removenewline)
{
	; pad spaces from 2nd line for breast nodule report
	
	; 資訊室打報告系統一行最大長度
	maxlinelen:=80
	

	space:=" "
	newln:="`r`n"
	dbg:=""	
	blankln:=dbg
	
	; 把多個空白合併成一個
	;input := RegExReplace(input, "m)[ ]{2,}", " ")
	
	
	if(removenewline=1)
	{
		input:=StrReplace(input,"`r","")
		input:=StrReplace(input,"`n"," ")
	}else
	{
		input:=StrReplace(input,"`r","")
		input:=StrReplace(input,"`n"," =====CRLF===== ")
		;MsgBox ya
	}
	;_dbgMsg(input)
	
	word_array := StrSplit(input, " ")
	spacestr:=RepeatChar(nspace," ")
	
	currentline:=blankln
	rst:=""
	
	
	
	Loop % word_array.MaxIndex()
	{
		nowword:=word_array[A_Index]
		;_dbgMsg(nowword)
	
		if(nowword="=====CRLF=====")
		{
			; 剛好有換行過就不用再換
			if(rst!="" && !_IsFirstWord(currentline, blankln, spacestr))
			{
				rst:=rst newln
			}
			rst:=rst currentline
			currentline:=blankln
			;MsgBox 換行 3
			continue
		}

	
		; 是否要換行？
		if(StrLen(currentline)+StrLen(nowword)+StrLen(space)>maxlinelen)
		{
			
			; 換行
			if(rst!="")
			{
				rst:=rst newln
			}
			rst:=rst currentline
			currentline:=blankln
			
			;MsgBox 換行 1
		}
		
		; 是否為第二行以後的行首？
		;if(rst!="" && _IsFirstWord(currentline, blankln, spacestr))
		if(rst!="" && currentline="" && StrLen(nowword)>0)
		{
			;MsgBox hahaha
			currentline:=spacestr
			;_dbgMsg(nowword)
		}
		
		
		if(not _IsFirstWord(currentline, blankln, spacestr))
		{
			currentline:=currentline space
		}
		currentline:=currentline nowword
		
		
		
		
		;_dbgMsg("nowword:" nowword)		
		;_dbgMsg("currentline:" currentline)	
		;_dbgMsg("rst:" rst)
		
	}
	; 最後沒處理完的
	if(currentline!="")
	{
		if(rst!="")
		{
			rst:=rst newln
		}
		rst:=rst currentline
	}
	
	;_dbgMsg(rst)
	return rst	
	
	
}





ArrangeTextByNumber(text)
{
	Now :=1
	
	while(1)
	{

	   r := Now
	   r := r "=====QQQQQXDRZQQQQ====="
	 

	   NewText := RegExReplace(text, "m)^[0-9]+\.(?![0-9])", r,tmp,1)
	   if(NewText=text)
	   {
			;MsgBox Break
			break
	   }else
	   {
			;MsgBox Ya
			;MsgBox %NewText%
			;MsgBox %text%
	   }
	   text := NewText
	   Now := Now+1
	}
	StringReplace, text, text,=====QQQQQXDRZQQQQ=====,.,1

	text := RegExReplace(text, "m)^(\d{1}\.)(?![0-9])(\S)", "$1 $2",tmp)
	
	text := RegExReplace(text, "m)^(\d{2}\.) ", "$1",tmp)
	
	
	
	text:=Capitalize(text)
	text:=ImpressionPadSpace(text)
	return text

}


ShowMenuSelector(macro, target)
{
	ClipBoard := macro
	rstr := "D:\python\App\python.exe D:\python\App\Code\hello.py "
	rstr := rstr . target
	RunWait ,%rstr%
	err=
	(
An error has occured, the differential diagnosis includes:
	1. Python enviroment not set correctly and cannot be run
	2. There is error in template script, either single or multiple
	3. The Python program crashed.
	4. Or others
Advise clinical correlation and further evaluation.
	)
	ifNotEqual, ClipBoard, %macro%
	{
		PasteText(ClipBoard)
	}else
	{
		PasteText(err)
	}
	
}


ActivatePACS2()
{
	WinGet, id, list, INFINITT PACS
	num:=2
	this_id := id%num%
	WinActivate, ahk_id %this_id%
	return this_id
}
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

StoredTextPurge()
{
	global StoredText
	
    ClipBoard := ""
    ClipBoard := StoredText
    
    now:= A_TickCount
    while(1)
    {
        if(ClipBoard=StoredText)
        {
            break
        }
        if(A_TickCount > (now+500))
        {
            break
        }
    }
    
    if(ClipBoard=StoredText)
    {
        Send ^v
    }
    StoredTextClear()
}

PasteText(s)
{
	
	StoredTextClear()
	s:=ConvertCrLf(s)
	StoredTextAdd(s)

    sleep, 50
    ;ActivateHIS() ; 會跟 CEF 衝突
	StoredTextPurge()
	
}

ConvertCrLf(str)
{
	ret:=""
	Loop, parse, str, `n
	{
		if(ret!="")
		{
			ret:=ret . Chr(13)
			ret:=ret . Chr(10)
		}
		ret:= ret . A_LoopField
	}
	return ret
}

GetQryLabPatientID()
{
	text:=""
	
	
	
	ControlGetText, text, ThunderRT6TextBox15,ahk_exe qrylab.exe

	text = %text% ; trim spaces
	
	if(StrLen(text)<8)
	{
		return ""
	}else
	{
	}
	
	
	return text
}

d8trim(str)
{
	rst:=trim(str," `t`n`r")
	return rst
}

GetCHK060PatientID()
{
	;Process, wait, chk060.exe, 1
	;NewPID = %ErrorLevel%  ; Save the value immediately since ErrorLevel is often changed.
	;if(NewPID=0)
	;{
	;	return ""
	;}
	
	
	
	text:=""
	
	;ControlGetText, text, ThunderRT6TextBox9,ahk_pid %NewPID% ;Get Patient ID
	
	ControlGetText, text, ThunderRT6TextBox12, ahk_exe chk060.exe

	text = %text% ; trim spaces
	
	if(StrLen(text)<8)
	{
		return ""
	}else
	{
	}
	
	
	return text
}

GetQryReport(byref report)
{
	Process, wait, qrylab.exe, 1
	NewPID = %ErrorLevel%  ; Save the value immediately since ErrorLevel is often changed.

	if(NewPID=0)
	{
		return false
	}	

	ControlGetText, text, RichTextWndClass1, ahk_pid %NewPID%
	if ErrorLevel
	{
		;something wrong when getting text
		return false
	}
	report := text
	return true
}