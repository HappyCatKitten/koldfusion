<CFSET App = StructNew()>
<CFSET App.Settings = StructNew()>
<CFSET App.Settings.Theme = "Classic">
<CFSET App.Users = QueryNew("Name")>
<CFSET Temp = QueryAddRow(App.Users)>
<CFSET Temp = QuerySetCell(App.Users, "Name", "Ann")>

<CFSET Mine = Duplicate(App)>
<CFSET Mine.Settings.Theme = "Hot Dog Stand">
<CFSET Temp = QuerySetCell(Mine.Users, "Name", "Bob", 1)>

<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>&nbsp;</TH><TH>Settings.Theme</TH><TH>Users.Name</TH></TR>
<TR><TD>App (original)</TD><TD>#App.Settings.Theme#</TD><TD>#App.Users.Name#</TD></TR>
<TR><TD>Mine (Duplicate)</TD><TD>#Mine.Settings.Theme#</TD><TD>#Mine.Users.Name#</TD></TR>
</TABLE>
</CFOUTPUT>
