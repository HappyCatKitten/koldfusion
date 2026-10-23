# -*- coding: utf-8 -*-
"""A tiny Marionette client: drives a headless Firefox so the flow tests can run the
site's 1999 JavaScript for real (cookies, document.write, forms).  No dependencies.

    with Browser() as b:
        b.go("http://orinoco.localhost:8702/")
        b.js("return document.title")
"""
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time


class Browser(object):
    def __init__(self, port=28702, width=1200, height=1600):
        self.port = port
        # snap-packaged Firefox can only see non-hidden folders under $HOME/snap/firefox/common
        base = os.path.expanduser("~/snap/firefox/common")
        if not os.path.isdir(base):
            base = tempfile.gettempdir()
        self.profile = tempfile.mkdtemp(prefix="kfflow", dir=base)
        with open(os.path.join(self.profile, "user.js"), "w") as f:
            f.write('user_pref("marionette.port", %d);\n' % port)
            f.write('user_pref("browser.shell.checkDefaultBrowser", false);\n')
            f.write('user_pref("dom.disable_open_during_load", false);\n')
            f.write('user_pref("network.dns.localDomains", "localhost");\n')
        self.proc = subprocess.Popen(["firefox", "--headless", "--marionette", "--no-remote", "--profile", self.profile,
                                      "--window-size=%d,%d" % (width, height)],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.sock = None
        for _ in range(150):
            try:
                self.sock = socket.create_connection(("127.0.0.1", port), timeout=60)
                break
            except OSError:
                time.sleep(0.2)
        if not self.sock:
            raise RuntimeError("Firefox/Marionette did not start")
        self.buf = b""
        self._read()  # greeting
        self.msgid = 0
        self.cmd("WebDriver:NewSession", {"capabilities": {"alwaysMatch": {"unhandledPromptBehavior": "accept"}}})
        self.alerts = []
        try:
            self.cmd("WebDriver:SetWindowRect", {"width": width, "height": height})
        except RuntimeError:
            pass

    def _read(self):
        while b":" not in self.buf:
            self.buf += self.sock.recv(65536)
        n, rest = self.buf.split(b":", 1)
        n = int(n)
        while len(rest) < n:
            rest += self.sock.recv(65536)
        self.buf = rest[n:]
        return json.loads(rest[:n].decode("utf-8"))

    def cmd(self, name, params=None):
        self.msgid += 1
        data = json.dumps([0, self.msgid, name, params or {}]).encode("utf-8")
        self.sock.sendall(str(len(data)).encode() + b":" + data)
        while True:
            r = self._read()
            if r[0] == 1 and r[1] == self.msgid:
                if r[2]:
                    raise RuntimeError("%s: %s" % (name, r[2].get("message", r[2])))
                return r[3]

    # ---- helpers
    def go(self, url):
        self.cmd("WebDriver:Navigate", {"url": url})
        self.hook_alerts()

    def hook_alerts(self):
        # record alert()/confirm() text instead of blocking on modal dialogs
        self.js("""
            if (!window.__hooked) {
              window.__hooked = true;
              window.alert = function (m) { var a = JSON.parse(sessionStorage.getItem('__alerts') || '[]'); a.push(String(m)); sessionStorage.setItem('__alerts', JSON.stringify(a)); };
              window.confirm = function (m) { window.alert('CONFIRM: ' + m); return true; };
            }""")

    def popalerts(self):
        r = self.js("var a = JSON.parse(sessionStorage.getItem('__alerts') || '[]'); sessionStorage.setItem('__alerts', '[]'); return a;")
        return r or []

    def js(self, script, args=None):
        r = self.cmd("WebDriver:ExecuteScript", {"script": script, "args": args or []})
        return r.get("value")

    def url(self):
        return self.cmd("WebDriver:GetCurrentURL")["value"]

    def text(self):
        return self.js("return document.body ? document.body.innerText : ''")

    def wait_load(self, old_url=None, timeout=10):
        t = time.time()
        while time.time() - t < timeout:
            try:
                u = self.url()
                st = self.js("return document.readyState")
                if (old_url is None or u != old_url) and st == "complete":
                    self.hook_alerts()
                    return u
            except RuntimeError:
                pass
            time.sleep(0.1)
        return self.url()

    def run_and_wait(self, script, timeout=10):
        """run JS that navigates (e.g. a form submit) and wait for the next page"""
        old = self.url()
        self.js("window.__marker = 1;")
        self.js(script)
        t = time.time()
        while time.time() - t < timeout:
            try:
                if self.js("return window.__marker === undefined && document.readyState == 'complete'"):
                    time.sleep(0.25)
                    if self.js("return document.readyState == 'complete' && document.body != null"):
                        self.hook_alerts()
                        return self.url()
            except RuntimeError:
                pass
            time.sleep(0.1)
        return self.url()

    def screenshot(self, path, full=False):
        import base64
        r = self.cmd("WebDriver:TakeScreenshot", {"full": full})
        with open(path, "wb") as f:
            f.write(base64.b64decode(r["value"]))

    def close(self):
        try:
            self.cmd("Marionette:Quit", {"flags": ["eForceQuit"]})
        except Exception:
            pass
        try:
            self.proc.wait(10)
        except Exception:
            self.proc.kill()
        shutil.rmtree(self.profile, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()
