<!---
	widgets/gridlink.cfm - target of the browse grid's links.
	The grid appends CFGRIDKEY (the HREFKEY column, Room_ID) to the URL.
--->
<CFPARAM NAME="URL.CFGRIDKEY" DEFAULT="0">
<CFLOCATION URL="/CFDOCS/exampleapp/GlobalCorp/scheduler/room.cfm?Room_ID=#Val(URL.CFGRIDKEY)#" ADDTOKEN="No">
