<!--- Encryption playground --->
<cfset pageTitle = "Encryption Playground">
<cfparam name="Form.plain" default="Meet me at the Y2K party">
<cfparam name="Form.key" default="secret">
<cfset enc = Encrypt(Form.plain, Form.key)>
<cfinclude template="_top.cfm">
<cfform action="crypto.cfm" method="POST" name="crypt">
<TABLE BORDER=0 CELLPADDING=4>
<TR><TD>Text:</TD><TD><cfinput type="text" name="plain" value="#Form.plain#" size="40"></TD></TR>
<TR><TD>Key:</TD><TD><cfinput type="text" name="key" value="#Form.key#" size="20" required="yes" message="Enter a key"></TD></TR>
<TR><TD></TD><TD><INPUT TYPE="submit" VALUE="Encrypt!"></TD></TR>
</TABLE>
</cfform>
<cfoutput>
<TABLE BORDER=1 CELLPADDING=6 CELLSPACING=0 BGCOLOR="##FFFFEE">
<TR><TD><B>Encrypt(text, key)</B></TD><TD><PRE>#HTMLEditFormat(enc)#</PRE></TD></TR>
<TR><TD><B>Decrypt(that, key)</B></TD><TD>#HTMLEditFormat(Decrypt(enc, Form.key))#</TD></TR>
<TR><TD><B>Hash(text)</B> (MD5)</TD><TD><TT>#Hash(Form.plain)#</TT></TD></TR>
<TR><TD><B>ToBase64(text)</B></TD><TD><TT>#ToBase64(Form.plain)#</TT></TD></TR>
</TABLE>
<P><B>Fun fact:</B> this cipher only looks at characters 5 to 8 of the key. Watch:
<cfset k2 = Left(Form.key & "xxxxxxxx", 4) & "ZZZZ" & Mid(Form.key & "xxxxxxxx", 9, 100)>
encrypting with key <TT>"zzzz#Mid(Form.key & 'xxxxxxxx', 5, 4)#"</TT> gives the same output:
<B>#YesNoFormat(Encrypt(Form.plain, "zzzz" & Mid(Form.key & "xxxxxxxx", 5, 4)) EQ Encrypt(Form.plain, Left(Form.key & "xxxxxxxx", 8)))#</B>
(when the key is at least 8 characters). The KoldFusion Administrator stores your password with this very algorithm.
Sleep well!</P>
</cfoutput>
<cfinclude template="_bottom.cfm">
