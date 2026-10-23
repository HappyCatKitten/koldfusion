#!/usr/bin/env python3
"""Draws every CNM Interactive graphic with Pillow (no outside artwork).

    python3 tools/gfx.py        (from the site folder; writes images/*.gif)

Logo, section title bars, nav doodads, market arrows, weather icons, QuickVote bars,
LED countdown digits, banner ads, the U.S. weather map, the video still, and one
"wire photo" illustration (+ thumbnail) per story, procedurally drawn from data.py.
"""
import math, os, random, sys, zlib
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data

OUT = os.path.join(HERE, "..", "images")
FONTDIRS = ["/usr/share/fonts/truetype/liberation/", "/usr/share/fonts/truetype/dejavu/",
            "/usr/share/fonts/truetype/freefont/"]
SANS_B = ["LiberationSans-Bold.ttf", "DejaVuSans-Bold.ttf", "FreeSansBold.ttf"]
SANS = ["LiberationSans-Regular.ttf", "DejaVuSans.ttf", "FreeSans.ttf"]
SANS_BI = ["LiberationSans-BoldItalic.ttf", "DejaVuSans-BoldOblique.ttf", "FreeSansBoldOblique.ttf"]
SERIF_B = ["LiberationSerif-Bold.ttf", "DejaVuSerif-Bold.ttf", "FreeSerifBold.ttf"]
NARROW_B = ["LiberationSansNarrow-Bold.ttf", "DejaVuSansCondensed-Bold.ttf", "LiberationSans-Bold.ttf"]
MONO_B = ["LiberationMono-Bold.ttf", "DejaVuSansMono-Bold.ttf", "FreeMonoBold.ttf"]

RED = (204, 0, 0)
NAVY = (51, 51, 102)
SLATE = (102, 102, 153)
LAV = (204, 204, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (102, 102, 102)
ORANGE = (255, 102, 0)

_fc = {}


def font(names, size):
    key = (names[0], size)
    if key not in _fc:
        f = None
        for d in FONTDIRS:
            for n in names:
                p = os.path.join(d, n)
                if os.path.exists(p) and f is None:
                    f = ImageFont.truetype(p, size)
        _fc[key] = f or ImageFont.load_default()
    return _fc[key]


def save(img, name, colors=128, transparent=None):
    img = img.convert("RGB")
    p = img.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE) if colors < 256 else img.convert("P", palette=Image.ADAPTIVE)
    kw = {}
    if transparent is not None:
        # find palette index closest to the transparent colour
        pal = p.getpalette()[:768]
        best, bi = 1e9, 0
        for i in range(len(pal) // 3):
            r, g, b = pal[i * 3:i * 3 + 3]
            d = (r - transparent[0]) ** 2 + (g - transparent[1]) ** 2 + (b - transparent[2]) ** 2
            if d < best:
                best, bi = d, i
        kw["transparency"] = bi
    p.save(os.path.join(OUT, name), **kw)


def tw(d, text, f):
    b = d.textbbox((0, 0), text, font=f)
    return b[2] - b[0], b[3] - b[1], b


def ctext(d, cx, cy, text, f, fill):
    w, h, b = tw(d, text, f)
    d.text((cx - w / 2 - b[0], cy - h / 2 - b[1]), text, font=f, fill=fill)


def ss(w, h, bg, k=3):
    """supersampled canvas"""
    return Image.new("RGB", (w * k, h * k), bg), k


def down(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


# ------------------------------------------------------------------ logo & chrome
def logo():
    img, k = ss(167, 40, RED)
    d = ImageDraw.Draw(img)
    f = font(SANS_BI, 34 * k)
    d.text((8 * k, 0 * k), "CNM", font=f, fill=WHITE)
    w, h, b = tw(d, "CNM", f)
    # two cable stripes cutting through the letters
    for y in (15, 22):
        d.rectangle([6 * k, y * k, (12 + w // k) * k, (y + 1) * k], fill=RED)
    f2 = font(SANS_B, 15 * k)
    d.text(((14 + w // k) * k, 13 * k), ".com", font=f2, fill=WHITE)
    f3 = font(SANS_B, 8 * k)
    d.text(((15 + w // k) * k, 29 * k), "INTERACTIVE", font=f3, fill=(255, 210, 210))
    d.rectangle([0, 0, 167 * k - 1, 40 * k - 1], outline=(150, 0, 0), width=k)
    save(down(img, 167, 40), "logo.gif", 32)
    # small footer logo
    save(down(img, 84, 20), "logo_small.gif", 32)


def title_bar(name, text, sub=None):
    """section title graphic, 470x40: red CNM tab, big navy caps, gray rule"""
    img, k = ss(470, 40, WHITE)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 6 * k, 44 * k, 34 * k], fill=RED)
    ctext(d, 22 * k, 20 * k, "CNM", font(SANS_BI, 15 * k), WHITE)
    f = font(SANS_B, 24 * k)
    d.text((54 * k, 5 * k), text, font=f, fill=NAVY)
    w, h, b = tw(d, text, f)
    if sub:
        d.text((58 * k + w, 15 * k), sub, font=font(SANS_B, 11 * k), fill=RED)
    d.rectangle([54 * k, 35 * k, 470 * k, 36 * k], fill=(153, 153, 153))
    d.rectangle([54 * k, 37 * k, 300 * k, 38 * k], fill=RED)
    save(down(img, 470, 40), name, 48)


def small_bits():
    # 1x1 transparent spacer
    im = Image.new("RGB", (1, 1), WHITE)
    save(im, "1.gif", 2, transparent=WHITE)
    # new arrow for MAIN PAGE cell
    img, k = ss(11, 11, NAVY)
    d = ImageDraw.Draw(img)
    d.polygon([(2 * k, 1 * k), (10 * k, 5.5 * k), (2 * k, 10 * k)], fill=(255, 204, 0))
    save(down(img, 11, 11), "newarrow.gif", 16)
    # market arrows
    for nm, col, up in (("arrow_up.gif", (0, 153, 0), True), ("arrow_down.gif", RED, False)):
        img, k = ss(10, 10, (238, 238, 238), 4)
        d = ImageDraw.Draw(img)
        if up:
            d.polygon([(5 * k, 1 * k), (9.5 * k, 9 * k), (0.5 * k, 9 * k)], fill=col)
        else:
            d.polygon([(0.5 * k, 1 * k), (9.5 * k, 1 * k), (5 * k, 9 * k)], fill=col)
        save(down(img, 10, 10), nm, 16)
    # quickvote / bar graph pieces
    for nm, col in (("bar_red.gif", RED), ("bar_navy.gif", SLATE), ("bar_gray.gif", (153, 153, 153)), ("bar_orange.gif", ORANGE)):
        img = Image.new("RGB", (10, 12), col)
        d = ImageDraw.Draw(img)
        d.line([(0, 0), (9, 0)], fill=tuple(min(255, c + 60) for c in col))
        d.line([(0, 11), (9, 11)], fill=tuple(max(0, c - 60) for c in col))
        save(img, nm, 8)
    # status dots for bug watch
    for nm, col in (("dot_green.gif", (0, 170, 0)), ("dot_yellow.gif", (240, 200, 0)), ("dot_red.gif", RED)):
        img, k = ss(12, 12, WHITE, 4)
        d = ImageDraw.Draw(img)
        d.ellipse([1 * k, 1 * k, 11 * k, 11 * k], fill=col, outline=(60, 60, 60), width=k // 2 + 1)
        d.ellipse([3 * k, 3 * k, 6 * k, 6 * k], fill=tuple(min(255, c + 90) for c in col))
        save(down(img, 12, 12), nm, 16)
    # video / audio icons
    img, k = ss(10, 10, WHITE, 4)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 2 * k, 7 * k, 8 * k], fill=NAVY)
    d.polygon([(7 * k, 5 * k), (10 * k, 2 * k), (10 * k, 8 * k)], fill=NAVY)
    save(down(img, 10, 10), "icon_video.gif", 16)
    img, k = ss(10, 10, WHITE, 4)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 3.5 * k, 3 * k, 6.5 * k], fill=NAVY)
    d.polygon([(3 * k, 3.5 * k), (7 * k, 0), (7 * k, 10 * k), (3 * k, 6.5 * k)], fill=NAVY)
    d.arc([5 * k, 2 * k, 10 * k, 8 * k], -60, 60, fill=NAVY, width=k)
    save(down(img, 10, 10), "icon_audio.gif", 16)
    # FULL STORY button
    img, k = ss(78, 14, WHITE)
    d = ImageDraw.Draw(img)
    d.polygon([(1 * k, 3 * k), (8 * k, 7 * k), (1 * k, 11 * k)], fill=RED)
    d.text((11 * k, 0.5 * k), "FULL STORY", font=font(SANS_B, 11 * k), fill=NAVY)
    save(down(img, 78, 14), "full_story.gif", 16)
    # small header strips
    for nm, text, bg, w in (("vod.gif", "VIDEO OF THE DAY", RED, 150), ("quickvote.gif", "QUICKVOTE", NAVY, 150),
                            ("countdown_hdr.gif", "COUNTDOWN TO 2000", RED, 150), ("newsnet.gif", "CNM.com NEWS NET", GRAY, 178)):
        img, k = ss(w, 20, bg)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 5 * k, 20 * k], fill=ORANGE)
        d.text((10 * k, 3 * k), text, font=font(SANS_B, 12 * k), fill=WHITE)
        save(down(img, w, 20), nm, 16)
    # "CNM WEB SITES" image map graphic 121x40
    img, k = ss(121, 40, LAV)
    d = ImageDraw.Draw(img)
    cells = [((0, 0, 63, 19), "myCNM"), ((64, 0, 120, 19), "CNM/SI"), ((0, 20, 63, 39), "Politics"), ((64, 20, 120, 39), "CNMfn")]
    for (x0, y0, x1, y1), t in cells:
        d.rectangle([x0 * k, y0 * k, x1 * k, y1 * k], fill=WHITE, outline=SLATE, width=k)
        d.rectangle([(x0 + 3) * k, (y0 + 4) * k, (x0 + 9) * k, (y1 - 4) * k], fill=RED)
        d.text(((x0 + 12) * k, (y0 + 4) * k), t, font=font(SANS_B, 10 * k), fill=NAVY)
    save(down(img, 121, 40), "websites.gif", 32)
    # ReelPlayer badge
    img, k = ss(88, 31, (20, 20, 60))
    d = ImageDraw.Draw(img)
    d.ellipse([3 * k, 4 * k, 26 * k, 27 * k], fill=(0, 102, 204), outline=WHITE, width=k)
    d.polygon([(11 * k, 9 * k), (21 * k, 15.5 * k), (11 * k, 22 * k)], fill=WHITE)
    d.text((30 * k, 3 * k), "Get", font=font(SANS, 9 * k), fill=(200, 200, 255))
    d.text((30 * k, 12 * k), "ReelPlayer", font=font(SANS_B, 10 * k), fill=WHITE)
    d.text((62 * k, 22 * k), "G2", font=font(SANS_B, 7 * k), fill=(255, 204, 0))
    save(down(img, 88, 31), "reelplayer.gif", 32)


# ------------------------------------------------------------------ weather icons
def wx_icon(kind, size):
    img, k = ss(size, size, WHITE, 4)
    d = ImageDraw.Draw(img)
    S = size * k / 40.0

    def sun(cx, cy, r):
        for a in range(0, 360, 45):
            x1 = cx + math.cos(math.radians(a)) * r * 1.35
            y1 = cy + math.sin(math.radians(a)) * r * 1.35
            x2 = cx + math.cos(math.radians(a)) * r * 1.8
            y2 = cy + math.sin(math.radians(a)) * r * 1.8
            d.line([(x1, y1), (x2, y2)], fill=(255, 170, 0), width=int(2.2 * S))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 204, 0), outline=(230, 140, 0), width=int(S))

    def cloud(cx, cy, w, col=(190, 190, 200), edge=(120, 120, 140)):
        parts = [(-0.3, 0.05, 0.28), (0.0, -0.12, 0.34), (0.3, 0.05, 0.26)]
        for dx, dy, r in parts:
            d.ellipse([cx + (dx - r) * w, cy + (dy - r) * w, cx + (dx + r) * w, cy + (dy + r) * w], fill=edge)
        for dx, dy, r in parts:
            r2 = r - 0.04
            d.ellipse([cx + (dx - r2) * w, cy + (dy - r2) * w, cx + (dx + r2) * w, cy + (dy + r2) * w], fill=col)
        d.rectangle([cx - 0.3 * w, cy + 0.02 * w, cx + 0.3 * w, cy + 0.29 * w], fill=col)

    if kind == "sun":
        sun(20 * S, 20 * S, 9 * S)
    elif kind == "partly":
        sun(14 * S, 14 * S, 7 * S)
        cloud(23 * S, 24 * S, 28 * S, col=(235, 235, 240))
    elif kind == "cloud":
        cloud(20 * S, 20 * S, 34 * S)
    elif kind == "rain":
        cloud(20 * S, 15 * S, 32 * S, col=(150, 150, 165), edge=(90, 90, 110))
        for x in (11, 18, 25, 32):
            d.line([(x * S, 27 * S), ((x - 3) * S, 36 * S)], fill=(0, 90, 220), width=int(2 * S))
    elif kind == "snow":
        cloud(20 * S, 15 * S, 32 * S, col=(205, 205, 215), edge=(130, 130, 150))
        for x, y in ((11, 29), (20, 33), (29, 29), (15, 37), (25, 37)):
            for a in (0, 60, 120):
                dx = math.cos(math.radians(a)) * 2.6 * S
                dy = math.sin(math.radians(a)) * 2.6 * S
                d.line([(x * S - dx, y * S - dy), (x * S + dx, y * S + dy)], fill=(0, 120, 220), width=int(1.1 * S))
    elif kind == "storm":
        cloud(20 * S, 14 * S, 34 * S, col=(110, 110, 125), edge=(60, 60, 75))
        d.polygon([(21 * S, 22 * S), (14 * S, 31 * S), (19 * S, 31 * S), (15 * S, 39 * S), (27 * S, 28 * S), (21 * S, 28 * S), (25 * S, 22 * S)],
                  fill=(255, 220, 0), outline=(200, 140, 0))
    return down(img, size, size)


def weather_icons():
    for kind in ("sun", "partly", "cloud", "rain", "snow", "storm"):
        save(wx_icon(kind, 40), "wx_%s.gif" % kind, 64)
        save(wx_icon(kind, 20), "wxs_%s.gif" % kind, 32)


US_OUTLINE = [(22, 28), (60, 30), (110, 34), (160, 36), (210, 36), (230, 40), (250, 52), (268, 56), (282, 60),
              (300, 62), (318, 58), (338, 52), (352, 40), (366, 30), (380, 26), (388, 36), (378, 52), (368, 62),
              (362, 76), (352, 90), (340, 104), (334, 124), (326, 146), (318, 160), (318, 178), (330, 196),
              (336, 214), (330, 226), (318, 222), (306, 200), (294, 186), (268, 188), (250, 196), (232, 196),
              (216, 210), (206, 228), (196, 228), (182, 208), (170, 196), (150, 192), (128, 188), (100, 180),
              (80, 176), (62, 168), (44, 150), (30, 128), (20, 104), (14, 80), (14, 56)]


def us_map():
    W, H = 400, 250
    img, k = ss(W, H, (150, 190, 230))
    d = ImageDraw.Draw(img)
    P = [(x * k, y * k) for x, y in US_OUTLINE]
    # temperature bands clipped by the outline: draw bands on a separate layer and mask
    bands = Image.new("RGB", img.size, WHITE)
    bd = ImageDraw.Draw(bands)
    cols = [(120, 120, 255), (150, 180, 255), (170, 230, 200), (230, 240, 140), (255, 200, 110), (255, 150, 90)]
    for i, c in enumerate(cols):
        y0 = (20 + i * 38) * k
        bd.polygon([(0, y0 - 30 * k), (W * k, y0 + 10 * k), (W * k, y0 + 48 * k), (0, y0 + 8 * k)], fill=c)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).polygon(P, fill=255)
    img.paste(bands, (0, 0), mask)
    d.polygon(P, outline=(60, 60, 60))
    d.line(P + [P[0]], fill=(60, 60, 60), width=2 * k)
    # front line with triangles
    pts = [(60, 70), (120, 90), (180, 100), (240, 110), (300, 100), (350, 80)]
    d.line([(x * k, y * k) for x, y in pts], fill=(0, 0, 200), width=3 * k)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        d.polygon([((mx - 6) * k, my * k), ((mx + 6) * k, my * k), (mx * k, (my + 9) * k)], fill=(0, 0, 200))
    f = font(SANS_B, 10 * k)
    for c in data.WEATHER:
        x, y = c[7]
        ic = wx_icon(c[2], 20)
        img.paste(ic.resize((20 * k, 20 * k)), ((x - 10) * k, (y - 22) * k))
        txt = "%d" % c[3]
        w, h, b = tw(d, txt, f)
        d.rectangle([(x - 2) * k - w / 2 - k, (y - 1) * k, (x + 2) * k + w / 2 + k, (y + 12) * k], fill=WHITE, outline=BLACK)
        d.text((x * k - w / 2 - b[0], (y + 0.5) * k), txt, font=f, fill=RED)
    d.text((8 * k, 228 * k), "CNM WEATHER  Highs for Monday, Dec. 20", font=font(SANS_B, 11 * k), fill=NAVY)
    im = down(img, W, H)
    save(im, "us_map.gif", 128)
    save(im.resize((150, 94), Image.LANCZOS), "us_map_small.gif", 128)


# ------------------------------------------------------------------ LED digits
SEGS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
        "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcfgd"}


def led_digits():
    W, H = 22, 34
    for ch in list("0123456789") + ["colon", "blank"]:
        img, k = ss(W, H, (16, 0, 0), 4)
        d = ImageDraw.Draw(img)
        on, off = (255, 40, 20), (48, 5, 3)
        x0, x1, y0, y1, y2 = 4 * k, 17 * k, 3 * k, 16.5 * k, 30 * k
        t = 2.4 * k
        seg = {"a": (x0 + t, y0 - t / 2, x1 - t, y0 + t / 2, "h"), "g": (x0 + t, y1 - t / 2, x1 - t, y1 + t / 2, "h"),
               "d": (x0 + t, y2 - t / 2, x1 - t, y2 + t / 2, "h"),
               "f": (x0 - t / 2, y0 + t, x0 + t / 2, y1 - t, "v"), "b": (x1 - t / 2, y0 + t, x1 + t / 2, y1 - t, "v"),
               "e": (x0 - t / 2, y1 + t, x0 + t / 2, y2 - t, "v"), "c": (x1 - t / 2, y1 + t, x1 + t / 2, y2 - t, "v")}
        lit = SEGS.get(ch, "")
        for s, (a, b, c, e, o) in seg.items():
            col = on if s in lit else off
            if o == "h":
                m = (b + e) / 2
                d.polygon([(a, m), (a + t / 2, b), (c - t / 2, b), (c, m), (c - t / 2, e), (a + t / 2, e)], fill=col)
            else:
                m = (a + c) / 2
                d.polygon([(m, b), (c, b + t / 2), (c, e - t / 2), (m, e), (a, e - t / 2), (a, b + t / 2)], fill=col)
        if ch == "colon":
            img, k = ss(W, H, (16, 0, 0), 4)
            d = ImageDraw.Draw(img)
            for cy in (11, 23):
                d.ellipse([8 * k, (cy - 2.5) * k, 13 * k, (cy + 2.5) * k], fill=on)
        name = "led_%s.gif" % ch
        save(down(img, W, H), name, 16)


# ------------------------------------------------------------------ banner ads
def banners():
    specs = {
        "ad_ubid.gif": ((0, 51, 153), "uBid", "Y2K survival gear from $1!", "Generators * Flashlights * Beans", "BID NOW >>"),
        "ad_orinoco.gif": ((0, 102, 102), "Orinoco.com", "Millennium gift books, shipped", "A river of books. Up to 40% off.", "SHOP >>"),
        "ad_snapster.gif": ((40, 40, 40), "Snapster", "Your music. Everyone's music.", "Free download -- 1.2 MB", "GET IT >>"),
        "ad_altavisor.gif": ((90, 0, 120), "AltaVisor", "Search 150 million pages", "...and find the one you wanted", "SEARCH >>"),
    }
    for name, (bg, brand, l1, l2, btn) in specs.items():
        img, k = ss(468, 60, bg)
        d = ImageDraw.Draw(img)
        for i in range(0, 468, 12):
            d.line([(i * k, 0), ((i - 60) * k, 60 * k)], fill=tuple(min(255, c + 18) for c in bg), width=k)
        d.rectangle([0, 0, 467 * k, 59 * k], outline=WHITE, width=k)
        bf = font(SANS_BI, 26 * k)
        while tw(d, brand, bf)[0] > 150 * k:
            bf = font(SANS_BI, bf.size - k)
        d.text((10 * k, 14 * k), brand, font=bf, fill=(255, 220, 0))
        d.text((170 * k, 10 * k), l1, font=font(SANS_B, 14 * k), fill=WHITE)
        d.text((170 * k, 32 * k), l2, font=font(SANS, 12 * k), fill=(220, 220, 255))
        d.rectangle([384 * k, 18 * k, 458 * k, 42 * k], fill=(255, 204, 0), outline=BLACK, width=k)
        ctext(d, 421 * k, 30 * k, btn, font(SANS_B, 12 * k), BLACK)
        save(down(img, 468, 60), name, 64)


# ------------------------------------------------------------------ photos
def rng_for(slug):
    return random.Random(zlib.crc32(slug.encode()))


def sky(d, w, h, top, bottom, k):
    for y in range(h):
        t = y / float(h)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)


def label_box(d, W, H, k, text, R):
    """a little lower-third 'chyron' like the wire photos carried"""
    if not text:
        return
    f = font(SANS_B, 11 * k)
    w, h, b = tw(d, text, f)
    x, y = 8 * k, H - 26 * k
    d.rectangle([x, y, x + w + 12 * k, y + 18 * k], fill=(0, 0, 0))
    d.rectangle([x, y, x + 4 * k, y + 18 * k], fill=RED)
    d.text((x + 8 * k - b[0], y + 3 * k), text, font=f, fill=WHITE)


def person(d, cx, base, s, col, k):
    """head-and-shoulders silhouette; base = bottom y, s = scale"""
    d.ellipse([cx - 40 * s, base - 50 * s, cx + 40 * s, base + 40 * s], fill=col)
    d.rectangle([cx - 9 * s, base - 62 * s, cx + 9 * s, base - 45 * s], fill=col)
    d.ellipse([cx - 22 * s, base - 108 * s, cx + 22 * s, base - 56 * s], fill=col)


def draw_photo(kind, label, slug):
    W, H = 280, 170
    img, k = ss(W, H, (200, 200, 200))
    d = ImageDraw.Draw(img)
    R = rng_for(slug)
    Wk, Hk = W * k, H * k

    if kind in ("portrait", "podium"):
        bg = R.choice([(70, 90, 140), (120, 60, 60), (60, 110, 90), (110, 100, 70)])
        sky(d, Wk, Hk, tuple(min(255, c + 50) for c in bg), bg, k)
        if kind == "podium":
            # flags/curtain stripes behind
            for i in range(6):
                d.rectangle([(20 + i * 45) * k, 0, (32 + i * 45) * k, 90 * k], fill=tuple(min(255, c + 25) for c in bg))
        person(d, Wk / 2, 150 * k, 1.05 * k, (25, 25, 35), k)
        if kind == "podium":
            d.polygon([(90 * k, 112 * k), (190 * k, 112 * k), (180 * k, 170 * k), (100 * k, 170 * k)], fill=(120, 80, 40))
            d.rectangle([90 * k, 108 * k, 190 * k, 116 * k], fill=(150, 100, 50))
            ctext(d, 140 * k, 138 * k, "CNM", font(SANS_BI, 14 * k), (230, 200, 120))
            for mx in (125, 140, 155):
                d.line([(mx * k, 108 * k), ((mx + R.randint(-6, 6)) * k, 92 * k)], fill=(20, 20, 20), width=2 * k)
                d.ellipse([(mx - 4) * k, 86 * k, (mx + 4) * k, 96 * k], fill=(40, 40, 40))
    elif kind in ("chart_up", "chart_down"):
        d.rectangle([0, 0, Wk, Hk], fill=(10, 20, 50))
        for gx in range(30, 280, 30):
            d.line([(gx * k, 15 * k), (gx * k, 140 * k)], fill=(30, 50, 90), width=k)
        for gy in range(20, 145, 20):
            d.line([(30 * k, gy * k), (270 * k, gy * k)], fill=(30, 50, 90), width=k)
        n = 24
        y = 110 if kind == "chart_up" else 40
        pts = []
        for i in range(n):
            x = 30 + i * 240 / (n - 1)
            y += (-4 if kind == "chart_up" else 4) + R.uniform(-7, 7)
            y = max(18, min(138, y))
            pts.append((x * k, y * k))
        col = (0, 230, 90) if kind == "chart_up" else (255, 70, 60)
        d.polygon(pts + [(270 * k, 140 * k), (30 * k, 140 * k)], fill=tuple(c // 4 for c in col))
        d.line(pts, fill=col, width=3 * k)
        d.line([(30 * k, 140 * k), (270 * k, 140 * k)], fill=(200, 200, 200), width=k)
        d.line([(30 * k, 15 * k), (30 * k, 140 * k)], fill=(200, 200, 200), width=k)
        d.text((36 * k, 18 * k), label, font=font(SANS_B, 14 * k), fill=WHITE)
        arrow = "+" if kind == "chart_up" else "-"
        d.text((210 * k, 18 * k), arrow + "%d.%02d" % (R.randint(2, 99), R.randint(0, 99)), font=font(MONO_B, 13 * k), fill=col)
        label = None
    elif kind == "map":
        d.rectangle([0, 0, Wk, Hk], fill=(110, 160, 210))
        for gy in range(0, 170, 24):
            d.line([(0, gy * k), (Wk, gy * k)], fill=(130, 175, 220), width=k)
        for gx in range(0, 280, 24):
            d.line([(gx * k, 0), (gx * k, Hk)], fill=(130, 175, 220), width=k)
        blobs = R.randint(2, 4)
        for i in range(blobs):
            cx, cy, r = R.randint(40, 240), R.randint(30, 140), R.randint(25, 60)
            pts = []
            for a in range(0, 360, 20):
                rr = r * R.uniform(0.6, 1.25)
                pts.append(((cx + math.cos(math.radians(a)) * rr * 1.3) * k, (cy + math.sin(math.radians(a)) * rr) * k))
            d.polygon(pts, fill=(200, 190, 140), outline=(120, 110, 70))
        # dashed line (border / date line)
        x = R.randint(100, 180)
        for y0 in range(0, 170, 10):
            d.line([(x * k, y0 * k), ((x + 3) * k, (y0 + 6) * k)], fill=RED, width=2 * k)
        sx, sy = R.randint(60, 220), R.randint(40, 120)
        star = []
        for i in range(10):
            rr = 9 if i % 2 == 0 else 4
            a = math.radians(-90 + i * 36)
            star.append(((sx + math.cos(a) * rr) * k, (sy + math.sin(a) * rr) * k))
        d.polygon(star, fill=RED, outline=WHITE)
        d.rectangle([0, 0, Wk - 1, Hk - 1], outline=(40, 40, 40), width=2 * k)
        f = font(SANS_B, 12 * k)
        d.rectangle([6 * k, 6 * k, (14 + tw(d, label, f)[0] / k) * k, 24 * k], fill=WHITE, outline=BLACK)
        d.text((10 * k, 8 * k), label, font=f, fill=NAVY)
        label = None
    elif kind in ("skyline", "fireworks"):
        night = kind == "fireworks" or R.random() < 0.6
        sky(d, Wk, Hk, (5, 10, 40) if night else (120, 170, 230), (60, 40, 90) if night else (220, 230, 250), k)
        if kind == "fireworks":
            for i in range(5):
                cx, cy = R.randint(30, 250) * k, R.randint(20, 80) * k
                col = R.choice([(255, 80, 80), (255, 220, 60), (120, 200, 255), (200, 120, 255), (120, 255, 140)])
                for a in range(0, 360, 15):
                    r = R.randint(18, 30) * k
                    d.line([(cx, cy), (cx + math.cos(math.radians(a)) * r, cy + math.sin(math.radians(a)) * r)], fill=col, width=k)
        x = 0
        while x < W:
            bw, bh = R.randint(16, 34), R.randint(40, 110)
            col = (20, 20, 30) if night else (90, 100, 120)
            d.rectangle([x * k, (H - bh) * k, (x + bw) * k, Hk], fill=col)
            for wy in range(H - bh + 6, H - 4, 8):
                for wx in range(x + 3, x + bw - 3, 6):
                    if R.random() < (0.5 if night else 0.2):
                        d.rectangle([wx * k, wy * k, (wx + 2) * k, (wy + 3) * k], fill=(255, 230, 120) if night else (200, 220, 240))
            x += bw + R.randint(0, 4)
        if label == "LIGHTS":
            for i in range(300):
                px, py = R.randint(0, W), R.randint(90, H)
                d.ellipse([px * k, py * k, (px + 2) * k, (py + 2) * k], fill=R.choice([(255, 0, 0), (0, 255, 0), (255, 255, 0), (0, 160, 255)]))
    elif kind in ("snow", "storm", "mountains", "sun", "beach"):
        if kind == "snow":
            sky(d, Wk, Hk, (150, 160, 180), (220, 225, 235), k)
        elif kind == "storm":
            sky(d, Wk, Hk, (40, 40, 55), (120, 120, 130), k)
        elif kind == "sun":
            sky(d, Wk, Hk, (60, 140, 230), (250, 220, 170), k)
            d.ellipse([200 * k, 15 * k, 250 * k, 65 * k], fill=(255, 230, 80))
        elif kind == "beach":
            sky(d, Wk, Hk, (250, 140, 80), (255, 220, 150), k)
            d.ellipse([110 * k, 70 * k, 170 * k, 130 * k], fill=(255, 240, 120))
            d.rectangle([0, 100 * k, Wk, Hk], fill=(30, 90, 150))
            for y in range(104, 140, 6):
                d.line([(R.randint(80, 120) * k, y * k), (R.randint(160, 200) * k, y * k)], fill=(255, 220, 140), width=k)
            d.polygon([(0, 140 * k), (Wk, 128 * k), (Wk, Hk), (0, Hk)], fill=(230, 210, 150))
            # palm tree
            d.line([(40 * k, 160 * k), (55 * k, 70 * k)], fill=(70, 40, 20), width=5 * k)
            for a in (200, 230, 260, 300, 330, 350):
                d.line([(55 * k, 70 * k), ((55 + math.cos(math.radians(a)) * 40) * k, (70 - math.sin(math.radians(a)) * -20 + math.sin(math.radians(a)) * 30) * k)], fill=(20, 80, 30), width=4 * k)
            if label == "CRUISE":
                d.polygon([(150 * k, 104 * k), (250 * k, 104 * k), (240 * k, 116 * k), (158 * k, 116 * k)], fill=WHITE)
                d.rectangle([170 * k, 94 * k, 225 * k, 104 * k], fill=(240, 240, 240))
                d.rectangle([200 * k, 84 * k, 210 * k, 94 * k], fill=RED)
        else:
            sky(d, Wk, Hk, (90, 150, 230), (200, 225, 250), k)
        if kind in ("snow", "storm", "mountains"):
            for i in range(4):
                px = R.randint(-20, 260)
                ph = R.randint(60, 120)
                col = (110, 120, 140) if kind != "storm" else (60, 60, 70)
                d.polygon([(px * k, Hk), ((px + 70) * k, (H - ph) * k), ((px + 140) * k, Hk)], fill=col)
                d.polygon([((px + 52) * k, (H - ph + 18) * k), ((px + 70) * k, (H - ph) * k), ((px + 88) * k, (H - ph + 18) * k)], fill=WHITE)
        if kind == "sun":
            d.polygon([(0, 130 * k), (Wk, 120 * k), (Wk, Hk), (0, Hk)], fill=(210, 170, 110))
            for cx in (50, 120, 230):
                d.rectangle([cx * k, 90 * k, (cx + 8) * k, 140 * k], fill=(40, 120, 50))
                d.rectangle([(cx - 10) * k, 105 * k, (cx - 4) * k, 112 * k], fill=(40, 120, 50))
                d.rectangle([(cx - 10) * k, 98 * k, (cx - 6) * k, 112 * k], fill=(40, 120, 50))
                d.rectangle([(cx + 12) * k, 100 * k, (cx + 18) * k, 106 * k], fill=(40, 120, 50))
                d.rectangle([(cx + 14) * k, 92 * k, (cx + 18) * k, 106 * k], fill=(40, 120, 50))
            if label == "BUNKER":
                d.rectangle([140 * k, 120 * k, 190 * k, 135 * k], fill=(120, 120, 120), outline=BLACK)
                d.ellipse([155 * k, 116 * k, 175 * k, 126 * k], fill=(90, 90, 90), outline=BLACK)
        if kind == "snow":
            d.polygon([(0, 130 * k), (Wk, 120 * k), (Wk, Hk), (0, Hk)], fill=(245, 248, 255))
            for hx in (40, 150):
                d.rectangle([hx * k, 100 * k, (hx + 50) * k, 135 * k], fill=(150, 60, 50))
                d.polygon([((hx - 6) * k, 102 * k), ((hx + 25) * k, 78 * k), ((hx + 56) * k, 102 * k)], fill=WHITE)
                d.rectangle([(hx + 20) * k, 115 * k, (hx + 30) * k, 135 * k], fill=(80, 40, 30))
            if label == "CURLING":
                d.ellipse([200 * k, 138 * k, 260 * k, 160 * k], outline=RED, width=3 * k)
                d.ellipse([218 * k, 143 * k, 242 * k, 155 * k], outline=(0, 0, 200), width=3 * k)
            for i in range(160):
                px, py = R.randint(0, W), R.randint(0, H)
                d.ellipse([px * k, py * k, (px + 2) * k, (py + 2) * k], fill=WHITE)
        if kind == "storm":
            d.polygon([(0, 140 * k), (Wk, 135 * k), (Wk, Hk), (0, Hk)], fill=(220, 220, 230))
            for i in range(220):
                px, py = R.randint(0, W), R.randint(0, H)
                d.line([(px * k, py * k), ((px + 8) * k, (py + 3) * k)], fill=(240, 240, 250), width=k)
        if kind == "mountains":
            d.polygon([(0, 150 * k), (Wk, 140 * k), (Wk, Hk), (0, Hk)], fill=WHITE)
            d.line([(30 * k, 60 * k), (250 * k, 30 * k)], fill=(40, 40, 40), width=k)
            for cx in (80, 140, 200):
                d.rectangle([cx * k, (52 - (cx - 30) * 30 / 220) * k, (cx + 8) * k, (58 - (cx - 30) * 30 / 220) * k], fill=RED)
    elif kind == "clock":
        sky(d, Wk, Hk, (110, 150, 210), (210, 220, 240), k)
        d.rectangle([95 * k, 30 * k, 185 * k, Hk], fill=(170, 120, 90), outline=(90, 60, 40), width=k)
        d.polygon([(85 * k, 32 * k), (140 * k, 0), (195 * k, 32 * k)], fill=(90, 60, 40))
        d.ellipse([105 * k, 45 * k, 175 * k, 115 * k], fill=(250, 245, 230), outline=BLACK, width=2 * k)
        for i in range(12):
            a = math.radians(i * 30)
            d.line([((140 + math.sin(a) * 28) * k, (80 - math.cos(a) * 28) * k), ((140 + math.sin(a) * 33) * k, (80 - math.cos(a) * 33) * k)], fill=BLACK, width=2 * k)
        d.line([(140 * k, 80 * k), (140 * k, 54 * k)], fill=BLACK, width=3 * k)
        d.line([(140 * k, 80 * k), (137 * k, 60 * k)], fill=BLACK, width=4 * k)
        for wx in (110, 155):
            d.rectangle([wx * k, 128 * k, (wx + 15) * k, 155 * k], fill=(60, 50, 50))
    elif kind == "computer":
        d.rectangle([0, 0, Wk, Hk], fill=(120, 110, 100))
        d.rectangle([0, 130 * k, Wk, Hk], fill=(150, 110, 70))
        d.rectangle([70 * k, 18 * k, 210 * k, 120 * k], fill=(225, 215, 190), outline=(120, 110, 90), width=2 * k)
        d.rectangle([84 * k, 28 * k, 196 * k, 100 * k], fill=(0, 0, 120) if R.random() < 0.5 else (10, 40, 10))
        txt = label or "C:\\>"
        f = font(MONO_B, 15 * k)
        ctext(d, 140 * k, 56 * k, txt, f, (120, 255, 120))
        d.text((88 * k, 82 * k), "C:\\> _", font=font(MONO_B, 9 * k), fill=(200, 200, 200))
        d.rectangle([115 * k, 120 * k, 165 * k, 132 * k], fill=(200, 190, 165))
        d.polygon([(60 * k, 150 * k), (220 * k, 150 * k), (232 * k, 166 * k), (48 * k, 166 * k)], fill=(225, 215, 190), outline=(120, 110, 90))
        for r in range(3):
            for c in range(14):
                d.rectangle([(62 + c * 11 + r * 2) * k, (152 + r * 4.5) * k, (70 + c * 11 + r * 2) * k, (155.5 + r * 4.5) * k], fill=(190, 180, 160))
        d.ellipse([240 * k, 148 * k, 258 * k, 166 * k], fill=(225, 215, 190), outline=(120, 110, 90))
        label = None
    elif kind == "stadium":
        sky(d, Wk, Hk, (20, 20, 60), (80, 80, 120), k)
        for row in range(5):
            y = 20 + row * 10
            for x in range(0, 280, 5):
                d.ellipse([x * k, y * k, (x + 4) * k, (y + 4) * k], fill=R.choice([(200, 60, 60), (230, 230, 230), (60, 60, 200), (240, 200, 80), (90, 90, 90)]))
        d.polygon([(0, 75 * k), (Wk, 75 * k), (Wk, Hk), (0, Hk)], fill=(30, 130, 40))
        for i in range(0, 300, 30):
            d.line([((i - 20) * k, Hk), ((i + 20) * k, 75 * k)], fill=WHITE, width=k)
        for i in range(8):
            px, py = R.randint(20, 260), R.randint(95, 155)
            col = RED if i % 2 else (0, 0, 160)
            d.ellipse([px * k, py * k, (px + 8) * k, (py + 8) * k], fill=col)
            d.rectangle([(px + 1) * k, (py + 8) * k, (px + 7) * k, (py + 16) * k], fill=col)
        d.rectangle([200 * k, 4 * k, 274 * k, 18 * k], fill=BLACK, outline=(255, 200, 0))
        ctext(d, 237 * k, 11 * k, label or "", font(MONO_B, 10 * k), (255, 200, 0))
        label = None
    elif kind == "crowd":
        sky(d, Wk, Hk, (150, 170, 200), (230, 230, 230), k)
        d.rectangle([150 * k, 10 * k, 270 * k, 60 * k], fill=(160, 150, 140))
        for row in range(4):
            for i in range(14):
                cx = i * 22 + (row % 2) * 11 + R.randint(-3, 3)
                base = 100 + row * 22
                col = R.choice([(40, 40, 50), (70, 50, 40), (50, 60, 80), (90, 30, 30), (30, 60, 40)])
                person(d, cx * k, (base + 40) * k, 0.33 * k, col, k)
        sx = R.randint(40, 180)
        d.line([((sx + 30) * k, 60 * k), ((sx + 30) * k, 110 * k)], fill=(100, 70, 40), width=2 * k)
        d.rectangle([sx * k, 40 * k, (sx + 70) * k, 66 * k], fill=WHITE, outline=BLACK)
        size = 12
        f = font(SANS_B, size * k)
        while tw(d, label, f)[0] > 64 * k and size > 6:
            size -= 1
            f = font(SANS_B, size * k)
        ctext(d, (sx + 35) * k, 53 * k, label, f, RED)
        label = None
    elif kind in ("capitol", "courthouse"):
        sky(d, Wk, Hk, (110, 150, 210), (210, 225, 245), k)
        stone = (225, 220, 205)
        if kind == "capitol":
            d.ellipse([105 * k, 20 * k, 175 * k, 90 * k], fill=stone, outline=(150, 140, 120), width=k)
            d.rectangle([137 * k, 8 * k, 143 * k, 22 * k], fill=stone)
            d.rectangle([95 * k, 60 * k, 185 * k, 80 * k], fill=stone)
            d.rectangle([30 * k, 80 * k, 250 * k, 140 * k], fill=stone, outline=(150, 140, 120))
        else:
            d.polygon([(40 * k, 60 * k), (140 * k, 25 * k), (240 * k, 60 * k)], fill=stone, outline=(150, 140, 120))
            d.rectangle([45 * k, 60 * k, 235 * k, 70 * k], fill=stone, outline=(150, 140, 120))
            ctext(d, 140 * k, 48 * k, "JUSTICE", font(SERIF_B, 10 * k), (120, 110, 90))
            d.rectangle([45 * k, 130 * k, 235 * k, 140 * k], fill=stone)
        for cx in range(55, 235, 22):
            d.rectangle([cx * k, 72 * k, (cx + 9) * k, 130 * k], fill=(240, 236, 225), outline=(170, 160, 140))
        for st in range(3):
            d.rectangle([(30 - st * 10) * k, (140 + st * 8) * k, (250 + st * 10) * k, (148 + st * 8) * k], fill=(200, 195, 180), outline=(150, 140, 120))
    elif kind == "food":
        d.rectangle([0, 0, Wk, Hk], fill=(140, 30, 30))
        for x in range(0, 280, 20):
            for y in range(0, 170, 20):
                if (x + y) // 20 % 2 == 0:
                    d.rectangle([x * k, y * k, (x + 20) * k, (y + 20) * k], fill=(230, 230, 230))
        d.ellipse([60 * k, 30 * k, 220 * k, 150 * k], fill=(250, 250, 250), outline=(180, 180, 180), width=2 * k)
        d.ellipse([80 * k, 45 * k, 200 * k, 135 * k], fill=(240, 240, 240))
        if label in ("BUBBLY",):
            for bx in (110, 150):
                d.polygon([(bx * k, 40 * k), ((bx + 24) * k, 40 * k), ((bx + 18) * k, 90 * k), ((bx + 6) * k, 90 * k)], fill=(250, 230, 150), outline=(150, 130, 60))
                d.line([((bx + 12) * k, 90 * k), ((bx + 12) * k, 125 * k)], fill=(150, 130, 60), width=2 * k)
                d.line([((bx + 2) * k, 125 * k), ((bx + 22) * k, 125 * k)], fill=(150, 130, 60), width=2 * k)
        elif label in ("CAKE", "FRUITCAKE"):
            d.rectangle([95 * k, 65 * k, 185 * k, 115 * k], fill=(120, 70, 30), outline=(70, 40, 10), width=k)
            d.rectangle([95 * k, 60 * k, 185 * k, 70 * k], fill=(250, 240, 220) if label == "CAKE" else (150, 90, 40))
            for i in range(14):
                px, py = R.randint(98, 180), R.randint(72, 110)
                d.ellipse([px * k, py * k, (px + 5) * k, (py + 5) * k], fill=R.choice([(220, 0, 30), (0, 150, 40), (240, 200, 0)]))
        elif label == "MAMMOTH":
            d.ellipse([95 * k, 60 * k, 175 * k, 110 * k], fill=(150, 60, 40), outline=(90, 30, 20), width=k)
            d.rectangle([170 * k, 80 * k, 200 * k, 88 * k], fill=(240, 235, 220))
            for i in range(9):
                px, py = R.randint(100, 180), R.randint(110, 125)
                d.ellipse([px * k, py * k, (px + 7) * k, (py + 7) * k], fill=(60, 0, 120))
        else:  # pantry
            for i, cx in enumerate((100, 140, 180)):
                d.rectangle([(cx - 15) * k, 55 * k, (cx + 15) * k, 115 * k], fill=(190, 190, 200), outline=(100, 100, 110))
                d.rectangle([(cx - 15) * k, 70 * k, (cx + 15) * k, 100 * k], fill=[(200, 40, 40), (40, 120, 40), (230, 180, 0)][i])
        label = label if label not in ("CAKE",) else label
    elif kind == "globe":
        sky(d, Wk, Hk, (0, 0, 30), (20, 20, 80), k)
        for i in range(60):
            px, py = R.randint(0, W), R.randint(0, H)
            d.point((px * k, py * k), fill=WHITE)
        cx, cy, r = 140, 85, 65
        d.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], fill=(200, 230, 255) if label == "BUBBLE" else (30, 90, 180))
        for a in range(-60, 61, 30):
            yy = cy + math.sin(math.radians(a)) * r
            ww = math.cos(math.radians(a)) * r
            d.line([((cx - ww) * k, yy * k), ((cx + ww) * k, yy * k)], fill=(120, 160, 220), width=k)
        for i in range(-2, 3):
            d.ellipse([(cx - abs(i) * 20 - 3) * k, (cy - r) * k, (cx + abs(i) * 20 + 3) * k, (cy + r) * k], outline=(120, 160, 220), width=k)
        if label == "BUBBLE":
            d.rectangle([0, 130 * k, Wk, Hk], fill=(60, 60, 70))
            d.rectangle([0, 128 * k, Wk, 132 * k], fill=(180, 180, 190))
    elif kind == "space":
        d.rectangle([0, 0, Wk, Hk], fill=(0, 0, 10))
        for i in range(120):
            px, py = R.randint(0, W), R.randint(0, H)
            d.point((px * k, py * k), fill=WHITE)
        d.ellipse([150 * k, 30 * k, 320 * k, 200 * k], fill=(190, 80, 40))
        d.ellipse([210 * k, 30 * k, 260 * k, 50 * k], fill=(240, 240, 240))
        d.rectangle([50 * k, 60 * k, 90 * k, 85 * k], fill=(200, 200, 210), outline=(120, 120, 120))
        d.rectangle([10 * k, 66 * k, 50 * k, 79 * k], fill=(40, 60, 160))
        d.rectangle([90 * k, 66 * k, 130 * k, 79 * k], fill=(40, 60, 160))
        d.ellipse([60 * k, 45 * k, 80 * k, 62 * k], outline=(220, 220, 220), width=2 * k)
    elif kind == "airplane":
        sky(d, Wk, Hk, (60, 120, 210), (210, 230, 250), k)
        for i in range(4):
            cx, cy = R.randint(0, 280), R.randint(10, 80)
            for dx in (0, 14, 28):
                d.ellipse([(cx + dx) * k, cy * k, (cx + dx + 26) * k, (cy + 14) * k], fill=(250, 250, 255))
        d.polygon([(40 * k, 100 * k), (220 * k, 70 * k), (240 * k, 72 * k), (232 * k, 80 * k), (60 * k, 112 * k)], fill=WHITE, outline=(80, 80, 90))
        d.polygon([(120 * k, 88 * k), (170 * k, 50 * k), (182 * k, 52 * k), (150 * k, 85 * k)], fill=(220, 220, 230), outline=(80, 80, 90))
        d.polygon([(110 * k, 94 * k), (150 * k, 120 * k), (162 * k, 118 * k), (138 * k, 90 * k)], fill=(220, 220, 230), outline=(80, 80, 90))
        d.polygon([(40 * k, 100 * k), (30 * k, 70 * k), (42 * k, 70 * k), (62 * k, 98 * k)], fill=RED)
        d.rectangle([0, 150 * k, Wk, Hk], fill=(80, 80, 80))
        for x in range(0, 280, 30):
            d.rectangle([x * k, 158 * k, (x + 15) * k, 161 * k], fill=WHITE)
    elif kind == "store":
        d.rectangle([0, 0, Wk, Hk], fill=(230, 220, 200))
        d.rectangle([0, 0, Wk, 30 * k], fill=(180, 30, 40))
        ctext(d, 140 * k, 15 * k, label or "SALE", font(SANS_B, 16 * k), WHITE)
        for sy in (45, 85, 125):
            d.rectangle([10 * k, (sy + 26) * k, 270 * k, (sy + 30) * k], fill=(120, 80, 40))
            x = 14
            while x < 262:
                bw = R.randint(10, 22)
                bh = R.randint(14, 26)
                d.rectangle([x * k, (sy + 26 - bh) * k, (x + bw) * k, (sy + 26) * k],
                            fill=R.choice([(200, 50, 50), (50, 120, 200), (240, 200, 60), (90, 170, 90), (200, 120, 200)]), outline=(60, 60, 60))
                x += bw + 3
        label = None
    elif kind == "ecg":
        d.rectangle([0, 0, Wk, Hk], fill=(0, 20, 0))
        for gx in range(0, 280, 14):
            d.line([(gx * k, 0), (gx * k, Hk)], fill=(0, 60, 0), width=k)
        for gy in range(0, 170, 14):
            d.line([(0, gy * k), (Wk, gy * k)], fill=(0, 60, 0), width=k)
        pts = []
        x = 0
        while x < 280:
            pts += [(x, 90), (x + 20, 90), (x + 25, 80), (x + 30, 90), (x + 36, 90), (x + 40, 40), (x + 45, 120), (x + 50, 90), (x + 70, 90)]
            x += 70
        d.line([(px * k, py * k) for px, py in pts], fill=(60, 255, 60), width=2 * k)
        d.text((10 * k, 8 * k), "101.8 F", font=font(MONO_B, 14 * k), fill=(60, 255, 60))
    elif kind == "mannequin":
        d.rectangle([0, 0, Wk, Hk], fill=(60, 30, 70))
        for i in range(40):
            px, py = R.randint(0, W), R.randint(0, H)
            d.ellipse([px * k, py * k, (px + 3) * k, (py + 3) * k], fill=(220, 200, 255))
        col = (200, 200, 215) if label == "SILVER" else (110, 120, 80)
        d.ellipse([125 * k, 12 * k, 155 * k, 44 * k], fill=(230, 210, 190))
        d.polygon([(110 * k, 50 * k), (170 * k, 50 * k), (160 * k, 95 * k), (195 * k, 165 * k), (85 * k, 165 * k), (120 * k, 95 * k)], fill=col, outline=WHITE)
        if label == "CARGO":
            for py in (110, 135):
                d.rectangle([100 * k, py * k, 120 * k, (py + 16) * k], outline=(60, 60, 40), width=k)
                d.rectangle([160 * k, py * k, 180 * k, (py + 16) * k], outline=(60, 60, 40), width=k)
        d.rectangle([60 * k, 0, 70 * k, Hk], fill=(90, 50, 100))
        d.rectangle([210 * k, 0, 220 * k, Hk], fill=(90, 50, 100))
    elif kind == "trophy":
        sky(d, Wk, Hk, (40, 40, 80), (10, 10, 30), k)
        gold = (220, 180, 40)
        d.rectangle([105 * k, 135 * k, 175 * k, 160 * k], fill=(80, 50, 20))
        d.rectangle([128 * k, 105 * k, 152 * k, 135 * k], fill=gold)
        d.ellipse([90 * k, 40 * k, 190 * k, 110 * k], fill=gold, outline=(150, 110, 10), width=2 * k)
        for i in range(10):
            px, py = R.randint(105, 170), R.randint(55, 95)
            d.ellipse([px * k, py * k, (px + 6) * k, (py + 6) * k], fill=(150, 110, 10))
        d.arc([60 * k, 45 * k, 105 * k, 90 * k], 90, 270, fill=gold, width=5 * k)
        d.arc([175 * k, 45 * k, 220 * k, 90 * k], 270, 90, fill=gold, width=5 * k)
    else:
        d.rectangle([0, 0, Wk, Hk], fill=(150, 150, 150))

    if kind in ("portrait", "podium", "skyline", "fireworks", "snow", "storm", "mountains", "sun", "beach", "clock",
                "capitol", "courthouse", "food", "globe", "space", "airplane", "ecg", "mannequin", "trophy"):
        label_box(d, Wk, Hk, k, label, R)
    # CNM photo credit bug
    f = font(SANS_B, 8 * k)
    d.text((Wk - 30 * k, Hk - 12 * k), "CNM", font=f, fill=(255, 255, 255))
    return down(img, W, H)


def story_photos():
    for s in data.STORIES:
        if not s["photo"]:
            continue
        kind, label = s["photo"]
        im = draw_photo(kind, label, s["slug"])
        save(im, "photo_%s.gif" % s["slug"], 128)
        save(im.resize((55, 45), Image.LANCZOS), "thumb_%s.gif" % s["slug"], 64)
        save(im.resize((220, 134), Image.LANCZOS), "photo220_%s.gif" % s["slug"], 128)


def video_still():
    W, H = 320, 240
    img, k = ss(W, H, (20, 40, 90))
    d = ImageDraw.Draw(img)
    sky(d, W * k, H * k, (20, 40, 110), (10, 15, 50), k)
    for i in range(8):
        d.ellipse([(i * 45 - 20) * k, 20 * k, (i * 45 + 20) * k, 60 * k], outline=(40, 70, 150), width=k)
    person(d, 160 * k, 205 * k, 1.25 * k, (30, 30, 40), k)
    d.rectangle([0, 170 * k, W * k, H * k], fill=(120, 80, 50))
    d.rectangle([0, 166 * k, W * k, 172 * k], fill=(160, 110, 70))
    d.rectangle([10 * k, 190 * k, 210 * k, 212 * k], fill=BLACK)
    d.rectangle([10 * k, 190 * k, 16 * k, 212 * k], fill=RED)
    d.text((22 * k, 193 * k), "NOR'EASTER BURIES MAINE", font=font(SANS_B, 12 * k), fill=WHITE)
    d.rectangle([250 * k, 12 * k, 306 * k, 30 * k], fill=RED)
    ctext(d, 278 * k, 21 * k, "LIVE", font(SANS_B, 13 * k), WHITE)
    d.rectangle([258 * k, 196 * k, 310 * k, 214 * k], fill=RED)
    ctext(d, 284 * k, 205 * k, "CNM", font(SANS_BI, 13 * k), WHITE)
    im = down(img, W, H)
    save(im, "video_still.gif", 128)
    save(im.resize((55, 45), Image.LANCZOS), "oncnm.gif", 64)
    save(im.resize((150, 112), Image.LANCZOS), "video_small.gif", 128)


def y2k_banner():
    W, H = 630, 80
    img, k = ss(W, H, BLACK)
    d = ImageDraw.Draw(img)
    R = random.Random(2000)
    f = font(MONO_B, 9 * k)
    for y in range(0, 80, 10):
        line = "".join(R.choice("01") for _ in range(110))
        d.text((0, y * k), line, font=f, fill=(0, 70, 0))
    d.rectangle([0, 0, 120 * k, 80 * k], fill=RED)
    ctext(d, 60 * k, 30 * k, "Y2K", font(SANS_BI, 34 * k), WHITE)
    ctext(d, 60 * k, 60 * k, "SPECIAL REPORT", font(SANS_B, 10 * k), (255, 220, 220))
    d.text((136 * k, 8 * k), "THE MILLENNIUM BUG", font=font(SANS_B, 30 * k), fill=WHITE)
    d.text((138 * k, 46 * k), "19100? 2000? 1900? ... Is your world ready?", font=font(SANS_B, 15 * k), fill=(255, 204, 0))
    save(down(img, W, H), "y2k_banner.gif", 64)
    # small Y2K promo for the front page
    img, k = ss(150, 40, BLACK)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 40 * k, 40 * k], fill=RED)
    ctext(d, 20 * k, 20 * k, "Y2K", font(SANS_BI, 14 * k), WHITE)
    d.text((46 * k, 4 * k), "SPECIAL", font=font(SANS_B, 12 * k), fill=WHITE)
    d.text((46 * k, 20 * k), "REPORT >>", font=font(SANS_B, 12 * k), fill=(255, 204, 0))
    save(down(img, 150, 40), "y2k_promo.gif", 32)


def world_map():
    """invented world map with millennium midnight markers"""
    W, H = 600, 260
    img, k = ss(W, H, (100, 150, 205))
    d = ImageDraw.Draw(img)
    R = random.Random(1999)
    for x in range(0, W, 25):
        d.line([(x * k, 0), (x * k, H * k)], fill=(120, 165, 215), width=k)
    conts = [(90, 80, 70), (120, 180, 55), (290, 70, 60), (310, 170, 50), (450, 90, 80), (500, 200, 35)]
    for cx, cy, r in conts:
        pts = []
        for a in range(0, 360, 15):
            rr = r * R.uniform(0.65, 1.2)
            pts.append(((cx + math.cos(math.radians(a)) * rr * 1.2) * k, (cy + math.sin(math.radians(a)) * rr) * k))
        d.polygon(pts, fill=(205, 195, 145), outline=(120, 110, 70))
    for x, y in ((560, 120), (572, 135), (585, 110)):
        d.ellipse([(x - 4) * k, (y - 3) * k, (x + 4) * k, (y + 3) * k], fill=(205, 195, 145), outline=(120, 110, 70))
    for y0 in range(0, H, 10):
        d.line([(592 * k, y0 * k), (594 * k, (y0 + 6) * k)], fill=RED, width=2 * k)
    f = font(SANS_B, 10 * k)
    places = [(572, 128, "Marisol Is."), (520, 160, "Tavai"), (300, 62, "Esterhaal"), (330, 92, "Ostravia"), (280, 100, "Bruskia"),
              (310, 175, "Tamberlay"), (120, 175, "Sandovar"), (150, 140, "Vellmark"), (95, 80, "U.S.")]
    for x, y, t in places:
        d.ellipse([(x - 3) * k, (y - 3) * k, (x + 3) * k, (y + 3) * k], fill=RED, outline=WHITE)
        if x > 540:
            d.text(((x - 5) * k - tw(d, t, f)[0], (y - 6) * k), t, font=f, fill=BLACK)
        else:
            d.text(((x + 5) * k, (y - 6) * k), t, font=f, fill=BLACK)
    d.text((8 * k, 240 * k), "Midnight sweeps west from the date line (red dashes)", font=font(SANS_B, 11 * k), fill=NAVY)
    save(down(img, W, H), "world_map.gif", 64)


def titles():
    for code, nav, dirn, text, blurb in data.SECTIONS:
        title_bar("sec_%s.gif" % dirn.lower(), text)
    for name, text, sub in [("sec_y2k.gif", "Y2K", "SPECIAL REPORT"), ("sec_quickvote.gif", "QUICKVOTE", None),
                            ("sec_search.gif", "SEARCH", None), ("sec_almanac.gif", "DAILY ALMANAC", None),
                            ("sec_quiz.gif", "NEWS QUIZ", None), ("sec_brief.gif", "HEADLINE NEWS", "BRIEF"),
                            ("sec_video.gif", "VIDEO", None), ("sec_audio.gif", "AUDIO", None),
                            ("sec_customnews.gif", "CUSTOM NEWS", None), ("sec_feedback.gif", "FEEDBACK", None),
                            ("sec_privacy.gif", "PRIVACY", None), ("sec_terms.gif", "TERMS", None),
                            ("sec_local.gif", "LOCAL", None), ("sec_indepth.gif", "IN-DEPTH", "SPECIALS"),
                            ("sec_email.gif", "FREE E-MAIL", None), ("sec_forecast.gif", "WEATHER", "FORECASTS")]:
        title_bar(name, text, sub)


def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    logo()
    small_bits()
    titles()
    weather_icons()
    us_map()
    led_digits()
    banners()
    video_still()
    y2k_banner()
    world_map()
    story_photos()
    print("graphics written to", os.path.normpath(OUT), "-", len([f for f in os.listdir(OUT) if f.endswith(".gif")]), "GIFs")


if __name__ == "__main__":
    main()
