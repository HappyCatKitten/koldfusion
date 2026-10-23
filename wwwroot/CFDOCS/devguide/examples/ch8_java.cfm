<!--- ch8_java.cfm: the Java runtime from CFML --->
<CFTRY>
  <CFSET Tokens = CreateObject("JAVA", "java.util.StringTokenizer")>
  <CFSET Tokens.init("Allaire,Netscape,Excite,Yahoo", ",")>
  <CFSET Dotcoms = ArrayNew(1)>
  <CFLOOP CONDITION="Tokens.hasMoreTokens()">
    <CFSET ArrayAppend(Dotcoms, Tokens.nextToken())>
  </CFLOOP>
  <CFSET Sorted = CreateObject("JAVA", "java.util.TreeSet")>
  <CFLOOP INDEX="D" LIST="#ArrayToList(Dotcoms)#"><CFSET Sorted.add(D)></CFLOOP>
  <CFOUTPUT>
  <P>#ArrayLen(Dotcoms)# companies, sorted by Java: #ArrayToList(Sorted.toArray(), ", ")#</P>
  </CFOUTPUT>
  <CFTRY>
    <CFSET N = CreateObject("JAVA", "java.lang.Integer").parseInt("1999 or bust")>
    <CFCATCH TYPE="Object">
      <CFOUTPUT><P>parseInt threw <B>#CFCATCH.Message#</B>, as it should.</P></CFOUTPUT>
    </CFCATCH>
  </CFTRY>
  <CFCATCH TYPE="Object">
    <CFOUTPUT><P>Java is not available here: <I>#CFCATCH.Message#</I></P></CFOUTPUT>
  </CFCATCH>
</CFTRY>
