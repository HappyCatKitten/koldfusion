<CFSET Right_Now = Now()>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>Now()</TD><TD>#Right_Now#</TD></TR>
<TR><TD>Formatted</TD><TD>#DateFormat(Right_Now, "dddd, mmmm d, yyyy")# at #TimeFormat(Right_Now, "h:mm tt")#</TD></TR>
<TR><TD>A week from now</TD><TD>#DateFormat(DateAdd("ww", 1, Right_Now), "mmmm d, yyyy")#</TD></TR>
<TR><TD>Days since Jan 1, 2000</TD><TD>#DateDiff("d", CreateDate(2000, 1, 1), Right_Now)#</TD></TR>
</TABLE>
</CFOUTPUT>
