#!/usr/bin/env python3
"""Оригинальная тихая музыкальная подложка (lo-fi, ~100 bpm) без внешних лицензий.
Генерируется кодом (numpy), права наши. Результат: media/music/insait-bed-01.wav
    python tools/make_music_bed.py
"""
import numpy as np, wave
from pathlib import Path

SR = 44100; BPM = 100; BEAT = 60 / BPM; BARS = 16
N = int(SR * BEAT * 4 * BARS); rng = np.random.default_rng(7)
mix = np.zeros(N)

def mtof(m): return 440 * 2 ** ((m - 69) / 12)

def add(sig, t0):
    i = int(t0 * SR); j = min(N, i + len(sig))
    if i < N: mix[i:j] += sig[:j - i]

def keys(m, dur, amp):
    t = np.arange(int(SR * dur)) / SR; f = mtof(m)
    s = (np.sin(2*np.pi*f*t) + .35*np.sin(2*np.pi*2*f*t)*np.exp(-3*t) + .12*np.sin(2*np.pi*3*f*t)*np.exp(-5*t))
    s *= np.exp(-1.6*t) * np.minimum(1, t / 0.006) * (1 + .05*np.sin(2*np.pi*5*t))
    return amp * s

def bass(m, dur, amp):
    t = np.arange(int(SR * dur)) / SR; f = mtof(m)
    return amp * np.sin(2*np.pi*f*t) * np.exp(-2.2*t) * np.minimum(1, t / 0.01)

def kick(amp):
    t = np.arange(int(SR * .35)) / SR
    return amp * np.sin(2*np.pi*(50 + 90*np.exp(-30*t)) * t) * np.exp(-9*t)

def noise(dur, decay, amp, hp=False):
    n = rng.standard_normal(int(SR * dur)); t = np.arange(len(n)) / SR
    if hp: n = np.diff(n, prepend=0)
    return amp * n * np.exp(-decay * t)

# Am7 – Fmaj7 – Cmaj7 – G6 : по такту каждый, 4 раза по 4 такта
chords = [([57, 60, 64, 67], 45), ([53, 57, 60, 64], 41), ([60, 64, 67, 71], 48), ([55, 59, 62, 64], 43)]
for bar in range(BARS):
    notes, root = chords[bar % 4]; t0 = bar * 4 * BEAT
    for k, m in enumerate(notes):                      # аккорд, лёгкий «перебор»
        add(keys(m, 2.6, .16), t0 + k * 0.025)
    for k, m in enumerate(notes[1:]):                  # синкопа на «и» третьей доли
        add(keys(m + 12, 1.2, .07), t0 + 2.5 * BEAT + k * 0.02)
    add(bass(root, 1.1, .5), t0); add(bass(root, 1.0, .4), t0 + 2.5 * BEAT)
    for b in (0, 2): add(kick(.55), t0 + b * BEAT)
    for b in (1, 3): add(noise(.18, 22, .12), t0 + b * BEAT + .004)
    for e in range(8):
        sw = 0.04 * BEAT if e % 2 else 0
        add(noise(.05, 70, .05 if e % 2 else .07, hp=True), t0 + e * BEAT / 2 + sw)

# мягкий «ламповый» тембр: срез верха + простая реверберация
spec = np.fft.rfft(mix); fr = np.fft.rfftfreq(N, 1 / SR); spec *= 1 / (1 + (fr / 5500) ** 4)
mix = np.fft.irfft(spec, N)
out = mix.copy()
for d, g in ((.047, .33), (.083, .26), (.131, .2)):
    k = int(d * SR); out[k:] += g * mix[:-k]
out /= np.abs(out).max(); out *= .9
fade = int(SR * 1.5); out[-fade:] *= np.linspace(1, 0, fade)
p = Path(__file__).resolve().parent.parent / "media" / "music" / "insait-bed-01.wav"
p.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(p), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes())
print(p, round(N / SR, 1), "c")
