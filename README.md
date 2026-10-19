# AR business cards

Point a phone at a printed card and a cube floats above its QR code, following the card as it moves.

One shared page serves every card. Each card's QR code links to `https://willmore-pixel.github.io/AR-card/?card=<id>`, and the page loads that card's tracking data and cube colors from `cards/<id>/`. The bare link (no `?card=`) opens willmore's card.

## Add a card for someone

1. Create `cards/<id>/card.json` (lowercase id, letters, digits and dashes), copying `cards/willmore/card.json`. Give it a new `seed` so the confetti pattern is unique, set `url` to `.../AR-card/?card=<id>`, and fill in the name, title, contact lines and cube colors.
2. Run `python3 tools/build_card.py <id>`. It writes `cards/<id>/card.mind` and `target.png` for the page, and print files (SVG, 600 dpi PNG, PDF with 3 mm bleed, preview) to `print/<id>/`.
3. Commit `cards/<id>/` and push.

The build needs Python with `segno` and Pillow, plus Node with Playwright and Chromium. MindAR 1.2.5 and three.js 0.160 are vendored under `vendor/`, so the page has no CDN dependency.
