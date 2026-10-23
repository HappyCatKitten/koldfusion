<!-- ch7_error.cfm: the error template used by ch7_errorpage.cfm.
     CFML tags are not run in a request error template, so even this
     comment is plain HTML. Opened on its own, the page simply shows
     the placeholders. -->
<HTML>
<HEAD><TITLE>We are sorry</TITLE></HEAD>
<BODY BGCOLOR="#FFFFFF">
<FONT FACE="Arial, Helvetica" SIZE="2">
<H2>Oops. Our server tripped over its own power cord.</H2>
<P>Something went wrong while building this page. It is not your fault.
Please try again in a few minutes, or write to
<A HREF="mailto:#Error.MailTo#">#Error.MailTo#</A>.</P>
<P><FONT SIZE="1">Time of the error: #Error.DateTime#<BR>
Page: #Error.Template#</FONT></P>
<!-- For the developer:
#Error.Diagnostics#
-->
</FONT>
</BODY>
</HTML>
