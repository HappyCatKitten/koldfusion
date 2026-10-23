# KoldFusion research notes (condensed)

Sources: CF 4.5 "Administering the ColdFusion Server" manual (assocsrv.ca/CFDOCS mirror),
CF 4.5 release notes, Forta CF4 WACK ch.4 screenshots (ptgmedia.pearsoncmg.com/images/078971809X/updates/),
Lucee CFMXCompat.java/UUCoder.java, node-cf-encrypt, Synacktiv "CFMX_COMPAT lolcryption",
evolt.org 2001 captured CF 4.x error page, cfdocs.org/cf45.

## Admin nav (4.5 = 4.0 nav + Caching, Locking, Java, Source Control)
- server: Settings, Caching, Basic Security, Advanced Security, Variables, Locking, Mappings, Java, Version Info
- datasources: ODBC, Native Drivers, OLE DB, Verify Data Source
- extensions: CFX Tags, Applets
- logging: Settings, Mail Logging, Log Files
- automated tasks: Settings, Scheduled Tasks
- miscellaneous: Mail, Debugging, Verity, Source Control

## Look
- Frameset. Nav ~145px; nav bg 1px horizontal pinstripes #006699/#99CC99 (band ~27px left, ~20px top);
  section headers #003399 white bold lowercase Arial; link area #99CC99, links #0000FF underlined font size=1.
- Content: white; logo top-right; title bold black ~14pt; bold labels, help text size=2 beneath.
- Tables: header row #669966 white bold; rows alternate #FFFFFF / #FFFBF0; names bold underlined links; visited #336633.
- Grey form buttons; Apply/Cancel under <HR>. Paths in Courier.
- Status pages: red centred message between HRs + "Go Back" button,
  e.g. "The connection to the data source was verified successfully."
- Login: bg #99CC99, centred white card ~580x420, navy #333399 swoosh on right, footer bar #000066
  "Copyright 1995-1999, Allaire Corporation"; password field + button labelled "Password"; text
  "In order to access the administrative functions on this ColdFusion server you need to login using the administrator password."
  Window titles: "ColdFusion Administrator Login" / "ColdFusion Administrator".

## Pages (field labels, defaults)
Settings ("Server Settings"): Limit simultaneous requests to [5/15]; [x] Timeout requests after [30] seconds;
[x] Restart at [10] unresponsive requests; [x] Restart when requests terminate abnormally; Enforce strict attribute
validation; Suppress whitespace by default; Missing Template Handler; Site-wide Error Handler; restart needed note.
Caching: Template cache size [1024] KB; Trusted cache; Limit database connection inactive time [60] min; Limit max cached queries [100].
Basic Security ("Basic Server Security"): [x] Use a ColdFusion Administration Password + New Password/Confirmation;
[x] Use a ColdFusion Studio Password + New/Confirm; Tag Restrictions checkboxes CFCONTENT CFDIRECTORY CFFILE CFOBJECT
CFREGISTRY CFADMINSECURITY CFEXECUTE (checked = enabled); Unsecured Tags Directory (default admin dir).
Advanced Security: Use Advanced Server Security; Security Server 127.0.0.1; Shared Secret; ports; caches; admin/studio
authentication; sandbox security; buttons User Directories / Security Contexts / Security Sandboxes / Resources / Map.
User directory: Name, Namespace (Windows NT/LDAP/ODBC), Location, Username, Password... Context: name, description, rules, policies.
Variables: Client Variable Storage table (Name|Type; Registry=System Registry; add DSN select + Add...);
Default Client Variable Storage select (Registry/Cookie/DSNs); Session and Application Variables: Enable application
variables, Enable session variables, Maximum/Default timeout (days hrs mins secs) app 2 days, session 20 min.
Create client storage: Purge data for clients unvisited for [90] days; Disable global client variable updates; Create Client database tables.
Locking: Server/Application/Session scope radios: No automatic checking or locking / Full checking / Automatic read locking; session + Single threaded sessions.
Mappings ("Add New Mapping"): Logical Path [/], Directory Path + Browse Server..., Add Mapping/Cancel; table Logical Path | Directory Path.
Java: JVM Path, Class Path, Initial Heap Size, Max Heap Size, System Options, Implementation Options, CFX Jar Path.
Version Info: Server Product, Version, Edition, Serial Number, Operating System, OS Version, Additional Information, Build Number.
ODBC ("ODBC Data Sources Available to ColdFusion", Verify All): Data Source Name | ODBC Driver | Verify; add row text+driver select+Add...
 edit: DSN, Description, Database File+Browse, System Database, Page Timeout(600), Buffer Size(0), Login Name, Password, Create/Update/Delete, "CF Settings >>":
 Login Timeout(30), Limit Connections [ ], ColdFusion Login Username/Password, Maintain database connections, Disable Database Connections,
 Connection timeout, Restrict SQL Operations (SELECT INSERT UPDATE DELETE SP), Enable retrieval of long text, Long Text Buffer Size 65000.
Native Drivers ("Native Database Interface Data Sources Available to ColdFusion"): drivers Sybase11, Oracle73, Oracle80, Informix9, DB2; Host String.
OLE DB ("OLEDB Data Sources Available to ColdFusion"): provider free text e.g. SQLOLEDB, Microsoft.Jet.OLEDB.3.51.
Verify Data Source: Data Source Name | ODBC Driver | Status, Verify All.
CFX Tags ("Registered CFX Tags"): Tag name | Description; New CFX Tag: Tag name, Server library (DLL)+Browse, Procedure [ProcessTagRequest],
 [x] Keep library loaded, Description; 4.5 adds Java CFX (Class Name).
Applets ("Registered Applets"): Applet | Code | Codebase | Method; Register New Applet...: Codebase, Code, Method, Height, Width, VSpace,
 HSpace, Align, Java Not Supported Message, Parameter Name/Value rows.
Logging Settings ("General Error Logging"): Administrator E-Mail; Log Directory C:\CFUSION\LOG; Log Slow Pages taking longer than [30] seconds (to server.log); System Logging (syslog).
Mail Logging: Error Log Severity (Error/Warning/Information); Log all email messages sent by ColdFusion.
Log Files ("Log Files (C:\CFUSION\LOG)"): File Name | Size | Last Modified | Attributes; viewer w/ Download/Delete.
 logs: application.log server.log webserver.log schedule.log rdsservice.log customtag.log exec.log remote.log mail.log mailsent.log
Scheduler Settings: Scheduler Refresh Interval [15] minutes; log scheduled task activity.
Scheduled Tasks: Task Name | Operation | Duration | Interval; add: name, operation HTTPRequest, "Add New Task..."; RUN link.
 Add Scheduler Task: Duration Start Date/End Date; One-time at time; Recurring Daily/Weekly/Monthly at time; Daily every N minutes start/end time;
 URL, Username, Password, Request Time out, Proxy server, Publish: Save output to a file, File, Resolve URL.
Mail ("Mail Server Connection Settings"): Mail Server, Server Port 25, Connection Timeout 60; Apply/Verify/Cancel.
Debugging ("Debug Settings"): Enable performance monitoring; Enable CFML stack trace; Show variables; Show processing time (Detail View);
 Show SQL and data source name; Show query information; Display the template path in error messages;
 Restrict debug output to selected IP addresses (IP add/remove list).
Verity ("Verity Collections"): list box; Index..., Repair, Optimize, Purge, Delete; Add a Collection: Name, Path, Language English, Create/Map.
 Index form: File Extensions .htm, .html, .cfm, .cfml; Directory Path; Recursively index sub directories; Return URL; Language.
Source Control: Path to SrcSafe.ini, Working directory, Operation Timeout.

## Crypto
CFMX_COMPAT (legacy Encrypt/Decrypt) — 3-register generator. Key schedule: empty key -> "Default Seed"; seed buffer
len max(12,len) padded by self-repetition; A=B=C = big-endian of seed[4..7] (init constants A0=0x13579BDF,
B0=0x2468ACE0, C0=0xFDB97531 used only if 0). Per byte: b=B&1, c=C&1; 8 times:
 if A&1: A=(A^0x40000031)|0x80000000; if B&1: B=(B^0x20000010)|0xC0000000,b=1 else B=(B>>1)&0x3FFFFFFF,b=0
 else:   A=(A>>1)&0x7FFFFFFF;         if C&1: C=(C^0x08000001)|0xF0000000,c=1 else C=(C>>1)&0x0FFFFFFF,c=0
 crypto=((crypto<<1)|(b^c))&0xFF.  out=in^crypto.
Output uuencoded: lines of <=45 bytes, first char 32+n, groups 32+(6bit) (space variant), '\n' after each line.
Golden vector: Encrypt("text","key") = "$38YC!P  \n" (hex 4D8E6307).
Hash(): MD5, 32 uppercase hex (new in 4.5).
Admin password: registry Server\UseAdminPassword (1/0), AdminPassword stored obfuscated ("cannot be read back").
User choice for KoldFusion: "fully authentic" weak scheme everywhere -> store with CFMX_COMPAT + fixed key.

## Error page (real CF 4.x capture)
Error Diagnostic Information
An error occurred while evaluating the expression:
    <expr>
Error near line 73, column 36.
<hr>
Error resolving parameter GETARTICLE.USERID
ColdFusion was unable to determine the value of the parameter. This problem is very likely due to the fact that either:
1. You have misspelled the parameter name, or
2. You have not specified a QUERY attribute for a CFOUTPUT, CFMAIL, or CFTABLE tag.
The error occurred while processing an element with a general identifier of (CFIF), occupying document position
(73:10) to (73:88) in the template file /path/dsp_sidebar.cfm.
Date/Time: Wed Jul 25 16:07:46 2001
Browser: Mozilla/4.0 (compatible; MSIE 5.0; Mac_PowerPC)
Remote Address: 62.31.77.8
HTTP Referer: http://...
Query String:

## Logs
Quoted CSV: "Severity","ThreadID","Date","Time","Details" (4.5 exact delimiter unverified; CF5 added "Application").

## Language
4.5 tags incl. CFSILENT, CFEXECUTE, CFQUERYPARAM, CFMAILPARAM, CFRETHROW, CFPROCESSINGDIRECTIVE, CFSERVLET (new in 4.5).
Not in 4.5: CFDUMP, CFSAVECONTENT, CFFLUSH, CFFUNCTION/UDFs, CFLOG? (CF5), == / && (CFMX).
New 4.5 functions: CreateObject, Duplicate, GetFunctionList, GetHTTPTimeString, GetMetricData, Hash, IsBinary,
JavaCast, JSStringFormat, ToBase64, ToBinary, ToString, URLDecode, XMLFormat.
CreateUUID: 8-4-4-16 hex (35 chars). CFID sequential integer; CFTOKEN 8-digit random.
Server.ColdFusion.ProductVersion "4, 5, 1, 0"-style; ProductName "ColdFusion Server"; ProductLevel "Enterprise".

## Shipped samples (from memory of research agent, unverified)
/CFDOCS/index.htm welcome; /CFDOCS/dochome.htm docs index; /CFDOCS/snippets/ (one example per tag/function,
DSN cfsnippets: Employees(Emp_ID, FirstName, LastName, Email, Phone, Department, StartDate, Salary, Contract),
Departments(Dept_ID, Dept_Name), CourseList(Course_ID, Dept_ID, CorNumber, CorName, CorLevel, CorDesc, LastUpdate),
Parks(ParkName, ParkType, Region, State, City)); /CFDOCS/exampleapp/ (email via CFPOP, publish admin, docs sourcewindow);
/CFDOCS/examples/parks/detail.cfm (National Parks drill-down); /CFDOCS/expeval/ExprCalc.cfm (the infamous 1999
Expression Evaluator, ASB99-01); /CFIDE/scripts/cfform.js; /CFIDE/classes/ (applet jars).

## Corpus
Scratch copy: <scratchpad>/cfml-corpus/<source>/ with SOURCE.txt (URL, author, licence).
rosettacode (GFDL), balancetags (GPL), btg-contacts (GPL-3, DSN btg), cfwebstore-pagethru (GPL-3),
tonyjunkes-cf-calendar (MIT), footballmitoo-eventcalendar (MIT, DSN table event), learnxinyminutes (CC BY-SA),
wikipedia-cfml (CC BY-SA), leachim6-hello-world (MIT).
Idea: CFCRYPT-encrypted templates (github.com/disccomp/cfdecrypt documents format) - fun extra.

## Verified sample-content details (assocsrv.ca/CFDOCS mirror, 3gpp2.org CF4 mirror)
Welcome /CFDOCS/index.htm "Welcome to ColdFusion Server 4.5": bgcolor #99CC99 + tile bgblue.gif (191x4, alternating
1px rows #006699 / #99CC99 = pinstripes); centred 640px navy (000066) frame table around white table: 51px blank left
gutter, 52px right column solid #003399, 400x105 logo; intro + "Register today"; two columns of bold link groups:
Installation (Test your Installation testinstallation/test.cfm), Product Support, Registration, Documentation (Release
Notes, New Features in 4.5, Product Documentation dochome.htm, Example Applications examplehome.cfm, CFML Syntax Checker),
Administration (Server Administrator), Online Resources; right column Contact; footer white -2 Arial "Copyright 1995-2000".
dochome.htm: 16x16 nav icons (back uplevel next home search), logo, rule, H1, four books as H4 links + blockquote blurbs.
Doc CSS: Verdana/Arial 12px, bg #FFFFF0 ivory, PRE Courier New maroon, headings hang left; Language Reference entries
have Syntax PRE, attribute paragraphs, Example, and a form button "Example" -> tagframe.cfm (frameset: header,
viewexample source | runexample output; localhost only).
cfsnippets tables: Employees(Emp_ID, FirstName, LastName, Email, Phone, Department), Courses(Course_ID, Number, Descript),
CourseList(Course_ID, Dept_ID, CorNumber, CorName, CorLevel, CorDesc), Parks(ParkName, Region, State, City),
Messages(Message_ID, Username, Subject, Posted), Comments(CommentID, Email, FromUser, Subject, CommtType, MessText, Posted, Processed).
DSNs in 4.5: cfexamples, cfsnippets. CompanyInfo: Employees(Employee_ID, FirstName, LastName, Department_ID, StartDate,
Salary, Contract), Departments(Department_ID, Department_Name, Location) (Training, Marketing, HR, Sales; Arlington, Boston...).
Example apps: GlobalCorp intranet (directory, threaded discussion, product catalog, meeting room scheduler),
HRApp "Human Resources Employee Manager" (EmpList, Search, Insert, Update; toolbar #003399 table, title #CCCCCC +2, white bold links).
Admin frameset title "ColdFusion Administrator"; leftbgblue.gif 200x4: ~121px teal/green pinstripe, 1px #330033, 1px #0099CC,
then white; right.htm bgcolor #ccFFcc; bluecurve.gif #333399; fistbg.gif faint grey watermark.
Forta CF4 WACK used "A2Z" database; CF5 WACK used Orange Whip Studios (ows).
