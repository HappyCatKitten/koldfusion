<!--- A Hashtable from the Java runtime, used straight from CFML --->
<CFTRY>
  <CFOBJECT TYPE="JAVA" ACTION="Create" CLASS="java.util.Hashtable" NAME="Prices">
  <CFSET Prices.put("56K modem", "129.95")>
  <CFSET Prices.put("Zip drive", "149.00")>
  <CFSET Prices.put("Y2K sticker", "0.99")>
  <CFOUTPUT>
  <P>The Hashtable holds #Prices.size()# items. A Zip drive costs
  #DollarFormat(Prices.get("Zip drive"))#.</P>
  </CFOUTPUT>
  <!--- returned Hashtables become structures --->
  <CFSET Copy = Prices.clone()>
  <TABLE BORDER=1 CELLPADDING=3>
  <CFLOOP COLLECTION="#Copy#" ITEM="Item">
    <CFOUTPUT><TR><TD>#Item#</TD><TD ALIGN=RIGHT>#Copy[Item]#</TD></TR></CFOUTPUT>
  </CFLOOP>
  </TABLE>
  <!--- static methods work before init() --->
  <CFOBJECT TYPE="JAVA" ACTION="Create" CLASS="java.lang.Math" NAME="JMath">
  <CFOUTPUT><P>Math.max(1999, 2000) = #JMath.max(1999, 2000)#,
  Math.PI = #JMath.PI#</P></CFOUTPUT>
  <CFCATCH TYPE="Object">
    <CFOUTPUT>
    <P><B>No Java today:</B> #CFCATCH.Message#<BR>
    <I>#CFCATCH.Detail#</I></P>
    </CFOUTPUT>
  </CFCATCH>
</CFTRY>
