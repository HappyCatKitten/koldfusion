<!--- ch2_collections.cfm: lists, arrays and structures --->
<CFSET Depts = "Sales,Marketing,Engineering">
<CFSET Depts = ListAppend(Depts, "Training")>

<CFOUTPUT>
<P>The list "#Depts#" has #ListLen(Depts)# elements.
The second is #ListGetAt(Depts, 2)#, and Engineering is
number #ListFind(Depts, "Engineering")#.</P>
</CFOUTPUT>

<!--- An array of modem speeds --->
<CFSET Speeds = ArrayNew(1)>
<CFSET Speeds[1] = 14.4>
<CFSET Speeds[2] = 28.8>
<CFSET ArrayAppend(Speeds, 33.6)>
<CFSET ArrayAppend(Speeds, 56)>

<P>Modem speeds through the years:</P>
<UL>
<CFLOOP INDEX="i" FROM="1" TO="#ArrayLen(Speeds)#">
  <CFOUTPUT><LI>#Speeds[i]#K</CFOUTPUT>
</CFLOOP>
</UL>
<CFOUTPUT><P>Average: #NumberFormat(ArrayAvg(Speeds), "99.9")#K</P></CFOUTPUT>

<!--- A structure describing one employee --->
<CFSET Emp = StructNew()>
<CFSET Emp.Name = "Jack Lindqvist">
<CFSET Emp.Department = "Engineering">
<CFSET Emp["Phone"] = "617-555-0121">

<TABLE BORDER="1" CELLPADDING="3" CELLSPACING="0">
<CFLOOP COLLECTION="#Emp#" ITEM="Key">
  <CFOUTPUT><TR><TD><B>#Key#</B></TD><TD>#Emp[Key]#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<CFOUTPUT>
<P>The structure has #StructCount(Emp)# keys.
Is there a Fax key? #YesNoFormat(StructKeyExists(Emp, "Fax"))#</P>
</CFOUTPUT>
