# -*- coding: utf-8 -*-
"""Orinoco.com graphics, all drawn procedurally with Pillow (no original artwork).

Writes GIFs into ../images/.  Called from build.py; can also be run alone.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "images")

_FONTS = {
    "sans": ["DejaVuSans.ttf", "LiberationSans-Regular.ttf", "FreeSans.ttf"],
    "sansb": ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "FreeSansBold.ttf"],
    "arialb": ["LiberationSans-Bold.ttf", "FreeSansBold.ttf", "DejaVuSans-Bold.ttf"],
    "arial": ["LiberationSans-Regular.ttf", "FreeSans.ttf", "DejaVuSans.ttf"],
    "serif": ["LiberationSerif-Regular.ttf", "DejaVuSerif.ttf", "FreeSerif.ttf"],
    "serifb": ["LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf", "FreeSerifBold.ttf"],
    "serifi": ["LiberationSerif-Italic.ttf", "DejaVuSerif-Italic.ttf", "FreeSerifItalic.ttf"],
    "serifbi": ["LiberationSerif-BoldItalic.ttf", "DejaVuSerif-BoldItalic.ttf", "FreeSerifBoldItalic.ttf"],
}
_FONT_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation",
              "/usr/share/fonts/truetype/freefont", "/usr/share/fonts/TTF", "/Library/Fonts",
              "C:/Windows/Fonts"]
_cache = {}


def font(kind, size):
    key = (kind, size)
    if key in _cache:
        return _cache[key]
    f = None
    for name in _FONTS[kind]:
        for d in _FONT_DIRS:
            p = os.path.join(d, name)
            if os.path.exists(p):
                f = ImageFont.truetype(p, size)
                break
        if f:
            break
    if f is None:
        f = ImageFont.load_default(size)
    _cache[key] = f
    return f


def tsize(draw, text, fnt):
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def save(im, name, colors=64, transparent=None):
    path = os.path.join(IMG, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    p = im.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    if transparent is not None:
        # make the palette entry closest to `transparent` see-through
        pal = p.getpalette()[:768]
        best, bi = 1e9, 0
        for i in range(len(pal) // 3):
            d = sum((pal[i * 3 + k] - transparent[k]) ** 2 for k in range(3))
            if d < best:
                best, bi = d, i
        p.save(path, transparency=bi)
    else:
        p.save(path)


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------- logo
def logo():
    W, H = 172, 58
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    f = font("serifb", 30)
    d.text((6, 4), "orinoco", font=f, fill=(0, 0, 0))
    w, _ = tsize(d, "orinoco", f)
    d.text((8 + w, 16), ".com", font=font("serifb", 16), fill=(0, 0, 0))
    # the river: a wavy blue-green band under the name, widening to the right
    for x in range(8, W - 6):
        t = (x - 8) / float(W - 14)
        y = 44 + 4 * math.sin(t * 3.3 * math.pi)
        thick = 1.5 + 3.5 * t
        c = mix(hexc("#2e8b57"), hexc("#1f5fa8"), t)
        d.line([(x, y - thick / 2), (x, y + thick / 2)], fill=c)
    # little delta at the end
    d.polygon([(W - 9, 38), (W - 2, 44), (W - 9, 50)], fill=hexc("#1f5fa8"))
    d.text((10, 49), "EARTH'S BIGGEST BOOKSTORE", font=font("sansb", 7), fill=(90, 90, 90))
    save(im, "logo.gif")


# ---------------------------------------------------------------- folder tabs
TABS = [
    ("welcome", "WELCOME", "#336699"),
    ("books", "BOOKS", "#006666"),
    ("music", "MUSIC", "#663399"),
    ("video", "VIDEO", "#993333"),
    ("toys", "TOYS & GAMES", "#CC6600"),
    ("auctions", "AUCTIONS", "#666633"),
    ("ecards", "e-CARDS", "#996699"),
]


def tab(key, label, color, active):
    f = font("sansb", 9)
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw, th = tsize(tmp, label, f)
    W, H = tw + 24, 22 if active else 20
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    base = hexc(color)
    fill = base if active else mix(base, (255, 255, 255), 0.72)
    edge = mix(base, (0, 0, 0), 0.35)
    r = 6
    poly = [(0, H), (4, r), (4 + r, 0), (W - 5 - r, 0), (W - 5, r), (W - 1, H)]
    d.polygon(poly, fill=fill)
    d.pieslice([4, 0, 4 + 2 * r, 2 * r], 180, 270, fill=fill)
    d.pieslice([W - 5 - 2 * r, 0, W - 5, 2 * r], 270, 360, fill=fill)
    d.rectangle([4 + r, 0, W - 5 - r, r], fill=fill)
    d.line([(0, H - 1), (4, r)], fill=edge)
    d.arc([4, 0, 4 + 2 * r, 2 * r], 180, 270, fill=edge)
    d.line([(4 + r, 0), (W - 5 - r, 0)], fill=edge)
    d.arc([W - 5 - 2 * r, 0, W - 5, 2 * r], 270, 360, fill=edge)
    d.line([(W - 5, r), (W - 1, H - 1)], fill=edge)
    tc = (255, 255, 255) if active else mix(base, (0, 0, 0), 0.45)
    d.text(((W - tw) // 2, (H - th) // 2 + (1 if active else 0)), label, font=f, fill=tc)
    save(im, "tabs/%s_%s.gif" % (key, "on" if active else "off"), colors=32)
    return W, H


def tabs():
    sizes = {}
    for key, label, color in TABS:
        sizes[key] = (tab(key, label, color, False), tab(key, label, color, True))
    return sizes


# ---------------------------------------------------------------- small buttons
def pill(name, text, bg, fg=(0, 0, 0), size=10, w=None, h=None, bold=True, border=(80, 80, 80), grad=None):
    f = font("sansb" if bold else "sans", size)
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw, th = tsize(tmp, text, f)
    W = w or tw + 22
    H = h or th + 10
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    top = hexc(bg)
    bot = hexc(grad) if grad else mix(top, (0, 0, 0), 0.18)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, H - 1], radius=H // 2 - 1, fill=255)
    g = Image.new("RGB", (W, H))
    gd = ImageDraw.Draw(g)
    for y in range(H):
        gd.line([(0, y), (W, y)], fill=mix(top, bot, y / float(H)))
    im.paste(g, (0, 0), mask)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=H // 2 - 1, outline=border)
    d.text(((W - tw) // 2, (H - th) // 2 - 1), text, font=f, fill=fg)
    save(im, name, colors=64)
    return W, H


def go_arrow():
    im = Image.new("RGB", (21, 21), "white")
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, 20, 20], fill=hexc("#CC6600"), outline=hexc("#884400"))
    d.polygon([(7, 5), (15, 10), (7, 15)], fill="white")
    save(im, "go.gif", colors=16)
    im = Image.new("RGB", (12, 11), "white")
    d = ImageDraw.Draw(im)
    d.polygon([(2, 1), (10, 5), (2, 9)], fill=hexc("#CC6600"))
    save(im, "arrow.gif", colors=8)


def topbuttons():
    # VIEW CART | YOUR ACCOUNT | HELP, Orinoco-style little capsule icons
    items = [("btn_cart.gif", "VIEW CART", "cart"), ("btn_account.gif", "YOUR ACCOUNT", "acct"),
             ("btn_help.gif", "HELP", "help")]
    out = {}
    for name, text, kind in items:
        f = font("sansb", 8)
        tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        tw, th = tsize(tmp, text, f)
        W, H = tw + 30, 19
        im = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 1, W - 1, H - 2], radius=8, fill=hexc("#EEEECC"), outline=hexc("#999966"))
        # icon
        ix, iy = 5, 4
        if kind == "cart":
            d.rectangle([ix, iy + 2, ix + 11, iy + 7], outline=(0, 0, 0))
            d.line([(ix - 2, iy), (ix, iy + 2)], fill=(0, 0, 0))
            d.ellipse([ix + 1, iy + 8, ix + 3, iy + 10], fill=(0, 0, 0))
            d.ellipse([ix + 8, iy + 8, ix + 10, iy + 10], fill=(0, 0, 0))
        elif kind == "acct":
            d.ellipse([ix + 3, iy, ix + 8, iy + 5], fill=hexc("#336699"))
            d.pieslice([ix, iy + 5, ix + 11, iy + 16], 180, 360, fill=hexc("#336699"))
        else:
            d.ellipse([ix, iy, ix + 11, iy + 11], fill=hexc("#CC6600"))
            d.text((ix + 3, iy - 1), "?", font=font("sansb", 10), fill="white")
        d.text((ix + 17, (H - th) // 2 - 1), text, font=f, fill=hexc("#333333"))
        save(im, name, colors=32)
        out[name] = (W, H)
    return out


# ---------------------------------------------------------------- star ratings
def stars():
    for tenths in range(0, 51, 5):
        v = tenths / 10.0
        W, H = 64, 13
        im = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(im)
        for i in range(5):
            cx, cy, R, r = 6 + i * 13, 6.5, 6, 2.6
            pts = []
            for k in range(10):
                a = -math.pi / 2 + k * math.pi / 5
                rr = R if k % 2 == 0 else r
                pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
            fillv = max(0.0, min(1.0, v - i))
            d.polygon(pts, fill=hexc("#E8E8E8"), outline=hexc("#BBBBBB"))
            if fillv > 0:
                star = Image.new("L", (W, H), 0)
                ImageDraw.Draw(star).polygon(pts, fill=255)
                clip = Image.new("L", (W, H), 0)
                ImageDraw.Draw(clip).rectangle([0, 0, cx - R + 2 * R * fillv, H], fill=255)
                from PIL import ImageChops
                m = ImageChops.multiply(star, clip)
                im.paste(hexc("#FF9900"), (0, 0), m)
                d.polygon(pts, outline=hexc("#CC6600"))
        save(im, "stars/stars-%d-%d.gif" % (tenths // 10, tenths % 10), colors=16)


# ---------------------------------------------------------------- covers
PALETTES = {
    "comp": [("#1b2a49", "#4fc3f7"), ("#003300", "#33ff66"), ("#202020", "#ffcc00"), ("#2d1b69", "#ff66cc")],
    "biz": [("#0b3d2e", "#e6c35c"), ("#1c2833", "#d4ac0d"), ("#ffffff", "#145a32"), ("#7b241c", "#f7dc6f")],
    "myst": [("#0a0a0a", "#c0392b"), ("#1a1a2e", "#e0e0e0"), ("#2c3e50", "#f39c12"), ("#3b0a0a", "#f5f5dc")],
    "scifi": [("#000022", "#00e5ff"), ("#14002b", "#ff9100"), ("#001a1a", "#76ff03"), ("#1a0033", "#e1bee7")],
    "lit": [("#f4ecd8", "#5d4037"), ("#e8d5b7", "#1b5e20"), ("#dfe6e9", "#2d3436"), ("#fdebd0", "#922b21")],
    "health": [("#e8f8f5", "#117a65"), ("#fef9e7", "#d35400"), ("#eaf2f8", "#1f618d"), ("#f9ebea", "#943126")],
    "cook": [("#fdf2e9", "#c0392b"), ("#fffde7", "#e65100"), ("#f1f8e9", "#33691e"), ("#fce4ec", "#880e4f")],
    "kids": [("#fff176", "#d32f2f"), ("#81d4fa", "#1a237e"), ("#a5d6a7", "#e65100"), ("#f8bbd0", "#4a148c")],
    "hist": [("#d7c4a3", "#3e2723"), ("#bcaaa4", "#212121"), ("#cfd8dc", "#263238"), ("#e0c9a6", "#4e342e")],
    "ref": [("#0d47a1", "#ffffff"), ("#b71c1c", "#ffffff"), ("#1b5e20", "#fff59d"), ("#212121", "#ffd54f")],
    "rom": [("#f8bbd0", "#880e4f"), ("#e1bee7", "#4a148c"), ("#ffcdd2", "#b71c1c"), ("#fff3e0", "#ad1457")],
    "travel": [("#81d4fa", "#e65100"), ("#ffe0b2", "#01579b"), ("#c8e6c9", "#004d40"), ("#fff9c4", "#bf360c")],
    "music": [("#111111", "#ff4081"), ("#ffeb3b", "#212121"), ("#311b92", "#80deea"), ("#e0e0e0", "#d50000")],
    "video": [("#000000", "#ffd600"), ("#263238", "#ff5252"), ("#0d0d0d", "#18ffff"), ("#3e2723", "#ffe0b2")],
}


def wrap(d, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tsize(d, t, fnt)[0] <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _motif(d, rnd, subj, W, H, bg, fg):
    acc = mix(fg, bg, 0.55)
    if subj == "comp":
        for i in range(14):
            x, y = rnd.randint(0, W), rnd.randint(int(H * .45), H)
            d.line([(x, y), (x + rnd.choice([-30, 30]), y)], fill=acc)
            d.line([(x, y), (x, y + rnd.choice([-20, 20]))], fill=acc)
            d.rectangle([x - 2, y - 2, x + 2, y + 2], fill=fg)
    elif subj == "biz":
        pts = [(10, H - 30)]
        for i in range(1, 8):
            pts.append((10 + i * (W - 20) / 7.0, H - 30 - i * 9 - rnd.randint(-6, 6)))
        d.line(pts, fill=fg, width=3)
        d.polygon([pts[-1], (pts[-1][0] - 9, pts[-1][1] + 2), (pts[-1][0] - 3, pts[-1][1] + 9)], fill=fg)
    elif subj == "myst":
        d.polygon([(0, H), (W, int(H * .45)), (W, int(H * .55)), (0, H)], fill=acc)
        cx = rnd.randint(30, W - 30)
        d.ellipse([cx - 14, H - 70, cx + 14, H - 42], outline=fg, width=2)
        d.line([(cx + 10, H - 46), (cx + 24, H - 30)], fill=fg, width=4)
    elif subj == "scifi":
        for i in range(60):
            x, y = rnd.randint(0, W), rnd.randint(0, H)
            d.point((x, y), fill=(255, 255, 255))
        r = rnd.randint(22, 36)
        cx, cy = rnd.randint(r, W - r), H - r - 10
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=acc, outline=fg)
        d.arc([cx - r - 12, cy - 8, cx + r + 12, cy + 8], 160, 380, fill=fg, width=2)
    elif subj == "lit":
        d.rectangle([12, int(H * .48), W - 12, H - 30], outline=fg)
        for i in range(5):
            y = int(H * .52) + i * 9
            d.line([(20, y), (W - 20 - rnd.randint(0, 25), y)], fill=acc)
    elif subj == "health":
        cx, cy = W // 2, int(H * .72)
        d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=fg)
        for k in range(12):
            a = k * math.pi / 6
            d.line([(cx + 22 * math.cos(a), cy + 22 * math.sin(a)), (cx + 32 * math.cos(a), cy + 32 * math.sin(a))], fill=fg, width=2)
    elif subj == "cook":
        s = 12
        for y in range(int(H * .55), H, s):
            for x in range(0, W, s):
                if ((x // s) + (y // s)) % 2 == 0:
                    d.rectangle([x, y, x + s - 1, y + s - 1], fill=acc)
        d.ellipse([W // 2 - 26, int(H * .62), W // 2 + 26, int(H * .62) + 22], fill=(255, 255, 255), outline=fg)
    elif subj == "kids":
        for i in range(9):
            r = rnd.randint(6, 16)
            x, y = rnd.randint(0, W), rnd.randint(int(H * .45), H)
            c = rnd.choice([(255, 82, 82), (68, 138, 255), (255, 214, 0), (0, 200, 83), (170, 0, 255)])
            d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    elif subj == "hist":
        cx = W // 2
        d.rectangle([cx - 28, int(H * .5), cx + 28, int(H * .5) + 6], fill=fg)
        for i in range(4):
            x = cx - 22 + i * 14
            d.rectangle([x, int(H * .5) + 6, x + 6, H - 36], fill=acc)
        d.rectangle([cx - 32, H - 36, cx + 32, H - 30], fill=fg)
    elif subj == "ref":
        d.rectangle([0, int(H * .5), W, int(H * .5) + 4], fill=fg)
        d.rectangle([0, H - 40, W, H - 38], fill=fg)
    elif subj == "rom":
        for i in range(5):
            x, y, r = rnd.randint(15, W - 15), rnd.randint(int(H * .5), H - 30), rnd.randint(5, 11)
            d.ellipse([x - r, y - r, x, y], fill=fg)
            d.ellipse([x, y - r, x + r, y], fill=fg)
            d.polygon([(x - r, y - r / 2), (x + r, y - r / 2), (x, y + r)], fill=fg)
    elif subj == "travel":
        hy = int(H * .7)
        d.rectangle([0, hy, W, H], fill=acc)
        d.ellipse([W - 50, hy - 26, W - 14, hy + 10], fill=fg)
        d.rectangle([0, hy, W, H], fill=acc)
        d.polygon([(20, hy), (45, hy - 30), (70, hy)], fill=fg)
    elif subj == "music":
        cx, cy = W // 2, int(H * .6)
        for r in range(40, 4, -6):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=acc)
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=fg)
    elif subj == "video":
        for i in range(0, W, 14):
            d.rectangle([i + 2, 4, i + 9, 10], fill=acc)
            d.rectangle([i + 2, H - 10, i + 9, H - 4], fill=acc)


def cover(code, title, author, subj, seed, kind="book"):
    rnd = random.Random(seed)
    if kind == "music":
        W, H = 120, 120
    elif kind == "video":
        W, H = 110, 160
    else:
        W, H = 120, 180
    bg, fg = (hexc(c) for c in rnd.choice(PALETTES[subj]))
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    _motif(d, rnd, subj, W, H, bg, fg)
    style = rnd.randint(0, 2)
    tf = font(rnd.choice(["serifb", "sansb", "serifbi"]) if subj not in ("comp", "ref") else "sansb", 13 if kind != "music" else 11)
    short = title.split(":")[0]
    lines = wrap(d, short, tf, W - 16)[:5]
    y = 10
    if style == 1 and kind == "book":
        d.rectangle([0, 6, W, 6 + 17 * len(lines) + 8], fill=fg)
        tcol = bg
    else:
        tcol = fg
    for ln in lines:
        tw, th = tsize(d, ln, tf)
        d.text(((W - tw) // 2, y), ln, font=tf, fill=tcol)
        y += 17 if kind != "music" else 14
    af = font("sans", 9)
    al = wrap(d, author.upper(), af, W - 12)[:2]
    y = H - 12 - 11 * len(al)
    if kind == "music":
        y = H - 8 - 11 * len(al)
    for ln in al:
        tw, th = tsize(d, ln, af)
        d.rectangle([(W - tw) // 2 - 2, y - 1, (W + tw) // 2 + 2, y + 10], fill=bg)
        d.text(((W - tw) // 2, y), ln, font=af, fill=fg)
        y += 11
    # spine shading for books
    if kind == "book":
        for x in range(5):
            d.line([(x, 0), (x, H)], fill=mix(bg, (0, 0, 0), 0.35 - x * 0.06))
    d.rectangle([0, 0, W - 1, H - 1], outline=mix(bg, (0, 0, 0), 0.5))
    save(im, "covers/%s.gif" % code, colors=64)
    sm = im.resize((W // 2, H // 2), Image.LANCZOS)
    save(sm, "covers/%s_s.gif" % code, colors=64)
    return (W, H)


# ---------------------------------------------------------------- misc art
def headers():
    # section header bars ("Orinoco.com 100 Hot Books" etc. are text; these are icons)
    im = Image.new("RGB", (44, 47), "white")
    d = ImageDraw.Draw(im)
    # a gift box for Wish Lists
    d.rectangle([6, 18, 38, 44], fill=hexc("#CC3333"), outline=hexc("#661111"))
    d.rectangle([4, 12, 40, 19], fill=hexc("#DD4444"), outline=hexc("#661111"))
    d.rectangle([19, 12, 25, 44], fill=hexc("#FFCC00"))
    d.ellipse([10, 2, 22, 13], outline=hexc("#FFCC00"), width=3)
    d.ellipse([22, 2, 34, 13], outline=hexc("#FFCC00"), width=3)
    save(im, "giftbox.gif", colors=16)
    # "Hot 100" flame badge
    im = Image.new("RGB", (40, 40), "white")
    d = ImageDraw.Draw(im)
    d.polygon([(20, 2), (30, 16), (34, 28), (28, 38), (12, 38), (6, 28), (12, 18), (16, 22)], fill=hexc("#FF6600"))
    d.polygon([(20, 14), (26, 26), (24, 36), (16, 36), (14, 28)], fill=hexc("#FFCC00"))
    d.text((9, 25), "100", font=font("sansb", 9), fill=hexc("#660000"))
    save(im, "hot100.gif", colors=16)
    # padlock for secure checkout
    im = Image.new("RGB", (20, 24), "white")
    d = ImageDraw.Draw(im)
    d.arc([4, 1, 15, 14], 180, 360, fill=hexc("#996600"), width=3)
    d.line([(5, 8), (5, 11)], fill=hexc("#996600"), width=3)
    d.line([(14, 8), (14, 11)], fill=hexc("#996600"), width=3)
    d.rectangle([2, 10, 17, 22], fill=hexc("#FFCC33"), outline=hexc("#996600"))
    d.ellipse([8, 13, 11, 16], fill=(60, 40, 0))
    save(im, "lock.gif", colors=16)
    # e-card fronts
    cards = [("card_birthday", "#FFE0F0", "Happy Birthday!", "#CC0066"),
             ("card_y2k", "#E0F0FF", "See You in 2000!", "#003399"),
             ("card_thanks", "#F0FFE0", "Thank You!", "#336600"),
             ("card_hello", "#FFF8DC", "Just Saying Hi", "#996600")]
    for name, bg, text, fg in cards:
        rnd = random.Random(name)
        im = Image.new("RGB", (150, 100), hexc(bg))
        d = ImageDraw.Draw(im)
        for i in range(25):
            x, y = rnd.randint(0, 150), rnd.randint(0, 100)
            c = rnd.choice([(255, 102, 102), (102, 153, 255), (255, 204, 0), (102, 204, 102)])
            r = rnd.randint(2, 5)
            d.ellipse([x - r, y - r, x + r, y + r], fill=c)
        f = font("serifbi", 17)
        tw, th = tsize(d, text, f)
        d.rectangle([(150 - tw) // 2 - 6, 38, (150 + tw) // 2 + 6, 38 + th + 10], fill=(255, 255, 255), outline=hexc(fg))
        d.text(((150 - tw) // 2, 41), text, font=f, fill=hexc(fg))
        d.rectangle([0, 0, 149, 99], outline=hexc(fg))
        save(im, name + ".gif", colors=32)
    # a tiny "pointing finger" for 1-Click
    im = Image.new("RGB", (16, 16), "white")
    d = ImageDraw.Draw(im)
    d.rectangle([6, 1, 9, 9], fill=(255, 220, 180), outline=(120, 80, 40))
    d.rounded_rectangle([3, 7, 13, 15], radius=3, fill=(255, 220, 180), outline=(120, 80, 40))
    save(im, "finger.gif", colors=8)


def all_static():
    os.makedirs(IMG, exist_ok=True)
    logo()
    sizes = {"tabs": tabs(), "top": topbuttons()}
    go_arrow()
    stars()
    headers()
    b = {}
    b["addcart"] = pill("btn_addcart.gif", "add to Shopping Cart", "#FFE38A", grad="#F2B400", size=10)
    b["oneclick"] = pill("btn_1click.gif", "Buy now with 1-Click", "#C9DDF2", grad="#7FA8D6", size=10)
    b["checkout"] = pill("btn_checkout.gif", "Proceed to Checkout", "#FFE38A", grad="#F2B400", size=11)
    b["update"] = pill("btn_update.gif", "Update", "#EEEECC", grad="#CCCC99", size=10)
    b["continue"] = pill("btn_continue.gif", "Continue", "#FFE38A", grad="#F2B400", size=11)
    b["placeorder"] = pill("btn_placeorder.gif", "Place Your Order", "#FFE38A", grad="#F2B400", size=12)
    b["signin"] = pill("btn_signin.gif", "Sign in using our secure server", "#FFE38A", grad="#F2B400", size=10)
    b["search"] = pill("btn_search.gif", "Search", "#EEEECC", grad="#CCCC99", size=10)
    b["wishlist"] = pill("btn_wishlist.gif", "Add to Wish List", "#EEEECC", grad="#CCCC99", size=9)
    b["send"] = pill("btn_send.gif", "Send this e-Card", "#FFE38A", grad="#F2B400", size=11)
    sizes["buttons"] = b
    return sizes


if __name__ == "__main__":
    print(all_static())
