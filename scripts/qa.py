#!/usr/bin/env python3
"""Automated acceptance QA for one rendered episode (see docs/ACCEPTANCE.md).
Usage: scripts/qa.py <CompositionId> <slug> <iteration> [--no-stems]
Writes qa/<Id>/report_it<N>.json, transitions_it<N>.png (dense frames around every shot boundary + the loop seam),
grid_it<N>.png (one frame per 1.5 s). Prints PASS/FAIL per automated check; visual checks are listed for the reviewer."""
import json, os, re, subprocess, sys
from pathlib import Path
import numpy as np
import soundfile as sf
sys.path.insert(0, str(Path(__file__).parent))
from shotlib import ROOT, words, phrase_time, shots

ID, SLUG, IT = sys.argv[1], sys.argv[2], int(sys.argv[3])
STEMS = "--no-stems" not in sys.argv
SUF = os.environ.get("SUF", "v2")
MP4 = ROOT / "renders" / f"{ID}_{SUF}.mp4"
# QA_DIR overrides the folder under qa/<Id>/ (e.g. QA_DIR=v4/baseline_v3 to re-check an old render with new checks without touching its QA)
OUT = ROOT / "qa" / ID / os.environ.get("QA_DIR", "" if SUF == "v2" else SUF); OUT.mkdir(parents=True, exist_ok=True)
LOOP_FRAMES, T_FRAMES = 14, 10  # keep in sync with brand/EpisodeShell.tsx and brand/Shot.tsx
sh = lambda c: subprocess.run(c, shell=True, capture_output=True, text=True)
res, checks = {}, []
def check(name, ok, detail): checks.append(dict(check=name, ok=bool(ok), detail=detail))

# 1. container
pr = json.loads(sh(f"ffprobe -v error -show_streams -show_format -of json {MP4}").stdout)
v = next(s for s in pr["streams"] if s["codec_type"] == "video"); a = next(s for s in pr["streams"] if s["codec_type"] == "audio")
dur = float(pr["format"]["duration"]); fps = eval(v["r_frame_rate"])
res["probe"] = dict(w=v["width"], h=v["height"], fps=fps, vcodec=v["codec_name"], acodec=a["codec_name"], sr=a["sample_rate"], dur=round(dur, 2), mb=round(int(pr["format"]["size"]) / 2**20, 2))
check("format 1080x1920@30 h264+aac 48 kHz, 35-55 s", v["width"] == 1080 and v["height"] == 1920 and abs(fps - 30) < 0.01 and a["codec_name"] == "aac" and a["sample_rate"] == "48000" and 35 <= dur <= 55, res["probe"])

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
    # onset density: 50 ms windows, rise > 6 dB over the previous 150 ms floor, above -55 dBFS, >= 80 ms apart
    x, sr = sf.read(OUT / "stem_sfx.wav"); x = x.mean(1) if x.ndim > 1 else x
    w5 = int(0.05 * sr); e5 = np.array([20 * np.log10(np.sqrt(np.mean(x[i:i + w5] ** 2)) + 1e-9) for i in range(0, len(x) - w5, w5)])
    ons, last = [], -99
    for i in range(3, len(e5)):
        if e5[i] > -55 and e5[i] - e5[i - 3:i].min() > 6 and e5[i] >= e5[i - 1] and (i - last) * 0.05 >= 0.08:
            ons.append(i); last = i
    res["sfx"]["onsets"] = len(ons); res["sfx"]["onsets_per_s"] = round(len(ons) / dur, 2)
    # round 4: the target band is now the gate (L-6/L-13: 1.77/s on QR read as clutter)
    check("SFX onset density 1.2-1.5 /s", 1.2 <= len(ons) / dur <= 1.5, dict(onsets_per_s=res["sfx"]["onsets_per_s"], onsets=len(ons)))
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

# 4a-r8. captions never dimmed (Sky_v7 0:38 critic blocker: pages faded in from opacity 0 -> ghost frames).
#        Every frame inside a spoken word (outside the card and the loop fade) must show caption fill at full
#        strength: >= 400 px brighter than 225 AND >= 400 px of the black stroke (< 30) in the caption band.
cap = subprocess.run(f"ffmpeg -v error -i {MP4} -vf crop=984:208:48:1222,format=gray -f rawvideo -", shell=True, capture_output=True).stdout
cb = np.frombuffer(cap, np.uint8).reshape(-1, 208, 984)
_ws = words(SLUG); _ca = phrase_time(_ws, "That's the mechanism")
_fade_from = len(cb) - LOOP_FRAMES - T_FRAMES
need_cap = sorted({k for w in _ws for k in range(int(np.ceil(w["start"] * fps)) + 1, int(w["end"] * fps))
                   if k < _fade_from and not (_ca - 0.2 <= k / fps <= _ca + 2.0)})
ghost = [k for k in need_cap if k < len(cb) and ((cb[k] > 225).sum() < 400 or (cb[k] < 30).sum() < 400)]
runs_g, cur_g = [], []
for k in ghost:
    if cur_g and k != cur_g[-1] + 1: runs_g.append(cur_g); cur_g = []
    cur_g.append(k)
if cur_g: runs_g.append(cur_g)
res["captions_full_opacity"] = dict(frames_checked=len(need_cap), ghost_frames=len(ghost), worst_runs=[[round(r[0] / fps, 2), len(r)] for r in sorted(runs_g, key=len, reverse=True)[:6]])
check("captions: never dimmed while a word is spoken (no ghost frames)", len(ghost) <= max(2, 0.005 * len(need_cap)) and all(len(r) <= 1 for r in runs_g), res["captions_full_opacity"])

# 4a-r8b. captions are the SCRIPT words, aligned to whisper.cpp timing (scripts/captions.py writes captions_align.json)
_alp = ROOT / "episodes" / SLUG / "captions_align.json"
if _alp.exists():
    _al = json.loads(_alp.read_text()); res["captions_align"] = {k: _al.get(k) for k in ("match_rate", "max_unmatched_run", "unmatched", "window_violations", "initial_prompt")}
    check("captions: script-aligned (match >= 90 %, no unmatched run > 3 words, words inside their TTS chunk)", _al.get("ok"), res["captions_align"])
else:
    check("captions: script-aligned (match >= 90 %, no unmatched run > 3 words, words inside their TTS chunk)", False, dict(error="captions_align.json missing: re-run scripts/captions.py"))

# 4c-r8. meaningful-motion hold (Sky_v7 critic cap "static for > 2 s"): ambient particles/drift do not count. Change is
#        measured on a blurred stage (sigma 3 px at 1/5 scale, so dots and grain vanish) over 0.33 s; motion counts only
#        when one connected region >= 1 % of the stage changes. Longest run without it <= 1.75 s, excluding the end hold
#        (catchphrase card onward) and the loop whip.
from scipy import ndimage as _ndi
_bl = np.stack([_ndi.gaussian_filter(x, 3) for x in fr]); _W = 10; _big = []
for i in range(len(_bl) - _W):
    m = np.abs(_bl[i + _W] - _bl[i]) > 8
    if m.sum() < 0.01 * m.size: _big.append(0.0); continue
    lab, n = _ndi.label(m); _big.append(float(np.bincount(lab.ravel())[1:].max() / m.size) if n else 0.0)
_end = int((card_at - 0.2) * fps) if (card_at := phrase_time(words(SLUG), "That's the mechanism")) else len(_big)
_runs, _cur = [], 0
for i, b in enumerate(_big[:_end]):
    _cur = _cur + 1 if b < 0.01 else 0
    if _cur and (i + 1 == _end or _big[i + 1] >= 0.01): _runs.append((round((i - _cur + 1) / fps, 2), round((_cur + _W) / fps, 2)))
_worst = max(_runs, key=lambda r: r[1], default=(0, 0))
res["meaningful_motion"] = dict(longest_s=_worst[1], at_s=_worst[0], over_limit=[r for r in sorted(_runs, key=lambda r: -r[1]) if r[1] > 1.75][:6], limit_s=1.75)
check("motion: meaningful (structure-level) change at least every 1.75 s (particles/drift don't count; end hold excluded)", _worst[1] <= 1.75, res["meaningful_motion"])

# 4b. end card hold (round 4, from L-9): (a) the "THAT'S THE MECHANISM." card is up long enough to read,
#     (b) the payoff state is complete and settled >= 1.5 s before the loop whip starts.
ws_all = words(SLUG)
card_at = phrase_time(ws_all, "That's the mechanism")
k_mech = next(i for i, w in enumerate(ws_all) if w["start"] >= card_at and "mechanism" in w["text"].lower())
card_until = ws_all[k_mech + 1]["start"] if k_mech + 1 < len(ws_all) else dur
whip = len(fr) - LOOP_FRAMES - T_FRAMES  # first frame of the loop whip (LoopBack starts at loopFrom - T_FRAMES)
ref = fr[whip - 1]; k = whip - 1
while k > 0 and np.abs(fr[k] - ref).mean() < 6.0: k -= 1
settled = (whip - 1 - k) / fps
res["end_card"] = dict(card_s=round(card_until - card_at, 2), payoff_settled_s=round(settled, 2), payoff_settled_from_s=round((k + 1) / fps, 2), whip_at_s=round(whip / fps, 2))
check("end card: catchphrase card >= 1.0 s and payoff settled >= 1.5 s before loop", card_until - card_at >= 1.0 and settled >= 1.5, res["end_card"])

# 5. hook visual in the first second (subject already drawn at 0.3 s and stage changes before 1 s)
f9 = fr[9]; bright = float((f9 > 90).mean())
moved = float(np.abs(fr[29] - fr[0]).mean())
res["hook"] = dict(bright_frac_at_0_3s=round(bright, 3), change_0_to_1s=round(moved, 2))
check("hook: subject on screen at 0.3 s and visible change by 1 s", bright > 0.02 and moved > 1.0, res["hook"])
# round 4 (L-14): frame 0 must read as a bright, finished picture (the thumbnail/first impression); v3 Elevator was 0.04
b0 = float((fr[0] > 90).mean()); res["hook"]["bright_frac_at_0s"] = round(b0, 3)
# r8 hook gate: frame 1 already shows a hero/anomaly (one connected high-contrast structure >= 8 % of the stage) that is
#    MOVING (>= 5 % of stage pixels change by > 25 levels within the first 0.33 s). Sky_v7 (critic: "static title card"):
#    1.6 %; QR/Elevator/ANC 13-60 %.
from scipy import ndimage as _nd
_g = np.hypot(_nd.sobel(fr[0], 0), _nd.sobel(fr[0], 1)) > 60
_lab, _n = _nd.label(_nd.binary_dilation(_g, iterations=2))
_hero = float(np.bincount(_lab.ravel())[1:].max() / _g.size) if _n else 0.0
_mv = float((np.abs(fr[10] - fr[0]) > 25).mean())
_hc = json.loads((ROOT / "pipeline.config.json").read_text()).get("hooks", {})
res["hook"].update(hero_frac_frame0=round(_hero, 3), moved_frac_0_to_0_33s=round(_mv, 4))
check("hook: frame 1 has a moving hero/anomaly (hero >= 8 % of stage, >= 5 % of pixels change in 0.33 s)", _hero >= _hc.get("frame1_min_hero_frac", 0.08) and _mv >= _hc.get("frame1_min_moved_frac", 0.05), dict(hero_frac=round(_hero, 3), moved_frac=round(_mv, 4)))
check("hook: frame 0 bright (>= 12% of stage pixels > 90/255) and at 0.3 s", b0 >= 0.12 and bright >= 0.12, dict(bright_frac_at_0s=round(b0, 3), bright_frac_at_0_3s=round(bright, 3)))

# 6. exact loop: seam jump (last -> first) vs normal frame-to-frame motion, full frame
full = subprocess.run(f"ffmpeg -v error -i {MP4} -vf scale=270:480,format=gray -f rawvideo -", shell=True, capture_output=True).stdout
ff = np.frombuffer(full, np.uint8).reshape(-1, 480, 270).astype(np.float32)
cons = np.abs(np.diff(ff, axis=0)).mean(axis=(1, 2)); seam = float(np.abs(ff[-1] - ff[0]).mean())
mse = float(((ff[-1] - ff[0]) ** 2).mean()); psnr = 99.0 if mse == 0 else 10 * np.log10(255 ** 2 / mse)
res["loop"] = dict(seam_diff=round(seam, 2), median_step=round(float(np.median(cons)), 2), p95_step=round(float(np.percentile(cons, 95)), 2), psnr_last_vs_first=round(psnr, 1))
check("loop: seam jump <= p95 frame step (and PSNR >= 25 dB)", seam <= np.percentile(cons, 95) and psnr >= 25, res["loop"])

# 6b. label contrast, WCAG >= 4.5:1 on real pixels (round 4, from L-8/L-13; scripts/contrast.py)
if "--no-contrast" not in sys.argv:
    try:
        _cuts = ",".join(f"{phrase_time(ws_all, r['at']):.2f}" for r in shots(SLUG) if r["at"])
    except Exception:
        _cuts = ""
    cr = subprocess.run([sys.executable, str(ROOT / "scripts" / "contrast.py"), ID, str(MP4), str(OUT), "--cuts", _cuts,
                         "--card", f"{card_at:.2f},{card_until:.2f}"], capture_output=True, text=True)
    try:
        c = json.loads((OUT / "contrast.json").read_text()); res["contrast"] = c
        check("labels: WCAG contrast >= 4.5:1 (held >= 0.6 s)", c["ok"], dict(min=c["min_ratio"], p10=c["p10_ratio"], failures=[(f["t_start_s"], f["worst_ratio"]) for f in c["held_failures"]]))
        # r5: Shorts UI safe zones on the same probe masks (top 220, bottom >1560, right column x>900 below y 900)
        check("labels: inside Shorts UI safe zones + >= 24 px from side edges", c.get("safe_zone_ok", True), dict(violations=c.get("safe_zone_violations", [])[:6]))
        check("labels: icon/label clearance >= 36 px (held >= 0.6 s)", c.get("overlap_ok", True),
              dict(min_clearance=c.get("overlap_min_clearance"), violations=c.get("overlap_violations", [])[:6]))
        # r6 (critic R-002, 3 episodes): badges never snap in at full size; component = TagLabel/Pill pop
        check("motion: badge entrances pop with anticipation/overshoot (incl. hand-rolled badges)", c.get("pop_ok", True),
              dict(entrances=c.get("pop_entrances"), handrolled_tracks=c.get("pop_handrolled_tracks"), snaps=c.get("pop_snaps", [])[:6]))
        # r7 (critic, Sky_v6 0:35): no more than 3 pills/badges on the stage at once (held >= 0.6 s)
        check("layout: callout clutter <= 3 pills/badges at once (held >= 0.6 s)", c.get("clutter_ok", True),
              dict(peak=c.get("clutter_peak"), violations=c.get("clutter_violations", [])[:6]))
    except Exception as e:
        check("labels: WCAG contrast >= 4.5:1 (held >= 0.6 s)", False, dict(error=str(e), stderr=cr.stderr[-400:]))

# 6c. label minimum readable font size (routed from critic repeated finding across all episodes)
ep_tsx = ROOT / "remotion" / "src" / "episodes" / f"{ID}.tsx"
if ep_tsx.exists():
    small_labels = [int(m) for m in re.findall(r"<Label[^>]*\bsize=\{(\d+)\}", ep_tsx.read_text()) if int(m) < 30]
    res["label_sizes"] = dict(min_allowed=30, small_labels=small_labels)
    check("labels: minimum font size >= 30 px on all <Label> elements", len(small_labels) == 0, res["label_sizes"])
    # r5 (L-19 open item): raw SVG <text fontSize={N}> and CSS fontSize: N in the episode AND the shared brand kit
    raw_small = []
    for src in [ep_tsx, *sorted((ROOT / "remotion" / "src" / "brand").glob("*.tsx"))]:
        for ln, line in enumerate(src.read_text().splitlines(), 1):
            for m in re.finditer(r"fontSize(?:=\{|:\s*)(\d+)", line):
                if int(m.group(1)) < 30: raw_small.append(f"{src.name}:{ln}:{m.group(1)}px")
    res["raw_text_sizes"] = dict(min_allowed=30, small=raw_small)
    check("text: no raw SVG/CSS fontSize < 30 px (episode + brand kit)", not raw_small, res["raw_text_sizes"])

# 6c-r7. slide-deck boxing (scripts/framing.py): no whole-stage card held >= 1 s, boxed framing <= 50 % of runtime
if "--no-framing" not in sys.argv:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "framing.py"), str(MP4), str(OUT), "--card", f"{card_at:.2f},{card_until:.2f}"], capture_output=True, text=True)
    try:
        fj = json.loads((OUT / "framing.json").read_text()); res["framing"] = {k: v for k, v in fj.items() if k != "series"}
        check("framing: no whole-stage card >= 1 s, boxed framing <= 50 % of runtime", fj["ok"],
              dict(boxed_frac=fj["boxed_frac"], whole_stage_card=fj["whole_stage_card_runs"][:6]))
    except Exception as e:
        check("framing: no whole-stage card >= 1 s, boxed framing <= 50 % of runtime", False, dict(error=str(e)))
# 6c-r8. every element entrance arrives with motion (scripts/entrances.py): no snaps, no opacity-only fades (Sky_v7 critic cap)
if "--no-entrances" not in sys.argv:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "entrances.py"), str(MP4), str(OUT), "--cuts", _cuts if "_cuts" in dir() else "",
                    "--card", f"{card_at:.2f},{card_until:.2f}"], capture_output=True, text=True)
    try:
        ej = json.loads((OUT / "entrances.json").read_text()); res["entrances"] = ej
        check("motion: every element entrance scales/slides/draws on (no snaps, <= 2 opacity-only fades)", ej["ok"],
              dict(entrances=ej["entrances"], snaps=ej["snaps"][:5], fades=ej["fades"][:5]))
    except Exception as e:
        check("motion: every element entrance scales/slides/draws on (no snaps, <= 2 opacity-only fades)", False, dict(error=str(e)))
# 6c-r8b. planned key labels stay readable during their beat (OCR on the render; Elevator v7 tie-break lost CAR/CW + MOTOR labels)
if "--no-labels" not in sys.argv:
    try:
        sys.path.insert(0, str(ROOT / "scripts")); import labels_persist as _lp
        lp = _lp.check(ID, SLUG, MP4); res["labels_persist"] = lp; (OUT / "labels_persist.json").write_text(json.dumps(lp, indent=1))
        check("labels: every shots.md key label is readable in its shot and stays (OCR)", lp["ok"],
              dict(labels=lp["labels"], failing=lp["failing"][:5]))
    except Exception as e:
        check("labels: every shots.md key label is readable in its shot and stays (OCR)", False, dict(error=str(e)[:300]))
    # VO sync is ADVISORY: a pixel-motion event near each beat word does not catch semantic lag (v6b and v7 both pass)
    try:
        import vo_sync as _vs
        vs = _vs.check(ID, SLUG, MP4); res["vo_sync_advisory"] = {k: vs[k] for k in ("ok", "beats", "missed", "consecutive_miss", "tol_s")}
    except Exception as e:
        res["vo_sync_advisory"] = dict(error=str(e)[:300])
# 6c-r7b. no decorative HUD / fake timecodes (AI LABS 'AI tells'); the real chapter deck lives in brand/Chrome.tsx, not here
from static_gates import checks as _static_checks
for _name, _ok, _detail in _static_checks(ID, SLUG):
    if _name.startswith("text: no decorative HUD"):
        res["hud"] = _detail; check(_name, _ok, _detail)
    elif _name.startswith(("hook:", "clarity:")):  # r8
        res.setdefault("hook_static", {})[_name] = _detail; check(_name, _ok, _detail)

# 6d. visual-state change cadence (r5, Gemini/The Why Side: a new visual state every 3-4 s, not just motion):
#     a "state change" = stage ROI differs from 0.5 s earlier by >= STATE_DIFF mean grey levels; max gap between changes <= 4.0 s
STATE_DIFF = 10.0  # calibrated on v4: p50 3-9, p90 30-60; at 10 v4 has 4.0-4.6 s gaps (QR 6.0 s, Elevator 20.0 s, Sky 10.2 s)
dd = np.abs(fr[15:] - fr[:-15]).mean(axis=(1, 2))
ev = np.where(dd >= STATE_DIFF)[0] + 15
gaps_s = np.diff(np.concatenate([[0], ev, [len(fr) - 1]])) / fps
worst = int(np.argmax(gaps_s)) if len(gaps_s) else 0
res["state_changes"] = dict(threshold=STATE_DIFF, max_gap_s=round(float(gaps_s.max()), 2), at_s=round(float(np.concatenate([[0], ev])[worst] / fps), 2), p90_diff=round(float(np.percentile(dd, 90)), 2))
check("cadence: visual-state change at least every 4.0 s", gaps_s.max() <= 4.0, res["state_changes"])

# 6e. dramatic beat (r5, Gemini): 0.2-0.3 s of near-silence in the FULL MIX right before "That's the mechanism."
xa = subprocess.run(f"ffmpeg -v error -i {MP4} -vn -ac 1 -ar 48000 -f f32le -", shell=True, capture_output=True).stdout
xa = np.frombuffer(xa, np.float32)
i1 = int((card_at - 0.03) * 48000); i0 = int((card_at - 0.23) * 48000)
pre_db = float(20 * np.log10(np.sqrt(np.mean(xa[i0:i1] ** 2)) + 1e-9)) if i1 > i0 > 0 else 0.0
res["pre_catchphrase"] = dict(window_s=[round(card_at - 0.23, 2), round(card_at - 0.03, 2)], rms_db=round(pre_db, 1))
check("beat: >= 0.2 s near-silence (<= -38 dBFS RMS) before the catchphrase", pre_db <= -38, res["pre_catchphrase"])

# 7. visual review sheets
def sheets():
    ws = words(SLUG); bounds = [phrase_time(ws, r["at"]) for r in shots(SLUG) if r["at"]] + [dur - 0.02]
    rows = []
    for k, t in enumerate(bounds):
        ts = [max(0, min(dur - 0.04, t + o)) for o in (-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.33, 0.5)]
        if k == len(bounds) - 1: ts = [dur - 0.5, dur - 0.4, dur - 0.3, dur - 0.2, dur - 0.1, dur - 0.04, 0.0, 0.1]  # loop seam -> frame 0
        files = []
        for j, tt in enumerate(ts):
            p = OUT / f"_t{k}_{j}.png"; seek = f"-sseof -{max(0.05, dur - tt + 0.04):.2f}" if tt >= dur - 0.18 else f"-ss {tt:.3f}"
            sh(f"ffmpeg -v error -y {seek} -i {MP4} -frames:v 1 -update 1 -vf scale=270:-1 {p}")
            if not p.exists():
                sh(f"ffmpeg -v error -y -sseof -0.15 -i {MP4} -frames:v 1 -update 1 -vf scale=270:-1 {p}")
            files.append(p)
        r = OUT / f"_row{k}.png"; sh("ffmpeg -v error -y " + " ".join(f"-i {p}" for p in files) + f" -filter_complex hstack=inputs={len(files)} {r}"); rows.append(r)
    sh("ffmpeg -v error -y " + " ".join(f"-i {r}" for r in rows) + f" -filter_complex vstack=inputs={len(rows)} {OUT}/transitions_it{IT}.png")
    sh(f"ffmpeg -v error -y -i {MP4} -vf fps=1/1.5,scale=216:-1,tile=8x5 -frames:v 1 {OUT}/grid_it{IT}.png")
    for p in OUT.glob("_*.png"): p.unlink()


sheets() if '--no-sheets' not in sys.argv else None
res["checks"] = checks; res["iteration"] = IT
(OUT / f"report_it{IT}.json").write_text(json.dumps(res, indent=2))
for c in checks: print(("PASS" if c["ok"] else "FAIL"), "|", c["check"], "|", json.dumps(c["detail"]))
print("VISUAL (reviewer):", f"{OUT}/transitions_it{IT}.png", f"{OUT}/grid_it{IT}.png", "— overlaps, caption readability, SFX sync, style failure list")
