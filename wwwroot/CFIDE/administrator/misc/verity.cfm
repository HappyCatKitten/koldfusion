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
<cfset colls = KFUSION_VERITYLIST()>
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
</cfoutput>
<cfinclude template="../_footer.cfm">
