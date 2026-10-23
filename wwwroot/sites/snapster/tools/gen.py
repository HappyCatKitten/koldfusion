#!/usr/bin/env python3
"""Generates every Snapster page (static HTML with inline 1999-style JavaScript).

    python3 tools/gfx.py && python3 tools/gen.py      (from the site folder)

Only .html, .gif and .mid are published: the song catalog is written as an
inline JavaScript array into the pages that need it (search.html, transfer.html).
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import data  # noqa: E402
import midi  # noqa: E402

SITES = 'yowza altavisor askreeves orinoco ubid etoyz petz geohoods hamstershuffle dashdot snapster cnm'.split()
FONT = '<FONT FACE="Arial, Helvetica" SIZE=2>'
CAT = data.build_catalog()
ARTISTS = [b for b, g, s in data.BANDS]
UNAMES = [u for u, c, g in data.USERS]
CONN_OF = dict((u, c) for u, c, g in data.USERS)
HOT = [h[0] for h in data.HOTLIST]
PAGES = []


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def js(v):
    """a JS (ES3) literal; never lets '</' end the SCRIPT block"""
    return json.dumps(v).replace('</', '<\\/')


def commas(n):
    return '{:,}'.format(n)


def write(name, html):
    with open(os.path.join(SITE, name), 'w', encoding='latin-1') as f:
        f.write(html)
    PAGES.append(name)


def webring(title='Snapster'):
    i = SITES.index('snapster')
    prev, nxt = SITES[i - 1], SITES[(i + 1) % len(SITES)]
    lst = ', '.join('"../%s/index.html"' % s for s in SITES)
    return '''
<SCRIPT LANGUAGE="JavaScript1.2">
<!--
function ringRandom() {
  var list = new Array(%s);
  location.href = list[Math.floor(Math.random() * list.length)];
  return false;
}
// -->
</SCRIPT>
<P><CENTER><TABLE BORDER=2 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#C0C0C0"><TR><TD ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=1>
<A HREF="../%s/index.html"><FONT COLOR="#000080">&lt;&lt; Prev</FONT></A> <FONT COLOR="#000000">|</FONT> <A HREF="../../web1999/index.html" onClick="return ringRandom()"><FONT COLOR="#000080">Random</FONT></A> <FONT COLOR="#000000">|</FONT> <B><A HREF="../../web1999/index.html"><FONT COLOR="#000080">The 1999 Web Ring</FONT></A></B> <FONT COLOR="#000000">&middot; %s is site %d of 12 |</FONT> <A HREF="../%s/index.html"><FONT COLOR="#000080">Next &gt;&gt;</FONT></A>
</FONT></TD></TR></TABLE></CENTER>
''' % (lst, prev, title, i + 1, nxt)


# =====================================================================================
#                                     the web site
# =====================================================================================
LEFT = [('whatis', 'whatis.html'), ('download', 'download.html'), ('advertise', 'advertise.html'),
        ('company', 'company.html'), ('groundzero', 'groundzero.html'), ('artists', 'artists.html'),
        ('press', 'press.html'), ('legal', 'legal.html'), (None, None), ('help', 'help.html'),
        ('terms', 'terms.html')]

WEB_JS = '''<SCRIPT LANGUAGE="JavaScript">
<!--
var pre = new Array();
function preload() {
  if (!document.images) return;
  for (var i = 0; i < preload.arguments.length; i++) {
    pre[pre.length] = new Image();
    pre[pre.length - 1].src = preload.arguments[i];
  }
}
function sw(n, s) {
  if (document.images && document.images[n]) document.images[n].src = s;
}
// -->
</SCRIPT>'''


def web_page(fname, title, key, content, top=None, extra_head='', onload=''):
    def topbtn(k, href, w):
        cur = (top == k)
        img = 'images/btn_%s%s.gif' % (k, '_mo' if cur else '')
        tag = '<IMG SRC="%s" WIDTH=%d HEIGHT=23 NAME="t_%s" BORDER=0 ALT="%s">' % (img, w, k, k)
        if cur:
            return tag
        return ('<A HREF="%s" onMouseOver="sw(\'t_%s\',\'images/btn_%s_mo.gif\')" '
                'onMouseOut="sw(\'t_%s\',\'images/btn_%s.gif\')">%s</A>' % (href, k, k, k, k, tag))

    left = []
    for k, href in LEFT:
        if k is None:
            left.append('<TR><TD><IMG SRC="images/left_space.gif" WIDTH=133 HEIGHT=49></TD></TR>')
            continue
        if k == key:
            left.append('<TR><TD><A HREF="%s"><IMG SRC="images/left_%s_on.gif" WIDTH=133 HEIGHT=16 BORDER=0 '
                        'ALT="%s"></A></TD></TR>' % (href, k, k))
        else:
            left.append('<TR><TD><A HREF="%s" onMouseOver="sw(\'l_%s\',\'images/left_%s_on.gif\')" '
                        'onMouseOut="sw(\'l_%s\',\'images/left_%s.gif\')"><IMG SRC="images/left_%s.gif" '
                        'WIDTH=133 HEIGHT=16 NAME="l_%s" BORDER=0 ALT="%s"></A></TD></TR>'
                        % (href, k, k, k, k, k, k, k))
    preload = ', '.join("'images/left_%s_on.gif'" % k for k, h in LEFT if k) + \
        ", 'images/btn_whatis_mo.gif', 'images/btn_company_mo.gif', 'images/btn_home_mo.gif', " \
        "'images/btn_download_mo.gif'"
    html = '''<HTML>
<HEAD>
<TITLE>%(title)s</TITLE>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1">
%(webjs)s
%(extra_head)s
</HEAD>
<BODY BGCOLOR="#000000" BACKGROUND="images/bk.gif" TEXT="#000000" LINK="#000099" VLINK="#336699" ALINK="#FFCC00" onLoad="preload(%(preload)s)%(onload)s">
<TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0 WIDTH=566>
  <TR>
    <TD COLSPAN=2 BGCOLOR="#000000"><A HREF="index.html"><IMG SRC="images/logo.gif" WIDTH=273 HEIGHT=68 BORDER=0 ALT="Snapster"></A></TD>
    <TD BGCOLOR="#000000">&nbsp;</TD>
    <TD ROWSPAN=2 VALIGN=BOTTOM><IMG SRC="images/arrows.gif" WIDTH=174 HEIGHT=91 ALT=""></TD>
    <TD ROWSPAN=4 VALIGN=TOP><IMG SRC="images/head_curve.gif" WIDTH=12 HEIGHT=121 ALT=""></TD>
  </TR>
  <TR>
    <TD BGCOLOR="#666666">%(home)s</TD>
    <TD BGCOLOR="#666666">%(whatis)s</TD>
    <TD BGCOLOR="#666666">%(company)s</TD>
  </TR>
  <TR>
    <TD><IMG SRC="images/available.gif" WIDTH=150 HEIGHT=20 ALT="available music:"></TD>
    <TD COLSPAN=2>
      <TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0>
        <TR>
          <TD ROWSPAN=3><IMG SRC="images/num_left.gif" WIDTH=1 HEIGHT=20></TD>
          <TD><IMG SRC="images/num_top.gif" WIDTH=222 HEIGHT=3></TD>
          <TD ROWSPAN=3><IMG SRC="images/num_right.gif" WIDTH=7 HEIGHT=20></TD>
        </TR>
        <TR>
<!-- the "available music" counter -->
          <TD BGCOLOR="#99CCCC" NOWRAP><IMG SRC="images/clear.gif" WIDTH=5 HEIGHT=12>%(counter)s<IMG SRC="images/cnt_songs.gif" WIDTH=60 HEIGHT=12></TD>
        </TR>
        <TR>
          <TD><IMG SRC="images/num_bottom.gif" WIDTH=222 HEIGHT=5></TD>
        </TR>
      </TABLE>
    </TD>
    <TD BGCOLOR="#666666"><A HREF="download.html" onMouseOver="sw('dl','images/btn_download_mo.gif')" onMouseOut="sw('dl','images/btn_download.gif')"><IMG SRC="images/btn_download.gif" WIDTH=174 HEIGHT=20 NAME="dl" BORDER=0 ALT="Download"></A></TD>
  </TR>
  <TR>
    <TD COLSPAN=4><IMG SRC="images/cap.gif" WIDTH=554 HEIGHT=10></TD>
  </TR>
  <TR>
    <TD COLSPAN=4 VALIGN=TOP>
      <TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0 WIDTH=554>
        <TR>
          <TD VALIGN=TOP BGCOLOR="#999999" WIDTH=133>
            <TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0 BGCOLOR="#666666">
            %(left)s
            <TR><TD><IMG SRC="images/left_bottom.gif" WIDTH=133 HEIGHT=13></TD></TR>
            </TABLE>
            <IMG SRC="images/clear.gif" WIDTH=133 HEIGHT=8><BR>
            <CENTER><A HREF="groundzero.html#contest"><IMG SRC="images/sponsor.gif" WIDTH=120 HEIGHT=90 BORDER=0 ALT="RadioRhombus contest"></A></CENTER>
          </TD>
          <TD BGCOLOR="#777777" VALIGN=TOP WIDTH=1><IMG SRC="images/clear.gif" WIDTH=1 HEIGHT=1></TD>
          <TD BGCOLOR="#4F4F4F" VALIGN=TOP WIDTH=1><IMG SRC="images/clear.gif" WIDTH=1 HEIGHT=1></TD>
          <TD BGCOLOR="#CCCC99" VALIGN=TOP WIDTH=400>
            <IMG SRC="images/clear.gif" WIDTH=399 HEIGHT=2><BR>
            <TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0 WIDTH=398>
              <TR>
                <TD VALIGN=TOP><IMG SRC="images/clear.gif" WIDTH=15 HEIGHT=15></TD>
<!-- body text -->
                <TD VALIGN=TOP>
%(content)s
                </TD>
              </TR>
            </TABLE>
            <P>&nbsp;</P>
          </TD>
          <TD VALIGN=TOP WIDTH=19 BGCOLOR="#CCCC99"><IMG SRC="images/bodycurve.gif" WIDTH=20 HEIGHT=37></TD>
        </TR>
        <TR>
          <TD VALIGN=TOP BGCOLOR="#999999" WIDTH=133>&nbsp;</TD>
          <TD BGCOLOR="#777777" WIDTH=1><IMG SRC="images/clear.gif" WIDTH=1 HEIGHT=1></TD>
          <TD BGCOLOR="#4F4F4F" WIDTH=1><IMG SRC="images/clear.gif" WIDTH=1 HEIGHT=1></TD>
          <TD BGCOLOR="#CCCC99" WIDTH=400><CENTER><FONT SIZE="-2" FACE="Arial, Helvetica">Copyright 1999-2000 Snapster, Inc.<BR>All rights reserved. Snappy the Turtle is a registered turtle.</FONT><BR>&nbsp;</CENTER></TD>
          <TD WIDTH=19 BGCOLOR="#CCCC99">&nbsp;</TD>
        </TR>
      </TABLE>
    </TD>
  </TR>
  <TR>
    <TD COLSPAN=4><IMG SRC="images/bottom.gif" WIDTH=554 HEIGHT=20></TD>
    <TD>&nbsp;</TD>
  </TR>
</TABLE>
<TABLE BORDER=0 WIDTH=566><TR><TD ALIGN=CENTER>
<FONT FACE="Arial, Helvetica" SIZE=1 COLOR="#999999">
<A HREF="index.html"><FONT COLOR="#99CCCC">home</FONT></A> |
<A HREF="client.html"><FONT COLOR="#99CCCC">launch the web client</FONT></A> |
<A HREF="help.html"><FONT COLOR="#99CCCC">help</FONT></A> |
<A HREF="terms.html"><FONT COLOR="#99CCCC">terms of use</FONT></A> |
<A HREF="legal.html"><FONT COLOR="#99CCCC">copyright policy</FONT></A>
</FONT>
%(ring)s
<P><A HREF="../../web1999/index.html"><IMG SRC="images/powered_by_kf.gif" WIDTH=88 HEIGHT=31 BORDER=0 ALT="Powered by KoldFusion"></A>
</TD></TR></TABLE>
</BODY>
</HTML>
''' % dict(title=title, webjs=WEB_JS, extra_head=extra_head, preload=preload, onload=onload,
           home=topbtn('home', 'index.html', 150), whatis=topbtn('whatis', 'whatis.html', 143),
           company=topbtn('company', 'company.html', 87), counter=counter_imgs(data.TOTAL_SONGS),
           left='\n            '.join(left), content=content, ring=webring())
    write(fname, html)


def counter_imgs(n):
    out = []
    for i, ch in enumerate(commas(n)):
        nm = 'comma' if ch == ',' else ch
        w = 4 if ch == ',' else 8
        out.append('<IMG SRC="images/cnt_%s.gif" WIDTH=%d HEIGHT=12 NAME="k%d">' % (nm, w, i))
    return ''.join(out)


def p(text, size=2):
    return '<P><FONT FACE="Arial, Helvetica" SIZE=%d>%s</FONT></P>' % (size, text)


def hdr(key, alt):
    return '<P><IMG SRC="images/hdr_%s.gif" WIDTH=380 HEIGHT=34 ALT="%s"></P>' % (key, alt)


COUNTER_JS = '''<SCRIPT LANGUAGE="JavaScript">
<!--
var songs = %d;
function drawCount() {
  var s = "" + songs, out = "", i;
  for (i = 0; i < s.length; i++) {
    if (i > 0 && (s.length - i) %% 3 == 0) out += ",";
    out += s.charAt(i);
  }
  for (i = 0; i < out.length && i < 9; i++) {
    var c = out.charAt(i);
    if (document.images["k" + i]) document.images["k" + i].src = "images/cnt_" + (c == "," ? "comma" : c) + ".gif";
  }
}
function tick() {
  songs += Math.floor(Math.random() * 40) + 1;
  if (songs > 9999999) songs = 1000000;
  drawCount();
  setTimeout("tick()", 1700);
}
// -->
</SCRIPT>''' % data.TOTAL_SONGS


def build_web():
    # ---------------------------------------------------------------- index
    content = '''
                  <P><I><B><FONT FACE="Arial, Helvetica" SIZE=3>Snapster: music at modem speed.</FONT></B></I></P>
                  <P><FONT FACE="Arial, Helvetica" SIZE="+1"><A HREF="download.html"><B><I>Download Snapster 2.0 Beta 5!</I></B></A></FONT></P>
                  <CENTER><TABLE WIDTH=300 BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD>
                  <FONT FACE="Arial, Helvetica" SIZE=3><B>The band Shiny Metallic Things has sent us another very nice letter.
                  Our Legal Department (Gary) is reading it now. Click <A HREF="legal.html">here</A> for more information!</B></FONT>
                  <P><FONT FACE="Arial, Helvetica" SIZE=2><B>Got a Macintosh? A guy named Tosh is writing
                  <A HREF="download.html#mac">Snaptosh</A> in his garage. It's beige. Then it's blue. We'll let you know.</B></FONT>
                  </TD></TR></TABLE></CENTER>
                  <P><FONT FACE="Arial, Helvetica" SIZE=2>No time to install? Take the brand new
                  <A HREF="client.html"><B>Snapster Web Edition</B></A> for a spin right here in your browser
                  &#151; search, chat, Hot List and transfers, no download required. (Requires Netscape 3 or
                  Internet Explorer 4 and a positive attitude.)</FONT></P>
                  <P><FONT FACE="Arial, Helvetica" SIZE=2>Want to know more? Get the <A HREF="whatis.html">inside
                  scoop on the product</A> and its innovative turtle-powered technology, or
                  <A HREF="download.html">download Snapster</A> and see for yourself!</FONT></P>
                  <FONT FACE="Arial, Helvetica" SIZE=2>Snapster respects artists, especially the ones with lawyers.
                  Please read our <A HREF="legal.html">MP3 Copyright Policy</A> and <A HREF="terms.html">Terms of Use</A>.</FONT>
                  <P><TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 BGCOLOR="#BBBB88" WIDTH="100%"><TR><TD>
                  <FONT FACE="Arial, Helvetica" SIZE=1><B>SNAPSTER NEWS:</B>
                  <A HREF="press.html">Snapster passes 8,000 simultaneous users, and one simultaneous lawyer</A> &middot;
                  <A HREF="artists.html">New Artist Program now accepting demo tapes (MP3 only, please, not tapes)</A> &middot;
                  <A HREF="groundzero.html">ground zero: the swing revival refuses to end</A></FONT>
                  </TD></TR></TABLE>'''
    web_page('index.html', 'Snapster', None, content, top='home', extra_head=COUNTER_JS,
             onload='; drawCount(); setTimeout(\'tick()\', 1700)')

    # ---------------------------------------------------------------- what is
    content = hdr('whatis', 'What is Snapster?') + '''
                  <TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0><TR><TD VALIGN=TOP>
                  <FONT FACE="Arial, Helvetica" SIZE=2><B><I>Snapster is the world's leading
                  turtle-themed MP3 community.</I></B><P>
                  With Snapster you can search the hard drives of thousands of fellow music fans for the songs you
                  love, chat about them, add your new friends to a Hot List, and watch a little green progress
                  bar crawl across your screen like it has somewhere to be.</FONT></TD>
                  <TD VALIGN=TOP><IMG SRC="images/snappy_big.gif" WIDTH=160 HEIGHT=160 ALT="Snappy" HSPACE=6></TD></TR></TABLE>
                  ''' + p('<B>How does it work?</B><BR>When you sign on, Snapster tells our server which MP3s are in your '
                          'shared folder. When somebody searches, our server says "hey, that guy has it" and your '
                          'two computers talk directly, like two kids with tin cans and a very long string.') + '''
                  <CENTER><IMG SRC="images/screenshot.gif" WIDTH=220 HEIGHT=160 ALT="Snapster screenshot"><BR>
                  <FONT FACE="Arial, Helvetica" SIZE=1><I>Snapster 2.0 Beta 5 in action. Actual size may vary.</I></FONT></CENTER>
                  <P><FONT FACE="Arial, Helvetica" SIZE=2><B>Features</B></FONT>
                  <UL><FONT FACE="Arial, Helvetica" SIZE=2>
                  <LI><B>Search</B> by artist and title, then narrow it down by line speed, bitrate, frequency and ping.
                  <LI><B>Line speed dots:</B> green means fast, yellow means okay, red means you should go make a sandwich.
                  <LI><B>Chat</B> in dozens of channels, from #Ska to #Y2K (which is still going, somehow).
                  <LI><B>Hot List</B> your favorite users and get notified when they sign on.
                  <LI><B>Browse</B> another user's entire collection. Judge them silently.
                  <LI><B>Transfer</B> window with real-time "Remote user cancelled" technology.
                  </FONT></UL>
                  ''' + p('<B>System requirements:</B> Windows 95, 98 or NT 4.0; Pentium 90 or better; 16 MB RAM '
                          '(32 MB if you also want to run an MP3 player and a flying-toasters-style screensaver); a 28.8 modem or faster; '
                          'and patience. Lots of patience.') + p(
        '<A HREF="client.html"><B>Try the Web Edition now &gt;&gt;</B></A> &nbsp; or &nbsp; '
        '<A HREF="download.html"><B>Download &gt;&gt;</B></A>')
    web_page('whatis.html', 'What is Snapster?', 'whatis', content, top='whatis')

    # ---------------------------------------------------------------- download
    dl_js = '''<SCRIPT LANGUAGE="JavaScript">
<!--
var total = 1433, got = 0, busy = 0, waited = 0;
function pad2(n) { return (n < 10 ? "0" : "") + n; }
function startDl() {
  if (busy) { alert("Easy there, cowboy. One download at a time."); return false; }
  busy = 1; got = 0; waited = 0;
  sw("dlmsg", "images/clear.gif");
  document.dlg.file.value = "snapster20b5.exe from dl.snapster.com";
  setTimeout("stepDl()", 300);
  return false;
}
function stepDl() {
  var rate = 90 + Math.floor(Math.random() * 70);
  if (got >= total * 0.99 && waited < 8) {
    waited++;
    document.dlg.stat.value = "Saved: " + Math.floor(got) + " KB of " + total + " KB (the last 1% is the hardest)";
    setTimeout("stepDl()", 300);
    return;
  }
  got += rate / 4;
  if (got > total) got = total;
  var pct = Math.floor(got * 20 / total);
  sw("dlbar", "images/bar_" + pad2(pct) + ".gif");
  var left = Math.ceil((total - got) / rate);
  document.dlg.stat.value = "Saved: " + Math.floor(got) + " KB of " + total + " KB (" + rate + ".0 KB/s)";
  document.dlg.eta.value = "0:" + pad2(left) + " remaining";
  if (got < total) { setTimeout("stepDl()", 250); return; }
  document.dlg.eta.value = "Done.";
  sw("dlmsg", "images/punchline.gif");
  busy = 0;
  setTimeout("alert('Download complete!\\\\n\\\\nJust kidding: this is a parody site. Nothing was downloaded,\\\\nnothing was installed, and your hard drive is exactly as full as before.')", 400);
}
// -->
</SCRIPT>'''
    content = hdr('download', 'Download Snapster') + p(
        '<B><I>Snapster 2.0 Beta 5</I></B> for Windows 95/98/NT is here. It\'s free, it\'s small, and it '
        'is only a little bit beta.') + '''
                  <CENTER><A HREF="download.html" onClick="return startDl()" onMouseOver="sw('dn','images/download_now_mo.gif')" onMouseOut="sw('dn','images/download_now.gif')"><IMG SRC="images/download_now.gif" WIDTH=170 HEIGHT=44 BORDER=0 NAME="dn" ALT="Download Snapster NOW!"></A><BR>
                  <FONT FACE="Arial, Helvetica" SIZE=1>snapster20b5.exe &middot; 1.4 MB &middot; about 7 minutes at 28.8</FONT></CENTER>
                  <P><FORM NAME="dlg" onSubmit="return false">
                  <TABLE BORDER=2 CELLPADDING=4 CELLSPACING=0 BGCOLOR="#C0C0C0" WIDTH=360><TR><TD BGCOLOR="#000080"><FONT FACE="Arial, Helvetica" SIZE=2 COLOR="#FFFFFF"><B>File Download</B></FONT></TD></TR>
                  <TR><TD><FONT FACE="Arial, Helvetica" SIZE=1>
                  <INPUT TYPE=TEXT NAME="file" SIZE=40 VALUE="(click Download Snapster NOW! above)" onFocus="this.blur()"><BR>
                  <IMG SRC="images/bar_00.gif" WIDTH=100 HEIGHT=11 NAME="dlbar"><BR>
                  <INPUT TYPE=TEXT NAME="stat" SIZE=40 VALUE="Saved: 0 KB of 1433 KB" onFocus="this.blur()"><BR>
                  <INPUT TYPE=TEXT NAME="eta" SIZE=20 VALUE="Estimated time: who knows" onFocus="this.blur()">
                  <INPUT TYPE=BUTTON VALUE="Cancel" onClick="alert('You can\\'t cancel. We\\'re already best friends now.')">
                  </FONT></TD></TR></TABLE></FORM>
                  <IMG SRC="images/clear.gif" WIDTH=360 HEIGHT=40 NAME="dlmsg">
                  ''' + p('<B>Installing:</B> double-click <TT>snapster20b5.exe</TT>, click Next about eleven times, '
                          'choose your shared folder, tell us your line speed (honestly!), and you\'re in.') + p(
        '<B>What\'s new in Beta 5:</B><BR>&middot; Hot List remembers your friends even after a crash<BR>'
        '&middot; Search results now sorted by ping, so the fastest strangers come first<BR>'
        '&middot; Fixed a bug where the turtle icon would spin forever<BR>'
        '&middot; Added a bug where the turtle icon spins a little bit<BR>'
        '&middot; "Remote user cancelled" now 12% more polite') + '<A NAME="mac"></A>' + p(
        '<B>Macintosh:</B> Snaptosh is coming. A fellow named Tosh is writing it. In a garage. On a beige '
        'machine that he swears he will paint blue.<BR><B>Linux:</B> the source is in your heart. Compile it.') + p(
        'Or skip all that and <A HREF="client.html"><B>launch the Web Edition</B></A>.')
    web_page('download.html', 'Download Snapster', 'download', content, extra_head=dl_js)

    # ---------------------------------------------------------------- company
    content = hdr('company', 'The Company') + p(
        '<B><I>Snapster, Inc.</I></B> was founded in the spring of 1999 in a dorm room, by a college freshman who '
        'was tired of driving to the mall to buy one song and getting eleven others. His pet snapping turtle, '
        'Snappy, watched the whole thing from a 10-gallon tank and became our mascot, our logo, and our '
        'morale officer.') + p(
        'Today Snapster has 31 employees, 2 interns, 1 lawyer, 0 profits and a very sophisticated office in '
        'Redwood Shoal, California, with a foosball table, a hammock, and a refrigerator stocked with '
        'warm soda.') + '''
                  <P><FONT FACE="Arial, Helvetica" SIZE=2><B>Management Team</B></FONT>
                  <TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0>
                  <TR><TD VALIGN=TOP><FONT FACE="Arial, Helvetica" SIZE=2><B>Founder &amp; Chief Turtle Officer</B></FONT></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>Dropped out of a 9 AM class to write the server. Still sleeps until noon.</FONT></TD></TR>
                  <TR><TD VALIGN=TOP><FONT FACE="Arial, Helvetica" SIZE=2><B>CEO</B></FONT></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>An Actual Grown-Up in a tie. Previously ran a chain of mattress stores.</FONT></TD></TR>
                  <TR><TD VALIGN=TOP><FONT FACE="Arial, Helvetica" SIZE=2><B>VP, Bandwidth</B></FONT></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>Keeps the servers running by unplugging the coffee maker at peak hours.</FONT></TD></TR>
                  <TR><TD VALIGN=TOP><FONT FACE="Arial, Helvetica" SIZE=2><B>Legal Department</B></FONT></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>Gary. See <A HREF="legal.html">Legal Department</A>. Knock first.</FONT></TD></TR>
                  <TR><TD VALIGN=TOP><FONT FACE="Arial, Helvetica" SIZE=2><B>Snappy</B></FONT></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>Mascot. Eats lettuce. Has bitten two venture capitalists.</FONT></TD></TR>
                  </TABLE>
                  ''' + p('<B>Investors:</B> Hump Day Ventures, Sand Hill Sandwich Partners, and the founder\'s '
                          'uncle, who invested $500 and a minivan.') + '<A NAME="jobs"></A>' + p(
        '<B>Jobs at Snapster</B> (we\'re hiring!)<BR>&middot; Java Ninja (must own throwing stars, ironically)<BR>'
        '&middot; Perl Wrangler (we have one regex and nobody knows what it does)<BR>'
        '&middot; Server Babysitter, night shift (must love fans, the cooling kind)<BR>'
        '&middot; Legal Department Assistant (must bring own broom)<BR>'
        'Stock options for everybody. They will be worth a fortune. Probably. Send your r&eacute;sum&eacute; by '
        'fax; our email is full.')
    web_page('company.html', 'Snapster - Company', 'company', content, top='company')

    # ---------------------------------------------------------------- advertise
    content = hdr('advertise', 'Advertise With Us') + p(
        '<B><I>Reach the most wired audience on the planet:</I></B> people who leave their computers on all '
        'night so a stranger in Ohio can finish downloading a swing song.') + '''
                  <P><TABLE BORDER=1 CELLPADDING=4 CELLSPACING=0 BGCOLOR="#DDDDAA">
                  <TR BGCOLOR="#99CCCC"><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Our audience</B></FONT></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>%</B></FONT></TD></TR>
                  <TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>College students</FONT></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>87</FONT></TD></TR>
                  <TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>Their roommates</FONT></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>11</FONT></TD></TR>
                  <TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>Their moms, wondering why the phone is busy</FONT></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>1</FONT></TD></TR>
                  <TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>Gary from Legal</FONT></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>1</FONT></TD></TR>
                  </TABLE>
                  ''' + p('<B>Ad units</B><BR>&middot; 468x60 full banner &mdash; $40 CPM (Cost Per Modem)<BR>'
                          '&middot; 120x90 button in the left column &mdash; $25 CPM<BR>'
                          '&middot; Your logo on Snappy\'s shell &mdash; price on request; Snappy must approve') + p(
        'Banners must be under 12 KB, animated GIFs may loop at most 3 times, and absolutely no "punch the monkey" '
        'games. We have standards. Low ones, but standards.') + p(
        'Interested? Fax our ad sales team at (555) 010-SNAP. We check the fax machine every Tuesday.')
    web_page('advertise.html', 'Snapster - Advertise', 'advertise', content)

    # ---------------------------------------------------------------- help (FAQ)
    faq = [
        ('Is Snapster free?', 'Yes. Snapster is free. The modem, the phone line and the electricity are your problem.'),
        ('What does the colored dot next to a song mean?',
         'It shows the line speed of the user who has the file. <B>Green</B>: cable, DSL, T1 &mdash; fast. '
         '<B>Yellow</B>: 56K or ISDN &mdash; fine. <B>Red</B>: 14.4 to 33.6 &mdash; go do your homework while you wait. '
         '<B>Gray</B>: unknown, which usually means "red".'),
        ('Why does my download say "Remote user cancelled"?',
         'The other user stopped sharing, signed off, or their mom picked up the phone. It is not personal. '
         'Probably.'),
        ('What is "ping"?', 'How long it takes for a little message to go to the other computer and back, in '
                            'milliseconds. Lower is better. Anything over 500 means they are on the moon, or on a free dial-up trial disc.'),
        ('How do I share my music?',
         'Put your MP3s in your shared folder (see the Library tab). Then leave your computer on. Then leave it '
         'on some more. Your roommate will love it.'),
        ('Can I download the whole Internet?', 'No. We asked. It does not fit on a Zip disk.'),
        ('Will Snapster work after Y2K?', 'It is the year 2000. It already does. Please let Bob out of the bunker.'),
        ('Why can\'t I find any Shiny Metallic Things songs?', 'Please see our <A HREF="legal.html">Legal '
                                                               'Department</A>. Bring a broom.'),
        ('I am firewalled at school. Can I still use Snapster?',
         'You can download from people who are not firewalled. Two firewalled people cannot talk to each other, '
         'which is also true of most dorm floors.'),
        ('How do I get rid of the turtle?', 'You don\'t. The turtle is forever.'),
    ]
    items = ''.join('<LI><A HREF="#q%d">%s</A>' % (i, q) for i, (q, a) in enumerate(faq))
    body = ''.join('<A NAME="q%d"></A>' % i + p('<B>Q: %s</B><BR>A: %s' % (q, a)) for i, (q, a) in enumerate(faq))
    content = hdr('help', 'Help & FAQ') + p(
        'Before asking in #Help, please check if your question is answered below. Hank is only a sophomore.') + \
        '<FONT FACE="Arial, Helvetica" SIZE=2><OL>%s</OL></FONT><HR SIZE=1 NOSHADE>%s' % (items, body) + p(
            'Still stuck? Ask in the <A HREF="chat.html?channel=Help">#Help chat channel</A>.')
    web_page('help.html', 'Snapster - Help', 'help', content)

    # ---------------------------------------------------------------- terms
    terms = [
        'By using Snapster you agree to these Terms of Use, which you did not read. Nobody does. That is fine.',
        'You promise to share only files that you have the right to share, such as recordings of yourself '
        'humming, your garage band, and your dog\'s birthday song.',
        'You will not use Snapster to share anything that is not music, such as spreadsheets, your term paper, '
        'or "dancing_baby_final_FINAL2.avi".',
        'You will tell the truth about your line speed. Claiming a T3 from a 14.4 is a violation of these Terms '
        'and of the laws of physics.',
        'Snapster may change these Terms at any time, usually around 3 AM, usually after pizza.',
        'Snapster is provided "as is", "as was" and "as it will hopefully be in Beta 6".',
        'Snappy the Turtle is not liable for any bites. You were warned.',
        'If any part of these Terms is found unenforceable, Gary will rewrite it on a napkin.',
    ]
    content = hdr('terms', 'Terms of Use') + p('<I>Last updated: whenever Gary had a free minute.</I>') + \
        '<FONT FACE="Arial, Helvetica" SIZE=2><OL>%s</OL></FONT>' % ''.join('<LI>%s<P>' % t for t in terms)
    web_page('terms.html', 'Snapster - Terms of Use', 'terms', content)

    # ---------------------------------------------------------------- artists
    newbies = [('Garage Door Opener', 'Pop-punk from a garage, with the door open, for ventilation.'),
               ('The Sandwich Theory', 'Math rock about lunch. Every song is in 7/8 and about rye bread.'),
               ('Cul-de-Sac Symphony', 'A 14-piece orchestra made entirely of neighbors.'),
               ('DJ Screensaver', 'Ambient tracks that start playing after 10 minutes of inactivity.'),
               ('Mildly Annoyed Hornets', 'Ska. Of course it\'s ska.')]
    content = hdr('artists', 'New Artist Program') + p(
        '<B><I>Unsigned? Undiscovered? Under your parents\' roof?</I></B> The Snapster New Artist Program lets '
        'independent bands share their music with thousands of fans who are already online and already sharing.') + \
        p('<B>Featured new artists this week:</B>') + '<FONT FACE="Arial, Helvetica" SIZE=2><UL>%s</UL></FONT>' % \
        ''.join('<LI><B>%s</B> &mdash; %s' % (n, d) for n, d in newbies) + '''
                  <FORM NAME="artist" onSubmit="alert('Thanks! Your band has been added to the queue.\\nYou are number 48,112. Keep practicing!'); return false">
                  <TABLE BORDER=0 CELLPADDING=2 CELLSPACING=0 BGCOLOR="#BBBB88">
                  <TR><TD COLSPAN=2><FONT FACE="Arial, Helvetica" SIZE=2><B>Sign up your band</B></FONT></TD></TR>
                  <TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>Band name:</FONT></TD><TD><INPUT TYPE=TEXT NAME="band" SIZE=24></TD></TR>
                  <TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>Genre:</FONT></TD><TD><SELECT NAME="genre"><OPTION>Ska<OPTION>Ska-punk<OPTION>Ska-core<OPTION>Swing<OPTION>Nu-metal<OPTION>Trip-hop<OPTION>Big beat<OPTION>Emo<OPTION>Something else (it's ska)</SELECT></TD></TR>
                  <TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>Members:</FONT></TD><TD><INPUT TYPE=TEXT NAME="members" SIZE=4> <FONT FACE="Arial, Helvetica" SIZE=1>(trombonists count double)</FONT></TD></TR>
                  <TR><TD></TD><TD><INPUT TYPE=SUBMIT VALUE="Sign us up!"></TD></TR>
                  </TABLE></FORM>
                  ''' + p('Artists keep all rights to their music. We just keep the turtle.', 1)
    web_page('artists.html', 'Snapster - New Artist Program', 'artists', content)

    # ---------------------------------------------------------------- ground zero
    stories = [
        ('SCENE REPORT', 'Swing revival refuses to end, now entering its fourth "final" summer',
         'Our correspondents report that the swing revival, declared over in March, then in May, then again '
         'in July, continues at full tilt. "We just bought the shoes," explains one lindy hopper. "We are not '
         'stopping until we get our money\'s worth."'),
        ('SKA WATCH', 'Local ska band adds tenth trombonist; stage collapses gently',
         'The Checkerboard Tuxedo Revue added a tenth trombone player on Friday. The venue added a sign that '
         'reads "MAX 9 TROMBONES". Nobody was hurt, but several slides were bent.'),
        ('INTERVIEW', 'Five minutes with DJ Dialtone',
         '<I>Q: Your new single is just the sound of a modem connecting. Why?</I><BR>A: It is the sound of our '
         'generation. Also, I could not afford a sampler.'),
        ('CHARTS', 'Most searched on Snapster this week',
         '1. Mambo Number 404 &middot; 2. Oops, I Rebooted Again &middot; 3. Teardrop in My Latte &middot; '
         '4. Bye Bye Pager &middot; 5. Napkin of Doom (0 results, see <A HREF="legal.html">Legal</A>)'),
    ]
    content = hdr('groundzero', 'ground zero') + p(
        '<B><I>ground zero</I></B> is where the Snapster community talks about music: who\'s new, who\'s touring, '
        'and who has 47 trombones.') + ''.join(
        '<P><FONT FACE="Arial, Helvetica" SIZE=1 COLOR="#666633"><B>%s</B></FONT><BR>'
        '<FONT FACE="Arial, Helvetica" SIZE=3><B>%s</B></FONT><BR><FONT FACE="Arial, Helvetica" SIZE=2>%s</FONT></P>'
        % s for s in stories) + '<A NAME="contest"></A>' + p(
        '<B>CONTEST: RadioRhombus.com wants to give you a 32 MB MP3 player!</B> That\'s almost eight songs at '
        '128 kbps, or one jam band song. To enter, tell us in 25 words or fewer why you deserve it. Entries '
        'accepted by fax only. (Contest is pretend. So is the fax.)') + p(
        '<B>Hear it:</B> the official <A HREF="jingle.mid">Snapster startup jingle</A> (MIDI, 1 KB &mdash; '
        'plays on your sound card\'s finest kazoo patch).')
    web_page('groundzero.html', 'Snapster - ground zero', 'groundzero', content)

    # ---------------------------------------------------------------- press
    releases = [
        ('October 23, 2000', 'Snapster ships 2.0 Beta 5; turtle icon now spins only a little'),
        ('October 2, 2000', 'Snapster passes 8,000 simultaneous users and one simultaneous lawyer'),
        ('September 12, 2000', 'Snapster opens second office in the other half of the first office'),
        ('August 1, 2000', 'Snapster and RadioRhombus.com announce contest nobody understands'),
        ('June 30, 2000', 'Snapster Legal Department expands from one broom to two brooms'),
        ('May 15, 2000', 'Snapster raises Series B from Hump Day Ventures, spends it on beanbags'),
    ]
    quotes = [('The Modem Monthly', 'The most exciting thing to happen to my phone line since call waiting.'),
              ('Dot Com Daily', 'Burning cash at a pace we can only describe as inspiring.'),
              ('Teen Zine Quarterly', 'OMG. The turtle is SO cute.'),
              ('Gary, Snapster Legal Department', 'No comment. Please close the door, there is a draft.')]
    content = hdr('press', 'Press Room') + p('<B>Press Releases</B>') + '<FONT FACE="Arial, Helvetica" SIZE=2>' + \
        ''.join('<B>%s</B><BR><A HREF="press.html#r%d">%s</A><P>' % (d, i, t) for i, (d, t) in enumerate(releases)) + \
        '</FONT>' + p('<B>What they\'re saying</B>') + ''.join(
            '<BLOCKQUOTE><FONT FACE="Arial, Helvetica" SIZE=2><I>"%s"</I><BR>&mdash; %s</FONT></BLOCKQUOTE>' % (q, s)
            for s, q in quotes) + ''.join(
            '<A NAME="r%d"></A>' % i for i in range(len(releases))) + p(
        '<B>Press contact:</B> our PR person is on vacation. Please talk to Snappy. He will not respond, but he '
        'is a good listener.')
    web_page('press.html', 'Snapster - Press Room', 'press', content)

    # ---------------------------------------------------------------- legal
    legal_js = '''<SCRIPT LANGUAGE="JavaScript">
<!--
var letters = 4812;
function drawLetters() {
  var s = "" + letters;
  while (s.length < 6) s = "0" + s;
  for (var i = 0; i < 6; i++) sw("cd" + i, "images/digit_" + s.charAt(i) + ".gif");
}
function moreMail() {
  letters += Math.floor(Math.random() * 3) + 1;
  drawLetters();
  setTimeout("moreMail()", 2500 + Math.floor(Math.random() * 3000));
}
// -->
</SCRIPT>'''
    digits = ''.join('<IMG SRC="images/digit_%s.gif" WIDTH=15 HEIGHT=20 NAME="cd%d">' % (c, i)
                     for i, c in enumerate('004812'))
    letters = [
        ('March 3, 2000',
         'Dear Snapster, We are Shiny Metallic Things. Perhaps you have heard of us. We have noticed that some '
         'of your users have our songs, including "Napkin of Doom", which is about a napkin and also doom. '
         'Please make them stop. Sincerely, the band (and our manager, and his manager).'),
        ('April 19, 2000',
         'Dear Snapster, This is our second letter. Enclosed please find a list of 4,000 screen names, printed '
         'on very nice paper. Our drummer typed them himself. It took a while. Please make them stop.'),
        ('June 2, 2000',
         'Dear Snapster, Gary called us back. We appreciate that. We did not appreciate that he called from a '
         'broom closet and kept saying "hang on, the mop fell over". Third letter. Please make them stop.'),
    ]
    content = hdr('legal', 'Legal Department') + '''
                  <TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0><TR>
                  <TD VALIGN=TOP><IMG SRC="images/broom_closet.gif" WIDTH=130 HEIGHT=170 ALT="Legal Department door" HSPACE=4></TD>
                  <TD VALIGN=TOP><FONT FACE="Arial, Helvetica" SIZE=2><B><I>Welcome to the Snapster Legal Department.</I></B><P>
                  Our entire legal staff, Gary, works out of a former broom closet on the second floor, next to the
                  router. He is very busy. Please slide all correspondence under the door.</FONT>
                  <P><FONT FACE="Arial, Helvetica" SIZE=1><B>CEASE &amp; DESIST LETTERS RECEIVED:</B></FONT><BR>
                  <TABLE BORDER=2 CELLPADDING=0 CELLSPACING=0 BGCOLOR="#000000"><TR><TD>%s</TD></TR></TABLE>
                  <FONT FACE="Arial, Helvetica" SIZE=1><I>(updated in real time, unfortunately)</I></FONT>
                  </TD></TR></TABLE>
                  ''' % digits + p('<B>Our Position on Artists</B><BR>Snapster respects artists. We love artists. '
                                   'Some of our best friends are artists. We respect artists so much that we have '
                                   'a whole <A HREF="artists.html">program</A> for them. We respect the ones with '
                                   'lawyers even more, and with a little more eye contact.') + p(
        '<B>MP3 Copyright Policy</B><BR>If you own the rights to a song and believe a Snapster user is sharing it '
        'without permission, please fill out Form 7-B in triplicate, list the user\'s screen name, the file name, '
        'and your favorite color, and slide it under Gary\'s door. Gary will block that user, who will then sign up '
        'again as that user plus "2". We are working on this.') + p(
        '<B>Selected correspondence from the band Shiny Metallic Things</B>') + ''.join(
        '<TABLE BORDER=1 CELLPADDING=6 CELLSPACING=0 BGCOLOR="#FFFFEE" WIDTH=360><TR><TD><FONT FACE="Times New Roman, '
        'Times" SIZE=2><I>%s</I><P>%s</FONT></TD></TR></TABLE><BR>' % l for l in letters) + p(
        '<B>Gary\'s reply</B> (all three times): "Thank you for your letter. It has been placed in the important '
        'pile, which is the one on the left, under the mop. Rock on."') + p(
        '<I>Snapster is a parody. Gary, the broom, and the band Shiny Metallic Things are all made up.</I>', 1)
    web_page('legal.html', 'Snapster - Legal Department', 'legal', content, extra_head=legal_js,
             onload='; drawLetters(); setTimeout(\'moreMail()\', 3000)')


# =====================================================================================
#                                  the "client" pages
# =====================================================================================
TAB_HREF = {'home': 'client.html', 'chat': 'chat.html', 'library': 'library.html', 'search': 'search.html',
            'hotlist': 'hotlist.html', 'transfer': 'transfer.html', 'discover': 'discover.html',
            'help': 'help.html'}
TAB_NAMES = dict((k, v) for k, v in [('home', 'Home'), ('chat', 'Chat'), ('library', 'Library'),
                                     ('search', 'Search'), ('hotlist', 'Hot List'), ('transfer', 'Transfer'),
                                     ('discover', 'Discover'), ('help', 'Help')])

CLIENT_JS = '''<SCRIPT LANGUAGE="JavaScript">
<!--
// ---- Snapster Web Edition common code (JavaScript 1.2) ----
function sw(n, s) {
  if (document.images && document.images[n]) document.images[n].src = s;
}
function getArg(name) {
  var q = location.search, i, parts, kv;
  if (q.length < 2) return "";
  parts = q.substring(1).split("&");
  for (i = 0; i < parts.length; i++) {
    kv = parts[i].split("=");
    if (kv[0] == name && kv.length > 1) return unescape(kv[1].split("+").join(" "));
  }
  return "";
}
function getCookie(name) {
  var c = "; " + document.cookie, p = "; " + name + "=", i = c.indexOf(p), j;
  if (i == -1) return "";
  j = c.indexOf(";", i + p.length);
  if (j == -1) j = c.length;
  return unescape(c.substring(i + p.length, j));
}
function setCookie(name, value, days) {
  var exp = new Date();
  exp.setTime(exp.getTime() + days * 86400000);
  document.cookie = name + "=" + escape(value) + "; expires=" + exp.toGMTString();
}
function getSelected(f) {
  var ids = new Array(), old = getCookie("snapdl"), i, e, n = 0;
  if (old != "") ids = old.split(".");
  for (i = 0; i < f.elements.length; i++) {
    e = f.elements[i];
    if (e.type == "checkbox" && e.checked && e.value != "") {
      var dup = false;
      for (var j = 0; j < ids.length; j++) if (ids[j] == e.value) dup = true;
      if (!dup) { ids[ids.length] = e.value; n++; }
    }
  }
  if (n == 0) {
    alert("Select at least one song first.\\nSnappy can't read minds. Yet. (Beta 6.)");
    return false;
  }
  while (ids.length > 30) ids = ids.slice(1);
  setCookie("snapdl", ids.join("."), 7);
  location.href = "transfer.html";
  return false;
}
function selAll(f, on) {
  for (var i = 0; i < f.elements.length; i++)
    if (f.elements[i].type == "checkbox") f.elements[i].checked = on;
}
function menu(m) {
  if (m == "file") alert("File\\n\\nNew Window... (disabled)\\nExit (please don't, we're bonding)");
  else if (m == "actions") alert("Actions\\n\\nShare MP3s: ON\\nAuto-reconnect: ON\\nPretend to have a T3: OFF (thank you)");
  else alert("Snapster v2.0 BETA 5 (Web Edition)\\n\\n(c) 1999-2000 Snapster, Inc.\\nTurtle by Snappy.");
}
function winBtn(b) {
  if (b == "min") alert("Snapster has been minimized to the system tray.\\n(Not really. This is a web page.)");
  else alert("Snapster is already as big as it gets.\\nTry a 17-inch monitor.");
}
function commas(n) {
  var s = "" + n, out = "";
  while (s.length > 3) { out = "," + s.substring(s.length - 3) + out; s = s.substring(0, s.length - 3); }
  return s + out;
}
function mmss(sec) {
  var m = Math.floor(sec / 60), s = Math.floor(sec % 60);
  return m + ":" + (s < 10 ? "0" : "") + s;
}
// -->
</SCRIPT>'''


def catalog_js():
    rows = []
    for r in CAT:
        rows.append([ARTISTS.index(r['artist']), r['title'], r['file'], r['size'], r['bitrate'], r['freq'],
                     r['secs'], UNAMES.index(r['user']), r['conn'], r['ping']])
    lines = ',\n'.join(js(r) for r in rows)
    return '''<SCRIPT LANGUAGE="JavaScript">
<!--
// Snapster song catalog, generated by tools/gen.py from tools/data.py
// row: [artist#, title, filename, bytes, kbps, Hz, seconds, user#, line#, ping]
var CONN = %s;
var CONNKB = %s;
var ARTISTS = %s;
var USERS = %s;
var CAT = [
%s
];
// -->
</SCRIPT>''' % (js(data.CONN), js(data.CONN_KBPS), js(ARTISTS), js(UNAMES), lines)


def dot_for(ci):
    if ci == 0:
        return 'gray'
    if ci <= 3:
        return 'red'
    if ci <= 6:
        return 'yellow'
    return 'green'


DOT_JS = '''<SCRIPT LANGUAGE="JavaScript">
<!--
function dotImg(ci) {
  var c = "green";
  if (ci == 0) c = "gray"; else if (ci <= 3) c = "red"; else if (ci <= 6) c = "yellow";
  var src = "images/dot_" + c + ".gif";
  return "<IMG SRC=\\"" + src + "\\" WIDTH=10 HEIGHT=10 ALT=\\"" + c + "\\">";
}
// -->
</SCRIPT>'''


def shared_count():
    return sum(len(files) for root, folders in data.LIBRARY for name, files in folders)


def status_text():
    return 'Online (%s): Sharing %d songs. Currently %s users (%s songs) available.' % (
        data.ME, shared_count(), commas(data.TOTAL_USERS), commas(data.TOTAL_SONGS))


def client_page(fname, tab, title, body, head='', onload='', catalog=False):
    tabs = []
    for k, label in data_tabs():
        href = TAB_HREF[k]
        if k == tab:
            tabs.append('<TD><A HREF="%s"><IMG SRC="images/tab_%s_on.gif" WIDTH=70 HEIGHT=50 BORDER=0 ALT="%s"></A></TD>'
                        % (href, k, label))
        else:
            tabs.append('<TD><A HREF="%s" onMouseOver="sw(\'tb_%s\',\'images/tab_%s_mo.gif\')" '
                        'onMouseOut="sw(\'tb_%s\',\'images/tab_%s.gif\')"><IMG SRC="images/tab_%s.gif" WIDTH=70 '
                        'HEIGHT=50 BORDER=0 NAME="tb_%s" ALT="%s"></A></TD>' % (href, k, k, k, k, k, k, label))
    html = '''<HTML>
<HEAD>
<TITLE>Snapster v2.0 BETA 5 - %(title)s</TITLE>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1">
%(cjs)s
%(cat)s
%(head)s
</HEAD>
<BODY BGCOLOR="#008080" TEXT="#CCCCCC" LINK="#99CCCC" VLINK="#99CCCC" ALINK="#FFFFFF"%(onload)s>
<CENTER>
<P><TABLE BORDER=2 CELLPADDING=0 CELLSPACING=0 BGCOLOR="#C0C0C0" WIDTH=644><TR><TD>
<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=640>
<TR>
  <TD BGCOLOR="#000080" WIDTH=584><IMG SRC="images/titlebar.gif" WIDTH=584 HEIGHT=18 ALT="Snapster v2.0 BETA 5"></TD>
  <TD BGCOLOR="#1084D0" ALIGN=RIGHT NOWRAP><A HREF="javascript:winBtn('min')"><IMG SRC="images/win_min.gif" WIDTH=16 HEIGHT=14 BORDER=0 ALT="_"></A><A HREF="javascript:winBtn('max')"><IMG SRC="images/win_max.gif" WIDTH=16 HEIGHT=14 BORDER=0 ALT="[]"></A><IMG SRC="images/clear.gif" WIDTH=2 HEIGHT=14><A HREF="index.html"><IMG SRC="images/win_close.gif" WIDTH=16 HEIGHT=14 BORDER=0 ALT="X"></A><IMG SRC="images/clear.gif" WIDTH=2 HEIGHT=14></TD>
</TR>
<TR><TD COLSPAN=2 BGCOLOR="#C0C0C0"><FONT FACE="Arial, Helvetica" SIZE=1 COLOR="#000000">&nbsp;
  <A HREF="javascript:menu('file')"><FONT COLOR="#000000"><U>F</U>ile</FONT></A> &nbsp;
  <A HREF="javascript:menu('actions')"><FONT COLOR="#000000"><U>A</U>ctions</FONT></A> &nbsp;
  <A HREF="javascript:menu('help')"><FONT COLOR="#000000"><U>H</U>elp</FONT></A></FONT></TD></TR>
<TR><TD COLSPAN=2 BGCOLOR="#1A1A1A">
  <TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=640><TR>
  %(tabs)s
  <TD ALIGN=RIGHT WIDTH=80><A HREF="index.html"><IMG SRC="images/snappy_48.gif" WIDTH=48 HEIGHT=48 BORDER=0 ALT="snapster.com" HSPACE=6></A></TD>
  </TR></TABLE>
</TD></TR>
<TR><TD COLSPAN=2 BGCOLOR="#3A3A3A" HEIGHT=360 VALIGN=TOP>
<TABLE BORDER=0 CELLPADDING=8 CELLSPACING=0 WIDTH=640><TR><TD VALIGN=TOP>
%(body)s
</TD></TR></TABLE>
</TD></TR>
<TR><TD COLSPAN=2 BGCOLOR="#C0C0C0">
  <TABLE BORDER=1 CELLPADDING=1 CELLSPACING=0 WIDTH=640><TR><TD><FONT FACE="Arial, Helvetica" SIZE=1 COLOR="#000000">%(status)s</FONT></TD><TD WIDTH=60 ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=1 COLOR="#000000">%(clock)s</FONT></TD></TR></TABLE>
</TD></TR>
</TABLE>
</TD></TR></TABLE>
<P><FONT FACE="Arial, Helvetica" SIZE=1>This is <B>Snapster Web Edition</B>, a pretend client. Back to <A HREF="index.html"><FONT COLOR="#FFFFFF">snapster.com</FONT></A>.</FONT>
</CENTER>
%(ring)s
</BODY>
</HTML>
''' % dict(title=title, cjs=CLIENT_JS, cat=catalog_js() if catalog else '', head=head,
           onload=(' onLoad="%s"' % onload) if onload else '', tabs='\n  '.join(tabs), body=body,
           status=status_text(), clock='11:52 PM', ring=webring())
    write(fname, html)


def data_tabs():
    return [('home', 'Home'), ('chat', 'Chat'), ('library', 'Library'), ('search', 'Search'),
            ('hotlist', 'Hot List'), ('transfer', 'Transfer'), ('discover', 'Discover'), ('help', 'Help')]


def f(text, size=2, color=None, bold=False):
    t = '<B>%s</B>' % text if bold else text
    c = ' COLOR="%s"' % color if color else ''
    return '<FONT FACE="Arial, Helvetica" SIZE=%d%s>%s</FONT>' % (size, c, t)


def panel(title, inner, width='100%'):
    return ('<TABLE BORDER=0 CELLPADDING=1 CELLSPACING=0 BGCOLOR="#666666" WIDTH="%s"><TR><TD>'
            '<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 BGCOLOR="#2A2A2A" WIDTH="100%%">'
            '<TR><TD BGCOLOR="#555555">%s</TD></TR><TR><TD>%s</TD></TR></TABLE></TD></TR></TABLE>'
            % (width, f(title, 2, '#FFFFFF', True), inner))


def grid_head(cols):
    return '<TR BGCOLOR="#555555">' + ''.join('<TD NOWRAP>%s</TD>' % f(c, 1, '#FFFFFF', True) for c in cols) + '</TR>'


def build_client():
    online = [h for h in data.HOTLIST if h[1]]
    # ---------------------------------------------------------------- home
    news = ''.join('<P>%s<BR>%s<BR>%s</P>' % (f(d, 1, '#999999'), f(t, 2, '#99CCCC', True), f(b, 2))
                   for d, t, b in data.NEWS)
    body = '''<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=620><TR>
<TD VALIGN=TOP WIDTH=400>%s</TD><TD WIDTH=12>&nbsp;</TD>
<TD VALIGN=TOP>%s<P>%s<P>%s</TD></TR></TABLE>''' % (
        panel('Welcome back, %s!' % data.ME,
              f('You are connected to <B>server 3 of 5</B> (the one under the desk). There are <B>%s</B> users '
                'online sharing <B>%s</B> songs. %d of your Hot List friends are online.'
                % (commas(data.TOTAL_USERS), commas(data.TOTAL_SONGS), len(online))) + news),
        panel('Quick Search', '<FORM NAME="qs" ACTION="search.html" METHOD=GET>' + f('Artist:', 1) +
              '<BR><INPUT TYPE=TEXT NAME="artist" SIZE=18><BR>' + f('Title:', 1) +
              '<BR><INPUT TYPE=TEXT NAME="title" SIZE=18><BR><INPUT TYPE=SUBMIT VALUE="Find It!"></FORM>'),
        panel('Tip of the Day', f('Try searching for <A HREF="search.html?artist=swing&amp;title=">swing</A>. The swing '
                                  'revival is still going. It will always be going.', 1)),
        panel('Startup Sound', f('Missed the jingle? <A HREF="jingle.mid">Play it again</A> (MIDI).', 1)))
    client_page('client.html', 'home', 'Home', body)

    # ---------------------------------------------------------------- search
    def opts(values, cur=None):
        return ''.join('<OPTION VALUE="%s">%s' % (v, l) for v, l in values)
    ops = opts([('ge', 'at least'), ('eq', 'equal to'), ('le', 'at most')])
    speed = opts([('', 'Any')] + [(str(i), c) for i, c in enumerate(data.CONN)])
    brs = opts([('', 'Any')] + [(str(b), str(b)) for b in (64, 96, 112, 128, 160, 192, 256, 320)])
    fqs = opts([('', 'Any'), ('22050', '22050'), ('44100', '44100')])
    pings = opts([('', 'Any')] + [(str(v), str(v)) for v in (25, 50, 100, 200, 400, 800)])
    maxr = opts([(str(v), str(v)) for v in (100, 50, 25, 10, 500)])

    def adv(label, name, values, default_op):
        return ('<TR><TD>%s</TD><TD><SELECT NAME="%sop">%s</SELECT></TD><TD><SELECT NAME="%s">%s</SELECT></TD></TR>'
                % (f(label, 1), name, ops, name, values))
    search_js = '''<SCRIPT LANGUAGE="JavaScript">
<!--
function norm(s) { return s.toLowerCase().split("_").join(" "); }
function cmp(op, a, b) {
  if (op == "eq") return a == b;
  if (op == "le") return a <= b;
  return a >= b;
}
function setSel(sel, v) {
  for (var i = 0; i < sel.options.length; i++) if (sel.options[i].value == v) sel.selectedIndex = i;
}
function fill() {
  var f = document.forms["find"], names = new Array("speed", "bitrate", "freq", "ping"), i;
  f.artist.value = getArg("artist");
  f.title.value = getArg("title");
  if (getArg("max") != "") setSel(f.max, getArg("max"));
  for (i = 0; i < names.length; i++) {
    if (getArg(names[i] + "op") != "") setSel(f.elements[names[i] + "op"], getArg(names[i] + "op"));
    setSel(f.elements[names[i]], getArg(names[i]));
  }
  if (getArg("pingop") == "") setSel(f.pingop, "le");
}
function sortPing(a, b) { return CAT[a][9] - CAT[b][9]; }
function doSearch() {
  var artist = norm(getArg("artist")), title = norm(getArg("title"));
  var max = parseInt(getArg("max")); if (isNaN(max) || max < 1) max = 100;
  var fl = new Array(), names = new Array("speed", "bitrate", "freq", "ping"), col = new Array(8, 4, 5, 9), i, k;
  for (k = 0; k < 4; k++) {
    var v = getArg(names[k]);
    var op = getArg(names[k] + "op");
    if (op == "") op = (k == 3 ? "le" : "ge");
    if (v != "") fl[fl.length] = new Array(col[k], op, parseInt(v));
  }
  if (artist == "" && title == "") {
    document.write("<P><FONT FACE=\\"Arial, Helvetica\\" SIZE=2>Type an artist and/or a song title above and click <B>Find It!</B><BR>" +
      "<FONT SIZE=1 COLOR=\\"#999999\\">Psst: try <A HREF=\\"search.html?artist=swing&title=\\">swing</A>, " +
      "<A HREF=\\"search.html?artist=&title=modem\\">modem</A> or <A HREF=\\"search.html?artist=frosted+tips&title=\\">frosted tips</A>.</FONT></FONT>");
    return;
  }
  var hits = new Array();
  for (i = 0; i < CAT.length; i++) {
    var r = CAT[i], fn = norm(r[2]);
    if (artist != "" && norm(ARTISTS[r[0]]).indexOf(artist) == -1 && fn.indexOf(artist) == -1) continue;
    if (title != "" && norm(r[1]).indexOf(title) == -1 && fn.indexOf(title) == -1) continue;
    var ok = true;
    for (k = 0; k < fl.length; k++) if (!cmp(fl[k][1], r[fl[k][0]], fl[k][2])) ok = false;
    if (ok) hits[hits.length] = i;
  }
  hits.sort(sortPing);
  var shown = hits.length > max ? max : hits.length;
  var out = "<FONT FACE=\\"Arial, Helvetica\\" SIZE=1>Returned <B>" + hits.length + "</B> results" +
    (shown < hits.length ? " (showing the " + shown + " with the best ping)" : "") + ".</FONT><BR>";
  if (hits.length == 0) {
    out += "<P><FONT FACE=\\"Arial, Helvetica\\" SIZE=2>No results found. Try fewer words, check your spelling, " +
      "or loosen those Advanced filters. (If you were looking for Shiny Metallic Things, please see our " +
      "<A HREF=\\"legal.html\\">Legal Department</A>.)</FONT>";
    document.write(out);
    return;
  }
  out += "<FORM NAME=\\"res\\" onSubmit=\\"return getSelected(this)\\"><TABLE BORDER=0 CELLPADDING=2 CELLSPACING=1 WIDTH=620>" +
    "<TR BGCOLOR=\\"#555555\\"><TD></TD>";
  var heads = new Array("Filename", "Filesize", "Bitrate", "Freq", "Length", "User", "Connection", "Ping");
  for (k = 0; k < heads.length; k++) out += "<TD NOWRAP><FONT FACE=\\"Arial, Helvetica\\" SIZE=1 COLOR=\\"#FFFFFF\\"><B>" + heads[k] + "</B></FONT></TD>";
  out += "</TR>";
  for (i = 0; i < shown; i++) {
    var r = CAT[hits[i]], fo = "<FONT FACE=\\"Arial, Helvetica\\" SIZE=1>";
    out += "<TR BGCOLOR=\\"" + (i % 2 ? "#111111" : "#000000") + "\\">" +
      "<TD><INPUT TYPE=CHECKBOX NAME=\\"c" + i + "\\" VALUE=\\"" + hits[i] + "\\"></TD>" +
      "<TD>" + dotImg(r[8]) + " " + fo + r[2] + "</FONT></TD>" +
      "<TD ALIGN=RIGHT>" + fo + commas(r[3]) + "</FONT></TD>" +
      "<TD ALIGN=RIGHT>" + fo + r[4] + "</FONT></TD>" +
      "<TD ALIGN=RIGHT>" + fo + r[5] + "</FONT></TD>" +
      "<TD ALIGN=RIGHT>" + fo + mmss(r[6]) + "</FONT></TD>" +
      "<TD>" + fo + USERS[r[7]] + "</FONT></TD>" +
      "<TD>" + fo + CONN[r[8]] + "</FONT></TD>" +
      "<TD ALIGN=RIGHT>" + fo + r[9] + "</FONT></TD></TR>";
  }
  out += "</TABLE><P><INPUT TYPE=SUBMIT VALUE=\\"Get Selected Song(s)\\"> " +
    "<INPUT TYPE=BUTTON VALUE=\\"Select All\\" onClick=\\"selAll(this.form, true)\\"> " +
    "<INPUT TYPE=BUTTON VALUE=\\"Select None\\" onClick=\\"selAll(this.form, false)\\"></FORM>";
  document.write(out);
}
// -->
</SCRIPT>'''
    form = '''<FORM NAME="find" ACTION="search.html" METHOD=GET>
<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=620><TR><TD VALIGN=TOP>
%s
</TD><TD WIDTH=10>&nbsp;</TD><TD VALIGN=TOP>
%s
</TD></TR></TABLE>
</FORM>''' % (
        panel('Search', '<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=0>'
              '<TR><TD>%s</TD><TD><INPUT TYPE=TEXT NAME="artist" SIZE=26></TD></TR>'
              '<TR><TD>%s</TD><TD><INPUT TYPE=TEXT NAME="title" SIZE=26></TD></TR>'
              '<TR><TD>%s</TD><TD><SELECT NAME="max">%s</SELECT></TD></TR>'
              '<TR><TD></TD><TD><INPUT TYPE=SUBMIT VALUE="Find It!"> '
              '<INPUT TYPE=BUTTON VALUE="Clear" onClick="location.href=\'search.html\'"></TD></TR></TABLE>'
              % (f('Artist:', 2), f('Title:', 2), f('Max Results:', 1), maxr), 290),
        panel('Advanced', '<TABLE BORDER=0 CELLPADDING=1 CELLSPACING=0>' +
              adv('Line Speed', 'speed', speed, 'ge') + adv('Bitrate', 'bitrate', brs, 'ge') +
              adv('Frequency', 'freq', fqs, 'ge') + adv('Ping', 'ping', pings, 'le') + '</TABLE>', 300))
    body = form + '''
<SCRIPT LANGUAGE="JavaScript">
<!--
fill();
doSearch();
// -->
</SCRIPT>
<NOSCRIPT><FONT FACE="Arial, Helvetica" SIZE=2>Snapster Web Edition needs JavaScript. Like, a lot.</FONT></NOSCRIPT>'''
    client_page('search.html', 'search', 'Search', body, head=DOT_JS + search_js, catalog=True)

    # ---------------------------------------------------------------- transfer
    transfer_js = '''<SCRIPT LANGUAGE="JavaScript">
<!--
var D = new Array();
function pad2(n) { return (n < 10 ? "0" : "") + n; }
function Dl(row) {
  var r = Math.random();
  this.row = row;
  this.size = CAT[row][3];
  this.got = 0;
  this.state = "info";
  this.wait = 2 + Math.floor(Math.random() * 5);
  this.rate = 0;
  this.fate = r < 0.12 ? "cancel" : (r < 0.2 ? "timeout" : (r < 0.28 ? "queue" : "ok"));
  this.queue = 2 + Math.floor(Math.random() * 4);
  this.failAt = 0.15 + Math.random() * 0.7;
}
function show(i, st, rt, tl) {
  var f = document.forms["xf"];
  f.elements["st" + i].value = st;
  f.elements["rt" + i].value = rt;
  f.elements["tl" + i].value = tl;
}
function bar(i, frac) {
  var n = Math.floor(frac * 20);
  if (n > 20) n = 20;
  sw("p" + i, "images/bar_" + pad2(n) + ".gif");
}
function step() {
  var busy = false;
  for (var i = 0; i < D.length; i++) {
    var d = D[i];
    if (d.state == "info") {
      busy = true;
      show(i, "Getting info...", "", "");
      if (--d.wait <= 0) { d.state = "conn"; d.wait = d.fate == "timeout" ? 12 : 2 + Math.floor(Math.random() * 3); }
    } else if (d.state == "conn") {
      busy = true;
      show(i, "Connecting...", "", "");
      if (--d.wait <= 0) {
        if (d.fate == "timeout") { d.state = "dead"; show(i, "Timed out", "", "--:--"); }
        else if (d.fate == "queue") { d.state = "queue"; d.wait = 6; }
        else d.state = "xfer";
      }
    } else if (d.state == "queue") {
      busy = true;
      show(i, "Remotely queued (" + d.queue + ")", "", "");
      if (--d.wait <= 0) { d.wait = 6; if (--d.queue <= 0) d.state = "xfer"; }
    } else if (d.state == "xfer") {
      busy = true;
      var kb = CONNKB[CAT[d.row][8]] * (0.6 + Math.random() * 0.7);
      if (kb > 160) kb = 160;
      d.rate = kb;
      d.got += kb * 1024 / 2;
      if (d.fate == "cancel" && d.got >= d.size * d.failAt) {
        d.state = "dead";
        show(i, "Remote user cancelled", "", "--:--");
        continue;
      }
      if (d.got >= d.size) {
        d.got = d.size; d.state = "done";
        bar(i, 1);
        show(i, "Complete", "", "0:00");
        continue;
      }
      bar(i, d.got / d.size);
      show(i, "Transferring " + Math.floor(d.got * 100 / d.size) + "%", (Math.round(kb * 10) / 10) + " KB/s",
           mmss((d.size - d.got) / 1024 / kb));
    }
  }
  upStep();
  setTimeout("step()", 500);
}
var up = 0, upGot = 0, upSize = 1504128;
function upStep() {
  var f = document.forms["xf"];
  if (up == 0) {
    upGot += 900 * (0.5 + Math.random());
    if (upGot > upSize * 0.37) { up = 1; f.ust.value = "Remote user cancelled"; f.urt.value = ""; f.utl.value = "(mom picked up the phone)"; return; }
    sw("up0", "images/bar_" + pad2(Math.floor(upGot * 20 / upSize)) + ".gif");
    f.ust.value = "Uploading " + Math.floor(upGot * 100 / upSize) + "%";
    f.urt.value = (Math.round(9 * (0.5 + Math.random())) / 10) + " KB/s";
    f.utl.value = mmss((upSize - upGot) / 900);
  }
}
function clearFinished() {
  setCookie("snapdl", "", -1);
  location.href = "transfer.html";
}
function writeDownloads() {
  var c = getCookie("snapdl"), ids = c == "" ? new Array() : c.split("."), i, out = "", fo = "<FONT FACE=\\"Arial, Helvetica\\" SIZE=1>";
  for (i = 0; i < ids.length; i++) {
    var n = parseInt(ids[i]);
    if (!isNaN(n) && n >= 0 && n < CAT.length) D[D.length] = new Dl(n);
  }
  if (D.length == 0) {
    out = "<TR BGCOLOR=\\"#000000\\"><TD COLSPAN=6>" + fo + "<BR>&nbsp; No downloads yet. Go to the " +
      "<A HREF=\\"search.html\\">Search</A> tab (or browse a friend on your <A HREF=\\"hotlist.html\\">Hot List</A>), " +
      "tick some songs and click <B>Get Selected Song(s)</B>.<BR>&nbsp;</FONT></TD></TR>";
  }
  for (i = 0; i < D.length; i++) {
    var r = CAT[D[i].row];
    out += "<TR BGCOLOR=\\"" + (i % 2 ? "#111111" : "#000000") + "\\">" +
      "<TD>" + fo + r[2] + "</FONT><BR>" + fo + "<FONT COLOR=\\"#999999\\">" + commas(r[3]) + " bytes</FONT></FONT></TD>" +
      "<TD><INPUT TYPE=TEXT NAME=\\"st" + i + "\\" SIZE=17 VALUE=\\"Queued\\" onFocus=\\"this.blur()\\"></TD>" +
      "<TD><IMG SRC=\\"images/bar_00.gif\\" WIDTH=100 HEIGHT=11 NAME=\\"p" + i + "\\"></TD>" +
      "<TD><INPUT TYPE=TEXT NAME=\\"rt" + i + "\\" SIZE=8 VALUE=\\"\\" onFocus=\\"this.blur()\\"></TD>" +
      "<TD><INPUT TYPE=TEXT NAME=\\"tl" + i + "\\" SIZE=6 VALUE=\\"\\" onFocus=\\"this.blur()\\"></TD>" +
      "<TD>" + fo + USERS[r[7]] + "<BR><FONT COLOR=\\"#999999\\">" + CONN[r[8]] + "</FONT></FONT></TD></TR>";
  }
  document.write(out);
}
// -->
</SCRIPT>'''
    cols = ['Filename', 'State', 'Progress', 'Rate', 'Time Left', 'User']
    body = '''<FORM NAME="xf" onSubmit="return false">
%s
<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=1 WIDTH=620>
%s
<SCRIPT LANGUAGE="JavaScript">
<!--
writeDownloads();
// -->
</SCRIPT>
</TABLE>
<INPUT TYPE=BUTTON VALUE="Clear Finished" onClick="clearFinished()">
<INPUT TYPE=BUTTON VALUE="Cancel" onClick="alert('Cancelling is for quitters. (Click Clear Finished to start over.)')">
<INPUT TYPE=BUTTON VALUE="Play" onClick="alert('Launching your MP3 player... it is loading skins. Please wait 4-6 minutes.')">
<INPUT TYPE=BUTTON VALUE="Open Folder" onClick="alert('C:\\\\My Documents\\\\My Music\\\\\\n\\n(Your hard drive is 97%% full.)')">
<P>%s
<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=1 WIDTH=620>
%s
<TR BGCOLOR="#000000"><TD>%s</TD><TD><INPUT TYPE=TEXT NAME="ust" SIZE=17 VALUE="Connecting..." onFocus="this.blur()"></TD><TD><IMG SRC="images/bar_00.gif" WIDTH=100 HEIGHT=11 NAME="up0"></TD><TD><INPUT TYPE=TEXT NAME="urt" SIZE=8 onFocus="this.blur()"></TD><TD><INPUT TYPE=TEXT NAME="utl" SIZE=6 onFocus="this.blur()"></TD><TD>%s</TD></TR>
<TR BGCOLOR="#111111"><TD>%s</TD><TD><INPUT TYPE=TEXT SIZE=17 VALUE="Complete" onFocus="this.blur()"></TD><TD><IMG SRC="images/bar_20.gif" WIDTH=100 HEIGHT=11></TD><TD><INPUT TYPE=TEXT SIZE=8 onFocus="this.blur()"></TD><TD><INPUT TYPE=TEXT SIZE=6 VALUE="0:00" onFocus="this.blur()"></TD><TD>%s</TD></TR>
<TR BGCOLOR="#000000"><TD>%s</TD><TD><INPUT TYPE=TEXT SIZE=17 VALUE="Queued (3 ahead)" onFocus="this.blur()"></TD><TD><IMG SRC="images/bar_00.gif" WIDTH=100 HEIGHT=11></TD><TD><INPUT TYPE=TEXT SIZE=8 onFocus="this.blur()"></TD><TD><INPUT TYPE=TEXT SIZE=6 onFocus="this.blur()"></TD><TD>%s</TD></TR>
</TABLE>
</FORM>''' % (
        f('Downloads', 2, '#FFFFFF', True), grid_head(cols), f('Uploads', 2, '#FFFFFF', True), grid_head(cols),
        f('Snapster legal disclaimer.mp3', 1), f('DialUpDiva4eva<BR><FONT COLOR="#999999">28.8</FONT>', 1),
        f('Me humming the dial-up sound.mp3', 1), f('xXdarkangelXx<BR><FONT COLOR="#999999">56K</FONT>', 1),
        f('Grandma - Happy Birthday voicemail.mp3', 1), f('newbie_ned<BR><FONT COLOR="#999999">Unknown</FONT>', 1))
    client_page('transfer.html', 'transfer', 'Transfer', body, head=transfer_js, catalog=True,
                onload='setTimeout(\'step()\', 600)')

    # ---------------------------------------------------------------- hot list
    counts = {}
    for r in CAT:
        counts[r['user']] = counts.get(r['user'], 0) + 1
    rows = []
    for i, (u, on, note) in enumerate(data.HOTLIST):
        rows.append('<TR BGCOLOR="%s"><TD><IMG SRC="images/user_%s.gif" WIDTH=16 HEIGHT=16 ALT="%s"></TD>'
                    '<TD>%s</TD><TD>%s</TD><TD>%s</TD><TD ALIGN=RIGHT>%s</TD><TD>%s</TD><TD NOWRAP>%s</TD></TR>' % (
                        '#111111' if i % 2 else '#000000', 'on' if on else 'off', 'online' if on else 'offline',
                        f('<B>%s</B>' % esc(u), 1, '#FFFFFF' if on else '#777777'),
                        f('Online' if on else 'Offline', 1, '#66CC66' if on else '#777777'),
                        f('<IMG SRC="images/dot_%s.gif" WIDTH=10 HEIGHT=10> %s' % (dot_for(data.CONN.index(CONN_OF[u])),
                                                                                 CONN_OF[u]), 1),
                        f(str(counts.get(u, 0)) if on else '-', 1), f('<I>%s</I>' % esc(note), 1, '#AAAAAA'),
                        f('<A HREF="browse_%s.html">Browse</A> | <A HREF="javascript:msg(\'%s\', %s)">Message</A>'
                          % (data.slug(u), u, 'true' if on else 'false'), 1)))
    hot_js = '''<SCRIPT LANGUAGE="JavaScript">
<!--
function msg(u, on) {
  if (!on) { alert(u + " is offline. Your message will be delivered never."); return; }
  var t = prompt("Send instant message to " + u + ":", "hey do u have any ska");
  if (t != null && t != "") alert("Message sent to " + u + ".\\n\\n" + u + " replies: \\"brb\\"");
}
function addUser(f) {
  var u = f.who.value;
  if (u == "") { alert("Type a screen name first."); return false; }
  alert(u + " has been added to your Hot List.\\n(They are offline. They are always offline. Some people are like that.)");
  f.who.value = "";
  return false;
}
// -->
</SCRIPT>'''
    body = panel('Hot List (%d of %d online)' % (len(online), len(data.HOTLIST)),
                 '<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=1 WIDTH="100%%">%s%s</TABLE>' % (
                     grid_head(['', 'User', 'Status', 'Connection', 'Files', 'Note', '']), '\n'.join(rows))) + \
        '<P><FORM NAME="add" onSubmit="return addUser(this)">%s <INPUT TYPE=TEXT NAME="who" SIZE=20> ' \
        '<INPUT TYPE=SUBMIT VALUE="Add User"></FORM>' % f('Add to Hot List:', 1)
    client_page('hotlist.html', 'hotlist', 'Hot List', body, head=hot_js)

    # ---------------------------------------------------------------- browse pages
    for u, on, note in data.HOTLIST:
        if not on:
            inner = ('<P>' + f('<B>Could not browse %s.</B>' % esc(u), 2, '#FF6666') + '<BR>' +
                     f('The user is not online. Note on your Hot List: <I>%s</I>.<P>Try again later, or '
                       'go back to your <A HREF="hotlist.html">Hot List</A>.' % esc(note), 2))
        else:
            mine = sorted([r for r in CAT if r['user'] == u], key=lambda r: (r['artist'], r['title']))
            trs = []
            for i, r in enumerate(mine):
                trs.append('<TR BGCOLOR="%s"><TD><INPUT TYPE=CHECKBOX NAME="c%d" VALUE="%d"></TD><TD>%s</TD>'
                           '<TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD>'
                           '<TD ALIGN=RIGHT>%s</TD></TR>' % (
                               '#111111' if i % 2 else '#000000', i, r['id'],
                               f('<IMG SRC="images/mp3.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE> ' + esc(r['file']), 1),
                               f(commas(r['size']), 1), f(str(r['bitrate']), 1), f(str(r['freq']), 1),
                               f(data.fmt_len(r['secs']), 1)))
            inner = ('<FORM NAME="res" onSubmit="return getSelected(this)">' +
                     f('%d files shared &middot; <IMG SRC="images/dot_%s.gif" WIDTH=10 HEIGHT=10> %s &middot; <I>%s</I>'
                       % (len(mine), dot_for(data.CONN.index(CONN_OF[u])), CONN_OF[u], esc(note)), 1) +
                     '<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=1 WIDTH="100%%">%s%s</TABLE>' % (
                         grid_head(['', 'Filename', 'Filesize', 'Bitrate', 'Freq', 'Length']), '\n'.join(trs)) +
                     '<P><INPUT TYPE=SUBMIT VALUE="Get Selected Song(s)"> '
                     '<INPUT TYPE=BUTTON VALUE="Select All" onClick="selAll(this.form, true)"> '
                     '<INPUT TYPE=BUTTON VALUE="Back to Hot List" onClick="location.href=\'hotlist.html\'"></FORM>')
        body = panel('Browsing: %s' % esc(u), inner)
        client_page('browse_%s.html' % data.slug(u), 'hotlist', 'Browse %s' % u, body)

    # ---------------------------------------------------------------- library
    trs = []
    root, folders = data.LIBRARY[0]

    def tree(*parts):
        return ''.join('<IMG SRC="images/tree_%s.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE>' % x for x in parts)
    trs.append('<TR><TD COLSPAN=4 NOWRAP><IMG SRC="images/folder_open.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE> %s</TD></TR>'
               % f('<B>%s</B>' % esc(root), 1, '#FFFFFF'))
    for fi, (name, files) in enumerate(folders):
        last_f = fi == len(folders) - 1
        trs.append('<TR><TD COLSPAN=4 NOWRAP>%s<IMG SRC="images/folder_open.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE> %s</TD></TR>'
                   % (tree('l' if last_f else 't'), f('<B>%s</B> (%d)' % (esc(name), len(files)), 1, '#FFFFCC')))
        for j, (fn, br, secs) in enumerate(files):
            size = int(br * 1000 / 8 * secs) + 128
            trs.append('<TR><TD NOWRAP>%s%s<IMG SRC="images/mp3.gif" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE> %s</TD>'
                       '<TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD></TR>' % (
                           tree('blank' if last_f else 'i', 'l' if j == len(files) - 1 else 't'),
                           '', f(esc(fn), 1), f(commas(size), 1), f('%d kbps' % br, 1), f(data.fmt_len(secs), 1)))
    lib_js = '''<SCRIPT LANGUAGE="JavaScript">
<!--
function lib(b) {
  var m = new Array();
  m["add"] = "Add Folder\\n\\nPlease choose a folder. Any folder. Except C:\\\\WINDOWS. Please not C:\\\\WINDOWS.";
  m["rescan"] = "Rescanning... found 21 MP3s, 3 WAVs, and a file called 'homework_final_really.doc'.\\nOnly MP3s are shared. Your homework is safe.";
  m["play"] = "Now playing: Snapster legal disclaimer.mp3\\n\\n(It is 94 seconds of Gary reading the Terms of Use.)";
  m["burn"] = "Burn to CD\\n\\nYour 2x CD-R drive estimates 74 minutes and 3 coasters.\\nDo not move the mouse. Do not breathe.";
  m["remove"] = "Are you sure? Removing files makes you a leech.\\nNobody likes a leech. (Not removed.)";
  alert(m[b]);
}
// -->
</SCRIPT>'''
    body = panel('My Shared Library &mdash; %d songs' % shared_count(),
                 '<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH="100%%">%s%s</TABLE>' % (
                     '<TR BGCOLOR="#555555"><TD>%s</TD><TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD><TD ALIGN=RIGHT>%s</TD></TR>'
                     % tuple(f(c, 1, '#FFFFFF', True) for c in ('Name', 'Size', 'Bitrate', 'Length')),
                     '\n'.join(trs))) + '''<P><FORM onSubmit="return false">
<INPUT TYPE=BUTTON VALUE="Add Folder..." onClick="lib('add')">
<INPUT TYPE=BUTTON VALUE="Remove" onClick="lib('remove')">
<INPUT TYPE=BUTTON VALUE="Rescan" onClick="lib('rescan')">
<INPUT TYPE=BUTTON VALUE="Play" onClick="lib('play')">
<INPUT TYPE=BUTTON VALUE="Burn to CD" onClick="lib('burn')">
</FORM>'''
    client_page('library.html', 'library', 'Library', body, head=lib_js)

    # ---------------------------------------------------------------- discover
    picks = [('Ska', 'Checkerboard Tuxedo Revue', 'Trombone Emergency', 'you have ska in your library. Of course you do.'),
             ('Trip-Hop', 'Porthole Mood', 'Sad Robot Lounge', 'perfect for staring at a screensaver at 3 AM.'),
             ('Swing', 'The Cherry Lounge Hepcats', 'Martini Emergency', 'your khakis are ready.'),
             ('Big Beat', 'The Chemistry Set Brothers', 'Lab Coat Rave', 'safety goggles recommended.'),
             ('Emo', 'Cardigan Feelings Society', 'Letter I Never Mailed', 'you seem like you have feelings.'),
             ('Lounge', 'Tiki Bar Cosmonauts', 'Volcano Highball', 'space-age bachelor pad not included.')]
    items = ''.join('<TR BGCOLOR="%s"><TD>%s</TD><TD>%s</TD><TD>%s</TD></TR>' % (
        '#111111' if i % 2 else '#000000', f(g, 1, '#99CCCC'),
        f('<A HREF="search.html?artist=%s&amp;title=%s"><B>%s</B> &mdash; %s</A>' % (
            a.replace(' ', '+').replace('&', '%26'), t.split(' ')[0], esc(a), esc(t)), 1), f(w, 1, '#AAAAAA'))
        for i, (g, a, t, w) in enumerate(picks))
    body = panel('Discover &mdash; Snappy\'s Picks', f(
        'Snappy has looked at your library (sorry) and thinks you\'ll like these. Click one to search for it.', 1) +
        '<P><TABLE BORDER=0 CELLPADDING=3 CELLSPACING=1 WIDTH="100%%">%s%s</TABLE>' % (
            grid_head(['Genre', 'Song', 'Why']), items)) + '<P>' + panel('New Artists', f(
                'Fresh unsigned bands from the <A HREF="artists.html">New Artist Program</A>: Garage Door Opener, '
                'The Sandwich Theory, Cul-de-Sac Symphony, DJ Screensaver, Mildly Annoyed Hornets.', 1))
    client_page('discover.html', 'discover', 'Discover', body)

    # ---------------------------------------------------------------- chat
    chans = ''.join('<TR><TD NOWRAP>%s</TD><TD ALIGN=RIGHT>%s</TD></TR>' % (
        f('<A HREF="chat.html?channel=%s">#%s</A>' % (c, c), 1), f(str(len(data.CHAT[c]['users']) * 4 + i), 1, '#999999'))
        for i, (c, topic) in enumerate(data.CHANNELS))
    lobby = data.CHAT['Lobby']
    chat_data = {}
    for c, topic in data.CHANNELS:
        d = data.CHAT[c]
        chat_data[c] = {'topic': topic, 'users': d['users'], 'log': d['log'], 'script': d['script']}
    chat_js = '''<SCRIPT LANGUAGE="JavaScript">
<!--
var ME = %s;
var CH = new Array();
%s
var chan = getArg("channel");
if (chan.charAt(0) == "#") chan = chan.substring(1);
if (!CH[chan]) chan = "Lobby";
var C = CH[chan], next = 0;
function addLine(s) {
  var t = document.forms["chat"].log;
  t.value += s + "\\n";
  if (t.scrollHeight) t.scrollTop = t.scrollHeight;
}
function more() {
  if (next < C[3].length) {
    addLine(C[3][next++]);
    setTimeout("more()", 2500 + Math.floor(Math.random() * 3500));
  }
}
function startChat() {
  var t = document.forms["chat"].log;
  if (chan != "Lobby") t.value = C[2].join("\\n") + "\\n";
  addLine("*** " + ME + " has joined #" + chan);
  setTimeout("more()", 2000);
}
function send(f) {
  var s = f.say.value, low = s.toLowerCase();
  if (s == "") return false;
  f.say.value = "";
  if (low.indexOf("/join ") == 0) {
    var j = s.substring(6);
    if (j.charAt(0) == "#") j = j.substring(1);
    if (CH[j]) { location.href = "chat.html?channel=" + j; return false; }
    addLine("*** No such channel: #" + j);
    return false;
  }
  if (low.indexOf("/me ") == 0) { addLine("* " + ME + " " + s.substring(4)); return false; }
  if (low == "/help") { addLine("*** Commands: /join #channel, /me action, /help, /part"); return false; }
  if (low == "/part" || low == "/quit") { addLine("*** " + ME + " has left #" + chan); location.href = "client.html"; return false; }
  addLine("<" + ME + "> " + s);
  if (low.indexOf("snappy") != -1) setTimeout("addLine('<Snappy_Bot> snap snap! (that means hi)')", 1500);
  else if (low.indexOf("a/s/l") != -1) setTimeout("addLine('<Snappy_Bot> Please do not ask a/s/l. Snappy is 3, male, and from a tank.')", 1500);
  return false;
}
function writeHeader() {
  document.write("<FONT FACE=\\"Arial, Helvetica\\" SIZE=2 COLOR=\\"#FFFFFF\\"><B>#" + chan + "</B></FONT> " +
    "<FONT FACE=\\"Arial, Helvetica\\" SIZE=1 COLOR=\\"#999999\\">" + C[0] + "</FONT>");
}
function writeUsers() {
  var u = C[1], out = "<SELECT NAME=\\"who\\" SIZE=16 onChange=\\"whois(this)\\">";
  for (var i = 0; i < u.length; i++) out += "<OPTION>" + u[i];
  document.write(out + "</SELECT>");
}
function whois(s) {
  var u = s.options[s.selectedIndex].text;
  if (u == ME) alert("That's you! Looking good.");
  else alert("Whois " + u + ":\\nConnection: who knows\\nIdle: 0 sec\\nSharing: plenty\\n\\n(Add them from the Hot List tab.)");
}
// -->
</SCRIPT>''' % (js(data.ME), '\n'.join('CH[%s] = new Array(%s, %s, %s, %s);' % (
        js(c), js(v['topic']), js(v['users']), js(v['log']), js(v['script'])) for c, v in chat_data.items()))
    body = '''<FORM NAME="chat" onSubmit="return send(this)">
<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH=620><TR>
<TD VALIGN=TOP WIDTH=110>%s</TD><TD WIDTH=8>&nbsp;</TD>
<TD VALIGN=TOP>
<SCRIPT LANGUAGE="JavaScript">
<!--
writeHeader();
// -->
</SCRIPT><BR>
<TEXTAREA NAME="log" ROWS=18 COLS=46 WRAP=VIRTUAL>%s
</TEXTAREA><BR>
<INPUT TYPE=TEXT NAME="say" SIZE=38> <INPUT TYPE=SUBMIT VALUE="Send">
</TD><TD WIDTH=8>&nbsp;</TD>
<TD VALIGN=TOP>%s<BR>
<SCRIPT LANGUAGE="JavaScript">
<!--
writeUsers();
// -->
</SCRIPT>
</TD></TR></TABLE>
</FORM>''' % (
        panel('Channels', '<TABLE BORDER=0 CELLPADDING=1 CELLSPACING=0 WIDTH="100%%">%s</TABLE>' % chans +
              f('<P>Type <B>/join #name</B> to switch, <B>/me</B> to emote.', 1, '#999999')),
        esc('\n'.join(lobby['log'])), f('Users', 1, '#FFFFFF', True))
    client_page('chat.html', 'chat', 'Chat', body, head=chat_js, onload='startChat()')


def main():
    build_web()
    build_client()
    midi.jingle(os.path.join(SITE, 'jingle.mid'))
    print('wrote %d pages + jingle.mid; catalog has %d shared files' % (len(PAGES), len(CAT)))


if __name__ == '__main__':
    main()
