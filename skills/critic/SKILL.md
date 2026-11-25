---
name: critic
description: Independent multimodal video critic via Gemini Files API (watches rendered MP4 with audio). Use after automated QA passes on v4 renders (and optionally on a baseline render).
---
# Independent Video Critic

## Purpose
The builder never grades its own work. `scripts/critic.py` uploads the rendered MP4 (including its mixed audio track) to Gemini via the Files API (`gemini-2.5-pro`, falling back to `gemini-2.5-flash` / `gemini-3-flash-preview`), requests a structured rubric review across 8 dimensions (`1–10`), and saves the output to `qa/<Id>/<SUF>/critic.json` and `critic.md`.

## Security
- Uses `GEMINI_API_KEY` from the environment via the `x-goog-api-key` HTTP header only.
- NEVER print, echo, or embed `GEMINI_API_KEY` in URLs, logs, or docs.

## Usage
```bash
P=.venv-tts/bin/python   # any python3 with requests
SUF=v4 $P scripts/critic.py QR
SUF=v4 $P scripts/critic.py Elevator
SUF=v4 $P scripts/critic.py Sky

# Baseline comparison on v3:
$P scripts/critic.py Elevator --mp4 renders/Elevator_v3.mp4 --out-dir qa/Elevator/v4/baseline_v3 --label baseline_v3
```

## Routing findings
1. Read `qa/<Id>/v4/critic.json` and `critic.md`.
2. Route bugs/regressions to `docs/LESSONS.md`; if a finding repeats across episodes, turn it into an automated check in `scripts/qa.py`.
3. Route non-bug creative ideas to `docs/BACKLOG.md`.
4. If any dimension scores **below 7**, address the top timestamped issues and run one more render + QA iteration, then re-run the critic.
5. `critic.py` logs each call, token count, and `$0.00` free-tier cost to `metrics/runs.jsonl` and rebuilds `metrics/metrics.json` + `docs/METRICS.md`.
