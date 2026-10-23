<CFSET Kinds = "JAVA|java.util.Vector,JAVA|java.util.Random,COM|Word.Application,CORBA|c:\myobject.ior">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>CreateObject()</TH><TH>Result</TH></TR>
<CFLOOP LIST="#Kinds#" INDEX="k">
  <CFTRY>
    <CFSET Obj = CreateObject(ListFirst(k, "|"), ListLast(k, "|"), "IOR")>
    <CFSET Result = "Created: <TT>#Obj.toString()#</TT>">
  <CFCATCH TYPE="Object">
    <CFSET Result = "<I>#CFCATCH.Message#</I>">
  </CFCATCH>
  </CFTRY>
  <CFOUTPUT><TR><TD>"#ListFirst(k, "|")#", "#ListLast(k, "|")#"</TD><TD>#Result#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
<CFTRY>
  <CFSET Words = CreateObject("JAVA", "java.util.StringTokenizer")>
  <CFSET Words.init("one small step for man", " ")>
  <CFOUTPUT><P>StringTokenizer counted #Words.countTokens()# words.</P></CFOUTPUT>
  <CFCATCH TYPE="Object"><CFOUTPUT><P><I>#CFCATCH.Message#</I></P></CFOUTPUT></CFCATCH>
</CFTRY>
