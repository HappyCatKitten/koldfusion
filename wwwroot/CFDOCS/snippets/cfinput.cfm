<CFIF IsDefined("Form.FieldNames")>
  <CFOUTPUT>
  <P><B>Order received:</B> #Form.Quantity# x #Form.Color# case,
  ship #Form.ShipDate# to ZIP #Form.Zip#, phone #Form.Phone#,
  <CFIF IsDefined("Form.GiftWrap")>gift wrapped.<CFELSE>no gift wrap.</CFIF>
  </CFOUTPUT>
</CFIF>

<CFFORM NAME="Order" ACTION="cfinput.cfm">
<TABLE>
<TR><TD>Quantity:</TD><TD><CFINPUT TYPE="Text" NAME="Quantity" VALUE="1" SIZE="3"
    VALIDATE="integer" RANGE="1,99" REQUIRED="Yes"
    MESSAGE="Order between 1 and 99 cases."></TD></TR>
<TR><TD>Case color:</TD><TD>
    <CFINPUT TYPE="Radio" NAME="Color" VALUE="Beige" CHECKED="Yes"> Beige
    <CFINPUT TYPE="Radio" NAME="Color" VALUE="Translucent blue"> Translucent blue</TD></TR>
<TR><TD>Ship on:</TD><TD><CFINPUT TYPE="Text" NAME="ShipDate" SIZE="10" VALIDATE="date"
    VALUE="#DateFormat(DateAdd('d', 7, Now()), 'mm/dd/yyyy')#"
    MESSAGE="Enter the date as mm/dd/yyyy."></TD></TR>
<TR><TD>ZIP code:</TD><TD><CFINPUT TYPE="Text" NAME="Zip" SIZE="10" VALIDATE="zipcode"
    REQUIRED="Yes" MESSAGE="A US ZIP code, like 02139."></TD></TR>
<TR><TD>Phone:</TD><TD><CFINPUT TYPE="Text" NAME="Phone" SIZE="14"
    VALIDATE="telephone" MESSAGE="A phone number like 617-555-1212."></TD></TR>
<TR><TD></TD><TD><CFINPUT TYPE="Checkbox" NAME="GiftWrap" VALUE="Yes"> Gift wrap</TD></TR>
</TABLE>
<INPUT TYPE="Submit" VALUE="Place order">
</CFFORM>
