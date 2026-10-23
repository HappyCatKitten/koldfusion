<CFSCRIPT>
  speeds = "14.4,28.8,33.6,56";
  WriteOutput("<TABLE BORDER=1 CELLPADDING=3>");
  WriteOutput("<TR><TH>Modem (Kbps)</TH><TH>1 MB download</TH></TR>");
  for (i = 1; i LTE ListLen(speeds); i = i + 1) {
    kbps = ListGetAt(speeds, i);
    seconds = Round(8 * 1024 / kbps);
    WriteOutput("<TR><TD>" & kbps & "</TD><TD>" & Int(seconds / 60) & " min " & (seconds MOD 60) & " s</TD></TR>");
  }
  WriteOutput("</TABLE>");
</CFSCRIPT>
