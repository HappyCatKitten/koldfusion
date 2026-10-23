#!/usr/bin/env python3
"""Draws every AltaVisor graphic from scratch with Pillow (no outside artwork).

    python3 tools/mkgfx.py        (writes ../images/*.gif)
"""
import math, os, shutil
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'images')
STOCK = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'images'))
FONTS = ['/usr/share/fonts/truetype/liberation/', '/usr/share/fonts/truetype/dejavu/', '/usr/share/fonts/truetype/freefont/']
S = 4
NAVY, GOLD, SKY = (0, 51, 153), (255, 204, 102), (153, 204, 255)


def font(names, size):
    for d in FONTS:
        for n in names:
            if os.path.exists(os.path.join(d, n)):
                return ImageFont.truetype(os.path.join(d, n), size)
    return ImageFont.load_default()


SANS_BI = ['LiberationSans-BoldItalic.ttf', 'DejaVuSans-BoldOblique.ttf']
SANS_B = ['LiberationSans-Bold.ttf', 'DejaVuSans-Bold.ttf']
SANS = ['LiberationSans-Regular.ttf', 'DejaVuSans.ttf']
SERIF_I = ['LiberationSerif-Italic.ttf', 'DejaVuSerif-Italic.ttf']


def save(img, name, size=None, colors=64):
    if size:
        img = img.resize(size, Image.LANCZOS)
    img.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=colors).save(os.path.join(OUT, name))
    print('wrote', name)


def logo(W=480, H=60, name='av_logo.gif'):
    out = (W, H)
    W, H = 480, 60
    img = Image.new('RGB', (W * S, H * S), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # three snowy peaks on the left
    base = 54 * S
    peaks = [(6, 30, 22), (20, 14, 30), (40, 26, 22)]
    for x, top, half in peaks:
        x, top, half = x * S, top * S, half * S
        d.polygon([(x, base), (x + half, top), (x + 2 * half, base)], fill=NAVY)
        d.polygon([(x + half * 0.62, top + (base - top) * 0.38), (x + half, top), (x + half * 1.38, top + (base - top) * 0.38),
                   (x + half * 1.15, top + (base - top) * 0.30), (x + half, top + (base - top) * 0.42),
                   (x + half * 0.85, top + (base - top) * 0.30)], fill=(255, 255, 255))
    # the golden visor arcing over the peaks
    d.arc([2 * S, 4 * S, 88 * S, 64 * S], 200, 340, fill=GOLD, width=6 * S)
    d.arc([2 * S, 4 * S, 88 * S, 64 * S], 200, 340, fill=(204, 153, 0), width=2 * S)
    f = font(SANS_BI, 40 * S)
    d.text((96 * S, 6 * S), 'AltaVisor', font=f, fill=NAVY)
    tw = d.textlength('AltaVisor', font=f)
    f2 = font(SERIF_I, 13 * S)
    d.rectangle([96 * S, 47 * S, 96 * S + tw, 49 * S], fill=GOLD)
    d.text((104 * S + tw, 30 * S), 'smart is beautiful', font=f2, fill=(102, 102, 102))
    save(img, name, out)


def search_btn():
    W, H = 66, 23
    img = Image.new('RGB', (W * S, H * S), GOLD)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([1 * S, 1 * S, (W - 2) * S, (H - 2) * S], radius=5 * S, fill=NAVY, outline=(0, 0, 0), width=S)
    f = font(SANS_B, 12 * S)
    tw = d.textlength('Search', font=f)
    d.text(((W * S - tw) / 2, 4 * S), 'Search', font=f, fill=(255, 255, 255))
    save(img, 'av_search.gif', (W, H))


def dart():
    W, H = 8, 9
    img = Image.new('RGB', (W * S, H * S), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (W * S, H * S / 2), (0, H * S), (2.5 * S, H * S / 2)], fill=(204, 0, 0))
    save(img, 'dart.gif', (W, H), colors=8)


def sponsor():
    """a 120x60 house ad for the Parrot translator"""
    W, H = 120, 60
    img = Image.new('RGB', (W * S, H * S), SKY)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W * S - 1, H * S - 1], outline=NAVY, width=S)
    # parrot: green body, red head, yellow beak
    d.ellipse([8 * S, 20 * S, 30 * S, 50 * S], fill=(0, 153, 51), outline=(0, 0, 0), width=S)
    d.ellipse([12 * S, 8 * S, 32 * S, 28 * S], fill=(204, 0, 0), outline=(0, 0, 0), width=S)
    d.polygon([(30 * S, 14 * S), (38 * S, 18 * S), (30 * S, 24 * S)], fill=(255, 204, 0), outline=(0, 0, 0))
    d.ellipse([22 * S, 13 * S, 26 * S, 17 * S], fill=(255, 255, 255))
    d.ellipse([23 * S, 14 * S, 25 * S, 16 * S], fill=(0, 0, 0))
    d.line([(14 * S, 50 * S), (10 * S, 57 * S)], fill=(0, 0, 0), width=S)
    f = font(SANS_B, 11 * S)
    d.text((42 * S, 8 * S), 'Parrot', font=f, fill=NAVY)
    f2 = font(SANS, 9 * S)
    d.text((42 * S, 22 * S), 'translates', font=f2, fill=(0, 0, 0))
    d.text((42 * S, 32 * S), 'any page!', font=f2, fill=(0, 0, 0))
    d.text((42 * S, 44 * S), 'Squawk >>', font=font(SANS_B, 9 * S), fill=(204, 0, 0))
    save(img, 'sponsor_parrot.gif', (W, H))


def spider():
    """the crawler mascot, Skeeter the spider"""
    W, H = 64, 64
    img = Image.new('RGB', (W * S, H * S), (255, 255, 255))
    d = ImageDraw.Draw(img)
    cx, cy = 32 * S, 34 * S
    d.line([(cx, 0), (cx, cy - 10 * S)], fill=(120, 120, 120), width=S)
    for side in (-1, 1):
        for k in range(4):
            a = math.radians(-40 + k * 27)
            x1 = cx + side * 9 * S
            y1 = cy + (k - 1.5) * 4 * S
            x2 = x1 + side * 14 * S * math.cos(a)
            y2 = y1 - 10 * S * math.sin(a) - 4 * S
            x3 = x2 + side * 6 * S
            y3 = y2 + 12 * S
            d.line([(x1, y1), (x2, y2), (x3, y3)], fill=(0, 0, 0), width=2 * S)
    d.ellipse([cx - 11 * S, cy - 9 * S, cx + 11 * S, cy + 13 * S], fill=NAVY, outline=(0, 0, 0), width=S)
    d.ellipse([cx - 7 * S, cy - 16 * S, cx + 7 * S, cy - 3 * S], fill=NAVY, outline=(0, 0, 0), width=S)
    # a tiny gold visor
    d.chord([cx - 9 * S, cy - 19 * S, cx + 9 * S, cy - 9 * S], 180, 360, fill=GOLD, outline=(0, 0, 0))
    for ex in (-3, 3):
        d.ellipse([cx + (ex - 2) * S, cy - 10 * S, cx + (ex + 2) * S, cy - 6 * S], fill=(255, 255, 255))
        d.ellipse([cx + (ex - 1) * S, cy - 9 * S, cx + (ex + 1) * S, cy - 7 * S], fill=(0, 0, 0))
    save(img, 'skeeter.gif', (W, H))


def bar_pieces():
    for name, col in (('bar_navy.gif', NAVY), ('bar_gold.gif', GOLD), ('bar_gray.gif', (192, 192, 192))):
        Image.new('RGB', (8, 12), col).save(os.path.join(OUT, name))
    Image.new('RGB', (1, 1), (255, 255, 255)).save(os.path.join(OUT, 'pixel.gif'))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    logo(); logo(300, 38, 'av_logo_sm.gif'); search_btn(); dart(); sponsor(); spider(); bar_pieces()
    # stock 1999 GIFs used by the invented homepages in web/
    for g in ['construction.gif', 'new.gif', 'email.gif', 'globe.gif', 'fire.gif', 'rainbow_hr.gif', 'bullet_red.gif',
              'bullet_blue.gif', 'mailbox.gif', 'bg_tile.gif', 'stars_bg.gif', 'netscape_now.gif', 'ie_parody.gif',
              'webring.gif', 'powered_by_kf.gif'] + ['digit_%d.gif' % i for i in range(10)]:
        shutil.copy(os.path.join(STOCK, g), os.path.join(OUT, g))
    print('copied stock GIFs')
