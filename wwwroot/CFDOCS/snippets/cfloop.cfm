<CFOUTPUT>
<P><B>Index loop</B> (FROM 10 TO 1 STEP -3):
<CFLOOP INDEX="i" FROM="10" TO="1" STEP="-3"> #i#</CFLOOP></P>

<P><B>Conditional loop</B> (double it until it passes 1000):
<CFSET n = 1>
<CFLOOP CONDITION="n LT 1000"><CFSET n = n * 2> #n#</CFLOOP></P>

<P><B>List loop</B> (delimiters ";" and "|"):
<CFLOOP INDEX="Browser" LIST="Netscape 4.7;Internet Explorer 5|Opera 3.6;Lynx" DELIMITERS=";|">
  [#Browser#]</CFLOOP></P>

<P><B>Collection loop</B>:
<CFSET Modem = StructNew()>
<CFSET Modem.Speed = "56K">
<CFSET Modem.Standard = "V.90">
<CFSET Modem.Port = "COM2">
<CFLOOP COLLECTION="#Modem#" ITEM="Key"> #Key#=#Modem[Key]#</CFLOOP></P>
</CFOUTPUT>

<P><B>Query loop</B> (rows 2 to 4 of Departments):</P>
<CFQUERY NAME="Depts" DATASOURCE="cfsnippets">
SELECT Dept_Name, Location FROM Departments ORDER BY Dept_ID
</CFQUERY>
<TABLE BORDER=1 CELLPADDING=3>
<CFLOOP QUERY="Depts" STARTROW="2" ENDROW="4">
  <CFOUTPUT><TR><TD>#Depts.CurrentRow#</TD><TD>#Dept_Name#</TD><TD>#Location#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
