#!/usr/bin/env python3
"""
mkgraphics.py -- procedurally generate every GIF used by KoldFusion.

KoldFusion by <gibson> is a nostalgic tribute to a certain 1999 web
application server.  All artwork here is drawn from scratch with Pillow
(no downloads, no copied logos): emblem, wordmarks, nav bars, 16x16
icons and a pile of peak-1999 "web page" decorations (88x31 buttons,
under-construction signs, flaming strips, spinning globes, ...).

Usage:   python3 tools/mkgraphics.py [--sheet /path/contact_sheet.png]

Requires Pillow (tested with 12.x).  Fonts: Liberation Sans / Mono are
preferred (metric-compatible with Arial / Courier New), falling back to
DejaVu and finally to Pillow's built-in font.
"""
import colorsys
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ADMIN_DIR = os.path.join(ROOT, 'wwwroot', 'CFIDE', 'administrator', 'images')
DEMO_DIR = os.path.join(ROOT, 'wwwroot', 'images')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NAVY = (0, 51, 153)          # #003399 - the classic admin header blue
SAGE = (153, 204, 153)       # #99CC99 - nav panel green

# --------------------------------------------------------------------------
# fonts
# --------------------------------------------------------------------------
FONT_DIRS = ['/usr/share/fonts', '/usr/local/share/fonts',
             os.path.expanduser('~/.local/share/fonts'), os.path.expanduser('~/.fonts'),
             '/Library/Fonts', '/System/Library/Fonts', 'C:/Windows/Fonts']

FONT_CANDIDATES = {
    'sans':     ['LiberationSans-Regular.ttf', 'Arial.ttf', 'arial.ttf', 'DejaVuSans.ttf'],
    'sans_b':   ['LiberationSans-Bold.ttf', 'Arial Bold.ttf', 'arialbd.ttf', 'DejaVuSans-Bold.ttf'],
    'sans_bi':  ['LiberationSans-BoldItalic.ttf', 'arialbi.ttf', 'DejaVuSans-BoldOblique.ttf',
                 'DejaVuSans-Bold.ttf'],
    'sans_i':   ['LiberationSans-Italic.ttf', 'ariali.ttf', 'DejaVuSans-Oblique.ttf', 'DejaVuSans.ttf'],
    'narrow_b': ['LiberationSansNarrow-Bold.ttf', 'DejaVuSansCondensed-Bold.ttf',
                 'LiberationSans-Bold.ttf', 'DejaVuSans-Bold.ttf'],
    'mono':     ['LiberationMono-Regular.ttf', 'cour.ttf', 'DejaVuSansMono.ttf'],
    'mono_b':   ['LiberationMono-Bold.ttf', 'courbd.ttf', 'DejaVuSansMono-Bold.ttf'],
}

_font_index = None
_font_cache = {}


def _index_fonts():
    global _font_index
    if _font_index is None:
        _font_index = {}
        for d in FONT_DIRS:
            if not os.path.isdir(d):
                continue
            for dp, _dn, fns in os.walk(d):
                for fn in fns:
                    if fn.lower().endswith(('.ttf', '.otf')):
                        _font_index.setdefault(fn.lower(), os.path.join(dp, fn))
    return _font_index


def font(key, size):
    ck = (key, size)
    if ck in _font_cache:
        return _font_cache[ck]
    idx = _index_fonts()
    f = None
    for name in FONT_CANDIDATES[key]:
        p = idx.get(name.lower())
        if p:
            try:
                f = ImageFont.truetype(p, size)
                break
            except OSError:
                pass
    if f is None:
        sys.stderr.write('warning: no TTF for %s, using Pillow default font\n' % key)
        f = ImageFont.load_default(size=size)
    _font_cache[ck] = f
    return f


def tbox(f, text):
    """(x0, y0, x1, y1) ink box of text drawn at origin."""
    return f.getbbox(text)


def tsize(f, text):
    b = f.getbbox(text)
    return b[2] - b[0], b[3] - b[1]


def text_at(dr, x, y, text, f, fill, **kw):
    """Draw text so that its *ink* top-left lands on (x, y)."""
    b = f.getbbox(text)
    dr.text((x - b[0], y - b[1]), text, font=f, fill=fill, **kw)


def text_center(dr, cx, y, text, f, fill, **kw):
    w, _ = tsize(f, text)
    text_at(dr, int(round(cx - w / 2.0)), y, text, f, fill, **kw)


def fit_font(key, text, max_w, max_h=None, start=48, minimum=6):
    for s in range(start, minimum - 1, -1):
        f = font(key, s)
        w, h = tsize(f, text)
        if w <= max_w and (max_h is None or h <= max_h):
            return f
    return font(key, minimum)


def aliased(dr):
    """1999 small text: no anti-aliasing."""
    dr.fontmode = '1'
    return dr


# --------------------------------------------------------------------------
# colour helpers
# --------------------------------------------------------------------------
def hexc(s):
    s = s.lstrip('#')
    if len(s) == 3:
        s = ''.join(c * 2 for c in s)
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


def ramp(stops, t):
    """stops: [(pos, colour), ...] sorted by pos."""
    if t <= stops[0][0]:
        return stops[0][1]
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if t <= p1:
            return lerp(c0, c1, (t - p0) / float(p1 - p0) if p1 > p0 else 0)
    return stops[-1][1]


def vgrad(w, h, stops, alpha=255):
    im = Image.new('RGBA', (w, h))
    dr = ImageDraw.Draw(im)
    for y in range(h):
        c = ramp(stops, y / float(max(1, h - 1)))
        dr.line([(0, y), (w - 1, y)], fill=c + (alpha,))
    return im


def hgrad(w, h, stops, alpha=255):
    im = Image.new('RGBA', (w, h))
    dr = ImageDraw.Draw(im)
    for x in range(w):
        c = ramp(stops, x / float(max(1, w - 1)))
        dr.line([(x, 0), (x, h - 1)], fill=c + (alpha,))
    return im


def down(im, size):
    """Supersample-down an RGBA image with premultiplied alpha."""
    return im.convert('RGBa').resize(size, Image.LANCZOS).convert('RGBA')


def blank(w, h, c=(0, 0, 0, 0)):
    return Image.new('RGBA', (w, h), c)


def over(base, top, xy=(0, 0)):
    base.alpha_composite(top, dest=(int(xy[0]), int(xy[1])))
    return base


# --------------------------------------------------------------------------
# palette / GIF writing
# --------------------------------------------------------------------------
WEB216 = [(r, g, b) for r in range(0, 256, 51) for g in range(0, 256, 51) for b in range(0, 256, 51)]

_near_cache = {}


def _nearest(c, palette, pkey):
    k = (pkey, c)
    v = _near_cache.get(k)
    if v is not None:
        return v
    r, g, b = c
    best, bi = 1 << 30, 0
    for i, (pr, pg, pb) in enumerate(palette):
        d = 2 * (r - pr) ** 2 + 4 * (g - pg) ** 2 + 3 * (b - pb) ** 2
        if d < best:
            best, bi = d, i
            if d == 0:
                break
    _near_cache[k] = bi
    return bi


def _pixels(im):
    f = getattr(im, 'get_flattened_data', None)
    return f() if f else im.getdata()


def _flatten(rgba, matte):
    rgba = rgba.convert('RGBA')
    bg = Image.new('RGBA', rgba.size, tuple(matte) + (255,))
    bg.alpha_composite(rgba)
    return bg.convert('RGB'), rgba.getchannel('A')


def _adaptive_palette(rgbs, masks, n):
    """Median-cut palette shared across all frames (opaque pixels only)."""
    w = sum(i.width for i in rgbs)
    h = max(i.height for i in rgbs)
    mont = Image.new('RGB', (w, h))
    x = 0
    for im, m in zip(rgbs, masks):
        src = im
        if m is not None:  # replace transparent pixels by an opaque neighbour colour
            src = im.copy()
            ref = None
            for px, a in zip(_pixels(im), _pixels(m)):
                if not a:
                    ref = px
                    break
            if ref is not None:
                src.paste(ref, mask=m)
        mont.paste(src, (x, 0))
        x += im.width
    q = mont.quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = q.getpalette()
    used = sorted(i for _c, i in q.getcolors(1 << 16))
    out = []
    for i in used:
        c = tuple(pal[i * 3:i * 3 + 3])
        if c not in out:
            out.append(c)
    return out


def _to_p(rgb, palette, pkey, tmask, tcolor):
    cols = rgb.getcolors(rgb.width * rgb.height)
    lut = {c: _nearest(c, palette, pkey) for _n, c in cols}
    p = Image.new('P', rgb.size)
    p.putdata([lut[c] for c in _pixels(rgb)])
    flat = [v for c in palette for v in c]
    tidx = None
    if tmask is not None:
        tidx = len(palette)
        flat += list(tcolor)
        p.paste(tidx, (0, 0, rgb.width, rgb.height), tmask)
    flat += [0] * (768 - len(flat))
    p.putpalette(flat)
    return p, tidx


MANIFEST = []   # (path, description)


def save_gif(frames, path, pal='web', matte=WHITE, transparent=False, durations=100,
             desc='', alpha_cut=128, loop=0):
    """frames: RGBA image or list of them.
    pal: 'web' (216 web-safe), int (adaptive N colours shared by all frames),
         or an explicit list of RGB tuples."""
    if isinstance(frames, Image.Image):
        frames = [frames]
    rgbs, masks = [], []
    for fr in frames:
        rgb, a = _flatten(fr, matte)
        rgbs.append(rgb)
        masks.append(a.point(lambda v: 255 if v < alpha_cut else 0) if transparent else None)
    if masks[0] is not None and not any(m.getbbox() for m in masks):
        masks = [None] * len(masks)     # nothing actually transparent
    if pal == 'web':
        palette, pkey = WEB216, 'web'
    elif isinstance(pal, int):
        palette = _adaptive_palette(rgbs, masks, min(pal, 255))
        pkey = tuple(palette)
    else:
        palette, pkey = list(pal), tuple(pal)
    pims = []
    tidx = None
    for rgb, m in zip(rgbs, masks):
        p, tidx = _to_p(rgb, palette, pkey, m, matte)
        pims.append(p)
    # compact the palette to the colours actually used (smaller files, like a
    # 1999 "exact palette" export), keeping the transparent index consistent
    used = sorted(set(i for p in pims for _n, i in p.getcolors(256)))
    if tidx is not None and tidx not in used:
        used.append(tidx)
    pims = [p.remap_palette(used) for p in pims]
    if tidx is not None:
        tidx = used.index(tidx)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    kw = {}
    if tidx is not None:
        kw['transparency'] = tidx
    if len(pims) == 1:
        pims[0].save(path, 'GIF', optimize=False, **kw)
    else:
        if isinstance(durations, int):
            durations = [durations] * len(pims)
        pims[0].save(path, 'GIF', save_all=True, append_images=pims[1:], duration=durations,
                     loop=loop, disposal=2 if tidx is not None else 1, optimize=False, **kw)
    MANIFEST.append((path, desc))
    return path


# --------------------------------------------------------------------------
# shared artwork: the "Kold" emblem and heavy logo lettering
# --------------------------------------------------------------------------
BOLT = [(0.64, 0.02), (0.82, 0.02), (0.61, 0.41), (0.76, 0.41), (0.28, 0.98),
        (0.43, 0.54), (0.28, 0.54)]


def emblem(d, ss=8):
    """Original emblem: green disc, white ice crystal, yellow lightning bolt."""
    S = d * ss
    im = blank(S, S)
    dr = ImageDraw.Draw(im)
    cx = cy = S / 2.0
    # dark rim
    dr.ellipse([0, 0, S - 1, S - 1], fill=(0, 51, 0, 255))
    # glossy green inner disc (offset radial gradient)
    r0 = S * 0.455
    steps = 48
    for i in range(steps):
        t = i / float(steps - 1)
        r = r0 * (1 - 0.88 * t)
        off = (r0 - r) * 0.42
        col = ramp([(0, (0, 102, 0)), (0.55, (0, 170, 51)), (1, (170, 255, 150))], t ** 0.9)
        dr.ellipse([cx - off - r, cy - off - r, cx - off + r, cy - off + r], fill=col + (255,))
    dr.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], outline=(204, 255, 204, 255),
               width=max(1, int(S * 0.018)))

    # ice crystal: draw once dark+wide (outline) then white
    def flake(col, extra):
        R = S * 0.335
        lw = S * 0.062 + extra
        for k in range(6):
            a = math.pi / 2 + k * math.pi / 3
            tip = (cx + R * math.cos(a), cy - R * math.sin(a))
            dr.line([(cx, cy), tip], fill=col, width=int(lw))
            dr.ellipse([tip[0] - lw / 2, tip[1] - lw / 2, tip[0] + lw / 2, tip[1] + lw / 2], fill=col)
            for f, bl in ((0.48, 0.15), (0.76, 0.10)):
                bx, by = cx + f * R * math.cos(a), cy - f * R * math.sin(a)
                for s in (1, -1):
                    ba = a + s * math.pi / 3.2
                    ex, ey = bx + bl * S * math.cos(ba), by - bl * S * math.sin(ba)
                    dr.line([(bx, by), (ex, ey)], fill=col, width=int(lw * 0.8))
                    q = lw * 0.4
                    dr.ellipse([ex - q, ey - q, ex + q, ey + q], fill=col)
        hr = S * 0.075 + extra / 2
        dr.regular_polygon((cx, cy, hr), 6, rotation=30, fill=col)

    flake((0, 51, 0, 255), S * 0.035)
    flake((255, 255, 255, 255), 0)

    # lightning bolt with vertical gradient fill and dark outline
    pts = [(x * S, y * S) for x, y in BOLT]
    sh = [(x + S * 0.03, y + S * 0.03) for x, y in pts]
    dr.polygon(sh, fill=(0, 0, 0, 110))
    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).polygon(pts, fill=255)
    g = vgrad(S, S, [(0, (255, 255, 153)), (0.45, (255, 204, 0)), (1, (255, 102, 0))])
    im.paste(g, (0, 0), mask)
    dr.polygon(pts, outline=(51, 26, 0, 255), width=max(2, int(S * 0.028)))
    return down(im, (d, d))


def heavy_text(text, w, h, top=(102, 221, 51), bot=(0, 128, 0), outline=(0, 51, 0),
               shadow=(80, 80, 80), o=1, sh=(1, 1), fontkey='sans_b', ss=4):
    """Big heavy lettering stretched into a w x h box, gradient fill, outline, drop shadow."""
    S = ss
    W, H = w * S, h * S
    iw, ih = W - 2 * o * S - sh[0] * S, H - 2 * o * S - sh[1] * S
    f = font(fontkey, 160)
    b = f.getbbox(text)
    m = Image.new('L', (b[2] - b[0] + 8, b[3] - b[1] + 8), 0)
    ImageDraw.Draw(m).text((4 - b[0], 4 - b[1]), text, font=f, fill=255)
    m = m.crop(m.getbbox()).resize((iw, ih), Image.LANCZOS)
    tm = Image.new('L', (W, H), 0)
    tm.paste(m, (o * S, o * S))
    om = tm
    if o:
        om = tm.filter(ImageFilter.MaxFilter(2 * o * S + 1))
    sm = ImageChops.offset(om, sh[0] * S, sh[1] * S)
    out = blank(W, H)
    if sh != (0, 0):
        out.paste(Image.new('RGBA', (W, H), shadow + (255,)), (0, 0), sm)
    out.paste(Image.new('RGBA', (W, H), outline + (255,)), (0, 0), om)
    out.paste(vgrad(W, H, [(0, top), (1, bot)]), (0, 0), tm)
    return down(out, (w, h))


def gibson_wordmark(dr, x, y, size, col=(153, 153, 153), bracket=None, key='mono'):
    """The "<gibson>" wordmark (light monospace, angle brackets)."""
    f = font(key, size)
    bracket = bracket or col
    text_at(dr, x, y, '<', f, bracket)
    wl = f.getlength('<')
    dr.text((x + wl - f.getbbox('<')[0], y - f.getbbox('<')[1]), 'gibson', font=f, fill=col)
    wa = f.getlength('gibson')
    dr.text((x + wl + wa - f.getbbox('<')[0], y - f.getbbox('<')[1]), '>', font=f, fill=bracket)
    return f.getlength('<gibson>')


def bevel(dr, w, h, light=(255, 255, 255), dark=(102, 102, 102), border=(0, 0, 0)):
    if border is not None:
        dr.rectangle([0, 0, w - 1, h - 1], outline=border)
        x0, y0, x1, y1 = 1, 1, w - 2, h - 2
    else:
        x0, y0, x1, y1 = 0, 0, w - 1, h - 1
    dr.line([(x0, y1), (x0, y0), (x1, y0)], fill=light)
    dr.line([(x0 + 1, y1), (x1, y1), (x1, y0 + 1)], fill=dark)


def starfield(im, n, rng, colours=((102, 102, 102), (153, 153, 153), (204, 204, 204), (255, 255, 255))):
    w, h = im.size
    px = im.load()
    for _ in range(n):
        x, y = rng.randrange(w), rng.randrange(h)
        c = rng.choice(colours)
        px[x, y] = c + (255,) if len(px[x, y]) == 4 else c


# --------------------------------------------------------------------------
# administrator images
# --------------------------------------------------------------------------
def make_logos():
    # kf_logo.gif 200x70
    W, H = 200, 70
    im = blank(W, H, WHITE + (255,))
    dr = ImageDraw.Draw(im)
    em = emblem(54)
    over(im, em, (3, 12))
    gibson_wordmark(dr, 62, 6, 14)
    ht = heavy_text('KOLDFUSION', 134, 27)
    over(im, ht, (61, 27))
    dr2 = aliased(ImageDraw.Draw(im))
    text_at(dr2, 62, 58, 'Server 4.5', font('sans_b', 9), (0, 51, 0))
    save_gif(im, os.path.join(ADMIN_DIR, 'kf_logo.gif'), pal=64,
             desc='Main admin logo: "<gibson>" wordmark, ice-crystal/bolt emblem, heavy green KOLDFUSION')

    # kf_logo_small.gif 120x40
    W, H = 120, 40
    im = blank(W, H, WHITE + (255,))
    dr = ImageDraw.Draw(im)
    over(im, emblem(32), (2, 5))
    aliased(dr)
    gibson_wordmark(dr, 38, 3, 10)
    over(im, heavy_text('KOLDFUSION', 80, 17, o=1, sh=(1, 1)), (37, 17))
    save_gif(im, os.path.join(ADMIN_DIR, 'kf_logo_small.gif'), pal=48,
             desc='Compact header logo (emblem + wordmark + KOLDFUSION)')

    # login_banner.gif 400x80
    W, H = 400, 80
    im = blank(W, H, WHITE + (255,))
    dr = ImageDraw.Draw(im)
    over(im, emblem(66), (8, 6))
    gibson_wordmark(dr, 86, 5, 15)
    over(im, heavy_text('KOLDFUSION', 196, 31, o=1, sh=(2, 2)), (84, 24))
    f = fit_font('sans_bi', 'Administrator', 400 - 288 - 6, start=22)
    text_at(dr, 288, 38, 'Administrator', f, NAVY)
    text_at(dr, 86, 61, 'Server version 4.5   \u00b7   please log in to continue',
            font('sans', 11), (102, 102, 102))
    # sage + navy rules at the bottom
    dr.rectangle([0, H - 5, W - 1, H - 3], fill=SAGE)
    dr.line([(0, H - 2), (W - 1, H - 2)], fill=NAVY)
    save_gif(im, os.path.join(ADMIN_DIR, 'login_banner.gif'), pal=96,
             desc='"KoldFusion Administrator" login banner with emblem')


def make_nav():
    # nav_gutter.gif: seamless 28x32 tile of blue/cyan diagonal stripes
    W, H = 28, 32
    ramp8 = [hexc(c) for c in ('99CCFF', '66CCFF', '3399FF', '3366CC',
                               '003399', '003399', '3366CC', '3399CC')]
    im = blank(W, H)
    px = im.load()
    rng = random.Random(28)
    for y in range(H):
        for x in range(W):
            c = ramp8[(2 * x + y) % 8]
            r = rng.random()
            if r < 0.06:
                c = lerp(c, (255, 255, 255), 0.35)
            elif r < 0.12:
                c = lerp(c, (0, 0, 51), 0.35)
            px[x, y] = c + (255,)
    save_gif(im, os.path.join(ADMIN_DIR, 'nav_gutter.gif'), pal='web',
             desc='Seamless tile for the left nav gutter (blue/cyan diagonal stripes)')

    # section headers
    names = [('server', 'server'), ('datasources', 'datasources'), ('extensions', 'extensions'),
             ('logging', 'logging'), ('automated', 'automated tasks'),
             ('miscellaneous', 'miscellaneous'), ('security', 'security'), ('tools', 'tools')]
    f = font('sans_b', 12)
    for fn, label in names:
        im = blank(115, 20, NAVY + (255,))
        dr = ImageDraw.Draw(im)
        _, th = tsize(f, 'dg')
        b = f.getbbox('dg')
        dr.text((5, (20 - th) // 2 - b[1]), label, font=f, fill=WHITE)
        save_gif(im, os.path.join(ADMIN_DIR, 'nav_hdr_%s.gif' % fn), pal='web',
                 desc='Nav section header bar "%s"' % label)

    # spacer.gif - the classic
    save_gif(blank(1, 1), os.path.join(ADMIN_DIR, 'spacer.gif'), transparent=True,
             desc='1x1 transparent spacer')

    # bar_blue / bar_green: 1x10 bevelled bar-chart segments
    blue = ['99CCFF', '6699FF', '3366FF', '3366FF', '0033FF', '0033CC', '0033CC', '003399', '003399', '000066']
    green = ['CCFFCC', '99FF99', '66CC66', '33CC33', '33CC33', '009933', '009900', '006600', '006600', '003300']
    for nm, cols in (('blue', blue), ('green', green)):
        im = blank(1, 10)
        for y, c in enumerate(cols):
            im.putpixel((0, y), hexc(c) + (255,))
        save_gif(im, os.path.join(ADMIN_DIR, 'bar_%s.gif' % nm), pal='web',
                 desc='1x10 %s bar-chart segment (stretch with WIDTH=)' % nm)


def icon_canvas(ss=8):
    return blank(16 * ss, 16 * ss), ss


def make_icons():
    out = ADMIN_DIR
    # --- check
    im, s = icon_canvas()
    dr = ImageDraw.Draw(im)
    pts = [(2.2 * s, 8.6 * s), (6 * s, 12.6 * s), (14 * s, 3.2 * s)]
    dr.line(pts, fill=(0, 51, 0, 255), width=int(4.4 * s), joint='curve')
    for p in (pts[0], pts[2]):
        dr.ellipse([p[0] - 2.2 * s, p[1] - 2.2 * s, p[0] + 2.2 * s, p[1] + 2.2 * s], fill=(0, 51, 0, 255))
    dr.line(pts, fill=(0, 170, 0, 255), width=int(2.4 * s), joint='curve')
    dr.line([(p[0] - 0.4 * s, p[1] - 0.6 * s) for p in pts], fill=(102, 255, 102, 255), width=int(0.8 * s))
    save_gif(down(im, (16, 16)), os.path.join(out, 'check.gif'), transparent=True,
             desc='Green check mark (OK / verified)')

    # --- x
    im, s = icon_canvas()
    dr = ImageDraw.Draw(im)
    a, b = 3.2 * s, 12.8 * s
    for w, c in ((int(4.6 * s), (102, 0, 0, 255)), (int(2.6 * s), (221, 0, 0, 255))):
        dr.line([(a, a), (b, b)], fill=c, width=w)
        dr.line([(a, b), (b, a)], fill=c, width=w)
    dr.line([(a + 0.3 * s, a - 0.5 * s), (b - 0.6 * s, b - 1.4 * s)], fill=(255, 102, 102, 255), width=int(0.7 * s))
    save_gif(down(im, (16, 16)), os.path.join(out, 'x.gif'), transparent=True,
             desc='Red X (failed / delete)')

    # --- warn
    im, s = icon_canvas()
    dr = ImageDraw.Draw(im)
    tri = [(8 * s, 0.8 * s), (15.4 * s, 14.6 * s), (0.6 * s, 14.6 * s)]
    dr.polygon(tri, fill=(255, 204, 0, 255), outline=(0, 0, 0, 255), width=int(1.1 * s))
    dr.rectangle([7 * s, 5 * s, 9 * s - 1, 10.4 * s], fill=(0, 0, 0, 255))
    dr.rectangle([7 * s, 11.6 * s, 9 * s - 1, 13.4 * s], fill=(0, 0, 0, 255))
    save_gif(down(im, (16, 16)), os.path.join(out, 'warn.gif'), transparent=True,
             desc='Yellow warning triangle')

    # --- help
    im, s = icon_canvas()
    dr = ImageDraw.Draw(im)
    dr.ellipse([0.5 * s, 0.5 * s, 15.5 * s, 15.5 * s], fill=(0, 0, 102, 255))
    dr.ellipse([1.5 * s, 1.5 * s, 14.5 * s, 14.5 * s], fill=(0, 51, 204, 255))
    dr.ellipse([3 * s, 2.2 * s, 10 * s, 7 * s], fill=(102, 153, 255, 255))
    f = font('sans_b', 12 * s)
    text_center(dr, 8 * s, 3.2 * s, '?', f, (255, 255, 255, 255))
    save_gif(down(im, (16, 16)), os.path.join(out, 'help.gif'), transparent=True,
             desc='Blue help "?" button')

    # --- folder (pixel art, Win95-ish)
    im = blank(16, 16)
    dr = ImageDraw.Draw(im)
    ol = (102, 51, 0, 255)
    dr.polygon([(1, 3), (6, 3), (7, 4), (14, 4), (14, 13), (1, 13)], fill=(204, 153, 0, 255), outline=ol)
    dr.polygon([(1, 13), (3, 6), (15, 6), (13, 13)], fill=(255, 204, 51, 255), outline=ol)
    dr.line([(4, 7), (14, 7)], fill=(255, 255, 153, 255))
    dr.line([(2, 4), (5, 4)], fill=(255, 255, 153, 255))
    save_gif(im, os.path.join(out, 'folder.gif'), transparent=True, desc='Yellow folder')

    # --- file (log page with dog-ear)
    im = blank(16, 16)
    dr = ImageDraw.Draw(im)
    dr.polygon([(2, 0), (10, 0), (13, 3), (13, 15), (2, 15)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
    dr.polygon([(10, 0), (10, 3), (13, 3)], fill=(204, 204, 204, 255), outline=(0, 0, 0, 255))
    for i, y in enumerate((5, 7, 9, 11, 13)):
        x1 = (11, 10, 11, 8, 10)[i]
        dr.line([(4, y), (x1, y)], fill=(102, 102, 153, 255))
    dr.line([(4, 3), (7, 3)], fill=(0, 51, 153, 255))
    save_gif(im, os.path.join(out, 'file.gif'), transparent=True, desc='Log/text file page')

    # --- arrow bullet
    im, s = icon_canvas()
    dr = ImageDraw.Draw(im)
    dr.polygon([(4.5 * s, 2.5 * s), (12.5 * s, 8 * s), (4.5 * s, 13.5 * s)], fill=(0, 0, 102, 255))
    dr.polygon([(5.6 * s, 4.4 * s), (10.6 * s, 8 * s), (5.6 * s, 11.6 * s)], fill=(0, 51, 204, 255))
    dr.polygon([(5.6 * s, 4.4 * s), (10.6 * s, 8 * s), (5.6 * s, 8 * s)], fill=(51, 102, 255, 255))
    save_gif(down(im, (16, 16)), os.path.join(out, 'arrow.gif'), transparent=True,
             desc='Small blue right-pointing triangle bullet')

    # --- lock
    im, s = icon_canvas()
    dr = ImageDraw.Draw(im)
    dr.arc([4 * s, 1 * s, 12 * s, 11 * s], 180, 360, fill=(51, 51, 51, 255), width=int(2.4 * s))
    dr.line([(4.6 * s, 6 * s), (4.6 * s, 8 * s)], fill=(51, 51, 51, 255), width=int(2.2 * s))
    dr.line([(11.4 * s, 6 * s), (11.4 * s, 8 * s)], fill=(51, 51, 51, 255), width=int(2.2 * s))
    dr.arc([4.6 * s, 1.6 * s, 11.4 * s, 10.4 * s], 200, 300, fill=(204, 204, 204, 255), width=int(0.8 * s))
    dr.rounded_rectangle([2 * s, 7 * s, 14 * s, 15.4 * s], radius=1.2 * s, fill=(153, 102, 0, 255))
    body = vgrad(int(10.4 * s), int(6.8 * s), [(0, (255, 255, 102)), (0.5, (255, 204, 0)), (1, (204, 153, 0))])
    over(im, body, (2.8 * s, 7.8 * s))
    dr.ellipse([6.8 * s, 9.2 * s, 9.2 * s, 11.6 * s], fill=(51, 26, 0, 255))
    dr.polygon([(7.4 * s, 11 * s), (8.6 * s, 11 * s), (8.9 * s, 13.6 * s), (7.1 * s, 13.6 * s)], fill=(51, 26, 0, 255))
    save_gif(down(im, (16, 16)), os.path.join(out, 'lock.gif'), transparent=True, desc='Gold padlock (security)')

    # --- db cylinder
    im, s = icon_canvas()
    dr = ImageDraw.Draw(im)
    x0, x1 = 2 * s, 14 * s
    ol = (0, 0, 102, 255)
    dr.rectangle([x0, 3.5 * s, x1, 12.5 * s], fill=ol)
    dr.ellipse([x0, 10 * s, x1, 15 * s], fill=ol)
    body = hgrad(int(11 * s), int(10 * s), [(0, (51, 102, 204)), (0.35, (153, 204, 255)), (1, (0, 51, 153))])
    bm = Image.new('L', body.size, 0)
    bd = ImageDraw.Draw(bm)
    bd.rectangle([0, 0, body.width, 6.5 * s], fill=255)
    bd.ellipse([0, 4 * s, body.width - 1, 9 * s], fill=255)
    im.paste(body, (int(2.5 * s), int(4 * s)), bm)
    for yy in (6.6, 9.4):
        dr.arc([x0, (yy - 2.5) * s, x1, (yy + 2.5) * s], 0, 180, fill=ol, width=int(0.7 * s))
    dr.ellipse([x0, 1 * s, x1, 6 * s], fill=ol)
    dr.ellipse([x0 + 0.8 * s, 1.7 * s, x1 - 0.8 * s, 5.3 * s], fill=(204, 230, 255, 255))
    save_gif(down(im, (16, 16)), os.path.join(out, 'db.gif'), transparent=True,
             desc='Database cylinder (datasources)')


# --------------------------------------------------------------------------
# demo / example page images (peak 1999)
# --------------------------------------------------------------------------
def make_buttons():
    out = DEMO_DIR
    # powered_by_kf.gif 88x31
    im = vgrad(88, 31, [(0, (0, 0, 51)), (1, (0, 51, 153))])
    dr = ImageDraw.Draw(im)
    bevel(dr, 88, 31, light=(102, 153, 255), dark=(0, 0, 51))
    over(im, emblem(25), (3, 3))
    aliased(dr)
    f1 = font('sans', 9)
    text_at(dr, 31, 4, 'Powered by', f1, (204, 204, 204))
    ht = heavy_text('KoldFusion', 54, 15, top=(153, 255, 102), bot=(0, 204, 51), outline=(0, 51, 0),
                    shadow=(0, 0, 0), o=1, sh=(1, 1))
    over(im, ht, (30, 13))
    save_gif(im, os.path.join(out, 'powered_by_kf.gif'), pal=64,
             desc='88x31 "Powered by KoldFusion" button')

    # gibson_88x31.gif
    im = blank(88, 31, WHITE + (255,))
    dr = ImageDraw.Draw(im)
    dr.rectangle([1, 21, 86, 29], fill=SAGE)
    bevel(dr, 88, 31, light=(255, 255, 255), dark=(153, 153, 153))
    f = font('mono_b', 15)
    w = f.getlength('<gibson>')
    gibson_wordmark(dr, int((88 - w) / 2), 4, 15, col=(51, 51, 51), bracket=(153, 153, 153), key='mono_b')
    aliased(dr)
    text_center(dr, 44, 22, 'gibson.example', font('sans_b', 9), NAVY)
    save_gif(im, os.path.join(out, 'gibson_88x31.gif'), pal='web',
             desc='88x31 "<gibson>" company button')

    # netscape_now.gif -> generic "Best viewed with Navigator 4.x"
    im = vgrad(88, 31, [(0, (0, 0, 0)), (1, (0, 0, 102))])
    rng = random.Random(4)
    starfield(im, 40, rng)
    dr = ImageDraw.Draw(im)
    bevel(dr, 88, 31, light=(102, 102, 153), dark=(0, 0, 0), border=(0, 0, 0))
    # compass rose (not anybody's logo)
    S = 8
    cr = blank(26 * S, 26 * S)
    cd = ImageDraw.Draw(cr)
    c = 13 * S
    cd.ellipse([2 * S, 2 * S, 24 * S, 24 * S], outline=(102, 204, 255, 255), width=S)
    for k in range(8):
        a = k * math.pi / 4
        L = (11.8 if k % 2 == 0 else 7.5) * S
        wdt = (2.6 if k % 2 == 0 else 1.8) * S
        tip = (c + L * math.sin(a), c - L * math.cos(a))
        l1 = (c + wdt * math.sin(a - math.pi / 2), c - wdt * math.cos(a - math.pi / 2))
        l2 = (c + wdt * math.sin(a + math.pi / 2), c - wdt * math.cos(a + math.pi / 2))
        cd.polygon([tip, l1, (c, c)], fill=(255, 255, 255, 255) if k % 2 == 0 else (153, 204, 255, 255))
        cd.polygon([tip, l2, (c, c)], fill=(51, 153, 204, 255) if k % 2 == 0 else (0, 102, 204, 255))
    cd.ellipse([c - 1.5 * S, c - 1.5 * S, c + 1.5 * S, c + 1.5 * S], fill=(255, 204, 0, 255))
    over(im, down(cr, (26, 26)), (2, 3))
    aliased(dr)
    text_at(dr, 30, 3, 'Best viewed', font('sans', 9), (204, 204, 204))
    fN = fit_font('sans_b', 'Navigator', 55, start=13)
    text_at(dr, 30, 12, 'Navigator', fN, (255, 255, 255))
    f9 = font('sans_b', 9)
    text_at(dr, 30, 23, '4.x', f9, (255, 204, 0))
    text_at(dr, 30 + tsize(f9, '4.x')[0] + 4, 23, 'NOW!', f9, (102, 204, 255))
    save_gif(im, os.path.join(out, 'netscape_now.gif'), pal=64,
             desc='88x31 "Best viewed with Navigator 4.x" (generic compass, no real logos)')

    # ie_parody.gif "Best viewed with ANY browser"
    im = blank(88, 31, WHITE + (255,))
    dr = ImageDraw.Draw(im)
    dr.rectangle([0, 0, 87, 30], outline=(0, 0, 0))
    dr.rectangle([2, 2, 85, 28], outline=(204, 204, 204))
    aliased(dr)
    text_center(dr, 44, 4, 'Best viewed with', font('sans', 9), (0, 0, 0))
    fa = font('sans_b', 15)
    fb = font('sans_b', 11)
    wa = sum(fa.getlength(ch) for ch in 'ANY')
    wb = fb.getlength(' browser')
    x = int((88 - wa - wb) / 2)
    base = 27
    for ch, col in zip('ANY', ((204, 0, 0), (0, 153, 0), (0, 51, 204))):
        dr.text((x, base), ch, font=fa, fill=col, anchor='ls')
        x += fa.getlength(ch)
    dr.text((x, base), ' browser', font=fb, fill=(0, 0, 0), anchor='ls')
    save_gif(im, os.path.join(out, 'ie_parody.gif'), pal='web',
             desc='88x31 "Best viewed with ANY browser" campaign button')

    # webring.gif
    W, H = 300, 40
    im = blank(W, H, (204, 204, 204, 255))
    dr = ImageDraw.Draw(im)
    bevel(dr, W, H, light=(255, 255, 255), dark=(102, 102, 102))
    for bx, label in ((5, '<< Prev'), (W - 65, 'Next >>')):
        dr.rectangle([bx, 8, bx + 59, 31], fill=(204, 204, 204), outline=(0, 0, 0))
        dr.line([(bx + 1, 30), (bx + 1, 9), (bx + 58, 9)], fill=(255, 255, 255))
        dr.line([(bx + 2, 30), (bx + 58, 30), (bx + 58, 10)], fill=(128, 128, 128))
        fb = font('sans_b', 11)
        tw, th = tsize(fb, label)
        text_at(dr, bx + 30 - tw // 2, 20 - th // 2, label, fb, NAVY)
    over(im, emblem(24), (70, 8))
    ft = fit_font('sans_b', 'KoldFusion WebRing', W - 70 - 98, start=14)
    text_at(dr, 98, 8, 'KoldFusion WebRing', ft, NAVY)
    aliased(dr)
    text_at(dr, 100, 25, '[ Random | List Sites | Join ]', font('sans', 9), (0, 0, 204))
    save_gif(im, os.path.join(out, 'webring.gif'), pal=64,
             desc='"KoldFusion WebRing" navigation bar (prev / next / random)')


def make_animated():
    out = DEMO_DIR
    # ---------------- construction.gif ----------------
    W, H = 140, 50
    frames = []
    yel = (255, 204, 0)
    for fi in range(4):
        im = blank(W, H, yel + (255,))
        px = im.load()
        shift = fi * 3
        for y in list(range(0, 8)) + list(range(H - 8, H)):
            for x in range(W):
                px[x, y] = (0, 0, 0, 255) if ((x + y + shift) % 12) < 6 else yel + (255,)
        dr = ImageDraw.Draw(im)
        dr.line([(0, 8), (W - 1, 8)], fill=(0, 0, 0))
        dr.line([(0, H - 9), (W - 1, H - 9)], fill=(0, 0, 0))
        dr.rectangle([0, 0, W - 1, H - 1], outline=(0, 0, 0))
        # road-works sign figure (black silhouette), drawn supersampled
        S = 8
        fg = blank(34 * S, 34 * S)
        fd = ImageDraw.Draw(fg)
        k = (0, 0, 0, 255)

        def P(x, y):
            return (x * S, y * S)
        fd.polygon([P(17, 31), P(23, 24), P(30, 31)], fill=k)                 # dirt pile
        fd.ellipse([P(7.5, 3.5), P(12.5, 8.5)], fill=k)                         # head
        fd.chord([P(6.5, 2.5), P(13.5, 7.5)], 180, 360, fill=k)                 # hard hat
        fd.line([P(5.5, 5.2), P(14, 5.2)], fill=k, width=S)                     # brim
        fd.line([P(10, 9.5), P(12.5, 19)], fill=k, width=int(3.2 * S))           # torso
        fd.line([P(12.5, 19), P(8, 25), P(7, 31)], fill=k, width=int(2.4 * S), joint='curve')
        fd.line([P(12.5, 19), P(16, 25), P(15, 31)], fill=k, width=int(2.4 * S), joint='curve')
        if (fi // 2) % 2 == 0:
            fd.line([P(6, 9), P(21, 26)], fill=k, width=int(1.3 * S))           # shovel handle
            fd.polygon([P(19.5, 24), P(23.5, 22.5), P(24.5, 28.5), P(21, 29)], fill=k)
            fd.line([P(10.5, 11), P(13, 16), P(16, 20)], fill=k, width=int(1.8 * S))
        else:
            fd.line([P(9, 8), P(17.5, 28)], fill=k, width=int(1.3 * S))
            fd.polygon([P(15.5, 26.5), P(19.5, 25.5), P(20, 31), P(16.5, 31)], fill=k)
            fd.line([P(10.5, 11), P(12, 15.5), P(13.8, 19.5)], fill=k, width=int(1.8 * S))
        # flashing beacon
        lc = (255, 51, 0, 255) if fi % 2 == 0 else (102, 26, 0, 255)
        fd.pieslice([P(25, 1.5), P(32, 8.5)], 180, 360, fill=lc, outline=k, width=S)
        fd.rectangle([P(24.5, 5), P(32.5, 6.5)], fill=k)
        if fi % 2 == 0:
            for a in (200, 240, 270, 300, 340):
                r1, r2 = 4.6, 6.4
                ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                fd.line([P(28.5 + r1 * ca, 5 + r1 * sa), P(28.5 + r2 * ca, 5 + r2 * sa)],
                        fill=(204, 0, 0, 255), width=int(0.8 * S))
        over(im, down(fg, (34, 34)), (3, 9))
        f1 = font('sans_b', 15)
        f2 = fit_font('sans_b', 'CONSTRUCTION', 98, start=14)
        text_center(dr, 88, 12, 'UNDER', f1, (0, 0, 0))
        text_center(dr, 88, 29, 'CONSTRUCTION', f2, (0, 0, 0))
        frames.append(im)
    save_gif(frames, os.path.join(out, 'construction.gif'), pal='web', durations=160,
             desc='Animated UNDER CONSTRUCTION sign: crawling hazard stripes, digging worker, flashing beacon')

    # ---------------- new.gif ----------------
    W, H = 44, 22
    frames = []
    for fi in range(2):
        S = 8
        b = blank(W * S, H * S)
        bd = ImageDraw.Draw(b)
        pts = []
        n = 14
        for i in range(2 * n):
            a = i * math.pi / n
            rx, ry = (21.5, 10.8) if i % 2 == 0 else (17, 7.6)
            pts.append(((22 + rx * math.cos(a)) * S, (11 + ry * math.sin(a)) * S))
        burst, edge, txt = ((255, 255, 0), (204, 0, 0), (255, 0, 0)) if fi == 0 else \
                           ((255, 0, 0), (255, 255, 0), (255, 255, 0))
        bd.polygon(pts, fill=burst + (255,), outline=edge + (255,), width=S)
        im = down(b, (W, H))
        dr = aliased(ImageDraw.Draw(im))
        f = font('sans_b', 11)
        tw, th = tsize(f, 'NEW!')
        text_at(dr, 22 - tw // 2 + 1, 11 - th // 2 + 1, 'NEW!', f, (102, 0, 0) if fi == 0 else (102, 0, 0))
        text_at(dr, 22 - tw // 2, 11 - th // 2, 'NEW!', f, txt)
        frames.append(im)
    save_gif(frames, os.path.join(out, 'new.gif'), pal='web', transparent=True, durations=350,
             desc='Animated flashing "NEW!" starburst (red/yellow swap)')

    # ---------------- email.gif ----------------
    W, H = 40, 30
    frames = []
    env = (255, 255, 204, 255)
    ol = (51, 51, 51, 255)
    for fi in range(4):
        im = blank(W, H)
        dr = ImageDraw.Draw(im)
        top, bot, l, r = 12, 28, 2, 37
        mid = (l + r) / 2.0
        dr.rectangle([l, top, r, bot], fill=(204, 204, 153, 255), outline=ol)    # inside/back
        if fi == 0:
            dr.rectangle([l, top, r, bot], fill=env, outline=ol)
            dr.line([(l, bot), (15, 20)], fill=(153, 153, 102, 255))
            dr.line([(r, bot), (24, 20)], fill=(153, 153, 102, 255))
            dr.polygon([(l, top), (mid, 22), (r, top)], fill=(255, 255, 230, 255), outline=ol)
            dr.ellipse([mid - 2.5, 18.5, mid + 2.5, 23.5], fill=(204, 0, 0, 255))   # wax seal
        else:
            dr.polygon([(l, top), (mid, 2), (r, top)], fill=(255, 255, 153, 255), outline=ol)
            if fi >= 2:
                ly = 8 if fi == 2 else 1
                dr.rectangle([8, ly, 31, 26], fill=(255, 255, 255, 255), outline=(102, 102, 102, 255))
                for yy in range(ly + 3, 24, 3):
                    dr.line([(11, yy), (28 if yy % 2 else 25, yy)], fill=(0, 51, 204, 255))
                if fi == 3:
                    aliased(dr)
                    text_at(dr, 25, ly + 2, '@', font('sans_b', 8), (204, 0, 0, 255))
            dr.polygon([(l, top), (mid, 21), (r, top), (r, bot), (l, bot)], fill=env, outline=ol)
            dr.line([(l, bot), (15, 21)], fill=(153, 153, 102, 255))
            dr.line([(r, bot), (24, 21)], fill=(153, 153, 102, 255))
        frames.append(im)
    save_gif(frames, os.path.join(out, 'email.gif'), pal='web', transparent=True,
             durations=[700, 200, 200, 900], desc='Animated envelope opening, letter pops out')

    # ---------------- digits ----------------
    segs = {'a': ((3.5, 2.6), (11.5, 2.6)), 'b': ((11.5, 2.6), (11.5, 10)), 'c': ((11.5, 10), (11.5, 17.4)),
            'd': ((3.5, 17.4), (11.5, 17.4)), 'e': ((3.5, 10), (3.5, 17.4)), 'f': ((3.5, 2.6), (3.5, 10)),
            'g': ((3.5, 10), (11.5, 10))}
    lit = {0: 'abcdef', 1: 'bc', 2: 'abged', 3: 'abgcd', 4: 'fgbc', 5: 'afgcd', 6: 'afgedc',
           7: 'abc', 8: 'abcdefg', 9: 'abcdfg'}
    for dgt in range(10):
        S = 8
        im = blank(15 * S, 20 * S, (0, 0, 0, 255))
        dr = ImageDraw.Draw(im)
        t, gap = 1.9, 0.45
        for name, ((x1, y1), (x2, y2)) in segs.items():
            if y1 == y2:
                x1, x2 = x1 + gap, x2 - gap
                poly = [(x1, y1), (x1 + t / 2, y1 - t / 2), (x2 - t / 2, y1 - t / 2), (x2, y1),
                        (x2 - t / 2, y1 + t / 2), (x1 + t / 2, y1 + t / 2)]
            else:
                y1, y2 = y1 + gap, y2 - gap
                poly = [(x1, y1), (x1 + t / 2, y1 + t / 2), (x1 + t / 2, y2 - t / 2), (x1, y2),
                        (x1 - t / 2, y2 - t / 2), (x1 - t / 2, y1 + t / 2)]
            poly = [((x + (10 - y) * 0.07) * S, y * S) for x, y in poly]   # slight italic slant
            on = name in lit[dgt]
            dr.polygon(poly, fill=(0, 255, 51, 255) if on else (0, 40, 0, 255))
        sm = down(im, (15, 20))
        d2 = ImageDraw.Draw(sm)
        d2.line([(0, 0), (0, 19)], fill=(51, 51, 51))
        d2.line([(14, 0), (14, 19)], fill=(26, 26, 26))
        d2.line([(1, 0), (13, 0)], fill=(34, 34, 34))
        d2.line([(1, 19), (13, 19)], fill=(34, 34, 34))
        save_gif(sm, os.path.join(out, 'digit_%d.gif' % dgt), pal='web',
                 desc='Hit-counter odometer digit %d (green LCD)' % dgt)

    # ---------------- fire.gif: flame strip of drifting, flickering tongues ----------------
    W, H, NF = 120, 30, 10
    fire_stops = [(0, (255, 255, 204)), (0.2, (255, 255, 51)), (0.45, (255, 170, 0)),
                  (0.7, (255, 68, 0)), (0.9, (204, 0, 0)), (1, (128, 0, 0))]
    rng = random.Random(1999)
    frames = []

    def tongue(x, period, drift):
        return (1 - abs(math.sin(math.pi * (x + drift) / period))) ** 1.3

    for fi in range(NF):
        t = fi / float(NF)
        im = blank(W, H)
        px = im.load()
        for x in range(W):
            a1 = 0.72 + 0.28 * math.sin(2 * math.pi * 2 * t + x * 0.37)
            a2 = 0.6 + 0.4 * math.sin(-2 * math.pi * 3 * t + x * 0.81 + 1.0)
            h = H * (0.2 + 0.66 * tongue(x, 15, 15 * t) * a1 + 0.3 * tongue(x, 8, -16 * t) * a2)
            h = min(H - 1.0, h)
            for y in range(H):
                rel = (H - y - 0.5) / h
                rel += rng.uniform(-0.07, 0.07)
                if rel <= 1.0:
                    px[x, y] = ramp(fire_stops, max(0.0, rel)) + (255,)
        frames.append(im)
    save_gif(frames, os.path.join(out, 'fire.gif'), pal='web', matte=(0, 0, 0), transparent=True,
             durations=80, desc='Animated flame strip (drifting flickering tongues), transparent background')

    # ---------------- globe.gif ----------------
    D, S = 32, 4
    R = D * S / 2.0 - S * 0.6
    cxy = D * S / 2.0
    L = (-0.5, -0.55, 0.67)
    ln = math.sqrt(sum(v * v for v in L))
    L = tuple(v / ln for v in L)

    def land(lon, lat):
        v = (math.sin(2 * lon + 0.6) * math.cos(1.6 * lat) + 0.6 * math.sin(3 * lon + 2.1 + 2 * lat)
             + 0.45 * math.cos(5 * lon - 1.3 + 3 * lat) + 0.3 * math.sin(7 * lon + 0.5 - 4 * lat)
             - 0.6 * (abs(lat) > 1.15))
        return v > 0.35 or lat > 1.3

    frames = []
    nf = 16
    tilt = math.radians(20)
    for fi in range(nf):
        rot = 2 * math.pi * fi / nf
        big = blank(D * S, D * S)
        px = big.load()
        for py in range(D * S):
            for pxx in range(D * S):
                x = (pxx + 0.5 - cxy) / R
                y = (py + 0.5 - cxy) / R
                rr = x * x + y * y
                if rr > 1:
                    continue
                z = math.sqrt(1 - rr)
                # un-tilt about x axis
                y2 = y * math.cos(tilt) - z * math.sin(tilt)
                z2 = y * math.sin(tilt) + z * math.cos(tilt)
                lat = -math.asin(max(-1, min(1, y2)))
                lon = math.atan2(x, z2) + rot
                shade = max(0.0, x * L[0] + y * L[1] + z * L[2])
                k = 0.30 + 0.75 * shade
                if land(lon, lat):
                    base = (230, 240, 255) if abs(lat) > 1.2 else (51, 170, 51)
                else:
                    base = (0, 90, 220)
                # graticule
                lonm = (math.degrees(lon) % 30.0)
                latm = (math.degrees(lat) % 30.0)
                if min(lonm, 30 - lonm) < 1.6 or min(latm, 30 - latm) < 1.4:
                    base = lerp(base, (170, 220, 255), 0.55)
                c = tuple(min(255, int(v * k)) for v in base)
                spec = max(0.0, x * L[0] + y * L[1] + z * L[2]) ** 24
                c = lerp(c, (255, 255, 255), spec * 0.8)
                px[pxx, py] = c + (255,)
        bd = ImageDraw.Draw(big)
        bd.ellipse([cxy - R, cxy - R, cxy + R, cxy + R], outline=(0, 0, 80, 255), width=int(S * 0.9))
        frames.append(down(big, (D, D)))
    save_gif(frames, os.path.join(out, 'globe.gif'), pal=96, transparent=True, durations=90,
             desc='Animated spinning globe with graticule (16 frames, seamless loop)')

    # ---------------- mailbox.gif ----------------
    frames = []
    for fi in range(2):
        S = 8
        big = blank(32 * S, 32 * S)
        dr = ImageDraw.Draw(big)

        def P(x, y):
            return (x * S, y * S)
        dr.rectangle([P(14, 18), P(18, 31.5)], fill=(102, 51, 0, 255))
        dr.rectangle([P(14.8, 18), P(16.2, 31.5)], fill=(153, 102, 51, 255))
        dr.rectangle([P(11, 29.5), P(21, 31.5)], fill=(51, 102, 0, 255))           # grass tuft
        ol = (51, 51, 51, 255)
        dr.rounded_rectangle([P(6, 6), P(28, 19)], radius=5 * S, fill=ol)
        dr.rectangle([P(6, 12), P(28, 19)], fill=ol)
        body = vgrad(int(21 * S), int(12 * S), [(0, (230, 230, 230)), (0.4, (190, 190, 200)), (1, (110, 110, 120))])
        bm = Image.new('L', body.size, 0)
        ImageDraw.Draw(bm).rounded_rectangle([0, 0, body.width - 1, body.height + 6 * S], radius=4.4 * S, fill=255)
        big.paste(body, (int(6.5 * S), int(6.5 * S)), bm)
        # arched front door
        dr.rounded_rectangle([P(2, 6), P(8, 19)], radius=3 * S, fill=ol)
        dr.rounded_rectangle([P(2.8, 6.8), P(7.2, 18.2)], radius=2.3 * S, fill=(150, 150, 160, 255))
        dr.rectangle([P(1, 13), P(3, 14)], fill=ol)
        aliased(dr)
        # flag
        red, dred = (221, 0, 0, 255), (102, 0, 0, 255)
        if fi == 0:   # flag down
            dr.rectangle([P(22, 13), P(30, 14.2)], fill=dred)
            dr.rectangle([P(26, 14), P(30.5, 17.5)], fill=red, outline=dred, width=int(0.6 * S))
        else:         # flag up
            dr.rectangle([P(22.8, 2), P(24, 14)], fill=dred)
            dr.rectangle([P(24, 2), P(29.5, 6)], fill=red, outline=dred, width=int(0.6 * S))
        dr.ellipse([P(22, 12.6), P(24.6, 15.2)], fill=(51, 51, 51, 255))
        frames.append(down(big, (32, 32)))
    save_gif(frames, os.path.join(out, 'mailbox.gif'), pal=48, transparent=True, durations=[900, 900],
             desc='Rural mailbox, flag pops up (2-frame animation)')

    # ---------------- kf_welcome.gif 468x60 banner ----------------
    W, H = 468, 60
    bg = hgrad(W, H, [(0, (0, 0, 51)), (0.55, (0, 51, 153)), (1, (0, 0, 102))])
    starfield(bg, 140, random.Random(45))
    dr = ImageDraw.Draw(bg)
    dr.rectangle([0, 0, W - 1, H - 1], outline=(0, 0, 0))
    dr.rectangle([1, 1, W - 2, H - 2], outline=(102, 153, 204))
    over(bg, emblem(50), (7, 5))
    fh = fit_font('sans_b', 'Welcome to KoldFusion Server 4.5', 388, start=24)
    hx, hy = 68, 7
    # headline: white with green "KoldFusion"
    parts = [('Welcome to ', (255, 255, 255)), ('KoldFusion', (102, 255, 51)), (' Server 4.5', (255, 255, 255))]
    asc = fh.getbbox('W')[1]
    x = hx
    for txt, col in parts:
        dr.text((x + 2, hy - asc + 2), txt, font=fh, fill=(0, 0, 0))
        dr.text((x, hy - asc), txt, font=fh, fill=col)
        x += fh.getlength(txt)
    subs = ['The Web Application Server for the New Millennium!',
            'Build database-driven sites in hours, not months.',
            'Click here to enter the Administrator  >>']
    frames = []
    fs = font('sans_b', 13)
    for i, s in enumerate(subs):
        im = bg.copy()
        d = ImageDraw.Draw(im)
        d.text((hx + 1, 37 - fs.getbbox('T')[1] + 1), s, font=fs, fill=(0, 0, 0))
        d.text((hx, 37 - fs.getbbox('T')[1]), s, font=fs, fill=(255, 204, 0) if i < 2 else (255, 255, 255))
        frames.append(im)
    save_gif(frames, os.path.join(out, 'kf_welcome.gif'), pal=96, durations=[2600, 2600, 2000],
             desc='468x60 banner "Welcome to KoldFusion Server 4.5" with rotating tag lines')


def make_textures():
    out = DEMO_DIR
    # rainbow_hr.gif 500x6
    W, H = 500, 6
    im = blank(W, H)
    px = im.load()
    rowk = [1.0, 1.0, 0.92, 0.82, 0.70, 0.55]
    rowl = [0.45, 0.1, 0, 0, 0, 0]
    for x in range(W):
        r, g, b = colorsys.hsv_to_rgb(0.83 * x / (W - 1.0), 1, 1)
        base = (r * 255, g * 255, b * 255)
        for y in range(H):
            c = tuple(v * rowk[y] for v in base)
            c = lerp(c, (255, 255, 255), rowl[y])
            px[x, y] = tuple(int(v) for v in c) + (255,)
    save_gif(im, os.path.join(out, 'rainbow_hr.gif'), pal=96, desc='500x6 rainbow horizontal rule (3D shaded)')

    # stars_bg.gif 128x128 tileable
    W = H = 128
    im = blank(W, H, (0, 0, 0, 255))
    px = im.load()
    rng = random.Random(1969)
    greys = [(51, 51, 51), (102, 102, 102), (102, 102, 153), (153, 153, 153), (204, 204, 204),
             (255, 255, 255), (255, 255, 204), (204, 204, 255)]
    for _ in range(230):
        px[rng.randrange(W), rng.randrange(H)] = rng.choice(greys) + (255,)
    for _ in range(9):
        x, y = rng.randrange(W), rng.randrange(H)
        px[x, y] = (255, 255, 255, 255)
        arm = rng.choice([(102, 153, 204), (153, 153, 153), (204, 204, 153)])
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            px[(x + dx) % W, (y + dy) % H] = arm + (255,)
    save_gif(im, os.path.join(out, 'stars_bg.gif'), pal='web', desc='Tileable dark starfield background')

    # bg_tile.gif 96x96 subtle grey marble / paper (periodic noise => seamless)
    W = H = 96
    rng = random.Random(7)
    waves = [(rng.randint(1, 4), rng.randint(-3, 3), rng.uniform(0, 6.3), rng.uniform(0.3, 1.0)) for _ in range(9)]
    im = blank(W, H)
    px = im.load()
    for y in range(H):
        for x in range(W):
            u, v = x / float(W), y / float(H)
            turb = sum(a * math.sin(2 * math.pi * (fx * u + fy * v) + ph) for fx, fy, ph, a in waves)
            m = math.sin(2 * math.pi * (u + 2 * v) + 1.6 * turb)
            vein = (1 - abs(m)) ** 6
            g = 228 - 22 * vein + 5 * math.sin(2 * math.pi * (3 * u - v) + turb) + rng.uniform(-4, 4)
            px[x, y] = (int(g), int(g), int(g + 3)) + (255,)
    save_gif(im, os.path.join(out, 'bg_tile.gif'), pal=16, desc='Seamless subtle grey marble/paper background tile')

    # 3D ball bullets
    for nm, base in (('red', (204, 0, 0)), ('blue', (0, 51, 204))):
        D, S = 13, 8
        big = blank(D * S, D * S)
        p = big.load()
        R = D * S / 2.0 - 2
        c0 = D * S / 2.0
        Lv = (-0.45, -0.55, 0.7)
        ln = math.sqrt(sum(v * v for v in Lv))
        Lv = tuple(v / ln for v in Lv)
        for yy in range(D * S):
            for xx in range(D * S):
                x, y = (xx + 0.5 - c0) / R, (yy + 0.5 - c0) / R
                rr = x * x + y * y
                if rr > 1:
                    continue
                z = math.sqrt(1 - rr)
                dif = max(0, x * Lv[0] + y * Lv[1] + z * Lv[2])
                hv = (Lv[0], Lv[1], Lv[2] + 1)
                hn = math.sqrt(sum(v * v for v in hv))
                spec = max(0, (x * hv[0] + y * hv[1] + z * hv[2]) / hn) ** 40
                c = tuple(v * (0.25 + 0.85 * dif) for v in base)
                c = lerp(c, (255, 255, 255), min(1, spec * 1.2))
                p[xx, yy] = tuple(min(255, int(v)) for v in c) + (255,)
        save_gif(down(big, (D, D)), os.path.join(out, 'bullet_%s.gif' % nm), pal=24, transparent=True,
                 desc='13x13 3D %s ball bullet' % nm)


# --------------------------------------------------------------------------
# verification + contact sheet
# --------------------------------------------------------------------------
def verify():
    rows = []
    ok = True
    for path, desc in MANIFEST:
        try:
            im = Image.open(path)
            n = getattr(im, 'n_frames', 1)
            info = (path, im.size, n, 'transparency' in im.info or im.info.get('transparency') is not None,
                    os.path.getsize(path), desc)
            im.seek(n - 1)
            im.load()
            rows.append(info)
        except Exception as e:   # pragma: no cover
            ok = False
            print('FAILED %s: %s' % (path, e))
    return ok, rows


def contact_sheet(path, W=1200):
    """Every image (all frames of animations, up to 16) on a checkerboard, small ones enlarged."""
    lab = font('sans', 11)
    ck = Image.new('RGBA', (16, 16), (232, 232, 232, 255))
    cd = ImageDraw.Draw(ck)
    cd.rectangle([0, 0, 7, 7], fill=(208, 208, 208, 255))
    cd.rectangle([8, 8, 15, 15], fill=(208, 208, 208, 255))
    tiles = []
    for p, _desc in MANIFEST:
        im = Image.open(p)
        n = getattr(im, 'n_frames', 1)
        frames = []
        for i in range(min(n, 16)):
            im.seek(i)
            frames.append(im.convert('RGBA'))
        w, h = frames[0].size
        sc = 3 if max(w, h) <= 20 else 2 if max(w, h) <= 140 else 1
        fw, fh = w * sc, h * sc
        cols = max(1, min(len(frames), (W - 20) // (fw + 4)))
        rows = (len(frames) + cols - 1) // cols
        tile = Image.new('RGBA', (max(cols * (fw + 4), 150), rows * (fh + 4) + 16), (255, 255, 255, 255))
        for i, f in enumerate(frames):
            cb = Image.new('RGBA', (fw, fh))
            for yy in range(0, fh, 16):
                for xx in range(0, fw, 16):
                    cb.paste(ck, (xx, yy))
            cb.alpha_composite(f.resize((fw, fh), Image.NEAREST))
            tile.paste(cb, ((i % cols) * (fw + 4), (i // cols) * (fh + 4)))
        ImageDraw.Draw(tile).text((0, rows * (fh + 4)), '%s  %dx%d%s' % (
            os.path.basename(p), w, h, ('  [%d fr]' % n) if n > 1 else ''), font=lab, fill=(0, 0, 0))
        tiles.append(tile)
    x, y, rowh, place = 10, 10, 0, []
    for t in tiles:
        if x + t.width > W - 10 and x > 10:
            x, y, rowh = 10, y + rowh + 12, 0
        place.append((x, y, t))
        x += t.width + 14
        rowh = max(rowh, t.height)
    sheet = Image.new('RGB', (W, y + rowh + 10), (255, 255, 255))
    for x, y, t in place:
        sheet.paste(t, (x, y))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path)
    return path


def main(argv):
    sheet = None
    if '--sheet' in argv:
        sheet = argv[argv.index('--sheet') + 1]
    make_logos()
    make_nav()
    make_icons()
    make_buttons()
    make_animated()
    make_textures()
    ok, rows = verify()
    for path, size, n, tr, nbytes, desc in rows:
        print('%-46s %4dx%-4d %2d fr %s %6d B  %s' % (os.path.relpath(path, ROOT), size[0], size[1], n,
                                                      'T' if tr else '-', nbytes, desc))
    print('%d files, %s' % (len(rows), 'all OK' if ok else 'ERRORS'))
    if sheet:
        print('contact sheet:', contact_sheet(sheet))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
