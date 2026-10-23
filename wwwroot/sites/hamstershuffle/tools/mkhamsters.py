#!/usr/bin/env python3
"""mkhamsters.py -- build the whole Hamster Shuffle site: original dancing-critter GIFs (Pillow), an original
chiptune MIDI loop, and every static HTML page.  Everything is drawn/composed/written from scratch.

Usage:  python3 tools/mkhamsters.py
"""
import math
import os
import random
import struct

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(os.path.join(HERE, '..'))
IMG = os.path.join(SITE, 'images')
MID = os.path.join(SITE, 'midi')
KEY = (255, 0, 254)
RING = ['yowza', 'altavisor', 'askreeves', 'orinoco', 'ubid', 'etoyz', 'petz', 'geohoods', 'hamstershuffle',
        'dashdot', 'snapster', 'cnm']


# ====================================================================== GIF helpers
def font(size, bold=True):
    for p in ['/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf' if bold else
              '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf']:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def canvas(w, h, bg=KEY):
    im = Image.new('RGB', (w, h), bg)
    d = ImageDraw.Draw(im)
    d.fontmode = '1'
    return im, d


def save(name, frames, dur=120, transparent=True):
    if not isinstance(frames, list):
        frames = [frames]
    w, h = frames[0].size
    tall = Image.new('RGB', (w, h * len(frames)))
    masks = []
    for i, f in enumerate(frames):
        m = f.copy()
        px, mp = m.load(), None
        mk = Image.new('1', (w, h), 0)
        mp = mk.load()
        for y in range(h):
            for x in range(w):
                if px[x, y] == KEY:
                    mp[x, y] = 1
                    px[x, y] = (255, 255, 255)
        masks.append(mk)
        tall.paste(m, (0, h * i))
    q = tall.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = (q.getpalette()[:765] + [0] * 765)[:765] + [254, 1, 253]
    q.putpalette(pal)
    out = []
    for i in range(len(frames)):
        fr = tall.crop((0, h * i, w, h * (i + 1))).quantize(palette=q, dither=Image.Dither.NONE)
        if transparent:
            fr.paste(255, (0, 0), masks[i])
            p2 = list(pal)
            p2[765:768] = list(KEY)
            fr.putpalette(p2)
        out.append(fr)
    kw = dict(save_all=len(out) > 1, optimize=False)
    if len(out) > 1:
        kw.update(append_images=out[1:], duration=dur, loop=0, disposal=2)
    if transparent:
        kw['transparency'] = 255
    out[0].save(os.path.join(IMG, name), **kw)


FUR = (222, 158, 82)
FUR_D = (120, 70, 25)
BELLY = (255, 238, 205)
PINK = (255, 150, 170)


def hamster(d, cx, cy, s=1.0, lean=0, arm_l=0.0, arm_r=0.0, leg_l=0, leg_r=0, blink=False, mouth=False,
            fur=FUR, fur_d=FUR_D, belly=BELLY, ears=1.0, glasses=False):
    """a chubby upright hamster centred on (cx, cy) = middle of the body. arm angles in radians from 'down'."""
    def S(v):
        return int(round(v * s))
    bx = cx + lean
    # legs (feet)
    for side, lift in ((-1, leg_l), (1, leg_r)):
        fx = bx + side * S(7)
        fy = cy + S(16) - lift
        d.ellipse((fx - S(5), fy - S(3), fx + S(5), fy + S(3)), fill=PINK, outline=fur_d)
    # body
    d.ellipse((bx - S(13), cy - S(14), bx + S(13), cy + S(17)), fill=fur, outline=fur_d)
    d.ellipse((bx - S(8), cy - S(6), bx + S(8), cy + S(15)), fill=belly)
    # arms
    for side, ang in ((-1, arm_l), (1, arm_r)):
        sx, sy = bx + side * S(10), cy - S(4)
        ex = sx + side * S(11) * math.sin(ang)
        ey = sy + S(11) * math.cos(ang)
        d.line((sx, sy, ex, ey), fill=fur, width=max(2, S(4)))
        d.ellipse((ex - S(3), ey - S(3), ex + S(3), ey + S(3)), fill=PINK)
    # head
    hx, hy = bx + lean // 2, cy - S(20)
    for side in (-1, 1):
        ex, ey = hx + side * S(9), hy - S(9)
        r = S(4.5 * ears)
        d.ellipse((ex - r, ey - r, ex + r, ey + r), fill=fur, outline=fur_d)
        d.ellipse((ex - r + 2, ey - r + 2, ex + r - 2, ey + r - 2), fill=PINK)
    d.ellipse((hx - S(12), hy - S(10), hx + S(12), hy + S(10)), fill=fur, outline=fur_d)
    d.ellipse((hx - S(7), hy - S(1), hx + S(7), hy + S(10)), fill=belly)
    for side in (-1, 1):
        d.ellipse((hx + side * S(8) - S(3), hy + S(1), hx + side * S(8) + S(3), hy + S(5)), fill=(255, 175, 175))
    if glasses:
        d.rectangle((hx - S(9), hy - S(5), hx - S(1), hy - S(1)), fill=(0, 0, 0))
        d.rectangle((hx + S(1), hy - S(5), hx + S(9), hy - S(1)), fill=(0, 0, 0))
        d.line((hx - S(1), hy - S(4), hx + S(1), hy - S(4)), fill=(0, 0, 0))
    elif blink:
        d.line((hx - S(7), hy - S(3), hx - S(3), hy - S(3)), fill=(0, 0, 0))
        d.line((hx + S(3), hy - S(3), hx + S(7), hy - S(3)), fill=(0, 0, 0))
    else:
        for side in (-1, 1):
            ex = hx + side * S(5)
            d.ellipse((ex - S(2.5), hy - S(5), ex + S(2.5), hy), fill=(0, 0, 0))
            d.point((ex - S(1), hy - S(4)), fill=(255, 255, 255))
    d.ellipse((hx - S(1.5), hy + S(1), hx + S(1.5), hy + S(3)), fill=(200, 80, 100))
    if mouth:
        d.ellipse((hx - S(2), hy + S(4), hx + S(2), hy + S(8)), fill=(150, 30, 50))
    else:
        d.arc((hx - S(3), hy + S(2), hx + S(3), hy + S(6)), 20, 160, fill=(120, 40, 40))


def draw_gifs():
    os.makedirs(IMG, exist_ok=True)
    # 1. the kick-line trio (144x48)
    frames = []
    for i in range(4):
        im, d = canvas(144, 48)
        for k in range(3):
            ph = (i + k) % 4
            up = ph in (0, 1)
            hamster(d, 24 + k * 48, 30, s=0.62, lean=[-2, 0, 2, 0][ph], arm_l=2.6 if up else 0.5,
                    arm_r=0.5 if up else 2.6, leg_l=6 if ph == 0 else 0, leg_r=6 if ph == 2 else 0,
                    mouth=ph == 1, blink=ph == 3 and k == 1)
        frames.append(im)
    save('trio.gif', frames, 150)

    # 2. hammy: side-to-side shuffle (60x70)
    frames = []
    for i in range(4):
        im, d = canvas(60, 70)
        lean = [-5, 0, 5, 0][i]
        hamster(d, 30, 44, s=0.95, lean=lean, arm_l=[2.8, 1.6, 0.4, 1.6][i], arm_r=[0.4, 1.6, 2.8, 1.6][i],
                leg_l=4 if i == 2 else 0, leg_r=4 if i == 0 else 0, mouth=i % 2 == 1)
        frames.append(im)
    save('hammy.gif', frames, 160)

    # 3. gerbil with a long tufted tail, hopping (60x70)
    frames = []
    for i in range(4):
        im, d = canvas(60, 70)
        hop = [0, 6, 10, 6][i]
        tail = [-0.5, 0.0, 0.5, 0.0][i]
        tx, ty = 40, 58 - hop
        pts = [(tx + 6 * k * math.cos(tail - 0.7 + k * 0.2), ty - 6 * k * math.sin(0.4 + tail * k * 0.2))
               for k in range(4)]
        d.line([(tx, ty)] + pts, fill=(170, 120, 70), width=2)
        d.ellipse((pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4), fill=(110, 70, 30))
        hamster(d, 28, 46 - hop, s=0.85, lean=0, arm_l=2.2 if hop else 0.6, arm_r=2.2 if hop else 0.6,
                leg_l=2 if hop else 0, leg_r=2 if hop else 0, fur=(200, 165, 110), fur_d=(110, 80, 40),
                belly=(250, 245, 230), ears=1.5, mouth=hop > 8)
        frames.append(im)
    save('gerbil.gif', frames, 140)

    # 4. moonwalker (53x74): legs slide, body glides
    frames = []
    for i in range(6):
        im, d = canvas(53, 74)
        x = 26 + int(5 * math.sin(i * math.pi / 3))
        hamster(d, x, 48, s=0.9, lean=-3, arm_l=0.4 + 0.5 * math.sin(i), arm_r=0.4 - 0.5 * math.sin(i),
                leg_l=5 if i % 2 == 0 else 0, leg_r=0 if i % 2 == 0 else 5, blink=i == 4)
        d.rectangle((x - 9, 18, x + 9, 21), fill=(20, 20, 20))
        d.rectangle((x - 6, 9, x + 6, 19), fill=(30, 30, 30))
        frames.append(im)
    save('moonwalk.gif', frames, 130)

    # 5. guinea pig popcorning (64x56)
    frames = []
    for i in range(4):
        im, d = canvas(64, 56)
        hop = [0, 8, 14, 6][i]
        y = 40 - hop
        d.ellipse((8, y - 16, 56, y + 12), fill=(250, 250, 245), outline=(110, 80, 50))
        d.pieslice((8, y - 16, 56, y + 12), 200, 300, fill=(230, 140, 60))
        d.pieslice((8, y - 16, 56, y + 12), 300, 340, fill=(50, 40, 30))
        d.ellipse((2, y - 14, 26, y + 6), fill=(230, 140, 60), outline=(110, 80, 50))
        d.ellipse((6, y - 10, 10, y - 6), fill=(0, 0, 0))
        d.ellipse((14, y - 17, 22, y - 11), fill=(255, 170, 170), outline=(110, 80, 50))
        d.ellipse((3, y - 3, 6, y), fill=(200, 80, 100))
        for fx in (14, 46):
            d.ellipse((fx - 4, y + 9, fx + 4, y + 13), fill=PINK)
        if hop > 6:
            d.line((30, y + 16, 26, y + 20), fill=(120, 120, 120))
            d.line((36, y + 16, 40, y + 20), fill=(120, 120, 120))
        frames.append(im)
    save('guinea.gif', frames, 140)

    # 6. mouse doing the twist (48x60)
    frames = []
    for i in range(4):
        im, d = canvas(48, 60)
        tw = [-4, 0, 4, 0][i]
        d.line((24 - tw, 52, 40 - tw, 56, 46, 48), fill=(255, 160, 170), width=2)
        hamster(d, 24, 40, s=0.75, lean=tw, arm_l=[2.0, 1.2, 0.6, 1.2][i], arm_r=[0.6, 1.2, 2.0, 1.2][i],
                leg_l=3 if tw < 0 else 0, leg_r=3 if tw > 0 else 0, fur=(170, 170, 180), fur_d=(80, 80, 90),
                belly=(235, 235, 240), ears=1.9, blink=i == 1)
        frames.append(im)
    save('mouse.gif', frames, 150)

    # 7. disco hamster with shades, pointing up/down (60x70)
    frames = []
    for i in range(2):
        im, d = canvas(60, 70)
        hamster(d, 30, 44, s=0.95, lean=3 if i else -3, arm_l=3.0 if i == 0 else 0.3, arm_r=0.3 if i == 0 else 2.2,
                leg_l=4 * i, leg_r=4 * (1 - i), glasses=True)
        for k in range(3):
            sx = [8, 50, 30][k]
            d.point([(sx, 6 + 4 * k), (sx - 1, 6 + 4 * k), (sx + 1, 6 + 4 * k), (sx, 5 + 4 * k), (sx, 7 + 4 * k)],
                    fill=(255, 220, 0) if (k + i) % 2 else (255, 80, 200))
        frames.append(im)
    save('disco.gif', frames, 300)

    # title banner: bouncing letters
    title = 'THE HAMSTER SHUFFLE'
    f = font(30)
    frames = []
    for i in range(6):
        im, d = canvas(460, 56, (255, 255, 255))
        x = 8
        for j, ch in enumerate(title):
            y = 12 + int(6 * math.sin((j + i) * 1.1))
            col = [(255, 0, 128), (255, 140, 0), (0, 160, 0), (0, 90, 255), (160, 0, 220)][(j + i) % 5]
            d.text((x + 2, y + 2), ch, font=f, fill=(200, 200, 200))
            d.text((x, y), ch, font=f, fill=col)
            x += int(f.getlength(ch)) + (2 if ch != ' ' else 4)
        frames.append(im)
    save('title.gif', frames, 120, transparent=False)

    # counter digits: little wheel-cage digits
    for n in range(10):
        im, d = canvas(16, 22, (255, 255, 200))
        d.rectangle((0, 0, 15, 21), outline=(200, 120, 0))
        d.text((3, 1), str(n), font=font(17), fill=(200, 60, 0))
        save('cnt_%d.gif' % n, im, transparent=False)

    # buttons
    for name, text, col in [('btn_fanclub.gif', 'FAN CLUB', (255, 0, 128)), ('btn_friend.gif', 'TELL A FRIEND',
                                                                             (0, 120, 255)),
                            ('btn_dancers.gif', 'MEET THE DANCERS', (0, 160, 0)),
                            ('btn_help.gif', 'NO MUSIC?!', (255, 120, 0))]:
        frames = []
        for i in range(2):
            im, d = canvas(130, 32)
            c = col if i == 0 else tuple(min(255, v + 60) for v in col)
            d.rounded_rectangle((0, 0, 129, 31), 14, fill=c, outline=(0, 0, 0))
            w = f2 = font(12)
            tw = f2.getlength(text)
            d.text(((130 - tw) / 2, 8), text, font=f2, fill=(255, 255, 255) if i == 0 else (255, 255, 0))
            del w
            frames.append(im)
        save(name, frames, 500)

    # 88x31 link button
    im, d = canvas(88, 31, (255, 255, 200))
    d.rectangle((0, 0, 87, 30), outline=(255, 0, 128))
    hamster(d, 14, 22, s=0.42, arm_l=2.6, arm_r=2.6)
    d.text((28, 3), 'Hamster', font=font(11), fill=(255, 0, 128))
    d.text((28, 16), 'Shuffle!', font=font(11), fill=(0, 90, 255))
    save('hamster_88.gif', im, transparent=False)

    # awards
    for name, l1, l2, col in [('award_annoying.gif', 'Most Annoying', 'Site of 1999', (200, 0, 0)),
                              ('award_hamsterific.gif', 'Hamster-rific!', 'Site Award', (0, 120, 0)),
                              ('award_stuck.gif', 'Song Stuck In', 'My Head Award', (90, 0, 160))]:
        im, d = canvas(100, 100)
        d.ellipse((20, 2, 80, 62), fill=(255, 215, 0), outline=(150, 100, 0))
        hamster(d, 50, 40, s=0.6, arm_l=2.8, arm_r=2.8, mouth=True)
        d.rectangle((2, 66, 97, 97), fill=col, outline=(0, 0, 0))
        f3 = font(11)
        for k, t in enumerate((l1, l2)):
            d.text(((100 - f3.getlength(t)) / 2, 69 + k * 13), t, font=f3, fill=(255, 255, 255) if k == 0 else
                   (255, 255, 0))
        save(name, im)

    # merch mockups
    im, d = canvas(120, 120, (230, 240, 255))
    d.polygon([(30, 20), (50, 12), (70, 12), (90, 20), (108, 40), (94, 50), (88, 44), (88, 112), (32, 112),
               (32, 44), (26, 50), (12, 40)], fill=(255, 255, 255), outline=(0, 0, 0))
    hamster(d, 60, 70, s=0.7, arm_l=2.6, arm_r=0.6)
    d.text((40, 94), 'SHUFFLE!', font=font(9), fill=(255, 0, 128))
    save('merch_shirt.gif', im, transparent=False)
    im, d = canvas(120, 100, (230, 240, 255))
    d.rounded_rectangle((8, 14, 112, 90), 10, fill=(0, 160, 220), outline=(0, 0, 0))
    for k in range(3):
        hamster(d, 30 + k * 30, 58, s=0.45, arm_l=2.6 if k % 2 else 0.5, arm_r=0.5 if k % 2 else 2.6)
    save('merch_mousepad.gif', im, transparent=False)
    im, d = canvas(120, 100, (230, 240, 255))
    d.rectangle((30, 20, 90, 86), fill=(255, 255, 255), outline=(0, 0, 0))
    d.arc((80, 34, 104, 64), 270, 90, fill=(0, 0, 0), width=3)
    hamster(d, 60, 58, s=0.55, glasses=True, arm_l=3.0)
    save('merch_mug.gif', im, transparent=False)

    # rainbow divider
    im, d = canvas(468, 8)
    import colorsys
    for x in range(468):
        r, g, b = colorsys.hsv_to_rgb(x / 468.0, 0.9, 1.0)
        d.line((x, 1, x, 6), fill=(int(r * 255), int(g * 255), int(b * 255)))
    save('rainbow.gif', im)

    # wheel (spinning hamster wheel)
    frames = []
    for i in range(8):
        im, d = canvas(64, 64)
        d.ellipse((4, 4, 60, 60), outline=(120, 120, 140), width=3)
        for k in range(12):
            a = math.radians(k * 30 + i * 7.5)
            d.line((32 + 24 * math.cos(a), 32 + 24 * math.sin(a), 32 + 28 * math.cos(a), 32 + 28 * math.sin(a)),
                   fill=(150, 150, 170), width=2)
        d.line((32, 32, 32, 63), fill=(100, 100, 110), width=3)
        hamster(d, 32, 44, s=0.55, lean=0, arm_l=1.5, arm_r=1.5, leg_l=4 * (i % 2), leg_r=4 * (1 - i % 2))
        frames.append(im)
    save('wheel.gif', frames, 90)


# ====================================================================== MIDI
TPQ = 96


def vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(out))


def track(evs, name):
    nb = name.encode()
    evs = [(0, b'\xff\x03' + vlq(len(nb)) + nb)] + sorted(evs, key=lambda e: (e[0], 0 if e[1][0] & 0xF0 == 0x80 else 1))
    data, last = b'', 0
    for t, b in evs:
        data += vlq(t - last) + b
        last = t
    data += b'\x00\xff\x2f\x00'
    return b'MTrk' + struct.pack('>I', len(data)) + data


def note(evs, ch, t, dur, p, v=100):
    evs.append((t, bytes([0x90 | ch, p, v])))
    evs.append((t + max(1, dur - 6), bytes([0x80 | ch, p, 0])))


N = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def pitch(s):
    return 12 * (int(s[-1]) + 1) + N[s[0]] + (1 if '#' in s else 0)


# an original 8-bar hook (pitch, eighths) - the "Shuffle"
HOOK_A = [('E5', 1), ('E5', 1), ('G5', 1), ('E5', 1), ('D5', 1), ('C5', 1), ('D5', 2),
          ('E5', 1), ('E5', 1), ('G5', 1), ('A5', 1), ('G5', 2), ('E5', 2),
          ('F5', 1), ('F5', 1), ('A5', 1), ('F5', 1), ('E5', 1), ('D5', 1), ('E5', 2),
          ('D5', 1), ('C5', 1), ('D5', 1), ('E5', 1), ('C5', 4)]
HOOK_B = [('C6', 1), ('B5', 1), ('A5', 1), ('G5', 1), ('A5', 2), ('G5', 2),
          ('F5', 1), ('E5', 1), ('D5', 1), ('E5', 1), ('F5', 2), ('A5', 2),
          ('G5', 1), ('G5', 1), ('A5', 1), ('G5', 1), ('E5', 1), ('C5', 1), ('E5', 2),
          ('D5', 2), ('G4', 2), ('C5', 4)]
CHORDS_A = ['C', 'C', 'F', 'G']
CHORDS_B = ['A', 'F', 'C', 'G']
ROOT = {'C': 36, 'F': 41, 'G': 43, 'A': 45}


def make_tune(fname, title, bpm, lead_prog, hooks, transpose=0):
    E = TPQ // 2
    bar = TPQ * 4
    lead, bass, drums, harm = [], [], [], []
    t = 0
    for sec in hooks:
        mel = HOOK_A if sec == 'A' else HOOK_B
        chords = CHORDS_A if sec == 'A' else CHORDS_B
        start = t
        for p, ln in mel:
            note(lead, 0, t, ln * E, pitch(p) + transpose, 105)
            note(harm, 2, t, ln * E, pitch(p) + transpose - 12 + (4 if sec == 'B' else 0), 55)
            t += ln * E
        for b, ch in enumerate(chords):
            r = ROOT[ch] + transpose
            bt = start + b * bar
            for k in range(8):
                note(bass, 1, bt + k * E, E, r + (12 if k % 2 else 0), 95)
            for k in range(4):
                note(drums, 9, bt + k * TPQ, E, 36 if k % 2 == 0 else 38, 110)
                note(drums, 9, bt + k * TPQ, E, 42, 60)
                note(drums, 9, bt + k * TPQ + E, E, 42, 80)
            note(drums, 9, bt + 3 * TPQ + E, E, 39, 90)
        t = start + 4 * bar
    tempo = 60000000 // bpm
    meta = [(0, b'\xff\x51\x03' + struct.pack('>I', tempo)[1:]), (0, b'\xff\x58\x04\x04\x02\x18\x08')]
    tracks = [track(meta, title), track([(0, bytes([0xC0, lead_prog]))] + lead, 'Lead'),
              track([(0, bytes([0xC1, 38]))] + bass, 'Bass'), track([(0, bytes([0xC2, 81]))] + harm, 'Harmony'),
              track(drums, 'Drums')]
    with open(os.path.join(MID, fname), 'wb') as f:
        f.write(b'MThd' + struct.pack('>IHHH', 6, 1, len(tracks), TPQ) + b''.join(tracks))


def make_midis():
    os.makedirs(MID, exist_ok=True)
    make_tune('shuffle.mid', 'The Hamster Shuffle', 168, 80, ['A', 'A', 'B', 'A'])
    make_tune('shuffle_remix.mid', 'Hamster Shuffle (Turbo Wheel Remix)', 184, 81, ['A', 'B', 'A', 'B', 'A'], 2)


# ====================================================================== HTML
def ring_bar(root=''):
    i = RING.index('hamstershuffle')
    prev, nxt = RING[i - 1], RING[(i + 1) % len(RING)]
    arr = ','.join('"%s"' % s for s in RING)
    return ('<P><CENTER><TABLE BORDER=2 CELLPADDING=3 CELLSPACING=0 BGCOLOR="#C0C0C0"><TR><TD ALIGN=CENTER>'
            '<FONT FACE="Arial, Helvetica" SIZE=1 COLOR="#000000">\n'
            '<A HREF="%s../%s/index.html">&lt;&lt; Prev</A> |\n'
            '<A HREF="%s../yowza/index.html" onClick="var s=new Array(%s); location.href=\'%s../\'+'
            's[Math.floor(Math.random()*s.length)]+\'/index.html\'; return false;">Random</A> |\n'
            '<B><A HREF="%s../../web1999/index.html">The 1999 Web Ring</A></B> |\n'
            '<A HREF="%s../%s/index.html">Next &gt;&gt;</A>\n'
            '</FONT></TD></TR></TABLE></CENTER></P>\n' % (root, prev, root, arr, root, root, root, nxt))


def music_js(mid):
    # the classic 1998 browser sniff: Pioneer gets EMBED, Explor-o-Matic gets BGSOUND
    return ('<SCRIPT LANGUAGE="JavaScript">\n<!--\nif (navigator.appName == "Netscape") {\n'
            '  document.write(\'<EMBED SRC="midi/%s" AUTOSTART="true" HIDDEN="true" LOOP="true"></EMBED>\');\n'
            '} else if (navigator.appName == "Microsoft Internet Explorer") {\n'
            '  document.write(\'<BGSOUND SRC="midi/%s" LOOP="-1">\');\n'
            '} else {\n  document.write(\'<BGSOUND SRC="midi/%s" LOOP="-1"><EMBED SRC="midi/%s" AUTOSTART="true" '
            'HIDDEN="true" LOOP="true"></EMBED>\');\n}\n//-->\n</SCRIPT>\n' % (mid, mid, mid, mid))


def page(title, body, head_extra='', bg='#FFFFFF'):
    return ('<HTML>\n<HEAD>\n<TITLE>%s</TITLE>\n<META NAME="GENERATOR" CONTENT="Microsoft FrontDoor Page 3.0">\n'
            '<META NAME="KEYWORDS" CONTENT="hamster, hamsters, dance, shuffle, dancing hamsters, funny, cute">\n%s'
            '</HEAD>\n<BODY BGCOLOR="%s" TEXT="#000000" LINK="#0000FF" VLINK="#551A8B">\n%s\n</BODY>\n</HTML>\n'
            % (title, head_extra, bg, body))


DANCERS = [('trio.gif', 144, 48), ('hammy.gif', 60, 70), ('gerbil.gif', 60, 70), ('moonwalk.gif', 53, 74),
           ('guinea.gif', 64, 56), ('mouse.gif', 48, 60), ('disco.gif', 60, 70)]


def dance_floor(pattern_seed, rows=24):
    """rows of dancers, roughly 800 pixels wide each (they wrap like the real thing)"""
    rr = random.Random(pattern_seed)
    out = []
    count = 0
    order = [1, 0, 2, 0, 3, 4, 0, 5, 6]
    for r in range(rows):
        kind = DANCERS[order[r % len(order)]]
        # every row is mostly one kind of dancer with the odd guest
        line = []
        width = 0
        while width < 760:
            k = kind if rr.random() < 0.85 else rr.choice(DANCERS)
            line.append('<IMG SRC="images/%s" WIDTH=%d HEIGHT=%d ALT="">' % k)
            width += k[1]
            count += 3 if k[0] == 'trio.gif' else 1
        out.append(''.join(line))
    return '\n'.join(out), count


GB_NAMES = ['Jenny', 'SkaterDude', 'Hamster Lover #1', 'Mr. Wiggles', 'Bob', 'Kristy & Megan', 'Anonymous',
            'Cubicle Guy', 'Sarah (age 9)', 'The Night Shift', 'xXHammyFanXx', 'Grandpa Joe', 'Becky', 'Professor Pip',
            'Dave in Accounting', 'Lindsay', 'NotACatPerson', 'The whole 3rd floor', 'Trish', 'Hammy\'s #1 fan',
            'Tyler', 'Ms. Kowalski\'s 4th grade class', 'Kyle', 'A very tired mom', 'Nadia', 'Captain Cheeks',
            'Rolf', 'Gerbil Gary', 'Marcy', 'Pete']
GB_TEXT = [
    'I have had this page open for 3 hours. My boss thinks I am working. I am not working.',
    'WHY CAN\'T I STOP WATCHING THIS',
    'My hamster Nibbles watched this with me and he started running on his wheel really fast. True story.',
    'I sent this to everyone in my address book. Some of them are not speaking to me now.',
    'This song is going to be in my head until the year 2000. Maybe longer.',
    'The guinea pig is the best dancer. Fight me.',
    'Moonwalk Mike for President!!!',
    'I made my whole computer class come look. The teacher made us close it. Then she opened it again.',
    'Is there a version with more hamsters? I need MORE HAMSTERS.',
    'My dad says this is the stupidest thing on the Internet and then he watched it for twenty minutes.',
    'hamsters hamsters hamsters hamsters hamsters',
    'We played this at our office party. Productivity has never recovered.',
    'Best. Site. Ever.',
    'I can\'t hear the music!!! Oh wait I had my speakers off. NOW I CAN HEAR IT.',
    'The gerbil is not a hamster. Just saying. Still love it.',
    'I counted the hamsters and lost count at 211. Then I started over.',
    'My cat sat in front of the monitor and tried to catch the hamsters. 10/10.',
    'This is what the Internet was invented for.',
    'Please make a T-shirt!!! (Oh, there is a merch page. Never mind!)',
    'I am a serious adult with a serious job and I have bookmarked this page.',
    'Disco hamster with the sunglasses is my spirit animal.',
    'Greetings from Norway! The hamsters are very popular here also.',
    'My little brother cried when I closed the window so now it is open forever.',
    'Hammy is so cute I want to put him in my pocket.',
    'I came for the hamsters. I stayed for the hamsters.',
]


def write(rel, html):
    p = os.path.join(SITE, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='latin-1', errors='xmlcharrefreplace') as f:
        f.write(html)


def footer(root=''):
    return ('<P><CENTER><FONT FACE="Arial" SIZE=2>\n<A HREF="%sindex.html">Dance Floor</A> | '
            '<A HREF="%sdancers.html">Meet the Dancers</A> | <A HREF="%sfanclub.html">Fan Club</A> | '
            '<A HREF="%stellafriend.html">Tell a Friend</A> | <A HREF="%sremix.html">Turbo Remix</A> | '
            '<A HREF="%smerch.html">Merchandise</A> | <A HREF="%shelp.html">Help!</A>\n</FONT></CENTER></P>\n'
            '<P><CENTER><FONT FACE="Arial" SIZE=1>This page hosted by <A HREF="%s../geohoods/index.html">GeoHoods</A>. '
            '<A HREF="%s../geohoods/join.html">Get your own Free Home Page</A></FONT></CENTER></P>\n'
            % ((root,) * 9)) + ring_bar(root)


def counter_js(base):
    return ('<SCRIPT LANGUAGE="JavaScript">\n<!--\nvar hits = %d + Math.floor((new Date().getTime() - '
            'new Date(1999, 0, 1).getTime()) / 2500);\nvar s = "" + hits;\nfor (var i = 0; i < s.length; i++)\n'
            '  document.write("<IMG SRC=\\"images/cnt_" + s.charAt(i) + ".gif\\" WIDTH=16 HEIGHT=22>");\n//-->\n'
            '</SCRIPT><NOSCRIPT>%s</NOSCRIPT>\n' % (base, ''.join('<IMG SRC="images/cnt_%s.gif" WIDTH=16 HEIGHT=22>'
                                                                   % c for c in str(base))))


def make_pages():
    floor, count = dance_floor('shuffle')
    body = ('<CENTER>\n<H1><FONT FACE="Arial Black, Arial" COLOR="#FF0080">THE HAMSTER SHUFFLE</FONT></H1>\n'
            '<H3><FONT FACE="Comic Sans MS, Arial">everybody shuffle now!</FONT></H3>\n'
            '<BR>\n</CENTER>\n<DL>\n<DT><CENTER>\n%s\n</CENTER>\n</DL>\n'
            '<CENTER>\n<P><FONT FACE="Arial" SIZE=2>%d dancers and counting!</FONT></P>\n'
            '<P><FONT FACE="Arial" SIZE=2>You are shuffler number</FONT><BR>\n%s</P>\n'
            '<P><A HREF="help.html"><IMG SRC="images/btn_help.gif" WIDTH=130 HEIGHT=32 BORDER=0 ALT="HELP! I can\'t '
            'hear the music!"></A> <A HREF="fanclub.html"><IMG SRC="images/btn_fanclub.gif" WIDTH=130 HEIGHT=32 '
            'BORDER=0 ALT="Fan Club"></A> <A HREF="tellafriend.html"><IMG SRC="images/btn_friend.gif" WIDTH=130 '
            'HEIGHT=32 BORDER=0 ALT="Tell a friend"></A> <A HREF="dancers.html"><IMG SRC="images/btn_dancers.gif" '
            'WIDTH=130 HEIGHT=32 BORDER=0 ALT="Meet the dancers"></A></P>\n'
            '<P><FONT FACE="Arial" SIZE=1>&copy; 1998 shuffle@hamstershuffle.com - all dancers are original '
            'and were not harmed</FONT></P>\n'
            '<P><A HREF="help.html"><FONT FACE="Arial" SIZE=2>HELP! I can\'t hear the music!</FONT></A><BR>\n'
            '<A HREF="merch.html"><FONT FACE="Arial" SIZE=2>Pre-order your Hamster Shuffle merchandise!</FONT></A>'
            '<BR>\n<A HREF="remix.html"><FONT FACE="Arial" SIZE=2>NEW!!! The Turbo Wheel Remix</FONT></A></P>\n'
            '</CENTER>\n%s' % (floor, count, counter_js(1384227), footer()))
    write('index.html', page('The Hamster Shuffle', body, music_js('shuffle.mid')))

    floor2, count2 = dance_floor('remix', rows=30)
    body = ('<CENTER>\n<P><IMG SRC="images/title.gif" WIDTH=460 HEIGHT=56 ALT="THE HAMSTER SHUFFLE"></P>\n'
            '<H2><FONT FACE="Comic Sans MS, Arial" COLOR="#00FFFF"><BLINK>TURBO WHEEL REMIX</BLINK></FONT></H2>\n'
            '<MARQUEE BEHAVIOR=ALTERNATE><FONT FACE="Arial" COLOR="#FFFF00"><B>faster! more hamsters! more '
            'disco!</B></FONT></MARQUEE>\n<P><IMG SRC="images/wheel.gif" WIDTH=64 HEIGHT=64> '
            '<IMG SRC="images/wheel.gif" WIDTH=64 HEIGHT=64> <IMG SRC="images/wheel.gif" WIDTH=64 HEIGHT=64></P>\n'
            '%s\n<P><IMG SRC="images/rainbow.gif" WIDTH=468 HEIGHT=8></P>\n<P><FONT FACE="Arial" SIZE=2 '
            'COLOR="#FFFFFF">%d dancers on the floor tonight. Listen to the <A HREF="midi/shuffle_remix.mid">'
            '<FONT COLOR="#FFFF00">remix</FONT></A> or the <A HREF="midi/shuffle.mid"><FONT COLOR="#FFFF00">'
            'original</FONT></A>.</FONT></P>\n</CENTER>\n%s' % (
                floor2.replace('hammy.gif', 'disco.gif'), count2,
                footer().replace('<FONT FACE="Arial" SIZE=1>', '<FONT FACE="Arial" SIZE=1 COLOR="#FFFFFF">')))
    write('remix.html', page('Hamster Shuffle - Turbo Wheel Remix', body, music_js('shuffle_remix.mid'),
                             bg='#000033').replace('LINK="#0000FF" VLINK="#551A8B"', 'LINK="#FF66FF" VLINK="#CC99FF"'))

    dancers = [('hammy.gif', 60, 70, 'Hammy', 'The founder. Shuffles left, shuffles right, never misses a beat. '
                                               'Favorite food: sunflower seeds. Favorite move: the Hammy Hop.'),
               ('trio.gif', 144, 48, 'The Cheek Sisters', 'Peanut, Pickle and Pumpernickel. Trained in kick-line '
                                                          'at the Cage Academy of Dance. They do not take requests.'),
               ('gerbil.gif', 60, 70, 'Gerty the Gerbil', 'Technically not a hamster. Nobody had the heart to tell '
                                                          'her. Hops higher than anybody.'),
               ('moonwalk.gif', 53, 74, 'Moonwalk Mike', 'Wears a tiny hat. Glides backwards. Has a mysterious past.'),
               ('guinea.gif', 64, 56, 'Pip', 'A guinea pig who "popcorns" (that is a real guinea pig thing, look it '
                                             'up) whenever the beat drops.'),
               ('mouse.gif', 48, 60, 'Twisty', 'A mouse who learned the twist from a 1962 record and never stopped.'),
               ('disco.gif', 60, 70, 'Disco Duke', 'Sunglasses indoors. Points at the sky. Only comes out for the '
                                                   'Turbo Wheel Remix (and sometimes the fan club party).'),
               ('wheel.gif', 64, 64, 'The Wheel', 'Where everybody warms up. Squeaks a little. We are working on it.')]
    body = '<CENTER><H1><FONT FACE="Arial Black, Arial" COLOR="#FF0080">Meet The Dancers!</FONT></H1></CENTER>\n'
    body += '<CENTER><TABLE WIDTH=600 BORDER=0 CELLPADDING=8>\n'
    for i, (im, w, h, name, txt) in enumerate(dancers):
        body += ('<TR VALIGN=MIDDLE BGCOLOR="%s"><TD ALIGN=CENTER WIDTH=160><IMG SRC="images/%s" WIDTH=%d HEIGHT=%d '
                 'ALT="%s"></TD><TD><FONT FACE="Comic Sans MS, Arial" SIZE=3><B>%s</B><BR>%s</FONT></TD></TR>\n' % (
                     '#FFFFCC' if i % 2 == 0 else '#E6F7FF', im, w, h, name, name, txt))
    body += '</TABLE></CENTER>\n' + footer()
    write('dancers.html', page('Hamster Shuffle - Meet the Dancers', body, music_js('shuffle.mid')))

    # fan club guestbook
    rr = random.Random('fanclub')
    entries = []
    for i in range(36):
        y = rr.choice([1998, 1999, 1999])
        m = rr.randint(9 if y == 1998 else 1, 12 if y == 1998 else 10)
        entries.append(((y, m, rr.randint(1, 28)), rr.choice(GB_NAMES), rr.choice(GB_TEXT),
                        rr.choice(['Toledo, OH', 'Fresno, CA', 'Leeds, England', 'Tulsa, OK', 'Halifax, NS',
                                   'Brisbane, Australia', 'Oslo, Norway', 'Duluth, MN', 'Boise, ID', 'Macon, GA'])))
    entries.sort(reverse=True)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    body = ('<CENTER><P><IMG SRC="images/trio.gif" WIDTH=144 HEIGHT=48> <IMG SRC="images/trio.gif" WIDTH=144 HEIGHT=48>'
            '</P><H1><FONT FACE="Arial Black, Arial" COLOR="#FF0080">The Hamster Shuffle Fan Club</FONT></H1>\n'
            '<P><FONT FACE="Arial" SIZE=2>Official members: %d (and every one of them is a little bit dizzy)<BR>\n'
            '<A HREF="#join">Sign the guestbook and join the club!</A></FONT></P></CENTER>\n' % (12000 + len(entries)))
    body += '<CENTER><TABLE WIDTH=600 BORDER=0 CELLPADDING=0>\n'
    for (y, m, d), nm, txt, where in entries:
        body += ('<TR><TD><TABLE WIDTH="100%%" BORDER=1 CELLPADDING=6 CELLSPACING=0 BGCOLOR="#FFF0F8"><TR><TD>'
                 '<FONT FACE="Arial" SIZE=2><B>%s</B> from %s - %s %d, %d<BR>%s</FONT></TD></TR></TABLE><BR></TD></TR>\n'
                 % (nm, where, months[m - 1], d, y, txt))
    body += '</TABLE></CENTER>\n'
    body += ('<A NAME="join"></A><CENTER><TABLE BORDER=3 CELLPADDING=8 BGCOLOR="#FFFFCC"><TR><TD>\n'
             '<FORM NAME="club" ACTION="thanks.html" METHOD="GET">\n<INPUT TYPE="hidden" NAME="form" VALUE="fanclub">\n'
             '<FONT FACE="Arial" SIZE=2><B>Join the Fan Club!</B><BR><BR>\nYour name: <INPUT TYPE="text" NAME="name" '
             'SIZE=25><BR>\nWhere are you from? <INPUT TYPE="text" NAME="from" SIZE=20><BR>\nFavorite dancer: '
             '<SELECT NAME="fave"><OPTION>Hammy<OPTION>The Cheek Sisters<OPTION>Gerty the Gerbil<OPTION>Moonwalk Mike'
             '<OPTION>Pip<OPTION>Twisty<OPTION>Disco Duke</SELECT><BR>\nYour message:<BR><TEXTAREA NAME="msg" ROWS=4 '
             'COLS=40 WRAP=VIRTUAL></TEXTAREA><BR>\n<INPUT TYPE="checkbox" NAME="newsletter" CHECKED> Send me the '
             'Hamster Shuffle newsletter (whenever we remember to write one)<BR><BR>\n'
             '<INPUT TYPE="submit" VALUE="Join The Club!"> <INPUT TYPE="reset" VALUE="Start Over"></FONT>\n'
             '</FORM></TD></TR></TABLE></CENTER>\n')
    body += footer()
    write('fanclub.html', page('Hamster Shuffle Fan Club Guestbook', body, music_js('shuffle.mid')))

    body = ('<CENTER><P><IMG SRC="images/hammy.gif" WIDTH=60 HEIGHT=70> <IMG SRC="images/disco.gif" WIDTH=60 HEIGHT=70>'
            ' <IMG SRC="images/hammy.gif" WIDTH=60 HEIGHT=70></P>\n<H1><FONT FACE="Arial Black, Arial" '
            'COLOR="#FF0080">Thank You!</FONT></H1>\n<P><FONT FACE="Arial" SIZE=3>\n'
            '<SCRIPT LANGUAGE="JavaScript">\n<!--\nvar s = location.search.substring(1), nm = "", form = "";\n'
            'var parts = s.split("&");\nfor (var i = 0; i < parts.length; i++) {\n  var kv = parts[i].split("=");\n'
            '  if (kv.length > 1 && kv[0] == "name") nm = unescape(kv[1].replace(/\\+/g, " "));\n'
            '  if (kv.length > 1 && kv[0] == "form") form = kv[1];\n}\n'
            'nm = nm.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");\n'
            'if (form == "friend") document.write("Your friend has been notified. They will thank you later. Or they '
            'will not. Either way, they will be humming.");\n'
            'else document.write("Welcome to the club" + (nm != "" ? ", <B>" + nm + "</B>" : "") + "! Your membership '
            'card is in the mail (it is a picture of a hamster).");\n//-->\n</SCRIPT>\n'
            '<NOSCRIPT>Thanks! You are officially part of the shuffle.</NOSCRIPT>\n</FONT></P>\n'
            '<P><FONT FACE="Arial" SIZE=2><A HREF="index.html">Back to the dance floor</A></FONT></P>\n'
            '<P><IMG SRC="images/award_hamsterific.gif" WIDTH=100 HEIGHT=100></P></CENTER>\n' + footer())
    write('thanks.html', page('Thanks! - The Hamster Shuffle', body))

    subject = 'You HAVE to see this'
    msg = 'Dancing hamsters. That is it. That is the whole website. Turn your speakers up!'
    body = ('<CENTER><P><IMG SRC="images/trio.gif" WIDTH=144 HEIGHT=48></P>\n<H1><FONT FACE="Arial Black, Arial" '
            'COLOR="#0066FF">Tell A Friend!</FONT></H1>\n<P><FONT FACE="Arial" SIZE=2>Spread the shuffle! Fill this '
            'in and we will open an e-mail to your friend for you.</FONT></P>\n'
            '<TABLE BORDER=3 CELLPADDING=8 BGCOLOR="#E6F7FF"><TR><TD>\n'
            '<FORM NAME="friend" ACTION="thanks.html" METHOD="GET" onSubmit="return tell();">\n'
            '<INPUT TYPE="hidden" NAME="form" VALUE="friend">\n<FONT FACE="Arial" SIZE=2>Your name: <INPUT TYPE="text" '
            'NAME="from" SIZE=25><BR>\nYour friend\'s e-mail: <INPUT TYPE="text" NAME="to" SIZE=25><BR>\n'
            'Message:<BR><TEXTAREA NAME="msg" ROWS=4 COLS=40 WRAP=VIRTUAL>%s</TEXTAREA><BR>\n'
            '<INPUT TYPE="submit" VALUE="Send it!"></FONT>\n</FORM></TD></TR></TABLE>\n'
            '<SCRIPT LANGUAGE="JavaScript">\n<!--\nfunction tell() {\n  var f = document.forms["friend"];\n'
            '  if (f.to.value.indexOf("@") < 0) { alert("Please type your friend\'s e-mail address!"); return false; }\n'
            '  var url = location.href.substring(0, location.href.lastIndexOf("/") + 1) + "index.html";\n'
            '  var body = f.msg.value + "\\n\\n" + url + "\\n\\n-- " + f.from.value;\n'
            '  location.href = "mailto:" + f.to.value + "?subject=" + escape("%s") + "&body=" + escape(body);\n'
            '  setTimeout("location.href = \'thanks.html?form=friend\'", 1500);\n  return false;\n}\n//-->\n'
            '</SCRIPT>\n<P><FONT FACE="Arial" SIZE=2>No JavaScript? Just <A HREF="mailto:?subject=You%%20HAVE%%20to%%20see'
            '%%20this&amp;body=Dancing%%20hamsters.%%20Turn%%20your%%20speakers%%20up!">click here to e-mail a friend</A>.'
            '</FONT></P>\n<P><IMG SRC="images/mouse.gif" WIDTH=48 HEIGHT=60> <IMG SRC="images/guinea.gif" WIDTH=64 '
            'HEIGHT=56> <IMG SRC="images/mouse.gif" WIDTH=48 HEIGHT=60></P></CENTER>\n' % (msg, subject))
    body += footer()
    write('tellafriend.html', page('Tell a Friend about the Hamster Shuffle', body))

    body = ('<CENTER><H1><FONT FACE="Arial Black, Arial" COLOR="#FF6600">HELP! I Can\'t Hear The Music!</FONT></H1>'
            '<P><IMG SRC="images/hammy.gif" WIDTH=60 HEIGHT=70></P></CENTER>\n'
            '<CENTER><TABLE WIDTH=560><TR><TD><FONT FACE="Arial" SIZE=3>\n<P>Don\'t panic! The hamsters are dancing to '
            'a little MIDI tune. Try these:</P>\n<OL>\n<LI>Turn on your speakers. Turn them UP.\n'
            '<LI>Check that your sound card works (does your computer go "ta-da" when it starts?).\n'
            '<LI>Pioneer Navigator users: you need a MIDI plug-in. Explor-o-Matic users: it should just work.\n'
            '<LI>Wait for the page to finish loading. There are a LOT of hamsters.\n'
            '<LI>Still nothing? <A HREF="midi/shuffle.mid">Click here to play the song directly</A>.\n'
            '<LI>Hum along. That is what the hamsters do.\n</OL>\n'
            '<P>Want it louder at work? We cannot help you with that. Please think of your coworkers.</P>\n'
            '</FONT></TD></TR></TABLE></CENTER>\n' + footer())
    write('help.html', page('Hamster Shuffle - Help', body))

    items = [('merch_shirt.gif', 'Official Hamster Shuffle T-Shirt', '$14.99', 'Glow-in-the-dark hamster! Sizes S-XL.'),
             ('merch_mousepad.gif', 'Dance Floor Mouse Pad', '$7.99', 'Your mouse will want to dance too.'),
             ('merch_mug.gif', 'Disco Duke Coffee Mug', '$9.99', 'Holds 12 oz. of coffee or 4,000 sunflower seeds.')]
    body = ('<CENTER><H1><FONT FACE="Arial Black, Arial" COLOR="#FF0080">Hamster Shuffle Merchandise</FONT></H1>\n'
            '<P><FONT FACE="Arial" SIZE=2><BLINK><B>PRE-ORDER NOW!</B></BLINK> Ships in time for the holidays '
            '(holidays not specified).</FONT></P>\n<TABLE WIDTH=600 BORDER=1 CELLPADDING=8 CELLSPACING=0>\n')
    for im, name, price, txt in items:
        body += ('<TR><TD ALIGN=CENTER><IMG SRC="images/%s" ALT="%s"></TD><TD><FONT FACE="Arial" SIZE=2><B>%s</B><BR>'
                 '%s<BR><FONT COLOR="#CC0000"><B>%s</B></FONT><BR><FORM ACTION="thanks.html" METHOD="GET" '
                 'onSubmit="alert(\'Thanks for your pre-order! We will e-mail you when the hamsters finish knitting '
                 'it.\'); return false;"><INPUT TYPE="submit" VALUE="Pre-Order"></FORM></FONT></TD></TR>\n' % (
                     im, name, name, txt, price))
    body += '</TABLE></CENTER>\n'
    body += ('<CENTER><P><FONT FACE="Arial" SIZE=2>Also coming soon: the Hamster Shuffle CD single, the plush Hammy, '
             'and a screensaver for Panes 95/98.</FONT></P>\n<P><IMG SRC="images/award_annoying.gif" WIDTH=100 '
             'HEIGHT=100> <IMG SRC="images/award_stuck.gif" WIDTH=100 HEIGHT=100> <IMG SRC="images/award_hamsterific.gif"'
             ' WIDTH=100 HEIGHT=100></P><P><FONT FACE="Arial" SIZE=1>Link to us! <IMG SRC="images/hamster_88.gif" '
             'WIDTH=88 HEIGHT=31 ALIGN=ABSMIDDLE></FONT></P></CENTER>\n' + footer())
    write('merch.html', page('Hamster Shuffle Merchandise', body))

    write('images/index.html', page('images', '<P><FONT FACE="Arial" SIZE=2>Nothing to see here but hamsters. '
                                              '<A HREF="../index.html">Go dance!</A></FONT></P>'))
    write('midi/index.html', page('midi', '<P><FONT FACE="Arial" SIZE=2><A HREF="shuffle.mid">shuffle.mid</A> | '
                                          '<A HREF="shuffle_remix.mid">shuffle_remix.mid</A> | <A HREF="../index.html">'
                                          'Back to the dance floor</A></FONT></P>'))
    write('tools/index.html', page('tools', '<P><IMG SRC="../images/wheel.gif" WIDTH=64 HEIGHT=64> <FONT FACE="Arial" '
                                            'SIZE=2>Backstage. Hamsters only. <A HREF="../index.html">Back</A></FONT>'
                                            '</P>'))
    return count


def main():
    draw_gifs()
    make_midis()
    n = make_pages()
    files = sum(len(f) for _d, _s, f in os.walk(SITE))
    size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _s, fs in os.walk(SITE) for f in fs)
    print('Hamster Shuffle: %d dancers on the floor, %d files, %d KB' % (n, files, size // 1024))


if __name__ == '__main__':
    main()
