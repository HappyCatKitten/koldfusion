<CFSET Names = "smith,Smith,SMITH,Smythe">
<UL>
<CFLOOP LIST="#Names#" INDEX="n">
<CFOUTPUT><LI>CompareNoCase("Smith", "#n#") = #CompareNoCase("Smith", n)#</CFOUTPUT>
</CFLOOP>
</UL>
