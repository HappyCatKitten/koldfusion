<!--- ch8_mail.cfm: a feedback form that e-mails the webmaster.
      Mail goes only to the local machine. --->
<CFIF IsDefined("Form.Message") AND Trim(Form.Message) IS NOT "">
  <CFPARAM NAME="Form.Topic" DEFAULT="General">
  <CFMAIL TO="webmaster@localhost"
          FROM="devguide@localhost"
          SUBJECT="Feedback: #Form.Topic#">
A visitor sent feedback from #CGI.REMOTE_ADDR# on #DateFormat(Now(), "mm/dd/yyyy")#.

Topic: #Form.Topic#

#Form.Message#
</CFMAIL>
  <P>Thank you! Your message is on its way to the webmaster
  (well, to the webmaster account on this machine).</P>
  <P><A HREF="ch8_mail.cfm">Send another</A></P>
<CFELSE>
  <H3>Send us your feedback</H3>
  <FORM ACTION="ch8_mail.cfm" METHOD="POST">
  Topic:
  <SELECT NAME="Topic">
    <OPTION>General
    <OPTION>Praise
    <OPTION>Bug Report
    <OPTION>Y2K Question
  </SELECT><BR>
  <TEXTAREA NAME="Message" ROWS="5" COLS="50" WRAP="virtual"></TEXTAREA><BR>
  <INPUT TYPE="submit" VALUE="Send feedback">
  </FORM>
</CFIF>
