# AR business card

Point a phone at the printed card and a cube appears standing on the QR code, following the card as it moves.

- `index.html` is the AR page (MindAR image tracking + three.js, vendored under `vendor/` so it has no CDN dependency).
- `card.mind` is the tracking data compiled from `target.png` (the trimmed card front). Recompile it with `dev/compile_target.js` whenever the card artwork changes.
- `dev/` holds the compile script and a simulated-camera test.

Served with GitHub Pages at https://willmore-pixel.github.io/AR-card/
