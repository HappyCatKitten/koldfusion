#!/usr/bin/env python3
"""Syntax-checks every <SCRIPT> block and inline event handler in the generated site.

    python3 tools/jscheck.py

Uses gjs (SpiderMonkey) or node if either is installed: each unique snippet is compiled with
new Function(...) (never executed). Also greps for post-1999 JavaScript (let/const/arrow
functions/template strings/JSON/fetch/querySelector/addEventListener/classList).
"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
SCRIPT = re.compile(r"<SCRIPT[^>]*>(.*?)</SCRIPT>", re.I | re.S)
HANDLER = re.compile(r'\bon(?:Click|Change|Submit|Load)="([^"]*)"', re.I)
MODERN = re.compile(r"\blet\s|\bconst\s|=>|`|\bJSON\.|\bfetch\(|XMLHttpRequest|querySelector|addEventListener|classList|\bclass\s")

snippets = {}
for d, dirs, files in os.walk(ROOT):
    if "tools" in d.split(os.sep):
        continue
    for f in files:
        if f.endswith(".html"):
            p = os.path.join(d, f)
            t = open(p, encoding="latin-1").read()
            for s in SCRIPT.findall(t):
                s = s.replace("<!--", "").replace("//-->", "")
                snippets.setdefault(s, os.path.relpath(p, ROOT))
            for h in HANDLER.findall(SCRIPT.sub("", t)):
                h = h.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&").replace("&quot;", '"')
                snippets.setdefault(h, os.path.relpath(p, ROOT) + " (handler)")

problems = 0
for s, where in snippets.items():
    m = MODERN.search(s)
    if m:
        print("%s: modern JavaScript token %r" % (where, m.group(0)))
        problems += 1

engine = shutil.which("gjs") or shutil.which("node")
if engine:
    items = list(snippets.items())
    prog = "var src = %s; var where = %s; var bad = 0;\n" % (json.dumps([s for s, w in items]), json.dumps([w for s, w in items]))
    prog += """for (var i = 0; i < src.length; i++) {
  try { new Function(src[i]); } catch (e) { bad++; print(where[i] + ": " + e); }
}
print("compiled " + src.length + " snippets, " + bad + " syntax problems");
"""
    if engine.endswith("node"):
        prog = "var print = console.log;\n" + prog
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
        tf.write(prog)
    out = subprocess.run([engine, tf.name], capture_output=True, text=True)
    os.unlink(tf.name)
    sys.stdout.write(out.stdout + out.stderr)
    if " 0 syntax problems" not in out.stdout:
        problems += 1
else:
    print("no gjs/node found; only the modern-token scan was run on %d snippets" % len(snippets))
print("%d JavaScript problems" % problems)
sys.exit(1 if problems else 0)
