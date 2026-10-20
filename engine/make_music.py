"""Genera una pista lo-fi suave (sin derechos de terceros) para los Reels.
Uso: python3 make_music.py musica/lofi_suave.wav [segundos]"""
import sys, numpy as np, wave
SR = 44100
out = sys.argv[1] if len(sys.argv) > 1 else 'musica/lofi_suave.wav'
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
BPM = 74; beat = 60 / BPM; bar = 4 * beat
n = int(DUR * SR); t = np.arange(n) / SR
mix = np.zeros((n, 2))
rng = np.random.default_rng(7)
def midi(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, start, pan=0.0, gain=1.0):
    i0 = int(start * SR); i1 = min(n, i0 + len(sig))
    if i0 >= n: return
    s = sig[:i1 - i0] * gain
    mix[i0:i1, 0] += s * (1 - pan) / 2 * 2 ** 0.5 * 0.71
    mix[i0:i1, 1] += s * (1 + pan) / 2 * 2 ** 0.5 * 0.71
def epiano(m, length):
    tt = np.arange(int(length * SR)) / SR; f = midi(m)
    env = np.exp(-tt * 1.6) * (1 - np.exp(-tt * 200))
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.5 * tt)
    return env * trem * (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 3))
def bass(m, length):
    tt = np.arange(int(length * SR)) / SR; f = midi(m)
    env = np.exp(-tt * 1.2) * (1 - np.exp(-tt * 80))
    return env * (np.sin(2 * np.pi * f * tt) + 0.15 * np.sin(2 * np.pi * 2 * f * tt))
def kick():
    tt = np.arange(int(0.35 * SR)) / SR
    f = 50 + 70 * np.exp(-tt * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
def hat():
    tt = np.arange(int(0.08 * SR)) / SR
    x = rng.normal(0, 1, len(tt)); x = np.diff(np.r_[0, x])  # brillo
    return x * np.exp(-tt * 60)
# Fmaj7 - Em7 - Dm7 - Cmaj7 (voicings cerrados, registro medio)
CHORDS = [(53, [64, 69, 72, 76]), (52, [62, 67, 71, 74]), (50, [60, 65, 69, 72]), (48, [59, 64, 67, 71])]
nb = int(DUR / bar) + 1
for b in range(nb):
    root, notes = CHORDS[b % 4]; t0 = b * bar
    for j, m in enumerate(notes):           # acorde rasgueado suave
        add(epiano(m, bar * 1.1), t0 + 0.018 * j + 0.01, pan=-0.3 + 0.2 * j, gain=0.11)
    add(epiano(notes[-1] + (2 if b % 2 else 0), beat * 1.5), t0 + 2.5 * beat, pan=0.3, gain=0.07)  # adorno
    add(bass(root - 12, beat * 2), t0, gain=0.30); add(bass(root - 12, beat * 1.5), t0 + 2 * beat, gain=0.22)
    for k in range(4):
        if k in (0, 2): add(kick(), t0 + k * beat, gain=0.32)
        add(hat(), t0 + k * beat + beat / 2 + 0.012, pan=0.4, gain=0.05)
# crujido de vinil muy bajito
crack = (rng.random(n) < 0.0006) * rng.normal(0, 0.25, n)
mix += np.c_[crack, crack] * 0.4 + rng.normal(0, 0.003, (n, 2))
# low-pass suave (promedio móvil) para sonido "tibio"
k = 9; ker = np.ones(k) / k
mix = np.c_[np.convolve(mix[:, 0], ker, 'same'), np.convolve(mix[:, 1], ker, 'same')]
mix /= np.abs(mix).max() / 0.45   # bajito: es fondo, no protagonista
pcm = (mix * 32767).astype(np.int16)
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok', out, DUR, 's')
