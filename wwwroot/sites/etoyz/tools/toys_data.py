# -*- coding: utf-8 -*-
# eToyz catalog: 120 invented toys from the holiday season of 1999.  Every toy, brand and
# description is made up for the 1999 Web parody.

AGES = [  # key, label, min months, max months
    ("baby", "0-12 months", 0, 12),
    ("toddler", "1-2 years", 12, 35),
    ("preschool", "3-4 years", 36, 59),
    ("kids", "5-7 years", 60, 95),
    ("bigkids", "8-11 years", 96, 143),
    ("teens", "12 &amp; up", 144, 1200),
]

CATEGORIES = [
    ("action", "Action Figures"), ("arts", "Arts &amp; Crafts"), ("building", "Building Sets"),
    ("dolls", "Dolls &amp; Dollhouses"), ("games", "Games &amp; Puzzles"), ("learning", "Learning Toys"),
    ("pretend", "Pretend Play"), ("rc", "Radio Control"), ("plush", "Stuffed Animals"),
    ("ride", "Bikes &amp; Ride-Ons"), ("outdoor", "Outdoor Play"), ("electronic", "Video Games &amp; Electronics"),
]

# category|picture kind|name|brand|min age (months)|max age (months)|price|for (b/g/a)|description
TOYS = """
action|robot|Megabot 3000 Transforming Robot|Gizmotron|60|144|24.99|b|Turns from a robot into a monster truck in nine easy steps (and back again in forty frustrating ones). Lights, sounds and a voice that says "Megabot, roll out!"
action|figure|Galaxy Rangers Space Squad 5-pack|Starhopper|48|120|19.99|b|Five poseable space heroes with snap-on jetpacks and laser blasters. Collect all twelve squads!
action|figure|Captain Comet 12-inch Talking Figure|Starhopper|48|120|29.99|b|Press his belt badge for ten heroic phrases, including "To the stars, and step on it!"
action|dino|T-Rex Rampage Roaring Dinosaur|Mighty Mo Toys|36|108|34.99|a|Walks, roars, and swings its tail at unsuspecting plastic cavemen. Eyes glow red. Requires 4 C batteries.
action|figure|Ninja Ferret Warriors Dojo Playset|Mighty Mo Toys|48|108|39.99|b|The masked ferrets' secret hideout, with a trap door, a pizza oven and a working zip line.
action|figure|Wrestle-Mania Ring with 2 Figures|Bumblebee Toy Co.|60|144|29.99|b|Spring-loaded ropes send figures flying. Commentator not included (that's your job).
action|robot|Robo-Pup Electronic Dog|Gizmotron|60|1200|49.99|a|Sits, begs, barks and wags. Never needs walking, but it will chase the cat.
action|figure|Monster Pocket Trainers Battle Arena|Plinko Industries|72|144|24.99|a|Launch your spinning monster tops into the arena and see who stays standing.
action|dino|Dino Dig Excavation Kit|Tinkerton|72|144|17.99|a|Chisel real-looking fossils out of a plaster block. Includes brush, goggles and a fossil fact book.
action|figure|Super Squad Hero Cape &amp; Mask|Bumblebee Toy Co.|36|96|14.99|a|Satin cape and foam mask. Super powers sold separately (but your imagination is free).
arts|crayons|Rainbow Crayon Carry-All, 120 colors|Kazoo Kids|36|144|12.99|a|One hundred and twenty crayons, a built-in sharpener and a handle for coloring on the go.
arts|easel|Deluxe Double-Sided Art Easel|Little Sprout|36|96|59.99|a|Chalkboard on one side, dry-erase on the other, paper roll on top. Includes paint cups and a smock.
arts|crayons|Glow-in-the-Dark Sidewalk Chalk 24-pack|Kazoo Kids|36|120|7.99|a|Draw hopscotch boards that glow after sunset.
arts|slime|Super Goo Slime Lab|Wobbleworks|72|144|19.99|a|Mix your own glowing, bouncing, stretching slime. Parents: it washes out. Mostly.
arts|beads|Bead-a-Rama Jewelry Studio|Puddlejump|72|144|16.99|g|Over 1,000 beads, charms and stretchy cord for bracelets, necklaces and friendship rings.
arts|easel|Spin Art Spirograph Machine|Wobbleworks|60|144|24.99|a|Squirt the paint, flip the switch, and watch your masterpiece spin into being.
arts|crayons|Paint-by-Number Dino Set|Kazoo Kids|60|120|9.99|a|Six dinosaur scenes and 20 pots of paint.
arts|beads|Pot-Holder Loom Kit|Little Sprout|72|144|11.99|g|A metal loom and 200 colored loops. Grandma will finally have enough pot holders.
arts|slime|Clay Factory Extruder Set|Wobbleworks|36|96|14.99|a|Squeeze modeling dough into noodles, hair, bricks and spaghetti. Twelve tubs of dough.
arts|crayons|Magic Sketch Board|Kazoo Kids|36|1200|11.99|a|Draw with the magnetic pen, slide to erase. No mess, no batteries, no excuses.
building|blocks|Snap-Brix Big Bucket, 600 pieces|Tinkerton|60|144|29.99|a|Six hundred interlocking bricks in a sturdy bucket with a lid. Build anything. Step on some.
building|blocks|Snap-Brix Space Station Command Base|Tinkerton|84|144|79.99|b|Over 900 pieces, four astronaut figures, a docking shuttle and a working airlock.
building|blocks|Wooden Alphabet Blocks, 48 pieces|Little Sprout|12|60|19.99|a|Classic hardwood blocks with letters, numbers and animals. Non-toxic paint.
building|blocks|Mega-Jumbo Soft Blocks|Little Sprout|6|36|24.99|a|Big, squishy, bite-friendly blocks for the youngest builders.
building|train|Wooden Railway Starter Set|Tinkerton|36|96|49.99|a|Thirty-two pieces of track, a bridge, a tunnel and three magnetic train cars.
building|blocks|Log Cabin Builder Kit|Tinkerton|60|144|29.99|a|Notched wooden logs and green roof slats. Build a frontier fort or a ranch house.
building|gears|Gear-Works Motorized Machine Set|Gizmotron|60|144|34.99|a|Snap together gears, cranks and a motor to build whirling, clanking contraptions.
building|blocks|K'Nex-style Roller Coaster Builder|Plinko Industries|108|1200|69.99|a|Five feet of loops and drops with a motorized chain lift. Requires adult patience.
building|gears|Erector-style Steel Builder 400 pc|Gizmotron|96|1200|39.99|b|Real metal girders, nuts and bolts. Comes with a tiny wrench and a big imagination.
building|blocks|Magnetic Tiles Rainbow Set|Puddlejump|36|120|39.99|a|Colorful see-through tiles that click together with magnets. Great on a sunny windowsill.
dolls|doll|Starlight Ballerina Barbara Doll|Puddlejump|36|120|19.99|g|Pirouettes when you press her crown. Includes tutu, tiara and a music box stage.
dolls|doll|Baby Snuggles Drink &amp; Wet Doll|Little Sprout|36|96|24.99|g|Comes with a bottle, a diaper and a very convincing hiccup.
dolls|dollhouse|Victorian Dream Dollhouse with 30 pieces of furniture|Puddlejump|48|144|129.99|g|Three stories, a working doorbell and a staircase that is easier to climb than ours.
dolls|doll|Friendship Club Twins Gift Set|Puddlejump|60|144|29.99|g|Two best-friend dolls with matching outfits and a secret diary with a tiny lock.
dolls|doll|Cabbage-Patch-Style Adoption Baby|Little Sprout|24|96|29.99|a|Every baby is one of a kind and comes with adoption papers to sign.
dolls|dollhouse|Dream Car Convertible for 12-inch Dolls|Puddlejump|36|120|24.99|g|Pink convertible with a working radio, seat belts and a rearview mirror.
dolls|doll|Historical Pioneer Girl Doll &amp; Book|Puddlejump|84|144|84.99|g|An 18-inch doll with calico dress, bonnet and an illustrated storybook about her journey west.
dolls|doll|Rag Doll Raggedy Ruthie|Little Sprout|12|72|17.99|a|Soft cloth doll with yarn hair and a stitched heart that says "I love you."
dolls|dollhouse|Pocket Palace Mini Dollhouse|Puddlejump|48|120|14.99|g|A whole palace that folds into a compact. Includes two tiny princesses.
dolls|doll|Fashion Studio 50-Outfit Wardrobe|Puddlejump|60|144|34.99|g|Fifty mix-and-match outfits on hangers in a rolling wardrobe trunk.
games|boardgame|Hungry Hungry Hippopotami|Plinko Industries|48|120|14.99|a|Four ravenous hippos, twenty marbles, zero quiet. A classic for a reason.
games|boardgame|Mouse Trap-o-Matic|Plinko Industries|72|144|19.99|a|Build the crazy contraption and catch the other players' mice.
games|boardgame|Millionaire Mogul Real Estate Game|Plinko Industries|96|1200|14.99|a|Buy, sell and trade your way to the top of the Internet boom. Includes dot-com cards.
games|puzzle|1000-Piece World Map Puzzle|Kazoo Kids|120|1200|12.99|a|Every country, ocean and mountain range, as of 1999. Several may change by 2000.
games|puzzle|Chunky Farm Animal Puzzle|Little Sprout|12|48|9.99|a|Eight chunky wooden animals with peg knobs for little fingers.
games|boardgame|Twister-Tangle Party Game|Plinko Industries|72|1200|12.99|a|Left foot red! Right hand blue! Chiropractor not included.
games|boardgame|Y2K Countdown Trivia Game|Kazoo Kids|120|1200|19.99|a|Two thousand questions about the last thousand years. Play before the clocks roll over.
games|puzzle|Rubix-style Twisty Cube|Wobbleworks|96|1200|7.99|a|The classic color cube puzzle. Peeling off the stickers is cheating.
games|boardgame|Candy Lane Adventure Game|Plinko Industries|36|72|9.99|a|No reading required. Race through the gumdrop mountains to the Candy Castle.
games|puzzle|3-D Glow Castle Puzzle|Wobbleworks|108|1200|24.99|a|A foam puzzle that becomes a glowing castle, complete with towers and a drawbridge.
learning|computer|Learn-a-Lot Junior Laptop|Gizmotron|48|96|39.99|a|Forty activities: spelling, math, music and a mouse that teaches mousing.
learning|globe|Talking Explorer Globe|Gizmotron|72|144|89.99|a|Touch any country with the magic pen to hear its capital, population and a fun fact.
learning|telescope|Junior Astronomer Telescope|Tinkerton|96|1200|59.99|a|60mm refractor with tripod and moon map. See the rings of Saturn on a clear night.
learning|chemset|Mad Scientist Chemistry Lab|Tinkerton|120|1200|34.99|a|Over 60 safe experiments: invisible ink, rock candy and a volcano that will impress the neighbors.
learning|computer|Speak-and-Spell-style Word Whiz|Gizmotron|60|120|24.99|a|It says the word, you spell it. The robot voice is exactly as you remember.
learning|microscope|Microscope Discovery Kit|Tinkerton|96|1200|39.99|a|Up to 600x magnification, prepared slides and a shrimp hatchery.
learning|globe|Phonics Fridge Letters|Little Sprout|24|60|19.99|a|Pop a letter in and it sings its sound. Sticks to the fridge.
learning|computer|Kid-Safe Internet Starter CD-ROM|Gizmotron|60|144|19.99|a|A friendly first step onto the Information Superhighway, with a talking guide named Byte.
learning|telescope|Bug Catcher Explorer Kit|Tinkerton|48|120|14.99|a|Bug jar with magnifier lid, net, tweezers and a field guide to backyard critters.
learning|chemset|Crystal Growing Kit|Tinkerton|96|1200|16.99|a|Grow sparkling crystals in seven colors on your windowsill.
pretend|kitchen|Retro Diner Play Kitchen|Little Sprout|36|96|99.99|a|Stove that sizzles, a toaster that pops and a jukebox counter. Twenty pieces of play food.
pretend|tools|Handy Helper Workbench|Little Sprout|36|84|49.99|a|Hammer, saw, drill and 50 nuts and bolts. Safety goggles for very serious carpentry.
pretend|kitchen|Cash Register with Working Calculator|Kazoo Kids|36|96|24.99|a|Scanner beeps, drawer pops, play money included. Learn to make change (or keep it).
pretend|phone|Walkie-Talkie Spy Set|Gizmotron|60|144|29.99|a|Two-way radios with a range of a quarter mile and Morse code buttons. Over and out.
pretend|kitchen|Shopping Cart with Play Groceries|Little Sprout|24|72|29.99|a|A sturdy cart filled with pretend cereal, milk, eggs and a very small watermelon.
pretend|costume|Princess Dress-Up Trunk|Puddlejump|36|96|34.99|g|Four gowns, a tiara, wand and shoes that click on the kitchen floor.
pretend|costume|Firefighter Dress-Up Set|Bumblebee Toy Co.|36|84|24.99|a|Helmet, jacket, extinguisher that sprays water and a siren that says "Stand back!"
pretend|tools|Doctor's Kit with Real Stethoscope|Kazoo Kids|36|96|14.99|a|Listen to heartbeats, check reflexes and hand out pretend lollipops.
pretend|phone|Toy Cellular Phone with Lights|Kazoo Kids|12|48|9.99|a|Ring-ring! A flip phone just like Mom's, but with friendlier ringtones.
pretend|kitchen|Tea Party Set, 24 pieces|Puddlejump|36|96|16.99|g|Teapot, cups, saucers and cakes for the stuffed animals' afternoon tea.
rc|rccar|Turbo Thunder RC Monster Truck|Gizmotron|72|1200|49.99|b|Six-wheel drive climbs over couches. Rechargeable battery pack. Fast. Really fast.
rc|rccar|Mini Racer RC Car 2-pack|Gizmotron|60|144|24.99|a|Two pocket-size racers on different frequencies, so you can race your brother.
rc|rcplane|Sky Hawk RC Airplane|Gizmotron|120|1200|79.99|b|Foam glider with propeller motor. Practices patience, flies in the park.
rc|rcboat|Splash Dash RC Speedboat|Gizmotron|96|1200|39.99|a|For pools and ponds. Self-righting hull for the inevitable wipeout.
rc|rccar|Stunt Flipper 360 RC Car|Gizmotron|72|144|34.99|b|Flips, spins and drives upside down. The walls will never be the same.
rc|robot|Remote Control Robot Butler|Gizmotron|72|1200|59.99|a|Carries snacks on his tray and says "Very good, sir." Batteries not included, as usual.
rc|rccar|Toddler's First Remote Bus|Little Sprout|24|60|24.99|a|Big buttons, gentle speed and a horn that plays a song.
rc|rcplane|Mini Helicopter Indoor Flyer|Gizmotron|120|1200|49.99|a|Hovers in the living room. Keep away from the ceiling fan.
plush|bear|Snugglesworth Teddy Bear, 18 inch|Little Sprout|0|1200|24.99|a|A classic jointed bear with a satin bow and the softest fur we could find.
plush|bear|Bean Bag Buddies Lion|Kazoo Kids|36|1200|5.99|a|A floppy, pellet-filled lion with a heart tag. Collect the whole zoo.
plush|bear|Tickle Monster Giggling Plush|Wobbleworks|18|72|29.99|a|Squeeze his tummy and he laughs, shakes and rolls on the floor.
plush|owl|Gabbo the Talking Owl|Wobbleworks|72|1200|34.99|a|Learns words as you play with him, blinks his big eyes, and talks in his own language until you teach him yours.
plush|giraffe|Giant Plush Giraffe, 4 feet tall|Little Sprout|12|1200|49.99|a|Taller than most kindergartners and twice as huggable.
plush|bear|Sleepytime Glow Lamb|Little Sprout|0|36|19.99|a|Soft lamb whose tummy glows and plays lullabies for ten minutes.
plush|owl|Virtual Pet Plush Penguin|Wobbleworks|72|144|19.99|a|A plush penguin with a clip-on virtual pet to feed and play with.
plush|bear|Puppet Pals Hand Puppet Set|Kazoo Kids|36|96|14.99|a|Four animal hand puppets and a folding theater.
plush|dino|Dino-Mite Plush Stegosaurus|Kazoo Kids|12|96|12.99|a|Green and squishy, with felt spikes and a big goofy grin.
plush|owl|Pocket Pets Collectible Kittens 6-pack|Puddlejump|48|120|9.99|g|Six fuzzy kittens with collars and tiny baskets.
ride|bike|Rocket 16-inch Bike with Training Wheels|Puddlejump|48|96|89.99|a|Streamers, a bell and training wheels that come off when you're ready.
ride|bike|BMX Freestyle 20-inch Bike|Mighty Mo Toys|84|144|129.99|b|Pegs, stunt bars and a frame tough enough for curb hops.
ride|scooter|Kick Scooter, Folding Aluminum|Mighty Mo Toys|72|1200|79.99|a|The scooter everyone is riding this fall. Folds to fit in a locker.
ride|wagon|Classic Red Wagon|Little Sprout|12|96|69.99|a|All-steel wagon with rubber tires. Hauls toys, groceries and little brothers.
ride|bike|Tricycle with Push Handle|Little Sprout|18|60|59.99|a|A parent push handle for the early days, a bell for every day.
ride|scooter|Power Wheels-style Jeep 6V|Bumblebee Toy Co.|36|84|179.99|a|Battery-powered ride-on with forward, reverse and a top speed of 2.5 mph.
ride|wagon|Rocking Horse Pony|Little Sprout|12|48|39.99|a|Plush pony on sturdy rockers. Neighs when you squeeze its ear.
ride|scooter|Inline Skates Adjustable, with Pads|Mighty Mo Toys|72|1200|49.99|a|Adjusts four sizes as feet grow. Includes knee, elbow and wrist pads.
outdoor|ball|Super Bounce Playground Ball 3-pack|Kazoo Kids|24|1200|9.99|a|Three bright balls for four square, kickball and dodgeball.
outdoor|kite|Rainbow Dragon Kite, 6 feet|Kazoo Kids|60|1200|14.99|a|A long-tailed dragon that flies in the lightest breeze.
outdoor|watergun|Super Soaker-style Hydro Blaster|Mighty Mo Toys|72|1200|24.99|a|Pump it up and drench the neighborhood from forty feet.
outdoor|ball|Junior Basketball Hoop, Adjustable|Mighty Mo Toys|36|120|49.99|a|Adjusts from 4 to 6 feet. Swish!
outdoor|ball|Foam Football Whistler|Kazoo Kids|60|1200|7.99|a|Whistles as it spirals through the air.
outdoor|sandbox|Turtle Sandbox with Lid|Little Sprout|12|72|39.99|a|Holds 150 pounds of sand, and the lid keeps the cats out.
outdoor|kite|Bubble Machine Deluxe|Kazoo Kids|24|96|14.99|a|Hundreds of bubbles a minute. Includes 32 oz of bubble solution.
outdoor|watergun|Water Balloon Launcher|Mighty Mo Toys|96|1200|14.99|a|Three-person slingshot that sends water balloons over the fence. Use responsibly.
outdoor|sandbox|Backyard Explorer Tent|Puddlejump|36|120|29.99|a|Pop-up dome tent for backyard campouts and living room forts.
outdoor|ball|Pogo Stick, Jumbo Spring|Mighty Mo Toys|84|1200|29.99|a|Boing! A sturdy steel pogo stick for kids up to 120 pounds.
electronic|console|Game Station 64 Console with 2 Controllers|Gizmotron|72|1200|129.99|a|Sixty-four bits of pure fun. Includes two controllers and a racing game.
electronic|handheld|Pocket Game Color Handheld|Gizmotron|72|1200|69.99|a|Play anywhere in full color! Runs on two AA batteries for ten hours.
electronic|handheld|Pocket Monsters Red Version Game Pak|Gizmotron|72|1200|29.99|a|Catch, train and trade 150 pocket monsters. The game every kid is asking for.
electronic|console|Dream Console 128 with Modem|Gizmotron|96|1200|199.99|a|The newest console: 128 bits and a built-in modem for playing online. Launched 9/9/99.
electronic|handheld|Virtual Pet Egg Keychain|Wobbleworks|72|1200|9.99|a|Feed it, clean it, love it. Pause button for school hours.
electronic|phone|Electronic Diary with Password|Gizmotron|96|1200|24.99|g|Secret voice password, a clock and room for 100 phone numbers. Keep out, little brother!
electronic|console|Karaoke Star Machine with Microphone|Gizmotron|72|1200|59.99|a|Sing along with any cassette or CD. Echo effect makes everyone sound like a star.
electronic|handheld|Handheld LCD Space Battle Game|Wobbleworks|72|1200|12.99|a|Blast the alien fleet on a tiny screen. Beeps loudly; volume switch thoughtfully included.
electronic|computer|Kids' Digital Camera|Gizmotron|96|1200|69.99|a|Takes 20 low-resolution photos you can download to the family computer. The future!
electronic|console|Dance Pad Game Mat|Gizmotron|96|1200|39.99|a|Step on the arrows in time to the music. Plugs into Game Station 64.
baby|rattle|Busy Bee Rattle &amp; Teether|Little Sprout|0|12|6.99|a|Lightweight rattle with soft teething rings. Freezable for sore gums.
baby|rings|Stack-a-Ring Rainbow Tower|Little Sprout|6|24|7.99|a|Five colorful rings on a rocking base. A first-birthday classic.
baby|mobile|Starry Night Crib Mobile|Little Sprout|0|9|34.99|a|Plays three lullabies while the moon and stars turn slowly overhead.
baby|rattle|Activity Gym Play Mat|Little Sprout|0|12|44.99|a|Arches with dangling toys, a mirror and crinkly fabric for tummy time.
baby|rings|Shape Sorter Bucket|Little Sprout|12|36|9.99|a|Twelve chunky shapes, one bucket, endless "it goes here!"
baby|xylophone|Pull-Along Xylophone|Little Sprout|12|36|14.99|a|Pull it and it plays, or bang the keys with the mallet.
baby|mobile|Bath Time Squirters 6-pack|Little Sprout|6|36|5.99|a|Six bath animals that squirt, float and make bath time splashier.
baby|xylophone|Musical Activity Cube|Little Sprout|6|36|29.99|a|Five sides of buttons, beads, gears and a song for every one.
baby|rattle|Soft Book: Farm Friends|Little Sprout|0|24|9.99|a|Crinkly, chewable cloth book with a squeaky cow.
baby|rings|Walker Wagon with Blocks|Little Sprout|9|24|29.99|a|Sturdy push wagon for first steps, filled with 20 wooden blocks.
"""

BRANDS = ["Gizmotron", "Starhopper", "Mighty Mo Toys", "Plinko Industries", "Tinkerton", "Bumblebee Toy Co.",
          "Kazoo Kids", "Little Sprout", "Wobbleworks", "Puddlejump"]

TOP10 = ["Gabbo the Talking Owl", "Pocket Monsters Red Version Game Pak", "Megabot 3000 Transforming Robot",
         "Kick Scooter, Folding Aluminum", "Dream Console 128 with Modem", "Snap-Brix Space Station Command Base",
         "Starlight Ballerina Barbara Doll", "Robo-Pup Electronic Dog", "Talking Explorer Globe", "Retro Diner Play Kitchen"]

PARENT_REVIEWS = [
    ("A big hit!", "My son has played with this every single day since his birthday. Worth every penny."),
    ("Grandma approved", "Bought this for my granddaughter and she hasn't put it down. Sturdy and well made."),
    ("Great value", "Better quality than I expected for the price. Arrived in two days, gift-wrapped beautifully."),
    ("Batteries!!", "Fun toy, but buy a pack of batteries when you order. Trust me on this one."),
    ("Educational AND fun", "Sneaky learning. The kids think it's just a game."),
    ("Survived the twins", "If it can survive my twins, it can survive anything. Five stars."),
    ("Holiday lifesaver", "Every store in town was sold out. eToyz had it on my doorstep in three days."),
    ("Noisy but loved", "It is LOUD. My daughter adores it. I adore the volume switch."),
]
