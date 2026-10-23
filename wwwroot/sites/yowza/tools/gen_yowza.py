#!/usr/bin/env python3
"""Generates the whole static Yowza! site from tools/yowza_data.py.

    python3 tools/gen_yowza.py

Writes index.html, dir/**/index.html (one page per category), the search index
yz_index.js and the service pages. Every URL is relative, so the site works at
http://yowza.localhost:PORT/ and at http://localhost:PORT/sites/yowza/ alike.
"""
import html, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import yowza_data as Y  # noqa: E402

SITE = 'yowza'
RING = [k for k, _, _ in Y.WEB1999]
TODAY = 'Tuesday October 12, 1999'


def esc(s):
    return html.escape(s, quote=True)


def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='latin-1', errors='xmlcharrefreplace') as f:
        f.write(text)


def up(rel):
    """prefix that climbs from the page at rel back to the site root"""
    return '../' * rel.count('/')


def cat_url(path, pre):
    return '%sdir/%s/index.html' % (pre, path)


def site_href(s, pre):
    """where a listing points: a 1999-Web site, or the invented homepage on AltaVisor's web"""
    if s['web1999']:
        return '%s../%s/index.html' % (pre, s['web1999'])
    return '%s../altavisor/web/%s/index.html' % (pre, s['host'])


def ring(pre):
    i = RING.index(SITE)
    prv, nxt = RING[i - 1], RING[(i + 1) % len(RING)]
    arr = ','.join("'%s'" % r for r in RING)
    return '''<P><CENTER>
<TABLE BORDER=2 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#C0C0C0"><TR><TD ALIGN=CENTER>
<FONT FACE="Arial, Helvetica" SIZE=1>
<A HREF="%(pre)s../%(prv)s/index.html">&lt;&lt; Prev</A> |
<A HREF="%(pre)s../../web1999/index.html" onClick="var r=new Array(%(arr)s); location.href='%(pre)s../'+r[Math.floor(Math.random()*r.length)]+'/index.html'; return false;">Random</A> |
<B><A HREF="%(pre)s../../web1999/index.html">The 1999 Web Ring</A></B> &middot; Yowza! is site %(n)d of %(tot)d |
<A HREF="%(pre)s../%(nxt)s/index.html">Next &gt;&gt;</A>
</FONT></TD></TR></TABLE>
</CENTER>
''' % dict(pre=pre, prv=prv, nxt=nxt, arr=arr, n=i + 1, tot=len(RING))


def page(title, body, pre, onload='', desc='Yowza! - a hand-sorted guide to the World Wide Web.'):
    return '''<HTML>
<HEAD>
<TITLE>%s</TITLE>
<META NAME="description" CONTENT="%s">
</HEAD>
<BODY BGCOLOR="#FFFFFF" TEXT="#000000" LINK="#0000CC" VLINK="#551A8B" ALINK="#FF0000"%s>
%s
%s</BODY>
</HTML>
''' % (esc(title), esc(desc), (' onLoad="%s"' % onload) if onload else '', body, ring(pre))


def inner_header(pre, crumbs, here_title):
    """the small-logo header used on every page below the home page"""
    trail = ''.join('<A HREF="%s">%s</A> &gt; ' % (u, esc(t)) for u, t in crumbs)
    return '''<TABLE BORDER=0 WIDTH="100%%" CELLSPACING=0 CELLPADDING=0>
<TR><TD WIDTH="1%%"><A HREF="%(pre)sindex.html"><IMG SRC="%(pre)simages/yowza_sm.gif" ALT="Yowza!" BORDER=0 WIDTH=147 HEIGHT=31></A></TD>
<TD><TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0 WIDTH="100%%"><TR>
<TD VALIGN=BOTTOM><FONT FACE=arial SIZE=-1><A HREF="%(pre)smy.html">Personalize</A></FONT></TD>
<TD ALIGN=RIGHT VALIGN=BOTTOM><FONT FACE=arial SIZE=-1><A HREF="%(pre)shelp.html">Help</A> - <A HREF="%(pre)smail.html">Check Email</A></FONT></TD>
</TR></TABLE><HR SIZE=1 NOSHADE></TD></TR></TABLE>
<TABLE BORDER=0 WIDTH="100%%" CELLSPACING=0 CELLPADDING=3>
<TR><TD><FONT FACE="arial,helvetica" SIZE=-1><A HREF="%(pre)sindex.html">Home</A> &gt; %(trail)s</FONT></TD></TR>
<TR><TD WIDTH="80%%" BGCOLOR="#A0B8C8"><NOBR><B><FONT FACE="arial,helvetica">%(title)s</FONT></B></NOBR></TD></TR>
</TABLE>
''' % dict(pre=pre, trail=trail, title=esc(here_title))


def inner_footer(pre, cat=None):
    sug = '%ssuggest.html' % pre + ('?c=%s' % cat if cat else '')
    return '''<P><HR SIZE=0>
<CENTER><FONT SIZE=-1><I>Copyright &copy; 1994-99 Yowza! Inc. All Rights Reserved.</I> -
<A HREF="%(pre)sinfo.html">Company Information</A> -
<A HREF="%(sug)s">Suggest a Site</A> -
<A HREF="%(pre)shelp.html">FAQ</A></FONT></CENTER>
''' % dict(pre=pre, sug=sug)


# ================================================================ data prep
CATS, ORDER = Y.parse()


def children(path):
    pref = path + '/'
    return [p for p in ORDER if p.startswith(pref) and '/' not in p[len(pref):]]


def subtree_sites(path):
    out = []
    for p in ORDER:
        if p == path or p.startswith(path + '/'):
            out.extend(CATS[p]['sites'])
    return out


def count(path):
    return len(subtree_sites(path))


def has_new(path):
    return any(s['new'] for s in subtree_sites(path))


def crumbs_for(path, pre):
    segs = path.split('/')
    return [(cat_url('/'.join(segs[:i]), pre), CATS['/'.join(segs[:i])]['title']) for i in range(1, len(segs))]


def sort_key(t):
    return t.lower().lstrip('"\'')


# ================================================================ category pages
def site_li(s, pre):
    icons = ''
    if s['cool']:
        icons += ' <IMG SRC="%simages/cool.gif" WIDTH=22 HEIGHT=11 ALT="[cool]" BORDER=0>' % pre
    if s['new']:
        icons += ' <IMG SRC="%simages/new2.gif" WIDTH=28 HEIGHT=11 ALT="[new]">' % pre
    return '<LI><A HREF="%s">%s</A>%s - %s\n' % (site_href(s, pre), esc(s['name']), icons, esc(s['desc']))


def two_col(items):
    half = (len(items) + 1) // 2
    cols = [items[:half], items[half:]]
    out = '<TABLE BORDER=0 CELLPADDING=0 WIDTH="80%"><TR>\n'
    for c in cols:
        out += '<TD VALIGN=TOP WIDTH="50%%"><UL>\n%s</UL></TD>\n' % ''.join(c)
    return out + '</TR></TABLE>\n'


def category_page(path):
    rel = 'dir/%s/index.html' % path
    pre = up(rel)
    c = CATS[path]
    body = inner_header(pre, crumbs_for(path, pre), c['title'])
    body += '''<P>
<FORM NAME="sf" METHOD=GET ACTION="%(pre)ssearch.html">
<TABLE BORDER=0 WIDTH="100%%" CELLPADDING=8 CELLSPACING=0>
<TR><TD BGCOLOR="#DDDDDD">
<INPUT SIZE=24 NAME=p> <INPUT TYPE=submit VALUE=Search>
<SELECT NAME=c>
<OPTION SELECTED VALUE="">all of Yowza!
<OPTION VALUE="%(path)s">just this category
</SELECT>
</TD></TR></TABLE></FORM>
''' % dict(pre=pre, path=path)
    if '/' not in path:
        body += '''<TABLE BORDER=0 CELLPADDING=0 WIDTH="80%%"><TR><TD><UL>
<LI><FONT SIZE=-1><A HREF="%(pre)sservices/chat.html"><B>Join a Chat</B></A></FONT>, <FONT SIZE=-1><A HREF="%(pre)sservices/clubs.html"><B>Start a Club</B></A></FONT>
<LI><FONT SIZE=-1><A HREF="%(pre)sservices/events.html"><B>Live Net Events</B></A></FONT>, <FONT SIZE=-1><A HREF="%(pre)s../cnm/index.html"><B>Headline News</B></A></FONT>
</UL></TD></TR></TABLE>
''' % dict(pre=pre)
    subs = []
    for ch in children(path):
        n = count(ch)
        if n == 0 and CATS[ch]['xrefs']:
            # an empty shelf that only points elsewhere is shown as a cross-link
            tgt = CATS[ch]['xrefs'][0] if len(CATS[ch]['xrefs']) == 1 else ch
            subs.append((sort_key(CATS[ch]['title']), '<LI><A HREF="%s"><B>%s@</B></A>\n' % (cat_url(tgt, pre), esc(CATS[ch]['title']))))
            continue
        tag = ' <IMG SRC="%simages/new2.gif" WIDTH=28 HEIGHT=11 ALT=" [new]">' % pre if has_new(ch) else ''
        subs.append((sort_key(CATS[ch]['title']), '<LI><A HREF="%s"><B>%s</B></A> <I>(%d)</I>%s\n' % (
            cat_url(ch, pre), esc(CATS[ch]['title']), n, tag)))
    for x in c['xrefs']:
        subs.append((sort_key(CATS[x]['title']), '<LI><A HREF="%s"><B>%s@</B></A>\n' % (cat_url(x, pre), esc(CATS[x]['title']))))
    subs.sort()
    if subs:
        body += '<HR SIZE=0>\n' + two_col([s for _, s in subs])
    sites = sorted(c['sites'], key=lambda s: sort_key(s['name']))
    if sites:
        body += '<HR SIZE=0>\n<UL>\n' + ''.join(site_li(s, pre) for s in sites) + '</UL>\n'
    if not subs and not sites:
        body += '<P>There are no sites in this category yet. <A HREF="%ssuggest.html?c=%s">Suggest one!</A>\n' % (pre, path)
    body += inner_footer(pre, path)
    kids = [CATS[ch]['title'] for ch in children(path)][:5]
    names = [x['name'] for x in sites][:3]
    desc = 'Yowza! directory: %s. ' % ' > '.join(CATS['/'.join(path.split('/')[:i])]['title'] for i in range(1, len(path.split('/')) + 1))
    if kids:
        desc += 'Categories include %s. ' % ', '.join(kids)
    if names:
        desc += '%d site%s listed, including %s.' % (len(sites), '' if len(sites) == 1 else 's', ', '.join(names))
    write(rel, page('Yowza! - ' + ' : '.join(CATS['/'.join(path.split('/')[:i])]['title']
                                              for i in range(1, len(path.split('/')) + 1)), body, pre, desc=desc))


# ================================================================ search index (JS)
def js_str(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'").replace('</', '<\\/') + "'"


def search_index():
    lines = ['// Yowza! directory index for search.html - generated by tools/gen_yowza.py',
             '// C: path|title|count    S: name|description|category|href|flags', 'var C = new Array(']
    lines.append(',\n'.join(js_str('%s|%s|%d' % (p, CATS[p]['title'], count(p))) for p in sorted(ORDER)))
    lines.append(');\nvar S = new Array(')
    rows = []
    for p in ORDER:
        for s in CATS[p]['sites']:
            fl = ('c' if s['cool'] else '') + ('n' if s['new'] else '')
            rows.append(js_str('%s|%s|%s|%s|%s' % (s['name'], s['desc'], p, site_href(s, ''), fl)))
    lines.append(',\n'.join(rows))
    lines.append(');\nvar T = new Array();')
    for p in sorted(ORDER):
        lines.append('T[%s] = %s;' % (js_str(p), js_str(CATS[p]['title'])))
    write('yz_index.js', '\n'.join(lines) + '\n')


SEARCH_JS = r'''<SCRIPT LANGUAGE="JavaScript" SRC="yz_index.js"></SCRIPT>
<SCRIPT LANGUAGE="JavaScript">
<!--
function getArg(name) {
  var q = location.search.substring(1).split('&');
  for (var i = 0; i < q.length; i++) {
    var kv = q[i].split('=');
    if (kv[0] == name && kv.length > 1) return unescape(kv[1].replace(/\+/g, ' '));
  }
  return '';
}
function h(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
function words(s) {
  var w = s.toLowerCase().replace(/[^a-z0-9\-\.' ]/g, ' ').split(' '), out = new Array();
  for (var i = 0; i < w.length; i++) if (w[i].length > 1 && w[i] != 'and' && w[i] != 'the' && w[i] != 'of') out[out.length] = w[i];
  return out;
}
function hasAll(text, ws) {
  text = ' ' + text.toLowerCase().replace(/[^a-z0-9\-\.']/g, ' ') + ' ';
  for (var i = 0; i < ws.length; i++) if (text.indexOf(' ' + ws[i]) < 0) return false;
  return true;
}
function bold(text, ws) {
  var out = h(text);
  for (var i = 0; i < ws.length; i++) {
    if (ws[i].length < 2) continue;
    var re = new RegExp('(^|[^a-zA-Z0-9])(' + ws[i].replace(/[\.\-]/g, '\\$&') + '[a-z]*)', 'gi');
    out = out.replace(re, '$1<B>$2</B>');
  }
  return out;
}
function crumb(path, ws) {
  var segs = path.split('/'), out = '';
  for (var i = 1; i <= segs.length; i++) {
    var p = segs.slice(0, i).join('/');
    out += (i > 1 ? ' &gt; ' : '') + bold(T[p], ws);
  }
  return out;
}
var p = getArg('p'), c = getArg('c'), b = parseInt(getArg('b')) || 1, mode = getArg('h');
var ws = words(p);
var cm = new Array(), sm = new Array();
if (ws.length > 0) {
  for (var i = 0; i < C.length; i++) {
    var f = C[i].split('|');
    if (c != '' && f[0] != c && f[0].indexOf(c + '/') != 0) continue;
    if (hasAll(f[1] + ' ' + f[0].replace(/_/g, ' '), ws) && hasAll(f[1], ws.slice(ws.length - 1))) cm[cm.length] = f;
  }
  for (var i = 0; i < S.length; i++) {
    var f = S[i].split('|');
    if (c != '' && f[2] != c && f[2].indexOf(c + '/') != 0) continue;
    if (hasAll(f[0] + ' ' + f[1] + ' ' + T[f[2]], ws)) sm[sm.length] = f;
  }
}
function tabs() {
  var q = escape(p);
  var t = '<P><TABLE BGCOLOR="black" BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH="100%"><TR><TD><TABLE BORDER=0 CELLPADDING=2 CELLSPACING=1 WIDTH="100%"><TR ALIGN=center BGCOLOR="#EEEEEE">';
  t += (mode == 's' ? '<TD WIDTH="20%"><FONT SIZE=-1 FACE=arial><A HREF="search.html?p=' + q + '&c=' + escape(c) + '">Categories</A></FONT></TD><TD BGCOLOR="#A0B8C8" WIDTH="20%"><FONT SIZE=-1 FACE=arial><B>Web Sites</B></FONT></TD>'
                    : '<TD BGCOLOR="#A0B8C8" WIDTH="20%"><FONT SIZE=-1 FACE=arial><B>Categories</B></FONT></TD><TD WIDTH="20%"><FONT SIZE=-1 FACE=arial><A HREF="search.html?h=s&p=' + q + '&c=' + escape(c) + '">Web Sites</A></FONT></TD>');
  t += '<TD WIDTH="20%"><FONT SIZE=-1 FACE=arial><A HREF="../altavisor/results.html?q=' + q + '">Web Pages</A></FONT></TD>';
  t += '<TD WIDTH="20%"><FONT SIZE=-1 FACE=arial><A HREF="../cnm/index.html">Related News</A></FONT></TD>';
  t += '<TD WIDTH="20%"><FONT SIZE=-1 FACE=arial><A HREF="services/events.html">Net Events</A></FONT></TD></TR></TABLE></TD></TR></TABLE><P>';
  return t;
}
function catUrl(path) { return 'dir/' + path + '/index.html'; }
function siteLi(f, showCat) {
  var s = '<LI><A HREF="' + f[3] + '">' + bold(f[0], ws) + '</A>';
  if (f[4].indexOf('c') >= 0) s += ' <IMG SRC="images/cool.gif" WIDTH=22 HEIGHT=11 ALT="[cool]">';
  if (f[4].indexOf('n') >= 0) s += ' <IMG SRC="images/new2.gif" WIDTH=28 HEIGHT=11 ALT="[new]">';
  s += ' - ' + bold(f[1], ws);
  if (showCat) s += '<BR><FONT SIZE=-1><A HREF="' + catUrl(f[2]) + '">' + crumb(f[2], ws) + '</A></FONT>';
  return s + '\n';
}
function pager(total, per) {
  if (total <= b + per - 1) return '';
  var n = b + per;
  return '<P><CENTER><FONT FACE=arial><A HREF="search.html?h=' + mode + '&p=' + escape(p) + '&c=' + escape(c) + '&b=' + n + '">Next ' + Math.min(per, total - n + 1) + ' Matches</A></FONT></CENTER>';
}
// -->
</SCRIPT>
'''

SEARCH_BODY = r'''<SCRIPT LANGUAGE="JavaScript">
<!--
document.sf.p.value = p;
var where = (c != '' ? ' in <B>' + h(T[c] || c) + '</B>' : '');
document.write('<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=2 WIDTH="100%"><TR><TD BGCOLOR="#A0B8C8"><FONT FACE=arial><B>Search Result</B></FONT>&nbsp;&nbsp;<FONT SIZE=-1 FACE=arial>Found <B>' + cm.length + '</B> categories and <B>' + sm.length + '</B> sites for <B>' + h(p) + '</B>' + where + '</FONT></TD></TR></TABLE>');
if (ws.length == 0) {
  document.write('<P>Please type a word or two in the box above and press <B>Search</B>. Yowza! will look through every category and every site our surfers have filed.');
} else if (cm.length == 0 && sm.length == 0) {
  document.write(tabs());
  document.write('<P><CENTER><B>Sorry, no matches were found containing <I>' + h(p) + '</I>.</B></CENTER><P>Yowza! looked through ' + C.length + ' categories and ' + S.length + ' sites, under every couch cushion. Some ideas:<UL>');
  document.write('<LI>Check your spelling. (We have all typed &quot;teh&quot;.)<LI>Try fewer or more general words.');
  document.write('<LI>Let <A HREF="../altavisor/results.html?q=' + escape(p) + '">AltaVisor</A> search the full text of millions of Web pages for <B>' + h(p) + '</B>.');
  document.write('<LI>Ask the butler: <A HREF="../askreeves/answer.html?ask=' + escape(p) + '">Ask Reeves</A> about <B>' + h(p) + '</B>.');
  document.write('<LI>Know a good site about it? <A HREF="suggest.html">Suggest a Site</A>.</UL>');
} else if (mode == 's' || cm.length == 0) {
  mode = 's';
  document.write(tabs());
  var per = 20, last = Math.min(sm.length, b + per - 1);
  document.write('<CENTER><FONT SIZE="+1"><B>Yowza! Site Matches &nbsp; <FONT SIZE="-1">(' + b + '&nbsp;-&nbsp;' + last + '&nbsp;of&nbsp;' + sm.length + ')</FONT></B></FONT></CENTER><P><UL>');
  for (var i = b - 1; i < last; i++) document.write(siteLi(sm[i], true));
  document.write('</UL>' + pager(sm.length, per));
} else {
  document.write(tabs());
  var per = 20, last = Math.min(cm.length, b + per - 1);
  document.write('<CENTER><FONT SIZE="+1"><B>Yowza! Category Matches &nbsp; <FONT SIZE="-1">(' + b + '&nbsp;-&nbsp;' + last + '&nbsp;of&nbsp;' + cm.length + ')</FONT></B></FONT></CENTER>');
  for (var i = b - 1; i < last; i++) document.write('<P><A HREF="' + catUrl(cm[i][0]) + '">' + crumb(cm[i][0], ws) + '</A>');
  document.write(pager(cm.length, per));
  if (sm.length > 0 && b == 1) {
    document.write('<P><HR SIZE=0><CENTER><FONT SIZE="+1"><B>Yowza! Site Matches &nbsp; <FONT SIZE="-1">(1&nbsp;-&nbsp;' + Math.min(sm.length, 10) + '&nbsp;of&nbsp;' + sm.length + ')</FONT></B></FONT></CENTER><P><UL>');
    for (var i = 0; i < Math.min(sm.length, 10); i++) document.write(siteLi(sm[i], true));
    document.write('</UL>');
    if (sm.length > 10) document.write('<CENTER><FONT FACE=arial><A HREF="search.html?h=s&p=' + escape(p) + '&c=' + escape(c) + '">More Site Matches</A></FONT></CENTER>');
  }
}
// -->
</SCRIPT>
<NOSCRIPT><P><B>Yowza! search needs JavaScript.</B> Please turn it on in your browser's preferences,
or browse the <A HREF="index.html">categories</A> by hand like it's 1994.</NOSCRIPT>
'''


def search_page():
    body = '''<TABLE BORDER=0 WIDTH="100%" CELLSPACING=0 CELLPADDING=0><TR><TD VALIGN=MIDDLE WIDTH="1%">
<A HREF="index.html"><IMG BORDER=0 HEIGHT=31 WIDTH=147 SRC="images/yowza_sm.gif" ALT="Yowza!"></A></TD>
<TD VALIGN=MIDDLE><TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0 WIDTH="100%"><TR>
<TD VALIGN=BOTTOM ALIGN=LEFT><FONT FACE=arial SIZE=-1><A HREF="my.html">Personalize</A></FONT></TD>
<TD ALIGN=RIGHT VALIGN=BOTTOM><FONT FACE=arial SIZE=-1><A HREF="help.html">Help</A> - <A HREF="mail.html">Check Email</A></FONT></TD>
</TR></TABLE><HR SIZE=1 NOSHADE></TD></TR></TABLE>
<FORM NAME="sf" METHOD=GET ACTION="search.html">
<TABLE BORDER=0 WIDTH="100%" CELLPADDING=6 CELLSPACING=0><TR><TD BGCOLOR="#DDDDDD">
<INPUT SIZE=30 NAME=p> <INPUT TYPE=submit VALUE=Search> <FONT SIZE=-1><A HREF="search_adv.html">advanced search</A></FONT>
</TD></TR></TABLE></FORM>
''' + SEARCH_BODY + inner_footer('')
    write('search.html', page('Yowza! Search Results', SEARCH_JS + body, ''))


def advanced_page():
    opts = ''.join('<OPTION VALUE="%s">%s\n' % (p, esc(t)) for p, t, _ in Y.TOP)
    body = inner_header('', [], 'Search Options') + '''<P>
<FORM NAME="sf" METHOD=GET ACTION="search.html">
<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH=600>
<TR><TD BGCOLOR="#DDDDDD" COLSPAN=2><INPUT SIZE=30 NAME=p> <INPUT TYPE=submit VALUE=Search> <FONT SIZE=-1><A HREF="help.html#search">help on search</A></FONT></TD></TR>
<TR><TD VALIGN=TOP WIDTH=300><FONT SIZE=-1>
<INPUT TYPE=radio NAME=h VALUE="" CHECKED> Yowza! Categories<BR>
<INPUT TYPE=radio NAME=h VALUE="s"> Yowza! Web Sites<BR>
</FONT></TD>
<TD VALIGN=TOP><FONT SIZE=-1>Look only in:<BR><SELECT NAME=c><OPTION VALUE="" SELECTED>all of Yowza!
''' + opts + '''</SELECT></FONT></TD></TR>
<TR><TD COLSPAN=2><FONT SIZE=-1>Every word you type must appear in the category name or the site's title and
description. Yowza! ignores little words like <I>the</I> and <I>of</I>, and matches the beginnings of words, so
<B>photo</B> also finds <B>photography</B>. Searching the full text of Web pages is a job for
<A HREF="../altavisor/index.html">AltaVisor</A>.</FONT></TD></TR>
</TABLE></FORM>
''' + inner_footer('')
    write('search_adv.html', page('Yowza! Search Options', body, ''))


# ================================================================ home page
AUCTION_ITEMS = ['Furry Talkers', 'Bean Bags', 'Pokey Monsters', 'Y2K kits']
NEWS = [
    ('Banks say they are 99.9% ready for Y2K', '../cnm/index.html'),
    ('Mars probe lost; engineers blame inches', '../cnm/index.html'),
    ('Baseball playoffs', '../cnm/index.html'), ('Hockey', '../cnm/index.html'),
]


def home_page():
    cats_html = ['', '']
    for i, (p, t, subs) in enumerate(Y.TOP):
        col = 0 if i < 7 else 1
        links = ',\n'.join('<A HREF="dir/%s/index.html">%s</A>' % (Y.HOME_LINKS[s], esc(s)) for s in subs)
        cats_html[col] += '<FONT SIZE=3 FACE=arial><A HREF="dir/%s/index.html"><B>%s</B></A></FONT><BR>%s...<BR><BR>' % (
            p, esc(t), links)
    for col in (0, 1):
        cats_html[col] = cats_html[col][:-8]
    news = ''.join('<TR><TD VALIGN=top><B>&#183;</B></TD><TD><FONT SIZE=-1><A HREF="%s">%s</A></FONT></TD></TR>\n' % (u, esc(t))
                   for t, u in NEWS[:2])
    news += '<TR><TD VALIGN=top><B>&#183;</B></TD><TD><FONT SIZE=-1><A HREF="../cnm/index.html">Baseball playoffs</A> - <A HREF="../cnm/index.html">Hockey</A></FONT></TD></TR>\n'
    auctions = ', '.join('<A HREF="../ubid/index.html">%s</A>' % esc(a) for a in AUCTION_ITEMS)
    rule = '<TABLE BORDER=0 CELLSPACING=0 WIDTH=600><TR><TD BGCOLOR="#6699CC"><IMG SRC="images/pixel.gif" WIDTH=1 HEIGHT=2></TD></TR></TABLE>\n'
    body = '''<CENTER>
<FORM NAME="sf" ACTION="search.html" METHOD=GET>
<MAP NAME="m">
<AREA SHAPE=rect COORDS="4,0,62,58" HREF="new.html" ALT="What's New">
<AREA SHAPE=rect COORDS="63,0,121,58" HREF="cool.html" ALT="What's Cool">
<AREA SHAPE=rect COORDS="420,0,478,58" HREF="my.html" ALT="My Yowza!">
<AREA SHAPE=rect COORDS="479,0,537,58" HREF="mail.html" ALT="Yowza! Mail">
<AREA SHAPE=rect COORDS="538,0,596,58" HREF="help.html" ALT="Help">
<AREA SHAPE=rect COORDS="125,0,417,58" HREF="index.html" ALT="Yowza!">
</MAP>
<IMG WIDTH=600 HEIGHT=59 BORDER=0 USEMAP="#m" SRC="images/yowza_main.gif" ALT="Yowza!"><BR>
<TABLE BORDER=0 CELLSPACING=0 CELLPADDING=4 WIDTH=600><TR>
<TD ALIGN=center WIDTH=160><A HREF="services/pager.html"><B>Yowza! Pager</B></A><BR><IMG SRC="images/new2.gif" HEIGHT=11 WIDTH=28> beep your buddies</TD>
<TD ALIGN=center><FONT FACE=arial SIZE=-1><A HREF="random.html"><B>Feeling lucky?</B></A><BR>try a <A HREF="random.html">Random Yowza! Link</A></FONT></TD>
<TD ALIGN=center WIDTH=160><A HREF="mail.html"><B>Yowza! Mail</B></A><BR>free email for life</TD></TR>
<TR><TD COLSPAN=3 ALIGN=center><INPUT SIZE=30 NAME=p>
<INPUT TYPE=submit VALUE=Search> <A HREF="search_adv.html">advanced search</A></TD></TR></TABLE>
<TABLE BORDER=0 CELLSPACING=0 CELLPADDING=4 WIDTH=600>
<TR><TD NOWRAP ALIGN=center><A HREF="../ubid/index.html"><B>Yowza! Auctions</B></A> - <FONT COLOR="red"><B>bid now!</B></FONT> %(auctions)s...</TD></TR>
<TR><TD NOWRAP ALIGN=center><FONT SIZE=-1><A HREF="../orinoco/index.html">Shopping</A> -
<A HREF="../ubid/index.html"><B>Auctions</B></A> -
<A HREF="services/yellowpages.html">Yellow Pages</A> -
<A HREF="services/people.html">People Search</A> -
<A HREF="services/maps.html">Maps</A> -
<A HREF="services/travel.html">Travel</A> -
<A HREF="services/classifieds.html">Classifieds</A> -
<A HREF="services/personals.html">Personals</A> -
<A HREF="services/games.html">Games</A> -
<A HREF="services/chat.html">Chat</A> -
<A HREF="services/clubs.html"><B>Clubs</B></A><BR>
<A HREF="mail.html">Mail</A> -
<A HREF="services/calendar.html">Calendar</A> -
<A HREF="services/pager.html">Pager</A> -
<A HREF="my.html">My Yowza!</A> -
<A HREF="../cnm/index.html">News</A> -
<A HREF="services/sports.html">Sports</A> -
<A HREF="services/weather.html">Weather</A> -
<A HREF="services/tv.html">TV</A> -
<A HREF="services/stocks.html">Stock Quotes</A> -
<A HREF="services/index.html">more...</A></FONT></TD></TR></TABLE>
%(rule)s<TABLE BORDER=0 CELLSPACING=7 CELLPADDING=2><TR><TD VALIGN=top ALIGN=center>
<TABLE BORDER=0 CELLSPACING=0 CELLPADDING=4><TR>
<TD VALIGN=top NOWRAP><FONT SIZE=-1>%(col0)s</FONT></TD>
<TD VALIGN=top NOWRAP><FONT SIZE=-1>%(col1)s</FONT></TD>
</TR></TABLE></TD>
<TD ALIGN=right VALIGN=top BGCOLOR="#DCDCDC" WIDTH=155><TABLE BORDER=0 CELLSPACING=1 CELLPADDING=1 WIDTH="100%%">
<TR><TD ALIGN=center BGCOLOR="#FFFFCC" NOWRAP COLSPAN=2><FONT FACE=arial SIZE=2><B>In the News</B></FONT></TD></TR>
%(news)s<TR><TD ALIGN=right COLSPAN=2><A HREF="../cnm/index.html"><FONT SIZE=-1>more...</FONT></A></TD></TR>
<TR><TD ALIGN=center BGCOLOR="#FFFFCC" COLSPAN=2><FONT FACE=arial SIZE=2><B>Marketplace</B></FONT></TD></TR>
<TR><TD VALIGN=top><B>&#183;</B></TD><TD><FONT SIZE=-1><A HREF="../orinoco/index.html">Books</A>, <A HREF="../snapster/index.html">music</A>, <A HREF="../etoyz/index.html">toys</A>, <A HREF="../petz/index.html">pet food</A> and <A HREF="../orinoco/index.html">more</A></FONT></TD></TR>
<TR><TD VALIGN=top><B>&#183;</B></TD><TD><FONT SIZE=-1><A HREF="services/stocks.html">Y2K Money Center</A> - stash your cash</FONT></TD></TR>
<TR><TD ALIGN=right COLSPAN=2><A HREF="services/index.html"><FONT SIZE=-1>more...</FONT></A></TD></TR>
<TR><TD ALIGN=center BGCOLOR="#FFFFCC" COLSPAN=2><FONT FACE=arial SIZE=2><B>Inside Yowza!</B></FONT></TD></TR>
<TR><TD VALIGN=top><B>&#183;</B></TD><TD><FONT SIZE=-1><A HREF="../geohoods/index.html">Yowza! GeoHoods</A> - build your own home page</FONT></TD></TR>
<TR><TD VALIGN=top><B>&#183;</B></TD><TD><FONT SIZE=-1><A HREF="dir/Entertainment/Cool_Links/index.html">Cool Links</A> - hamsters, and more hamsters</FONT></TD></TR>
<TR><TD VALIGN=top><B>&#183;</B></TD><TD><FONT SIZE=-1><A HREF="services/games.html">Y! Games</A> - hearts, checkers, tic-tac-toe</FONT></TD></TR>
<TR><TD ALIGN=right COLSPAN=2><A HREF="services/index.html"><FONT SIZE=-1>more...</FONT></A></TD></TR>
</TABLE></TD></TR></TABLE>
%(rule)s</FORM>
<FORM NAME="zf" ACTION="dir/Regional/U_S__States/index.html" onSubmit="return zipGo();">
<TABLE BORDER=0 CELLSPACING=4 CELLPADDING=0>
<TR><TD ALIGN=right VALIGN=top NOWRAP><FONT SIZE=-1><B>World Yowza!s</B></FONT></TD><TD></TD><TD VALIGN=top COLSPAN=2><FONT SIZE=-1><I>Europe</I> :
<A HREF="dir/Regional/Countries/France/index.html">France</A> -
<A HREF="dir/Regional/Countries/Germany/index.html">Germany</A> -
<A HREF="dir/Regional/Countries/United_Kingdom/index.html">UK &amp; Ireland</A><BR><I>Pacific Rim</I> :
<A HREF="dir/Regional/Countries/Australia/index.html">Australia &amp; NZ</A> -
<A HREF="dir/Regional/Countries/Japan/index.html">Japan</A><BR><I>Americas</I> :
<A HREF="dir/Regional/Countries/Canada/index.html">Canada</A> -
<A HREF="dir/Regional/U_S__States/index.html">U.S. States</A></FONT></TD></TR>
<TR><TD ALIGN=right NOWRAP><FONT SIZE=-1><B>Yowza! Get Local</B></FONT></TD><TD></TD><TD NOWRAP><FONT SIZE=-1>
<A HREF="dir/Regional/U_S__States/California/index.html">LA</A> -
<A HREF="dir/Regional/U_S__States/New_York/index.html">NYC</A> -
<A HREF="dir/Regional/U_S__States/California/index.html">SF Bay</A> -
<A HREF="dir/Regional/U_S__States/Texas/index.html">Austin</A> -
<A HREF="dir/Regional/U_S__States/index.html">more...</A> &nbsp;&nbsp;</FONT></TD>
<TD NOWRAP><FONT SIZE=-1><INPUT NAME=zip SIZE=5 MAXLENGTH=5>&nbsp;<INPUT TYPE=submit VALUE="Enter Zip Code"></FONT></TD></TR>
<TR><TD ALIGN=right VALIGN=top NOWRAP><FONT SIZE=-1><B>Other</B></FONT></TD><TD></TD><TD VALIGN=top COLSPAN=2><FONT SIZE=-1>
<A HREF="services/autos.html">Autos</A> -
<A HREF="services/careers.html">Careers</A> -
<A HREF="services/greetings.html"><B>Greetings</B></A> -
<A HREF="services/health.html">Health</A> -
<A HREF="services/events.html">Net Events</A> -
<A HREF="services/boards.html">Message Boards</A><BR>
<A HREF="services/movies.html">Movies</A> -
<A HREF="services/music.html">Music</A> -
<A HREF="services/realestate.html">Real Estate</A> -
<A HREF="services/smallbiz.html">Small Business</A> -
<A HREF="services/kids.html">Yowzlings! for Kids</A></FONT></TD></TR>
</TABLE></FORM>
%(rule)s<TABLE BORDER=0 CELLSPACING=6 CELLPADDING=0><TR><TD ALIGN=right><FONT SIZE=-1>Yowza! runs on</FONT></TD><TD><IMG SRC="images/powered_by_kf.gif" WIDTH=88 HEIGHT=31 ALT="Powered by KoldFusion"></TD></TR></TABLE>
<FONT SIZE=-1><A HREF="suggest.html">How to Suggest a Site</A> -
<A HREF="info.html">Company Info</A> -
<A HREF="info.html#privacy">Privacy Policy</A> -
<A HREF="info.html#terms">Terms of Service</A> -
<A HREF="info.html#contributors">Contributors</A> -
<A HREF="info.html#jobs">Openings at Yowza!</A>
<P>Copyright &copy; 1999 Yowza! Inc. All rights reserved.<BR><A HREF="info.html#copyright">Copyright Policy</A></FONT></CENTER>
<SCRIPT LANGUAGE="JavaScript">
<!--
function zipGo() {
  var z = document.zf.zip.value;
  var st = new Array('New_York','New_York','New_York','Texas','Ohio','Wisconsin','Texas','Texas','California','California');
  if (z.length != 5 || isNaN(parseInt(z))) { alert('Please enter a five-digit zip code.'); return false; }
  location.href = 'dir/Regional/U_S__States/' + st[parseInt(z.charAt(0))] + '/index.html';
  return false;
}
// -->
</SCRIPT>
''' % dict(auctions=auctions, rule=rule, col0=cats_html[0], col1=cats_html[1], news=news)
    write('index.html', page('Yowza!', body, ''))


# ================================================================ What's New / Cool / Random
def listing_page(rel, title, intro, pick):
    pre = up(rel)
    body = inner_header(pre, [], title) + '<P><FONT SIZE=-1>%s</FONT>\n' % intro
    for p in sorted(ORDER):
        ss = [s for s in CATS[p]['sites'] if pick(s)]
        if not ss:
            continue
        crumbs = ' &gt; '.join('<A HREF="%s">%s</A>' % (cat_url('/'.join(p.split('/')[:i]), pre), esc(CATS['/'.join(p.split('/')[:i])]['title']))
                               for i in range(1, len(p.split('/')) + 1))
        body += '<P><FONT FACE=arial SIZE=-1><B>%s</B></FONT>\n<UL>\n%s</UL>\n' % (crumbs, ''.join(site_li(s, pre) for s in ss))
    body += inner_footer(pre)
    write(rel, page('Yowza! - ' + title, body, pre))


def random_page():
    body = '''<SCRIPT LANGUAGE="JavaScript" SRC="yz_index.js"></SCRIPT>
<CENTER><A HREF="index.html"><IMG SRC="images/yowza_sm.gif" WIDTH=147 HEIGHT=31 BORDER=0 ALT="Yowza!"></A>
<P><FONT FACE=arial><B>Spinning the big Yowza! wheel...</B></FONT>
<SCRIPT LANGUAGE="JavaScript">
<!--
var pick = S[Math.floor(Math.random() * S.length)].split('|');
document.write('<P><FONT FACE=arial SIZE=-1>and it landed on <A HREF="' + pick[3] + '"><B>' + pick[0] + '</B></A>.<BR>Taking you there now. Buckle up.</FONT>');
setTimeout("location.href = pick[3]", 1500);
// -->
</SCRIPT>
<NOSCRIPT><P>The Random Yowza! Link needs JavaScript. Try <A HREF="cool.html">What's Cool</A> instead.</NOSCRIPT>
</CENTER>
'''
    write('random.html', page('Yowza! Random Link', body, ''))


# ================================================================ suggest a site (cookie moderation queue)
def suggest_pages():
    opts = ''.join('<OPTION VALUE="%s">%s\n' % (p, esc(' > '.join(CATS['/'.join(p.split('/')[:i])]['title']
                                                                   for i in range(1, len(p.split('/')) + 1))))
                   for p in sorted(ORDER))
    body = inner_header('', [], 'Suggest a Site') + '''<P>
<TABLE WIDTH=600 BORDER=0 CELLPADDING=0><TR><TD><FONT FACE=arial SIZE=-1>
Yowza! is built by people, not robots. Every site you suggest is read by one of our surfers, who decides whether it
belongs in the directory and which category fits it best. That takes time: we receive thousands of suggestions a day,
and roughly a third of them are for the same dancing hamster page. Please suggest each site only once, and please
choose the most specific category you can find.</FONT>
<P><FONT FACE=arial SIZE=-1><B>Step 1.</B> Choose a category. <B>Step 2.</B> Fill in the form. <B>Step 3.</B> Wait patiently.</FONT>
</TD></TR></TABLE>
<FORM NAME="sg" ACTION="suggest_thanks.html" METHOD=GET onSubmit="return checkSuggest();">
<TABLE WIDTH=600 BORDER=0 CELLPADDING=4 CELLSPACING=0>
<TR><TD BGCOLOR="#A0B8C8" COLSPAN=2><FONT FACE=arial><B>Site Information</B></FONT></TD></TR>
<TR><TD ALIGN=RIGHT VALIGN=TOP><FONT SIZE=-1><B>Category:</B></FONT></TD><TD><SELECT NAME=c>
''' + opts + '''</SELECT></TD></TR>
<TR><TD ALIGN=RIGHT><FONT SIZE=-1><B>Title:</B></FONT></TD><TD><INPUT NAME=stitle SIZE=40 MAXLENGTH=60></TD></TR>
<TR><TD ALIGN=RIGHT><FONT SIZE=-1><B>URL:</B></FONT></TD><TD><INPUT NAME=url SIZE=40 VALUE="http://"></TD></TR>
<TR><TD ALIGN=RIGHT VALIGN=TOP><FONT SIZE=-1><B>Description:</B><BR>(25 words or less)</FONT></TD><TD><TEXTAREA NAME=desc ROWS=4 COLS=40 WRAP=virtual></TEXTAREA></TD></TR>
<TR><TD BGCOLOR="#A0B8C8" COLSPAN=2><FONT FACE=arial><B>About You</B> <FONT SIZE=-1>(optional)</FONT></FONT></TD></TR>
<TR><TD ALIGN=RIGHT><FONT SIZE=-1><B>Your name:</B></FONT></TD><TD><INPUT NAME=who SIZE=30></TD></TR>
<TR><TD></TD><TD><FONT SIZE=-1><INPUT TYPE=checkbox NAME=mine VALUE=1> This is my own site (we promise not to hold it against you)</FONT></TD></TR>
<TR><TD></TD><TD><INPUT TYPE=submit VALUE="Submit Suggestion"> <INPUT TYPE=reset VALUE="Start Over"></TD></TR>
</TABLE></FORM>
<SCRIPT LANGUAGE="JavaScript">
<!--
function getArg(name) {
  var q = location.search.substring(1).split('&');
  for (var i = 0; i < q.length; i++) { var kv = q[i].split('='); if (kv[0] == name && kv.length > 1) return unescape(kv[1].replace(/\\+/g, ' ')); }
  return '';
}
var want = getArg('c'), sel = document.sg.c;
for (var i = 0; i < sel.options.length; i++) if (sel.options[i].value == want) sel.selectedIndex = i;
function checkSuggest() {
  var f = document.sg;
  if (f.stitle.value == '') { alert('Please give the site a title.'); f.stitle.focus(); return false; }
  if (f.url.value.length < 12 || f.url.value.indexOf('http://') != 0) { alert('Please enter the full URL, beginning with http://'); f.url.focus(); return false; }
  var w = f.desc.value.split(' '), n = 0;
  for (var i = 0; i < w.length; i++) if (w[i] != '') n++;
  if (n == 0) { alert('Please describe the site in a few words.'); f.desc.focus(); return false; }
  if (n > 25) { alert('Your description has ' + n + ' words. Our surfers only read the first 25, and they are very strict about it.'); f.desc.focus(); return false; }
  if (f.desc.value.toUpperCase() == f.desc.value && f.desc.value.length > 10) { alert('PLEASE DO NOT SHOUT. Descriptions in all capital letters are returned to sender.'); return false; }
  var item = escape(f.c.options[f.c.selectedIndex].value) + '~' + escape(f.stitle.value) + '~' + escape(f.url.value) + '~' + escape(f.desc.value) + '~' + (new Date()).getTime();
  var q = readQueue();
  q[q.length] = item;
  while (q.length > 10) q = q.slice(1);
  var exp = new Date(); exp.setTime(exp.getTime() + 30 * 24 * 3600 * 1000);
  document.cookie = 'yzqueue=' + escape(q.join('^')) + '; expires=' + exp.toGMTString() + '; path=/';
  location.href = 'suggest_thanks.html';
  return false;
}
function readQueue() {
  var all = document.cookie.split('; ');
  for (var i = 0; i < all.length; i++) if (all[i].indexOf('yzqueue=') == 0) { var v = unescape(all[i].substring(8)); return v == '' ? new Array() : v.split('^'); }
  return new Array();
}
// -->
</SCRIPT>
''' + inner_footer('')
    write('suggest.html', page('Yowza! - Suggest a Site', body, ''))

    body = inner_header('', [('suggest.html', 'Suggest a Site')], 'Thank You!') + '''<P>
<TABLE WIDTH=600 BORDER=0><TR><TD><FONT FACE=arial SIZE=-1>
<B>Your suggestion has been added to the Yowza! moderation queue.</B> One of our surfers will look at it as soon as
they finish the cold pizza and the 48,000 suggestions ahead of yours. If the site is accepted it will appear in
the directory within a few weeks. If it is not, please do not take it personally. Unless it was the hamster page again.
</FONT></TD></TR></TABLE>
<P><TABLE WIDTH=600 BORDER=0 CELLPADDING=3 CELLSPACING=1 BGCOLOR="#000000">
<TR BGCOLOR="#A0B8C8"><TD><FONT FACE=arial SIZE=-1><B>#</B></FONT></TD><TD><FONT FACE=arial SIZE=-1><B>Your suggestion</B></FONT></TD><TD><FONT FACE=arial SIZE=-1><B>Category</B></FONT></TD><TD><FONT FACE=arial SIZE=-1><B>Status</B></FONT></TD></TR>
<SCRIPT LANGUAGE="JavaScript" SRC="yz_index.js"></SCRIPT>
<SCRIPT LANGUAGE="JavaScript">
<!--
function h(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
var all = document.cookie.split('; '), q = new Array();
for (var i = 0; i < all.length; i++) if (all[i].indexOf('yzqueue=') == 0) { var v = unescape(all[i].substring(8)); if (v != '') q = v.split('^'); }
var stat = new Array('Waiting for a surfer', 'Waiting for a surfer', 'Surfer is on a coffee break', 'Being read (slowly)', 'Under review by a senior surfer', 'Surfer is laughing (good sign?)');
if (q.length == 0) document.write('<TR BGCOLOR="#FFFFFF"><TD COLSPAN=4><FONT SIZE=-1>Your queue is empty. (Cookies must be turned on for Yowza! to remember your suggestions.)</FONT></TD></TR>');
for (var i = q.length - 1; i >= 0; i--) {
  var f = q[i].split('~');
  var age = Math.floor(((new Date()).getTime() - parseInt(f[4])) / 60000);
  var st = stat[Math.min(stat.length - 1, Math.floor(age / 7))];
  document.write('<TR BGCOLOR="#FFFFFF"><TD><FONT SIZE=-1>' + (48213 + i * 977) + '</FONT></TD><TD><FONT SIZE=-1><B>' + h(unescape(f[1])) + '</B><BR>' + h(unescape(f[2])) + '<BR><I>' + h(unescape(f[3])) + '</I></FONT></TD><TD><FONT SIZE=-1><A HREF="dir/' + unescape(f[0]) + '/index.html">' + h(T[unescape(f[0])] || unescape(f[0])) + '</A></FONT></TD><TD><FONT SIZE=-1 COLOR="#CC0000">' + st + '</FONT></TD></TR>');
}
// -->
</SCRIPT>
</TABLE>
<P><FONT FACE=arial SIZE=-1><A HREF="suggest.html">Suggest another site</A> - <A HREF="index.html">Back to Yowza!</A> -
<A HREF="#" onClick="document.cookie='yzqueue=; path=/'; location.reload(); return false;">Withdraw all my suggestions</A></FONT>
''' + inner_footer('')
    write('suggest_thanks.html', page('Yowza! - Thank You', body, ''))


# ================================================================ My Yowza! (cookie personalization)
def my_page():
    body = inner_header('', [], 'My Yowza!') + r'''<P>
<SCRIPT LANGUAGE="JavaScript">
<!--
function getCookie(n) {
  var all = document.cookie.split('; ');
  for (var i = 0; i < all.length; i++) if (all[i].indexOf(n + '=') == 0) return unescape(all[i].substring(n.length + 1));
  return '';
}
function h(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
function save() {
  var f = document.mf, mods = '';
  if (f.nick.value == '') { alert('Please choose a nickname. Anything but "Webmaster".'); return false; }
  for (var i = 0; i < f.mod.length; i++) if (f.mod[i].checked) mods += f.mod[i].value;
  var exp = new Date(); exp.setTime(exp.getTime() + 365 * 24 * 3600 * 1000);
  document.cookie = 'myyz=' + escape(f.nick.value + '|' + f.zip.value + '|' + mods + '|' + f.color.options[f.color.selectedIndex].value) + '; expires=' + exp.toGMTString() + '; path=/';
  location.reload();
  return false;
}
function signOut() { document.cookie = 'myyz=; path=/'; location.reload(); }
var me = getCookie('myyz');
if (me == '') {
  document.write('<TABLE WIDTH=600 BORDER=0 CELLPADDING=4><TR><TD><FONT FACE=arial SIZE=-1><B>Welcome to My Yowza!</B> - your own personal front page of the Web. Pick the things you care about and we will put them all on one page, just for you. Free! (We just like you.)</FONT></TD></TR></TABLE>');
  document.write('<FORM NAME="mf" onSubmit="return save();"><TABLE WIDTH=600 BORDER=0 CELLPADDING=4 CELLSPACING=0>');
  document.write('<TR><TD BGCOLOR="#A0B8C8" COLSPAN=2><FONT FACE=arial><B>Set up your page</B></FONT></TD></TR>');
  document.write('<TR><TD ALIGN=RIGHT><FONT SIZE=-1><B>Nickname:</B></FONT></TD><TD><INPUT NAME=nick SIZE=20 MAXLENGTH=20></TD></TR>');
  document.write('<TR><TD ALIGN=RIGHT><FONT SIZE=-1><B>Zip code:</B></FONT></TD><TD><INPUT NAME=zip SIZE=5 MAXLENGTH=5> <FONT SIZE=-1>(for your weather)</FONT></TD></TR>');
  document.write('<TR><TD ALIGN=RIGHT VALIGN=TOP><FONT SIZE=-1><B>Show me:</B></FONT></TD><TD><FONT SIZE=-1>');
  var mods = new Array('W','Weather','S','Stock Quotes','N','Headlines','H','Horoscope','Y','Y2K Countdown','C','Cool Site of the Day');
  for (var i = 0; i < mods.length; i += 2) document.write('<INPUT TYPE=checkbox NAME=mod VALUE="' + mods[i] + '" CHECKED> ' + mods[i + 1] + '<BR>');
  document.write('</FONT></TD></TR><TR><TD ALIGN=RIGHT><FONT SIZE=-1><B>Page color:</B></FONT></TD><TD><SELECT NAME=color><OPTION VALUE="FFFFCC">Classic Cream<OPTION VALUE="CCFFCC">Mint<OPTION VALUE="CCCCFF">Periwinkle<OPTION VALUE="FFCCFF">Bubblegum<OPTION VALUE="DCDCDC">Corporate Gray</SELECT></TD></TR>');
  document.write('<TR><TD></TD><TD><INPUT TYPE=submit VALUE="Create My Page"></TD></TR></TABLE></FORM>');
  document.write('<P><FONT SIZE=-1>My Yowza! remembers you with a cookie. A cookie is a small text file your browser keeps. It does not contain chocolate chips.</FONT>');
} else {
  var f = me.split('|'), nick = f[0], zip = f[1], mods = f[2], col = f[3];
  var d = new Date();
  var days = new Array('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday');
  document.write('<TABLE WIDTH=600 BORDER=0 CELLPADDING=4 CELLSPACING=0 BGCOLOR="#' + col + '"><TR><TD><FONT FACE=arial SIZE=+1><B>' + h(nick) + "'s Yowza!</B></FONT><BR><FONT SIZE=-1>" + days[d.getDay()] + ' - <A HREF="#" onClick="signOut(); return false;">Start over</A></FONT></TD></TR></TABLE><P>');
  document.write('<TABLE WIDTH=600 BORDER=0 CELLPADDING=4 CELLSPACING=4><TR><TD VALIGN=TOP WIDTH="50%">');
  if (mods.indexOf('W') >= 0) {
    var sky = new Array('Sunny','Partly cloudy','Drizzle','Foggy','Windy','Mostly modem-colored');
    var t = 40 + (parseInt(zip) || 12345) % 45;
    document.write('<TABLE WIDTH="100%" BORDER=0 CELLPADDING=2><TR><TD BGCOLOR="#A0B8C8"><FONT FACE=arial SIZE=-1><B>Weather for ' + (zip == '' ? 'Anytown' : h(zip)) + '</B></FONT></TD></TR><TR><TD><FONT SIZE=-1>Today: ' + sky[d.getDate() % sky.length] + ', high ' + t + '&deg;F<BR>Tomorrow: ' + sky[(d.getDate() + 1) % sky.length] + ', high ' + (t + 3) + '&deg;F</FONT></TD></TR></TABLE><P>');
  }
  if (mods.indexOf('S') >= 0) {
    var tick = new Array('ORIN','Orinoco.com','UBID','uBid','PETZ','Petz.com','ETOY','eToyz','GEOH','GeoHoods','KOLD','Gibson Mainframe');
    document.write('<TABLE WIDTH="100%" BORDER=0 CELLPADDING=2><TR><TD BGCOLOR="#A0B8C8" COLSPAN=3><FONT FACE=arial SIZE=-1><B>Stock Quotes</B></FONT></TD></TR>');
    for (var i = 0; i < tick.length; i += 2) {
      var px = 20 + Math.floor(Math.random() * 300), ch = Math.floor(Math.random() * 40) - 12;
      document.write('<TR><TD><FONT SIZE=-1><A HREF="services/stocks.html">' + tick[i] + '</A></FONT></TD><TD ALIGN=RIGHT><FONT SIZE=-1>' + px + ' ' + (Math.floor(Math.random() * 8)) + '/8</FONT></TD><TD ALIGN=RIGHT><FONT SIZE=-1 COLOR="' + (ch < 0 ? '#CC0000' : '#009900') + '">' + (ch < 0 ? '' : '+') + ch + '</FONT></TD></TR>');
    }
    document.write('</TABLE><FONT SIZE=-2>Quotes delayed by at least 20 minutes, possibly 20 years.</FONT><P>');
  }
  document.write('</TD><TD VALIGN=TOP WIDTH="50%">');
  if (mods.indexOf('N') >= 0) document.write('<TABLE WIDTH="100%" BORDER=0 CELLPADDING=2><TR><TD BGCOLOR="#A0B8C8"><FONT FACE=arial SIZE=-1><B>Headlines</B></FONT></TD></TR><TR><TD><FONT SIZE=-1>&#183; <A HREF="../cnm/index.html">Banks say they are 99.9% ready for Y2K</A><BR>&#183; <A HREF="../cnm/index.html">Mars probe lost; engineers blame inches</A><BR>&#183; <A HREF="../dashdot/index.html">Nerds argue about it at length</A></FONT></TD></TR></TABLE><P>');
  if (mods.indexOf('H') >= 0) {
    var sc = new Array('A stranger will sign your guestbook.','Avoid chat rooms after midnight.','Your modem will connect at 53.3K. Rejoice.','Someone will forward you a chain letter. Do not send it to ten friends.','You will find exactly the category you need on the first try.','Today is a good day to defragment.');
    document.write('<TABLE WIDTH="100%" BORDER=0 CELLPADDING=2><TR><TD BGCOLOR="#A0B8C8"><FONT FACE=arial SIZE=-1><B>Horoscope</B></FONT></TD></TR><TR><TD><FONT SIZE=-1>' + sc[(d.getDate() + nick.length) % sc.length] + '</FONT></TD></TR></TABLE><P>');
  }
  if (mods.indexOf('Y') >= 0) {
    var y2k = new Date(2000, 0, 1), d99 = new Date(1999, d.getMonth(), d.getDate()), left = Math.ceil((y2k.getTime() - d99.getTime()) / 86400000);
    document.write('<TABLE WIDTH="100%" BORDER=0 CELLPADDING=2><TR><TD BGCOLOR="#A0B8C8"><FONT FACE=arial SIZE=-1><B>Y2K Countdown</B></FONT></TD></TR><TR><TD><FONT SIZE=-1>' + (left > 0 ? '<B>' + left + '</B> days until the year 2000. Have you checked your VCR?' : 'The year 2000 came and went. Your toaster survived. You may now take down the bunker.') + '</FONT></TD></TR></TABLE><P>');
  }
  if (mods.indexOf('C') >= 0) document.write('<TABLE WIDTH="100%" BORDER=0 CELLPADDING=2><TR><TD BGCOLOR="#A0B8C8"><FONT FACE=arial SIZE=-1><B>Cool Site of the Day</B></FONT></TD></TR><TR><TD><FONT SIZE=-1><A HREF="random.html">Spin the wheel</A> or see <A HREF="cool.html">What\'s Cool</A>.</FONT></TD></TR></TABLE>');
  document.write('</TD></TR></TABLE>');
}
// -->
</SCRIPT>
<NOSCRIPT>My Yowza! needs JavaScript and cookies turned on.</NOSCRIPT>
''' + inner_footer('')
    write('my.html', page('My Yowza!', body, ''))


# ================================================================ Mail (a fake inbox)
MAIL = [
    ('Yowza! Mail Team', 'Welcome to Yowza! Mail!', 'Oct 12',
     'Congratulations on your new free email account! You now have six whole megabytes of storage, which is enough for '
     'roughly 4,000 messages or one picture of your cousin\'s wedding. Tip: your address is easy to remember and impossible to spell.'),
    ('Aunt Margie', 'FW: FW: FW: FW: Free Cookie Recipe!!!', 'Oct 11',
     '>>>>> A woman ate a cookie at a department store cafe and asked for the recipe. They charged her TWO HUNDRED FIFTY '
     'DOLLARS!!! So she is sending it to EVERYONE for free. Forward this to ten friends!!! (Recipe: butter, sugar, flour, chips. Bake.)'),
    ('IT Department', 'Y2K: Please test your computer', 'Oct 11',
     'All staff: before December 31st, please set your computer clock to 11:58 PM on 12/31/1999 and watch it for two minutes. '
     'If anything catches fire, please notify IT. Do not do this on the server.'),
    ('The Webring Registry', 'Your site has been added to the Unicorn Webring', 'Oct 10',
     'Thank you for joining! Please paste the ring navigation code at the bottom of your page within 7 days or your site '
     'will be removed from the ring. The unicorns are watching.'),
    ('Make Money Fast', '$$$ EARN $50,000 FROM HOME $$$', 'Oct 09',
     'Dear Friend, This is not spam. This is a ONE TIME opportunity. All you need is a fax machine, a dream and a list of '
     'everyone you have ever met. Reply REMOVE to be removed (you will not be removed).'),
    ('Dave', 're: did you see the hamsters', 'Oct 08',
     'dude. DUDE. go to the hamster shuffle site and turn your speakers up. i have been watching for 40 minutes. send help.'),
]


def mail_page():
    rows = ''
    for i, (frm, subj, date, _) in enumerate(MAIL):
        rows += ('<TR BGCOLOR="%s"><TD><INPUT TYPE=checkbox NAME=sel></TD><TD><FONT SIZE=-1>%s</FONT></TD>'
                 '<TD><FONT SIZE=-1><A HREF="#read" onClick="showMsg(%d)">%s%s%s</A></FONT></TD><TD><FONT SIZE=-1>%s</FONT></TD></TR>\n') % (
            '#FFFFCC' if i < 3 else '#FFFFFF', esc(frm), i, '<B>' if i < 3 else '', esc(subj), '</B>' if i < 3 else '', date)
    msgs = ',\n'.join(js_str(m[3]) for m in MAIL)
    body = inner_header('', [], 'Yowza! Mail') + '''<P>
<TABLE WIDTH=600 BORDER=0 CELLPADDING=3><TR>
<TD><FONT FACE=arial SIZE=-1><B>Inbox</B> (3 new) - <A HREF="#read" onClick="alert('Your message has been composed. Sadly it has nowhere to go: the Yowza! Mail servers are busy upgrading to 1999-compliant date handling.'); return false;">Compose</A> -
<A HREF="#" onClick="alert('Addresses: Aunt Margie, Dave, and 1,402 people who forward chain letters.'); return false;">Addresses</A> - <A HREF="help.html">Help</A></FONT></TD>
<TD ALIGN=RIGHT><FONT SIZE=-1>Storage used: 5.9 MB of 6 MB</FONT></TD></TR></TABLE>
<FORM NAME="inbox"><TABLE WIDTH=600 BORDER=0 CELLPADDING=3 CELLSPACING=1 BGCOLOR="#999999">
<TR BGCOLOR="#A0B8C8"><TD></TD><TD><FONT FACE=arial SIZE=-1><B>Sender</B></FONT></TD><TD><FONT FACE=arial SIZE=-1><B>Subject</B></FONT></TD><TD><FONT FACE=arial SIZE=-1><B>Date</B></FONT></TD></TR>
''' + rows + '''</TABLE>
<P><A NAME="read"></A><TEXTAREA NAME=body ROWS=6 COLS=70 WRAP=virtual>Click a subject to read the message.</TEXTAREA><BR>
<INPUT TYPE=button VALUE="Delete" onClick="alert('Deleted. (It will be back. They always come back.)')">
<INPUT TYPE=button VALUE="Forward to 10 Friends" onClick="alert('Please do not.')">
</FORM>
<SCRIPT LANGUAGE="JavaScript">
<!--
var M = new Array(''' + msgs + ''');
function showMsg(i) { document.inbox.body.value = M[i]; }
// -->
</SCRIPT>
<P><IMG SRC="images/ad_mail.gif" WIDTH=468 HEIGHT=60 ALT="Get your free Yowza! Mail">
<P><FONT SIZE=-2>*For life means the life of the account, which ends if you do not log in for 30 days.</FONT>
''' + inner_footer('')
    write('mail.html', page('Yowza! Mail', body, ''))


# ================================================================ help / info / services
def help_page():
    body = inner_header('', [], 'Yowza! Help') + '''<P>
<TABLE WIDTH=600 BORDER=0><TR><TD><FONT FACE=arial SIZE=-1>
<P><B>What is Yowza!?</B><BR>
Yowza! is a guide to the World Wide Web, organized by real people into categories you can browse, like the shelves of a
library that never closes and never shushes you. Each listing was visited and described by one of our surfers.
<P><B>What do the symbols mean?</B><BR>
<IMG SRC="images/cool.gif" WIDTH=22 HEIGHT=11> means our surfers think the site is especially cool.<BR>
<IMG SRC="images/new2.gif" WIDTH=28 HEIGHT=11> means the site or category was added recently.<BR>
A category name ending in <B>@</B> lives somewhere else in the directory; clicking it takes you there.<BR>
The number in parentheses, like <I>(12)</I>, is how many sites are filed in that category and everything below it.
<P><A NAME="search"></A><B>How do I search?</B><BR>
Type a few words in the box and press Search. Yowza! looks for categories and sites whose names and descriptions contain
every word you typed. From any category page you can choose to search <I>just this category</I>. If Yowza! comes up empty,
the search results page will offer to pass your words along to <A HREF="../altavisor/index.html">AltaVisor</A>, which
reads the full text of Web pages.
<P><B>How do I get my site listed?</B><BR>
Go to the category where it belongs and click <A HREF="suggest.html">Suggest a Site</A> at the bottom of the page.
<P><B>Why is my site not listed yet?</B><BR>
Our surfers are reading as fast as they can. Bribes in the form of baked goods are not accepted, but they are eaten.
<P><B>What browser do I need?</B><BR>
Any browser from 1996 or later. Search, My Yowza! and the Random Link use JavaScript, so please leave it on.
</FONT></TD></TR></TABLE>
''' + inner_footer('')
    write('help.html', page('Yowza! Help', body, ''))


def info_page():
    body = inner_header('', [], 'Company Information') + '''<P>
<TABLE WIDTH=600 BORDER=0><TR><TD><FONT FACE=arial SIZE=-1>
<P><B>About Yowza! Inc.</B><BR>
Yowza! began in 1994 as a list of favorite links kept by two graduate students who should have been writing their
dissertations. The list grew, the dissertations did not, and today Yowza! is used by millions of people every month.
Our offices are in a former mattress warehouse with a slide instead of stairs.
<P><A NAME="contributors"></A><B>Contributors</B><BR>
The directory is maintained by a team of surfers who have, between them, visited every web page about hamsters.
Yowza! runs on the KoldFusion Application Server from Gibson Mainframe Co.
<P><A NAME="jobs"></A><B>Openings at Yowza!</B><BR>
We are hiring surfers. Requirements: a love of the Web, a fast modem, an ability to describe any website in 25 words
or less, and a tolerance for beanbag chairs. Stock options available; we are told they will be worth a fortune.
<P><A NAME="privacy"></A><B>Privacy Policy</B><BR>
Yowza! uses cookies to remember your My Yowza! settings and your site suggestions. They stay in your browser.
We do not sell your name to anybody, partly out of principle and partly because nobody has asked.
<P><A NAME="terms"></A><B>Terms of Service</B><BR>
Please be nice. Do not suggest the same site 400 times. Do not use Yowza! to plan world domination
(that is our job).
<P><A NAME="copyright"></A><B>Copyright Policy</B><BR>
Everything on Yowza!, including the bouncy logo, was made by us. Yowza! is a parody and is not affiliated with any
real company, living or acquired.
</FONT></TD></TR></TABLE>
''' + inner_footer('')
    write('info.html', page('Yowza! Company Information', body, ''))


SERVICES = [
    ('yellowpages', 'Yellow Pages', 'Find a plumber, a pizza place or a guy who fixes modems, by city and category.',
     'Business_and_Economy/Shopping_and_Services'),
    ('people', 'People Search', 'Look up long-lost friends by name, city or high school mascot.', 'Reference/Phone_Numbers_and_Addresses'),
    ('maps', 'Maps', 'Type an address and get a map with a little red star on it. Driving directions coming soon.', 'Reference/Maps'),
    ('travel', 'Travel', 'Book flights, hotels and rental cars. Our travel agents work from home in their pajamas.', 'Recreation_and_Sports/Travel'),
    ('classifieds', 'Classifieds', 'Buy and sell used cars, couches and lava lamps in your neighborhood.', 'Business_and_Economy/Shopping_and_Services'),
    ('personals', 'Personals', 'Single web surfer, likes long walks to the computer. Meet someone who also types in lowercase.', 'Society_and_Culture/Relationships'),
    ('games', 'Games', 'Play hearts, checkers, chess and tic-tac-toe against people on the other side of the planet.', 'Recreation_and_Sports/Games'),
    ('chat', 'Chat', 'Talk with other Yowza! users in real time. Please do not ask everyone their age, sex and location.', 'Computers_and_Internet/Internet/Chat'),
    ('clubs', 'Clubs', 'Start a club about anything: knitting, Linux, knitting with Linux. Free message boards and photo albums.', 'Recreation_and_Sports/Hobbies'),
    ('calendar', 'Calendar', 'Keep track of birthdays, meetings and the end of the millennium. December 31 is already marked.', 'Society_and_Culture/Holidays_and_Observances'),
    ('pager', 'Pager', 'See when your buddies are online and send them instant messages. Beep!', 'Computers_and_Internet/Internet/Chat'),
    ('sports', 'Sports', 'Scores, standings and the latest trade rumors, updated every few minutes.', 'Recreation_and_Sports/Sports'),
    ('weather', 'Weather', 'Forecasts for 10,000 cities. Today: partly cloudy with a chance of Y2K.', 'News_and_Media/Weather'),
    ('tv', 'TV', 'What is on tonight, on all 57 channels.', 'News_and_Media/Television'),
    ('stocks', 'Stock Quotes', 'Delayed quotes for every stock, including the 40 internet companies that went public this morning.', 'Business_and_Economy/Finance_and_Investment'),
    ('autos', 'Autos', 'New and used car prices, reviews and a minivan for every family.', 'Recreation_and_Sports/Automotive'),
    ('careers', 'Careers', 'Thousands of jobs, many of which require knowing HTML.', 'Business_and_Economy/Employment_and_Work'),
    ('greetings', 'Greetings', 'Send a free animated greeting card with a MIDI soundtrack. Your friends will love it (once).', 'Society_and_Culture/Holidays_and_Observances'),
    ('health', 'Health', 'Health news and a medical encyclopedia written in plain English.', 'Health'),
    ('events', 'Net Events', 'Live chats with celebrities, webcasts and online concerts. Times are Pacific, sorry.', 'Entertainment'),
    ('boards', 'Message Boards', 'Thousands of discussion boards on every topic. Arguments start at the third post.', 'Computers_and_Internet/Internet/Chat'),
    ('movies', 'Movies', 'Showtimes, reviews and trailers (if you have a very fast modem).', 'Entertainment/Movies_and_Film'),
    ('music', 'Music', 'Charts, news and where to buy the CD.', 'Entertainment/Music'),
    ('realestate', 'Real Estate', 'Find a house, an apartment or a bunker with three years of canned goods.', 'Business_and_Economy'),
    ('smallbiz', 'Small Business', 'Start a business, get a web site, and incorporate before lunch.', 'Business_and_Economy/Small_Business'),
    ('kids', 'Yowzlings!', 'A directory just for kids, with only the safe and the silly.', 'Education/K_12'),
]


def service_pages():
    for key, name, blurb, cat in SERVICES:
        rel = 'services/%s.html' % key
        pre = up(rel)
        body = inner_header(pre, [(pre + 'services/index.html', 'More Yowza!')], 'Yowza! ' + name) + '''<P>
<TABLE WIDTH=600 BORDER=0 CELLPADDING=4><TR><TD VALIGN=TOP><IMG SRC="%(pre)simages/construction.gif" WIDTH=140 HEIGHT=50 ALT="Under Construction"></TD>
<TD VALIGN=TOP><FONT FACE=arial SIZE=-1><B>Yowza! %(name)s</B> - %(blurb)s
<P>Our engineers are putting the finishing touches on %(name)s right now. It will open very soon,
probably before the year 2000, almost certainly before the year 2001.
<P>In the meantime, browse the <A HREF="%(cu)s">%(ct)s</A> category, or <A HREF="%(pre)ssearch.html">search Yowza!</A>.</FONT></TD></TR></TABLE>
''' % dict(pre=pre, name=esc(name), blurb=esc(blurb), cu=cat_url(cat, pre), ct=esc(CATS[cat]['title'])) + inner_footer(pre)
        write(rel, page('Yowza! ' + name, body, pre))
    pre = '../'
    items = ''.join('<LI><A HREF="%s.html"><B>%s</B></A> - %s\n' % (k, esc(n), esc(b)) for k, n, b, _ in SERVICES)
    body = inner_header(pre, [], 'More Yowza!') + '''<P><TABLE WIDTH=600><TR><TD><FONT FACE=arial SIZE=-1>
Yowza! is more than a directory. Here is everything else we do, or are about to do, or have announced at a trade show.
<UL>
<LI><A HREF="../my.html"><B>My Yowza!</B></A> - your personal start page
<LI><A HREF="../mail.html"><B>Yowza! Mail</B></A> - free email for life
<LI><A HREF="../../ubid/index.html"><B>Auctions</B></A> - our friends at uBid
<LI><A HREF="../../geohoods/index.html"><B>GeoHoods</B></A> - free home pages
<LI><A HREF="../../cnm/index.html"><B>News</B></A> - headlines from CNM Interactive
''' + items + '''</UL></FONT></TD></TR></TABLE>
''' + inner_footer(pre)
    write('services/index.html', page('More Yowza!', body, pre))


def copy_stock():
    src = os.path.normpath(os.path.join(ROOT, '..', '..', 'images'))
    for g in ('construction.gif', 'powered_by_kf.gif'):
        shutil.copy(os.path.join(src, g), os.path.join(ROOT, 'images', g))


def main():
    # clear the generated category tree so removed categories disappear
    shutil.rmtree(os.path.join(ROOT, 'dir'), ignore_errors=True)
    copy_stock()
    for p in ORDER:
        category_page(p)
    search_index()
    search_page()
    advanced_page()
    home_page()
    listing_page('new.html', "What's New",
                 "Sites added to Yowza! this week, as of %s. Our surfers have been busy (and a little over-caffeinated)." % TODAY,
                 lambda s: s['new'])
    listing_page('cool.html', "What's Cool",
                 'The sites our surfers keep going back to when they should be working. Feeling adventurous? '
                 'Try a <A HREF="random.html">Random Yowza! Link</A>.', lambda s: s['cool'])
    random_page()
    suggest_pages()
    my_page()
    mail_page()
    help_page()
    info_page()
    service_pages()
    n = sum(len(fs) for _, _, fs in os.walk(ROOT))
    print('Yowza! generated: %d categories, %d listings, %d files in the site folder' % (
        len(ORDER), sum(len(CATS[p]['sites']) for p in ORDER), n))


if __name__ == '__main__':
    main()
