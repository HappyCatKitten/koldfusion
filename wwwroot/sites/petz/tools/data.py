# -*- coding: utf-8 -*-
"""Invented data for Petz.com (a 1999 Web parody). Everything here is fiction."""

SITE_TITLE = "Petz.com"
MASCOT = "Argyle"
MASCOT_FULL = "Argyle the Sock Dog"
VET = "Dr. Bea Woofington, DVM"

# Category id -> (page, label, header gif base, tagline)
CATEGORIES = [
    ("dogs",      "Dogs",       "Everything your dog needs, delivered by a man in shorts.",
     "Dog Food, Toys &amp; Gear"),
    ("cats",      "Cats",       "Your cat will ignore all of it. But it will arrive tomorrow.",
     "Cat Food, Litter &amp; Toys"),
    ("fish",      "Fish",       "Aquariums, food and castles. Water sold separately (by the ocean).",
     "Aquariums &amp; Supplies"),
    ("birds",     "Birds",      "Cages, seed and swings for the songbird in your life.",
     "Cages, Seed &amp; Perches"),
    ("ferrets",   "Ferrets",    "For the weasel who has everything (because he stole it).",
     "Ferret Supplies"),
    ("reptiles",  "Reptiles",   "Heat lamps, rocks and crickets for cold-blooded customers.",
     "Heat, Habitat &amp; Food"),
    ("smallpets", "Small Pets", "Hamsters, gerbils, bunnies and guinea pigs. Wheels included.",
     "Small Pet Supplies"),
]

# Shipping one-liners (rotated through the products)
SHIP_JOKES = [
    "Yes, we lose money on that too.",
    "The truck alone costs more than this. We checked.",
    "Our accountant has asked us to stop saying this out loud.",
    "Shipped overnight from our warehouse, which is also losing money.",
    "That is not a typo. Neither is our quarterly report.",
    "Free if you live inside our warehouse.",
]

# Product records.
# id, cat, name, brand, list, price, ship (charged), cost (what we paid), realship (what UPS charged us),
# img: (kind, dict of options), blurb
P = []
def prod(pid, cat, name, brand, lst, price, ship, cost, realship, img, blurb, feature=False):
    P.append(dict(id=pid, cat=cat, name=name, brand=brand, list=lst, price=price, ship=ship,
                  cost=cost, realship=realship, img=img, blurb=blurb, feature=feature))

# ---------------- DOGS
prod("d01", "dogs", "Hearty Chunks Dog Food, 40 lb Bag", "Kibbleworks", 29.99, 18.99, 14.95, 24.10, 38.40,
     ("bag", dict(color=(178, 34, 34), band=(255, 204, 0), label="KIBBLE", sub="40 LB", animal="dog")),
     "Forty pounds of crunchy, beefy nuggets in a bag roughly the size of a sixth-grader. "
     "Our delivery driver asked us to mention that he has a bad back. We pay for his chiropractor too.",
     feature=True)
prod("d02", "dogs", "Indestructible Chew Bone (Medium)", "Chewbilee", 12.99, 4.99, 4.95, 7.80, 6.10,
     ("bone", dict(color=(255, 120, 40))),
     "Made from the same rubber compound as the tires on our delivery vans. "
     "Guaranteed to outlast your dog's interest, your couch, and possibly our company.")
prod("d03", "dogs", "Y2K-Compliant Squeaky Ball", "Bounce Bros.", 6.99, 1.99, 4.95, 3.20, 5.75,
     ("ball", dict(color=(0, 153, 255), stripe=(255, 255, 0), text="Y2K")),
     "Independently certified to keep squeaking after midnight on December 31, 1999. "
     "Our millennium team tested it on a golden retriever named Bug. Bug is fine. The ball is fine. "
     "Our servers are fine. Probably.")
prod("d04", "dogs", "Tug-O-Matic 3000 Rope Toy", "Knotworks", 9.99, 3.49, 4.95, 5.10, 5.90,
     ("rope", dict(color=(0, 102, 204), color2=(255, 51, 51))),
     "Three feet of braided cotton rope with a knot at each end and a dog at one of them. "
     "Engineered for tug-of-war. Your dog will win. Plan accordingly.")
prod("d05", "dogs", "Retractable Leash, 26 ft", "Fetchmaster", 24.99, 11.99, 6.95, 15.40, 7.20,
     ("leash", dict(color=(51, 153, 0))),
     "Twenty-six feet of freedom on a spring-loaded reel with a one-thumb brake. "
     "Long enough for your dog to visit the neighbors without technically leaving the yard.")
prod("d06", "dogs", "Memory-Foam Orthopedic Dog Bed (Large)", "Snoozehound", 89.00, 39.99, 34.95, 61.00, 72.80,
     ("bed", dict(color=(102, 51, 153), cushion=(204, 153, 255))),
     "Four inches of the same foam they put in astronaut mattresses (we are told). "
     "Ships in a box large enough to live in, which several of our warehouse employees do.")
prod("d07", "dogs", "Snuggle-Knit Dog Sweater, Dot-Com Teal", "Pawsh", 22.00, 7.95, 4.95, 11.50, 5.40,
     ("sweater", dict(color=(0, 153, 153), trim=(255, 255, 255))),
     "Hand-knit acrylic sweater in this season's hottest color, the exact teal of every "
     "startup logo in San Francisco. Sizes XS (chihuahua) through XXL (small pony).")

# ---------------- CATS
prod("c01", "cats", "Scoopable Cat Litter, 40 lb Bag", "ClumpKing", 12.99, 5.49, 14.95, 6.80, 41.25,
     ("bag", dict(color=(102, 102, 153), band=(255, 255, 255), label="LITTER", sub="40 LB", animal="cat")),
     "Forty pounds of premium clumping clay. It costs us $6.80 to buy and $41.25 to ship, and we sell it "
     "to you for $5.49. Our CFO calls this item 'the anchor.' He does not mean it in a nice way.",
     feature=True)
prod("c02", "cats", "Ocean Medley Cat Food, 24 Cans", "Purrfecta", 18.99, 9.99, 9.95, 13.20, 16.80,
     ("can", dict(color=(0, 102, 153), label="OCEAN", sub="24 CANS")),
     "Tuna, whitefish and something our supplier describes only as 'sea product.' "
     "Your cat will sniff it, walk away, and come back for it at 3 a.m.")
prod("c03", "cats", "Day-Trader Catnip Mouse", "Whiskerworks", 4.99, 0.99, 3.95, 2.10, 4.80,
     ("mouse", dict(color=(153, 153, 153), tie=(204, 0, 0))),
     "A felt mouse stuffed with organic catnip and wearing a tiny red power tie. "
     "Buys low, sells high, naps through the opening bell.")
prod("c04", "cats", "Kitty Skyscraper 6-ft Cat Tree", "Feline Towers", 149.00, 69.00, 49.95, 98.00, 124.00,
     ("cattree", dict(color=(204, 170, 120), carpet=(153, 102, 51))),
     "Six feet, four platforms, two condos and a penthouse with a view of your refrigerator. "
     "The tallest structure in your home that is not actually a skyscraper or our burn rate.")
prod("c05", "cats", "Sisal Scratching Post", "Sir Scratchalot", 29.99, 12.99, 9.95, 17.10, 14.20,
     ("post", dict(color=(222, 196, 140), base=(102, 51, 0))),
     "Thirty inches of tightly wound sisal rope on a weighted base. "
     "Studies show cats prefer it to your leather sofa nearly 4 percent of the time.")
prod("c06", "cats", "Laser Pointer 2000 with Millennium Mode", "Dot Chaser", 14.99, 4.99, 3.95, 7.75, 4.60,
     ("laser", dict(color=(51, 51, 51))),
     "A pocket laser that projects a red dot your cat will chase until one of you collapses. "
     "Millennium Mode makes the dot blink '2000.' Your cat cannot read. Ours either.")
prod("c07", "cats", "Hooded Litter Box, Executive Edition", "Privy Paws", 39.99, 17.99, 12.95, 24.50, 22.00,
     ("litterbox", dict(color=(153, 0, 51))),
     "A hooded litter box with a swinging door, a carbon filter and a little brass nameplate. "
     "Because your cat deserves a corner office.")

# ---------------- FISH
prod("f01", "fish", "AquaVista 55-Gallon Aquarium Kit", "AquaVista", 299.00, 149.00, 89.95, 210.00, 186.00,
     ("tank", dict(color=(51, 153, 255))),
     "Glass tank, hood, light, filter, heater, gravel and a little plastic diver. "
     "Weighs 78 pounds empty. We did briefly consider shipping it full. Legal said no.",
     feature=True)
prod("f02", "fish", "Classic Goldfish Bowl, 1 Gallon", "Glub", 14.99, 5.99, 7.95, 8.20, 11.40,
     ("bowl", dict(color=(153, 204, 255))),
     "The timeless round bowl. Packed in so many foam peanuts that you will be finding them until 2003.")
prod("f03", "fish", "Tropical Flake Food, 2 oz", "FinFeast", 5.49, 1.99, 3.95, 3.10, 4.40,
     ("can", dict(color=(255, 102, 0), label="FLAKES", sub="2 OZ")),
     "Colorful flakes with spirulina and krill. One pinch twice a day. "
     "Not the whole can. We know you were thinking about it.")
prod("f04", "fish", "Bubbling Treasure Chest Ornament", "Deep Thoughts", 9.99, 3.99, 4.95, 5.60, 5.30,
     ("chest", dict(color=(153, 102, 0))),
     "Connects to your air pump. Every few seconds the lid pops open and releases a stream of bubbles, "
     "just like our venture capital.")
prod("f05", "fish", "Bubble-Tron Air Pump", "Bubble-Tron", 19.99, 8.99, 5.95, 12.20, 6.80,
     ("pump", dict(color=(0, 102, 102))),
     "Whisper-quiet diaphragm pump for tanks up to 60 gallons. "
     "Quieter than a 56k modem handshake. Louder than a goldfish.")
prod("f06", "fish", "Fish Net, 4-inch", "Scoop-n-Swoosh", 3.99, 0.99, 3.95, 1.80, 4.50,
     ("net", dict(color=(0, 153, 0))),
     "Fine green mesh on a ten-inch handle. For catching fish, not for catching our losses. "
     "We have a much bigger net for that.")
prod("f07", "fish", "Moatsworth Aquarium Castle", "Deep Thoughts", 12.99, 4.99, 5.95, 7.40, 6.60,
     ("castle", dict(color=(170, 170, 170))),
     "A resin castle with three towers and an arched doorway big enough for a tetra. "
     "No drawbridge. The fish have asked.")

# ---------------- BIRDS
prod("b01", "birds", "Victorian Bird Cage", "Tweetopolis", 129.00, 59.99, 39.95, 84.00, 66.00,
     ("cage", dict(color=(204, 153, 0))),
     "Brass-finish dome cage with two feeders, two perches and a slide-out tray. "
     "Ships fully assembled in a box shaped exactly like a bird cage, which confuses the post office.",
     feature=True)
prod("b02", "birds", "Wild Bird Seed Mix, 25 lb", "SeedSational", 21.99, 8.99, 14.95, 12.30, 29.10,
     ("bag", dict(color=(51, 102, 0), band=(255, 255, 153), label="SEED", sub="25 LB", animal="bird")),
     "Millet, sunflower and safflower for every beak in the neighborhood. "
     "Twenty-five pounds, which is roughly a million meals for a finch.")
prod("b03", "birds", "Bird Mirror with Bell", "Mirror-Mirror", 6.99, 2.49, 3.95, 3.60, 4.20,
     ("mirror", dict(color=(255, 0, 102))),
     "Your budgie will spend hours chatting with the handsome stranger in this mirror. "
     "Like a chat room, but with fewer fake names.")
prod("b04", "birds", "Talking Bird Training Cassette", "Polly's Phrasebook", 12.99, 4.99, 3.95, 6.90, 4.10,
     ("cassette", dict(color=(255, 204, 0))),
     "Ninety minutes of patient repetition. Teaches your parrot to say 'Hello,' 'Pretty bird,' "
     "'Buy on the dip' and 'Your call is important to us.'")
prod("b05", "birds", "Cuttlebone Calcium Treat, 2-Pack", "Beakwell", 3.99, 0.99, 3.95, 2.20, 4.40,
     ("cuttlebone", dict(color=(255, 250, 230))),
     "Natural calcium for strong beaks. Clips right onto the cage. "
     "Shipping costs four times as much as the cuttlebone. We are aware.")
prod("b06", "birds", "Swing Time Perch Swing", "Tweetopolis", 7.99, 2.99, 3.95, 4.30, 4.70,
     ("swing", dict(color=(255, 51, 153))),
     "A wooden perch on a brass swing with three colored beads. Your cockatiel will swing on it, "
     "sing on it, and then throw seed hulls at you from it.")
prod("b07", "birds", "Backyard Bird Bath", "Featherlite", 11.99, 4.49, 9.95, 6.80, 15.30,
     ("birdbath", dict(color=(153, 204, 204))),
     "Lightweight resin bird bath on a fluted pedestal. Looks like stone. Weighs less than stone. "
     "Costs more to ship than stone.")

# ---------------- FERRETS
prod("fe01", "ferrets", "Slinky Sleeper Ferret Hammock", "Weaselworks", 19.99, 7.99, 4.95, 11.20, 5.80,
     ("hammock", dict(color=(204, 0, 0), color2=(255, 255, 255))),
     "A fleece hammock that clips to any cage. Ferrets sleep up to 18 hours a day, "
     "so this is technically their office.")
prod("fe02", "ferrets", "Crinkle Tunnel, 6 ft", "Tunnel Vision", 14.99, 5.99, 4.95, 8.30, 5.60,
     ("tube", dict(color=(255, 153, 0))),
     "Six feet of collapsible, crinkly nylon tunnel. Your ferret will dive in, dook happily, "
     "and emerge with one of your socks. We do not know where the socks come from either.")
prod("fe03", "ferrets", "Weasel Wonderland 3-Story Ferret Condo", "Weaselworks", 199.00, 89.00, 59.95, 132.00, 118.00,
     ("cage", dict(color=(80, 80, 80), tall=True)),
     "Three levels, two ramps, a litter corner and a front door wide enough for a ferret and a stolen sock. "
     "Our biggest seller among people who own ferrets and also our biggest loss among everyone.",
     feature=True)
prod("fe04", "ferrets", "Ferret Kibble, 10 lb", "Dook Dook", 24.99, 11.99, 9.95, 16.40, 14.30,
     ("bag", dict(color=(255, 102, 0), band=(255, 255, 255), label="FERRET", sub="10 LB", animal="ferret")),
     "High-protein, high-fat kibble for an animal that runs at full speed until it falls asleep mid-hop.")
prod("fe05", "ferrets", "Ferret-Proof Sock Safe", "Weaselworks", 16.99, 6.99, 5.95, 9.40, 7.10,
     ("safe", dict(color=(102, 102, 102))),
     "A locking steel box for your socks. Ferrets hoard socks. This keeps your socks safe. "
     "It is also where we keep our mascot overnight.")
prod("fe06", "ferrets", "Low-Musk Ferret Shampoo, 8 oz", "Bandit's Bath", 8.99, 3.49, 3.95, 5.10, 4.40,
     ("bottle", dict(color=(102, 204, 102), label="BANDIT")),
     "Gentle tearless formula that leaves your ferret smelling like a meadow for nearly twenty minutes.")

# ---------------- REPTILES
prod("rp01", "reptiles", "Basking Heat Lamp, 150 Watt", "SunBeam", 34.99, 14.99, 7.95, 21.50, 9.30,
     ("lamp", dict(color=(153, 153, 153))),
     "A ceramic socket, a reflector dome and a 150-watt bulb that turns any corner of the tank into Arizona. "
     "Your electric company sends its regards.",
     feature=True)
prod("rp02", "reptiles", "Desert Oasis 20-Gallon Terrarium", "Scaletown", 89.99, 39.99, 44.95, 58.00, 77.00,
     ("terrarium", dict(color=(204, 153, 102))),
     "Glass terrarium with a locking screen lid, sand, a fake cactus and a rock with a hollow under it "
     "for hiding. Not unlike our CFO's office.")
prod("rp03", "reptiles", "Live Crickets, 500 Count", "Chirpco", 15.99, 6.99, 24.95, 9.10, 44.50,
     ("crickets", dict(color=(102, 153, 51))),
     "Five hundred live crickets shipped overnight in a ventilated box. Some assembly required. "
     "Some escape. Our Indianapolis warehouse chirps at night now.")
prod("rp04", "reptiles", "Iguana Lounge Climbing Branch", "Scaletown", 12.99, 4.99, 6.95, 7.20, 8.80,
     ("branch", dict(color=(102, 51, 0))),
     "A sanded, sealed grapevine branch for climbing, basking and looking unimpressed.")
prod("rp05", "reptiles", "Hot Rock Deluxe Heated Stone", "SunBeam", 24.99, 9.99, 6.95, 14.30, 8.10,
     ("hotrock", dict(color=(153, 136, 119))),
     "A resin rock with a built-in heating element. Looks like a rock. Feels like a warm rock. "
     "Is a rock. Our most honest product.")
prod("rp06", "reptiles", "Humidity Mister", "Shed Happens", 19.99, 7.99, 5.95, 11.60, 6.90,
     ("bottle", dict(color=(0, 153, 204), label="MIST")),
     "A pump-action mister for keeping your gecko's skin supple and your windows foggy.")

# ---------------- SMALL PETS
prod("sp01", "smallpets", "Spin Cycle 8-inch Hamster Wheel", "Rodentronics", 14.99, 5.99, 4.95, 8.40, 5.70,
     ("wheel", dict(color=(0, 153, 255))),
     "Silent-spinner wheel with a solid running surface. Your hamster will run all night and get nowhere, "
     "which our investors tell us is a perfectly valid business model.",
     feature=True)
prod("sp02", "smallpets", "Timothy Hay, 10 lb Bale", "Haystack Farms", 16.99, 6.99, 14.95, 9.80, 31.60,
     ("hay", dict(color=(204, 204, 102))),
     "Sun-cured second-cut timothy hay for rabbits, guinea pigs and chinchillas. "
     "Ten pounds of hay in a box the size of a dishwasher.")
prod("sp03", "smallpets", "Drip-Free Water Bottle, 16 oz", "Rodentronics", 5.99, 1.99, 3.95, 3.10, 4.40,
     ("waterbottle", dict(color=(0, 153, 255))),
     "A clear bottle with a stainless sipper tube and a ball valve. Drip-free, unlike our cash flow.")
prod("sp04", "smallpets", "Hamster Hacienda Habitat", "Rodentronics", 39.99, 15.99, 12.95, 24.20, 21.80,
     ("habitat", dict(color=(255, 102, 0))),
     "Plastic habitat with a sleeping loft, a wheel, a spiral slide and a tube that leads to a little "
     "rooftop observation deck. Nicer than most dot-com office space.")
prod("sp05", "smallpets", "Bunny Bungalow Wooden Hutch", "Haystack Farms", 79.99, 34.99, 39.95, 52.00, 68.40,
     ("hutch", dict(color=(153, 102, 51))),
     "A two-story cedar hutch with a ramp, a wire run and a shingled roof. "
     "Several of our programmers have asked whether it comes in a human size.")
prod("sp06", "smallpets", "Chew Sticks, 12 Pack", "Gnaw-Some", 4.99, 1.49, 3.95, 2.40, 4.10,
     ("sticks", dict(color=(204, 153, 102))),
     "Natural apple-wood sticks for keeping little teeth trim. Far cheaper than your phone cord.")
prod("sp07", "smallpets", "Guinea Pig Party Hats, Set of 3", "Wheek!", 7.99, 2.99, 3.95, 4.10, 4.60,
     ("hats", dict(color=(255, 0, 153))),
     "Three tiny cardboard party hats with elastic chin straps. For birthdays, New Year's Eve 1999, "
     "and our next round of financing.")

# ---------------- MASCOT MERCHANDISE
prod("m01", "mascot", "Argyle the Sock Dog Plush Puppet", "Petz.com", 19.99, 9.99, 4.95, 14.00, 5.60,
     ("puppet", dict()),
     "The official 18-inch Argyle, with button eyes, a stitched felt mouth and a genuine twist-tie bow tie. "
     "Fits any human hand. It costs us fourteen dollars to make and we sell it for $9.99. "
     "Argyle says this is fine. Argyle is a sock.", feature=True)
prod("m02", "mascot", "Argyle 'Pets Can't Drive' Coffee Mug", "Petz.com", 12.99, 4.99, 5.95, 7.20, 7.80,
     ("mug", dict(color=(153, 204, 51))),
     "Eleven-ounce ceramic mug with Argyle on one side and our slogan on the other. "
     "Holds enough coffee for one board meeting.")
prod("m03", "mascot", "Argyle Commemorative T-Shirt", "Petz.com", 18.00, 5.00, 4.95, 7.90, 5.10,
     ("shirt", dict(color=(153, 204, 51))),
     "100 percent cotton, heavyweight, one size fits most. "
     "Front: Argyle. Back: 'I WAS THERE (AT THE LAUNCH PARTY)'.")

BY_ID = dict((p["id"], p) for p in P)

def loss(p):
    """What Petz.com loses on one unit (always positive, of course)."""
    return round(p["cost"] + p["realship"] - p["price"] - p["ship"], 2)

# ---------------- TODAY'S FEATURES (left column)
FEATURES = [
    ("Puppy Love, Online", "Is your pug ready for e-dating?", "feature_1.html"),
    ("Is Your Cat Y2K Ready?", "Stock up on litter before the clocks roll", "feature_2.html"),
    ("The 56k Hamster", "One rodent, one wheel, one tiny ISP", "feature_3.html"),
    ("Our Super Bowl Ad", "Thirty seconds, two million dollars, one sock", "superbowl.html"),
    ("Meet Argyle", "The sock that launched a thousand shipments", "mascot.html"),
    ("Ask the Vet", "Dr. Woofington answers your letters", "advice.html"),
    ("Sock Thieves", "Why does my ferret do that?", "advice_5.html"),
    ("Investor Relations", "Our stock only goes up. Ask anyone.", "investor.html"),
]

FEATURE_PAGES = {
 1: ("Puppy Love, Online", "Is your pug ready for e-dating?", "dog", [
  "It used to be that a dog met other dogs the old-fashioned way: at the park, nose first. "
  "But this is 1999, and the information superhighway has an off-ramp for everybody. "
  "This spring a handful of new web sites began offering personal ads for pets, complete with "
  "scanned photos, favorite chew toys and a little box to check if you are 'looking for a playmate' "
  "or 'just looking.'",
  "We talked to Marge Pumpernickel of Spokane, Washington, whose pug Doodle has been 'online' since March. "
  "\"He's had three dates,\" she told us. \"One of them was a cat. The photo was blurry. We think the "
  "cat's owner did it on purpose.\"",
  "Our advice? Meet in a public place, like a park or a pet store. Bring a leash. Let your dog sniff first "
  "and ask questions later. And never, ever give out your dog's home address in a chat room. "
  "That is how Doodle ended up with a pen pal who is a goat.",
  "<B>Petz Picks for the First Date:</B> a fresh <A HREF=\"product_d07.html\">Dot-Com Teal sweater</A>, "
  "a <A HREF=\"product_d03.html\">Y2K-compliant ball</A> to break the ice, and a "
  "<A HREF=\"product_d05.html\">26-foot leash</A> in case things go really well.",
 ]),
 2: ("Is Your Cat Y2K Ready?", "Stock up on litter before the clocks roll", "cat", [
  "With fewer than two hundred days left until the year 2000, every bank, airline and power company in "
  "America is busy checking its computers. But who is checking your cat?",
  "The good news: cats do not contain any two-digit date fields. Our engineering staff spent three weekends "
  "confirming this using a tabby named Pixel and a borrowed oscilloscope. Pixel is fully compliant. "
  "The oscilloscope has been reported missing.",
  "The bad news: if the trucks stop running on January 1, you could be facing a litter situation. "
  "That is why Petz.com recommends a 'millennium stockpile' of at least one month of food, water and "
  "<A HREF=\"product_c01.html\">40-pound bags of litter</A>. Yes, we lose about forty dollars on every bag. "
  "We consider it our civic duty.",
  "<B>Petz Y2K Checklist:</B> two weeks of <A HREF=\"product_c02.html\">canned food</A>, a manual can opener, "
  "fresh water, one <A HREF=\"product_c07.html\">executive litter box</A>, and a "
  "<A HREF=\"product_c03.html\">Day-Trader Mouse</A> for morale.",
 ]),
 3: ("The 56k Hamster", "One rodent, one wheel, one tiny ISP", "hamster", [
  "In a garage in Boise, Idaho, a dwarf hamster named Megabyte runs four miles a night on an exercise wheel. "
  "His owner, a retired ham radio operator named Gus Thibodeaux, has wired that wheel to a bicycle "
  "generator, a car battery and the modem bank for HamsterNet, a small internet provider serving eleven "
  "households and one church.",
  "\"He does the evening peak,\" Gus explained. \"After midnight we switch over to the regular power. "
  "Megabyte needs his rest.\"",
  "Customers say HamsterNet connects at a steady 28.8 when Megabyte is fresh and drops to about 14.4 around "
  "2 a.m. Nobody has complained. \"It's still faster than the cable company,\" said one subscriber, "
  "\"and the cable company never sends a Christmas card with a hamster on it.\"",
  "Want to start your own ISP? We can't help with the modems, but we do sell a very good "
  "<A HREF=\"product_sp01.html\">Spin Cycle hamster wheel</A> and a "
  "<A HREF=\"product_sp04.html\">Hamster Hacienda</A> with room for a server rack (a very small one).",
 ]),
}

# ---------------- ASK THE VET (12 Q&As)
ADVICE = [
 ("My Beagle Howls at the Modem",
  "Every time I dial in to the internet, my beagle Chester throws back his head and howls along with the "
  "modem noises. The neighbors have complained. Is he in pain?",
  "Wendell T., Akron, Ohio",
  ["Chester is not in pain. Chester is singing. Many dogs respond to high-pitched sounds, including sirens, "
   "harmonicas and the squeal of a modem handshake, by joining in. It is a social behavior; as far as Chester "
   "is concerned, the computer just called the pack together and he is answering.",
   "To help, give him something better to do when you connect. Ask him to sit, toss him a treat or a chew toy "
   "right before you click 'Dial,' and praise him for quiet. Over a few weeks the modem will start to mean "
   "'snack time,' not 'concert time.' You can also turn down your modem speaker in the control panel, "
   "which your neighbors will appreciate even more than Chester will."]),
 ("Cat Sleeps on My Keyboard",
  "My cat Biscuit lies across my keyboard every morning while I am trying to trade stocks. Yesterday she "
  "accidentally sold 300 shares of something. Why does she do this?",
  "Doris K., Tempe, Arizona",
  ["Your keyboard is warm, it is right in front of you, and it is where your attention is. To a cat, that is "
   "the perfect bed. Biscuit is not interested in the market; she is interested in you.",
   "Put a soft, warm cat bed or a folded towel right beside your monitor so she can be close without "
   "lying on the keys. A sunny window perch nearby helps too. Give her ten minutes of play before the "
   "opening bell so she is ready for a nap. And please, set your trading software to ask for confirmation. "
   "I am a veterinarian, not a stockbroker, but even I know that much."]),
 ("Will My Goldfish Survive Y2K?",
  "My son is worried his goldfish, Captain, will stop working on January 1, 2000. What should I tell him?",
  "Phil R., Duluth, Minnesota",
  ["You can tell him that Captain is completely Y2K compliant. Fish do not have calendars, clocks or "
   "computer chips. The only thing Captain cares about is clean water, the right temperature and not too much food.",
   "If your son wants a project, have him help you do a partial water change once a week and test the water "
   "with a simple kit. A well-kept goldfish can live ten years or more, which means Captain may very well "
   "see the year 2010. Your computer may not."]),
 ("My Parrot Repeats My Stock Tips",
  "My African grey, Mortimer, has started repeating things I say on the phone to my broker. He shouted "
  "'SELL!' during my mother-in-law's visit. Can I stop this?",
  "Lionel P., Greenwich, Connecticut",
  ["African greys are among the best talkers in the bird world, and they pick up words that come with "
   "strong emotion. If you get excited on the phone with your broker, Mortimer notices.",
   "You cannot erase a word, but you can make it less interesting. Do not react when he says it; "
   "laughing or scolding both reward him with attention. Instead, reward the words you like with a treat "
   "and a happy voice. Grey parrots also need hours of daily interaction and toys to destroy, so a bored "
   "Mortimer is a talkative Mortimer. And maybe take your broker's calls in the other room."]),
 ("Why Does My Ferret Steal Socks?",
  "My ferret Ziggy steals socks, keys and the TV remote and hides them under the couch. Is something wrong with him?",
  "Rhonda M., Bakersfield, California",
  ["Nothing is wrong with Ziggy. He is a ferret. 'Stashing' is completely normal ferret behavior; in the wild "
   "their relatives cache food in burrows, and pet ferrets apply the same instinct to anything they can carry.",
   "Check his stash regularly, especially for rubber, foam or anything small enough to swallow, because "
   "intestinal blockages are a real danger for ferrets. Give him a legal stash spot with a fleece blanket "
   "and some safe toys, and ferret-proof your house the way you would for a toddler. As for the socks, "
   "I recommend a laundry basket with a lid. Our mascot recommends it too, but for personal reasons."]),
 ("My Iguana's Heat Lamp and My Electric Bill",
  "My iguana Lola needs a heat lamp all day, and my electric bill went up eleven dollars. Can I turn it off "
  "to save money?",
  "Tony D., Tampa, Florida",
  ["Please don't. Iguanas are cold-blooded and depend on outside heat to digest food and fight infection. "
   "Lola needs a warm basking spot of roughly 95 degrees Fahrenheit, a cooler side of the enclosure, "
   "and a UVB light for about 12 hours a day so she can use calcium properly.",
   "To save money, put the lights on an inexpensive appliance timer, make sure the enclosure is not in a "
   "drafty spot, and use a thermometer at each end so you are not overheating. Eleven dollars a month is a "
   "bargain compared to treating metabolic bone disease. Trust me. I've seen the bills."]),
 ("Hamster Runs All Night",
  "My hamster Pickles runs on his wheel from 11 p.m. to 5 a.m. and it squeaks. I haven't slept since March. Help!",
  "Kendra L., Portland, Oregon",
  ["Hamsters are nocturnal and very active, and a hamster can easily run several miles a night. "
   "Taking away the wheel is not the answer; it's his gym, his office and his hobby all in one.",
   "Instead, get a solid-surface 'silent' wheel that is large enough that his back stays straight "
   "while he runs; wire-rung wheels can injure little feet. A drop of vegetable oil on a squeaky axle (not "
   "where he can lick it) or a quick swap usually fixes the noise. And if all else fails, move the cage "
   "to a room that isn't your bedroom. Pickles won't mind. Pickles is busy."]),
 ("Dog Barks at Delivery Trucks",
  "Ever since I started ordering from Petz.com, my sheltie Rosie barks at every delivery truck. "
  "Is it something you are shipping?",
  "Sam B., Overland Park, Kansas",
  ["It's not the kibble, I promise. Shelties are herding dogs, and big, loud vehicles that pull up, "
   "drop something off and leave are, from Rosie's point of view, intruders she personally chased away. "
   "Every time the truck drives off, her barking 'worked,' so she does it again.",
   "Start by rewarding calm behavior when she hears a truck in the distance, before she's revved up. "
   "Keep treats near the front window. A tired herding dog is a quiet herding dog, so make sure she gets "
   "plenty of exercise and puzzle toys. And please give our driver a wave. He's been through a lot."]),
 ("Rabbit Chews Through Phone Cords",
  "My rabbit Hopscotch chewed through the phone cord three times this month. I keep getting knocked offline. "
  "Is she trying to tell me something?",
  "Grace W., Burlington, Vermont",
  ["She is telling you that rabbits must chew. Their teeth grow throughout their lives, and cords happen to be "
   "the perfect size and texture. Unfortunately, chewing a live electrical cord can be fatal, so this needs "
   "fixing right away.",
   "Run cords through hard plastic tubing or split-loom covers, or move them out of reach entirely. "
   "Then give Hopscotch better things to chew: unlimited timothy hay, apple-wood sticks and untreated "
   "cardboard boxes. Supervise her when she's out of her pen. Your modem will thank you, and so will she."]),
 ("Cat Won't Use the Litter Box",
  "My cat Mr. Fluffington has started going outside the litter box. I switched to a new brand of litter last month. Is that it?",
  "Arthur G., Cedar Rapids, Iowa",
  ["It might be. Cats have strong opinions about texture and scent, and a sudden switch can be enough to "
   "send them elsewhere. Try mixing the old litter with the new and changing over gradually across a week or two.",
   "But please also call your veterinarian. A change in litter box habits can be the first sign of a urinary "
   "tract problem, which is painful and, in male cats especially, can become an emergency quickly. "
   "Keep the box very clean, in a quiet spot, and have one more box than you have cats."]),
 ("How Long Do Box Turtles Live?",
  "My grandson wants a box turtle. How long will it live?",
  "Edna F., Bowling Green, Kentucky",
  ["With good care, a box turtle can live 40 years or more. Some have lived over a century. That is longer "
   "than most companies on the stock exchange, and certainly longer than some I could name.",
   "Before you buy, think about who will care for the turtle when your grandson goes to college. Box "
   "turtles need a large enclosure, a UVB light, a varied diet of insects, worms, vegetables and some fruit, "
   "and a shallow water dish. Never take one from the wild; buy from a reputable breeder or adopt from a "
   "reptile rescue."]),
 ("Can My Dog Eat the Packing Peanuts?",
  "Your boxes are full of foam packing peanuts. My lab Duke keeps trying to eat them. Is that safe?",
  "Ray H., Baton Rouge, Louisiana",
  ["No. Foam peanuts can cause choking or an intestinal blockage, especially in a dog who swallows first "
   "and asks questions later, which describes most labs. The newer 'dissolvable' starch peanuts are less "
   "dangerous but still not food.",
   "Open boxes where Duke can't help, and bag up the peanuts right away. If he does swallow a large amount, "
   "or starts vomiting, acting lethargic or straining, call your veterinarian. We've asked our warehouse "
   "to use fewer peanuts. They said they'd need more funding."]),
]

# ---------------- MISC
PET_OF_DAY = ("Mr. Biscuits", "a basset hound from Muncie, Indiana, who enjoys long naps and short walks")
