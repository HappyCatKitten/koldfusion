<!---
	directory/save.cfm - action page for edit.cfm
	Adds (Emp_ID = 0), updates, or deletes a directory entry, then shows it.
	The hidden _required/_date fields on the form have already been
	checked by the server before this page runs.
--->
<CFIF NOT Request.IsAdmin OR NOT IsDefined("Form.Emp_ID")>
	<CFLOCATION URL="index.cfm" ADDTOKEN="No">
</CFIF>
<CFPARAM NAME="Form.Photo" DEFAULT="photo_1.gif">
<CFPARAM NAME="Form.Notes" DEFAULT="">

<CFIF IsDefined("Form.DeleteButton") AND Val(Form.Emp_ID)>
	<CFQUERY DATASOURCE="#Request.DSN#">
		DELETE FROM Employees WHERE Emp_ID = #Val(Form.Emp_ID)#
	</CFQUERY>
	<CFLOCATION URL="index.cfm" ADDTOKEN="No">

<CFELSEIF Val(Form.Emp_ID) EQ 0>
	<CFTRANSACTION>
		<CFQUERY DATASOURCE="#Request.DSN#">
			INSERT INTO Employees (FirstName, LastName, Title, Dept_ID, Email, Phone, Office, StartDate, Photo, Notes)
			VALUES ('#Trim(Form.FirstName)#', '#Trim(Form.LastName)#', '#Trim(Form.Title)#', #Val(Form.Dept_ID)#,
			        '#Trim(Form.Email)#', '#Trim(Form.Phone)#', '#Trim(Form.Office)#',
			        <CFQUERYPARAM CFSQLTYPE="CF_SQL_DATE" VALUE="#Form.StartDate#">,
			        '#Form.Photo#', '#Trim(Form.Notes)#')
		</CFQUERY>
		<CFQUERY NAME="GetNewID" DATASOURCE="#Request.DSN#">
			SELECT MAX(Emp_ID) AS NewID FROM Employees
		</CFQUERY>
	</CFTRANSACTION>
	<CFSET SavedID = GetNewID.NewID>

<CFELSE>
	<CFQUERY DATASOURCE="#Request.DSN#">
		UPDATE Employees
		SET FirstName = '#Trim(Form.FirstName)#',
		    LastName  = '#Trim(Form.LastName)#',
		    Title     = '#Trim(Form.Title)#',
		    Dept_ID   = #Val(Form.Dept_ID)#,
		    Email     = '#Trim(Form.Email)#',
		    Phone     = '#Trim(Form.Phone)#',
		    Office    = '#Trim(Form.Office)#',
		    StartDate = <CFQUERYPARAM CFSQLTYPE="CF_SQL_DATE" VALUE="#Form.StartDate#">,
		    Photo     = '#Form.Photo#',
		    Notes     = '#Trim(Form.Notes)#'
		WHERE Emp_ID = #Val(Form.Emp_ID)#
	</CFQUERY>
	<CFSET SavedID = Val(Form.Emp_ID)>
</CFIF>

<CFLOCATION URL="detail.cfm?Emp_ID=#SavedID#&saved=yes" ADDTOKEN="No">
