<CFSET Text = "KoldFusion makes it easy to build dynamic Web applications that run equally well on a 56K modem and a T1 line.">
<CFOUTPUT>
<P>Wrapped at 30 characters:</P>
<PRE>#Wrap(Text, 30)#</PRE>
<P>Wrapped at 50 characters:</P>
<PRE>#Wrap(Text, 50)#</PRE>
</CFOUTPUT>
