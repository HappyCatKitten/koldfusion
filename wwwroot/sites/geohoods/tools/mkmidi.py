#!/usr/bin/env python3
"""mkmidi.py -- compose the GeoHoods background MIDI files (all original, generated from a seed).

Each tune is a little AABA song: a chord progression, a seeded melody that leans on chord tones,
an optional bass line and an optional drum groove, written as a Standard MIDI File (type 1).

Usage:  python3 tools/mkmidi.py     (writes into ../midi/)
"""
import os
import random
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'midi')
TPQ = 96   # ticks per quarter note


def vlq(n):
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(out))


def track(events, name=None):
    """events: list of (tick, bytes); returns MTrk chunk"""
    evs = []
    if name:
        nb = name.encode('latin-1')
        evs.append((0, b'\xff\x03' + vlq(len(nb)) + nb))
    evs += sorted(events, key=lambda e: (e[0], 0 if e[1][0] & 0xF0 == 0x80 else 1))
    data = b''
    last = 0
    for t, b in evs:
        data += vlq(t - last) + b
        last = t
    data += vlq(0) + b'\xff\x2f\x00'
    return b'MTrk' + struct.pack('>I', len(data)) + data


def write_midi(path, tracks):
    hdr = b'MThd' + struct.pack('>IHHH', 6, 1, len(tracks), TPQ)
    with open(path, 'wb') as f:
        f.write(hdr + b''.join(tracks))


def note(evs, ch, t, dur, pitch, vel=96):
    evs.append((t, bytes([0x90 | ch, pitch, vel])))
    evs.append((t + max(1, dur - 4), bytes([0x80 | ch, pitch, 0])))


SCALES = {'major': [0, 2, 4, 5, 7, 9, 11], 'minor': [0, 2, 3, 5, 7, 8, 10], 'dorian': [0, 2, 3, 5, 7, 9, 10],
          'mixo': [0, 2, 4, 5, 7, 9, 10], 'harm': [0, 2, 3, 5, 7, 8, 11]}

# rhythm cells in eighths (lengths summing to 8 per bar)
RHYTHMS = {
    'straight': [[2, 2, 2, 2], [2, 1, 1, 2, 2], [1, 1, 2, 2, 2], [2, 2, 4], [3, 1, 2, 2]],
    'waltz': [[2, 2, 2], [4, 2], [2, 1, 1, 2], [6]],
    'busy': [[1, 1, 1, 1, 1, 1, 2], [1, 1, 2, 1, 1, 2], [2, 1, 1, 1, 1, 2], [1, 1, 1, 1, 2, 2]],
    'slow': [[4, 4], [6, 2], [8], [2, 2, 4]],
}


def compose(name, title, key=60, scale='major', bpm=110, prog=None, mel_prog=0, bass_prog=33, drums='rock',
            rhythm='straight', beats=4, seed=None, octave=12, chord_prog=None, pad_prog=None, bars_per=4):
    rr = random.Random(seed or name)
    sc = SCALES[scale]
    prog = prog or [0, 5, 3, 4]       # scale degrees of chords (I vi IV V)
    bar = TPQ * beats
    eighth = TPQ // 2

    def deg_pitch(deg, base):
        o, d = divmod(deg, 7)
        return base + 12 * o + sc[d]

    def phrase(seedoff):
        r2 = random.Random((seed or name) + str(seedoff))
        notes = []
        cur = 7 + r2.randint(0, 4)
        for b in range(bars_per):
            chord = prog[b % len(prog)]
            cell = r2.choice(RHYTHMS[rhythm])
            for i, ln in enumerate(cell):
                tones = [chord, chord + 2, chord + 4, chord + 7]
                if i == 0 or r2.random() < 0.5:
                    target = min(tones + [t - 7 for t in tones] + [t + 7 for t in tones], key=lambda t: abs(t - cur) + r2.random() * 2)
                else:
                    target = cur + r2.choice([-1, 1, -2, 2, 0])
                cur = max(2, min(14, target))
                notes.append((ln, cur))
        # end on the tonic
        ln, _ = notes[-1]
        notes[-1] = (ln, 7)
        return notes

    A = phrase('A')
    A2 = A[:-3] + phrase('A2')[-3:]
    B = phrase('B')
    form = [A, A2, B, A]
    mel, bass, drm, pad = [], [], [], []
    t = 0
    for sec, ph in enumerate(form):
        start = t
        for ln, deg in ph:
            p = deg_pitch(deg, key + octave - 12)
            note(mel, 0, t, ln * eighth, p, 100 if ln > 1 else 88)
            t += ln * eighth
        # bass + pad per bar
        for b in range(bars_per):
            chord = prog[b % len(prog)] if sec != 2 else prog[(b + 2) % len(prog)]
            root = deg_pitch(chord, key - 24)
            bt = start + b * bar
            if rhythm == 'waltz':
                note(bass, 1, bt, TPQ, root, 90)
                for k in (1, 2):
                    for dd in (2, 4):
                        note(bass, 1, bt + k * TPQ, TPQ, deg_pitch(chord + dd, key - 12), 60)
            elif rhythm == 'slow':
                note(bass, 1, bt, bar, root, 80)
            else:
                for k in range(beats):
                    p = root if k % 2 == 0 else deg_pitch(chord + 4, key - 24)
                    note(bass, 1, bt + k * TPQ, TPQ, p, 90)
            if pad_prog is not None:
                for dd in (0, 2, 4):
                    note(pad, 3, bt, bar, deg_pitch(chord + dd, key - 12), 55)
            if drums == 'rock':
                for k in range(beats):
                    note(drm, 9, bt + k * TPQ, eighth, 36 if k % 2 == 0 else 38, 100)
                    note(drm, 9, bt + k * TPQ, eighth, 42, 70)
                    note(drm, 9, bt + k * TPQ + eighth, eighth, 42, 55)
            elif drums == 'disco':
                for k in range(beats):
                    note(drm, 9, bt + k * TPQ, eighth, 36, 110)
                    note(drm, 9, bt + k * TPQ + eighth, eighth, 46, 70)
                    if k % 2:
                        note(drm, 9, bt + k * TPQ, eighth, 39, 90)
            elif drums == 'march':
                for k in range(beats):
                    note(drm, 9, bt + k * TPQ, eighth, 38, 100 if k == 0 else 70)
                    note(drm, 9, bt + k * TPQ + eighth, eighth // 2, 38, 50)
                note(drm, 9, bt, eighth, 36, 110)
            elif drums == 'waltz':
                note(drm, 9, bt, eighth, 36, 90)
                note(drm, 9, bt + TPQ, eighth, 42, 60)
                note(drm, 9, bt + 2 * TPQ, eighth, 42, 60)
        t = start + bars_per * bar
    # final chord
    for dd in (0, 2, 4, 7):
        note(mel, 0, t, bar, deg_pitch(dd, key), 90)
    note(bass, 1, t, bar, key - 24, 90)
    tempo = 60000000 // bpm
    meta = [(0, b'\xff\x51\x03' + struct.pack('>I', tempo)[1:]),
            (0, b'\xff\x58\x04' + bytes([beats, 2, 24, 8]))]
    tracks = [track(meta, title)]
    tracks.append(track([(0, bytes([0xC0, mel_prog]))] + mel, 'Melody'))
    tracks.append(track([(0, bytes([0xC1, bass_prog]))] + bass, 'Bass'))
    if pad_prog is not None:
        tracks.append(track([(0, bytes([0xC3, pad_prog]))] + pad, 'Pad'))
    if drums:
        tracks.append(track(drm, 'Drums'))
    write_midi(os.path.join(OUT, name + '.mid'), tracks)


TUNES = [
    # name, title, kwargs
    ('starfield', 'Starfield Drift', dict(key=62, scale='dorian', bpm=96, mel_prog=81, bass_prog=38, drums=None,
                                          pad_prog=89, rhythm='busy', prog=[0, 6, 5, 6])),
    ('kitten_waltz', 'Kitten Waltz', dict(key=65, scale='major', bpm=150, mel_prog=10, bass_prog=0, drums=None,
                                          rhythm='waltz', beats=3, prog=[0, 3, 4, 0])),
    ('heartthrob', 'Heartthrob Ballad', dict(key=64, scale='major', bpm=76, mel_prog=73, bass_prog=33, drums='rock',
                                             pad_prog=48, rhythm='slow', prog=[0, 5, 3, 4])),
    ('y2k_march', 'Countdown March', dict(key=58, scale='major', bpm=118, mel_prog=56, bass_prog=58, drums='march',
                                          prog=[0, 4, 0, 4])),
    ('lullaby', 'Porch Light Lullaby', dict(key=67, scale='major', bpm=70, mel_prog=10, bass_prog=0, drums=None,
                                            rhythm='waltz', beats=3, prog=[0, 3, 0, 4])),
    ('hoedown', 'Skillet Hoedown', dict(key=62, scale='mixo', bpm=150, mel_prog=110, bass_prog=32, drums='rock',
                                        rhythm='busy', prog=[0, 0, 3, 4])),
    ('fight_song', 'Gridiron Fight Song', dict(key=60, scale='major', bpm=132, mel_prog=61, bass_prog=58,
                                                drums='march', prog=[0, 3, 4, 0])),
    ('spooky', 'The Murk Theme', dict(key=57, scale='harm', bpm=88, mel_prog=79, bass_prog=39, drums=None,
                                      pad_prog=91, rhythm='slow', prog=[0, 5, 3, 4])),
    ('techno', 'Modem Rave', dict(key=57, scale='minor', bpm=136, mel_prog=80, bass_prog=38, drums='disco',
                                  rhythm='busy', prog=[0, 5, 6, 4])),
    ('elevator', 'Lobby Bossa', dict(key=65, scale='major', bpm=104, mel_prog=11, bass_prog=32, drums='rock',
                                     pad_prog=4, prog=[1, 4, 0, 5])),
    ('holiday', 'Sleigh Bells on the Modem', dict(key=67, scale='major', bpm=140, mel_prog=9, bass_prog=33,
                                                  drums='rock', prog=[0, 3, 0, 4])),
    ('ragtime', 'Attic Rag', dict(key=60, scale='major', bpm=120, mel_prog=0, bass_prog=0, drums=None,
                                  rhythm='busy', prog=[0, 5, 1, 4])),
    ('anthem', 'Homesteader Anthem', dict(key=60, scale='major', bpm=90, mel_prog=60, bass_prog=57, drums='march',
                                          pad_prog=48, rhythm='slow', prog=[0, 3, 4, 0])),
    ('chiptune', 'Insert Coin', dict(key=64, scale='minor', bpm=150, mel_prog=80, bass_prog=81, drums='disco',
                                     rhythm='busy', prog=[0, 5, 2, 6])),
    ('memorial', 'Over the Rainbow Fields', dict(key=63, scale='major', bpm=64, mel_prog=19, bass_prog=19,
                                                 drums=None, pad_prog=52, rhythm='slow', prog=[0, 3, 0, 4])),
    ('surf', 'Boardwalk Stomp', dict(key=64, scale='mixo', bpm=160, mel_prog=27, bass_prog=34, drums='rock',
                                     rhythm='busy', prog=[0, 3, 0, 4])),
    ('punk', 'Three Chords and a Modem', dict(key=64, scale='major', bpm=176, mel_prog=30, bass_prog=34,
                                              drums='rock', prog=[0, 3, 4, 3])),
    ('lovesong', 'Sonnet for a Screen Name', dict(key=62, scale='major', bpm=80, mel_prog=1, bass_prog=32,
                                                   drums=None, pad_prog=49, rhythm='slow', prog=[0, 2, 3, 4])),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, title, kw in TUNES:
        compose(name, title, **kw)
    print('%d MIDI files' % len(TUNES))


if __name__ == '__main__':
    main()
