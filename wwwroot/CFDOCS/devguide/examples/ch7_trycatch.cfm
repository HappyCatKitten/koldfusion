<!--- ch7_trycatch.cfm: catching errors --->

<!--- 1. A database error: the table name is misspelled --->
<CFTRY>
  <CFQUERY NAME="GetEmps" DATASOURCE="cfsnippets">
  SELECT LastName FROM Employes
  </CFQUERY>
  <P>This line is never reached.</P>
<CFCATCH TYPE="Database">
  <CFOUTPUT>
  <P><B>The staff list is unavailable right now.</B><BR>
  <FONT SIZE="1">(For the developer: #CFCATCH.Message#, SQLState #CFCATCH.SQLState#)</FONT></P>
  </CFOUTPUT>
</CFCATCH>
</CFTRY>

<!--- 2. An expression error: dividing by zero --->
<CFSET Visitors = 0>
<CFTRY>
  <CFSET Ratio = 100 / Visitors>
  <CFCATCH TYPE="Expression">
    <CFSET Ratio = 0>
    <CFOUTPUT><P>Could not compute the ratio (#CFCATCH.Message#); using 0.</P></CFOUTPUT>
  </CFCATCH>
</CFTRY>

<!--- 3. Your own errors, thrown with CFTHROW --->
<CFQUERY NAME="GetSoftware" DATASOURCE="cfsnippets">
SELECT Name, InStock FROM Products WHERE Category = 'Software' ORDER BY Name
</CFQUERY>
<P>Ordering one of each software title:</P>
<UL>
<CFLOOP QUERY="GetSoftware">
  <CFTRY>
    <CFIF InStock LTE 0>
      <CFTHROW TYPE="Store.OutOfStock" MESSAGE="#Name# is sold out"
               DETAIL="Restocking is expected after January 1, 2000.">
    </CFIF>
    <CFOUTPUT><LI>#Name#: ordered.</CFOUTPUT>
  <CFCATCH TYPE="Store">
    <CFOUTPUT><LI><FONT COLOR="##CC0000">#CFCATCH.Message#.</FONT> #CFCATCH.Detail#</CFOUTPUT>
  </CFCATCH>
  </CFTRY>
</CFLOOP>
</UL>
