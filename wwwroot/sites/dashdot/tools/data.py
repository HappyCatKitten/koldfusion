# -*- coding: utf-8 -*-
"""Dashdot content: every story, person, company and comment here is invented.

Stories run Monday October 11 - Monday October 18, 1999 (Eastern time).
Text fields may contain a little HTML (<I>, <A HREF=...> to other ring sites via @RING:name@).
"""

EDITORS = {
    "CmdrGrits": "Founder. Wrote the Dashdot code in a weekend in Perl; still apologizing.",
    "Hemlock":   "Co-founder. Posts the stories CmdrGrits is asleep for.",
    "Rotundo":   "Senior editor. Old enough to remember punch cards, young enough to complain about them.",
    "jamie_k":   "Your Rights Online editor. Has read the whole EULA. Twice.",
    "Pixelfish": "Games and hardware. Owns three video cards and no furniture.",
}

# Sections (left-hand "Sections" box)
SECTIONS = [
    ("askdashdot", "askdashdot", "Ask Dashdot", "Readers ask, readers answer, readers argue."),
    ("books",      "books",      "Book Reviews", "Dead-tree reviews for people who mostly read man pages."),
    ("bsd",        "bsd",        "BSD", "News for daemons. The section that is not dying, thank you very much."),
    ("features",   "features",   "Features", "Long-form essays, rants and Geeks in Cyberspace."),
    ("interviews", "interviews", "Interviews", "You ask the questions. We forward the best ten."),
    ("yro",        "yro",        "Your Rights Online", "Patents, privacy, and people who would like to read your e-mail."),
]

# Topics: id, label, icon file (drawn by gfx.py)
TOPICS = [
    ("linix",     "Linix",           "topiclinix.gif"),
    ("bsd",       "BSD",             "topicbsd.gif"),
    ("y2k",       "Y2K",             "topicy2k.gif"),
    ("hardware",  "Hardware",        "topichardware.gif"),
    ("internet",  "The Internet",    "topicinternet.gif"),
    ("science",   "Science",         "topicscience.gif"),
    ("space",     "Space",           "topicspace.gif"),
    ("games",     "Games",           "topicgames.gif"),
    ("patents",   "Patents",         "topicpatents.gif"),
    ("privacy",   "Privacy",         "topicprivacy.gif"),
    ("music",     "Music",           "topicmusic.gif"),
    ("money",     "Money",           "topicmoney.gif"),
    ("bug",       "Bug",             "topicbug.gif"),
    ("humor",     "Humor",           "topichumor.gif"),
    ("books",     "Books",           "topicbooks.gif"),
    ("monolith",  "Monolith",        "topicmonolith.gif"),
    ("security",  "Security",        "topicsecurity.gif"),
    ("handhelds", "Handhelds",       "topichandhelds.gif"),
    ("browsers",  "Browsers",        "topicbrowsers.gif"),
    ("news",      "News",            "topicnews.gif"),
]

# The stories. date = (month, day, hour24, minute). Newest first is NOT required; gen sorts.
# Fields: sid-ish key, title, topic, section, editor, date, dept, submitter, intro, more, comments
# comments: story-specific top-level comments: (subject, body, kind)
#   kind: insightful funny informative interesting troll flamebait offtopic first
STORIES = [
dict(key="y2kfridge", title="Y2K Bug Found in Smart Refrigerator Firmware", topic="y2k", section="",
 editor="CmdrGrits", date=(10,18,9,42), dept="it's-the-y2k-dept", submitter="frostbyte",
 intro='"Owners of the Kelvinator-Plus NetChill 2000, the fridge that e-mails you when you\'re out of milk, have discovered '
       'that it thinks January 1st 2000 is January 1st 1900. Since milk bought in 1999 will then be 99 years in the future, '
       'the fridge has decided all of it has expired and is scheduling a self-defrost. The vendor says a patch will ship on '
       'floppy disk \'well before the holidays.\'"',
 editor_note="Nothing says the future like a refrigerator that needs a firmware upgrade. I'm keeping my milk in a cooler.",
 more="<P>The NetChill 2000 runs an embedded 8-bit controller and stores the year in two BCD digits, according to a reader "
      "who dumped the EEPROM with a homemade programmer and a lot of patience. The good news: the fridge does not actually "
      "control the compressor from the clock. The bad news: it controls the ice maker, the door alarm, and the e-mail "
      "notification feature, which will inform you once per minute that your 1999 butter is a century old.</P>"
      "<P>Kelvinator-Plus says customers can call a toll-free number to request the update floppy, which requires "
      "a PC with a serial port and \"approximately one weekend\" to apply.</P>",
 comments=[
  ("Two-digit years in 1999?", "Who on earth designs a product in 1998 with two-digit years? This isn't a COBOL payroll system from 1971, it's a refrigerator that was designed while people were already on TV talking about Y2K every night.", "insightful"),
  ("Re: the e-mail feature", "So the fridge is going to spam me once a minute on New Year's Day. Finally, my refrigerator and my inbox will have something in common.", "funny"),
  ("Why does a fridge need e-mail?", "Serious question. My fridge from 1974 still works, keeps things cold, and has never once needed a patch. The only firmware it has is the little light.", "insightful"),
  ("Embedded systems are the real Y2K risk", "Everyone worries about mainframes, but those have teams of people fixing them. The scary stuff is the millions of little 8-bit controllers in buildings, elevators and appliances that nobody remembers are there. Most will be fine, because most don't care about the date. The ones that do are a needle in a haystack the size of Ohio.", "informative"),
  ("Does it run Linix?", "Seriously, could you port Linix to the NetChill? I'd love a fridge with a 2.2 kernel. uptime: 'up 413 days, eggs low'.", "funny"),
 ]),

dict(key="pentode600", title="Intellon Ships 600MHz Pentode III", topic="hardware", section="",
 editor="Pixelfish", date=(10,18,8,15), dept="more-megahertz-than-sense dept", submitter="overclocked_otter",
 intro='"Intellon today announced the Pentode III at 600MHz, featuring a new 0.18 micron process and an on-die cache that '
       'actually runs at full speed. The chip lists at $669 in quantities of a thousand, which means about $1,100 at the '
       'store down the street. Benchmarks show it beating last month\'s chip by a margin noticeable only to benchmarks."',
 editor_note="Meanwhile Advanced Micro Gizmos says its Marathon will hit 700 before Christmas. Your move, Intellon.",
 more="<P>The new core adds what Intellon calls Streaming SIMD Extensions Plus, which according to the press release "
      "\"enhances the Internet experience.\" How exactly a floating point instruction set makes web pages arrive faster over "
      "a 56k modem is left as an exercise for the reader.</P>",
 comments=[
  ("Enhances the Internet experience", "My Internet experience is bottlenecked by a phone line that crackles when it rains. Unless the Pentode III comes with a new phone company I'm not sure how it helps.", "funny"),
  ("Marathon vs Pentode", "The AMG Marathon is faster clock for clock on integer work and the FPU is finally competitive. The only reason to buy Intellon right now is if your boss buys everything from the same three vendors. Which, admittedly, is most bosses.", "insightful"),
  ("Price per MHz", "Quick math: the 500 is $239 now. The 600 is $669. You're paying $4.30 per extra megahertz. Buy the 500, buy more RAM with the difference. RAM is what's actually making your box swap.", "informative"),
  ("Imagine a Beowulf cluster of these", "Sixteen of these in a rack and you could render the entire Quack III intro in under a week.", "funny"),
 ]),

dict(key="orinococlick", title="Orinoco.com Granted Patent on Clicking", topic="patents", section="yro",
 editor="jamie_k", date=(10,18,7,30), dept="click-here-to-infringe dept", submitter="Prior Art Pete",
 intro='"The online bookseller <A HREF="@RING:orinoco@">Orinoco.com</A> has been granted U.S. Patent 5,999,999 covering '
       '\'a method and system for placing an order by means of a pointing device actuated a single time.\' The claims '
       'appear to cover any web store where you buy something with one click. Competitors are said to be considering a '
       'two-click workaround, or in one case, a long press."',
 editor_note="The patent office appears to be granting patents on anything that runs on a computer and has been done "
             "before, as long as it is described with enough words. I'm patenting 'a method of reading Dashdot at work.'",
 more="<P>Several readers have pointed out that the patent examiner cited exactly zero web-related prior art. One reader "
      "sent in a screenshot of a 1996 shareware catalog program with a button labeled, in its entirety, \"Buy.\"</P>",
 comments=[
  ("Prior art: every vending machine ever", "You press one button and a soda comes out. The vending machine stores your payment info in the form of the quarters you just put in it. I rest my case.", "insightful"),
  ("Boycott", "I've already moved my book buying elsewhere. It's a small gesture but if enough of us do it they'll notice. Or they won't, and I'll have fewer books. Either way.", "interesting"),
  ("The patent office is understaffed", "Examiners have something like 20 hours per application and almost no access to software literature, since most software prior art was never published as a paper or a patent. This is a systemic problem, not just a dumb examiner.", "informative"),
  ("Patent on breathing pending", "I just filed for 'a method of oxygen intake by means of a respiratory organ actuated repeatedly.' You will all owe me royalties by Thursday.", "funny"),
 ]),

dict(key="kernel2322", title="Linix Kernel 2.3.22 Released; 2.4 'Real Soon Now'", topic="linix", section="",
 editor="Hemlock", date=(10,17,23,5), dept="development-kernels-are-for-developers dept", submitter="kernel_kid",
 intro='"The latest development kernel is out, with USB updates, a reworked VM, and a new filesystem driver for reading '
       'disks formatted by a 1987 word processor. As always, this is a development series. It will eat your disk, '
       'your cat and your homework. 2.4 is expected \'when it is done,\' which is the official release date of all '
       'good software."',
 editor_note="Download it from your nearest mirror. Please, the nearest. The main site is hosted on a 486 in a closet.",
 more="",
 comments=[
  ("USB support finally", "I can't wait to plug in my USB mouse and have it actually work. Then I just need USB on something other than this one laptop.", "interesting"),
  ("Compiled fine here", "2.3.22 compiled and booted on my dual Celeron 366 (the Abit board everyone is overclocking). Uptime 4 hours so far, no oopses. Your mileage will absolutely vary.", "informative"),
  ("2.4 by Christmas?", "I'll bet anyone a case of Jolt that 2.4 doesn't ship in 1999. The VM alone needs months.", "interesting"),
  ("The VM rewrite", "The new VM is much better under memory pressure on my 64MB box. Netsail Voyager no longer brings the whole machine to its knees, only to its ankles.", "insightful"),
 ]),

dict(key="sego_daydream", title="Sego Daydream Sells 500,000 Units in Two Weeks", topic="games", section="",
 editor="Pixelfish", date=(10,17,20,12), dept="128-bits-of-fun dept", submitter="RetroRaccoon",
 intro='"Sego\'s new Daydream console has reportedly moved half a million units since its 9/9/99 launch, making it the '
       'fastest selling console ever, at least until the next one. The box has a built-in 56k modem, which means it is '
       'the first game console that can tell you your mom is trying to use the phone."',
 editor_note="I've been playing Soul Spatula for twelve days straight. Send help, or more controllers.",
 more="",
 comments=[
  ("The modem is the killer feature", "Online console gaming is going to be huge. Not with a 56k modem, mind you, but eventually.", "insightful"),
  ("PlayBox 2 will crush it", "Wait for the PlayBox 2. The Emotional Engine is supposed to render actual feelings in real time.", "flamebait"),
  ("Visual memory unit", "The little memory card with the LCD screen is the best gadget of the year. I raise a virtual pet on it during meetings.", "funny"),
 ]),

dict(key="doublebytefinder", title="Ask Dashdot: How Do I Explain My Job to My Grandmother?", topic="humor", section="askdashdot",
 editor="Rotundo", date=(10,17,17,40), dept="it's-like-a-typewriter-but dept", submitter="sysadmin_steve",
 intro='"I\'m a Unix system administrator. Every Thanksgiving my grandmother asks what I do, and every year I say '
       '\'I keep the computers running\' and she asks if I can fix her VCR clock. This year I want to do better. '
       'How do you explain sysadmin work, network engineering, or (heaven help you) database administration to '
       'someone who still writes checks at the supermarket?"',
 editor_note="My personal approach: 'I'm a plumber, but the pipes are invisible and the water is made of numbers.'",
 more="",
 comments=[
  ("The janitor analogy", "Tell her you're the janitor of a very big building that nobody can see. When you do your job right, nobody notices. When something breaks, everybody notices and blames you. She will understand completely.", "insightful"),
  ("Just fix the VCR clock", "Fix the VCR clock. Then fix the microwave clock. She will tell the entire family you're a genius and the question will never come up again.", "funny"),
  ("Librarian", "I'm a DBA and I tell people I'm a librarian for a library where the books are all numbers and people want them back in under a second. Works surprisingly well.", "insightful"),
  ("My grandma runs Linix", "Actually my grandmother runs Red Fedora 6.0. I set it up, she uses Netsail for e-mail and solitaire. She's had fewer problems than my dad on Portals 98.", "interesting"),
 ]),

dict(key="transmuta", title="Secretive Startup Transmuta Updates Web Page", topic="hardware", section="",
 editor="CmdrGrits", date=(10,17,14,2), dept="this-headline-is-not-here-yet dept", submitter="Speculatron",
 intro='"The famously quiet chip startup Transmuta has changed its web page. Where it previously said \'This web page is '
       'not here yet,\' it now says \'This web page is still not here yet.\' Analysts are reading the extra word as a '
       'signal of an imminent product launch, or possibly of a new web designer."',
 editor_note="Rumors range from a low-power x86 clone to a quantum toaster. I'm putting my money on the toaster.",
 more="<P>Readers who viewed the page source report a hidden HTML comment reading \"keep guessing.\" Several readers have "
      "also reported trying to send resumes. All were returned with the message \"this mailbox is not here yet.\"</P>",
 comments=[
  ("View source", "View source on their page. There's a comment that says 'keep guessing'. They are absolutely messing with us and I love it.", "informative"),
  ("Code morphing", "My cousin's roommate's dentist says they're doing software that translates x86 instructions on the fly to a VLIW core. Sounds crazy, but so did the Web.", "interesting"),
  ("The best marketing ever", "They've spent zero dollars on marketing and they've been on Dashdot four times. Every startup in the Valley should take notes.", "insightful"),
 ]),

dict(key="snapsterlaunch", title="College Student's MP3 Swapping Program Takes Off", topic="music", section="",
 editor="Hemlock", date=(10,17,11,25), dept="what-could-possibly-go-wrong dept", submitter="dormroom_dj",
 intro='"A freshman has written a program called <A HREF="@RING:snapster@">Snapster</A> that lets you search other '
       'people\'s hard drives for MP3s and download them directly. It has a chat room, a hot list, and about 30,000 '
       'users who are apparently all in my dorm, judging by the network. Our campus admins have started muttering '
       'about bandwidth. The record labels have not said anything yet, which is probably the calm before something."',
 editor_note="This is either the future of music or the future of a lot of lawyers. Possibly both.",
 more="",
 comments=[
  ("The labels will sue", "Give it six months. The Recording Industry Association of Anywhere is going to come down on this like a ton of shrink-wrapped CDs.", "insightful"),
  ("Bandwidth", "Our dorm's T1 is now 90% MP3s. The other 10% is people asking why the web is so slow.", "funny"),
  ("Distribution is the point", "The interesting thing isn't piracy, it's that a single kid replaced a distribution network that costs billions. The labels should be buying this, not suing it.", "insightful"),
  ("Quality", "Half the files are 96kbps rips with a skip in the middle and the last 20 seconds missing. The other half are labelled as one band and turn out to be another.", "informative"),
 ]),

dict(key="gnume_kdx", title="GNUME 1.0.55 and KDX 1.1.2 Desktop Wars Continue", topic="linix", section="",
 editor="Rotundo", date=(10,16,22,48), dept="my-desktop-can-beat-up-your-desktop dept", submitter="WindowManiac",
 intro='"Both of the big free desktops shipped point releases this week. GNUME adds a new panel applet that shows the '
       'phase of the moon, while KDX now has a control center for its control center. Flame wars on the mailing lists '
       'have reached a level not seen since the great vi versus emacs conflict of last Tuesday."',
 editor_note="I run twm. Get off my lawn.",
 more="",
 comments=[
  ("Choice is good", "Two desktops competing means both get better faster. This is how it's supposed to work. Now if they'd just agree on a drag-and-drop protocol.", "insightful"),
  ("License flames incoming", "Before anyone starts: yes, we know about the toolkit license. Yes, it has been discussed. Yes, for 400 messages. No, it is not going to be settled in this thread.", "funny"),
  ("Both are too heavy", "On my P133 with 32MB both of them take a minute to start. Window Maker starts before I let go of the Enter key.", "interesting"),
  ("Linix on the desktop", "This is the year of Linix on the desktop. I can feel it.", "funny"),
 ]),

dict(key="marsprobe", title="Mars Weather Probe Lost Over Feet-vs-Furlongs Mixup", topic="space", section="",
 editor="Hemlock", date=(10,16,19,30), dept="should-have-used-cubits dept", submitter="RocketRandy",
 intro='"An investigation board has concluded that the Mars Weather Probe was lost because one contractor\'s software '
       'reported thrust in pound-force seconds and the navigation team assumed newton-seconds. The $125 million '
       'spacecraft is now believed to be either in a very low orbit or a very small crater."',
 editor_note="Let this be a lesson to everyone who ever skipped the units in physics class. I'm looking at myself here.",
 more="",
 comments=[
  ("Integration testing", "Nobody ran an end-to-end test of the actual data files passed between teams. This isn't a units problem, it's a process problem. The units are just where the process failure showed up.", "insightful"),
  ("The metric system", "This is why every country except about three uses metric. Feet are based on a king's foot. Which king? Nobody knows!", "flamebait"),
  ("My math teacher was right", "I would like to formally apologize to Mr. Hoskins, 10th grade physics. Units matter. You were right.", "funny"),
 ]),

dict(key="descramble", title="DVD Encryption Cracked by Norwegian Teens", topic="security", section="yro",
 editor="jamie_k", date=(10,16,16,10), dept="forty-bits-of-security dept", submitter="Linixdvd",
 intro='"A program called DeScramble that decrypts DVD video has appeared on the net, apparently because one software '
       'player left its key lying around unencrypted. The goal, according to its authors, was to let Linix users watch '
       'DVDs they had bought. The movie studios do not appear to see it that way."',
 editor_note="Forty-bit keys in 1999. Somewhere a cryptographer is crying into a pocket protector.",
 more="<P>The scheme relied on a few hundred player keys staying secret forever. Readers note that a secret shared by "
      "every DVD player manufacturer on Earth is a secret in roughly the same way that the plot of a summer movie is.</P>",
 comments=[
  ("I just want to watch my DVDs", "I bought a DVD drive and a stack of movies. I run Linix. There is no licensed player for Linix. What exactly am I supposed to do, buy a second computer to watch a movie I already paid for?", "insightful"),
  ("Lawsuits incoming", "Mark my words, they'll go after every web site that even links to the code. This will end up in front of a judge and it won't be pretty.", "interesting"),
  ("Security through obscurity", "Any system where the key has to be in the hands of the attacker (because the attacker is also the customer) is fundamentally broken. You can make it annoying, you can't make it secure.", "informative"),
 ]),

dict(key="petzipo", title="Petz.com IPO Soars Despite Losing Money on Every Sale", topic="money", section="",
 editor="CmdrGrits", date=(10,16,13,0), dept="we'll-make-it-up-in-volume dept", submitter="DayTraderDan",
 intro='"Online pet store <A HREF="@RING:petz@">Petz.com</A>, whose sock puppet mascot has become oddly famous, went '
       'public today and closed up 85%. According to the S-1, the company sells 40-pound bags of dog food for less than '
       'the cost of shipping them. When asked about the business model, a spokesperson said: \'Eyeballs.\'"',
 editor_note="I'm not saying it's a bubble. I'm saying I just saw a sock puppet with a market cap larger than my town.",
 more="",
 comments=[
  ("We'll make it up in volume", "Lose $5 on every order and make it up in volume. Classic.", "funny"),
  ("The bubble", "When a company that ships heavy, cheap, low-margin goods over long distances is valued at a billion dollars, the market has stopped looking at fundamentals. This will end badly.", "insightful"),
  ("I bought some", "I bought 100 shares at the open. I'm either a genius or I'm going to be eating the dog food. Check back in a year.", "interesting"),
  ("Sock puppet", "I'd buy the sock puppet. Just the puppet. Not the stock.", "funny"),
 ]),

dict(key="ucluta", title="UCLUTA: The Shrink-Wrap License Law You Should Be Worried About", topic="privacy", section="yro",
 editor="jamie_k", date=(10,15,21,30), dept="by-reading-this-headline-you-agree dept", submitter="LawGeek",
 intro='"A proposed model law called UCLUTA would make shrink-wrap and click-through licenses enforceable in every '
       'state that adopts it, let vendors disable software remotely, and allow licenses to forbid publishing benchmarks '
       'or reviews. It is being considered in state legislatures right now, mostly without anyone noticing."',
 editor_note="Write your state representatives. Use paper. They read paper.",
 more="",
 comments=[
  ("Remote disable", "The remote disable provision terrifies me. A vendor gets into a billing dispute with my company and turns off our accounting software on the last day of the quarter? That's not a license, that's a hostage situation.", "insightful"),
  ("No benchmarks", "Banning benchmarks is the tell. If your product is good you want people publishing numbers.", "insightful"),
  ("Free software exemption?", "How does this interact with the GPL? The GPL relies on copyright law, not on contract. Could UCLUTA actually help or hurt free software? Any lawyers in the house?", "interesting"),
 ]),

dict(key="beowulfgarage", title="Teen Builds 64-Node Cluster in Parents' Garage", topic="science", section="",
 editor="Rotundo", date=(10,15,18,22), dept="imagine-a-beowulf-cluster-of-these dept", submitter="NodeNinja",
 intro='"A 16-year-old in Ohio has built a 64-node cluster out of discarded 486s and Pentium 75s collected from local '
       'businesses upgrading for Y2K. It runs Linix and PVM, heats the garage through the winter, and according to the '
       'builder\'s father, \'has made the electric meter spin like a ceiling fan.\'"',
 editor_note="Finally, a story where the joke has already been made for you in the department line.",
 more="",
 comments=[
  ("Y2K upgrades are a goldmine", "Every company in America is dumping perfectly good machines because the BIOS isn't certified. If you have a pickup truck and a weekend you can build a supercomputer for the price of gas.", "informative"),
  ("Power bill", "64 nodes at maybe 60 watts each is close to 4 kW. At 8 cents a kilowatt-hour that's more than $200 a month. Dad is a saint.", "informative"),
  ("Imagine a...", "Imagine a Beowulf cluster of Beowulf clusters. Okay, I'll stop.", "funny"),
 ]),

dict(key="godzillam10", title="Mothzilla Milestone 10 Released", topic="browsers", section="",
 editor="Hemlock", date=(10,15,15,45), dept="the-lizard-is-getting-big dept", submitter="GeckoGuy",
 intro='"The open source browser project spun out of Netsail has released Milestone 10, with a working mail client, '
       'better standards support, and a first cut at the new skinnable interface. It still crashes when you look at it '
       'funny, but it renders CSS better than anything else on the market."',
 editor_note="Download, test, file bugs. That's how this works, people.",
 more="",
 comments=[
  ("Too slow", "It's been over a year and a half since the source was released. It still isn't usable as a daily browser. Navigational Explorer 5 is eating everyone's lunch while the lizard rewrites the layout engine for the third time.", "flamebait"),
  ("Rewrite was the right call", "The old codebase was unmaintainable. Throwing it out was painful but the new engine is actually standards-compliant. Give it a year.", "insightful"),
  ("Skins", "Do we really need skinnable chrome? I'd settle for a browser that doesn't leak 40MB an hour.", "interesting"),
 ]),

dict(key="greybeardinterview", title="Interview: The Man Who Wrote the Payroll Code in 1974", topic="y2k", section="interviews",
 editor="Rotundo", date=(10,15,12,10), dept="back-then-we-had-to-use-two-digits dept", submitter="Rotundo",
 intro='Last month you sent in questions for Walt Ferraday, the COBOL programmer who wrote the payroll system that is '
       'still running at a large Midwestern insurance company, and who came out of retirement this year to fix it. '
       'His answers are below. He typed them himself, on a terminal, in all capital letters.',
 editor_note="",
 more="<P><B>1) Why two digits?</B> <I>(asked by many, many people)</I><BR>BECAUSE CORE MEMORY COST MORE THAN MY CAR. "
      "EVERY BYTE WAS A DECISION. NOBODY EXPECTED THE PROGRAM TO OUTLIVE THE MACHINE. THEN THEY BOUGHT ANOTHER MACHINE "
      "AND COPIED THE PROGRAM. THEN ANOTHER. THE PROGRAM IS NOW OLDER THAN THREE OF MY GRANDCHILDREN.</P>"
      "<P><B>2) Is it going to be okay on January 1st?</B> <I>(asked by Nervous Ned)</I><BR>MY CODE WILL BE FINE. I FIXED "
      "IT IN MARCH. I AM LESS SURE ABOUT THE CODE THAT CALLS MY CODE. I DID NOT WRITE THAT. A CONSULTANT WROTE THAT IN "
      "1988 AND HE HAD A PONYTAIL.</P>"
      "<P><B>3) What do you think of Linix?</B> <I>(asked by kernel_kid)</I><BR>MY GRANDSON INSTALLED IT ON MY PC. IT "
      "ASKED ME WHICH KEYBOARD I HAD. NO COMPUTER HAS EVER ASKED ME THAT. I LIKE IT.</P>"
      "<P><B>4) How much are they paying you?</B> <I>(asked by Anonymous Coward)</I><BR>ENOUGH TO BUY A BOAT. I WILL "
      "NAME IT 'PIC 9(2)'.</P>"
      "<P><B>5) Any advice for young programmers?</B><BR>WRITE COMMENTS. SOMEBODY WILL READ YOUR CODE IN 25 YEARS AND "
      "IT MIGHT BE YOU.</P>",
 comments=[
  ("Best interview ever", "The all-caps answers are perfect. This man is a national treasure. Somebody give him a boat. Oh wait, they did.", "funny"),
  ("Write comments", "That last answer should be printed on every CS diploma.", "insightful"),
  ("The consultant with the ponytail", "Hey, I resent that. My ponytail and I wrote very good code in 1988. Mostly.", "funny"),
 ]),

dict(key="ostrichsat", title="Ostrich Satellite Phone Network to Deorbit 66 Satellites", topic="space", section="",
 editor="Pixelfish", date=(10,15,9,5), dept="can-you-hear-me-now dept", submitter="LowEarthLarry",
 intro='"After its bankruptcy, the Ostrich satellite phone network has announced it will steer all 66 of its satellites '
       'into the atmosphere to burn up. The handsets were the size of a brick, cost $3,000, and only worked outdoors, '
       'which turned out to be a hard sell to business travelers who spend most of their time indoors."',
 editor_note="Five billion dollars of hardware turned into the world's most expensive meteor shower.",
 more="",
 comments=[
  ("Sell them to us", "Can't some university buy them for a dollar? Imagine what amateur radio folks could do with 66 satellites.", "interesting"),
  ("Business model", "The business model assumed cell networks wouldn't grow. Cell networks grew. Oops.", "insightful"),
  ("Free meteor shower", "Free light show. I'll bring the lawn chairs.", "funny"),
 ]),

dict(key="bsddaemon", title="FreeDaemon 3.3 Released", topic="bsd", section="bsd",
 editor="Hemlock", date=(10,14,22,15), dept="the-daemon-is-alive dept", submitter="pitchfork_pete",
 intro='"FreeDaemon 3.3-RELEASE is out, with improved SMP support, a new sound driver framework, Linix binary compatibility '
       'that actually runs most Linix binaries faster than Linix does, and the usual mountain of bug fixes. ISO images '
       'are on the FTP mirrors; the main FTP server is reportedly already maxed out at 2,000 users."',
 editor_note="Before anyone posts it: no, it is not dying.",
 more="",
 comments=[
  ("Rock solid", "We run our mail and web on FreeDaemon. Uptime on the oldest box is 403 days, and we only rebooted it then because we moved offices.", "informative"),
  ("Ports collection", "The ports tree is still the best package system out there. cd /usr/ports/whatever; make install clean. Done.", "insightful"),
  ("Linix compatibility", "Running Linix binaries faster than Linix is a great party trick. Not that I get invited to parties.", "funny"),
 ]),

dict(key="regexbook", title="Review: Regular Expressions for Irregular People", topic="books", section="books",
 editor="Rotundo", date=(10,14,19,0), dept="s/confusion/clarity/g dept", submitter="Rotundo",
 intro='Gladys Okonkwo-Pratt\'s new book from Trout & Turtle Press promises to teach regular expressions to people who '
       'have previously only used them by copying lines out of other people\'s Perl scripts and praying. Our reviewer '
       'is one of those people. Read on to see if it worked.',
 editor_note="",
 more="<TABLE BORDER=0 CELLPADDING=2><TR><TD><FONT SIZE=2><B>author</B></FONT></TD><TD><FONT SIZE=2>Gladys Okonkwo-Pratt</FONT></TD></TR>"
      "<TR><TD><FONT SIZE=2><B>pages</B></FONT></TD><TD><FONT SIZE=2>312</FONT></TD></TR>"
      "<TR><TD><FONT SIZE=2><B>publisher</B></FONT></TD><TD><FONT SIZE=2>Trout &amp; Turtle Press</FONT></TD></TR>"
      "<TR><TD><FONT SIZE=2><B>rating</B></FONT></TD><TD><FONT SIZE=2>8/10</FONT></TD></TR>"
      "<TR><TD><FONT SIZE=2><B>summary</B></FONT></TD><TD><FONT SIZE=2>Finally, an explanation of backtracking a human can follow.</FONT></TD></TR></TABLE>"
      "<P><B>The Scoop</B><BR>The book starts with grep and ends with a full chapter on why you should not parse HTML with "
      "regular expressions, which the author then proceeds to do for 40 pages anyway, very entertainingly.</P>"
      "<P><B>What's Good?</B><BR>The diagrams of the matching engine stepping through a pattern are worth the cover price. "
      "Each chapter ends with exercises that start easy and end with patterns that look like line noise but actually "
      "work.</P><P><B>What's Bad?</B><BR>The index is thin, and the chapter on Unicode is two pages long, one of which "
      "is a picture of a confused cat.</P>",
 comments=[
  ("Now you have two problems", "Some people, when confronted with a problem, think 'I'll use a regular expression.' Then they buy this book. Then they have a book.", "funny"),
  ("Exercises", "I worked through the first five chapters on the train. The exercises are genuinely good. The backtracking diagrams finally made it click for me.", "informative"),
 ]),

dict(key="pearitop", title="Pear Computer's iTop Laptop Now in Five Fruit Flavors", topic="hardware", section="",
 editor="Pixelfish", date=(10,14,16,33), dept="fruit-salad dept", submitter="ClamshellCarl",
 intro='"Pear has expanded its translucent clamshell laptop line to five colors: Blueberry, Tangerine, Lime, Grape and a '
       'new \'Graphite\' for people who want to be taken seriously at meetings. It has a handle, wireless networking '
       'that works without wires, and weighs about as much as a medium-sized cat."',
 editor_note="I want one. I don't know why. I just do.",
 more="",
 comments=[
  ("Wireless networking", "The wireless card is the real story here. In five years every laptop will have it and every coffee shop will have a base station. Mark my words.", "insightful"),
  ("Toilet seat", "It looks like a toilet seat. A very nice, translucent, tangerine toilet seat.", "funny"),
  ("One button mouse", "Still with the one button trackpad. How do I middle-click paste?", "interesting"),
 ]),

dict(key="kevlarthumb", title="Researchers Grow Cloned Llama Named 'Tina'", topic="science", section="",
 editor="Hemlock", date=(10,14,13,20), dept="hello-llama dept", submitter="BioBob",
 intro='"A research lab in a small Scottish-sounding town that is actually in Oregon has announced the birth of Tina, '
       'the first cloned llama. Tina is reportedly healthy, curious, and has already spat at two members of the press."',
 editor_note="Clearly the ethical implications of cloning will be with us for decades. Also, llamas are great.",
 more="",
 comments=[
  ("Why llamas?", "Llama antibodies are unusually small and simple, which makes them interesting for medical research. This isn't just a stunt.", "informative"),
  ("Spat at the press", "Tina is my new favorite journalist critic.", "funny"),
  ("Slippery slope", "First llamas, then sheep, then people. Where does it end? Probably with a lot of identical, confused sysadmins.", "flamebait"),
 ]),

dict(key="quackarena", title="Quack III Arena Demo Hits the Net", topic="games", section="",
 editor="Pixelfish", date=(10,14,10,0), dept="frag-before-you-buy dept", submitter="RailgunRhonda",
 intro='"ego Software has released a playable demo of Quack III Arena, with four maps, bots, and a Linix version on day '
       'one. Download mirrors are melting worldwide. The demo requires a 3D card; the readme suggests that if you are '
       'trying to run it on a software renderer you should \'consider a hobby, perhaps knitting.\'"',
 editor_note="Productivity across the industry has just dropped 40%. Mine certainly has.",
 more="",
 comments=[
  ("Linix version on day one!", "This is huge. A major game shipping a native Linix demo on the same day as Portals. Thank you, ego. This is the kind of thing that actually moves people over.", "insightful"),
  ("Unlikely Tournament is better", "Unlikely Tournament has better bots and more game modes. Quack III has better netcode. Flame on.", "flamebait"),
  ("Frame rates", "Voodoo3 3000 on a Celeron 450: 58 fps in timedemo at 800x600. RazorForce 256 gets 71. Don't bother with the TNT1.", "informative"),
  ("Knitting", "I tried it on my software renderer. I've taken up knitting. It runs at about the same frame rate.", "funny"),
 ]),

dict(key="earwig", title="Project Earwig: Are Your E-Mails Being Read?", topic="privacy", section="yro",
 editor="jamie_k", date=(10,13,21,12), dept="hi-to-everyone-reading-this dept", submitter="ParanoidPolly",
 intro='"A European parliamentary report has described Project Earwig, an alleged international network of listening '
       'stations that sifts phone calls, faxes and e-mail for keywords. A group of netizens has declared October 21 '
       '\'Jam Earwig Day\' and is asking everyone to put suspicious-sounding words in their e-mail signatures."',
 editor_note="Hello to all our readers in the listening stations. Please moderate this story up.",
 more="",
 comments=[
  ("Jam day won't work", "Adding keywords to your sig just trains their filters on noise. Real traffic analysis doesn't care about words anyway, it cares about who talks to whom.", "insightful"),
  ("Use encryption", "Use PGP. Use it for everything, including mail to your mom about dinner. If everything is encrypted, encrypted mail stops being suspicious.", "insightful"),
  ("sig", "pineapple anarchist cryptography secret plans tuesday. There. Let them read about my Tuesday.", "funny"),
 ]),

dict(key="slashdottedeffect", title="Small Museum Web Server Survives Being Linked From Here", topic="internet", section="",
 editor="CmdrGrits", date=(10,13,18,40), dept="the-dashdot-effect dept", submitter="WebWeaver",
 intro='"Remember last week\'s story about the Museum of Obsolete Calculators? Their webmaster wrote in to say the site '
       'took 140,000 hits in 24 hours, on a 486/66 with 16MB of RAM and a single ISDN line, and it stayed up. Her secret: '
       'static HTML, no CGI, and a strongly worded note taped to the server that said \'DO NOT TURN OFF.\'"',
 editor_note="We salute you, 486/66. You are braver than most corporate web farms.",
 more="",
 comments=[
  ("Static HTML wins", "This is the lesson every web developer should learn. Static files are fast. You don't need an application server to serve a picture of a slide rule.", "insightful"),
  ("The note", "The note is the most important part of the infrastructure. Our whole data center runs on notes like that.", "funny"),
  ("Mirror", "Here's a mirror in case it goes down this time: just kidding, it won't. It's a 486. It fears nothing.", "funny"),
 ]),

dict(key="beeos", title="BeeOS 4.5 Free for Personal Use", topic="news", section="",
 editor="Rotundo", date=(10,13,15,5), dept="buzz-buzz dept", submitter="MediaMaven",
 intro='"Bee Inc. says it will give away a version of its media-focused operating system for personal use. BeeOS boots '
       'in about ten seconds, plays eight video streams at once without breaking a sweat, and has a file system that '
       'acts like a database. It currently has eleven applications, four of which are image viewers."',
 editor_note="If only it had a web browser that worked on more than half the web.",
 more="",
 comments=[
  ("Best OS nobody uses", "BeeOS is technically amazing. It's also doomed, because nobody writes software for an OS that nobody uses, and nobody uses an OS that has no software.", "insightful"),
  ("Pervasive multithreading", "The responsiveness is incredible. Dragging a window while playing four videos and nothing stutters. Portals 98 stutters when I move the mouse too fast.", "interesting"),
 ]),

dict(key="frondvii", title="Frond VII Handheld Gets Wireless Web Clipping", topic="handhelds", section="",
 editor="Pixelfish", date=(10,13,12,30), dept="little-pieces-of-the-web dept", submitter="StylusSam",
 intro='"The new Frond VII handheld has a built-in radio and an antenna you flip up to grab \'web clippings\' -- tiny '
       'pages built just for the device. Service costs $9.99 a month for 50K of data, which works out to roughly two '
       'weather reports and half a stock quote."',
 editor_note="I'll stick with my Frond III and its 2MB of RAM, which is more than my first PC had.",
 more="",
 comments=[
  ("50K a month?", "50K a month. Fifty kilobytes. The Dashdot front page is bigger than that. This will not catch on until the data costs drop by 100x.", "insightful"),
  ("Graffiti", "I've gotten so used to the Graffiti alphabet I now write my grocery lists that way. My wife thinks I've had a stroke.", "funny"),
 ]),

dict(key="openfridgesource", title="Monolith Software: Open Source Is 'Intellectual Pac-Man'", topic="monolith", section="",
 editor="CmdrGrits", date=(10,13,9,15), dept="waka-waka-waka dept", submitter="Gnuisance",
 intro='"A leaked internal memo from Monolith Software, makers of Portals 98, says that open source software \'poses a '
       'direct, short-term revenue and platform threat\' and that the company should consider \'de-commoditizing '
       'protocols.\' The memo was titled \'Halloween Treat\' and was apparently not meant to be read by anyone with a '
       'modem."',
 editor_note="De-commoditizing protocols. I'm going to need someone to translate that into English. Actually, no, I'm not.",
 more="",
 comments=[
  ("They take it seriously", "Whatever else this memo says, it says that the biggest software company in the world takes Linix seriously. A year ago they were laughing. That's a win.", "insightful"),
  ("Embrace, extend...", "De-commoditize protocols = add proprietary extensions so that their stuff only works with their stuff. We've seen this movie.", "insightful"),
  ("Portals 2000", "I've used the Portals 2000 beta. It's actually pretty stable. Flame away.", "troll"),
 ]),

dict(key="y2kgenerator", title="Ask Dashdot: Should I Buy a Generator for Y2K?", topic="y2k", section="askdashdot",
 editor="Hemlock", date=(10,12,22,0), dept="the-power-of-positive-thinking dept", submitter="Nervous Ned",
 intro='"My brother-in-law has filled his basement with canned beans, a generator, 400 gallons of water and a copy of '
       'every Linix distribution on CD. He says I\'m a fool for not doing the same. I\'m a programmer and I think the '
       'power grid will be fine. But I\'m only about 95% sure. What are Dashdot readers doing to prepare?"',
 editor_note="I'm preparing by having a backup of my backups. And beans. Okay, some beans.",
 more="",
 comments=[
  ("I work at a utility", "I work at a power utility. We have been testing since 1997. We rolled the clocks forward on every system we could. The grid will be fine. Your brother-in-law will have a lot of beans.", "informative"),
  ("Beans are always useful", "Even if nothing happens, beans don't go bad. Worst case you have chili for a year.", "funny"),
  ("Fill the bathtub", "Fill your bathtub, have some cash on hand, keep a flashlight. Same thing you'd do for a big storm. That's all the prep anyone sane needs.", "insightful"),
  ("I'll be at work", "I'll be at work on New Year's Eve watching logs scroll by. Pizza is provided. Bring your own champagne. In a thermos. Don't tell my boss.", "interesting"),
 ]),

dict(key="ipv6", title="IPv6 Test Network Hits 400 Sites", topic="internet", section="",
 editor="Rotundo", date=(10,12,19,10), dept="enough-addresses-for-every-grain-of-sand dept", submitter="HexHead",
 intro='"The experimental IPv6 backbone now connects more than 400 sites across 40 countries. With 128-bit addresses '
       'there will be enough to give an IP address to every grain of sand on every beach, which should help with the '
       'impending sand-networking boom."',
 editor_note="Adoption is expected any day now, give or take a decade.",
 more="",
 comments=[
  ("NAT will kill it", "Everybody's going to put their houses behind NAT boxes and nobody will feel the pain of address shortage. IPv6 will take 20 years.", "insightful"),
  ("Memorizing addresses", "I can't memorize a 32-bit address half the time. Good luck memorizing fe80:0000:0000:0000... oh I give up.", "funny"),
 ]),

dict(key="slashcode", title="Dashdot Source Code Released Under the GPL", topic="news", section="features",
 editor="CmdrGrits", date=(10,12,16,0), dept="please-don't-look-at-it dept", submitter="CmdrGrits",
 intro='After months of requests, we are releasing the code that runs this site, under the GPL. It\'s Perl. It\'s '
       'mostly held together with regular expressions, sticky notes and hope. There are comments in it that say things '
       'like "# I am so sorry". You have been warned.',
 editor_note="Patches welcome. Mockery also welcome, but patches are more welcome.",
 more="<P>The release is called \"Dash 0.3\" and includes the comment engine, the moderation system and the "
      "infamous poll booth. It does not include the cron job that crashes every Tuesday, because frankly we don't know "
      "which one that is.</P>",
 comments=[
  ("Finally", "I've wanted to run a Dashdot-style site for my LUG for ages. Thank you!", "interesting"),
  ("Looked at it", "I looked at it. I need a drink. There's a 900-line function called 'displayStory'. I'm not kidding.", "funny"),
  ("Regex heaven", "There is a regular expression in the comment filter that is 340 characters long. I've printed it out and framed it.", "funny"),
 ]),

dict(key="leonids", title="Leonid Meteor Storm Could Threaten Satellites", topic="space", section="",
 editor="Hemlock", date=(10,12,13,25), dept="duck-and-cover dept", submitter="StargazerSue",
 intro='"Astronomers predict that next month\'s Leonid meteor shower could become a full storm, with thousands of '
       'meteors per hour. Satellite operators are planning to turn their solar panels edge-on to the stream and hope '
       'for the best. Ground observers just need dark skies, a lawn chair and something hot to drink."',
 editor_note="I'll be the one in the lawn chair. Wake me if the satellites fall.",
 more="",
 comments=[
  ("Best viewing", "Get away from city lights, face east after midnight, and give your eyes 20 minutes to adapt. Don't bother with binoculars, you want the widest field of view possible.", "informative"),
  ("Space junk", "Each grain of sand at 70 km/s carries more energy than a bullet. It's not the big ones you worry about, it's the plasma they make when they hit.", "informative"),
 ]),

dict(key="emacsvi", title="Poll Results: vi Narrowly Beats Emacs, ed Gets 3%", topic="humor", section="",
 editor="Rotundo", date=(10,12,10,20), dept="holy-war-continues dept", submitter="Rotundo",
 intro='Last week\'s poll asking for your one true editor came in at 31,442 votes. vi took 41%, emacs 39%, pico 9%, '
       'and ed a surprisingly loyal 3%. "Cat with a redirect" got 2%, and 6% voted for a word processor whose name we '
       'will not print here for fear of starting a riot.',
 editor_note="Comments are open, but please keep the flames below 451 degrees.",
 more="",
 comments=[
  ("ed is the standard text editor", "ed is the standard text editor. ?", "funny"),
  ("Emacs is an OS", "Emacs is a fine operating system. It just lacks a decent text editor.", "funny"),
  ("The poll is rigged", "vi users vote faster because they don't have to press Control-Meta-Shift-Vote.", "funny"),
  ("Use what works", "Honestly, use whatever makes you productive. I use vi for quick edits and emacs for long sessions and nobody has been harmed.", "insightful"),
 ]),

dict(key="cybersquat", title="Congress Passes Anti-Cybersquatting Bill", topic="internet", section="yro",
 editor="jamie_k", date=(10,11,22,40), dept="this-domain-for-sale dept", submitter="DomainDave",
 intro='"A bill that lets trademark holders sue people who register domain names \'in bad faith\' has passed. Critics '
       'say the definition of bad faith is so broad that a kid named Mike who registered mike.com could be dragged into '
       'court by a soft drink company with a Mike product."',
 editor_note="I had a domain once. I let it expire. Now it's a casino.",
 more="",
 comments=[
  ("Reverse hijacking", "The real risk is reverse domain hijacking: big companies taking legitimate names from small owners by threatening a lawsuit the small owner can't afford to fight.", "insightful"),
  ("Good riddance", "I'm actually fine with this. Squatters registering every brand name and holding them for ransom were a plague.", "interesting"),
 ]),

dict(key="xmlhype", title="Is XML the Answer to Everything?", topic="internet", section="features",
 editor="Rotundo", date=(10,11,19,15), dept="angle-brackets-will-save-us dept", submitter="MarkupMarcy",
 intro='"Every trade magazine on my desk this month has XML on the cover. It will apparently replace EDI, databases, '
       'HTML, configuration files and possibly my toaster. As someone who has to actually write the parsers, I\'d like '
       'to ask: what problem does XML solve that a well-specified text format didn\'t already?"',
 editor_note="Answer in well-formed comments, please. Close your tags.",
 more="",
 comments=[
  ("It's just syntax", "XML is just a syntax for trees. It doesn't solve the hard problem, which is agreeing on what the tags mean. Two companies using XML can still be completely incompatible.", "insightful"),
  ("Free parsers", "The win is that you never have to write a parser again. That alone is worth a lot.", "insightful"),
  ("Toaster", "<toaster><bread state='burnt'/></toaster>. See? It works.", "funny"),
 ]),

dict(key="andoveripo", title="Dashdot's Parent Overandover.net Files for IPO", topic="money", section="",
 editor="CmdrGrits", date=(10,11,16,30), dept="we-promise-not-to-sell-out dept", submitter="CmdrGrits",
 intro='Some of you have already noticed the filing. Yes, Overandover.net, which owns Dashdot, is going public. No, '
       'nothing changes. No, we will not put banner ads in the comments. Okay, we\'ll put one in the corner. A small one.',
 editor_note="Our lawyers have asked us to tell you that we are in a quiet period. This is the quietest I've ever been.",
 more="",
 comments=[
  ("Sell-outs", "Sell-outs! I've been reading this site since it was a hobby page on a university server.", "flamebait"),
  ("Congrats", "Seriously, congratulations. You built something people use every day out of a Perl script and spite. You've earned it.", "insightful"),
  ("Shares for readers", "Will there be a directed share program for readers? Some of us have karma to cash in.", "interesting"),
 ]),

dict(key="monolithtrial", title="Monolith Antitrust Trial: Judge's Findings Due Soon", topic="monolith", section="yro",
 editor="jamie_k", date=(10,11,13,10), dept="the-browser-is-part-of-the-OS dept", submitter="CourtWatcher",
 intro='"The judge in the government\'s antitrust case against Monolith Software is expected to issue findings of fact '
       'within weeks. At issue is whether bundling the Navigational Explorer browser into Portals 98 was an attempt to '
       'crush Netsail. Monolith\'s lawyers maintain that the browser cannot be removed without breaking the operating '
       'system, and also that it can be removed easily if you really want to."',
 editor_note="Both of those statements were made under oath, by the way. On different days.",
 more="",
 comments=[
  ("The video", "The best part of the trial was the video where they demonstrated removing the browser and the desktop icons visibly changed between cuts.", "funny"),
  ("Breakup?", "If they find a monopoly, the real question is the remedy. A breakup into an OS company and an apps company would be the most interesting outcome.", "insightful"),
  ("Leave them alone", "Monolith made computers affordable for regular people. The government should stay out of the software business.", "troll"),
 ]),

dict(key="firstpost", title="Ask Dashdot: Why Do People Post 'First Post'?", topic="humor", section="askdashdot",
 editor="Hemlock", date=(10,11,10,0), dept="a-sociological-inquiry dept", submitter="Anthropologeek",
 intro='"I\'m writing a paper on online communities and I keep seeing comments that consist entirely of the words '
       '\'first post.\' They are usually not first, and they are always moderated into oblivion. What drives this '
       'behavior? Is it an art form? A cry for help? Please explain."',
 editor_note="We expect this to be the most self-referential thread in Dashdot history.",
 more="",
 comments=[
  ("It's a race", "It's a race with no prize. That's what makes it pure.", "insightful"),
  ("Hall of Fame", "There should be a hall of fame for the rare person who actually gets first post AND is moderated up because it's also insightful. I've seen it happen twice.", "interesting"),
 ]),

dict(key="crapware", title="Leaked: Portals 2000 Requires 64MB and a 300MHz CPU", topic="monolith", section="",
 editor="Pixelfish", date=(10,16,10,5), dept="buy-a-new-computer dept", submitter="UpgradeUma",
 intro='"Final system requirements for Portals 2000 Professional have leaked: a 300MHz processor, 64MB of RAM, and two '
       'gigabytes of free disk space. The previous version ran happily in 16MB. Hardware vendors are said to be '
       'delighted."',
 editor_note="My first hard drive was 20 megabytes and I thought I'd never fill it.",
 more="",
 comments=[
  ("Bloat", "Every version needs twice the hardware to do the same thing. This is why I run Linix on a P166 and it flies.", "insightful"),
  ("Real requirements", "If the minimum says 64MB, you need 128MB to actually use it without swapping. Minimum requirements are written by marketing.", "informative"),
  ("Hardware makers love it", "Every new Portals release is basically a stimulus package for the RAM industry.", "funny"),
 ]),

dict(key="gpsweek", title="GPS Week Number Rollover Passed Without Incident (Mostly)", topic="bug", section="",
 editor="Rotundo", date=(10,14,8,0), dept="practice-run dept", submitter="NavNerd",
 intro='"Remember the GPS week rollover in August, when the 10-bit week counter wrapped from 1023 to 0? A survey of '
       'readers finds that most receivers handled it fine, a few thought it was 1980, and one hiker reports his '
       'handheld insisted he was standing in the middle of the Pacific Ocean for three days."',
 editor_note="Consider it a dress rehearsal for New Year's. The ocean part was a nice touch.",
 more="",
 comments=[
  ("1980", "My car's nav system thought it was 1980 for a week. It kept trying to route me to a mall that was torn down in 1991.", "funny"),
  ("Firmware updates", "Most manufacturers had firmware updates out months in advance. The people who got bitten were the ones who never update anything, which is most people.", "informative"),
 ]),

dict(key="jolt_lang", title="Solar Microsystems Releases Jolt 2 Platform", topic="news", section="",
 editor="Hemlock", date=(10,16,7,45), dept="write-once-debug-everywhere dept", submitter="CoffeeCoder",
 intro='"Solar has released the Jolt 2 SDK, with a new graphics toolkit, a faster virtual machine and a 20MB download. '
       'The new HotStove compiler promises speeds \'approaching C\' on long-running server code, as long as you don\'t '
       'mind waiting for it to warm up, which takes about as long as a pot of coffee."',
 editor_note="Applets are dead, long live servlets.",
 more="",
 comments=[
  ("Servers", "Jolt on the server is where it's actually going. Nobody wants applets. Everybody wants a garbage-collected language for their middleware.", "insightful"),
  ("20MB", "A 20MB download on a 56k modem is about an hour, if nobody picks up the phone.", "funny"),
 ]),

dict(key="ecommerce_xmas", title="Online Retailers Brace for First 'E-Christmas'", topic="internet", section="",
 editor="CmdrGrits", date=(10,17,8,20), dept="ho-ho-http dept", submitter="ShopperSheila",
 intro='"Analysts predict this will be the first holiday season where millions of people do their shopping online. '
       'Toy sites like <A HREF="@RING:etoyz@">eToyz</A> are hiring warehouse staff by the thousand, and auction sites '
       'like <A HREF="@RING:ubid@">uBid</A> are bracing for a flood of novelty plush toys. Shipping companies say they '
       'are ready. Shipping companies always say they are ready."',
 editor_note="Prediction: at least one large web store will promise delivery by Christmas and deliver in February.",
 more="",
 comments=[
  ("Fulfillment is the hard part", "Taking orders on a web page is easy. Getting a box to a house in three days is hard. The companies that win this season will be the ones with warehouses, not the ones with the coolest Flash intro.", "insightful"),
  ("I'm shopping offline", "I'm going to an actual store, where I can touch the thing and take it home today. Call me old fashioned.", "interesting"),
 ]),
]

# ---------------------------------------------------------------------------
# Generic comment pool for filling threads (subject, body, kind)
GENERIC = [
 ("first post!", "first post!!!1 woohoo", "first"),
 ("FP", "Frist psot. Ha! In your face, everybody who has a job.", "first"),
 ("First post!!", "I got first post! Hi mom!", "first"),
 ("Does it run Linix?", "But does it run Linix?", "funny"),
 ("Beowulf", "Imagine a Beowulf cluster of these.", "funny"),
 ("Hmm", "I wonder how long until someone ports Doom to it.", "funny"),
 ("Interesting, but...", "This is interesting, but I think the article misses the bigger picture. Technology like this only matters when it gets cheap enough for ordinary people. Until then it's a toy for people who read Dashdot. Which, admittedly, is us.", "insightful"),
 ("Old news", "This was on a mailing list I read three weeks ago. Dashdot, always first with yesterday's news.", "flamebait"),
 ("Read the article", "Did anyone actually read the article? Half the comments here are answering questions that are answered in the second paragraph.", "insightful"),
 ("BSD: a eulogy", "Sad news, everyone. Analysts at a firm I just made up report that BSD now runs on fewer than 4% of servers, down from 4.1% last spring. Even the daemon mascot has been seen updating his resume. Gather round, friends, and light a candle for the little OS that could, but statistically shouldn't.", "troll"),
 ("Offtopic, but", "Offtopic, but does anyone know how to get a Sound Blaster 16 working under the new kernel? It just beeps at me. Rhythmically.", "offtopic"),
 ("Karma", "I'm posting this to burn karma. Please mod me down so I can feel something.", "offtopic"),
 ("Slashdotted", "Site's already slashdotted. Er, dashdotted. Anyone have a mirror?", "informative"),
 ("Mirror", "Mirror here, while it lasts: it's on my cable modem so be gentle.", "informative"),
 ("Who cares", "Why is this news for nerds? This is news for people who like being angry at things.", "flamebait"),
 ("Boring", "Another day, another story about a chip that is 8% faster. Wake me when they invent the flying car. Or at least the flying modem.", "troll"),
 ("Portals sucks", "This is why Portals sucks. I've been saying it for years. Install Linix. Problem solved.", "flamebait"),
 ("The real problem", "The real problem here is management. Engineers know how to build things right; management sets a deadline that makes it impossible, and then acts surprised when it ships broken. Every single time.", "insightful"),
 ("Meh", "Meh. Wake me up when it's open source.", "flamebait"),
 ("Moderators on crack", "Why was my last post moderated down as Offtopic? It was totally on topic. Moderators must be on crack today.", "offtopic"),
 ("Answer: 42", "The answer, of course, is 42. What was the question?", "funny"),
 ("Year 2000", "Just wait until January. Then we'll see who's laughing. (Probably everyone. The answer is probably everyone.)", "funny"),
 ("My experience", "I've been working in this industry for 15 years, and I can tell you that this kind of thing comes around every five years with a new name. The underlying ideas don't change much; the marketing does.", "insightful"),
 ("Links", "For anyone who wants to read more, the original announcement is on their site and there's a good technical write-up in the newsgroups. Search for it, the link is too long to paste.", "informative"),
 ("Correction", "Small correction to the story: it's not the first time this has been done. A university group demonstrated something very similar in 1996. The difference is that this one actually ships.", "informative"),
 ("Hmm, not so sure", "I'm not so sure this is good news. Every time someone says 'this will change everything', it changes about 3% of something.", "interesting"),
 ("Re: real world", "In the real world, nobody cares about this stuff. They care whether their e-mail works.", "interesting"),
 ("lol", "lol", "offtopic"),
 ("Jolt", "I'm going to need another case of Jolt to read all these comments.", "offtopic"),
 ("Grammar", "It's 'its', not 'it's'. Doesn't anyone proofread these stories? ;-)", "offtopic"),
 ("Profit", "Step 1: write story. Step 2: get 300 comments. Step 3: ...", "funny"),
 ("Information wants to be free", "Information wants to be free. Hardware wants to be cheap. I want a nap.", "funny"),
 ("Microwave", "My microwave has more processing power than the computer that went to the moon, and it still can't figure out popcorn.", "funny"),
 ("Standards", "This is why we need open standards. Without them every vendor builds a little walled garden and the users pay for the walls.", "insightful"),
 ("Hype", "The hype-to-substance ratio on this one is pretty high. Let's see it running in production before we all get excited.", "interesting"),
 ("Re: First post", "Not even close to first post. You lose. Good day sir.", "offtopic"),
]

# Replies: bodies used for responses (subject will be "Re: <parent subject>")
REPLIES = [
 ("Agreed. Couldn't have said it better myself.", "interesting"),
 ("I think you're missing the point. Nobody is arguing it's perfect, just that it's better than what we had.", "insightful"),
 ("Citation needed. Where are you getting these numbers?", "interesting"),
 ("You must be new here.", "funny"),
 ("Whoosh. That was the sound of the joke going over your head.", "funny"),
 ("Not true at all. I've been running it for months with no problems. Maybe check your hardware?", "informative"),
 ("This is the most sensible thing I've read on Dashdot all week. Somebody mod this up.", "insightful"),
 ("Funny, I had the exact opposite experience. Ymmv, I guess.", "interesting"),
 ("Actually, that's a common misconception. The spec explicitly allows it; it's the vendors who didn't implement it.", "informative"),
 ("Don't feed the trolls.", "offtopic"),
 ("Mod parent up!", "offtopic"),
 ("Mod parent down! Flamebait.", "offtopic"),
 ("You're both wrong, and I'm going to explain why in a post that's way too long for anyone to read. Paragraph one: ...", "funny"),
 ("I work in this field, and the parent is basically right, although the details are a bit more complicated than one comment can cover.", "informative"),
 ("Thanks for posting this. I learned something today, which is rare for a comment section.", "interesting"),
 ("Heh. Nice one.", "funny"),
 ("Says the guy posting at 3am on a Tuesday.", "funny"),
 ("Did you even read the parent post? He said the opposite.", "interesting"),
 ("Wait until you see the next version. It's going to be worse.", "funny"),
 ("Source? My brother-in-law says otherwise, and he has a Pentode.", "funny"),
 ("Exactly. And the vendors know it, which is why they're scared.", "insightful"),
 ("This. A thousand times this.", "interesting"),
 ("No, that's not how any of this works. Please read the FAQ before posting.", "flamebait"),
 ("I tried that and it set my monitor on fire. Thanks a lot.", "funny"),
 ("Real men use a magnetized needle and a steady hand.", "funny"),
 ("So what you're saying is that it's a conspiracy. Got it.", "flamebait"),
 ("The parent's point stands, though: it depends entirely on the use case.", "insightful"),
 ("Hey, at least it's not Portals.", "funny"),
]

# Registered users. nick -> (uid, karma, bio)
USERS = [
 ("frostbyte", 4120, 23, "Embedded systems by day, fridge hacker by night."),
 ("overclocked_otter", 13377, 41, "My CPU runs at 112% and so do I."),
 ("Prior Art Pete", 2201, 55, "Collector of 1980s shareware and patent office rejection letters."),
 ("kernel_kid", 30217, 18, "make bzImage && make modules && pray"),
 ("RetroRaccoon", 9011, 12, "Owns every console ever made except the one you're thinking of."),
 ("sysadmin_steve", 552, 61, "BOFH in training."),
 ("Speculatron", 17840, 9, "Rumors, hearsay and wild guesses since 1997."),
 ("dormroom_dj", 40112, 4, "128kbps or bust."),
 ("WindowManiac", 22053, 15, "Tried every window manager. Currently on number 31."),
 ("RocketRandy", 6610, 30, "Amateur rocketry. Professional singed eyebrows."),
 ("Linixdvd", 33303, 7, "Just want to watch my movies."),
 ("DayTraderDan", 41871, -2, "Bought high, sold higher, bought higher."),
 ("LawGeek", 1987, 72, "IANAL, but I play one on Dashdot."),
 ("NodeNinja", 29180, 20, "16 nodes is not a cluster, it's a start."),
 ("GeckoGuy", 15550, 26, "Files Mothzilla bugs as a form of meditation."),
 ("LowEarthLarry", 8008, 11, "Orbital mechanics enthusiast."),
 ("pitchfork_pete", 777, 48, "The daemon made me do it."),
 ("ClamshellCarl", 38220, 3, "Tangerine forever."),
 ("BioBob", 26601, 14, "Lab tech. Llama wrangler."),
 ("RailgunRhonda", 19990, 33, "Rail, rocket, repeat."),
 ("ParanoidPolly", 31337, 22, "This bio has been encrypted."),
 ("WebWeaver", 4404, 29, "Static HTML evangelist. Hand-coded since 1994."),
 ("MediaMaven", 21212, 8, "BeeOS user #47."),
 ("StylusSam", 35035, 5, "Writes everything in Graffiti now."),
 ("Gnuisance", 1024, 50, "Free as in speech, free as in beer, free as in lunch if you're buying."),
 ("Nervous Ned", 43210, 1, "Fully stocked. Just in case."),
 ("HexHead", 3456, 37, "0xDEADBEEF"),
 ("StargazerSue", 12121, 19, "Dark skies or bust."),
 ("DomainDave", 27272, 6, "Owns 212 domains, 211 of which are parked."),
 ("MarkupMarcy", 18181, 24, "Close your tags."),
 ("CourtWatcher", 9999, 31, "Reading trial transcripts so you don't have to."),
 ("Anthropologeek", 44444, 2, "Studying you. Yes, you."),
 ("UpgradeUma", 37373, 10, "Never met a RAM upgrade I didn't like."),
 ("NavNerd", 23023, 13, "Recalculating."),
 ("CoffeeCoder", 16161, 21, "Brewed, not compiled."),
 ("ShopperSheila", 45454, 3, "Bought her first book online in 1998 and never looked back."),
 ("perl_monger_mo", 2048, 44, "There's more than one way to do it, and I've tried them all."),
 ("cyber_wombat", 11011, 17, "Marsupial of the Information Superhighway."),
 ("Tux_Tamer", 5150, 28, "Sixteen distributions installed, zero regrets."),
 ("modem_mike", 28800, 6, "Still on 28.8. Please don't post screenshots."),
 ("ByteBandit", 32768, 12, "Ex-BBS sysop. Ask me about FidoNet."),
 ("GrumpyGreybeard", 101, 66, "Was using Unix before your parents met."),
 ("ladybug_lisp", 7070, 35, "(car (cdr life))"),
 ("JavaJunkie", 24601, 9, "One more cup of coffee before I go."),
 ("NullPointer", 1337, 27, "Segmentation fault (core dumped)"),
 ("q_bert", 36963, 4, "@!#?@!"),
 ("SpudGun", 39393, 8, "Potato-powered computing advocate."),
 ("shell_shocked", 6502, 32, "6502 assembly is the only real language."),
 ("DaemonDiva", 14641, 25, "chmod 755 my_heart"),
 ("RTFM_Ralph", 8080, 40, "Have you tried reading the manual?"),
 ("mp3_maniac", 42424, 2, "My hard drive is 90% music and 10% excuses."),
 ("PolarPenguin", 20000, 16, "Cold, but fair."),
 ("kludge_king", 3030, 38, "If it works, it's not a kludge. It's a feature."),
 ("FidoFan", 46464, 1, "Bring back the BBS."),
 ("crufty", 2525, 47, "Accumulating cruft since 1983."),
]
EDITOR_UIDS = {"CmdrGrits": 1, "Hemlock": 2, "Rotundo": 3, "jamie_k": 7, "Pixelfish": 12}

# Polls: id, question, answers [(text, votes)], comments, date string
POLLS = [
 ("y2kplans", "Where will you be when the clock strikes 2000?",
  [("At a party, like a normal person", 4210), ("In the server room, watching logs", 9872),
   ("In a bunker with 400 cans of beans", 1663), ("Asleep. It's just a number.", 6091),
   ("Rebooting something", 5327), ("Wherever CmdrGrits is", 2214)], 482, "October 18"),
 ("editor", "My one true editor is", [("vi", 12890), ("emacs", 12261), ("pico", 2830), ("ed", 941),
   ("cat > file", 631), ("A word processor (shame!)", 1889)], 1201, "October 11"),
 ("modem", "My connection to the Internet is", [("14.4 or slower (send help)", 812), ("28.8 / 33.6", 6234),
   ("56k (on a good day, 44k)", 15110), ("ISDN", 2871), ("Cable or DSL", 7712), ("A T1 at work, which is why I'm reading this at work", 11408)], 655, "October 4"),
 ("boxes", "I have root on", [("No boxes", 1820), ("1 box", 7790), ("2 boxes", 6031), ("3-5 boxes", 5544),
   ("6-10 boxes", 1902), ("11 or more boxes", 2390), ("My toaster", 1203)], 327, "September 27"),
 ("cpu", "My main box has a", [("486 or older", 1544), ("Pentium/Pentium MMX", 6012), ("Pentode II/III", 11873),
   ("Celeron (overclocked, obviously)", 9002), ("AMG K6 or Marathon", 7310), ("Something with a fruit on it", 2120),
   ("An Alpha. Show-off.", 803)], 571, "September 20"),
]

# Dashboxes on the right side
FEATURES_BOX = [
 ("slashcode", "The Dashdot source code is out under the GPL. Look upon our Perl, ye mighty, and despair."),
 ("greybeardinterview", "Our interview with Walt Ferraday, the man who wrote the payroll code in 1974, in all capital letters."),
 ("xmlhype", "Is XML the answer to everything? Readers weigh in with well-formed opinions."),
]
QUICK_LINKS = [
 ("Cool Sites:", None),
 ("Orinoco.com", "@RING:orinoco@", "(Buy a book. With one click.)"),
 ("Snapster", "@RING:snapster@", "(The labels will love this)"),
 ("CNM Interactive", "@RING:cnm@", "(Real news. Well, news.)"),
 ("Yowza!", "@RING:yowza@", "(Find stuff)"),
 ("AltaVisor", "@RING:altavisor@", "(Find more stuff)"),
 ("Hamster Shuffle", "@RING:hamstershuffle@", "(Don't ask)"),
 ("Support Dashdot:", None),
 ("Dashdot T-shirts", "shirts.html", "(Clothe yourself in Dashdot)"),
 ("Advertise here", "advertising.html", "(We have eyeballs)"),
]
FRESHBEAT = ["grepmail 3.4", "xsnow 1.40", "gkrellm-ish 0.7.2", "fetchpopmail 5.1.1", "ToastTerm 0.3",
             "libdashdot 0.0.1", "y2kcheck 1.0", "mp3blaster-lite 2.0", "sockpuppetd 0.9", "beanctl 1.2"]
