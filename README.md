# AR business cards

Point a phone at a printed card and a cube floats above its QR code, following the card as it moves.

One shared page serves every card. Each card's QR code links to `https://willmore-pixel.github.io/AR-card/?card=<id>`, and the page loads that card's tracking data and cube colors from `cards/<id>/`. The bare link (no `?card=`) opens willmore's card.

## Add a card for someone

1. Create `cards/<id>/card.json` (lowercase id, letters, digits and dashes), copying `cards/willmore/card.json`. Give it a new `seed` so the confetti pattern is unique, set `url` to `.../AR-card/?card=<id>`, and fill in the name, title, contact lines and cube colors.
2. Run `python3 tools/build_card.py <id>`. It writes `cards/<id>/card.mind` and `target.png` for the page, and print files (SVG, 600 dpi PNG, PDF with 3 mm bleed, preview) to `print/<id>/`.
3. Commit `cards/<id>/` and push.

## Cards that share one design (a company pattern)

Give every member's `card.json` the same `seed` and the same `"track": "<group>"`, and their own `url` and `cube` colors. The first build trains `tracks/<group>.mind` on the shared design only (QR code and personal text left out), and later builds reuse it, so add `--retrain` after changing the shared design. Each person's QR link picks their own cube. The page follows whichever group card it sees, so Sam's link pointed at a colleague's card still shows Sam's cube.

Commit `cards/<id>/` (and `tracks/` for a new group) and push.

The build needs Python with `segno` and Pillow, plus Node with Playwright and Chromium. MindAR 1.2.5 and three.js 0.160 are vendored under `vendor/`, so the page has no CDN dependency.
