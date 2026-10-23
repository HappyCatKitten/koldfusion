#!/usr/bin/env python3
"""
mkdocs.py -- build the KoldFusion 4.5 documentation set under wwwroot/CFDOCS/.

Sources live in tools/docsrc/ as plain text (see FORMAT below):

    tags_*.txt     CFML Language Reference: one @tag entry per tag page
    funcs_*.txt    CFML Language Reference: one @func entry per function page
    book_*.txt     the books (Administering KoldFusion Server, Developing Web
                   Applications with KoldFusion): one @book header + @page entries

Output (all static, HTML 3.2 + a little CSS1, like the 1999 docs):

    wwwroot/CFDOCS/langref/<name>.htm        one page per tag / function
    wwwroot/CFDOCS/langref/index.htm         contents: tags + functions by category
    wwwroot/CFDOCS/langref/tags.htm          alphabetical tag list
    wwwroot/CFDOCS/langref/functions.htm     alphabetical function list
    wwwroot/CFDOCS/quickref/index.htm        CFML Quick Reference (all syntax on one page)
    wwwroot/CFDOCS/snippets/<name>.cfm       the runnable example of each entry
    wwwroot/CFDOCS/snippets/_catalog.cfm     query "Snippets" used by the launcher pages
    wwwroot/CFDOCS/<book>/<page>.htm         book pages (+ <book>/examples/*.cfm)
    wwwroot/CFDOCS/images/doc_*.gif          16x16 navigation icons (needs Pillow)

Usage:
    python3 tools/mkdocs.py                  build everything
    python3 tools/mkdocs.py --only FILE...   build just the entries/pages of FILE(s)
    python3 tools/mkdocs.py --test [FILE...] build, then run every generated .cfm through
                                             ./bin/kfserver --run and report errors
    python3 tools/mkdocs.py --check          parse + validate only, write nothing

FORMAT
------
An entry starts with a line "@tag CFNAME", "@func Name" or "@page id | Title".
Fields follow as "key: value" lines starting in column 0.  A field's value is the
rest of its line plus all following lines up to the next field or entry.
Lines starting with "#" before the first entry of a file are comments.

  @tag / @func fields
    title:     page title if not the entry name (e.g. "CFTRY/CFCATCH")
    also:      other names documented on this page (CFCATCH, CFELSE, ...)
    category:  one of TAG_CATEGORIES / FUNC_CATEGORIES below
    new45:     yes  -> "New in KoldFusion 4.5" marker
    summary:   one line for the indexes and the Quick Reference
    desc:      description (markup)
    syntax:    verbatim syntax block
    attrs:     tags: one attribute per line  NAME | Required|Optional[, default "x"] | description
    params:    funcs: one parameter per line  name | description
               (lines starting with whitespace continue the previous description)
    returns:   funcs: what the function returns (markup)
    usage:     usage notes (markup)
    example:   verbatim CFML; becomes snippets/<lowercase name>.cfm and the page's Example
    nosnippet: reason   -> example is shown but no snippet file / Example button is made
    testargs:  query string passed when --test runs the snippet
    see:       comma-separated names to link under "See also"

  @book id | Title           (once, at the top of a book file)
  @page id | Title
    the page body is markup; "<<run file.cfm>> ... <<end>>" writes a runnable example
    to <book>/examples/file.cfm, shows its code, and adds a "Run this example" link.

MARKUP (desc, usage, returns, attribute descriptions, book pages)
    blank lines separate blocks
    "# Heading" / "## Heading"       H2 / H3
    "- item"   "1. item"             bulleted / numbered list (indent to continue)
    lines indented 4 spaces          preformatted code
    "| a | b |" lines                table, first row is the header
    "> text"                         a "Note" paragraph
    "<<html>> ... <<end>>"           raw HTML passed through
    inline: `code` (auto-links tag/function names), **bold**, [text](url), {{Name}} (link)
    everything else is HTML-escaped.
"""
import html
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'tools', 'docsrc')
DOCS = os.path.join(ROOT, 'wwwroot', 'CFDOCS')

TAG_CATEGORIES = [
    'Variable manipulation',
    'Flow control',
    'Exception handling',
    'Output and page processing',
    'Database manipulation',
    'Application framework',
    'Extensibility',
    'Internet protocols',
    'File, directory and system',
    'Data interchange',
    'Verity search',
    'Security',
    'Forms',
]
FUNC_CATEGORIES = [
    'Array functions',
    'Authentication functions',
    'Date and time functions',
    'Decision functions',
    'Display and formatting functions',
    'Dynamic evaluation functions',
    'International functions',
    'List functions',
    'Mathematical functions',
    'Query functions',
    'String functions',
    'Structure functions',
    'System functions',
    'Other functions',
]

FIELDS = ('title', 'also', 'category', 'new45', 'summary', 'desc', 'syntax', 'attrs', 'params',
          'returns', 'usage', 'example', 'nosnippet', 'testargs', 'see')
FIELD_RE = re.compile(r'^(%s):[ \t]?(.*)$' % '|'.join(FIELDS))
COPYRIGHT = 'Copyright &copy; 1995-1999, Gibson Mainframe Co. All rights reserved.'


class DocError(Exception):
    pass


# =========================================================================== parsing
class Entry:
    def __init__(self, kind, name, path, line):
        self.kind, self.name, self.path, self.line = kind, name, path, line
        self.f = {}

    @property
    def slug(self):
        return self.name.lower()

    @property
    def title(self):
        return self.f.get('title') or (self.name if self.kind == 'tag' else self.name)

    def has_snippet(self):
        return bool(self.f.get('example')) and not self.f.get('nosnippet')


class Book:
    def __init__(self, bid, title, path):
        self.id, self.title, self.path = bid, title, path
        self.pages = []  # list of (id, title, body)


def parse_file(path):
    entries, book = [], None
    cur, field, buf = None, None, []
    page = None
    lines = open(path, encoding='utf-8').read().split('\n')

    def flush():
        nonlocal buf, field
        if field is None:
            buf = []
            return
        val = '\n'.join(buf)
        val = val.strip('\n')
        if field != 'example' and field != 'syntax' and field != '__body':
            val = val.strip()
        if field == '__body':
            page[2] = val.strip('\n')
        else:
            if field in cur.f:
                raise DocError('%s:%d: duplicate field %s in %s' % (path, cur.line, field, cur.name))
            cur.f[field] = val
        buf, field = [], None

    for no, line in enumerate(lines, 1):
        if line.startswith('@'):
            flush()
            m = re.match(r'^@(tag|func|page|book)\s+(.*)$', line.rstrip())
            if not m:
                raise DocError('%s:%d: bad entry line %r' % (path, no, line))
            kind, rest = m.group(1), m.group(2).strip()
            if kind in ('tag', 'func'):
                cur = Entry(kind, rest, path, no)
                entries.append(cur)
                page = None
            elif kind == 'book':
                bid, _, title = rest.partition('|')
                book = Book(bid.strip(), title.strip(), path)
            else:
                if book is None:
                    raise DocError('%s:%d: @page before @book' % (path, no))
                pid, _, title = rest.partition('|')
                page = [pid.strip(), title.strip(), '']
                book.pages.append(page)
                cur, field, buf = None, '__body', []
            continue
        if cur is None and page is None:
            continue  # file header comments
        if page is not None:
            buf.append(line)
            continue
        m = FIELD_RE.match(line)
        if m:
            flush()
            field = m.group(1)
            buf = [m.group(2)] if m.group(2) else []
            continue
        if field is None:
            if line.strip() and not line.startswith('#'):
                raise DocError('%s:%d: text outside a field in %s' % (path, no, cur.name))
            continue
        buf.append(line)
    flush()
    return entries, book


def load(files):
    entries, books = [], []
    for p in files:
        e, b = parse_file(p)
        entries.extend(e)
        if b:
            books.append(b)
    return entries, books


def validate(entries):
    errs = []
    seen = {}
    for e in entries:
        where = '%s:%d %s' % (os.path.basename(e.path), e.line, e.name)
        if e.slug in seen:
            errs.append('%s: duplicate entry (also %s)' % (where, seen[e.slug]))
        seen[e.slug] = where
        cats = TAG_CATEGORIES if e.kind == 'tag' else FUNC_CATEGORIES
        if e.f.get('category') not in cats:
            errs.append('%s: unknown category %r' % (where, e.f.get('category')))
        for req in ('summary', 'desc', 'syntax'):
            if not e.f.get(req):
                errs.append('%s: missing %s' % (where, req))
        if not e.f.get('example'):
            errs.append('%s: missing example' % where)
        if e.kind == 'tag' and not e.name.upper().startswith('CF'):
            errs.append('%s: tag names start with CF' % where)
        if e.kind == 'tag' and e.name != e.name.upper():
            errs.append('%s: write tag names in upper case' % where)
    return errs


# =========================================================================== markup
class Linker:
    """Resolves tag/function names to langref pages."""

    def __init__(self, entries):
        self.map = {}
        for e in entries:
            self.map[e.name.lower()] = e.slug
            for a in [x.strip() for x in e.f.get('also', '').split(',') if x.strip()]:
                self.map.setdefault(a.lower(), e.slug)

    def href(self, name, base):
        key = name.strip().lower()
        key = re.sub(r'\(.*$', '', key)
        key = key.lstrip('<').rstrip('>')
        slug = self.map.get(key)
        if not slug:
            return None
        return '%s%s.htm' % (base, slug)


def esc(s):
    return html.escape(s, quote=True)


def inline(text, linker, base):
    out = []
    pos = 0
    pat = re.compile(r'`([^`]+)`|\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)\s]+)\)|\{\{([^}]+)\}\}')
    for m in pat.finditer(text):
        out.append(esc(text[pos:m.start()]))
        if m.group(1) is not None:
            code = m.group(1)
            h = linker.href(code, base) if linker and re.match(r'^<?/?[A-Za-z_][A-Za-z0-9_]*(\(\))?>?$', code) else None
            c = '<CODE>%s</CODE>' % esc(code)
            out.append('<A HREF="%s">%s</A>' % (h, c) if h else c)
        elif m.group(2) is not None:
            out.append('<B>%s</B>' % inline(m.group(2), linker, base))
        elif m.group(3) is not None:
            out.append('<A HREF="%s">%s</A>' % (esc(m.group(4)), inline(m.group(3), linker, base)))
        else:
            name = m.group(5)
            h = linker.href(name, base) if linker else None
            out.append('<A HREF="%s">%s</A>' % (h, esc(name)) if h else esc(name))
        pos = m.end()
    out.append(esc(text[pos:]))
    return ''.join(out)


def markup(text, linker, base, runner=None):
    """Convert the light markup to HTML. runner(file, code) handles <<run>> blocks."""
    lines = text.split('\n')
    out = []
    i = 0
    n = len(lines)

    def para_end(j):
        return j >= n or not lines[j].strip() or lines[j].startswith(('- ', '|', '> ', '#', '<<')) \
            or re.match(r'^\d+\. ', lines[j]) or lines[j].startswith('    ')

    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = re.match(r'^<<run\s+(\S+)>>\s*$', line)
        if m or line.strip() == '<<html>>':
            j = i + 1
            body = []
            while j < n and lines[j].strip() != '<<end>>':
                body.append(lines[j])
                j += 1
            if j >= n:
                raise DocError('unterminated %s block' % line.strip())
            if m:
                if runner is None:
                    raise DocError('<<run>> blocks are only allowed in book pages')
                out.append(runner(m.group(1), '\n'.join(body).strip('\n') + '\n'))
            else:
                out.append('\n'.join(body))
            i = j + 1
            continue
        if line.startswith('#'):
            lvl = len(line) - len(line.lstrip('#'))
            tag = 'H2' if lvl == 1 else 'H3'
            out.append('<%s>%s</%s>' % (tag, inline(line.lstrip('#').strip(), linker, base), tag))
            i += 1
            continue
        if line.startswith('    ') or line.startswith('\t'):
            block = []
            while i < n and (lines[i].startswith('    ') or lines[i].startswith('\t') or
                             (not lines[i].strip() and i + 1 < n and (lines[i + 1].startswith('    ') or lines[i + 1].startswith('\t')))):
                l = lines[i]
                l = l[4:] if l.startswith('    ') else l[1:] if l.startswith('\t') else ''
                block.append(l)
                i += 1
            out.append('<PRE>%s</PRE>' % esc('\n'.join(block)))
            continue
        if line.startswith('|'):
            rows = []
            while i < n and lines[i].startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                rows.append(cells)
                i += 1
            t = ['<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=1 BGCOLOR="#999999" CLASS="doctable">']
            for r, cells in enumerate(rows):
                bg = '#669966' if r == 0 else ('#FFFFFF' if r % 2 else '#FFFBF0')
                t.append('<TR BGCOLOR="%s" VALIGN=TOP>' % bg)
                for c in cells:
                    if r == 0:
                        t.append('<TH ALIGN=LEFT><FONT COLOR="#FFFFFF">%s</FONT></TH>' % inline(c, linker, base))
                    else:
                        t.append('<TD>%s</TD>' % inline(c, linker, base))
                t.append('</TR>')
            t.append('</TABLE>')
            out.append('\n'.join(t))
            continue
        if line.startswith('- ') or re.match(r'^\d+\. ', line):
            ordered = not line.startswith('- ')
            items = []
            while i < n and (lines[i].startswith('- ') if not ordered else re.match(r'^\d+\. ', lines[i])):
                cur = [re.sub(r'^(- |\d+\. )', '', lines[i])]
                i += 1
                while i < n and lines[i].startswith('  ') and not lines[i].startswith('    ') and lines[i].strip():
                    cur.append(lines[i].strip())
                    i += 1
                items.append(' '.join(cur))
            tag = 'OL' if ordered else 'UL'
            out.append('<%s>\n%s\n</%s>' % (tag, '\n'.join('<LI>%s' % inline(x, linker, base) for x in items), tag))
            continue
        if line.startswith('> '):
            buf = []
            while i < n and lines[i].startswith('> '):
                buf.append(lines[i][2:])
                i += 1
            out.append('<P CLASS="note"><B>Note</B>&nbsp; %s</P>' % inline(' '.join(buf), linker, base))
            continue
        buf = [line]
        i += 1
        while not para_end(i):
            buf.append(lines[i])
            i += 1
        out.append('<P>%s</P>' % inline(' '.join(x.strip() for x in buf), linker, base))
    return '\n'.join(out)


# =========================================================================== page shell
def nav_bar(prev, up, nxt, base_img='/CFDOCS/images/'):
    def icon(href, img, alt):
        if href:
            return '<A HREF="%s"><IMG SRC="%s%s" WIDTH=16 HEIGHT=16 BORDER=0 ALT="%s"></A>' % (href, base_img, img, alt)
        return '<IMG SRC="%s%s" WIDTH=16 HEIGHT=16 BORDER=0 ALT="">' % (base_img, img.replace('.gif', '_off.gif'))
    return ('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=2><TR>'
            '<TD>%s</TD><TD>%s</TD><TD>%s</TD><TD>%s</TD><TD>%s</TD>'
            '</TR></TABLE>' % (icon(prev, 'doc_back.gif', 'Previous page'), icon(up, 'doc_up.gif', 'Up one level'),
                               icon(nxt, 'doc_next.gif', 'Next page'), icon('/CFDOCS/dochome.cfm', 'doc_home.gif', 'Documentation home'),
                               icon('/CFDOCS/langref/index.htm', 'doc_index.gif', 'CFML Language Reference contents')))


def page(title, body, prev=None, up=None, nxt=None, book='KoldFusion Documentation', head_extra=''):
    return '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<!-- Generated by tools/mkdocs.py from tools/docsrc. Edit the source, not this file. -->
<HTML>
<HEAD>
<TITLE>%(title)s</TITLE>
<META NAME="generator" CONTENT="KoldFusion mkdocs">
<LINK REL="stylesheet" TYPE="text/css" HREF="/CFDOCS/kfdocs.css">%(head)s
</HEAD>
<BODY BGCOLOR="#FFFFF0" TEXT="#000000" LINK="#0000CC" VLINK="#663399" ALINK="#CC0000">
%(nav)s
<FONT SIZE=1 CLASS="booktitle">%(book)s</FONT>
<HR NOSHADE SIZE=1>
<DIV CLASS="docbody">
%(body)s
</DIV>
<HR NOSHADE SIZE=1>
%(nav)s
<FONT SIZE=1 CLASS="copyright">%(copy)s</FONT>
</BODY>
</HTML>
''' % dict(title=esc(title), head=head_extra, nav=nav_bar(prev, up, nxt), book=esc(book), body=body, copy=COPYRIGHT)


EXAMPLE_JS = '''
<SCRIPT LANGUAGE="JavaScript">
<!--
function runExample(name) {
	var w = window.open('/CFDOCS/snippets/tagframe.cfm?tagname=' + name, 'kfexample',
		'width=720,height=560,resizable=yes,scrollbars=yes,toolbar=no,status=yes');
	if (w) w.focus();
}
//-->
</SCRIPT>'''


# =========================================================================== reference pages
def attr_table(text, kind, linker):
    rows = []
    for raw in text.split('\n'):
        if not raw.strip():
            continue
        if raw[0] in ' \t' and rows:
            rows[-1][-1] += ' ' + raw.strip()
            continue
        parts = [p.strip() for p in raw.split('|')]
        if kind == 'tag':
            if len(parts) < 3:
                raise DocError('attribute line needs NAME | Required/Optional | description: %r' % raw)
            rows.append([parts[0], parts[1], '|'.join(parts[2:]).strip()])
        else:
            if len(parts) < 2:
                raise DocError('parameter line needs name | description: %r' % raw)
            rows.append([parts[0], '|'.join(parts[1:]).strip()])
    out = ['<DL>']
    for r in rows:
        if kind == 'tag':
            out.append('<DT><B>%s</B></DT>\n<DD><I>%s.</I> %s</DD>' % (esc(r[0]), esc(r[1].rstrip('.')), inline(r[2], linker, '')))
        else:
            out.append('<DT><I>%s</I></DT>\n<DD>%s</DD>' % (esc(r[0]), inline(r[1], linker, '')))
    out.append('</DL>')
    return '\n'.join(out)


def ref_page(e, linker, prev, nxt):
    f = e.f
    b = []
    names = [e.name] + [x.strip() for x in f.get('also', '').split(',') if x.strip()]
    b.append('<H1>%s</H1>' % esc(f.get('title') or e.name))
    if f.get('new45', '').lower().startswith('y'):
        b.append('<P><FONT COLOR="#CC0000" SIZE=1><B>NEW IN KOLDFUSION 4.5</B></FONT></P>')
    b.append(markup(f['desc'], linker, ''))
    b.append('<H4>Category</H4><P><A HREF="index.htm#%s">%s</A></P>' % (cat_anchor(f['category']), esc(f['category'])))
    b.append('<H4>Syntax</H4>\n<PRE>%s</PRE>' % esc(f['syntax'].strip('\n')))
    if e.kind == 'tag' and f.get('attrs'):
        b.append('<H4>Attributes</H4>\n' + attr_table(f['attrs'], 'tag', linker))
    if e.kind == 'func' and f.get('params'):
        b.append('<H4>Parameters</H4>\n' + attr_table(f['params'], 'func', linker))
    if f.get('returns'):
        b.append('<H4>Returns</H4>\n' + markup(f['returns'], linker, ''))
    if f.get('usage'):
        b.append('<H4>Usage</H4>\n' + markup(f['usage'], linker, ''))
    b.append('<H4>Example</H4>')
    if e.has_snippet():
        b.append('<FORM ACTION="/CFDOCS/snippets/tagframe.cfm" METHOD="GET" TARGET="kfexample">'
                 '<INPUT TYPE="hidden" NAME="tagname" VALUE="%s">'
                 '<INPUT TYPE="submit" VALUE="Example" onClick="runExample(\'%s\'); return false;">'
                 ' <FONT SIZE=1>Opens the example in a new window. The example runs on this server, so it only works when you browse from the server itself (127.0.0.1).</FONT>'
                 '</FORM>' % (e.slug, e.slug))
    elif f.get('nosnippet'):
        b.append('<P><FONT SIZE=1><I>%s</I></FONT></P>' % inline(f['nosnippet'], linker, ''))
    b.append('<PRE CLASS="example">%s</PRE>' % esc(f['example'].strip('\n')))
    if f.get('see'):
        links = []
        for s in [x.strip() for x in f['see'].split(',') if x.strip()]:
            h = linker.href(s, '')
            links.append('<A HREF="%s">%s</A>' % (h, esc(s)) if h else esc(s))
        b.append('<H4>See also</H4>\n<P>%s</P>' % ', '.join(links))
    what = 'Tag' if e.kind == 'tag' else 'Function'
    body = re.sub(r'<A HREF="%s\.htm">(<CODE>[^<]*</CODE>)</A>' % re.escape(e.slug), r'<B>\1</B>', '\n'.join(b))
    return page('%s - CFML Language Reference' % (f.get('title') or e.name), body,
                prev=prev, up='index.htm', nxt=nxt, book='CFML Language Reference: %ss' % what,
                head_extra=EXAMPLE_JS if e.has_snippet() else '')


def cat_anchor(cat):
    return re.sub(r'[^a-z]+', '_', cat.lower()).strip('_')


def sort_key(e):
    return e.name.lower()


def index_pages(entries, linker):
    tags = sorted([e for e in entries if e.kind == 'tag'], key=sort_key)
    funcs = sorted([e for e in entries if e.kind == 'func'], key=sort_key)
    out = {}

    def cat_block(items, cats, kind):
        b = []
        for c in cats:
            its = [e for e in items if e.f['category'] == c]
            if not its:
                continue
            b.append('<H3><A NAME="%s">%s</A></H3>' % (cat_anchor(c), esc(c)))
            b.append('<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=0 WIDTH="95%">')
            for e in its:
                label = e.f.get('title') or e.name
                if kind == 'func':
                    label = e.name
                b.append('<TR VALIGN=TOP><TD WIDTH="30%%"><A HREF="%s.htm">%s</A>%s</TD><TD>%s</TD></TR>'
                         % (e.slug, esc(label), ' <FONT COLOR="#CC0000" SIZE=1>4.5</FONT>' if e.f.get('new45', '').lower().startswith('y') else '',
                            inline(e.f['summary'], linker, '')))
            b.append('</TABLE>')
        return '\n'.join(b)

    def cat_toc(items, cats):
        return ' | '.join('<A HREF="#%s">%s</A>' % (cat_anchor(c), esc(c.replace(' functions', '')))
                          for c in cats if any(e.f['category'] == c for e in items))

    body = ['<H1>CFML Language Reference</H1>',
            '<P>This reference describes every tag and function that the KoldFusion 4.5 server understands, with the '
            'syntax, the attributes or parameters, notes on how KoldFusion behaves, and an example you can run. '
            'Entries marked <FONT COLOR="#CC0000" SIZE=1>4.5</FONT> are new in this release.</P>',
            '<P><B>Alphabetical lists:</B> <A HREF="tags.htm">all %d tags</A> &middot; <A HREF="functions.htm">all %d functions</A> '
            '&middot; <A HREF="/CFDOCS/quickref/index.htm">CFML Quick Reference</A> &middot; <A HREF="/CFDOCS/snippets/index.cfm">Snippets Launcher</A></P>'
            % (len(tags), len(funcs)),
            '<H2><A NAME="tags">Chapter 1: CFML Tags</A></H2>',
            '<P><FONT SIZE=1>%s</FONT></P>' % cat_toc(tags, TAG_CATEGORIES),
            cat_block(tags, TAG_CATEGORIES, 'tag'),
            '<H2><A NAME="functions">Chapter 2: CFML Functions</A></H2>',
            '<P><FONT SIZE=1>%s</FONT></P>' % cat_toc(funcs, FUNC_CATEGORIES),
            cat_block(funcs, FUNC_CATEGORIES, 'func')]
    out['index.htm'] = page('CFML Language Reference', '\n'.join(body), up='/CFDOCS/dochome.cfm',
                            nxt='tags.htm', book='CFML Language Reference')

    def alpha(items, title, kind):
        letters = sorted(set(e.name.lstrip('cCfF')[0].upper() if kind == 'tag' else e.name[0].upper() for e in items))
        b = ['<H1>%s</H1>' % title,
             '<P>%s</P>' % ' '.join('<A HREF="#%s">%s</A>' % (l, l) for l in letters),
             '<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=0 WIDTH="95%">']
        last = None
        for e in items:
            l = (e.name[2:3] if kind == 'tag' else e.name[0]).upper()
            if l != last:
                b.append('<TR><TD COLSPAN=2><BR><B><A NAME="%s">%s</A></B></TD></TR>' % (l, l))
                last = l
            label = e.name if kind == 'func' else (e.f.get('title') or e.name)
            b.append('<TR VALIGN=TOP><TD WIDTH="30%%"><A HREF="%s.htm">%s</A></TD><TD>%s</TD></TR>'
                     % (e.slug, esc(label), inline(e.f['summary'], linker, '')))
            for a in [x.strip() for x in e.f.get('also', '').split(',') if x.strip()]:
                pass
        b.append('</TABLE>')
        return '\n'.join(b)

    out['tags.htm'] = page('CFML Tags (alphabetical)', alpha(tags, 'CFML Tags A-Z', 'tag'), prev='index.htm',
                           up='index.htm', nxt='functions.htm', book='CFML Language Reference')
    out['functions.htm'] = page('CFML Functions (alphabetical)', alpha(funcs, 'CFML Functions A-Z', 'func'),
                                prev='tags.htm', up='index.htm', book='CFML Language Reference')
    return out


def quickref(entries, linker):
    tags = sorted([e for e in entries if e.kind == 'tag'], key=sort_key)
    funcs = sorted([e for e in entries if e.kind == 'func'], key=sort_key)
    b = ['<H1>CFML Quick Reference</H1>',
         '<P>Every KoldFusion 4.5 tag and function on one page, for printing and pinning above your monitor. '
         'Square brackets mark optional parts; follow a name to its full Language Reference entry.</P>',
         '<P><A HREF="#tags">Tags</A> &middot; <A HREF="#functions">Functions</A> &middot; <A HREF="#ops">Operators</A></P>',
         '<H2><A NAME="tags">Tags</A></H2>']
    for c in TAG_CATEGORIES:
        its = [e for e in tags if e.f['category'] == c]
        if not its:
            continue
        b.append('<H3>%s</H3>' % esc(c))
        for e in its:
            b.append('<P CLASS="qr"><A HREF="/CFDOCS/langref/%s.htm"><B>%s</B></A> &nbsp;<FONT SIZE=1>%s</FONT></P>'
                     % (e.slug, esc(e.f.get('title') or e.name), inline(e.f['summary'], linker, '/CFDOCS/langref/')))
            b.append('<PRE CLASS="qr">%s</PRE>' % esc(e.f['syntax'].strip('\n')))
    b.append('<H2><A NAME="functions">Functions</A></H2>')
    for c in FUNC_CATEGORIES:
        its = [e for e in funcs if e.f['category'] == c]
        if not its:
            continue
        b.append('<H3>%s</H3>' % esc(c))
        b.append('<TABLE BORDER=0 CELLPADDING=1 CELLSPACING=0 WIDTH="100%">')
        for e in its:
            syn = e.f['syntax'].strip().split('\n')
            b.append('<TR VALIGN=TOP><TD WIDTH="45%%"><A HREF="/CFDOCS/langref/%s.htm"><CODE>%s</CODE></A></TD><TD><FONT SIZE=1>%s</FONT></TD></TR>'
                     % (e.slug, '<BR>'.join(esc(s) for s in syn), inline(e.f['summary'], linker, '/CFDOCS/langref/')))
        b.append('</TABLE>')
    b.append('''<H2><A NAME="ops">Operators</A></H2>
<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=1 BGCOLOR="#999999">
<TR BGCOLOR="#669966"><TH ALIGN=LEFT><FONT COLOR="#FFFFFF">Kind</FONT></TH><TH ALIGN=LEFT><FONT COLOR="#FFFFFF">Operators (highest precedence first)</FONT></TH></TR>
<TR BGCOLOR="#FFFFFF"><TD>Arithmetic</TD><TD><CODE>+ -</CODE> (unary) <CODE>^ * / \\ MOD + -</CODE></TD></TR>
<TR BGCOLOR="#FFFBF0"><TD>String</TD><TD><CODE>&amp;</CODE> (concatenation)</TD></TR>
<TR BGCOLOR="#FFFFFF"><TD>Comparison</TD><TD><CODE>IS, EQ, EQUAL &middot; IS NOT, NEQ, NOT EQUAL &middot; GT, GREATER THAN &middot; LT, LESS THAN &middot; GTE, GE, GREATER THAN OR EQUAL TO &middot; LTE, LE, LESS THAN OR EQUAL TO &middot; CONTAINS &middot; DOES NOT CONTAIN</CODE></TD></TR>
<TR BGCOLOR="#FFFBF0"><TD>Boolean</TD><TD><CODE>NOT AND OR XOR EQV IMP</CODE></TD></TR>
</TABLE>
<P>Inside <CODE>CFSCRIPT</CODE> KoldFusion also accepts <CODE>== != &lt; &gt; &lt;= &gt;= &amp;&amp; || ! ++ -- += -=</CODE> as a convenience.</P>''')
    return page('CFML Quick Reference', '\n'.join(b), up='/CFDOCS/dochome.cfm', book='CFML Quick Reference')


# =========================================================================== snippets
def snippet_text(e):
    return e.f['example'].strip('\n') + '\n'


def cf_str(s):
    return '"%s"' % s.replace('"', '""').replace('#', '##')


def catalog(entries):
    lines = ['<!--- Generated by tools/mkdocs.py: the list of Language Reference snippets. --->',
             '<cfset Snippets = QueryNew("Name,Title,Kind,Category,Summary,New45")>']
    def order(x):
        cats = TAG_CATEGORIES if x.kind == 'tag' else FUNC_CATEGORIES
        return (x.kind != 'tag', cats.index(x.f['category']), x.name.lower())
    for e in sorted([x for x in entries if x.has_snippet()], key=order):
        summ = re.sub(r'`([^`]*)`', r'\1', e.f['summary'])
        summ = re.sub(r'\*\*(.*?)\*\*', r'\1', summ)
        summ = re.sub(r'\{\{([^}]*)\}\}', r'\1', summ)
        summ = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', summ)
        vals = [('Name', e.slug), ('Title', e.f.get('title') or e.name), ('Kind', 'Tag' if e.kind == 'tag' else 'Function'),
                ('Category', e.f['category']), ('Summary', summ),
                ('New45', 'Yes' if e.f.get('new45', '').lower().startswith('y') else 'No')]
        lines.append('<cfset QueryAddRow(Snippets)>' + ''.join('<cfset QuerySetCell(Snippets, "%s", %s)>' % (k, cf_str(v)) for k, v in vals))
    return '\n'.join(lines) + '\n'


# =========================================================================== books
def build_book(b, linker, write):
    base = os.path.join(DOCS, b.id)
    pages = b.pages
    runs = []

    for i, (pid, title, body) in enumerate(pages):
        def runner(fname, code, _pid=pid):
            if not re.match(r'^[A-Za-z0-9_]+\.cfm$', fname):
                raise DocError('bad example file name %r' % fname)
            write(os.path.join(base, 'examples', fname), code)
            runs.append(os.path.join(base, 'examples', fname))
            return ('<TABLE BORDER=0 CELLPADDING=0 CELLSPACING=0 WIDTH="100%%"><TR><TD><FONT SIZE=1><B>%s</B></FONT></TD>'
                    '<TD ALIGN=RIGHT><FONT SIZE=1><A HREF="examples/%s" TARGET="kfrun">Run this example</A> &middot; '
                    '<A HREF="/CFDOCS/snippets/viewsource.cfm?file=%s/examples/%s" TARGET="kfrun">View source</A></FONT></TD></TR></TABLE>\n'
                    '<PRE CLASS="example">%s</PRE>' % (esc(fname), fname, b.id, fname, esc(code.rstrip('\n'))))
        html_body = '<H1>%s</H1>\n%s' % (esc(title), markup(body, linker, '/CFDOCS/langref/', runner))
        if pid == 'index':
            toc = ['<H3>Contents</H3>', '<OL>']
            for (qid, qt, _) in pages:
                if qid != 'index':
                    toc.append('<LI><A HREF="%s.htm">%s</A>' % (qid, esc(qt)))
            toc.append('</OL>')
            html_body += '\n' + '\n'.join(toc)
        prev = pages[i - 1][0] + '.htm' if i > 0 else None
        nxt = pages[i + 1][0] + '.htm' if i + 1 < len(pages) else None
        up = '/CFDOCS/dochome.cfm' if pid == 'index' else 'index.htm'
        write(os.path.join(base, pid + '.htm'), page('%s - %s' % (title, b.title), html_body, prev=prev, up=up, nxt=nxt, book=b.title))
    return runs


# =========================================================================== icons
def make_icons(write_bin):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return
    import io
    BLUE, DARK, GREY, LGREY = (0, 51, 153), (0, 0, 102), (153, 153, 153), (204, 204, 204)
    BG = (255, 255, 240)

    def mk(draw_fn, name):
        for suffix, col, edge in (('', BLUE, DARK), ('_off', LGREY, GREY)):
            im = Image.new('RGB', (16, 16), BG)
            d = ImageDraw.Draw(im)
            draw_fn(d, col, edge)
            im = im.convert('P', palette=Image.ADAPTIVE, colors=16)
            # make the ivory background transparent
            bgi = im.getpixel((0, 0))
            buf = io.BytesIO()
            im.save(buf, 'GIF', transparency=bgi)
            write_bin(os.path.join(DOCS, 'images', 'doc_%s%s.gif' % (name, suffix)), buf.getvalue())

    mk(lambda d, c, e: d.polygon([(11, 2), (11, 13), (3, 7)], fill=c, outline=e), 'back')
    mk(lambda d, c, e: d.polygon([(4, 2), (4, 13), (12, 7)], fill=c, outline=e), 'next')
    mk(lambda d, c, e: d.polygon([(2, 11), (13, 11), (7, 3)], fill=c, outline=e), 'up')

    def home(d, c, e):
        d.polygon([(1, 8), (7, 2), (14, 8)], fill=(204, 0, 0) if c == (0, 51, 153) else c, outline=e)
        d.rectangle([3, 8, 12, 14], fill=c, outline=e)
        d.rectangle([6, 10, 8, 14], fill=(255, 255, 240))
    mk(home, 'home')

    def book(d, c, e):
        d.rectangle([2, 2, 13, 14], fill=c, outline=e)
        d.line([(4, 2), (4, 14)], fill=e)
        for y in (5, 8, 11):
            d.line([(6, y), (11, y)], fill=(255, 255, 255))
    mk(book, 'index')


# =========================================================================== main
class Writer:
    def __init__(self, dry=False):
        self.dry = dry
        self.count = 0

    def __call__(self, path, text):
        self.count += 1
        if self.dry:
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        old = None
        if os.path.exists(path):
            with open(path, encoding='utf-8', errors='replace') as fh:
                old = fh.read()
        if old != text:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(text)

    def binary(self, path, data):
        if self.dry:
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as fh:
            fh.write(data)


def run_tests(cfm_files, testargs):
    kf = os.path.join(ROOT, 'bin', 'kfserver')
    bad = 0
    for f in cfm_files:
        rel = os.path.relpath(f, ROOT)
        args = [kf, '--run', rel]
        qs = testargs.get(f)
        if qs:
            args.append(qs)
        try:
            p = subprocess.run(args, cwd=ROOT, capture_output=True, timeout=60)
            out = p.stdout.decode('utf-8', 'replace')
        except subprocess.TimeoutExpired:
            out = 'TIMEOUT'
        status = out.split('\r\n', 1)[0] if out else 'NO OUTPUT'
        if 'Error Diagnostic Information' in out or 'TIMEOUT' == out or not out.startswith('HTTP/1.0 2') and not out.startswith('HTTP/1.0 3'):
            bad += 1
            msg = re.findall(r'<P>(Error[^\n]*|[^<\n]{0,200})\n?', out)
            detail = re.sub(r'<[^>]+>', '', out.split('Error Diagnostic Information', 1)[-1])[:500].strip()
            print('FAIL %s [%s]\n     %s' % (rel, status, detail.replace('\n', '\n     ')))
        else:
            print('ok   %s' % rel)
    print('%d of %d failed' % (bad, len(cfm_files)))
    return bad


def main(argv):
    only, test, check = None, False, False
    args = argv[1:]
    if args and args[0] == '--only':
        only = [os.path.abspath(a) for a in args[1:]]
    elif args and args[0] == '--test':
        test = True
        only = [os.path.abspath(a) for a in args[1:]] or None
    elif args and args[0] == '--check':
        check = True
    elif args:
        print(__doc__)
        return 2

    all_files = sorted(os.path.join(SRC, f) for f in os.listdir(SRC) if f.endswith('.txt'))
    if only is not None:
        for p in only:
            if p not in all_files:
                print('error: %s is not a file in %s' % (p, SRC))
                return 1
        # strict for the selected files; best effort (for links only) for the rest,
        # so a half-edited neighbour file does not block a partial build
        others = []
        for p in all_files:
            if p in only:
                continue
            try:
                others.extend(parse_file(p)[0])
            except DocError:
                pass
        all_files = only
    try:
        entries, books = load(all_files)
    except DocError as ex:
        print('error:', ex)
        return 1
    errs = validate(entries)
    for e in errs:
        print('error:', e)
    if errs:
        return 1
    linker = Linker(entries + (others if only is not None else []))
    w = Writer(dry=check)
    sel = (lambda path: True) if only is None else (lambda path: os.path.abspath(path) in only)

    tags = sorted([e for e in entries if e.kind == 'tag'], key=sort_key)
    funcs = sorted([e for e in entries if e.kind == 'func'], key=sort_key)
    cfm, testargs = [], {}
    try:
        for seq in (tags, funcs):
            for i, e in enumerate(seq):
                if not sel(e.path):
                    continue
                prev = seq[i - 1].slug + '.htm' if i > 0 else None
                nxt = seq[i + 1].slug + '.htm' if i + 1 < len(seq) else None
                try:
                    w(os.path.join(DOCS, 'langref', e.slug + '.htm'), ref_page(e, linker, prev, nxt))
                except DocError as ex:
                    raise DocError('%s:%d %s: %s' % (os.path.basename(e.path), e.line, e.name, ex))
                if e.has_snippet():
                    p = os.path.join(DOCS, 'snippets', e.slug + '.cfm')
                    w(p, snippet_text(e))
                    cfm.append(p)
                    if e.f.get('testargs'):
                        testargs[p] = e.f['testargs']
        if only is None:
            for name, text in index_pages(entries, linker).items():
                w(os.path.join(DOCS, 'langref', name), text)
            w(os.path.join(DOCS, 'quickref', 'index.htm'), quickref(entries, linker))
            w(os.path.join(DOCS, 'snippets', '_catalog.cfm'), catalog(entries))
            if not check:
                make_icons(w.binary)
        for b in books:
            if sel(b.path):
                cfm.extend(build_book(b, linker, w))
    except DocError as ex:
        print('error:', ex)
        return 1
    print('%s %d files from %d entries and %d books (%d tags, %d functions, %d snippets)'
          % ('checked' if check else 'wrote', w.count, len(entries), len(books), len(tags), len(funcs),
             sum(1 for e in entries if e.has_snippet())))
    if test:
        return 1 if run_tests(cfm, testargs) else 0
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
