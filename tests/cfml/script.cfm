<cfsetting enablecfoutputonly="yes">
<cfscript>
fib = ArrayNew(1); fib[1] = 1; fib[2] = 1;
for (i = 3; i LTE 10; i = i + 1) fib[i] = fib[i-1] + fib[i-2];
s = StructNew(); s.one = 1; s.two = 2; keys = "";
for (k in s) keys = ListAppend(keys, k);
n = 0; while (n LT 5) { n = n + 1; if (n EQ 3) continue; }
do { n = n - 1; } while (n GT 2);
switch ("b") { case "a": r = "A"; break; case "b": case "c": r = "BC"; break; default: r = "?"; }
WriteOutput(ArrayToList(fib) & "|" & ListSort(keys, "text") & "|" & n & "|" & r);
</cfscript>
<cfoutput>
</cfoutput>
