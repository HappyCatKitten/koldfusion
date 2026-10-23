# KoldFusion engine notes (for page authors)

KoldFusion is a C re-creation of an Allaire ColdFusion 4.5 server. Pages are CFML 4.5.

## Build and run
- `make` builds `bin/kfserver` and the CFX libraries in `kfroot/cfx/`.
- `./bin/kfserver` serves on http://127.0.0.1:8500/ (`-p PORT` changes the port, `-b ADDR` the bind address), and on
  https://127.0.0.1:8543/ when OpenSSL can be loaded (`--ssl-port PORT` changes it, `--ssl-port 0` turns it off).
- `./bin/kfserver --run wwwroot/path/page.cfm [query-string]` renders one page to stdout (HTTP headers first) — the fastest way to test.
- Administrator: /CFIDE/administrator/ (default password `admin`).
- Install directory ("C:\CFUSION"): `kfroot/` — registry in `kfroot/registry/kf.registry` (REGEDIT4 format), logs in `kfroot/log/`,
  data sources in `kfroot/db/<name>/` (one `.tbl` text file per table), seed scripts in `kfroot/seed/<dsn>.sql` (run once, the
  first time the server starts and the db directory does not exist yet — delete `kfroot/db/<dsn>` to re-seed).
- Virtual sites: `http://<name>.localhost:PORT/` serves `wwwroot/sites/<name>/` (any other host gets `wwwroot/`). A
  site without its own `/CFIDE/` or `/images/` file falls back to the main web root's. A request for a missing
  `/<othersite>/...` path is redirected to `http://<othersite>.localhost:PORT/...`, and any other missing path the main
  site has (e.g. `/web1999/`) to `http://localhost:PORT/...`, so sites can link to each other with relative paths.
- Every `kfroot/seed/<dsn>.sql` whose first line is `-- DSN: description` is registered as a data source automatically.
- Web root: `wwwroot/`. Custom tags: same directory as the caller, or anywhere under `kfroot/customtags/`.

## Web server (http.c, netio.c, tls.c, httpc.c)
- HTTP/1.1 with persistent connections and pipelining (HTTP/1.0 clients get keep-alive when they send
  `Connection: keep-alive`), chunked request bodies, `Expect: 100-continue`, HEAD, exact Content-Length on every
  response, `Last-Modified`/`ETag` and 304 for static files (the zoom setting is part of the validator). Settings:
  Administrator > Web Server & SSL (registry `Server\KeepAlive*`, `HeaderTimeout`, `MaxConnections`).
- One thread per connection; each request gets a fresh arena, and per-thread engine state is reset between requests
  (`*_thread_reset()` in netio.h) - new `__thread` state in the engine must be reset there too.
- Every socket read/write has a deadline (headers and SSL handshake: `HeaderTimeout`, 20 s; idle keep-alive: 15 s;
  bodies: 30 s + 1 s per 64 KB), so slowloris-style clients are dropped with 408.
- SSL: libssl/libcrypto are `dlopen()`ed at run time (3, 1.1, then unversioned; `KF_LIBSSL=none` pretends they are
  missing, `KF_LIBSSL=/path/libssl.so.X` picks one). No OpenSSL headers or link-time dependency. The first start makes
  `kfroot/ssl/kfserver.crt`/`.key` with `/usr/bin/openssl` (CN=localhost, O=Gibson Mainframe Co., SANs localhost,
  *.localhost, 127.0.0.1 and each virtual site); `kfroot/ssl/<host>.crt`/`.key` are served by SNI.
- Over SSL: `CGI.HTTPS` = on, `CGI.SERVER_PORT_SECURE` = 1, `CGI.SERVER_PORT` = the SSL port, and the IIS 4
  `CGI.CERT_*` / `CGI.HTTPS_*` variables (KEYSIZE, SECRETKEYSIZE, SERVER_SUBJECT, SERVER_ISSUER, client SUBJECT,
  ISSUER, SERIALNUMBER, COOKIE, FLAGS). Build self-referencing URLs with the scheme from `CGI.HTTPS`.
- CFHTTP: http:// and https://, HTTP/1.1, chunked responses, PORT, PROXYSERVER/PROXYPORT (CONNECT for https),
  USERNAME/PASSWORD, RESOLVEURL, REDIRECT (up to 4), TIMEOUT (whole request), THROWONERROR, USERAGENT, and the
  KoldFusion extra `CHECKCERTIFICATE="No"`. Certificates are verified against the system CA store plus KoldFusion's own
  certificate. A header received twice (Set-Cookie) is an array in `CFHTTP.ResponseHeader`.

## Data sources
cfsnippets, exampleapp, btg, cfexamples, CompanyInfo, demos (all served by the built-in flat-file SQL engine:
SELECT/INSERT/UPDATE/DELETE, joins, GROUP BY, ORDER BY, TOP/LIMIT, subqueries, LIKE, IN, BETWEEN, COUNT/SUM/AVG/MIN/MAX,
CREATE/DROP/ALTER TABLE, COUNTER autoincrement columns, `SELECT @@IDENTITY`, Access `#date#` and ODBC `{d '...'}` literals).
Seed SQL scripts: statements separated by `;`, `--` comments, start with `DROP TABLE IF EXISTS`.

## Tags
cfset cfoutput (query/group/startrow/maxrows) cfif/cfelseif/cfelse cfloop (index/from/to/step, condition, query, list,
collection) cfbreak cfabort cfexit cfparam cfinclude cfmodule cfassociate cfswitch/cfcase/cfdefaultcase cftry/cfcatch
cfthrow cfrethrow cfscript cfsetting cfsilent cfprocessingdirective cflocation cfcookie cfheader cfcontent cfhtmlhead
cfapplication (session/client/application) cflock cferror cfcache (page caching to disk) cfquery (cachedwithin, maxrows) cfqueryparam
cftransaction cfinsert cfupdate cfstoredproc(error) cfmail/cfmailparam (spooled to kfroot/mail/spool) cffile (upload, read,
readbinary, write, append, copy, move, rename, delete) cfdirectory cfregistry cfhttp/cfhttpparam (http:// and https://) cfschedule
cfexecute cfwddx cfpop cfftp (passive-mode client) cfldap(error) cfobject(error) cfservlet(error) cfreport(error) cfindex cfsearch
cfcollection cfauthenticate cfimpersonate cfform cfinput cfselect cftextinput cfslider cfgrid/cfgridcolumn/cfgridrow/
cfgridupdate cftree/cftreeitem cfapplet cftable/cfcol, custom tags (cf_name, cfmodule; Attributes/Caller/ThisTag),
CFX tags (cfx_hello, cfx_dice, cfx_sysinfo).

Not in 4.5 and therefore not supported: CFDUMP, CFSAVECONTENT, CFFLUSH, CFFUNCTION/CFCOMPONENT/CFINVOKE/CFRETURN, CFLOG,
user-defined functions in CFSCRIPT, query-of-queries (DBTYPE="query"), array/struct literals `[]` `{}`.
CFSCRIPT accepts `==`, `!=`, `<`, `&&`, `++`, `+=` as a convenience, but tag expressions use EQ, NEQ, LT, GT, AND, OR, NOT.

## Functions
Abs ACos ArrayAppend ArrayAvg ArrayClear ArrayDeleteAt ArrayInsertAt ArrayIsEmpty ArrayLen ArrayMax ArrayMin ArrayNew
ArrayPrepend ArrayResize ArraySet ArraySort ArraySum ArraySwap ArrayToList Asc ASin Atn BitAnd BitMaskClear BitMaskRead
BitMaskSet BitNot BitOr BitSHLN BitSHRN BitXor Ceiling Chr CJustify Compare CompareNoCase Cos CreateDate CreateDateTime
CreateObject CreateODBCDate CreateODBCDateTime CreateODBCTime CreateTime CreateTimeSpan CreateUUID DateAdd DateCompare
DateConvert DateDiff DateFormat DatePart Day DayOfWeek DayOfWeekAsString DayOfYear DaysInMonth DaysInYear DE DecimalFormat
DecrementValue Decrypt DeleteClientVariable DirectoryExists DollarFormat Duplicate Encrypt Evaluate Exp ExpandPath
FileExists Find FindNoCase FindOneOf FirstDayOfMonth Fix FormatBaseN GetBaseTagData GetBaseTagList GetBaseTemplatePath
GetClientVariablesList GetCurrentTemplatePath GetDirectoryFromPath GetFileFromPath GetFunctionList GetHTTPTimeString
GetLocale GetMetricData GetProfileString GetTempDirectory GetTempFile GetTemplatePath GetTickCount GetTimeZoneInfo
GetToken Hash Hour HTMLCodeFormat HTMLEditFormat IIf IncrementValue InputBaseN Insert Int IsArray IsAuthenticated
IsAuthorized IsBinary IsBoolean IsDate IsDebugMode IsDefined IsLeapYear IsNumeric IsNumericDate IsProtected IsQuery
IsSimpleValue IsStruct IsWDDX JavaCast JSStringFormat LCase Left Len ListAppend ListChangeDelims ListContains
ListContainsNoCase ListDeleteAt ListFind ListFindNoCase ListFirst ListGetAt ListInsertAt ListLast ListLen ListPrepend
ListQualify ListRest ListSetAt ListSort ListToArray ListValueCount ListValueCountNoCase LJustify Log Log10 LS* LTrim Max Mid
Min Minute Month MonthAsString Now NumberFormat ParagraphFormat ParameterExists ParseDateTime Pi PreserveSingleQuotes
Quarter QueryAddColumn QueryAddRow QueryNew QuerySetCell QuotedValueList Rand Randomize RandRange REFind REFindNoCase
RemoveChars RepeatString Replace ReplaceList ReplaceNoCase REReplace REReplaceNoCase Reverse Right RJustify Round RTrim
Second SetLocale SetProfileString SetVariable Sgn Sin SpanExcluding SpanIncluding Sqr StripCR StructAppend StructClear
StructCopy StructCount StructDelete StructFind StructGet StructInsert StructIsEmpty StructKeyArray StructKeyExists
StructKeyList StructNew StructUpdate Tan TimeFormat ToBase64 ToBinary ToString Trim UCase URLDecode URLEncodedFormat Val
ValueList Week Wrap WriteOutput XMLFormat Year YesNoFormat.
`KFUSION_CHECKSYNTAX(code)` (struct OK, Message, Detail, Line, Column) works anywhere; other KFUSION_* functions are
Administrator-only.

## CFML gotchas (all authentically 4.5)
- Variable names are case-insensitive: `<cfloop index="t">` overwrites a struct named `T`.
- Inside CFOUTPUT every `#` starts an expression: write `bgcolor="##FFFFFF"`.
- `IIf()` evaluates the chosen *string* as an expression — use `DE()` for literal strings, and never nest IIf.
- Comparison results print as YES/NO. Numbers print without trailing zeros.
- `Form.FieldNames`, hidden `field_required` / `_integer` / `_float` / `_range` / `_date` validation fields work.
- Only `Application.cfm` in the template's directory or a parent (up to the web root) is run, plus `OnRequestEnd.cfm`.
- CFLOCATION ends the request (OnRequestEnd.cfm does not run).

## 1999 house style
HTML 3.2/4.0 only: `<FONT FACE="Arial, Helvetica" SIZE="2">`, layout tables, BGCOLOR/BACKGROUND attributes, `<CENTER>`,
GIFs (see `wwwroot/images/` and `wwwroot/CFIDE/administrator/images/`), JavaScript 1.2 style (`var`, `document.forms`),
no CSS frameworks, no modern JS. Product name "KoldFusion" by "Gibson"; never copy original Allaire/Macromedia text verbatim.

## Compatibility leniencies (things real 4.5 was stricter or different about)
- XHTML-style `<cfset x = 1 />` and `<cfinclude ... />` closers (CFMX syntax) are accepted.
- File names are resolved case-insensitively, like on Windows NT (`<CFINCLUDE TEMPLATE="Header.CFM">`, `<CF_MyTag>`,
  static URLs).
- DOS paths work: `C:\CFUSION\...` maps to `kfroot/`, `C:\Inetpub\wwwroot\...` and `C:\CFUSION\wwwroot\...` to the web
  root, any other `X:\path` to `kfroot/drive_x/path` (`C:\TEMP` exists).
- A local variable may shadow a scope name (`<cfset attributes = "">`): bare references see the variable, dotted
  references (`attributes.text`) still reach the scope — as in ColdFusion 4.0.
- `Evaluate("")` and `IIf(cond, "", ...)` return an empty string.
- Two date strings compare as dates with EQ/LT/GT (`"10/22/1999" EQ "1999-10-22"` is YES).
- Inside CFQUERY, single quotes in #expressions# are doubled, except for the SQL-building functions
  (PreserveSingleQuotes, QuotedValueList, ListQualify, CreateODBCDate/Time/DateTime) and ODBC
  date/time values such as `#CreateODBCDate(Now())#`.
