<!--- Verity Collections --->
<cfset msg = "">
<cfif IsDefined("Form.CollectionAction") AND IsDefined("Form.Collection")>
	<cfif Form.CollectionAction EQ "Index..."><cflocation url="verityindex.cfm?collection=#URLEncodedFormat(Form.Collection)#" addtoken="no"></cfif>
	<cfset r = KFUSION_VERITY(Form.CollectionAction, Form.Collection)>
	<cfset msg = r.Message>
</cfif>
<cfif IsDefined("Form.Create") AND Len(Trim(Form.Name))>
	<cfif Form.CreateMode EQ "map">
		<cfcollection action="map" collection="#Trim(Form.Name)#" path="#Trim(Form.Path)#" language="#Form.Language#">
		<cfset msg = "The collection #Trim(Form.Name)# has been mapped.">
	<cfelse>
		<cfset r = KFUSION_VERITY("create", Trim(Form.Name), Trim(Form.Path), Form.Language)>
		<cfset msg = r.Message>
	</cfif>
</cfif>
<cfif IsDefined("Form.K2Apply")>
	<cfif IsNumeric(Form.DocCountLimit) AND Form.DocCountLimit GTE 0 AND IsNumeric(Form.K2Port)>
		<cfmodule template="../_tags/setreg.cfm" key="Verity\K2Server" entry="DocCountLimit" value="#Int(Form.DocCountLimit)#">
		<cfmodule template="../_tags/setreg.cfm" key="Verity\K2Server" entry="Port" value="#Int(Form.K2Port)#">
		<cfmodule template="../_tags/setreg.cfm" key="Verity\K2Server" entry="Online" value="#IIf(IsDefined('Form.K2Online'), 1, 0)#">
		<cfset msg = "The Verity K2 Server settings have been applied.">
	<cfelse>
		<cfset msg = "The document count limit and the port must be numeric.">
	</cfif>
</cfif>
<cfset colls = KFUSION_VERITYLIST()>
<cfmodule template="../_tags/getreg.cfm" key="Verity\K2Server" variable="K2">
<cfparam name="K2.Port" default="9901">
<cfset info = KFUSION_SERVERINFO()>
<cfset pageTitle = "Verity Collections">
<cfinclude template="../_header.cfm">
<cfmodule template="../_tags/status.cfm" message="#msg#">
<cfoutput>
<FORM ACTION="verity.cfm" METHOD="POST">
<SELECT NAME="Collection" SIZE=6 STYLE="width:520px;font-family:Courier New,monospace">
<cfloop query="colls"><OPTION VALUE="#colls.Name#"<cfif colls.CurrentRow EQ 1> SELECTED</cfif>>#colls.Name# (#colls.Path#/#colls.Name#) - #colls.Documents# docs</cfloop>
</SELECT><BR>
<cfloop list="Index...,Repair,Optimize,Purge,Delete" index="a"><INPUT TYPE="submit" NAME="CollectionAction" VALUE="#a#"<cfif a EQ "Delete"> onClick="return confirm('Delete the selected collection?')"</cfif>> </cfloop>
</FORM>
<P><TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>Add a Collection</B></FONT></TD></TR></TABLE>
<FORM ACTION="verity.cfm" METHOD="POST">
<P>#Request.f#Enter a unique name for the new collection and specify a server path for the data.</FONT>
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD>#Request.f#<B>Name</B></FONT></TD><TD><INPUT TYPE="text" NAME="Name" SIZE=20></TD></TR>
<TR><TD>#Request.f#<B>Path</B></FONT></TD><TD><INPUT TYPE="text" NAME="Path" VALUE="#info.Root#/verity/collections" SIZE=45 STYLE="font-family:Courier New,monospace">
	<INPUT TYPE="button" VALUE="Browse Server..." onClick="browseServer('Path')"></TD></TR>
<TR><TD>#Request.f#<B>Language</B></FONT></TD><TD><SELECT NAME="Language"><OPTION SELECTED>English<OPTION>French<OPTION>German<OPTION>Spanish<OPTION>Italian</SELECT></TD></TR>
<TR><TD></TD><TD>#Request.f#<INPUT TYPE="radio" NAME="CreateMode" VALUE="create" CHECKED> <B>Create</B> a new collection. &nbsp;
	<INPUT TYPE="radio" NAME="CreateMode" VALUE="map"> <B>Map</B> an existing collection.</FONT></TD></TR>
</TABLE>
<INPUT TYPE="submit" NAME="Create" VALUE="Create">
</FORM>
<P><TABLE WIDTH="100%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD BGCOLOR="##669966"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="##FFFFFF"><B>Verity K2 Server</B></FONT></TD></TR></TABLE>
<FORM ACTION="verity.cfm" METHOD="POST">
<P>#Request.f#The KoldFusion search engine also answers as a Verity K2 Server, serving every collection listed above.
Pages can query it with GetK2ServerCollections(), GetK2ServerDocCount() and the other K2 Server functions.</FONT>
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD>#Request.f#<B>Status</B></FONT></TD><TD>#Request.f#<cfif IsK2ServerOnline()><FONT COLOR="##006600"><B>Online</B></FONT><cfelse><FONT COLOR="##CC0000"><B>Offline</B></FONT></cfif>
	&nbsp; (#IIf(IsK2ServerABroker(), DE("broker"), DE("stand-alone server, not a broker"))#)</FONT></TD></TR>
<TR><TD>#Request.f#<B>Collections served</B></FONT></TD><TD>#Request.f##ListLen(GetK2ServerCollections())#</FONT></TD></TR>
<TR><TD>#Request.f#<B>Documents indexed</B></FONT></TD><TD>#Request.f##NumberFormat(GetK2ServerDocCount())#
	<cfif IsK2ServerDocCountExceeded()><FONT COLOR="##CC0000"><B>- the document limit has been exceeded</B></FONT></cfif></FONT></TD></TR>
<TR><TD>#Request.f#<B>Document count limit</B></FONT></TD><TD><INPUT TYPE="text" NAME="DocCountLimit" VALUE="#GetK2ServerDocCountLimit()#" SIZE=10></TD></TR>
<TR><TD>#Request.f#<B>K2 Server port</B></FONT></TD><TD><INPUT TYPE="text" NAME="K2Port" VALUE="#K2.Port#" SIZE=6></TD></TR>
<TR><TD></TD><TD>#Request.f#<INPUT TYPE="checkbox" NAME="K2Online"<cfif IsK2ServerOnline()> CHECKED</cfif>> Run the K2 Server</FONT></TD></TR>
</TABLE>
<INPUT TYPE="submit" NAME="K2Apply" VALUE="Apply">
</FORM>
</cfoutput>
<cfinclude template="../_footer.cfm">
