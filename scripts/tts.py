import sys, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
k = Kokoro("models/kokoro-v1.0.onnx", "models/voices-v1.0.bin")
voice, speed = sys.argv[1], float(sys.argv[2])
for path in sys.argv[3:]:
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
