<CFIF IsDefined("Form.FromUser")>
  <CFINSERT DATASOURCE="cfsnippets" TABLENAME="Comments"
            FORMFIELDS="FromUser,Email,Subject,CommtType,MessText">
  <CFQUERY NAME="Newest" DATASOURCE="cfsnippets">
  SELECT MAX(CommentID) AS LastID FROM Comments
  </CFQUERY>
  <CFQUERY NAME="Added" DATASOURCE="cfsnippets">
  SELECT * FROM Comments WHERE CommentID = #Newest.LastID#
  </CFQUERY>
  <CFOUTPUT QUERY="Added">
  <P>Thank you! Comment ###CommentID# was stored:</P>
  <TABLE BORDER=1 CELLPADDING=3>
  <TR><TD>From</TD><TD>#HTMLEditFormat(FromUser)# (#HTMLEditFormat(Email)#)</TD></TR>
  <TR><TD>Subject</TD><TD>#HTMLEditFormat(Subject)# [#CommtType#]</TD></TR>
  <TR><TD>Message</TD><TD>#HTMLEditFormat(MessText)#</TD></TR>
  </TABLE>
  </CFOUTPUT>
  <!--- Tidy up, so the next visitor finds the table as it was --->
  <CFQUERY DATASOURCE="cfsnippets">
  DELETE FROM Comments WHERE CommentID = #Newest.LastID#
  </CFQUERY>
  <P>(The row has been removed again.) <A HREF="cfinsert.cfm">Try again</A></P>
<CFELSE>
  <FORM ACTION="cfinsert.cfm" METHOD="POST">
  Name: <INPUT TYPE="Text" NAME="FromUser" VALUE="Pat Kowal"><BR>
  Email: <INPUT TYPE="Text" NAME="Email" VALUE="pat@localhost"><BR>
  Subject: <INPUT TYPE="Text" NAME="Subject" VALUE="Nice site"><BR>
  Type: <SELECT NAME="CommtType"><OPTION>Praise<OPTION>Question<OPTION>Bug Report</SELECT><BR>
  <TEXTAREA NAME="MessText" ROWS=3 COLS=40>Loads fast even on my 56K modem.</TEXTAREA><BR>
  <INPUT TYPE="Submit" VALUE="Insert comment">
  </FORM>
</CFIF>
