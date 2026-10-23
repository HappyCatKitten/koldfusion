<!--- ch6app/index.cfm: the home page. Application.cfm makes sure
      only signed-in visitors get this far. --->
<CFQUERY NAME="GetDepts" DATASOURCE="#Request.DSN#">
SELECT Department, COUNT(*) AS Staff
FROM Employees
GROUP BY Department
ORDER BY Department
</CFQUERY>

<CFLOCK SCOPE="Session" TYPE="Exclusive" TIMEOUT="10">
  <CFPARAM NAME="Session.Views" DEFAULT="0">
  <CFSET Session.Views = Session.Views + 1>
  <CFSET Views = Session.Views>
</CFLOCK>

<CFINCLUDE TEMPLATE="../ch6_header.cfm">
<CFOUTPUT>
<P>Welcome, <B>#Request.UserName#</B>! This is visit number #Views#
to the home page in this session.</P>
</CFOUTPUT>

<TABLE BORDER="1" CELLPADDING="3" CELLSPACING="0">
<TR BGCOLOR="#CCCCFF"><TH>Department</TH><TH>Staff</TH></TR>
<CFOUTPUT QUERY="GetDepts">
<TR><TD>#Department#</TD><TD ALIGN="RIGHT">#Staff#</TD></TR>
</CFOUTPUT>
</TABLE>

<P><A HREF="index.cfm">Reload</A> | <A HREF="logout.cfm">Sign out</A></P>
<CFINCLUDE TEMPLATE="../ch6_footer.cfm">
