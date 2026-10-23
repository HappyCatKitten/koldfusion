<!---
  magic8ball.cfm - ask the Magic 8-Ball a yes/no question. The twenty classic
  answers live in a list; RandRange picks one. Ask the same question twice in
  a row and the ball gets annoyed. KoldFusion Demo Gallery original - MIT licence.
--->
<cfset answers = "It is certain.|It is decidedly so.|Without a doubt.|Yes - definitely.|You may rely on it.|"
	& "As I see it, yes.|Most likely.|Outlook good.|Yes.|Signs point to yes.|"
	& "Reply hazy, try again.|Ask again later.|Better not tell you now.|Cannot predict now.|Concentrate and ask again.|"
	& "Don't count on it.|My reply is no.|My sources say no.|Outlook not so good.|Very doubtful.">
<cfparam name="Form.question" default="">
<cfparam name="Form.lastQuestion" default="">
<cfset question = Trim(Form.question)>
<cfset answer = "">
<cfset mood = "">

<cfif Len(question)>
	<cfif CompareNoCase(question, Form.lastQuestion) IS 0>
		<cfset answer = "You already asked me that. Shake harder.">
		<cfset mood = "grumpy">
	<cfelseif Right(question, 1) IS NOT "?">
		<cfset answer = "That's not a question. Try ending it with a question mark.">
		<cfset mood = "grumpy">
	<cfelse>
		<cfset Randomize(GetTickCount() MOD 100000)>
		<cfset pick = RandRange(1, ListLen(answers, "|"))>
		<cfset answer = ListGetAt(answers, pick, "|")>
		<cfif pick LTE 10><cfset mood = "yes"><cfelseif pick LTE 15><cfset mood = "maybe"><cfelse><cfset mood = "no"></cfif>
	</cfif>
</cfif>

<html>
<head>
<title>The Magic 8-Ball</title>
<script language="JavaScript">
<!--
function checkQuestion(f) {
	if (f.question.value == "") {
		alert("The Magic 8-Ball needs a question!");
		f.question.focus();
		return false;
	}
	return true;
}
// -->
</script>
</head>
<body bgcolor="#FFFFCC" text="#000000">
<center>
<font face="Arial, Helvetica" size="6" color="#000099"><b>~ The Magic 8-Ball ~</b></font><br>
<font face="Arial, Helvetica" size="2"><i>Ask a yes-or-no question. The server knows all.</i></font>
<p>
<img src="/demos/images/8ball.gif" width="160" height="160" alt="Magic 8-Ball">
<p>
<cfif Len(answer)>
	<cfif mood IS "yes"><cfset tint = "000066"><cfelseif mood IS "maybe"><cfset tint = "330066"><cfelseif mood IS "no"><cfset tint = "660000"><cfelse><cfset tint = "333333"></cfif>
	<cfoutput>
	<table border="0" cellpadding="2" cellspacing="0" bgcolor="##000000"><tr><td>
	<table border="0" cellpadding="14" cellspacing="0" bgcolor="###tint#" width="320"><tr><td align="center">
		<font face="Arial, Helvetica" size="1" color="##9999FF">You asked: &quot;#HTMLEditFormat(question)#&quot;</font><br><br>
		<font face="Arial, Helvetica" size="4" color="##FFFFFF"><b>#answer#</b></font>
	</td></tr></table>
	</td></tr></table>
	</cfoutput>
	<p>
</cfif>
<form action="magic8ball.cfm" method="post" onsubmit="return checkQuestion(this)">
<cfoutput><input type="hidden" name="lastQuestion" value="#HTMLEditFormat(question)#"></cfoutput>
<font face="Arial, Helvetica" size="2"><b>Your question:</b></font><br>
<input type="text" name="question" size="45" maxlength="200">
<input type="submit" value="Shake the ball!">
</form>
<font face="Arial, Helvetica" size="1">For entertainment purposes only. Gibson Mainframe Co. is not responsible for decisions made with the help of this 8-Ball.</font>
</center>
<cfinclude template="_footer.cfm">
</body>
</html>
