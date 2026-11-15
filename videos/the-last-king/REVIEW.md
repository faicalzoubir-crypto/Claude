# The Last King: review

Delivery: `livrables/the-last-king.mp4`, 1080 x 1920 (9:16), 24 fps, 1440 frames, 60.0 s, H.264,
no audio track (silent on purpose), 90.5 MB.

## Creative calls

- **Painted, not AI-generated.** The HeyGen sign-in never completed (three device codes expired), and
  the person chose the procedural fallback ("Do it"). Every shot is painted in code
  (`tools/paint/`): a soft underpainting per frame, turned into wet oil by strokes that follow the
  image's own forms, a bristle texture locked to the camera that boils slowly, and a faint canvas
  weave. Any shot can still be swapped for an AI shot of the same length at
  `assets/shots/<id>.mp4` (prompts ready in `tools/shots.json`); then run
  `python3 tools/build.py transitions` and render again.
- **Look from the person's reference clip** (its grammar only): pools of light in pure black, smooth
  curved strokes, faceless figures, cream-yellow / bone / dusty blue-grey / periwinkle / umber, one
  small red. Red appears as the gem on the crown, the candle's core, and the flag in scene 5.
- **Vertical recomposition** (the person switched from 16:9): one subject per frame, the action
  between 168 and 1330 px from the top, frame 0 is the king on the balcony.
- **Scene 5's "puppet on a thread"** is a jointed wooden marionette of the king with splayed limbs,
  so the cut thread drops a puppet, not a person.
- **Dissolves**: five swirling brushstroke dissolves between scenes (1.6 s, baked per seam by
  `tools/brush_transition.py`), nine shorter paint melts inside scenes, and a gold-to-blue drain in
  scene 1. Fade to black from 57.4 s, black from 59.2 s.

## Measured

- `hyperframes check`: ok, 0 errors; lint 0 errors, 0 warnings.
- The render: 1440 frames, 60.000 s, 24/1 fps, one video stream, no audio stream.
- Seams: frame-to-frame difference measured at all 28 dissolve boundaries in the rendered file;
  all within the film's normal motion (median 0.9 on 255), and no duplicated frame anywhere after
  the dissolves were rounded up to whole frames.
- Source windows: every shot covers its on-screen time plus both dissolve handles
  (`python3 tools/build.py check`).

## Only looked at

- The spec's check frames, the beat and seam sheets from `snapshot --review`, and contact sheets of
  each shot. Nobody has watched it at full speed on a phone yet. There is no sound to judge.

## Weakest shots, and what more time would change

- **2a (raised arms)**: the arms read, but as rather stiff stalks; real AI footage or hand-drawn arm
  poses would sell "a crowd lifting a crown" better.
- **1b (the cell)**: the seated king reads as a cloak-shaped block; the stone wall is too regular.
- **4b (horsemen)**: ghostly and readable up close, small on a phone.
- In general, figures are simple shapes; that suits the reference's few-stroke figures, but AI
  footage would give richer acting.

## Warnings kept on purpose

- `film_silent`: the person asked for no music, voice or sound.
