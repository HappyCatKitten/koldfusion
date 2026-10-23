#!/usr/bin/env python3
"""Runs a page's 1999-style JavaScript under gjs (SpiderMonkey) with a tiny fake browser.

    from jsharness import run
    r = run("article/y2kfridge.html", search="?x=1", cookies={"dd_user": "bob"}, after="doMod();")
    r -> dict(out=<document.write text>, cookies={...}, alerts=[...], location=<href or None>, errors=[...])

The fake browser has: document.write/cookie/forms/images, location (search, hash, href, replace,
reload), alert/confirm, window.open (a dummy window), Math/Date as usual.  Inline <SCRIPT> blocks
run in document order, each in its own try/catch so one error does not hide the next.
"""
import json, os, re, subprocess, tempfile

SCRIPT = re.compile(r"<script[^>]*>(.*?)</script>", re.I | re.S)

PRELUDE = r"""
var __out = [], __alerts = [], __errors = [], __loc = null;
var __jar = %(cookies)s;
function __auto() {
  return new Proxy({}, { get: function (t, k) {
    if (k === Symbol.toPrimitive || k === "toString" || k === "valueOf") return function () { return ""; };
    if (!(k in t)) t[k] = __auto(); return t[k]; } });
}
var document = {
  write: function (s) { __out.push(String(s)); },
  writeln: function (s) { __out.push(String(s) + "\n"); },
  open: function () {}, close: function () {},
  images: __auto(),
  forms: %(forms)s
};
Object.defineProperty(document, "cookie", {
  get: function () { var a = []; for (var k in __jar) a.push(k + "=" + __jar[k]); return a.join("; "); },
  set: function (v) {
    var parts = v.split(";"), nv = parts[0], p = nv.indexOf("=");
    var name = nv.substring(0, p).trim(), val = nv.substring(p + 1);
    var expired = /expires=([^;]*)/i.exec(v);
    if (expired && new Date(expired[1]).getTime() < Date.now()) delete __jar[name]; else __jar[name] = val;
  }
});
var location = {
  search: %(search)s, hash: %(hash)s, pathname: "/page.html",
  replace: function (u) { __loc = "replace:" + u; },
  reload: function () { __loc = "reload"; }
};
Object.defineProperty(location, "href", { get: function () { return "http://site.localhost/page.html" + location.search; },
                                          set: function (u) { __loc = String(u); } });
var window = { open: function () { return { document: document, close: function () {} }; }, location: location };
var navigator = { appName: "Netscape", appVersion: "4.7 [en] (X11; U; Linux 2.2.12 i686)", userAgent: "Mozilla/4.7" };
function alert(s) { __alerts.push(String(s)); }
function confirm(s) { __alerts.push("confirm: " + String(s)); return true; }
function setTimeout(f, ms) { return 1; }
function clearTimeout(t) {}
function setInterval(f, ms) { return 1; }
function clearInterval(t) {}
globalThis.document = document; globalThis.location = location; globalThis.window = window;
globalThis.navigator = navigator; globalThis.alert = alert; globalThis.confirm = confirm;
globalThis.setTimeout = setTimeout; globalThis.clearTimeout = clearTimeout;
globalThis.setInterval = setInterval; globalThis.clearInterval = clearInterval;
"""

EPILOGUE = r"""
print(JSON.stringify({ out: __out.join(""), alerts: __alerts, errors: __errors, location: __loc, cookies: __jar }));
"""

def extract(html):
    blocks = []
    for m in SCRIPT.finditer(html):
        code = m.group(1)
        code = re.sub(r"^\s*<!--.*$", "", code, flags=re.M)
        code = re.sub(r"^\s*//\s*-->.*$", "", code, flags=re.M)
        blocks.append(code)
    return blocks

def run(path, search="", hash_="", cookies=None, forms="__auto()", after=""):
    html = open(path, encoding="latin-1").read()
    jar = dict((k, v) for k, v in (cookies or {}).items())
    # cookies are stored escaped, like a browser would after setCookie(escape(v))
    jar = dict((k, _escape(v)) for k, v in jar.items())
    parts = [PRELUDE % dict(cookies=json.dumps(jar), forms=forms, search=json.dumps(search), hash=json.dumps(hash_))]
    for i, b in enumerate(extract(html) + ([after] if after else [])):
        # function declarations must stay global: run each block through indirect eval
        parts.append("try { (0, eval)(%s); } catch (e) { __errors.push('block %d: ' + e); }" % (json.dumps(b), i))
    parts.append(EPILOGUE)
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write("\n".join(parts))
        name = f.name
    try:
        p = subprocess.run(["gjs", name], capture_output=True, text=True, timeout=30)
    finally:
        os.unlink(name)
    lines = [l for l in p.stdout.splitlines() if l.startswith("{")]
    if not lines:
        return dict(out="", alerts=[], errors=["gjs failed: " + p.stderr[-400:]], location=None, cookies={})
    r = json.loads(lines[-1])
    r["cookies"] = dict((k, _unescape(v)) for k, v in r["cookies"].items())
    return r

def _escape(s):
    out = []
    for ch in s:
        if ch.isalnum() or ch in "@*_+-./":
            out.append(ch)
        elif ord(ch) < 256:
            out.append("%%%02X" % ord(ch))
        else:
            out.append("%%u%04X" % ord(ch))
    return "".join(out)

def _unescape(s):
    s = re.sub(r"%u([0-9A-Fa-f]{4})", lambda m: chr(int(m.group(1), 16)), s)
    return re.sub(r"%([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1), 16)), s)

ES3_BAD = [(re.compile(r"\blet\s+[A-Za-z_$][\w$]*\s*[=;,]"), "let"), (re.compile(r"\bconst\s+[A-Za-z_$][\w$]*\s*="), "const"),
           (re.compile(r"=>"), "arrow function"), (re.compile(r"`"), "template string"),
           (re.compile(r"\b(fetch|XMLHttpRequest|querySelector|addEventListener|classList|JSON)\b"), "modern API")]

def es3_problems(path):
    html = open(path, encoding="latin-1").read()
    probs = []
    for b in extract(html):
        for rx, what in ES3_BAD:
            if rx.search(b):
                probs.append(what)
    return probs
