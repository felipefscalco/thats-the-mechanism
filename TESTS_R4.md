# Round 4 tool tests

## cloveric/claude-drawing-skill (commit 6af36dc, 2026-11-08) · licence MIT (LICENSE, "Copyright (c) 2026 cloveric")
What it is: Python (numpy + Pillow) procedural painting library with 80+ styles. It renders **raster** images (PNG/JPG), not SVG or animation.
Test: `assets/library/backdrops/make_backdrops.py` uses `lib/flatvector.py` (`FlatVector`) with our palette to draw four 1080x1920 backdrops:
`sky_noon`, `sky_sunset`, `city_dusk`, `street_wall` (4.8 s wall for all four, CPU only, 313 MB peak, $0).

Quality: good. Clean flat shapes, lit/shade faces, soft ambient "lifted paper" shadows, a fine print grain. It matches our palette once colours are passed in.
It reads as "illustrated" rather than "infographic", which is exactly what Look B needed. Weak points: rasters can't be re-coloured or
animated per element in Remotion (only moved/scaled as a whole layer); the moon/cloud/mountain primitives are landscape-oriented; text and fonts
are CJK-first (we don't use its text).

Verdict: **Adopt as a tool for static backdrops / parallax plates** (Look B), not as the animation engine. Its *rules* (no outlines, one light,
lit/shade split, short soft drop shadow) are re-implemented in SVG in `assets/library/build_library.py` so foreground objects stay vector and animatable.

## LottieFiles free animations · licence "Lottie Simple License (FL 9.13.21)"
Verified at https://lottiefiles.com/page/license. Not CC0 or MIT, and modified files must be distributed under the same licence. **Rejected** under the
owner's CC0/MIT-only rule. Replacement: original Lottie JSON authored by `assets/library/build_lottie.py` (gear_spin, pulse_ring, scan_line, check_pop),
played with `@remotion/lottie` 4.0.547 (`LottiePreview` composition renders the thumbnails).

## Tabler icons (@tabler/icons-react) · MIT
Installed next to Lucide (ISC); adds machine-specific glyphs (IconElevator, IconCrane, IconEngine, IconBuildingSkyscraper). Adopted.
