#!/usr/bin/env python3
"""linkcheck.py -- check every relative link and image in a static 1999 Web site.

Usage:  python3 tools/linkcheck.py [SITE_DIR ...]      (default: the geohoods site)

Checks HREF / SRC / BACKGROUND / ACTION / FRAME SRC attributes in every .html file:
  * no URL may start with "/" (sites must work at /sites/<name>/ and on GitHub Pages too)
  * relative targets must exist (directories need an index.html)
  * #fragments must match an <A NAME> in the target page
  * links that climb out of the site must land on a 1999-Web site folder or the web1999 hub
Also checks string literals in inline <SCRIPT> blocks that look like complete relative file paths,
that every .gif/.mid file is well-formed, and that every folder has an index page.
"""
import os
import re
import sys

RING = ['yowza', 'altavisor', 'askreeves', 'orinoco', 'ubid', 'etoyz', 'petz', 'geohoods', 'hamstershuffle',
        'dashdot', 'snapster', 'cnm']
TAG = re.compile(r'(?s)<[A-Za-z][^>]*>')
ATTR = re.compile(r'''(?is)(?<![.\w])(src|href|background|action)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>"']+))''')
SCRIPT = re.compile(r'(?is)<script\b[^>]*>(.*?)</script>')
LIT = re.compile(r'''["']((?:\.\./|[A-Za-z0-9_])[A-Za-z0-9_./-]*\.(?:gif|html|mid|js))["']''')
NAME = re.compile(r'''(?i)<a\s+name\s*=\s*"?([^"\s>]+)''')


def anchors(path, cache={}):
    if path not in cache:
        try:
            cache[path] = set(NAME.findall(open(path, encoding='latin-1').read()))
        except OSError:
            cache[path] = set()
    return cache[path]


def check_site(site):
    site = os.path.abspath(site)
    sites_dir = os.path.dirname(site)
    wwwroot = os.path.dirname(sites_dir)
    errors, warnings, n_links, n_files = [], [], 0, 0
    for dp, dns, fns in os.walk(site):
        rel_dir = os.path.relpath(dp, site)
        if not any(f.lower() in ('index.html', 'index.htm') for f in fns):
            errors.append('%s/: folder has no index.html' % rel_dir)
        for fn in fns:
            path = os.path.join(dp, fn)
            if fn.endswith('.gif'):
                with open(path, 'rb') as f:
                    if f.read(6) not in (b'GIF89a', b'GIF87a'):
                        errors.append('%s: not a GIF' % os.path.relpath(path, site))
            if fn.endswith('.mid'):
                with open(path, 'rb') as f:
                    data = f.read()
                if data[:4] != b'MThd' or b'MTrk' not in data:
                    errors.append('%s: not a MIDI file' % os.path.relpath(path, site))
            if not fn.endswith('.html'):
                continue
            n_files += 1
            text = open(path, encoding='latin-1').read()
            scripts = SCRIPT.findall(text)
            html = SCRIPT.sub('', text)
            urls = []
            for m in (a for t in TAG.findall(html) for a in ATTR.finditer(t)):
                urls.append((m.group(1).lower(), m.group(2) if m.group(2) is not None else
                             m.group(3) if m.group(3) is not None else m.group(4)))
            for s in scripts:
                for lit in LIT.findall(s):
                    urls.append(('script', lit))
            for kind, url in urls:
                url = url.strip()
                n_links += 1
                where = '%s: %s="%s"' % (os.path.relpath(path, site), kind, url)
                low = url.lower()
                if not url or low.startswith(('mailto:', 'javascript:', 'http://')) and (low != 'http://') \
                        or low.startswith('#') and len(url) == 1:
                    if low.startswith('http://') and len(url) > 7:
                        warnings.append(where + ' (absolute URL)')
                    continue
                if low == 'http://':
                    continue
                if url.startswith('/'):
                    errors.append(where + ' starts with "/"')
                    continue
                if low.startswith('#'):
                    if url[1:] not in anchors(path):
                        errors.append(where + ' (no such anchor)')
                    continue
                target, _q, _ = url.partition('?')
                target, _h, frag = target.partition('#')
                full = os.path.normpath(os.path.join(dp, target))
                if not full.startswith(site + os.sep) and full != site:
                    relw = os.path.relpath(full, wwwroot)
                    first = relw.split(os.sep)[0]
                    if relw.startswith('sites' + os.sep):
                        name = relw.split(os.sep)[1]
                        if name not in RING:
                            errors.append(where + ' (leaves the site to unknown %s)' % name)
                        elif not os.path.exists(full):
                            warnings.append(where + ' (1999-Web site %s not built yet)' % name)
                        continue
                    if first == 'web1999':
                        if not os.path.exists(full):
                            warnings.append(where + ' (hub not built yet)')
                        continue
                    errors.append(where + ' (leaves the site)')
                    continue
                if os.path.isdir(full):
                    if not os.path.exists(os.path.join(full, 'index.html')):
                        errors.append(where + ' (folder without index.html)')
                    full = os.path.join(full, 'index.html')
                if not os.path.exists(full):
                    errors.append(where + ' (missing)')
                elif frag and full.endswith('.html') and frag not in anchors(full):
                    errors.append(where + ' (no anchor #%s)' % frag)
    return errors, warnings, n_links, n_files


def main():
    sites = sys.argv[1:] or [os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')]
    bad = 0
    for s in sites:
        errors, warnings, n_links, n_files = check_site(s)
        print('%s: %d HTML files, %d links/images checked, %d errors, %d warnings' % (
            os.path.basename(os.path.abspath(s)), n_files, n_links, len(errors), len(warnings)))
        for e in errors[:60]:
            print('  ERROR', e)
        seen = set()
        for w in warnings:
            key = w.split('(')[-1]
            if key not in seen:
                seen.add(key)
                print('  warn ', w)
        bad += len(errors)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
