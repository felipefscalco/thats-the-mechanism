#!/usr/bin/env python3
"""Independent critic via the Antigravity CLI (`agy`), no API key needed (uses the owner's Antigravity login).
Same calibrated rubric, schema and weakest-link overall as scripts/critic.py (imported, not copied), so scores are comparable
in kind - but compare scores only within one model (L-22): the model id is recorded in every output.

The agent is asked to read the MP4 itself (video + audio). As evidence and fallback it also gets 2 fps frame sheets and the
word-timed transcript. It runs in plan mode (read-only) inside a sandbox; the builder never grades its own work.

Usage: .venv-tts/bin/python scripts/critic_agy.py <CompId> <slug> [--suf v1] [--iter N] [--model gemini-4-neon-high]
                                                  [--verify prev.json]
Writes qa/<Id>/<suf>/critic_agy[_N].{json,md} and a metrics line (cost $0 to this pipeline)."""
import argparse, json, subprocess, sys, time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from critic import CAL_DIMS, CAL_PROMPT, CAL_SCHEMA, MEASURED_ADDON, VERIFY_ADDON, cal_overall, measured_lines, render_md_cal  # noqa: E402


def to_jsonschema(s):
    """Gemini-style schema (TYPE upper-case, propertyOrdering) -> standard JSON schema."""
    if isinstance(s, dict):
        out = {}
        for k, v in s.items():
            if k == "propertyOrdering":
                continue
            out[k] = v.lower() if k == "type" and isinstance(v, str) else to_jsonschema(v)
        return out
    if isinstance(s, list):
        return [to_jsonschema(x) for x in s]
    return s


def frame_sheets(mp4: Path, out: Path) -> list:
    """2 fps frames tiled 6x4 per sheet (12 s per sheet), each frame stamped with its timecode."""
    # timecodes stamped with PIL: Homebrew's ffmpeg is built without drawtext (no libfreetype)
    from PIL import Image, ImageDraw
    out.mkdir(parents=True, exist_ok=True)
    for p in list(out.glob("sheet_*.jpg")) + list(out.glob("f_*.png")):
        p.unlink()
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp4), "-vf", "fps=2,scale=270:-1", str(out / "f_%04d.png")], check=True)
    frames = sorted(out.glob("f_*.png"))
    per, cols = 24, 6
    sheets = []
    for k in range(0, len(frames), per):
        chunk = [Image.open(p).convert("RGB") for p in frames[k:k + per]]
        w, h = chunk[0].size
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (w + 4) + 4, rows * (h + 4) + 4), (0, 0, 0))
        for i, im in enumerate(chunk):
            t = (k + i) / 2
            d = ImageDraw.Draw(im); d.rectangle([0, 0, 92, 22], fill=(0, 0, 0)); d.text((5, 5), f"{int(t // 60)}:{t % 60:04.1f}", fill=(255, 210, 0))
            sheet.paste(im, (4 + (i % cols) * (w + 4), 4 + (i // cols) * (h + 4)))
        sp = out / f"sheet_{k // per + 1:02d}.jpg"; sheet.save(sp, quality=85); sheets.append(sp)
    for p in frames:
        p.unlink()
    return sheets


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("id"); ap.add_argument("slug")
    ap.add_argument("--suf", default="v1"); ap.add_argument("--iter", type=int, default=1)
    ap.add_argument("--model", default="gemini-4-neon-high")
    ap.add_argument("--verify"); ap.add_argument("--timeout", default="900s")
    a = ap.parse_args()

    mp4 = ROOT / "renders" / f"{a.id}_{a.suf}.mp4"
    if not mp4.exists():
        sys.exit(f"missing {mp4}")
    qa_dir = ROOT / "qa" / a.id / a.suf
    sheets = frame_sheets(mp4, qa_dir / "critic_frames")
    words = json.loads((ROOT / "episodes" / a.slug / "captions.json").read_text())
    transcript = " ".join(f"[{w['start']:.1f}] {w['text']}" for w in words)
    report = qa_dir / f"report_it{a.iter}.json"
    measured = measured_lines(report) if report.exists() else ""

    prompt = CAL_PROMPT
    if a.verify:
        prev = json.loads(Path(a.verify).read_text())
        prompt += VERIFY_ADDON + "\n".join(f"{i + 1}. [{w.get('timestamp')}] {w.get('issue')}" for i, w in enumerate(prev.get("weaknesses", [])))
    if measured:
        prompt += MEASURED_ADDON + measured
    prompt += f"""

MATERIAL (absolute paths; read them with your file tools, do not modify anything in the repository):
- THE FILM (watch AND listen, start to end): {mp4}
- Frame sheets at 2 fps with timecodes (evidence / fallback if a part of the video is unclear): {', '.join(str(s) for s in sheets)}
- Word-timed voice-over transcript (seconds): {transcript}

Before the JSON, do the review in your head only. Your final answer must be ONLY the JSON object matching the schema,
with one extra top-level field "evidence": "video" if you watched/listened to the MP4 itself, otherwise "frames"."""

    schema = to_jsonschema(CAL_SCHEMA)
    schema["properties"]["evidence"] = {"type": "string", "enum": ["video", "frames"]}
    schema["required"] = schema["required"] + ["evidence"]
    schema_path = qa_dir / "critic_agy_schema.json"
    schema_path.write_text(json.dumps(schema))

    cmd = ["agy", "-p", prompt, "--model", a.model, "--mode", "plan", "--sandbox", "--output-format", "json",
           "--json-schema", str(schema_path), "--print-timeout", a.timeout, "--add-dir", str(qa_dir), "--add-dir", str(ROOT / "renders")]
    t0 = time.time()
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    wall = round(time.time() - t0, 1)
    if r.returncode:
        sys.exit(f"agy failed ({r.returncode}): {r.stderr[-1500:]}")
    raw = r.stdout.strip()
    data = None
    try:
        env = json.loads(raw)
        cand = env.get("structured_output") or env.get("result") or env if isinstance(env, dict) else env
        data = json.loads(cand) if isinstance(cand, str) else cand
    except json.JSONDecodeError:
        s, e = raw.find("{"), raw.rfind("}")
        data = json.loads(raw[s:e + 1])
    if not isinstance(data, dict) or "scores" not in data:
        # envelope without structured output: dig the JSON out of the text result
        txt = data.get("result", "") if isinstance(data, dict) else str(data)
        s, e = txt.find("{"), txt.rfind("}")
        data = json.loads(txt[s:e + 1])
    data["overall"] = data["overall_score"] = cal_overall(data["scores"])
    data.update(episode=a.id, label=a.suf, mp4=str(mp4.relative_to(ROOT)), timestamp=datetime.now().astimezone().isoformat(timespec="seconds"))
    data["model"] = f"agy:{a.model}"
    data["mode"] = "calibrated" + ("+verify" if a.verify else "")
    data["wall_s"] = wall

    name = f"critic_agy_{a.iter}" if a.iter > 1 else "critic_agy"
    (qa_dir / f"{name}.json").write_text(json.dumps(data, indent=1, ensure_ascii=False))
    (qa_dir / f"{name}.md").write_text(f"# Critic (Antigravity {a.model}, evidence={data.get('evidence')}) — {a.id} {a.suf}\n\n" + render_md_cal(data))
    with open(ROOT / "metrics" / "runs.jsonl", "a") as fh:
        fh.write(json.dumps(dict(ts=datetime.now().astimezone().isoformat(timespec="seconds"), ep=a.slug, stage="critic", iter=a.iter,
                                 cmd=f"agy {a.model} calibrated", exit=0, wall_s=wall, cpu_s=0, peak_rss_mb=0,
                                 out=str(qa_dir / f"{name}.json"), out_mb=None, cost_usd=0.0)) + "\n")
    s = data["scores"]
    print(f"{a.id} {a.suf}: overall {data['overall']}  verdict {data.get('verdict')}  evidence {data.get('evidence')}  ({wall}s)")
    print("  " + "  ".join(f"{k}={s[k]}" for k in CAL_DIMS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
