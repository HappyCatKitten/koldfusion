# -*- coding: utf-8 -*-
"""eToyz graphics, drawn procedurally with Pillow: the toy-block logo, tabs, Sprocket the
robot mascot (an animated GIF, naturally), age badges, buttons, banners and a product shot
of every toy.  Also writes Sprocket's theme song as a tiny MIDI file."""
import math
import os
import random
import struct

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "images")

_FONTS = {
    "sans": ["LiberationSans-Regular.ttf", "DejaVuSans.ttf", "FreeSans.ttf"],
    "sansb": ["LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf", "FreeSansBold.ttf"],
    "dvb": ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "FreeSansBold.ttf"],
    "serifbi": ["LiberationSerif-BoldItalic.ttf", "DejaVuSerif-BoldItalic.ttf", "FreeSerifBoldItalic.ttf"],
}
_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation",
         "/usr/share/fonts/truetype/freefont", "/usr/share/fonts/TTF", "/Library/Fonts", "C:/Windows/Fonts"]
_cache = {}

RED, BLUE, YEL, GRN, ORA, PUR = (226, 27, 27), (27, 95, 226), (255, 210, 27), (27, 168, 74), (255, 128, 0), (140, 60, 200)


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


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def dk(c, t=0.35):
    return mix(c, (0, 0, 0), t)


def save(im, name, colors=64):
    path = os.path.join(IMG, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(path)


# ------------------------------------------------------------------ logo: letters on toy blocks
def logo():
    W, H = 200, 70
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    blocks = [("e", RED, -6), ("T", BLUE, 4), ("o", YEL, -3), ("y", GRN, 5), ("z", ORA, -4)]
    x = 4
    for n, (ch, col, ang) in enumerate(blocks):
        s = 36
        blk = Image.new("RGBA", (s + 8, s + 8), (0, 0, 0, 0))
        bd = ImageDraw.Draw(blk)
        bd.rectangle([6, 6, s + 6, s + 6], fill=dk(col, .5))           # 3-D side
        bd.rectangle([2, 2, s + 2, s + 2], fill=col, outline=dk(col, .5), width=2)
        bd.rectangle([5, 5, s - 1, s - 1], outline=mix(col, (255, 255, 255), .5))
        f = font("dvb", 26)
        tw, th = tsize(bd, ch, f)
        bb = bd.textbbox((0, 0), ch, font=f)
        tc = (40, 40, 40) if col == YEL else (255, 255, 255)
        bd.text((2 + (s - tw) // 2 - bb[0], 2 + (s - th) // 2 - bb[1]), ch, font=f, fill=tc)
        blk = blk.rotate(ang, resample=Image.BICUBIC, expand=False)
        im.paste(blk, (x, 6 + (n % 2) * 6), blk)
        x += 37
    d.text((8, 56), "toys delivered to your door!", font=font("sansb", 10), fill=BLUE)
    save(im, "logo.gif", 48)
    return W, H


TABS = [("toys", "toys", RED), ("baby", "baby", (240, 120, 170)), ("ages", "shop by age", BLUE),
        ("games", "video games", GRN), ("gifts", "gift finder", ORA), ("holiday", "holiday", PUR)]


def tabs():
    sizes = {}
    f = font("sansb", 13)
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    for key, label, col in TABS:
        tw, th = tsize(tmp, label, f)
        W, H = tw + 28, 30
        for on in (0, 1):
            im = Image.new("RGB", (W, H), "white")
            d = ImageDraw.Draw(im)
            fill = col if on else mix(col, (255, 255, 255), .25)
            d.rounded_rectangle([1, 2 if on else 6, W - 2, H + 12], radius=12, fill=fill, outline=dk(col))
            # stitched highlight, like a felt tab
            d.rounded_rectangle([5, (6 if on else 10), W - 6, H + 10], radius=9, outline=mix(fill, (255, 255, 255), .45))
            d.text(((W - tw) // 2, (8 if on else 11)), label, font=f, fill=(255, 255, 255))
            save(im, "tabs/%s_%d.gif" % (key, on), 24)
        sizes[key] = (W, H)
    return sizes


# ------------------------------------------------------------------ Sprocket, the mascot (animated)
def sprocket_frame(arm, blink, size=(110, 130), bg=(255, 255, 255)):
    W, H = size
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    cx = W // 2
    # antenna
    d.line([(cx, 18), (cx, 6)], fill=(90, 90, 90), width=3)
    d.ellipse([cx - 6, 0, cx + 6, 12], fill=YEL if blink % 2 == 0 else ORA, outline=dk(YEL))
    # head
    d.rounded_rectangle([cx - 30, 16, cx + 30, 58], radius=10, fill=(200, 210, 225), outline=(70, 80, 100), width=2)
    if blink:
        d.line([(cx - 18, 36), (cx - 8, 36)], fill=(30, 30, 30), width=3)
        d.line([(cx + 8, 36), (cx + 18, 36)], fill=(30, 30, 30), width=3)
    else:
        for sx in (-13, 13):
            d.ellipse([cx + sx - 7, 28, cx + sx + 7, 42], fill="white", outline=(30, 30, 30), width=2)
            d.ellipse([cx + sx - 3, 32, cx + sx + 3, 38], fill=BLUE)
    d.arc([cx - 14, 38, cx + 14, 52], 20, 160, fill=RED, width=3)
    d.ellipse([cx - 36, 30, cx - 28, 42], fill=RED)
    d.ellipse([cx + 28, 30, cx + 36, 42], fill=RED)
    # body
    d.rounded_rectangle([cx - 28, 62, cx + 28, 104], radius=6, fill=RED, outline=dk(RED), width=2)
    d.rectangle([cx - 16, 70, cx + 16, 90], fill=(255, 255, 255), outline=dk(RED))
    d.text((cx - 12, 72), "eT", font=font("dvb", 13), fill=BLUE)
    for i, c in enumerate((YEL, GRN, BLUE)):
        d.ellipse([cx - 14 + i * 11, 93, cx - 7 + i * 11, 100], fill=c)
    # left arm (still) and right arm (waving)
    d.line([(cx - 28, 70), (cx - 42, 92)], fill=(120, 130, 150), width=6)
    d.ellipse([cx - 48, 88, cx - 36, 100], fill=YEL, outline=dk(YEL))
    ang = math.radians(-60 - arm * 25)
    ex, ey = cx + 28 + 22 * math.cos(ang) * -1 * -1, 70 + 22 * math.sin(ang)
    ex = cx + 28 + 22 * abs(math.cos(ang))
    d.line([(cx + 28, 70), (ex, ey)], fill=(120, 130, 150), width=6)
    d.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=YEL, outline=dk(YEL))
    # wheels
    d.rectangle([cx - 20, 104, cx + 20, 112], fill=(90, 90, 90))
    for sx in (-18, 0, 18):
        d.ellipse([cx + sx - 7, 110, cx + sx + 7, 124], fill=(40, 40, 40), outline=(120, 120, 120))
    return im


def mascot():
    frames = []
    seq = [(0, 0), (1, 0), (2, 0), (1, 0), (0, 0), (1, 0), (2, 0), (1, 0), (0, 1), (0, 0)]
    for arm, blink in seq:
        frames.append(sprocket_frame(arm, blink).convert("P", palette=Image.ADAPTIVE, colors=32))
    path = os.path.join(IMG, "sprocket.gif")
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=[160] * 8 + [120, 900], loop=0)
    save(sprocket_frame(1, 0, size=(110, 130), bg=(153, 204, 255)).resize((55, 65), Image.LANCZOS), "sprocket_small.gif", 32)
    # big hello pose for the about page
    save(sprocket_frame(2, 0, size=(110, 130)).resize((220, 260), Image.LANCZOS), "sprocket_big.gif", 48)


# ------------------------------------------------------------------ badges, buttons, banners
def age_badges(ages):
    cols = [(240, 120, 170), ORA, YEL, GRN, BLUE, PUR]
    for (key, label, _a, _b), col in zip(ages, cols):
        im = Image.new("RGB", (64, 64), "white")
        d = ImageDraw.Draw(im)
        d.ellipse([2, 2, 61, 61], fill=col, outline=dk(col), width=3)
        d.ellipse([7, 7, 56, 56], outline=mix(col, (255, 255, 255), .5), width=1)
        lab = label.replace("&amp;", "&")
        num, unit = lab.split(" ", 1)
        f1, f2 = font("dvb", 15 if len(num) < 5 else 13), font("sansb", 9)
        tc = (40, 40, 40) if col == YEL else (255, 255, 255)
        tw, th = tsize(d, num, f1)
        d.text(((64 - tw) // 2, 16), num, font=f1, fill=tc)
        tw, th = tsize(d, unit, f2)
        d.text(((64 - tw) // 2, 36), unit, font=f2, fill=tc)
        save(im, "age_%s.gif" % key, 24)


def button(name, text, col, w=None, size=12):
    f = font("sansb", size)
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw, th = tsize(tmp, text, f)
    W, H = w or tw + 30, 26
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=12, fill=dk(col, .3))
    d.rounded_rectangle([0, 0, W - 1, H - 4], radius=12, fill=col)
    d.rounded_rectangle([4, 3, W - 5, 9], radius=4, fill=mix(col, (255, 255, 255), .35))
    tc = (40, 40, 40) if col == YEL else (255, 255, 255)
    d.text(((W - tw) // 2, 4), text, font=f, fill=tc)
    save(im, name, 24)
    return W, H


def banner():
    # the classic 468x60 banner
    W, H = 468, 60
    im = Image.new("RGB", (W, H), (200, 20, 30))
    d = ImageDraw.Draw(im)
    for x in range(-60, W, 24):
        d.polygon([(x, 0), (x + 12, 0), (x + 72, H), (x + 60, H)], fill=(230, 50, 60))
    d.rectangle([0, 0, W - 1, H - 1], outline=(255, 255, 255), width=3)
    d.rectangle([3, 3, W - 4, H - 4], outline=(30, 140, 60), width=2)
    d.text((70, 8), "Order by Dec. 20", font=font("dvb", 20), fill=(255, 255, 255))
    d.text((70, 33), "for Christmas delivery!", font=font("serifbi", 18), fill=YEL)
    # presents
    for i, (c, rc) in enumerate(((GRN, YEL), (BLUE, RED), (YEL, GRN))):
        x = 330 + i * 42
        d.rectangle([x, 22, x + 34, 52], fill=c, outline=(255, 255, 255))
        d.rectangle([x + 14, 22, x + 20, 52], fill=rc)
        d.ellipse([x + 7, 12, x + 17, 24], outline=rc, width=3)
        d.ellipse([x + 17, 12, x + 27, 24], outline=rc, width=3)
    # tree
    d.polygon([(30, 6), (54, 46), (6, 46)], fill=(30, 140, 60), outline=(255, 255, 255))
    d.rectangle([26, 46, 34, 54], fill=(120, 70, 20))
    d.ellipse([26, 2, 34, 10], fill=YEL)
    save(im, "banner_holiday.gif", 32)


def headers():
    for name, text, col, w in (("h_top10.gif", "Top 10 Toys", RED, 200), ("h_giftfinder.gif", "Gift Finder", ORA, 200),
                               ("h_shopbyage.gif", "Shop by Age", BLUE, 222), ("h_categories.gif", "Toy Categories", GRN, 222),
                               ("h_featured.gif", "Toy of the Day", PUR, 340)):
        im = Image.new("RGB", (w, 26), "white")
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, w - 1, 40], radius=12, fill=col)
        for i in range(0, w, 18):
            d.ellipse([i + 2, 20, i + 8, 26], fill=mix(col, (255, 255, 255), .4))
        d.text((12, 3), text, font=font("dvb", 15), fill=(255, 255, 255) if col != YEL else (40, 40, 40))
        save(im, name, 16)
    # top-10 ribbon
    im = Image.new("RGB", (40, 46), "white")
    d = ImageDraw.Draw(im)
    d.polygon([(8, 26), (2, 44), (12, 38), (18, 46), (20, 28)], fill=BLUE)
    d.polygon([(32, 26), (38, 44), (28, 38), (22, 46), (20, 28)], fill=BLUE)
    d.ellipse([4, 2, 36, 34], fill=YEL, outline=ORA, width=3)
    d.text((10, 9), "10", font=font("dvb", 14), fill=RED)
    save(im, "top10.gif", 16)
    # cart icon
    im = Image.new("RGB", (24, 20), "white")
    d = ImageDraw.Draw(im)
    d.line([(0, 2), (4, 2), (7, 13), (20, 13), (22, 5), (5, 5)], fill=RED, width=2)
    d.ellipse([7, 15, 11, 19], fill=(40, 40, 40))
    d.ellipse([16, 15, 20, 19], fill=(40, 40, 40))
    save(im, "cart.gif", 8)
    # heart (wish list)
    im = Image.new("RGB", (18, 16), "white")
    d = ImageDraw.Draw(im)
    d.ellipse([1, 1, 9, 9], fill=(230, 50, 120))
    d.ellipse([8, 1, 16, 9], fill=(230, 50, 120))
    d.polygon([(1, 6), (16, 6), (9, 15)], fill=(230, 50, 120))
    save(im, "heart.gif", 8)
    # hot! starburst
    im = Image.new("RGB", (40, 26), "white")
    d = ImageDraw.Draw(im)
    pts = []
    for k in range(18):
        a = k * math.pi / 9
        r = 1.0 if k % 2 == 0 else 0.72
        pts.append((20 + 19 * r * math.cos(a), 13 + 12 * r * math.sin(a)))
    d.polygon(pts, fill=YEL, outline=RED)
    d.text((8, 6), "HOT!", font=font("dvb", 10), fill=RED)
    save(im, "hot.gif", 8)
    # snowflake bullet
    im = Image.new("RGB", (14, 14), "white")
    d = ImageDraw.Draw(im)
    for k in range(3):
        a = k * math.pi / 3
        d.line([(7 - 6 * math.cos(a), 7 - 6 * math.sin(a)), (7 + 6 * math.cos(a), 7 + 6 * math.sin(a))], fill=BLUE, width=2)
    save(im, "flake.gif", 8)
    # stars for ratings
    for n in range(1, 6):
        im = Image.new("RGB", (70, 14), "white")
        d = ImageDraw.Draw(im)
        for i in range(5):
            cx = 7 + i * 14
            pts = []
            for k in range(10):
                a = -math.pi / 2 + k * math.pi / 5
                r = 6.5 if k % 2 == 0 else 2.8
                pts.append((cx + r * math.cos(a), 7.3 + r * math.sin(a)))
            d.polygon(pts, fill=YEL if i < n else (225, 225, 225), outline=ORA if i < n else (180, 180, 180))
        save(im, "stars%d.gif" % n, 16)


# ------------------------------------------------------------------ toy product shots
def toy(d, rnd, kind, W, H):
    cx, cy = W // 2, H // 2 + 6
    pal = [RED, BLUE, YEL, GRN, ORA, PUR, (240, 120, 170), (0, 170, 200)]
    c1, c2, c3 = rnd.sample(pal, 3)
    if kind == "robot":
        d.rounded_rectangle([cx - 22, cy - 50, cx + 22, cy - 18], radius=6, fill=(190, 200, 215), outline=(60, 60, 80), width=2)
        d.ellipse([cx - 14, cy - 42, cx - 4, cy - 32], fill=c1)
        d.ellipse([cx + 4, cy - 42, cx + 14, cy - 32], fill=c1)
        d.rectangle([cx - 28, cy - 14, cx + 28, cy + 26], fill=c2, outline=dk(c2), width=2)
        d.rectangle([cx - 40, cy - 12, cx - 30, cy + 16], fill=(150, 150, 165))
        d.rectangle([cx + 30, cy - 12, cx + 40, cy + 16], fill=(150, 150, 165))
        d.rectangle([cx - 22, cy + 26, cx - 6, cy + 50], fill=(150, 150, 165))
        d.rectangle([cx + 6, cy + 26, cx + 22, cy + 50], fill=(150, 150, 165))
        d.line([(cx, cy - 50), (cx, cy - 60)], fill=(60, 60, 60), width=2)
        d.ellipse([cx - 4, cy - 66, cx + 4, cy - 58], fill=c3)
    elif kind == "figure":
        for i, ox in enumerate((-30, 0, 30) if rnd.random() < .5 else (0,)):
            c = pal[(i + pal.index(c1)) % len(pal)]
            d.ellipse([cx + ox - 9, cy - 50, cx + ox + 9, cy - 32], fill=(240, 200, 160))
            d.rectangle([cx + ox - 10, cy - 50, cx + ox + 10, cy - 44], fill=c)
            d.rectangle([cx + ox - 12, cy - 32, cx + ox + 12, cy], fill=c, outline=dk(c))
            d.rectangle([cx + ox - 12, cy, cx + ox - 2, cy + 30], fill=dk(c, .2))
            d.rectangle([cx + ox + 2, cy, cx + ox + 12, cy + 30], fill=dk(c, .2))
            d.polygon([(cx + ox - 12, cy - 30), (cx + ox - 20, cy + 20), (cx + ox - 12, cy + 10)], fill=c3)
    elif kind == "dino":
        d.ellipse([cx - 40, cy - 14, cx + 24, cy + 26], fill=GRN, outline=dk(GRN), width=2)
        d.polygon([(cx + 18, cy - 4), (cx + 30, cy - 46), (cx + 46, cy - 50), (cx + 52, cy - 36), (cx + 30, cy + 4)], fill=GRN, outline=dk(GRN))
        d.ellipse([cx + 40, cy - 46, cx + 44, cy - 42], fill=(0, 0, 0))
        d.polygon([(cx - 40, cy + 4), (cx - 62, cy + 20), (cx - 36, cy + 16)], fill=GRN)
        d.rectangle([cx - 24, cy + 20, cx - 12, cy + 44], fill=dk(GRN, .2))
        d.rectangle([cx + 4, cy + 20, cx + 16, cy + 44], fill=dk(GRN, .2))
        for i in range(5):
            d.polygon([(cx - 30 + i * 11, cy - 12), (cx - 25 + i * 11, cy - 24), (cx - 20 + i * 11, cy - 12)], fill=c1)
    elif kind in ("crayons", "beads"):
        for i in range(8):
            c = pal[i % len(pal)]
            x = cx - 44 + i * 11
            if kind == "crayons":
                d.rectangle([x, cy - 20, x + 8, cy + 34], fill=c, outline=dk(c))
                d.polygon([(x, cy - 20), (x + 4, cy - 34), (x + 8, cy - 20)], fill=c)
                d.rectangle([x, cy, x + 8, cy + 6], fill=(30, 30, 30))
            else:
                for k in range(5):
                    d.ellipse([x, cy - 30 + k * 13, x + 9, cy - 21 + k * 13], fill=pal[(i + k) % len(pal)])
        if kind == "beads":
            d.arc([cx - 50, cy - 46, cx + 50, cy + 50], 200, 340, fill=(200, 200, 200), width=2)
    elif kind == "easel":
        d.line([(cx - 40, cy + 50), (cx - 20, cy - 50)], fill=(160, 110, 50), width=6)
        d.line([(cx + 40, cy + 50), (cx + 20, cy - 50)], fill=(160, 110, 50), width=6)
        d.rectangle([cx - 34, cy - 44, cx + 34, cy + 16], fill=(255, 255, 255), outline=(120, 80, 30), width=3)
        d.ellipse([cx - 22, cy - 34, cx + 2, cy - 10], fill=c1)
        d.polygon([(cx - 6, cy + 8), (cx + 12, cy - 30), (cx + 28, cy + 8)], fill=c2)
        d.ellipse([cx + 14, cy - 40, cx + 28, cy - 26], fill=YEL)
    elif kind == "slime":
        d.rectangle([cx - 26, cy - 30, cx + 26, cy + 40], fill=(220, 240, 255), outline=(120, 140, 160), width=2)
        d.rectangle([cx - 30, cy - 40, cx + 30, cy - 30], fill=c1)
        d.polygon([(cx - 24, cy + 38), (cx - 24, cy), (cx - 10, cy + 8), (cx, cy - 6), (cx + 12, cy + 6), (cx + 24, cy - 4), (cx + 24, cy + 38)], fill=(120, 230, 60))
        d.ellipse([cx + 20, cy + 30, cx + 44, cy + 46], fill=(120, 230, 60))
    elif kind == "blocks":
        letters = "ABCDEF"
        for i in range(6):
            c = pal[i % len(pal)]
            x, y = cx - 46 + (i % 3) * 32, cy - 4 - (i // 3) * 30
            if i >= 3:
                x += 16
            d.rectangle([x, y, x + 28, y + 28], fill=c, outline=dk(c), width=2)
            d.text((x + 8, y + 5), letters[i], font=font("dvb", 15), fill=(255, 255, 255) if c != YEL else (40, 40, 40))
    elif kind == "train":
        for i, c in enumerate((RED, BLUE, GRN)):
            x = cx - 54 + i * 38
            d.rectangle([x, cy - 10, x + 32, cy + 16], fill=c, outline=dk(c), width=2)
            d.ellipse([x + 2, cy + 12, x + 12, cy + 22], fill=(40, 40, 40))
            d.ellipse([x + 20, cy + 12, x + 30, cy + 22], fill=(40, 40, 40))
        d.rectangle([cx - 50, cy - 28, cx - 34, cy - 10], fill=RED)
        d.rectangle([cx - 58, cy + 24, cx + 60, cy + 30], fill=(170, 120, 60))
    elif kind == "gears":
        for (gx, gy, r, c) in ((cx - 22, cy - 6, 24, c1), (cx + 20, cy + 14, 18, c2), (cx + 18, cy - 30, 12, c3)):
            for k in range(12):
                a = k * math.pi / 6
                d.rectangle([gx + (r + 2) * math.cos(a) - 4, gy + (r + 2) * math.sin(a) - 4, gx + (r + 2) * math.cos(a) + 4, gy + (r + 2) * math.sin(a) + 4], fill=c)
            d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=c, outline=dk(c))
            d.ellipse([gx - 5, gy - 5, gx + 5, gy + 5], fill=(255, 255, 255))
    elif kind == "doll":
        hair = rnd.choice([(250, 220, 100), (110, 60, 20), (40, 30, 20), (200, 80, 30)])
        d.ellipse([cx - 16, cy - 56, cx + 16, cy - 24], fill=hair)
        d.ellipse([cx - 12, cy - 52, cx + 12, cy - 26], fill=(250, 215, 180))
        d.ellipse([cx - 7, cy - 44, cx - 3, cy - 40], fill=BLUE)
        d.ellipse([cx + 3, cy - 44, cx + 7, cy - 40], fill=BLUE)
        d.arc([cx - 5, cy - 38, cx + 5, cy - 31], 20, 160, fill=RED, width=2)
        d.polygon([(cx - 10, cy - 24), (cx + 10, cy - 24), (cx + 34, cy + 44), (cx - 34, cy + 44)], fill=c1, outline=dk(c1))
        d.line([(cx - 10, cy - 20), (cx - 24, cy + 4)], fill=(250, 215, 180), width=5)
        d.line([(cx + 10, cy - 20), (cx + 24, cy + 4)], fill=(250, 215, 180), width=5)
        d.polygon([(cx - 14, cy - 60), (cx - 8, cy - 70), (cx, cy - 62), (cx + 8, cy - 70), (cx + 14, cy - 60)], fill=YEL) if rnd.random() < .4 else None
    elif kind == "dollhouse":
        d.polygon([(cx - 50, cy - 16), (cx, cy - 58), (cx + 50, cy - 16)], fill=c1, outline=dk(c1))
        d.rectangle([cx - 44, cy - 16, cx + 44, cy + 48], fill=(255, 240, 220), outline=dk(c1), width=2)
        for wx in (-30, 10):
            for wy in (-6, 22):
                d.rectangle([cx + wx, cy + wy, cx + wx + 18, cy + wy + 16], fill=(170, 220, 255), outline=dk(c1))
        d.rectangle([cx - 6, cy + 26, cx + 6, cy + 48], fill=c2)
    elif kind in ("boardgame", "puzzle"):
        d.rectangle([cx - 52, cy - 34, cx + 52, cy + 34], fill=c1, outline=dk(c1), width=3)
        if kind == "boardgame":
            d.rectangle([cx - 44, cy - 26, cx + 44, cy + 26], fill=(255, 255, 255))
            for i in range(10):
                d.rectangle([cx - 44 + i * 9, cy - 26, cx - 36 + i * 9, cy - 18], fill=pal[i % len(pal)])
                d.rectangle([cx - 44 + i * 9, cy + 18, cx - 36 + i * 9, cy + 26], fill=pal[(i + 3) % len(pal)])
            d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=c2)
        else:
            for i in range(4):
                for j in range(3):
                    c = pal[(i + j * 4) % len(pal)]
                    d.rectangle([cx - 44 + i * 22, cy - 28 + j * 19, cx - 24 + i * 22, cy - 11 + j * 19], fill=c, outline=(255, 255, 255))
                    d.ellipse([cx - 37 + i * 22, cy - 14 + j * 19, cx - 31 + i * 22, cy - 8 + j * 19], fill=c)
    elif kind in ("computer", "console", "handheld"):
        if kind == "handheld":
            d.rounded_rectangle([cx - 26, cy - 48, cx + 26, cy + 48], radius=10, fill=c1, outline=dk(c1), width=2)
            d.rectangle([cx - 18, cy - 38, cx + 18, cy - 4], fill=(150, 200, 120), outline=(40, 40, 40))
            d.rectangle([cx - 18, cy + 12, cx - 6, cy + 16], fill=(40, 40, 40))
            d.rectangle([cx - 14, cy + 8, cx - 10, cy + 20], fill=(40, 40, 40))
            d.ellipse([cx + 6, cy + 10, cx + 14, cy + 18], fill=RED)
            d.ellipse([cx + 14, cy + 4, cx + 22, cy + 12], fill=RED)
        elif kind == "console":
            d.rounded_rectangle([cx - 50, cy - 18, cx + 50, cy + 14], radius=8, fill=(70, 70, 80), outline=(30, 30, 30), width=2)
            d.rectangle([cx - 30, cy - 12, cx + 30, cy - 4], fill=(40, 40, 50))
            d.ellipse([cx + 34, cy - 8, cx + 42, cy], fill=RED)
            for ox in (-36, 20):
                d.rounded_rectangle([cx + ox, cy + 22, cx + ox + 26, cy + 40], radius=6, fill=(90, 90, 100))
                d.ellipse([cx + ox + 16, cy + 26, cx + ox + 22, cy + 32], fill=c1)
            d.line([(cx - 23, cy + 22), (cx - 30, cy + 14)], fill=(40, 40, 40), width=2)
        else:
            d.rounded_rectangle([cx - 44, cy - 36, cx + 44, cy + 10], radius=6, fill=c1, outline=dk(c1), width=2)
            d.rectangle([cx - 34, cy - 28, cx + 34, cy + 2], fill=(180, 230, 180))
            d.text((cx - 22, cy - 22), "ABC", font=font("dvb", 14), fill=(30, 60, 30))
            d.polygon([(cx - 50, cy + 12), (cx + 50, cy + 12), (cx + 56, cy + 40), (cx - 56, cy + 40)], fill=dk(c1, .15), outline=dk(c1))
            for i in range(8):
                for j in range(2):
                    d.rectangle([cx - 40 + i * 10, cy + 18 + j * 9, cx - 33 + i * 10, cy + 24 + j * 9], fill=(255, 255, 255))
    elif kind == "globe":
        d.ellipse([cx - 38, cy - 50, cx + 38, cy + 26], fill=(60, 140, 230), outline=(30, 70, 140), width=2)
        for i in range(4):
            x, y = cx - 26 + rnd.randint(0, 40), cy - 40 + rnd.randint(0, 50)
            d.ellipse([x, y, x + rnd.randint(12, 24), y + rnd.randint(8, 16)], fill=GRN)
        d.arc([cx - 46, cy - 58, cx + 46, cy + 34], 300, 120, fill=(150, 150, 150), width=4)
        d.rectangle([cx - 4, cy + 26, cx + 4, cy + 40], fill=(150, 150, 150))
        d.ellipse([cx - 28, cy + 38, cx + 28, cy + 50], fill=(110, 110, 120))
    elif kind in ("telescope", "microscope"):
        if kind == "telescope":
            d.polygon([(cx - 50, cy - 10), (cx + 40, cy - 44), (cx + 46, cy - 30), (cx - 44, cy + 4)], fill=c1, outline=dk(c1))
            d.line([(cx, cy - 18), (cx - 26, cy + 48)], fill=(80, 80, 80), width=3)
            d.line([(cx, cy - 18), (cx + 26, cy + 48)], fill=(80, 80, 80), width=3)
            d.line([(cx, cy - 18), (cx, cy + 48)], fill=(80, 80, 80), width=3)
        else:
            d.rectangle([cx - 30, cy + 34, cx + 30, cy + 46], fill=(60, 60, 70))
            d.line([(cx + 16, cy + 34), (cx + 16, cy - 30)], fill=(60, 60, 70), width=8)
            d.polygon([(cx - 6, cy - 50), (cx + 10, cy - 50), (cx + 4, cy + 6), (cx - 4, cy + 6)], fill=c1, outline=dk(c1))
            d.rectangle([cx - 22, cy + 10, cx + 22, cy + 16], fill=(80, 80, 90))
    elif kind == "chemset":
        d.rectangle([cx - 54, cy + 20, cx + 54, cy + 40], fill=c1, outline=dk(c1))
        for i, c in enumerate((GRN, BLUE, RED, YEL, PUR)):
            x = cx - 46 + i * 20
            d.rectangle([x, cy - 26, x + 12, cy + 22], fill=(235, 245, 255), outline=(120, 140, 160))
            d.rectangle([x + 1, cy - 4 + i * 3, x + 11, cy + 21], fill=c)
        d.polygon([(cx + 30, cy - 50), (cx + 40, cy - 50), (cx + 40, cy - 34), (cx + 52, cy - 6), (cx + 18, cy - 6), (cx + 30, cy - 34)], fill=(235, 245, 255), outline=(120, 140, 160))
    elif kind == "kitchen":
        d.rectangle([cx - 46, cy - 40, cx + 46, cy + 46], fill=c1, outline=dk(c1), width=2)
        d.rectangle([cx - 40, cy - 6, cx + 40, cy + 40], fill=(255, 255, 255), outline=dk(c1))
        for ox in (-24, 10):
            d.ellipse([cx + ox, cy - 34, cx + ox + 16, cy - 20], fill=(60, 60, 60))
        d.rectangle([cx - 34, cy + 4, cx + 34, cy + 30], fill=(40, 40, 40))
        d.ellipse([cx - 4, cy + 32, cx + 4, cy + 38], fill=c2)
    elif kind == "tools":
        d.rectangle([cx - 54, cy + 4, cx + 54, cy + 14], fill=(200, 140, 70), outline=(120, 80, 30))
        d.rectangle([cx - 48, cy + 14, cx - 40, cy + 46], fill=(200, 140, 70))
        d.rectangle([cx + 40, cy + 14, cx + 48, cy + 46], fill=(200, 140, 70))
        d.rectangle([cx - 30, cy - 40, cx - 24, cy + 4], fill=c1)
        d.rectangle([cx - 38, cy - 48, cx - 16, cy - 36], fill=(150, 150, 160))
        d.polygon([(cx + 4, cy - 2), (cx + 46, cy - 30), (cx + 50, cy - 24), (cx + 8, cy + 4)], fill=(170, 170, 180))
        d.rectangle([cx - 4, cy - 10, cx + 10, cy + 2], fill=c2)
    elif kind == "phone":
        d.rounded_rectangle([cx - 22, cy - 44, cx + 22, cy + 46], radius=8, fill=c1, outline=dk(c1), width=2)
        d.rectangle([cx - 15, cy - 34, cx + 15, cy - 12], fill=(170, 220, 170))
        for r in range(4):
            for c in range(3):
                d.ellipse([cx - 14 + c * 11, cy - 4 + r * 11, cx - 6 + c * 11, cy + 4 + r * 11], fill=pal[(r * 3 + c) % len(pal)])
        d.line([(cx + 14, cy - 44), (cx + 14, cy - 62)], fill=(40, 40, 40), width=4)
    elif kind == "costume":
        d.polygon([(cx - 14, cy - 40), (cx + 14, cy - 40), (cx + 44, cy + 46), (cx - 44, cy + 46)], fill=c1, outline=dk(c1))
        d.polygon([(cx - 14, cy - 40), (cx - 30, cy - 30), (cx - 24, cy - 14), (cx - 10, cy - 30)], fill=c1)
        d.polygon([(cx + 14, cy - 40), (cx + 30, cy - 30), (cx + 24, cy - 14), (cx + 10, cy - 30)], fill=c1)
        for i in range(6):
            d.ellipse([cx - 30 + i * 11, cy + 30, cx - 24 + i * 11, cy + 36], fill=YEL)
        d.polygon([(cx - 14, cy - 54), (cx - 8, cy - 64), (cx, cy - 56), (cx + 8, cy - 64), (cx + 14, cy - 54), (cx + 14, cy - 48), (cx - 14, cy - 48)], fill=YEL, outline=ORA)
    elif kind in ("rccar", "rcboat", "rcplane"):
        if kind == "rccar":
            d.polygon([(cx - 50, cy + 10), (cx - 40, cy - 14), (cx + 20, cy - 14), (cx + 46, cy), (cx + 50, cy + 10)], fill=c1, outline=dk(c1), width=2)
            d.rectangle([cx - 30, cy - 30, cx + 10, cy - 14], fill=(170, 220, 255), outline=dk(c1))
            for wx in (-34, 30):
                d.ellipse([cx + wx - 16, cy, cx + wx + 16, cy + 32], fill=(30, 30, 30))
                d.ellipse([cx + wx - 6, cy + 10, cx + wx + 6, cy + 22], fill=(180, 180, 180))
        elif kind == "rcboat":
            d.polygon([(cx - 56, cy - 4), (cx + 56, cy - 4), (cx + 36, cy + 22), (cx - 50, cy + 22)], fill=c1, outline=dk(c1), width=2)
            d.rectangle([cx - 20, cy - 22, cx + 14, cy - 4], fill=(255, 255, 255), outline=dk(c1))
            for i in range(5):
                d.arc([cx - 60 + i * 26, cy + 24, cx - 34 + i * 26, cy + 38], 180, 360, fill=(60, 140, 230), width=3)
        else:
            d.polygon([(cx - 56, cy), (cx + 40, cy - 6), (cx + 56, cy), (cx + 40, cy + 6)], fill=c1, outline=dk(c1))
            d.polygon([(cx - 8, cy - 2), (cx + 6, cy - 40), (cx + 16, cy - 40), (cx + 12, cy - 2)], fill=c2)
            d.polygon([(cx - 8, cy + 2), (cx + 6, cy + 40), (cx + 16, cy + 40), (cx + 12, cy + 2)], fill=c2)
            d.polygon([(cx - 50, cy), (cx - 56, cy - 18), (cx - 44, cy - 2)], fill=c2)
        # remote
        d.rectangle([cx + 30, cy + 30, cx + 54, cy + 50], fill=(60, 60, 70))
        d.line([(cx + 50, cy + 30), (cx + 56, cy + 12)], fill=(60, 60, 70), width=2)
    elif kind == "giraffe":
        y1 = (240, 190, 60)
        d.rectangle([cx - 30, cy - 4, cx + 26, cy + 22], fill=y1, outline=dk(y1, .3))
        for lx in (-26, -12, 10, 20):
            d.rectangle([cx + lx, cy + 22, cx + lx + 6, cy + 48], fill=y1)
        d.polygon([(cx + 12, cy - 2), (cx + 22, cy - 50), (cx + 32, cy - 48), (cx + 26, cy + 4)], fill=y1)
        d.ellipse([cx + 16, cy - 64, cx + 44, cy - 44], fill=y1, outline=dk(y1, .3))
        d.ellipse([cx + 32, cy - 58, cx + 36, cy - 54], fill=(0, 0, 0))
        d.line([(cx + 22, cy - 62), (cx + 20, cy - 70)], fill=(140, 90, 30), width=3)
        d.line([(cx + 30, cy - 63), (cx + 30, cy - 71)], fill=(140, 90, 30), width=3)
        for sx, sy in ((-20, 4), (-4, 10), (10, 2), (18, -24), (22, -38), (-14, 14)):
            d.ellipse([cx + sx, cy + sy, cx + sx + 7, cy + sy + 6], fill=(170, 100, 40))
    elif kind in ("bear", "owl"):
        if kind == "bear":
            c = rnd.choice([(170, 110, 60), (230, 200, 150), (250, 250, 250), (240, 150, 190), (130, 90, 60)])
            d.ellipse([cx - 32, cy - 6, cx + 32, cy + 50], fill=c, outline=dk(c, .3))
            d.ellipse([cx - 26, cy - 52, cx + 26, cy - 2], fill=c, outline=dk(c, .3))
            d.ellipse([cx - 30, cy - 58, cx - 12, cy - 40], fill=c, outline=dk(c, .3))
            d.ellipse([cx + 12, cy - 58, cx + 30, cy - 40], fill=c, outline=dk(c, .3))
            d.ellipse([cx - 10, cy - 24, cx + 10, cy - 8], fill=mix(c, (255, 255, 255), .4))
            d.ellipse([cx - 4, cy - 22, cx + 4, cy - 16], fill=(30, 30, 30))
            d.ellipse([cx - 13, cy - 36, cx - 7, cy - 30], fill=(30, 30, 30))
            d.ellipse([cx + 7, cy - 36, cx + 13, cy - 30], fill=(30, 30, 30))
            d.polygon([(cx - 12, cy - 4), (cx, cy + 2), (cx + 12, cy - 4), (cx + 12, cy + 6), (cx, cy + 2), (cx - 12, cy + 6)], fill=c1)
        else:
            d.ellipse([cx - 34, cy - 44, cx + 34, cy + 46], fill=c1, outline=dk(c1), width=2)
            d.ellipse([cx - 20, cy - 10, cx + 20, cy + 40], fill=mix(c1, (255, 255, 255), .5))
            d.polygon([(cx - 28, cy - 36), (cx - 38, cy - 64), (cx - 12, cy - 42)], fill=c1)
            d.polygon([(cx + 28, cy - 36), (cx + 38, cy - 64), (cx + 12, cy - 42)], fill=c1)
            for sx in (-14, 14):
                d.ellipse([cx + sx - 12, cy - 34, cx + sx + 12, cy - 10], fill=(255, 255, 255), outline=(30, 30, 30))
                d.ellipse([cx + sx - 5, cy - 27, cx + sx + 5, cy - 17], fill=(30, 30, 30))
            d.polygon([(cx - 6, cy - 8), (cx + 6, cy - 8), (cx, cy + 2)], fill=ORA)
    elif kind in ("bike", "scooter", "wagon"):
        if kind == "bike":
            for wx in (-34, 34):
                d.ellipse([cx + wx - 24, cy - 4, cx + wx + 24, cy + 44], outline=(40, 40, 40), width=4)
                d.ellipse([cx + wx - 3, cy + 17, cx + wx + 3, cy + 23], fill=(100, 100, 100))
            d.line([(cx - 34, cy + 20), (cx - 4, cy - 14), (cx + 26, cy - 14), (cx + 34, cy + 20)], fill=c1, width=5)
            d.line([(cx - 4, cy - 14), (cx, cy + 20), (cx - 34, cy + 20)], fill=c1, width=5)
            d.line([(cx + 26, cy - 14), (cx + 22, cy - 30)], fill=(60, 60, 60), width=3)
            d.line([(cx + 14, cy - 30), (cx + 30, cy - 30)], fill=(60, 60, 60), width=4)
            d.rectangle([cx - 12, cy - 22, cx + 4, cy - 16], fill=(40, 40, 40))
        elif kind == "scooter":
            d.rectangle([cx - 44, cy + 22, cx + 30, cy + 30], fill=(190, 190, 200), outline=(90, 90, 100))
            d.line([(cx + 30, cy + 26), (cx + 30, cy - 50)], fill=(150, 150, 160), width=5)
            d.line([(cx + 16, cy - 50), (cx + 44, cy - 50)], fill=c1, width=6)
            for wx in (-40, 34):
                d.ellipse([cx + wx - 10, cy + 24, cx + wx + 10, cy + 44], fill=c1, outline=(40, 40, 40))
        else:
            d.polygon([(cx - 50, cy - 10), (cx + 40, cy - 10), (cx + 34, cy + 20), (cx - 44, cy + 20)], fill=RED, outline=dk(RED), width=2)
            for wx in (-30, 20):
                d.ellipse([cx + wx - 13, cy + 14, cx + wx + 13, cy + 40], fill=(40, 40, 40))
            d.line([(cx + 40, cy - 4), (cx + 60, cy - 30)], fill=(40, 40, 40), width=4)
    elif kind in ("ball", "kite", "watergun", "sandbox"):
        if kind == "ball":
            for i, (ox, oy, r) in enumerate(((-28, 10, 26), (24, 18, 20), (2, -26, 22))):
                c = pal[(pal.index(c1) + i) % len(pal)]
                d.ellipse([cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r], fill=c, outline=dk(c))
                d.arc([cx + ox - r, cy + oy - r // 2, cx + ox + r, cy + oy + r // 2], 0, 180, fill=(255, 255, 255), width=2)
        elif kind == "kite":
            d.polygon([(cx, cy - 56), (cx + 34, cy - 14), (cx, cy + 20), (cx - 34, cy - 14)], fill=c1, outline=dk(c1), width=2)
            d.line([(cx, cy - 56), (cx, cy + 20)], fill=dk(c1))
            d.line([(cx - 34, cy - 14), (cx + 34, cy - 14)], fill=dk(c1))
            pts = [(cx, cy + 20)]
            for k in range(1, 8):
                pts.append((cx + 10 * math.sin(k), cy + 20 + k * 5))
            d.line(pts, fill=(80, 80, 80), width=2)
            for k in range(1, 8, 2):
                d.polygon([(pts[k][0] - 5, pts[k][1]), (pts[k][0] + 5, pts[k][1] - 3), (pts[k][0] + 5, pts[k][1] + 3)], fill=pal[k % len(pal)])
        elif kind == "watergun":
            d.rounded_rectangle([cx - 50, cy - 20, cx + 30, cy + 4], radius=10, fill=c1, outline=dk(c1), width=2)
            d.rectangle([cx + 30, cy - 14, cx + 50, cy - 6], fill=c2)
            d.ellipse([cx - 40, cy - 46, cx - 6, cy - 16], fill=YEL, outline=dk(YEL))
            d.polygon([(cx - 20, cy + 4), (cx - 4, cy + 4), (cx - 10, cy + 40), (cx - 28, cy + 40)], fill=c1, outline=dk(c1))
            for k in range(4):
                d.ellipse([cx + 54 + k * 6, cy - 12 + k * 3, cx + 58 + k * 6, cy - 8 + k * 3], fill=(100, 180, 255))
        else:
            d.ellipse([cx - 56, cy - 10, cx + 56, cy + 40], fill=GRN, outline=dk(GRN), width=2)
            d.ellipse([cx - 44, cy - 2, cx + 44, cy + 32], fill=(240, 220, 160))
            d.ellipse([cx + 40, cy - 24, cx + 62, cy - 4], fill=GRN)
            d.ellipse([cx + 52, cy - 18, cx + 56, cy - 14], fill=(0, 0, 0))
            d.polygon([(cx - 10, cy + 10), (cx + 4, cy - 20), (cx + 10, cy + 10)], fill=RED)
    elif kind in ("rattle", "rings", "mobile", "xylophone"):
        if kind == "rattle":
            d.ellipse([cx - 26, cy - 50, cx + 26, cy + 2], fill=c1, outline=dk(c1), width=2)
            d.rectangle([cx - 6, cy, cx + 6, cy + 40], fill=c2)
            d.ellipse([cx - 16, cy + 34, cx + 16, cy + 50], outline=c3, width=5)
            d.ellipse([cx - 10, cy - 34, cx + 10, cy - 14], fill=YEL)
        elif kind == "rings":
            d.ellipse([cx - 44, cy + 34, cx + 44, cy + 50], fill=dk(c1, .1))
            d.rectangle([cx - 4, cy - 50, cx + 4, cy + 40], fill=(230, 230, 230))
            for i in range(5):
                c = pal[i % len(pal)]
                w = 40 - i * 6
                y = cy + 26 - i * 14
                d.ellipse([cx - w, y - 8, cx + w, y + 10], fill=c, outline=dk(c))
            d.ellipse([cx - 9, cy - 58, cx + 9, cy - 40], fill=RED)
        elif kind == "mobile":
            d.line([(cx - 50, cy - 40), (cx + 50, cy - 40)], fill=(160, 120, 60), width=3)
            d.line([(cx, cy - 60), (cx, cy - 40)], fill=(160, 120, 60), width=3)
            for i, ox in enumerate((-44, -14, 16, 44)):
                d.line([(cx + ox, cy - 40), (cx + ox, cy - 10 + (i % 2) * 14)], fill=(150, 150, 150))
                y = cy - 10 + (i % 2) * 14
                if i % 2:
                    d.ellipse([cx + ox - 10, y, cx + ox + 10, y + 20], fill=YEL)
                else:
                    pts = []
                    for k in range(10):
                        a = -math.pi / 2 + k * math.pi / 5
                        r = 11 if k % 2 == 0 else 5
                        pts.append((cx + ox + r * math.cos(a), y + 10 + r * math.sin(a)))
                    d.polygon(pts, fill=pal[i % len(pal)])
        else:
            for i in range(7):
                c = pal[i % len(pal)]
                h = 50 - i * 5
                d.rectangle([cx - 52 + i * 15, cy - h // 2, cx - 41 + i * 15, cy + h // 2], fill=c, outline=dk(c))
            d.line([(cx - 56, cy - 26), (cx + 52, cy - 10)], fill=(150, 100, 50), width=3)
            d.line([(cx - 56, cy + 26), (cx + 52, cy + 10)], fill=(150, 100, 50), width=3)
            d.line([(cx + 20, cy - 50), (cx + 44, cy - 30)], fill=(150, 100, 50), width=3)
            d.ellipse([cx + 14, cy - 56, cx + 24, cy - 46], fill=RED)
    else:
        d.rectangle([cx - 40, cy - 30, cx + 40, cy + 40], fill=c1)


def toy_image(code, kind, seed):
    rnd = random.Random(seed)
    W, H = 140, 140
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    d.ellipse([20, H - 26, W - 20, H - 12], fill=(232, 232, 232))
    toy(d, rnd, kind, W, H)
    save(im, "toys/%s.gif" % code, 64)
    save(im.resize((70, 70), Image.LANCZOS), "toys/%s_s.gif" % code, 64)


# ------------------------------------------------------------------ Sprocket's theme song (MIDI)
def midi():
    # an original little tune in C major: (note, beats)
    melody = [(67, 1), (72, 1), (76, 1), (72, 1), (74, 1), (77, 1), (76, 2),
              (72, 1), (74, 1), (76, 1), (79, 1), (77, 1), (74, 1), (72, 2),
              (69, 1), (72, 1), (77, 1), (76, 1), (74, 1), (71, 1), (72, 1), (74, 1),
              (76, 1), (79, 1), (81, 1), (79, 1), (77, 1), (74, 1), (72, 2)]
    bass = [48, 53, 55, 48, 45, 53, 55, 48]
    tpq = 96

    def vlq(n):
        out = [n & 0x7F]
        n >>= 7
        while n:
            out.insert(0, (n & 0x7F) | 0x80)
            n >>= 7
        return bytes(out)

    def track(events):
        data = b"".join(events) + b"\x00\xFF\x2F\x00"
        return b"MTrk" + struct.pack(">I", len(data)) + data

    ev = [b"\x00\xFF\x51\x03" + struct.pack(">I", 400000)[1:], b"\x00\xC0\x0B"]  # tempo, vibraphone
    for note, beats in melody:
        ev.append(b"\x00\x90" + bytes([note, 96]))
        ev.append(vlq(beats * tpq) + b"\x80" + bytes([note, 0]))
    ev2 = [b"\x00\xC1\x20"]  # acoustic bass
    for n in bass:
        ev2.append(b"\x00\x91" + bytes([n, 80]))
        ev2.append(vlq(4 * tpq) + b"\x81" + bytes([n, 0]))
    data = b"MThd" + struct.pack(">IHHH", 6, 1, 2, tpq) + track(ev) + track(ev2)
    with open(os.path.join(IMG, "sprocket.mid"), "wb") as f:
        f.write(data)


def all_static(ages):
    os.makedirs(IMG, exist_ok=True)
    sizes = {"logo": logo(), "tabs": tabs()}
    mascot()
    age_badges(ages)
    sizes["btn"] = {
        "addcart": button("btn_addcart.gif", "Add to Cart", RED),
        "wish": button("btn_wish.gif", "Add to Wish List", BLUE),
        "checkout": button("btn_checkout.gif", "Check Out Now", GRN),
        "find": button("btn_find.gif", "Find Gifts!", ORA),
        "continue": button("btn_continue.gif", "Continue", GRN),
        "place": button("btn_place.gif", "Place My Order", RED),
    }
    banner()
    headers()
    midi()
    return sizes


if __name__ == "__main__":
    import toys_data
    print(all_static(toys_data.AGES))
