// Ask Reeves question database - written by tools/gen_askreeves.py from tools/rs_data.py
// Q[i] = id, topic, question, slots (options ~, slots ^, option=rule), keywords, rule, has own answer page
var Q = new Array();
Q[0] = new Array('pet_pics', 'pets', 'Where can I find [0] of [1]?', 'pictures=avimg:{1}~care tips~fan pages~facts^dogs=yz:Science/Animals/Dogs~cats=web:www.catbehavior.com~hamsters=web:www.hamsterhangout.com~ferrets=web:www.ferretfriends.org~goldfish=web:www.goldfishguardian.com~beagles=web:www.beaglemania.com~poodles=web:www.poodleparlor.com', 'picture pictures photo photos image images pet pets animal animals', 'opt', 0);
Q[1] = new Array('pet_buy', 'shopping', 'Where can I buy [0] for my [1]?', 'food~toys~sweaters=web:www.doggieduds.com~supplies^dog~cat~hamster~ferret~goldfish', 'buy purchase shop store food kibble supplies pet pets', 'site:petz', 0);
Q[2] = new Array('pet_choose', 'pets', 'Which breed of dog is right for [0]?', 'my family~a small apartment~a lazy person~a jogger', 'breed breeds dog dogs puppy puppies choose pick right best', 'web:www.dogbreedselector.com', 0);
Q[3] = new Array('animal_facts', 'kids', 'Where can I learn about the animal [0]?', 'aardvark~blobfish~platypus~zebra~aye-aye', 'animal animals learn facts wild zoo creature creatures', 'web:www.animalfacts.org', 0);
Q[4] = new Array('zoo_cam', 'kids', 'Where can I watch [0] on a live webcam?', 'zoo animals~a coffee pot=web:www.webcamcoffee.com~the beach=web:www.beachcam.com', 'webcam cam live camera watch video zoo', 'web:www.zoocams.com', 0);
Q[5] = new Array('buy_books', 'shopping', 'Where can I buy [0] online?', 'books=site:orinoco~used books=web:www.dustyshelves.com~comic books=web:www.comicbookcavern.com~CDs=web:www.cdcrate.com~toys=site:etoyz~pet food=site:petz~a lava lamp=site:ubid', 'buy purchase online order shop shopping store book books novel cd cds', 'opt', 0);
Q[6] = new Array('auction', 'shopping', 'Where can I bid on [0] at an auction?', 'collectible bean bags~a used computer~a lava lamp~just about anything', 'auction auctions bid bidding sell selling trade collectible collectibles', 'site:ubid', 0);
Q[7] = new Array('price_beanie', 'shopping', 'How much is my [0] worth?', 'bean bag animal=web:www.beanbagbuddies.com~coin collection=web:www.coinclub.org~stamp=web:www.stampcorner.org~old toy=web:www.retrotoyattic.com', 'worth value price collectible collect collecting valuable bean beanie', 'opt', 0);
Q[8] = new Array('gift', 'shopping', 'What is a good gift for [0]?', 'a child~a computer nerd~my mom~my dad~someone who has everything', 'gift gifts present presents birthday christmas holiday holidays shopping mother father', 'ans', 1);
Q[9] = new Array('toys_hot', 'shopping', 'What are the most popular toys for [0]?', 'the holidays~boys~girls~collectors', 'toy toys popular hot christmas holiday holidays kids children', 'site:etoyz', 0);
Q[10] = new Array('learn_html', 'computers', 'How do I build my own [0]?', 'home page=web:www.htmlmadeeasy.com~web site=web:www.htmlmadeeasy.com~computer=web:www.homemadecomputer.net~webring=web:www.webringregistry.com', 'build make create own homepage home page website web site html learn', 'opt', 0);
Q[11] = new Array('free_homepage', 'computers', 'Where can I get a free [0]?', 'home page=site:geohoods~email account=yz:Computers_and_Internet/Internet~hit counter=web:www.hitcounterstore.com~screen saver=web:www.screensaverheaven.com', 'free get homepage home page email counter screensaver screen saver', 'opt', 0);
Q[12] = new Array('y2k_ready', 'computers', 'Is my [0] ready for the year 2000?', 'computer~VCR~toaster~bank~coffee maker', 'y2k year 2000 millennium bug ready compliant date problem prepare', 'ans', 1);
Q[13] = new Array('mp3', 'computers', 'Where can I download [0] files?', 'MP3=site:snapster~MIDI~free software=web:www.freewarefriday.com~shareware=web:www.sharewareshack.com', 'download downloads mp3 mp3s midi music song songs file files software free', 'opt', 0);
Q[14] = new Array('fix_pc', 'computers', 'Why does my computer [0]?', 'crash all the time=web:www.bluescreengallery.com~make that screeching noise=web:www.howtheinternetworks.net~jam the printer=web:www.printerjam.net~run so slowly=web:www.overclockersanon.org', 'computer pc crash crashes slow broken fix noise modem printer error', 'opt', 0);
Q[15] = new Array('search_web', 'computers', 'How do I search the Web for [0]?', 'anything at all~a web page~pictures~a person', 'search engine engines find web internet look', 'ans', 1);
Q[16] = new Array('linux', 'computers', 'Where can I learn about [0]?', 'Linux=web:www.penguinpower.org~Perl=web:www.perlpearls.org~Java=web:www.javabeancounter.com~CFML=web:www.cfmlcookbook.com~DOS=web:www.dosprompt.net', 'learn programming program language linux perl java cfml dos operating system unix', 'opt', 0);
Q[17] = new Array('nerd_news', 'computers', 'Where can I read [0] news?', 'technology=site:dashdot~computer=web:www.bitsbytesweekly.com~internet=web:www.dotcomdaily.com', 'news nerd nerds geek geeks technology tech computer read stories', 'opt', 0);
Q[18] = new Array('chat', 'computers', 'Where can I [0] with other people online?', 'chat=web:www.chatshack.com~play games=web:www.fragfest.com~trade music=site:snapster', 'chat talk meet friends people online irc messenger', 'opt', 0);
Q[19] = new Array('news', 'popular', 'Where can I find today\'s [0] news?', 'world~business~sports~weather=web:www.weatherwonks.com~technology=site:dashdot', 'news today headlines current events latest breaking world', 'site:cnm', 0);
Q[20] = new Array('weather', 'travel', 'What is the weather forecast for [0]?', 'my town~the weekend~Seattle=web:www.rainreport.com~the beach=web:www.beachcam.com', 'weather forecast rain snow sunny temperature storm', 'web:www.weatherwonks.com', 0);
Q[21] = new Array('define', 'reference', 'What does the word [0] mean?', 'phat=web:www.slang99.com~ROTFL=web:www.acronymfinder.net~villanelle=web:www.villanellevillage.com~serendipity', 'mean meaning define definition word words dictionary slang', 'web:www.onebigdictionary.com', 0);
Q[22] = new Array('quote', 'reference', 'Where can I find a famous quotation about [0]?', 'love~success~computers~butlers', 'quote quotes quotation quotations famous saying sayings', 'web:www.quotegarden.org', 0);
Q[23] = new Array('convert', 'reference', 'How many [0] are in a [1]?', 'inches~cups~ounces~furlongs^meter~liter~pound~fathom', 'convert conversion how many measure measurement units metric', 'web:www.measureconvert.com', 0);
Q[24] = new Array('encyclopedia', 'reference', 'Where can I find an encyclopedia article on [0]?', 'volcanoes=web:www.volcanotour.com~pyramids=web:www.pyramidmysteries.com~comets=web:www.cometwatch.org~earthquakes=web:www.quaketracker.net', 'encyclopedia article report homework school research', 'opt', 0);
Q[25] = new Array('map', 'travel', 'Where can I get a map of [0]?', 'my neighborhood~the subway=web:www.subwaymaponline.com~the United States~the world', 'map maps directions street address where located location', 'web:www.mapitnow.com', 0);
Q[26] = new Array('travel_cheap', 'travel', 'How can I find cheap [0]?', 'airline tickets=web:www.cheapseatsair.com~hotels=web:www.budgetbackpacker.com~vacations=web:www.budgetbackpacker.com', 'cheap travel airline airfare flight flights ticket tickets hotel hotels vacation trip', 'opt', 0);
Q[27] = new Array('travel_go', 'travel', 'What is there to do in [0]?', 'New York=yz:Regional/U_S__States/New_York~California=yz:Regional/U_S__States/California~Texas=yz:Regional/U_S__States/Texas~Canada=yz:Regional/Countries/Canada~Japan=yz:Regional/Countries/Japan~Wisconsin=yz:Regional/U_S__States/Wisconsin', 'travel visit vacation trip things to do attractions tourist sightseeing city', 'opt', 0);
Q[28] = new Array('road_trip', 'travel', 'Where can I find [0] for a road trip?', 'roadside attractions~maps~theme parks=web:www.themeparkinsider.com', 'road trip drive driving car vacation attraction attractions twine', 'web:www.roadtripplanner.com', 0);
Q[29] = new Array('dancing_hamsters', 'popular', 'Where can I see the [0]?', 'dancing hamsters=site:hamstershuffle~dancing baby=web:www.dancingbaby.net~dancing man from Turkey=web:www.dancingturkfan.com', 'dancing dance hamster hamsters baby funny animation cool', 'opt', 0);
Q[30] = new Array('movie', 'entertainment', 'Where can I find [0] about the movie [1]?', 'reviews=web:www.popcorncritics.com~showtimes~fan pages~quotes=web:www.moviequotequiz.com^about the sinking ship=web:www.sinkingshipshrine.com~about the space saga prequel=web:www.spacesagacountdown.com~about the witch in the woods=web:www.witchwoodsfans.com', 'movie movies film films review reviews showtimes cinema theater', 'opt', 0);
Q[31] = new Array('music_band', 'entertainment', 'Where can I find [0] for my favorite [1]?', 'lyrics=web:www.lyricslocker.com~tour dates~fan clubs~MP3s=site:snapster^boy band=web:www.boybandbulletin.com~ska band=web:www.skaisnotdead.org~swing band=web:www.swingrevival.com~garage band=web:www.garagebandgazette.com', 'music band bands lyrics song songs singer concert tour album', 'opt', 0);
Q[32] = new Array('tv', 'entertainment', 'Where can I find an episode guide for [0]?', 'the alien conspiracy show=web:www.alienfilesguide.com~the coffee shop sitcom=web:www.sitcomcouch.com~the teen drama=web:www.teendramarecap.com', 'tv television show shows episode episodes guide sitcom drama', 'opt', 0);
Q[33] = new Array('joke', 'entertainment', 'Can you tell me a [0]?', 'joke=web:www.jokeoftheday.com~lightbulb joke=web:www.lightbulbjokes.org~pun=web:www.punpit.com', 'joke jokes funny humor laugh pun puns tell', 'opt', 0);
Q[34] = new Array('games', 'entertainment', 'Where can I play [0] games?', 'computer=yz:Recreation_and_Sports/Games/Computer_Games~board=web:www.boardgamegeeks.net~card=web:www.solitairestrategy.com~trivia=web:www.triviatavern.com~crossword=web:www.crosswordcorner.com', 'game games play playing fun video computer board card trivia', 'opt', 0);
Q[35] = new Array('cool', 'popular', 'What are the coolest sites on the Web [0]?', 'today~this week~of all time', 'cool coolest best site sites web neat fun', 'site:yowza', 0);
Q[36] = new Array('bored', 'popular', 'What should I do when I am [0]?', 'bored~at work~up too late~avoiding homework', 'bored boring nothing to do fun waste time', 'ans', 1);
Q[37] = new Array('health', 'health', 'Where can I find information about [0]?', 'allergies=web:www.allergyalley.com~back pain=web:www.backpainbasics.com~carpal tunnel=web:www.carpaltunnel.org~the common cold=web:www.coldcorner.com', 'health sick illness disease symptoms pain doctor medicine cure treatment', 'opt', 0);
Q[38] = new Array('fitness', 'health', 'How can I get in shape [0]?', 'at my desk=web:www.cubicleworkout.com~with aerobics=web:www.stepaerobics.com~with kickboxing=web:www.kickboxtribune.com~without moving=web:www.walktothefridge.com', 'exercise fitness fit shape workout weight lose diet gym', 'opt', 0);
Q[39] = new Array('recipe', 'home', 'Where can I find a recipe for [0]?', 'chili=web:www.chilicookoff.com~low-fat dinners=web:www.lowfatkitchen.com~gelatin molds=web:www.gelatinmolds.com~canned meat=web:www.cannedmeat.org~dorm room meals=web:www.dormcooking.com~cookies', 'recipe recipes cook cooking food dinner meal bake baking kitchen', 'opt', 0);
Q[40] = new Array('wedding', 'home', 'How do I plan a [0]?', 'wedding=web:www.weddingplanner.com~millennium party=web:www.millenniumparty.com~Halloween party=web:www.halloweenhaunt.com~LAN party=web:www.lanpartyplanner.com', 'plan planning party wedding celebrate celebration organize', 'opt', 0);
Q[41] = new Array('family_tree', 'home', 'How can I trace my [0]?', 'family tree~ancestors~long-lost relatives', 'family tree genealogy ancestor ancestors relatives trace', 'web:www.familytreefinder.com', 0);
Q[42] = new Array('garden', 'home', 'How do I start a [0]?', 'compost pile=web:www.compostcorner.com~scrapbook=web:www.scrapbookstation.com~model railroad=web:www.modelrailroad.com~business in my garage=web:www.garagestartup.com', 'start begin hobby hobbies garden compost scrapbook railroad business', 'opt', 0);
Q[43] = new Array('stocks', 'money', 'Which [0] stocks should I buy?', 'internet~penny~technology~boring but sensible', 'stock stocks invest investing investment money market buy ipo shares', 'ans', 1);
Q[44] = new Array('job', 'money', 'Where can I find a job [0]?', 'on the Internet=web:www.jobjungle.com~writing HTML=web:www.htmljobs.net~working from home=web:www.telecommutetoday.com~as a butler', 'job jobs work career careers employment hire hiring resume', 'opt', 0);
Q[45] = new Array('taxes', 'money', 'Where can I get help with my [0]?', 'taxes=web:www.aprilpanic.com~resume=web:www.resumerobot.com~homework=web:www.homeworkhelper.com~legal problem=web:www.legaleagle.com', 'help taxes tax resume homework legal law lawyer advice', 'opt', 0);
Q[46] = new Array('homework', 'kids', 'Where can I find help with my [0] homework?', 'math~science=web:www.sciencefaircentral.com~spelling=web:www.spellingbeebuzz.com~history', 'homework school study kids student math science spelling history', 'web:www.homeworkhelper.com', 0);
Q[47] = new Array('science_fair', 'kids', 'What is a good idea for a science fair project about [0]?', 'volcanoes~paper airplanes=web:www.paperairplanelab.com~bridges=web:www.bridgecontest.org~robots=web:www.robotworkshop.com', 'science fair project experiment idea school', 'web:www.sciencefaircentral.com', 0);
Q[48] = new Array('stars', 'kids', 'What can I see in the night sky [0]?', 'this month~with a telescope=web:www.backyardtelescope.com~if I live in a city', 'star stars sky night astronomy telescope planet planets moon comet', 'web:www.stargazersguide.com', 0);
Q[49] = new Array('mars', 'kids', 'Where can I see pictures from [0]?', 'Mars=web:www.marsroverfans.com~a volcano=web:www.volcanotour.com~a tornado=web:www.stormchasers.net', 'mars space pictures photos rover planet volcano tornado', 'opt', 0);
Q[50] = new Array('college', 'kids', 'How can I find [0] for college?', 'scholarships=web:www.scholarshipsearch.org~a good cafeteria=web:www.ratemycafeteria.com~a campus tour=web:www.campustour.com', 'college university school scholarship scholarships tuition campus', 'opt', 0);
Q[51] = new Array('reeves_who', 'popular', 'Who is [0]?', 'Reeves~the butler~the man in the bow tie', 'who reeves butler you yourself jeeves name', 'ans', 1);
Q[52] = new Array('meaning_life', 'popular', 'What is the meaning of [0]?', 'life~the Internet~all those blinking lights', 'meaning life purpose universe everything why exist', 'ans', 1);
Q[53] = new Array('ufo', 'popular', 'Have [0] really visited the Earth?', 'aliens~UFOs~little green men', 'alien aliens ufo ufos space visitors earth conspiracy', 'web:www.ufodatabase.net', 0);
Q[54] = new Array('personal', 'popular', 'Where can I find someone\'s [0]?', 'email address=web:www.phonebookonline.com~phone number=web:www.phonebookonline.com~home page=yz:Society_and_Culture/People/Personal_Home_Pages', 'find someone person people email address phone number homepage friend', 'opt', 0);
var PEEK = new Array('How do I get the hamster song out of my head?',
  'Is it safe to turn off my computer on New Year\'s Eve?',
  'Where can I buy a lava lamp?',
  'What is the capital of Wisconsin?',
  'Why does my modem scream at me?',
  'How many bean bag animals are there?',
  'Who invented the Internet?',
  'What is a webring?',
  'Where can I find free MIDI files?',
  'Can I eat a Furry Talker?',
  'How do I make my page blink?',
  'Where can I see pictures of dogs in costumes?',
  'What does ASL mean in a chat room?',
  'Is the year 2000 a leap year?',
  'How do I unsubscribe from a chain letter?',
  'Where can I get a free email address?',
  'What should I name my goldfish?',
  'How tall is the tallest skyscraper?',
  'Where can I find cheap airline tickets to Ohio?',
  'Do butlers ever take a day off?',
  'How do I tie a bow tie?',
  'Where can I download screen savers with fish?',
  'What is the best search engine?',
  'How do I build a web page in Notepad?',
  'Where can I read about the Mars rover?',
  'Why is the sky blue?',
  'How do I stop my cat from walking on the keyboard?',
  'What is an MP3?',
  'Where can I find a recipe for chili?',
  'Is there a cure for the common cold?',
  'How do I get on Yowza!?',
  'Who will win the election in 2000?',
  'Where can I find the lyrics to that boy band song?',
  'How do I become a webmaster?',
  'What is the meaning of life?',
  'Where can I find a job writing HTML?',
  'How do I stop the dancing baby?',
  'Can my toaster get the Y2K bug?',
  'What time is it in Tokyo?',
  'Where can I trade Pokey Monster cards?',
  'How do I clean my mouse ball?',
  'How do I make a paper airplane that flies far?',
  'Where can I find a map of the subway?',
  'Who are you, really?');
var QUIPS = new Array('Very good. I have found answers to the following questions:', 'Certainly. I took the liberty of finding answers to the following questions:', 'An excellent question, if I may say so. I have found answers to the following questions:', 'Right away. I have found answers to the following questions:', 'Of course. I have laid out answers to the following questions:');
var NOMATCH = new Array('I beg your pardon, but that is a new one on me. While I look into it, perhaps one of these will serve:', 'I am afraid my notes do not cover that particular matter. I have, however, prepared the following:', 'Most irregular. I could not find that question in my files, but I have taken the liberty of finding these:');
