<!--- KoldFusion Demo Gallery - application settings for everything under /demos/.
      Folders with their own Application.cfm (btg-contacts, footballmitoo-eventcalendar)
      use theirs instead; this one is the nearest for every other demo. Session
      variables power the Game of Life and Tic-Tac-Toe originals; Application
      variables hold the gallery hit counter. --->
<cfapplication name="KFDemoGallery"
	sessionmanagement="Yes"
	sessiontimeout="#CreateTimeSpan(0,0,30,0)#"
	applicationtimeout="#CreateTimeSpan(2,0,0,0)#">
