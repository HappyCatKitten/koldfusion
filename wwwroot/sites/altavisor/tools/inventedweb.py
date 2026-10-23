# -*- coding: utf-8 -*-
"""The invented "rest of the Web" that AltaVisor crawls besides the twelve 1999-Web sites.

Every invented site listed in the Yowza! directory gets a small 1999-style homepage under
altavisor/web/<host>/ (written by gen_altavisor.py), so Yowza! listings and AltaVisor results
always land on a real page. EXTRA_PAGES adds sites Yowza! never listed, including a few
in other languages for the language selector.
"""

# sentences mixed into each homepage, by top-level Yowza! category ({name}, {topic} are filled in)
BANKS = {
    'Arts_and_Humanities': [
        'Here at {name} we believe that everybody is an artist, even people who only draw stick figures.',
        'This page is dedicated to {topic} and to everyone who has ever been told to get a real job.',
        'We add new pieces to the gallery every week, so bookmark us and come back often.',
        'All works shown here are copyright their creators. Please ask before you borrow anything.',
        'Our monthly contest is open to anyone with a scanner or a very steady hand with the mouse.',
        'The best way to look at the gallery is with your monitor set to thousands of colors.',
    ],
    'Business_and_Economy': [
        '{name} is a leading provider of {topic} solutions for the new economy.',
        'Call our toll-free number or fill out the order form; we accept all major credit cards and personal checks.',
        'Our customers say we have the friendliest service on the whole information superhighway.',
        'Ask about our special Internet-only prices, available for a limited time.',
        'We are proud to be one of the first companies in our industry with a World Wide Web site.',
        'Please allow four to six weeks for delivery. Y2K compliance statement available on request.',
    ],
    'Computers_and_Internet': [
        'This site covers {topic} for beginners and experts alike, with plenty of screenshots.',
        'Make sure you have the latest drivers before you write to us about crashes.',
        'All software on this page is freeware unless marked otherwise. Download at your own risk.',
        'This page looks best in Netscape Navigator 4 or Internet Explorer 4 at 800 by 600 pixels.',
        'If the page loads slowly, blame your modem, not us. We tested it at 28.8.',
        'Questions? Read the FAQ first. Then read it again. Then email the webmaster.',
    ],
    'Education': [
        '{name} helps students, parents and teachers with {topic}.',
        'Teachers are welcome to print these pages for classroom use.',
        'Every activity was tested by real kids in a real classroom, and most of them survived.',
        'Parents: please supervise children while they are online.',
        'New lessons are added at the start of each semester.',
    ],
    'Entertainment': [
        'Welcome to the coolest {topic} page on the whole Internet!',
        'You can download sounds, pictures and wallpaper from the links below.',
        'This is an unofficial fan page and is not endorsed by anybody important.',
        'Vote in our poll and see what other fans think.',
        'Check out the links section for more great sites, and do not forget to sign the guestbook.',
        'Warning: the next page has a MIDI file that starts playing automatically.',
    ],
    'Government': [
        '{name} provides information about {topic} to the public.',
        'Forms may be printed and mailed to the address shown on each form.',
        'Office hours are Monday through Friday, 9 to 5, except holidays.',
        'This site is maintained as a public service. No endorsement of any product is implied.',
        'Please consult a professional for advice about your own situation.',
    ],
    'Health': [
        '{name} offers plain-English information about {topic}.',
        'This page is for information only and is not a substitute for advice from your doctor.',
        'Drink plenty of water, get some sleep, and step away from the computer once in a while.',
        'Our articles are reviewed by a panel of health professionals and one very fit cat.',
        'Have a question? Our nurses answer email within two business days.',
    ],
    'News_and_Media': [
        '{name} brings you the latest in {topic}, updated around the clock.',
        'Subscribe to our free email newsletter and never miss a headline.',
        'Our reporters are standing by, mostly next to the coffee machine.',
        'Stories in the archive are available for 30 days.',
        'Got a tip? Send it to our newsroom and we might feature it tomorrow.',
    ],
    'Recreation_and_Sports': [
        '{name} is your online headquarters for {topic}.',
        'Get outside and enjoy it! But first, read the tips on this page.',
        'Our message board has hundreds of members who love {topic} as much as you do.',
        'Photos sent in by readers are posted every Monday.',
        'Safety first: always wear a helmet, even while browsing.',
        'Upcoming events and meetups are listed on the calendar page.',
    ],
    'Reference': [
        '{name} is a free reference for anyone who needs to look something up about {topic}.',
        'Our database is updated weekly by a team of very careful volunteers.',
        'If you find a mistake, please let us know and we will fix it.',
        'Bookmark this page, you will be back.',
        'Searches are free. They will always be free. Probably.',
    ],
    'Regional': [
        '{name} is the place to start for everything about {topic}.',
        'Find restaurants, attractions, the weather and the best places to park.',
        'Visitors are always welcome. Bring a jacket, just in case.',
        'Locals: tell us your favorite spots and we will add them to the guide.',
        'Our photo gallery shows the area in every season.',
    ],
    'Science': [
        '{name} explores {topic} for curious people of all ages.',
        'All of our facts are checked by real scientists, who wear real lab coats.',
        'Try the experiments at home, with permission from a grown-up.',
        'Our image gallery has pictures you can use in school reports.',
        'Science is about asking questions. Email us yours.',
    ],
    'Social_Science': [
        '{name} is a resource for students and fans of {topic}.',
        'Our reading list has been compiled by professors and enthusiasts.',
        'Discussion is welcome on the message board, as long as it stays civil.',
        'Statistics on this page were last updated this spring.',
        'Cite this page in your bibliography, your teacher will be impressed.',
    ],
    'Society_and_Culture': [
        'Welcome to {name}, a friendly corner of the Web about {topic}.',
        'Everyone is welcome here. Please be kind on the message board.',
        'This page is a labor of love maintained in my spare time.',
        'If you liked this page, please tell your friends and sign my guestbook.',
        'Links to similar pages are at the bottom of this page.',
    ],
}

# hosts Yowza! never listed. lang: en fr de es it nl pt xp (Pig Latin)
EXTRA_PAGES = [
    ('www.bunkerdiary.com', 'My Y2K Bunker Diary', 'en', 'Day 112 in the basement bunker. I have 400 cans of beans, a hand crank radio, and a generator that I am afraid to start. The cat is unimpressed. My wife says the year 2000 problem will be fixed by programmers. I say the programmers are in their own bunkers. Updates daily until the power goes out.'),
    ('www.furryautopsy.com', 'The Furry Talker Autopsy', 'en', 'We opened up the chattering owl hamster toy to find out how it learns words. Answer: it does not learn anything. It has a little speaker, a motor, a light sensor and a chip that unlocks phrases over time. Pictures of every step. No toys were harmed. Well, one toy was harmed.'),
    ('www.vrmlvillage.com', 'VRML Village 3D', 'en', 'Walk around our virtual reality village in three dimensions! You will need a VRML plugin and a very patient computer. Visit the 3D town hall, the 3D fountain, and the 3D gift shop where nothing is for sale. Best viewed on a computer with 32 megabytes of RAM.'),
    ('www.icqnumbers.org', 'Low ICQ Number Collectors', 'en', 'The lower your instant messenger number, the longer you have been online. Members of this club have numbers under one million. We trade stories about the old days of 1996. Proof of number required to join. No, you cannot have mine.'),
    ('www.blinktag.org', 'Save the Blink Tag', 'en', 'Some people say the blink tag is annoying. We say it is expressive. Sign our petition to keep blinking text in every browser forever. This page uses 14 blink tags, a marquee and a scrolling status bar message as a show of support.'),
    ('www.hamsterwheelsociety.org', 'Hamster Wheel Society', 'en', 'The international society for the study of hamster wheels. Silent wheels, squeaky wheels, wheels that power a light bulb. Our research shows the average hamster runs five miles a night. Our hamster ran zero miles and then danced. We blame the Internet.'),
    ('www.ufodatabase.net', 'The UFO Sighting Database', 'en', 'Over 12,000 reports of unidentified flying objects, sorted by state and by shape: disc, cigar, triangle and shiny thing. Submit your sighting with our online form. Most sightings turn out to be weather balloons, Venus, or a neighbor with a kite.'),
    ('www.tamagotchigraveyard.com', 'Virtual Pet Memorial Garden', 'en', 'A place to remember the keychain pets who did not make it through the school year. Write a message for your pet, light a virtual candle and read stories from other grieving owners. Rest in pixels.'),
    ('www.webcamcoffee.com', 'The Office Coffee Pot Cam', 'en', 'A live picture of our office coffee pot, updated every 30 seconds, so nobody walks down the hall for an empty pot ever again. Current status: probably empty. Thank you to the 2 million visitors who have watched our coffee.'),
    ('www.homemadecomputer.net', 'I Built a Computer From Scratch', 'en', 'This page tells how I built my own computer with a soldering iron, a kit, and three summers. It has 4K of memory and blinks lights in a pattern. It cannot run a web browser, so I am writing this on my other computer.'),
    ('www.lavalampfacts.com', 'Lava Lamp Facts and Fiction', 'en', 'How do lava lamps work? Heat, wax and a secret liquid. This page explains it all, and why you should never shake one. Includes a gallery of 200 lamps in every color, and a Java applet of a lava lamp for people who cannot afford one.'),
    ('www.recipesforchaos.com', 'Recipes for Disaster', 'en', 'Recipes that went horribly wrong, submitted by readers. The microwave egg. The pancake that would not end. The Thanksgiving turkey that was still frozen at dinnertime. Laugh, learn, and keep a fire extinguisher in the kitchen.'),
    ('www.webmasterconfessions.com', 'Webmaster Confessions', 'en', 'Anonymous confessions from the people who build web pages. I copied my whole layout from another site. I still use the font tag. My hit counter starts at 10,000 to look popular. Submit your own confession with the form below.'),
    ('www.flatearthforums.net', 'The Round Table Forum', 'en', 'A debate forum for people who argue about everything: pie versus cake, tabs versus spaces, Netscape versus Explorer. Our longest thread is 14,000 posts about whether a hot dog is a sandwich. All opinions welcome, all of them wrong.'),
    ('www.pagesperso-mireille.fr', 'La page perso de Mireille', 'fr', 'Bienvenue sur ma page personnelle! Je m appelle Mireille et j habite a Lyon. Ici vous trouverez mes photos de vacances, mes recettes de cuisine preferees et des liens vers mes sites favoris. N oubliez pas de signer mon livre d or. Page en construction, revenez bientot!'),
    ('www.croissantclub.fr', 'Le Club du Croissant', 'fr', 'Le club des amateurs de croissants au beurre. Chaque semaine nous visitons une boulangerie differente et nous donnons une note sur dix. Les meilleures adresses de Paris, de Lyon et de Marseille. Le croissant parfait existe, nous le cherchons encore.'),
    ('www.heimseite-klaus.de', 'Klaus seine Heimseite', 'de', 'Herzlich willkommen auf meiner Homepage! Ich heisse Klaus und wohne in Hamburg. Hier finden Sie Bilder von meiner Modelleisenbahn, meinem Hund und meinem Auto. Diese Seite ist noch im Aufbau. Bitte tragen Sie sich in mein Gaestebuch ein. Vielen Dank fuer Ihren Besuch!'),
    ('www.wurstfreunde.de', 'Die Wurstfreunde', 'de', 'Der Verein fuer Freunde der deutschen Wurst. Wir stellen jede Woche eine neue Wurst vor, mit Rezept und Bildern. Bratwurst, Weisswurst, Currywurst und viele mehr. Mitglied werden ist kostenlos. Senf bringen Sie bitte selbst mit.'),
    ('www.paginadelucia.es', 'La pagina de Lucia', 'es', 'Hola y bienvenidos a mi pagina! Me llamo Lucia y vivo en Sevilla. Aqui tengo fotos de mi familia, mis canciones favoritas y enlaces a otras paginas muy interesantes. La pagina esta en construccion. Por favor firma mi libro de visitas. Gracias por visitar!'),
    ('www.futbolfanaticos.es', 'Futbol Fanaticos', 'es', 'Todo sobre el futbol: resultados, noticias, fotos y un foro para discutir con otros aficionados. Cada lunes publicamos el resumen de la jornada. Vota por el mejor gol de la semana en nuestra encuesta.'),
    ('www.lapaginadimarco.it', 'La pagina di Marco', 'it', 'Benvenuti nella mia pagina personale! Mi chiamo Marco e abito a Bologna. Qui trovate le mie ricette di pasta, le foto della mia Vespa e tanti link utili. Il sito e ancora in costruzione. Firmate il mio libro degli ospiti, grazie!'),
    ('www.thuispagina-joost.nl', 'De thuispagina van Joost', 'nl', 'Welkom op mijn homepage! Ik ben Joost en ik woon in Utrecht. Hier vind je foto s van mijn fiets, mijn kat en mijn verzameling klompen. Deze pagina is nog in aanbouw. Teken alsjeblieft mijn gastenboek. Bedankt voor je bezoek!'),
    ('www.paginadojoao.com.br', 'A pagina do Joao', 'pt', 'Bem-vindo a minha pagina pessoal! Meu nome e Joao e moro no Rio de Janeiro. Aqui voce encontra fotos da praia, minhas musicas favoritas e links legais. A pagina esta em construcao. Assine meu livro de visitas, obrigado!'),
    ('www.igpay-atinlay.com', 'Igpay Atinlay Omepagehay', 'xp', 'Elcomeway otay ymay omepagehay! Isthay agepay isway ittenwray entirelyway inway igpay atinlay. Ignsay ymay uestbookgay andway eecay ymay atcay icturespay. Isthay agepay isway underway onstructioncay. Ankthay ouyay orfay isitingvay!'),
]

LANG_NAMES = {'en': 'English', 'fr': 'French', 'de': 'German', 'es': 'Spanish', 'it': 'Italian', 'nl': 'Dutch',
              'pt': 'Portuguese', 'xp': 'Pig Latin'}

GUESTBOOK = [
    ('Kimberly', 'Cool page!!! Check out mine too!'),
    ('surfer_dude_77', 'found u on Yowza. awesome site. pls add me to ur links'),
    ('Webmaster Bob', 'Nice layout. What program did you use?'),
    ('Grandma', 'Hello dear, I do not know if this is where I type. Love, Grandma'),
    ('anonymous', 'first post!'),
    ('Tina from Ohio', 'I have been looking for a page like this for months. Bookmarked!'),
    ('xXDarkAngelXx', 'nice. very nice. -DA'),
    ('Marcus', 'The MIDI made me jump out of my chair. Five stars.'),
    ('Jen', 'Your page loads so fast on my 33.6! Thanks for not using frames.'),
    ('Pete', 'Hi from Australia!!! G day!'),
    ('mom', 'Honey, call me when you get this. Love Mom'),
    ('NetSurfer2000', 'Ready for Y2K? I am. Cool site btw.'),
]
