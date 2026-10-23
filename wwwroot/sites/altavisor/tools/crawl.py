#!/usr/bin/env python3
"""Skeeter, the AltaVisor web spider (re-runnable).

    python3 tools/crawl.py [--limit N]

Reads the 1999-Web sites straight from disk (wwwroot/sites/<name>/), starting at each
site's index.html and following same-site relative links up to N pages per site
(default 400). Sites that do not exist yet are logged as failures and skipped; run the
script again later to pick them up. The invented hosts in altavisor/web/ are crawled the
same way. Writes:

    av_index.js        the search index used by results.html and translate.html
    crawl.html         the crawler report
    popular.html       Top Searches, linking to...
    results/*.html     pre-computed static results pages (work without JavaScript)
"""
import hashlib, html, math, os, re, sys, time
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
SITES = os.path.normpath(os.path.join(ROOT, '..'))
sys.path.insert(0, HERE)
import gen_altavisor as G  # noqa: E402
import inventedweb as W  # noqa: E402

LIMIT = 400
# JavaScript shells and generated output that would only pollute the index
SKIP_FILES = {'results.html', 'search.html', 'random.html', 'answer.html', 'translate.html', 'crawl.html', 'popular.html'}
SKIP_DIRS_ALTAVISOR = ('web/', 'results/', 'tools/')
STOP = set('a an and are as at be but by can do for from has have he her his how i if in into is it its me my no not of on '
           'or our she so than that the their them then there these they this to too up us was we were what when where which '
           'who will with you your'.split())
MEDIA = ('.mid', '.midi', '.wav', '.mp3', '.au', '.ra', '.aif', '.mpg', '.mpeg', '.mov', '.avi', '.qt', '.rm')
POPULAR = ['y2k', 'hamster', 'mp3', 'dogs', 'books', 'toys', 'auction', 'pets', 'news', 'home page', 'bean bag',
           'linux', 'millennium', 'chat', 'games', 'weather', 'recipes', 'music', 'cool', 'guestbook']

A_HREF = re.compile(r'''<A\b[^>]*?\bHREF\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))''', re.I | re.S)
SRC_ATTR = re.compile(r'''<(?:EMBED|BGSOUND)\b[^>]*?\bSRC\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))''', re.I | re.S)
IMG = re.compile(r'<IMG\b([^>]*)>', re.I | re.S)


def attr(tag, name):
    m = re.search(r'''\b%s\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))''' % name, tag, re.I | re.S)
    if not m:
        return None
    return next(g for g in m.groups()[1:] if g is not None)


def mval(m):
    return next(g for g in m.groups()[1:] if g is not None)


def strip(text):
    text = re.sub(r'(?is)<(script|style)\b.*?</\1\s*>', ' ', text)
    text = re.sub(r'(?s)<!--.*?-->', ' ', text)
    text = re.sub(r'(?s)<[^>]*>', ' ', text)
    text = html.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()


def resolve(cur_file, href):
    """absolute file path for a relative link, or None"""
    href = href.strip()
    if not href or href.startswith(('#', 'mailto:', 'javascript:', 'news:', 'ftp:')) or re.match(r'^[a-z]+://', href, re.I):
        return None
    if href.startswith('/'):
        return None
    href = re.split(r'[?#]', href)[0]
    if not href:
        return None
    from urllib.parse import unquote
    p = os.path.normpath(os.path.join(os.path.dirname(cur_file), unquote(href)))
    if os.path.isdir(p):
        p = os.path.join(p, 'index.html')
    return p


def pick_summary(body, title):
    """the first real sentence of the page (skipping navigation bars and menus), like a 1999 abstract"""
    if body.startswith(title):
        body = body[len(title):].strip()
    for m in re.finditer(r'(?:^|(?<=\s))[A-Z]', body):
        seg = body[m.start():m.start() + 300]
        e = re.search(r'[.!?](\s|$)', seg)
        if not e:
            continue
        words = seg[:e.end()].split()
        if not 6 <= len(words) <= 45 or '|' in seg[:e.end()] or '**' in seg[:e.end()]:
            continue
        if not (words[1][:1].islower() or words[1] == 'I'):
            continue
        caps = sum(1 for w in words if w[:1].isupper())
        if caps <= 0.25 * len(words):
            return body[m.start():m.start() + 200].strip()
    return body[:200]


def fake_date(key):
    """a stable 'last modified' date between Nov 1998 and Oct 1999"""
    h = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
    day = h % 340
    t = time.mktime((1998, 11, 1, 12, 0, 0, 0, 0, -1)) + day * 86400
    return time.strftime('%Y%m%d', time.localtime(t))


class Spider:
    def __init__(self, limit):
        self.limit = limit
        self.docs = []
        self.report = []   # (host, status, pages, bytes, seconds, note)
        self.log = []

    def crawl_host(self, base_dir, host, disp_prefix, skip_dirs=()):
        start = os.path.join(base_dir, 'index.html')
        t0 = time.time()
        if not os.path.isdir(base_dir):
            self.report.append((host, 'FAILED', 0, 0, 0, 'Host not found - the site is not on the 1999 Web yet. Skeeter will try again next crawl.'))
            self.log.append('%s  GET http://%s/  ->  host not found' % (time.strftime('%H:%M:%S'), host))
            return
        if not os.path.exists(start):
            self.report.append((host, 'FAILED', 0, 0, 0, '404 Not Found - the site has no home page yet.'))
            self.log.append('%s  GET http://%s/  ->  404 Not Found' % (time.strftime('%H:%M:%S'), host))
            return
        seen, queue, n, nbytes, broken = {start}, deque([start]), 0, 0, 0
        while queue and n < self.limit:
            f = queue.popleft()
            rel = os.path.relpath(f, base_dir).replace(os.sep, '/')
            if not os.path.exists(f):
                broken += 1
                self.log.append('%s  GET http://%s/%s  ->  404 Not Found' % (time.strftime('%H:%M:%S'), host, rel))
                continue
            with open(f, 'rb') as fh:
                raw = fh.read()
            nbytes += len(raw)
            text = raw.decode('utf-8', errors='replace') if b'\xc3' in raw else raw.decode('latin-1')
            n += 1
            for m in A_HREF.finditer(text):
                p = resolve(f, mval(m))
                if not p or p in seen or not p.startswith(base_dir + os.sep):
                    continue
                r = os.path.relpath(p, base_dir).replace(os.sep, '/')
                if any(r.startswith(d) for d in skip_dirs) or not r.lower().endswith(('.html', '.htm')):
                    continue
                seen.add(p)
                queue.append(p)
            if os.path.basename(f).lower() in SKIP_FILES:
                continue
            self.add_doc(f, rel, text, len(raw), host, disp_prefix)
        status = 'OK' if n else 'EMPTY'
        note = '%d broken link%s' % (broken, '' if broken == 1 else 's') if broken else ''
        if queue:
            note = (note + '; ' if note else '') + 'stopped at the %d-page limit' % self.limit
        self.report.append((host, status, n, nbytes, time.time() - t0, note))
        self.log.append('%s  crawled http://%s/  ->  %d pages, %d KB' % (time.strftime('%H:%M:%S'), host, n, nbytes // 1024))

    def add_doc(self, f, rel, text, size, host, disp_prefix):
        m = re.search(r'(?is)<title[^>]*>(.*?)</title>', text)
        title = strip(m.group(1)) if m else os.path.basename(f)
        body = strip(re.sub(r'(?is)<title[^>]*>.*?</title>', ' ', text))
        md = re.search(r'''(?is)<meta\s+name\s*=\s*"?description"?\s+content\s*=\s*"([^"]*)"''', text)
        summary = strip(md.group(1)) if md else pick_summary(body, title)
        lm = re.search(r'(?is)<html[^>]*\blang\s*=\s*"?([a-z]{2})', text)
        lang = lm.group(1).lower() if lm else 'en'
        words, seen = [], set()
        for w in re.findall(r"[a-z0-9][a-z0-9']+", (title + ' ' + body).lower()):
            w = w.strip("'")
            if len(w) < 2 or w in STOP or w in seen:
                continue
            seen.add(w)
            words.append(w)
            if len(words) >= 260:
                break
        imgs, iseen = [], set()
        for im in IMG.finditer(text):
            src = attr(im.group(1), 'SRC')
            if not src:
                continue
            p = resolve(f, src)
            if not p or not os.path.exists(p):
                continue
            wd, ht = attr(im.group(1), 'WIDTH') or '', attr(im.group(1), 'HEIGHT') or ''
            if (wd.isdigit() and int(wd) <= 4) or (ht.isdigit() and int(ht) <= 4) or 'digit_' in p or p in iseen:
                continue
            iseen.add(p)
            alt = (attr(im.group(1), 'ALT') or '').replace('|', ' ').replace('~', ' ').replace(';', ',')
            imgs.append('%s~%s~%s~%s' % (os.path.relpath(p, ROOT).replace(os.sep, '/'), alt, wd, ht))
        media = []
        for mm in list(A_HREF.finditer(text)) + list(SRC_ATTR.finditer(text)):
            href = mval(mm)
            if not href.lower().split('?')[0].endswith(MEDIA):
                continue
            p = resolve(f, href)
            if p and os.path.exists(p):
                media.append('%s~%s' % (os.path.relpath(p, ROOT).replace(os.sep, '/'), title.replace('|', ' ').replace('~', ' ').replace(';', ',')))
        disp_rel = rel[:-10] if rel.endswith('index.html') else rel
        self.docs.append({
            'url': os.path.relpath(f, ROOT).replace(os.sep, '/'),
            'disp': disp_prefix + '/' + disp_rel, 'title': title.replace('|', '-'), 'sum': summary.replace('|', '-'),
            'words': ' '.join(words), 'kb': max(1, (size + 1023) // 1024), 'date': fake_date(f), 'lang': lang,
            'imgs': ';'.join(imgs[:8]), 'media': ';'.join(media[:8]),
        })

    def run(self):
        for name, title, _ in G.Y.WEB1999:
            skip = SKIP_DIRS_ALTAVISOR if name == 'altavisor' else ('tools/',)
            self.crawl_host(os.path.join(SITES, name), name + '.localhost', name + '.localhost', skip)
        webdir = os.path.join(ROOT, 'web')
        for host in sorted(os.listdir(webdir)) if os.path.isdir(webdir) else []:
            self.crawl_host(os.path.join(webdir, host), host, host)


# ---------------------------------------------------------------- output
def write_index(sp):
    lines = ['// AltaVisor index - written by tools/crawl.py on %s' % time.strftime('%Y-%m-%d %H:%M'),
             '// url|display url|title|summary|words|KB|yyyymmdd|lang|images (src~alt~w~h;...)|media (href~title;...)',
             'var NPAGES = %d;' % len(sp.docs), 'var CRAWLED = %s;' % G.js_str(time.strftime('%B %d')),
             'var LANGS = new Object();']
    for k, v in sorted(W.LANG_NAMES.items()):
        lines.append('LANGS[%s] = %s;' % (G.js_str(k), G.js_str(v)))
    lines.append('var D = new Array(')
    rows = []
    for d in sp.docs:
        rows.append(G.js_str('|'.join(str(d[k]) for k in ('url', 'disp', 'title', 'sum', 'words', 'kb', 'date', 'lang', 'imgs', 'media'))))
    lines.append(',\n'.join(rows))
    lines.append(');')
    with open(os.path.join(ROOT, 'av_index.js'), 'w', encoding='latin-1', errors='xmlcharrefreplace') as f:
        f.write('\n'.join(lines) + '\n')


DFCACHE = {}


def idf(docs, w):
    if w not in DFCACHE:
        n = 0
        for d in docs:
            if (' %s ' % w) in d['_w'] or (' %ss ' % w) in d['_w'] or (' %s ' % w) in d['_t'] or (' %ss ' % w) in d['_t']:
                n += 1
        DFCACHE[w] = n
    return math.log((len(docs) + 1) / (DFCACHE[w] + 1)) + 0.5


def score(d, terms, docs):
    """same ranking as the JavaScript engine in results.html (simple mode, no operators)"""
    tn = ' ' + re.sub(r'[^a-z0-9\']+', ' ', d['title'].lower()) + ' '
    wn = ' ' + d['words'] + ' '
    un = ' ' + re.sub(r'[^a-z0-9\']+', ' ', d['disp'].lower()) + ' '

    def has(hay, w):
        return (' %s ' % w) in hay or (' %ss ' % w) in hay
    s, matched, sum_idf = 0, 0, 0
    for w in terms:
        it, iw, iu = has(tn, w), has(wn, w), has(un, w)
        if it or iw or iu:
            matched += 1
        wt = idf(docs, w)
        sum_idf += wt
        s += wt * ((15 if it else 0) + (4 if iw else 0) + (3 if iu else 0))
    if not matched:
        return -1
    if matched == len(terms):
        s += 3 * sum_idf + 5
    if d['url'].endswith('index.html'):
        s += 2
    return s


def slug(q):
    return re.sub(r'[^a-z0-9]+', '_', q.lower()).strip('_')


def static_results(sp):
    outdir = os.path.join(ROOT, 'results')
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):
        os.remove(os.path.join(outdir, f))
    counts = []
    for q in POPULAR:
        terms = q.split()
        for d in sp.docs:
            d['_t'] = ' ' + re.sub(r"[^a-z0-9']+", ' ', d['title'].lower()) + ' '
            d['_w'] = ' ' + d['words'] + ' '
        hits = sorted(((score(d, terms, sp.docs), d) for d in sp.docs), key=lambda x: (-x[0], x[1]['url']))
        hits = [d for s, d in hits if s >= 0]
        counts.append((q, len(hits)))
        pre = '../'
        items = ''
        for i, d in enumerate(hits[:20]):
            dt = time.strftime('%d-%b-%y', time.strptime(d['date'], '%Y%m%d'))
            items += '''<DT><B>%d. <A HREF="../%s">%s</A></B>
<DD><FONT SIZE=-1>%s...<BR><FONT COLOR="#808080">URL: %s</FONT><BR>
<FONT COLOR="#808080">Last modified %s - page size %sK - in %s</FONT> [ <A HREF="../translate.html?u=%s">Translate</A> ]<BR>
<A HREF="../results.html?q=host:%s">More pages from this site</A></FONT><P>
''' % (i + 1, d['url'], G.esc(d['title']), G.esc(d['sum']), G.esc(d['disp']), dt, d['kb'], W.LANG_NAMES.get(d['lang'], 'English'),
                d['url'], d['disp'].split('/')[0])
        body = G.small_header(pre) + '''<P><FONT FACE=arial SIZE=-1><B>AltaVisor found %d Web pages for you.</B>
(Top Searches are pre-computed by Skeeter after every crawl. The <A HREF="../results.html?q=%s">live search</A> can do more.)</FONT>
<P><DL>
%s</DL>
''' % (len(hits), q.replace(' ', '+'), items) + G.footer(pre)
        with open(os.path.join(outdir, slug(q) + '.html'), 'w', encoding='latin-1', errors='xmlcharrefreplace') as f:
            f.write(G.page('AltaVisor: ' + q, body, pre))
    rows = ''.join('<TR><TD><FONT SIZE=-1>%d.</FONT></TD><TD><FONT SIZE=-1><A HREF="results/%s.html">%s</A></FONT></TD><TD ALIGN=RIGHT><FONT SIZE=-1>%d pages</FONT></TD></TR>\n' % (
        i + 1, slug(q), G.esc(q), n) for i, (q, n) in enumerate(counts))
    body = G.small_header('') + '''<P><FONT FACE=arial SIZE=+1><B>This Week's Top Searches</B></FONT><BR>
<FONT FACE=arial SIZE=-1>What the world is looking for this week, according to AltaVisor's search logs and a guy named Phil.</FONT>
<P><TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0 WIDTH=400>
%s</TABLE>
''' % rows + G.footer('')
    G.write('popular.html', G.page('AltaVisor: Top Searches', body, ''))


def crawl_report(sp, secs):
    rows = ''
    for host, status, n, nb, t, note in sp.report[:len(G.Y.WEB1999)]:
        col = '#009900' if status == 'OK' else '#CC0000'
        link = '<A HREF="results.html?q=host:%s">%s</A>' % (host, host) if n else host
        rows += '<TR BGCOLOR="#FFFFFF"><TD><FONT SIZE=-1>%s</FONT></TD><TD><FONT SIZE=-1 COLOR="%s"><B>%s</B></FONT></TD><TD ALIGN=RIGHT><FONT SIZE=-1>%d</FONT></TD><TD ALIGN=RIGHT><FONT SIZE=-1>%d</FONT></TD><TD><FONT SIZE=-1>%s</FONT></TD></TR>\n' % (
            link, col, status, n, nb // 1024, G.esc(note) or '&nbsp;')
    ext = sp.report[len(G.Y.WEB1999):]
    ext_pages = sum(r[2] for r in ext)
    ext_kb = sum(r[3] for r in ext) // 1024
    rows += '<TR BGCOLOR="#FFFFCC"><TD><FONT SIZE=-1><I>the rest of the Web (%d hosts)</I></FONT></TD><TD><FONT SIZE=-1 COLOR="#009900"><B>OK</B></FONT></TD><TD ALIGN=RIGHT><FONT SIZE=-1>%d</FONT></TD><TD ALIGN=RIGHT><FONT SIZE=-1>%d</FONT></TD><TD><FONT SIZE=-1>personal pages, companies, fan sites and one coffee pot</FONT></TD></TR>\n' % (
        len(ext), ext_pages, ext_kb)
    log = '\n'.join(G.esc(l) for l in sp.log[:len(G.Y.WEB1999)] + ['...'] + sp.log[-5:])
    ok = sum(1 for r in sp.report[:len(G.Y.WEB1999)] if r[1] == 'OK')
    body = G.small_header('') + '''<P><TABLE WIDTH=600 BORDER=0><TR><TD VALIGN=TOP><IMG SRC="images/skeeter.gif" WIDTH=64 HEIGHT=64 ALT="Skeeter"></TD>
<TD><FONT FACE=arial SIZE=+1><B>Skeeter's Crawler Report</B></FONT><BR><FONT FACE=arial SIZE=-1>
Skeeter last crawled the Web on <B>%(when)s</B>. He visited %(ok)d of the %(tot)d sites on the 1999 Web plus %(ext)d other hosts,
read <B>%(pages)d</B> pages and took %(secs).1f seconds, not counting snack breaks. Sites that could not be reached
are skipped and retried on the next crawl. Pages are followed only within the same site, up to %(limit)d per site.</FONT></TD></TR></TABLE>
<P><TABLE WIDTH=600 BORDER=0 CELLPADDING=3 CELLSPACING=1 BGCOLOR="#003399">
<TR BGCOLOR="#FFCC66"><TD><FONT SIZE=-1><B>Host</B></FONT></TD><TD><FONT SIZE=-1><B>Status</B></FONT></TD><TD><FONT SIZE=-1><B>Pages</B></FONT></TD><TD><FONT SIZE=-1><B>KB</B></FONT></TD><TD><FONT SIZE=-1><B>Notes</B></FONT></TD></TR>
%(rows)s</TABLE>
<P><FONT FACE=arial SIZE=-1><B>From the spider's log:</B></FONT>
<PRE>%(log)s</PRE>
<FONT FACE=arial SIZE=-1>Want Skeeter to come back sooner? He re-crawls whenever the webmaster runs <TT>tools/crawl.py</TT>.
Or <A HREF="addurl.html">submit a URL</A> and he will add it to his list.</FONT>
''' % dict(when=time.strftime('%B %d at %I:%M %p'), ok=ok, tot=len(G.Y.WEB1999), ext=len(ext), pages=len(sp.docs),
           secs=secs, limit=sp.limit, rows=rows, log=log) + G.footer('')
    G.write('crawl.html', G.page("AltaVisor: Skeeter's Crawler Report", body, ''))


def main():
    limit = LIMIT
    if '--limit' in sys.argv:
        limit = int(sys.argv[sys.argv.index('--limit') + 1])
    t0 = time.time()
    sp = Spider(limit)
    sp.run()
    write_index(sp)
    static_results(sp)
    crawl_report(sp, time.time() - t0)
    G.home_page()   # refresh the page count under Skeeter
    # bust browser caches so a re-crawl shows up right away
    stamp = str(int(time.time()))
    for name in ('results.html', 'translate.html'):
        p = os.path.join(ROOT, name)
        if os.path.exists(p):
            with open(p, encoding='latin-1') as f:
                t = f.read()
            with open(p, 'w', encoding='latin-1') as f:
                f.write(re.sub(r'av_index\.js(\?v=\d+)?', 'av_index.js?v=' + stamp, t))
    for host, status, n, nb, t, note in sp.report[:len(G.Y.WEB1999)]:
        print('%-26s %-7s %4d pages %6d KB  %s' % (host, status, n, nb // 1024, note))
    print('the rest of the Web: %d hosts' % (len(sp.report) - len(G.Y.WEB1999)))
    print('indexed %d pages -> av_index.js (%d KB)' % (len(sp.docs), os.path.getsize(os.path.join(ROOT, 'av_index.js')) // 1024))


if __name__ == '__main__':
    main()
