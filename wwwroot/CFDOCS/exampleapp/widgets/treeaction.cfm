<!---
	widgets/treeaction.cfm - shows what the tree, slider and text input submitted.
--->
<HTML>
<HEAD><TITLE>What the Form Controls Sent</TITLE></HEAD>
<BODY BGCOLOR="#FFFFFF">
<FONT FACE="Arial, Helvetica" SIZE=4><B>What the form controls sent</B></FONT>
<P><FONT FACE="Arial, Helvetica" SIZE=2>
<CFIF IsDefined("Form.FieldNames")>
	<TABLE BORDER=1 CELLPADDING=4 CELLSPACING=0>
	<TR BGCOLOR="#CCCCCC"><TH><FONT FACE="Arial, Helvetica" SIZE=2>Form field</FONT></TH><TH><FONT FACE="Arial, Helvetica" SIZE=2>Value</FONT></TH></TR>
	<CFLOOP LIST="#Form.FieldNames#" INDEX="field">
		<CFOUTPUT><TR><TD><FONT FACE="Courier New, Courier" SIZE=2>Form.#field#</FONT></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>#HTMLEditFormat(Form[field])#&nbsp;</FONT></TD></TR></CFOUTPUT>
	</CFLOOP>
	</TABLE>
	<!--- the tree submits a field named "ParkTree.node" (the path of the clicked item) --->
	<CFIF StructKeyExists(Form, "ParkTree.node") AND Len(Form["ParkTree.node"])>
		<CFSET ParkPath = Form["ParkTree.node"]>
		<CFOUTPUT><P>You picked <B>#ListLast(ParkPath, "/")#</B>, in the <B>#ListGetAt(ParkPath, 1, "/")#</B> region.</P></CFOUTPUT>
	</CFIF>
<CFELSE>
	Nothing was submitted.
</CFIF>
</FONT>
<P><FONT FACE="Arial, Helvetica" SIZE=2><A HREF="index.cfm">Back to the demo</A></FONT>
</BODY>
</HTML>
