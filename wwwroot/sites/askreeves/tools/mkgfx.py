#!/usr/bin/env python3
"""Draws every Ask Reeves graphic from scratch with Pillow: Reeves the butler, his
Ask! button, the tagline, the keyhole and the little head used on the answer pages.

    python3 tools/mkgfx.py        (writes ../images/*.gif)
"""
import math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'images')
FONTS = ['/usr/share/fonts/truetype/liberation/', '/usr/share/fonts/truetype/dejavu/', '/usr/share/fonts/truetype/freefont/']
S = 4
CREAM = (255, 255, 204)
PURPLE = (102, 102, 153)
OLIVE = (153, 153, 102)
SKIN = (250, 214, 180)
SKIN_D = (222, 176, 140)
COAT = (28, 28, 40)
INK = (0, 0, 0)


def font(names, size):
    for d in FONTS:
        for n in names:
            if os.path.exists(os.path.join(d, n)):
                return ImageFont.truetype(os.path.join(d, n), size)
    return ImageFont.load_default()


SERIF_BI = ['LiberationSerif-BoldItalic.ttf', 'DejaVuSerif-BoldItalic.ttf']
SERIF_B = ['LiberationSerif-Bold.ttf', 'DejaVuSerif-Bold.ttf']
SANS_B = ['LiberationSans-Bold.ttf', 'DejaVuSans-Bold.ttf']


def save(img, name, size=None, colors=64):
    if size:
        img = img.resize(size, Image.LANCZOS)
    img.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=colors).save(os.path.join(OUT, name))
    print('wrote', name)


def P(*xy):
    return [v * S for v in xy]


def head(d, cx, cy, k=1.0):
    """Reeves' head centred on (cx, cy) in 1x units; k scales it"""
    def p(x, y):
        return (cx + x * k) * S, (cy + y * k) * S
    # ears
    for sx in (-1, 1):
        x0, y0 = p(sx * 21 - 4, -4)
        x1, y1 = p(sx * 21 + 4, 8)
        d.ellipse([min(x0, x1), y0, max(x0, x1), y1], fill=SKIN_D, outline=INK, width=S)
    # long face
    d.ellipse([*p(-20, -26), *p(20, 30)], fill=SKIN, outline=INK, width=S)
    # tidy grey hair at the sides, shiny dome on top
    d.chord([*p(-21, -27), *p(21, 10)], 180, 360, fill=SKIN, outline=None)
    for sx in (-1, 1):
        d.pieslice([*p(-22 if sx < 0 else 8, -14), *p(-8 if sx < 0 else 22, 6)], 90 if sx < 0 else 270, 270 if sx < 0 else 450,
                   fill=(150, 150, 160), outline=INK)
    d.arc([*p(-20, -26), *p(20, 30)], 200, 340, fill=INK, width=S)
    d.arc([*p(-9, -22), *p(-1, -16)], 200, 300, fill=(255, 255, 255), width=2 * S)   # shine
    # one eyebrow raised (he has seen your question)
    d.line([p(-12, -6), p(-4, -8)], fill=INK, width=2 * S)
    d.arc([*p(3, -14), *p(13, -4)], 200, 340, fill=INK, width=2 * S)
    # half-closed eyes
    for ex in (-8, 8):
        d.ellipse([*p(ex - 4, -4), *p(ex + 4, 2)], fill=(255, 255, 255), outline=INK, width=S)
        d.ellipse([*p(ex - 1.5, -2), *p(ex + 1.5, 1.5)], fill=INK)
        d.chord([*p(ex - 4, -4), *p(ex + 4, 2)], 180, 360, fill=SKIN_D, outline=INK)
    # long nose
    d.polygon([p(0, -2), p(5, 13), p(-1, 14)], fill=SKIN_D, outline=INK)
    # faint, patient smile
    d.arc([*p(-8, 12), *p(8, 22)], 20, 160, fill=INK, width=S)


def butler():
    """full figure, 140 x 220: head, wing collar, bow tie, tailcoat, towel over one arm, tray in the other"""
    W, H = 140, 220
    img = Image.new('RGB', (W * S, H * S), CREAM)
    d = ImageDraw.Draw(img)
    cx = 70
    # coat tails and body
    d.polygon(P(cx - 36, 78, cx + 36, 78, cx + 44, 212, cx + 6, 206, cx, 120, cx - 6, 206, cx - 44, 212), fill=COAT, outline=INK)
    # white shirt front + waistcoat
    d.polygon(P(cx - 14, 74, cx + 14, 74, cx + 10, 150, cx - 10, 150), fill=(255, 255, 255), outline=INK)
    d.polygon(P(cx - 14, 96, cx - 4, 150, cx - 22, 150, cx - 24, 96), fill=(90, 90, 110), outline=INK)
    d.polygon(P(cx + 14, 96, cx + 4, 150, cx + 22, 150, cx + 24, 96), fill=(90, 90, 110), outline=INK)
    for by in (104, 118, 132):
        d.ellipse(P(cx - 2, by, cx + 2, by + 4), fill=INK)
    # lapels
    d.polygon(P(cx - 36, 78, cx - 14, 74, cx - 20, 120), fill=(50, 50, 66), outline=INK)
    d.polygon(P(cx + 36, 78, cx + 14, 74, cx + 20, 120), fill=(50, 50, 66), outline=INK)
    # neck, wing collar and bow tie
    d.rectangle(P(cx - 8, 60, cx + 8, 76), fill=SKIN, outline=INK, width=S)
    d.polygon(P(cx - 12, 70, cx, 76, cx - 4, 82), fill=(255, 255, 255), outline=INK)
    d.polygon(P(cx + 12, 70, cx, 76, cx + 4, 82), fill=(255, 255, 255), outline=INK)
    d.polygon(P(cx - 12, 74, cx, 79, cx - 12, 85), fill=INK)
    d.polygon(P(cx + 12, 74, cx, 79, cx + 12, 85), fill=INK)
    d.ellipse(P(cx - 3, 76, cx + 3, 82), fill=INK)
    # left arm down with a white towel over it
    d.polygon(P(cx - 36, 80, cx - 48, 150, cx - 38, 154, cx - 26, 96), fill=COAT, outline=INK)
    d.polygon(P(cx - 50, 128, cx - 34, 124, cx - 30, 168, cx - 46, 172), fill=(255, 255, 255), outline=INK)
    d.line(P(cx - 46, 140, cx - 34, 137), fill=(200, 200, 200), width=S)
    # right arm bent, holding a silver tray with a calling card
    d.polygon(P(cx + 36, 80, cx + 50, 120, cx + 44, 126, cx + 28, 96), fill=COAT, outline=INK)
    d.polygon(P(cx + 44, 118, cx + 58, 110, cx + 60, 118, cx + 48, 126), fill=COAT, outline=INK)
    d.ellipse(P(cx + 54, 106, cx + 64, 116), fill=(255, 255, 255), outline=INK, width=S)   # white glove
    d.ellipse(P(cx + 26, 96, cx + 68, 106), fill=(200, 200, 210), outline=INK, width=S)  # tray
    d.ellipse(P(cx + 30, 97, cx + 64, 103), fill=(230, 230, 240))
    d.polygon(P(cx + 38, 98, cx + 54, 96, cx + 56, 101, cx + 40, 103), fill=(255, 255, 255), outline=INK)
    d.text(P(cx + 43, 95.5), '?', font=font(SERIF_B, 6 * S), fill=(204, 0, 0))
    head(d, cx, 36, 1.0)
    save(img, 'reeves.gif', (W, H))


def reeves_small():
    W, H = 60, 70
    img = Image.new('RGB', (W * S, H * S), CREAM)
    d = ImageDraw.Draw(img)
    d.polygon(P(4, 70, 10, 54, 50, 54, 56, 70), fill=COAT, outline=INK)
    d.polygon(P(24, 54, 36, 54, 33, 70, 27, 70), fill=(255, 255, 255), outline=INK)
    d.polygon(P(22, 56, 30, 60, 22, 64), fill=INK)
    d.polygon(P(38, 56, 30, 60, 38, 64), fill=INK)
    head(d, 30, 30, 0.85)
    save(img, 'reeves_sm.gif', (W, H))


def ask_button():
    W, H = 36, 23
    img = Image.new('RGB', (W * S, H * S), CREAM)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(P(1, 1, W - 2, H - 2), radius=8 * S, fill=(204, 0, 0), outline=INK, width=S)
    f = font(SERIF_BI, 13 * S)
    tw = d.textlength('Ask!', font=f)
    d.text(((W * S - tw) / 2, 3 * S), 'Ask!', font=f, fill=(255, 255, 255))
    save(img, 'ask.gif', (W, H))


def tagline():
    W, H = 260, 62
    img = Image.new('RGB', (W * S, H * S), CREAM)
    d = ImageDraw.Draw(img)
    f = font(SERIF_BI, 34 * S)
    d.text((4 * S + 2 * S, 0 + 2 * S), 'Ask Reeves', font=f, fill=(200, 200, 160))
    d.text((4 * S, 0), 'Ask Reeves', font=f, fill=PURPLE)
    f2 = font(SERIF_BI, 13 * S)
    d.text((8 * S, 42 * S), 'Your questions, answered with dignity.', font=f2, fill=(102, 51, 0))
    save(img, 'tagline.gif', (W, H))


def keyhole():
    W, H = 90, 120
    img = Image.new('RGB', (W * S, H * S), (153, 102, 51))
    d = ImageDraw.Draw(img)
    # wood grain
    for i in range(0, W * S, 9 * S):
        d.line([(i, 0), (i + 6 * S, H * S)], fill=(140, 92, 44), width=2 * S)
    d.rounded_rectangle(P(15, 12, 75, 108), radius=10 * S, fill=(212, 175, 55), outline=INK, width=S)
    d.ellipse(P(31, 28, 59, 56), fill=INK)
    d.polygon(P(38, 48, 52, 48, 58, 92, 32, 92), fill=INK)
    # an eye peering through
    d.ellipse(P(35, 34, 55, 48), fill=(255, 255, 255))
    d.ellipse(P(41, 36, 49, 46), fill=(51, 102, 204))
    d.ellipse(P(43, 38, 47, 44), fill=INK)
    for sx in (20, 70):
        d.ellipse(P(sx - 3, 98, sx + 3, 104), fill=(150, 120, 40), outline=INK)
    save(img, 'keyhole.gif', (W, H))


def bullet():
    W, H = 10, 10
    img = Image.new('RGB', (W * S, H * S), (204, 204, 153))
    d = ImageDraw.Draw(img)
    d.ellipse(P(1, 1, 9, 9), fill=(204, 0, 0))
    save(img, 'dot.gif', (W, H), colors=8)
    Image.new('RGB', (1, 1), CREAM).save(os.path.join(OUT, 'pixel.gif'))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    butler(); reeves_small(); ask_button(); tagline(); keyhole(); bullet()
