<CFSET Line = "Sales    Boston   MA  02110">
<CFSET Path = "C:\CFUSION\CustomTags\cf_hello.cfm">
<CFOUTPUT>
<UL>
<LI>Token 2 of "#Line#": #GetToken(Line, 2)#
<LI>Token 4: #GetToken(Line, 4)#
<LI>Token 9: [#GetToken(Line, 9)#]
<LI>Token 3 of the path, split at "\": #GetToken(Path, 3, "\")#
</UL>
</CFOUTPUT>
