#!/usr/bin/env python3
"""mkhomepages.py -- generate the whole static GeoHoods site.

  * plans ~250 member homepages from the themes in gh_themes1-3.py (invented personas, seeded, reproducible)
  * renders each one (plus sub-pages, a guestbook and frames/splash variants) with gh_render.py
  * builds the portal, neighborhood + suburb directories, webrings, search index etc. with gh_portal.py

Run mkgfx.py and mkmidi.py first (they draw ../images/*.gif and compose ../midi/*.mid).

Usage:  python3 tools/mkhomepages.py
"""
import os
import random
import shutil
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SITE = os.path.abspath(os.path.join(HERE, '..'))

from gh_hoods import HOODS, HOOD  # noqa: E402
from gh_people import make_persona, gb_entries, fmt_date, rand_date  # noqa: E402
from gh_render import STYLES, GENERATORS, MIDI_TITLES, sub, render_member  # noqa: E402
from gh_imgsizes import SIZES  # noqa: E402
import gh_themes1  # noqa: E402
import gh_themes2  # noqa: E402
import gh_themes3  # noqa: E402
import mkmidi  # noqa: E402

THEMES = gh_themes1.T1 + gh_themes2.T2 + gh_themes3.T3
for _n, _t, _kw in mkmidi.TUNES:
    MIDI_TITLES[_n] = _t

RINGS = {
    'truth': ('The UFO Truth Ring', '#99FF99', 'Sightings, abductions and the things They do not want you to know.'),
    'murk': ('Look Closer: The Murk Files Ring', '#CCCCFF', 'Fan pages for the best show on Friday night.'),
    'scifi': ('Final Frontier Fan Ring', '#99CCFF', 'Starhold, Galaxion and fan fiction from across the galaxy.'),
    'geek': ('Geek Pride Ring', '#CCFFCC', 'Rigs, code, BBS memories. Beep boop.'),
    'newbie': ('Brand New Homesteaders Ring', '#FFFFCC', 'First pages, first steps, first counters.'),
    'webdesign': ('Webmasters\' Guild Ring', '#FFCC99', 'HTML help, free graphics and webmaster tips.'),
    'couch': ('Couch Potato Ring', '#FFCCCC', 'TV and movie fan pages.'),
    'brock': ('Heartthrob Ring', '#FFCCFF', 'Shrines to the cutest stars on the big screen.'),
    'sports': ('Sports Fanatics Ring', '#CCFFCC', 'Teams, leagues, fishing holes and bowling alleys.'),
    'boyband': ('Boy Band Babes Ring', '#FFCCFF', 'For fans of the cutest bands in the universe!!!'),
    'indie': ('Garage & Jukebox Ring', '#CCCCCC', 'Bands, MIDIs and music of every kind.'),
    'family': ('Family Pages Ring', '#FFFFCC', 'Family home pages, babies, reunions and roots.'),
    'kitty': ('Kitty Lovers Ring', '#FFCCE6', 'Purr-fect pages about cats and kittens.'),
    'dogs': ('Dog Days Ring', '#FFE6CC', 'Woof! Pages about our best friends.'),
    'critters': ('Small Critters Ring', '#FFFFCC', 'Hamsters, ferrets, bunnies, fish and horses.'),
    'rainbow': ('Rainbow Fields Memorial Ring', '#E6E6FF', 'Remembering the pets who wait for us.'),
    'glam': ('Glitter & Glam Ring', '#FFCCFF', 'Fashion, beauty and prom night.'),
    'poetry': ('Poetry Corner Ring', '#F5F0DC', 'Poems, stories and book reviews.'),
    'trainers': ('Monstropals Trainers Ring', '#FFFF99', 'Befriend \'em all!'),
    'gamers': ('Insert Coin Gamers Ring', '#CCFFFF', 'Cheats, clans and campaigns.'),
    'teens': ('Teen Scene Ring', '#FFCCFF', 'About-me pages, dorm cams and the Class of 2000.'),
    'y2k': ('Y2K Preparedness Ring', '#FFFF99', 'Prepared, not scared.'),
    'travel': ('Road Trip Ring', '#CCFFFF', 'Vacations, RVs, coasters and cruises.'),
    'recipes': ('Recipe Box Ring', '#FFE6CC', 'Grandma\'s recipes, barbecue and sweets.'),
    'gearheads': ('Gearheads Ring', '#DDDDDD', 'Cars, engines and model trains.'),
    'crafty': ('Crafty Collectors Ring', '#FFE6F2', 'Quilts, stamps and Plushie Pals.'),
}

EXT = {  # links out to the rest of the 1999 Web
    'default': [('yowza', 'Yowza! - find anything on the Web'), ('altavisor', 'AltaVisor search'),
                ('hamstershuffle', 'The Hamster Shuffle (LOL!!!)'), ('cnm', 'CNM Interactive news')],
    'geek': [('dashdot', 'Dashdot - news for nerds'), ('snapster', 'Snapster'), ('altavisor', 'AltaVisor')],
    'teen': [('hamstershuffle', 'THE HAMSTER SHUFFLE!!!'), ('snapster', 'Snapster'), ('yowza', 'Yowza!'),
             ('askreeves', 'Ask Reeves')],
    'family': [('orinoco', 'Orinoco.com (books!)'), ('etoyz', 'eToyz'), ('petz', 'Petz.com'), ('cnm', 'CNM news'),
               ('askreeves', 'Ask Reeves')],
    'pets': [('petz', 'Petz.com - pet supplies'), ('hamstershuffle', 'Hamster Shuffle'), ('yowza', 'Yowza!')],
    'shop': [('ubid', 'uBid auctions'), ('orinoco', 'Orinoco.com'), ('etoyz', 'eToyz')],
}
RING_EXT = {'geek': 'geek', 'webdesign': 'geek', 'gamers': 'geek', 'trainers': 'teen', 'teens': 'teen',
            'boyband': 'teen', 'brock': 'teen', 'glam': 'teen', 'family': 'family', 'recipes': 'family',
            'travel': 'family', 'kitty': 'pets', 'dogs': 'pets', 'critters': 'pets', 'rainbow': 'pets',
            'crafty': 'shop', 'gearheads': 'shop', 'sports': 'default', 'y2k': 'default'}

BADGES = ['best_800.gif', 'notepad.gif', 'y2k_ok.gif', 'pioneer_now.gif', 'explorer.gif', 'handcoded.gif',
          'noframes.gif', 'webring_88.gif', 'html32.gif', 'anti_spam.gif', 'stop_ie.gif', 'geohoods_88.gif']
AWARDS = ['award_coolweek.gif', 'award_hammer.gif', 'award_top4.gif', 'award_gold.gif']
AWARD_BY_RING = {'truth': 'award_spooky.gif', 'murk': 'award_spooky.gif', 'scifi': 'award_galactic.gif',
                 'kitty': 'award_purrfect.gif', 'dogs': 'award_purrfect.gif', 'critters': 'award_purrfect.gif',
                 'family': 'award_blue.gif', 'recipes': 'award_blue.gif', 'poetry': 'award_gold.gif'}
SMALL_ANIMS = ['heart.gif', 'twinkle.gif', 'ufo.gif', 'alien.gif', 'kitten.gif', 'puppy.gif', 'skull_spin.gif',
               'notes.gif', 'cd_spin.gif', 'football.gif', 'hamster.gif', 'globe.gif', 'gear.gif', 'chili.gif',
               'pie.gif', 'candle.gif', 'tower.gif', 'cool_face.gif', 'hot.gif', 'y2k_bomb.gif', 'snowman.gif',
               'dancing_baby.gif', 'mp_voltwhisker.gif', 'mp_flintfox.gif', 'mp_puddlepup.gif', 'pumpkin.gif',
               'train.gif', 'new.gif', 'updated.gif']


def expand_entity(ent):
    v = {}
    for k, val in ent.items():
        if isinstance(val, list):
            single = {'members': 'member', 'songs': 'song', 'chars': 'c'}.get(k, k[:-1])
            for i, x in enumerate(val):
                v['%s%d' % (single, i + 1)] = x
            v['n' + k] = len(val)
            for i in range(len(val), 8):
                v['%s%d' % (single, i + 1)] = val[i % len(val)]
        else:
            v[k] = val
    return v


def plan():
    rr = random.Random(19991023)
    taken = {}
    pages = []
    for t in THEMES:
        h = HOOD[t['hood']]
        assert t['suburb'] in [s for s, _d in h['suburbs']], (t['key'], t['suburb'])
        titles = list(t['titles'])
        rr.shuffle(titles)
        ents = list(t['entities'])
        rr.shuffle(ents)
        for i in range(t['count']):
            key = (t['hood'], t['suburb'])
            used = taken.setdefault(key, set())
            while True:
                num = rr.choice([rr.randint(1000, 1999), rr.randint(1000, 4999), rr.randint(1000, 9999)])
                if num not in used:
                    used.add(num)
                    break
            addr = '%s/%s/%d/' % (t['hood'], t['suburb'], num)
            prr = random.Random(addr)
            per = make_persona(prr, gender=t['gender'], age_range=t['age'], handle_style=t['handle'])
            v = dict(first=per.first, last=per.last, name=per.name, handle=per.handle, age=per.age, town=per.town,
                     state=per.state, where=per.where, email=per.email, n1=prr.randint(12, 140),
                     date1=fmt_date(rand_date(prr, 1996, 1998)))
            if ents:
                v.update(expand_entity(ents[i % len(ents)]))
            p = dict(theme=t['key'], hood=t['hood'], suburb=t['suburb'], num=num, addr=addr, rr=prr, vars=v,
                     tdef=t, v_handle=per.handle, v_email=per.email, v_first=per.first, v_town=per.town,
                     owner=per.name, age=per.age, where=per.where)
            p['title'] = sub(titles[i % len(titles)], v)
            pages.append(p)
    return pages


def decorate(p):
    """choose the look and the 1999 furniture for one page"""
    t = p['tdef']
    rr = p['rr']
    v = p['vars']
    feats = t['features']
    calm = feats.get('calm')
    nofancy = feats.get('nofancy')
    first = feats.get('firstpage')
    p['style'] = rr.choice(t['styles'])
    p['layout'] = rr.choice(t['layouts'])
    p['hmode'] = rr.choice(['plain', 'bullet', 'underline', 'stars', 'caps', 'plain', 'bullet'])
    p['bullet'] = rr.choice(t['bullets']) if t.get('bullets') and rr.random() < 0.8 else None
    p['listmode'] = rr.choice(['img', 'img', 'ul'])
    p['line'] = rr.choice(t['lines']) if t.get('lines') and rr.random() < 0.85 else None
    if first or nofancy:
        p['hmode'], p['bullet'], p['line'] = 'plain', None, None
    t_head = p['title']
    p['headline'] = rr.choice([t_head, t_head, 'Welcome to %s!' % t_head, '~*~ %s ~*~' % t_head, t_head.upper()]) \
        if not nofancy else t_head
    p['intro'] = sub(rr.choice(t['intro']), v) if t['intro'] else ''
    p['desc'] = sub(rr.choice(t['desc']), v)
    p['keywords'] = sub(t['keywords'], v)
    p['ring'] = t['ring']
    p['inring'] = bool(t['ring']) and rr.random() < 0.8
    p['ext'] = EXT[RING_EXT.get(t['ring'], 'default')]
    p['generator'] = rr.choice(GENERATORS)
    imgs = t['images']
    photos = [i for i in imgs if i.startswith('photo_') or SIZES.get(i, (0, 0))[0] > 100]
    smalls = [i for i in imgs if i in SMALL_ANIMS or SIZES.get(i, (999, 0))[0] <= 80]
    p['photo_top'] = rr.choice(photos) if photos and rr.random() < 0.45 else None
    p['titleimg'] = rr.choice(smalls) if smalls and rr.random() < 0.45 and not nofancy else None
    p['photo_menu'] = rr.choice(smalls) if smalls and rr.random() < 0.5 and SIZES.get(
        rr.choice(smalls), (99, 99))[0] <= 64 else None
    if p['photo_menu'] and SIZES[p['photo_menu']][0] > 64:
        p['photo_menu'] = None
    # music & counters
    p['midi'] = rr.choice(t['midi']) if not nofancy else None
    p['midimode'] = rr.choice(['bgsound', 'embed', 'console', 'sniff', 'embed'])
    p['counter'] = None if feats.get('nocounter') else rr.choice(['digit', 'led', 'odo', 'js', 'digit', None])
    p['hits'] = int(rr.choice([rr.randint(12, 400), rr.randint(300, 5000), rr.randint(1000, 40000),
                               rr.randint(40, 2000)]))
    p['since'] = fmt_date(rand_date(rr, 1996, 1998), 1)
    p['updated'] = fmt_date(rand_date(rr, 1998, 1999), rr.randint(0, 2))
    p['guestbook'] = rr.random() < (0.75 if not first else 0.3)
    p['gbentries'] = gb_entries(rr, rr.randint(2, 15), [sub(x, v) for x in t['gb']]) if p['guestbook'] else []
    p['email'] = rr.random() < 0.85
    p['mailimg'] = rr.choice(['mailme.gif', 'mail_fly.gif', 'email.gif', 'mailbox.gif', None])
    # badges and awards
    pool = [b for b in BADGES if not (b == 'noframes.gif' and p['layout'] == 'frames')]
    p['badges'] = rr.sample(pool, rr.randint(1, 4)) if rr.random() < 0.55 and not first else []
    p['badges'] += feats.get('badges', [])
    if nofancy:
        p['badges'] = ['gnulix.gif', 'handcoded.gif']
    p['awards'] = []
    if rr.random() < 0.35 and not first and not nofancy:
        aw = list(AWARDS) + ([AWARD_BY_RING[t['ring']]] * 2 if t['ring'] in AWARD_BY_RING else [])
        p['awards'] = list(dict.fromkeys(rr.sample(aw, rr.randint(1, 3))))
    p['awards'] = list(dict.fromkeys(p['awards'] + (feats.get('awards', []) if rr.random() < 0.5 else [])))
    # the loud stuff
    loud = not (calm or nofancy)
    p['marquee'] = loud and rr.random() < 0.45
    p['blink'] = loud and rr.random() < 0.28
    p['welcomegif'] = loud and rr.random() < 0.18
    p['construction'] = feats.get('construction') or (loud and rr.random() < 0.22)
    p['bestviewed'] = rr.random() < 0.4 and not nofancy
    p['applet'] = loud and rr.random() < 0.07
    p['broken'] = loud and rr.random() < 0.09
    p['scroller'] = loud and rr.random() < 0.12
    p['norightclick'] = loud and rr.random() < 0.035
    p['sniff'] = loud and rr.random() < 0.08
    p['clock'] = loud and rr.random() < 0.08
    p['navbuttons'] = rr.random() < 0.4
    if first:
        p['style'] = rr.choice(['default_gray', 'plain', 'default_gray'])
        p['layout'] = 'single'
    # sections & subpages
    secs = list(t['sections'])
    linksec = [s for s in secs if s['kind'] == 'links']
    rest = [s for s in secs if s['kind'] != 'links']
    if len(rest) > 2 and rr.random() < 0.5:
        a, b = rr.sample(range(len(rest)), 2)
        rest[a], rest[b] = rest[b], rest[a]
    p['sections'] = rest + linksec
    p['haslinks'] = bool(linksec)
    p['subpages'] = []
    for sp in t['subpages']:
        if rr.random() < sp['prob']:
            p['subpages'].append(dict(fname=sp['fname'], title=sub(rr.choice(sp['titles']), v),
                                      sections=sp['sections']))


def neighbors(pages):
    by = {}
    for p in pages:
        by.setdefault((p['hood'], p['suburb']), []).append(p)
    for lst in by.values():
        lst.sort(key=lambda q: q['num'])
        for i, p in enumerate(lst):
            p['prevn'] = lst[i - 1]['addr']
            p['nextn'] = lst[(i + 1) % len(lst)]['addr']


def build_rings(pages):
    rings = {}
    for code, (name, color, blurb) in RINGS.items():
        mem = [p for p in pages if p['ring'] == code and p['inring']]
        random.Random(code).shuffle(mem)
        if len(mem) < 2:
            for p in mem:
                p['inring'] = False
            continue
        rings[code] = dict(code=code, name=name, color=color, blurb=blurb, members=mem)
    return rings


def main():
    pages = plan()
    for p in pages:
        decorate(p)
    neighbors(pages)
    rings = build_rings(pages)
    # wipe previously generated neighborhood folders
    for h in HOODS:
        d = os.path.join(SITE, h['key'])
        if os.path.isdir(d):
            shutil.rmtree(d)
    nfiles = 0
    for p in pages:
        d = os.path.join(SITE, p['addr'])
        os.makedirs(d, exist_ok=True)
        files = render_member(p, pages, rings)
        p['files'] = sorted(files)
        for fn, html in files.items():
            with open(os.path.join(d, fn), 'w', encoding='latin-1', errors='xmlcharrefreplace') as f:
                f.write(html)
            nfiles += 1
    import gh_portal
    nportal = gh_portal.build(SITE, pages, rings)
    print('%d homepages (%d files) + %d portal/directory files' % (len(pages), nfiles, nportal))
    counts = {}
    for p in pages:
        counts[p['hood']] = counts.get(p['hood'], 0) + 1
    for h in HOODS:
        print('  %-14s %3d' % (h['key'], counts.get(h['key'], 0)))


if __name__ == '__main__':
    main()
