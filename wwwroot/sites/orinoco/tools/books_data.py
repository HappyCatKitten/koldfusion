# -*- coding: utf-8 -*-
# Orinoco.com catalog -- 150 invented books. Every title, author, publisher and
# blurb here is made up for the 1999 Web parody; any resemblance is a coincidence.

SUBJECTS = [
    ("comp",   "Computers & Internet"),
    ("biz",    "Business & Investing"),
    ("myst",   "Mystery & Thrillers"),
    ("scifi",  "Science Fiction & Fantasy"),
    ("lit",    "Literature & Fiction"),
    ("health", "Health, Mind & Body"),
    ("cook",   "Cooking, Food & Wine"),
    ("kids",   "Children's Books"),
    ("hist",   "History"),
    ("ref",    "Reference"),
    ("rom",    "Romance"),
    ("travel", "Travel"),
]

# subject -> list of "Title|Author|Blurb"
BOOKS = {
"comp": """
Teach Yourself Web Pages in 21 Minutes|Dale P. Korvath|From your first &lt;BLINK&gt; tag to a guestbook that actually works, this breezy guide gets you published on the Information Superhighway before your coffee gets cold.
Y2K and You: A Survival Handbook for the Digital Apocalypse|Marjorie Fennimore-Bask|Will your toaster know what year it is? Fennimore-Bask walks nervous households through bottled water, paper bank statements and the great two-digit date bug.
The Java Way: Applets, Beans and Other Caffeinated Things|Ravi Subramanyan|A friendly, coffee-stained tour of the language everyone says will run everywhere. Includes a CD-ROM with forty spinning-logo applets.
Mastering the Modem: Getting the Most from 56K|Lloyd Petrakis|Why does it screech? What is a handshake? Petrakis decodes init strings, AT commands and the mysteries of the busy signal.
Netiquette for the Clueless|Beverly Ann Toomey|Stop TYPING IN CAPITALS. A gentle guide to newsgroups, chat rooms, forwarded chain letters and the proper use of the smiley.
Database Design for Mere Mortals Who Hate Databases|Hector Valdez-Lund|Tables, keys and joins explained with recipe cards, sock drawers and a very patient golden retriever.
The Cathedral and the Lemonade Stand|Eric Mondragon|An impassioned essay on why software written by volunteers at 3 a.m. might just beat the big boys. Fiery, funny and full of footnotes.
Webmaster's Bible, Millennium Edition|Gordon T. Ashgrove|1,412 pages on frames, image maps, server-side includes and keeping your hit counter honest. The book that holds your monitor at the right height.
Spreadsheets Made Painless|Connie Wexford|Rows, columns and the dreaded circular reference, explained for people who just want the totals to add up.
Building Your Online Store in a Weekend|Trent Halvorsen|Shopping carts, secure servers and why your mother should be able to buy a sweater from your site. A blueprint for the electronic commerce gold rush.
Linux for the Rest of Us|Pavel Okonkwo|You have heard about the penguin. Now install it, configure X Windows, and impress everyone at the office with your terminal window.
The Palm of Your Hand: Living with a Personal Digital Assistant|Sandra Kiel|Graffiti, HotSync and the zen of carrying your whole life in your shirt pocket.
Hackers, Crackers and Other Snackers|Miles Odegaard|A breathless true story of teenage phone phreaks, midnight BBS raids and the federal agents who chased them.
""",
"biz": """
The Dot-Com Millionaire Next Door|Warren B. Tisdale|Meet the dentists, librarians and bus drivers who put their savings into Internet stocks and woke up rich. Tisdale explains how you can too, probably.
Who Ate My Bagel?|Dr. Spencer Hollings|A short parable about two office mice who discover that the break room has changed. Read it in an hour; quote it in meetings for a decade.
Dow 40,000: Why the Market Can Only Go Up|James K. Glassner-Hunt|A confident, chart-filled argument that stocks are cheap, the business cycle is dead and your 401(k) is about to triple.
The Seven Habits of Highly Caffeinated People|Stephen R. Covington|Begin with the end of the pot in mind. A productivity classic for the latte age.
Getting to Maybe: Negotiating When Nobody Wants to Commit|Roger Fishbein|Practical tactics for meetings, mergers and deciding where to eat lunch.
Rich Uncle, Broke Uncle|Robert Kiyomura|Two uncles, two philosophies of money, and one nephew who learns that a house is not an asset if you keep buying lawn ornaments.
Day Trading from Your Den|Kip Maranzano|Charts, chat rooms and the thrill of buying a stock at 9:31 and selling it at 9:34. Not for the faint of heart.
The Tipping Bucket|Malcolm Grayle|How small ideas spill over and become big trends, from hush puppies to yo-yos.
Business @ the Speed of Light Bulbs|William H. Goetz|A visionary look at how digital nervous systems will let companies think faster, sell more and replace all their filing cabinets.
Managing Your Boss in 30 Days|Linda Quarrington|A step-by-step program for training the person who signs your timesheet.
Mutual Funds Without Tears|Arthur Pennywhistle|Load, no-load, front-end, back-end: a plain-English tour of the fund supermarket.
The IPO Cookbook|Natalie Fronczak|From garage to Nasdaq in eighteen months. Includes sample business plans written on actual napkins.
""",
"myst": """
The Ninth Juror|Grant Halloway|A lone holdout on a murder jury begins receiving anonymous faxes. Halloway's courtroom thrillers have kept America up past bedtime for years; this is his tautest yet.
Cold Storage|Patricia Cornwall-Reyes|Chief medical examiner Kay Barlowe investigates a body found in a meat locker in a story as chilling as its setting.
The Bishop's Gambit|Thomas Arlen Venn|A chess grandmaster, a missing Vatican manuscript and a race across six European capitals.
Dead Reckoning in Duluth|Marla Petersen|Sheriff Ingrid Halvorsen returns for a frozen-lake mystery full of hotdish, gossip and a very suspicious ice-fishing shanty.
The Partner's Partner|John Gresham Beale|A young associate at a Memphis law firm discovers that the firm's biggest client is himself. Twisty, clever and impossible to put down.
Killer Spreadsheet|Ann B. Corrigan|An accountant finds a formula that should not exist -- and someone will kill to keep it hidden.
Whispers on Widow's Hill|Mary Higgins-Clarke-Dunn|A grieving widow, a lighthouse that will not stay dark and a neighbor with far too many secrets.
Silent Partner, Silent Night|Jonathan Kellermann-Price|Child psychologist Alex Delmont untangles a case of holiday kidnapping in Los Angeles.
Agent Zero Zero Nothing|Frederick Forsythe-Cole|A retired spy is drawn back into the game when his old codebook turns up in a pawn shop.
The Hacker Who Knew Too Much|Dana Kristoff|A teenage programmer stumbles on a plot to crash the world's banks on January 1, 2000.
Tinseltown Homicide|Elmore Lennard-Stiles|Hollywood stuntmen, a stolen script and dialogue sharp enough to cut glass.
Murder at the Book Club|Agatha Penhallow|When the hostess dies during a discussion of a mystery novel, the members must solve one of their own.
The Last Ferry to Nantucket|Robert Ludlow-Hart|A whistle-blower, a fog bank and an island with only one way off.
""",
"scifi": """
Penelope Pike and the Cellar of Whispers|J. K. Rowntree|An orphan with a crooked scar learns she is enrolled at a boarding school for wizards. The British sensation that has grown-ups reading under the covers.
Penelope Pike and the Prisoner of Azkharim|J. K. Rowntree|In her third year at Hogsbottom, Penelope must face an escaped prisoner who seems to be after her alone.
The Wheel of Weather, Book Nine|Robert Jordache|The saga continues as the Dragon Prince gathers his allies and tugs on many, many braids.
Neutron Valley|William Gibbons|Console cowboys and corporate samurai collide in a gleaming, grimy near future.
The Diamond Primer|Neal Stephenson-Clark|A nanotech fairy tale about a stolen interactive book and the little girl it raises.
Foundation's Basement|Isaac Asimolov|The long-awaited prequel reveals what the psychohistorians kept in storage.
The Dragons of Mumblecore|Terry Prattle|A comic fantasy in which a reluctant wizard must save a kingdom run entirely by committees.
Starship Accountants|Lois McMaster-Bujoldt|The galaxy's most dangerous job: auditing a fleet of space marines.
The Androids of Amber Lane|Philippa K. Dickens|Do mechanical people dream of suburban lawns? A haunting novel of identity and lawn care.
Ender's Brother's Game|Orson Scott Kard|Another child genius, another war, another twist ending.
Dune Buggy|Frank Herbertson|Spice, sandworms and one very ambitious off-road vehicle.
The Crystal Shard of Xanthor|Margaret Weisberg|An elf, a dwarf and a sarcastic halfling quest for a gem that may be cursed.
""",
"lit": """
The Readers' Circle|Anita Shreeve-Lane|Five women in a small Iowa town meet monthly to discuss books, and end up rewriting their own lives. A heartfelt book-club favorite.
The Poisonwood Hymnal|Barbara Kingsley|A missionary family's year in the jungle, told in five unforgettable voices.
White Teeth, Grey Skies|Zara Smithfield|A sprawling, funny novel of three families in North London.
Memoirs of a Tea Hostess|Arthur Golding|The secret world of a Kyoto teahouse, told by a woman who rose from servant to legend.
The Hours Before Lunch|Michael Cunningham-Bly|Three women, three eras, one very important sandwich.
Angela's Ashtrays|Frank McCourtney|A memoir of a childhood so miserable it is laugh-out-loud funny.
Cold Mountain Dew|Charles Frazee|A wounded soldier walks home across the Blue Ridge, and nobody offers him a ride.
The Corrections Department|Jonathan Franzwell|A Midwestern family gathers for one last Christmas, and every one of them needs fixing.
The God of Small Appliances|Arundhati Rao|Twins in Kerala, a forbidden love and a very old blender.
Snow Falling on Seedlings|David Guterson-May|A courtroom drama set among the strawberry farmers of a misty Puget Sound island.
A Map of the Whole Wide World|Jane Hamilton-Sharp|A day-care accident unravels a farm family in rural Wisconsin.
The Girl with the Pearl Necklace|Tracy Chevron|A maid in a Dutch painter's house becomes the subject of his most famous portrait.
White Oleander Blues|Janet Fitchburg|A daughter navigates foster homes while her poet mother serves time.
""",
"health": """
The Grapefruit Protocol|Dr. Barry Sears-Adkins|Eat half a grapefruit before every meal, never after six, and only while standing. A revolutionary 40-30-30-0 plan for permanent weight loss.
Chicken Noodle Soup for the Soul|Jack Canfield-Hansen|One hundred and one stories to warm the heart and clear the sinuses.
Men Are from Mars Bars, Women Are from Venus Flytraps|John Grayson|Understanding the opposite sex through the language of snacks and carnivorous plants.
Don't Sweat the Small Stuff (It's All Small Stuff, Except Taxes)|Richard Carlsbad|Simple ways to keep little things from taking over your life, with one notable exception.
Eight Weeks to Optimum Wellness, Give or Take|Andrew Weilson, M.D.|A gentle program of broccoli, breathing and ginger tea.
Tuesdays with Mortimer|Mitch Albright|A sportswriter reconnects with his old college professor for a series of profound and well-catered visits.
The Carbohydrate Detective|Rachel and Richard Hellman|Track down the hidden starches lurking in your pantry, then arrest them.
Ageless Body, Timeless Wristwatch|Deepak Chopperton|Mind-body wisdom for living longer, with a chapter on punctuality.
Simple Abundance of Stuff|Sarah Ban Breathwick|A daybook of comfort and joy, and of finding room in the garage.
Sugar Busters!|H. Leighton Stewart-Bain|Cut the sugar, cut the fat, cut out the pages and make paper snowflakes.
The 8-Minute Ab Crunch Plan|Jorge Cruz-Bento|A whole new you, in less time than it takes to microwave popcorn.
Emotional Intelligence for Dogs|Daniel Golemann|Why your terrier's EQ may matter more than his IQ.
""",
"cook": """
Joy of Cooking Again|Irma S. Rombauer-Becker|The beloved kitchen companion, revised to cover blackened fish, sun-dried tomatoes and the microwave.
The Bread Machine Bible|Beth Hensperger-Klein|Three hundred loaves you can bake while you sleep, including a respectable bagel.
How to Boil Water (and Other Advanced Techniques)|Chef Tony Barbieri|Television's friendliest chef starts at the very beginning.
The Naked Spatula|Jamie Oliveira|A cheeky young chef shows you how to throw together dinner with a scooter, a mortar and a lot of olive oil.
Back to Basics with Ina's Cousin|Rhoda Garten|Elegant Hamptons entertaining for people who live nowhere near the Hamptons.
The Cake Doctor's Waiting Room|Anne Byrn-Hollis|Doctored cake-mix recipes that will make your neighbors wonder.
Wines Under Ten Dollars|Kevin Zraly-Moss|Three hundred bottles that taste like they cost twice as much (several of them do).
Salsa, Sofrito and the Secrets of the Spice Rack|Maria Elena Robles|Bright, bold flavors from the Caribbean kitchen.
Fondue Forever|Gretchen Ammann|The seventies are back. Dust off the burner and get dipping.
The Low-Fat Fat Cookbook|Dorothy Pruitt|Everything you love, minus the part you love.
Kitchen Confidential Memos|Anthony Bordwell|A line cook's swaggering report from the steaming underbelly of the restaurant business.
Cooking for One Hundred and One|Chuck Wagner-Lowe|Church suppers, family reunions and very large weddings.
""",
"kids": """
Goodnight Mouse|Margaret Wise Browner|A small mouse says goodnight to every object in his cozy hole. A bedtime classic in the making.
The Very Hungry Llama|Eric Carlisle|A llama eats his way through a week of increasingly ridiculous snacks.
Where the Wild Socks Are|Maurice Sandak|Max sails off to the land where lost laundry goes.
Oh, the Places You'll Commute!|Dr. Seusser|Rhymes for graduates heading into their very first traffic jam.
Brown Bear, Beige Bear, What Do You See?|Bill Martini Jr.|Colors, animals and a bear with surprisingly neutral taste.
The Rainbow Trout|Marcus Pfeiffer|A shimmering fish learns that sharing scales is the key to friendship.
Goosebumps Galore #67: The Haunted Cafeteria|R. L. Steen|Something is wrong with the sloppy joes, and only Jenny can stop them.
Captain Underpants and the Attack of the Talking Toilets|Dav Pilkington|Two fourth graders and their hypnotized principal save the day, again.
Holes in the Ground|Louis Sachar-Bell|A boy at a desert camp digs one hole a day, and finds a family curse at the bottom.
The Babysitters' Union|Ann M. Martino|The girls of Stoneybrook band together to demand better snacks.
If You Give a Moose a Modem|Laura Numeroff-Bond|One thing leads to another when a moose discovers the World Wide Web.
Arthur's Y2K Adventure|Marc Brownell|Arthur worries that the computers will stop on New Year's Eve. D.W. worries about the cake.
Stellaluna's Cousin|Janell Cannonball|A fruit bat raised by owls learns to stay up late and love it.
""",
"hist": """
The Greatest Generation Gap|Tom Brockway|Stories of the men and women who won the war and then could not program their VCRs.
Guns, Germs and Steel Drums|Jared Diamante|Why some societies conquered continents, and why others developed better music.
Undaunted Courage, Undated Receipts|Stephen Ambrosio|The expense reports of the Lewis and Clark expedition, newly annotated.
Longitude and Latitude|Dava Sobelman|The story of a lone genius who solved the greatest navigational problem of his time, and then the other one.
The Professor and the Lunatic Fringe|Simon Winchell|The madcap history of the world's longest dictionary and its most enthusiastic contributors.
Flags of Our Grandfathers|James Bradford-Lee|The story behind six men and one very famous photograph.
Isaac's Storm Drain|Erik Larsen-Moss|The deadliest hurricane in American history, told through the eyes of a weatherman who got it wrong.
The Perfect Squall|Sebastian Junger-Walsh|A fishing boat, a monster storm and the families waiting on shore.
Into Thin Hair|Jon Krakauer-Bain|A gripping account of a disastrous expedition up the world's highest barbershop chair.
A Short History of Nearly Every Sandwich|Brian Byson|From the Earl to the club, a delicious romp through the history of bread-based meals.
Cod: The Fish That Changed Everything|Mark Kurlanski-Ford|A lively biography of a humble fish and the empires it built.
The Year 1000 and Some Change|Robert Lacy-Ward|What life was like at the turn of the last millennium, and what they worried about instead of computers.
""",
"ref": """
The Orinoco Pocket Dictionary of Internet Words|Editors of Orinoco.com|From "applet" to "zine," every buzzword you heard at the last cocktail party, defined in plain English.
Roget's Thesaurus of Synonyms, Words, Terms and Expressions|Peter Roget-Hayes|Find the right word, the perfect word, the apt, fitting and suitable word.
The Elements of Styling|William Strunkel and E. B. Whyte|Omit needless words. Omit them. Also, hair care.
The Chicago Manual of Style, Abridged for Commuters|University Press Editors|All the rules, now light enough to hold on the train.
The 1999 World Almanac of Things|Almanac Staff|Facts, figures and the population of every country, plus a list of the tallest roller coasters.
Grammar for Smarty Pants|Lynne Truss-Wilder|A zero-tolerance approach to the misplaced apostrophe.
The Complete Book of Flags|Margaret Vexillo|Every banner of every nation in full color, including several that changed while this book was being printed.
How Things Work, Mostly|David Macaulay-Finch|Gears, levers, microchips and woolly mammoths in an illustrated guide to the machines of daily life.
The Dictionary of Imaginary Places|Alberto Manguelli|A traveler's guide to lands found only in books.
Peterson's Field Guide to Office Birds|Roger T. Peters|Identify the Cubicle Warbler, the Lesser Water-Cooler Finch and the Middle Manager.
Bartleby's Familiar Quotations, Unfamiliar Edition|John Bartleby|Quotations you have never heard, attributed to people you have never met.
The Oxford Handbook of Cliches|Elizabeth Knowles-Penn|Avoid them like the plague; you will know them when you see them.
""",
"rom": """
The Duke and the Dot-Com Heiress|Julia Quinlan|Regency manners meet Silicon Valley money in a sparkling time-slip romance.
Highland Hearts Aflame|Diana Gabaldon-Ross|A nurse in 1946 steps through a standing stone and into the arms of a kilted Scot.
Message in a Bottle Opener|Nicholas Sparkman|A divorced reporter finds a love letter tucked into a corkscrew at a yard sale.
The Bridges of Madison Avenue|Robert James Waller-Kent|A married advertising executive and a traveling photographer share four unforgettable days in Manhattan.
Ranch of Desire|Nora Robertson|A city girl inherits a Montana ranch, and its very handsome foreman.
Hearts in Cyberspace|LaVyrle Spenser-Pratt|They met in a chat room. They live three thousand miles apart. They type very, very fast.
The Wedding Planner's Wedding|Debbie Macomberly|A woman who has organized four hundred weddings finally plans her own.
Stormwatch Lighthouse|Linda Lael Millerson|A keeper's widow and a shipwrecked stranger weather a Maine winter together.
Dangerous Dreams of the Bayou|Sandra Browne-Lee|Steamy Louisiana suspense with an alligator or two.
Love in the Time of Pagers|Gabriela Marquez-Soto|A doctor and his beloved keep missing each other's pages for fifty years.
The Lord of Thornfield Glen|Mary Jo Putney-Burke|A wounded war hero and a spirited governess find healing in the Yorkshire moors.
Sweet Valley Retirement Village|Francine Pascal-Moore|The beloved twins are back, and they are taking up shuffleboard.
""",
"travel": """
Frommer's Europe on Five Dollars a Week|Arthur Frommerman|Cheap rooms, cheaper meals and how to sleep in a train station with dignity.
A Walk in the Parking Lot|Bill Bryston|An out-of-shape writer sets out to walk across the mall's entire parking structure.
Under the Tuscan Sunscreen|Frances Mayes-Lowry|An American poet buys a crumbling villa and discovers olives, plumbing and SPF 30.
Lonely Planet Neptune|Tony Wheelwright|Off-the-beaten-path tips for the outer solar system, including where to change money.
The Rough Guide to the Information Superhighway|Angus Kennard|Rest stops, toll booths and scenic overlooks of the World Wide Web.
Let's Go Nowhere: A Guide to Staying Home|Harvard Student Agents|The budget traveler's best friend for the year we all stay in for Y2K.
Notes from a Tiny Island|Bill Bryston|A fond farewell tour of Britain by an American who kept getting lost.
Fodor's Guide to Your Own Backyard|Eugene Fodorsky|Hidden gems within forty feet of your patio door.
Road Trip America, Route 66 and a Half|Jamie Jensen-Hart|Diners, motor courts and the world's largest ball of twine.
In a Sunburned Country Club|Bill Bryston|An affectionate look at Australia's golf courses and the creatures that live on them.
Eat, Drive, Lodge|Elizabeth Gilmore|A recently divorced writer drives across Ohio in search of the perfect pancake house.
The Hitchhiker's Atlas|Douglas Adamson|Towel not included.
""",
}

PUBLISHERS = ["Pemberton House", "Larchmont & Finch", "Quill & Abacus Press", "Bitstream Books",
              "Saltmarsh Publishing", "Hollowbrook", "Kettle Moraine Press", "Silver Thimble Books",
              "Harbinger & Sons", "Tumbleweed Editions", "Gibson Mainframe Press", "Orchard Lane Books"]

REVIEW_PLACES = ["Duluth, MN", "Tacoma, WA", "Bangor, ME", "Boise, ID", "Tulsa, OK", "Albany, NY",
                 "Fresno, CA", "Savannah, GA", "Toledo, OH", "Provo, UT", "Lubbock, TX", "Cedar Rapids, IA",
                 "Burlington, VT", "Mobile, AL", "Reno, NV", "Madison, WI", "Anchorage, AK", "Topeka, KS",
                 "Ottawa, Canada", "Leeds, England", "Perth, Australia", "Hilo, HI", "Asheville, NC",
                 "Missoula, MT", "Dayton, OH", "Santa Fe, NM"]

REVIEWERS = ["A reader", "A reader", "A reader", "A customer", "bookworm42", "Marge K.", "Dennis T.",
             "A homeschooling mom", "A retired engineer", "night_owl_reader", "Professor Pete",
             "A grateful dad", "Lisa from accounting", "J. Okafor", "A satisfied customer",
             "R. Delgado", "The Book Nook Gang", "Sid V.", "GrannyReads", "techie99", "Pam W.",
             "a long-time Orinoco customer", "Chris in the kitchen", "A teacher"]

REVIEW_TITLES = {
    5: ["Couldn't put it down!", "Best book I've read this year", "A must-read", "Wow. Just wow.",
        "Buy two -- one to lend", "Five stars is not enough", "Stayed up until 3 a.m.",
        "Finally, a book that delivers", "My new favorite", "Read it in one sitting"],
    4: ["Very good, with a few slow spots", "Worth your time", "Solid and enjoyable",
        "Great gift idea", "Almost perfect", "Recommended"],
    3: ["Good, not great", "Some gems, some filler", "Okay for the beach", "Mixed feelings",
        "Fine, I guess"],
    2: ["Disappointing", "Expected more", "Not for me", "Wanted to like it"],
    1: ["Save your money", "Used it as a doorstop", "What were they thinking?", "Ugh"],
}

REVIEW_BODIES = {
    5: ["I bought this on a whim and ended up recommending it to everyone at work. {a} has a real gift for making you care about every page.",
        "This is the kind of book you press into a friend's hands. I have already ordered three more copies for the holidays.",
        "I read a lot of books in this category and this one is head and shoulders above the rest. Clear, smart and genuinely fun.",
        "My husband kept asking why I was laughing out loud in bed. Then he read it and kept me up laughing.",
        "I was skeptical after all the hype, but it lives up to every bit of it. The last chapter alone is worth the price.",
        "Shipping from Orinoco took two days and I finished the book in one. Fantastic.",
        "I have given this book to my sister, my neighbor and my dentist. All three called to thank me.",
        "I read the first page in the store, the next fifty in the parking lot and the rest that night. Highly recommended.",
        "Our book club picked this one and for once everybody actually finished it. We talked for three hours.",
        "Every so often a book comes along that you want everyone to read. This is that book for 1999.",
        "Smart, funny and surprisingly moving. I did not expect to cry on the bus, but here we are.",
        "I am not usually a fan of this genre, but {a} won me over by chapter two."],
    4: ["A very satisfying read. A couple of chapters drag in the middle, but the payoff is worth it.",
        "Not quite as good as {a}'s earlier work, but still well above average. I would read the next one.",
        "Useful, well organized and pleasant to read. Knocked off one star because the index is thin.",
        "I enjoyed this a great deal. It is not life-changing, but it is a good companion for a long weekend.",
        "Very readable, with a few moments of real brilliance. The ending felt a little rushed to me.",
        "Good value for the price, and Orinoco had it on my doorstep in two days.",
        "My teenager borrowed it and has not given it back, which I take as a good sign."],
    3: ["Parts of this are terrific and parts of it feel like they were written to fill pages.",
        "It was fine. I finished it, which is more than I can say for some books, but I will not reread it.",
        "Good ideas, uneven execution. Borrow it from the library before you buy."],
    2: ["I really wanted to love this after reading the other reviews, but it never grabbed me.",
        "The cover is great. The inside, less so. Maybe I am just not the audience for it."],
    1: ["I cannot understand the rave reviews. I gave up on page 40 and I never give up on books.",
        "This book arrived in perfect condition, which is the nicest thing I can say about it."],
}

# ---- the other tabs: a small invented music and video shelf
MUSIC = """
Supernatural Mayo|Carlos Sandoval|Latin-rock guitar fireworks with a parade of guest stars. The comeback of the year.
Millennium Bugaboo|The Backalley Boys|Five harmonizing heartthrobs and thirteen songs about calling you back.
Oops, I Rebooted|Brittany Sparks|The teen-pop debut that has every middle school humming along.
Livin' la Vida Lowercase|Rocky Martinez|Shimmy-worthy dance pop with a horn section that will not quit.
Brand New Daydream|Stingray|Moody, jazzy pop from the former bass player of a famous trio.
Buena Vista Social Hour|The Havana Uncles|Gentle Cuban son recorded by legends who had been waiting for the phone to ring.
Play Nice|Mobyrd|Ambient beats stitched together with old field recordings. Every song is in a car commercial.
Fanmail from Space|TLC Corp.|Three-part R&amp;B harmonies about pagers, scrubs and the future.
Smash Mouth Wash|Sugar Ray Gun|Breezy summer rock you will hear at every barbecue until 2003.
Mambo Number Fourteen|Lou Begbie|A swing-revival novelty hit that lists every name in the phone book.
Significant Other Brother|Limp Biscuit|Rap-metal angst, turned up past eleven.
The Matrix Mixtape|Various Artists|Industrial and techno anthems for dodging bullets in slow motion.
"""

VIDEO = """
The Matrices|Keanu Reid, Lawrence Fishbourne|A hacker learns that the world is a simulation and that leather coats never go out of style. Widescreen DVD.
The Blair Switch Project|Heather Donohue-Price|Three film students, a camcorder and some extremely unsettling twigs.
Titanick: Collector's Edition|Leo DiCarpaccio|The unsinkable love story, now on two tapes.
The Sixth Sensor|Bruce Willoughby|A child psychologist and a boy who sees smoke detectors that are not there.
Austin Powwow: The Spy Who Charmed Me|Mike Meyerson|Groovy, baby. The international man of mystery returns.
Star Wars Episode One-Half|Liam Neeson-Smith|A young podracer, a trade dispute and a lot of senate hearings.
American Beauty Supply|Kevin Spacely|A suburban dad quits his job and finds himself in the cosmetics aisle.
Notting Hillside|Hugh Grantham|A shy bookshop owner and the most famous actress in the world.
Office Spaceship|Ron Livingstone-Park|A cubicle drone, a broken printer and a very red stapler, in space.
Toy Tale 2|Voices of Tim Hanks|Cowboy Woody is kidnapped by a toy collector, and Buzz leads the rescue.
"""
