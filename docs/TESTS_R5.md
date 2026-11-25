# Round 5 tests: tools, gates, feasibility

| # | test | result |
|---|---|---|
| T1 | `facts.py check` on 01-qr-code, 02-elevator, 03-sky | PASS (all spoken numbers covered by verified facts, ≥2 sources each; Elevator World page 403 → caveat recorded) |
| T2 | Negative: temp episode `_gate_test` saying "seven times" with no fact → `tts.py` | BLOCKED, exit 1 ("facts.py check failed"); temp folder removed |
| T3 | Negative: `gates.py require _t3_dummy script` with no approval (the call tts.py makes) | BLOCKED rc=2; with `GATE_MODE_SCRIPT=auto` → rc=0 and an override row logged (test row then removed) |
| T4 | `gates.py stats` | final 3/3 and script 3/3 approved without changes (streak 3/5 toward suggest-auto); style_frames 0/1 (approved with changes) |
| T5 | `storyboard.py` QR / Elevator / Sky | 36 / 29 / 32 stills, about 4 s each, gate auto (logged) |
| T6 | qa.py raw-font gate on r4 code | caught CAR/L-labels < 30 px, fixed → PASS |
| T7 | qa.py cadence gate on v4 renders | v4 gaps of 4.0–4.6 s → FAIL; v5 3.5–3.8 s → PASS |
| T8 | qa.py silence beat on v4 | about −37 dB (riser overlapped) → FAIL; v5 −88 / −116 / −180 dB → PASS |
| T9 | Safe-zone gate | 9 real violations found across it1–it3, all fixed |
| T10 | Critic position-bias (Elevator v3 vs v4, both orders) | 3-flash-preview: v4 +1.76 / swapped −0.85; lite: +0.95 / swapped −0.41 → consistent |
| T11 | Critic absolute ranking (calibrated) | FAIL: v3 6.46 > v4 6.06 (same model) → absolute score not used for ship decisions |
| T12 | Grain benchmark, 150 frames | off 8.3 s · static 8.7 s · animated 11.4 s → static default |
| T13 | UISFX cues in mix | SFX median 13–15 dB under voice, density 1.34–1.40 /s → PASS |

## Feasibility (notes only, nothing integrated)
- **Pocket TTS** (kyutai, pip `pocket-tts` 4.0.1): code MIT, weights CC-BY-4.0 on HF, gated by an "auto" click-through (needs an HF login/token). About 100 M params, runs on CPU (2 cores enough, real time on this 8-CPU box per the docs). Voice cloning from a short sample; the terms require consent of the voice owner. **Verdict:** best candidate for the postponed cloned voice; test when Felipe records a consent sample. Not installed (gated weights).
- **ZONOS3-Mini** (Zyphra): weights Apache-2.0, code MIT. Reference server is CUDA (about 9 GB of weights); MLX for Apple Silicon; a community ggml C++ server can run on CPU but slowly. The box has no GPU (8 CPU, 15 GB RAM). **Verdict:** not practical here; revisit only with a GPU.
- Kokoro am_michael stays as the voice for round 5 (owner decision).
