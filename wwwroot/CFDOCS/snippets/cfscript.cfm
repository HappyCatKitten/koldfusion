<CFQUERY NAME="Staff" DATASOURCE="cfsnippets">
SELECT Department, Salary FROM Employees
</CFQUERY>

<CFSCRIPT>
// total the payroll per department in a structure
Payroll = StructNew();
depts = "";
for (row = 1; row LTE Staff.RecordCount; row = row + 1) {
    dept = Staff.Department[row];
    if (NOT StructKeyExists(Payroll, dept)) {
        Payroll[dept] = 0;
        depts = ListAppend(depts, dept);
    }
    Payroll[dept] = Payroll[dept] + Staff.Salary[row];
}

/* and print it as a table */
WriteOutput("<TABLE BORDER=1 CELLPADDING=3><TR><TH>Department</TH><TH>Payroll</TH><TH>Size</TH></TR>");
depts = ListSort(depts, "textnocase");
for (i = 1; i LTE ListLen(depts); i = i + 1) {
    dept = ListGetAt(depts, i);
    switch (dept) {
        case "Engineering": size = "Large"; break;
        case "Administration": case "Training": size = "Small"; break;
        default: size = "Medium";
    }
    WriteOutput("<TR><TD>" & dept & "</TD><TD ALIGN=RIGHT>" & DollarFormat(Payroll[dept]) & "</TD><TD>" & size & "</TD></TR>");
}
WriteOutput("</TABLE>");
</CFSCRIPT>
