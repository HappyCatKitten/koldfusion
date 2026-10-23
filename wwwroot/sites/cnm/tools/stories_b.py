# -*- coding: utf-8 -*-
"""CNM Interactive stories, part B: BUSINESS, SCI-TECH, SPORTS. All people, firms and teams invented."""
from storymaker import S

STORIES = [

# ----------------------------------------------------------------- BUSINESS
S("BUSINESS", 20, "16:35", "netspud.ipo",
  "NetSpud.com soars 640 percent in debut; company has never sold a potato",
  "Shares of NetSpud.com, which plans to sell potatoes over the Internet, closed at $118 in their first day of trading, valuing the 11-employee company at $3.2 billion.",
  "NEW YORK (CNM) --", "From CNM Business Correspondent Marcy Feld",
  """
  NetSpud.com priced its initial public offering at $16 a share late Sunday. By the closing bell Monday, the stock had changed hands more than 40 million times and stood at $118, one of the biggest first-day gains of a year full of them.

  The Mossbank, Oregon, company says it will deliver fresh potatoes to customers' doors within 48 hours, ordered through a Web site featuring an animated spud named "Tater Tim." It has not yet shipped a potato, and its prospectus warns that it "may never be profitable, and may never have potatoes."

  "Investors are not buying potatoes, they are buying the future of potatoes," said chief executive Brent Kowalczyk, 26, who until last year managed a frozen-yogurt shop. Asked what the future of potatoes was, he said, "Online."

  Analysts were divided. "Everybody eats potatoes, and everybody will soon be online," said one technology fund manager. A more skeptical analyst noted that the company's market value now exceeds that of the entire Idaho potato crop "and the state of Idaho, possibly."

  The company's ticker symbol is SPUD. Its founders said they would celebrate with a dinner at a steakhouse, "with a baked potato, obviously, ordered the old-fashioned way."
  """,
  photo=("chart_up", "SPUD"), caption="NetSpud.com shares on Monday, their first day of trading",
  tags="dotcom"),

S("BUSINESS", 17, "16:20", "dow.record",
  "Dow ends week at record as investors shrug off Y2K jitters",
  "Blue-chip stocks closed at an all-time high Friday, as investors bet that the economy -- and their computers -- would sail smoothly into the new year.",
  "NEW YORK (CNM) --", "",
  """
  The Dow Jones industrial average rose 112.40 points Friday to close at 11,257.43, its fourth record of the month, led by gains in technology, retail and, curiously, companies that make canned soup.

  The technology-heavy Nasdaq composite index also set a record, rising 68 points to 3,742. Trading volume was heavy as many investors repositioned portfolios before the year-end holiday.

  "The market has decided Y2K is a non-event," said Walter Quigg, chief strategist at the brokerage Quigg Lammerding. "Or it has decided that if Y2K is an event, there is nothing to do about it, so you might as well buy."

  Bond prices fell slightly. Gold was little changed, despite strong demand at a Cotterville, Kansas, coin shop where the owner said customers were "buying it in small bars, like chocolate."
  """,
  photo=("chart_up", "DJIA"), caption="The Dow industrials over the past month",
  tags="y2k"),

S("BUSINESS", 15, "12:00", "daytraders",
  "Day traders swap holiday cheer for stock tickers",
  "At a storefront trading room in suburban Ohio, two dozen amateur investors are spending the holiday season staring at six monitors each -- and many say they wouldn't have it any other way.",
  "GRISTMILL FALLS, Ohio (CNM) --", "",
  """
  The Strip Mall Securities trading floor opens at 8 a.m., but most of its regulars are already waiting outside by 7:30, clutching coffee and printouts of Internet message boards.

  Inside, rows of desks hold monitors flashing green and red. Members pay $300 a month for a seat, a high-speed connection and unlimited popcorn. "It's like a casino," said one trader, "except the popcorn is better and they do not bring you drinks."

  Retired schoolteacher Lorraine Duffy, 61, says she made $14,000 in November and lost $9,000 in the first week of December. "Net, I am up," she said. "Net is a very important word here."

  Regulators have warned that most day traders lose money. Many in the room acknowledged the warnings and returned to their screens. "My wife wanted to know what I want for Christmas," said one. "I told her: volatility."
  """,
  photo=("computer", "BUY!"), caption="A day trader at Strip Mall Securities",
  tags="dotcom"),

S("BUSINESS", 13, "10:30", "online.shopping",
  "Online holiday sales triple; so do the complaints",
  "Americans are expected to spend more than three times as much online this holiday season as last year. Many are discovering that the Web is open 24 hours a day, but the warehouses are not.",
  "BELLWETHER, Iowa (CNM) --", "",
  """
  Shoppers who have embraced the Internet as a way to avoid holiday crowds are running into a new problem: the e-mail that says their order is "pending."

  A survey released Monday by the market research firm ClickCount estimated that online holiday sales would reach $9 billion, up from about $3 billion in 1998. The same survey found that one in four online shoppers had experienced a delayed or missing order.

  "I ordered a train set for my grandson on November 20," said Bellwether resident Gene Ostrander. "The Web site says it is 'in a state of fulfillment.' I do not know what state that is. Possibly Nebraska."

  Retailers insist they are hiring thousands of temporary warehouse workers and adding shipping options. Several are offering free delivery to customers who order by December 18 -- and an apology coupon to those whose orders arrive after Christmas.
  """,
  photo=("store", "ORDER NOW"), caption="Online shopping has tripled this season",
  tags="dotcom holiday"),

S("BUSINESS", 10, "14:15", "plushie.crash",
  "Plushie Pals market collapses as maker 'retires' entire line",
  "Prices for the collectible bean-filled animals plunged after their maker announced all of them would be retired at midnight on December 31.",
  "LAKE WENDELL, Minnesota (CNM) --", "",
  """
  Collectors who once paid $500 for a rare Plushie Pals walrus found that the same toy was fetching $40 on online auction sites Friday, after the manufacturer said every animal in the line would be retired at the end of the year.

  "If everything is rare, nothing is rare," said Darlene Voss, who keeps 1,100 Plushie Pals in acid-free plastic bins in her basement. "I learned that this week. It was an expensive lesson in economics."

  Toymaker Snugglemax Inc. said it had "no current plans" for the year 2000, fueling speculation of a new line. A company spokesman declined to say whether the "Millennium Moose," the final Plushie Pal, would be produced in limited quantities.

  Dealers said prices could rebound. "These things go in cycles," said one. "Collectors are like the stock market, but with tag protectors."
  """,
  photo=("chart_down", "PLUSHIE"), caption="Plushie Pals prices on one auction site this month",
  tags="holiday"),

S("BUSINESS", 7, "11:50", "isp.merger",
  "Two dial-up giants agree to $40 billion merger",
  "Hyperbaud Communications and WorldWire Online will combine to form the nation's largest Internet service provider, with 21 million subscribers and roughly as many busy signals.",
  "NEW YORK (CNM) --", "",
  """
  Hyperbaud Communications agreed Tuesday to buy WorldWire Online for about $40 billion in stock, creating an Internet giant that will serve one of every three American households that dial up to go online.

  The combined company will be called HyperWorld. Executives said customers would see "a seamless transition, faster connections and a free mouse pad."

  Wall Street reacted cautiously; Hyperbaud shares fell 6 percent. Consumer advocates said they would watch for higher prices. "Somebody will still have to answer the phone when the modem screams," said one.

  The deal must be approved by regulators and by shareholders, as well as, according to Hyperbaud's chairman, "the 2 million people who still have our CD-ROMs as coasters."
  """,
  photo=("chart_down", "HYPERBAUD"), caption="Hyperbaud shares Tuesday after the merger announcement",
  tags="dotcom"),

S("BUSINESS", 3, "15:00", "generator.boom",
  "Generator makers can't keep up with Y2K demand",
  "Manufacturers of portable generators say December orders are running at five times normal levels. Some customers are waiting until February -- after the crisis they are worried about.",
  "SAINT ULRIC, Louisiana (CNM) --", "",
  """
  The Bayou Power Equipment plant in Saint Ulric has been running three shifts a day since August to keep up with orders for its portable generators, and the backlog still stretches into next year.

  "People want them by December 31. We are telling them February 15," said sales manager Dupree Thibodeaux. "Most of them still buy one. I guess they figure there will be another emergency eventually."

  Hardware chains report similar shortages of kerosene heaters, water purifiers and flashlights. One chain has started selling a "Y2K Readiness Bundle" that includes a generator, a flashlight and a copy of a book titled Surviving the Bug.

  Economists say the surge has given a modest lift to manufacturing. "Fear is a very powerful economic stimulus," said one. "It's just not a very renewable one."
  """,
  photo=None, tags="y2k"),

S("BUSINESS", 1, "13:40", "etailer.ads",
  "Dot-coms spend millions on ads for big football game",
  "More than a dozen Internet companies, several with no revenue, have bought 30-second spots during next month's championship game at a record price of $2.2 million each.",
  "NEW YORK (CNM) --", "",
  """
  It may be the most expensive half-minute of the millennium. Television executives say Internet start-ups have bought nearly half the commercial time in January's championship football broadcast, at an average price of $2.2 million per 30 seconds.

  Among the buyers are an online pet-supply store, a Web site that sells office furniture, and NetSpud.com, a potato-delivery company that has not yet gone public. "Brand is everything," said NetSpud's marketing director. "Potatoes are secondary."

  Advertising executives say some of the start-ups are spending most of the money they raised from venture capitalists on the single ad. "It is a bold strategy," one said. "Boldness is what they are selling."

  The network said it still had a few spots left, "for any company with a URL and a dream."
  """,
  photo=("stadium", "AD"), caption="Championship game ads have become a dot-com status symbol",
  tags="dotcom sports"),

# ----------------------------------------------------------------- SCI-TECH
S("TECH", 20, "11:15", "bug.fixers",
  "Retired COBOL programmers called back for last-minute Y2K fixes",
  "The hottest job in technology this month belongs to programmers in their 60s and 70s who still remember how the old mainframe code was written -- because they wrote it.",
  "GRISTMILL FALLS, Ohio (CNM) --", "From CNM Sci-Tech Correspondent Raj Pemberton",
  """
  Harold Snedeker retired from the Ohio Mutual insurance company in 1986, taking with him a gold watch and an intimate knowledge of 400,000 lines of COBOL he had written in the 1970s. This month, the company asked him to come back.

  "They said, 'Harold, did you store the year as two digits?' and I said, 'Of course I did. Memory cost a fortune,'" said Snedeker, 71. "Then they asked how much I would charge to fix it. I told them. They said yes very quickly."

  Recruiters say experienced mainframe programmers are commanding $150 an hour or more in the final weeks before January 1. Some companies have flown retirees in from Florida and Arizona, complete with spouses and golf clubs.

  The work is tedious: searching for date fields, expanding them to four digits and testing the results. Snedeker works from a folding table in the company's basement next to a mainframe he describes as "an old friend who never learned to count past 99."

  "The young people ask me why we did it this way," he said. "I tell them, 'We didn't think anyone would still be using this in 2000.' Then they look at the computer, and they look at me, and nobody says anything."
  """,
  photo=("computer", "19100"), caption="A mainframe date field, before and after the fix",
  tags="y2k"),

S("TECH", 18, "09:40", "browser.war",
  "Browser war: Netscope, Explorist trade blows over new versions",
  "The two leading Web browsers released new versions within hours of each other this week, each promising to be faster, more secure and better at displaying blinking text.",
  "CEDAR NOTCH, Colorado (CNM) --", "",
  """
  Netscope Communications released a test version of its Navigator 5 browser Thursday morning. By Thursday afternoon, Cascade Software had answered with a new release of its Internet Explorist, along with a press release calling its rival's product "a 1997 browser in a 1999 hat."

  Netscope says its new version will load pages 40 percent faster and include a built-in "Smart Bookmarks" feature. Cascade says Explorist 5.5 offers "unmatched integration" with its Panes operating system, which critics say is exactly the problem.

  Web designers, caught in the middle, are building pages that work in both browsers -- or posting small buttons that say "Best viewed in" one or the other. "I have three versions of every page," said one designer. "And a fourth that just says 'please upgrade.'"

  Industry analysts say Explorist now holds about 70 percent of the market. Netscope fans remain fiercely loyal. "It is not about market share," said one. "It is about the little lighthouse logo."
  """,
  photo=("computer", "LOADING"), caption="The two rival browsers, side by side",
  tags="dotcom"),

S("TECH", 16, "14:50", "pentagon.chip",
  "Megahertz Micro unveils 800 MHz chip, promises 'end of waiting'",
  "Megahertz Micro says its new Pentagon IV processor is so fast that users will no longer have time to get coffee while their computers start up.",
  "MOSSBANK, Oregon (CNM) --", "",
  """
  Megahertz Micro on Thursday introduced the Pentagon IV, an 800-megahertz processor the company says is the fastest ever sold for personal computers.

  "With the Pentagon IV, the waiting is over," said marketing chief Dana Ruiz, as a demonstration machine opened a spreadsheet in what she called "the blink of an eye, or two blinks, if the spreadsheet is large."

  The chip will appear first in high-end desktop PCs priced around $2,800. Analysts expect rival chipmakers to answer with 850 or even 1,000 MHz parts next year. "This is the megahertz war," said one. "Everyone is winning, especially the heat-sink industry."

  Early testers said the chip ran warm. A company engineer acknowledged that during one benchmark, "a nearby muffin was noticeably toasted."
  """,
  photo=("computer", "800 MHz"), caption="A demonstration PC powered by the new chip",
  tags=""),

S("TECH", 14, "17:05", "snapster.sued",
  "Record labels sue song-swapping service Snapster",
  "The music industry has filed suit against Snapster, a free program that lets college students trade songs over the Internet, calling it \"the biggest record store in the world, without a cash register.\"",
  "SAN ESTEVAN, California (CNM) --", "",
  """
  Five major record companies filed suit Tuesday against Snapster Inc., the 19-employee start-up whose free software lets users share music files stored on their computers.

  Snapster, written by a 19-year-old college dropout during his winter break, has spread rapidly on campuses, where students with fast dormitory connections can download a song in minutes. Some universities say the program is clogging their networks.

  "This is theft, plain and simple," said the head of a recording industry trade group. Snapster's lawyer countered that the company "does not store a single song. We just introduce people to each other. Musically."

  Students interviewed on one campus seemed unconcerned. "I have 3,000 songs," said one sophomore. "I have listened to maybe 40 of them. Downloading them is the fun part."
  """,
  photo=("computer", "MP3"), caption="The Snapster program running in a college dorm room",
  tags="dotcom music"),

S("TECH", 11, "10:05", "mars.probe",
  "Mars lander falls silent; scientists keep listening",
  "Engineers have heard nothing from the Martian Polar Prober since it began its descent Friday. They hope it is merely shy.",
  "CEDAR NOTCH, Colorado (CNM) --", "",
  """
  Flight controllers at the National Space Exploration Office sent dozens of commands Saturday to the Martian Polar Prober, which was scheduled to land near the planet's south pole Friday afternoon. None has been answered.

  "We are not giving up," said mission manager Dr. Constance Yee. "Mars is 150 million miles away. Sometimes the mail is slow."

  The $165 million spacecraft was designed to dig for water ice using a robotic arm. Engineers say it may have landed safely but with its antenna pointed the wrong way, or may have had a harder landing than planned.

  Scientists will continue listening through the end of the month, including from a radio dish in the Marisol Islands, whose government has offered "the first antenna of the new millennium."
  """,
  photo=("space", "MARS"), caption="An artist's rendering of the Martian Polar Prober",
  tags=""),

S("TECH", 8, "15:30", "robo.rover",
  "Robot dog is year's hottest $2,500 gift",
  "A shiny robotic puppy that wags its tail, chases a ball and costs as much as a used car sold out in 20 minutes online.",
  "HALCYON SPRINGS, Florida (CNM) --", "",
  """
  The Robo-Rover, a silver robotic dog made by the electronics firm Kitamura, went on sale on the Internet Wednesday morning. All 5,000 units were sold in 20 minutes, the company said.

  The dog can walk, sit, wag its tail and recognize a pink ball. It does not shed, bark at the mail carrier or need to be walked, though owners can take it for a walk "for its morale," according to the manual.

  "It is the perfect pet for the year 2000," said Halcyon Springs resident Tom Larkspur, who got through on his fourth try. "It doesn't eat, and it doesn't care that I work 80 hours a week."

  Kitamura says it will make more next year. Meanwhile, the dogs are reselling on online auction sites for up to $6,000. "The resale market is very strong," said one dealer. "Stronger than the dog, actually."
  """,
  photo=("store", "ROBO-ROVER"), caption="The Robo-Rover chasing its pink ball",
  tags="holiday"),

S("TECH", 5, "12:30", "fuzzle.hack",
  "Hobbyists hack talking toy to recite stock quotes",
  "A group of engineers has reprogrammed the Fuzzle, last year's must-have talking toy, to read out the Nasdaq.",
  "SAN ESTEVAN, California (CNM) --", "",
  """
  The Fuzzle, a furry owl-like toy that babbles in its own language, sold millions last holiday season. Now a group of hobbyists says it has taught one to speak English -- specifically, the language of Wall Street.

  "It says, 'Fuzzle loves Nasdaq up 40,'" said hobbyist Wendell Ong, who posted instructions on his home page. "It says it with real feeling."

  The modification requires opening the toy, removing a chip and soldering in a new one connected to a modem. The toy's maker said it did not endorse the hack, and warned that it voids the warranty "and possibly the toy's sense of self."

  Ong's Web site has received more than 200,000 visitors this week. He says his next project is a Fuzzle that reads e-mail aloud "in a very, very small voice."
  """,
  photo=None, tags="dotcom"),

S("TECH", 2, "16:00", "modem.56k",
  "Survey: Most Americans still connect at 28.8 or slower",
  "Despite ads for 56K modems and 'blazing' cable connections, a new survey finds most home Internet users are still waiting -- and waiting -- for pages to load.",
  "BELLWETHER, Iowa (CNM) --", "",
  """
  About 62 percent of American households with Internet access connect through a modem rated at 28.8 kilobits per second or slower, according to a survey released Thursday by the research firm NetMetrics.

  Only 4 percent have high-speed cable or digital-subscriber-line connections, though the number is growing. "Most people are surfing the Web in a canoe," said NetMetrics analyst Jo Haddad.

  The survey found that the average home user spends 14 minutes a week watching a progress bar. Asked what they do while pages load, respondents most often listed "make a sandwich," "check the other phone line" and "sigh."

  Cable companies are rushing to wire neighborhoods, but many rural areas are not expected to have high-speed service for years. "We are told it is coming," said one Bellwether resident. "So is the year 2000, and that is on time."
  """,
  photo=("chart_up", "56K"), caption="Home connection speeds, according to the survey",
  tags="dotcom"),

# ----------------------------------------------------------------- SPORTS
S("SPORTS", 19, "23:30", "lobstermen.win",
  "Lobstermen clinch playoff berth with overtime win in snow",
  "The Port Halloway Lobstermen beat the Gristmill Falls Grinders 23-20 in overtime Sunday in a game played in a foot of snow.",
  "PORT HALLOWAY, Maine (CNM) --", "",
  """
  Quarterback Danny Thibault's 6-yard touchdown run in overtime gave the Lobstermen a 23-20 victory over the Grinders on Sunday and clinched Port Halloway's first playoff appearance since 1987.

  The game was played in a driving snowstorm, with groundskeepers using leaf blowers to clear the yard lines between plays. At one point, a punt disappeared into a drift and was ruled dead by an official who "could not, in good conscience, look for it."

  "This team has heart," said Lobstermen coach Burt Laliberte. "It also has very good boots. I want to thank the boot sponsor."

  The Lobstermen (10-5) will host a playoff game in two weeks -- on January 2, 2000, which the team's marketing office has already christened "the first game of the millennium."
  """,
  photo=("stadium", "23-20"), caption="Snow covers the field at Lobstermen Stadium during Sunday's game",
  tags="weather"),

S("SPORTS", 16, "21:45", "fruitcake.bowl",
  "Fruitcake Bowl matchup set: Twin Forks State vs. Saint Ulric Tech",
  "The 41st Fruitcake Bowl will match two teams that have never met, in a game sponsored by the nation's largest maker of the holiday's most regifted food.",
  "SAINT ULRIC, Louisiana (CNM) --", "",
  """
  Bowl organizers announced Thursday that Twin Forks State (8-3) will face Saint Ulric Tech (9-2) in the Fruitcake Bowl on December 29, the last bowl game of the century.

  The winner will receive the traditional trophy: a 40-pound bronze fruitcake. Each player will also receive an actual fruitcake. "Many of them will give it to someone else," a bowl official acknowledged. "That is part of the tradition."

  Twin Forks State features the nation's leading rusher, senior tailback Marcus Oyelaran, who ran for 1,840 yards this season. Saint Ulric Tech's defense allowed only 11 points a game.

  Tickets are still available. Organizers promised a halftime show featuring 300 marching-band members dressed as candied cherries.
  """,
  photo=("trophy", "FRUITCAKE BOWL"), caption="The Fruitcake Bowl trophy weighs 40 pounds",
  tags="holiday"),

S("SPORTS", 14, "22:10", "curling.millennium",
  "Curling team plans to throw first stone of the millennium",
  "A Minnesota curling club says it will deliver a stone at the stroke of midnight on New Year's Eve, making it -- by its own count -- the first sporting event of the year 2000.",
  "LAKE WENDELL, Minnesota (CNM) --", "",
  """
  Members of the Lake Wendell Curling Club will gather on the frozen lake at 11:55 p.m. on December 31 and, as the clock strikes midnight, slide a 42-pound granite stone toward the target.

  "We will have the first sporting event of the new millennium," said skip Gunnar Halvorsen. "Unless someone in the Marisol Islands is doing something, in which case we will have the first one in Minnesota."

  The club has invited spectators, though it warned that the event could last as little as 12 seconds. A hot-dish supper will follow.

  Halvorsen said the club had considered the possibility of Y2K problems. "The ice does not use computers," he said. "The scoreboard is a chalkboard. We are ready."
  """,
  photo=("snow", "CURLING"), caption="The Lake Wendell Curling Club practices on the lake",
  tags="millennium y2k"),

S("SPORTS", 11, "18:30", "scorpions.coach",
  "Scorpions fire coach after 1-11 season, hire his twin",
  "The Dry Spoon Scorpions dismissed head coach Ray Bixby on Saturday and promptly replaced him with his identical twin brother, Roy.",
  "DRY SPOON, Arizona (CNM) --", "",
  """
  The Dry Spoon Scorpions ended a dismal season with a surprising change at the top: they fired coach Ray Bixby and hired his twin brother, Roy, a longtime assistant with another team.

  "We wanted a fresh face," said team owner Lyle Garrity. Asked whether it was in fact the same face, he said, "Fresh in spirit."

  Roy Bixby said he and his brother have "very different philosophies," noting that he prefers to pass on third down. Ray Bixby said he wished his brother well and planned to attend games "in a fake mustache, so people can tell us apart."

  The Scorpions finished 1-11, their only win coming against a team whose bus broke down in the desert and arrived at halftime.
  """,
  photo=("portrait", "COACH"), caption="New Scorpions coach Roy Bixby (or possibly Ray)",
  tags=""),

S("SPORTS", 7, "20:00", "golf.y2k",
  "Golf tour reschedules January event over Y2K worries",
  "A professional golf tour has moved its season-opening tournament back a week, citing concerns that the computerized scoreboards might report every player at 1900 under par.",
  "HALCYON SPRINGS, Florida (CNM) --", "",
  """
  The Sunbelt Golf Tour said Tuesday it was delaying its first event of 2000, the Halcyon Springs Classic, from January 6 to January 13 to give technicians more time to test scoring systems.

  "We did a test and the leader board showed a man at minus-1,900," said tour commissioner Doug Farnsworth. "He was very pleased. Unfortunately, it was not accurate."

  Players reacted mostly with shrugs. "One more week of vacation," said three-time tour winner Teddy Calloway. "I'll take it."

  Officials said volunteers with pencils and paper would stand by at every hole "just in case."
  """,
  photo=None, tags="y2k"),

S("SPORTS", 3, "22:40", "hockey.brawl",
  "Mascots ejected after brawl at minor-league hockey game",
  "Two team mascots -- a moose and a giant loon -- were ejected from a minor-league hockey game Friday after a scuffle at center ice during the second intermission.",
  "LAKE WENDELL, Minnesota (CNM) --", "",
  """
  The Lake Wendell Loons beat the Cedar Notch Snowshoes 4-2 Friday, but the most memorable fight of the night came between periods, when the teams' mascots collided during a T-shirt cannon contest.

  Witnesses said Mortimer the Moose, the Snowshoes' mascot, fired a T-shirt that struck Lonnie the Loon in the beak. Lonnie responded with what the league later described as "an aggressive wing."

  Both mascots were escorted from the arena and fined $50. The league said the costumes would be suspended for one game.

  "It was the best entertainment we have had all year," said season-ticket holder Ellen Trask, 72. "Better than the hockey, frankly."
  """,
  photo=("stadium", "4-2"), caption="The Lake Wendell arena, scene of Friday's mascot incident",
  tags=""),
]
