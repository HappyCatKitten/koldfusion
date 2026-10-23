<!--- ch1_variables.cfm: setting and showing variables --->
<CFSET Product = "56K V.90 Fax/Modem">
<CFSET Price = 129.99>
<CFSET Quantity = 3>
<CFSET Total = Price * Quantity>
<CFSET OrderDate = Now()>
<CFSET IsRush = Quantity GT 2>

<CFOUTPUT>
<TABLE BORDER="1" CELLPADDING="4" CELLSPACING="0">
<TR BGCOLOR="##CCCCFF"><TH>Item</TH><TH>Qty</TH><TH>Total</TH><TH>Rush?</TH></TR>
<TR>
  <TD>#Product#</TD>
  <TD ALIGN="RIGHT">#Quantity#</TD>
  <TD ALIGN="RIGHT">#DollarFormat(Total)#</TD>
  <TD>#YesNoFormat(IsRush)#</TD>
</TR>
</TABLE>
<P>Ordered on #DateFormat(OrderDate, "mm/dd/yyyy")#. Raw values:
Total = #Total#, IsRush = #IsRush#.</P>
</CFOUTPUT>
