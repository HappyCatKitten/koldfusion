#!/usr/bin/env python3
"""Dashdot site test: walks every page over HTTP (both URL forms), checks images, runs the link checker,
executes every page's JavaScript under gjs, and exercises the cookie-powered flows
(login, moderation, posting a comment, the lameness filter, voting, search, threshold preference).

Usage: python3 tools/test_site.py [PORT]      (default 8704; a KoldFusion server must be running)
"""
import os, re, sys, subprocess, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from jsharness import run, es3_problems

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8704
BASES = ["http://dashdot.localhost:%d/" % PORT, "http://localhost:%d/sites/dashdot/" % PORT]
fails = []
ok = 0

def check(cond, what):
    global ok
    if cond:
        ok += 1
    else:
        fails.append(what)
        print("FAIL:", what)

def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        return e.code, "", b""
    except Exception as e:
        return 0, "", str(e).encode()

pages = []
for root, dirs, files in os.walk(SITE):
    if "tools" in root.split(os.sep):
        continue
    for f in files:
        if f.endswith(".html"):
            pages.append(os.path.relpath(os.path.join(root, f), SITE))
pages.sort()
images = sorted("images/" + f for f in os.listdir(os.path.join(SITE, "images")))
print("%d pages, %d images" % (len(pages), len(images)))

# 1. HTTP: every page and image at both URL forms
for base in BASES:
    for p in pages:
        st, ct, body = fetch(base + p)
        check(st == 200 and "text/html" in ct, "%s%s -> %s %s" % (base, p, st, ct))
        check(b"Error Diagnostic Information" not in body, "%s%s shows an error page" % (base, p))
    for im in images:
        st, ct, body = fetch(base + im)
        check(st == 200 and ct.startswith("image/gif") and body[:3] == b"GIF", "%s%s -> %s %s" % (base, im, st, ct))
    st, ct, body = fetch(base)
    check(st == 200 and b"dashdot" in body.lower(), "%s (directory index) -> %s" % (base, st))

# 2. static link check
r = subprocess.run([sys.executable, os.path.join(HERE, "checklinks.py"), SITE], capture_output=True, text=True)
print(r.stdout.strip().splitlines()[-1])
check(r.returncode == 0, "checklinks: " + r.stdout[-500:])

# 3. every page's JavaScript runs without errors (logged out and logged in) and is ES3-clean
for p in pages:
    path = os.path.join(SITE, p)
    for cookies in ({}, {"dd_user": "tester", "dd_points": "5"}):
        res = run(path, cookies=cookies)
        check(not res["errors"], "JS errors in %s %s: %s" % (p, cookies, res["errors"][:2]))
    bad = es3_problems(path)
    check(not bad, "non-1999 JavaScript in %s: %s" % (p, bad))

A = os.path.join(SITE, "article", "y2kfridge.html")

# 4. login box
res = run(os.path.join(SITE, "index.html"), after='ddLogin({unickname:{value:"tester"}, upasswd:{value:"x"}});')
check(res["cookies"].get("dd_user") == "tester" and res["cookies"].get("dd_points") == "5", "login sets cookies: %s" % res["cookies"])
check(any("moderate" in a for a in res["alerts"]), "login announces moderator points")

# 5. moderation: menus appear only for logged-in moderators, doMod records and the score changes
res = run(A)
check('NAME="m1"' not in res["out"], "no moderation menus when logged out")
res = run(A, cookies={"dd_user": "tester", "dd_points": "5"})
check('NAME="m1"' in res["out"] and "moderator point" in res["out"], "moderation menus + button when logged in")
m = re.search(r"\(Score:(-?\d)(?:, (\w+))?\)", res["out"])
before = int(m.group(1))
form = ('{"mod": {elements: [{name: "m1", options: [{value: ""}, {value: "-1:Overrated"}], selectedIndex: 1},'
        ' {name: "m2", options: [{value: ""}, {value: "1:Funny"}], selectedIndex: 0}]}}')
res = run(A, cookies={"dd_user": "tester", "dd_points": "5"}, forms=form, after="doMod();")
check(res["cookies"].get("dd_mods") == "y2kfridge:1:-1:Overrated", "dd_mods recorded: %s" % res["cookies"].get("dd_mods"))
check(res["cookies"].get("dd_points") == "4", "a moderator point was spent")
check(res["location"] and res["location"].startswith("../moderated.html?n=1"), "goes to moderated.html: %s" % res["location"])
res = run(A, cookies={"dd_user": "tester", "dd_points": "4", "dd_mods": "y2kfridge:1:-1:Overrated"})
m2 = re.search(r"\(Score:(-?\d)(?:, (\w+))?\)", res["out"])
check(int(m2.group(1)) == max(-1, before - 1) and m2.group(2) == "Overrated", "score reflects moderation: %s" % m2.group(0))
res = run(A, cookies={"dd_user": "tester", "dd_points": "1"}, forms=form.replace("selectedIndex: 0", "selectedIndex: 1"), after="doMod();")
check(any("only have 1" in a for a in res["alerts"]), "can't spend more points than you have")
res = run(os.path.join(SITE, "moderated.html"), search="?n=1&sid=y2kfridge", cookies={"dd_points": "4"})
check("<B>1</B> moderation" in res["out"] and "<B>4</B> moderator" in res["out"], "moderated.html summary")

# 6. posting a comment (and the lameness filter)
R = os.path.join(SITE, "reply.html")
res = run(R, search="?sid=y2kfridge&pid=3")
check("Replying to" in res["out"] and "#3" in res["out"], "reply page shows context")
post = ('postIt({sid: {value: "y2kfridge"}, pid: {value: "3"}, postanon: {checked: false},'
        ' postersubj: {value: "My fridge is fine"}, postercomment: {value: "Mine runs Linix.\\n\\nNo <script> here."},'
        ' posttype: {options: [{value: "text"}], selectedIndex: 0}});')
res = run(R, search="?sid=y2kfridge&pid=3", cookies={"dd_user": "tester"}, after=post)
posted = res["cookies"].get("dd_posts_y2kfridge", "")
check("My fridge is fine" in posted and "&lt;script&gt;" in posted and "tester" in posted, "comment stored: %r" % posted[:120])
check(res["location"] == "article/y2kfridge.html?posted=1#mine", "back to the story: %s" % res["location"])
res = run(A, cookies={"dd_posts_y2kfridge": posted})
check("My fridge is fine" in res["out"] and "reply to" in res["out"], "posted comment appears on the story page")
res = run(R, search="?sid=y2kfridge", after=post.replace("My fridge is fine", "frist psot"))
check(any("Lameness filter" in a for a in res["alerts"]) and not res["location"], "lameness filter blocks first post")
res = run(R, search="?sid=y2kfridge", after=post.replace("postanon: {checked: false}", "postanon: {checked: true}"),
          cookies={"dd_user": "tester"})
check("Anonymous Coward" in res["cookies"].get("dd_posts_y2kfridge", ""), "post anonymously")

# 7. voting
P = os.path.join(SITE, "pollbooth.html")
res = run(P, search="?qid=y2kplans&aid=2")
check(res["cookies"].get("dd_voted_y2kplans") == "2" and "(your vote)" in res["out"] and "registered" in res["out"], "vote recorded")
res = run(P, search="?qid=y2kplans&aid=3", cookies={"dd_voted_y2kplans": "2"})
check("already voted" in res["out"] and res["cookies"].get("dd_voted_y2kplans") == "2", "no double voting")
res = run(P, search="?qid=editor")
check("one true editor" in res["out"] and "Cast your vote" in res["out"], "past poll results + ballot")

# 8. search
res = run(os.path.join(SITE, "search.html"), search="?query=fridge")
check("article/y2kfridge.html" in res["out"], "search finds the fridge story")
res = run(os.path.join(SITE, "search.html"), search="?query=zzzqqq")
check("No matches" in res["out"], "search with no hits")

# 9. threshold preference redirects the default story page; explicit pages don't
res = run(A, cookies={"dd_thresh": "3"})
check(res["location"] == "replace:y2kfridge_t3.html", "threshold preference redirect: %s" % res["location"])
res = run(os.path.join(SITE, "article", "y2kfridge_t3.html"), cookies={"dd_thresh": "3"})
check(res["location"] is None, "no redirect loop on the threshold page")
res = run(os.path.join(SITE, "preferences.html"), after='savePrefs({thresh: {options: [{value: "4"}], selectedIndex: 0}});')
check(res["cookies"].get("dd_thresh") == "4", "preferences saved")

# 10. threshold pages hide low scores
for t in (-1, 3, 5):
    fn = "y2kfridge%s.html" % ("" if t == 1 else "_t" + ("m1" if t < 0 else str(t)))
    html = open(os.path.join(SITE, "article", fn), encoding="latin-1").read()
    scores = [int(x) for x in re.findall(r"<NOSCRIPT>\(Score:(-?\d)", html)]
    check(scores and min(scores) >= t, "threshold %d page only shows score >= %d" % (t, t))

print("\n%d checks passed, %d failed" % (ok, len(fails)))
sys.exit(1 if fails else 0)
