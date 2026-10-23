#!/usr/bin/env python3
"""Static link checker for a 1999 Web site folder.

Usage: python3 tools/checklinks.py [SITE_DIR]   (default: the folder above tools/)

Reads every .html/.htm/.js file, extracts HREF/SRC/BACKGROUND/ACTION attributes
plus quoted '*.html|gif|jpg|mid|js' strings inside scripts, and checks that
  * no URL starts with "/" and no URL is absolute http(s)://
  * every relative target exists inside the site folder, or (when it climbs out)
    is another 1999 Web site's index.html or the ring hub web1999/index.html.
Exit status 1 if anything is broken.
"""
import os, re, sys

SITES = "yowza altavisor askreeves orinoco ubid etoyz petz geohoods hamstershuffle dashdot snapster cnm".split()
site = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), ".."))
sites_dir = os.path.dirname(site)
wwwroot = os.path.dirname(sites_dir)

ATTR = re.compile(r'''\b(?:href|src|background|action|lowsrc|dynsrc)\s*=\s*("([^"]*)"|'([^']*)'|([^\s>]+))''', re.I)
SCRIPT = re.compile(r'<script[^>]*>(.*?)</script>', re.I | re.S)
JSSTR = re.compile(r'''["']([A-Za-z0-9_./-]+\.(?:html?|gif|jpe?g|png|mid|js))(?:[?#][^"']*)?["']''')
errors = []
checked = 0

def check(src_file, url):
    global checked
    url = url.strip()
    if not url or url.startswith(("#", "mailto:", "javascript:", "about:")):
        return
    if "+" in url and ("'" in url or '"' in url):
        return   # JS-built URL fragment
    if url.startswith("/"):
        errors.append((src_file, url, "root-relative URL"))
        return
    if re.match(r"^[a-z]+://", url, re.I):
        errors.append((src_file, url, "absolute URL"))
        return
    path = re.split(r"[?#]", url)[0]
    if not path:
        return
    target = os.path.normpath(os.path.join(os.path.dirname(src_file), path))
    checked += 1
    if target.startswith(site + os.sep) or target == site:
        if os.path.isdir(target):
            target = os.path.join(target, "index.html")
        if not os.path.exists(target):
            errors.append((src_file, url, "missing"))
        return
    rel = os.path.relpath(target, wwwroot)
    parts = rel.split(os.sep)
    if rel == os.path.join("web1999", "index.html"):
        return
    if len(parts) == 3 and parts[0] == "sites" and parts[1] in SITES and parts[2] == "index.html":
        return
    errors.append((src_file, url, "climbs out of the site to " + rel))

for root, dirs, files in os.walk(site):
    if "tools" in root.split(os.sep):
        continue
    for f in files:
        if not f.lower().endswith((".html", ".htm", ".js")):
            continue
        p = os.path.join(root, f)
        text = open(p, encoding="latin-1").read()
        if f.lower().endswith(".js"):
            scripts = [text]
            html = ""
        else:
            scripts = SCRIPT.findall(text)
            html = SCRIPT.sub("", text)
        for m in ATTR.finditer(html):
            check(p, m.group(2) if m.group(2) is not None else (m.group(3) if m.group(3) is not None else m.group(4)))
        for s in scripts:
            for m in JSSTR.finditer(s):
                check(p, m.group(1))
            for m in ATTR.finditer(s.replace('\\"', '"')):
                v = m.group(2) if m.group(2) is not None else (m.group(3) if m.group(3) is not None else m.group(4))
                if "'" in v or '"' in v or "+" in v:
                    continue
                check(p, v)

for f, u, why in errors:
    print("%s: %s (%s)" % (os.path.relpath(f, site), u, why))
print("%d links checked, %d problems" % (checked, len(errors)))
sys.exit(1 if errors else 0)
