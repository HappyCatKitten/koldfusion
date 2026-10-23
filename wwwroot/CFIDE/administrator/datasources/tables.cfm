<!--- View the tables in a data source (a KoldFusion extra) --->
<cfparam name="URL.DSN" default="">
<cfparam name="URL.table" default="">
<cfparam name="URL.proc" default="">
<cfif NOT Len(URL.DSN)><cflocation url="odbc.cfm" addtoken="no"></cfif>
<cfset tbls = KFUSION_DBTABLES(URL.DSN)>
<cfset procs = KFUSION_DBPROCS(URL.DSN)>
<cfset pageTitle = "Tables in #URL.DSN#">
<cfinclude template="../_header.cfm">
<cfoutput>
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966"><cfloop list="Table,Columns,Rows" index="h"><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>#h#</B></FONT></TD></cfloop></TR>
<cfloop query="tbls">
<TR BGCOLOR="#IIf(tbls.CurrentRow MOD 2, DE('FFFBF0'), DE('FFFFFF'))#">
<TD>#Request.f#<B><A HREF="tables.cfm?DSN=#URLEncodedFormat(URL.DSN)#&table=#URLEncodedFormat(tbls.TABLE_NAME)#">#tbls.TABLE_NAME#</A></B></FONT></TD>
<TD>#Request.f##tbls.COLUMN_COUNT#</FONT></TD><TD>#Request.f##tbls.ROW_COUNT#</FONT></TD></TR>
</cfloop>
</TABLE>
<cfif procs.RecordCount>
<P><TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="##669966"><cfloop list="Stored Procedure,Parameters" index="h"><TD><FONT FACE="Arial" SIZE=2 COLOR="##FFFFFF"><B>#h#</B></FONT></TD></cfloop></TR>
<cfloop query="procs">
<TR BGCOLOR="#IIf(procs.CurrentRow MOD 2, DE('FFFBF0'), DE('FFFFFF'))#">
<TD>#Request.f#<B><A HREF="tables.cfm?DSN=#URLEncodedFormat(URL.DSN)#&proc=#URLEncodedFormat(procs.PROCEDURE_NAME)#">#procs.PROCEDURE_NAME#</A></B></FONT></TD>
<TD><FONT FACE="Courier New" SIZE=2>#HTMLEditFormat(procs.PARAMETERS)#</FONT></TD></TR>
</cfloop>
</TABLE>
</cfif>
<cfif Len(URL.proc)>
	<cfloop query="procs"><cfif procs.PROCEDURE_NAME EQ URL.proc>
	<P>#Request.f#<B>#procs.PROCEDURE_NAME#</B></FONT>
	<TABLE BORDER=1 CELLPADDING=4 CELLSPACING=0><TR><TD BGCOLOR="##FFFBF0"><PRE>#HTMLEditFormat(procs.SOURCE)#</PRE></TD></TR></TABLE>
	</cfif></cfloop>
</cfif>
<cfif Len(URL.table)>
	<cfset cols = KFUSION_DBDESCRIBE(URL.DSN, URL.table)>
	<P>#Request.f#<B>#URL.table#</B></FONT>
	<TABLE BORDER=1 CELLPADDING=3 CELLSPACING=0>
	<TR BGCOLOR="##C0C0C0"><TH>#Request.f#Column</FONT></TH><TH>#Request.f#Type</FONT></TH><TH>#Request.f#Key</FONT></TH></TR>
	<cfloop query="cols"><TR><TD>#Request.f##cols.COLUMN_NAME#</FONT></TD><TD>#Request.f##cols.TYPE_NAME#</FONT></TD><TD>#Request.f##IIf(cols.IS_PRIMARY_KEY, DE("PK"), DE(""))#</FONT></TD></TR></cfloop>
	</TABLE>
	<cfquery name="peek" datasource="#URL.DSN#" maxrows="10">SELECT * FROM #URL.table#</cfquery>
	<P>#Request.f#First rows:</FONT>
	<TABLE BORDER=1 CELLPADDING=2 CELLSPACING=0>
	<TR BGCOLOR="##C0C0C0"><cfloop list="#peek.ColumnList#" index="col"><TH><FONT FACE="Arial" SIZE=1>#col#</FONT></TH></cfloop></TR>
	<cfloop query="peek"><TR><cfloop list="#peek.ColumnList#" index="col"><TD><FONT FACE="Arial" SIZE=1>#HTMLEditFormat(Left(peek[col][peek.CurrentRow], 40))#</FONT></TD></cfloop></TR></cfloop>
	</TABLE>
</cfif>
<FORM><INPUT TYPE="button" VALUE="Back" onClick="location='dsnedit.cfm?DSN=#URLEncodedFormat(URL.DSN)#'"></FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
