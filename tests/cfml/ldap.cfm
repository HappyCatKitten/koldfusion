<!--- CFLDAP against the built-in Gibson Directory Server (started in-process by kfserver --run,
      or the running server on the registry's port). Everything happens in a private subtree
      ou=KFRegression below the base DN, created and removed by this test. Assumes the
      Directory Manager password is still the default "admin". --->
<cfsetting enablecfoutputonly="yes">
<cfset L = StructNew()>
<cfset L.s = Server.Directory.Host><cfset L.p = Server.Directory.Port>
<cfset L.u = "cn=Directory Manager"><cfset L.pw = "admin">
<cfset T = "ou=KFRegression, " & Server.Directory.BaseDN>
<cfset P = "ou=People, " & T>
<cfset G = "ou=Groups, " & T>

<!--- clean up after an earlier failed run --->
<cfset leftovers = "uid=babs,#P#|uid=bjensen,#P#|uid=kjensen,#P#|uid=jsmith,#P#|uid=rhill,#P#|uid=qq,#P#|cn=Testers,#G#|#P#|#G#|#T#">
<cfloop list="#leftovers#" index="dn" delimiters="|">
	<cftry><cfldap action="delete" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="#dn#"><cfcatch type="Any"></cfcatch></cftry>
</cfloop>

<!--- 1. ADD (DELIMITER/SEPARATOR) --->
<cfldap action="add" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="#T#" attributes="objectclass=top,organizationalUnit;ou=KFRegression">
<cfldap action="add" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="#P#" attributes="objectclass=top,organizationalUnit;ou=People">
<cfldap action="add" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="#G#" attributes="objectclass=top,organizationalUnit;ou=Groups">
<cfset people = "bjensen|Barbara|Jensen|408-555-1862|Engineering~kjensen|Kurt|Jensen|408-555-6127|Sales~jsmith|John|Smith|408-555-0001|Engineering~rhill|Randy|Hill|408-555-4444|Accounting">
<cfloop list="#people#" index="person" delimiters="~">
	<cfset uid = ListGetAt(person, 1, "|")>
	<cfldap action="add" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="uid=#uid#,#P#"
	        attributes="objectclass=top|person|organizationalPerson|inetOrgPerson^uid=#uid#^givenName=#ListGetAt(person, 2, '|')#^sn=#ListGetAt(person, 3, '|')#^cn=#ListGetAt(person, 2, '|')# #ListGetAt(person, 3, '|')#^telephoneNumber=#ListGetAt(person, 4, '|')#^ou=#ListGetAt(person, 5, '|')#^l=Cupertino, CA^userPassword=pw#uid#"
	        delimiter="^" separator="|">
</cfloop>
<cfldap action="add" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="cn=Testers,#G#"
        attributes="objectclass=top|groupOfUniqueNames;cn=Testers;uniqueMember=uid=bjensen,#P#|uid=rhill,#P#" separator="|">
<cfoutput>add:ok|</cfoutput>

<!--- 2. QUERY: scopes, filters, columns, multi-valued attributes --->
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#P#" scope="onelevel" filter="(sn=Jensen)" attributes="cn,telephoneNumber" sort="cn">
<cfoutput>#q.RecordCount#:#q.ColumnList#:#ValueList(q.cn)#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#T#" scope="subtree" filter="(&(objectclass=person)(|(ou=Sales)(ou=Accounting)))" attributes="uid" sort="uid">
<cfoutput>or:#ValueList(q.uid)#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#T#" scope="subtree" filter="(&(objectclass=person)(!(ou=Engineering)))" attributes="uid" sort="uid">
<cfoutput>not:#ValueList(q.uid)#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#T#" scope="subtree" filter="(cn=*en*sen)" attributes="uid" sort="uid">
<cfoutput>substr:#ValueList(q.uid)#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#T#" scope="subtree" filter="(telephoneNumber=4085551862)" attributes="uid">
<cfoutput>phone:#ValueList(q.uid)#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#T#" scope="subtree" filter="(givenName~=Jon)" attributes="uid">
<cfoutput>approx:#ValueList(q.uid)#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#T#" scope="subtree" filter="(&(objectclass=person)(telephoneNumber>=408-555-5000))" attributes="uid" sort="uid">
<cfoutput>ge:#ValueList(q.uid)#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#T#" scope="subtree" filter="(&(objectclass=person)(telephoneNumber<=408-555-1862))" attributes="uid" sort="uid">
<cfoutput>le:#ValueList(q.uid)#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#T#" scope="subtree" filter="(ou:dn:=Groups)" attributes="dn">
<cfoutput>ext:#q.RecordCount#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#T#" scope="subtree" filter="mail=*" attributes="uid">
<cfoutput>present:#q.RecordCount#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="uid=bjensen,#P#" scope="base" attributes="objectclass,l,dn">
<cfoutput>base:#q.objectclass#:#q.l#:#q.dn#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="uid=bjensen,#P#" scope="base" attributes="objectclass" separator="/">
<cfoutput>sep:#q.objectclass#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="cn=Testers,#G#" scope="base" attributes="*">
<cfoutput>all:#q.ColumnList#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="uid=rhill,#P#" scope="base" attributes="userPassword,cn">
<cfoutput>anonpw:[#q.userPassword#]|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" start="uid=rhill,#P#" scope="base" attributes="userPassword">
<cfoutput>mgrpw:#Left(q.userPassword, 5)#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#T#" scope="onelevel" attributes="ou" sort="ou">
<cfoutput>onelevel:#ValueList(q.ou)#|</cfoutput>

<!--- 3. SORT, SORTCONTROL, STARTROW, MAXROWS --->
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#P#" attributes="uid" sort="sn,givenName">
<cfoutput>sort:#ValueList(q.uid)#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#P#" attributes="uid" sort="sn,givenName" sortcontrol="nocase, desc">
<cfoutput>desc:#ValueList(q.uid)#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#P#" attributes="uid" sort="uid desc, sn">
<cfoutput>keydesc:#ValueList(q.uid)#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#P#" attributes="uid" sort="uid" startrow="2" maxrows="2">
<cfoutput>page:#ValueList(q.uid)#|</cfoutput>
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#P#" attributes="uid" maxrows="3">
<cfoutput>maxrows:#q.RecordCount#|</cfoutput>

<!--- 4. MODIFY (replace/add/delete), MODIFYDN, DELETE --->
<cfldap action="modify" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="uid=bjensen,#P#" attributes="title=Programmer;telephoneNumber=408-555-0000">
<cfldap action="modify" modifytype="add" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="uid=bjensen,#P#" attributes="mail=bjensen@example.com,babs@example.com">
<cfldap action="modify" modifytype="delete" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="uid=bjensen,#P#" attributes="mail=babs@example.com;l=">
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="uid=bjensen,#P#" scope="base" attributes="title,telephoneNumber,mail,l">
<cfoutput>modify:#q.title#:#q.telephoneNumber#:#q.mail#:[#q.l#]|</cfoutput>
<cfldap action="modifydn" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="uid=bjensen,#P#" attributes="uid=babs">
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#P#" filter="(sn=Jensen)" attributes="uid" sort="uid">
<cfoutput>moddn:#ValueList(q.uid)#|</cfoutput>
<cfldap action="delete" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="uid=kjensen,#P#">
<cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#P#" attributes="uid">
<cfoutput>delete:#q.RecordCount#|</cfoutput>

<!--- 5. errors --->
<cfoutput>
</cfoutput>
<cfset tries = ArrayNew(1)>
<cftry><cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="ou=Nowhere,#T#" attributes="cn">
	<cfcatch type="Any"><cfoutput>#cfcatch.Type#:#cfcatch.ErrorCode#:#cfcatch.Message#|</cfoutput></cfcatch></cftry>
<cftry><cfldap action="add" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="uid=jsmith,#P#" attributes="objectclass=person;cn=J;sn=S">
	<cfcatch type="Any"><cfoutput>#cfcatch.Message#|</cfoutput></cfcatch></cftry>
<cftry><cfldap action="add" server="#L.s#" port="#L.p#" dn="uid=qq,#P#" attributes="objectclass=person;cn=Q;sn=Q">
	<cfcatch type="Any"><cfoutput>#cfcatch.Message#|</cfoutput></cfcatch></cftry>
<cftry><cfldap action="delete" server="#L.s#" port="#L.p#" username="#L.u#" password="wrong" dn="uid=jsmith,#P#">
	<cfcatch type="Any"><cfoutput>#cfcatch.Message#|</cfoutput></cfcatch></cftry>
<cftry><cfldap action="delete" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="#P#">
	<cfcatch type="Any"><cfoutput>#cfcatch.Message#|</cfoutput></cfcatch></cftry>
<cftry><cfldap action="modify" modifytype="add" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="uid=jsmith,#P#" attributes="sn=Smith">
	<cfcatch type="Any"><cfoutput>#cfcatch.Message#|</cfoutput></cfcatch></cftry>
<cftry><cfldap action="modify" modifytype="delete" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="uid=jsmith,#P#" attributes="uid=">
	<cfcatch type="Any"><cfoutput>#cfcatch.Message#|</cfoutput></cfcatch></cftry>
<cftry><cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#T#" filter="(&(cn=a)(sn=b)" attributes="cn">
	<cfcatch type="Any"><cfoutput>#cfcatch.Message#|</cfoutput></cfcatch></cftry>
<cftry><cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#T#" scope="everywhere" attributes="cn">
	<cfcatch type="Any"><cfoutput>#cfcatch.Message#|</cfoutput></cfcatch></cftry>
<cftry><cfldap action="search" server="#L.s#" port="#L.p#">
	<cfcatch type="Any"><cfoutput>#cfcatch.Detail#|</cfoutput></cfcatch></cftry>
<cftry><cfldap action="query" server="#L.s#" port="#L.p#" start="#T#" attributes="cn">
	<cfcatch type="Any"><cfoutput>#cfcatch.Detail#|</cfoutput></cfcatch></cftry>
<cftry><cfldap action="query" name="q" server="127.0.0.1" port="1" start="#T#" attributes="cn">
	<cfcatch type="Any"><cfoutput>#cfcatch.Message#:#cfcatch.ErrorCode#|</cfoutput></cfcatch></cftry>
<cfoutput>
</cfoutput>

<!--- 6. Advanced Security with an LDAP user directory and an LDAP group --->
<cfset R = "HKEY_LOCAL_MACHINE\SOFTWARE\Gibson\KoldFusion\CurrentVersion\Security">
<cfregistry action="set" branch="#R#\UserDirectories\KFRegressionDir" entry="Namespace" value="LDAP">
<cfregistry action="set" branch="#R#\UserDirectories\KFRegressionDir" entry="Location" value="#L.s#:#L.p#">
<cfregistry action="set" branch="#R#\UserDirectories\KFRegressionDir" entry="Root" value="#T#">
<cfregistry action="set" branch="#R#\UserDirectories\KFRegressionDir" entry="UserAttribute" value="uid">
<cfregistry action="set" branch="#R#\Contexts\KFRegressionCtx" entry="UserDirectories" value="KFRegressionDir">
<cfregistry action="set" branch="#R#\Contexts\KFRegressionCtx\Rules\Edit" entry="ResourceType" value="Application">
<cfregistry action="set" branch="#R#\Contexts\KFRegressionCtx\Rules\Edit" entry="Resource" value="KFRegression">
<cfregistry action="set" branch="#R#\Contexts\KFRegressionCtx\Rules\Edit" entry="Actions" value="Edit">
<cfregistry action="set" branch="#R#\Contexts\KFRegressionCtx\Policies\Testers" entry="Rules" value="Edit">
<cfregistry action="set" branch="#R#\Contexts\KFRegressionCtx\Policies\Testers" entry="Users" value="">
<cfregistry action="set" branch="#R#\Contexts\KFRegressionCtx\Policies\Testers" entry="Groups" value="Testers">
<cfloop list="rhill:pwrhill,jsmith:pwjsmith,rhill:nope,jsmith:,nobody:x,*:pwrhill" index="cred">
	<cfauthenticate securitycontext="KFRegressionCtx" username="#ListFirst(cred, ':')#" password="#ListRest(cred, ':')#" setcookie="no" throwonfailure="no">
	<cfoutput>auth #ListFirst(cred, ':')#:#CFAUTHENTICATE.AuthenticationStatus#:#IsAuthorized("Application", "KFRegression", "Edit")#|</cfoutput>
</cfloop>
<cftry><cfauthenticate securitycontext="KFRegressionCtx" username="rhill" password="nope" setcookie="no">
	<cfcatch type="Security"><cfoutput>#cfcatch.Message#|</cfoutput></cfcatch></cftry>
<cfregistry action="delete" branch="#R#\Contexts\KFRegressionCtx">
<cfregistry action="delete" branch="#R#\UserDirectories\KFRegressionDir">

<!--- clean up --->
<cfloop list="#leftovers#" index="dn" delimiters="|">
	<cftry><cfldap action="delete" server="#L.s#" port="#L.p#" username="#L.u#" password="#L.pw#" dn="#dn#"><cfcatch type="Any"></cfcatch></cftry>
</cfloop>
<cftry><cfldap action="query" name="q" server="#L.s#" port="#L.p#" start="#T#" scope="base" attributes="ou">
	<cfcatch type="Any"><cfoutput>
cleanup:#cfcatch.ErrorCode#</cfoutput></cfcatch></cftry>
<cfoutput>
</cfoutput>
