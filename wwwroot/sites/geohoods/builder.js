// builder.js - GeoHoods Build-a-Page and EZ Editor (JavaScript 1.2). Needs ghdata.js.
var tpl = new Array();
tpl[0] = new Array("starfield","Starfield (sci-fi, space, mystery)","stars_bg.gif","#000000","#FFFF00","#00FFFF","Arial, Helvetica","line_stars.gif","bullet_star.gif");
tpl[1] = new Array("kitty","Pastel Kitty (cute, pets, friends)","bg_hearts.gif","#FFE6F0","#993366","#CC0066","Comic Sans MS","line_hearts.gif","bullet_heart.gif");
tpl[2] = new Array("classic","Plain & Simple (classic gray)","","#C0C0C0","#000000","#0000FF","Times New Roman","","");
tpl[3] = new Array("flames","Flame On! (bands, cars, wrestling)","bg_border_flames.gif","#140000","#FFCC00","#FF6600","Arial, Helvetica","flames.gif","bullet_skull.gif");
tpl[4] = new Array("country","Country Kitchen (family, recipes)","bg_gingham.gif","#FFAAAA","#660000","#CC0000","Comic Sans MS","line_rope.gif","ball_red.gif");
tpl[5] = new Array("sports","Game Day (sports, teams)","bg_grass.gif","#289628","#FFFFFF","#FFFF00","Arial Black, Arial","rainbow_hr.gif","ball_green.gif");
tpl[6] = new Array("spooky","Dark & Spooky (poetry, goth)","bg_blood.gif","#000000","#CC0000","#999999","Times New Roman","line_barbed.gif","bullet_skull.gif");
tpl[7] = new Array("neon","Neon Party (teens, music)","","#000000","#FF00FF","#00FFFF","Comic Sans MS","rainbow_line.gif","bullet_star.gif");
tpl[8] = new Array("clouds","Blue Skies (travel, babies)","bg_clouds.gif","#78B4FF","#000080","#CC0000","Comic Sans MS","rainbow_line.gif","ball_blue.gif");
tpl[9] = new Array("geek","Green Screen (computers)","bg_binary.gif","#000000","#00FF00","#FFFFFF","Courier New","line_laser.gif","ball_green.gif");
var bgs = new Array("stars_bg.gif","bg_space.gif","bg_nebula.gif","bg_hearts.gif","bg_flowers.gif","bg_paws.gif","bg_glitter.gif","bg_clouds.gif","bg_parchment.gif","bg_marble.gif","bg_brick.gif","bg_camo.gif","bg_wood.gif","bg_grass.gif","bg_water.gif","bg_bubbles.gif","bg_snow.gif","bg_binary.gif","bg_leopard.gif","bg_denim.gif","bg_checker.gif","bg_gingham.gif","bg_concrete.gif","bg_blood.gif","bg_notebook.gif","bg_border_blue.gif","bg_border_purple.gif","bg_border_green.gif","bg_border_pink.gif","bg_border_flames.gif");
var clips = new Array("welcome.gif","dancing_baby.gif","kitten.gif","puppy.gif","hamster.gif","ufo.gif","alien.gif","skull_spin.gif","heart.gif","twinkle.gif","cd_spin.gif","notes.gif","football.gif","globe.gif","construction.gif","worker.gif","hot.gif","y2k_bomb.gif","pie.gif","chili.gif","train.gif","gear.gif","snowman.gif","pumpkin.gif","candle.gif","tower.gif","cool_face.gif","mp_voltwhisker.gif","mp_flintfox.gif","photo_me.gif","photo_me2.gif","photo_cat.gif","photo_dog.gif","photo_family.gif","photo_ufo.gif","photo_car.gif","photo_beach.gif");
var clipW = new Array(400,56,64,64,40,80,48,48,32,24,40,48,48,32,140,120,80,64,64,48,120,40,48,48,32,40,64,64,64,120,120,160,160,200,160,200,200);
var clipH = new Array(40,72,56,52,40,64,56,48,32,24,40,40,40,32,50,70,40,64,48,24,40,40,64,48,64,64,64,64,64,150,150,120,120,130,120,120,130);
var midis = new Array("anthem","chiptune","elevator","fight_song","heartthrob","hoedown","holiday","kitten_waltz","lovesong","lullaby","memorial","punk","ragtime","spooky","starfield","surf","techno","y2k_march");
var midiNames = new Array("Homesteader Anthem","Insert Coin","Lobby Bossa","Gridiron Fight Song","Heartthrob Ballad","Skillet Hoedown","Sleigh Bells on the Modem","Kitten Waltz","Sonnet for a Screen Name","Porch Light Lullaby","Over the Rainbow Fields","Three Chords and a Modem","Attic Rag","The Murk Theme","Starfield Drift","Boardwalk Stomp","Modem Rave","Countdown March");

function getParam(name) {
  var s = location.search.substring(1);
  var parts = s.split("&");
  for (var i = 0; i < parts.length; i++) {
    var kv = parts[i].split("=");
    if (kv[0] == name && kv.length > 1) return unescape(kv[1].replace(/\+/g, " "));
  }
  return "";
}
function esc(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function isTaken(hood, sub, num) {
  var a = hood + "/" + sub + "/" + num + "/";
  for (var i = 0; i < ghPages.length; i++) if (ghPages[i][0] == a) return true;
  return false;
}
function selVal(sel) { return sel.options[sel.selectedIndex].value; }
function fillHoods() {
  var f = document.forms["builder"];
  f.hood.options.length = 0;
  for (var i = 0; i < ghHoods.length; i++) f.hood.options[i] = new Option(ghHoods[i][0] + " - " + ghHoods[i][1], ghHoods[i][0]);
}
function hoodChanged() {
  var f = document.forms["builder"];
  var subs = ghHoods[f.hood.selectedIndex][2].split("|");
  f.suburb.options.length = 0;
  for (var i = 0; i < subs.length; i++) f.suburb.options[i] = new Option(subs[i], subs[i]);
}
function findVacant() {
  var f = document.forms["builder"];
  var n;
  do { n = 1000 + Math.floor(Math.random() * 9000); } while (isTaken(selVal(f.hood), selVal(f.suburb), n));
  f.num.value = n;
  window.status = "Address " + n + " is vacant!";
}
function checkAddr() {
  var f = document.forms["builder"];
  var n = parseInt(f.num.value, 10);
  if (isNaN(n) || n < 1000 || n > 9999) { alert("Addresses are numbers from 1000 to 9999."); return false; }
  if (isTaken(selVal(f.hood), selVal(f.suburb), n)) {
    alert("Sorry! " + selVal(f.hood) + "/" + selVal(f.suburb) + "/" + n + " is already taken. Try 'Find a vacant lot'.");
    return false;
  }
  return true;
}
function initBuilder() {
  var f = document.forms["builder"];
  fillHoods();
  var h = getParam("hood");
  for (var i = 0; i < ghHoods.length; i++) if (ghHoods[i][0] == h) f.hood.selectedIndex = i;
  hoodChanged();
  var s = getParam("suburb");
  for (var i = 0; i < f.suburb.options.length; i++) if (f.suburb.options[i].value == s) f.suburb.selectedIndex = i;
  var n = getParam("num");
  if (n != "") f.num.value = n; else findVacant();
  f.template.options.length = 0;
  for (var i = 0; i < tpl.length; i++) f.template.options[i] = new Option(tpl[i][1], tpl[i][0]);
  f.bg.options.length = 0;
  f.bg.options[0] = new Option("(use the template's background)", "");
  for (var i = 0; i < bgs.length; i++) f.bg.options[i + 1] = new Option(bgs[i], bgs[i]);
  f.clip.options.length = 0;
  f.clip.options[0] = new Option("(no picture)", "");
  for (var i = 0; i < clips.length; i++) f.clip.options[i + 1] = new Option(clips[i], i);
  f.midi.options.length = 0;
  f.midi.options[0] = new Option("(no music)", "");
  for (var i = 0; i < midis.length; i++) f.midi.options[i + 1] = new Option(midiNames[i], midis[i]);
  f.clip.selectedIndex = 2;
}
function bgChanged() {
  var f = document.forms["builder"];
  var b = selVal(f.bg);
  if (b == "") b = tpl[f.template.selectedIndex][2];
  document.images["bgprev"].src = b == "" ? "images/spacer.gif" : "images/" + b;
}
function clipChanged() {
  var f = document.forms["builder"];
  var c = selVal(f.clip);
  document.images["clipprev"].src = c == "" ? "images/spacer.gif" : "images/" + clips[c];
}
function counterDigits(style) {
  var s = "", n = "000001";
  for (var i = 0; i < n.length; i++)
    s += "<IMG SRC=\"../../../images/" + style + "_" + n.charAt(i) + ".gif\" WIDTH=" + (style == "digit" ? 15 : 14) + " HEIGHT=20>";
  return s;
}
function makeHTML() {
  var f = document.forms["builder"];
  var t = tpl[f.template.selectedIndex];
  var bg = selVal(f.bg); if (bg == "") bg = t[2];
  var text = f.textcolor.value != "" ? f.textcolor.value : t[4];
  var link = f.linkcolor.value != "" ? f.linkcolor.value : t[5];
  var face = selVal(f.face); if (face == "") face = t[6];
  var I = "../../../images/";
  var title = f.title.value == "" ? "My Home Page" : f.title.value;
  var h = "<HTML>\n<HEAD>\n<TITLE>" + esc(title) + "</TITLE>\n<META NAME=\"GENERATOR\" CONTENT=\"GeoHoods Build-a-Page 2.1\">\n</HEAD>\n";
  h += "<BODY BGCOLOR=\"" + t[3] + "\"" + (bg != "" ? " BACKGROUND=\"" + I + bg + "\"" : "") + " TEXT=\"" + text + "\" LINK=\"" + link + "\" VLINK=\"" + link + "\">\n";
  h += "<CENTER>\n<FONT FACE=\"" + face + "\">\n";
  if (selVal(f.midi) != "") h += "<BGSOUND SRC=\"../../../midi/" + selVal(f.midi) + ".mid\" LOOP=INFINITE>\n<EMBED SRC=\"../../../midi/" + selVal(f.midi) + ".mid\" AUTOSTART=\"true\" LOOP=\"true\" HIDDEN=\"true\">\n";
  if (f.marquee.checked && f.marqueetext.value != "") h += "<MARQUEE><B>" + esc(f.marqueetext.value) + "</B></MARQUEE>\n";
  h += "<H1>" + esc(f.headline.value == "" ? title : f.headline.value) + "</H1>\n";
  var c = selVal(f.clip);
  if (c != "") h += "<P><IMG SRC=\"" + I + clips[c] + "\" WIDTH=" + clipW[c] + " HEIGHT=" + clipH[c] + "></P>\n";
  if (t[7] != "") h += "<P><IMG SRC=\"" + I + t[7] + "\"></P>\n"; else h += "<HR>\n";
  var about = f.about.value.split("\n");
  for (var i = 0; i < about.length; i++) if (about[i] != "") h += "<P>" + about[i] + "</P>\n";
  var links = "";
  for (var i = 1; i <= 3; i++) {
    var ln = f.elements["linkname" + i].value, lu = f.elements["linkurl" + i].value;
    if (ln != "" && lu != "" && lu != "http://")
      links += (t[8] != "" ? "<IMG SRC=\"" + I + t[8] + "\"> " : "<LI>") + "<A HREF=\"" + esc(lu) + "\">" + esc(ln) + "</A><BR>\n";
  }
  if (links != "") h += "<H2>My Favorite Links</H2>\n" + (t[8] == "" ? "<UL>\n" + links + "</UL>\n" : "<P>" + links + "</P>\n");
  if (t[7] != "") h += "<P><IMG SRC=\"" + I + t[7] + "\"></P>\n";
  if (f.email.value != "") h += "<P><A HREF=\"mailto:" + esc(f.email.value) + "\"><IMG SRC=\"" + I + "mailme.gif\" WIDTH=100 HEIGHT=30 BORDER=0></A></P>\n";
  if (f.guestbook.checked) h += "<P><A HREF=\"guestbook.html\"><IMG SRC=\"" + I + "sign_gb.gif\" WIDTH=120 HEIGHT=44 BORDER=0></A></P>\n";
  if (selVal(f.counter) != "") h += "<P>You are visitor number " + counterDigits(selVal(f.counter)) + "</P>\n";
  if (f.construction.checked) h += "<P><IMG SRC=\"" + I + "construction.gif\" WIDTH=140 HEIGHT=50></P>\n";
  h += "<P><FONT SIZE=1>Page built with GeoHoods Build-a-Page. Last updated: " + (new Date()).toLocaleString() + "</FONT></P>\n";
  h += "</FONT>\n</CENTER>\n";
  h += "<P><CENTER><TABLE BORDER=1 CELLPADDING=3 CELLSPACING=0 BGCOLOR=\"#FFFFCC\"><TR><TD><A HREF=\"../../../index.html\"><IMG SRC=\"" + I + "gh_88x31.gif\" WIDTH=88 HEIGHT=31 BORDER=0></A></TD>";
  h += "<TD ALIGN=CENTER><FONT FACE=\"Arial\" SIZE=1 COLOR=\"#000000\"><B><A HREF=\"../../../index.html\">GeoHoods</A></B> | <A HREF=\"../../index.html\">" + selVal(f.hood) + "</A> | <A HREF=\"../index.html\">" + selVal(f.suburb) + "</A><BR><A HREF=\"../../../join.html\">Get your own Free Home Page</A></FONT></TD></TR></TABLE></CENTER></P>\n";
  h += "</BODY>\n</HTML>\n";
  return h;
}
function siteBase() {
  var u = location.href;
  if (u.indexOf("?") >= 0) u = u.substring(0, u.indexOf("?"));
  if (u.indexOf("#") >= 0) u = u.substring(0, u.indexOf("#"));
  return u.substring(0, u.lastIndexOf("/") + 1);
}
function writePreview(html, addr) {
  var w = window.open("", "ghpreview", "width=700,height=500,scrollbars=yes,resizable=yes,toolbar=no");
  if (!w) { alert("Your pop-up blocker ate the preview window! Use 'Show me the HTML' instead."); return; }
  var base = "<BASE HREF=\"" + siteBase() + addr + "\">";
  w.document.open();
  w.document.write(html.replace("<HEAD>", "<HEAD>\n" + base));
  w.document.close();
  w.focus();
}
function addrOf() {
  var f = document.forms["builder"];
  return selVal(f.hood) + "/" + selVal(f.suburb) + "/" + f.num.value + "/";
}
function previewPage() {
  if (!checkAddr()) return;
  writePreview(makeHTML(), addrOf());
}
function showSource() {
  document.forms["builder"].source.value = makeHTML();
  location.hash = "source";
}
function moveIn() {
  var f = document.forms["builder"];
  if (f.member.value == "") { alert("Please choose a member name."); f.member.focus(); return; }
  if (f.title.value == "") { alert("Please give your page a title."); f.title.focus(); return; }
  if (!checkAddr()) return;
  f.source.value = makeHTML();
  location.href = "movedin.html?addr=" + escape(addrOf()) + "&member=" + escape(f.member.value);
}

