# -*- coding: utf-8 -*-
"""All the invented content for CNM Interactive (December 20, 1999).

Stories live in stories_a..d.py (one S(...) call each); this module gathers them and holds
the front-page odds and ends: breaking news, TV schedule, QuickVote, markets, weather,
quiz, almanac, related-site pools and banner ads.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stories_a, stories_b, stories_c, stories_d

TODAY = "December 20, 1999"
UPDATED = "Updated 3:52 p.m. EST (2052 GMT)"

# code, nav label, directory, title-graphic text, short blurb for the section front
SECTIONS = [
    ("WORLD",    "WORLD",         "WORLD",       "WORLD",          "News from every corner of the globe, including several corners we invented."),
    ("US",       "U.S.",          "US",          "U.S. NEWS",      "From Port Halloway to Dry Spoon: the nation's news."),
    ("WEATHER",  "WEATHER",       "WEATHER",     "WEATHER",        "Storms, forecasts and the occasional La Nada."),
    ("BUSINESS", "BUSINESS",      "BUSINESS",    "BUSINESS",       "Markets, money and companies that sell potatoes on the Internet."),
    ("SPORTS",   "SPORTS",        "SPORTS",      "SPORTS",         "Scores, standings and mascot misconduct."),
    ("TECH",     "SCI-TECH",      "TECH",        "SCI-TECH",       "Computers, the Internet, space -- and the Bug."),
    ("SHOWBIZ",  "ENTERTAINMENT", "SHOWBIZ",     "ENTERTAINMENT",  "Movies, music, television and dancing rodents."),
    ("POLITICS", "POLITICS",      "POLITICS",    "POLITICS",    "The race for 2000, and everything else under the Capitol dome."),
    ("LAW",      "LAW",           "LAW",         "LAW",            "Courts, crime and the legal side of the millennium."),
    ("HEALTH",   "HEALTH",        "HEALTH",      "HEALTH",         "Medicine, fitness, and what your mouse is doing to your elbow."),
    ("TRAVEL",   "TRAVEL",        "TRAVEL",      "TRAVEL",         "Where to go, how to get there and where to see the first sunrise."),
    ("FOOD",     "FOOD",          "FOOD",        "FOOD",           "Recipes, trends and an unapologetic defense of fruitcake."),
    ("STYLE",    "STYLE",         "STYLE",       "STYLE",          "Fashion, trends and the shiny future of party wear."),
]
SEC = dict((s[0], s) for s in SECTIONS)

STORIES = stories_a.STORIES + stories_b.STORIES + stories_c.STORIES + stories_d.STORIES
STORIES.sort(key=lambda s: (s["day"], s["hhmm"]), reverse=True)

TOP_STORY = "y2k.drill"
TOP_BULLETS = ["bug.fixers", "beans.stockpile", "y2k.anxiety", "airlines.newyear", "dow.record"]
IN_OTHER_NEWS = ["marisol.dateline", "noreaster", "ostravia.vote", "netspud.ipo", "granite.debate", "vellmark.canal"]
SPORTS_FRONT = ["lobstermen.win", "fruitcake.bowl", "curling.millennium"]
FEATURES = ["silver.lame", "pantry.gourmet", "first.light.tours", "thousandaire"]
VIDEO_STORY = "noreaster"

BREAKING = ("The Marisol Islands parliament has voted to shift the international date line a second time "
            "this year; the Kingdom of Tavai says it will respond \"at the appropriate time.\"")

TV = [  # time, show
    ("Noon", "Midday Report: Final Y2K drill results"),
    ("3 p.m.", "Talk Back Alive: Are you ready for 2000?"),
    ("7 p.m.", "Money Minute: NetSpud.com and the potato bubble"),
    ("10 p.m.", "Weekend Wrap: Nor'easter clean-up in Maine"),
]

MARKETS = [  # name, value, change, up?
    ("DJIA", "11,257.43", "+112.40", True),
    ("NAS", "3,742.10", "+68.02", True),
    ("S&amp;P", "1,421.03", "-3.91", False),
]
MARKETS_TIME = "4:31pm ET, 12/20"

# ---------------------------------------------------------------- QuickVote
QUICKVOTE = dict(
    question="How will you spend the last night of 1999?",
    answers=["At a big millennium party", "At home with family and friends",
             "In my Y2K bunker with canned goods", "Watching my PC clock roll over",
             "Asleep. It's just another night."],
    votes=[4211, 9874, 1307, 2156, 3588],
)
QUICKVOTE_ARCHIVE = [
    ("December 17, 1999", "Would you buy shares in a company that sells potatoes online?",
     [("Yes, it's the future of potatoes", 1840), ("No, it's a bubble", 6122), ("Only if it splits", 933)]),
    ("December 15, 1999", "Have you finished your holiday shopping?",
     [("Yes, all online", 2210), ("Yes, at the mall", 1675), ("Not even started", 5302)]),
    ("December 13, 1999", "Is the new millennium beginning on January 1, 2000, or January 1, 2001?",
     [("2000 -- look at the odometer", 8817), ("2001 -- there was no year zero", 5530), ("I'm celebrating both", 2904)]),
    ("December 10, 1999", "Which browser are you using to read this?",
     [("Netscope Navigator", 4402), ("Internet Explorist", 6970), ("Something else entirely", 812)]),
    ("December 8, 1999", "Would you pay $2,500 for a robot dog?",
     [("Yes", 703), ("No", 9120), ("Only if it fetches the newspaper", 2265)]),
    ("December 6, 1999", "How fast is your Internet connection at home?",
     [("14.4 or slower", 1306), ("28.8 / 33.6", 5011), ("56K", 4380), ("Cable or DSL", 701)]),
    ("December 3, 1999", "Is fruitcake a food?",
     [("Yes, and a delicious one", 2988), ("No, it's a doorstop", 6477)]),
    ("December 1, 1999", "How much cash will you keep at home for Y2K?",
     [("None", 3870), ("Under $100", 3122), ("$100 to $500", 2005), ("All of it", 611)]),
]

# ---------------------------------------------------------------- weather
# city, state, icon, hi, lo, forecast, zip prefixes, map x,y (on 400x250 map)
WEATHER = [
    ("Port Halloway", "Maine", "snow", 22, 5, "Snow ending, then clearing and bitter cold", "0", (372, 48)),
    ("New Bramford", "Conn.", "cloud", 31, 18, "Cloudy and breezy, flurries late", "", (356, 78)),
    ("Gristmill Falls", "Ohio", "partly", 34, 21, "Partly sunny, chilly", "4", (290, 92)),
    ("Halcyon Springs", "Fla.", "sun", 78, 61, "Sunny and pleasant", "3", (322, 212)),
    ("Saint Ulric", "La.", "rain", 64, 52, "Showers and a few thunderstorms", "7", (248, 192)),
    ("Lake Wendell", "Minn.", "snow", 15, -4, "Light snow, blowing and drifting", "5", (222, 52)),
    ("Bellwether", "Iowa", "cloud", 27, 12, "Mostly cloudy, cold", "", (226, 92)),
    ("Cotterville", "Kan.", "partly", 38, 19, "Partly cloudy, windy", "6", (192, 126)),
    ("Cedar Notch", "Colo.", "snow", 29, 8, "Snow showers in the mountains", "8", (142, 112)),
    ("Dry Spoon", "Ariz.", "sun", 66, 39, "Sunny and mild", "", (96, 168)),
    ("Twin Forks", "Mont.", "storm", 18, 2, "Windy with snow squalls", "", (118, 46)),
    ("Mossbank", "Ore.", "rain", 47, 39, "Rain, heavy at times", "9", (30, 56)),
]
WEATHER_INTL = [
    ("Saint Ambrose", "Marisol Islands", "sun", 86, 75),
    ("Velkograd", "Ostravia", "snow", 19, 6),
    ("Lornswick", "Esterhaal", "rain", 44, 37),
    ("Puerto Caldera", "Vellmark", "storm", 88, 74),
    ("Bruskholm", "Lower Bruskia", "cloud", 33, 25),
    ("Port Sabrino", "Tamberlay", "partly", 71, 60),
]

# ---------------------------------------------------------------- news quiz
# question, choices, index of right answer, story slug
QUIZ = [
    ("Which country moved the international date line for a second time this year?",
     ["Ostravia", "The Marisol Islands", "Lower Bruskia", "Vellmark"], 1, "marisol.dateline"),
    ("What does NetSpud.com plan to sell over the Internet?",
     ["Potatoes", "Spatulas", "Potato-shaped mouse pads", "Nothing; it is a portal"], 0, "netspud.ipo"),
    ("During Monday's Y2K drill, which device in Gristmill Falls believed it was 1900?",
     ["A traffic light", "A turbine", "A coffee maker", "The mayor's pager"], 2, "y2k.drill"),
    ("How long is Lower Bruskia's record millennium cake?",
     ["300 feet", "1 mile", "3.1 miles", "As long as Upper Bruskia's"], 2, "bruskia.cake"),
    ("What is the top prize on 'Who Wants to Be a Thousandaire?'",
     ["$1,000 and a mug", "$1 million", "A thousand potatoes", "A Robo-Rover"], 0, "thousandaire"),
    ("How did the Kingdom of Tavai become Y2K compliant?",
     ["It bought a new mainframe", "It unplugged its only government computer", "It skipped the year 2000", "It hired retired COBOL programmers"], 1, "tavai.bug"),
    ("What did candidate Rex Ambergast display during his 30-minute broadcast?",
     ["A pressure cooker", "Steak knives", "A Plushie Pals walrus", "A hamster"], 1, "ambergast.ads"),
    ("Why did a Saint Ulric man sue his VCR's manufacturer?",
     ["It ate his tapes", "It recorded the wrong show", "Its clock has blinked 12:00 for six years", "It is not Y2K compliant"], 2, "vcr.lawsuit"),
    ("How many cans of beans fill Walt Brunheimer's garage, basement and guest room?",
     ["400", "1,999", "4,000", "2 million"], 2, "beans.stockpile"),
    ("What did forecasters name this winter's neutral Pacific pattern?",
     ["El Nino", "La Nina", "La Nada", "El Bug"], 2, "la.nada"),
]

# ---------------------------------------------------------------- daily almanac
ALMANAC = dict(
    day="Monday, December 20, 1999",
    dayno="354th day of 1999; 11 days remain in the year, the century and (depending on whom you ask) the millennium.",
    sun="Sunrise in Port Halloway, Maine: 7:09 a.m. Sunset: 3:58 p.m.",
    moon="Moon: Waxing gibbous, full on December 22 -- the brightest December full moon in 133 years, according to the Lake Wendell Astronomy Club.",
    history=[
        ("1803", "The town of Port Halloway, Maine, is incorporated; its first ordinance bans lobsters from the town green."),
        ("1887", "The Lake Wendell town hall clock is wound for the first time. It has never displayed the year."),
        ("1921", "The first transcontinental yodeling contest is held by telephone; the operator in Cotterville, Kansas, declares a tie."),
        ("1958", "Dry Spoon, Arizona, records a high of 79 degrees, a record that stood until December 9 of this year."),
        ("1971", "Construction begins on the Velkograd ring road in Ostravia. Completion is expected shortly."),
        ("1985", "The first Plushie Pal, a brown bear named Mortimer, goes on sale for $4.99."),
        ("1996", "A Gristmill Falls programmer notices that his payroll system thinks the year 2000 will be 1900. He mentions it at lunch."),
    ],
    birthdays=[
        "Monty Vance, game-show host, 58",
        "Gunnar Halvorsen, curling skip, 47",
        "Odette Fontenot, fruitcake defender, 64",
        "Tater Tim, animated potato, 1",
    ],
    quote=("\"We didn't think anyone would still be using this in 2000.\"", "-- retired programmer Harold Snedeker, on his 1970s COBOL code"),
    number=("4,000", "cans of beans in one Cotterville, Kansas, guest room"),
)

# ---------------------------------------------------------------- related sites
# (label, kind, target): kind "ring" -> other 1999 Web site folder; "self" -> path from site root
RELATED_SITES = {
    "WORLD":    [("Marisol Islands Tourism Board", "self", "TRAVEL/index.html"), ("AltaVisor: search the world", "ring", "altavisor"), ("GeoHoods: home pages from 40 countries", "ring", "geohoods")],
    "US":       [("Yowza! Regional directory", "ring", "yowza"), ("GeoHoods Main Street", "ring", "geohoods"), ("CNM Y2K Special Report", "self", "y2k/index.html")],
    "WEATHER":  [("CNM Weather forecasts", "self", "weather.html"), ("Ask Reeves: Will it snow?", "ring", "askreeves"), ("GeoHoods: storm chasers' home pages", "ring", "geohoods")],
    "BUSINESS": [("Orinoco.com", "ring", "orinoco"), ("uBid auctions", "ring", "ubid"), ("eToyz.com", "ring", "etoyz"), ("Petz.com", "ring", "petz")],
    "SPORTS":   [("Yowza! Sports", "ring", "yowza"), ("uBid: sports memorabilia", "ring", "ubid"), ("CNM Weather", "self", "weather.html")],
    "TECH":     [("DashDot: news for geeks", "ring", "dashdot"), ("Snapster", "ring", "snapster"), ("AltaVisor search", "ring", "altavisor")],
    "SHOWBIZ":  [("The Hamster Shuffle", "ring", "hamstershuffle"), ("Snapster", "ring", "snapster"), ("Orinoco.com: music and video", "ring", "orinoco")],
    "POLITICS": [("CNM QuickVote archive", "self", "quickvote_archive.html"), ("Yowza! Politics", "ring", "yowza"), ("Ask Reeves: Who is running?", "ring", "askreeves")],
    "LAW":      [("Ask Reeves: legal questions", "ring", "askreeves"), ("DashDot: tech law threads", "ring", "dashdot"), ("CNM Y2K Special Report", "self", "y2k/index.html")],
    "HEALTH":   [("Ask Reeves: health questions", "ring", "askreeves"), ("Petz.com: pet health", "ring", "petz"), ("GeoHoods: support groups", "ring", "geohoods")],
    "TRAVEL":   [("CNM Weather around the world", "self", "weather.html"), ("Yowza! Travel", "ring", "yowza"), ("Millennium celebrations", "self", "y2k/celebrations.html")],
    "FOOD":     [("Orinoco.com: cookbooks", "ring", "orinoco"), ("GeoHoods: family recipe pages", "ring", "geohoods"), ("Are you ready? Y2K checklist", "self", "y2k/ready.html")],
    "STYLE":    [("eToyz.com", "ring", "etoyz"), ("GeoHoods: fashion home pages", "ring", "geohoods"), ("uBid: vintage clothing", "ring", "ubid")],
}

# banner ads: image, link kind, target, alt
BANNERS = [
    ("ad_ubid.gif", "ring", "ubid", "uBid: bid on Y2K survival gear"),
    ("ad_orinoco.gif", "ring", "orinoco", "Orinoco.com: millennium gift books"),
    ("ad_snapster.gif", "ring", "snapster", "Snapster: share your music"),
    ("ad_altavisor.gif", "ring", "altavisor", "AltaVisor: find it faster"),
]

RING = "yowza altavisor askreeves orinoco ubid etoyz petz geohoods hamstershuffle dashdot snapster cnm".split()
