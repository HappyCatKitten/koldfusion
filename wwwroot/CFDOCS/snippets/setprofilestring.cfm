<CFSET IniFile = GetTempDirectory() & "snippet_" & CreateUUID() & ".ini">
<CFSET SetProfileString(IniFile, "Dialer", "Modem", "US Robotics Sportster")>
<CFSET SetProfileString(IniFile, "Dialer", "Speed", "28800")>
<CFSET SetProfileString(IniFile, "Browser", "Name", "Netscape Navigator 4.7")>
<!--- upgrade day: replace an existing entry --->
<CFSET SetProfileString(IniFile, "Dialer", "Speed", "56000")>
<CFFILE ACTION="READ" FILE="#IniFile#" VARIABLE="Contents">
<CFFILE ACTION="DELETE" FILE="#IniFile#">
<P>The file now contains:</P>
<CFOUTPUT><PRE>#HTMLEditFormat(Contents)#</PRE></CFOUTPUT>
