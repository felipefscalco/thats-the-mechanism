"""Normalise every SFX to the same loudness: loudest 400 ms window -> TARGET dBFS RMS (≈ -27 LUFS momentary),
so at volume=1 a cue sits ~13 dB under the -14 LUFS voice. Writes remotion/public/sfx/<name>.wav"""
import numpy as np, soundfile as sf, scipy.signal as ss, csv, os
TARGET = {"default": -27.0, "whoosh": -28.0, "riser": -29.0, "sting": -25.0, "tick": -31.0, "pop": -28.0, "click": -29.0}
K = "sfx/kenney"
SRC = {
  "pop":     (f"{K}/interface-sounds/Audio/drop_002.ogg", "Kenney Interface Sounds", "CC0 1.0"),
  "click":   (f"{K}/interface-sounds/Audio/click_002.ogg", "Kenney Interface Sounds", "CC0 1.0"),
  "confirm": (f"{K}/interface-sounds/Audio/confirmation_002.ogg", "Kenney Interface Sounds", "CC0 1.0"),
  "error":   (f"{K}/interface-sounds/Audio/error_004.ogg", "Kenney Interface Sounds", "CC0 1.0"),
  "glitch":  (f"{K}/interface-sounds/Audio/glitch_002.ogg", "Kenney Interface Sounds", "CC0 1.0"),
  "thud":    (f"{K}/impact-sounds/Audio/impactMetal_medium_001.ogg", "Kenney Impact Sounds", "CC0 1.0"),
  "clank":   (f"{K}/impact-sounds/Audio/impactPlate_light_002.ogg", "Kenney Impact Sounds", "CC0 1.0"),
  "whoosh":  ("sfx/synth/whoosh.wav", "Self-synthesised (scripts/synth_sfx.py)", "Original, CC0 (ours)"),
  "riser":   ("sfx/synth/riser.wav", "Self-synthesised (scripts/synth_sfx.py)", "Original, CC0 (ours)"),
  "sting":   ("sfx/synth/sting.wav", "Self-synthesised (scripts/synth_sfx.py)", "Original, CC0 (ours)"),
  "tick":    ("sfx/synth/tick.wav", "Self-synthesised (scripts/synth_sfx.py)", "Original, CC0 (ours)"),
}
os.makedirs("remotion/public/sfx", exist_ok=True)
rows = []
for name, (path, origin, lic) in SRC.items():
    x, sr = sf.read(path, always_2d=True)
    if sr != 48000: x = ss.resample_poly(x, 48000, sr, axis=0); sr = 48000
    if x.shape[1] == 1: x = np.repeat(x, 2, 1)
    w = int(0.4 * sr); m = (x ** 2).mean(1)
    rms = np.sqrt(np.convolve(m, np.ones(w) / w, mode="same").max() if len(m) > w else m.mean())
    g = 10 ** ((TARGET.get(name, TARGET["default"]) - 20 * np.log10(rms + 1e-12)) / 20)
    y = np.clip(x * g, -0.95, 0.95)
    sf.write(f"remotion/public/sfx/{name}.wav", y.astype(np.float32), sr)
    rows.append([f"remotion/public/sfx/{name}.wav", path, origin, lic, "https://kenney.nl" if "Kenney" in origin else "-"])
with open("sfx/CREDITS.csv", "w", newline="") as f:
    cw = csv.writer(f); cw.writerow(["file", "source_file", "origin", "license", "url"]); cw.writerows(rows)
print(open("sfx/CREDITS.csv").read())
