<!--- ch5_guestbook.cfm: sign the guest book with CFINSERT.
      To keep the demo tidy, the new entry is removed again
      after it has been displayed. --->
<CFIF IsDefined("Form.Name") AND Trim(Form.Name) IS NOT "">
  <CFSET Form.Name = Left(Trim(Form.Name), 50)>
  <CFTRANSACTION>
    <CFINSERT DATASOURCE="cfsnippets" TABLENAME="GuestBook"
              FORMFIELDS="Name,Email,Comments">
    <CFQUERY NAME="GetNew" DATASOURCE="cfsnippets">
    SELECT MAX(ID) AS NewID FROM GuestBook
    </CFQUERY>
  </CFTRANSACTION>
  <CFSET Highlight = GetNew.NewID>
<CFELSE>
  <CFSET Highlight = 0>
</CFIF>

<CFQUERY NAME="GetEntries" DATASOURCE="cfsnippets" MAXROWS="5">
SELECT ID, Name, Comments, Posted FROM GuestBook ORDER BY ID DESC
</CFQUERY>

<H3>Our guest book</H3>
<CFOUTPUT QUERY="GetEntries">
  <P<CFIF ID IS Highlight> STYLE="background: ##FFFFCC"</CFIF>>
  <B>#HTMLEditFormat(Name)#</B> wrote on #DateFormat(Posted, "mmm d, yyyy")#:<BR>
  #HTMLEditFormat(Comments)#</P>
</CFOUTPUT>

<CFIF Highlight GT 0>
  <!--- Tidy up: remove the entry we just added --->
  <CFQUERY DATASOURCE="cfsnippets">
  DELETE FROM GuestBook
  WHERE ID = <CFQUERYPARAM VALUE="#Highlight#" CFSQLTYPE="CF_SQL_INTEGER">
  </CFQUERY>
  <P><I>(This is a demo, so your entry has been erased again.)</I></P>
</CFIF>

<HR>
<FORM ACTION="ch5_guestbook.cfm" METHOD="POST">
<INPUT TYPE="hidden" NAME="Name_required" VALUE="Please enter your name.">
Name: <INPUT TYPE="text" NAME="Name" SIZE="25" MAXLENGTH="50">
E-mail: <INPUT TYPE="text" NAME="Email" SIZE="25" MAXLENGTH="60"><BR>
Comments:<BR>
<TEXTAREA NAME="Comments" ROWS="4" COLS="50" WRAP="virtual"></TEXTAREA><BR>
<INPUT TYPE="submit" VALUE="Sign the guest book">
</FORM>
