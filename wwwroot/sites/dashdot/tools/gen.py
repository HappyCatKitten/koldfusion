#!/usr/bin/env python3
"""Generates the static Dashdot site (Slashdot-style, October 1999) from tools/data.py.

Run from anywhere:  python3 tools/gen.py      (run tools/gfx.py first for the images)
Everything is pre-generated: story pages at every comment threshold, user pages, sections,
topics, polls.  "Dynamic" bits (login, moderation, posting, voting) are 1999-style JavaScript
that keeps its state in cookies.
"""
import os, sys, re, random, html, glob, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import data

RING = "yowza altavisor askreeves orinoco ubid etoyz petz geohoods hamstershuffle dashdot snapster cnm".split()
ME = "dashdot"
DAYS = {11: "Monday", 12: "Tuesday", 13: "Wednesday", 14: "Thursday", 15: "Friday", 16: "Saturday", 17: "Sunday", 18: "Monday"}
THRESHOLDS = [-1, 0, 1, 2, 3, 4, 5]
FRONT_COUNT = 12

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")

def tfile(key, t):
    if t == 1:
        return key + ".html"
    return "%s_t%s.html" % (key, "m1" if t < 0 else str(t))

def ring_url(name, prefix):
    return prefix + "../" + name + "/index.html"

def fix_ring(text, prefix):
    return re.sub(r"@RING:([a-z]+)@", lambda m: ring_url(m.group(1), prefix), text)

# ------------------------------------------------------------------ dates
def minutes(date):
    mo, d, h, mi = date
    return ((d - 11) * 24 + h) * 60 + mi

def from_minutes(m):
    d = 11 + m // 1440
    r = m % 1440
    return (10, d, r // 60, r % 60)

def fmt_date(date, tz=True):
    mo, d, h, mi = date
    ap = "AM" if h < 12 else "PM"
    hh = h % 12 or 12
    return "%s October %d, @%02d:%02d%s%s" % (DAYS.get(d, "Monday"), d, hh, mi, ap, " EDT" if tz else "")

def short_date(date):
    return "10/%02d %02d:%02d" % (date[1], date[2], date[3])

# ------------------------------------------------------------------ users
USERS = {}
for nick, uid, karma, bio in data.USERS:
    USERS[nick] = dict(nick=nick, uid=uid, karma=karma, bio=bio, comments=[], editor=False)
for nick, bio in data.EDITORS.items():
    USERS[nick] = dict(nick=nick, uid=data.EDITOR_UIDS[nick], karma=99, bio=bio, comments=[], editor=True)
REG_NICKS = [u[0] for u in data.USERS]

def user_link(nick, prefix):
    if nick in USERS:
        return '<A HREF="%susers/%s.html">%s</A>' % (prefix, slug(nick), esc(nick))
    return esc(nick)

# ------------------------------------------------------------------ stories
TOPIC = dict((t[0], t) for t in data.TOPICS)
SECTION = dict((s[0], s) for s in data.SECTIONS)
STORIES = sorted(data.STORIES, key=lambda s: minutes(s["date"]), reverse=True)
for s in STORIES:
    s["sid"] = "99/10/%02d/%02d%02d%03d" % (s["date"][1], s["date"][2], s["date"][3], zlib.crc32(s["key"].encode()) % 1000)
    s["dept_line"] = re.sub(r"\s+dept\.?$", "", s["dept"]).strip()
    t = s["title"]
    if s["section"] == "yro" and not t.startswith("Your Rights"):
        t = "Your Rights Online: " + t
    s["full_title"] = t

# ------------------------------------------------------------------ comments
KIND_REASON = {"insightful": "Insightful", "informative": "Informative", "interesting": "Interesting",
               "funny": "Funny", "troll": "Troll", "flamebait": "Flamebait", "offtopic": "Offtopic", "first": "Offtopic"}

def make_comments(story):
    rng = random.Random("dashdot-" + story["key"])
    t0 = minutes(story["date"])
    comments = []

    def author():
        r = rng.random()
        if r < 0.33:
            return "Anonymous Coward"
        if r < 0.36:
            return story["editor"]
        return rng.choice(REG_NICKS)

    def score_for(nick, kind, reply=False):
        if nick == "Anonymous Coward":
            base = 0
        elif nick in USERS and USERS[nick]["karma"] >= 25:
            base = 2
        else:
            base = 1
        reason = ""
        if kind in ("insightful", "informative", "interesting", "funny"):
            bump = rng.choice([0, 0, 0, 1, 1, 1, 2, 3] if reply else [0, 0, 1, 1, 2, 2, 3, 3, 4, 5])
            if bump:
                reason = KIND_REASON[kind]
            s = base + bump
        elif kind in ("troll", "flamebait", "offtopic", "first"):
            drop = rng.choice([0, 1, 1, 2])
            if drop:
                reason = KIND_REASON[kind]
            s = base - drop
        else:
            s = base
        s = max(-1, min(5, s))
        if s == base:
            reason = ""
        return s, reason

    def add(subject, body, kind, pid, at, nick=None):
        nick = nick or author()
        score, reason = score_for(nick, kind, pid != 0)
        c = dict(cid=len(comments) + 1, pid=pid, subject=subject, body=body, nick=nick, kind=kind,
                 score=score, reason=reason, date=from_minutes(at), children=[])
        comments.append(c)
        return c

    clock = t0 + rng.randint(1, 3)
    # the first-post sprint
    for i in range(rng.choice([0, 1, 1, 2])):
        subj, body, kind = rng.choice([g for g in data.GENERIC if g[2] == "first"])
        add(subj, body, kind, 0, clock, "Anonymous Coward" if rng.random() < 0.8 else None)
        clock += rng.randint(0, 2)
    # top level: story specific, interleaved with generic
    generic = [g for g in data.GENERIC if g[2] != "first"]
    rng.shuffle(generic)
    tops = list(story["comments"]) + generic[:rng.randint(4, 11)]
    head = tops[:2]
    rest = tops[2:]
    rng.shuffle(rest)
    tops = head + rest
    replies = list(data.REPLIES)
    rng.shuffle(replies)
    ri = 0
    target = rng.randint(14, 34) + 4 * len(story["comments"])
    for subj, body, kind in tops:
        clock += rng.randint(1, 14)
        add(subj, body, kind, 0, clock)
        # sprinkle replies after each top-level post
        while len(comments) < target and rng.random() < 0.62:
            clock += rng.randint(1, 20)
            # prefer recent, high scoring parents
            cand = comments[-8:]
            weights = [max(0.3, c["score"] + 1.5) for c in cand]
            parent = rng.choices(cand, weights=weights)[0]
            body2, kind2 = replies[ri % len(replies)]
            ri += 1
            psub = parent["subject"]
            subj2 = psub if psub.startswith("Re:") else "Re:" + psub
            add(subj2, body2, kind2, parent["cid"], clock)
    by = dict((c["cid"], c) for c in comments)
    for c in comments:
        if c["pid"]:
            by[c["pid"]]["children"].append(c)
        if c["nick"] in USERS:
            USERS[c["nick"]]["comments"].append((story, c))
    story["comment_list"] = comments
    story["by_cid"] = by
    story["total"] = len(comments)
    story["at"] = dict((t, sum(1 for c in comments if c["score"] >= t)) for t in THRESHOLDS)

for s in STORIES:
    make_comments(s)

# ------------------------------------------------------------------ fortunes
FORTUNES = [
    "You will be dashdotted within the hour. Back up your web server.",
    "Real programmers count from zero. Real sysadmins count backups.",
    "A clean desk is a sign of an empty inbox. Neither is likely.",
    "The year 2000 is just 1999 with better marketing.",
    "There are 10 kinds of people: those who read Dashdot at work, and those who are lying.",
    "Your karma is excellent. Your social life, less so.",
    "To err is human. To really foul things up requires a cron job.",
    "Any sufficiently advanced bug is indistinguishable from a feature.",
    "Today's lucky number is 0x2A. Tomorrow's is undefined.",
    "If at first you don't succeed, call it version 1.0.",
    "He who laughs last probably has a slower modem.",
    "The best way to predict the future is to set the clock forward and see what breaks.",
    "Never trust a computer you can't throw out a window.",
    "Moderation in all things, including moderation.",
    "Beware of programmers who carry screwdrivers.",
    "Your code compiles. Do not ask why. Simply accept the gift.",
    "Someone, somewhere, is posting 'first post' right now. Pray for them.",
    "Linix on the desktop: next year. It's always next year.",
]

# ------------------------------------------------------------------ javascript
JS_COOKIES = r"""
function getCookie(n) {
  var c = document.cookie.split("; ");
  for (var i = 0; i < c.length; i++) {
    var p = c[i].indexOf("=");
    if (p > 0 && c[i].substring(0, p) == n) return unescape(c[i].substring(p + 1));
  }
  return "";
}
function setCookie(n, v, days) {
  var e = "";
  if (days) { var d = new Date(); d.setTime(d.getTime() + days * 86400000); e = "; expires=" + d.toGMTString(); }
  document.cookie = n + "=" + escape(v) + e + "; path=/";
}
function delCookie(n) { document.cookie = n + "=; expires=Thu, 01-Jan-1970 00:00:01 GMT; path=/"; }
function qs(n) {
  var q = location.search.substring(1).split("&");
  for (var i = 0; i < q.length; i++) {
    var p = q[i].indexOf("=");
    if (p > 0 && q[i].substring(0, p) == n) return unescape(q[i].substring(p + 1).replace(/\+/g, " "));
  }
  return "";
}
function htmlEsc(s) {
  s = "" + s;
  s = s.replace(/&/g, "&amp;"); s = s.replace(/</g, "&lt;"); s = s.replace(/>/g, "&gt;"); s = s.replace(/"/g, "&quot;");
  return s;
}
"""

JS_RING = r"""
function ringRandom(p) {
  var s = new Array("yowza","altavisor","askreeves","orinoco","ubid","etoyz","petz","geohoods","hamstershuffle","snapster","cnm");
  var n = Math.floor(Math.random() * s.length);
  location.href = p + "../" + s[n] + "/" + "index.html";
  return false;
}
"""

JS_LOGIN = r"""
function ddLogin(f) {
  var n = f.unickname.value;
  if (n == "") { alert("Please enter a nickname. Even Anonymous Cowards have to type something."); return false; }
  if (f.upasswd.value == "") { alert("Please enter your password. (We won't look at it. We don't even keep it.)"); return false; }
  setCookie("dd_user", n, 30);
  if (getCookie("dd_points") == "") {
    setCookie("dd_points", "5", 3);
    alert("Welcome back, " + n + "!\n\nYou have been randomly selected to moderate.\nYou have 5 moderator points; they expire in 3 days.\nUse them wisely: look for the Moderate menus under each comment.");
  }
  location.reload();
  return false;
}
function ddLogout() { delCookie("dd_user"); location.reload(); }
function loginBox(root) {
  var u = getCookie("dd_user");
  if (u != "") {
    var p = getCookie("dd_points"); if (p == "") p = "0";
    document.write('<B>Welcome back, ' + htmlEsc(u) + '!</B><BR>Karma: Positive<BR>Moderator points: <B>' + p + '</B><P>');
    document.write('[ <A HREF="' + root + 'preferences.html">preferences</A> | <A HREF="javascript:ddLogout()">logout</A> ]');
  } else {
    document.write('<FORM ACTION="' + root + 'users.html" METHOD="get" onSubmit="return ddLogin(this)">');
    document.write('<B>Nickname:</B><BR><INPUT TYPE="text" NAME="unickname" SIZE=18><BR><B>Password:</B><BR>');
    document.write('<INPUT TYPE="password" NAME="upasswd" SIZE=18><BR><INPUT TYPE="submit" VALUE="userlogin"></FORM>');
    document.write('No account? <A HREF="' + root + 'users.html">Make one</A>. It\'s free, and it lets you pick your comment threshold, keep your nickname, and moderate when the dice say so.');
  }
}
"""

JS_ARTICLE = r"""
var MODPTS = 0;
if (getCookie("dd_user") != "") { MODPTS = parseInt("0" + getCookie("dd_points"), 10); }
var MODS = getCookie("dd_mods");
function S(c, b, r) {
  var d = 0, rr = r;
  if (MODS != "") {
    var a = MODS.split("|");
    for (var i = 0; i < a.length; i++) {
      var f = a[i].split(":");
      if (f[0] == SID && f[1] == "" + c) { d += parseInt(f[2], 10); rr = f[3]; }
    }
  }
  var s = b + d; if (s > 5) s = 5; if (s < -1) s = -1;
  document.write("(Score:" + s + (rr != "" ? ", " + rr : "") + ")");
}
function M(c) {
  if (MODPTS <= 0) return;
  document.write(' | <SELECT NAME="m' + c + '"><OPTION VALUE="">Moderate</OPTION>' +
    '<OPTION VALUE="-1:Offtopic">Offtopic</OPTION><OPTION VALUE="-1:Flamebait">Flamebait</OPTION>' +
    '<OPTION VALUE="-1:Troll">Troll</OPTION><OPTION VALUE="-1:Redundant">Redundant</OPTION>' +
    '<OPTION VALUE="1:Insightful">Insightful</OPTION><OPTION VALUE="1:Interesting">Interesting</OPTION>' +
    '<OPTION VALUE="1:Informative">Informative</OPTION><OPTION VALUE="1:Funny">Funny</OPTION>' +
    '<OPTION VALUE="-1:Overrated">Overrated</OPTION><OPTION VALUE="1:Underrated">Underrated</OPTION></SELECT>');
}
function modButton() {
  if (MODPTS > 0) {
    document.write('<CENTER><TABLE BORDER=0 CELLPADDING=4 BGCOLOR="#CCCCCC"><TR><TD ALIGN=CENTER><FONT SIZE=2>' +
      'You have <B>' + MODPTS + '</B> moderator point(s). Pick reasons from the menus above, then ' +
      '<INPUT TYPE="button" VALUE="Moderate" onClick="doMod()"></FONT></TD></TR></TABLE></CENTER>');
  }
}
function doMod() {
  var f = document.forms["mod"];
  var list = new Array();
  for (var i = 0; i < f.elements.length; i++) {
    var e = f.elements[i];
    if (e.name && e.name.charAt(0) == "m" && e.options) {
      var v = e.options[e.selectedIndex].value;
      if (v != "") list[list.length] = SID + ":" + e.name.substring(1) + ":" + v;
    }
  }
  if (list.length == 0) { alert("You didn't pick any moderations. Choose a reason from a comment's Moderate menu first."); return; }
  if (list.length > MODPTS) { alert("You only have " + MODPTS + " moderator point(s) left, but you picked " + list.length + "."); return; }
  var m = getCookie("dd_mods");
  for (var j = 0; j < list.length; j++) m += (m == "" ? "" : "|") + list[j];
  while (m.length > 3000) m = m.substring(m.indexOf("|") + 1);
  setCookie("dd_mods", m, 30);
  setCookie("dd_points", "" + (MODPTS - list.length), 3);
  location.href = ROOT + "moderated.html?n=" + list.length + "&sid=" + SID;
}
function mine() {
  var raw = getCookie("dd_posts_" + SID);
  if (raw == "") return;
  var recs = raw.split("~#~");
  document.write('<A NAME="mine"></A><P><TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0><TR><TD BGCOLOR="#006666"><FONT SIZE=2 COLOR="#FFFFFF"><B>Your comments</B> (saved in your browser until the next cron run weaves them into the thread)</FONT></TD></TR></TABLE>');
  for (var i = 0; i < recs.length; i++) {
    var f = recs[i].split("~|~");
    if (f.length < 6) continue;
    var sc = (f[1] == "Anonymous Coward") ? 0 : 1;
    document.write('<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0><TR><TD BGCOLOR="#CCCCCC">' +
      '<FONT SIZE=3 COLOR="#000000"><B>' + htmlEsc(f[2]) + '</B></FONT> (Score:' + sc + ')<BR><FONT SIZE=2>by ' +
      (f[1] == "Anonymous Coward" ? "Anonymous Coward" : '<B>' + htmlEsc(f[1]) + '</B>') + ' on ' + htmlEsc(f[4]) +
      (f[0] != "0" ? ' (reply to <A HREF="#' + f[0] + '">#' + f[0] + '</A>)' : '') + '</FONT></TD></TR>' +
      '<TR><TD><FONT SIZE=2>' + f[3] + '</FONT></TD></TR></TABLE><P>');
  }
}
"""

JS_REPLY = r"""
function cleanBody(t, mode) {
  var s = htmlEsc(t);
  if (mode == "html") {
    s = s.replace(/&lt;(\/?)(b|i|p|br|em|strong|tt|blockquote)&gt;/gi, "<$1$2>");
  }
  s = s.replace(/\r\n/g, "\n").replace(/\n\n/g, "<P>").replace(/\n/g, "<BR>");
  return s;
}
function lame(f) {
  var b = f.postercomment.value, s = f.postersubj.value;
  if (s == "") return "Please give your comment a subject.";
  if (b.length < 4) return "Your comment is too short. Even 'first post' has ten characters. (Don't post that either.)";
  if (/f(i|ri|ir)r?st\s*p(o|s)(s|o)?t/i.test(b + " " + s)) return "Lameness filter encountered. Post aborted!\n\nReason: your comment appears to be a 'first post'. It isn't, and it never is.";
  var caps = b.replace(/[^A-Z]/g, "").length, lows = b.replace(/[^a-z]/g, "").length;
  if (caps > 20 && caps > lows * 2) return "Lameness filter encountered. Post aborted!\n\nReason: please don't use so many caps. It's like YELLING.";
  return "";
}
function posterName(f) {
  var u = getCookie("dd_user");
  if (u == "" || f.postanon.checked) return "Anonymous Coward";
  return u;
}
function nowStr() {
  var d = new Date();
  var days = new Array("Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday");
  var mons = new Array("January","February","March","April","May","June","July","August","September","October","November","December");
  var h = d.getHours(), ap = (h < 12) ? "AM" : "PM"; h = h % 12; if (h == 0) h = 12;
  var m = d.getMinutes();
  return days[d.getDay()] + " " + mons[d.getMonth()] + " " + d.getDate() + ", @" + (h < 10 ? "0" : "") + h + ":" + (m < 10 ? "0" : "") + m + ap;
}
function preview(f) {
  var msg = lame(f);
  if (msg != "") { alert(msg); return; }
  var w = window.open("", "ddpreview", "width=520,height=320,scrollbars=yes,resizable=yes");
  w.document.open();
  w.document.write('<HTML><HEAD><TITLE>Dashdot | Preview</TITLE></HEAD><BODY BGCOLOR="#FFFFFF" TEXT="#000000">' +
    '<TABLE WIDTH="100%" BORDER=0 CELLPADDING=3 CELLSPACING=0><TR><TD BGCOLOR="#CCCCCC"><FONT FACE="arial,helvetica" SIZE=3><B>' +
    htmlEsc(f.postersubj.value) + '</B></FONT> (Score:?)<BR><FONT FACE="arial,helvetica" SIZE=2>by ' + htmlEsc(posterName(f)) +
    ' on ' + nowStr() + '</FONT></TD></TR><TR><TD><FONT FACE="arial,helvetica" SIZE=2>' +
    cleanBody(f.postercomment.value, f.posttype.options[f.posttype.selectedIndex].value) +
    '</FONT></TD></TR></TABLE><P><CENTER><FORM><INPUT TYPE="button" VALUE="Close Preview" onClick="window.close()"></FORM></CENTER></BODY></HTML>');
  w.document.close();
}
function postIt(f) {
  var msg = lame(f);
  if (msg != "") { alert(msg); return false; }
  var sid = f.sid.value, pid = f.pid.value;
  if (sid == "" || !TITLES[sid]) { alert("Which story were you replying to? Go back to the story and click Reply."); return false; }
  var rec = pid + "~|~" + posterName(f) + "~|~" + f.postersubj.value + "~|~" +
            cleanBody(f.postercomment.value, f.posttype.options[f.posttype.selectedIndex].value) + "~|~" + nowStr() + "~|~x";
  var old = getCookie("dd_posts_" + sid);
  var all = (old == "") ? rec : old + "~#~" + rec;
  while (escape(all).length > 3500 && all.indexOf("~#~") > 0) all = all.substring(all.indexOf("~#~") + 3);
  if (escape(all).length > 3500) { alert("That comment is too long for our state-of-the-art cookie-based database. Please trim it a little."); return false; }
  setCookie("dd_posts_" + sid, all, 30);
  location.href = "article/" + sid + ".html?posted=1#mine";
  return false;
}
"""

# ------------------------------------------------------------------ page chrome
def page_head(title, prefix, extra_js="", onload=""):
    js = JS_COOKIES + JS_RING + JS_LOGIN + extra_js
    return ('<HTML><HEAD><TITLE>%s</TITLE>\n<SCRIPT LANGUAGE="JavaScript"><!--\n%s\n//--></SCRIPT>\n</HEAD>\n'
            '<BODY BGCOLOR="#000000" TEXT="#000000" LINK="#006666" VLINK="#000000"%s>\n'
            % (esc(title), js, (' onLoad="%s"' % onload) if onload else ""))

def banner(prefix, n=0):
    if n % 2 == 0:
        img, alt, href = "banner_kf.gif", "KoldFusion 4.5 from Gibson Mainframe Co.", prefix + "advertising.html"
    else:
        img, alt, href = "banner_orinoco.gif", "Orinoco.com", ring_url("orinoco", prefix)
    return ('<CENTER><A HREF="%s"><IMG SRC="%simages/%s" WIDTH=468 HEIGHT=60 BORDER=0 ALT="%s"></A></CENTER><P>\n'
            % (href, prefix, img, alt))

def header(prefix, topics=None, n=0):
    out = [banner(prefix, n)]
    out.append('<TABLE BGCOLOR="#FFFFFF" CELLPADDING=0 CELLSPACING=0 BORDER=0 WIDTH="99%" ALIGN=CENTER><TR>\n'
               '<TD VALIGN=TOP ALIGN=LEFT><A HREF="' + prefix + 'index.html"><IMG SRC="' + prefix +
               'images/title.gif" WIDTH=300 HEIGHT=72 BORDER=0 ALT="Welcome to Dashdot"></A></TD>\n')
    if topics is None:
        topics = []
        for s in STORIES:
            if s["topic"] not in topics:
                topics.append(s["topic"])
            if len(topics) == 5:
                break
    for t in topics:
        tid, label, img = TOPIC[t]
        out.append('<TD ALIGN=CENTER VALIGN=BOTTOM><A HREF="%stopic_%s.html"><IMG SRC="%simages/%s" BORDER=0 ALT="%s"></A></TD>\n'
                   % (prefix, tid, prefix, img, esc(label)))
    out.append('</TR></TABLE>\n')
    return "".join(out)

NAV = [("faq", "faq.html"), ("code", "code.html"), ("awards", "awards.html"), ("privacy", "privacy.html"),
       ("dashNET", "dashnet.html"), ("older stuff", "older.html"), ("grits' page", "grits.html"),
       ("preferences", "preferences.html"), ("overandover.net", "overandover.html"), ("submit story", "submit.html"),
       ("advertising", "advertising.html"), ("supporters", "supporters.html"), ("past polls", "polls.html"),
       ("topics", "topics.html"), ("about", "about.html"), ("jobs", "jobs.html"), ("hof", "hof.html"),
       ("search", "search.html")]

def left_column(prefix):
    out = ['<TD VALIGN=TOP ROWSPAN=5 WIDTH=110 BGCOLOR="#FFFFFF"><NOBR><FONT FACE="arial,helvetica" SIZE=2><B>\n']
    out.append("<BR>\n".join('&nbsp;<A HREF="%s%s">%s</A>' % (prefix, h, l) for l, h in NAV))
    out.append('\n</B></FONT></NOBR>\n<P><TABLE BORDER=0 CELLPADDING=1 CELLSPACING=0 ALIGN=CENTER BGCOLOR="#CCCCCC"><TR>'
               '<TD><FONT FACE="arial,helvetica" SIZE=2 COLOR="#000000"><B>&nbsp;Sections</B></FONT></TD></TR>\n'
               '<TR><TD><TABLE BORDER=0 CELLSPACING=1 CELLPADDING=1 BGCOLOR="#FFFFFF" WIDTH="100%"><TR><TD><FONT FACE="arial,helvetica" COLOR="#000000" SIZE=2><NOBR>\n')
    for sec_id, fname, label, blurb in data.SECTIONS:
        ss = [s for s in STORIES if s["section"] == sec_id]
        last = ss[0]["date"] if ss else (10, 11, 0, 0)
        cnt = sum(1 for s in ss if s["date"][1] == STORIES[0]["date"][1])
        out.append('10/%02d%s<BR>\n<B><A HREF="%s%s.html">%s</A></B><BR>\n'
                   % (last[1], (" (%d)" % cnt) if cnt else "", prefix, fname, sec_id))
    out.append('</NOBR></FONT></TD></TR></TABLE></TD></TR>\n'
               '<TR><TD><FONT FACE="arial,helvetica" SIZE=2 COLOR="#000000"><B>&nbsp;Overandover.net</B></FONT></TD></TR>\n'
               '<TR><TD><TABLE BORDER=0 CELLSPACING=1 CELLPADDING=1 BGCOLOR="#FFFFFF" WIDTH="100%"><TR><TD><FONT FACE="arial,helvetica" COLOR="#000000" SIZE=2><NOBR>\n')
    for label, site in [("Snapster", "snapster"), ("CNM", "cnm"), ("Petz.com", "petz"), ("uBid", "ubid"), ("GeoHoods", "geohoods")]:
        out.append('<A HREF="%s">%s</A><BR>\n' % (ring_url(site, prefix), label))
    out.append('</NOBR></FONT></TD></TR></TABLE></TD></TR></TABLE><P>\n</TD>\n')
    return "".join(out)

def box(title, body, href=None):
    t = '<A HREF="%s"><FONT COLOR="#FFFFFF">%s</FONT></A>' % (href, title) if href else title
    return ('<TABLE CELLPADDING=1 CELLSPACING=0 BORDER=0 WIDTH=200 ALIGN=CENTER>\n<TR BGCOLOR="#006666"><TD VALIGN=TOP>'
            '<FONT SIZE=4 COLOR="#FFFFFF" FACE="arial,helvetica"><B>%s</B></FONT></TD></TR>\n'
            '<TR><TD BGCOLOR="#CCCCCC"><FONT FACE="arial,helvetica" COLOR="#000000" SIZE=2>\n%s\n</FONT></TD></TR></TABLE><P>\n'
            % (t, body))

def poll_form(prefix):
    pid, q, answers, ncom, _ = data.POLLS[0]
    total = sum(v for _, v in answers)
    rows = "".join('<INPUT TYPE="radio" NAME="aid" VALUE="%d">%s<BR>\n' % (i + 1, esc(a)) for i, (a, v) in enumerate(answers))
    return ('<FORM ACTION="%spollbooth.html" METHOD="get"><INPUT TYPE="hidden" NAME="qid" VALUE="%s">\n<B>%s</B><BR>\n%s'
            '<INPUT TYPE="submit" VALUE="Vote"> [ <A HREF="%spollbooth.html?qid=%s"><B>Results</B></A> | '
            '<A HREF="%spolls.html"><B>Polls</B></A> ]<BR>Comments:<B>%d</B> | Votes:<B>%d</B></FORM>'
            % (prefix, pid, esc(q), rows, prefix, pid, prefix, ncom, total))

def right_column(prefix, stories_on_page):
    out = ['<TD WIDTH=210 ALIGN=CENTER VALIGN=TOP>\n']
    by_key = dict((s["key"], s) for s in STORIES)
    feats = "<P>".join('%s <A HREF="%sarticle/%s.html">More...</A>' % (esc(txt), prefix, k) for k, txt in data.FEATURES_BOX)
    feats += '<P ALIGN=RIGHT><B><A HREF="%sfeatures.html">Past Features</A></B>' % prefix
    out.append(box("Features", feats, prefix + "features.html"))
    out.append(box("Dashdot Login", '<SCRIPT LANGUAGE="JavaScript"><!--\nloginBox("%s");\n//--></SCRIPT>\n'
                   '<NOSCRIPT><A HREF="%susers.html">Log in or create an account</A>.</NOSCRIPT>' % (prefix, prefix)))
    out.append(box("Dashdot Poll", poll_form(prefix)))
    # older stuff: stories not on this page, grouped by day
    shown = set(s["key"] for s in stories_on_page)
    older = [s for s in STORIES if s["key"] not in shown][:14]
    body, day = [], None
    for s in older:
        if s["date"][1] != day:
            day = s["date"][1]
            body.append('<P><B><FONT SIZE=4>%s</FONT> October %d</B>\n' % (DAYS[day], day))
        body.append('<LI><A HREF="%sarticle/%s.html">%s</A> (%d)\n' % (prefix, s["key"], esc(s["title"]), s["total"]))
    body.append('<P ALIGN=RIGHT><BR><B><A HREF="%solder.html">Older Articles</A></B><BR><B><A HREF="%syesterday.html">Yesterday\'s Edition</A></B>' % (prefix, prefix))
    out.append(box("Older Stuff", "".join(body)))
    rv = by_key["regexbook"]
    out.append(box("Book Reviews", '<P>Can a book teach regular expressions to humans? We read <CITE><A HREF="%sarticle/regexbook.html">Regular Expressions for Irregular People</A></CITE> to find out.'
                   '<P>Coming soon: a review of <CITE>Debugging the Year 2000</CITE>, which is either a technical manual or a horror novel.'
                   '<P>Visit our <A HREF="%sbooks.html">Book Reviews Section</A> for more.' % (prefix, prefix), prefix + "books.html"))
    ql = []
    for item in data.QUICK_LINKS:
        if item[1] is None:
            ql.append('<P><B>%s</B>' % item[0])
        else:
            href = item[1]
            href = fix_ring(href, prefix) if href.startswith("@") else prefix + href
            ql.append('<LI><A HREF="%s">%s</A> %s' % (href, esc(item[0]), esc(item[2])))
    out.append(box("Quick Links", "\n".join(ql)))
    fb = "".join('<LI><A HREF="%sfreshbeat.html">%s</A>\n' % (prefix, esc(x)) for x in data.FRESHBEAT)
    out.append(box("Freshbeat", '<P><FONT SIZE=4 COLOR="#006666"><B>October</B></FONT><BR>\n' + fb +
                   '<P ALIGN=RIGHT><B><A HREF="%sfreshbeat.html">More Beat...</A></B>' % prefix, prefix + "freshbeat.html"))
    ask = [s for s in STORIES if s["section"] == "askdashdot"]
    out.append(box("Ask Dashdot", "".join('<LI><A HREF="%sarticle/%s.html">%s</A>\n' % (prefix, s["key"], esc(s["title"].replace("Ask Dashdot: ", ""))) for s in ask) +
                   '<P>If you have a question for Ask Dashdot, <A HREF="%ssubmit.html">submit it</A>.' % prefix, prefix + "askdashdot.html"))
    out.append('</TD>\n')
    return "".join(out)

def footer(prefix, n=0):
    fortune = FORTUNES[n % len(FORTUNES)]
    links = " | ".join('<A HREF="%s%s">%s</A>' % (prefix, h, l) for l, h in
                       [("home", "index.html"), ("awards", "awards.html"), ("supporters", "supporters.html"),
                        ("grits' homepage", "grits.html"), ("contribute story", "submit.html"), ("older articles", "older.html"),
                        ("overandover.net", "overandover.html"), ("advertising", "advertising.html"), ("past polls", "polls.html"),
                        ("topics", "topics.html"), ("about", "about.html"), ("jobs", "jobs.html"), ("hof", "hof.html")])
    return ('<TABLE BGCOLOR="#FFFFFF" WIDTH="99%%" ALIGN=CENTER BORDER=0 CELLPADDING=4 CELLSPACING=0><TR><TD>\n'
            '<TABLE WIDTH="100%%" BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD BGCOLOR="#006666"><IMG SRC="%simages/pix.gif" WIDTH=1 HEIGHT=4 ALT=""></TD></TR></TABLE>\n'
            '<CENTER><FORM ACTION="%ssearch.html" METHOD="get"><FONT FACE="arial,helvetica" SIZE=2>'
            '<INPUT TYPE="text" NAME="query" SIZE=20> <INPUT TYPE="submit" VALUE="Search"></FONT></FORM>\n'
            '<FONT FACE="arial,helvetica" SIZE=2><I>%s</I></FONT><P>\n'
            '<FONT FACE="arial,helvetica" SIZE=1>[ %s ]</FONT><P>\n'
            '<FONT FACE="arial,helvetica" SIZE=1>Trademarks belong to whoever trademarked them. Comments belong to whoever typed them. '
            'Everything else &copy; 1997-99 Overandover.net. Dashdot is served hot by KoldFusion 4.5 from Gibson Mainframe Co.</FONT><BR>\n'
            '<A HREF="%sabout.html"><IMG SRC="%simages/powered_by_kf.gif" WIDTH=88 HEIGHT=31 BORDER=0 ALT="Powered by KoldFusion" VSPACE=6></A>\n'
            '</CENTER></TD></TR></TABLE>\n%s</BODY></HTML>\n'
            % (prefix, prefix, esc(fortune), links, prefix, prefix, webring(prefix)))

def webring(prefix):
    i = RING.index(ME)
    prev, nxt = RING[i - 1], RING[(i + 1) % len(RING)]
    return ('<P><CENTER>\n<TABLE BORDER=2 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#C0C0C0"><TR><TD ALIGN=CENTER>\n'
            '<FONT FACE="Arial, Helvetica" SIZE=1>\n'
            '<A HREF="%s">&lt;&lt; Prev</A> |\n'
            '<A HREF="%s../../web1999/index.html" onClick="return ringRandom(\'%s\')">Random</A> |\n'
            '<B><A HREF="%s../../web1999/index.html">The 1999 Web Ring</A></B> &middot; Dashdot is site %d of %d |\n'
            '<A HREF="%s">Next &gt;&gt;</A>\n</FONT></TD></TR></TABLE>\n</CENTER><P>\n'
            % (ring_url(prev, prefix), prefix, prefix, prefix, i + 1, len(RING), ring_url(nxt, prefix)))

def three_column(title, prefix, center, n=0, topics=None, stories_on_page=(), extra_js="", onload=""):
    return (page_head(title, prefix, extra_js, onload) + header(prefix, topics, n) +
            '<TABLE WIDTH="99%" ALIGN=CENTER CELLPADDING=0 CELLSPACING=0 BORDER=0 BGCOLOR="#FFFFFF"><TR>\n' +
            left_column(prefix) + '<TD VALIGN=TOP ALIGN=LEFT><FONT FACE="arial,helvetica" COLOR="#000000">\n' + center +
            '</FONT></TD>\n' + right_column(prefix, stories_on_page) + '</TR></TABLE>\n' + footer(prefix, n))

def one_column(title, prefix, center, n=0, topics=None, extra_js="", onload=""):
    """Story pages and utility pages: no side boxes, like the real thing."""
    return (page_head(title, prefix, extra_js, onload) + header(prefix, topics, n) +
            '<TABLE WIDTH="99%" ALIGN=CENTER CELLPADDING=8 CELLSPACING=0 BORDER=0 BGCOLOR="#FFFFFF"><TR>\n'
            '<TD VALIGN=TOP><FONT FACE="arial,helvetica" COLOR="#000000">\n' + center +
            '</FONT></TD></TR></TABLE>\n' + footer(prefix, n))

def title_bar(text, size=4):
    return ('<TABLE WIDTH="99%%" CELLPADDING=0 CELLSPACING=0 BORDER=0><TR><TD VALIGN=TOP BGCOLOR="#006666">'
            '<IMG SRC="@P@images/slc.gif" WIDTH=13 HEIGHT=16 ALT="" ALIGN=TOP><FONT SIZE=%d COLOR="#FFFFFF" FACE="arial,helvetica">'
            '<B>%s</B></FONT></TD></TR></TABLE>\n' % (size, text))

def bar(text, prefix, size=4):
    return title_bar(text, size).replace("@P@", prefix)

def write(rel, content):
    path = os.path.join(SITE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="latin-1", errors="xmlcharrefreplace") as f:
        f.write(content)
    WRITTEN.append(rel)

WRITTEN = []

# ------------------------------------------------------------------ story blocks
def story_intro(s, prefix):
    sub = s["submitter"]
    out = []
    if sub == s["editor"]:
        out.append(fix_ring(s["intro"], prefix))
    else:
        out.append('%s writes <I>%s</I>' % (user_link(sub, prefix), fix_ring(s["intro"], prefix)))
    if s.get("editor_note"):
        out.append(" " + fix_ring(s["editor_note"], prefix))
    return "".join(out)

def story_block(s, prefix, full=False):
    tid, label, img = TOPIC[s["topic"]]
    out = [bar(esc(s["full_title"]), prefix)]
    out.append('<A HREF="%stopic_%s.html"><IMG SRC="%simages/%s" BORDER=0 ALIGN=RIGHT HSPACE=20 VSPACE=10 ALT="%s"></A>\n'
               % (prefix, tid, prefix, img, esc(label)))
    out.append('<B>Posted by %s on %s</B><BR>\n<FONT SIZE=2><B>from the %s dept.</B></FONT><BR>\n'
               % (user_link(s["editor"], prefix), fmt_date(s["date"]), esc(s["dept_line"])))
    out.append(story_intro(s, prefix))
    if full:
        if s.get("more"):
            out.append("<P>" + fix_ring(s["more"], prefix))
        out.append('<BR CLEAR=ALL>\n')
    else:
        art = "%sarticle/%s.html" % (prefix, s["key"])
        words = len(re.sub("<[^>]+>", "", s.get("more", "")).split())
        more_bits = ' | <B>%d bytes in body</B>' % (len(s["more"])) if s.get("more") else ""
        out.append('<P><B>( </B><A HREF="%s"><B>Read More...</B></A> | <B><A HREF="%s">%d</A> of <A HREF="%sarticle/%s">%d</A> </B>comments%s <B>)</B>\n<P>\n'
                   % (art, art, s["at"][1], prefix, tfile(s["key"], -1), s["total"], more_bits))
    return "".join(out)

# ------------------------------------------------------------------ front pages
def front(rel, stories, n, label=""):
    center = []
    if label:
        center.append('<FONT SIZE=2><B>%s</B></FONT><P>\n' % label)
    for s in stories:
        center.append(story_block(s, ""))
    if rel == "index.html":
        center.append('<P ALIGN=RIGHT><FONT SIZE=2><B><A HREF="yesterday.html">Yesterday\'s Edition</A> | <A HREF="older.html">Older Articles</A></B></FONT>\n')
    else:
        center.append('<P ALIGN=RIGHT><FONT SIZE=2><B><A HREF="index.html">Today\'s Edition</A> | <A HREF="older.html">Older Articles</A></B></FONT>\n')
    write(rel, three_column("Dashdot: News for Nerds. Stuff that Matters.", "", "".join(center), n, stories_on_page=stories))

# ------------------------------------------------------------------ comments rendering
def render_comment(s, c, prefix, t):
    nick = c["nick"]
    if nick == "Anonymous Coward":
        by = "Anonymous Coward"
        info = ""
    else:
        by = user_link(nick, prefix)
        info = '<BR>(<A HREF="%susers/%s.html">User Info</A>)' % (prefix, slug(nick))
    sc_static = "(Score:%d%s)" % (c["score"], (", " + c["reason"]) if c["reason"] else "")
    parent = (' | <A HREF="#%d">Parent</A>' % c["pid"]) if c["pid"] else ""
    body = esc(c["body"]).replace("\n", "<BR>")
    return ('<A NAME="%d"></A><TABLE WIDTH="100%%" BORDER=0 CELLPADDING=3 CELLSPACING=0>'
            '<TR><TD BGCOLOR="#CCCCCC"><FONT FACE="arial,helvetica" SIZE=3 COLOR="#000000"><B>%s</B></FONT> '
            '<FONT FACE="arial,helvetica" SIZE=2><SCRIPT LANGUAGE="JavaScript">S(%d,%d,"%s")</SCRIPT><NOSCRIPT>%s</NOSCRIPT><BR>'
            'by %s on %s (<A HREF="#%d">#%d</A>)%s</FONT></TD></TR>\n'
            '<TR><TD><FONT FACE="arial,helvetica" SIZE=2>%s</FONT></TD></TR>\n'
            '<TR><TD><FONT FACE="arial,helvetica" SIZE=2>[ <A HREF="%sreply.html?sid=%s&amp;pid=%d">Reply to This</A>%s'
            '<SCRIPT LANGUAGE="JavaScript">M(%d)</SCRIPT> ]</FONT></TD></TR></TABLE>\n'
            % (c["cid"], esc(c["subject"]), c["cid"], c["score"], c["reason"], sc_static, by, fmt_date(c["date"]),
               c["cid"], c["cid"], info, body, prefix, s["key"], c["cid"], parent, c["cid"]))

def visible_below(c, t):
    return c["score"] >= t or any(visible_below(k, t) for k in c["children"])

def render_tree(s, c, prefix, t, out):
    if c["score"] >= t:
        out.append(render_comment(s, c, prefix, t))
    elif visible_below(c, t):
        out.append('<LI><FONT SIZE=2><A HREF="%s#%d">%s</A> by %s (Score:%d)</FONT>\n'
                   % (tfile(s["key"], -1), c["cid"], esc(c["subject"]), esc(c["nick"]), c["score"]))
    else:
        return
    kids = [k for k in c["children"] if visible_below(k, t)]
    if kids:
        out.append('<UL>\n')
        for k in kids:
            render_tree(s, k, prefix, t, out)
        out.append('</UL>\n')

def article(s, t, n):
    prefix = "../"
    out = []
    out.append(story_block(s, prefix, full=True))
    out.append('<P>')
    # comment control panel
    opts = "".join('<OPTION VALUE="%d"%s>%d: %d comments\n' % (x, " SELECTED" if x == t else "", x, s["at"][x]) for x in THRESHOLDS)
    out.append('<TABLE WIDTH="100%%" BORDER=0 CELLSPACING=0 CELLPADDING=0>\n<TR><TD BGCOLOR="#006666" ALIGN=CENTER>'
               '<FONT SIZE=2 COLOR="#FFFFFF"><B>%s</B> | <A HREF="../users.html"><FONT COLOR="#FFFFFF">Login/Create an Account</FONT></A> | '
               '<A HREF="#top"><FONT COLOR="#FFFFFF">Top</FONT></A> | <B>%d</B> comments | '
               '<A HREF="../search.html?query=%s"><FONT COLOR="#FFFFFF">Search Discussion</FONT></A></FONT></TD></TR>\n'
               '<TR><TD BGCOLOR="#CCCCCC" ALIGN=CENTER><FORM NAME="ctl" onSubmit="return changeT(this)"><FONT SIZE=2>\n'
               'Threshold: <SELECT NAME="threshold">%s</SELECT>\n'
               '<SELECT NAME="mode"><OPTION VALUE="nested" SELECTED>Nested<OPTION VALUE="flat">Flat<OPTION VALUE="thread">Threaded<OPTION VALUE="nocomment">No Comments</SELECT>\n'
               '<SELECT NAME="order"><OPTION VALUE="0" SELECTED>Oldest First<OPTION VALUE="1">Newest First<OPTION VALUE="2">Highest Scores First</SELECT>\n'
               '<INPUT TYPE="submit" VALUE="Change"> <INPUT TYPE="button" VALUE="Reply" onClick="location.href=\'../reply.html?sid=%s\'">\n'
               '</FONT></FORM></TD></TR>\n'
               '<TR><TD BGCOLOR="#006666" ALIGN=CENTER><FONT SIZE=2 COLOR="#FFFFFF">The fine print: the following comments belong to whoever typed them. '
               'Dashdot takes no responsibility for them, and frankly, neither do most of the people who typed them.</FONT></TD></TR></TABLE><P>\n'
               % (esc(s["full_title"]), s["total"], s["key"], opts, s["key"]))
    # comments
    out.append('<FORM NAME="mod" onSubmit="return false">\n<UL>\n')
    tops = [c for c in s["comment_list"] if c["pid"] == 0]
    hidden = s["total"] - s["at"][t]
    body = []
    for c in tops:
        if visible_below(c, t):
            render_tree(s, c, prefix, t, body)
            body.append('<P>\n')
    out.append("".join(body))
    out.append('</UL>\n')
    if hidden:
        out.append('<P><FONT SIZE=2><B>%d</B> repl%s beneath your current threshold. '
                   '<A HREF="%s">Show them all</A> (threshold -1).</FONT>\n'
                   % (hidden, "y" if hidden == 1 else "ies", tfile(s["key"], -1)))
    out.append('<SCRIPT LANGUAGE="JavaScript"><!--\nmine();\nmodButton();\n//--></SCRIPT>\n</FORM>\n')
    js = JS_ARTICLE + ('\nvar SID = "%s"; var ROOT = "../";\n' % s["key"]) + r"""
function changeT(f) {
  var t = f.threshold.options[f.threshold.selectedIndex].value;
  var m = f.mode.options[f.mode.selectedIndex].value;
  var o = f.order.options[f.order.selectedIndex].value;
  if (m == "flat" || m == "thread") alert("Flat and Threaded modes are coming in Dash 0.4. Until then, enjoy Nested.");
  if (m == "nocomment") { location.href = "../index.html"; return false; }
  if (o != "0") alert("Sorting is handled by a cron job that is currently on fire. Showing oldest first.");
  location.href = SID + (t == "1" ? "" : "_t" + (t == "-1" ? "m1" : t)) + ".html";
  return false;
}
"""
    if t == 1:
        js += r"""
var pt = getCookie("dd_thresh");
if (pt != "" && pt != "1" && location.search.indexOf("posted") < 0) {
  location.replace(SID + "_t" + (pt == "-1" ? "m1" : pt) + ".html" + location.hash);
}
"""
    topics = []
    title = "Dashdot | %s" % s["full_title"]
    write("article/" + tfile(s["key"], t), one_column(title, prefix, '<A NAME="top"></A>' + "".join(out), n, topics, js))

# ------------------------------------------------------------------ simple pages
def simple(rel, title, heading, body, n=0, js="", onload=""):
    depth = rel.count("/")
    prefix = "../" * depth
    content = bar(heading, prefix) + '<P>' + body.replace("@P@", prefix)
    write(rel, one_column("Dashdot | " + title, prefix, content, n, None, js, onload))

def listing(s, prefix=""):
    return ('<LI><A HREF="%sarticle/%s.html"><B>%s</B></A> <FONT SIZE=2>(%s, %d comments) posted by %s</FONT>\n'
            % (prefix, s["key"], esc(s["full_title"]), short_date(s["date"]), s["total"], esc(s["editor"])))

def build():
    # wipe previously generated html (keep images/ and tools/)
    for p in glob.glob(os.path.join(SITE, "*.html")) + glob.glob(os.path.join(SITE, "article", "*.html")) + \
             glob.glob(os.path.join(SITE, "users", "*.html")):
        os.remove(p)

    front("index.html", STORIES[:FRONT_COUNT], 0)
    front("yesterday.html", STORIES[FRONT_COUNT:FRONT_COUNT + 14], 3, "Yesterday's Edition")

    for i, s in enumerate(STORIES):
        for t in THRESHOLDS:
            article(s, t, i)

    # sections
    for k, (sec_id, fname, label, blurb) in enumerate(data.SECTIONS):
        ss = [s for s in STORIES if s["section"] == sec_id]
        center = '<FONT SIZE=2><B>%s:</B> %s</FONT><P>\n' % (esc(label), esc(blurb))
        center += "".join(story_block(s, "") for s in ss) or "<P>Nothing here yet. Submit something!"
        write(fname + ".html", three_column("Dashdot | " + label, "", center, k + 5, stories_on_page=ss))

    # topics
    cells = []
    for i, (tid, label, img) in enumerate(data.TOPICS):
        cnt = sum(1 for s in STORIES if s["topic"] == tid)
        cells.append('<TD ALIGN=CENTER VALIGN=BOTTOM WIDTH="20%%"><A HREF="topic_%s.html"><IMG SRC="images/%s" BORDER=0 ALT="%s"></A>'
                     '<BR><FONT SIZE=2><A HREF="topic_%s.html">%s</A> (%d)</FONT></TD>' % (tid, img, esc(label), tid, esc(label), cnt))
    rows = "".join("<TR>" + "".join(cells[i:i + 5]) + "</TR>\n" for i in range(0, len(cells), 5))
    simple("topics.html", "Topics", "Current Topics",
           '<FONT SIZE=2>Click an icon to see every story filed under it. Icons drawn by a volunteer with a mouse and a lot of free time.</FONT><P>'
           '<TABLE WIDTH="100%%" BORDER=0 CELLPADDING=8>%s</TABLE>' % rows, 2)
    for i, (tid, label, img) in enumerate(data.TOPICS):
        ss = [s for s in STORIES if s["topic"] == tid]
        body = '<IMG SRC="@P@images/%s" ALIGN=RIGHT ALT="%s">' % (img, esc(label))
        body += ("<UL>" + "".join(listing(s) for s in ss) + "</UL>") if ss else \
                "<P>No stories under this topic this week. The topic is lonely. Submit something!"
        body += '<P><A HREF="topics.html">All topics</A>'
        simple("topic_%s.html" % tid, label, "Topic: " + esc(label), body, i, )

    # older articles
    body, day = [], None
    for s in STORIES:
        if s["date"][1] != day:
            if day is not None:
                body.append("</UL>")
            day = s["date"][1]
            body.append('<P><B><FONT SIZE=4>%s</FONT> October %d, 1999</B><UL>' % (DAYS[day], day))
        body.append(listing(s))
    body.append("</UL>")
    simple("older.html", "Older Articles", "Older Articles", "".join(body), 4)

    build_users()
    build_polls()
    build_misc()
    build_search()

def build_users():
    users = sorted(USERS.values(), key=lambda u: u["uid"])
    for i, u in enumerate(users):
        cs = u["comments"]
        karma = "Positive" if u["karma"] > 5 else ("Neutral" if u["karma"] >= 0 else "Bad")
        rows = "".join('<LI><A HREF="../article/%s.html#%d">%s</A> <FONT SIZE=2>(Score:%d) attached to <A HREF="../article/%s.html">%s</A> '
                       'posted on %s</FONT>\n' % (s["key"], c["cid"], esc(c["subject"]), c["score"], s["key"], esc(s["title"]), fmt_date(c["date"], False))
                       for s, c in sorted(cs, key=lambda x: minutes(x[1]["date"]), reverse=True)[:24])
        stories = [s for s in STORIES if s["editor"] == u["nick"] or s["submitter"] == u["nick"]]
        srows = "".join(listing(s, "../") for s in stories)
        body = ('<TABLE BORDER=0 CELLPADDING=3><TR><TD><FONT SIZE=2><B>User #</B></FONT></TD><TD><FONT SIZE=2>%d</FONT></TD></TR>'
                '<TR><TD><FONT SIZE=2><B>Karma</B></FONT></TD><TD><FONT SIZE=2>%s%s</FONT></TD></TR>'
                '<TR><TD VALIGN=TOP><FONT SIZE=2><B>Bio</B></FONT></TD><TD><FONT SIZE=2>%s</FONT></TD></TR></TABLE>'
                % (u["uid"], karma, " (Dashdot editor)" if u["editor"] else "", esc(u["bio"])))
        if stories:
            body += '<P><B>Stories %s posted or submitted:</B><UL>%s</UL>' % (esc(u["nick"]), srows)
        body += ('<P><B>%s has posted %d comment%s this week</B>%s<UL>%s</UL>'
                 % (esc(u["nick"]), len(cs), "" if len(cs) == 1 else "s", " (most recent 24 shown)" if len(cs) > 24 else "", rows or "<LI>None yet. Lurker!"))
        simple("users/%s.html" % slug(u["nick"]), "User Info for " + u["nick"], "User Info for %s (%d)" % (esc(u["nick"]), u["uid"]), body, i)
    # user list
    lst = "".join('<LI><A HREF="users/%s.html">%s</A> <FONT SIZE=2>(#%d, %d comments)</FONT>\n' % (slug(u["nick"]), esc(u["nick"]), u["uid"], len(u["comments"]))
                  for u in sorted(USERS.values(), key=lambda u: u["nick"].lower()))
    simple("users.html", "Users", "Login / Create an Account", r"""
<TABLE WIDTH="100%" BORDER=0 CELLPADDING=4><TR><TD VALIGN=TOP WIDTH="50%"><FONT SIZE=2>
<B>Existing users</B><P>
<SCRIPT LANGUAGE="JavaScript"><!--
loginBox("");
//--></SCRIPT>
<NOSCRIPT>Logging in needs JavaScript. It's 1999; turn it on.</NOSCRIPT>
</FONT></TD><TD VALIGN=TOP><FONT SIZE=2>
<B>New users</B><P>
<FORM NAME="newuser" ACTION="newuser.html" METHOD="get" onSubmit="return newUser(this)">
Nickname:<BR><INPUT TYPE="text" NAME="newnick" SIZE=20 MAXLENGTH=20><BR>
E-mail address:<BR><INPUT TYPE="text" NAME="email" SIZE=20><BR>
<FONT SIZE=1>(Your password will be mailed to this address. We promise not to sell it. Probably.)</FONT><BR>
<INPUT TYPE="submit" VALUE="Create Account">
</FORM></FONT></TD></TR></TABLE>
<P><B>Some of our regulars</B><UL>""" + lst + "</UL>", 1, js=r"""
function newUser(f) {
  if (f.newnick.value == "") { alert("Pick a nickname. 'Anonymous Coward' is taken."); return false; }
  if (f.newnick.value.toLowerCase().indexOf("anonymous") >= 0) { alert("Nice try."); return false; }
  if (f.email.value.indexOf("@") < 1) { alert("That doesn't look like an e-mail address."); return false; }
  setCookie("dd_user", f.newnick.value, 30);
  return true;
}
""")
    simple("newuser.html", "Account Created", "Account Created", r"""
<FONT SIZE=2>
<SCRIPT LANGUAGE="JavaScript"><!--
var n = qs("newnick");
document.write("<B>" + htmlEsc(n == "" ? "Mystery user" : n) + "</B>, your account has been created as user #" + (46000 + Math.floor(Math.random() * 900)) + ".");
//--></SCRIPT>
<P>Your password has been mailed to you. It will arrive shortly, give or take the mail queue, which is currently
about as long as the line for the new Pentode chips.
<P>You are now logged in on this computer. Your karma starts at zero, which makes you exactly as
respected as everyone else who just showed up. Go <A HREF="index.html">read some stories</A>, post something
insightful, and try not to post "first post".
</FONT>""", 2)

def build_polls():
    js_polls = []
    for pid, q, answers, ncom, date in data.POLLS:
        js_polls.append('POLLS["%s"] = new Array("%s", "%s", %d, %s);'
                        % (pid, q.replace('"', '\\"'), date, ncom,
                           ", ".join('"%s", %d' % (a.replace('"', '\\"'), v) for a, v in answers)))
    js = r"""
var POLLS = new Object();
""" + "\n".join(js_polls) + r"""
function showPoll(qid) {
  var p = POLLS[qid];
  if (!p) { qid = "%s"; p = POLLS[qid]; }
  var aid = qs("aid");
  var voted = getCookie("dd_voted_" + qid);
  if (aid != "") {
    if (voted == "") {
      setCookie("dd_voted_" + qid, aid, 365); voted = aid;
      document.write('<P><FONT SIZE=2 COLOR="#006666"><B>Your vote has been registered. Thanks!</B></FONT>');
    } else {
      document.write('<P><FONT SIZE=2 COLOR="#990000"><B>You\'ve already voted in this poll. Your vote has been counted once, which is plenty.</B></FONT>');
    }
  }
  var n = (p.length - 3) / 2, total = 0, i;
  for (i = 0; i < n; i++) total += p[4 + 2 * i] + ((voted == "" + (i + 1)) ? 1 : 0);
  document.write('<P><FONT SIZE=4><B>' + p[0] + '</B></FONT><BR><FONT SIZE=2>Poll started ' + p[1] + ', 1999</FONT><P>');
  document.write('<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=0>');
  for (i = 0; i < n; i++) {
    var v = p[4 + 2 * i] + ((voted == "" + (i + 1)) ? 1 : 0);
    var pct = Math.round(v * 1000 / total) / 10;
    var w = Math.round(v * 300 / total) + 1;
    document.write('<TR><TD ALIGN=RIGHT><FONT SIZE=2>' + p[3 + 2 * i] + (voted == "" + (i + 1) ? ' <B>(your vote)</B>' : '') + '</FONT>&nbsp;</TD>' +
      '<TD><IMG SRC="' + (voted == "" + (i + 1) ? "images/bar_mine.gif" : "images/bar.gif") + '" WIDTH=' + w + ' HEIGHT=12 ALT="">' +
      ' <FONT SIZE=2>' + v + ' / <I>' + pct + '%%</I></FONT></TD></TR>');
  }
  document.write('</TABLE><P><FONT SIZE=2><B>' + total + '</B> total votes. <B>' + p[2] + '</B> comments.</FONT>');
  if (voted == "") {
    document.write('<P><FORM ACTION="pollbooth.html" METHOD="get"><INPUT TYPE="hidden" NAME="qid" VALUE="' + qid + '"><FONT SIZE=2><B>Cast your vote:</B><BR>');
    for (i = 0; i < n; i++) document.write('<INPUT TYPE="radio" NAME="aid" VALUE="' + (i + 1) + '">' + p[3 + 2 * i] + '<BR>');
    document.write('<INPUT TYPE="submit" VALUE="Vote"></FONT></FORM>');
  }
  document.write('<P><FONT SIZE=1>Polls on Dashdot are not scientific. If you want scientific, try the <A HREF="article/emacsvi.html">vi vs. emacs</A> thread and see how far science gets you.</FONT>');
}
""" % data.POLLS[0][0]
    # static fallback
    pid, q, answers, ncom, date = data.POLLS[0]
    total = sum(v for _, v in answers)
    fb = "".join('<LI>%s: %d (%.1f%%)' % (esc(a), v, v * 100.0 / total) for a, v in answers)
    simple("pollbooth.html", "Poll Booth", "Dashdot Poll Booth",
           '<SCRIPT LANGUAGE="JavaScript"><!--\nshowPoll(qs("qid"));\n//--></SCRIPT>\n'
           '<NOSCRIPT><B>%s</B><UL>%s</UL></NOSCRIPT>\n<P><FONT SIZE=2>[ <A HREF="polls.html">Other Polls</A> ]</FONT>' % (esc(q), fb), 1, js=js)
    rows = "".join('<LI><A HREF="pollbooth.html?qid=%s"><B>%s</B></A> <FONT SIZE=2>(%s; %d votes, %d comments)</FONT>\n'
                   % (p, esc(q), d, sum(v for _, v in a), c) for p, q, a, c, d in data.POLLS)
    simple("polls.html", "Past Polls", "Past Polls",
           '<FONT SIZE=2>Every Monday, a new question. Every Tuesday, 400 comments explaining why the answers were wrong.</FONT><UL>%s</UL>' % rows, 2)

def build_misc():
    pages = [
     ("faq.html", "FAQ", "Frequently Asked Questions", r"""
<FONT SIZE=2>
<P><B>What is Dashdot?</B><BR>Dashdot is news for nerds: a few stories a day about computers, science, the Internet and
whatever else our editors find interesting at 3am, followed by hundreds of comments from readers who disagree with them.
<P><B>Why is it called Dashdot?</B><BR>Say it out loud: dash, dot. In Morse code, dash-dot is the letter N. N is for News.
Also, the domain was available.
<P><B>How do stories get posted?</B><BR>Readers <A HREF="@P@submit.html">submit</A> them. Editors pick the ones that look
interesting, add a snarky remark, invent a department name, and hit the button. We get about 300 submissions a day. If
yours didn't run, don't take it personally. Unless it was about your own web site.
<P><B>What's a department?</B><BR>The little "from the something dept." line under each headline. It's a joke. It has
always been a joke. There is no actual department. We checked.
<P><B>What is moderation?</B><BR>Comments start with a score (0 for Anonymous Cowards, 1 for registered users, 2 for
users with good karma). Moderators, picked at random from regular readers, get five points to spend adding or subtracting
a point with a reason like Insightful, Funny, Troll or Offtopic. Readers set a threshold and only see comments at or
above it. In theory, the good stuff floats and the junk sinks. In practice, Funny floats highest of all.
<P><B>How do I become a moderator?</B><BR><A HREF="@P@users.html">Log in</A>. If the random number generator smiles on
you, you'll get points. Use them wisely, then go meta-moderate the other moderators on the
<A HREF="@P@metamod.html">meta-moderation</A> page.
<P><B>What's karma?</B><BR>A number that goes up when your comments are moderated up and down when they're moderated down.
It is not a measure of your worth as a person. It is, however, a measure of your worth as a Dashdot poster.
<P><B>What is a "Dashdot effect"?</B><BR>When we link to a small web site and fifty thousand nerds click on it in the same
ten minutes. Sorry about that. We recommend static HTML and a sturdy 486.
<P><B>Why does the site look like this?</B><BR>Because tables and FONT tags work in every browser, including the one
running on your toaster.
<P><B>Who runs this?</B><BR>See <A HREF="@P@about.html">about</A>. We're a handful of people, a rack of donated servers,
and a Perl script that's held together with hope.
</FONT>"""),
     ("about.html", "About", "About Dashdot", r"""
<FONT SIZE=2>
<P>Dashdot started in 1997 as a hobby page that CmdrGrits ran from his dorm room on a hand-me-down 486. It was a list of
links he thought were cool and a place for his friends to argue about them. Then the friends brought friends.
Then the friends' friends brought a T1.
<P>Today Dashdot is read by an estimated <B>200,000</B> people a day, most of whom should be working. We are part of
<A HREF="@P@overandover.html">Overandover.net</A>, which has very kindly let us keep doing exactly what we were doing
before, just with more servers.
<P><B>The crew</B><UL>
""" + "".join('<LI><A HREF="@P@users/%s.html"><B>%s</B></A> - %s\n' % (slug(k), k, esc(v)) for k, v in data.EDITORS.items()) + r"""
</UL>
<P><B>The hardware</B><BR>Four web servers, one database server, and a very tired load balancer, all running Linix. The
dynamic pages are served by KoldFusion 4.5 from Gibson Mainframe Co., and when that's busy, by plain old static HTML
that a cron job regenerates every few minutes.
<P><B>Contact</B><BR>Story submissions go through the <A HREF="@P@submit.html">submission form</A>. Everything else goes to
<A HREF="mailto:grits@dashdot.example">grits@dashdot.example</A>, where it will be read eventually, possibly in 2000.
</FONT>"""),
     ("code.html", "Dash Code", "The Dash Code", r"""
<FONT SIZE=2>
<P>The code that runs Dashdot is called <B>Dash</B>, and as of <A HREF="@P@article/slashcode.html">this week</A> it's
free software under the GPL.
<P><B>Current release:</B> Dash 0.3 (dash-0.3.tar.gz, 212K)<BR>
<B>Requirements:</B> Perl 5.005, a database, a web server, a cron daemon and a high tolerance for regular expressions.
<P><FORM><INPUT TYPE="button" VALUE="Download dash-0.3.tar.gz" onClick="alert('The tarball lives on our FTP server, which is a 486 in a closet. It is currently serving 1,914 people. Please try again in about 1999 minutes.')"></FORM>
<P><B>Known issues</B><UL>
<LI>The cron job that rebuilds the front page sometimes runs twice and produces two front pages. We call this a feature.
<LI>displayStory() is 900 lines long. Do not attempt to read it after midnight.
<LI>Moderation points occasionally go negative. We don't know what that means either.
<LI>Posting a comment titled "first post" is blocked by the lameness filter. This is not a bug.
</UL>
<P>Patches welcome. So are bug reports, as long as they aren't about the 900-line function. We know.
</FONT>"""),
     ("awards.html", "Awards", "Awards", r"""
<FONT SIZE=2>
<P>Dashdot has been honored with a number of awards, several of which we did not give ourselves:
<UL>
<LI><B>Best Site to Read Instead of Working, 1998</B> - Readers of a magazine we have since lost the name of.
<LI><B>Most Comments on a Story About a Refrigerator</B> - This week, <A HREF="@P@article/y2kfridge.html">probably</A>.
<LI><B>Webby-ish Award for Community</B> - Presented in a hotel ballroom by a man in a very shiny suit.
<LI><B>Golden Server Award</B> - For keeping a 486 running through three Dashdot effects. (Accepted on behalf of the Museum of Obsolete Calculators.)
<LI><B>Honorable Mention, Fewest Graphics</B> - The International Society for People on 14.4 Modems.
</UL>
<P>Want to give us an award? We accept trophies, plaques, T-shirts, and Jolt.
</FONT>"""),
     ("privacy.html", "Privacy", "Privacy Policy", r"""
<FONT SIZE=2>
<P><B>The short version:</B> we don't sell your information. We don't even know most of it.
<P><B>Cookies.</B> Dashdot uses a few cookies to remember your nickname, your comment threshold, how many moderator points
you have left and any comments you've posted. They live in your browser. We never see them. If you delete them we will
forget you completely, which some of you may consider a feature.
<P><B>Passwords.</B> The login box asks for a password because login boxes always do. This version of Dashdot doesn't
store it, check it, or send it anywhere. Please don't use your real password from somewhere else, here or anywhere else.
<P><B>Logs.</B> Our web servers keep access logs, which we use to find out which story crashed the database.
<P><B>Ads.</B> The banner at the top is served by us. It does not follow you around the web. It barely follows you down the page.
</FONT>"""),
     ("dashnet.html", "dashNET", "dashNET", r"""
<FONT SIZE=2>
<P><B>dashNET</B> is our IRC network, where Dashdot readers gather to discuss stories in real time, which is like
the comment section but faster and with fewer capital letters.
<P>Point your IRC client at <TT>irc.dashnet.example</TT>, port 6667, and join <TT>#dashdot</TT>. Popular channels:
<UL><LI><TT>#dashdot</TT> - general chat about the day's stories
<LI><TT>#y2k</TT> - countdown, bunker tips, bean recipes
<LI><TT>#linix-help</TT> - "how do I make my modem work" (answer: it's a Winmodem; it won't)
<LI><TT>#moderators</TT> - where people with points pretend they aren't bragging about it
</UL>
<P>Recent highlights from #dashdot:
<PRE>
[23:41] &lt;kernel_kid&gt; 2.3.22 is out
[23:41] &lt;Tux_Tamer&gt; compiling
[23:42] &lt;modem_mike&gt; downloading. see you thursday
[23:44] &lt;GrumpyGreybeard&gt; in my day we compiled kernels uphill both ways
[23:44] &lt;NullPointer&gt; segfault
[23:45] &lt;NullPointer&gt; nm, typo
</PRE>
</FONT>"""),
     ("grits.html", "CmdrGrits", "CmdrGrits' Page", r"""
<FONT SIZE=2>
<P>Hi. I'm CmdrGrits. I started this site. I'm sorry about the code.
<P><B>Things I like:</B> anime, pizza, Linix, giant robots, the smell of a new hard drive, and people who submit stories
with the link already in the right place.
<P><B>Things I don't like:</B> 'first post', the cron job that crashes on Tuesdays, and being woken up because a
server is on fire.
<P><B>Currently listening to:</B> whatever my roommate found on <A HREF="@P@../snapster/index.html">Snapster</A> last night.
<P><B>Currently reading:</B> <A HREF="@P@article/regexbook.html">Regular Expressions for Irregular People</A>. Hemlock made me.
<P><IMG SRC="@P@images/construction.gif" ALT="Under construction"> This page has been under construction since 1997.
</FONT>"""),
     ("preferences.html", "Preferences", "Preferences", r"""
<FONT SIZE=2>
<P>These preferences are stored in a cookie in your browser.
<FORM NAME="prefs" onSubmit="return savePrefs(this)">
<B>Default comment threshold:</B> <SELECT NAME="thresh">
<OPTION VALUE="-1">-1: show everything, even the trolls
<OPTION VALUE="0">0: include Anonymous Cowards
<OPTION VALUE="1" SELECTED>1: the default
<OPTION VALUE="2">2: only the moderated-up stuff
<OPTION VALUE="3">3: picky
<OPTION VALUE="4">4: very picky
<OPTION VALUE="5">5: only the absolute best (about four comments a week)
</SELECT><P>
<B>Slashboxes</B> (er, Dashboxes) to show: <INPUT TYPE="checkbox" CHECKED> Features <INPUT TYPE="checkbox" CHECKED> Poll
<INPUT TYPE="checkbox" CHECKED> Older Stuff <INPUT TYPE="checkbox" CHECKED> Freshbeat<BR>
<FONT SIZE=1>(Box preferences are coming in Dash 0.4. For now, you get all the boxes. Enjoy the boxes.)</FONT><P>
<INPUT TYPE="submit" VALUE="Save Preferences"> <INPUT TYPE="button" VALUE="Reset Everything" onClick="resetAll()">
</FORM>
<SCRIPT LANGUAGE="JavaScript"><!--
var t = getCookie("dd_thresh");
if (t != "") { var s = document.forms["prefs"].thresh; for (var i = 0; i < s.options.length; i++) if (s.options[i].value == t) s.selectedIndex = i; }
//--></SCRIPT>
</FONT>"""),
     ("submit.html", "Submit Story", "Submit a Story", r"""
<FONT SIZE=2>
<P>Got news for nerds? Tell us about it. Please include a link, a summary in your own words, and no more than three
exclamation points.
<FORM NAME="sub" ACTION="submitted.html" METHOD="get" onSubmit="return checkSub(this)">
<B>Your name:</B><BR><INPUT TYPE="text" NAME="from" SIZE=40><BR>
<B>Subject:</B><BR><INPUT TYPE="text" NAME="subj" SIZE=50><BR>
<B>Topic:</B><BR><SELECT NAME="topic">""" + "".join('<OPTION>%s' % esc(t[1]) for t in data.TOPICS) + r"""</SELECT><BR>
<B>The Scoop:</B><BR><TEXTAREA NAME="story" ROWS=10 COLS=55 WRAP=VIRTUAL></TEXTAREA><BR>
<INPUT TYPE="submit" VALUE="Submit">
</FORM>
</FONT>"""),
     ("submitted.html", "Thanks", "Submission Received", r"""
<FONT SIZE=2>
<SCRIPT LANGUAGE="JavaScript"><!--
var s = qs("subj");
document.write("<P>Thanks for submitting <B>" + htmlEsc(s == "" ? "your story" : s) + "</B>.");
document.write(" There are currently <B>" + (280 + Math.floor(Math.random() * 90)) + "</B> submissions in the queue ahead of it.");
//--></SCRIPT>
<P>An editor will look at it soon. If it runs, you'll see your name on the front page and your web server will
probably melt. If it doesn't, it may have been a duplicate, or it may have been about your own web site, or we may
just have been asleep.
<P><A HREF="index.html">Back to Dashdot</A>
</FONT>"""),
     ("advertising.html", "Advertising", "Advertise on Dashdot", r"""
<FONT SIZE=2>
<P>Reach <B>200,000</B> highly technical, highly opinionated, extremely ad-blind readers a day!
<P><B>Our audience:</B> system administrators, programmers, students, and people who will absolutely tell you what's wrong
with your product in a 600-word comment.
<P><B>Rates:</B> 468x60 banners, $35 CPM. Tasteful only. Blinking banners will be rejected and mocked.
<P>Our current advertiser is Gibson Mainframe Co., makers of <B>KoldFusion 4.5</B>, the application server with
"40% more &lt;CF&gt;." Their ad is at the top of every page. They paid for it, so please look at it for a moment.
<P><A HREF="@P@index.html"><IMG SRC="@P@images/banner_kf.gif" WIDTH=468 HEIGHT=60 BORDER=0 ALT="KoldFusion 4.5"></A>
</FONT>"""),
     ("supporters.html", "Supporters", "Our Supporters", r"""
<FONT SIZE=2>
<P>Dashdot would not be possible without the generosity of:
<UL>
<LI><B>Gibson Mainframe Co.</B> - for KoldFusion and for not asking too many questions about our traffic.
<LI><B>Overandover.net</B> - for the servers, the bandwidth, and the patience.
<LI><B>A large university's computer science department</B> - for the original 486, which we have not returned.
<LI><B>The Jolt delivery driver</B> - who has never once been late.
<LI><B>You</B> - for reading, posting, moderating, and for submitting the same story 40 times so we'd know it was important.
</UL>
</FONT>"""),
     ("jobs.html", "Jobs", "Jobs at Dashdot", r"""
<FONT SIZE=2>
<P>We're hiring! Now that we're part of a company that's about to have an IPO, we have something called a "budget."
<P><B>Perl Hacker</B> - Help us maintain the Dash code. Must be able to read a 900-line function without crying.
Crying afterward is fine.
<P><B>System Administrator</B> - Keep the servers up during Dashdot effects. Pager provided. Sleep not provided.
<P><B>Story Editor</B> - Read 300 submissions a day. Pick ten. Invent department names. Must have strong opinions about
vi and emacs (either is fine, as long as it's strong).
<P>Send your resume as plain ASCII text to <A HREF="mailto:jobs@dashdot.example">jobs@dashdot.example</A>. Word documents
will be read with a hex editor.
</FONT>"""),
     ("hof.html", "Hall of Fame", "Hall of Fame", None),
     ("overandover.html", "Overandover.net", "Overandover.net", r"""
<FONT SIZE=2>
<P><B>Overandover.net</B> is a network of web sites for people who build, run and break computers. We own Dashdot,
a software archive, a hardware review site, and a mailing-list archive with nine million messages, four million of
which are "me too."
<P>Overandover.net has filed for an initial public offering. Due to the quiet period, this page has nothing more to say,
quietly.
<P>Friends of the network: <A HREF="@P@../snapster/index.html">Snapster</A>, <A HREF="@P@../cnm/index.html">CNM Interactive</A>,
<A HREF="@P@../geohoods/index.html">GeoHoods</A>, <A HREF="@P@../yowza/index.html">Yowza!</A>
</FONT>"""),
     ("shirts.html", "T-shirts", "Dashdot T-shirts", r"""
<FONT SIZE=2>
<IMG SRC="@P@images/shirt.gif" WIDTH=160 HEIGHT=150 ALIGN=RIGHT ALT="Dashdot T-shirt">
<P>Clothe yourself in Dashdot! Our classic black T-shirt features the Dashdot logo on the front and, on the back, the
words <I>"I read the article"</I> (a bold claim).
<P>Sizes: L, XL, XXL, XXXL. We don't make S or M. We know our audience.
<P>Price: $15 plus shipping.
<FORM><INPUT TYPE="button" VALUE="Order One" onClick="alert('Our online store is being built by a startup that went public last week. It has a sock puppet. It does not have an order form yet. Check back after the holidays!')"></FORM>
</FONT>"""),
     ("freshbeat.html", "Freshbeat", "Freshbeat", r"""
<FONT SIZE=2>
<P><B>Freshbeat</B> is our sister site's index of new free software releases, updated many times a day by maintainers who
really should be sleeping. Today's releases:
<UL>""" + "".join('<LI><B>%s</B> - %s\n' % (esc(n), esc(d)) for n, d in zip(data.FRESHBEAT, [
    "Sorts your mail into folders by regular expression. Now with fewer false positives.",
    "Makes it snow on your X desktop. Seasonally appropriate.",
    "A system monitor with more graphs than you have system.",
    "Fetches mail from POP servers. Faster than walking to the server.",
    "A terminal emulator that also browns bread. (Requires toaster with serial port.)",
    "A client library for reading Dashdot. API is unstable, like the site.",
    "Scans your binaries for two-digit years. Finds them. Prints a sad face.",
    "Plays MP3s in a terminal. Uses 2% CPU on a P166.",
    "A daemon that monitors your sock drawer. Inspired by a certain pet store.",
    "Inventory control for your Y2K bean supply."])) + r"""
</UL></FONT>"""),
     ("metamod.html", "Meta-Moderation", "Meta-Moderation", None),
     ("moderated.html", "Moderation Recorded", "Moderation Recorded", r"""
<FONT SIZE=2>
<SCRIPT LANGUAGE="JavaScript"><!--
var n = qs("n"), sid = qs("sid"), p = getCookie("dd_points");
document.write("<P>Thanks! <B>" + htmlEsc(n == "" ? "0" : n) + "</B> moderation(s) recorded.");
document.write(" You have <B>" + htmlEsc(p == "" ? "0" : p) + "</B> moderator point(s) left.");
if (sid != "") document.write(' <P><A HREF="article/' + escape(sid) + '.html">Back to the story</A> (your moderations show up in your browser right away).');
//--></SCRIPT>
<P>Your moderations will be reviewed by meta-moderators, who are people with even more free time than you. If they
find your moderations fair, your karma goes up. If they find them unfair, you'll never be a moderator again, or at
least not until next week.
<P><A HREF="index.html">Back to Dashdot</A>
</FONT>"""),
    ]
    js_prefs = r"""
function savePrefs(f) {
  var t = f.thresh.options[f.thresh.selectedIndex].value;
  setCookie("dd_thresh", t, 365);
  alert("Preferences saved. Story pages will now open at threshold " + t + ".");
  return false;
}
function resetAll() {
  if (!confirm("Forget your nickname, threshold, moderator points and posted comments?")) return;
  var c = document.cookie.split("; ");
  for (var i = 0; i < c.length; i++) { var n = c[i].substring(0, c[i].indexOf("=")); if (n.indexOf("dd_") == 0) delCookie(n); }
  alert("Done. Dashdot has forgotten all about you.");
  location.reload();
}
"""
    js_sub = r"""
function checkSub(f) {
  if (f.subj.value == "") { alert("Your story needs a subject."); return false; }
  if (f.story.value.length < 20) { alert("That's a pretty short scoop. Tell us a little more."); return false; }
  var bangs = f.story.value.split("!").length - 1;
  if (bangs > 3) { alert("We counted " + bangs + " exclamation points. The limit is three!!!"); return false; }
  return true;
}
"""
    for i, (rel, title, heading, body) in enumerate(pages):
        if body is None:
            continue
        js = js_prefs if rel == "preferences.html" else (js_sub if rel == "submit.html" else "")
        simple(rel, title, heading, body, i, js)

    # hall of fame
    busiest = sorted(STORIES, key=lambda s: -s["total"])[:10]
    posters = sorted([u for u in USERS.values() if not u["editor"]], key=lambda u: -len(u["comments"]))[:10]
    eds = sorted(data.EDITORS.keys(), key=lambda e: -sum(1 for s in STORIES if s["editor"] == e))
    best = sorted([(s, c) for s in STORIES for c in s["comment_list"] if c["score"] == 5 and c["kind"] == "funny"],
                  key=lambda x: minutes(x[1]["date"]))[:8]
    body = ('<FONT SIZE=2><P><B>Most Active Stories</B><UL>%s</UL>'
            '<P><B>Most Active Posters</B> (registered users, this week)<UL>%s</UL>'
            '<P><B>Most Active Authors</B><UL>%s</UL>'
            '<P><B>Funniest Comments</B> (Score:5, Funny)<UL>%s</UL>'
            '<P><B>Most Active Poll</B><UL><LI><A HREF="pollbooth.html?qid=editor">%s</A> - and the comments are still coming.</UL></FONT>'
            % ("".join('<LI><A HREF="article/%s.html">%s</A> (%d comments)\n' % (s["key"], esc(s["title"]), s["total"]) for s in busiest),
               "".join('<LI><A HREF="users/%s.html">%s</A> (%d comments)\n' % (slug(u["nick"]), esc(u["nick"]), len(u["comments"])) for u in posters),
               "".join('<LI><A HREF="users/%s.html">%s</A> (%d stories)\n' % (slug(e), esc(e), sum(1 for s in STORIES if s["editor"] == e)) for e in eds),
               "".join('<LI><A HREF="article/%s.html#%d">%s</A> by %s, in <I>%s</I>\n' % (s["key"], c["cid"], esc(c["subject"]), esc(c["nick"]), esc(s["title"])) for s, c in best),
               esc(data.POLLS[1][1])))
    simple("hof.html", "Hall of Fame", "Hall of Fame", body, 9)

    # meta-moderation: pick 8 moderated comments
    rng = random.Random("metamod")
    pool = [(s, c) for s in STORIES for c in s["comment_list"] if c["reason"]]
    picks = rng.sample(pool, 8)
    rows = []
    for i, (s, c) in enumerate(picks):
        rows.append('<TR><TD VALIGN=TOP BGCOLOR="#CCCCCC"><FONT SIZE=2><B>%s</B><BR>moderated <B>%s</B></FONT></TD>'
                    '<TD VALIGN=TOP><FONT SIZE=2>%s<BR><A HREF="article/%s.html#%d">context</A></FONT></TD>'
                    '<TD VALIGN=TOP NOWRAP><FONT SIZE=2><INPUT TYPE="radio" NAME="mm%d" VALUE="1">Fair<BR>'
                    '<INPUT TYPE="radio" NAME="mm%d" VALUE="0" CHECKED>Unsure<BR><INPUT TYPE="radio" NAME="mm%d" VALUE="-1">Unfair</FONT></TD></TR>\n'
                    % (esc(c["subject"]), c["reason"], esc(c["body"]), s["key"], c["cid"], i, i, i))
    simple("metamod.html", "Meta-Moderation", "Meta-Moderation",
           '<FONT SIZE=2><P>Who watches the watchers? You do. Below are eight recent moderations. Tell us whether each one was fair.'
           '</FONT><FORM NAME="mm" onSubmit="return metaDone(this)"><TABLE BORDER=0 CELLPADDING=4 CELLSPACING=2>%s</TABLE>'
           '<INPUT TYPE="submit" VALUE="Meta-Moderate"></FORM>' % "".join(rows), 3, js=r"""
function metaDone(f) {
  var fair = 0, unfair = 0;
  for (var i = 0; i < f.elements.length; i++) {
    var e = f.elements[i];
    if (e.type == "radio" && e.checked) { if (e.value == "1") fair++; if (e.value == "-1") unfair++; }
  }
  alert("Thanks! You found " + fair + " moderation(s) fair and " + unfair + " unfair.\n\nThe moderators in question will be notified by a sternly worded cron job.");
  location.href = "index.html";
  return false;
}
""")

    # reply / post comment page
    titles = "\n".join('TITLES["%s"] = "%s";' % (s["key"], s["full_title"].replace('"', '\\"')) for s in STORIES)
    simple("reply.html", "Post Comment", "Post Comment", r"""
<FONT SIZE=2>
<SCRIPT LANGUAGE="JavaScript"><!--
var sid = qs("sid"), pid = qs("pid");
if (pid == "") pid = "0";
if (TITLES[sid]) {
  document.write('<P>Replying to <B><A HREF="article/' + sid + '.html">' + TITLES[sid] + '</A></B>');
  if (pid != "0") document.write(', comment <A HREF="article/' + sid + '.html#' + pid + '">#' + pid + '</A>');
  document.write('.');
} else {
  document.write('<P><B>No story selected.</B> Go to a story and click <B>Reply</B>. (Or <A HREF="index.html">start at the front page</A>.)');
}
var u = getCookie("dd_user");
//--></SCRIPT>
<FORM NAME="post" ACTION="reply.html" METHOD="get" onSubmit="return postIt(this)">
<SCRIPT LANGUAGE="JavaScript"><!--
document.write('<INPUT TYPE="hidden" NAME="sid" VALUE="' + htmlEsc(sid) + '"><INPUT TYPE="hidden" NAME="pid" VALUE="' + htmlEsc(pid) + '">');
document.write('<TABLE BORDER=0 CELLPADDING=3><TR><TD ALIGN=RIGHT><FONT SIZE=2><B>Name</B></FONT></TD><TD><FONT SIZE=2>');
if (u == "") document.write('Anonymous Coward [ <A HREF="users.html">Create an Account!</A> ]<INPUT TYPE="hidden" NAME="postanon" VALUE="1">');
else document.write('<B>' + htmlEsc(u) + '</B> [ <A HREF="javascript:ddLogout()">Log Out</A> ] <INPUT TYPE="checkbox" NAME="postanon"> Post Anonymously');
document.write('</FONT></TD></TR>');
//--></SCRIPT>
<TR><TD ALIGN=RIGHT><FONT SIZE=2><B>Subject</B></FONT></TD><TD><INPUT TYPE="text" NAME="postersubj" SIZE=50 MAXLENGTH=50></TD></TR>
<TR><TD ALIGN=RIGHT VALIGN=TOP><FONT SIZE=2><B>Comment</B></FONT></TD><TD><TEXTAREA NAME="postercomment" ROWS=10 COLS=50 WRAP=VIRTUAL></TEXTAREA><BR>
<FONT SIZE=1>Allowed HTML: &lt;B&gt; &lt;I&gt; &lt;P&gt; &lt;BR&gt; &lt;EM&gt; &lt;STRONG&gt; &lt;TT&gt; &lt;BLOCKQUOTE&gt;<BR>
(Use "HTML Formatted" for those. "Plain Old Text" escapes everything and keeps your line breaks.)</FONT></TD></TR>
<TR><TD></TD><TD><SELECT NAME="posttype"><OPTION VALUE="text" SELECTED>Plain Old Text<OPTION VALUE="html">HTML Formatted</SELECT>
<INPUT TYPE="button" VALUE="Preview" onClick="preview(this.form)"> <INPUT TYPE="submit" VALUE="Submit"></TD></TR>
</TABLE>
</FORM>
<P><FONT SIZE=1><B>House rules:</B> Stay near the topic, or at least within shouting distance of it. If someone already
made your point, moderate them up instead of making it again. Reply under the comment you're answering so the thread
makes sense to the next reader. Give your comment a subject a human could understand. Moderators may bury anything
nasty, off-topic or pointless, but nothing is ever deleted: set your threshold to -1 and you can read every last
word. And no "first post". Please. We're begging.</FONT>
</FONT>""", 5, js="\nvar TITLES = new Object();\n" + titles + "\n" + JS_REPLY)

def build_search():
    arr = []
    for s in STORIES:
        text = re.sub("<[^>]+>", " ", s["intro"] + " " + s.get("editor_note", "") + " " + s.get("more", ""))
        text = re.sub(r"\s+", " ", text).replace("\\", "").replace('"', "'")
        arr.append('S[S.length] = new Array("%s", "%s", "%s", "%s", %d, "%s");'
                   % (s["key"], s["full_title"].replace('"', "'"), s["editor"], fmt_date(s["date"], False), s["total"],
                      text[:600].replace("@RING", "")))
    js = "\nvar S = new Array();\n" + "\n".join(arr) + r"""
function doSearch() {
  var q = qs("query");
  document.forms["sf"].query.value = q;
  if (q == "") { document.write("<P>Enter some words above to search the last week of Dashdot stories."); return; }
  var words = q.toLowerCase().split(" "), hits = 0;
  document.write('<P>Results for <B>' + htmlEsc(q) + '</B>:<P>');
  for (var i = 0; i < S.length; i++) {
    var hay = (S[i][1] + " " + S[i][5]).toLowerCase(), ok = true;
    for (var j = 0; j < words.length; j++) { if (words[j] != "" && hay.indexOf(words[j]) < 0) ok = false; }
    if (ok) {
      hits++;
      document.write('<LI><A HREF="article/' + S[i][0] + '.html"><B>' + S[i][1] + '</B></A><BR><FONT SIZE=2>posted by ' + S[i][2] +
        ' on ' + S[i][3] + ' (' + S[i][4] + ' comments)<BR>' + S[i][5].substring(0, 160) + '...</FONT><P>');
    }
  }
  if (hits == 0) document.write("<P>No matches. Try fewer words, or different ones, or just go outside for a bit.");
  else document.write("<P><B>" + hits + "</B> stor" + (hits == 1 ? "y" : "ies") + " matched.");
}
"""
    simple("search.html", "Search", "Search Dashdot", r"""
<FORM NAME="sf" ACTION="search.html" METHOD="get"><FONT SIZE=2>
<INPUT TYPE="text" NAME="query" SIZE=30> <INPUT TYPE="submit" VALUE="Search"></FONT></FORM>
<FONT SIZE=2>
<SCRIPT LANGUAGE="JavaScript"><!--
doSearch();
//--></SCRIPT>
<NOSCRIPT>Searching needs JavaScript. Try the <A HREF="older.html">older articles</A> list instead.</NOSCRIPT>
</FONT>""", 6, js=js)

if __name__ == "__main__":
    build()
    print("wrote %d pages; %d stories, %d comments, %d users" %
          (len(WRITTEN), len(STORIES), sum(s["total"] for s in STORIES), len(USERS)))
