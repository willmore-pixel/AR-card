# AR business cards

Point a phone at a printed card and a cube floats above its QR code, following the card as it moves.

One shared page serves every card. Each card's QR code links to `https://willmore-pixel.github.io/AR-card/?card=<id>`, and the page loads that card's tracking data and cube colors from `cards/<id>/`. The bare link (no `?card=`) opens willmore's card.

## Add a card for someone

1. Create `cards/<id>/card.json` (lowercase id, letters, digits and dashes), copying `cards/willmore/card.json`. Give it a new `seed` so the confetti pattern is unique, set `url` to `.../AR-card/?card=<id>`, and fill in the name, title, contact lines and cube colors.
2. Run `python3 tools/build_card.py <id>`. It writes `cards/<id>/card.mind` and `target.png` for the page, and print files (SVG, 600 dpi PNG, PDF with 3 mm bleed, preview) to `print/<id>/`.
3. Commit `cards/<id>/` and push.

## Company looks

An optional `"theme"` in `card.json` restyles the card: background, confetti colors and shapes (including tailoring motifs `button`, `stitch`, `cross`, `needle` and baby motifs `heart`, `star`, `bottle`, `rattle`, `pacifier`, floral `flower`, `leaf`; `scale` enlarges them), panel position, fonts, and a logo image kept clear of confetti. `"edge"` sets the cube's edge color. `"object": {"type": "neon", "src": "<svg or png>", "color": "#6FE3FF", "size_mm": 26, "spin": {"period": 6.5, "turn": 3}}` replaces the cube with a glowing neon-sign version of an image; `spin` (seconds per cycle and per turn) also works for cubes. Neon signs also take `"upright": true` (stand the drawing up along the spin axis), `"depth_mm"` and `"side"` (thickness and its color), `"glow"`, `"flicker"` and `"spill"` (glow strength, how often it flickers, its light on the card; 1 = default, 0 = off). Any object takes `"hover_mm"` and `"bob_mm"` (default 10.8 and 2.16 mm), and `"size_mm"` also sizes a cube (default 18). A cube can be textured with `"faces": {"top": img, "bottom": img, "sides": [4 imgs]}` (see `cards/huirong-aliang`). The preview tool in `preview/` exports these settings. See `cards/kenny-yen/card.json` (Pacewing Bespoke).

## Cards that share one design (a company pattern)

Give every member's `card.json` the same `seed` and the same `"track": "<group>"`, and their own `url` and `cube` colors. The first build trains `tracks/<group>.mind` on the shared design only (QR code and personal text left out), and later builds reuse it, so add `--retrain` after changing the shared design. Each person's QR link picks their own cube. While running, the page keeps reading the QR code in view (vendored jsQR) and switches to that card's cube, so pointing the phone at a colleague's card shows their cube. A card from another group reloads the page for that card.

Commit `cards/<id>/` (and `tracks/` for a new group) and push.

The build needs Python with `segno` and Pillow, plus Node with Playwright and Chromium. MindAR 1.2.5, three.js 0.160 and jsQR 1.4.0 are vendored under `vendor/`, so the page has no CDN dependency.
