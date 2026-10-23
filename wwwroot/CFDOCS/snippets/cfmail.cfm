<!--- One message per Training employee, all addressed to a harmless local mailbox --->
<CFQUERY NAME="Trainers" DATASOURCE="cfsnippets">
SELECT FirstName, LastName, Email FROM Employees
WHERE Department = 'Training' ORDER BY LastName
</CFQUERY>

<CFMAIL QUERY="Trainers"
        TO="someone@localhost"
        FROM="webmaster@localhost"
        SUBJECT="Course schedule for #FirstName# #LastName#">
Hello #FirstName#,

The spring course schedule is now on the intranet.
(In real life this message would go to #Email#.)

-- The KoldFusion mail robot
</CFMAIL>

<CFOUTPUT><P>Spooled #Trainers.RecordCount# messages:</P></CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>To</TH><TH>Subject</TH></TR>
<CFOUTPUT QUERY="Trainers">
<TR><TD>someone@localhost</TD><TD>Course schedule for #FirstName# #LastName#</TD></TR>
</CFOUTPUT>
</TABLE>
