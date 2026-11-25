---
name: licensed-photos
description: Find, verify and credit 1-2 real public-domain/CC0 photos per episode for the "real proof" card. Use after the script is locked and before animating.
---
# Licensed real photos ("real proof" card)

## Rule
Only **public domain or CC0**. Reject: NC, ND, BY-SA, BY (attribution licences are out of scope for now), "no licence",
logos/trademarks/insignia, identifiable people, images under 900 px on the short side. "Free on the internet" is not a licence.
Every licence is read from the **source's own API or page** at search time and again at pick time, never assumed.

## Sources (in order of preference)
1. Wikimedia Commons API (`extmetadata`: LicenseShortName, Copyrighted, Restrictions, Credit). HABS/HAER (Library of Congress) scans are excellent for machines.
2. NASA Image and Video Library API (rejects any item with a third-party credit / copyright notice).
3. Openverse API with `license=cc0,pdm`. Openverse is an index: Wikimedia items are re-verified with the Commons API; others with the landing page's licence link.
4. Library of Congress JSON (`rights_advisory` must say "No known restrictions" / public domain / free to use). The LOC API often times out; it is optional.

## Steps
```bash
P=.venv-tts/bin/python
$P scripts/photos.py search <slug> "<query>" [--sources commons,nasa,openverse,loc] [-n 10]   # OK/REJ list with reasons
$P scripts/photo_sheet.py <slug> "<regex on title>"                                        # look at the OK candidates
$P scripts/photos.py pick <slug> <candidate_key> "<role: which shot it proves>"            # re-verifies, downloads, logs
```
`pick` writes `assets/photos/<slug>/<file>`, `remotion/public/photos/<slug>--<file>`, a row in `assets/photos/CREDITS.csv`
(source URL, author, licence, licence URL, how it was verified) and `episodes/<slug>/photo_credits.md` (paste into the description).

## Look before you use (human/bot check, the script cannot see)
- No identifiable faces, no brand logos or readable trademarks in frame (crop them out or reject).
- **QR codes in photos are scannable.** Decode or trace the payload and record it; reject if it points somewhere unknown.
- The photo must prove the claim of the shot it sits in (not decoration).

## On screen
- `ProofCard` (see `remotion/src/style/StyleFrames.tsx`): about 1-2 s, brand frame, slow Ken Burns 1.00 -> 1.06, a "REAL PHOTO" pill + what it is,
  an amber dashed focus box on the part that matters, and a credit line in MONO >= 30 px ("PHOTO: <author> · <licence>").
- One or two photos per video. Keep everything around it flat/brand.
- QA: `qa.py` contrast check covers the pill/labels; the credit line is plain text on the dark stage.
