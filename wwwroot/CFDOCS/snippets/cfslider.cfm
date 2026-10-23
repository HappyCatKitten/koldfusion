<CFIF IsDefined("Form.Volume")>
  <CFOUTPUT><P>Volume set to <B>#Form.Volume#</B>,
  modem speaker at <B>#Form.Speaker#</B>%.</CFOUTPUT>
</CFIF>

<CFFORM NAME="Mixer" ACTION="cfslider.cfm">
<TABLE CELLPADDING=4>
<TR><TD><CFSLIDER NAME="Volume" LABEL="Volume" RANGE="0,11" VALUE="7"></TD></TR>
<TR><TD><CFSLIDER NAME="Speaker" LABEL="Modem speaker" RANGE="0,100" SCALE="25"
    VALUE="100" BGCOLOR="##99CC99"></TD></TR>
</TABLE>
<INPUT TYPE="Submit" VALUE="Apply">
</CFFORM>
