<!---
	/CFDOCS/snippets/sn_sysorder.cfm
	Helper custom tag for the GetBaseTagData and GetBaseTagList examples.
	<CF_SN_SYSORDER CUSTOMER="name"> ... <CF_SN_SYSITEM> tags ... </CF_SN_SYSORDER>
--->
<CFPARAM NAME="Attributes.Customer" DEFAULT="(walk-in customer)">
<CFIF ThisTag.ExecutionMode IS "start">
	<!--- the child tags add to this counter through GetBaseTagData() --->
	<CFSET ThisTag.ItemCount = 0>
	<CFOUTPUT><P><B>Order for #Attributes.Customer#</B></P></CFOUTPUT>
	<TABLE BORDER=1 CELLPADDING=3>
	<TR><TH>Qty</TH><TH>Product</TH><TH>Ordered by</TH><TH>GetBaseTagList()</TH></TR>
<CFELSE>
	</TABLE>
	<CFOUTPUT><P>#ThisTag.ItemCount# items in this order.</P></CFOUTPUT>
</CFIF>
