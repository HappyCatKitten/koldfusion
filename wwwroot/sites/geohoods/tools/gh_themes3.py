"""gh_themes3.py -- Campus, Bunker, Driftwood, Skillet, Workbench homepage themes (all content original)."""
from gh_tdefs import S, SUB, T

T3 = []

ABOUT_ME = [
    ('Name', '{first}'), ('Age', '{age}'), ('Location', '{where}'), ('Sign', 'Scorpio (watch out)'),
    ('Fave color', 'Purple!!!'), ('Fave band', 'Northbound / Heartbeat Harbor'), ('Fave show', 'Maple Cove'),
    ('Fave food', 'Pizza bagels'), ('Pet peeve', 'People who chew loud'), ('Crush', 'Not telling!!! (ok his name '
                                                                                   'starts with a J)'),
    ('ISeekU #', '31337420'), ('Screen name', '{handle}'), ('Hobbies', 'Chatting, sleepovers, rollerblading'),
    ('Dream job', 'Marine biologist or famous'), ('Shoe size', 'why do you need to know that'),
]

T3.append(T('aboutme', 'Campus', 'Hallway', 8, age=(13, 18),
    titles=['~*~{handle}\'s World~*~', 'ALL ABOUT ME!!!', '{first}\'s Page of Randomness', 'Welcome 2 My Page!!!',
            '{handle}\'s Crib', 'xX {first}\'s Place Xx', '{first} Online', 'This Is Me'],
    intro=['Hey!!! Welcome to my page! My name is {first} and I am {age} years old and I live in {town}. I made this '
           'page in computer class (shhh). It is kind of random but that is what I am like. Enjoy!!! And SIGN MY '
           'GUESTBOOK!!!',
           'wassup!!! u have found {handle}\'s page. it is still under construction but there is lots of stuff. check '
           'out my friends and my fave links. peace out',
           'Hi! I\'m {first}! This is my homepage where I put all my stuff. I like music, my friends, and talking on '
           'the phone for 4 hours. My mom says I need a hobby. THIS is my hobby.'],
    sections=[
        S('table', ['All About Me', 'Stats', 'The 411 On Me'], ABOUT_ME, n=(7, 12)),
        S('list', ['My Friends', 'My Buds', 'Shout Outs'], [
            '<B>Kristy</B> - my best friend since 2nd grade!!! BFF!!', '<B>Jen</B> - the funniest person alive',
            '<B>Mike</B> - he is like my brother. a really annoying brother', '<B>Ashley</B> - fellow Maple Cove '
            'addict', '<B>Tyler</B> - skater boy', '<B>Megan</B> - we have every class together LOL',
            '<B>my cat Peaches</B> - she counts'], n=(3, 6)),
        S('webcam', ['My Webcam!!!', '{handle}-Cam'], [], n=(1, 1), prob=0.5),
        S('list', ['Things I Hate', 'Pet Peeves'], ['Mondays', 'When the phone line is busy because my brother is '
                                                    'online', 'Pop quizzes', 'Pickles', 'When people say "whatever"',
                                                    'Getting kicked out of chat rooms', 'Daylight savings time'],
          n=(3, 5)),
        S('poll', ['Rate My Page!', 'Poll'], ['10 - AWESOME', '7 - pretty cool', '5 - ok', '1 - boring (be nice)'],
          n=(1, 1), prob=0.6),
        S('links', ['My Fave Links', 'Cool Sites', 'My Friends\' Pages'], n=(4, 7)),
    ],
    subpages=[SUB('quiz.html', ['Quiz: How Well Do You Know Me?'], [
        S('faq', ['The Quiz (answers at bottom)'], [('What is my favorite color?', 'Purple. Duh.'),
                                                    ('Who is my best friend?', 'Kristy!!!'),
                                                    ('What do I want to be?', 'Marine biologist (or famous)'),
                                                    ('What is my cat\'s name?', 'Peaches'),
                                                    ('Pickles: yes or no?', 'NO.')], n=(4, 5))], prob=0.5),
        SUB('poems.html', ['My Poems'], [
            S('poems', ['Poems I Wrote'], [('Friends', 'Friends are like stars\nyou can\'t always see them\nbut you '
                                            'know they are there\n<3 Kristy'),
                                           ('School', 'Bell rings\nI sit\ntest time\noh no')], n=(1, 2))], prob=0.4)],
    images=['welcome.gif', 'heart.gif', 'twinkle.gif', 'photo_me2.gif', 'photo_me.gif'],
    bullets=['bullet_heart.gif', 'bullet_star.gif', 'ball_purple.gif', 'ball_pink.gif'],
    lines=['rainbow_line.gif', 'line_hearts.gif', 'line_stars.gif', 'line_bows.gif'],
    styles=['glitter', 'black_neon', 'pastel_hearts', 'border_purple', 'leopard', 'clouds', 'notebook', 'denim'],
    layouts=['single', 'single', 'sidebar', 'frames', 'splash'], midi=['heartthrob', 'techno', 'lovesong', None],
    ring='teens', keywords='about me teen homepage friends {first}',
    desc=['All about {first}: stats, friends and links', '{handle}\'s personal homepage', 'Random stuff by {first}, '
                                                                                          'age {age}'],
    gb=['hiiii {first}!!! luv the page!!!', 'its kristy!!! ur page is so cool', 'sign mine back k?',
        'purple rules', 'lol at the pickles thing']))

T3.append(T('firstpage', 'Campus', 'Hallway', 5, age=(11, 70),
    titles=['My First Webpage!!!', 'MY FIRST HOME PAGE', 'my first web page', 'Welcome To My First Page Ever',
            'Testing Testing 1 2 3'],
    intro=['This is my first webpage!!! I am still learning HTML so please be patient. I will add more stuff soon!!!',
           'hello. this is my first web page. i am not sure what to put here yet. here is a picture of a construction '
           'guy because my page is under construction.',
           'Welcome to my FIRST EVER home page on the World Wide Web! My daughter showed me how. I do not know how to '
           'make the words bigger yet.'],
    sections=[
        S('list', ['Stuff About Me'], ['I like pizza', 'I have a dog', 'I am learning HTML!!!', 'This is a list',
                                       'I figured out how to make lists', 'Lists are cool'], n=(3, 6)),
        S('para', ['Coming Soon'], ['More pictures! A guestbook! A counter! Maybe a MIDI! Check back soon!!!',
                                    'I will put my vacation pictures here when I figure out the scanner.'], n=(1, 1)),
        S('links', ['Links'], n=(1, 3)),
    ],
    images=['construction.gif', 'worker.gif', 'barricade.gif', 'globe.gif'], bullets=[],
    lines=['rainbow_hr.gif'], styles=['default_gray', 'plain', 'default_gray', 'black_neon'], layouts=['single'],
    midi=[None, None, 'ragtime'], ring='newbie', keywords='first webpage under construction new',
    desc=['My first webpage!!! (under construction)', 'A brand new homepage'],
    gb=['Welcome to the Web! Nice first page!', 'Everybody starts somewhere :)', 'Add more stuff!!!'],
    features={'construction': True, 'firstpage': True}))

T3.append(T('dormcam', 'Campus', 'Dorm', 3, age=(18, 23),
    titles=['Room 314 Live!', '{handle}\'s Dorm Room', 'The {last} Hall Cam'],
    intro=['Welcome to Room 314 of Tolliver Hall, the most famous dorm room on the Internet (according to us). Our '
           'webcam takes a picture every 60 seconds so you can watch us... study. Mostly study. Sometimes play '
           'Fragmatic Arena.'],
    sections=[
        S('webcam', ['The Cam'], [], n=(1, 1)),
        S('table', ['Roommates'], [('{first}', 'Major: undecided. Minor: naps.'), ('Dave', 'Major: computer science. '
                                                                                         'Built the cam.'),
                                   ('Ramen', 'Not a person. Our main food group.')], n=(2, 3)),
        S('log', ['Dorm Log'], ['Fire alarm at 3 am. Again. Someone microwaved a fork.', 'Finals week. Dave has not '
                                'slept in 40 hours. He seems fine. He is talking to the cam.',
                                'Pizza delivery guy recognized us from the website. We are famous.',
                                'The cam fell off the shelf. Nobody noticed for 2 days.', 'Road trip! Cam will show an '
                                                                                         'empty room. Do not rob us.'],
          n=(3, 5)),
        S('links', ['Other Cams'], n=(2, 4)),
    ],
    images=['webcam_88.gif', 'photo_computer.gif'], bullets=['ball_blue.gif'], lines=['line_laser.gif'],
    styles=['black_neon', 'concrete', 'pro_blue', 'denim'], layouts=['single', 'frames'], midi=['techno', None],
    ring='teens', keywords='dorm webcam college room live', desc=['Live (ish) dorm room webcam'],
    gb=['I watched you guys eat ramen for an hour. Thrilling.', 'Is the cam broken? It is just a black square.']))

T3.append(T('class2000', 'Campus', 'Quad', 3, age=(16, 18),
    titles=['{town} High Class of 2000!!!', 'Class of Y2K', 'Seniors 2000'],
    intro=['WE ARE THE CLASS OF 2000!!! The first graduating class of the new millennium! This is the unofficial '
           'class page. Countdown to graduation below.'],
    sections=[
        S('list', ['Senior Superlatives', 'Most Likely To...'], ['Most Likely To Succeed: Megan P.',
                                                                 'Class Clown: Tyler R.', 'Best Hair: Kevin D. (frosted '
                                                                                          'tips)',
                                                                 'Most Likely To Be Famous: Jen K.',
                                                                 'Most Likely To Still Be Online In 2020: {first}',
                                                                 'Best Car: Dustin\'s Thunderbolt'],
          n=(4, 6)),
        S('table', ['Senior Events'], [('Homecoming', 'Oct 15'), ('Senior Skip Day', 'Shhh, it is secret'),
                                       ('Prom', 'May 6, 2000'), ('Graduation', 'June 2, 2000'),
                                       ('All-night party', 'June 2, at the Bowl-a-Rama')], n=(3, 5)),
        S('para', ['Y2K??'], ['If Y2K happens and the computers all crash, does that mean we don\'t have to take '
                              'finals? Asking for a friend.'], n=(1, 1)),
        S('links', ['Classmates\' Pages'], n=(3, 5)),
    ],
    images=['y2k_bomb.gif', 'cool_face.gif', 'award_coolweek.gif'], bullets=['bullet_star.gif', 'ball_blue.gif'],
    lines=['rainbow_line.gif', 'line_stars.gif'], styles=['denim', 'black_neon', 'checker', 'clouds'],
    layouts=['single', 'sidebar'], midi=['fight_song', 'techno'], ring='teens',
    keywords='class of 2000 high school seniors graduation y2k', desc=['Class of 2000 unofficial page'],
    gb=['2000 RULES!!!', 'Best Hair should have been me.']))

# ------------------------------------------------------------------ Bunker
T3.append(T('y2k', 'Bunker', 'Silo', 6, age=(35, 70),
    titles=['Y2K: Are YOU Ready?', 'The {last} Family Y2K Preparedness Page', 'Millennium Bug Survival Guide',
            'COUNTDOWN TO Y2K', 'Prepared Not Scared: Y2K', '{first}\'s Y2K Bunker'],
    intro=['When the clocks strike midnight on January 1, 2000, every computer that stores the year as two digits '
           'will think it is 1900. Banks. Power plants. Water. Elevators. The microwave. I am not panicking. I am '
           'PREPARING. You should too.',
           'This page is not about fear. It is about common sense. Even if Y2K turns out to be nothing (and I hope it '
           'does), a family with 3 months of food and water is a family that sleeps well at night.',
           'Welcome to the bunker. Literally: I built one. It is 12 by 16 feet, under the garden shed, and it has a '
           'generator, 400 gallons of water and a lot of canned peaches.'],
    sections=[
        S('countdown', ['Countdown', 'Time Left'], [], n=(1, 1)),
        S('list', ['Y2K Checklist', 'What You Need'], [
            'Water: 1 gallon per person per day. Get 90 days worth.', 'Canned food you actually like to eat',
            'Manual can opener (VERY important, do not laugh)', 'Cash. Small bills. ATMs may not work.',
            'Generator + fuel (store fuel SAFELY)', 'Kerosene heater and lamps', 'Batteries, batteries, batteries',
            'Paper copies of bank statements from December 1999', 'First aid kit and 3 months of prescriptions',
            'A hand-crank radio', 'Board games (it will be a long winter)', 'Toilet paper. So much toilet paper.'],
          n=(6, 10)),
        S('table', ['My Bunker Inventory', 'The Stockpile'], [('Water', '400 gallons + filter'),
                                                             ('Rice', '200 lbs'), ('Beans', '150 lbs'),
                                                             ('Canned peaches', '96 cans (my weakness)'),
                                                             ('Peanut butter', '40 jars'), ('Generator', '5000 watt'),
                                                             ('Gas', '60 gallons, rotated monthly'),
                                                             ('Candles', '300'), ('Toilet paper', '144 rolls'),
                                                             ('Coffee', 'enough for the next millennium')], n=(5, 9)),
        S('para', ['What Will Happen?', 'My Prediction'], [
            'Nobody knows, and that is the point. The best case: a few glitches, a lot of jokes, and I eat canned '
            'peaches until June. The worst case: power out for weeks in January. Which would you rather be ready for?',
            'I work in IT at a bank (I will not say which). I have seen the code. Some of it was written in 1971 by '
            'people who are now retired to Florida. We are fixing it as fast as we can. Draw your own conclusions.',
            'My brother-in-law says I am crazy. He also does not own a manual can opener. We will see who is crazy '
            'on January 2nd.'], n=(1, 2)),
        S('links', ['Y2K Links', 'Other Prepared Families'], n=(3, 6)),
    ],
    subpages=[SUB('bunker.html', ['Bunker Construction Diary'], [
        S('log', ['Construction Log'], ['Dug the hole. 3 weekends. My back will never forgive me.',
                                        'Poured the concrete. Neighbors asking questions. Told them it is a wine '
                                        'cellar.',
                                        'Installed the air vent and the hand pump.', 'Moved in the shelves and the first '
                                                                                    'load of peaches.',
                                        'Wife says the bunker needs a rug. Bunker now has a rug.',
                                        'Ran the generator test. Bunker is GO.'], n=(4, 6)),
        S('photos', ['Photos'], [('photo_pantry.gif', 'Shelves, half full'), ('photo_house.gif', 'The shed (the bunker '
                                                                                                 'is under it)')],
          n=(1, 2))], prob=0.6)],
    images=['y2k_bomb.gif', 'y2k_ok.gif', 'photo_pantry.gif', 'ad_y2k.gif'], bullets=['ball_red.gif',
                                                                                     'bullet_skull.gif',
                                                                                     'ball_yellow.gif'],
    lines=['line_barbed.gif', 'line_laser.gif', 'rainbow_hr.gif'],
    styles=['camo', 'concrete', 'black_neon', 'hacker', 'border_flames', 'plain'],
    layouts=['single', 'sidebar', 'frames'], midi=['y2k_march', 'spooky', None], ring='y2k',
    keywords='y2k millennium bug preparedness bunker survival food storage generator',
    desc=['Y2K preparedness checklist and bunker inventory', 'Getting ready for the millennium bug',
          'Family Y2K survival page with countdown'],
    gb=['Thank you for the checklist. Buying a can opener today.', 'You are going to have a LOT of peaches.',
        'My brother-in-law says I am crazy too!', 'See you on the other side of 2000!'],
    features={'badges': ['y2k_not.gif']}))

T3.append(T('conspiracy', 'Bunker', 'Silo', 2, age=(30, 70),
    titles=['WAKE UP PEOPLE!!!', 'The Truth About {thing}'],
    entities=[dict(thing='Daylight Saving Time'), dict(thing='The Barcodes')],
    intro=['They do not want you to read this page. That is why it has a black background: so it is harder to read. '
           'Think about it. This page is about <B>{thing}</B> and what They are hiding.'],
    sections=[
        S('list', ['The Facts They Hide', 'Evidence'], [
            'Ask yourself: who BENEFITS?', 'Why do all the clocks change at 2 a.m., when everyone is asleep?',
            'The lines on every barcode add up to the same number. Coincidence???', 'I wrote to my congressman. He '
            'wrote back. On LETTERHEAD. What is he hiding?', 'My toaster has started making a clicking noise.',
            'Notice how nobody talks about this.'], n=(4, 6)),
        S('para', ['My Research'], ['I have been researching this for 9 years at the public library. The librarian now '
                                    'hides when I come in. That tells you everything.'], n=(1, 1)),
        S('links', ['Other Awake People'], n=(2, 4)),
    ],
    images=['skull_spin.gif', 'tinfoil.gif'], bullets=['bullet_skull.gif'], lines=['line_barbed.gif'],
    styles=['black_neon', 'hacker', 'concrete'], layouts=['single'], midi=['spooky'], ring='truth',
    keywords='conspiracy truth wake up {thing}', desc=['The truth about {thing}'],
    gb=['I KNEW IT', 'The librarian hides from me too!'], features={'badges': ['tinfoil.gif']}))

T3.append(T('hamradio', 'Bunker', 'Antenna', 3, age=(40, 80), gender='m',
    titles=['{call} - Amateur Radio Station', '{call} Shack', 'The {call} Radio Page'],
    entities=[dict(call='W9XKQ'), dict(call='KD0ZZT'), dict(call='N4BRP')],
    intro=['73 and welcome to the home page of amateur radio station <B>{call}</B>, located in {town}, {state}. Licensed '
           'since 1968. I work mostly HF, some 2 meters, and I check into the Tuesday night emergency net.'],
    sections=[
        S('table', ['The Shack', 'Equipment'], [('HF rig', 'Hamwell HT-430 (bought used in 1985, still perfect)'),
                                                ('2m', 'Handheld + mobile in the truck'), ('Antenna', 'Dipole, 40 feet up '
                                                                                                  'in the oak tree'),
                                                ('Power', '100 watts, plus a solar backup (Y2K ready!)'),
                                                ('Key', 'Grandpa\'s old straight key'), ('Logbook', 'Paper. Always '
                                                                                                    'paper.')], n=(4, 6)),
        S('log', ['Recent Contacts', 'From The Log'], ['Worked a station in New Zealand on 20 meters! 11,000 miles!',
                                                       'Field Day: 212 contacts from a tent. Mosquitoes: 4,000.',
                                                       'Helped relay messages during the ice storm.',
                                                       'Talked to a ham in Finland about pickles for 40 minutes.',
                                                       'Antenna fell out of the oak tree. Squirrel suspected.'],
          n=(3, 5)),
        S('list', ['Why Ham Radio?'], ['When the phones go down, we are still on the air.', 'You can talk to the '
                                                                                            'whole world with a wire '
                                                                                            'and a battery.',
                                       'No monthly bill!', 'The people are friendly.'], n=(3, 4)),
        S('links', ['Radio Links'], n=(2, 4)),
    ],
    images=['tower.gif', 'globe.gif'], bullets=['ball_green.gif'], lines=['line_lightning.gif', 'rainbow_hr.gif'],
    styles=['concrete', 'plain', 'retro_tan', 'pro_blue'], layouts=['single'], midi=[None], ring='y2k',
    keywords='ham radio amateur {call} hf antenna emergency net', desc=['Amateur radio station {call}'],
    gb=['73 from KC5WWW!', 'Good QSO last week OM.']))

T3.append(T('foodstorage', 'Bunker', 'Pantry', 2, age=(30, 70), gender='f',
    titles=['The Prepared Pantry', '{first}\'s Canning Kitchen'],
    intro=['Canning, dehydrating and long-term food storage, the way my grandmother taught me. Y2K or no Y2K, a full '
           'pantry is a happy pantry.'],
    sections=[
        S('table', ['What I Canned This Year'], [('Tomatoes', '64 quarts'), ('Green beans', '40 pints'),
                                                 ('Peaches', '30 quarts'), ('Strawberry jam', '24 jars'),
                                                 ('Pickles', '18 quarts (dill AND bread & butter)'),
                                                 ('Applesauce', '20 quarts')], n=(4, 6)),
        S('list', ['Storage Tips'], ['First in, first out!', 'Label everything with the date', 'Store in a cool, '
                                                                                               'dark place',
                                     'Rotate your water every 6 months', 'Rice and beans keep for years in buckets'],
          n=(3, 5)),
        S('photos', ['My Pantry'], [('photo_pantry.gif', 'The pantry in October')], n=(1, 1)),
        S('links', ['Links'], n=(2, 3)),
    ],
    images=['photo_pantry.gif', 'pie.gif'], bullets=['ball_red.gif'], lines=['line_rope.gif'],
    styles=['gingham', 'wood', 'retro_tan'], layouts=['single'], midi=['hoedown', None], ring='y2k',
    keywords='canning food storage pantry preserving', desc=['Canning and long-term food storage'],
    gb=['64 quarts of tomatoes! Wow!', 'Bread and butter pickles are the best.']))

# ------------------------------------------------------------------ Driftwood
T3.append(T('vacation', 'Driftwood', 'Postcard', 4, age=(30, 60),
    titles=['Our Summer Vacation 1999', 'The Great {last} Road Trip', '{last} Family Vacation Slide Show',
            'Are We There Yet? (Our Trip Out West)'],
    intro=['This summer the {last} family piled into the minivan and drove 2,400 miles. Nobody threw up (until '
           'Nebraska). Here is the trip, day by day!',
           'Welcome to our vacation page! We went to the mountains, the beach AND the World\'s Second Largest Ball of '
           'Twine. Click on the pictures!'],
    sections=[
        S('log', ['Day By Day', 'Trip Diary'], [
            'Day 1: Left at 5 am. Kids asleep. By 7 am kids awake and asking "are we there yet". We were not.',
            'Day 2: The World\'s Second Largest Ball of Twine. The man in the gift shop was very proud.',
            'Day 3: Mountains! Dad got us lost on a "shortcut". We saw a moose. Worth it.',
            'Day 4: Motel pool. The kids say this was the best part of the whole trip. $1,800 for a motel pool.',
            'Day 5: The canyon! So big! Mom would not go near the edge.', 'Day 6: Flat tire in the desert. Dad '
            'changed it in 104 degrees. He is still talking about it.', 'Day 7: The beach! Sunburns all around.',
            'Day 8: Drove home. 14 hours. Played the license plate game. Found 41 states.'], n=(4, 8)),
        S('photos', ['Pictures', 'Photo Album'], [('photo_mountain.gif', 'The mountains (before Dad\'s shortcut)'),
                                                  ('photo_beach.gif', 'The beach on day 7'),
                                                  ('photo_car.gif', 'The minivan, our home for 8 days'),
                                                  ('photo_family.gif', 'Everybody (still speaking to each other)')],
          n=(2, 4)),
        S('list', ['Road Trip Tips'], ['Pack snacks. More snacks. More.', 'Bring a cooler', 'Motels with pools = happy '
                                                                                            'kids',
                                       'Get a real map, not just the "shortcut" Dad remembers', 'Books on tape!'],
          n=(3, 5)),
        S('links', ['Travel Links'], n=(2, 4)),
    ],
    images=['photo_mountain.gif', 'photo_beach.gif', 'globe.gif'], bullets=['ball_blue.gif', 'ball_yellow.gif'],
    lines=['rainbow_hr.gif', 'line_rope.gif'], styles=['clouds', 'water', 'retro_tan', 'border_blue', 'marble'],
    layouts=['single', 'sidebar', 'frames'], midi=['surf', 'elevator', None], ring='travel',
    keywords='family vacation road trip photos twine mountains beach', desc=['Family road trip diary and photos'],
    gb=['We saw the twine too!!!', 'Your kids are troopers.', 'Dad\'s shortcut LOL']))

T3.append(T('rv', 'Driftwood', 'Campground', 3, age=(55, 80),
    titles=['{first} & {spouse}\'s RV Adventures', 'Retired and On The Road', 'The Rolling {last}s'],
    entities=[dict(spouse='Bev'), dict(spouse='Earl'), dict(spouse='Marv')],
    intro=['We retired in 1996, sold the house, bought a 34-foot motorhome and hit the road. 48 states so far. This '
           'page is so the kids know where we are (sometimes we do not know either).'],
    sections=[
        S('table', ['States Visited', 'Where We\'ve Been'], [('Arizona', 'Winters. Every winter.'),
                                                             ('Maine', 'Lobster! Too much lobster.'),
                                                             ('Montana', 'Big sky. Big mosquitoes.'),
                                                             ('Texas', 'Took 4 days to cross it'),
                                                             ('Florida', 'Saw the space shuttle go up!'),
                                                             ('Oregon', 'Rained. The whole time.'),
                                                             ('South Dakota', 'The faces on the mountain')], n=(4, 7)),
        S('list', ['RV Tips'], ['Always check the tire pressure', 'Never trust a campground that says "rustic"',
                                'Make friends at every stop', 'Bring a good book for rainy days',
                                'Learn to back up with someone waving at you'], n=(3, 5)),
        S('photos', ['Pictures'], [('photo_car.gif', 'Our rig (well, a car, the RV would not fit in the scanner)'),
                                   ('photo_mountain.gif', 'Somewhere in Colorado')], n=(1, 2)),
        S('links', ['RV Links'], n=(2, 3)),
    ],
    images=['globe.gif', 'photo_mountain.gif'], bullets=['ball_green.gif'], lines=['line_rope.gif', 'rainbow_hr.gif'],
    styles=['retro_tan', 'wood', 'clouds'], layouts=['single'], midi=['hoedown', 'elevator'], ring='travel',
    keywords='rv motorhome retired travel campgrounds states', desc=['Retired couple\'s RV travel journal'],
    gb=['Safe travels!', 'Come visit us in Arizona!']))

T3.append(T('backpack', 'Driftwood', 'Postcard', 2, age=(19, 28),
    titles=['Europe On $30 A Day', '{handle}\'s Backpacking Journal'],
    intro=['After graduation I took my savings and a 40-pound backpack to Europe for 2 months. I wrote this journal in '
           'Internet cafes along the way (at $5 an hour, so excuse the typos).'],
    sections=[
        S('log', ['Journal'], ['Landed. Lost my luggage. Gained a friend at the luggage desk.',
                               'Night train. Slept sitting up next to a man eating sardines.',
                               'Hostel with 14 people in one room. One snorer. One VERY good snorer.',
                               'Climbed 600 steps to a cathedral roof. Worth it.', 'Ran out of money. Ate bread for 3 '
                                                                                   'days. Good bread though.',
                               'Last day. Sat by a fountain and wrote postcards to everyone.'], n=(4, 6)),
        S('list', ['Packing List'], ['A good pair of shoes', 'Rain jacket', 'Padlock for hostel lockers',
                                     'A phrasebook', 'Less stuff than you think'], n=(3, 5)),
        S('links', ['Travel Links'], n=(2, 3)),
    ],
    images=['globe.gif'], bullets=['ball_blue.gif'], lines=['line_rope.gif'], styles=['parchment', 'plain',
                                                                                       'border_green'],
    layouts=['single'], midi=[None], ring='travel', keywords='backpacking europe hostels journal',
    desc=['Two months backpacking around Europe'], gb=['The sardine man!!!']))

T3.append(T('themepark', 'Driftwood', 'Boardwalk', 2, age=(12, 40),
    titles=['Coaster Crazy!', 'Fun Kingdom Trip Report'],
    intro=['I am a roller coaster enthusiast. I have ridden 113 coasters in 9 states. Here are my rankings and trip '
           'reports!'],
    sections=[
        S('top10', ['Top Coasters', 'My Rankings'], ['The Thunderhawk (wooden, rattles your teeth out, perfect)',
                                                     'Steel Viper', 'The Corkscrewdriver', 'Mine Train Mayhem',
                                                     'Big Dipper Deluxe', 'The Vomitron 3000 (unofficial name)',
                                                     'Sky Scraper', 'The Loopy Loop'], n=(5, 8)),
        S('log', ['Trip Reports'], ['Fun Kingdom: Rode the Thunderhawk 11 times. Lost a shoe on ride 7.',
                                    'Boardwalk Pier: Old wooden coaster, built 1926. Terrifying in a good way.',
                                    'Opening day at Coaster Island: waited 3 hours. Ride was 58 seconds. No regrets.'],
          n=(2, 3)),
        S('links', ['Coaster Links'], n=(2, 3)),
    ],
    images=['hot.gif', 'twinkle.gif'], bullets=['ball_red.gif'], lines=['rainbow_line.gif'],
    styles=['checker', 'clouds', 'black_neon'], layouts=['single'], midi=['surf', 'techno'], ring='travel',
    keywords='roller coasters theme parks rankings trip reports', desc=['Roller coaster rankings and trip reports'],
    gb=['Thunderhawk is #1 for me too!']))

T3.append(T('cruise', 'Driftwood', 'Boardwalk', 1, age=(40, 70),
    titles=['Our Caribbean-ish Cruise'],
    intro=['For our 25th anniversary we took a 7-night cruise on the SS Sunny Disposition. Here is the scoop, '
           'including the midnight buffet (all 6 of them).'],
    sections=[
        S('log', ['Cruise Diary'], ['Boarded. Found the buffet. Found the second buffet.', 'At sea. Played bingo. Won '
                                    'a keychain.', 'Port day: snorkeling! Saw a fish that looked like Uncle Lou.',
                                    'Captain\'s dinner. Wore the tux. Spilled the soup.', 'Midnight buffet. Ice '
                                                                                         'sculpture of a swan.'],
          n=(3, 5)),
        S('photos', ['Photos'], [('photo_beach.gif', 'The private island'), ('photo_food.gif', 'The midnight buffet')],
          n=(1, 2)),
    ],
    images=['photo_beach.gif'], bullets=['ball_blue.gif'], lines=['rainbow_hr.gif'], styles=['water', 'bubbles'],
    layouts=['single'], midi=['surf', 'elevator'], ring='travel', keywords='cruise anniversary buffet snorkeling',
    desc=['Anniversary cruise diary'], gb=['Happy anniversary!']))

# ------------------------------------------------------------------ Skillet
RECIPES = [
    dict(name='Grandma Dot\'s Sunday Pot Roast', serves='6', ing=['3 lb chuck roast', '6 carrots', '6 potatoes',
                                                                  '2 onions', '1 packet onion soup mix',
                                                                  '2 cups water', 'Salt & pepper'],
         steps='Brown the roast in a hot Dutch oven. Pile the vegetables around it, sprinkle the soup mix over '
               'everything, add the water, cover, and bake at 325 for 3 hours while you are at church. Gravy: '
               'whatever is in the pan plus a spoonful of flour.'),
    dict(name='Lime Jiggle Party Salad', serves='12', ing=['2 boxes lime gelatin', '1 can crushed pineapple',
                                                           '1 cup cottage cheese', '1 cup mini marshmallows',
                                                           '1/2 cup chopped walnuts'],
         steps='Make the gelatin with a little less cold water than the box says. Chill until syrupy, stir in '
               'everything else, pour into a ring mold and chill overnight. Unmold onto lettuce. Everyone will '
               'ask what it is. Do not tell them.'),
    dict(name='Firehouse Five-Alarm Chili', serves='10', ing=['2 lb ground beef', '1 lb hot sausage',
                                                              '2 cans kidney beans', '2 cans crushed tomatoes',
                                                              '3 jalapenos', '3 tbsp chili powder', '1 tbsp cumin',
                                                              '1 bottle of beer (optional)', '1 square dark chocolate'],
         steps='Brown the meats. Add everything else. Simmer at least 3 hours. The chocolate is the secret. Do not '
               'tell the judges.'),
    dict(name='Blue Ribbon Snickerdoodles', serves='4 dozen', ing=['1 cup butter', '1 1/2 cups sugar', '2 eggs',
                                                                   '2 3/4 cups flour', '2 tsp cream of tartar',
                                                                   '1 tsp baking soda', 'Cinnamon sugar for rolling'],
         steps='Cream the butter and sugar, beat in the eggs, stir in the dry stuff. Roll into balls, roll the balls '
               'in cinnamon sugar, bake at 400 for 8 to 10 minutes. Won first place at the 1994 county fair.'),
    dict(name='Tater Tot Hotdish', serves='8', ing=['1 lb ground beef', '1 onion', '1 can cream of mushroom soup',
                                                    '1 can green beans', '1 bag tater tots', '1 cup shredded cheese'],
         steps='Brown the beef and onion, spread in a 9x13 pan. Layer the soup, then the beans, then the cheese, then '
               'line up the tots in neat rows (this is important). Bake at 375 for 45 minutes.'),
    dict(name='Smoky Backyard Ribs', serves='4', ing=['2 racks pork ribs', '1/4 cup brown sugar', '2 tbsp paprika',
                                                     '1 tbsp garlic powder', '1 tbsp salt', 'Your favorite sauce',
                                                     'Hickory chips'],
         steps='Rub the ribs the night before. Smoke low and slow at 225 for 5 hours, adding hickory every hour. '
               'Sauce them for the last 30 minutes. Lick fingers. Repeat.'),
    dict(name='Peanut Butter Fudge (No Fail)', serves='36 squares', ing=['2 cups sugar', '1/2 cup milk',
                                                                          '1 cup peanut butter', '1 jar marshmallow '
                                                                                                 'creme'],
         steps='Boil the sugar and milk for 3 minutes, stirring. Take off the heat, stir in the peanut butter and the '
               'marshmallow creme. Pour into a buttered pan. Hide it from your husband.'),
    dict(name='Seven-Layer Dip', serves='a party', ing=['1 can refried beans', '1 cup sour cream', '1 cup guacamole',
                                                        '1 cup salsa', '1 cup shredded cheese', 'Sliced olives',
                                                        'Chopped green onions'],
         steps='Layer in a glass dish in that order so everyone can see the layers. Serve with chips. It will be gone '
               'in 9 minutes.'),
    dict(name='Rhubarb Crisp', serves='8', ing=['4 cups chopped rhubarb', '1 cup sugar', '1 cup oats',
                                               '1 cup brown sugar', '1/2 cup flour', '1/2 cup butter'],
         steps='Toss rhubarb with the sugar and put it in a pan. Crumble the rest together and sprinkle on top. Bake at '
               '350 for 40 minutes. Vanilla ice cream is not optional.'),
    dict(name='Monster Cookies', serves='5 dozen', ing=['1 cup peanut butter', '1/2 cup butter', '1 cup brown sugar',
                                                        '3 eggs', '4 1/2 cups oats', '1 cup chocolate chips',
                                                        '1 cup candy-coated chocolates'],
         steps='Mix it all in your biggest bowl (there is no flour!). Drop big spoonfuls on a sheet, bake at 350 for '
               '12 minutes. The kids will call them monster cookies. You will call them breakfast.'),
    dict(name='Church Supper Baked Beans', serves='20', ing=['4 cans pork and beans', '1 lb bacon', '1 onion',
                                                             '1 cup brown sugar', '1/2 cup ketchup', '2 tbsp mustard'],
         steps='Fry the bacon and onion. Mix everything in a big roaster. Bake at 325 for 2 hours. Bring the '
               'roaster home empty.'),
    dict(name='Frosted Sugar Cookie Cutouts', serves='3 dozen', ing=['1 cup butter', '1 cup sugar', '1 egg',
                                                                     '1 tsp vanilla', '3 cups flour',
                                                                     'Powdered sugar frosting', 'Sprinkles!!!'],
         steps='Mix, chill 2 hours, roll out, cut into shapes, bake at 375 for 7 minutes. Frost when cool. Let the kids '
               'do the sprinkles and then sweep the whole kitchen.'),
]

T3.append(T('grandma', 'Skillet', 'Oven', 5, age=(45, 85), gender='f',
    titles=['Grandma\'s Kitchen', '{first}\'s Recipe Box', 'Recipes From The {last} Farm', 'Mom\'s Best Recipes',
            'Comfort Food Corner'],
    intro=['Come on in and sit down! These are the recipes I have been making for my family for 40 years, typed up '
           'by my grandson so they do not get lost when I am gone (not for a while yet, I hope).',
           'Every family has a recipe box. This is ours. Some of these recipes came over from the old country, some '
           'came off the back of a soup can. All of them are good.'],
    sections=[
        S('recipes', ['Recipes', 'From The Recipe Box', 'Family Favorites'], RECIPES, n=(3, 5)),
        S('list', ['Kitchen Tips', 'Grandma\'s Tips'], ['Butter, not margarine.', 'Read the whole recipe first.',
                                                        'Clean as you go.', 'A pinch of salt makes sweet things '
                                                                            'sweeter.',
                                                        'If it smells done, check it.', 'Always make a little extra for '
                                                                                        'the neighbors.'], n=(3, 5)),
        S('links', ['Other Recipe Pages', 'Cooking Links'], n=(3, 5)),
    ],
    images=['pie.gif', 'photo_food.gif', 'photo_cake.gif'], bullets=['ball_red.gif', 'bullet_heart.gif'],
    lines=['line_rope.gif', 'rainbow_hr.gif', 'line_hearts.gif'],
    styles=['gingham', 'retro_tan', 'pastel_flowers', 'wood', 'parchment'], layouts=['single', 'sidebar', 'frames'],
    midi=['ragtime', 'lullaby', 'hoedown', None], ring='recipes',
    keywords='recipes grandma home cooking casseroles cookies pot roast', desc=['Family recipes from {first}\'s kitchen',
                                                                                'Grandma\'s recipe box online'],
    gb=['I made the hotdish and my husband had thirds!', 'Just like my grandma used to make.',
        'The gelatin salad was a hit at the potluck!']))

T3.append(T('bbq', 'Skillet', 'Grill', 3, age=(30, 65), gender='m',
    titles=['{handle}\'s BBQ Pit', 'Low & Slow BBQ', 'Smoke Signals: A Barbecue Page'],
    intro=['Barbecue is not a verb. It is a way of life. Welcome to my pit, where the smoke rolls and the ribs fall '
           'off the bone.'],
    sections=[
        S('recipes', ['Pit Recipes'], RECIPES[5:6] + RECIPES[2:3] + RECIPES[7:8], n=(2, 3)),
        S('table', ['Competition Results'], [('Smokin\' on the River', '3rd place ribs'),
                                             ('County Fair BBQ-Off', '1st place brisket!!!'),
                                             ('Hog Wild Festival', '7th place (rained)')], n=(2, 3)),
        S('list', ['Rules of the Pit'], ['Never peek. If you\'re lookin\', you ain\'t cookin\'.', 'Hickory for pork, '
                                                                                                  'oak for beef',
                                         'Sauce at the end, not the beginning', 'Beer is for the cook'], n=(3, 4)),
        S('links', ['BBQ Links'], n=(2, 4)),
    ],
    images=['fire.gif', 'photo_food.gif', 'chili.gif'], bullets=['ball_red.gif'], lines=['flames.gif', 'line_rope.gif'],
    styles=['wood', 'border_flames', 'checker', 'denim'], layouts=['single', 'sidebar'], midi=['hoedown'],
    ring='recipes', keywords='bbq barbecue ribs smoking brisket competition', desc=['Barbecue recipes and competitions'],
    gb=['Made the ribs. Wife proposed again.', 'Hickory all the way!']))

T3.append(T('chili', 'Skillet', 'Grill', 2, age=(30, 70),
    titles=['Chili Cook-Off Champion', 'Red Hot Chili Page'],
    intro=['Three-time winner of the {town} Firehouse Chili Cook-Off. Here is my recipe (well, MOST of it).'],
    sections=[
        S('recipes', ['The Recipe'], RECIPES[2:3], n=(1, 1)),
        S('table', ['Heat Scale'], [('Mild', 'For the kids'), ('Medium', 'For most folks'), ('Hot', 'For the '
                                                                                                'firemen'),
                                    ('Five-Alarm', 'Sign a waiver')], n=(4, 4)),
        S('links', ['Chili Links'], n=(2, 3)),
    ],
    images=['chili.gif', 'hot.gif', 'fire.gif'], bullets=['ball_red.gif'], lines=['flames.gif'],
    styles=['border_flames', 'gingham', 'denim'], layouts=['single'], midi=['hoedown'], ring='recipes',
    keywords='chili cook-off recipe five alarm', desc=['Award-winning five-alarm chili'], gb=['Too hot! Loved it!']))

T3.append(T('sweets', 'Skillet', 'Sweets', 3, age=(20, 70), gender='f',
    titles=['Sugar & Spice Baking', 'The Cookie Jar', '{first}\'s Sweet Treats'],
    intro=['I bake when I am happy, I bake when I am sad, and I bake when it is Tuesday. Here are my favorite sweet '
           'recipes. Calories do not count on the Internet.'],
    sections=[
        S('recipes', ['Sweet Recipes'], [RECIPES[3], RECIPES[6], RECIPES[8], RECIPES[9], RECIPES[11], RECIPES[1]],
          n=(3, 4)),
        S('list', ['Baking Tips'], ['Room temperature butter!', 'Do not overmix', 'Use parchment paper',
                                    'Always taste the dough (quality control)'], n=(3, 4)),
        S('links', ['Baking Links'], n=(2, 4)),
    ],
    images=['pie.gif', 'photo_cake.gif', 'heart.gif'], bullets=['bullet_heart.gif', 'ball_pink.gif'],
    lines=['line_bows.gif', 'line_hearts.gif'], styles=['pastel_hearts', 'gingham', 'pastel_flowers', 'glitter'],
    layouts=['single', 'sidebar'], midi=['kitten_waltz', 'holiday'], ring='recipes',
    keywords='baking cookies fudge desserts sweets recipes', desc=['Sweet baking recipes'],
    gb=['The fudge recipe is dangerous. Thank you.', 'Snickerdoodles turned out perfect!']))

# ------------------------------------------------------------------ Workbench
T3.append(T('carrestore', 'Workbench', 'Garage', 3, age=(30, 70), gender='m',
    titles=['Project Car: My \'{year} {car}', 'The {last} Garage', 'Restoring Old Blue'],
    entities=[dict(car='Thunderbolt Super Sport', year='68'), dict(car='Comet Cruiser', year='57'),
              dict(car='Mustang-ish... no, a Stallion GT', year='66')],
    intro=['In 1994 I bought a \'{year} {car} from a farmer for $400 and a case of motor oil. It had a tree growing '
           'through the floor. Five years later... it still is not done. But it is close! Follow the restoration here.'],
    sections=[
        S('log', ['Restoration Log', 'Progress'], ['Pulled the engine. Found a mouse family. Relocated them.',
                                                   'Sandblasted the frame. Neighbors not thrilled.',
                                                   'New floor pans welded in. Goodbye tree.', 'Engine rebuilt: '
                                                                                              '.030 over, new cam, '
                                                                                              'sounds like thunder.',
                                                   'Paint! Candy apple red. Took 3 weekends and my whole garage is now '
                                                   'red too.', 'Chrome bumpers back from the plater. Blinding.',
                                                   'First drive around the block. Wife cried. I cried. The mouse family '
                                                   'did not comment.'], n=(4, 7)),
        S('table', ['Specs'], [('Engine', '350 V8, 4 barrel'), ('Transmission', '4 speed'), ('Paint', 'Candy apple '
                                                                                                    'red'),
                               ('Interior', 'Black vinyl (new)'), ('Money spent', 'Do not tell my wife')], n=(3, 5)),
        S('photos', ['Photos'], [('photo_car.gif', 'The car today'), ('gear.gif', 'Engine (artist\'s impression)')],
          n=(1, 2)),
        S('links', ['Car Links'], n=(2, 4)),
    ],
    images=['photo_car.gif', 'gear.gif', 'flames.gif'], bullets=['ball_red.gif'], lines=['flames.gif', 'line_rope.gif'],
    styles=['checker', 'concrete', 'denim', 'border_flames'], layouts=['single', 'sidebar'], midi=['surf', None],
    ring='gearheads', keywords='car restoration classic project engine paint {car}',
    desc=['Restoring a \'{year} {car}'], gb=['Candy apple red is the only color.', 'Mice relocation, very humane.']))

T3.append(T('quilt', 'Workbench', 'Quilt', 3, age=(40, 80), gender='f',
    titles=['Quilting Bee Corner', '{first}\'s Quilt Gallery', 'Patchwork Memories'],
    intro=['Welcome to my sewing room! I have been quilting for 30 years and I belong to the Tuesday Morning Quilting '
           'Bee at the {town} library. Here are some of my quilts and patterns.'],
    sections=[
        S('table', ['My Quilts', 'Gallery'], [('Double Wedding Ring', 'For my granddaughter\'s wedding, 1998'),
                                              ('Log Cabin', 'My first quilt, 1969. Crooked but loved.'),
                                              ('Grandmother\'s Flower Garden', 'Hand-pieced, 2 years'),
                                              ('Crazy Quilt', 'Made from my late husband\'s ties'),
                                              ('Y2K Millennium Quilt', 'In progress! 2000 different fabrics!')],
          n=(3, 5)),
        S('list', ['Quilting Tips'], ['Press your seams', 'Measure twice, cut once', 'A sharp rotary cutter is a safe '
                                                                                      'rotary cutter',
                                      'Buy more fabric than you need. You will need it.'], n=(3, 4)),
        S('links', ['Quilting Links'], n=(2, 4)),
    ],
    images=['heart.gif'], bullets=['bullet_heart.gif', 'ball_purple.gif'], lines=['line_bows.gif', 'line_rope.gif'],
    styles=['gingham', 'pastel_flowers', 'parchment', 'retro_tan'], layouts=['single'], midi=['kitten_waltz', 'lullaby'],
    ring='crafty', keywords='quilting quilts patterns sewing bee', desc=['Quilt gallery and tips'],
    gb=['The tie quilt made me tear up.', 'Can I get the pattern for the flower garden?']))

T3.append(T('plushie', 'Workbench', 'Collectibles', 5, age=(10, 60),
    titles=['Plushie Pals Paradise', '{handle}\'s Plushie Pals Collection', 'Mint With Mint Tags!',
            'Plushie Pals Price Guide', 'The Plushie Pals Swap Shop'],
    intro=['I collect <B>Plushie Pals</B>, the little bean-bag critters everyone is crazy about! I have 212 of them '
           'and every single one has its tag (with a tag protector!). Here is my collection and my price guide.',
           'Welcome, fellow Plushie Pals collector! Remember: NEVER cut off the tag. A Pal without a tag is just a '
           'stuffed animal.'],
    sections=[
        S('table', ['Price Guide', 'What They\'re Worth'], [('Patches the Pony (1st gen tag)', '$45'),
                                                           ('Bingo the Bear (RETIRED)', '$300!!!'),
                                                           ('Sir Waddles the Penguin', '$12'),
                                                           ('Peaches the Pig', '$8'), ('Ziggy Zebra (rare tag error)',
                                                                                      '$150'),
                                                           ('Hoot the Owl', '$6'), ('Rosie the Ladybug', '$5'),
                                                           ('Midnight the Black Cat', '$22'),
                                                           ('Millennium Bear (not out yet!)', '???')], n=(5, 9)),
        S('list', ['Collecting Tips'], ['Keep the tags on and in protectors!', 'Store out of the sun',
                                        'Watch out for fakes (check the stitching)', 'Retired Pals go up in value FAST',
                                        'Do not let your dog near them. Trust me.'], n=(3, 5)),
        S('table', ['Want List / Have List'], [('WANT', 'Bingo the Bear, Ziggy Zebra'), ('HAVE (to trade)', '3 Hoots, '
                                                                                                         '2 Peaches')],
          n=(2, 2)),
        S('links', ['Other Collectors'], n=(3, 5)),
    ],
    images=['heart.gif', 'plushie.gif', 'twinkle.gif'], bullets=['bullet_heart.gif', 'bullet_star.gif'],
    lines=['line_hearts.gif', 'rainbow_line.gif'], styles=['pastel_hearts', 'glitter', 'pastel_flowers',
                                                          'border_pink'],
    layouts=['single', 'sidebar'], midi=['kitten_waltz', 'heartthrob'], ring='crafty',
    keywords='plushie pals collectibles bean bag price guide tags retired',
    desc=['Plushie Pals collection and price guide', 'Plushie Pals trading and want list'],
    gb=['Want to trade for Ziggy? I have 2!', 'My dog ate Peaches. RIP.', '$300 for Bingo?!'],
    features={'badges': ['plushie.gif']}))

T3.append(T('stamps', 'Workbench', 'Collectibles', 1, age=(50, 85), gender='m',
    titles=['Stamp Collecting With {first}'],
    intro=['I have been collecting stamps since 1946. My specialty is airmail covers and stamps with birds on them.'],
    sections=[
        S('list', ['My Collection'], ['US airmail 1918-1960', 'Birds of the world (topical)', 'First day covers',
                                      'A whole album of stamps with lighthouses'], n=(3, 4)),
        S('para', ['Why Stamps?'], ['Every stamp is a tiny piece of history you can hold in your hand. And they are '
                                    'quiet, unlike my grandson\'s video games.'], n=(1, 1)),
        S('links', ['Links'], n=(2, 3)),
    ],
    images=[], bullets=['ball_blue.gif'], lines=['rainbow_hr.gif'], styles=['plain', 'parchment'], layouts=['single'],
    midi=[None], ring='crafty', keywords='stamps philately airmail collecting', desc=['Stamp collecting page'],
    gb=['I collect lighthouses too!']))

T3.append(T('trains', 'Workbench', 'Trains', 3, age=(35, 80), gender='m',
    titles=['The {line} Railroad (HO Scale)', '{first}\'s Model Railroad', 'All Aboard the {line}!'],
    entities=[dict(line='Pine Hollow & Western'), dict(line='Basement Valley Line'), dict(line='Duluth & Cheese Belt')],
    intro=['Welcome to the <B>{line}</B>, an HO scale model railroad that fills most of my basement (my wife has the '
           'laundry corner). Construction began in 1987 and will end... never, that is the fun of it.'],
    sections=[
        S('table', ['Layout Facts'], [('Scale', 'HO (1:87)'), ('Size', '18 x 24 feet'), ('Track', '340 feet'),
                                      ('Era', '1950s transition (steam AND diesel!)'), ('Locomotives', '23'),
                                      ('Freight cars', '140'), ('Tiny people', 'about 400')], n=(4, 7)),
        S('log', ['Construction Notes'], ['Finished the trestle over Hollow Creek. Used 2,000 craft sticks.',
                                          'Grandkids visited. One locomotive now lives in the creek.',
                                          'Added working crossing lights. Watched them for an hour.',
                                          'Built a tiny diner with tiny people eating tiny pie.',
                                          'Operating session with the club: 4 hours, 2 derailments, 0 regrets.'],
          n=(3, 5)),
        S('photos', ['Photos'], [('train.gif', 'The 4-8-4 pulling the evening freight'),
                                 ('photo_mountain.gif', 'The mountain scene (plaster and paint)')], n=(1, 2)),
        S('links', ['Railroad Links'], n=(2, 4)),
    ],
    images=['train.gif'], bullets=['ball_green.gif', 'ball_red.gif'], lines=['line_rope.gif', 'rainbow_hr.gif'],
    styles=['wood', 'retro_tan', 'grass', 'plain'], layouts=['single', 'sidebar'], midi=['ragtime', 'hoedown'],
    ring='gearheads', keywords='model railroad ho scale trains layout {line}', desc=['HO scale model railroad layout'],
    gb=['Love the trestle!', 'Tiny pie!!!']))

# fix a near-real car name
for _t in T3:
    if _t['key'] == 'carrestore':
        _t['entities'][2] = dict(car='Stallion GT', year='66')
    if _t['key'] == 'cruise':
        _t['titles'] = ['Our Island Cruise']
