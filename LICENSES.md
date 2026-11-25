# Licenses and attribution

## This repository (code and original docs)

[MIT](LICENSE) © 2026 Felipe Scalco.

Original synthesised sound effects in `sfx/synth/` (whoosh, riser, sting, tick), produced by `scripts/synth_sfx.py`, are released as **CC0 1.0**.

## Bundled assets

| Asset | Path | License | Source |
|---|---|---|---|
| Kenney Interface / Impact / Sci-fi Sounds | `sfx/kenney/` (and the prepared copies in `remotion/public/sfx/`) | **CC0 1.0** | [kenney.nl](https://kenney.nl/assets/) — `License.txt` is in each pack folder. Mapping: `sfx/CREDITS.csv`. |
| Pilot contact sheets | `contact_sheet.png`, `contact_sheet_v2.png` | MIT (original frames from this project) | Generated locally with Remotion + ffmpeg |
| Episode scripts, shot tables, captions JSON, QA reports | `episodes/`, `qa/`, `metadata.md` | MIT | This project |

## Runtime dependencies (not vendored)

These are downloaded by `scripts/setup.sh` or `npm install`. They are **not** re-licensed by the MIT grant above.

| Dependency | Use | License notes |
|---|---|---|
| [Remotion](https://www.remotion.dev/) (`remotion`, `@remotion/cli`, …) | React → MP4 renderer | Remotion company license: **free for individuals and companies of up to 3 people**. Larger companies need a [Remotion license](https://www.remotion.dev/docs/licensing). See also `remotion/.agents/skills/remotion-license`. |
| [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) + Kokoro v1.0 model | TTS | kokoro-onnx is MIT. The ONNX model and voice bank come from the [model-files-v1.0 release](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0) — check that release for the model terms before commercial use. |
| [whisper.cpp](https://github.com/ggml-org/whisper.cpp) + `ggml-small.en` | Word-level captions | whisper.cpp is MIT. The GGML model is derived from OpenAI Whisper (MIT). |
| [FFmpeg](https://ffmpeg.org/) | Mix, loudness, QA | LGPL/GPL, used as an external binary — this repo does not distribute FFmpeg. |
| `qrcode` (npm) | Real QR matrices in episodes | MIT |
| [HyperFrames](https://github.com/heygen-com/hyperframes) | Optional QA helper only | Apache-2.0 — not required, not bundled |

YouTube, Instagram and TikTok are not dependencies of this repo. **Do not publish** from the pipeline; a human uploads after approval.
