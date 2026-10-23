<CFSET Files = "report.cfm,logo.gif,readme.txt">
<CFOUTPUT>
<UL>
<CFLOOP LIST="#Files#" INDEX="f">
<LI>#f# has the extension #Right(f, 3)#
</CFLOOP>
<LI>Order number #Right("00000" & 42, 5)#
</UL>
</CFOUTPUT>
