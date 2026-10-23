<!--- Create a task, look at what was stored, and delete it again --->
<CFSET Tomorrow = DateFormat(DateAdd("d", 1, Now()), "mm/dd/yyyy")>
<CFSCHEDULE ACTION="Update" TASK="SnippetDemoTask" OPERATION="HTTPRequest"
            URL="/CFDOCS/index.cfm" STARTDATE="#Tomorrow#" STARTTIME="2:00 AM"
            INTERVAL="Daily" REQUESTTIMEOUT="60" PUBLISH="No">

<CFREGISTRY ACTION="GetAll" NAME="Stored" TYPE="String" SORT="Entry"
  BRANCH="HKEY_LOCAL_MACHINE\SOFTWARE\Gibson\KoldFusion\CurrentVersion\Schedule\SnippetDemoTask">
<P>The scheduler now knows this task:</P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Setting</TH><TH>Value</TH></TR>
<CFOUTPUT QUERY="Stored">
<CFIF Len(Value)><TR><TD>#Entry#</TD><TD>#Value#</TD></TR></CFIF>
</CFOUTPUT>
</TABLE>

<CFSCHEDULE ACTION="Delete" TASK="SnippetDemoTask">
<CFTRY>
  <CFSCHEDULE ACTION="Delete" TASK="SnippetDemoTask">
  <CFCATCH TYPE="Application">
    <CFOUTPUT><P>Deleted. A second Delete says: <I>#CFCATCH.Detail#</I></P></CFOUTPUT>
  </CFCATCH>
</CFTRY>
