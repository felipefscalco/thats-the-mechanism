# Research notes

References already analysed for this channel, and what to adopt or skip. Dates are when the analysis was done. Stars and prices go stale; re-check a licence at the source before adopting anything new.

## Reference channels (2026-11-19)

Used to set tone and hook craft, not to copy a look or a cadence.

- **Zack D. Films** — huge Shorts-only curiosity channel. A ceiling, not a production model.
- **@speedy_devv** (Instagram) — motion-graphics explainers built with Claude Code + Remotion; object already moving on frame 0. Example retention: ~30.6 s on an 84 s Reel (Keyframes, Oct–Nov 2026).
- **Shyam** (Medium, 2026-11-03) — same Claude + Remotion kit: a Truecaller Reel at ~1 M views on Instagram + Facebook, then a reCAPTCHA Reel at 3,452 Instagram views. The author's lesson: **topic universality beat the edit**. That is why the angle gate exists.
- **Kurzgesagt, Veritasium, Vsauce** — rigour and clarity; their core is long-form.
- **Practical Engineering** — physical mechanisms, calm tone; not vertical length.
- **School of Life, Pursuit of Wonder, Einzelgänger** — accessible philosophy tone, usually long essays.
- Research scrape of Shorts metadata (zackdfilms, kurzgesagt, lowpolyshorts) lives in [`../research/yt_shorts_meta.txt`](../research/yt_shorts_meta.txt).

Jenny Hoyos (YouTube Blog, 2025-01-28): you have about one second to hook someone on Shorts. YouTube's official studio metric is “How many chose to view,” compared to this channel's own baseline.

## AI LABS video — Claude motion-graphics workflow

Source: YouTube `eFog2ttK95g` (AI LABS / Claude motion tutorial). Watched and used as a workflow reference, not as a renderer.

**Adopted (in spirit, then in repo code in rounds 6–7):**

- A frozen **`VIDEO.md` brief** written before the build, so a fresh session can continue without re-asking.
- A **banned-slop list** used in plan, build, and review (tiny corner labels, fake timecodes / HUD, generic AI-video patterns). Several of these are now gates.
- A **fixer** path so the agent does not redo finished work and burn usage. The repo's fixer is narrower (value-only) and guarded in code.
- Do not render the final file until stills and the plan have been checked (preview-first loop).
- Usage warning: one-prompt video work can consume a large share of a weekly limit, often by repeating finished work or starting from an unclear idea.

**Skip:** treating their stack or model-effort advice as mandatory. This repo is LLM-agnostic and already has its own skills, gates, and brand kit.

## MoneyPrinterTurbo (harry0703/MoneyPrinterTurbo)

Analysed 2026-11-26. Popular MIT “Shorts factory” (~146k stars at the time): LLM script → TTS → captions → **stock footage** (Pexels, Pixabay) + background music.

**Adopted (round 8, with Felipe's approval on queue/publish):** a batch topic queue with `--stop-at` and preflight; a review-only publish pack (titles, captions, hashtags, synthetic-media and not-for-kids flags, credits, `review.md`); script-aligned captions that fail if alignment breaks; narration pause marks (implemented as Kokoro `[pause: Ns]`, not Edge TTS); sanitised credit URLs; a cleaner provider-config pattern for the common LLM layer.

**Skip:**

- Stock / reused footage as the base (YouTube reused-content and inauthentic-content risk).
- Pexels and Pixabay as stills (not CC0 / public domain; breaks the photo rule).
- Music bundled in that repo (the upstream README warned it was taken from YouTube).
- Unofficial Edge TTS as the primary voice.
- Automatic posting.

## Promptkura and hook skills (2026-11-26)

[Promptkura](https://promptkura.me) is a paid prompt/skill library (about US$29.99 lifetime, on the order of 13k prompts). Much of the material is already public on GitHub. The product was new and closed-source, with modest weekly downloads. The only visible video example without paying was a prompt for generative clips (Veo / Sora / Kling), which does not fit narrated explainers.

**Decision: do not buy or install it.**

Better free references for hook craft: [hook-anatomy](https://www.skills.sh/scrollmark/social-skills/hook-anatomy) and [video-hook-generator](https://www.skillsdirectory.com/skills/nicepkg-video-hook-generator). Ideas taken into the **round 8 hook step** (code first, not a prompt pack): 3–5 mixed-pattern candidates (curiosity gap, visual pattern interrupt, specific question, careful contrarian); a judge plus payoff check; measured tests (narration soon, anomaly on frame 1, curiosity in the first sentence, short first on-screen line, no “hey guys” / “today I'll show you”); no “wait, don't scroll” style lines. Current Sky/Elevator hooks stay as they are until Felipe approves a script change.

## Voice options

Current default: **Kokoro `am_michael`**. Details and licences: [`LICENSES.md`](../../LICENSES.md), [`skills/voice`](../../skills/voice/SKILL.md), [`TESTS_R5.md`](../TESTS_R5.md).

| Option | Licence / notes | Verdict |
|---|---|---|
| Kokoro 82M (`am_michael`) | Apache-2.0, local, fast, no clone | **In use** |
| Kokoro `am_fenrir` | Wider pitch range (measured 12.7 st vs 8.6) | Worth a human listen; not switched |
| Qwen3-TTS | Apache-2.0, can clone, English | Tested in r3, **not adopted** (slow, not clearly better) |
| Pocket TTS (Kyutai) | Code MIT; weights gated, confirm licence; consent required to clone | **Best local clone candidate** when Felipe records a sample. Catalogue Expresso/EARS voices are CC BY-NC — do not use those. |
| CosyVoice | Apache-2.0, zero-shot clone | Candidate on Mac / MLX; untested in this pipeline |
| GPT-SoVITS | MIT, fine-tune from little audio | Candidate; heavier install |
| Chatterbox (mlx-audio) | MIT, but **retired** Aug 2026 | Do not depend on it |
| ElevenLabs Creator | Paid (~US$22/mo); free plan is not commercial | Paid fallback if local clone quality is not professional |
| F5-TTS, Fish S2 Pro | Non-commercial / research weights | **Skip** |
| ZONOS3-Mini | Apache-2.0 weights; practical only with a GPU | Skip on CPU-only boxes |
| Unofficial Edge TTS | Not an official API | **Skip** as primary voice |

## Other tools already judged (2026-11-25)

Adopted from that pass: ffmpeg-normalize, Lucide, Tabler, Kenney CC0 SFX, Inter, Remotion official skills, whisper.cpp captions. Explainroo, papercut-explainer, and iart-ai explainer/motion skills were useful as references (AGENTS.md flow, paper-cut motion, hook/QA ideas), not as a replacement for this brand kit.

**Skip:** ghost-editor (HyperFrames, Mac Vision, not Remotion); MotionClone and other diffusion/video-to-video tools; onetake (non-commercial licence); Ken Burns “media pipeline” skills; using YouTube-ripped or uncleared music. CreatorMix-style libraries that warn about Content ID on Instagram/TikTok/Facebook are a poor default; Kenney CC0 is what the repo ships.

Early research also listed youtube-agent-skill, remotion-shorts-skill, shorts-factory, and similar. Steal checklists (safe zones, variation axes), not their look, and never their auto-upload.

## Production-research page (2026-11-25)

A longer tool survey (voice engines, Mac install sketch, platform APIs, AI labels, anti-slop practice) was written as a private Page, “Pipeline completo: That's the Mechanism,” building on the 2026-11-19 plan “Plano: canal de Shorts curiosos.” Several of those recommendations have since been **superseded** by repo decisions: the pipeline is LLM-agnostic (not Claude-only); voice cloning is postponed; publish stays manual; stills are CC0/PD only; work ran first on a Linux box so the pipeline would not depend on the Mac. Prefer this folder and `AGENTS.md` over those pages when they disagree.
