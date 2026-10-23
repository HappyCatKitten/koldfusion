<CFSET Email = "fred.flintstone@bedrock.localhost">
<CFSET At = Find("@", Email)>
<CFOUTPUT>
<P>Address: #Email#</P>
<UL>
<LI>User part: #Mid(Email, 1, At - 1)#
<LI>Domain: #Mid(Email, At + 1, Len(Email) - At)#
<LI>Mid(Email, 6, 10): #Mid(Email, 6, 10)#
</UL>
</CFOUTPUT>
