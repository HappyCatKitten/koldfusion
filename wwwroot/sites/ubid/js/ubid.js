// uBid auction engine -- JavaScript 1.2 style, no server required.
// Every auction runs on a fixed schedule computed from EPOCH, so the same auctions are
// live, ending and closed for everybody, and they relist themselves two days after they close.
// Bids from house bidders are pre-generated (I[n][9]); your own bids live in a cookie.
// Needs items.js (I, CATS, USERS) and the page variable P (relative path to the site root).

function noteError(msg, url, line) { if (!window.__e) window.__e = new Array(); window.__e[window.__e.length] = msg + " @" + line; return false; }
window.onerror = noteError;

var DAY = 86400000, HOUR = 3600000, MIN = 60000;

// ------------------------------------------------------------------ cookies & misc
function getCookie(name) {
  var s = document.cookie, k = name + "=", i = s.indexOf(k);
  while (i != -1) {
    if (i == 0 || s.charAt(i - 1) == " " || s.charAt(i - 1) == ";") {
      var j = s.indexOf(";", i);
      if (j == -1) j = s.length;
      return unescape(s.substring(i + k.length, j));
    }
    i = s.indexOf(k, i + 1);
  }
  return "";
}
function setCookie(name, val, days) {
  var d = new Date();
  d.setTime(d.getTime() + (days ? days : 365) * DAY);
  document.cookie = name + "=" + escape(val) + "; expires=" + d.toGMTString() + "; path=/";
}
function delCookie(name) { document.cookie = name + "=; expires=Thu, 01-Jan-1970 00:00:01 GMT; path=/"; }
function qs(name) {
  var q = location.search.substring(1).split("&");
  for (var i = 0; i < q.length; i++) {
    var p = q[i].split("=");
    if (p[0] == name) return unescape((p[1] || "").replace(/\+/g, " "));
  }
  return "";
}
function esc(s) { return ("" + s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); }
function money(c) {
  c = Math.round(c);
  var d = Math.floor(c / 100), r = c % 100, ds = "" + d, out = "";
  while (ds.length > 3) { out = "," + ds.substring(ds.length - 3) + out; ds = ds.substring(0, ds.length - 3); }
  return "$" + ds + out + "." + (r < 10 ? "0" : "") + r;
}
function cents(s) {
  s = ("" + s).replace(/[$,\s]/g, "");
  if (s == "" || isNaN(parseFloat(s))) return -1;
  return Math.round(parseFloat(s) * 100);
}
function now() { return (new Date()).getTime(); }

// ------------------------------------------------------------------ dates, Pacific time, always 1999
var MON = new Array("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec");
function pacific(t) {
  var d = new Date(t), m = d.getUTCMonth();
  var dst = (m > 2 && m < 10);
  var p = new Date(t - (dst ? 7 : 8) * HOUR);
  return new Array(p, dst ? "PDT" : "PST");
}
function two(n) { return (n < 10 ? "0" : "") + n; }
function longTime(t) {
  var a = pacific(t), p = a[0];
  return MON[p.getUTCMonth()] + "-" + two(p.getUTCDate()) + "-99 " + two(p.getUTCHours()) + ":" + two(p.getUTCMinutes()) + ":" + two(p.getUTCSeconds()) + " " + a[1];
}
function shortTime(t) {
  var p = pacific(t)[0];
  return two(p.getUTCMonth() + 1) + "/" + two(p.getUTCDate()) + " " + two(p.getUTCHours()) + ":" + two(p.getUTCMinutes());
}
function timeLeft(ms) {
  if (ms <= 0) return "Auction has ended.";
  var d = Math.floor(ms / DAY), h = Math.floor((ms % DAY) / HOUR), m = Math.floor((ms % HOUR) / MIN), s = Math.floor((ms % MIN) / 1000);
  if (d > 0) return d + " day" + (d == 1 ? "" : "s") + ", " + h + " hour" + (h == 1 ? "" : "s") + " +";
  if (h > 0) return h + " hour" + (h == 1 ? "" : "s") + ", " + m + " min" + (m == 1 ? "" : "s") + " +";
  return m + " min" + (m == 1 ? "" : "s") + ", " + s + " sec" + (s == 1 ? "" : "s");
}

// ------------------------------------------------------------------ users and feedback stars
function findUser(id) {
  id = id.toLowerCase();
  for (var i = 0; i < USERS.length; i++) if (USERS[i][0] == id) return USERS[i];
  return null;
}
function myFeedbackFor(id) {
  // feedback you left on this computer: cookie ubid_fb = to^type^comment^item^time;...
  var s = getCookie("ubid_fb"), out = new Array();
  if (s == "") return out;
  var a = s.split(";");
  for (var i = 0; i < a.length; i++) { var f = a[i].split("^"); if (f[0] == id) out[out.length] = f; }
  return out;
}
function scoreOf(id) {
  var u = findUser(id), sc = 0;
  if (u) sc = u[1];
  else if (id == userId()) sc = 0;
  var f = myFeedbackFor(id);
  for (var i = 0; i < f.length; i++) sc += (f[i][1] == "positive" ? 1 : (f[i][1] == "negative" ? -1 : 0));
  return sc;
}
function starImg(score) {
  var s = "";
  if (score >= 5000) s = "gold"; else if (score >= 1000) s = "red"; else if (score >= 500) s = "purple";
  else if (score >= 100) s = "turquoise"; else if (score >= 50) s = "green"; else if (score >= 10) s = "yellow";
  if (s == "") return "";
  return " <A HREF=\"" + P + "help.html#stars\"><IMG SRC=\"" + P + "images/stars/star_" + s + ".gif\" WIDTH=16 HEIGHT=16 BORDER=0 ALIGN=ABSMIDDLE ALT=\"" + s + " star\"></A>";
}
function userLink(id) {
  var href = findUser(id) ? P + "member/" + id + ".html" : P + "feedback.html?user=" + escape(id);
  return "<A HREF=\"" + href + "\">" + esc(id) + "</A> (<A HREF=\"" + href + "\">" + scoreOf(id) + "</A>)" + starImg(scoreOf(id));
}

// ------------------------------------------------------------------ accounts
// demo members (password check is a tiny hash, as secure as 1999)
function pwHash(s) { var h = 11; for (var i = 0; i < s.length; i++) h = (h * 37 + s.charCodeAt(i)) % 999983; return "" + h; }
var DEMO = new Array(new Array("beaniebaron", "bidbid"), new Array("y2kprepper", "canned"));
function registered() {
  var s = getCookie("ubid_reg"), out = new Array();
  for (var i = 0; i < DEMO.length; i++) out[out.length] = new Array(DEMO[i][0], DEMO[i][0] + "@example.com", pwHash(DEMO[i][1]), "");
  if (s != "") { var a = s.split(";"); for (var i = 0; i < a.length; i++) out[out.length] = a[i].split("|"); }
  return out;
}
function findAccount(id) {
  var r = registered(); id = id.toLowerCase();
  for (var i = 0; i < r.length; i++) if (r[i][0] == id) return r[i];
  return null;
}
function checkLogin(id, pw) {
  var a = findAccount(id);
  if (!a) return "There is no registered uBid user with the User ID \"" + id + "\". Please check the spelling, or register (it's free!).";
  if (a[2] != pwHash(pw)) return "The password you entered is incorrect. Please try again.";
  return "";
}
function userId() { return getCookie("ubid_user"); }
function signIn(id) { setCookie("ubid_user", id.toLowerCase(), 30); }
function signOut() { delCookie("ubid_user"); location.href = P + "index.html"; return false; }

// ------------------------------------------------------------------ the auction engine
// I[n] = id, title, cat, seller, start, reserve, durDays, phaseMs, featured, bids, location, fixedStart, kind
function findItem(id) {
  for (var i = 0; i < I.length; i++) if (I[i][0] == id) return I[i];
  var u = myListings();
  for (var i = 0; i < u.length; i++) if (u[i][0] == id) return u[i];
  return null;
}
function itemURL(it) { return it[11] ? P + "uitem.html?id=" + it[0] : P + "item/" + it[0] + ".html"; }
function thumbURL(it) { return P + "images/items/" + (it[11] ? "stock_" + it[12] : it[0]) + "_t.gif"; }
function photoURL(it) { return P + "images/items/" + (it[11] ? "stock_" + it[12] : it[0]) + ".gif"; }
function catName(c) { for (var i = 0; i < CATS.length; i++) if (CATS[i][0] == c) return CATS[i][1]; return c; }
function inc(c) {
  if (c < 100) return 5; if (c < 500) return 25; if (c < 2500) return 50; if (c < 10000) return 100;
  if (c < 25000) return 250; if (c < 50000) return 500; if (c < 100000) return 1000; return 2500;
}
// your bids: cookie ubid_bids = id:maxcents:time;...
function myBids() {
  var s = getCookie("ubid_bids"), out = new Array();
  if (s == "") return out;
  var a = s.split(";");
  for (var i = 0; i < a.length; i++) { var b = a[i].split(":"); out[out.length] = new Array(b[0], parseInt(b[1]), parseFloat(b[2]), b[3] || ""); }
  return out;
}
function addMyBid(id, max, who) {
  var b = myBids(), out = new Array();
  out[0] = id + ":" + max + ":" + now() + ":" + who;
  for (var i = 0; i < b.length && out.length < 24; i++) out[out.length] = b[i][0] + ":" + b[i][1] + ":" + b[i][2] + ":" + b[i][3];
  setCookie("ubid_bids", out.join(";"), 30);
}
function auction(it, t) {
  var A = new Object();
  var dur = it[6] * DAY;
  if (it[11]) { A.k = 0; A.start = it[11]; }
  else {
    var len = dur + 2 * DAY;
    A.k = Math.floor((t - EPOCH - it[7]) / len);
    A.start = EPOCH + it[7] + A.k * len;
  }
  A.end = A.start + dur;
  A.live = (t < A.end);
  A.relist = A.start + dur + 2 * DAY;
  // gather the bids placed so far in this run of the auction
  var bids = new Array();
  if (it[9] != "") {
    var hb = it[9].split(";");
    for (var i = 0; i < hb.length; i++) {
      var p = hb[i].split(",");
      var bt = A.start + parseFloat(p[0]) * dur;
      if (bt <= t) bids[bids.length] = new Array(bt, p[1], parseInt(p[2]), false);
    }
  }
  var mine = myBids();
  for (var i = mine.length - 1; i >= 0; i--) {
    if (mine[i][0] == it[0] && mine[i][2] >= A.start && mine[i][2] < A.end && mine[i][2] <= t)
      bids[bids.length] = new Array(mine[i][2], mine[i][3] != "" ? mine[i][3] : userId(), mine[i][1], true);
  }
  // sort by time (simple insertion sort; there are never many)
  for (var i = 1; i < bids.length; i++) {
    var x = bids[i], j = i - 1;
    while (j >= 0 && bids[j][0] > x[0]) { bids[j + 1] = bids[j]; j--; }
    bids[j + 1] = x;
  }
  // proxy bidding: the highest maximum wins, paying one increment over the runner-up
  var price = it[4], high = "", highMax = 0, highMine = false;
  for (var i = 0; i < bids.length; i++) {
    var b = bids[i];
    if (high == "") { high = b[1]; highMax = b[2]; highMine = b[3]; price = it[4]; continue; }
    if (b[1] == high) { if (b[2] > highMax) highMax = b[2]; continue; }
    if (b[2] > highMax) { price = Math.min(b[2], highMax + inc(highMax)); high = b[1]; highMax = b[2]; highMine = b[3]; }
    else { price = Math.min(highMax, b[2] + inc(b[2])); }
  }
  A.bids = bids;
  A.nbids = bids.length;
  A.price = price;
  A.high = high;
  A.highMax = highMax;
  A.highMine = highMine;
  A.minBid = (bids.length == 0) ? it[4] : price + inc(price);
  A.reserveMet = (it[5] == 0 || (bids.length > 0 && highMax >= it[5]));
  if (A.reserveMet && it[5] > 0 && price < it[5]) A.price = Math.min(highMax, it[5]);
  A.winner = (!A.live && bids.length > 0 && A.reserveMet) ? high : "";
  return A;
}

// ------------------------------------------------------------------ your own listings (Sell your item)
// cookie ubid_sell = id~title~cat~startcents~dur~listedTime~pic~desc~reserve;...
function myListings() {
  var s = getCookie("ubid_sell"), out = new Array();
  if (s == "") return out;
  var a = s.split(";");
  for (var i = 0; i < a.length; i++) {
    var f = a[i].split("~");
    if (f.length < 8) continue;
    var start = parseInt(f[3]), listed = parseFloat(f[5]), dur = parseInt(f[4]);
    // a few house bidders find your item: deterministic from the item id
    var seed = 0;
    for (var k = 0; k < f[0].length; k++) seed = (seed * 31 + f[0].charCodeAt(k)) % 2147483647;
    var n = 2 + seed % 6, bids = new Array(), max = start;
    for (var k = 0; k < n; k++) {
      seed = (seed * 16807) % 2147483647;
      var who = USERS[seed % USERS.length][0];
      max = Math.round(max * (1.15 + (seed % 40) / 100) + 25);
      bids[bids.length] = (0.002 + 0.12 * k * k / (n * n) + 0.0005 * k) + "," + who + "," + max;
    }
    out[out.length] = new Array(f[0], f[1], f[2], userIdOf(f[0]), start, parseInt(f[8] || "0"), dur, 0, 0, bids.join(";"), "", listed, f[6], f[7]);
  }
  return out;
}
function userIdOf(listingId) { var p = listingId.split("-"); return p.length > 2 ? p[1] : userId(); }

// ------------------------------------------------------------------ listing tables
function allItems() {
  var out = new Array();
  for (var i = 0; i < I.length; i++) out[out.length] = I[i];
  var u = myListings();
  for (var i = 0; i < u.length; i++) out[out.length] = u[i];
  return out;
}
var TH = "<FONT FACE=\"Arial, Helvetica\" SIZE=2><B>";
function listTable(rows, mode) {
  // rows: array of [item, auctionState]; mode: "live" or "ended"
  var t = now(), h = "";
  h += "<TABLE BORDER=0 CELLPADDING=3 CELLSPACING=0 WIDTH=\"100%\">";
  h += "<TR BGCOLOR=\"#CCCCFF\"><TD>" + TH + "Item</B></FONT></TD><TD ALIGN=RIGHT>" + TH + (mode == "ended" ? "Sold for" : "Price") + "</B></FONT></TD><TD ALIGN=CENTER>" + TH + "Bids</B></FONT></TD><TD ALIGN=RIGHT NOWRAP>" + TH + (mode == "ended" ? "Ended" : "Ends PT") + "</B></FONT></TD></TR>";
  if (rows.length == 0) h += "<TR><TD COLSPAN=4><FONT SIZE=2><I>No items found.</I></FONT></TD></TR>";
  for (var i = 0; i < rows.length; i++) {
    var it = rows[i][0], A = rows[i][1];
    var left = A.end - t;
    h += "<TR BGCOLOR=\"" + (i % 2 ? "#EFEFEF" : "#FFFFFF") + "\"><TD><FONT SIZE=3>";
    h += "<A HREF=\"" + itemURL(it) + "\">" + esc(it[1]) + "</A>";
    h += " <IMG SRC=\"" + P + "images/pic.gif\" WIDTH=22 HEIGHT=14 ALT=\"[PIC]\" ALIGN=ABSMIDDLE>";
    if (t - A.start < DAY && A.live) h += " <IMG SRC=\"" + P + "images/new_icon.gif\" WIDTH=30 HEIGHT=13 ALT=\"NEW!\" ALIGN=ABSMIDDLE>";
    if (A.nbids >= 12) h += " <IMG SRC=\"" + P + "images/hot.gif\" WIDTH=14 HEIGHT=16 ALT=\"HOT!\" ALIGN=ABSMIDDLE>";
    if (it[11]) h += " <FONT SIZE=1 COLOR=\"#E0218A\"><B>YOUR LISTING</B></FONT>";
    if (A.highMine && A.live) h += " <FONT SIZE=1 COLOR=\"#009900\"><B>YOU'RE THE HIGH BIDDER</B></FONT>";
    h += "</FONT></TD><TD ALIGN=RIGHT VALIGN=TOP NOWRAP><FONT SIZE=3><B>" + money(A.price) + "</B></FONT>";
    if (mode == "ended" && A.nbids > 0 && !A.reserveMet) h += "<BR><FONT SIZE=1>reserve not met</FONT>";
    h += "</TD><TD ALIGN=CENTER VALIGN=TOP><FONT SIZE=3>" + (A.nbids == 0 ? "-" : A.nbids) + "</FONT></TD>";
    if (mode == "ended") h += "<TD ALIGN=RIGHT VALIGN=TOP NOWRAP><FONT SIZE=2>" + shortTime(A.end) + "<BR>" + (A.winner != "" ? "to " + esc(A.winner) : "no sale") + "</FONT></TD></TR>";
    else h += "<TD ALIGN=RIGHT VALIGN=TOP NOWRAP><FONT SIZE=2" + (left < 5 * HOUR ? " COLOR=\"#FF0000\"" : "") + ">" + shortTime(A.end) + (left < 5 * HOUR ? "<BR><B>" + timeLeft(left) + "</B>" : "") + "</FONT></TD></TR>";
  }
  h += "</TABLE>";
  return h;
}
function sortRows(rows, by) {
  for (var i = 1; i < rows.length; i++) {
    var x = rows[i], j = i - 1;
    while (j >= 0 && ((by == "price" && rows[j][1].price < x[1].price) || (by == "end" && rows[j][1].end > x[1].end) ||
           (by == "ended" && rows[j][1].end < x[1].end) || (by == "new" && rows[j][1].start < x[1].start))) { rows[j + 1] = rows[j]; j--; }
    rows[j + 1] = x;
  }
  return rows;
}
// does an auction match a filter? kind: "all", "cat", "featured", "seller", "search", "soon", "new"
function matches(it, A, kind, arg) {
  if (kind == "all") return true;
  if (kind == "cat") return it[2] == arg;
  if (kind == "featured") return it[8] == 1;
  if (kind == "seller") return it[3] == arg;
  if (kind == "soon") return A.end - now() < arg;
  if (kind == "new") return now() - A.start < arg;
  if (kind == "search") {
    var words = arg.toLowerCase().split(" "), hay = (it[1] + " " + (it[13] || "") + " " + catName(it[2]) + " " + it[0] + " " + it[3]).toLowerCase();
    for (var w = 0; w < words.length; w++) if (words[w] != "" && hay.indexOf(words[w]) == -1) return false;
    return true;
  }
  return false;
}
// select live (or ended) auctions matching a filter
function pick(kind, arg, ended) {
  var out = new Array(), t = now(), all = allItems();
  for (var i = 0; i < all.length; i++) {
    var A = auction(all[i], t);
    if ((ended ? !A.live : A.live) && matches(all[i], A, kind, arg)) out[out.length] = new Array(all[i], A);
  }
  return out;
}
function writeCategory(cat) {
  var rows = sortRows(pick("cat", cat, false), "end");
  document.write("<FONT SIZE=2>" + rows.length + " items, ending first. Items ending within five hours are in <FONT COLOR=\"#FF0000\">red</FONT>. </FONT><BR><BR>");
  var feat = new Array(), rest = new Array();
  for (var i = 0; i < rows.length; i++) { if (rows[i][0][8]) feat[feat.length] = rows[i]; else rest[rest.length] = rows[i]; }
  if (feat.length) document.write("<FONT FACE=\"Arial, Helvetica\" SIZE=3 COLOR=\"#6A2DB8\"><B><IMG SRC=\"" + P + "images/featured.gif\" WIDTH=16 HEIGHT=16 ALIGN=ABSMIDDLE> Featured Items</B></FONT>" + listTable(feat, "live") + "<BR>");
  document.write("<FONT FACE=\"Arial, Helvetica\" SIZE=3 COLOR=\"#0E8C8C\"><B>Current Items</B></FONT>" + listTable(rest, "live"));
}

// ------------------------------------------------------------------ header bits
function writeUserLinks() {
  var u = userId();
  if (u != "") document.write("Hi, <B>" + esc(u) + "</B>! (<A HREF=\"" + P + "index.html\" onClick=\"return signOut()\">sign out</A>)");
  else document.write("<A HREF=\"" + P + "signin.html\">sign in</A> | <A HREF=\"" + P + "register.html\">register</A>");
}
function writeStamp() {
  document.write("Last updated: " + longTime(now()).replace(/^(...)-(..)-99/, "$1-$2-99,"));
}

// ------------------------------------------------------------------ the web ring "Random" button
var RING = new Array("yowza","altavisor","askreeves","orinoco","ubid","etoyz","petz","geohoods","hamstershuffle","dashdot","snapster","cnm");
function ringRandom() { location.href = P + "../" + RING[Math.floor(Math.random() * RING.length)] + "/index.html"; return false; }

// ------------------------------------------------------------------ the item page
var TL_END = 0;
function tick() {
  var f = document.forms["tl"];
  if (!f) return;
  var left = TL_END - now();
  f.left.value = timeLeft(left);
  if (left <= 0) { setTimeout("location.reload()", 1500); return; }
  setTimeout("tick()", 1000);
}
function row2(a, b, c, d) {
  return "<TR><TD VALIGN=TOP NOWRAP><FONT SIZE=2>" + a + "</FONT></TD><TD VALIGN=TOP><FONT SIZE=2>" + b + "</FONT></TD><TD WIDTH=12></TD>" +
         "<TD VALIGN=TOP NOWRAP><FONT SIZE=2>" + c + "</FONT></TD><TD VALIGN=TOP><FONT SIZE=2>" + d + "</FONT></TD></TR>";
}
function statusBanner(it, A) {
  var me = userId(), bidHere = false, mine = myBids();
  for (var i = 0; i < mine.length; i++) if (mine[i][0] == it[0] && mine[i][2] >= A.start && mine[i][2] < A.end) bidHere = true;
  var msg = "", col = "#FFFFCC";
  if (!A.live) {
    if (A.winner != "" && A.highMine) { msg = "<B>Congratulations! You won this item</B> for " + money(A.price) + ". The seller will e-mail you within three business days. Remember to leave feedback!"; col = "#CCFFCC"; }
    else if (A.winner != "") msg = "<B>Bidding is closed for this item.</B> Winning bid: " + money(A.price) + " by " + userLink(A.winner) + ".";
    else if (A.nbids > 0) msg = "<B>Bidding is closed for this item.</B> The seller's reserve price was not met, so the item did not sell.";
    else msg = "<B>Bidding is closed for this item.</B> There were no bids.";
    msg += " This item will be relisted " + longTime(A.relist) + ".";
  } else if (A.highMine) { msg = "<B>You are the current high bidder!</B> Your maximum bid is " + money(A.highMax) + ". Our proxy will bid for you up to that amount."; col = "#CCFFCC"; }
  else if (bidHere) { msg = "<B>You have been outbid.</B> Another bidder's maximum is higher than yours. <A HREF=\"#bid\">Bid again?</A>"; col = "#FFCCCC"; }
  else if (me != "" && me == it[3]) { msg = "<B>This is your auction.</B> Sit back and watch the bids roll in."; }
  if (msg != "") document.write("<TABLE BORDER=0 CELLPADDING=5 CELLSPACING=0 WIDTH=\"100%\"><TR><TD BGCOLOR=\"" + col + "\"><FONT SIZE=2>" + msg + "</FONT></TD></TR></TABLE><BR>");
}
function writeItemBox(id) {
  var it = findItem(id);
  if (!it) { document.write("<B>Item not found.</B> It may have been removed by the seller."); return; }
  var t = now(), A = auction(it, t);
  statusBanner(it, A);
  var cur = money(A.price);
  if (it[5] > 0) cur += A.reserveMet ? " <FONT SIZE=1>(reserve met)</FONT>" : " <FONT SIZE=1 COLOR=\"#CC0000\">(reserve not yet met)</FONT>";
  var h = "<TABLE BORDER=0 CELLPADDING=2 CELLSPACING=0>";
  h += row2("<B>" + (A.live ? "Currently" : "Final price") + "</B>", "<B>" + cur + "</B>", "First bid", money(it[4]));
  h += row2("Quantity", "1", "# of bids", A.nbids + " <FONT SIZE=1>(<A HREF=\"" + P + "bidhistory.html?item=" + it[0] + "\">bid history</A>)</FONT>");
  h += row2("Time left", A.live ? "<FORM NAME=\"tl\" STYLE=\"margin:0\"><INPUT TYPE=text NAME=\"left\" SIZE=24 VALUE=\"" + timeLeft(A.end - t) + "\" onFocus=\"this.blur()\"></FORM>" : "<B>Auction has ended.</B>", "Location", esc(it[10] || "") );
  h += row2("Started", longTime(A.start), "Country", "USA");
  h += row2("Ends", longTime(A.end), "", "");
  h += "<TR><TD COLSPAN=5><HR SIZE=1 NOSHADE></TD></TR>";
  h += row2("Seller (Rating)", userLink(it[3]) + "<BR><FONT SIZE=1>(<A HREF=\"" + (findUser(it[3]) ? P + "member/" + it[3] + ".html" : P + "feedback.html?user=" + it[3]) + "\">view comments in seller's Feedback Profile</A>) (<A HREF=\"#\" onClick=\"alert('The seller has been sent your question by carrier pigeon. Please allow 2-3 business days.'); return false\">ask seller a question</A>)</FONT>", "", "");
  h += row2(A.live ? "High bid" : "Winner", A.high != "" ? userLink(A.high) + (A.highMine ? " <FONT COLOR=\"#009900\" SIZE=1><B>(that's you!)</B></FONT>" : "") : "--", "", "");
  h += row2("Payment", "Money order/Cashier's check, Personal check", "", "");
  h += row2("Shipping", "Buyer pays fixed shipping charges. Will ship to United States only.", "", "");
  h += "</TABLE>";
  document.write(h);
  if (A.live) { TL_END = A.end; setTimeout("tick()", 1000); }
}
function writeBidForm(id) {
  var it = findItem(id), t = now(), A = auction(it, t);
  if (!A.live) {
    document.write("<P><FONT SIZE=3>Bidding is closed for this item. Watch for it to be relisted " + longTime(A.relist) + ", or <A HREF=\"" + P + "category/" + it[2] + ".html\">browse similar items</A>.</FONT></P>");
    return;
  }
  if (userId() != "" && userId() == it[3]) {
    document.write("<P><FONT SIZE=3>You are the seller of this item, so you can't bid on it. (Nice try, though.)</FONT></P>");
    return;
  }
  var h = "<FORM NAME=\"bidform\" ACTION=\"" + P + "bid.html\" METHOD=GET><INPUT TYPE=hidden NAME=\"item\" VALUE=\"" + it[0] + "\">";
  h += "<TABLE BORDER=0 CELLPADDING=4><TR><TD COLSPAN=2><FONT SIZE=3><B>uBidding on:</B> " + esc(it[1]) + "</FONT></TD></TR>";
  h += "<TR><TD><FONT SIZE=2>Current minimum bid</FONT></TD><TD><FONT SIZE=3><B>" + money(A.minBid) + "</B></FONT></TD></TR>";
  h += "<TR><TD><FONT SIZE=2><B>Your maximum bid:</B></FONT></TD><TD><FONT SIZE=2>$<INPUT TYPE=text NAME=\"maxbid\" SIZE=10> <INPUT TYPE=submit VALUE=\"Review bid\"></FONT></TD></TR>";
  h += "<TR><TD></TD><TD><FONT SIZE=1>(Minimum bid: " + money(A.minBid) + ")</FONT></TD></TR></TABLE></FORM>";
  h += "<FONT SIZE=2><B>How proxy bidding works:</B> enter the most you are willing to pay. uBid will bid on your behalf, only as much as needed to keep you in the lead, ";
  h += "up to your maximum. Nobody, not even the seller, can see your maximum while the auction runs. <A HREF=\"" + P + "help.html#bidding\">More about bidding</A>.</FONT>";
  document.write(h);
}

// ------------------------------------------------------------------ feedback you left (member pages)
function writeMyFeedback(user) {
  var f = myFeedbackFor(user);
  if (f.length == 0) return;
  document.write("<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH=\"100%\">");
  for (var i = 0; i < f.length; i++) {
    var col = f[i][1] == "positive" ? "#008800" : (f[i][1] == "negative" ? "#CC0000" : "#000000");
    var lab = f[i][1] == "positive" ? "Praise" : (f[i][1] == "negative" ? "Complaint" : "Neutral");
    document.write("<TR BGCOLOR=\"#FFFFCC\"><TD><FONT SIZE=2>User: <B>" + esc(userId() || "you") + "</B> <FONT SIZE=1 COLOR=\"#E0218A\">(left from this computer)</FONT><BR>Date: " + longTime(parseFloat(f[i][4])) + " &nbsp; Item: " + esc(f[i][3]) + "<BR><FONT COLOR=\"" + col + "\"><B>" + lab + ":</B></FONT> " + esc(f[i][2]) + "</FONT></TD></TR>");
  }
  document.write("</TABLE>");
}
