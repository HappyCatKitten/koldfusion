<!---
    sn_titlebox.cfm - a custom tag used by the CFMODULE example.
    Draws a titled box around the text between its start and end tags.
    Call it as <CF_SN_TITLEBOX TITLE="..."> ... </CF_SN_TITLEBOX>
    or as <CFMODULE TEMPLATE="sn_titlebox.cfm" TITLE="..."> ... </CFMODULE>
--->
<CFIF NOT IsDefined("ThisTag.ExecutionMode")>
  This template is a custom tag. Run the CFMODULE example to see it at work.
  <CFABORT>
</CFIF>
<CFPARAM NAME="Attributes.Title" DEFAULT="Untitled">
<CFPARAM NAME="Attributes.Color" DEFAULT="##FFFFCC">
<CFPARAM NAME="Attributes.Shout" DEFAULT="No">

<CFIF ThisTag.ExecutionMode IS "Start">
  <!--- Report back to the calling page --->
  <CFPARAM NAME="Caller.BoxesDrawn" DEFAULT="0">
  <CFSET Caller.BoxesDrawn = Caller.BoxesDrawn + 1>
  <CFOUTPUT>
  <TABLE BORDER=1 CELLPADDING=4 CELLSPACING=0 WIDTH=360>
  <TR><TH ALIGN=LEFT BGCOLOR="#Attributes.Color#"><FONT FACE="Arial, Helvetica" SIZE=2>#Attributes.Title#</FONT></TH></TR>
  <TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>
  </CFOUTPUT>
  <CFIF NOT ThisTag.HasEndTag>
    <I>(called without an end tag, so there is no body)</I></FONT></TD></TR></TABLE><BR>
  </CFIF>
<CFELSE>
  <!--- End mode: the body has run; we may rewrite what it produced --->
  <CFIF Attributes.Shout>
    <CFSET ThisTag.GeneratedContent = UCase(ThisTag.GeneratedContent)>
  </CFIF>
  </FONT></TD></TR></TABLE><BR>
</CFIF>
