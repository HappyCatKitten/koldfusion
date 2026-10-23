<CFSET TempDir = GetTempDirectory()>
<CFSET Scratch = TempDir & "snippet_" & CreateUUID() & ".txt">
<CFFILE ACTION="WRITE" FILE="#Scratch#" OUTPUT="Written at #TimeFormat(Now(), 'HH:mm:ss')#">
<CFFILE ACTION="READ" FILE="#Scratch#" VARIABLE="Back">
<CFFILE ACTION="DELETE" FILE="#Scratch#">
<CFOUTPUT>
<P>Temporary directory: <TT>#TempDir#</TT> (exists: #DirectoryExists(TempDir)#)
<P>We wrote, read back and deleted <TT>#GetFileFromPath(Scratch)#</TT>: "#Trim(Back)#"
</CFOUTPUT>
