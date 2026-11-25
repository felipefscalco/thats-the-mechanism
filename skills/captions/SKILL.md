---
name: captions
description: Align word-level captions to the narration with whisper.cpp (DTW) and install them where Remotion reads them. Use when generating or fixing captions, caption timing, or word highlight issues.
---

# captions

Word timestamps drive both the on-screen captions and the shot `timing.makeAt(words)("phrase")` helpers. Wrong times break animation cues.

## Command

Requires `episodes/<slug>/narration16k.wav` and `script.txt`.

```bash
.venv-tts/bin/python scripts/captions.py episodes/<slug>
cp episodes/<slug>/captions.json remotion/src/<slug>.captions.json
```

`scripts/captions.py` uses the local whisper.cpp build first:

- binary: `tools/whisper.cpp/build/bin/whisper-cli`
- model: `tools/whisper.cpp/models/ggml-small.en.bin`
- flags: `--dtw small.en -nfa` (DTW is disabled under flash attention)
- a calibrated **−0.12 s** offset is applied to DTW times

If whisper.cpp is missing or returns no DTW times, the script falls back to `faster-whisper` (`requirements-optional.txt`).

## Rules

- After captions exist, re-run `python3 scripts/lint_shots.py <slug>` so every shot phrase resolves.
- Captions render at **84 px**, active word in amber, in the caption band (y 1222–1440) — do not draw them on the stage.
- Prefer fixing the aligner or the script over hand-editing dozens of timestamps. Small one-word fixes in `captions.json` are OK if you document why.
- Commit the JSON (small, useful). Do not commit wavs.
