#!/usr/bin/env python3
"""Draws every Dashdot GIF with Pillow (all original artwork).

Run from the site folder:  python3 tools/gfx.py
"""
import os, math, shutil
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
OUT = os.path.join(SITE, "images")
WWW = os.path.dirname(os.path.dirname(SITE))
os.makedirs(OUT, exist_ok=True)

FONTDIRS = ["/usr/share/fonts/truetype/liberation", "/usr/share/fonts/truetype/dejavu",
            "/usr/share/fonts/truetype/freefont"]

def font(names, size):
    for n in names:
        for d in FONTDIRS:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()

SANS_B = ["LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf", "FreeSansBold.ttf"]
SANS = ["LiberationSans-Regular.ttf", "DejaVuSans.ttf", "FreeSans.ttf"]
SERIF_B = ["LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf", "FreeSerifBold.ttf"]
MONO_B = ["LiberationMono-Bold.ttf", "DejaVuSansMono-Bold.ttf", "FreeMonoBold.ttf"]

TEAL = (0, 102, 102)
DTEAL = (0, 60, 60)
GRAY = (204, 204, 204)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

S = 4  # supersampling factor

def canvas(w, h, bg=WHITE):
    im = Image.new("RGB", (w * S, h * S), bg)
    return im, ImageDraw.Draw(im)

def save(im, name, w=None, h=None, colors=64):
    if im.size[0] > 0 and w:
        im = im.resize((w, h), Image.LANCZOS)
    im = im.convert("P", palette=Image.ADAPTIVE, colors=colors)
    im.save(os.path.join(OUT, name))

def sc(*v):
    return [x * S for x in v]

# ---------------------------------------------------------------- logo
def logo():
    W, H = 300, 72
    im, d = canvas(W, H)
    # big morse "-." block on the left
    d.rounded_rectangle(sc(6, 26, 50, 42), radius=3 * S, fill=TEAL)
    d.ellipse(sc(58, 26, 74, 42), fill=TEAL)
    # shadow
    f = font(SANS_B, 46 * S)
    d.text((88 * S + 2 * S, 8 * S + 2 * S), "dashdot", font=f, fill=(150, 170, 170))
    d.text((88 * S, 8 * S), "dashdot", font=f, fill=BLACK)
    f2 = font(SANS_B, 11 * S)
    d.text((92 * S, 57 * S), "news for nerds.  stuff that matters.", font=f2, fill=TEAL)
    d.line(sc(4, 50, 80, 50), fill=DTEAL, width=2 * S)
    save(im, "title.gif", W, H)

def slc():
    # rounded corner that sits at the left of each teal story bar
    im = Image.new("RGB", (13 * S, 16 * S), WHITE)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 13 * S, 16 * S), fill=TEAL)
    d.pieslice((0, 0, 26 * S, 32 * S), 180, 270, fill=TEAL)
    im2 = Image.new("RGB", (13 * S, 16 * S), WHITE)
    d2 = ImageDraw.Draw(im2)
    d2.pieslice((0, 0, 26 * S, 32 * S), 180, 270, fill=TEAL)
    d2.rectangle((13 * S - 1, 0, 13 * S, 16 * S), fill=TEAL)
    d2.rectangle((0, 8 * S, 13 * S, 16 * S), fill=TEAL)
    save(im2, "slc.gif", 13, 16, colors=8)
    im3 = im2.transpose(Image.FLIP_LEFT_RIGHT)
    save(im3, "src.gif", 13, 16, colors=8)

def pixel():
    im = Image.new("P", (1, 1), 0)
    im.putpalette([255, 255, 255] + [0] * 765)
    im.save(os.path.join(OUT, "pix.gif"), transparency=0)

def bars():
    for name, col in [("bar.gif", TEAL), ("bar_mine.gif", (204, 102, 0))]:
        im = Image.new("RGB", (4, 12), col)
        d = ImageDraw.Draw(im)
        d.line((0, 0, 3, 0), fill=tuple(min(255, c + 70) for c in col))
        d.line((0, 11, 3, 11), fill=tuple(max(0, c - 40) for c in col))
        im.convert("P", palette=Image.ADAPTIVE, colors=8).save(os.path.join(OUT, name))

def banner():
    W, H = 468, 60
    im, d = canvas(W, H, (0, 0, 64))
    for i in range(H * S):
        c = int(40 + 60 * i / (H * S))
        d.line((0, i, W * S, i), fill=(0, 0, c))
    # a little server tower
    d.rectangle(sc(10, 8, 44, 54), fill=(190, 190, 190), outline=WHITE, width=S)
    for y in (14, 22, 30):
        d.rectangle(sc(14, y, 40, y + 5), fill=(90, 90, 90))
    d.ellipse(sc(34, 44, 39, 49), fill=(0, 220, 0))
    f = font(SANS_B, 20 * S)
    d.text(sc(56, 6), "KoldFusion 4.5", font=f, fill=(255, 204, 0))
    f2 = font(SANS_B, 11 * S)
    d.text(sc(56, 32), "Y2K-ready web applications. Now with 40% more <CF>.", font=f2, fill=WHITE)
    d.text(sc(56, 45), "Gibson Mainframe Co.", font=font(SANS, 10 * S), fill=(170, 200, 255))
    d.rounded_rectangle(sc(380, 18, 462, 42), radius=4 * S, fill=(255, 204, 0), outline=WHITE, width=S)
    d.text(sc(386, 23), "CLICK HERE", font=font(SANS_B, 11 * S), fill=BLACK)
    save(im, "banner_kf.gif", W, H, colors=128)

    im, d = canvas(W, H, (255, 255, 230))
    d.rectangle(sc(0, 0, W - 1, H - 1), outline=(0, 102, 0), width=2 * S)
    f = font(SERIF_B, 22 * S)
    d.text(sc(14, 6), "Orinoco.com", font=f, fill=(0, 51, 102))
    d.text(sc(16, 36), "Books, music, and now: one-click everything.", font=font(SANS, 12 * S), fill=BLACK)
    d.polygon(sc(400, 30, 440, 12, 440, 48), fill=(0, 102, 0))
    save(im, "banner_orinoco.gif", W, H, colors=64)

def shirt():
    W, H = 160, 150
    im, d = canvas(W, H)
    d.polygon(sc(40, 20, 65, 10, 95, 10, 120, 20, 150, 50, 128, 66, 118, 56, 118, 140, 42, 140, 42, 56, 32, 66, 10, 50),
              fill=(20, 20, 20))
    d.rounded_rectangle(sc(55, 60, 80, 70), radius=2 * S, fill=TEAL)
    d.ellipse(sc(86, 59, 98, 71), fill=TEAL)
    d.text(sc(52, 80), "dashdot", font=font(SANS_B, 16 * S), fill=WHITE)
    save(im, "shirt.gif", W, H)

# ---------------------------------------------------------------- topic icons
def icon(name, w, h, draw):
    im, d = canvas(w, h)
    draw(d, w, h)
    save(im, name, w, h)

def t_linix(d, w, h):  # terminal with prompt
    d.rounded_rectangle(sc(4, 6, 60, 50), radius=4 * S, fill=(80, 80, 80), outline=BLACK, width=S)
    d.rectangle(sc(9, 11, 55, 44), fill=BLACK)
    f = font(MONO_B, 11 * S)
    d.text(sc(11, 13), "$ make", font=f, fill=(0, 255, 0))
    d.text(sc(11, 27), "$ _", font=f, fill=(0, 255, 0))
    d.polygon(sc(20, 50, 44, 50, 50, 62, 14, 62), fill=(120, 120, 120))
    d.text(sc(8, 62), "LINIX", font=font(SANS_B, 9 * S), fill=TEAL)

def t_bsd(d, w, h):  # pitchfork
    d.line(sc(32, 20, 32, 66), fill=(150, 0, 0), width=4 * S)
    d.line(sc(16, 20, 48, 20), fill=(150, 0, 0), width=4 * S)
    for x in (16, 32, 48):
        d.polygon(sc(x - 5, 22, x, 3, x + 5, 22), fill=(200, 0, 0))
    d.text(sc(46, 50), "bsd", font=font(SANS_B, 10 * S), fill=(150, 0, 0))

def t_y2k(d, w, h):  # clock with bug
    d.ellipse(sc(4, 4, 60, 60), fill=(255, 255, 210), outline=BLACK, width=2 * S)
    for i in range(12):
        a = i * math.pi / 6
        d.line(sc(32 + 23 * math.sin(a), 32 - 23 * math.cos(a), 32 + 26 * math.sin(a), 32 - 26 * math.cos(a)), fill=BLACK, width=S)
    d.line(sc(32, 32, 32, 10), fill=BLACK, width=2 * S)
    d.line(sc(32, 32, 44, 32), fill=BLACK, width=2 * S)
    d.ellipse(sc(36, 38, 50, 52), fill=(200, 0, 0))
    for dx in (-3, 3):
        d.line(sc(43 + dx, 40, 43 + dx * 3, 34), fill=BLACK, width=S)
    d.text(sc(10, 62), "Y2K", font=font(SANS_B, 12 * S), fill=(200, 0, 0))

def t_hardware(d, w, h):  # chip
    d.rectangle(sc(14, 14, 50, 50), fill=(40, 40, 40))
    for i in range(6):
        p = 17 + i * 6
        d.rectangle(sc(p, 6, p + 2, 14), fill=(200, 200, 200))
        d.rectangle(sc(p, 50, p + 2, 58), fill=(200, 200, 200))
        d.rectangle(sc(6, p, 14, p + 2), fill=(200, 200, 200))
        d.rectangle(sc(50, p, 58, p + 2), fill=(200, 200, 200))
    d.text(sc(19, 25), "CPU", font=font(SANS_B, 11 * S), fill=(255, 220, 0))

def t_internet(d, w, h):  # globe
    d.ellipse(sc(6, 6, 58, 58), fill=(60, 120, 220), outline=DTEAL, width=S)
    d.polygon(sc(18, 16, 30, 12, 34, 22, 26, 32, 20, 28), fill=(40, 160, 60))
    d.polygon(sc(36, 30, 48, 28, 52, 40, 42, 50, 36, 42), fill=(40, 160, 60))
    d.arc(sc(6, 20, 58, 44), 0, 360, fill=WHITE, width=S)
    d.arc(sc(20, 6, 44, 58), 0, 360, fill=WHITE, width=S)
    d.line(sc(32, 6, 32, 58), fill=WHITE, width=S)

def t_science(d, w, h):  # atom
    for ang in (0, 60, 120):
        e = Image.new("L", (64 * S, 64 * S), 0)
        ed = ImageDraw.Draw(e)
        ed.ellipse(sc(4, 22, 60, 42), outline=255, width=2 * S)
        e = e.rotate(ang, resample=Image.BICUBIC)
        d.bitmap((0, 0), e, fill=(0, 0, 160))
    d.ellipse(sc(27, 27, 37, 37), fill=(220, 0, 0))

def t_space(d, w, h):  # rocket
    d.polygon(sc(32, 2, 42, 18, 42, 46, 22, 46, 22, 18), fill=(230, 230, 230), outline=BLACK)
    d.ellipse(sc(27, 18, 37, 28), fill=(80, 160, 255), outline=BLACK)
    d.polygon(sc(22, 34, 12, 50, 22, 46), fill=(200, 0, 0))
    d.polygon(sc(42, 34, 52, 50, 42, 46), fill=(200, 0, 0))
    d.polygon(sc(25, 46, 39, 46, 32, 62), fill=(255, 150, 0))
    for x, y in ((6, 8), (54, 12), (10, 30), (56, 34)):
        d.ellipse(sc(x, y, x + 2, y + 2), fill=(200, 200, 0))

def t_games(d, w, h):  # joystick
    d.rounded_rectangle(sc(8, 38, 56, 58), radius=4 * S, fill=(40, 40, 40))
    d.line(sc(32, 40, 32, 14), fill=(90, 90, 90), width=4 * S)
    d.ellipse(sc(24, 4, 40, 20), fill=(220, 0, 0))
    d.ellipse(sc(44, 42, 52, 50), fill=(255, 200, 0))

def t_patents(d, w, h):  # document with seal
    d.rectangle(sc(10, 4, 50, 58), fill=(255, 255, 235), outline=BLACK, width=S)
    for y in range(12, 40, 6):
        d.line(sc(15, y, 45, y), fill=(120, 120, 120), width=S)
    d.ellipse(sc(32, 40, 54, 62), fill=(200, 160, 0), outline=(120, 90, 0), width=S)
    d.text(sc(37, 45), "TM", font=font(SANS_B, 8 * S), fill=(90, 60, 0))

def t_privacy(d, w, h):  # eye
    d.chord(sc(4, 14, 60, 50), 180, 360, fill=WHITE, outline=BLACK, width=2 * S)
    d.chord(sc(4, 14, 60, 50), 0, 180, fill=WHITE, outline=BLACK, width=2 * S)
    d.ellipse(sc(20, 18, 44, 46), fill=(0, 110, 140))
    d.ellipse(sc(27, 25, 37, 39), fill=BLACK)
    d.ellipse(sc(29, 26, 32, 29), fill=WHITE)

def t_music(d, w, h):  # notes
    d.line(sc(24, 12, 24, 46), fill=BLACK, width=3 * S)
    d.line(sc(48, 6, 48, 40), fill=BLACK, width=3 * S)
    d.polygon(sc(24, 12, 48, 6, 48, 14, 24, 20), fill=BLACK)
    d.ellipse(sc(10, 40, 26, 52), fill=BLACK)
    d.ellipse(sc(34, 34, 50, 46), fill=BLACK)
    d.text(sc(6, 54), "MP3", font=font(SANS_B, 10 * S), fill=(160, 0, 160))

def t_money(d, w, h):  # chart going up with dollar
    d.rectangle(sc(4, 4, 60, 60), fill=(240, 255, 240), outline=(0, 100, 0), width=S)
    d.line(sc(8, 52, 20, 40, 30, 46, 44, 22, 56, 10), fill=(0, 140, 0), width=3 * S)
    d.text(sc(10, 6), "$", font=font(SANS_B, 22 * S), fill=(0, 100, 0))

def t_bug(d, w, h):  # beetle
    d.ellipse(sc(16, 14, 48, 58), fill=(30, 120, 30), outline=BLACK, width=S)
    d.line(sc(32, 16, 32, 58), fill=BLACK, width=S)
    d.ellipse(sc(24, 4, 40, 18), fill=BLACK)
    for y in (24, 36, 48):
        d.line(sc(16, y, 4, y - 4), fill=BLACK, width=2 * S)
        d.line(sc(48, y, 60, y - 4), fill=BLACK, width=2 * S)
    d.line(sc(28, 6, 22, 0), fill=BLACK, width=S)
    d.line(sc(36, 6, 42, 0), fill=BLACK, width=S)

def t_humor(d, w, h):  # grinning face
    d.ellipse(sc(4, 4, 60, 60), fill=(255, 220, 0), outline=BLACK, width=2 * S)
    d.ellipse(sc(18, 18, 26, 28), fill=BLACK)
    d.ellipse(sc(38, 18, 46, 28), fill=BLACK)
    d.chord(sc(14, 22, 50, 50), 0, 180, fill=WHITE, outline=BLACK, width=2 * S)

def t_books(d, w, h):  # open book
    d.polygon(sc(4, 14, 32, 20, 32, 56, 4, 50), fill=WHITE, outline=BLACK)
    d.polygon(sc(60, 14, 32, 20, 32, 56, 60, 50), fill=WHITE, outline=BLACK)
    for y in range(24, 48, 5):
        d.line(sc(8, y - 4, 28, y), fill=(130, 130, 130), width=S)
        d.line(sc(36, y, 56, y - 4), fill=(130, 130, 130), width=S)
    d.polygon(sc(2, 52, 32, 58, 62, 52, 62, 56, 32, 62, 2, 56), fill=(120, 40, 0))

def t_monolith(d, w, h):  # black slab with window panes
    d.polygon(sc(20, 4, 44, 4, 48, 60, 16, 60), fill=(25, 25, 25))
    d.line(sc(21, 5, 18, 59), fill=(120, 120, 120), width=S)
    d.text(sc(24, 20), "M", font=font(SERIF_B, 16 * S), fill=(200, 200, 200))
    d.line(sc(4, 61, 60, 61), fill=(90, 70, 40), width=2 * S)
    d.text(sc(48, 2), "$", font=font(SANS_B, 12 * S), fill=(0, 120, 0))

def t_security(d, w, h):  # padlock
    d.arc(sc(16, 4, 48, 40), 180, 360, fill=(120, 120, 120), width=5 * S)
    d.line(sc(18, 22, 18, 30), fill=(120, 120, 120), width=5 * S)
    d.line(sc(46, 22, 46, 30), fill=(120, 120, 120), width=5 * S)
    d.rounded_rectangle(sc(10, 28, 54, 60), radius=3 * S, fill=(220, 170, 0), outline=(120, 90, 0), width=S)
    d.ellipse(sc(28, 36, 36, 44), fill=BLACK)
    d.rectangle(sc(31, 42, 33, 52), fill=BLACK)

def t_handhelds(d, w, h):  # PDA
    d.rounded_rectangle(sc(14, 2, 50, 62), radius=5 * S, fill=(70, 70, 90), outline=BLACK, width=S)
    d.rectangle(sc(19, 8, 45, 38), fill=(170, 190, 150))
    d.text(sc(21, 10), "9:42", font=font(MONO_B, 8 * S), fill=BLACK)
    for x in (19, 27, 35, 43):
        d.ellipse(sc(x - 2, 46, x + 4, 52), fill=(180, 180, 200))
    d.line(sc(56, 4, 52, 60), fill=(180, 180, 180), width=2 * S)

def t_browsers(d, w, h):  # browser window with a lizard-ish compass
    d.rectangle(sc(2, 6, 62, 58), fill=WHITE, outline=BLACK, width=S)
    d.rectangle(sc(2, 6, 62, 14), fill=(0, 0, 128))
    d.rectangle(sc(54, 8, 60, 13), fill=GRAY)
    d.rectangle(sc(6, 18, 58, 24), fill=GRAY)
    d.ellipse(sc(20, 28, 44, 54), outline=(0, 100, 0), width=2 * S)
    d.polygon(sc(32, 30, 36, 41, 32, 52, 28, 41), fill=(200, 0, 0))

def t_news(d, w, h):  # newspaper
    d.rectangle(sc(6, 8, 58, 58), fill=WHITE, outline=BLACK, width=S)
    d.text(sc(10, 10), "NEWS", font=font(SERIF_B, 13 * S), fill=BLACK)
    d.line(sc(10, 26, 54, 26), fill=BLACK, width=S)
    d.rectangle(sc(10, 30, 28, 44), fill=(150, 150, 150))
    for y in range(30, 56, 4):
        d.line(sc(32, y, 54, y), fill=(120, 120, 120), width=S)
    for y in range(48, 56, 4):
        d.line(sc(10, y, 28, y), fill=(120, 120, 120), width=S)

ICONS = {
    "topiclinix.gif": (t_linix, 64, 72), "topicbsd.gif": (t_bsd, 64, 68), "topicy2k.gif": (t_y2k, 64, 76),
    "topichardware.gif": (t_hardware, 64, 64), "topicinternet.gif": (t_internet, 64, 64),
    "topicscience.gif": (t_science, 64, 64), "topicspace.gif": (t_space, 64, 64), "topicgames.gif": (t_games, 64, 62),
    "topicpatents.gif": (t_patents, 60, 64), "topicprivacy.gif": (t_privacy, 64, 64), "topicmusic.gif": (t_music, 60, 66),
    "topicmoney.gif": (t_money, 64, 64), "topicbug.gif": (t_bug, 64, 62), "topichumor.gif": (t_humor, 64, 64),
    "topicbooks.gif": (t_books, 64, 64), "topicmonolith.gif": (t_monolith, 64, 64),
    "topicsecurity.gif": (t_security, 64, 64), "topichandhelds.gif": (t_handhelds, 64, 64),
    "topicbrowsers.gif": (t_browsers, 64, 64), "topicnews.gif": (t_news, 64, 64),
}

def copy_stock():
    for n in ("powered_by_kf.gif", "new.gif", "construction.gif", "email.gif"):
        src = os.path.join(WWW, "images", n)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(OUT, n))

if __name__ == "__main__":
    logo(); slc(); pixel(); bars(); banner(); shirt()
    for n, (fn, w, h) in ICONS.items():
        icon(n, w, h, fn)
    copy_stock()
    print("wrote", len(os.listdir(OUT)), "images to", OUT)
