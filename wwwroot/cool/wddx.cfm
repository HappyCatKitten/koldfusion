<!--- WDDX: serialize a query to a packet and to JavaScript --->
<cfset pageTitle = "WDDX: CFML to JavaScript">
<cfquery name="products" datasource="cfsnippets" maxrows="6">SELECT Name, Price, Category FROM Products ORDER BY Price DESC</cfquery>
<cfwddx action="cfml2wddx" input="#products#" output="packet">
<cfwddx action="cfml2js" input="#products#" toplevelvariable="products" output="js">
<cfinclude template="_top.cfm">
<P>The query below was converted to JavaScript on the server with <TT>&lt;CFWDDX ACTION="CFML2JS"&gt;</TT> and the table is
drawn by <TT>document.write()</TT> in your browser:</P>
<SCRIPT LANGUAGE="JavaScript" SRC="/CFIDE/scripts/wddx.js"></SCRIPT>
<SCRIPT LANGUAGE="JavaScript">
<!--
<cfoutput>#js#</cfoutput>
document.write("<TABLE BORDER=1 CELLPADDING=4 CELLSPACING=0 BGCOLOR='#FFFFEE'><TR BGCOLOR='#C0C0C0'><TH>Product</TH><TH>Price</TH><TH>Category</TH></TR>");
for (var i = 0; i < products.getRowCount(); i++) {
	document.write("<TR><TD>" + products.getField(i, "name") + "</TD><TD ALIGN=RIGHT>$" + products.getField(i, "price") + "</TD><TD>" + products.getField(i, "category") + "</TD></TR>");
}
document.write("</TABLE>");
//-->
</SCRIPT>
<P>The same data as a WDDX packet (<cfoutput>#Len(packet)#</cfoutput> bytes of XML, the format Gibson invented in 1998 so servers could swap data):</P>
<TABLE BORDER=1 CELLPADDING=6 BGCOLOR="#EEEEEE"><TR><TD><FONT FACE="Courier New" SIZE=1><cfoutput>#HTMLEditFormat(packet)#</cfoutput></FONT></TD></TR></TABLE>
<cfinclude template="_bottom.cfm">
