# Pairwise critic — Sky (ship_swap)

- A: `/workspace/ttm-r7/renders/Sky_v7.mp4`
- B: `/workspace/ttm-r7/renders/Sky_v5.mp4`
- Model: `gemini-3.8-flash-high` · free tier $0
- **Preferred: A** (strength 3/3, confidence high); weighted margin B−A = -1.89

## Weaknesses A
- In the tangent sunset scene (0:33-0:35), the secondary observer label ('SOMEONE ELSE'S AFTERNOON') is somewhat small and delicate compared to the primary annotations, risking reduced legibility on compact mobile screens.
- The rainbow dispersion bands in the prism shot (0:07) are relatively narrow and could benefit from slightly thicker stroke widths for immediate punch on smaller displays.
- The callback badge ('SAME LIGHT, LATER') at 0:41 sits slightly high in the upper third, which momentarily pulls eye tracking away from the central sunbeam.

## Weaknesses B
- Rigid, slide-deck card paradigm: excessive nesting of rounded cards, pill containers, and dashboard boxes robs the film of an organic engineering diagram feel.
- Irrelevant decorative background: the middle section (0:07-0:20) places a dark cityscape with lit windows and gear silhouettes behind the prism and molecule, creating visual distraction unrelated to atmospheric physics.
- Abstract dashboard substitute: replacing physical ray scattering with a bar chart and mathematical formula (Rayleigh scattering equation) at 0:17-0:20 diminishes visual clarity and engagement in a short-form video.
- Severe visual clutter and label collisions (0:34-0:38): up to five callout badges crowd around the upper hemisphere of Earth, overlapping continental outlines and glow paths.
- Undersized proof photograph (0:30-0:32): the real NASA ISS photo is cramped inside a small card container surrounded by excessive borders and meta tags, severely muting its impact.
- Broken loop seam (0:45 -> 0:00): the closing frame zooms and blurs into a single card that does not match the opening two-tier layout, creating a noticeable visual jump on loop playback.
- Misleading noon sun angle (0:21): depicts the sun shining horizontally from the side onto an observer labeled 'YOU, AT NOON', visually conflicting with the concept of an overhead midday sun.

| dimension | better | margin | why |
|---|---|---:|---|
| hook | A | 2 | Video A immediately immerses the viewer in a luminous, atmospheric sunset horizon with dynamic blue particles scattering upward from the light beam, instantly posing the visual core of the film. Video B buries the hook in a rigid boxed title container and a tiny inset card over an unrelated dark cityscape background. |
| clarity | A | 2 | Video A explains Rayleigh scattering through tangible physics: ray deflection, particle scattering, and a full dome of blue arrows showering down onto the observer at noon, followed by a tangent beam shedding blue light onto someone else's afternoon while orange/red survives. Video B relies on an abstract dashboard bar chart with a mathematical formula and produces extreme label congestion in the sunset Earth scene. |
| motion_craft | A | 2 | Video A features fluid secondary motion, natural particle dispersion, and smooth scale transitions across atmospheric layers. Video B relies heavily on mechanical UI card slides, progress-bar tweening, and static framing. |
| design_typography | A | 2 | Video A maintains pristine typography, generous negative space, and disciplined hierarchy. Video B suffers from severe UI card nesting, cluttered badges, and overlapping labels (0:34-0:38) that collide with the Earth illustration. |
| concept_wow | A | 2 | Video A delivers two standout visual moments: the noon sky dome raining blue arrows from all directions and the edge-to-edge NASA ISS photograph. Video B trivializes the ISS proof photo by shrinking it inside a nested UI card loaded with redundant metadata badges. |
| style_fidelity | A | 2 | Video A executes a true editorial engineering diagram aesthetic with thematic lighting and atmospheric gradients. Video B introduces an irrelevant dark cityscape with decorative gear outlines throughout the middle scenes, resembling a generic presentation slide deck. |
| finish_texture | A | 2 | Video A displays rich lighting, optical glows, soft gradients, and delicate particle physics. Video B feels flat, cardboard-like, and constrained by heavy container borders. |
| sound_sync | A | 1 | Both audio mixes are solid, but Video A's sound design integrates much better with the physical phenomena (crystalline spray for the noon dome, textured scatter sizzle, rhythmic counter clicks), whereas Video B uses generic UI clicks and whooshes. |
| voice_captions | A | 1 | Both utilize clean, synchronized word-highlight captions, but Video A leaves ample clearance around the caption track whereas Video B crowds the caption area with stacked diagram labels in the third act. |
| loop | A | 3 | Video A executes a flawless, seamless loop where the final callback frame matches the opening frame 00:00 in horizon position, sun glow, and particle flow. Video B attempts a zoom/blur transition into a sunset card that fails to match the opening frame's top-titled layout, resulting in a jarring jump cut. |

Video A is decisively superior across every visual and structural dimension. It delivers a cinematic, atmospheric hook, intuitive physical motion design (especially the noon sky dome and tangent sunset beam), generous presentation of the real ISS proof photo, and a seamless infinite loop back to frame 0. Video B is heavily burdened by a rigid card-based UI aesthetic, unrelated decorative cityscape backgrounds, an abstract bar-chart/formula slide, severe label clutter at sunset, and a broken loop seam.

## General rules (reusable, episode-agnostic)
- **[gate · major · loop]** Always lock the visual state of the final frame to match the first frame exactly to ensure a seamless infinite loop. (evidence B 0:45 vs B 0:00; A 0:45 vs A 0:00)
- **[gate · major · design_typography]** Never place decorative or unrelated background illustrations behind technical explanatory diagrams. (evidence B 0:07 - B 0:20)
- **[gate · major · design_typography]** Never crowd more than three annotation badges simultaneously within the same focal region. (evidence B 0:34 - B 0:38)
- **[component · major · concept_wow]** Always display real-world proof photographic assets at maximum safe-zone width rather than enclosing them in nested card containers. (evidence B 0:30 vs A 0:30)
- **[prose · major · clarity]** Always prioritize animated physical particle or ray behaviors over static formulas and abstract bar charts when explaining dynamic mechanisms. (evidence B 0:18 vs A 0:18)
- **[component · major · hook]** Never obscure the opening hook visual with heavy boxed title containers or multi-layered card frames. (evidence B 0:00 - B 0:03)
