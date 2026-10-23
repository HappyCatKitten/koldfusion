#!/usr/bin/env python3
"""Generates every page of CNM Interactive (a December 1999 news-site parody).

    python3 tools/gfx.py && python3 tools/gen.py      (from the site folder)

Static HTML 3.2-ish output, relative URLs only, 1999-style JavaScript (ES3: var, function,
document.write, document.forms, document.images, location.search, setTimeout).
"""
import json, os, sys, zlib
sys.dont_write_bytecode = True
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data
from data import STORIES, SEC, SECTIONS

ROOT = os.path.normpath(os.path.join(HERE, ".."))
BY_SLUG = dict((s["slug"], s) for s in STORIES)
WRITTEN = []

ARIAL = 'FACE="Arial, Helvetica"'
VERD = 'FACE="Verdana, Arial, Helvetica"'


# ------------------------------------------------------------------ helpers
def esc(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    return t.encode("ascii", "xmlcharrefreplace").decode("ascii")


def jsstr(t):
    """a JavaScript string literal (ES3-safe, ASCII only)"""
    return json.dumps(t, ensure_ascii=True).replace("</", "<\\/")


def write(rel, html):
    p = os.path.join(ROOT, rel)
    d = os.path.dirname(p)
    if not os.path.isdir(d):
        os.makedirs(d)
    with open(p, "w", encoding="ascii", errors="xmlcharrefreplace", newline="\n") as f:
        f.write(html)
    WRITTEN.append(rel)


def prefix(rel):
    return "../" * rel.count("/")


def story_url(s):
    return "1999/%s/12/%02d/%s/index.html" % (SEC[s["section"]][2], s["day"], s["slug"])


def sec_url(code):
    return "%s/index.html" % SEC[code][2]


def date_str(s):
    return "December %d, 1999" % s["day"]


def time_str(s, gmt=True):
    h, m = [int(x) for x in s["hhmm"].split(":")]
    ap = "a.m." if h < 12 else "p.m."
    h12 = h % 12 or 12
    t = "%d:%02d %s EST" % (h12, m, ap)
    if gmt:
        t += " (%02d%02d GMT)" % ((h + 5) % 24, m)
    return t


def ring_href(P, name):
    return "%s../%s/index.html" % (P, name)


def site_href(P, kind, target):
    return ring_href(P, target) if kind == "ring" else P + target


def related(s, n=4):
    out = []
    for o in STORIES:
        if o is not s and set(o["tags"]) & set(s["tags"]) and o["section"] == s["section"]:
            out.append(o)
    for o in STORIES:
        if o is not s and o["section"] == s["section"] and o not in out:
            out.append(o)
    for o in STORIES:
        if o is not s and set(o["tags"]) & set(s["tags"]) and o not in out:
            out.append(o)
    return out[:n]


def sec_stories(code):
    return [s for s in STORIES if s["section"] == code]


# ------------------------------------------------------------------ page chrome
def head(title, P, onload="", refresh=False, script=""):
    meta = '<META HTTP-EQUIV="REFRESH" CONTENT="1800">\n' if refresh else ""
    ol = ' onLoad="%s"' % onload if onload else ""
    return """<HTML>
<HEAD>
<TITLE>%s</TITLE>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1">
%s%s</HEAD>
<BODY BGCOLOR="#FFFFFF" TEXT="#000000" LINK="#003366" VLINK="#663366" ALINK="#CC0000" MARGINWIDTH=0 MARGINHEIGHT=0 LEFTMARGIN=0 TOPMARGIN=0%s>
<A NAME="top"></A>
""" % (title, meta, script, ol)


def banner(P, rel):
    img, kind, target, alt = data.BANNERS[zlib.crc32(rel.encode()) % len(data.BANNERS)]
    return ('<A HREF="%s" TARGET="_top"><IMG SRC="%simages/%s" WIDTH=468 HEIGHT=60 BORDER=0 ALT="%s"></A>'
            % (site_href(P, kind, target), P, img, esc(alt)))


def search_form(P, name, light=False):
    col = ' COLOR="#FFFFFF"' if light else ""
    return """<FORM ACTION="%ssearch.html" METHOD=GET NAME="%s">
<FONT %s SIZE=1%s><B>Search</B></FONT><BR>
<SELECT NAME="sites"><OPTION VALUE="CNM" SELECTED>CNM.com<OPTION VALUE="WEB">The Web</SELECT><BR>
<INPUT TYPE=TEXT NAME="query" SIZE=8><INPUT TYPE=SUBMIT VALUE="Find">
</FORM>""" % (P, name, VERD, col)


def top(P, rel, label="MAIN PAGE"):
    sites = [("CNM", "index.html"), ("CNMfn", "BUSINESS/index.html"), ("CNM/SI", "SPORTS/index.html"),
             ("Politics", "POLITICS/index.html"), ("myCNM", "customnews.html"), ("Y2K Special", "y2k/index.html"),
             ("Weather", "weather.html")]
    opts = "".join('<OPTION VALUE="%s%s">%s' % (P, u, t) for t, u in sites)
    links = [("Video", "video.html"), ("Audio", "audio.html"), ("Headline News Brief", "brief.html"),
             ("Free E-mail", "email.html"), ("Feedback", "feedback.html")]
    lk = "&nbsp;|&nbsp;".join('<A HREF="%s%s"><FONT COLOR="#FFFFFF">%s</FONT></A>' % (P, u, t) for t, u in links)
    return """<TABLE WIDTH=770 BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR>
<TD WIDTH=167 VALIGN=BOTTOM><A HREF="%sindex.html"><IMG SRC="%simages/logo.gif" WIDTH=167 HEIGHT=40 BORDER=0 ALT="CNM Interactive"></A></TD>
<TD WIDTH=10><IMG SRC="%simages/1.gif" WIDTH=10 HEIGHT=1 ALT=""></TD>
<TD WIDTH=468 ALIGN=CENTER VALIGN=TOP>%s</TD>
<TD WIDTH=125 ALIGN=RIGHT VALIGN=BOTTOM>%s</TD>
</TR>
<TR><TD COLSPAN=4><IMG SRC="%simages/1.gif" WIDTH=1 HEIGHT=4 ALT=""></TD></TR>
</TABLE>
<TABLE WIDTH=770 BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR BGCOLOR="#666699">
<TD WIDTH=125 VALIGN=MIDDLE><FORM NAME="cnmsites"><FONT %s SIZE=1>
<SELECT NAME="go" onChange="if (this.selectedIndex != 0) window.location = this.options[this.selectedIndex].value;">
<OPTION VALUE="">CNM Sites%s
</SELECT></FONT></FORM></TD>
<TD WIDTH=15><IMG SRC="%simages/1.gif" WIDTH=15 HEIGHT=1 ALT=""></TD>
<TD WIDTH=630 ALIGN=RIGHT VALIGN=MIDDLE><FONT %s SIZE=1 COLOR="#FFFFFF">%s&nbsp;&nbsp;</FONT></TD>
</TR>
<TR>
<TD WIDTH=125 BGCOLOR="#333366" HEIGHT=18>&nbsp;<IMG SRC="%simages/newarrow.gif" WIDTH=11 HEIGHT=11 ALIGN=RIGHT HSPACE=3 ALT="*"><A HREF="%sindex.html"><FONT %s SIZE=1 COLOR="#FFFFFF"><B>MAIN PAGE</B></FONT></A></TD>
<TD WIDTH=15>&nbsp;</TD>
<TD WIDTH=630><FONT %s SIZE=1><A HREF="%salmanac.html">%s</A> -- %s</FONT></TD>
</TR>
</TABLE>
""" % (P, P, P, banner(P, rel), search_form(P, "seek_top"), P, VERD, opts, P, VERD, lk,
       P, P, VERD, VERD, P, data.TODAY, data.UPDATED)


def nav_top(P, current=None):
    rows = []
    for code, nav, dirn, text, blurb in SECTIONS:
        lab = nav
        if code == current:
            lab = '<FONT COLOR="#CC0000">%s</FONT>' % nav
        rows.append('&nbsp;<A HREF="%s%s/index.html">%s</A><BR>' % (P, dirn, lab))
    rows.append('&nbsp;<A HREF="%sindepth.html">IN-DEPTH</A><BR>' % P)
    rows.append('&nbsp;<A HREF="%slocal.html">LOCAL</A><BR>' % P)
    return """<TABLE WIDTH=125 BORDER=0 CELLPADDING=2 CELLSPACING=0>
<TR><TD BGCOLOR="#CCCCFF"><FONT %s SIZE=1><B>
%s
</B><HR SIZE=1 WIDTH="90%%" NOSHADE>
&nbsp;<A HREF="%scustomnews.html">Custom News</A><BR>
&nbsp;<A HREF="%sbrief.html">Headline News brief</A><BR>
&nbsp;<A HREF="%squiz.html">news quiz</A><BR>
&nbsp;<A HREF="%salmanac.html">daily almanac</A><BR><BR>
</FONT></TD></TR>
<TR BGCOLOR="#666699"><TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>&nbsp;MULTIMEDIA:</B></FONT></TD></TR>
<TR><TD BGCOLOR="#CCCCFF"><FONT %s SIZE=1>
&nbsp;<A HREF="%svideo.html">video</A><BR>
&nbsp;<A HREF="%saudio.html">audio</A><BR>
&nbsp;<A HREF="%sy2k/index.html">Y2K countdown</A><BR>
&nbsp;<A HREF="%sweather.html">weather maps</A><BR><BR>
</FONT></TD></TR>
</TABLE>""" % (VERD, "\n".join(rows), P, P, P, P, VERD, VERD, P, P, P, P)


def nav_bottom(P):
    return """<TABLE WIDTH=125 BORDER=0 CELLPADDING=2 CELLSPACING=0 BGCOLOR="#CCCCFF">
<TR BGCOLOR="#666699"><TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>&nbsp;E-MAIL:</B></FONT></TD></TR>
<TR><TD><FONT %s SIZE=1>Subscribe to one of our <A HREF="%scustomnews.html">news e-mail lists</A>.<BR>Enter your address:</FONT>
<FORM NAME="emailform" ACTION="%scustomnews.html" METHOD=GET><INPUT TYPE=TEXT NAME="email" SIZE=10>&nbsp;<INPUT TYPE=SUBMIT VALUE="Go"></FORM></TD></TR>
<TR BGCOLOR="#666699"><TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>&nbsp;DISCUSSION:</B></FONT></TD></TR>
<TR><TD><FONT %s SIZE=1>
&nbsp;<A HREF="%squickvote.html">QuickVote</A><BR>
&nbsp;<A HREF="%squickvote_archive.html">past votes</A><BR>
&nbsp;<A HREF="%sfeedback.html">feedback</A><BR><BR>
</FONT></TD></TR>
<TR BGCOLOR="#666699"><TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>&nbsp;CNM WEB SITES:</B></FONT></TD></TR>
<TR><TD>
<MAP NAME="cnmwebsites">
<AREA SHAPE="rect" COORDS="0,0,63,19" HREF="%scustomnews.html" ALT="myCNM">
<AREA SHAPE="rect" COORDS="64,0,120,19" HREF="%sSPORTS/index.html" ALT="CNM/SI">
<AREA SHAPE="rect" COORDS="0,20,63,39" HREF="%sPOLITICS/index.html" ALT="Politics">
<AREA SHAPE="rect" COORDS="64,20,120,39" HREF="%sBUSINESS/index.html" ALT="CNMfn">
</MAP>
<IMG SRC="%simages/websites.gif" WIDTH=121 HEIGHT=40 BORDER=0 USEMAP="#cnmwebsites" ALT="CNM Web sites">
</TD></TR>
<TR><TD><FONT %s SIZE=1>
&nbsp;<A HREF="%sy2k/index.html">Y2K Special</A><BR>
&nbsp;<A HREF="%sindepth.html">In-Depth</A><BR>
&nbsp;<A HREF="%slocal.html">Local news</A><BR><BR>
</FONT></TD></TR>
</TABLE>""" % (VERD, VERD, P, P, VERD, VERD, P, P, P, VERD, P, P, P, P, P, VERD, P, P, P)


def webring(P):
    hub = P + "../../web1999/index.html"
    me = data.RING.index("cnm")
    prev = ring_href(P, data.RING[me - 1])
    nxt = ring_href(P, data.RING[(me + 1) % len(data.RING)])
    lst = ",".join('"%s"' % ring_href(P, n) for n in data.RING)
    return """<SCRIPT LANGUAGE="JavaScript1.2"><!--
function ringRandom() {
  var list = new Array(%s);
  window.location = list[Math.floor(Math.random() * list.length)];
  return false;
}
//--></SCRIPT>
<CENTER><TABLE BORDER=2 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#C0C0C0"><TR><TD ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=1>
<A HREF="%s">&lt;&lt; Prev</A> | <A HREF="%s" onClick="return ringRandom();">Random</A> | <B><A HREF="%s">The 1999 Web Ring</A></B> &middot; CNM Interactive is site 12 of 12 | <A HREF="%s">Next &gt;&gt;</A>
</FONT></TD></TR></TABLE></CENTER>
""" % (lst, prev, hub, hub, nxt)


def footer(P, left=True):
    lcell = '<TD WIDTH=125 BGCOLOR="#CCCCFF" VALIGN=TOP><IMG SRC="%simages/1.gif" WIDTH=125 HEIGHT=1 ALT=""></TD>' % P if left else \
            '<TD WIDTH=125><IMG SRC="%simages/1.gif" WIDTH=125 HEIGHT=1 ALT=""></TD>' % P
    return """<TABLE WIDTH=770 BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR>%s<TD WIDTH=15>&nbsp;</TD>
<TD WIDTH=630>
<HR NOSHADE SIZE=1>
<CENTER><FONT %s SIZE=1>
<A HREF="#top">Back to the top</A><BR><BR>
&copy; 1999 Cable News Mobile. All Rights Reserved.<BR>
<A HREF="%sterms.html">The fine print under which we let you read any of this</A>.
<A HREF="%sprivacy.html">What we do (and mostly don't do) with your cookies</A>.<BR>
<A HREF="%sfeedback.html">Write to CNM</A> | <A HREF="%sindex.html">CNM.com main page</A> | <A HREF="%ssearch.html">Search</A><BR><BR>
<A HREF="%sindex.html"><IMG SRC="%simages/logo_small.gif" WIDTH=84 HEIGHT=20 BORDER=0 ALT="CNM" ALIGN=MIDDLE></A>
&nbsp;<IMG SRC="%simages/powered_by_kf.gif" WIDTH=88 HEIGHT=31 BORDER=0 ALT="Powered by KoldFusion" ALIGN=MIDDLE>
</FONT></CENTER><BR>
%s<BR>
</TD></TR></TABLE>
</BODY>
</HTML>
""" % (lcell, ARIAL, P, P, P, P, P, P, P, P, webring(P))


def page(rel, title, content, current=None, onload="", script="", label="MAIN PAGE"):
    """standard inner page: header, lavender nav column, 630px content column, footer"""
    P = prefix(rel)
    html = head(title, P, onload=onload, script=script) + top(P, rel, label) + """<TABLE WIDTH=770 BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR>
<TD WIDTH=125 VALIGN=TOP BGCOLOR="#CCCCFF">%s
%s</TD>
<TD WIDTH=15><IMG SRC="%simages/1.gif" WIDTH=15 HEIGHT=1 ALT=""></TD>
<TD WIDTH=630 VALIGN=TOP><BR>
%s
</TD>
</TR>
</TABLE>
""" % (nav_top(P, current), nav_bottom(P), P, content) + footer(P)
    write(rel, html)


def title_gif(P, name, alt, link=None):
    img = '<IMG SRC="%simages/%s" WIDTH=470 HEIGHT=40 BORDER=0 ALT="%s">' % (P, name, alt)
    if link:
        img = '<A HREF="%s">%s</A>' % (link, img)
    return img + "<BR>\n"


def box_title(text, width="100%"):
    return ('<TABLE WIDTH="%s" BORDER=0 CELLPADDING=2 CELLSPACING=0><TR><TD WIDTH=5 BGCOLOR="#FF6600">&nbsp;</TD>'
            '<TD BGCOLOR="#666666" NOWRAP><FONT %s SIZE=2 COLOR="#FFFFFF"><B>&nbsp;%s</B></FONT></TD></TR></TABLE>'
            % (width, ARIAL, text))


# ------------------------------------------------------------------ JavaScript snippets
COUNTDOWN_JS = """<SCRIPT LANGUAGE="JavaScript"><!--
// counts down to the next January 1 -- which, as far as this page is concerned, is always the year 2000
function two(n) { return (n < 10 ? "0" : "") + n; }
function cdParts() {
  var now = new Date();
  var target = new Date(now.getFullYear() + 1, 0, 1, 0, 0, 0);
  var s = Math.floor((target.getTime() - now.getTime()) / 1000);
  if (s < 0) s = 0;
  var d = Math.floor(s / 86400); s = s - d * 86400;
  var h = Math.floor(s / 3600); s = s - h * 3600;
  var m = Math.floor(s / 60); s = s - m * 60;
  return new Array(d, h, m, s);
}
function cdTick() {
  var p = cdParts();
  if (document.forms["countdown"]) {
    document.forms["countdown"].clock.value = p[0] + " days " + two(p[1]) + ":" + two(p[2]) + ":" + two(p[3]);
  }
  setTimeout("cdTick()", 1000);
}
//--></SCRIPT>
"""


def countdown_box(P, width=150):
    return """<TABLE WIDTH=%d BORDER=0 CELLPADDING=0 CELLSPACING=0 BGCOLOR="#000000">
<TR><TD><A HREF="%sy2k/index.html"><IMG SRC="%simages/countdown_hdr.gif" WIDTH=150 HEIGHT=20 BORDER=0 ALT="Countdown to 2000"></A></TD></TR>
<TR><TD ALIGN=CENTER><FORM NAME="countdown"><INPUT TYPE=TEXT NAME="clock" SIZE=17 VALUE="loading..."></FORM>
<FONT %s SIZE=1 COLOR="#FFCC00">until the year 2000</FONT><BR>
<A HREF="%sy2k/index.html"><FONT %s SIZE=1 COLOR="#FFFFFF"><B>Y2K Special Report &gt;&gt;</B></FONT></A><BR><BR></TD></TR>
</TABLE>""" % (width, P, P, VERD, P, VERD)


# ------------------------------------------------------------------ story pages
def story_page(s):
    rel = story_url(s)
    P = prefix(rel)
    code, nav, dirn, ttl, blurb = SEC[s["section"]]
    paras = list(s["paras"])
    body = []
    first = "%s %s" % (esc(s["dateline"]), esc(paras[0]))
    photo = ""
    if s["photo"]:
        photo = """<TABLE ALIGN=RIGHT WIDTH=222 BORDER=0 CELLPADDING=0 CELLSPACING=6>
<TR><TD><IMG SRC="%simages/photo220_%s.gif" WIDTH=220 HEIGHT=134 BORDER=1 ALT="%s"></TD></TR>
<TR><TD><FONT %s SIZE=1>%s</FONT></TD></TR>
</TABLE>
""" % (P, s["slug"], esc(s["caption"]), ARIAL, esc(s["caption"]))
    body.append("<P>" + first)
    for i, p in enumerate(paras[1:]):
        if i == 0 and photo:
            body.append(photo)
        body.append("<P>" + esc(p))
    if photo and len(paras) == 1:
        body.append(photo)
    byline = '<FONT %s SIZE=2><I>%s</I></FONT><BR>\n' % (ARIAL, esc(s["byline"])) if s["byline"] else ""
    rel_rows = "".join('<TR><TD VALIGN=TOP><FONT %s SIZE=1>&#149;</FONT></TD><TD><FONT %s SIZE=1><A HREF="%s%s">%s</A><BR><I>%s</I></FONT></TD></TR>\n'
                       % (ARIAL, ARIAL, P, story_url(o), esc(o["headline"]), date_str(o)) for o in related(s))
    site_rows = "".join('<TR><TD VALIGN=TOP><FONT %s SIZE=1>&#149;</FONT></TD><TD><FONT %s SIZE=1><A HREF="%s" TARGET="_blank">%s</A></FONT></TD></TR>\n'
                        % (ARIAL, ARIAL, site_href(P, k, t), esc(l)) for l, k, t in data.RELATED_SITES[code])
    subj = quote("CNM.com - " + s["headline"])
    mbody = quote("I thought you might like this story from CNM.com:\n\n%s\n%s\n\nwww.cnm.com/%s" % (s["headline"], s["summary"], rel.replace("index.html", "")))
    mail = "mailto:?subject=%s&amp;body=%s" % (subj, mbody)
    content = """%s<TABLE WIDTH=630 BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR>
<TD WIDTH=460 VALIGN=TOP>
<FONT %s SIZE=2>%s<BR>Web posted at: %s</FONT><BR><BR>
<FONT %s SIZE=5><B>%s</B></FONT><BR><BR>
%s<FONT SIZE=3>
%s
</FONT>
<BR CLEAR=ALL><BR>
<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=0><TR>
<TD><A HREF="%s"><IMG SRC="%simages/email.gif" BORDER=0 ALT="E-mail"></A></TD>
<TD><FONT %s SIZE=1><B><A HREF="%s">E-MAIL THIS STORY</A></B> to a friend</FONT></TD>
<TD>&nbsp;&nbsp;</TD>
<TD><FONT %s SIZE=1><B><A HREF="%s%s">MORE %s NEWS</A></B> | <A HREF="%squickvote.html">QuickVote</A> | <A HREF="%ssearch.html">Search</A></FONT></TD>
</TR></TABLE>
</TD>
<TD WIDTH=10><IMG SRC="%simages/1.gif" WIDTH=10 HEIGHT=1 ALT=""></TD>
<TD WIDTH=160 VALIGN=TOP>
%s
<TABLE WIDTH=160 BORDER=0 CELLPADDING=2 CELLSPACING=0 BGCOLOR="#EEEEEE">
%s</TABLE><BR>
%s
<TABLE WIDTH=160 BORDER=0 CELLPADDING=2 CELLSPACING=0 BGCOLOR="#EEEEEE">
%s</TABLE>
<FONT %s SIZE=1><I>Note: Pages will open in a new browser window</I><BR>
External sites are not endorsed by CNM Interactive, and vice versa.</FONT><BR><BR>
%s
</TD>
</TR>
</TABLE>
""" % (title_gif(P, "sec_%s.gif" % dirn.lower(), ttl, P + sec_url(code)),
       ARIAL, date_str(s), time_str(s), ARIAL, esc(s["headline"]), byline, "\n".join(body),
       mail, P, ARIAL, mail, ARIAL, P, sec_url(code), esc(nav), P, P, P,
       box_title("RELATED STORIES:", 160), rel_rows, box_title("RELATED SITES:", 160), site_rows, ARIAL,
       countdown_box(P))
    page(rel, "CNM - %s - %s" % (esc(s["headline"]), date_str(s)), content, current=code,
         onload="cdTick()", script=COUNTDOWN_JS, label=nav)


# ------------------------------------------------------------------ section fronts
SCOREBOARD = [("Port Halloway Lobstermen", 23, "Gristmill Falls Grinders", 20, "OT"),
              ("Lake Wendell Loons", 4, "Cedar Notch Snowshoes", 2, ""),
              ("Twin Forks State", 31, "Mossbank A&amp;M", 17, ""),
              ("Saint Ulric Tech", 14, "Bellwether College", 10, ""),
              ("Dry Spoon Scorpions", 3, "Halcyon Springs Herons", 38, "")]


def markets_box(P, width=200):
    rows = "".join('<TR><TD><FONT %s SIZE=1><B>%s</B></FONT></TD><TD><IMG SRC="%simages/%s" WIDTH=10 HEIGHT=10 ALT="%s"></TD>'
                   '<TD ALIGN=RIGHT><FONT %s SIZE=1>%s</FONT></TD><TD ALIGN=RIGHT><FONT %s SIZE=1 COLOR="%s">%s</FONT></TD></TR>\n'
                   % (VERD, n, P, "arrow_up.gif" if up else "arrow_down.gif", "up" if up else "down", VERD, v, VERD,
                      "#009900" if up else "#CC0000", c) for n, v, c, up in data.MARKETS)
    return """<TABLE WIDTH=%d BGCOLOR="#EEEEEE" BORDER=0 CELLPADDING=2 CELLSPACING=0>
<TR><TD COLSPAN=4><FONT %s SIZE=1><B>MARKETS:</B> %s</FONT></TD></TR>
%s</TABLE>""" % (width, VERD, data.MARKETS_TIME, rows)


def section_front(code):
    code, nav, dirn, ttl, blurb = SEC[code]
    rel = sec_url(code)
    P = prefix(rel)
    ss = sec_stories(code)
    lead = next((s for s in ss if s["photo"]), ss[0])
    rest = [s for s in ss if s is not lead]
    more = "".join('<LI><FONT %s SIZE=2><A HREF="%s%s">%s</A></FONT>\n' % (ARIAL, P, story_url(s), esc(s["headline"])) for s in rest[:5])
    extra = ""
    if code == "WEATHER":
        cells = "".join('<TD ALIGN=CENTER><FONT %s SIZE=1><IMG SRC="%simages/wx_%s.gif" WIDTH=40 HEIGHT=40 ALT="%s"><BR><B>%s</B><BR>%d/%d</FONT></TD>'
                        % (ARIAL, P, w[2], w[2], esc(w[0]), w[3], w[4]) for w in data.WEATHER[:6])
        extra = """<TABLE WIDTH=340 BORDER=0 CELLPADDING=2 CELLSPACING=0 BGCOLOR="#EEEEEE"><TR><TD COLSPAN=6>%s</TD></TR><TR>%s</TR>
<TR><TD COLSPAN=6 ALIGN=RIGHT><FONT %s SIZE=1><B><A HREF="%sweather.html">Full forecasts and U.S. map &gt;&gt;</A></B></FONT></TD></TR></TABLE><BR>""" % (
            box_title("TODAY'S FORECASTS"), cells, ARIAL, P)
    elif code == "BUSINESS":
        extra = markets_box(P, 340) + "<BR>"
    elif code == "SPORTS":
        rows = "".join('<TR><TD><FONT %s SIZE=1>%s</FONT></TD><TD ALIGN=RIGHT><FONT %s SIZE=1><B>%d</B></FONT></TD><TD><FONT %s SIZE=1>%s</FONT></TD><TD ALIGN=RIGHT><FONT %s SIZE=1><B>%d</B> %s</FONT></TD></TR>\n'
                       % (VERD, a, VERD, sa, VERD, b, VERD, sb, ot) for a, sa, b, sb, ot in SCOREBOARD)
        extra = '%s<TABLE WIDTH=340 BORDER=0 CELLPADDING=2 CELLSPACING=0 BGCOLOR="#EEEEEE">%s</TABLE><BR>' % (box_title("SCOREBOARD"), rows)
    elif code == "POLITICS":
        extra = """%s<TABLE WIDTH=340 BORDER=0 CELLPADDING=2 CELLSPACING=0 BGCOLOR="#EEEEEE">
<TR><TD><FONT %s SIZE=1>Whitcomb</FONT></TD><TD><IMG SRC="%simages/bar_red.gif" WIDTH=136 HEIGHT=12 ALT=""> <FONT %s SIZE=1>34%%</FONT></TD></TR>
<TR><TD><FONT %s SIZE=1>Price-Morrow</FONT></TD><TD><IMG SRC="%simages/bar_navy.gif" WIDTH=100 HEIGHT=12 ALT=""> <FONT %s SIZE=1>25%%</FONT></TD></TR>
<TR><TD><FONT %s SIZE=1>Fenwick</FONT></TD><TD><IMG SRC="%simages/bar_gray.gif" WIDTH=24 HEIGHT=12 ALT=""> <FONT %s SIZE=1>6%%</FONT></TD></TR>
<TR><TD><FONT %s SIZE=1>Ambergast</FONT></TD><TD><IMG SRC="%simages/bar_orange.gif" WIDTH=16 HEIGHT=12 ALT=""> <FONT %s SIZE=1>4%%</FONT></TD></TR>
<TR><TD><FONT %s SIZE=1>Undecided</FONT></TD><TD><IMG SRC="%simages/bar_gray.gif" WIDTH=124 HEIGHT=12 ALT=""> <FONT %s SIZE=1>31%%</FONT></TD></TR>
<TR><TD COLSPAN=2><FONT %s SIZE=1>Source: <A HREF="%s%s">CNM/Bellwether Gazette poll</A></FONT></TD></TR>
</TABLE><BR>""" % ((box_title("CAMPAIGN 2000 POLL"),) + (VERD, P, VERD) * 5 + (VERD, P, story_url(BY_SLUG["poll.whitcomb"])))
    lead_photo = ""
    if lead["photo"]:
        lead_photo = '<A HREF="%s%s"><IMG SRC="%simages/photo_%s.gif" WIDTH=280 HEIGHT=170 BORDER=0 ALT="%s"></A>' % (
            P, story_url(lead), P, lead["slug"], esc(lead["caption"]))
    by_day = []
    for s in ss:
        if not by_day or by_day[-1][0] != s["day"]:
            by_day.append((s["day"], []))
        by_day[-1][1].append(s)
    week = ""
    for day, lst in by_day:
        week += '<TR><TD COLSPAN=2 BGCOLOR="#CCCCFF"><FONT %s SIZE=2><B>December %d, 1999</B></FONT></TD></TR>\n' % (ARIAL, day)
        for s in lst:
            thumb = ('<A HREF="%s%s"><IMG SRC="%simages/thumb_%s.gif" WIDTH=55 HEIGHT=45 BORDER=0 ALT=""></A>' % (P, story_url(s), P, s["slug"])) if s["photo"] else "&nbsp;"
            week += '<TR><TD VALIGN=TOP WIDTH=60>%s</TD><TD VALIGN=TOP><FONT %s SIZE=2><B><A HREF="%s%s">%s</A></B><BR>%s<BR><FONT SIZE=1 COLOR="#666666">%s</FONT></FONT></TD></TR>\n' % (
                thumb, ARIAL, P, story_url(s), esc(s["headline"]), esc(s["summary"]), time_str(s, False))
    content = """%s<FONT %s SIZE=2><I>%s</I></FONT><BR><BR>
<TABLE WIDTH=630 BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR>
<TD WIDTH=280 VALIGN=TOP>%s
<H3><FONT %s><A HREF="%s%s">%s</A></FONT></H3>
<FONT %s SIZE=2>%s</FONT>
<P><A HREF="%s%s"><IMG SRC="%simages/full_story.gif" WIDTH=78 HEIGHT=14 BORDER=0 ALT="FULL STORY"></A>
</TD>
<TD WIDTH=10>&nbsp;</TD>
<TD WIDTH=340 VALIGN=TOP>
%s
%s
<UL>
%s</UL>
</TD>
</TR>
</TABLE>
<BR>
%s
<TABLE WIDTH=630 BORDER=0 CELLPADDING=3 CELLSPACING=0>
%s</TABLE>
""" % (title_gif(P, "sec_%s.gif" % dirn.lower(), ttl), ARIAL, esc(blurb), lead_photo, ARIAL, P, story_url(lead),
       esc(lead["headline"]), ARIAL, esc(lead["summary"]), P, story_url(lead), P,
       extra, box_title("MORE %s NEWS:" % esc(nav)), more, box_title("%s STORIES THIS MONTH" % esc(nav), 630), week)
    page(rel, "CNM - %s - %s" % (esc(nav), data.TODAY), content, current=code, label=nav)


# ------------------------------------------------------------------ front page
def front_page():
    rel = "index.html"
    P = ""
    top_s = BY_SLUG[data.TOP_STORY]
    bullets = "".join('<LI><A HREF="%s">%s</A>\n' % (story_url(BY_SLUG[x]), esc(BY_SLUG[x]["headline"])) for x in data.TOP_BULLETS)
    bullets += '<LI><A HREF="y2k/index.html">Y2K Special Report: countdown, checklist and bug watch</A>\n'
    other = "".join('<LI><A HREF="%s">%s</A>%s\n' % (story_url(BY_SLUG[x]), esc(BY_SLUG[x]["headline"]),
                    '&nbsp;<IMG SRC="images/icon_video.gif" WIDTH=10 HEIGHT=10 ALT="This story contains video">' if x == data.VIDEO_STORY else "")
                    for x in data.IN_OTHER_NEWS)
    sports = "".join('<LI><A HREF="%s">%s</A>\n' % (story_url(BY_SLUG[x]), esc(BY_SLUG[x]["headline"])) for x in data.SPORTS_FRONT)
    f0 = BY_SLUG[data.FEATURES[0]]
    feats = "".join('<LI><A HREF="%s">%s</A>\n' % (story_url(BY_SLUG[x]), esc(BY_SLUG[x]["headline"])) for x in data.FEATURES[1:])
    tv = "".join('<TR><TD NOWRAP><FONT %s SIZE=1>&nbsp;&nbsp;&#149;&nbsp;%s: %s</FONT></TD></TR>\n' % (VERD, t, esc(x)) for t, x in data.TV)
    qv = data.QUICKVOTE
    radios = "".join('<INPUT TYPE=RADIO NAME="answer" VALUE="%d"> %s<BR>\n' % (i + 1, esc(a)) for i, a in enumerate(qv["answers"]))

    def heads(code, n=3):
        return "".join('<LI><A HREF="%s">%s</A>\n' % (story_url(s), esc(s["headline"])) for s in sec_stories(code)[:n])

    biz = heads("BUSINESS", 4)
    spo = heads("SPORTS", 4)
    more_cells = []
    for code, nav, dirn, ttl, blurb in SECTIONS:
        more_cells.append('<FONT %s SIZE=2><B><A HREF="%s">%s</A>:</B></FONT><FONT %s SIZE=1><UL>%s</UL></FONT>'
                          % (ARIAL, sec_url(code), nav, ARIAL, heads(code)))
    half = (len(more_cells) + 1) // 2
    more_html = '<TABLE WIDTH=630 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD WIDTH=310 VALIGN=TOP>%s</TD><TD WIDTH=10>&nbsp;</TD><TD WIDTH=310 VALIGN=TOP>%s</TD></TR></TABLE>' % (
        "\n".join(more_cells[:half]), "\n".join(more_cells[half:]))

    qv_js = """<SCRIPT LANGUAGE="JavaScript"><!--
function qvCheck(f) {
  var i;
  for (i = 0; i < f.answer.length; i++) {
    if (f.answer[i].checked) return true;
  }
  alert("Please choose an answer before you vote. Undecided is not one of the options -- yet.");
  return false;
}
function zipCheck(f) {
  var z = f.zip.value;
  if (z.length != 5 || isNaN(z)) {
    alert("Please enter a five-digit U.S. Zip code.");
    return false;
  }
  return true;
}
//--></SCRIPT>
"""
    html = head("CNM Interactive", P, onload="cdTick()", refresh=True, script=COUNTDOWN_JS + qv_js) + top(P, rel)
    html += """<TABLE WIDTH=770 BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR>
<TD WIDTH=125 VALIGN=TOP BGCOLOR="#CCCCFF">%s</TD>
<TD WIDTH=15><IMG SRC="images/1.gif" WIDTH=15 HEIGHT=1 ALT=""></TD>
<TD WIDTH=630 VALIGN=TOP>
<TABLE WIDTH=630 BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR><TD WIDTH=120 ALIGN=RIGHT BGCOLOR="#CC0000"><B><FONT %s SIZE=2 COLOR="#FFFFFF">BREAKING<BR>NEWS</FONT></B></TD>
<TD WIDTH=510 BGCOLOR="#CCCCCC"><FONT %s SIZE=2>%s</FONT></TD></TR>
</TABLE><BR>
<TABLE WIDTH=630 BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR>
<TD WIDTH=280 VALIGN=TOP>
<A HREF="%s"><IMG SRC="images/photo_%s.gif" WIDTH=280 HEIGHT=170 BORDER=0 ALT="%s"></A>
<H3><FONT %s><A HREF="%s">%s</A></FONT></H3>
<FONT %s SIZE=2>%s</FONT>
<P><A HREF="%s"><IMG SRC="images/full_story.gif" WIDTH=78 HEIGHT=14 BORDER=0 ALT="FULL STORY"></A>
<FONT %s SIZE=2><UL>
%s</UL></FONT>
</TD>
<TD WIDTH=10><IMG SRC="images/1.gif" WIDTH=10 HEIGHT=1 ALT=""></TD>
<TD WIDTH=340 VALIGN=TOP>
<TABLE BGCOLOR="#CCCCCC" WIDTH=340 BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR><TD COLSPAN=2>%s</TD></TR>
<TR><TD WIDTH=275 VALIGN=TOP><TABLE WIDTH=275 BORDER=0 CELLPADDING=2 CELLSPACING=0>
<TR><TD NOWRAP><FONT %s SIZE=1>&nbsp;<B>Watch CNM (all times EST)</B></FONT></TD></TR>
%s</TABLE></TD>
<TD VALIGN=TOP ALIGN=RIGHT><A HREF="video.html"><IMG SRC="images/oncnm.gif" WIDTH=55 HEIGHT=45 BORDER=0 ALT="CNM video" VSPACE=3 HSPACE=3></A><BR>
<FONT %s SIZE=1><A HREF="video.html">watch</A>&nbsp;</FONT></TD></TR>
</TABLE><BR>
<TABLE WIDTH=340 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR>
<TD WIDTH=150 VALIGN=TOP>%s</TD>
<TD WIDTH=10>&nbsp;</TD>
<TD WIDTH=180 VALIGN=TOP><A HREF="y2k/index.html"><IMG SRC="images/y2k_promo.gif" WIDTH=150 HEIGHT=40 BORDER=0 ALT="Y2K Special Report"></A><BR>
<FONT %s SIZE=1><A HREF="y2k/ready.html">Are you ready?</A> Take our checklist.<BR>
<A HREF="y2k/bugwatch.html">Bug Watch:</A> how the world stands.<BR>
<A HREF="y2k/celebrations.html">Millennium celebrations</A> around the globe.</FONT></TD>
</TR></TABLE><BR>
<FONT %s SIZE=2><B>In Other News:</B></FONT>
<FONT %s SIZE=2><UL>
%s</UL></FONT>
<FONT %s SIZE=2><B>Sports:</B></FONT>
<FONT %s SIZE=2><UL>
%s</UL></FONT>
<FONT %s SIZE=2><B>Features:</B><BR>
<A HREF="%s"><IMG SRC="images/thumb_%s.gif" WIDTH=55 HEIGHT=45 BORDER=0 ALIGN=LEFT HSPACE=4 ALT=""></A><A HREF="%s">%s</A><BR CLEAR=ALL>
<UL>
%s</UL></FONT>
</TD>
</TR>
</TABLE>
</TD>
</TR>
</TABLE>
""" % (nav_top(P), ARIAL, ARIAL, esc(data.BREAKING),
       story_url(top_s), top_s["slug"], esc(top_s["caption"]), ARIAL, story_url(top_s), esc(top_s["headline"]),
       ARIAL, esc(top_s["summary"]), story_url(top_s), ARIAL, bullets,
       box_title("ON CNM TV"), VERD, tv, VERD, countdown_box(P), VERD,
       ARIAL, ARIAL, other, ARIAL, ARIAL, sports, ARIAL, story_url(f0), f0["slug"], story_url(f0), esc(f0["headline"]), feats)

    # ---- the "news net" fold
    wx_opts = data.WEATHER[0]
    html += """<TABLE WIDTH=770 BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR><TD COLSPAN=7 BGCOLOR="#666666"><IMG SRC="images/1.gif" WIDTH=1 HEIGHT=2 ALT=""></TD></TR>
<TR><TD WIDTH=125 BGCOLOR="#666666"><IMG SRC="images/newsnet.gif" WIDTH=125 HEIGHT=20 ALT="CNM.com news net"></TD>
<TD WIDTH=15>&nbsp;</TD>
<TD WIDTH=230><FONT %s SIZE=2><B><A HREF="SPORTS/index.html">Top Sports News</A></B></FONT></TD>
<TD WIDTH=10>&nbsp;</TD>
<TD WIDTH=230><FONT %s SIZE=2><B><A HREF="BUSINESS/index.html">Top Business News</A></B></FONT></TD>
<TD WIDTH=10>&nbsp;</TD>
<TD WIDTH=150><FONT %s SIZE=2><B><A HREF="weather.html">Weather:</A></B></FONT></TD></TR>
<TR>
<TD WIDTH=125 BGCOLOR="#666666" VALIGN=TOP>&nbsp;%s</TD>
<TD WIDTH=15>&nbsp;</TD>
<TD VALIGN=TOP><FONT %s SIZE=1><UL>
%s</UL></FONT>
<TABLE WIDTH=220 BGCOLOR="#EEEEEE" BORDER=0 CELLPADDING=2 CELLSPACING=0>
<TR><TD><FONT %s SIZE=1><B>LAST NIGHT:</B> Lobstermen 23, Grinders 20 (OT)<BR>Loons 4, Snowshoes 2 &nbsp;<A HREF="SPORTS/index.html">scoreboard</A></FONT></TD></TR>
</TABLE></TD>
<TD>&nbsp;</TD>
<TD VALIGN=TOP><FONT %s SIZE=1><UL>
%s<LI><A HREF="BUSINESS/index.html">Market news and analysis</A>
</UL></FONT>
%s</TD>
<TD>&nbsp;</TD>
<TD VALIGN=TOP><FORM NAME="wxform" ACTION="weather.html" METHOD=GET onSubmit="return zipCheck(this);">
<IMG SRC="images/wxs_snow.gif" WIDTH=20 HEIGHT=20 ALIGN=LEFT ALT=""><FONT %s SIZE=1>%s: %s, %d/%d</FONT><BR CLEAR=ALL>
<FONT %s SIZE=1>Visit the CNM.com <A HREF="WEATHER/index.html">weather section</A> or enter your U.S. Zip code:</FONT><BR>
<INPUT TYPE=TEXT NAME="zip" SIZE=6 MAXLENGTH=5><INPUT TYPE=SUBMIT VALUE="Go">
</FORM></TD>
</TR>
<TR><TD COLSPAN=7 BGCOLOR="#666666"><IMG SRC="images/1.gif" WIDTH=1 HEIGHT=2 ALT=""></TD></TR>
</TABLE>
""" % (ARIAL, ARIAL, ARIAL, search_form(P, "seek_nn", True), ARIAL, spo, VERD, ARIAL, biz, markets_box(P, 220),
       VERD, esc(wx_opts[0]), esc(wx_opts[5]), wx_opts[3], wx_opts[4], VERD)

    # ---- lower part: rest of nav + more news + quickvote + video of the day
    html += """<TABLE WIDTH=770 BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR>
<TD WIDTH=125 VALIGN=TOP BGCOLOR="#CCCCFF">%s</TD>
<TD WIDTH=15>&nbsp;</TD>
<TD WIDTH=630 VALIGN=TOP><BR>
<TABLE WIDTH=630 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR>
<TD WIDTH=440 VALIGN=TOP>%s<BR>%s</TD>
<TD WIDTH=10>&nbsp;</TD>
<TD WIDTH=180 VALIGN=TOP>
<IMG SRC="images/quickvote.gif" WIDTH=150 HEIGHT=20 ALT="QuickVote"><BR>
<FORM NAME="qv" ACTION="quickvote.html" METHOD=GET onSubmit="return qvCheck(this);">
<FONT %s SIZE=1><B>%s</B><BR>
%s
<INPUT TYPE=SUBMIT VALUE="VOTE"><BR>
<A HREF="quickvote.html">View results</A> | <A HREF="quickvote_archive.html">Past votes</A></FONT>
</FORM>
<IMG SRC="images/vod.gif" WIDTH=150 HEIGHT=20 ALT="Video of the Day"><BR>
<A HREF="video.html"><IMG SRC="images/video_small.gif" WIDTH=150 HEIGHT=112 BORDER=0 ALT="Video of the day"></A><BR>
<FONT %s SIZE=1>Nor'easter buries the Maine coast.<BR><A HREF="video.html"><B>Play video</B></A> &nbsp;<IMG SRC="images/icon_video.gif" WIDTH=10 HEIGHT=10 ALT=""></FONT><BR><BR>
<A HREF="weather.html"><IMG SRC="images/us_map_small.gif" WIDTH=150 HEIGHT=94 BORDER=0 ALT="U.S. weather map"></A><BR>
<FONT %s SIZE=1><A HREF="weather.html">U.S. weather map</A></FONT>
</TD>
</TR></TABLE>
</TD>
</TR>
</TABLE>
""" % (nav_bottom(P), box_title("MORE NEWS:", 440), more_html.replace("WIDTH=630", "WIDTH=440").replace("WIDTH=310", "WIDTH=215"),
       VERD, esc(qv["question"]), radios, VERD, VERD)
    html += footer(P)
    write(rel, html)


# ------------------------------------------------------------------ QuickVote
def quickvote_pages():
    qv = data.QUICKVOTE
    rel = "quickvote.html"
    P = ""
    total = sum(qv["votes"])
    static_rows = "".join('<TR><TD><FONT %s SIZE=2>%s</FONT></TD><TD><IMG SRC="images/bar_navy.gif" WIDTH=%d HEIGHT=12 ALT=""></TD><TD ALIGN=RIGHT><FONT %s SIZE=2>%d%%</FONT></TD><TD ALIGN=RIGHT><FONT %s SIZE=2>%d</FONT></TD></TR>\n'
                          % (ARIAL, esc(a), max(1, int(v * 200 / total)), ARIAL, round(v * 100.0 / total), ARIAL, v)
                          for a, v in zip(qv["answers"], qv["votes"]))
    js = """<SCRIPT LANGUAGE="JavaScript"><!--
var answers = new Array(%s);
var votes = new Array(%s);
function getParam(name) {
  var q = location.search.substring(1);
  var parts = q.split("&");
  var i;
  for (i = 0; i < parts.length; i++) {
    var kv = parts[i].split("=");
    if (kv[0] == name && kv.length > 1) return unescape(kv[1].replace(/\\+/g, " "));
  }
  return "";
}
function getCookie(name) {
  var c = document.cookie.split("; ");
  var i;
  for (i = 0; i < c.length; i++) {
    var kv = c[i].split("=");
    if (kv[0] == name) return unescape(kv[1]);
  }
  return "";
}
function showResults() {
  var mine = parseInt(getParam("answer"), 10);
  var before = getCookie("cnmqv");
  var total = 0, i;
  if (mine >= 1 && mine <= answers.length) {
    votes[mine - 1] = votes[mine - 1] + 1;
    document.cookie = "cnmqv=" + mine + "; path=/";
  } else {
    mine = 0;
  }
  for (i = 0; i < votes.length; i++) total = total + votes[i];
  if (mine > 0 && before != "") {
    document.write('<P><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#CC0000"><B>Our records show you have voted before.</B> We counted this one too. As we said, this is not science.</FONT>');
  } else if (mine > 0) {
    document.write('<P><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#CC0000"><B>Thank you for voting!</B></FONT>');
  }
  document.write('<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH=600>');
  for (i = 0; i < answers.length; i++) {
    var pct = Math.round(votes[i] * 100 / total);
    var w = Math.round(votes[i] * 200 / total);
    if (w < 1) w = 1;
    var bg = (i + 1 == mine) ? ' BGCOLOR="#FFFFCC"' : '';
    var bar = (i + 1 == mine) ? "images/bar_red.gif" : "images/bar_navy.gif";
    document.write('<TR' + bg + '><TD><FONT FACE="Arial, Helvetica" SIZE=2>' + answers[i] + '</FONT></TD>');
    document.write('<TD><IMG SRC="' + bar + '" WIDTH=' + w + ' HEIGHT=12 ALT=""></TD>');
    document.write('<TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2>' + pct + '%%</FONT></TD>');
    document.write('<TD ALIGN=RIGHT><FONT FACE="Arial, Helvetica" SIZE=2>' + votes[i] + '</FONT></TD>');
    document.write('<TD><FONT FACE="Arial, Helvetica" SIZE=1 COLOR="#CC0000"><B>' + ((i + 1 == mine) ? '&lt;-- your vote' : '&nbsp;') + '</B></FONT></TD></TR>');
  }
  document.write('<TR><TD COLSPAN=5><FONT FACE="Arial, Helvetica" SIZE=2><B>Total votes: ' + total + '</B></FONT></TD></TR></TABLE>');
}
//--></SCRIPT>
""" % (",".join(jsstr(esc(a)) for a in qv["answers"]), ",".join(str(v) for v in qv["votes"]))
    content = """%s<FONT %s SIZE=2>%s -- Results as of %s</FONT>
<H3><FONT %s>%s</FONT></H3>
<SCRIPT LANGUAGE="JavaScript"><!--
showResults();
//--></SCRIPT>
<NOSCRIPT><TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH=600>
%s<TR><TD COLSPAN=4><FONT %s SIZE=2><B>Total votes: %d</B></FONT></TD></TR></TABLE></NOSCRIPT>
<P><FONT %s SIZE=1><I>This QuickVote is not scientific. It reflects only the opinions of the Internet users who happened
to wander by and click a button, and it should not be taken to represent the views of Internet users in general,
the public at large, or anyone's cat.</I></FONT>
<P><FONT %s SIZE=2><B><A HREF="quickvote_archive.html">See past QuickVotes</A></B> | <A HREF="index.html">Vote on the CNM.com main page</A></FONT>
<P><FONT %s SIZE=2><B>Related stories:</B><UL>
<LI><A HREF="%s">%s</A>
<LI><A HREF="%s">%s</A>
<LI><A HREF="y2k/index.html">Y2K Special Report</A>
</UL></FONT>
""" % (title_gif(P, "sec_quickvote.gif", "QuickVote"), ARIAL, data.TODAY, data.UPDATED.replace("Updated ", ""), ARIAL,
       esc(qv["question"]), static_rows, ARIAL, total, ARIAL, ARIAL, ARIAL,
       story_url(BY_SLUG["celebrate.twice"]), esc(BY_SLUG["celebrate.twice"]["headline"]),
       story_url(BY_SLUG["bunker.tour"]), esc(BY_SLUG["bunker.tour"]["headline"]))
    page(rel, "CNM - QuickVote - %s" % data.TODAY, content, script=js, label="QUICKVOTE")

    # archive
    blocks = ""
    for date, q, ans in data.QUICKVOTE_ARCHIVE:
        tot = sum(v for a, v in ans)
        rows = "".join('<TR><TD WIDTH=230><FONT %s SIZE=2>%s</FONT></TD><TD WIDTH=210><IMG SRC="images/bar_navy.gif" WIDTH=%d HEIGHT=12 ALT=""></TD><TD ALIGN=RIGHT><FONT %s SIZE=2>%d%%</FONT></TD><TD ALIGN=RIGHT><FONT %s SIZE=2>%d</FONT></TD></TR>\n'
                       % (ARIAL, esc(a), max(1, int(v * 200 / tot)), ARIAL, round(v * 100.0 / tot), ARIAL, v) for a, v in ans)
        blocks += """<TABLE WIDTH=600 BORDER=0 CELLPADDING=2 CELLSPACING=0>
<TR><TD COLSPAN=4 BGCOLOR="#CCCCFF"><FONT %s SIZE=2><B>%s</B> -- %s</FONT></TD></TR>
%s<TR><TD COLSPAN=4 ALIGN=RIGHT><FONT %s SIZE=1>Total votes: %d</FONT></TD></TR>
</TABLE><BR>
""" % (ARIAL, date, esc(q), rows, ARIAL, tot)
    content = """%s<FONT %s SIZE=2>Past QuickVote results, from the most recent. Today's question is on the
<A HREF="index.html">main page</A>; today's results are <A HREF="quickvote.html">here</A>.</FONT><BR><BR>
%s
<FONT %s SIZE=1><I>QuickVotes are not scientific. Nobody's are. Ours are especially not.</I></FONT>
""" % (title_gif(P, "sec_quickvote.gif", "QuickVote"), ARIAL, blocks, ARIAL)
    page("quickvote_archive.html", "CNM - QuickVote archive", content, label="QUICKVOTE")


# ------------------------------------------------------------------ search
def search_page():
    rel = "search.html"
    items = []
    for s in STORIES:
        items.append("new Array(%s,%s,%s,%s,%s,%s)" % (
            jsstr(s["headline"]), jsstr(s["summary"]), jsstr(SEC[s["section"]][1]), jsstr(story_url(s)),
            jsstr(date_str(s)), jsstr(" ".join(s["tags"]) + " " + s["dateline"] + " " + s["byline"])))
    js = """<SCRIPT LANGUAGE="JavaScript"><!--
var stories = new Array(
%s
);
function getParam(name) {
  var q = location.search.substring(1);
  var parts = q.split("&");
  var i;
  for (i = 0; i < parts.length; i++) {
    var kv = parts[i].split("=");
    if (kv[0] == name && kv.length > 1) return unescape(kv[1].replace(/\\+/g, " "));
  }
  return "";
}
function clean(t) {
  return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function doSearch() {
  var q = getParam("query");
  var where = getParam("sites");
  var f = '<FONT FACE="Arial, Helvetica" SIZE=2>';
  var i, j;
  if (q == "") {
    document.write(f + 'Type a word or two in the box above and press <B>Find</B>. Try ');
    document.write('<A HREF="search.html?query=y2k">Y2K</A>, <A HREF="search.html?query=potato">potato</A>, ');
    document.write('<A HREF="search.html?query=fruitcake">fruitcake</A> or <A HREF="search.html?query=Marisol">Marisol</A>.</FONT>');
    return;
  }
  if (where == "WEB") {
    document.write(f + '<B>Searching The Web?</B> CNM.com searches only CNM.com. For the rest of the Internet, try our friends at ');
    document.write('<A HREF="../altavisor/index.html">AltaVisor</A>, <A HREF="../yowza/index.html">Yowza!</A> or ');
    document.write('<A HREF="../askreeves/index.html">Ask Reeves</A>. Meanwhile, here is what we found on CNM.com:</FONT><BR><BR>');
  }
  var words = q.toLowerCase().split(" ");
  var hits = new Array();
  for (i = 0; i < stories.length; i++) {
    var hay = (stories[i][0] + " " + stories[i][1] + " " + stories[i][2] + " " + stories[i][5]).toLowerCase();
    var score = 0, all = true;
    for (j = 0; j < words.length; j++) {
      if (words[j] == "") continue;
      if (hay.indexOf(words[j]) >= 0) {
        score++;
        if (stories[i][0].toLowerCase().indexOf(words[j]) >= 0) score = score + 2;
      } else {
        all = false;
      }
    }
    if (all && score > 0) hits[hits.length] = new Array(score, i);
  }
  hits.sort(function (a, b) { return (b[0] - a[0]) || (a[1] - b[1]); });
  document.write(f + 'Search results for <B>' + clean(q) + '</B>: <B>' + hits.length + '</B> document' + (hits.length == 1 ? '' : 's') + ' found.</FONT><HR SIZE=1 NOSHADE>');
  if (hits.length == 0) {
    document.write(f + 'No CNM.com stories matched your search. Check your spelling, use fewer words, or try a broader term such as <A HREF="search.html?query=millennium">millennium</A>.</FONT>');
    return;
  }
  document.write('<DL>');
  for (i = 0; i < hits.length; i++) {
    var s = stories[hits[i][1]];
    document.write('<DT>' + f + '<B>' + (i + 1) + '.</B> <A HREF="' + s[3] + '"><B>' + clean(s[0]) + '</B></A></FONT>');
    document.write('<DD>' + f + clean(s[1]) + '<BR><FONT SIZE=1><FONT COLOR="#008000">www.cnm.com/' + s[3].replace("index.html", "") + '</FONT> - ' + s[2] + ' - <I>' + s[4] + '</I></FONT></FONT><BR><BR>');
  }
  document.write('</DL>');
}
function fillBox() {
  if (document.forms["seek_page"]) document.forms["seek_page"].query.value = getParam("query");
}
//--></SCRIPT>
""" % ",\n".join(items)
    content = """%s<FORM NAME="seek_page" ACTION="search.html" METHOD=GET>
<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 BGCOLOR="#CCCCFF" WIDTH=600><TR><TD>
<FONT %s SIZE=2><B>Search:</B></FONT>
<SELECT NAME="sites"><OPTION VALUE="CNM" SELECTED>CNM.com<OPTION VALUE="WEB">The Web</SELECT>
<INPUT TYPE=TEXT NAME="query" SIZE=30> <INPUT TYPE=SUBMIT VALUE="Find">
<FONT %s SIZE=1>&nbsp; Searching %d stories from December 1999</FONT>
</TD></TR></TABLE>
</FORM>
<SCRIPT LANGUAGE="JavaScript"><!--
doSearch();
//--></SCRIPT>
<NOSCRIPT><FONT %s SIZE=2>CNM.com search requires a JavaScript-capable browser, such as Netscope Navigator 3.0 or later.
In the meantime, try the <A HREF="brief.html">Headline News brief</A>, which lists every story.</FONT></NOSCRIPT>
<BR><BR><FONT %s SIZE=1><I>Search tips: use simple words. Searching is not case sensitive. All of your words must appear
in a story for it to be found. Boolean operators are coming in a future version, possibly in the next millennium.</I></FONT>
""" % (title_gif("", "sec_search.gif", "Search"), ARIAL, VERD, len(STORIES), ARIAL, ARIAL)
    page(rel, "CNM - Search", content, script=js, onload="fillBox()", label="SEARCH")


# ------------------------------------------------------------------ Y2K special
def y2k_pages():
    P = "../"
    y2k = [s for s in STORIES if "y2k" in s["tags"]]
    mil = [s for s in STORIES if "millennium" in s["tags"] and "y2k" not in s["tags"]]

    def ul(lst):
        return "".join('<LI><A HREF="%s%s">%s</A> <FONT SIZE=1 COLOR="#666666">(%s)</FONT>\n' % (P, story_url(s), esc(s["headline"]), "Dec. %d" % s["day"]) for s in lst)

    sub = """<TABLE WIDTH=630 BORDER=0 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#000000"><TR>
<TD ALIGN=CENTER><A HREF="index.html"><FONT %s SIZE=1 COLOR="#FFFFFF"><B>Y2K HOME</B></FONT></A></TD>
<TD ALIGN=CENTER><A HREF="ready.html"><FONT %s SIZE=1 COLOR="#FFCC00"><B>ARE YOU READY?</B></FONT></A></TD>
<TD ALIGN=CENTER><A HREF="bugwatch.html"><FONT %s SIZE=1 COLOR="#FFCC00"><B>BUG WATCH</B></FONT></A></TD>
<TD ALIGN=CENTER><A HREF="celebrations.html"><FONT %s SIZE=1 COLOR="#FFCC00"><B>MILLENNIUM CELEBRATIONS</B></FONT></A></TD>
</TR></TABLE><BR>
""" % (VERD, VERD, VERD, VERD)
    banner_img = '<IMG SRC="../images/y2k_banner.gif" WIDTH=630 HEIGHT=80 ALT="Y2K: The Millennium Bug"><BR>\n'

    led_js = """<SCRIPT LANGUAGE="JavaScript"><!--
var ledPics = new Array();
var n;
function ledPath(d) { return "../images/led_" + d + ".gif"; }
for (n = 0; n < 10; n++) {
  ledPics[n] = new Image();
  ledPics[n].src = "" + ledPath(n);
}
function setDigits(prefix, value, count) {
  var s = "" + value;
  while (s.length < count) s = "0" + s;
  var k;
  for (k = 0; k < count; k++) {
    var pic = ledPics[parseInt(s.charAt(k), 10)];
    if (document.images[prefix + k].src != pic.src) document.images[prefix + k].src = "" + pic.src;
  }
}
function bigTick() {
  var p = cdParts();
  setDigits("dd", p[0], 3);
  setDigits("hh", p[1], 2);
  setDigits("mm", p[2], 2);
  setDigits("ss", p[3], 2);
  setTimeout("bigTick()", 1000);
}
//--></SCRIPT>
"""

    def leds(prefix_, count):
        return "".join('<IMG NAME="%s%d" SRC="../images/led_0.gif" WIDTH=22 HEIGHT=34 ALT="0">' % (prefix_, i) for i in range(count))
    colon = '<IMG SRC="../images/led_colon.gif" WIDTH=22 HEIGHT=34 ALT=":">'
    big = """<TABLE BORDER=0 CELLPADDING=8 CELLSPACING=0 BGCOLOR="#100000" WIDTH=630><TR><TD ALIGN=CENTER>
<FONT %s SIZE=2 COLOR="#FFCC00"><B>COUNTDOWN TO THE YEAR 2000</B></FONT><BR><BR>
<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0>
<TR><TD>%s</TD><TD>%s</TD><TD>%s</TD><TD>%s</TD><TD>%s</TD><TD>%s</TD><TD>%s</TD></TR>
<TR><TD ALIGN=CENTER><FONT %s SIZE=1 COLOR="#FFFFFF">DAYS</FONT></TD><TD></TD><TD ALIGN=CENTER><FONT %s SIZE=1 COLOR="#FFFFFF">HOURS</FONT></TD><TD></TD>
<TD ALIGN=CENTER><FONT %s SIZE=1 COLOR="#FFFFFF">MINUTES</FONT></TD><TD></TD><TD ALIGN=CENTER><FONT %s SIZE=1 COLOR="#FFFFFF">SECONDS</FONT></TD></TR>
</TABLE>
<FONT %s SIZE=1 COLOR="#CCCCCC">Based on your computer's clock -- which, let's be honest, is part of the problem.</FONT>
</TD></TR></TABLE><BR>
""" % (VERD, leds("dd", 3), colon, leds("hh", 2), colon, leds("mm", 2), colon, leds("ss", 2), VERD, VERD, VERD, VERD, VERD)

    content = banner_img + sub + big + """<TABLE WIDTH=630 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR>
<TD WIDTH=380 VALIGN=TOP><FONT %s SIZE=2>
<B>What is the Y2K bug?</B><BR>
For decades, programmers saved precious memory by storing years as two digits: 99 for 1999. When the calendar
turns, many computers will read 00 as 1900. The results could range from nothing at all to a coffee maker
that believes it is the McKinley administration.<BR><BR>
<B>Will anything happen?</B><BR>
Governments and companies have spent billions testing and fixing their systems. Most experts expect scattered,
minor glitches. A few expect more. Nobody expects the toaster to care.<BR><BR>
<B>What should I do?</B><BR>
Officials recommend the same preparations you would make for a winter storm: a few days of food and water,
flashlights, batteries and some cash. Then, they suggest, try to enjoy the party.
<A HREF="ready.html">Take our readiness checklist</A>.</FONT>
<P><FONT %s SIZE=2><B>Y2K stories:</B><UL>
%s</UL>
<B>Millennium stories:</B><UL>
%s</UL></FONT>
</TD>
<TD WIDTH=10>&nbsp;</TD>
<TD WIDTH=240 VALIGN=TOP>
%s
<TABLE WIDTH=240 BORDER=0 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#EEEEEE"><TR><TD><FONT %s SIZE=1>
<B>Y2K BY THE NUMBERS</B><BR><BR>
<B>99.6%%</B> of systems passed Monday's final drill<BR><BR>
<B>$14,000</B> spent on one Minnesota town's Y2K report<BR><BR>
<B>4,000</B> cans of beans in one Kansas guest room<BR><BR>
<B>900</B> D-cell batteries owned by one anxious Connecticut man<BR><BR>
<B>1</B> government computer in the Kingdom of Tavai (now unplugged)<BR><BR>
<B>0</B> horses affected
</FONT></TD></TR></TABLE><BR>
%s
<TABLE WIDTH=240 BORDER=0 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#EEEEEE"><TR><TD><FONT %s SIZE=1>
&#149; <A HREF="ready.html">Are you ready? Take the checklist</A><BR>
&#149; <A HREF="bugwatch.html">Bug Watch: country-by-country status</A><BR>
&#149; <A HREF="celebrations.html">Where midnight strikes first</A><BR>
&#149; <A HREF="../quickvote.html">QuickVote: How will you spend Dec. 31?</A><BR>
&#149; <A HREF="../search.html?query=y2k">Search CNM for Y2K</A>
</FONT></TD></TR></TABLE>
</TD></TR></TABLE>
""" % (ARIAL, ARIAL, ul(y2k), ul(mil), box_title("THE BUG IN BRIEF", 240), VERD, box_title("INSIDE THIS REPORT", 240), VERD)
    page("y2k/index.html", "CNM - Y2K Special Report: The Millennium Bug", title_gif(P, "sec_y2k.gif", "Y2K Special Report") + content,
         onload="bigTick()", script=COUNTDOWN_JS + led_js, label="Y2K")

    small_clock = '<TABLE ALIGN=RIGHT BORDER=0 CELLPADDING=0 CELLSPACING=6><TR><TD>%s</TD></TR></TABLE>\n' % countdown_box(P)

    # --- are you ready?
    items = [("Water: one gallon per person per day, for three days", 1),
             ("Canned food you would actually eat (see: Pantry Paella)", 1),
             ("A manual can opener", 1),
             ("Flashlights and fresh batteries", 1),
             ("Some cash -- a few days' worth, not your life savings", 1),
             ("Printed copies of important bank and insurance statements", 1),
             ("A full tank of gas", 1),
             ("Prescription medicines refilled", 1),
             ("Your VCR's clock set correctly (bonus: it has never been)", 0),
             ("A generator you know how to use safely, outdoors", 1),
             ("A bunker", 0),
             ("4,000 cans of beans", 0),
             ("A party to go to, or a good book and a warm blanket", 1)]
    boxes = "".join('<TR><TD VALIGN=TOP><INPUT TYPE=CHECKBOX NAME="c%d" VALUE="%d"></TD><TD><FONT %s SIZE=2>%s</FONT></TD></TR>\n' % (i, w, ARIAL, esc(t)) for i, (t, w) in enumerate(items))
    js = """<SCRIPT LANGUAGE="JavaScript"><!--
function rateMe(f) {
  var useful = 0, silly = 0, i, total = %d;
  for (i = 0; i < f.elements.length; i++) {
    var e = f.elements[i];
    if (e.type == "checkbox" && e.checked) {
      if (e.value == "1") useful++; else silly++;
    }
  }
  var msg;
  if (useful >= total - 1) msg = "Ready as anyone can be. Go enjoy the party.";
  else if (useful >= 6) msg = "Mostly ready. A trip to the hardware store should do it.";
  else if (useful >= 3) msg = "Getting there. Add water, batteries and a can opener.";
  else msg = "Not ready. But then again, neither is the coffee maker.";
  if (silly >= 2) msg = msg + " (Also: you may be over-preparing. Please put down the beans.)";
  f.score.value = useful + " of " + total + " essentials";
  f.verdict.value = msg;
  return false;
}
//--></SCRIPT>
""" % sum(w for t, w in items)
    content = title_gif(P, "sec_y2k.gif", "Y2K Special Report") + sub + small_clock + """<FONT %s SIZE=4><B>Are you ready for 2000?</B></FONT><BR>
<FONT %s SIZE=2>Check off everything you have done, then press the button. Our patented Readiness-O-Meter&#153; will
tell you how you stand. (It runs on JavaScript, which we are told is Y2K compliant.)</FONT><BR><BR>
<FORM NAME="ready" onSubmit="return rateMe(this);">
<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=0 WIDTH=440>
%s</TABLE><BR>
<INPUT TYPE=BUTTON VALUE="Rate my readiness" onClick="rateMe(this.form);"> <INPUT TYPE=RESET VALUE="Start over"><BR><BR>
<FONT %s SIZE=2><B>Score:</B></FONT> <INPUT TYPE=TEXT NAME="score" SIZE=22><BR>
<FONT %s SIZE=2><B>Verdict:</B></FONT><BR><TEXTAREA NAME="verdict" ROWS=3 COLS=50 WRAP=VIRTUAL></TEXTAREA>
</FORM>
<FONT %s SIZE=1><I>This checklist is for entertainment. For real advice, ask your local emergency-management office,
which has been waiting all year for someone to call.</I></FONT>
""" % (ARIAL, ARIAL, boxes, ARIAL, ARIAL, ARIAL)
    page("y2k/ready.html", "CNM - Y2K: Are you ready?", content, onload="cdTick()", script=COUNTDOWN_JS + js, label="Y2K")

    # --- bug watch
    countries = [("Marisol Islands", "green", "Ready. Has also moved the date line, just in case.", "marisol.dateline"),
                 ("Kingdom of Tavai", "green", "Only government computer unplugged; payroll by pencil.", "tavai.bug"),
                 ("Republic of Ostravia", "yellow", "Election ballots arriving by sleigh. Sleighs compliant.", "ostravia.vote"),
                 ("Esterhaal", "yellow", "Millennium Bubble sagging slightly; computers fine.", "eurobubble.opens"),
                 ("Lower Bruskia", "green", "Cake complete. Ovens compliant.", "bruskia.cake"),
                 ("Upper Bruskia", "yellow", "Declined to share data with Lower Bruskia.", None),
                 ("Federated States of Vellmark", "yellow", "Canal locks are hand-cranked; ships nervous anyway.", "vellmark.canal"),
                 ("Republic of Tamberlay", "green", "Taking over Port Sabrino; stamps redesigned.", "sabrino.handover"),
                 ("Republic of Sandovar", "yellow", "Lottery drum from 1899 certified reliable.", "sandovar.lottery"),
                 ("United States", "green", "99.6% of systems passed final drill. Coffee makers under review.", "y2k.drill"),
                 ("Lake Wendell, Minn.", "green", "Town clock cleared. Has never displayed the year.", "town.clock"),
                 ("Mossbank, Ore.", "red", "Parking meters still believe it is 1980.", "parking.meter")]
    rows = ""
    for name, col, note, slug in countries:
        link = '<A HREF="%s%s">story</A>' % (P, story_url(BY_SLUG[slug])) if slug else "&nbsp;"
        rows += '<TR><TD><IMG SRC="../images/dot_%s.gif" WIDTH=12 HEIGHT=12 ALT="%s"></TD><TD><FONT %s SIZE=2><B>%s</B></FONT></TD><TD><FONT %s SIZE=2>%s</FONT></TD><TD><FONT %s SIZE=1>%s</FONT></TD></TR>\n' % (
            col, col, ARIAL, esc(name), ARIAL, esc(note), ARIAL, link)
    content = title_gif(P, "sec_y2k.gif", "Y2K Special Report") + sub + """<FONT %s SIZE=4><B>Bug Watch: How ready is the world?</B></FONT><BR>
<FONT %s SIZE=2>CNM correspondents around the globe rate Year 2000 readiness, based on official statements,
independent monitors and what we could see from the hotel window. Updated %s.</FONT><BR><BR>
<TABLE WIDTH=630 BORDER=1 CELLPADDING=4 CELLSPACING=0>
<TR BGCOLOR="#666699"><TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>STATUS</B></FONT></TD><TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>COUNTRY / PLACE</B></FONT></TD>
<TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>REPORT</B></FONT></TD><TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>MORE</B></FONT></TD></TR>
%s</TABLE><BR>
<TABLE BORDER=0 CELLPADDING=3><TR>
<TD><IMG SRC="../images/dot_green.gif" WIDTH=12 HEIGHT=12 ALT="green"></TD><TD><FONT %s SIZE=1>Ready</FONT></TD>
<TD><IMG SRC="../images/dot_yellow.gif" WIDTH=12 HEIGHT=12 ALT="yellow"></TD><TD><FONT %s SIZE=1>Mostly ready / some concerns</FONT></TD>
<TD><IMG SRC="../images/dot_red.gif" WIDTH=12 HEIGHT=12 ALT="red"></TD><TD><FONT %s SIZE=1>Living in another decade</FONT></TD>
</TR></TABLE>
""" % (ARIAL, ARIAL, data.TODAY, VERD, VERD, VERD, VERD, rows, VERD, VERD, VERD)
    page("y2k/bugwatch.html", "CNM - Y2K: Bug Watch", content, label="Y2K")

    # --- celebrations
    events = [("12:00 a.m. Jan. 1 (local)", "1000 GMT Dec. 31", "Saint Ambrose, Marisol Islands", "Sunrise ceremony on the main jetty; viewing spots sold by the square foot.", "first.light.tours"),
              ("12:00 a.m.", "1100 GMT Dec. 31", "Nuku'ala, Tavai", "The Royal Brass Band plays at the museum, beside the unplugged computer.", "tavai.bug"),
              ("12:00 a.m.", "2200 GMT Dec. 31", "Velkograd, Ostravia", "Fireworks over the unfinished ring road; new parliament sworn in.", "ostravia.vote"),
              ("12:00 a.m.", "2300 GMT Dec. 31", "Bruskholm, Lower Bruskia", "Remaining cake served from the palace balcony.", "bruskia.cake"),
              ("12:00 a.m.", "0000 GMT Jan. 1", "Lornswick, Esterhaal", "Grand opening night at the Millennium Bubble, blowers permitting.", "eurobubble.opens"),
              ("12:00 a.m.", "0300 GMT Jan. 1", "Puerto Caldera, Vellmark", "Canal handover; the largest ribbon in the Southern Hemisphere is cut.", "vellmark.canal"),
              ("12:00 a.m.", "0500 GMT Jan. 1", "New Bramford, Conn.", "Time capsule party on the green (opening in 2100).", "time.capsule"),
              ("12:00 a.m.", "0600 GMT Jan. 1", "Lake Wendell, Minn.", "First curling stone of the millennium, followed by hot dish.", "curling.millennium"),
              ("12:00 a.m.", "0800 GMT Jan. 1", "Mossbank, Ore.", "Chamber of Commerce street dance. (Historical Society: see you next year.)", "celebrate.twice"),
              ("All night", "--", "Aboard the Silver Meridian", "Celebrates midnight twice by crossing the date line.", "cruise.millennium")]
    rows = "".join('<TR VALIGN=TOP><TD NOWRAP><FONT %s SIZE=1>%s</FONT></TD><TD><FONT %s SIZE=2><B>%s</B><BR>%s <A HREF="%s%s">More</A></FONT></TD></TR>\n'
                   % (VERD, gmt, ARIAL, esc(place), esc(what), P, story_url(BY_SLUG[slug])) for local, gmt, place, what, slug in events)
    content = title_gif(P, "sec_y2k.gif", "Y2K Special Report") + sub + small_clock + """<FONT %s SIZE=4><B>Millennium celebrations around the world</B></FONT><BR>
<FONT %s SIZE=2>Midnight will sweep westward from the international date line -- wherever the Marisol Islands have
put it this week. Here is where, and when, the party starts. Times are given in GMT; Eastern Time is GMT minus five hours.</FONT><BR CLEAR=ALL><BR>
<IMG SRC="../images/world_map.gif" WIDTH=600 HEIGHT=260 ALT="World map of millennium celebrations"><BR><BR>
<TABLE WIDTH=630 BORDER=0 CELLPADDING=4 CELLSPACING=0>
<TR BGCOLOR="#666699"><TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>MIDNIGHT (GMT)</B></FONT></TD><TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>WHERE AND WHAT</B></FONT></TD></TR>
%s</TABLE>
""" % (ARIAL, ARIAL, VERD, VERD, rows)
    page("y2k/celebrations.html", "CNM - Millennium celebrations", content, onload="cdTick()", script=COUNTDOWN_JS, label="Y2K")


# ------------------------------------------------------------------ weather
def weather_page():
    P = ""
    zipmap = {"0": 0, "1": 1, "2": 3, "3": 3, "4": 2, "5": 5, "6": 7, "7": 4, "8": 8, "9": 11}
    cities = ",".join(jsstr("%s, %s" % (w[0], w[1])) for w in data.WEATHER)
    icons = ",".join(jsstr(w[2]) for w in data.WEATHER)
    his = ",".join(str(w[3]) for w in data.WEATHER)
    los = ",".join(str(w[4]) for w in data.WEATHER)
    fcs = ",".join(jsstr(w[5]) for w in data.WEATHER)
    zm = ",".join(str(zipmap[str(i)]) for i in range(10))
    js = """<SCRIPT LANGUAGE="JavaScript"><!--
var wxCity = new Array(%s);
var wxIcon = new Array(%s);
var wxHi = new Array(%s);
var wxLo = new Array(%s);
var wxFc = new Array(%s);
var zipToCity = new Array(%s);
function getParam(name) {
  var q = location.search.substring(1);
  var parts = q.split("&");
  var i;
  for (i = 0; i < parts.length; i++) {
    var kv = parts[i].split("=");
    if (kv[0] == name && kv.length > 1) return unescape(kv[1].replace(/\\+/g, " "));
  }
  return "";
}
function zipCheck(f) {
  var z = f.zip.value;
  if (z.length != 5 || isNaN(z)) {
    alert("Please enter a five-digit U.S. Zip code.");
    return false;
  }
  return true;
}
function localForecast() {
  var z = getParam("zip");
  if (z == "") return;
  if (z.length != 5 || isNaN(z)) {
    document.write('<P><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#CC0000">Sorry, we could not find a forecast for that Zip code.</FONT>');
    return;
  }
  var c = zipToCity[parseInt(z.charAt(0), 10)];
  document.write('<TABLE WIDTH=630 BORDER=0 CELLPADDING=6 CELLSPACING=0 BGCOLOR="#FFFFCC"><TR>');
  document.write('<TD><IMG SRC="images/wx_' + wxIcon[c] + '.gif" WIDTH=40 HEIGHT=40 ALT="' + wxIcon[c] + '"></TD>');
  document.write('<TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Your local forecast</B> (Zip ' + z + ', nearest CNM reporting city: ' + wxCity[c] + ')<BR>');
  document.write(wxFc[c] + '. High <B>' + wxHi[c] + '</B>, low <B>' + wxLo[c] + '</B>.</FONT></TD></TR></TABLE><BR>');
}
//--></SCRIPT>
""" % (cities, icons, his, los, fcs, zm)
    R = __import__("random").Random(1220)
    kinds = ["sun", "partly", "cloud", "rain", "snow", "storm"]
    rows = ""
    for i, w in enumerate(data.WEATHER):
        bg = ' BGCOLOR="#EEEEEE"' if i % 2 else ""
        ext = ""
        for dname in ("TUE", "WED"):
            k = kinds[(kinds.index(w[2]) + R.choice([-1, 0, 1])) % len(kinds)]
            dh, dl = R.randint(-6, 6), R.randint(-5, 5)
            if w[3] > 50 and k == "snow":
                k = "rain"
            ext += '<TD ALIGN=CENTER><IMG SRC="images/wxs_%s.gif" WIDTH=20 HEIGHT=20 ALT="%s"><BR><FONT %s SIZE=1>%d/%d</FONT></TD>' % (
                k, k, VERD, w[3] + dh, min(w[4] + dl, w[3] + dh - 5))
        rows += '<TR%s><TD><A NAME="c%d"></A><FONT %s SIZE=2><B>%s</B>, %s</FONT></TD><TD ALIGN=CENTER><IMG SRC="images/wx_%s.gif" WIDTH=40 HEIGHT=40 ALT="%s"></TD><TD><FONT %s SIZE=1>%s</FONT></TD><TD ALIGN=RIGHT><FONT %s SIZE=2 COLOR="#CC0000"><B>%d</B></FONT></TD><TD ALIGN=RIGHT><FONT %s SIZE=2 COLOR="#0000CC"><B>%d</B></FONT></TD>%s</TR>\n' % (
            bg, i, ARIAL, esc(w[0]), esc(w[1]), w[2], w[2], VERD, esc(w[5]), ARIAL, w[3], ARIAL, w[4], ext)
    intl = "".join('<TR><TD><FONT %s SIZE=2><B>%s</B>, %s</FONT></TD><TD ALIGN=CENTER><IMG SRC="images/wxs_%s.gif" WIDTH=20 HEIGHT=20 ALT="%s"></TD><TD ALIGN=RIGHT><FONT %s SIZE=2>%d/%d</FONT></TD></TR>\n'
                   % (ARIAL, esc(a), esc(b), k, k, VERD, hi, lo) for a, b, k, hi, lo in data.WEATHER_INTL)
    stories = "".join('<LI><A HREF="%s">%s</A>\n' % (story_url(s), esc(s["headline"])) for s in sec_stories("WEATHER"))
    content = title_gif(P, "sec_forecast.gif", "Weather forecasts") + """<SCRIPT LANGUAGE="JavaScript"><!--
localForecast();
//--></SCRIPT>
<TABLE WIDTH=630 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR>
<TD WIDTH=400 VALIGN=TOP><IMG SRC="images/us_map.gif" WIDTH=400 HEIGHT=250 ALT="U.S. weather map"><BR>
<FONT %s SIZE=1>Blue line: cold front, moving east. Numbers: today's highs. Map not to scale, or to any particular projection.</FONT></TD>
<TD WIDTH=10>&nbsp;</TD>
<TD WIDTH=220 VALIGN=TOP>
%s
<FORM NAME="wxform" ACTION="weather.html" METHOD=GET onSubmit="return zipCheck(this);">
<FONT %s SIZE=1>Enter a U.S. Zip code for your local forecast:</FONT><BR>
<INPUT TYPE=TEXT NAME="zip" SIZE=6 MAXLENGTH=5> <INPUT TYPE=SUBMIT VALUE="Go">
</FORM>
%s
<FONT %s SIZE=2><UL>%s</UL></FONT>
</TD></TR></TABLE><BR>
%s
<TABLE WIDTH=630 BORDER=0 CELLPADDING=3 CELLSPACING=0>
<TR BGCOLOR="#666699"><TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>CITY</B></FONT></TD><TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>MON</B></FONT></TD>
<TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>FORECAST</B></FONT></TD><TD ALIGN=RIGHT><FONT %s SIZE=1 COLOR="#FFFFFF"><B>HI</B></FONT></TD><TD ALIGN=RIGHT><FONT %s SIZE=1 COLOR="#FFFFFF"><B>LO</B></FONT></TD>
<TD ALIGN=CENTER><FONT %s SIZE=1 COLOR="#FFFFFF"><B>TUE</B></FONT></TD><TD ALIGN=CENTER><FONT %s SIZE=1 COLOR="#FFFFFF"><B>WED</B></FONT></TD></TR>
%s</TABLE><BR>
%s
<TABLE WIDTH=400 BORDER=0 CELLPADDING=3 CELLSPACING=0>
%s</TABLE>
<P><FONT %s SIZE=1><I>Forecasts by the CNM Weather Unit. Temperatures in degrees Fahrenheit. Forecasts beyond
48 hours are about as reliable as a 1980s computer clock.</I></FONT>
""" % (VERD, box_title("FIND YOUR FORECAST", 220), VERD, box_title("WEATHER NEWS", 220), ARIAL, stories,
       box_title("U.S. CITIES", 630), VERD, VERD, VERD, VERD, VERD, VERD, VERD, rows,
       box_title("AROUND THE WORLD", 400), intl, VERD)
    page("weather.html", "CNM - Weather - %s" % data.TODAY, content, current="WEATHER", script=js, label="WEATHER")


# ------------------------------------------------------------------ misc pages
GETPARAM_JS = """function getParam(name) {
  var q = location.search.substring(1);
  var parts = q.split("&");
  var i;
  for (i = 0; i < parts.length; i++) {
    var kv = parts[i].split("=");
    if (kv[0] == name && kv.length > 1) return unescape(kv[1].replace(/\\+/g, " "));
  }
  return "";
}
function getParams(name) {
  var q = location.search.substring(1);
  var parts = q.split("&");
  var out = new Array();
  var i;
  for (i = 0; i < parts.length; i++) {
    var kv = parts[i].split("=");
    if (kv[0] == name && kv.length > 1) out[out.length] = unescape(kv[1].replace(/\\+/g, " "));
  }
  return out;
}
function clean(t) {
  return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
"""


def customnews_pages():
    checks = "".join('<TD><INPUT TYPE=CHECKBOX NAME="sec" VALUE="%s"%s><FONT %s SIZE=2>%s</FONT></TD>%s' % (
        code, " CHECKED" if code in ("US", "WORLD") else "", ARIAL, nav, "</TR><TR>" if i % 3 == 2 else "")
        for i, (code, nav, dirn, t, b) in enumerate(SECTIONS))
    js = """<SCRIPT LANGUAGE="JavaScript"><!--
%s
function cnCheck(f) {
  var i, any = false;
  if (f.name.value == "") { alert("Please tell us your name."); f.name.focus(); return false; }
  if (f.email.value.indexOf("@") < 1 || f.email.value.indexOf(".") < 0) {
    alert("Please enter a valid e-mail address, such as you@yourisp.com");
    f.email.focus();
    return false;
  }
  for (i = 0; i < f.sec.length; i++) if (f.sec[i].checked) any = true;
  if (!any) { alert("Please choose at least one news section."); return false; }
  return true;
}
function prefill() {
  var e = getParam("email");
  if (e != "") document.forms["cn"].email.value = e;
}
//--></SCRIPT>
""" % GETPARAM_JS
    content = title_gif("", "sec_customnews.gif", "Custom News") + """<FONT %s SIZE=2>Build your own front page, delivered to your
e-mail box every morning before your coffee is ready -- or, with a 28.8 modem, shortly after. Choose the sections you
want, tell us where to send them, and CNM Custom News does the rest. It's free!</FONT><BR><BR>
<FORM NAME="cn" ACTION="customnews_thanks.html" METHOD=GET onSubmit="return cnCheck(this);">
<TABLE WIDTH=600 BORDER=0 CELLPADDING=4 CELLSPACING=0 BGCOLOR="#CCCCFF">
<TR><TD><FONT %s SIZE=2><B>Your name:</B></FONT></TD><TD><INPUT TYPE=TEXT NAME="name" SIZE=30></TD></TR>
<TR><TD><FONT %s SIZE=2><B>E-mail address:</B></FONT></TD><TD><INPUT TYPE=TEXT NAME="email" SIZE=30></TD></TR>
<TR><TD VALIGN=TOP><FONT %s SIZE=2><B>Sections:</B></FONT></TD><TD><TABLE BORDER=0 CELLPADDING=1 CELLSPACING=0><TR>%s</TR></TABLE></TD></TR>
<TR><TD><FONT %s SIZE=2><B>Format:</B></FONT></TD><TD><FONT %s SIZE=2>
<INPUT TYPE=RADIO NAME="fmt" VALUE="html" CHECKED> HTML (with pictures)
<INPUT TYPE=RADIO NAME="fmt" VALUE="text"> Plain text
<INPUT TYPE=RADIO NAME="fmt" VALUE="both"> Both, twice</FONT></TD></TR>
<TR><TD><FONT %s SIZE=2><B>How often:</B></FONT></TD><TD><SELECT NAME="freq">
<OPTION VALUE="daily" SELECTED>Every morning
<OPTION VALUE="weekly">Once a week
<OPTION VALUE="breaking">Breaking news only
<OPTION VALUE="bug">Only if the Bug strikes
</SELECT></TD></TR>
<TR><TD>&nbsp;</TD><TD><INPUT TYPE=SUBMIT VALUE="Sign me up"> <INPUT TYPE=RESET VALUE="Clear"></TD></TR>
</TABLE>
</FORM>
<FONT %s SIZE=1><I>We will never sell your address. We might mention it fondly at parties. See our
<A HREF="privacy.html">privacy guidelines</A>.</I></FONT>
""" % (ARIAL, ARIAL, ARIAL, ARIAL, checks, ARIAL, ARIAL, ARIAL, ARIAL)
    page("customnews.html", "CNM - Custom News", content, script=js, onload="prefill()", label="CUSTOM NEWS")

    secmap = ",".join("%s,%s,%s" % (jsstr(code), jsstr(nav), jsstr(sec_url(code))) for code, nav, d, t, b in SECTIONS)
    js2 = """<SCRIPT LANGUAGE="JavaScript"><!--
%s
var secs = new Array(%s);
function thanks() {
  var name = getParam("name"), email = getParam("email"), chosen = getParams("sec");
  var i, j, freq = getParam("freq");
  var f = '<FONT FACE="Arial, Helvetica" SIZE=2>';
  if (name == "") name = "news fan";
  document.write(f + '<FONT SIZE=4><B>Thanks, ' + clean(name) + '!</B></FONT><BR><BR>');
  if (email != "") document.write('Your CNM Custom News will be delivered to <B>' + clean(email) + '</B>');
  else document.write('Your CNM Custom News will be delivered');
  if (freq == "weekly") document.write(' once a week');
  else if (freq == "breaking") document.write(' whenever news breaks');
  else if (freq == "bug") document.write(' only if the Y2K bug strikes (so, hopefully, never)');
  else document.write(' every morning');
  document.write('. You chose:</FONT><UL>');
  for (i = 0; i < chosen.length; i++) {
    for (j = 0; j < secs.length; j = j + 3) {
      if (secs[j] == chosen[i]) document.write('<LI>' + f + '<A HREF="' + secs[j + 2] + '">' + secs[j + 1] + '</A></FONT>');
    }
  }
  document.write('</UL>');
}
//--></SCRIPT>
""" % (GETPARAM_JS, secmap)
    content = title_gif("", "sec_customnews.gif", "Custom News") + """<SCRIPT LANGUAGE="JavaScript"><!--
thanks();
//--></SCRIPT>
<NOSCRIPT><FONT %s SIZE=4><B>Thanks for signing up!</B></FONT></NOSCRIPT>
<FONT %s SIZE=2>Your first edition should arrive within 24 hours. If it doesn't, check that your mailbox isn't full
(some services give you only 2 MB!), or <A HREF="customnews.html">sign up again</A>.<BR><BR>
<B><A HREF="index.html">Return to the CNM.com main page</A></B></FONT>
""" % (ARIAL, ARIAL)
    page("customnews_thanks.html", "CNM - Custom News - Thank you", content, script=js2, label="CUSTOM NEWS")


def feedback_pages():
    js = """<SCRIPT LANGUAGE="JavaScript"><!--
function fbCheck(f) {
  if (f.comments.value.length < 5) { alert("Please type a comment. Even a short one. Even 'hi'."); return false; }
  if (f.email.value != "" && f.email.value.indexOf("@") < 1) { alert("That e-mail address doesn't look right."); return false; }
  return true;
}
//--></SCRIPT>
"""
    content = title_gif("", "sec_feedback.gif", "Feedback") + """<FONT %s SIZE=2>We read every message. Well, we read the subject
line of every message. Tell us what you think about CNM.com, a story, a typo, or the fact that our pages take
forever to load on your 14.4.</FONT><BR><BR>
<FORM NAME="fb" ACTION="feedback_thanks.html" METHOD=GET onSubmit="return fbCheck(this);">
<TABLE WIDTH=600 BORDER=0 CELLPADDING=4 CELLSPACING=0 BGCOLOR="#CCCCFF">
<TR><TD><FONT %s SIZE=2><B>Name:</B></FONT></TD><TD><INPUT TYPE=TEXT NAME="name" SIZE=30></TD></TR>
<TR><TD><FONT %s SIZE=2><B>E-mail (optional):</B></FONT></TD><TD><INPUT TYPE=TEXT NAME="email" SIZE=30></TD></TR>
<TR><TD><FONT %s SIZE=2><B>Topic:</B></FONT></TD><TD><SELECT NAME="topic">
<OPTION>A story<OPTION>The Web site<OPTION>QuickVote<OPTION>Y2K<OPTION>Weather<OPTION>Something else entirely</SELECT></TD></TR>
<TR><TD VALIGN=TOP><FONT %s SIZE=2><B>Comments:</B></FONT></TD><TD><TEXTAREA NAME="comments" ROWS=6 COLS=45 WRAP=VIRTUAL></TEXTAREA></TD></TR>
<TR><TD>&nbsp;</TD><TD><INPUT TYPE=SUBMIT VALUE="Send feedback"> <INPUT TYPE=RESET VALUE="Clear"></TD></TR>
</TABLE></FORM>
""" % (ARIAL, ARIAL, ARIAL, ARIAL, ARIAL)
    page("feedback.html", "CNM - Feedback", content, script=js, label="FEEDBACK")
    js2 = """<SCRIPT LANGUAGE="JavaScript"><!--
%s//--></SCRIPT>
""" % GETPARAM_JS
    content = title_gif("", "sec_feedback.gif", "Feedback") + """<SCRIPT LANGUAGE="JavaScript"><!--
var who = getParam("name");
document.write('<FONT FACE="Arial, Helvetica" SIZE=4><B>Thank you' + (who != "" ? ', ' + clean(who) : '') + '!</B></FONT><BR><BR>');
//--></SCRIPT>
<FONT %s SIZE=2>Your message has been placed in our feedback queue, where it is currently number 41,207. An editor will
read it shortly, for a newsroom definition of "shortly."<BR><BR>
<B><A HREF="index.html">Back to the CNM.com main page</A></B></FONT>
""" % ARIAL
    page("feedback_thanks.html", "CNM - Feedback - Thank you", content, script=js2, label="FEEDBACK")


def quiz_page():
    qs = ""
    for i, (q, choices, right, slug) in enumerate(data.QUIZ):
        opts = "".join('<INPUT TYPE=RADIO NAME="q%d" VALUE="%d"> %s<BR>\n' % (i, j, esc(c)) for j, c in enumerate(choices))
        qs += """<TR><TD VALIGN=TOP><FONT %s SIZE=3><B>%d.</B></FONT></TD><TD><FONT %s SIZE=2><B>%s</B><BR>
%s<INPUT TYPE=TEXT NAME="a%d" SIZE=50 VALUE=""> <A HREF="%s"><FONT SIZE=1>read the story</FONT></A></FONT><BR><BR></TD></TR>
""" % (ARIAL, i + 1, ARIAL, esc(q), opts, i, story_url(BY_SLUG[slug]))
    answers = ",".join(str(r) for q, c, r, s in data.QUIZ)
    texts = ",".join(jsstr(c[r]) for q, c, r, s in data.QUIZ)
    js = """<SCRIPT LANGUAGE="JavaScript"><!--
var answers = new Array(%s);
var answerText = new Array(%s);
function scoreQuiz(f) {
  var right = 0, i, j, picked;
  for (i = 0; i < answers.length; i++) {
    picked = -1;
    var r = f.elements["q" + i];
    for (j = 0; j < r.length; j++) if (r[j].checked) picked = j;
    if (picked == answers[i]) { right++; f.elements["a" + i].value = "Correct!"; }
    else if (picked == -1) f.elements["a" + i].value = "No answer. It was: " + answerText[i];
    else f.elements["a" + i].value = "Sorry -- the answer is: " + answerText[i];
  }
  var rank;
  if (right == 10) rank = "Anchor material. Report to makeup.";
  else if (right >= 8) rank = "Senior correspondent.";
  else if (right >= 5) rank = "Promising intern.";
  else if (right >= 2) rank = "Have you considered reading the news?";
  else rank = "Are you sure your browser is Y2K compliant?";
  f.score.value = right + " out of " + answers.length;
  alert("You scored " + right + " out of " + answers.length + ". " + rank);
  return false;
}
//--></SCRIPT>
""" % (answers, texts)
    content = title_gif("", "sec_quiz.gif", "News Quiz") + """<FONT %s SIZE=2>How closely have you been following the news this month?
Answer all 10 questions, then press <B>Score my quiz</B>. No peeking at the stories -- or do; we can't actually tell.</FONT><BR><BR>
<FORM NAME="quiz" onSubmit="return scoreQuiz(this);">
<TABLE WIDTH=600 BORDER=0 CELLPADDING=2 CELLSPACING=0>
%s</TABLE>
<INPUT TYPE=BUTTON VALUE="Score my quiz" onClick="scoreQuiz(this.form);"> <INPUT TYPE=RESET VALUE="Start over">
&nbsp;<FONT %s SIZE=2><B>Your score:</B></FONT> <INPUT TYPE=TEXT NAME="score" SIZE=12>
</FORM>
""" % (ARIAL, qs, ARIAL)
    page("quiz.html", "CNM - News Quiz - Week of December 13, 1999", content, script=js, label="NEWS QUIZ")


def almanac_page():
    a = data.ALMANAC
    hist = "".join('<TR><TD VALIGN=TOP><FONT %s SIZE=2><B>%s</B></FONT></TD><TD><FONT %s SIZE=2>%s</FONT></TD></TR>\n' % (ARIAL, y, ARIAL, esc(t)) for y, t in a["history"])
    bdays = "".join("<LI>%s\n" % esc(b) for b in a["birthdays"])
    content = title_gif("", "sec_almanac.gif", "Daily Almanac") + """<FONT %s SIZE=4><B>%s</B></FONT><BR>
<FONT %s SIZE=2>%s<BR>%s<BR>%s</FONT><BR><BR>
<TABLE WIDTH=630 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR>
<TD WIDTH=400 VALIGN=TOP>%s
<TABLE WIDTH=400 BORDER=0 CELLPADDING=3 CELLSPACING=0>
%s</TABLE></TD>
<TD WIDTH=10>&nbsp;</TD>
<TD WIDTH=220 VALIGN=TOP>%s
<FONT %s SIZE=2><UL>%s</UL></FONT>
%s
<FONT %s SIZE=2><I>%s</I><BR>%s</FONT><BR><BR>
%s
<FONT %s SIZE=5 COLOR="#CC0000"><B>%s</B></FONT><BR><FONT %s SIZE=2>%s</FONT><BR><BR>
%s
</TD></TR></TABLE>
""" % (ARIAL, a["day"], ARIAL, a["dayno"], a["sun"], a["moon"], box_title("ON THIS DAY", 400), hist,
       box_title("BIRTHDAYS", 220), ARIAL, bdays, box_title("QUOTE OF THE DAY", 220), ARIAL, esc(a["quote"][0]), esc(a["quote"][1]),
       box_title("NUMBER OF THE DAY", 220), ARIAL, a["number"][0], ARIAL, esc(a["number"][1]), countdown_box(""))
    page("almanac.html", "CNM - Daily Almanac - %s" % data.TODAY, content, onload="cdTick()", script=COUNTDOWN_JS, label="ALMANAC")


def brief_page():
    latest = STORIES[:10]
    top = "".join('<TR><TD VALIGN=TOP NOWRAP><FONT %s SIZE=1>%s<BR>Dec. %d</FONT></TD><TD><FONT %s SIZE=2><B><A HREF="%s">%s</A></B><BR>%s</FONT></TD></TR>\n'
                  % (VERD, time_str(s, False), s["day"], ARIAL, story_url(s), esc(s["headline"]), esc(s["summary"])) for s in latest)
    rest = ""
    for code, nav, dirn, t, b in SECTIONS:
        rest += '<FONT %s SIZE=2><B><A HREF="%s">%s</A></B></FONT><FONT %s SIZE=2><UL>%s</UL></FONT>\n' % (
            ARIAL, sec_url(code), nav, ARIAL,
            "".join('<LI><A HREF="%s">%s</A> <FONT SIZE=1 COLOR="#666666">Dec. %d</FONT>\n' % (story_url(s), esc(s["headline"]), s["day"]) for s in sec_stories(code)))
    content = title_gif("", "sec_brief.gif", "Headline News brief") + """<FONT %s SIZE=2>The news in a hurry. The ten latest stories,
followed by every headline on CNM.com this month. Perfect for reading on a 14.4 modem, or during a commercial.</FONT><BR><BR>
%s<TABLE WIDTH=630 BORDER=0 CELLPADDING=4 CELLSPACING=0>
%s</TABLE><BR>
%s%s
""" % (ARIAL, box_title("LATEST HEADLINES", 630), top, box_title("ALL HEADLINES BY SECTION", 630), rest)
    page("brief.html", "CNM - Headline News brief - %s" % data.TODAY, content, label="BRIEF")


def player_page(rel, kind):
    video = kind == "video"
    still = '<IMG SRC="images/video_still.gif" WIDTH=320 HEIGHT=240 ALT="CNM video">' if video else \
            '<TABLE WIDTH=320 HEIGHT=120 BGCOLOR="#000033"><TR><TD ALIGN=CENTER><FONT %s SIZE=4 COLOR="#33FF33">CNM RADIO<BR>NETCAST</FONT></TD></TR></TABLE>' % VERD
    js = """<SCRIPT LANGUAGE="JavaScript"><!--
var pct = 0, playing = false, msgs = 0;
function setStat(t) { document.forms["player"].stat.value = t; }
function play(speed) {
  if (playing) return;
  playing = true;
  pct = 0;
  setStat("Contacting server (" + speed + "k)...");
  setTimeout("buffer()", 1500);
}
function buffer() {
  if (!playing) return;
  pct = pct + Math.floor(Math.random() * 9) + 1;
  if (pct >= 99) {
    pct = 99;
    msgs++;
    setStat("Network congestion. Rebuffering... (attempt " + msgs + ")");
    pct = Math.floor(Math.random() * 40);
    setTimeout("buffer()", 2500);
    return;
  }
  setStat("Buffering... " + pct + "%");
  setTimeout("buffer()", 700);
}
function stopClip() { playing = false; setStat("Stopped."); }
function getPlugin() {
  alert("The ReelPlayer G2 download servers are very busy. Estimated download time at 28.8: 71 minutes. Please try again after the new millennium.");
}
//--></SCRIPT>
"""
    clips = ["noreaster", "y2k.drill", "netspud.ipo", "lobstermen.win", "marisol.dateline", "thousandaire", "granite.debate", "silver.lame"]
    lst = "".join('<TR><TD><IMG SRC="images/icon_%s.gif" WIDTH=10 HEIGHT=10 ALT=""></TD><TD><FONT %s SIZE=2><A HREF="%s">%s</A></FONT></TD>'
                  '<TD NOWRAP><FONT %s SIZE=1><A HREF="javascript:play(28)">28k</A> | <A HREF="javascript:play(56)">56k</A> | <A HREF="javascript:play(100)">100k</A></FONT></TD></TR>\n'
                  % (kind, ARIAL, story_url(BY_SLUG[c]), esc(BY_SLUG[c]["headline"]), VERD) for c in clips)
    noun = "video" if video else "audio"
    content = title_gif("", "sec_%s.gif" % kind, kind.upper()) + """<TABLE WIDTH=630 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR>
<TD WIDTH=340 VALIGN=TOP>
<TABLE BORDER=3 CELLPADDING=0 CELLSPACING=0 BGCOLOR="#C0C0C0"><TR><TD ALIGN=CENTER>%s<BR>
<FORM NAME="player">
<INPUT TYPE=BUTTON VALUE=" Play " onClick="play(28);"> <INPUT TYPE=BUTTON VALUE=" Stop " onClick="stopClip();">
<INPUT TYPE=TEXT NAME="stat" SIZE=30 VALUE="Ready."></FORM></TD></TR></TABLE>
</TD>
<TD WIDTH=10>&nbsp;</TD>
<TD WIDTH=280 VALIGN=TOP><FONT %s SIZE=2>
<B>%s of the Day:</B> Nor'easter buries the Maine coast. CNM's Gil Haverstock reports from Port Halloway,
where the CyberLobster Internet cafe has closed early.<BR><BR>
This %s requires the <B>ReelPlayer G2</B> plug-in, version 6.0.3.162 or later. If you have version 6.0.3.161,
we're very sorry.<BR><BR>
<A HREF="javascript:getPlugin()"><IMG SRC="images/reelplayer.gif" WIDTH=88 HEIGHT=31 BORDER=0 ALT="Get ReelPlayer G2" ALIGN=LEFT HSPACE=4></A>
<FONT SIZE=1>Download the free player (14.2 MB). Installation requires a restart, a second restart,
and the patience of a saint.</FONT></FONT>
</TD></TR></TABLE><BR CLEAR=ALL>
%s
<TABLE WIDTH=630 BORDER=0 CELLPADDING=3 CELLSPACING=0>
%s</TABLE>
<P><FONT %s SIZE=1><I>Choose 28k for modems, 56k for faster modems, 100k for the lucky few with cable or a T1 at work.
Actual frame rate may resemble a slide show.</I></FONT>
""" % (still, ARIAL, noun.capitalize(), noun, box_title("MORE %s" % noun.upper(), 630), lst, ARIAL)
    page(rel, "CNM - %s" % noun.capitalize(), content, script=js, label=noun.upper())


def text_page(rel, gif, alt, title, paras, label):
    body = "".join("<P>%s\n" % p for p in paras)
    content = title_gif("", gif, alt) + '<FONT %s SIZE=2>%s</FONT>' % (ARIAL, body)
    page(rel, title, content, label=label)


def misc_pages():
    text_page("privacy.html", "sec_privacy.gif", "Privacy", "CNM - Privacy guidelines", [
        "<B>What we do (and mostly don't do) with your information</B>",
        "CNM Interactive respects your privacy, within reason and within the limits of 1999 technology.",
        "<B>Cookies.</B> Our site places a small file, called a cookie, on your computer. It remembers how you voted in QuickVote. It does not remember anything else, because frankly it is a very small cookie.",
        "<B>E-mail addresses.</B> If you sign up for Custom News, we use your address to send you the news. We will not sell it, rent it, or trade it for a Plushie Pal, however rare.",
        "<B>Server logs.</B> Our servers record which pages are visited, and when. We use this information to learn which stories are popular (fruitcake, mysteriously) and to decide how many more servers to buy.",
        "<B>Children.</B> CNM.com is a general news site. Children under 13 should ask a parent before filling out any form, and should probably be outside playing anyway.",
        "<B>Changes.</B> We may update these guidelines from time to time. If we do, we will post the changes here, in this same small type.",
        'Questions? <A HREF="feedback.html">Write to us</A>.'], "PRIVACY")
    text_page("terms.html", "sec_terms.gif", "Terms", "CNM - Terms of service", [
        "<B>The fine print under which we let you read any of this</B>",
        "By using CNM.com you agree to the following terms, which our lawyers wrote and which we have been told are binding.",
        "1. All material on this site is &copy; 1999 Cable News Mobile. You may read it, print it, and e-mail it to your mother. You may not republish it, sell it, or claim you wrote it.",
        "2. News is provided \"as is.\" We try to get everything right. When we don't, we correct it, usually in smaller type than the original.",
        "3. QuickVote results are not scientific, and neither, for that matter, are our weather forecasts beyond 48 hours.",
        "4. Links to other sites are provided as a convenience. We are not responsible for their content, their blinking text, or their background MIDI files.",
        "5. CNM.com is believed to be Year 2000 compliant. If on January 1 this page reads 1900, please stay calm and refresh.",
        "6. These terms are governed by the laws of the state in which our server is located, which is a matter of some dispute among our engineers.",
        '<A HREF="privacy.html">Read our privacy guidelines</A>.'], "TERMS")
    text_page("email.html", "sec_email.gif", "Free E-mail", "CNM - Free E-mail", [
        "<B>Get your own free @cnm.com e-mail address!</B>",
        "Coming soon: free, Web-based e-mail from CNM. Check your mail from any computer in the world with a browser and a phone line. Two full megabytes of storage -- enough for hundreds of messages, or one picture of your nephew.",
        'Sign-ups open on January 1, 2000 -- assuming January 1, 2000 opens. In the meantime, get the news delivered to your existing mailbox with <A HREF="customnews.html">CNM Custom News</A>.',
        '<FORM NAME="freemail"><INPUT TYPE=TEXT NAME="wanted" SIZE=20 VALUE="yourname">@cnm.com <INPUT TYPE=BUTTON VALUE="Reserve it" onClick="alert(\'Good news: \' + this.form.wanted.value + \'@cnm.com appears to be available. Bad news: so is everything else, because we have not launched yet.\');"></FORM>'],
        "FREE E-MAIL")
    # local
    stations = [("WKFM 6", "Port Halloway, Maine", "noreaster"), ("WGFO 11", "Gristmill Falls, Ohio", "y2k.drill"),
                ("KCOT 3", "Cotterville, Kansas", "beans.stockpile"), ("KDRY 9", "Dry Spoon, Arizona", "bunker.tour"),
                ("WLWM 4", "Lake Wendell, Minnesota", "town.clock"), ("KMOS 12", "Mossbank, Oregon", "celebrate.twice"),
                ("WHSF 7", "Halcyon Springs, Florida", "cash.atm"), ("KTWF 2", "Twin Forks, Montana", "lights.contest")]
    rows = "".join('<TR><TD><FONT %s SIZE=2><B>%s</B></FONT></TD><TD><FONT %s SIZE=2>%s</FONT></TD><TD><FONT %s SIZE=2><A HREF="%s">%s</A></FONT></TD></TR>\n'
                   % (ARIAL, st, ARIAL, city, ARIAL, story_url(BY_SLUG[sl]), esc(BY_SLUG[sl]["headline"])) for st, city, sl in stations)
    content = title_gif("", "sec_local.gif", "Local") + """<FONT %s SIZE=2>News from CNM affiliate stations across the country.
For your local weather, <A HREF="weather.html">enter your Zip code on our weather page</A>.</FONT><BR><BR>
<TABLE WIDTH=630 BORDER=0 CELLPADDING=4 CELLSPACING=0>
<TR BGCOLOR="#666699"><TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>STATION</B></FONT></TD><TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>CITY</B></FONT></TD><TD><FONT %s SIZE=1 COLOR="#FFFFFF"><B>TOP LOCAL STORY</B></FONT></TD></TR>
%s</TABLE>
<P><FONT %s SIZE=1><I>Don't see your town? Neither do we. We're working on it.</I></FONT>
""" % (ARIAL, VERD, VERD, VERD, rows, ARIAL)
    page("local.html", "CNM - Local news", content, label="LOCAL")
    # in-depth
    specials = [("y2k/index.html", "y2k_promo.gif", 150, 40, "Y2K: The Millennium Bug", "Countdown clock, readiness checklist and a country-by-country bug watch."),
                ("y2k/celebrations.html", "thumb_marisol.dateline.gif", 55, 45, "The Millennium", "Where midnight strikes first, and who moved the date line."),
                ("POLITICS/index.html", "thumb_granite.debate.gif", 55, 45, "Campaign 2000", "The candidates, the polls and one 30-minute infomercial."),
                ("BUSINESS/index.html", "thumb_netspud.ipo.gif", 55, 45, "Dot-com Fever", "IPOs, day traders and the future of potatoes."),
                (story_url(BY_SLUG["browser.war"]), "thumb_browser.war.gif", 55, 45, "The Browser War", "Netscope vs. Explorist, round 5."),
                ("weather.html", "wx_snow.gif", 40, 40, "Winter 1999", "La Nada, nor'easters and the New Year's Eve outlook.")]
    rows = "".join('<TR><TD VALIGN=TOP ALIGN=CENTER WIDTH=160><A HREF="%s"><IMG SRC="images/%s" WIDTH=%d HEIGHT=%d BORDER=0 ALT=""></A></TD><TD VALIGN=TOP><FONT %s SIZE=3><B><A HREF="%s">%s</A></B></FONT><BR><FONT %s SIZE=2>%s</FONT></TD></TR>\n'
                   % (u, g, w, h, ARIAL, u, t, ARIAL, d) for u, g, w, h, t, d in specials)
    content = title_gif("", "sec_indepth.gif", "In-Depth Specials") + """<FONT %s SIZE=2>CNM's in-depth special reports: the stories behind the stories,
with maps, timelines, and more clicking than is strictly necessary.</FONT><BR><BR>
<TABLE WIDTH=630 BORDER=0 CELLPADDING=6 CELLSPACING=0>
%s</TABLE>
""" % (ARIAL, rows)
    page("indepth.html", "CNM - In-Depth Specials", content, label="IN-DEPTH")


def main():
    for s in STORIES:
        story_page(s)
    for code, nav, dirn, t, b in SECTIONS:
        section_front(code)
    front_page()
    quickvote_pages()
    search_page()
    y2k_pages()
    weather_page()
    customnews_pages()
    feedback_pages()
    quiz_page()
    almanac_page()
    brief_page()
    player_page("video.html", "video")
    player_page("audio.html", "audio")
    misc_pages()
    with open(os.path.join(HERE, "pages.txt"), "w") as f:
        f.write("\n".join(sorted(WRITTEN)) + "\n")
    print("wrote %d pages (list in tools/pages.txt)" % len(WRITTEN))


if __name__ == "__main__":
    main()
