#!/usr/bin/env python3
"""Original Lottie animations (authored here as JSON, brand palette; MIT with the repo). Bodymovin 5.x schema, shape layers only.
Why authored instead of downloaded: LottieFiles free animations use the 'Lottie Simple License (FL 9.13.21)', which is
neither CC0 nor MIT and requires derivatives to carry the same licence -> rejected by our licence rule (see README)."""
import json
from pathlib import Path
R = Path(__file__).resolve().parent; P = json.loads((R / "palette.json").read_text())
PUB = R.parents[1] / "remotion" / "public" / "library"
rgb = lambda h: [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)] + [1]
st = lambda v: {"a": 0, "k": v}
def kf(frames):  # [(t, value)], eased
    ks = []
    for (t, v), (t2, v2) in zip(frames, frames[1:]):
        ks.append({"t": t, "s": v if isinstance(v, list) else [v], "e": v2 if isinstance(v2, list) else [v2], "i": {"x": [0.3], "y": [1]}, "o": {"x": [0.6], "y": [0]}})
    ks.append({"t": frames[-1][0], "s": frames[-1][1] if isinstance(frames[-1][1], list) else [frames[-1][1]]})
    return {"a": 1, "k": ks}
def tr(p=(0, 0), s=100, r=0, o=100):
    return {"ty": "tr", "p": st(list(p)), "a": st([0, 0]), "s": s if isinstance(s, dict) else st([s, s]), "r": r if isinstance(r, dict) else st(r), "o": o if isinstance(o, dict) else st(o), "sk": st(0), "sa": st(0)}
def layer(name, shapes, op, ks=None):
    ks = ks or {}
    return {"ddd": 0, "ind": 1, "ty": 4, "nm": name, "sr": 1, "ip": 0, "op": op, "st": 0, "bm": 0,
            "ks": {"o": ks.get("o", st(100)), "r": ks.get("r", st(0)), "p": ks.get("p", st([256, 256, 0])), "a": st([0, 0, 0]), "s": ks.get("s", st([100, 100, 100]))},
            "shapes": shapes}
def anim(name, layers, op=60):
    for i, l in enumerate(layers): l["ind"] = i + 1
    return {"v": "5.7.4", "fr": 30, "ip": 0, "op": op, "w": 512, "h": 512, "nm": name, "ddd": 0, "assets": [], "layers": layers}
fill = lambda h, o=100: {"ty": "fl", "c": st(rgb(h)), "o": st(o), "r": 1}
stroke = lambda h, w, o=100: {"ty": "st", "c": st(rgb(h)), "o": st(o), "w": st(w), "lc": 2, "lj": 2}
L = {}
# 1 gear spin (one turn per loop, seamless)
gear = {"ty": "sr", "sy": 1, "d": 1, "pt": st(12), "p": st([0, 0]), "r": st(0), "ir": st(120), "is": st(0), "or": st(160), "os": st(0)}
L["gear_spin"] = anim("gear_spin", [
    layer("hub", [{"ty": "gr", "it": [{"ty": "el", "d": 1, "p": st([0, 0]), "s": st([90, 90])}, fill(P["ink2"]), tr()]}], 60),
    layer("gear", [{"ty": "gr", "it": [gear, fill(P["amber"]), tr()]}], 60, {"r": kf([(0, 0), (60, 360)])})])
# 2 pulse ring (attention ping)
ring = lambda delay: layer(f"ring{delay}", [{"ty": "gr", "it": [{"ty": "el", "d": 1, "p": st([0, 0]), "s": st([200, 200])}, stroke(P["tech"], 14), tr()]}], 60,
                           {"s": kf([(delay, [40, 40, 100]), (delay + 40, [220, 220, 100])]), "o": kf([(delay, 100), (delay + 40, 0)])})
L["pulse_ring"] = anim("pulse_ring", [ring(0), ring(20), layer("dot", [{"ty": "gr", "it": [{"ty": "el", "d": 1, "p": st([0, 0]), "s": st([70, 70])}, fill(P["tech"]), tr()]}], 60)])
# 3 scan line sweeping a frame
L["scan_line"] = anim("scan_line", [
    layer("line", [{"ty": "gr", "it": [{"ty": "rc", "d": 1, "p": st([0, 0]), "s": st([340, 14]), "r": st(7)}, fill(P["amber"]), tr()]}], 60, {"p": kf([(0, [256, 110, 0]), (30, [256, 402, 0]), (60, [256, 110, 0])])}),
    layer("frame", [{"ty": "gr", "it": [{"ty": "rc", "d": 1, "p": st([0, 0]), "s": st([380, 380]), "r": st(40)}, stroke(P["paper"], 12), tr()]}], 60)])
# 4 check pop (scale overshoot + stroke draw-on)
check = {"ty": "sh", "d": 1, "ks": st({"i": [[0, 0]] * 3, "o": [[0, 0]] * 3, "v": [[-80, 0], [-20, 60], [90, -60]], "c": False})}
L["check_pop"] = anim("check_pop", [
    layer("check", [{"ty": "gr", "it": [check, stroke(P["ink"], 30), {"ty": "tm", "s": st(0), "e": kf([(8, 0), (22, 100)]), "o": st(0), "m": 1}, tr()]}], 45),
    layer("disc", [{"ty": "gr", "it": [{"ty": "el", "d": 1, "p": st([0, 0]), "s": st([300, 300])}, fill(P["green"]), tr()]}], 45, {"s": kf([(0, [0, 0, 100]), (10, [115, 115, 100]), (16, [100, 100, 100])])})], 45)
for k, v in L.items():
    (R / "lottie").mkdir(exist_ok=True); (R / "lottie" / f"{k}.json").write_text(json.dumps(v)); (PUB / f"{k}.json").write_text(json.dumps(v))
print(len(L), "lottie")
