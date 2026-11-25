#!/usr/bin/env python3
"""Independent multimodal video critic using Gemini Files API (watches MP4 WITH audio).

Usage:
  scripts/critic.py <CompositionId> [--mp4 path/to/video.mp4] [--out-dir qa/<Id>/v4] [--models gemini-2.5-pro,gemini-2.5-flash,gemini-3-flash-preview]

Environment:
  GEMINI_API_KEY   Required. Sent only in the x-goog-api-key header (never logged).
  SUF              Render/QA suffix (default: v4).

Outputs:
  <out_dir>/critic.json   Structured scores (1-10), timestamped issues, suggestions, model & token metadata
  <out_dir>/critic.md     Human-readable review summary
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metrics

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://generativelanguage.googleapis.com"
# r5: 2.5-* return 404 for new users (L-20); 3.1-pro-preview has ~0 free-tier quota (429, L-22).
DEFAULT_MODELS = ["gemini-3.1-pro-preview", "gemini-3.8-flash", "gemini-3-flash-preview"]
REF_SHEET = ROOT / "research" / "r5" / "flatvector" / "sheet.jpg"

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "scores": {
            "type": "OBJECT",
            "properties": {
                "hook": {"type": "INTEGER"},
                "pacing": {"type": "INTEGER"},
                "clarity": {"type": "INTEGER"},
                "animation_quality": {"type": "INTEGER"},
                "audio_sfx_balance": {"type": "INTEGER"},
                "voice": {"type": "INTEGER"},
                "captions": {"type": "INTEGER"},
                "loop": {"type": "INTEGER"},
            },
            "required": [
                "hook", "pacing", "clarity", "animation_quality",
                "audio_sfx_balance", "voice", "captions", "loop",
            ],
        },
        "overall_score": {"type": "NUMBER"},
        "timestamped_issues": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "timestamp": {"type": "STRING"},
                    "severity": {"type": "STRING", "enum": ["blocker", "major", "minor"]},
                    "category": {"type": "STRING"},
                    "issue": {"type": "STRING"},
                },
                "required": ["timestamp", "severity", "category", "issue"],
            },
        },
        "suggestions": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
        },
        "summary": {"type": "STRING"},
    },
    "required": ["scores", "overall_score", "timestamped_issues", "suggestions", "summary"],
}

PROMPT = """You are an independent, demanding senior motion-graphics & short-form video critic reviewing a finished 1080x1920 vertical explainer ("That's the Mechanism") WITH BOTH VIDEO AND AUDIO.

Watch and listen to the entire video from frame 0 through the final loop whip. Grade honestly and strictly (1-10 integers; 7 = solid/publishable, 8 = strong, 9 = exceptional, <=6 = needs another pass):
1. hook (0:00-0:03): Does frame 0 grab attention immediately? Does the title + visual reveal pull the viewer in?
2. pacing: Does every 1-3 s advance the idea cleanly without dead air or rushed cuts?
3. clarity: Is the mechanism instantly understandable? Do the visuals, labels, and real-photo proof card support the narration rather than fight it?
4. animation_quality: Easing, anticipation/overshoot, secondary mechanical/physical motion, camera work, depth, zero cheap static slides.
5. audio_sfx_balance: Are SFX crisp, well-timed to visual beats, and balanced nicely under the voice (neither buried nor harsh/cluttered)?
6. voice: Clarity, cadence, pronunciation, naturalness, loudness consistency.
7. captions: Readability, contrast, zero overlap with stage graphics/pills/safe zones, accurate sync to speech.
8. loop: Does the ending settle cleanly and whip smoothly back to frame 0?

Return JSON matching the schema. Be specific with MM:SS timestamps (e.g. "0:14", "0:32") for every real issue you spot, and give concrete, actionable suggestions."""



# ---------------------------------------------------------------- calibrated (r5)
CAL_DIMS = {  # weight in overall
    "hook": 0.14, "clarity": 0.14, "motion_craft": 0.15, "design_typography": 0.12,
    "concept_wow": 0.09, "style_fidelity": 0.08, "finish_texture": 0.07,
    "sound_sync": 0.10, "voice_captions": 0.06, "loop": 0.05,
}
_ISSUE = {
    "type": "OBJECT",
    "properties": {
        "timestamp": {"type": "STRING"},
        "severity": {"type": "STRING", "enum": ["blocker", "major", "minor"]},
        "category": {"type": "STRING"},
        "issue": {"type": "STRING"},
        "fix": {"type": "STRING"},
    },
    "required": ["timestamp", "severity", "category", "issue", "fix"],
    "propertyOrdering": ["timestamp", "severity", "category", "issue", "fix"],
}
CAL_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "weaknesses": {"type": "ARRAY", "items": _ISSUE},
        "reference_gaps": {"type": "ARRAY", "items": {"type": "STRING"}},
        "strengths": {"type": "ARRAY", "items": {"type": "STRING"}},
        "caps_triggered": {"type": "ARRAY", "items": {"type": "STRING"}},
        "scores": {
            "type": "OBJECT",
            "properties": {k: {"type": "INTEGER"} for k in CAL_DIMS},
            "required": list(CAL_DIMS),
            "propertyOrdering": list(CAL_DIMS),
        },
        "verdict": {"type": "STRING", "enum": ["SHIP", "ONE MORE PASS"]},
        "summary": {"type": "STRING"},
    },
    "required": ["weaknesses", "reference_gaps", "strengths", "caps_triggered", "scores", "verdict", "summary"],
    "propertyOrdering": ["weaknesses", "reference_gaps", "strengths", "caps_triggered", "scores", "verdict", "summary"],
}

CAL_PROMPT = """You are a senior motion-design jury member (Motionographer editor / Buck creative director) AND a YouTube Shorts
retention editor. You did NOT make this film; the builder is not the judge. Judge harshly and precisely: kindness is useless,
specificity is everything. The film is a 1080x1920 vertical science-explainer Short ("That's the Mechanism"), flat 2D
vector motion graphics with voice-over, SFX and burned-in captions. Watch AND listen from frame 0 to the last frame.

REFERENCE BAR (what 8+ looks like):
- Jared Owen: every mechanical part moves physically and continuously; camera orbits explain the 3D relationship; zero
  static slides.
- Animagraffs: dense, precise mechanism detail; labels are crisp, large and perfectly placed; parts animate in sequence.
- The Why Side: one big idea per beat; bold flat shapes; a visual-state change every 2-4 s; tight punchy VO-to-picture sync.
- mg-styles-15 "Flat Vector" film (contact sheet attached as an image when present): anticipation -> stretch -> squash ->
  overshoot -> settle on entries, 2-4 frame staggers, one hero moving at a time, shape-wipe / element-driven transitions,
  bold flat palette. An expert jury scored THAT film 7.6/10 on this same scale. Use it as the anchor: anything less
  crafted than it must score below 7.6 on motion_craft/style_fidelity.

ANCHORED SCALE (integers): 5 = competent student work; 6 = decent template level (clean but generic, "AI-template");
7 = solid professional; 8 = high-end agency; 9 = award shortlist; 10 = best in the world. MOST RENDERS DESERVE 5-7.
A 9 requires that you could not name a single major weakness in that dimension. Do not inflate. Do not average upward
because the video is "competent".

HARD CAPS (apply them and list each one you trigger in caps_triggered):
- Any on-screen stage that is visually static (no meaningful motion) for > 2 s -> motion_craft <= 6.
- Elements that pop in/out with no easing, anticipation or overshoot -> motion_craft <= 6.
- Generic or template look (stock-like icons dropped on a plain background, slide-deck feel) -> style_fidelity <= 6 and concept_wow <= 6.
- Any label/text you must squint at on a phone (< ~30 px at 1080 wide) or that collides with captions -> design_typography <= 6.
- The mechanism cannot be understood with sound OFF from the picture alone -> clarity <= 6.
- Frame 0-1 s shows no single clear subject or no motion -> hook <= 6.
- SFX buried, harsh, repetitive or "bleepy" synthetic UI tones -> sound_sync <= 6.
- Ending does not settle and loop cleanly -> loop <= 5.

FORMAT CONVENTIONS of this channel (deliberate, owner-approved; do NOT penalize them as style breaks): the top brand chip
and episode meta line, burned-in word captions, the lower chapter/progress deck, the "THAT'S THE MECHANISM." end card, and
"REAL PHOTO" proof cards (documentary evidence inside the flat style). The film LOOPS BY DESIGN: the last ~0.5 s whips back
into frame 0; judge the loop by whether the payoff settles and the whip lands on the opening frame (measured seam data,
when given below, is authoritative).

DIMENSIONS: hook (0-3 s: single subject, instant curiosity), clarity (mechanism understood; picture carries it),
motion_craft (easing, spacing, overlap, anticipation/follow-through, arcs, transitions, camera), design_typography
(composition, hierarchy, type size and setting, palette, negative space, safe zones), concept_wow (a clear visual idea and an
unmistakable hero moment, beyond a diagram), style_fidelity (canonical flat-vector craft), finish_texture (detail, depth,
grain/shadow where apt, no aliasing/banding), sound_sync (SFX design, hits locked to picture, mix under VO),
voice_captions (VO naturalness and caption readability/sync), loop (settle + seamless return to frame 0).

PROCESS (order matters - fill the JSON fields in this order):
1. weaknesses: list 6-12 concrete, observable weaknesses FIRST, ordered by impact, each with MM:SS timestamp, severity,
   and a concrete fix (technique + numbers: frames, px, easing, colour). At least one fix must raise the wow factor.
2. reference_gaps: for each reference above, one sentence on the biggest gap between this film and it.
3. strengths: at most 4.
4. caps_triggered.
5. scores - only now, consistent with the weaknesses and caps you listed.
6. verdict: SHIP only if every dimension >= 7 and there is no blocker/major weakness; otherwise ONE MORE PASS.
"""

VERIFY_ADDON = """

VERIFICATION ROUND: a previous independent critic reviewed an earlier version of this film and listed the items below.
For EACH item, add one entry to weaknesses whose category is "verify:<n>" and whose issue starts with FIXED, PARTLY or
STILL PRESENT followed by what you observe now (use severity minor for FIXED). Then list any NEW weaknesses as usual.
Previous items:
"""

MEASURED_ADDON = """

MEASURED QA (automated, trust these numbers over your own impression of the same property):
"""


CMP_DIMS = list(CAL_DIMS)
CMP_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "weaknesses_A": {"type": "ARRAY", "items": {"type": "STRING"}},
        "weaknesses_B": {"type": "ARRAY", "items": {"type": "STRING"}},
        "per_dimension": {
            "type": "ARRAY",
            "items": {"type": "OBJECT", "properties": {
                "dimension": {"type": "STRING", "enum": CMP_DIMS},
                "better": {"type": "STRING", "enum": ["A", "B", "tie"]},
                "margin": {"type": "INTEGER"},
                "why": {"type": "STRING"}},
                "required": ["dimension", "better", "margin", "why"],
                "propertyOrdering": ["dimension", "better", "margin", "why"]},
        },
        "preferred": {"type": "STRING", "enum": ["A", "B", "tie"]},
        "preference_strength": {"type": "INTEGER"},
        "confidence": {"type": "STRING", "enum": ["low", "medium", "high"]},
        "summary": {"type": "STRING"},
    },
    "required": ["weaknesses_A", "weaknesses_B", "per_dimension", "preferred", "preference_strength", "confidence", "summary"],
    "propertyOrdering": ["weaknesses_A", "weaknesses_B", "per_dimension", "preferred", "preference_strength", "confidence", "summary"],
}
CMP_PROMPT = """You are a senior motion-design jury member and YouTube Shorts retention editor. You made neither film.
You get TWO versions of the same 1080x1920 vertical science-explainer Short ("That's the Mechanism"), same script and voice:
VIDEO A is the FIRST attached video, VIDEO B is the SECOND. Watch and listen to both completely.
Judge which version a demanding viewer would rather watch and share, as a motion designer would: motion craft (easing,
anticipation/overshoot, secondary motion, continuous mechanical motion, camera), visual richness vs. a flat diagram,
clarity of the mechanism with sound off, typography/legibility, finish, sound design and sync, hook, loop.
Order of work: 1) list the weaknesses of A, 2) list the weaknesses of B, 3) for EVERY dimension say which is better and by
how much (margin 0 = tie, 1 = slight, 2 = clear, 3 = night and day), 4) overall preference and its strength (0-3).
Do not reward length of your own analysis; ignore which one is first. Ties are allowed only if you truly cannot tell."""


def cal_overall(scores: dict) -> float:
    w = sum(CAL_DIMS[k] * scores[k] for k in CAL_DIMS)
    # weakest-link cap: one bad dimension caps the overall at min+2
    return round(min(w, min(scores[k] for k in CAL_DIMS) + 2.0), 2)


def measured_lines(report: Path) -> str:
    try:
        r = json.loads(report.read_text())
    except Exception:
        return ""
    out = []
    for k, v in r.items():
        if isinstance(v, (int, float, str, bool)) and len(str(v)) < 80:
            out.append(f"- {k}: {v}")
        elif isinstance(v, dict) and "ok" in v:
            out.append(f"- {k}: ok={v.get('ok')} " + ", ".join(f"{a}={b}" for a, b in v.items() if a != 'ok' and not isinstance(b, (list, dict)))[:160])
    return "\n".join(out[:40])


def upload_video(mp4: Path, api_key: str) -> dict:
    size = mp4.stat().st_size
    start = requests.post(
        f"{BASE_URL}/upload/v1beta/files",
        headers={
            "x-goog-api-key": api_key,
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(size),
            "X-Goog-Upload-Header-Content-Type": "video/mp4",
            "Content-Type": "application/json",
        },
        json={"file": {"display_name": mp4.name}},
        timeout=30,
    )
    start.raise_for_status()
    upload_url = start.headers["X-Goog-Upload-URL"]

    with mp4.open("rb") as fh:
        fin = requests.post(
            upload_url,
            headers={
                "Content-Length": str(size),
                "X-Goog-Upload-Offset": "0",
                "X-Goog-Upload-Command": "upload, finalize",
            },
            data=fh,
            timeout=300,
        )
    fin.raise_for_status()
    fobj = fin.json().get("file", fin.json())
    name = fobj["name"]

    for _ in range(90):
        st = requests.get(
            f"{BASE_URL}/v1beta/{name}",
            headers={"x-goog-api-key": api_key},
            timeout=30,
        )
        st.raise_for_status()
        info = st.json()
        state = info.get("state")
        if state == "ACTIVE":
            return info
        if state == "FAILED":
            raise RuntimeError(f"Gemini file processing failed: {info.get('error')}")
        time.sleep(2)
    raise TimeoutError(f"Timed out waiting for Gemini file {name} to become ACTIVE")


def delete_video(name: str, api_key: str) -> None:
    try:
        requests.delete(
            f"{BASE_URL}/v1beta/{name}",
            headers={"x-goog-api-key": api_key},
            timeout=15,
        )
    except Exception:
        pass


def call_model(model: str, file_uri: str, api_key: str, prompt: str = PROMPT,
               schema: dict = RESPONSE_SCHEMA, ref_image: Path | None = None, first_uri: str | None = None) -> dict:
    import base64
    def vid(uri: str) -> dict:  # r5: VIDEO_FPS env samples more frames (default API sampling is 1 fps -> misses 4-frame punches)
        part = {"file_data": {"mime_type": "video/mp4", "file_uri": uri}}
        if os.environ.get("VIDEO_FPS"):
            part["video_metadata"] = {"fps": float(os.environ["VIDEO_FPS"])}
        return part
    parts = ([{"text": "VIDEO A:"}, vid(first_uri), {"text": "VIDEO B:"}] if first_uri else []) + [vid(file_uri)]
    if ref_image and ref_image.exists():
        parts.append({"text": "Attached image: contact sheet (0.5 s steps) of the mg-styles-15 Flat Vector reference film, jury score 7.6/10."})
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(ref_image.read_bytes()).decode()}})
    parts.append({"text": prompt})
    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": schema,
        },
    }
    resp = requests.post(
        f"{BASE_URL}/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json=body,
        timeout=300,
    )
    if resp.status_code == 429:
        try:  # r5: surface which quota (daily vs per-minute) so the caller knows whether waiting helps
            det = resp.json().get("error", {}).get("details", [])
            ids = [v.get("quotaId") for d in det for v in d.get("violations", [])]
            delay = next((d.get("retryDelay") for d in det if "retryDelay" in d), "?")
        except Exception:
            ids, delay = [], "?"
        raise RuntimeError(f"429 quota ({model}) {ids} retry={delay}")
    resp.raise_for_status()
    return resp.json()


def render_md_cal(data: dict) -> str:
    s = data["scores"]
    L = [f"# Calibrated Critic — {data['episode']} ({data['label']})", "",
         f"- **File:** `{data['mp4']}`", f"- **Model:** `{data['model']}` · samples {data.get('samples', 1)} · free tier `$0.00`",
         f"- **Overall (weighted, weakest-link capped):** **{data['overall_score']:.2f} / 10** · verdict **{data['verdict']}**",
         f"- **Generated:** {data['timestamp']}", "", "## Weaknesses (listed before scoring)"]
    for it in data.get("weaknesses", []):
        L.append(f"- **[{it['timestamp']}] ({it['severity']} · {it['category']})** {it['issue']} — *fix:* {it.get('fix','')}")
    L += ["", "## Gaps vs reference channels"] + [f"- {g}" for g in data.get("reference_gaps", [])]
    L += ["", "## Strengths"] + [f"- {g}" for g in data.get("strengths", [])]
    L += ["", "## Caps triggered"] + ([f"- {g}" for g in data.get("caps_triggered", [])] or ["- none"])
    L += ["", "## Scores", "| Dimension | Score |", "|---|---:|"] + [f"| {k} | {s[k]} |" for k in CAL_DIMS]
    if data.get("score_samples"):
        L += ["", "Per-sample overall: " + ", ".join(f"{x:.2f}" for x in data["score_samples"])]
    L += ["", "## Summary", data.get("summary", "").strip(), ""]
    return "\n".join(L)


def render_md(data: dict) -> str:
    s = data["scores"]
    lines = [
        f"# Video Critic Report — {data['episode']}",
        "",
        f"- **File:** `{data['mp4']}`",
        f"- **Model:** `{data['model']}` (free tier, `$0.00`)",
        f"- **Overall score:** **{data['overall_score']:.1f} / 10**",
        f"- **Generated:** {data['timestamp']}",
        "",
        "## Scores",
        "| Dimension | Score |",
        "|---|---:|",
    ]
    for k in ("hook", "pacing", "clarity", "animation_quality", "audio_sfx_balance", "voice", "captions", "loop"):
        lines.append(f"| {k} | {s[k]} / 10 |")
    lines += ["", "## Summary", data.get("summary", "").strip(), "", "## Timestamped Issues"]
    issues = data.get("timestamped_issues", [])
    if not issues:
        lines.append("- None flagged.")
    else:
        for it in issues:
            lines.append(f"- **[{it['timestamp']}] ({it['severity']} · {it['category']})** {it['issue']}")
    lines += ["", "## Suggestions"]
    for sg in data.get("suggestions", []):
        lines.append(f"- {sg}")
    lines.append("")
    return "\n".join(lines)


def compare_main(args, api_key: str, mp4_b: Path, out_dir: Path, models: list) -> int:
    mp4_a = Path(args.compare)
    t0 = time.time(); fa = fb = None; raw = None; used = None; last = ""
    try:
        fa = upload_video(mp4_a, api_key); fb = upload_video(mp4_b, api_key)
        for m in models:
            for attempt in range(2):
                try:
                    raw = call_model(m, fb["uri"], api_key, CMP_PROMPT, CMP_SCHEMA, None, first_uri=fa["uri"]); break
                except Exception as exc:
                    last = f"{m}: {exc}"[:200]; print(f"[critic] {m} attempt {attempt + 1} failed ({str(exc)[:80]})", file=sys.stderr)
                    if "429" in str(exc) or "404" in str(exc): break
                    time.sleep(8)
            if raw is not None: used = m; break
        if raw is None: raise RuntimeError(f"All models failed ({last})")
    finally:
        for fo in (fa, fb):
            if fo and fo.get("name"): delete_video(fo["name"], api_key)
    res = json.loads(raw["candidates"][0]["content"]["parts"][0]["text"]); usage = raw.get("usageMetadata", {})
    sign = {"A": -1, "B": 1, "tie": 0}
    net = sum(sign[d["better"]] * d["margin"] * CAL_DIMS.get(d["dimension"], 0.1) for d in res["per_dimension"])
    out = {"episode": args.id, "label": args.label, "mode": "compare", "A": str(mp4_a), "B": str(mp4_b), "model": used,
           "wall_s": round(time.time() - t0, 2), "cost_usd": 0.0, "weighted_margin_B_minus_A": round(net, 2),
           "usage": {"prompt_tokens": usage.get("promptTokenCount"), "output_tokens": usage.get("candidatesTokenCount")},
           "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"), **res}
    j = out_dir / f"{args.name}.json"; j.write_text(json.dumps(out, indent=2))
    md = [f"# Pairwise critic — {args.id} ({args.label})", "", f"- A: `{mp4_a}`", f"- B: `{mp4_b}`", f"- Model: `{used}` · free tier $0",
          f"- **Preferred: {res['preferred']}** (strength {res['preference_strength']}/3, confidence {res['confidence']}); weighted margin B−A = {net:+.2f}", "",
          "## Weaknesses A"] + [f"- {w}" for w in res["weaknesses_A"]] + ["", "## Weaknesses B"] + [f"- {w}" for w in res["weaknesses_B"]] + \
         ["", "| dimension | better | margin | why |", "|---|---|---:|---|"] + [f"| {d['dimension']} | {d['better']} | {d['margin']} | {d['why']} |" for d in res["per_dimension"]] + ["", res["summary"], ""]
    (out_dir / f"{args.name}.md").write_text("\n".join(md))
    metrics.record({"ts": out["timestamp"], "ep": f"{args.id}:{args.label}", "stage": "critic", "iter": None,
                    "cmd": f"critic.py {args.id} --compare --model {used}", "exit": 0, "wall_s": out["wall_s"], "cpu_s": 0.0, "peak_rss_mb": 0,
                    "out": str(j), "out_mb": round(j.stat().st_size / 2**20, 4), "model": used,
                    "prompt_tokens": usage.get("promptTokenCount"), "output_tokens": usage.get("candidatesTokenCount"), "cost_usd": 0.0})
    print(f"[{args.id}] compare model={used} preferred={res['preferred']} strength={res['preference_strength']} conf={res['confidence']} margin(B-A)={net:+.2f}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("id", help="Composition id (e.g. QR, Elevator, Sky)")
    ap.add_argument("--mp4", help="Path to MP4 (default: renders/<Id>_<SUF>.mp4)")
    ap.add_argument("--out-dir", help="Output directory (default: qa/<Id>/<SUF>)")
    ap.add_argument("--models", default=",".join(DEFAULT_MODELS), help="Comma-separated model fallback order")
    ap.add_argument("--label", default="", help="Optional label stored in metadata (e.g. baseline_v3)")
    ap.add_argument("--mode", choices=["calibrated", "legacy"], default="calibrated", help="legacy = round-4 prompt (kept for before/after)")
    ap.add_argument("--samples", type=int, default=1, help="Independent samples; scores are averaged (calibrated mode)")
    ap.add_argument("--verify", help="Previous critic.json: ask a fresh critic FIXED/PARTLY/STILL PRESENT per item (Gauntlet)")
    ap.add_argument("--qa-report", help="qa report_it*.json whose measurements are given to the critic")
    ap.add_argument("--no-ref", action="store_true", help="Do not attach the Flat Vector reference contact sheet")
    ap.add_argument("--name", default="critic", help="Output basename (critic -> critic.json/critic.md)")
    ap.add_argument("--compare", help="Pairwise mode: this MP4 is VIDEO A, --mp4 is VIDEO B (e.g. A = last owner-approved render)")
    args = ap.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is not set", file=sys.stderr)
        return 2

    suf = os.environ.get("SUF", "v4")
    mp4 = Path(args.mp4) if args.mp4 else ROOT / "renders" / f"{args.id}_{suf}.mp4"
    if not mp4.is_absolute():
        mp4 = ROOT / mp4
    if not mp4.exists():
        print(f"ERROR: MP4 not found: {mp4}", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir) if args.out_dir else ROOT / "qa" / args.id / suf
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    t0 = time.time()
    finfo = None
    last_err = None
    used_model = None
    raw_resp = None

    cal = args.mode == "calibrated"
    prompt, schema = (CAL_PROMPT, CAL_SCHEMA) if cal else (PROMPT, RESPONSE_SCHEMA)
    if args.compare:
        return compare_main(args, api_key, mp4, out_dir, models)
    if cal and args.verify:
        prev = json.loads(Path(args.verify).read_text())
        items = prev.get("weaknesses") or prev.get("timestamped_issues") or []
        prompt += VERIFY_ADDON + "\n".join(f"{i+1}. [{it.get('timestamp')}] {it.get('issue')}" for i, it in enumerate(items))
    if cal and args.qa_report:
        ml = measured_lines(Path(args.qa_report))
        if ml:
            prompt += MEASURED_ADDON + ml
    ref = None if (args.no_ref or not cal) else REF_SHEET
    samples = []
    usage_tot = {"promptTokenCount": 0, "candidatesTokenCount": 0, "totalTokenCount": 0}
    try:
        finfo = upload_video(mp4, api_key)
        file_uri = finfo["uri"]
        for _ in range(max(1, args.samples if cal else 1)):
            raw_resp = None
            order = ([used_model] + [m for m in models if m != used_model]) if used_model else models
            for m in order:
                for attempt in range(2):  # transient 503 / dropped connections get one retry
                    try:
                        raw_resp = call_model(m, file_uri, api_key, prompt, schema, ref)
                        break
                    except Exception as exc:
                        last_err = f"{m}: {exc}"[:200]
                        transient = "429" not in str(exc) and "404" not in str(exc)
                        print(f"[critic] {m} attempt {attempt + 1} failed ({type(exc).__name__}: {str(exc)[:80]})", file=sys.stderr)
                        if not transient:
                            break
                        time.sleep(8)
                if raw_resp is not None:
                    if used_model and m != used_model:
                        print(f"[critic] WARNING: sample model changed {used_model} -> {m}", file=sys.stderr)
                    used_model = used_model or m
                    break
            if raw_resp is None:
                if samples:
                    print(f"[critic] keeping {len(samples)} sample(s); later sample failed ({last_err})", file=sys.stderr)
                    break
                raise RuntimeError(f"All models failed ({last_err})")
            samples.append(json.loads(raw_resp["candidates"][0]["content"]["parts"][0]["text"]))
            for k in usage_tot:
                usage_tot[k] += raw_resp.get("usageMetadata", {}).get(k) or 0
    finally:
        if finfo and finfo.get("name"):
            delete_video(finfo["name"], api_key)

    wall = round(time.time() - t0, 2)
    critique = samples[0]
    usage = usage_tot
    if cal:
        per = [cal_overall(x["scores"]) for x in samples]
        if len(samples) > 1:
            critique["scores"] = {k: round(sum(x["scores"][k] for x in samples) / len(samples), 1) for k in CAL_DIMS}
            critique["score_samples"] = per
        critique["overall_score"] = round(sum(per) / len(per), 2)
        critique["samples"] = len(samples)

    out = {
        "episode": args.id,
        "label": args.label or suf,
        "mode": args.mode,
        "mp4": str(mp4.relative_to(ROOT)) if mp4.is_relative_to(ROOT) else str(mp4),
        "model": used_model,
        "wall_s": wall,
        "cost_usd": 0.0,
        "usage": {
            "prompt_tokens": usage.get("promptTokenCount"),
            "output_tokens": usage.get("candidatesTokenCount"),
            "total_tokens": usage.get("totalTokenCount"),
        },
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        **critique,
    }

    jpath = out_dir / f"{args.name}.json"
    mpath = out_dir / f"{args.name}.md"
    jpath.write_text(json.dumps(out, indent=2))
    mpath.write_text(render_md_cal(out) if cal else render_md(out))

    metrics.record({
        "ts": out["timestamp"],
        "ep": f"{args.id}:{args.label}" if args.label else args.id,
        "stage": "critic",
        "iter": None,
        "cmd": f"critic.py {args.id} --mode {args.mode} --model {used_model} --samples {len(samples)}",
        "exit": 0,
        "wall_s": wall,
        "cpu_s": 0.0,
        "peak_rss_mb": 0,
        "out": str(jpath),
        "out_mb": round(jpath.stat().st_size / 2**20, 4),
        "model": used_model,
        "prompt_tokens": usage.get("promptTokenCount"),
        "output_tokens": usage.get("candidatesTokenCount"),
        "cost_usd": 0.0,
    })

    print(f"[{args.id}] model={used_model} overall={out['overall_score']:.1f}/10 wall={wall}s -> {jpath}")
    print("  scores:", json.dumps(out["scores"]))
    if cal:
        print("  verdict:", out.get("verdict"), "caps:", out.get("caps_triggered"))
    for it in (out.get("weaknesses") or out.get("timestamped_issues", []))[:6]:
        print(f"  - [{it['timestamp']}] ({it['severity']}) {it['issue']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
