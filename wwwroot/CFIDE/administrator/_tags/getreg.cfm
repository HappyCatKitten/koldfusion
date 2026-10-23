<!--- <cfmodule template="/CFIDE/administrator/_tags/getreg.cfm" key="Server" variable="S">
      loads every value under the key into a structure in the caller --->
<cfparam name="Attributes.key" default="Server">
<cfparam name="Attributes.variable" default="reg">
<cfregistry action="getall" branch="#Request.reg#\#Attributes.key#" name="r" type="any">
<cfset s = StructNew()>
<cfloop query="r"><cfif r.Type NEQ "Key"><cfset s[r.Entry] = r.Value></cfif></cfloop>
<cfset SetVariable("Caller.#Attributes.variable#", s)>
