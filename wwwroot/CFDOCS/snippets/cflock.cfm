<CFAPPLICATION NAME="KFSnippets" SESSIONMANAGEMENT="Yes">

<!--- Writers take an exclusive lock... --->
<CFLOCK SCOPE="Application" TYPE="Exclusive" TIMEOUT="10">
  <CFPARAM NAME="Application.LockDemoHits" DEFAULT="0">
  <CFSET Application.LockDemoHits = Application.LockDemoHits + 1>
</CFLOCK>

<!--- ...readers share a read-only lock and copy what they need --->
<CFLOCK SCOPE="Application" TYPE="ReadOnly" TIMEOUT="10">
  <CFSET Hits = Application.LockDemoHits>
</CFLOCK>

<!--- A named lock with THROWONTIMEOUT="No" simply skips its body on a timeout --->
<CFSET GotIt = "No">
<CFLOCK NAME="SnippetsGuestBook" TYPE="Exclusive" TIMEOUT="5" THROWONTIMEOUT="No">
  <CFSET GotIt = "Yes">
</CFLOCK>

<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>Hits on this example since the server started</TD><TD ALIGN=RIGHT>#Hits#</TD></TR>
<TR><TD>Got the named lock SnippetsGuestBook?</TD><TD ALIGN=RIGHT>#GotIt#</TD></TR>
</TABLE>
</CFOUTPUT>
