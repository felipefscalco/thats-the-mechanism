"""Self-synthesised SFX (original, CC0 by us): whoosh, riser, sting, soft tick. 48 kHz stereo."""
import numpy as np, soundfile as sf
SR = 48000
rng = np.random.default_rng(7)
def env(n, a, r):  # attack/release in samples, shape
    e = np.ones(n); a = max(1, a); r = max(1, r)
    e[:a] = np.linspace(0, 1, a) ** 2; e[-r:] *= np.linspace(1, 0, r) ** 2; return e
def onepole_lp(x, fc):  # time-varying lowpass, fc array in Hz
    y = np.zeros_like(x); s = 0.0
    a = np.exp(-2 * np.pi * fc / SR)
    for i in range(len(x)): s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y
def save(name, l, r=None, peak=0.5):
    r = l if r is None else r
    st = np.stack([l, r], 1); st = st / (np.abs(st).max() + 1e-9) * peak
    sf.write(f"sfx/synth/{name}.wav", st.astype(np.float32), SR)
# whoosh: noise through a sweeping lowpass, bell-shaped envelope, slight pan movement
n = int(0.55 * SR); t = np.arange(n) / SR
noise = rng.standard_normal(n)
fc = 300 + 5200 * np.sin(np.pi * t / t[-1]) ** 2
w = onepole_lp(onepole_lp(noise, fc), fc) * np.sin(np.pi * t / t[-1]) ** 1.5
pan = 0.5 + 0.4 * np.sin(np.pi * (t / t[-1] - 0.5))
save("whoosh", w * (1 - pan) * 2, w * pan * 2)
# riser: noise + upward sine glide, crescendo, 1.3 s
n = int(1.3 * SR); t = np.arange(n) / SR
f = 180 * (6 ** (t / t[-1])); ph = 2 * np.pi * np.cumsum(f) / SR
ris = 0.5 * np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.6 * onepole_lp(rng.standard_normal(n), 400 + 6000 * (t / t[-1]) ** 2)
ris *= (t / t[-1]) ** 2.2 * env(n, 10, int(0.04 * SR))
save("riser", ris)
# sting: mechanical double tick + warm bell chord (A, E, C#, A) with soft thump
n = int(1.6 * SR); t = np.arange(n) / SR
sting = np.zeros(n)
for k, t0 in enumerate([0.0, 0.11]):
    i0 = int(t0 * SR); m = int(0.03 * SR); tt = np.arange(m) / SR
    sting[i0:i0 + m] += (0.6 if k == 0 else 0.8) * np.sin(2 * np.pi * (2400 if k == 0 else 1800) * tt) * np.exp(-tt * 180)
i0 = int(0.2 * SR); tt = t[: n - i0]
chord = sum(a * np.sin(2 * np.pi * fr * tt) * np.exp(-tt * d) for fr, a, d in [(440, .5, 3), (659.25, .35, 3.5), (1108.7, .25, 4.5), (880, .3, 4), (1760, .08, 7)])
thump = 0.9 * np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 18)
sting[i0:] += chord + thump
sting *= env(n, 5, int(0.2 * SR))
save("sting", sting, np.roll(sting, 240), peak=0.6)
# soft tick for counters
n = int(0.05 * SR); tt = np.arange(n) / SR
save("tick", np.sin(2 * np.pi * 3000 * tt) * np.exp(-tt * 120), peak=0.4)
print("ok")
