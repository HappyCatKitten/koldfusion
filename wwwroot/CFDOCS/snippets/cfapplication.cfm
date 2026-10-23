<CFAPPLICATION NAME="KFSnippets"
    SESSIONMANAGEMENT="Yes"
    SESSIONTIMEOUT="#CreateTimeSpan(0, 0, 20, 0)#">

<CFLOCK SCOPE="Session" TYPE="Exclusive" TIMEOUT="10">
  <CFPARAM NAME="Session.Visits" DEFAULT="0">
  <CFSET Session.Visits = Session.Visits + 1>
  <CFSET Visits = Session.Visits>
  <CFSET Token = Session.URLToken>
</CFLOCK>

<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>Application.ApplicationName</TD><TD>#Application.ApplicationName#</TD></TR>
<TR><TD>Session.URLToken</TD><TD>#Token#</TD></TR>
<TR><TD>Visits in this session</TD><TD>#Visits#</TD></TR>
</TABLE>
<P><A HREF="cfapplication.cfm">Reload</A> and watch the counter go up.</P>
</CFOUTPUT>
