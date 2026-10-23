"""gh_themes1.py -- Area52, SiliconHills, Tinseltown, Gridiron, Bayou homepage themes.
All shows, bands, products and people are invented for the parody."""
from gh_tdefs import S, SUB, T

MURK_EPISODES = [
    ('Pilot', 'Agent Holloway meets Dr. Petrakis in a cornfield. Something hums. Nobody believes them.'),
    ('Salt Flats', 'Three hikers lose nine hours in the desert and come back speaking backwards.'),
    ('The Quiet Orchard', 'An apple farm where nobody has aged since 1957. The cider is NOT safe.'),
    ('Dead Air', 'A late-night radio host keeps getting calls from a listener who died in 1981.'),
    ('Seventeen Minutes', 'A whole town loses seventeen minutes every night at 3:03 am. Holloway stays awake.'),
    ('Cornfield Lights', 'The Consortium is testing something over Nebraska. Petrakis finally sees it too (sort of).'),
    ('Hollow Earth Motel', 'Room 9 has a staircase that goes down further than the building does.'),
    ('The Lighthouse Keeper', 'A lighthouse that signals ships that are not there. Yet.'),
    ('Static', 'Every TV in a trailer park shows the same face. My favorite episode EVER.'),
    ('Licorice', 'We finally learn where the Licorice Man buys his licorice. Chills!!!'),
    ('Paper Moon', 'Holloway finds his sister\'s name in a government file folder made of something not paper.'),
    ('Dust Devil', 'A tornado that only hits one family, every year, on the same day.'),
]

T1 = []

# ------------------------------------------------------------------ Area52
T1.append(T('ufo', 'Area52', 'Hangar', 6, age=(24, 66),
    titles=['{first}\'s UFO Sighting Log', 'The {town} UFO Report', 'Lights Over {town}', 'UFO Truth Page',
            '{handle}\'s Skywatch HQ', 'They Are Here: The {last} Files'],
    intro=['I am not crazy. On the night of {date1} I saw something over {town} that I cannot explain, and I have '
           'been keeping records ever since. This page is my attempt to get the truth out there before they shut me '
           'down.',
           'Welcome, fellow skywatcher. This site documents unexplained aerial phenomena in the greater {town} area. '
           'Everything here was seen by me or by people I trust. Draw your own conclusions.',
           'Some people collect stamps. I collect sightings. {n1} of them so far, all logged with date, time and '
           'direction. Keep watching the skies!'],
    sections=[
        S('log', ['My Sighting Log', 'Sightings 1997-1999', 'The Log'], [
            'Three orange lights in a triangle over the water tower. Silent. Hovered 4 minutes then shot off to the NE.',
            'Bright white light, way too fast for a plane, zig-zagged twice. Dog went nuts.',
            'Cigar-shaped object, metallic, low over Route 9. My brother-in-law saw it too and he does not believe in ANYTHING.',
            'Pulsing green orb over the cornfield behind the Kwik-Stop. Car radio went to static.',
            'Disc with a ring of red lights. I got a photo (see Photos page) but it came out blurry, as usual.',
            'Formation of 5 lights in a V. Could have been geese. Geese do not glow.',
            'Humming noise all night, no lights. Neighbor\'s TV kept turning on by itself.',
            'Something blocked out the stars over the lake for about 30 seconds. Huge. Black. Triangle.',
            'Two jets chased a single amber light. The jets came back. The light did not.',
            'Lost about 40 minutes driving home from my shift. Clock in the truck said 2:10, then 2:50. No memory.',
            'Blue light landed (?) in the gravel pit. Found a circle of dead grass the next morning.',
            'Saw the same three lights as in March. They are coming back on a schedule, I am sure of it.',
        ], n=(4, 7)),
        S('list', ['What To Do If YOU See A UFO', 'Skywatching Tips'], [
            'Stay calm. Write down the time FIRST, everything else second.',
            'Note the direction and estimate the angle above the horizon with your fist (one fist = 10 degrees).',
            'Do not approach any landed craft. I mean it.',
            'Bring a camera with FAST film (400 or higher).',
            'Check the airport schedule afterward so the skeptics can\'t say it was the 9:40 from Denver.',
            'Tell someone you trust. Then tell me! E-mail me your report.',
            'Do NOT report it to the base. They already know.',
            'Keep a notebook in your glove compartment at all times.',
        ], n=(4, 6)),
        S('para', ['My Theory', 'What I Believe'], [
            'I believe the lights are surveying us. The pattern of sightings follows the power lines, which tells me '
            'they are interested in our electricity. Maybe they need it. Maybe they are studying it. Either way, '
            'the government knows more than it is saying.',
            'Most sightings can be explained: planes, satellites, weather balloons, swamp gas. I am a reasonable '
            'person. But about 5 percent cannot be explained, and that 5 percent is what this page is about.',
            'The official story changes every time somebody asks. First it was a balloon, then a flare, then a '
            '"training exercise". A training exercise for WHAT?',
        ], n=(1, 2), prob=0.8),
        S('links', ['Other Truth Seekers', 'Links to the Truth', 'More UFO Pages'], n=(4, 7)),
    ],
    subpages=[SUB('photos.html', ['UFO Photos', 'My Evidence'], [
        S('photos', ['Photos (click to enlarge... just kidding, they are already big)'],
          [('photo_ufo.gif', 'November 3rd, 1998, 2:14 am, looking west. Note the four lights.'),
           ('photo_mountain.gif', 'Where I saw the triangle. It was right above the left peak.'),
           ('broken.gif', 'This one got confiscated. Seriously. Ask me about it.'),
           ('photo_house.gif', 'My house. The lights hovered right over the garage.')], n=(2, 4))]),
        SUB('report.html', ['Report a Sighting'], [
            S('poll', ['Report Your Sighting'], ['Lights', 'Disc', 'Triangle', 'Cigar', 'Orb', 'Other / unsure'])])],
    images=['ufo.gif', 'alien.gif', 'photo_ufo.gif'], bullets=['bullet_alien.gif', 'bullet_star.gif'],
    lines=['line_stars.gif', 'line_laser.gif', 'line_lightning.gif'],
    styles=['starfield', 'nebula', 'black_neon', 'hacker', 'border_blue', 'snow'],
    layouts=['single', 'single', 'sidebar', 'frames'], midi=['spooky', 'starfield', None],
    ring='truth', keywords='ufo sighting lights aliens skywatch truth',
    desc=['Personal UFO sighting log with photos', 'Strange lights over {town} - sightings and theories',
          'Documented UFO reports from {state}'],
    gb=['I saw the same triangle over Kansas!! E-mail me ASAP.', 'The truth is in here. Great page.',
        'You are being watched. (Just kidding. Or am I?)', 'Have you read about the Salt Flats incident?']))

T1.append(T('murk', 'Area52', 'Vault', 5, age=(15, 45),
    titles=['The Murk Files Shrine', 'LOOK CLOSER: A Murk Files Fan Page', '{first}\'s Murk Files Episode Guide',
            'Holloway & Petrakis Forever', 'The Licorice Man Is Watching'],
    intro=['Welcome to my shrine to <B>The Murk Files</B>, the best show on television, Friday nights at 9 on '
           'Channel 9. If you have not seen it, stop reading this and go find a tape. Agent Dale Holloway believes. Dr. '
           'Renata Petrakis does not. Together they investigate the cases the Bureau would rather bury.',
           'This page is dedicated to the scariest, smartest show ever made. I have watched every episode at least '
           'three times and I tape the reruns just in case. Spoilers below!!!',
           'LOOK CLOSER. That is the motto of the show and of this page. Here you will find episode summaries, my '
           'theories about the Consortium, and a whole lot of pictures of Agent Holloway (sorry, not sorry).'],
    sections=[
        S('table', ['Episode Guide', 'Season One Episodes', 'My Episode Guide (with ratings)'], MURK_EPISODES, n=(5, 9)),
        S('list', ['Characters', 'Who\'s Who'], [
            '<B>Agent Dale Holloway</B> - believer, sunflower-seed eater, lost his sister to the lights in 1973.',
            '<B>Dr. Renata Petrakis</B> - medical doctor, skeptic, always has a flashlight.',
            '<B>The Licorice Man</B> - never says his name, always chewing. Knows everything.',
            '<B>Director Kessler</B> - Holloway\'s boss. Is he on our side? NOBODY KNOWS.',
            '<B>The Consortium</B> - a group of old men in a smoky room deciding the fate of the planet.',
            '<B>The Basement Three</B> - three conspiracy nerds who publish a newsletter from a basement.',
        ], n=(4, 6)),
        S('top10', ['Top 10 Murk Files Moments', 'Best Quotes'], [
            '"I want to see it. Not believe it. SEE it."',
            'When Petrakis finally admits the lights were "not entirely conventional."',
            'The flashlight duel in the motel basement.',
            '"Look closer, Agent Holloway. You always miss the part that matters."',
            'The Licorice Man\'s first appearance (just standing there. chewing.)',
            'The entire episode "Static". Do not watch it alone.',
            'Holloway eating sunflower seeds during an autopsy. Gross. Iconic.',
            'The cliffhanger at the end of season two. I screamed.',
            '"Somewhere out there is a filing cabinet with my whole life in it."',
            'The cornfield. You know the scene.',
        ], n=(5, 10)),
        S('para', ['Holloway + Petrakis = ?', 'Shipper or No-Romo?'], [
            'Okay, I have to say it. They are SO in love. The way he looks at her in "The Lighthouse Keeper"? '
            'Come on. I am a proud shipper and I do not care who knows.',
            'I am a NoRomo and proud of it. Their partnership is better than any romance. Leave them alone, '
            'writers!!!',
        ], n=(1, 1), prob=0.6),
        S('links', ['Other Murk Files Pages', 'The Murk Webring Neighbors'], n=(3, 6)),
    ],
    subpages=[SUB('theories.html', ['My Consortium Theories', 'The Mythology Explained (I Think)'], [
        S('para', ['Theories'], [
            'The Consortium has been working with the visitors since at least 1947. The bees in season 2 are part of '
            'it. So is the corn.',
            'Holloway\'s sister was taken as part of a "trade". The Licorice Man made the deal.',
            'Director Kessler is a double agent. Watch his left hand in every scene.',
            'The black liquid and the static are the SAME THING. Mark my words.',
        ], n=(3, 4))], prob=0.7),
        SUB('fanfic.html', ['My Murk Files Fan Fiction'], [
            S('story', ['Fan Fiction'], [('After Hours', [
                'Rating: PG. Disclaimer: The Murk Files and its characters are not mine. I am just borrowing them.',
                'The basement office was cold. Holloway had been staring at the same photograph for two hours when '
                'Petrakis came down the stairs with two coffees and a look.',
                '"You\'re still here," she said. It was not a question.',
                '"It\'s the shadow," he said, tapping the picture. "Look closer. It\'s pointing the wrong way."',
                'She looked. She did not want to look. She looked anyway, and the shadow WAS pointing the wrong way, '
                'and somewhere upstairs a filing cabinet slammed shut by itself.',
                'To be continued... (e-mail me if you want part 2!!)'])], n=(1, 1))], prob=0.5)],
    images=['alien.gif', 'ufo.gif', 'skull_spin.gif'], bullets=['bullet_alien.gif', 'bullet_skull.gif'],
    lines=['line_lightning.gif', 'line_stars.gif'],
    styles=['black_neon', 'starfield', 'goth', 'nebula', 'border_flames'],
    layouts=['single', 'sidebar', 'frames', 'splash'], midi=['spooky'],
    ring='murk', keywords='murk files holloway petrakis tv show episode guide consortium',
    desc=['Fan shrine to The Murk Files: episode guide, characters, theories', 'Holloway and Petrakis fan page',
          'Murk Files episode guide and fan fiction'],
    gb=['Holloway is SO cute. Thank you for this page.', 'NoRomo forever!!', 'Look closer... great site!',
        'Did you see last Friday\'s episode?! I can\'t sleep.']))

STARHOLD_CREW = ['<B>Captain Elena Okoro</B> - commanding officer of the ISS Meridian. Fair, fearless, terrible at poker.',
                 '<B>Commander Varek</B> - half-Tessarine first officer. Logical. Secretly loves jazz.',
                 '<B>Chief Engineer "Mags" Mahoney</B> - can fix a warp coil with a hairpin and a bad attitude.',
                 '<B>Dr. Ilsa Pell</B> - ship\'s doctor, collects alien houseplants.',
                 '<B>Ensign Tobias Reed</B> - the new kid. Always ends up on the away team. Always survives (somehow).',
                 '<B>Lieutenant Kaa\'ren</B> - Vorrangi defector at tactical. Do not touch her lunch.',
                 '<B>COMP</B> - the ship\'s computer, which is definitely developing a personality.']

T1.append(T('starhold', 'Area52', 'Nebula', 4, age=(14, 50),
    titles=['Starhold: Frontier - The Meridian Archives', 'Hold Fast! A Starhold Fan Site',
            '{handle}\'s Starhold Fan Fiction', 'The Unofficial ISS Meridian Technical Manual'],
    intro=['<I>"Space: it is bigger than you think, and it is not empty."</I> Welcome aboard! This site is all about '
           '<B>Starhold: Frontier</B>, the syndicated space series that follows the crew of the ISS Meridian on the '
           'far edge of charted space.',
           'Greetings, crewmate. This is my archive of Starhold fan fiction, technical specs and episode notes. '
           'Set phasers to "read"!'],
    sections=[
        S('list', ['The Crew', 'Bridge Crew Profiles'], STARHOLD_CREW, n=(4, 7)),
        S('table', ['ISS Meridian Specifications', 'Tech Specs'], [
            ('Class', 'Horizon-class long-range explorer'), ('Length', '412 meters'), ('Crew', '211 + 1 cat'),
            ('Top speed', 'Fold factor 8.6 (9.1 for "brief periods", says Mags)'), ('Armament', '6 pulse emitters, 2 '
             'torpedo bays'), ('Shuttles', '4 (the Daisy, the Pickle, the Oberon, the Spare)'),
            ('Commissioned', 'Stardate 2291.4'), ('Registry', 'NX-7700')], n=(5, 8)),
        S('story', ['Fan Fiction: Latest Story', 'My Fan Fic'], [
            ('Hold Fast, Part 1', [
                'Disclaimer: Starhold: Frontier belongs to its creators. No infringement intended, I am a poor student.',
                'The distress call came in at 0300 ship\'s time, which Captain Okoro would later point out was the '
                'only time distress calls ever seemed to come in.',
                '"It\'s Vorrangi," Kaa\'ren said, frowning at her console. "But it\'s using an old code. Very old. '
                'Older than me."',
                'Varek raised one eyebrow, which for him was the equivalent of shouting. "That code was retired '
                'before the Dominion signed the Accord."',
                'Okoro stood. "Then somebody out there doesn\'t know the war is over. Helm, take us in. Slowly."',
                'NEXT TIME: The ghost ship! Will Ensign Reed survive ANOTHER away mission?']),
            ('The Long Shift', [
                'Rated G. Takes place after the episode "Quiet Reactor".',
                'Mags Mahoney had not slept in thirty hours, and the warp coil had not stopped humming in E-flat, which '
                'was wrong, because it was supposed to hum in D.',
                '"COMP," she said, "are you humming?"',
                'There was a pause that lasted slightly too long for a computer. "No, Chief."',
                'She narrowed her eyes at the ceiling. "Uh huh."'])], n=(1, 1)),
        S('top10', ['Best Episodes', 'My Top Episodes'], [
            '"Quiet Reactor" - the ship talks. Or does it?', '"Okoro\'s Gambit" - poker night with a hostile armada.',
            '"The Tessarine Heart" - Varek goes home. Bring tissues.', '"Away Team Eleven" - Reed survives AGAIN.',
            '"Fold Zero" - the engine stops in the middle of nowhere.', '"Kaa\'ren\'s Lunch" - a comedy classic.',
            '"Mirrorfall" - evil twins, but done right.', '"Hold Fast" - the two-part season finale.'], n=(5, 8)),
        S('links', ['Other Starhold Sites', 'Fellow Crewmates'], n=(3, 6)),
    ],
    subpages=[SUB('chapter2.html', ['Fan Fiction Part 2'], [
        S('story', ['Hold Fast, Part 2'], [('Hold Fast, Part 2', [
            'The derelict hung in space like a broken promise. Its hull was older than any design in the database.',
            '"Life signs?" Okoro asked.', '"One," said Dr. Pell. "Faint. And... it\'s singing."',
            'Ensign Reed sighed and reached for an environment suit before anyone even asked.',
            'END OF PART 2. Part 3 coming soon - feedback makes me write faster!!!'])], n=(1, 1))], prob=0.7)],
    images=['ufo.gif', 'twinkle.gif'], bullets=['bullet_star.gif', 'ball_blue.gif'],
    lines=['line_stars.gif', 'line_laser.gif'], styles=['starfield', 'nebula', 'border_blue', 'pro_blue', 'hacker'],
    layouts=['single', 'sidebar', 'frames'], midi=['starfield', 'anthem'],
    ring='scifi', keywords='starhold frontier meridian fan fiction okoro varek space tv',
    desc=['Starhold: Frontier fan fiction and ship specs', 'ISS Meridian crew profiles and episode picks'],
    gb=['Hold fast! Loved part 1.', 'Varek is the best character on TV.', 'Write more about Mags please!!!']))

T1.append(T('galaxion', 'Area52', 'Nebula', 3, age=(12, 40),
    titles=['GALAXION Shrine', 'The Lumen Is Strong Here: A Galaxion Page', '{first}\'s Galaxion Trilogy Tribute'],
    intro=['Long ago, in a nebula far beyond our own... Welcome to my tribute to the <B>Galaxion</B> trilogy, the '
           'greatest movies ever made. Jax Corvane, Admiral Seren Vale and the wise old pilot Brannoc versus the '
           'evil Lord Malgrath and his Obsidian Fleet. And yes I have the action figures. All of them. Still in the box.',
           'May the Lumen guide you! This page has everything about Galaxion: characters, ships, my action figure '
           'collection, and a countdown to the NEW prequel coming out in May!!!'],
    sections=[
        S('list', ['Characters', 'Heroes & Villains'], [
            '<B>Jax Corvane</B> - farm boy from the moon of Teska who turns out to be the last Lumen Knight.',
            '<B>Admiral Seren Vale</B> - youngest admiral in the Alliance, best blaster shot in the galaxy.',
            '<B>Brannoc</B> - grumpy smuggler pilot with a heart of gold and a ship held together with tape.',
            '<B>Lord Malgrath</B> - masked villain, breathes VERY loudly, secretly Jax\'s uncle (SPOILER!!)',
            '<B>Pip-9</B> - nervous little repair droid who saves everybody in all three movies.',
            '<B>Old Maeve</B> - the hermit who teaches Jax to feel the Lumen.'], n=(4, 6)),
        S('table', ['Ships of the Galaxion Universe', 'Ship Stats'], [
            ('The Rusty Comet', 'Brannoc\'s freighter. Fastest junk in the nebula.'),
            ('Obsidian Dreadnought', 'Malgrath\'s flagship. 3 miles long. Has a weak spot (of course).'),
            ('Arrowhead Fighter', 'Alliance one-pilot fighter. Jax flies Red-7.'),
            ('Moonhopper', 'Jax\'s farm skiff. Top speed: not very.')], n=(3, 4)),
        S('para', ['The New Prequel!!!', 'Countdown to the Prequel'], [
            'The new Galaxion prequel comes out this May and I already have my ticket for the midnight show. I am '
            'going to camp out in line with my friends from the fan club. We are bringing glow sticks and lawn chairs. '
            'If the movie is bad I will still say it is good. That is loyalty.',
            'Rumor has it the prequel shows how young Malgrath fell to the shadow side. I heard there is a funny alien '
            'sidekick. I am a little worried about that.'], n=(1, 1)),
        S('photos', ['My Collection'], [('photo_band.gif', 'My action figures lined up on the shelf (lighting is bad)'),
                                         ('photo_computer.gif', 'Playing the Galaxion flight sim on my PC'),
                                         ('broken.gif', 'Picture of my Obsidian Dreadnought model coming soon')],
          n=(2, 3), prob=0.6),
        S('links', ['Other Galaxion Sites'], n=(3, 5)),
    ],
    images=['twinkle.gif', 'ufo.gif'], bullets=['bullet_star.gif'], lines=['line_laser.gif', 'line_stars.gif'],
    styles=['starfield', 'nebula', 'black_neon', 'border_blue'], layouts=['single', 'splash', 'sidebar'],
    midi=['anthem', 'starfield'], ring='scifi', keywords='galaxion movie trilogy jax corvane malgrath lumen prequel',
    desc=['Tribute to the Galaxion space movie trilogy', 'Galaxion characters, ships and action figures'],
    gb=['MAY THE LUMEN GUIDE YOU!!!!', 'I am camping out for the prequel too!', 'Malgrath rules.']))

T1.append(T('cryptid', 'Area52', 'Saucer', 4, age=(20, 70),
    titles=['Cryptozoology Corner', 'The {state} Bigfoot Research Page', 'Crop Circle Central', 'Strange {town}'],
    intro=['Not every mystery comes from the sky. Some of them walk on two legs through the woods at night, '
           'smelling terrible. Welcome to my research page.',
           'I have spent eleven summers in the backwoods of {state} with a camera, a tape recorder and a jar of '
           'peanut butter (bait). Here is what I have found.',
           'Crop circles appear every summer in the fields outside {town}. The farmers say it is kids. I measured '
           'them. Kids are not that precise.'],
    sections=[
        S('log', ['Field Notes', 'Expedition Log'], [
            'Found a footprint 17 inches long near the creek. Made a plaster cast. My wife is not happy about the '
            'plaster in the sink.',
            'Heard three loud knocks from the ridge. Knocked back with a stick. Something knocked back AGAIN.',
            'Peanut butter jar was gone in the morning. Lid was unscrewed, not broken. Raccoons cannot unscrew lids. '
            'Can they?',
            'New crop formation in the Hendricks field: seven circles, perfectly spaced, wheat bent but not broken.',
            'Strange smell, like wet dog and burnt pennies. Hair on my arms stood up. Went home early.',
            'Recorded a howl that does not match any animal on my tapes. Will post a WAV file when I figure out how.',
            'Found a tree with branches twisted into an X. Second one this month.',
        ], n=(4, 6)),
        S('list', ['Creatures I Am Researching', 'The Files'], [
            '<B>The Ridge Walker</B> - tall, hairy, shy. Most sightings near logging roads.',
            '<B>The Lake Lump</B> - something big in Lake Tamarack. Seen by fishermen since 1902.',
            '<B>The Mothwing</B> - giant winged shape near the old bridge. Red eyes.',
            '<B>The Swamp Glow</B> - floating lights that move against the wind.',
            '<B>The Corn Man</B> - figure seen standing in fields right before crop circles appear.'], n=(3, 5)),
        S('faq', ['FAQ', 'Questions People Ask Me'], [
            ('Are you serious?', 'Yes. Mostly. About 80 percent.'),
            ('Have you ever seen one?', 'I have seen SOMETHING. That is all I will say on the Internet.'),
            ('Can I come on an expedition?', 'E-mail me. Bring your own bug spray.'),
            ('Why the peanut butter?', 'Everybody likes peanut butter.')], n=(2, 4)),
        S('links', ['Other Researchers'], n=(3, 5)),
    ],
    images=['photo_mountain.gif', 'alien.gif', 'ufo.gif'], bullets=['bullet_paw.gif', 'ball_green.gif'],
    lines=['line_paws.gif', 'line_rope.gif'], styles=['camo', 'parchment', 'starfield', 'border_green', 'wood'],
    layouts=['single', 'sidebar'], midi=['spooky', None], ring='truth',
    keywords='bigfoot cryptozoology crop circles lake monster research',
    desc=['Bigfoot, lake monsters and crop circles in {state}', 'Field notes from a backwoods cryptid researcher'],
    gb=['I found a footprint too!', 'The Ridge Walker is real, my uncle saw it.', 'Crop circles are made by kids. '
        'Sorry. Nice page though.']))

T1.append(T('abduct', 'Area52', 'Hangar', 2, age=(30, 60),
    titles=['My Abduction Story', 'Missing Time: An Experiencer\'s Journal'],
    intro=['I have debated for two years whether to put this on the Internet. My family thinks I should not. But '
           'other people need to know they are not alone. This is my story.',
           'If you have ever woken up with your pajamas on inside out and a feeling that you were somewhere else, '
           'please read this page.'],
    sections=[
        S('para', ['The Night It Happened', 'What I Remember'], [
            'It was a Tuesday. I remember because the garbage truck comes on Wednesdays and I had just taken the cans '
            'out. There was a light in the backyard, brighter than the porch light, and a sound like a refrigerator '
            'humming but bigger.',
            'The next thing I remember is standing in the kitchen. The clock on the microwave said 4:12. I had gone '
            'outside at 11:30. My shoes were wet and there was a triangle of three little dots on my wrist.',
            'Under hypnosis I remembered a room with a curved ceiling and small figures with large dark eyes. They '
            'were not mean. They seemed... curious. Like I was a science project. I suppose I was.',
            'Since then I have had dreams about the room almost every month. In the dreams they show me pictures of '
            'oceans and forests. I do not know what they want me to understand.'], n=(3, 4)),
        S('list', ['Signs You May Be An Experiencer'], [
            'Missing time you cannot explain', 'Strange marks (often in groups of three)', 'Nosebleeds after vivid '
            'dreams', 'Fear of certain lights or sounds', 'Electronics acting up around you', 'A sense of being '
            'watched at night'], n=(4, 6)),
        S('para', ['Support'], ['If any of this sounds familiar, please e-mail me. I run a small support group that '
                                'meets in the chat room on Thursday nights. You are not crazy and you are not alone.'],
          n=(1, 1)),
        S('links', ['Helpful Pages'], n=(3, 5)),
    ],
    images=['alien.gif', 'ufo.gif'], bullets=['bullet_alien.gif'], lines=['line_stars.gif'],
    styles=['nebula', 'starfield', 'clouds', 'plain'], layouts=['single'], midi=['spooky', 'memorial'],
    ring='truth', keywords='abduction experiencer missing time aliens support',
    desc=['A personal abduction story and support page'],
    gb=['Thank you for sharing this. It happened to me too.', 'You are very brave.']))

# ------------------------------------------------------------------ SiliconHills
T1.append(T('rig', 'SiliconHills', 'Lab', 4, age=(15, 45), gender='m',
    titles=['{handle}\'s Rig Page', 'My Computer (Overclocked!!!)', 'The {last} Home Network', 'Welcome To My Lab'],
    intro=['This page is about my computer. Yes, a whole page. You would understand if you saw it. I built it myself '
           'from parts I bought at the computer show at the {town} fairgrounds.',
           'Some guys work on cars. I work on THIS. Specs, benchmarks and pictures of my overclocking adventures below.',
           'Welcome to the lab! Here you will find my rig specs, my LAN setup, and tips for squeezing every last '
           'megahertz out of your chip without burning down the house (mostly).'],
    sections=[
        S('table', ['My Rig', 'Current Specs', 'The Machine'], [
            ('CPU', 'Pentathlon II 300 @ 450MHz (!!!)'), ('CPU', 'Kestrel K6-2 350 (runs cool, rock solid)'),
            ('RAM', '128 MB PC100 SDRAM'), ('RAM', '64 MB EDO (upgrading soon)'),
            ('Video', 'Hoodoo2 12MB SLI (two cards!!)'), ('Video', 'Rage Against the Polygon 8MB AGP'),
            ('Sound', 'NoiseCannon AWE64'), ('Hard drive', '10.2 GB UltraDMA (filled up already)'),
            ('Modem', 'Hayseed 56K V.90 (connects at 44K on a good day)'), ('Monitor', '17" Trinitube'),
            ('OS', 'Panes 98 SE and Gnulix dual boot'), ('Case', 'Beige mid-tower with 5 fans and a window I cut myself'),
            ('Mouse', 'Ball mouse. I clean the rollers every Sunday.'), ('CD-ROM', '40x + CD burner (2x, takes forever)')],
          n=(6, 10)),
        S('log', ['Overclocking Diary', 'Lab Notes'], [
            'Bumped the front side bus to 100MHz. Booted! Ran Gibfest Arena for an hour, no crashes.',
            'Tried 112MHz. Blue screen. Smelled something. Backed off.',
            'Added a second fan with a hacked-up molex adapter. Temps down 6 degrees.',
            'Reinstalled Panes for the fourth time this month. I could do it in my sleep.',
            'Got the LAN working with my brother\'s computer. Two hours of frag time before Mom said dinner.',
            'Flashed the BIOS. Held my breath the whole time. Success!',
            'Upgraded to 128MB. Everything opens so fast now. I can have FOUR browser windows open.',
        ], n=(3, 6)),
        S('list', ['Tips', 'Overclocking Tips'], [
            'Always write down your old jumper settings first.', 'Thermal paste: a dab, not a glob.',
            'If it smells hot, it IS hot.', 'Ground yourself before touching anything. Trust me on this one.',
            'Defrag weekly. It is relaxing to watch the little blocks.',
            'Do not overclock the computer you need for your term paper.'], n=(3, 6)),
        S('links', ['Hardware Links', 'Other Rig Pages'], n=(3, 5)),
    ],
    subpages=[SUB('benchmarks.html', ['Benchmarks'], [
        S('table', ['Benchmark Results'], [('3D Frames Test', '58.2 fps'), ('PaneStone 99', '22.1'),
                                           ('Boot time', '41 seconds'), ('Gibfest timedemo', '64.0 fps'),
                                           ('Dhrystones', 'a lot')], n=(3, 5))], prob=0.6)],
    images=['photo_computer.gif', 'gear.gif', 'globe.gif'], bullets=['ball_green.gif', 'ball_blue.gif'],
    lines=['line_laser.gif', 'rainbow_hr.gif'], styles=['hacker', 'pro_blue', 'border_blue', 'concrete', 'plain'],
    layouts=['single', 'sidebar', 'frames'], midi=['techno', None], ring='geek',
    keywords='computer overclocking hardware specs pc build lan',
    desc=['Overclocked PC specs and benchmarks', 'Homebuilt computer and LAN setup'],
    gb=['Nice rig dude. My K6 does 400.', 'How did you cut the window in the case?', 'Two Hoodoo cards = sweet.']))

T1.append(T('gnulix', 'SiliconHills', 'Mainframe', 3, age=(16, 40), gender='m', handle='initials',
    titles=['~{handle} - Gnulix Stuff', '{handle}@localhost', 'Free Software and Me'],
    intro=['This page was written in vi. It contains no frames, no blinking text and no Java-ish applets. '
           'It is about Gnulix, the free operating system, and the scripts I wrote for it.',
           'Hi. I run Gnulix on everything I own, including a 486 I found at a garage sale that now routes my whole '
           'apartment. Below: config files, hacks and rants.'],
    sections=[
        S('list', ['Projects', 'Stuff I Wrote'], [
            '<TT>mailsort.pl</TT> - sorts my mail into 40 folders by angriness of subject line.',
            '<TT>modemwatch</TT> - redials when the ISP drops me (every 20 minutes).',
            '<TT>tinyhttpd</TT> - a web server in 400 lines of C. Do not run it on the Internet.',
            '<TT>fortune-y2k</TT> - fortune cookies about the end of the world.',
            '<TT>.emacs</TT>? No. I use vi. Next question.',
            '<TT>cdplay</TT> - plays CDs from the command line, ejects on error (on purpose).'], n=(3, 5)),
        S('para', ['Why Gnulix?', 'A Rant'], [
            'Because it does not crash. Because I can read the source. Because when it breaks, I can fix it, and '
            'when Panes breaks you have to call a phone number and wait for 40 minutes listening to smooth jazz.',
            'Compiling a kernel is the most relaxing thing you can do on a Friday night. Do not let anyone tell you '
            'otherwise.'], n=(1, 2)),
        S('table', ['Machines', 'My Boxes'], [('gromit', '486DX2/66, 16MB, router/firewall, uptime 214 days'),
                                              ('wallace', 'Pentathlon 200, 64MB, desktop'),
                                              ('feathers', 'old laptop, 8MB, runs a text editor and that is it'),
                                              ('hal', 'the fileserver, 3 drives held in with zip ties')], n=(2, 4)),
        S('quote', ['Quote of the Week'], ['"Real programmers count from zero."', '"RTFM, but nicely."',
                                           '"There is no place like 127.0.0.1"', '"It compiled. Ship it."'], n=(1, 1)),
        S('links', ['Links'], n=(3, 5)),
    ],
    images=[], bullets=[], lines=[], styles=['hacker', 'plain', 'concrete'], layouts=['single'],
    midi=[None], ring='geek', keywords='gnulix free software unix scripts programming',
    desc=['Gnulix hacks, scripts and rants', 'Free software projects and config files'],
    gb=['vi forever.', 'Nice no-frames page, very readable.', 'Your httpd crashed my browser. Respect.'],
    features={'nofancy': True}))

T1.append(T('aolrefugee', 'SiliconHills', 'Modem', 4, age=(25, 65),
    titles=['Free At Last! (An America OffLine Refugee)', '{first}\'s New Home On The Real Internet',
            'I Left America OffLine And Lived', 'Life After AOffL'],
    intro=['For three years I was on America OffLine. Three years of busy signals, three years of "You\'ve Got '
           'Junk!", three years of keyword this and keyword that. Then my nephew set me up with a real Internet '
           'Service Provider and now I have a REAL homepage with my OWN address. Welcome!',
           'This is my first homepage on the World Wide Web. I used to only go to the chat rooms on America OffLine '
           'but my granddaughter showed me that there is a whole Internet out there. Who knew!'],
    sections=[
        S('list', ['Things I Do Not Miss', 'Why I Left'], [
            'Busy signals every night from 7 to 11.', 'The CDs. So many CDs. I built a wind chime out of them.',
            'Paying by the hour (I once had a $211 bill. True story.)', 'Getting kicked off in the middle of a chat.',
            'People asking "A/S/L?" every 5 minutes.', 'The little man running when it connects. Actually I miss him a bit.'],
          n=(3, 6)),
        S('para', ['What I Like About The Real Internet'], [
            'You can go ANYWHERE. Last night I read about the history of buttons for two hours. Buttons! There is a '
            'whole page about buttons.',
            'I have my own e-mail address now and I have been sending forwards to everyone I know. Some of them have '
            'asked me to stop. I will not stop.',
            'My homepage! I made it myself with the Build-a-Page and it only took me four evenings.'], n=(2, 3)),
        S('photos', ['My Old Setup'], [('photo_computer.gif', 'The computer my nephew gave me. 133 megahertz!'),
                                       ('photo_family.gif', 'My grandkids, who are smarter than me'),
                                       ('photo_cat.gif', 'Mittens, who sleeps on the monitor because it is warm')],
          n=(2, 3)),
        S('links', ['My Favorite Places On The Web', 'Good Links'], n=(4, 6)),
    ],
    images=['mail_fly.gif', 'globe.gif', 'email.gif'], bullets=['ball_red.gif', 'ball_yellow.gif'],
    lines=['rainbow_hr.gif', 'rainbow_line.gif'], styles=['clouds', 'retro_tan', 'plain', 'marble', 'default_gray'],
    layouts=['single'], midi=['elevator', 'ragtime', None], ring='newbie',
    keywords='america offline refugee new internet user first homepage',
    desc=['Escaped from America OffLine to the real Internet', 'An online-service refugee\'s first real homepage'],
    gb=['Welcome to the real Internet!', 'I left too! Best decision ever.', 'I still have 40 of those CDs.']))

T1.append(T('bbs', 'SiliconHills', 'Modem', 2, age=(22, 45), gender='m',
    titles=['The Electric Basement BBS (1987-1996) Memorial', 'Remember BBSes?'],
    intro=['Before the Web there were bulletin board systems. You dialed a phone number, your modem screamed, and if '
           'nobody else was on, you got in. I ran <B>The Electric Basement</B> out of my parents\' basement for nine '
           'years on two phone lines. This page remembers it.'],
    sections=[
        S('table', ['BBS Stats', 'By The Numbers'], [('Years online', '9'), ('Users', '1,412'), ('Phone lines', '2'),
                                                    ('Door games', '14'), ('Messages posted', '88,000-ish'),
                                                    ('Times my dad picked up the phone mid-download', 'countless')],
          n=(4, 6)),
        S('list', ['Door Games We Had', 'Remember These?'], [
            'Legend of the Red Ogre', 'Trade Lanes 3000', 'Barren Galaxy Conquest', 'Dungeon of a Thousand Doors',
            'Ye Olde Tavern', 'Global Thermonuclear Checkers'], n=(3, 6)),
        S('para', ['Why I Shut It Down'], [
            'Everybody went to the Web. The last month I had three callers, and two of them were me testing the line. '
            'I unplugged the modem on New Year\'s Eve 1996 and had a little cry. Then I built this page.'], n=(1, 1)),
        S('links', ['Links'], n=(3, 5)),
    ],
    images=['photo_computer.gif'], bullets=['ball_green.gif'], lines=['line_laser.gif'],
    styles=['hacker', 'default_gray', 'black_neon'], layouts=['single'], midi=['chiptune', None], ring='geek',
    keywords='bbs bulletin board door games ansi modem nostalgia',
    desc=['Memorial for a 1980s-90s BBS', 'Bulletin board nostalgia and door games'],
    gb=['I called your board in 1991! Handle: RAZORBACK.', 'Legend of the Red Ogre forever.']))

T1.append(T('htmltut', 'SiliconHills', 'Pixel', 4, age=(14, 50),
    titles=['{first}\'s HTML Help Center', 'HTML Made EZ', 'Learn HTML In 10 Minutes', 'Webmaster Tips & Tricks'],
    intro=['Want to make your own homepage? It is easier than you think! I learned HTML in one weekend and now I '
           'make pages for my whole family. Here are my lessons, free for everybody.',
           'Welcome to my HTML tutorial! No experience needed. All you need is Notepad and a dream.'],
    sections=[
        S('table', ['Lesson 1: Tags You Need', 'Basic Tags'], [
            ('&lt;HTML&gt;', 'Starts the page. Do not forget it!'), ('&lt;BODY BGCOLOR="..."&gt;', 'Sets your '
             'background color'), ('&lt;FONT FACE="Comic Sans MS"&gt;', 'Changes the font (Comic Sans is the BEST)'),
            ('&lt;CENTER&gt;', 'Centers everything. Use it a lot.'), ('&lt;IMG SRC="..."&gt;', 'Puts in a picture'),
            ('&lt;A HREF="..."&gt;', 'Makes a link'), ('&lt;MARQUEE&gt;', 'Makes text scroll. Fancy!'),
            ('&lt;BLINK&gt;', 'Makes text blink. Use with care.'), ('&lt;TABLE&gt;', 'Puts things in boxes'),
            ('&lt;HR&gt;', 'A line across the page')], n=(6, 10)),
        S('list', ['Do\'s and Don\'ts', 'Webmaster Tips'], [
            'DO put a counter on your page so you know people visited.', 'DON\'T put 40 animated GIFs on one page. '
            'Thirty is plenty.', 'DO give your pictures WIDTH and HEIGHT so the page loads faster.',
            'DON\'T use light yellow text on a white background.', 'DO update your page so people come back.',
            'DON\'T steal bandwidth by linking to other people\'s images!', 'DO sign other people\'s guestbooks.',
            'DON\'T make your MIDI play 10 songs at once.', 'DO test your page in both Pioneer Navigator and '
            'Internet Explor-o-Matic.'], n=(4, 7)),
        S('faq', ['Questions', 'Help!'], [
            ('My picture does not show up!', 'Check the file name. Capital letters count on some servers!'),
            ('How do I make my text move?', 'Use the &lt;MARQUEE&gt; tag. Only works in some browsers.'),
            ('What is a frame?', 'It splits your page into windows. It is very advanced.'),
            ('How do I get my page on a search engine?', 'Submit it to every search engine. Then wait. And wait.'),
            ('Why does my page look different on my friend\'s computer?', 'Nobody knows. It is the great mystery of the '
             'Web.')], n=(3, 5)),
        S('links', ['Other Helpful Sites'], n=(3, 5)),
    ],
    subpages=[SUB('lesson2.html', ['Lesson 2: Tables'], [
        S('para', ['Tables'], ['Tables are the secret of every good-looking page. Put your whole page in a table with '
                               'WIDTH=600 and it will look the same on every monitor (almost).',
                               'Use CELLPADDING to give your text room to breathe, and BORDER=0 to hide the lines. '
                               'Then nobody will know you used a table!'], n=(2, 2))], prob=0.7)],
    images=['notepad.gif', 'construction.gif'], bullets=['ball_blue.gif', 'ball_red.gif'],
    lines=['rainbow_hr.gif', 'line_laser.gif'], styles=['pro_blue', 'border_blue', 'notebook', 'plain', 'retro_tan'],
    layouts=['sidebar', 'single', 'frames'], midi=[None, 'elevator'], ring='webdesign',
    keywords='html tutorial webmaster tips tags beginner',
    desc=['Beginner HTML lessons and webmaster tips', 'Free HTML tutorial, no experience needed'],
    gb=['Your tutorial helped me make my page!!!', 'Thanks for the marquee tip.', 'Lesson 3 please!']))

T1.append(T('freegfx', 'SiliconHills', 'Pixel', 3, age=(13, 40),
    titles=['{handle}\'s FREE Graphics', 'Free GIFs! Free Backgrounds!', 'The Graphics Garage'],
    intro=['All the graphics on this page are FREE for you to use on your homepage! All I ask is that you link back '
           'to me and DON\'T hotlink (save them to your own space!).',
           'Welcome to my graphics collection. I made all of these myself in Pixel Shop Pro. Right-click and Save '
           'As. Please give credit!'],
    sections=[
        S('gallery', ['Animated GIFs', 'Animations'], ['flames.gif', 'skull_spin.gif', 'mail_fly.gif', 'dancing_baby.gif',
                                                       'ufo.gif', 'heart.gif', 'cd_spin.gif', 'hot.gif', 'kitten.gif',
                                                       'twinkle.gif', 'notes.gif', 'football.gif', 'gear.gif'],
          n=(6, 10)),
        S('gallery', ['Lines & Dividers', 'Bars'], ['rainbow_line.gif', 'line_hearts.gif', 'line_stars.gif',
                                                   'line_barbed.gif', 'line_lightning.gif', 'line_paws.gif',
                                                   'line_notes.gif', 'line_rope.gif', 'line_slime.gif', 'line_bows.gif'],
          n=(4, 7)),
        S('gallery', ['Buttons & Bullets'], ['ball_red.gif', 'ball_green.gif', 'ball_blue.gif', 'ball_yellow.gif',
                                             'ball_purple.gif', 'bullet_star.gif', 'bullet_heart.gif',
                                             'bullet_skull.gif', 'btn_home.gif', 'btn_next.gif', 'btn_back.gif'],
          n=(5, 9)),
        S('list', ['Rules', 'Terms of Use'], ['Link back to me with my button.', 'No hotlinking!!!',
                                              'Do not claim you made them.', 'Do not put them on hate pages.',
                                              'Have fun!'], n=(3, 5)),
        S('links', ['Other Graphics Sites'], n=(3, 5)),
    ],
    images=['construction.gif'], bullets=['ball_purple.gif', 'bullet_star.gif'],
    lines=['rainbow_line.gif', 'line_stars.gif'], styles=['black_neon', 'glitter', 'border_purple', 'starfield'],
    layouts=['single', 'sidebar'], midi=['techno', None], ring='webdesign',
    keywords='free graphics gifs backgrounds animations buttons clip art',
    desc=['Free animated GIFs, lines and buttons', 'Free graphics collection for your homepage'],
    gb=['I used your flames on my page! Linked you back.', 'Awesome GIFs!!!']))

# ------------------------------------------------------------------ Tinseltown
T1.append(T('glacier', 'Tinseltown', 'Marquee', 3, age=(13, 35), gender='f',
    titles=['THE GLACIER - My Heart Will Float On', 'Finn & Rosalind 4-Ever', 'The Glacier Shrine'],
    intro=['I have seen <B>The Glacier</B> in the theater ELEVEN times. The story of the luxury airship Majestica '
           'and the iceberg-covered mountain that brought it down is the most beautiful love story ever told. Finn '
           'and Rosalind forever!!!',
           'This page is dedicated to the greatest movie of all time. If you did not cry at the end, you have no '
           'heart. Sorry but it is true.'],
    sections=[
        S('para', ['The Story', 'Plot'], [
            'In 1912, the luxury airship Majestica sets off across the Arctic. Rosalind is a rich girl engaged to a '
            'mean man named Cal-something. Finn is a poor artist who won his ticket in a card game. They fall in '
            'love on the observation deck. Then the airship hits a glacier. I will not tell you the ending. (It is sad.)',
            'The special effects are amazing, especially when the airship tips over and everybody slides down the '
            'ballroom. And the music! I have the soundtrack and I play it every night.'], n=(1, 2)),
        S('top10', ['Best Scenes', 'Scenes That Made Me Cry'], [
            '"I\'m flying!" on the front of the gondola.', 'The drawing scene. *blush*',
            'The old couple holding hands in their cabin.', 'The band playing as the ship goes down.',
            '"Never let go, Rosalind."', 'The ending. I can\'t even talk about it.', 'When Finn wins the ticket.',
            'The dance party below decks with the fiddle.'], n=(4, 8)),
        S('list', ['Finn Facts', 'Did You Know?'], [
            'The actor who plays Finn, Brock Delaney, is 24 years old and his favorite food is spaghetti.',
            'They built a real airship for the movie. Well, half of one.', 'It is three hours and fourteen minutes long '
            'and it goes by in a FLASH.', 'The glacier was made of 400 tons of styrofoam.',
            'The necklace is called the Heart of the North.'], n=(3, 5)),
        S('links', ['Other Glacier Pages'], n=(3, 5)),
    ],
    images=['heart.gif', 'twinkle.gif'], bullets=['bullet_heart.gif'], lines=['line_hearts.gif', 'line_bows.gif'],
    styles=['pastel_hearts', 'glitter', 'water', 'clouds', 'snow'], layouts=['single', 'splash'],
    midi=['heartthrob', 'lovesong'], ring='brock', keywords='glacier movie finn rosalind brock delaney majestica',
    desc=['Shrine to the movie The Glacier', 'Finn and Rosalind fan page'],
    gb=['I saw it 14 times!!!!', 'Brock is a HOTTIE', 'Never let go!!!']))

T1.append(T('tvfan', 'Tinseltown', 'Couch', 5, age=(13, 45),
    titles=['{show} Fan Page', 'The Unofficial {show} Site', '{first}\'s {show} Episode Guide', '{show} Central',
            'All About {show}'],
    entities=[
        dict(show='Maple Cove', blurb='the teen drama about four friends in a small seaside town who talk in really '
             'long words about their feelings', chars=['Tessa', 'Cole', 'Ryder', 'Brianna', 'Mr. Haverford'],
             night='Wednesdays'),
        dict(show='Apartment 4B', blurb='the funniest sitcom on TV about six friends who live in (and mostly hang '
             'around) the same apartment building', chars=['Lenny', 'Carla', 'Marty', 'Jo', 'Dev', 'Priya'],
             night='Thursdays'),
        dict(show='Vera the Vampire Wrangler', blurb='the show about a high school sophomore who secretly herds '
             'vampires back to where they belong with a lasso made of garlic', chars=['Vera', 'Oscar',
                                                                                     'Mr. Gilbert', 'Willa',
                                                                                     'Xavier'],
             night='Tuesdays'),
        dict(show='The Cul-de-Sac', blurb='the cartoon about a very sarcastic family that lives at the end of a '
             'dead-end street', chars=['Dad', 'Mom', 'Bartholomew', 'Lisette', 'the baby'], night='Sundays'),
        dict(show='Paramedic Heart', blurb='the hospital drama where everyone is either in surgery or in love, '
             'usually both', chars=['Dr. Ross Calloway', 'Nurse Hannah', 'Dr. Benji Okafor', 'Dr. Lou Lindqvist'],
             night='Thursdays at 10')],
    intro=['Welcome to my page about <B>{show}</B>, {blurb}! It is on {night} and I never miss it. My VCR is set to '
           'record every episode in case I am at softball.',
           'If you love <B>{show}</B> as much as I do, you are in the right place. Here you will find character '
           'bios, my episode guide and lots of other stuff. Enjoy!'],
    sections=[
        S('list', ['Characters', 'Meet The Cast (the characters, not the actors)'], [
            '<B>{c1}</B> - my favorite. Always says the right thing at the wrong time.',
            '<B>{c2}</B> - kind of annoying but you can\'t help loving them.',
            '<B>{c3}</B> - the funny one. Gets all the best lines.',
            '<B>{c4}</B> - mysterious. What is their deal??',
            '<B>{c5}</B> - only in a few episodes but SO important.'], n=(3, 5)),
        S('log', ['Episode Guide', 'Recent Episodes'], [
            '{c1} and {c2} have a big fight about a borrowed sweater. I think it was really about something else.',
            '{c3} gets a job at the diner and immediately sets the kitchen on fire. Classic.',
            'The Halloween episode! Everybody dresses up as each other. {c4} as {c1} was hilarious.',
            'A sad one. {c2}\'s grandpa is sick. I cried and so did my dad (he says he didn\'t).',
            'Season finale!!! {c1} finally says IT. Then the screen goes black. I have to wait all SUMMER.',
            '{c5} comes back from the summer and is totally different. New hair, new attitude.',
            'The one where the power goes out and they all tell scary stories.'], n=(3, 6)),
        S('poll', ['Poll: Who Is Your Favorite?', 'Vote!'], ['{c1}', '{c2}', '{c3}', '{c4}'], n=(1, 1), prob=0.6),
        S('links', ['Other {show} Pages', 'More Fan Sites'], n=(3, 5)),
    ],
    images=['photo_band.gif', 'heart.gif', 'new.gif'], bullets=['ball_pink.gif', 'bullet_star.gif', 'ball_blue.gif'],
    lines=['rainbow_line.gif', 'line_stars.gif', 'line_hearts.gif'],
    styles=['pastel_flowers', 'black_neon', 'border_purple', 'clouds', 'marble', 'glitter', 'denim'],
    layouts=['single', 'sidebar', 'frames'], midi=['heartthrob', 'elevator', None], ring='couch',
    keywords='tv show fan page episode guide characters {show}',
    desc=['Fan page for {show}: characters and episodes', '{show} episode guide and character bios'],
    gb=['I love {show}!!!', '{c1} is the best!', 'Did you see last week???']))

T1.append(T('reviews', 'Tinseltown', 'Marquee', 3, age=(20, 55),
    titles=['{first}\'s Movie Reviews', 'Two Thumbs and a Mouse: Movie Reviews', 'The Popcorn Report'],
    intro=['I see every movie that comes to the {town} Cineplex 8 (all eight screens!) and I review them here, '
           'honestly. My rating system: 1 to 5 tubs of popcorn.',
           'Movie reviews from a regular person who pays for a ticket like you do. No fancy critics here.'],
    sections=[
        S('table', ['Recent Reviews', 'Now Playing'], [
            ('Star Feuds Episode I: The Phantom Tariff', '3 tubs. Lots of trade negotiations. Great pod race.'),
            ('The Glacier', '5 tubs. I cried and so did the guy next to me.'),
            ('Asteroid Day', '2 tubs. Somebody blows up an asteroid. Again.'),
            ('The Matrimony', '4 tubs. Is reality real? Is this wedding real? Woah.'),
            ('Tiny Toy Tale 2', '5 tubs. The cowboy doll is back!'),
            ('Shark Feelings', '2 tubs. A shark goes to therapy. Weird but sweet.'),
            ('The Swamp Witch Tapes', '4 tubs. I had to sleep with the lights on.'),
            ('Big Ape in the Big City', '3 tubs. He climbs the building. We all knew he would.'),
            ('Agent of Mystery 3', '3 tubs. Same plot, new gadgets.'),
            ('My Cousin the Mummy', '1 tub. I left halfway through to get nachos and did not go back.')], n=(5, 8)),
        S('top10', ['My All-Time Top 10'], [
            'The Glacier', 'Galaxion IV', 'Tiny Toy Tale', 'The Matrimony', 'Moonlight Over Marrakesh (old but good)',
            'The Lost Idol of Quetzal', 'Back to Last Tuesday', 'The Wizard of Ozark', 'Lake Teeth',
            'A Very Long Musical'], n=(5, 10)),
        S('links', ['Other Movie Sites'], n=(3, 5)),
    ],
    images=['photo_band.gif', 'cool_face.gif'], bullets=['bullet_star.gif', 'ball_red.gif'],
    lines=['line_stars.gif', 'rainbow_hr.gif'], styles=['black_neon', 'border_flames', 'pro_blue', 'marble'],
    layouts=['single', 'sidebar'], midi=[None, 'anthem'], ring='couch', keywords='movie reviews ratings popcorn',
    desc=['Honest movie reviews rated in popcorn tubs', 'Movie reviews from a regular moviegoer'],
    gb=['You were too nice to Asteroid Day.', 'Phantom Tariff deserved 4 tubs!']))

T1.append(T('homemovies', 'Tinseltown', 'Backlot', 2, age=(14, 30), gender='m',
    titles=['{last} Brothers Productions', '{handle} Films'],
    intro=['We make movies in my backyard with my dad\'s camcorder. So far we have made 7 movies, including one with '
           'a real explosion (a firecracker in a model car). This is our studio website.'],
    sections=[
        S('table', ['Our Movies', 'Filmography'], [
            ('Attack of the Lawn Gnomes (1997)', '12 minutes. The gnomes win.'),
            ('Ninja Mailman (1998)', '8 minutes. He delivers. Justice.'),
            ('Space Raiders from Planet Garage (1998)', '22 minutes. Our epic. Took all summer.'),
            ('The Babysitter Is A Robot (1999)', 'In editing. Our sister plays the robot.'),
            ('The Swamp Witch Backyard Tapes (1999)', 'Shaky cam, so it is supposed to look like that.')], n=(3, 5)),
        S('list', ['Special Effects Secrets'], ['Ketchup = blood', 'Flour = smoke (do not breathe it)',
                                                'Fishing line = flying', 'Cardboard + tinfoil = spaceship',
                                                'Turning the camera upside down = walking on the ceiling'], n=(3, 5)),
        S('links', ['Links'], n=(2, 4)),
    ],
    images=['photo_band.gif', 'hot.gif'], bullets=['ball_red.gif'], lines=['flames.gif', 'line_laser.gif'],
    styles=['black_neon', 'border_flames', 'checker'], layouts=['single'], midi=['surf', 'punk'], ring='couch',
    keywords='home movies camcorder special effects backyard films',
    desc=['Backyard camcorder movies and special effects'], gb=['Ninja Mailman is a masterpiece.']))

T1.append(T('heartthrob', 'Tinseltown', 'Premiere', 4, age=(12, 19), gender='f',
    titles=['BROCK DELANEY IS A GOD', 'The Ultimate {star} Shrine', '{star} Lovers Unite!!!', '{handle}\'s {star} Page'],
    entities=[dict(star='Brock Delaney', movie='The Glacier'), dict(star='Tad Kingsley', movie='Maple Cove'),
              dict(star='Dex Romero', movie='Surf Patrol'), dict(star='Juliet Marchetti', movie='The Matrimony')],
    intro=['OMG welcome to my shrine to <B>{star}</B>!!!!! {star} is the most talented, most beautiful person in '
           'the whole world and if you don\'t agree you can leave right now. JK. But really.',
           'This page is 100% dedicated to {star}, star of <I>{movie}</I>. I have 47 posters and my mom says that is '
           'enough but she is WRONG.'],
    sections=[
        S('table', ['{star} Fact File', 'Fast Facts'], [
            ('Birthday', 'March 14'), ('Sign', 'Pisces (sensitive!!)'), ('Height', '5\' 11"'),
            ('Eyes', 'Blue like the ocean'), ('Fave food', 'Pizza with pineapple'), ('Fave color', 'Green'),
            ('Pets', 'A dog named Moose'), ('Movies', '{movie}, and a commercial for soup when they were 9')],
          n=(5, 8)),
        S('list', ['Reasons I Love {star}', 'Why {star} Rules'], [
            'That smile!!!!', 'Is nice to fans (I read it in a magazine)', 'Can sing AND act', 'Loves animals',
            'Did not get a big head after {movie}', 'The hair. Just the hair.', 'Once waved at my cousin at a mall'],
          n=(4, 7)),
        S('para', ['My Dream'], ['My dream is to meet {star} someday. I would just say hi and maybe ask for an '
                                 'autograph and then I would probably faint. I already wrote a letter to the fan club '
                                 'and I am waiting for my signed picture (it has been 9 weeks).'], n=(1, 1)),
        S('links', ['Other {star} Shrines'], n=(3, 5)),
    ],
    images=['heart.gif', 'twinkle.gif', 'photo_me.gif'], bullets=['bullet_heart.gif', 'ball_pink.gif'],
    lines=['line_hearts.gif', 'rainbow_line.gif', 'line_bows.gif'], styles=['glitter', 'pastel_hearts',
                                                                         'border_pink', 'black_neon'],
    layouts=['single', 'splash'], midi=['heartthrob', 'lovesong'], ring='brock',
    keywords='{star} shrine fan page heartthrob actor', desc=['Ultimate shrine to {star}', '{star} fan page'],
    gb=['{star} is MINE. Just kidding. Cool page.', 'OMG I love {star} too!!!!', 'Can we trade pictures?']))

# ------------------------------------------------------------------ Gridiron
T1.append(T('fantasy', 'Gridiron', 'Bleachers', 3, age=(22, 50), gender='m',
    titles=['The {league} Fantasy League', '{league} - Official Site', '{handle}\'s Fantasy Football HQ'],
    entities=[dict(league='Beer Belly Bowl'), dict(league='Couch Commissioner League'),
              dict(league='Office Pool of Doom')],
    intro=['Welcome to the official home of the <B>{league}</B>, now in its 6th glorious season. 10 teams, 1 trophy '
           '(a bowling trophy we spray-painted gold), and 0 mercy.',
           'This is the website for our fantasy football league. Check the standings, read the trash talk, and pay '
           'your dues, Gary.'],
    sections=[
        S('table', ['Standings', 'Week 9 Standings'], [
            ('The Gridiron Gangsters', '7-1'), ('Toledo Tailgaters', '6-2'), ('Gary\'s Team (pay your dues)', '5-3'),
            ('The Couch Potatoes', '4-4'), ('Blitzkrieg Bop', '4-4'), ('Mama\'s Boys', '3-5'),
            ('The Fumble Bees', '3-5'), ('Injured Reserve', '2-6'), ('Commissioner\'s Pets', '2-6'),
            ('The Bye Week', '1-7')], n=(6, 10)),
        S('log', ['Trash Talk', 'Commissioner\'s Notes'], [
            'Gangsters win again. Somebody stop this man.', 'Gary still has not paid. Gary. GARY.',
            'Trade of the year: two backups and a kicker for a star running back. Collusion? The commish says no.',
            'Bye Week lost by 61 points. A league record. Congratulations?',
            'Draft night was a success. 4 pizzas, 2 arguments, 1 broken lamp.',
            'Rule change: no more drafting players who retired in 1994.'], n=(3, 5)),
        S('list', ['League Rules'], ['Draft is in August at Dave\'s house.', 'Dues are $20. Due at the draft. '
                                     'Looking at you Gary.', 'Trades must be approved by the commish.',
                                     'Last place has to wear the Hat of Shame to the playoffs.'], n=(3, 4)),
        S('links', ['Links'], n=(2, 4)),
    ],
    images=['football.gif', 'award_coolweek.gif'], bullets=['ball_green.gif', 'ball_red.gif'],
    lines=['rainbow_hr.gif', 'line_rope.gif'], styles=['grass', 'pro_blue', 'checker', 'border_green'],
    layouts=['single', 'sidebar'], midi=['fight_song', None], ring='sports',
    keywords='fantasy football league standings trash talk', desc=['Fantasy football league standings and trash talk'],
    gb=['Gangsters 4 life', 'I PAID. Stop putting it on the website. -Gary']))

T1.append(T('teamfan', 'Gridiron', 'Bleachers', 3, age=(16, 60),
    titles=['{team} Fan Page', 'GO {team}!!!', 'The {team} Nation'],
    entities=[dict(team='Ohio Ironmen', sport='football', mascot='Iron Mike', stadium='Ironworks Field'),
              dict(team='Tacoma Tidal', sport='baseball', mascot='Sammy the Seal', stadium='Harbor Park'),
              dict(team='Kansas City Comets', sport='hockey', mascot='Cosmo', stadium='the Comet Dome')],
    intro=['This page is for true fans of the <B>{team}</B>! Win or lose (mostly lose lately) I have had season '
           'tickets at {stadium} for 12 years. Here is everything you need to know.',
           'GO {team} GO!!! The best {sport} team in the world, no matter what the scoreboard says.'],
    sections=[
        S('table', ['Schedule', 'Upcoming Games'], [('Sept 12', 'vs. Portland Pioneers'), ('Sept 19', '@ Denver '
                                                    'Dynamos'), ('Sept 26', 'vs. Memphis Muskrats'),
                                                   ('Oct 3', '@ Boston Bulldogs'), ('Oct 10', 'vs. Fresno Firebirds'),
                                                   ('Oct 17', 'BYE (I will be sad)')], n=(4, 6)),
        S('list', ['Why We Are Going All The Way This Year'], ['New coach!', 'Healthy roster (for now)', 'The fans!',
                                                              '{mascot} has never looked better',
                                                              'The other teams are not that good either'], n=(3, 5)),
        S('photos', ['Game Day Photos'], [('photo_family.gif', 'Me and my kids at {stadium}'),
                                          ('photo_food.gif', 'Tailgate chili. The real MVP.'),
                                          ('photo_car.gif', 'My truck painted in team colors')], n=(2, 3)),
        S('links', ['Other Fan Sites'], n=(2, 4)),
    ],
    images=['football.gif', 'fire.gif'], bullets=['ball_red.gif', 'ball_blue.gif'],
    lines=['rainbow_hr.gif', 'flames.gif'], styles=['grass', 'denim', 'checker', 'border_green'],
    layouts=['single', 'frames'], midi=['fight_song'], ring='sports', keywords='{team} {sport} fans schedule',
    desc=['{team} fan page: schedule and game-day photos'], gb=['GO {team}!!!', 'See you at {stadium}!']))

T1.append(T('littleleague', 'Gridiron', 'Dugout', 3, age=(30, 50),
    titles=['{town} {team} Little League', 'Go {team}! (Little League Team Page)', 'The {team} - 10U Softball'],
    entities=[dict(team='Hornets'), dict(team='Mud Hens'), dict(team='Rockets'), dict(team='Pirates')],
    intro=['Welcome to the home page of the <B>{town} {team}</B>! I am the coach (and the snack schedule organizer, '
           'and the guy who lines the field). Check here for practice times and rain-outs.',
           'Hi parents and players! This is the official {team} website. Please read the snack schedule.'],
    sections=[
        S('table', ['Roster', 'Our Team'], [('#2', 'Tyler - shortstop'), ('#4', 'Ashley - pitcher'),
                                            ('#7', 'Marcus - catcher'), ('#9', 'Kaylee - 1st base'),
                                            ('#11', 'Jordan - outfield (and dandelion picker)'), ('#12', 'Bobby - 2nd '
                                                                                                 'base'),
                                            ('#15', 'Sam - outfield'), ('#21', 'Brianna - 3rd base'),
                                            ('#33', 'Kevin - pitcher/outfield')], n=(7, 9)),
        S('table', ['Snack Schedule'], [('Game 1', 'The Millers (orange slices please)'), ('Game 2', 'The Ruizes'),
                                        ('Game 3', 'The Hendersons'), ('Game 4', 'The Kowalskis (juice boxes!)'),
                                        ('Game 5', 'The Phams')], n=(4, 5)),
        S('log', ['Game Recaps'], ['Won 12-11 in extra innings! Jordan caught a fly ball (while looking at a '
                                   'butterfly).', 'Lost 8-3 but we had fun. Pizza party anyway.',
                                   'Rained out. Rescheduled for Thursday.', 'Ashley pitched 3 strikeouts in a row!!!',
                                   'Tied 6-6, called for darkness.'], n=(3, 5)),
        S('links', ['Links'], n=(2, 3)),
    ],
    images=['award_coolweek.gif', 'photo_family.gif'], bullets=['ball_red.gif', 'bullet_star.gif'],
    lines=['rainbow_hr.gif', 'line_stars.gif'], styles=['grass', 'clouds', 'plain', 'retro_tan'],
    layouts=['single'], midi=['fight_song', None], ring='sports',
    keywords='little league softball baseball team roster snack schedule',
    desc=['Little League team page with roster and snack schedule'], gb=['Go {team}!!! -Kaylee\'s mom']))

T1.append(T('stockcar', 'Gridiron', 'Pitstop', 3, age=(20, 60),
    titles=['#{carnum} {driver} Fan Page', 'Thunder Cup Racing Central', '{handle}\'s Racing Page'],
    entities=[dict(driver='Jimmy Ray Tolliver', carnum='44'), dict(driver='Bobby Lee Dupree', carnum='17'),
              dict(driver='Darlene "Lead Foot" Pruitt', carnum='8')],
    intro=['Gentlemen (and ladies), start your engines! This page is for fans of the <B>Thunder Cup Series</B> and '
           'especially the #{carnum} car driven by the one and only {driver}.',
           'I have been a race fan since I was knee-high. Every Sunday you will find me in front of the TV or in the '
           'stands at Cottonmouth Speedway with a cooler and a scanner.'],
    sections=[
        S('table', ['1999 Season Results', 'Results So Far'], [('Big Pine 500', '3rd'), ('Cottonmouth 400', '1st!!!'),
                                                             ('Mud Flat 250', '22nd (wreck, not his fault)'),
                                                             ('Delta Dash', '5th'), ('Thunder Valley 300', '2nd'),
                                                             ('Peach State 500', '11th'), ('Lakeshore 400', '4th')],
          n=(4, 7)),
        S('list', ['Why #{carnum} Is The Best'], ['Never gives up', 'Best pit crew in the series (14 second stops)',
                                                  'Signs every autograph', 'Drives like the wind', 'Cool paint job'],
          n=(3, 5)),
        S('photos', ['Race Day'], [('photo_car.gif', 'Close as I got to the #{carnum} car'),
                                   ('photo_food.gif', 'Infield cookout')], n=(1, 2)),
        S('links', ['Racing Links'], n=(2, 4)),
    ],
    images=['photo_car.gif', 'fire.gif', 'flames.gif'], bullets=['ball_red.gif', 'bullet_star.gif'],
    lines=['flames.gif', 'line_rope.gif'], styles=['checker', 'border_flames', 'denim', 'concrete'],
    layouts=['single', 'sidebar'], midi=['hoedown', 'surf'], ring='sports',
    keywords='stock car racing thunder cup {driver} speedway', desc=['Stock car racing fan page for #{carnum}'],
    gb=['#{carnum} all the way!!!', 'See ya at Cottonmouth!']))

T1.append(T('outdoors', 'Gridiron', 'Tackle', 3, age=(30, 70), gender='m',
    titles=['{first}\'s Fishing Hole', 'Big Bass Bragging Page', 'Gone Fishin\''],
    intro=['If you are reading this, I am probably fishing. This page has my best catches, my favorite lakes '
           '(not the SECRET ones) and my fishing tips. Tight lines!'],
    sections=[
        S('table', ['My Best Catches', 'Brag Board'], [('Largemouth bass', '7 lb 2 oz, Lake Tamarack, 1997'),
                                                     ('Walleye', '9 lb 6 oz, Rainy River, 1998'),
                                                     ('Catfish', '22 lb, behind the dam, 1996'),
                                                     ('Crappie', '42 of them in one afternoon'),
                                                     ('Trout', '4 lb, it got away but it was 4 lb I swear'),
                                                     ('My hat', 'Lake Erie, 1995, still mad about it')], n=(4, 6)),
        S('list', ['Fishing Tips'], ['Fish early. Fish late. Fish in the rain.', 'Change lures if nothing bites in '
                                     '20 minutes.', 'Bring more snacks than you think.', 'Do not let your brother-in-'
                                     'law drive the boat.', 'Catch and release the little ones.'], n=(3, 5)),
        S('photos', ['Photos'], [('photo_mountain.gif', 'The lake at sunrise'), ('photo_food.gif', 'Fish fry!')],
          n=(1, 2)),
        S('links', ['Links'], n=(2, 4)),
    ],
    images=['photo_mountain.gif'], bullets=['ball_green.gif'], lines=['line_rope.gif'],
    styles=['wood', 'water', 'camo', 'retro_tan'], layouts=['single'], midi=['hoedown', None], ring='sports',
    keywords='fishing bass walleye lakes tips', desc=['Fishing brag board and tips'],
    gb=['Nice walleye!', 'Where is the secret lake? I won\'t tell.']))

T1.append(T('wrestling', 'Gridiron', 'Tackle', 2, age=(13, 30), gender='m',
    titles=['UGW: Ultimate Grudge Wrestling Fan Site', '{handle}\'s Wrestling Page'],
    intro=['WHAT\'S UP!!! This is the best page on the Internet for fans of <B>Ultimate Grudge Wrestling</B>, the '
           'wildest show on Monday nights. Results, rumors and my power rankings!'],
    sections=[
        S('top10', ['Power Rankings', 'Top Wrestlers'], ['Captain Concussion', 'Gravedigger Gus', 'Mighty Mike Mayhem',
                                                       'Lord Lariat', 'Hurricane Harlan', 'The Accountant (he audits '
                                                                                         'you... with PAIN)',
                                                       'Sister Suplex', 'El Tornado Azul', 'Big Country Cletus',
                                                       'The Masked Substitute Teacher'], n=(5, 10)),
        S('log', ['Monday Night Results'], ['Captain Concussion pinned Lord Lariat after a chair shot. The ref did NOT '
                                            'see it.', 'Gravedigger Gus came out of a coffin. Again.',
                                            'Steel cage match ended when the cage fell over. Nobody won.',
                                            'Sister Suplex won the title!!! The crowd went nuts.',
                                            'The Accountant made Hurricane Harlan file his taxes. Brutal.'], n=(3, 5)),
        S('links', ['Wrestling Links'], n=(2, 4)),
    ],
    images=['skull_spin.gif', 'fire.gif', 'hot.gif'], bullets=['bullet_skull.gif', 'ball_red.gif'],
    lines=['flames.gif', 'line_barbed.gif'], styles=['border_flames', 'black_neon', 'checker'], layouts=['single'],
    midi=['punk', 'techno'], ring='sports', keywords='wrestling ugw results power rankings',
    desc=['Ultimate Grudge Wrestling results and rankings'], gb=['Concussion RULES', 'The cage falling was the best.']))

T1.append(T('bowling', 'Gridiron', 'Tackle', 1, age=(40, 75),
    titles=['Tuesday Night Strikers Bowling League'],
    intro=['Welcome to the website of the <B>Tuesday Night Strikers</B>, {town}\'s friendliest mixed bowling league. '
           'We bowl at Starlite Lanes every Tuesday at 7. New members always welcome, even if you throw gutter balls.'],
    sections=[
        S('table', ['Team Standings'], [('Pin Pals', '48-24'), ('Split Happens', '45-27'), ('Gutter Gang', '40-32'),
                                        ('The Spare Parts', '33-39'), ('Alley Cats', '30-42'), ('Lucky Strikes',
                                                                                              '20-52')], n=(5, 6)),
        S('table', ['High Averages'], [('Earl', '201'), ('Bev', '188'), ('Marvin', '176'), ('Gloria', '170'),
                                       ('Lyle', '163')], n=(4, 5)),
        S('para', ['News'], ['Congratulations to Bev for her first 250 game! The whole alley stood up and clapped. '
                             'Banquet is May 20 at the VFW. Bring a covered dish.'], n=(1, 1)),
        S('links', ['Links'], n=(2, 3)),
    ],
    images=['award_coolweek.gif'], bullets=['ball_blue.gif'], lines=['rainbow_hr.gif'],
    styles=['retro_tan', 'plain', 'marble'], layouts=['single'], midi=['ragtime', None], ring='sports',
    keywords='bowling league standings averages', desc=['Mixed bowling league standings'],
    gb=['Split Happens will win next year!', 'Congrats Bev!']))

# ------------------------------------------------------------------ Bayou
BANDS = [
    dict(band='Northbound', members=['AJ', 'Trey', 'Kip', 'Dominic', 'Shane'],
         songs=['Can\'t Stop Thinking (About You Baby)', 'Hold Me Like a Pager', 'Forever Tonight', 'Northbound Train',
                'Girl You\'re My Screensaver', 'One More Slow Dance']),
    dict(band='Heartbeat Harbor', members=['Corey', 'Jamal', 'Dex', 'Tommy', 'Lucas'],
         songs=['Harbor Lights', 'Every Little Heartbeat', 'Call Me (On The Landline)', 'Summer Was You',
                'Don\'t Go Breakin\' My Pager', 'Ooh La La Lovesick']),
    dict(band='Velvet Avenue', members=['Ricky', 'Tyler', 'Marcus', 'Jesse'],
         songs=['Velvet Love', 'All My Life (Plus One Day)', 'Baby Come Back To The Mall', 'Starlight Promise',
                'Bring It On Home Tonight', 'Remember Me (In Your Diary)']),
]

T1.append(T('boyband', 'Bayou', 'Backstage', 7, age=(11, 17), gender='f',
    titles=['{band} 4-EVER!!!', 'The {band} Fan Club Page', '{member1} Is My Boyfriend (A {band} Site)',
            '{handle}\'s {band} Shrine', 'I {band}!!!', '{band} Lyrics & Pics', 'ALL ABOUT {band}'],
    entities=BANDS,
    intro=['HI!!!!! Welcome to my <B>{band}</B> page!!!! {band} is the best band in the WHOLE WORLD and {member1} is '
           'my favorite (sorry {member2}). This page has bios, pics, tour dates and MORE. Please sign my guestbook!!!!',
           'If you love <B>{band}</B> you have come to the right place!!! I have been a fan since their first single '
           'and I have seen them in concert TWICE. My voice still hurts from screaming.',
           'This page is dedicated to the 5 cutest guys on the planet... okay {band} has {nmembers} guys but '
           'you know what I mean. ENJOY!!!'],
    sections=[
        S('list', ['The Guys', 'Meet {band}', 'Bios'], [
            '<B>{member1}</B> - the sweet one. Born in April. Loves puppies and his mom.',
            '<B>{member2}</B> - the bad boy. Has a tattoo (of a dolphin!!!)', '<B>{member3}</B> - the funny one. '
            'Can do 14 voices.', '<B>{member4}</B> - the shy one. Plays guitar. Sigh.',
            '<B>{member5}</B> - the one with the frosted tips. You know the one.'], n=(3, 5)),
        S('list', ['Discography', 'Their Songs'], ['"{song1}"', '"{song2}"', '"{song3}"', '"{song4}"', '"{song5}"',
                                                   '"{song6}"'], n=(4, 6)),
        S('para', ['Concert Report!!!', 'I SAW THEM LIVE'], [
            'Okay so my mom took me and my best friend Kristy to see {band} at the {town} Civic Arena and it was THE '
            'BEST NIGHT OF MY LIFE. They did "{song1}" and {member1} pointed RIGHT AT US. Kristy says he was pointing '
            'at her but he was NOT. We bought shirts and a poster and a keychain.',
            'They came out on a platform that came up through the floor with smoke and lasers and everybody screamed '
            'so loud I could not hear the first song. Then they did the dance from the video and I almost cried.'],
          n=(1, 1), prob=0.7),
        S('table', ['Tour Dates', '1999 Tour'], [('Oct 15', 'Fresno Civic Arena'), ('Oct 17', 'Reno Event Center'),
                                                 ('Oct 22', 'Boise Dome'), ('Oct 30', 'Tulsa Pavilion (Halloween '
                                                                                       'show!!)'),
                                                 ('Nov 5', 'Omaha Coliseum'), ('Nov 12', 'Peoria Fieldhouse')],
          n=(3, 6), prob=0.6),
        S('poll', ['Who Is The Cutest?', 'VOTE: Fave Member'], ['{member1}', '{member2}', '{member3}', '{member4}'],
          n=(1, 1), prob=0.7),
        S('links', ['Other {band} Pages', 'My Friends\' Pages'], n=(3, 6)),
    ],
    subpages=[SUB('lyrics.html', ['Lyrics (I wrote them down from the CD)', 'My Fan Lyrics'], [
        S('poems', ['Lyrics'], [
            ('{song1} (my own version)', 'Every time the phone rings\nI hope that it is you\nEvery time the night '
             'comes\nI think about you too\n\nCan\'t stop thinking, baby\nCan\'t stop thinking \'bout you\nOoh yeah'),
            ('A Song I Wrote For {member1}', 'You smile on my poster\nI smile right back\nOne day we will meet\nAnd '
             'that is a fact\n\n(I know it is not very good. I am working on it.)')], n=(1, 2))], prob=0.6),
        SUB('pics.html', ['PICS!!!', 'Picture Gallery'], [
            S('photos', ['Pictures'], [('photo_band.gif', '{band} at the music awards!!!'),
                                       ('photo_me2.gif', 'Me in my {band} shirt'),
                                       ('broken.gif', 'This pic of {member1} is loading (or my scanner broke)'),
                                       ('heart.gif', '<3 <3 <3')], n=(2, 4))], prob=0.6)],
    images=['heart.gif', 'notes.gif', 'cd_spin.gif', 'photo_band.gif'], bullets=['bullet_heart.gif', 'ball_pink.gif',
                                                                                 'bullet_star.gif'],
    lines=['line_hearts.gif', 'rainbow_line.gif', 'line_stars.gif', 'line_bows.gif'],
    styles=['glitter', 'pastel_hearts', 'border_pink', 'black_neon', 'pastel_flowers', 'clouds'],
    layouts=['single', 'single', 'splash', 'frames', 'sidebar'], midi=['heartthrob', 'lovesong', 'techno'],
    ring='boyband', keywords='{band} boy band fan page lyrics tour {member1}',
    desc=['{band} fan page with bios, songs and tour dates', 'Shrine to {band} and especially {member1}',
          '{band} pictures, lyrics and concert report'],
    gb=['{member1} is MINE!!! lol jk', 'I love {band} SO MUCH', 'Can I put your page on my links? <3',
        'I saw them in Boise!!!!!!', '{member2} is cuter!!!!!']))

T1.append(T('girlpop', 'Bayou', 'Backstage', 2, age=(10, 16), gender='f',
    titles=['The Glitter Girlz Fan Zone', 'Candi Sweetwater Superfan Page'],
    intro=['Girl power!!! This page is all about the <B>Glitter Girlz</B> (Sparkle, Sassy, Sleepy, Saucy and Smarty) '
           'and their new album <I>Shine On, Sister</I>. Which Glitter Girl are you? Take my quiz!',
           'Candi Sweetwater is the best singer in the world and she is only 17!!! Her song "Lollipop Heart" has been '
           'number 1 for 6 weeks. This is my page about her.'],
    sections=[
        S('list', ['Which One Are You?'], ['<B>Sparkle</B> - loves glitter (obviously) and dancing',
                                           '<B>Sassy</B> - says what she thinks!', '<B>Sleepy</B> - the chill one',
                                           '<B>Saucy</B> - cooks, wears big shoes', '<B>Smarty</B> - reads books, wears '
                                                                                   'glasses, still cool'], n=(4, 5)),
        S('list', ['Songs'], ['"Shine On, Sister"', '"Lollipop Heart"', '"Friendship Bracelet"', '"Don\'t Call Me Baby '
                                                                                                 '(Call Me Later)"',
                              '"Platform Shoes"'], n=(3, 5)),
        S('poll', ['Quiz: Which Glitter Girl Are You?'], ['Sparkle', 'Sassy', 'Sleepy', 'Saucy', 'Smarty'], n=(1, 1)),
        S('links', ['Links'], n=(2, 4)),
    ],
    images=['heart.gif', 'twinkle.gif', 'notes.gif'], bullets=['bullet_heart.gif', 'bullet_star.gif'],
    lines=['line_hearts.gif', 'rainbow_line.gif'], styles=['glitter', 'pastel_hearts', 'leopard'], layouts=['single'],
    midi=['heartthrob', 'techno'], ring='boyband', keywords='glitter girlz candi sweetwater girl pop',
    desc=['Girl pop fan page'], gb=['I am Sassy!!!', 'GIRL POWER!!']))

T1.append(T('garageband', 'Bayou', 'Mosh', 4, age=(15, 28), gender='m',
    titles=['{gband} - Official Site', '{gband} (we rock)', 'The {gband} Homepage', '{gband}: Shows, Lyrics, Merch'],
    entities=[dict(gband='Dial Tone Riot', genre='punk', practice='my garage'),
              dict(gband='The Mopeds', genre='ska', practice='Dave\'s basement'),
              dict(gband='Sorry Mom', genre='grunge', practice='the storage unit'),
              dict(gband='Velcro Sunrise', genre='indie rock', practice='the church basement (shh)'),
              dict(gband='Lunchbox Martyrs', genre='pop-punk', practice='my parents\' garage when they are at work')],
    intro=['We are <B>{gband}</B>, a {genre} band from {town}. We practice in {practice} and play anywhere that will '
           'have us (VFW halls, skate parks, one bar mitzvah). Check out our shows and lyrics below. Our demo tape is '
           '$3.',
           '<B>{gband}</B> = loud. That is pretty much all you need to know. Shows, lyrics and our demo tape below.'],
    sections=[
        S('table', ['Upcoming Shows', 'Gigs'], [('Fri 10/22', 'Skate Barn w/ Plastic Saints, $5, all ages'),
                                                ('Sat 10/30', 'Halloween show at the VFW (costumes required)'),
                                                ('Fri 11/12', 'Battle of the Bands @ {town} High (wish us luck)'),
                                                ('Sat 11/20', 'Somebody\'s basement, ask us for directions'),
                                                ('Sun 12/5', 'Record store parking lot (if it doesn\'t snow)')],
          n=(3, 5)),
        S('list', ['The Band', 'Members'], ['{first} - vocals, guitar, writes the songs', 'Nick - bass (4 strings, '
                                                                                         'mostly)',
                                            'Jen - drums (hits the hardest)', 'Paco - trumpet (we are ska sometimes)',
                                            'Dave - guitar, owns the van'], n=(3, 5)),
        S('poems', ['Lyrics'], [('Dial Tone', 'I called you up at midnight\nall I got was the dial tone\nI called you '
                                 'up at one a.m.\nstill nobody home\n\nDIAL TONE (x4)'),
                                ('Cul-de-sac', 'Every street around here\nends in a circle\nevery day around here\nends '
                                 'up the same\nride my bike around the cul-de-sac\nnobody knows my name'),
                                ('Microwave Dinner', 'Three minutes on high\nand my whole life goes by\nstir halfway '
                                 'through\nI am thinking of you')], n=(1, 2)),
        S('para', ['Merch'], ['Demo tape: $3 (6 songs, recorded on a 4-track). T-shirts: $8, we screen printed them '
                              'ourselves so each one is unique (crooked). E-mail us to order!'], n=(1, 1)),
        S('links', ['Bands We Like', 'Friends'], n=(3, 5)),
    ],
    images=['photo_band.gif', 'skull_spin.gif', 'cd_spin.gif', 'fire.gif'], bullets=['bullet_skull.gif',
                                                                                     'ball_red.gif'],
    lines=['line_barbed.gif', 'flames.gif', 'line_lightning.gif'], styles=['black_neon', 'border_flames', 'goth',
                                                                         'checker', 'denim', 'concrete'],
    layouts=['single', 'sidebar', 'frames'], midi=['punk', 'surf', 'techno'], ring='indie',
    keywords='{gband} band {genre} shows lyrics demo tape',
    desc=['{gband}: {genre} band from {town}', 'Shows, lyrics and demo tapes from {gband}'],
    gb=['You guys rocked the skate barn!!!', 'When is the next show?', 'Dial Tone is stuck in my head.']))

T1.append(T('midicoll', 'Bayou', 'Jukebox', 3, age=(15, 60),
    titles=['{first}\'s MIDI Jukebox', 'The MIDI Lounge', 'MIDI Heaven'],
    intro=['Welcome to my MIDI collection! All of these MIDI files are original tunes made by me and my friends on '
           'my keyboard. Click a title to listen. Feel free to use them on your page (give credit please!).',
           'I love MIDI music. These files are small, they load fast, and they sound great on a NoiseCannon card. '
           'Pick a song!'],
    sections=[
        S('midis', ['The Collection', 'Pick A Song'], [], n=(8, 14)),
        S('para', ['About MIDI'], ['A MIDI file is not a recording, it is more like sheet music for your computer. '
                                   'That is why they are so small! Every sound card plays them a little differently, '
                                   'so if it sounds weird, blame your sound card, not me.'], n=(1, 1)),
        S('links', ['More MIDI Sites'], n=(3, 5)),
    ],
    images=['notes.gif', 'cd_spin.gif'], bullets=['ball_purple.gif', 'ball_blue.gif'],
    lines=['line_notes.gif', 'rainbow_line.gif'], styles=['black_neon', 'border_purple', 'nebula', 'marble'],
    layouts=['single', 'sidebar'], midi=['ragtime', 'elevator', 'holiday'], ring='indie',
    keywords='midi music collection jukebox songs', desc=['Collection of original MIDI tunes'],
    gb=['Great MIDIs! Using one on my page.', 'Sounds awesome on my AWE64.']))

T1.append(T('bandstand', 'Bayou', 'Bandstand', 3, age=(40, 80),
    titles=['The {town} Polka Pals', '{first}\'s Country Music Corner', 'Big Band Memories'],
    intro=['Welcome, friends! This page is about the music I love, the music my parents loved, and the music that '
           'still gets the whole family dancing at weddings.',
           'Pull up a hay bale. This page is about real country music, the kind with fiddles and stories about trucks.'],
    sections=[
        S('list', ['Favorite Songs'], ['"The Beer Barrel Shuffle"', '"My Truck Left Me Too"', '"Accordion Sunrise"',
                                       '"Dance Hall Saturday"', '"Grandpa\'s Fiddle"', '"Cotton Field Two-Step"',
                                       '"Moonlight Over the Lodge Hall"'], n=(4, 6)),
        S('table', ['Where To Dance', 'Dance Schedule'], [('Fridays', 'Polka night at the Lodge Hall'),
                                                          ('Saturdays', 'Line dancing at the Rusty Spur'),
                                                          ('Sundays', 'Big band brunch at the Elks Club'),
                                                          ('2nd Tuesday', 'Fiddle jam at the library')], n=(2, 4)),
        S('photos', ['Photos'], [('photo_band.gif', 'Our band at the county fair'),
                                 ('photo_family.gif', 'The whole family at Cousin Al\'s wedding')], n=(1, 2)),
        S('links', ['Links'], n=(2, 4)),
    ],
    images=['notes.gif'], bullets=['ball_red.gif'], lines=['line_rope.gif', 'line_notes.gif'],
    styles=['gingham', 'wood', 'retro_tan', 'denim'], layouts=['single'], midi=['hoedown', 'ragtime', 'anthem'],
    ring='indie', keywords='polka country music big band dancing', desc=['Polka, country and big band music page'],
    gb=['See you at polka night!', 'Yee-haw!']))
