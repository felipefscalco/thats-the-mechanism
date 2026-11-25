---
name: package-metadata
description: Write titles, descriptions, hashtags, and a pinned comment for a finished Short, including AI-disclosure notes for each platform. Use when packaging an episode for upload, or drafting metadata.md. Never uploads.
---

# package-metadata

Prepare the listing copy for a **human** to paste into YouTube, Instagram, and TikTok. **Do not upload, schedule, or call a publishing API.**

## Deliverable

Append a section to `metadata.md` (see the pilot entries) with:

- **Title** for YouTube Shorts, ≤ 60 characters, hook-first, no clickbait numbers you did not source.
- 1–2 alt titles.
- **Description:** the mechanism in plain language, then sources (named + URL), then a short hashtag line. Credit the special moment if it is observable (e.g. “the QR in this video actually scans”).
- **Hashtags** for TikTok/Instagram (few, specific). Include `#thatsthemechanism` when it fits.
- **Pinned comment:** one extra fact or a viewer test, a primary source, and a question for the next topic.
- **Language:** English, matching the voiceover.

## AI / synthetic-content labels

The pilot voice is Kokoro TTS (synthetic). A later personal voice clone may not need a YouTube “altered content” label, but **Instagram and TikTok still ask for a label on AI-generated media**. Until a human decides otherwise, note in the metadata:

- YouTube: the conservative choice for a fully generated Short is to declare altered or synthetic content.
- Instagram and TikTok: use each platform’s required AI-content toggle.

Do not hide that the video is AI-assisted.

## Rules

- Every fact in the description must already appear in `sources.json`.
- Do not promise a publish time or auto-post.
- Stop and wait for human approval of the final video + this copy.
