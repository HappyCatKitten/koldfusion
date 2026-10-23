<CFSET Radius = 5>
<CFOUTPUT>
<P>Pi() = #Pi()#
<P>A circle with radius #Radius#:
<UL>
<LI>circumference #NumberFormat(2 * Pi() * Radius, "9.99")#
<LI>area #NumberFormat(Pi() * Radius ^ 2, "9.99")#
</UL>
<P>180 degrees = #Pi()# radians; 1 radian = #NumberFormat(180 / Pi(), "9.9999")# degrees
</CFOUTPUT>
