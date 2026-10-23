#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builds the static eToyz site (a 1999 Web parody of an online toy store).

    python3 tools/build.py          # pages + graphics (+ Sprocket's MIDI jingle)
    python3 tools/build.py --pages  # pages only
"""
import os
import random
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import toys_data as D  # noqa: E402

AR = "Arial, Helvetica"
RING = ["yowza", "altavisor", "askreeves", "orinoco", "ubid", "etoyz", "petz", "geohoods",
        "hamstershuffle", "dashdot", "snapster", "cnm"]
CATS = D.CATEGORIES + [("baby", "Baby &amp; Preschool")]
TABCOLOR = {"toys": "#E21B1B", "baby": "#F078AA", "ages": "#1B5FE2", "games": "#1BA84A", "gifts": "#FF8000", "holiday": "#8C3CC8"}
TABHREF = {"toys": "index.html", "baby": "category/baby.html", "ages": "ages.html", "games": "category/electronic.html",
           "gifts": "giftfinder.html", "holiday": "holiday.html"}
SUBNAV = {
    "toys": [("top 10", "top10.html"), ("all categories", "categories.html"), ("shop by age", "ages.html"),
             ("under $20", "holiday.html#under20"), ("meet Sprocket", "about.html")],
    "baby": [("0-12 months", "age/baby.html"), ("1-2 years", "age/toddler.html"), ("baby toys", "category/baby.html")],
    "ages": [(lab.replace("&amp;", "&amp;"), "age/%s.html" % k) for k, lab, _a, _b in D.AGES],
    "games": [("video games", "category/electronic.html"), ("board games", "category/games.html"), ("puzzles", "search.html?q=puzzle")],
    "gifts": [("gift finder", "giftfinder.html"), ("wish lists", "wishlist.html"), ("top 10", "top10.html")],
    "holiday": [("shipping deadlines", "holiday.html#deadlines"), ("stocking stuffers", "holiday.html#under20"),
                ("Sprocket's jingle", "holiday.html#jingle")],
}
PAGES = []
SIZES = {}


def money(c):
    return "$%s.%02d" % ("{:,}".format(c // 100), c % 100)


def age_label(a, b):
    if b >= 1200:
        return (("%d months" % a) if a < 24 else ("%d years" % (a // 12))) + " &amp; up"
    if b < 24:
        return "%d-%d months" % (a, b)
    if a < 24:
        return "%d months - %d years" % (a, b // 12)
    return "%d-%d years" % (a // 12, b // 12)


# ====================================================================== data
def parse():
    rnd = random.Random(1225)
    toys = []
    codes = set()
    for line in D.TOYS.strip().splitlines():
        cat, kind, name, brand, amin, amax, price, gender, desc = line.split("|")
        while True:
            code = "ET%05d" % rnd.randint(10000, 99999)
            if code not in codes:
                codes.add(code)
                break
        t = {"code": code, "cat": cat, "kind": kind, "name": name, "brand": brand, "amin": int(amin), "amax": int(amax),
             "price": int(round(float(price) * 100)), "for": gender, "desc": desc}
        toys.append(t)
    order = list(toys)
    rnd.shuffle(order)
    top = dict((n, i) for i, n in enumerate(D.TOP10))
    order.sort(key=lambda t: top.get(t["name"], 99))
    for r, t in enumerate(order):
        t["rank"] = r + 1
        if r < 10:
            t["avail"] = "HOT! Limited quantities -- usually ships in 1-2 days"
        else:
            t["avail"] = rnd.choice(["In stock -- usually ships in 1-2 days"] * 5 + ["In stock -- usually ships in 3-5 days",
                                     "Backordered -- expected to ship by Dec. 15"])
        t["list"] = int(t["price"] * rnd.choice([1.0, 1.0, 1.1, 1.2, 1.25])) // 100 * 100 + 99 if rnd.random() < .45 else t["price"]
        nrev = rnd.choice([0, 1, 1, 2, 3])
        t["reviews"] = [(rnd.choice([4, 5, 5, 5, 3]),) + rnd.choice(D.PARENT_REVIEWS) + (rnd.choice(["Mom in Ohio", "Dad of three", "Grandma Jo", "A happy aunt", "Teacher in Texas", "Busy parent"]),) for _ in range(nrev)]
    for t in toys:
        same = [o for o in toys if o is not t and o["cat"] == t["cat"]]
        t["also"] = rnd.sample(same, min(3, len(same)))
    return toys


# ====================================================================== chrome
def page(path, title, tab, body):
    depth = path.count("/")
    P = "../" * depth
    h = ['<HTML>\n<HEAD>\n<TITLE>eToyz - %s</TITLE>\n' % title]
    h.append('<META NAME="description" CONTENT="eToyz: toys delivered to your door in time for the holidays. Probably.">\n')
    h.append('<SCRIPT LANGUAGE="JavaScript">var P = "%s";</SCRIPT>\n' % P)
    h.append('<SCRIPT LANGUAGE="JavaScript1.2" SRC="%sjs/toys.js"></SCRIPT>\n' % P)
    h.append('<SCRIPT LANGUAGE="JavaScript1.2" SRC="%sjs/etoyz.js"></SCRIPT>\n' % P)
    h.append('</HEAD>\n<BODY BGCOLOR="#FFFFFF" TEXT="#000000" LINK="#1B5FE2" VLINK="#8C3CC8" ALINK="#E21B1B" TOPMARGIN=0 MARGINHEIGHT=0>\n')
    h.append(header(P, tab))
    h.append(body.replace("{P}", P))
    h.append(footer(P))
    h.append("</BODY>\n</HTML>\n")
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="latin-1", errors="xmlcharrefreplace") as f:
        f.write("".join(h))
    PAGES.append(path)


def header(P, tab):
    from gfx import TABS
    s = ['<TABLE WIDTH=760 BORDER=0 CELLPADDING=0 CELLSPACING=0>\n<TR><TD ROWSPAN=2 WIDTH=210 VALIGN=BOTTOM>'
         '<A HREF="%sindex.html"><IMG SRC="%simages/logo.gif" WIDTH=200 HEIGHT=70 BORDER=0 ALT="eToyz"></A></TD>\n' % (P, P)]
    s.append('<TD ALIGN=RIGHT VALIGN=TOP><FONT FACE="%s" SIZE=2><SCRIPT LANGUAGE="JavaScript">writeUserLinks(); document.write(" | "); writeCartLine();</SCRIPT>'
             ' | <A HREF="%swishlist.html">wish list</A> | <A HREF="%shelp.html">help</A></FONT></TD></TR>\n' % (AR, P, P))
    s.append('<TR><TD VALIGN=BOTTOM ALIGN=RIGHT NOWRAP>')
    for key, label, _c in TABS:
        w, hgt = SIZES["tabs"][key]
        s.append('<A HREF="%s%s"><IMG SRC="%simages/tabs/%s_%d.gif" WIDTH=%d HEIGHT=%d BORDER=0 ALT="%s"></A>' % (
            P, TABHREF[key], P, key, 1 if key == tab else 0, w, hgt, label))
    s.append('</TD></TR>\n')
    links = " &nbsp;&#149;&nbsp; ".join('<A HREF="%s%s"><FONT COLOR="#FFFFFF">%s</FONT></A>' % (P, h, l) for l, h in SUBNAV[tab])
    s.append('<TR><TD COLSPAN=2 BGCOLOR="%s" HEIGHT=24 ALIGN=CENTER><FONT FACE="%s" SIZE=2 COLOR="#FFFFFF"><B>%s</B></FONT></TD></TR>\n' % (TABCOLOR[tab], AR, links))
    s.append('</TABLE>\n')
    return "".join(s)


def footer(P):
    i = RING.index("etoyz")
    prev, nxt = RING[i - 1], RING[(i + 1) % len(RING)]
    s = ['<TABLE WIDTH=760 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD ALIGN=CENTER><BR>'
         '<TABLE WIDTH="100%%" BORDER=0 CELLPADDING=4 CELLSPACING=0><TR><TD BGCOLOR="#99CCFF" ALIGN=CENTER><FONT FACE="%s" SIZE=2>' % AR]
    s.append(" | ".join('<A HREF="%s%s">%s</A>' % (P, h, l) for l, h in [
        ("toys", "index.html"), ("baby", "category/baby.html"), ("shop by age", "ages.html"), ("video games", "category/electronic.html"),
        ("gift finder", "giftfinder.html"), ("holiday", "holiday.html")]))
    s.append('<BR>' + " | ".join('<A HREF="%s%s">%s</A>' % (P, h, l) for l, h in [
        ("home", "index.html"), ("about eToyz", "about.html"), ("help", "help.html"), ("my eToyz", "account.html"),
        ("privacy", "help.html#privacy"), ("safe &amp; secure", "help.html#secure"), ("shopping cart", "cart.html")]))
    s.append('</FONT></TD></TR></TABLE><FONT FACE="%s" SIZE=1><BR>&copy; 1999 eToyz, Inc. All rights reserved. Toys delivered by a fleet of '
             'KoldFusion 4.5 servers from Gibson Mainframe Co.<BR><I>A 1999 Web parody: every toy, brand and price here is invented.</I></FONT>\n' % AR)
    s.append('<BR><BR><TABLE BORDER=2 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#C0C0C0"><TR><TD ALIGN=CENTER NOWRAP><FONT FACE="Arial, Helvetica" SIZE=1>\n')
    s.append('<A HREF="%s../%s/index.html">&lt;&lt; Prev</A> | <A HREF="%s../../web1999/index.html" onClick="return ringRandom()">Random</A> | '
             '<B><A HREF="%s../../web1999/index.html">The 1999 Web Ring</A></B> | <A HREF="%s../%s/index.html">Next &gt;&gt;</A>\n' % (P, prev, P, P, P, nxt))
    s.append('</FONT></TD></TR></TABLE>\n</TD></TR></TABLE>\n')
    return "".join(s)


def spine():
    ages = "".join('<A HREF="{P}age/%s.html">%s</A><BR>' % (k, lab) for k, lab, _a, _b in D.AGES)
    cats = "".join('<A HREF="{P}category/%s.html">%s</A><BR>' % (c, n) for c, n in CATS)
    def box(title, inner):
        return ('<TABLE BORDER=0 WIDTH=190 CELLPADDING=5 CELLSPACING=0><TR><TD BGCOLOR="#FFFFED"><FONT FACE="%s" SIZE=2>'
                '<FONT COLOR="#1B5FE2"><B>%s</B></FONT><BR>%s</FONT></TD></TR></TABLE><IMG SRC="{P}images/pixel.gif" WIDTH=1 HEIGHT=6><BR>' % (AR, title, inner))
    s = ('<TABLE BORDER=0 WIDTH=200 CELLPADDING=5 CELLSPACING=0 BGCOLOR="#99CCFF"><TR><TD VALIGN=TOP>'
         + box("quick search", '<FORM NAME="qs" ACTION="{P}search.html" METHOD=GET><INPUT TYPE=text NAME="q" SIZE=12> <INPUT TYPE=submit VALUE="Go"></FORM>'
               '<A HREF="{P}giftfinder.html"><B>Gift Finder</B></A>: search by age, price &amp; more!')
         + box("shop by age", ages)
         + box("toy categories", cats)
         + box("toy picks", '<A HREF="{P}top10.html">Top 10 Toys</A><BR><A HREF="{P}holiday.html#under20">Stocking Stuffers Under $20</A><BR>'
               '<A HREF="{P}search.html?q=learning">Learning Toys</A><BR><A HREF="{P}search.html?q=y2k">Y2K Fun</A>')
         + box("gift services", '<A HREF="{P}giftfinder.html">Gift Finder</A><BR><A HREF="{P}wishlist.html">Wish Lists</A><BR>'
               '<A HREF="{P}help.html#wrap">Gift Wrapping</A><BR><A HREF="{P}help.html#giftcert">Gift Certificates</A>')
         + box("need info?", '<A HREF="{P}help.html">Help</A><BR><A HREF="{P}help.html#shipping">Shipping Options</A><BR>'
               '<A HREF="{P}help.html#price">Low Price Promise</A><BR><A HREF="{P}help.html#privacy">Privacy Policy</A><BR><A HREF="{P}about.html">About eToyz</A>')
         + '</TD></TR></TABLE>')
    return s


def layout(center, right=None):
    s = '<TABLE WIDTH=760 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD WIDTH=200 VALIGN=TOP BGCOLOR="#99CCFF">%s</TD><TD WIDTH=14>&nbsp;</TD>' % spine()
    s += '<TD VALIGN=TOP><BR><FONT FACE="%s" SIZE=2>%s</FONT></TD>' % (AR, center)
    if right:
        s += '<TD WIDTH=12>&nbsp;</TD><TD WIDTH=180 VALIGN=TOP><BR>%s</TD>' % right
    return s + '</TR></TABLE>\n'


def toy_link(t):
    return '<A HREF="{P}toy/%s.html">%s</A>' % (t["code"], t["name"])


def toy_rows(lst, numbered=False):
    s = ['<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%">']
    for n, t in enumerate(lst):
        s.append('<TR BGCOLOR="%s">' % ("#FFFFFF" if n % 2 == 0 else "#FFFFED"))
        if numbered:
            s.append('<TD VALIGN=TOP ALIGN=RIGHT><FONT FACE="%s" SIZE=5 COLOR="#E21B1B"><B>%d</B></FONT></TD>' % (AR, n + 1))
        s.append('<TD WIDTH=74 VALIGN=TOP><A HREF="{P}toy/%s.html"><IMG SRC="{P}images/toys/%s_s.gif" WIDTH=70 HEIGHT=70 BORDER=0 ALT=""></A></TD>' % (t["code"], t["code"]))
        s.append('<TD VALIGN=TOP><FONT FACE="%s" SIZE=2><B>%s</B><BR>%s &middot; ages %s<BR><FONT COLOR="#E21B1B"><B>%s</B></FONT>%s &nbsp; '
                 '<A HREF="{P}cart.html" onClick="return cartAdd(\'%s\', 1)">add to cart</A> | <A HREF="{P}wishlist.html" onClick="return wishAdd(\'%s\')">wish list</A>%s</FONT></TD></TR>'
                 % (AR, toy_link(t), t["brand"], age_label(t["amin"], t["amax"]), money(t["price"]),
                    (" <STRIKE><FONT COLOR=\"#888888\">%s</FONT></STRIKE>" % money(t["list"])) if t["list"] > t["price"] else "",
                    t["code"], t["code"], ' <IMG SRC="{P}images/hot.gif" WIDTH=40 HEIGHT=26 ALIGN=ABSMIDDLE ALT="HOT!">' if t["rank"] <= 10 else ""))
    s.append("</TABLE>")
    return "".join(s)


# ====================================================================== pages
def build_home(toys):
    top = sorted(toys, key=lambda t: t["rank"])[:10]
    ages = "".join('<TD ALIGN=CENTER><A HREF="{P}age/%s.html"><IMG SRC="{P}images/age_%s.gif" WIDTH=64 HEIGHT=64 BORDER=0 ALT="%s"></A></TD>' % (k, k, lab)
                   for k, lab, _a, _b in D.AGES)
    toyday = ('<IMG SRC="{P}images/h_featured.gif" WIDTH=340 HEIGHT=26 ALT="Toy of the Day"><BR>'
              '<SCRIPT LANGUAGE="JavaScript">\n'
              'var n = new Date(), doy = Math.floor((n.getTime() - (new Date(n.getFullYear(), 0, 1)).getTime()) / DAY);\n'
              'var t = T[(doy * 7) % T.length];\n'
              'document.write("<TABLE BORDER=0 CELLPADDING=4><TR><TD><A HREF=\\"" + toyURL(t) + "\\"><IMG SRC=\\"" + P + "images/toys/" + t[0] + ".gif\\" WIDTH=140 HEIGHT=140 BORDER=0></A></TD><TD VALIGN=TOP><FONT FACE=\\"Arial, Helvetica\\" SIZE=2>");\n'
              'document.write("<FONT SIZE=3><B><A HREF=\\"" + toyURL(t) + "\\">" + esc(t[1]) + "</A></B></FONT><BR>by " + esc(t[2]) + "<BR>Ages " + ageLabel(t) + "<BR><BR><FONT SIZE=4 COLOR=\\"#E21B1B\\"><B>" + money(t[6]) + "</B></FONT><BR><BR>");\n'
              'document.write("<A HREF=\\"" + P + "cart.html\\" onClick=\\"return cartAdd(\'" + t[0] + "\', 1)\\"><IMG SRC=\\"" + P + "images/btn_addcart.gif\\" WIDTH=95 HEIGHT=26 BORDER=0 ALT=\\"Add to Cart\\"></A><BR>");\n'
              'document.write("<A HREF=\\"" + P + "wishlist.html\\" onClick=\\"return wishAdd(\'" + t[0] + "\')\\"><IMG SRC=\\"" + P + "images/btn_wish.gif\\" WIDTH=125 HEIGHT=26 BORDER=0 ALT=\\"Add to Wish List\\"></A></FONT></TD></TR></TABLE>");\n'
              '</SCRIPT>')
    top_rows = ('<CENTER><A HREF="{P}holiday.html"><IMG SRC="{P}images/banner_holiday.gif" WIDTH=468 HEIGHT=60 BORDER=0 ALT="Order by Dec. 20 for Christmas delivery!"></A><BR>'
                '<FONT FACE="%s" SIZE=2><SCRIPT LANGUAGE="JavaScript">writeCountdown();</SCRIPT></FONT></CENTER><BR>'
                '<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD VALIGN=TOP><IMG SRC="{P}images/sprocket.gif" WIDTH=110 HEIGHT=130 ALT="Sprocket the eToyz robot waves hello"></TD>'
                '<TD VALIGN=TOP><FONT FACE="%s" SIZE=3 COLOR="#1B5FE2"><B><SCRIPT LANGUAGE="JavaScript">if (userGet()) document.write("Welcome back, " + esc(firstName()) + "!"); else document.write("Hi! I\'m Sprocket!");</SCRIPT></B></FONT><BR>'
                '<FONT FACE="%s" SIZE=2>Welcome to eToyz, the toy store that never closes, never runs out of parking and never makes you wrestle '
                'another parent for the last talking owl. Shop by age, use our <A HREF="{P}giftfinder.html"><B>Gift Finder</B></A>, or make a '
                '<A HREF="{P}wishlist.html"><B>Wish List</B></A> and leave it open on the family computer. Hint, hint. '
                '<FONT COLOR="#1BA84A"><B>Free standard shipping on orders of $50 or more!</B></FONT></FONT></TD></TR></TABLE><BR>'
                '<IMG SRC="{P}images/h_shopbyage.gif" WIDTH=222 HEIGHT=26 ALT="Shop by Age"><TABLE BORDER=0 CELLPADDING=2><TR>%s</TR></TABLE><BR>'
                % (AR, AR, AR, ages))
    right = ('<IMG SRC="{P}images/h_top10.gif" WIDTH=180 HEIGHT=26 ALT="Top 10 Toys"><TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0 WIDTH=180 BGCOLOR="#FFFFED"><TR><TD><FONT FACE="%s" SIZE=2>%s'
             '<BR><A HREF="{P}top10.html"><B>See the Top 10 &gt;</B></A></FONT></TD></TR></TABLE><BR>'
             '<IMG SRC="{P}images/h_giftfinder.gif" WIDTH=180 HEIGHT=26 ALT="Gift Finder"><TABLE BORDER=0 CELLPADDING=5 CELLSPACING=0 WIDTH=180 BGCOLOR="#FFF0D0"><TR><TD>'
             '<FORM NAME="gf" ACTION="{P}giftfinder.html" METHOD=GET><FONT FACE="%s" SIZE=2>Age:<BR><SELECT NAME="age">%s</SELECT><BR>'
             'Price:<BR><SELECT NAME="price"><OPTION VALUE="0">any price<OPTION VALUE="1">under $10<OPTION VALUE="2">$10 - $25<OPTION VALUE="3">$25 - $50<OPTION VALUE="4">$50 and up</SELECT><BR>'
             'For a:<BR><INPUT TYPE=radio NAME="for" VALUE="b">boy <INPUT TYPE=radio NAME="for" VALUE="g">girl <INPUT TYPE=radio NAME="for" VALUE="a" CHECKED>either<BR><BR>'
             '<INPUT TYPE=image SRC="{P}images/btn_find.gif" WIDTH=90 HEIGHT=26 BORDER=0 ALT="Find Gifts!"></FONT></FORM></TD></TR></TABLE>'
             % (AR, "".join('<FONT COLOR="#E21B1B"><B>%d.</B></FONT> %s<BR>' % (n + 1, toy_link(t)) for n, t in enumerate(top)), AR,
                "".join('<OPTION VALUE="%s">%s' % (k, lab) for k, lab, _a, _b in D.AGES)))
    center = ('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=546><TR><TD COLSPAN=3><FONT FACE="%s" SIZE=2>%s</FONT></TD></TR>'
              '<TR><TD VALIGN=TOP WIDTH=354><FONT FACE="%s" SIZE=2>%s</FONT></TD><TD WIDTH=12>&nbsp;</TD><TD VALIGN=TOP WIDTH=180>%s</TD></TR></TABLE>'
              % (AR, top_rows, AR, toyday, right))
    page("index.html", "Toys delivered to your door!", "toys", layout(center))


def build_lists(toys):
    for k, lab, a, b in D.AGES:
        lst = sorted([t for t in toys if t["amin"] <= b and t["amax"] >= a], key=lambda t: t["rank"])
        c = ('<IMG SRC="{P}images/age_%s.gif" WIDTH=64 HEIGHT=64 ALIGN=LEFT HSPACE=6><FONT FACE="%s" SIZE=5 COLOR="#1B5FE2"><B>Toys for %s</B></FONT><BR>'
             '%d toys picked by our play experts for this age, most popular first.<BR CLEAR=ALL><BR>%s' % (k, AR, lab, len(lst), toy_rows(lst)))
        page("age/%s.html" % k, "Toys for %s" % lab.replace("&amp;", "&"), "ages", layout(c))
    c = '<FONT FACE="%s" SIZE=5 COLOR="#1B5FE2"><B>Shop by Age</B></FONT><BR>Every toy has an age range. Pick one and we\'ll show you what fits.<BR><BR><TABLE BORDER=0 CELLPADDING=6>' % AR
    for k, lab, a, b in D.AGES:
        n = len([t for t in toys if t["amin"] <= b and t["amax"] >= a])
        c += '<TR><TD><A HREF="{P}age/%s.html"><IMG SRC="{P}images/age_%s.gif" WIDTH=64 HEIGHT=64 BORDER=0 ALT="%s"></A></TD><TD><FONT FACE="%s" SIZE=3><A HREF="{P}age/%s.html"><B>%s</B></A></FONT><BR>%d toys</TD></TR>' % (k, k, lab, AR, k, lab, n)
    page("ages.html", "Shop by Age", "ages", layout(c + "</TABLE>"))
    for code, name in CATS:
        lst = sorted([t for t in toys if t["cat"] == code], key=lambda t: t["rank"])
        tab = {"baby": "baby", "electronic": "games", "games": "games"}.get(code, "toys")
        c = '<FONT SIZE=1><A HREF="{P}categories.html">Categories</A> &gt; %s</FONT><BR><FONT FACE="%s" SIZE=5 COLOR="#1BA84A"><B>%s</B></FONT><BR><BR>%s' % (name, AR, name, toy_rows(lst))
        page("category/%s.html" % code, name.replace("&amp;", "&"), tab, layout(c))
    c = '<FONT FACE="%s" SIZE=5 COLOR="#1BA84A"><B>All Toy Categories</B></FONT><BR><BR><TABLE BORDER=0 CELLPADDING=4 WIDTH="100%%"><TR>' % AR
    for n, (code, name) in enumerate(CATS):
        if n and n % 2 == 0:
            c += "</TR><TR>"
        lst = sorted([t for t in toys if t["cat"] == code], key=lambda t: t["rank"])
        c += ('<TD VALIGN=TOP WIDTH="50%%"><A HREF="{P}category/%s.html"><IMG SRC="{P}images/toys/%s_s.gif" WIDTH=70 HEIGHT=70 BORDER=0 ALIGN=LEFT ALT=""></A>'
              '<FONT FACE="%s" SIZE=3><A HREF="{P}category/%s.html"><B>%s</B></A></FONT><BR><FONT SIZE=2>%d toys, like the %s</FONT></TD>'
              % (code, lst[0]["code"], AR, code, name, len(lst), lst[0]["name"]))
    page("categories.html", "Toy Categories", "toys", layout(c + "</TR></TABLE>"))
    top = sorted(toys, key=lambda t: t["rank"])[:10]
    c = ('<IMG SRC="{P}images/top10.gif" WIDTH=40 HEIGHT=46 ALIGN=LEFT><FONT FACE="%s" SIZE=5 COLOR="#E21B1B"><B>The eToyz Top 10</B></FONT><BR>'
         'The ten toys everybody wants this season, updated every morning by Sprocket and a very large abacus.<BR CLEAR=ALL><BR>%s' % (AR, toy_rows(top, numbered=True)))
    page("top10.html", "Top 10 Toys", "toys", layout(c))


def build_toys(toys):
    for t in toys:
        cat = dict(CATS)[t["cat"]]
        rev = ""
        if t["reviews"]:
            avg = round(sum(r[0] for r in t["reviews"]) / float(len(t["reviews"])))
            rev = '<IMG SRC="{P}images/stars%d.gif" WIDTH=70 HEIGHT=14 ALT="%d stars"> <FONT SIZE=1>(%d parent review%s)</FONT><BR>' % (avg, avg, len(t["reviews"]), "" if len(t["reviews"]) == 1 else "s")
        save = ""
        if t["list"] > t["price"]:
            save = 'Was: <STRIKE>%s</STRIKE> &nbsp; <FONT COLOR="#1BA84A"><B>You save %s!</B></FONT><BR>' % (money(t["list"]), money(t["list"] - t["price"]))
        c = ['<FONT SIZE=1><A HREF="{P}categories.html">Categories</A> &gt; <A HREF="{P}category/%s.html">%s</A></FONT><BR>' % (t["cat"], cat)]
        c.append('<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%%"><TR><TD VALIGN=TOP WIDTH=150><IMG SRC="{P}images/toys/%s.gif" WIDTH=140 HEIGHT=140 BORDER=1 ALT="%s"></TD>'
                 '<TD VALIGN=TOP><FONT FACE="%s" SIZE=4 COLOR="#1B5FE2"><B>%s</B></FONT>%s<BR><FONT SIZE=2>by %s</FONT><BR>%s<BR>'
                 '<FONT FACE="%s" SIZE=5 COLOR="#E21B1B"><B>%s</B></FONT><BR><FONT SIZE=2>%s<B>Ages:</B> %s<BR><B>Availability:</B> %s</FONT><BR><BR>'
                 '<FORM NAME="buy" onSubmit="return cartAdd(\'%s\', parseInt(document.forms[\'buy\'].qty.options[document.forms[\'buy\'].qty.selectedIndex].text))">'
                 '<FONT SIZE=2>Qty: <SELECT NAME="qty"><OPTION>1<OPTION>2<OPTION>3<OPTION>4<OPTION>5</SELECT></FONT> '
                 '<INPUT TYPE=image SRC="{P}images/btn_addcart.gif" WIDTH=95 HEIGHT=26 BORDER=0 ALIGN=ABSMIDDLE ALT="Add to Cart"> '
                 '<A HREF="{P}wishlist.html" onClick="return wishAdd(\'%s\')"><IMG SRC="{P}images/btn_wish.gif" WIDTH=125 HEIGHT=26 BORDER=0 ALIGN=ABSMIDDLE ALT="Add to Wish List"></A></FORM>'
                 '</TD></TR></TABLE>'
                 % (t["code"], t["name"], AR, t["name"], (' <IMG SRC="{P}images/hot.gif" WIDTH=40 HEIGHT=26 ALT="HOT!">' if t["rank"] <= 10 else ""),
                    t["brand"], rev, AR, money(t["price"]), save, age_label(t["amin"], t["amax"]), t["avail"], t["code"], t["code"]))
        c.append('<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%%"><TR><TD BGCOLOR="#FFD21B"><FONT FACE="%s" SIZE=2><B>About this toy</B></FONT></TD></TR></TABLE>' % AR)
        c.append('<FONT SIZE=2>%s<BR><BR><B>eToyz says:</B> %s</FONT><BR><BR>' % (t["desc"], random.Random(t["code"]).choice([
            "A guaranteed hit at birthday parties. We've tested it on our own kids (and a few grown-ups).",
            "Sprocket gives this one two mechanical thumbs up.",
            "Our play experts love how this one grows with your child.",
            "One of those rare toys that is still played with in February.",
            "Parents tell us this is the toy that finally got the TV turned off.",
            "Great for siblings to share -- in theory."])))
        c.append('<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%%"><TR><TD BGCOLOR="#99CCFF"><FONT FACE="%s" SIZE=2><B>Product details</B></FONT></TD></TR></TABLE>' % AR)
        batt = "Yes, not included (of course)" if t["kind"] in ("robot", "rccar", "rcboat", "rcplane", "handheld", "console", "computer", "phone", "owl", "dino", "globe", "mobile") else "No"
        c.append('<FONT SIZE=2>eToyz item #: %s<BR>Manufacturer: %s<BR>Recommended ages: %s<BR>Batteries required: %s<BR>Gift wrap available: Yes</FONT><BR><BR>'
                 % (t["code"], t["brand"], age_label(t["amin"], t["amax"]), batt))
        if t["reviews"]:
            c.append('<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%%"><TR><TD BGCOLOR="#1BA84A"><FONT FACE="%s" SIZE=2 COLOR="#FFFFFF"><B>What parents say</B></FONT></TD></TR></TABLE><FONT SIZE=2>' % AR)
            for st, title, body, who in t["reviews"]:
                c.append('<IMG SRC="{P}images/stars%d.gif" WIDTH=70 HEIGHT=14 ALT="%d stars"> <B>%s</B> -- %s<BR>%s<BR><BR>' % (st, st, title, who, body))
            c.append('</FONT>')
        c.append('<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%%"><TR><TD BGCOLOR="#F078AA"><FONT FACE="%s" SIZE=2 COLOR="#FFFFFF"><B>You might also like</B></FONT></TD></TR></TABLE>' % AR)
        c.append('<TABLE BORDER=0 CELLPADDING=4><TR>' + "".join(
            '<TD ALIGN=CENTER VALIGN=TOP WIDTH=120><A HREF="{P}toy/%s.html"><IMG SRC="{P}images/toys/%s_s.gif" WIDTH=70 HEIGHT=70 BORDER=0 ALT=""></A><BR><FONT SIZE=1>%s<BR><B>%s</B></FONT></TD>'
            % (o["code"], o["code"], toy_link(o), money(o["price"])) for o in t["also"]) + '</TR></TABLE>')
        page("toy/%s.html" % t["code"], re.sub(r"&amp;", "&", t["name"]), {"baby": "baby", "electronic": "games", "games": "games"}.get(t["cat"], "toys"), layout("".join(c)))


def build_holiday(toys):
    under = sorted([t for t in toys if t["price"] < 2000], key=lambda t: t["rank"])
    c = ('<FONT FACE="%s" SIZE=5 COLOR="#8C3CC8"><B>Holiday Headquarters</B></FONT><BR><BR>'
         '<CENTER><IMG SRC="{P}images/banner_holiday.gif" WIDTH=468 HEIGHT=60 ALT="Order by Dec. 20 for Christmas delivery!"></CENTER><BR>'
         '<TABLE BORDER=0 CELLPADDING=8 CELLSPACING=0 WIDTH="100%%" BGCOLOR="#FFFFED"><TR><TD ALIGN=CENTER><FONT FACE="%s" SIZE=3><SCRIPT LANGUAGE="JavaScript">writeCountdown();</SCRIPT></FONT>'
         '<FORM NAME="clock"><FONT FACE="%s" SIZE=2>Time left for standard shipping: <INPUT TYPE=text NAME="t" SIZE=34 onFocus="this.blur()"></FONT></FORM>'
         '<SCRIPT LANGUAGE="JavaScript">\n'
         'function tock() {\n'
         '  var left = deadline(11, 20).getTime() - (new Date()).getTime();\n'
         '  if (left < 0) left = 0;\n'
         '  var d = Math.floor(left / DAY), h = Math.floor(left %% DAY / 3600000), m = Math.floor(left %% 3600000 / 60000), s = Math.floor(left %% 60000 / 1000);\n'
         '  document.forms["clock"].t.value = d + " days " + h + " hrs " + m + " min " + s + " sec";\n'
         '  setTimeout("tock()", 1000);\n'
         '}\n'
         'tock();\n'
         '</SCRIPT></TD></TR></TABLE><BR>'
         '<A NAME="deadlines"></A><TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%%"><TR><TD BGCOLOR="#E21B1B"><FONT FACE="%s" SIZE=3 COLOR="#FFFFFF"><B>Order-by dates for Christmas delivery</B></FONT></TD></TR></TABLE>'
         '<TABLE BORDER=1 CELLPADDING=4 CELLSPACING=0><TR BGCOLOR="#FFFFED"><TD><FONT SIZE=2><B>Shipping method</B></FONT></TD><TD><FONT SIZE=2><B>Order by</B></FONT></TD><TD><FONT SIZE=2><B>Cost</B></FONT></TD></TR>'
         '<TR><TD><FONT SIZE=2>Standard (3-6 business days)</FONT></TD><TD><FONT SIZE=2><B>December 20</B></FONT></TD><TD><FONT SIZE=2>$4.95 + $0.95/item (FREE over $50)</FONT></TD></TR>'
         '<TR><TD><FONT SIZE=2>2nd Day Air</FONT></TD><TD><FONT SIZE=2><B>December 22</B></FONT></TD><TD><FONT SIZE=2>$9.95 + $1.95/item</FONT></TD></TR>'
         '<TR><TD><FONT SIZE=2>Overnight</FONT></TD><TD><FONT SIZE=2><B>December 23</B></FONT></TD><TD><FONT SIZE=2>$15.95 + $2.95/item</FONT></TD></TR></TABLE><BR>'
         '<A NAME="jingle"></A><TABLE BORDER=0 CELLPADDING=4><TR><TD><IMG SRC="{P}images/sprocket.gif" WIDTH=110 HEIGHT=130 ALT="Sprocket"></TD><TD><FONT FACE="%s" SIZE=2>'
         '<B>Sprocket wrote a song!</B> It is called &quot;Rolling Home for the Holidays&quot; and it goes beep-boop-beep. '
         '<A HREF="{P}images/sprocket.mid"><B>Play Sprocket\'s jingle</B></A> (MIDI, 1K -- even a 14.4 modem can handle it).<BR><BR>'
         '<EMBED SRC="{P}images/sprocket.mid" AUTOSTART="false" LOOP="false" WIDTH=145 HEIGHT=40></EMBED></FONT></TD></TR></TABLE><BR>'
         '<A NAME="under20"></A><TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH="100%%"><TR><TD BGCOLOR="#1BA84A"><FONT FACE="%s" SIZE=3 COLOR="#FFFFFF"><B>Stocking stuffers under $20</B></FONT></TD></TR></TABLE>%s'
         % (AR, AR, AR, AR, AR, AR, toy_rows(under)))
    page("holiday.html", "Holiday Headquarters", "holiday", layout(c))


def build_about():
    c = ('<FONT FACE="%s" SIZE=5 COLOR="#1B5FE2"><B>Meet Sprocket!</B></FONT><BR><BR>'
         '<IMG SRC="{P}images/sprocket_big.gif" WIDTH=220 HEIGHT=260 ALIGN=RIGHT ALT="Sprocket">'
         '<FONT SIZE=3>Sprocket is the eToyz robot. He was assembled in 1997 from a spare toaster, three roller skates and a lot of love. '
         'He runs on AA batteries and enthusiasm, checks every toy before it ships, and still has not figured out how stairs work.<BR><BR>'
         '<B>Sprocket\'s favorite things:</B><UL><LI>Bubble wrap (popping it, sleeping on it)<LI>The Top 10 list, which he reorganizes hourly<LI>'
         'Kids who send him drawings<LI>Anything with blinking lights</UL>'
         '<B>About eToyz</B><BR>eToyz opened its virtual doors in 1997 with a simple idea: buying toys should be as much fun as playing with them. '
         'No lines, no parking, no tug-of-war over the last Megabot. Today we stock thousands of toys from hundreds of brands '
         '(well, %d toys from ten brands, but who\'s counting) and ship them anywhere in the U.S.<BR><BR>'
         'eToyz is part of <A HREF="{P}../../web1999/index.html">The 1999 Web</A>. It is a parody: every toy, brand and price here is invented, '
         'and no real money changes hands.</FONT><BR CLEAR=ALL>' % (AR, len(D.TOYS.strip().splitlines())))
    page("about.html", "Meet Sprocket", "toys", layout(c))


def read_tpl(name):
    with open(os.path.join(HERE, "pages", name), encoding="utf-8") as f:
        return f.read()


def build_js_pages():
    for path, title, tab in [("cart.html", "Shopping Cart", "toys"), ("checkout.html", "Checkout", "toys"),
                             ("thanks.html", "Thank You!", "toys"), ("signin.html", "Sign In", "toys"),
                             ("account.html", "my eToyz", "toys"), ("wishlist.html", "Wish Lists", "gifts"),
                             ("giftfinder.html", "Gift Finder", "gifts"), ("search.html", "Search", "toys"),
                             ("help.html", "Help", "toys")]:
        page(path, title, tab, layout(read_tpl(path)))


def write_js(toys):
    def js(s):
        return '"' + s.replace("&amp;", "&").replace("\\", "\\\\").replace('"', '\\"') + '"'
    out = ["// eToyz catalog, generated by tools/build.py -- do not edit by hand",
           "// T[i] = code, name, brand, category, min age (months), max age, price (cents), for, picture, rank, availability, description",
           "var T = new Array();"]
    for n, t in enumerate(sorted(toys, key=lambda t: t["rank"])):
        out.append("T[%d] = new Array(%s, %s, %s, %s, %d, %d, %d, %s, %s, %d, %s, %s);" % (
            n, js(t["code"]), js(t["name"]), js(t["brand"]), js(t["cat"]), t["amin"], t["amax"], t["price"], js(t["for"]),
            js(t["kind"]), t["rank"], js(t["avail"]), js(t["desc"])))
    out.append("var AGES = new Array(%s);" % ", ".join("new Array(%s, %s, %d, %d)" % (js(k), js(l), a, b) for k, l, a, b in D.AGES))
    out.append("var CATS = new Array(%s);" % ", ".join("new Array(%s, %s)" % (js(c), js(n)) for c, n in CATS))
    with open(os.path.join(ROOT, "js", "toys.js"), "w", encoding="latin-1", errors="xmlcharrefreplace") as f:
        f.write("\n".join(out) + "\n")


def main():
    import gfx
    from PIL import Image
    toys = parse()
    global SIZES
    if "--pages" in sys.argv:
        SIZES = {"tabs": dict((k, Image.open(os.path.join(ROOT, "images", "tabs", k + "_0.gif")).size) for k, _l, _c in gfx.TABS)}
    else:
        SIZES = gfx.all_static(D.AGES)
        shutil.rmtree(os.path.join(ROOT, "images", "toys"), ignore_errors=True)
        for t in toys:
            gfx.toy_image(t["code"], t["kind"], t["code"])
        px = Image.new("P", (1, 1), 0)
        px.putpalette([255, 255, 255] * 2)
        px.save(os.path.join(ROOT, "images", "pixel.gif"), transparency=0)
    for d in ("toy", "age", "category"):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    write_js(toys)
    build_home(toys)
    build_lists(toys)
    build_toys(toys)
    build_holiday(toys)
    build_about()
    build_js_pages()
    print("eToyz: %d toys, %d pages" % (len(toys), len(PAGES)))


if __name__ == "__main__":
    main()
