import sys, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
import os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
k = Kokoro(f"{R}/models/kokoro-v1.0.onnx", f"{R}/models/voices-v1.0.bin")
voice, speed = sys.argv[1], float(sys.argv[2])
import subprocess
for path in sys.argv[3:]:
    # r5 gates: no voice until the fact ledger passes and the script gate is open (pipeline.config.json)
    slug = os.path.basename(os.path.dirname(os.path.abspath(path)))
    if os.environ.get("TTM_TTS_SCRATCH") != "1" and (os.path.exists(f"{R}/episodes/{slug}/facts.json") or os.path.exists(f"{R}/pipeline.config.json")):  # TTM_TTS_SCRATCH=1: tests on a scratch dir only
        for cmd in ([sys.executable, f"{R}/scripts/facts.py", "check", slug], [sys.executable, f"{R}/scripts/gates.py", "require", slug, "script", "--artifact", f"episodes/{slug}/script.txt"]):
            if subprocess.run(cmd).returncode: sys.exit(f"tts blocked for {slug}: {' '.join(cmd[1:3])} failed")
    from script_text import chunks, HEAD_S
    sr = 24000; out = [np.zeros(int(HEAD_S * sr), dtype=np.float32)]; pos = len(out[0]); segs = []
    for text, gap in chunks(open(path).read()):
        s, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
        s = s.astype(np.float32); out.append(s)
        n_sil = int(round(gap * sr)); out.append(np.zeros(n_sil, dtype=np.float32))
        # r8: exact sample offsets of every spoken chunk; captions.py shifts its word timing estimate by these counts
        segs.append(dict(text=text, start_sample=pos, end_sample=pos + len(s), silence_after_samples=n_sil, sr=sr,
                         start_s=round(pos / sr, 4), end_s=round((pos + len(s)) / sr, 4)))
        pos += len(s) + n_sil
    a = np.concatenate(out)
    dst = path.replace("script.txt", "narration_raw.wav")
    sf.write(dst, a, sr)
    json.dump(dict(sr=sr, total_samples=len(a), segments=segs), open(path.replace("script.txt", "narration_segments.json"), "w"), indent=1)
    print(dst, round(len(a)/sr, 2), "s,", len(segs), "chunks")
