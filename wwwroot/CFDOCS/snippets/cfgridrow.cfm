<!--- How long does a 1 MB download take? (1 MB = 8,388,608 bits) --->
<H3>The 1999 download calculator</H3>
<CFFORM NAME="Calc" ACTION="cfgridrow.cfm">
<CFGRID NAME="Speeds" WIDTH="360">
  <CFGRIDCOLUMN NAME="Line" HEADER="Connection">
  <CFGRIDCOLUMN NAME="Bps" HEADER="Bits/second" DATAALIGN="Right">
  <CFGRIDCOLUMN NAME="Minutes" HEADER="Minutes per MB" DATAALIGN="Right">
  <CFLOOP LIST="14.4K modem:14400|28.8K modem:28800|56K modem:53000|ISDN:128000|T1:1544000"
      DELIMITERS="|" INDEX="Line">
    <CFSET Bps = ListLast(Line, ":")>
    <CFGRIDROW DATA="#ListFirst(Line, ':')#,#Bps#,#DecimalFormat(8388608 / Bps / 60)#">
  </CFLOOP>
</CFGRID>
</CFFORM>
