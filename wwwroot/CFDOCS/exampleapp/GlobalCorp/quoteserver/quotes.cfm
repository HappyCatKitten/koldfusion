<!---
	quotes.cfm - GlobalCorp's pretend stock quote server.
	Returns one line per symbol, as plain text:
	    SYMBOL|Company name|last price|change from previous close
	Every request nudges the prices up or down by a few eighths,
	so the ticker on the home page looks alive.
	Usage: quotes.cfm?symbols=GLBC,WDGT
--->
<CFSETTING ENABLECFOUTPUTONLY="Yes">
<CFPARAM NAME="URL.symbols" DEFAULT="GLBC">
<CFSET SymbolList = UCase(REReplace(URL.symbols, "[^A-Za-z,]", "", "ALL"))>
<CFIF NOT Len(SymbolList)><CFSET SymbolList = "GLBC"></CFIF>

<!--- ListQualify adds single quotes; PreserveSingleQuotes stops CFQUERY doubling them --->
<CFSET QuotedSymbols = ListQualify(SymbolList, "'")>

<CFLOCK NAME="GlobalCorpQuoteServer" TYPE="Exclusive" TIMEOUT="10">
	<CFQUERY NAME="GetQuotes" DATASOURCE="#Request.DSN#">
		SELECT Symbol, Company, LastPrice, PrevClose
		FROM Quotes
		WHERE Symbol IN (#PreserveSingleQuotes(QuotedSymbols)#)
		ORDER BY Symbol
	</CFQUERY>
	<CFLOOP QUERY="GetQuotes">
		<!--- random walk in eighths of a dollar, never below a dollar --->
		<CFSET NewPrice = LastPrice + (RandRange(-3, 3) / 8)>
		<CFIF NewPrice LT 1><CFSET NewPrice = 1></CFIF>
		<CFQUERY DATASOURCE="#Request.DSN#">
			UPDATE Quotes SET LastPrice = #NewPrice# WHERE Symbol = '#Symbol#'
		</CFQUERY>
		<CFSET QuerySetCell(GetQuotes, "LastPrice", NewPrice, CurrentRow)>
	</CFLOOP>
</CFLOCK>

<CFCONTENT TYPE="text/plain">
<CFOUTPUT QUERY="GetQuotes">#Symbol#|#Company#|#NumberFormat(LastPrice, "0.000")#|#NumberFormat(LastPrice - PrevClose, "-0.000")##Chr(13)##Chr(10)#</CFOUTPUT>
