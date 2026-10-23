<!---
  hanoi_move.cfm - custom tag used by hanoi.cfm. CFML 4.5 has no user-defined
  functions, but a custom tag can call itself with CFMODULE, which gives us
  honest-to-goodness recursion:

     to move N disks from A to C:  move N-1 from A to B, move disk N A->C,
                                   move N-1 from B to C.

  Each move is appended to the Request.hanoiMoves array as "disk,from,to".
  Attributes: N, FROM, TO, VIA. KoldFusion Demo Gallery original - MIT licence.
--->
<cfif ThisTag.ExecutionMode IS "end"><cfexit method="exittag"></cfif>
<cfif Attributes.n GT 0>
	<cfmodule template="hanoi_move.cfm" n="#Attributes.n - 1#" from="#Attributes.from#" to="#Attributes.via#" via="#Attributes.to#">
	<cfset ArrayAppend(Request.hanoiMoves, "#Attributes.n#,#Attributes.from#,#Attributes.to#")>
	<cfmodule template="hanoi_move.cfm" n="#Attributes.n - 1#" from="#Attributes.via#" to="#Attributes.to#" via="#Attributes.from#">
</cfif>
