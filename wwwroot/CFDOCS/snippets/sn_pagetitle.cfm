<!--- sn_pagetitle.cfm: helper for the CFINCLUDE example.
      Reads Variables.PageTitle from the including page and counts
      its title bars in Variables.TitleDrawn. --->
<CFPARAM NAME="PageTitle" DEFAULT="Untitled">
<CFPARAM NAME="TitleDrawn" DEFAULT="0">
<CFSET TitleDrawn = TitleDrawn + 1>
<CFOUTPUT>
<TABLE WIDTH="100%" CELLPADDING=4 CELLSPACING=0 BORDER=0>
<TR><TD BGCOLOR="##000080"><FONT FACE="Arial, Helvetica" SIZE="3" COLOR="##FFFFFF"><B>#PageTitle#</B></FONT></TD>
<TD BGCOLOR="##000080" ALIGN="RIGHT"><FONT FACE="Arial, Helvetica" SIZE="1" COLOR="##FFFFCC">#DateFormat(Now(), "mmmm d, yyyy")#</FONT></TD></TR>
</TABLE>
</CFOUTPUT>
