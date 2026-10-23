<CFSET Items = "Y2K,KoldFusion,Netscape">
<PRE>
<CFLOOP LIST="#Items#" INDEX="item"><CFOUTPUT>[#CJustify(item, 14)#]
</CFOUTPUT></CFLOOP></PRE>
