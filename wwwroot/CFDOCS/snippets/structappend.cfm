<CFSET Prefs = StructNew()>
<CFSET Prefs.Color = "Teal">
<CFSET Defaults = StructNew()>
<CFSET Defaults.Color = "Gray">
<CFSET Defaults.Font = "Arial">
<CFSET Defaults.Modem = "56K">

<CFSET Temp = StructAppend(Prefs, Defaults, "No")>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Key</TH><TH>Value</TH></TR>
<CFLOOP LIST="#StructKeyList(Prefs)#" INDEX="Key">
<CFOUTPUT><TR><TD>#Key#</TD><TD>#Prefs[Key]#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
