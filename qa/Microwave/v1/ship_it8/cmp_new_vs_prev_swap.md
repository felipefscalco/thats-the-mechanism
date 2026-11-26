# Pairwise critic — Microwave (ship_swap)

- A: `/Users/felipefscalco/orca/workspaces/thats-the-mechanism/initial-test/renders/Microwave_v1_it8.mp4`
- B: `/Users/felipefscalco/orca/workspaces/thats-the-mechanism/initial-test/renders/Microwave_v1_it3.mp4`
- Model: `gemini-3.8-flash-high` · free tier $0
- **Preferred: A** (strength 3/3, confidence high); weighted margin B−A = -1.69

## Weaknesses A
- The top header badge metadata is vertically dense and sits close to the upper safe margin near y 290.
- In shot 04/07 (00:17-00:23), the cross-section diagram contains many competing elements simultaneously (steam, container, wave, bounce, eye, barrier, status pill), creating visual density on smaller screens.
- The transition between the leakage limit shot (00:35) and the recapitulation shot (00:36) is an abrupt hard cut without an easing or whip cue.

## Weaknesses B
- Major rendering failure in shot 06/07 (00:29-00:35): the side-on apparatus renders as a blank, unlabelled beige silhouette completely missing door seams, vents, dials, and technical labels.
- Awkward layout and typography in shot 02/07 (00:08): the 'METAL SCREEN' badge is shoved into the upper-left corner directly against the perforation circles instead of being centered.
- Omission of scale context in shot 03/07 (00:15): lacks the 'ONE HOLE' callout next to the 12 cm wavelength bracket, leaving the viewer without a direct visual comparison between wavelength and hole size.
- Smeary transition blur at 00:05 causing ghosting artifacts on the upper deck badge before settling on the mesh.
- Cramped badge positioning at 00:37 where 'SEES A WALL' crowds the incoming waveform trajectory.

| dimension | better | margin | why |
|---|---|---:|---|
| hook | A | 1 | Video A transitions into the screen shot with cleaner camera scaling and no ghosting artifacts on the upper badge, whereas Video B exhibits smearing on the top card during the 00:05 zoom. |
| clarity | A | 2 | Video A includes an essential scale comparison icon ('ONE HOLE') alongside the 12 cm wave bracket at 00:15 to clarify aperture scale, and renders a fully articulated technical diagram for the side-on view at 00:29-00:35, whereas Video B reduces the apparatus to an unlabelled blank silhouette. |
| motion_craft | A | 2 | Secondary animations, such as the aperture ripple pulse at 00:08 and the scale reference entry at 00:15, are well-staged with balanced easing in Video A, avoiding the jarring placement jumps seen in Video B. |
| design_typography | A | 2 | In Video B at 00:08, 'METAL SCREEN' is awkwardly crammed in the top-left corner against the perforations, and the label at 00:37 collides with the waveform; Video A maintains balanced centering, consistent padding, and clean visual hierarchy throughout. |
| concept_wow | A | 2 | The direct visual juxtaposition of the tiny aperture circle against the 12 cm wavelength in Video A makes the underlying physics concept instantly click, whereas Video B relies purely on mental arithmetic from the viewer. |
| style_fidelity | A | 3 | Video A preserves the technical engineering diagram aesthetic consistently across every shot; Video B breaks style fidelity severely in shot 06/07 where the side-on technical illustration fails to render its linework. |
| finish_texture | A | 3 | Video B exhibits a major rendering defect at 00:29-00:35, displaying a featureless flat beige shape lacking door seams, vents, dials, or labels, whereas Video A delivers complete, polished vector linework. |
| sound_sync | A | 1 | Both share a strong SFX bed and Kokoro TTS mix, but Video A has slightly tighter synchronization between the aperture highlight pulse and audio click at 00:08. |
| voice_captions | tie | 0 | Both versions share identical narration, pacing, volume normalization, and well-positioned word-level highlighted captions within the lower safe zone. |
| loop | tie | 0 | Both cuts resolve cleanly back to the identical front-facing frame-0 state at 0:00 with matching typography and turntable orientation, executing a seamless infinite loop. |

Video A is decisively superior to Video B. Video B suffers from an egregious rendering defect in shot 06/07 (00:29-00:35) where the side-on apparatus collapses into an empty, unlabelled beige silhouette missing all technical linework. Furthermore, Video B shoves the 'METAL SCREEN' badge awkwardly into the upper-left corner against the perforated grid at 00:08 and omits the crucial 'ONE HOLE' visual scale reference callout at 00:15 that makes the wave-to-aperture comparison intuitive. Video A provides complete, refined diagram craft, proper typography padding, and a vastly clearer explanation of the mechanism.

## General rules (reusable, episode-agnostic)
- **[gate · blocker · finish_texture]** Always verify that every vector diagram asset renders interior line work and structural features rather than collapsing into an empty flat silhouette. (evidence B 0:29)
- **[prose · major · clarity]** Always pair physical dimension callouts with an on-screen visual scale reference when introducing microscopic or macroscopic measurements. (evidence A 0:15 / B 0:15)
- **[component · major · design_typography]** Always center section header labels horizontally within diagram containers and maintain a minimum 32px clearance from interior grid elements. (evidence B 0:08)
- **[gate · minor · motion_craft]** Never use full-screen motion blur transitions that cause high-contrast header badges to ghost or smear across shot boundaries. (evidence B 0:05)
- **[component · minor · design_typography]** Always maintain minimum padding between animated waveform trajectories and static status badge pills. (evidence B 0:37)
- **[gate · minor · design_typography]** Keep persistent header badge metadata concise and positioned strictly within the top platform safe zone. (evidence A 0:00)
