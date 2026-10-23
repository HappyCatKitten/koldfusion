# -*- coding: utf-8 -*-
# uBid listings -- 200 invented auctions from the autumn of 1999.  All sellers, bidders,
# items and descriptions are made up for the 1999 Web parody.

CATEGORIES = [
    ("antiques", "Antiques &amp; Art", 73412),
    ("books", "Books, Movies, Music", 455318),
    ("coins", "Coins &amp; Stamps", 120554),
    ("collect", "Collectibles", 1052117),
    ("computers", "Computers", 104902),
    ("dolls", "Dolls &amp; Figures", 63340),
    ("jewelry", "Jewelry &amp; Watches", 144068),
    ("electronics", "Photo &amp; Electronics", 57211),
    ("glass", "Pottery &amp; Glass", 198007),
    ("sports", "Sports Memorabilia", 358406),
    ("toys", "Toys &amp; Bean Bags", 320777),
    ("misc", "Everything Else", 335990),
]

# cat|picture kind|title|starting bid|what it will go for|reserve? (1 = has a reserve)|description
ITEMS = """
toys|beanie|PRINCESS the purple bear BEANIE BABY w/ TAG PROTECTOR mint!!|9.99|185|1|Purple bear with the white rose on her chest. Tag is MINT, kept in a hard case on top of the fridge since the day I got her. Smoke-free home.
toys|beanie|Beanie Baby LOT of 25 - all with tags - GREAT STARTER LOT|19.99|74|0|Twenty-five assorted bean bag animals, mostly 1998 releases. Some swing tags creased. A great way to start a collection or to keep the grandkids busy.
toys|beanie|*RARE* Peanut the ROYAL BLUE elephant 3rd gen tag L@@K|25.00|240|1|The famous dark blue elephant. 3rd generation swing tag, 1st gen tush tag. Comes with a printed certificate I made on my inkjet.
toys|beanie|Garcia the tie-dye bear RETIRED nr|5.00|62|0|Groovy retired bear. Tags attached. No reserve, highest bidder takes it.
toys|beanie|Teenie Beanie COMPLETE SET of 12 from the burger place, still in bags|4.99|38|0|All twelve of the 1999 happy-meal teenies, sealed in their original plastic bags. My son ate a LOT of hamburgers for these.
toys|beanie|Erin the green bear - St Patrick's - MINT w/ protector|3.00|21|0|Kelly green bear with the white shamrock. Comes with tag protector.
toys|beanie|Glory the flag bear, stars and stripes, ALL STAR GAME giveaway?|7.50|44|0|Not sure if this is the giveaway version or a regular one. Bid with your heart.
toys|beanie|Bean bag LOBSTER *** Pinchers *** old style tag|2.00|16|0|Red lobster with old-style swing tag. Slight fading on one claw. Pet free home.
toys|furby|FURBY - BRAND NEW IN BOX - NEVER OPENED - holiday gift!!|35.00|71|0|Bought two at the toy store at 6 a.m. last November and this one has never been out of the box. Speaks Furbish. Batteries not included (they never are).
toys|furby|Furby WHITE & PINK talks, sleeps, works great|15.00|39|0|Used, works perfectly, says all the phrases. Eyes blink. Will NOT stop talking at 3 a.m. That is why it is for sale.
toys|furby|LOT OF 3 FURBYS - one needs new batteries - talking toys|20.00|58|0|Three Furby-style talking creatures. Two work, one is very quiet. Might just be shy.
toys|furby|Furby Babies - SET OF 4 NIB rare colors|29.99|84|1|Four of the new smaller babies in the hard-to-find colors. New in box.
toys|tamagotchi|Original TAMAGOTCHI virtual pet - blue - works - with box|5.00|19|0|The original egg-shaped virtual pet. Has been fed, cleaned and loved. Box and instructions included.
toys|tamagotchi|GIGA PET virtual dog - Lil Puppy - new batteries|2.50|11|0|Keychain digital puppy. Fresh batteries. Has not died in three weeks, which is a personal record.
toys|tamagotchi|Lot of 6 VIRTUAL PETS - dinos, cats, chicks - all work|9.00|27|0|Six keychain virtual pets. All work, some need a reset. Great for a classroom prize jar.
toys|pokecard|POKEMON CHARIZARD holo 1st EDITION shadowless!!! NM|49.00|420|1|The fire dragon everyone at school wants. 1st edition stamp, shadowless, near mint. Shipped in a top loader in a box in a bigger box.
toys|pokecard|Pokemon BASE SET booster box SEALED 36 packs|60.00|165|0|Factory sealed box of 36 booster packs. Gotta catch 'em all, as they say.
toys|pokecard|Lot of 200 Pokemon cards w/ 8 holos, Pikachu, Mewtwo|15.00|62|0|Two hundred cards from the base set and Jungle. Eight holos including a Mewtwo. Some played, most fine.
toys|pokecard|Pokemon JUNGLE holo set complete 16/16 mint|35.00|98|0|All sixteen holofoil cards from the Jungle expansion. Pack fresh, sleeved.
toys|yoyo|Pro-style ball bearing YO-YO, glow in the dark, NEW|3.00|12|0|Sleeps for a full minute. Glows in the dark. Great for walking the dog.
toys|actionfig|SPACE WARS Episode I horned villain 12 inch figure MIB|9.99|34|0|New in box, never displayed. Double-bladed saber included. Box has small shelf wear.
toys|actionfig|Toy Tale 2 talking cowboy doll - pull string works|12.00|30|0|Pull-string talking cowboy. Says eight phrases. Hat included.
toys|yoyo|Tickle-type laughing ELMO style doll - still giggles|8.00|24|0|Squeeze his tummy and he laughs, shakes and falls over. Still very funny. My dog disagrees.
toys|beanie|*Beanie Buddies* large size bear, Peace sign, mint|10.00|33|0|Large plush Buddy version with the peace sign. Mint tags.
collect|pez|VINTAGE PEZ dispenser LOT 40+ no feet, 1970s!!|25.00|146|1|More than forty dispensers, many without feet. Includes some oddballs I cannot identify. A treasure chest for the serious collector.
collect|pez|Pez dispenser - Santa - 1960s - NO FEET|15.00|55|0|Older Santa dispenser with no feet. Some paint wear on the beard.
collect|lunchbox|METAL LUNCHBOX 1977 space movie w/ thermos|30.00|118|0|Embossed metal lunchbox with matching thermos. A few dings, latch works. Smells faintly of bologna.
collect|lunchbox|Vintage 1980 lunch box - cartoon cat - no thermos|8.00|26|0|Plastic lunch box, cartoon cat on both sides. No thermos. Light scratches.
collect|mug|Millennium 2000 commemorative MUG - dated, unused|2.00|9|0|Big 2000 mug, never used. Get yours before they are worth a fortune (or nothing).
collect|snowglobe|Snowglobe collection - 12 cities - from my aunt's travels|10.00|41|0|Twelve snowglobes from Reno to Rome. One has a small air bubble. My aunt says sell, so I am selling.
collect|button|LOT 75 political campaign BUTTONS 1950s-1990s|20.00|88|0|Seventy-five pinback buttons spanning forty years of campaigns. A few rusty pins.
collect|sign|Porcelain GAS STATION sign - flying horse style - 30 inch|150.00|410|1|Big two-sided porcelain sign from a closed station in Kansas. Chips around the bolt holes, colors still bright.
collect|mug|Lot of 6 diner coffee mugs, heavy, Route 66|6.00|22|0|Six thick white diner mugs from a diner that closed in 1994. Great for coffee or pencils.
collect|lunchbox|Space shuttle lunchbox - 1981 - VG|12.00|39|0|Space shuttle launch scene. Very good condition, some rust on the hinge.
collect|snowglobe|Musical snowglobe plays a carol - works - 1970s|7.50|19|0|Wind it up and it plays a carol while the snow falls on a little church.
collect|button|Y2K Smiley face buttons x 50 - for your New Year party|5.00|14|0|Fifty brand new buttons with a smiling computer saying Happy 2000. Party favors!
collect|pez|PEZ - complete set of 9 space saga characters - sealed on cards|12.00|29|0|All nine on their original blister cards, sealed.
collect|sign|Neon BEER sign - works - blue and red|45.00|120|0|Works great, a little buzz when it first turns on. Local pickup preferred but will ship at your risk.
collect|mug|Collectible SPACE NEEDLE salt and pepper shakers|3.00|11|0|Matched pair from a 1962 fair. Small chip on the pepper.
computers|zipdisk|ZIP DISKS 100MB - LOT OF 10 - formatted PC - like new|10.00|46|0|Ten 100MB cartridges, formatted for PC. Labels removed. Click of death not included.
computers|zipdisk|IOMEGA-style Zip drive 100MB external parallel port w/ cables|25.00|62|0|External 100MB drive with parallel cable and power brick. Works on Windows 95 and 98.
computers|zipdisk|Jaz-style 1GB removable cartridges x 3|15.00|41|0|Three 1GB cartridges. Never had a problem with them, unlike my last car.
computers|modem|56K V.90 external MODEM - upgradeable - box & manual|20.00|48|0|Fast 56K modem with flashable firmware. Screeches beautifully. Box and manual included.
computers|modem|US Robotics-style 28.8 modem - works - FREE SHIPPING|3.00|12|0|Slow but faithful. Free shipping in the lower 48.
computers|pda|PALM-style III organizer w/ cradle, stylus & case - EXC|60.00|151|0|Excellent condition. HotSync cradle, stylus, leather case. Graffiti still recognizes my handwriting better than my doctor does.
computers|pda|Palm-style V aluminum - like new - with box - holiday gift?|150.00|310|1|Super slim aluminum model. Rechargeable. Box, manuals, cradle all included.
computers|computer|Apple-style iMac Bondi Blue 233MHz 32MB - LOCAL PICKUP|300.00|705|1|The translucent blue all-in-one. 233MHz, 32MB RAM, 4GB drive. Hockey-puck mouse included (sorry).
computers|computer|Pentium II 400 tower 64MB 10GB Win98 + 17in monitor|250.00|640|1|Fast machine, ready to surf. Windows 98 installed. Monitor is heavy, shipping will be fun.
computers|floppy|3.5 FLOPPY DISKS - box of 50 - HD 1.44MB - new|4.00|15|0|Fifty brand new high density floppies. Enough for one modern program, almost.
computers|softbox|WINDOZE 98 Second Edition full version SEALED|40.00|96|0|Sealed full retail box, not upgrade. Includes the cool startup sound.
computers|softbox|Lot of 25 CD-ROM games 1995-1998 - all complete|15.00|55|0|Twenty-five boxed CD-ROM games. Adventure, flight sims, golf. All complete with manuals.
computers|computer|Laptop - 266MHz - 32MB - CD-ROM - battery holds 40 min|200.00|455|0|Works well, small crack on the lid hinge. Battery lasts about forty minutes, or one episode of a show.
computers|modem|Cable modem - unused - from the cable co. promo|10.00|31|0|Got two at a promotion. Never used this one.
computers|floppy|5.25 floppy disks - 30 assorted - old DOS games?|1.00|9|0|Found in the basement. Labels say things like GAMES and DO NOT ERASE. Contents unknown!
computers|softbox|Y2K COMPLIANCE CHECKER software - test your PC!|5.00|18|0|Find out if your PC will survive January 1. Runs on Windows 95/98. Peace of mind on a CD.
computers|zipdisk|SuperDisk 120MB drive USB - reads floppies too|20.00|44|0|Reads old floppies AND the new 120MB disks. USB, works on the new iMac.
computers|pda|Pocket organizer with keyboard, 2MB - works|15.00|36|0|Clamshell organizer with a tiny keyboard. Two megabytes of memory, which is a lot of phone numbers.
computers|computer|Commodore-style 64 with disk drive and joystick - VINTAGE|30.00|85|0|Classic 8-bit home computer with disk drive, joystick and a box of disks. Boots to the READY prompt.
electronics|camera|DIGITAL CAMERA 1.3 MEGAPIXEL!! w/ 8MB card|99.00|260|1|Takes 1280x960 pictures! Stores about 20 on the card. Uses four AA batteries an hour.
electronics|camera|35mm SLR camera body + 50mm lens - classic|40.00|118|0|All-manual classic. Light meter works. Lens is clean, no fungus.
electronics|pager|PAGER alphanumeric - clip - new battery - 911 911!|5.00|19|0|Shows text messages! Clip and holster included. Service not included.
electronics|phone|Cellular phone - flip style - with charger|20.00|52|0|Flip phone, extra battery and car charger. Antenna pulls out nicely.
electronics|gameboy|GAME KID COLOR handheld - purple - with 3 games|35.00|72|0|Color handheld in see-through purple. Includes three games, one of them is the one with the electric mouse.
electronics|gameboy|Nintendo-style 64 console w/ 2 controllers + 4 games|60.00|128|0|Works great. Two controllers, one stick slightly loose. Four games including go-karts.
electronics|phone|Clear see-through phone - lights up when it rings!!|8.00|24|0|The phone you have always wanted. Neon lights inside flash when it rings. Touch tone.
electronics|camera|POLAROID-style instant camera - film included|6.00|21|0|Instant camera with two packs of film. Shake it like you mean it.
electronics|pager|LOT of 5 pagers - various - no service|5.00|15|0|Five pagers. A drug dealer once asked me if I was selling. I said only on uBid.
electronics|gameboy|DREAMBOX-style console - NEW - 9.9.99 launch!!|150.00|260|1|Bought on launch day and never opened. Comes with modem built in. The future of gaming!
electronics|camera|Camcorder Hi8 with case, 2 batteries, tapes|60.00|165|0|Shoulder strap, case, two batteries and five tapes (one is my cousin's wedding, will erase).
electronics|phone|Cordless phone 900MHz with answering machine|10.00|28|0|900MHz for crystal clear calls from the backyard.
electronics|pager|Two-way pager - send AND receive - new in box|30.00|74|0|Tiny keyboard, sends messages! Like e-mail on your belt.
electronics|gameboy|Handheld LCD game - space invaders style - 1981|10.00|37|0|Old LCD handheld game. Still beeps. Battery door taped.
electronics|camera|Web cam - parallel port - see yourself on the Internet!|10.00|29|0|320x240 color video. Be the first on your block to broadcast your goldfish.
books|book|HARRY-style wizard school book 1st AMERICAN printing|20.00|95|0|First American printing of the wizard boarding school book everybody is reading. Dust jacket clean.
books|book|Lot of 30 paperback SCIENCE FICTION 1960s-1980s|10.00|38|0|Thirty mass market paperbacks with gorgeous painted covers. Some yellowed pages.
books|vhs|SPACE WARS trilogy VHS - widescreen box set - sealed|25.00|55|0|Sealed widescreen box set. The last time they will ever be the originals, probably.
books|vhs|Lot of 20 Disney-style animated VHS tapes - clamshells|20.00|61|0|Twenty animated movies in white clamshell cases. Some black diamond editions? I do not know what that means but people keep asking.
books|cd|CD lot - 50 alternative rock CDs 1990-1998|15.00|58|0|Fifty CDs, jewel cases mostly intact. Grunge, Britpop and one accidental polka.
books|record|Vintage VINYL record lot 1960s rock - 40 LPs|30.00|135|0|Forty LPs from my dad's collection. He said I could. Some sleeves worn, vinyl is good.
books|book|Signed first edition mystery novel - inscribed|25.00|70|0|Signed and inscribed to 'Linda.' If your name is Linda, this is your lucky day.
books|cd|Boy band CD - SIGNED by all five members!!|15.00|52|0|Signed at the mall in March. I screamed. They smiled. Certificate of authenticity from me.
books|vhs|TITANICK VHS 2 tape set - like new|5.00|14|0|Watched once. Cried twice.
books|record|45 rpm singles lot of 100 - jukebox pulls|20.00|66|0|One hundred 45s pulled from a diner jukebox. Lots of doo-wop.
books|book|Cookbooks lot of 15 - church and community 1950s-1970s|8.00|29|0|Spiral bound community cookbooks, full of gelatin salads. A sociologist's dream.
books|cd|THE MATRICES soundtrack CD - mint|4.00|12|0|Industrial and techno for dodging bullets. Mint.
books|vhs|Workout VHS tapes - lot of 8 - 80s aerobics|3.00|13|0|Leg warmers recommended. Eight tapes of pure 1980s sweat.
books|book|Complete set of encyclopedias 1987 - 22 volumes|20.00|42|0|Twenty-two volumes, green leather-look. Local pickup only, these weigh as much as a car.
books|record|Beatles-era British invasion LP - mono pressing|25.00|90|0|Original mono pressing, VG+ vinyl, cover has ring wear.
books|cd|Y2K party mix CD - 20 dance hits - sealed|3.00|10|0|Sealed party CD to ring in the millennium. Track 7 is the one about partying like it is a certain year.
coins|coin|1999 STATE QUARTERS complete set uncirculated P & D|5.00|19|0|All five 1999 state quarters from both mints, uncirculated. The start of a 10-year project!
coins|coin|Morgan silver dollar 1921 - nice luster|15.00|31|0|Nice coin with good luster. Raw, not slabbed.
coins|coin|Lot of 100 WHEAT pennies 1909-1958|5.00|16|0|One hundred wheat back cents. Didn't check for the good dates. Maybe you'll get lucky.
coins|stamp|Stamp album - 1,000+ worldwide stamps - 1920s-1970s|20.00|67|0|Big old album, stamps hinged. Lots of countries that no longer exist.
coins|stamp|Sheet of 1999 commemorative stamps - mint never hinged|4.00|12|0|Full sheet, mint never hinged. Face value plus a little extra for my trouble.
coins|coin|Gold coin 1/10 oz - 1999 - in capsule|30.00|52|0|One-tenth ounce gold piece, brilliant uncirculated, in capsule.
coins|coin|Foreign coin lot - 2 pounds of world coins|10.00|29|0|Two pounds of coins from all over. Kids love sorting these. So do adults with nothing to do.
coins|stamp|First day covers lot of 40 - 1960s space program|15.00|48|0|Forty first day covers from the space race. Great cachets.
coins|coin|Silver proof set 1999 - original box|25.00|58|0|Proof set with silver coins, original government packaging.
coins|stamp|Inverted airplane stamp REPRODUCTION - fun gift|1.00|6|0|A REPRODUCTION of the famous upside-down airplane stamp. Not real! Very fun for the stamp nut in your life.
coins|coin|Bicentennial 1976 coins - bag of 50 quarters|12.50|17|0|Fifty drummer-boy quarters. Spend them or save them.
coins|coin|Millennium medallion 2000 - silver - limited edition|8.00|24|0|Limited edition (of how many, the box does not say). Silver-plated.
dolls|doll|BARBARA-style 1999 holiday doll in red gown NRFB|20.00|46|0|Never removed from box. Red velvet gown. Box is perfect, no creases.
dolls|doll|Vintage 1960s fashion doll with trunk and clothes|50.00|190|1|Original 1960s doll with case and over 30 outfits. Some hair loss (hers, not mine).
dolls|doll|Cabbage-patch-style doll w/ birth certificate 1984|10.00|32|0|Adopted in 1984, still has her papers. Yarn hair, signed bottom.
dolls|actionfig|G.I. style 12 inch soldier 1964 - original|60.00|210|1|Early 12 inch soldier with dog tag and boots. Scar on cheek. Some wear.
dolls|actionfig|Lot of 30 action figures - 1980s - robots, heroes|15.00|59|0|Thirty loose figures, transforming robots, heroes and some guys I don't know. Missing accessories.
dolls|doll|American-girl-style doll w/ 3 outfits and book|30.00|88|0|Historical doll with three outfits and her book. Excellent condition.
dolls|actionfig|SPAWN-style figure series 1 - carded|5.00|17|0|Still on card. Cape is very dramatic.
dolls|doll|Porcelain doll - Victorian - 18 inch - stand|12.00|35|0|Lace dress, glass eyes, stand included. She watches you sleep.
dolls|actionfig|Space-saga-style figures lot of 12 1978-1983 LOOSE|25.00|96|0|Twelve original loose figures. Some missing weapons. One has a chewed foot (dog).
dolls|doll|Troll dolls lot of 15 with wild hair|6.00|23|0|Fifteen trolls with pink, green and purple hair. Hair is in fair condition, considering.
dolls|actionfig|Wrestling figures lot of 8 - 1999 - carded|8.00|30|0|Eight wrestlers still on cards. Smackdown not included.
dolls|doll|Paper doll books x 5 - 1950s - uncut!|10.00|41|0|Five uncut paper doll books. Rare to find uncut!
jewelry|watch|Swatch-style plastic watches LOT of 10 1980s|20.00|72|0|Ten colorful plastic watches. Need batteries. Very 1987.
jewelry|watch|Men's DIVER watch - automatic - steel - box|60.00|160|1|Automatic diver style watch, keeps good time. Box but no papers.
jewelry|ring|14K gold ring - size 7 - sapphire & diamonds|40.00|130|1|Oval blue sapphire with two small diamonds. Stamped 14K.
jewelry|ring|MOOD RING lot of 25 - changes color!|3.00|12|0|Twenty-five mood rings. My mood: ready to sell.
jewelry|watch|Pocket watch - railroad grade - 1915 - runs|80.00|240|1|Seventeen jewels, lever set, runs strong. Case shows wear.
jewelry|ring|Sterling silver toe rings x 12 - beach ready|4.00|14|0|Twelve adjustable sterling toe rings. Very 1999.
jewelry|watch|Digital calculator watch - 1983 - works|8.00|31|0|Do math on your wrist! Buttons work, alarm plays a tune.
jewelry|ring|Costume jewelry box - 3 lbs - brooches, clip earrings|10.00|38|0|Three pounds of sparkly costume jewelry from a grandma's estate.
jewelry|watch|Y2K COUNTDOWN watch - counts to midnight 12/31/99|5.00|16|0|Shows days, hours, minutes until the year 2000. After that, who knows!
jewelry|ring|Class ring 1978 - 10K - initials JRB|25.00|61|0|If you are JRB from the class of 1978, I found your ring in a pawn shop.
glass|vase|Depression glass vase - green - 8 inch|10.00|36|0|Pretty green depression glass. No chips or cracks.
glass|glass|Fiesta-style dinnerware - 20 pieces mixed colors|40.00|125|1|Twenty pieces of colorful dinnerware: plates, bowls and a pitcher. A few utensil marks.
glass|vase|Art pottery vase - signed - drip glaze|25.00|80|0|Hand thrown, signed on the bottom. Lovely blue drip glaze.
glass|glass|Jadeite-style mixing bowls set of 3|30.00|95|0|Three nesting mixing bowls in that lovely jade green.
glass|glass|Carnival glass bowl - marigold - grape pattern|15.00|46|0|Marigold iridescent carnival bowl. Very shiny.
glass|vase|Cookie jar - cow shaped - moos when opened|8.00|25|0|Ceramic cow cookie jar. Moo mechanism needs batteries.
glass|glass|Milk glass hobnail lot - 12 pieces|12.00|34|0|Twelve white hobnail pieces. Candy dishes, vases, a lamp base.
glass|vase|Studio glass paperweight - swirls - signed|20.00|57|0|Heavy glass paperweight with a colorful swirl. Signed and dated.
glass|glass|Pyrex-style casserole set - turquoise - with lids|15.00|44|0|Turquoise casserole dishes with lids. Ready for your next potluck.
glass|vase|Pottery planter shaped like a swan|5.00|17|0|Swan planter, glossy white. Small chip on tail, faces the wall nicely.
sports|baseball|1998 HOME RUN RACE souvenir baseball - stadium sold|10.00|34|0|Commemorative ball from the great home run chase of 1998. Display cube included.
sports|card|Baseball card LOT of 500 - 1987 - commons|5.00|13|0|Five hundred cards from 1987. Every kid in America has these, but now you can too.
sports|card|ROOKIE CARD basketball star 1986 - PSA style graded 8|60.00|240|1|The famous rookie card of the guy who wore 23. Graded 8. Sharp corners.
sports|baseball|Autographed baseball - 1970s pitcher - with COA|30.00|75|0|Signed on the sweet spot. Comes with a certificate of authenticity.
sports|pennant|Vintage felt PENNANT lot 10 - 1960s teams|15.00|52|0|Ten felt pennants. Colors bright, a few pin holes.
sports|card|Hockey card set 1999-2000 complete|10.00|28|0|Complete base set, sorted and in a box.
sports|baseball|Game-used bat - minor league - cracked|20.00|48|0|Cracked during a game in Toledo. Signed by somebody named Dave.
sports|pennant|World Series 1986 program and ticket stub|15.00|40|0|Program and a stub from game 6. Yes, THAT game.
sports|card|Football cards 1970s lot of 300|10.00|33|0|Three hundred cards, some stars, some creases.
sports|baseball|Bobblehead - 1960s - baseball player - nodder|25.00|88|0|Old paper mache nodder. Head still bobbles. Small crack at neck.
sports|pennant|Olympic 1996 pin collection - 60 pins|20.00|56|0|Sixty pins from the Atlanta games, on a felt board.
sports|card|Golf - signed scorecard - famous young champion 1997|40.00|110|1|Signed scorecard from the 1997 green jacket tournament. COA from a shop in Florida.
antiques|clock|Antique MANTEL CLOCK 1890s - runs and chimes|60.00|210|1|Walnut case, runs and chimes on the hour. Key included.
antiques|painting|Oil painting - seascape - signed - gilt frame|50.00|165|1|Stormy seascape, signed lower right. Ornate gilt frame with some losses.
antiques|lamp|Tiffany-style stained glass lamp - dragonfly|40.00|120|0|Reproduction stained glass lamp with dragonfly shade. Beautiful glow.
antiques|clock|Kit-cat-style wall clock - eyes and tail move|15.00|48|0|Black cat clock with moving eyes and tail. Battery operated.
antiques|painting|Paint-by-number - 1950s - horses - framed|5.00|22|0|Two galloping horses. Painted by somebody's very patient uncle.
antiques|lamp|LAVA LAMP - 1970s - orange - works|15.00|41|0|Original 1970s lava lamp. Takes about an hour to get going, like me.
antiques|clock|Railroad station clock - 18 inch - electric|50.00|135|0|Big schoolhouse-style clock from a train depot. Electric.
antiques|painting|Velvet painting - Elvis-style singer - 24x36|10.00|45|0|Black velvet portrait of a famous sideburned singer. The eyes follow you.
antiques|vase|Chinese-style ginger jar - blue and white|20.00|60|0|Blue and white ginger jar with lid. Age unknown, charm guaranteed.
antiques|lamp|Antique oil lamp - brass - with chimney|15.00|43|0|Brass oil lamp with glass chimney. Ready for Y2K!
antiques|painting|Folk art weathervane - rooster - copper|80.00|260|1|Hand-hammered copper rooster weathervane. Nice green patina.
antiques|clock|Cuckoo clock - Black Forest style - needs work|20.00|54|0|Carved leaves and birds. Cuckoo is shy and needs some adjustment.
misc|kit|Y2K SURVIVAL KIT - water, food, flashlight, radio - BE READY!!!|30.00|98|0|Everything your family needs for 72 hours: water pouches, food bars, crank radio, flashlight, whistle and a deck of cards. Don't wait until December 31!
misc|kit|Y2K survival BUCKET - 30 days of dehydrated food|60.00|155|0|Thirty days of freeze-dried meals in a sealed bucket. Shelf life 15 years, just in case the world ends late.
misc|kit|Hand crank flashlight/radio - NO BATTERIES NEEDED - Y2K|8.00|24|0|Crank for one minute, get twenty minutes of light. Picks up AM/FM.
misc|kit|Water purification tablets 500 count - Y2K preparedness|5.00|16|0|Five hundred tablets. Turns creek water into slightly-less-creek water.
misc|box|Millennium time capsule - stainless - engraved free|20.00|45|0|Stainless steel capsule, airtight. I will engrave it for free. Open in 2025!
misc|box|Electric generator 5000W - gas - Y2K ready - LOCAL PICKUP|250.00|540|1|5000 watt generator, used twice. Will keep your fridge and modem going when the grid goes down.
misc|sign|AUTHENTIC piece of the Berlin Wall?? w/ letter|10.00|40|0|My uncle brought it back in 1990. Letter included. It is a rock. It is probably a good rock.
misc|box|Ghost in a jar - REAL - haunted - from my attic|1.00|28|0|Jar was in the attic when we moved in. Lid is taped. Strange noises at night. Not responsible for anything.
misc|box|Box of mystery items from storage unit - unopened|5.00|31|0|Bought a storage unit at auction. This box is one of 40. I have not looked inside. Neither have you. Let's both be surprised.
misc|kit|Freeze-dried astronaut ice cream x 24 packs|6.00|19|0|Neapolitan. Crunchy. Space-age.
misc|sign|Dot-com company T-shirts lot of 20 - startup swag|5.00|18|0|Twenty T-shirts from companies that may or may not exist next year. Mostly XL.
misc|box|1999 Pentium wafer - framed - from a chip plant|25.00|70|0|Real silicon wafer in a shadow box frame. Looks great in a home office.
misc|kit|Emergency candles - 48 hour - case of 24|6.00|17|0|Twenty-four big emergency candles. For Y2K, power outages, or romance.
misc|box|Ant farm - complete - ants by mail coupon|4.00|13|0|Ant farm with sand and a coupon to mail away for ants. Ants not included (federal law).
misc|sign|Unused BAGEL SLICER - as seen on TV|3.00|9|0|Still in box. I bought it at 2 a.m. and regretted it at 8 a.m.
misc|box|Lifetime supply of packing peanuts - 30 cu ft|1.00|7|0|Thirty cubic feet of packing peanuts. Great for other uBid sellers! Shipping will be expensive and very light.
misc|kit|Survival WHISTLE + compass + mirror - lot of 10|5.00|15|0|Ten tiny survival kits. Fits in a pocket. Signal for help in style.
misc|box|Pet rock - original 1975 - in box with manual|10.00|36|0|The original pet rock in its carrying case, with the training manual. Very well behaved.
toys|actionfig|Tickle-me-style plush - 1996 craze - still works|7.00|20|0|The giggling plush that caused stampedes in 1996. Still giggles.
toys|yoyo|Slinky - original metal - 1960s box|5.00|18|0|Walks down stairs alone or in pairs. Everybody knows the song.
toys|furby|Talking electronic pet DOG robot - new - dances|25.00|61|0|Robot puppy that sits, dances and barks at the cat. New in box.
toys|pokecard|Pokemon PIKACHU plush 12 inch - talks|8.00|24|0|Says its name over and over. And over.
toys|yoyo|Lite-brite style peg toy with 500 pegs|8.00|23|0|Make glowing pictures! 500 pegs, some templates.
toys|tamagotchi|Electronic handheld 20 questions - guesses your thing|10.00|26|0|Think of something. It will guess it. Spooky.
toys|actionfig|Toy robot - 1980s - transforms into a cassette|15.00|46|0|Transforms into a cassette player! Classic.
toys|beanie|Beanie Baby Y2K BEAR 'Millennium' - mint tags|6.00|28|0|The millennium bear. Mint tags. Very timely.
computers|softbox|Encarta-style encyclopedia CD-ROM 1999 deluxe|8.00|22|0|Complete reference on five CDs. Includes a video of a volcano.
computers|zipdisk|CD-R blank discs - spindle of 50 - 74 min|10.00|30|0|Burn your own CDs! 650MB each. Spindle of 50.
computers|modem|ISDN terminal adapter - 128K - FAST|15.00|38|0|128K ISDN for the true speed demon. Phone company setup required.
collect|sign|Route 66 metal road sign - reproduction|10.00|26|0|Heavy metal reproduction sign. Ready to hang.
collect|lunchbox|Kiss-band lunchbox 1977 - with thermos!|75.00|240|1|Rock band lunchbox with matching thermos. Good color, some scratches. A real 1970s classic.
electronics|phone|Fax machine - thermal paper - with 3 rolls|10.00|21|0|Sends and receives faxes. Three rolls of shiny thermal paper included.
books|book|COMPUTER BOOKS lot of 12 - HTML, Java, Perl|10.00|28|0|Twelve thick computer books. Learn to make web pages! (I didn't.)
coins|stamp|Duck stamps lot - federal - 1970s-1990s|25.00|75|0|Federal waterfowl stamps, mint and used. Beautiful art.
sports|card|Basketball rookie cards lot of 50 1990s|8.00|29|0|Fifty rookie cards from the 90s. Future hall of famers? You decide.
jewelry|ring|Friendship bracelets lot of 40 - handmade|3.00|10|0|Forty handmade friendship bracelets. Woven with love at summer camp.
glass|glass|Tupperware-style party lot - 30 pieces|10.00|33|0|Thirty pieces in harvest gold and avocado. Burping still works.
antiques|lamp|Gooseneck desk lamp - 1950s - chrome|12.00|38|0|Chrome gooseneck. Rewired. Bulb included.
misc|kit|Bottled water - 55 gallon drum - food grade|15.00|35|0|Food grade drum, clean. Fill it before New Year's Eve.
dolls|doll|Big-head fashion doll prototype? found at yard sale|5.00|19|0|Doll with very big head and feet. Not sure what she is. Maybe a prototype? Maybe not.
"""

USERS = [
    # user id, feedback score, location, member since year
    ("beaniebaron", 128, "Naperville, IL", 1997), ("grandmas_attic", 1204, "Lancaster, PA", 1996),
    ("furbyfan99", 34, "Plano, TX", 1999), ("y2kprepper", 61, "Coeur d'Alene, ID", 1998),
    ("zipdiskzach", 220, "Fremont, CA", 1997), ("pezhead", 812, "Orange, CA", 1996),
    ("cardshark77", 455, "Brooklyn, NY", 1997), ("vintage_vicki", 2310, "Asheville, NC", 1996),
    ("thrift_queen", 677, "Portland, OR", 1997), ("dealmaster2000", 15, "Phoenix, AZ", 1999),
    ("estate_sale_ed", 3150, "Columbus, OH", 1996), ("lunchbox_larry", 98, "Bakersfield, CA", 1998),
    ("pokemaniac", 22, "Chandler, AZ", 1999), ("silver_sam", 540, "Carson City, NV", 1997),
    ("dollhouse_dee", 305, "Kalamazoo, MI", 1997), ("gadgetguy", 147, "Austin, TX", 1998),
    ("cdbin_carl", 73, "Seattle, WA", 1998), ("stampede_steve", 990, "Hartford, CT", 1996),
    ("toy_chest_tina", 412, "Boise, ID", 1997), ("hoops_harold", 11, "Indianapolis, IN", 1999),
    ("clockwork_clara", 86, "Burlington, VT", 1998), ("garage_gus", 6100, "Tulsa, OK", 1996),
    ("bargainbetty", 52, "Pensacola, FL", 1998), ("macmaven", 260, "Cupertino, CA", 1997),
    ("geocacher_gail", 8, "Bend, OR", 1999), ("modem_mike", 41, "Reston, VA", 1998),
    ("crystal_kat", 19, "Sedona, AZ", 1999), ("nascar_ned", 133, "Charlotte, NC", 1998),
    ("atticus_finds", 1520, "Savannah, GA", 1996), ("jukebox_joe", 66, "Memphis, TN", 1998),
    ("palmpilot_pat", 29, "Palo Alto, CA", 1999), ("bidnbuy_brenda", 380, "Omaha, NE", 1997),
    ("snowglobe_sue", 47, "Duluth, MN", 1998), ("velvet_elvis", 212, "Tupelo, MS", 1997),
    ("coin_collector_cy", 1888, "Denver, CO", 1996), ("retro_rita", 95, "Albuquerque, NM", 1998),
    ("sniper_sid", 302, "Las Vegas, NV", 1997), ("lastsecond_lou", 158, "Reno, NV", 1997),
    ("mom_of_5", 26, "Provo, UT", 1999), ("collegekid03", 3, "Ann Arbor, MI", 1999),
    ("cyberpunk42", 14, "Cambridge, MA", 1999), ("tamagotchi_tom", 9, "San Jose, CA", 1999),
    ("antiquarian_al", 745, "Charleston, SC", 1996), ("hobby_hut", 2890, "Akron, OH", 1996),
    ("fleamarket_fran", 168, "Fort Worth, TX", 1997), ("boomer_bob", 57, "Sarasota, FL", 1998),
    ("pixel_pete", 31, "Redmond, WA", 1999), ("happy_hoarder", 112, "Scranton, PA", 1998),
]

PRAISE = [
    "A+++ fast shipping, great packing, would buy again!!!",
    "Item exactly as described. Smooth transaction. A real asset to uBid.",
    "Super fast payment. A pleasure to do business with.",
    "Great communication, item arrived in two days. Highly recommended!",
    "Packed like it was going to the moon. Thanks!!",
    "Honest seller, quick e-mail replies. Five stars.",
    "Paid by money order same day. Excellent buyer!",
    "WOW! Better than the pictures. Thank you so much!",
    "Fast, friendly, fair. What more could you want?",
    "Second time buying from this seller, will be back.",
    "Great item, my daughter screamed when she opened it. A+",
    "Prompt payment, good communication, welcome back any time.",
]
NEUTRAL = [
    "Item OK, shipping took almost three weeks.",
    "Took a while to get an answer to my e-mail, but it worked out.",
    "Box was a bit crushed, item fine.",
]
COMPLAINT = [
    "Never received item. Seller stopped answering e-mail.",
    "Item not as described. Tag was creased. Disappointed.",
    "Bounced check. Stay away.",
]
