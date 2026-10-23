<!--- KoldFusion Demo Gallery: mechanical CF 4.5 port of index.cfm (the original sits next to this file, unchanged).
      Change: XHTML-style self-closing CF tags ("<cfset x = 1 />") were removed - that syntax arrived with
      ColdFusion MX and CF 4.5 reads the trailing "/" as a division operator. Also: CFMODULE points at cf-calendar_cf45port.cfm and the stylesheet link at the saved cf-calendar.css (jQuery files were not saved).
      All credit and the original licence (see SOURCE.txt) belong to the original author. --->
<!DOCTYPE html>

<html lang="en-us">

   <head>
      <meta charset="utf-8" />
      <title>CFCalendar - Simple, quick and dirty calendar layout in ColdFusion</title>
      <link href="css/jquery-ui-1.8.16.custom.css" type="text/css" rel="stylesheet" />
      <link href="cf-calendar.css" type="text/css" rel="stylesheet" />
      <script type="text/javascript" src="js/jquery-1.7.1.min.js"></script>
      <script type="text/javascript" src="js/jquery-ui-1.8.16.custom.min.js"></script>
   </head>

   <body>
      <cfmodule template="cf-calendar_cf45port.cfm" callingPage="index_cf45port.cfm">
   </body>

</html>
