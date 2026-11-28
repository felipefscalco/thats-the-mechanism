"""r10 caption/anchor tests (L-40): numbers whisper writes as decimals or unit symbols align with the spoken script, and
every at("phrase") anchor in an episode must exist in its captions (captions show spoken numbers as digits).
Run: .venv-tts/bin/python tests/test_r10_captions.py"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import captions, static_gates


def _sf(*tokens):
    return [w["text"] for w in captions.spoken_form([dict(text=t, start=i, end=i + 1) for i, t in enumerate(tokens)])]


def t_decimal_and_units():
    assert _sf("2.45", "GHz.") == ["two", "point", "four", "five", "gigahertz"], _sf("2.45", "GHz.")
    assert _sf("0.5%") == ["zero", "point", "five", "percent"]
    assert _sf("5", "mW") == ["five", "milliwatts"] and _sf("5", "MW") == ["five", "megawatts"]   # case matters
    assert _sf("60", "mph") == ["sixty", "miles", "per", "hour"]
    assert _sf("40-50%") == ["forty", "to", "fifty", "percent"] and _sf("door,") == ["door,"]   # existing forms unchanged


def t_decimal_tokens_keep_written_form():
    out = captions.spoken_form([dict(text="2.45", start=0.0, end=1.0)])
    assert all(w.get("written") == "2.45" for w in out) and len({w["src"] for w in out}) == 1   # merged back as "2.45" on screen
    assert abs(out[0]["start"] - 0.0) < 1e-9 and abs(out[-1]["end"] - 1.0) < 1e-9


def t_anchor_gate():
    src = (ROOT / "remotion/src/episodes/Microwave.tsx").read_text()
    assert static_gates.anchors_resolve(src, "06-microwave-door")[0][1] is True
    bad = static_gates.anchors_resolve(src + '\nconst x = at("five milliwatts");', "06-microwave-door")[0]
    assert bad[1] is False and bad[2]["missing"] == ["five milliwatts"], bad


def t_label_sync_repeated_phrase_uses_this_shot():
    """e07 v2: "68 °C @sixty-eight" in shot 5 was judged against the shot-4 "sixty-eight" (10.5 s 'late')."""
    import label_sync as L
    ws = [dict(text=w, start=float(i), end=i + 0.5) for i, w in enumerate("at sixty-eight degrees red bulb built for sixty-eight".split())]
    assert L.echo("68 °C @sixty-eight", ws, 0, 4)[0] == 1.0
    assert L.echo("68 °C @sixty-eight", ws, 4, 9)[0] == 7.0


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("t_"):
            fn(); print("PASS", name)
