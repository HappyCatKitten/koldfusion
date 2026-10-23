#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Walks every Orinoco.com page and shopping flow in a real (headless) Firefox.

    python3 tools/flowtest.py PORT [--base http://localhost:PORT/sites/orinoco/]

Needs a server on PORT (./bin/kfserver -p PORT) and Firefox.  Checks: every page loads
without a JavaScript error, cart add/update/delete, sign-in (demo + new customer), the
three-step checkout, 1-Click, order cancel, wish list, reviews, helpful votes, search
and e-cards -- at both URL forms.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from marionette import Browser  # noqa: E402

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
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
        for f in fn:
            if f.endswith(".html"):
                out.append(os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, "/"))
    return sorted(out)


def page_errors(b, base, pages):
    """load each page; orinoco.js records script errors in window.__e"""
    bad = 0
    for p in pages:
        b.go(base + p)
        errs = b.js("return window.__e || []")
        n = b.js("return (typeof ITEMS == 'undefined') ? -1 : document.body.innerHTML.length")
        if errs or not n or n < 0:
            bad += 1
            ok(False, "page %s: errors %s, body %s" % (p, errs, n))
    return bad


def flows(b, base):
    first = lambda s: re.search(s, b.text())  # noqa: E731
    b.cmd("WebDriver:DeleteAllCookies")
    b.go(base + "index.html")
    ok("Earth's Biggest" in b.js("return document.title"), "home page title")
    ok("Sign in" in b.text(), "home says Sign in when signed out")
    codes = b.js("var a = []; for (var i = 0; i < ITEMS.length; i++) a.push(ITEMS[i][0]); return a;")
    pike = b.js("for (var i = 0; i < ITEMS.length; i++) if (ITEMS[i][1].indexOf('Cellar of Whispers') != -1) return ITEMS[i][0];")
    other = codes[5]
    # ---------------------------------------------------------------- cart
    b.go(base + "detail/%s.html" % pike)
    ok("You Save" in b.text() and "Usually ships" in b.text(), "detail page shows You Save + availability")
    ok("Customers who bought this book also bought" in b.text(), "also-bought list")
    b.run_and_wait("cartAdd('%s', 1)" % pike)
    ok(b.url().split("?")[0].endswith("cart.html"), "add to cart goes to cart")
    ok("Added to your Shopping Cart" in b.text() and "Penelope Pike" in b.text(), "cart shows added item")
    b.go(base + "detail/%s.html" % other)
    b.run_and_wait("cartAdd('%s', 1)" % other)
    ok(b.js("return cartCount()") == 2, "two items in cart")
    b.js("document.forms['cart'].elements['q0'].value = '3';")
    b.run_and_wait("updateCart()")
    ok(b.js("return cartCount()") == 4, "update quantity to 3")
    sub = b.js("return money(cartTotal(cartGet()))")
    ok(sub in b.text(), "subtotal %s shown" % sub)
    b.run_and_wait("cartDelete(1)")
    ok(b.js("return cartCount()") == 3, "delete item from cart")
    ok("items in your cart" in b.text(), "header cart line")
    # ---------------------------------------------------------------- checkout (signed out -> sign in)
    b.run_and_wait("checkoutStart()")
    ok("signin.html" in b.url() and "next=checkout.html" in b.url(), "checkout asks to sign in")
    b.js("var f = document.forms['signin']; f.email.value = 'demo@orinoco.com'; f.password.value = 'wrong';")
    b.js("doSignin()")
    ok(any("does not match" in a for a in b.popalerts()), "wrong password rejected")
    b.js("var f = document.forms['signin']; f.email.value = 'demo@orinoco.com'; f.password.value = 'river';")
    b.run_and_wait("doSignin()")
    ok(b.url().endswith("checkout.html"), "demo sign-in continues to checkout")
    b.js("var f = document.forms['addr']; f.street.value = '1 Riverbank Way'; f.city.value = 'Ciudad Bolivar'; f.state.value = 'BO'; f.zip.value = '8001'; f.country.selectedIndex = 3;")
    b.run_and_wait("saveAddr()")
    ok(b.url().endswith("checkout2.html"), "address -> shipping & payment")
    b.js("var f = document.forms['pay']; f.cardnum.value = '1234 5678 9012 3456';")
    b.js("savePay()")
    ok(any("doesn't look right" in a for a in b.popalerts()), "bad card number rejected (Luhn)")
    b.js("var f = document.forms['pay']; f.cardnum.value = '4111 1111 1111 1111'; f.ship[1].checked = true; f.giftwrap.checked = true;")
    b.run_and_wait("savePay()")
    ok(b.url().endswith("checkout3.html"), "payment -> review order")
    ok("Second Day Air" in b.text() and "ending in 1111" in b.text() and "Venezuela" in b.text(), "review shows ship method, card, address")
    total = b.js("var c = cartGet(); return money(cartTotal(c) + shipCost(1, cartCount()) + 249 * cartCount());")
    ok(total in b.text(), "order total %s" % total)
    b.run_and_wait("doPlace()")
    ok("thanks.html?order=" in b.url(), "place order -> thank you")
    ok("Thank you for shopping" in b.text() and total in b.text(), "thank-you page shows total")
    ok(b.js("return cartCount()") == 0, "cart emptied after order")
    ok(b.js("return oneClickOn()") is True, "1-Click switched on")
    # ---------------------------------------------------------------- 1-Click
    b.go(base + "detail/%s.html" % codes[10])
    ok("1-Click ordering is ON" in b.text(), "detail page says 1-Click is on")
    b.run_and_wait("oneClick('%s')" % codes[10])
    ok("oneclick=1" in b.url() and "Ordered with 1-Click" in b.text(), "1-Click order placed instantly")
    b.go(base + "account.html")
    ok(len(b.js("return ordersGet()")) == 2, "account lists two orders")
    ok("Della Ware" in b.text() and "Recommendations" in b.text(), "account greets demo customer")
    no = b.js("return ordersGet()[0][0]")
    b.run_and_wait("cancelOrder('%s')" % no)
    ok(len(b.js("return ordersGet()")) == 1, "order cancelled")
    b.run_and_wait("toggle1Click()")
    ok(b.js("return oneClickOn()") is False, "1-Click switched off in Your Account")
    # ---------------------------------------------------------------- wish list
    b.go(base + "detail/%s.html" % codes[20])
    b.run_and_wait("wishAdd('%s')" % codes[20])
    ok("is on your Wish List" in b.text(), "added to wish list")
    b.run_and_wait("wishRemove('%s')" % codes[20])
    ok("Your Wish List is empty" in b.text(), "removed from wish list")
    # ---------------------------------------------------------------- reviews and votes
    b.go(base + "review.html?code=%s" % pike)
    b.js("var f = document.forms['rev']; f.stars.selectedIndex = 1; f.title.value = 'Owls everywhere'; f.text.value = 'My cat now insists on being called Professor. Great fun for the whole family.';")
    b.run_and_wait("saveReview()")
    ok("Owls everywhere" in b.text() and "your review" in b.text(), "my review shows on the detail page")
    rid = pike + "-1"
    before = b.text()
    b.run_and_wait("vote('%s','y')" % rid)
    ok(b.js("return voteGet('%s')" % rid) == "y", "helpful vote recorded")
    # ---------------------------------------------------------------- search
    b.go(base + "search.html?index=blended&keywords=penelope+pike")
    ok("2 matches" in b.text(), "search finds both Penelope Pike books")
    b.go(base + "search.html?index=music&keywords=boys")
    ok("Backalley" in b.text(), "music search")
    b.go(base + "search.html?index=toys&keywords=furby")
    ok("eToyz" in b.text(), "toy search points to eToyz")
    b.go(base + "search.html?index=books&keywords=zzzzqqq")
    ok("no matches" in b.text(), "no-match search")
    # ---------------------------------------------------------------- e-cards
    b.go(base + "ecards.html")
    b.js("var f = document.forms['card']; f.card[1].checked = true; f.to.value = 'Aunt Edna'; f.email.value = 'edna@example.com'; f.msg.value = 'Happy Y2K!';")
    b.run_and_wait("if (sendCard()) document.forms['card'].submit();")
    ok("Aunt Edna" in b.text() and "Happy Y2K!" in b.text(), "e-card sent page")
    # ---------------------------------------------------------------- new customer
    b.go(base + "index.html")
    b.run_and_wait("signOut()")
    b.go(base + "signin.html?next=account.html")
    b.js("var f = document.forms['signin']; f.email.value = 'newbie@example.com'; f.action[0].checked = true;")
    b.run_and_wait("doSignin()")
    ok("step=new" in b.url(), "new customer step")
    b.js("var f = document.forms['reg']; f.fullname.value = 'Rio Grande'; f.pw1.value = 'delta'; f.pw2.value = 'delta';")
    b.run_and_wait("doRegister()")
    ok("Rio Grande" in b.text(), "new account created and signed in")
    b.run_and_wait("signOut()")
    b.go(base + "signin.html")
    b.js("var f = document.forms['signin']; f.email.value = 'newbie@example.com'; f.password.value = 'delta';")
    b.run_and_wait("doSignin()")
    ok("Rio Grande" in b.text(), "new customer signs back in")
    b.go(base + "index.html")
    ok("Hello, Rio" in b.text(), "home greets signed-in customer")


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "8702"
    bases = ["http://orinoco.localhost:%s/" % port, "http://localhost:%s/sites/orinoco/" % port]
    with Browser() as b:
        for base in bases:
            print("== %s" % base)
            b.go(base + "index.html")
            print("  loading %d pages..." % len(all_pages()))
            bad = page_errors(b, base, all_pages())
            ok(bad == 0, "all pages load without JavaScript errors")
            flows(b, base)
    print("\n%d failures" % len(FAILS))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
