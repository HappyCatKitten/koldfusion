# -*- coding: utf-8 -*-
"""The Yowza! directory: every category, cross-link and site listing.

All names, hosts and descriptions are invented for the 1999 Web parody.
Format of DIRECTORY (parsed by parse()):

    ## Path/To/Category | Optional Display Title
    @ Other/Category/Path                 a cross-link ("Name@") shown among the subcategories
    - Site Name | host | description | flags     an invented site (flags: c = cool, n = new)
    * sitename | description | flags              one of the twelve 1999-Web sites

AltaVisor's generator imports this module too: every invented host becomes a little
homepage in altavisor/web/<host>/ so links always land somewhere.
"""

# the twelve sites of the 1999 Web (folder name, title, what it is)
WEB1999 = [
    ('yowza', 'Yowza!', 'The guide to the Web: every site, sorted by a human.'),
    ('altavisor', 'AltaVisor', 'Smart is beautiful. Twenty million pages, give or take.'),
    ('askreeves', 'Ask Reeves', 'Ask a question in plain English. Reeves will see to it, sir.'),
    ('orinoco', 'Orinoco.com', "Earth's biggest bookstore (on a different river)."),
    ('ubid', 'uBid', 'Your personal trading community. Bid early, bid often.'),
    ('etoyz', 'eToyz', 'Toys delivered to your door in time for the holidays. Probably.'),
    ('petz', 'Petz.com', "Because pets can't drive. Pet food at a loss, shipped overnight."),
    ('geohoods', 'GeoHoods', 'Free homepages! Move into a neighborhood and build your own site.'),
    ('hamstershuffle', 'Hamster Shuffle', "Dancing hamsters. That's it. That's the site."),
    ('dashdot', 'Dashdot', 'News for nerds. Stuff that matters.'),
    ('snapster', 'Snapster', 'Share your music with the world. What could possibly go wrong?'),
    ('cnm', 'CNM Interactive', "The world's news leader, now on the World Wide Web."),
]

# the 14 top categories in home-page order, with the small links shown under each
TOP = [
    ('Arts_and_Humanities', 'Arts & Humanities', ['Literature', 'Photography', 'Architecture']),
    ('Business_and_Economy', 'Business & Economy', ['Companies', 'Finance', 'Jobs']),
    ('Computers_and_Internet', 'Computers & Internet', ['Internet', 'WWW', 'Software', 'Games']),
    ('Education', 'Education', ['Colleges', 'K-12']),
    ('Entertainment', 'Entertainment', ['Cool Links', 'Movies', 'Humor', 'Music']),
    ('Government', 'Government', ['Elections', 'Military', 'Law', 'Taxes']),
    ('Health', 'Health', ['Medicine', 'Diseases', 'Fitness']),
    ('News_and_Media', 'News & Media', ['Newspapers', 'TV', 'Magazines']),
    ('Recreation_and_Sports', 'Recreation & Sports', ['Sports', 'Travel', 'Autos', 'Outdoors']),
    ('Reference', 'Reference', ['Libraries', 'Dictionaries', 'Quotations']),
    ('Regional', 'Regional', ['Countries', 'Regions', 'U.S. States']),
    ('Science', 'Science', ['Animals', 'Astronomy', 'Engineering']),
    ('Social_Science', 'Social Science', ['Archaeology', 'Economics', 'Languages']),
    ('Society_and_Culture', 'Society & Culture', ['People', 'Environment', 'Religion']),
]

# home-page sub-link label -> category path
HOME_LINKS = {
    'Literature': 'Arts_and_Humanities/Literature', 'Photography': 'Arts_and_Humanities/Photography',
    'Architecture': 'Arts_and_Humanities/Architecture',
    'Companies': 'Business_and_Economy/Companies', 'Finance': 'Business_and_Economy/Finance_and_Investment',
    'Jobs': 'Business_and_Economy/Employment_and_Work',
    'Internet': 'Computers_and_Internet/Internet', 'WWW': 'Computers_and_Internet/Internet/World_Wide_Web',
    'Software': 'Computers_and_Internet/Software', 'Games': 'Recreation_and_Sports/Games/Computer_Games',
    'Colleges': 'Education/Colleges_and_Universities', 'K-12': 'Education/K_12',
    'Cool Links': 'Entertainment/Cool_Links', 'Movies': 'Entertainment/Movies_and_Film',
    'Humor': 'Entertainment/Humor', 'Music': 'Entertainment/Music',
    'Elections': 'Government/Politics/Elections', 'Military': 'Government/Military', 'Law': 'Government/Law',
    'Taxes': 'Government/Taxes',
    'Medicine': 'Health/Medicine', 'Diseases': 'Health/Diseases_and_Conditions', 'Fitness': 'Health/Fitness',
    'Newspapers': 'News_and_Media/Newspapers', 'TV': 'News_and_Media/Television', 'Magazines': 'News_and_Media/Magazines',
    'Sports': 'Recreation_and_Sports/Sports', 'Travel': 'Recreation_and_Sports/Travel',
    'Autos': 'Recreation_and_Sports/Automotive', 'Outdoors': 'Recreation_and_Sports/Outdoors',
    'Libraries': 'Reference/Libraries', 'Dictionaries': 'Reference/Dictionaries', 'Quotations': 'Reference/Quotations',
    'Countries': 'Regional/Countries', 'Regions': 'Regional/Regions', 'U.S. States': 'Regional/U_S__States',
    'Animals': 'Science/Animals', 'Astronomy': 'Science/Astronomy', 'Engineering': 'Science/Engineering',
    'Archaeology': 'Social_Science/Archaeology', 'Economics': 'Social_Science/Economics',
    'Languages': 'Social_Science/Linguistics_and_Human_Languages',
    'People': 'Society_and_Culture/People', 'Environment': 'Society_and_Culture/Environment_and_Nature',
    'Religion': 'Society_and_Culture/Religion_and_Spirituality',
}

DIRECTORY = r"""
## Arts_and_Humanities | Arts & Humanities
@ Entertainment/Movies_and_Film
@ Education/Colleges_and_Universities
- Muse-O-Matic | www.museomatic.com | random painting generator; press the button and become a modern master in 4 seconds. | c
- Culture Vulture Weekly | www.culturevulture.net | reviews of gallery openings, poetry slams and anything else with free cheese.
## Arts_and_Humanities/Architecture
- Brutalist Fan Club | www.brutalistfans.org | celebrating the world's grayest buildings, one parking structure at a time.
- Gazebo Gazette | www.gazebogazette.com | plans, photos and heated opinions about backyard gazebos.
- Skyscraper Trading Cards | www.skyscrapercards.com | collect all 88 of the world's tallest buildings. Shiny cards extra. | n
- Lighthouse Lovers Online | www.lighthouselovers.org | photos and histories of lighthouses on every coast, with a keeper's diary.
## Arts_and_Humanities/Design_Arts
- Font Foundry Freebies | www.fontfreebies.com | over 400 free TrueType fonts including 61 that look like ransom notes.
- The Clip Art Attic | www.clipartattic.com | animated GIFs: spinning globes, mailboxes, flaming skulls and under construction signs. | c
- Logo Laughs | www.logolaughs.com | a gallery of the worst corporate logos ever designed by a nephew.
## Arts_and_Humanities/Literature
@ Business_and_Economy/Shopping_and_Services/Books
- Paperback Pundit | www.paperbackpundit.com | one reader, one book a day, no spoilers (except that one time).
- The Haiku Hut | www.haikuhut.org | submit a haiku / about anything at all / we post them all here | c
- Library of Lost Endings | www.lostendings.com | readers write new final chapters for famous unfinished novels.
- Bookworm's Burrow | www.bookwormburrow.net | reading lists, book club guides and a very busy message board.
## Arts_and_Humanities/Literature/Poetry
- Rhyme Time Station | www.rhymetime.org | poetry contests every month; winners get their poem in a blinking marquee.
- Villanelle Village | www.villanellevillage.com | a whole neighborhood devoted to the villanelle. Yes, the whole thing.
- Couplets for Cats | www.catcouplets.com | poems written for, about and occasionally by cats.
- The Sonnet Machine | www.sonnetmachine.net | type fourteen words and receive a computer-generated sonnet. | n
## Arts_and_Humanities/Literature/Science_Fiction
- Rocket Pulp Archive | www.rocketpulp.com | covers and stories from the golden age of pulp science fiction magazines.
- Starship Fan Fiction Depot | www.starshipfanfic.org | thousands of stories set aboard the starship of your choice.
- Robots Who Read | www.robotswhoread.com | reviews of science fiction novels written from the point of view of a toaster. | c
## Arts_and_Humanities/Photography
- Shutterbug Central | www.shutterbugcentral.com | tips, tutorials and a weekly photo contest for amateur shooters.
- Pinhole Planet | www.pinholeplanet.org | build a camera out of an oatmeal box and take pictures with it.
- The Darkroom Door | www.darkroomdoor.net | chemistry recipes and troubleshooting for home darkrooms. Knock first.
- Digital Camera Diaries | www.digicamdiaries.com | reviews of the newest one-megapixel wonders. | n
- Sunset Photo of the Day | www.sunsetphoto.com | every day, one sunset. Thousands of them now. Still pretty.
## Arts_and_Humanities/Performing_Arts
- Community Theater Network | www.commtheater.org | find auditions, scripts and costume swaps near you.
- Mime Time | www.mimetime.com | this site intentionally left silent.
- Juggle This | www.jugglethis.net | juggling patterns animated in Java, and a forum for dropped clubs. | c
- The Kazoo Orchestra | www.kazooorchestra.org | the world's largest kazoo ensemble needs YOU.
## Arts_and_Humanities/Visual_Arts
- Velvet Painting Gallery | www.velvetgallery.com | the finest paintings on black velvet: dogs, clowns and dogs dressed as clowns. | c
- Origami Online | www.origamionline.org | step-by-step diagrams for paper cranes, frogs and a working paper modem.
- Sidewalk Chalk Society | www.chalksociety.org | photos of street chalk art before the rain.
- Pixel Pushers | www.pixelpushers.net | 16-color art made in paint programs, displayed with pride.

## Business_and_Economy | Business & Economy
@ Government/Taxes
- Dot-Com Daily | www.dotcomdaily.com | which internet startup went public today? (all of them.) | n
- The Cubicle Chronicle | www.cubiclechronicle.com | office life news, gossip and how to make a stapler fort.
## Business_and_Economy/Companies
- Acme Widget Corporation | www.acmewidget.com | makers of fine widgets since 1952. Now with a website.
- Gibson Mainframe Co. | www.gibsonmainframe.com | makers of the KoldFusion application server and very large computers. | c
- Hypertext Synergies Inc. | www.hypersynergy.com | we leverage your paradigm to empower e-solutions. Ask us how.
- Bob's Big Data Barn | www.bobsdatabarn.com | rent a rack in a converted dairy barn in Wisconsin. Cows included.
## Business_and_Economy/Companies/Computers
@ Computers_and_Internet/Hardware
- Beige Box Builders | www.beigeboxbuilders.com | custom PCs in any color as long as it is beige.
- ModemWorld | www.modemworld.com | 56K modems, cables and the noises they make. | n
- Floppy Disk Warehouse | www.floppywarehouse.com | buy 3.5" disks by the pallet. AOL coasters not included.
## Business_and_Economy/Companies/Internet_Services
- Dial-Up Depot | www.dialupdepot.net | unlimited internet access for $19.95/month. Busy signal at no extra charge.
- WebHost Wonderland | www.webhostwonderland.com | 10 MB of web space, a hit counter and your own cgi-bin.
- Banner Barn | www.bannerbarn.com | design a 468x60 banner ad for your site in five minutes.
## Business_and_Economy/Shopping_and_Services
@ Recreation_and_Sports/Toys
- Mall of the Web | www.mallofweb.com | over 1,200 stores in one virtual mall with a virtual food court.
- Coupon Clipper Online | www.couponclipper.net | printable coupons for groceries, oil changes and miniature golf.
- Shop Till You Drop.com | www.shoptillyoudrop.com | price comparisons on stereos, cameras and bread machines. | n
## Business_and_Economy/Shopping_and_Services/Auctions
* ubid | the person-to-person auction site where you can buy a used lava lamp from a stranger in Ohio. | c
- Going Going Gone | www.goinggoinggone.com | live online auctions every Thursday night for computer parts.
- Bid Bunker | www.bidbunker.com | auctions for surplus military gear, survival rations and Y2K supplies.
## Business_and_Economy/Shopping_and_Services/Books
* orinoco | the biggest bookstore on any river: millions of titles, reviews by readers, one-click everything. | c
- Dusty Shelves Used Books | www.dustyshelves.com | rare and out-of-print books from a shop with a very old cat.
- Comic Book Cavern | www.comicbookcavern.com | back issues, bags, boards and opinions.
## Business_and_Economy/Shopping_and_Services/Pets
* petz | pet food, toys and supplies delivered overnight by a talking sock puppet.
- Doggie Duds | www.doggieduds.com | sweaters, booties and Halloween costumes for small dogs.
## Business_and_Economy/Shopping_and_Services/Toys
* etoyz | an online toy store for the holidays, with gift wrap and good intentions.
- Retro Toy Attic | www.retrotoyattic.com | toys from the 70s and 80s, mostly still in the box.
## Business_and_Economy/Shopping_and_Services/Music
* snapster | swap music files with anybody, anywhere. The record companies will love it.
- CD Crate | www.cdcrate.com | new and used compact discs at prices that are only slightly too high.
- Vinyl Revival | www.vinylrevival.com | records, turntables and the people who still use them.
## Business_and_Economy/Finance_and_Investment
- Day Trader Diner | www.daytraderdiner.com | stock picks, chat rooms and a lot of coffee. | n
- Penny Stock Prophets | www.pennyprophets.com | tomorrow's big winners today, according to a guy named Ray.
- Compound Interest Calculator | www.compoundcalc.com | see how rich you will be in 2040 if you start saving right now.
- The IPO Watch | www.ipowatch.net | every internet company going public this week, plus the ones that should not.
- Mattress Money | www.mattressmoney.com | for those who trust no bank: Y2K-proof savings strategies.
## Business_and_Economy/Employment_and_Work
- JobJungle | www.jobjungle.com | search 40,000 job listings, post your resume, and get spam forever. | c
- Telecommute Today | www.telecommutetoday.com | work from home in your pajamas: tips, jobs and a support group.
- Resume Robot | www.resumerobot.com | answer twelve questions and get a resume with a lot of action verbs.
- HTML Jobs Board | www.htmljobs.net | companies desperate for people who know what a TABLE tag is. | n
## Business_and_Economy/Small_Business
- Garage Startup Guide | www.garagestartup.com | everything you need to start a company in your garage, except the garage.
- Home Business Hotline | www.homebizhotline.com | real ways to make money at home. Envelope stuffing not recommended.

## Computers_and_Internet | Computers & Internet
@ Business_and_Economy/Companies/Computers
- Bits and Bytes Weekly | www.bitsbytesweekly.com | computer news and reviews for the rest of us.
- The Y2K Clock | www.y2kclock.com | counts down the seconds until every computer explodes. Or not. | c
## Computers_and_Internet/Hardware
- Overclockers Anonymous | www.overclockersanon.org | push your processor past its limits. Fire extinguisher recommended.
- The Mouse Pad Museum | www.mousepadmuseum.com | over 900 mouse pads from trade shows around the world.
- Printer Jam Help Desk | www.printerjam.net | step-by-step help for every paper jam known to science.
- Zip Drive Zone | www.zipdrivezone.com | 100 megabytes on a single disk! Tips, drivers and the click of death. | n
## Computers_and_Internet/Internet
- Netiquette Now | www.netiquettenow.org | the rules of polite online behavior. DON'T TYPE IN ALL CAPS.
- The Webring Registry | www.webringregistry.com | find a ring for any hobby and add your page to the chain.
- How the Internet Works | www.howtheinternetworks.net | explains packets, routers and why your modem screeches.
- Cyber Cafe Finder | www.cybercafefinder.com | coffee and computers in 52 countries.
## Computers_and_Internet/Internet/Chat
- Chat Shack | www.chatshack.com | 200 chat rooms on every topic; a/s/l please.
- IRC for Beginners | www.ircbeginners.org | what is a channel op and why is everyone typing /me?
- Instant Message Gazette | www.imgazette.com | tips and tricks for every instant messenger program, plus buddy icons.
## Computers_and_Internet/Internet/World_Wide_Web
- HTML Made Easy | www.htmlmadeeasy.com | learn to build a home page in one afternoon. Blink tag lessons included. | c
- The Hit Counter Store | www.hitcounterstore.com | free odometer-style hit counters for your website.
- Under Construction Archive | www.underconstruction.org | the internet's largest collection of under construction signs.
- Browser Wars Report | www.browserwars.net | daily score of the browser battle, with charts. | n
## Computers_and_Internet/Internet/World_Wide_Web/Searching_the_Web
@ Reference
- Search Engine Showdown | www.searchshowdown.com | side-by-side tests: which engine finds your cat's homepage first?
- Meta Search Mania | www.metasearchmania.com | queries a dozen search engines at once and shows you all of it.
## Computers_and_Internet/Internet/World_Wide_Web/Searching_the_Web/Search_Engines
* altavisor | a huge index of the Web; type in any word, get back a few hundred thousand pages. | c
* askreeves | a butler who answers questions typed in plain English.
- Spider Speed | www.spiderspeed.com | a tiny search engine that indexes only pages about spiders.
## Computers_and_Internet/Internet/World_Wide_Web/Searching_the_Web/Directories
* yowza | the directory you are reading right now. Hello! | c
- The Other List | www.theotherlist.com | a directory of sites that no other directory would list.
## Computers_and_Internet/Internet/World_Wide_Web/Free_Homepages
* geohoods | free home pages in themed neighborhoods; pick an address and move right in. | c
- Pages4Free | www.pages4free.net | 5 MB of free web space in exchange for a pop-up window or two.
- HomePage Helper | www.homepagehelper.com | backgrounds, buttons and MIDI files for your free home page.
## Computers_and_Internet/Software
- Shareware Shack | www.sharewareshack.com | thousands of shareware programs; register them, you cheapskate.
- Freeware Friday | www.freewarefriday.com | a new free program every Friday. This week: a talking clock.
- Screen Saver Heaven | www.screensaverheaven.com | flying toasters, fish tanks and pipes, pipes, pipes. | c
- Patch Tuesday Tracker | www.patchtracker.com | keeping up with the fixes for the fixes.
## Computers_and_Internet/Software/Operating_Systems
- Penguin Power | www.penguinpower.org | installation help for the free operating system with the bird mascot. | n
- Blue Screen Gallery | www.bluescreengallery.com | photos of error screens in airports, banks and stadiums. | c
- DOS Prompt Nostalgia | www.dosprompt.net | C:\> tips for people who never upgraded.
## Computers_and_Internet/Software/MP3
* snapster | find and share MP3s with millions of strangers. | n
- MP3 Encoder Guide | www.mp3encoder.com | rip your CDs into files that fit on a 2 GB hard drive.
- Winamp Skins Galore | www.skinsgalore.com | make your MP3 player look like a car stereo, a toaster or a spaceship.
## Computers_and_Internet/News_and_Media
* dashdot | news for nerds, with thousands of comments on every story. | c
- Geek Gazette | www.geekgazette.com | tech headlines plus the occasional photo of a server room.
- Modem Monthly | www.modemmonthly.com | the magazine for people who care about baud rates.
## Computers_and_Internet/Programming_Languages
- Perl Pearls | www.perlpearls.org | one-line Perl scripts that do too much.
- Java Bean Counter | www.javabeancounter.com | applet tutorials and a gallery of spinning Java logos.
- The CFML Cookbook | www.cfmlcookbook.com | recipes for tag-based web applications, served hot. | n
- Basic Instinct | www.basicinstinct.net | GOTO statements and line numbers forever.

## Education | Education
- Homework Helper Hotline | www.homeworkhelper.com | answers to math questions, but you have to show your work.
- Teacher Lounge Online | www.teacherlounge.net | lesson plans, bulletin board ideas and gossip from the faculty lounge.
- Distance Learning Directory | www.distancelearn.com | earn a degree in your bathrobe from 300 accredited schools.
## Education/Colleges_and_Universities
- Campus Tour Online | www.campustour.com | virtual tours of 400 colleges, mostly of the library.
- Dorm Room Cooking | www.dormcooking.com | 101 recipes for a hot pot and a microwave. | c
- Scholarship Search | www.scholarshipsearch.org | free money for college, if you write the essay.
- Rate My Cafeteria | www.ratemycafeteria.com | students grade their college dining halls. Mystery meat gets an F.
## Education/K_12
- Recess Online | www.recessonline.com | games, jokes and science experiments for grade schoolers.
- Science Fair Central | www.sciencefaircentral.com | 200 science fair projects, including the baking soda volcano. | c
- Spelling Bee Buzz | www.spellingbeebuzz.com | practice word lists and a pronunciation guide for spellers.
- Field Trip Finder | www.fieldtripfinder.com | museums, farms and factories that let classes visit.
## Education/Educational_Software
- Typing Tutor Tower | www.typingtower.com | improve your words per minute by shooting falling letters.
- Math Blaster Fan Club | www.mathfans.net | fan site for educational games with explosions.

## Entertainment | Entertainment
- Couch Potato Central | www.couchpotato.com | TV listings, movie times and a snack recipe of the week.
- Trivia Tavern | www.triviatavern.com | live trivia games every hour; winner gets bragging rights. | c
## Entertainment/Cool_Links
* hamstershuffle | rows of dancing hamsters with a squeaky soundtrack. You will watch for longer than you think. | c
- Random Link Generator | www.randomlink.com | press the button, go somewhere. No refunds. | c
- The Useless Pages | www.uselesspages.com | a collection of the least useful pages on the Web. We are very proud. | c
- Ask the Eight Ball | www.asktheeightball.com | ask a yes-or-no question, get a mysterious answer.
- Dancing Baby Archive | www.dancingbaby.net | every version of the dancing infant animation, including the disco one. | n
## Entertainment/Humor
- Joke of the Day | www.jokeoftheday.com | a new clean joke every morning, emailed to 200,000 people.
- Lightbulb Jokes Database | www.lightbulbjokes.org | 4,000 ways to change a lightbulb. | c
- The Pun Pit | www.punpit.com | where bad jokes go to get worse.
- Office Prank Headquarters | www.officepranks.com | how to fill a cubicle with packing peanuts and other important skills.
## Entertainment/Humor/Internet_Humor
- Top Ten Signs Your Computer Is Haunted | www.hauntedpc.com | number one: it keeps playing that hamster song by itself.
- Dot-Com Name Generator | www.dotcomnames.com | generate a startup name like Zoomtastic or Cyberlicious. | n
- Email Forward Hall of Shame | www.forwardshame.com | chain letters, urban legends and the free-cookie-recipe story.
## Entertainment/Movies_and_Film
- Popcorn Critics | www.popcorncritics.com | three teenagers review every movie. They hated most of them.
- Movie Quote Quiz | www.moviequotequiz.com | guess the film from the line. Hundreds of quotes. | c
- The Space Saga Countdown | www.spacesagacountdown.com | counting the days until the new space opera prequel opens. Lines forming now.
- Witch Woods Documentary Fans | www.witchwoodsfans.com | was the shaky-camera forest movie real? Fans argue in 400 threads. | n
- Sinking Ship Shrine | www.sinkingshipshrine.com | a fan page for the 3-hour ocean liner romance. Includes 47 MIDI files.
## Entertainment/Music
@ Business_and_Economy/Shopping_and_Services/Music
- Boy Band Bulletin | www.boybandbulletin.com | news, photos and fan polls about every boy band with five members. | n
- Lyrics Locker | www.lyricslocker.com | words to over 10,000 songs, mostly typed by teenagers.
- Garage Band Gazette | www.garagebandgazette.com | unsigned bands, free MP3 downloads and a guide to annoying the neighbors.
- Ska Is Not Dead | www.skaisnotdead.org | checkered tour dates and reviews. Horn section required.
- Swing Revival Ballroom | www.swingrevival.com | find a swing dance lesson in your town. Zoot suits optional.
## Entertainment/Music/MP3
* snapster | download and share songs. All of them. Right now.
- MP3 Underground | www.mp3underground.net | legal MP3s from independent bands; really, they are legal.
## Entertainment/Television_Shows
- Alien Files Episode Guide | www.alienfilesguide.com | every episode of the conspiracy show, with a trust-no-one rating.
- Teen Drama Recap | www.teendramarecap.com | weekly recaps of every teen drama set in a small coastal town.
- Sitcom Couch | www.sitcomcouch.com | episode guides for the six-friends-in-a-coffee-shop show and its many imitators.
## Entertainment/Games_and_Toys
@ Recreation_and_Sports/Toys
@ Recreation_and_Sports/Games

## Government | Government
- Government Forms Online | www.govforms.net | download and print the forms; standing in line not required.
- Civics 101 | www.civics101.org | how a bill becomes a law, explained with cartoons.
## Government/Politics
- Pundit Pile-Up | www.punditpileup.com | every opinion column in one place. Arguments not included.
- The Bumper Sticker Archive | www.bumpersticker.org | political slogans from 1952 to 1999.
## Government/Politics/Elections
- Election 2000 Countdown | www.election2000.net | every candidate, every poll, every straw poll in every county. | n
- Register to Vote Online | www.registertovote.org | print the form, mail it in, vote in November.
- Campaign Button Collectors | www.campaignbuttons.com | collectors trade buttons from every presidential race.
## Government/Military
- Military Surplus Mall | www.surplusmall.com | wool blankets, canteens and ammo cans.
- Veterans Reunion Board | www.vetreunion.org | find old friends from your unit.
## Government/Law
- Legal Eagle Answers | www.legaleagle.com | free legal information written by law students. Not legal advice.
- Weird Laws of America | www.weirdlaws.com | it is illegal to bowl on Sundays in some towns, allegedly. | c
- Small Claims Survival Guide | www.smallclaims.net | how to sue your landlord over the security deposit.
## Government/Taxes
- Tax Form Finder | www.taxformfinder.com | every tax form ever printed, in a format your printer hates.
- April Fifteenth Panic Room | www.aprilpanic.com | last-minute tax help for procrastinators.
## Government/U_S__Government
- Federal Agency Finder | www.agencyfinder.gov | an alphabet soup of agencies, now with links.
- Y2K Preparedness Office | www.y2kprepare.gov | what the government is doing about the date problem. Please remain calm. | n

## Health | Health
- Health Answers Online | www.healthanswers.com | a medical encyclopedia written in plain English.
- Second Opinion Central | www.secondopinion.net | ask a nurse a question and get an answer within 48 hours.
## Health/Medicine
- Pill Identifier | www.pillidentifier.com | identify a pill by its shape, color and markings.
- Medical Myth Busters | www.medicalmyths.org | no, you will not catch a cold from going out with wet hair.
- Doctor Directory | www.doctordirectory.com | find a physician by specialty and zip code.
## Health/Diseases_and_Conditions
- Allergy Alley | www.allergyalley.com | pollen counts and coping tips for the sneezing season.
- Back Pain Basics | www.backpainbasics.com | exercises and advice for people who sit at computers all day.
- Carpal Tunnel Central | www.carpaltunnel.org | wrist stretches for web surfers. Do them now. | n
- Common Cold Corner | www.coldcorner.com | chicken soup recipes and what really works.
## Health/Fitness
- Step Aerobics Online | www.stepaerobics.com | routines, music and leg warmers. | c
- Cubicle Workout | www.cubicleworkout.com | ten exercises you can do at your desk without anyone noticing.
- The Tae Bo Tribune | www.kickboxtribune.com | fans of the kickboxing workout video compare bruises.
- Walk to the Fridge | www.walktothefridge.com | the minimalist fitness program. Results may vary.
## Health/Nutrition
- Low-Fat Kitchen | www.lowfatkitchen.com | 400 recipes with no fat at all, and some flavor.
- Vitamin Village | www.vitaminvillage.com | what every vitamin does, from A to zinc.
- Cabbage Soup Diet Support | www.cabbagesoup.org | a very windy support group.

## News_and_Media | News & Media
- The Morning Wire | www.morningwire.com | headlines updated every 15 minutes, all day long.
- Headline Hound | www.headlinehound.com | sniffs out news from 300 sources and lists it in one place.
## News_and_Media/Newspapers
* cnm | breaking news, weather and video clips from a cable network on the Web. | c
- Smalltown Gazette Online | www.smalltowngazette.com | the paper that covers every bake sale in Pine Hollow.
- The Daily Byte | www.dailybyte.com | an online-only newspaper published twice a day.
- Student Press Online | www.studentpress.org | high school and college newspapers that publish online.
## News_and_Media/Television
* cnm | the round-the-clock news network, now on your computer. | n
- Remote Control Review | www.remotecontrolreview.com | what to watch tonight, rated in clickers.
- Public Access Pals | www.publicaccesspals.org | fans of local cable access television, the best TV there is.
## News_and_Media/Magazines
- Zine Scene | www.zinescene.com | an index of 3,000 photocopied zines and their e-zine cousins. | c
- E-Zine Express | www.ezineexpress.com | subscribe to 500 free email newsletters with one click.
- Cyber Teen Magazine | www.cyberteenmag.com | quizzes, fashion and chat for teen surfers.
## News_and_Media/Technology
* dashdot | links to tech news with heated discussion attached. | c
- Silicon Scoop | www.siliconscoop.com | rumors from the valley, mostly about pizza at the office.
## News_and_Media/Weather
- Weather Wonks | www.weatherwonks.com | radar maps, forecasts and lots of opinions about clouds.
- Storm Chasers Online | www.stormchasers.net | photos of tornadoes taken by people who should know better. | c

## Recreation_and_Sports | Recreation & Sports
- Weekend Warrior | www.weekendwarrior.com | ideas for every free Saturday: hikes, crafts and naps.
## Recreation_and_Sports/Sports
- Fantasy Football Frenzy | www.fantasyfrenzy.com | set your lineup, trade players and trash-talk your friends. | n
- Box Score Junkies | www.boxscorejunkies.com | every score in every league, updated every inning.
- Extreme Sports Zone | www.extremezone.com | skateboarding, snowboarding and anything else with a helmet.
- Bowling Alley Online | www.bowlingalley.net | tips for getting more strikes and choosing a ball. | c
## Recreation_and_Sports/Sports/Soccer
- Kick It Online | www.kickitonline.com | scores and news from soccer leagues around the world.
- Women's Soccer Fever | www.womenssoccerfever.com | after the big summer championship, everyone is talking about it. | n
## Recreation_and_Sports/Sports/Baseball
- The Home Run Race | www.homerunrace.com | tracking every long ball hit this season.
- Ballpark Food Guide | www.ballparkfood.com | rating the hot dogs at every major league stadium.
## Recreation_and_Sports/Travel
- Budget Backpacker | www.budgetbackpacker.com | see Europe on $20 a day; hostel reviews and train tips.
- Road Trip Planner | www.roadtripplanner.com | routes, roadside attractions and the world's largest ball of twine. | c
- Cheap Seats Airfare | www.cheapseatsair.com | find the lowest fares by being very flexible about which city you fly to.
- Theme Park Insider | www.themeparkinsider.com | ratings for roller coasters and the lines that go with them.
## Recreation_and_Sports/Automotive
- Car Talk Garage | www.cartalkgarage.com | ask a mechanic why your car is making that noise.
- Used Car Lemon Check | www.lemoncheck.com | is that used car a lemon? Find out before you buy.
- Minivan Monthly | www.minivanmonthly.com | road tests of every family hauler, with cupholder counts.
- Hot Rod Heaven | www.hotrodheaven.com | photos of custom cars and flame paint jobs. | c
## Recreation_and_Sports/Outdoors
- Trail Mix Hiking Guide | www.trailmixguide.com | trail reports for 3,000 hikes, plus snack recommendations.
- Camping Gear Reviews | www.campinggear.com | tents, stoves and sleeping bags tested by people who got rained on.
- Fishing Hole Reports | www.fishinghole.net | what's biting and where, reported by anglers. | n
- Birdwatchers' Backyard | www.birdbackyard.com | identify the birds at your feeder.
## Recreation_and_Sports/Hobbies
- Bean Bag Buddies Price Guide | www.beanbagbuddies.com | values for every retired bean bag animal. Tag protectors essential. | c
- Stamp Collector's Corner | www.stampcorner.org | philately for beginners and experts.
- Model Railroad Junction | www.modelrailroad.com | layouts, tracks and tiny trees.
- Scrapbook Station | www.scrapbookstation.com | ideas, stickers and acid-free everything.
- Coin Collecting Club | www.coinclub.org | find the value of every quarter in your pocket.
## Recreation_and_Sports/Toys
* etoyz | buy toys online and have them shipped in time for the holidays. | c
- Furry Talker Hacks | www.furrytalkerhacks.com | open up the chattering owl-hamster toy and make it say new things. | n
- Yo-Yo Trick Guide | www.yoyotricks.com | walk the dog, around the world and 40 other tricks with videos.
- Pocket Pet Virtual Care | www.pocketpetcare.com | how to keep your keychain pet alive through math class.
- Plastic Brick Builders | www.brickbuilders.org | huge models made from interlocking plastic bricks.
## Recreation_and_Sports/Games
- Board Game Geeks | www.boardgamegeeks.net | reviews of board games you have never heard of.
- Crossword Corner | www.crosswordcorner.com | a new puzzle every day in a Java applet.
- Solitaire Strategy | www.solitairestrategy.com | how to win at the card game that came with your computer.
## Recreation_and_Sports/Games/Computer_Games
- Frag Fest Online | www.fragfest.com | news, maps and mods for first-person shooters. | c
- Pocket Monster Trainer | www.pocketmonstertrainer.com | catch-em-all tips for the handheld creature-collecting game. | n
- Adventure Game Hints | www.adventurehints.com | stuck in a text adventure? Type HINT.
- LAN Party Planner | www.lanpartyplanner.com | how to fit 30 computers in your basement without blowing a fuse.
## Recreation_and_Sports/Pets
@ Science/Animals/Pets

## Reference | Reference
- Ask a Librarian | www.askalibrarian.org | real librarians answer your questions by email.
- Measurement Converter | www.measureconvert.com | inches to centimeters, cups to liters, furlongs to fathoms.
## Reference/Libraries
- Public Library Locator | www.librarylocator.org | find a library near you and its hours.
- The Card Catalog Museum | www.cardcatalogmuseum.com | a tribute to the drawers of index cards we used before computers.
## Reference/Dictionaries
- One Big Dictionary | www.onebigdictionary.com | 300,000 words with definitions and pronunciation.
- Slang Dictionary 99 | www.slang99.com | what the kids are saying this year: phat, all that, and the bomb. | c
- Acronym Finder | www.acronymfinder.net | what does LOL mean? What about ROTFL? Look it up.
## Reference/Quotations
- Quote Garden | www.quotegarden.org | famous quotes arranged by topic.
- Fortune Cookie Wisdom | www.fortunecookies.com | thousands of fortune cookie messages, plus lucky numbers. | c
## Reference/Maps
- Map It Now | www.mapitnow.com | type an address, get a map. Directions in beta.
- Zip Code Lookup | www.ziplookup.com | find any zip code in the U.S.
## Reference/Phone_Numbers_and_Addresses
- Phone Book Online | www.phonebookonline.com | white pages for the whole country.
- Area Code Finder | www.areacodefinder.com | they keep adding new area codes; we keep up.

## Regional | Regional
- World Flag Gallery | www.worldflags.org | the flag of every country, with animated waving GIFs. | c
## Regional/Countries
- Embassy Finder | www.embassyfinder.com | addresses and phone numbers of embassies worldwide.
## Regional/Countries/Canada
- Maple Leaf Links | www.mapleleaflinks.ca | the best Canadian websites, eh.
- Hockey Night Online | www.hockeynight.ca | scores and news from the frozen north.
## Regional/Countries/United_Kingdom
- Tea Time Times | www.teatimetimes.co.uk | news and views over a cup of tea.
- Queue Watch UK | www.queuewatch.co.uk | rating the queues of Britain. Very orderly. | c
## Regional/Countries/Australia
- G'day Guide | www.gdayguide.com.au | travel and culture from down under.
- Outback Online | www.outbackonline.com.au | life on a cattle station, with a satellite modem.
## Regional/Countries/Japan
- Tokyo Tech Tour | www.tokyotechtour.co.jp | the latest gadgets from the electronics district.
- Cute Characters Daily | www.cutecharacters.co.jp | a new adorable mascot every day.
## Regional/Countries/Germany
- Autobahn Atlas | www.autobahnatlas.de | the highways of Germany, mapped and measured.
- Sausage Guide Online | www.sausageguide.de | a regional guide to 900 kinds of sausage.
## Regional/Countries/France
- Croissant Corner | www.croissantcorner.fr | the best bakeries in every arrondissement.
## Regional/Regions
- Caribbean Connection | www.caribbeanconnect.com | island hopping guides and ferry schedules.
- Arctic Circle Online | www.arcticonline.org | life above 66 degrees north, including the sun that never sets.
- Pacific Northwest Rain Report | www.rainreport.com | it rained again. Here are the pictures. | c
## Regional/U_S__States
- Fifty State Facts | www.fiftystatefacts.com | state birds, flowers, mottos and capitals.
## Regional/U_S__States/California
- Silicon Valley Tour | www.siliconvalleytour.com | drive past the garages where the computer companies started.
- Beach Cam California | www.beachcam.com | live pictures of the beach updated every 60 seconds. | c
## Regional/U_S__States/New_York
- Big Apple Bites | www.bigapplebites.com | where to eat in the city that never sleeps.
- Subway Map Online | www.subwaymaponline.com | every line, every stop, and which ones have air conditioning.
## Regional/U_S__States/Texas
- Texas Chili Cookoff | www.chilicookoff.com | recipes from 40 years of chili competitions.
- Lone Star Links | www.lonestarlinks.com | the best of Texas on the Web.
## Regional/U_S__States/Ohio
- Buckeye Backroads | www.buckeyebackroads.com | scenic drives through Ohio farm country.
- Ohio Lava Lamp Exchange | www.ohiolavalamps.com | collectors in Ohio swap groovy lamps. | n
## Regional/U_S__States/Wisconsin
- Cheese Curd Chronicles | www.cheesecurd.com | squeaky cheese news from America's Dairyland. | c
- Supper Club Survey | www.supperclubsurvey.com | rating the relish trays of Wisconsin.

## Science | Science
- Ask a Scientist | www.askascientist.org | scientists answer questions from students and the curious.
- Science News Daily | www.sciencenewsdaily.com | discoveries announced today, in plain language.
## Science/Animals
- Animal Fact Files | www.animalfacts.org | fact sheets for 1,000 animals, from aardvark to zebra.
- Zoo Cam Network | www.zoocams.com | live webcams at 12 zoos. Most animals are asleep. | c
- Weird Animal Gallery | www.weirdanimals.com | the blobfish, the aye-aye and other creatures nature apologized for.
## Science/Animals/Pets
* petz | supplies for every pet, shipped to your door. | n
- Dog Breed Selector | www.dogbreedselector.com | answer ten questions, find your perfect dog.
- Cat Behavior Corner | www.catbehavior.com | why does your cat knock things off the table? Because it can.
- Hamster Hangout | www.hamsterhangout.com | care tips, cage ideas and wheel reviews.
- Goldfish Guardian | www.goldfishguardian.com | how to keep a goldfish alive for more than a week.
- Ferret Friends | www.ferretfriends.org | ferret care, rescue and a lot of photos of ferrets in hammocks.
## Science/Animals/Dogs
- Beagle Mania | www.beaglemania.com | photos, stories and a howling-sound archive for beagle owners. | c
- Dachshund Digest | www.dachshunddigest.com | news about the long dogs.
- Poodle Parlor | www.poodleparlor.com | grooming tips for the pompom-inclined.
- Golden Retriever Rescue | www.goldenrescue.org | adopt a retriever in need of a home.
- Mutt Gallery | www.muttgallery.com | send us a picture of your mixed-breed dog. Over 2,000 so far. | n
## Science/Astronomy
- Star Gazers' Guide | www.stargazersguide.com | what to look for in the night sky this month.
- Comet Watch | www.cometwatch.org | tracking every comet visible from Earth.
- Mars Rover Fan Page | www.marsroverfans.com | photos from the little rover that rolled around Mars. | c
- Backyard Telescope | www.backyardtelescope.com | build a telescope from a mailing tube and a magnifying glass.
## Science/Engineering
- Bridge Building Contest | www.bridgecontest.org | build a bridge from popsicle sticks and see how much it holds.
- Robot Wars Workshop | www.robotworkshop.com | build a fighting robot in your garage. | n
- Paper Airplane Lab | www.paperairplanelab.com | 40 designs tested for distance and hang time. | c
## Science/Biology
- Cell Biology Online | www.cellbio.org | animations of cells dividing, set to classical music.
- Frog Dissection Virtual Lab | www.virtualfrog.com | dissect a frog on screen. No formaldehyde.
## Science/Earth_Sciences
- Volcano World Tour | www.volcanotour.com | photos and data for every active volcano.
- Earthquake Tracker | www.quaketracker.net | maps of every earthquake in the last 24 hours.
- Rock Hound Hangout | www.rockhound.org | identify the rocks in your collection.
## Science/Computer_Science
@ Computers_and_Internet
- Algorithm Animations | www.algoanimations.edu | watch sorting algorithms race each other in Java.

## Social_Science | Social Science
- Social Science Gateway | www.socscigateway.org | links to 2,000 social science resources.
## Social_Science/Archaeology
- Dig Diary | www.digdiary.com | daily notes from an archaeological dig in the desert. | c
- Pottery Shard Puzzle | www.shardpuzzle.com | piece together ancient pottery in an online puzzle.
- Pyramid Mysteries | www.pyramidmysteries.com | how were the pyramids built? Here are 60 theories, 3 of them sensible.
## Social_Science/Economics
- Economics for Everyone | www.econforeveryone.com | supply and demand explained with pizza.
- The Big Mac Index Fan Site | www.burgerindex.com | comparing currencies using fast food prices.
- Dot-Com Bubble Watch | www.bubblewatch.com | is the stock market overheating? This economist thinks so. | n
## Social_Science/Linguistics_and_Human_Languages
- Learn Klingonese | www.learnklingonese.org | an invented alien language, taught by fans.
- Esperanto Today | www.esperantotoday.org | the international language for everyone.
- Accent Archive | www.accentarchive.com | recordings of people from 200 places reading the same paragraph. | c
## Social_Science/Psychology
- Personality Quiz Palace | www.quizpalace.com | which cartoon character are you? Find out in 20 questions. | c
- Dream Dictionary | www.dreamdictionary.com | what does it mean when you dream about your teeth falling out?
## Social_Science/Sociology
- Generation X Survey | www.genxsurvey.com | is everyone born in the 1970s cynical? Take the survey.

## Society_and_Culture | Society & Culture
- Etiquette Online | www.etiquetteonline.com | which fork to use and how to RSVP by email.
## Society_and_Culture/People
- Family Tree Finder | www.familytreefinder.com | trace your ancestors back to the Middle Ages.
- Personal Home Page Gallery | www.homepagegallery.com | a gallery of the best personal home pages, with guestbooks.
- Dancing Turk Fan Club | www.dancingturkfan.com | fans of the internet's most famous self-promoting home page. | c
## Society_and_Culture/People/Personal_Home_Pages
@ Computers_and_Internet/Internet/World_Wide_Web/Free_Homepages
- Dave's Totally Rad Home Page | www.davesradpage.com | pictures of my cat, my car and my favorite links. Sign my guestbook!
- Jennifer's Corner of the Web | www.jenniferscorner.com | poems, pictures of my horse and a MIDI of my favorite song. | c
- The Webmaster Formerly Known as Kevin | www.kevinsplace.net | I made this page in HTML in Notepad. Enjoy.
- Grandma Edna's Recipe Box | www.grandmaedna.com | Grandma's recipes, typed in by her grandson. | c
- Captain Pixel's Hideout | www.captainpixel.com | my animated GIF collection and my thoughts on the future.
- Linda's Unicorn Haven | www.lindasunicorns.com | unicorn pictures, stories and a unicorn webring.
## Society_and_Culture/Environment_and_Nature
- Recycle This | www.recyclethis.org | what goes in which bin. Pizza boxes: it depends.
- Rainforest Watch | www.rainforestwatch.org | adopt an acre of rainforest for $25.
- Compost Corner | www.compostcorner.com | turning banana peels into black gold.
## Society_and_Culture/Religion_and_Spirituality
- Interfaith Calendar | www.interfaithcalendar.org | holy days of every faith, all in one place.
- Meditation Minute | www.meditationminute.com | a one-minute guided meditation for busy people.
## Society_and_Culture/Food_and_Drink
- Recipe Roundup | www.reciperoundup.com | 25,000 recipes searchable by ingredient. | c
- Jell-O Mold Museum | www.gelatinmolds.com | the wobbliest desserts of the 1950s and 1960s.
- Coffee Shop Locator | www.coffeeshoplocator.com | find a cafe with a couch near you.
- Spam Recipe Archive | www.cannedmeat.org | 300 ways to cook the famous canned meat. | c
## Society_and_Culture/Relationships
- Cyber Romance Advice | www.cyberromance.com | did you meet someone in a chat room? Read this first.
- Wedding Planner Online | www.weddingplanner.com | checklists, budgets and how to seat feuding relatives.
## Society_and_Culture/Holidays_and_Observances
- Millennium Party Planner | www.millenniumparty.com | where to ring in 2000 and what to do if the lights go out. | n
- Halloween Haunt Guide | www.halloweenhaunt.com | haunted houses, costume ideas and pumpkin carving patterns. | c
- Holiday Lights Gallery | www.holidaylights.net | houses decorated with 100,000 lights and the neighbors who hate them.
## Society_and_Culture/Issues_and_Causes
- Y2K Survival Guide | www.y2ksurvival.com | water, canned goods and a hand-crank radio. Be ready on January 1st. | n
- Save the Floppy Disk | www.savethefloppy.org | a campaign to keep 3.5-inch disks in every computer.
"""


def title_of(path):
    """display title of a category: the TOP names, else the last segment with _ as spaces"""
    for p, t, _ in TOP:
        if p == path:
            return t
    seg = path.split('/')[-1]
    seg = seg.replace('U_S__', 'U.S. ').replace('K_12', 'K-12').replace('__', ', ').replace('_', ' ')
    return seg


def parse():
    """returns (cats, order) where cats[path] = dict(title, xrefs[], sites[]) and order = list of paths"""
    cats, order, cur = {}, [], None
    web = dict((k, (t, b)) for k, t, b in WEB1999)
    for raw in DIRECTORY.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith('## '):
            parts = [x.strip() for x in line[3:].split('|')]
            cur = parts[0]
            cats[cur] = {'path': cur, 'title': parts[1] if len(parts) > 1 else title_of(cur), 'xrefs': [], 'sites': []}
            order.append(cur)
        elif line.startswith('@ '):
            cats[cur]['xrefs'].append(line[2:].strip())
        elif line.startswith('- '):
            f = [x.strip() for x in line[2:].split('|')]
            flags = f[3] if len(f) > 3 else ''
            cats[cur]['sites'].append({'name': f[0], 'host': f[1], 'desc': f[2], 'cool': 'c' in flags,
                                       'new': 'n' in flags, 'web1999': None, 'cat': cur})
        elif line.startswith('* '):
            f = [x.strip() for x in line[2:].split('|')]
            flags = f[2] if len(f) > 2 else ''
            t, b = web[f[0]]
            cats[cur]['sites'].append({'name': t, 'host': f[0] + '.localhost', 'desc': f[1], 'cool': 'c' in flags,
                                       'new': 'n' in flags, 'web1999': f[0], 'cat': cur})
    # make sure every ancestor exists
    for p in list(order):
        segs = p.split('/')
        for i in range(1, len(segs)):
            a = '/'.join(segs[:i])
            if a not in cats:
                cats[a] = {'path': a, 'title': title_of(a), 'xrefs': [], 'sites': []}
                order.append(a)
    return cats, order


def invented_sites():
    """every invented (non-1999-Web) listing, de-duplicated by host"""
    cats, order = parse()
    seen, out = set(), []
    for p in order:
        for s in cats[p]['sites']:
            if s['web1999'] or s['host'] in seen:
                continue
            seen.add(s['host'])
            out.append(s)
    return out


if __name__ == '__main__':
    c, o = parse()
    print(len(o), 'categories,', sum(len(c[p]['sites']) for p in o), 'listings,', len(invented_sites()), 'invented hosts')
