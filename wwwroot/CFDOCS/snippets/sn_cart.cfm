<!---
    sn_cart.cfm - base tag used by the CFASSOCIATE example.
    Collects the attributes of the <CF_SN_CARTITEM> tags nested inside it
    and prints them as an order table with a total.
--->
<CFIF NOT IsDefined("ThisTag.ExecutionMode")>
  This template is a custom tag. Run the CFASSOCIATE example to see it at work.
  <CFABORT>
</CFIF>
<CFPARAM NAME="Attributes.Customer" DEFAULT="Valued Customer">

<CFIF ThisTag.ExecutionMode IS "End">
  <!--- The child tags have run and filed their attributes in ThisTag.AssocAttribs --->
  <CFSET ThisTag.GeneratedContent = "">
  <CFSET Total = 0>
  <CFOUTPUT>
  <TABLE BORDER=1 CELLPADDING=3 CELLSPACING=0>
  <TR BGCOLOR="##CCCCFF"><TH COLSPAN=3 ALIGN=LEFT>Order for #Attributes.Customer#</TH></TR>
  <TR><TH ALIGN=LEFT>Item</TH><TH>Qty</TH><TH ALIGN=RIGHT>Amount</TH></TR>
  <CFLOOP FROM="1" TO="#ArrayLen(ThisTag.AssocAttribs)#" INDEX="i">
    <CFSET Line = ThisTag.AssocAttribs[i]>
    <CFSET Amount = Line.Qty * Line.Price>
    <CFSET Total = Total + Amount>
    <TR><TD>#Line.Item#</TD><TD ALIGN=CENTER>#Line.Qty#</TD><TD ALIGN=RIGHT>#DollarFormat(Amount)#</TD></TR>
  </CFLOOP>
  <TR><TD COLSPAN=2><B>Total (#ArrayLen(ThisTag.AssocAttribs)# lines)</B></TD><TD ALIGN=RIGHT><B>#DollarFormat(Total)#</B></TD></TR>
  </TABLE>
  </CFOUTPUT>
</CFIF>
