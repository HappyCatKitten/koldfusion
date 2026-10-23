<HTML>
<HEAD><TITLE>CFHTMLHEAD example</TITLE></HEAD>
<BODY>
<H3 CLASS="fancy">A heading styled from the bottom of the page</H3>
<P>The style sheet for the heading above is defined by a CFHTMLHEAD tag that runs
after the heading has been written. View the source of this frame to see where it went.</P>
<CFSET Shade = "##336699">
<CFHTMLHEAD TEXT="<STYLE TYPE=""text/css"">H3.fancy { color: #Shade#; font-family: Arial, Helvetica; }</STYLE>">
</BODY>
</HTML>
