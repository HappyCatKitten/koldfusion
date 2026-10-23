<!--- write a small .ini file in the temp directory, read it back, clean up --->
<CFSET IniFile = GetTempDirectory() & "snippet_" & CreateUUID() & ".ini">
<CFFILE ACTION="WRITE" FILE="#IniFile#" OUTPUT="[Dialer]
Modem=US Robotics Sportster
Speed=56000
[Browser]
Name=Netscape Navigator 4.7">
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Section</TH><TH>Entry</TH><TH>GetProfileString</TH></TR>
<TR><TD>Dialer</TD><TD>Modem</TD><TD>#GetProfileString(IniFile, "Dialer", "Modem")#</TD></TR>
<TR><TD>Dialer</TD><TD>Speed</TD><TD>#GetProfileString(IniFile, "Dialer", "Speed")#</TD></TR>
<TR><TD>browser</TD><TD>name</TD><TD>#GetProfileString(IniFile, "browser", "name")#</TD></TR>
<TR><TD>Browser</TD><TD>Plugins</TD><TD>"#GetProfileString(IniFile, "Browser", "Plugins")#"</TD></TR>
</TABLE>
</CFOUTPUT>
<CFFILE ACTION="DELETE" FILE="#IniFile#">
