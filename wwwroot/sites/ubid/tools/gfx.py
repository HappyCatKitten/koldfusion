# -*- coding: utf-8 -*-
"""uBid graphics, drawn procedurally with Pillow: logo, nav buttons, feedback stars, icons,
and a slightly-too-dark 'scanned photo' of every item.  Writes GIFs into ../images/."""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "images")

_FONTS = {
    "sans": ["LiberationSans-Regular.ttf", "DejaVuSans.ttf", "FreeSans.ttf"],
    "sansb": ["LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf", "FreeSansBold.ttf"],
    "dvb": ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "FreeSansBold.ttf"],
    "serifb": ["LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf", "FreeSerifBold.ttf"],
    "serifbi": ["LiberationSerif-BoldItalic.ttf", "DejaVuSerif-BoldItalic.ttf", "FreeSerifBoldItalic.ttf"],
}
_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation",
         "/usr/share/fonts/truetype/freefont", "/usr/share/fonts/TTF", "/Library/Fonts", "C:/Windows/Fonts"]
_cache = {}


def font(kind, size):
    if (kind, size) in _cache:
        return _cache[(kind, size)]
    f = None
    for n in _FONTS[kind]:
        for d in _DIRS:
            if os.path.exists(os.path.join(d, n)):
                f = ImageFont.truetype(os.path.join(d, n), size)
                break
        if f:
            break
    f = f or ImageFont.load_default(size)
    _cache[(kind, size)] = f
    return f


def tsize(d, t, f):
    b = d.textbbox((0, 0), t, font=f)
    return b[2] - b[0], b[3] - b[1]


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def save(im, name, colors=64, transparent=None):
    path = os.path.join(IMG, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    p = im.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    if transparent is not None:
        pal = p.getpalette()[:768]
        bi = min(range(len(pal) // 3), key=lambda i: sum((pal[i * 3 + k] - transparent[k]) ** 2 for k in range(3)))
        p.save(path, transparency=bi)
    else:
        p.save(path)


# ------------------------------------------------------------------ logo
def logo():
    W, H = 150, 64
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    letters = [("u", "#E0218A", 32), ("B", "#0E8C8C", 40), ("i", "#F28C00", 34), ("d", "#6A2DB8", 38)]
    x = 6
    for n, (ch, col, size) in enumerate(letters):
        f = font("dvb", size)
        w, h = tsize(d, ch, f)
        y = 8 + (4 if n % 2 else 0) + (40 - size)
        # chunky black drop shadow, like a cut-out letter
        d.text((x + 2, y + 2), ch, font=f, fill=(40, 40, 40))
        d.text((x, y), ch, font=f, fill=hexc(col))
        x += w - 1
    # gavel
    gx, gy = x + 6, 18
    d.polygon([(gx, gy + 6), (gx + 14, gy - 2), (gx + 19, gy + 7), (gx + 5, gy + 15)], fill=hexc("#8B5A2B"), outline=(60, 30, 10))
    d.line([(gx + 10, gy + 10), (gx + 26, gy + 34)], fill=hexc("#8B5A2B"), width=4)
    d.text((8, 52), "your personal trading post", font=font("sans", 9), fill=(80, 80, 80))
    save(im, "logo.gif", colors=32)
    return W, H


# ------------------------------------------------------------------ navigation buttons
NAV = [("browse", "Browse", "#6A2DB8"), ("sell", "Sell", "#E0218A"), ("services", "Services", "#0E8C8C"),
       ("search", "Search", "#F28C00"), ("help", "Help", "#3366CC"), ("community", "Community", "#339933")]


def nav():
    sizes = {}
    f = font("sansb", 12)
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    for key, label, col in NAV:
        tw, th = tsize(tmp, label, f)
        W, H = tw + 22, 24
        for active in (0, 1):
            im = Image.new("RGB", (W, H), "white")
            d = ImageDraw.Draw(im)
            base = hexc(col)
            fill = base if active else mix(base, (255, 255, 255), 0.82)
            d.rounded_rectangle([1, 1, W - 2, H + 8], radius=9, fill=fill, outline=mix(base, (0, 0, 0), 0.3))
            d.line([(0, H - 1), (W, H - 1)], fill=base)
            d.text(((W - tw) // 2, 5), label, font=f, fill=(255, 255, 255) if active else mix(base, (0, 0, 0), 0.4))
            save(im, "nav/%s_%d.gif" % (key, active), colors=16)
        sizes[key] = (W, H)
    return sizes


# ------------------------------------------------------------------ small icons
def icons():
    # camera "pic" icon used in listings
    im = Image.new("RGB", (22, 14), "white")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([1, 3, 20, 13], radius=2, fill=hexc("#555555"))
    d.rectangle([7, 1, 13, 3], fill=hexc("#555555"))
    d.ellipse([7, 5, 14, 12], fill=hexc("#99CCFF"), outline="white")
    d.rectangle([16, 4, 18, 5], fill=hexc("#FFCC00"))
    save(im, "pic.gif", colors=8)
    # NEW!
    im = Image.new("RGB", (30, 13), "white")
    d = ImageDraw.Draw(im)
    pts = []
    for k in range(16):
        a = k * math.pi / 8
        r = 7 if k % 2 == 0 else 5
        pts.append((15 + 14 * math.cos(a) * r / 7, 6.5 + 6 * math.sin(a) * r / 7))
    d.polygon(pts, fill=hexc("#FFEE00"), outline=hexc("#CC0000"))
    d.text((5, 1), "NEW!", font=font("sansb", 8), fill=hexc("#CC0000"))
    save(im, "new_icon.gif", colors=8)
    # HOT flame
    im = Image.new("RGB", (14, 16), "white")
    d = ImageDraw.Draw(im)
    d.polygon([(7, 0), (12, 7), (12, 12), (9, 15), (4, 15), (1, 12), (2, 6), (5, 9)], fill=hexc("#FF4400"))
    d.polygon([(7, 6), (9, 11), (8, 14), (5, 14), (5, 11)], fill=hexc("#FFCC00"))
    save(im, "hot.gif", colors=8)
    # gift (featured) ribbon
    im = Image.new("RGB", (16, 16), "white")
    d = ImageDraw.Draw(im)
    d.ellipse([2, 1, 13, 12], fill=hexc("#3366CC"))
    d.ellipse([5, 4, 10, 9], fill=hexc("#FFCC00"))
    d.polygon([(4, 10), (2, 15), (6, 13), (7, 11)], fill=hexc("#3366CC"))
    d.polygon([(11, 10), (13, 15), (9, 13), (8, 11)], fill=hexc("#3366CC"))
    save(im, "featured.gif", colors=8)
    # gavel bullet
    im = Image.new("RGB", (14, 14), "white")
    d = ImageDraw.Draw(im)
    d.polygon([(1, 5), (7, 1), (10, 5), (4, 9)], fill=hexc("#8B5A2B"))
    d.line([(6, 6), (13, 13)], fill=hexc("#8B5A2B"), width=2)
    save(im, "gavel.gif", colors=8)
    # clock for "going going gone"
    im = Image.new("RGB", (16, 16), "white")
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, 15, 15], fill=hexc("#FFFFFF"), outline=hexc("#CC0000"), width=2)
    d.line([(7, 7), (7, 3)], fill=(0, 0, 0), width=2)
    d.line([(7, 7), (11, 9)], fill=(0, 0, 0), width=1)
    save(im, "clock.gif", colors=8)


# feedback stars: our own scheme
STARS = [(10, "yellow", "#F5D000"), (50, "green", "#33AA33"), (100, "turquoise", "#22BBBB"),
         (500, "purple", "#8833CC"), (1000, "red", "#DD2222"), (5000, "gold", "#C89B00")]


def stars():
    for minimum, name, col in STARS:
        im = Image.new("RGB", (16, 16), "white")
        d = ImageDraw.Draw(im)
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            r = 7.5 if k % 2 == 0 else 3.2
            pts.append((8 + r * math.cos(a), 8.3 + r * math.sin(a)))
        d.polygon(pts, fill=hexc(col), outline=mix(hexc(col), (0, 0, 0), 0.45))
        if name == "gold":
            d.line([(1, 15), (5, 11)], fill=hexc("#C89B00"), width=2)
        save(im, "stars/star_%s.gif" % name, colors=8)


def promo(name, line1, line2, bg, fg="#FFFFFF", w=128, h=40):
    im = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=8, fill=hexc(bg), outline=mix(hexc(bg), (0, 0, 0), 0.4), width=2)
    f1, f2 = font("sansb", 13), font("sans", 10)
    tw, _ = tsize(d, line1, f1)
    d.text(((w - tw) // 2, 5), line1, font=f1, fill=hexc(fg))
    tw, _ = tsize(d, line2, f2)
    d.text(((w - tw) // 2, 23), line2, font=f2, fill=hexc(fg))
    save(im, name, colors=16)


def header_bar(name, text, bg, w=290, h=22):
    im = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h + 10], radius=10, fill=hexc(bg))
    d.text((10, 3), text, font=font("serifbi", 15), fill=(255, 255, 255))
    save(im, name, colors=16)


# ------------------------------------------------------------------ item "photos"
BACKS = [("#C8B89A", "#B7A584"), ("#9AA5B8", "#8994A8"), ("#D9C9C9", "#C4B2B2"), ("#A9B99A", "#98A889"),
         ("#E6E0D0", "#D4CDBB"), ("#7A6A5A", "#6A5A4A")]


def _bg(rnd, W, H):
    a, b = (hexc(c) for c in rnd.choice(BACKS))
    im = Image.new("RGB", (W, H), a)
    d = ImageDraw.Draw(im)
    style = rnd.randint(0, 2)
    if style == 0:      # bedspread stripes
        for x in range(-H, W, 14):
            d.line([(x, 0), (x + H, H)], fill=b, width=5)
    elif style == 1:    # carpet speckle
        for i in range(900):
            d.point((rnd.randint(0, W - 1), rnd.randint(0, H - 1)), fill=b)
    else:               # tabletop with edge
        d.rectangle([0, int(H * .72), W, H], fill=b)
    return im


def _body(d, rnd, kind, W, H):
    cx, cy = W // 2, H // 2 + 4
    pal = [(220, 40, 40), (40, 90, 200), (240, 190, 20), (40, 160, 70), (150, 60, 190), (240, 120, 30), (240, 240, 240), (30, 30, 30)]
    c1, c2 = rnd.sample(pal, 2)
    dk = lambda c: mix(c, (0, 0, 0), 0.4)  # noqa: E731
    if kind == "beanie":
        d.ellipse([cx - 30, cy - 10, cx + 30, cy + 34], fill=c1, outline=dk(c1))
        d.ellipse([cx - 22, cy - 42, cx + 22, cy + 0], fill=c1, outline=dk(c1))
        d.ellipse([cx - 24, cy - 46, cx - 12, cy - 34], fill=c1, outline=dk(c1))
        d.ellipse([cx + 12, cy - 46, cx + 24, cy - 34], fill=c1, outline=dk(c1))
        d.ellipse([cx - 10, cy - 26, cx - 5, cy - 21], fill=(0, 0, 0))
        d.ellipse([cx + 5, cy - 26, cx + 10, cy - 21], fill=(0, 0, 0))
        d.ellipse([cx - 4, cy - 17, cx + 4, cy - 11], fill=dk(c1))
        d.polygon([(cx + 24, cy - 6), (cx + 40, cy - 14), (cx + 42, cy + 4), (cx + 26, cy + 4)], fill=(230, 30, 60))  # heart tag
        d.text((cx + 28, cy - 10), "TY", font=font("sansb", 7), fill="white") if False else None
    elif kind == "furby":
        d.ellipse([cx - 32, cy - 30, cx + 32, cy + 36], fill=c1, outline=dk(c1))
        d.polygon([(cx - 26, cy - 22), (cx - 40, cy - 52), (cx - 12, cy - 28)], fill=c1, outline=dk(c1))
        d.polygon([(cx + 26, cy - 22), (cx + 40, cy - 52), (cx + 12, cy - 28)], fill=c1, outline=dk(c1))
        for sx in (-1, 1):
            d.ellipse([cx + sx * 14 - 11, cy - 18, cx + sx * 14 + 11, cy + 4], fill="white", outline=(0, 0, 0))
            d.ellipse([cx + sx * 14 - 5, cy - 12, cx + sx * 14 + 5, cy - 2], fill=(20, 20, 120))
        d.polygon([(cx - 8, cy + 6), (cx + 8, cy + 6), (cx, cy + 16)], fill=(240, 160, 30))
    elif kind == "tamagotchi":
        d.ellipse([cx - 28, cy - 36, cx + 28, cy + 34], fill=c1, outline=dk(c1), width=2)
        d.rectangle([cx - 16, cy - 18, cx + 16, cy + 6], fill=(170, 190, 150), outline=(60, 60, 60))
        d.rectangle([cx - 4, cy - 10, cx + 4, cy - 2], fill=(40, 40, 40))
        for i in range(3):
            d.ellipse([cx - 14 + i * 11, cy + 14, cx - 8 + i * 11, cy + 20], fill=c2)
        d.line([(cx, cy - 36), (cx, cy - 48)], fill=(120, 120, 120), width=3)
        d.ellipse([cx - 6, cy - 54, cx + 6, cy - 44], outline=(160, 160, 160), width=2)
    elif kind in ("pokecard", "card"):
        for i in range(3 if kind == "card" else 1):
            ox = (i - 1) * 16
            d.rectangle([cx - 24 + ox, cy - 36 + i * 3, cx + 24 + ox, cy + 32 + i * 3], fill=(250, 220, 60) if kind == "pokecard" else (245, 245, 245), outline=(80, 80, 80))
            d.rectangle([cx - 19 + ox, cy - 28 + i * 3, cx + 19 + ox, cy + 2 + i * 3], fill=c1)
            d.ellipse([cx - 9 + ox, cy - 22 + i * 3, cx + 9 + ox, cy - 4 + i * 3], fill=c2)
            d.line([(cx - 18 + ox, cy + 10 + i * 3), (cx + 18 + ox, cy + 10 + i * 3)], fill=(90, 90, 90))
            d.line([(cx - 18 + ox, cy + 18 + i * 3), (cx + 10 + ox, cy + 18 + i * 3)], fill=(90, 90, 90))
    elif kind == "yoyo":
        d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=c1, outline=dk(c1), width=2)
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=c2)
        d.line([(cx, cy), (cx + 40, cy - 50)], fill=(250, 250, 250), width=1)
    elif kind in ("actionfig", "doll"):
        skin = (240, 200, 160)
        d.ellipse([cx - 11, cy - 46, cx + 11, cy - 24], fill=skin, outline=(120, 90, 60))
        if kind == "doll":
            d.pieslice([cx - 15, cy - 50, cx + 15, cy - 18], 180, 360, fill=rnd.choice([(250, 220, 100), (110, 60, 20), (200, 60, 20)]))
            d.polygon([(cx - 8, cy - 22), (cx + 8, cy - 22), (cx + 26, cy + 34), (cx - 26, cy + 34)], fill=c1, outline=dk(c1))
        else:
            d.rectangle([cx - 14, cy - 22, cx + 14, cy + 8], fill=c1, outline=dk(c1))
            d.rectangle([cx - 14, cy + 8, cx - 2, cy + 38], fill=c2)
            d.rectangle([cx + 2, cy + 8, cx + 14, cy + 38], fill=c2)
            d.rectangle([cx - 24, cy - 20, cx - 15, cy + 6], fill=c1)
            d.rectangle([cx + 15, cy - 20, cx + 24, cy + 6], fill=c1)
        d.ellipse([cx - 5, cy - 39, cx - 2, cy - 36], fill=(0, 0, 0))
        d.ellipse([cx + 2, cy - 39, cx + 5, cy - 36], fill=(0, 0, 0))
    elif kind == "pez":
        for i in range(-2, 3):
            x = cx + i * 18
            c = pal[(i + 7) % len(pal)]
            d.rectangle([x - 5, cy - 6, x + 5, cy + 34], fill=c, outline=dk(c))
            d.ellipse([x - 8, cy - 24, x + 8, cy - 6], fill=(240, 200, 160), outline=(100, 70, 40))
    elif kind == "lunchbox":
        d.rectangle([cx - 40, cy - 22, cx + 40, cy + 30], fill=c1, outline=dk(c1), width=2)
        d.rectangle([cx - 32, cy - 14, cx + 32, cy + 20], fill=c2)
        d.arc([cx - 16, cy - 40, cx + 16, cy - 10], 180, 360, fill=(60, 60, 60), width=4)
        d.ellipse([cx - 12, cy - 6, cx + 12, cy + 14], fill=(250, 230, 120))
    elif kind == "mug":
        d.rectangle([cx - 22, cy - 26, cx + 18, cy + 28], fill=(245, 245, 240), outline=(120, 120, 120))
        d.arc([cx + 8, cy - 16, cx + 34, cy + 16], 270, 90, fill=(120, 120, 120), width=5)
        d.text((cx - 16, cy - 8), "2000", font=font("sansb", 12), fill=c1)
    elif kind == "snowglobe":
        d.rectangle([cx - 26, cy + 14, cx + 26, cy + 34], fill=(120, 70, 30))
        d.ellipse([cx - 32, cy - 44, cx + 32, cy + 20], fill=(200, 225, 245), outline=(150, 170, 190), width=2)
        d.polygon([(cx - 12, cy + 8), (cx, cy - 20), (cx + 12, cy + 8)], fill=(30, 120, 50))
        for i in range(25):
            x, y = rnd.randint(cx - 24, cx + 24), rnd.randint(cy - 36, cy + 10)
            d.point((x, y), fill="white")
    elif kind == "button":
        for i in range(7):
            x, y, r = cx + rnd.randint(-40, 40), cy + rnd.randint(-28, 28), rnd.randint(10, 16)
            c = rnd.choice(pal)
            d.ellipse([x - r, y - r, x + r, y + r], fill=c, outline=(250, 250, 250), width=2)
            d.line([(x - r / 2, y), (x + r / 2, y)], fill="white", width=2)
    elif kind == "sign":
        d.rectangle([cx - 46, cy - 30, cx + 46, cy + 26], fill=c1, outline=(240, 240, 240), width=3)
        d.text((cx - 36, cy - 12), rnd.choice(["GAS", "EAT", "OPEN", "SALE", "DINER"]), font=font("sansb", 20), fill="white")
    elif kind in ("zipdisk", "floppy"):
        for i in range(3):
            ox, oy = (i - 1) * 14, (i - 1) * 8
            if kind == "zipdisk":
                d.rectangle([cx - 30 + ox, cy - 30 + oy, cx + 30 + ox, cy + 30 + oy], fill=(40, 90, 170), outline=(20, 40, 80))
                d.rectangle([cx - 18 + ox, cy - 30 + oy, cx + 18 + ox, cy - 14 + oy], fill=(180, 180, 190))
                d.rectangle([cx - 20 + ox, cy + 2 + oy, cx + 20 + ox, cy + 24 + oy], fill=(240, 240, 240))
            else:
                d.rectangle([cx - 28 + ox, cy - 28 + oy, cx + 28 + ox, cy + 28 + oy], fill=c1, outline=(20, 20, 20))
                d.rectangle([cx - 12 + ox, cy - 28 + oy, cx + 14 + ox, cy - 10 + oy], fill=(190, 190, 200))
                d.rectangle([cx - 20 + ox, cy + 2 + oy, cx + 20 + ox, cy + 28 + oy], fill=(250, 250, 250))
    elif kind == "modem":
        d.rounded_rectangle([cx - 46, cy - 12, cx + 46, cy + 18], radius=5, fill=(70, 70, 75), outline=(30, 30, 30))
        for i in range(8):
            d.ellipse([cx - 38 + i * 9, cy - 2, cx - 33 + i * 9, cy + 3], fill=(255, 40, 40) if i % 3 else (60, 230, 60))
    elif kind == "pda":
        d.rounded_rectangle([cx - 22, cy - 42, cx + 22, cy + 38], radius=6, fill=(110, 110, 120), outline=(40, 40, 40))
        d.rectangle([cx - 16, cy - 34, cx + 16, cy + 6], fill=(170, 190, 150))
        for i in range(4):
            d.ellipse([cx - 18 + i * 10, cy + 18, cx - 12 + i * 10, cy + 24], fill=(60, 60, 60))
    elif kind == "computer":
        d.rectangle([cx - 38, cy - 40, cx + 38, cy + 18], fill=(225, 220, 200), outline=(90, 90, 80))
        d.rectangle([cx - 30, cy - 34, cx + 30, cy + 8], fill=(30, 60, 140))
        d.rectangle([cx - 46, cy + 22, cx + 46, cy + 36], fill=(225, 220, 200), outline=(90, 90, 80))
        d.line([(cx - 26, cy - 26), (cx + 4, cy - 26)], fill="white")
    elif kind == "softbox":
        d.polygon([(cx - 30, cy - 36), (cx + 22, cy - 36), (cx + 34, cy - 28), (cx + 34, cy + 36), (cx - 30, cy + 36)], fill=c1, outline=dk(c1))
        d.polygon([(cx + 22, cy - 36), (cx + 34, cy - 28), (cx + 34, cy + 36), (cx + 22, cy + 30)], fill=dk(c1))
        d.ellipse([cx - 20, cy - 20, cx + 12, cy + 12], fill=c2)
    elif kind == "camera":
        d.rounded_rectangle([cx - 40, cy - 20, cx + 40, cy + 26], radius=5, fill=(40, 40, 40))
        d.rectangle([cx - 14, cy - 30, cx + 10, cy - 20], fill=(50, 50, 50))
        d.ellipse([cx - 18, cy - 14, cx + 18, cy + 22], fill=(90, 90, 100), outline=(160, 160, 170), width=3)
        d.ellipse([cx - 8, cy - 4, cx + 8, cy + 12], fill=(20, 30, 70))
        d.rectangle([cx + 24, cy - 16, cx + 34, cy - 10], fill=(230, 230, 230))
    elif kind == "pager":
        d.rounded_rectangle([cx - 30, cy - 18, cx + 30, cy + 22], radius=8, fill=c1 if rnd.random() < .5 else (30, 30, 30))
        d.rectangle([cx - 22, cy - 10, cx + 18, cy + 4], fill=(170, 190, 150))
        d.text((cx - 20, cy - 10), "911", font=font("sansb", 11), fill=(30, 30, 30))
    elif kind == "phone":
        d.rounded_rectangle([cx - 16, cy - 40, cx + 16, cy + 40], radius=6, fill=(50, 50, 60))
        d.rectangle([cx - 11, cy - 30, cx + 11, cy - 12], fill=(170, 190, 150))
        for r in range(4):
            for c in range(3):
                d.rectangle([cx - 10 + c * 8, cy - 4 + r * 9, cx - 5 + c * 8, cy + r * 9], fill=(200, 200, 200))
        d.line([(cx + 10, cy - 40), (cx + 10, cy - 56)], fill=(30, 30, 30), width=3)
    elif kind == "gameboy":
        d.rounded_rectangle([cx - 26, cy - 42, cx + 26, cy + 40], radius=8, fill=(150, 90, 200) if rnd.random() < .5 else (190, 190, 180))
        d.rectangle([cx - 18, cy - 34, cx + 18, cy - 4], fill=(140, 170, 100), outline=(60, 60, 60))
        d.rectangle([cx - 18, cy + 10, cx - 6, cy + 14], fill=(40, 40, 40))
        d.rectangle([cx - 14, cy + 6, cx - 10, cy + 18], fill=(40, 40, 40))
        d.ellipse([cx + 6, cy + 10, cx + 12, cy + 16], fill=(170, 30, 60))
        d.ellipse([cx + 14, cy + 6, cx + 20, cy + 12], fill=(170, 30, 60))
    elif kind == "book":
        for i in range(3):
            c = rnd.choice(pal)
            d.rectangle([cx - 40 + i * 4, cy + 20 - i * 16, cx + 40 - i * 4, cy + 34 - i * 16], fill=c, outline=dk(c))
        d.rectangle([cx - 26, cy - 44, cx + 26, cy - 14], fill=c1, outline=dk(c1))
    elif kind == "vhs":
        for i in range(2):
            d.rectangle([cx - 36 + i * 10, cy - 30 + i * 12, cx + 30 + i * 10, cy + 8 + i * 12], fill=(30, 30, 30), outline=(90, 90, 90))
            d.rectangle([cx - 30 + i * 10, cy - 24 + i * 12, cx + 24 + i * 10, cy - 8 + i * 12], fill=(245, 245, 245))
    elif kind == "cd":
        for i in range(2):
            ox = (i * 2 - 1) * 16
            d.ellipse([cx - 30 + ox, cy - 30, cx + 30 + ox, cy + 30], fill=(210, 210, 225), outline=(140, 140, 160))
            d.ellipse([cx - 6 + ox, cy - 6, cx + 6 + ox, cy + 6], fill=(140, 140, 160))
            d.arc([cx - 24 + ox, cy - 24, cx + 24 + ox, cy + 24], 200, 250, fill=(255, 120, 200), width=3)
    elif kind == "record":
        d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(15, 15, 15))
        for r in range(36, 14, -5):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(45, 45, 45))
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=c1)
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(200, 200, 200))
    elif kind == "coin":
        for i in range(5):
            x, y = cx + rnd.randint(-36, 36), cy + rnd.randint(-24, 24)
            c = rnd.choice([(200, 200, 205), (205, 160, 60), (190, 110, 60)])
            d.ellipse([x - 15, y - 15, x + 15, y + 15], fill=c, outline=mix(c, (0, 0, 0), .4), width=2)
            d.ellipse([x - 8, y - 8, x + 8, y + 8], outline=mix(c, (0, 0, 0), .25))
    elif kind == "stamp":
        for i in range(4):
            x, y = cx - 34 + (i % 2) * 36, cy - 30 + (i // 2) * 34
            d.rectangle([x, y, x + 30, y + 28], fill=(250, 250, 245))
            c = rnd.choice(pal)
            d.rectangle([x + 4, y + 4, x + 26, y + 24], fill=c)
            for k in range(0, 30, 4):
                d.ellipse([x + k - 1, y - 1, x + k + 1, y + 1], fill=(200, 190, 170))
    elif kind == "watch":
        d.rectangle([cx - 10, cy - 50, cx + 10, cy + 50], fill=(60, 40, 30))
        d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=(210, 210, 215), outline=(120, 120, 130), width=3)
        d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(250, 250, 245))
        d.line([(cx, cy), (cx, cy - 15)], fill=(0, 0, 0), width=2)
        d.line([(cx, cy), (cx + 10, cy + 4)], fill=(0, 0, 0), width=2)
    elif kind == "ring":
        d.ellipse([cx - 26, cy - 14, cx + 26, cy + 34], outline=(220, 180, 60), width=6)
        d.polygon([(cx - 10, cy - 14), (cx + 10, cy - 14), (cx + 6, cy - 28), (cx - 6, cy - 28)], fill=(60, 90, 220), outline=(240, 240, 255))
    elif kind in ("vase", "glass"):
        if kind == "vase":
            d.polygon([(cx - 10, cy - 42), (cx + 10, cy - 42), (cx + 8, cy - 30), (cx + 28, cy), (cx + 18, cy + 38),
                       (cx - 18, cy + 38), (cx - 28, cy), (cx - 8, cy - 30)], fill=c1, outline=dk(c1))
            d.line([(cx - 20, cy), (cx + 20, cy)], fill=c2, width=4)
        else:
            for i in range(3):
                x = cx - 34 + i * 34
                c = rnd.choice([(100, 190, 140), (240, 160, 40), (120, 160, 220), (230, 90, 90)])
                d.pieslice([x - 18, cy - 14, x + 18, cy + 24], 0, 180, fill=c, outline=dk(c))
                d.line([(x - 18, cy + 5), (x + 18, cy + 5)], fill=dk(c))
    elif kind == "baseball":
        d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=(250, 250, 240), outline=(170, 170, 160))
        d.arc([cx - 50, cy - 26, cx - 8, cy + 26], 300, 60, fill=(200, 30, 30), width=2)
        d.arc([cx + 8, cy - 26, cx + 50, cy + 26], 120, 240, fill=(200, 30, 30), width=2)
    elif kind == "pennant":
        d.polygon([(cx - 46, cy - 24), (cx + 46, cy), (cx - 46, cy + 24)], fill=c1, outline=dk(c1))
        d.rectangle([cx - 50, cy - 26, cx - 44, cy + 26], fill=(240, 240, 240))
        d.text((cx - 36, cy - 7), rnd.choice(["GO!", "CHAMPS", "1986"]), font=font("sansb", 12), fill="white")
    elif kind == "clock":
        d.polygon([(cx - 34, cy + 36), (cx - 34, cy - 10), (cx, cy - 40), (cx + 34, cy - 10), (cx + 34, cy + 36)], fill=(110, 70, 35), outline=(60, 35, 15))
        d.ellipse([cx - 20, cy - 22, cx + 20, cy + 18], fill=(250, 245, 225), outline=(180, 150, 60), width=2)
        d.line([(cx, cy - 2), (cx, cy - 16)], fill=(0, 0, 0), width=2)
        d.line([(cx, cy - 2), (cx + 10, cy + 2)], fill=(0, 0, 0), width=2)
    elif kind == "painting":
        d.rectangle([cx - 48, cy - 36, cx + 48, cy + 34], fill=(200, 160, 60), outline=(120, 90, 30), width=2)
        d.rectangle([cx - 40, cy - 28, cx + 40, cy + 26], fill=(90, 140, 190))
        d.polygon([(cx - 40, cy + 26), (cx - 40, cy + 4), (cx - 10, cy - 8), (cx + 20, cy + 6), (cx + 40, cy - 2), (cx + 40, cy + 26)], fill=(40, 90, 60))
        d.ellipse([cx + 14, cy - 24, cx + 28, cy - 10], fill=(250, 220, 90))
    elif kind == "lamp":
        d.polygon([(cx - 30, cy - 4), (cx - 14, cy - 40), (cx + 14, cy - 40), (cx + 30, cy - 4)], fill=c1, outline=dk(c1))
        d.rectangle([cx - 3, cy - 4, cx + 3, cy + 28], fill=(150, 120, 60))
        d.ellipse([cx - 20, cy + 26, cx + 20, cy + 36], fill=(150, 120, 60))
    elif kind == "kit":
        d.rectangle([cx - 40, cy - 26, cx + 40, cy + 34], fill=(230, 190, 60), outline=(120, 90, 20), width=2)
        d.rectangle([cx - 40, cy - 26, cx + 40, cy - 10], fill=(200, 40, 40))
        d.text((cx - 22, cy - 25), "Y2K", font=font("sansb", 13), fill="white")
        d.text((cx - 34, cy - 4), "SURVIVAL", font=font("sansb", 11), fill=(60, 40, 0))
        d.text((cx - 18, cy + 12), "KIT", font=font("sansb", 13), fill=(60, 40, 0))
    else:  # box
        d.polygon([(cx - 40, cy - 14), (cx, cy - 34), (cx + 40, cy - 14), (cx, cy + 6)], fill=(205, 170, 120), outline=(120, 90, 50))
        d.polygon([(cx - 40, cy - 14), (cx, cy + 6), (cx, cy + 40), (cx - 40, cy + 20)], fill=(180, 145, 95), outline=(120, 90, 50))
        d.polygon([(cx + 40, cy - 14), (cx, cy + 6), (cx, cy + 40), (cx + 40, cy + 20)], fill=(160, 125, 80), outline=(120, 90, 50))
        d.text((cx - 4, cy - 22), "?", font=font("sansb", 16), fill=(90, 60, 20))


def item_photo(item_id, kind, seed):
    rnd = random.Random(seed)
    W, H = 160, 120
    im = _bg(rnd, W, H)
    d = ImageDraw.Draw(im)
    # shadow under the item
    d.ellipse([W // 2 - 44, H // 2 + 28, W // 2 + 44, H // 2 + 44], fill=mix(im.getpixel((2, H - 3)), (0, 0, 0), 0.35))
    _body(d, rnd, kind, W, H)
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    # 1999 photography: too dark, a flash glare, and a date stamp in the corner
    px = im.load()
    dim = rnd.uniform(0.72, 0.92)
    gx, gy = rnd.randint(30, 130), rnd.randint(20, 60)
    for y in range(H):
        for x in range(W):
            r, g, b = px[x, y]
            glare = max(0.0, 1 - ((x - gx) ** 2 + (y - gy) ** 2) / 900.0) * 90
            px[x, y] = (min(255, int(r * dim + glare)), min(255, int(g * dim + glare)), min(255, int(b * dim * 0.97 + glare)))
    d = ImageDraw.Draw(im)
    if rnd.random() < .5:
        d.text((W - 62, H - 13), "'99 10 %02d" % rnd.randint(1, 28), font=font("sansb", 9), fill=(255, 140, 0))
    save(im, "items/%s.gif" % item_id, colors=96)
    save(im.resize((80, 60), Image.LANCZOS), "items/%s_t.gif" % item_id, colors=64)


def all_static():
    os.makedirs(IMG, exist_ok=True)
    sizes = {"logo": logo(), "nav": nav()}
    icons()
    stars()
    promo("promo_sell.gif", "Sell your item!", "it's quick and easy", "#E0218A")
    promo("promo_new.gif", "New to uBid?", "start here", "#0E8C8C")
    promo("promo_register.gif", "Register", "it's free!", "#6A2DB8")
    promo("promo_gone.gif", "Going, going...", "gone! ending soon", "#F28C00")
    header_bar("h_featured.gif", "Featured Auctions", "#6A2DB8")
    header_bar("h_categories.gif", "Categories", "#0E8C8C", w=169)
    header_bar("h_gone.gif", "Going, Going, Gone!", "#F28C00")
    return sizes


if __name__ == "__main__":
    print(all_static())
