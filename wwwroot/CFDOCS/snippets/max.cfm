<CFPARAM NAME="URL.Page" DEFAULT="-3">
<CFSET SafePage = Min(Max(URL.Page, 1), 10)>
<CFOUTPUT>
<P>Max(3, 7) = #Max(3, 7)#<BR>
Max(-1, -1.5) = #Max(-1, -1.5)#<BR>
Requested page #URL.Page#, clamped to 1-10: page #SafePage#
</CFOUTPUT>
