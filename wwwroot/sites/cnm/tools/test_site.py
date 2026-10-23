#!/usr/bin/env python3
"""End-to-end test for CNM Interactive.

    python3 tools/test_site.py [PORT]        (default port 8704)

Fetches every generated .html page over HTTP at both URL forms
(http://cnm.localhost:PORT/... and http://localhost:PORT/sites/cnm/...), checks for
HTTP 200 and no "Error" text, fetches every image each page references (once per form),
tries a few query-string URLs, then runs the static link checker and the JavaScript check.
"""
import os, re, subprocess, sys, urllib.error, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8704
BASES = ["http://cnm.localhost:%d/" % PORT, "http://localhost:%d/sites/cnm/" % PORT]
IMG = re.compile(r'''\b(?:SRC|BACKGROUND)\s*=\s*"([^"]+\.gif)"''', re.I)
EXTRA = ["quickvote.html?answer=2", "search.html?query=y2k&sites=CNM", "search.html?query=potato&sites=WEB",
         "weather.html?zip=04101", "customnews.html?email=me%40isp.com",
         "customnews_thanks.html?name=Pat&email=pat%40isp.com&sec=US&sec=TECH", "feedback_thanks.html?name=Pat"]


def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        return e.code, "", b""
    except Exception as e:  # connection refused etc.
        return 0, str(e), b""


pages = []
for d, dirs, files in os.walk(ROOT):
    if "tools" in d.split(os.sep):
        continue
    for f in files:
        if f.endswith(".html"):
            pages.append(os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/"))
pages.sort()

fails = 0
images_ok = 0
for base in BASES:
    seen_imgs = set()
    for rel in pages + EXTRA:
        st, ct, body = fetch(base + rel)
        text = body.decode("latin-1")
        if st != 200:
            print("FAIL %s%s -> HTTP %s %s" % (base, rel, st, ct))
            fails += 1
            continue
        if "Error" in text:
            print("FAIL %s%s contains 'Error'" % (base, rel))
            fails += 1
        if "1999 Web Ring" not in text:
            print("FAIL %s%s has no webring footer" % (base, rel))
            fails += 1
        for src in [s for s in IMG.findall(text) if "'" not in s and "+" not in s]:
            u = urllib.parse.urljoin(base + rel, src)
            if u in seen_imgs:
                continue
            seen_imgs.add(u)
            ist, ict, ib = fetch(u)
            if ist != 200 or not ib.startswith(b"GIF8"):
                print("FAIL image %s (from %s) -> %s %s" % (u, rel, ist, ict))
                fails += 1
            else:
                images_ok += 1
    print("%s: %d pages + %d query URLs fetched, %d distinct images checked" % (base, len(pages), len(EXTRA), len(seen_imgs)))

for tool in ("checklinks.py", "jscheck.py"):
    r = subprocess.run([sys.executable, os.path.join(HERE, tool)], capture_output=True, text=True)
    print(tool + ": " + r.stdout.strip().splitlines()[-1])
    if r.returncode != 0:
        print(r.stdout)
        fails += 1

print("RESULT: %s (%d failures)" % ("PASS" if fails == 0 else "FAIL", fails))
sys.exit(1 if fails else 0)
