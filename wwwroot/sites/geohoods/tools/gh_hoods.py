"""gh_hoods.py -- the GeoHoods neighborhoods and suburbs (shared by mkgfx.py and mkhomepages.py).

Everything here is invented for the 1999 Web parody.  Each neighborhood has:
  key       folder / URL name (StudlyCaps, like the real thing)
  title     display name
  tagline   one-line theme
  blurb     paragraph for the neighborhood directory
  color     (dark, light) hex colors used for the landing page
  icon      icon kind drawn by mkgfx.py
  suburbs   list of (name, description)
"""

HOODS = [
    dict(key='SiliconHills', title='SiliconHills', tagline='Computers, programming & the Information Superhighway',
         blurb='Overclockers, HTML wizards, BBS veterans and anyone who has ever opened a beige case with a butter knife. '
               'If it beeps, boots or blue-screens, it lives here.',
         color=('#003366', '#CCE6FF'), icon='chip',
         suburbs=[('Lab', 'Homebrew hardware, overclocking and "my rig" pages'),
                  ('Mainframe', 'Programmers, scripters and the Gnulix faithful'),
                  ('Modem', 'BBS nostalgia, online services and dial-up refugees'),
                  ('Pixel', 'Web design tutorials, free graphics and HTML help')]),
    dict(key='Tinseltown', title='Tinseltown', tagline='Movies, television & the stars',
         blurb='Fan shrines, episode guides, spoiler-free reviews (mostly) and the occasional screenplay a homesteader '
               'is absolutely going to sell next year.',
         color=('#660000', '#FFE9C9'), icon='film',
         suburbs=[('Marquee', 'Blockbusters, reviews and movie trivia'),
                  ('Couch', 'Television: sitcoms, dramas and episode guides'),
                  ('Backlot', 'Home movies, screenwriting and special effects'),
                  ('Premiere', 'Heartthrob shrines and celebrity fan clubs')]),
    dict(key='Gridiron', title='Gridiron', tagline='Sports, fitness & the great outdoors',
         blurb='Fantasy leagues, Little League rosters, bowling averages and enough team spirit to paint a stadium. '
               'Bring your foam finger.',
         color=('#004400', '#E0F5D0'), icon='football',
         suburbs=[('Bleachers', 'Fans of the big leagues and fantasy football'),
                  ('Dugout', 'Little League, softball and the local team'),
                  ('Pitstop', 'Stock cars, drag racing and motorsports'),
                  ('Tackle', 'Fishing, hunting, bowling and wrestling')]),
    dict(key='Area52', title='Area52', tagline='Science fiction, UFOs & the unexplained',
         blurb='The truth is in here. Sightings, abductions, starship schematics, fan fiction and the occasional '
               'tinfoil hat pattern. Keep watching the skies.',
         color=('#000033', '#D8D8FF'), icon='ufo',
         suburbs=[('Hangar', 'UFO sightings, abductions and cover-ups'),
                  ('Nebula', 'Space opera shrines and starship fan fiction'),
                  ('Vault', 'The Murk Files and paranormal TV'),
                  ('Saucer', 'Cryptozoology, crop circles and strange lights')]),
    dict(key='Bayou', title='Bayou', tagline='Music of every kind',
         blurb='Boy-band shrines, garage bands, MIDI collections, lyrics (our own!) and tour diaries. Turn your '
               'speakers up: half the homes on this street play music when you walk in.',
         color=('#330066', '#F0E0FF'), icon='note',
         suburbs=[('Jukebox', 'MIDI collections and music trivia'),
                  ('Backstage', 'Fan clubs for pop groups and singers'),
                  ('Mosh', 'Punk, ska, grunge and garage bands'),
                  ('Bandstand', 'Country, jazz, polka and community bands')]),
    dict(key='Hearth', title='Hearth', tagline='Family, home & genealogy',
         blurb='Baby announcements, family reunions, wedding albums and family trees going back to the old country. '
               'Pull up a chair, there is pie.',
         color=('#663300', '#FFF2DD'), icon='house',
         suburbs=[('Porch', 'Family home pages and newsletters'),
                  ('Nursery', 'Babies, toddlers and proud parents'),
                  ('Attic', 'Genealogy and family history'),
                  ('Garden', 'Gardening, weddings and home improvement')]),
    dict(key='Prairie', title='Prairie', tagline='Pets & animals',
         blurb='Kittens in teacups, dogs in sunglasses, hamsters with their own webrings, and gentle memorial pages '
               'for the friends who are waiting for us.',
         color=('#336600', '#F2FFE0'), icon='paw',
         suburbs=[('Litterbox', 'Cats and kittens'),
                  ('Kennel', 'Dogs and puppies'),
                  ('Burrow', 'Hamsters, ferrets, fish and other small pets'),
                  ('Meadow', 'Horses, farm animals and pet memorials')]),
    dict(key='Boulevard', title='Boulevard', tagline='Fashion, beauty & style',
         blurb='Glitter, platform shoes, prom night photo albums and makeup tips. The sidewalks here are pink and '
               'nobody minds.',
         color=('#990066', '#FFE6F5'), icon='heel',
         suburbs=[('Runway', 'Fashion, trends and style tips'),
                  ('Vanity', 'Makeup, hair and nails'),
                  ('Boutique', 'Prom, weddings and special occasions')]),
    dict(key='Athenaeum', title='Athenaeum', tagline='Literature, poetry & writing',
         blurb='Sonnets, free verse, dark poetry, fan fiction archives and book reviews. Mind the candles; some of '
               'the poets here have very black backgrounds.',
         color=('#333300', '#F5F0DC'), icon='book',
         suburbs=[('Quill', 'Poetry of every kind'),
                  ('Stacks', 'Book reviews and reading lists'),
                  ('Inkwell', 'Fan fiction and short stories'),
                  ('Sonnet', 'Love poems and song lyrics')]),
    dict(key='Arcade', title='Arcade', tagline='Games, gamers & game cheats',
         blurb='Cheat codes, walkthroughs, clan pages and the biggest Monstropals trainer community on the Web. '
               'Insert coin to continue.',
         color=('#000066', '#E0E8FF'), icon='joystick',
         suburbs=[('Joystick', 'Console games, cheats and codes'),
                  ('Pocket', 'Monstropals trainers and collectors'),
                  ('Fragzone', 'PC games, clans and LAN parties'),
                  ('Dungeon', 'Role-playing games and dice')]),
    dict(key='Campus', title='Campus', tagline='Teens, students & school life',
         blurb='About-me pages, dorm cams, class pages for the Class of 2000, and a great many "my first webpage!!!" '
               'pages. Please sign their guestbooks.',
         color=('#000099', '#FFFFCC'), icon='cap',
         suburbs=[('Hallway', 'Teen home pages and about-me pages'),
                  ('Dorm', 'College life, dorm cams and road trips'),
                  ('Quad', 'Clubs, classes and the Class of 2000')]),
    dict(key='Bunker', title='Bunker', tagline='Y2K, survival & things they don\'t want you to know',
         blurb='Will the clocks roll over or will the lights go out? Homesteaders here are ready either way: canned '
               'goods, ham radios, generators and a healthy suspicion of anything with a chip in it.',
         color=('#333300', '#EAEAD0'), icon='bunker',
         suburbs=[('Silo', 'Y2K preparedness and survival'),
                  ('Antenna', 'Ham radio, scanners and shortwave'),
                  ('Pantry', 'Food storage, canning and self-reliance')]),
    dict(key='Driftwood', title='Driftwood', tagline='Travel, vacations & road trips',
         blurb='Family vacations, cross-country RV journeys, backpacking diaries and slide shows of the World\'s '
               'Second Largest Ball of Twine.',
         color=('#006666', '#DFFFFF'), icon='palm',
         suburbs=[('Postcard', 'Family vacations and trip reports'),
                  ('Campground', 'RVs, camping and the open road'),
                  ('Boardwalk', 'Beaches, cruises and theme parks')]),
    dict(key='Skillet', title='Skillet', tagline='Food, cooking & recipes',
         blurb='Grandma\'s recipe box, barbecue secrets, chili cook-off champions and a surprising number of gelatin '
               'salads. Wipe your feet.',
         color=('#993300', '#FFF0E0'), icon='pan',
         suburbs=[('Oven', 'Baking, desserts and family recipes'),
                  ('Grill', 'Barbecue, chili and cook-offs'),
                  ('Sweets', 'Candy, cookies and cake decorating')]),
    dict(key='Workbench', title='Workbench', tagline='Hobbies, crafts & collecting',
         blurb='Model trains, quilting bees, car restorations and the Plushie Pals collectors who know the tag '
               'generation of every bean-bag critter ever sewn.',
         color=('#4D3319', '#F3EBDD'), icon='hammer',
         suburbs=[('Garage', 'Cars, engines and restorations'),
                  ('Quilt', 'Sewing, quilting and crafts'),
                  ('Collectibles', 'Plushie Pals, stamps, coins and cards'),
                  ('Trains', 'Model railroads and woodworking')]),
]

HOOD = dict((h['key'], h) for h in HOODS)
