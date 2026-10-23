"""gh_themes2.py -- Hearth, Prairie, Boulevard, Athenaeum, Arcade homepage themes (all content original)."""
from gh_tdefs import S, SUB, T

T2 = []

# ------------------------------------------------------------------ Hearth
T2.append(T('family', 'Hearth', 'Porch', 5, age=(30, 60),
    titles=['The {last} Family Home Page', 'Welcome to the {last} Household!', 'The {last}s of {town}',
            '{last} Family Newsletter Online', 'Home Sweet {last} Home'],
    intro=['Welcome to our little corner of the World Wide Web! We are the {last} family of {town}, {state}: '
           '{first}, our three kids, one dog, two cats and a goldfish named Captain. This page is mostly so Grandma '
           'can see pictures without us mailing them, so hi Grandma!',
           'Hello and welcome! {first} here, the "webmaster" of the family (my husband says that title is a stretch). '
           'Here you will find news, photos and the dates of our summer reunion.',
           'This is the {last} family web site. Please excuse the mess, it is always under construction, just like '
           'our kitchen.'],
    sections=[
        S('list', ['Meet the Family', 'Who\'s Who'], [
            '<B>{first}</B> - Mom/Dad, chief cook, webmaster', '<B>Tyler</B> (12) - into skateboards and '
            'Monstropals', '<B>Ashley</B> (9) - wants to be a veterinarian, practices on the cats',
            '<B>Baby Cody</B> (2) - into everything, especially the VCR', '<B>Buster</B> - our dog, part beagle, part '
            'mystery', '<B>Mittens and Socks</B> - the cats, who run the house', '<B>Captain</B> - goldfish, age 4, '
            'a legend'], n=(4, 7)),
        S('log', ['Family News', 'What\'s New With Us'], [
            'Tyler made the honor roll! We are so proud. He gets to pick the pizza Friday.',
            'Ashley lost her first tooth at the dinner table (in the mashed potatoes).',
            'We finally finished the deck. Only took two summers and one trip to the emergency room.',
            'The whole family had the flu. Do not come over. We mean it.',
            'Baby Cody said his first word: "uh-oh". Appropriate.', 'Buster ate a whole birthday cake off the '
            'counter. He is fine. The cake is not.', 'We got a new computer! 400 megahertz! That is why this page '
            'exists.', 'Family reunion date is set! See the Reunion page for details.'], n=(3, 6)),
        S('photos', ['Family Photos', 'Our Photo Album'], [('photo_family.gif', 'The whole gang at the lake'),
                                                           ('photo_baby.gif', 'Baby Cody\'s first birthday'),
                                                           ('photo_house.gif', 'Our house (the deck is in the back)'),
                                                           ('photo_dog.gif', 'Buster, the cake thief'),
                                                           ('photo_cake.gif', 'Before Buster got to it')], n=(2, 4)),
        S('links', ['Family & Friends Pages', 'Our Favorite Links'], n=(3, 5)),
    ],
    subpages=[SUB('reunion.html', ['Family Reunion 1999', 'Reunion Info'], [
        S('para', ['Reunion Details'], ['The {last} Family Reunion will be held the second Saturday in July at '
                                        'Riverside Park, Pavilion B. Bring a covered dish and a lawn chair. Uncle Lou is '
                                        'bringing his famous baked beans again (sorry). Horseshoes start at 2.'],
          n=(1, 1)),
        S('table', ['Who\'s Bringing What'], [('Aunt Marge', 'Potato salad'), ('Uncle Lou', 'The beans'),
                                              ('Cousin Darla', 'gelatin salad (green)'), ('The {last}s', 'Hot dogs and '
                                                                                                    'buns'),
                                              ('Grandma', 'Pies, plural')], n=(3, 5))], prob=0.6)],
    images=['photo_family.gif', 'photo_house.gif', 'heart.gif'], bullets=['ball_red.gif', 'ball_green.gif',
                                                                          'bullet_heart.gif'],
    lines=['rainbow_hr.gif', 'line_hearts.gif', 'line_rope.gif'],
    styles=['clouds', 'gingham', 'retro_tan', 'pastel_flowers', 'marble', 'border_green', 'plain'],
    layouts=['single', 'sidebar', 'frames'], midi=['lullaby', 'elevator', 'ragtime', None], ring='family',
    keywords='family home page photos news reunion kids', desc=['The {last} family: news, photos and reunion info',
                                                               'Family home page from {town}, {state}'],
    gb=['Hi everybody! Love, Grandma', 'Cute kids!', 'Can\'t wait for the reunion!', 'Tell Buster he is a good boy.']))

T2.append(T('baby', 'Hearth', 'Nursery', 4, age=(24, 38),
    titles=['Welcome Baby {baby}!', '{baby}\'s Very Own Web Page', 'Our Little Miracle: {baby}', 'Baby {baby} Online'],
    entities=[dict(baby='Kaylee', bday='March 3, 1999', weight='7 lbs 4 oz'),
              dict(baby='Brandon', bday='November 18, 1998', weight='8 lbs 11 oz'),
              dict(baby='Madison', bday='June 30, 1999', weight='6 lbs 15 oz'),
              dict(baby='Tanner', bday='January 1, 1999 (first baby of the year in our county!)', weight='7 lbs 9 oz'),
              dict(baby='Emma and Ethan (twins!)', bday='August 12, 1999', weight='5 lbs 2 oz and 5 lbs 8 oz')],
    intro=['Hi! My name is <B>{baby}</B> and this is my web page. My mommy and daddy made it for me because I can\'t '
           'type yet. I was born on {bday} and I weighed {weight}.',
           'We are so happy to announce the arrival of our baby, <B>{baby}</B>, born {bday}, {weight}. Mom and baby '
           'are doing great. Dad is tired.'],
    sections=[
        S('table', ['Baby Stats', 'All About Me'], [('Born', '{bday}'), ('Weight', '{weight}'), ('Length', '20 '
                                                     'inches'), ('Hair', 'Not much yet!'), ('Eyes', 'Blue (for now)'),
                                                    ('Favorite thing', 'Being held'), ('Least favorite thing',
                                                                                       'Bath time'),
                                                    ('Sleeps', 'Not at night, apparently')], n=(5, 8)),
        S('log', ['Milestones', 'Baby\'s Firsts'], ['First smile (or gas, Grandpa says)', 'First time rolling over '
                                                     '(off the couch, onto a pillow, everyone is fine)',
                                                     'First tooth! Ouch.', 'First real food: mashed bananas. Most of '
                                                                          'it went on the dog.',
                                                     'Slept through the night!!! We cried with happiness.',
                                                     'First time saying "dada". Mommy is not speaking to Daddy.',
                                                     'First steps! Then sat down really fast.'], n=(3, 6)),
        S('photos', ['Photos', 'Baby Pictures'], [('photo_baby.gif', 'Home from the hospital'),
                                                  ('photo_family.gif', 'Meeting the grandparents'),
                                                  ('photo_cake.gif', 'Getting ready for the first birthday!')],
          n=(1, 3)),
        S('poems', ['A Poem For {baby}'], [('Little One', 'Ten little fingers\nten little toes\na tiny little '
                                            'yawn\nand a button nose\n\nWe waited so long\nand now you are here\nour '
                                            'whole world is you\nour little dear')], n=(1, 1), prob=0.5),
        S('links', ['Links For New Parents', 'Other Baby Pages'], n=(2, 4)),
    ],
    images=['dancing_baby.gif', 'heart.gif', 'photo_baby.gif'], bullets=['bullet_heart.gif', 'ball_pink.gif',
                                                                         'ball_blue.gif'],
    lines=['line_bows.gif', 'line_hearts.gif', 'rainbow_line.gif'], styles=['pastel_flowers', 'pastel_hearts',
                                                                         'clouds', 'border_pink'],
    layouts=['single', 'splash'], midi=['lullaby', 'kitten_waltz'], ring='family',
    keywords='baby announcement newborn milestones photos', desc=['Baby {baby}\'s web page: stats, milestones, photos'],
    gb=['Congratulations!!!', 'What a cutie!', 'Welcome to the world, {baby}!']))

T2.append(T('genealogy', 'Hearth', 'Attic', 3, age=(45, 80),
    titles=['The {last} Family Tree', '{last} Genealogy: From the Old Country to {state}', 'Roots of the {last} Clan'],
    intro=['This page is the result of fourteen years of research in libraries, courthouses, churchyards and, more '
           'recently, on the Internet. If you are a {last}, or think you might be, please e-mail me!',
           'Our family came to America in 1887 with one trunk and a recipe for dumplings. This is their story.'],
    sections=[
        S('table', ['Family Line', 'Direct Line'], [('Johann {last}', 'b. 1841, d. 1919. Came over in 1887.'),
                                                    ('Wilhelmina (Brandt) {last}', 'b. 1845, d. 1922. Brought the '
                                                                                   'dumpling recipe.'),
                                                    ('August {last}', 'b. 1871, d. 1950. Farmer, fiddler.'),
                                                    ('Rose (Kline) {last}', 'b. 1878, d. 1961. Had eleven children.'),
                                                    ('Walter {last}', 'b. 1902, d. 1988. Ran the hardware store.'),
                                                    ('Dorothy (Yoder) {last}', 'b. 1906, d. 1995. Best pie in the '
                                                                                'county.'),
                                                    ('Robert {last}', 'b. 1931. My dad!')], n=(5, 7)),
        S('para', ['Stories', 'Family Legends'], [
            'Family legend says Johann won the farm in a card game. The deed says he bought it for $340. I prefer the '
            'legend.',
            'Great-Aunt Hilda was the first woman in the county to drive a car. She drove it into the creek on the '
            'first day and never drove again.',
            'During the Depression Grandpa Walter traded hammers for eggs. The store survived. So did the hens.'],
          n=(2, 3)),
        S('list', ['Surnames I Am Researching', 'Looking For'], ['{last}', 'Brandt', 'Kline', 'Yoder', 'Haskell',
                                                                 'Pettibone', 'Sorensen', 'Moreau'], n=(4, 7)),
        S('links', ['Genealogy Links'], n=(2, 4)),
    ],
    images=['photo_house.gif', 'photo_family.gif'], bullets=['ball_green.gif', 'ball_yellow.gif'],
    lines=['line_rope.gif', 'rainbow_hr.gif'], styles=['parchment', 'retro_tan', 'marble', 'wood'],
    layouts=['single', 'sidebar'], midi=['anthem', 'ragtime', None], ring='family',
    keywords='genealogy family tree {last} ancestors surnames', desc=['{last} family genealogy and stories'],
    gb=['I think we are related! E-mail me.', 'My great-grandma was a Kline too!']))

T2.append(T('wedding', 'Hearth', 'Garden', 2, age=(23, 35),
    titles=['{first} & {partner}\'s Wedding Page', 'We\'re Getting Married!'],
    entities=[dict(partner='Chris'), dict(partner='Jamie'), dict(partner='Sam')],
    intro=['We are getting married!!! After four years, one cross-country move and a proposal on a Ferris wheel, '
           '{first} and {partner} are tying the knot. Here is everything our guests need to know.'],
    sections=[
        S('table', ['The Details'], [('Date', 'Saturday, June 10, 2000 (we are a millennium wedding!)'),
                                     ('Ceremony', '2:00 pm, Lakeside Chapel'), ('Reception', '5:00 pm, the {town} '
                                                                                            'Elks Lodge'),
                                     ('Dress code', 'Nice but comfy. There will be dancing.'),
                                     ('Registry', 'The Home Barn and Linens \'n\' Lamps')], n=(4, 5)),
        S('para', ['How We Met'], ['We met in a chat room in 1995! {partner} typed "anybody here like bowling?" and I '
                                   'said yes even though I had never bowled. We met in person a month later (at the '
                                   'bowling alley, of course). I bowled a 41. {partner} still married me.'],
          n=(1, 1)),
        S('list', ['The Wedding Party'], ['Maid of honor: Kristy', 'Best man: Doug', 'Flower girl: Ashley (age 6)',
                                          'Ring bearer: Buster the dog (if he behaves)'], n=(3, 4)),
        S('links', ['Links'], n=(2, 3)),
    ],
    images=['heart.gif', 'twinkle.gif'], bullets=['bullet_heart.gif'], lines=['line_hearts.gif', 'line_bows.gif'],
    styles=['pastel_hearts', 'marble', 'pastel_flowers'], layouts=['single'], midi=['lovesong'], ring='family',
    keywords='wedding engagement millennium wedding details', desc=['Wedding page for {first} and {partner}'],
    gb=['Congratulations you two!', 'A bowling alley romance!!!']))

T2.append(T('gardening', 'Hearth', 'Garden', 2, age=(40, 75),
    titles=['{first}\'s Garden Journal', 'Tomatoes & Tulips'],
    intro=['Welcome to my garden! Zone 5, clay soil, too many rabbits. I grow vegetables, roses and an embarrassing '
           'number of zucchini.'],
    sections=[
        S('log', ['Garden Journal'], ['Planted tomatoes (Big Boy, Early Girl, Cherry). Fingers crossed for no frost.',
                                      'Rabbits ate the lettuce. All of it. I saw one wink at me.',
                                      'First zucchini! By the end of the week I will be leaving them on porches.',
                                      'Roses blooming. The "Grandma\'s Pink" is the best it has ever been.',
                                      'Put the garden to bed for winter. See you in April, old friend.'], n=(3, 5)),
        S('list', ['Tips'], ['Coffee grounds for the roses', 'Marigolds keep bugs away', 'Water in the morning',
                             'Never plant more than two zucchini plants. NEVER.'], n=(3, 4)),
        S('links', ['Garden Links'], n=(2, 3)),
    ],
    images=['photo_house.gif'], bullets=['ball_green.gif'], lines=['line_bows.gif', 'rainbow_hr.gif'],
    styles=['pastel_flowers', 'grass', 'parchment'], layouts=['single'], midi=['kitten_waltz', None], ring='family',
    keywords='gardening vegetables roses zucchini journal', desc=['Garden journal from zone 5'],
    gb=['Please send zucchini. Just kidding, do not.']))

T2.append(T('xmasletter', 'Hearth', 'Porch', 1, age=(40, 70),
    titles=['The {last} Family Holiday Letter 1998'],
    intro=['Season\'s Greetings from the {last} household! This year instead of photocopying 80 letters we are putting '
           'it on the World Wide Web. Progress!'],
    sections=[
        S('para', ['Our Year'], ['{first} retired from the plant in March and immediately took up woodworking. We now '
                                 'own eleven birdhouses. The birds are thrilled.',
                                 'We drove the RV to see the World\'s Second Largest Ball of Twine. It was large.',
                                 'Our oldest got engaged, our middle one got a job in the city, and the youngest is '
                                 'learning to drive. Pray for us.'], n=(2, 3)),
        S('photos', ['Photos'], [('photo_family.gif', 'Thanksgiving'), ('photo_house.gif', 'The house in the snow')],
          n=(1, 2)),
    ],
    images=['snowman.gif', 'twinkle.gif'], bullets=['bullet_star.gif'], lines=['line_stars.gif'],
    styles=['snow'], layouts=['single'], midi=['holiday'], ring='family', keywords='christmas holiday letter family news',
    desc=['Holiday letter from the {last} family'], gb=['Merry Christmas to you too!']))

# ------------------------------------------------------------------ Prairie
T2.append(T('kitten', 'Prairie', 'Litterbox', 7, age=(10, 70), gender='f',
    titles=['{cat}\'s Purrfect Page', 'Kitty Kingdom', 'The Cats of {town}', 'Meow! Welcome To {cat}\'s World',
            'My Kitties', '{handle}\'s Cat Corner', 'Whiskers & Purrs'],
    entities=[dict(cat='Princess Fluffington', cat2='Mr. Biscuits'), dict(cat='Tiger', cat2='Pooky'),
              dict(cat='Snowball', cat2='Midnight'), dict(cat='Sir Purrs-a-Lot', cat2='Muffin'),
              dict(cat='Cleo', cat2='Smokey'), dict(cat='Pumpkin', cat2='Domino'), dict(cat='Gizmo', cat2='Peaches')],
    intro=['Meow and welcome!!! This is the home page of <B>{cat}</B> and <B>{cat2}</B>, the two most spoiled kitties '
           'in {town}. My human typed this for me because my paws are too fluffy for the keyboard.',
           'Welcome to my kitty page! I love cats more than anything (except maybe chocolate). Here you can meet my '
           'babies, {cat} and {cat2}, and read my cat care tips.',
           'Purr purr purr! This page is all about my cats. If you are a dog person, it is okay, you can stay too.'],
    sections=[
        S('table', ['Meet {cat}', 'Kitty Fact File'], [('Name', '{cat}'), ('Breed', 'Fancy (we think)'),
                                                       ('Age', '3 and a half'), ('Likes', 'Tuna, sunbeams, my sweaters'),
                                                       ('Dislikes', 'The vacuum, Tuesdays, the vet'),
                                                       ('Best trick', 'Opens the cabinet with the treats'),
                                                       ('Nicknames', 'Fluffy-bum, Her Majesty, Sweet Pea')], n=(4, 7)),
        S('list', ['Things {cat2} Has Knocked Off The Table', 'Kitty Crimes'], [
            'A glass of milk (full)', 'My homework', 'The TV remote (behind the couch, gone forever)',
            'A whole plant', 'Grandma\'s ceramic owl', 'Three pens in a row while looking at me', 'The phone, during a '
            'call'], n=(3, 6)),
        S('list', ['Kitty Care Tips', 'How To Be A Good Cat Mom'], [
            'Always have fresh water out.', 'Brush long-haired cats every day or they get knots!',
            'Cats need a scratching post or your couch will become one.', 'Take your kitty to the vet once a year.',
            'Never give cats chocolate or onions!', 'Spay and neuter your pets!!!', 'Give LOTS of love.'], n=(4, 6)),
        S('photos', ['Kitty Pics', 'Photo Gallery'], [('photo_cat.gif', '{cat} in her favorite sunbeam'),
                                                      ('kitten.gif', 'A drawing of {cat2} I made'),
                                                      ('photo_house.gif', 'Our house, a.k.a. the Cat Palace')],
          n=(1, 3)),
        S('poems', ['A Poem About {cat}'], [('Ode To {cat}', 'Soft as a cloud\nand twice as proud\nyou sleep all '
                                             'day\nand purr out loud\n\nYou wake me at five\nyou want your food\nI '
                                             'love you anyway\nyou furry dude')], n=(1, 1), prob=0.4),
        S('links', ['Other Kitty Pages', 'Cat Links'], n=(3, 6)),
    ],
    images=['kitten.gif', 'heart.gif', 'photo_cat.gif'], bullets=['bullet_paw.gif', 'bullet_heart.gif', 'ball_pink.gif'],
    lines=['line_paws.gif', 'line_hearts.gif', 'line_bows.gif'],
    styles=['pastel_hearts', 'pastel_flowers', 'paws', 'border_pink', 'glitter', 'clouds', 'border_purple'],
    layouts=['single', 'single', 'sidebar', 'splash'], midi=['kitten_waltz', 'lullaby'], ring='kitty',
    keywords='cats kittens kitty {cat} pet page cat care', desc=['Home page of {cat} and {cat2}, two spoiled cats',
                                                                 'Kitty pictures and cat care tips'],
    gb=['Give {cat} a scratch behind the ears for me!', 'My cat knocks stuff off the table too!!',
        'Purrrrfect page!', 'Meow! (my cat typed that)'], features={'awards': ['award_purrfect.gif']}))

T2.append(T('dog', 'Prairie', 'Kennel', 5, age=(15, 70),
    titles=['{dog}\'s Dog House', 'Woof! It\'s {dog}!', 'The {last} Kennel', 'Life With {dog}', 'Doggone Good Page'],
    entities=[dict(dog='Buster', breed='beagle mix'), dict(dog='Duke', breed='German shepherd'),
              dict(dog='Biscuit', breed='golden retriever'), dict(dog='Peanut', breed='chihuahua'),
              dict(dog='Moose', breed='Newfoundland (150 lbs of love)'), dict(dog='Ziggy', breed='border collie')],
    intro=['WOOF! Welcome to the home page of <B>{dog}</B>, a {breed} who thinks he is a person. Grab a biscuit and '
           'stay a while.',
           'This page is dedicated to my best friend, {dog}. Dogs are the best. That is all.'],
    sections=[
        S('table', ['About {dog}', 'Dog Stats'], [('Breed', '{breed}'), ('Age', '5 (35 in dog years)'),
                                                  ('Favorite toy', 'A tennis ball that is 90% slobber'),
                                                  ('Favorite food', 'Anything that falls on the floor'),
                                                  ('Tricks', 'Sit, shake, play dead, open the fridge (bad)'),
                                                  ('Enemy', 'The mailman (they are working on it)')], n=(4, 6)),
        S('list', ['Things {dog} Has Eaten', 'Hall of Shame'], ['A whole stick of butter', 'My retainer ($300)',
                                                               'A birthday cake', 'Christmas tinsel (it came out '
                                                                                  'fine)',
                                                               'One (1) shoe, left', 'The homework. Really.'],
          n=(3, 5)),
        S('list', ['Dog Training Tips'], ['Be patient!', 'Treats work better than yelling.', 'Walk your dog every day.',
                                          'Crate training is not mean, dogs like dens.',
                                          'Never leave a cake on the counter.'], n=(3, 5)),
        S('photos', ['Photos'], [('photo_dog.gif', '{dog} at the park'), ('puppy.gif', '{dog} as a puppy (drawing)'),
                                 ('photo_family.gif', '{dog} with the family')], n=(1, 3)),
        S('links', ['Dog Links'], n=(3, 5)),
    ],
    images=['puppy.gif', 'photo_dog.gif'], bullets=['bullet_paw.gif', 'ball_red.gif'],
    lines=['line_paws.gif', 'line_rope.gif'], styles=['paws', 'grass', 'denim', 'clouds', 'gingham'],
    layouts=['single', 'sidebar'], midi=['hoedown', 'kitten_waltz', None], ring='dogs',
    keywords='dog {dog} {breed} pet tricks training', desc=['Home page of {dog} the {breed}'],
    gb=['Good boy {dog}!!!', 'My dog ate my retainer too!', 'Woof woof (that means great page)']))

T2.append(T('smallpet', 'Prairie', 'Burrow', 4, age=(9, 40),
    titles=['{pet}\'s Hamster Habitat', 'Ferret Frenzy!', 'The Fishbowl', 'Bunny Hop Home Page'],
    entities=[dict(pet='Nibbles', kind='hamster', kinds='hamsters'), dict(pet='Bandit', kind='ferret', kinds='ferrets'),
              dict(pet='Bubbles', kind='goldfish', kinds='fish'), dict(pet='Thumper', kind='bunny', kinds='rabbits'),
              dict(pet='Sir Wiggles', kind='guinea pig', kinds='guinea pigs')],
    intro=['Hello! This page is about my {kind}, <B>{pet}</B>! {kinds} make GREAT pets and I want everyone to know it.',
           'Welcome to the home of {pet} the {kind}. Small pets need love too!'],
    sections=[
        S('table', ['{pet} Facts'], [('Species', '{kind}'), ('Age', '1 year'), ('Color', 'Golden brown and white'),
                                     ('Favorite snack', 'Sunflower seeds / carrots'), ('Hobbies', 'Running, napping, '
                                                                                                   'escaping')],
          n=(3, 5)),
        S('log', ['Daily Diary', '{pet}\'s Diary'], ['Ran 4 miles on the wheel (my dad measured it).',
                                                    'Escaped! Found in the sock drawer 6 hours later.',
                                                    'Got a new tube for the cage. Will not come out of it.',
                                                    'Stuffed 11 seeds in cheeks at once. New record.',
                                                    'Had a bath (fish do not count). Was not happy.'], n=(3, 5)),
        S('list', ['Care Tips For {kinds}'], ['Clean the cage every week', 'Fresh water every day',
                                               'Do not use cedar bedding', 'Handle gently!', 'Give them toys to chew',
                                               'Read a book about them before you buy one'], n=(3, 5)),
        S('links', ['Links'], n=(2, 4)),
    ],
    images=['hamster.gif', 'heart.gif'], bullets=['bullet_paw.gif', 'ball_yellow.gif'],
    lines=['line_paws.gif', 'rainbow_line.gif'], styles=['pastel_flowers', 'bubbles', 'paws', 'clouds'],
    layouts=['single'], midi=['kitten_waltz', 'chiptune'], ring='critters',
    keywords='{kind} small pet {pet} care tips', desc=['All about {pet} the {kind}'],
    gb=['{pet} is so cute!!!', 'Have you seen Hamster Shuffle?? LOL']))

T2.append(T('memorial', 'Prairie', 'Meadow', 4, age=(18, 70),
    titles=['In Loving Memory of {pet}', '{pet}: Forever In Our Hearts', 'Over The Rainbow Fields', 'Remembering {pet}'],
    entities=[dict(pet='Lady', kind='collie', years='1984 - 1998', photo='photo_dog.gif', spot='the porch'),
              dict(pet='Pepper', kind='cat', years='1981 - 1999', photo='photo_cat.gif', spot='the windowsill'),
              dict(pet='Rusty', kind='dog', years='1987 - 1998', photo='photo_dog.gif', spot='the porch'),
              dict(pet='Goldie', kind='horse', years='1975 - 1999', photo='photo_mountain.gif', spot='the far pasture'),
              dict(pet='Tux', kind='cat', years='1985 - 1999', photo='photo_cat.gif', spot='the windowsill')],
    intro=['This page is in memory of <B>{pet}</B>, our beloved {kind}, {years}. For fourteen years {pet} was part of '
           'our family. We miss her every day.',
           'I made this page because I do not know what else to do. {pet} was my best friend.'],
    sections=[
        S('para', ['Our Friend', 'About {pet}'], [
            '{pet} came to us as a tiny thing that fit in two hands. She grew up with our children, watched them leave '
            'for the school bus every morning from {spot} and was waiting there every afternoon.',
            'She was never fancy, never won a ribbon, never learned a single trick except the important one: knowing '
            'exactly when somebody needed company.',
            'In the end she was tired, and we held her and told her she was a good girl, and she was.'], n=(2, 3)),
        S('poems', ['A Poem', 'For {pet}'], [('The Rainbow Fields', 'Beyond the hill where the clover grows\nthere is a '
                                              'field that the sunlight knows\nwhere old friends run and never tire\nand '
                                              'nap in grass instead of by the fire\n\nAnd someday when my walking\'s '
                                              'done\nI\'ll find you waiting in the sun\nyou\'ll lift your head and '
                                              'know my call\nand we will walk home, after all')], n=(1, 1)),
        S('photos', ['Remembering'], [('{photo}', '{pet} in her favorite spot'),
                                      ('photo_house.gif', 'Home, where she waited on {spot}')], n=(1, 2), prob=0.7),
        S('para', ['Light A Candle'], ['If you have lost a pet too, please sign our guestbook and tell us their name. '
                                       'We will light a candle for them.'], n=(1, 1)),
    ],
    images=['candle.gif', 'rainbow_bridge.gif'], bullets=['bullet_heart.gif', 'bullet_star.gif'],
    lines=['rainbow_line.gif', 'line_stars.gif'], styles=['clouds', 'nebula', 'pastel_flowers', 'snow'],
    layouts=['single'], midi=['memorial'], ring='rainbow', keywords='pet memorial {pet} rainbow loss grief',
    desc=['A memorial page for {pet}', 'In memory of a beloved {kind}'],
    gb=['I am so sorry for your loss. My dog Sparky is waiting with her.', 'Lighting a candle for {pet} tonight.',
        'Beautiful poem. I cried.'], features={'nocounter': True, 'calm': True}))

T2.append(T('horse', 'Prairie', 'Meadow', 2, age=(12, 50), gender='f',
    titles=['Horse Crazy!', '{first}\'s Barn'],
    intro=['I am horse crazy and proud of it! I ride at Willow Creek Stables and I am saving up for my own horse '
           '(only $2,850 to go).'],
    sections=[
        S('table', ['Horses I Ride'], [('Chester', 'Quarter horse, 14 years, lazy but sweet'),
                                       ('Duchess', 'Appaloosa, spots everywhere, likes peppermints'),
                                       ('Rocket', 'Not as fast as his name'), ('Lady Grey', 'Old, wise, '
                                                                                            'teaches beginners')],
          n=(2, 4)),
        S('list', ['Horse Facts'], ['Horses can sleep standing up!', 'A horse\'s teeth take up more room in its head '
                                                                      'than its brain.',
                                    'Horses cannot throw up.', 'You measure horses in "hands".'], n=(3, 4)),
        S('links', ['Horse Links'], n=(2, 3)),
    ],
    images=['heart.gif'], bullets=['ball_yellow.gif'], lines=['line_rope.gif'],
    styles=['grass', 'wood', 'pastel_flowers'], layouts=['single'], midi=['hoedown', 'kitten_waltz'], ring='critters',
    keywords='horses riding stable barn', desc=['Horse crazy riding page'], gb=['Horse crazy too!!!']))

# ------------------------------------------------------------------ Boulevard
T2.append(T('fashion', 'Boulevard', 'Runway', 3, age=(14, 30), gender='f',
    titles=['{handle}\'s Style File', 'Platform Shoes & Butterfly Clips', 'What I\'m Wearing'],
    intro=['Welcome to my fashion page!!! Here you will find what\'s HOT and what\'s NOT for fall 1999, plus my '
           'shopping tips for the mall on a babysitting budget.'],
    sections=[
        S('table', ['Hot or Not', 'Fall 1999'], [('Platform sneakers', 'HOT'), ('Butterfly clips', 'SO HOT'),
                                                 ('Body glitter', 'HOT'), ('Choker necklaces', 'hot'),
                                                 ('Overalls with one strap down', 'over it'), ('Scrunchies', 'not'),
                                                 ('Cargo pants', 'HOT'), ('Frosted lip gloss', 'always hot'),
                                                 ('Slap bracelets', 'SO 1991')], n=(5, 9)),
        S('list', ['Mall Shopping Tips'], ['Go on a weeknight, less crowded', 'Check the clearance rack FIRST',
                                           'Bring a friend who will tell you the truth', 'Mix and match!',
                                           'Accessories make the outfit'], n=(3, 5)),
        S('links', ['Fashion Links'], n=(2, 4)),
    ],
    images=['heart.gif', 'twinkle.gif'], bullets=['bullet_heart.gif', 'ball_pink.gif'],
    lines=['line_bows.gif', 'line_hearts.gif'], styles=['leopard', 'glitter', 'border_pink', 'black_neon'],
    layouts=['single', 'sidebar'], midi=['techno', 'heartthrob'], ring='glam',
    keywords='fashion style trends platform shoes glitter', desc=['Fall 1999 fashion: what\'s hot and what\'s not'],
    gb=['Butterfly clips 4ever!', 'Your page is SO cute']))

T2.append(T('makeup', 'Boulevard', 'Vanity', 3, age=(15, 40), gender='f',
    titles=['Glamour Girl Beauty Tips', '{first}\'s Makeup Bag', 'Pretty In Pixels'],
    intro=['Hi gorgeous! Welcome to my beauty page. I am not a professional, but I have been doing makeup for my friends '
           'for proms and weddings for years. Here are my secrets!'],
    sections=[
        S('list', ['Beauty Tips', 'My Secrets'], ['Always take your makeup off before bed!', 'Less is more with blush.',
                                                  'Match your foundation to your neck, not your hand.',
                                                  'Ice cubes for puffy eyes', 'Drink water, it is the best beauty '
                                                                               'product', 'Blue eyeshadow: be brave or '
                                                                                          'be careful',
                                                  'Glitter goes everywhere. Plan accordingly.'], n=(4, 7)),
        S('table', ['Product Reviews'], [('Frost Bite lip gloss', '5/5, smells like bubblegum'),
                                         ('Mega Lash mascara', '3/5, clumpy'), ('Sparkle Dust body glitter', '4/5, '
                                                                                                             'found it '
                                                                                                             'in my cereal'),
                                         ('Nail polish "Alien Green"', '5/5, very 1999')], n=(3, 4)),
        S('links', ['Links'], n=(2, 4)),
    ],
    images=['twinkle.gif', 'heart.gif'], bullets=['bullet_star.gif', 'ball_purple.gif'],
    lines=['line_bows.gif', 'rainbow_line.gif'], styles=['glitter', 'pastel_flowers', 'marble', 'border_purple'],
    layouts=['single'], midi=['heartthrob', None], ring='glam', keywords='makeup beauty tips product reviews',
    desc=['Beauty and makeup tips'], gb=['Alien Green is my fave too!']))

T2.append(T('prom', 'Boulevard', 'Boutique', 3, age=(16, 19), gender='f',
    titles=['PROM 1999!!!', 'My Prom Night', 'Senior Prom Photo Album'],
    intro=['Prom was the BEST NIGHT EVER (except for the part where it rained). Here are all the pictures and the '
           'story. The theme was "A Night Under the Stars" and it was in the gym but they made it look nice.'],
    sections=[
        S('table', ['The Details'], [('Dress', 'Lavender, spaghetti straps, $89 on sale!!!'), ('Date', 'Kevin (just '
                                                                                                     'friends)'),
                                     ('Limo', 'White stretch, split with 8 people'), ('Dinner', 'Pasta Palace'),
                                     ('Song of the night', '"Forever Tonight" by Northbound'),
                                     ('After party', 'Bowling until 3 am')], n=(4, 6)),
        S('photos', ['Pictures'], [('photo_me2.gif', 'Me in my dress!'), ('photo_family.gif', 'Our group before the '
                                                                                             'limo'),
                                   ('photo_car.gif', 'The limo (it was white, the pic is weird)')], n=(2, 3)),
        S('links', ['Friends\' Pages'], n=(2, 4)),
    ],
    images=['twinkle.gif', 'heart.gif'], bullets=['bullet_star.gif'], lines=['line_stars.gif', 'line_bows.gif'],
    styles=['nebula', 'glitter', 'pastel_hearts'], layouts=['single'], midi=['lovesong', 'heartthrob'], ring='glam',
    keywords='prom 1999 dress photos night under the stars', desc=['Prom 1999 photo album'],
    gb=['You looked SO pretty!', 'Bowling after prom is genius.']))

# ------------------------------------------------------------------ Athenaeum
DARK_POEMS = [
    ('Midnight', 'The clock strikes twelve\nand no one hears\nbut me and the moon\nand a thousand years\n\nI light a '
     'candle\nit flickers and dies\nlike every promise\nlike all your lies'),
    ('Black Rose', 'I gave you a rose\nit was black like my heart\nyou said "how goth"\nthen we drifted apart'),
    ('The Rain Knows', 'The rain knows my name\nit whispers it at night\nagainst the window glass\nwhen nothing feels '
     'right\n\nThe rain knows my name\nbut it never calls it loud\nit just keeps on falling\nfrom a lonely cloud'),
    ('Static Heart', 'My heart is a TV\nat three in the morning\nall static and snow\nand no one is watching'),
    ('Shadow', 'I am the shadow\nat the edge of the hall\nI am the whisper\nthat you don\'t hear at all\n\nDon\'t '
     'look for me\nin the bright light of day\nI only come out\nwhen the stars come to play'),
    ('Ashes', 'We burned the letters\nin a coffee can\nthe smoke went up\nlike it had a plan\n\nnow all that is left\n'
     'is a smudge on my hand\nand a song on the radio\nI can\'t stand'),
    ('Untitled #7', 'nobody understands\nnot my mother\nnot my friends\nnot the guy at the gas station\nnot even me\n'
     '\nbut my cat does\nsometimes'),
]
LOVE_POEMS = [
    ('Screen Name', 'I only know your screen name\nand the way you type "lol"\nbut every night at nine o\'clock\nmy '
     'heart begins to fall'),
    ('Summer', 'You were the summer\nI was the shore\nyou came and you went\nand I wanted more'),
    ('Two Hearts', 'Two hearts, one dream\ntwo spoons, one ice cream\ntwo people on a park bench\nmore than they '
     'seem'),
    ('Forever', 'Forever is a long time\nmy grandma used to say\nbut when I look at you\nit feels like just a day'),
    ('The Letter', 'I wrote you a letter\nI never sent\nit sits in my drawer\nwith my heart, all bent\n\nmaybe '
     'tomorrow\nI will be brave\nor maybe I will keep it\nlike a secret I save'),
    ('Stargazing', 'We counted the stars\nfrom the hood of your car\nwe got to two hundred\nand then lost track of '
     'where we are'),
]
NATURE_POEMS = [
    ('October', 'The maples blush\nthe pumpkins grin\nthe porch light calls\nthe children in'),
    ('Haiku for a Modem', 'shrieking, then a hiss\nconnected at twenty-eight\nmy mother picks up'),
    ('Haiku for Monday', 'alarm clock again\nthe coffee maker gurgles\nthe cat does not care'),
    ('The Old Barn', 'The old barn leans\nlike a tired man\nit has held hay and horses\nsince the century began\n\n'
     'now swallows live\nwhere the cows used to be\nand the wind through the boards\nsings a song just for me'),
    ('First Snow', 'Quiet as a secret\nthe first snow came\nand covered the town\nand everything was the same\n\nbut '
     'whiter'),
]

T2.append(T('darkpoetry', 'Athenaeum', 'Quill', 4, age=(14, 24),
    titles=['~*Shadows Of My Soul*~', 'The Black Candle', 'Raven\'s Requiem', 'Poetry of the Night'],
    intro=['Welcome, wanderer, to my realm of shadows. These poems come from the darkest places of my heart. Read '
           'them by candlelight. Do not steal them, they are copyrighted (by me).',
           'Here lie my poems. Some are sad. Some are very sad. One is about my cat. Enter if you dare.'],
    sections=[
        S('poems', ['Poems', 'Verses From The Dark'], DARK_POEMS, n=(3, 5)),
        S('quote', ['Quote'], ['"Even the darkest night will end and the sun will rise." (I don\'t believe it but '
                               'it is pretty)', '"To sleep, perchance to dream." - some guy',
                               '"The night is darkest before the dawn but also around 3 am."'], n=(1, 1)),
        S('links', ['Other Dark Souls', 'Kindred Spirits'], n=(3, 5)),
    ],
    images=['skull_spin.gif', 'candle.gif'], bullets=['bullet_skull.gif'], lines=['line_barbed.gif',
                                                                                  'line_lightning.gif'],
    styles=['goth', 'border_flames', 'nebula', 'black_neon'], layouts=['single', 'splash', 'frames'],
    midi=['spooky', 'memorial'], ring='poetry', keywords='dark poetry gothic poems night shadows',
    desc=['Dark and gothic poetry', 'Poems from the shadows of my soul'],
    gb=['Your poems speak to my soul.', '"Static Heart" is so true.', '*lights a black candle for you*']))

T2.append(T('lovepoetry', 'Athenaeum', 'Sonnet', 3, age=(15, 60),
    titles=['Words From The Heart', '{first}\'s Love Poems', 'Poetry Garden'],
    intro=['Welcome to my little poetry garden. I write poems about love, life and the little things. I hope one of '
           'them makes you smile.',
           'These poems are for anyone who has ever been in love, out of love, or waiting by the phone.'],
    sections=[
        S('poems', ['Love Poems', 'From The Heart'], LOVE_POEMS, n=(3, 5)),
        S('poems', ['Other Poems'], NATURE_POEMS, n=(1, 2), prob=0.6),
        S('links', ['Poetry Links', 'Other Poets'], n=(3, 5)),
    ],
    images=['heart.gif', 'twinkle.gif'], bullets=['bullet_heart.gif', 'ball_pink.gif'],
    lines=['line_hearts.gif', 'line_bows.gif'], styles=['pastel_hearts', 'parchment', 'marble', 'clouds',
                                                       'pastel_flowers'],
    layouts=['single', 'frames'], midi=['lovesong', 'kitten_waltz'], ring='poetry',
    keywords='love poems poetry romance heart', desc=['Love poems from the heart'],
    gb=['"Screen Name" is SO me.', 'Beautiful poems.', 'You should publish these!']))

T2.append(T('naturepoetry', 'Athenaeum', 'Quill', 2, age=(40, 80),
    titles=['Seasons: Poems by {name}', 'Porch Swing Poetry'],
    intro=['I have been writing poems since I was a girl and my grandson finally convinced me to put them on the '
           'computer. Here they are. Be kind.'],
    sections=[
        S('poems', ['Poems'], NATURE_POEMS, n=(3, 5)),
        S('links', ['Links'], n=(2, 3)),
    ],
    images=[], bullets=['ball_green.gif'], lines=['line_rope.gif', 'rainbow_hr.gif'],
    styles=['parchment', 'retro_tan', 'pastel_flowers'], layouts=['single'], midi=['lullaby', None], ring='poetry',
    keywords='poems seasons nature haiku', desc=['Poems about the seasons'], gb=['Lovely. "The Old Barn" is my favorite.']))

T2.append(T('bookreviews', 'Athenaeum', 'Stacks', 3, age=(20, 70),
    titles=['{first}\'s Bookshelf', 'The Reading Lamp', 'Book Nook Reviews'],
    intro=['I read about 80 books a year (mostly on the bus). Here are my reviews. Ratings are out of five bookmarks.',
           'Welcome to my bookshelf! I review mysteries, science fiction and the occasional romance (do not tell anyone).'],
    sections=[
        S('table', ['Recent Reviews', 'What I\'ve Been Reading'], [
            ('The Wizard School Kid (Book 1)', '5 bookmarks. A boy finds out he is a wizard. My nephew loves it too.'),
            ('Murder at the Bake Sale', '3 bookmarks. Guessed the killer on page 40 (it was the frosting).'),
            ('The Clockwork Moon', '4 bookmarks. Steampunk astronauts. Weird but great.'),
            ('Ten Thousand Acres of Feelings', '2 bookmarks. Daytime-TV book club pick. Very sad. Too long.'),
            ('Galaxion: The Novelization', '3 bookmarks. Same as the movie but with more breathing.'),
            ('The Lighthouse Cookbook Murders', '4 bookmarks. Recipes included! I made the chowder.'),
            ('Cold Harbor Nights', '5 bookmarks. Stayed up until 2 am to finish.'),
            ('A Brief History of Buttons', '4 bookmarks. Surprisingly gripping.')], n=(4, 7)),
        S('top10', ['My All-Time Favorites'], ['Cold Harbor Nights', 'The Clockwork Moon', 'Little House in the '
                                               'Suburbs', 'The Wizard School Kid', 'Pride and Pudding',
                                               'Moby Duck', 'The Old Man and the Lake'], n=(4, 7)),
        S('links', ['Book Links'], n=(2, 4)),
    ],
    images=[], bullets=['ball_blue.gif', 'bullet_star.gif'], lines=['rainbow_hr.gif', 'line_rope.gif'],
    styles=['parchment', 'retro_tan', 'wood', 'plain'], layouts=['single', 'sidebar'], midi=[None, 'ragtime'],
    ring='poetry', keywords='book reviews reading mysteries science fiction', desc=['Book reviews out of five bookmarks'],
    gb=['Have you read "The Clockwork Sun", the sequel?', 'Great reviews!']))

T2.append(T('fanficarchive', 'Athenaeum', 'Inkwell', 3, age=(15, 35),
    titles=['The Inkwell Fan Fiction Archive', '{handle}\'s Fic Corner', 'Stories by {handle}'],
    intro=['Welcome to my fan fiction archive! I write mostly Starhold: Frontier and Murk Files stories, plus the '
           'occasional crossover. Feedback is LOVE. Please e-mail me!',
           'This is where I keep my stories. Disclaimer: I do not own any of these characters, I just play with them.'],
    sections=[
        S('table', ['Stories', 'The Archive'], [
            ('Hold Fast (Starhold, PG)', 'The Meridian finds a ghost ship. 3 parts, complete.'),
            ('After Hours (Murk Files, PG)', 'Holloway and Petrakis, a basement, a shadow.'),
            ('Mags and the Missing Wrench (Starhold, G)', 'A comedy. Somebody took the wrench.'),
            ('Lassoed (Vera the Vampire Wrangler, PG-13)', 'Vera has to wrangle her own prom date.'),
            ('Crossover: The Meridian Files (PG)', 'What if Holloway was beamed aboard the Meridian?'),
            ('The Long Shift (Starhold, G)', 'Mags vs. a humming computer.')], n=(4, 6)),
        S('story', ['Latest Story'], [('Lassoed, Part 1', [
            'Rated PG-13 for vampire peril. Vera the Vampire Wrangler is not mine.',
            'Vera had never been asked to prom before, so she was not sure if the bite marks were a red flag or just '
            'nerves.', '"So," said her date, smiling a little too widely, "do you like... dancing?"',
            'She reached slowly into her purse, past the lip gloss, until her fingers touched the garlic lasso. '
            '"Love it," she said.', 'TO BE CONTINUED']),
            ('The Meridian Files', ['A crossover. Rated PG.',
                                    'Agent Dale Holloway had seen a lot of strange things, but he had never been '
                                    'beamed into a starship mid-sandwich.',
                                    '"Fascinating," said Commander Varek, looking at the sandwich.',
                                    '"I want to see it," said Holloway, "but mostly I want to finish this."'])],
          n=(1, 1)),
        S('links', ['Other Archives'], n=(3, 5)),
    ],
    images=['notepad.gif'], bullets=['bullet_star.gif', 'ball_purple.gif'], lines=['line_stars.gif', 'rainbow_line.gif'],
    styles=['nebula', 'notebook', 'border_purple', 'starfield'], layouts=['sidebar', 'frames', 'single'],
    midi=['starfield', None], ring='scifi', keywords='fan fiction archive stories starhold murk files crossover',
    desc=['Fan fiction archive: Starhold, Murk Files and crossovers'],
    gb=['MORE LASSOED PLEASE', 'The crossover made me laugh out loud.']))

T2.append(T('shortstory', 'Athenaeum', 'Inkwell', 2, age=(20, 60),
    titles=['Short Stories by {name}', 'Tales From The Kitchen Table'],
    intro=['I write short stories in the evenings after work. Some are funny, some are odd. All are short (I have a '
           'short attention span).'],
    sections=[
        S('story', ['Stories'], [
            ('The Vending Machine', [
                'The vending machine on the third floor gave out free soda every Thursday at 4:15, and nobody knew why.',
                'Accounting thought it was a glitch. Facilities thought it was a prank. Gladys in Payroll thought it '
                'was the ghost of Mr. Farnsworth, who had installed the machine in 1971 and died at 4:15 on a '
                'Thursday.', 'Nobody reported it. Some mysteries are better with a free root beer.']),
            ('Lost and Found', [
                'Every lost glove in town ends up at the bus station, in a cardboard box behind the counter.',
                'Earl had worked there thirty years and he had a theory: the gloves were waiting for each other.',
                'Every so often, a left one and a right one that did not match would go missing together. Earl never '
                'told anyone. He just smiled.'])], n=(1, 2)),
        S('links', ['Links'], n=(2, 3)),
    ],
    images=[], bullets=['ball_blue.gif'], lines=['rainbow_hr.gif'], styles=['parchment', 'plain', 'notebook'],
    layouts=['single'], midi=[None], ring='poetry', keywords='short stories fiction writing',
    desc=['Original short stories'], gb=['I loved the vending machine story!']))

# ------------------------------------------------------------------ Arcade
MONSTROPALS = [('Flintfox', 'Fire', 'mp_flintfox.gif', 'Its tail sparks when it is happy. Do not pet it near curtains.'),
               ('Puddlepup', 'Water', 'mp_puddlepup.gif', 'Shakes itself dry on everybody. Very loyal.'),
               ('Sproutle', 'Grass', 'mp_sproutle.gif', 'Grows taller when you sing to it. Scientifically proven (by '
                                                        'me).'),
               ('Voltwhisker', 'Electric', 'mp_voltwhisker.gif', 'The cutest and the most powerful. Everybody wants '
                                                                 'one.'),
               ('Gloomoth', 'Ghost/Bug', 'mp_gloomoth.gif', 'Only comes out at night. Its dust makes you sleepy.'),
               ('Pebblin', 'Rock', 'mp_pebblin.gif', 'Looks like a rock. Is a rock. Is also your friend.')]

T2.append(T('monstropals', 'Arcade', 'Pocket', 7, age=(9, 16), gender='m',
    titles=['MONSTROPALS MANIA!!!', '{handle}\'s Monstropals Page', 'The Ultimate Monstropals Trainer Guide',
            'Monstropals Crimson & Cobalt Cheats', 'BEFRIEND \'EM ALL!!!', 'Voltwhisker Fan Club', 'Trainer {first}\'s '
                                                                                                   'Base'],
    intro=['WELCOME TRAINER!!! This is the best Monstropals page on the whole Internet. I have played Monstropals '
           'Crimson for 140 hours and I have 147 out of 150 pals. Here are all my tips and secrets!',
           'Monstropals is the best game EVER for the PocketBoy. If you don\'t have it you should get it. This page '
           'has a pal guide, cheats and my team!',
           'Befriend \'em all! This is my Monstropals site. I also watch the cartoon every morning before school.'],
    sections=[
        S('mpals', ['Pal Guide', 'Monstropals Index', 'My Favorite Pals'], MONSTROPALS, n=(4, 6)),
        S('table', ['My Team', 'Current Party'], [('Voltwhisker', 'Lv. 54 - my best pal'), ('Flintfox', 'Lv. 50'),
                                                  ('Puddlepup', 'Lv. 47'), ('Gloomoth', 'Lv. 41'), ('Pebblin',
                                                                                                   'Lv. 38 (tank!!)'),
                                                  ('Sproutle', 'Lv. 45'), ('Thornback', 'Lv. 52'),
                                                  ('Mistwing', 'Lv. 49'), ('Rumblebear', 'Lv. 55')], n=(6, 6)),
        S('list', ['Cheats & Secrets', 'Tips'], [
            'To find the secret 151st pal, talk to the old man in Cinder Town 15 times. (Not confirmed. My cousin said.)',
            'Surf up and down the coast near Saltspray Isle to find rare pals.',
            'Save before every gym battle!!!', 'Rumblebear blocks the road until you use the Flute item.',
            'Trade with a friend to evolve Pebblin into Boulderbro.', 'The Golden Net catches ANYTHING. Save it!',
            'Use Water pals against Rock pals. It is super effective!', 'There is a truck near the ship. Some '
            'people say there is a secret pal under it. (I looked. There is not.)'], n=(4, 7)),
        S('table', ['Gym Badges', 'My Badges'], [('Pebble Badge', 'GOT IT'), ('Ripple Badge', 'GOT IT'),
                                                 ('Spark Badge', 'GOT IT'), ('Petal Badge', 'GOT IT'),
                                                 ('Phantom Badge', 'GOT IT'), ('Bog Badge', 'working on it'),
                                                 ('Ember Badge', 'not yet'), ('Summit Badge', 'not yet')],
          n=(5, 8), prob=0.5),
        S('poll', ['Vote: Best Starter Pal'], ['Flintfox', 'Puddlepup', 'Sproutle'], n=(1, 1), prob=0.6),
        S('links', ['Other Trainer Sites', 'Monstropals Links'], n=(3, 6)),
    ],
    subpages=[SUB('cards.html', ['My Card Collection', 'Trading Cards'], [
        S('table', ['My Cards'], [('Holo Voltwhisker', 'MINT!!! Not for trade'), ('Holo Flintfox', 'Trade for holo '
                                                                                                  'Mistwing'),
                                  ('Rumblebear', 'Have 3'), ('Gloomoth 1st edition', 'Got it in a pack at the gas '
                                                                                   'station'),
                                  ('Energy cards', 'like 400')], n=(3, 5)),
        S('para', ['Trading Rules'], ['I only trade by mail with people I know. No ripoffs!!! Holos for holos only.'],
          n=(1, 1))], prob=0.6)],
    images=['mp_voltwhisker.gif', 'mp_flintfox.gif', 'mp_puddlepup.gif', 'mp_trainer.gif'],
    bullets=['ball_red.gif', 'ball_yellow.gif', 'bullet_star.gif'], lines=['rainbow_line.gif', 'line_stars.gif',
                                                                          'line_lightning.gif'],
    styles=['black_neon', 'clouds', 'border_blue', 'checker', 'starfield', 'denim'],
    layouts=['single', 'sidebar', 'frames', 'single'], midi=['chiptune', 'techno'], ring='trainers',
    keywords='monstropals pocketboy cheats pal guide trainer crimson cobalt voltwhisker',
    desc=['Monstropals pal guide, cheats and my team', 'Monstropals trainer page with secrets and badges'],
    gb=['I have 149!!! Beat that!', 'Voltwhisker is the best!!!', 'Want to trade? I have a holo Flintfox.',
        'The old man thing did not work :('], features={'badges': ['mp_trainer.gif']}))

T2.append(T('cheats', 'Arcade', 'Joystick', 3, age=(11, 25), gender='m',
    titles=['{handle}\'s Cheat Codes', 'Game Cheats Central', 'The Code Vault'],
    intro=['Stuck on a level? This page has codes, cheats and secrets for all the best games on the Zenith 64 and the '
           'PlayBox. All codes tested by me (most of them).'],
    sections=[
        S('table', ['Zenith 64 Codes', 'Cheats'], [
            ('Turbo Turtle 64', 'At the title screen press UP, UP, Z, Z, START for all shells.'),
            ('Legend of Zephyr: Clockwork Flute', 'Play the song backwards at the lake to find the hidden harp.'),
            ('Dino Kart 64', 'Hold L while selecting a track for mirror mode.'),
            ('Double-O-Nothing: Agent of Paperwork', 'Beat the dam level in under 2:40 for paintball mode.'),
            ('Wrestle Ruckus 99', 'Enter "BIGHEAD" as a name for big heads mode.'),
            ('Ultimate Fantasia VII', 'Breed a gold riding-bird by feeding it 40 carrots.'),
            ('Pro Skater Dude 99', 'Pause and press L, R, R, L for a secret skater (a ghost).'),
            ('Wombat Warp 3', 'Spin the 7th crate 3 times for an extra life.')], n=(5, 8)),
        S('list', ['General Tips'], ['Read the manual (I know, I know)', 'Save often!', 'Rent before you buy',
                                     'Blow in the cartridge if it does not work (does that actually help?)',
                                     'Never trust your little brother with your memory card'], n=(3, 5)),
        S('links', ['Gaming Links'], n=(3, 5)),
    ],
    images=['hot.gif', 'cool_face.gif'], bullets=['ball_green.gif', 'ball_red.gif'], lines=['line_laser.gif',
                                                                                            'rainbow_line.gif'],
    styles=['black_neon', 'hacker', 'checker', 'border_blue'], layouts=['single', 'sidebar'],
    midi=['chiptune', 'techno'], ring='gamers', keywords='cheat codes video games zenith 64 playbox secrets',
    desc=['Video game cheat codes and secrets'], gb=['The Turbo Turtle code worked!!!', 'Blowing in the cartridge '
                                                                                         'DOES help.']))

T2.append(T('clan', 'Arcade', 'Fragzone', 3, age=(14, 28), gender='m',
    titles=['[{tag}] Clan Homepage', 'Clan {clan}', '{clan} - Fragmatic Arena Clan'],
    entities=[dict(clan='Lag Assassins', tag='LAG'), dict(clan='Rocket Jump Society', tag='RJS'),
              dict(clan='The Campers', tag='TENT')],
    intro=['Welcome to the official homepage of <B>[{tag}] {clan}</B>, a Fragmatic Arena clan founded in 1997. We play '
           'CTF and deathmatch on the Frag Barn server every Friday night. Recruiting skilled players with low ping!',
           '[{tag}] {clan} rules the Frag Barn server. Respect the clan. Check out our roster and match results.'],
    sections=[
        S('table', ['Roster', 'Members'], [('[{tag}]Razor', 'Leader. Railgun god.'), ('[{tag}]Mongoose', 'Rocket '
                                                                                                        'jumper'),
                                           ('[{tag}]Gibbs', 'Shotgun. Gets gibbed a lot.'), ('[{tag}]Kitten', 'Will '
                                                                                                             'frag '
                                                                                                             'you. '
                                                                                                             'Sweetly.'),
                                           ('[{tag}]PingOfDeath', 'Plays on a 28.8. Somehow wins.'),
                                           ('[{tag}]{handle}', 'webmaster, medic, mostly dies')], n=(4, 6)),
        S('table', ['Match Results'], [('vs [SNIP] Snipers Inc', 'WON 15-9'), ('vs [OWN] Ownage', 'LOST 7-15 (lag)'),
                                       ('vs [N00B] Beginners Club', 'WON 15-0'), ('vs [CAMP] The Other Campers',
                                                                                  'TIED (power outage)')], n=(3, 4)),
        S('list', ['Clan Rules'], ['No cheating. Ever.', 'Be at matches on time.', 'Respect other clans.',
                                   'No camping (unless you are in TENT)', 'Have fun, frag hard.'], n=(3, 5)),
        S('links', ['Clan Links', 'Allied Clans'], n=(2, 4)),
    ],
    images=['skull_spin.gif', 'fire.gif'], bullets=['bullet_skull.gif'], lines=['line_barbed.gif', 'flames.gif',
                                                                                'line_laser.gif'],
    styles=['border_flames', 'hacker', 'black_neon', 'concrete', 'camo'], layouts=['frames', 'sidebar', 'single'],
    midi=['techno', 'punk'], ring='gamers', keywords='clan fragmatic arena deathmatch ctf lan {clan}',
    desc=['[{tag}] {clan}: Fragmatic Arena clan'], gb=['GG last night [{tag}]', 'Can I join? My ping is 80.']))

T2.append(T('rpg', 'Arcade', 'Dungeon', 3, age=(14, 40),
    titles=['The Dragon\'s Lair (Our Tabletop Campaign)', 'Ultimate Fantasia VII Walkthrough', '{first}\'s RPG Corner'],
    intro=['Roll for initiative! This page is for our Saturday night tabletop game, the Kingdom of Varn campaign. '
           'Here are the character sheets, the story so far and the house rules.',
           'Welcome, adventurer. This page has my complete walkthrough for Ultimate Fantasia VII, the best role-playing '
           'game ever made (4 discs!!!).'],
    sections=[
        S('table', ['The Party', 'Characters'], [('Thorgrim', 'Dwarf fighter, lvl 7, played by Kevin'),
                                                 ('Elowen', 'Elf ranger, lvl 7, played by Sarah'),
                                                 ('Brother Pell', 'Human cleric, lvl 6, played by Mike'),
                                                 ('Zazz the Magnificent', 'Gnome wizard, lvl 7, played by me'),
                                                 ('Sneaky Pete', 'Halfling rogue, lvl 7, played by Pete (obviously)')],
          n=(3, 5)),
        S('log', ['The Story So Far', 'Session Log'], [
            'The party met in a tavern. Of course.', 'Thorgrim fought a goblin and lost. To one goblin.',
            'Found the map to the Sunken Temple. Sneaky Pete tried to sell it. Twice.',
            'Zazz accidentally fireballed the bridge we were standing on.', 'Defeated the Lich King! Sort of. He '
            'will be back.', 'Rolled three natural 20s in a row. Kevin\'s mom came downstairs to see why we were '
                             'screaming.'], n=(3, 5)),
        S('list', ['House Rules'], ['Pizza money is due BEFORE the game.', 'The DM is always right.', 'No rules '
                                    'lawyering after 11 pm.', 'If you roll a 1, you have to do a funny voice.'],
          n=(3, 4)),
        S('links', ['RPG Links'], n=(2, 4)),
    ],
    images=['skull_spin.gif', 'fire.gif'], bullets=['bullet_star.gif', 'bullet_skull.gif'],
    lines=['line_rope.gif', 'flames.gif'], styles=['parchment', 'goth', 'wood', 'nebula'], layouts=['single',
                                                                                                   'sidebar'],
    midi=['spooky', 'anthem'], ring='gamers', keywords='rpg role playing dungeon campaign dice walkthrough',
    desc=['Tabletop RPG campaign page'], gb=['Zazz should not be allowed fireball.', 'Nat 20s!!!']))

# ------------------------------------------------------------------ fix up near-real names
for _t in T2:
    pass
