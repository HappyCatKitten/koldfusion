<!--- ch6_counter.cfm: session and application variables.
      In a real application the CFAPPLICATION tag would live in Application.cfm. --->
<CFAPPLICATION NAME="DevGuideCounter"
    SESSIONMANAGEMENT="Yes"
    SESSIONTIMEOUT="#CreateTimeSpan(0, 0, 20, 0)#"
    APPLICATIONTIMEOUT="#CreateTimeSpan(1, 0, 0, 0)#">

<!--- Shared data must be locked while it is changed --->
<CFLOCK SCOPE="Application" TYPE="Exclusive" TIMEOUT="10">
  <CFPARAM NAME="Application.TotalHits" DEFAULT="0">
  <CFSET Application.TotalHits = Application.TotalHits + 1>
  <CFSET MyTotal = Application.TotalHits>
</CFLOCK>

<CFLOCK SCOPE="Session" TYPE="Exclusive" TIMEOUT="10">
  <CFPARAM NAME="Session.Hits" DEFAULT="0">
  <CFPARAM NAME="Session.FirstVisit" DEFAULT="#Now()#">
  <CFSET Session.Hits = Session.Hits + 1>
  <CFSET MyHits = Session.Hits>
  <CFSET MyFirst = Session.FirstVisit>
</CFLOCK>

<CFINCLUDE TEMPLATE="ch6_header.cfm">
<CFOUTPUT>
<P>You have viewed this page <B>#MyHits#</B> time(s) since
#TimeFormat(MyFirst, "h:mm:ss tt")#.</P>
<P>All visitors together: <B>#MyTotal#</B> view(s) since the
application started.</P>
</CFOUTPUT>
<P><A HREF="ch6_counter.cfm">Reload</A> the page to count up. Open it in a different
browser and you get a new session, but the shared total keeps growing.</P>
<CFINCLUDE TEMPLATE="ch6_footer.cfm">
