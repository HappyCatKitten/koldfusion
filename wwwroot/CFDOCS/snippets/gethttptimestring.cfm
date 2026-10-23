<CFSET Expires = DateAdd("d", 1, Now())>
<CFHEADER NAME="Expires" VALUE="#GetHTTPTimeString(Expires)#">
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>GetHTTPTimeString()</TD><TD>#GetHTTPTimeString()#</TD></TR>
<TR><TD>Tomorrow (sent as Expires)</TD><TD>#GetHTTPTimeString(Expires)#</TD></TR>
</TABLE>
</CFOUTPUT>
