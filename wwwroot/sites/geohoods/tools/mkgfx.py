#!/usr/bin/env python3
"""mkgfx.py -- draw every GeoHoods GIF from scratch with Pillow.

All artwork is original and procedural: the GeoHoods logo, neighborhood icons and banners, fake ad banners,
and a big pile of 1999 member-page clip art (flames, spinning skulls, e-mail envelopes, under-construction
workers, a dancing diaper baby, rainbow rules, guestbook buttons, award badges, UFOs, kittens, critters,
tiled backgrounds, counters, 88x31 buttons ...).

Usage:  python3 tools/mkgfx.py          (writes into ../images/)
"""
import math
import os
import random
import sys

sys.dont_write_bytecode = True

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gh_hoods import HOODS  # noqa: E402

OUT = os.path.join(HERE, '..', 'images')
STOCK = os.path.abspath(os.path.join(HERE, '..', '..', '..', 'images'))
KEY = (255, 0, 254)          # transparent key colour (never used in drawings)
R = random.Random(1999)

# ------------------------------------------------------------------ fonts
FONT_FILES = {
    'sans': ['LiberationSans-Regular.ttf', 'DejaVuSans.ttf', 'FreeSans.ttf'],
    'sansb': ['LiberationSans-Bold.ttf', 'DejaVuSans-Bold.ttf', 'FreeSansBold.ttf'],
    'sansbi': ['LiberationSans-BoldItalic.ttf', 'FreeSansBoldOblique.ttf', 'DejaVuSans-Bold.ttf'],
    'serifb': ['LiberationSerif-Bold.ttf', 'DejaVuSerif-Bold.ttf', 'FreeSerifBold.ttf'],
    'serifbi': ['LiberationSerif-BoldItalic.ttf', 'FreeSerifBoldItalic.ttf', 'DejaVuSerif-Bold.ttf'],
    'mono': ['LiberationMono-Bold.ttf', 'DejaVuSansMono-Bold.ttf', 'FreeMonoBold.ttf'],
    'narrow': ['LiberationSansNarrow-Bold.ttf', 'Ubuntu-C.ttf', 'LiberationSans-Bold.ttf', 'DejaVuSans-Bold.ttf'],
    'round': ['Ubuntu-B.ttf', 'LiberationSans-Bold.ttf', 'DejaVuSans-Bold.ttf'],
}
_fidx = None
_fcache = {}


def font(kind, size):
    global _fidx
    if (kind, size) in _fcache:
        return _fcache[(kind, size)]
    if _fidx is None:
        _fidx = {}
        for d in ['/usr/share/fonts', '/usr/local/share/fonts', os.path.expanduser('~/.fonts'),
                  '/Library/Fonts', 'C:/Windows/Fonts']:
            for dp, _dn, fns in os.walk(d):
                for fn in fns:
                    _fidx.setdefault(fn.lower(), os.path.join(dp, fn))
    f = None
    for name in FONT_FILES[kind]:
        p = _fidx.get(name.lower())
        if p:
            try:
                f = ImageFont.truetype(p, size)
                break
            except OSError:
                pass
    if f is None:
        f = ImageFont.load_default()
    _fcache[(kind, size)] = f
    return f


def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def hsv(h, s=1.0, v=1.0):
    import colorsys
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def canvas(w, h, bg=KEY):
    im = Image.new('RGB', (w, h), bg)
    d = ImageDraw.Draw(im)
    d.fontmode = '1'          # no anti-aliasing: crisp 1999 pixels
    return im, d


def tsize(d, text, f):
    b = d.textbbox((0, 0), text, font=f)
    return b[2] - b[0], b[3] - b[1], b[0], b[1]


def ctext(d, box, text, f, fill, shadow=None, outline=None):
    """centre text in box (x0,y0,x1,y1)"""
    w, h, ox, oy = tsize(d, text, f)
    x = box[0] + (box[2] - box[0] - w) // 2 - ox
    y = box[1] + (box[3] - box[1] - h) // 2 - oy
    if outline:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    d.text((x + dx, y + dy), text, font=f, fill=outline)
    if shadow:
        d.text((x + 1, y + 1), text, font=f, fill=shadow)
    d.text((x, y), text, font=f, fill=fill)
    return x, y


# ------------------------------------------------------------------ saving
def save(name, frames, dur=100, transparent=None, loop=0):
    """save one or more RGB frames as a (possibly animated) GIF.
    Pixels equal to KEY become transparent."""
    if not isinstance(frames, (list, tuple)):
        frames = [frames]
    frames = [f.convert('RGB') for f in frames]
    if transparent is None:
        transparent = any(KEY in [c for _n, c in (f.getcolors(1 << 20) or [])] for f in frames)
    w, h = frames[0].size
    tall = Image.new('RGB', (w, h * len(frames)))
    masks = []
    for i, f in enumerate(frames):
        m = f.copy()
        px = f.load()
        mk = Image.new('1', (w, h), 0)
        mpx = mk.load()
        g = m.load()
        for y in range(h):
            for x in range(w):
                if px[x, y] == KEY:
                    mpx[x, y] = 1
                    g[x, y] = (0, 0, 0)
        masks.append(mk)
        tall.paste(m, (0, h * i))
    ncol = 255 if transparent else 256
    pal_img = tall.quantize(colors=ncol, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = pal_img.getpalette()[:768]
    pal += [0] * (768 - len(pal))
    if transparent:
        pal[765:768] = [254, 1, 253]
        pal_img.putpalette(pal)
    out = []
    for i, f in enumerate(frames):
        q = tall.crop((0, h * i, w, h * (i + 1))).quantize(palette=pal_img, dither=Image.Dither.NONE)
        if transparent:
            q.paste(255, (0, 0), masks[i])
            p2 = list(pal)
            p2[765:768] = list(KEY)
            q.putpalette(p2)
        out.append(q)
    path = os.path.join(OUT, name)
    kw = dict(save_all=len(out) > 1, optimize=False)
    if len(out) > 1:
        kw.update(append_images=out[1:], duration=dur, loop=loop, disposal=2)
    if transparent:
        kw['transparency'] = 255
    out[0].save(path, **kw)
    return path


# ================================================================== portal art
def house(d, x, y, s, wall, roof, door=(90, 50, 20)):
    d.rectangle((x, y + s // 2, x + s, y + s + s // 3), fill=wall, outline=(0, 0, 0))
    d.polygon([(x - 2, y + s // 2), (x + s // 2, y), (x + s + 2, y + s // 2)], fill=roof, outline=(0, 0, 0))
    d.rectangle((x + s // 2 - 2, y + s - 2, x + s // 2 + 2, y + s + s // 3), fill=door)
    d.rectangle((x + 2, y + s // 2 + 3, x + 5, y + s // 2 + 6), fill=(255, 255, 160))


def logo():
    w, h = 300, 54
    im, d = canvas(w, h, (255, 255, 255))
    cols = [((255, 204, 0), (204, 0, 0)), ((102, 204, 255), (0, 51, 153)), ((153, 255, 102), (0, 102, 0))]
    for i, (wall, roof) in enumerate(cols):
        house(d, 6 + i * 20, 14 + (i % 2) * 4, 16, wall, roof)
    d.line((2, 44, 70, 44), fill=(0, 120, 0), width=2)
    f = font('serifbi', 34)
    x = 74
    for i, ch in enumerate('GeoHoods'):
        col = [(0, 51, 153), (204, 0, 0), (0, 128, 0), (255, 153, 0)][i % 4] if i < 3 else (0, 51, 153)
        d.text((x + 2, 4), ch, font=f, fill=(170, 170, 170))
        d.text((x, 2), ch, font=f, fill=col)
        x += int(f.getlength(ch))
    f2 = font('sans', 10)
    d.text((76, 40), 'Free Home Pages  *  Neighborhoods  *  Fun', font=f2, fill=(80, 80, 80))
    save('gh_logo.gif', im, transparent=False)

    # small 88x31 badge for member pages
    im, d = canvas(88, 31, (255, 255, 255))
    d.rectangle((0, 0, 87, 30), outline=(0, 51, 153))
    house(d, 4, 4, 12, (255, 204, 0), (204, 0, 0))
    ctext(d, (20, 1, 87, 17), 'GeoHoods', font('serifbi', 13), (0, 51, 153))
    ctext(d, (20, 16, 87, 30), 'free pages!', font('sans', 9), (204, 0, 0))
    save('gh_88x31.gif', im, transparent=False)

    # corner watermark (the famous translucent-looking tab)
    im, d = canvas(48, 40)
    for yy in range(40):
        for xx in range(48):
            if (xx + yy) % 2 == 0:
                d.point((xx, yy), fill=(200, 200, 255))
    house(d, 14, 4, 18, (255, 255, 255), (102, 102, 204), (102, 102, 204))
    ctext(d, (0, 29, 48, 40), 'GeoHoods', font('sans', 8), (51, 51, 153))
    save('gh_watermark.gif', im)

    # big navy portal buttons
    for name, label, sub, icon in [('btn_build.gif', 'Build a Page', 'free & easy', 'trowel'),
                                   ('btn_edit.gif', 'Edit Pages', 'File Manager', 'pencil'),
                                   ('btn_join.gif', 'Move In!', 'claim an address', 'key')]:
        im, d = canvas(199, 66, (0, 51, 153))
        for yy in range(66):
            d.line((0, yy, 198, yy), fill=mix((0, 51, 153), (0, 20, 90), yy / 66))
        d.rectangle((0, 0, 198, 65), outline=(102, 153, 255))
        d.ellipse((10, 10, 56, 56), fill=(255, 204, 0), outline=(255, 255, 255))
        if icon == 'trowel':
            d.polygon([(22, 40), (38, 22), (46, 30), (30, 46)], fill=(192, 192, 192), outline=(0, 0, 0))
            d.line((40, 26, 50, 16), fill=(120, 60, 0), width=4)
        elif icon == 'pencil':
            d.polygon([(20, 46), (24, 36), (44, 16), (50, 22), (30, 42)], fill=(255, 102, 0), outline=(0, 0, 0))
            d.polygon([(20, 46), (24, 36), (30, 42)], fill=(255, 220, 170), outline=(0, 0, 0))
        else:
            d.ellipse((18, 24, 32, 38), outline=(0, 0, 0), width=3)
            d.line((31, 31, 48, 31), fill=(0, 0, 0), width=3)
            d.line((44, 31, 44, 37), fill=(0, 0, 0), width=2)
        d.text((68, 14), label, font=font('sansb', 18), fill=(255, 255, 255))
        d.text((70, 40), sub, font=font('sans', 12), fill=(255, 255, 153))
        save(name, im, transparent=False)

    # JOIN NOW blinker
    frames = []
    for i in range(4):
        im, d = canvas(120, 40, (204, 0, 0) if i % 2 == 0 else (255, 204, 0))
        d.rectangle((0, 0, 119, 39), outline=(0, 0, 0))
        ctext(d, (0, 0, 120, 24), 'JOIN NOW!', font('sansb', 17),
              (255, 255, 0) if i % 2 == 0 else (204, 0, 0), shadow=(0, 0, 0))
        ctext(d, (0, 22, 120, 38), "it's FREE!", font('sansbi', 11), (255, 255, 255) if i % 2 == 0 else (0, 0, 0))
        frames.append(im)
    save('join_now.gif', frames, 450, transparent=False)

    # section header tabs
    for name, text, col in [('hdr_cool.gif', 'Cool Page of the Day', (255, 102, 0)),
                            ('hdr_hoods.gif', 'Explore Neighborhoods', (0, 102, 0)),
                            ('hdr_featured.gif', 'Featured Homesteaders', (153, 0, 153)),
                            ('hdr_news.gif', 'What\'s New in the Hood', (0, 51, 153))]:
        im, d = canvas(200, 22, col)
        d.polygon([(0, 0), (190, 0), (199, 11), (190, 21), (0, 21)], fill=col)
        d.rectangle((0, 0, 3, 21), fill=(255, 255, 255))
        d.text((10, 3), text, font=font('sansb', 13), fill=(255, 255, 255))
        save(name, im, transparent=False)

    # sunglasses "cool" badge animated
    frames = []
    for i in range(6):
        im, d = canvas(64, 64)
        d.ellipse((4, 4, 60, 60), fill=(255, 220, 0), outline=(0, 0, 0))
        d.rectangle((12, 22, 30, 32), fill=(0, 0, 0))
        d.rectangle((34, 22, 52, 32), fill=(0, 0, 0))
        d.line((30, 25, 34, 25), fill=(0, 0, 0), width=2)
        if i in (2, 3):
            d.line((15 + i * 2, 24, 18 + i * 2, 27), fill=(255, 255, 255))
            d.line((37 + i * 2, 24, 40 + i * 2, 27), fill=(255, 255, 255))
        d.arc((18, 30, 46, 50), 20, 160, fill=(0, 0, 0), width=2)
        frames.append(im)
    save('cool_face.gif', frames, 250)

    im, d = canvas(1, 1)
    save('spacer.gif', im)
    im, d = canvas(9, 9)
    d.polygon([(1, 0), (8, 4), (1, 8)], fill=(204, 0, 0))
    save('arrow.gif', im)


ICON_DRAW = {}


def icon(kind, s=32):
    im, d = canvas(s, s)
    k = s / 32.0

    def P(*pts):
        return [(int(x * k), int(y * k)) for x, y in pts]

    def B(x0, y0, x1, y1):
        return (int(x0 * k), int(y0 * k), int(x1 * k), int(y1 * k))
    if kind == 'chip':
        d.rectangle(B(7, 7, 25, 25), fill=(40, 40, 40), outline=(0, 0, 0))
        for i in range(4):
            for (x0, y0, x1, y1) in [(9 + i * 4, 2, 10 + i * 4, 7), (9 + i * 4, 25, 10 + i * 4, 30),
                                     (2, 9 + i * 4, 7, 10 + i * 4), (25, 9 + i * 4, 30, 10 + i * 4)]:
                d.rectangle(B(x0, y0, x1, y1), fill=(220, 190, 60))
        d.text((int(9 * k), int(10 * k)), 'GH', font=font('sansb', int(9 * k)), fill=(0, 200, 0))
    elif kind == 'film':
        d.ellipse(B(2, 2, 30, 30), fill=(160, 160, 170), outline=(0, 0, 0))
        for a in range(0, 360, 60):
            cx, cy = 16 + 8 * math.cos(math.radians(a)), 16 + 8 * math.sin(math.radians(a))
            d.ellipse(B(cx - 3, cy - 3, cx + 3, cy + 3), fill=(60, 60, 60))
        d.ellipse(B(14, 14, 18, 18), fill=(0, 0, 0))
    elif kind == 'football':
        d.ellipse(B(2, 8, 30, 24), fill=(140, 70, 20), outline=(0, 0, 0))
        d.line(P((10, 16), (22, 16)), fill=(255, 255, 255), width=1)
        for x in range(12, 22, 3):
            d.line(P((x, 14), (x, 18)), fill=(255, 255, 255))
    elif kind == 'ufo':
        d.ellipse(B(10, 6, 22, 18), fill=(150, 220, 255), outline=(0, 0, 0))
        d.ellipse(B(2, 12, 30, 22), fill=(170, 170, 190), outline=(0, 0, 0))
        for x in (7, 13, 19, 25):
            d.ellipse(B(x - 1, 16, x + 1, 18), fill=(255, 255, 0))
        d.polygon(P((12, 22), (20, 22), (26, 31), (6, 31)), fill=(200, 255, 150))
    elif kind == 'note':
        d.ellipse(B(4, 20, 14, 28), fill=(0, 0, 0))
        d.ellipse(B(18, 17, 28, 25), fill=(0, 0, 0))
        d.line(P((13, 24), (13, 5)), fill=(0, 0, 0), width=max(1, int(2 * k)))
        d.line(P((27, 21), (27, 2)), fill=(0, 0, 0), width=max(1, int(2 * k)))
        d.polygon(P((13, 5), (27, 2), (27, 7), (13, 10)), fill=(0, 0, 0))
    elif kind == 'house':
        house(d, int(5 * k), int(4 * k), int(22 * k), (255, 230, 170), (180, 40, 20))
        d.polygon(P((24, 4), (26, 2), (28, 4), (26, 7)), fill=(255, 0, 80))
    elif kind == 'paw':
        d.ellipse(B(9, 14, 23, 28), fill=(120, 70, 30))
        for (x, y) in [(5, 9), (11, 4), (19, 4), (25, 9)]:
            d.ellipse(B(x - 3, y - 3, x + 3, y + 4), fill=(120, 70, 30))
    elif kind == 'heel':
        d.polygon(P((3, 24), (8, 14), (20, 22), (29, 22), (29, 26), (6, 26)), fill=(220, 0, 120), outline=(0, 0, 0))
        d.line(P((27, 26), (28, 31)), fill=(0, 0, 0), width=2)
        d.polygon(P((8, 14), (12, 8), (15, 18)), fill=(255, 120, 200), outline=(0, 0, 0))
    elif kind == 'book':
        d.polygon(P((2, 8), (16, 11), (30, 8), (30, 27), (16, 30), (2, 27)), fill=(255, 255, 240), outline=(0, 0, 0))
        d.line(P((16, 11), (16, 30)), fill=(0, 0, 0))
        for y in range(14, 26, 3):
            d.line(P((5, y), (13, y + 1)), fill=(120, 120, 120))
            d.line(P((19, y + 1), (27, y)), fill=(120, 120, 120))
        d.line(P((22, 4), (16, 11)), fill=(200, 0, 0), width=2)
    elif kind == 'joystick':
        d.rectangle(B(4, 20, 28, 29), fill=(40, 40, 40), outline=(0, 0, 0))
        d.line(P((16, 21), (13, 8)), fill=(80, 80, 80), width=max(1, int(3 * k)))
        d.ellipse(B(9, 2, 17, 10), fill=(220, 0, 0), outline=(0, 0, 0))
        d.ellipse(B(21, 22, 26, 26), fill=(255, 200, 0))
    elif kind == 'cap':
        d.polygon(P((2, 12), (16, 6), (30, 12), (16, 18)), fill=(20, 20, 20), outline=(90, 90, 90))
        d.rectangle(B(9, 15, 23, 22), fill=(20, 20, 20))
        d.line(P((28, 12), (28, 24)), fill=(255, 204, 0), width=2)
    elif kind == 'bunker':
        d.ellipse(B(2, 2, 30, 30), fill=(255, 220, 0), outline=(0, 0, 0))
        d.ellipse(B(13, 13, 19, 19), fill=(0, 0, 0))
        for a in (90, 210, 330):
            d.pieslice(B(4, 4, 28, 28), a - 30 - 90, a + 30 - 90, fill=(0, 0, 0))
        d.ellipse(B(11, 11, 21, 21), fill=(255, 220, 0))
        d.ellipse(B(13, 13, 19, 19), fill=(0, 0, 0))
    elif kind == 'palm':
        d.ellipse(B(0, 24, 32, 36), fill=(240, 220, 150))
        d.line(P((16, 28), (18, 10)), fill=(130, 80, 30), width=max(1, int(3 * k)))
        for dx, dy in [(-12, 4), (12, 4), (-9, -4), (9, -5), (0, -8)]:
            d.line(P((18, 10), (18 + dx, 10 + dy)), fill=(0, 140, 0), width=max(1, int(3 * k)))
        d.ellipse(B(24, 1, 31, 8), fill=(255, 230, 0))
    elif kind == 'pan':
        d.ellipse(B(2, 10, 22, 28), fill=(50, 50, 50), outline=(0, 0, 0))
        d.ellipse(B(6, 14, 18, 24), fill=(255, 230, 120))
        d.ellipse(B(9, 16, 14, 21), fill=(255, 170, 0))
        d.line(P((21, 18), (31, 14)), fill=(40, 40, 40), width=max(1, int(3 * k)))
    elif kind == 'hammer':
        d.line(P((8, 28), (22, 10)), fill=(160, 100, 40), width=max(1, int(4 * k)))
        d.polygon(P((14, 6), (26, 2), (30, 10), (20, 14)), fill=(150, 150, 160), outline=(0, 0, 0))
    return im


def hood_art():
    for h in HOODS:
        save('hood_%s.gif' % h['key'].lower(), icon(h['icon'], 32))
        # 468x60 neighborhood banner
        dark, light = hexc(h['color'][0]), hexc(h['color'][1])
        im, d = canvas(468, 60, dark)
        for x in range(468):
            d.line((x, 0, x, 59), fill=mix(dark, mix(dark, light, 0.5), x / 467))
        rr = random.Random(h['key'])
        for _ in range(40):
            x, y = rr.randrange(468), rr.randrange(60)
            d.point((x, y), fill=light)
        big = icon(h['icon'], 48)
        m = Image.new('1', big.size, 0)
        bp, mp = big.load(), m.load()
        for yy in range(48):
            for xx in range(48):
                mp[xx, yy] = 0 if bp[xx, yy] == KEY else 1
        d.ellipse((4, 2, 60, 58), fill=light, outline=(255, 255, 255))
        im.paste(big, (8, 6), m)
        d = ImageDraw.Draw(im)
        d.fontmode = '1'
        f = font('serifbi', 30)
        d.text((74, 4), h['title'], font=f, fill=(0, 0, 0))
        d.text((72, 2), h['title'], font=f, fill=(255, 255, 255))
        d.text((74, 38), h['tagline'], font=font('sansb', 12), fill=light)
        save('banner_%s.gif' % h['key'].lower(), im, transparent=False)


def ad_banners():
    # 1: swat the mosquito
    frames = []
    for i in range(8):
        im, d = canvas(468, 60, (255, 255, 0))
        d.rectangle((0, 0, 467, 59), outline=(0, 0, 0))
        mx = 200 + int(120 * math.sin(i * 0.9))
        my = 22 + int(12 * math.cos(i * 1.7))
        d.ellipse((mx, my, mx + 14, my + 8), fill=(60, 60, 60))
        d.line((mx + 14, my + 4, mx + 22, my + 5), fill=(0, 0, 0))
        wing = (200, 220, 255)
        d.ellipse((mx + 2, my - 6 - (i % 2) * 3, mx + 10, my + 1), fill=wing, outline=(0, 0, 0))
        d.text((8, 6), 'SWAT THE', font=font('sansb', 16), fill=(204, 0, 0))
        d.text((8, 26), 'MOSQUITO!', font=font('sansb', 16), fill=(204, 0, 0))
        d.text((330, 8), 'WIN A FREE', font=font('sansb', 15), fill=(0, 0, 153))
        d.text((330, 28), '56K MODEM!', font=font('sansb', 15), fill=(0, 0, 153))
        if i % 2 == 0:
            d.text((140, 44), 'Click here! You could be a winner!', font=font('sans', 11), fill=(0, 0, 0))
        frames.append(im)
    save('ad_mosquito.gif', frames, 220, transparent=False)

    # 2: lose weight while you surf
    frames = []
    for i, msg in enumerate(['Tired of sitting at the computer?', 'Our Surf-n-Slim chair does the work!',
                             'Lose up to 30 lbs while you SURF!', 'Order now: only 3 easy payments!']):
        im, d = canvas(468, 60, (204, 255, 204))
        d.rectangle((0, 0, 467, 59), outline=(0, 102, 0), width=2)
        d.ellipse((10, 10, 50, 50), fill=(255, 153, 51), outline=(0, 0, 0))
        ctext(d, (10, 10, 50, 50), '$', font('sansb', 28), (255, 255, 255))
        ctext(d, (60, 0, 468, 60), msg, font('sansb', 18), (0, 102, 0))
        frames.append(im)
    save('ad_surfslim.gif', frames, 1200, transparent=False)

    # 3: Y2K kits
    frames = []
    for i in range(6):
        im, d = canvas(468, 60, (0, 0, 0))
        d.rectangle((0, 0, 467, 59), outline=(255, 0, 0), width=2)
        days = 70 - i
        d.text((10, 8), 'Y2K IS COMING', font=font('mono', 20), fill=(255, 0, 0) if i % 2 else (255, 255, 0))
        d.text((10, 34), 'Are YOU ready?', font=font('sansb', 14), fill=(255, 255, 255))
        d.rectangle((240, 8, 456, 52), fill=(40, 0, 0), outline=(255, 0, 0))
        ctext(d, (240, 8, 456, 30), '%02d DAYS LEFT' % days, font('mono', 16), (255, 80, 80))
        ctext(d, (240, 30, 456, 52), 'Millennium Survival Kits', font('sansb', 12), (255, 255, 0))
        frames.append(im)
    save('ad_y2k.gif', frames, 600, transparent=False)

    # 4: Pioneer Navigator
    frames = []
    for i in range(10):
        im, d = canvas(468, 60, (0, 0, 102))
        for s in range(30):
            rr = random.Random(s)
            d.point(((rr.randrange(468) + i * 5 * (s % 3 + 1)) % 468, rr.randrange(60)), fill=(255, 255, 255))
        # ship wheel
        cx, cy = 34, 30
        d.ellipse((cx - 20, cy - 20, cx + 20, cy + 20), outline=(255, 204, 0), width=3)
        for a in range(0, 360, 45):
            aa = math.radians(a + i * 9)
            d.line((cx, cy, cx + 26 * math.cos(aa), cy + 26 * math.sin(aa)), fill=(255, 204, 0), width=2)
        d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(255, 204, 0))
        d.text((70, 6), 'Pioneer Navigator 4.6', font=font('serifbi', 22), fill=(255, 255, 255))
        d.text((72, 36), 'Download it FREE - chart your own course on the Web!', font=font('sans', 12),
               fill=(255, 204, 0))
        frames.append(im)
    save('ad_pioneer.gif', frames, 120, transparent=False)

    # 5: cyberpet
    frames = []
    for i in range(4):
        im, d = canvas(468, 60, (255, 204, 255))
        d.rectangle((0, 0, 467, 59), outline=(153, 0, 153), width=2)
        d.ellipse((14, 8, 58, 54), fill=(240, 240, 240), outline=(0, 0, 0))
        d.rectangle((24, 18, 48, 38), fill=(170, 200, 160), outline=(0, 0, 0))
        d.ellipse((30 + (i % 2) * 4, 22, 40 + (i % 2) * 4, 32), fill=(0, 0, 0))
        d.text((74, 6), 'Your VirtuaPup is HUNGRY!', font=font('sansb', 18), fill=(153, 0, 153))
        d.text((76, 34), ['Feed it now >>', 'Only $14.99 at the CyberMall', 'Feed it now >>',
                          'Collect all 12 colors!'][i], font=font('sansb', 14), fill=(0, 0, 0))
        frames.append(im)
    save('ad_virtuapup.gif', frames, 700, transparent=False)


# ================================================================== clip art
def flames():
    w, h = 480, 28
    frames = []
    for i in range(8):
        im, d = canvas(w, h)
        for x in range(0, w, 3):
            hh = 10 + int(8 * (math.sin(x * 0.13 + i * 1.3) + math.sin(x * 0.31 - i * 0.9)) / 2 + R.randint(0, 6))
            for y in range(hh):
                t = y / max(hh, 1)
                col = mix((255, 255, 120), (255, 120, 0), t) if t < 0.6 else mix((255, 120, 0), (200, 0, 0), (t - .6) / .4)
                d.line((x, h - 1 - y, x + 2, h - 1 - y), fill=col)
        frames.append(im)
    save('flames.gif', frames, 90)

    # HOT! flaming text
    frames = []
    for i in range(6):
        im, d = canvas(80, 40)
        for x in range(0, 80, 2):
            hh = 14 + int(10 * abs(math.sin(x * 0.2 + i)))
            d.line((x, 39, x, 39 - hh), fill=(255, 100 + (x * 7 + i * 30) % 120, 0))
        ctext(d, (0, 4, 80, 40), 'HOT!', font('sansb', 22), (255, 255, 0), outline=(150, 0, 0))
        frames.append(im)
    save('hot.gif', frames, 120)


def skull():
    frames = []
    n = 12
    for i in range(n):
        im, d = canvas(48, 48)
        sx = math.cos(2 * math.pi * i / n)
        w = max(2, int(36 * abs(sx)))
        x0 = 24 - w // 2
        d.ellipse((x0, 4, x0 + w, 34), fill=(235, 235, 220), outline=(0, 0, 0))
        d.rectangle((24 - int(w * .3), 28, 24 + int(w * .3), 42), fill=(235, 235, 220), outline=(0, 0, 0))
        if sx > 0.15:
            ew = max(1, int(8 * sx))
            d.ellipse((24 - int(10 * sx) - ew // 2, 14, 24 - int(10 * sx) + ew // 2, 24), fill=(0, 0, 0))
            d.ellipse((24 + int(10 * sx) - ew // 2, 14, 24 + int(10 * sx) + ew // 2, 24), fill=(0, 0, 0))
            d.polygon([(24, 25), (24 - int(3 * sx), 30), (24 + int(3 * sx), 30)], fill=(0, 0, 0))
            for t in range(-2, 3):
                d.line((24 + int(t * 4 * sx), 36, 24 + int(t * 4 * sx), 42), fill=(0, 0, 0))
        elif sx < -0.15:
            d.line((24, 6, 24, 30), fill=(200, 200, 190))
        frames.append(im)
    save('skull_spin.gif', frames, 80)


def email():
    frames = []
    for i in range(8):
        im, d = canvas(64, 48)
        dx = int(6 * math.sin(i * math.pi / 4))
        dy = int(3 * math.cos(i * math.pi / 4))
        x0, y0 = 10 + dx, 12 + dy
        d.rectangle((x0, y0, x0 + 40, y0 + 26), fill=(255, 255, 255), outline=(0, 0, 0))
        if i % 4 < 2:
            d.line((x0, y0, x0 + 20, y0 + 14, x0 + 40, y0), fill=(0, 0, 0))
        else:
            d.polygon([(x0, y0), (x0 + 20, y0 - 12), (x0 + 40, y0)], fill=(255, 255, 220), outline=(0, 0, 0))
            d.rectangle((x0 + 8, y0 - 6, x0 + 32, y0 + 4), fill=(255, 255, 255), outline=(0, 0, 255))
        d.rectangle((x0 + 31, y0 + 3, x0 + 37, y0 + 10), fill=(255, 0, 0))
        for k in range(3):
            d.line((x0 - 9 + k, y0 + 6 + k * 6, x0 - 3, y0 + 6 + k * 6), fill=(150, 150, 255))
        frames.append(im)
    save('mail_fly.gif', frames, 120)

    frames = []
    for i in range(2):
        im, d = canvas(100, 30, (0, 0, 153) if i == 0 else (255, 255, 0))
        d.rectangle((0, 0, 99, 29), outline=(0, 0, 0))
        d.rectangle((5, 7, 25, 22), fill=(255, 255, 255), outline=(0, 0, 0))
        d.line((5, 7, 15, 15, 25, 7), fill=(0, 0, 0))
        ctext(d, (28, 0, 100, 30), 'E-MAIL ME!', font('sansb', 12), (255, 255, 0) if i == 0 else (0, 0, 153))
        frames.append(im)
    save('mailme.gif', frames, 500, transparent=False)


def construction():
    # worker with shovel + sign
    frames = []
    for i in range(4):
        im, d = canvas(120, 70)
        d.polygon([(4, 66), (40, 66), (30, 52), (14, 52)], fill=(150, 100, 50))
        # sign
        d.polygon([(66, 6), (118, 6), (118, 40), (66, 40)], fill=(255, 220, 0), outline=(0, 0, 0))
        ctext(d, (66, 7, 118, 23), 'UNDER', font('narrow', 10), (0, 0, 0))
        ctext(d, (66, 22, 118, 38), 'CONSTRUCTION', font('narrow', 8), (0, 0, 0))
        d.line((90, 40, 90, 66), fill=(100, 100, 100), width=3)
        # worker
        bx = 46
        d.ellipse((bx, 20, bx + 12, 32), fill=(255, 210, 170), outline=(0, 0, 0))
        d.chord((bx - 1, 17, bx + 13, 29), 180, 360, fill=(255, 204, 0), outline=(0, 0, 0))
        d.rectangle((bx + 1, 32, bx + 11, 48), fill=(255, 120, 0), outline=(0, 0, 0))
        d.line((bx + 3, 48, bx + 1, 64), fill=(0, 0, 150), width=3)
        d.line((bx + 9, 48, bx + 11, 64), fill=(0, 0, 150), width=3)
        ang = [0.3, 0.8, 1.2, 0.6][i]
        sx, sy = bx + 4, 38
        ex, ey = sx - 22 * math.cos(ang), sy + 22 * math.sin(ang)
        d.line((sx + 6, sy - 2, ex, ey), fill=(120, 70, 20), width=2)
        d.polygon([(ex - 4, ey), (ex + 4, ey), (ex + 2, ey + 7), (ex - 6, ey + 6)], fill=(160, 160, 170), outline=(0, 0, 0))
        if i == 2:
            d.point([(ex - 8, ey - 6), (ex - 10, ey - 2), (ex - 5, ey - 9)], fill=(150, 100, 50))
        frames.append(im)
    save('worker.gif', frames, 220)

    # barricade with flashing light
    frames = []
    for i in range(2):
        im, d = canvas(100, 50)
        for k in range(6):
            col = (255, 140, 0) if k % 2 == 0 else (255, 255, 255)
            d.polygon([(8 + k * 14, 16), (20 + k * 14, 16), (14 + k * 14, 30), (2 + k * 14, 30)], fill=col)
        d.rectangle((2, 16, 96, 30), outline=(0, 0, 0))
        d.line((12, 30, 12, 48), fill=(80, 80, 80), width=3)
        d.line((86, 30, 86, 48), fill=(80, 80, 80), width=3)
        for x in (12, 86):
            d.ellipse((x - 6, 2, x + 6, 14), fill=(255, 255, 0) if i == 0 else (120, 90, 0), outline=(0, 0, 0))
        frames.append(im)
    save('barricade.gif', frames, 400)


def baby():
    """an original big-headed diaper dancer, 8 frames"""
    frames = []
    for i in range(8):
        im, d = canvas(56, 72)
        t = i * math.pi / 4
        bob = int(3 * abs(math.sin(t)))
        hx, hy = 28, 16 + bob
        # legs
        for side in (-1, 1):
            kick = math.sin(t + (0 if side < 0 else math.pi))
            d.line((28 + side * 5, 46 + bob, 28 + side * (8 + int(6 * kick)), 66 - int(4 * max(kick, 0))),
                   fill=(255, 200, 170), width=5)
        # body
        d.ellipse((17, 28 + bob, 39, 52 + bob), fill=(255, 205, 175), outline=(120, 70, 50))
        d.chord((17, 36 + bob, 39, 54 + bob), 0, 180, fill=(255, 255, 255), outline=(150, 150, 150))
        # arms waving
        for side in (-1, 1):
            a = math.sin(t * 2 + (side * 1.5))
            d.line((28 + side * 9, 34 + bob, 28 + side * 20, 28 + bob - int(12 * a)), fill=(255, 200, 170), width=4)
        # head
        d.ellipse((hx - 14, hy - 13, hx + 14, hy + 13), fill=(255, 210, 180), outline=(120, 70, 50))
        d.ellipse((hx - 7, hy - 3, hx - 3, hy + 1), fill=(0, 0, 0))
        d.ellipse((hx + 3, hy - 3, hx + 7, hy + 1), fill=(0, 0, 0))
        d.arc((hx - 6, hy, hx + 6, hy + 9), 10, 170, fill=(160, 0, 0), width=2)
        d.arc((hx - 4, hy - 16, hx + 4, hy - 8), 180, 360, fill=(120, 70, 50))
        frames.append(im)
    save('dancing_baby.gif', frames, 110)


def lines():
    W = 480
    # animated rainbow line
    frames = []
    for i in range(10):
        im, d = canvas(W, 8)
        for x in range(W):
            col = hsv(x / 160.0 + i / 10.0, 1, 1)
            d.line((x, 1, x, 6), fill=col)
        frames.append(im)
    save('rainbow_line.gif', frames, 100)
    # hearts line
    im, d = canvas(W, 16)
    for x in range(0, W, 20):
        col = [(255, 0, 102), (255, 102, 204), (204, 0, 204)][(x // 20) % 3]
        d.ellipse((x + 3, 3, x + 10, 10), fill=col)
        d.ellipse((x + 9, 3, x + 16, 10), fill=col)
        d.polygon([(x + 3, 7), (x + 16, 7), (x + 9, 15)], fill=col)
    save('line_hearts.gif', im)
    # stars line (twinkling)
    frames = []
    for i in range(3):
        im, d = canvas(W, 16)
        for x in range(0, W, 16):
            on = (x // 16 + i) % 3 == 0
            col = (255, 255, 0) if on else (200, 200, 255)
            cx = x + 8
            r = 7 if on else 4
            pts = []
            for k in range(10):
                a = math.pi / 2 + k * math.pi / 5
                rr = r if k % 2 == 0 else r * 0.4
                pts.append((cx + rr * math.cos(a), 8 - rr * math.sin(a)))
            d.polygon(pts, fill=col)
        frames.append(im)
    save('line_stars.gif', frames, 250)
    # barbed wire
    im, d = canvas(W, 14)
    d.line((0, 6, W, 6), fill=(110, 110, 110), width=1)
    d.line((0, 8, W, 8), fill=(70, 70, 70), width=1)
    for x in range(0, W, 24):
        d.line((x + 6, 2, x + 14, 12), fill=(90, 90, 90), width=2)
        d.line((x + 6, 12, x + 14, 2), fill=(90, 90, 90), width=2)
    save('line_barbed.gif', im)
    # lightning
    frames = []
    for i in range(3):
        im, d = canvas(W, 16)
        pts = [(0, 8)]
        rr = random.Random(i)
        for x in range(8, W + 8, 8):
            pts.append((x, rr.randint(1, 14)))
        d.line(pts, fill=(255, 255, 255) if i == 1 else (120, 180, 255), width=2)
        frames.append(im)
    save('line_lightning.gif', frames, 120)
    # paw prints
    im, d = canvas(W, 16)
    for x in range(0, W, 24):
        y = 2 if (x // 24) % 2 else 6
        d.ellipse((x + 5, y + 4, x + 12, y + 10), fill=(140, 80, 40))
        for px in (x + 3, x + 7, x + 11, x + 14):
            d.ellipse((px - 1, y, px + 1, y + 3), fill=(140, 80, 40))
    save('line_paws.gif', im)
    # music notes
    im, d = canvas(W, 20)
    d.line((0, 15, W, 15), fill=(0, 0, 0))
    for x in range(10, W, 30):
        y = 8 + (x // 30 % 3) * 2
        d.ellipse((x, y, x + 6, y + 5), fill=(102, 0, 153))
        d.line((x + 6, y + 2, x + 6, y - 7), fill=(102, 0, 153))
    save('line_notes.gif', im)
    # rope / western
    im, d = canvas(W, 10)
    for x in range(0, W, 8):
        d.arc((x, 1, x + 10, 9), 200, 340, fill=(160, 110, 50), width=2)
        d.arc((x - 4, 1, x + 6, 9), 20, 160, fill=(120, 80, 30), width=2)
    save('line_rope.gif', im)
    # laser bar animated
    frames = []
    for i in range(8):
        im, d = canvas(W, 6)
        d.line((0, 3, W, 3), fill=(120, 0, 0))
        x = i * W // 8
        d.line((x, 2, x + 60, 2), fill=(255, 80, 80), width=1)
        d.line((x, 3, x + 60, 3), fill=(255, 255, 255))
        d.line((x, 4, x + 60, 4), fill=(255, 80, 80))
        frames.append(im)
    save('line_laser.gif', frames, 60)
    # slime green
    im, d = canvas(W, 14)
    for x in range(W):
        hh = 4 + int(3 * math.sin(x * 0.2)) + (6 if x % 37 < 3 else 0)
        d.line((x, 0, x, hh), fill=(0, 200 + (x % 3) * 20, 0))
    save('line_slime.gif', im)
    # pastel bow line
    im, d = canvas(W, 12)
    for x in range(W):
        d.point((x, 6), fill=(255, 153, 204))
    for x in range(20, W, 60):
        d.polygon([(x, 6), (x - 10, 1), (x - 10, 11)], fill=(204, 153, 255))
        d.polygon([(x, 6), (x + 10, 1), (x + 10, 11)], fill=(204, 153, 255))
        d.ellipse((x - 2, 4, x + 2, 8), fill=(255, 102, 178))
    save('line_bows.gif', im)
    # copy stock rainbow
    for nm in ('rainbow_hr.gif', 'fire.gif', 'construction.gif', 'new.gif', 'email.gif', 'globe.gif',
               'mailbox.gif', 'bullet_red.gif', 'bullet_blue.gif', 'stars_bg.gif', 'bg_tile.gif', 'powered_by_kf.gif'):
        src = os.path.join(STOCK, nm)
        if os.path.exists(src):
            with open(src, 'rb') as fi, open(os.path.join(OUT, nm), 'wb') as fo:
                fo.write(fi.read())
    for i in range(10):
        src = os.path.join(STOCK, 'digit_%d.gif' % i)
        if os.path.exists(src):
            with open(src, 'rb') as fi, open(os.path.join(OUT, 'digit_%d.gif' % i), 'wb') as fo:
                fo.write(fi.read())


def guestbook_buttons():
    for name, l1, l2, c1, c2 in [('sign_gb.gif', 'SIGN MY', 'GUESTBOOK!', (255, 0, 102), (255, 255, 255)),
                                 ('view_gb.gif', 'VIEW MY', 'GUESTBOOK', (0, 102, 204), (255, 255, 255))]:
        frames = []
        for i in range(6):
            im, d = canvas(120, 44)
            d.rounded_rectangle((0, 0, 119, 43), 8, fill=c1 if i % 3 else mix(c1, (255, 255, 255), .4), outline=(0, 0, 0))
            # book
            d.rectangle((6, 10, 28, 34), fill=(120, 60, 20), outline=(0, 0, 0))
            d.rectangle((9, 12, 26, 32), fill=(255, 255, 230))
            px = 12 + (i % 3) * 4
            d.line((px, 30, px + 10, 14), fill=(0, 0, 0), width=2)
            d.text((34, 5), l1, font=font('sansb', 13), fill=c2)
            d.text((34, 22), l2, font=font('sansb', 13), fill=(255, 255, 0) if i % 2 else c2)
            frames.append(im)
        save(name, frames, 250)


def award(name, title, sub, col, kind='trophy'):
    im, d = canvas(100, 100)
    if kind == 'trophy':
        d.polygon([(30, 14), (70, 14), (64, 46), (36, 46)], fill=(255, 204, 0), outline=(120, 80, 0))
        d.arc((18, 16, 38, 38), 90, 270, fill=(200, 150, 0), width=3)
        d.arc((62, 16, 82, 38), 270, 90, fill=(200, 150, 0), width=3)
        d.rectangle((46, 46, 54, 56), fill=(255, 204, 0))
        d.rectangle((34, 56, 66, 62), fill=(120, 80, 0))
        d.text((44, 22), '#1', font=font('sansb', 12), fill=(120, 80, 0))
    elif kind == 'ribbon':
        d.polygon([(38, 40), (30, 66), (40, 60), (46, 70), (50, 44)], fill=col)
        d.polygon([(62, 40), (70, 66), (60, 60), (54, 70), (50, 44)], fill=col)
        d.ellipse((26, 4, 74, 52), fill=col, outline=(0, 0, 0))
        d.ellipse((32, 10, 68, 46), fill=(255, 255, 255), outline=col)
        ctext(d, (32, 10, 68, 46), '*', font('sansb', 26), col)
    elif kind == 'star':
        pts = []
        for k in range(10):
            a = math.pi / 2 + k * math.pi / 5
            rr = 30 if k % 2 == 0 else 13
            pts.append((50 + rr * math.cos(a), 36 - rr * math.sin(a)))
        d.polygon(pts, fill=(255, 255, 0), outline=(200, 100, 0))
    elif kind == 'paw':
        d.ellipse((30, 6, 70, 62), fill=(255, 204, 230), outline=(204, 0, 102))
        d.ellipse((40, 30, 60, 50), fill=(204, 0, 102))
        for (x, y) in [(37, 22), (45, 15), (55, 15), (63, 22)]:
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(204, 0, 102))
    elif kind == 'shovel':
        d.line((50, 4, 50, 40), fill=(140, 90, 30), width=4)
        d.polygon([(38, 40), (62, 40), (58, 62), (42, 62)], fill=(255, 204, 0), outline=(120, 80, 0))
    elif kind == 'globe':
        d.ellipse((24, 6, 76, 58), fill=(0, 102, 204), outline=(0, 0, 0))
        d.polygon([(34, 18), (48, 14), (52, 28), (40, 36)], fill=(0, 170, 0))
        d.polygon([(56, 34), (68, 30), (66, 48), (56, 50)], fill=(0, 170, 0))
    d.rectangle((2, 68, 97, 97), fill=col, outline=(0, 0, 0))
    ctext(d, (2, 68, 98, 84), title, font('narrow', 12), (255, 255, 255), shadow=(0, 0, 0))
    ctext(d, (2, 82, 98, 97), sub, font('narrow', 11), (255, 255, 0))
    save(name, im)


def awards():
    award('award_coolweek.gif', 'Cool Site', 'of the Week!', (204, 0, 0), 'trophy')
    award('award_hammer.gif', 'Golden Shovel', 'Homestead Award', (153, 102, 0), 'shovel')
    award('award_galactic.gif', 'Galactic Site', 'Award 1999', (0, 0, 102), 'star')
    award('award_purrfect.gif', 'Purrfect Page', 'Award', (204, 0, 102), 'paw')
    award('award_top4.gif', 'Top 4% of', 'the Whole Net', (0, 102, 0), 'globe')
    award('award_blue.gif', 'Blue Ribbon', 'Family Site', (0, 51, 204), 'ribbon')
    award('award_spooky.gif', 'Spooky Site', 'of the Month', (80, 0, 80), 'star')
    award('award_gold.gif', 'Gold Star', 'Webmaster', (204, 120, 0), 'star')


def creatures():
    # UFO hovering with beam
    frames = []
    for i in range(6):
        im, d = canvas(80, 64)
        y = 6 + int(3 * math.sin(i * math.pi / 3))
        if i % 2 == 0:
            d.polygon([(30, y + 20), (50, y + 20), (64, 63), (16, 63)], fill=(200, 255, 170))
        d.ellipse((28, y, 52, y + 18), fill=(150, 230, 255), outline=(0, 0, 0))
        d.ellipse((6, y + 10, 74, y + 26), fill=(170, 170, 190), outline=(0, 0, 0))
        for k, x in enumerate((16, 28, 40, 52, 64)):
            on = (k + i) % 3 == 0
            d.ellipse((x - 2, y + 16, x + 2, y + 20), fill=(255, 255, 0) if on else (255, 80, 0))
        frames.append(im)
    save('ufo.gif', frames, 160)

    # alien head blinking
    frames = []
    for i in range(4):
        im, d = canvas(48, 56)
        d.ellipse((6, 2, 42, 40), fill=(140, 220, 120), outline=(0, 60, 0))
        d.polygon([(12, 30), (36, 30), (24, 54)], fill=(140, 220, 120), outline=(0, 60, 0))
        d.ellipse((8, 2, 40, 38), fill=(140, 220, 120))
        if i != 2:
            d.polygon([(10, 22), (20, 20), (22, 30), (14, 30)], fill=(0, 0, 0))
            d.polygon([(38, 22), (28, 20), (26, 30), (34, 30)], fill=(0, 0, 0))
            d.point([(13, 23), (35, 23)], fill=(255, 255, 255))
        else:
            d.line((11, 26, 21, 26), fill=(0, 0, 0), width=2)
            d.line((27, 26, 37, 26), fill=(0, 0, 0), width=2)
        d.line((22, 42, 26, 42), fill=(0, 60, 0))
        frames.append(im)
    save('alien.gif', frames, [900, 900, 150, 900])

    # pastel kitten with swishing tail
    frames = []
    for i in range(4):
        im, d = canvas(64, 56)
        tail = [(-0.6), (-0.2), (0.2), (-0.2)][i]
        d.line((44, 40, 44 + int(14 * math.cos(tail)), 40 - int(16 * math.sin(tail + 1.2))), fill=(255, 180, 210), width=5)
        d.ellipse((16, 26, 50, 52), fill=(255, 200, 225), outline=(150, 80, 110))
        d.ellipse((8, 6, 40, 34), fill=(255, 200, 225), outline=(150, 80, 110))
        d.polygon([(10, 14), (12, 0), (22, 8)], fill=(255, 200, 225), outline=(150, 80, 110))
        d.polygon([(26, 8), (36, 0), (38, 14)], fill=(255, 200, 225), outline=(150, 80, 110))
        d.ellipse((15, 15, 20, 21), fill=(60, 120, 200))
        d.ellipse((28, 15, 33, 21), fill=(60, 120, 200))
        d.polygon([(22, 23), (26, 23), (24, 26)], fill=(255, 100, 150))
        for s in (-1, 1):
            d.line((24 + s * 4, 25, 24 + s * 16, 23), fill=(150, 80, 110))
            d.line((24 + s * 4, 26, 24 + s * 16, 28), fill=(150, 80, 110))
        d.polygon([(32, 4), (36, 1), (36, 7)], fill=(204, 102, 255))
        frames.append(im)
    save('kitten.gif', frames, 250)

    # puppy wagging
    frames = []
    for i in range(2):
        im, d = canvas(64, 52)
        d.line((48, 30, 60, 18 + i * 10), fill=(180, 120, 60), width=4)
        d.ellipse((20, 24, 52, 46), fill=(200, 140, 70), outline=(90, 50, 20))
        for x in (24, 32, 42, 48):
            d.rectangle((x - 2, 42, x + 2, 50), fill=(200, 140, 70))
        d.ellipse((4, 6, 30, 32), fill=(210, 150, 80), outline=(90, 50, 20))
        d.ellipse((0, 8, 10, 26), fill=(120, 70, 30))
        d.ellipse((24, 8, 34, 26), fill=(120, 70, 30))
        d.ellipse((11, 14, 15, 18), fill=(0, 0, 0))
        d.ellipse((19, 14, 23, 18), fill=(0, 0, 0))
        d.ellipse((14, 22, 20, 26), fill=(0, 0, 0))
        d.ellipse((15, 27, 19, 33), fill=(255, 100, 120))
        frames.append(im)
    save('puppy.gif', frames, 200)

    # pulsing heart
    frames = []
    for i, s in enumerate([1.0, 0.85, 0.7, 0.85]):
        im, d = canvas(32, 32)
        r = 7 * s
        cx, cy = 16, 14
        d.ellipse((cx - 2 * r, cy - r, cx, cy + r), fill=(255, 0, 80))
        d.ellipse((cx, cy - r, cx + 2 * r, cy + r), fill=(255, 0, 80))
        d.polygon([(cx - 2 * r + 1, cy + 2), (cx + 2 * r - 1, cy + 2), (cx, cy + 2.4 * r)], fill=(255, 0, 80))
        d.ellipse((cx - r - 2, cy - r / 2, cx - r + 2, cy - r / 2 + 3), fill=(255, 200, 220))
        frames.append(im)
    save('heart.gif', frames, 150)

    # twinkle star
    frames = []
    for i in range(4):
        im, d = canvas(24, 24)
        s = [11, 7, 3, 7][i]
        d.polygon([(12, 12 - s), (13, 11), (12 + s, 12), (13, 13), (12, 12 + s), (11, 13), (12 - s, 12), (11, 11)],
                  fill=(255, 255, 200))
        d.point((12, 12), fill=(255, 255, 255))
        frames.append(im)
    save('twinkle.gif', frames, 120)

    # spinning cd
    frames = []
    for i in range(8):
        im, d = canvas(40, 40)
        d.ellipse((2, 2, 38, 38), fill=(200, 200, 215), outline=(90, 90, 100))
        for k in range(3):
            a = i * 45 + k * 120
            d.pieslice((3, 3, 37, 37), a, a + 30, fill=hsv((a % 360) / 360.0, .5, 1))
        d.ellipse((14, 14, 26, 26), fill=(240, 240, 255), outline=(90, 90, 100))
        d.ellipse((18, 18, 22, 22), fill=KEY)
        frames.append(im)
    save('cd_spin.gif', frames, 80)

    # bouncing music notes
    frames = []
    for i in range(4):
        im, d = canvas(48, 40)
        for k, x in enumerate((6, 26)):
            y = 18 + int(6 * math.sin((i + k * 2) * math.pi / 2))
            col = [(255, 0, 153), (0, 102, 255)][k]
            d.ellipse((x, y, x + 9, y + 7), fill=col)
            d.line((x + 9, y + 3, x + 9, y - 14), fill=col, width=2)
            d.line((x + 9, y - 14, x + 15, y - 9), fill=col, width=2)
        frames.append(im)
    save('notes.gif', frames, 180)

    # spinning football
    frames = []
    for i in range(8):
        im, d = canvas(48, 40)
        a = i * math.pi / 4
        w = 20
        h = 10 + int(4 * abs(math.sin(a)))
        d.ellipse((24 - w, 20 - h, 24 + w, 20 + h), fill=(140, 70, 20), outline=(60, 30, 0))
        if math.cos(a) > 0:
            d.line((16, 20, 32, 20), fill=(255, 255, 255))
            for x in range(18, 32, 4):
                d.line((x, 18, x, 22), fill=(255, 255, 255))
        frames.append(im)
    save('football.gif', frames, 90)

    # candle for memorials
    frames = []
    for i in range(4):
        im, d = canvas(32, 64)
        d.rectangle((10, 28, 22, 62), fill=(255, 250, 230), outline=(180, 170, 150))
        d.line((16, 28, 16, 24), fill=(0, 0, 0))
        fx = [0, 1, 0, -1][i]
        d.ellipse((12 + fx, 8 + (i % 2), 20 + fx, 25), fill=(255, 160, 0))
        d.ellipse((14 + fx, 13, 18 + fx, 24), fill=(255, 255, 160))
        frames.append(im)
    save('candle.gif', frames, 150)

    # y2k bomb with fuse
    frames = []
    for i in range(4):
        im, d = canvas(64, 64)
        d.ellipse((6, 16, 50, 60), fill=(30, 30, 30), outline=(0, 0, 0))
        d.rectangle((22, 10, 34, 18), fill=(80, 80, 80))
        d.line((28, 10, 36, 4, 44, 6), fill=(160, 120, 60), width=2)
        sx = [44, 42, 40, 38][i]
        for k in range(5):
            a = k * 72 + i * 20
            d.line((sx, 5, sx + 6 * math.cos(math.radians(a)), 5 + 6 * math.sin(math.radians(a))),
                   fill=(255, 220, 0) if k % 2 else (255, 80, 0))
        ctext(d, (6, 22, 50, 56), 'Y2K', font('sansb', 14), (255, 0, 0))
        frames.append(im)
    save('y2k_bomb.gif', frames, 120)

    # welcome banner color cycling
    frames = []
    txt = 'WELCOME TO MY HOMEPAGE!'
    f = font('sansbi', 22)
    for i in range(6):
        im, d = canvas(400, 40)
        x = 6
        for j, ch in enumerate(txt):
            col = hsv((j * 0.06 + i / 6.0), 1, 1)
            d.text((x + 2, 8), ch, font=f, fill=(0, 0, 0))
            d.text((x, 6), ch, font=f, fill=col)
            x += tsize(d, ch, f)[0] + (6 if ch == ' ' else 1)
        frames.append(im)
    save('welcome.gif', frames, 150)

    # dancing hamster (a cameo; the real ones live at hamstershuffle)
    frames = []
    for i in range(2):
        im, d = canvas(40, 40)
        lean = -3 if i else 3
        d.ellipse((10 + lean, 12, 30 + lean, 36), fill=(220, 160, 90), outline=(90, 50, 20))
        d.ellipse((14 + lean, 20, 26 + lean, 34), fill=(255, 235, 200))
        d.ellipse((11 + lean, 2, 29 + lean, 18), fill=(220, 160, 90), outline=(90, 50, 20))
        d.ellipse((15 + lean, 7, 18 + lean, 10), fill=(0, 0, 0))
        d.ellipse((22 + lean, 7, 25 + lean, 10), fill=(0, 0, 0))
        d.line((6, 16 if i else 26, 12 + lean, 22), fill=(220, 160, 90), width=3)
        d.line((34, 26 if i else 16, 28 + lean, 22), fill=(220, 160, 90), width=3)
        frames.append(im)
    save('hamster.gif', frames, 220)

    # Monstropals - six invented pocket critters
    critters = [
        ('flintfox', (255, 120, 40), 'fox'), ('puddlepup', (80, 160, 255), 'pup'),
        ('sproutle', (100, 200, 80), 'bulb'), ('voltwhisker', (255, 230, 0), 'mouse'),
        ('gloomoth', (150, 90, 200), 'moth'), ('pebblin', (160, 150, 140), 'rock')]
    for name, col, kind in critters:
        frames = []
        for i in range(2):
            im, d = canvas(64, 64)
            b = i * 2
            dark = mix(col, (0, 0, 0), .45)
            if kind == 'fox':
                d.polygon([(46, 44), (62, 30 - b), (56, 50)], fill=(255, 80, 0))
                d.ellipse((16, 26 + b, 48, 58), fill=col, outline=dark)
                d.ellipse((14, 8 + b, 46, 38 + b), fill=col, outline=dark)
                d.polygon([(16, 16 + b), (14, 0 + b), (28, 10 + b)], fill=col, outline=dark)
                d.polygon([(32, 10 + b), (46, 0 + b), (44, 16 + b)], fill=col, outline=dark)
            elif kind == 'pup':
                d.ellipse((12, 24 + b, 52, 58), fill=col, outline=dark)
                d.ellipse((14, 6 + b, 50, 38 + b), fill=col, outline=dark)
                d.ellipse((6, 10 + b, 18, 32 + b), fill=dark)
                d.ellipse((46, 10 + b, 58, 32 + b), fill=dark)
                d.ellipse((24, 0 + b, 32, 8 + b), fill=(200, 230, 255))
            elif kind == 'bulb':
                d.ellipse((12, 28, 52, 60), fill=col, outline=dark)
                d.ellipse((16, 10 + b, 48, 40 + b), fill=mix(col, (255, 255, 255), .3), outline=dark)
                d.polygon([(32, 12 + b), (22, -2 + b + 4), (32, 4 + b)], fill=(0, 150, 0))
                d.polygon([(32, 12 + b), (42, 0 + b + 4), (32, 4 + b)], fill=(0, 120, 0))
            elif kind == 'mouse':
                d.line((46, 46, 60, 34 - b, 54, 26), fill=(200, 160, 0), width=3)
                d.ellipse((14, 26 + b, 50, 58), fill=col, outline=dark)
                d.ellipse((14, 8 + b, 48, 38 + b), fill=col, outline=dark)
                d.ellipse((8, 0 + b, 24, 18 + b), fill=col, outline=dark)
                d.ellipse((40, 0 + b, 56, 18 + b), fill=col, outline=dark)
                d.ellipse((16, 24 + b, 22, 30 + b), fill=(255, 80, 80))
                d.ellipse((40, 24 + b, 46, 30 + b), fill=(255, 80, 80))
            elif kind == 'moth':
                wing = 18 if i else 24
                d.ellipse((32 - wing - 8, 14, 30, 46), fill=mix(col, (255, 255, 255), .3), outline=dark)
                d.ellipse((34, 14, 32 + wing + 8, 46), fill=mix(col, (255, 255, 255), .3), outline=dark)
                d.ellipse((24, 12, 40, 56), fill=col, outline=dark)
                d.ellipse((22, 6, 42, 26), fill=col, outline=dark)
            else:
                d.polygon([(10, 58), (8, 34 + b), (22, 14 + b), (44, 12 + b), (56, 32 + b), (54, 58)], fill=col, outline=dark)
                d.line((20, 40, 30, 44), fill=dark)
            ey = 18 + b if kind not in ('moth',) else 13
            d.ellipse((22, ey, 28, ey + 7), fill=(0, 0, 0))
            d.ellipse((36, ey, 42, ey + 7), fill=(0, 0, 0))
            d.point([(24, ey + 1), (38, ey + 1)], fill=(255, 255, 255))
            d.arc((26, ey + 6, 38, ey + 14), 20, 160, fill=(0, 0, 0))
            frames.append(im)
        save('mp_%s.gif' % name, frames, 400)


def badges():
    def btn(name, bg, lines_, fg=(255, 255, 255), icon_fn=None, border=(0, 0, 0)):
        im, d = canvas(88, 31, bg)
        d.rectangle((0, 0, 87, 30), outline=border)
        x0 = 2
        if icon_fn:
            icon_fn(d)
            x0 = 28
        n = len(lines_)
        for i, (t, f, c) in enumerate(lines_):
            ctext(d, (x0, 2 + i * (27 // n), 86, 2 + (i + 1) * (27 // n)), t, f, c or fg)
        save(name, im, transparent=False)

    def monitor(d):
        d.rectangle((4, 5, 24, 21), fill=(200, 200, 200), outline=(0, 0, 0))
        d.rectangle((7, 8, 21, 18), fill=(0, 0, 150))
        d.rectangle((10, 22, 18, 25), fill=(160, 160, 160))
    btn('best_800.gif', (0, 0, 0), [('Best viewed at', font('narrow', 9), (200, 200, 200)),
                                    ('800 x 600', font('sansb', 13), (0, 255, 0))], icon_fn=monitor)

    def pad(d):
        d.rectangle((6, 4, 22, 26), fill=(255, 255, 200), outline=(0, 0, 0))
        for y in range(8, 24, 3):
            d.line((8, y, 20, y), fill=(120, 120, 255))
    btn('notepad.gif', (255, 255, 255), [('Made with', font('sans', 10), (0, 0, 0)),
                                         ('NOTEPAD', font('sansb', 12), (0, 0, 153))], icon_fn=pad)
    btn('y2k_ok.gif', (0, 102, 0), [('Y2K', font('sansb', 13), (255, 255, 0)),
                                    ('COMPLIANT', font('sansb', 10), None)])
    btn('y2k_not.gif', (153, 0, 0), [('NOT Y2K', font('sansb', 12), (255, 255, 0)),
                                     ('compliant :-(', font('sans', 10), None)])

    def wheel(d):
        d.ellipse((4, 4, 24, 24), outline=(255, 204, 0), width=2)
        for a in range(0, 360, 60):
            d.line((14, 14, 14 + 11 * math.cos(math.radians(a)), 14 + 11 * math.sin(math.radians(a))), fill=(255, 204, 0))
    btn('pioneer_now.gif', (0, 0, 102), [('Pioneer', font('serifbi', 12), (255, 255, 255)),
                                         ('Navigator NOW!', font('narrow', 9), (255, 204, 0))], icon_fn=wheel)

    def e_icon(d):
        d.ellipse((4, 4, 24, 26), fill=(0, 120, 220))
        ctext(d, (4, 4, 24, 26), 'x', font('serifbi', 18), (255, 255, 0))
    btn('explorer.gif', (255, 255, 255), [('Internet', font('sans', 10), (0, 0, 0)),
                                          ('Explor-o-Matic', font('narrow', 9), (0, 80, 180))], icon_fn=e_icon)
    btn('handcoded.gif', (102, 51, 0), [('100% HAND', font('sansb', 11), (255, 220, 150)),
                                        ('CODED HTML', font('sansb', 11), None)])
    btn('noframes.gif', (204, 204, 204), [('FRAMES', font('sansb', 11), (0, 0, 0)),
                                          ('FREE ZONE', font('sansb', 11), (204, 0, 0))])
    btn('webring_88.gif', (51, 0, 102), [('Proud member', font('sans', 9), (255, 255, 255)),
                                         ('of a WEBRING', font('sansb', 11), (255, 204, 0))])
    btn('html32.gif', (255, 255, 204), [('HTML 3.2', font('sansb', 12), (204, 0, 0)),
                                        ('checked-ish', font('sans', 10), (0, 0, 0))])
    btn('mp_trainer.gif', (255, 0, 0), [('MONSTROPALS', font('narrow', 11), (255, 255, 255)),
                                        ('Trainer Site', font('sansb', 10), (255, 255, 0))])
    btn('kava_powered.gif', (153, 102, 51), [('KAVA', font('sansb', 13), (255, 255, 255)),
                                             ('applet inside', font('sans', 9), (255, 230, 180))])
    btn('anti_spam.gif', (0, 0, 0), [('NO SPAM!', font('sansb', 13), (255, 0, 0)),
                                     ('spammers stink', font('sans', 9), (255, 255, 255))])
    btn('stop_ie.gif', (255, 255, 255), [('Browser Wars:', font('sans', 9), (0, 0, 0)),
                                         ('I PICK SIDES', font('sansb', 10), (204, 0, 0))])
    btn('tinfoil.gif', (160, 160, 170), [('TINFOIL HAT', font('sansb', 10), (0, 0, 0)),
                                         ('certified', font('sans', 10), (0, 0, 102))])
    btn('gnulix.gif', (0, 0, 0), [('Powered by', font('sans', 9), (200, 200, 200)),
                                  ('GNULIX', font('mono', 13), (0, 255, 0))])
    btn('plushie.gif', (255, 153, 204), [('Plushie Pals', font('sansb', 11), (153, 0, 102)),
                                         ('COLLECTOR', font('sansb', 10), (255, 255, 255))])
    btn('webcam_88.gif', (0, 0, 0), [('LIVE', font('sansb', 13), (255, 0, 0)),
                                     ('WEBCAM', font('sansb', 11), (255, 255, 255))])
    btn('geohoods_88.gif', (255, 255, 204), [('Free Pages @', font('sans', 9), (0, 0, 0)),
                                             ('GeoHoods', font('serifbi', 13), (0, 51, 153))])


def counters():
    for style, bg, fg in [('led', (0, 0, 0), (0, 255, 0)), ('odo', (40, 40, 40), (255, 255, 255))]:
        for n in range(10):
            im, d = canvas(14, 20, bg)
            if style == 'odo':
                d.rectangle((0, 0, 13, 19), outline=(120, 120, 120))
                d.line((1, 1, 12, 1), fill=(90, 90, 90))
            ctext(d, (0, 0, 14, 20), str(n), font('mono', 15), fg)
            save('%s_%d.gif' % (style, n), im, transparent=False)


def bullets():
    for name, col in [('ball_red', (220, 0, 0)), ('ball_green', (0, 180, 0)), ('ball_blue', (0, 80, 255)),
                      ('ball_yellow', (255, 200, 0)), ('ball_purple', (150, 0, 200)), ('ball_pink', (255, 80, 180))]:
        im, d = canvas(14, 14)
        for r in range(6, 0, -1):
            t = 1 - r / 6
            d.ellipse((7 - r - (1 - t) * 0, 7 - r, 7 + r, 7 + r), fill=mix(mix(col, (0, 0, 0), .4), (255, 255, 255), t * .8))
        d.ellipse((1, 1, 13, 13), outline=mix(col, (0, 0, 0), .5))
        d.point((5, 4), fill=(255, 255, 255))
        save(name + '.gif', im)
    # star / skull / paw / alien bullets
    im, d = canvas(14, 14)
    pts = [(7 + 6 * math.cos(math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else .45),
            7 - 6 * math.sin(math.pi / 2 + k * math.pi / 5) * (1 if k % 2 == 0 else .45)) for k in range(10)]
    d.polygon(pts, fill=(255, 220, 0), outline=(150, 100, 0))
    save('bullet_star.gif', im)
    im, d = canvas(14, 14)
    d.ellipse((2, 1, 12, 10), fill=(240, 240, 230))
    d.rectangle((4, 8, 10, 12), fill=(240, 240, 230))
    d.point([(5, 5), (9, 5), (5, 4), (9, 4)], fill=(0, 0, 0))
    save('bullet_skull.gif', im)
    im, d = canvas(14, 14)
    d.ellipse((4, 6, 10, 12), fill=(160, 90, 40))
    for x in (3, 6, 8, 11):
        d.ellipse((x - 1, 2 + (1 if x in (3, 11) else 0), x + 1, 5 + (1 if x in (3, 11) else 0)), fill=(160, 90, 40))
    save('bullet_paw.gif', im)
    im, d = canvas(14, 14)
    d.ellipse((2, 1, 12, 11), fill=(120, 220, 100))
    d.polygon([(4, 9), (10, 9), (7, 13)], fill=(120, 220, 100))
    d.ellipse((3, 5, 6, 8), fill=(0, 0, 0))
    d.ellipse((8, 5, 11, 8), fill=(0, 0, 0))
    save('bullet_alien.gif', im)
    im, d = canvas(14, 14)
    d.ellipse((1, 3, 7, 9), fill=(255, 0, 100))
    d.ellipse((6, 3, 12, 9), fill=(255, 0, 100))
    d.polygon([(1, 7), (12, 7), (7, 13)], fill=(255, 0, 100))
    save('bullet_heart.gif', im)


def tile(name, w, h, fn, seed=0):
    im, d = canvas(w, h, (0, 0, 0))
    rr = random.Random(seed or name)
    fn(im, d, rr)
    save(name, im, transparent=False)


def backgrounds():
    def stars2(im, d, rr):
        d.rectangle((0, 0, 128, 128), fill=(0, 0, 16))
        for _ in range(70):
            c = rr.choice([(255, 255, 255), (180, 180, 255), (255, 255, 180), (120, 120, 160)])
            d.point((rr.randrange(128), rr.randrange(128)), fill=c)
        for _ in range(4):
            x, y = rr.randrange(4, 124), rr.randrange(4, 124)
            d.line((x - 2, y, x + 2, y), fill=(255, 255, 255))
            d.line((x, y - 2, x, y + 2), fill=(255, 255, 255))
    tile('bg_space.gif', 128, 128, stars2)

    def nebula(im, d, rr):
        px = im.load()
        for y in range(128):
            for x in range(128):
                v = (math.sin(x * 2 * math.pi / 128 * 2) + math.cos(y * 2 * math.pi / 128 * 3) +
                     math.sin((x + y) * 2 * math.pi / 128)) / 3
                v = max(0, v)
                px[x, y] = (int(60 * v + 5), int(10 * v), int(90 * v + 20))
        for _ in range(50):
            d.point((rr.randrange(128), rr.randrange(128)), fill=(255, 255, 255))
    tile('bg_nebula.gif', 128, 128, nebula)

    def hearts(im, d, rr):
        d.rectangle((0, 0, 80, 80), fill=(255, 220, 240))
        for (x, y, c) in [(10, 10, (255, 153, 204)), (50, 45, (204, 153, 255)), (52, 8, (255, 204, 230)),
                          (12, 52, (255, 204, 230))]:
            d.ellipse((x, y, x + 8, y + 8), fill=c)
            d.ellipse((x + 7, y, x + 15, y + 8), fill=c)
            d.polygon([(x, y + 5), (x + 15, y + 5), (x + 7, y + 14)], fill=c)
    tile('bg_hearts.gif', 80, 80, hearts)

    def clouds(im, d, rr):
        d.rectangle((0, 0, 160, 120), fill=(120, 180, 255))
        for (x, y) in [(10, 20), (90, 70), (100, 10), (20, 85)]:
            for k in range(5):
                d.ellipse((x + k * 9, y + (k % 2) * 4, x + k * 9 + 22, y + 16 + (k % 2) * 4), fill=(250, 250, 255))
    tile('bg_clouds.gif', 160, 120, clouds)

    def paper(im, d, rr):
        px = im.load()
        for y in range(96):
            for x in range(96):
                n = rr.randint(-10, 10)
                px[x, y] = (238 + n // 2, 225 + n, 190 + n)
        for _ in range(12):
            x, y = rr.randrange(96), rr.randrange(96)
            d.point((x, y), fill=(200, 180, 140))
    tile('bg_parchment.gif', 96, 96, paper)

    def marble(im, d, rr):
        px = im.load()
        for y in range(128):
            for x in range(128):
                v = math.sin((x + 30 * math.sin(y * 2 * math.pi / 128) + 8 * math.sin(x * 6 * math.pi / 128)) * 2 * math.pi / 64)
                c = int(200 + 40 * v)
                px[x, y] = (c, c - 8, c + 4 if c + 4 < 256 else 255)
    tile('bg_marble.gif', 128, 128, marble)

    def brick(im, d, rr):
        d.rectangle((0, 0, 64, 32), fill=(190, 190, 180))
        for row in range(4):
            off = 0 if row % 2 == 0 else 16
            for k in range(-1, 3):
                x = off + k * 32
                c = (150 + rr.randint(-15, 15), 40 + rr.randint(-10, 10), 30)
                d.rectangle((x + 1, row * 8 + 1, x + 30, row * 8 + 7), fill=c)
    tile('bg_brick.gif', 64, 32, brick)

    def camo(im, d, rr):
        d.rectangle((0, 0, 96, 96), fill=(110, 120, 70))
        for c in [(70, 80, 40), (140, 120, 80), (40, 40, 25)]:
            for _ in range(7):
                x, y, r = rr.randrange(96), rr.randrange(96), rr.randrange(6, 16)
                for dx in (-96, 0, 96):
                    for dy in (-96, 0, 96):
                        d.ellipse((x + dx - r, y + dy - r // 2, x + dx + r, y + dy + r // 2), fill=c)
    tile('bg_camo.gif', 96, 96, camo)

    def wood(im, d, rr):
        for x in range(128):
            for y in range(64):
                v = math.sin((y + 4 * math.sin(x * 2 * math.pi / 128 * 3)) * 0.7)
                im.putpixel((x, y), (150 + int(20 * v), 95 + int(15 * v), 50 + int(8 * v)))
        for y in (15, 31, 47, 63):
            d.line((0, y, 128, y), fill=(90, 55, 25))
    tile('bg_wood.gif', 128, 64, wood)

    def grass(im, d, rr):
        d.rectangle((0, 0, 64, 64), fill=(40, 130, 40))
        for _ in range(140):
            x, y = rr.randrange(64), rr.randrange(64)
            d.line((x, y, x + rr.randint(-1, 1), y - 3), fill=rr.choice([(60, 160, 50), (30, 110, 30), (80, 180, 60)]))
    tile('bg_grass.gif', 64, 64, grass)

    def water(im, d, rr):
        for y in range(64):
            for x in range(64):
                v = math.sin(x * 2 * math.pi / 32 + math.sin(y * 2 * math.pi / 64) * 2)
                im.putpixel((x, y), (0, 90 + int(30 * v), 170 + int(30 * v)))
    tile('bg_water.gif', 64, 64, water)

    def matrix(im, d, rr):
        d.rectangle((0, 0, 96, 96), fill=(0, 0, 0))
        f = font('mono', 9)
        for x in range(0, 96, 8):
            for y in range(0, 96, 11):
                if rr.random() < 0.6:
                    d.text((x, y), rr.choice('01'), font=f, fill=(0, rr.randint(70, 200), 0))
    tile('bg_binary.gif', 96, 96, matrix)

    def flowers(im, d, rr):
        d.rectangle((0, 0, 72, 72), fill=(235, 225, 255))
        for (x, y) in [(14, 14), (50, 46), (52, 12), (16, 54)]:
            for a in range(0, 360, 72):
                d.ellipse((x + 5 * math.cos(math.radians(a)) - 4, y + 5 * math.sin(math.radians(a)) - 4,
                           x + 5 * math.cos(math.radians(a)) + 4, y + 5 * math.sin(math.radians(a)) + 4),
                          fill=(204, 153, 255))
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 230, 100))
    tile('bg_flowers.gif', 72, 72, flowers)

    def paws(im, d, rr):
        d.rectangle((0, 0, 80, 80), fill=(255, 245, 225))
        for (x, y) in [(14, 16), (54, 52)]:
            d.ellipse((x, y + 6, x + 12, y + 16), fill=(230, 200, 160))
            for k, (px_, py) in enumerate([(-2, 2), (3, -2), (9, -2), (14, 2)]):
                d.ellipse((x + px_, y + py, x + px_ + 4, y + py + 5), fill=(230, 200, 160))
    tile('bg_paws.gif', 80, 80, paws)

    def notebook(im, d, rr):
        # classic left-border-strip background: 1200 wide so it doesn't repeat sideways
        d.rectangle((0, 0, 1200, 24), fill=(255, 255, 255))
        d.line((0, 23, 1200, 23), fill=(170, 200, 255))
        d.line((70, 0, 70, 24), fill=(255, 120, 120))
        d.ellipse((24, 6, 36, 18), fill=(220, 220, 220))
    tile('bg_notebook.gif', 1200, 24, notebook)

    for name, c1, c2, pattern in [('bg_border_blue.gif', (0, 0, 128), (200, 220, 255), 'stars'),
                                  ('bg_border_purple.gif', (80, 0, 120), (240, 225, 255), 'dots'),
                                  ('bg_border_flames.gif', (0, 0, 0), (20, 0, 0), 'flame'),
                                  ('bg_border_green.gif', (0, 90, 0), (235, 255, 225), 'stripes'),
                                  ('bg_border_pink.gif', (255, 102, 178), (255, 240, 248), 'hearts')]:
        def border(im, d, rr, c1=c1, c2=c2, pattern=pattern):
            d.rectangle((0, 0, 1200, 40), fill=c2)
            d.rectangle((0, 0, 110, 40), fill=c1)
            d.line((111, 0, 111, 40), fill=(0, 0, 0))
            d.line((113, 0, 113, 40), fill=mix(c1, c2, .5))
            if pattern == 'stars':
                for (x, y) in [(20, 10), (70, 30), (45, 22), (90, 5)]:
                    d.point([(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], fill=(255, 255, 200))
            elif pattern == 'dots':
                for x in range(10, 110, 20):
                    d.ellipse((x, 15, x + 8, 23), fill=(200, 150, 255))
            elif pattern == 'flame':
                for x in range(0, 110, 2):
                    hh = 10 + int(8 * math.sin(x * 0.3))
                    d.line((x, 40, x, 40 - hh), fill=(200, 60 + x, 0))
                    d.line((x, 0, x, hh // 2), fill=(150, 30, 0))
            elif pattern == 'stripes':
                for x in range(0, 110, 14):
                    d.rectangle((x, 0, x + 6, 40), fill=(0, 130, 0))
            else:
                for (x, y) in [(20, 8), (70, 26)]:
                    d.ellipse((x, y, x + 8, y + 8), fill=(255, 220, 240))
                    d.ellipse((x + 7, y, x + 15, y + 8), fill=(255, 220, 240))
                    d.polygon([(x, y + 5), (x + 15, y + 5), (x + 7, y + 14)], fill=(255, 220, 240))
        tile(name, 1200, 40, border)

    def checker(im, d, rr):
        for y in range(0, 32, 16):
            for x in range(0, 32, 16):
                d.rectangle((x, y, x + 15, y + 15), fill=(0, 0, 0) if (x + y) % 32 == 0 else (255, 255, 255))
    tile('bg_checker.gif', 32, 32, checker)

    def gingham(im, d, rr):
        for y in range(32):
            for x in range(32):
                a, b = (x // 8) % 2, (y // 8) % 2
                im.putpixel((x, y), [(255, 255, 255), (255, 170, 170), (255, 170, 170), (220, 40, 40)][a + 2 * b] if True else 0)
    tile('bg_gingham.gif', 32, 32, gingham)

    def bubbles(im, d, rr):
        d.rectangle((0, 0, 96, 96), fill=(0, 60, 120))
        for _ in range(9):
            x, y, r = rr.randrange(96), rr.randrange(96), rr.randrange(3, 9)
            d.ellipse((x - r, y - r, x + r, y + r), outline=(150, 220, 255))
            d.point((x - r // 2, y - r // 2), fill=(255, 255, 255))
    tile('bg_bubbles.gif', 96, 96, bubbles)

    def snow(im, d, rr):
        d.rectangle((0, 0, 96, 96), fill=(10, 20, 70))
        for _ in range(30):
            x, y = rr.randrange(96), rr.randrange(96)
            d.point([(x, y), (x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)], fill=(255, 255, 255))
    tile('bg_snow.gif', 96, 96, snow)

    def leopard(im, d, rr):
        d.rectangle((0, 0, 80, 80), fill=(230, 180, 90))
        for _ in range(14):
            x, y = rr.randrange(80), rr.randrange(80)
            d.arc((x - 6, y - 5, x + 6, y + 5), rr.randrange(0, 90), rr.randrange(200, 330), fill=(60, 30, 0), width=2)
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(170, 110, 40))
    tile('bg_leopard.gif', 80, 80, leopard)

    def glitter(im, d, rr):
        d.rectangle((0, 0, 64, 64), fill=(255, 150, 210))
        for _ in range(60):
            d.point((rr.randrange(64), rr.randrange(64)), fill=rr.choice([(255, 255, 255), (255, 210, 240), (200, 0, 120)]))
    tile('bg_glitter.gif', 64, 64, glitter)

    def denim(im, d, rr):
        for y in range(48):
            for x in range(48):
                v = ((x + y) % 4 < 2) * 18 + rr.randint(0, 10)
                im.putpixel((x, y), (40 + v, 70 + v, 130 + v))
    tile('bg_denim.gif', 48, 48, denim)

    def darkred(im, d, rr):
        d.rectangle((0, 0, 64, 64), fill=(20, 0, 0))
        for _ in range(25):
            x, y = rr.randrange(64), rr.randrange(64)
            d.point((x, y), fill=(80, 0, 0))
    tile('bg_blood.gif', 64, 64, darkred)

    def gray_tex(im, d, rr):
        for y in range(64):
            for x in range(64):
                n = rr.randint(185, 205)
                im.putpixel((x, y), (n, n, n))
    tile('bg_concrete.gif', 64, 64, gray_tex)


def photos():
    """crude 'scanned photo' placeholders"""
    def frame(im, d):
        d.rectangle((0, 0, im.size[0] - 1, im.size[1] - 1), outline=(255, 255, 255), width=3)

    im, d = canvas(120, 150, (150, 180, 220))
    d.ellipse((35, 25, 85, 80), fill=(240, 200, 170), outline=(0, 0, 0))
    d.chord((33, 18, 87, 60), 180, 360, fill=(110, 70, 20))
    d.rectangle((25, 90, 95, 150), fill=(200, 0, 0))
    d.polygon([(25, 90), (60, 80), (95, 90)], fill=(200, 0, 0))
    d.ellipse((47, 45, 53, 51), fill=(0, 0, 0))
    d.ellipse((67, 45, 73, 51), fill=(0, 0, 0))
    d.arc((48, 52, 72, 70), 20, 160, fill=(0, 0, 0), width=2)
    frame(im, d)
    save('photo_me.gif', im, transparent=False)

    im, d = canvas(120, 150, (230, 210, 180))
    d.ellipse((35, 25, 85, 80), fill=(200, 150, 120), outline=(0, 0, 0))
    d.chord((30, 15, 90, 85), 180, 360, fill=(240, 220, 120))
    d.rectangle((30, 18, 40, 100), fill=(240, 220, 120))
    d.rectangle((80, 18, 90, 100), fill=(240, 220, 120))
    d.rectangle((25, 90, 95, 150), fill=(150, 0, 200))
    d.ellipse((47, 45, 53, 51), fill=(0, 0, 0))
    d.ellipse((67, 45, 73, 51), fill=(0, 0, 0))
    d.arc((48, 52, 72, 70), 20, 160, fill=(200, 0, 50), width=2)
    frame(im, d)
    save('photo_me2.gif', im, transparent=False)

    im, d = canvas(160, 120, (180, 160, 140))
    d.rectangle((0, 80, 160, 120), fill=(120, 80, 60))
    d.ellipse((50, 45, 120, 100), fill=(255, 160, 60), outline=(0, 0, 0))
    d.ellipse((30, 25, 80, 70), fill=(255, 160, 60), outline=(0, 0, 0))
    d.polygon([(32, 35), (34, 12), (50, 28)], fill=(255, 160, 60), outline=(0, 0, 0))
    d.polygon([(60, 28), (76, 12), (78, 35)], fill=(255, 160, 60), outline=(0, 0, 0))
    d.ellipse((42, 40, 49, 48), fill=(40, 160, 40))
    d.ellipse((60, 40, 67, 48), fill=(40, 160, 40))
    d.line((118, 80, 140, 50), fill=(255, 160, 60), width=6)
    frame(im, d)
    save('photo_cat.gif', im, transparent=False)

    im, d = canvas(160, 120, (140, 200, 120))
    d.rectangle((0, 0, 160, 50), fill=(150, 200, 255))
    d.ellipse((60, 50, 140, 100), fill=(240, 240, 240), outline=(0, 0, 0))
    d.ellipse((30, 30, 80, 80), fill=(240, 240, 240), outline=(0, 0, 0))
    d.ellipse((24, 34, 40, 64), fill=(60, 40, 20))
    d.ellipse((70, 34, 86, 64), fill=(60, 40, 20))
    d.ellipse((90, 60, 110, 80), fill=(60, 40, 20))
    d.ellipse((44, 45, 50, 51), fill=(0, 0, 0))
    d.ellipse((60, 45, 66, 51), fill=(0, 0, 0))
    d.ellipse((50, 58, 60, 66), fill=(0, 0, 0))
    frame(im, d)
    save('photo_dog.gif', im, transparent=False)

    im, d = canvas(200, 130, (170, 210, 255))
    d.rectangle((0, 90, 200, 130), fill=(80, 160, 60))
    d.ellipse((150, 8, 180, 38), fill=(255, 240, 0))
    for i, (x, hgt, col) in enumerate([(20, 70, (0, 0, 200)), (60, 80, (200, 0, 0)), (100, 50, (255, 120, 200)),
                                       (130, 40, (0, 150, 0)), (160, 60, (250, 200, 0))]):
        top = 120 - hgt
        d.ellipse((x, top, x + 18, top + 18), fill=(240, 200, 170), outline=(0, 0, 0))
        d.rectangle((x + 1, top + 18, x + 17, 120), fill=col)
    frame(im, d)
    save('photo_family.gif', im, transparent=False)

    rr = random.Random(52)
    im, d = canvas(160, 120, (20, 20, 40))
    for y in range(120):
        for x in range(160):
            n = rr.randint(0, 30)
            im.putpixel((x, y), (20 + n, 20 + n, 40 + n))
    d.rectangle((0, 95, 160, 120), fill=(10, 10, 10))
    d.ellipse((60, 40, 100, 52), fill=(200, 200, 180))
    d.ellipse((72, 34, 88, 46), fill=(170, 200, 170))
    for x in (66, 76, 86, 94):
        d.point((x, 48), fill=(255, 255, 0))
    d.text((4, 104), '?? 11/3/98 2:14am', font=font('mono', 10), fill=(255, 150, 0))
    frame(im, d)
    save('photo_ufo.gif', im, transparent=False)

    im, d = canvas(200, 130, (120, 200, 255))
    d.rectangle((0, 70, 200, 100), fill=(0, 120, 200))
    d.rectangle((0, 100, 200, 130), fill=(240, 220, 160))
    d.ellipse((20, 10, 50, 40), fill=(255, 230, 0))
    d.polygon([(130, 100), (135, 70), (150, 60), (125, 66)], fill=(0, 0, 0))
    d.line((140, 100, 146, 40), fill=(130, 80, 30), width=4)
    for dx, dy in [(-20, 6), (20, 6), (-14, -8), (14, -8)]:
        d.line((146, 40, 146 + dx, 40 + dy), fill=(0, 140, 0), width=4)
    d.rectangle((60, 104, 100, 112), fill=(255, 0, 100))
    frame(im, d)
    save('photo_beach.gif', im, transparent=False)

    im, d = canvas(200, 120, (200, 200, 200))
    d.rectangle((0, 85, 200, 120), fill=(100, 100, 100))
    d.polygon([(20, 80), (40, 55), (130, 55), (160, 70), (185, 72), (185, 90), (20, 90)], fill=(200, 0, 0), outline=(0, 0, 0))
    d.polygon([(50, 58), (70, 58), (70, 70), (44, 70)], fill=(150, 200, 255))
    d.polygon([(76, 58), (124, 58), (140, 70), (76, 70)], fill=(150, 200, 255))
    d.ellipse((40, 78, 66, 104), fill=(30, 30, 30))
    d.ellipse((140, 78, 166, 104), fill=(30, 30, 30))
    d.ellipse((48, 86, 58, 96), fill=(200, 200, 200))
    d.ellipse((148, 86, 158, 96), fill=(200, 200, 200))
    frame(im, d)
    save('photo_car.gif', im, transparent=False)

    im, d = canvas(160, 120, (255, 240, 220))
    d.rectangle((0, 90, 160, 120), fill=(180, 120, 80))
    d.ellipse((30, 80, 130, 100), fill=(240, 240, 240))
    d.rectangle((40, 50, 120, 90), fill=(130, 70, 30))
    d.ellipse((40, 40, 120, 60), fill=(255, 220, 230))
    d.rectangle((40, 50, 120, 56), fill=(255, 220, 230))
    for x in (60, 80, 100):
        d.rectangle((x - 1, 28, x + 1, 44), fill=(100, 160, 255))
        d.ellipse((x - 2, 22, x + 2, 29), fill=(255, 180, 0))
    frame(im, d)
    save('photo_cake.gif', im, transparent=False)

    im, d = canvas(200, 120, (40, 0, 60))
    d.rectangle((0, 95, 200, 120), fill=(60, 30, 10))
    for x, col in [(30, (255, 0, 0)), (80, (0, 200, 255)), (130, (255, 255, 0)), (170, (0, 255, 100))]:
        d.ellipse((x - 9, 30, x + 9, 48), fill=(240, 200, 170))
        d.rectangle((x - 11, 48, x + 11, 95), fill=col)
        d.chord((x - 10, 26, x + 10, 42), 180, 360, fill=(80, 40, 0))
    d.polygon([(0, 0), (40, 0), (90, 95), (60, 95)], fill=(90, 50, 110))
    d.polygon([(200, 0), (160, 0), (110, 95), (140, 95)], fill=(90, 50, 110))
    frame(im, d)
    save('photo_band.gif', im, transparent=False)

    im, d = canvas(120, 120, (255, 230, 240))
    d.ellipse((20, 60, 100, 130), fill=(255, 255, 255), outline=(200, 200, 255))
    d.ellipse((30, 15, 90, 75), fill=(255, 215, 190), outline=(0, 0, 0))
    d.arc((48, 46, 72, 62), 20, 160, fill=(200, 60, 60), width=2)
    d.ellipse((45, 38, 51, 44), fill=(0, 0, 0))
    d.ellipse((69, 38, 75, 44), fill=(0, 0, 0))
    d.arc((52, 6, 68, 22), 180, 360, fill=(120, 70, 30), width=2)
    frame(im, d)
    save('photo_baby.gif', im, transparent=False)

    im, d = canvas(200, 130, (150, 200, 255))
    d.rectangle((0, 100, 200, 130), fill=(60, 160, 60))
    d.rectangle((50, 55, 150, 105), fill=(255, 250, 220), outline=(0, 0, 0))
    d.polygon([(40, 58), (100, 20), (160, 58)], fill=(150, 40, 30), outline=(0, 0, 0))
    d.rectangle((90, 75, 110, 105), fill=(120, 60, 20))
    for x in (60, 125):
        d.rectangle((x, 65, x + 16, 80), fill=(150, 200, 255), outline=(0, 0, 0))
    frame(im, d)
    save('photo_house.gif', im, transparent=False)

    im, d = canvas(160, 130, (210, 200, 180))
    d.rectangle((0, 100, 160, 130), fill=(140, 100, 60))
    d.rectangle((30, 15, 130, 85), fill=(230, 225, 205), outline=(0, 0, 0))
    d.rectangle((38, 22, 122, 74), fill=(0, 0, 160))
    d.text((42, 28), 'C:\\>_', font=font('mono', 11), fill=(200, 200, 200))
    d.rectangle((60, 85, 100, 94), fill=(230, 225, 205))
    d.rectangle((20, 100, 140, 112), fill=(230, 225, 205), outline=(0, 0, 0))
    frame(im, d)
    save('photo_computer.gif', im, transparent=False)

    im, d = canvas(200, 120, (170, 210, 255))
    d.polygon([(0, 120), (60, 30), (110, 90), (150, 20), (200, 120)], fill=(110, 110, 130))
    d.polygon([(52, 42), (60, 30), (70, 44)], fill=(255, 255, 255))
    d.polygon([(140, 36), (150, 20), (160, 38)], fill=(255, 255, 255))
    d.rectangle((0, 105, 200, 120), fill=(40, 120, 40))
    frame(im, d)
    save('photo_mountain.gif', im, transparent=False)

    im, d = canvas(160, 120, (240, 230, 210))
    d.rectangle((0, 70, 160, 120), fill=(160, 110, 70))
    d.ellipse((20, 64, 140, 104), fill=(250, 250, 250), outline=(0, 0, 0))
    d.ellipse((34, 70, 126, 98), fill=(170, 60, 20))
    for x, y in [(50, 78), (70, 84), (95, 76), (110, 86), (80, 74)]:
        d.ellipse((x - 4, y - 3, x + 4, y + 3), fill=(220, 160, 60))
    for k in range(3):
        d.arc((60 + k * 14, 30, 72 + k * 14, 66), 270, 90, fill=(200, 200, 200))
    frame(im, d)
    save('photo_food.gif', im, transparent=False)

    im, d = canvas(200, 120, (90, 90, 80))
    d.rectangle((40, 30, 160, 110), fill=(60, 60, 50), outline=(0, 0, 0))
    for y in range(40, 100, 14):
        for x in range(50, 150, 20):
            d.rectangle((x, y, x + 14, y + 10), fill=[(200, 50, 50), (60, 160, 60), (230, 200, 60), (120, 120, 200)][(x + y) % 4])
    d.polygon([(30, 30), (100, 0), (170, 30)], fill=(80, 80, 70))
    frame(im, d)
    save('photo_pantry.gif', im, transparent=False)


def misc():
    # webcam offline (snow)
    frames = []
    for i in range(3):
        rr = random.Random(i)
        im, d = canvas(160, 120, (0, 0, 0))
        px = im.load()
        for y in range(0, 120, 2):
            for x in range(0, 160, 2):
                v = rr.randint(0, 200)
                for dx in (0, 1):
                    for dy in (0, 1):
                        px[x + dx, y + dy] = (v, v, v)
        d.rectangle((14, 44, 146, 76), fill=(0, 0, 0))
        ctext(d, (14, 44, 146, 62), 'WEBCAM OFFLINE', font('sansb', 13), (255, 0, 0))
        ctext(d, (14, 60, 146, 76), 'check back later!', font('sans', 10), (255, 255, 255))
        frames.append(im)
    save('webcam_off.gif', frames, 120, transparent=False)

    # broken image icon (original drawing)
    im, d = canvas(24, 26, (192, 192, 192))
    d.rectangle((2, 2, 18, 22), fill=(255, 255, 255), outline=(0, 0, 0))
    d.polygon([(14, 2), (18, 6), (14, 6)], fill=(192, 192, 192), outline=(0, 0, 0))
    d.rectangle((5, 9, 10, 14), fill=(255, 0, 0))
    d.polygon([(10, 14), (14, 10), (15, 16)], fill=(0, 160, 0))
    d.ellipse((7, 16, 11, 20), fill=(0, 0, 255))
    d.line((2, 15, 9, 12, 13, 18, 18, 14), fill=(192, 192, 192), width=2)
    save('broken.gif', im, transparent=False)

    # kava applet loading box
    frames = []
    for i in range(4):
        im, d = canvas(300, 120, (192, 192, 192))
        d.rectangle((0, 0, 299, 119), outline=(128, 128, 128))
        d.line((0, 0, 299, 0), fill=(255, 255, 255))
        d.line((0, 0, 0, 119), fill=(255, 255, 255))
        cup_x = 20
        d.rectangle((cup_x, 40, cup_x + 26, 70), fill=(255, 255, 255), outline=(0, 0, 0))
        d.arc((cup_x + 20, 46, cup_x + 34, 62), 270, 90, fill=(0, 0, 0), width=2)
        for k in range(3):
            y0 = 36 - ((i + k) % 3) * 4
            d.arc((cup_x + 4 + k * 7, y0 - 10, cup_x + 10 + k * 7, y0), 90, 270, fill=(120, 120, 120))
        d.text((70, 30), 'Kava applet loading' + '.' * (i % 4), font=font('sans', 12), fill=(0, 0, 0))
        d.rectangle((70, 56, 270, 70), outline=(0, 0, 0), fill=(255, 255, 255))
        d.rectangle((72, 58, 72 + 49 * (i + 1) - 2, 68), fill=(0, 0, 128))
        d.text((70, 84), 'applet started.', font=font('sans', 10), fill=(60, 60, 60)) if i == 3 else None
        frames.append(im)
    save('kava_applet.gif', frames, [500, 500, 500, 3000], transparent=False)

    # nav buttons
    for name, label, col in [('btn_home.gif', 'HOME', (255, 153, 204)), ('btn_next.gif', 'NEXT >>', (153, 204, 255)),
                             ('btn_back.gif', '<< BACK', (204, 255, 153)), ('btn_links.gif', 'LINKS', (255, 255, 153)),
                             ('btn_about.gif', 'ABOUT ME', (204, 153, 255)), ('btn_enter.gif', 'ENTER', (0, 0, 0))]:
        im, d = canvas(90, 28)
        d.rounded_rectangle((0, 0, 89, 27), 12, fill=col, outline=(0, 0, 0))
        d.rounded_rectangle((3, 2, 86, 12), 6, fill=mix(col, (255, 255, 255), .5))
        ctext(d, (0, 0, 90, 28), label, font('sansb', 13), (0, 0, 0) if col != (0, 0, 0) else (0, 255, 0))
        save(name, im)

    # big ENTER for splash pages (animated)
    frames = []
    for i in range(2):
        im, d = canvas(160, 50, (0, 0, 0))
        d.rectangle((0, 0, 159, 49), outline=(255, 0, 0) if i else (255, 255, 0), width=2)
        ctext(d, (0, 0, 160, 50), '>> ENTER <<', font('sansb', 22), (255, 255, 0) if i else (255, 0, 0))
        frames.append(im)
    save('enter_big.gif', frames, 500, transparent=False)

    # new! and updated! burst
    frames = []
    for i in range(2):
        im, d = canvas(60, 24)
        pts = [(30 + (12 if k % 2 == 0 else 8) * 2.4 * math.cos(k * math.pi / 8) / 2,
                12 + (12 if k % 2 == 0 else 8) * math.sin(k * math.pi / 8)) for k in range(16)]
        d.polygon(pts, fill=(255, 0, 0) if i == 0 else (255, 255, 0))
        ctext(d, (0, 0, 60, 24), 'UPDATED!', font('narrow', 10), (255, 255, 255) if i == 0 else (255, 0, 0))
        frames.append(im)
    save('updated.gif', frames, 400)

    # rainbow bridge for pet memorials
    im, d = canvas(240, 90, (200, 230, 255))
    for k, col in enumerate([(255, 0, 0), (255, 150, 0), (255, 255, 0), (0, 200, 0), (0, 100, 255), (120, 0, 200)]):
        d.arc((10 + k * 6, 20 + k * 6, 230 - k * 6, 200 - k * 6), 180, 360, fill=col, width=6)
    d.rectangle((0, 80, 240, 90), fill=(120, 200, 100))
    for x in range(10, 240, 30):
        d.ellipse((x, 30 + (x % 3) * 4, x + 20, 40 + (x % 3) * 4), fill=(255, 255, 255))
    save('rainbow_bridge.gif', im, transparent=False)

    # pumpkin / snowman / flag for holiday pages
    im, d = canvas(48, 48)
    d.ellipse((4, 10, 44, 46), fill=(255, 130, 0), outline=(120, 50, 0))
    d.line((24, 10, 26, 2), fill=(0, 120, 0), width=3)
    d.polygon([(12, 22), (18, 22), (15, 17)], fill=(0, 0, 0))
    d.polygon([(30, 22), (36, 22), (33, 17)], fill=(0, 0, 0))
    d.chord((12, 26, 36, 40), 0, 180, fill=(0, 0, 0))
    save('pumpkin.gif', im)

    frames = []
    for i in range(2):
        im, d = canvas(48, 64)
        d.ellipse((8, 30, 40, 62), fill=(255, 255, 255), outline=(150, 150, 150))
        d.ellipse((13, 8, 35, 32), fill=(255, 255, 255), outline=(150, 150, 150))
        d.rectangle((14, 2, 34, 10), fill=(0, 0, 0))
        d.rectangle((10, 9, 38, 11), fill=(0, 0, 0))
        d.point([(19, 17), (28, 17)], fill=(0, 0, 0))
        d.polygon([(23, 20), (24, 20), (32, 23)], fill=(255, 120, 0))
        d.line((10, 40, 0, 30 + i * 8), fill=(110, 60, 20), width=2)
        frames.append(im)
    save('snowman.gif', frames, 400)

    # radio tower blinking
    frames = []
    for i in range(2):
        im, d = canvas(40, 64)
        d.line((20, 8, 6, 63), fill=(120, 120, 120), width=2)
        d.line((20, 8, 34, 63), fill=(120, 120, 120), width=2)
        for y in range(16, 60, 8):
            t = (y - 8) / 55
            d.line((20 - 14 * t, y, 20 + 14 * t, y + 6), fill=(150, 150, 150))
        d.ellipse((16, 2, 24, 10), fill=(255, 0, 0) if i == 0 else (90, 0, 0))
        if i == 0:
            for r in (8, 14):
                d.arc((20 - r, 6 - r, 20 + r, 6 + r), 200, 340, fill=(255, 255, 0))
        frames.append(im)
    save('tower.gif', frames, 500)

    # spinning gear (Workbench)
    frames = []
    for i in range(6):
        im, d = canvas(40, 40)
        for k in range(8):
            a = math.radians(k * 45 + i * 7.5)
            d.line((20 + 12 * math.cos(a), 20 + 12 * math.sin(a), 20 + 18 * math.cos(a), 20 + 18 * math.sin(a)),
                   fill=(130, 130, 140), width=6)
        d.ellipse((7, 7, 33, 33), fill=(150, 150, 160), outline=(60, 60, 70))
        d.ellipse((15, 15, 25, 25), fill=KEY, outline=(60, 60, 70))
        frames.append(im)
    save('gear.gif', frames, 90)

    # chili pepper
    im, d = canvas(48, 24)
    d.polygon([(4, 14), (14, 6), (36, 6), (44, 12), (38, 18), (14, 20)], fill=(220, 0, 0), outline=(120, 0, 0))
    d.line((40, 8, 46, 2), fill=(0, 130, 0), width=3)
    d.line((12, 9, 30, 9), fill=(255, 120, 120))
    save('chili.gif', im)

    # steaming pie
    frames = []
    for i in range(3):
        im, d = canvas(64, 48)
        d.chord((4, 20, 60, 46), 180, 360, fill=(220, 160, 80), outline=(120, 70, 20))
        d.rectangle((4, 32, 60, 40), fill=(200, 140, 60), outline=(120, 70, 20))
        for k in range(3):
            x = 18 + k * 14
            d.arc((x - 4 + (i + k) % 2 * 2, 2, x + 4 + (i + k) % 2 * 2, 18), 90, 270, fill=(200, 200, 200))
        frames.append(im)
    save('pie.gif', frames, 250)

    # train
    frames = []
    for i in range(4):
        im, d = canvas(120, 40)
        d.line((0, 37, 120, 37), fill=(80, 80, 80), width=2)
        x = 20 + i * 2
        d.rectangle((x, 12, x + 40, 32), fill=(0, 0, 0))
        d.rectangle((x + 30, 4, x + 46, 32), fill=(180, 0, 0))
        d.rectangle((x + 4, 4, x + 10, 12), fill=(30, 30, 30))
        for wx in (x + 6, x + 22, x + 38):
            d.ellipse((wx - 5, 28, wx + 5, 38), fill=(60, 60, 60), outline=(200, 200, 200))
        for k in range(3):
            d.ellipse((x + 2 - k * 8 - i % 2 * 2, 0 - k * 0 + k, x + 12 - k * 8 - i % 2 * 2, 8 + k), fill=(220, 220, 220))
        d.rectangle((x + 50, 16, x + 90, 32), fill=(0, 0, 160))
        for wx in (x + 56, x + 84):
            d.ellipse((wx - 5, 28, wx + 5, 38), fill=(60, 60, 60))
        frames.append(im)
    save('train.gif', frames, 160)


def main():
    os.makedirs(OUT, exist_ok=True)
    for fn in (logo, hood_art, ad_banners, flames, skull, email, construction, baby, lines, guestbook_buttons,
               awards, creatures, badges, counters, bullets, backgrounds, photos, misc):
        fn()
        print('drew', fn.__name__)
    n = len([f for f in os.listdir(OUT) if f.endswith('.gif')])
    sz = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print('%d GIFs, %d KB' % (n, sz // 1024))


if __name__ == '__main__':
    main()
