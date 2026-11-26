# Channel — That's the Mechanism

English-language faceless Shorts (also Instagram Reels and TikTok) that open one everyday object and show the hidden mechanism. The catchphrase, spoken and shown, is **That's the mechanism.**

The work is kept authentic even when AI is used: original Remotion animation, fact-checked scripts, a consistent brand kit, and no stock b-roll as the base of the video.

## Concept and format

- **One idea per video.** An everyday observation that seems wrong, then the mechanism, then a short callback that loops to frame 0.
- **Length:** 35–55 seconds, about 90–140 spoken English words (~150–160 wpm). Optional later: a 61–70 s TikTok cut with a real extra beat (not padding), only if Creator Rewards is in play.
- **Picture:** 1080×1920, 30 fps, H.264. Flat 2D editorial infographic (Look A, plus drawn backdrops where approved). Not cartoon 3D, not a slideshow, not photoreal people, not a public kinetic-text template.
- **Structure:** hook (subject on screen and moving by 0.3 s) → tension → 2–3 mechanism beats → turn → card **THAT'S THE MECHANISM.** → 6–10 word callback → exact loop back to frame 0. Full rules: [`STYLE_BRIEF.md`](../STYLE_BRIEF.md).
- **Sound:** Kokoro TTS voice `am_michael` at −14 LUFS for now; SFX 10–16 dB under the voice; signature sting on the catchphrase. A cloned voice is postponed (see [`DECISIONS.md`](DECISIONS.md)).
- **Special moment:** one real proof on screen per episode (for example a QR that actually scans).

## Audience and language

- Global, English-first, aimed at high-CPM markets (heavy YouTube use, USD-level ad rates). AI is how the channel crosses language barriers; Felipe speaks PT-BR in working chats, but **on-screen and spoken language is English**.
- Do not launch PT or ES dubs in the first phase: that triples review and splits the audience. The same Remotion compositions can take another voice track later.
- The channel is not about Japan, and it is not an on-camera AI-tool review show (that format was considered and dropped).

## Brand

- **Name:** That's the Mechanism.
- **Intended handle:** `@thatsthemechanism` on YouTube, Instagram, and TikTok, same day, same spelling. As of 2026-11-19 the YouTube URL returned 404, which does **not** prove the handle is free. The pilot QR animation points at `youtube.com/@thatsthemechanism`. **Confirm the handle is ours before publishing**, or switch that QR to the non-scannable library asset. See [`metadata.md`](../../metadata.md).
- **Palette and type:** ink `#0D0E12`, paper `#F3EFE6`, accent amber `#FFB020`, one pillar colour per episode (tech `#4CC9F0`, engineering `#7BD389`, physics `#9B8CFF`, philosophy `#FF7AB6`). Space Grotesk, Inter, JetBrains Mono. Details in the style brief.
- **Pillars (rotate; never two of the same in a row):** technology, engineering, science/physics, philosophy. A 30-idea backlog from the 2026-11-19 plan is at the end of this file.

## Platforms

Post the same 35–55 s cut on YouTube Shorts, Instagram Reels, and TikTok, once a video is approved. Nothing has been published yet.

AI / synthetic-content labels (conservative, current practice in [`metadata.md`](../../metadata.md)):

| Platform | For this channel |
|---|---|
| YouTube | Tick "altered or synthetic content" for the pilot (synthetic TTS). Animation that is not photoreal is not always required to be labelled; cloned own-voice narration is also often exempt. Photoreal fake b-roll would require the label. |
| Instagram | Label realistic AI audio, which includes a cloned or TTS voice. Use the platform's AI label. |
| TikTok | Label realistic AI-generated content; the platform may also auto-label (C2PA). |

## Monetization goal and metrics

**Goal (2026-11-25):** monetization across YouTube, TikTok, and Instagram together, on the order of **US$2,000 per month**. Treat the first stretch as audience-building, not a salary. Confirm tax and payout eligibility in the country of residence before counting on payment. This is not legal or tax advice.

Supporting figures from the 2026-11-19 research (directional; official RPMs are not published):

- **YouTube Shorts:** creator reports and trade press often sit around **US$0.03–0.20 RPM** (revenue per 1,000 views). AIR Media-Tech cited a median of US$0.07–0.20 in most niches, and US$0.328 in the US. Use **RPM, not CPM**. At US$0.20, 10 million views ≈ US$2,000; at US$0.05, ≈ US$500.
- **YPP today:** 1,000 subscribers plus 4,000 public watch hours in 12 months, **or** 1,000 subscribers plus 10 million qualified Shorts views in 90 days. **From 1 February 2027, for new channels:** 8,000 hours in 365 days **or 20 million Shorts views in 90 days**, still with 1,000 subscribers. The monthly Shorts fund may also require 10 million qualified views in 90 days.
- **TikTok Creator Rewards:** 18+, 10,000 followers, 100,000 views in 30 days, and videos **at least 1 minute**. The 35–55 s cut does **not** qualify. A 61–70 s TikTok-only cut is the later path, not the default.
- **Instagram Reels bonuses** are invite-only and geographically limited (Reels bonus: US and South Korea). Do not budget for them. Gifts, subscriptions, and brand partnerships are separate, later paths.
- **Judge the median of ~30 videos**, not the mean. The same pipeline can swing two orders of magnitude by topic (public example: a Truecaller Reel at ~1 M views, then a reCAPTCHA Reel at 3,452). Official Shorts studio metric: “How many chose to view” (stayed vs swiped). Compare each video to this channel's own baseline. YouTube Shorts “views” count every start and replay; prefer engaged views when available.

**What will not fund the main channel:** clipping other people's content, generic UGC, or stock/reused footage. Those conflict with the format and with YouTube reused-content rules. Brand deals and a media kit come after there is an audience. A parallel clipping account was discussed as an optional experiment only, never under this brand.

## Current pilots (unpublished)

| # | Slug | Composition | Pillar | Version on `main` (after round 9) |
|---|---|---|---|---|
| 001 | `01-qr-code` | `QR` | Tech | v7 |
| 002 | `02-elevator` | `Elevator` | Engineering | v6b (v7 did not ship) |
| 003 | `03-sky` | `Sky` | Physics | v8 |
| 005 | `05-anc-headphones` | `ANC` | Tech | v7 |
| — | `04-ice-demo` | `IceDemo` | — | Template smoke test only; not shippable |

Publish packs are review-only, for example `publish/01-qr-code/` (QR v7) and `publish/03-sky/` (Sky v8). No `APPROVED` file, no upload.

## Topic backlog (from the 2026-11-19 plan; not a shooting schedule)

Every idea still needs two independent sources before it is scripted. Titles and hooks are in English, as the video would be.

**Technology.** Incognito doesn't hide you from the site. Deleting a file almost never erases it. Why 2FA codes die in 30 seconds. Why a QR code still works with a logo on top (pilot). Why Wi-Fi dies two rooms over. The cloud has a street address. Why paste wrecks typography. Why a USB stick has to be ejected.

**Engineering.** An elevator almost balances you (pilot). Those gaps in the bridge are the point. Planes take off into the wind. A rigid skyscraper would be the dangerous one. Why a dam is thicker at the bottom. Gyroscopes are not why a bicycle stays up. Why a flask doesn't sweat. A bolt tightened too hard can be worse.

**Philosophy.** The ship of Theseus is a server migration. The map is not the territory. The trolley problem is a bad test for cars. Cogito was a demolition job. Buridan's ass and the Netflix queue. The veil of ignorance as a design constraint. You can't step in the same river twice.

**Science.** Why ice is slippery, really. An open fridge heats the room. A microwave is picky. Blue sky and red sunset are the same trick (pilot). Your head is a pressure vessel. A compass never pointed at the North Pole. Boiling water, raw pasta.
