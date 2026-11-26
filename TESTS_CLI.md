# CLI Integration Tests (Claude Code + Antigravity `agy`)

Workspace: `/workspace/ttm-r6` (branched locally from `ttm-r5`; nothing committed, pushed, or published).
Date: 2026-11-25 (America/Sao_Paulo, UTC-3).

## 1. Claude Code CLI (`claude -p`) — Script Writer + Scene Builder

- **Invocation:** `CLAUDE_CODE_OAUTH_TOKEN="$(cat ~/.secrets/claude_oauth_token)" claude -p --dangerously-skip-permissions --output-format json`
- **Model used:** `claude-sonnet-5-5` (plus 1 `claude-haiku-5-5` web search subcall)
- **Episode built:** `05-anc-headphones` (`CompId: ANC`, pillar `sci` / Physics) — *"These headphones fight sound with sound"* (110 words, 42.6 s with 1.8 s tail).
- **Fact ledger (`scripts/facts.py`):** **PASS** (6 verified facts; 6 real HTTP-200 sources: Wikipedia, BBC Science Focus, Mental Floss, SoundGuys, freeCodeCamp, MakeTechEasier; zero unverified claims or numbers).
- **Storyboard lint (`scripts/lint_shots.py`):** **PASS** (8 shots, 37 beats, longest gap 3.0 s, 4 camera kinds: `glide`, `pull`, `punch`, `push`).
- **Wall time & cost:** **886.6 s (14m 47s)** across 45 agentic turns (`$1.65` list-equivalent usage reported in `--output-format json`, covered by Claude subscription OAuth token).
- **Iterations to pass all 15 QA gates:** **3 iterations**:
  - `it1` (12/15): failed `pre_catchphrase` (-34.8 dB due to clank/swish cues in the 0.2 s window), `safe_zone` (title/label bounds), and `contrast` (2.41:1 red label over light panel).
  - `it2` (14/15): fixed `pre_catchphrase` (-113.3 dB) and `safe_zone` (clean); 1 held contrast failure remained (2.41:1 at 33.4–34.8 s).
  - `it3` (15/15 **PASS**): format `1080x1920@30`, `-14.0 LUFS` / `-1.5 dBTP`, SFX `1.46/s` (`12.9 dB` median under voice, min `8.3 dB`), longest hold `0.1 s`, end card `1.32 s` / payoff settled `1.70 s`, hook `0.64` / `0.661` bright, loop PSNR `52.2 dB`, WCAG contrast median `7.62:1` (p10 `6.28:1`), safe zones clean, labels `>= 30 px`, cadence max gap `3.0 s`, pre-catchphrase `-113.3 dB`.
- **Artifacts:**
  - Final mastered MP4: `/workspace/ttm-r6/renders/ANC_v6.mp4` (14.13 MB)
  - Contact sheet: `/workspace/ttm-r6/qa/ANC/v6/contact_sheet.jpg`
  - Storyboard: `/workspace/ttm-r6/qa/ANC/v6/storyboard.jpg`
  - Final QA report: `/workspace/ttm-r6/qa/ANC/v6/report_it3.json`
- **Quality vs v5 (`QR`, `Elevator`, `Sky`):** Technically compliant (15/15 QA PASS, crisp sound sync, 52.2 dB loop), and Claude generated a custom drawn backdrop (`anc_dusk.jpg`), verified every URL, and fixed its own QA failures. However, visually it leans on a white rounded card container ("slide-deck" look) for Beats 3–5 rather than one continuous physical cutaway like `Elevator`/`QR`, and had a real icon/badge overlap at 00:16 (`SPEAKER` clipping `CHIP` -> `CH!P`) that `qa.py` did not catch.

## 2. Antigravity CLI (`agy -p`) — Video Critic (`--backend agy`)

- **Video & audio ingestion findings (empirically verified):**
  - `agy`'s built-in `read_file` accepts `.mp4` natively, returning **1 fps visual frames** across the timeline (e.g., 54 frames for 53.8 s `QR_v5.mp4`), **with NO audio**.
  - `agy`'s `read_file` also accepts `.wav` natively and **listens to the full mixed audio track** (voice, bed, pops, ticks, whooshes, riser, silence beat, sting).
  - Solution in `scripts/critic.py --backend agy`: extract a 24 kHz mono `.wav` via `ffmpeg` for each MP4, pass both the `.mp4` and `.wav` (plus `research/r5/flatvector/sheet.jpg` in calibrated mode) to `agy` via `--add-dir` + `--json-schema` (converted to lowercase JSON Schema) + `--output-format json`, with strict prompt instructions forbidding shell/repo reads.
- **Quota behavior:** Zero `429` or `503` errors across 7+ `agy` critic calls (Google AI Pro subscription), unlike the Gemini API free tier (exhausted at 20 req/day/model).

### Pairwise `v4` vs `v5` (`gemini-3.8-flash-high`)

| Episode | Comparison | Preferred | Strength / Conf | Margin (B−A) | Wall time | Key finding |
|---|---|---|---|---:|---:|---|
| `QR` | `v4` vs `v5` | **B (`v5`)** | 1/3 · high | `+0.60` | 117.0 s | Spotted smoother `0:47` card transition, crisper SFX separation, and shared `Reed-Solom and` caption split. |
| `Elevator` | `v4` vs `v5` | **A (`v4`)** | 2/3 · high | `-0.94` | 134.8 s | **Caught a real regression in `Elevator_v5.mp4`:** at 00:23–00:24 the v5 cadence zoom pushes the `CAR` bar off the left screen edge (verified via `ffmpeg` frame inspection). |
| `Elevator` (swap) | `v5` vs `v4` | **tie** | 0/3 · high | `+0.00` | 162.4 s | Swap run blurred the 1-frame transient across 84 1-fps images and called a tie, showing 1-fps limits on sub-second zoom transients. |
| `Sky` | `v4` vs `v5` | **B (`v5`)** | 2/3 · high | `+1.32` | 62.5 s | Caught `FlatPlanet` replacing faceted 3D Earth, single-subject sunset hook, and `[ BLUE SCATTERED AWAY ]` pill. |

### Calibrated Single-Video Critiques (`--backend agy`)

| Video | Model | Overall | Verdict | Wall time | Notable findings |
|---|---|---:|---|---:|---|
| `QR_v5.mp4` | `gemini-4-neon-high` | **5.07 / 10** | `ONE MORE PASS` | 210.0 s | Caught `"Reed-Solom and"` caption split and `"30% REBUILDABLE"` tint covering top finder squares at 00:27–00:29 (contradicting 00:41); 1-fps sampling false-flagged sub-second holds/loop already passed by `qa.py`. |
| `ANC_v6.mp4` | `gemini-3.8-flash-high` | **5.80 / 10** | `ONE MORE PASS` | 132.4 s | Caught real `SPEAKER`/`CHIP` overlap at 00:16 (`CH!P`), white-card slide-deck look, and disembodied waves. |
| `ANC_v6.mp4` | `gemini-4-neon-high` | **5.20 / 10** | `ONE MORE PASS` | 159.2 s | Caught `SPEAKER`/`CHIP` overlap at 00:16, `00:17` ear/chip crowding, white-card slide-deck look, and `00:42` transient header ratio `1.22` (from QA report). |

## 3. Verdict & Recommended Role Split

- **Is `agy` a fair substitute for the Gemini API video critic?** **Yes, with one caveat:** pairing `read_file` on `.mp4` + extracted `.wav` gives `agy` full multimodal visual+audio judgment with zero free-tier 429/503 quota pain, and its reasoning quality (`gemini-3.8-flash-high` for fast pairwise, `gemini-4-neon-high` for deep calibrated critiques) matches or beats `3-flash-preview`. **Caveat:** `read_file` samples `.mp4` at **1 fps** (vs configurable `VIDEO_FPS` on the Gemini Files API), so it can miss 4-frame punches/easing and misread fast transitions as static holds or broken loops; always pass `--qa-report` so measured `qa.py` hold/PSNR numbers override 1-fps impressions, and keep `transitions_itN.png` for boundary checks.
- **Recommended pipeline roles:**
  - **Claude Code (`claude -p`, Sonnet 5.5):** **Script writer, fact-checker, and Remotion scene builder / QA fixer** — strong multi-file code editing, disciplined `facts.py` + `qa.py` iteration loop, fast TypeScript debugging.
  - **Antigravity (`agy -p`):** **Independent video critic (`--backend agy`)** — `gemini-3.8-flash-high` for fast pairwise ship gates (`--compare` + swap check) and `gemini-4-neon-high` for deep calibrated fix lists (`--qa-report`), keeping the builder != judge separation (`claude` builds, `agy` critiques) without hitting Gemini API free-tier daily caps.

## 4. Generic critic rules, enforcement hierarchy, and the overlap gate

Work still lives only in `/workspace/ttm-r6` (uncommitted). The official repo change below is the one exception, already pushed.

### Official docs commit (t55u, pushed to `main`)

`github.com/felipefscalco/thats-the-mechanism` @ `49c854c7c1d07743e440d84a618dcb41273ad295` — *Docs: enforcement hierarchy (code over prose) in AGENTS.md*.

Top-level AGENTS.md section **Enforcement hierarchy: code over prose** (gate that blocks the render, then a Remotion primitive that makes the error impossible, then prose only for subjective craft). New rules must declare `gate` / `component` / `prose`. A prose rule that becomes measurable must be promoted to a gate. README.md and CLAUDE.md link to `AGENTS.md#enforcement-hierarchy-code-over-prose`. Secret scan PASS. r6 experimental work was not included in this commit.

### Critic schema + re-runs (`--backend agy`, `gemini-3.8-flash-high`)

`CAL_SCHEMA` / `CMP_SCHEMA` now require `general_rules[]` with `rule` (imperative, episode-agnostic), `category`, `evidence`, `measurable`, `proposed_gate`, `enforcement` (`gate|component|prose`), `severity`. Prompts forbid episode-specific wording in `rule` and prefer gate, then component, over prose.

| Video | Overall | Verdict | Wall | `general_rules` |
|---|---:|---|---:|---:|
| `ANC_v6` | **6.69 / 10** | `ONE MORE PASS` | 109.2 s | 6 |
| `QR_v5` | **5.81 / 10** | `ONE MORE PASS` | 106.3 s | 6 |
| `Elevator_v5` | **5.60 / 10** | `ONE MORE PASS` | 118.3 s | 6 |
| `Sky_v5` | **6.48 / 10** | `ONE MORE PASS` | 120.1 s | 6 |

Outputs: `qa/ANC/v6/critic_rules.json`, `qa/{QR,Elevator,Sky}/agy_rules/critic_rules.json`.

### Overlap gate (A13) — now code, and it catches the 00:16 slip

`scripts/contrast.py` + `scripts/qa.py` check `labels: icon/label clearance >= 36 px (held >= 0.6 s)`. Occupancy comes from a **second** Remotion probe (`{"probeOccupancy":true}`) so WCAG still uses the original `{"probe":true}` pass (real backings, magenta text). Cyan backings are matched tightly to `#00FFFF` so brand teals (header "TECH", hex-cell strokes, chapter "01/05") are not treated as pills.

WCAG on this pass is unchanged vs the earlier green reports (ANC min 1.22 / p10 6.28 / median 7.63, no held failures). The new overlap gate:

| Video | WCAG | Overlap | Held overlap violations |
|---|---|---|---|
| `ANC_v6` | PASS | **FAIL** (5) | **15.6–17.4 s: `SPEAKER` covers `CHIP` (`CH!P`)** — the miss the old 15-gate QA did not catch. Also four verdict-pill / panel overlaps at 4.8–5.8, 20.8–21.4, 31.0–31.8, 33.6–35.0 s (camera punch tucks `QUIET` / `= FLAT` / `PREDICTABLE` / `TOO FAST` under the card). |
| `QR_v5` | PASS | **FAIL** (2) | Verdict-pill / panel overlaps at 4.8–5.2 and 43.6–44.4 s. (An earlier loose cyan mask had also flagged Reed-Solomon hex-cell strokes; that is fixed.) |
| `Elevator_v5` | PASS | **FAIL** (4) | Verdict-pill / panel overlaps at 17.0–26.8, 31.0–33.0, 34.0–35.0 s, plus 24 px clearance (under the 36 px floor) at 24.8–26.8 s. |
| `Sky_v5` | PASS | **FAIL** (7) | Verdict-pill / panel overlaps at 22.6–27.4, 28.0–31.8, 33.6–40.6 s, plus mid-stage label clearance 18–30 px at 18.8–20.2, 30.0–32.0, 35.2–37.4, 37.6–40.6 s. |

`ANC_v6` is still 15/15 on the previous gates; it would fail the new 16th gate if `qa.py` were re-run. Not re-rendered in this pass.

Components that make the same class of error harder: `Lane` / `LabeledBox` (`LANE_GAP = 36`) in `remotion/src/brand/Kit.tsx`, and `LoopEnd` (= `LoopBack`) in `EpisodeShell.tsx` (hook frozen at frame 0). Existing episodes were not rewritten to use `Lane`.

### `scripts/lessons.py`

Scans `qa/**/*.json` `general_rules`, clusters paraphrases (agy, with a local Jaccard + known-gate family fallback — agy clustering hit a 90 s print timeout once; this run used `--local`), promotes a cluster to **active** after ≥ 2 episodes or one blocker, and writes:

- `docs/style_rules.json`
- `docs/STYLE_RULES.md` (active prose + an index of gates/components + candidate gates)
- `docs/active_rules_prompt.txt` (prose only, for the writer prompt)

**24 rules → 16 clusters, 5 active.**

| Cluster | Class | Episodes | Enforcement |
|---|---|---|---|
| Contrast ≥ 4.5:1 (and typography measurables) | **gate** (active) | ANC, Elevator | existing WCAG + 30 px font checks |
| Lock the last frame to frame 0 (loop / HUD state) | **gate** + **component** (active, blocker) | Elevator, QR, Sky | loop PSNR gate + `LoopEnd` / `LoopBack` |
| No stage hold > 2 s | **gate** (active) | Elevator, QR, Sky | existing motion-hold check |
| Minimum 30 px type (and typography measurables) | **gate** (active) | QR, Sky | existing font-size + WCAG checks |
| Don't pop badges with zero anticipation / use overshoot | **candidate_gate** (active) | ANC, Elevator, Sky | not a gate yet — queued in STYLE_RULES.md |
| Icon/label 36 px clearance (the new A13 gate) | **gate** (implemented in code; not yet an active lesson cluster) | — | no critic `general_rules` row was written in those words; the gate was added from the 00:16 `CH!P` slip directly |

No **active prose** rules yet (so `active_rules_prompt.txt` is empty aside from the header). Subjective one-episode rules stay prose and are listed under "Not yet active" (squash-and-stretch climax, physical vs chart typography, SFX material honesty, documentary-card framing, etc.). Other measurable one-episode ideas are candidate gates (slide-deck card detector, 40 px stage-edge clearance, 4-frame chip stagger, hook motion in the first 12 frames, caption mid-word splits).

### r6 files touched (still uncommitted, not pushed)

`scripts/critic.py`, `scripts/contrast.py`, `scripts/qa.py`, `scripts/lessons.py` (new), `remotion/probe_frames.mjs`, `remotion/src/brand/Kit.tsx`, `remotion/src/brand/EpisodeShell.tsx`, `AGENTS.md`, `docs/ACCEPTANCE.md`, `docs/STYLE_RULES.md`, `docs/style_rules.json`, `docs/active_rules_prompt.txt`, critic skill / script-and-factcheck / animate-remotion skills, `TESTS_CLI.md`, plus `qa/**` critic and `overlap_test` artifacts. Episode `05-anc-headphones` and `renders/ANC_v6.mp4` remain from the earlier CLI test.
