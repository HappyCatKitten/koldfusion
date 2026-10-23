<!--- requires: java --->
<!--- Java CFX tags: com.allaire.cfx (vintage) and com.gibson.cfx APIs --->
<CFX_HELLOCOLDFUSION NAME="Les">
<cfsilent><CFX_JAVAHELLO NAME="Ben" TIMES="2" VARIABLE="greeting"></cfsilent>
<cfoutput>variable set: #REReplace(greeting, "Java [0-9][^ ]*", "Java x.y")#</cfoutput>
<cfset q = QueryNew("LastName,Salary")>
<cfloop list="Forta:52000,Allaire:61000,Gibson:48000" index="i"><cfset QueryAddRow(q)><cfset QuerySetCell(q, "LastName", ListFirst(i, ":"))><cfset QuerySetCell(q, "Salary", ListLast(i, ":"))></cfloop>
<CFX_JAVAQUERY ACTION="stats" QUERY="q" COLUMN="Salary" NAME="pay">
<cfoutput>stats count=#pay.Count# sum=#pay.Sum# min=#pay.Min# max=#pay.Max# avg=#NumberFormat(pay.Average, "9.99")#</cfoutput>
<CFX_JAVAQUERY ACTION="upper" QUERY="q" COLUMN="LastName">
<cfoutput>input query changed: #ValueList(q.LastName)#</cfoutput>
<CFX_JAVAQUERY ACTION="properties" NAME="props">
<cfoutput>new query columns=#props.ColumnList# rows&gt;0=#props.RecordCount GT 0#</cfoutput>
<cftry><CFX_JAVAHELLO><cfcatch type="Application"><cfoutput>missing attribute: #cfcatch.message#</cfoutput></cfcatch></cftry>
<cftry><CFX_JAVAHELLO NAME="x" TIMES="500"><cfcatch type="Application"><cfoutput>bad TIMES: #cfcatch.message#</cfoutput></cfcatch></cftry>
<cftry><CFX_JAVAQUERY ACTION="stats" QUERY="nosuchquery" COLUMN="x"><cfcatch type="Application"><cfoutput>bad query: #cfcatch.message#</cfoutput></cfcatch></cftry>
<cftry><CFX_JAVAQUERY ACTION="stats" QUERY="q" COLUMN="Nope"><cfcatch type="Application"><cfoutput>bad column: #cfcatch.message#</cfoutput></cfcatch></cftry>
