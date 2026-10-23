#!/usr/bin/env python3
"""HTTP/1.1, keep-alive and SSL regression tests for the KoldFusion web server and CFHTTP.

    python3 tests/http_tests.py [--keep] [-v]

Starts its own bin/kfserver (KFSERVER=... to use another binary, e.g. bin/kfserver-asan) on a throw-away install
directory and web root (tests/http/www), on HTTP port KF_TEST_PORT (8723) and SSL port KF_TEST_SSL_PORT (8546),
so the real kfroot/ is never touched. The first start also exercises certificate generation. Tests that need
the Internet (https://example.com/) are skipped when it cannot be reached.
"""
import os, re, select, shutil, signal, socket, ssl, subprocess, sys, tempfile, threading, time, http.server, socketserver

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
KF = os.environ.get('KFSERVER', os.path.join(ROOT, 'bin', 'kfserver'))
PORT = int(os.environ.get('KF_TEST_PORT', 8723))
SPORT = int(os.environ.get('KF_TEST_SSL_PORT', 8546))
VERBOSE = '-v' in sys.argv
passed = failed = skipped = 0


def check(name, cond, detail=''):
    global passed, failed
    if cond:
        passed += 1
        if VERBOSE: print('PASS', name)
    else:
        failed += 1
        print('FAIL', name, detail)


def skip(name, why):
    global skipped
    skipped += 1
    print('SKIP', name, '-', why)


# ------------------------------------------------------------------ raw HTTP helpers
class Resp:
    def __init__(self, status, reason, version, headers, body):
        self.status, self.reason, self.version, self.headers, self.body = status, reason, version, headers, body

    def h(self, name):
        return self.headers.get(name.lower())


def recv_until(sock, buf, cond, timeout=10):
    sock.settimeout(timeout)
    while not cond(buf):
        d = sock.recv(65536)
        if not d:
            raise ConnectionError('closed with %r' % buf[:200])
        buf += d
    return buf


def read_response(sock, buf=b'', head=False, timeout=10):
    """read one response; returns (Resp, leftover bytes)"""
    buf = recv_until(sock, buf, lambda b: b'\r\n\r\n' in b, timeout)
    hdr, _, rest = buf.partition(b'\r\n\r\n')
    lines = hdr.decode('latin-1').split('\r\n')
    version, status, reason = (lines[0].split(' ', 2) + [''])[:3]
    headers = {}
    for l in lines[1:]:
        k, _, v = l.partition(':')
        headers[k.strip().lower()] = v.strip()
    status = int(status)
    if status in (100, 101):
        return read_response(sock, rest, head, timeout)
    n = 0 if head or status in (204, 304) else int(headers.get('content-length', 0))
    rest = recv_until(sock, rest, lambda b: len(b) >= n, timeout)
    return Resp(status, reason, version, headers, rest[:n]), rest[n:]


def request(method, path, version='HTTP/1.1', headers=None, body=b''):
    h = {'Host': 'localhost'}
    h.update(headers or {})
    if body and 'Content-Length' not in h and 'Transfer-Encoding' not in h:
        h['Content-Length'] = str(len(body))
    return (f'{method} {path} {version}\r\n' + ''.join(f'{k}: {v}\r\n' for k, v in h.items() if v is not None) +
            '\r\n').encode() + body


def connect(port=PORT):
    return socket.create_connection(('127.0.0.1', port), timeout=10)


def is_closed(sock, wait=3):
    sock.settimeout(wait)
    try:
        return sock.recv(1) == b''
    except (ConnectionResetError, BrokenPipeError):
        return True
    except socket.timeout:
        return False


def get(path, port=PORT, **kw):
    s = connect(port)
    s.sendall(request('GET', path, 'HTTP/1.1', dict({'Connection': 'close'}, **kw)))
    r, _ = read_response(s)
    s.close()
    return r


def kv(text):
    return dict(l.split('=', 1) for l in text.splitlines() if '=' in l)


# ------------------------------------------------------------------ server management
def set_reg(root, entries):
    """edit kfroot/registry/kf.registry in place: entries {('Server','KeepAliveTimeout'): '2'}"""
    path = os.path.join(root, 'registry', 'kf.registry')
    time.sleep(1.1)                       # never in the same second as the server's own last write
    text = open(path, encoding='latin-1').read()
    for (key, entry), value in entries.items():
        sect = f'[HKEY_LOCAL_MACHINE\\SOFTWARE\\Gibson\\KoldFusion\\CurrentVersion\\{key}]'
        line = f'"{entry}"="{value}"'
        pat = re.compile(r'^"' + re.escape(entry) + r'"=.*$', re.M)
        i = text.find(sect)
        if i < 0:
            text += f'\n{sect}\n{line}\n'
            continue
        j = text.find('\n[', i + 1)
        j = len(text) if j < 0 else j
        block = text[i:j]
        block = pat.sub(line.replace('\\', '\\\\'), block) if pat.search(block) else block.rstrip('\n') + '\n' + line + '\n'
        text = text[:i] + block + text[j:]
    open(path, 'w', encoding='latin-1').write(text)
    time.sleep(1.1)                       # the registry is reloaded when its mtime changes (1 s resolution)


def start_server(tmp, env=None):
    log = open(os.path.join(tmp, 'server.log'), 'w')
    p = subprocess.Popen([KF, '-p', str(PORT), '--ssl-port', str(SPORT), '-r', os.path.join(tmp, 'kfroot'),
                          '-w', os.path.join(tmp, 'wwwroot')], stdout=log, stderr=subprocess.STDOUT,
                         env=dict(os.environ, **(env or {})))
    for _ in range(100):
        try:
            socket.create_connection(('127.0.0.1', PORT), timeout=1).close()
            return p
        except OSError:
            if p.poll() is not None:
                break
            time.sleep(0.1)
    print(open(os.path.join(tmp, 'server.log')).read())
    raise SystemExit('kfserver did not start')


def stop_server(p):
    p.send_signal(signal.SIGTERM)
    try:
        p.wait(5)
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()


# ------------------------------------------------------------------ little helper servers for CFHTTP
class Helper(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *a):
        pass

    def do_GET(self):
        self.handle_any()

    def do_POST(self):
        self.handle_any()

    def handle_any(self):
        n = int(self.headers.get('Content-Length') or 0)
        body = self.rfile.read(n) if n else b''
        if self.path.startswith('/chunked'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Transfer-Encoding', 'chunked')
            self.end_headers()
            for part in (b'Hello, ', b'chunked ', b'world', b'!' * 3000):
                self.wfile.write(b'%x;ext=1\r\n%s\r\n' % (len(part), part))
            self.wfile.write(b'0\r\nX-Trailer: yes\r\n\r\n')
        elif self.path.startswith('/redirect'):
            self.send_response(302)
            self.send_header('Location', '/target?from=redirect')
            self.send_header('Content-Length', '0')
            self.end_headers()
        elif self.path.startswith('/abs'):
            self.send_response(200)
            page = b'<A HREF="next.htm">next</A> <IMG SRC="/logo.gif">'
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(page)))
            self.end_headers()
            self.wfile.write(page)
        else:
            info = (f'method={self.command}\npath={self.path}\nauth={self.headers.get("Authorization", "")}\n'
                    f'version={self.request_version}\nhost={self.headers.get("Host")}\nbody={body.decode()}\n').encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(len(info)))
            self.end_headers()
            self.wfile.write(info)


class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class ConnectProxy(socketserver.BaseRequestHandler):
    """a minimal HTTP proxy: CONNECT tunnels, plus absolute-URI GET/POST forwarding"""
    seen = []

    def handle(self):
        data = b''
        while b'\r\n\r\n' not in data:
            d = self.request.recv(4096)
            if not d:
                return
            data += d
        first = data.split(b'\r\n', 1)[0].decode()
        ConnectProxy.seen.append(first)
        method, target, _ = first.split(' ', 2)
        if method == 'CONNECT':
            host, port = target.rsplit(':', 1)
            up = socket.create_connection(('127.0.0.1', int(port)))
            self.request.sendall(b'HTTP/1.1 200 Connection established\r\n\r\n')
            socks = [self.request, up]
            while True:
                r, _, _ = select.select(socks, [], [], 10)
                if not r:
                    break
                for s in r:
                    d = s.recv(65536)
                    if not d:
                        up.close()
                        return
                    (up if s is self.request else self.request).sendall(d)
        else:
            m = re.match(r'http://([^/:]+)(?::(\d+))?(/.*)', target)
            up = socket.create_connection(('127.0.0.1', int(m.group(2) or 80)))
            up.sendall(data.replace(target.encode(), m.group(3).encode(), 1))
            while True:
                d = up.recv(65536)
                if not d:
                    break
                self.request.sendall(d)
            up.close()


def make_cert(tmp, name):
    crt, key = os.path.join(tmp, name + '.crt'), os.path.join(tmp, name + '.key')
    subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '2', '-keyout', key, '-out', crt,
                    '-subj', '/CN=localhost/O=Not Trusted', '-addext', 'subjectAltName=DNS:localhost,IP:127.0.0.1'],
                   check=True, capture_output=True)
    return crt, key


# ------------------------------------------------------------------ the tests
def test_keepalive():
    s = connect()
    buf = b''
    for i in range(5):
        s.sendall(request('GET', '/static.htm' if i % 2 else '/hello.cfm'))
        r, buf = read_response(s, buf)
        check(f'keep-alive request {i + 1} is 200', r.status == 200, r.status)
        check(f'keep-alive request {i + 1} HTTP/1.1', r.version == 'HTTP/1.1', r.version)
        check(f'keep-alive request {i + 1} not closing', 'close' not in (r.h('connection') or ''), r.headers)
        check(f'keep-alive request {i + 1} has Content-Length', r.h('content-length') is not None)
    s.sendall(request('GET', '/hello.cfm', headers={'Connection': 'close'}))
    r, buf = read_response(s, buf)
    check('Connection: close honoured', r.h('connection') == 'close' and is_closed(s))
    s.close()

    # CGI.SERVER_PROTOCOL follows each request on a shared connection
    s = connect()
    s.sendall(request('GET', '/cgi.cfm', 'HTTP/1.0', {'Connection': 'keep-alive'}) + request('GET', '/cgi.cfm'))
    r1, buf = read_response(s)
    r2, buf = read_response(s, buf)
    v1, v2 = kv(r1.body.decode()), kv(r2.body.decode())
    check('CGI.SERVER_PROTOCOL per request', v1.get('SERVER_PROTOCOL') == 'HTTP/1.0' and v2.get('SERVER_PROTOCOL') == 'HTTP/1.1', (v1, v2))
    check('CGI.HTTP_CONNECTION per request', v1.get('HTTP_CONNECTION') == 'keep-alive' and v2.get('HTTP_CONNECTION') == '', (v1, v2))
    s.close()

    # HTTP/1.0 + Connection: keep-alive (Netscape 4 style)
    s = connect()
    s.sendall(request('GET', '/static.htm', 'HTTP/1.0', {'Connection': 'keep-alive'}))
    r, buf = read_response(s)
    check('HTTP/1.0 keep-alive answered as 1.0', r.version == 'HTTP/1.0', r.version)
    check('HTTP/1.0 keep-alive acknowledged', (r.h('connection') or '').lower() == 'keep-alive', r.headers)
    s.sendall(request('GET', '/hello.cfm', 'HTTP/1.0', {'Connection': 'keep-alive'}))
    r, buf = read_response(s, buf)
    check('HTTP/1.0 keep-alive second request', r.status == 200 and b'hello' in r.body)
    s.close()

    # plain HTTP/1.0 closes
    s = connect()
    s.sendall(request('GET', '/hello.cfm', 'HTTP/1.0'))
    r, buf = read_response(s)
    check('HTTP/1.0 without keep-alive closes', r.h('connection') == 'close' and is_closed(s))
    s.close()


def test_pipelining():
    s = connect()
    paths = ['/hello.cfm', '/static.htm', '/plain.txt', '/nothere.htm', '/hello.cfm']
    s.sendall(b''.join(request('GET', p) for p in paths))
    buf = b''
    got = []
    for p in paths:
        r, buf = read_response(s, buf)
        got.append(r.status)
    check('pipelined responses in order', got == [200, 200, 200, 404, 200], got)
    # a pipelined POST with a body followed by a GET
    s.sendall(request('POST', '/echo.cfm', headers={'Content-Type': 'application/x-www-form-urlencoded'},
                      body=b'a=1&b=two') + request('GET', '/plain.txt'))
    r, buf = read_response(s, buf)
    r2, buf = read_response(s, buf)
    check('pipelined POST body consumed exactly', b'A=1' in r.body and b'B=two' in r.body and r2.body == b'plain text file\n',
          (r.body, r2.body))
    s.close()


def test_head():
    for path in ('/static.htm', '/hello.cfm', '/plain.txt', '/missing.htm'):
        g = get(path)
        s = connect()
        s.sendall(request('HEAD', path) + request('GET', '/plain.txt'))
        h, buf = read_response(s, head=True)
        check(f'HEAD {path} status', h.status == g.status, (h.status, g.status))
        check(f'HEAD {path} Content-Length matches GET', h.h('content-length') == str(len(g.body)),
              (h.h('content-length'), len(g.body)))
        r2, buf = read_response(s, buf)
        check(f'HEAD {path} sends no body', r2.status == 200 and r2.body == b'plain text file\n', r2.body[:80])
        s.close()


def test_conditional(tmp):
    r = get('/static.htm')
    lm, etag = r.h('last-modified'), r.h('etag')
    check('static HTML has Last-Modified and ETag', lm and etag, r.headers)
    check('304 on If-Modified-Since', get('/static.htm', **{'If-Modified-Since': lm}).status == 304)
    r304 = get('/static.htm', **{'If-None-Match': etag})
    check('304 on If-None-Match', r304.status == 304 and r304.body == b'' and r304.h('etag') == etag, r304.status)
    check('200 on an old If-Modified-Since', get('/static.htm', **{'If-Modified-Since': 'Sat, 29 Oct 1994 19:43:31 GMT'}).status == 200)
    check('IE4 "; length=" suffix accepted', get('/static.htm', **{'If-Modified-Since': lm + '; length=99'}).status == 304)
    check('304 for a GIF/text file', get('/plain.txt', **{'If-Modified-Since': get('/plain.txt').h('last-modified')}).status == 304)
    # changing the zoom invalidates cached HTML (the zoom CSS is part of the page), but not plain files
    plain_lm = get('/plain.txt').h('last-modified')
    set_reg(os.path.join(tmp, 'kfroot'), {('Server', 'DisplayZoom'): '150'})
    r2 = get('/static.htm', **{'If-None-Match': etag})
    check('zoom change: ETag no longer matches', r2.status == 200 and r2.h('etag') != etag, (r2.status, r2.h('etag')))
    r3 = get('/static.htm', **{'If-Modified-Since': lm})
    check('zoom change: Last-Modified moves on', r3.status == 200 and b'zoom:150%' in r3.body, r3.status)
    check('zoom change: plain file still 304', get('/plain.txt', **{'If-Modified-Since': plain_lm}).status == 304)
    set_reg(os.path.join(tmp, 'kfroot'), {('Server', 'DisplayZoom'): '175'})


def test_bodies():
    # chunked request body
    s = connect()
    chunks = [b'name=Ada', b'+Lovelace&lang', b'=CFML']
    body = b''.join(b'%x\r\n%s\r\n' % (len(c), c) for c in chunks) + b'0\r\n\r\n'
    s.sendall(request('POST', '/echo.cfm', headers={'Transfer-Encoding': 'chunked',
                                                    'Content-Type': 'application/x-www-form-urlencoded'}, body=body))
    r, buf = read_response(s)
    v = kv(r.body.decode())
    check('chunked request body decoded', v.get('NAME') == 'Ada Lovelace' and v.get('LANG') == 'CFML', r.body)
    check('chunked request: CGI.CONTENT_LENGTH is the decoded length', v.get('length') == str(sum(map(len, chunks))), v)
    s.sendall(request('GET', '/plain.txt'))
    r, buf = read_response(s, buf)
    check('connection usable after a chunked body', r.status == 200)
    s.close()
    # Expect: 100-continue
    s = connect()
    payload = b'x=' + b'7' * 5000
    s.sendall(request('POST', '/echo.cfm', headers={'Content-Length': str(len(payload)), 'Expect': '100-continue',
                                                    'Content-Type': 'application/x-www-form-urlencoded'}))
    s.settimeout(5)
    first = s.recv(4096)
    check('Expect: 100-continue gets 100 Continue', first.startswith(b'HTTP/1.1 100 Continue\r\n\r\n'), first[:60])
    s.sendall(payload)
    r, _ = read_response(s, first[len(b'HTTP/1.1 100 Continue\r\n\r\n'):])
    check('body after 100 Continue', r.status == 200 and kv(r.body.decode()).get('X') == '7' * 5000)
    s.close()
    # too large: refused before the body is sent
    s = connect()
    s.sendall(request('POST', '/echo.cfm', headers={'Content-Length': str(512 * 1024 * 1024), 'Expect': '100-continue'}))
    r, _ = read_response(s)
    check('oversized body refused with 413', r.status == 413 and r.h('connection') == 'close', r.status)
    s.close()
    # malformed requests
    for name, raw, want in [('garbage request line', b'HELLO\r\n\r\n', 400),
                            ('HTTP/2.0 refused', b'GET / HTTP/2.0\r\nHost: x\r\n\r\n', 505),
                            ('HTTP/1.1 without Host', b'GET / HTTP/1.1\r\n\r\n', 400),
                            ('conflicting Content-Length', b'POST /echo.cfm HTTP/1.1\r\nHost: x\r\nContent-Length: 3\r\nContent-Length: 4\r\n\r\nabcd', 400),
                            ('space before colon', b'GET / HTTP/1.1\r\nHost : x\r\n\r\n', 400),
                            ('unknown transfer coding', b'POST / HTTP/1.1\r\nHost: x\r\nTransfer-Encoding: gzip\r\n\r\n', 501),
                            ('bad chunk size', b'POST /echo.cfm HTTP/1.1\r\nHost: x\r\nTransfer-Encoding: chunked\r\n\r\nzz\r\n', 400)]:
        s = connect()
        s.sendall(raw)
        r, _ = read_response(s)
        check(name, r.status == want and r.h('connection') == 'close', (r.status, r.headers))
        s.close()


def test_limits_and_timeouts(tmp):
    root = os.path.join(tmp, 'kfroot')
    set_reg(root, {('Server', 'KeepAliveTimeout'): '2', ('Server', 'KeepAliveMaxRequests'): '3', ('Server', 'HeaderTimeout'): '3'})
    s = connect()
    buf = b''
    conns = []
    for i in range(3):
        s.sendall(request('GET', '/plain.txt'))
        r, buf = read_response(s, buf)
        conns.append(r.h('connection'))
    check('per-connection request limit', conns[:2] == [None, None] and conns[2] == 'close' and is_closed(s), conns)
    s.close()
    s = connect()
    s.sendall(request('GET', '/plain.txt'))
    read_response(s)
    t0 = time.time()
    closed = is_closed(s, 6)
    check('idle keep-alive connection closed after KeepAliveTimeout', closed and 1.5 < time.time() - t0 < 4.5, time.time() - t0)
    s.close()
    # slowloris: one header byte per second never completes the request
    s = connect()
    t0 = time.time()
    status = None
    try:
        for ch in b'GET / HTTP/1.1\r\nHost: localhost\r\nX-Slow: ' + b'a' * 20:
            s.send(bytes([ch]))
            r = select.select([s], [], [], 0.5)[0]
            if r:
                status = s.recv(200)
                break
    except OSError:
        pass
    took = time.time() - t0
    check('slowloris header trickle cut off by HeaderTimeout', status is not None and b' 408 ' in status and took < 6,
          (status, took))
    s.close()
    # a client that never finishes the handshake is dropped
    raw = socket.create_connection(('127.0.0.1', SPORT), timeout=10)
    raw.sendall(b'\x16\x03\x01')
    t0 = time.time()
    check('stalled SSL handshake dropped', is_closed(raw, 8) and time.time() - t0 < 7)
    raw.close()
    # a connection that sends nothing at all
    s = connect()
    t0 = time.time()
    check('silent connection dropped by HeaderTimeout', is_closed(s, 6) and time.time() - t0 < 5)
    s.close()
    # slow POST body: deadline still holds (30 s + size/64KB/s), so only check that the thread keeps serving others
    s = connect()
    s.sendall(request('POST', '/echo.cfm', headers={'Content-Length': '100'}))
    s.sendall(b'x=1')
    ok = all(get('/plain.txt').status == 200 for _ in range(3))
    check('other clients served while a body trickles in', ok)
    s.close()
    set_reg(root, {('Server', 'KeepAliveTimeout'): '15', ('Server', 'KeepAliveMaxRequests'): '100', ('Server', 'HeaderTimeout'): '20'})


def ssl_ctx(tmp, verify=True):
    ctx = ssl.create_default_context(cafile=os.path.join(tmp, 'kfroot', 'ssl', 'kfserver.crt'))
    if not verify:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    return ctx


def ssl_connect(tmp, host='localhost'):
    raw = socket.create_connection(('127.0.0.1', SPORT), timeout=10)
    return ssl_ctx(tmp).wrap_socket(raw, server_hostname=host)


def test_https(tmp):
    crt = os.path.join(tmp, 'kfroot', 'ssl', 'kfserver.crt')
    check('self-signed certificate generated on first start', os.path.exists(crt))
    text = subprocess.run(['openssl', 'x509', '-in', crt, '-noout', '-subject', '-ext', 'subjectAltName'],
                          capture_output=True, text=True).stdout
    check('certificate subject', 'CN=localhost' in text and 'O=Gibson Mainframe Co.' in text, text)
    check('certificate SANs', all(x in text for x in ('DNS:localhost', 'DNS:*.localhost', 'IP Address:127.0.0.1',
                                                       'DNS:alpha.localhost', 'DNS:beta.localhost')), text)
    s = ssl_connect(tmp)
    buf = b''
    for i in range(3):
        s.sendall(request('GET', '/cgi.cfm'))
        r, buf = read_response(s, buf)
        check(f'HTTPS keep-alive request {i + 1}', r.status == 200, r.status)
    v = kv(r.body.decode())
    check('CGI.HTTPS on', v.get('HTTPS') == 'on', v)
    check('CGI.SERVER_PORT_SECURE 1', v.get('SERVER_PORT_SECURE') == '1')
    check('CGI.SERVER_PORT is the SSL port', v.get('SERVER_PORT') == str(SPORT), v.get('SERVER_PORT'))
    check('CGI.CERT_KEYSIZE', int(v.get('CERT_KEYSIZE') or 0) >= 128, v.get('CERT_KEYSIZE'))
    check('CGI.CERT_SECRETKEYSIZE', v.get('CERT_SECRETKEYSIZE') == '2048', v.get('CERT_SECRETKEYSIZE'))
    check('CGI.CERT_SERVER_SUBJECT', v.get('CERT_SERVER_SUBJECT') == 'CN=localhost, O=Gibson Mainframe Co.', v.get('CERT_SERVER_SUBJECT'))
    check('CGI.CERT_FLAGS without client certificate', v.get('CERT_FLAGS') == '0' and v.get('CERT_SUBJECT') == '', v)
    s.close()
    v = kv(get('/cgi.cfm').body.decode())
    check('CGI.HTTPS off on the plain port', v.get('HTTPS') == 'off' and v.get('SERVER_PORT_SECURE') == '0', v)
    # SNI + virtual sites, and redirects that keep scheme and port
    s = ssl_connect(tmp, 'alpha.localhost')
    s.sendall(request('GET', '/', headers={'Host': f'alpha.localhost:{SPORT}'}))
    r, buf = read_response(s)
    check('HTTPS virtual site via SNI', r.status == 200 and b'alpha site' in r.body, r.body[:100])
    s.sendall(request('GET', '/beta/page.htm?x=1', headers={'Host': f'alpha.localhost:{SPORT}'}))
    r, buf = read_response(s, buf)
    check('cross-site redirect keeps https and the SSL port', r.status == 302 and r.h('location') == f'https://beta.localhost:{SPORT}/page.htm?x=1',
          r.h('location'))
    s.close()
    s = connect()
    s.sendall(request('GET', '/beta/page.htm', headers={'Host': f'alpha.localhost:{PORT}', 'Connection': 'close'}))
    r, _ = read_response(s)
    check('cross-site redirect over http stays http', r.h('location') == f'http://beta.localhost:{PORT}/page.htm', r.h('location'))
    s.close()
    # HEAD and pipelining over SSL
    s = ssl_connect(tmp)
    s.sendall(request('HEAD', '/static.htm') + request('GET', '/plain.txt'))
    h, buf = read_response(s, head=True)
    r, buf = read_response(s, buf)
    check('HTTPS HEAD + pipelined GET', h.status == 200 and int(h.h('content-length')) > 0 and r.body == b'plain text file\n')
    s.close()
    # curl, if present: a real client, with verification
    if shutil.which('curl'):
        out = subprocess.run(['curl', '-s', '--cacert', crt, f'https://localhost:{SPORT}/static.htm',
                              f'https://localhost:{SPORT}/plain.txt', '-o', '/dev/null', '-o', '/dev/null',
                              '-w', '%{http_code} %{num_connects}\n'], capture_output=True, text=True).stdout.split()
        check('curl https with verification, connection reused', out == ['200', '1', '200', '0'], out)


def cfhttp(target, **params):
    from urllib.parse import urlencode
    r = get('/cfhttp.cfm?' + urlencode(dict(target=target, **params)))
    return kv(r.body.decode('latin-1')), r.body.decode('latin-1')


def test_cfhttp(tmp, helper_port, ssl_helper_port, proxy_port):
    v, raw = cfhttp(f'https://localhost:{SPORT}/hello.cfm')
    check('CFHTTP https to KoldFusion itself (verified)', v.get('status') == '200 OK' and f'hello {SPORT}' in raw, raw[:300])
    v, raw = cfhttp(f'https://127.0.0.1:{SPORT}/plain.txt')
    check('CFHTTP https by IP address', v.get('content') == 'plain text file', raw[:300])
    v, raw = cfhttp(f'https://localhost/plain.txt', port=str(SPORT))
    check('CFHTTP PORT attribute with https', v.get('content') == 'plain text file', raw[:300])
    v, raw = cfhttp(f'https://localhost:{SPORT}/echo.cfm', method='POST')
    check('CFHTTP POST over https', 'GREETING=hello there' in raw, raw[:300])
    # chunked response, HTTP/1.1, basic auth
    v, raw = cfhttp(f'http://127.0.0.1:{helper_port}/chunked')
    check('CFHTTP decodes a chunked response', v.get('content') == 'Hello, chunked world' + '!' * 3000, raw[:200])
    v, raw = cfhttp(f'http://127.0.0.1:{helper_port}/info', user='bob')
    check('CFHTTP sends HTTP/1.1 with Host', v.get('version') == 'HTTP/1.1' and v.get('host') == f'127.0.0.1:{helper_port}', v)
    check('CFHTTP USERNAME/PASSWORD basic auth', v.get('auth') == 'Basic Ym9iOnNlY3JldA==', v.get('auth'))
    # redirects
    v, raw = cfhttp(f'http://127.0.0.1:{helper_port}/redirect')
    check('CFHTTP follows redirects', v.get('path') == '/target?from=redirect', raw[:300])
    v, raw = cfhttp(f'http://127.0.0.1:{helper_port}/redirect', redirect='No')
    check('CFHTTP REDIRECT="No"', v.get('status', '').startswith('302') and v.get('location') == '/target?from=redirect', raw[:300])
    v, raw = cfhttp(f'http://127.0.0.1:{helper_port}/redirect', redirect='No', throw='Yes')
    check('CFHTTP REDIRECT="No" THROWONERROR="Yes" throws', 'error' in v, raw[:300])
    v, raw = cfhttp(f'http://127.0.0.1:{helper_port}/abs/page.htm', resolve='Yes')
    check('CFHTTP RESOLVEURL', f'HREF="http://127.0.0.1:{helper_port}/abs/next.htm"' in raw and
          f'SRC="http://127.0.0.1:{helper_port}/logo.gif"' in raw, raw[:300])
    # certificate checking against a server we don't trust
    v, raw = cfhttp(f'https://localhost:{ssl_helper_port}/info')
    check('CFHTTP refuses an untrusted certificate', v.get('status', '').startswith('Connection Failure'), raw[:300])
    v, raw = cfhttp(f'https://localhost:{ssl_helper_port}/info', throw='Yes')
    check('CFHTTP untrusted certificate error message', 'could not be verified' in raw and 'self-signed' in raw, raw[:400])
    v, raw = cfhttp(f'https://localhost:{ssl_helper_port}/info', check='No')
    check('CFHTTP CHECKCERTIFICATE="No"', 'method=GET' in raw and v.get('status') == '200 OK', raw[:300])
    # proxies: CONNECT for https, absolute URI for http
    ConnectProxy.seen.clear()
    v, raw = cfhttp(f'https://localhost:{SPORT}/hello.cfm', proxy='127.0.0.1', proxyport=str(proxy_port))
    check('CFHTTP https through a proxy (CONNECT)', f'hello {SPORT}' in raw and any(s.startswith(f'CONNECT localhost:{SPORT}') for s in ConnectProxy.seen),
          (raw[:200], ConnectProxy.seen))
    v, raw = cfhttp(f'http://127.0.0.1:{helper_port}/info', proxy='127.0.0.1', proxyport=str(proxy_port))
    check('CFHTTP http through a proxy (absolute URI)', v.get('path') == '/info' and
          any(s.startswith(f'GET http://127.0.0.1:{helper_port}/info') for s in ConnectProxy.seen), (raw[:200], ConnectProxy.seen))
    # timeouts
    t0 = time.time()
    v, raw = cfhttp('http://10.255.255.1/', throw='Yes', timeout='2')
    check('CFHTTP TIMEOUT on connect', 'error' in v and 'Timeout' in raw and time.time() - t0 < 5, raw[:200])
    # the Internet, if we have it
    try:
        socket.create_connection(('example.com', 443), timeout=5).close()
        v, raw = cfhttp('https://example.com/')
        check('CFHTTP https://example.com/ (verified)', v.get('status') == '200 OK' and 'Example Domain' in raw, raw[:300])
    except OSError as e:
        skip('CFHTTP https://example.com/', e)


def test_no_openssl(tmp):
    page = os.path.join(tmp, 'wwwroot', 'nossl.cfm')
    open(page, 'w').write('<cftry><cfhttp url="https://localhost:%d/" throwonerror="yes"></cfhttp>'
                          '<cfcatch><cfoutput>#CFCATCH.Detail#</cfoutput></cfcatch></cftry>' % SPORT)
    out = subprocess.run([KF, '-r', os.path.join(tmp, 'kfroot'), '-w', os.path.join(tmp, 'wwwroot'), '--run', page],
                         capture_output=True, text=True, env=dict(os.environ, KF_LIBSSL='none')).stdout
    check('CFHTTP https without OpenSSL: clear error', 'secure HTTP (https://) is not available' in out, out[-300:])
    os.unlink(page)


def test_concurrency():
    errors = []

    def worker():
        try:
            s = connect()
            buf = b''
            for i in range(30):
                s.sendall(request('GET', '/hello.cfm' if i % 3 else '/static.htm'))
                r, buf = read_response(s, buf)
                if r.status != 200:
                    errors.append(r.status)
            s.close()
        except Exception as e:
            errors.append(repr(e))
    ts = [threading.Thread(target=worker) for _ in range(20)]
    for t in ts: t.start()
    for t in ts: t.join()
    check('20 concurrent keep-alive clients x 30 requests', not errors, errors[:5])


def main():
    tmp = tempfile.mkdtemp(prefix='kfhttp')
    shutil.copytree(os.path.join(ROOT, 'tests', 'http', 'www'), os.path.join(tmp, 'wwwroot'))
    os.makedirs(os.path.join(tmp, 'kfroot'))
    srv = start_server(tmp)
    helpers = []
    try:
        h = ThreadingServer(('127.0.0.1', 0), Helper)
        threading.Thread(target=h.serve_forever, daemon=True).start()
        hs = ThreadingServer(('127.0.0.1', 0), Helper)
        crt, key = make_cert(tmp, 'untrusted')
        sctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        sctx.load_cert_chain(crt, key)
        hs.socket = sctx.wrap_socket(hs.socket, server_side=True)
        threading.Thread(target=hs.serve_forever, daemon=True).start()
        px = socketserver.ThreadingTCPServer(('127.0.0.1', 0), ConnectProxy)
        px.daemon_threads = True
        threading.Thread(target=px.serve_forever, daemon=True).start()
        helpers = [h, hs, px]
        test_keepalive()
        test_pipelining()
        test_head()
        test_conditional(tmp)
        test_bodies()
        test_https(tmp)
        test_cfhttp(tmp, h.server_address[1], hs.server_address[1], px.server_address[1])
        test_concurrency()
        test_limits_and_timeouts(tmp)
        test_no_openssl(tmp)
        check('server still running', srv.poll() is None)
    finally:
        stop_server(srv)
        for x in helpers:
            x.shutdown()
        if '--keep' in sys.argv:
            print('kept', tmp)
        else:
            shutil.rmtree(tmp, ignore_errors=True)
    print(f'{passed} passed, {failed} failed, {skipped} skipped')
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
