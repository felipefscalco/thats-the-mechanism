# Pairwise critic — Sky (ship)

- A: `/workspace/ttm-r7/renders/Sky_v5.mp4`
- B: `/workspace/ttm-r7/renders/Sky_v7.mp4`
- Model: `gemini-3.8-flash-high` · free tier $0
- **Preferred: B** (strength 3/3, confidence high); weighted margin B−A = +2.06

## Weaknesses A
- Relies on boxed, dark UI card containers and generic city silhouettes instead of an immersive natural atmosphere (0:00).
- Explains Rayleigh scattering with an abstract bar chart rather than showing the physical mechanism of photon scattering (0:18).
- Confines the real ISS proof photo inside a small, framed card with distracting dashed borders (0:32).
- Uses rigid, spiky geometric starburst lines to depict molecular scattering rather than fluid wave/particle behavior (0:14).
- Awkward zoom-in on the bottom card creates an abrupt and jarring loop seam at the loop transition (0:46).

## Weaknesses B
- NASA attribution metadata text at 0:32 has slightly low contrast against the dark curve of the ISS horizon.
- The secondary badge 'SOMEONE ELSE'S AFTERNOON' at 0:35 experiences brief contrast dips as animated glowing particles pass behind and across it.
- Upper HUD text in the opening hook (0:00) is slightly dense near the top safe margin.

| dimension | better | margin | why |
|---|---|---:|---|
| hook | B | 3 | Video B opens with a full-bleed, radiant sunset horizon with glowing particle scattering at frame 0, instantly immersing the viewer in the phenomenon, whereas Video A starts in a cramped, dark UI card with a generic city silhouette. |
| clarity | B | 2 | Video B replaces Video A's abstract bar chart at 0:18 with a brilliant physical collision demonstration showing blue light actively scattering four times more than red across a molecule field, dramatically improving sound-off comprehension. |
| motion_craft | B | 2 | Video B features fluid wave propagation, organic radial scattering ripples, and smooth camera pacing, whereas Video A uses rigid starburst spikes and mechanical card movements. |
| design_typography | B | 2 | Video B abandons dark UI containers for expansive atmospheric gradients, cleaner typographic breathing room, and intentional color design. |
| concept_wow | B | 3 | The photon-molecule collision chamber at 0:18 and the edge-to-edge ISS limb photograph at 0:32 in Video B deliver genuine visual awe, whereas Video A treats these moments like clinical slide deck widgets. |
| style_fidelity | B | 2 | Video B captures the quintessential editorial science look with atmospheric warmth and mechanical precision, whereas Video A relies too heavily on generic dark-mode app UI patterns. |
| finish_texture | B | 2 | Video B incorporates beautiful luminous solar glows, soft particle dispersion, and rich photographic fidelity, avoiding the flat vector aesthetic of Video A. |
| sound_sync | B | 1 | Both have crisp mix-minus voiceover and solid sound design, but Video B provides tighter audio accents for particle impacts and dispersion beats. |
| voice_captions | tie | 0 | Both versions share identical narration audio and word-level synchronized captions with clear legibility in the designated safe zone. |
| loop | B | 3 | Video B perfectly matches the framing, glowing sun position, and scattering particles between the final callback and frame 0 for an invisible loop, whereas Video A has an awkward zoom-in on a card with a jarring seam. |

Video B is a comprehensive, night-and-day leap forward in visual storytelling and motion design. It replaces Video A's dark, boxed UI cards and abstract bar charts with an expansive, immersive atmosphere, a brilliant physical photon-collision simulation to explain Rayleigh scattering, a full-bleed ISS proof photograph, and a seamless loop back to the opening hook.

## General rules (reusable, episode-agnostic)
- **[component · major · hook]** Never confine the opening hook to a dark boxed card when an immersive, full-stage environment can establish the visual premise instantly. (evidence A 0:00 vs B 0:00)
- **[prose · major · clarity]** Always visualize comparative ratios with active physical demonstrations rather than abstract UI bar charts. (evidence A 0:18 vs B 0:18)
- **[gate · blocker · loop]** Always match the exact camera position, background elements, and focal subject between the loop-out shot and frame zero to achieve a seamless loop. (evidence A 0:46 vs B 0:46)
- **[component · major · finish_texture]** Never box real-world proof photos inside nested card containers when full-bleed presentation provides higher immersion and scale. (evidence A 0:32 vs B 0:32)
- **[prose · major · motion_craft]** Always represent wave and particle interactions with continuous secondary motion and dynamic bursts rather than static geometric starbursts. (evidence A 0:14 vs B 0:14)
- **[gate · minor · design_typography]** Always maintain adequate contrast between secondary explanatory badges and underlying animated trajectories or backgrounds. (evidence B 0:35)
