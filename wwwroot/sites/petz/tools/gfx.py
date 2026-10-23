#!/usr/bin/env python3
"""Pillow graphics for Petz.com (1999 Web parody). All artwork is original.

Run from the site folder:  python3 tools/gfx.py
Writes every GIF into images/ and the MIDI jingle (via tools/midi.py).
"""
import os, sys, math, random, shutil
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
OUT = os.path.join(SITE, "images")
sys.path.insert(0, HERE)
import data  # noqa: E402

SS = 3  # supersampling factor

GREEN = (153, 204, 51)      # #99CC33 header band
DKGREEN = (51, 102, 0)
PALE = (255, 255, 204)      # #FFFFCC left column
TAN = (204, 204, 153)       # #CCCC99 search box
RED = (255, 0, 51)          # #FF0033
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 204, 0)

FONTDIR = "/usr/share/fonts/truetype/liberation/"
_fc = {}
def font(size, style=""):
    name = {"": "LiberationSans-Regular.ttf", "b": "LiberationSans-Bold.ttf",
            "i": "LiberationSans-Italic.ttf", "bi": "LiberationSans-BoldItalic.ttf",
            "serifbi": "LiberationSerif-BoldItalic.ttf", "serifb": "LiberationSerif-Bold.ttf",
            "mono": "LiberationMono-Bold.ttf", "narrow": "LiberationSansNarrow-Bold.ttf"}[style]
    key = (name, int(size))
    if key not in _fc:
        _fc[key] = ImageFont.truetype(FONTDIR + name, max(1, int(size)))
    return _fc[key]


class Pen(object):
    """Draws in logical coordinates; scales by S (supersampling) * k (local zoom) plus offset."""
    def __init__(self, img, S=SS, ox=0, oy=0, k=1.0):
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.S, self.ox, self.oy, self.k = S, ox, oy, k

    def sub(self, ox, oy, k):
        return Pen(self.img, self.S, self.ox + ox * self.k, self.oy + oy * self.k, self.k * k)

    def P(self, x, y):
        return ((self.ox + x * self.k) * self.S, (self.oy + y * self.k) * self.S)

    def W(self, w):
        return max(1, int(round(w * self.k * self.S)))

    def box(self, x0, y0, x1, y1):
        a = self.P(x0, y0); b = self.P(x1, y1)
        return [min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])]

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.d.rectangle(self.box(x0, y0, x1, y1), fill=fill, outline=outline, width=self.W(width) if outline else 0)

    def rrect(self, x0, y0, x1, y1, r, fill=None, outline=None, width=1):
        self.d.rounded_rectangle(self.box(x0, y0, x1, y1), radius=r * self.k * self.S, fill=fill,
                                 outline=outline, width=self.W(width) if outline else 0)

    def ell(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.d.ellipse(self.box(x0, y0, x1, y1), fill=fill, outline=outline, width=self.W(width) if outline else 0)

    def circ(self, cx, cy, r, fill=None, outline=None, width=1):
        self.ell(cx - r, cy - r, cx + r, cy + r, fill, outline, width)

    def poly(self, pts, fill=None, outline=None, width=1):
        self.d.polygon([self.P(x, y) for x, y in pts], fill=fill, outline=outline,
                       width=self.W(width) if outline else 0)

    def line(self, pts, fill=BLACK, width=1, joint="curve"):
        self.d.line([self.P(x, y) for x, y in pts], fill=fill, width=self.W(width), joint=joint)

    def arc(self, x0, y0, x1, y1, a0, a1, fill=BLACK, width=1):
        self.d.arc(self.box(x0, y0, x1, y1), a0, a1, fill=fill, width=self.W(width))

    def pie(self, x0, y0, x1, y1, a0, a1, fill=None, outline=None):
        self.d.pieslice(self.box(x0, y0, x1, y1), a0, a1, fill=fill, outline=outline)

    def chord(self, x0, y0, x1, y1, a0, a1, fill=None, outline=None, width=1):
        self.d.chord(self.box(x0, y0, x1, y1), a0, a1, fill=fill, outline=outline,
                     width=self.W(width) if outline else 0)

    def font(self, size, style=""):
        return font(size * self.k * self.S, style)

    def text(self, x, y, s, size, fill=BLACK, style="b", anchor="la", stroke=0, stroke_fill=None):
        self.d.text(self.P(x, y), s, font=self.font(size, style), fill=fill, anchor=anchor,
                    stroke_width=int(round(stroke * self.k * self.S)), stroke_fill=stroke_fill)

    def tw(self, s, size, style="b"):
        f = self.font(size, style)
        b = f.getbbox(s)
        return (b[2] - b[0]) / float(self.S * self.k)

    def fit(self, s, size, maxw, style="b"):
        while size > 5 and self.tw(s, size, style) > maxw:
            size -= 0.5
        return size


def canvas(w, h, bg=WHITE):
    img = Image.new("RGB", (w * SS, h * SS), bg)
    return img, Pen(img)


def save(img, name, w=None, h=None, colors=255):
    if w is None:
        w, h = img.size[0] // SS, img.size[1] // SS
    if img.size != (w, h):
        img = img.resize((w, h), Image.LANCZOS)
    img = img.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    img.save(os.path.join(OUT, name), optimize=True)
    return img


# ===================================================================== MASCOT
SOCK = (126, 172, 226)
SOCK_DK = (40, 64, 140)
SOCK_MID = (90, 130, 200)
FELT = (150, 92, 50)
MOUTH = (150, 10, 30)

def argyle_img(h, mood="happy", flip=False, hat=None, extras=None):
    """Return an RGBA image (h px tall, 0.75h wide) of Argyle the Sock Dog facing right.
    Unit box is 120 x 160. mood: happy | sing | sad | wink."""
    k = h / 160.0
    w = int(round(120 * k))
    pat = Image.new("RGBA", (w, h), SOCK + (255,))
    pp = Pen(pat, 1, 0, 0, k)
    # argyle diamonds
    dw, dh = 22, 30
    for row in range(-1, 8):
        for col in range(-1, 7):
            cx = col * dw + (dw / 2.0 if row % 2 else 0)
            cy = row * dh / 2.0
            c = SOCK_DK if (row + col) % 2 == 0 else SOCK_MID
            pp.poly([(cx, cy - dh / 2.0), (cx + dw / 2.0, cy), (cx, cy + dh / 2.0), (cx - dw / 2.0, cy)], fill=c)
    for i in range(-10, 14):  # thin yellow overcheck lines
        x = i * dw
        pp.line([(x, 0), (x + 120, 160 * 1.36)], fill=(250, 220, 90), width=1.2)
        pp.line([(x + 120, 0), (x, 160 * 1.36)], fill=(250, 220, 90), width=1.2)
    # cuff (ribbed), drawn over pattern
    pp.rect(0, 140, 120, 160, fill=(230, 236, 246))
    for x in range(22, 80, 4):
        pp.line([(x, 140), (x, 160)], fill=(190, 200, 220), width=1)
    mask = Image.new("L", (w, h), 0)
    mp = Pen(mask, 1, 0, 0, k)
    mp.rrect(24, 70, 78, 175, 12, fill=255)          # arm tube
    mp.ell(8, 16, 100, 94, fill=255)                 # head
    mp.ell(48, 32, 119, 84, fill=255)                # snout
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.paste(pat, (0, 0), mask)
    p = Pen(img, 1, 0, 0, k)
    # outline
    edge = (30, 40, 90)
    p.arc(8, 16, 100, 94, 120, 330, fill=edge, width=1.4)
    p.arc(48, 32, 119, 84, 280, 60, fill=edge, width=1.4)
    p.line([(24, 80), (24, 160)], fill=edge, width=1.4)
    p.line([(78, 88), (78, 160)], fill=edge, width=1.4)
    # ears (felt), flopping back
    p.poly([(26, 24), (50, 16), (44, 46), (30, 74), (14, 66), (12, 44)], fill=FELT, outline=(90, 50, 20), width=1.5)
    p.line([(36, 26), (28, 62)], fill=(110, 66, 30), width=1)
    # mouth
    if mood in ("sing",):
        p.poly([(62, 66), (118, 50), (119, 60), (112, 86), (96, 90), (70, 78)], fill=MOUTH)
        p.ell(80, 74, 106, 90, fill=(255, 110, 140))
        lips = [[(62, 66), (118, 50)], [(70, 78), (96, 90), (112, 86)]]
    elif mood == "sad":
        p.poly([(64, 74), (100, 76), (116, 72), (100, 79), (66, 77)], fill=MOUTH)
        lips = [[(64, 74), (100, 76), (116, 72)]]
    else:
        p.poly([(62, 66), (117, 60), (114, 74), (98, 80), (72, 74)], fill=MOUTH)
        p.ell(86, 70, 104, 79, fill=(255, 110, 140))
        lips = [[(62, 66), (117, 60)], [(72, 74), (98, 80), (114, 74)]]
    for seg in lips:  # white running stitch
        for (x0, y0), (x1, y1) in zip(seg, seg[1:]):
            n = int(math.hypot(x1 - x0, y1 - y0) / 6)
            for i in range(n):
                a = i / float(n); b = (i + 0.5) / float(n)
                p.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a - 1.5),
                        (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b - 1.5)], fill=WHITE, width=1.3)
    # nose pompom
    p.circ(112, 44, 9, fill=(20, 20, 20))
    p.circ(109, 41, 3, fill=(110, 110, 110))
    # button eyes
    def button(cx, cy, r, col):
        p.circ(cx, cy, r, fill=col, outline=(20, 20, 20), width=1)
        p.circ(cx, cy, r * 0.65, outline=tuple(max(0, c - 60) for c in col), width=0.8)
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            p.circ(cx + dx * r * 0.28, cy + dy * r * 0.28, r * 0.14, fill=(20, 20, 20))
        p.line([(cx - r * 0.28, cy - r * 0.28), (cx + r * 0.28, cy + r * 0.28)], fill=(240, 240, 240), width=0.8)
        p.line([(cx + r * 0.28, cy - r * 0.28), (cx - r * 0.28, cy + r * 0.28)], fill=(240, 240, 240), width=0.8)
    if mood == "sad":
        button(70, 40, 8, (40, 160, 70)); button(88, 37, 7, (220, 40, 40))
        p.line([(62, 28), (76, 32)], fill=(20, 20, 60), width=1.5)   # worried brows
        p.line([(84, 28), (96, 25)], fill=(20, 20, 60), width=1.5)
    elif mood == "wink":
        button(70, 38, 8, (40, 160, 70))
        p.arc(82, 30, 96, 40, 200, 340, fill=(20, 20, 20), width=2)
    else:
        button(70, 38, 8, (40, 160, 70)); button(88, 34, 7, (220, 40, 40))
    # twist-tie bow tie
    p.poly([(38, 96), (52, 102), (38, 110)], fill=RED, outline=(120, 0, 0), width=1)
    p.poly([(66, 96), (52, 102), (66, 110)], fill=RED, outline=(120, 0, 0), width=1)
    p.circ(52, 102, 3.5, fill=(200, 0, 0))
    if hat == "santa":
        p.poly([(22, 30), (66, 14), (40, -2), (10, 4)], fill=(220, 0, 0))
        p.circ(8, 4, 6, fill=WHITE)
        p.rrect(16, 22, 70, 32, 5, fill=WHITE)
    if hat == "party":
        p.poly([(40, 22), (64, 18), (46, -6)], fill=(255, 0, 153), outline=(150, 0, 90))
        p.circ(46, -6, 3, fill=YELLOW)
    if flip:
        img = ImageOps.mirror(img)
    return img


def paste_argyle(base, x, y, h, **kw):
    """Paste Argyle onto a supersampled canvas at logical x,y with logical height h."""
    a = argyle_img(int(h * SS), **kw)
    base.paste(a, (int(x * SS), int(y * SS)), a)
    return a


# ===================================================================== ANIMALS (unit box 100x100)
def animal(p, kind, col=None):
    if kind == "dog":
        c = col or (204, 153, 102)
        p.ell(14, 30, 34, 78, fill=(120, 72, 36))            # ears
        p.ell(66, 30, 86, 78, fill=(120, 72, 36))
        p.ell(22, 18, 78, 78, fill=c, outline=BLACK, width=2)
        p.ell(34, 50, 66, 86, fill=(240, 220, 190), outline=BLACK, width=2)
        p.ell(43, 52, 57, 62, fill=BLACK)
        p.circ(38, 42, 4, fill=BLACK); p.circ(62, 42, 4, fill=BLACK)
        p.ell(46, 74, 56, 90, fill=(255, 100, 120), outline=BLACK, width=1.5)
        p.line([(50, 62), (50, 72)], width=2)
    elif kind == "cat":
        c = col or (255, 153, 51)
        p.poly([(20, 40), (26, 8), (46, 26)], fill=c, outline=BLACK, width=2)
        p.poly([(80, 40), (74, 8), (54, 26)], fill=c, outline=BLACK, width=2)
        p.ell(16, 20, 84, 84, fill=c, outline=BLACK, width=2)
        p.ell(30, 40, 44, 54, fill=(120, 200, 60)); p.ell(56, 40, 70, 54, fill=(120, 200, 60))
        p.ell(35, 41, 39, 53, fill=BLACK); p.ell(61, 41, 65, 53, fill=BLACK)
        p.poly([(45, 60), (55, 60), (50, 66)], fill=(255, 120, 150))
        p.line([(50, 66), (44, 72)], width=1.5); p.line([(50, 66), (56, 72)], width=1.5)
        for dy in (-3, 3):
            p.line([(40, 64 + dy), (6, 60 + dy * 2)], width=1); p.line([(60, 64 + dy), (94, 60 + dy * 2)], width=1)
    elif kind == "fish":
        c = col or (255, 140, 0)
        p.poly([(70, 50), (96, 26), (92, 50), (96, 74)], fill=c, outline=BLACK, width=2)
        p.poly([(40, 30), (60, 14), (62, 34)], fill=c, outline=BLACK, width=2)
        p.ell(6, 26, 78, 74, fill=c, outline=BLACK, width=2)
        p.circ(24, 44, 6, fill=WHITE, outline=BLACK); p.circ(23, 44, 3, fill=BLACK)
        p.arc(36, 32, 56, 68, 300, 60, fill=BLACK, width=1.5)
        p.arc(8, 52, 22, 62, 0, 120, fill=BLACK, width=1.5)
    elif kind == "bird":
        c = col or (51, 204, 255)
        p.poly([(30, 70), (6, 96), (22, 96), (40, 76)], fill=(0, 120, 200), outline=BLACK, width=1.5)
        p.ell(20, 36, 76, 88, fill=c, outline=BLACK, width=2)
        p.ell(46, 12, 86, 50, fill=(255, 235, 60), outline=BLACK, width=2)
        p.poly([(84, 28), (98, 36), (82, 40)], fill=(255, 140, 0), outline=BLACK, width=1.5)
        p.circ(70, 28, 4, fill=BLACK)
        p.ell(28, 50, 62, 76, fill=(0, 150, 220), outline=BLACK, width=1.5)
        p.line([(42, 88), (40, 98)], width=2); p.line([(54, 88), (56, 98)], width=2)
    elif kind == "ferret":
        c = col or (230, 210, 170)
        p.poly([(10, 66), (2, 82), (6, 84), (22, 72)], fill=(150, 110, 70), outline=BLACK, width=1.5)
        p.ell(8, 50, 74, 80, fill=c, outline=BLACK, width=2)
        p.ell(58, 30, 96, 66, fill=c, outline=BLACK, width=2)
        p.circ(64, 32, 6, fill=c, outline=BLACK, width=1.5); p.circ(86, 32, 6, fill=c, outline=BLACK, width=1.5)
        p.ell(62, 40, 94, 52, fill=(90, 60, 40))         # bandit mask
        p.circ(70, 46, 3, fill=BLACK); p.circ(86, 46, 3, fill=BLACK)
        p.circ(94, 56, 3, fill=(255, 120, 150))
        for x in (20, 34, 50, 60):
            p.line([(x, 76), (x, 90)], width=3)
    elif kind == "lizard":
        c = col or (60, 170, 60)
        p.line([(30, 60), (18, 70), (8, 88), (16, 96), (30, 92)], fill=c, width=7)
        p.ell(24, 46, 74, 70, fill=c, outline=BLACK, width=2)
        p.ell(64, 40, 96, 62, fill=c, outline=BLACK, width=2)
        p.circ(84, 48, 3.5, fill=WHITE, outline=BLACK); p.circ(85, 48, 1.8, fill=BLACK)
        for x0, x1 in ((34, 26), (62, 70)):
            p.line([(x0, 66), (x1, 82)], fill=c, width=5)
        p.line([(46, 48), (52, 44), (58, 48)], fill=(0, 100, 0), width=1.5)
        p.line([(94, 54), (100, 52), (98, 56)], fill=(255, 60, 90), width=1)
    elif kind == "hamster":
        c = col or (230, 170, 90)
        p.circ(30, 26, 9, fill=c, outline=BLACK, width=2); p.circ(70, 26, 9, fill=c, outline=BLACK, width=2)
        p.circ(30, 26, 4, fill=(255, 160, 170)); p.circ(70, 26, 4, fill=(255, 160, 170))
        p.ell(12, 22, 88, 92, fill=c, outline=BLACK, width=2)
        p.ell(30, 50, 70, 92, fill=(255, 245, 225))
        p.circ(38, 46, 4, fill=BLACK); p.circ(62, 46, 4, fill=BLACK)
        p.circ(50, 56, 3, fill=(255, 100, 130))
        p.ell(18, 52, 34, 64, fill=(255, 190, 190)); p.ell(66, 52, 82, 64, fill=(255, 190, 190))
    elif kind == "basset":
        c = (200, 140, 80)
        p.ell(6, 30, 30, 96, fill=(110, 60, 30), outline=BLACK, width=2)
        p.ell(70, 30, 94, 96, fill=(110, 60, 30), outline=BLACK, width=2)
        p.ell(22, 10, 78, 80, fill=c, outline=BLACK, width=2)
        p.ell(30, 50, 70, 92, fill=WHITE, outline=BLACK, width=2)
        p.ell(42, 52, 58, 64, fill=BLACK)
        p.ell(32, 34, 44, 44, fill=WHITE); p.circ(38, 41, 3, fill=BLACK)
        p.ell(56, 34, 68, 44, fill=WHITE); p.circ(62, 41, 3, fill=BLACK)
        p.arc(30, 30, 46, 40, 200, 340, fill=(120, 60, 20), width=2)
        p.arc(54, 30, 70, 40, 200, 340, fill=(120, 60, 20), width=2)


# ===================================================================== HEADER PIECES
def spacer():
    im = Image.new("P", (1, 1), 0)
    im.putpalette([255, 255, 255] + [0, 0, 0] * 255)
    im.save(os.path.join(OUT, "dot_clear.gif"), transparency=0)


def spine():
    im = Image.new("RGB", (1600, 8), WHITE)
    ImageDraw.Draw(im).rectangle([0, 0, 169, 7], fill=PALE)
    save(im, "spine.gif", 1600, 8)


def logo():
    W, H = 230, 66
    img, p = canvas(W, H, GREEN)
    paste_argyle(img, 2, 2, 62, mood="happy")
    p.text(52, 3, "petz", 38, fill=WHITE, style="serifbi", stroke=1.6, stroke_fill=(30, 60, 0))
    p.text(52 + p.tw("petz", 38, "serifbi") + 4, 14, ".com", 22, fill=YELLOW, style="serifbi",
           stroke=1.2, stroke_fill=(30, 60, 0))
    p.text(56, 47, "Because pets can't drive!", 11, fill=BLACK, style="bi")
    save(img, "logo.gif")


TAB_W = [("dogs", 55), ("cats", 52), ("fish", 50), ("birds", 60), ("ferrets", 66), ("reptiles", 69),
         ("smallpets", 87)]
TAB_LABEL = {"dogs": "dogs", "cats": "cats", "fish": "fish", "birds": "birds", "ferrets": "ferrets",
             "reptiles": "reptiles", "smallpets": "small pets"}
TAB_ANIMAL = {"dogs": "dog", "cats": "cat", "fish": "fish", "birds": "bird", "ferrets": "ferret",
              "reptiles": "lizard", "smallpets": "hamster"}

def tabs():
    for cat, w in TAB_W:
        for on in (False, True):
            img, p = canvas(w, 60, GREEN)
            fill = WHITE if on else (204, 238, 136)
            p.rrect(1, 6, w - 2, 70, 9, fill=fill, outline=DKGREEN, width=1)
            asz = 34
            a = p.sub((w - asz) / 2.0, 9, asz / 100.0)
            animal(a, TAB_ANIMAL[cat])
            lab = TAB_LABEL[cat]
            sz = p.fit(lab, 11, w - 6)
            p.text(w / 2.0, 46, lab, sz, fill=RED if on else (30, 70, 0), style="b", anchor="mt")
            save(img, "tab_%s%s.gif" % (cat, "_on" if on else ""))
    for on in (False, True):
        img, p = canvas(59, 20, GREEN)
        p.rrect(1, 1, 57, 26, 6, fill=WHITE if on else (204, 238, 136), outline=DKGREEN)
        p.poly([(8, 11), (14, 5), (20, 11)], fill=RED if on else DKGREEN)
        p.rect(10, 11, 18, 17, fill=RED if on else DKGREEN)
        p.text(37, 10, "home", 11, fill=RED if on else (30, 70, 0), anchor="mm")
        save(img, "tab_home%s.gif" % ("_on" if on else ""))


def header_buttons():
    for name, label, icon in (("btn_cart", "shopping cart", "cart"), ("btn_account", "my account", "key"),
                              ("btn_help", "help", "q")):
        img, p = canvas(86, 20, GREEN)
        p.rrect(0, 1, 85, 18, 8, fill=(255, 255, 255), outline=DKGREEN)
        p.circ(10, 10, 7, fill=YELLOW, outline=DKGREEN)
        if icon == "cart":
            p.line([(5, 7), (7, 7), (9, 12), (14, 12), (15, 8), (8, 8)], width=1)
            p.circ(10, 14, 1, fill=BLACK); p.circ(13, 14, 1, fill=BLACK)
        elif icon == "key":
            p.circ(8, 10, 2.5, outline=BLACK, width=1); p.line([(10, 10), (15, 10), (15, 12)], width=1)
        else:
            p.text(10, 10.5, "?", 10, anchor="mm")
        sz = p.fit(label, 10, 64)
        p.text(51, 10, label, sz, fill=(30, 70, 0), anchor="mm")
        save(img, name + ".gif")


def arrows():
    for name, col, up in (("up_arrow.gif", (51, 255, 51), True), ("down_arrow.gif", (255, 40, 40), False)):
        img, p = canvas(11, 11, BLACK)
        if up:
            p.poly([(5.5, 1), (10, 7), (7, 7), (7, 10), (4, 10), (4, 7), (1, 7)], fill=col)
        else:
            p.poly([(5.5, 10), (10, 4), (7, 4), (7, 1), (4, 1), (4, 4), (1, 4)], fill=col)
        save(img, name)
    img, p = canvas(11, 11, WHITE)
    p.circ(5.5, 5.5, 5, fill=(255, 102, 0))
    p.poly([(4, 2.5), (8, 5.5), (4, 8.5)], fill=WHITE)
    save(img, "arrow.gif")
    img, p = canvas(16, 16, PALE)
    p.circ(8, 8, 7.5, fill=(102, 170, 0))
    p.poly([(6, 4), (11, 8), (6, 12)], fill=WHITE)
    save(img, "greenarrow.gif")


TITLES = {
    "home": "home", "dogs": "dogs", "cats": "cats", "fish": "fish", "birds": "birds", "ferrets": "ferrets",
    "reptiles": "reptiles", "smallpets": "small pets", "cart": "shopping cart", "checkout": "checkout",
    "thankyou": "thank you!", "account": "my account", "help": "help", "about": "about us", "search": "search",
    "advice": "pet advice", "superbowl": "super bowl", "mascot": "meet argyle", "investor": "investors",
    "features": "features", "liquidation": "closing sale",
}

def titles():
    for key, label in TITLES.items():
        img, p = canvas(150, 28, BLACK)
        # small paw print
        pc = (153, 204, 51) if key != "liquidation" else (255, 60, 60)
        p.ell(9, 13, 19, 22, fill=pc)
        for dx, dy in ((7, 9), (11, 6), (16, 6), (20, 9)):
            p.circ(dx, dy, 2, fill=pc)
        sz = p.fit(label, 17, 120)
        p.text(26, 14, label, sz, fill=WHITE, style="b", anchor="lm")
        save(img, "title_%s.gif" % key)
    img, p = canvas(9, 11, WHITE)
    p.rect(0, 0, 9, 11, fill=BLACK)
    p.pie(-9, -11, 9, 11, 0, 90, fill=WHITE)
    # the pie above carves the wrong quadrant; redo: black quarter-disc with white outside corner
    img, p = canvas(9, 11, WHITE)
    p.pie(-9, -11, 9, 11, 0, 90, fill=BLACK)
    save(img, "corner.gif")


def search_bits():
    img, p = canvas(16, 36, PALE)
    p.pie(0, 0, 32, 36, 90, 270, fill=TAN)
    save(img, "search_side.gif")
    img, p = canvas(20, 10, TAN)
    p.text(10, 5, "find", 9, fill=(80, 60, 0), anchor="mm")
    save(img, "find.gif")
    img, p = canvas(20, 20, TAN)
    p.circ(10, 10, 9.5, fill=(255, 102, 0), outline=(150, 50, 0))
    p.text(10, 10, "go", 9, fill=WHITE, anchor="mm")
    save(img, "go.gif")
    img, p = canvas(135, 15, PALE)
    p.text(0, 8, "Today's Features", 13, fill=(102, 136, 0), style="bi", anchor="lm")
    save(img, "todays_features.gif")


def button(name, label, w, h=24, fill=(255, 102, 0), fg=WHITE, bg=WHITE, edge=(150, 50, 0)):
    img, p = canvas(w, h, bg)
    p.rrect(0.5, 0.5, w - 1, h - 1, h / 2.2, fill=fill, outline=edge)
    p.rrect(4, 2, w - 5, h / 2.0, h / 4.0, fill=tuple(min(255, c + 50) for c in fill))
    sz = p.fit(label, 12, w - 14)
    p.text(w / 2.0, h / 2.0 + 0.5, label, sz, fill=fg, anchor="mm")
    save(img, name)


def buttons():
    button("btn_addcart.gif", "Add to Cart", 110)
    button("btn_checkout.gif", "Checkout", 96)
    button("btn_update.gif", "Update Cart", 96, fill=(102, 153, 0), edge=DKGREEN)
    button("btn_continue.gif", "Continue Shopping", 130, fill=(102, 153, 0), edge=DKGREEN)
    button("btn_placeorder.gif", "Place My Order", 130)
    button("btn_signin.gif", "Sign In", 80, fill=(102, 153, 0), edge=DKGREEN)
    button("btn_ask.gif", "Ask the Vet", 100, fill=(102, 153, 0), edge=DKGREEN, bg=PALE)
    button("btn_search.gif", "Search", 80, fill=(102, 153, 0), edge=DKGREEN)
    button("btn_soldout.gif", "Repossessed", 110, fill=(150, 150, 150), edge=(90, 90, 90))


def section_header(name, label, w=200, h=20, bg=WHITE, col=(102, 153, 0)):
    img, p = canvas(w, h, bg)
    p.rect(0, h - 3, w, h - 1, fill=col)
    p.text(2, h / 2.0 - 1, label, h * 0.62, fill=col, style="bi", anchor="lm")
    save(img, name)


def home_graphics():
    # welcome strip
    img, p = canvas(408, 40, WHITE)
    for i, x in enumerate(range(6, 400, 26)):
        y = 30 if i % 2 else 34
        c = (225, 240, 190)
        p.ell(x, y - 3, x + 7, y + 3, fill=c)
    p.text(4, 4, "Welcome to Petz.com!", 20, fill=(102, 153, 0), style="bi")
    p.text(404, 10, "Pick a pet. Any pet.", 11, fill=BLACK, style="i", anchor="ra")
    save(img, "home_top.gif")
    # marketing banner 415x117
    img, p = canvas(415, 117, (255, 255, 204))
    p.rect(0, 0, 414, 116, outline=(102, 153, 0), width=2)
    for i in range(14):
        random.seed(i)
        x, y = random.randint(8, 280), random.randint(6, 110)
        p.text(x, y, "*", 12, fill=(204, 230, 150), anchor="mm")
    paste_argyle(img, 300, 4, 112, mood="sing", flip=False, hat="santa")
    # gift box
    p.rect(250, 72, 296, 112, fill=RED, outline=(120, 0, 0))
    p.rect(268, 72, 278, 112, fill=YELLOW)
    p.rect(250, 86, 296, 94, fill=YELLOW)
    p.ell(258, 60, 274, 74, outline=YELLOW, width=3); p.ell(272, 60, 288, 74, outline=YELLOW, width=3)
    p.text(12, 10, "THE BELOW-COST", 22, fill=(204, 0, 0), style="b")
    p.text(12, 34, "HOLIDAY SALE", 28, fill=(204, 0, 0), style="b")
    p.text(12, 70, "Prices so low, our accountants wept.", 12, fill=BLACK, style="bi")
    p.text(12, 88, "Click here for 40 lbs of litter for $5.49*", 11, fill=(51, 102, 0), style="b")
    p.text(12, 103, "*Shipping $14.95. They wept about that too.", 9, fill=(90, 90, 90), style="i")
    save(img, "banner_home.gif")
    # bottom separator
    img, p = canvas(408, 22, WHITE)
    p.line([(0, 11), (180, 11)], fill=(153, 204, 51), width=2)
    p.line([(228, 11), (408, 11)], fill=(153, 204, 51), width=2)
    p.rrect(186, 8, 222, 14, 3, fill=(240, 230, 200), outline=(150, 120, 80))
    for cx in (188, 220):
        p.circ(cx, 7, 4, fill=(240, 230, 200), outline=(150, 120, 80))
        p.circ(cx, 15, 4, fill=(240, 230, 200), outline=(150, 120, 80))
    save(img, "home_bottom.gif")
    for key, label in (("dogs", "for your dog"), ("cats", "for your cat"), ("fish", "for your fish"),
                       ("birds", "for your bird"), ("ferrets", "for your ferret"),
                       ("reptiles", "for your reptile"), ("smallpets", "for small pets"),
                       ("mascot", "for your inner sock")):
        section_header("hdr_%s.gif" % key, label)
    section_header("hdr_vet.gif", "ask the vet", 200, 20)
    section_header("hdr_news.gif", "petz news", 200, 20)
    section_header("hdr_related.gif", "customers also lost money on", 300, 20)
    section_header("hdr_letters.gif", "fan mail", 300, 20)
    section_header("hdr_merch.gif", "official merchandise", 300, 20)
    section_header("hdr_script.gif", "the script", 300, 20)
    section_header("hdr_storyboard.gif", "the storyboard", 300, 20)
    section_header("hdr_faq.gif", "frequently asked questions", 300, 20)
    section_header("hdr_history.gif", "our history", 300, 20)
    section_header("hdr_inventory.gif", "remaining inventory", 300, 20, col=(204, 0, 0))
    section_header("hdr_letter.gif", "a letter from argyle", 300, 20, col=(204, 0, 0))
    # right column bits
    for name, label, w in (("btn_advice.gif", "pet advice", 73), ("btn_investors.gif", "investors", 65)):
        img, p = canvas(w, 19, WHITE)
        p.rrect(0, 0, w - 1, 18, 4, fill=(255, 204, 0), outline=(180, 120, 0))
        p.text(w / 2.0, 9.5, label, p.fit(label, 10, w - 6), anchor="mm")
        save(img, name)
    # pet of the day 137x123
    img, p = canvas(137, 123, WHITE)
    p.rect(0, 0, 136, 122, fill=(255, 250, 230), outline=(204, 153, 0), width=2)
    p.text(68, 4, "Pet of the Day", 13, fill=(204, 102, 0), style="bi", anchor="mt")
    p.rect(30, 22, 106, 98, fill=(200, 230, 255), outline=(120, 120, 120))
    p.rect(30, 80, 106, 98, fill=(120, 190, 90))
    animal(p.sub(36, 26, 0.64), "basset")
    p.text(68, 108, data.PET_OF_DAY[0], 11, fill=BLACK, style="b", anchor="mm")
    save(img, "potd.gif")
    # associates
    img, p = canvas(145, 46, WHITE)
    p.rrect(0, 0, 144, 45, 8, fill=(51, 102, 0))
    p.text(10, 6, "$$ Earn Money! $$", 13, fill=YELLOW, style="b")
    p.text(10, 25, "Become a Petz Associate", 11, fill=WHITE, style="b")
    save(img, "makemoney.gif")
    img, p = canvas(148, 19, WHITE)
    p.text(0, 9.5, "Our Commitment", 14, fill=(204, 102, 0), style="bi", anchor="lm")
    save(img, "commitment.gif")
    img, p = canvas(82, 18, WHITE)
    p.text(0, 9, "newsletter", 14, fill=(102, 153, 0), style="bi", anchor="lm")
    save(img, "newsletter.gif")
    # mascot promo 160x86 (nose hot spot for the image map)
    img, p = canvas(160, 86, WHITE)
    p.rrect(1, 1, 158, 84, 8, fill=(220, 238, 180), outline=(102, 153, 0))
    paste_argyle(img, 92, 4, 80, mood="wink")
    p.text(8, 10, "Meet", 13, fill=(51, 102, 0), style="bi")
    p.text(8, 26, "Argyle!", 18, fill=(204, 0, 0), style="b")
    p.text(8, 50, "Our spokes-sock", 9, fill=BLACK, style="i")
    p.text(8, 63, "has a brand new", 9, fill=BLACK, style="i")
    p.text(8, 73, "fan club >>", 9, fill=BLACK, style="b")
    save(img, "puppet_promo.gif")
    # nose position in that image: unit (112,44) * 80/160 + (92,4)
    return (92 + 112 * 0.5, 4 + 44 * 0.5)


def category_banners():
    for cat, label, tag, short in data.CATEGORIES:
        img, p = canvas(415, 80, WHITE)
        p.rrect(0, 0, 414, 79, 10, fill=(240, 248, 220), outline=(153, 204, 51), width=2)
        p.circ(368, 40, 37, fill=(255, 255, 204))
        animal(p.sub(334, 6, 0.68), TAB_ANIMAL[cat])
        p.text(14, 8, label, 30, fill=(102, 153, 0), style="b")
        p.text(16, 48, data.CATEGORIES[[c[0] for c in data.CATEGORIES].index(cat)][3].replace("&amp;", "&"),
               13, fill=(80, 80, 80), style="bi")
        save(img, "cat_%s.gif" % cat)


# ===================================================================== PRODUCTS (200x200)
def ground(p):
    p.ell(30, 172, 170, 192, fill=(225, 225, 225))

def label_text(p, x, y, s, size, col=WHITE, maxw=90, style="b"):
    p.text(x, y, s, p.fit(s, size, maxw, style), fill=col, style=style, anchor="mm")

def k_bag(p, o):
    ground(p)
    c = o["color"]
    p.poly([(44, 30), (156, 30), (164, 180), (36, 180)], fill=c, outline=BLACK, width=2)
    for x in range(44, 157, 8):
        p.poly([(x, 30), (x + 4, 22), (x + 8, 30)], fill=c, outline=BLACK, width=1)
    p.rect(40, 70, 160, 132, fill=o["band"], outline=BLACK, width=1)
    animal(p.sub(44, 80, 0.42), o["animal"])
    label_text(p, 126, 92, o["label"], 18, col=c, maxw=58)
    label_text(p, 126, 116, o["sub"], 15, col=BLACK, maxw=58)
    p.text(100, 150, "PREMIUM", 13, fill=WHITE, anchor="mm")

def k_can(p, o):
    ground(p)
    for i, x in enumerate((40, 104)):
        p.rect(x, 60, x + 56, 176, fill=o["color"], outline=BLACK, width=2)
        p.ell(x, 50, x + 56, 70, fill=(200, 200, 210), outline=BLACK, width=2)
        p.ell(x + 6, 54, x + 50, 66, outline=(150, 150, 160), width=1)
        p.rect(x, 96, x + 56, 140, fill=WHITE)
        label_text(p, x + 28, 110, o["label"], 12, col=o["color"], maxw=50)
        label_text(p, x + 28, 128, o["sub"], 9, col=BLACK, maxw=50)
        p.ell(x, 168, x + 56, 184, fill=o["color"], outline=BLACK, width=2)

def k_bone(p, o):
    ground(p)
    c = o["color"]
    for cx, cy in ((40, 76), (48, 120), (152, 76), (160, 120)):
        p.circ(cx, cy, 26, fill=c, outline=BLACK, width=2)
    p.rect(44, 82, 156, 114, fill=c)
    p.line([(54, 82), (146, 82)], width=2); p.line([(54, 114), (146, 114)], width=2)
    p.text(100, 98, "CHEW", 14, fill=(150, 60, 0), anchor="mm")

def k_ball(p, o):
    ground(p)
    p.circ(100, 100, 70, fill=o["color"], outline=BLACK, width=2)
    p.chord(30, 74, 170, 126, 0, 360, fill=o["stripe"])
    p.circ(100, 100, 70, outline=BLACK, width=2)
    p.ell(56, 46, 90, 70, fill=(180, 230, 255))
    p.text(100, 101, o["text"], 26, fill=(0, 51, 153), anchor="mm")

def k_rope(p, o):
    ground(p)
    for i in range(8):
        y = 92 + (i % 4) * 5
        p.line([(48, y), (152, y)], fill=o["color"] if i % 2 else o["color2"], width=5)
    for cx in (40, 160):
        p.circ(cx, 100, 24, fill=o["color"], outline=BLACK, width=2)
        p.arc(cx - 16, 84, cx + 16, 116, 30, 300, fill=o["color2"], width=4)
        for k in range(-2, 3):
            p.line([(cx + k * 6, 122), (cx + k * 8, 150)], fill=o["color2"], width=3)

def k_leash(p, o):
    ground(p)
    p.rrect(44, 60, 120, 140, 34, fill=o["color"], outline=BLACK, width=2)
    p.rrect(56, 132, 82, 176, 8, fill=(60, 60, 60), outline=BLACK, width=2)
    p.circ(82, 100, 18, fill=(230, 230, 230), outline=BLACK)
    p.rect(118, 92, 128, 104, fill=(60, 60, 60))
    p.line([(128, 98), (150, 90), (168, 70), (176, 50)], fill=(30, 30, 30), width=3)
    p.circ(178, 44, 7, outline=(180, 180, 180), width=3)
    p.text(82, 100, "26'", 12, anchor="mm")

def k_bed(p, o):
    ground(p)
    p.ell(14, 70, 186, 182, fill=o["color"], outline=BLACK, width=2)
    p.ell(40, 88, 160, 164, fill=o["cushion"], outline=BLACK, width=2)
    p.arc(60, 104, 140, 150, 200, 340, fill=(150, 100, 200), width=2)
    p.text(100, 132, "zzz", 18, fill=(102, 51, 153), style="bi", anchor="mm")

def k_sweater(p, o):
    ground(p)
    c = o["color"]
    p.poly([(40, 50), (160, 50), (176, 100), (150, 110), (148, 170), (52, 170), (50, 110), (24, 100)],
           fill=c, outline=BLACK, width=2)
    p.rect(64, 44, 136, 56, fill=o["trim"], outline=BLACK)
    p.rect(52, 158, 148, 170, fill=o["trim"], outline=BLACK)
    for y in range(80, 150, 22):
        for x in range(64, 140, 22):
            p.poly([(x + 11, y), (x + 20, y + 9), (x + 11, y + 18), (x + 2, y + 9)], fill=o["trim"])
    p.text(100, 100, ".com", 13, fill=c, anchor="mm")

def k_mouse(p, o):
    ground(p)
    p.line([(40, 140), (24, 120), (20, 90), (34, 70)], fill=(255, 120, 150), width=3)
    p.ell(40, 90, 150, 170, fill=o["color"], outline=BLACK, width=2)
    p.circ(132, 92, 18, fill=(200, 200, 200), outline=BLACK, width=2)
    p.circ(132, 92, 9, fill=(255, 180, 200))
    p.circ(150, 128, 3, fill=BLACK)
    p.circ(166, 140, 5, fill=(255, 100, 130))
    p.poly([(114, 150), (124, 152), (122, 182), (116, 186), (110, 182)], fill=o["tie"], outline=BLACK)
    p.poly([(112, 146), (126, 146), (122, 154), (116, 154)], fill=o["tie"], outline=BLACK)

def k_cattree(p, o):
    ground(p)
    c, cp = o["carpet"], o["color"]
    p.rect(60, 30, 74, 176, fill=cp, outline=BLACK); p.rect(126, 60, 140, 176, fill=cp, outline=BLACK)
    for x in range(60, 74, 3):
        pass
    for y0 in range(34, 176, 8):
        p.line([(60, y0), (74, y0 + 3)], fill=(160, 130, 80), width=1)
        p.line([(126, y0 + 26 if y0 + 26 < 176 else y0), (140, y0 + 29 if y0 + 29 < 176 else y0)], fill=(160, 130, 80))
    p.rect(30, 166, 170, 180, fill=c, outline=BLACK, width=2)
    p.rect(40, 110, 110, 150, fill=c, outline=BLACK, width=2)
    p.ell(56, 118, 86, 146, fill=(60, 30, 0))
    p.rect(104, 54, 166, 66, fill=c, outline=BLACK, width=2)
    p.rect(34, 22, 100, 34, fill=c, outline=BLACK, width=2)
    animal(p.sub(116, 22, 0.34), "cat")

def k_post(p, o):
    ground(p)
    p.rect(50, 160, 150, 182, fill=o["base"], outline=BLACK, width=2)
    p.rect(80, 30, 120, 162, fill=o["color"], outline=BLACK, width=2)
    for y in range(34, 160, 5):
        p.line([(80, y), (120, y + 2)], fill=(170, 140, 90), width=1)
    p.rect(66, 20, 134, 32, fill=o["base"], outline=BLACK, width=2)
    p.line([(120, 60), (140, 80)], fill=(255, 0, 0), width=1)
    p.circ(142, 84, 7, fill=(255, 220, 0), outline=BLACK)

def k_laser(p, o):
    ground(p)
    p.rrect(30, 70, 140, 96, 12, fill=o["color"], outline=BLACK, width=2)
    p.rect(132, 74, 142, 92, fill=(150, 150, 150))
    p.circ(60, 83, 5, fill=RED)
    p.line([(142, 83), (176, 150)], fill=(255, 0, 0), width=2)
    p.circ(176, 152, 6, fill=(255, 0, 0))
    p.text(90, 83, "2000", 11, fill=WHITE, anchor="mm")
    p.text(60, 130, "Millennium", 12, fill=(204, 0, 0), style="bi", anchor="mm")
    p.text(60, 146, "Mode!", 12, fill=(204, 0, 0), style="bi", anchor="mm")

def k_litterbox(p, o):
    ground(p)
    c = o["color"]
    p.rect(30, 120, 170, 176, fill=c, outline=BLACK, width=2)
    p.chord(30, 50, 170, 190, 180, 360, fill=c, outline=BLACK, width=2)
    p.rect(30, 116, 170, 124, fill=tuple(max(0, x - 50) for x in c), outline=BLACK)
    p.rrect(74, 82, 126, 150, 20, fill=(240, 240, 240), outline=BLACK, width=2)
    p.rect(84, 158, 116, 168, fill=(220, 180, 60), outline=BLACK)
    p.text(100, 163, "EXEC", 7, anchor="mm")

def k_tank(p, o):
    ground(p)
    p.rect(12, 40, 188, 176, fill=(170, 220, 255), outline=BLACK, width=3)
    p.rect(12, 30, 188, 44, fill=(40, 40, 40), outline=BLACK)
    p.rect(12, 150, 188, 176, fill=(200, 170, 120))
    for x in range(16, 186, 6):
        p.circ(x, 156 + (x % 4), 2, fill=(150, 120, 80))
    for x, h in ((30, 70), (44, 50), (160, 80), (172, 60)):
        p.line([(x, 152), (x - 6, 152 - h / 2.0), (x + 2, 152 - h)], fill=(0, 140, 60), width=4)
    animal(p.sub(60, 70, 0.34), "fish")
    animal(p.sub(110, 96, 0.26), "fish", (255, 255, 0))
    for y in (60, 76, 92, 110):
        p.circ(150, y, 3, outline=WHITE)
    p.rect(12, 176, 188, 186, fill=(40, 40, 40))

def k_bowl(p, o):
    ground(p)
    p.ell(30, 50, 170, 186, fill=(210, 235, 255), outline=(80, 120, 160), width=3)
    p.chord(30, 50, 170, 186, 10, 170, fill=(150, 200, 255))
    p.ell(54, 40, 146, 62, fill=WHITE, outline=(80, 120, 160), width=3)
    animal(p.sub(70, 100, 0.4), "fish")
    p.arc(46, 70, 90, 160, 120, 200, fill=WHITE, width=4)

def k_chest(p, o):
    ground(p)
    c = o["color"]
    p.rect(40, 100, 160, 170, fill=c, outline=BLACK, width=2)
    p.poly([(40, 100), (60, 50), (180, 40), (160, 100)], fill=tuple(min(255, x + 30) for x in c), outline=BLACK, width=2)
    p.rect(40, 96, 160, 104, fill=YELLOW, outline=BLACK)
    p.rect(92, 104, 108, 124, fill=YELLOW, outline=BLACK)
    for i, (x, y) in enumerate(((90, 86), (110, 80), (100, 70))):
        p.circ(x, y, 7, fill=YELLOW, outline=(150, 100, 0))
    p.text(120, 66, "VC $$", 10, fill=(0, 100, 0), anchor="mm")
    for y in (30, 16, 4):
        p.circ(70 + y, y + 6, 4, outline=(100, 160, 255), width=1.5)

def k_pump(p, o):
    ground(p)
    p.rrect(40, 90, 150, 170, 14, fill=o["color"], outline=BLACK, width=2)
    p.text(95, 120, "BUBBLE", 13, fill=WHITE, anchor="mm")
    p.text(95, 138, "TRON", 13, fill=WHITE, anchor="mm")
    p.line([(150, 110), (170, 100), (176, 60), (170, 30)], fill=(150, 200, 150), width=3)
    p.rrect(160, 20, 180, 34, 4, fill=(120, 120, 120))
    for y in (10, 2):
        p.circ(170 - y, y + 4, 3, outline=(100, 160, 255))

def k_net(p, o):
    ground(p)
    p.line([(30, 170), (106, 96)], fill=(80, 80, 80), width=5)
    p.ell(100, 30, 180, 110, outline=(60, 60, 60), width=3)
    for i in range(1, 8):
        p.line([(100 + i * 10, 34), (100 + i * 10, 140 - abs(4 - i) * 6)], fill=o["color"], width=1)
    for j in range(1, 8):
        p.line([(104, 30 + j * 10), (176, 30 + j * 10)], fill=o["color"], width=1)
    p.ell(100, 30, 180, 110, outline=(60, 60, 60), width=3)

def k_castle(p, o):
    ground(p)
    c = o["color"]
    p.rect(40, 90, 160, 176, fill=c, outline=BLACK, width=2)
    for x0 in (30, 84, 136):
        p.rect(x0, 50, x0 + 34, 176, fill=c, outline=BLACK, width=2)
        for i in range(3):
            p.rect(x0 + i * 12, 40, x0 + i * 12 + 8, 52, fill=c, outline=BLACK)
        p.rrect(x0 + 11, 70, x0 + 23, 90, 6, fill=(40, 40, 40))
    p.chord(84, 130, 118, 200, 180, 360, fill=(40, 40, 40))
    p.line([(101, 40), (101, 20)], width=2)
    p.poly([(101, 20), (122, 26), (101, 32)], fill=RED)

def k_cage(p, o):
    ground(p)
    c = o["color"]
    tall = o.get("tall")
    if tall:
        p.rect(36, 24, 164, 178, outline=c, width=3)
        for x in range(36, 165, 9):
            p.line([(x, 24), (x, 178)], fill=c, width=1.5)
        for y in (74, 126):
            p.rect(36, y, 164, y + 6, fill=(120, 120, 120), outline=BLACK)
        p.line([(60, 120), (110, 80)], fill=(150, 110, 70), width=5)
        p.line([(100, 172), (150, 132)], fill=(150, 110, 70), width=5)
        animal(p.sub(110, 34, 0.38), "ferret")
        p.rect(30, 172, 170, 184, fill=(60, 60, 60))
    else:
        p.chord(36, 20, 164, 120, 180, 360, outline=c, width=3)
        for x in range(40, 162, 10):
            top = 70 - math.sqrt(max(0, 64 ** 2 - (x - 100) ** 2)) * 50 / 64.0
            p.line([(x, top), (x, 170)], fill=c, width=1.5)
        p.rect(30, 166, 170, 180, fill=c, outline=BLACK, width=2)
        p.line([(56, 120), (144, 120)], fill=(150, 110, 70), width=4)
        animal(p.sub(78, 80, 0.38), "bird")
        p.circ(100, 16, 6, outline=c, width=3)

def k_mirror(p, o):
    ground(p)
    p.line([(100, 10), (100, 40)], fill=(150, 150, 150), width=2)
    p.ell(54, 36, 146, 140, fill=o["color"], outline=BLACK, width=2)
    p.ell(64, 46, 136, 130, fill=(220, 240, 255), outline=BLACK)
    p.line([(80, 60), (96, 76)], fill=WHITE, width=4)
    p.chord(86, 140, 114, 170, 180, 360, fill=YELLOW, outline=BLACK)
    p.circ(100, 158, 3, fill=BLACK)

def k_cassette(p, o):
    ground(p)
    p.rrect(24, 50, 176, 150, 8, fill=(40, 40, 40), outline=BLACK, width=2)
    p.rect(36, 60, 164, 110, fill=o["color"], outline=BLACK)
    p.text(100, 72, "POLLY'S", 12, anchor="mm"); p.text(100, 90, "PHRASEBOOK", 11, anchor="mm")
    p.rrect(60, 112, 140, 140, 6, fill=(100, 100, 100))
    p.circ(78, 126, 8, fill=WHITE); p.circ(122, 126, 8, fill=WHITE)
    animal(p.sub(140, 140, 0.34), "bird", (0, 200, 80))

def k_cuttlebone(p, o):
    ground(p)
    for dx in (0, 34):
        p.ell(50 + dx, 30, 96 + dx, 176, fill=o["color"], outline=(150, 140, 120), width=2)
        for y in range(46, 166, 10):
            p.line([(58 + dx, y), (88 + dx, y)], fill=(230, 220, 200), width=1)
    p.rect(60, 100, 140, 110, fill=(200, 200, 200), outline=BLACK)

def k_swing(p, o):
    ground(p)
    p.line([(60, 150), (100, 20), (140, 150)], fill=(200, 160, 50), width=3)
    p.circ(100, 20, 6, outline=(200, 160, 50), width=3)
    p.rrect(46, 146, 154, 158, 5, fill=(170, 120, 60), outline=BLACK)
    for i, c in enumerate(((255, 0, 0), (0, 160, 255), (255, 220, 0))):
        p.circ(70 + i * 3, 100 + i * 14, 6, fill=c, outline=BLACK)
    animal(p.sub(84, 92, 0.48), "bird", (255, 120, 200))

def k_birdbath(p, o):
    ground(p)
    c = o["color"]
    p.poly([(84, 90), (116, 90), (124, 170), (76, 170)], fill=c, outline=BLACK, width=2)
    p.rect(64, 166, 136, 180, fill=c, outline=BLACK, width=2)
    p.chord(30, 50, 170, 110, 0, 180, fill=c, outline=BLACK, width=2)
    p.ell(30, 70, 170, 92, fill=(170, 220, 255), outline=BLACK, width=2)
    animal(p.sub(110, 26, 0.4), "bird")

def k_hammock(p, o):
    ground(p)
    p.line([(20, 20), (40, 70)], fill=(120, 120, 120), width=2); p.line([(180, 20), (160, 70)], fill=(120, 120, 120), width=2)
    p.line([(20, 20), (60, 70)], fill=(120, 120, 120), width=2); p.line([(180, 20), (140, 70)], fill=(120, 120, 120), width=2)
    p.chord(36, 30, 164, 150, 0, 180, fill=o["color"], outline=BLACK, width=2)
    for x in range(48, 160, 20):
        p.circ(x, 100, 5, fill=o["color2"])
    animal(p.sub(64, 46, 0.5), "ferret")
    p.chord(36, 30, 164, 150, 10, 170, fill=o["color"])

def k_tube(p, o):
    ground(p)
    c = o["color"]
    p.line([(26, 140), (70, 110), (120, 120), (170, 80)], fill=BLACK, width=46)
    p.line([(26, 140), (70, 110), (120, 120), (170, 80)], fill=c, width=42)
    for x, y in ((50, 124), (80, 112), (110, 118), (140, 104)):
        p.line([(x - 8, y - 20), (x + 6, y + 20)], fill=tuple(max(0, v - 60) for v in c), width=2)
    p.ell(156, 56, 186, 104, fill=(60, 30, 0), outline=BLACK, width=2)
    animal(p.sub(150, 52, 0.36), "ferret")

def k_safe(p, o):
    ground(p)
    p.rect(40, 50, 160, 176, fill=o["color"], outline=BLACK, width=3)
    p.rect(52, 62, 148, 164, outline=(40, 40, 40), width=2)
    p.circ(100, 104, 22, fill=(200, 200, 200), outline=BLACK, width=2)
    for a in range(0, 360, 30):
        r = math.radians(a)
        p.line([(100 + 16 * math.cos(r), 104 + 16 * math.sin(r)), (100 + 20 * math.cos(r), 104 + 20 * math.sin(r))])
    p.rect(130, 96, 140, 112, fill=(200, 200, 200), outline=BLACK)
    p.text(100, 146, "SOCKS", 12, fill=WHITE, anchor="mm")

def k_bottle(p, o):
    ground(p)
    c = o["color"]
    p.rrect(62, 60, 138, 178, 14, fill=c, outline=BLACK, width=2)
    p.rect(84, 34, 116, 62, fill=WHITE, outline=BLACK, width=2)
    p.rect(90, 18, 110, 36, fill=(80, 80, 80), outline=BLACK)
    p.rect(62, 92, 138, 140, fill=WHITE, outline=BLACK)
    label_text(p, 100, 108, o["label"], 14, col=c, maxw=66)
    p.text(100, 128, "8 oz", 10, anchor="mm")

def k_lamp(p, o):
    ground(p)
    p.line([(170, 30), (130, 40), (110, 56)], fill=BLACK, width=3)
    p.chord(30, 30, 170, 170, 180, 360, fill=o["color"], outline=BLACK, width=2)
    p.chord(46, 60, 154, 140, 180, 360, fill=(220, 220, 220))
    p.ell(70, 80, 130, 120, fill=(255, 240, 150), outline=(200, 160, 0))
    for a in range(20, 170, 25):
        r = math.radians(a)
        p.line([(100 + 40 * math.cos(r), 110 + 40 * math.sin(r)), (100 + 70 * math.cos(r), 110 + 70 * math.sin(r))],
               fill=(255, 160, 0), width=3)
    p.text(100, 74, "150W", 12, anchor="mm")

def k_terrarium(p, o):
    ground(p)
    p.rect(14, 50, 186, 176, fill=(230, 245, 250), outline=BLACK, width=3)
    for x in range(14, 187, 6):
        p.line([(x, 44), (x, 50)], fill=(80, 80, 80))
    p.rect(14, 42, 186, 50, outline=BLACK)
    p.rect(14, 140, 186, 176, fill=(240, 210, 150))
    p.ell(110, 118, 170, 160, fill=(150, 130, 110), outline=BLACK)
    p.rrect(40, 80, 54, 146, 7, fill=(40, 150, 60), outline=BLACK)
    p.rrect(26, 100, 38, 124, 6, fill=(40, 150, 60), outline=BLACK)
    p.line([(38, 112), (42, 112)], fill=(40, 150, 60), width=4)
    animal(p.sub(70, 100, 0.42), "lizard")

def k_crickets(p, o):
    ground(p)
    p.rect(30, 60, 170, 176, fill=(230, 200, 140), outline=BLACK, width=2)
    for x in range(44, 160, 18):
        p.circ(x, 76, 4, fill=(60, 40, 10))
    p.text(100, 112, "LIVE!", 22, fill=RED, anchor="mm")
    p.text(100, 140, "500 CRICKETS", 12, anchor="mm")
    p.text(100, 158, "THIS SIDE UP", 9, fill=(80, 80, 80), anchor="mm")
    for x, y in ((150, 40), (60, 36), (176, 150)):
        p.ell(x - 10, y - 4, x + 10, y + 4, fill=o["color"])
        p.line([(x + 6, y), (x + 14, y - 10)], width=1)
        p.line([(x - 4, y + 2), (x - 12, y + 10)], width=1)

def k_branch(p, o):
    ground(p)
    c = o["color"]
    p.line([(20, 170), (70, 120), (110, 110), (150, 60), (180, 40)], fill=c, width=14)
    p.line([(110, 110), (150, 130), (176, 128)], fill=c, width=9)
    p.line([(70, 120), (60, 80)], fill=c, width=8)
    animal(p.sub(84, 50, 0.5), "lizard", (90, 200, 90))

def k_hotrock(p, o):
    ground(p)
    p.poly([(30, 170), (40, 120), (80, 92), (140, 96), (172, 132), (176, 172)], fill=o["color"], outline=BLACK, width=2)
    for x, y in ((70, 130), (120, 120), (150, 150)):
        p.circ(x, y, 4, fill=(110, 100, 90))
    for x in (70, 100, 130):
        p.arc(x - 10, 40, x + 10, 60, 90, 270, fill=(255, 100, 0), width=2)
        p.arc(x - 10, 60, x + 10, 80, 270, 90, fill=(255, 100, 0), width=2)
    p.line([(176, 160), (190, 150), (196, 176)], width=2)

def k_wheel(p, o):
    ground(p)
    c = o["color"]
    p.poly([(70, 176), (100, 100), (130, 176)], fill=(200, 200, 200), outline=BLACK, width=2)
    p.circ(100, 96, 76, fill=c, outline=BLACK, width=2)
    p.circ(100, 96, 64, fill=(220, 240, 255), outline=BLACK, width=2)
    for a in range(0, 360, 45):
        r = math.radians(a)
        p.line([(100, 96), (100 + 64 * math.cos(r), 96 + 64 * math.sin(r))], fill=c, width=2)
    p.circ(100, 96, 8, fill=(150, 150, 150), outline=BLACK)
    animal(p.sub(70, 110, 0.4), "hamster")

def k_hay(p, o):
    ground(p)
    c = o["color"]
    p.rect(26, 70, 174, 176, fill=c, outline=BLACK, width=2)
    random.seed(7)
    for i in range(90):
        x = random.randint(28, 170); y = random.randint(72, 172)
        p.line([(x, y), (x + random.randint(-6, 6), y + random.randint(4, 12))], fill=(160, 150, 60), width=1)
    p.rect(60, 70, 66, 176, fill=(150, 100, 50)); p.rect(134, 70, 140, 176, fill=(150, 100, 50))
    p.text(100, 50, "10 LB", 16, fill=(102, 102, 0), anchor="mm")

def k_waterbottle(p, o):
    ground(p)
    p.rrect(70, 20, 130, 140, 16, fill=(220, 240, 255), outline=BLACK, width=2)
    p.rect(72, 60, 128, 138, fill=(150, 200, 255))
    p.rect(84, 138, 116, 152, fill=o["color"], outline=BLACK)
    p.line([(100, 152), (112, 186)], fill=(180, 180, 180), width=5)
    p.circ(112, 188, 3, fill=(120, 200, 255))

def k_habitat(p, o):
    ground(p)
    p.rect(24, 90, 150, 176, fill=(230, 245, 255), outline=BLACK, width=2)
    p.rect(24, 160, 150, 176, fill=o["color"], outline=BLACK)
    p.chord(20, 60, 154, 120, 180, 360, fill=o["color"], outline=BLACK, width=2)
    p.line([(140, 100), (170, 70), (176, 40)], fill=BLACK, width=18)
    p.line([(140, 100), (170, 70), (176, 40)], fill=(255, 220, 120), width=14)
    p.ell(156, 18, 196, 50, fill=(230, 245, 255), outline=BLACK, width=2)
    p.circ(60, 130, 22, outline=(0, 150, 255), width=3)
    animal(p.sub(90, 120, 0.36), "hamster")

def k_hutch(p, o):
    ground(p)
    c = o["color"]
    p.poly([(16, 70), (100, 20), (184, 70)], fill=(160, 40, 40), outline=BLACK, width=2)
    p.rect(24, 70, 176, 170, fill=c, outline=BLACK, width=2)
    p.rect(30, 80, 94, 160, fill=(230, 230, 230), outline=BLACK)
    for x in range(30, 95, 8):
        p.line([(x, 80), (x, 160)], fill=(150, 150, 150))
    for y in range(80, 161, 8):
        p.line([(30, y), (94, y)], fill=(150, 150, 150))
    p.rect(104, 80, 170, 160, fill=(120, 80, 40), outline=BLACK)
    p.line([(170, 160), (196, 186)], fill=c, width=6)
    p.ell(40, 110, 84, 156, fill=WHITE, outline=BLACK)
    p.ell(48, 80, 58, 118, fill=WHITE, outline=BLACK); p.ell(62, 80, 72, 118, fill=WHITE, outline=BLACK)

def k_sticks(p, o):
    ground(p)
    random.seed(3)
    for i in range(12):
        x = 40 + i * 10
        p.line([(x, 170), (x + random.randint(-16, 16), 40 + random.randint(0, 30))], fill=o["color"], width=6)
    p.rect(40, 110, 160, 126, fill=RED, outline=BLACK)
    p.text(100, 118, "GNAW-SOME", 10, fill=WHITE, anchor="mm")

def k_hats(p, o):
    ground(p)
    for i, c in enumerate((o["color"], (0, 180, 255), (255, 200, 0))):
        x = 30 + i * 52
        p.poly([(x, 160), (x + 50, 160), (x + 25, 50 + i * 8)], fill=c, outline=BLACK, width=2)
        p.circ(x + 25, 46 + i * 8, 7, fill=WHITE, outline=BLACK)
        for j in range(3):
            p.circ(x + 18 + j * 7, 140 - j * 22, 3, fill=WHITE)

def k_puppet(p, o):
    ground(p)
    paste_argyle(p.img, 42 if p.k == 1 else 0, 18, 168 * p.k, mood="happy")

def k_mug(p, o):
    ground(p)
    p.rrect(40, 50, 140, 176, 10, fill=WHITE, outline=BLACK, width=2)
    p.arc(120, 80, 176, 146, 270, 90, fill=BLACK, width=10)
    p.arc(120, 80, 176, 146, 270, 90, fill=WHITE, width=6)
    p.ell(40, 42, 140, 60, fill=(120, 70, 30), outline=BLACK, width=2)
    paste_argyle(p.img, 56, 66, 90)
    p.rect(40, 150, 140, 160, fill=o["color"])

def k_shirt(p, o):
    ground(p)
    c = o["color"]
    p.poly([(60, 30), (140, 30), (190, 70), (166, 96), (150, 84), (150, 180), (50, 180), (50, 84), (34, 96), (10, 70)],
           fill=c, outline=BLACK, width=2)
    p.chord(80, 20, 120, 46, 0, 180, fill=WHITE, outline=BLACK)
    paste_argyle(p.img, 70, 60, 100)

KINDS = dict((k[2:], v) for k, v in globals().items() if k.startswith("k_"))


def products():
    for pr in data.P:
        kind, o = pr["img"]
        img, p = canvas(200, 200, WHITE)
        KINDS[kind](p, o)
        big = img.resize((200, 200), Image.LANCZOS)
        save(big, "prod_%s.gif" % pr["id"], 200, 200)
        save(img, "thumb_%s.gif" % pr["id"], 90, 90)


# ===================================================================== SUPER BOWL STORYBOARD
def van(p, x, y, k=1.0, col=(102, 170, 0)):
    q = p.sub(x, y, k)
    q.rect(0, 0, 90, 46, fill=WHITE, outline=BLACK, width=2)
    q.rect(0, 0, 90, 8, fill=col)
    q.text(45, 24, "PETZ.COM", 13, fill=col, style="b", anchor="mm")
    q.text(45, 38, "we deliver (at a loss)", 6, fill=BLACK, style="i", anchor="mm")
    q.poly([(90, 12), (112, 12), (124, 30), (124, 52), (90, 52)], fill=col, outline=BLACK, width=2)
    q.poly([(96, 16), (110, 16), (118, 30), (96, 30)], fill=(200, 230, 255), outline=BLACK)
    q.rect(0, 46, 124, 54, fill=(80, 80, 80))
    for wx in (20, 100):
        q.circ(wx, 56, 9, fill=(30, 30, 30)); q.circ(wx, 56, 4, fill=(180, 180, 180))

def notes(p, x, y, n=3, col=BLACK):
    for i in range(n):
        nx, ny = x + i * 14, y - i * 8
        p.ell(nx, ny + 10, nx + 8, ny + 16, fill=col)
        p.line([(nx + 7.5, ny + 13), (nx + 7.5, ny)], fill=col, width=1.5)
        p.line([(nx + 7.5, ny), (nx + 12, ny + 4)], fill=col, width=1.5)

def storyboard():
    W, H = 200, 150
    def frame(n, draw):
        img, p = canvas(W, H, WHITE)
        draw(img, p)
        p.rect(0, 0, W - 1, H - 1, outline=BLACK, width=3)
        p.rect(6, 6, 24, 20, fill=BLACK)
        p.text(15, 13, str(n), 10, fill=WHITE, anchor="mm")
        save(img, "sb%d.gif" % n)

    def f1(img, p):  # night, at the window, rain
        p.rect(0, 0, W, H, fill=(40, 40, 80))
        p.rect(30, 20, 170, 120, fill=(20, 20, 50), outline=(200, 170, 120), width=6)
        p.line([(100, 20), (100, 120)], fill=(200, 170, 120), width=4)
        p.line([(30, 70), (170, 70)], fill=(200, 170, 120), width=4)
        random.seed(11)
        for i in range(40):
            x = random.randint(34, 166); y = random.randint(24, 110)
            p.line([(x, y), (x - 3, y + 9)], fill=(150, 170, 220), width=1)
        p.rect(0, 120, W, H, fill=(120, 80, 50))
        paste_argyle(img, 66, 52, 80, mood="sad")
    def f2(img, p):  # van pulls away, Argyle sings at window
        p.rect(0, 0, W, H, fill=(180, 210, 255))
        p.rect(0, 112, W, H, fill=(110, 110, 110))
        p.line([(0, 130), (W, 130)], fill=YELLOW, width=2)
        p.rect(8, 20, 70, 110, fill=(230, 200, 160), outline=BLACK, width=2)
        p.rect(16, 34, 62, 80, fill=(200, 230, 255), outline=BLACK)
        paste_argyle(img, 18, 36, 46, mood="sing")
        notes(p, 60, 24, 3)
        van(p, 90, 66, 0.82)
        for y in (78, 90, 102):
            p.line([(178, y), (196, y)], fill=(90, 90, 90), width=2)
    def f3(img, p):  # chasing down the street
        p.rect(0, 0, W, H, fill=(255, 220, 160))
        p.rect(0, 108, W, H, fill=(110, 110, 110))
        van(p, 128, 76, 0.55)
        paste_argyle(img, 20, 40, 84, mood="sing")
        for y in (70, 84, 98):
            p.line([(2, y), (18, y)], fill=(90, 90, 90), width=2)
        notes(p, 84, 36, 3, col=(204, 0, 0))
    def f4(img, p):  # hug the 40-lb bag
        p.rect(0, 0, W, H, fill=(200, 235, 200))
        p.rect(0, 116, W, H, fill=(110, 110, 110))
        kb = p.sub(96, 34, 0.48)
        k_bag(kb, dict(color=(102, 102, 153), band=WHITE, label="LITTER", sub="40 LB", animal="cat"))
        paste_argyle(img, 34, 34, 90, mood="happy")
        for x, y in ((90, 26), (160, 20), (70, 14)):
            p.text(x, y, "<3", 12, fill=RED, style="b")
    def f5(img, p):  # title card
        p.rect(0, 0, W, H, fill=GREEN)
        paste_argyle(img, 8, 30, 104, mood="wink")
        p.text(132, 46, "petz", 32, fill=WHITE, style="serifbi", anchor="mm", stroke=1, stroke_fill=DKGREEN)
        p.text(132, 74, ".com", 20, fill=YELLOW, style="serifbi", anchor="mm", stroke=1, stroke_fill=DKGREEN)
        p.text(132, 100, "Because pets", 11, fill=BLACK, style="bi", anchor="mm")
        p.text(132, 114, "can't drive!", 11, fill=BLACK, style="bi", anchor="mm")
    def f6(img, p):  # the accountant
        p.rect(0, 0, W, H, fill=(245, 245, 245))
        p.rect(110, 30, 190, 100, fill=WHITE, outline=BLACK, width=2)
        p.text(150, 42, "INVOICE", 10, anchor="mm")
        p.text(118, 56, "Litter  $5.49", 8, style="")
        p.text(118, 68, "Ship  $14.95", 8, style="")
        p.text(118, 82, "Our cost $48.05", 8, fill=RED)
        # fainting accountant (stick figure, horizontal)
        p.circ(40, 110, 10, fill=(255, 220, 180), outline=BLACK)
        p.line([(50, 112), (96, 116)], width=3)
        p.line([(96, 116), (112, 104)], width=3); p.line([(96, 116), (114, 126)], width=3)
        p.line([(64, 113), (70, 96)], width=2); p.line([(80, 115), (88, 132)], width=2)
        p.text(30, 86, "x x", 9, anchor="mm")
        p.rect(0, 128, W, H, fill=(160, 120, 80))
    for i, f in enumerate((f1, f2, f3, f4, f5, f6)):
        frame(i + 1, f)


# ===================================================================== INVESTOR CHART
def chart():
    W, H = 420, 250
    img, p = canvas(W, H, WHITE)
    p.text(W / 2.0, 6, "PETZ Since Our IPO: Up and to the Right!", 14, fill=(51, 102, 0), style="b", anchor="mt")
    x0, y0, x1, y1 = 50, 30, 400, 210
    p.rect(x0, y0, x1, y1, fill=(255, 255, 230), outline=BLACK)
    for i in range(1, 5):
        y = y0 + (y1 - y0) * i / 5.0
        p.line([(x0, y), (x1, y)], fill=(220, 220, 180), width=1)
        p.text(x0 - 4, y, "$%d" % (100 - 20 * i), 9, style="", anchor="rm")
    p.text(x0 - 4, y0, "$100", 9, style="", anchor="rm")
    p.text(x0 - 4, y1, "$0", 9, style="", anchor="rm")
    months = ["AUG", "SEP", "OCT", "NOV", "DEC"]
    for i, m in enumerate(months):
        x = x0 + (x1 - x0) * (i + 0.5) / 5.0
        p.text(x, y1 + 4, m + " '99", 9, style="b", anchor="mt")
    random.seed(1999)
    n = 100
    price, loss = [], []
    v = 11.0
    for i in range(n):
        v += random.uniform(0.1, 1.45)     # it only goes up
        price.append(v)
        loss.append(4 + (i / float(n)) ** 1.6 * 88)
    scale = (87.25 - 11) / (price[-1] - 11)
    price = [11 + (x - 11) * scale for x in price]
    def pts(vals):
        return [(x0 + (x1 - x0) * i / float(n - 1), y1 - (y1 - y0) * v / 100.0) for i, v in enumerate(vals)]
    p.line(pts(loss), fill=(204, 0, 0), width=2.5)
    p.line(pts(price), fill=(0, 150, 0), width=2.5)
    p.text(x1 - 6, y1 - (y1 - y0) * 87.25 / 100.0 - 4, "87 1/4", 10, fill=(0, 120, 0), anchor="rb")
    p.rect(60, 40, 70, 48, fill=(0, 150, 0)); p.text(74, 44, "Share price", 9, style="", anchor="lm")
    p.rect(60, 54, 70, 62, fill=(204, 0, 0)); p.text(74, 58, "Money lost ($ millions)", 9, style="", anchor="lm")
    p.text(W / 2.0, H - 12, "Both lines go up. Our CEO calls this 'synergy.'", 10, fill=(90, 90, 90), style="i", anchor="mm")
    save(img, "chart.gif")


# ===================================================================== MASCOT / VET / LIQUIDATION
def misc():
    img, p = canvas(180, 240, WHITE)
    p.ell(10, 214, 170, 236, fill=(230, 230, 230))
    paste_argyle(img, 0, 0, 236, mood="sing")
    notes(p, 140, 10, 2, col=RED)
    save(img, "argyle_big.gif")
    for pose, mood, hat in (("argyle_party.gif", "happy", "party"),):
        img, p = canvas(120, 160, WHITE)
        paste_argyle(img, 0, 0, 160, mood=mood, hat=hat)
        save(img, pose)
    # vet portrait
    img, p = canvas(90, 110, (255, 255, 230))
    p.rect(0, 0, 89, 109, outline=(102, 153, 0), width=2)
    p.chord(10, 70, 80, 140, 180, 360, fill=WHITE, outline=BLACK, width=1.5)     # lab coat
    p.line([(36, 76), (30, 96), (40, 104)], fill=(60, 60, 60), width=2)            # stethoscope
    p.circ(42, 104, 4, fill=(160, 160, 160), outline=BLACK)
    p.ell(22, 12, 68, 34, fill=(120, 70, 30))                                      # hair
    p.ell(26, 20, 64, 72, fill=(255, 220, 185), outline=BLACK, width=1.5)
    p.ell(18, 26, 34, 70, fill=(120, 70, 30)); p.ell(56, 26, 72, 70, fill=(120, 70, 30))
    p.ell(26, 20, 64, 36, fill=(120, 70, 30))
    p.circ(37, 46, 6, outline=BLACK, width=1.5); p.circ(53, 46, 6, outline=BLACK, width=1.5)
    p.line([(43, 46), (47, 46)], width=1.5)
    p.circ(37, 46, 2, fill=BLACK); p.circ(53, 46, 2, fill=BLACK)
    p.arc(36, 52, 54, 64, 20, 160, fill=(200, 0, 50), width=2)
    save(img, "vet.gif")
    # liquidation banner
    img, p = canvas(415, 80, (255, 255, 0))
    for x in range(-80, 415, 30):
        p.poly([(x, 0), (x + 15, 0), (x + 95, 80), (x + 80, 80)], fill=(255, 230, 0))
    p.rect(0, 0, 414, 79, outline=BLACK, width=3)
    p.text(207, 26, "EVERYTHING MUST GO", 30, fill=(204, 0, 0), style="b", anchor="mm", stroke=1, stroke_fill=BLACK)
    p.text(207, 58, "including us.  90% off.  No returns.  No company.", 13, fill=BLACK, style="bi", anchor="mm")
    save(img, "liq_banner.gif")
    # sad Argyle with sign
    img, p = canvas(200, 220, WHITE)
    p.ell(20, 200, 180, 218, fill=(225, 225, 225))
    paste_argyle(img, 0, 30, 186, mood="sad", flip=False)
    p.line([(148, 120), (148, 210)], fill=(140, 100, 60), width=4)
    p.poly([(110, 60), (198, 56), (196, 124), (112, 128)], fill=(200, 160, 100), outline=(120, 90, 40), width=2)
    p.text(154, 74, "WILL", 13, fill=BLACK, style="b", anchor="mm")
    p.text(154, 92, "FETCH FOR", 11, fill=BLACK, style="b", anchor="mm")
    p.text(154, 110, "FOOD", 13, fill=BLACK, style="b", anchor="mm")
    save(img, "argyle_sad.gif")
    # "closed" stamp for liquidation tabs area
    img, p = canvas(150, 40, WHITE)
    p.rrect(4, 4, 146, 36, 6, outline=(204, 0, 0), width=3)
    p.text(75, 20, "LIQUIDATED", 18, fill=(204, 0, 0), style="b", anchor="mm")
    save(img, "stamp.gif")
    # feature illustrations
    for n, (t, sub, kind, paras) in data.FEATURE_PAGES.items():
        img, p = canvas(120, 100, WHITE)
        p.rrect(1, 1, 118, 98, 10, fill=(240, 248, 220), outline=(153, 204, 51))
        animal(p.sub(16, 6, 0.88), kind)
        if n == 1:
            for x, y in ((14, 18), (96, 70)):
                p.text(x, y, "<3", 12, fill=RED, style="b")
        if n == 2:
            p.text(98, 16, "Y2K", 12, fill=RED, style="b", anchor="mm")
        if n == 3:
            p.text(100, 86, "56k", 12, fill=(0, 0, 150), style="b", anchor="mm")
        save(img, "feature_%d.gif" % n)


def stock():
    src = os.path.join(SITE, "..", "..", "images")
    for f in ("powered_by_kf.gif", "netscape_now.gif", "new.gif"):
        s = os.path.join(src, f)
        if os.path.exists(s):
            shutil.copy(s, os.path.join(OUT, f))


def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    spacer(); spine(); logo(); tabs(); header_buttons(); arrows(); titles(); search_bits(); buttons()
    home_graphics()
    category_banners(); products(); storyboard(); chart(); misc(); stock()
    import midi
    midi.write(os.path.join(OUT, "jingle.mid"))
    print("wrote %d files to images/" % len(os.listdir(OUT)))


if __name__ == "__main__":
    main()
