<!--- Edits comment 3, then puts it back the way it was --->
<CFQUERY NAME="Original" DATASOURCE="cfsnippets">
SELECT CommentID, Subject FROM Comments WHERE CommentID = 3
</CFQUERY>
<CFIF IsDefined("Form.CommentID")>
  <CFUPDATE DATASOURCE="cfsnippets" TABLENAME="Comments" FORMFIELDS="CommentID,Subject">
  <CFQUERY NAME="Changed" DATASOURCE="cfsnippets">
  SELECT Subject FROM Comments WHERE CommentID = 3
  </CFQUERY>
  <CFOUTPUT>
  <TABLE BORDER=1 CELLPADDING=3>
  <TR><TD>Subject before</TD><TD>#HTMLEditFormat(Original.Subject)#</TD></TR>
  <TR><TD>Subject after CFUPDATE</TD><TD>#HTMLEditFormat(Changed.Subject)#</TD></TR>
  </TABLE>
  </CFOUTPUT>
  <!--- Restore the original subject for the next visitor --->
  <CFQUERY DATASOURCE="cfsnippets">
  UPDATE Comments
  SET Subject = <CFQUERYPARAM VALUE="#Original.Subject#" CFSQLTYPE="CF_SQL_VARCHAR">
  WHERE CommentID = 3
  </CFQUERY>
  <P>(The original subject has been restored.) <A HREF="cfupdate.cfm">Try again</A></P>
<CFELSE>
  <CFOUTPUT>
  <FORM ACTION="cfupdate.cfm" METHOD="POST">
  <INPUT TYPE="Hidden" NAME="CommentID" VALUE="#Original.CommentID#">
  Subject of comment #Original.CommentID#:
  <INPUT TYPE="Text" NAME="Subject" SIZE=30 VALUE="#HTMLEditFormat(Original.Subject)# - is my PC Y2K OK?">
  <INPUT TYPE="Submit" VALUE="Update">
  </FORM>
  </CFOUTPUT>
</CFIF>
