#!/usr/bin/env python3
"""Tiny Standard MIDI File writer + the original Petz.com jingle ("Argyle's Song").

midi.write(path) writes a format-0 file: melody on a piano-ish voice, bass and a little percussion.
"""
import struct

def vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(out)

NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
def pitch(name):
    n, octv = name[:-1], int(name[-1])
    v = NOTE[n[0]] + (1 if "#" in n else 0) - (1 if n.endswith("b") and len(n) > 1 else 0)
    return 12 * (octv + 1) + v

TPQ = 240
# Original melody (note, beats).  Bouncy 4/4 in F major, two phrases plus a tag.
MELODY = [
    ("C5", .5), ("A4", .5), ("F4", .5), ("A4", .5), ("C5", 1), ("D5", .5), ("C5", .5),
    ("A#4", .5), ("G4", .5), ("E4", .5), ("G4", .5), ("A#4", 1.5), ("R", .5),
    ("A4", .5), ("F4", .5), ("A4", .5), ("C5", .5), ("F5", 1), ("E5", .5), ("D5", .5),
    ("C5", .5), ("A#4", .5), ("G4", .5), ("E4", .5), ("F4", 1.5), ("R", .5),
    # tag: "pets can't drive!"
    ("F5", .25), ("F5", .25), ("E5", .5), ("C5", .5), ("D5", 1), ("C5", 1), ("F4", 1.5), ("R", .5),
]
BASS = [("F2", 2), ("F2", 2), ("C3", 2), ("C3", 2), ("F2", 2), ("A#2", 2), ("C3", 2), ("F2", 2),
        ("A#2", 2), ("C3", 2), ("F2", 2)]

def events():
    ev = []  # (tick, order, bytes)
    t = 0
    for n, b in MELODY:
        d = int(b * TPQ)
        if n != "R":
            ev.append((t, 1, bytes([0x90, pitch(n), 100])))
            ev.append((t + d - 10, 0, bytes([0x80, pitch(n), 0])))
        t += d
    total = t
    t = 0
    for n, b in BASS:
        d = int(b * TPQ)
        for half in (0, d // 2):
            ev.append((t + half, 1, bytes([0x91, pitch(n), 90])))
            ev.append((t + half + d // 2 - 20, 0, bytes([0x81, pitch(n), 0])))
        t += d
    t = 0
    while t < total - TPQ:
        ev.append((t, 1, bytes([0x99, 36 if (t // TPQ) % 2 == 0 else 38, 80])))
        ev.append((t + 60, 0, bytes([0x89, 36 if (t // TPQ) % 2 == 0 else 38, 0])))
        ev.append((t + TPQ // 2, 1, bytes([0x99, 42, 50])))
        ev.append((t + TPQ // 2 + 40, 0, bytes([0x89, 42, 0])))
        t += TPQ
    ev.sort(key=lambda e: (e[0], e[1]))
    return ev

def write(path):
    trk = bytearray()
    trk += vlq(0) + b"\xFF\x03" + vlq(13) + b"Argyle's Song"
    trk += vlq(0) + b"\xFF\x51\x03" + struct.pack(">I", 500000)[1:]   # 120 bpm
    trk += vlq(0) + b"\xFF\x58\x04\x04\x02\x18\x08"
    trk += vlq(0) + bytes([0xC0, 1])     # bright acoustic piano
    trk += vlq(0) + bytes([0xC1, 33])    # finger bass
    last = 0
    for t, _, b in events():
        trk += vlq(t - last) + b
        last = t
    trk += vlq(TPQ) + b"\xFF\x2F\x00"
    with open(path, "wb") as f:
        f.write(b"MThd" + struct.pack(">IHHH", 6, 0, 1, TPQ))
        f.write(b"MTrk" + struct.pack(">I", len(trk)) + bytes(trk))

if __name__ == "__main__":
    import sys
    write(sys.argv[1] if len(sys.argv) > 1 else "jingle.mid")
