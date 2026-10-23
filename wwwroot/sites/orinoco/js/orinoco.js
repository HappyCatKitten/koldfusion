// Orinoco.com client-side shopping engine, JavaScript 1.2 style (works in Navigator 4 and IE 4).
// Cart, sign-in, 1-Click and orders live in cookies, exactly like a 1999 site with no budget for servers.
// Needs ITEMS from books.js and the page variable P (relative path to the site root).

// remember script errors (the flow test reads window.__e; visitors never see a thing)
function noteError(msg, url, line) { if (!window.__e) window.__e = new Array(); window.__e[window.__e.length] = msg + " @" + line; return false; }
window.onerror = noteError;

function getCookie(name) {
  var s = document.cookie, k = name + "=";
  var i = s.indexOf(k);
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
  var exp = "";
  if (days) {
    var d = new Date();
    d.setTime(d.getTime() + days * 86400000);
    exp = "; expires=" + d.toGMTString();
  }
  document.cookie = name + "=" + escape(val) + exp + "; path=/";
}
function delCookie(name) { setCookie(name, "", -1); }

function qs(name) {
  var q = location.search.substring(1).split("&");
  for (var i = 0; i < q.length; i++) {
    var p = q[i].split("=");
    if (p[0] == name) return unescape((p[1] || "").replace(/\+/g, " "));
  }
  return "";
}
function esc(s) {
  s = "" + s;
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function money(c) {
  c = Math.round(c);
  var d = Math.floor(c / 100), r = c % 100;
  var ds = "" + d, out = "";
  while (ds.length > 3) { out = "," + ds.substring(ds.length - 3) + out; ds = ds.substring(0, ds.length - 3); }
  return "$" + ds + out + "." + (r < 10 ? "0" : "") + r;
}

// ---- catalog lookups: ITEMS[i] = code, title, author, price, list, subject, binding, avail, kind
function findItem(code) {
  for (var i = 0; i < ITEMS.length; i++) if (ITEMS[i][0] == code) return ITEMS[i];
  return null;
}
function itemURL(it) { return P + "detail/" + it[0] + ".html"; }
function coverURL(it) { return P + "images/covers/" + it[0] + "_s.gif"; }

// ---- it is always 1999 on Orinoco.com
var MONTHS = new Array("January","February","March","April","May","June","July","August","September","October","November","December");
var DAYS = new Array("Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday");
function in1999(d) {
  var day = d.getDate();
  if (d.getMonth() == 1 && day == 29) day = 28;
  return new Date(1999, d.getMonth(), day, d.getHours(), d.getMinutes(), d.getSeconds());
}
function longDate(d) {
  var e = in1999(d);
  return DAYS[e.getDay()] + ", " + MONTHS[e.getMonth()] + " " + e.getDate() + ", 1999";
}
function shortDate(d) {
  var e = in1999(d);
  return (e.getMonth() + 1) + "/" + e.getDate() + "/99";
}

// ---- shopping cart: cookie "orinoco_cart" = code:qty,code:qty
function cartGet() {
  var s = getCookie("orinoco_cart"), out = new Array();
  if (s == "") return out;
  var a = s.split(",");
  for (var i = 0; i < a.length; i++) {
    var p = a[i].split(":");
    if (findItem(p[0]) && parseInt(p[1]) > 0) out[out.length] = new Array(p[0], parseInt(p[1]));
  }
  return out;
}
function cartSet(c) {
  var a = new Array();
  for (var i = 0; i < c.length; i++) if (c[i][1] > 0) a[a.length] = c[i][0] + ":" + c[i][1];
  setCookie("orinoco_cart", a.join(","), 30);
}
function cartCount() {
  var c = cartGet(), n = 0;
  for (var i = 0; i < c.length; i++) n += c[i][1];
  return n;
}
function cartAdd(code, qty) {
  var c = cartGet(), found = false;
  for (var i = 0; i < c.length; i++) if (c[i][0] == code) { c[i][1] += qty; found = true; }
  if (!found) c[c.length] = new Array(code, qty);
  cartSet(c);
  location.href = P + "cart.html?added=" + code;
  return false;
}
function cartTotal(c) {
  var t = 0;
  for (var i = 0; i < c.length; i++) t += findItem(c[i][0])[3] * c[i][1];
  return t;
}

// ---- customers: "orinoco_user" = name|email ; registered accounts "orinoco_reg" = email|name|pwhash;...
function pwHash(s) {
  var h = 7;
  for (var i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) % 1000003;
  return "" + h;
}
function userGet() {
  var s = getCookie("orinoco_user");
  if (s == "") return null;
  return s.split("|");
}
function firstName() {
  var u = userGet();
  if (!u) return "";
  return u[0].split(" ")[0];
}
function accounts() {
  var s = getCookie("orinoco_reg"), out = new Array();
  out[0] = new Array("demo@orinoco.com", "Della Ware", pwHash("river"));
  if (s != "") {
    var a = s.split(";");
    for (var i = 0; i < a.length; i++) out[out.length] = a[i].split("|");
  }
  return out;
}
function findAccount(email) {
  var a = accounts();
  email = email.toLowerCase();
  for (var i = 0; i < a.length; i++) if (a[i][0] == email) return a[i];
  return null;
}
function signOut() {
  delCookie("orinoco_user");
  location.href = P + "index.html";
  return false;
}
function writeHello() {
  var u = userGet();
  if (u) {
    document.write("Hello, <B>" + esc(firstName()) + "</B>! We have <A HREF=\"" + P + "account.html\">recommendations</A> for you. ");
    document.write("(If you're not " + esc(u[0]) + ", <A HREF=\"" + P + "signin.html\" onClick=\"return signOutTo('signin.html')\">click here</A>.)");
  } else {
    document.write("Hello! Every order at Orinoco.com is covered by our <A HREF=\"" + P + "help.html#safe\">Safe Shopping Pledge</A>. ");
    document.write("<BR>Been here before? <A HREF=\"" + P + "signin.html\">Sign in</A>.");
  }
}
function signOutTo(page) { delCookie("orinoco_user"); location.href = P + page; return false; }

// ---- shipping & orders
var SHIP = new Array(
  new Array("Standard Shipping (3-7 business days)", 295, 99),
  new Array("Second Day Air", 595, 199),
  new Array("Next Day Air", 995, 299));
function shipCost(method, n) { var s = SHIP[method]; return s[1] + s[2] * n; }
// address/payment profile: "orinoco_addr" = name|street|city|state|zip|country|shipmethod|cardtype|last4|giftwrap
function addrGet() {
  var s = getCookie("orinoco_addr");
  if (s == "") return null;
  return s.split("|");
}
function addrSet(a) { setCookie("orinoco_addr", a.join("|"), 365); }
function oneClickOn() { return getCookie("orinoco_1click") == "on"; }
// orders: "orinoco_orders" = no~time~code:qty,code:qty~ship~total~status;...  (newest first, at most 6)
function ordersGet() {
  var s = getCookie("orinoco_orders"), out = new Array();
  if (s == "") return out;
  var a = s.split(";");
  for (var i = 0; i < a.length; i++) out[out.length] = a[i].split("~");
  return out;
}
function ordersSet(o) {
  var a = new Array();
  for (var i = 0; i < o.length && i < 6; i++) a[a.length] = o[i].join("~");
  setCookie("orinoco_orders", a.join(";"), 365);
}
function placeOrder(cart, method) {
  var n = 0;
  for (var i = 0; i < cart.length; i++) n += cart[i][1];
  var sub = cartTotal(cart), ship = shipCost(method, n);
  var no = "002-" + (1000000 + Math.floor(Math.random() * 8999999)) + "-" + (1000000 + Math.floor(Math.random() * 8999999));
  var items = new Array();
  for (var i = 0; i < cart.length; i++) items[items.length] = cart[i][0] + ":" + cart[i][1];
  var o = ordersGet();
  o.splice(0, 0, new Array(no, "" + (new Date()).getTime(), items.join(","), "" + method, "" + (sub + ship), "Shipping soon"));
  ordersSet(o);
  return no;
}
function oneClick(code) {
  var u = userGet(), a = addrGet();
  if (!u) {
    alert("1-Click ordering is for signed-in customers. Please sign in first; we'll bring you right back.");
    location.href = P + "signin.html?next=detail/" + code + ".html";
    return false;
  }
  if (!a || !oneClickOn()) {
    alert("To use 1-Click, complete one regular order (so we know where to ship and how you pay), then switch 1-Click on in Your Account.");
    location.href = P + "account.html";
    return false;
  }
  var c = new Array(new Array(code, 1));
  var no = placeOrder(c, parseInt(a[6]));
  location.href = P + "thanks.html?order=" + no + "&oneclick=1";
  return false;
}

// ---- the little cart line in page headers
function writeCartLine() {
  var n = cartCount();
  if (n > 0) document.write("<A HREF=\"" + P + "cart.html\">" + n + " item" + (n == 1 ? "" : "s") + " in your cart</A>");
}

// ---- reviews you have written (cookie "orinoco_rev" = code^stars^title^text^name;...)
function myReviews(code) {
  var s = getCookie("orinoco_rev"), out = new Array();
  if (s == "") return out;
  var a = s.split(";");
  for (var i = 0; i < a.length; i++) {
    var r = a[i].split("^");
    if (!code || r[0] == code) out[out.length] = r;
  }
  return out;
}
function writeMyReviews(code) {
  var r = myReviews(code);
  for (var i = 0; i < r.length; i++) {
    var st = parseInt(r[i][1]);
    document.write("<P><IMG SRC=\"" + P + "images/stars/stars-" + st + "-0.gif\" WIDTH=64 HEIGHT=13 ALT=\"" + st + " out of 5 stars\"> <B>" + esc(r[i][2]) + "</B>, " + longDate(new Date()).substring(longDate(new Date()).indexOf(",") + 2) + "<BR>");
    document.write("<B>Reviewer:</B> " + esc(r[i][4]) + " <FONT COLOR=\"#CC0000\" SIZE=-2>(your review -- thank you!)</FONT><BR>");
    document.write(esc(r[i][3]) + "</P>");
  }
}

// ---- "Was this review helpful to you?"  (cookie "orinoco_votes" = reviewid:y|n,...)
function voteGet(id) {
  var s = "," + getCookie("orinoco_votes") + ",";
  if (s.indexOf("," + id + ":y,") != -1) return "y";
  if (s.indexOf("," + id + ":n,") != -1) return "n";
  return "";
}
function writeHelpful(id, yes, total) {
  var v = voteGet(id);
  if (v == "y") { yes++; total++; }
  if (v == "n") total++;
  if (total > 0) document.write("<FONT SIZE=-1>" + yes + " out of " + total + " people found the following review helpful:</FONT><BR>");
}
function vote(id, yn) {
  if (voteGet(id) != "") { alert("You have already voted on this review. Thanks!"); return false; }
  var s = getCookie("orinoco_votes");
  setCookie("orinoco_votes", (s == "" ? "" : s + ",") + id + ":" + yn, 365);
  alert("Thank you for your feedback! Your vote will be counted the next time this page is displayed.");
  location.reload();
  return false;
}

// ---- recently viewed (the "Your Recent History" box)
function noteViewed(code) {
  var s = getCookie("orinoco_seen"), a = (s == "" ? new Array() : s.split(",")), out = new Array(code);
  for (var i = 0; i < a.length && out.length < 4; i++) if (a[i] != code) out[out.length] = a[i];
  setCookie("orinoco_seen", out.join(","), 30);
}
function writeRecent() {
  var s = getCookie("orinoco_seen");
  if (s == "") { document.write("<FONT SIZE=-2>Items you look at will show up here, so you can find them again.</FONT>"); return; }
  var a = s.split(",");
  for (var i = 0; i < a.length; i++) {
    var it = findItem(a[i]);
    if (it) document.write("<FONT SIZE=-2>&#149; <A HREF=\"" + itemURL(it) + "\">" + esc(it[1]) + "</A></FONT><BR>");
  }
}

// ---- the web ring "Random" button
var RING = new Array("yowza","altavisor","askreeves","orinoco","ubid","etoyz","petz","geohoods","hamstershuffle","dashdot","snapster","cnm");
function ringRandom() {
  var n = Math.floor(Math.random() * RING.length);
  location.href = P + "../" + RING[n] + "/index.html";
  return false;
}

// ---- wish list: cookie "orinoco_wish" = code,code,...
function wishGet() {
  var s = getCookie("orinoco_wish"), out = new Array();
  if (s == "") return out;
  var a = s.split(",");
  for (var i = 0; i < a.length; i++) if (findItem(a[i])) out[out.length] = a[i];
  return out;
}
function wishAdd(code) {
  var w = wishGet();
  for (var i = 0; i < w.length; i++) if (w[i] == code) { location.href = P + "wishlist.html?added=" + code; return false; }
  w[w.length] = code;
  setCookie("orinoco_wish", w.join(","), 365);
  location.href = P + "wishlist.html?added=" + code;
  return false;
}
function wishRemove(code) {
  var w = wishGet(), out = new Array();
  for (var i = 0; i < w.length; i++) if (w[i] != code) out[out.length] = w[i];
  setCookie("orinoco_wish", out.join(","), 365);
  location.href = P + "wishlist.html";
  return false;
}
function checkoutStart() {
  if (cartCount() == 0) { alert("Your Shopping Cart is empty."); return false; }
  if (!userGet()) location.href = P + "signin.html?next=checkout.html";
  else location.href = P + "checkout.html";
  return false;
}
// the "stars" image for a whole number of stars
function starsImg(n) {
  return "<IMG SRC=\"" + P + "images/stars/stars-" + n + "-0.gif\" WIDTH=64 HEIGHT=13 ALT=\"" + n + " out of 5 stars\">";
}
