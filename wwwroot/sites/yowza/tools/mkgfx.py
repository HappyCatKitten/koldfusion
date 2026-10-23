#!/usr/bin/env python3
"""Draws every Yowza! graphic from scratch with Pillow (no outside artwork).

    python3 tools/mkgfx.py        (run from anywhere; writes ../images/*.gif)
"""
import math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'images')
FONTS = ['/usr/share/fonts/truetype/liberation/', '/usr/share/fonts/truetype/dejavu/',
         '/usr/share/fonts/truetype/freefont/']


def font(names, size):
    for d in FONTS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


SERIF_B = ['LiberationSerif-Bold.ttf', 'DejaVuSerif-Bold.ttf', 'FreeSerifBold.ttf']
SANS_B = ['LiberationSans-Bold.ttf', 'DejaVuSans-Bold.ttf', 'FreeSansBold.ttf']
SANS = ['LiberationSans-Regular.ttf', 'DejaVuSans.ttf', 'FreeSans.ttf']
NARROW_B = ['LiberationSansNarrow-Bold.ttf', 'DejaVuSansCondensed-Bold.ttf', 'LiberationSans-Bold.ttf']

S = 4  # supersampling factor


def save(img, name, small=None):
    """downsample a 4x canvas and save it as an adaptive-palette GIF"""
    if small:
        img = img.resize(small, Image.LANCZOS)
    img = img.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=64)
    img.save(os.path.join(OUT, name))
    print('wrote', name, img.size)


def logo_word(w, h, size, fill=(204, 0, 51), text='Yowza!'):
    """the bouncing letters: each glyph tilted a little, black drop shadow"""
    img = Image.new('RGBA', (w * S, h * S), (255, 255, 255, 0))
    f = font(SERIF_B, size * S)
    widths = [f.getbbox(ch)[2] - f.getbbox(ch)[0] for ch in text]
    total = sum(widths) + (len(text) - 1) * int(size * S * 0.02)
    x = (w * S - total) // 2
    tilts = [-8, 6, -5, 7, -6, 10]
    lifts = [0, -3, 2, -2, 1, -4]
    for i, ch in enumerate(text):
        g = Image.new('RGBA', (int(size * S * 1.5), int(size * S * 1.6)), (255, 255, 255, 0))
        gd = ImageDraw.Draw(g)
        off = int(size * S * 0.07)
        bb = f.getbbox(ch)
        ox, oy = int(size * S * 0.18) - bb[0], int(size * S * 0.15) - bb[1]
        gd.text((ox + off, oy + off), ch, font=f, fill=(0, 0, 0, 255))
        gd.text((ox, oy), ch, font=f, fill=fill + (255,), stroke_width=max(2, S * 2), stroke_fill=(0, 0, 0, 255))
        g = g.rotate(tilts[i % len(tilts)], resample=Image.BICUBIC)
        y = (h * S - (bb[3] - bb[1])) // 2 - int(size * S * 0.15) + lifts[i % len(lifts)] * S
        img.alpha_composite(g, (x - int(size * S * 0.18), y))
        x += widths[i] + int(size * S * 0.02)
    return img


def flatten(rgba, bg=(255, 255, 255)):
    base = Image.new('RGBA', rgba.size, bg + (255,))
    base.alpha_composite(rgba)
    return base


# ---------------------------------------------------------------- icons (58x58 cells at 4x)
def icon_cell(label):
    img = Image.new('RGBA', (58 * S, 58 * S), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    f = font(NARROW_B, 10 * S)
    tw = d.textlength(label, font=f)
    d.text(((58 * S - tw) / 2, 45 * S), label, font=f, fill=(0, 0, 0))
    return img, d


def icon_new():
    img, d = icon_cell('New')
    cx, cy, r1, r2 = 29 * S, 22 * S, 20 * S, 12 * S
    pts = []
    for i in range(24):
        a = math.pi * 2 * i / 24
        r = r1 if i % 2 == 0 else r2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=(255, 221, 0), outline=(0, 0, 0))
    d.line(pts + [pts[0]], fill=(0, 0, 0), width=S)
    f = font(SANS_B, 10 * S)
    tw = d.textlength('NEW', font=f)
    d.text((cx - tw / 2, cy - 6 * S), 'NEW', font=f, fill=(204, 0, 0))
    return img


def sunglasses(d, cx, cy, sc):
    """two dark lenses with a bridge and arms; sc = pixel scale"""
    lw = max(1, int(sc))
    d.line([(cx - 17 * sc, cy - 4 * sc), (cx + 17 * sc, cy - 4 * sc)], fill=(0, 0, 0), width=lw * 2)
    for side in (-1, 1):
        x0 = cx + side * 2 * sc if side > 0 else cx - 15 * sc
        d.chord([x0, cy - 5 * sc, x0 + 13 * sc, cy + 7 * sc], 0, 180, fill=(20, 20, 60), outline=(0, 0, 0))
        d.rectangle([x0, cy - 5 * sc, x0 + 13 * sc, cy + 1 * sc], fill=(20, 20, 60))
        # glint
        d.line([(x0 + 3 * sc, cy - 3 * sc), (x0 + 6 * sc, cy - 3 * sc)], fill=(170, 200, 255), width=lw)
    d.line([(cx - 17 * sc, cy - 4 * sc), (cx - 20 * sc, cy - 1 * sc)], fill=(0, 0, 0), width=lw * 2)
    d.line([(cx + 17 * sc, cy - 4 * sc), (cx + 20 * sc, cy - 1 * sc)], fill=(0, 0, 0), width=lw * 2)


def icon_cool():
    img, d = icon_cell('Cool')
    cx, cy = 29 * S, 22 * S
    d.ellipse([cx - 19 * S, cy - 19 * S, cx + 19 * S, cy + 19 * S], fill=(255, 204, 51), outline=(0, 0, 0), width=S)
    sunglasses(d, cx, cy - 3 * S, S * 0.95)
    d.arc([cx - 11 * S, cy - 4 * S, cx + 11 * S, cy + 12 * S], 20, 160, fill=(0, 0, 0), width=2 * S)
    return img


def icon_my():
    img, d = icon_cell('My Yowza!')
    cx, cy = 29 * S, 22 * S
    # a little page with a person on it
    d.rectangle([cx - 15 * S, cy - 19 * S, cx + 15 * S, cy + 19 * S], fill=(255, 255, 255), outline=(0, 0, 0), width=S)
    d.rectangle([cx - 15 * S, cy - 19 * S, cx + 15 * S, cy - 12 * S], fill=(102, 153, 204), outline=(0, 0, 0), width=S)
    d.ellipse([cx - 6 * S, cy - 9 * S, cx + 6 * S, cy + 3 * S], fill=(255, 210, 160), outline=(0, 0, 0), width=S)
    d.pieslice([cx - 11 * S, cy + 3 * S, cx + 11 * S, cy + 25 * S], 180, 360, fill=(204, 0, 51), outline=(0, 0, 0))
    d.line([(cx - 15 * S, cy + 14 * S), (cx + 15 * S, cy + 14 * S)], fill=(0, 0, 0), width=S)
    return img


def icon_mail():
    img, d = icon_cell('Mail')
    cx, cy = 29 * S, 22 * S
    box = [cx - 21 * S, cy - 12 * S, cx + 21 * S, cy + 14 * S]
    d.rectangle(box, fill=(255, 255, 240), outline=(0, 0, 0), width=S)
    d.line([(box[0], box[1]), (cx, cy + 3 * S), (box[2], box[1])], fill=(0, 0, 0), width=S)
    d.line([(box[0], box[3]), (cx - 6 * S, cy - 1 * S)], fill=(0, 0, 0), width=S)
    d.line([(box[2], box[3]), (cx + 6 * S, cy - 1 * S)], fill=(0, 0, 0), width=S)
    d.rectangle([cx + 12 * S, cy - 10 * S, cx + 19 * S, cy - 3 * S], fill=(204, 0, 51))
    return img


def icon_help():
    img, d = icon_cell('Help')
    cx, cy = 29 * S, 22 * S
    d.ellipse([cx - 19 * S, cy - 19 * S, cx + 19 * S, cy + 19 * S], fill=(102, 153, 204), outline=(0, 0, 0), width=S)
    f = font(SERIF_B, 30 * S)
    tw = d.textlength('?', font=f)
    d.text((cx - tw / 2 + S, cy - 16 * S + S), '?', font=f, fill=(0, 0, 0))
    d.text((cx - tw / 2, cy - 16 * S), '?', font=f, fill=(255, 255, 255))
    return img


def masthead():
    """600x59 home page header: New, Cool | logo | My Yowza!, Mail, Help"""
    W, H = 600, 59
    img = Image.new('RGBA', (W * S, H * S), (255, 255, 255, 255))
    for x, ic in ((4, icon_new()), (63, icon_cool()), (420, icon_my()), (479, icon_mail()), (538, icon_help())):
        img.paste(ic, (x * S, 1 * S))
    word = logo_word(292, 59, 50)
    img.alpha_composite(word, (125 * S, 0))
    save(flatten(img), 'yowza_main.gif', (W, H))


def small_logo():
    word = logo_word(147, 31, 23)
    save(flatten(word), 'yowza_sm.gif', (147, 31))


def new_badge():
    W, H = 28, 11
    img = Image.new('RGB', (W * S, H * S), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W * S - 1, H * S - 1], fill=(255, 238, 0), outline=(204, 0, 0), width=S)
    f = font(SANS_B, 9 * S)
    tw = d.textlength('NEW!', font=f)
    d.text(((W * S - tw) / 2, -0.5 * S), 'NEW!', font=f, fill=(204, 0, 0))
    save(img, 'new2.gif', (W, H))


def cool_badge():
    W, H = 22, 11
    img = Image.new('RGB', (W * S, H * S), (255, 255, 255))
    d = ImageDraw.Draw(img)
    sunglasses(d, W * S // 2, H * S // 2, S * 0.5)
    save(img, 'cool.gif', (W, H))


def dot_bar():
    """the blue rule under the header (a 1x2 pixel would do, but 1999 sites loved spacer GIFs)"""
    img = Image.new('RGB', (1, 1), (255, 255, 255))
    img.save(os.path.join(OUT, 'pixel.gif'))
    print('wrote pixel.gif')


def ad_banner():
    """an original 468x60 house ad"""
    W, H = 468, 60
    img = Image.new('RGB', (W * S, H * S), (255, 255, 204))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W * S - 1, H * S - 1], outline=(0, 0, 0), width=S)
    for i in range(0, W * S, 24 * S):
        d.polygon([(i, H * S), (i + 12 * S, 44 * S), (i + 24 * S, H * S)], fill=(255, 238, 170))
    f = font(SANS_B, 18 * S)
    d.text((14 * S, 8 * S), 'Get your FREE Yowza! Mail', font=f, fill=(204, 0, 51))
    f2 = font(SANS, 12 * S)
    d.text((14 * S, 34 * S), 'six whole megabytes of storage - for life!*', font=f2, fill=(0, 0, 0))
    d.rounded_rectangle([370 * S, 14 * S, 452 * S, 46 * S], radius=6 * S, fill=(102, 153, 204), outline=(0, 0, 0), width=S)
    f3 = font(SANS_B, 13 * S)
    d.text((381 * S, 22 * S), 'Sign Up!', font=f3, fill=(255, 255, 255))
    save(img, 'ad_mail.gif', (W, H))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    masthead(); small_logo(); new_badge(); cool_badge(); dot_bar(); ad_banner()
