#!/workspace/thats-the-mechanism/.venv-tts/bin/python
"""Automated acceptance QA for one rendered episode (see docs/ACCEPTANCE.md).
Usage: scripts/qa.py <CompositionId> <slug> <iteration> [--no-stems]
Writes qa/<Id>/report_it<N>.json, transitions_it<N>.png (dense frames around every shot boundary + the loop seam),
grid_it<N>.png (one frame per 1.5 s). Prints PASS/FAIL per automated check; visual checks are listed for the reviewer."""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
import soundfile as sf
sys.path.insert(0, str(Path(__file__).parent))
from shotlib import ROOT, words, phrase_time, shots

ID, SLUG, IT = sys.argv[1], sys.argv[2], int(sys.argv[3])
STEMS = "--no-stems" not in sys.argv
MP4 = ROOT / "renders" / f"{ID}_v2.mp4"
OUT = ROOT / "qa" / ID; OUT.mkdir(parents=True, exist_ok=True)
sh = lambda c: subprocess.run(c, shell=True, capture_output=True, text=True)
res, checks = {}, []
def check(name, ok, detail): checks.append(dict(check=name, ok=bool(ok), detail=detail))

# 1. container
pr = json.loads(sh(f"ffprobe -v error -show_streams -show_format -of json {MP4}").stdout)
v = next(s for s in pr["streams"] if s["codec_type"] == "video"); a = next(s for s in pr["streams"] if s["codec_type"] == "audio")
dur = float(pr["format"]["duration"]); fps = eval(v["r_frame_rate"])
res["probe"] = dict(w=v["width"], h=v["height"], fps=fps, vcodec=v["codec_name"], acodec=a["codec_name"], sr=a["sample_rate"], dur=round(dur, 2), mb=round(int(pr["format"]["size"]) / 2**20, 2))
check("format 1080x1920@30 h264+aac, 35-55 s", v["width"] == 1080 and v["height"] == 1920 and abs(fps - 30) < 0.01 and a["codec_name"] == "aac" and 35 <= dur <= 55, res["probe"])

# 2. loudness
e = sh(f"ffmpeg -nostats -i {MP4} -af ebur128=peak=true -f null - 2>&1").stdout
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1]); TP = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e)[-1]); LRA = float(re.findall(r"LRA:\s+(-?[\d.]+) LU", e)[-1])
res["loudness"] = dict(I=I, TP=TP, LRA=LRA)
check("loudness -15.5..-13 LUFS, true peak <= -1 dBTP", -15.5 <= I <= -13 and TP <= -1.0, res["loudness"])

# 3. SFX vs voice from stems (rendered with --props stem)
if STEMS:
    st = {}
    for stem in ("sfx", "voice"):
        w = OUT / f"stem_{stem}.wav"
        sh(f"cd {ROOT}/remotion && npx remotion render {ID} {w} --codec=wav --props='{{\"stem\":\"{stem}\"}}' --log=error")
        x, sr = sf.read(w); x = x.mean(1) if x.ndim > 1 else x
        win, hop = int(0.4 * sr), int(0.1 * sr)
        st[stem] = np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + win] ** 2)) + 1e-9) for i in range(0, len(x) - win, hop)])
    vo, sx = st["voice"], st["sfx"]
    voice_lvl = float(np.median(vo[vo > -45]))
    peaks = [i for i in range(1, len(sx) - 1) if sx[i] >= sx[i - 1] and sx[i] > sx[i + 1] and sx[i] > -60 and sx[i] == sx[max(0, i - 4):i + 5].max()]
    gaps = np.array([voice_lvl - sx[i] for i in peaks])
    res["sfx"] = dict(voice_rms_db=round(voice_lvl, 1), events=len(peaks), gap_db_median=round(float(np.median(gaps)), 1), gap_db_min=round(float(gaps.min()), 1),
                      gap_db_max=round(float(gaps.max()), 1), sfx_per_s=round(len(peaks) / dur, 2))
    check("SFX median 10-16 dB under voice, none louder than voice-8 dB", 10 <= np.median(gaps) <= 16 and gaps.min() >= 8, res["sfx"])

# 4. motion on the stage ROI (y 290..1190)
raw = subprocess.run(f"ffmpeg -v error -i {MP4} -vf crop=1080:900:0:290,scale=216:180,format=gray -f rawvideo -", shell=True, capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, 180, 216).astype(np.float32)
# change over a 0.2 s window (so slow eases/fades and small pops count as motion, background drift does not)
d = np.abs(fr[6:] - fr[:-6]).mean(axis=(1, 2))
still = d < 0.5
longest, cur, at_ = 0, 0, 0
for i, s in enumerate(still):
    cur = cur + 1 if s else 0
    if cur > longest: longest, at_ = cur, i - cur + 1
res["motion"] = dict(longest_hold_s=round(longest / fps, 2), hold_starts_s=round(at_ / fps, 2), mean_diff=round(float(d.mean()), 2))
check("motion: no stage hold > 2.0 s", longest / fps <= 2.0, res["motion"])

# 5. hook visual in the first second (subject already drawn at 0.3 s and stage changes before 1 s)
f9 = fr[9]; bright = float((f9 > 90).mean())
moved = float(np.abs(fr[29] - fr[0]).mean())
res["hook"] = dict(bright_frac_at_0_3s=round(bright, 3), change_0_to_1s=round(moved, 2))
check("hook: subject on screen at 0.3 s and visible change by 1 s", bright > 0.02 and moved > 1.0, res["hook"])

# 6. exact loop: seam jump (last -> first) vs normal frame-to-frame motion, full frame
full = subprocess.run(f"ffmpeg -v error -i {MP4} -vf scale=270:480,format=gray -f rawvideo -", shell=True, capture_output=True).stdout
ff = np.frombuffer(full, np.uint8).reshape(-1, 480, 270).astype(np.float32)
cons = np.abs(np.diff(ff, axis=0)).mean(axis=(1, 2)); seam = float(np.abs(ff[-1] - ff[0]).mean())
mse = float(((ff[-1] - ff[0]) ** 2).mean()); psnr = 99.0 if mse == 0 else 10 * np.log10(255 ** 2 / mse)
res["loop"] = dict(seam_diff=round(seam, 2), median_step=round(float(np.median(cons)), 2), p95_step=round(float(np.percentile(cons, 95)), 2), psnr_last_vs_first=round(psnr, 1))
check("loop: seam jump <= p95 frame step (and PSNR >= 25 dB)", seam <= np.percentile(cons, 95) and psnr >= 25, res["loop"])

# 7. visual review sheets
def sheets():
    ws = words(SLUG); bounds = [phrase_time(ws, r["at"]) for r in shots(SLUG) if r["at"]] + [dur - 0.02]
    rows = []
    for k, t in enumerate(bounds):
        ts = [max(0, min(dur - 0.04, t + o)) for o in (-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.33, 0.5)]
        if k == len(bounds) - 1: ts = [dur - 0.5, dur - 0.4, dur - 0.3, dur - 0.2, dur - 0.1, dur - 0.04, 0.0, 0.1]  # loop seam -> frame 0
        files = []
        for j, tt in enumerate(ts):
            p = OUT / f"_t{k}_{j}.png"; seek = f"-sseof -0.07" if tt > dur - 0.1 else f"-ss {tt:.3f}"
            sh(f"ffmpeg -v error -y {seek} -i {MP4} -frames:v 1 -update 1 -vf scale=270:-1 {p}"); files.append(p)
        r = OUT / f"_row{k}.png"; sh("ffmpeg -v error -y " + " ".join(f"-i {p}" for p in files) + f" -filter_complex hstack=inputs={len(files)} {r}"); rows.append(r)
    sh("ffmpeg -v error -y " + " ".join(f"-i {r}" for r in rows) + f" -filter_complex vstack=inputs={len(rows)} {OUT}/transitions_it{IT}.png")
    sh(f"ffmpeg -v error -y -i {MP4} -vf fps=1/1.5,scale=216:-1,tile=8x5 -frames:v 1 {OUT}/grid_it{IT}.png")
    for p in OUT.glob("_*.png"): p.unlink()


sheets() if '--no-sheets' not in sys.argv else None
res["checks"] = checks; res["iteration"] = IT
(OUT / f"report_it{IT}.json").write_text(json.dumps(res, indent=2))
for c in checks: print(("PASS" if c["ok"] else "FAIL"), "|", c["check"], "|", json.dumps(c["detail"]))
print("VISUAL (reviewer):", f"{OUT}/transitions_it{IT}.png", f"{OUT}/grid_it{IT}.png", "— overlaps, caption readability, SFX sync, style failure list")
