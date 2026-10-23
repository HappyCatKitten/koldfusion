<!---
	widgets/gridaction.cfm - saves the editable vendor grid.
	CFGRIDUPDATE reads the grid's form fields and works out the
	INSERT, UPDATE and DELETE statements by itself, finding rows by
	the table's primary key (Vendor_ID, a hidden grid column).
--->
<CFIF IsDefined("Form.__CFGRID__VendorGrid__ROWS") OR IsDefined("Form.VendorGrid.RowStatus.Action")>
	<CFGRIDUPDATE GRID="VendorGrid" DATASOURCE="#Request.DSN#" TABLENAME="Vendors" KEYONLY="Yes">
</CFIF>
<CFLOCATION URL="index.cfm?saved=yes" ADDTOKEN="No">
