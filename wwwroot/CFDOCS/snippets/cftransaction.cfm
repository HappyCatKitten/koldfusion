<!--- Add a comment, look at it, take it back out again --->
<CFQUERY NAME="Before" DATASOURCE="cfsnippets">
SELECT COUNT(*) AS Total FROM Comments
</CFQUERY>

<CFTRANSACTION>
  <CFQUERY DATASOURCE="cfsnippets">
  INSERT INTO Comments (Email, FromUser, Subject, CommtType, MessText, Processed)
  VALUES ('ann@localhost', 'Ann Example', 'Transaction test', 'Question', 'Testing 1, 2, 3', 0)
  </CFQUERY>
  <CFQUERY NAME="During" DATASOURCE="cfsnippets">
  SELECT COUNT(*) AS Total, MAX(CommentID) AS LastID FROM Comments
  </CFQUERY>
  <CFQUERY DATASOURCE="cfsnippets">
  DELETE FROM Comments WHERE CommentID = #During.LastID#
  </CFQUERY>
</CFTRANSACTION>

<CFQUERY NAME="After" DATASOURCE="cfsnippets">
SELECT COUNT(*) AS Total FROM Comments
</CFQUERY>

<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Moment</TH><TH>Rows in Comments</TH></TR>
<TR><TD>Before the transaction</TD><TD>#Before.Total#</TD></TR>
<TR><TD>After the INSERT (new ID #During.LastID#)</TD><TD>#During.Total#</TD></TR>
<TR><TD>After the DELETE</TD><TD>#After.Total#</TD></TR>
</TABLE>
</CFOUTPUT>
