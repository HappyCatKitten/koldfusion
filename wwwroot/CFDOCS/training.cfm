<!--- /CFDOCS/training.cfm - Allair Education and Training (course catalog from the cfsnippets Courses table) --->
<cfset pageTitle = "Education and Training">
<cfset section = "training.cfm">
<cfparam name="URL.enroll" default="0">
<cfquery name="Courses" datasource="cfsnippets">
SELECT c.Course_ID, c.Number, c.Descript, d.Dept_Name
FROM Courses c, Departments d
WHERE c.Dept_ID = d.Dept_ID
ORDER BY c.Number
</cfquery>
<cfset Variables.cities = "Boston MA,Frostbite Falls MN,San Francisco CA,Chicago IL,Washington DC,Dallas TX,Seattle WA,London UK">
<cfinclude template="_siteheader.cfm">
<FONT FACE="Arial, Helvetica" SIZE=2>
<P>Allair Authorized Training gets you productive with KoldFusion fast. Our instructors are certified
KoldFusion developers who have seen every error message at least twice. Classes are small, hands-on,
and include lunch, a binder and a commemorative mug.</P>

<cfif Val(URL.enroll)>
	<cfquery name="Picked" datasource="cfsnippets">
	SELECT Number, Descript FROM Courses WHERE Course_ID = <cfqueryparam value="#Val(URL.enroll)#" cfsqltype="CF_SQL_INTEGER">
	</cfquery>
	<cfif Picked.RecordCount>
	<TABLE BORDER=0 CELLPADDING=8 CELLSPACING=0 BGCOLOR="#FFFFCC" WIDTH="100%"><TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>
	<cfoutput>
	<B>#Picked.Number#: you are on the list!</B><BR>
	Good news: there is a seat for you. Better news: you are number #RandRange(2, 9)# on the waiting list,
	which means the class is popular. Our registrar will contact you by fax. Please make sure your fax machine has paper.
	</cfoutput>
	</FONT></TD></TR></TABLE>
	</cfif>
</cfif>

<H3>Course catalog and schedule</H3>
<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=1 BGCOLOR="#999999" WIDTH="100%">
<TR BGCOLOR="#669966">
	<TH ALIGN=LEFT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF">Course</FONT></TH>
	<TH ALIGN=LEFT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF">Description</FONT></TH>
	<TH ALIGN=LEFT><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF">Next class</FONT></TH>
	<TH><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF">Days</FONT></TH>
	<TH><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF">Price</FONT></TH>
	<TH></TH>
</TR>
<cfoutput query="Courses">
	<!--- schedule: deterministic dates in late 1999 / early 2000 --->
	<cfset Variables.start = DateAdd("d", Courses.Course_ID * 11, CreateDate(1999, 11, 1))>
	<cfif DayOfWeek(Variables.start) EQ 1><cfset Variables.start = DateAdd("d", 1, Variables.start)></cfif>
	<cfif DayOfWeek(Variables.start) EQ 7><cfset Variables.start = DateAdd("d", 2, Variables.start)></cfif>
	<cfset Variables.days = (Courses.CurrentRow MOD 3) + 1>
	<cfif CurrentRow MOD 2><cfset Variables.bg = "FFFFFF"><cfelse><cfset Variables.bg = "FFFBF0"></cfif>
	<TR BGCOLOR="###Variables.bg#" VALIGN=TOP>
	<TD NOWRAP><FONT FACE="Arial, Helvetica" SIZE=2><B>#Number#</B></FONT><BR><FONT FACE="Arial, Helvetica" SIZE=1>#Dept_Name#</FONT></TD>
	<TD><FONT FACE="Arial, Helvetica" SIZE=2>#HTMLEditFormat(Descript)#</FONT></TD>
	<TD NOWRAP><FONT FACE="Arial, Helvetica" SIZE=1>#DateFormat(Variables.start, "ddd, mmm d, yyyy")#<BR>#ListGetAt(Variables.cities, (Courses.Course_ID MOD ListLen(Variables.cities)) + 1)#</FONT></TD>
	<TD ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=2>#Variables.days#</FONT></TD>
	<TD ALIGN=RIGHT NOWRAP><FONT FACE="Arial, Helvetica" SIZE=2>#DollarFormat(Variables.days * 495)#</FONT></TD>
	<TD><FONT FACE="Arial, Helvetica" SIZE=1><A HREF="training.cfm?enroll=#Course_ID#">Enroll</A></FONT></TD>
	</TR>
</cfoutput>
</TABLE>
<P><FONT FACE="Arial, Helvetica" SIZE=1>Prices in US dollars per student. Registered KoldFusion owners
receive 10% off; <A HREF="registration.cfm">register now</A>. Classes in Frostbite Falls include a free parka
from November through April.</FONT></P>

<H3>Allair Certified KoldFusion Developer</H3>
<P>Prove your skills with the certification exam: 60 multiple-choice questions, 90 minutes, no
<CODE>CFDUMP</CODE> allowed (it does not exist yet). Study tips:</P>
<UL>
<LI>Know when you need <CODE>##</CODE> signs and when you do not.
<LI>Know the difference between <CODE>StructCopy</CODE> and <CODE>Duplicate</CODE>.
<LI>Lock every read and write of Session, Application and Server variables with <CODE>CFLOCK</CODE>.
<LI>Read <A HREF="devguide/index.htm">Developing Web Applications with KoldFusion</A> cover to cover. Twice.
</UL>

<H3>Self-paced learning</H3>
<P>Can't get away from the office? Work through the <A HREF="devguide/index.htm">online tutorial</A>,
try every example in the <A HREF="snippets/index.cfm">Snippets Launcher</A>, and practice expressions in the
<A HREF="expeval/ExprCalc.cfm">Expression Evaluator</A>. The CD-ROM edition of our video course runs on any
Pentium with a 4x CD-ROM drive and a sound card.</P>
</FONT>
<cfinclude template="_sitefooter.cfm">
