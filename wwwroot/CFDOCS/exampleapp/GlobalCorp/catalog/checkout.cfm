<!---
	catalog/checkout.cfm - delivery details for the order
--->
<CFSET Section = "catalog">
<CFSET PageTitle = "Check Out">

<CFLOCK SCOPE="Session" TYPE="ReadOnly" TIMEOUT="10">
	<CFSET CartIsEmpty = StructIsEmpty(Session.Cart)>
</CFLOCK>
<CFIF CartIsEmpty>
	<CFLOCATION URL="cart.cfm" ADDTOKEN="No">
</CFIF>

<!--- fill in what we already know about the shopper from the directory --->
<CFQUERY NAME="GetMe" DATASOURCE="#Request.DSN#">
	SELECT e.Email, d.MailStop, d.DeptName
	FROM Employees e, Departments d
	WHERE e.Dept_ID = d.Dept_ID AND e.Emp_ID = #Val(Request.Emp_ID)#
</CFQUERY>

<CFINCLUDE TEMPLATE="../header.cfm">

<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD BGCOLOR="#003366">
<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=1><TR><TD BGCOLOR="#FFFFFF">
	<CF_CARTSUMMARY TEXTCOLOR="##000000">
</TD></TR></TABLE>
</TD></TR></TABLE>
<P>Tell us where to deliver your order. A confirmation will be e-mailed to you.</P>

<CFFORM ACTION="placeorder.cfm" METHOD="POST" NAME="CheckoutForm">
<CFOUTPUT>
<INPUT TYPE="Hidden" NAME="ShipName_required" VALUE="Please enter the name to deliver to.">
<INPUT TYPE="Hidden" NAME="Email_required" VALUE="Please enter an e-mail address for the confirmation.">
<INPUT TYPE="Hidden" NAME="MailStop_required" VALUE="Please enter a mail stop.">
<TABLE BORDER=0 CELLPADDING=3>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Deliver to:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="ShipName" VALUE="#Request.FullName#" SIZE="30" MAXLENGTH="60" REQUIRED="Yes" MESSAGE="Please enter the name to deliver to."></TD></TR>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>E-mail:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="Email" VALUE="#GetMe.Email#" SIZE="30" MAXLENGTH="60" REQUIRED="Yes" MESSAGE="Please enter an e-mail address for the confirmation."></TD></TR>
<TR><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Mail stop:</B></FONT></TD>
	<TD><CFINPUT TYPE="Text" NAME="MailStop" VALUE="#GetMe.MailStop#" SIZE="10" MAXLENGTH="20" REQUIRED="Yes" MESSAGE="Please enter a mail stop.">
	<FONT FACE="#Request.Font#" SIZE=1><CFIF GetMe.RecordCount>(#GetMe.DeptName#)</CFIF></FONT></TD></TR>
<TR VALIGN=TOP><TD ALIGN=RIGHT><FONT FACE="#Request.Font#" SIZE=2><B>Notes:</B></FONT></TD>
	<TD><TEXTAREA NAME="Notes" ROWS=3 COLS=40 WRAP="VIRTUAL"></TEXTAREA><BR>
	<FONT FACE="#Request.Font#" SIZE=1>Shirt sizes, delivery instructions, etc.</FONT></TD></TR>
<TR><TD></TD><TD><INPUT TYPE="Submit" VALUE="Place Order"> <INPUT TYPE="Button" VALUE="Back to Cart" onClick="location.href='cart.cfm'"></TD></TR>
</TABLE>
</CFOUTPUT>
</CFFORM>

<CFINCLUDE TEMPLATE="../footer.cfm">
