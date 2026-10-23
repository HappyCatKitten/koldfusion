<cfsetting enablecfoutputonly="yes">
<cfoutput>#10/4#|#7 MOD 3#|#2^10#|#7 \ 2#|#Round(2.5)#|#1 EQ 1#|#"abc" IS "ABC"#|#"abc" CONTAINS "B"#|#5 GT 3 AND 2 LT 1#|#NOT false#|#"a" & 1 + 2#|#1/3#|#-7 MOD 3#|#3 XOR 0#|#1 IMP 0#|#2 EQV 2#|#007#|#"10" + "5"#|#1E3#|#Len(12345)#
</cfoutput>
<cfset x = 5><cfset x = x * 2 + 1><cfset s = "x is #x#"><cfoutput>#s#|#IIf(x GT 10, DE("big"), DE("small"))#|#Evaluate("x + 1")#
</cfoutput>
