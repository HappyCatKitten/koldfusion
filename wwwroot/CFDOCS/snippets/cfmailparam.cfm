<CFMAIL TO="someone@localhost"
        FROM="support@localhost"
        SUBJECT="Your Y2K readiness report">
<CFMAILPARAM NAME="Reply-To" VALUE="helpdesk@localhost">
<CFMAILPARAM NAME="X-Priority" VALUE="1">
<CFMAILPARAM NAME="Organization" VALUE="Gibson Mainframe Co.">
Good news: all 25 workstations passed the December 31, 1999 rollover test.
</CFMAIL>

<P>Message spooled with these extra headers:</P>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Header</TH><TH>Value</TH></TR>
<TR><TD>Reply-To</TD><TD>helpdesk@localhost</TD></TR>
<TR><TD>X-Priority</TD><TD>1 (urgent)</TD></TR>
<TR><TD>Organization</TD><TD>Gibson Mainframe Co.</TD></TR>
</TABLE>
