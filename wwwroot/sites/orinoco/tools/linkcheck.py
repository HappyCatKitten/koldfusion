#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Link checker for a static 1999 Web site.

Reads every .html file in the site folder (the parent of tools/), and checks that every
HREF/SRC/ACTION/BACKGROUND is relative (never starting with "/" or a scheme), and that it
points at a file that exists.  Links that climb out of the site must go to another 1999 Web
site's index.html or to the web ring hub.  With --http PORT it also fetches every file
at both http://<site>.localhost:PORT/ and http://localhost:PORT/sites/<site>/.

    python3 tools/linkcheck.py [--http 8702]
"""
import os
import re
import sys
import urllib.request
from urllib.parse import unquote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
SITE = os.path.basename(ROOT)
SITES_DIR = os.path.dirname(ROOT)
RING = ["yowza", "altavisor", "askreeves", "orinoco", "ubid", "etoyz", "petz", "geohoods",
        "hamstershuffle", "dashdot", "snapster", "cnm"]
ATTR = re.compile(r"""\b(HREF|SRC|ACTION|BACKGROUND)\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))""", re.I)


def files():
    for dp, dn, fn in os.walk(ROOT):
        for f in fn:
            yield os.path.join(dp, f)


def strip_scripts(html):
    # links built inside <SCRIPT> blocks are checked by the flow test, not here
    return re.sub(r"(?is)<script\b[^>]*>.*?</script>", lambda m: re.sub(r"(?is)^(<script\b[^>]*>).*$", r"\1", m.group(0)), html)


def check():
    errors, nlinks = [], 0
    pages = [f for f in files() if f.endswith(".html") and "/tools/" not in f]
    for path in pages:
        html = strip_scripts(open(path, encoding="latin-1").read())
        for m in ATTR.finditer(html):
            url = m.group(3) if m.group(3) is not None else (m.group(4) if m.group(4) is not None else m.group(5))
            nlinks += 1
            rel = os.path.relpath(path, ROOT)
            if url.startswith(("mailto:", "javascript:", "#")) or url == "":
                continue
            if url.startswith("/") or re.match(r"^[a-z]+:", url, re.I):
                errors.append("%s: absolute URL %s" % (rel, url))
                continue
            target = unquote(url.split("#")[0].split("?")[0])
            if target == "":
                continue
            full = os.path.normpath(os.path.join(os.path.dirname(path), target))
            if not full.startswith(ROOT + os.sep) and full != ROOT:
                # climbing out: allowed only to ../<site>/index.html (or deeper pages of a sibling) and ../../web1999/
                relout = os.path.relpath(full, SITES_DIR)
                parts = relout.split(os.sep)
                if parts[0] == ".." and parts[1:] == ["web1999", "index.html"]:
                    continue
                if parts[0] in RING:
                    if parts[0] in ("orinoco", "ubid", "etoyz") and not os.path.exists(full):
                        errors.append("%s: missing sibling page %s" % (rel, url))
                    continue
                errors.append("%s: link leaves the 1999 Web: %s" % (rel, url))
                continue
            if os.path.isdir(full):
                full = os.path.join(full, "index.html")
            if not os.path.exists(full):
                errors.append("%s: broken link %s" % (rel, url))
    # links built in JavaScript as P + "page.html..." (P is the page's path to the site root)
    jsre = re.compile(r'P \+ "([^"]+?\.(?:html|gif|mid))(?:[?#][^"]*)?"')
    scripts = [f for f in files() if f.endswith(".js")] + pages
    for path in scripts:
        for m in jsre.finditer(open(path, encoding="latin-1").read()):
            nlinks += 1
            target = m.group(1)
            if target.startswith("../"):
                parts = target.split("/")
                if (parts[1] in RING and parts[-1] == "index.html") or (parts[1] in RING and parts[1] in ("orinoco", "ubid", "etoyz")) or target == "../../web1999/index.html":
                    full = os.path.normpath(os.path.join(ROOT, target))
                    if parts[1] in ("orinoco", "ubid", "etoyz") and not os.path.exists(full):
                        errors.append("%s: JavaScript link to missing sibling page %s" % (os.path.relpath(path, ROOT), target))
                    continue
            if not os.path.exists(os.path.join(ROOT, target)):
                errors.append("%s: JavaScript link to missing file %s" % (os.path.relpath(path, ROOT), target))
    return pages, nlinks, errors


def http(port):
    bad = []
    n = 0
    for f in files():
        if "/tools/" in f:
            continue
        rel = os.path.relpath(f, ROOT).replace(os.sep, "/")
        for base in ("http://%s.localhost:%s/" % (SITE, port), "http://localhost:%s/sites/%s/" % (port, SITE)):
            n += 1
            try:
                r = urllib.request.urlopen(base + rel, timeout=20)
                body = r.read()
                if r.status != 200 or (rel.endswith(".html") and b"Error Diagnostic Information" in body):
                    bad.append("%s%s -> %s" % (base, rel, r.status))
            except Exception as e:
                bad.append("%s%s -> %s" % (base, rel, e))
    return n, bad


def main():
    pages, nlinks, errors = check()
    print("%s: %d pages, %d links/images checked, %d problems" % (SITE, len(pages), nlinks, len(errors)))
    for e in errors[:200]:
        print("  " + e)
    if "--http" in sys.argv:
        port = sys.argv[sys.argv.index("--http") + 1]
        n, bad = http(port)
        print("%s: %d HTTP fetches (both URL forms), %d failures" % (SITE, n, len(bad)))
        for b in bad[:100]:
            print("  " + b)
        errors += bad
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
