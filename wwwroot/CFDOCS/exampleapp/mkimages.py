#!/usr/bin/env python3
"""mkimages.py - draws the GIFs in /CFDOCS/exampleapp/images (KoldFusion Example Applications).
Run: python3 wwwroot/CFDOCS/exampleapp/mkimages.py
Reuses the helpers in tools/mkgraphics.py (fonts, web-safe GIF writer)."""
import math, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import mkgraphics as G
from PIL import Image, ImageDraw

OUT = os.path.join(ROOT, 'wwwroot', 'CFDOCS', 'exampleapp', 'images')
os.makedirs(OUT, exist_ok=True)
W = (255, 255, 255); K = (0, 0, 0)
NAVY = (0, 51, 153); GOLD = (255, 204, 0); SAGE = (153, 204, 153)


def ss_canvas(w, h, ss=4, bg=(0, 0, 0, 0)):
    im = Image.new('RGBA', (w * ss, h * ss), bg)
    return im, ImageDraw.Draw(im), ss


def finish(im, w, h):
    return im.resize((w, h), Image.LANCZOS)


def save(im, name, pal=64, transparent=False, matte=W):
    G.save_gif(im, os.path.join(OUT, name), pal=pal, transparent=transparent, matte=matte)


def globe(dr, cx, cy, r, ss, sea=(0, 102, 204), land=(102, 204, 102), grid=GOLD):
    dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=sea, outline=(0, 0, 102), width=ss)
    # blobby continents
    for (dx, dy, rx, ry) in [(-0.35, -0.25, 0.30, 0.22), (-0.2, 0.25, 0.18, 0.35), (0.35, -0.1, 0.28, 0.4), (0.5, 0.45, 0.15, 0.1)]:
        x, y = cx + dx * r, cy + dy * r
        dr.ellipse([x - rx * r, y - ry * r, x + rx * r, y + ry * r], fill=land)
    dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 0, 102), width=ss)
    for k in (-0.5, 0, 0.5):   # latitudes
        y = cy + k * r
        hw = math.sqrt(max(0, r * r - (k * r) ** 2))
        dr.line([cx - hw, y, cx + hw, y], fill=grid, width=max(1, ss // 2))
    for k in (0.35, 0.75):     # meridians
        dr.ellipse([cx - k * r, cy - r, cx + k * r, cy + r], outline=grid, width=max(1, ss // 2))
    dr.line([cx, cy - r, cx, cy + r], fill=grid, width=max(1, ss // 2))


def gc_logo():
    w, h = 300, 64
    im, dr, ss = ss_canvas(w, h, bg=(255, 255, 255, 255))
    globe(dr, 32 * ss, 32 * ss, 27 * ss, ss)
    f = G.font('sans_bi', 34 * ss)
    dr.text((66 * ss, 4 * ss), 'GlobalCorp', font=f, fill=NAVY)
    f2 = G.font('sans_b', 11 * ss)
    dr.rectangle([68 * ss, 46 * ss, 292 * ss, 48 * ss], fill=GOLD)
    dr.text((68 * ss, 50 * ss), 'I N T R A N E T   ·   S I N C E   1 9 8 5', font=f2, fill=(102, 102, 102))
    save(finish(im, w, h), 'gc_logo.gif', pal=96)


def gc_small_logo():
    w, h = 32, 32
    im, dr, ss = ss_canvas(w, h, ss=8)
    globe(dr, 16 * ss, 16 * ss, 14 * ss, ss)
    save(finish(im, w, h), 'gc_globe.gif', pal=48, transparent=True)


def photo(n, bgc):
    w, h = 72, 90
    im, dr, ss = ss_canvas(w, h, bg=bgc + (255,))
    sil = (90, 90, 110)
    dr.ellipse([22 * ss, 14 * ss, 50 * ss, 46 * ss], fill=sil)                  # head
    dr.ellipse([6 * ss, 50 * ss, 66 * ss, 120 * ss], fill=sil)                   # shoulders
    dr.rectangle([30 * ss, 42 * ss, 42 * ss, 54 * ss], fill=sil)                 # neck
    im = finish(im, w, h)
    d2 = ImageDraw.Draw(im)
    d2.rectangle([0, 0, w - 1, h - 1], outline=(102, 102, 102))
    f = G.font('sans', 9)
    G.text_center(d2, w // 2, h - 12, 'NO PHOTO', f, (255, 255, 255))
    save(im, 'photo_%d.gif' % n, pal=32)


def icon(name, draw, w=32, h=32, ss=8):
    im, dr, s = ss_canvas(w, h, ss=ss)
    draw(dr, s)
    save(finish(im, w, h), name, pal=48, transparent=True)


def ic_directory(dr, s):
    dr.rounded_rectangle([3 * s, 7 * s, 29 * s, 27 * s], radius=2 * s, fill=(255, 255, 204), outline=K, width=s)
    dr.ellipse([7 * s, 11 * s, 14 * s, 18 * s], fill=(90, 90, 110))
    dr.ellipse([5 * s, 18 * s, 16 * s, 28 * s], fill=(90, 90, 110))
    dr.rectangle([3 * s, 24 * s, 29 * s, 27 * s], fill=(255, 255, 204))
    dr.rounded_rectangle([3 * s, 7 * s, 29 * s, 27 * s], radius=2 * s, outline=K, width=s)
    for y in (12, 16, 20):
        dr.line([17 * s, y * s, 26 * s, y * s], fill=(0, 51, 153), width=s)
    dr.ellipse([9 * s, 3 * s, 13 * s, 8 * s], outline=K, width=s)
    dr.ellipse([19 * s, 3 * s, 23 * s, 8 * s], outline=K, width=s)


def ic_forum(dr, s):
    dr.rounded_rectangle([2 * s, 4 * s, 20 * s, 16 * s], radius=4 * s, fill=(204, 255, 255), outline=K, width=s)
    dr.polygon([(6 * s, 15 * s), (5 * s, 21 * s), (11 * s, 15 * s)], fill=(204, 255, 255), outline=K)
    dr.rounded_rectangle([12 * s, 13 * s, 30 * s, 25 * s], radius=4 * s, fill=(255, 255, 153), outline=K, width=s)
    dr.polygon([(24 * s, 24 * s), (27 * s, 30 * s), (20 * s, 24 * s)], fill=(255, 255, 153), outline=K)
    for x in (16, 21, 26):
        dr.ellipse([(x - 1) * s, 18 * s, (x + 1) * s, 20 * s], fill=K)


def ic_cart(dr, s):
    c = (0, 51, 153)
    dr.line([2 * s, 6 * s, 7 * s, 6 * s, 11 * s, 22 * s, 26 * s, 22 * s], fill=c, width=2 * s, joint='curve')
    dr.polygon([(8 * s, 9 * s), (29 * s, 9 * s), (26 * s, 19 * s), (10 * s, 19 * s)], fill=(204, 204, 255), outline=c)
    for x in (13, 18, 23):
        dr.line([x * s, 9 * s, x * s, 19 * s], fill=c, width=s)
    dr.line([9 * s, 14 * s, 27 * s, 14 * s], fill=c, width=s)
    dr.ellipse([10 * s, 24 * s, 14 * s, 28 * s], fill=K)
    dr.ellipse([22 * s, 24 * s, 26 * s, 28 * s], fill=K)


def ic_calendar(dr, s):
    dr.rectangle([3 * s, 5 * s, 29 * s, 29 * s], fill=W, outline=K, width=s)
    dr.rectangle([3 * s, 5 * s, 29 * s, 11 * s], fill=(204, 0, 0), outline=K, width=s)
    for i in range(1, 4):
        dr.line([(3 + i * 6.5) * s, 11 * s, (3 + i * 6.5) * s, 29 * s], fill=(153, 153, 153), width=s // 2)
    for j in range(1, 3):
        dr.line([3 * s, (11 + j * 6) * s, 29 * s, (11 + j * 6) * s], fill=(153, 153, 153), width=s // 2)
    dr.rectangle([16 * s, 17.5 * s, 22 * s, 23 * s], fill=(255, 255, 0))
    dr.ellipse([8 * s, 2 * s, 11 * s, 8 * s], outline=K, width=s)
    dr.ellipse([21 * s, 2 * s, 24 * s, 8 * s], outline=K, width=s)


def ic_news(dr, s):
    dr.polygon([(4 * s, 5 * s), (28 * s, 5 * s), (28 * s, 27 * s), (4 * s, 27 * s)], fill=W, outline=K)
    dr.rectangle([6 * s, 7 * s, 26 * s, 11 * s], fill=K)
    dr.rectangle([6 * s, 13 * s, 14 * s, 20 * s], fill=(153, 153, 153))
    for y in (13, 15, 17, 19, 22, 24):
        dr.line([16 * s, y * s, 26 * s, y * s], fill=(102, 102, 102), width=s)
    for y in (22, 24):
        dr.line([6 * s, y * s, 14 * s, y * s], fill=(102, 102, 102), width=s)


def ic_people(dr, s):
    for (x, col) in ((10, (0, 102, 204)), (22, (204, 102, 0))):
        dr.ellipse([(x - 4) * s, 5 * s, (x + 4) * s, 13 * s], fill=(255, 204, 153), outline=K, width=s // 2)
        dr.pieslice([(x - 8) * s, 14 * s, (x + 8) * s, 34 * s], 180, 360, fill=col, outline=K)
    dr.rectangle([0, 28 * s, 32 * s, 32 * s], fill=(0, 0, 0, 0))


def ic_tree(dr, s):
    dr.polygon([(0, 30 * s), (11 * s, 9 * s), (22 * s, 30 * s)], fill=(153, 153, 153))
    dr.polygon([(8 * s, 15 * s), (11 * s, 9 * s), (14 * s, 15 * s)], fill=W)
    dr.polygon([(23 * s, 3 * s), (16 * s, 16 * s), (19 * s, 16 * s), (14 * s, 24 * s), (32 * s, 24 * s), (27 * s, 16 * s), (30 * s, 16 * s)], fill=(0, 102, 51))
    dr.rectangle([21.5 * s, 24 * s, 24.5 * s, 30 * s], fill=(102, 51, 0))
    dr.line([0, 30 * s, 32 * s, 30 * s], fill=(102, 51, 0), width=s)


def ic_grid(dr, s):
    dr.rectangle([2 * s, 4 * s, 30 * s, 28 * s], fill=W, outline=K, width=s)
    dr.rectangle([2 * s, 4 * s, 30 * s, 10 * s], fill=(192, 192, 192), outline=K, width=s)
    for x in (11, 21):
        dr.line([x * s, 4 * s, x * s, 28 * s], fill=(128, 128, 128), width=s)
    for y in (16, 22):
        dr.line([2 * s, y * s, 30 * s, y * s], fill=(128, 128, 128), width=s)
    dr.rectangle([11.5 * s, 16.5 * s, 20.5 * s, 21.5 * s], fill=(0, 0, 128))


def arrow(name, up):
    w, h = 9, 9
    im, dr, s = ss_canvas(w, h, ss=8)
    if up:
        dr.polygon([(4.5 * s, 1 * s), (8.5 * s, 8 * s), (0.5 * s, 8 * s)], fill=(0, 153, 0))
    else:
        dr.polygon([(4.5 * s, 8 * s), (8.5 * s, 1 * s), (0.5 * s, 1 * s)], fill=(204, 0, 0))
    save(finish(im, w, h), name, pal=16, transparent=True, matte=K)


def star(name, on):
    w, h = 12, 12
    im, dr, s = ss_canvas(w, h, ss=8)
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = 5.8 if i % 2 == 0 else 2.4
        pts.append(((6 + r * math.cos(a)) * s, (6.3 + r * math.sin(a)) * s))
    dr.polygon(pts, fill=(255, 204, 0) if on else (204, 204, 204), outline=(153, 102, 0) if on else (153, 153, 153))
    save(finish(im, w, h), name, pal=16, transparent=True)


def product(name, kind):
    w, h = 100, 80
    im, dr, s = ss_canvas(w, h, bg=(255, 255, 255, 255))
    if kind == 'widget':
        dr.ellipse([20 * s, 52 * s, 80 * s, 68 * s], fill=(102, 102, 102))
        dr.rectangle([20 * s, 30 * s, 80 * s, 60 * s], fill=(204, 204, 204))
        dr.ellipse([20 * s, 22 * s, 80 * s, 38 * s], fill=(230, 230, 230), outline=(102, 102, 102), width=s)
        dr.ellipse([38 * s, 24 * s, 62 * s, 36 * s], fill=(0, 102, 204))
        dr.line([50 * s, 30 * s, 58 * s, 26 * s], fill=W, width=2 * s)
        dr.line([20 * s, 30 * s, 20 * s, 60 * s], fill=(102, 102, 102), width=s)
        dr.line([80 * s, 30 * s, 80 * s, 60 * s], fill=(102, 102, 102), width=s)
    elif kind == 'keyboard':
        dr.polygon([(8 * s, 50 * s), (92 * s, 50 * s), (86 * s, 30 * s), (14 * s, 30 * s)], fill=(230, 225, 210), outline=(102, 102, 102))
        for row in range(4):
            y = 32 + row * 4.5
            for k in range(14):
                x = 15 + row * 1.2 + k * 5
                dr.rectangle([x * s, y * s, (x + 3.8) * s, (y + 3.2) * s], fill=(250, 248, 240), outline=(153, 153, 153))
        dr.ellipse([70 * s, 56 * s, 84 * s, 74 * s], fill=(230, 225, 210), outline=(102, 102, 102), width=s)
        dr.line([77 * s, 56 * s, 77 * s, 63 * s], fill=(102, 102, 102), width=s)
        dr.line([77 * s, 56 * s, 77 * s, 50 * s], fill=(102, 102, 102), width=s)
    elif kind == 'office':
        dr.rectangle([12 * s, 40 * s, 52 * s, 66 * s], fill=(255, 255, 102), outline=(153, 153, 0), width=s)
        dr.rectangle([18 * s, 34 * s, 58 * s, 60 * s], fill=(255, 153, 204), outline=(153, 51, 102), width=s)
        dr.polygon([(60 * s, 66 * s), (88 * s, 20 * s), (94 * s, 24 * s), (66 * s, 70 * s)], fill=(255, 204, 0), outline=(102, 51, 0))
        dr.polygon([(60 * s, 66 * s), (66 * s, 70 * s), (58 * s, 74 * s)], fill=(255, 204, 153), outline=(102, 51, 0))
    else:   # mug
        dr.rounded_rectangle([28 * s, 18 * s, 66 * s, 70 * s], radius=4 * s, fill=NAVY)
        dr.ellipse([60 * s, 30 * s, 80 * s, 56 * s], outline=NAVY, width=5 * s)
        dr.ellipse([28 * s, 14 * s, 66 * s, 24 * s], fill=(0, 34, 102))
        globe(dr, 47 * s, 44 * s, 10 * s, s, sea=W, land=(204, 204, 255), grid=GOLD)
    save(finish(im, w, h), name, pal=64)


def banner(name, title, sub, w=468, h=60, top=(0, 51, 153), bot=(0, 102, 204), scene=None):
    im = G.vgrad(w, h, [(0, top), (1, bot)])
    dr = ImageDraw.Draw(im)
    if scene:
        scene(im, dr)
    f = G.font('sans_b', 26)
    G.text_at(dr, 82, 6, title, f, (0, 0, 0))
    G.text_at(dr, 80, 4, title, f, W)
    G.text_at(dr, 82, 38, sub, G.font('sans_i', 12), (255, 255, 204))
    save(im, name, pal=128)


def parks_scene(im, dr):
    # mountains and pines on the left
    dr.polygon([(0, 60), (30, 14), (60, 60)], fill=(102, 102, 153))
    dr.polygon([(24, 24), (30, 14), (36, 24)], fill=W)
    dr.polygon([(20, 60), (52, 22), (78, 60)], fill=(80, 80, 130))
    dr.polygon([(46, 30), (52, 22), (58, 30)], fill=W)
    for x in (8, 22, 60):
        dr.polygon([(x, 58), (x + 7, 34), (x + 14, 58)], fill=(0, 102, 51))
    dr.rectangle([0, 56, 79, 59], fill=(0, 80, 40))


def hr_scene(im, dr):
    tmp = Image.new('RGBA', (64 * 4, 64 * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    ic_people(d, 8)
    tmp = tmp.resize((56, 56), Image.LANCZOS)
    im.paste(tmp, (12, 4), tmp)


def sale_burst():
    w, h = 60, 40
    im, dr, s = ss_canvas(w, h, ss=4)
    pts = []
    for i in range(24):
        a = i * math.pi / 12
        r = (28 if i % 2 == 0 else 20)
        pts.append(((30 + r * math.cos(a)) * s, (20 + r * 0.66 * math.sin(a)) * s))
    dr.polygon(pts, fill=(255, 0, 0))
    f = G.font('sans_b', 12 * s)
    G.text_center(dr, 30 * s, 13 * s, 'SALE!', f, (255, 255, 0))
    save(finish(im, w, h), 'sale.gif', pal=16, transparent=True)


if __name__ == '__main__':
    gc_logo(); gc_small_logo()
    for i, c in enumerate([(204, 221, 238), (204, 230, 204), (238, 226, 204), (226, 214, 238)], 1):
        photo(i, c)
    icon('ic_directory.gif', ic_directory); icon('ic_forum.gif', ic_forum); icon('ic_cart.gif', ic_cart)
    icon('ic_calendar.gif', ic_calendar); icon('ic_news.gif', ic_news); icon('ic_people.gif', ic_people)
    icon('ic_parks.gif', ic_tree); icon('ic_grid.gif', ic_grid)
    arrow('up.gif', True); arrow('down.gif', False)
    star('star_on.gif', True); star('star_off.gif', False)
    for i, k in enumerate(['widget', 'keyboard', 'office', 'mug'], 1):
        product('cat_%d.gif' % i, k)
    banner('parks_banner.gif', 'National Parks Finder', 'Browse park units by state - a KoldFusion drill-down example',
           top=(0, 85, 51), bot=(102, 153, 102), scene=parks_scene)
    sale_burst()
    print('wrote', len(G.MANIFEST), 'images to', OUT)
