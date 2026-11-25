# Round 4 style frames (for approval before animating v4)

`contact_sheet_style_frames.jpg` = all 24 frames. One sheet per episode: `sheet_qr.png`, `sheet_elevator.png`, `sheet_sky.png`.
Full-size PNGs (1080x1920): `final/<ep>_<look>_<n>-<kind>.png`. Earlier iterations: `r1/`, `r2/` (r1 -> r2 fixed title/art overlap, labels off the safe zone, credit overlaps; r2 -> final nudged the Elevator shaft and stopped a tag from wrapping).

Frames per episode: 1 hook (title-as-hook "The X that Y" + scale reveal end state, the amber bracket marks where the camera starts), 2 mechanism, 3 real-photo proof card, 4 end card.

- **Look A — current brand refined.** Dark ink stage, line/flat art, brighter hook (Elevator opens on a bright paper shaft: fixes the dark first frame), contrast fixes (A CRANE, NO SCAN, SHORT PATH pills), ProofCard with an amber frame.
  A2 and A4 are real frames of the current episode code (with the contrast fixes) so they show exactly what v4 would look like without new art.
- **Look B — illustrated.** Backdrops drawn with claude-drawing-skill FlatVector in the brand palette; foreground from `assets/library` (lit/shade faces, soft shadows, faceless characters); labels as paper/colour tags; ProofCard as a taped print. Same brand chip, captions and deck as A.

Rendered with `node remotion/style_frames.mjs style_frames/final _scratch/realframes.json` (24 stills in ~31 s) and `scripts/style_sheet.py`.
