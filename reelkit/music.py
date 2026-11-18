"""Original background music for Reels, composed in code (copyright-free, free to use).

python music.py <style> <seconds> <out.wav> [seed] [transpose]

Parents styles (cheerful): bright (ukulele + glockenspiel), marimba (tropical), piano (gentle piano + strings),
                           funk (bouncy bass + claps)
PG styles (calm, study):   lofi (e-piano + vinyl), jazzhop (rhodes + walking bass), arp (soft synth arpeggios),
                           studypiano (slow piano + pads)
Every track has sections (intro -> A -> B -> A' -> break -> B' ...), drum fills before each new section,
a melody generated per section (seeded, so each Reel differs) and a key lift in the late chorus,
so it doesn't sound like one loop repeating.
"""
import sys
import wave

import numpy as np

STYLE = sys.argv[1] if len(sys.argv) > 1 else "bright"
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 45
OUT = sys.argv[3] if len(sys.argv) > 3 else "music.wav"
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 0
KEY = int(sys.argv[5]) if len(sys.argv) > 5 else 0
SR = 48000
rng = np.random.default_rng(1000 + SEED * 7 + sum(map(ord, STYLE)))
N = int((DUR + 4) * SR)
L = np.zeros(N)
R = np.zeros(N)

PARENT_STYLES = ["bright", "marimba", "piano", "funk"]
PG_STYLES = ["lofi", "jazzhop", "arp", "studypiano"]


def hz(m):
    return 440 * 2 ** ((m + KEY - 69) / 12)


def tt(d):
    return np.arange(int(max(d, 0.01) * SR)) / SR


def add(start, sig, pan=0.0, gain=1.0):
    i = max(0, int(start * SR))
    if i >= N:
        return
    j = min(N, i + len(sig))
    s = sig[: j - i] * gain
    L[i:j] += s * np.sqrt((1 - pan) / 2)
    R[i:j] += s * np.sqrt((1 + pan) / 2)


def env(t, a=0.005, d=1.0):
    return np.minimum(1, t / a) * np.exp(-t * d)


# ------------------------------------------------------------------ instruments
def pluck(m, d=0.7):
    t, f = tt(d), hz(m)
    return sum((0.8 ** k) * np.sin(2 * np.pi * f * (k + 1) * t) * np.exp(-t * (3 + 6 * k)) for k in range(6)) * np.minimum(1, t / 0.003)


def glock(m, d=1.2):
    t, f = tt(d), hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6) + 0.12 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 10)
    return s * env(t, 0.002, 3.2)


def marimba(m, d=0.6):
    t, f = tt(d), hz(m)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30) + 0.15 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t * 60)) * env(t, 0.001, 7)


def piano(m, d=1.6, bright=1.0):
    t, f = tt(d), hz(m)
    s = sum((0.55 ** k) * np.sin(2 * np.pi * f * (k + 1) * (1 + 0.0004 * k * k) * t) * np.exp(-t * (1.6 + 1.8 * k * bright)) for k in range(7))
    return s * np.minimum(1, t / 0.002) * np.clip((d - t) / 0.25, 0, 1)


def epiano(ms, d):
    t = tt(d + 0.6)
    s = np.zeros(len(t))
    for m in ms:
        f = hz(m)
        s += np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * f * t) * np.exp(-t * 3)) * np.exp(-t * 1.1) * (1 + 0.12 * np.sin(2 * np.pi * 4.5 * t))
    return s / len(ms) * np.minimum(1, t / 0.01) * np.clip((d + 0.6 - t) / 0.5, 0, 1)


def pad(ms, d):
    t = tt(d + 0.8)
    s = np.zeros(len(t))
    for m in ms:
        for det in (-0.12, 0.0, 0.11):
            f = hz(m + 12 + det)
            s += np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t)
    return s / (3 * len(ms)) * np.minimum(1, t / 0.6) * np.clip((d + 0.8 - t) / 0.8, 0, 1)


def synth(m, d=0.25):
    t, f = tt(d), hz(m)
    return sum(np.sin(2 * np.pi * f * k * t) / k for k in (1, 3, 5, 7)) * env(t, 0.003, 9)


def bass(m, d, pluck_like=False):
    t, f = tt(d), hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    if pluck_like:
        s = s + 0.2 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 12)
    return s * np.minimum(1, t / 0.008) * np.clip((d - t) / 0.06, 0, 1) * np.exp(-t * (3.0 if pluck_like else 1.2))


def noise(d, decay, hp=True):
    n = rng.uniform(-1, 1, int(d * SR))
    n = np.diff(n, prepend=0) * 0.6 if hp else np.convolve(n, np.ones(6) / 6, mode="same")
    return n * np.exp(-tt(d) * decay)


def kick_s():
    t = tt(0.35)
    return np.sin(2 * np.pi * (50 * t + 90 / 25 * (1 - np.exp(-t * 25)))) * np.exp(-t * 9)


KICK = kick_s()
SNARE = noise(0.22, 18, False) * 0.9 + 0.4 * np.sin(2 * np.pi * 190 * tt(0.22)) * np.exp(-tt(0.22) * 25)
HAT = noise(0.05, 80)
OPENHAT = noise(0.25, 14)
SHAKER = noise(0.08, 55)
_cl = int(0.2 * SR)
CLAP = sum(np.pad(noise(0.16, 22, False), (int(k * 0.011 * SR), _cl))[:_cl] for k in range(3))
RIM = np.sin(2 * np.pi * 1700 * tt(0.04)) * np.exp(-tt(0.04) * 120)

# ------------------------------------------------------------------ harmony
QUAL = {"maj": [0, 4, 7], "min": [0, 3, 7], "maj7": [0, 4, 7, 11], "min7": [0, 3, 7, 10], "7": [0, 4, 7, 10],
        "min9": [0, 3, 7, 10, 14], "maj9": [0, 4, 7, 11, 14], "sus": [0, 5, 7, 10], "add9": [0, 4, 7, 14]}
NOTE = {"C": 0, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}


def chord(name):
    root, q = name.split(":")
    r = NOTE[root]
    base = 48 + r if 48 + r <= 55 else 36 + r
    return (36 + r if r <= 7 else 24 + r), [base + i for i in QUAL[q]]


STYLES = {
    "bright": dict(bpm=104, scale=[0, 2, 4, 7, 9], A=["C:maj", "G:maj", "A:min", "F:maj"], B=["F:maj", "G:maj", "E:min", "A:min"]),
    "marimba": dict(bpm=112, scale=[0, 2, 4, 7, 9], A=["C:maj", "A:min", "F:maj", "G:maj"], B=["D:min", "G:maj", "C:maj", "A:min"]),
    "piano": dict(bpm=92, scale=[0, 2, 4, 5, 7, 9, 11], A=["C:add9", "E:min", "F:maj7", "G:sus"], B=["A:min", "F:maj", "C:maj", "G:maj"]),
    "funk": dict(bpm=100, scale=[0, 2, 3, 5, 7, 9, 10], A=["A:min7", "D:7", "A:min7", "D:7"], B=["F:maj7", "E:7", "D:min7", "E:7"]),
    "lofi": dict(bpm=84, scale=[0, 2, 4, 7, 9], A=["F:maj7", "E:min7", "D:min9", "G:sus"], B=["Bb:maj7", "A:min7", "D:min7", "G:7"]),
    "jazzhop": dict(bpm=88, scale=[0, 2, 3, 5, 7, 9, 10], A=["D:min9", "G:7", "C:maj9", "A:7"], B=["F:maj7", "E:min7", "D:min7", "G:7"]),
    "arp": dict(bpm=96, scale=[0, 2, 3, 5, 7, 8, 10], A=["A:min", "F:maj", "C:maj", "G:maj"], B=["F:maj", "G:maj", "A:min", "E:min"]),
    "studypiano": dict(bpm=76, scale=[0, 2, 4, 7, 9], A=["C:maj9", "A:min7", "F:maj9", "G:sus"], B=["E:min7", "A:min7", "D:min7", "G:sus"]),
}
S = STYLES.get(STYLE, STYLES["bright"])
BEAT = 60 / S["bpm"]
BAR = BEAT * 4
SWING = 0.06 if STYLE in ("lofi", "jazzhop") else 0.0
SCALE_NOTES = [60 + o * 12 + d for o in range(0, 3) for d in S["scale"]]


def melody_bar(ch, r, density):
    """One bar of melody: chord tones on the beat, scale steps between."""
    pool = sorted({n + 12 * o for n in ch for o in (1, 2, 3) if 67 <= n + 12 * o <= 86})
    rhythms = [[0, 1, 1.5, 2, 3], [0, 0.5, 1.5, 2.5, 3], [0, 1, 2, 2.5, 3.5], [0.5, 1, 2, 3], [0, 1.5, 2, 3, 3.5]]
    rhythm = rhythms[int(r.integers(0, len(rhythms)))]
    notes, last = [], int(pool[int(r.integers(0, len(pool)))])
    for pos in rhythm:
        if r.random() > density:
            continue
        if pos % 1 == 0:
            target = last + int(r.choice([-4, -2, 0, 2, 4]))
            last = min(pool, key=lambda p: abs(p - target))
        else:
            target = last + int(r.choice([-2, -1, 1, 2]))
            last = min((p for p in SCALE_NOTES if 67 <= p <= 86), key=lambda p: abs(p - target))
        notes.append((pos, int(last)))
    return notes


# ------------------------------------------------------------------ song form: (name, bars, progression, intensity)
# Short 4-bar sections so a 40-60 s Reel hears something new every ~8-10 s.
form = [("intro", 1, "A", 0), ("A", 4, "A", 1), ("B", 4, "B", 2), ("break", 1, "B", 0), ("A2", 4, "A", 2), ("B2", 4, "B", 3)]
while sum(f[1] for f in form) * BAR < DUR + 2:
    form += [("A3", 4, "A", 2), ("break", 1, "A", 0), ("B3", 4, "B", 3)]

t0, total_bars = 0.0, 0
for si, (name, bars, pk, inten) in enumerate(form):
    prog = S[pk]
    lift = 2 if (name in ("B2", "B3") and STYLE not in ("funk",)) else 0
    mel_seed = int(rng.integers(0, 10 ** 6)) if name not in ("A2", "A3") else 4242 + SEED
    for b in range(bars):
        if t0 > DUR + 1:
            break
        root, ch = chord(prog[b % len(prog)])
        root += lift
        ch = [n + lift for n in ch]
        last_bar = b == bars - 1 and si + 1 < len(form)
        mr = np.random.default_rng(mel_seed + (b % 4) * 13)
        mel = melody_bar(ch, mr, 0.85 if inten >= 2 else 0.6) if (inten >= 2 or (inten == 1 and b >= 2)) else []

        # harmony + lead
        if STYLE == "bright":
            for k, s in enumerate([0, 1, 1.5, 2.5, 3, 3.5] if inten else [0, 2]):
                for n_i, m in enumerate(ch[:4]):
                    add(t0 + s * BEAT + n_i * 0.012, pluck(m + 12, 0.7), pan=-0.3 + 0.2 * n_i, gain=0.08 if k else 0.11)
            for pos, m in mel:
                add(t0 + pos * BEAT, glock(m), pan=0.35, gain=0.12)
        elif STYLE == "marimba":
            for k in range(8):
                if k % 2 or inten == 0:
                    add(t0 + k * BEAT / 2, marimba(ch[k % len(ch)] + 12, 0.4), pan=-0.25, gain=0.12)
            for pos, m in mel:
                add(t0 + pos * BEAT, marimba(m, 0.5), pan=0.3, gain=0.2)
                add(t0 + pos * BEAT + BEAT * 0.75, marimba(m, 0.3), pan=-0.3, gain=0.06)
        elif STYLE in ("piano", "studypiano"):
            arp = (ch + [ch[1] + 12, ch[2] + 12])[:6]
            step = 0.5 if STYLE == "piano" else 1.0
            for k in range(int(4 / step)):
                add(t0 + k * step * BEAT, piano(arp[k % len(arp)] + 12, 1.4, 0.8), pan=-0.2 + 0.08 * (k % 5), gain=0.09)
            if inten >= 2:
                add(t0, pad(ch, BAR), gain=0.06)
            for pos, m in mel:
                add(t0 + pos * BEAT, piano(m, 1.2, 1.1), pan=0.2, gain=0.15)
        elif STYLE == "funk":
            for s in ([0.5, 1.25, 2.5, 3.0, 3.75] if inten else [0]):
                add(t0 + s * BEAT, epiano([n + 12 for n in ch[:4]], BEAT * 0.3), pan=-0.2, gain=0.12)
            for pos, m in mel:
                add(t0 + pos * BEAT, synth(m, 0.22), pan=0.3, gain=0.08)
        elif STYLE == "lofi":
            add(t0, epiano([n + 12 for n in ch[:4]], BEAT * 2.2), pan=-0.15, gain=0.16)
            add(t0 + BEAT * 2.5 + SWING, epiano([n + 12 for n in ch[1:4]], BEAT * 1.3), pan=0.15, gain=0.11)
            for pos, m in mel:
                add(t0 + pos * BEAT + (SWING if pos % 1 else 0), glock(m - 12, 1.0), pan=0.3, gain=0.06)
        elif STYLE == "jazzhop":
            add(t0, epiano([n + 12 for n in ch], BEAT * 1.6), pan=-0.1, gain=0.15)
            add(t0 + BEAT * 2.75, epiano([n + 12 for n in ch[1:]], BEAT * 0.9), pan=0.1, gain=0.11)
            for pos, m in mel:
                add(t0 + pos * BEAT + (SWING if pos % 1 else 0), piano(m - 12, 0.8, 1.3), pan=0.25, gain=0.09)
        elif STYLE == "arp":
            seq = ch + [ch[0] + 12, ch[1] + 12]
            cnt = 16 if inten else 8
            for k in range(cnt):
                add(t0 + k * BAR / cnt, synth(seq[(k * 3) % len(seq)] + 12, 0.18), pan=0.3 * np.sin(k), gain=0.055)
            add(t0, pad(ch, BAR), gain=0.08)
            for pos, m in mel:
                add(t0 + pos * BEAT, glock(m, 0.9), pan=-0.2, gain=0.07)

        # bass
        if inten >= 1:
            if STYLE == "funk":
                for s, o in [(0, 0), (0.75, 12), (1.5, 0), (2.5, 0), (3.25, 12)]:
                    add(t0 + s * BEAT, bass(root + o, BEAT * 0.4, True), gain=0.36)
            elif STYLE == "jazzhop":
                for k, m in enumerate([root, root + 4, root + 7, root + 9]):
                    add(t0 + k * BEAT, bass(m, BEAT * 0.9, True), gain=0.3)
            elif STYLE == "marimba":
                for s in (0, 1.5, 2.5):
                    add(t0 + s * BEAT, bass(root, BEAT * 0.8, True), gain=0.32)
            elif STYLE == "arp":
                for s in (0, 2):
                    add(t0 + s * BEAT, bass(root, BEAT * 1.8), gain=0.3)
            else:
                add(t0, bass(root, BEAT * 3.5), gain=0.32)

        # drums
        going_to_break = last_bar and form[si + 1][0] == "break"
        if inten >= 1 and not going_to_break:
            if STYLE in ("bright", "marimba", "funk", "arp"):
                for k in {"bright": [0, 2], "marimba": [0, 2, 2.75], "funk": [0, 0.75, 2.5], "arp": [0, 1, 2, 3]}[STYLE]:
                    add(t0 + k * BEAT, KICK, gain=0.26)
                if inten >= 2:
                    for k in (1, 3):
                        add(t0 + k * BEAT, SNARE if STYLE == "arp" else CLAP, pan=0.05, gain=0.09)
                sub = 4 if (STYLE == "funk" or inten >= 3) else 2
                for k in range(4 * sub):
                    add(t0 + k * BEAT / sub, SHAKER if STYLE in ("bright", "marimba") else HAT, pan=0.35, gain=0.035 if k % 2 else 0.05)
            elif STYLE in ("lofi", "jazzhop"):
                for k, g in [(0, 0.3), (2.5 + SWING / BEAT, 0.22)]:
                    add(t0 + k * BEAT, KICK, gain=g)
                for k in (1, 3):
                    add(t0 + k * BEAT, SNARE, gain=0.08)
                for k in range(8):
                    add(t0 + k * BEAT / 2 + (SWING if k % 2 else 0), HAT, pan=0.3, gain=0.04)
            else:
                add(t0, KICK, gain=0.16)
                if inten >= 2:
                    add(t0 + 2 * BEAT, RIM, pan=0.2, gain=0.06)
                    for k in range(4):
                        add(t0 + k * BEAT, SHAKER, pan=0.3, gain=0.03)
            if last_bar:  # fill into the next section
                for k in range(4):
                    add(t0 + (3 + k / 4) * BEAT, SNARE, pan=-0.2 + 0.1 * k, gain=0.05 + 0.02 * k)
        if b == 0 and inten >= 2:
            add(t0, OPENHAT, pan=-0.3, gain=0.06)
        t0 += BAR
        total_bars += 1

if STYLE in ("lofi", "jazzhop"):  # vinyl crackle
    pops = rng.random(N) < 0.00025
    crackle = np.where(pops, rng.uniform(-1, 1, N), 0) * 0.08 + rng.normal(0, 0.003, N)
    L += crackle
    R += np.roll(crackle, 37)

n = int(DUR * SR)
L, R = L[:n], R[:n]
fade = np.ones(n)
fi, fo = int(0.6 * SR), int(2.0 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fade[-fo:] = np.linspace(1, 0, fo)
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max()) or 1
st = np.stack([L, R], 1) / peak * 0.85
with wave.open(OUT, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print(f"wrote {OUT}: {STYLE}, {S['bpm']} bpm, {DUR:.1f}s, {total_bars} bars")
