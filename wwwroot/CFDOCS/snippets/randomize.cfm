<CFSET Seed = Year(Now()) * 1000 + DayOfYear(Now())>
<CFSET First = Randomize(Seed)>
<CFSET Pick1 = RandRange(1, 49)>
<CFSET Again = Randomize(Seed)>
<CFSET Pick2 = RandRange(1, 49)>
<CFOUTPUT>
<P>Seeded with #Seed#: first number #First#, then lucky number #Pick1#.
<P>Seeded again with #Seed#: first number #Again#, then lucky number #Pick2#.
<P>Same both times? #YesNoFormat(First EQ Again AND Pick1 EQ Pick2)#. Come back tomorrow for a new lucky number.
</CFOUTPUT>
