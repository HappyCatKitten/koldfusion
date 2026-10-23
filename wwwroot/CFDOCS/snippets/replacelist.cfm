<CFSET Shorthand = "Pls call me b4 lunch, thx, cu l8r">
<CFSET Short = "Pls,b4,thx,cu,l8r">
<CFSET Long = "Please,before,thanks,see you,later">
<CFOUTPUT>
<P><B>Before:</B> #Shorthand#</P>
<P><B>After:</B> #ReplaceList(Shorthand, Short, Long)#</P>
</CFOUTPUT>
