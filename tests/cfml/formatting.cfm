<cfsetting enablecfoutputonly="yes">
<cfset d = CreateDateTime(1999, 12, 31, 23, 59, 58)>
<cfoutput>#DateFormat(d)#|#DateFormat(d, "mmmm d, yyyy")#|#DateFormat(d, "ddd mm/dd/yy")#|#TimeFormat(d)#|#TimeFormat(d, "HH:mm:ss")#|#DateFormat(DateAdd("s", 2, d), "yyyy-mm-dd")#|#d#
</cfoutput>
<cfoutput>#DollarFormat(1234.5)#|#DollarFormat(-5)#|#NumberFormat(3.14159, "9.99")#|#NumberFormat(1234567)#|#DecimalFormat(2)#|#YesNoFormat(0)#|#HTMLEditFormat("<b>&")#|#URLEncodedFormat("a b")#|#ParagraphFormat("x")#
</cfoutput>
<cfoutput>#Encrypt("text", "key")#|#Hash("abc")#|#ToBase64("1999")#|#Len(CreateUUID())#
</cfoutput>
