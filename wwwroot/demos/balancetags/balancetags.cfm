<!--- KoldFusion Demo Gallery companion file (not part of the original balanceTags repo).
      callstag.cfm invokes <CF_balanceTags>, but the repo ships the custom tag as
      cfml_version_balancer.cfm. This one-line shim lets the CF_ lookup find it,
      leaving the original file untouched. --->
<cfinclude template="cfml_version_balancer.cfm">
