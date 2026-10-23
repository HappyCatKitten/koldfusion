<!--- 
	showvalue.cfm - custom tag used by the Expression Evaluator to display any value
	(simple values, arrays, structures, queries), nesting up to a few levels.
	Usage: <CFMODULE TEMPLATE="showvalue.cfm" VALUE="#x#" DEPTH="1">
	(No CFDUMP in 4.5, so we do it the long way.)
--->
<cfif NOT IsDefined("ThisTag.ExecutionMode") OR ThisTag.ExecutionMode NEQ "start"><cfexit method="exittag"></cfif>
<cfparam name="Attributes.Depth" default="1">
<cfset v = Attributes.Value>
<cfset maxDepth = 4>
<cfif IsQuery(v)>
	<cfoutput>
	<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=1 BGCOLOR="##993399">
	<TR BGCOLOR="##CC99CC"><TH COLSPAN="#ListLen(v.ColumnList) + 1#" ALIGN=LEFT><FONT SIZE=1>query &middot; #v.RecordCount# row<cfif v.RecordCount NEQ 1>s</cfif></FONT></TH></TR>
	<TR BGCOLOR="##EEDDEE"><TD></TD><cfloop list="#v.ColumnList#" index="col"><TD><FONT SIZE=1><B>#col#</B></FONT></TD></cfloop></TR>
	<cfloop index="r" from="1" to="#Min(v.RecordCount, 50)#">
		<TR BGCOLOR="##FFFFFF"><TD><FONT SIZE=1>#r#</FONT></TD>
		<cfloop list="#v.ColumnList#" index="col"><TD><FONT SIZE=1>#HTMLEditFormat(v[col][r])#</FONT></TD></cfloop>
		</TR>
	</cfloop>
	<cfif v.RecordCount GT 50><TR BGCOLOR="##FFFFFF"><TD COLSPAN="#ListLen(v.ColumnList) + 1#"><FONT SIZE=1>... #v.RecordCount - 50# more rows</FONT></TD></TR></cfif>
	</TABLE>
	</cfoutput>
<cfelseif IsStruct(v)>
	<cfoutput>
	<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=1 BGCOLOR="##3366CC">
	<TR BGCOLOR="##99BBEE"><TH COLSPAN=2 ALIGN=LEFT><FONT SIZE=1>struct &middot; #StructCount(v)# key<cfif StructCount(v) NEQ 1>s</cfif></FONT></TH></TR>
	<cfloop list="#ListSort(StructKeyList(v), 'textnocase')#" index="k">
		<TR BGCOLOR="##FFFFFF" VALIGN=TOP><TD BGCOLOR="##DDE6F6"><FONT SIZE=1><B>#k#</B></FONT></TD><TD><FONT SIZE=1>
		<cfif Attributes.Depth LT maxDepth><cfmodule template="showvalue.cfm" value="#v[k]#" depth="#Attributes.Depth + 1#"><cfelse>...</cfif>
		</FONT></TD></TR>
	</cfloop>
	</TABLE>
	</cfoutput>
<cfelseif IsArray(v)>
	<cfoutput>
	<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=1 BGCOLOR="##339933">
	<TR BGCOLOR="##99CC99"><TH COLSPAN=2 ALIGN=LEFT><FONT SIZE=1>array &middot; #ArrayLen(v)# element<cfif ArrayLen(v) NEQ 1>s</cfif></FONT></TH></TR>
	<cfloop index="i" from="1" to="#Min(ArrayLen(v), 100)#">
		<TR BGCOLOR="##FFFFFF" VALIGN=TOP><TD BGCOLOR="##DDEEDD"><FONT SIZE=1><B>#i#</B></FONT></TD><TD><FONT SIZE=1>
		<cfif Attributes.Depth LT maxDepth><cfmodule template="showvalue.cfm" value="#v[i]#" depth="#Attributes.Depth + 1#"><cfelse>...</cfif>
		</FONT></TD></TR>
	</cfloop>
	</TABLE>
	</cfoutput>
<cfelseif IsBinary(v)>
	<cfoutput><I>binary, #Len(ToBase64(v))# Base64 characters:</I> #HTMLEditFormat(Left(ToBase64(v), 60))#<cfif Len(ToBase64(v)) GT 60>...</cfif></cfoutput>
<cfelseif IsSimpleValue(v)>
	<cfoutput><CODE>#HTMLEditFormat(v)#</CODE></cfoutput>
<cfelse>
	<I>(an object that cannot be displayed)</I>
</cfif>
