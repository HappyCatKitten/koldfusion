#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Walks every uBid page and auction flow in a real (headless) Firefox.

    python3 tools/flowtest.py PORT

Checks: all pages load without script errors (at both URL forms), listings, proxy bidding
(win the lead, get outbid), bid validation and sign-in on the confirm page, auctions ending
and picking a winner, relisting, won items in My uBid, selling an item, registration,
feedback, search and bid history.
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
        n = b.js("return (typeof I == 'undefined' || typeof auction == 'undefined') ? -1 : document.body.innerHTML.length")
        if errs or not n or n < 0:
            bad += 1
            ok(False, "page %s: errors %s, body %s" % (p, errs, n))
    return bad


def flows(b, base):
    b.cmd("WebDriver:DeleteAllCookies")
    b.go(base + "index.html")
    ok("What are you looking for?" in b.text(), "home page search box")
    ok(b.js("return pick('featured', '', false).length") > 3, "featured auctions are live")
    b.go(base + "category/toys.html")
    ok(b.text().count("$") >= 10, "toys category lists items with prices")
    # ------------------------------------------------ pick a live item with bids, no reserve, not ours
    iid = b.js("""var t = now();
        for (var i = 0; i < I.length; i++) { var A = auction(I[i], t);
          if (A.live && A.nbids >= 2 && I[i][5] == 0 && I[i][3] != 'beaniebaron' && A.end - t > 2 * HOUR) return I[i][0]; }""")
    ok(iid is not None, "found a live item to bid on (%s)" % iid)
    b.go(base + "item/%s.html" % iid)
    ok("Currently" in b.text() and "Time left" in b.text(), "item page shows current bid and time left")
    left1 = b.js("return document.forms['tl'].left.value")
    import time
    time.sleep(2.2)
    left2 = b.js("return document.forms['tl'].left.value")
    ok(left1 and left2 and ("min" in left1 or "hour" in left1 or "day" in left1), "time-left countdown shows (%s -> %s)" % (left1, left2))
    minbid = b.js("return auction(findItem('%s'), now()).minBid" % iid)
    # too low
    b.go(base + "bid.html?item=%s&maxbid=%.2f" % (iid, (minbid - 5) / 100.0))
    ok("Problem with bid" in b.text(), "bid below minimum rejected")
    # good bid, confirm with wrong then right password
    high = b.js("var A = auction(findItem('%s'), now()); return A.highMax;" % iid)
    mymax = max(minbid, high) + 5000
    b.go(base + "bid.html?item=%s&maxbid=%.2f" % (iid, mymax / 100.0))
    ok("Review and Confirm Bid" in b.text() and "Place bid" in b.js("return document.body.innerHTML"), "review bid page")
    b.js("var f = document.forms['confirm']; f.userid.value = 'beaniebaron'; f.pass.value = 'nope';")
    b.js("placeBid()")
    ok(any("incorrect" in a for a in b.popalerts()), "wrong password rejected")
    b.js("var f = document.forms['confirm']; f.userid.value = 'beaniebaron'; f.pass.value = 'bidbid';")
    b.run_and_wait("placeBid()")
    ok("bidresult.html" in b.url() and "You are the current high bidder" in b.text(), "proxy bid wins the lead")
    st = b.js("var A = auction(findItem('%s'), now()); return [A.high, A.price, A.highMax, A.nbids];" % iid)
    ok(st[0] == "beaniebaron" and st[2] == mymax and st[1] <= high + 5000, "price is one increment over the runner-up (%s)" % st)
    b.go(base + "item/%s.html" % iid)
    ok("You are the current high bidder" in b.text() and "that's you" in b.text(), "item page shows you as high bidder")
    # the auction ends: who wins, and does it relist?
    w = b.js("""var it = findItem('%s'), A = auction(it, now()); var E = auction(it, A.end + 1000); var R = auction(it, A.relist + 1000);
                return [E.live, E.winner, E.highMine, R.live, R.nbids <= it[9].split(';').length];""" % iid)
    ok(w[0] is False and w[1] == "beaniebaron" and w[2] is True, "when the clock runs out you win (%s)" % w)
    ok(w[3] is True and w[4] is True, "auction relists two days later with a fresh bid history")
    # bid history
    b.go(base + "bidhistory.html?item=%s" % iid)
    ok("(you)" in b.text() and "beaniebaron" in b.text(), "bid history lists your bid")
    # ------------------------------------------------ get outbid on another item
    iid2 = b.js("""var t = now();
        for (var i = 0; i < I.length; i++) { var A = auction(I[i], t);
          if (A.live && A.nbids >= 2 && A.highMax > A.minBid + 100 && I[i][3] != 'beaniebaron' && I[i][0] != '%s') return I[i][0]; }""" % iid)
    mb2 = b.js("return auction(findItem('%s'), now()).minBid" % iid2)
    b.go(base + "bid.html?item=%s&maxbid=%.2f" % (iid2, mb2 / 100.0))
    b.js("var f = document.forms['confirm']; f.pass.value = 'bidbid';")
    b.run_and_wait("placeBid()")
    ok("You have been outbid" in b.text(), "a lower maximum is outbid by an earlier proxy")
    # ------------------------------------------------ a win from an earlier run shows in My uBid
    won = b.js("""var it = null, t = now();
        for (var i = 0; i < I.length; i++) { if (I[i][5] == 0 && I[i][3] != 'beaniebaron' && I[i][0] != '%s' && I[i][0] != '%s') { it = I[i]; break; } }
        var A = auction(it, t), len = (it[6] + 2) * DAY, prevStart = A.start - len;
        var s = getCookie('ubid_bids');
        setCookie('ubid_bids', it[0] + ':' + 9000000 + ':' + (prevStart + 1000) + ':beaniebaron' + (s ? ';' + s : ''), 30);
        return it[1];""" % (iid, iid2))
    b.go(base + "myubid.html")
    txt = b.text()
    ok("Items I'm Bidding On" in txt and "High bidder" in txt and "Outbid" in txt, "My uBid shows high-bidder and outbid items")
    ok("Items I've Won" in txt and won.split()[0] in txt.split("Items I've Won")[1], "My uBid lists an auction won in an earlier run")
    ok("Items I'm Selling" in txt, "My uBid selling section (beaniebaron is a house seller too)")
    # ------------------------------------------------ completed auctions
    b.go(base + "completed.html")
    ok(b.js("return pick('all', '', true).length") > 5 and "Sold for" in b.text(), "completed auctions list winners")
    b.go(base + "ending.html")
    ok("Going, Going, Gone" in b.text(), "going, going, gone page")
    # ------------------------------------------------ sell an item
    b.go(base + "sell.html")
    b.js("""var f = document.forms['sell']; f.userid.value = 'beaniebaron'; f.pass.value = 'bidbid';
            f.title.value = 'TALKING Y2K BUG plush - RARE L@@K'; f.desc.value = 'Plush millennium bug, says the year 1900 when squeezed.';
            f.minbid.value = '4.00'; f.pic[2].checked = true; f.cat.selectedIndex = 10;""")
    b.run_and_wait("listItem()")
    ok("sold.html" in b.url() and "Your item is listed" in b.text(), "sell your item -> listed")
    uid = b.js("return myListings()[0][0]")
    b.go(base + "uitem.html?id=%s" % uid)
    ok("TALKING Y2K BUG" in b.text() and "This is your auction" in b.text(), "your listing page")
    b.go(base + "category/toys.html")
    ok("YOUR LISTING" in b.text(), "your listing appears in its category")
    # ------------------------------------------------ feedback
    b.go(base + "feedback.html?to=garage_gus")
    b.js("var f = document.forms['leave']; f.comment.value = 'Great seller, fast shipping!';")
    b.run_and_wait("leaveFeedback()")
    ok("member/garage_gus.html" in b.url() and "left from this computer" in b.text(), "feedback shows on the member profile")
    ok(b.js("return scoreOf('garage_gus')") == 6101, "feedback raises the rating")
    # ------------------------------------------------ search
    b.go(base + "search.html?q=furby")
    ok(b.js("return pick('search', 'furby', false).length + pick('search', 'furby', true).length") >= 4, "search finds Furbys")
    b.go(base + "search.html?seller=pezhead")
    ok("seller pezhead" in b.text(), "search by seller")
    b.go(base + "search.html?q=lunchbox&completed=1")
    ok("completed item" in b.text(), "search completed auctions")
    # ------------------------------------------------ register a new member
    b.go(base + "index.html")
    b.run_and_wait("signOut()")
    b.go(base + "register.html")
    b.js("var f = document.forms['reg']; f.email.value = 'kid@example.com'; f.userid.value = 'furby'; f.pw1.value = 'gurby'; f.pw2.value = 'gurby';")
    b.js("doRegister()")
    ok(any("agree" in a for a in b.popalerts()), "must agree to the User Agreement")
    b.js("document.forms['reg'].userid.value = 'pezhead'; document.forms['reg'].agree.checked = true;")
    b.js("doRegister()")
    ok(any("already taken" in a for a in b.popalerts()), "taken User ID rejected")
    b.js("document.forms['reg'].userid.value = 'furby_fan_2000';")
    b.run_and_wait("doRegister()")
    ok("myubid.html" in b.url() and "furby_fan_2000" in b.text(), "new member registered and signed in")
    b.go(base + "signin.html")
    b.js("var f = document.forms['si']; f.userid.value = 'furby_fan_2000'; f.pass.value = 'gurby';")
    b.run_and_wait("doSignin()")
    ok("Hello" in b.text(), "new member signs in")


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
