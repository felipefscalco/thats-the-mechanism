# Pairwise critic — Microwave (ship)

- A: `/Users/felipefscalco/orca/workspaces/thats-the-mechanism/initial-test/renders/Microwave_v1_it3.mp4`
- B: `/Users/felipefscalco/orca/workspaces/thats-the-mechanism/initial-test/renders/Microwave_v1_it8.mp4`
- Model: `gemini-3.8-flash-high` · free tier $0
- **Preferred: B** (strength 2/3, confidence high); weighted margin B−A = +1.06

## Weaknesses A
- In Shot 06/07 (0:29-0:35), the emitting source on the left is represented by an unlabelled, featureless beige silhouette with empty notches, looking like an incomplete draft asset or broken SVG shape.
- In Shot 03/07 (0:14-0:15), the introduction of the wavelength measurement lacks an immediate relative scale comparison to the barrier's aperture diameter.
- The terminating frame retains two large summary overlay badges and displays a 0:00 timer, creating an abrupt visual seam when looping back to the opening 0:30 unbadged state.

## Weaknesses B
- The loop seam retains the concluding summary callout pills and a 0:00 counter state, preventing a seamless pixel-level loop back to the initial frame.
- The sensor probe graphic in Shot 06/07 (0:34-0:35) is somewhat delicate and thin compared to the heavy typography of the adjacent numerical limit badge, diminishing its visual impact.
- In the cross-section bounce animation (0:18-0:23), the reflected wave overlap can momentarily read as wave interference rather than a single reflected wave path.

| dimension | better | margin | why |
|---|---|---:|---|
| hook | tie | 0 | Both versions share an identical, high-energy hook showing the front face with active motion, bold typography, and immediate narrative question delivery within the first second. |
| clarity | B | 2 | Version B introduces a scale callout for the aperture diameter alongside the wavelength curve at 0:15, and provides an explicitly labeled, detailed side profile in the regulatory measurement shot at 0:29, whereas Version A leaves the source device as an ambiguous, unlabelled silhouette. |
| motion_craft | B | 1 | Version B integrates smooth contextual badge arrivals and emission rings around the side profile seam, elevating the kinetic pacing without distracting from the central data. |
| design_typography | B | 2 | Version B avoids the raw, untextured placeholder shape found in Version A's leakage diagram (0:29) by adding clear technical labeling ('OVEN, SIDE-ON') and balanced vector styling consistent with the brand system. |
| concept_wow | B | 1 | Showing the micro-aperture comparison directly beneath the macro wave dimension creates an immediate intuitive spark before transitioning into the barrier mechanics. |
| style_fidelity | B | 2 | Version A has an unpolished, incomplete vector outline in shot 6 that breaks the editorial engineering diagram aesthetic, while Version B maintains rigorous schematic polish throughout. |
| finish_texture | B | 2 | Version B feels like a completed, broadcast-ready technical animation with consistent line weights, subtle glows, and complete vector assets, whereas Version A contains apparent draft geometry. |
| sound_sync | tie | 0 | Both versions utilize the same crisp, well-mixed Kokoro narration track with identical whooshes, UI transients, and end-sting placement. |
| voice_captions | tie | 0 | Both versions feature perfectly timed, high-contrast captions centered in the designated safe zone with identical kinetic highlighting. |
| loop | tie | 0 | Both versions return to the hero subject but suffer from the same loop jump: summary badges remain on screen at the final frame and the display timer reads 0:00 instead of seamlessly matching frame 0 (which reads 0:30 with no badges). |

Version B is clearly superior due to the elimination of Version A's unfinished placeholder art in the regulatory leakage sequence (0:29) and the inclusion of a crucial scale callout at 0:15 that visually anchors the wavelength to the aperture size. Both versions share identical high-quality audio mixing and captions, but Version B delivers a complete, professional engineering-diagram finish.

## General rules (reusable, episode-agnostic)
- **[component · major · design_typography]** Always provide explicit labels and internal structural features on technical silhouettes rather than unadorned solid shapes. (evidence A 0:29)
- **[prose · minor · clarity]** Always provide an immediate visual scale reference when introducing absolute physical dimensions before transitioning to an abstract cross-section. (evidence A 0:15 / B 0:15)
- **[gate · major · loop]** Never retain end-card summary badges or modal callouts into the final frame if they create a visual jump cut against the opening scene. (evidence A 0:44 / B 0:44)
- **[gate · minor · sound_sync]** Ensure dynamic numeric stat reveals synchronize precisely with an audio transient or punch cue within three frames. (evidence A 0:32 / B 0:32)
- **[gate · minor · loop]** Always ensure recurring environmental props returned to in the closing hook match the visual configuration of the opening frame. (evidence A 0:42 / B 0:42)
