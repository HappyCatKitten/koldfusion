<!--- ch1_hello.cfm: a first KoldFusion template.
      Comments with three dashes are removed by the server
      and never reach the browser. --->
<HTML>
<HEAD><TITLE>Hello from KoldFusion</TITLE></HEAD>
<BODY BGCOLOR="#FFFFFF">
<FONT FACE="Arial, Helvetica" SIZE="2">

<H2>Hello, world!</H2>

<CFOUTPUT>
<P>Today is #DateFormat(Now(), "dddd, mmmm d, yyyy")#
and the server clock says #TimeFormat(Now(), "h:mm tt")#.</P>

<P>Only #DateDiff("d", Now(), CreateDate(2000, 1, 1))# days left
until the year 2000. (If that number is negative, congratulations:
you made it.)</P>

<!-- An HTML comment with two dashes is sent to the browser. -->
<P>Inside CFOUTPUT a literal pound sign is written twice: ##1 on the charts.</P>
</CFOUTPUT>

<P>Outside CFOUTPUT, #Now()# is just text.</P>
</FONT>
</BODY>
</HTML>
