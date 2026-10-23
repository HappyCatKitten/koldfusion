#!/usr/bin/env python3
"""Snapster site test.

    python3 tools/test_site.py [PORT]        (default port 8704)

1. fetches every generated page at http://snapster.localhost:PORT/<page> and
   http://localhost:PORT/sites/snapster/<page>: expects 200 and no "Error" text;
2. fetches every image/MIDI the pages reference (both URL forms) and checks it is served;
3. lints every inline <SCRIPT> for post-1999 JavaScript (let/const/arrows/JSON/...);
4. if a JS engine is installed (node or gjs) syntax-checks every script block and runs the
   search / transfer / chat logic against a fake document to make sure it really works;
5. runs tools/checklinks.py.
Exit status 1 on any failure.
"""
import os, re, shutil, subprocess, sys, tempfile, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, '..'))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8704
BASES = ['http://snapster.localhost:%d/' % PORT, 'http://localhost:%d/sites/snapster/' % PORT]
SCRIPT = re.compile(r'<script[^>]*>(.*?)</script>', re.I | re.S)
REF = re.compile(r'''\b(?:src|background|href)\s*=\s*"([^"]+\.(?:gif|mid))"''', re.I)
MODERN = re.compile(r'\blet\s|\bconst\s|=>|`|\bclass\s|querySelector|addEventListener|classList|\bfetch\(|'
                    r'XMLHttpRequest|JSON\.|\.forEach\(|\.map\(|\.includes\(')
fails = []


def get(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return r.status, r.read(), r.headers.get('Content-Type', '')
    except urllib.error.HTTPError as e:
        return e.code, b'', ''
    except Exception as e:  # noqa
        return 0, str(e).encode(), ''


pages = sorted(f for f in os.listdir(SITE) if f.endswith('.html'))
assets = set()
scripts = {}
for pg in pages:
    text = open(os.path.join(SITE, pg), encoding='latin-1').read()
    scripts[pg] = SCRIPT.findall(text)
    for m in REF.finditer(text):
        if not m.group(1).startswith('..'):
            assets.add(m.group(1))
    for s in scripts[pg]:
        for m in re.finditer(r'"(images/[A-Za-z0-9_]+\.gif)"', s):
            assets.add(m.group(1))
for i in range(21):
    assets.add('images/bar_%02d.gif' % i)
for n in list(range(10)) + ['comma']:
    assets.add('images/cnt_%s.gif' % n)
for n in range(10):
    assets.add('images/digit_%d.gif' % n)

# 1 + 2: HTTP
for base in BASES:
    for pg in pages:
        st, body, ct = get(base + pg)
        if st != 200:
            fails.append('%s%s: HTTP %s' % (base, pg, st))
        elif b'Error' in body:
            fails.append('%s%s: contains "Error"' % (base, pg))
        elif 'text/html' not in ct:
            fails.append('%s%s: Content-Type %s' % (base, pg, ct))
    for a in sorted(assets):
        st, body, ct = get(base + a)
        want = 'image/gif' if a.endswith('.gif') else 'midi'
        if st != 200 or not body:
            fails.append('%s%s: HTTP %s' % (base, a, st))
        elif want not in ct:
            fails.append('%s%s: Content-Type %s' % (base, a, ct))
print('HTTP: %d pages + %d assets x %d URL forms checked' % (len(pages), len(assets), len(BASES)))

# 3: 1999 JavaScript only
for pg, ss in scripts.items():
    for s in ss:
        for line in s.split('\n'):
            code = re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', '""', line)
            m = MODERN.search(code)
            if m:
                fails.append('%s: modern JS %r in: %s' % (pg, m.group(0), line.strip()[:80]))

# 4: run the scripts in a JS engine if there is one
engine = shutil.which('node') or shutil.which('gjs')
if engine:
    def jsstr(s):
        return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '') \
            .replace('\u2028', '') + '"'
    prog = ['var out = (typeof print == "function") ? print : function (s) { console.log(s); };',
            'var bad = 0;',
            'function chk(name, src) { try { new Function(src); } catch (e) { out("SYNTAX " + name + ": " + e); bad++; } }']
    for pg, ss in scripts.items():
        for i, s in enumerate(ss):
            prog.append('chk(%s, %s);' % (jsstr('%s#%d' % (pg, i)), jsstr(s)))
    # functional: a tiny fake browser
    shim = '''
var written = "";
function Img() { this.src = ""; }
var location = { search: "", href: "" };
function Field() { this.value = ""; this.options = []; this.selectedIndex = 0; }
function mkForm(names) { var f = { elements: {} }; for (var i = 0; i < names.length; i++) { var x = new Field(); f[names[i]] = x; f.elements[names[i]] = x; } return f; }
var document = { cookie: "", images: {}, forms: {}, write: function (s) { written += s; } };
var images = new Proxy({}, { get: function (t, k) { if (!(k in t)) t[k] = new Img(); return t[k]; } });
document.images = images;
function alert(s) {} function prompt() { return null; } function setTimeout() {}
var navigator = { appName: "Netscape" };
'''

    def run(pg, setup, check, label):
        body = '\n'.join(scripts[pg])
        return '(function () {%s\n%s\ntry {\n%s\n%s\n} catch (e) { out("FAIL %s: " + e); bad++; }\n})();' % (
            shim, setup, body, check, label)
    prog.append(run('search.html', 'location.search = "?artist=ska&title=&max=100&speedop=ge&speed=7";'
                    'document.forms["find"] = mkForm(["artist","title","max","speedop","speed","bitrateop","bitrate",'
                    '"freqop","freq","pingop","ping"]);',
                    'var rows = written.split("TYPE=CHECKBOX").length - 1;'
                    'if (rows < 5) { out("FAIL search: only " + rows + " rows for ska/fast"); bad++; }'
                    'else out("search ska (Cable or faster): " + rows + " rows");'
                    'if (written.indexOf("dot_red") != -1) { out("FAIL search: speed filter let a red dot through"); bad++; }',
                    'search'))
    prog.append(run('search.html', 'location.search = "?artist=frosted+tips&title=modem";'
                    'document.forms["find"] = mkForm(["artist","title","max","speedop","speed","bitrateop","bitrate",'
                    '"freqop","freq","pingop","ping"]);',
                    'var rows = written.split("TYPE=CHECKBOX").length - 1;'
                    'if (rows < 1) { out("FAIL search: frosted tips/modem found nothing"); bad++; }'
                    'else out("search frosted+tips / modem: " + rows + " rows");', 'search2'))
    prog.append(run('transfer.html', 'document.cookie = "snapdl=" + escape("3.10.200");'
                    'document.forms["xf"] = mkForm(["st0","rt0","tl0","st1","rt1","tl1","st2","rt2","tl2","ust","urt","utl"]);',
                    'for (var k = 0; k < 400; k++) step();'
                    'var rows = written.split("NAME=\\"st").length - 1;'
                    'if (rows != 3 || D.length != 3) { out("FAIL transfer: " + rows + " rows"); bad++; }'
                    'else out("transfer: 3 rows; states after 200 s: " + document.forms["xf"].st0.value + " / " +'
                    ' document.forms["xf"].st1.value + " / " + document.forms["xf"].st2.value);', 'transfer'))
    prog.append(run('chat.html', 'location.search = "?channel=Rock"; document.forms["chat"] = mkForm(["log","say"]);',
                    'startChat(); for (var k = 0; k < 40; k++) more();'
                    'var f = document.forms["chat"]; f.say.value = "/me air guitars"; send(f);'
                    'if (f.log.value.indexOf("air guitars") == -1 || f.log.value.indexOf("#Rock") == -1) { out("FAIL chat"); bad++; }'
                    'else out("chat #Rock: " + f.log.value.split("\\n").length + " lines");', 'chat'))
    prog.append('out(bad ? "JS: " + bad + " problems" : "JS: all script blocks compile, logic OK"); ')
    fd, path = tempfile.mkstemp(suffix='.js')
    with os.fdopen(fd, 'w') as fh:
        fh.write('\n'.join(prog))
    r = subprocess.run([engine, path], capture_output=True, text=True)
    os.unlink(path)
    print(r.stdout.strip())
    if r.returncode != 0 or 'FAIL' in r.stdout or 'SYNTAX' in r.stdout or r.stderr.strip():
        fails.append('JS engine (%s): %s %s' % (os.path.basename(engine), r.stdout.strip()[-400:], r.stderr.strip()[-400:]))
else:
    print('JS: no node/gjs found, skipped engine checks')

# 5: link checker
r = subprocess.run([sys.executable, os.path.join(HERE, 'checklinks.py'), SITE], capture_output=True, text=True)
print(r.stdout.strip().split('\n')[-1])
if r.returncode != 0:
    fails.append('checklinks: ' + r.stdout)

for f in fails:
    print('FAIL', f)
print('%s: %d failures' % ('OK' if not fails else 'NOT OK', len(fails)))
sys.exit(1 if fails else 0)
