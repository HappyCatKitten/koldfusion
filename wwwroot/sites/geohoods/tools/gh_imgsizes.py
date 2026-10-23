"""gh_imgsizes.py -- WIDTH/HEIGHT of every GIF in ../images (read once at import)."""
import os

from PIL import Image

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images')
SIZES = {}
for _f in os.listdir(_DIR):
    if _f.lower().endswith('.gif'):
        with Image.open(os.path.join(_DIR, _f)) as _im:
            SIZES[_f] = _im.size
