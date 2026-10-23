<!--- sn_errorpage.cfm: Exception error handler for the CFERROR example --->
<HTML><HEAD><TITLE>We are sorry</TITLE></HEAD>
<BODY BGCOLOR="#FFFFFF">
<CFOUTPUT>
<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 WIDTH="100%">
<TR><TD BGCOLOR="##FFE0E0"><IMG SRC="/CFIDE/administrator/images/warn.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>
<FONT FACE="Arial, Helvetica" SIZE="3"><B>Our server tripped over its modem cable.</B></FONT></TD></TR>
</TABLE>
<P>This friendly page comes from <B>sn_errorpage.cfm</B>, registered with CFERROR TYPE="Exception".</P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TD>Error.Type</TD><TD>#Error.Type#</TD></TR>
<TR><TD>Error.Message</TD><TD>#Error.Message#</TD></TR>
<TR><TD>Error.Detail</TD><TD>#Error.Detail#</TD></TR>
<TR><TD>Error.DateTime</TD><TD>#Error.DateTime#</TD></TR>
<TR><TD>Error.Template</TD><TD>#GetFileFromPath(Error.Template)#</TD></TR>
<TR><TD>Error.QueryString</TD><TD>#HTMLEditFormat(Error.QueryString)#</TD></TR>
<TR><TD>Error.RemoteAddress</TD><TD>#Error.RemoteAddress#</TD></TR>
</TABLE>
<P>Please tell <A HREF="mailto:#Error.MailTo#">#Error.MailTo#</A> what you were doing.
<A HREF="cferror.cfm">Back to the example</A></P>
</CFOUTPUT>
</BODY></HTML>
