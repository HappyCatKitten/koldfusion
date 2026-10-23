<!--- the 1999 Java applet controls, rendered in HTML --->
<cfset pageTitle = "Applet Controls">
<cfquery name="emps" datasource="cfsnippets" maxrows="8">SELECT Emp_ID, FirstName, LastName, Department FROM Employees ORDER BY Department, LastName</cfquery>
<cfinclude template="_top.cfm">
<P>In ColdFusion 4.5 these were Java applets that took a minute to load and occasionally crashed Netscape. Here they
are as plain HTML. Same tags, same attributes.</P>
<cfform action="widgets.cfm" method="POST" name="w">
<TABLE BORDER=0 CELLPADDING=8><TR VALIGN=TOP><TD>
<B>CFGRID</B><BR>
<cfgrid name="empgrid" query="emps" selectmode="browse" width="380" font="Arial">
	<cfgridcolumn name="FirstName" header="First">
	<cfgridcolumn name="LastName" header="Last">
	<cfgridcolumn name="Department" header="Department">
</cfgrid>
</TD><TD>
<B>CFTREE</B><BR>
<cftree name="org" width="220">
	<cftreeitem value="Department,LastName" display="Department,LastName" query="emps" queryasroot="no">
</cftree>
<BR><B>CFSLIDER</B><BR>
<cfslider name="volume" range="0,11" value="11" label="Volume:" scale="1"><BR>
<B>CFTEXTINPUT</B><BR>
<cftextinput name="note" value="Hello from 1999" font="Courier New" bgcolor="##FFFFCC" bold="yes">
</TD></TR></TABLE>
<INPUT TYPE="submit" VALUE="Submit">
</cfform>
<cfif IsDefined("Form.volume")><cfoutput><P>You submitted volume <B>#Form.volume#</B><cfif Form.volume EQ 11> (one louder)</cfif>,
note <B>#HTMLEditFormat(Form.note)#</B>, tree node <B>#HTMLEditFormat(Form["org.node"])#</B>.</P></cfoutput></cfif>
<cfinclude template="_bottom.cfm">
