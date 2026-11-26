"""Word-level captions. Primary: whisper.cpp (local build, small.en + DTW). Fallback: faster-whisper.
Usage: .venv-tts/bin/python scripts/captions.py episodes/<slug> [...]   (needs narration16k.wav + script.txt)"""
import sys, json, re, difflib, os, subprocess, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WCLI = f"{ROOT}/tools/whisper.cpp/build/bin/whisper-cli"
WMODEL = f"{ROOT}/tools/whisper.cpp/models/ggml-small.en.bin"

DTW_OFFSET = 0.12  # calibrated: DTW token times land ~0.12 s after the silence-detected onset

def whisper_cpp(wav):
    """whisper.cpp with DTW token timestamps (needs -nfa: DTW is disabled under flash attention)."""
    out = tempfile.mktemp()
    subprocess.run([WCLI, "-m", WMODEL, "-f", wav, "-ojf", "-of", out, "-t", "6",
                    "--dtw", "small.en", "-nfa", "-np"], check=True, capture_output=True)
    toks = [t for s in json.load(open(out + ".json"))["transcription"] for t in s["tokens"] if not t["text"].startswith("[_")]
    words = []
    for t in toks:
        if t.get("t_dtw", -1) < 0: raise RuntimeError("no DTW timestamps")
        if t["text"].startswith(" ") or not words:
            words.append(dict(text=t["text"].strip(), start=max(0.0, t["t_dtw"] / 100 - DTW_OFFSET), end=t["offsets"]["to"] / 1000))
        else:
            words[-1]["text"] += t["text"]
    for i in range(1, len(words)):  # keep monotonic
        words[i]["start"] = max(words[i]["start"], words[i - 1]["start"] + 0.04)
    words[-1]["end"] = max(words[-1]["end"], words[-1]["start"] + 0.4)
    if not words: raise RuntimeError("whisper.cpp returned no words")
    return words, "whisper.cpp+DTW"

def faster_whisper(wav):
    import soundfile as sf
    from faster_whisper import WhisperModel
    m = WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(sf.read(wav, dtype="float32")[0], word_timestamps=True, beam_size=5, language="en")
    return [dict(text=w.word.strip(), start=w.start, end=w.end) for s in segs for w in s.words], "faster-whisper"

norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
for ep in sys.argv[1:]:
    wav = f"{ep}/narration16k.wav"
    try:
        words, engine = whisper_cpp(wav)
    except Exception as e:
        print("whisper.cpp failed, falling back:", e)
        words, engine = faster_whisper(wav)
    script = open(f"{ep}/script.txt").read().split()
    sm = difflib.SequenceMatcher(a=[norm(w["text"]) for w in words], b=[norm(t) for t in script], autojunk=False)
    for tag, i1, i2, j1, j2 in reversed(sm.get_opcodes()):  # reversed: span rebuilds change lengths
        if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
            for k in range(i2 - i1): words[i1 + k]["text"] = script[j1 + k]
        elif tag == "replace" and "".join(norm(w["text"]) for w in words[i1:i2]) and difflib.SequenceMatcher(
                a="".join(norm(w["text"]) for w in words[i1:i2]), b="".join(norm(t) for t in script[j1:j2])).ratio() >= 0.75:
            # r6 (QR "Reed-Solom and"): whisper split/truncated a word. Rebuild the span from the SCRIPT words,
            # timing spread by character length, so a caption can never show a fragment.
            t0, t1 = words[i1]["start"], words[i2 - 1]["end"]
            ln = [max(1, len(norm(s))) for s in script[j1:j2]]; tot = sum(ln); acc = 0; span = []
            for s, l in zip(script[j1:j2], ln):
                a = t0 + (t1 - t0) * acc / tot; acc += l
                span.append(dict(text=s, start=a, end=t0 + (t1 - t0) * acc / tot))
            words[i1:i2] = span
            print(ep, "rebuilt", script[j1:j2])
        elif tag != "equal":
            print(ep, tag, [w["text"] for w in words[i1:i2]], script[j1:j2])
    out = []
    for x in words:  # glue "-50", "%" etc. onto the previous word
        if out and (x["text"].startswith("-") or x["text"] == "%"):
            out[-1]["text"] += x["text"].replace("-", "–"); out[-1]["end"] = x["end"]
        else: out.append(x)
    ov = json.load(open(f"{ep}/display.json")) if os.path.exists(f"{ep}/display.json") else []
    for phrase, disp in ov:  # e.g. ["forty to 50%", "40–50%"]
        p = [norm(x) for x in phrase.split()]
        i = 0
        while i + len(p) <= len(out):
            if [norm(w["text"]) for w in out[i:i + len(p)]] == p:
                out[i:i + len(p)] = [dict(text=disp, start=out[i]["start"], end=out[i + len(p) - 1]["end"])]
            i += 1
    for i in range(len(out) - 1):  # end = min(own end, next start) so highlight never overlaps
        out[i]["end"] = min(max(out[i]["end"], out[i]["start"] + 0.08), out[i + 1]["start"])  # DTW start can land after the segment end
    json.dump(out, open(f"{ep}/captions.json", "w"), indent=1)
    print(ep, engine, len(out), "words; script", len(script), "last end", out[-1]["end"])
