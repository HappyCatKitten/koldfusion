#!/usr/bin/env python3
"""Generates the static Ask Reeves site from tools/rs_data.py.

    python3 tools/gen_askreeves.py

Writes index.html, answer.html (question matching in JavaScript), peek.html (the keyhole),
about.html, channels/*.html, ans/*.html (Reeves' own answers) and rs_data.js.
"""
import html, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
SITES = os.path.normpath(os.path.join(ROOT, '..'))
sys.path.insert(0, HERE)
import rs_data as R  # noqa: E402

SITE = 'askreeves'
RING = ['yowza', 'altavisor', 'askreeves', 'orinoco', 'ubid', 'etoyz', 'petz', 'geohoods', 'hamstershuffle', 'dashdot', 'snapster', 'cnm']
TOPICS = [('popular', 'POPULAR QUESTIONS'), ('shopping', 'SHOPPING'), ('health', 'HEALTH'), ('travel', 'TRAVEL'),
          ('entertainment', 'ENTERTAINMENT'), ('computers', 'COMPUTERS'), ('kids', 'KIDS'), ('home', 'HOME'),
          ('money', 'MONEY'), ('pets', 'PETS'), ('reference', 'REFERENCE')]


def esc(s):
    return html.escape(s, quote=True)


def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='latin-1', errors='xmlcharrefreplace') as f:
        f.write(text)


def up(rel):
    return '../' * rel.count('/')


def js_str(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'").replace('</', '<\\/') + "'"


def ring(pre):
    i = RING.index(SITE)
    arr = ','.join("'%s'" % r for r in RING)
    return '''<P><CENTER>
<TABLE BORDER=2 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#C0C0C0"><TR><TD ALIGN=CENTER>
<FONT FACE="Arial, Helvetica" SIZE=1>
<A HREF="%(pre)s../%(prv)s/index.html">&lt;&lt; Prev</A> |
<A HREF="%(pre)s../../web1999/index.html" onClick="var r=new Array(%(arr)s); location.href='%(pre)s../'+r[Math.floor(Math.random()*r.length)]+'/index.html'; return false;">Random</A> |
<B><A HREF="%(pre)s../../web1999/index.html">The 1999 Web Ring</A></B> &middot; Ask Reeves is site %(n)d of %(tot)d |
<A HREF="%(pre)s../%(nxt)s/index.html">Next &gt;&gt;</A>
</FONT></TD></TR></TABLE>
</CENTER>
''' % dict(pre=pre, prv=RING[i - 1], nxt=RING[(i + 1) % len(RING)], arr=arr, n=i + 1, tot=len(RING))


def page(title, body, pre, onload=''):
    return '''<HTML>
<HEAD>
<TITLE>%s</TITLE>
</HEAD>
<BODY BGCOLOR="#FFFFFF" TEXT="#000000" LINK="#000000" VLINK="#666666" ALINK="#CC0000"%s>
%s
%s</BODY>
</HTML>
''' % (esc(title), (' onLoad="%s"' % onload) if onload else '', body, ring(pre))


def topbar(pre):
    return '''<TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0 BGCOLOR="#666699" WIDTH=620><TR>
<TD HEIGHT=20>&nbsp;&nbsp;<FONT FACE="Arial, Helvetica" SIZE=1 COLOR="#FFFFCC"><B>
<A HREF="%(pre)sindex.html"><FONT COLOR="#FFFFCC">HOME</FONT></A> &nbsp;|&nbsp;
<A HREF="%(pre)sabout.html"><FONT COLOR="#FFFFCC">ABOUT REEVES</FONT></A> &nbsp;|&nbsp;
<A HREF="%(pre)sabout.html#help"><FONT COLOR="#FFFFCC">HELP</FONT></A> &nbsp;|&nbsp;
<A HREF="%(pre)speek.html"><FONT COLOR="#FFFFCC">PEEK THROUGH THE KEYHOLE</FONT></A> &nbsp;|&nbsp;
<A HREF="%(pre)schannels/kids.html"><FONT COLOR="#FFFFCC">REEVES FOR KIDS</FONT></A></B></FONT></TD></TR></TABLE>
''' % dict(pre=pre)


def channel_bar(pre, current=None):
    cells = ''
    for key, label in TOPICS[:7]:
        style = '<FONT COLOR="#CC0000">%s</FONT>' % label if key == current else label
        cells += '<TD NOWRAP><FONT COLOR="#CC0000" SIZE=3><B>&#149;</B></FONT><FONT FACE="Arial, Helvetica" SIZE=1><B><A HREF="%schannels/%s.html">%s</A></B></FONT>&nbsp;</TD>\n' % (pre, key, style)
    return '''<TABLE WIDTH=620 BORDER=0 CELLSPACING=0 CELLPADDING=0 BGCOLOR="#666699"><TR><TD><FONT FACE="Arial, Helvetica" SIZE=1 COLOR="#FFFFCC">&nbsp;&nbsp;<B>PICK A TOPIC:</B></FONT></TD></TR></TABLE>
<TABLE WIDTH=620 BORDER=0 CELLSPACING=0 CELLPADDING=3 BGCOLOR="#CCCC99"><TR>
%s</TR></TABLE>
''' % cells


def footer(pre):
    return '''<TABLE WIDTH=620 BORDER=0 CELLSPACING=0 CELLPADDING=4><TR><TD ALIGN=CENTER><FONT FACE="Arial, Helvetica" SIZE=1>
<A HREF="%(pre)sabout.html">About Reeves</A> | <A HREF="%(pre)sabout.html#help">Help</A> | <A HREF="%(pre)sabout.html#privacy">Privacy</A> |
<A HREF="%(pre)speek.html">Peek Through the Keyhole</A> | <A HREF="%(pre)s../altavisor/index.html">AltaVisor</A> | <A HREF="%(pre)s../yowza/index.html">Yowza!</A><BR>
Copyright &copy; 1996-99 Ask Reeves, Inc. All rights reserved. Reeves is a butler; he is not a doctor, lawyer or stockbroker.</FONT></TD></TR></TABLE>
''' % dict(pre=pre)


# ================================================================ data for JavaScript
def rule_url(rule, pre=''):
    """static version of the JS resolver, for links written into pages"""
    kind, _, arg = rule.partition(':')
    if kind == 'yz':
        return '%s../yowza/dir/%s/index.html' % (pre, arg)
    if kind == 'yzs':
        return '%s../yowza/search.html?p=%s' % (pre, arg.replace(' ', '+'))
    if kind == 'av':
        return '%s../altavisor/results.html?q=%s' % (pre, arg.replace(' ', '+'))
    if kind == 'avimg':
        return '%s../altavisor/results.html?stype=simage&amp;q=%s' % (pre, arg.replace(' ', '+'))
    if kind == 'site':
        return '%s../%s/index.html' % (pre, arg)
    if kind == 'web':
        return '%s../altavisor/web/%s/index.html' % (pre, arg)
    if kind == 'url':
        return pre + arg
    raise ValueError(rule)


def check_rules():
    """every web: rule must point at an invented homepage that really exists"""
    sys.path.insert(0, os.path.join(SITES, 'yowza', 'tools'))
    sys.path.insert(0, os.path.join(SITES, 'altavisor', 'tools'))
    import yowza_data, inventedweb
    hosts = {s['host'] for s in yowza_data.invented_sites()} | {h for h, _, _, _ in inventedweb.EXTRA_PAGES}
    bad = []
    for q in R.Q:
        rules = [q[5]] + [o.split('=', 1)[1] for sl in q[3] for o in sl if '=' in o]
        if q[6]:
            rules += [r for _, r in q[6][1]]
        for r in rules:
            if r.startswith('web:') and r[4:] not in hosts:
                bad.append((q[0], r))
    if bad:
        raise SystemExit('unknown invented hosts: %r' % bad)


def data_js():
    lines = ['// Ask Reeves question database - written by tools/gen_askreeves.py from tools/rs_data.py',
             '// Q[i] = id, topic, question, slots (options ~, slots ^, option=rule), keywords, rule, has own answer page',
             'var Q = new Array();']
    for i, (qid, topic, text, slots, kw, rule, ans) in enumerate(R.Q):
        sl = '^'.join('~'.join(opts) for opts in slots)
        lines.append('Q[%d] = new Array(%s, %s, %s, %s, %s, %s, %d);' % (i, js_str(qid), js_str(topic), js_str(text), js_str(sl),
                                                                        js_str(kw), js_str(rule), 1 if ans else 0))
    lines.append('var PEEK = new Array(%s);' % ',\n  '.join(js_str(p) for p in R.PEEK))
    lines.append('var QUIPS = new Array(%s);' % ', '.join(js_str(p) for p in R.QUIPS))
    lines.append('var NOMATCH = new Array(%s);' % ', '.join(js_str(p) for p in R.NO_MATCH))
    write('rs_data.js', '\n'.join(lines) + '\n')


COMMON_JS = r'''function getArg(name) {
  var q = location.search.substring(1).split('&');
  for (var i = 0; i < q.length; i++) {
    var kv = q[i].split('=');
    if (kv[0] == name && kv.length > 1) return unescape(kv[1].replace(/\+/g, ' '));
  }
  return '';
}
function h(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
function getCookie(n) {
  var all = document.cookie.split('; ');
  for (var i = 0; i < all.length; i++) if (all[i].indexOf(n + '=') == 0) return unescape(all[i].substring(n.length + 1));
  return '';
}
'''

# ================================================================ home page
def home_page():
    body = topbar('') + '''<TABLE BORDER=0 CELLSPACING=0 CELLPADDING=0 BGCOLOR="#FFFFCC" WIDTH=620>
<TR><TD WIDTH=170 VALIGN=TOP ROWSPAN=2><IMG SRC="images/reeves.gif" WIDTH=140 HEIGHT=220 HSPACE=15 VSPACE=8 ALT="Reeves"></TD>
<TD VALIGN=TOP><IMG SRC="images/tagline.gif" WIDTH=260 HEIGHT=62 VSPACE=10 ALT="Ask Reeves - your questions, answered with dignity"></TD>
<TD ALIGN=RIGHT VALIGN=TOP WIDTH=150><FONT FACE="Arial, Helvetica" SIZE=1><BR>
<A HREF="#" onClick="alert('To make Ask Reeves your home page, open your browser preferences and type this address in the Home Page box. Reeves will be waiting each morning with the papers.'); return false;">Make Reeves your<BR>home page &raquo;</A></FONT></TD></TR>
<TR><TD VALIGN=TOP COLSPAN=2>
<FORM NAME="askf" METHOD=GET ACTION="answer.html" onSubmit="return checkAsk(this)">
<TABLE WIDTH=420 BORDER=0>
<TR><TD><FONT SIZE=2>Just type a question in plain English and click &quot;Ask!&quot;</FONT></TD><TD>&nbsp;</TD></TR>
<TR><TD ALIGN=CENTER><TABLE BORDER=0 CELLSPACING=0 CELLPADDING=2 BGCOLOR="#999966"><TR><TD>
<INPUT TYPE=text NAME=ask SIZE=40 VALUE=""></TD></TR></TABLE></TD>
<TD VALIGN=TOP><INPUT TYPE=image SRC="images/ask.gif" WIDTH=36 HEIGHT=23 BORDER=0 ALT="Ask!"></TD></TR>
<TR><TD ALIGN=RIGHT><INPUT TYPE=checkbox NAME=spell VALUE=on CHECKED><FONT SIZE=1 FACE="Verdana, Arial, Helvetica">CHECK MY SPELLING, REEVES</FONT></TD><TD></TD></TR>
</TABLE></FORM>
<FORM NAME="rotate" METHOD=GET ACTION="answer.html">
<TABLE WIDTH=420 BORDER=0>
<TR><TD COLSPAN=2><FONT FACE="Arial, Helvetica" SIZE=2>&nbsp;&nbsp;What other guests are asking Reeves right now:</FONT></TD></TR>
<TR><TD><TABLE BORDER=0 CELLSPACING=0 CELLPADDING=1><TR><TD BGCOLOR="#999966">
<TEXTAREA NAME=ask ROWS=3 COLS=34 WRAP=virtual>How do I get the hamster song out of my head?</TEXTAREA></TD>
<TD VALIGN=TOP>&nbsp;<INPUT TYPE=image SRC="images/ask.gif" WIDTH=36 HEIGHT=23 BORDER=0 ALT="Ask!"></TD></TR></TABLE></TD>
<TD VALIGN=TOP ALIGN=CENTER><A HREF="peek.html"><IMG SRC="images/keyhole.gif" WIDTH=45 HEIGHT=60 BORDER=0 ALT="Peek through the keyhole"></A><BR><FONT FACE="Arial, Helvetica" SIZE=1><A HREF="peek.html">Peek through<BR>the keyhole</A></FONT></TD></TR>
</TABLE></FORM>
</TD></TR></TABLE>
''' + channel_bar('') + '''<TABLE WIDTH=620 BORDER=0 CELLSPACING=0 CELLPADDING=6 BGCOLOR="#FFFFFF"><TR>
<TD VALIGN=TOP WIDTH=310><FONT FACE="Arial, Helvetica" SIZE=2><B>Reeves recommends</B></FONT><BR>
<FONT FACE="Arial, Helvetica" SIZE=2>
<IMG SRC="images/dot.gif" WIDTH=10 HEIGHT=10> <A HREF="answer.html?ask=Is+my+computer+ready+for+the+year+2000%3F">Is my computer ready for the year 2000?</A><BR>
<IMG SRC="images/dot.gif" WIDTH=10 HEIGHT=10> <A HREF="answer.html?ask=Where+can+I+see+the+dancing+hamsters%3F">Where can I see the dancing hamsters?</A><BR>
<IMG SRC="images/dot.gif" WIDTH=10 HEIGHT=10> <A HREF="answer.html?ask=What+is+a+good+gift+for+a+computer+nerd%3F">What is a good gift for a computer nerd?</A><BR>
<IMG SRC="images/dot.gif" WIDTH=10 HEIGHT=10> <A HREF="answer.html?ask=How+do+I+build+my+own+home+page%3F">How do I build my own home page?</A>
</FONT></TD>
<TD VALIGN=TOP><FONT FACE="Arial, Helvetica" SIZE=2><B>Did you know?</B></FONT><BR>
<FONT FACE="Arial, Helvetica" SIZE=2>
<SCRIPT LANGUAGE="JavaScript">
<!--
var dyk = new Array('Reeves has answered more than four million questions, and raised an eyebrow at roughly half of them.',
  'The most popular question this week involves hamsters. It usually does.',
  'Reeves irons the newspaper every morning, including the Web pages.',
  'You may ask Reeves anything at all. He will not repeat it, except through the keyhole.',
  'A butler never runs. Reeves does, however, return answers in under a second.');
document.write(dyk[Math.floor(Math.random() * dyk.length)]);
// -->
</SCRIPT>
<NOSCRIPT>The most popular question this week involves hamsters. It usually does.</NOSCRIPT>
<BR><A HREF="channels/popular.html">More popular questions &raquo;</A></FONT></TD></TR></TABLE>
<TABLE WIDTH=620 BORDER=0 CELLSPACING=0 CELLPADDING=0><TR><TD BGCOLOR="#666699"><IMG SRC="images/pixel.gif" WIDTH=1 HEIGHT=3></TD></TR></TABLE>
''' + footer('') + '''<SCRIPT LANGUAGE="JavaScript" SRC="rs_data.js"></SCRIPT>
<SCRIPT LANGUAGE="JavaScript">
<!--
var n = 0;
function rotate() {
  if (typeof PEEK == 'undefined') return;
  document.rotate.ask.value = PEEK[n % PEEK.length];
  n++;
  setTimeout('rotate()', 3500);
}
function checkAsk(f) {
  if (f.ask.value.replace(/ /g, '') == '') { alert('I beg your pardon? You did not ask anything. Please type a question in the box.'); return false; }
  return true;
}
n = Math.floor(Math.random() * 40);
rotate();
// -->
</SCRIPT>
'''
    write('index.html', page('Ask Reeves!', body, ''))


# ================================================================ the answer page
ANSWER_JS = r'''<SCRIPT LANGUAGE="JavaScript" SRC="rs_data.js"></SCRIPT>
<SCRIPT LANGUAGE="JavaScript">
<!--
''' + COMMON_JS + r'''
var STOP = ' a an and are as at be by can could do does for from get how i if in into is it me my of on or our please some tell that the there this to was what when where which who why will with would you your find information about out any good best should there their them they want need know ';
var FIX = new Object();   // Reeves' spell checker: common 1999 typos
FIX['teh'] = 'the'; FIX['recieve'] = 'receive'; FIX['hampster'] = 'hamster'; FIX['hampsters'] = 'hamsters'; FIX['pictres'] = 'pictures';
FIX['computor'] = 'computer'; FIX['definately'] = 'definitely'; FIX['interent'] = 'internet'; FIX['millenium'] = 'millennium';
FIX['y2k'] = 'y2k'; FIX['webpage'] = 'web page'; FIX['homepage'] = 'home page'; FIX['dawg'] = 'dog'; FIX['kitty'] = 'cat';
function stem(w) {
  if (w.length > 4 && w.substring(w.length - 3) == 'ies') return w.substring(0, w.length - 3) + 'y';
  if (w.length > 3 && w.charAt(w.length - 1) == 's' && w.charAt(w.length - 2) != 's') return w.substring(0, w.length - 1);
  return w;
}
function tokens(s) {
  var raw = s.toLowerCase().replace(/[^a-z0-9' ]/g, ' ').split(' '), out = new Array();
  for (var i = 0; i < raw.length; i++) {
    var w = raw[i].replace(/'s$/, '').replace(/'/g, '');
    if (w == '') continue;
    out[out.length] = w;
  }
  return out;
}
function content(ws) {
  var out = new Array();
  for (var i = 0; i < ws.length; i++) if (STOP.indexOf(' ' + ws[i] + ' ') < 0) out[out.length] = ws[i];
  return out;
}
function bag(s) { var t = tokens(s), b = ' '; for (var i = 0; i < t.length; i++) b += stem(t[i]) + ' '; return b; }
function inBag(b, w) { return b.indexOf(' ' + stem(w) + ' ') >= 0; }
function label(o) { return o.split('=')[0]; }
function optRule(o) { var k = o.indexOf('='); return k < 0 ? '' : o.substring(k + 1); }

var ask = getArg('ask'), spell = getArg('spell'), fixed = '';
if (spell == 'on') {
  var t = ask.split(' '), changed = false;
  for (var i = 0; i < t.length; i++) { var k = t[i].toLowerCase().replace(/[^a-z0-9]/g, ''); if (FIX[k] != null && FIX[k] != k) { t[i] = FIX[k]; changed = true; } }
  if (changed) { fixed = ask; ask = t.join(' '); }
}
var words = content(tokens(ask));
if (words.length == 0) { var all = tokens(ask); for (var i = 0; i < all.length; i++) if (all[i].length > 2) words[words.length] = all[i]; }

// score every question in the database
var found = new Array();
for (var i = 0; i < Q.length; i++) {
  var slots = Q[i][3].split('^'), kw = bag(Q[i][4] + ' ' + Q[i][2]), score = 0, picks = new Array();
  for (var s = 0; s < slots.length; s++) {
    var opts = slots[s].split('~'), best = 0, bestScore = 0;
    for (var o = 0; o < opts.length; o++) {
      var lb = bag(label(opts[o])), sc = 0;
      for (var w = 0; w < words.length; w++) if (inBag(lb, words[w])) sc++;
      if (sc > bestScore) { bestScore = sc; best = o; }
    }
    picks[s] = best;
    score += bestScore * 3;
  }
  for (var w = 0; w < words.length; w++) if (inBag(kw, words[w])) score++;
  if (score > 0) found[found.length] = new Array(score, i, picks);
}
found.sort(function (a, b) { return b[0] - a[0]; });
if (found.length > 5) found = found.slice(0, 5);
if (found.length > 1 && found[0][0] >= 4) { var cut = new Array(); for (var i = 0; i < found.length; i++) if (found[i][0] >= 2) cut[cut.length] = found[i]; found = cut; }

// remember the question for the keyhole page (this browser only)
if (ask != '') {
  var mine = getCookie('rsasked'), list = mine == '' ? new Array() : mine.split('^');
  list[list.length] = ask.substring(0, 120);
  while (list.length > 10) list = list.slice(1);
  var exp = new Date(); exp.setTime(exp.getTime() + 7 * 24 * 3600 * 1000);
  document.cookie = 'rsasked=' + escape(list.join('^')) + '; expires=' + exp.toGMTString() + '; path=/';
}

function fill(rule, sel) {
  for (var k = 0; k < sel.length; k++) rule = rule.split('{' + k + '}').join(sel[k]);
  return rule;
}
function resolve(rule, sel, id) {
  var kind = rule.substring(0, rule.indexOf(':')), arg = rule.substring(rule.indexOf(':') + 1);
  if (rule == 'ans') return 'ans/' + id + '.html?a=' + escape(sel[0] || '') + '&b=' + escape(sel[1] || '');
  arg = fill(arg, sel);
  if (kind == 'yz') return '../yowza/dir/' + arg + '/index.html';
  if (kind == 'yzs') return '../yowza/search.html?p=' + escape(arg);
  if (kind == 'av') return '../altavisor/results.html?q=' + escape(arg);
  if (kind == 'avimg') return '../altavisor/results.html?stype=simage&q=' + escape(arg);
  if (kind == 'site') return '../' + arg + '/index.html';
  if (kind == 'web') return '../altavisor/web/' + arg + '/index.html';
  if (kind == 'url') return arg;
  return '../altavisor/results.html?q=' + escape(arg);
}
// the Ask! button next to each question
function go(n) {
  var f = document.forms['qf' + n], qi = parseInt(f.qi.value), sel = new Array(), rule = '';
  if (qi < 0) {   // one of Reeves' improvised questions
    var v = f.s0.options[f.s0.selectedIndex].text;
    location.href = resolve(f.rule.value, new Array(v), '');
    return false;
  }
  var slots = Q[qi][3].split('^');
  for (var s = 0; s < slots.length; s++) {
    var o = slots[s].split('~')[f['s' + s].selectedIndex];
    sel[s] = label(o);
    if (rule == '' && optRule(o) != '') rule = optRule(o);
  }
  if (rule == '') rule = Q[qi][5];
  if (rule == 'opt') rule = 'av:' + sel.join(' ');
  location.href = resolve(rule, sel, Q[qi][0]);
  return false;
}
function questionHtml(n, qi, picks) {
  var text = Q[qi][2], slots = Q[qi][3].split('^');
  var out = '<FORM NAME="qf' + n + '" onSubmit="return go(' + n + ')"><INPUT TYPE=hidden NAME=qi VALUE="' + qi + '"><TABLE WIDTH=620 BORDER=0 CELLSPACING=0 CELLPADDING=4><TR><TD VALIGN=TOP WIDTH=46><INPUT TYPE=image SRC="images/ask.gif" WIDTH=36 HEIGHT=23 BORDER=0 ALT="Ask!"></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>';
  for (var s = 0; s < slots.length; s++) {
    var opts = slots[s].split('~'), sel = '<SELECT NAME="s' + s + '">';
    for (var o = 0; o < opts.length; o++) sel += '<OPTION' + (o == picks[s] ? ' SELECTED' : '') + '>' + h(label(opts[o]));
    sel += '</SELECT>';
    text = text.split('[' + s + ']').join('\u0001' + s + '\u0001');
    slots[s] = sel;
  }
  var parts = text.split('\u0001');
  for (var p = 0; p < parts.length; p++) out += (p % 2 == 1) ? slots[parseInt(parts[p])] : h(parts[p]);
  return out + '</FONT></TD></TR></TABLE></FORM>';
}
function improvised(n, pattern, rule) {
  var sel = '<SELECT NAME="s0">';
  for (var w = 0; w < words.length && w < 8; w++) sel += '<OPTION>' + h(words[w]);
  if (words.length > 1) sel += '<OPTION SELECTED>' + h(words.join(' '));
  sel += '</SELECT>';
  return '<FORM NAME="qf' + n + '" onSubmit="return go(' + n + ')"><INPUT TYPE=hidden NAME=qi VALUE="-1"><INPUT TYPE=hidden NAME=rule VALUE="' + rule + '"><TABLE WIDTH=620 BORDER=0 CELLSPACING=0 CELLPADDING=4><TR><TD VALIGN=TOP WIDTH=46><INPUT TYPE=image SRC="images/ask.gif" WIDTH=36 HEIGHT=23 BORDER=0 ALT="Ask!"></TD><TD><FONT FACE="Arial, Helvetica" SIZE=2>' + h(pattern).replace('[]', sel) + '</FONT></TD></TR></TABLE></FORM>';
}
// -->
</SCRIPT>
'''

ANSWER_BODY = r'''<SCRIPT LANGUAGE="JavaScript">
<!--
var quip = ask == '' ? 'Good day. You did not ask anything, but I have prepared a few questions you might enjoy:'
         : (found.length > 0 ? QUIPS[Math.floor(Math.random() * QUIPS.length)] : NOMATCH[Math.floor(Math.random() * NOMATCH.length)]);
function qIndex(id) { for (var i = 0; i < Q.length; i++) if (Q[i][0] == id) return i; return 0; }
if (ask == '') { found = new Array(); var picks = new Array(0, 0); found[0] = new Array(1, qIndex('y2k_ready'), picks); found[1] = new Array(1, qIndex('dancing_hamsters'), picks); found[2] = new Array(1, qIndex('bored'), picks); }
document.write('<TABLE WIDTH=620 BORDER=0 CELLSPACING=0 CELLPADDING=6 BGCOLOR="#FFFFCC"><TR><TD VALIGN=TOP WIDTH=70><IMG SRC="images/reeves_sm.gif" WIDTH=60 HEIGHT=70 ALT="Reeves"></TD><TD VALIGN=TOP>');
if (ask != '') document.write('<FONT FACE="Arial, Helvetica" SIZE=2>You asked: <B>' + h(ask) + '</B>' + (fixed != '' ? ' <FONT SIZE=1>(I took the liberty of correcting your spelling of &quot;' + h(fixed) + '&quot;.)</FONT>' : '') + '</FONT><P>');
document.write('<FONT FACE="Times New Roman, Times" SIZE=3><I>' + quip + '</I></FONT></TD></TR></TABLE>');
var n = 0;
for (var i = 0; i < found.length; i++) document.write(questionHtml(n++, found[i][1], found[i][2]));
if (words.length > 0 && found.length < 4) {
  document.write(improvised(n++, 'Where can I find an encyclopedia-style page about []?', 'av:{0}'));
  document.write(improvised(n++, 'What does the Yowza! directory list under []?', 'yzs:{0}'));
  if (found.length < 2) document.write(improvised(n++, 'Where can I see pictures of []?', 'avimg:{0}'));
}
// the "metasearch" section
if (words.length > 0) {
  var kw = words.join(' ');
  document.write('<P><TABLE WIDTH=620 BORDER=0 CELLSPACING=0 CELLPADDING=4 BGCOLOR="#CCCC99"><TR><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>You may also find my search results useful:</B></FONT></TD></TR></TABLE>');
  document.write('<FORM NAME="meta" onSubmit="location.href = this.eng.options[this.eng.selectedIndex].value; return false;"><TABLE WIDTH=620 BORDER=0 CELLPADDING=4><TR><TD><FONT FACE="Arial, Helvetica" SIZE=2>');
  document.write('I sent a footman round to ask my colleagues about <B>' + h(kw) + '</B>. See what <SELECT NAME=eng>');
  document.write('<OPTION VALUE="../altavisor/results.html?q=' + escape(kw) + '">AltaVisor found on the Web');
  document.write('<OPTION VALUE="../yowza/search.html?p=' + escape(kw) + '">Yowza! has in its directory');
  document.write('<OPTION VALUE="../altavisor/results.html?stype=simage&q=' + escape(kw) + '">AltaVisor found in pictures');
  document.write('<OPTION VALUE="../cnm/index.html">CNM has in the news');
  document.write('<OPTION VALUE="../dashdot/index.html">the nerds at Dashdot think');
  document.write('</SELECT> <INPUT TYPE=image SRC="images/ask.gif" WIDTH=36 HEIGHT=23 BORDER=0 ALT="Ask!" ALIGN=ABSMIDDLE></FONT></TD></TR></TABLE></FORM>');
}
// -->
</SCRIPT>
<NOSCRIPT><P><FONT FACE="Arial, Helvetica" SIZE=2>I am terribly sorry, but I can only read your question with JavaScript switched on.
In the meantime, may I suggest one of the <A HREF="channels/popular.html">popular questions</A>?</FONT></NOSCRIPT>
<P><FORM NAME="again" METHOD=GET ACTION="answer.html">
<TABLE WIDTH=620 BORDER=0 CELLSPACING=0 CELLPADDING=4 BGCOLOR="#FFFFCC"><TR><TD><FONT FACE="Arial, Helvetica" SIZE=2><B>Ask another question:</B></FONT><BR>
<TABLE BORDER=0 CELLSPACING=0 CELLPADDING=2 BGCOLOR="#999966"><TR><TD><INPUT TYPE=text NAME=ask SIZE=50></TD></TR></TABLE></TD>
<TD VALIGN=BOTTOM><INPUT TYPE=image SRC="images/ask.gif" WIDTH=36 HEIGHT=23 BORDER=0 ALT="Ask!"><INPUT TYPE=hidden NAME=spell VALUE=on></TD></TR></TABLE></FORM>
'''


def answer_page():
    body = topbar('') + ANSWER_BODY + channel_bar('') + footer('')
    write('answer.html', page('Ask Reeves: Answers', ANSWER_JS + body, ''))


# ================================================================ Reeves' own answers
def ans_pages():
    for qid, topic, text, slots, kw, rule, ans in R.Q:
        if not ans:
            continue
        reply, links = ans
        rel = 'ans/%s.html' % qid
        pre = up(rel)
        items = ''.join('<IMG SRC="%simages/dot.gif" WIDTH=10 HEIGHT=10> <A HREF="%s">%s</A><BR>\n' % (pre, rule_url(r, pre), esc(t)) for t, r in links)
        q_static = re.sub(r'\[(\d)\]', lambda m: label_of(slots[int(m.group(1))][0]), text)
        body = topbar(pre) + '''<TABLE WIDTH=620 BORDER=0 CELLSPACING=0 CELLPADDING=8 BGCOLOR="#FFFFCC"><TR>
<TD VALIGN=TOP WIDTH=150><IMG SRC="%(pre)simages/reeves.gif" WIDTH=140 HEIGHT=220 ALT="Reeves"></TD>
<TD VALIGN=TOP><FONT FACE="Arial, Helvetica" SIZE=2>You asked:</FONT><BR>
<FONT FACE="Times New Roman, Times" SIZE=4><B>
<SCRIPT LANGUAGE="JavaScript">
<!--
%(js)s
var a = getArg('a') || %(d0)s, b = getArg('b') || %(d1)s;
document.write(h(%(q)s.split('[0]').join(a).split('[1]').join(b)));
// -->
</SCRIPT>
<NOSCRIPT>%(qs)s</NOSCRIPT></B></FONT>
<P><FONT FACE="Times New Roman, Times" SIZE=3>
<SCRIPT LANGUAGE="JavaScript">
<!--
document.write(h(%(reply)s.split('{0}').join(a).split('{1}').join(b)));
// -->
</SCRIPT>
<NOSCRIPT>%(rs)s</NOSCRIPT></FONT>
<P><FONT FACE="Arial, Helvetica" SIZE=2><B>Reeves suggests:</B><BR>
%(items)s</FONT>
<P><FONT FACE="Arial, Helvetica" SIZE=1><A HREF="%(pre)sindex.html">Ask Reeves another question</A></FONT>
</TD></TR></TABLE>
''' % dict(pre=pre, js=COMMON_JS, d0=js_str(label_of(slots[0][0])), d1=js_str(label_of(slots[1][0]) if len(slots) > 1 else ''),
           q=js_str(text), qs=esc(q_static), reply=js_str(reply), rs=esc(reply.replace('{0}', label_of(slots[0][0]))), items=items) + channel_bar(pre) + footer(pre)
        write(rel, page('Ask Reeves: ' + q_static, body, pre))


def label_of(o):
    return o.split('=')[0]


# ================================================================ channels
def channel_pages():
    for key, label in TOPICS:
        rel = 'channels/%s.html' % key
        pre = up(rel)
        qs = [q for q in R.Q if q[1] == key]
        if key == 'popular':
            qs = [q for q in R.Q if q[1] == 'popular'] + [q for q in R.Q if q[0] in ('pet_pics', 'buy_books', 'y2k_ready', 'mp3', 'recipe', 'joke')]
        rows = ''
        for q in qs:
            for opt in q[3][0][:3]:
                lab = label_of(opt)
                text = q[2].replace('[0]', lab)
                if len(q[3]) > 1:
                    text = text.replace('[1]', label_of(q[3][1][0]))
                rows += '<IMG SRC="%simages/dot.gif" WIDTH=10 HEIGHT=10> <A HREF="%sanswer.html?ask=%s">%s</A><BR>\n' % (
                    pre, pre, re.sub(r'[^A-Za-z0-9]+', '+', text).strip('+') + '%3F', esc(text))
        body = topbar(pre) + channel_bar(pre, key) + '''<TABLE WIDTH=620 BORDER=0 CELLSPACING=0 CELLPADDING=8 BGCOLOR="#FFFFCC"><TR>
<TD VALIGN=TOP WIDTH=70><IMG SRC="%(pre)simages/reeves_sm.gif" WIDTH=60 HEIGHT=70 ALT="Reeves"></TD>
<TD VALIGN=TOP><FONT FACE="Arial, Helvetica" SIZE=4 COLOR="#666699"><B>%(title)s</B></FONT><BR>
<FONT FACE="Times New Roman, Times" SIZE=3><I>%(intro)s</I></FONT><P>
<FONT FACE="Arial, Helvetica" SIZE=2>%(rows)s</FONT></TD></TR></TABLE>
''' % dict(pre=pre, title=label.title(), rows=rows,
           intro='Questions our guests ask most often about %s. Click any of them and I shall see to it.' % label.lower()
           if key != 'kids' else 'Hello, young sir or madam. Here are questions other children have asked me. Do mind your manners online.') + footer(pre)
        write(rel, page('Ask Reeves: ' + label.title(), body, pre))


# ================================================================ the keyhole
def peek_page():
    noscript = ''.join('<IMG SRC="images/dot.gif" WIDTH=10 HEIGHT=10> <A HREF="answer.html?ask=%s">%s</A><BR>\n' % (
        re.sub(r'[^A-Za-z0-9]+', '+', p).strip('+'), esc(p)) for p in R.PEEK[:15])
    body = topbar('') + '''<TABLE WIDTH=620 BORDER=0 CELLSPACING=0 CELLPADDING=8 BGCOLOR="#FFFFCC"><TR>
<TD VALIGN=TOP WIDTH=100><IMG SRC="images/keyhole.gif" WIDTH=90 HEIGHT=120 ALT="The keyhole"></TD>
<TD VALIGN=TOP><FONT FACE="Arial, Helvetica" SIZE=4 COLOR="#666699"><B>Peek Through the Keyhole</B></FONT><BR>
<FONT FACE="Times New Roman, Times" SIZE=3><I>A good butler never listens at doors. A good butler does, however, occasionally
glance through the keyhole. Here is what other guests are asking me at this very moment. Names have been withheld, out of discretion.</I></FONT>
<P><FORM NAME="peek" METHOD=GET ACTION="answer.html" onSubmit="return askSel();">
<SELECT NAME=list SIZE=12 WIDTH=400 onChange="document.peek.ask.value = this.options[this.selectedIndex].text.replace(/^.* - /, '');">
<OPTION>Peeking...
</SELECT><BR>
<INPUT TYPE=hidden NAME=ask VALUE="">
<FONT FACE="Arial, Helvetica" SIZE=2>Pick a question and </FONT><INPUT TYPE=image SRC="images/ask.gif" WIDTH=36 HEIGHT=23 BORDER=0 ALT="Ask!" ALIGN=ABSMIDDLE>
<FONT FACE="Arial, Helvetica" SIZE=1>&nbsp; The view refreshes every few seconds. <A HREF="#" onClick="paused = !paused; this.blur(); return false;">Pause / resume</A></FONT>
</FORM>
<NOSCRIPT><FONT FACE="Arial, Helvetica" SIZE=2>%(noscript)s</FONT></NOSCRIPT>
<FONT FACE="Arial, Helvetica" SIZE=2><B>Your own recent questions</B> (only you can see these):</FONT><BR>
<FONT FACE="Arial, Helvetica" SIZE=2>
<SCRIPT LANGUAGE="JavaScript">
<!--
var mine = getCookie('rsasked');
if (mine == '') document.write('<I>None yet. Reeves is waiting.</I>');
else { var m = mine.split('^'); for (var i = m.length - 1; i >= 0; i--) document.write('<IMG SRC="images/dot.gif" WIDTH=10 HEIGHT=10> <A HREF="answer.html?ask=' + escape(m[i]) + '">' + h(m[i]) + '</A><BR>'); }
// -->
</SCRIPT></FONT>
</TD></TR></TABLE>
<SCRIPT LANGUAGE="JavaScript">
<!--
var shown = new Array(), ages = new Array(), paused = false, pool = PEEK.slice(0);
var own = getCookie('rsasked');
if (own != '') pool = pool.concat(own.split('^'));
function pickOne() { return pool[Math.floor(Math.random() * pool.length)]; }
for (var i = 0; i < 12; i++) { shown[i] = pickOne(); ages[i] = 4 + i * 6 + Math.floor(Math.random() * 5); }
function draw() {
  var sel = document.peek.list;
  for (var i = 0; i < shown.length; i++) {
    var t = ages[i] < 60 ? ages[i] + ' sec ago' : Math.floor(ages[i] / 60) + ' min ago';
    sel.options[i] = new Option(t + ' - ' + shown[i], shown[i]);
  }
}
function tick() {
  if (!paused) {
    for (var i = 0; i < ages.length; i++) ages[i] += 4;
    shown = new Array(pickOne()).concat(shown.slice(0, 11));
    ages = new Array(Math.floor(Math.random() * 3)).concat(ages.slice(0, 11));
    draw();
  }
  setTimeout('tick()', 4000);
}
function askSel() {
  var sel = document.peek.list;
  if (sel.selectedIndex < 0) { alert('Please choose a question from the list first. Quickly, before it moves.'); return false; }
  document.peek.ask.value = sel.options[sel.selectedIndex].value;
  return true;
}
draw();
setTimeout('tick()', 4000);
// -->
</SCRIPT>
''' % dict(noscript=noscript) + channel_bar('') + footer('')
    head = '<SCRIPT LANGUAGE="JavaScript" SRC="rs_data.js"></SCRIPT>\n<SCRIPT LANGUAGE="JavaScript">\n<!--\n' + COMMON_JS + '// -->\n</SCRIPT>\n'
    write('peek.html', page('Ask Reeves: Peek Through the Keyhole', head + body, ''))


def about_page():
    body = topbar('') + '''<TABLE WIDTH=620 BORDER=0 CELLSPACING=0 CELLPADDING=8 BGCOLOR="#FFFFCC"><TR>
<TD VALIGN=TOP WIDTH=150><IMG SRC="images/reeves.gif" WIDTH=140 HEIGHT=220 ALT="Reeves"></TD>
<TD VALIGN=TOP><FONT FACE="Arial, Helvetica" SIZE=4 COLOR="#666699"><B>About Reeves</B></FONT>
<P><FONT FACE="Times New Roman, Times" SIZE=3>
Reeves entered service at the age of fourteen, polishing the doorknobs of a large country house. By twenty he was
under-butler; by thirty he could tell, from the sound of the front door, whether a guest wanted tea or a stiff drink.
In 1996 he came to the World Wide Web, where the guests are more numerous and considerably more curious.
<P>Reeves reads your question, sets aside the little words, and considers which of the many thousands of questions in
his files you most likely meant. He then offers you those questions, with small menus so that you may adjust the
particulars, and an <B>Ask!</B> button beside each. When he does not know, he sends a footman round to his colleagues
at <A HREF="../altavisor/index.html">AltaVisor</A> and <A HREF="../yowza/index.html">Yowza!</A>.
<P><A NAME="help"></A><B>How to ask</B><BR>
Type a question as you would ask a person: <I>Where can I buy books online?</I> Full sentences are welcome; Reeves was
raised properly. Then choose the question that fits best, adjust the menus, and press <B>Ask!</B>.
Leave <I>check my spelling</I> ticked and Reeves will quietly correct a few common slips.
<P><A NAME="privacy"></A><B>Discretion</B><BR>
Your recent questions are kept in a cookie in your own browser so that you can find them again on the keyhole page.
Reeves keeps no other record. A butler hears everything and repeats nothing.
</FONT></TD></TR></TABLE>
''' + channel_bar('') + footer('')
    write('about.html', page('About Ask Reeves', body, ''))


def main():
    check_rules()
    data_js(); home_page(); answer_page(); ans_pages(); channel_pages(); peek_page(); about_page()
    n = sum(len(fs) for _, fs in [(d, [f for f in fs if f.endswith('.html')]) for d, _, fs in os.walk(ROOT)])
    print('Ask Reeves generated: %d questions, %d HTML pages' % (len(R.Q), n))


if __name__ == '__main__':
    main()
