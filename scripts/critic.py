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
DEFAULT_MODELS = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-3-flash-preview"]

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


def call_model(model: str, file_uri: str, api_key: str) -> dict:
    body = {
        "contents": [{
            "role": "user",
            "parts": [
                {"file_data": {"mime_type": "video/mp4", "file_uri": file_uri}},
                {"text": PROMPT},
            ],
        }],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
        },
    }
    resp = requests.post(
        f"{BASE_URL}/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json=body,
        timeout=240,
    )
    resp.raise_for_status()
    return resp.json()


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("id", help="Composition id (e.g. QR, Elevator, Sky)")
    ap.add_argument("--mp4", help="Path to MP4 (default: renders/<Id>_<SUF>.mp4)")
    ap.add_argument("--out-dir", help="Output directory (default: qa/<Id>/<SUF>)")
    ap.add_argument("--models", default=",".join(DEFAULT_MODELS), help="Comma-separated model fallback order")
    ap.add_argument("--label", default="", help="Optional label stored in metadata (e.g. baseline_v3)")
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

    try:
        finfo = upload_video(mp4, api_key)
        file_uri = finfo["uri"]
        for m in models:
            try:
                raw_resp = call_model(m, file_uri, api_key)
                used_model = m
                break
            except Exception as exc:
                last_err = f"{m}: {type(exc).__name__}"
                print(f"[critic] fallback from {m} ({type(exc).__name__})", file=sys.stderr)
                continue
        if raw_resp is None:
            raise RuntimeError(f"All models failed ({last_err})")
    finally:
        if finfo and finfo.get("name"):
            delete_video(finfo["name"], api_key)

    wall = round(time.time() - t0, 2)
    cand = raw_resp["candidates"][0]["content"]["parts"][0]["text"]
    critique = json.loads(cand)
    usage = raw_resp.get("usageMetadata", {})

    out = {
        "episode": args.id,
        "label": args.label or suf,
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

    jpath = out_dir / "critic.json"
    mpath = out_dir / "critic.md"
    jpath.write_text(json.dumps(out, indent=2))
    mpath.write_text(render_md(out))

    metrics.record({
        "ts": out["timestamp"],
        "ep": f"{args.id}:{args.label}" if args.label else args.id,
        "stage": "critic",
        "iter": None,
        "cmd": f"critic.py {args.id} --model {used_model}",
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
    for it in out.get("timestamped_issues", [])[:5]:
        print(f"  - [{it['timestamp']}] ({it['severity']}) {it['issue']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
