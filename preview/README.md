# Object preview

`preview/` is a camera-free page for tuning what floats above a card: open
`https://willmore-pixel.github.io/AR-card/preview/`, pick a card, and the card lies on a table at an angle
with its object animating above the QR code, the same way the AR page draws it.

- Sliders change the effect (neon color, glow, flicker, light on the card, thickness, upright) and the
  motion (size, hover height, bob, turn time, rest time). Drag the view to orbit, scroll or pinch to zoom.
- "匯出設定" shows the settings as the card's `card.json` `"object"`. Copy it, download a whole
  `card.json`, or copy a link that reopens the preview with the same settings.
- Fields added for the preview, also read by the AR page: `glow`, `flicker`, `spill` (1 = the original
  look), `hover_mm`, `bob_mm` (defaults 10.8 and 2.2 mm), and `size_mm` for cubes.

## Adding a filter

Filters are entries in `FILTERS` in `index.html`: a `label` for the menu, `params` (sliders, colors and
checkboxes, each with a default read from the card's `object`), `build(settings, ctx)` returning a
three.js object, and an optional `tick()` for per-frame effects. The panel, export and link pick a new
entry up on their own; the AR page needs the same effect added before cards can use it.

## Card fronts

The card picture comes from `fronts/<id>.jpg`, falling back to the tracking image. After building a
new card, render its front with `node preview/make_front.js print/<id>/card-front.svg <id>`.
