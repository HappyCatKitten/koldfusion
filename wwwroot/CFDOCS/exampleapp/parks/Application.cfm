<!---
	parks/Application.cfm - National Parks Finder
	Sets the data source and a lookup table of state names.
--->
<CFAPPLICATION NAME="NationalParksFinder" SESSIONMANAGEMENT="No">
<CFSET Request.DSN = "cfexamples">
<CFSET Request.PageSize = 5>
<CFSET Request.StateCodes = "AK,AR,AZ,CA,CO,FL,HI,KY,MD,ME,MI,MN,MT,NC,ND,NM,NV,NY,OR,PA,SD,TN,TX,UT,VA,VI,WA,WY">
<CFSET Request.StateNames = "Alaska,Arkansas,Arizona,California,Colorado,Florida,Hawaii,Kentucky,Maryland,Maine,Michigan,Minnesota,Montana,North Carolina,North Dakota,New Mexico,Nevada,New York,Oregon,Pennsylvania,South Dakota,Tennessee,Texas,Utah,Virginia,Virgin Islands,Washington,Wyoming">
