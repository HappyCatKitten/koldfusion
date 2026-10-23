# -*- coding: utf-8 -*-
"""Invented data for Snapster: bands, songs, users, chat logs.  Everything here is
made up -- no real songs, artists, albums, labels or files.

build_catalog() turns bands x songs x users into the shared-file rows that end
up in catalog.js (deterministic: seeded RNG)."""
import random

ME = 'snapfan_99'
ME_CONN = 'T1'          # a dorm-room T1, naturally
TOTAL_USERS = 8412
TOTAL_SONGS = 1207553

# Napster-style line speed list; the index is the rank used by the filters
CONN = ['Unknown', '14.4', '28.8', '33.6', '56K', 'ISDN-64K', 'ISDN-128K', 'Cable', 'DSL', 'T1', 'T3+']
# rough KB/s a remote user of that line can push (used by transfer.html)
CONN_KBPS = [3.0, 1.1, 2.4, 2.9, 4.4, 6.5, 12.0, 60.0, 45.0, 150.0, 220.0]

# (band, genre, [(title, seconds), ...])
BANDS = [
    ('Shiny Metallic Things', 'Metal', [
        ('Napkin of Doom', 452), ('Enter Lawyer', 331), ('Sad But Billable', 324),
        ('Fade to Beige', 417), ('Horsemen Running Late', 433)]),
    ('Limp Noodle Theory', 'Nu-Metal', [
        ('Red Cap of Rage', 233), ('Do It All for the Snacks', 214), ('My Mom Doesn\'t Get It', 248),
        ('Chain Wallet', 197), ('Drop D Daydream', 262)]),
    ('The Bling Bling Lawnmowers', 'Rap-Rock', [
        ('Rap Rock Rock Rap', 201), ('Turntable in a Mosh Pit', 236), ('Mow Your Lawn', 189),
        ('Rage Against the Vending Machine', 254), ('Wallet Chain Reaction', 222)]),
    ('Frosted Tips Federation', 'Boy Band', [
        ('Bye Bye Pager', 199), ('Tearin\' Up My Modem', 211), ('Girl, You\'re My Screensaver', 236),
        ('Five Part Harmony (Four Part Talent)', 244), ('Please Sign My Lunchbox', 205)]),
    ('Mall Tour 5', 'Boy Band', [
        ('Synchronized Heartbreak', 228), ('Food Court Valentine', 216), ('Key Change of My Heart', 251),
        ('Turtleneck Tuesday', 203), ('Stool Ballad (Everybody Stand Up)', 262)]),
    ('Platform Shoe Posse', 'Pop', [
        ('Tell Me What You Really Really Need', 182), ('Girl Power Strip', 207), ('Zig-a-Zag', 194),
        ('Glitter Emergency', 213), ('Mall Fountain Wish', 225)]),
    ('Kayleigh Glitter', 'Pop', [
        ('Oops, I Rebooted Again', 211), ('Baby One More Byte', 217), ('Sometimes (I Forget My Password)', 243),
        ('Glitter Pen Diary', 198), ('Crush on the Webmaster', 206)]),
    ('Checkerboard Tuxedo Revue', 'Ska', [
        ('Pick It Up (And Put It Down Again)', 178), ('Skank Like an Accountant', 191), ('Trombone Emergency', 164),
        ('Two-Tone Phone', 203), ('Rudy Got a Day Job', 186)]),
    ('The Upstroke Accountants', 'Ska', [
        ('Spreadsheet Skank', 172), ('Pork Pie Payroll', 199), ('Horn Section Overtime', 214),
        ('Fiscal Year Stomp', 183), ('Checkered Past', 207)]),
    ('Swing Shift Mortgage Brokers', 'Swing', [
        ('Jump, Jive an\' Refinance', 196), ('Zoot Suit Layaway', 184), ('Hep to the Interest Rate', 209),
        ('Lindy Hop on Pop', 171), ('Daddy-O\'s Dial-Up', 222)]),
    ('The Cherry Lounge Hepcats', 'Swing', [
        ('Martini Emergency', 188), ('Cocktail Napkin Serenade', 231), ('Swing Baby Swing (Not That Swing)', 175),
        ('Two Left Wingtips', 193), ('Khakis Commercial Blues', 158)]),
    ('Bristol Fog Machine', 'Trip-Hop', [
        ('Teardrop in My Latte', 327), ('Downtempo Dial Tone', 381), ('Slow Motion Mood Ring', 344),
        ('Smoke Machine Sunday', 402), ('Basement Strings', 296)]),
    ('Porthole Mood', 'Trip-Hop', [
        ('Theremin for Two', 268), ('Vinyl Crackle Lullaby', 302), ('Sad Robot Lounge', 285),
        ('Scratchy Record of You', 317), ('Grey Afternoon in 3/4', 356)]),
    ('Captain Bigbeat & the Vinyl Squad', 'Big Beat', [
        ('Funk Soul Accountant', 342), ('Breaks for Breakfast', 288), ('Big Beat Big Sneakers', 307),
        ('The Bassline Is a Lie', 365), ('Acid Lawn Party', 401)]),
    ('The Chemistry Set Brothers', 'Big Beat', [
        ('Bunsen Burner Breakbeat', 318), ('Hey Girl Hey Beaker', 286), ('Setting Sun Lamp', 344),
        ('Petri Dish Groove', 297), ('Lab Coat Rave', 412)]),
    ('Prodigal Sons of Noise', 'Big Beat', [
        ('Breathe Into the Paper Bag', 263), ('Mohawk Emergency', 241), ('Glowstick Fight', 289),
        ('Warehouse Ticket Stub', 312), ('Out of Space Bar', 274)]),
    ('DJ Dialtone', 'Electronica', [
        ('Handshake (56K Mix)', 389), ('Carrier Detected', 421), ('Busy Signal Dub', 366),
        ('ATDT Anthem', 344), ('Connection Dropped (Reprise)', 132)]),
    ('Y2K Bug Collective', 'Techno', [
        ('Nineteen Hundred Again', 377), ('Millennium Bunker Groove', 412), ('Two Digit Date', 299),
        ('Canned Goods Stomp', 318), ('Midnight Rollover', 600)]),
    ('Floppy Disco', 'Techno', [
        ('3.5 Inch Love', 245), ('Insert Disk 2', 262), ('Abort Retry Ignore', 231),
        ('Format C: Your Heart', 284), ('Disk Full of Love', 239)]),
    ('Cardigan Feelings Society', 'Emo', [
        ('Your Bike Is in My Garage (So Is My Heart)', 287), ('Thick Rimmed Glasses', 233),
        ('Letter I Never Mailed', 301), ('Sweater Weather Inside My Chest', 268),
        ('Song for the Girl at the Show', 344)]),
    ('Glasses Fogged Over', 'Emo', [
        ('Basement Show at Kevin\'s', 254), ('The Mixtape I Didn\'t Give You', 312), ('Van Broke Down in Ohio', 276),
        ('Crying in the Food Court', 241), ('Dear Diary, Dear Distortion', 299)]),
    ('Skate Park Detention', 'Pop-Punk', [
        ('Lunch Detention', 154), ('Girlfriend Got a Pager', 167), ('Prom Is Lame (I Didn\'t Get Asked)', 149),
        ('Skateboard Insurance', 138), ('Mom\'s Minivan', 172)]),
    ('Flannel Hangover', 'Alternative', [
        ('Seattle Was Yesterday', 276), ('Plaid to the Bone', 248), ('Black Coffee Hole', 301),
        ('Unplugged & Unwashed', 263), ('Mumble Anthem', 289)]),
    ('Lunchbox Forty', 'Alternative', [
        ('Push the Cart', 233), ('3 A.M. Infomercial', 246), ('Real World Laundromat', 228),
        ('Back 2 Good Enough', 259), ('Bent Spork', 214)]),
    ('MC Dial-Up', 'Hip-Hop', [
        ('Gettin\' Jiggy With the Modem', 238), ('Bandwidth Ballin\'', 251), ('Straight Outta Cul-de-sac', 226),
        ('My Two-Way Pager', 243), ('Shout Out to My Sysop', 219)]),
    ('Lil\' Pager', 'Hip-Hop', [
        ('Beep Me (911)', 207), ('Pager Code 143', 229), ('Bling Bling Calculator', 244),
        ('Ice on My Watch (Digital)', 216), ('Throw Your Hands Up (Then Put Them Back Down)', 232)]),
    ('Tiki Bar Cosmonauts', 'Lounge', [
        ('Moon Bossa', 187), ('Volcano Highball', 203), ('Space Age Bachelor Pad Detective', 224),
        ('Hula Hoop Orbit', 176), ('Lava Lamp Lullaby', 241)]),
    ('Hacky Sack Philosophy', 'Jam Band', [
        ('Twenty-Two Minute Tuning Jam', 1322), ('Parking Lot Grilled Cheese', 487), ('Tie-Dye Tuesday', 411),
        ('Bootleg Taper Section', 563), ('Noodle Dancer (Part 1 of 9)', 702)]),
    ('Los Hermanos Bailamania', 'Latin', [
        ('Mambo Number 404', 214), ('La Macaroni', 228), ('El Electric Slide 2000', 241),
        ('Cha Cha Chupacabra', 196), ('Fiesta en el Food Court', 219)]),
    ('Barrette Riot', 'Punk', [
        ('Zine Queen', 131), ('Photocopy Revolution', 144), ('Not Your Dial-Up Girl', 158),
        ('Combat Boot Ballet', 167), ('Sharpie on My Hand', 122)]),
    ('Patchouli Fair Sisters', 'Folk', [
        ('Barefoot at the Open Mic', 263), ('Candle Shop Lament', 288), ('Herbal Tea Breakup', 241),
        ('Acoustic Guitar Strap', 229), ('Unplugged in the Rain', 302)]),
]

# (screen name, connection, genres they hoard)
USERS = [
    ('xXdarkangelXx', '56K', ['Metal', 'Nu-Metal', 'Emo', 'Trip-Hop']),
    ('b0rk_b0rk', 'Cable', ['Big Beat', 'Electronica', 'Techno', 'Ska']),
    ('DormRoomDJ', 'T1', ['Hip-Hop', 'Big Beat', 'Latin', 'Pop', 'Rap-Rock']),
    ('sk8rkev', '33.6', ['Pop-Punk', 'Ska', 'Punk']),
    ('mp3kid99', 'DSL', ['Pop', 'Boy Band', 'Hip-Hop']),
    ('lanparty_larry', 'T3+', ['Metal', 'Techno', 'Electronica']),
    ('DialUpDiva4eva', '28.8', ['Boy Band', 'Pop']),
    ('y2k_bunker_bob', '14.4', ['Techno', 'Folk']),
    ('ska_dad_mike', 'ISDN-128K', ['Ska', 'Swing']),
    ('glitterpen_jen', '56K', ['Pop', 'Boy Band', 'Latin']),
    ('newbie_ned', 'Unknown', ['Alternative']),
    ('ftp_phil', 'T1', ['Alternative', 'Jam Band', 'Metal']),
    ('tapersection_tom', 'DSL', ['Jam Band', 'Folk']),
    ('swinggirl76', 'Cable', ['Swing', 'Lounge']),
    ('BigBeatBen', 'ISDN-64K', ['Big Beat', 'Electronica']),
    ('RedPillBluePill', 'Cable', ['Techno', 'Electronica', 'Rap-Rock']),
    ('Furbee_Hacker', '56K', ['Electronica', 'Pop']),
    ('FrondPilotPete', '14.4', ['Lounge', 'Alternative']),
    ('NetsailNavi_Gator', '56K', ['Alternative', 'Pop-Punk']),
    ('IEisBetter', 'T1', ['Boy Band', 'Swing']),
    ('beanie_baron', '33.6', ['Folk', 'Pop']),
    ('daytrader_dan', 'DSL', ['Swing', 'Lounge', 'Big Beat']),
    ('keychainpet_ghost', 'Unknown', ['Pop', 'Emo']),
    ('paperclip_fan', '28.8', ['Lounge', 'Folk']),
    ('[phreak]0ut', 'ISDN-128K', ['Electronica', 'Techno', 'Punk']),
    ('emo_kid_sad_face', 'DSL', ['Emo', 'Pop-Punk', 'Punk']),
    ('frosted_tips_4ever', '56K', ['Boy Band']),
    ('nu_metal_nate', 'Cable', ['Nu-Metal', 'Rap-Rock', 'Metal']),
    ('trip_hop_tina', 'Cable', ['Trip-Hop', 'Lounge']),
    ('kazoo_kid', '33.6', ['Ska', 'Latin']),
    ('llama_whipper', '56K', ['Alternative', 'Rap-Rock', 'Big Beat']),
    ('quake_clan_leader', 'T1', ['Metal', 'Techno']),
    ('geohoods_gwen', '28.8', ['Folk', 'Emo']),
    ('dancing_baby_dave', '56K', ['Latin', 'Techno']),
    ('bondi_blue_betty', 'DSL', ['Trip-Hop', 'Electronica', 'Swing']),
    ('1337_h4x0r', 'Unknown', ['Nu-Metal', 'Electronica']),
    ('pentium3_paul', 'T1', ['Hip-Hop', 'Alternative']),
    ('pogs_champion', '33.6', ['Pop-Punk', 'Hip-Hop']),
]

# the Hot List: (user, online?, note)
HOTLIST = [
    ('xXdarkangelXx', True, 'always has the live stuff'),
    ('b0rk_b0rk', True, 'fastest cable on the block'),
    ('DormRoomDJ', True, 'campus T1, do NOT tell the RA'),
    ('sk8rkev', False, 'last seen 11:52 PM (mom picked up the phone)'),
    ('mp3kid99', True, 'has every boy band single, ironically'),
    ('y2k_bunker_bob', False, 'logged off to fill water jugs'),
    ('ska_dad_mike', True, 'owns 3 pork pie hats'),
    ('swinggirl76', True, 'swing revival archivist'),
    ('RedPillBluePill', False, 'went to see that movie again'),
    ('daytrader_dan', True, 'downloads between trades'),
    ('glitterpen_jen', True, 'great taste, slow modem'),
    ('emo_kid_sad_face', False, 'away: writing in journal'),
]

BITRATES = [(128, 50), (160, 10), (192, 10), (96, 9), (64, 8), (320, 5), (112, 4), (256, 4)]
SPEEDS = {}


def slug(s):
    return ''.join(c for c in s.lower() if c.isalnum() or c == '_')


def fmt_len(sec):
    return '%d:%02d' % (sec // 60, sec % 60)


def _filename(rng, band, title, track):
    v = rng.randint(0, 11)
    if v <= 3:
        return '%s - %s.mp3' % (band, title)
    if v == 4:
        return ('%s-%s.mp3' % (band, title)).lower().replace(' ', '_').replace('\'', '').replace(',', '')
    if v == 5:
        return '%s - %s (LIVE).mp3' % (band, title)
    if v == 6:
        return '%s - %02d - %s.mp3' % (band, track, title)
    if v == 7:
        return ('%s_-_%s.mp3' % (band, title)).replace(' ', '_')
    if v == 8:
        return '%s - %s [radio edit].mp3' % (band, title)
    if v == 9:
        return '%s - %s (good quality!!).mp3' % (band, title)
    if v == 10:
        return ('%s - %s.mp3' % (band, title)).upper()
    return '%s - %s (REMIX).mp3' % (band, title)


def build_catalog():
    """returns list of dicts: id, artist, title, file, size, bitrate, freq, secs, user, conn, ping"""
    rng = random.Random(1999)
    by_genre = {}
    for u, c, g in USERS:
        for x in g:
            by_genre.setdefault(x, []).append(u)
    conn_of = dict((u, c) for u, c, g in USERS)
    names = [u for u, c, g in USERS]
    rows = []
    bitrates = [b for b, w in BITRATES for _ in range(w)]
    for band, genre, songs in BANDS:
        for track, (title, secs) in enumerate(songs, 1):
            sharers = [u for u in by_genre.get(genre, []) if rng.random() < 0.55]
            sharers += rng.sample(names, rng.randint(1, 2))
            seen = []
            for u in sharers:
                if u not in seen:
                    seen.append(u)
            for u in seen[:6]:
                br = rng.choice(bitrates)
                freq = 22050 if br <= 64 or (br == 96 and rng.random() < 0.5) else 44100
                s = secs
                fname = _filename(rng, band, title, track)
                if rng.random() < 0.04:
                    s = int(secs * rng.uniform(0.3, 0.8))
                    fname = fname[:-4] + ' (incomplete).mp3'
                size = int(br * 1000 / 8 * s) + 128 + rng.randint(0, 4000)
                conn = conn_of[u]
                ci = CONN.index(conn)
                base = {0: 400, 1: 600, 2: 420, 3: 330, 4: 210, 5: 140, 6: 110, 7: 60, 8: 70, 9: 25, 10: 15}[ci]
                ping = int(base * rng.uniform(0.6, 1.8))
                rows.append(dict(artist=band, title=title, file=fname, size=size, bitrate=br, freq=freq,
                                 secs=s, user=u, conn=ci, ping=ping, genre=genre))
    for i, r in enumerate(rows):
        r['id'] = i
    return rows


# ------------------------------------------------------------------ your library
LIBRARY = [
    ('C:\\My Documents\\My Music', [
        ('Totally Legal Stuff', [
            ('Snapster legal disclaimer.mp3', 128, 94),
            ('Me humming the dial-up sound.mp3', 64, 31),
            ('Grandma - Happy Birthday voicemail.mp3', 96, 47),
        ]),
        ('Stuff I Own On Cassette (honest)', [
            ('Platform Shoe Posse - Zig-a-Zag.mp3', 128, 194),
            ('Frosted Tips Federation - Bye Bye Pager.mp3', 128, 199),
            ('Skate Park Detention - Mom\'s Minivan.mp3', 160, 172),
            ('Checkerboard Tuxedo Revue - Trombone Emergency.mp3', 128, 164),
        ]),
        ('Recorded Off the Radio (DJ talks over intro)', [
            ('Lunchbox Forty - Push the Cart (DJ Rick ruins it).mp3', 96, 241),
            ('MC Dial-Up - My Two-Way Pager (traffic report at end).mp3', 96, 260),
        ]),
        ('Wedding DJ Gig Sat', [
            ('Los Hermanos Bailamania - Mambo Number 404.mp3', 192, 214),
            ('Los Hermanos Bailamania - El Electric Slide 2000.mp3', 192, 241),
            ('Swing Shift Mortgage Brokers - Jump, Jive an\' Refinance.mp3', 160, 196),
            ('The Cherry Lounge Hepcats - Two Left Wingtips.mp3', 128, 193),
        ]),
        ('Study Music (do not tell roommate)', [
            ('Bristol Fog Machine - Teardrop in My Latte.mp3', 192, 327),
            ('Porthole Mood - Sad Robot Lounge.mp3', 128, 285),
            ('Tiki Bar Cosmonauts - Moon Bossa.mp3', 128, 187),
        ]),
        ('Incomplete', [
            ('Hacky Sack Philosophy - Twenty-Two Minute Tuning Jam.mp3.incomplete', 128, 61),
            ('DJ Dialtone - Handshake (56K Mix).mp3.incomplete', 160, 12),
        ]),
    ]),
]

NEWS = [
    ('10/23/00', 'Snapster 2.0 Beta 5 is here!',
     'Now with 40% fewer crashes, a Hot List that remembers who your friends are, and a brand new '
     '"Remote user cancelled" message that is 12% more polite.'),
    ('10/20/00', 'Server farm upgraded',
     'We moved the Snapster servers from Shawn\'s closet to Shawn\'s roommate\'s closet, which has a window. '
     'Expect faster searches when the window is open.'),
    ('10/16/00', 'Tip: set your line speed honestly',
     'Telling everybody you are on a T3 when you are on a 14.4 makes Snappy sad. Very sad. He is a turtle; '
     'he knows slow when he sees it.'),
    ('10/11/00', 'Chat etiquette reminder',
     'Please do not type IN ALL CAPS in #Lobby. Please do not ask "a/s/l" in #Swing. Please do not paste '
     'the entire lyrics of anything, anywhere.'),
]

# ------------------------------------------------------------------ chat
CHANNELS = [
    ('Lobby', 'Welcome to Snapster! Be nice. No flooding. Snappy is watching.'),
    ('Rock', 'Rock talk. Flannel optional. Air guitar mandatory.'),
    ('Hip-Hop', 'Shouts to the sysops. Two-way pagers welcome.'),
    ('Electronica', 'Big beat, techno, trip-hop. BPM > 120 please.'),
    ('Ska', 'Pick it up! Checkered shoes at the door.'),
    ('Swing', 'Jump, jive and wail. Khakis encouraged.'),
    ('Y2K', 'Y2K happened. Nothing happened. Bob is still in the bunker.'),
    ('Help', 'Snapster help channel. Read the FAQ first, please, we beg you.'),
]

CHAT = {
    'Lobby': {
        'users': ['Snappy_Bot', 'DormRoomDJ', 'glitterpen_jen', 'DialUpDiva4eva', 'b0rk_b0rk', 'newbie_ned',
                  'daytrader_dan', 'Furbee_Hacker', ME],
        'log': [
            '*** Now talking in #Lobby',
            '*** Topic is: Welcome to Snapster! Be nice. No flooding. Snappy is watching.',
            '<Snappy_Bot> Welcome to #Lobby! Type /help for help. Type /hlep for nothing.',
            '<glitterpen_jen> hi everyone!!! :)',
            '<DialUpDiva4eva> HI JEN!!!!!',
            '<b0rk_b0rk> caps lock is cruise control for cool',
            '<DialUpDiva4eva> sorry my kid brother changed something',
            '<newbie_ned> how do i download the internet',
            '<DormRoomDJ> ned you need a bigger hard drive. at least 10 GB',
            '<newbie_ned> i have 2.1 GB is that enough',
            '<daytrader_dan> sold my SNAPPY puts. bought SNAPPY calls. this chat is my office now',
            '*** Furbee_Hacker has joined #Lobby',
            '<Furbee_Hacker> my furbee learned to say "buffer underrun". proud parent moment',
        ],
        'script': [
            '<glitterpen_jen> anyone else\'s download stuck at 99%?',
            '<b0rk_b0rk> the last 1% is the hardest. like a marathon',
            '<newbie_ned> ok i deleted windows to make room, brb',
            '*** newbie_ned has quit (Connection reset by peer)',
            '<DormRoomDJ> rip ned',
            '<DialUpDiva4eva> my mom needs the phone in 5 min. GET ALL THE SONGS',
            '<daytrader_dan> anyone know if Y2K affects mp3s? asking for my portfolio',
            '<Snappy_Bot> Reminder: Snapster does not condone deleting Windows.',
            '<Furbee_Hacker> furbee says "me love T1". me too furbee. me too',
            '*** DialUpDiva4eva has quit (Mom picked up the phone)',
            '<glitterpen_jen> she had 3 min left :(',
            '<b0rk_b0rk> F5 F5 F5 F5',
            '<DormRoomDJ> pro tip: rename your mp3s so your RA doesn\'t notice. i call mine "Calculus Notes"',
            '<glitterpen_jen> my calculus notes have a sick bassline',
            '*** newbie_ned has joined #Lobby',
            '<newbie_ned> windows is back. it says "press any key". where is the any key',
            '<Snappy_Bot> Snappy says: snap snap! (that means hi)',
        ]},
    'Rock': {
        'users': ['xXdarkangelXx', 'nu_metal_nate', 'ftp_phil', 'llama_whipper', 'quake_clan_leader', ME],
        'log': [
            '*** Now talking in #Rock',
            '*** Topic is: Rock talk. Flannel optional. Air guitar mandatory.',
            '<nu_metal_nate> Limp Noodle Theory live = best concert of my LIFE',
            '<xXdarkangelXx> they played Red Cap of Rage for 14 minutes',
            '<ftp_phil> 13 of those minutes were the singer adjusting his hat',
            '<llama_whipper> anybody have Shiny Metallic Things - Napkin of Doom at 192?',
            '<quake_clan_leader> you can\'t. they emailed everyone. personally. with a lawyer',
            '<xXdarkangelXx> i got a letter. it was on very nice paper',
        ],
        'script': [
            '<nu_metal_nate> nu-metal is just metal that owns a skateboard',
            '<ftp_phil> flannel is back. flannel never left. flannel is eternal',
            '<llama_whipper> playing it really loud on my mp3 player right now',
            '<xXdarkangelXx> Fade to Beige is the saddest song ever written. about a wall',
            '*** quake_clan_leader has quit (rocket jump)',
            '<nu_metal_nate> my mom says drop D is "just a phase". MOM IT IS A TUNING',
            '<ftp_phil> just downloaded a 22 minute jam band track by accident. still going',
            '<llama_whipper> lol its the tuning jam. thats the whole song',
            '<xXdarkangelXx> rock is not dead. it is just buffering',
            '*** quake_clan_leader has joined #Rock',
            '<quake_clan_leader> back. what did i miss',
            '<nu_metal_nate> nothing. we are still waiting for the guitar solo to download',
        ]},
    'Hip-Hop': {
        'users': ['DormRoomDJ', 'mp3kid99', 'pentium3_paul', 'pogs_champion', 'MC_fan_2000', ME],
        'log': [
            '*** Now talking in #Hip-Hop',
            '*** Topic is: Shouts to the sysops. Two-way pagers welcome.',
            '<DormRoomDJ> MC Dial-Up dropped a new one. "Shout Out to My Sysop". instant classic',
            '<pentium3_paul> his flow is 56 kbps but it feels like 128',
            '<mp3kid99> Lil\' Pager - Pager Code 143 is my whole personality',
            '<pogs_champion> what does 143 mean',
            '<mp3kid99> I. LOVE. YOU. (in pager)',
            '<pogs_champion> oh. ok. 143 to you too i guess',
        ],
        'script': [
            '<MC_fan_2000> who got that Bling Bling Calculator at 160',
            '<DormRoomDJ> check my share. alphabetized. color coded. no RA can stop me',
            '<pentium3_paul> just got a two-way pager. i have nobody to page. paging myself',
            '<pogs_champion> 143 paul',
            '<pentium3_paul> 143 pogs',
            '<mp3kid99> "Straight Outta Cul-de-sac" is so real. my street ends in a circle',
            '<MC_fan_2000> anyone going to the open mic at the food court saturday',
            '<DormRoomDJ> only if they let me bring my 2 turntables and my 1 microphone and my 3 extension cords',
            '*** pogs_champion has quit (slammed)',
            '<pentium3_paul> he got slammed. respect',
            '<mp3kid99> throw your hands up!',
            '<MC_fan_2000> ...and then put them back down, per the song',
        ]},
    'Electronica': {
        'users': ['b0rk_b0rk', 'BigBeatBen', 'RedPillBluePill', '[phreak]0ut', 'trip_hop_tina', ME],
        'log': [
            '*** Now talking in #Electronica',
            '*** Topic is: Big beat, techno, trip-hop. BPM > 120 please.',
            '<BigBeatBen> Captain Bigbeat & the Vinyl Squad - The Bassline Is a Lie. the bassline is NOT a lie',
            '<b0rk_b0rk> it IS a lie that is the point ben',
            '<trip_hop_tina> anything under 90 bpm in here or am i in the wrong room',
            '<[phreak]0ut> DJ Dialtone sampled my actual modem. i want royalties',
            '<RedPillBluePill> there is no modem',
        ],
        'script': [
            '<trip_hop_tina> Bristol Fog Machine makes me want to stare out a rainy window in a nice coat',
            '<b0rk_b0rk> glowsticks: ordered. 500 of them. dorm room will look like a submarine',
            '<BigBeatBen> breaks for breakfast. beats for brunch. bass for lunch',
            '<[phreak]0ut> fun fact: "Handshake (56K Mix)" is just 6 minutes of BEEEE-KSSHHHH',
            '<RedPillBluePill> i know kung fu. and also how to set up a playlist',
            '<trip_hop_tina> Porthole Mood - Sad Robot Lounge at 3am is a spiritual experience',
            '*** b0rk_b0rk has quit (Ping timeout)',
            '<BigBeatBen> ping timeout. the most electronic way to leave',
            '<[phreak]0ut> Y2K Bug Collective - Midnight Rollover is exactly 10 minutes so you can time it',
            '*** b0rk_b0rk has joined #Electronica',
            '<b0rk_b0rk> my roommate unplugged the router to charge his keychain pet',
        ]},
    'Ska': {
        'users': ['ska_dad_mike', 'sk8rkev', 'kazoo_kid', 'checkered_shoes', ME],
        'log': [
            '*** Now talking in #Ska',
            '*** Topic is: Pick it up! Checkered shoes at the door.',
            '<ska_dad_mike> third wave never died. it just went to work at a bank',
            '<kazoo_kid> The Upstroke Accountants - Spreadsheet Skank. finally ska for professionals',
            '<sk8rkev> is a kazoo a horn section',
            '<kazoo_kid> it is if you believe',
        ],
        'script': [
            '<ska_dad_mike> picking it up',
            '<checkered_shoes> picking it up',
            '<kazoo_kid> picking it up',
            '<sk8rkev> putting it down (my mom said so)',
            '<ska_dad_mike> Checkerboard Tuxedo Revue opened for a swing band last night. it was a suspender riot',
            '<kazoo_kid> they had 9 trombones. on a stage built for 2',
            '<checkered_shoes> Trombone Emergency is about that exact night',
            '*** sk8rkev has quit (Mom picked up the phone)',
            '<ska_dad_mike> every time',
            '<kazoo_kid> RIP kev. pick it up kev. wherever you are',
        ]},
    'Swing': {
        'users': ['swinggirl76', 'daytrader_dan', 'IEisBetter', 'bondi_blue_betty', ME],
        'log': [
            '*** Now talking in #Swing',
            '*** Topic is: Jump, jive and wail. Khakis encouraged.',
            '<swinggirl76> anyone have The Cherry Lounge Hepcats - Khakis Commercial Blues?',
            '<IEisBetter> it is literally 2 min 38 sec of dancing in pants',
            '<daytrader_dan> Swing Shift Mortgage Brokers are the only band my broker likes',
            '<bondi_blue_betty> my zoot suit is on layaway, just like the song',
        ],
        'script': [
            '<swinggirl76> lindy hop lessons thursday at the rec center. bring a partner or a sturdy chair',
            '<daytrader_dan> "Hep to the Interest Rate" is about a fixed 30-year. very moving',
            '<IEisBetter> my browser renders swing music 4% faster',
            '<bondi_blue_betty> my computer is translucent and so is my love for big bands',
            '<swinggirl76> anybody got 160 kbps of Martini Emergency, the 128 has a skip',
            '<daytrader_dan> buy low, swing high',
            '*** IEisBetter has quit (Illegal operation)',
            '<bondi_blue_betty> his browser performed an illegal operation and will be shut down',
            '<swinggirl76> daddy-o down',
        ]},
    'Y2K': {
        'users': ['y2k_bunker_bob', 'keychainpet_ghost', 'paperclip_fan', 'FrondPilotPete', ME],
        'log': [
            '*** Now talking in #Y2K',
            '*** Topic is: Y2K happened. Nothing happened. Bob is still in the bunker.',
            '<y2k_bunker_bob> day 296 in the bunker. 312 cans of beans left. 1 copy of Canned Goods Stomp',
            '<FrondPilotPete> bob it is october. the computers are fine',
            '<paperclip_fan> It looks like you\'re still preparing for the apocalypse. Would you like help?',
            '<y2k_bunker_bob> yes paperclip. yes i would',
        ],
        'script': [
            '<keychainpet_ghost> my keychain pet died at 11:59 on new years eve. so SOMETHING happened',
            '<FrondPilotPete> my VCR still blinks 12:00. but now it is a 2000-compliant 12:00',
            '<y2k_bunker_bob> what if the bug is just running late. like a train',
            '<paperclip_fan> It looks like you\'re waiting for a bug. Would you like to save your work?',
            '<y2k_bunker_bob> 2001 is the REAL millennium. i read it on a newsgroup. staying put',
            '*** y2k_bunker_bob has quit (going to the bunker)',
            '<FrondPilotPete> he will be back in 5 min. the bunker has no outlet',
            '*** y2k_bunker_bob has joined #Y2K',
            '<y2k_bunker_bob> the bunker has no outlet',
        ]},
    'Help': {
        'users': ['Snappy_Bot', 'Helper_Hank', 'newbie_ned', 'geohoods_gwen', ME],
        'log': [
            '*** Now talking in #Help',
            '*** Topic is: Snapster help channel. Read the FAQ first, please, we beg you.',
            '<newbie_ned> my download says "Remote user cancelled" what did i do',
            '<Helper_Hank> nothing ned. they cancelled. it is in the name',
            '<newbie_ned> should i call them',
            '<Helper_Hank> please do not call them',
        ],
        'script': [
            '<geohoods_gwen> how do i put a snapster link on my homepage? it is in the Area 51 neighborhood',
            '<Helper_Hank> just link to the download page. also add a guestbook, legally required in 1999',
            '<newbie_ned> what does "Firewalled" mean',
            '<Helper_Hank> it means your computer has trust issues',
            '<Snappy_Bot> FAQ: www dot snapster dot com slash help. Or click the Help tab. Or ask Hank.',
            '<newbie_ned> hank are you a robot',
            '<Helper_Hank> i am a sophomore',
            '<geohoods_gwen> my hit counter says 000014. 13 of them are me',
            '<Helper_Hank> that is a very normal hit counter',
        ]},
}

CHAT_LINES_YOU = ['snap snap', 'lol', 'brb modem is screaming', 'a/s/l? jk jk']
