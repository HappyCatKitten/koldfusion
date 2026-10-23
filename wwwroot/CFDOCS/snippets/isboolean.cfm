<CFPARAM NAME="URL.ShowAll" DEFAULT="Yes">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>value</TH><TH>IsBoolean</TH></TR>
<CFLOOP INDEX="v" LIST="Yes,no,TRUE,false,0,12,-1.5,maybe,Y2K">
<CFOUTPUT><TR><TD>#v#</TD><TD>#IsBoolean(v)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<CFIF IsBoolean(URL.ShowAll) AND URL.ShowAll>
  <P>URL.ShowAll is a valid Boolean and it is true.
<CFELSE>
  <P>URL.ShowAll is false or not a Boolean.
</CFIF>
