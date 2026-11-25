import sys, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
import os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
k = Kokoro(f"{R}/models/kokoro-v1.0.onnx", f"{R}/models/voices-v1.0.bin")
voice, speed = sys.argv[1], float(sys.argv[2])
import subprocess
for path in sys.argv[3:]:
    # r5 gates: no voice until the fact ledger passes and the script gate is open (pipeline.config.json)
    slug = os.path.basename(os.path.dirname(os.path.abspath(path)))
    if os.path.exists(f"{R}/episodes/{slug}/facts.json") or os.path.exists(f"{R}/pipeline.config.json"):
        for cmd in ([sys.executable, f"{R}/scripts/facts.py", "check", slug], [sys.executable, f"{R}/scripts/gates.py", "require", slug, "script", "--artifact", f"episodes/{slug}/script.txt"]):
            if subprocess.run(cmd).returncode: sys.exit(f"tts blocked for {slug}: {' '.join(cmd[1:3])} failed")
    text = open(path).read().strip()
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    sr = 24000; out = [np.zeros(int(0.15*sr), dtype=np.float32)]
    for i, p in enumerate(paras):
        s, sr = k.create(p, voice=voice, speed=speed, lang="en-us")
        out.append(s.astype(np.float32))
        out.append(np.zeros(int((0.35 if i < len(paras)-1 else 0.5)*sr), dtype=np.float32))
    a = np.concatenate(out)
    dst = path.replace("script.txt", f"narration_raw.wav")
    sf.write(dst, a, sr)
    print(dst, round(len(a)/sr, 2), "s")
