"""Word-level captions. Primary: whisper.cpp (local build, small.en + DTW). Fallback: faster-whisper.
Usage: .venv-tts/bin/python scripts/captions.py episodes/<slug> [...]   (needs narration16k.wav + script.txt)"""
import sys, json, re, difflib, os, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WCLI = f"{ROOT}/tools/whisper.cpp/build/bin/whisper-cli"
WMODEL = f"{ROOT}/tools/whisper.cpp/models/ggml-small.en.bin"

DTW_OFFSET = 0.12  # calibrated: DTW token times land ~0.12 s after the silence-detected onset

def whisper_cpp(wav, prompt=""):
    """whisper.cpp with DTW token timestamps (needs -nfa: DTW is disabled under flash attention)."""
    out = tempfile.mktemp()
    subprocess.run([WCLI, "-m", WMODEL, "-f", wav, "-ojf", "-of", out, "-t", "6",
                    "--dtw", "small.en", "-nfa", "-np"] + (["--prompt", prompt] if prompt else []), check=True, capture_output=True)
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

def faster_whisper(wav, prompt=""):
    import soundfile as sf
    from faster_whisper import WhisperModel
    m = WhisperModel("small.en", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(sf.read(wav, dtype="float32")[0], word_timestamps=True, beam_size=5, language="en", initial_prompt=prompt or None)
    return [dict(text=w.word.strip(), start=w.start, end=w.end) for s in segs for w in s.words], "faster-whisper"

norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())

def lev(a, b):
    if a == b: return 0
    if not a or not b: return max(len(a), len(b))
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1): cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]
sim = lambda a, b: 1.0 - lev(a, b) / max(1, len(a), len(b))

_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
def num_words(n):
    if n < 20: return [_ONES[n]]
    if n < 100: return [_TENS[n // 10]] + ([_ONES[n % 10]] if n % 10 else [])
    if n < 1000: return [_ONES[n // 100], "hundred"] + (num_words(n % 100) if n % 100 else [])
    if n < 1_000_000: return num_words(n // 1000) + ["thousand"] + (num_words(n % 1000) if n % 1000 else [])
    return [str(n)]
def spoken_form(words):
    """Expand whisper's written numbers to the spoken form the script uses ("40" -> forty, "50%" -> fifty percent,
    "1,000" -> one thousand), splitting the word's time by character length, before alignment."""
    out = []
    for w in words:
        r = re.fullmatch(r"[^\w]*(\d+)\s*[-–]\s*(\d+)(%?)[^\w]*", w["text"])   # "40-50%" -> forty to fifty percent
        m = re.fullmatch(r"([^\w]*)(\d{1,3}(?:,\d{3})*|\d+)(%?)([^\w]*)", w["text"])
        if r: toks = num_words(int(r.group(1))) + ["to"] + num_words(int(r.group(2))) + (["percent"] if r.group(3) else [])
        elif m: toks = num_words(int(m.group(2).replace(",", ""))) + (["percent"] if m.group(3) else [])
        else: out.append(w); continue
        ln = [len(t) for t in toks]; tot = sum(ln); acc = 0; t0, t1 = w["start"], w["end"]
        for t, l in zip(toks, ln):
            out.append(dict(text=t, start=t0 + (t1 - t0) * acc / tot, end=t0 + (t1 - t0) * (acc + l) / tot, src=id(w), written=w["text"])); acc += l
    return out

def align(hyp, ref):
    """r8 script alignment (MoneyPrinterTurbo subtitle.correct idea, word level): Levenshtein DP over words where a
    substitution costs the normalised CHARACTER edit distance, gaps cost 1, and 1:2 / 2:1 merges let whisper split or
    glue words ("Reed-Solom and" -> "Reed-Solomon"). Returns per-script-word (hyp_i0, hyp_i1, similarity) or None."""
    H, R = [norm(w) for w in hyp], [norm(w) for w in ref]
    n, m = len(H), len(R); INF = 1e9
    D = [[INF] * (m + 1) for _ in range(n + 1)]; B = [[None] * (m + 1) for _ in range(n + 1)]; D[0][0] = 0
    for i in range(n + 1):
        for j in range(m + 1):
            d = D[i][j]
            if d >= INF: continue
            moves = [(i + 1, j, 1.0, "h"), (i, j + 1, 1.0, "r")]
            if i < n and j < m: moves.append((i + 1, j + 1, 1 - sim(H[i], R[j]), "s"))
            if i + 1 < n and j < m: moves.append((i + 2, j + 1, 1 - sim(H[i] + H[i + 1], R[j]) + 0.15, "s21"))
            if i < n and j + 1 < m: moves.append((i + 1, j + 2, 1 - sim(H[i], R[j] + R[j + 1]) + 0.15, "s12"))
            for a, b, c, k in moves:
                if a <= n and b <= m and d + c < D[a][b]: D[a][b] = d + c; B[a][b] = (i, j, k)
    out = [None] * m; i, j = n, m
    while (i, j) != (0, 0):
        pi, pj, k = B[i][j]
        if k == "s": out[pj] = (pi, pi + 1, sim(H[pi], R[pj]))
        elif k == "s21": out[pj] = (pi, pi + 2, sim(H[pi] + H[pi + 1], R[pj]))
        elif k == "s12":
            sc = sim(H[pi], R[pj] + R[pj + 1]); out[pj] = (pi, pi + 1, sc); out[pj + 1] = (pi, pi + 1, sc)
        i, j = pi, pj
    return out

def initial_prompt(script_words, ep):
    """whisper initial prompt: technical terms from the script (+ optional episodes/<slug>/terms.txt) so rare words,
    acronyms and units are spelled the way the script spells them."""
    terms, seen = [], set()
    extra = open(f"{ep}/terms.txt").read().split() if os.path.exists(f"{ep}/terms.txt") else []
    for k, w in enumerate(script_words):
        c = w.strip(".,!?;:\"'()")
        tech = any(ch.isdigit() for ch in c) or "-" in c or (c[:1].isupper() and k and script_words[k - 1][-1:] not in ".!?") or len(c) >= 9 or c.isupper() and len(c) > 1
        if tech and c.lower() not in seen: seen.add(c.lower()); terms.append(c)
    for c in extra:
        if c.lower() not in seen: seen.add(c.lower()); terms.append(c)
    return ("Glossary: " + ", ".join(terms))[:220] if terms else ""

MIN_MATCH, MIN_SIM, MAX_RUN, WIN_SLACK = 0.90, 0.70, 3, 0.35
for ep in sys.argv[1:]:
    if ep.startswith("--"): continue
    wav = f"{ep}/narration16k.wav"
    from script_text import words as script_words_of
    script = script_words_of(open(f"{ep}/script.txt").read())
    prompt = initial_prompt(script, ep)
    try:
        words, engine = whisper_cpp(wav, prompt)
    except Exception as e:
        print("whisper.cpp failed, falling back:", e)
        words, engine = faster_whisper(wav, prompt)
    words = spoken_form(words)
    al = align([w["text"] for w in words], script)
    good = [a is not None and a[2] >= MIN_SIM for a in al]
    # captions are ALWAYS the script words; timing comes from the aligned whisper words
    out = []
    for j, wtxt in enumerate(script):
        a = al[j]
        if good[j]:
            out.append(dict(text=wtxt, start=words[a[0]]["start"], end=words[a[1] - 1]["end"]))
        else:
            out.append(dict(text=wtxt, start=None, end=None))
    # s12 merges: two script words share one whisper word -> split its time by character length
    j = 0
    while j < len(out) - 1:
        if good[j] and good[j + 1] and al[j][:2] == al[j + 1][:2]:
            t0, t1 = out[j]["start"], out[j]["end"]; l0, l1 = max(1, len(norm(script[j]))), max(1, len(norm(script[j + 1])))
            mid = t0 + (t1 - t0) * l0 / (l0 + l1); out[j]["end"] = mid; out[j + 1]["start"] = mid; j += 2
        else: j += 1
    # r8 pause tags: TTS chunk windows (exact sample offsets from narration_segments.json) bound every word, and
    # unmatched words are re-timed inside their own chunk (char-proportional), i.e. shifted by the sample count.
    segp = f"{ep}/narration_segments.json"
    seg = json.load(open(segp)) if os.path.exists(segp) else None
    word_seg = []
    if seg:
        k = 0
        for si, sgm in enumerate(seg["segments"]):
            for _ in sgm["text"].split(): word_seg.append(si)
        if len(word_seg) != len(script): seg = None; word_seg = []
    def fill(lo, hi, t0, t1):
        ln = [max(1, len(norm(out[q]["text"]))) for q in range(lo, hi)]; tot = sum(ln); acc = 0
        for q, l in zip(range(lo, hi), ln):
            out[q]["start"] = t0 + (t1 - t0) * acc / tot; acc += l; out[q]["end"] = t0 + (t1 - t0) * acc / tot
    j = 0; runs = []
    while j < len(out):
        if out[j]["start"] is not None: j += 1; continue
        k = j
        while k < len(out) and out[k]["start"] is None: k += 1
        runs.append((j, k))
        if seg and all(word_seg[q] == word_seg[j] for q in range(j, k)):
            sg = seg["segments"][word_seg[j]]
            t0 = max(sg["start_s"], out[j - 1]["end"] if j and word_seg[j - 1] == word_seg[j] else sg["start_s"])
            t1 = min(sg["end_s"], out[k]["start"] if k < len(out) and word_seg[k] == word_seg[j] else sg["end_s"])
        else:
            t0 = out[j - 1]["end"] if j else 0.15; t1 = out[k]["start"] if k < len(out) else t0 + 0.3 * (k - j)
        fill(j, k, t0, max(t1, t0 + 0.08 * (k - j)))
        j = k
    window_viol = []
    if seg:
        for q, w in enumerate(out):
            sg = seg["segments"][word_seg[q]]
            if w["start"] < sg["start_s"] - WIN_SLACK or w["start"] > sg["end_s"] + WIN_SLACK: window_viol.append([w["text"], round(w["start"], 2), [sg["start_s"], sg["end_s"]]])
    if seg:  # a word never extends into an inserted pause: clamp its end to its chunk end (+0.1 s release)
        for q, w in enumerate(out): w["end"] = min(w["end"], seg["segments"][word_seg[q]]["end_s"] + 0.1)
    for i in range(1, len(out)):  # keep monotonic
        out[i]["start"] = max(out[i]["start"], out[i - 1]["start"] + 0.04)
    match = sum(good) / max(1, len(good)); max_run = max([k - j for j, k in runs], default=0)
    rep = dict(engine=engine, initial_prompt=prompt, script_words=len(script), whisper_words=len(words), match_rate=round(match, 3),
               max_unmatched_run=max_run, unmatched=[script[q] for q in range(len(script)) if not good[q]][:30],
               pause_segments=len(seg["segments"]) if seg else 0, window_violations=window_viol[:10],
               thresholds=dict(min_match=MIN_MATCH, min_word_sim=MIN_SIM, max_run=MAX_RUN, window_slack_s=WIN_SLACK))
    rep["ok"] = match >= MIN_MATCH and max_run <= MAX_RUN and len(window_viol) <= max(1, 0.02 * len(out))
    json.dump(rep, open(f"{ep}/captions_align.json", "w"), indent=1)
    print(ep, "align", "PASS" if rep["ok"] else "FAIL", json.dumps({k: rep[k] for k in ("match_rate", "max_unmatched_run", "unmatched")}))
    if not rep["ok"] and "--force" not in sys.argv:
        sys.exit(f"{ep}: script alignment broke (see captions_align.json); captions.json not written. Fix the script/TTS or add terms.txt; --force to override.")
    # numbers: script words that all came from ONE written whisper token ("thirty percent" <- "30%") are shown in the
    # written form (digits read faster on a phone), keeping the script's trailing punctuation
    j = 0; merged = []
    while j < len(out):
        a = al[j] if good[j] else None; src = words[a[0]].get("src") if a else None
        k = j + 1
        while src is not None and k < len(out) and good[k] and words[al[k][0]].get("src") == src: k += 1
        if src is not None and k - j == sum(1 for w in words if w.get("src") == src):
            wr = re.sub(r"[^\w%–-]+$", "", words[a[0]]["written"]); tail = re.sub(r"^.*?([^\w%]*)$", r"\1", script[k - 1])
            merged.append(dict(text=wr.replace("-", "–") + tail, start=out[j]["start"], end=out[k - 1]["end"])); j = k
        else: merged.append(out[j]); j += 1
    out = merged
    words_ = out; out = []
    for x in words_:  # glue "-50", "%" etc. onto the previous word
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
