"""r8: one parser for script.txt so TTS, captions, facts and hooks agree on what is spoken.
Pause tags: `[pause: 0.4s]` / `[pause: 0.4]` (0.05-3.0 s) insert exact PCM silence in TTS (scripts/tts.py); they are never
spoken and never captioned. Paragraph breaks keep their r5 gaps (0.35 s, 0.5 s after the last)."""
import re
PAUSE_RE = re.compile(r"\[\s*pause\s*:\s*(\d+(?:\.\d+)?)\s*s?\s*\]", re.I)
HEAD_S, PARA_S, TAIL_S = 0.15, 0.35, 0.5

def spoken(text: str) -> str:
    """Script text with pause tags removed (what the voice says and the captions show)."""
    return re.sub(r"[ \t]{2,}", " ", PAUSE_RE.sub(" ", text)).replace(" \n", "\n").strip()

def words(text: str):
    return spoken(text).split()

def chunks(text: str):
    """[(chunk_text, silence_after_s)] in order: split on paragraphs, then on pause tags inside a paragraph."""
    paras = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    out = []
    for i, p in enumerate(paras):
        parts = PAUSE_RE.split(p)  # text, secs, text, secs, ...
        for k in range(0, len(parts), 2):
            t = re.sub(r"\s+", " ", parts[k]).strip()
            gap = float(parts[k + 1]) if k + 1 < len(parts) else (PARA_S if i < len(paras) - 1 else TAIL_S)
            if not (0.05 <= gap <= 3.0) and k + 1 < len(parts): raise ValueError(f"pause {gap}s outside 0.05-3.0 s")
            if t: out.append((t, gap))
            elif out: out[-1] = (out[-1][0], out[-1][1] + gap)  # tag at paragraph start: extend previous silence
    return out
