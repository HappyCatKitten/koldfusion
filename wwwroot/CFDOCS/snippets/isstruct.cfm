<CFSET Employee = StructNew()>
<CFSET Employee.Name = "Ada">
<CFSET Employee.Dept = "Engineering">
<CFSET Roster = ArrayNew(1)>
<CFSET Roster[1] = Employee>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Expression</TH><TH>IsStruct</TH></TR>
<CFOUTPUT>
<TR><TD>Employee</TD><TD>#IsStruct(Employee)#</TD></TR>
<TR><TD>Employee.Name</TD><TD>#IsStruct(Employee.Name)#</TD></TR>
<TR><TD>Roster</TD><TD>#IsStruct(Roster)#</TD></TR>
<TR><TD>Roster[1]</TD><TD>#IsStruct(Roster[1])#</TD></TR>
</CFOUTPUT>
</TABLE>
