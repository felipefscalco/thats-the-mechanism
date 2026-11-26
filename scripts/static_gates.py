#!/usr/bin/env python3
"""Source-level gates shared by qa.py (full render) and preview.py (stills): run on the episode .tsx + brand kit, no render."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
HUD_RE = re.compile(r"[\"'>`]\s*((?:\d{1,2}:\d{2}(?::\d{2})?(?:[.:]\d{1,3})?)|REC\b[^\"'<`]{0,8}|T\s?[+-]\s?\d+[^\"'<`]{0,6}|\d+\s?FPS|ISO\s?\d+|HUD\b)")


def checks(comp_id: str, slug: str = None):
    out = []
    ep = ROOT / "remotion" / "src" / "episodes" / f"{comp_id}.tsx"
    if not ep.exists():
        return out
    src = ep.read_text()
    small = [int(m) for m in re.findall(r"<Label[^>]*\bsize=\{(\d+)\}", src) if int(m) < 30]
    out.append(("labels: minimum font size >= 30 px on all <Label> elements", not small, dict(min_allowed=30, small_labels=small)))
    raw_small = []
    for f in [ep, *sorted((ROOT / "remotion" / "src" / "brand").glob("*.tsx"))]:
        for ln, line in enumerate(f.read_text().splitlines(), 1):
            for m in re.finditer(r"fontSize(?:=\{|:\s*)(\d+)", line):
                if int(m.group(1)) < 30: raw_small.append(f"{f.name}:{ln}:{m.group(1)}px")
    out.append(("text: no raw SVG/CSS fontSize < 30 px (episode + brand kit)", not raw_small, dict(min_allowed=30, small=raw_small)))
    hud = sorted(set(HUD_RE.findall(src)))
    out.append(("text: no decorative HUD / fake timecode strings in the episode", not hud, dict(matches=hud)))
    # r9 atomic text (Sky v8 critic blocker: ghost text faded in apart from its pill). Every episode string is drawn by a kit
    # component (Label / TagLabel / Badge / Pill / TitleHook), which are fully opaque from their first visible frame and
    # share one transform with their backing. Raw SVG <text>/<tspan> or a CSS text div in an episode bypasses that.
    raw = [f"{ln}: {line.strip()[:80]}" for ln, line in enumerate(src.splitlines(), 1) if re.search(r"<(text|tspan)\b", line)]
    out.append(("text: atomic labels only (no raw <text>/<tspan> in the episode; use Label/TagLabel/Badge/Pill)", not raw, dict(raw=raw[:10])))
    if slug: out += hook_and_clarity(comp_id, slug) + payoff_hold(slug) + hero_marked(slug)
    return out


def payoff_hold(slug):
    """r9: the mix leaves >= hold_s of settled payoff after the last word, before the loop whip (0.8 s). The stage is frozen
    for that hold by EpisodeShell (PAYOFF_HOLD_S); the measured twin is qa.py 'end card ... payoff settled'."""
    import json
    hold = json.loads((ROOT / "pipeline.config.json").read_text()).get("qa_gates", {}).get("payoff", {}).get("hold_s", 1.5)
    try:
        d = json.loads((ROOT / "remotion/src/durations.json").read_text())[slug]
        w = json.loads((ROOT / "episodes" / slug / "captions.json").read_text())
    except Exception as e:
        return [("payoff: >= 1.5 s settled hold after the last word (mix tail)", False, dict(error=str(e)[:200]))]
    room = round(d - 0.8 - w[-1]["end"], 2)
    return [(f"payoff: >= {hold} s settled hold after the last word (mix tail)", room >= hold, dict(duration_s=d, last_word_end_s=w[-1]["end"], hold_room_s=room))]


def hook_and_clarity(comp_id, slug):
    """r8 hook gates that need no render + the sound-off clarity gate."""
    import json, sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import hooks, clarity
    from shotlib import shots
    cfg = json.loads((ROOT / "pipeline.config.json").read_text()).get("hooks", {})
    out = []
    caps = json.loads((ROOT / "episodes" / slug / "captions.json").read_text())
    t0 = caps[0]["start"] if caps else 99
    out.append((f"hook: first speech <= {cfg.get('first_speech_max_s', 0.5)} s", t0 <= cfg.get("first_speech_max_s", 0.5), dict(first_word=caps[0]["text"] if caps else None, start_s=round(t0, 2))))
    rows = shots(slug); first = rows[0]["text"][0] if rows and rows[0]["text"] else ""
    nw = len(first.split()); mx = cfg.get("max_onscreen_words", 7)
    out.append((f"hook: first on-screen line <= {mx} words", 0 < nw <= mx, dict(line=first, words=nw)))
    h = hooks.check(slug)
    out.append(("hook: opening has a curiosity gap, no padding/clickbait, promise paid off", h["ok"], dict(first_sentence=h["first_sentence"], failures=h["failures"], signals=h["curiosity"]["signals"], payoff_match=h["payoff_match"])))
    c = clarity.check(comp_id, slug)
    out.append(("clarity: every causal step shows an on-screen keyword (sound-off test)", c["ok"], dict(covered=f"{c['covered']}/{c['steps']}", missing=[(m["t_s"], m["sentence"][:60]) for m in c["missing"]][:6])))
    return out


def hero_marked(slug):
    """r9: shots.md marks the ONE special moment as a beat `hero@<spoken phrase>` (measured by scripts/hero.py)."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from shotlib import shots, words, phrase_time
    hb = [(r["n"], p) for r in shots(slug) for k, p in r["beats"] if k == "hero"]
    ok, why = len(hb) == 1, None
    if ok:
        try: phrase_time(words(slug), hb[0][1])
        except KeyError as e: ok, why = False, str(e)
    return [("hero: shots.md marks exactly one hero@<spoken phrase> beat", ok, dict(hero_beats=hb, error=why))]
