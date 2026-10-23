<!--- Clicking a link redirects back to this page with a "from" parameter --->
<CFPARAM NAME="URL.Go" DEFAULT="">
<CFPARAM NAME="URL.From" DEFAULT="">
<CFIF URL.Go IS NOT "">
  <CFLOCATION URL="cflocation.cfm?From=#URLEncodedFormat(URL.Go)#" ADDTOKEN="No">
</CFIF>

<CFIF URL.From IS NOT "">
  <CFOUTPUT>
  <P><IMG SRC="/CFIDE/administrator/images/check.gif" WIDTH=16 HEIGHT=16>
  You arrived here through a <B>302 Object Moved</B> redirect.
  The link you clicked was <B>#HTMLEditFormat(URL.From)#</B>.</P>
  </CFOUTPUT>
</CFIF>

<P>Pick a destination. Each link calls this page with a "Go" parameter,
and CFLOCATION then sends your browser on.</P>
<UL>
  <LI><A HREF="cflocation.cfm?Go=Departure+Lounge">Departure Lounge</A>
  <LI><A HREF="cflocation.cfm?Go=Y2K+Bunker">Y2K Bunker</A>
  <LI><A HREF="cflocation.cfm">Start over (no redirect)</A>
</UL>
