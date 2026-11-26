#!/usr/bin/env python3
"""Fact ledger gate (r5, adopted from shorts-kit's facts.json/sources.json idea, re-implemented).

episodes/<slug>/facts.json:
  {"facts": [{"id": "f-0001", "claim": str, "value": str, "status": "verified|contested|unverified",
              "sources": ["s-0001", ...], "caveat": str, "checkedAt": "YYYY-MM-DD", "spoken": [exact substrings of script.txt]}],
   "sources": [{"id": "s-0001", "title": str, "url": str, "publisher": str, "accessed": "YYYY-MM-DD"}]}

check <slug>: FAILS (exit 1) when
  - a fact is spoken (its `spoken` text is in script.txt) but status != verified, or has < 2 sources (single-source facts need a caveat)
  - a sentence of script.txt contains a number / quantity word that no verified fact's `spoken` span covers
  - schema problems (missing ids, dangling source ids)
init <slug>: one-off migration from the older episodes/<slug>/sources.json claims list (statuses start as "unverified").
The TTS step refuses to run while `check` fails (pipeline.config.json gates.facts), so a script can't be voiced on unverified claims."""
import sys as _s, os as _o
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import json, re, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NUM = re.compile(r"\b(\d[\d,.]*|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|thirty|forty|fifty|sixty|"
                 r"seventy|eighty|ninety|hundred|thousand|million|billion|dozens?|half|percent|twice|double|triple)\b", re.I)
FILLER_OK = {"one of", "the three big corner squares"}  # counted things that are definitions, not claims (still listed here, reviewed)


def load(slug):
    return json.loads((ROOT / "episodes" / slug / "facts.json").read_text())


def check(slug) -> list[str]:
    d = load(slug); script = __import__("script_text").spoken((ROOT / "episodes" / slug / "script.txt").read_text())  # r8: pause tags are not spoken
    flat = " ".join(script.split())
    errs = []
    sids = {s["id"] for s in d.get("sources", [])}
    for s in d.get("sources", []):
        if not re.fullmatch(r"s-\d{4}", s["id"]) or not s.get("url"): errs.append(f"source {s.get('id')}: bad id or missing url")
    covered = []
    for f in d["facts"]:
        if not re.fullmatch(r"f-\d{4}", f["id"]): errs.append(f"{f['id']}: bad id")
        for sid in f["sources"]:
            if sid not in sids: errs.append(f"{f['id']}: dangling source {sid}")
        spoken = [sp for sp in f.get("spoken", []) if " ".join(sp.split()) in flat]
        missing = [sp for sp in f.get("spoken", []) if " ".join(sp.split()) not in flat]
        for sp in missing: errs.append(f"{f['id']}: spoken span not in script (stale?): {sp!r}")
        if spoken and f["status"] != "verified": errs.append(f"{f['id']}: spoken but status={f['status']}: {f['claim']}")
        if spoken and len(f["sources"]) < 2 and not f.get("caveat"): errs.append(f"{f['id']}: spoken with 1 source and no caveat")
        if f["status"] == "verified": covered += [" ".join(sp.split()).lower() for sp in spoken]
    for sent in re.split(r"(?<=[.!?])\s+", flat):
        for m in NUM.finditer(sent):
            ctx = sent.lower()
            if any(fl in ctx for fl in FILLER_OK) and not any(c in ctx for c in covered):
                continue
            if not any(m.group(0).lower() in c and c in ctx for c in covered):
                errs.append(f"unbacked quantity {m.group(0)!r} in: {sent!r}")
    return errs


def init(slug):
    src = json.loads((ROOT / "episodes" / slug / "sources.json").read_text())
    sources, facts = [], []
    for i, c in enumerate(src["claims"], 1):
        ids = []
        for u in c["sources"]:
            url = u.split(" ")[0]; note = u[len(url):].strip(" ()")
            hit = next((s for s in sources if s["url"] == url), None)
            if not hit:
                hit = dict(id=f"s-{len(sources) + 1:04d}", title=note or url, url=url, publisher=re.sub(r"^https?://(www\.)?", "", url).split("/")[0], accessed="2026-11-24")
                sources.append(hit)
            ids.append(hit["id"])
        facts.append(dict(id=f"f-{i:04d}", claim=c["claim"], value="", status="unverified", sources=ids, caveat="", checkedAt="", spoken=[]))
    out = ROOT / "episodes" / slug / "facts.json"
    out.write_text(json.dumps(dict(facts=facts, sources=sources), indent=1, ensure_ascii=False)); print("wrote", out)


if __name__ == "__main__":
    cmd, slug = sys.argv[1], sys.argv[2]
    if cmd == "init": init(slug)
    elif cmd == "check":
        e = check(slug)
        for x in e: print("FAIL |", x)
        print(f"facts {slug}: {'PASS' if not e else 'FAIL'} ({len(load(slug)['facts'])} facts)")
        sys.exit(1 if e else 0)
