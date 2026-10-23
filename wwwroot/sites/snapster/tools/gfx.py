#!/usr/bin/env python3
"""Draws every Snapster graphic from scratch with Pillow (no outside artwork).

    python3 tools/gfx.py          (from the site folder; writes images/*.gif)

The mascot is "Snappy", an original cartoon snapping turtle wearing headphones.
A few stock 1999 Web GIFs (KoldFusion badge, counter digits) are copied from the
shared wwwroot/images/ folder so the site never relies on the server fallback.
"""
import math, os, shutil
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, '..'))
OUT = os.path.join(SITE, 'images')
STOCK = os.path.normpath(os.path.join(SITE, '..', '..', 'images'))
FONTDIRS = ['/usr/share/fonts/truetype/liberation/', '/usr/share/fonts/truetype/dejavu/',
            '/usr/share/fonts/truetype/freefont/']

SANS = ['LiberationSans-Regular.ttf', 'DejaVuSans.ttf', 'FreeSans.ttf']
SANS_B = ['LiberationSans-Bold.ttf', 'DejaVuSans-Bold.ttf', 'FreeSansBold.ttf']
SANS_BI = ['LiberationSans-BoldItalic.ttf', 'DejaVuSans-BoldOblique.ttf', 'FreeSansBoldOblique.ttf']
SANS_I = ['LiberationSans-Italic.ttf', 'DejaVuSans-Oblique.ttf', 'FreeSansOblique.ttf']
MONO_B = ['LiberationMono-Bold.ttf', 'DejaVuSansMono-Bold.ttf']

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
G4F = (0x4F, 0x4F, 0x4F)
G66 = (0x66, 0x66, 0x66)
G77 = (0x77, 0x77, 0x77)
G99 = (0x99, 0x99, 0x99)
KHAKI = (0xCC, 0xCC, 0x99)
KHAKI_D = (0x99, 0x99, 0x66)
TEAL = (0x99, 0xCC, 0xCC)
TEAL_D = (0x33, 0x66, 0x66)
WIN = (0xC0, 0xC0, 0xC0)
CLIENT = (0x1A, 0x1A, 0x1A)
S = 4  # supersampling factor


def font(names, size):
    for d in FONTDIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def save(img, name, colors=64, transparent=None):
    """save as an adaptive-palette GIF; `transparent` = RGB colour to key out"""
    img = img.convert('RGB')
    p = img.convert('P', palette=Image.ADAPTIVE, colors=colors)
    if transparent is not None:
        pal = p.getpalette()[:768]
        best, bi = None, 0
        for i in range(len(pal) // 3):
            d = sum((pal[i * 3 + k] - transparent[k]) ** 2 for k in range(3))
            if best is None or d < best:
                best, bi = d, i
        p.save(os.path.join(OUT, name), transparency=bi)
    else:
        p.save(os.path.join(OUT, name))


def down(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


def text_w(f, t):
    b = f.getbbox(t)
    return b[2] - b[0]


# ---------------------------------------------------------------- the mascot
def mascot(size, bg=BLACK, cups=TEAL, outline=WHITE):
    """Snappy, front view: turtle head, hooked beak, angry brows, headphones."""
    W = size * S
    im = Image.new('RGB', (W, W), bg)
    d = ImageDraw.Draw(im)
    u = W / 100.0
    lw = max(2, int(3.2 * u))

    def E(x0, y0, x1, y1, **k):
        d.ellipse([x0 * u, y0 * u, x1 * u, y1 * u], **k)

    # shell rim peeking at the bottom
    d.pieslice([8 * u, 78 * u, 92 * u, 128 * u], 180, 360, fill=(0x55, 0x77, 0x44), outline=outline, width=lw)
    for x in (26, 50, 74):
        d.line([x * u, 80 * u, x * u, 100 * u], fill=outline, width=lw // 2 + 1)
    # neck
    d.rectangle([34 * u, 66 * u, 66 * u, 92 * u], fill=(0x88, 0xAA, 0x66))
    d.line([34 * u, 66 * u, 34 * u, 90 * u], fill=outline, width=lw)
    d.line([66 * u, 66 * u, 66 * u, 90 * u], fill=outline, width=lw)
    # head
    E(20, 18, 80, 76, fill=(0x99, 0xBB, 0x77), outline=outline, width=lw)
    # scaly spots
    for (x, y, r) in ((32, 30, 3), (64, 28, 3.5), (44, 24, 2.5), (58, 40, 2), (36, 44, 2)):
        E(x - r, y - r, x + r, y + r, fill=(0x77, 0x99, 0x55))
    # eyes + brows
    for cx in (37, 63):
        E(cx - 8, 36, cx + 8, 52, fill=WHITE, outline=BLACK, width=lw // 2 + 1)
        E(cx - 3, 41, cx + 4, 50, fill=BLACK)
        E(cx - 1, 42, cx + 1.5, 44.5, fill=WHITE)
    d.line([27 * u, 32 * u, 46 * u, 38 * u], fill=BLACK, width=lw + 2)
    d.line([73 * u, 32 * u, 54 * u, 38 * u], fill=BLACK, width=lw + 2)
    # beak (hooked, pointing down) and the snap-grin
    d.polygon([(41 * u, 52 * u), (59 * u, 52 * u), (53 * u, 66 * u), (50 * u, 70 * u), (47 * u, 66 * u)],
              fill=(0xDD, 0xCC, 0x66), outline=BLACK)
    d.arc([28 * u, 48 * u, 72 * u, 70 * u], 20, 160, fill=BLACK, width=lw)
    E(46, 55, 48, 57, fill=BLACK)
    E(52, 55, 54, 57, fill=BLACK)
    # headphones: band over the top, cups on the sides
    d.arc([12 * u, 4 * u, 88 * u, 70 * u], 195, 345, fill=(0x33, 0x33, 0x33), width=int(7 * u))
    d.arc([12 * u, 4 * u, 88 * u, 70 * u], 195, 345, fill=outline, width=max(1, int(1.6 * u)))
    for x0 in (8, 78):
        d.rounded_rectangle([x0 * u, 34 * u, (x0 + 14) * u, 62 * u], radius=int(5 * u), fill=cups,
                            outline=outline, width=lw)
        d.line([(x0 + 4) * u, 40 * u, (x0 + 4) * u, 56 * u], fill=TEAL_D, width=lw)
    # cord
    d.line([15 * u, 62 * u, 13 * u, 74 * u, 18 * u, 84 * u], fill=(0x33, 0x33, 0x33), width=lw)
    return down(im, size, size)


def logo():
    W, H = 273, 68
    im = Image.new('RGB', (W * S, H * S), BLACK)
    im.paste(mascot(64).resize((64 * S, 64 * S), Image.LANCZOS), (6 * S, 2 * S))
    d = ImageDraw.Draw(im)
    f = font(SANS_BI, 40 * S)
    d.text((78 * S, 0), 'snapster', font=f, fill=WHITE)
    fs = font(SANS_B, 9 * S)
    d.text((82 * S, 55 * S), 'the  music  community  at  modem  speed', font=fs, fill=TEAL)
    save(down(im, W, H), 'logo.gif')
    save(mascot(160, bg=KHAKI, outline=BLACK), 'snappy_big.gif')
    save(mascot(48, bg=CLIENT), 'snappy_48.gif')
    icon = mascot(64, bg=(0, 0, 0x80)).resize((16, 16), Image.LANCZOS)
    save(icon, 'icon16.gif')


def arrows():
    """black top, gray strip at the bottom, two swooshes dropping a note into the strip"""
    W, H = 174, 91
    im = Image.new('RGB', (W * S, H * S), BLACK)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 68 * S, W * S, H * S], fill=G66)
    for (box, col, wd) in (([-40, 8, 150, 150], TEAL, 9), ([-10, 26, 140, 140], KHAKI, 6)):
        d.arc([v * S for v in box], 280, 358, fill=col, width=wd * S)
    # arrow heads
    d.polygon([(132 * S, 66 * S), (157 * S, 66 * S), (145 * S, 86 * S)], fill=TEAL)
    d.polygon([(118 * S, 72 * S), (136 * S, 72 * S), (127 * S, 86 * S)], fill=KHAKI)
    # notes riding the swoosh
    for (x, y, c) in ((54, 22, WHITE), (88, 12, TEAL), (110, 34, KHAKI)):
        d.ellipse([x * S, y * S, (x + 9) * S, (y + 7) * S], fill=c)
        d.line([(x + 8) * S, (y + 3) * S, (x + 8) * S, (y - 14) * S], fill=c, width=2 * S)
        d.line([(x + 8) * S, (y - 14) * S, (x + 14) * S, (y - 9) * S], fill=c, width=2 * S)
    f = font(SANS_BI, 10 * S)
    d.text((8 * S, 74 * S), 'get it while it\'s hot', font=f, fill=WHITE)
    save(down(im, W, H), 'arrows.gif')


def strip_button(name, label, w, h=23, bg=G66, fg=WHITE, hi=False):
    im = Image.new('RGB', (w * S, h * S), bg)
    d = ImageDraw.Draw(im)
    f = font(SANS_BI, 13 * S)
    tw = text_w(f, label)
    x = (w * S - tw) // 2
    if hi:
        d.rounded_rectangle([4 * S, 3 * S, (w - 4) * S, (h - 3) * S], radius=8 * S, fill=(0x44, 0x44, 0x44))
        fg = TEAL
    d.text((x, 3 * S), label, font=f, fill=fg)
    d.line([(w - 1) * S, 4 * S, (w - 1) * S, (h - 4) * S], fill=G99, width=S)
    save(down(im, w, h), name)


def top_buttons():
    for key, label, w in (('home', 'home', 150), ('whatis', 'what is snapster?', 143), ('company', 'company', 87)):
        strip_button('btn_%s.gif' % key, label, w)
        strip_button('btn_%s_mo.gif' % key, label, w, hi=True)
    strip_button('btn_download.gif', 'download >>', 174, h=20)
    strip_button('btn_download_mo.gif', 'download >>', 174, h=20, hi=True)
    # "available music:" label on black
    im = Image.new('RGB', (150 * S, 20 * S), BLACK)
    d = ImageDraw.Draw(im)
    f = font(SANS_BI, 11 * S)
    d.text((24 * S, 4 * S), 'available music:', font=f, fill=TEAL)
    save(down(im, 150, 20), 'available.gif')


def counter_box():
    """the teal rounded number box, sliced into left/top/right/bottom like the real thing"""
    W, H = 230, 20
    im = Image.new('RGB', (W * S, H * S), BLACK)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, (W - 1) * S, (H - 1) * S], radius=6 * S, fill=TEAL)
    d.rounded_rectangle([1 * S, (H - 4) * S, (W - 2) * S, (H - 1) * S], radius=3 * S, fill=(0x77, 0xAA, 0xAA))
    d.rounded_rectangle([0, 0, (W - 1) * S, (H - 3) * S], radius=6 * S, fill=TEAL)
    im = down(im, W, H)
    im.crop((0, 0, 1, 20)).save(os.path.join(OUT, 'num_left.gif'))
    im.crop((1, 0, 223, 3)).save(os.path.join(OUT, 'num_top.gif'))
    im.crop((223, 0, 230, 20)).save(os.path.join(OUT, 'num_right.gif'))
    im.crop((1, 15, 223, 20)).save(os.path.join(OUT, 'num_bottom.gif'))
    # digits for the live counter: 8x12 on teal
    f = font(SANS_B, 13 * S)
    for ch, nm in [(str(i), str(i)) for i in range(10)] + [(',', 'comma')]:
        w = 8 if ch != ',' else 4
        g = Image.new('RGB', (w * S, 12 * S), TEAL)
        gd = ImageDraw.Draw(g)
        tw = text_w(f, ch)
        gd.text(((w * S - tw) // 2 - f.getbbox(ch)[0], -2 * S), ch, font=f, fill=BLACK)
        save(down(g, w, 12), 'cnt_%s.gif' % nm, colors=16)
    g = Image.new('RGB', (60 * S, 12 * S), TEAL)
    gd = ImageDraw.Draw(g)
    gd.text((4 * S, -1 * S), 'songs', font=font(SANS_BI, 12 * S), fill=TEAL_D)
    save(down(g, 60, 12), 'cnt_songs.gif', colors=16)


def curves():
    # right-hand end cap of the header (rows 68 + 23 + 20 + 10)
    W, H = 12, 121
    im = Image.new('RGB', (W * S, H * S), BLACK)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([-20 * S, 68 * S, 11 * S, 111 * S], radius=9 * S, fill=G66)
    save(down(im, W, H), 'head_curve.gif', colors=16)
    # khaki cap above the body: gray left column, rounded corners
    W, H = 554, 10
    im = Image.new('RGB', (W * S, H * S), BLACK)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 160 * S, 40 * S], radius=10 * S, fill=G99)
    d.rectangle([133 * S, 0, 135 * S, H * S], fill=G4F)
    d.rectangle([133 * S, 0, 134 * S, H * S], fill=G77)
    d.rounded_rectangle([135 * S, 0, (W - 1) * S, 40 * S], radius=10 * S, fill=KHAKI)
    d.rectangle([135 * S, 0, 180 * S, 40 * S], fill=KHAKI)
    save(down(im, W, H), 'cap.gif', colors=16)
    # bottom of the body
    W, H = 554, 20
    im = Image.new('RGB', (W * S, H * S), BLACK)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, -40 * S, 160 * S, 12 * S], radius=10 * S, fill=G99)
    d.rounded_rectangle([135 * S, -40 * S, (W - 1) * S, 12 * S], radius=10 * S, fill=KHAKI)
    d.rectangle([135 * S, -40 * S, 180 * S, 12 * S], fill=KHAKI)
    d.rectangle([133 * S, -40 * S, 134 * S, 12 * S], fill=G77)
    d.rectangle([134 * S, -40 * S, 135 * S, 12 * S], fill=G4F)
    save(down(im, W, H), 'bottom.gif', colors=16)
    # decorative curve at the top right of the khaki column (vinyl-record edge)
    W, H = 20, 37
    im = Image.new('RGB', (W * S, H * S), KHAKI)
    d = ImageDraw.Draw(im)
    d.arc([-44 * S, -36 * S, 16 * S, 34 * S], 300, 360, fill=KHAKI_D, width=2 * S)
    d.arc([-44 * S, -30 * S, 10 * S, 30 * S], 310, 360, fill=KHAKI_D, width=S)
    save(down(im, W, H), 'bodycurve.gif', colors=16)
    Image.new('RGB', (1, 1), BLACK).save(os.path.join(OUT, 'clear.gif'), transparency=0)


def left_nav():
    items = [('whatis', 'what is snapster?'), ('download', 'download'), ('advertise', 'advertise'),
             ('company', 'company'), ('groundzero', 'ground zero'), ('artists', 'new artists'),
             ('press', 'press'), ('legal', 'legal dept.'), ('help', 'help'), ('terms', 'terms of use')]
    f = font(SANS_B, 11 * S)
    for key, label in items:
        for suffix, bg, fg, mark in (('', G66, KHAKI, None), ('_on', (0x33, 0x33, 0x33), WHITE, TEAL)):
            im = Image.new('RGB', (133 * S, 16 * S), bg)
            d = ImageDraw.Draw(im)
            if mark:
                d.polygon([(6 * S, 4 * S), (6 * S, 12 * S), (12 * S, 8 * S)], fill=mark)
            else:
                d.ellipse([7 * S, 6 * S, 11 * S, 10 * S], fill=G99)
            d.text((17 * S, 1 * S), label, font=f, fill=fg)
            d.line([0, 15 * S, 133 * S, 15 * S], fill=(0x55, 0x55, 0x55), width=S)
            save(down(im, 133, 16), 'left_%s%s.gif' % (key, suffix), colors=32)
    # spacer with a little "snap!" graphic
    im = Image.new('RGB', (133 * S, 49 * S), G66)
    d = ImageDraw.Draw(im)
    d.text((22 * S, 8 * S), 'snap!', font=font(SANS_BI, 26 * S), fill=(0x88, 0x88, 0x88))
    for i, x in enumerate((96, 104, 112)):
        d.arc([x * S, 12 * S, (x + 10 + i * 6) * S, (34 + i * 2) * S], 300, 60, fill=(0x88, 0x88, 0x88), width=2 * S)
    save(down(im, 133, 49), 'left_space.gif', colors=16)
    im = Image.new('RGB', (133 * S, 13 * S), G99)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, -30 * S, 133 * S, 12 * S], radius=8 * S, fill=G66)
    d.rectangle([0, -30 * S, 30 * S, 12 * S], fill=G66)
    save(down(im, 133, 13), 'left_bottom.gif', colors=16)


def headers():
    titles = {
        'whatis': 'What is Snapster?', 'download': 'Download Snapster', 'company': 'The Company',
        'advertise': 'Advertise With Us', 'help': 'Help & FAQ', 'terms': 'Terms of Use',
        'artists': 'New Artist Program', 'groundzero': 'ground zero', 'press': 'Press Room',
        'legal': 'Legal Department',
    }
    f = font(SANS_BI, 22 * S)
    for key, t in titles.items():
        W, H = 380, 34
        im = Image.new('RGB', (W * S, H * S), KHAKI)
        d = ImageDraw.Draw(im)
        d.text((4 * S + 2 * S, 4 * S + 2 * S), t, font=f, fill=KHAKI_D)
        d.text((4 * S, 4 * S), t, font=f, fill=BLACK)
        tw = text_w(f, t)
        d.arc([0, 29 * S, tw + 60 * S, 53 * S], 190, 350, fill=TEAL_D, width=2 * S)
        save(down(im, W, H), 'hdr_%s.gif' % key, colors=32)


def download_now():
    for suffix, bg in (('', (0x33, 0x66, 0x66)), ('_mo', (0x22, 0x44, 0x44))):
        W, H = 170, 44
        im = Image.new('RGB', (W * S, H * S), KHAKI)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([2 * S, 2 * S, (W - 2) * S, (H - 2) * S], radius=14 * S, fill=bg, outline=BLACK,
                            width=2 * S)
        d.polygon([(14 * S, 12 * S), (30 * S, 12 * S), (30 * S, 20 * S), (36 * S, 20 * S), (22 * S, 34 * S),
                   (8 * S, 20 * S), (14 * S, 20 * S)], fill=KHAKI)
        d.text((44 * S, 7 * S), 'Download', font=font(SANS_BI, 15 * S), fill=WHITE)
        d.text((44 * S, 23 * S), 'Snapster NOW!', font=font(SANS_B, 12 * S), fill=TEAL)
        save(down(im, W, H), 'download_now%s.gif' % suffix)


def background():
    im = Image.new('RGB', (64, 64), (0x08, 0x08, 0x08))
    d = ImageDraw.Draw(im)
    for i in range(-64, 64, 8):
        d.line([i, 64, i + 64, 0], fill=(0x14, 0x14, 0x14))
    for x in range(0, 64, 16):
        h = (x * 7) % 13 + 3
        d.line([x + 4, 40 - h, x + 4, 40 + h], fill=(0x1C, 0x1C, 0x1C))
    save(im, 'bk.gif', colors=8)


def sponsor():
    W, H = 120, 90
    im = Image.new('RGB', (W * S, H * S), (0x22, 0x22, 0x55))
    d = ImageDraw.Draw(im)
    for i in range(0, H, 6):
        d.line([0, i * S, W * S, i * S], fill=(0x2A, 0x2A, 0x66), width=S)
    d.text((6 * S, 4 * S), 'RadioRhombus', font=font(SANS_BI, 15 * S), fill=(0xFF, 0xCC, 0x00))
    d.text((6 * S, 24 * S), 'presents', font=font(SANS_I, 10 * S), fill=WHITE)
    d.text((6 * S, 38 * S), 'WIN a 32MB', font=font(SANS_B, 13 * S), fill=WHITE)
    d.text((6 * S, 54 * S), 'MP3 player!', font=font(SANS_B, 13 * S), fill=WHITE)
    d.rounded_rectangle([20 * S, 70 * S, 100 * S, 86 * S], radius=6 * S, fill=(0xFF, 0xCC, 0x00))
    d.text((32 * S, 71 * S), 'click here', font=font(SANS_B, 11 * S), fill=BLACK)
    save(down(im, W, H), 'sponsor.gif')


def screenshot():
    """a tiny schematic of the client window for the What Is page"""
    W, H = 220, 160
    im = Image.new('RGB', (W * S, H * S), WIN)
    d = ImageDraw.Draw(im)
    d.rectangle([2 * S, 2 * S, (W - 3) * S, 14 * S], fill=(0, 0, 0x80))
    d.text((6 * S, 2 * S), 'Snapster v2.0 BETA 5', font=font(SANS_B, 9 * S), fill=WHITE)
    for i in range(3):
        d.rectangle([(W - 13 - i * 11) * S, 4 * S, (W - 5 - i * 11) * S, 12 * S], fill=WIN, outline=BLACK)
    d.rectangle([2 * S, 16 * S, (W - 3) * S, (H - 14) * S], fill=CLIENT)
    cols = [TEAL, KHAKI, (0x99, 0xCC, 0x66), (0xCC, 0x99, 0x66), WHITE, TEAL, KHAKI]
    for i in range(7):
        d.rounded_rectangle([(8 + i * 29) * S, 20 * S, (28 + i * 29) * S, 36 * S], radius=3 * S, fill=cols[i])
    d.rectangle([6 * S, 42 * S, (W - 7) * S, 52 * S], fill=(0x55, 0x55, 0x55))
    for r in range(9):
        y = 56 + r * 9
        d.rectangle([6 * S, y * S, (W - 7) * S, (y + 7) * S], fill=(0x11, 0x11, 0x11) if r % 2 else BLACK)
        dot = [(0x00, 0xCC, 0x00), (0xEE, 0xCC, 0x00), (0xCC, 0x00, 0x00)][r % 3]
        d.ellipse([8 * S, (y + 1) * S, 13 * S, (y + 6) * S], fill=dot)
        d.line([16 * S, (y + 4) * S, (60 + (r * 37) % 70) * S, (y + 4) * S], fill=(0xCC, 0xCC, 0xCC), width=2 * S)
        d.line([150 * S, (y + 4) * S, 200 * S, (y + 4) * S], fill=(0x88, 0x88, 0x88), width=2 * S)
    d.rectangle([2 * S, (H - 12) * S, (W - 3) * S, (H - 3) * S], fill=WIN, outline=(0x80, 0x80, 0x80))
    d.text((6 * S, (H - 12) * S), 'Online (snapfan_99): Sharing 47 songs', font=font(SANS, 8 * S), fill=BLACK)
    save(down(im, W, H), 'screenshot.gif')


def broom_closet():
    W, H = 130, 170
    im = Image.new('RGB', (W * S, H * S), KHAKI)
    d = ImageDraw.Draw(im)
    d.rectangle([20 * S, 8 * S, 110 * S, 168 * S], fill=(0x66, 0x44, 0x22), outline=BLACK, width=2 * S)
    d.rectangle([28 * S, 18 * S, 102 * S, 80 * S], outline=(0x44, 0x2A, 0x11), width=2 * S)
    d.rectangle([28 * S, 92 * S, 102 * S, 158 * S], outline=(0x44, 0x2A, 0x11), width=2 * S)
    d.ellipse([92 * S, 84 * S, 100 * S, 92 * S], fill=(0xDD, 0xBB, 0x33), outline=BLACK)
    d.rectangle([34 * S, 30 * S, 96 * S, 58 * S], fill=WHITE, outline=BLACK, width=S)
    d.text((40 * S, 31 * S), 'LEGAL', font=font(SANS_B, 12 * S), fill=BLACK)
    d.text((40 * S, 44 * S), 'DEPT.', font=font(SANS_B, 12 * S), fill=(0xAA, 0, 0))
    d.text((38 * S, 62 * S), '(knock)', font=font(SANS_I, 9 * S), fill=KHAKI)
    # broom leaning against the door
    d.line([8 * S, 40 * S, 30 * S, 150 * S], fill=(0xAA, 0x77, 0x33), width=3 * S)
    d.polygon([(22 * S, 142 * S), (40 * S, 138 * S), (46 * S, 168 * S), (18 * S, 168 * S)], fill=(0xDD, 0xBB, 0x55),
              outline=BLACK)
    # light under the door, and a mop bucket
    d.line([22 * S, 166 * S, 108 * S, 166 * S], fill=(0xFF, 0xEE, 0x88), width=2 * S)
    d.polygon([(84 * S, 140 * S), (124 * S, 140 * S), (120 * S, 168 * S), (88 * S, 168 * S)], fill=(0x77, 0x88, 0x99),
              outline=BLACK)
    save(down(im, W, H), 'broom_closet.gif')


def punchline():
    W, H = 360, 40
    im = Image.new('RGB', (W * S, H * S), KHAKI)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([1 * S, 1 * S, (W - 2) * S, (H - 2) * S], radius=6 * S, fill=(0xFF, 0xFF, 0xCC),
                        outline=(0xAA, 0, 0), width=2 * S)
    d.text((10 * S, 4 * S), 'Download complete! (Not really.)', font=font(SANS_B, 13 * S), fill=(0xAA, 0, 0))
    d.text((10 * S, 21 * S), 'This is a parody. Nothing was downloaded. Your modem thanks you.',
           font=font(SANS_I, 10 * S), fill=BLACK)
    save(down(im, W, H), 'punchline.gif')


# ---------------------------------------------------------------- client chrome
def window_chrome():
    W, H = 584, 18
    im = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(im)
    a, b = (0, 0, 0x80), (0x10, 0x84, 0xD0)
    for x in range(W):
        t = x / (W - 1)
        d.line([x, 0, x, H], fill=tuple(int(a[k] + (b[k] - a[k]) * t) for k in range(3)))
    im.paste(mascot(64, bg=(0, 0, 0x80)).resize((16, 16), Image.LANCZOS), (1, 1))
    big = im.resize((W * S, H * S))
    bd = ImageDraw.Draw(big)
    bd.text((22 * S, 1 * S), 'Snapster v2.0 BETA 5', font=font(SANS_B, 11 * S), fill=WHITE)
    im2 = down(big, W, H)
    im2.paste(im.crop((0, 0, 18, 18)), (0, 0))
    save(im2, 'titlebar.gif')
    for name in ('min', 'max', 'close'):
        g = Image.new('RGB', (16, 14), WIN)
        d = ImageDraw.Draw(g)
        d.line([0, 0, 15, 0], fill=WHITE)
        d.line([0, 0, 0, 13], fill=WHITE)
        d.line([0, 13, 15, 13], fill=BLACK)
        d.line([15, 0, 15, 13], fill=BLACK)
        d.line([1, 12, 14, 12], fill=(0x80, 0x80, 0x80))
        d.line([14, 1, 14, 12], fill=(0x80, 0x80, 0x80))
        if name == 'min':
            d.rectangle([4, 9, 9, 10], fill=BLACK)
        elif name == 'max':
            d.rectangle([3, 2, 11, 10], outline=BLACK)
            d.line([3, 3, 11, 3], fill=BLACK)
        else:
            for o in (0, 1):
                d.line([4 + o, 3, 10 + o, 9], fill=BLACK)
                d.line([10 + o, 3, 4 + o, 9], fill=BLACK)
        save(g, 'win_%s.gif' % name, colors=8)


def icon(kind, size, col, accent):
    W = size * S
    im = Image.new('RGB', (W, W), CLIENT)
    d = ImageDraw.Draw(im)
    u = W / 32.0
    lw = int(2.2 * u)
    if kind == 'home':
        d.polygon([(16 * u, 4 * u), (29 * u, 16 * u), (3 * u, 16 * u)], fill=accent, outline=col)
        d.rectangle([7 * u, 16 * u, 25 * u, 28 * u], fill=col)
        d.rectangle([13 * u, 20 * u, 19 * u, 28 * u], fill=CLIENT)
        d.rectangle([21 * u, 6 * u, 24 * u, 12 * u], fill=col)
    elif kind == 'chat':
        d.rounded_rectangle([2 * u, 4 * u, 24 * u, 18 * u], radius=int(5 * u), fill=col)
        d.polygon([(6 * u, 17 * u), (12 * u, 17 * u), (5 * u, 23 * u)], fill=col)
        d.rounded_rectangle([12 * u, 13 * u, 30 * u, 25 * u], radius=int(4 * u), fill=accent)
        d.polygon([(22 * u, 24 * u), (27 * u, 24 * u), (28 * u, 29 * u)], fill=accent)
        for x in (8, 13, 18):
            d.ellipse([x * u, 10 * u, (x + 2.4) * u, 12.4 * u], fill=CLIENT)
    elif kind == 'library':
        d.polygon([(2 * u, 8 * u), (11 * u, 8 * u), (14 * u, 11 * u), (30 * u, 11 * u), (30 * u, 27 * u),
                   (2 * u, 27 * u)], fill=accent)
        d.rectangle([2 * u, 13 * u, 30 * u, 27 * u], fill=col)
        d.ellipse([12 * u, 20 * u, 17 * u, 24 * u], fill=CLIENT)
        d.line([16.5 * u, 22 * u, 16.5 * u, 14.5 * u], fill=CLIENT, width=lw)
        d.line([16.5 * u, 14.5 * u, 21 * u, 17 * u], fill=CLIENT, width=lw)
    elif kind == 'search':
        d.ellipse([3 * u, 3 * u, 20 * u, 20 * u], outline=col, width=int(3 * u))
        d.ellipse([7 * u, 7 * u, 12 * u, 12 * u], fill=accent)
        d.line([18 * u, 18 * u, 28 * u, 28 * u], fill=col, width=int(4.5 * u))
    elif kind == 'hotlist':
        pts = []
        for i in range(10):
            r = 9 * u if i % 2 == 0 else 4 * u
            a = math.pi / 2 + i * math.pi / 5
            pts.append((10 * u + r * math.cos(a), 11 * u - r * math.sin(a)))
        d.polygon(pts, fill=accent)
        for y in (8, 15, 22, 28):
            d.line([20 * u, y * u, 30 * u, y * u], fill=col, width=lw)
        d.line([4 * u, 25 * u, 16 * u, 25 * u], fill=col, width=lw)
    elif kind == 'transfer':
        d.polygon([(9 * u, 3 * u), (16 * u, 12 * u), (12 * u, 12 * u), (12 * u, 28 * u), (6 * u, 28 * u),
                   (6 * u, 12 * u), (2 * u, 12 * u)], fill=accent)
        d.polygon([(23 * u, 29 * u), (30 * u, 20 * u), (26 * u, 20 * u), (26 * u, 4 * u), (20 * u, 4 * u),
                   (20 * u, 20 * u), (16 * u, 20 * u)], fill=col)
    elif kind == 'discover':
        d.ellipse([3 * u, 3 * u, 29 * u, 29 * u], outline=col, width=int(2.5 * u))
        d.polygon([(16 * u, 6 * u), (19 * u, 16 * u), (16 * u, 26 * u), (13 * u, 16 * u)], fill=accent)
        d.polygon([(16 * u, 16 * u), (19 * u, 16 * u), (16 * u, 26 * u), (13 * u, 16 * u)], fill=col)
    elif kind == 'help':
        d.ellipse([3 * u, 3 * u, 29 * u, 29 * u], fill=accent)
        f = font(SANS_B, int(22 * u))
        tw = text_w(f, '?')
        d.text(((W - tw) / 2 - f.getbbox('?')[0], 3 * u), '?', font=f, fill=CLIENT)
    return down(im, size, size)


TABS = [('home', 'Home'), ('chat', 'Chat'), ('library', 'Library'), ('search', 'Search'),
        ('hotlist', 'Hot List'), ('transfer', 'Transfer'), ('discover', 'Discover'), ('help', 'Help')]


def tabs():
    f = font(SANS_B, 10 * S)
    for kind, label in TABS:
        for suffix, col, accent, bg, fg in (('', (0x99, 0x99, 0x99), (0x55, 0x77, 0x77), CLIENT, (0xAA, 0xAA, 0xAA)),
                                            ('_on', WHITE, TEAL, (0x3A, 0x3A, 0x3A), WHITE),
                                            ('_mo', (0xDD, 0xDD, 0xDD), (0x77, 0xAA, 0xAA), (0x2A, 0x2A, 0x2A), WHITE)):
            W, H = 70, 50
            im = Image.new('RGB', (W * S, H * S), bg)
            ic = icon(kind, 30, col, accent)
            if bg != CLIENT:
                ic2 = Image.new('RGB', ic.size, bg)
                px, px2 = ic.load(), ic2.load()
                for y in range(ic.size[1]):
                    for x in range(ic.size[0]):
                        p = px[x, y]
                        px2[x, y] = bg if max(abs(p[k] - CLIENT[k]) for k in range(3)) < 6 else p
                ic = ic2
            im.paste(ic.resize((30 * S, 30 * S), Image.LANCZOS), (20 * S, 3 * S))
            d = ImageDraw.Draw(im)
            tw = text_w(f, label)
            d.text(((W * S - tw) // 2, 35 * S), label, font=f, fill=fg)
            if suffix == '_on':
                d.rectangle([4 * S, (H - 3) * S, (W - 4) * S, (H - 1) * S], fill=TEAL)
                d.line([0, 0, 0, H * S], fill=(0x55, 0x55, 0x55), width=S)
                d.line([(W - 1) * S, 0, (W - 1) * S, H * S], fill=(0x0A, 0x0A, 0x0A), width=S)
            save(down(im, W, H), 'tab_%s%s.gif' % (kind, suffix))


def dots_and_icons():
    for name, col in (('green', (0x00, 0xCC, 0x00)), ('yellow', (0xEE, 0xCC, 0x00)), ('red', (0xDD, 0x11, 0x11)),
                      ('gray', (0x77, 0x77, 0x77))):
        im = Image.new('RGB', (10 * S, 10 * S), (255, 0, 255))
        d = ImageDraw.Draw(im)
        d.ellipse([1 * S, 1 * S, 9 * S, 9 * S], fill=col, outline=BLACK, width=S)
        d.ellipse([3 * S, 3 * S, 5 * S, 5 * S], fill=tuple(min(255, c + 110) for c in col))
        im = im.resize((10, 10), Image.NEAREST)
        save(im, 'dot_%s.gif' % name, colors=8, transparent=(255, 0, 255))
    # users online/offline
    for name, face, extra in (('on', (0xFF, 0xCC, 0x33), 'smile'), ('off', (0x77, 0x77, 0x77), 'zz')):
        im = Image.new('RGB', (16 * S, 16 * S), (255, 0, 255))
        d = ImageDraw.Draw(im)
        d.ellipse([1 * S, 1 * S, 14 * S, 14 * S], fill=face, outline=BLACK, width=S)
        d.ellipse([4 * S, 5 * S, 6 * S, 7 * S], fill=BLACK)
        d.ellipse([9 * S, 5 * S, 11 * S, 7 * S], fill=BLACK)
        if extra == 'smile':
            d.arc([4 * S, 6 * S, 11 * S, 12 * S], 20, 160, fill=BLACK, width=S)
        else:
            d.line([5 * S, 10 * S, 10 * S, 10 * S], fill=BLACK, width=S)
        im = im.resize((16, 16), Image.NEAREST)
        save(im, 'user_%s.gif' % name, colors=8, transparent=(255, 0, 255))
    # library: folders, mp3 note page, tree lines
    for name, open_ in (('folder', False), ('folder_open', True)):
        im = Image.new('RGB', (16, 16), (255, 0, 255))
        d = ImageDraw.Draw(im)
        d.polygon([(1, 3), (6, 3), (7, 5), (14, 5), (14, 13), (1, 13)], fill=(0xCC, 0xAA, 0x33), outline=BLACK)
        if open_:
            d.polygon([(3, 7), (15, 7), (13, 13), (1, 13)], fill=(0xFF, 0xDD, 0x66), outline=BLACK)
        else:
            d.rectangle([1, 6, 14, 13], fill=(0xFF, 0xDD, 0x66), outline=BLACK)
        save(im, '%s.gif' % name, colors=8, transparent=(255, 0, 255))
    im = Image.new('RGB', (16, 16), (255, 0, 255))
    d = ImageDraw.Draw(im)
    d.polygon([(3, 1), (10, 1), (13, 4), (13, 15), (3, 15)], fill=WHITE, outline=BLACK)
    d.ellipse([5, 10, 8, 13], fill=(0, 0x66, 0x99))
    d.line([8, 11, 8, 5], fill=(0, 0x66, 0x99))
    d.line([8, 5, 11, 7], fill=(0, 0x66, 0x99))
    save(im, 'mp3.gif', colors=8, transparent=(255, 0, 255))
    for name in ('t', 'l', 'i', 'blank'):
        im = Image.new('RGB', (16, 16), (255, 0, 255))
        d = ImageDraw.Draw(im)
        c = (0x88, 0x88, 0x88)
        if name in ('t', 'i'):
            for y in range(0, 16, 2):
                d.point((7, y), fill=c)
        if name == 'l':
            for y in range(0, 8, 2):
                d.point((7, y), fill=c)
        if name in ('t', 'l'):
            for x in range(7, 16, 2):
                d.point((x, 8), fill=c)
        save(im, 'tree_%s.gif' % name, colors=4, transparent=(255, 0, 255))


def progress_bars():
    W, H = 100, 11
    for i in range(21):
        im = Image.new('RGB', (W, H), BLACK)
        d = ImageDraw.Draw(im)
        d.line([0, 0, W - 1, 0], fill=(0x44, 0x44, 0x44))
        d.line([0, 0, 0, H - 1], fill=(0x44, 0x44, 0x44))
        d.line([0, H - 1, W - 1, H - 1], fill=(0x88, 0x88, 0x88))
        d.line([W - 1, 0, W - 1, H - 1], fill=(0x88, 0x88, 0x88))
        for b in range(i):
            x = 2 + b * 4.8
            d.rectangle([int(x), 2, int(x + 3.6), H - 3], fill=(0x33, 0xCC, 0x33) if i < 20 else TEAL)
        save(im, 'bar_%02d.gif' % i, colors=8)


def copy_stock():
    for n in ['powered_by_kf.gif'] + ['digit_%d.gif' % i for i in range(10)]:
        src = os.path.join(STOCK, n)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(OUT, n))


def main():
    os.makedirs(OUT, exist_ok=True)
    logo(); arrows(); top_buttons(); counter_box(); curves(); left_nav(); headers(); download_now()
    background(); sponsor(); screenshot(); broom_closet(); punchline()
    window_chrome(); tabs(); dots_and_icons(); progress_bars(); copy_stock()
    print('wrote %d GIFs to %s' % (len([f for f in os.listdir(OUT) if f.endswith('.gif')]), OUT))


if __name__ == '__main__':
    main()
