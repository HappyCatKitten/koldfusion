#!/usr/bin/env python3
"""Static page generator for Petz.com (1999 Web parody).

Run from the site folder:  python3 tools/gfx.py && python3 tools/gen.py
Every page is plain HTML 3.2/4.0 with inline 1999-style JavaScript (ES3, no external .js).
"""
import os, sys, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import data  # noqa: E402
from data import P, BY_ID, CATEGORIES, loss  # noqa: E402

RING = "yowza altavisor askreeves orinoco ubid etoyz petz geohoods hamstershuffle dashdot snapster cnm".split()
PREV, NEXT = "../etoyz/index.html", "../geohoods/index.html"
HUB = "../../web1999/index.html"
SITE_DATE = "Monday, December 13, 1999"
CAT_IDS = [c[0] for c in CATEGORIES]
CAT_LABEL = dict((c[0], c[1]) for c in CATEGORIES)
TAB_W = [("dogs", 55), ("cats", 52), ("fish", 50), ("birds", 60), ("ferrets", 66), ("reptiles", 69),
         ("smallpets", 87)]
CAT_TIP = {"dogs": 1, "cats": 2, "fish": 3, "birds": 4, "ferrets": 5, "reptiles": 6, "smallpets": 7}

FV = 'FACE="Verdana, Arial, Helvetica"'
FA = 'FACE="Arial, Helvetica"'
written = []


def money(x):
    return "$%.2f" % x

def js(s):
    return json.dumps(s)  # a plain double-quoted JS string literal (ES3-compatible, ASCII only)

def spc(w, h):
    return '<IMG SRC="images/dot_clear.gif" WIDTH=%d HEIGHT=%d BORDER=0>' % (w, h)

def img(src, w, h, alt="", extra=""):
    return '<IMG SRC="images/%s" WIDTH=%d HEIGHT=%d BORDER=0 ALT="%s"%s>' % (src, w, h, alt, extra)

def write(name, html):
    with open(os.path.join(SITE, name), "w", encoding="latin-1") as f:
        f.write(html)
    written.append(name)


# ======================================================================= shared JavaScript
JS_COMMON = r"""
<SCRIPT LANGUAGE="JavaScript">
<!--
// ---- category tab rollovers (document.images swaps)
var tabNames = new Array("home", "dogs", "cats", "fish", "birds", "ferrets", "reptiles", "smallpets");
var tabOn = new Array();
var tabOff = new Array();
if (document.images) {
  for (var i = 0; i < tabNames.length; i++) {
    tabOn[tabNames[i]] = new Image();
    tabOn[tabNames[i]]["src"] = "images/tab_" + tabNames[i] + "_on" + ".gif";
    tabOff[tabNames[i]] = new Image();
    tabOff[tabNames[i]]["src"] = "images/tab_" + tabNames[i] + ".gif";
  }
}
function imgOn(n) {
  if (document.images) document.images["t" + n]["src"] = tabOn[n]["src"];
}
function imgOff(n) {
  if (document.images && n != curTab) document.images["t" + n]["src"] = tabOff[n]["src"];
}
// ---- search box
function isBlank(s) {
  if (s == null) return true;
  for (var i = 0; i < s.length; i++) {
    if (s.charAt(i) != " ") return false;
  }
  return true;
}
function checkSearch(f) {
  if (isBlank(f.q.value)) {
    alert("Please type something to search for.\nTry 'litter', 'hamster' or 'loss'.");
    f.q.focus();
    return false;
  }
  return true;
}
// ---- newsletter
function checkNews(f) {
  var e = f.email.value;
  if (e.indexOf("@") < 1 || e.indexOf(".") < 0) {
    alert("Please enter an e-mail address like argyle@petz.com");
    return false;
  }
  alert("Thanks! You are now subscribed to The Petz Weekly Wag.\n(Nothing was actually sent anywhere. Our mail server is a beagle.)");
  return false;
}
// ---- 1999 Web Ring random hop
var ringSites = new Array("yowza", "altavisor", "askreeves", "orinoco", "ubid", "etoyz", "petz",
  "geohoods", "hamstershuffle", "dashdot", "snapster", "cnm");
function ringRandom() {
  var n = Math.floor(Math.random() * ringSites.length);
  var u = "../" + ringSites[n] + "/" + "index.html";
  window.location = u;
  return false;
}
//-->
</SCRIPT>
"""

JS_TICKER_UP = r"""
<SCRIPT LANGUAGE="JavaScript">
<!--
// ---- PETZ stock ticker: it only goes up (price kept in eighths, remembered in a cookie)
var tkOpen = 679;   // opened today at 84 7/8
function tkGet() {
  var c = document.cookie;
  var i = c.indexOf("petzpx=");
  if (i < 0) return 698;
  var j = c.indexOf(";", i);
  if (j < 0) j = c.length;
  var v = parseInt(c.substring(i + 7, j), 10);
  if (isNaN(v) || v < 698) return 698;
  return v;
}
function tkFmt(e) {
  var w = Math.floor(e / 8);
  var r = e % 8;
  var f = new Array("", "1/8", "1/4", "3/8", "1/2", "5/8", "3/4", "7/8");
  if (r == 0) return "" + w;
  return w + " " + f[r];
}
function tkShow(e) {
  if (document.forms["ticker"]) {
    document.forms["ticker"].px.value = tkFmt(e);
    document.forms["ticker"].chg.value = "+" + tkFmt(e - tkOpen);
  }
}
function tkTick() {
  var e = tkGet() + 1 + Math.floor(Math.random() * 3);
  document.cookie = "petzpx=" + e;
  tkShow(e);
  setTimeout("tkTick()", 2500);
}
function tkStart() {
  tkShow(tkGet());
  setTimeout("tkTick()", 2500);
}
//-->
</SCRIPT>
"""

JS_TICKER_DOWN = r"""
<SCRIPT LANGUAGE="JavaScript">
<!--
// ---- November 2000: the ticker finally learns the other direction
var tkNow = 7;   // in sixteenths: 7/16
function tkFmt16(e) {
  if (e <= 0) return "0";
  var f = new Array("", "1/16", "1/8", "3/16", "1/4", "5/16", "3/8", "7/16");
  return "0 " + f[e];
}
function tkTick() {
  if (document.forms["ticker"]) {
    if (tkNow > 0) {
      tkNow = tkNow - 1;
      document.forms["ticker"].px.value = tkFmt16(tkNow);
      var d = 1396 - tkNow;
      var num = d % 16;
      var den = 16;
      while (num > 0 && num % 2 == 0) { num = num / 2; den = den / 2; }
      document.forms["ticker"].chg.value = "-" + Math.floor(d / 16) + (num > 0 ? " " + num + "/" + den : "");
      setTimeout("tkTick()", 3000);
    } else {
      document.forms["ticker"].px.value = "DELISTED";
      document.forms["ticker"].chg.value = "R.I.P.";
    }
  }
}
function tkStart() {
  setTimeout("tkTick()", 3000);
}
//-->
</SCRIPT>
"""

def js_products(ids=None):
    rows = []
    for p in P:
        if ids is not None and p["id"] not in ids:
            continue
        rows.append('PZ[%s] = new Prod(%s, %s, %s, %.2f, %.2f, %.2f, %.2f, %s);' % (
            js(p["id"]), js(p["id"]), js(p["name"]), js(p["cat"]), p["price"], p["list"], p["ship"], loss(p),
            js(p["brand"] + " " + p["blurb"])))
    return ("function Prod(id, name, cat, price, list, ship, loss, text) {\n"
            "  this.id = id; this.name = name; this.cat = cat; this.price = price; this.list = list;\n"
            "  this.ship = ship; this.loss = loss; this.text = text;\n}\n"
            "var PZ = new Object();\nvar PZids = new Array();\n" +
            "\n".join(rows) + "\nfor (var k in PZ) PZids[PZids.length] = k;\n")

JS_CART = r"""
// ---- shopping cart kept in document.cookie as  petzcart=id.qty-id.qty
function money(n) {
  var c = Math.round(n * 100);
  var d = Math.floor(c / 100);
  c = c % 100;
  var s = "" + d;
  if (d >= 1000) s = Math.floor(d / 1000) + "," + ("" + (1000 + d % 1000)).substring(1);
  return "$" + s + "." + (c < 10 ? "0" : "") + c;
}
function cartRead() {
  var c = document.cookie;
  var i = c.indexOf("petzcart=");
  var items = new Array();
  if (i < 0) return items;
  var j = c.indexOf(";", i);
  if (j < 0) j = c.length;
  var v = c.substring(i + 9, j);
  if (v == "") return items;
  var parts = v.split("-");
  for (var n = 0; n < parts.length; n++) {
    var pq = parts[n].split(".");
    var q = parseInt(pq[1], 10);
    if (pq.length == 2 && !isNaN(q) && q > 0) {
      items[items.length] = new Array(pq[0], q);
    }
  }
  return items;
}
function cartWrite(items) {
  var s = "";
  for (var n = 0; n < items.length; n++) {
    if (items[n][1] > 0) {
      if (s != "") s = s + "-";
      s = s + items[n][0] + "." + items[n][1];
    }
  }
  if (s == "") document.cookie = "petzcart=; expires=Thu, 01-Jan-1970 00:00:01 GMT";
  else document.cookie = "petzcart=" + s;
}
function cartAdd(id, q) {
  var items = cartRead();
  for (var n = 0; n < items.length; n++) {
    if (items[n][0] == id) {
      items[n][1] = items[n][1] + q;
      cartWrite(items);
      return;
    }
  }
  items[items.length] = new Array(id, q);
  cartWrite(items);
}
function cartCount() {
  var items = cartRead();
  var t = 0;
  for (var n = 0; n < items.length; n++) t = t + items[n][1];
  return t;
}
function cartTotals() {
  var items = cartRead();
  var t = new Object();
  t.sub = 0; t.ship = 0; t.save = 0; t.loss = 0; t.count = 0;
  for (var n = 0; n < items.length; n++) {
    var p = PZ[items[n][0]];
    var q = items[n][1];
    if (!p) continue;
    t.sub = t.sub + p.price * q;
    t.ship = t.ship + p.ship * q;
    t.save = t.save + (p.list - p.price) * q;
    t.loss = t.loss + p.loss * q;
    t.count = t.count + q;
  }
  return t;
}
"""


def script(body):
    return '<SCRIPT LANGUAGE="JavaScript">\n<!--\n' + body + '//-->\n</SCRIPT>\n'


# ======================================================================= page chrome
STYLE = """<STYLE TYPE="text/css">
<!--
.editorialtitle { font-family: Verdana, Arial, Helvetica; font-size: 11px; font-weight: bold; color: #000000 }
.editorialsubhead { font-family: Verdana, Arial, Helvetica; font-size: 10px; font-style: italic; color: #666633 }
.ticker { background-color: #000000; color: #33FF33; font-family: Courier New, Courier; font-size: 12px; font-weight: bold; border: 0px }
-->
</STYLE>
"""

def header(tab, titlekey, liquidation=False):
    t = []
    t.append('<TABLE CELLSPACING=0 CELLPADDING=0 BORDER=0 WIDTH=770>')
    t.append('<TR><TD BGCOLOR="#99CC33">%s</TD><TD BGCOLOR="#99CC33">%s</TD><TD BGCOLOR="#99CC33">%s</TD>'
             '<TD BGCOLOR="#99CC33">%s</TD></TR>' % (spc(232, 1), spc(446, 1), spc(86, 1), spc(6, 1)))
    # row 1: logo, ticker, button stack
    t.append('<TR><TD BGCOLOR="#99CC33" VALIGN=TOP>%s<BR>%s<A HREF="index.html">%s</A></TD>' % (
        spc(1, 4), spc(2, 1), img("logo.gif", 230, 66, "Petz.com - Because pets can't drive!")))
    arrow = img("down_arrow.gif" if liquidation else "up_arrow.gif", 11, 11, "")
    px, chg = ("0 7/16", "-86 13/16") if liquidation else ("87 1/4", "+2 3/8")
    note = ("Trading halted. Mostly." if liquidation else
            '<A HREF="investor.html"><FONT COLOR="#FFFFFF">Investor info</FONT></A> &middot; delayed 20 min, not that it matters')
    t.append('<TD BGCOLOR="#99CC33" ALIGN=CENTER VALIGN=MIDDLE><FORM NAME="ticker" onSubmit="return false">'
             '<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=0 BGCOLOR="#000000"><TR>'
             '<TD><FONT %s SIZE=1 COLOR="#FFFFFF">&nbsp;<B>PETZ</B> (NASDAQ: PETZ)</FONT></TD>'
             '<TD><INPUT TYPE=TEXT NAME="px" VALUE="%s" SIZE=8 CLASS="ticker"></TD>'
             '<TD>%s</TD>'
             '<TD><INPUT TYPE=TEXT NAME="chg" VALUE="%s" SIZE=9 CLASS="ticker"></TD></TR>'
             '<TR><TD COLSPAN=4 ALIGN=CENTER><FONT %s SIZE=1 COLOR="#99CC33">%s</FONT></TD></TR>'
             '</TABLE></FORM></TD>' % (FA, px, arrow, chg, FV, note))
    t.append('<TD BGCOLOR="#99CC33" VALIGN=TOP>%s<BR><A HREF="cart.html">%s</A><BR>%s<BR>'
             '<A HREF="myaccount.html">%s</A><BR>%s<BR><A HREF="help.html">%s</A></TD>'
             '<TD BGCOLOR="#99CC33">%s</TD></TR>' % (
                 spc(1, 4), img("btn_cart.gif", 86, 20, "Shopping Cart"), spc(1, 4),
                 img("btn_account.gif", 86, 20, "My Account"), spc(1, 4), img("btn_help.gif", 86, 20, "Help"),
                 spc(1, 72)))
    # row 2: category tabs + home tab
    tabs = []
    for cat, w in TAB_W:
        src = "tab_%s%s.gif" % (cat, "_on" if cat == tab else "")
        tabs.append('<A HREF="%s.html" onMouseOver="imgOn(\'%s\')" onMouseOut="imgOff(\'%s\')">'
                    '<IMG NAME="t%s" SRC="images/%s" WIDTH=%d HEIGHT=60 BORDER=0 ALT="%s"></A>' % (
                        cat, cat, cat, cat, src, w, CAT_LABEL[cat]))
    home = ('<A HREF="index.html" onMouseOver="imgOn(\'home\')" onMouseOut="imgOff(\'home\')">'
            '<IMG NAME="thome" SRC="images/tab_home%s.gif" WIDTH=59 HEIGHT=20 BORDER=0 ALT="Home"></A>' % (
                "_on" if tab == "home" else ""))
    t.append('<TR><TD BGCOLOR="#99CC33" COLSPAN=4 VALIGN=BOTTOM><TABLE CELLSPACING=0 CELLPADDING=0 BORDER=0><TR>'
             '<TD VALIGN=BOTTOM>%s</TD><TD VALIGN=BOTTOM>%s</TD></TR></TABLE></TD></TR>' % ("".join(tabs), home))
    # row 3: black strip with title and rounded corner
    t.append('<TR><TD BGCOLOR="#000000" COLSPAN=4><TABLE CELLSPACING=0 CELLPADDING=0 BORDER=0 WIDTH=770><TR>'
             '<TD>%s</TD><TD WIDTH=611>%s</TD><TD VALIGN=BOTTOM>%s</TD></TR></TABLE></TD></TR>' % (
                 img("title_%s.gif" % titlekey, 150, 28, ""), spc(1, 1), img("corner.gif", 9, 11, "")))
    t.append('</TABLE>')
    return "\n".join(t)


def left_column():
    t = []
    t.append('<TABLE CELLSPACING=0 CELLPADDING=0 BORDER=0 WIDTH=170>')
    t.append('<TR><TD ALIGN=RIGHT>%s<BR><FORM NAME="search" ACTION="search.html" METHOD="GET" '
             'onSubmit="return checkSearch(this)"><TABLE CELLSPACING=0 CELLPADDING=0 BORDER=0 BGCOLOR="#CCCC99"><TR>'
             '<TD BGCOLOR="#FFFFCC">%s</TD>'
             '<TD BGCOLOR="#CCCC99">%s%s</TD>'
             '<TD BGCOLOR="#CCCC99"><INPUT TYPE=TEXT NAME="q" SIZE=9 MAXLENGTH=100>%s</TD>'
             '<TD BGCOLOR="#CCCC99"><INPUT TYPE=IMAGE NAME="go" SRC="images/go.gif" WIDTH=20 HEIGHT=20 BORDER=0>%s</TD>'
             '</TR></TABLE></FORM></TD></TR>' % (
                 spc(1, 8), img("search_side.gif", 16, 36), img("find.gif", 20, 10, "find"), spc(2, 1), spc(2, 1),
                 spc(2, 1)))
    t.append('<TR><TD><TABLE CELLSPACING=2 CELLPADDING=0 BORDER=0><TR><TD>%s</TD><TD>%s</TD></TR></TABLE>' % (
        spc(12, 1), img("todays_features.gif", 135, 15, "Today's Features")))
    t.append('<TABLE CELLSPACING=2 CELLPADDING=0 BORDER=0>')
    for title, sub, href in data.FEATURES:
        t.append('<TR><TD VALIGN=TOP ALIGN=LEFT><TABLE CELLPADDING=2 CELLSPACING=0 BORDER=0><TR><TD>%s</TD>'
                 '<TD VALIGN=TOP><A HREF="%s" CLASS="editorialtitle"><FONT %s SIZE=1><B>%s</B></FONT></A><BR>'
                 '<FONT %s SIZE=1 COLOR="#666633"><I>%s</I></FONT></TD></TR></TABLE></TD></TR>' % (
                     spc(8, 1), href, FV, title, FV, sub))
    t.append('</TABLE><BR>')
    t.append('<CENTER><FONT %s SIZE=1><B>Shop by pet:</B><BR>%s</FONT></CENTER><BR>' % (
        FV, " &middot; ".join('<A HREF="%s.html">%s</A>' % (c, CAT_LABEL[c]) for c in CAT_IDS)))
    t.append('</TD></TR></TABLE>')
    return "\n".join(t)


def footer(liquidation=False):
    links = [("help.html", "Help"), ("help.html#contact", "Contact Us"), ("about.html", "About Us"),
             ("about.html#jobs", "Jobs"), ("help.html#terms", "Terms of Use"),
             ("about.html#associates", "Associates"), ("help.html#guarantee", "Our Guarantee")]
    bar = " | ".join('<A HREF="%s">%s</A>' % l for l in links)
    copy = ("Copyright &copy; 1998-2000 Petz.com, Inc. (in liquidation). All rights reserved, briefly."
            if liquidation else
            "Copyright &copy; 1999 Petz.com, Inc. All rights reserved. Petz.com is not responsible for pets that drive.")
    return """
<TABLE CELLSPACING=0 CELLPADDING=0 BORDER=0 WIDTH=770><TR><TD WIDTH=170 BGCOLOR="#FFFFCC">%s</TD><TD ALIGN=CENTER>
<FONT %s SIZE=1><BR><BR>%s<BR><BR>%s<BR><BR></FONT>
<CENTER><TABLE BORDER=2 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#C0C0C0"><TR><TD ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=1>
<A HREF="%s">&lt;&lt; Prev</A> | <A HREF="%s" onClick="return ringRandom()">Random</A> | <B><A HREF="%s">The 1999 Web Ring</A></B> &middot; Petz.com is site 7 of 12 | <A HREF="%s">Next &gt;&gt;</A>
</FONT></TD></TR></TABLE></CENTER>
<BR>%s<BR><BR>
</TD></TR></TABLE>
""" % (spc(170, 1), FV, bar, copy, PREV, HUB, HUB, NEXT, img("powered_by_kf.gif", 88, 31, "Powered by KoldFusion"))


def page(fname, title, tab, titlekey, center, right=None, head_js="", onload="", liquidation=False):
    on = "tkStart();" + onload
    body = []
    body.append('<HTML>\n<HEAD>\n<TITLE>Petz.com : %s</TITLE>\n'
                '<META http-equiv="Content-Type" content="text/html; charset=iso-8859-1">\n' % title)
    body.append(STYLE)
    body.append(JS_COMMON)
    body.append(JS_TICKER_DOWN if liquidation else JS_TICKER_UP)
    body.append(script('var curTab = "%s";\n' % tab))
    body.append(head_js)
    body.append('</HEAD>\n<BODY BGCOLOR="#FFFFFF" BACKGROUND="images/spine.gif" MARGINHEIGHT=0 MARGINWIDTH=0 '
                'LEFTMARGIN=0 TOPMARGIN=0 TEXT="#000000" LINK="#000000" ALINK="#FF0033" VLINK="#000000" '
                'onLoad="%s">\n' % on)
    body.append(header(tab, titlekey, liquidation))
    cw = 428 if right else 586
    body.append('<TABLE CELLSPACING=0 CELLPADDING=0 BORDER=0 WIDTH=770><TR>'
                '<TD BGCOLOR="#FFFFCC" VALIGN=TOP WIDTH=170>%s</TD><TD WIDTH=14>%s</TD>'
                '<TD VALIGN=TOP WIDTH=%d>%s<BR>\n%s\n</TD>' % (left_column(), spc(14, 1), cw, spc(cw, 10), center))
    if right:
        body.append('<TD WIDTH=12>%s</TD><TD VALIGN=TOP WIDTH=146>%s</TD>' % (spc(12, 1), right))
    body.append('</TR></TABLE>\n')
    body.append(footer(liquidation))
    body.append('</BODY>\n</HTML>\n')
    write(fname, "".join(body))


def font(text, size=2, face=FV, color=None, b=False, i=False):
    if b:
        text = "<B>%s</B>" % text
    if i:
        text = "<I>%s</I>" % text
    return '<FONT %s SIZE=%s%s>%s</FONT>' % (face, size, ' COLOR="%s"' % color if color else "", text)


def product_cell(p):
    return ('<TABLE CELLSPACING=0 CELLPADDING=0 BORDER=0><TR>'
            '<TD VALIGN=TOP ROWSPAN=2><A HREF="product_%(id)s.html">%(thumb)s</A></TD>'
            '<TD VALIGN=TOP ROWSPAN=2>%(s1)s</TD>'
            '<TD VALIGN=TOP ROWSPAN=2>%(s2)s<BR><A HREF="product_%(id)s.html">%(arrow)s</A></TD>'
            '<TD VALIGN=TOP ROWSPAN=2>%(s3)s</TD>'
            '<TD VALIGN=TOP>%(s2)s<BR><A HREF="product_%(id)s.html"><FONT %(fv)s SIZE=1><B>%(name)s</B></FONT></A><BR>'
            '<FONT %(fv)s SIZE=1 COLOR="#666666">%(brand)s</FONT></TD></TR>'
            '<TR><TD VALIGN=BOTTOM><FONT %(fv)s SIZE=1>list <S>%(list)s</S></FONT><BR>'
            '<FONT %(fv)s SIZE=1 COLOR="#CC0000"><B>price: %(price)s</B></FONT></TD></TR></TABLE>') % dict(
        id=p["id"], thumb=img("thumb_%s.gif" % p["id"], 90, 90, p["name"]), s1=spc(5, 95), s2=spc(10, 8),
        arrow=img("arrow.gif", 11, 11, "more"), s3=spc(8, 10), fv=FV, name=p["name"], brand=p["brand"],
        list=money(p["list"]), price=money(p["price"]))


# ======================================================================= HOME
def home():
    feats = dict((c, [p for p in P if p["cat"] == c and p["feature"]][0]) for c in CAT_IDS + ["mascot"])
    rows = [("dogs", "cats"), ("fish", "birds"), ("ferrets", "reptiles"), ("smallpets", "mascot")]
    c = []
    c.append('<TABLE CELLSPACING=0 CELLPADDING=0 BORDER=0 WIDTH=428>')
    c.append('<TR><TD>%s</TD><TD>%s</TD><TD>%s</TD><TD>%s</TD></TR>' % (spc(204, 1), spc(10, 1), spc(204, 1), spc(10, 1)))
    c.append('<TR><TD COLSPAN=4><FONT %s SIZE=1 COLOR="#666633">%s &middot; Free shipping on orders over $10,000*</FONT><BR>'
             '%s<BR>%s</TD></TR>' % (
                 FV, SITE_DATE, img("home_top.gif", 408, 40, "Welcome to Petz.com"),
                 img("banner_home.gif", 415, 117, "The Below-Cost Holiday Sale", ' USEMAP="#homemap"')))
    c.append('<TR><TD COLSPAN=4>%s</TD></TR>' % spc(1, 15))
    for a, b in rows:
        c.append('<TR><TD VALIGN=TOP>%s</TD><TD></TD><TD VALIGN=TOP>%s</TD><TD></TD></TR>' % (
            img("hdr_%s.gif" % a, 200, 20, "for your " + a), img("hdr_%s.gif" % b, 200, 20, "for your " + b)))
        c.append('<TR><TD VALIGN=TOP>%s</TD><TD></TD><TD VALIGN=TOP>%s</TD><TD></TD></TR>' % (
            product_cell(feats[a]), product_cell(feats[b])))
        c.append('<TR><TD COLSPAN=4>%s</TD></TR>' % spc(1, 10))
    c.append('<TR><TD COLSPAN=4>%s</TD></TR>' % img("home_bottom.gif", 408, 22, ""))
    c.append('<TR><TD COLSPAN=4>%s</TD></TR>' % spc(1, 8))
    c.append('<TR><TD VALIGN=TOP>%s</TD><TD></TD><TD VALIGN=TOP>%s</TD><TD></TD></TR>' % (
        img("hdr_vet.gif", 200, 20, "Ask the Vet"), img("hdr_news.gif", 200, 20, "Petz News")))
    vet = [(n, data.ADVICE[n - 1][0], data.ADVICE[n - 1][1].split(".")[0] + ".") for n in (2, 5, 12)]
    news = [("investor.html", "PETZ Hits New High!", "Shares up again. Profits: still pending."),
            ("superbowl.html", "Super Bowl Ad Storyboards Leak", "Argyle sings. A delivery van flees."),
            ("mascot.html", "Argyle Signs Book Deal", "Memoir titled 'Left Foot, Right Hand.'")]
    for i in range(3):
        n, t, s = vet[i]
        if len(s) > 60:
            s = s[:57].rsplit(" ", 1)[0] + "..."
        h, t2, s2 = news[i]
        c.append('<TR><TD VALIGN=TOP><A HREF="advice_%d.html" CLASS="editorialtitle">%s</A><BR>%s<BR>%s</TD><TD></TD>'
                 '<TD VALIGN=TOP><A HREF="%s" CLASS="editorialtitle">%s</A><BR>%s<BR>%s</TD><TD></TD></TR>' % (
                     n, font("<B>%s</B>" % t, 1), font(s, 1, color="#666633", i=True), spc(1, 8),
                     h, font("<B>%s</B>" % t2, 1), font(s2, 1, color="#666633", i=True), spc(1, 8)))
    c.append('<TR><TD COLSPAN=4><FONT %s SIZE=1 COLOR="#999999"><BR>*Offer valid on orders over $10,000 '
             'shipped to the continental United States. We still lose money. We checked twice.</FONT></TD></TR>' % FV)
    c.append('</TABLE>')
    c.append('<MAP NAME="homemap"><AREA SHAPE="rect" COORDS="0,0,415,117" HREF="product_c01.html" '
             'ALT="The Below-Cost Holiday Sale"></MAP>')
    r = []
    r.append('%s<BR><CENTER><A HREF="advice.html">%s</A><A HREF="investor.html">%s</A></CENTER><BR>' % (
        spc(1, 15), img("btn_advice.gif", 73, 19, "Pet Advice"), img("btn_investors.gif", 65, 19, "Investors")))
    r.append('<TABLE CELLSPACING=0 CELLPADDING=0 BORDER=0 WIDTH=146>')
    sep = '<TR><TD BGCOLOR="#FFCC00">%s</TD></TR>' % spc(1, 1)
    r.append(sep)
    r.append('<TR><TD ALIGN=CENTER>%s<BR>%s<BR>%s</TD></TR>' % (
        spc(1, 7), img("potd.gif", 137, 123, "Pet of the Day"),
        font("%s, %s." % data.PET_OF_DAY, 1, i=True)))
    r.append('<TR><TD>%s</TD></TR>' % spc(1, 6))
    r.append(sep)
    # Argyle promo. The first AREA is a 5-pixel hot spot on his pompom nose (the hidden liquidation page).
    r.append('<TR><TD>%s<BR>%s</TD></TR>' % (spc(1, 5), img("puppet_promo.gif", 160, 86, "Meet Argyle!",
                                                            ' USEMAP="#argylemap"')))
    r.append('<TR><TD>%s<A HREF="about.html#associates">%s</A></TD></TR>' % (
        spc(1, 5), img("makemoney.gif", 145, 46, "Become a Petz Associate")))
    r.append('<TR><TD>%s</TD></TR>' % spc(1, 8))
    r.append(sep)
    r.append('<TR><TD>%s<BR><A HREF="help.html#guarantee">%s</A><BR>%s</TD></TR>' % (
        spc(1, 5), img("commitment.gif", 148, 19, "Our Commitment"),
        font("If your pet doesn't love it, send it back. We will lose money on the return shipping too.", 1)))
    r.append('<TR><TD>%s</TD></TR>' % spc(1, 8))
    r.append(sep)
    r.append('<TR><TD><FORM NAME="newsletter" ACTION="index.html" onSubmit="return checkNews(this)">%s<BR>%s<BR>'
             '%s<BR><INPUT TYPE=TEXT NAME="email" VALUE="email address" SIZE=13>%s'
             '<INPUT TYPE=IMAGE SRC="images/greenarrow.gif" WIDTH=16 HEIGHT=16 BORDER=0></FORM></TD></TR>' % (
                 spc(1, 6), img("newsletter.gif", 82, 18, "newsletter"), font("The Petz Weekly Wag, free!", 1),
                 spc(2, 1)))
    r.append(sep)
    r.append('</TABLE>')
    r.append('<MAP NAME="argylemap">'
             '<AREA SHAPE="circle" COORDS="148,26,5" HREF="liquidation.html">'
             '<AREA SHAPE="rect" COORDS="0,0,160,86" HREF="mascot.html" ALT="Meet Argyle!"></MAP>')
    page("index.html", "Home Page", "home", "home", "\n".join(c), right="\n".join(r))


# ======================================================================= CATEGORIES
def category(cat, label, tagline, short):
    items = [p for p in P if p["cat"] == cat]
    c = []
    c.append(img("cat_%s.gif" % cat, 415, 80, label))
    c.append('<BR>%s<BR><FONT %s SIZE=2><B>%s</B></FONT><BR>%s<BR>' % (
        spc(1, 6), FV, tagline, font("All prices below our cost. Every single one. You're welcome.", 1, color="#666633",
                                    i=True)))
    c.append('<BR><TABLE CELLSPACING=0 CELLPADDING=4 BORDER=0 WIDTH=586>')
    for i in range(0, len(items), 2):
        pair = items[i:i + 2]
        c.append('<TR>' + "".join('<TD VALIGN=TOP WIDTH=293>%s</TD>' % product_cell(p) for p in pair) +
                 ('<TD></TD>' if len(pair) == 1 else '') + '</TR>')
        c.append('<TR><TD COLSPAN=2 BGCOLOR="#FFCC00">%s</TD></TR>' % spc(1, 1))
    c.append('</TABLE><BR>')
    n = CAT_TIP[cat]
    q = data.ADVICE[n - 1]
    c.append('<TABLE CELLSPACING=0 CELLPADDING=6 BORDER=0 WIDTH=586 BGCOLOR="#FFFFCC"><TR><TD VALIGN=TOP>%s</TD>'
             '<TD VALIGN=TOP>%s<BR><A HREF="advice_%d.html">%s</A><BR>%s<BR>%s</TD></TR></TABLE>' % (
                 img("vet.gif", 90, 110, data.VET), img("hdr_vet.gif", 200, 20, "Ask the Vet"), n,
                 font("<B>%s</B>" % q[0], 2), font('"%s"' % q[1], 1, i=True),
                 font('<A HREF="advice_%d.html">Read Dr. Woofington\'s answer</A> &middot; '
                      '<A HREF="advice.html">More pet advice</A>' % n, 1)))
    page("%s.html" % cat, label, cat, cat, "\n".join(c))


# ======================================================================= PRODUCTS
def product(p, idx):
    cat = p["cat"]
    tab = cat if cat in CAT_IDS else "home"
    catname = CAT_LABEL.get(cat, "Argyle Merchandise")
    cathref = "%s.html" % cat if cat in CAT_IDS else "mascot.html"
    save = p["list"] - p["price"]
    joke = data.SHIP_JOKES[idx % len(data.SHIP_JOKES)]
    c = []
    c.append(font('<A HREF="index.html">home</A> &gt; <A HREF="%s">%s</A> &gt; %s' % (cathref, catname.lower(), p["name"]), 1))
    c.append('<BR><BR><TABLE CELLSPACING=0 CELLPADDING=0 BORDER=0 WIDTH=586><TR>')
    c.append('<TD VALIGN=TOP WIDTH=210>%s<BR><CENTER>%s</CENTER></TD><TD WIDTH=16>%s</TD>' % (
        img("prod_%s.gif" % p["id"], 200, 200, p["name"]), font("actual size may vary", 1, color="#999999", i=True),
        spc(16, 1)))
    c.append('<TD VALIGN=TOP>')
    c.append('<FONT %s SIZE=3><B>%s</B></FONT><BR>%s<BR><BR>' % (FA, p["name"], font("by " + p["brand"], 1, color="#666666")))
    c.append('%s<BR><BR>' % font(p["blurb"], 2))
    c.append('<TABLE CELLSPACING=0 CELLPADDING=1 BORDER=0 BGCOLOR="#CCCC99" WIDTH=340><TR><TD>'
             '<TABLE CELLSPACING=0 CELLPADDING=6 BORDER=0 BGCOLOR="#FFFFCC" WIDTH=100%><TR><TD>')
    c.append('%s<BR>' % font("List price: <S>%s</S>" % money(p["list"]), 2))
    c.append('<FONT %s SIZE=2><B>Our price: <FONT COLOR="#CC0000" SIZE=3>%s</FONT></B> &mdash; '
             'you save %s, which is more than we make!</FONT><BR>' % (FV, money(p["price"]), money(save)))
    c.append('%s<BR>' % font("<B>Shipping: %s.</B> %s" % (money(p["ship"]), joke), 1))
    c.append('%s' % font("(Petz.com loses %s on every one of these. We make it up in volume.)" % money(loss(p)),
                         1, color="#999999", i=True))
    c.append('<BR><BR><FORM NAME="buy" ACTION="cart.html" METHOD="GET" onSubmit="return buyIt(this)">'
             '<INPUT TYPE=HIDDEN NAME="added" VALUE="%s">%s <INPUT TYPE=TEXT NAME="qty" VALUE="1" SIZE=2 MAXLENGTH=3> '
             '<INPUT TYPE=IMAGE SRC="images/btn_addcart.gif" WIDTH=110 HEIGHT=24 BORDER=0 ALIGN=ABSMIDDLE ALT="Add to Cart">'
             '</FORM>' % (p["id"], font("<B>Qty:</B>", 2)))
    c.append(font("In stock. Ships within 24 hours from our Indianapolis warehouse.", 1, color="#336600"))
    c.append('</TD></TR></TABLE></TD></TR></TABLE>')
    c.append('</TD></TR></TABLE><BR>')
    rel = [q for q in P if q["cat"] == cat and q["id"] != p["id"]][:3]
    if len(rel) < 3:
        rel += [BY_ID[x] for x in ("c01", "d01", "f01") if x != p["id"]][:3 - len(rel)]
    c.append(img("hdr_related.gif", 300, 20, "Customers also lost money on"))
    c.append('<TABLE CELLSPACING=0 CELLPADDING=4 BORDER=0><TR>')
    for q in rel:
        c.append('<TD VALIGN=TOP ALIGN=CENTER WIDTH=140><A HREF="product_%s.html">%s</A><BR>%s<BR>%s</TD>' % (
            q["id"], img("thumb_%s.gif" % q["id"], 90, 90, q["name"]),
            font('<A HREF="product_%s.html">%s</A>' % (q["id"], q["name"]), 1),
            font(money(q["price"]), 1, color="#CC0000", b=True)))
    c.append('</TR></TABLE>')
    js_buy = script(js_products([p["id"]]) + JS_CART + r"""
function buyIt(f) {
  var q = parseInt(f.qty.value, 10);
  if (isNaN(q) || q < 1) {
    alert("Please enter a quantity of 1 or more.\nZero is our profit margin, not a quantity.");
    f.qty.focus();
    return false;
  }
  if (q > 99) {
    alert("Whoa! Our warehouse only has 99 of these.\nAlso, our accountant just fainted.");
    return false;
  }
  cartAdd(%s, q);
  return true;
}
""" % js(p["id"]))
    page("product_%s.html" % p["id"], p["name"], tab, tab if tab != "home" else "mascot", "\n".join(c), head_js=js_buy)


# ======================================================================= CART / CHECKOUT / THANK YOU
def cart():
    js_all = js_products()
    body = js_all + JS_CART + r"""
function cartRemove(id) {
  var items = cartRead();
  for (var n = 0; n < items.length; n++) {
    if (items[n][0] == id) items[n][1] = 0;
  }
  cartWrite(items);
  location.href = "cart.html";
}
function cartUpdate(f) {
  var items = cartRead();
  for (var n = 0; n < items.length; n++) {
    var el = f.elements["q_" + items[n][0]];
    if (el) {
      var q = parseInt(el.value, 10);
      if (isNaN(q) || q < 0) q = 0;
      if (q > 99) q = 99;
      items[n][1] = q;
    }
  }
  cartWrite(items);
  location.href = "cart.html";
  return false;
}
function getArg(name) {
  var s = location.search;
  var i = s.indexOf(name + "=");
  if (i < 0) return "";
  var j = s.indexOf("&", i);
  if (j < 0) j = s.length;
  return unescape(s.substring(i + name.length + 1, j));
}
function drawCart() {
  var items = cartRead();
  var F = '<FONT FACE="Verdana, Arial, Helvetica" SIZE=1>';
  var added = getArg("added");
  if (added != "" && PZ[added]) {
    document.write('<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 BGCOLOR="#FFFFCC" WIDTH=586><TR><TD>' +
      '<FONT FACE="Verdana, Arial, Helvetica" SIZE=2><B>Argyle put "' + PZ[added].name + '" in your cart!</B> ' +
      'Somewhere, an accountant just sighed.</FONT></TD></TR></TABLE><BR>');
  }
  if (items.length == 0) {
    document.write('<FONT FACE="Verdana, Arial, Helvetica" SIZE=2><B>Your shopping cart is empty.</B><BR>' +
      'So is our bank account, so you are in good company.<BR><BR>' +
      'Pick a pet tab above, or <A HREF="index.html">return to the home page</A>.</FONT><BR><BR>');
    return;
  }
  document.write('<FORM NAME="cartform" ACTION="cart.html" onSubmit="return cartUpdate(this)">');
  document.write('<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH=586>');
  document.write('<TR BGCOLOR="#99CC33"><TD COLSPAN=2>' + F + '<B>Item</B></FONT></TD><TD ALIGN=RIGHT>' + F +
    '<B>Price</B></FONT></TD><TD ALIGN=CENTER>' + F + '<B>Qty</B></FONT></TD><TD ALIGN=RIGHT>' + F +
    '<B>Total</B></FONT></TD><TD>&nbsp;</TD></TR>');
  for (var n = 0; n < items.length; n++) {
    var p = PZ[items[n][0]];
    var q = items[n][1];
    if (!p) continue;
    var bg = (n % 2 == 0) ? "#FFFFFF" : "#FFFFCC";
    document.write('<TR BGCOLOR="' + bg + '"><TD><A HREF="product_' + p.id + '.html"><IMG SRC="images/thumb_' + p.id +
      '.gif" WIDTH=45 HEIGHT=45 BORDER=0></A></TD><TD>' + F + '<A HREF="product_' + p.id + '.html"><B>' + p.name +
      '</B></A><BR>Shipping ' + money(p.ship) + ' each</FONT></TD><TD ALIGN=RIGHT>' + F + money(p.price) +
      '</FONT></TD><TD ALIGN=CENTER><INPUT TYPE=TEXT NAME="q_' + p.id + '" VALUE="' + q + '" SIZE=2 MAXLENGTH=2></TD>' +
      '<TD ALIGN=RIGHT>' + F + money(p.price * q) + '</FONT></TD><TD>' + F +
      '<A HREF="javascript:cartRemove(\'' + p.id + '\')">remove</A></FONT></TD></TR>');
  }
  var t = cartTotals();
  document.write('<TR><TD COLSPAN=6 BGCOLOR="#CCCC99"><IMG SRC="images/dot_clear.gif" WIDTH=1 HEIGHT=1></TD></TR>');
  document.write('<TR><TD COLSPAN=4 ALIGN=RIGHT>' + F + 'Subtotal (' + t.count + ' items):</FONT></TD><TD ALIGN=RIGHT>' +
    F + money(t.sub) + '</FONT></TD><TD></TD></TR>');
  document.write('<TR><TD COLSPAN=4 ALIGN=RIGHT>' + F + 'Shipping &amp; handling:</FONT></TD><TD ALIGN=RIGHT>' +
    F + money(t.ship) + '</FONT></TD><TD></TD></TR>');
  document.write('<TR><TD COLSPAN=4 ALIGN=RIGHT>' + F + '<B>Order total:</B></FONT></TD><TD ALIGN=RIGHT>' +
    F + '<B>' + money(t.sub + t.ship) + '</B></FONT></TD><TD></TD></TR>');
  document.write('<TR><TD COLSPAN=4 ALIGN=RIGHT>' + F + '<FONT COLOR="#336600">Your savings off list price:</FONT></FONT>' +
    '</TD><TD ALIGN=RIGHT>' + F + '<FONT COLOR="#336600"><B>' + money(t.save) + '</B></FONT></FONT></TD><TD></TD></TR>');
  document.write('<TR><TD COLSPAN=4 ALIGN=RIGHT>' + F + '<FONT COLOR="#CC0000">Our loss on this order:</FONT></FONT>' +
    '</TD><TD ALIGN=RIGHT>' + F + '<FONT COLOR="#CC0000"><B>' + money(t.loss) + '</B></FONT></FONT></TD><TD></TD></TR>');
  document.write('</TABLE><BR>');
  document.write('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=586><TR>' +
    '<TD><INPUT TYPE=IMAGE SRC="images/btn_update.gif" WIDTH=96 HEIGHT=24 BORDER=0 ALT="Update Cart"></TD>' +
    '<TD ALIGN=CENTER><A HREF="index.html"><IMG SRC="images/btn_continue.gif" WIDTH=130 HEIGHT=24 BORDER=0 ALT="Continue Shopping"></A></TD>' +
    '<TD ALIGN=RIGHT><A HREF="checkout.html"><IMG SRC="images/btn_checkout.gif" WIDTH=96 HEIGHT=24 BORDER=0 ALT="Checkout"></A></TD>' +
    '</TR></TABLE></FORM>');
  document.write(F + '<BR>To change a quantity, type a new number and click <B>Update Cart</B>. ' +
    'Set it to 0 to remove an item (and to reduce our losses, thank you).</FONT>');
}
"""
    c = []
    c.append(font("<B>Your Shopping Cart</B>", 3, face=FA))
    c.append('<BR><BR>')
    c.append(script("drawCart();\n"))
    c.append('<NOSCRIPT>%s</NOSCRIPT>' % font("Our shopping cart needs JavaScript. Please switch it on, or "
                                               "upgrade to Netscape Navigator 4.", 2))
    c.append('<BR><BR>' + font("Items in your cart are stored in a cookie on your own computer. "
                               "Like a real cookie, but you can't eat it. Please don't try.", 1, color="#999999", i=True))
    page("cart.html", "Shopping Cart", "home", "cart", "\n".join(c), head_js=script(body))


PAYMENTS = [
    ("sock", "Bill my sock drawer"),
    ("options", "Pay in Petz stock options (vesting in 2004)"),
    ("biscuit", "IOU, written on a dog biscuit"),
    ("bones", "Bury cash in the backyard; Argyle will dig it up"),
    ("vc", "Charge it to our venture capitalists (everyone else does)"),
]

def checkout():
    body = js_products() + JS_CART + r"""
function drawSummary() {
  var t = cartTotals();
  var F = '<FONT FACE="Verdana, Arial, Helvetica" SIZE=2>';
  if (t.count == 0) {
    document.write(F + '<B>Your cart is empty.</B> You can fill out this form anyway; it is very good practice ' +
      'for when we have something to sell you. <A HREF="index.html">Go shopping</A>.</FONT><BR><BR>');
    return;
  }
  document.write('<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 BGCOLOR="#FFFFCC" WIDTH=586><TR><TD>' + F +
    '<B>Order summary:</B> ' + t.count + ' item(s), ' + money(t.sub) + ' plus ' + money(t.ship) +
    ' shipping = <B>' + money(t.sub + t.ship) + '</B>. <A HREF="cart.html">Change order</A></FONT></TD></TR></TABLE><BR>');
}
function checkOrder(f) {
  var need = new Array("fname", "First name", "lname", "Last name", "addr1", "Street address",
    "city", "City", "state", "State", "zip", "ZIP code");
  for (var i = 0; i < need.length; i = i + 2) {
    if (isBlank(f.elements[need[i]].value)) {
      alert("Please fill in: " + need[i + 1] + ".\nOur delivery van can't find you without it.\n(Pets can't drive, and neither can our van, without directions.)");
      f.elements[need[i]].focus();
      return false;
    }
  }
  var paid = false;
  for (var j = 0; j < f.pay.length; j++) {
    if (f.pay[j].checked) paid = true;
  }
  if (!paid) {
    alert("Please choose a payment method.\nWe accept almost anything except money, apparently.");
    return false;
  }
  if (!confirm("Place this order?\nPetz.com will lose money on it. Click OK to make that happen.")) return false;
  document.cookie = "petzname=" + escape(f.fname.value);
  location.href = "thankyou.html";
  return false;
}
"""
    def field(label, name, size, maxlen=40):
        return ('<TR><TD ALIGN=RIGHT>%s</TD><TD><INPUT TYPE=TEXT NAME="%s" SIZE=%d MAXLENGTH=%d></TD></TR>' % (
            font(label, 1, b=True), name, size, maxlen))
    c = []
    c.append(font("<B>Checkout</B>", 3, face=FA))
    c.append('<BR>' + font("Step 1 of 1. We streamlined. It saves us almost a dollar per order.", 1, color="#666633", i=True))
    c.append('<BR><BR>' + script("drawSummary();\n"))
    c.append('<FORM NAME="order" ACTION="thankyou.html" METHOD="GET" onSubmit="return checkOrder(this)">')
    c.append('<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0>')
    c.append('<TR><TD COLSPAN=2 BGCOLOR="#99CC33">%s</TD></TR>' % font("<B>Ship to:</B>", 2))
    for lab, nm, sz in (("First name:", "fname", 20), ("Last name:", "lname", 24), ("Street address:", "addr1", 34),
                        ("Apt / suite:", "addr2", 12), ("City:", "city", 22), ("State:", "state", 3), ("ZIP code:", "zip", 10),
                        ("Pet's name:", "petname", 20)):
        c.append(field(lab, nm, sz))
    c.append('<TR><TD ALIGN=RIGHT VALIGN=TOP>%s</TD><TD><SELECT NAME="speed">'
             '<OPTION SELECTED>Standard ground (3-7 days)'
             '<OPTION>Second day air (we lose more)'
             '<OPTION>Overnight (we lose the most)'
             '<OPTION>Carrier pigeon (bird food orders only)</SELECT></TD></TR>' % font("Delivery:", 1, b=True))
    c.append('<TR><TD ALIGN=RIGHT VALIGN=TOP>%s</TD><TD><TEXTAREA NAME="gift" ROWS=3 COLS=34 WRAP=VIRTUAL></TEXTAREA><BR>%s</TD></TR>' % (
        font("Gift message:", 1, b=True), font("Printed on the packing slip, under the part where we lose money.", 1, i=True)))
    c.append('<TR><TD COLSPAN=2>%s</TD></TR>' % spc(1, 6))
    c.append('<TR><TD COLSPAN=2 BGCOLOR="#99CC33">%s</TD></TR>' % font("<B>Payment method:</B>", 2))
    c.append('<TR><TD></TD><TD>')
    for val, lab in PAYMENTS:
        c.append('<INPUT TYPE=RADIO NAME="pay" VALUE="%s"> %s<BR>' % (val, font(lab, 2)))
    c.append('%s</TD></TR>' % font("<BR>Petz.com does not accept credit cards at this time. Our bank asked us to "
                                   "stop sending them so much paperwork.", 1, color="#999999", i=True))
    c.append('<TR><TD COLSPAN=2>%s</TD></TR>' % spc(1, 6))
    c.append('<TR><TD></TD><TD><INPUT TYPE=IMAGE SRC="images/btn_placeorder.gif" WIDTH=130 HEIGHT=24 BORDER=0 '
             'ALT="Place My Order"></TD></TR>')
    c.append('</TABLE></FORM>')
    c.append(font("This is a parody web site from 1999. Nothing you type here is sent anywhere, stored, or read by "
                  "anyone, including Argyle.", 1, color="#999999"))
    page("checkout.html", "Checkout", "home", "checkout", "\n".join(c), head_js=script(body))


def thankyou():
    body = js_products() + JS_CART + r"""
function getCookie(name) {
  var c = document.cookie;
  var i = c.indexOf(name + "=");
  if (i < 0) return "";
  var j = c.indexOf(";", i);
  if (j < 0) j = c.length;
  return unescape(c.substring(i + name.length + 1, j));
}
function htmlSafe(s) {
  var out = "";
  for (var i = 0; i < s.length; i++) {
    var ch = s.charAt(i);
    if (ch == "<") out = out + "&lt;";
    else if (ch == ">") out = out + "&gt;";
    else if (ch == "&") out = out + "&amp;";
    else if (ch == '"') out = out + "&quot;";
    else out = out + ch;
  }
  return out;
}
function drawThanks() {
  var F = '<FONT FACE="Verdana, Arial, Helvetica" SIZE=2>';
  var t = cartTotals();
  var who = htmlSafe(getCookie("petzname"));
  if (who == "") who = "valued customer";
  var num = "PZ-" + (1000000 + Math.floor(Math.random() * 8999999)) + "-99";
  document.write('<FONT FACE="Arial, Helvetica" SIZE=4><B>Thank you, ' + who + '!</B></FONT><BR><BR>');
  if (t.count == 0) {
    document.write(F + 'Hmm. Your cart was empty, so this order totals <B>$0.00</B>.<BR>' +
      'That makes it the first order in Petz.com history on which we did not lose money. ' +
      'Our CFO would like to frame it.</FONT><BR><BR>');
  } else {
    document.write(F + 'Your order number is <B>' + num + '</B>. Please write it down on a sock.<BR><BR>' +
      'You bought ' + t.count + ' item(s) for <B>' + money(t.sub + t.ship) + '</B>, including ' + money(t.ship) +
      ' shipping, and saved ' + money(t.save) + ' off list price.<BR><BR>' +
      '<TABLE BORDER=0 CELLPADDING=8 CELLSPACING=0 BGCOLOR="#FFFFCC"><TR><TD>' + F +
      'Petz.com lost <FONT COLOR="#CC0000" SIZE=4><B>' + money(t.loss) + '</B></FONT> on this order.<BR>' +
      'That is our gift to you. Our investors would like to thank you personally, but they are lying down.' +
      '</FONT></TD></TR></TABLE><BR>' +
      'Your order will leave our warehouse within 24 hours, by truck, because pets can\'t drive.</FONT><BR><BR>');
    var px = 698;
    var i = document.cookie.indexOf("petzpx=");
    if (i >= 0) {
      var v = parseInt(document.cookie.substring(i + 7), 10);
      if (!isNaN(v) && v > px) px = v;
    }
    document.cookie = "petzpx=" + (px + 8);
    document.write(F + '<B>Good news!</B> On word of your order, PETZ stock just jumped another full point. ' +
      'Wall Street loves it when we lose money.</FONT><BR><BR>');
  }
  document.cookie = "petzcart=; expires=Thu, 01-Jan-1970 00:00:01 GMT";
  document.write(F + '<A HREF="index.html">Keep shopping</A> &middot; <A HREF="investor.html">Check our stock</A>' +
    ' &middot; <A HREF="mascot.html">Thank Argyle personally</A></FONT>');
}
"""
    c = []
    c.append('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=586><TR><TD VALIGN=TOP>')
    c.append(script("drawThanks();\n"))
    c.append('</TD><TD VALIGN=TOP ALIGN=RIGHT>%s</TD></TR></TABLE>' % img("argyle_party.gif", 120, 160, "Argyle celebrates"))
    page("thankyou.html", "Thank You", "home", "thankyou", "\n".join(c), head_js=script(body))


# ======================================================================= ACCOUNT / HELP / ABOUT
def myaccount():
    js_ = script(r"""
function signIn(f) {
  if (isBlank(f.email.value) || isBlank(f.pw.value)) {
    alert("Please enter your e-mail address and password.");
    return false;
  }
  alert("Sorry! Our account server is out for a walk.\nPlease try again after its nap.\n\n(Nothing you typed was sent anywhere.)");
  f.pw.value = "";
  return false;
}
function newAcct(f) {
  alert("New accounts are temporarily unavailable.\nOur database is being housebroken.");
  return false;
}
""")
    c = []
    c.append(font("<B>My Account</B>", 3, face=FA) + "<BR><BR>")
    c.append('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=586><TR><TD VALIGN=TOP WIDTH=290>')
    c.append('<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 BGCOLOR="#FFFFCC" WIDTH=280><TR><TD>')
    c.append(font("<B>Returning customers, sign in:</B>", 2))
    c.append('<FORM NAME="signin" ACTION="myaccount.html" onSubmit="return signIn(this)">%s<BR>'
             '<INPUT TYPE=TEXT NAME="email" SIZE=24><BR>%s<BR><INPUT TYPE=PASSWORD NAME="pw" SIZE=24><BR><BR>'
             '<INPUT TYPE=IMAGE SRC="images/btn_signin.gif" WIDTH=80 HEIGHT=24 BORDER=0 ALT="Sign In"></FORM>' % (
                 font("E-mail address:", 1), font("Password:", 1)))
    c.append(font('<A HREF="help.html#password">Forgot your password?</A>', 1))
    c.append('</TD></TR></TABLE></TD><TD VALIGN=TOP>')
    c.append('<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 WIDTH=286><TR><TD>')
    c.append(font("<B>New to Petz.com?</B><BR>Create an account and enjoy one-click shopping, order tracking "
                  "and a personalized pet profile, coming in Version 2.0 of our web site (Q3 2000, probably).", 2))
    c.append('<FORM NAME="newacct" ACTION="myaccount.html" onSubmit="return newAcct(this)">'
             '<INPUT TYPE=SUBMIT VALUE="Create Account"></FORM>')
    c.append('</TD></TR></TABLE></TD></TR></TABLE><BR>')
    c.append(img("hdr_history.gif", 300, 20, "History"))
    c.append('<BR>' + font("<B>Your order history:</B> 0 orders found.<BR>"
                           "Unlike us, you have not lost anything yet.", 2))
    c.append('<BR><BR>' + font("<B>Your pet profile:</B> Not found. Possibly hiding under the bed.", 2))
    page("myaccount.html", "My Account", "home", "account", "\n".join(c), head_js=js_)


FAQ = [
 ("shipping", "How much does shipping cost?",
  "Shipping is charged per item and is shown on every product page. It is always less than what it costs us. "
  "Heavy things (litter, kibble, aquariums, bird baths) cost the most to ship. We charge you $14.95 for a 40-pound "
  "bag of litter; the trucking company charges us about $41. We have done this math many times. It does not improve."),
 ("when", "When will my order arrive?",
  "Most orders leave our Indianapolis warehouse within 24 hours and arrive in 3 to 7 business days. Overnight orders "
  "arrive overnight, unless it is snowing, in which case they arrive with snow on them."),
 ("returns", "What is your return policy?",
  "If you or your pet are not completely satisfied, return any item within 30 days for a full refund. We pay the return "
  "shipping. Yes, that means we lose money twice on the same item. Our CFO calls this 'the boomerang.'"),
 ("live", "Do you ship live animals?",
  "Only crickets. Five hundred of them, overnight, in a ventilated box. We do not sell dogs, cats or any other pet "
  "online. Please visit your local shelter. They have wonderful animals and a much better business model."),
 ("guarantee", "Our Guarantee",
  "Every product on Petz.com is guaranteed to be priced below our cost, shipped for less than it costs to ship, and "
  "loved by your pet or your money back. Argyle personally guarantees it, in writing, with a crayon."),
 ("password", "I forgot my password. Help!",
  "Our account system is currently on a walk. When it returns, there will be a 'forgot password' button. Until then, "
  "try your pet's name. That's what everyone uses."),
 ("privacy", "Do you sell my information?",
  "No. We barely manage to sell pet food. Any information you type into this web site stays in your own browser."),
 ("browser", "Which browsers do you support?",
  "Petz.com is best viewed with Netscape Navigator 4.0 or Microsoft Internet Explorer 4.0 or later, at 800x600 or "
  "higher, with cookies and JavaScript turned on. Our shopping cart uses cookies. Our mascot uses socks."),
 ("terms", "Terms of Use",
  "By using this web site you agree that pets cannot drive, that prices are subject to change (downward, mostly), and "
  "that Argyle is a sock and cannot be held legally responsible for anything he says on television."),
 ("contact", "How do I contact Petz.com?",
  "Call 1-888-555-PETZ, 24 hours a day. Our phones are answered by real people, most of whom also have stock options. "
  "Or write to Petz.com, Customer Happiness, 435 Brannan Street, Suite 2, San Francisco, CA 94107."),
]

def help_page():
    c = []
    c.append(font("<B>Help &amp; Customer Service</B>", 3, face=FA) + "<BR><BR>")
    c.append(img("hdr_faq.gif", 300, 20, "FAQ") + "<BR>")
    c.append('<UL>')
    for a, q, _ in FAQ:
        c.append('<LI>%s' % font('<A HREF="#%s">%s</A>' % (a, q), 2))
    c.append('</UL>')
    for a, q, ans in FAQ:
        c.append('<A NAME="%s"></A>%s<BR>%s<BR>%s<BR><BR>' % (
            a, font("<B>%s</B>" % q, 2, color="#336600"), font(ans, 2), font('<A HREF="#top">back to top</A>', 1)))
    c.append(font("Still stuck? Try the <A HREF=\"advice.html\">Pet Advice</A> section, or just "
                  "<A HREF=\"search.html\">search</A> for it.", 2))
    page("help.html", "Help", "home", "help", '<A NAME="top"></A>' + "\n".join(c))


def about():
    c = []
    c.append(font("<B>About Petz.com</B>", 3, face=FA) + "<BR><BR>")
    c.append('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=586><TR><TD VALIGN=TOP>')
    c.append(font("Petz.com is the Internet's leading online retailer of pet supplies, measured by the number of "
                  "40-pound bags of litter shipped below cost. Our mission is simple: to deliver everything your pet "
                  "needs right to your door, because pets can't drive.", 2))
    c.append('<BR><BR>' + font("Petz.com is headquartered in San Francisco, with a warehouse in Indianapolis "
                               "and a sock drawer in Fresno.", 2))
    c.append('</TD><TD VALIGN=TOP ALIGN=RIGHT>%s</TD></TR></TABLE><BR>' % img("argyle_party.gif", 120, 160, "Argyle"))
    c.append(img("hdr_history.gif", 300, 20, "Our History") + "<BR>")
    hist = [
        ("November 1998", "Founders Chip Barkley and Wendy Okonkwo-Pugh write the Petz.com business plan on the back "
         "of a kibble bag during a layover in Denver. The plan has three steps: 1. Sell pet food online. "
         "2. ??? 3. Profit."),
        ("February 1999", "Series A financing of $10 million from Benchwarmer Capital. The partners love the business "
         "plan, especially step 2, which they describe as 'visionary.'"),
        ("April 1999", "Petz.com opens for business. First order: one squeaky ball, shipped to a golden retriever's "
         "owner in Tucson. Revenue: $1.99. Cost: $11.40. A tradition is born."),
        ("June 1999", "Argyle the Sock Dog is discovered in the lost-and-found box of a Fresno laundromat and hired "
         "on the spot. He signs his contract with his mouth, because he does not have hands. He is a hand."),
        ("August 1999", "Petz.com goes public on NASDAQ under the symbol PETZ at $11 per share. The stock closes its "
         "first day at $14 3/8. Argyle rings the opening bell, then eats it."),
        ("October 1999", "Series C financing of $50 million from Woof &amp; Tweet Ventures, mostly to pay for "
         "shipping 40-pound bags of litter."),
        ("December 1999", "PETZ hits an all-time high. Argyle appears on morning television, a parade balloon and "
         "the cover of a magazine about magazines. We buy thirty seconds of Super Bowl airtime."),
    ]
    c.append('<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH=586>')
    for d, t in hist:
        c.append('<TR><TD VALIGN=TOP WIDTH=110>%s</TD><TD VALIGN=TOP>%s</TD></TR>' % (font("<B>%s</B>" % d, 1, color="#336600"),
                                                                                      font(t, 2)))
    c.append('</TABLE><BR>')
    c.append('<A NAME="vc"></A>' + font("<B>A word from our investors</B>", 2, color="#336600") + "<BR>")
    c.append(font('"We have never seen a company lose money with such focus, such discipline, such enthusiasm. '
                  'Petz.com isn\'t burning cash; it\'s investing in the future of burning cash." '
                  '&mdash; a general partner at Benchwarmer Capital, from a hammock', 2, i=True))
    c.append('<BR><BR><A NAME="jobs"></A>' + font("<B>Jobs at Petz.com</B>", 2, color="#336600") + "<BR>")
    c.append(font("We're hiring! Open positions: Senior Java Developer, Director of Sock Relations, Chief Litter "
                  "Officer, Warehouse Chiropractor, and Accountant (must not faint easily). Benefits include stock options, "
                  "free snacks, a foosball table, and the right to bring your pet to work, as long as your pet doesn't "
                  "mind being asked about our margins.", 2))
    c.append('<BR><BR><A NAME="associates"></A>' + font("<B>Petz Associates Program</B>", 2, color="#336600") + "<BR>")
    c.append(font("Have a web site about your pet? Put a Petz.com banner on it and earn 15% of every sale you send "
                  "our way. Fifteen percent of our profits would be zero, so we're paying you out of revenue instead. "
                  "Our investors think this is a great idea. To join, e-mail your site's URL to "
                  "associates@petz.com.", 2))
    c.append('<BR><BR>' + font("<B>Press contact:</B> Monique Featherstonehaugh, 1-888-555-PETZ ext. 4.", 1))
    page("about.html", "About Us", "home", "about", "\n".join(c))


# ======================================================================= SEARCH
def search():
    body = js_products() + r"""
function getArg(name) {
  var s = location.search;
  var i = s.indexOf(name + "=");
  if (i < 0) return "";
  var j = s.indexOf("&", i);
  if (j < 0) j = s.length;
  var v = s.substring(i + name.length + 1, j);
  var out = "";
  for (var k = 0; k < v.length; k++) out = out + (v.charAt(k) == "+" ? " " : v.charAt(k));
  return unescape(out);
}
function htmlSafe(s) {
  var out = "";
  for (var i = 0; i < s.length; i++) {
    var ch = s.charAt(i);
    if (ch == "<") out = out + "&lt;";
    else if (ch == ">") out = out + "&gt;";
    else if (ch == "&") out = out + "&amp;";
    else if (ch == '"') out = out + "&quot;";
    else out = out + ch;
  }
  return out;
}
function money(n) {
  var c = Math.round(n * 100);
  var d = Math.floor(c / 100);
  c = c % 100;
  return "$" + d + "." + (c < 10 ? "0" : "") + c;
}
function doSearch() {
  var q = getArg("q");
  var F = '<FONT FACE="Verdana, Arial, Helvetica" SIZE=2>';
  var f1 = '<FONT FACE="Verdana, Arial, Helvetica" SIZE=1>';
  document.forms["search2"].q.value = q;
  if (isBlank(q)) {
    document.write(F + 'Type a word or two above and click <B>Search</B>. Try <I>litter</I>, ' +
      '<I>hamster</I>, <I>Y2K</I> or <I>sock</I>.</FONT>');
    return;
  }
  var words = q.toLowerCase().split(" ");
  var hits = new Array();
  for (var n = 0; n < PZids.length; n++) {
    var p = PZ[PZids[n]];
    var hay = (p.name + " " + p.cat + " " + p.text).toLowerCase();
    var ok = true;
    var any = false;
    for (var w = 0; w < words.length; w++) {
      if (words[w] == "") continue;
      any = true;
      if (hay.indexOf(words[w]) < 0) ok = false;
    }
    if (ok && any) hits[hits.length] = p;
  }
  document.write(F + 'Your search for <B>' + htmlSafe(q) + '</B> found <B>' + hits.length + '</B> product' +
    (hits.length == 1 ? '' : 's') + '.</FONT><BR><BR>');
  if (hits.length == 0) {
    document.write(F + 'No matches. Try fewer words, or browse by pet using the tabs above.<BR>' +
      '(If you were searching for "profit," we have been looking for it too.)</FONT>');
    return;
  }
  document.write('<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH=586>');
  for (var h = 0; h < hits.length; h++) {
    var r = hits[h];
    document.write('<TR><TD VALIGN=TOP><A HREF="product_' + r.id + '.html"><IMG SRC="images/thumb_' + r.id +
      '.gif" WIDTH=90 HEIGHT=90 BORDER=0></A></TD><TD VALIGN=TOP>' + F + '<A HREF="product_' + r.id + '.html"><B>' +
      r.name + '</B></A></FONT><BR>' + f1 + r.text.substring(0, 140) + '...<BR>List <S>' + money(r.list) +
      '</S> &middot; <FONT COLOR="#CC0000"><B>Our price ' + money(r.price) + '</B></FONT></FONT></TD></TR>');
    document.write('<TR><TD COLSPAN=2 BGCOLOR="#FFCC00"><IMG SRC="images/dot_clear.gif" WIDTH=1 HEIGHT=1></TD></TR>');
  }
  document.write('</TABLE>');
}
"""
    c = []
    c.append(font("<B>Search Petz.com</B>", 3, face=FA) + "<BR><BR>")
    c.append('<FORM NAME="search2" ACTION="search.html" METHOD="GET" onSubmit="return checkSearch(this)">'
             '<INPUT TYPE=TEXT NAME="q" SIZE=30 MAXLENGTH=100> '
             '<INPUT TYPE=IMAGE SRC="images/btn_search.gif" WIDTH=80 HEIGHT=24 BORDER=0 ALIGN=ABSMIDDLE ALT="Search"></FORM>')
    c.append(script("doSearch();\n"))
    page("search.html", "Search", "home", "search", "\n".join(c), head_js=script(body))


# ======================================================================= ADVICE
def advice():
    c = []
    c.append('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=586><TR><TD VALIGN=TOP WIDTH=100>%s</TD>'
             '<TD VALIGN=TOP>%s<BR>%s<BR><BR>%s</TD></TR></TABLE><BR>' % (
                 img("vet.gif", 90, 110, data.VET), font("<B>Ask the Vet</B>", 4, face=FA),
                 font("with %s" % data.VET, 2, color="#336600", b=True),
                 font("Dr. Bea Woofington has treated dogs, cats, birds, ferrets, reptiles and one very confused "
                      "llama in her 22 years of practice in Sacramento. Every week she answers your letters here on "
                      "Petz.com. She does not own any stock options. She asked us to mention that.", 2)))
    c.append(img("hdr_vet.gif", 200, 20, "Ask the Vet") + "<BR>")
    c.append('<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH=586>')
    for i, (t, q, who, ans) in enumerate(data.ADVICE):
        s = q if len(q) < 110 else q[:107].rsplit(" ", 1)[0] + "..."
        c.append('<TR><TD VALIGN=TOP>%s</TD><TD VALIGN=TOP><A HREF="advice_%d.html">%s</A><BR>%s</TD></TR>' % (
            img("arrow.gif", 11, 11, ""), i + 1, font("<B>%s</B>" % t, 2), font(s, 1, color="#666633", i=True)))
    c.append('</TABLE><BR>')
    c.append('<A NAME="ask"></A><TABLE BORDER=0 CELLPADDING=8 CELLSPACING=0 BGCOLOR="#FFFFCC" WIDTH=586><TR><TD>')
    c.append(font("<B>Ask Dr. Woofington a question</B>", 2, color="#336600") + "<BR>")
    c.append('<FORM NAME="ask" ACTION="advice_thanks.html" METHOD="GET" onSubmit="return checkAsk(this)">'
             '<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=0>'
             '<TR><TD ALIGN=RIGHT>%s</TD><TD><INPUT TYPE=TEXT NAME="pet" SIZE=20 MAXLENGTH=30></TD></TR>'
             '<TR><TD ALIGN=RIGHT>%s</TD><TD><SELECT NAME="kind"><OPTION>Dog<OPTION>Cat<OPTION>Fish<OPTION>Bird'
             '<OPTION>Ferret<OPTION>Reptile<OPTION>Small pet<OPTION>Sock puppet</SELECT></TD></TR>'
             '<TR><TD ALIGN=RIGHT VALIGN=TOP>%s</TD><TD><TEXTAREA NAME="question" ROWS=5 COLS=40 WRAP=VIRTUAL></TEXTAREA></TD></TR>'
             '<TR><TD></TD><TD><INPUT TYPE=IMAGE SRC="images/btn_ask.gif" WIDTH=100 HEIGHT=24 BORDER=0 ALT="Ask the Vet"></TD></TR>'
             '</TABLE></FORM>' % (font("Pet's name:", 1, b=True), font("Kind of pet:", 1, b=True),
                                 font("Your question:", 1, b=True)))
    c.append(font("Dr. Woofington's column is for general information only and is not a substitute for a visit to "
                  "your own veterinarian. If your pet is sick or hurt, call your vet right away.", 1, i=True))
    c.append('</TD></TR></TABLE>')
    js_ = script(r"""
function checkAsk(f) {
  if (isBlank(f.question.value)) {
    alert("Please type your question for Dr. Woofington.\nShe is good, but she can't read minds. Not even a parrot's.");
    f.question.focus();
    return false;
  }
  return true;
}
""")
    page("advice.html", "Pet Advice", "home", "advice", "\n".join(c), head_js=js_)

    for i, (t, q, who, ans) in enumerate(data.ADVICE):
        n = i + 1
        c = []
        c.append(font('<A HREF="index.html">home</A> &gt; <A HREF="advice.html">pet advice</A> &gt; %s' % t, 1) + "<BR><BR>")
        c.append('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=586><TR><TD VALIGN=TOP>')
        c.append(font("<B>%s</B>" % t, 4, face=FA) + "<BR>")
        c.append(font("Ask the Vet with %s" % data.VET, 1, color="#336600", b=True) + "<BR><BR>")
        c.append('<TABLE BORDER=0 CELLPADDING=8 CELLSPACING=0 BGCOLOR="#FFFFCC" WIDTH=100%%><TR><TD>%s<BR>%s</TD></TR></TABLE><BR>' % (
            font("<B>Q:</B> " + q, 2, i=True), font("&mdash; " + who, 1)))
        for k, para in enumerate(ans):
            c.append(font(("<B>A:</B> " if k == 0 else "") + para, 2) + "<BR><BR>")
        c.append(font("&mdash; Dr. Bea Woofington", 2, b=True) + "<BR><BR>")
        c.append('</TD><TD WIDTH=10>%s</TD><TD VALIGN=TOP WIDTH=100>%s</TD></TR></TABLE>' % (spc(10, 1),
                                                                                           img("vet.gif", 90, 110, data.VET)))
        nav = []
        if n > 1:
            nav.append('<A HREF="advice_%d.html">&lt;&lt; previous question</A>' % (n - 1))
        nav.append('<A HREF="advice.html">all questions</A>')
        nav.append('<A HREF="advice.html#ask">ask your own</A>')
        if n < len(data.ADVICE):
            nav.append('<A HREF="advice_%d.html">next question &gt;&gt;</A>' % (n + 1))
        c.append(font(" | ".join(nav), 1) + "<BR><BR>")
        c.append(font("This column is for general information only. If your pet is sick or hurt, call your own "
                      "veterinarian.", 1, color="#999999", i=True))
        page("advice_%d.html" % n, "Ask the Vet: " + t, "home", "advice", "\n".join(c))

    js_ = script(r"""
function getArg(name) {
  var s = location.search;
  var i = s.indexOf(name + "=");
  if (i < 0) return "";
  var j = s.indexOf("&", i);
  if (j < 0) j = s.length;
  var v = s.substring(i + name.length + 1, j);
  var out = "";
  for (var k = 0; k < v.length; k++) out = out + (v.charAt(k) == "+" ? " " : v.charAt(k));
  return unescape(out);
}
function htmlSafe(s) {
  var out = "";
  for (var i = 0; i < s.length; i++) {
    var ch = s.charAt(i);
    if (ch == "<") out = out + "&lt;";
    else if (ch == ">") out = out + "&gt;";
    else if (ch == "&") out = out + "&amp;";
    else if (ch == '"') out = out + "&quot;";
    else out = out + ch;
  }
  return out;
}
""")
    c = []
    c.append(font("<B>Thank you for your question!</B>", 4, face=FA) + "<BR><BR>")
    c.append('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=586><TR><TD VALIGN=TOP>')
    c.append(script(r"""var pet = htmlSafe(getArg("pet"));
var kind = htmlSafe(getArg("kind"));
if (pet == "") pet = "your pet";
document.write('<FONT FACE="Verdana, Arial, Helvetica" SIZE=2>Dr. Woofington has received your question about <B>' +
  pet + '</B>' + (kind != "" ? ' (' + kind.toLowerCase() + ')' : '') + '. ');
if (kind == "Sock puppet") document.write('She would like you to know that she is not that kind of doctor. ');
document.write('</FONT>');
"""))
    c.append(font("She receives about four thousand letters a week, so she can't answer every one personally, but "
                  "she reads them all, usually with a cat on her lap. Watch this space: your question might be next!", 2))
    c.append('<BR><BR>' + font("If your pet needs help right now, please don't wait for the column. "
                               "Call your own veterinarian.", 2, b=True))
    c.append('<BR><BR>' + font('<A HREF="advice.html">Back to Pet Advice</A> &middot; <A HREF="index.html">Home</A>', 2))
    c.append('</TD><TD VALIGN=TOP WIDTH=100>%s</TD></TR></TABLE>' % img("vet.gif", 90, 110, data.VET))
    page("advice_thanks.html", "Ask the Vet: Thank You", "home", "advice", "\n".join(c), head_js=js_)


# ======================================================================= FEATURES
def features():
    for n, (t, sub, kind, paras) in data.FEATURE_PAGES.items():
        c = []
        c.append(font('<A HREF="index.html">home</A> &gt; features &gt; %s' % t, 1) + "<BR><BR>")
        c.append('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=586><TR><TD VALIGN=TOP>')
        c.append(font("<B>%s</B>" % t, 4, face=FA) + "<BR>" + font(sub, 2, color="#666633", i=True) + "<BR>")
        c.append(font("By the Petz.com editors &middot; %s" % SITE_DATE, 1, color="#999999") + "<BR><BR>")
        c.append('</TD><TD VALIGN=TOP ALIGN=RIGHT>%s</TD></TR></TABLE>' % img("feature_%d.gif" % n, 120, 100, t))
        for para in paras:
            c.append(font(para, 2) + "<BR><BR>")
        others = [(m, v[0]) for m, v in data.FEATURE_PAGES.items() if m != n]
        c.append(font("<B>More features:</B> " + " | ".join('<A HREF="feature_%d.html">%s</A>' % o for o in others) +
                      ' | <A HREF="advice.html">Ask the Vet</A>', 1))
        page("feature_%d.html" % n, t, "home", "features", "\n".join(c))


# ======================================================================= SUPER BOWL
STORY = [
    "INT. LIVING ROOM - NIGHT. Rain on the window. ARGYLE, a sock puppet dog, gazes out at the street. "
    "He is feeling something. Possibly lint.",
    "EXT. STREET. A Petz.com delivery van pulls away from the curb. Argyle presses his button eyes to the glass and "
    "begins to sing.",
    "EXT. STREET - CONTINUOUS. Argyle chases the van down the block, still singing, ears flapping, "
    "with no visible means of locomotion.",
    "EXT. CURB. The van stops. The DRIVER hands Argyle a 40-pound bag of litter. Argyle hugs it. "
    "Little hearts float up. The driver rubs his back.",
    "TITLE CARD on lime green: Petz.com. Because pets can't drive! Argyle winks.",
    "INT. PETZ.COM ACCOUNTING DEPT. An invoice. A small sound. Our ACCOUNTANT faints. (Director's cut only.)",
]

SCRIPT = [
    ("", "(Soft piano. Rain. ARGYLE at the window.)"),
    ("ARGYLE (singing)", "Oh, delivery van, with your big rubber wheels,<BR>"
                         "you bring me my kibble, you don't bring the bills..."),
    ("", "(The van pulls away. Argyle turns to camera, devastated.)"),
    ("ARGYLE (singing, louder)", "Don't go, little truck, don't you leave me this way,<BR>"
                                 "I can't follow you, darling, I'm a sock, and I'm gray..."),
    ("DRIVER (off-camera)", "You're blue, actually. Sort of an argyle."),
    ("ARGYLE (singing)", "...I'm a sock, and I'm BLUE!<BR>And I'd drive after you,<BR>"
                         "but pets can't drive, so I'll sing it to you!"),
    ("", "(The van stops. The DRIVER hands over a 40-lb bag of litter. Argyle hugs it.)"),
    ("ARGYLE (spoken, to camera)", "Forty pounds. Five forty-nine. Somebody call my accountant."),
    ("ANNOUNCER (V.O.)", "Petz.com. Everything for your pet, delivered to your door. Because pets can't drive."),
    ("", "(Title card. Jingle sting. Argyle winks. FADE OUT.)"),
]

def superbowl():
    c = []
    c.append(font("<B>Our Super Bowl Ad</B>", 4, face=FA) + "<BR>")
    c.append(font("World premiere: Super Bowl XXXIV, January 30, 2000, third quarter, right after the beer frogs*", 2,
                  color="#336600", b=True) + "<BR>")
    c.append(font("*not actual frogs", 1, color="#999999", i=True) + "<BR><BR>")
    c.append(font("For the first time ever, the Petz.com marketing team is proud to share the storyboards for our "
                  "first national television commercial, <B>\"Don't Leave Me, Delivery Van.\"</B> It was written in "
                  "eleven minutes, focus-grouped for eleven weeks, and approved by our board in one emotional vote "
                  "(Argyle abstained, citing a conflict of interest).", 2))
    c.append('<BR><BR>' + img("hdr_storyboard.gif", 300, 20, "The Storyboard") + "<BR>")
    c.append('<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH=586>')
    for row in range(2):
        c.append('<TR>')
        for col in range(3):
            n = row * 3 + col
            c.append('<TD VALIGN=TOP WIDTH=195>%s<BR>%s</TD>' % (img("sb%d.gif" % (n + 1), 180, 135,
                                                                     "Frame %d" % (n + 1), ""),
                                                                 font(STORY[n], 1)))
        c.append('</TR>')
    c.append('</TABLE><BR>')
    c.append(img("hdr_script.gif", 300, 20, "The Script") + "<BR>")
    c.append('<TABLE BORDER=0 CELLPADDING=8 CELLSPACING=0 BGCOLOR="#FFFFCC" WIDTH=586><TR><TD>')
    c.append('<FONT FACE="Courier New, Courier" SIZE=2><B>"DON\'T LEAVE ME, DELIVERY VAN"</B><BR>:30 TV spot. '
             'Agency: Hound &amp; Holler, San Francisco. FINAL FINAL v7.<BR><BR>')
    for who, line in SCRIPT:
        if who:
            c.append('<CENTER><B>%s</B></CENTER><BLOCKQUOTE>%s</BLOCKQUOTE>' % (who, line))
        else:
            c.append('<I>%s</I><BR><BR>' % line)
    c.append('</FONT></TD></TR></TABLE><BR>')
    c.append(font("<B>Hear the jingle!</B> Argyle's theme, as heard in the spot (MIDI, 2 KB, sounds best on a "
                  "Sound Blaster):", 2) + "<BR><BR>")
    c.append('<EMBED SRC="images/jingle.mid" AUTOSTART=false HIDDEN=false LOOP=false WIDTH=144 HEIGHT=60>'
             '<NOEMBED><BGSOUND SRC="images/jingle.mid" LOOP=1></NOEMBED><BR>')
    c.append(font('<A HREF="images/jingle.mid">Download jingle.mid</A>', 1) + "<BR><BR>")
    c.append(img("hdr_news.gif", 200, 20, "By the numbers") + "<BR>")
    c.append('<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0>')
    for k, v in (("Cost of 30 seconds of airtime", "$2.2 million"),
                 ("Cost per second", "$73,333.33"),
                 ("Petz.com revenue last quarter", "$619,000"),
                 ("Airtime, measured in years of revenue", "roughly 9 (we did the math, then lay down)"),
                 ("Number of socks harmed in production", "0 (Argyle had a stunt double)"),
                 ("Bags of litter we could have shipped instead", "about 45,800, at a loss of $1.6 million"),
                 ("Which, you'll note, is cheaper", "We noticed too. Too late.")):
        c.append('<TR><TD>%s</TD><TD>%s</TD></TR>' % (font(k + ":", 2), font("<B>%s</B>" % v, 2, color="#CC0000")))
    c.append('</TABLE><BR>')
    c.append(font("Want your own Argyle? He's available as an 18-inch plush puppet, sold at a loss, of course. "
                  '<A HREF="mascot.html">Meet Argyle</A> or <A HREF="product_m01.html">buy him now</A>.', 2))
    page("superbowl.html", "Our Super Bowl Ad", "home", "superbowl", "\n".join(c))


# ======================================================================= MASCOT
FAN_MAIL = [
    ("Dear Argyle, I am 7 and I have a sock that looks just like you except it is white and has a hole. "
     "Can it be your brother? Please write back.", "Tyler, age 7, Sioux Falls, South Dakota"),
    ("Argyle, I watched you on the morning news and I laughed so hard I spilled my coffee on my modem. "
     "I am now writing this from the library. Worth it.", "Patricia M., Raleigh, North Carolina"),
    ("To the sock: my dog barks every time you come on TV. I think he is jealous. He doesn't have a bow tie. "
     "Where can I get one?", "Hector V., El Paso, Texas"),
    ("I bought 500 shares of PETZ because of you. My wife says I should have bought the puppet instead. "
     "Which one is going to be worth more in a year? Just curious.", "A shareholder, Scottsdale, Arizona"),
]

def mascot():
    c = []
    c.append('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=586><TR><TD VALIGN=TOP>')
    c.append(font("<B>Meet Argyle the Sock Dog</B>", 4, face=FA) + "<BR>")
    c.append(font("Spokes-sock, Petz.com", 2, color="#336600", b=True) + "<BR><BR>")
    c.append(font("Argyle was discovered in June 1999 in the lost-and-found box of a self-serve laundromat in Fresno, "
                  "California, where he had been waiting for his matching sock for nearly three years. It never came. "
                  "But Petz.com did.", 2) + "<BR><BR>")
    c.append(font("Today Argyle is the most recognized sock in America. He has appeared on three morning talk shows, "
                  "one late-night talk show, a parade balloon and a cereal box (regional). He answers all his own fan mail, "
                  "with help.", 2) + "<BR><BR>")
    c.append('<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#FFFFCC">')
    for k, v in (("Species", "Dog (sock)"), ("Height", "18 inches, including arm"), ("Eyes", "Two buttons, mismatched"),
                 ("Mouth", "Red felt, hand-stitched"), ("Bow tie", "Genuine twist-tie"),
                 ("Favorite food", "Lint"), ("Hobbies", "Singing to vans, the stock ticker"),
                 ("Fear", "The spin cycle"), ("Catchphrase", "\"Because pets can't drive!\"")):
        c.append('<TR><TD>%s</TD><TD>%s</TD></TR>' % (font("<B>%s:</B>" % k, 1), font(v, 1)))
    c.append('</TABLE>')
    c.append('</TD><TD WIDTH=10>%s</TD><TD VALIGN=TOP>%s</TD></TR></TABLE><BR>' % (
        spc(10, 1), img("argyle_big.gif", 180, 240, "Argyle the Sock Dog")))
    c.append(img("hdr_merch.gif", 300, 20, "Official Merchandise") + "<BR>")
    c.append('<TABLE CELLSPACING=0 CELLPADDING=4 BORDER=0 WIDTH=586><TR>')
    merch = [p for p in P if p["cat"] == "mascot"]
    for p in merch[:2]:
        c.append('<TD VALIGN=TOP WIDTH=293>%s</TD>' % product_cell(p))
    c.append('</TR><TR><TD VALIGN=TOP>%s</TD><TD VALIGN=TOP>%s</TD></TR></TABLE>' % (
        product_cell(merch[2]),
        font("<B>Note:</B> each official plush Argyle costs us $14.00 to make and sells for $9.99. "
             "Collect them all, and help us lose money faster!", 1, i=True)))
    c.append('<BR>' + img("hdr_letters.gif", 300, 20, "Fan Mail") + "<BR>")
    for letter, who in FAN_MAIL:
        c.append('<TABLE BORDER=0 CELLPADDING=6 CELLSPACING=0 WIDTH=586><TR><TD>%s<BR>%s</TD></TR></TABLE>' % (
            font('"%s"' % letter, 2, i=True), font("&mdash; " + who, 1, color="#336600")))
    c.append('<BR>' + font("Write to Argyle: Argyle, c/o Petz.com, 435 Brannan Street, San Francisco, CA 94107. "
                           "He reads everything, mostly upside down.", 1))
    c.append('<BR><BR>' + font('See Argyle in action: <A HREF="superbowl.html">our Super Bowl ad</A>.', 2))
    page("mascot.html", "Meet Argyle", "home", "mascot", "\n".join(c))


# ======================================================================= INVESTORS
def investor():
    c = []
    c.append(font("<B>Investor Relations</B>", 4, face=FA) + "<BR>")
    c.append(font("PETZ (NASDAQ) &middot; Last trade: 87 1/4 &middot; Up, obviously", 2, color="#336600", b=True))
    c.append("<BR><BR>" + img("chart.gif", 420, 250, "PETZ share price since IPO"))
    c.append("<BR><BR>" + font("Since our initial public offering in August 1999, PETZ shares have climbed from $11 to "
                               "$87 1/4, a gain of nearly 700 percent. Over the same period, our losses have climbed "
                               "at almost exactly the same rate. Analysts call this 'remarkable.' We call it 'consistency.'", 2))
    c.append("<BR><BR>" + img("hdr_news.gif", 200, 20, "Key figures") + "<BR>")
    c.append('<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#FFFFCC" WIDTH=420>')
    for k, v in (("Revenue, Q3 1999", "$619,000"), ("Cost of goods sold, Q3 1999", "$1,140,000"),
                 ("Gross margin", "-84% (the minus sign is silent)"), ("Advertising, Q3 1999", "$11,800,000"),
                 ("Average loss per order", "$38.20"), ("Burn rate", "$3,100 per minute"),
                 ("Cash on hand", "Enough until about next Thursday*"), ("Employees", "312 (and Argyle)"),
                 ("Socks under contract", "1")):
        c.append('<TR><TD>%s</TD><TD ALIGN=RIGHT>%s</TD></TR>' % (font(k, 2), font("<B>%s</B>" % v, 2)))
    c.append('</TABLE>' + font("*Not counting the Series D, which we are confident will close any day now.", 1,
                               color="#999999", i=True) + "<BR><BR>")
    c.append(font("At our current burn rate, Petz.com spends a used compact car's worth of money in the time it takes "
                  "you to read this paragraph. Don't worry: we're reading it very slowly.", 2) + "<BR><BR>")
    c.append(img("hdr_faq.gif", 300, 20, "Shareholder FAQ") + "<BR>")
    for q, a in (("When will Petz.com be profitable?",
                  "Next quarter. We have said this every quarter since 1998, and we will keep saying it until it is true "
                  "or until we run out of quarters."),
                 ("Why do you lose money on every order?",
                  "Pet food is heavy. Shipping heavy things is expensive. Customers do not like to pay for shipping. "
                  "Our plan is to lose a little money on a very large number of orders, which our investors assure us "
                  "will eventually turn into a lot of money. They have not said which direction."),
                 ("Is the stock a good buy?",
                  "We are a pet supply store with a sock for a spokesman. Please talk to a licensed financial advisor, "
                  "a trusted friend, and possibly your dog before buying any stock, including ours."),
                 ("Where is the annual meeting?",
                  "The 2000 annual meeting will be held at our San Francisco headquarters. Snacks will be provided, "
                  "at a loss.")):
        c.append(font("<B>%s</B>" % q, 2, color="#336600") + "<BR>" + font(a, 2) + "<BR><BR>")
    c.append(img("hdr_news.gif", 200, 20, "Press releases") + "<BR>")
    for d, t in (("12/13/99", "Petz.com Announces Record Revenue, Record Losses, Record Sock Appearances"),
                 ("11/30/99", "Petz.com Buys Thirty Seconds of Super Bowl XXXIV Airtime"),
                 ("10/18/99", "Petz.com Closes $50 Million Series C; Immediately Ships It as Cat Litter"),
                 ("08/11/99", "Petz.com Prices Initial Public Offering at $11 Per Share")):
        c.append(font("<B>%s</B> &nbsp; %s" % (d, t), 1) + "<BR>")
    c.append("<BR>" + font("Forward-looking statements: this page contains statements about the future. The future is "
                           "uncertain. So are we. Actual results may differ materially, and also financially.", 1,
                           color="#999999", i=True))
    page("investor.html", "Investor Relations", "home", "investor", "\n".join(c))


# ======================================================================= LIQUIDATION (hidden)
def liquidation():
    c = []
    c.append(font("<B>November 7, 2000</B>", 2, color="#CC0000") + "<BR>")
    c.append(img("liq_banner.gif", 415, 80, "Everything must go, including us") + "<BR><BR>")
    c.append('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=586><TR><TD VALIGN=TOP>')
    c.append(img("hdr_letter.gif", 300, 20, "A letter from Argyle") + "<BR>")
    c.append(font("Dear friends,<BR><BR>"
                  "Today Petz.com is closing its doors. I want you to hear it from me, a sock, before you hear it "
                  "from the evening news, a newspaper, or a man in a suit holding a clipboard in our lobby. "
                  "(He's very nice. He's counting the chairs.)<BR><BR>"
                  "We had a good run. We shipped you kibble, litter, crickets and hamster wheels. We shipped every "
                  "one of them for less than it cost us, which in hindsight was the problem. We sang at the Super Bowl. "
                  "We rang a bell. I was a parade balloon for one glorious Thanksgiving.<BR><BR>"
                  "To our customers: thank you. To our pets: we're sorry about the packing peanuts. To our investors: "
                  "we are also sorry, but you did read the business plan, including step 2.<BR><BR>"
                  "I'll be fine. I'm a sock. There is always a drawer somewhere.<BR><BR>"
                  "Love,<BR><B>Argyle</B><BR>(former spokes-sock)", 2))
    c.append('</TD><TD WIDTH=10>%s</TD><TD VALIGN=TOP>%s</TD></TR></TABLE><BR>' % (
        spc(10, 1), img("argyle_sad.gif", 200, 220, "Argyle, will fetch for food")))
    c.append(font("<B>Argyle is looking for work.</B> Experienced spokes-sock seeks new hand. Skills: lip-sync, "
                  "national television, parade balloon, singing to vehicles, remaining upbeat on a falling stock. "
                  "Will relocate. Will fetch. References available from a Fresno laundromat.", 2) + "<BR><BR>")
    c.append(img("hdr_inventory.gif", 300, 20, "Remaining inventory, 90% off") + "<BR>")
    c.append('<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0 WIDTH=586>')
    c.append('<TR BGCOLOR="#000000"><TD>%s</TD><TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD></TR>' % (
        font("<B>Item</B>", 1, color="#FFFFFF"), font("<B>Was</B>", 1, color="#FFFFFF"),
        font("<B>Now</B>", 1, color="#FFFFFF"), font("<B>Left</B>", 1, color="#FFFFFF")))
    left = [4100, 212, 1730, 88, 940, 12, 655, 7, 3002, 41, 77, 19]
    for i, p in enumerate(P[::4]):
        bg = "#FFFFCC" if i % 2 else "#FFFFFF"
        c.append('<TR BGCOLOR="%s"><TD>%s</TD><TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD></TR>' % (
            bg, font(p["name"], 1), font("<S>%s</S>" % money(p["price"]), 1),
            font("<B>%s</B>" % money(round(p["price"] * 0.10, 2)), 1, color="#CC0000"), font(str(left[i % len(left)]), 1)))
    c.append('<TR BGCOLOR="#FFFFCC"><TD>%s</TD><TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD></TR>' % (
        font("Argyle plush puppets (unsold)", 1), font("<S>$9.99</S>", 1), font("<B>$0.99</B>", 1, color="#CC0000"),
        font("38,000", 1)))
    c.append('<TR><TD>%s</TD><TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD></TR>' % (
        font("Ergonomic mesh office chairs", 1), font("<S>$740.00</S>", 1), font("<B>$40.00</B>", 1, color="#CC0000"),
        font("296", 1)))
    c.append('<TR BGCOLOR="#FFFFCC"><TD>%s</TD><TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD></TR>' % (
        font("Foosball table, lightly used (heavily)", 1), font("<S>$1,200.00</S>", 1),
        font("<B>$15.00</B>", 1, color="#CC0000"), font("1", 1)))
    c.append('</TABLE><BR>')
    c.append('%s %s<BR><BR>' % (img("btn_soldout.gif", 110, 24, "Repossessed"),
                                font("Our shopping cart has been repossessed. All sales final. All sales, in fact, "
                                     "are final.", 1, i=True)))
    c.append(img("hdr_faq.gif", 300, 20, "What happens now?") + "<BR>")
    c.append(font("<B>What about my order?</B> Orders placed before today will be shipped. At a loss. "
                  "For old times' sake.<BR><BR>"
                  "<B>What about my stock?</B> Please see the ticker above. Try not to watch it for too long.<BR><BR>"
                  "<B>What about Argyle?</B> Argyle has received several offers, including a car insurance company, "
                  "a sock drawer in Ohio and a very nice family in Fresno. He is weighing his options. "
                  "He weighs two ounces.", 2))
    c.append('<BR><BR>' + img("stamp.gif", 150, 40, "Liquidated"))
    page("liquidation.html", "Everything Must Go", "home", "liquidation", "\n".join(c), liquidation=True)


def main():
    for f in glob.glob(os.path.join(SITE, "*.html")):
        os.remove(f)
    home()
    for cat, label, tag, short in CATEGORIES:
        category(cat, label, tag, short)
    for i, p in enumerate(P):
        product(p, i)
    cart(); checkout(); thankyou(); myaccount(); help_page(); about(); search(); advice(); features()
    superbowl(); mascot(); investor(); liquidation()
    print("wrote %d pages" % len(written))


if __name__ == "__main__":
    main()
