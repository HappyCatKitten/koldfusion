<CFSET Colors = "Red,Green,Blue">
<P>Without the directive, every indent survives:</P>
<PRE>
<CFLOOP LIST="#Colors#" INDEX="c">
        <CFOUTPUT>[#c#]</CFOUTPUT>
</CFLOOP>
</PRE>
<P>With SUPPRESSWHITESPACE="Yes", the runs of blanks collapse:</P>
<PRE>
<CFPROCESSINGDIRECTIVE SUPPRESSWHITESPACE="Yes">
<CFLOOP LIST="#Colors#" INDEX="c">
        <CFOUTPUT>[#c#]</CFOUTPUT>
</CFLOOP>
</CFPROCESSINGDIRECTIVE>
</PRE>
