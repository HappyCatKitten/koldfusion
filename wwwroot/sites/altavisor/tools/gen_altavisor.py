#!/usr/bin/env python3
"""Generates AltaVisor's static pages and the invented "rest of the Web" in web/.

    python3 tools/gen_altavisor.py     then     python3 tools/crawl.py

gen_altavisor.py writes index.html, results.html (the JavaScript search engine),
advanced.html, translate.html, addurl.html, help.html, about.html and web/<host>/*.html.
crawl.py then spiders everything on disk and writes the index (av_index.js), the crawler
report (crawl.html), Top Searches (popular.html) and the static results/ pages.
"""
import hashlib, html, os, random, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', '..', 'yowza', 'tools')))
import inventedweb as W  # noqa: E402
import yowza_data as Y  # noqa: E402

SITE = 'altavisor'
RING = [k for k, _, _ in Y.WEB1999]


def esc(s):
    return html.escape(s, quote=True)


def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='latin-1', errors='xmlcharrefreplace') as f:
        f.write(text)


def up(rel):
    return '../' * rel.count('/')


def ring(pre):
    i = RING.index(SITE)
    arr = ','.join("'%s'" % r for r in RING)
    return '''<P><CENTER>
<TABLE BORDER=2 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#C0C0C0"><TR><TD ALIGN=CENTER>
<FONT FACE="Arial, Helvetica" SIZE=1>
<A HREF="%(pre)s../%(prv)s/index.html">&lt;&lt; Prev</A> |
<A HREF="%(pre)s../../web1999/index.html" onClick="var r=new Array(%(arr)s); location.href='%(pre)s../'+r[Math.floor(Math.random()*r.length)]+'/index.html'; return false;">Random</A> |
<B><A HREF="%(pre)s../../web1999/index.html">The 1999 Web Ring</A></B> &middot; AltaVisor is site %(n)d of %(tot)d |
<A HREF="%(pre)s../%(nxt)s/index.html">Next &gt;&gt;</A>
</FONT></TD></TR></TABLE>
</CENTER>
''' % dict(pre=pre, prv=RING[i - 1], nxt=RING[(i + 1) % len(RING)], arr=arr, n=i + 1, tot=len(RING))


def page(title, body, pre, onload='', head=''):
    return '''<HTML>
<HEAD>
<TITLE>%s</TITLE>
%s</HEAD>
<BODY BGCOLOR="#FFFFFF" TEXT="#000000" LINK="#000099" VLINK="#663366" ALINK="#FF0000"%s>
%s
%s</BODY>
</HTML>
''' % (esc(title), head, (' onLoad="%s"' % onload) if onload else '', body, ring(pre))


LANGS = [('XX', 'any language'), ('zh', 'Chinese'), ('cs', 'Czech'), ('da', 'Danish'), ('nl', 'Dutch'), ('en', 'English'),
         ('fi', 'Finnish'), ('fr', 'French'), ('de', 'German'), ('el', 'Greek'), ('it', 'Italian'), ('ja', 'Japanese'),
         ('ko', 'Korean'), ('no', 'Norwegian'), ('xp', 'Pig Latin'), ('pl', 'Polish'), ('pt', 'Portuguese'),
         ('ru', 'Russian'), ('es', 'Spanish'), ('sv', 'Swedish')]


def lang_select():
    return '<SELECT NAME=kl>' + ''.join('<OPTION VALUE=%s%s>%s\n' % (k, ' SELECTED' if k == 'XX' else '', n) for k, n in LANGS) + '</SELECT>'


def small_header(pre, q_js=True):
    """logo + search bar used on every inner page"""
    return '''<TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0 WIDTH=600>
<TR VALIGN=BOTTOM><TD><A HREF="%(pre)sindex.html"><IMG SRC="%(pre)simages/av_logo_sm.gif" WIDTH=300 HEIGHT=38 BORDER=0 ALT="AltaVisor"></A></TD>
<TD ALIGN=RIGHT><FONT SIZE=-1><A HREF="%(pre)shelp.html">Help</A> - <A HREF="%(pre)sadvanced.html">Advanced</A> - <A HREF="%(pre)stranslate.html">Translate</A></FONT></TD></TR>
<TR><TD COLSPAN=2 BGCOLOR="#003399"><IMG SRC="%(pre)simages/pixel.gif" WIDTH=1 HEIGHT=2></TD></TR></TABLE>
<TABLE BORDER=0 BGCOLOR="#FFCC66" WIDTH=600 CELLSPACING=0 CELLPADDING=4><TR><TD>
<FORM NAME=mfrm METHOD=GET ACTION="%(pre)sresults.html"><INPUT TYPE=hidden NAME=pg VALUE=q>
<FONT SIZE=-1><B>Search</B> %(langs)s <B>for</B></FONT><BR>
<INPUT NAME=q SIZE=50 MAXLENGTH=800 VALUE=""> <INPUT TYPE=image SRC="%(pre)simages/av_search.gif" WIDTH=66 HEIGHT=23 BORDER=0 ALT="Search" ALIGN=ABSMIDDLE>
</FORM></TD></TR></TABLE>
<TABLE WIDTH=600 BORDER=0 CELLSPACING=0 CELLPADDING=0><TR><TD BGCOLOR="#003399"><IMG SRC="%(pre)simages/pixel.gif" WIDTH=1 HEIGHT=2></TD></TR></TABLE>
''' % dict(pre=pre, langs=lang_select())


def footer(pre):
    return '''<P><CENTER><TABLE WIDTH=600 BORDER=0 CELLSPACING=0 CELLPADDING=0><TR><TD BGCOLOR="#003399"><IMG SRC="%(pre)simages/pixel.gif" WIDTH=1 HEIGHT=2></TD></TR></TABLE>
<FONT SIZE=-1><A HREF="%(pre)sabout.html">About AltaVisor</A> | <A HREF="%(pre)shelp.html">Help</A> | <A HREF="%(pre)saddurl.html">Add/Remove URL</A> |
<A HREF="%(pre)scrawl.html">Crawler Report</A> | <A HREF="%(pre)spopular.html">Top Searches</A> | <A HREF="%(pre)stranslate.html">Translate</A><BR>
<A HREF="%(pre)sabout.html#legal">Disclaimer</A> | <A HREF="%(pre)sabout.html#privacy">Privacy Policy</A><BR>
Copyright &copy; 1999 AltaVisor Company. All rights reserved.</FONT></CENTER>
''' % dict(pre=pre)


def js_str(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'").replace('</', '<\\/') + "'"


JS_ARGS = r'''function getArg(name) {
  var q = location.search.substring(1).split('&');
  for (var i = 0; i < q.length; i++) {
    var kv = q[i].split('=');
    if (kv[0] == name && kv.length > 1) return unescape(kv[1].replace(/\+/g, ' '));
  }
  return '';
}
function h(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
'''

# ================================================================ invented web
def seeded(host):
    return random.Random(int(hashlib.md5(host.encode()).hexdigest()[:8], 16))


STYLES = ['geo', 'corp', 'fan', 'plain']


def counter(pre, rnd):
    n = '%06d' % rnd.randint(312, 98000)
    return ''.join('<IMG SRC="%simages/digit_%s.gif" WIDTH=15 HEIGHT=20 ALT="%s">' % (pre, d, d) for d in n)


def homepage(site, siblings, rnd, extra_text=None, lang='en'):
    """one invented 1999 homepage; returns dict(name -> html) for index/guestbook/links"""
    host = site['host']
    pre = '../../'           # web/<host>/x.html -> altavisor root
    ysite = '../../../yowza/'  # -> the Yowza! site root
    top = site['cat'].split('/')[0]
    topic = Y.title_of(site['cat']).lower()
    name = site['name']
    style = STYLES[rnd.randint(0, 3)] if lang == 'en' else 'plain'
    if extra_text:
        paras = [extra_text]
    else:
        bank = W.BANKS[top][:]
        rnd.shuffle(bank)
        sents = [b.format(name=name, topic=topic) for b in bank[:4]]
        paras = [site['desc'][0].upper() + site['desc'][1:], ' '.join(sents[:2]), ' '.join(sents[2:])]
    year_upd = '%s %d, 1999' % (rnd.choice(['January', 'March', 'May', 'June', 'August', 'September', 'October']), rnd.randint(1, 28))
    has_gb, has_links = rnd.random() < 0.45, rnd.random() < 0.45
    nav = ['<A HREF="index.html">Home</A>']
    if has_links:
        nav.append('<A HREF="links.html">Cool Links</A>')
    if has_gb:
        nav.append('<A HREF="guestbook.html">Guestbook</A>')
    sib_links = ''.join('<LI><A HREF="../%s/index.html">%s</A>\n' % (s['host'], esc(s['name'])) for s in siblings[:4])
    yz = '<A HREF="%sdir/%s/index.html">Yowza!</A>' % (ysite, site['cat']) if site.get('cat') and not extra_text else '<A HREF="%sindex.html">Yowza!</A>' % ysite
    body_ps = ''.join('<P>%s\n' % esc(p) for p in paras)
    lang_attr = ' LANG="%s"' % lang if lang != 'en' else ''
    if style == 'geo':
        bodytag = '<BODY BACKGROUND="%simages/stars_bg.gif" BGCOLOR="#000000" TEXT="#FFFF00" LINK="#00FFFF" VLINK="#FF99FF">' % pre
        main = '''<CENTER><FONT FACE="Arial" SIZE=6 COLOR="#FF3333"><B>%s</B></FONT><BR>
<IMG SRC="%simages/fire.gif" WIDTH=120 HEIGHT=30><BR>
<MARQUEE WIDTH=400><FONT COLOR="#00FF00">*** Welcome to %s *** Updated %s *** Sign my guestbook! ***</FONT></MARQUEE></CENTER>
<IMG SRC="%simages/rainbow_hr.gif" WIDTH=500 HEIGHT=6><BR>
<FONT FACE="Arial">%s</FONT>
<IMG SRC="%simages/rainbow_hr.gif" WIDTH=500 HEIGHT=6>
''' % (esc(name), pre, esc(name), year_upd, pre, body_ps, pre)
    elif style == 'corp':
        bodytag = '<BODY BGCOLOR="#FFFFFF" TEXT="#000000" LINK="#003366" VLINK="#666666">'
        main = '''<TABLE WIDTH=600 BORDER=0 CELLPADDING=6 CELLSPACING=0>
<TR><TD COLSPAN=2 BGCOLOR="#003366"><FONT FACE="Arial" SIZE=5 COLOR="#FFFFFF"><B>%s</B></FONT></TD></TR>
<TR><TD WIDTH=120 VALIGN=TOP BGCOLOR="#DDEEFF"><FONT FACE="Arial" SIZE=2>%s<BR><BR><IMG SRC="%simages/globe.gif" WIDTH=32 HEIGHT=32></FONT></TD>
<TD VALIGN=TOP><FONT FACE="Arial" SIZE=2>%s</FONT></TD></TR></TABLE>
''' % (esc(name), '<BR>'.join(nav), pre, body_ps)
    elif style == 'fan':
        bodytag = '<BODY BACKGROUND="%simages/bg_tile.gif" BGCOLOR="#FFFFCC" TEXT="#000066">' % pre
        main = '''<CENTER><H1><FONT COLOR="#CC0066">%s</FONT></H1>
<IMG SRC="%simages/new.gif" WIDTH=44 HEIGHT=22> <I>Last updated %s</I><BR>
<IMG SRC="%simages/rainbow_hr.gif" WIDTH=500 HEIGHT=6></CENTER>
%s<CENTER><IMG SRC="%simages/construction.gif" WIDTH=140 HEIGHT=50 ALT="Under Construction"><BR>
<IMG SRC="%simages/netscape_now.gif" WIDTH=88 HEIGHT=31> <FONT SIZE=1>Best viewed with Netscape Navigator at 800x600</FONT></CENTER>
''' % (esc(name), pre, year_upd, pre, body_ps, pre, pre)
    else:
        bodytag = '<BODY BGCOLOR="#C0C0C0" TEXT="#000000">'
        main = '<H1>%s</H1>\n<HR>\n%s<HR>\n<I>Last updated %s</I>\n' % (esc(name), body_ps, year_upd)
    tail = '''<P><CENTER><FONT SIZE=2>%s</FONT></CENTER>
<P><CENTER><FONT SIZE=2>You are visitor number</FONT><BR>%s</CENTER>
<P><CENTER><FONT SIZE=2>Found us on %s? Tell a friend! &middot; <A HREF="mailto:webmaster@%s"><IMG SRC="%simages/email.gif" WIDTH=40 HEIGHT=30 BORDER=0 ALIGN=ABSMIDDLE> Email the webmaster</A></FONT></CENTER>
''' % (' | '.join(nav), counter(pre, rnd), yz, host, pre)
    if sib_links and not extra_text:
        tail = '<P><B>Other great sites about %s:</B><UL>\n%s</UL>\n' % (esc(topic), sib_links) + tail
    pages = {'index.html': '<HTML%s>\n<HEAD><TITLE>%s</TITLE></HEAD>\n%s\n%s%s</BODY>\n</HTML>\n' % (
        lang_attr, esc(name), bodytag, main, tail)}
    if has_gb:
        entries = rnd.sample(W.GUESTBOOK, 5)
        rows = ''.join('<P><B>%s</B> wrote on %s/%d/99:<BR><I>%s</I>\n<HR WIDTH=200 ALIGN=LEFT>\n' % (
            esc(n), rnd.randint(1, 10), rnd.randint(1, 28), esc(t)) for n, t in entries)
        pages['guestbook.html'] = '''<HTML><HEAD><TITLE>%s - Guestbook</TITLE></HEAD>
%s
<H2>%s Guestbook</H2>
<P>Thanks for visiting %s! Here is what people are saying. (The sign-in form is broken again. Email me instead.)
<HR>
%s<P><A HREF="index.html">Back to %s</A>
</BODY></HTML>
''' % (esc(name), bodytag, esc(name), esc(name), rows, esc(name))
    if has_links:
        web = '<LI><A HREF="../../../%s/index.html">%s</A> - %s\n'
        picks = rnd.sample(Y.WEB1999, 3)
        pages['links.html'] = '''<HTML><HEAD><TITLE>%s - Cool Links</TITLE></HEAD>
%s
<H2>My Favorite Links</H2>
<P>These are the sites I visit every day. If you want to trade links, email me!
<UL>
%s%s<LI><A HREF="../../index.html">AltaVisor</A> - the best search engine, period
</UL>
<P><IMG SRC="%simages/webring.gif" WIDTH=300 HEIGHT=40 ALT="Webring">
<P><A HREF="index.html">Back to %s</A>
</BODY></HTML>
''' % (esc(name), bodytag, sib_links, ''.join(web % (k, esc(t), esc(b)) for k, t, b in picks), pre, esc(name))
    return pages


def invented_web():
    shutil.rmtree(os.path.join(ROOT, 'web'), ignore_errors=True)
    sites = Y.invented_sites()
    bycat = {}
    for s in sites:
        bycat.setdefault(s['cat'], []).append(s)
    n = 0
    for s in sites:
        rnd = seeded(s['host'])
        sibs = [x for x in bycat[s['cat']] if x['host'] != s['host']]
        for fname, text in homepage(s, sibs, rnd).items():
            write('web/%s/%s' % (s['host'], fname), text)
            n += 1
    for host, title, lang, text in W.EXTRA_PAGES:
        rnd = seeded(host)
        s = {'host': host, 'name': title, 'cat': 'Society_and_Culture/People/Personal_Home_Pages', 'desc': text}
        for fname, t in homepage(s, [], rnd, extra_text=text, lang=lang).items():
            write('web/%s/%s' % (host, fname), t)
            n += 1
    return n


# ================================================================ home page
EXAMPLES = ['Where can I find pictures of hamsters?', 'How do I get ready for Y2K?', 'Where can I download free screen savers?',
            'What is the best bean bag animal to collect?', 'Where can I learn HTML?', 'How do I build a paper airplane?',
            'Who won the soccer championship?', 'Where can I buy books online?']


def home_page():
    cats = [('Arts_and_Humanities', 'Arts&nbsp;&amp;&nbsp;Humanities'), ('Business_and_Economy', 'Business&nbsp;&amp;&nbsp;Finance'),
            ('Computers_and_Internet', 'Computers&nbsp;&amp;&nbsp;Internet'), ('Health', 'Health&nbsp;&amp;&nbsp;Fitness'),
            ('Recreation_and_Sports/Hobbies', 'Hobbies&nbsp;&amp;&nbsp;Interests'), ('Society_and_Culture', 'Home&nbsp;&amp;&nbsp;Family'),
            ('Entertainment', 'Media&nbsp;&amp;&nbsp;Amusements'), ('Society_and_Culture/People', 'People&nbsp;&amp;&nbsp;Chat'),
            ('Reference', 'Reference&nbsp;&amp;&nbsp;Education'), ('Business_and_Economy/Shopping_and_Services', 'Shopping&nbsp;&amp;&nbsp;Services'),
            ('Government', 'Society&nbsp;&amp;&nbsp;Politics'), ('Recreation_and_Sports/Sports', 'Sports&nbsp;&amp;&nbsp;Recreation'),
            ('Recreation_and_Sports/Travel', 'Travel&nbsp;&amp;&nbsp;Vacations')]
    sp = '<IMG SRC="images/pixel.gif" HEIGHT=7 WIDTH=1><BR>'
    catlinks = sp.join('<A HREF="../yowza/dir/%s/index.html">%s</A><BR>\n' % (p, t) for p, t in cats)
    bar = '<TABLE WIDTH="100%%" CELLPADDING=0 BGCOLOR="#FFCC66" CELLSPACING=0 BORDER=0><TR><TD><IMG SRC="images/pixel.gif" HEIGHT=3 WIDTH=1></TD></TR></TABLE>'
    dart = '<IMG SRC="images/dart.gif" WIDTH=8 HEIGHT=9 BORDER=0> '
    ex = ','.join(js_str(e) for e in EXAMPLES)
    body = '''<CENTER><TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0>
<TR VALIGN=BOTTOM><TD><A HREF="index.html"><IMG SRC="images/av_logo.gif" ALT="AltaVisor" BORDER=0 HEIGHT=60 WIDTH=480></A></TD>
<TD WIDTH=120 HEIGHT=60><A HREF="translate.html"><IMG SRC="images/sponsor_parrot.gif" ALT="Translate with Parrot" WIDTH=120 HEIGHT=60 BORDER=0></A></TD></TR>
<TR><TD COLSPAN=2 BGCOLOR="#003399"><IMG SRC="images/pixel.gif" WIDTH=1 HEIGHT=2 BORDER=0></TD></TR>
</TABLE>
<TABLE BORDER=0 BGCOLOR="#FFCC66" WIDTH=600 CELLSPACING=0 CELLPADDING=4><TR>
<TD WIDTH=5><BR></TD>
<TD><TABLE WIDTH="100%%" BORDER=0 BGCOLOR="#FFCC66" CELLSPACING=0 CELLPADDING=2>
<FORM NAME=mfrm METHOD=GET ACTION="results.html">
<INPUT TYPE=hidden NAME=pg VALUE=q>
<TR><TD VALIGN=TOP><TABLE CELLSPACING=0 CELLPADDING=0 WIDTH="100%%" BORDER=0><TR><TD ALIGN=LEFT><FONT SIZE=-1><B>Ask AltaVisor<SUP><SMALL>TM</SMALL></SUP> a question.</B>&nbsp;&nbsp;Or enter a few words in
%(langs)s</FONT></TD><TD ALIGN=RIGHT><FONT SIZE=-1><A HREF="help.html">Help</A> - <A HREF="advanced.html">Advanced</A></FONT></TD></TR></TABLE></TD></TR>
<TR><TD><FONT SIZE=-1><B>Search For:</B>&nbsp;&nbsp;<FONT SIZE=-2><INPUT TYPE=radio NAME=stype VALUE=stext CHECKED>Web Pages&nbsp;&nbsp;&nbsp;<INPUT TYPE=radio NAME=stype VALUE=simage>Images&nbsp;&nbsp;&nbsp;<INPUT TYPE=radio NAME=stype VALUE=svideo>Video&nbsp;&nbsp;&nbsp;<INPUT TYPE=radio NAME=stype VALUE=saudio>Audio</FONT></FONT></TD></TR>
<TR><TD><INPUT NAME=q SIZE=50 MAXLENGTH=800 VALUE=""> <INPUT TYPE=image SRC="images/av_search.gif" WIDTH=66 HEIGHT=23 BORDER=0 ALT="Search" ALIGN=ABSMIDDLE></TD></TR>
<TR><TD>
<SCRIPT LANGUAGE="JavaScript">
<!--
var ex = new Array(%(ex)s);
document.write('<FONT FACE=arial,helvetica SIZE=-1>Example: <B>' + ex[Math.floor(Math.random() * ex.length)] + '</B></FONT><BR>');
// -->
</SCRIPT>
<NOSCRIPT><FONT FACE=arial,helvetica SIZE=-1>Example: <B>Where can I find pictures of hamsters?</B></FONT><BR></NOSCRIPT>
</TD></TR>
</FORM>
</TABLE></TD></TR></TABLE>
<TABLE WIDTH=600 BORDER=0 CELLSPACING=0 CELLPADDING=0>
<TR><TD COLSPAN=2 BGCOLOR="#003399"><IMG SRC="images/pixel.gif" BORDER=0 WIDTH=1 HEIGHT=2></TD></TR>
</TABLE>
<TABLE WIDTH=600 CELLPADDING=0 CELLSPACING=0 BORDER=0>
<TR><TD><IMG SRC="images/pixel.gif" WIDTH=1 HEIGHT=5 BORDER=0></TD></TR>
<TR><TD ALIGN=CENTER><TABLE CELLPADDING=0 CELLSPACING=0 BORDER=0>
<TR><TD ALIGN=LEFT VALIGN=MIDDLE><FONT FACE=arial,helvetica COLOR="#003399"><B>Specialty<BR>Searches</B></FONT></TD>
<TD WIDTH=40><BR></TD>
<TD ALIGN=LEFT VALIGN=MIDDLE><FONT SIZE=-1 FACE="arial,Helvetica">
<A HREF="results.html?stype=simage&amp;q=hamster"><B>AV Picture Finder</B></A> -
<A HREF="results.html?stype=saudio&amp;q=midi"><B>AV Sound Finder</B></A> -
<A HREF="translate.html">Parrot Translations</A>
<BR><A HREF="../orinoco/index.html">Online Shopping</A> -
<A HREF="../yowza/dir/Business_and_Economy/Finance_and_Investment/index.html">AV Finance</A> -
<A HREF="../yowza/dir/Health/index.html">Health</A> -
<A HREF="../yowza/dir/Business_and_Economy/Employment_and_Work/index.html">Careers</A>
<BR><A HREF="../yowza/dir/Reference/Maps/index.html">Maps</A> -
<A HREF="../yowza/dir/Reference/Phone_Numbers_and_Addresses/index.html">People Finder</A> -
<A HREF="../yowza/dir/Recreation_and_Sports/Travel/index.html">Travel</A> -
<A HREF="../dashdot/index.html">Discussion Groups</A> -
<A HREF="../yowza/dir/Entertainment/index.html">Entertainment</A>
</FONT></TD></TR></TABLE></TD></TR>
<TR><TD BGCOLOR=WHITE><IMG SRC="images/pixel.gif" WIDTH=1 HEIGHT=5 BORDER=0></TD></TR>
<TR><TD BGCOLOR="#003399"><IMG SRC="images/pixel.gif" WIDTH=1 HEIGHT=2 BORDER=0></TD></TR>
</TABLE>
<BR><TABLE WIDTH=600 BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR><TD WIDTH=175 VALIGN=TOP><FONT FACE="arial,helvetica" SIZE=-1><FONT SIZE=+1>C</FONT><B>ATEGORIES</B><BR>
%(bar)s
<TABLE CELLPADDING=0 CELLSPACING=0 BORDER=0><TR><TD WIDTH=8><BR></TD><TD ALIGN=LEFT VALIGN=TOP><FONT FACE="arial,helvetica" SIZE=-1><B>
%(catlinks)s</B><FONT SIZE=-2>directory by <A HREF="../yowza/index.html">Yowza!</A></FONT></FONT></TD></TR></TABLE></FONT></TD>
<TD WIDTH=17><BR></TD>
<TD WIDTH=265 VALIGN=TOP><FONT FACE="arial,helvetica" SIZE=-1><FONT SIZE=+1>N</FONT><B>EWS BY <FONT COLOR="#CC0000">CNM</FONT></B><BR>
%(bar)s
%(dart)s<A HREF="../cnm/index.html">Banks Vow Y2K Readiness</A><BR>
%(dart)s<A HREF="../cnm/index.html">Mars Probe Lost Over Units Mixup</A><BR>
%(dart)s<A HREF="../cnm/index.html">Dot-Com Stocks Soar Again</A><BR>
%(dart)s<A HREF="../dashdot/index.html">Nerds Weigh In, At Length</A><BR>
<BR>
<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH="100%%"><TR><TD ALIGN=RIGHT><FONT FACE="arial,helvetica" SIZE=-1><FONT SIZE=+1>A</FONT><B>LTA</B><FONT SIZE=+1>V</FONT><B>ISOR</B> <FONT SIZE=+1>H</FONT><B>IGHLIGHTS</B></FONT></TD></TR></TABLE>
%(bar)s
<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD WIDTH=8><BR></TD>
<TD><FONT FACE="arial,helvetica" SIZE=-1>%(dart)s<A HREF="crawl.html">Meet Skeeter, Our Web Spider</A><BR>
%(dart)s<A HREF="popular.html">This Week's Top Searches</A><BR>
%(dart)s<A HREF="translate.html"><FONT COLOR="#CC0000">New</FONT> Parrot Translates Any Page</A><BR>
%(dart)s<A HREF="results.html?stype=simage&amp;q=logo">Try the AV Picture Finder</A><BR>
</FONT></TD></TR></TABLE>
<BR><FONT SIZE=+1>O</FONT><B>THER</B> <FONT SIZE=+1>S</FONT><B>ERVICES</B><BR>
%(bar)s
<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD WIDTH=8><BR></TD>
<TD><FONT FACE="arial,helvetica" SIZE=-1><A HREF="addurl.html"><B><FONT COLOR="#CC0000">Add</FONT> Your Page</B></A> - <A HREF="../yowza/mail.html">Email</A><BR>
<A HREF="../askreeves/index.html">Ask&nbsp;the&nbsp;Butler</A> - <A HREF="../geohoods/index.html">Free&nbsp;Home&nbsp;Pages</A><BR>
<A HREF="#" onClick="alert('To make AltaVisor your home page: choose Preferences from the Edit menu, click Navigator, and type this address in the Home Page box. We will wait.'); return false;">Make&nbsp;Us&nbsp;Your&nbsp;Homepage</A>
</FONT></TD></TR></TABLE>
</FONT></TD>
<TD WIDTH=18><BR></TD>
<TD WIDTH=125 VALIGN=TOP><FONT FACE="arial,helvetica" SIZE=-1 COLOR=gray>
<CENTER><IMG SRC="images/skeeter.gif" WIDTH=64 HEIGHT=64 ALT="Skeeter"><BR><FONT SIZE=-2>Skeeter has read<BR><B>%(npages)s</B> pages</FONT></CENTER>
<BR><B>Featured&nbsp;Sponsors</B><BR>
<TABLE WIDTH="100%%" CELLPADDING=0 BGCOLOR="#CCCCCC" CELLSPACING=0 BORDER=0><TR><TD><IMG SRC="images/pixel.gif" HEIGHT=3 WIDTH=1></TD></TR></TABLE>
<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD WIDTH=8><BR></TD>
<TD><FONT FACE="arial,helvetica" SIZE=-1>
<A HREF="../orinoco/index.html">Orinoco.com - Books by the riverful</A><BR><BR>
<A HREF="../ubid/index.html">uBid - Bid on a lava lamp</A><BR><BR>
<A HREF="../petz/index.html">Petz.com - Kibble at a loss</A><BR><BR>
<A HREF="../snapster/index.html">Snapster - Share some tunes</A>
</FONT></TD></TR></TABLE></FONT></TD></TR></TABLE>
</CENTER>
''' % dict(langs=lang_select(), ex=ex, bar=bar, catlinks=catlinks, dart=dart, npages=npages_text())
    write('index.html', page('AltaVisor - Smart is Beautiful', body + footer(''), ''))


def npages_text():
    p = os.path.join(ROOT, 'av_index.js')
    if os.path.exists(p):
        with open(p, encoding='latin-1') as f:
            for line in f:
                if line.startswith('var NPAGES'):
                    return '{:,}'.format(int(line.split('=')[1].strip(' ;\n')))
    return 'thousands of'


# ================================================================ results (the search engine itself)
ENGINE_JS = r'''<SCRIPT LANGUAGE="JavaScript" SRC="av_index.js"></SCRIPT>
<SCRIPT LANGUAGE="JavaScript">
<!--
''' + JS_ARGS + r'''
var STOP = ' a an and are as at be by can could do does for from get how i in into is it me my of on or our please some tell that the there this to was what when where which who why will with would you your find information info about ';
var QWORDS = /^(who|what|where|when|why|how|which|can|could|is|are|do|does|did|should|will)\b/i;
var MONTHS = new Array('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec');
function norm(s) { return ' ' + s.toLowerCase().replace(/[^a-z0-9'\*]+/g, ' ') + ' '; }
function hasWord(hay, w) {
  if (w.charAt(w.length - 1) == '*') return hay.indexOf(' ' + w.substring(0, w.length - 1)) >= 0;
  return hay.indexOf(' ' + w + ' ') >= 0 || hay.indexOf(' ' + w + 's ') >= 0 || (w.length > 3 && w.charAt(w.length - 1) == 's' && hay.indexOf(' ' + w.substring(0, w.length - 1) + ' ') >= 0);
}
function Term(w, req, neg, field) { this.w = w; this.req = req; this.neg = neg; this.field = field; }
// simple query: words, +required, -excluded, "phrases", host: title: url: fields, wildcards*
function parseSimple(q, natural) {
  var t = new Array(), re = /([+\-]?)(host:|domain:|title:|url:)?("([^"]*)"|[^\s"]+)/gi, m;
  while ((m = re.exec(q)) != null) {
    var sign = m[1], field = (m[2] || '').toLowerCase().replace('domain:', 'host:'), text = m[4] != null && m[4] != '' ? m[4] : m[3];
    if (field == 'host:') { t[t.length] = new Term(text.toLowerCase(), sign != '-', sign == '-', 'host'); continue; }
    var phrase = m[4] != null && m[4] != '';
    var ws = norm(text).split(' ');
    for (var i = 0; i < ws.length; i++) {
      var w = ws[i];
      if (w == '' || (natural && STOP.indexOf(' ' + w + ' ') >= 0 && !phrase && sign == '')) continue;
      t[t.length] = new Term(w, sign == '+' || phrase || field != '', sign == '-', field.replace(':', ''));
    }
  }
  return t;
}
// advanced query: a AND b, a OR b, AND NOT, NEAR (treated as AND); groups separated by OR
function parseBool(q) {
  var groups = q.split(/\s+OR\s+/), out = new Array();
  for (var g = 0; g < groups.length; g++) {
    var toks = groups[g].replace(/[()]/g, ' ').split(/\s+/), t = new Array(), neg = false;
    for (var i = 0; i < toks.length; i++) {
      var k = toks[i];
      if (k == '' || k == 'AND' || k == 'NEAR' || k == 'and' || k == 'near') continue;
      if (k == 'NOT' || k == 'not') { neg = true; continue; }
      var ws = norm(k).split(' ');
      for (var j = 0; j < ws.length; j++) if (ws[j] != '') t[t.length] = new Term(ws[j], !neg, neg, '');
      neg = false;
    }
    out[out.length] = t;
  }
  return out;
}
function Doc(s, i) {
  var f = s.split('|');
  this.i = i; this.url = f[0]; this.disp = f[1]; this.title = f[2]; this.sum = f[3]; this.words = ' ' + f[4] + ' ';
  this.kb = f[5]; this.date = f[6]; this.lang = f[7]; this.imgs = f[8]; this.media = f[9];
  this.host = this.disp.split('/')[0];
  this.tn = norm(this.title); this.un = norm(this.disp);
}
var DF = new Object();
function idf(w) {
  if (DF[w] == null) {
    var n = 0;
    for (var j = 0; j < D.length; j++) { var f = D[j].split('|'); if (hasWord(' ' + f[4] + ' ', w) || hasWord(norm(f[2]), w)) n++; }
    DF[w] = n;
  }
  return Math.log((D.length + 1) / (DF[w] + 1)) + 0.5;
}
function scoreDoc(d, terms) {
  var score = 0, matched = 0, pos = 0, sumIdf = 0;
  for (var i = 0; i < terms.length; i++) {
    var t = terms[i], hit;
    if (t.field == 'host') hit = d.host.indexOf(t.w) >= 0;
    else if (t.field == 'title') hit = hasWord(d.tn, t.w);
    else if (t.field == 'url') hit = hasWord(d.un, t.w) || d.disp.toLowerCase().indexOf(t.w) >= 0;
    else {
      var inT = hasWord(d.tn, t.w), inW = hasWord(d.words, t.w), inU = hasWord(d.un, t.w);
      hit = inT || inW || inU;
      if (!t.neg) { var wt = idf(t.w); sumIdf += wt; score += wt * ((inT ? 15 : 0) + (inW ? 4 : 0) + (inU ? 3 : 0)); }
    }
    if (t.neg) { if (hit) return -1; continue; }
    pos++;
    if (hit) matched++; else if (t.req) return -1;
    if (hit && t.field != '') score += 5;
  }
  if (pos == 0) return terms.length > 0 ? 1 : -1;
  if (matched == 0) return -1;
  if (matched == pos) score += 3 * sumIdf + 5;
  if (d.url.indexOf('index.html') == d.url.length - 10) score += 2;
  return score;
}
function fmtDate(s) { return s.substring(6, 8) + '-' + MONTHS[parseInt(s.substring(4, 6), 10) - 1] + '-' + s.substring(2, 4); }
function bold(text, terms) {
  var out = h(text);
  for (var i = 0; i < terms.length; i++) {
    var w = terms[i].w.replace(/\*$/, '');
    if (terms[i].neg || terms[i].field == 'host' || w.length < 2) continue;
    out = out.replace(new RegExp('(^|[^a-zA-Z0-9])(' + w.replace(/[^a-z0-9]/g, '.') + '[a-z]*)', 'gi'), '$1<B>$2</B>');
  }
  return out;
}

var q = getArg('q'), kl = getArg('kl') || 'XX', stype = getArg('stype') || 'stext', pg = getArg('pg') || 'q';
var stq = parseInt(getArg('stq')) || 0, d0 = getArg('d0'), d1 = getArg('d1'), rk = getArg('r');
var natural = pg != 'aq' && (QWORDS.test(q) || /\?\s*$/.test(q));
var groups = pg == 'aq' ? parseBool(q) : new Array(parseSimple(q, natural));
var rterms = rk != '' ? parseSimple(rk, false) : new Array();
var allTerms = new Array();
for (var g = 0; g < groups.length; g++) allTerms = allTerms.concat(groups[g]);
function cvtDate(s) { var p = s.split(/[\/\-]/); if (p.length != 3) return ''; var y = parseInt(p[2], 10); if (y < 100) y += 1900; return '' + y + (p[1].length < 2 ? '0' : '') + p[1] + (p[0].length < 2 ? '0' : '') + p[0]; }
var D0 = d0 != '' ? cvtDate(d0) : '', D1 = d1 != '' ? cvtDate(d1) : '';
var hits = new Array(), searched = 0;
if (allTerms.length > 0) {
  for (var i = 0; i < D.length; i++) {
    var d = new Doc(D[i], i);
    searched++;
    if (kl != 'XX' && d.lang != kl) continue;
    if (D0 != '' && d.date < D0) continue;
    if (D1 != '' && d.date > D1) continue;
    var best = -1;
    for (var g = 0; g < groups.length; g++) { var s = scoreDoc(d, groups[g]); if (s > best) best = s; }
    if (best < 0) continue;
    if (rterms.length > 0) { var rs = scoreDoc(d, rterms); if (rs > 0) best += rs * 3; }
    d.score = best;
    hits[hits.length] = d;
  }
  hits.sort(function (a, b) { return b.score != a.score ? b.score - a.score : (a.url < b.url ? -1 : 1); });
}
function wordCounts() {
  var out = '', seen = ' ';
  for (var i = 0; i < allTerms.length; i++) {
    var t = allTerms[i];
    if (t.field != '' || seen.indexOf(' ' + t.w + ' ') >= 0) continue;
    seen += t.w + ' ';
    idf(t.w);
    out += (out == '' ? '' : ', ') + h(t.w) + ':' + DF[t.w];
  }
  return out;
}
function link(start) {
  return 'results.html?pg=' + pg + '&stype=' + stype + '&kl=' + kl + '&q=' + escape(q) + (rk != '' ? '&r=' + escape(rk) : '') + (d0 != '' ? '&d0=' + escape(d0) : '') + (d1 != '' ? '&d1=' + escape(d1) : '') + '&stq=' + start;
}
function pager(total, per) {
  if (total <= per) return '';
  var cur = Math.floor(stq / per), last = Math.ceil(total / per) - 1, out = '<P><FONT FACE=arial SIZE=-1><B>Result Pages:</B> ';
  if (cur > 0) out += '<A HREF="' + link((cur - 1) * per) + '">[&lt;&lt; Prev]</A> ';
  var from = Math.max(0, cur - 9), to = Math.min(last, from + 19);
  for (var p = from; p <= to; p++) out += (p == cur ? '<B>' + (p + 1) + '</B> ' : '<A HREF="' + link(p * per) + '">' + (p + 1) + '</A> ');
  if (cur < last) out += '<A HREF="' + link((cur + 1) * per) + '">[Next &gt;&gt;]</A>';
  return out + '</FONT>';
}
// -->
</SCRIPT>
'''

RESULTS_BODY = r'''<SCRIPT LANGUAGE="JavaScript">
<!--
document.mfrm.q.value = q;
for (var i = 0; i < document.mfrm.kl.options.length; i++) if (document.mfrm.kl.options[i].value == kl) document.mfrm.kl.selectedIndex = i;
var per = 10;
if (allTerms.length == 0) {
  document.write('<P><FONT FACE=arial>Type a few words or a question in the box above, then press <B>Search</B>. AltaVisor will look through all ' + NPAGES + ' pages its spider has read.</FONT>');
} else if (stype == 'simage') {
  var seen = ' ', imgs = new Array();
  for (var i = 0; i < hits.length && imgs.length < 60; i++) {
    if (hits[i].imgs == '') continue;
    var li = hits[i].imgs.split(';');
    for (var j = 0; j < li.length; j++) { var f = li[j].split('~'); if (seen.indexOf(' ' + f[0] + ' ') >= 0) continue; seen += f[0] + ' '; imgs[imgs.length] = new Array(f[0], f[1], f[2], f[3], hits[i]); }
  }
  document.write('<P><FONT FACE=arial SIZE=-1><B>AV Picture Finder found ' + imgs.length + ' pictures</B> on pages about <B>' + h(q) + '</B>.</FONT><P><TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 WIDTH=600><TR>');
  for (var i = 0; i < imgs.length; i++) {
    var w = parseInt(imgs[i][2]) || 60, ht = parseInt(imgs[i][3]) || 60, sc = Math.min(1, 120 / w, 90 / ht);
    if (i > 0 && i % 4 == 0) document.write('</TR><TR>');
    document.write('<TD ALIGN=CENTER VALIGN=BOTTOM WIDTH=150><A HREF="' + imgs[i][4].url + '"><IMG SRC="' + imgs[i][0] + '" WIDTH=' + Math.round(w * sc) + ' HEIGHT=' + Math.round(ht * sc) + ' BORDER=1 ALT="' + h(imgs[i][1]) + '"></A><BR><FONT SIZE=-2>' + h(imgs[i][1] != '' ? imgs[i][1] : imgs[i][0].split('/').pop()) + '<BR><FONT COLOR="#808080">' + h(imgs[i][4].host) + '</FONT></FONT></TD>');
  }
  document.write('</TR></TABLE>');
  if (imgs.length == 0) document.write('<P>No pictures found. Try <A HREF="results.html?stype=simage&q=hamster">hamster</A>, <A HREF="results.html?stype=simage&q=logo">logo</A> or <A HREF="results.html?stype=simage&q=new">new</A>.');
} else if (stype == 'saudio' || stype == 'svideo') {
  var exts = stype == 'saudio' ? ' mid midi wav mp3 au ra aif ' : ' mpg mpeg mov avi qt rm ', n = 0;
  document.write('<P><FONT FACE=arial SIZE=-1><B>AV ' + (stype == 'saudio' ? 'Sound' : 'Video') + ' Finder</B></FONT><UL>');
  var all = q.toLowerCase().indexOf('mid') >= 0 || q.toLowerCase().indexOf('sound') >= 0 || q.toLowerCase().indexOf('music') >= 0;
  var pool = all ? D : null;
  var list = new Array();
  if (pool) { for (var i = 0; i < D.length; i++) list[list.length] = new Doc(D[i], i); } else list = hits;
  for (var i = 0; i < list.length && n < 50; i++) {
    if (list[i].media == '') continue;
    var li = list[i].media.split(';');
    for (var j = 0; j < li.length; j++) {
      var f = li[j].split('~'), ext = f[0].split('.').pop().toLowerCase();
      if (exts.indexOf(' ' + ext + ' ') < 0) continue;
      document.write('<LI><A HREF="' + f[0] + '">' + h(f[1] != '' ? f[1] : f[0].split('/').pop()) + '</A> <FONT SIZE=-1>(' + ext.toUpperCase() + ') on <A HREF="' + list[i].url + '">' + h(list[i].title) + '</A></FONT>');
      n++;
    }
  }
  document.write('</UL>');
  if (n == 0) document.write('<P>No ' + (stype == 'saudio' ? 'sound clips' : 'video clips') + ' found for <B>' + h(q) + '</B>.' + (stype == 'svideo' ? ' Video on the Web is still mostly a 40-second postage stamp that takes an hour to download. Try again in 2005.' : ' Try searching for <A HREF="results.html?stype=saudio&q=midi">midi</A>.'));
} else {
  document.write('<P><TABLE WIDTH=600 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD><FONT FACE=arial SIZE=-1>');
  if (natural) document.write('<TABLE WIDTH="100%" BGCOLOR="#FFFFCC" BORDER=0 CELLPADDING=4><TR><TD><FONT FACE=arial SIZE=-1><B>AltaVisor knows someone who can answer that.</B> Ask our friend the butler: <A HREF="../askreeves/answer.html?ask=' + escape(q) + '">' + h(q) + '</A></FONT></TD></TR></TABLE><P>');
  document.write('<B>AltaVisor found ' + hits.length + ' Web page' + (hits.length == 1 ? '' : 's') + ' for you.</B>');
  if (hits.length > 0) document.write(' <A HREF="advanced.html?q=' + escape(q) + '">Refine your search</A>');
  document.write('<BR><FONT COLOR="#808080">Word count: ' + wordCounts() + '</FONT>');
  if (kl != 'XX') document.write(' &middot; <FONT COLOR="#808080">only pages in ' + h(document.mfrm.kl.options[document.mfrm.kl.selectedIndex].text) + '</FONT>');
  document.write('</FONT></TD></TR></TABLE><P>');
  if (hits.length == 0) {
    document.write('<FONT FACE=arial SIZE=-1>No documents match the query. Some suggestions:<UL><LI>Check the spelling of your words.<LI>Use fewer words, or remove the + and - signs.<LI>Choose <B>any language</B> from the menu.<LI>Browse the <A HREF="../yowza/search.html?p=' + escape(q) + '">Yowza! directory</A> instead.<LI>Ask <A HREF="../askreeves/answer.html?ask=' + escape(q) + '">Reeves</A>, who has never once admitted defeat.</UL></FONT>');
  }
  document.write('<DL>');
  for (var i = stq; i < Math.min(hits.length, stq + per); i++) {
    var d = hits[i];
    document.write('<DT><B>' + (i + 1) + '. <A HREF="' + d.url + '">' + h(d.title) + '</A></B>');
    document.write('<DD><FONT SIZE=-1>' + bold(d.sum, allTerms) + (d.sum.length >= 195 ? '...' : '') + '<BR>');
    document.write('<FONT COLOR="#808080">URL: ' + h(d.disp) + '</FONT><BR>');
    document.write('<FONT COLOR="#808080">Last modified ' + fmtDate(d.date) + ' - page size ' + d.kb + 'K - in ' + LANGS[d.lang] + '</FONT> [ <A HREF="translate.html?u=' + escape(d.url) + '">Translate</A> ]<BR>');
    document.write('<A HREF="results.html?q=host:' + escape(d.host) + '">More pages from this site</A></FONT><P>');
  }
  document.write('</DL>' + pager(hits.length, per));
}
// -->
</SCRIPT>
<NOSCRIPT><P><B>AltaVisor's search engine runs in your browser and needs JavaScript.</B>
Until you switch it on, try one of <A HREF="popular.html">this week's top searches</A>.</NOSCRIPT>
'''


def results_page():
    body = small_header('') + RESULTS_BODY + '''<P><TABLE WIDTH=600 BORDER=0 CELLPADDING=4><TR><TD BGCOLOR="#FFCC66"><FONT SIZE=-1 FACE=arial>
<B>Also try:</B> <A HREF="javascript:location.href='../yowza/search.html?p='+escape(q)">Yowza! directory</A> -
<A HREF="javascript:location.href='../askreeves/answer.html?ask='+escape(q)">Ask Reeves</A> -
<A HREF="javascript:location.href='results.html?stype=simage&q='+escape(q)">Pictures</A> -
<A HREF="javascript:location.href='results.html?stype=saudio&q='+escape(q)">Sounds</A></FONT></TD></TR></TABLE>
''' + footer('')
    write('results.html', page('AltaVisor: Simple Query', ENGINE_JS + body, ''))


def advanced_page():
    body = small_header('') + '''<P><FONT SIZE=+1 FACE=arial><B>Advanced Search</B></FONT>
<FORM NAME=af METHOD=GET ACTION="results.html"><INPUT TYPE=hidden NAME=pg VALUE=aq>
<TABLE WIDTH=600 BORDER=0 CELLPADDING=4 CELLSPACING=0 BGCOLOR="#FFCC66">
<TR><TD><FONT SIZE=-1><B>Boolean expression:</B></FONT><BR><TEXTAREA NAME=q ROWS=3 COLS=60 WRAP=virtual></TEXTAREA></TD></TR>
<TR><TD><FONT SIZE=-1><B>Ranking:</B> <INPUT NAME=r SIZE=30> (words that should push a page to the top)</FONT></TD></TR>
<TR><TD><FONT SIZE=-1><B>Start date:</B> <INPUT NAME=d0 SIZE=10> <B>End date:</B> <INPUT NAME=d1 SIZE=10> e.g. 21/Mar/99 as 21/03/99
&nbsp; <B>Language:</B> ''' + lang_select() + '''</FONT></TD></TR>
<TR><TD><INPUT TYPE=submit VALUE="Search"> <INPUT TYPE=reset VALUE="Clear"></TD></TR>
</TABLE></FORM>
<SCRIPT LANGUAGE="JavaScript">
<!--
''' + JS_ARGS + '''document.af.q.value = getArg('q');
// -->
</SCRIPT>
<TABLE WIDTH=600 BORDER=0><TR><TD><FONT FACE=arial SIZE=-1>
<B>How to write a Boolean expression</B>
<UL>
<LI><B>AND</B> - both words must appear: <TT>hamster AND wheel</TT>
<LI><B>OR</B> - either word may appear: <TT>cat OR kitten</TT>
<LI><B>AND NOT</B> - leave out pages with the second word: <TT>java AND NOT coffee</TT>
<LI><B>NEAR</B> - both words, close together (Skeeter is generous about "close"): <TT>bean NEAR bag</TT>
</UL>
Words in the <B>Ranking</B> box do not change which pages are found, only the order they come back in.
Dates are compared with the date each page was last modified.</FONT></TD></TR></TABLE>
''' + footer('')
    write('advanced.html', page('AltaVisor: Advanced Search', body, ''))


TRANSLATE_JS = r'''<SCRIPT LANGUAGE="JavaScript" SRC="av_index.js"></SCRIPT>
<SCRIPT LANGUAGE="JavaScript">
<!--
''' + JS_ARGS + r'''
function mapWords(s, map) {
  return s.replace(/[A-Za-z']+/g, function (w) {
    var k = w.toLowerCase(), r = map[k];
    if (typeof r != 'string') return w;
    if (w.charAt(0) != w.charAt(0).toLowerCase()) r = r.charAt(0).toUpperCase() + r.substring(1);
    return r;
  });
}
var PIRATE = { hello: 'ahoy', hi: 'ahoy', my: 'me', you: 'ye', your: 'yer', is: 'be', are: 'be', am: 'be', the: "th'", friend: 'matey', friends: 'mateys',
  money: 'doubloons', computer: 'treasure chest', computers: 'treasure chests', internet: 'seven seas', web: 'seven seas', site: 'ship', page: 'map', pages: 'maps',
  yes: 'aye', no: 'nay', stop: 'avast', look: 'spy', email: 'message in a bottle', welcome: 'welcome aboard', home: 'port', search: 'plunder', find: 'plunder', free: 'stolen' };
var OLDE = { you: 'thou', your: 'thy', yours: 'thine', are: 'art', the: 'ye', is: 'be', has: 'hath', does: 'doth', do: 'dost', hello: 'hail', hi: 'well met',
  computer: 'thinking engine', internet: 'great web of the realm', email: 'missive', page: 'scroll', pages: 'scrolls', site: 'manor', yes: 'aye', no: 'nay',
  very: 'most', cool: 'wondrous', free: 'without coin', before: 'ere', often: 'oft', over: "o'er", it: "'tis", maybe: 'perchance' };
var VALLEY = { very: 'totally', good: 'awesome', great: 'way cool', bad: 'grody', said: 'was all', really: 'like, really', interesting: 'whatever',
  hello: 'hey', excellent: 'all that', boring: 'so lame', information: 'stuff', many: 'like a gazillion' };
function pig(s) {
  return s.replace(/[A-Za-z]+/g, function (w) {
    var cap = w.charAt(0) != w.charAt(0).toLowerCase(), lw = w.toLowerCase(), m = lw.match(/^[^aeiou]+/);
    var r = m == null ? lw + 'way' : (m[0].length == lw.length ? lw + 'ay' : lw.substring(m[0].length) + m[0] + 'ay');
    return cap ? r.charAt(0).toUpperCase() + r.substring(1) : r;
  });
}
function leet(s) {
  var a = 'aeiotsAEIOTS', b = '43107543107$';
  var out = '';
  for (var i = 0; i < s.length; i++) { var k = a.indexOf(s.charAt(i)); out += k >= 0 ? b.charAt(k) : (i % 3 == 0 ? s.charAt(i).toUpperCase() : s.charAt(i)); }
  return out + ' d00d!';
}
function translate(s, lp) {
  if (lp == 'en_xp') return pig(s);
  if (lp == 'en_pi') return mapWords(s, PIRATE).replace(/ing\b/g, "in'").replace(/\.(\s|$)/g, ', arr!$1');
  if (lp == 'en_ol') return 'Verily, ' + mapWords(s, OLDE).replace(/\.(\s|$)/g, ', forsooth.$1');
  if (lp == 'en_va') return 'Like, ' + mapWords(s, VALLEY).replace(/, /g, ', like, ').replace(/\.(\s|$)/g, '. Totally.$1');
  if (lp == 'en_le') return leet(s);
  return s;
}
// -->
</SCRIPT>
'''


def translate_page():
    pairs = [('en_xp', 'English to Pig Latin'), ('en_pi', 'English to Pirate'), ('en_ol', 'English to Olde English'),
             ('en_va', 'English to Valley'), ('en_le', 'English to H4x0r')]
    sel = '<SELECT NAME=lp>' + ''.join('<OPTION VALUE=%s>%s\n' % p for p in pairs) + '</SELECT>'
    body = small_header('') + '''<P><TABLE WIDTH=600 BORDER=0 CELLPADDING=0><TR>
<TD VALIGN=TOP><IMG SRC="images/sponsor_parrot.gif" WIDTH=120 HEIGHT=60 ALT="Parrot"></TD>
<TD VALIGN=TOP><FONT FACE=arial SIZE=+1><B>AltaVisor Translation with Parrot</B></FONT><BR>
<FONT FACE=arial SIZE=-1>Parrot repeats anything you say, only in a different language. He is very proud of it.
Machine translation is not perfect; Parrot is a bird.</FONT></TD></TR></TABLE>
<FORM NAME=tf onSubmit="doText(); return false;">
<TABLE WIDTH=600 BORDER=0 CELLPADDING=4 CELLSPACING=0 BGCOLOR="#FFCC66">
<TR><TD><FONT SIZE=-1><B>Translate this text:</B></FONT><BR><TEXTAREA NAME=src ROWS=4 COLS=60 WRAP=virtual>Welcome to my home page! Please sign my guestbook before you leave.</TEXTAREA></TD></TR>
<TR><TD>''' + sel + ''' <INPUT TYPE=submit VALUE="Translate"></TD></TR>
<TR><TD><FONT SIZE=-1><B>Parrot says:</B></FONT><BR><TEXTAREA NAME=dst ROWS=4 COLS=60 WRAP=virtual></TEXTAREA></TD></TR>
</TABLE></FORM>
<SCRIPT LANGUAGE="JavaScript">
<!--
function lp() { return document.tf.lp.options[document.tf.lp.selectedIndex].value; }
function doText() { document.tf.dst.value = translate(document.tf.src.value, lp()); }
var u = getArg('u'), w = getArg('lp');
if (w != '') for (var i = 0; i < document.tf.lp.options.length; i++) if (document.tf.lp.options[i].value == w) document.tf.lp.selectedIndex = i;
if (u != '') {
  var doc = null;
  for (var i = 0; i < D.length; i++) { var f = D[i].split('|'); if (f[0] == u) doc = f; }
  if (doc == null) document.write('<P>Parrot could not find that page in the index. Perhaps Skeeter has not crawled it yet.');
  else {
    document.write('<P><TABLE WIDTH=600 BORDER=0 CELLPADDING=4 CELLSPACING=0><TR><TD BGCOLOR="#003399"><FONT FACE=arial COLOR="#FFFFFF" SIZE=-1><B>Translated page: ' + h(doc[1]) + '</B></FONT></TD></TR>');
    document.write('<TR><TD><FONT SIZE=-1>In ' + document.tf.lp.options[document.tf.lp.selectedIndex].text.replace('English to ', '') + ':</FONT><P><B>' + h(translate(doc[2], lp())) + '</B><BR>' + h(translate(doc[3], lp())) + '...');
    document.write('<P><FONT SIZE=-1>Original: <A HREF="' + doc[0] + '">' + h(doc[2]) + '</A> - Another language: ');
    for (var i = 0; i < document.tf.lp.options.length; i++) document.write('<A HREF="translate.html?u=' + escape(u) + '&lp=' + document.tf.lp.options[i].value + '">' + document.tf.lp.options[i].text.replace('English to ', '') + '</A> ');
    document.write('</FONT></TD></TR></TABLE>');
  }
}
// -->
</SCRIPT>
''' + footer('')
    write('translate.html', page('AltaVisor Translation with Parrot', TRANSLATE_JS + body, ''))


def addurl_page():
    body = small_header('') + '''<P><TABLE WIDTH=600 BORDER=0><TR><TD VALIGN=TOP><IMG SRC="images/skeeter.gif" WIDTH=64 HEIGHT=64 ALT="Skeeter"></TD>
<TD><FONT FACE=arial SIZE=+1><B>Add or Remove a URL</B></FONT><BR><FONT FACE=arial SIZE=-1>
Skeeter, our web spider, visits millions of pages on his own. If he has missed yours, type its address below and
he will drop by. To remove a page that no longer exists, submit it the same way: Skeeter will notice it is gone
and quietly take it out of the index. Please submit each page only once; Skeeter has a long memory and eight legs to count on.</FONT></TD></TR></TABLE>
<FORM NAME=uf onSubmit="return addUrl();">
<TABLE WIDTH=600 BORDER=0 CELLPADDING=4 CELLSPACING=0 BGCOLOR="#FFCC66">
<TR><TD><FONT SIZE=-1><B>URL:</B></FONT> <INPUT NAME=url SIZE=50 VALUE="http://"> <INPUT TYPE=submit VALUE="Submit"></TD></TR>
</TABLE></FORM>
<P><DIV ID=prog></DIV>
<FORM NAME=pf><TABLE BORDER=0 CELLPADDING=2><TR><TD><FONT SIZE=-1 FACE=arial>Skeeter's progress:</FONT></TD>
<TD><INPUT NAME=bar SIZE=40 VALUE="" STYLE="font-family: monospace"></TD></TR>
<TR><TD></TD><TD><INPUT NAME=msg SIZE=40 VALUE="Waiting for a URL..."></TD></TR></TABLE></FORM>
<SCRIPT LANGUAGE="JavaScript">
<!--
var steps = new Array('Looking up the host name...', 'Knocking on port 80...', 'Reading the page...', 'Ignoring the MIDI file...',
  'Counting the blink tags...', 'Writing it all down...', 'Done! Your page will appear within two weeks.');
var n = 0;
function tick() {
  n++;
  var b = '';
  for (var i = 0; i < n * 6 && i < 40; i++) b += '#';
  document.pf.bar.value = b;
  document.pf.msg.value = steps[Math.min(n - 1, steps.length - 1)];
  if (n < steps.length) setTimeout('tick()', 700);
}
function addUrl() {
  var u = document.uf.url.value;
  if (u.indexOf('http://') != 0 || u.length < 12) { alert('Please enter a complete URL starting with http://'); return false; }
  if (u.indexOf('https://') == 0) { alert('Skeeter cannot read secure pages. Nobody can. That is the point.'); return false; }
  n = 0; tick();
  return false;
}
// -->
</SCRIPT>
''' + footer('')
    write('addurl.html', page('AltaVisor: Add/Remove URL', body, ''))


def help_page():
    body = small_header('') + '''<P><TABLE WIDTH=600 BORDER=0><TR><TD><FONT FACE=arial SIZE=-1>
<FONT SIZE=+1><B>AltaVisor Search Help</B></FONT>
<P><B>Ask a question, or type a few words.</B> AltaVisor understands plain English questions such as
<I>Where can I find pictures of hamsters?</I> It throws away the little words and looks for the important ones.
Pages that contain all of your words come first.
<P><B>Make a word required:</B> put a plus sign in front of it: <TT>+hamster dance</TT>
<BR><B>Leave a word out:</B> put a minus sign in front of it: <TT>java -coffee</TT>
<BR><B>Find a phrase:</B> use double quotes: <TT>"under construction"</TT>
<BR><B>Wildcards:</B> an asterisk at the end matches any ending: <TT>comput*</TT>
<P><B>Special words:</B><BR>
<TT>host:yowza.localhost</TT> - only pages from that host (the <I>More pages from this site</I> link uses this)<BR>
<TT>title:guestbook</TT> - the word must be in the page title<BR>
<TT>url:dogs</TT> - the word must be in the page address
<P><B>Languages:</B> choose a language from the menu to see only pages written in it. Yes, Pig Latin counts.
<P><B>Pictures and sounds:</B> choose <I>Images</I> or <I>Audio</I> above the search box and AltaVisor will show you the
pictures and sound files found on pages about your words.
<P><B>Translate:</B> every result has a <I>Translate</I> link. Parrot will retell the page in another language.
<P><B>Where do the pages come from?</B> Skeeter, our spider, follows links from page to page and reads everything he
finds. See the <A HREF="crawl.html">crawler report</A> for what he read on his last trip.
<P><A NAME="family"></A><B>Family Filter:</B> AltaVisor does not need one. Everything Skeeter found is about hamsters, recipes or Y2K.
</FONT></TD></TR></TABLE>
''' + footer('')
    write('help.html', page('AltaVisor Help', body, ''))


def about_page():
    body = small_header('') + '''<P><TABLE WIDTH=600 BORDER=0><TR><TD><FONT FACE=arial SIZE=-1>
<FONT SIZE=+1><B>About AltaVisor</B></FONT>
<P>AltaVisor began in 1995 in a research lab at Gibson Mainframe Co., where a team of engineers needed a reason
to keep a refrigerator-sized 64-bit computer busy over the weekend. They wrote a program that read the entire
Web, which at the time took most of a Saturday. The program was named Skeeter, it grew eight legs, and it has
not stopped reading since.
<P>Today AltaVisor answers millions of questions a day. Our motto, <I>smart is beautiful</I>, refers to the
search engine. It does not refer to the engineers, who still wear the same T-shirt from the 1996 company picnic.
<P><A NAME="legal"></A><B>Disclaimer</B><BR>
AltaVisor indexes pages written by other people. We are not responsible for what they say, how they spell it, or
how many animated GIFs they put next to it. AltaVisor is a parody and is not affiliated with any real company.
<P><A NAME="privacy"></A><B>Privacy Policy</B><BR>
Your searches run inside your own browser. We do not see them, we do not keep them, and frankly we do not want
to know what you were looking for.
</FONT></TD></TR></TABLE>
''' + footer('')
    write('about.html', page('About AltaVisor', body, ''))


def main():
    n = invented_web()
    home_page(); results_page(); advanced_page(); translate_page(); addurl_page(); help_page(); about_page()
    print('AltaVisor static pages written; %d invented-web pages in web/' % n)
    print('now run tools/crawl.py to (re)build the index')


if __name__ == '__main__':
    main()
