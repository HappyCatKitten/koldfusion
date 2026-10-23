<!--- ch7_rethrow.cfm: handle what you can, pass on the rest --->
<CFSET Attempts = "Store.OutOfStock,Store.PriceChanged">

<CFLOOP LIST="#Attempts#" INDEX="ErrType">
  <CFTRY>
    <CFTRY>
      <CFTHROW TYPE="#ErrType#" MESSAGE="Simulated #ErrType# error">
    <CFCATCH TYPE="Store">
      <CFIF CFCATCH.Type IS "Store.OutOfStock">
        <CFOUTPUT><P>Inner handler: offered a back-order for "#CFCATCH.Message#".</P></CFOUTPUT>
      <CFELSE>
        <CFOUTPUT><P>Inner handler: cannot deal with #CFCATCH.Type#, passing it on.</P></CFOUTPUT>
        <CFRETHROW>
      </CFIF>
    </CFCATCH>
    </CFTRY>
  <CFCATCH TYPE="Any">
    <CFOUTPUT><P>Outer handler: caught #CFCATCH.Type# ("#CFCATCH.Message#").</P></CFOUTPUT>
  </CFCATCH>
  </CFTRY>
</CFLOOP>
