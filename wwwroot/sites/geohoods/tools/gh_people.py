"""gh_people.py -- invented homesteaders, towns, e-mail providers and guestbook visitors.

All names are invented / generic; any resemblance to real people is coincidental.
"""
import random

FIRST_F = ['Jennifer', 'Amber', 'Brittany', 'Kayla', 'Heather', 'Crystal', 'Tiffany', 'Melissa', 'Stacy', 'Dawn',
           'Kimberly', 'Becky', 'Tammy', 'Lori', 'Denise', 'Shelly', 'Nicole', 'Ashley', 'Mandy', 'Kristen',
           'Courtney', 'Jessica', 'Megan', 'Carrie', 'Wendy', 'Darlene', 'Gloria', 'Marjorie', 'Edna', 'Bev',
           'Lynn', 'Rhonda', 'Holly', 'Erin', 'Trish', 'Misty', 'April', 'Sabrina', 'Jolene', 'Paula', 'Vicki',
           'Dorothy', 'Hazel', 'Natalie', 'Sierra', 'Cassie', 'Robin', 'Joanne', 'Leigh', 'Tara']
FIRST_M = ['Jason', 'Kevin', 'Brian', 'Chad', 'Travis', 'Josh', 'Ryan', 'Derek', 'Kyle', 'Shawn', 'Dustin', 'Brandon',
           'Greg', 'Doug', 'Gary', 'Larry', 'Randy', 'Earl', 'Dale', 'Wayne', 'Terry', 'Rick', 'Steve', 'Mike',
           'Todd', 'Cody', 'Jeremy', 'Corey', 'Matt', 'Nate', 'Jimmy', 'Ron', 'Walt', 'Herb', 'Lyle', 'Marvin',
           'Floyd', 'Vern', 'Zach', 'Trent', 'Lance', 'Wade', 'Clint', 'Rusty', 'Kirk', 'Darren', 'Phil', 'Neil',
           'Stu', 'Gus']
LAST = ['Miller', 'Kowalski', 'Henderson', 'Pruitt', 'Dobbs', 'Larsen', 'Whitaker', 'Ogden', 'Fenwick', 'Haskell',
        'McCready', 'Thibodeaux', 'Brandt', 'Vasquez', 'Nakamura', 'Okafor', 'Delgado', 'Pettibone', 'Sorensen',
        'Grubb', 'Abernathy', 'Kline', 'Mayhew', 'Pickett', 'Ruiz', 'Schaefer', 'Tolliver', 'Underwood', 'Voss',
        'Wexler', 'Yoder', 'Zimmer', 'Barlow', 'Castellano', 'Dupree', 'Eckert', 'Fong', 'Gallagher', 'Huang',
        'Ingram', 'Jablonski', 'Keener', 'Lindqvist', 'Moreau', 'Novak', 'Oyelaran', 'Pham', 'Quimby', 'Rasmussen',
        'Stroud', 'Tran', 'Ulrich', 'Van Pelt', 'Winslow', 'Hatfield', 'Bergstrom', 'Calloway', 'Duchesne']

OLD_F = ['Gloria', 'Marjorie', 'Edna', 'Bev', 'Darlene', 'Dorothy', 'Hazel', 'Joanne', 'Paula', 'Vicki', 'Rhonda',
         'Denise', 'Lori', 'Tammy', 'Lynn', 'Wendy']
OLD_M = ['Larry', 'Earl', 'Dale', 'Wayne', 'Herb', 'Lyle', 'Marvin', 'Floyd', 'Vern', 'Walt', 'Ron', 'Gary', 'Rick',
         'Phil', 'Gus', 'Stu', 'Terry', 'Doug']

TOWNS = [('Toledo', 'OH'), ('Boise', 'ID'), ('Fresno', 'CA'), ('Tulsa', 'OK'), ('Duluth', 'MN'), ('Peoria', 'IL'),
         ('Mobile', 'AL'), ('Spokane', 'WA'), ('Topeka', 'KS'), ('Bangor', 'ME'), ('Lubbock', 'TX'),
         ('Scranton', 'PA'), ('Muncie', 'IN'), ('Billings', 'MT'), ('Macon', 'GA'), ('Fargo', 'ND'),
         ('Ames', 'IA'), ('Reno', 'NV'), ('Tucson', 'AZ'), ('Eugene', 'OR'), ('Biloxi', 'MS'), ('Dayton', 'OH'),
         ('Akron', 'OH'), ('Flint', 'MI'), ('Kalamazoo', 'MI'), ('Green Bay', 'WI'), ('Sioux Falls', 'SD'),
         ('Little Rock', 'AR'), ('Shreveport', 'LA'), ('Knoxville', 'TN'), ('Roanoke', 'VA'), ('Wilmington', 'NC'),
         ('Burlington', 'VT'), ('Erie', 'PA'), ('Albany', 'NY'), ('Pueblo', 'CO'), ('Provo', 'UT'),
         ('Cheyenne', 'WY'), ('Amarillo', 'TX'), ('Lansing', 'MI'), ('Omaha', 'NE'), ('Wichita', 'KS'),
         ('Halifax', 'Nova Scotia'), ('Winnipeg', 'Manitoba'), ('Hamilton', 'Ontario'), ('Leeds', 'England'),
         ('Brisbane', 'Australia'), ('Dunedin', 'New Zealand'), ('Cork', 'Ireland'), ('Saskatoon', 'Saskatchewan')]

MAILHOSTS = ['geohoods.com', 'americaoffline.com', 'compuverse.com', 'prodigal.net', 'earthlynk.net',
             'mindsurf.net', 'dialtone.net', 'snailmail.net', 'cybermall.net', 'modemland.com']

HANDLE_PARTS_A = ['Star', 'Cyber', 'Dark', 'Angel', 'Kitty', 'Moon', 'Sk8r', 'Dragon', 'Shadow', 'Pixie', 'Tiger',
                  'Neon', 'Purple', 'Mystic', 'Silver', 'Thunder', 'Rocket', 'Lil', 'Big', 'Crazy', 'Funky',
                  'Groovy', 'Wild', 'Sweet', 'Sunny', 'Bubble', 'Raven', 'Wolf', 'Ghost', 'Turbo', 'Mega', 'Hyper']
HANDLE_PARTS_B = ['Grrl', 'Dude', 'Babe', 'Rider', 'Dancer', 'Child', 'Master', 'Freak', 'Monkey', 'Princess', 'Man',
                  'Kat', 'Wizard', 'Chick', 'Boy', 'Fox', 'Pup', 'Queen', 'King', 'Surfer', 'Walker', 'Hunter',
                  'Storm', 'Blade', 'Heart', 'Flower', 'Wing', 'Fire', 'Pilot', 'Hacker']


class Persona(object):
    pass


def make_persona(rr, gender=None, age_range=(13, 70), handle_style=None):
    p = Persona()
    p.gender = gender or rr.choice('fm')
    p.age = rr.randint(*age_range)
    pool = FIRST_F if p.gender == 'f' else FIRST_M
    old = OLD_F if p.gender == 'f' else OLD_M
    if p.age < 30:
        pool = [n for n in pool if n not in old]
    elif p.age > 50:
        pool = old
    p.first = rr.choice(pool)
    p.last = rr.choice(LAST)
    p.name = '%s %s' % (p.first, p.last)
    p.town, p.state = rr.choice(TOWNS)
    p.where = '%s, %s' % (p.town, p.state)
    style = handle_style or rr.choice(['combo', 'combo', 'name', 'xx', 'initials'])
    yr = rr.choice(['', str(rr.randint(1, 99)), str(rr.randint(75, 87)), '2000', '69', '77', '13'])
    if style == 'combo':
        p.handle = rr.choice(HANDLE_PARTS_A) + rr.choice(HANDLE_PARTS_B) + yr
    elif style == 'xx':
        p.handle = 'xX' + rr.choice(HANDLE_PARTS_A) + rr.choice(HANDLE_PARTS_B) + 'Xx'
    elif style == 'initials':
        p.handle = (p.first[0] + p.last).lower() + yr
    else:
        p.handle = p.first + rr.choice(['_', '', '.']) + p.last[:1] + yr
    p.email = '%s@%s' % (p.handle.lower().replace(' ', ''), rr.choice(MAILHOSTS))
    return p


GB_NAMES = ['Kristy', 'DJ Sparkle', 'Bob from Ohio', 'Nate', 'Tammy L.', 'xXAngelEyesXx', 'The Webmaster of '
            'CoolStuff', 'Grandma Jo', 'Dwayne', 'Ms. Patterson', 'SpaceCadet', 'Cheryl & Don', 'kewl_kid99',
            'Rolf (Germany)', 'Lindsay', 'Pete the Programmer', 'Mike T.', 'Becca', 'A fellow homesteader',
            'Anonymous', 'HappyHamster', 'Darla', 'Sir Surfs-a-Lot', 'Marco', 'Jen', 'Uncle Lou', 'Kelsey',
            'Trucker Tom', 'Sunflower', 'The Cat Lady of Topeka', 'Skippy', 'Vince', 'Agnes', 'Brock', 'Ellie',
            'MoonUnit', 'Coach Hal', 'Professor Plum', 'Gus', 'Wanda', 'NightOwl', 'Ricky', 'Shawna', 'Bert',
            'Ramona', 'Lefty', 'Cupcake22', 'Ted in Tacoma', 'Brenda', 'Old Salt']
GB_FOUND = ['Surfing around', 'Webring', 'Search engine', 'A friend told me', 'Your e-mail signature',
            'The neighborhood directory', 'Cool Page of the Day', 'Just lucky!', 'Link from another page']
GB_GENERIC = [
    'Cool page!!! Keep up the good work. Please visit my page too!',
    'I love your page!!! The background is so pretty. How did you make the words move?',
    'Great site. I added you to my bookmarks. Come sign MY guestbook sometime!',
    'Wow, you put a lot of work into this. My page is still under construction, ha ha.',
    'Your page took a while to load on my 28.8 but it was worth it!',
    'Hi from across the pond! Found you through the webring. Cheers!',
    'Nice graphics! Can I borrow the spinning thingy? I will link back to you, promise.',
    'This is the best page in the whole neighborhood. No lie.',
    'Just dropping by to say hi. Your music is stuck in my head now. Thanks a lot :-)',
    'I can\'t believe I found someone else who likes this stuff! E-mail me!',
    'Neat-o. Add more pictures please!',
    'I am a fellow homesteader and I gave your page 5 out of 5 stars on my links page.',
    'How do you get a counter like that? Mine just says 0 all the time.',
    'Sorry, I hit the submit button twice. Great page though!',
    'Your page crashed my browser the first time but the second time it was great.',
    'My mom says I spend too much time on the Internet. Then she saw your page and said OK fine.',
    'Greetings from the library computer! I only have 15 minutes so I will be quick: AWESOME.',
    'Please update soon! I check every day.',
    'Very professional looking. Are you a web designer?',
    'I found a typo in your third paragraph but otherwise perfect! :)',
    'Hello from a fellow night owl. It is 3am and I should be asleep.',
    'Signing your guestbook like you asked. Now sign mine! Deal?',
    'LOL. I laughed so hard at your page my cat left the room.',
    'Two thumbs up. Three if I had three thumbs.',
    'Bookmarked! Also, the link to the page with the pictures is broken I think?',
]


def gb_entries(rr, n, theme_lines=None, start_year=1998):
    out = []
    lines = list(GB_GENERIC) + list(theme_lines or []) * 2
    for i in range(n):
        y = rr.choice([start_year, 1998, 1999, 1999, 1999])
        m = rr.randint(1, 12 if y < 1999 else 10)
        d = rr.randint(1, 28)
        hh, mm = rr.randint(0, 23), rr.randint(0, 59)
        nm = rr.choice(GB_NAMES)
        out.append(dict(name=nm, date=(y, m, d), time='%d:%02d %s' % ((hh % 12) or 12, mm, 'AM' if hh < 12 else 'PM'),
                        where=rr.choice(TOWNS), found=rr.choice(GB_FOUND), text=rr.choice(lines),
                        email=rr.random() < 0.6 and ('%s@%s' % (nm.lower().replace(' ', '').replace('.', '')
                                                                .replace('(', '').replace(')', '')
                                                                .replace('&', 'and')[:14], rr.choice(MAILHOSTS)))
                        or ''))
    out.sort(key=lambda e: e['date'], reverse=True)
    return out


MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
          'November', 'December']


def fmt_date(t, style=0):
    y, m, d = t
    if style == 0:
        return '%s %d, %d' % (MONTHS[m - 1], d, y)
    if style == 1:
        return '%d/%d/%02d' % (m, d, y % 100)
    if style == 2:
        return '%d %s %d' % (d, MONTHS[m - 1][:3], y)
    return '%02d.%02d.%d' % (m, d, y)


def rand_date(rr, y0=1997, y1=1999):
    y = rr.randint(y0, y1)
    m = rr.randint(1, 12 if y < 1999 else 10)
    return (y, m, rr.randint(1, 28))
