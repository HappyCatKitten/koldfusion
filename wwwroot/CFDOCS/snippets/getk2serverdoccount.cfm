<CFSET Used = GetK2ServerDocCount()>
<CFSET Limit = GetK2ServerDocCountLimit()>
<CFOUTPUT>
<P>#NumberFormat(Used)# of #NumberFormat(Limit)# documents indexed
(#DecimalFormat(Used * 100 / Limit)#% of the limit).</P>
</CFOUTPUT>
