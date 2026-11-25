---
name: voice
description: Synthesize the episode voiceover with local Kokoro TTS, loudness-normalize it, and prepare the 16 kHz captions wav. Use when generating or regenerating narration, changing TTS voice or speed, or debugging audio levels.
---

# voice

Narration is generated locally. Default (pilot): **Kokoro ONNX**, voice `am_michael`, speed `1.08`, language `en-us`.

## Command

Usually you do not run TTS alone — `scripts/build-episode.sh <slug> <CompId>` does it. To run just this stage:

```bash
.venv-tts/bin/python scripts/tts.py am_michael 1.08 episodes/<slug>/script.txt
# writes episodes/<slug>/narration_raw.wav
ffmpeg -loglevel error -y -i episodes/<slug>/narration_raw.wav \
  -af loudnorm=I=-14:TP=-1.5:LRA=7 -ar 48000 -ac 1 episodes/<slug>/narration.wav
ffmpeg -loglevel error -y -i episodes/<slug>/narration.wav \
  -ar 16000 -ac 1 episodes/<slug>/narration16k.wav
```

`scripts/tts.py` splits on blank lines (paragraphs), inserts a short pause between them, and a slightly longer tail at the end. Re-runs with the same model and text are deterministic (bit-identical).

Models must already be present at `models/kokoro-v1.0.onnx` and `models/voices-v1.0.bin` (`scripts/setup.sh`, not `--fast`).

## Targets

- Integrated loudness of `narration.wav`: **−14 LUFS** (true peak ≤ −1.5 dBTP in the loudnorm filter). The finished mix is checked at about −15 to −13 LUFS.
- Duration should land in **35–55 s**. If it does not, edit the script — do not just change speed past 1.15 or below 1.0 without a human decision.
- Do not commit `*.wav` files (gitignored). They are rebuilt.

## Notes

- A personal voice clone is a planned swap, not the default in this tree. Do not add a paid API (ElevenLabs, etc.) unless a human asks and the license is recorded.
- If you trial another local model (for example Qwen3-TTS), keep it behind a flag and document the license before making it the default.
