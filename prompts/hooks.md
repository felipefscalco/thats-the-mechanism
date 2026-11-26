You write the opening hook for a 35-50 s vertical science-explainer Short ("That's the Mechanism", episode {SLUG}).
Write {N} candidate hooks for the script below. The hook REPLACES the script's first sentence only; the rest of the script stays.

Mix the patterns (use at least 3 different ones across the candidates): {PATTERNS}.
- curiosity_gap: state a surprising, true result and withhold the cause.
- pattern_interrupt: the line goes with an odd, instantly visible frame-1 image (an anomaly on screen from frame 1).
- specific_question: one concrete question the viewer can't answer yet. Don't write "Have you ever wondered".
- contrarian: correct a common belief carefully. It must be true and supported by the facts below. Don't use straw men or "everyone is wrong".

Hard limits. These are checked in code, so a candidate that breaks one is discarded:
- `line`: at most {MAX_SPOKEN} words, speakable in under 4 s. The FIRST sentence must open a curiosity gap and must not explain the cause.
- `on_screen`: the first on-screen text line, at most {MAX_ONSCREEN} words. It must not be a transcript of `line`.
- Never use intro padding or clickbait. These are banned: {BANNED}.
- `payoff_quote`: an EXACT quote (5-15 words) copied from LATER in the script that pays off the hook's promise.
- `promise`: the hook's promise in a few plain words, using the same key terms the payoff uses.
- `frame1_visual`: what frame 1 shows. It must be one clear hero or anomaly already moving, never a title card.
- Every claim must stay inside the verified facts.

SCRIPT:
{SCRIPT}

FROZEN PLAN (VIDEO.md, may be empty):
{VIDEO}

FACTS (facts.json excerpt):
{FACTS}

Return JSON only, matching the schema.
