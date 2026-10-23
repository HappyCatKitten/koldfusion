<CFSET N = 1234.567>
<CFOUTPUT>
<PRE>
Mask           Result
(none)         [#NumberFormat(N)#]
9,999.99       [#NumberFormat(N, "9,999.99")#]
99999.9        [#NumberFormat(N, "99999.9")#]
L99999.9       [#NumberFormat(N, "L99999.9")#]
000000         [#NumberFormat(42, "000000")#]
$999,999.99    [#NumberFormat(N, "$999,999.99")#]
(9,999.99)     [#NumberFormat(-N, "(9,999.99)")#]
+9999          [#NumberFormat(42, "+9999")#]
-9999          [#NumberFormat(-42, "-9999")#]
</PRE>
</CFOUTPUT>
