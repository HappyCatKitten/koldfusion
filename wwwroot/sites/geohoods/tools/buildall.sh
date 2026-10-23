#!/bin/sh
# Rebuild the whole GeoHoods site (graphics, MIDI, ~250 homepages, portal) and check every link.
cd "$(dirname "$0")" || exit 1
python3 mkgfx.py && python3 mkmidi.py && python3 mkhomepages.py && python3 linkcheck.py
