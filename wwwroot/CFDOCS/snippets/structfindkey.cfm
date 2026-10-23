<CFSET Company = StructNew()>
<CFSET Company.Name = "Gibson Mainframe Co.">
<CFSET Company.Staff = ArrayNew(1)>
<CFSET Company.Staff[1] = StructNew()>
<CFSET Company.Staff[1].Name = "Carol Reardon">
<CFSET Company.Staff[2] = StructNew()>
<CFSET Company.Staff[2].Name = "Jack Lindqvist">
<CFSET Found = StructFindKey(Company, "Name", "all")>
<CFOUTPUT>
<P>#ArrayLen(Found)# keys called Name:</P>
<UL>
<CFLOOP FROM="1" TO="#ArrayLen(Found)#" INDEX="i">
  <LI>#Found[i].Path# = #Found[i].Value#
</CFLOOP>
</UL>
</CFOUTPUT>
