<!---
	/CFDOCS/snippets/sn_sysitem.cfm
	Helper custom tag for the GetBaseTagData and GetBaseTagList examples.
	Must be used inside <CF_SN_SYSORDER>.
--->
<CFPARAM NAME="Attributes.Product" DEFAULT="(unknown)">
<CFPARAM NAME="Attributes.Qty" DEFAULT="1">
<CFIF ThisTag.ExecutionMode IS "start">
	<!--- reach up to the enclosing order tag --->
	<CFSET Order = GetBaseTagData("CF_SN_SYSORDER")>
	<CFSET Order.ThisTag.ItemCount = Order.ThisTag.ItemCount + Attributes.Qty>
	<CFOUTPUT><TR><TD ALIGN="right">#Attributes.Qty#</TD><TD>#Attributes.Product#</TD>
	<TD>#Order.Attributes.Customer#</TD><TD><TT>#GetBaseTagList()#</TT></TD></TR></CFOUTPUT>
</CFIF>
