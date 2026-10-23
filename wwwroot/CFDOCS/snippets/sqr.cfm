<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>number</TH><TH>Sqr(number)</TH></TR>
<CFLOOP INDEX="n" LIST="0,1,2,16,56000">
<CFOUTPUT><TR><TD ALIGN="RIGHT">#n#</TD><TD>#Sqr(n)#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<CFSET a = 3><CFSET b = 4>
<CFOUTPUT><P>Hypotenuse of a #a#-#b# right triangle: #Sqr(a^2 + b^2)#</CFOUTPUT>
<CFTRY>
  <CFSET x = Sqr(-1)>
  <CFCATCH TYPE="Expression"><P><I>Sqr(-1) is imaginary, and so is the result: an Expression error.</I></CFCATCH>
</CFTRY>
