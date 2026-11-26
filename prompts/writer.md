You draft a script for "That's the Mechanism", a 35-50 s vertical science-explainer Short of about 110-125 words,
read aloud at 162-168 words per minute.
Topic: {TITLE}
Angle: {ANGLE}
Episode: {SLUG}

The script must follow the channel grammar. Put paragraphs on separate lines with a blank line between them:
1. Hook paragraph. The first sentence opens a curiosity gap about something the viewer has felt or seen and is at most
   14 words long. Never use intro padding ("hey guys", "in this video", "today I'll show you") or clickbait ("secret",
   "you won't believe", "wait, don't scroll").
2. The mechanism, step by step, in 3-4 short paragraphs. Each sentence is one causal step that can be drawn, and each
   step names a concrete thing a label can show.
3. A paragraph that is exactly: That's the mechanism.
4. A one-line payoff that loops back into the hook.
Optional `[pause: 0.3s]` tags (0.05-3.0 s) insert exact silence for a beat. Use at most 2.

Also return:
- `brief`: a short visual plan with one persistent world, a hero for frame 1, and the reveal moment.
- `claims`: every factual claim and number in the script, one per item. A researcher verifies each claim against
  two sources before any voice is recorded, so only state things you are confident are true and checkable.
Return JSON only, matching the schema.
