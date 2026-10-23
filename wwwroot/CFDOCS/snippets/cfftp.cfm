<!--- Is there an FTP server on this machine? Ask politely with STOPONERROR="No" --->
<CFFTP ACTION="Open" SERVER="127.0.0.1" USERNAME="anonymous" PASSWORD="someone@localhost"
       CONNECTION="Demo" TIMEOUT="10" STOPONERROR="No">
<CFIF CFFTP.Succeeded>
  <CFFTP ACTION="ListDir" CONNECTION="Demo" DIRECTORY="/" NAME="Files" STOPONERROR="No">
  <CFFTP ACTION="Close" CONNECTION="Demo" STOPONERROR="No">
  <CFIF IsDefined("Files")>
    <TABLE BORDER=1 CELLPADDING=3>
    <TR><TH>Name</TH><TH>Size</TH><TH>Directory?</TH></TR>
    <CFOUTPUT QUERY="Files">
    <TR><TD>#Name#</TD><TD>#Length#</TD><TD>#IsDirectory#</TD></TR>
    </CFOUTPUT>
    </TABLE>
  </CFIF>
<CFELSE>
  <CFOUTPUT>
  <TABLE BORDER=1 CELLPADDING=3>
  <TR><TD>CFFTP.Succeeded</TD><TD>#CFFTP.Succeeded#</TD></TR>
  <TR><TD>CFFTP.ErrorCode</TD><TD>#CFFTP.ErrorCode#</TD></TR>
  <TR><TD>CFFTP.ErrorText</TD><TD>#CFFTP.ErrorText#</TD></TR>
  </TABLE>
  </CFOUTPUT>
</CFIF>
