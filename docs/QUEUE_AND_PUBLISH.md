# Batch topic queue and publish pack

Round 8, design approved by Felipe. Two tools:

- `scripts/pipeline.py` runs many topics through the pipeline, one by one, and resumes after a failure.
- `scripts/publish.py` builds everything needed to post an episode. It posts nothing.

Both follow the repo rules. Rules live in code, not prompts. Every LLM call goes through `scripts/llm.py` roles. Human gates stay human. Nothing is uploaded.

---

## 1. Batch topic queue: `scripts/pipeline.py`

### 1.1 Topic file

The topic file is either JSONL (one JSON object per line; lines starting with `//` are ignored) or a JSON list. An example is in `queue/topics.example.jsonl`.

```jsonl
{"title": "Why a microwave heats unevenly", "angle": "standing waves leave cold spots; the turntable is a workaround, not a fix", "priority": 5, "approved": true}
{"title": "Why the sky is blue but sunsets are red", "angle": "the same scattering seen from two places", "priority": 9, "approved": true, "slug": "03-sky", "id": "Sky", "prev": "renders/Sky_v7.mp4", "suf": "v8"}
{"title": "How a lock's pin tumblers work", "angle": "shear line", "priority": 7, "approved": false}
```

| field | required | meaning |
|---|---|---|
| `title` | yes | Working title. A new episode's slug is built from it, for example `07-why-a-microwave-heats-unevenly`. |
| `angle` | yes | The one idea the episode explains. The `writer` role gets it. |
| `priority` | yes | A number. Higher runs first; ties keep file order. |
| `approved` | yes | Must be JSON `true`. Any other value (`false`, `"yes"`, `1`) means the topic is **skipped** and its state is marked `skipped`. Only Felipe flips this. |
| `slug` | no | An existing episode folder (`episodes/<slug>`). If omitted, it is derived from the title. A title that matches an existing folder reuses that folder. |
| `id` | no | Remotion composition id. Default: the first two words of the slug, in PascalCase. |
| `pillar` | no | `tech`, `eng`, `sci` or `philo` (default `sci`). Used when scaffolding. |
| `prev` | no | Previous render, used by the pairwise judge at `ship`. |
| `suf` | no | Render suffix / QA folder (default `v1`). |

A topic missing any required field aborts the whole run before anything happens, and the error names the line.

### 1.2 CLI

```bash
# checks only: CLIs per role chain, ffmpeg/ffprobe, node/npx, venv, models, CLI logins. Exit 2 if anything is missing.
.venv-tts/bin/python scripts/pipeline.py --preflight --stop-at ship

# what would run, per topic. Writes nothing; never calls an LLM.
.venv-tts/bin/python scripts/pipeline.py --batch queue/topics.jsonl --stop-at hooks --dry-run

# run every approved topic up to the audio stage
.venv-tts/bin/python scripts/pipeline.py --batch queue/topics.jsonl --stop-at audio

# one topic only; retry a topic that failed earlier
.venv-tts/bin/python scripts/pipeline.py --batch queue/topics.jsonl --only 03-sky --stop-at ship --retry-failed

# state table
.venv-tts/bin/python scripts/pipeline.py --status
```

`--batch-file` is an alias of `--batch`. `--stop-at` names the **last** stage to run (default `ship`).

### 1.3 Stages

| # | stage | what runs | LLM | can wait on a human |
|---|---|---|---|---|
| 1 | `plan` | Scaffolds the episode if missing (`new-episode.sh`, which writes placeholder captions so the shared Remotion bundle keeps compiling). If `script.txt` is still the template, the `writer` role drafts `script.txt` + `brief.md` and lists every factual claim in `facts.json` as `unverified`. | writer | – |
| 2 | `hooks` | `scripts/hooks.py gen`: 3-5 hooks from the `hooks` role (curiosity gap / visual pattern interrupt / specific question / careful contrarian). Code rules filter them (ban list, word limits, curiosity signal, payoff quote found later in the script). The `hook_judge` role scores the survivors on a rubric. The best one replaces the draft's first sentence, **but only if the current script text is not approved** (`gates.py require … script` fails). An approved script is never rewritten; the chosen hook is then only a proposal in `hooks.md`. | hooks, hook_judge | – |
| 3 | `script` | `facts.py check` (every number and claim verified with 2 sources) and `gates.py require <slug> script` (human gate, keyed to the script's hash). | – | **yes** |
| 4 | `audio` | Kokoro TTS (with `[pause: Ns]` tags giving exact silence) → loudnorm −14 LUFS → script-aligned captions (`captions.py` stops the topic if alignment breaks) → mix → `durations.json`. | – | – |
| 5 | `preview` | `build_loop.py --until preview`: the planner writes VIDEO.md, the builder implements it, and the loop runs the still-only gates. | planner, builder, fixer | – |
| 6 | `ship` | `build_loop.py --until judge`: one full render + all gates + pairwise/calibrated judge. Then `publish.py pack` (section 2). | builder, critics, clusterer | – (the upload approval is separate, see 2.4) |

### 1.4 State files

There is one file per topic: `queue/state/<slug>.json`. It is gitignored because it is machine-local. It is rewritten atomically after every stage.

```json
{
 "slug": "07-why-a-microwave-heats-unevenly", "title": "Why a microwave heats unevenly", "id": "WhyA",
 "status": "waiting",
 "stages_done": ["plan", "hooks"],
 "waiting_stage": "script",
 "waiting_on": "facts gate: FAIL | unbacked quantity '2.45' in: 'A magnetron … 2.45 gigahertz.' …",
 "attempts": 1,
 "history": [
  {"t": "2026-11-26T05:15:02-0300", "stage": "plan",  "status": "done", "wall_s": 21.2, "writer": "claude", "cost_usd": 0.124},
  {"t": "2026-11-26T05:15:28-0300", "stage": "hooks", "status": "done", "wall_s": 25.7, "chosen": "Why is your microwave leftover scalding in one spot and frozen in another?", "applied": true, "cost_usd": 0.047},
  {"t": "2026-11-26T05:15:29-0300", "stage": "script", "status": "waiting", "reason": "facts gate: …"}
 ]
}
```

| status | meaning | what happens on the next run |
|---|---|---|
| `pending` | never started | runs from `plan` |
| `running` | in progress, or the process was killed | resumes at the first stage not in `stages_done` |
| `waiting` | a human gate is closed (facts or script approval). This is not a failure. | re-checks the gate; continues once it is open |
| `failed` | a stage raised an error. `failed_stage` and `last_error` hold the error tail. | skipped unless `--retry-failed`; then it resumes at the failed stage |
| `stopped_at_<stage>` | reached `--stop-at` | a later run with a further `--stop-at` continues from there |
| `done` | ran through `ship` | nothing to do |
| `skipped` | `approved` is not `true` | re-evaluated every run |

### 1.5 Resume and failure behaviour

- **Resume.** A stage is recorded in `stages_done` only after it succeeds. Rerunning the same command after a crash, a kill or a reboot continues at the first missing stage. `build_loop.py` has its own resumable `loop_state.json` inside `preview` and `ship`, so a long loop is not redone either.
- **Isolation.** Every topic runs in its own try/except. One failing topic (a crashed render, a CLI error, a scaffold collision) is marked `failed` with the error, and the queue moves on to the next topic. This was tested in r8: a topic whose `id` collided with an existing episode failed at `plan`, and the next topic still ran `plan` → `hooks` → `waiting` (facts).
- **Preflight first.** Preflight runs **before any LLM call**. It checks only what the requested stages need:
  - for every role used, at least one installed provider in its fallback chain;
  - for the providers that will be used, whether a login is present (`claude`: token env, token file or `claude auth status`; `agy`: CLI profile present). The result is recorded as true or false; no token value is ever read into output or printed;
  - `ffmpeg`/`ffprobe`, plus `node`/`npx` for render stages;
  - the venv, and the Kokoro and whisper.cpp models for `audio`;
  - Remotion for `preview` and `ship`.

  Any problem means exit 2 and no topic runs. `--skip-preflight` bypasses it; use it only for debugging.
- **Never self-approves.** The queue never calls `gates.py approve` and never flips `approved`. The script gate and the fact gate are where Felipe reviews.

### 1.6 Not automated

- Fact verification. `writer` only lists claims. A researcher or Felipe fills `facts.json` with sources.
- Script approval (`gates.py approve <slug> script --by Felipe --artifact episodes/<slug>/script.txt`).
- Topic approval (`"approved": true`).
- Parallel topics. Topics run one at a time on purpose: the scope guard in `llm.py` reverts out-of-scope edits across the work tree, so two builders must never share one checkout.

---

## 2. Publish pack: `scripts/publish.py`

### 2.1 CLI

```bash
# build or refresh the pack from the final render (ship runs this automatically)
.venv-tts/bin/python scripts/publish.py pack Sky 03-sky --suf v8            # LLM drafts the text once (role `publisher`)
.venv-tts/bin/python scripts/publish.py pack Sky 03-sky --suf v8 --no-llm   # deterministic text from the script
.venv-tts/bin/python scripts/publish.py pack Sky 03-sky --suf v8 --regen-text   # throw away the saved draft text

.venv-tts/bin/python scripts/publish.py verify 03-sky                       # re-check limits, flags, credits
.venv-tts/bin/python scripts/publish.py upload 03-sky --platform youtube_shorts   # STUB: always refuses in r8
```

### 2.2 Pack contents: `publish/<slug>/`

| file | in git | contents |
|---|---|---|
| `video.mp4` | no (gitignored) | Byte copy of the final render. Its sha256 is in `pack.json`. |
| `pack.json` | yes | Everything below. |
| `review.md` | yes | What Felipe reads: the three posts with their limits, the disclosure flags, credits and sources, the checks, a checklist, and the exact approve command. |
| `APPROVED` | no (gitignored) | **Created by Felipe only.** It contains the pack sha. |
| `uploads.jsonl` | yes | Append-only log of every upload attempt (see 2.5). |

`pack.json`, abridged:

```json
{
 "episode": "03-sky", "composition": "Sky", "render": "renders/Sky_v8.mp4", "video_sha256": "b1df…",
 "platforms": {
  "tiktok":          {"title": "…", "caption": "…\n\nImages: NASA (JSC) (Public domain …)\n\n#ThatsTheMechanism #science …",
                      "hashtags": ["#ThatsTheMechanism", "#science", "#physics", "#optics", "#sunset"],
                      "lengths": {"title": 42, "caption": 414, "hashtags": 5}, "limits": {"title": 100, "caption": 2200, "hashtags": 5},
                      "ai_generated_content_label": true, "request_id": "a1242a4109fa9af83b50"},
  "youtube_shorts":  {"…": "…", "hashtags": ["#Shorts", "#ThatsTheMechanism", "#science"],
                      "synthetic_media": true, "made_for_kids": false, "category": "Education", "visibility": "private_until_approved",
                      "request_id": "0239e162473d1eeac668"},
  "instagram_reels": {"…": "…", "ai_info_label": true, "request_id": "…"}
 },
 "credits": {"images": [{"title": "Earth Observation", "author": "NASA (JSC)", "license": "Public domain (NASA media usage guidelines)",
                         "source_url": "https://images.nasa.gov/details/iss028e007274", "license_url": "https://www.nasa.gov/…"}],
             "sources": [{"title": "Met Office", "url": "https://weather.metoffice.gov.uk/…"}]},
 "draft": {"title": "…", "caption": "…", "tags": ["…"]},
 "approval": {"required": true, "file": "publish/03-sky/APPROVED", "status": "pending"},
 "upload": "not implemented (r8): stub refuses",
 "pack_sha": "3dedb8eb5038068d",
 "violations": []
}
```

### 2.3 Platform limits and flags (enforced in code)

| platform | title | caption | hashtags | flags |
|---|---|---|---|---|
| TikTok | 100 | 2200 | 5 | `ai_generated_content_label: true` |
| YouTube Shorts | 100 | 5000 | 3 (`#Shorts` first) | `synthetic_media: true` (altered/synthetic content disclosure: synthetic voice and generated visuals; conservative default), `made_for_kids: false`, `visibility: private_until_approved` |
| Instagram Reels | 125 | 2200 | 8 | `ai_info_label: true` |

How the text is built:

- Text is cut on word boundaries.
- The caption ends with the image credit line and then the hashtags. All three must fit inside the caption limit.
- `#Shorts` never goes on TikTok or Instagram.
- The brand tag `#ThatsTheMechanism` is always included.
- The `publisher` role drafts the text once. That draft is saved in `pack.json`, so re-packing gives the same text and the same sha unless `--regen-text` is passed.
- `violations` lists any of the following. A pack with violations can never be uploaded:
  - a limit overflow;
  - wrong disclosure flags;
  - a banned clickbait or padding phrase (the same ban list as the hook step);
  - a credit or caption that leaks a token, a URL query, userinfo or a local path. Credits come from `scripts/credits.py`, which rebuilds rows from a whitelist and keeps only public `http(s)` page URLs.

### 2.4 Approval flow

1. `ship` (or `publish.py pack`) writes the pack. `review.md` ends with the exact approve command:

   ```bash
   echo 3dedb8eb5038068d > publish/03-sky/APPROVED
   ```

2. Felipe watches `video.mp4` with sound, works through the checklist, and runs that command himself. The bot never creates `APPROVED`.
3. `pack_sha` is the sha256 of the episode, the video sha, the platform posts and the credits. If anything changes (a new render or edited text), the sha changes and the old `APPROVED` no longer matches. The approval is void and Felipe must review again.
4. `upload` checks the following in order and logs every outcome:
   1. If the `request_id` was already `posted`, it logs `skipped_duplicate` and does nothing.
   2. If there is no `APPROVED` file, it logs `refused` (exit 3).
   3. If `APPROVED` does not contain this `pack_sha`, it logs `refused` (exit 3).
   4. If the pack has violations, it logs `refused` (exit 3).
   5. Otherwise it logs `refused`: "approved, but no uploader is implemented in r8" (exit 4).

### 2.5 Idempotency

- Every post has a `request_id` = sha256(`slug|platform|video_sha|title|caption`)[:20]. The same video with the same text always gives the same id.
- `uploads.jsonl` is append-only: `{t, platform, request_id, pack_sha, status, reason}`.
- A future uploader must log `posted` with the platform's returned post id. It must refuse to post a `request_id` that is already `posted`. That stops double-posting after retries, crashes or re-runs. It must also pass the `request_id` as the platform's idempotency key wherever the API supports one.

### 2.6 Not automated, by design

- **No upload or posting of any kind** in r8. The stub refuses even with a valid approval.
- No platform logins, API keys or OAuth flows.
- No scheduling and no thumbnail upload.
- `APPROVED` is never written by the bot.
- Disclosure flags are fixed in code (`synthetic_media` true, `made_for_kids` false). Changing them is a code change that goes through review.
