#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builds the static uBid site (a 1999 Web parody of an online auction house).

    python3 tools/build.py          # pages + graphics
    python3 tools/build.py --pages  # pages only

Auctions are "live" thanks to js/ubid.js: every listing runs on a fixed schedule from
EPOCH (Jan 1 2000, naturally), ends, picks a winner by proxy bidding, and relists itself
two days later.  House bids are generated here; visitors' bids live in a cookie.
"""
import os
import random
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import items_data as D  # noqa: E402

AR = "Arial, Helvetica"
RING = ["yowza", "altavisor", "askreeves", "orinoco", "ubid", "etoyz", "petz", "geohoods",
        "hamstershuffle", "dashdot", "snapster", "cnm"]
DAY = 86400000
DEMO_IDS = ("beaniebaron", "y2kprepper")
NAVCOLOR = {"browse": "#6A2DB8", "sell": "#E0218A", "services": "#0E8C8C", "search": "#F28C00",
            "help": "#3366CC", "community": "#339933"}
NAVHREF = {"browse": "categories.html", "sell": "sell.html", "services": "myubid.html", "search": "search.html",
           "help": "help.html", "community": "feedback.html"}
SUBNAV = {
    "browse": [("categories", "categories.html"), ("featured", "featured.html"), ("going, going, gone", "ending.html"),
               ("new today", "new.html"), ("completed", "completed.html")],
    "sell": [("sell your item", "sell.html"), ("my listings", "myubid.html#selling"), ("seller tips", "help.html#selling")],
    "services": [("register", "register.html"), ("sign in", "signin.html"), ("my uBid", "myubid.html"),
                 ("feedback forum", "feedback.html"), ("SafeBid", "help.html#safebid")],
    "search": [("find items", "search.html"), ("by seller", "search.html#seller"), ("completed auctions", "search.html#completed")],
    "help": [("help topics", "help.html"), ("how to bid", "help.html#bidding"), ("how to sell", "help.html#selling"),
             ("feedback stars", "help.html#stars"), ("site map", "sitemap.html")],
    "community": [("feedback forum", "feedback.html"), ("news", "help.html#news"), ("about uBid", "help.html#about")],
}
PAGES = []
NAVSIZE = {}


# ====================================================================== data
def parse_items():
    rnd = random.Random(19991999)
    users = [u for u in D.USERS]
    by_kind_seller = {}
    items = []
    ids = set()
    for n, line in enumerate(D.ITEMS.strip().splitlines()):
        cat, kind, title, start, value, reserve, desc = line.split("|")
        while True:
            iid = str(rnd.randint(168000000, 199999999))
            if iid not in ids:
                ids.add(iid)
                break
        seller = rnd.choice(users)
        # sellers tend to specialise: reuse a seller for the same kind sometimes
        if kind in by_kind_seller and rnd.random() < .5:
            seller = by_kind_seller[kind]
        by_kind_seller[kind] = seller
        it = {"id": iid, "cat": cat, "kind": kind, "title": title, "start": int(round(float(start) * 100)),
              "value": int(round(float(value) * 100)), "desc": desc, "seller": seller[0], "location": seller[2],
              "dur": rnd.choice([3, 5, 5, 7, 7, 7]), "featured": 0}
        it["phase"] = rnd.randint(0, (it["dur"] + 2) * DAY - 1)
        it["reserve"] = int(it["value"] * rnd.uniform(0.75, 1.25)) // 100 * 100 if reserve == "1" else 0
        it["bids"] = make_bids(rnd, it, users)
        items.append(it)
    # featured: the twenty juiciest
    for it in sorted(items, key=lambda i: -i["value"])[:22]:
        it["featured"] = 1
    return items


def inc(c):
    for lim, step in ((100, 5), (500, 25), (2500, 50), (10000, 100), (25000, 250), (50000, 500), (100000, 1000)):
        if c < lim:
            return step
    return 2500


def make_bids(rnd, it, users):
    """house bids for one run of the auction: (fraction of duration, bidder, max) with sniping at the end"""
    S, V = it["start"], it["value"]
    heat = V / float(max(S, 1))
    n = int(min(28, max(0, rnd.gauss(2 + heat * 1.6, 2.5))))
    if rnd.random() < .12:
        n = 0
    pool = [u[0] for u in users if u[0] != it["seller"] and u[0] not in DEMO_IDS]
    bidders = rnd.sample(pool, min(len(pool), max(2, n // 2 + 1)))
    fr = sorted([rnd.random() ** 0.6 if rnd.random() < .6 else rnd.uniform(0.9, 0.9995) for _ in range(n)])
    bids = []
    price, high, high_max = S, None, 0
    for k, f in enumerate(fr):
        who = rnd.choice(bidders)
        target = S + (V - S) * ((k + 1) / float(n)) * rnd.uniform(0.75, 1.15)
        minimum = S if high is None else price + inc(price)
        mx = max(int(target) // 25 * 25, minimum)
        if who == high:
            mx = max(mx, high_max + inc(high_max))
        bids.append((round(f, 5), who, mx))
        # proxy bookkeeping so later bids are sensible
        if high is None:
            high, high_max, price = who, mx, S
        elif who == high:
            high_max = max(high_max, mx)
        elif mx > high_max:
            price, high, high_max = min(mx, high_max + inc(high_max)), who, mx
        else:
            price = min(high_max, mx + inc(mx))
    return bids


def make_feedback(rnd, user, items_by_seller):
    score = user[1]
    neg = int(score * rnd.uniform(0, 0.02)) if score > 30 else 0
    neu = int(score * rnd.uniform(0, 0.03))
    pos = score + neg
    shown = []
    others = [u[0] for u in D.USERS if u[0] != user[0]]
    total = min(pos + neg + neu, 25)
    for k in range(total):
        r = rnd.random()
        if r < neg / float(max(1, pos + neg + neu)):
            typ, text = "Complaint", rnd.choice(D.COMPLAINT)
        elif r < (neg + neu) / float(max(1, pos + neg + neu)):
            typ, text = "Neutral", rnd.choice(D.NEUTRAL)
        else:
            typ, text = "Praise", rnd.choice(D.PRAISE)
        day = 20 - k
        shown.append((rnd.choice(others), "%02d/%02d/99" % (10 if day > 0 else 9, day if day > 0 else 30 + day), typ, text,
                      str(rnd.randint(150000000, 199999999))))
    return {"pos": pos, "neg": neg, "neu": neu, "list": shown}


# ====================================================================== chrome
def money(c):
    return "$%s.%02d" % ("{:,}".format(c // 100), c % 100)


def page(path, title, section, body, extra_head=""):
    depth = path.count("/")
    P = "../" * depth
    h = ['<HTML>\n<HEAD>\n<TITLE>uBid %s</TITLE>\n' % title]
    h.append('<META NAME="description" CONTENT="uBid: your personal trading post. Bid on Beanie Babies, Furbys, Zip disks and Y2K survival kits.">\n')
    h.append('<SCRIPT LANGUAGE="JavaScript">var P = "%s";</SCRIPT>\n' % P)
    h.append('<SCRIPT LANGUAGE="JavaScript1.2" SRC="%sjs/items.js"></SCRIPT>\n' % P)
    h.append('<SCRIPT LANGUAGE="JavaScript1.2" SRC="%sjs/ubid.js"></SCRIPT>\n' % P)
    h.append(extra_head)
    h.append('</HEAD>\n<BODY BGCOLOR="#FFFFFF" TEXT="#000000" LINK="#0000CC" VLINK="#660099">\n')
    h.append(header(P, section))
    h.append(body.replace("{P}", P))
    h.append(footer(P))
    h.append("</BODY>\n</HTML>\n")
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="latin-1", errors="xmlcharrefreplace") as f:
        f.write("".join(h))
    PAGES.append(path)


def header(P, section):
    from gfx import NAV
    s = ['<TABLE WIDTH=760 BORDER=0 CELLPADDING=0 CELLSPACING=0>\n<TR><TD ROWSPAN=2 WIDTH=160 VALIGN=TOP>'
         '<A HREF="%sindex.html"><IMG SRC="%simages/logo.gif" WIDTH=150 HEIGHT=64 BORDER=0 ALT="uBid"></A></TD>\n' % (P, P)]
    s.append('<TD ALIGN=RIGHT VALIGN=TOP><FONT FACE="%s" SIZE=2><A HREF="%sindex.html">home</A> | <A HREF="%smyubid.html">my uBid</A> | '
             '<A HREF="%ssitemap.html">site map</A> | <SCRIPT LANGUAGE="JavaScript">writeUserLinks();</SCRIPT></FONT></TD></TR>\n' % (AR, P, P, P))
    s.append('<TR><TD VALIGN=BOTTOM NOWRAP>')
    for key, label, _c in NAV:
        w, hgt = NAVSIZE[key]
        s.append('<A HREF="%s%s"><IMG SRC="%simages/nav/%s_%d.gif" WIDTH=%d HEIGHT=%d BORDER=0 ALT="%s"></A>' % (
            P, NAVHREF[key], P, key, 1 if key == section else 0, w, hgt, label))
    s.append('</TD></TR>\n')
    color = NAVCOLOR.get(section, "#6A2DB8")
    s.append('<TR><TD COLSPAN=2 BGCOLOR="%s"><IMG SRC="%simages/pixel.gif" WIDTH=1 HEIGHT=3></TD></TR>\n' % (color, P))
    links = " | ".join('<A HREF="%s%s">%s</A>' % (P, h, l) for l, h in SUBNAV.get(section, SUBNAV["browse"]))
    s.append('<TR><TD COLSPAN=2 BGCOLOR="#EFEFEF"><TABLE WIDTH="100%%" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD><FONT FACE="%s" SIZE=2>&nbsp;%s</FONT></TD>'
             '<TD ALIGN=RIGHT><FORM NAME="hs" ACTION="%ssearch.html" METHOD=GET><FONT FACE="%s" SIZE=2><INPUT TYPE=text NAME="q" SIZE=14> '
             '<INPUT TYPE=submit VALUE="Search"></FONT></FORM></TD></TR></TABLE></TD></TR>\n' % (AR, links, P, AR))
    s.append('</TABLE>\n')
    return "".join(s)


def footer(P):
    i = RING.index("ubid")
    prev, nxt = RING[i - 1], RING[(i + 1) % len(RING)]
    s = ['<TABLE WIDTH=760 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD ALIGN=CENTER><BR><HR SIZE=1 NOSHADE>\n<FONT FACE="%s" SIZE=2>' % AR]
    s.append(" | ".join('<A HREF="%s%s">%s</A>' % (P, h, l) for l, h in [
        ("Announcements", "help.html#news"), ("Register", "register.html"), ("SafeBid", "help.html#safebid"),
        ("Feedback Forum", "feedback.html"), ("About uBid", "help.html#about")]))
    s.append('<BR>' + " | ".join('<A HREF="%s%s">%s</A>' % (P, h, l) for l, h in [
        ("Browse", "categories.html"), ("Sell", "sell.html"), ("Services", "myubid.html"), ("Search", "search.html"),
        ("Help", "help.html"), ("Community", "feedback.html")]))
    s.append('<BR><BR><FONT SIZE=1><SCRIPT LANGUAGE="JavaScript">writeStamp();</SCRIPT><BR>'
             'Copyright &copy; 1995-1999 uBid Inc. All Rights Reserved. By bidding you agree to the uBid User Agreement, which mostly says &quot;pay for what you win.&quot;<BR>'
             'Running on a rack of KoldFusion 4.5 servers from Gibson Mainframe Co. <I>A 1999 Web parody: every item, member and bid here is invented.</I></FONT></FONT>\n')
    s.append('<BR><BR><TABLE BORDER=2 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#C0C0C0"><TR><TD ALIGN=CENTER NOWRAP><FONT FACE="Arial, Helvetica" SIZE=1>\n')
    s.append('<A HREF="%s../%s/index.html">&lt;&lt; Prev</A> | <A HREF="%s../../web1999/index.html" onClick="return ringRandom()">Random</A> | '
             '<B><A HREF="%s../../web1999/index.html">The 1999 Web Ring</A></B> | <A HREF="%s../%s/index.html">Next &gt;&gt;</A>\n' % (P, prev, P, P, P, nxt))
    s.append('</FONT></TD></TR></TABLE>\n</TD></TR></TABLE>\n')
    return "".join(s)


def wrap(inner):
    return '<TABLE WIDTH=760 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD><BR>%s</TD></TR></TABLE>\n' % inner


def bar(text, color="#CCCCFF", size=3):
    return ('<TABLE WIDTH="100%%" BORDER=0 CELLPADDING=3 CELLSPACING=0><TR><TD BGCOLOR="%s"><FONT FACE="%s" SIZE=%d><B>%s</B></FONT></TD></TR></TABLE>'
            % (color, AR, size, text))


def cat_name(c):
    return dict((a, b) for a, b, _n in D.CATEGORIES)[c]


# ====================================================================== pages
def build_home(items):
    cats = "".join('<FONT SIZE=2><A HREF="{P}category/%s.html">%s</A> (%s)</FONT><BR>' % (c, n, "{:,}".format(cnt)) for c, n, cnt in D.CATEGORIES)
    total = sum(cnt for _c, _n, cnt in D.CATEGORIES)
    left = ('<TABLE BORDER=0 WIDTH=169 CELLPADDING=0 CELLSPACING=0><TR><TD><IMG SRC="{P}images/h_categories.gif" WIDTH=169 HEIGHT=22 ALT="Categories"></TD></TR>'
            '<TR><TD BGCOLOR="#E5E5CC"><TABLE BORDER=0 CELLPADDING=5 CELLSPACING=0><TR><TD><FONT FACE="%s">%s<BR>'
            '<FONT SIZE=2><A HREF="{P}categories.html"><B>all categories...</B></A><BR><A HREF="{P}ending.html">going, going, gone...</A><BR>'
            '<A HREF="{P}new.html">new today...</A><BR><A HREF="{P}completed.html">just sold...</A></FONT></FONT></TD></TR></TABLE></TD></TR></TABLE><BR>'
            '<TABLE BORDER=0 WIDTH=169 CELLPADDING=5 CELLSPACING=0 BGCOLOR="#FFFFCC"><TR><TD><FONT FACE="%s" SIZE=2><B>uBid in numbers</B><BR>'
            '%s items for sale in 2,568 categories now!<BR><BR>Over 1.6 billion page views per month, give or take a billion.</FONT></TD></TR></TABLE>'
            % (AR, cats, AR, "{:,}".format(total)))
    promos = ('<A HREF="{P}sell.html"><IMG SRC="{P}images/promo_sell.gif" WIDTH=128 HEIGHT=40 BORDER=0 ALT="Sell your item!"></A> '
              '<A HREF="{P}help.html"><IMG SRC="{P}images/promo_new.gif" WIDTH=128 HEIGHT=40 BORDER=0 ALT="New to uBid?"></A> '
              '<A HREF="{P}register.html"><IMG SRC="{P}images/promo_register.gif" WIDTH=128 HEIGHT=40 BORDER=0 ALT="Register, it\'s free!"></A> '
              '<A HREF="{P}ending.html"><IMG SRC="{P}images/promo_gone.gif" WIDTH=128 HEIGHT=40 BORDER=0 ALT="Going, going, gone!"></A>')
    search = ('<FORM NAME="big" ACTION="{P}search.html" METHOD=GET><TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 BGCOLOR="#CCCCFF" WIDTH="100%%"><TR><TD>'
              '<FONT FACE="%s" SIZE=3><B>What are you looking for?</B></FONT><BR><INPUT TYPE=text NAME="q" SIZE=30 MAXLENGTH=100> '
              '<INPUT TYPE=submit VALUE="Find it!"> <FONT SIZE=1 FACE="%s"><A HREF="{P}help.html#searching">tips</A></FONT></TD></TR></TABLE></FORM>' % (AR, AR))
    feat = ('<IMG SRC="{P}images/h_featured.gif" WIDTH=290 HEIGHT=22 ALT="Featured Auctions"><BR>'
            '<SCRIPT LANGUAGE="JavaScript">\n'
            'var fr = pick("featured", "", false);\n'
            'for (var i = 0; i < fr.length && i < 9; i++) {\n'
            '  var it = fr[i][0], A = fr[i][1];\n'
            '  document.write("<IMG SRC=\\"" + P + "images/gavel.gif\\" WIDTH=14 HEIGHT=14> <FONT SIZE=2><A HREF=\\"" + itemURL(it) + "\\">" + esc(it[1]) + "</A> <B>" + money(A.price) + "</B> <FONT COLOR=\\"#666666\\">(" + timeLeft(A.end - now()) + ")</FONT></FONT><BR>");\n'
            '}\n'
            '</SCRIPT><FONT SIZE=2><A HREF="{P}featured.html"><B>see all featured...</B></A></FONT><BR><BR>')
    gone = ('<IMG SRC="{P}images/h_gone.gif" WIDTH=290 HEIGHT=22 ALT="Going, Going, Gone!"><BR>'
            '<SCRIPT LANGUAGE="JavaScript">\n'
            'var gr = sortRows(pick("soon", 12 * HOUR, false), "end");\n'
            'for (var i = 0; i < gr.length && i < 6; i++) {\n'
            '  var it = gr[i][0], A = gr[i][1];\n'
            '  document.write("<IMG SRC=\\"" + P + "images/clock.gif\\" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE> <FONT SIZE=2><A HREF=\\"" + itemURL(it) + "\\">" + esc(it[1]) + "</A> <B>" + money(A.price) + "</B> <FONT COLOR=\\"#FF0000\\">" + timeLeft(A.end - now()) + "</FONT></FONT><BR>");\n'
            '}\n'
            'if (gr.length == 0) document.write("<FONT SIZE=2>Nothing ends in the next twelve hours. Go outside!</FONT><BR>");\n'
            '</SCRIPT><FONT SIZE=2><A HREF="{P}ending.html"><B>see everything ending soon...</B></A></FONT>')
    news = ('<TABLE BORDER=0 CELLPADDING=5 CELLSPACING=0 WIDTH=180 BGCOLOR="#E5E5CC"><TR><TD><FONT FACE="%s" SIZE=2>'
            '<B>New to uBid?</B><BR>&#149; <A HREF="{P}help.html#bidding">How do I bid?</A><BR>&#149; <A HREF="{P}help.html#selling">How do I sell?</A><BR>'
            '&#149; <A HREF="{P}help.html#safebid">Is uBid safe?</A><BR>&#149; <A HREF="{P}register.html">Register, it\'s free!</A></FONT></TD></TR></TABLE><BR>'
            '<TABLE BORDER=0 CELLPADDING=5 CELLSPACING=0 WIDTH=180 BGCOLOR="#FFFFCC"><TR><TD><FONT FACE="%s" SIZE=2><B>cool happenings...</B><BR><BR>'
            '<IMG SRC="{P}images/new_icon.gif" WIDTH=30 HEIGHT=13> <B>Y2K Bunker Week!</B> Generators, candles and freeze-dried ice cream are flying off the virtual shelves. '
            '<A HREF="{P}search.html?q=y2k">Shop the bunker</A>.<BR><BR><B>Furby Watch:</B> prices for new-in-box Furbys are up 40%% since Halloween. '
            'Our economists are baffled. <A HREF="{P}search.html?q=furby">See for yourself</A>.<BR><BR><B>Tip of the week:</B> enter the most you are willing to pay; '
            'our proxy bidding robot will bid for you, one increment at a time. <A HREF="{P}help.html#bidding">Learn more</A>.</FONT></TD></TR></TABLE>' % (AR, AR))
    body = ('<TABLE WIDTH=760 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD COLSPAN=5><BR></TD></TR><TR>'
            '<TD WIDTH=169 VALIGN=TOP>%s</TD><TD WIDTH=12>&nbsp;</TD>'
            '<TD VALIGN=TOP WIDTH=380><FONT FACE="%s">%s%s<BR><BR>%s%s</FONT></TD><TD WIDTH=12>&nbsp;</TD><TD VALIGN=TOP WIDTH=180>%s</TD></TR></TABLE>'
            % (left, AR, search, promos, feat, gone, news))
    page("index.html", "- your personal trading post", "browse", body)


def build_categories(items):
    rows = []
    for c, n, cnt in D.CATEGORIES:
        sample = [i for i in items if i["cat"] == c][:4]
        rows.append('<TR><TD VALIGN=TOP><FONT FACE="%s" SIZE=3><B><A HREF="{P}category/%s.html">%s</A></B></FONT> <FONT SIZE=2>(%s)</FONT><BR>'
                    '<FONT SIZE=2>%s ...</FONT></TD></TR>' % (AR, c, n, "{:,}".format(cnt), ", ".join(
                        '<A HREF="{P}item/%s.html">%s</A>' % (i["id"], i["title"][:38].rstrip() + ("..." if len(i["title"]) > 38 else "")) for i in sample)))
    body = wrap('<FONT FACE="%s" SIZE=5><B>All Categories</B></FONT><BR><FONT SIZE=2>Click on a category to see what is up for auction right now.</FONT><BR><BR>'
                '<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%%">%s</TABLE>' % (AR, "".join(rows)))
    page("categories.html", "Categories", "browse", body)
    for c, n, cnt in D.CATEGORIES:
        static = "".join('<A HREF="{P}item/%s.html">%s</A><BR>' % (i["id"], i["title"]) for i in items if i["cat"] == c)
        body = wrap('<FONT SIZE=2><A HREF="{P}categories.html">Categories</A> &gt; %s</FONT><BR>'
                    '<FONT FACE="%s" SIZE=5><B>%s</B></FONT><BR>'
                    '<SCRIPT LANGUAGE="JavaScript">writeCategory("%s");</SCRIPT>'
                    '<NOSCRIPT><B>Your browser does not run JavaScript, so here is the plain list:</B><BR>%s</NOSCRIPT>' % (n, AR, n, c, static))
        page("category/%s.html" % c, n, "browse", body)


def build_lists():
    specs = [
        ("featured.html", "Featured Auctions", '<IMG SRC="{P}images/featured.gif" WIDTH=16 HEIGHT=16> Featured Auctions',
         "Our sellers' finest offerings, hand-picked by the people who paid us $99.95 to feature them.",
         'sortRows(pick("featured", "", false), "end")', "live"),
        ("ending.html", "Going, Going, Gone!", '<IMG SRC="{P}images/clock.gif" WIDTH=16 HEIGHT=16> Going, Going, Gone!',
         "Every auction ending in the next 24 hours, soonest first. Bid now or forever hold your peace.",
         'sortRows(pick("soon", DAY, false), "end")', "live"),
        ("new.html", "New Today", '<IMG SRC="{P}images/new_icon.gif" WIDTH=30 HEIGHT=13> New Today',
         "Auctions that started in the last 24 hours. Get in early, before the snipers wake up.",
         'sortRows(pick("new", DAY, false), "new")', "live"),
        ("completed.html", "Completed Auctions", "Completed Auctions",
         "These auctions have closed. Winners have been notified by e-mail and are presumably doing a little dance. Items relist two days after closing.",
         'sortRows(pick("all", "", true), "ended")', "ended"),
    ]
    for path, title, head, intro, expr, mode in specs:
        body = wrap('<FONT FACE="%s" SIZE=5><B>%s</B></FONT><BR><FONT SIZE=2>%s</FONT><BR><BR>'
                    '<SCRIPT LANGUAGE="JavaScript">var rows = %s; document.write("<FONT SIZE=2>" + rows.length + " items</FONT><BR>" + listTable(rows, "%s"));</SCRIPT>'
                    '<NOSCRIPT>This list is computed live and needs JavaScript. <A HREF="{P}categories.html">Browse categories</A> instead.</NOSCRIPT>'
                    % (AR, head, intro, expr, mode))
        page(path, title, "browse", body)


def build_items(items):
    for it in items:
        cat = cat_name(it["cat"])
        u = dict((x[0], x) for x in D.USERS)[it["seller"]]
        body = []
        body.append('<TABLE WIDTH="100%%" BORDER=0 CELLPADDING=4 CELLSPACING=0><TR><TD BGCOLOR="#99CCFF" ALIGN=CENTER>'
                    '<FONT FACE="%s" SIZE=4><B>%s</B></FONT><BR><FONT FACE="%s" SIZE=2>Item #%s</FONT></TD></TR></TABLE>' % (AR, it["title"], AR, it["id"]))
        body.append('<CENTER><FONT SIZE=2><A HREF="{P}categories.html">Categories</A> &gt; <A HREF="{P}category/%s.html">%s</A></FONT></CENTER><BR>' % (it["cat"], cat))
        body.append('<TABLE WIDTH="100%" BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD VALIGN=TOP>')
        body.append('<SCRIPT LANGUAGE="JavaScript">writeItemBox("%s");</SCRIPT>' % it["id"])
        body.append('<NOSCRIPT><B>Seller:</B> %s<BR><B>Location:</B> %s<BR>Live prices and bidding need JavaScript.</NOSCRIPT>' % (it["seller"], it["location"]))
        body.append('</TD><TD VALIGN=TOP ALIGN=RIGHT WIDTH=170><IMG SRC="{P}images/items/%s.gif" WIDTH=160 HEIGHT=120 BORDER=1 ALT="photo"><BR>'
                    '<FONT SIZE=1>(picture is of the actual item)</FONT></TD></TR></TABLE><BR>' % it["id"])
        body.append(bar("Description", "#EFEFEF"))
        boiler = random.Random(it["id"]).choice([
            "Buyer pays actual shipping. Money orders ship the same day; personal checks wait ten days to clear. Good luck bidding!",
            "Winning bidder adds $4.00 shipping and handling. I ship Monday and Thursday. E-mail me with any questions BEFORE bidding.",
            "Please pay within 10 days of the auction's end. Insurance optional but recommended. Check out my other auctions!",
            "Ships in a sturdy box with plenty of packing peanuts. U.S. buyers only, sorry. Thanks for looking!",
        ])
        body.append('<BLOCKQUOTE><FONT SIZE=3>%s</FONT><BR><BR><FONT SIZE=2>%s</FONT><BR><BR>'
                    '<CENTER><IMG SRC="{P}images/items/%s.gif" WIDTH=160 HEIGHT=120 BORDER=0 ALT="another picture of the item"></CENTER></BLOCKQUOTE>' % (it["desc"], boiler, it["id"]))
        body.append('<A NAME="bid"></A>' + bar("Bidding", "#CCCCFF"))
        body.append('<SCRIPT LANGUAGE="JavaScript">writeBidForm("%s");</SCRIPT>' % it["id"])
        page("item/%s.html" % it["id"], "item %s - %s" % (it["id"], re.sub(r"<[^>]+>", "", it["title"])), "browse", wrap("".join(body)))


def build_members(items):
    rnd = random.Random(42)
    for u in D.USERS:
        fb = make_feedback(rnd, u, None)
        star = ""
        for minimum, name, _c in reversed([(10, "yellow", 0), (50, "green", 0), (100, "turquoise", 0), (500, "purple", 0), (1000, "red", 0), (5000, "gold", 0)]):
            if u[1] >= minimum:
                star = '<IMG SRC="{P}images/stars/star_%s.gif" WIDTH=16 HEIGHT=16 ALT="%s star">' % (name, name)
                break
        rows = []
        for n, (frm, date, typ, text, item) in enumerate(fb["list"]):
            col = {"Praise": "#008800", "Neutral": "#000000", "Complaint": "#CC0000"}[typ]
            rows.append('<TR BGCOLOR="%s"><TD><FONT SIZE=2>User: <A HREF="{P}member/%s.html">%s</A><BR>Date: %s PDT &nbsp; Item: %s<BR>'
                        '<FONT COLOR="%s"><B>%s:</B></FONT> %s</FONT></TD></TR>' % ("#FFFFFF" if n % 2 else "#EFEFEF", frm, frm, date, item, col, typ, text))
        selling = [i for i in items if i["seller"] == u[0]]
        body = wrap(
            '<FONT FACE="%s" SIZE=5><B>Feedback Profile</B></FONT><BR><BR>'
            '<TABLE BORDER=1 CELLPADDING=6 CELLSPACING=0 WIDTH="100%%"><TR><TD VALIGN=TOP BGCOLOR="#FFFFCC" WIDTH="45%%"><FONT FACE="%s" SIZE=4><B>%s</B> '
            '(<SCRIPT LANGUAGE="JavaScript">document.write(scoreOf("%s"));</SCRIPT><NOSCRIPT>%d</NOSCRIPT>) %s</FONT><BR>'
            '<FONT SIZE=2>Member since %s. Location: %s<BR><A HREF="{P}search.html?seller=%s">Items for sale by %s</A> (%d)</FONT></TD>'
            '<TD VALIGN=TOP><FONT FACE="%s" SIZE=2><B>uBid Feedback Overall Profile</B><BR>'
            '<TABLE BORDER=0 CELLPADDING=1><TR><TD><FONT SIZE=2>Positives:</FONT></TD><TD ALIGN=RIGHT><FONT SIZE=2 COLOR="#008800">%d</FONT></TD></TR>'
            '<TR><TD><FONT SIZE=2>Neutrals:</FONT></TD><TD ALIGN=RIGHT><FONT SIZE=2>%d</FONT></TD></TR>'
            '<TR><TD><FONT SIZE=2>Negatives:</FONT></TD><TD ALIGN=RIGHT><FONT SIZE=2 COLOR="#CC0000">%d</FONT></TD></TR></TABLE>'
            'Your feedback rating is the number of positive comments minus negative comments, one per member.</FONT></TD></TR></TABLE><BR>'
            '<FONT SIZE=2><A HREF="{P}feedback.html?to=%s">Leave feedback for %s</A> | <A HREF="{P}help.html#stars">What do the stars mean?</A></FONT><BR><BR>'
            '%s<SCRIPT LANGUAGE="JavaScript">writeMyFeedback("%s");</SCRIPT>'
            '<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%%">%s</TABLE>'
            % (AR, AR, u[0], u[0], u[1], star, u[3], u[2], u[0], u[0], len(selling), AR, fb["pos"], fb["neu"], fb["neg"], u[0], u[0],
               bar("Recent comments about %s" % u[0]), u[0], "".join(rows)))
        page("member/%s.html" % u[0], "Feedback Profile for %s" % u[0], "community", body)


def read_tpl(name):
    with open(os.path.join(HERE, "pages", name), encoding="utf-8") as f:
        return f.read()


def build_js_pages():
    specs = [("bid.html", "Review Bid", "browse"), ("bidresult.html", "Bid Result", "browse"),
             ("bidhistory.html", "Bid History", "browse"), ("uitem.html", "Your Listing", "sell"),
             ("sell.html", "Sell Your Item", "sell"), ("sold.html", "Item Listed", "sell"),
             ("register.html", "Registration", "services"), ("signin.html", "Sign In", "services"),
             ("myubid.html", "My uBid", "services"), ("feedback.html", "Feedback Forum", "community"),
             ("search.html", "Search", "search"), ("help.html", "Help", "help")]
    for path, title, section in specs:
        page(path, title, section, wrap(read_tpl(path)))


def build_sitemap():
    groups = [("Browse", [("All categories", "categories.html"), ("Featured auctions", "featured.html"),
                          ("Going, going, gone", "ending.html"), ("New today", "new.html"), ("Completed auctions", "completed.html")]
               + [(n, "category/%s.html" % c) for c, n, _x in D.CATEGORIES]),
              ("Sell", [("Sell your item", "sell.html"), ("My listings", "myubid.html#selling")]),
              ("Services", [("Register", "register.html"), ("Sign in", "signin.html"), ("My uBid", "myubid.html"),
                            ("Feedback Forum", "feedback.html")]),
              ("Search", [("Search items", "search.html"), ("Search by seller", "search.html#seller")]),
              ("Help", [("Help topics", "help.html"), ("How to bid", "help.html#bidding"), ("How to sell", "help.html#selling"),
                        ("Feedback stars", "help.html#stars"), ("SafeBid", "help.html#safebid")]),
              ("Members", [(u[0], "member/%s.html" % u[0]) for u in D.USERS])]
    cols = []
    for g, links in groups:
        cols.append('<P><FONT FACE="%s" SIZE=3><B>%s</B></FONT><BR><FONT SIZE=2>%s</FONT></P>' % (
            AR, g, " | ".join('<A HREF="{P}%s">%s</A>' % (h, l) for l, h in links)))
    page("sitemap.html", "Site Map", "help", wrap('<FONT FACE="%s" SIZE=5><B>Site Map</B></FONT><BR>%s' % (AR, "".join(cols))))


def write_js(items):
    def js(s):
        s = s.replace("&amp;", "&")
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    out = ["// uBid listings, generated by tools/build.py -- do not edit by hand",
           "// I[n] = id, title, category, seller, start bid (cents), reserve, days, phase (ms), featured, house bids, location, fixedStart, picture, description",
           "var EPOCH = 946684800000; // the auction clock started at midnight, January 1 2000 (UTC). Of course it did.",
           "var I = new Array();"]
    for n, it in enumerate(items):
        bids = ";".join("%s,%s,%d" % (f, w, m) for f, w, m in it["bids"])
        out.append("I[%d] = new Array(%s, %s, %s, %s, %d, %d, %d, %d, %d, %s, %s, 0, %s, %s);" % (
            n, js(it["id"]), js(it["title"]), js(it["cat"]), js(it["seller"]), it["start"], it["reserve"], it["dur"], it["phase"],
            it["featured"], js(bids), js(it["location"]), js(it["kind"]), js(it["desc"])))
    out.append("var CATS = new Array(%s);" % ", ".join("new Array(%s, %s, %d)" % (js(c), js(n), k) for c, n, k in D.CATEGORIES))
    out.append("var USERS = new Array(%s);" % ", ".join("new Array(%s, %d, %s)" % (js(u[0]), u[1], js(u[2])) for u in D.USERS))
    with open(os.path.join(ROOT, "js", "items.js"), "w", encoding="latin-1", errors="xmlcharrefreplace") as f:
        f.write("\n".join(out) + "\n")


STOCK = ["box", "beanie", "furby", "computer", "book", "coin", "doll", "lamp", "camera", "card"]


def main():
    import gfx
    from PIL import Image
    items = parse_items()
    global NAVSIZE
    if "--pages" in sys.argv:
        for key, _l, _c in gfx.NAV:
            NAVSIZE[key] = Image.open(os.path.join(ROOT, "images", "nav", key + "_0.gif")).size
    else:
        sizes = gfx.all_static()
        NAVSIZE = sizes["nav"]
        shutil.rmtree(os.path.join(ROOT, "images", "items"), ignore_errors=True)
        for it in items:
            gfx.item_photo(it["id"], it["kind"], it["id"])
        for k in STOCK:
            gfx.item_photo("stock_" + k, k, "stock" + k)
        px = Image.new("P", (1, 1), 0)
        px.putpalette([255, 255, 255] * 2)
        px.save(os.path.join(ROOT, "images", "pixel.gif"), transparency=0)
    for d in ("item", "member", "category"):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    write_js(items)
    build_home(items)
    build_categories(items)
    build_lists()
    build_items(items)
    build_members(items)
    build_js_pages()
    build_sitemap()
    print("uBid: %d items, %d pages" % (len(items), len(PAGES)))


if __name__ == "__main__":
    main()
