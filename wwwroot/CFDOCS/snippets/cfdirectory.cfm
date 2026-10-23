<!--- Build a little directory in the temp area, list it, and clean up --->
<CFSET Demo = GetTempDirectory() & "cfdirectory_demo">
<CFIF NOT DirectoryExists(Demo)>
  <CFDIRECTORY ACTION="CREATE" DIRECTORY="#Demo#">
</CFIF>
<CFFILE ACTION="WRITE" FILE="#Demo#/readme.txt" OUTPUT="Read me first.">
<CFFILE ACTION="WRITE" FILE="#Demo#/index.cfm" OUTPUT="<CFOUTPUT>##Now()##</CFOUTPUT>">
<CFFILE ACTION="WRITE" FILE="#Demo#/notes.txt" OUTPUT="Remember to test on Netscape 4.7 too.">

<CFDIRECTORY ACTION="LIST" DIRECTORY="#Demo#" NAME="Listing" FILTER="*.*" SORT="Size DESC">
<TABLE BORDER=1 CELLPADDING=3>
<TR><TH>Name</TH><TH>Size</TH><TH>Type</TH><TH>Mode</TH></TR>
<CFOUTPUT QUERY="Listing">
<TR><TD>#Name#</TD><TD>#Size#</TD><TD>#Type#</TD><TD>#Mode#</TD></TR>
</CFOUTPUT>
</TABLE>

<CFLOOP QUERY="Listing">
  <CFFILE ACTION="DELETE" FILE="#Demo#/#Listing.Name#">
</CFLOOP>
<CFDIRECTORY ACTION="DELETE" DIRECTORY="#Demo#">
<CFOUTPUT><P>Directory removed again: #YesNoFormat(NOT DirectoryExists(Demo))#</P></CFOUTPUT>
