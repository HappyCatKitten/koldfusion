<CFIF IsDefined("Form.Callsign")>
  <CFOUTPUT><P>Welcome aboard, <B>#HTMLEditFormat(Form.Callsign)#</B>
  (#Form.Hours# hours online this week).</CFOUTPUT>
</CFIF>

<CFFORM NAME="Pilot" ACTION="cftextinput.cfm">
<P>Screen name:
<CFTEXTINPUT NAME="Callsign" VALUE="WebSurfer99" SIZE="20" MAXLENGTH="16"
    FONT="Courier New" FONTSIZE="11" BOLD="Yes"
    BGCOLOR="Navy" TEXTCOLOR="Yellow"
    REQUIRED="Yes" MESSAGE="Every pilot needs a screen name.">
<P>Hours online per week:
<CFTEXTINPUT NAME="Hours" VALUE="40" SIZE="4" VALIDATE="integer"
    RANGE="0,168" ITALIC="Yes" MESSAGE="A week has only 168 hours.">
<P><INPUT TYPE="Submit" VALUE="Sign on">
</CFFORM>
