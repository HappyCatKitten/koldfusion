#!/usr/bin/env python3
"""Link checker and page walker for the static 1999-Web sites.

    python3 tools/checklinks.py [--port 8701] [--http] [site ...]     (default sites: yowza altavisor askreeves)

1. Reads every .html file of each site from disk and checks every HREF, SRC and BACKGROUND:
   - no URL may start with "/" (sites must work at two different roots)
   - links inside the site must point at files that exist
   - links that climb into another 1999-Web site are counted (and reported if that site
     or page does not exist yet); links to the hub ../../web1999/ likewise
   - URLs inside the generated JavaScript data (yz_index.js, av_index.js) are checked too
2. With --http, fetches every page from a running kfserver at BOTH
   http://<site>.localhost:PORT/<page> and http://localhost:PORT/sites/<site>/<page>
   and fails on anything but 200 or on an "Error Diagnostic Information" page.
"""
import os, re, sys, urllib.request
from urllib.parse import unquote

HERE = os.path.dirname(os.path.abspath(__file__))
SITES = os.path.normpath(os.path.join(HERE, '..', '..'))
WEBROOT = os.path.normpath(os.path.join(SITES, '..'))
ALL = ['yowza', 'altavisor', 'askreeves', 'orinoco', 'ubid', 'etoyz', 'petz', 'geohoods', 'hamstershuffle', 'dashdot', 'snapster', 'cnm']
ATTR = re.compile(r'''(?<![.\w])(HREF|SRC|BACKGROUND)\s*=\s*("([^"]*)"|'([^']*)'|([^\s>"']+))''', re.I)


def html_files(root):
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x != 'tools']
        for f in files:
            if f.lower().endswith(('.html', '.htm')):
                yield os.path.join(d, f)


def classify(src_file, url, site_root):
    """returns (kind, target) kind: skip | abs-slash | internal | cross | hub"""
    if not url or url.startswith(('#', 'mailto:', 'javascript:', 'news:')) or re.match(r'^[a-z]+://', url, re.I):
        return 'skip', None
    if "'" in url or '+' in url and url.startswith("'"):
        return 'skip', None
    if url.startswith('/'):
        return 'abs-slash', url
    path = unquote(re.split(r'[?#]', url)[0])
    if not path:
        return 'skip', None
    t = os.path.normpath(os.path.join(os.path.dirname(src_file), path))
    if url.endswith('/') or os.path.isdir(t):
        t = os.path.join(t, 'index.html')
    if t.startswith(site_root + os.sep):
        return 'internal', t
    if t.startswith(os.path.join(WEBROOT, 'web1999')):
        return 'hub', t
    if t.startswith(SITES + os.sep):
        return 'cross', t
    return 'outside', t


def check_site(site):
    root = os.path.join(SITES, site)
    errors, cross_missing, n_links, n_pages = [], {}, 0, 0
    for f in html_files(root):
        n_pages += 1
        with open(f, encoding='latin-1') as fh:
            text = fh.read()
        # URLs assembled inside inline JavaScript can't be checked statically; keep <SCRIPT SRC=...> itself
        scan = re.sub(r'(?is)(<script\b[^>]*>).*?</script>', r'\1</script>', text)
        for m in ATTR.finditer(scan):
            url = next(g for g in m.groups()[2:] if g is not None)
            if '+' in url and ("'" in url or '"' in url):
                continue
            kind, t = classify(f, url, root)
            if kind == 'skip':
                continue
            n_links += 1
            rel = os.path.relpath(f, root)
            if kind == 'abs-slash':
                errors.append('%s: root-relative URL %s' % (rel, url))
            elif kind == 'outside':
                errors.append('%s: link leaves the web root: %s' % (rel, url))
            elif kind == 'internal' and not os.path.exists(t):
                errors.append('%s: broken link %s' % (rel, url))
            elif kind in ('cross', 'hub') and not os.path.exists(t):
                key = os.path.relpath(t, WEBROOT)
                cross_missing.setdefault(key, set()).add(rel)
    # URLs stored in the generated JavaScript data files
    for js, pattern, base in (('yz_index.js', r"'([^'|]*\|){3}([^|]*)\|", 2), ('av_index.js', r"^'([^|]*)\|", 1)):
        p = os.path.join(root, js)
        if not os.path.exists(p):
            continue
        with open(p, encoding='latin-1') as fh:
            for line in fh:
                m = re.match(pattern, line.strip().lstrip(','), re.M)
                if not m:
                    continue
                url = m.group(base)
                n_links += 1
                kind, t = classify(os.path.join(root, 'x.html'), url, root)
                if kind == 'internal' and not os.path.exists(t):
                    errors.append('%s: broken link %s' % (js, url))
                elif kind == 'cross' and not os.path.exists(t):
                    cross_missing.setdefault(os.path.relpath(t, WEBROOT), set()).add(js)
                if js == 'av_index.js':
                    for img in re.findall(r'(?:^|;)([^~;|]+)~', line.split('|')[8] if line.count('|') >= 9 else ''):
                        kind, t = classify(os.path.join(root, 'x.html'), img, root)
                        if kind in ('internal', 'cross') and not os.path.exists(t):
                            errors.append('%s: missing image %s' % (js, img))
    return n_pages, n_links, errors, cross_missing


def http_walk(site, port):
    root = os.path.join(SITES, site)
    bad, n = [], 0
    for f in html_files(root):
        rel = os.path.relpath(f, root).replace(os.sep, '/')
        for url in ('http://%s.localhost:%d/%s' % (site, port, rel), 'http://localhost:%d/sites/%s/%s' % (port, site, rel)):
            n += 1
            try:
                with urllib.request.urlopen(url, timeout=20) as r:
                    body = r.read().decode('latin-1')
                    if r.status != 200 or 'Error Diagnostic Information' in body:
                        bad.append('%s -> %s' % (url, r.status))
            except Exception as e:
                bad.append('%s -> %s' % (url, e))
    return n, bad


def main():
    args = sys.argv[1:]
    port, http = 8701, False
    if '--port' in args:
        i = args.index('--port'); port = int(args[i + 1]); del args[i:i + 2]
    if '--http' in args:
        args.remove('--http'); http = True
    sites = args or ['yowza', 'altavisor', 'askreeves']
    failed = False
    for s in sites:
        n_pages, n_links, errors, cross = check_site(s)
        print('%-10s %5d pages, %6d links checked, %d errors' % (s, n_pages, n_links, len(errors)))
        for e in errors[:40]:
            print('   ERROR', e)
        if len(errors) > 40:
            print('   ... and %d more' % (len(errors) - 40))
        failed = failed or bool(errors)
        if cross:
            missing_sites = sorted({k.split(os.sep)[1] if k.startswith('sites') else 'the hub (' + k + ')' for k in cross})
            print('   (links into sites/pages that do not exist yet: %s - %d targets)' % (', '.join(missing_sites), len(cross)))
        if http:
            n, bad = http_walk(s, port)
            print('   HTTP: %d fetches at both URL forms, %d failures' % (n, len(bad)))
            for b in bad[:20]:
                print('   FAIL', b)
            failed = failed or bool(bad)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
