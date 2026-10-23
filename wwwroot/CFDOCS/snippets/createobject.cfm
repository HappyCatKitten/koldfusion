<CFSET Kinds = "COM|Word.Application,JAVA|java.util.Vector">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>CreateObject()</TH><TH>Result</TH></TR>
<CFLOOP LIST="#Kinds#" INDEX="k">
  <CFSET Result = "Created">
  <CFTRY>
    <CFSET Obj = CreateObject(ListFirst(k, "|"), ListLast(k, "|"))>
  <CFCATCH TYPE="Object">
    <CFSET Result = "<I>#CFCATCH.Message#</I>">
  </CFCATCH>
  </CFTRY>
  <CFOUTPUT><TR><TD>"#ListFirst(k, "|")#", "#ListLast(k, "|")#"</TD><TD>#Result#</TD></TR></CFOUTPUT>
</CFLOOP>
</TABLE>
