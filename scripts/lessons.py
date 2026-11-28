#!/usr/bin/env python3
"""Merge critic `general_rules` into docs/style_rules.json + docs/STYLE_RULES.md.

Usage:
  scripts/lessons.py                  # scan qa/**/**.json, rewrite STYLE_RULES.md
  scripts/lessons.py --prompt         # print the active prose prompt on stdout

Promotion: a cluster becomes `active` if it appears in >= 2 episodes, or any supporting
severity is `blocker`. Enforcement prefers code over prose (AGENTS.md hierarchy):
  1. gate       — a known (or newly implemented) qa.py / contrast.py / facts.py check
  2. component  — a Remotion primitive that makes the error impossible
  3. prose      — only subjective craft; these alone are written out as followable rules

STYLE_RULES.md holds active prose rules plus an index pointing at the gate/component
for everything enforced in code. Measurable clusters with no gate yet are listed as
candidate gates (not silently left as prose).
"""
from __future__ import annotations
import json, re, sys, subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "docs" / "style_rules.json"
OUT_MD = ROOT / "docs" / "STYLE_RULES.md"
OUT_PROMPT = ROOT / "docs" / "active_rules_prompt.txt"
OUT_BACKLOG = ROOT / "docs" / "gate_backlog.json"   # r10: candidate gates + gate misses with evidence

KNOWN_GATES = [
    # r7: rules now implemented by gates (lessons.py marks their clusters `gate`, not `candidate_gate`)
    (r"overshoot|anticipation|snap(?:s|ped)? in|pop(?:s|ping)? in|appear(?:s)? (?:out of nowhere|from nothing)|nothing appears",
     "scripts/qa.py + scripts/contrast.py: badge entrances pop with anticipation/overshoot (incl. hand-rolled badges, A14)"),
    (r"\bboxed\b|box(?:ed)? fram|card frame|slide[- ]?(?:deck|show)|white card|enclosing (?:the )?(?:whole|entire) stage|container card|rounded box|floating cards?|isolated (?:floating )?cards?|nested card",
     "scripts/qa.py + scripts/framing.py: no whole-stage card >= 1 s, boxed framing <= 50 % of runtime (A16)"),
    (r"clutter|too many (?:pills|badges|callouts|labels)|(?:pills|badges|callouts) at once|simultaneous (?:pills|badges|callouts)",
     "scripts/qa.py + scripts/contrast.py: callout clutter <= 3 pills/badges at once (A17)"),
    (r"\bhud\b|timecode|fake (?:ui|data|readout)|decorative (?:readout|telemetry)",
     "scripts/static_gates.py: no decorative HUD / fake timecode strings (A18)"),
    (r"edge of the frame|frame edge|off[- ]screen|pushed off|clipped at the (?:left|right)|side edge",
     "scripts/qa.py + scripts/contrast.py: >= 24 px from side edges; intro (first 2 s) judged frame by frame (A15)"),
    (r"icon.{0,30}(label|pill)|label.{0,30}(icon|pill|overlap)|labels?.{0,20}clearance|clearance.{0,30}(label|icon|pill)|occupancy|LANE_GAP",
     "scripts/qa.py + scripts/contrast.py: labels: icon/label clearance >= 36 px (held >= 0.6 s)"),
    (r"font size|30 ?px|thirty pixels|squint",
     "scripts/qa.py: labels >= 30 px and no raw SVG/CSS fontSize < 30"),
    (r"wcag|contrast ratio|4\.5\s*(:|to)|four point five",
     "scripts/qa.py + scripts/contrast.py: WCAG contrast >= 4.5:1 (held >= 0.6 s)"),
    (r"safe zone",
     "scripts/qa.py: labels inside Shorts UI safe zones"),
    (r"visually static|stage.{0,24}static|static.{0,24}(stage|hold)|dead air|hold.*> ?2|stage hold|longer than two seconds|more than sixty frames",
     "scripts/qa.py: motion: no stage hold > 2.0 s"),
    (r"\bcadence\b|every 4(?:\.0)? s|state change at least",
     "scripts/qa.py: visual-state change at least every 4.0 s"),
    (r"silence|catchphrase|pre-catch",
     "scripts/qa.py: >= 0.2 s near-silence (<= -38 dBFS) before the catchphrase"),
    (r"\bloop\b|frame zero|frame 0|last frame|terminal frame|lock the final frame|initial visual|loop seam|psnr",
     "scripts/qa.py: loop seam jump <= p95 frame step and PSNR >= 25 dB"),
    (r"loudness|lufs",
     "scripts/qa.py: loudness -15.5..-13 LUFS, true peak <= -1 dBTP"),
    (r"\bsfx\b|whoosh|onset density|under the voice",
     "scripts/qa.py: SFX density 1.2-1.5/s and 10-16 dB under voice"),
    (r"caption.{0,40}(gap|spacing|fuse|glued|orphan)|(orphan|stranded?).{0,40}(word|caption)|between consecutive .{0,20}caption words",
     "scripts/qa.py + scripts/caption_spacing.py: caption words keep a gap, no orphan short word (A20)"),
    (r"\bfact|sources|unverified",
     "scripts/facts.py: spoken quantities covered by verified facts"),
]
# r10 gate_miss: KNOWN_GATES "where" -> prefix of the qa.py check that implements it. If the critic reports the rule on a
# render whose QA report shows that check PASSING, the gate exists but let the problem through: fix the gate, not the prompt.
GATE_CHECK = {
    "A14": "motion: badge entrances pop", "A16": "framing: no whole-stage card", "A17": "layout: callout clutter",
    "A18": "text: no decorative HUD", "A15": "labels: inside Shorts UI safe zones", "icon/label clearance": "labels: icon/label clearance",
    "labels >= 30 px": "labels: minimum font size", "WCAG contrast": "labels: WCAG contrast", "Shorts UI safe zones": "labels: inside Shorts UI safe zones",
    "no stage hold": "motion: no stage hold", "visual-state change": "cadence: visual-state change", "near-silence": "beat: >= 0.2 s near-silence",
    "loop seam": "loop: seam jump", "loudness": "loudness", "SFX density": "SFX", "A20": "captions: words keep a visible gap",
}


def check_for(where: str):
    return next((pref for key, pref in GATE_CHECK.items() if key in where), None)


def gate_misses(gates: list[str], members: list[dict]) -> list[dict]:
    out = []
    for m in members:
        rp = m.get("qa_report")
        if not rp or not (ROOT / rp).exists():
            continue
        try:
            checks = json.loads((ROOT / rp).read_text()).get("checks", [])
        except (OSError, json.JSONDecodeError):
            continue
        for where in gates:
            pref = check_for(where)
            hit = next((c for c in checks if pref and c["check"].startswith(pref)), None)
            if hit and hit["ok"]:
                out.append(dict(episode=m["episode"], timestamp=m["evidence"], check=hit["check"], qa_report=rp, source=m["source"]))
    return out


KNOWN_COMPONENTS = [
    (r"icon.{0,30}(label|pill)|label.{0,30}(icon|pill|overlap)|labels?.{0,20}clearance|clearance.{0,30}(label|icon|pill)|occupancy|LANE_GAP|\blane\b|labeledbox",
     "remotion/src/brand/Kit.tsx `Lane` / `LabeledBox` (LANE_GAP = 36)"),
    (r"\bloop\b|frame zero|frame 0|last frame|terminal frame|lock the final frame|initial visual|loopend|loopback",
     "remotion/src/brand/EpisodeShell.tsx `LoopEnd` / `LoopBack` (hook frozen at frame 0)"),
    (r"busy (art|background)|label on .*art|taglabel",
     "remotion/src/brand/Kit.tsx `TagLabel` (ink backing behind stage labels)"),
    (r"(debris|particles?|fluid|water|steam|stream|shards?).{0,80}(freez|mid-air|continu)|(freez|mid-air).{0,60}(debris|particles?|fluid|water|shards?)",
     "remotion/src/brand/frame.tsx `useAmbient()` (ambient motion keeps running through the payoff freeze; pinned to 0 in LoopBack)"),
]

STOP = {"the","a","an","and","or","to","of","in","on","for","with","from","that","this","it","is","be","as","at","by","not","no","never","always","keep","use","must","should","do","don't","than","then","into"}


def iter_critic_jsons():
    for p in sorted((ROOT / "qa").rglob("*.json")):
        if p.name in {"contrast.json", "captions.json"} or p.name.startswith("report_"):
            continue
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        if not isinstance(d, dict) or not d.get("general_rules"):
            continue
        yield p, d


def episode_id(data, path: Path) -> str:
    return str(data.get("episode") or data.get("label") or path.parent.parent.name)


def tokenize(rule: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", rule.lower()) if w not in STOP and len(w) > 2}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def match_known(rule: str, table):
    hits = []
    for pat, where in table:
        if re.search(pat, rule, re.I):
            hits.append(where)
    return hits


def collect():
    rows = []
    for path, data in iter_critic_jsons():
        ep = episode_id(data, path)
        model = data.get("model", "")
        for i, r in enumerate(data.get("general_rules") or []):
            rule = " ".join((r.get("rule") or "").split())
            if not rule:
                continue
            rows.append({
                "rule": rule,
                "category": r.get("category") or "",
                "evidence": r.get("evidence") or "",
                "measurable": bool(r.get("measurable")),
                "proposed_gate": r.get("proposed_gate") or "",
                "enforcement": r.get("enforcement") or "prose",
                "severity": r.get("severity") or "minor",
                "episode": ep,
                "source": str(path.relative_to(ROOT)),
                "model": model,
                "qa_report": data.get("qa_report"),
            })
    return rows


# Clustering-only themes (do not classify enforcement). Merge paraphrases that
# the token Jaccard would otherwise leave split across episodes.
CLUSTER_THEMES = [
    (r"overshoot|anticipation|spring(?:ing)?|easing|linear interpolation", "motion_easing"),
]


def family_keys(rule: str) -> frozenset:
    return frozenset(match_known(rule, KNOWN_GATES) + match_known(rule, KNOWN_COMPONENTS) + match_known(rule, CLUSTER_THEMES))


def close_to_cluster(rule: str, toks: set[str], c: dict, thresh: float) -> float:
    """Similarity in [0, 1], or -1 if the pair should not merge."""
    jac = jaccard(toks, c["tokens"])
    if jac >= thresh:
        return jac
    fa, fb = family_keys(rule), c.get("family") or frozenset()
    if fa and fb and fa == fb:
        return max(jac, 0.24)
    if fa and fb and (fa & fb) and jac >= 0.18:
        return jac
    return -1.0


def cluster_local(rows, thresh=0.25):
    # Paraphrases from the critic rarely share 45% of tokens; also merge rules that
    # already map to the same known gate / component.
    clusters = []
    for r in rows:
        toks = tokenize(r["rule"])
        best, best_s = None, -1.0
        for c in clusters:
            s = close_to_cluster(r["rule"], toks, c, thresh)
            if s > best_s:
                best, best_s = c, s
        if best is not None and best_s >= 0:
            best["members"].append(r)
            best["tokens"] |= toks
            best["family"] = (best.get("family") or frozenset()) | family_keys(r["rule"])
        else:
            clusters.append({"tokens": set(toks), "members": [r], "family": family_keys(r["rule"])})
    return clusters


def cluster_agy(rows):
    """Ask the clusterer role (any provider) to merge near-duplicates; fall back to Jaccard on any failure."""
    if len(rows) < 2 or "--local" in sys.argv:
        return cluster_local(rows)
    schema = {
        "type": "object",
        "properties": {
            "clusters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "canonical_rule": {"type": "string"},
                        "category": {"type": "string"},
                        "member_indexes": {"type": "array", "items": {"type": "integer"}},
                    },
                    "required": ["canonical_rule", "category", "member_indexes"],
                },
            }
        },
        "required": ["clusters"],
    }
    listing = "\n".join(f"{i}. [{r['episode']}] ({r['severity']}/{r['enforcement']}) {r['rule']}" for i, r in enumerate(rows))
    prompt = (
        "Cluster these critic general_rules into unique, episode-agnostic rules. "
        "Merge paraphrases of the same instruction. Do not invent rules that are not represented. "
        "canonical_rule must stay imperative and must not name a specific episode or subject.\n\n"
        + listing
    )
    try:
        import llm  # r7: vendor-neutral clusterer role (pipeline.config.json llm.roles.clusterer)
        r = llm.run("clusterer", prompt, ROOT, schema=schema, read_only=True, timeout_s=150)
        if not r["ok"]:
            raise RuntimeError(r["meta"].get("error"))
        parsed = r["json"]
        out = []
        used = set()
        for c in parsed["clusters"]:
            idxs = [i for i in c["member_indexes"] if 0 <= i < len(rows)]
            if not idxs:
                continue
            used.update(idxs)
            members = [rows[i] for i in idxs]
            out.append({"tokens": tokenize(c["canonical_rule"]), "members": members,
                        "canonical": " ".join(c["canonical_rule"].split()),
                        "category": c.get("category") or members[0]["category"]})
        leftover = [rows[i] for i in range(len(rows)) if i not in used]
        if leftover:
            out.extend(cluster_local(leftover))
        return out or cluster_local(rows)
    except Exception as exc:
        print(f"[lessons] clusterer role failed ({exc}); using local Jaccard", file=sys.stderr)
        return cluster_local(rows)


def classify(canonical: str, members: list[dict]) -> dict:
    gates = match_known(canonical, KNOWN_GATES)
    comps = match_known(canonical, KNOWN_COMPONENTS)
    for m in members:
        gates += match_known(m["rule"], KNOWN_GATES)
        comps += match_known(m["rule"], KNOWN_COMPONENTS)
    gates, comps = list(dict.fromkeys(gates)), list(dict.fromkeys(comps))
    measurable = any(m["measurable"] or m["proposed_gate"] for m in members)
    proposed = next((m["proposed_gate"] for m in members if m.get("proposed_gate")), "")
    # Prefer code over the model's own label.
    if gates:
        enforcement = "gate"
    elif comps:
        enforcement = "component"
    elif measurable:
        enforcement = "candidate_gate"
    else:
        enforcement = "prose"
    episodes = sorted({m["episode"] for m in members})
    sev_rank = {"blocker": 3, "major": 2, "minor": 1}
    severity = max(members, key=lambda m: sev_rank.get(m["severity"], 0))["severity"]
    active = len(episodes) >= 2 or severity == "blocker"
    categories = [m["category"] for m in members if m["category"]]
    category = max(set(categories), key=categories.count) if categories else ""
    return {
        "id": "",
        "rule": canonical,
        "category": category,
        "enforcement": enforcement,
        "active": active,
        "severity": severity,
        "measurable": measurable,
        "proposed_gate": proposed,
        "gates": gates,
        "components": comps,
        "episodes": episodes,
        "episode_count": len(episodes),
        "evidence": [{"episode": m["episode"], "timestamp": m["evidence"], "severity": m["severity"], "source": m["source"]} for m in members],
        "gate_miss": gate_misses(gates, members),
    }


def render_md(clusters: list[dict], generated: str) -> str:
    active = [c for c in clusters if c["active"]]
    prose = [c for c in active if c["enforcement"] == "prose"]
    code = [c for c in active if c["enforcement"] in {"gate", "component"}]
    candidates = [c for c in clusters if c["enforcement"] == "candidate_gate"]
    pending = [c for c in clusters if not c["active"]]
    L = [
        "# Style rules",
        "",
        f"Generated by `scripts/lessons.py` on {generated}. Do not edit by hand; change comes from critic `general_rules` plus this merger.",
        "Enforcement follows [AGENTS.md — Enforcement hierarchy: code over prose](../AGENTS.md#enforcement-hierarchy-code-over-prose): gate, then component, then prose.",
        "A cluster is **active** after it appears in ≥ 2 episodes, or in one episode as a blocker.",
        "",
        "## Active prose rules",
        "",
        "Follow these when writing a script or building a Remotion scene. They are subjective (or not yet measurable) and are injected into the script-writer / scene-builder prompt via `docs/active_rules_prompt.txt`.",
        "",
    ]
    if not prose:
        L.append("_None yet._")
    else:
        for i, c in enumerate(prose, 1):
            L += [f"{i}. **{c['rule']}**", f"   - category: `{c['category'] or '—'}` · severity {c['severity']} · seen in {c['episode_count']} episode(s): {', '.join(c['episodes'])}", ""]
    L += ["", "## Enforced in code (index)", "",
          "These active rules are **not** restated as instructions. The gate or component is the source of truth.",
          "", "| Rule | Class | Where |", "|---|---|---|"]
    if not code:
        L.append("| — | — | — |")
    else:
        for c in code:
            where = "; ".join(c["gates"] + c["components"]) or "—"
            L.append(f"| {c['rule']} | {c['enforcement']} | `{where}` |")
    L += ["", "## Candidate gates", "",
          "Measurable rules that are not yet an automated check. Implement these as `qa.py` gates before leaving them as prose.",
          ""]
    if not candidates:
        L.append("_None._")
    else:
        for c in candidates:
            status = "active" if c["active"] else "not yet active"
            L += [f"- **{c['rule']}** ({status}; {c['episode_count']} episode(s): {', '.join(c['episodes'])})",
                  f"  - proposed: {c['proposed_gate'] or '—'}", ""]
    misses = [c for c in clusters if c.get("gate_miss")]
    L += ["", "## Gate misses (a gate exists but the critic still saw it)", "",
          "The QA report of the judged render shows the gate PASSING while the critic reports the rule. Fix the gate (threshold, coverage, "
          "what it measures); until then the rule is also in the builder prompt.", ""]
    if not misses:
        L.append("_None._")
    else:
        for c in misses:
            ev_ = "; ".join(f"{g['episode']} {g['timestamp']} ({g['check']})" for g in c["gate_miss"][:4])
            L += [f"- **{c['rule']}**", f"  - missed by: {ev_}", ""]
    if pending:
        L += ["", "## Not yet active", ""]
        for c in pending:
            L.append(f"- ({c['enforcement']}, {c['episode_count']} ep) {c['rule']}")
    L.append("")
    return "\n".join(L)


def render_prompt(clusters: list[dict]) -> str:
    prose = [c for c in clusters if c["active"] and c["enforcement"] == "prose"]
    # r10: an active measurable rule with no gate yet, or one a gate missed, must not vanish between "not prose" and
    # "not code": it rides in the prompt as an INTERIM rule until scripts/qa.py enforces it (docs/gate_backlog.json).
    interim = [c for c in clusters if c["active"] and (c["enforcement"] == "candidate_gate" or c.get("gate_miss"))]
    lines = [
        "Active style rules (generated by scripts/lessons.py).",
        "Gates and Remotion primitives already enforce the measurable/structural rules — do not restate them here.",
        "Apply every item below to this episode:",
        "",
    ]
    if not prose:
        lines.append("(no active prose rules yet)")
    else:
        for i, c in enumerate(prose, 1):
            lines.append(f"{i}. {c['rule']}")
    if interim:
        lines += ["", "Interim rules (measurable, but no automated gate catches them yet - check them yourself on the preview stills):"]
        for i, c in enumerate(interim, 1):
            why = "a gate exists but missed it" if c.get("gate_miss") else "gate not written yet"
            lines.append(f"I{i}. {c['rule']} ({why})")
    lines.append("")
    return "\n".join(lines)


def write_backlog(clusters: list[dict]) -> None:
    """r10: the work list for turning rules into code (input of the gatesmith role): every active candidate gate and every
    gate miss, with the renders and timestamps that show the problem - the evidence a new gate must FAIL on."""
    items = []
    for c in clusters:
        if not c["active"] or not (c["enforcement"] == "candidate_gate" or c.get("gate_miss")):
            continue
        items.append(dict(id=c["id"], kind="gate_miss" if c.get("gate_miss") else "candidate_gate", rule=c["rule"],
                          category=c["category"], severity=c["severity"], proposed_gate=c["proposed_gate"],
                          existing_gates=c["gates"], misses=c.get("gate_miss", []), evidence=c["evidence"]))
    sev = {"blocker": 0, "major": 1, "minor": 2}
    items.sort(key=lambda x: (x["kind"] != "gate_miss", sev.get(x["severity"], 3), -len(x["evidence"])))
    OUT_BACKLOG.write_text(json.dumps(dict(generated=datetime.now().astimezone().isoformat(timespec="seconds"), items=items), indent=1, ensure_ascii=False))


def guard_active(new_clusters: list[dict]) -> None:
    """L-36 gate: qa/** critic JSONs are gitignored, so a fresh clone sees only its own episodes. Never let a rebuild
    silently drop a rule that is active in the committed docs/style_rules.json. Exit 3 (nothing written) unless --force."""
    if "--force" in sys.argv or not OUT_JSON.exists():
        return
    try:
        prev = [c for c in json.loads(OUT_JSON.read_text()).get("clusters", []) if c.get("active")]
    except (json.JSONDecodeError, OSError):
        return
    new_toks = [tokenize(c["rule"]) for c in new_clusters if c.get("active")]
    lost = [c["rule"] for c in prev if not any(jaccard(tokenize(c["rule"]), t) >= 0.5 for t in new_toks)]
    if lost:
        print(f"lessons.py: REFUSED - this rebuild would drop {len(lost)} active rule(s) from {OUT_JSON.relative_to(ROOT)} "
              "(their critic JSONs under qa/ are probably not on this machine). Nothing written. Re-run with --force only "
              "if dropping them is intended.", file=sys.stderr)
        for r in lost:
            print(f"  - {r[:140]}", file=sys.stderr)
        sys.exit(3)


def refresh() -> int:
    """r10: re-render STYLE_RULES.md, the builder prompt and the gate backlog from the COMMITTED docs/style_rules.json,
    without re-clustering (no critic JSONs needed, so a fresh clone gets the interim rules and the backlog too)."""
    data = json.loads(OUT_JSON.read_text())
    clusters = data.get("clusters", [])
    for c in clusters:
        c.setdefault("gate_miss", [])
        # re-check against the current KNOWN_GATES / KNOWN_COMPONENTS (a new gate or component promotes the rule to code)
        g = list(dict.fromkeys(c.get("gates", []) + match_known(c["rule"], KNOWN_GATES)))
        k = list(dict.fromkeys(c.get("components", []) + match_known(c["rule"], KNOWN_COMPONENTS)))
        if (g, k) != (c.get("gates", []), c.get("components", [])):
            c["gates"], c["components"] = g, k
            c["enforcement"] = "gate" if g else "component" if k else c["enforcement"]
    data["clusters"] = clusters
    OUT_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    OUT_MD.write_text(render_md(clusters, data.get("generated", "")))
    OUT_PROMPT.write_text(render_prompt(clusters))
    write_backlog(clusters)
    interim = sum(1 for c in clusters if c["active"] and (c["enforcement"] == "candidate_gate" or c.get("gate_miss")))
    print(f"lessons.py --refresh: {len(clusters)} clusters; {interim} interim rules in {OUT_PROMPT.relative_to(ROOT)}; backlog {OUT_BACKLOG.relative_to(ROOT)}")
    return 0


def _rows_from(path: Path) -> tuple[str, list[dict]]:
    p = path.resolve()
    key = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
    data = json.loads(p.read_text())
    ep = episode_id(data, p)
    rows = []
    for r in data.get("general_rules") or []:
        rule = " ".join((r.get("rule") or "").split())
        if rule:
            rows.append(dict(rule=rule, category=r.get("category") or "", evidence=r.get("evidence") or "",
                             measurable=bool(r.get("measurable")), proposed_gate=r.get("proposed_gate") or "",
                             enforcement=r.get("enforcement") or "prose", severity=r.get("severity") or "minor",
                             episode=ep, source=key, model=data.get("model", ""), qa_report=data.get("qa_report")))
    return key, rows


def _merge_into(c: dict, r: dict) -> None:
    sev = {"blocker": 3, "major": 2, "minor": 1}
    c["evidence"].append(dict(episode=r["episode"], timestamp=r["evidence"], severity=r["severity"], source=r["source"]))
    c["episodes"] = sorted(set(c["episodes"]) | {r["episode"]}); c["episode_count"] = len(c["episodes"])
    if sev.get(r["severity"], 0) > sev.get(c["severity"], 0):
        c["severity"] = r["severity"]
    c["measurable"] = bool(c.get("measurable")) or r["measurable"] or bool(r["proposed_gate"])
    c["proposed_gate"] = c.get("proposed_gate") or r["proposed_gate"]
    c["gates"] = list(dict.fromkeys(c["gates"] + match_known(r["rule"], KNOWN_GATES)))
    c["components"] = list(dict.fromkeys(c["components"] + match_known(r["rule"], KNOWN_COMPONENTS)))
    c["enforcement"] = ("gate" if c["gates"] else "component" if c["components"]
                        else "candidate_gate" if c["measurable"] else "prose")
    c["active"] = c["episode_count"] >= 2 or c["severity"] == "blocker"
    c["gate_miss"] = c.get("gate_miss", []) + gate_misses(c["gates"], [r])


def merge(paths: list[str]) -> int:
    """r10 (L-36 follow-up): add the general_rules of NEW critic JSONs to the committed docs/style_rules.json instead of
    rebuilding from qa/** (gitignored, so a rebuild on another machine only sees its own episodes). Each rule joins the
    closest existing cluster (same similarity as cluster_local) or opens a new one; nothing is ever dropped, and a source
    already merged is skipped, so re-running is a no-op. Then re-renders STYLE_RULES.md, the builder prompt and the backlog."""
    data = json.loads(OUT_JSON.read_text())
    clusters, done = data.get("clusters", []), set(data.get("merged_sources", []))
    for c in clusters:
        c.setdefault("gate_miss", [])
    nxt = max([int(c["id"].split("-")[1]) for c in clusters if c.get("id", "").startswith("R-")] or [0]) + 1
    added = joined = 0
    for p in paths:
        key, rows = _rows_from(Path(p))
        if key in done:
            print(f"lessons.py --merge: {key} already merged, skipped"); continue
        for r in rows:
            toks = tokenize(r["rule"]); best, best_s = None, -1.0
            for c in clusters:
                s = close_to_cluster(r["rule"], toks, {"tokens": tokenize(c["rule"]), "family": family_keys(c["rule"])}, 0.25)
                if s > best_s:
                    best, best_s = c, s
            if best is not None and best_s >= 0:
                _merge_into(best, r); joined += 1
            else:
                rec = classify(r["rule"], [r]); rec.update(id=f"R-{nxt:03d}", rule=r["rule"]); nxt += 1
                clusters.append(rec); added += 1
        done.add(key)
    data.update(clusters=clusters, merged_sources=sorted(done), generated=datetime.now().astimezone().isoformat(timespec="seconds"))
    OUT_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    OUT_MD.write_text(render_md(clusters, data["generated"]))
    OUT_PROMPT.write_text(render_prompt(clusters))
    write_backlog(clusters)
    act = [c for c in clusters if c["active"]]
    print(f"lessons.py --merge: {joined} rules joined existing clusters, {added} new clusters; {len(clusters)} clusters, {len(act)} active; "
          f"interim {sum(1 for c in act if c['enforcement'] == 'candidate_gate' or c.get('gate_miss'))}")
    return 0


def main():
    if "--refresh" in sys.argv:
        return refresh()
    if "--merge" in sys.argv:
        return merge([a for a in sys.argv[sys.argv.index("--merge") + 1:] if not a.startswith("--")])
    rows = collect()
    if not rows:
        print("lessons.py: no general_rules found under qa/", file=sys.stderr)
        guard_active([])
        # still write empty files so the prompt path exists
        empty = {"generated": datetime.now().astimezone().isoformat(timespec="seconds"), "clusters": []}
        OUT_JSON.parent.mkdir(exist_ok=True)
        OUT_JSON.write_text(json.dumps(empty, indent=2))
        OUT_MD.write_text(render_md([], empty["generated"]))
        OUT_PROMPT.write_text(render_prompt([]))
        return 0
    raw = cluster_agy(rows)
    clusters = []
    for i, c in enumerate(raw, 1):
        canonical = c.get("canonical") or min((m["rule"] for m in c["members"]), key=len)
        rec = classify(canonical, c["members"])
        rec["id"] = f"R-{i:03d}"
        rec["rule"] = canonical
        if c.get("category"):
            rec["category"] = rec["category"] or c["category"]
        clusters.append(rec)
    guard_active(clusters)
    generated = datetime.now().astimezone().isoformat(timespec="seconds")
    OUT_JSON.write_text(json.dumps({"generated": generated, "source_rules": len(rows), "clusters": clusters}, indent=2, ensure_ascii=False))
    OUT_MD.write_text(render_md(clusters, generated))
    OUT_PROMPT.write_text(render_prompt(clusters))
    write_backlog(clusters)
    active = [c for c in clusters if c["active"]]
    print(f"lessons.py: {len(rows)} rules → {len(clusters)} clusters, {sum(c['active'] for c in clusters)} active")
    print(f"  prose={sum(c['enforcement']=='prose' and c['active'] for c in clusters)} "
          f"gate={sum(c['enforcement']=='gate' and c['active'] for c in clusters)} "
          f"component={sum(c['enforcement']=='component' and c['active'] for c in clusters)} "
          f"candidate_gate={sum(c['enforcement']=='candidate_gate' for c in clusters)}")
    print(f"  wrote {OUT_MD.relative_to(ROOT)}, {OUT_JSON.relative_to(ROOT)}, {OUT_PROMPT.relative_to(ROOT)}")
    if "--prompt" in sys.argv:
        print()
        print(OUT_PROMPT.read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
