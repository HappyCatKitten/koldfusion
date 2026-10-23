<!--- Registered Applets --->
<cfregistry action="getall" branch="#Request.reg#\Applets" name="apps" type="key" sort="Entry ASC">
<cfset pageTitle = "Registered Applets">
<cfinclude template="../_header.cfm">
<cfoutput>
<FORM ACTION="appletedit.cfm" METHOD="POST">
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966"><cfloop list="Applet,Code,Codebase,Method" index="h"><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>#h#</B></FONT></TD></cfloop></TR>
<TR BGCOLOR="##FFFFFF"><TD COLSPAN=4><INPUT TYPE="text" NAME="AppletName" SIZE=20> <INPUT TYPE="submit" VALUE="Register New Applet..."></TD></TR>
<cfloop query="apps">
	<cfmodule template="../_tags/getreg.cfm" key="Applets\#apps.Entry#" variable="A">
	<TR BGCOLOR="#IIf(apps.CurrentRow MOD 2, DE('FFFBF0'), DE('FFFFFF'))#">
	<TD>#Request.f#<B><A HREF="appletedit.cfm?AppletName=#URLEncodedFormat(apps.Entry)#">#apps.Entry#</A></B></FONT></TD>
	<TD>#Request.f##A.Code#</FONT></TD><TD>#Request.f##A.Codebase#</FONT></TD><TD>#Request.f##A.Method#</FONT></TD></TR>
</cfloop>
</TABLE>
</FORM>
<P>#Request.f#<I>Registered applets can be embedded with &lt;CFAPPLET APPLETSOURCE="name" NAME="..."&gt; inside a CFFORM.
Modern browsers no longer run Java applets; the NOTSUPPORTED message will be shown instead.</I></FONT>
</cfoutput>
<cfinclude template="../_footer.cfm">
