#!/usr/bin/env python3
"""Test Petz.com over HTTP.

Usage: python3 tools/test_site.py [PORT]      (default 8704)

* fetches every generated page at http://petz.localhost:PORT/<page> and http://localhost:PORT/sites/petz/<page>
* checks HTTP 200, no "Error" text, and that every referenced image / MIDI is served (200, right-ish type)
* runs tools/checklinks.py
* checks inline JavaScript: no ES5+/modern-DOM constructs, and (if gjs is installed) a real syntax parse
"""
import os, re, sys, glob, subprocess, tempfile, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8704
BASES = ["http://petz.localhost:%d/" % PORT, "http://localhost:%d/sites/petz/" % PORT]
SRC = re.compile(r'''\b(?:src|background)\s*=\s*"([^"]+)"''', re.I)
SCRIPT = re.compile(r'<script[^>]*>(.*?)</script>', re.I | re.S)
MODERN = re.compile(r'\b(let|const|class|querySelector\w*|addEventListener|classList|JSON|fetch|XMLHttpRequest|'
                    r'forEach|Promise)\b|=>|`')

problems = []
def bad(msg):
    problems.append(msg)
    print("  FAIL", msg)

def get(url):
    try:
        r = urllib.request.urlopen(url, timeout=10)
        return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        return e.code, "", b""
    except Exception as e:
        return 0, str(e), b""

pages = sorted(os.path.basename(p) for p in glob.glob(os.path.join(SITE, "*.html")))
assets = set()
for base in BASES:
    print("Fetching %d pages from %s" % (len(pages), base))
    for pg in pages:
        st, ct, body = get(base + pg)
        if st != 200:
            bad("%s%s -> HTTP %s" % (base, pg, st))
            continue
        text = body.decode("latin-1")
        if "Error" in text:
            bad("%s%s contains 'Error'" % (base, pg))
        for m in SRC.finditer(SCRIPT.sub("", text)):
            assets.add(m.group(1))
    assets.add("images/jingle.mid")
    for a in sorted(assets):
        st, ct, body = get(base + a)
        if st != 200 or not body:
            bad("%s%s -> HTTP %s" % (base, a, st))
        elif a.endswith(".gif") and not body.startswith(b"GIF8"):
            bad("%s%s is not a GIF" % (base, a))
        elif a.endswith(".mid") and not body.startswith(b"MThd"):
            bad("%s%s is not a MIDI file" % (base, a))
        elif a.endswith(".mid") and "midi" not in ct.lower():
            print("  NOTE %s%s served as %r" % (base, a, ct))
print("Assets checked per base: %d" % len(assets))

print("Link checker:")
rc = subprocess.call([sys.executable, os.path.join(HERE, "checklinks.py"), SITE])
if rc:
    bad("checklinks.py reported problems")

print("JavaScript checks:")
gjs = None
for p in os.environ.get("PATH", "").split(os.pathsep):
    if os.path.exists(os.path.join(p, "gjs")):
        gjs = os.path.join(p, "gjs")
nblocks = 0
tmpdir = tempfile.mkdtemp()
checker = os.path.join(tmpdir, "check.js")
with open(checker, "w") as f:
    f.write("const GLib = imports.gi.GLib;\n"
            "let [ok, c] = GLib.file_get_contents(ARGV[0]);\n"
            "new Function(new TextDecoder().decode(c));\n")
for pg in pages:
    text = open(os.path.join(SITE, pg), encoding="latin-1").read()
    blocks = SCRIPT.findall(text)
    handlers = re.findall(r'\bon[A-Za-z]+="([^"]*)"', text)
    for i, b in enumerate(blocks + handlers):
        nblocks += 1
        code = b.replace("<!--", "").replace("//-->", "")
        stripped = re.sub(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'|//[^\n]*', '""', code)
        m = MODERN.search(stripped)
        if m:
            bad("%s script %d uses non-1999 construct %r" % (pg, i, m.group(0)))
        if gjs:
            fn = os.path.join(tmpdir, "s.js")
            with open(fn, "w") as f:
                f.write(code)
            r = subprocess.run([gjs, checker, fn], capture_output=True, text=True)
            if r.returncode != 0:
                bad("%s script %d syntax error: %s" % (pg, i, r.stderr.strip()[:200]))
print("  %d script blocks / handlers checked%s" % (nblocks, " with gjs" if gjs else " (gjs not found: lint only)"))

print("\n%d problems" % len(problems))
sys.exit(1 if problems else 0)
