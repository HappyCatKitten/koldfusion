#!/usr/bin/env python3
"""Extra Administrator artwork: the 1-px teal/sage pinstripe tiles and the
login-page swoosh, reproduced from the colours of the 4.x originals."""
import os
from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(__file__), '..', 'wwwroot')
ADM = os.path.join(ROOT, 'CFIDE', 'administrator', 'images')
IMG = os.path.join(ROOT, 'images')
TEAL, SAGE, NAVY = (0x00, 0x66, 0x99), (0x99, 0xCC, 0x99), (0x33, 0x33, 0x99)

def save(im, path):
    im.convert('P', palette=Image.ADAPTIVE, colors=32).save(path)

def pinstripe(w, h):
    im = Image.new('RGB', (w, h), SAGE)
    d = ImageDraw.Draw(im)
    for y in range(0, h, 2):
        d.line([(0, y), (w, y)], fill=TEAL)
    return im

os.makedirs(ADM, exist_ok=True); os.makedirs(IMG, exist_ok=True)
save(pinstripe(4, 4), os.path.join(ADM, 'pinstripe.gif'))
save(pinstripe(191, 4), os.path.join(IMG, 'bgblue.gif'))

# admin page body: 121px pinstripe, dark rule, light-blue rule, then white
im = Image.new('RGB', (200, 4), (255, 255, 255))
im.paste(pinstripe(121, 4), (0, 0))
d = ImageDraw.Draw(im)
d.line([(121, 0), (121, 3)], fill=(0x33, 0x00, 0x33))
d.line([(122, 0), (122, 3)], fill=(0x00, 0x99, 0xCC))
save(im, os.path.join(ADM, 'leftbgblue.gif'))

# login swoosh: a big navy curve filling the right of the login card
W, H = 260, 400
im = Image.new('RGB', (W, H), (255, 255, 255))
d = ImageDraw.Draw(im)
d.ellipse([60, -260, W + 520, H + 260], fill=NAVY)
d.ellipse([120, -200, W + 560, H + 200], fill=(0x40, 0x40, 0xAA))
d.ellipse([170, -150, W + 600, H + 150], fill=NAVY)
save(im, os.path.join(ADM, 'swoosh.gif'))
print('admin graphics written')

# welcome page logo, 400x105: the admin logo plus a big "4.5" and tagline
from PIL import ImageFont
def font(names, size):
    for n in names:
        for d in ('/usr/share/fonts/truetype/liberation', '/usr/share/fonts/truetype/liberation2', '/usr/share/fonts/truetype/dejavu'):
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()
logo = Image.open(os.path.join(ADM, 'kf_logo.gif')).convert('RGB')
im = Image.new('RGB', (400, 105), (255, 255, 255))
im.paste(logo, (8, 8))
d = ImageDraw.Draw(im)
big = font(['LiberationSans-BoldItalic.ttf', 'DejaVuSans-BoldOblique.ttf'], 44)
d.text((222, 18), '4.5', font=big, fill=(0x1E, 0x55, 0x10))
d.text((220, 16), '4.5', font=big, fill=(0x46, 0x93, 0x20))
small = font(['LiberationSans-Bold.ttf', 'DejaVuSans-Bold.ttf'], 13)
d.text((60, 82), 'w e b   a p p l i c a t i o n   s e r v e r', font=small, fill=(0x2D, 0x44, 0x92))
save(im, os.path.join(IMG, 'welcome_logo.gif'))
print('welcome logo written')
