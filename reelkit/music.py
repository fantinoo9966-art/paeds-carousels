"""Original background music for Reels, composed in code (copyright-free, free to use).

python reel_music.py <style> <seconds> <out.wav> [seed] [transpose]
  style "bright": cheerful ukulele-style plucks + glockenspiel + soft kick/shaker, 104 BPM (parents Reels)
  style "lofi":   calm lo-fi study beat, electric-piano chords + soft drums + vinyl crackle, 84 BPM (PG Reels)
"""
import sys
import wave

import numpy as np

STYLE = sys.argv[1] if len(sys.argv) > 1 else "bright"
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 45
OUT = sys.argv[3] if len(sys.argv) > 3 else "music.wav"
SEED = int(sys.argv[4]) if len(sys.argv) > 4 else 0  # different seed = different drum fills/melody choices
KEY = int(sys.argv[5]) if len(sys.argv) > 5 else 0  # transpose in semitones, so each Reel sounds a bit different
SR = 48000
rng = np.random.default_rng((11 if STYLE == "bright" else 23) + SEED)
N = int((DUR + 3) * SR)
L = np.zeros(N)
R = np.zeros(N)


def hz(m):
    return 440 * 2 ** ((m + KEY - 69) / 12)


def add(start, sig, pan=0.0, gain=1.0):
    i = max(0, int(start * SR))
    if i >= N:
        return
    j = min(N, i + len(sig))
    s = sig[: j - i] * gain
    L[i:j] += s * (1 - pan) ** 0.5 * 0.7071 * 2 ** 0.5 / 2 ** 0.5
    R[i:j] += s * (1 + pan) ** 0.5 * 0.7071 * 2 ** 0.5 / 2 ** 0.5


def tt(d):
    return np.arange(int(d * SR)) / SR


def pluck(m, d=0.9, bright=1.0):
    t = tt(d)
    f = hz(m)
    s = sum((0.8 ** k) * np.sin(2 * np.pi * f * (k + 1) * t) * np.exp(-t * (3 + 5 * k * bright)) for k in range(6))
    return s * np.minimum(1, t / 0.003)


def glock(m, d=1.2):
    t = tt(d)
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6) + 0.12 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 10)
    return s * np.exp(-t * 3.2) * np.minimum(1, t / 0.002)


def epiano(ms, d):
    t = tt(d + 0.6)
    s = np.zeros(len(t))
    for m in ms:
        f = hz(m)
        trem = 1 + 0.12 * np.sin(2 * np.pi * 4.5 * t)
        s += (np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * f * t) * np.exp(-t * 3))) * np.exp(-t * 1.1) * trem
    rel = np.clip((d + 0.6 - t) / 0.5, 0, 1)
    return s / len(ms) * np.minimum(1, t / 0.01) * rel


def bass(m, d):
    t = tt(d)
    f = hz(m)
    return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)) * np.minimum(1, t / 0.01) * np.clip((d - t) / 0.08, 0, 1) * np.exp(-t * 1.2)


def kick():
    t = tt(0.35)
    return np.sin(2 * np.pi * (50 * t + 90 / 25 * (1 - np.exp(-t * 25)))) * np.exp(-t * 9)


def noise_hit(d, decay, lp):
    n = rng.uniform(-1, 1, int(d * SR))
    out = np.zeros_like(n)
    a = 0.0
    for i in range(len(n)):  # short, so a simple loop is fine
        a += lp * (n[i] - a)
        out[i] = n[i] - a if lp < 0.5 else a
    return out * np.exp(-tt(d) * decay)


SHAKER = noise_hit(0.08, 60, 0.9)
SNARE = noise_hit(0.22, 18, 0.35) + 0.4 * np.sin(2 * np.pi * 190 * tt(0.22)) * np.exp(-tt(0.22) * 25)
KICK = kick()

if STYLE == "bright":
    BPM = 104
    beat = 60 / BPM
    # C – G – Am – F  (bass note, chord tones)
    prog = [(36, [60, 64, 67, 72]), (43, [59, 62, 67, 71]), (45, [60, 64, 69, 72]), (41, [60, 65, 69, 72])]
    melody = [[76, None, 79, 76, 74, None, 72, None], [74, None, 71, 74, 79, None, None, None],
              [72, None, 76, 77, 76, None, 72, None], [69, 72, None, 74, 72, None, None, None]]
    bar = 0
    t0 = 0.0
    while t0 < DUR + 1:
        b, ch = prog[bar % 4]
        add(t0, bass(b, beat * 4), gain=0.35)
        strum = [0, 1, 1.5, 2.5, 3, 3.5]
        for k, s in enumerate(strum):
            for n_i, m in enumerate(ch):
                add(t0 + s * beat + n_i * 0.012, pluck(m, 0.7, 1.2), pan=-0.3 + 0.2 * n_i, gain=0.08 if k else 0.11)
        if bar >= 2 and (bar // 4) % 2 == 1:
            for k, m in enumerate(melody[bar % 4]):
                if m:
                    add(t0 + k * beat / 2, glock(m), pan=0.35, gain=0.12)
        if bar >= 1:
            for k in range(4):
                add(t0 + k * beat, KICK, gain=0.28 if k % 2 == 0 else 0.0)
            for k in range(8):
                add(t0 + k * beat / 2, SHAKER, pan=0.4, gain=0.05 if k % 2 else 0.03)
        t0 += beat * 4
        bar += 1
else:
    BPM = 84
    beat = 60 / BPM
    swing = 0.06
    # Fmaj9 – Em7 – Dm9 – G13sus  (ii–V-ish lo-fi loop)
    prog = [(41, [57, 60, 64, 67]), (40, [55, 59, 62, 67]), (38, [57, 60, 64, 65]), (43, [57, 60, 65, 69])]
    bar = 0
    t0 = 0.0
    while t0 < DUR + 1:
        b, ch = prog[bar % 4]
        add(t0, bass(b, beat * 3.5), gain=0.33)
        add(t0, epiano(ch, beat * 2.2), pan=-0.15, gain=0.16)
        add(t0 + beat * 2.5 + swing, epiano(ch[1:], beat * 1.3), pan=0.15, gain=0.11)
        if bar >= 1:
            for k, g in [(0, 0.3), (2.5 + swing / beat, 0.22)]:
                add(t0 + k * beat, KICK, gain=g)
            for k in (1, 3):
                add(t0 + k * beat, SNARE, gain=0.07)
            for k in range(8):
                add(t0 + k * beat / 2 + (swing if k % 2 else 0), SHAKER, pan=0.3, gain=0.035)
        if bar >= 4 and bar % 2 == 0:
            for k, m in enumerate([72, 74, 76, 79] if bar % 4 == 0 else [77, 76, 72, 69]):
                add(t0 + (k * 0.75 + 0.5) * beat, glock(m, 1.0), pan=0.3, gain=0.05)
        t0 += beat * 4
        bar += 1
    # vinyl crackle
    pops = rng.random(N) < 0.00025
    crackle = np.where(pops, rng.uniform(-1, 1, N), 0) * 0.08 + rng.normal(0, 0.003, N)
    L += crackle
    R += np.roll(crackle, 37)

n = int(DUR * SR)
L, R = L[:n], R[:n]
fade = np.ones(n)
fi, fo = int(0.8 * SR), int(2.0 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fade[-fo:] = np.linspace(1, 0, fo)
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
st = np.stack([L, R], 1) / peak * 0.85
with wave.open(OUT, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print(f"wrote {OUT}: {STYLE}, {DUR:.1f}s")
