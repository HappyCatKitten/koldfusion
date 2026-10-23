<CFSET Orig = StructNew()>
<CFSET Orig.Name = "Ann">
<CFSET Orig.Address = StructNew()>
<CFSET Orig.Address.City = "Boston">

<CFSET Alias = Orig>
<CFSET Shallow = StructCopy(Orig)>
<CFSET Deep = Duplicate(Orig)>

<CFSET Shallow.Name = "Bob">
<CFSET Shallow.Address.City = "Cambridge">
<CFSET Deep.Address.City = "Denver">

<CFOUTPUT>
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>&nbsp;</TH><TH>Name</TH><TH>Address.City</TH></TR>
<TR><TD>Orig</TD><TD>#Orig.Name#</TD><TD>#Orig.Address.City#</TD></TR>
<TR><TD>Alias (same structure)</TD><TD>#Alias.Name#</TD><TD>#Alias.Address.City#</TD></TR>
<TR><TD>Shallow (StructCopy)</TD><TD>#Shallow.Name#</TD><TD>#Shallow.Address.City#</TD></TR>
<TR><TD>Deep (Duplicate)</TD><TD>#Deep.Name#</TD><TD>#Deep.Address.City#</TD></TR>
</TABLE>
<P>Changing Shallow.Name left Orig.Name alone, but changing Shallow.Address.City
also changed Orig's city: the nested structure is shared. Deep is fully independent.</P>
</CFOUTPUT>
