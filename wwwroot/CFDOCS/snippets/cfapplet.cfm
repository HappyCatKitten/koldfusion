<CFFORM NAME="News" ACTION="cfapplet.cfm">
<P>Today's headline ticker:
<CFAPPLET APPLETSOURCE="marquee" NAME="Ticker" WIDTH="400"
    NOTSUPPORTED="<I>Your browser cannot run Java, so here is the news
    as text: KoldFusion 4.5 ships! Y2K compliance certified!</I>">

<P>An applet that nobody registered:
<CFTRY>
  <CFAPPLET APPLETSOURCE="dancing_hamster" NAME="Hamster">
<CFCATCH TYPE="Any">
  <CFOUTPUT><I>#CFCATCH.Message#</I></CFOUTPUT>
</CFCATCH>
</CFTRY>
</CFFORM>
