<CFSET Things = StructNew()>
<CFSET Things.AString = "Hello">
<CFSET Things.ANumber = 56000>
<CFSET Things.ADate = Now()>
<CFSET Things.AnArray = ArrayNew(1)>
<CFSET Things.AStruct = StructNew()>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Key</TH><TH>IsSimpleValue</TH><TH>Value</TH></TR>
<CFLOOP COLLECTION="#Things#" ITEM="k">
<CFOUTPUT><TR><TD>#k#</TD><TD>#IsSimpleValue(Things[k])#</TD>
<TD><CFIF IsSimpleValue(Things[k])>#Things[k]#<CFELSE><I>(complex value)</I></CFIF></TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
