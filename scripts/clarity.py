#!/usr/bin/env python3
"""r8 sound-off clarity gate (Sky_v7 critic: "the picture alone fails the sound-off test"). Every causal step of the
mechanism must put a KEYWORD of that step on screen while it is spoken, so a muted viewer can follow the chain.
  causal step  = each sentence of the body (after the hook paragraph, before "That's the mechanism"), >= 5 words
  keyword      = a content word of the sentence (crude stem; number words == digits, "times" == "×") that appears in
                 the on-screen text of the shot playing when the sentence starts (shots.md), AND that text is really
                 drawn by the episode (string present in the episode .tsx)
Usage: clarity.py <CompositionId> <slug> [--json]   (static: shots.md + captions.json + episode .tsx, no render)"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shotlib import ROOT, words, phrase_time, shots
from script_text import spoken

NUM = {w: str(i) for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve".split())}
NUM.update(dict(twenty="20", thirty="30", forty="40", fifty="50", hundred="100", thousand="1000", million="1000000", times="×", percent="%"))
STOP = set("""the a an of to and is are was were be been it its it's in on at for by with that this these those you your
you're as from or so but then than when what which who how all any each every more most less very just only also there here
into onto off out up down over under about again same both one two can could would will isn't doesn't don't""".split())
def stem(w):
    w = w.lower().strip(".,!?;:\"'()“”’")
    if w in NUM: return NUM[w]
    for suf in ("able", "ing", "ers", "er", "ed", "es", "s", "ly"):
        if len(w) > len(suf) + 3 and w.endswith(suf): return w[: -len(suf)]
    return w
def keys(text): return {stem(w) for w in re.findall(r"[A-Za-z]+(?:['’][a-z]+)?|\d+|[×%]", text) if (w.lower() not in STOP and len(w) > 2) or w.isdigit() or w in ("×", "%")}

def check(comp, slug):
    ep = ROOT / "episodes" / slug; tsx = (ROOT / "remotion/src/episodes" / f"{comp}.tsx").read_text()
    paras = [p for p in spoken((ep / "script.txt").read_text()).split("\n\n") if p.strip()]
    body = " ".join(paras[1:]); body = body.split("That's the mechanism")[0]
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if len(s.split()) >= 5]
    ws = words(slug); rows = [r for r in shots(slug)]
    t_rows = [(phrase_time(ws, r["at"]) if r["at"] else 0.0, r) for r in rows]
    tsx_keys = keys(tsx); out = []   # identifiers too, but a keyword must ALSO be in the shot's planned on-screen text
    for s in sents:
        first = " ".join(s.split()[:3])
        try: t = phrase_time(ws, first)
        except KeyError: t = None
        row = max([x for x in t_rows if t is None or x[0] <= t + 0.05], key=lambda x: x[0], default=(0, rows[0]))[1]
        drawn = row["text"]
        hit = keys(s) & keys(" ".join(drawn)) & tsx_keys   # the keyword is planned for this shot AND drawn by the episode
        out.append(dict(sentence=s[:90], t_s=round(t, 2) if t is not None else None, shot=row["n"], on_screen=drawn, keyword=sorted(hit)[:4], ok=bool(hit)))
    bad = [o for o in out if not o["ok"]]
    return dict(ok=not bad, steps=len(out), missing=bad, covered=len(out) - len(bad))

if __name__ == "__main__":
    r = check(sys.argv[1], sys.argv[2])
    if "--json" in sys.argv: print(json.dumps(r, indent=1))
    else:
        print("clarity", sys.argv[1], "PASS" if r["ok"] else "FAIL", f"{r['covered']}/{r['steps']} causal steps with an on-screen keyword")
        for m in r["missing"]: print("  missing:", m["t_s"], m["sentence"], "| shot", m["shot"], m["on_screen"])
    sys.exit(0 if r["ok"] else 1)
