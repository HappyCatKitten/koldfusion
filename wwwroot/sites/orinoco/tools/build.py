#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builds the static Orinoco.com site (a 1999 Web parody) into the folder above this one.

    python3 tools/build.py          # pages + graphics
    python3 tools/build.py --pages  # pages only (skip the Pillow drawing)

Everything is relative-linked so the site works at http://orinoco.localhost:PORT/,
at http://localhost:PORT/sites/orinoco/ and from a plain folder.
"""
import os
import random
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import books_data as D  # noqa: E402

FONT = "verdana,arial,helvetica"
SUBJ = dict(D.SUBJECTS)
RING = ["yowza", "altavisor", "askreeves", "orinoco", "ubid", "etoyz", "petz", "geohoods",
        "hamstershuffle", "dashdot", "snapster", "cnm"]
RING_TITLES = {"yowza": "Yowza!", "altavisor": "AltaVisor", "askreeves": "Ask Reeves", "orinoco": "Orinoco.com",
               "ubid": "uBid", "etoyz": "eToyz", "petz": "Petz.com", "geohoods": "GeoHoods",
               "hamstershuffle": "Hamster Shuffle", "dashdot": "Dashdot", "snapster": "Snapster", "cnm": "CNM Interactive"}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]

TAB_SUB = {
    "welcome": [("HOT 100", "hot100.html"), ("BOOKS", "books.html"), ("MUSIC", "music.html"),
                ("VIDEO", "video.html"), ("e-CARDS", "ecards.html"), ("WISH LISTS", "wishlist.html"),
                ("YOUR ACCOUNT", "account.html")],
    "books": [("SEARCH", "search.html?index=books"), ("BROWSE SUBJECTS", "books.html#subjects"),
              ("BESTSELLERS", "hot100.html"), ("COMPUTERS", "subjects/comp.html"),
              ("BUSINESS", "subjects/biz.html"), ("KIDS", "subjects/kids.html")],
    "music": [("TOP SELLERS", "music.html"), ("SEARCH", "search.html?index=music"), ("CLASSICAL? SOON", "help.html#soon")],
    "video": [("DVD &amp; VHS TOP SELLERS", "video.html"), ("SEARCH", "search.html?index=video")],
    "toys": [("TOYS FOR GROWN-UPS", "toys.html"), ("THE BIG TOY STORE", "../etoyz/index.html")],
    "auctions": [("TODAY'S AUCTIONS", "auctions.html"), ("ALL AUCTIONS AT uBID", "../ubid/index.html")],
    "ecards": [("SEND A CARD", "ecards.html"), ("HELP", "help.html")],
}


# ======================================================================= catalog
def isbn10(rnd):
    while True:
        digits = [0] + [rnd.randint(0, 9) for _ in range(8)]
        s = sum((i + 1) * d for i, d in enumerate(digits)) % 11
        if s < 10:
            return "".join(map(str, digits)) + str(s)


def parse(block):
    out = []
    for line in block.strip().splitlines():
        line = line.strip()
        if line:
            out.append(line.split("|"))
    return out


TRACK_A = ["Midnight", "Velvet", "Electric", "Lonely", "Dancing", "Broken", "Summer", "Cosmic", "Paper",
           "Neon", "Silver", "Crazy", "Sweet", "Rocket", "Ocean", "Last", "Secret", "Little"]
TRACK_B = ["Highway", "Heart", "Pager", "Moon", "Radio", "Rain", "Kiss", "Girl", "Train", "Fire", "Angel",
           "Dream", "Party", "Telephone", "Groove", "Sunrise", "Mystery", "Millennium"]
LABELS = ["Cartwheel Records", "Big Kahuna Music", "Lava Lamp Records", "Blue Parrot", "Mighty Lungs",
          "Sidewalk Sound"]


def build_catalog():
    rnd = random.Random(1999)
    items = []
    hits = {"Penelope Pike and the Cellar of Whispers", "Who Ate My Bagel?", "The Grapefruit Protocol",
            "Tuesdays with Mortimer", "The Ninth Juror", "The Readers' Circle", "Y2K and You: A Survival Handbook for the Digital Apocalypse",
            "The Dot-Com Millionaire Next Door", "Penelope Pike and the Prisoner of Azkharim", "Chicken Noodle Soup for the Soul",
            "Men Are from Mars Bars, Women Are from Venus Flytraps", "The Partner's Partner", "Dow 40,000: Why the Market Can Only Go Up",
            "Memoirs of a Tea Hostess", "Goodnight Mouse", "Teach Yourself Web Pages in 21 Minutes"}
    preorder = {"The Wheel of Weather, Book Nine", "Foundation's Basement"}
    for code, _name in D.SUBJECTS:
        for title, author, blurb in parse(D.BOOKS[code]):
            it = {"kind": "book", "title": title, "author": author, "subj": code, "blurb": blurb,
                  "code": isbn10(rnd), "hit": title in hits, "preorder": title in preorder}
            if code == "comp":
                it["binding"] = rnd.choice(["Paperback", "Paperback", "Paperback - Book &amp; CD-ROM"])
                lst = rnd.choice([2499, 2999, 3499, 3999, 4499, 4999])
                it["pages"] = rnd.randint(280, 1412)
            elif code == "kids":
                it["binding"] = rnd.choice(["Hardcover", "Board book", "Paperback", "Library Binding"])
                lst = rnd.choice([595, 795, 1495, 1595, 1695]) if it["binding"] != "Hardcover" else rnd.choice([1495, 1595, 1795])
                it["pages"] = rnd.randint(24, 320)
            elif code in ("rom", "myst", "scifi") and rnd.random() < .45:
                it["binding"] = "Mass Market Paperback"
                lst = rnd.choice([599, 699, 799])
                it["pages"] = rnd.randint(310, 520)
            elif code == "ref":
                it["binding"] = rnd.choice(["Hardcover", "Paperback"])
                lst = rnd.choice([1295, 1995, 2995, 3500, 4500])
                it["pages"] = rnd.randint(200, 1600)
            else:
                it["binding"] = rnd.choice(["Hardcover", "Hardcover", "Paperback"])
                lst = rnd.choice([2195, 2400, 2495, 2595, 2695, 2795]) if it["binding"] == "Hardcover" else rnd.choice([1200, 1295, 1395, 1495, 1600])
                it["pages"] = rnd.randint(160, 640)
            it["list"] = lst
            items.append(it)
    for kind, block, subj in (("music", D.MUSIC, "music"), ("video", D.VIDEO, "video")):
        for n, (title, author, blurb) in enumerate(parse(block)):
            it = {"kind": kind, "title": title, "author": author, "subj": subj, "blurb": blurb,
                  "code": "B00000%s%03d" % ("M" if kind == "music" else "V", n + 1), "hit": n < 4, "preorder": False}
            if kind == "music":
                it["binding"] = "Audio CD"
                it["list"] = rnd.choice([1398, 1698, 1798])
                it["label"] = rnd.choice(LABELS)
                trs = []
                for k in range(rnd.randint(10, 14)):
                    trs.append("%s %s" % (rnd.choice(TRACK_A), rnd.choice(TRACK_B)))
                it["tracks"] = trs
            else:
                it["binding"] = rnd.choice(["DVD", "VHS Tape"]) if n else "DVD"
                it["list"] = 2498 if it["binding"] == "DVD" else rnd.choice([1498, 1998, 2298])
                it["rating"] = rnd.choice(["PG", "PG-13", "R", "G"]) if "Toy" not in title else "G"
                it["runtime"] = rnd.randint(81, 194)
            items.append(it)
    # sales rank: the hits first, then everybody else
    books = [i for i in items if i["kind"] == "book"]
    rnd.shuffle(books)
    books.sort(key=lambda i: 0 if i["hit"] else 1)
    for r, it in enumerate(books):
        it["rank"] = r + 1 if r < 100 else rnd.randint(140, 98000)
    for kind in ("music", "video"):
        for r, it in enumerate([i for i in items if i["kind"] == kind]):
            it["rank"] = r + 1
    for it in items:
        lst = it["list"]
        if it["kind"] != "book":
            disc = 30 if it["rank"] <= 4 else 20
        elif it["rank"] <= 25 and it["binding"] == "Hardcover":
            disc = 50 if it["rank"] <= 5 else 40
        elif it["rank"] <= 100:
            disc = 30 if it["binding"] == "Hardcover" else 20
        elif lst >= 2000:
            disc = 20
        elif it["binding"] == "Mass Market Paperback":
            disc = 0
        else:
            disc = 10
        it["disc"] = disc
        it["price"] = int(round(lst * (100 - disc) / 100.0))
        if it["preorder"]:
            it["avail"] = "Not yet published -- reserve your copy now and we'll ship it the day it arrives."
        elif it["rank"] <= 100 or it["kind"] != "book":
            it["avail"] = "Usually ships within 24 hours."
        else:
            it["avail"] = rnd.choice(["Usually ships within 24 hours.", "Usually ships within 2-3 days.",
                                      "Usually ships within 2-3 days.", "Usually ships within 1-2 weeks.",
                                      "Usually ships within 4-6 weeks.", "Special order: usually ships within 4-6 weeks."])
        if it["preorder"]:
            it["pubdate"] = "November 1999"
        else:
            m = rnd.randint(0, 9) if rnd.random() < .7 else rnd.randint(0, 11)
            y = 1999 if rnd.random() < .7 else rnd.choice([1996, 1997, 1998])
            it["pubdate"] = "%s %d" % (MONTHS[m], y)
        it["publisher"] = rnd.choice(D.PUBLISHERS) if it["kind"] == "book" else it.get("label", "Starlight Home Video")
        it["reviews"] = make_reviews(rnd, it)
    # customers who bought this also bought
    for it in items:
        same = [o for o in items if o is not it and o["kind"] == it["kind"] and o["subj"] == it["subj"]]
        other = [o for o in items if o is not it and o["kind"] == "book" and o["rank"] <= 40]
        picks = rnd.sample(same, min(3, len(same))) + rnd.sample([o for o in other if o not in same], 2)
        it["also"] = picks
    return items


def make_reviews(rnd, it):
    n = rnd.choice([0, 1, 2, 2, 3, 3, 4, 5, 6, 8]) + (5 if it["hit"] else 0)
    quality = rnd.choice([3.4, 3.9, 4.2, 4.5, 4.7]) + (0.3 if it["hit"] else 0)
    out = []
    used = set()
    for k in range(n):
        st = int(round(min(5, max(1, rnd.gauss(quality, 1.0)))))
        tpool = [t for t in D.REVIEW_TITLES[st] if t not in used] or D.REVIEW_TITLES[st]
        bpool = [b for b in D.REVIEW_BODIES[st] if b not in used] or D.REVIEW_BODIES[st]
        title = rnd.choice(tpool)
        raw = rnd.choice(bpool)
        used.add(title)
        used.add(raw)
        body = raw.replace("{a}", it["author"].split(",")[0])
        who = rnd.choice(D.REVIEWERS)
        place = rnd.choice(D.REVIEW_PLACES)
        m = rnd.randint(0, 9)
        date = "%s %d, 1999" % (MONTHS[m], rnd.randint(1, 28))
        total = rnd.randint(0, 40)
        yes = int(total * (rnd.random() * .5 + (.5 if st >= 4 else .2)))
        out.append({"stars": st, "title": title, "body": body, "who": who, "place": place, "date": date,
                    "yes": yes, "total": total, "id": "%s-%d" % (it["code"], k + 1)})
    return out


def avg_rating(it):
    r = it["reviews"]
    if not r:
        return None
    a = sum(x["stars"] for x in r) / float(len(r))
    return round(a * 2) / 2.0


def stars_img(P, v):
    if v is None:
        return ""
    t = int(round(v * 10))
    return '<IMG SRC="%simages/stars/stars-%d-%d.gif" WIDTH=64 HEIGHT=13 BORDER=0 ALT="%s out of 5 stars">' % (P, t // 10, t % 10, ("%g" % v))


def money(c):
    return "$%s.%02d" % ("{:,}".format(c // 100), c % 100)


# ======================================================================= page chrome
TABSIZES = {}


def page(path, title, tab, body, scripts=True, onload=""):
    depth = path.count("/")
    P = "../" * depth
    html = []
    html.append('<HTML>\n<HEAD>\n<TITLE>Orinoco.com: %s</TITLE>\n' % title)
    html.append('<META NAME="description" CONTENT="Orinoco.com, Earth\'s Biggest Bookstore: millions of titles, invented daily.">\n')
    html.append('<SCRIPT LANGUAGE="JavaScript">var P = "%s";</SCRIPT>\n' % P)
    if scripts:
        html.append('<SCRIPT LANGUAGE="JavaScript1.2" SRC="%sjs/books.js"></SCRIPT>\n' % P)
        html.append('<SCRIPT LANGUAGE="JavaScript1.2" SRC="%sjs/orinoco.js"></SCRIPT>\n' % P)
    html.append('</HEAD>\n')
    html.append('<BODY BGCOLOR="#FFFFFF" TEXT="#000000" LINK="#003399" VLINK="#996633" ALINK="#FF9900"%s>\n'
                % (' onLoad="%s"' % onload if onload else ""))
    html.append(header(P, tab))
    html.append(body.replace("{P}", P))
    html.append(footer(P))
    html.append("</BODY>\n</HTML>\n")
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="latin-1", errors="xmlcharrefreplace") as f:
        f.write("".join(html))
    PAGES.append(path)


PAGES = []


def header(P, tab):
    from gfx import TABS
    color = dict((k, c) for k, _l, c in TABS)[tab]
    t = []
    t.append('<TABLE WIDTH=760 BORDER=0 CELLPADDING=0 CELLSPACING=0>\n<TR>\n')
    t.append('<TD ROWSPAN=2 VALIGN=BOTTOM WIDTH=176><A HREF="%sindex.html"><IMG SRC="%simages/logo.gif" WIDTH=172 HEIGHT=58 BORDER=0 ALT="Orinoco.com"></A></TD>\n' % (P, P))
    t.append('<TD ALIGN=RIGHT VALIGN=TOP><FONT FACE="%s" SIZE=-2><SCRIPT LANGUAGE="JavaScript">writeCartLine();</SCRIPT>&nbsp;</FONT>' % FONT)
    t.append('<A HREF="%scart.html"><IMG SRC="%simages/btn_cart.gif" WIDTH=80 HEIGHT=19 BORDER=0 ALT="View Cart"></A>' % (P, P))
    t.append('<A HREF="%saccount.html"><IMG SRC="%simages/btn_account.gif" WIDTH=103 HEIGHT=19 BORDER=0 ALT="Your Account"></A>' % (P, P))
    t.append('<A HREF="%shelp.html"><IMG SRC="%simages/btn_help.gif" WIDTH=53 HEIGHT=19 BORDER=0 ALT="Help"></A></TD>\n</TR>\n' % (P, P))
    t.append('<TR><TD VALIGN=BOTTOM NOWRAP>')
    for key, label, _c in TABS:
        on = key == tab
        w, h = TABSIZES[key][1 if on else 0]
        href = {"welcome": "index.html", "books": "books.html", "music": "music.html", "video": "video.html",
                "toys": "toys.html", "auctions": "auctions.html", "ecards": "ecards.html"}[key]
        t.append('<A HREF="%s%s"><IMG SRC="%simages/tabs/%s_%s.gif" WIDTH=%d HEIGHT=%d BORDER=0 ALT="%s"></A>'
                 % (P, href, P, key, "on" if on else "off", w, h, label.replace("&", "&amp;")))
    t.append('</TD></TR>\n')
    t.append('<TR><TD COLSPAN=2 BGCOLOR="%s" HEIGHT=20 ALIGN=CENTER><FONT FACE="%s" SIZE=-2 COLOR="#FFFFFF">' % (color, FONT))
    links = []
    for label, href in TAB_SUB[tab]:
        links.append('<A HREF="%s%s"><FONT COLOR="#FFFFFF"><B>%s</B></FONT></A>' % (P, href, label))
    t.append(" &nbsp;|&nbsp; ".join(links))
    t.append('</FONT></TD></TR>\n</TABLE>\n')
    return "".join(t)


def footer(P):
    i = RING.index("orinoco")
    prev, nxt = RING[i - 1], RING[(i + 1) % len(RING)]
    links = [("Orinoco.com Home", "index.html"), ("Books", "books.html"), ("Music", "music.html"),
             ("Video", "video.html"), ("Toys &amp; Games", "toys.html"), ("Auctions", "auctions.html"),
             ("e-Cards", "ecards.html"), ("Hot 100", "hot100.html"), ("Your Account", "account.html"),
             ("Shopping Cart", "cart.html"), ("Help", "help.html")]
    f = ['<TABLE WIDTH=760 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD ALIGN=CENTER>\n<BR><HR NOSHADE SIZE=1 COLOR="#CCCC99">\n']
    f.append('<FONT FACE="%s" SIZE=-2>' % FONT)
    f.append(" | ".join('<A HREF="%s%s">%s</A>' % (P, h, l) for l, h in links))
    f.append('<BR><BR><A HREF="%shelp.html#privacy">Our Privacy Pledge</A> | <A HREF="%shelp.html#safe">Safe Shopping Pledge</A> | <A HREF="%shelp.html#about">About Orinoco.com</A>' % (P, P, P))
    f.append('<BR><BR>Copyright &copy; 1996-1999, Orinoco.com, Inc. All rights reserved. Served by a KoldFusion 4.5 cluster from Gibson Mainframe Co.<BR>')
    f.append('<I>A 1999 Web parody. No rivers, retailers or authors were harmed; every book here is invented.</I></FONT>\n')
    f.append('<BR><BR><CENTER><TABLE BORDER=2 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#C0C0C0"><TR><TD ALIGN=CENTER NOWRAP><FONT FACE="Arial, Helvetica" SIZE=1>\n')
    f.append('<A HREF="%s../%s/index.html">&lt;&lt; Prev</A> | ' % (P, prev))
    f.append('<A HREF="%s../../web1999/index.html" onClick="return ringRandom()">Random</A> | ' % P)
    f.append('<B><A HREF="%s../../web1999/index.html">The 1999 Web Ring</A></B> | ' % P)
    f.append('<A HREF="%s../%s/index.html">Next &gt;&gt;</A>\n' % (P, nxt))
    f.append('</FONT></TD></TR></TABLE></CENTER>\n</TD></TR></TABLE>\n')
    return "".join(f)


def box(title, inner, width=171, color="#708090", inbg="#FFFFFF", tcolor="#FFFFFF"):
    return ('<TABLE BORDER=0 WIDTH=%d CELLPADDING=1 CELLSPACING=0 BGCOLOR="%s"><TR><TD>'
            '<TABLE BORDER=0 WIDTH="100%%" CELLPADDING=4 CELLSPACING=0>'
            '<TR><TD BGCOLOR="%s"><FONT FACE="%s" SIZE=-1 COLOR="%s"><B>%s</B></FONT></TD></TR>'
            '<TR><TD BGCOLOR="%s"><FONT FACE="%s" SIZE=-1>%s</FONT></TD></TR></TABLE></TD></TR></TABLE>\n'
            % (width, color, color, FONT, tcolor, title, inbg, FONT, inner))


def search_box(default="blended"):
    opts = [("blended", "All Products"), ("books", "Books"), ("music", "Popular Music"), ("video", "Video"),
            ("toys", "Toys &amp; Games"), ("auctions", "Auctions")]
    o = "".join('<OPTION VALUE="%s"%s>%s' % (v, " SELECTED" if v == default else "", l) for v, l in opts)
    inner = ('<FORM NAME="sf" METHOD=GET ACTION="{P}search.html">'
             '<FONT SIZE=-2>Search:</FONT><BR><SELECT NAME="index">%s</SELECT><BR>'
             '<INPUT TYPE="text" NAME="keywords" SIZE=12> '
             '<INPUT TYPE="image" SRC="{P}images/go.gif" WIDTH=21 HEIGHT=21 BORDER=0 ALIGN=ABSMIDDLE ALT="Go!" NAME="Go"></FORM>' % o)
    return box("Search Orinoco.com", inner, inbg="#EEEECC")


def browse_box():
    rows = []
    rows.append('<B><A HREF="{P}books.html">Books</A></B><BR><FONT SIZE=-2>' +
                ", ".join('<A HREF="{P}subjects/%s.html">%s</A>' % (c, n.split(",")[0].split(" &")[0]) for c, n in D.SUBJECTS[:5]) + "...</FONT><BR>")
    rows.append('<B><A HREF="{P}music.html">Music</A></B><BR><FONT SIZE=-2><A HREF="{P}music.html">Top Sellers</A>, <A HREF="{P}search.html?index=music">Search</A>...</FONT><BR>')
    rows.append('<B><A HREF="{P}video.html">Video</A></B><BR><FONT SIZE=-2><A HREF="{P}video.html">DVDs</A>, <A HREF="{P}video.html">Top Sellers</A>...</FONT><BR>')
    rows.append('<B><A HREF="{P}toys.html">Toys &amp; Games</A></B><BR><FONT SIZE=-2><A HREF="{P}toys.html">Toys for Grown-ups</A>, <A HREF="{P}../etoyz/index.html">eToyz</A>...</FONT><BR>')
    rows.append('<B><A HREF="{P}auctions.html">Auctions</A></B><BR><FONT SIZE=-2><A HREF="{P}auctions.html">Collectibles</A>, <A HREF="{P}../ubid/index.html">uBid</A>...</FONT><BR>')
    rows.append('<B><A HREF="{P}ecards.html">Free e-Cards</A></B><BR><FONT SIZE=-2><A HREF="{P}ecards.html">Birthday</A>, <A HREF="{P}ecards.html">Y2K</A>, <A HREF="{P}ecards.html">Thanks</A>...</FONT>')
    inner = "".join("&#149; " + r for r in rows)
    more = ('<BR><BR><B>Gift Services</B><BR>&#149; <A HREF="{P}wishlist.html">Wish Lists</A><BR>&#149; <A HREF="{P}ecards.html">e-Cards</A>'
            '<BR><BR><B>Need Help?</B><BR>&#149; <A HREF="{P}help.html">Help Desk</A><BR>&#149; <A HREF="{P}help.html#shipping">Shipping Rates</A>'
            '<BR>&#149; <A HREF="{P}help.html#privacy">Privacy Pledge</A>'
            '<BR><BR><B>Your Recent History</B><BR><SCRIPT LANGUAGE="JavaScript">writeRecent();</SCRIPT>')
    return box("Browse", inner + more, inbg="#FFFFFF")


def subject_box(cur=None):
    rows = []
    for c, n in D.SUBJECTS:
        if c == cur:
            rows.append("<B>%s</B>" % n)
        else:
            rows.append('<A HREF="{P}subjects/%s.html">%s</A>' % (c, n))
    inner = "<FONT SIZE=-2>" + "<BR>".join(rows) + "</FONT>"
    inner += ('<BR><BR><FONT SIZE=-2><B>Your Recent History</B><BR></FONT><SCRIPT LANGUAGE="JavaScript">writeRecent();</SCRIPT>')
    return box("Browse Subjects", inner, inbg="#FFFFFF")


def twocol(left, center, right=None):
    s = '<TABLE WIDTH=760 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR>\n'
    s += '<TD WIDTH=171 VALIGN=TOP><BR>%s</TD>\n<TD WIDTH=12>&nbsp;</TD>\n' % left
    s += '<TD VALIGN=TOP><BR><FONT FACE="%s" SIZE=-1>%s</FONT></TD>\n' % (FONT, center)
    if right:
        s += '<TD WIDTH=12>&nbsp;</TD><TD WIDTH=194 VALIGN=TOP><BR>%s</TD>\n' % right
    s += '</TR></TABLE>\n'
    return s


def h_orange(text, size=""):
    return '<FONT FACE="%s" COLOR="#CC6600"%s><B>%s</B></FONT>' % (FONT, (" SIZE=%s" % size) if size else "", text)


def link_item(it, P="{P}"):
    return '<A HREF="%sdetail/%s.html">%s</A>' % (P, it["code"], it["title"])


def by(it):
    return {"book": "by ", "music": "", "video": "Starring "}[it["kind"]] + it["author"]


def cover_img(it, small=True, P="{P}", align=""):
    w, h = SIZES[it["kind"]]
    if small:
        w, h = w // 2, h // 2
    return '<IMG SRC="%simages/covers/%s%s.gif" WIDTH=%d HEIGHT=%d BORDER=0%s ALT="%s">' % (
        P, it["code"], "_s" if small else "", w, h, (" ALIGN=%s" % align) if align else "", it["title"].replace('"', "&quot;"))


SIZES = {"book": (120, 180), "music": (120, 120), "video": (110, 160)}


def price_line(it):
    s = '<FONT COLOR="#990000">%s</FONT>' % money(it["price"])
    if it["disc"]:
        s += ' <FONT SIZE=-2>(Save %d%%)</FONT>' % it["disc"]
    return s


# ======================================================================= pages
def build_home(items):
    books = sorted([i for i in items if i["kind"] == "book"], key=lambda i: i["rank"])
    music = sorted([i for i in items if i["kind"] == "music"], key=lambda i: i["rank"])
    video = sorted([i for i in items if i["kind"] == "video"], key=lambda i: i["rank"])
    byt = dict((i["title"], i) for i in items)
    left = search_box() + "<BR>" + browse_box()

    def hot_list(lst, more_href, more_label, n=3):
        s = ""
        for it in lst[:n]:
            s += ('<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD VALIGN=TOP>%s</TD><TD VALIGN=TOP><FONT FACE="%s" SIZE=-2><B>%s</B><BR>%s<BR>%s</FONT></TD></TR></TABLE>'
                  % ('<A HREF="{P}detail/%s.html">%s</A>' % (it["code"], cover_img(it)), FONT, link_item(it), by(it), price_line(it)))
        s += '<FONT SIZE=-2><IMG SRC="{P}images/arrow.gif" WIDTH=12 HEIGHT=11> <A HREF="{P}%s">%s</A></FONT>' % (more_href, more_label)
        return s
    right = box('<FONT COLOR="#000000">Orinoco.com 100 Hot Books</FONT><BR><FONT SIZE=-2 COLOR="#666633">Updated hourly, more or less</FONT>',
                hot_list(books, "hot100.html", "More Hot Books"), width=194, color="#CCCC99")
    right += "<BR>" + box('<FONT COLOR="#000000">Music Top Sellers</FONT>', hot_list(music, "music.html", "More Music Top Sellers"), width=194, color="#CCCC99")
    right += "<BR>" + box('<FONT COLOR="#000000">DVD &amp; Video Top Sellers</FONT>', hot_list(video, "video.html", "More Video Top Sellers"), width=194, color="#CCCC99")

    feat = byt["The Readers' Circle"]
    pike = byt["Penelope Pike and the Cellar of Whispers"]
    y2k = byt["Y2K and You: A Survival Handbook for the Digital Apocalypse"]
    matr = byt["The Matrices"]
    c = []
    c.append('<FONT SIZE=-2 COLOR="#666666"><SCRIPT LANGUAGE="JavaScript">document.write(longDate(new Date()));</SCRIPT></FONT><BR><BR>')
    c.append('<SCRIPT LANGUAGE="JavaScript">writeHello();</SCRIPT><BR><BR>')
    c.append('<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%%" BGCOLOR="#EEEECC"><TR><TD><IMG SRC="{P}images/giftbox.gif" WIDTH=44 HEIGHT=47 ALIGN=LEFT HSPACE=4>'
             '<FONT FACE="%s" SIZE=-1><B>Make the holidays painless:</B> start an Orinoco.com <A HREF="{P}wishlist.html">Wish List</A>, '
             'and your relatives will finally stop buying you socks. Or send a free <A HREF="{P}ecards.html">e-Card</A> -- no stamp required.</FONT></TD></TR></TABLE><BR>' % FONT)

    def feature(section, href, headline, it, text, golabel):
        return ('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH="100%%"><TR><TD BGCOLOR="#CCCC99"><FONT FACE="%s" SIZE=-1><B>&nbsp;%s</B></FONT></TD></TR></TABLE>'
                '<FONT FACE="%s" SIZE=+1 COLOR="#CC6600"><B>%s</B></FONT><BR>'
                '<A HREF="{P}detail/%s.html">%s</A>'
                '<FONT FACE="%s" SIZE=-1>%s <IMG SRC="{P}images/arrow.gif" WIDTH=12 HEIGHT=11> <A HREF="{P}%s">%s</A></FONT><BR CLEAR=ALL><BR>'
                % (FONT, section, FONT, headline, it["code"], cover_img(it, align="LEFT").replace("BORDER=0", "BORDER=0 HSPACE=7 VSPACE=3"),
                   FONT, text, href, golabel))
    c.append(feature("In Books", "books.html", "A Club You'll Want to Join", feat,
                     'Five neighbors, one battered folding table and a new book every month: in <A HREF="{P}detail/%s.html"><I>%s</I></A>, '
                     '%s turns a small-town reading group into a novel about everything a book can stir up. Our editors passed '
                     'their copy around the office until the spine gave out. %s' % (feat["code"], feat["title"], feat["author"], stars_img("{P}", avg_rating(feat))),
                     "Go to Books"))
    c.append(feature("In Children's Books", "subjects/kids.html", "The Owl Post Has Arrived", pike,
                     'Grown-ups on commuter trains are hiding it behind newspapers. <A HREF="{P}detail/%s.html"><I>%s</I></A> is the '
                     'boarding-school fantasy that turned a generation of reluctant readers into flashlight-under-the-covers readers. '
                     'Save %d%% -- and pick up the third book while you are at it.' % (pike["code"], pike["title"], pike["disc"]),
                     "Go to Children's Books"))
    c.append(feature("In Computers &amp; Internet", "subjects/comp.html", "Is Your Toaster Y2K-Compliant?", y2k,
                     'With fewer than a hundred days left before the big rollover, <A HREF="{P}detail/%s.html"><I>%s</I></A> '
                     'has become our fastest-selling handbook. Stock up on candles, then stock up on reading.' % (y2k["code"], y2k["title"].split(":")[0]),
                     "Go to Computers &amp; Internet"))
    c.append(feature("In Video", "video.html", "Red Pill or Blue Pill?", matr,
                     'The bullet-dodging, coat-swishing hit of the year arrives on DVD. <A HREF="{P}detail/%s.html"><I>%s</I></A> '
                     'is the disc that sold a million DVD players. %s.' % (matr["code"], matr["title"], price_line(matr)),
                     "Go to Video"))
    c.append('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH="100%%"><TR><TD BGCOLOR="#CCCC99"><FONT FACE="%s" SIZE=-1><B>&nbsp;In Toys &amp; Games and Auctions</B></FONT></TD></TR></TABLE>' % FONT)
    c.append('<FONT FACE="%s" SIZE=-1>Looking for a Furby, a Pok&eacute;mon starter deck or a slightly used Zip drive? Our neighbors are '
             'open all night: browse the toy chest at <A HREF="{P}../etoyz/index.html"><B>eToyz</B></A>, or bid on 1999\'s most '
             'collectible collectibles at <A HREF="{P}../ubid/index.html"><B>uBid</B></A>. <IMG SRC="{P}images/arrow.gif" WIDTH=12 HEIGHT=11> '
             '<A HREF="{P}toys.html">Go to Toys &amp; Games</A></FONT><BR>' % FONT)
    page("index.html", "Earth's Biggest Bookstore", "welcome", twocol(left, "".join(c), right))


def build_books(items):
    books = sorted([i for i in items if i["kind"] == "book"], key=lambda i: i["rank"])
    left = search_box("books") + "<BR>" + subject_box()
    c = []
    c.append('<FONT FACE="%s" SIZE=+1><B>Welcome to Books</B></FONT><BR><FONT SIZE=-1>Earth\'s Biggest Bookstore has %d titles in stock, '
             'every one of them invented by somebody with a very active imagination.</FONT><BR><BR>' % (FONT, len(books)))
    c.append(h_orange("Bestsellers This Week") + "<BR>")
    c.append('<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0><TR>')
    for it in books[:4]:
        c.append('<TD VALIGN=TOP ALIGN=CENTER WIDTH=95><A HREF="{P}detail/%s.html">%s</A><BR><FONT FACE="%s" SIZE=-2>%s<BR>%s</FONT></TD>'
                 % (it["code"], cover_img(it), FONT, link_item(it), price_line(it)))
    c.append('</TR></TABLE><FONT SIZE=-2><IMG SRC="{P}images/arrow.gif" WIDTH=12 HEIGHT=11> <A HREF="{P}hot100.html">See the whole Hot 100</A></FONT><BR><BR>')
    c.append('<A NAME="subjects"></A>' + h_orange("Browse Subjects") + "<BR>")
    c.append('<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0 WIDTH="100%"><TR>')
    for n, (code, name) in enumerate(D.SUBJECTS):
        if n and n % 2 == 0:
            c.append("</TR><TR>")
        top = [i for i in books if i["subj"] == code][:2]
        c.append('<TD VALIGN=TOP WIDTH="50%%"><FONT FACE="%s" SIZE=-1><B><A HREF="{P}subjects/%s.html">%s</A></B><BR><FONT SIZE=-2>%s</FONT></FONT></TD>'
                 % (FONT, code, name, "<BR>".join("&#149; " + link_item(i) for i in top)))
    c.append("</TR></TABLE><BR>")
    c.append(h_orange("Coming Soon: Reserve Yours Today") + "<BR>")
    for it in [i for i in books if i["preorder"]]:
        c.append('&#149; %s, %s -- %s<BR>' % (link_item(it), by(it), it["avail"]))
    page("books.html", "Books", "books", twocol(left, "".join(c)))


def list_rows(lst, numbered=False):
    s = ['<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%">']
    for n, it in enumerate(lst):
        bg = "#FFFFFF" if n % 2 == 0 else "#F4F4E8"
        s.append('<TR BGCOLOR="%s">' % bg)
        if numbered:
            s.append('<TD VALIGN=TOP ALIGN=RIGHT><FONT FACE="%s" SIZE=+1 COLOR="#CC6600"><B>%d.</B></FONT></TD>' % (FONT, n + 1))
        s.append('<TD VALIGN=TOP><A HREF="{P}detail/%s.html">%s</A></TD>' % (it["code"], cover_img(it)))
        s.append('<TD VALIGN=TOP><FONT FACE="%s" SIZE=-1><B>%s</B><BR>%s<BR><FONT SIZE=-2>%s (%s)</FONT><BR>'
                 'List Price: %s &nbsp; Our Price: <B>%s</B><BR>%s <FONT SIZE=-2>%s</FONT></FONT></TD>'
                 % (FONT, link_item(it), by(it), it["binding"], it["pubdate"], money(it["list"]), price_line(it),
                    stars_img("{P}", avg_rating(it)), it["avail"]))
        s.append('</TR>')
    s.append('</TABLE>')
    return "".join(s)


def build_subjects(items):
    for code, name in D.SUBJECTS:
        lst = sorted([i for i in items if i["subj"] == code], key=lambda i: i["rank"])
        left = search_box("books") + "<BR>" + subject_box(code)
        c = '<FONT FACE="%s" SIZE=+1><B>%s</B></FONT><BR><FONT SIZE=-2><A HREF="{P}books.html">Books</A> &gt; Subjects &gt; %s</FONT><BR><BR>' % (FONT, name, name)
        c += h_orange("%d titles, sorted by bestselling" % len(lst)) + "<BR>" + list_rows(lst)
        page("subjects/%s.html" % code, name, "books", twocol(left, c))


def build_hot100(items):
    books = sorted([i for i in items if i["kind"] == "book"], key=lambda i: i["rank"])[:100]
    left = search_box("books") + "<BR>" + subject_box()
    c = '<IMG SRC="{P}images/hot100.gif" WIDTH=40 HEIGHT=40 ALIGN=LEFT><FONT FACE="%s" SIZE=+1><B>The Orinoco.com Hot 100</B></FONT><BR>' % FONT
    c += ('<FONT SIZE=-1>Our 100 best-selling books, recalculated every hour by a room full of very tired abacus operators. '
          'Updated <SCRIPT LANGUAGE="JavaScript">var d=new Date(); document.write(longDate(d) + " at " + (d.getHours()%12==0?12:d.getHours()%12) + ":00 " + (d.getHours()<12?"a.m.":"p.m.") + " Pacific");</SCRIPT>.</FONT><BR CLEAR=ALL><BR>')
    c += list_rows(books, numbered=True)
    page("hot100.html", "The Hot 100", "books", twocol(left, c))


def build_detail(items):
    for it in items:
        tab = {"book": "books", "music": "music", "video": "video"}[it["kind"]]
        left = search_box({"book": "books", "music": "music", "video": "video"}[it["kind"]]) + "<BR>" + (
            subject_box(it["subj"]) if it["kind"] == "book" else browse_box())
        avg = avg_rating(it)
        c = []
        c.append('<SCRIPT LANGUAGE="JavaScript">noteViewed("%s");</SCRIPT>' % it["code"])
        c.append('<FONT FACE="%s" SIZE=+1><B>%s</B></FONT><BR>' % (FONT, it["title"]))
        if it["kind"] == "book":
            c.append('<FONT FACE="%s" SIZE=-1>by <A HREF="{P}search.html?index=books&keywords=%s">%s</A></FONT><BR><BR>'
                     % (FONT, it["author"].split(",")[0].replace(" ", "+").replace("&", "%26"), it["author"]))
        elif it["kind"] == "music":
            c.append('<FONT FACE="%s" SIZE=-1><A HREF="{P}search.html?index=music&keywords=%s">%s</A></FONT><BR><BR>' % (FONT, it["author"].replace(" ", "+"), it["author"]))
        else:
            c.append('<FONT FACE="%s" SIZE=-1>Starring: %s</FONT><BR><BR>' % (FONT, it["author"]))
        c.append('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH="100%"><TR><TD VALIGN=TOP WIDTH=130>')
        c.append(cover_img(it, small=False))
        c.append('</TD><TD WIDTH=10>&nbsp;</TD><TD VALIGN=TOP><FONT FACE="%s" SIZE=-1>' % FONT)
        c.append('<B>List Price:</B> %s<BR>' % money(it["list"]))
        c.append('<B>Our Price: <FONT COLOR="#990000">%s</FONT></B><BR>' % money(it["price"]))
        if it["disc"]:
            c.append('<B>You Save:</B> <FONT COLOR="#990000">%s (%d%%)</FONT><BR>' % (money(it["list"] - it["price"]), it["disc"]))
        c.append('<BR><B>Availability:</B> %s<BR><BR>' % it["avail"])
        if it["kind"] == "book":
            c.append('<FONT SIZE=-2>%s - %d pages (%s)<BR>%s; ISBN: %s</FONT><BR><BR>' % (it["binding"], it["pages"], it["pubdate"], it["publisher"], it["code"]))
        elif it["kind"] == "music":
            c.append('<FONT SIZE=-2>Audio CD (%s)<BR>Number of Discs: 1<BR>Label: %s; ASIN: %s</FONT><BR><BR>' % (it["pubdate"], it["publisher"], it["code"]))
        else:
            c.append('<FONT SIZE=-2>%s (%s)<BR>Rated: %s; Run Time: %d minutes<BR>%s; ASIN: %s</FONT><BR><BR>'
                     % (it["binding"], it["pubdate"], it["rating"], it["runtime"], it["publisher"], it["code"]))
        if avg is not None:
            c.append('<B>Average Customer Review:</B> %s Based on %d review%s. <A HREF="#reviews">Read them</A><BR>'
                     % (stars_img("{P}", avg), len(it["reviews"]), "" if len(it["reviews"]) == 1 else "s"))
        c.append('<FONT SIZE=-2><B>Orinoco.com Sales Rank:</B> %s</FONT>' % "{:,}".format(it["rank"]))
        c.append('</FONT></TD><TD WIDTH=10>&nbsp;</TD><TD VALIGN=TOP WIDTH=160>')
        buy = ('<CENTER><FORM NAME="buy" onSubmit="return cartAdd(\'%s\', 1)">'
               '<A HREF="{P}cart.html" onClick="return cartAdd(\'%s\', 1)"><IMG SRC="{P}images/btn_addcart.gif" WIDTH=142 HEIGHT=20 BORDER=0 ALT="Add to Shopping Cart"></A><BR>'
               '<FONT SIZE=-2>(you can always remove it later)</FONT><BR><BR>'
               '<A HREF="{P}account.html" onClick="return oneClick(\'%s\')"><IMG SRC="{P}images/btn_1click.gif" WIDTH=140 HEIGHT=20 BORDER=0 ALT="Buy now with 1-Click"></A><BR>'
               '<FONT SIZE=-2><SCRIPT LANGUAGE="JavaScript">if (oneClickOn() && userGet()) document.write("1-Click ordering is ON for " + esc(firstName()) + "."); '
               'else document.write("1-Click ordering is off. <A HREF=\\"" + P + "account.html\\">Turn it on</A>");</SCRIPT></FONT><BR><BR>'
               '<A HREF="{P}wishlist.html" onClick="return wishAdd(\'%s\')"><IMG SRC="{P}images/btn_wishlist.gif" WIDTH=106 HEIGHT=18 BORDER=0 ALT="Add to Wish List"></A>'
               '</FORM></CENTER>' % (it["code"], it["code"], it["code"], it["code"]))
        c.append(box('<FONT COLOR="#000000">Ready to buy?</FONT>', buy, width=160, color="#CCCC99", inbg="#FFFFF0"))
        c.append('<BR><FONT FACE="%s" SIZE=-2>Share your thoughts with other customers:<BR><IMG SRC="{P}images/arrow.gif" WIDTH=12 HEIGHT=11> <A HREF="{P}review.html?code=%s">Write an online review</A></FONT>' % (FONT, it["code"]))
        c.append('</TD></TR></TABLE><BR>')
        # also bought
        what = {"book": "book", "music": "CD", "video": "video"}[it["kind"]]
        c.append('<HR NOSHADE SIZE=1 COLOR="#CCCC99">' + h_orange("Customers who bought this %s also bought:" % what, "-1") + "<BR><FONT SIZE=-1>")
        for o in it["also"]:
            c.append('&#149; %s; %s<BR>' % (link_item(o), by(o)))
        c.append('</FONT><BR>')
        # editorial
        c.append('<HR NOSHADE SIZE=1 COLOR="#CCCC99">' + h_orange("Editorial Reviews", "-1") + "<BR>")
        c.append('<B>Orinoco.com</B><BR>%s %s<BR><BR>' % (it["blurb"], editorial_extra(it)))
        if it["kind"] == "music":
            c.append('<B>Track Listing</B><BR><FONT SIZE=-1>')
            for n, t in enumerate(it["tracks"]):
                c.append("%d. %s<BR>" % (n + 1, t))
            c.append("</FONT><BR>")
        # reviews
        c.append('<A NAME="reviews"></A><HR NOSHADE SIZE=1 COLOR="#CCCC99">' + h_orange("Customer Comments", "-1") + "<BR>")
        if avg is not None:
            c.append('<B>Average Customer Review:</B> %s<BR><B>Number of Reviews:</B> %d<BR>' % (stars_img("{P}", avg), len(it["reviews"])))
        else:
            c.append('No customer reviews yet. Be the first!<BR>')
        c.append('<IMG SRC="{P}images/arrow.gif" WIDTH=12 HEIGHT=11> <A HREF="{P}review.html?code=%s">Write an online review</A> and share your thoughts with other customers.<BR>' % it["code"])
        c.append('<SCRIPT LANGUAGE="JavaScript">writeMyReviews("%s");</SCRIPT>' % it["code"])
        for r in it["reviews"]:
            c.append('<P><SCRIPT LANGUAGE="JavaScript">writeHelpful("%s", %d, %d);</SCRIPT>' % (r["id"], r["yes"], r["total"]))
            c.append('%s <B>%s</B>, %s<BR>' % (stars_img("{P}", r["stars"]), r["title"], r["date"]))
            c.append('<B>Reviewer:</B> %s from %s<BR>%s<BR>' % (r["who"], r["place"], r["body"]))
            c.append('<FONT SIZE=-2>Was this review helpful to you? <A HREF="#reviews" onClick="return vote(\'%s\',\'y\')"><B>YES</B></A> '
                     '<A HREF="#reviews" onClick="return vote(\'%s\',\'n\')"><B>NO</B></A></FONT></P>' % (r["id"], r["id"]))
        page("detail/%s.html" % it["code"], it["title"], tab, twocol(left, "".join(c)))


EXTRA = [
    "It is the sort of %s our staff argue about at lunch, which is the highest compliment we know.",
    "Whether you read it in one gulp or a chapter a night, this %s rewards the attention.",
    "We predict this %s will turn up under a great many trees this December.",
    "Short of hiring the author to come read it aloud, this is the best way to experience the %s.",
    "Few %ss this year have generated as much mail to our editors -- nearly all of it enthusiastic.",
]


def editorial_extra(it):
    rnd = random.Random(it["code"])
    what = {"book": "book", "music": "album", "video": "film"}[it["kind"]]
    return rnd.choice(EXTRA) % what + " <I>--Orinoco.com staff</I>"


def build_shelf(items, kind, path, title, tab, intro):
    lst = sorted([i for i in items if i["kind"] == kind], key=lambda i: i["rank"])
    left = search_box(kind) + "<BR>" + browse_box()
    c = '<FONT FACE="%s" SIZE=+1><B>%s</B></FONT><BR><FONT SIZE=-1>%s</FONT><BR><BR>' % (FONT, title, intro)
    c += h_orange("Top Sellers") + "<BR>" + list_rows(lst, numbered=True)
    page(path, title, tab, twocol(left, c))


def build_static_pages(items):
    left = search_box() + "<BR>" + browse_box()
    # ------------------------------------------------------------ toys
    c = ('<FONT FACE="%s" SIZE=+1><B>Toys &amp; Games</B></FONT><BR><BR>'
         '<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 BGCOLOR="#FFF4DD" WIDTH="100%%"><TR><TD><FONT FACE="%s" SIZE=-1>'
         '<B>We stock the books; our friends stock the toys.</B> For dolls, robots, bikes and every stocking stuffer under the sun, '
         'head over to <A HREF="{P}../etoyz/index.html"><B>eToyz</B></A>, where the toy chest is open 24 hours a day and the '
         'holiday elves are already working double shifts.</FONT></TD></TR></TABLE><BR>' % (FONT, FONT))
    c += h_orange("Toys for Grown-ups (on our own shelves)") + "<BR><FONT SIZE=-1>"
    for it in sorted([i for i in items if i["subj"] in ("ref", "cook")], key=lambda i: i["rank"])[:6]:
        c += '&#149; %s, %s -- %s<BR>' % (link_item(it), by(it), price_line(it))
    c += ('</FONT><BR>' + h_orange("Games &amp; Puzzles") + '<BR><FONT SIZE=-1>Our crossword team is still arguing about seven-down. '
          'Check back soon. <IMG SRC="{P}images/construction.gif" WIDTH=140 HEIGHT=50 ALIGN=MIDDLE ALT="Under construction"></FONT>')
    page("toys.html", "Toys & Games", "toys", twocol(left, c))
    # ------------------------------------------------------------ auctions
    c = ('<FONT FACE="%s" SIZE=+1><B>Orinoco.com Auctions</B></FONT><BR><FONT SIZE=-1>Bid on rare books, signed first editions and '
         'one slightly famous typewriter. Orinoco.com Auctions are run by our trading partners at <A HREF="{P}../ubid/index.html"><B>uBid</B></A>, '
         'so your uBid user ID works here too.</FONT><BR><BR>' % FONT)
    c += h_orange("Today's Featured Lots") + '<BR><TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0 WIDTH="100%">'
    lots = [("Signed first edition, <I>Teach Yourself Web Pages in 21 Minutes</I> (coffee ring on cover)", "$41.00", 7),
            ("Typewriter said to have been used to draft a Penelope Pike fan letter", "$12.50", 3),
            ("Box of 40 assorted dot-com stock certificates (framing recommended)", "$8.75", 11),
            ("Complete set of 1998 almanacs, smells pleasantly of attic", "$22.00", 4),
            ("Hand-annotated <I>Y2K and You</I>, every page highlighted in yellow", "$5.50", 2)]
    for n, (t, p, b) in enumerate(lots):
        c += '<TR BGCOLOR="%s"><TD><FONT FACE="%s" SIZE=-1>%s</FONT></TD><TD ALIGN=RIGHT NOWRAP><FONT FACE="%s" SIZE=-1><B>%s</B><BR><FONT SIZE=-2>%d bids</FONT></FONT></TD><TD><FONT SIZE=-2><A HREF="{P}../ubid/index.html">Bid at uBid</A></FONT></TD></TR>' % (
            "#FFFFFF" if n % 2 else "#EEEECC", FONT, t, FONT, p, b)
    c += "</TABLE>"
    page("auctions.html", "Auctions", "auctions", twocol(left, c))
    # ------------------------------------------------------------ e-cards
    cards = [("card_birthday", "Happy Birthday!"), ("card_y2k", "See You in 2000!"), ("card_thanks", "Thank You!"), ("card_hello", "Just Saying Hi")]
    c = ('<FONT FACE="%s" SIZE=+1><B>Free e-Cards</B></FONT><BR><FONT SIZE=-1>Pick a card, type a note, and we will send it '
         'through the Information Superhighway faster than you can lick a stamp.</FONT><BR><BR>'
         '<FORM NAME="card" ACTION="{P}ecard_sent.html" METHOD=GET onSubmit="return sendCard()">'
         '<TABLE BORDER=0 CELLPADDING=4><TR>' % FONT)
    for n, (img, label) in enumerate(cards):
        if n == 2:
            c += "</TR><TR>"
        c += '<TD ALIGN=CENTER><IMG SRC="{P}images/%s.gif" WIDTH=150 HEIGHT=100><BR><INPUT TYPE=radio NAME="card" VALUE="%s"%s><FONT FACE="%s" SIZE=-1>%s</FONT></TD>' % (
            img, img, " CHECKED" if n == 0 else "", FONT, label)
    c += ('</TR></TABLE><FONT FACE="%s" SIZE=-1>'
          'Your friend\'s name:<BR><INPUT TYPE=text NAME="to" SIZE=30><BR>'
          'Your friend\'s e-mail address:<BR><INPUT TYPE=text NAME="email" SIZE=30><BR>'
          'Your message:<BR><TEXTAREA NAME="msg" ROWS=4 COLS=40 WRAP=VIRTUAL></TEXTAREA><BR><BR>'
          '<INPUT TYPE=image SRC="{P}images/btn_send.gif" WIDTH=125 HEIGHT=19 BORDER=0 ALT="Send this e-Card"></FONT></FORM>'
          '<SCRIPT LANGUAGE="JavaScript">\nfunction sendCard() {\n  var f = document.forms["card"];\n'
          '  if (f.to.value == "" || f.email.value.indexOf("@") < 1) { alert("Please enter your friend\'s name and a valid e-mail address."); return false; }\n'
          '  return true;\n}\n</SCRIPT>' % FONT)
    page("ecards.html", "Free e-Cards", "ecards", twocol(left, c))
    c = ('<FONT FACE="%s" SIZE=+1><B>Your e-Card is on its way!</B></FONT><BR><BR>'
         '<SCRIPT LANGUAGE="JavaScript">\nvar card = qs("card"); if (card == "") card = "card_hello";\n'
         'document.write("<IMG SRC=\\"" + P + "images/" + esc(card.replace(/[^a-z0-9_]/g, "")) + ".gif\\" WIDTH=150 HEIGHT=100 ALIGN=LEFT HSPACE=8>");\n'
         'document.write("<FONT SIZE=-1>Dear <B>" + esc(qs("to")) + "</B>,<BR><BR>" + esc(qs("msg")) + "<BR><BR></FONT>");\n'
         'document.write("<FONT SIZE=-2>(Card queued for " + esc(qs("email")) + ". Our mail carrier is a hamster named Pedro, so please allow 2-3 business days.)</FONT>");\n'
         '</SCRIPT><BR CLEAR=ALL><BR><A HREF="{P}ecards.html">Send another e-Card</A>' % FONT)
    page("ecard_sent.html", "e-Card Sent", "ecards", twocol(left, c))
    # ------------------------------------------------------------ help
    c = ('<FONT FACE="verdana,arial,helvetica" SIZE=+1><B>Orinoco.com Help Desk</B></FONT><BR><BR>'
         '<A NAME="ordering"></A>' + h_orange("Ordering") + '<BR>Find something you like, click <B>add to Shopping Cart</B>, and when you are ready, '
         'click <B>Proceed to Checkout</B>. You will be asked to sign in (or to tell us your e-mail address if you are new), where to ship, '
         'and how you would like to pay. Then click <B>Place Your Order</B> and go have a sandwich.<BR><BR>'
         '<A NAME="oneclick"></A>' + h_orange("1-Click Ordering") + '<BR>Once we have your shipping address and payment method on file, '
         'you may switch on 1-Click in <A HREF="{P}account.html">Your Account</A>. After that, the <B>Buy now with 1-Click</B> button '
         'on any product page places your order instantly. One click. No take-backs (well, a few take-backs).<BR><BR>'
         '<A NAME="shipping"></A>' + h_orange("Shipping Rates (U.S.)") + '<BR><TABLE BORDER=1 CELLPADDING=3 CELLSPACING=0>'
         '<TR BGCOLOR="#EEEECC"><TD><FONT SIZE=-1><B>Method</B></FONT></TD><TD><FONT SIZE=-1><B>Per shipment</B></FONT></TD><TD><FONT SIZE=-1><B>Per item</B></FONT></TD></TR>'
         '<TR><TD><FONT SIZE=-1>Standard (3-7 business days)</FONT></TD><TD><FONT SIZE=-1>$2.95</FONT></TD><TD><FONT SIZE=-1>$0.99</FONT></TD></TR>'
         '<TR><TD><FONT SIZE=-1>Second Day Air</FONT></TD><TD><FONT SIZE=-1>$5.95</FONT></TD><TD><FONT SIZE=-1>$1.99</FONT></TD></TR>'
         '<TR><TD><FONT SIZE=-1>Next Day Air</FONT></TD><TD><FONT SIZE=-1>$9.95</FONT></TD><TD><FONT SIZE=-1>$2.99</FONT></TD></TR></TABLE><BR>'
         '<A NAME="safe"></A>' + h_orange("Safe Shopping Pledge") + '<BR>Our servers encrypt your order with the very latest 40-bit technology. '
         'If anyone ever misuses your card because you shopped here, we will cover the first $50 of your liability and send you a '
         'sympathy bookmark.<BR><BR>'
         '<A NAME="privacy"></A>' + h_orange("Privacy Pledge") + '<BR>We keep what we know about you in a cookie in your own browser. '
         'We could not sell it if we tried. (Really: this whole store runs on JavaScript and good intentions.)<BR><BR>'
         '<A NAME="soon"></A>' + h_orange("Coming Soon") + '<BR>Classical music, electronics, lawn furniture, pet food, and possibly the rest of '
         'the planet. Stay tuned.<BR><BR>'
         '<A NAME="about"></A>' + h_orange("About Orinoco.com") + '<BR>Orinoco.com opened in a two-car garage in 1995 with a card table, '
         'three computers and a catalog of books nobody has written yet. Today we ship to over 160 countries and two research stations. '
         'Our name comes from one of the great rivers of South America, because the other good river was taken.<BR><BR>'
         '<B>Demo account:</B> sign in as <TT>demo@orinoco.com</TT> with password <TT>river</TT>.')
    page("help.html", "Help", "welcome", twocol(left, c))


def read_tpl(name):
    with open(os.path.join(HERE, "pages", name), encoding="utf-8") as f:
        return f.read()


def build_js_pages():
    """Pages whose content is written by JavaScript (cart, account, checkout...) live as
    templates in tools/pages/; the generator wraps them in the site chrome."""
    left = search_box() + "<BR>" + browse_box()
    specs = [("cart.html", "Shopping Cart", "welcome", True), ("signin.html", "Sign In", "welcome", True),
             ("account.html", "Your Account", "welcome", True), ("checkout.html", "Checkout: Shipping Address", "welcome", False),
             ("checkout2.html", "Checkout: Shipping &amp; Payment", "welcome", False), ("checkout3.html", "Checkout: Place Your Order", "welcome", False),
             ("thanks.html", "Thank You", "welcome", True), ("search.html", "Search Results", "books", True),
             ("review.html", "Write a Review", "books", True), ("wishlist.html", "Wish List", "welcome", True)]
    for path, title, tab, with_left in specs:
        body = read_tpl(path)
        if with_left:
            content = twocol(left, body)
        else:
            content = ('<TABLE WIDTH=760 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD><BR><FONT FACE="%s" SIZE=-1>%s</FONT></TD></TR></TABLE>' % (FONT, body))
        page(path, title.replace("&amp;", "&"), tab, content)


def write_js(items):
    lines = ["// Orinoco.com catalog, generated by tools/build.py -- do not edit by hand",
             "// ITEMS[i] = code, title, author, price (cents), list price, subject, binding, availability, kind",
             "var ITEMS = new Array();"]
    for n, it in enumerate(sorted(items, key=lambda i: (i["kind"] != "book", i["rank"]))):
        def js(s):
            s = re.sub(r"&amp;", "&", s)
            return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
        lines.append("ITEMS[%d] = new Array(%s, %s, %s, %d, %d, %s, %s, %s, %s);" % (
            n, js(it["code"]), js(it["title"]), js(it["author"]), it["price"], it["list"], js(it["subj"]),
            js(it["binding"]), js(it["avail"]), js(it["kind"])))
    lines.append("var SUBJECTS = new Array(%s);" % ", ".join('new Array("%s", "%s")' % (c, n) for c, n in D.SUBJECTS))
    with open(os.path.join(ROOT, "js", "books.js"), "w", encoding="latin-1", errors="xmlcharrefreplace") as f:
        f.write("\n".join(lines) + "\n")


def main():
    import gfx
    pages_only = "--pages" in sys.argv
    items = build_catalog()
    global TABSIZES
    if pages_only:
        from PIL import Image
        for key, _l, _c in gfx.TABS:
            a = Image.open(os.path.join(ROOT, "images", "tabs", key + "_off.gif")).size
            b = Image.open(os.path.join(ROOT, "images", "tabs", key + "_on.gif")).size
            TABSIZES[key] = (a, b)
    else:
        sizes = gfx.all_static()
        TABSIZES = sizes["tabs"]
        shutil.rmtree(os.path.join(ROOT, "images", "covers"), ignore_errors=True)
        for it in items:
            gfx.cover(it["code"], it["title"], it["author"], it["subj"], it["code"], it["kind"])
    for d in ("detail", "subjects"):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    write_js(items)
    build_home(items)
    build_books(items)
    build_subjects(items)
    build_hot100(items)
    build_detail(items)
    build_shelf(items, "music", "music.html", "Popular Music", "music",
                "Twelve albums everybody is humming this fall, at prices that will not make you hum less.")
    build_shelf(items, "video", "video.html", "DVD &amp; Video", "video",
                "Ten movies to watch on the new DVD player you are about to buy. Widescreen when available; popcorn not included.")
    build_static_pages(items)
    build_js_pages()
    print("Orinoco.com: %d items, %d pages" % (len(items), len(PAGES)))


if __name__ == "__main__":
    main()
