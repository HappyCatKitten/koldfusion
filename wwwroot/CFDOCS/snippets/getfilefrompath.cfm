<CFSET Paths = "#GetCurrentTemplatePath()#|C:\CFUSION\MAIL\SPOOL\Mail1.cfmail|/home/kf/readme.txt|plain.htm">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Path</TH><TH>GetFileFromPath</TH><TH>Extension</TH></TR>
<CFLOOP LIST="#Paths#" DELIMITERS="|" INDEX="p">
<CFOUTPUT><TR><TD>#p#</TD><TD>#GetFileFromPath(p)#</TD><TD>#ListLast(GetFileFromPath(p), ".")#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
