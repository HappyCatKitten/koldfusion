"""gh_render.py -- turn a planned GeoHoods homepage into 1999 HTML files.

Every URL is relative: a member page lives at <Hood>/<Suburb>/<num>/ so the site root is "../../../".
"""
import re

from gh_people import fmt_date

# ------------------------------------------------------------------ visual styles
# keys: bgcolor background text link vlink face size hcolor hface align box navbg margin
STYLES = {
    'starfield': dict(bgcolor='#000000', background='stars_bg.gif', text='#FFFF00', link='#00FFFF', vlink='#FF66FF',
                      face='Arial, Helvetica', hcolor='#00FF00', hface='Arial Black, Arial', align='CENTER',
                      navbg='#000066'),
    'nebula': dict(bgcolor='#110022', background='bg_nebula.gif', text='#CCCCFF', link='#FF99FF', vlink='#CC99FF',
                   face='Verdana, Arial', hcolor='#FFFFFF', hface='Verdana', align='CENTER', navbg='#330066'),
    'black_neon': dict(bgcolor='#000000', text='#FF00FF', link='#00FFFF', vlink='#FFFF00', face='Comic Sans MS',
                       hcolor='#00FF00', hface='Comic Sans MS', align='CENTER', navbg='#333333'),
    'hacker': dict(bgcolor='#000000', background='bg_binary.gif', text='#00FF00', link='#FFFFFF', vlink='#99FF99',
                   face='Courier New, Courier', hcolor='#00FF00', hface='Courier New', align=None, navbg='#003300',
                   box='#000000'),
    'pastel_hearts': dict(bgcolor='#FFE6F0', background='bg_hearts.gif', text='#993366', link='#CC0066',
                          vlink='#9900CC', face='Comic Sans MS', hcolor='#FF3399', hface='Comic Sans MS',
                          align='CENTER', navbg='#FFCCE6'),
    'pastel_flowers': dict(bgcolor='#F0E6FF', background='bg_flowers.gif', text='#663399', link='#9933CC',
                           vlink='#CC66CC', face='Comic Sans MS', hcolor='#9900CC', hface='Comic Sans MS',
                           align='CENTER', navbg='#E6CCFF'),
    'glitter': dict(bgcolor='#FF99CC', background='bg_glitter.gif', text='#660033', link='#0000CC', vlink='#660099',
                    face='Comic Sans MS', hcolor='#FFFFFF', hface='Comic Sans MS', align='CENTER', navbg='#FF66B2',
                    box='#FFE6F2'),
    'default_gray': dict(bgcolor='#C0C0C0', text='#000000', link='#0000FF', vlink='#800080', face=None, hcolor=None,
                         hface=None, align=None, navbg='#A0A0A0'),
    'plain': dict(bgcolor='#FFFFFF', text='#000000', link='#0000EE', vlink='#551A8B', face='Times New Roman',
                  hcolor='#000080', hface=None, align=None, navbg='#DDDDDD'),
    'border_blue': dict(bgcolor='#C8DCFF', background='bg_border_blue.gif', text='#000066', link='#0000CC',
                        vlink='#663399', face='Arial, Helvetica', hcolor='#000099', hface='Arial', align=None,
                        margin=True, navbg='#99BBFF'),
    'border_purple': dict(bgcolor='#F0E1FF', background='bg_border_purple.gif', text='#330066', link='#6600CC',
                          vlink='#993399', face='Verdana, Arial', hcolor='#660099', hface='Verdana', align=None,
                          margin=True, navbg='#CC99FF'),
    'border_green': dict(bgcolor='#EBFFE1', background='bg_border_green.gif', text='#003300', link='#006600',
                         vlink='#336633', face='Arial, Helvetica', hcolor='#006600', hface='Arial', align=None,
                         margin=True, navbg='#99CC99'),
    'border_pink': dict(bgcolor='#FFF0F8', background='bg_border_pink.gif', text='#990066', link='#CC0066',
                        vlink='#993399', face='Comic Sans MS', hcolor='#FF0099', hface='Comic Sans MS', align=None,
                        margin=True, navbg='#FFCCE6'),
    'border_flames': dict(bgcolor='#140000', background='bg_border_flames.gif', text='#FFCC00', link='#FF6600',
                          vlink='#FF3300', face='Arial, Helvetica', hcolor='#FF3300', hface='Impact, Arial Black',
                          align=None, margin=True, navbg='#330000'),
    'goth': dict(bgcolor='#000000', background='bg_blood.gif', text='#CC0000', link='#999999', vlink='#666666',
                 face='Times New Roman', hcolor='#990000', hface='Times New Roman', align='CENTER', navbg='#220000',
                 italic=True),
    'parchment': dict(bgcolor='#EEE1BE', background='bg_parchment.gif', text='#333300', link='#663300',
                      vlink='#996633', face='Georgia, Times New Roman', hcolor='#663300', hface='Georgia', align=None,
                      navbg='#D9C59A'),
    'marble': dict(bgcolor='#E6E6EA', background='bg_marble.gif', text='#000066', link='#003399', vlink='#660066',
                   face='Times New Roman', hcolor='#000066', hface='Times New Roman', align='CENTER', navbg='#CCCCDD'),
    'brick': dict(bgcolor='#996633', background='bg_brick.gif', text='#000000', link='#990000', vlink='#663300',
                  face='Arial', hcolor='#990000', hface='Arial Black', align='CENTER', navbg='#FFFFCC', box='#FFFFCC'),
    'camo': dict(bgcolor='#6E7846', background='bg_camo.gif', text='#FFFF99', link='#FFFFFF', vlink='#CCCC99',
                 face='Courier New, Courier', hcolor='#FFFF00', hface='Impact, Arial Black', align=None,
                 navbg='#333300', box='#2A2A15'),
    'wood': dict(bgcolor='#966432', background='bg_wood.gif', text='#331100', link='#993300', vlink='#663300',
                 face='Arial, Helvetica', hcolor='#663300', hface='Georgia', align='CENTER', navbg='#E8D5B0',
                 box='#FFF8DC'),
    'gingham': dict(bgcolor='#FFAAAA', background='bg_gingham.gif', text='#660000', link='#CC0000', vlink='#990033',
                    face='Comic Sans MS, Arial', hcolor='#CC0000', hface='Comic Sans MS', align='CENTER',
                    navbg='#FFE6E6', box='#FFFFFF'),
    'clouds': dict(bgcolor='#78B4FF', background='bg_clouds.gif', text='#000080', link='#CC0000', vlink='#660099',
                   face='Comic Sans MS, Arial', hcolor='#0000CC', hface='Comic Sans MS', align='CENTER',
                   navbg='#CCE6FF', box='#FFFFFF'),
    'grass': dict(bgcolor='#289628', background='bg_grass.gif', text='#003300', link='#0000CC', vlink='#663399',
                  face='Arial, Helvetica', hcolor='#006600', hface='Arial Black', align='CENTER', navbg='#CCFFCC',
                  box='#F0FFF0'),
    'water': dict(bgcolor='#005AAA', background='bg_water.gif', text='#FFFFFF', link='#FFFF00', vlink='#CCFFFF',
                  face='Arial, Helvetica', hcolor='#FFFF99', hface='Arial Black', align='CENTER', navbg='#003366'),
    'bubbles': dict(bgcolor='#003C78', background='bg_bubbles.gif', text='#CCFFFF', link='#FFFF66', vlink='#99FFCC',
                    face='Comic Sans MS, Arial', hcolor='#FFFFFF', hface='Comic Sans MS', align='CENTER',
                    navbg='#002244'),
    'snow': dict(bgcolor='#0A1446', background='bg_snow.gif', text='#FFFFFF', link='#99CCFF', vlink='#CCCCFF',
                 face='Georgia, Times New Roman', hcolor='#CCFFFF', hface='Georgia', align='CENTER', navbg='#1E2860'),
    'leopard': dict(bgcolor='#E6B45A', background='bg_leopard.gif', text='#000000', link='#990066', vlink='#660033',
                    face='Verdana, Arial', hcolor='#FF0099', hface='Comic Sans MS', align='CENTER', navbg='#000000',
                    box='#FFE6F5'),
    'denim': dict(bgcolor='#28468C', background='bg_denim.gif', text='#FFFFFF', link='#FFCC00', vlink='#FFCC99',
                  face='Arial, Helvetica', hcolor='#FFFF00', hface='Arial Black', align='CENTER', navbg='#1C3366'),
    'checker': dict(bgcolor='#000000', background='bg_checker.gif', text='#000000', link='#CC0000', vlink='#660000',
                    face='Arial, Helvetica', hcolor='#CC0000', hface='Impact, Arial Black', align='CENTER',
                    navbg='#FFFF00', box='#FFFFFF'),
    'notebook': dict(bgcolor='#FFFFFF', background='bg_notebook.gif', text='#000099', link='#CC0000',
                     vlink='#990099', face='Comic Sans MS', hcolor='#CC0000', hface='Comic Sans MS', align=None,
                     margin=True, navbg='#E6E6FF'),
    'concrete': dict(bgcolor='#C3C3C3', background='bg_concrete.gif', text='#000000', link='#000099',
                     vlink='#660066', face='Arial, Helvetica', hcolor='#333333', hface='Arial Black', align=None,
                     navbg='#999999'),
    'pro_blue': dict(bgcolor='#FFFFFF', text='#000000', link='#003399', vlink='#663399', face='Verdana, Arial',
                     hcolor='#003399', hface='Verdana', align=None, navbg='#CCDDFF', header='#003399'),
    'retro_tan': dict(bgcolor='#FFFFCC', text='#663300', link='#996600', vlink='#663300', face='Arial, Helvetica',
                      hcolor='#993300', hface='Georgia', align='CENTER', navbg='#FFE699'),
    'paws': dict(bgcolor='#FFF5E1', background='bg_paws.gif', text='#663300', link='#CC6600', vlink='#996633',
                 face='Comic Sans MS, Arial', hcolor='#996600', hface='Comic Sans MS', align='CENTER',
                 navbg='#FFE6C2'),
}

GENERATORS = ['GeoHoods Build-a-Page 2.1', 'Pioneer Composer 4.5', 'FrontDoor Page Express 98', 'Notepad (by hand!)',
              'HotDog-style HTML Editor 5', 'WordPad', 'Pioneer Composer 4.06', 'GeoHoods EZ Editor']

MIDI_TITLES = {}


def sub(text, v):
    """replace {key} placeholders (unknown keys stay as they are)"""
    if not isinstance(text, str):
        return text
    return re.sub(r'\{(\w+)\}', lambda m: str(v[m.group(1)]) if m.group(1) in v else m.group(0), text)


class Ctx(object):
    """per-page rendering context"""

    def __init__(self, page, allpages, rings):
        self.p = page
        self.st = STYLES[page['style']]
        self.root = '../../../'
        self.v = page['vars']
        self.all = allpages
        self.rings = rings
        self.rr = page['rr']

    def img(self, name):
        return self.root + 'images/' + name

    def font(self, inner, size=None, color=None, face=True):
        a = ''
        f = self.st.get('face') if face else None
        if f:
            a += ' FACE="%s"' % f
        if size:
            a += ' SIZE="%s"' % size
        if color:
            a += ' COLOR="%s"' % color
        if not a:
            return inner
        return '<FONT%s>%s</FONT>' % (a, inner)


def body_tag(ctx, extra=''):
    st = ctx.st
    a = ['BGCOLOR="%s"' % st['bgcolor']]
    if st.get('background'):
        a.append('BACKGROUND="%s"' % ctx.img(st['background']))
    a.append('TEXT="%s" LINK="%s" VLINK="%s"' % (st['text'], st['link'], st['vlink']))
    if extra:
        a.append(extra)
    return '<BODY %s>' % ' '.join(a)


def heading(ctx, text, level=2):
    st = ctx.st
    p = ctx.p
    text = sub(text, ctx.v)
    mode = p['hmode']
    if st.get('header') and level == 2:
        return ('<TABLE WIDTH="100%%" CELLPADDING=3 CELLSPACING=0 BORDER=0><TR><TD BGCOLOR="%s"><FONT FACE="%s" '
                'COLOR="#FFFFFF"><B>%s</B></FONT></TD></TR></TABLE>\n' % (st['header'], st.get('hface') or 'Arial', text))
    face = (' FACE="%s"' % st['hface']) if st.get('hface') else ''
    color = (' COLOR="%s"' % st['hcolor']) if st.get('hcolor') else ''
    if mode == 'bullet' and p['bullet']:
        return '<P><IMG SRC="%s" WIDTH=14 HEIGHT=14 ALIGN=ABSMIDDLE> <FONT SIZE="+2"%s%s><B>%s</B></FONT></P>\n' % (
            ctx.img(p['bullet']), face, color, text)
    if mode == 'underline':
        return '<P><FONT SIZE="+1"%s%s><B><U>%s</U></B></FONT></P>\n' % (face, color, text)
    if mode == 'stars':
        return '<H3><FONT%s%s>*~*~ %s ~*~*</FONT></H3>\n' % (face, color, text)
    if mode == 'caps':
        return '<H2><FONT%s%s>%s</FONT></H2>\n' % (face, color, text.upper())
    return '<H%d><FONT%s%s>%s</FONT></H%d>\n' % (level, face, color, text, level)


def divider(ctx):
    line = ctx.p['line']
    if not line:
        return '<HR>\n' if ctx.rr.random() < 0.8 else '<HR SIZE=4 WIDTH="80%" NOSHADE>\n'
    from gh_imgsizes import SIZES
    w = SIZES.get(line, (480, 12))
    return '<P><CENTER><IMG SRC="%s" WIDTH=%d HEIGHT=%d></CENTER></P>\n' % (ctx.img(line), min(w[0], 480), w[1])


def bullet_list(ctx, items):
    p = ctx.p
    if p['bullet'] and p['listmode'] == 'img':
        out = ''
        for it in items:
            out += '<IMG SRC="%s" WIDTH=14 HEIGHT=14> %s<BR>\n' % (ctx.img(p['bullet']), it)
        return '<P>%s</P>\n' % out
    return '<UL>\n' + ''.join('<LI>%s\n' % it for it in items) + '</UL>\n'


def pick(rr, pool, n):
    lo, hi = n
    k = min(len(pool), rr.randint(lo, hi))
    idx = sorted(rr.sample(range(len(pool)), k))
    return [pool[i] for i in idx]


def table(ctx, rows, cols=2, head=None):
    st = ctx.st
    border = ctx.rr.choice([1, 1, 2, 0])
    bg = st.get('box') or ''
    out = '<TABLE BORDER=%d CELLPADDING=4 CELLSPACING=0%s>\n' % (border, (' BGCOLOR="%s"' % bg) if bg else '')
    if head:
        out += '<TR>' + ''.join('<TH>%s</TH>' % ctx.font(h, size=2) for h in head) + '</TR>\n'
    for r in rows:
        out += '<TR VALIGN=TOP><TD><B>%s</B></TD><TD>%s</TD></TR>\n' % (ctx.font(r[0], size=2), ctx.font(r[1], size=2))
    return out + '</TABLE>\n'


# ------------------------------------------------------------------ sections
def render_section(ctx, sec, fname):
    rr = ctx.rr
    v = ctx.v
    kind = sec['kind']
    head = rr.choice(sec['heads'])
    pool = [sub(x, v) if isinstance(x, str) else tuple(sub(y, v) for y in x) if isinstance(x, tuple) else x
            for x in sec['pool']]
    out = ''
    if kind == 'links':
        out += '<A NAME="links"></A>' + heading(ctx, head)
        out += links_block(ctx, sec['n'])
        return out
    out += heading(ctx, head)
    if kind == 'para':
        for t in pick(rr, pool, sec['n']):
            out += '<P>%s</P>\n' % t
    elif kind == 'list':
        out += bullet_list(ctx, pick(rr, pool, sec['n']))
    elif kind == 'top10':
        items = pick(rr, pool, sec['n'])
        rr.shuffle(items)
        out += '<OL>\n' + ''.join('<LI>%s\n' % x for x in items) + '</OL>\n'
    elif kind == 'log':
        items = pick(rr, pool, sec['n'])
        y, m, d = 1997 + rr.randint(0, 1), rr.randint(1, 12), rr.randint(1, 20)
        dstyle = rr.randint(0, 3)
        rows = []
        for it in items:
            rows.append((fmt_date((y, m, d), dstyle), it))
            m += rr.randint(1, 3)
            d = rr.randint(1, 28)
            if m > 12:
                m -= 12
                y += 1
            if y > 1999 or (y == 1999 and m > 10):
                y, m = 1999, 10
        if rr.random() < 0.4:
            rows.reverse()
        if rr.random() < 0.5:
            out += table(ctx, rows)
        else:
            out += ''.join('<P><B>%s:</B> %s</P>\n' % r for r in rows)
    elif kind == 'table':
        out += table(ctx, pick(rr, pool, sec['n']))
    elif kind == 'photos':
        from gh_imgsizes import SIZES
        items = pick(rr, pool, sec['n'])
        out += '<TABLE BORDER=0 CELLPADDING=6><TR VALIGN=TOP>\n'
        for i, (im, cap) in enumerate(items):
            w, h = SIZES.get(im, (120, 120))
            out += '<TD ALIGN=CENTER><IMG SRC="%s" WIDTH=%d HEIGHT=%d BORDER=2 ALT="%s"><BR>%s</TD>\n' % (
                ctx.img(im), w, h, cap.replace('"', "'"), ctx.font('<I>%s</I>' % cap, size=2))
            if i % 2 == 1 and i < len(items) - 1:
                out += '</TR><TR VALIGN=TOP>\n'
        out += '</TR></TABLE>\n'
    elif kind == 'gallery':
        from gh_imgsizes import SIZES
        items = pick(rr, pool, sec['n'])
        out += '<P>'
        for im in items:
            w, h = SIZES.get(im, (40, 40))
            out += '<IMG SRC="%s" WIDTH=%d HEIGHT=%d ALT="%s" HSPACE=6 VSPACE=6> ' % (ctx.img(im), w, h, im)
            if w > 300:
                out += '<BR>'
        out += '</P>\n'
    elif kind == 'poems':
        for title, body in pick(rr, pool, sec['n']):
            out += '<P><B><I>%s</I></B><BR>\n%s</P>\n' % (title, body.replace('\n', '<BR>\n'))
            out += '<P>~ ~ ~</P>\n' if ctx.rr.random() < 0.5 else ''
    elif kind == 'recipes':
        for r in pick(rr, sec['pool'], sec['n']):
            out += '<P><B><FONT SIZE="+1">%s</FONT></B><BR><I>Serves %s</I></P>\n' % (r['name'], r['serves'])
            out += '<UL>\n' + ''.join('<LI>%s\n' % i for i in r['ing']) + '</UL>\n'
            out += '<P>%s</P>\n' % r['steps']
    elif kind == 'story':
        title, paras = rr.choice(pool)
        paras = [sub(x, v) for x in paras]
        out += '<P><B><FONT SIZE="+1">%s</FONT></B></P>\n' % title
        for t in paras:
            out += '<P>%s</P>\n' % t
    elif kind == 'faq':
        for q, a in pick(rr, pool, sec['n']):
            out += '<P><B>Q: %s</B><BR>A: %s</P>\n' % (q, a)
    elif kind == 'quote':
        out += '<BLOCKQUOTE><I>%s</I></BLOCKQUOTE>\n' % rr.choice(pool)
    elif kind == 'poll':
        out += ('<FORM NAME="poll" ACTION="%sgbthanks.html" METHOD="GET" onSubmit="alert(\'Thanks for voting! '
                'Results will be posted soon.\'); return true;">\n' % ctx.root)
        out += '<INPUT TYPE="hidden" NAME="form" VALUE="poll">\n'
        for i, opt in enumerate(pool):
            out += '<INPUT TYPE="radio" NAME="vote" VALUE="%d"%s> %s<BR>\n' % (i, ' CHECKED' if i == 0 else '', opt)
        out += '<INPUT TYPE="submit" VALUE="Vote!"></FORM>\n'
    elif kind == 'webcam':
        out += ('<P><IMG SRC="%s" WIDTH=160 HEIGHT=120 BORDER=3 ALT="webcam"><BR>%s</P>\n' % (
            ctx.img('webcam_off.gif'), ctx.font('<I>Cam updates every 60 seconds (when it is on). Hit RELOAD!</I>',
                                                size=1)))
    elif kind == 'countdown':
        out += ('<SCRIPT LANGUAGE="JavaScript">\n<!--\nvar y2k = new Date(2000, 0, 1, 0, 0, 0);\nvar now = new Date();\n'
                'var days = Math.ceil((y2k.getTime() - now.getTime()) / 86400000);\n'
                'if (days > 0) document.write("<FONT SIZE=+3 COLOR=#FF0000><B>" + days + "</B></FONT> days until the '
                'year 2000!");\nelse document.write("<FONT SIZE=+2 COLOR=#FF0000><B>WE MADE IT!!!</B></FONT> (or did '
                'we? check your bank statement)");\n// -->\n</SCRIPT>\n<NOSCRIPT>Only a few days left until the '
                'year 2000!</NOSCRIPT>\n<P><IMG SRC="%s" WIDTH=64 HEIGHT=64></P>\n' % ctx.img('y2k_bomb.gif'))
    elif kind == 'midis':
        names = sorted(MIDI_TITLES)
        rr.shuffle(names)
        names = names[:rr.randint(*sec['n'])]
        out += '<TABLE BORDER=1 CELLPADDING=4 CELLSPACING=0>\n'
        for nm in names:
            out += ('<TR><TD><IMG SRC="%s" WIDTH=14 HEIGHT=14></TD><TD><A HREF="%smidi/%s.mid">%s</A></TD>'
                    '<TD>%s</TD></TR>\n' % (ctx.img('ball_purple.gif'), ctx.root, nm, MIDI_TITLES[nm],
                                            ctx.font('%d KB' % rr.randint(2, 4), size=1)))
        out += '</TABLE>\n'
    elif kind == 'mpals':
        from gh_imgsizes import SIZES
        out += '<TABLE BORDER=1 CELLPADDING=4 CELLSPACING=0%s>\n' % (
            (' BGCOLOR="%s"' % ctx.st['box']) if ctx.st.get('box') else '')
        for name, typ, im, txt in pick(rr, pool, sec['n']):
            out += ('<TR VALIGN=TOP><TD><IMG SRC="%s" WIDTH=64 HEIGHT=64 ALT="%s"></TD><TD><B>%s</B> '
                    '<I>(%s type)</I><BR>%s</TD></TR>\n' % (ctx.img(im), name, name, typ, txt))
        out += '</TABLE>\n'
    return out


def links_block(ctx, n):
    """links to fellow homesteaders (same ring/theme/hood first) + a couple of 1999 Web sites"""
    rr = ctx.rr
    p = ctx.p
    cands = [q for q in ctx.all if q is not p and (q['ring'] == p['ring'] or q['theme'] == p['theme'])]
    others = [q for q in ctx.all if q is not p and q['hood'] == p['hood'] and q not in cands]
    k = rr.randint(*n)
    chosen = rr.sample(cands, min(len(cands), k))
    if len(chosen) < k and others:
        chosen += rr.sample(others, min(len(others), k - len(chosen)))
    items = []
    for q in chosen:
        items.append('<A HREF="%s%sindex.html">%s</A> - %s' % (ctx.root, q['addr'], q['title'],
                                                              rr.choice(['cool page!', 'my friend ' + q['v_handle'],
                                                                         'check it out', 'very nice',
                                                                         'by ' + q['v_handle'], 'a must see!!!',
                                                                         'great graphics', '']).strip(' -')))
    for site, label in rr.sample(p['ext'], min(len(p['ext']), rr.randint(1, 2))):
        items.append('<A HREF="%s../%s/index.html">%s</A>' % (ctx.root, site, label))
    items = [i.rstrip(' -') for i in items]
    return bullet_list(ctx, items)


# ------------------------------------------------------------------ page furniture
def counter_html(ctx):
    p = ctx.p
    c = p['counter']
    if not c:
        return ''
    rr = ctx.rr
    n = p['hits']
    lead = rr.choice(['You are visitor number', 'Visitors since %s:' % p['since'], 'This page has been visited',
                      'Hits:', 'You are lucky visitor #', '<B>Counter:</B>'])
    tail = ' times!' if 'visited' in lead else ''
    if c == 'js':
        style = rr.choice(['led', 'digit', 'odo'])
        return ('<P>%s\n<SCRIPT LANGUAGE="JavaScript">\n<!--\nvar base = %d;\nvar start = new Date(1999, 0, 1);\n'
                'var now = new Date();\nvar hits = base + Math.floor((now.getTime() - start.getTime()) / %d);\n'
                'var s = "" + hits;\nwhile (s.length < 6) s = "0" + s;\nfor (var i = 0; i < s.length; i++) {\n'
                '  document.write("<IMG SRC=\\"%s" + s.charAt(i) + ".gif\\" WIDTH=%d HEIGHT=20>");\n}\n// -->\n'
                '</SCRIPT><NOSCRIPT>%d</NOSCRIPT>%s</P>\n' % (
                    lead, n, rr.choice([3600000, 7200000, 14400000, 86400000]),
                    ctx.img(style + '_'), 15 if style == 'digit' else 14, n, tail))
    s = '%06d' % n
    w = 15 if c == 'digit' else 14
    imgs = ''.join('<IMG SRC="%s" WIDTH=%d HEIGHT=20>' % (ctx.img('%s_%s.gif' % (c, ch)), w) for ch in s)
    return '<P>%s %s%s</P>\n' % (lead, imgs, tail)


def midi_html(ctx):
    p = ctx.p
    m = p['midi']
    if not m:
        return ''
    src = '%smidi/%s.mid' % (ctx.root, m)
    mode = p['midimode']
    title = MIDI_TITLES.get(m, m)
    if mode == 'bgsound':
        h = '<BGSOUND SRC="%s" LOOP=INFINITE>\n' % src
    elif mode == 'embed':
        h = '<EMBED SRC="%s" AUTOSTART="true" LOOP="true" HIDDEN="true">\n<NOEMBED><BGSOUND SRC="%s"></NOEMBED>\n' % (
            src, src)
    elif mode == 'console':
        h = '<EMBED SRC="%s" AUTOSTART="true" LOOP="true" WIDTH=145 HEIGHT=60 CONTROLS="console">\n' % src
    else:
        h = ('<SCRIPT LANGUAGE="JavaScript">\n<!--\nif (navigator.appName == "Netscape") {\n'
             '  document.write(\'<EMBED SRC="%s" AUTOSTART="true" LOOP="true" HIDDEN="true">\');\n} else {\n'
             '  document.write(\'<BGSOUND SRC="%s" LOOP="-1">\');\n}\n// -->\n</SCRIPT>\n' % (src, src))
    cap = ctx.rr.choice(['Now playing: <I>%s</I>' % title, '<I>Music: "%s"</I>' % title,
                         'This page plays <I>%s</I>. <A HREF="%s">Click here</A> if you can\'t hear it!' % (title, src),
                         'Background music: <A HREF="%s">%s</A>' % (src, title)])
    return h + '<P>%s</P>\n' % ctx.font(cap, size=1)


def ring_html(ctx):
    p = ctx.p
    if not p['inring']:
        return ''
    ring = ctx.rings[p['ring']]
    mem = ring['members']
    i = mem.index(p)
    prev = mem[i - 1]
    nxt = mem[(i + 1) % len(mem)]
    arr = ','.join('"%s"' % q['addr'] for q in mem)
    r = ctx.root
    bg = ring['color']
    return ('<P><CENTER><TABLE BORDER=2 CELLPADDING=4 CELLSPACING=0 BGCOLOR="%s"><TR><TD ALIGN=CENTER>'
            '<FONT FACE="Arial" SIZE=2 COLOR="#000000">This <B>%s</B> site is owned by <B>%s</B>.<BR>\n'
            '[<A HREF="%s%sindex.html">Previous</A>] '
            '[<A HREF="%s%sindex.html">Next</A>] '
            '[<A HREF="%swebrings/%s.html" onClick="var a=new Array(%s); location.href=\'%s\'+a[Math.floor(Math.random()'
            '*a.length)]+\'index.html\'; return false;">Random</A>] '
            '[<A HREF="%swebrings/%s.html">List Sites</A>] '
            '[<A HREF="%swebrings/%s.html#join">Join</A>]</FONT></TD></TR></TABLE></CENTER></P>\n' % (
                bg, ring['name'], p['v_handle'], r, prev['addr'], r, nxt['addr'], r, p['ring'], arr, r, r, p['ring'],
                r, p['ring']))


def awards_html(ctx):
    a = ctx.p['awards']
    if not a:
        return ''
    out = heading(ctx, ctx.rr.choice(['My Awards!!!', 'Awards', 'Awards This Site Has Won', 'Thank You For The Awards!']))
    out += '<P>' + ' '.join('<IMG SRC="%s" WIDTH=100 HEIGHT=100 ALT="award" HSPACE=4>' % ctx.img(x) for x in a)
    out += '</P>\n'
    return out


def badges_html(ctx):
    b = ctx.p['badges']
    if not b:
        return ''
    return '<P>' + ' '.join('<IMG SRC="%s" WIDTH=88 HEIGHT=31 ALT="">' % ctx.img(x) for x in b) + '</P>\n'


def geoguide(ctx):
    p = ctx.p
    r = ctx.root
    return ('\n<!-- GeoHoods GeoGuide: inserted automatically by the GeoHoods server -->\n'
            '<P><CENTER><TABLE BORDER=1 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#FFFFCC"><TR>'
            '<TD><A HREF="%sindex.html"><IMG SRC="%s" WIDTH=88 HEIGHT=31 BORDER=0 ALT="GeoHoods"></A></TD>'
            '<TD ALIGN=CENTER><FONT FACE="Arial" SIZE=1 COLOR="#000000"><B><A HREF="%sindex.html">GeoHoods</A></B> | '
            '<A HREF="%s%s/index.html">%s</A> | <A HREF="%s%s/%s/index.html">%s</A><BR>\n'
            '<A HREF="%s%sindex.html">&lt;&lt; Prev neighbor</A> | <A HREF="%ssearch.html">Search</A> | '
            '<A HREF="%s%sindex.html">Next neighbor &gt;&gt;</A><BR>\n'
            '<A HREF="%sjoin.html">Get your own Free Home Page</A></FONT></TD>'
            '<TD><IMG SRC="%s" WIDTH=48 HEIGHT=40 ALT=""></TD></TR></TABLE></CENTER></P>\n' % (
                r, ctx.img('gh_88x31.gif'), r, r, p['hood'], p['hood'], r, p['hood'], p['suburb'], p['suburb'],
                r, p['prevn'], r, r, p['nextn'], r, ctx.img('gh_watermark.gif')))


def footer_bits(ctx, fname):
    p = ctx.p
    rr = ctx.rr
    home = fname in ('index.html', 'main.html')
    out = ''
    if p['guestbook'] and fname != 'guestbook.html':
        out += ('<P><A HREF="guestbook.html#sign"><IMG SRC="%s" WIDTH=120 HEIGHT=44 BORDER=0 ALT="Sign my guestbook"></A> '
                '<A HREF="guestbook.html"><IMG SRC="%s" WIDTH=120 HEIGHT=44 BORDER=0 ALT="View my guestbook"></A></P>\n'
                % (ctx.img('sign_gb.gif'), ctx.img('view_gb.gif')))
    if p['email'] and fname != 'guestbook.html':
        if p['mailimg'] and (home or rr.random() < 0.3):
            dims = {'mailme.gif': '100 HEIGHT=30', 'mail_fly.gif': '64 HEIGHT=48', 'email.gif': '40 HEIGHT=30',
                    'mailbox.gif': '32 HEIGHT=32'}[p['mailimg']]
            out += '<P><A HREF="mailto:%s"><IMG SRC="%s" WIDTH=%s BORDER=0 ALT="E-mail me"></A><BR>%s</P>\n' % (
                p['v_email'], ctx.img(p['mailimg']), dims,
                ctx.font('<A HREF="mailto:%s">%s</A>' % (p['v_email'], p['v_email']), size=1))
        else:
            out += '<P>%s</P>\n' % ctx.font('E-mail me at <A HREF="mailto:%s">%s</A>' % (p['v_email'], p['v_email']),
                                            size=2)
    if not home:
        return out
    out += counter_html(ctx)
    out += badges_html(ctx)
    if p['bestviewed']:
        out += '<P>%s</P>\n' % ctx.font(rr.choice([
            'This page is best viewed with Pioneer Navigator 4.0 at 800x600 with 256 colors.',
            'Best viewed in 800x600. Find more cool pages with <A HREF="%s../yowza/index.html">Yowza!</A>' % ctx.root,
            'Optimized for Internet Explor-o-Matic 4.0. Looks OK in Pioneer.',
            'Best viewed with your eyes open. And at 800x600.']), size=1)
    out += '<P>%s</P>\n' % ctx.font('Last updated: %s' % p['updated'], size=1)
    out += ring_html(ctx)
    return out


def extras_top(ctx):
    """welcome GIFs, marquees, blink, construction"""
    p = ctx.p
    rr = ctx.rr
    out = ''
    if p['welcomegif']:
        out += '<P><IMG SRC="%s" WIDTH=400 HEIGHT=40 ALT="Welcome to my homepage!"></P>\n' % ctx.img('welcome.gif')
    if p['marquee']:
        txt = rr.choice(['Welcome to my page!!! Thanks for stopping by!!! Please sign my guestbook!!!',
                         '*** WELCOME *** to the coolest page in %s ***' % p['hood'],
                         'This page is under construction!!! Come back soon for more stuff!!!',
                         'You are visiting %s\'s home page on the World Wide Web!!!' % p['v_first'],
                         'NEW: updated %s! ~~~ NEW: more links! ~~~ NEW: more everything!' % p['updated'],
                         'Hello world! Hello %s! Hello mom!' % p['v_town']])
        attrs = rr.choice(['', ' BEHAVIOR=ALTERNATE', ' SCROLLAMOUNT=8', ' BGCOLOR="#FFFF00"', ' DIRECTION=RIGHT'])
        out += '<MARQUEE%s>%s</MARQUEE>\n' % (attrs, ctx.font('<B>%s</B>' % txt))
    if p['construction']:
        g = rr.choice(['construction.gif', 'worker.gif', 'barricade.gif'])
        from gh_imgsizes import SIZES
        w, h = SIZES[g]
        out += '<P><IMG SRC="%s" WIDTH=%d HEIGHT=%d ALT="Under construction"><BR>%s</P>\n' % (
            ctx.img(g), w, h, ctx.font('<B>%s</B>' % rr.choice(['This page is UNDER CONSTRUCTION!!!',
                                                              'Pardon my dust!', 'Always under construction!',
                                                              'Still working on it, come back soon']), size=2))
    if p['blink']:
        out += '<P><BLINK><B>%s</B></BLINK></P>\n' % ctx.font(rr.choice(['NEW!!!', 'UPDATED!', 'SIGN MY GUESTBOOK!!!',
                                                                         'NEW PICTURES!!!', 'Under construction!']),
                                                              color='#FF0000')
    return out


def head_html(ctx, title, extra_head=''):
    p = ctx.p
    return ('<HTML>\n<HEAD>\n<TITLE>%s</TITLE>\n<META NAME="GENERATOR" CONTENT="%s">\n'
            '<META NAME="KEYWORDS" CONTENT="%s">\n<META NAME="DESCRIPTION" CONTENT="%s">\n%s</HEAD>\n' % (
                title, p['generator'], p['keywords'], p['desc'].replace('"', "'"), extra_head))


def js_extras(ctx):
    """status-bar scroller, no-right-click, browser sniff -- per page flags"""
    p = ctx.p
    h, onload, body = '', '', ''
    if p['scroller']:
        msg = '%s ... Welcome to %s ... Thanks for visiting! ... ' % (p['title'].replace('"', '').replace("'", ''),
                                                                    p['v_handle'])
        h += ('<SCRIPT LANGUAGE="JavaScript">\n<!--\nvar msg = "%s";\nvar pos = 0;\nfunction scrollit() {\n'
              '  window.status = msg.substring(pos, msg.length) + msg.substring(0, pos);\n'
              '  pos = (pos + 1) %% msg.length;\n  setTimeout("scrollit()", 120);\n}\n// -->\n</SCRIPT>\n' % msg)
        onload = 'onLoad="scrollit()"'
    if p['norightclick']:
        h += ('<SCRIPT LANGUAGE="JavaScript">\n<!--\nfunction noclick(e) {\n  if ((e && e.which == 3) || '
              '(window.event && window.event.button == 2)) {\n    alert("Sorry, no right-clicking! Please don\'t steal '
              'my graphics. E-mail me and ask!");\n    return false;\n  }\n  return true;\n}\n'
              'document.onmousedown = noclick;\n// -->\n</SCRIPT>\n')
    if p['sniff']:
        body += ('<SCRIPT LANGUAGE="JavaScript">\n<!--\nif (navigator.appName.indexOf("Netscape") >= 0) '
                 'document.write("<P><FONT SIZE=1>Pioneer users: this page looks best with your window maximized!'
                 '</FONT></P>");\nelse document.write("<P><FONT SIZE=1>Hey Explor-o-Matic user! This page was made for '
                 'Pioneer Navigator but I tried my best.</FONT></P>");\n// -->\n</SCRIPT>\n')
    if p['clock']:
        body += ('<SCRIPT LANGUAGE="JavaScript">\n<!--\nvar d = new Date();\nvar days = new Array("Sunday","Monday",'
                 '"Tuesday","Wednesday","Thursday","Friday","Saturday");\ndocument.write("<P><FONT SIZE=2>Today is " '
                 '+ days[d.getDay()] + ", " + (d.getMonth()+1) + "/" + d.getDate() + ". Have a nice day!</FONT></P>");'
                 '\n// -->\n</SCRIPT>\n')
    return h, onload, body


def wrap_margin(ctx, content):
    """for left-border backgrounds: push content right of the border strip"""
    if ctx.st.get('margin'):
        return ('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH="100%%"><TR><TD WIDTH=125>&nbsp;</TD>'
                '<TD VALIGN=TOP>\n%s</TD></TR></TABLE>\n' % content)
    return content


def boxed(ctx, content):
    st = ctx.st
    if st.get('box'):
        return ('<CENTER><TABLE WIDTH=600 BORDER=%d CELLPADDING=12 CELLSPACING=0 BGCOLOR="%s"><TR><TD>\n%s</TD></TR>'
                '</TABLE></CENTER>\n' % (ctx.rr.choice([0, 2, 3]), st['box'], content))
    return content


def nav_items(ctx, fname, frames=False):
    """(href, label) for the page's own navigation"""
    p = ctx.p
    home = 'main.html' if p['layout'] in ('frames', 'splash') else 'index.html'
    items = [(home, 'Home')]
    for sp in p['subpages']:
        items.append((sp['fname'], sp['title']))
    if p['guestbook']:
        items.append(('guestbook.html', 'Guestbook'))
    if p['haslinks']:
        items.append((home + '#links', 'Links'))
    if p['email']:
        items.append(('mailto:' + p['v_email'], 'E-mail me'))
    return items


def nav_html(ctx, fname, vertical=False, target=None):
    t = (' TARGET="%s"' % target) if target else ''
    items = nav_items(ctx, fname)
    p = ctx.p
    if vertical:
        out = ''
        for href, label in items:
            if p['navbuttons'] and label in ('Home', 'Links') and not target:
                im = {'Home': 'btn_home.gif', 'Links': 'btn_links.gif'}[label]
                out += '<A HREF="%s"%s><IMG SRC="%s" WIDTH=90 HEIGHT=28 BORDER=0 ALT="%s"></A><BR>\n' % (
                    href, t, ctx.img(im), label)
            else:
                bul = ('<IMG SRC="%s" WIDTH=14 HEIGHT=14> ' % ctx.img(p['bullet'])) if p['bullet'] else '&gt; '
                out += '%s<A HREF="%s"%s>%s</A><BR>\n' % (bul, href, t, ctx.font(label, size=2))
        return out
    return '<P>' + ctx.font(' | '.join('<A HREF="%s"%s>%s</A>' % (h, t, l) for h, l in items), size=2) + '</P>\n'


def title_block(ctx):
    p = ctx.p
    st = ctx.st
    face = st.get('hface') or st.get('face')
    out = ''
    if p['titleimg']:
        from gh_imgsizes import SIZES
        w, h = SIZES[p['titleimg']]
        out += '<IMG SRC="%s" WIDTH=%d HEIGHT=%d ALT=""> ' % (ctx.img(p['titleimg']), w, h)
    size = ctx.rr.choice(['+3', '+4', '6', '7'])
    t = '<FONT SIZE="%s"%s%s><B>%s</B></FONT>' % (size, (' FACE="%s"' % face) if face else '',
                                                 (' COLOR="%s"' % st['hcolor']) if st.get('hcolor') else '',
                                                 p['headline'])
    if st.get('italic'):
        t = '<I>%s</I>' % t
    out += t
    return '<P>%s</P>\n' % out


def page_content(ctx, sections, fname, is_home):
    p = ctx.p
    rr = ctx.rr
    out = ''
    if is_home:
        out += extras_top(ctx)
        out += title_block(ctx)
        if p['intro']:
            out += '<P>%s</P>\n' % p['intro']
        if p['photo_top']:
            from gh_imgsizes import SIZES
            w, h = SIZES[p['photo_top']]
            out += '<P><IMG SRC="%s" WIDTH=%d HEIGHT=%d ALT="%s"%s></P>\n' % (
                ctx.img(p['photo_top']), w, h, rr.choice(['me!', 'a picture', 'look!', '']),
                ' BORDER=2' if w > 60 else '')
        if p['broken']:
            out += ('<P><IMG SRC="%s" WIDTH=24 HEIGHT=26 ALT="[picture of me - coming soon!]"> '
                    '%s</P>\n' % (ctx.img('broken.gif'), ctx.font('<I>(my scanner is broken, real picture coming '
                                                                  'soon!)</I>', size=1)))
        out += midi_html(ctx)
        out += ''.join(js_extras(ctx)[2:3])
    else:
        out += '<P><FONT SIZE="+2"%s><B>%s</B></FONT></P>\n' % (
            (' COLOR="%s"' % ctx.st['hcolor']) if ctx.st.get('hcolor') else '', sub(ctx.cur_title, ctx.v))
    for sec in sections:
        if rr.random() > sec.get('prob', 1.0):
            continue
        out += render_section(ctx, sec, fname)
        out += divider(ctx) if rr.random() < 0.75 else '<BR>\n'
    if is_home:
        if p['applet']:
            out += ('<P><APPLET CODE="Fireworks.class" WIDTH=300 HEIGHT=120>\n<PARAM NAME="colors" VALUE="random">\n'
                    '<IMG SRC="%s" WIDTH=300 HEIGHT=120 ALT="Kava applet"><BR>\n'
                    '%s\n</APPLET></P>\n' % (ctx.img('kava_applet.gif'),
                                            ctx.font('<I>(You need a Kava-enabled browser to see the fireworks!)</I>',
                                                     size=1)))
        out += awards_html(ctx)
    return out


def finish(ctx, title, inner, fname, nav_where):
    """assemble a complete (non-frameset) page"""
    p = ctx.p
    h, onload, _body = js_extras(ctx)
    html = head_html(ctx, title, h)
    html += body_tag(ctx, onload) + '\n'
    st = ctx.st
    font_open = ('<FONT FACE="%s">' % st['face']) if st.get('face') else ''
    font_close = '</FONT>' if font_open else ''
    if p['layout'] == 'sidebar' and nav_where == 'side':
        side = nav_html(ctx, fname, vertical=True)
        if p['photo_menu']:
            side += '<P><IMG SRC="%s" WIDTH=64 HEIGHT=64 ALT=""></P>' % ctx.img(p['photo_menu'])
        body = ('<TABLE BORDER=0 CELLPADDING=8 CELLSPACING=0 WIDTH="100%%"><TR VALIGN=TOP>'
                '<TD WIDTH=150 BGCOLOR="%s">%s%s%s</TD>\n<TD%s>%s%s%s</TD></TR></TABLE>\n' % (
                    st['navbg'], font_open, side, font_close,
                    (' BGCOLOR="%s"' % st['box']) if st.get('box') else '', font_open,
                    inner + footer_bits(ctx, fname), font_close))
        body = wrap_margin(ctx, body)
    else:
        nav = nav_html(ctx, fname) if nav_where == 'top' else ''
        content = nav + inner + footer_bits(ctx, fname)
        if nav_where == 'top' and len(nav_items(ctx, fname)) > 2:
            content += nav_html(ctx, fname)
        content = boxed(ctx, content)
        if st.get('align'):
            content = '<CENTER>\n%s</CENTER>\n' % content
        body = wrap_margin(ctx, font_open + content + font_close)
    html += body
    html += geoguide(ctx)
    html += '</BODY>\n</HTML>\n'
    return html


def render_member(page, allpages, rings):
    """returns {filename: html}"""
    ctx = Ctx(page, allpages, rings)
    p = page
    files = {}
    lay = p['layout']
    home_name = 'main.html' if lay in ('frames', 'splash') else 'index.html'
    ctx.cur_title = p['title']
    nav_where = {'single': 'top', 'sidebar': 'side', 'frames': 'frame', 'splash': 'top'}[lay]
    inner = page_content(ctx, p['sections'], home_name, True)
    files[home_name] = finish(ctx, p['title'], inner, home_name, nav_where)
    for sp in p['subpages']:
        ctx.cur_title = sp['title']
        inner = page_content(ctx, sp['sections'], sp['fname'], False)
        files[sp['fname']] = finish(ctx, '%s - %s' % (p['title'], sub(sp['title'], ctx.v)), inner, sp['fname'],
                                    nav_where)
    if p['guestbook']:
        files['guestbook.html'] = guestbook_page(ctx, nav_where)
    if lay == 'frames':
        files['menu.html'] = frame_menu(ctx)
        files['index.html'] = frameset(ctx)
    elif lay == 'splash':
        files['index.html'] = splash(ctx)
    return files


def frameset(ctx):
    p = ctx.p
    return ('<HTML>\n<HEAD>\n<TITLE>%s</TITLE>\n<META NAME="GENERATOR" CONTENT="%s">\n</HEAD>\n'
            '<FRAMESET COLS="%d,*" BORDER=%d FRAMEBORDER=%s>\n'
            '<FRAME SRC="menu.html" NAME="menu" SCROLLING="auto" NORESIZE>\n'
            '<FRAME SRC="main.html" NAME="main">\n<NOFRAMES>\n<BODY>\n'
            '<P>This page uses FRAMES! Your browser does not support frames. '
            '<A HREF="main.html">Click here for the no-frames version</A>.</P>\n</BODY>\n</NOFRAMES>\n'
            '</FRAMESET>\n</HTML>\n' % (p['title'], p['generator'], ctx.rr.choice([150, 160, 170, 180]),
                                        ctx.rr.choice([0, 1, 3]), ctx.rr.choice(['NO', 'YES'])))


def frame_menu(ctx):
    p = ctx.p
    st = ctx.st
    html = head_html(ctx, 'menu')
    nb = dict(st)
    html += '<BODY BGCOLOR="%s" TEXT="%s" LINK="%s" VLINK="%s"%s>\n' % (
        st['navbg'], st['text'] if st['navbg'] != st['bgcolor'] else st['text'], st['link'], st['vlink'],
        (' BACKGROUND="%s"' % ctx.img(st['background'])) if st.get('background') and not st.get('margin') and
        ctx.rr.random() < 0.5 else '')
    face = ('<FONT FACE="%s">' % st['face']) if st.get('face') else '<FONT>'
    html += face + '<P><B>%s</B></P>\n' % ctx.font(p['v_handle'], size=2)
    if p['photo_menu']:
        html += '<P><IMG SRC="%s" WIDTH=64 HEIGHT=64 ALT=""></P>\n' % ctx.img(p['photo_menu'])
    html += nav_html(ctx, 'menu.html', vertical=True, target='main')
    html += '<P><A HREF="%sindex.html" TARGET="_top">%s</A></P>\n' % (ctx.root, ctx.font('GeoHoods', size=1))
    html += '</FONT>\n</BODY>\n</HTML>\n'
    del nb
    return html


def splash(ctx):
    p = ctx.p
    st = ctx.st
    rr = ctx.rr
    html = head_html(ctx, p['title'])
    html += body_tag(ctx) + '\n<CENTER>\n'
    html += '<P>&nbsp;</P><P>&nbsp;</P>\n'
    html += title_block(ctx)
    if p['photo_top']:
        from gh_imgsizes import SIZES
        w, h = SIZES[p['photo_top']]
        html += '<P><IMG SRC="%s" WIDTH=%d HEIGHT=%d></P>\n' % (ctx.img(p['photo_top']), w, h)
    html += '<P><A HREF="main.html"><IMG SRC="%s" WIDTH=160 HEIGHT=50 BORDER=0 ALT="ENTER"></A></P>\n' % ctx.img(
        'enter_big.gif')
    html += '<P>%s</P>\n' % ctx.font(rr.choice([
        'WARNING: This page contains MIDI music and lots of graphics. 28.8 users please be patient!',
        'This site is best viewed at 800x600 with Pioneer Navigator 4.0 or higher.',
        'Enter at your own risk!!!', 'Click ENTER to come in! (Frames version and no-frames version coming soon)']),
        size=2)
    html += '<P><IMG SRC="%s" WIDTH=88 HEIGHT=31> <IMG SRC="%s" WIDTH=88 HEIGHT=31></P>\n' % (
        ctx.img('best_800.gif'), ctx.img(rr.choice(['pioneer_now.gif', 'explorer.gif', 'notepad.gif'])))
    html += '</CENTER>\n'
    html += geoguide(ctx)
    html += '</BODY>\n</HTML>\n'
    del st
    return html


def guestbook_page(ctx, nav_where):
    p = ctx.p
    rr = ctx.rr
    r = ctx.root
    inner = '<P><FONT SIZE="+2"><B>%s</B></FONT></P>\n' % rr.choice([
        '%s\'s Guestbook' % p['v_handle'], 'Guestbook', 'Sign My Guestbook!!!', 'The Guestbook'])
    inner += '<P><IMG SRC="%s" WIDTH=32 HEIGHT=32> Thanks for visiting! %d people have signed so far.</P>\n' % (
        ctx.img('mailbox.gif'), len(p['gbentries']))
    inner += '<P><A HREF="#sign">Sign the guestbook</A> | <A HREF="%s">Back to my page</A></P>\n' % (
        'main.html' if p['layout'] in ('frames', 'splash') else 'index.html')
    box = ctx.st.get('box') or ''
    for e in p['gbentries']:
        inner += '<TABLE WIDTH="90%%" BORDER=1 CELLPADDING=6 CELLSPACING=0%s><TR><TD>\n' % (
            (' BGCOLOR="%s"' % box) if box else '')
        nm = '<B>%s</B>' % e['name']
        if e['email']:
            nm += ' &lt;<A HREF="mailto:%s">%s</A>&gt;' % (e['email'], e['email'])
        inner += ctx.font('%s<BR>\n<FONT SIZE=1>%s, %s - %s at %s - found me via: %s</FONT>\n<P>%s</P>' % (
            nm, e['where'][0], e['where'][1], fmt_date(e['date']), e['time'], e['found'], sub(e['text'], ctx.v)),
            size=2)
        inner += '</TD></TR></TABLE><BR>\n'
    inner += ('<A NAME="sign"></A><HR>\n<P><B>Sign My Guestbook</B></P>\n'
              '<FORM NAME="gb" ACTION="%sgbthanks.html" METHOD="GET">\n<INPUT TYPE="hidden" NAME="page" VALUE="%s">\n'
              '<TABLE BORDER=0 CELLPADDING=3>\n'
              '<TR><TD>Your name:</TD><TD><INPUT TYPE="text" NAME="name" SIZE=30></TD></TR>\n'
              '<TR><TD>E-mail:</TD><TD><INPUT TYPE="text" NAME="email" SIZE=30></TD></TR>\n'
              '<TR><TD>Your homepage:</TD><TD><INPUT TYPE="text" NAME="url" SIZE=30 VALUE="http://"></TD></TR>\n'
              '<TR><TD>Where are you from?</TD><TD><INPUT TYPE="text" NAME="from" SIZE=30></TD></TR>\n'
              '<TR><TD>How did you find me?</TD><TD><SELECT NAME="found"><OPTION>Surfing around<OPTION>Webring'
              '<OPTION>Search engine<OPTION>A friend told me<OPTION>The neighborhood directory<OPTION>Other</SELECT>'
              '</TD></TR>\n<TR><TD VALIGN=TOP>Comments:</TD><TD><TEXTAREA NAME="comments" ROWS=5 COLS=40 WRAP=VIRTUAL>'
              '</TEXTAREA></TD></TR>\n<TR><TD></TD><TD><INPUT TYPE="submit" VALUE="Sign It!"> '
              '<INPUT TYPE="reset" VALUE="Clear"></TD></TR>\n</TABLE>\n</FORM>\n' % (r, p['addr']))
    saved = (p['email'], p['inring'])
    p['inring'] = False
    html = finish(ctx, '%s - Guestbook' % p['title'], inner, 'guestbook.html', nav_where)
    p['email'], p['inring'] = saved
    return html
