#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Walks every eToyz page and shopping flow in a real (headless) Firefox.

    python3 tools/flowtest.py PORT

Checks: all pages load without script errors (at both URL forms), the holiday countdown,
cart add/update/remove, sign-in and new accounts, the three-step checkout with the
"arrives by Christmas" logic, orders in my eToyz, per-customer wish lists (and finding
someone else's), the Gift Finder, and search.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from marionette import Browser  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SITE = os.path.basename(ROOT)
FAILS = []


def ok(cond, what):
    print(("  ok   " if cond else "  FAIL ") + what)
    if not cond:
        FAILS.append(what)


def all_pages():
    out = []
    for dp, dn, fn in os.walk(ROOT):
        if "/tools" in dp:
            continue
        out += [os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, "/") for f in fn if f.endswith(".html")]
    return sorted(out)


def page_errors(b, base, pages):
    bad = 0
    for p in pages:
        b.go(base + p)
        errs = b.js("return window.__e || []")
        n = b.js("return (typeof T == 'undefined' || typeof cartAdd == 'undefined') ? -1 : document.body.innerHTML.length")
        if errs or not n or n < 0:
            bad += 1
            ok(False, "page %s: errors %s, body %s" % (p, errs, n))
    return bad


def flows(b, base):
    b.cmd("WebDriver:DeleteAllCookies")
    b.go(base + "index.html")
    t = b.text()
    ok("Sprocket" in t and "Top 10 Toys" in t, "home page: mascot and Top 10")
    ok(("left" in t and "Christmas" in t) or "Happy holidays" in t or "still time" in t or "Too late" in t, "holiday countdown is shown")
    ok(b.js("return deadline(11, 20).getMonth()") == 11, "countdown targets December 20")
    owl = b.js("for (var i = 0; i < T.length; i++) if (T[i][1].indexOf('Gabbo') == 0) return T[i][0];")
    blocks = b.js("return T[20][0]")
    # ---------------------------------------------------------------- cart
    b.go(base + "toy/%s.html" % owl)
    ok("Gabbo the Talking Owl" in b.text() and "Ages:" in b.text(), "toy page")
    b.js("document.forms['buy'].qty.selectedIndex = 1;")
    b.run_and_wait("document.forms['buy'].onsubmit()")
    ok("cart.html?added=" in b.url() and b.js("return cartCount()") == 2, "add 2 owls to the cart")
    b.go(base + "toy/%s.html" % blocks)
    b.run_and_wait("cartAdd('%s', 1)" % blocks)
    ok(b.js("return cartCount()") == 3, "second toy in the cart")
    b.js("document.forms['cart'].elements['q1'].value = '2';")
    b.run_and_wait("updateCart()")
    ok(b.js("return cartCount()") == 4, "update quantity")
    b.run_and_wait("removeItem(1)")
    ok(b.js("return cartCount()") == 2, "remove a toy")
    ok("FREE standard shipping" in b.text(), "free shipping message")
    # ---------------------------------------------------------------- checkout
    b.run_and_wait("startCheckout()")
    ok("signin.html" in b.url(), "checkout asks you to sign in")
    b.js("var f = document.forms['si']; f.email.value = 'demo@etoyz.com'; f.pass.value = 'nope';")
    b.js("doSignin()")
    ok(any("wrong password" in a for a in b.popalerts()), "wrong password rejected")
    b.js("var f = document.forms['si']; f.pass.value = 'toybox';")
    b.run_and_wait("doSignin()")
    ok("checkout.html?step=ship" in b.url() and "Holly Berry" in b.js("return document.forms['ship'].fullname.value"), "signed in, on to shipping")
    b.js("var f = document.forms['ship']; f.street.value = '1 Candy Cane Lane'; f.city.value = 'North Pole'; f.state.value = 'AK'; f.zip.value = '99705'; f.wrap.checked = true; f.message.value = 'Love, Santa';")
    b.run_and_wait("saveShip()")
    ok("step=pay" in b.url(), "address -> payment")
    xmas = b.js("return inTimeForXmas(0)")
    ok(("arrives by Christmas" in b.text()) == xmas or "too late for Christmas" in b.text(), "shipping options say whether they arrive by Christmas")
    b.js("var f = document.forms['pay']; f.card.value = '4111 1111 1111 1112';")
    b.js("savePay()")
    ok(any("doesn't look right" in a for a in b.popalerts()), "bad card rejected")
    b.js("var f = document.forms['pay']; f.card.value = '4111 1111 1111 1111'; f.method[1].checked = true;")
    b.run_and_wait("savePay()")
    ok("step=review" in b.url() and "ending in 1111" in b.text() and "Love, Santa" in b.text(), "review shows card, gift message")
    total = b.js("var c = cartGet(), n = cartCount(), s = cartTotal(c); return money(s + shipCost(1, n, s) + 395 * n);")
    ok(total in b.text(), "order total %s (with gift wrap and 2nd day air)" % total)
    b.run_and_wait("placeOrder()")
    ok("thanks.html?order=ETZ-" in b.url() and total in b.text(), "order placed")
    ok(b.js("return cartCount()") == 0, "cart emptied")
    b.go(base + "account.html")
    ok("Elves are packing it" in b.text() and "Gabbo" in b.text(), "order shows in my eToyz")
    # ---------------------------------------------------------------- wish lists, per customer
    b.go(base + "toy/%s.html" % blocks)
    b.run_and_wait("wishAdd('%s')" % blocks)
    ok("is on your wish list" in b.text(), "added to Holly's wish list")
    b.run_and_wait("signOut()")
    b.go(base + "toy/%s.html" % owl)
    b.run_and_wait("wishAdd('%s')" % owl)
    ok("signin.html" in b.url(), "wish list needs a sign-in")
    b.js("var f = document.forms['reg']; f.fullname.value = 'Timmy Tinsel'; f.email.value = 'timmy@example.com'; f.pw1.value = 'sled'; f.pw2.value = 'sled';")
    b.run_and_wait("doRegister()")
    b.wait_load()
    import time
    time.sleep(0.5)
    b.wait_load()
    ok("wishlist.html" in b.url() and b.js("return wishGet('timmy@example.com').length") == 1, "new customer's wish list gets the owl after sign-up")
    ok(b.js("return wishGet('demo@etoyz.com').length") == 1, "Holly's list is separate")
    b.go(base + "wishlist.html?for=demo@etoyz.com")
    ok("Holly Berry's wish list" in b.text(), "find someone else's wish list")
    b.go(base + "wishlist.html")
    b.run_and_wait("wishRemove('%s')" % owl)
    ok(b.js("return wishGet('timmy@example.com').length") == 0, "remove from wish list")
    # ---------------------------------------------------------------- gift finder and search
    b.go(base + "giftfinder.html?age=kids&price=2&for=g&cat=")
    n = b.js("""var c = 0; for (var i = 0; i < T.length; i++) { var t = T[i];
                if (t[4] <= 95 && t[5] >= 60 && t[6] >= 1000 && t[6] <= 2500 && (t[7] == 'a' || t[7] == 'g')) c++; } return c;""")
    ok(("Sprocket found %d gift" % n) in b.text() and n > 0, "gift finder: %d gifts for a 5-7 year old girl, $10-25" % n)
    b.go(base + "search.html?q=robot")
    ok("Megabot" in b.text(), "search finds the robot")
    b.go(base + "holiday.html")
    ok("Sprocket wrote a song" in b.text() and b.js("return document.forms['clock'].t.value").endswith("sec"), "holiday HQ with live clock")


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "8702"
    bases = ["http://%s.localhost:%s/" % (SITE, port), "http://localhost:%s/sites/%s/" % (port, SITE)]
    with Browser() as b:
        for base in bases:
            print("== %s" % base)
            b.go(base + "index.html")
            print("  loading %d pages..." % len(all_pages()))
            ok(page_errors(b, base, all_pages()) == 0, "all pages load without JavaScript errors")
            flows(b, base)
    print("\n%d failures" % len(FAILS))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
