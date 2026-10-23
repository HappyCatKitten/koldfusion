<CFSET OldLocale = SetLocale("German (Standard)")>
<CFSET NewLocale = GetLocale()>
<CFSET Dummy = SetLocale(OldLocale)>
<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Step</TH><TH>Locale</TH></TR>
<TR><TD>Before SetLocale</TD><TD>#OldLocale#</TD></TR>
<TR><TD>After SetLocale("German (Standard)")</TD><TD>#NewLocale#</TD></TR>
<TR><TD>After restoring the old locale</TD><TD>#GetLocale()#</TD></TR>
</TABLE>
</CFOUTPUT>
