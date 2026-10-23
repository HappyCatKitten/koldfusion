<CFPARAM NAME="URL.Word" DEFAULT="Supercalifragilistic">
<CFOUTPUT>
<P>"#URL.Word#" has #Len(URL.Word)# characters.</P>
<P>With spaces around it: #Len("  padded  ")#; trimmed: #Len(Trim("  padded  "))#</P>
<P>A binary object made from "KoldFusion" is #Len(ToBinary(ToBase64("KoldFusion")))# bytes long.</P>
</CFOUTPUT>
<FORM ACTION="len.cfm" METHOD="GET">
Try a word: <INPUT TYPE="Text" NAME="Word"> <INPUT TYPE="Submit" VALUE="Count">
</FORM>
