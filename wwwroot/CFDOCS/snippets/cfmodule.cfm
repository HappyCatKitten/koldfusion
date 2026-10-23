<!--- sn_titlebox.cfm is a custom tag in this directory --->
<CFSET BoxesDrawn = 0>

<CFMODULE TEMPLATE="sn_titlebox.cfm" TITLE="Called with CFMODULE" COLOR="##CCCCFF">
  The text between the start and end tags is the body.
</CFMODULE>

<CF_SN_TITLEBOX TITLE="Called as CF_SN_TITLEBOX" SHOUT="Yes">
  The end pass of this tag turned the body into capitals.
</CF_SN_TITLEBOX>

<CF_SN_TITLEBOX TITLE="Called without an end tag">

<CFOUTPUT><P>The tag counted its boxes in Caller.BoxesDrawn: #BoxesDrawn#</P></CFOUTPUT>
