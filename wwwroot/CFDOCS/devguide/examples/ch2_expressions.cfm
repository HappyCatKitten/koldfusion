<!--- ch2_expressions.cfm: operators, functions and decisions --->
<CFSET FirstName = "Ellen">
<CFSET LastName = "O'Malley">
<CFSET FullName = FirstName & " " & LastName>
<CFSET Salary = 61000>
<CFSET Raise = Salary * 0.04>

<CFOUTPUT>
<P><B>#UCase(FullName)#</B> has #Len(FullName)# characters
and her initials are #Left(FirstName, 1)##Left(LastName, 1)#.</P>

<P>A 4% raise is #DollarFormat(Raise)#, bringing her to
#DollarFormat(Salary + Raise)# a year.</P>

<P>Does "#LastName#" contain an apostrophe?
#YesNoFormat(LastName CONTAINS "'")#</P>

<CFIF Salary GTE 60000 AND Salary LT 80000>
  <P>Pay band: senior.</P>
<CFELSEIF Salary GTE 80000>
  <P>Pay band: principal.</P>
<CFELSE>
  <P>Pay band: associate.</P>
</CFIF>

<CFSWITCH EXPRESSION="#DayOfWeek(Now())#">
  <CFCASE VALUE="1,7"><P>It is the weekend. Why are you coding?</P></CFCASE>
  <CFCASE VALUE="6"><P>It is Friday. Do not deploy today.</P></CFCASE>
  <CFDEFAULTCASE><P>It is a working day.</P></CFDEFAULTCASE>
</CFSWITCH>

<P>Shipping: #IIf(Salary GT 50000, DE("free"), DE("$5.00"))#</P>

<P>You are viewing #CGI.SCRIPT_NAME# from #CGI.REMOTE_ADDR#.</P>
</CFOUTPUT>
