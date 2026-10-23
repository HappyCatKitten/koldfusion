<!---
  wddx.cfm - a WDDX round trip. A structure holding every WDDX data type
  (string, number, boolean, date-time, array, nested structure and a
  recordset) is serialized with CFWDDX CFML2WDDX, shown as an XML packet,
  deserialized again with WDDX2CFML and compared field by field. Also shows
  CFML2JS, and lets you paste your own packet. WDDX was Allaire's 1998
  answer to "how do two web apps swap data?" - XML before it was cool.
  KoldFusion Demo Gallery original - MIT licence.
--->
<cfparam name="Form.packet" default="">

<!--- 1. build some data --->
<cfset order = StructNew()>
<cfset order.customer = "Ada Lovelace & Co. <ada@example.com>">
<cfset order.total = 1999.99>
<cfset order.rush = true>
<cfset order.placed = CreateDateTime(1999, 12, 31, 23, 59, 59)>
<cfset order.items = ArrayNew(1)>
<cfset order.items[1] = "Y2K survival kit">
<cfset order.items[2] = "56k modem">
<cfset order.items[3] = 3>
<cfset order.shipTo = StructNew()>
<cfset order.shipTo.city = "Cambridge">
<cfset order.shipTo.zip = "02139">
<cfset order.history = QueryNew("Status,Changed")>
<cfset QueryAddRow(order.history, 2)>
<cfset QuerySetCell(order.history, "Status", "Received", 1)>
<cfset QuerySetCell(order.history, "Changed", "12/31/1999 23:59", 1)>
<cfset QuerySetCell(order.history, "Status", "Shipped", 2)>
<cfset QuerySetCell(order.history, "Changed", "01/01/2000 00:01", 2)>

<!--- 2. serialize, 3. deserialize --->
<cfwddx action="cfml2wddx" input="#order#" output="packet">
<cfwddx action="wddx2cfml" input="#packet#" output="copy">
<cfwddx action="cfml2js" input="#order#" toplevelvariable="order" output="js">

<html>
<head>
<title>WDDX Round Trip</title>
</head>
<body bgcolor="#FFFFFF" background="/images/bg_tile.gif">
<center>
<table width="640" border="0" cellpadding="10" bgcolor="#FFFFFF"><tr><td>
<font face="Arial, Helvetica" size="5" color="#003399"><b>WDDX Round Trip</b></font><br>
<font face="Arial, Helvetica" size="2">Web Distributed Data eXchange: CFML values in, XML out, and back again.</font>
<p>
<font face="Arial, Helvetica" size="3"><b>1. The packet</b></font>
<font face="Arial, Helvetica" size="2">(<cfoutput>#Len(packet)#</cfoutput> bytes, line breaks added for reading)</font>
<cfoutput>#HTMLCodeFormat(Replace(packet, "><", ">" & Chr(10) & "<", "ALL"))#</cfoutput>

<font face="Arial, Helvetica" size="3"><b>2. Before and after</b></font>
<cfoutput>
<table border="1" cellpadding="4" cellspacing="0" width="100%">
<tr bgcolor="##669966"><th><font face="Arial" size="2" color="##FFFFFF">Field</font></th><th><font face="Arial" size="2" color="##FFFFFF">Original</font></th><th><font face="Arial" size="2" color="##FFFFFF">After the round trip</font></th><th><font face="Arial" size="2" color="##FFFFFF">Same?</font></th></tr>
<cfloop list="customer,total,rush,placed,shipTo.city,shipTo.zip" index="f">
	<cfset a = Evaluate("order.#f#")>
	<cfset b = Evaluate("copy.#f#")>
	<tr><td><font face="Courier New" size="2">#f#</font></td>
	<td><font face="Arial" size="2">#HTMLEditFormat(a)#</font></td>
	<td><font face="Arial" size="2">#HTMLEditFormat(b)#</font></td>
	<td align="center"><font face="Arial" size="2">#YesNoFormat(a IS b)#</font></td></tr>
</cfloop>
<tr><td><font face="Courier New" size="2">items</font></td>
	<td><font face="Arial" size="2">#ArrayToList(order.items, " / ")#</font></td>
	<td><font face="Arial" size="2">#ArrayToList(copy.items, " / ")#</font></td>
	<td align="center"><font face="Arial" size="2">#YesNoFormat(ArrayToList(order.items) IS ArrayToList(copy.items))#</font></td></tr>
<tr><td><font face="Courier New" size="2">history</font></td>
	<td><font face="Arial" size="2">#order.history.RecordCount# rows: #ValueList(order.history.Status)#</font></td>
	<td><font face="Arial" size="2">#copy.history.RecordCount# rows: #ValueList(copy.history.Status)#</font></td>
	<td align="center"><font face="Arial" size="2">#YesNoFormat(ValueList(order.history.Status) IS ValueList(copy.history.Status))#</font></td></tr>
</table>
<p><font face="Arial, Helvetica" size="2">IsWDDX(packet): <b>#IsWDDX(packet)#</b> &middot;
IsStruct(copy): <b>#IsStruct(copy)#</b> &middot; IsQuery(copy.history): <b>#IsQuery(copy.history)#</b> &middot;
keys: <b>#ListSort(StructKeyList(copy), "textnocase")#</b></font></p>
</cfoutput>

<font face="Arial, Helvetica" size="3"><b>3. The same data as JavaScript (CFML2JS)</b></font>
<cfoutput>#HTMLCodeFormat(Replace(js, ";", ";" & Chr(10), "ALL"))#</cfoutput>

<font face="Arial, Helvetica" size="3"><b>4. Try your own packet</b></font><br>
<font face="Arial, Helvetica" size="2">Paste a WDDX packet (or edit the one above) and the server will deserialize it.</font>
<form action="wddx.cfm" method="post">
<textarea name="packet" rows="6" cols="70" wrap="virtual"><cfoutput>#HTMLEditFormat(IIf(Len(Form.packet), "Form.packet", DE("<wddxPacket version='1.0'><header/><data><array length='2'><string>Hello</string><number>42</number></array></data></wddxPacket>")))#</cfoutput></textarea><br>
<input type="submit" value="Deserialize">
</form>
<cfif Len(Form.packet)>
	<cfif IsWDDX(Form.packet)>
		<cfwddx action="wddx2cfml" input="#Form.packet#" output="yours">
		<font face="Arial, Helvetica" size="2"><b>Valid packet.</b>
		<cfoutput>
		<cfif IsArray(yours)>An array of #ArrayLen(yours)# element(s).
		<cfelseif IsQuery(yours)>A recordset of #yours.RecordCount# row(s), columns #yours.ColumnList#.
		<cfelseif IsStruct(yours)>A structure with keys #StructKeyList(yours)#.
		<cfelse>A simple value: <b>#HTMLEditFormat(yours)#</b>
		</cfif>
		Re-serialized it looks like this:
		<cfwddx action="cfml2wddx" input="#yours#" output="again">
		#HTMLCodeFormat(again)#
		</cfoutput>
		</font>
	<cfelse>
		<font face="Arial, Helvetica" size="2" color="#CC0000"><b>That is not a valid WDDX packet.</b></font>
	</cfif>
</cfif>
</td></tr></table>
</center>
<cfinclude template="_footer.cfm">
</body>
</html>
