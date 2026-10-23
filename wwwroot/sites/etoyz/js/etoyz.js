// eToyz shopping engine -- JavaScript 1.2 style.  Cart, accounts, per-user wish lists and
// orders all live in cookies.  Needs toys.js (T, AGES, CATS) and the page variable P.

function noteError(msg, url, line) { if (!window.__e) window.__e = new Array(); window.__e[window.__e.length] = msg + " @" + line; return false; }
window.onerror = noteError;

var DAY = 86400000;
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
var MONTHS = new Array("January","February","March","April","May","June","July","August","September","October","November","December");
var DAYS = new Array("Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday");

// ------------------------------------------------------------------ catalog
// T[i] = code, name, brand, category, min age (months), max age, price (cents), for (b/g/a), picture, rank, availability
function findToy(code) { for (var i = 0; i < T.length; i++) if (T[i][0] == code) return T[i]; return null; }
function toyURL(t) { return P + "toy/" + t[0] + ".html"; }
function toyImg(t) { return P + "images/toys/" + t[0] + "_s.gif"; }
function ageLabel(t) {
  var a = t[4], b = t[5];
  if (b >= 1200) return (a < 24 ? a + " months" : Math.floor(a / 12) + " years") + " &amp; up";
  if (b < 24) return a + "-" + b + " months";
  if (a < 24) return a + " months - " + Math.floor(b / 12) + " years";
  return Math.floor(a / 12) + "-" + Math.floor(b / 12) + " years";
}

// ------------------------------------------------------------------ holiday countdown
function deadline(month, day) {
  var n = new Date(), y = n.getFullYear();
  var d = new Date(y, month, day, 23, 59, 59);
  if (n.getTime() > (new Date(y, 11, 26)).getTime()) d = new Date(y + 1, month, day, 23, 59, 59);
  return d;
}
function writeCountdown() {
  var n = new Date(), std = deadline(11, 20), ovn = deadline(11, 23), xmas = deadline(11, 25);
  var left = std.getTime() - n.getTime();
  if (left > 0) {
    var d = Math.floor(left / DAY), h = Math.floor((left % DAY) / 3600000);
    document.write("<B>Only <FONT COLOR=\"#E21B1B\" SIZE=+1>" + d + "</FONT> day" + (d == 1 ? "" : "s") + " and <FONT COLOR=\"#E21B1B\" SIZE=+1>" + h + "</FONT> hour" + (h == 1 ? "" : "s") + " left</B> to order with standard shipping for Christmas delivery!");
  } else if (ovn.getTime() > n.getTime()) {
    document.write("<B><FONT COLOR=\"#E21B1B\">Standard shipping has closed, but there's still time!</FONT></B> Choose Overnight by 11:59 p.m. Dec. 23 and Santa's sleigh will make it.");
  } else if (xmas.getTime() > n.getTime()) {
    document.write("<B>Too late for shipping, but not for an <A HREF=\"" + P + "help.html#giftcert\">eToyz gift certificate</A></B> -- print it out and tuck it in a stocking!");
  } else {
    document.write("<B>Happy holidays from all of us at eToyz!</B>");
  }
}
// arrives by Christmas with this shipping method?
function inTimeForXmas(method) {
  var cut = new Array(deadline(11, 20), deadline(11, 22), deadline(11, 23));
  return (new Date()).getTime() <= cut[method].getTime();
}

// ------------------------------------------------------------------ accounts
function pwHash(s) { var h = 5; for (var i = 0; i < s.length; i++) h = (h * 33 + s.charCodeAt(i)) % 1000081; return "" + h; }
function accounts() {
  var s = getCookie("etoyz_reg"), out = new Array();
  out[0] = new Array("demo@etoyz.com", "Holly Berry", pwHash("toybox"));
  if (s != "") { var a = s.split(";"); for (var i = 0; i < a.length; i++) out[out.length] = a[i].split("|"); }
  return out;
}
function findAccount(email) {
  var a = accounts(); email = email.toLowerCase();
  for (var i = 0; i < a.length; i++) if (a[i][0] == email) return a[i];
  return null;
}
function userGet() { var s = getCookie("etoyz_user"); return s == "" ? null : s.split("|"); }
function firstName() { var u = userGet(); return u ? u[0].split(" ")[0] : ""; }
function signOut() { delCookie("etoyz_user"); location.href = P + "index.html"; return false; }
function writeUserLinks() {
  var u = userGet();
  if (u) document.write("Hi, <B>" + esc(firstName()) + "</B>! <A HREF=\"" + P + "account.html\">my eToyz</A> | <A HREF=\"" + P + "index.html\" onClick=\"return signOut()\">sign out</A>");
  else document.write("<A HREF=\"" + P + "signin.html\">sign in</A> | <A HREF=\"" + P + "account.html\">my eToyz</A>");
}

// ------------------------------------------------------------------ cart
function cartGet() {
  var s = getCookie("etoyz_cart"), out = new Array();
  if (s == "") return out;
  var a = s.split(",");
  for (var i = 0; i < a.length; i++) { var p = a[i].split(":"); if (findToy(p[0]) && parseInt(p[1]) > 0) out[out.length] = new Array(p[0], parseInt(p[1])); }
  return out;
}
function cartSet(c) {
  var a = new Array();
  for (var i = 0; i < c.length; i++) if (c[i][1] > 0) a[a.length] = c[i][0] + ":" + c[i][1];
  setCookie("etoyz_cart", a.join(","), 30);
}
function cartCount() { var c = cartGet(), n = 0; for (var i = 0; i < c.length; i++) n += c[i][1]; return n; }
function cartTotal(c) { var t = 0; for (var i = 0; i < c.length; i++) t += findToy(c[i][0])[6] * c[i][1]; return t; }
function cartAdd(code, qty) {
  if (!qty || qty < 1) qty = 1;
  var c = cartGet(), found = false;
  for (var i = 0; i < c.length; i++) if (c[i][0] == code) { c[i][1] += qty; found = true; }
  if (!found) c[c.length] = new Array(code, qty);
  cartSet(c);
  location.href = P + "cart.html?added=" + code;
  return false;
}
function writeCartLine() {
  var n = cartCount();
  document.write("<A HREF=\"" + P + "cart.html\"><IMG SRC=\"" + P + "images/cart.gif\" WIDTH=24 HEIGHT=20 BORDER=0 ALIGN=ABSMIDDLE ALT=\"cart\"></A> <A HREF=\"" + P + "cart.html\">cart" + (n ? " (" + n + ")" : "") + "</A>");
}

// ------------------------------------------------------------------ wish lists, one per customer
function wishKey(email) { return "etoyz_wish_" + email.toLowerCase().replace(/[^a-z0-9]/g, "_"); }
function wishGet(email) {
  var s = getCookie(wishKey(email)), out = new Array();
  if (s == "") return out;
  var a = s.split(",");
  for (var i = 0; i < a.length; i++) if (findToy(a[i])) out[out.length] = a[i];
  return out;
}
function wishAdd(code) {
  var u = userGet();
  if (!u) {
    alert("Wish lists belong to somebody! Please sign in (or create an account) and we'll add it for you.");
    location.href = P + "signin.html?next=" + escape("wishlist.html?add=" + code);
    return false;
  }
  var w = wishGet(u[1]);
  for (var i = 0; i < w.length; i++) if (w[i] == code) { location.href = P + "wishlist.html?added=" + code; return false; }
  w[w.length] = code;
  setCookie(wishKey(u[1]), w.join(","), 365);
  location.href = P + "wishlist.html?added=" + code;
  return false;
}
function wishRemove(code) {
  var u = userGet(); if (!u) return false;
  var w = wishGet(u[1]), out = new Array();
  for (var i = 0; i < w.length; i++) if (w[i] != code) out[out.length] = w[i];
  setCookie(wishKey(u[1]), out.join(","), 365);
  location.href = P + "wishlist.html";
  return false;
}

// ------------------------------------------------------------------ orders
var SHIP = new Array(new Array("Standard (3-6 business days)", 495, 95), new Array("2nd Day Air", 995, 195), new Array("Overnight", 1595, 295));
function shipCost(m, n, sub) { if (m == 0 && sub >= 5000) return 0; return SHIP[m][1] + SHIP[m][2] * n; }
function ordersGet() {
  var s = getCookie("etoyz_orders"), out = new Array();
  if (s == "") return out;
  var a = s.split(";");
  for (var i = 0; i < a.length; i++) out[out.length] = a[i].split("~");
  return out;
}
function ordersSet(o) { var a = new Array(); for (var i = 0; i < o.length && i < 6; i++) a[a.length] = o[i].join("~"); setCookie("etoyz_orders", a.join(";"), 365); }

// ------------------------------------------------------------------ lists of toys
function toyRows(list, max) {
  var h = "<TABLE BORDER=0 CELLPADDING=4 CELLSPACING=0 WIDTH=\"100%\">";
  for (var i = 0; i < list.length && (!max || i < max); i++) {
    var t = list[i];
    h += "<TR BGCOLOR=\"" + (i % 2 ? "#FFFFED" : "#FFFFFF") + "\"><TD WIDTH=74><A HREF=\"" + toyURL(t) + "\"><IMG SRC=\"" + toyImg(t) + "\" WIDTH=70 HEIGHT=70 BORDER=0></A></TD>";
    h += "<TD><FONT FACE=\"Arial, Helvetica\" SIZE=2><A HREF=\"" + toyURL(t) + "\"><B>" + esc(t[1]) + "</B></A><BR>" + esc(t[2]) + " &middot; ages " + ageLabel(t) + "<BR>";
    h += "<FONT COLOR=\"#E21B1B\"><B>" + money(t[6]) + "</B></FONT> &nbsp; <A HREF=\"" + P + "cart.html\" onClick=\"return cartAdd('" + t[0] + "', 1)\">add to cart</A> | <A HREF=\"" + P + "wishlist.html\" onClick=\"return wishAdd('" + t[0] + "')\">wish list</A></FONT></TD></TR>";
  }
  return h + "</TABLE>";
}

var RING = new Array("yowza","altavisor","askreeves","orinoco","ubid","etoyz","petz","geohoods","hamstershuffle","dashdot","snapster","cnm");
function ringRandom() { location.href = P + "../" + RING[Math.floor(Math.random() * RING.length)] + "/index.html"; return false; }
