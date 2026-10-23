<!--- <cfmodule template="/CFIDE/administrator/_tags/setreg.cfm" key="Server" entry="X" value="Y"> --->
<cfregistry action="set" branch="#Request.reg#\#Attributes.key#" entry="#Attributes.entry#" value="#Attributes.value#" type="string">
