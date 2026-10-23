"""gh_portal.py -- the GeoHoods portal: home page, neighborhood + suburb directories, members directory,
JS search, JS page builder and File Manager, Cool Page of the Day, add-ons, webring hubs, help pages.

All URLs are relative. A page at depth d (number of folders below the site root) uses root = "../" * d.
"""
import os
import random

from gh_hoods import HOODS, HOOD
from gh_imgsizes import SIZES
from gh_render import MIDI_TITLES, STYLES
from gh_people import FIRST_F, FIRST_M

RING1999 = ['yowza', 'altavisor', 'askreeves', 'orinoco', 'ubid', 'etoyz', 'petz', 'geohoods', 'hamstershuffle',
            'dashdot', 'snapster', 'cnm']
FONT = '<FONT FACE="Arial, Helvetica" SIZE=2>'
NAVY = '#003399'
YEL = '#FFFFCC'


def W(site, rel, html):
    path = os.path.join(site, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='latin-1', errors='xmlcharrefreplace') as f:
        f.write(html)
    W.count += 1


W.count = 0


def jstr(s):
    return '"%s"' % str(s).replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('</', '<\\/')


def img(root, name, alt='', extra=''):
    w, h = SIZES[name]
    return '<IMG SRC="%simages/%s" WIDTH=%d HEIGHT=%d BORDER=0 ALT="%s"%s>' % (root, name, w, h, alt, extra)


def ring_bar(root):
    i = RING1999.index('geohoods')
    prev, nxt = RING1999[i - 1], RING1999[(i + 1) % len(RING1999)]
    arr = ','.join('"%s"' % s for s in RING1999)
    return ('<P><CENTER><TABLE BORDER=2 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#C0C0C0"><TR><TD ALIGN=CENTER>'
            '<FONT FACE="Arial, Helvetica" SIZE=1 COLOR="#000000">\n'
            '<A HREF="%s../%s/index.html">&lt;&lt; Prev</A> |\n'
            '<A HREF="%s../yowza/index.html" onClick="var s=new Array(%s); location.href=\'%s../\'+'
            's[Math.floor(Math.random()*s.length)]+\'/index.html\'; return false;">Random</A> |\n'
            '<B><A HREF="%s../../web1999/index.html">The 1999 Web Ring</A></B> |\n'
            '<A HREF="%s../%s/index.html">Next &gt;&gt;</A>\n'
            '</FONT></TD></TR></TABLE></CENTER></P>\n' % (root, prev, root, arr, root, root, root, nxt))


def head(title, extra=''):
    return ('<HTML>\n<HEAD>\n<TITLE>%s</TITLE>\n<META NAME="GENERATOR" CONTENT="GeoHoods Portal Server 3.1">\n%s'
            '</HEAD>\n' % (title, extra))


def top(root, title, extra_head='', onload=''):
    h = head(title, extra_head)
    h += '<BODY BGCOLOR="#FFFFFF" TEXT="#000000" LINK="#0000CC" VLINK="#551A8B"%s>\n<CENTER>\n' % (
        (' onLoad="%s"' % onload) if onload else '')
    h += ('<TABLE WIDTH=600 BORDER=0 CELLSPACING=0 CELLPADDING=0><TR>\n<TD VALIGN=MIDDLE>'
          '<A HREF="%sindex.html">%s</A></TD>\n'
          '<TD ALIGN=RIGHT VALIGN=BOTTOM NOWRAP><FONT FACE="Arial, Helvetica" SIZE=2>'
          '<A HREF="%sneighborhoods.html">Neighborhoods</A> - <A HREF="%ssearch.html">Search</A> - '
          '<A HREF="%shelp.html">Help</A></FONT></TD></TR></TABLE>\n'
          '<HR SIZE=1 WIDTH=600 NOSHADE>\n'
          '<TABLE BGCOLOR="#EEEEEE" WIDTH=600 CELLPADDING=3 CELLSPACING=0 BORDER=0><TR>'
          '<TD><FONT FACE="Arial, Helvetica" SIZE=2>&nbsp;<B>Welcome, Homesteader!</B> - '
          '<A HREF="%sfilemanager.html">[Member Login]</A></FONT></TD>'
          '<TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2><A HREF="%sjoin.html">Get a free home page</A></FONT> '
          '<A HREF="%sjoin.html">%s</A></TD></TR></TABLE>\n' % (
              root, img(root, 'gh_logo.gif', 'GeoHoods'), root, root, root, root, root, root,
              img(root, 'arrow.gif', '', ' HSPACE=4')))
    return h


def bottom(root):
    return ('<P></P><HR SIZE=1 WIDTH=600 NOSHADE>\n'
            '<FONT FACE="Arial, Helvetica" SIZE=1>Copyright &copy; 1994-1999 GeoHoods Inc. All rights reserved.<BR>\n'
            '<A HREF="%shelp.html">Help</A> - <A HREF="%sguidelines.html">Terms of Service</A> - '
            '<A HREF="%sguidelines.html#content">Content Guidelines</A> - <A HREF="%snews.html">Press &amp; News</A> - '
            '<A HREF="%saddons/index.html">Add-Ons</A></FONT>\n'
            '%s<P>%s</P>\n</CENTER>\n</BODY>\n</HTML>\n' % (
                root, root, root, root, root, ring_bar(root), img(root, 'powered_by_kf.gif', 'Powered by KoldFusion')))


def bluehead(text, color=NAVY):
    return ('<TR><TD BGCOLOR="%s"><FONT FACE="Arial, Helvetica" COLOR="#FFFFFF"><B>%s</B></FONT></TD></TR>\n'
            % (color, text))


def panel(title, body, color=NAVY, bg=YEL, width='100%'):
    return ('<TABLE WIDTH="%s" CELLPADDING=4 CELLSPACING=0 BORDER=0>\n%s<TR><TD BGCOLOR="%s">%s%s</FONT></TD></TR>'
            '</TABLE>\n' % (width, bluehead(title, color), bg, FONT, body))


def ad_banner(root):
    ads = ['ad_mosquito.gif', 'ad_surfslim.gif', 'ad_y2k.gif', 'ad_pioneer.gif', 'ad_virtuapup.gif']
    arr = ','.join('"%simages/%s"' % (root, a) for a in ads)
    return ('<P><A HREF="%sadclick.html"><IMG NAME="adbanner" SRC="%simages/%s" WIDTH=468 HEIGHT=60 BORDER=0 '
            'ALT="Advertisement"></A><BR><FONT FACE="Arial" SIZE=1>Advertisement</FONT>\n'
            '<SCRIPT LANGUAGE="JavaScript">\n<!--\nvar ads = new Array(%s);\n'
            'document.images["adbanner"].src = ads[Math.floor(Math.random() * ads.length)];\n// -->\n</SCRIPT></P>\n'
            % (root, root, ads[0], arr))


def prow(p, root, extra=''):
    return '<A HREF="%s%sindex.html">%s</A>%s' % (root, p['addr'], p['title'], extra)


# ====================================================================== home page
def home(site, pages, rings, cool, featured):
    root = ''
    h = top(root, 'GeoHoods - Free Home Pages in Neighborhoods Across the Web')
    h += ('<TABLE WIDTH=600 CELLPADDING=0 CELLSPACING=0 BORDER=0><TR>\n'
          '<TD BGCOLOR="%s"><A HREF="build.html">%s</A></TD><TD WIDTH=2></TD>\n'
          '<TD BGCOLOR="%s"><A HREF="filemanager.html">%s</A></TD><TD WIDTH=2></TD>\n'
          '<TD BGCOLOR="%s"><A HREF="join.html">%s</A></TD></TR></TABLE>\n' % (
              NAVY, img(root, 'btn_build.gif', 'Build a Page'), NAVY, img(root, 'btn_edit.gif', 'Edit Pages'), NAVY,
              img(root, 'btn_join.gif', 'Move In')))
    h += ('<TABLE WIDTH=600 CELLPADDING=4 CELLSPACING=0 BORDER=0><TR><TD BGCOLOR="#FFFFCC" ALIGN=CENTER>'
          '<FONT FACE="Arial, Helvetica" SIZE=2><B>%d homesteaders</B> have already moved into our <B>%d neighborhoods'
          '</B>. <A HREF="join.html">Grab your free address</A> before the good ones are gone!</FONT></TD></TR>'
          '</TABLE>\n' % (len(pages), len(HOODS)))
    h += ad_banner(root)
    # two columns
    h += '<TABLE WIDTH=600 CELLPADDING=0 CELLSPACING=0 BORDER=0><TR VALIGN=TOP>\n<TD WIDTH=399 BGCOLOR="#FFFFCC">\n'
    h += panel('Search Home Pages',
               '<FORM ACTION="search.html" METHOD="GET" NAME="srch"><CENTER><INPUT TYPE="text" NAME="q" SIZE=25> '
               '<INPUT TYPE="submit" VALUE="Search"><BR><FONT SIZE=1>Try: <A HREF="search.html?q=ufo">ufo</A>, '
               '<A HREF="search.html?q=kitty">kitty</A>, <A HREF="search.html?q=y2k">y2k</A>, '
               '<A HREF="search.html?q=recipes">recipes</A>, <A HREF="search.html?q=northbound">northbound</A>'
               '</FONT></CENTER></FORM>')
    cols = [HOODS[0:5], HOODS[5:10], HOODS[10:15]]
    hb = '<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%"><TR VALIGN=TOP>\n'
    for c in cols:
        hb += '<TD WIDTH="33%">' + FONT
        for hd in c:
            hb += '<A HREF="%s/index.html">%s</A> <A HREF="%s/index.html">%s</A><BR>\n' % (
                hd['key'], img(root, 'hood_%s.gif' % hd['key'].lower(), '', ' ALIGN=ABSMIDDLE WIDTH=16 HEIGHT=16'
                               ).replace('WIDTH=32 HEIGHT=32 ', ''), hd['key'], hd['title'])
        hb += '</FONT></TD>\n'
    hb += ('</TR><TR><TD COLSPAN=3 ALIGN=CENTER>%sTake a vacation in <A HREF="Driftwood/index.html">Driftwood</A>, '
           'one of our %d <A HREF="neighborhoods.html">Neighborhoods</A>.<BR>Mingle with homesteaders in our '
           'Neighborhood <A HREF="chat.html">chats</A>!</FONT></TD></TR></TABLE>\n' % (FONT, len(HOODS)))
    h += '<TABLE WIDTH="100%" CELLPADDING=4 CELLSPACING=0 BORDER=0>' + bluehead('Explore Neighborhoods') + \
         '<TR><TD BGCOLOR="#FFFFCC">' + hb + '</TD></TR></TABLE>\n'
    ad = ('<TABLE WIDTH="100%%" CELLPADDING=5 CELLSPACING=0 BORDER=0><TR VALIGN=TOP>'
          '<TD WIDTH="50%%">%s<A HREF="addons/clipart.html"><B>Animation &amp; Clip Art</B></A><BR>'
          '<FONT SIZE=1>Flames, skulls, envelopes...</FONT></FONT></TD>'
          '<TD>%s<A HREF="addons/counters.html"><B>Counters</B></A><BR><FONT SIZE=1>Odometer, LED, '
          'classic...</FONT></FONT></TD></TR>\n<TR VALIGN=TOP><TD>%s<A HREF="addons/backgrounds.html"><B>Backgrounds'
          '</B></A><BR><FONT SIZE=1>Stars, hearts, camo...</FONT></FONT></TD>'
          '<TD>%s<A HREF="addons/guestbooks.html"><B>Guestbooks</B></A><BR><FONT SIZE=1>Let visitors sign in!'
          '</FONT></FONT></TD></TR>\n<TR VALIGN=TOP><TD>%s<A HREF="addons/midi.html"><B>MIDI Music</B></A><BR>'
          '<FONT SIZE=1>%d original tunes</FONT></FONT></TD><TD>%s<A HREF="addons/webrings.html"><B>Webrings</B></A>'
          '<BR><FONT SIZE=1>%d rings to join</FONT></FONT></TD></TR></TABLE>\n' % (
              FONT, FONT, FONT, FONT, FONT, len(MIDI_TITLES), FONT, len(rings)))
    h += '<TABLE WIDTH="100%" CELLPADDING=4 CELLSPACING=0 BORDER=0>' + bluehead('Cool Home Page Add-Ons') + \
         '<TR><TD BGCOLOR="#FFFFCC">' + ad + '</TD></TR></TABLE>\n'
    h += panel('Five Great Reasons to Get a Free Home Page',
               '<UL><LI><B>11 MB of free space</B> - room for hundreds of GIFs!\n'
               '<LI><B>Build-a-Page</B> - make a page in minutes, no HTML needed.\n'
               '<LI><B>Free add-ons</B> - counters, guestbooks, clip art and MIDI music.\n'
               '<LI><B>Neighborhoods</B> - meet people who like what you like, in %d themed communities.\n'
               '<LI><B>Your own address</B> - like <TT>geohoods.com/Area52/Hangar/1013/</TT>. Tell your friends!</UL>'
               % len(HOODS))
    h += '</TD>\n<TD WIDTH=2><IMG SRC="images/spacer.gif" WIDTH=2 HEIGHT=1></TD>\n<TD WIDTH=199>\n'
    # right column
    h += ('<TABLE WIDTH="100%" CELLPADDING=1 CELLSPACING=0 BORDER=0><TR><TD BGCOLOR="#00CC00">'
          '<TABLE WIDTH="100%" CELLPADDING=4 CELLSPACING=0 BORDER=0><TR><TD BGCOLOR="#00CC00">'
          '<FONT FACE="Arial, Helvetica" COLOR="#FFFFFF"><B>Member Login</B></FONT></TD></TR>'
          '<TR><TD BGCOLOR="#EEFFEE"><FORM NAME="login" ACTION="filemanager.html" METHOD="GET" '
          'onSubmit="location.href=\'filemanager.html?member=\' + escape(document.forms[\'login\'].member.value); '
          'return false;"><FONT FACE="Arial" SIZE=1>Member name:<BR><INPUT TYPE="text" NAME="member" SIZE=14><BR>'
          'Password:<BR><INPUT TYPE="password" NAME="pw" SIZE=14><BR><INPUT TYPE="submit" VALUE="Login"><BR>'
          '<A HREF="help.html#password">Forgot your password?</A></FONT></FORM></TD></TR></TABLE></TD></TR>'
          '</TABLE><BR>\n')
    # cool page of the day (JS picks by day)
    arr = ','.join('new Array(%s,%s,%s,%s)' % (jstr(c['addr']), jstr(c['title']), jstr(c['v_handle']),
                                                jstr(c['blurb'])) for c in cool)
    c0 = cool[0]
    h += ('<TABLE WIDTH="100%%" CELLPADDING=4 CELLSPACING=0 BORDER=1 BORDERCOLOR="#FF6600"><TR><TD BGCOLOR="#FFF0E0">'
          '%s<BR><CENTER>%s</CENTER>%s\n<SCRIPT LANGUAGE="JavaScript">\n<!--\nvar cool = new Array(%s);\n'
          'var now = new Date();\nvar doy = Math.floor((now.getTime() - new Date(now.getFullYear(), 0, 1).getTime()) / '
          '86400000);\nvar c = cool[doy %% cool.length];\n'
          'document.write("<B><A HREF=\\"" + c[0] + "index.html\\">" + c[1] + "</A></B><BR>by " + c[2] + "<P>" + c[3] + '
          '"</P>");\n// -->\n</SCRIPT>\n<NOSCRIPT><B>%s</B><BR>by %s<P>%s</P></NOSCRIPT>'
          '<A HREF="cool.html">Past Cool Pages</A></FONT></TD></TR></TABLE><BR>\n' % (
              img(root, 'hdr_cool.gif', 'Cool Page of the Day').replace('WIDTH=200', 'WIDTH=180'),
              img(root, 'cool_face.gif', ''), '<FONT FACE="Arial" SIZE=2>', arr, prow(c0, root), c0['v_handle'],
              c0['blurb']))
    fb = ''
    for p in featured[:4]:
        fb += '<P>%s<BR><FONT SIZE=1>%s<BR>%s/%s</FONT></P>\n' % (prow(p, root), p['desc'], p['hood'], p['suburb'])
    h += ('<TABLE WIDTH="100%%" CELLPADDING=4 CELLSPACING=0 BORDER=0><TR><TD BGCOLOR="#990099"><FONT FACE="Arial" '
          'COLOR="#FFFFFF" SIZE=2><B>Featured Homesteaders</B></FONT></TD></TR><TR><TD BGCOLOR="#FFEEFF">'
          '<FONT FACE="Arial" SIZE=2>%s</FONT></TD></TR></TABLE><BR>\n' % fb)
    h += ('<TABLE WIDTH="100%%" CELLPADDING=4 CELLSPACING=0 BORDER=0><TR><TD BGCOLOR="%s"><FONT FACE="Arial" '
          'COLOR="#FFFFFF" SIZE=2><B>New and Notable</B></FONT></TD></TR><TR><TD BGCOLOR="#EEEEEE">'
          '<FONT FACE="Arial" SIZE=2><P><B>More space!</B><BR>Every homesteader now gets 11 MB. We can\'t wait to see '
          'how many GIFs you fit in it.</P><P><B>Bunker opens</B><BR>Our 15th neighborhood is now accepting '
          'homesteaders. Bring canned goods. <A HREF="Bunker/index.html">Visit</A></P>'
          '<P><B>Y2K ready</B><BR>We rolled our clocks to 2000 in the lab. Everything worked except the coffee maker. '
          '<A HREF="news.html">Read more</A></P></FONT></TD></TR></TABLE>\n' % NAVY)
    h += '</TD></TR></TABLE>\n'
    h += ('<P>%s<B>Getting Help</B><BR>New to GeoHoods? Visit our <A HREF="help.html">Help</A> section for '
          'answers and tutorials, or browse the <A HREF="directory/index.html">Members Directory</A>.</FONT></P>\n'
          % FONT)
    h += bottom(root)
    W(site, 'index.html', h)


# ====================================================================== neighborhoods
def neighborhoods(site, pages):
    root = ''
    h = top(root, 'GeoHoods Neighborhoods')
    h += '<P><FONT FACE="Arial" SIZE=5><B>Neighborhood Directory</B></FONT><BR>%sEvery GeoHoods homesteader ' \
         'lives in a neighborhood. Pick the one that fits you best - it\'s like moving to a town where everybody ' \
         'likes the same things you do.</FONT></P>\n' % FONT
    h += '<TABLE WIDTH=600 BORDER=0 CELLPADDING=5 CELLSPACING=0>\n'
    for i, hd in enumerate(HOODS):
        n = len([p for p in pages if p['hood'] == hd['key']])
        subs = ', '.join('<A HREF="%s/%s/index.html">%s</A>' % (hd['key'], s, s) for s, _d in hd['suburbs'])
        h += ('<TR VALIGN=TOP BGCOLOR="%s"><TD><A HREF="%s/index.html">%s</A></TD><TD>%s<B><A HREF="%s/index.html">%s'
              '</A></B> - <I>%s</I><BR>%s<BR><FONT SIZE=1>Suburbs: %s | %d homesteaders</FONT></FONT></TD></TR>\n' % (
                  '#FFFFCC' if i % 2 == 0 else '#FFFFFF', hd['key'], img(root, 'hood_%s.gif' % hd['key'].lower()),
                  FONT, hd['key'], hd['title'], hd['tagline'], hd['blurb'], subs, n))
    h += '</TABLE>\n'
    h += bottom(root)
    W(site, 'neighborhoods.html', h)


NEWS_TEMPLATES = [
    'Neighborhood chat every Thursday at 9 pm Eastern in the {hood} room. This week\'s topic: "{topic}"',
    'Welcome to our newest homesteaders in {suburb}! Stop by and sign their guestbooks.',
    'The {hood} Homestead Awards are back! Nominate your favorite page by e-mailing your Community Leader.',
    'Reminder: please keep your pages within the content guidelines. Our Community Leaders are watching (nicely).',
    'Spotlight contest: best {topic2} page in {hood} wins a Golden Shovel award and eternal glory.',
    'Vacant lots available in {suburb}! Claim one today.',
]
TOPICS = {'SiliconHills': ('Is 56K worth it?', 'rig'), 'Tinseltown': ('Best movie of 1999', 'fan'),
          'Gridiron': ('Who wins the big game?', 'team'), 'Area52': ('What was that light over Nevada?', 'sighting'),
          'Bayou': ('Best boy band, final answer', 'band'), 'Hearth': ('Holiday traditions', 'family'),
          'Prairie': ('Cats vs. dogs (be nice)', 'pet'), 'Boulevard': ('Platform shoes: yes or no', 'style'),
          'Athenaeum': ('Rhyme or free verse?', 'poetry'), 'Arcade': ('Secret 151st pal: real or fake?', 'game'),
          'Campus': ('Class of 2000 prom themes', 'about-me'), 'Bunker': ('Generators: gas or diesel?', 'checklist'),
          'Driftwood': ('Worst motel ever', 'vacation'), 'Skillet': ('Gelatin salads: art or crime?', 'recipe'),
          'Workbench': ('Retired Plushie Pals prices', 'collection')}


def hood_page(site, hd, pages, leaders, featured):
    root = '../'
    key = hd['key']
    hp = [p for p in pages if p['hood'] == key]
    rr = random.Random(key)
    dark, light = hd['color']
    h = top(root, 'GeoHoods: %s - %s' % (key, hd['tagline']))
    h += '<P>%s</P>\n' % img(root, 'banner_%s.gif' % key.lower(), key)
    h += ('<TABLE WIDTH=600 BORDER=0 CELLPADDING=6 CELLSPACING=0><TR VALIGN=TOP><TD BGCOLOR="%s">%s'
          '<FONT SIZE=4><B>Welcome to %s!</B></FONT><BR>%s</FONT>\n' % (light, FONT, key, hd['blurb']))
    h += '<P>%s<B>Suburbs of %s</B></FONT></P>\n<TABLE BORDER=0 CELLPADDING=3 WIDTH="100%%">\n' % (FONT, key)
    for s, d in hd['suburbs']:
        n = len([p for p in hp if p['suburb'] == s])
        h += ('<TR VALIGN=TOP><TD>%s</TD><TD>%s<B><A HREF="%s/index.html">%s</A></B> - %s <FONT SIZE=1>(%d homes)'
              '</FONT></FONT></TD></TR>\n' % (img(root, 'ball_yellow.gif'), FONT, s, s, d, n))
    h += '</TABLE>\n'
    # featured
    h += '<P>%s<B>Spotlight Homesteaders</B></FONT></P>\n' % FONT
    for p in featured:
        h += '<P>%s%s<BR><FONT SIZE=1>%s - by %s, %s/%s</FONT></FONT></P>\n' % (
            FONT, prow(p, root), p['desc'], p['v_handle'], p['suburb'], p['num'])
    # news
    h += '<P>%s<B>%s News</B></FONT></P>\n<UL>\n' % (FONT, key)
    topic, topic2 = TOPICS[key]
    for t in rr.sample(NEWS_TEMPLATES, 3):
        h += '<LI>%s%s</FONT>\n' % (FONT, t.format(hood=key, suburb=rr.choice(hd['suburbs'])[0], topic=topic,
                                                   topic2=topic2))
    h += '</UL>\n'
    # full directory
    h += '<P>%s<B>Complete %s Directory</B></FONT></P>\n' % (FONT, key)
    for s, _d in hd['suburbs']:
        sp = sorted([p for p in hp if p['suburb'] == s], key=lambda q: q['num'])
        h += '<P>%s<B><A HREF="%s/index.html">%s</A></B><BR>\n' % (FONT, s, s)
        for p in sp:
            h += '<FONT SIZE=1><TT>%s/%s/%d/</TT></FONT> %s<BR>\n' % (key, s, p['num'], prow(p, root))
        h += '</FONT></P>\n'
    h += '</TD>\n<TD WIDTH=170 BGCOLOR="%s">' % dark
    h += '<FONT FACE="Arial" SIZE=2 COLOR="#FFFFFF"><B>Community Leaders</B></FONT><BR>\n'
    for p in leaders:
        h += ('<FONT FACE="Arial" SIZE=1 COLOR="#FFFFFF">%s<BR><A HREF="%s%sindex.html"><FONT COLOR="#FFFF99">%s'
              '</FONT></A></FONT><BR><BR>\n' % (p['v_handle'], root, p['addr'], p['title']))
    h += ('<FONT FACE="Arial" SIZE=2 COLOR="#FFFFFF"><B>Move In!</B></FONT><BR><FONT FACE="Arial" SIZE=1 '
          'COLOR="#FFFFFF">Vacant lots are available in every suburb of %s.</FONT><BR>'
          '<A HREF="%sbuild.html?hood=%s">%s</A><BR><BR>\n' % (key, root, key, img(root, 'join_now.gif', 'Join now')))
    h += '<FONT FACE="Arial" SIZE=2 COLOR="#FFFFFF"><B>Chat</B></FONT><BR><A HREF="%schat.html?room=%s">' \
         '<FONT FACE="Arial" SIZE=1 COLOR="#FFFF99">Enter the %s chat room</FONT></A><BR><BR>\n' % (root, key, key)
    h += '<FONT FACE="Arial" SIZE=2 COLOR="#FFFFFF"><B>Other Neighborhoods</B></FONT><BR>\n'
    for o in HOODS:
        if o['key'] != key:
            h += '<A HREF="%s%s/index.html"><FONT FACE="Arial" SIZE=1 COLOR="#FFFFFF">%s</FONT></A><BR>\n' % (
                root, o['key'], o['key'])
    h += '</TD></TR></TABLE>\n'
    h += bottom(root)
    W(site, '%s/index.html' % key, h)


def suburb_page(site, hd, sub, desc, pages):
    root = '../../'
    key = hd['key']
    sp = sorted([p for p in pages if p['hood'] == key and p['suburb'] == sub], key=lambda q: q['num'])
    taken = set(p['num'] for p in sp)
    rr = random.Random(key + sub)
    vacant = []
    while len(vacant) < 6:
        n = rr.randint(1000, 9999)
        if n not in taken and n not in vacant:
            vacant.append(n)
    vacant.sort()
    h = top(root, 'GeoHoods: %s/%s' % (key, sub))
    h += ('<P>%s<A HREF="%sindex.html">GeoHoods</A> &gt; <A HREF="../index.html">%s</A> &gt; <B>%s</B></FONT></P>\n'
          % (FONT, root, key, sub))
    h += '<TABLE WIDTH=600 BORDER=0><TR><TD>%s</TD><TD>%s<FONT SIZE=5><B>%s/%s</B></FONT><BR><I>%s</I></FONT>' \
         '</TD></TR></TABLE>\n' % (img(root, 'hood_%s.gif' % key.lower()), FONT, key, sub, desc)
    h += ('<TABLE WIDTH=600 BORDER=1 CELLPADDING=4 CELLSPACING=0>\n<TR BGCOLOR="%s"><TH>%s<FONT COLOR="#FFFFFF">'
          'Address</FONT></FONT></TH><TH>%s<FONT COLOR="#FFFFFF">Home Page</FONT></FONT></TH><TH>%s<FONT '
          'COLOR="#FFFFFF">Homesteader</FONT></FONT></TH><TH>%s<FONT COLOR="#FFFFFF">Updated</FONT></FONT></TH></TR>\n'
          % (NAVY, FONT, FONT, FONT, FONT))
    for i, p in enumerate(sp):
        new = ' ' + img(root, 'new.gif', 'NEW!', ' ALIGN=ABSMIDDLE') if '1999' in p['updated'] and \
            any(m in p['updated'] for m in ('Sep', 'Oct', '9/', '10/')) else ''
        h += ('<TR BGCOLOR="%s" VALIGN=TOP><TD>%s<TT>%d</TT></FONT></TD><TD>%s<A HREF="%d/index.html">%s</A>%s<BR>'
              '<FONT SIZE=1>%s</FONT></FONT></TD><TD>%s%s</FONT></TD><TD>%s<FONT SIZE=1>%s</FONT></FONT></TD></TR>\n'
              % ('#FFFFCC' if i % 2 == 0 else '#FFFFFF', FONT, p['num'], FONT, p['num'], p['title'], new, p['desc'],
                 FONT, p['v_handle'], FONT, p['updated']))
    h += '</TABLE>\n'
    h += '<P>%s<B>Vacant lots in %s/%s</B> - move in today!<BR>\n' % (FONT, key, sub)
    h += ' '.join('<A HREF="%sbuild.html?hood=%s&amp;suburb=%s&amp;num=%d">%d</A>' % (root, key, sub, n, n)
                  for n in vacant)
    h += '</FONT></P>\n'
    others = [s for s, _d in hd['suburbs'] if s != sub]
    h += '<P>%sOther suburbs of %s: %s</FONT></P>\n' % (FONT, key, ' | '.join(
        '<A HREF="../%s/index.html">%s</A>' % (s, s) for s in others))
    h += bottom(root)
    W(site, '%s/%s/index.html' % (key, sub), h)


# ====================================================================== data for JS
def ghdata(site, pages):
    out = '// ghdata.js - the GeoHoods member database (generated). Used by search, the builder and File Manager.\n'
    out += 'var ghPages = new Array();\n'
    for i, p in enumerate(pages):
        files = ';'.join('%s:%d' % (f, os.path.getsize(os.path.join(site, p['addr'], f))) for f in p['files'])
        out += 'ghPages[%d] = new Array(%s);\n' % (i, ','.join(jstr(x) for x in (
            p['addr'], p['title'], p['v_handle'], p['owner'], p['hood'], p['suburb'], p['desc'], p['keywords'],
            files)))
    out += 'var ghHoods = new Array();\n'
    for i, hd in enumerate(HOODS):
        out += 'ghHoods[%d] = new Array(%s,%s,%s);\n' % (i, jstr(hd['key']), jstr(hd['tagline']),
                                                         jstr('|'.join(s for s, _d in hd['suburbs'])))
    W(site, 'ghdata.js', out)


def search_page(site):
    root = ''
    h = top(root, 'GeoHoods Search', '<SCRIPT LANGUAGE="JavaScript" SRC="ghdata.js"></SCRIPT>\n')
    h += '<P><FONT FACE="Arial" SIZE=5><B>Search Home Pages</B></FONT></P>\n'
    h += ('<FORM NAME="s" ACTION="search.html" METHOD="GET">%s<INPUT TYPE="text" NAME="q" SIZE=30> in '
          '<SELECT NAME="hood"><OPTION VALUE="">All Neighborhoods\n' % FONT)
    for hd in HOODS:
        h += '<OPTION VALUE="%s">%s\n' % (hd['key'], hd['key'])
    h += '</SELECT> <INPUT TYPE="submit" VALUE="Search"></FONT></FORM>\n'
    h += '''<TABLE WIDTH=600 BORDER=0><TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>
<SCRIPT LANGUAGE="JavaScript">
<!--
function getParam(name) {
  var s = location.search.substring(1);
  var parts = s.split("&");
  for (var i = 0; i < parts.length; i++) {
    var kv = parts[i].split("=");
    if (kv[0] == name && kv.length > 1) return unescape(kv[1].replace(/\\+/g, " "));
  }
  return "";
}
function clean(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
var q = getParam("q");
var hood = getParam("hood");
document.forms["s"].q.value = q;
for (var i = 0; i < document.forms["s"].hood.options.length; i++)
  if (document.forms["s"].hood.options[i].value == hood) document.forms["s"].hood.selectedIndex = i;
if (q != "" || hood != "") {
  var words = q.toLowerCase().split(" ");
  var hits = new Array();
  for (var i = 0; i < ghPages.length; i++) {
    var p = ghPages[i];
    if (hood != "" && p[4] != hood) continue;
    var text = (p[0] + " " + p[1] + " " + p[2] + " " + p[3] + " " + p[6] + " " + p[7]).toLowerCase();
    var ok = true;
    for (var j = 0; j < words.length; j++)
      if (words[j] != "" && text.indexOf(words[j]) < 0) ok = false;
    if (ok) hits[hits.length] = p;
  }
  document.write("<P><B>" + hits.length + "</B> home page" + (hits.length == 1 ? "" : "s") + " found for <B>" +
                 clean(q == "" ? hood : q) + "</B>.</P>");
  if (hits.length == 0)
    document.write("<P>No pages found. Try a different word, or browse the <A HREF=\\"neighborhoods.html\\">" +
                   "neighborhoods</A>.</P>");
  for (var i = 0; i < hits.length; i++) {
    var p = hits[i];
    document.write("<P><IMG SRC=\\"images/ball_blue.gif\\" WIDTH=14 HEIGHT=14> <B><A HREF=\\"" + p[0] +
                   "index.html\\">" + p[1] + "</A></B><BR>" + p[6] + "<BR><FONT SIZE=1 COLOR=\\"#008000\\">" +
                   "geohoods.com/" + p[0] + " - by " + p[2] + " - " + p[4] + "/" + p[5] + "</FONT></P>");
  }
} else {
  document.write("<P>Type a word and press Search to look through all " + ghPages.length +
                 " GeoHoods home pages. Try <A HREF=\\"search.html?q=monstropals\\">monstropals</A>, " +
                 "<A HREF=\\"search.html?q=bunker\\">bunker</A> or <A HREF=\\"search.html?q=poems\\">poems</A>.</P>");
}
// -->
</SCRIPT>
<NOSCRIPT>Search needs JavaScript. You can browse the <A HREF="directory/index.html">Members Directory</A>
instead.</NOSCRIPT>
</FONT></TD></TR></TABLE>
'''
    h += bottom(root)
    W(site, 'search.html', h)


def directory(site, pages):
    def letter(p):
        c = p['v_handle'][0].upper()
        if c == 'X' and p['v_handle'][:2] == 'xX':
            c = p['v_handle'][2].upper()
        return c if c.isalpha() else '0'
    groups = {}
    for p in pages:
        groups.setdefault(letter(p), []).append(p)
    letters = sorted(groups)
    root = '../'
    bar = '<P><CENTER>%s' % FONT + ' | '.join('<A HREF="%s.html"><B>%s</B></A>' % (L, L if L != '0' else '0-9')
                                               for L in letters) + '</FONT></CENTER></P>\n'
    h = top(root, 'GeoHoods Members Directory')
    h += '<P><FONT FACE="Arial" SIZE=5><B>Members Directory</B></FONT><BR>%sAll %d homesteaders, by member name. ' \
         'Looking for a topic instead? Try <A HREF="../search.html">Search</A>.</FONT></P>\n' % (FONT, len(pages))
    h += bar
    h += '<TABLE WIDTH=600 BORDER=1 CELLPADDING=4 CELLSPACING=0><TR BGCOLOR="%s"><TH>%s<FONT COLOR="#FFFFFF">' \
         'Neighborhood</FONT></FONT></TH><TH>%s<FONT COLOR="#FFFFFF">Homesteaders</FONT></FONT></TH></TR>\n' % (
             NAVY, FONT, FONT)
    for hd in HOODS:
        h += '<TR><TD>%s<A HREF="../%s/index.html">%s</A></FONT></TD><TD ALIGN=CENTER>%s%d</FONT></TD></TR>\n' % (
            FONT, hd['key'], hd['key'], FONT, len([p for p in pages if p['hood'] == hd['key']]))
    h += '</TABLE>\n'
    h += bottom(root)
    W(site, 'directory/index.html', h)
    for L in letters:
        h = top(root, 'GeoHoods Members Directory: %s' % L)
        h += '<P><FONT FACE="Arial" SIZE=5><B>Members: %s</B></FONT></P>\n' % (L if L != '0' else '0-9')
        h += bar
        h += '<TABLE WIDTH=600 BORDER=0 CELLPADDING=3 CELLSPACING=0>\n'
        for i, p in enumerate(sorted(groups[L], key=lambda q: q['v_handle'].lower())):
            h += ('<TR BGCOLOR="%s" VALIGN=TOP><TD>%s<B>%s</B></FONT></TD><TD>%s<A HREF="../%sindex.html">%s</A><BR>'
                  '<FONT SIZE=1>%s</FONT></FONT></TD></TR>\n' % ('#FFFFCC' if i % 2 == 0 else '#FFFFFF', FONT,
                                                                p['v_handle'], FONT, p['addr'], p['title'],
                                                                p['addr']))
        h += '</TABLE>\n<P>%s<A HREF="index.html">Back to the directory</A></FONT></P>\n' % FONT
        h += bottom(root)
        W(site, 'directory/%s.html' % L, h)


def cool_page(site, cool):
    root = ''
    h = top(root, 'GeoHoods Cool Page of the Day')
    h += '<P>%s <FONT FACE="Arial" SIZE=5><B>Cool Page of the Day</B></FONT></P>\n' % img(root, 'cool_face.gif')
    h += '<P>%sEvery day our Community Leaders pick one homepage that makes the Web a cooler place. Winners get the ' \
         'coveted Golden Shovel. Here are the last %d picks:</FONT></P>\n' % (FONT, len(cool))
    h += '<TABLE WIDTH=600 BORDER=0 CELLPADDING=5 CELLSPACING=0>\n'
    for i, c in enumerate(cool):
        h += ('<TR VALIGN=TOP BGCOLOR="%s"><TD NOWRAP>%s<B>%s</B></FONT></TD><TD>%s<B>%s</B> by %s<BR>%s<BR>'
              '<FONT SIZE=1>%s/%s</FONT></FONT></TD></TR>\n' % ('#FFF0E0' if i % 2 == 0 else '#FFFFFF', FONT,
                                                               c['cooldate'], FONT, prow(c, root), c['v_handle'],
                                                               c['blurb'], c['hood'], c['suburb']))
    h += '</TABLE>\n<P>%s</P>\n' % img(root, 'award_hammer.gif', 'Golden Shovel')
    h += bottom(root)
    W(site, 'cool.html', h)


# ====================================================================== join / builder / file manager
def join_page(site, pages):
    root = ''
    h = top(root, 'Join GeoHoods - Free Home Pages')
    h += ('<P><FONT FACE="Arial" SIZE=5><B>Join GeoHoods - It\'s FREE!</B></FONT></P>\n'
          '<TABLE WIDTH=600 BORDER=0 CELLPADDING=6><TR VALIGN=TOP><TD>%s'
          '<P>Becoming a GeoHoods homesteader takes about five minutes. You get:</P><UL>'
          '<LI><B>11 MB</B> of free web space\n<LI>Your own address in the neighborhood of your choice, like '
          '<TT>geohoods.com/Prairie/Litterbox/1234/</TT>\n<LI>Build-a-Page, the EZ Editor and the File Manager\n'
          '<LI>Free counters, guestbooks, clip art and %d original MIDI tunes\n<LI>A free e-mail account '
          '(<I>yourname</I>@geohoods.com)</UL>\n'
          '<P><B>Step 1:</B> Pick a <A HREF="neighborhoods.html">neighborhood</A> that fits your page.<BR>'
          '<B>Step 2:</B> Pick a vacant address (every suburb page lists a few).<BR>'
          '<B>Step 3:</B> Build your page with <A HREF="build.html">Build-a-Page</A>!</P>\n'
          '<P>Before you move in, please read the <A HREF="guidelines.html">Homesteader Agreement</A>.</P>'
          '<FORM ACTION="build.html" METHOD="GET"><INPUT TYPE="submit" VALUE="I Accept - Let Me Build My Page!"> '
          '<INPUT TYPE="button" VALUE="I Do Not Accept" onClick="alert(\'Maybe next time! The neighborhood will '
          'still be here.\')"></FORM></FONT></TD>\n<TD WIDTH=150 ALIGN=CENTER>%s<P>%s</P>%s</TD></TR></TABLE>\n' % (
              FONT, len(MIDI_TITLES), img(root, 'join_now.gif'), img(root, 'construction.gif'),
              img(root, 'dancing_baby.gif')))
    h += '<P>%s<B>Where should I live?</B></FONT></P><TABLE WIDTH=600 BORDER=0 CELLPADDING=3>\n' % FONT
    for hd in HOODS:
        h += '<TR><TD>%s</TD><TD>%s<A HREF="build.html?hood=%s">%s</A> - %s</FONT></TD></TR>\n' % (
            img(root, 'hood_%s.gif' % hd['key'].lower()), FONT, hd['key'], hd['key'], hd['tagline'])
    h += '</TABLE>\n'
    h += bottom(root)
    W(site, 'join.html', h)


TEMPLATES_JS = [
    # name, label, background, bgcolor, text, link, face, line, bullet
    ('starfield', 'Starfield (sci-fi, space, mystery)', 'stars_bg.gif', '#000000', '#FFFF00', '#00FFFF',
     'Arial, Helvetica', 'line_stars.gif', 'bullet_star.gif'),
    ('kitty', 'Pastel Kitty (cute, pets, friends)', 'bg_hearts.gif', '#FFE6F0', '#993366', '#CC0066', 'Comic Sans MS',
     'line_hearts.gif', 'bullet_heart.gif'),
    ('classic', 'Plain & Simple (classic gray)', '', '#C0C0C0', '#000000', '#0000FF', 'Times New Roman', '', ''),
    ('flames', 'Flame On! (bands, cars, wrestling)', 'bg_border_flames.gif', '#140000', '#FFCC00', '#FF6600',
     'Arial, Helvetica', 'flames.gif', 'bullet_skull.gif'),
    ('country', 'Country Kitchen (family, recipes)', 'bg_gingham.gif', '#FFAAAA', '#660000', '#CC0000',
     'Comic Sans MS', 'line_rope.gif', 'ball_red.gif'),
    ('sports', 'Game Day (sports, teams)', 'bg_grass.gif', '#289628', '#FFFFFF', '#FFFF00', 'Arial Black, Arial',
     'rainbow_hr.gif', 'ball_green.gif'),
    ('spooky', 'Dark & Spooky (poetry, goth)', 'bg_blood.gif', '#000000', '#CC0000', '#999999', 'Times New Roman',
     'line_barbed.gif', 'bullet_skull.gif'),
    ('neon', 'Neon Party (teens, music)', '', '#000000', '#FF00FF', '#00FFFF', 'Comic Sans MS', 'rainbow_line.gif',
     'bullet_star.gif'),
    ('clouds', 'Blue Skies (travel, babies)', 'bg_clouds.gif', '#78B4FF', '#000080', '#CC0000', 'Comic Sans MS',
     'rainbow_line.gif', 'ball_blue.gif'),
    ('geek', 'Green Screen (computers)', 'bg_binary.gif', '#000000', '#00FF00', '#FFFFFF', 'Courier New',
     'line_laser.gif', 'ball_green.gif'),
]
BG_CHOICES = ['stars_bg.gif', 'bg_space.gif', 'bg_nebula.gif', 'bg_hearts.gif', 'bg_flowers.gif', 'bg_paws.gif',
              'bg_glitter.gif', 'bg_clouds.gif', 'bg_parchment.gif', 'bg_marble.gif', 'bg_brick.gif', 'bg_camo.gif',
              'bg_wood.gif', 'bg_grass.gif', 'bg_water.gif', 'bg_bubbles.gif', 'bg_snow.gif', 'bg_binary.gif',
              'bg_leopard.gif', 'bg_denim.gif', 'bg_checker.gif', 'bg_gingham.gif', 'bg_concrete.gif', 'bg_blood.gif',
              'bg_notebook.gif', 'bg_border_blue.gif', 'bg_border_purple.gif', 'bg_border_green.gif',
              'bg_border_pink.gif', 'bg_border_flames.gif']
CLIPART = ['welcome.gif', 'dancing_baby.gif', 'kitten.gif', 'puppy.gif', 'hamster.gif', 'ufo.gif', 'alien.gif',
           'skull_spin.gif', 'heart.gif', 'twinkle.gif', 'cd_spin.gif', 'notes.gif', 'football.gif', 'globe.gif',
           'construction.gif', 'worker.gif', 'hot.gif', 'y2k_bomb.gif', 'pie.gif', 'chili.gif', 'train.gif',
           'gear.gif', 'snowman.gif', 'pumpkin.gif', 'candle.gif', 'tower.gif', 'cool_face.gif',
           'mp_voltwhisker.gif', 'mp_flintfox.gif', 'photo_me.gif', 'photo_me2.gif', 'photo_cat.gif', 'photo_dog.gif',
           'photo_family.gif', 'photo_ufo.gif', 'photo_car.gif', 'photo_beach.gif']


def builder_js(site, pages):
    js = ['// builder.js - GeoHoods Build-a-Page and EZ Editor (JavaScript 1.2). Needs ghdata.js.']
    js.append('var tpl = new Array();')
    for i, t in enumerate(TEMPLATES_JS):
        js.append('tpl[%d] = new Array(%s);' % (i, ','.join(jstr(x) for x in t)))
    js.append('var bgs = new Array(%s);' % ','.join(jstr(b) for b in BG_CHOICES))
    js.append('var clips = new Array(%s);' % ','.join(jstr(c) for c in CLIPART))
    js.append('var clipW = new Array(%s);' % ','.join(str(SIZES[c][0]) for c in CLIPART))
    js.append('var clipH = new Array(%s);' % ','.join(str(SIZES[c][1]) for c in CLIPART))
    tunes = sorted(MIDI_TITLES.items())
    js.append('var midis = new Array(%s);' % ','.join(jstr(n) for n, _t in tunes))
    js.append('var midiNames = new Array(%s);' % ','.join(jstr(t) for _n, t in tunes))
    js.append(r'''
function getParam(name) {
  var s = location.search.substring(1);
  var parts = s.split("&");
  for (var i = 0; i < parts.length; i++) {
    var kv = parts[i].split("=");
    if (kv[0] == name && kv.length > 1) return unescape(kv[1].replace(/\+/g, " "));
  }
  return "";
}
function esc(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function isTaken(hood, sub, num) {
  var a = hood + "/" + sub + "/" + num + "/";
  for (var i = 0; i < ghPages.length; i++) if (ghPages[i][0] == a) return true;
  return false;
}
function selVal(sel) { return sel.options[sel.selectedIndex].value; }
function fillHoods() {
  var f = document.forms["builder"];
  f.hood.options.length = 0;
  for (var i = 0; i < ghHoods.length; i++) f.hood.options[i] = new Option(ghHoods[i][0] + " - " + ghHoods[i][1], ghHoods[i][0]);
}
function hoodChanged() {
  var f = document.forms["builder"];
  var subs = ghHoods[f.hood.selectedIndex][2].split("|");
  f.suburb.options.length = 0;
  for (var i = 0; i < subs.length; i++) f.suburb.options[i] = new Option(subs[i], subs[i]);
}
function findVacant() {
  var f = document.forms["builder"];
  var n;
  do { n = 1000 + Math.floor(Math.random() * 9000); } while (isTaken(selVal(f.hood), selVal(f.suburb), n));
  f.num.value = n;
  window.status = "Address " + n + " is vacant!";
}
function checkAddr() {
  var f = document.forms["builder"];
  var n = parseInt(f.num.value, 10);
  if (isNaN(n) || n < 1000 || n > 9999) { alert("Addresses are numbers from 1000 to 9999."); return false; }
  if (isTaken(selVal(f.hood), selVal(f.suburb), n)) {
    alert("Sorry! " + selVal(f.hood) + "/" + selVal(f.suburb) + "/" + n + " is already taken. Try 'Find a vacant lot'.");
    return false;
  }
  return true;
}
function initBuilder() {
  var f = document.forms["builder"];
  fillHoods();
  var h = getParam("hood");
  for (var i = 0; i < ghHoods.length; i++) if (ghHoods[i][0] == h) f.hood.selectedIndex = i;
  hoodChanged();
  var s = getParam("suburb");
  for (var i = 0; i < f.suburb.options.length; i++) if (f.suburb.options[i].value == s) f.suburb.selectedIndex = i;
  var n = getParam("num");
  if (n != "") f.num.value = n; else findVacant();
  f.template.options.length = 0;
  for (var i = 0; i < tpl.length; i++) f.template.options[i] = new Option(tpl[i][1], tpl[i][0]);
  f.bg.options.length = 0;
  f.bg.options[0] = new Option("(use the template's background)", "");
  for (var i = 0; i < bgs.length; i++) f.bg.options[i + 1] = new Option(bgs[i], bgs[i]);
  f.clip.options.length = 0;
  f.clip.options[0] = new Option("(no picture)", "");
  for (var i = 0; i < clips.length; i++) f.clip.options[i + 1] = new Option(clips[i], i);
  f.midi.options.length = 0;
  f.midi.options[0] = new Option("(no music)", "");
  for (var i = 0; i < midis.length; i++) f.midi.options[i + 1] = new Option(midiNames[i], midis[i]);
  f.clip.selectedIndex = 2;
}
function bgChanged() {
  var f = document.forms["builder"];
  var b = selVal(f.bg);
  if (b == "") b = tpl[f.template.selectedIndex][2];
  document.images["bgprev"].src = b == "" ? "images/spacer.gif" : "images/" + b;
}
function clipChanged() {
  var f = document.forms["builder"];
  var c = selVal(f.clip);
  document.images["clipprev"].src = c == "" ? "images/spacer.gif" : "images/" + clips[c];
}
function counterDigits(style) {
  var s = "", n = "000001";
  for (var i = 0; i < n.length; i++)
    s += "<IMG SRC=\"../../../images/" + style + "_" + n.charAt(i) + ".gif\" WIDTH=" + (style == "digit" ? 15 : 14) + " HEIGHT=20>";
  return s;
}
function makeHTML() {
  var f = document.forms["builder"];
  var t = tpl[f.template.selectedIndex];
  var bg = selVal(f.bg); if (bg == "") bg = t[2];
  var text = f.textcolor.value != "" ? f.textcolor.value : t[4];
  var link = f.linkcolor.value != "" ? f.linkcolor.value : t[5];
  var face = selVal(f.face); if (face == "") face = t[6];
  var I = "../../../images/";
  var title = f.title.value == "" ? "My Home Page" : f.title.value;
  var h = "<HTML>\n<HEAD>\n<TITLE>" + esc(title) + "</TITLE>\n<META NAME=\"GENERATOR\" CONTENT=\"GeoHoods Build-a-Page 2.1\">\n</HEAD>\n";
  h += "<BODY BGCOLOR=\"" + t[3] + "\"" + (bg != "" ? " BACKGROUND=\"" + I + bg + "\"" : "") + " TEXT=\"" + text + "\" LINK=\"" + link + "\" VLINK=\"" + link + "\">\n";
  h += "<CENTER>\n<FONT FACE=\"" + face + "\">\n";
  if (selVal(f.midi) != "") h += "<BGSOUND SRC=\"../../../midi/" + selVal(f.midi) + ".mid\" LOOP=INFINITE>\n<EMBED SRC=\"../../../midi/" + selVal(f.midi) + ".mid\" AUTOSTART=\"true\" LOOP=\"true\" HIDDEN=\"true\">\n";
  if (f.marquee.checked && f.marqueetext.value != "") h += "<MARQUEE><B>" + esc(f.marqueetext.value) + "</B></MARQUEE>\n";
  h += "<H1>" + esc(f.headline.value == "" ? title : f.headline.value) + "</H1>\n";
  var c = selVal(f.clip);
  if (c != "") h += "<P><IMG SRC=\"" + I + clips[c] + "\" WIDTH=" + clipW[c] + " HEIGHT=" + clipH[c] + "></P>\n";
  if (t[7] != "") h += "<P><IMG SRC=\"" + I + t[7] + "\"></P>\n"; else h += "<HR>\n";
  var about = f.about.value.split("\n");
  for (var i = 0; i < about.length; i++) if (about[i] != "") h += "<P>" + about[i] + "</P>\n";
  var links = "";
  for (var i = 1; i <= 3; i++) {
    var ln = f.elements["linkname" + i].value, lu = f.elements["linkurl" + i].value;
    if (ln != "" && lu != "" && lu != "http://")
      links += (t[8] != "" ? "<IMG SRC=\"" + I + t[8] + "\"> " : "<LI>") + "<A HREF=\"" + esc(lu) + "\">" + esc(ln) + "</A><BR>\n";
  }
  if (links != "") h += "<H2>My Favorite Links</H2>\n" + (t[8] == "" ? "<UL>\n" + links + "</UL>\n" : "<P>" + links + "</P>\n");
  if (t[7] != "") h += "<P><IMG SRC=\"" + I + t[7] + "\"></P>\n";
  if (f.email.value != "") h += "<P><A HREF=\"mailto:" + esc(f.email.value) + "\"><IMG SRC=\"" + I + "mailme.gif\" WIDTH=100 HEIGHT=30 BORDER=0></A></P>\n";
  if (f.guestbook.checked) h += "<P><A HREF=\"guestbook.html\"><IMG SRC=\"" + I + "sign_gb.gif\" WIDTH=120 HEIGHT=44 BORDER=0></A></P>\n";
  if (selVal(f.counter) != "") h += "<P>You are visitor number " + counterDigits(selVal(f.counter)) + "</P>\n";
  if (f.construction.checked) h += "<P><IMG SRC=\"" + I + "construction.gif\" WIDTH=140 HEIGHT=50></P>\n";
  h += "<P><FONT SIZE=1>Page built with GeoHoods Build-a-Page. Last updated: " + (new Date()).toLocaleString() + "</FONT></P>\n";
  h += "</FONT>\n</CENTER>\n";
  h += "<P><CENTER><TABLE BORDER=1 CELLPADDING=3 CELLSPACING=0 BGCOLOR=\"#FFFFCC\"><TR><TD><A HREF=\"../../../index.html\"><IMG SRC=\"" + I + "gh_88x31.gif\" WIDTH=88 HEIGHT=31 BORDER=0></A></TD>";
  h += "<TD ALIGN=CENTER><FONT FACE=\"Arial\" SIZE=1 COLOR=\"#000000\"><B><A HREF=\"../../../index.html\">GeoHoods</A></B> | <A HREF=\"../../index.html\">" + selVal(f.hood) + "</A> | <A HREF=\"../index.html\">" + selVal(f.suburb) + "</A><BR><A HREF=\"../../../join.html\">Get your own Free Home Page</A></FONT></TD></TR></TABLE></CENTER></P>\n";
  h += "</BODY>\n</HTML>\n";
  return h;
}
function siteBase() {
  var u = location.href;
  if (u.indexOf("?") >= 0) u = u.substring(0, u.indexOf("?"));
  if (u.indexOf("#") >= 0) u = u.substring(0, u.indexOf("#"));
  return u.substring(0, u.lastIndexOf("/") + 1);
}
function writePreview(html, addr) {
  var w = window.open("", "ghpreview", "width=700,height=500,scrollbars=yes,resizable=yes,toolbar=no");
  if (!w) { alert("Your pop-up blocker ate the preview window! Use 'Show me the HTML' instead."); return; }
  var base = "<BASE HREF=\"" + siteBase() + addr + "\">";
  w.document.open();
  w.document.write(html.replace("<HEAD>", "<HEAD>\n" + base));
  w.document.close();
  w.focus();
}
function addrOf() {
  var f = document.forms["builder"];
  return selVal(f.hood) + "/" + selVal(f.suburb) + "/" + f.num.value + "/";
}
function previewPage() {
  if (!checkAddr()) return;
  writePreview(makeHTML(), addrOf());
}
function showSource() {
  document.forms["builder"].source.value = makeHTML();
  location.hash = "source";
}
function moveIn() {
  var f = document.forms["builder"];
  if (f.member.value == "") { alert("Please choose a member name."); f.member.focus(); return; }
  if (f.title.value == "") { alert("Please give your page a title."); f.title.focus(); return; }
  if (!checkAddr()) return;
  f.source.value = makeHTML();
  location.href = "movedin.html?addr=" + escape(addrOf()) + "&member=" + escape(f.member.value);
}
''')
    W(site, 'builder.js', '\n'.join(js) + '\n')


def build_page(site):
    root = ''
    h = top(root, 'GeoHoods Build-a-Page', '<SCRIPT LANGUAGE="JavaScript" SRC="ghdata.js"></SCRIPT>\n'
                                           '<SCRIPT LANGUAGE="JavaScript" SRC="builder.js"></SCRIPT>\n',
            onload='initBuilder(); bgChanged(); clipChanged();')
    face_opts = ''.join('<OPTION VALUE="%s">%s\n' % (v, l) for v, l in [
        ('', '(template font)'), ('Comic Sans MS', 'Comic Sans MS'), ('Arial, Helvetica', 'Arial'),
        ('Times New Roman', 'Times New Roman'), ('Courier New', 'Courier New'), ('Verdana', 'Verdana'),
        ('Impact', 'Impact'), ('Georgia', 'Georgia')])
    color_opts = ''.join('<OPTION VALUE="%s">%s\n' % (v, l) for v, l in [
        ('', '(template color)'), ('#000000', 'Black'), ('#FFFFFF', 'White'), ('#FF0000', 'Red'),
        ('#FFFF00', 'Yellow'), ('#00FF00', 'Lime'), ('#00FFFF', 'Aqua'), ('#FF00FF', 'Hot Pink'),
        ('#000080', 'Navy'), ('#800080', 'Purple'), ('#FF9900', 'Orange'), ('#C0C0C0', 'Silver')])
    h += ('<P><FONT FACE="Arial" SIZE=5><B>Build-a-Page</B></FONT><BR>%sFill in the form, press <B>Preview</B> to see '
          'your page, and press <B>Move In!</B> when you love it. No HTML required (but you can use it if you know '
          'some).</FONT></P>\n' % FONT)
    h += '''<FORM NAME="builder" onSubmit="return false;">
<TABLE WIDTH=600 BORDER=0 CELLPADDING=4 CELLSPACING=0>
<TR><TD COLSPAN=2 BGCOLOR="#003399"><FONT FACE="Arial" COLOR="#FFFFFF"><B>1. Your Address</B></FONT></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD><FONT FACE="Arial" SIZE=2>Neighborhood:</FONT></TD><TD><SELECT NAME="hood" onChange="hoodChanged(); findVacant();"><OPTION>Loading...</SELECT></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD><FONT FACE="Arial" SIZE=2>Suburb:</FONT></TD><TD><SELECT NAME="suburb" onChange="findVacant();"><OPTION>Loading...</SELECT></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD><FONT FACE="Arial" SIZE=2>Address number:</FONT></TD><TD><INPUT TYPE="text" NAME="num" SIZE=6 MAXLENGTH=4> <INPUT TYPE="button" VALUE="Find a vacant lot" onClick="findVacant();"> <INPUT TYPE="button" VALUE="Is it free?" onClick="if (checkAddr()) alert('Good news: that address is vacant!');"></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD><FONT FACE="Arial" SIZE=2>Member name:</FONT></TD><TD><INPUT TYPE="text" NAME="member" SIZE=20> <FONT FACE="Arial" SIZE=1>(letters and numbers, like StarGrrl77)</FONT></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD><FONT FACE="Arial" SIZE=2>E-mail:</FONT></TD><TD><INPUT TYPE="text" NAME="email" SIZE=30></TD></TR>
<TR><TD COLSPAN=2 BGCOLOR="#003399"><FONT FACE="Arial" COLOR="#FFFFFF"><B>2. The Look</B></FONT></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD><FONT FACE="Arial" SIZE=2>Template:</FONT></TD><TD><SELECT NAME="template" onChange="bgChanged();"><OPTION>Loading...</SELECT></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD VALIGN=TOP><FONT FACE="Arial" SIZE=2>Background:</FONT></TD><TD><SELECT NAME="bg" onChange="bgChanged();"><OPTION>Loading...</SELECT><BR><TABLE BORDER=1 CELLPADDING=0 CELLSPACING=0><TR><TD><IMG NAME="bgprev" SRC="images/stars_bg.gif" WIDTH=96 HEIGHT=48></TD></TR></TABLE></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD><FONT FACE="Arial" SIZE=2>Text color:</FONT></TD><TD><SELECT NAME="textcolorsel" onChange="this.form.textcolor.value = this.options[this.selectedIndex].value;">COLOROPTS</SELECT> <INPUT TYPE="text" NAME="textcolor" SIZE=8></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD><FONT FACE="Arial" SIZE=2>Link color:</FONT></TD><TD><SELECT NAME="linkcolorsel" onChange="this.form.linkcolor.value = this.options[this.selectedIndex].value;">COLOROPTS</SELECT> <INPUT TYPE="text" NAME="linkcolor" SIZE=8></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD><FONT FACE="Arial" SIZE=2>Font:</FONT></TD><TD><SELECT NAME="face">FACEOPTS</SELECT></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD VALIGN=TOP><FONT FACE="Arial" SIZE=2>Picture:</FONT></TD><TD><SELECT NAME="clip" onChange="clipChanged();"><OPTION>Loading...</SELECT><BR><IMG NAME="clipprev" SRC="images/dancing_baby.gif"></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD><FONT FACE="Arial" SIZE=2>Music:</FONT></TD><TD><SELECT NAME="midi"><OPTION>Loading...</SELECT> <INPUT TYPE="button" VALUE="Listen" onClick="var m = this.form.midi.options[this.form.midi.selectedIndex].value; if (m != '') window.open('midi/' + m + '.mid', 'midiwin', 'width=200,height=100');"></TD></TR>
<TR><TD COLSPAN=2 BGCOLOR="#003399"><FONT FACE="Arial" COLOR="#FFFFFF"><B>3. Your Words</B></FONT></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD><FONT FACE="Arial" SIZE=2>Page title:</FONT></TD><TD><INPUT TYPE="text" NAME="title" SIZE=40></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD><FONT FACE="Arial" SIZE=2>Big headline:</FONT></TD><TD><INPUT TYPE="text" NAME="headline" SIZE=40 VALUE="Welcome To My Home Page!"></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD><FONT FACE="Arial" SIZE=2>Scrolling text:</FONT></TD><TD><INPUT TYPE="checkbox" NAME="marquee" CHECKED> <INPUT TYPE="text" NAME="marqueetext" SIZE=35 VALUE="Thanks for visiting!!! Sign my guestbook!!!"></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD VALIGN=TOP><FONT FACE="Arial" SIZE=2>About you:<BR><FONT SIZE=1>(HTML is OK)</FONT></FONT></TD><TD><TEXTAREA NAME="about" ROWS=6 COLS=45 WRAP=VIRTUAL>Hi! This is my brand new home page. I like computers, music and my cat. More stuff coming soon!</TEXTAREA></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD VALIGN=TOP><FONT FACE="Arial" SIZE=2>Favorite links:</FONT></TD><TD><FONT FACE="Arial" SIZE=1>
Name <INPUT TYPE="text" NAME="linkname1" SIZE=15 VALUE="GeoHoods"> URL <INPUT TYPE="text" NAME="linkurl1" SIZE=22 VALUE="../../../index.html"><BR>
Name <INPUT TYPE="text" NAME="linkname2" SIZE=15 VALUE="Hamster Shuffle"> URL <INPUT TYPE="text" NAME="linkurl2" SIZE=22 VALUE="../../../../hamstershuffle/index.html"><BR>
Name <INPUT TYPE="text" NAME="linkname3" SIZE=15> URL <INPUT TYPE="text" NAME="linkurl3" SIZE=22 VALUE="http://"></FONT></TD></TR>
<TR><TD COLSPAN=2 BGCOLOR="#003399"><FONT FACE="Arial" COLOR="#FFFFFF"><B>4. Extras</B></FONT></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD><FONT FACE="Arial" SIZE=2>Counter:</FONT></TD><TD><SELECT NAME="counter"><OPTION VALUE="digit">Classic<OPTION VALUE="led">Green LED<OPTION VALUE="odo">Odometer<OPTION VALUE="">No counter</SELECT></TD></TR>
<TR BGCOLOR="#FFFFCC"><TD><FONT FACE="Arial" SIZE=2>Also add:</FONT></TD><TD><FONT FACE="Arial" SIZE=2><INPUT TYPE="checkbox" NAME="guestbook" CHECKED> Guestbook button &nbsp; <INPUT TYPE="checkbox" NAME="construction"> Under construction sign</FONT></TD></TR>
<TR><TD COLSPAN=2 ALIGN=CENTER BGCOLOR="#EEEEEE"><INPUT TYPE="button" VALUE="Preview My Page" onClick="previewPage();"> <INPUT TYPE="button" VALUE="Show Me The HTML" onClick="showSource();"> <INPUT TYPE="button" VALUE="Move In!" onClick="moveIn();"></TD></TR>
</TABLE>
<A NAME="source"></A>
<P><FONT FACE="Arial" SIZE=2><B>Your page's HTML</B> - save this as <TT>index.html</TT> and upload it with the <A HREF="filemanager.html">File Manager</A>:</FONT><BR>
<TEXTAREA NAME="source" ROWS=12 COLS=70 WRAP=OFF></TEXTAREA></P>
</FORM>
<NOSCRIPT><P><B>Build-a-Page needs JavaScript.</B> Please turn it on in your browser preferences, or use the
<A HREF="help.html">Advanced HTML instructions</A>.</P></NOSCRIPT>
'''.replace('COLOROPTS', color_opts).replace('FACEOPTS', face_opts)
    h += bottom(root)
    W(site, 'build.html', h)

    h = top(root, 'Welcome to the Neighborhood!', '<SCRIPT LANGUAGE="JavaScript" SRC="builder.js"></SCRIPT>\n')
    h += '''<P><FONT FACE="Arial" SIZE=5><B>Welcome to the Neighborhood!</B></FONT></P>
<P>IMGBABY</P>
<FONT FACE="Arial, Helvetica" SIZE=2>
<SCRIPT LANGUAGE="JavaScript">
<!--
var addr = getParam("addr"), member = getParam("member");
document.write("<P>Congratulations, <B>" + esc(member) + "</B>! You are now a GeoHoods homesteader.</P>");
document.write("<P>Your new address is <B><TT>geohoods.com/" + esc(addr) + "</TT></B></P>");
document.write("<P>Your page has been sent to the moving van. To finish moving in, save the HTML from Build-a-Page as " +
  "<TT>index.html</TT> and upload it with the <A HREF=\\"filemanager.html?member=" + escape(member) + "\\">File Manager</A>. " +
  "(Tip: press your browser's Back button to get your HTML again.)</P>");
// -->
</SCRIPT>
<P>While you wait, why not visit your new <A HREF="neighborhoods.html">neighbors</A> and sign a few guestbooks?</P>
</FONT>
'''.replace('IMGBABY', img(root, 'dancing_baby.gif') + ' ' + img(root, 'award_hammer.gif') + ' ' +
            img(root, 'dancing_baby.gif'))
    h += bottom(root)
    W(site, 'movedin.html', h)


def filemanager_page(site):
    root = ''
    h = top(root, 'GeoHoods File Manager', '<SCRIPT LANGUAGE="JavaScript" SRC="ghdata.js"></SCRIPT>\n'
                                           '<SCRIPT LANGUAGE="JavaScript" SRC="builder.js"></SCRIPT>\n')
    h += '''<P><FONT FACE="Arial" SIZE=5><B>File Manager</B></FONT></P>
<FONT FACE="Arial, Helvetica" SIZE=2>
<SCRIPT LANGUAGE="JavaScript">
<!--
var member = getParam("member");
var me = null;
for (var i = 0; i < ghPages.length; i++)
  if (member != "" && ghPages[i][2].toLowerCase() == member.toLowerCase()) me = ghPages[i];
function editFile(name) {
  var f = document.forms["editor"];
  f.filename.value = name;
  f.code.value = "Loading " + name + " ...";
  document.getElementById("loaderframe").src = me[0] + name;
  location.hash = "editor";
}
function loaded() {
  if (me == null) return;
  var f = document.forms["editor"];
  if (f.filename.value == "") return;
  var d = null;
  try { d = window.frames["loader"].document; } catch (e) { d = null; }
  if (d && d.documentElement) f.code.value = "<HTML>\\n" + d.documentElement.innerHTML + "\\n</HTML>";
  else f.code.value = "<!-- The EZ Editor could not open this file from here. Try the View link. -->";
}
function saveFile() {
  alert("Saved " + document.forms["editor"].filename.value + "!\\n\\nOur servers are very busy today, so it may take " +
        "up to 15 minutes before the changes show up on your page.");
}
function previewFile() {
  writePreview(document.forms["editor"].code.value, me[0]);
}
if (member == "") {
  document.write("<P>Please log in to manage your files.</P>");
  document.write("<FORM NAME=\\"lf\\" onSubmit=\\"location.href='filemanager.html?member=' + escape(document.forms['lf'].m.value); return false;\\">" +
    "<TABLE BORDER=0 BGCOLOR=\\"#EEFFEE\\" CELLPADDING=6><TR><TD><FONT FACE=Arial SIZE=2>Member name:</FONT></TD><TD><INPUT TYPE=text NAME=m SIZE=20></TD></TR>" +
    "<TR><TD><FONT FACE=Arial SIZE=2>Password:</FONT></TD><TD><INPUT TYPE=password NAME=pw SIZE=20></TD></TR>" +
    "<TR><TD></TD><TD><INPUT TYPE=submit VALUE=\\"Login\\"></TD></TR></TABLE></FORM>");
  document.write("<P><FONT SIZE=1>Psst: try one of our homesteaders, like <A HREF=\\"filemanager.html?member=" +
    escape(ghPages[7][2]) + "\\">" + esc(ghPages[7][2]) + "</A>. (The password check is broken today. Don't tell anyone.)</FONT></P>");
} else if (me == null) {
  document.write("<P>Welcome, <B>" + esc(member) + "</B>! Your account was created, but you have not moved in yet.</P>");
  document.write("<P>Your directory is empty. <A HREF=\\"build.html\\">Build your page now</A> and come back to upload it.</P>");
  document.write("<P><B>Space used:</B> 0 KB of 11 MB</P>");
} else {
  var files = me[8].split(";");
  var total = 0;
  document.write("<P>Welcome back, <B>" + esc(me[2]) + "</B>! Your home page is <B><A HREF=\\"" + me[0] + "index.html\\">" +
                 "geohoods.com/" + me[0] + "</A></B></P>");
  document.write("<TABLE WIDTH=600 BORDER=1 CELLPADDING=4 CELLSPACING=0><TR BGCOLOR=\\"#003399\\"><TH><FONT COLOR=white FACE=Arial SIZE=2>File</FONT></TH>" +
                 "<TH><FONT COLOR=white FACE=Arial SIZE=2>Size</FONT></TH><TH><FONT COLOR=white FACE=Arial SIZE=2>Actions</FONT></TH></TR>");
  for (var i = 0; i < files.length; i++) {
    var nm = files[i].split(":")[0], sz = parseInt(files[i].split(":")[1], 10);
    total += sz;
    document.write("<TR BGCOLOR=\\"" + (i % 2 ? "#FFFFFF" : "#FFFFCC") + "\\"><TD><FONT FACE=Arial SIZE=2>" +
                   "<IMG SRC=\\"images/ball_blue.gif\\" WIDTH=14 HEIGHT=14> " + nm + "</FONT></TD><TD ALIGN=right><FONT FACE=Arial SIZE=2>" +
                   Math.ceil(sz / 1024) + " KB</FONT></TD><TD><FONT FACE=Arial SIZE=2><A HREF=\\"" + me[0] + nm + "\\" TARGET=\\"_blank\\">View</A> | " +
                   "<A HREF=\\"javascript:editFile('" + nm + "')\\">Edit</A> | <A HREF=\\"javascript:alert('Rename is disabled during Y2K testing.')\\">Rename</A> | " +
                   "<A HREF=\\"javascript:if (confirm('Really delete " + nm + "?')) alert('Just kidding. We never delete anything.')\\">Delete</A></FONT></TD></TR>");
  }
  document.write("</TABLE>");
  document.write("<P><B>Space used:</B> " + Math.ceil(total / 1024) + " KB of 11 MB (" + (Math.round(total / 115343.36 * 10) / 10) + "%)</P>");
}
// -->
</SCRIPT>
<NOSCRIPT><P>The File Manager needs JavaScript.</P></NOSCRIPT>
<P><B>Upload files</B> (up to 5 at a time):</P>
<FORM NAME="up" onSubmit="alert('Upload complete! (Your files will appear after the next server sync.)'); return false;">
<INPUT TYPE="file" NAME="f1" SIZE=30><BR><INPUT TYPE="file" NAME="f2" SIZE=30><BR><INPUT TYPE="submit" VALUE="Upload Files">
</FORM>
<A NAME="editor"></A>
<FORM NAME="editor" onSubmit="return false;">
<P><B>EZ Editor</B> - editing <INPUT TYPE="text" NAME="filename" SIZE=20 VALUE=""><BR>
<TEXTAREA NAME="code" ROWS=14 COLS=72 WRAP=OFF></TEXTAREA><BR>
<INPUT TYPE="button" VALUE="Save" onClick="saveFile();"> <INPUT TYPE="button" VALUE="Preview" onClick="if (me) previewFile();">
<INPUT TYPE="reset" VALUE="Undo All Changes"></P>
</FORM>
<IFRAME NAME="loader" ID="loaderframe" SRC="images/index.html" WIDTH=1 HEIGHT=1 FRAMEBORDER=0 onLoad="loaded();"></IFRAME>
</FONT>
'''
    h += bottom(root)
    W(site, 'filemanager.html', h)


# ====================================================================== add-ons, rings, misc
def addons(site, rings):
    root = '../'
    secs = [('clipart.html', 'Clip Art & Animations', 'Flames, skulls, kittens and every other thing a homepage needs.'),
            ('backgrounds.html', 'Backgrounds', 'Tiled backgrounds: stars, hearts, camo, marble, gingham and more.'),
            ('counters.html', 'Counters', 'Show the world how popular you are.'),
            ('guestbooks.html', 'Guestbooks', 'Let your visitors sign in.'),
            ('midi.html', 'MIDI Music', 'Original background tunes, free for homesteaders.'),
            ('webrings.html', 'Webrings', 'Link up with pages like yours.')]
    h = top(root, 'GeoHoods Home Page Add-Ons')
    h += '<P><FONT FACE="Arial" SIZE=5><B>Home Page Add-Ons</B></FONT><BR>%sFree goodies for GeoHoods ' \
         'homesteaders. Everything here was made by the GeoHoods art department (two guys and a scanner).' \
         '</FONT></P>\n<TABLE WIDTH=600 CELLPADDING=6>\n' % FONT
    for fn, t, d in secs:
        h += '<TR><TD>%s</TD><TD>%s<B><A HREF="%s">%s</A></B><BR>%s</FONT></TD></TR>\n' % (
            img(root, 'ball_red.gif'), FONT, fn, t, d)
    h += '</TABLE>\n' + bottom(root)
    W(site, 'addons/index.html', h)

    cats = [('Animations', ['flames.gif', 'fire.gif', 'skull_spin.gif', 'mail_fly.gif', 'email.gif', 'dancing_baby.gif',
                            'worker.gif', 'barricade.gif', 'construction.gif', 'ufo.gif', 'alien.gif', 'kitten.gif',
                            'puppy.gif', 'hamster.gif', 'heart.gif', 'twinkle.gif', 'cd_spin.gif', 'notes.gif',
                            'football.gif', 'globe.gif', 'gear.gif', 'candle.gif', 'y2k_bomb.gif', 'snowman.gif',
                            'tower.gif', 'train.gif', 'pie.gif', 'hot.gif', 'cool_face.gif', 'new.gif', 'updated.gif',
                            'welcome.gif', 'mailbox.gif', 'webcam_off.gif', 'kava_applet.gif']),
            ('Monstropals', ['mp_flintfox.gif', 'mp_puddlepup.gif', 'mp_sproutle.gif', 'mp_voltwhisker.gif',
                             'mp_gloomoth.gif', 'mp_pebblin.gif']),
            ('Lines & Dividers', ['rainbow_line.gif', 'rainbow_hr.gif', 'line_hearts.gif', 'line_stars.gif',
                                  'line_barbed.gif', 'line_lightning.gif', 'line_paws.gif', 'line_notes.gif',
                                  'line_rope.gif', 'line_laser.gif', 'line_slime.gif', 'line_bows.gif']),
            ('Buttons', ['sign_gb.gif', 'view_gb.gif', 'mailme.gif', 'btn_home.gif', 'btn_next.gif', 'btn_back.gif',
                         'btn_links.gif', 'btn_about.gif', 'btn_enter.gif', 'enter_big.gif', 'join_now.gif']),
            ('Bullets', ['ball_red.gif', 'ball_green.gif', 'ball_blue.gif', 'ball_yellow.gif', 'ball_purple.gif',
                         'ball_pink.gif', 'bullet_star.gif', 'bullet_heart.gif', 'bullet_skull.gif', 'bullet_paw.gif',
                         'bullet_alien.gif', 'bullet_red.gif', 'bullet_blue.gif']),
            ('Awards', ['award_coolweek.gif', 'award_hammer.gif', 'award_galactic.gif', 'award_purrfect.gif',
                        'award_top4.gif', 'award_blue.gif', 'award_spooky.gif', 'award_gold.gif']),
            ('88x31 Buttons', ['best_800.gif', 'notepad.gif', 'y2k_ok.gif', 'y2k_not.gif', 'pioneer_now.gif',
                               'explorer.gif', 'handcoded.gif', 'noframes.gif', 'webring_88.gif', 'html32.gif',
                               'anti_spam.gif', 'stop_ie.gif', 'tinfoil.gif', 'gnulix.gif', 'plushie.gif',
                               'mp_trainer.gif', 'kava_powered.gif', 'webcam_88.gif', 'geohoods_88.gif']),
            ('Photos (for people without scanners)', ['photo_me.gif', 'photo_me2.gif', 'photo_cat.gif', 'photo_dog.gif',
                                                     'photo_family.gif', 'photo_baby.gif', 'photo_house.gif',
                                                     'photo_car.gif', 'photo_beach.gif', 'photo_mountain.gif',
                                                     'photo_band.gif', 'photo_cake.gif', 'photo_food.gif',
                                                     'photo_computer.gif', 'photo_ufo.gif', 'photo_pantry.gif',
                                                     'rainbow_bridge.gif', 'broken.gif'])]
    h = top(root, 'GeoHoods Clip Art')
    h += '<P><FONT FACE="Arial" SIZE=5><B>Clip Art &amp; Animations</B></FONT><BR>%sTo use a picture on your page, ' \
         'copy the HTML under it. Please do not link to these from other web sites!</FONT></P>\n' % FONT
    for cat, items in cats:
        h += '<TABLE WIDTH=600 CELLPADDING=4 CELLSPACING=0>' + bluehead(cat) + '</TABLE>\n<P>'
        for it in items:
            w, hh = SIZES[it]
            sw, sh = (w, hh) if w <= 240 else (240, max(1, hh * 240 // w))
            h += '<TABLE BORDER=0 CELLPADDING=4 ALIGN=LEFT><TR><TD ALIGN=CENTER><IMG SRC="%simages/%s" WIDTH=%d ' \
                 'HEIGHT=%d ALT="%s"><BR><FONT FACE="Arial" SIZE=1><TT>&lt;IMG SRC="../../../images/%s"&gt;</TT>' \
                 '</FONT></TD></TR></TABLE>\n' % (root, it, sw, sh, it, it)
        h += '<BR CLEAR=ALL></P>\n'
    h += bottom(root)
    W(site, 'addons/clipart.html', h)

    h = top(root, 'GeoHoods Backgrounds')
    h += '<P><FONT FACE="Arial" SIZE=5><B>Backgrounds</B></FONT><BR>%sAdd <TT>BACKGROUND="../../../images/name.gif"' \
         '</TT> to your BODY tag. Remember to pick a text color you can read!</FONT></P>\n' % FONT
    h += '<TABLE WIDTH=600 BORDER=1 CELLPADDING=0 CELLSPACING=4>\n'
    for i, b in enumerate(BG_CHOICES):
        if i % 3 == 0:
            h += '<TR>'
        h += '<TD BACKGROUND="%simages/%s" HEIGHT=90 WIDTH=200 VALIGN=BOTTOM><TABLE BGCOLOR="#FFFFFF" CELLPADDING=1>' \
             '<TR><TD><FONT FACE="Arial" SIZE=1>%s</FONT></TD></TR></TABLE></TD>' % (root, b, b)
        if i % 3 == 2:
            h += '</TR>\n'
    h += '</TR></TABLE>\n' + bottom(root)
    W(site, 'addons/backgrounds.html', h)

    h = top(root, 'GeoHoods Counters')
    h += '<P><FONT FACE="Arial" SIZE=5><B>Counters</B></FONT></P>\n<P>%sEvery good homepage needs a counter. ' \
         'Pick a style:</FONT></P>\n' % FONT
    for style, label in [('digit', 'Classic'), ('led', 'Green LED'), ('odo', 'Odometer')]:
        h += '<P>%s<B>%s</B><BR>' % (FONT, label) + ''.join(
            img(root, '%s_%s.gif' % (style, c)) for c in '001999') + '</FONT></P>\n'
    h += ('<P>%sOur <B>JavaScript counter</B> counts up all by itself. Paste this into your page:</FONT></P>\n'
          '<PRE>&lt;SCRIPT LANGUAGE="JavaScript"&gt;\nvar hits = 1000 + Math.floor((new Date().getTime() - '
          'new Date(1999,0,1).getTime()) / 3600000);\nvar s = "" + hits;\nfor (var i = 0; i &lt; s.length; i++)\n'
          '  document.write("&lt;IMG SRC=../../../images/led_" + s.charAt(i) + ".gif&gt;");\n&lt;/SCRIPT&gt;</PRE>\n'
          '<P>%sLive demo: <SCRIPT LANGUAGE="JavaScript">\n<!--\nvar hits = 1000 + Math.floor((new Date().getTime() - '
          'new Date(1999,0,1).getTime()) / 3600000);\nvar s = "" + hits;\nfor (var i = 0; i < s.length; i++)\n'
          '  document.write("<IMG SRC=\\"../images/led_" + s.charAt(i) + ".gif\\" WIDTH=14 HEIGHT=20>");\n// -->\n'
          '</SCRIPT></FONT></P>\n' % (FONT, FONT))
    h += bottom(root)
    W(site, 'addons/counters.html', h)

    h = top(root, 'GeoHoods Guestbooks')
    h += ('<P><FONT FACE="Arial" SIZE=5><B>Guestbooks</B></FONT></P>\n<P>%s%s Every homesteader can have a free '
          'guestbook. Visitors fill in their name, where they are from, how they found you and a comment, and it shows '
          'up on <TT>guestbook.html</TT> in your directory (after our Community Leaders check it for spam).</P>'
          '<P>To add the buttons to your page, paste this:</P><PRE>&lt;A HREF="guestbook.html#sign"&gt;&lt;IMG '
          'SRC="../../../images/sign_gb.gif"&gt;&lt;/A&gt;\n&lt;A HREF="guestbook.html"&gt;&lt;IMG '
          'SRC="../../../images/view_gb.gif"&gt;&lt;/A&gt;</PRE><P>%s %s</P></FONT>\n' % (
              FONT, img(root, 'mailbox.gif'), img(root, 'sign_gb.gif'), img(root, 'view_gb.gif')))
    h += bottom(root)
    W(site, 'addons/guestbooks.html', h)

    h = top(root, 'GeoHoods MIDI Music')
    h += '<P><FONT FACE="Arial" SIZE=5><B>MIDI Music</B></FONT><BR>%sOriginal tunes by the GeoHoods house band. ' \
         'Click to listen. To play one on your page, use <TT>&lt;BGSOUND SRC="../../../midi/name.mid"&gt;</TT> ' \
         '(Explor-o-Matic) and <TT>&lt;EMBED SRC="../../../midi/name.mid" HIDDEN=TRUE&gt;</TT> (Pioneer).</FONT>' \
         '</P>\n<TABLE WIDTH=600 BORDER=1 CELLPADDING=4 CELLSPACING=0>\n' % FONT
    for n, t in sorted(MIDI_TITLES.items(), key=lambda x: x[1]):
        h += '<TR><TD>%s</TD><TD>%s<A HREF="../midi/%s.mid"><B>%s</B></A></FONT></TD><TD>%s<TT>%s.mid</TT></FONT>' \
             '</TD><TD>%s%d bytes</FONT></TD></TR>\n' % (img(root, 'notes.gif').replace('WIDTH=48 HEIGHT=40',
                                                                                       'WIDTH=24 HEIGHT=20'),
                                                        FONT, n, t, FONT, n, FONT,
                                                        os.path.getsize(os.path.join(site, 'midi', n + '.mid')))
    h += '</TABLE>\n' + bottom(root)
    W(site, 'addons/midi.html', h)

    h = top(root, 'GeoHoods Webrings')
    h += '<P><FONT FACE="Arial" SIZE=5><B>Webrings</B></FONT><BR>%sA webring links pages about the same thing into a ' \
         'circle. Click "Next" on one page and you land on the next page in the ring. Here are the rings our ' \
         'homesteaders run:</FONT></P>\n<TABLE WIDTH=600 BORDER=0 CELLPADDING=4>\n' % FONT
    for code in sorted(rings, key=lambda c: rings[c]['name']):
        rg = rings[code]
        h += '<TR BGCOLOR="%s"><TD>%s<B><A HREF="../webrings/%s.html">%s</A></B> (%d sites)<BR>%s</FONT></TD></TR>\n' % (
            rg['color'], FONT, code, rg['name'], len(rg['members']), rg['blurb'])
    h += '</TABLE>\n' + bottom(root)
    W(site, 'addons/webrings.html', h)


def webring_pages(site, rings):
    root = '../'
    h = top(root, 'GeoHoods Webring Directory')
    h += '<P><FONT FACE="Arial" SIZE=5><B>Webring Directory</B></FONT></P>\n<UL>\n'
    for code in sorted(rings, key=lambda c: rings[c]['name']):
        h += '<LI>%s<A HREF="%s.html">%s</A> - %d sites</FONT>\n' % (FONT, code, rings[code]['name'],
                                                                     len(rings[code]['members']))
    h += '</UL>\n' + bottom(root)
    W(site, 'webrings/index.html', h)
    for code, rg in rings.items():
        h = top(root, rg['name'])
        h += ('<CENTER><TABLE BORDER=3 CELLPADDING=10 BGCOLOR="%s"><TR><TD ALIGN=CENTER><FONT FACE="Arial" SIZE=5>'
              '<B>%s</B></FONT><BR>%s%s</FONT></TD></TR></TABLE></CENTER>\n' % (rg['color'], rg['name'], FONT,
                                                                               rg['blurb']))
        h += '<P>%s<B>Sites in this ring</B> (in ring order):</FONT></P>\n<OL>\n' % FONT
        for p in rg['members']:
            h += '<LI>%s<A HREF="../%sindex.html">%s</A> - %s<BR><FONT SIZE=1>%s</FONT></FONT>\n' % (
                FONT, p['addr'], p['title'], p['v_handle'], p['desc'])
        h += '</OL>\n'
        h += ('<A NAME="join"></A><P>%s<B>Join the ring!</B> Have a page about this topic? E-mail the ringmaster, '
              '<A HREF="mailto:%s">%s</A>, with your address. You\'ll get the HTML for the ring navigation bar. '
              'Pages must be family-friendly and actually have content (no "coming soon" pages, sorry).</FONT></P>\n'
              % (FONT, rg['members'][0]['v_email'], rg['members'][0]['v_handle']))
        h += '<P>%s</P>\n' % img(root, 'webring_88.gif')
        h += bottom(root)
        W(site, 'webrings/%s.html' % code, h)


def simple(site, rel, title, body, depth=0):
    root = '../' * depth
    W(site, rel, top(root, title) + '<TABLE WIDTH=600 BORDER=0><TR><TD>%s%s</FONT></TD></TR></TABLE>\n' % (
        FONT, body) + bottom(root))


def misc_pages(site, pages):
    simple(site, 'help.html', 'GeoHoods Help', '''<P><FONT SIZE=5><B>GeoHoods Help</B></FONT></P>
<P><B>What is GeoHoods?</B><BR>GeoHoods is a free home page community. Every homesteader gets a free address in one of our
themed neighborhoods, 11 MB of space and free tools to build a page.</P>
<P><B>How do I get a page?</B><BR>Go to <A HREF="join.html">Join</A>, pick a neighborhood and a vacant address, then use
<A HREF="build.html">Build-a-Page</A>.</P>
<P><B>What does my address mean?</B><BR>An address like <TT>Area52/Hangar/1013/</TT> means neighborhood Area52, suburb Hangar,
house number 1013. Tell your friends: "I live at 1013 Hangar, in Area52!"</P>
<P><B>How do I edit my page later?</B><BR>Log in to the <A HREF="filemanager.html">File Manager</A> and press Edit next to
the file. The EZ Editor shows you the HTML.</P>
<P><B>Why is there a GeoGuide box on my page?</B><BR>The GeoGuide helps visitors find your neighbors, and it keeps GeoHoods
free. Please don't try to hide it with a giant table. We can tell.</P>
<P><B>How do I add a counter / guestbook / music?</B><BR>See <A HREF="addons/index.html">Home Page Add-Ons</A>.</P>
<P><B>My images don't show up!</B><BR>Check the file name. On our servers <TT>Me.GIF</TT> and <TT>me.gif</TT> are... actually
the same, we run on a very forgiving server. Check that you uploaded it, then.</P>
<P><B>Can I have a page about my business?</B><BR>Small hobby businesses are OK (selling your quilts, your band's demo tape).
Please read the <A HREF="guidelines.html">guidelines</A>.</P>
<P><A NAME="password"></A><B>I forgot my password!</B><BR>We will mail you a new one on a floppy disk. Allow 4-6 weeks.
(Or just ask your Community Leader.)</P>
<P><B>Is GeoHoods Y2K compliant?</B><BR>Yes. See <A HREF="news.html">our Y2K statement</A>.</P>
''')
    simple(site, 'guidelines.html', 'GeoHoods Homesteader Agreement', '''<P><FONT SIZE=5><B>Homesteader Agreement</B></FONT></P>
<P>By moving into a GeoHoods neighborhood you agree to be a good neighbor. In plain English:</P>
<OL>
<LI>Your page is yours. You keep the rights to everything you make. We just host it (for free!).
<LI>Be nice. No hateful pages, no harassment, nothing illegal, nothing you would not show your grandmother. (Some of our
grandmothers are homesteaders too.)
<LI>Do not put other people's stuff on your page without permission. That includes pictures, MIDIs and lyrics.
<LI>No chain letters. We mean it. Not even the one about the cookie recipe.
<LI>Keep your page in the right neighborhood. A UFO page in the Kitchen will be gently moved to Area52.
<LI>Update your page at least once every six months, or the lot may be offered to someone else.
<LI>Do not hide or remove the GeoGuide.
<LI>We may change this agreement from time to time. We will put a NEW! GIF next to the changes.
</OL>
<A NAME="content"></A><P><B>Content Guidelines</B></P>
<P>GeoHoods is a family neighborhood. Community Leaders volunteer their time to keep it friendly. If you see a page that
breaks the rules, use the "Report a page" link in the GeoGuide (coming soon) or e-mail your Community Leader.</P>
''')
    simple(site, 'news.html', 'GeoHoods News', '''<P><FONT SIZE=5><B>GeoHoods Press &amp; News</B></FONT></P>
<P><B>October 1999 - GeoHoods Is Y2K Ready</B><BR>Our engineers rolled every server clock forward to December 31, 1999 and
waited. At midnight the counters on three test pages briefly read 000000, and the break room coffee maker started
brewing decaf. Both issues have been fixed. Your home page will be fine.</P>
<P><B>September 1999 - Bunker Becomes Our 15th Neighborhood</B><BR>For homesteaders who are preparing for anything. The
first 50 lots sold out in a week, mostly to people who already had a generator.</P>
<P><B>August 1999 - 11 Megabytes For Everyone</B><BR>Every homesteader now gets 11 MB of space, up from 6. That is enough
for about 400 animated GIFs, which we believe is too many, but who are we to judge.</P>
<P><B>June 1999 - Build-a-Page 2.1</B><BR>Now with ten templates, thirty backgrounds and original MIDI music by the GeoHoods
house band.</P>
<P><B>March 1999 - The Arcade Neighborhood Opens Pocket Suburb</B><BR>Monstropals trainers needed a place to call home.
They now have 7 webpages and 400 trading card scans between them.</P>
''')
    simple(site, 'gbthanks.html', 'Thank You!', '''<P><FONT SIZE=5><B>Thank You!</B></FONT></P>
<P><IMG SRC="images/mailbox.gif" WIDTH=32 HEIGHT=32>
<SCRIPT LANGUAGE="JavaScript">
<!--
var s = location.search.substring(1), nm = "", page = "";
var parts = s.split("&");
for (var i = 0; i < parts.length; i++) {
  var kv = parts[i].split("=");
  if (kv[0] == "name" && kv.length > 1) nm = unescape(kv[1].replace(/\\+/g, " "));
  if (kv[0] == "page" && kv.length > 1) page = unescape(kv[1].replace(/\\+/g, " "));
}
nm = nm.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
if (page.match(/^[A-Za-z0-9]+\\/[A-Za-z0-9]+\\/[0-9]+\\/$/) == null) page = "";
document.write("<B>Thanks for signing" + (nm != "" ? ", " + nm : "") + "!</B> ");
document.write("Your entry has been sent to the homesteader and will appear after it is approved (usually within a day or two).");
if (page != "") document.write("<P><A HREF=\\"" + page + "guestbook.html\\">Back to the guestbook</A></P>");
// -->
</SCRIPT></P>
<P><A HREF="javascript:history.back()">Go back</A> | <A HREF="index.html">GeoHoods home</A></P>
''')
    simple(site, 'adclick.html', 'Congratulations!!!', '''<P><CENTER><FONT SIZE=6 COLOR="#FF0000"><BLINK><B>CONGRATULATIONS!!!</B></BLINK></FONT></CENTER></P>
<P><CENTER><IMG SRC="images/hot.gif" WIDTH=80 HEIGHT=40> <IMG SRC="images/award_top4.gif" WIDTH=100 HEIGHT=100> <IMG SRC="images/hot.gif" WIDTH=80 HEIGHT=40></CENTER></P>
<P>You are the <B>1,000,000th</B> person to click on a banner ad today! Unfortunately, so was everybody else.</P>
<P>There is no prize. There was never a prize. The mosquito cannot be swatted. The VirtuaPup is not real (but it is
still hungry). Thank you for supporting free home pages by clicking on ads, though. Seriously. It keeps the lights on.</P>
<P><A HREF="index.html">Back to GeoHoods</A></P>
''')
    hood_opts = ''.join('<OPTION>%s\n' % hd['key'] for hd in HOODS)
    handles = [p['v_handle'] for p in pages]
    rr = random.Random('chat')
    lines = [
        'hi all', 'anybody here from Ohio?', 'a/s/l?', 'lol', 'brb mom needs the phone', 'is it just me or is the chat '
        'slow tonight', 'who saw Maple Cove last night???', 'my counter just hit 1000!!!', 'how do u make a marquee',
        'use the MARQUEE tag', 'thx!!!', 'anyone want to join my webring?', 'BRB', 'I am back', 'lag...',
        'sign my guestbook pleeeease', 'what neighborhood r u in', 'Area52, Hangar. you?', 'Prairie! kitty page!',
        'cats rule', 'dogs drool lol jk', 'Y2K is in 70 days people', 'my bunker has cable', '*waves*',
        'Community Leader here: keep it friendly folks :)', 'gotta go, bye!!!', 'night all']
    trans = ''
    for ln in lines:
        trans += '<B>&lt;%s&gt;</B> %s<BR>\n' % (rr.choice(handles), ln)
    simple(site, 'chat.html', 'GeoHoods Neighborhood Chat', '''<P><FONT SIZE=5><B>Neighborhood Chat</B></FONT></P>
<FORM NAME="chat">Room: <SELECT NAME="room">%s</SELECT></FORM>
<P><APPLET CODE="GeoChat.class" WIDTH=300 HEIGHT=120><PARAM NAME="server" VALUE="chat.geohoods.com">
<IMG SRC="images/kava_applet.gif" WIDTH=300 HEIGHT=120 ALT="Kava chat applet"></APPLET></P>
<P><I>The Kava chat applet is starting. This can take a minute on a 28.8 modem. While you wait, here is what people
were saying the last time we checked:</I></P>
<TABLE WIDTH="100%%" BORDER=1 CELLPADDING=6 BGCOLOR="#FFFFEE"><TR><TD><FONT FACE="Courier New" SIZE=2>%s</FONT></TD></TR></TABLE>
<P><INPUT TYPE="button" VALUE="Enter Chat" onClick="alert('The chat applet could not start: Kava Virtual Machine not found.\\n\\nPlease upgrade to Pioneer Navigator 4.6 or Internet Explor-o-Matic 5.');"></P>
<SCRIPT LANGUAGE="JavaScript">
<!--
var r = location.search.indexOf("room=");
if (r >= 0) {
  var room = location.search.substring(r + 5);
  for (var i = 0; i < document.forms["chat"].room.options.length; i++)
    if (document.forms["chat"].room.options[i].text == room) document.forms["chat"].room.selectedIndex = i;
}
// -->
</SCRIPT>
''' % (hood_opts, trans))
    W(site, 'images/index.html', '<HTML><HEAD><TITLE>GeoHoods images</TITLE></HEAD><BODY BGCOLOR="#FFFFFF">'
                                 '<P><FONT FACE="Arial" SIZE=2>Looking for clip art? See the '
                                 '<A HREF="../addons/clipart.html">Clip Art</A> page.</FONT></P></BODY></HTML>\n')
    W(site, 'midi/index.html', '<HTML><HEAD><TITLE>GeoHoods MIDI</TITLE></HEAD><BODY BGCOLOR="#FFFFFF">'
                               '<P><FONT FACE="Arial" SIZE=2>Looking for music? See the '
                               '<A HREF="../addons/midi.html">MIDI Music</A> page.</FONT></P></BODY></HTML>\n')
    W(site, 'tools/index.html', '<HTML><HEAD><TITLE>GeoHoods construction yard</TITLE></HEAD><BODY BGCOLOR="#FFFFFF">'
                                '<CENTER><IMG SRC="../images/worker.gif" WIDTH=120 HEIGHT=70><P><FONT FACE="Arial" '
                                'SIZE=2>Authorized GeoHoods staff only. These are the scripts that build the '
                                'neighborhood.<BR><A HREF="../index.html">Back to GeoHoods</A></FONT></P></CENTER>'
                                '</BODY></HTML>\n')


# ====================================================================== entry point
PRAISE = ['A must-see!', 'We laughed, we cried, we signed the guestbook.', 'Turn your speakers up!',
          'Pure homesteading at its finest.', 'Bring sunglasses.', 'This one has EVERYTHING.',
          'Our Community Leaders could not stop clicking.', 'Look at that counter go!', 'Five Golden Shovels.',
          'Proof that the Web is a wonderful place.']


def build(site, pages, rings):
    W.count = 0
    rr = random.Random('portal')
    good = [p for p in pages if len(p['files']) >= 2 and not p['tdef']['features'].get('firstpage')]
    cool = rr.sample(good, 30)
    import datetime
    d0 = datetime.date(1999, 10, 23)
    for i, c in enumerate(cool):
        c['cooldate'] = (d0 - datetime.timedelta(days=i)).strftime('%b %d, %Y').replace(' 0', ' ')
        c['blurb'] = '%s. %s' % (c['desc'].rstrip('.!'), rr.choice(PRAISE))
    featured = rr.sample(good, 4)
    home(site, pages, rings, cool, featured)
    neighborhoods(site, pages)
    for hd in HOODS:
        hp = [p for p in good if p['hood'] == hd['key']]
        hrr = random.Random(hd['key'] + 'lead')
        leaders = hrr.sample(hp, min(2, len(hp)))
        feats = hrr.sample([p for p in hp if p not in leaders] or hp, min(3, len(hp)))
        hood_page(site, hd, pages, leaders, feats)
        for s, d in hd['suburbs']:
            suburb_page(site, hd, s, d, pages)
    ghdata(site, pages)
    search_page(site)
    directory(site, pages)
    cool_page(site, cool)
    join_page(site, pages)
    builder_js(site, pages)
    build_page(site)
    filemanager_page(site)
    addons(site, rings)
    webring_pages(site, rings)
    misc_pages(site, pages)
    return W.count


del STYLES, FIRST_F, FIRST_M, HOOD
