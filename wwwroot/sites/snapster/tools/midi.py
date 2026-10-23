#!/usr/bin/env python3
"""Tiny Standard MIDI File writer + the original 4-bar "Snapster startup jingle".
Called by gen.py; can also be run alone:  python3 tools/midi.py  -> jingle.mid"""
import os, struct


def vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(out)


def write_midi(path, notes, tempo_bpm=132, tpq=96):
    """notes: list of (start_tick, length_ticks, channel, pitch, velocity)"""
    ev = []
    for st, ln, ch, p, v in notes:
        ev.append((st, 1, bytes([0x90 | ch, p, v])))
        ev.append((st + ln, 0, bytes([0x80 | ch, p, 0])))
    ev.sort(key=lambda e: (e[0], e[1]))
    trk = bytearray()
    trk += vlq(0) + b'\xFF\x51\x03' + struct.pack('>I', int(60000000 / tempo_bpm))[1:]
    trk += vlq(0) + b'\xFF\x03' + vlq(len(b'Snapster jingle')) + b'Snapster jingle'
    trk += vlq(0) + bytes([0xC0, 81])   # ch0: square lead
    trk += vlq(0) + bytes([0xC1, 38])   # ch1: synth bass
    t = 0
    for st, _, data in ev:
        trk += vlq(st - t) + data
        t = st
    trk += vlq(0) + b'\xFF\x2F\x00'
    with open(path, 'wb') as f:
        f.write(b'MThd' + struct.pack('>IHHH', 6, 0, 1, tpq))
        f.write(b'MTrk' + struct.pack('>I', len(trk)) + bytes(trk))


def jingle(path):
    q = 96
    e = q // 2
    # an original little hook: "snap-snap, da-da-dah" twice, then a rising tag
    lead = [(0, e, 72), (e, e, 72), (2 * e, q, 79), (4 * e, e, 77), (5 * e, e, 76), (6 * e, q, 74),
            (4 * q, e, 72), (4 * q + e, e, 72), (4 * q + 2 * e, q, 79), (4 * q + 4 * e, e, 81),
            (4 * q + 5 * e, e, 79), (4 * q + 6 * e, q, 77),
            (8 * q, e, 76), (8 * q + e, e, 77), (8 * q + 2 * e, e, 79), (8 * q + 3 * e, e, 81),
            (8 * q + 4 * e, q, 84), (8 * q + 6 * e, e, 79), (8 * q + 7 * e, e, 81),
            (12 * q, 3 * q, 84)]
    bass = [(0, q, 48), (q, q, 48), (2 * q, q, 55), (3 * q, q, 55), (4 * q, q, 53), (5 * q, q, 53),
            (6 * q, q, 55), (7 * q, q, 55), (8 * q, q, 57), (9 * q, q, 53), (10 * q, q, 55), (11 * q, q, 55),
            (12 * q, 3 * q, 48)]
    notes = [(s, l - 4, 0, p, 100) for s, l, p in lead] + [(s, l - 4, 1, p, 90) for s, l, p in bass]
    write_midi(path, notes)


if __name__ == '__main__':
    jingle(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'jingle.mid'))
