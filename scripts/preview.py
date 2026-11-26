#!/usr/bin/env python3
"""r7 preview-first gates: everything that can be judged on stills, with NO full render, master, stems or audio.

Builder/fixer iterations run this; the full render + master + audio gates (qa.py) run once at ship time.
  1. key stills (stills.mjs): frame 0, 0.3 s, 1.0 s, mid, last  -> hook brightness, change by 1 s, loop frame0 == last
  2. probe passes + normal-look stills from one bundle (contrast.py --preview) -> WCAG contrast (incl. raw SVG text),
     safe zone + side edges (+ intro frame-by-frame), icon/label clearance, badge pop (incl. hand-rolled), callout clutter
  3. framing.py on the normal stills -> whole-stage card / boxed framing
  4. stage hold + state-change cadence, approximated on the 0.2 s normal stills
  5. static_gates.py: label sizes, raw fontSize, HUD / fake timecodes
  6. contact sheet (1 still / 1.5 s) for the builder's self-critique
Usage: preview.py <CompId> <slug> <iter>   (SUF env as qa.py)  -> qa/<Id>/<SUF>/preview_it<N>.json + preview_sheet_it<N>.png
Exit 0 = all preview gates PASS.
"""
import json, os, shutil, subprocess, sys, time
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
from shotlib import ROOT, words, phrase_time, shots
import static_gates

ID, SLUG, IT = sys.argv[1], sys.argv[2], int(sys.argv[3])
SUF = os.environ.get("SUF", "v2")
OUT = ROOT / "qa" / ID / os.environ.get("QA_DIR", SUF); OUT.mkdir(parents=True, exist_ok=True)
PY = sys.executable
checks, res, T0 = [], {}, time.time()
def check(name, ok, detail): checks.append(dict(check=name, ok=bool(ok), detail=detail))

ws = words(SLUG)
card_at = phrase_time(ws, "That's the mechanism")
k = next(i for i, w in enumerate(ws) if w["start"] >= card_at and "mechanism" in w["text"].lower())
card_until = ws[k + 1]["start"] if k + 1 < len(ws) else ws[-1]["end"]
cuts = ",".join(f"{phrase_time(ws, r['at']):.2f}" for r in shots(SLUG) if r["at"])

# 1. key stills
KD = OUT / f"_keys_it{IT}"
t = time.time()
r = subprocess.run(["node", "stills.mjs", ID, str(KD), "0,9,29,mid,-1", "0.5", "{}"], cwd=ROOT / "remotion", capture_output=True, text=True)
if r.returncode: sys.exit(r.stderr[-1500:])
res["timing_keys_s"] = round(time.time() - t, 1)
g = lambda tok: np.asarray(Image.open(KD / f"still_{tok}.png").convert("L"), np.float32)
st = lambda a: a[145:595]  # stage band at half scale
f0, f9, f29, fl = g("0"), g("9"), g("29"), g("m1")
b0, b9 = float((st(f0) > 90).mean()), float((st(f9) > 90).mean())
check("hook: frame 0 bright (>= 12% of stage pixels > 90/255) and at 0.3 s", b0 >= 0.12 and b9 >= 0.12, dict(bright_frac_at_0s=round(b0, 3), bright_frac_at_0_3s=round(b9, 3)))
mv = float(np.abs(st(f29) - st(f0)).mean())
check("hook: visible change by 1 s", mv > 1.0, dict(change_0_to_1s=round(mv, 2)))
mse = float(((fl - f0) ** 2).mean()); psnr = 99.0 if mse == 0 else 10 * np.log10(255 ** 2 / mse)
check("loop: last frame == frame 0 (PSNR >= 25 dB, stills)", psnr >= 25, dict(psnr_last_vs_first=round(psnr, 1)))

# 2. probe gates on stills
t = time.time()
cr = subprocess.run([PY, str(ROOT / "scripts/contrast.py"), ID, "-", str(OUT / f"_pv_it{IT}"), "--preview", "--cuts", cuts, "--card", f"{card_at:.2f},{card_until:.2f}", "--keep-norm"],
                    capture_output=True, text=True)
res["timing_probe_s"] = round(time.time() - t, 1)
try:
    c = json.loads((OUT / f"_pv_it{IT}" / "contrast.json").read_text()); res["contrast"] = c
    check("labels: WCAG contrast >= 4.5:1 (held >= 0.6 s; raw SVG text included)", c["ok"], dict(min=c["min_ratio"], p10=c["p10_ratio"], failures=[(f["t_start_s"], f["worst_ratio"], f["bbox"]) for f in c["held_failures"]][:8]))
    check("labels: inside Shorts UI safe zones + >= 24 px from side edges (intro: any frame)", c.get("safe_zone_ok", True), dict(violations=c.get("safe_zone_violations", [])[:8]))
    check("labels: icon/label clearance >= 36 px (held >= 0.6 s)", c.get("overlap_ok", True), dict(min_clearance=c.get("overlap_min_clearance"), violations=[{k: v for k, v in o.items() if k != "detail"} for o in c.get("overlap_violations", [])[:8]]))
    check("motion: badge entrances pop with anticipation/overshoot (incl. hand-rolled badges)", c.get("pop_ok", True), dict(entrances=c.get("pop_entrances"), snaps=c.get("pop_snaps", [])[:8]))
    check("layout: callout clutter <= 3 pills/badges at once (held >= 0.6 s)", c.get("clutter_ok", True), dict(peak=c.get("clutter_peak"), violations=c.get("clutter_violations", [])[:6]))
except Exception as e:
    check("labels: probe gates ran", False, dict(error=str(e), stderr=cr.stderr[-600:]))

# 3. framing + 4. hold/cadence on the normal stills (every 6th frame = 0.2 s)
ND = OUT / f"_pv_it{IT}" / "_norm"
if ND.is_dir():
    subprocess.run([PY, str(ROOT / "scripts/framing.py"), str(ND), str(OUT / f"_pv_it{IT}"), "--card", f"{card_at:.2f},{card_until:.2f}"], capture_output=True, text=True)
    try:
        fj = json.loads((OUT / f"_pv_it{IT}" / "framing.json").read_text())
        check("framing: no whole-stage card >= 1 s, boxed framing <= 50 % of runtime", fj["ok"], dict(boxed_frac=fj["boxed_frac"], whole_stage_card=fj["whole_stage_card_runs"][:6]))
    except Exception as e:
        check("framing: ran", False, dict(error=str(e)))
    fr = np.stack([np.asarray(Image.open(p).convert("L").resize((216, 384)), np.float32)[58:238] for p in sorted(ND.glob("*.png"))])
    d = np.abs(fr[1:] - fr[:-1]).mean(axis=(1, 2)); still = d < 0.5
    longest = cur = 0
    for s_ in still: cur = cur + 1 if s_ else 0; longest = max(longest, cur)
    check("motion: no stage hold > 2.0 s (0.2 s stills, approx.)", longest * 0.2 <= 2.0, dict(longest_hold_s=round(longest * 0.2, 2)))
    dd = np.abs(fr[3:] - fr[:-3]).mean(axis=(1, 2)) if len(fr) > 3 else np.array([99.0])
    ev = np.where(dd >= 10.0)[0] + 3
    gaps = np.diff(np.concatenate([[0], ev, [len(fr) - 1]])) * 0.2
    check("cadence: visual-state change at least every 4.0 s (stills, approx.)", gaps.max() <= 4.0, dict(max_gap_s=round(float(gaps.max()), 2)))
    # 6. contact sheet: one still every 1.5 s, 8 columns
    ims = sorted(ND.glob("*.png"))[::max(1, int(1.5 / 0.2))]
    W, H = 216, 384; cols = 8; rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (W * cols, H * rows), (0, 0, 0))
    for i_, p in enumerate(ims): sheet.paste(Image.open(p).convert("RGB").resize((W, H)), ((i_ % cols) * W, (i_ // cols) * H))
    sheet.save(OUT / f"preview_sheet_it{IT}.png")
    keys = [Image.open(KD / f"still_{k_}.png").convert("RGB").resize((360, 640)) for k_ in ("0", "mid", "m1")]
    ks = Image.new("RGB", (1080, 640)); [ks.paste(im, (360 * i_, 0)) for i_, im in enumerate(keys)]; ks.save(OUT / f"keystills_it{IT}.png")
    shutil.rmtree(ND, ignore_errors=True)

# 5. static
for name, ok, detail in static_gates.checks(ID): check(name, ok, detail)
shutil.rmtree(KD, ignore_errors=True)
res.update(checks=checks, iteration=IT, mode="preview", wall_s=round(time.time() - T0, 1), contact_sheet=str(OUT / f"preview_sheet_it{IT}.png"), keystills=str(OUT / f"keystills_it{IT}.png"))
(OUT / f"preview_it{IT}.json").write_text(json.dumps(res, indent=1))
for c_ in checks: print(("PASS" if c_["ok"] else "FAIL"), "|", c_["check"], "|", json.dumps(c_["detail"])[:400])
print(f"preview wall {res['wall_s']} s -> {OUT}/preview_it{IT}.json")
sys.exit(0 if all(c_["ok"] for c_ in checks) else 1)
