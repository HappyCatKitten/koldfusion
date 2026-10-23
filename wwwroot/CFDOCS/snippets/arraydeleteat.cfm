<CFSET Browsers = ListToArray("Netscape 4.7,Mosaic,Internet Explorer 5,Lynx")>
<CFOUTPUT>
<P>Before: #ArrayToList(Browsers, ", ")#</P>
<!--- Mosaic has retired --->
<CFSET Temp = ArrayDeleteAt(Browsers, 2)>
<P>After ArrayDeleteAt(Browsers, 2): #ArrayToList(Browsers, ", ")#</P>
<P>Element 2 is now <B>#Browsers[2]#</B>.</P>
</CFOUTPUT>
