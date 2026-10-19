"""Generate an AR business card front as SVG (mm units, 3 mm bleed) from a card.json config.

Usage: make_card.py cards/<id>/card.json out.svg
"""
import html, json, math, random, sys
import segno

CFG = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
URL = CFG["url"]

TRIM_W, TRIM_H, BLEED = 50.8, 88.9, 3.0
W, H = TRIM_W + 2 * BLEED, TRIM_H + 2 * BLEED
X0, Y0 = BLEED, BLEED

BG = "#F4EEDF"
INK = "#1F2A2E"
PALETTE = ["#2F7F7A", "#B5473A", "#D9A441", "#5E7F3A", INK]

# QR placement (centered, near top as in the sketch)
QR_SIZE = 24.0
qr_x = X0 + (TRIM_W - QR_SIZE) / 2
qr_y = Y0 + 10.0
PLATE_PAD = 3.0
plate = (qr_x - PLATE_PAD, qr_y - PLATE_PAD, QR_SIZE + 2 * PLATE_PAD, QR_SIZE + 2 * PLATE_PAD + 4.5)

# Lower text panel
PANEL = (X0 + 3.5, Y0 + 56.0, TRIM_W - 7.0, 29.4)

# The seed gives each person their own confetti layout, so cards stay distinguishable
rng = random.Random(CFG["seed"])


def inside(r, x, y, m=0.0):
    rx, ry, rw, rh = r
    return rx - m <= x <= rx + rw + m and ry - m <= y <= ry + rh + m


def shape(kind, x, y, s, rot, color):
    t = f'transform="translate({x:.2f} {y:.2f}) rotate({rot:.1f})"'
    if kind == "circle":
        return f'<circle {t} r="{s/2:.2f}" fill="{color}"/>'
    if kind == "ring":
        return f'<circle {t} r="{s/2*0.8:.2f}" fill="none" stroke="{color}" stroke-width="{s*0.18:.2f}"/>'
    if kind == "tri":
        h = s * 0.87
        return f'<polygon {t} points="0,{-h*0.6:.2f} {s/2:.2f},{h*0.4:.2f} {-s/2:.2f},{h*0.4:.2f}" fill="{color}"/>'
    if kind == "square":
        return f'<rect {t} x="{-s/2*0.8:.2f}" y="{-s/2*0.8:.2f}" width="{s*0.8:.2f}" height="{s*0.8:.2f}" fill="{color}"/>'
    if kind == "bar":
        return f'<rect {t} x="{-s/2:.2f}" y="{-s*0.11:.2f}" width="{s:.2f}" height="{s*0.22:.2f}" rx="{s*0.11:.2f}" fill="{color}"/>'
    if kind == "half":
        r = s / 2
        return f'<path {t} d="M{-r:.2f},0 A{r:.2f},{r:.2f} 0 0 1 {r:.2f},0 Z" fill="{color}"/>'
    if kind == "plus":
        a, b = s * 0.5, s * 0.14
        return (f'<path {t} d="M{-a:.2f},{-b:.2f}H{a:.2f}V{b:.2f}H{-a:.2f}Z M{-b:.2f},{-a:.2f}H{b:.2f}V{a:.2f}H{-b:.2f}Z" '
                f'fill="{color}"/>')
    raise ValueError(kind)


KINDS = ["circle", "ring", "tri", "square", "bar", "half", "plus"]

# Scatter non-repeating confetti with rejection sampling: irregular, high-contrast
# features give image trackers (MindAR) many distinct keypoints to lock onto.
placed = []
shapes = []
tries = 0
while len(shapes) < 260 and tries < 60000:
    tries += 1
    x, y = rng.uniform(0, W), rng.uniform(0, H)
    if inside(plate, x, y, 1.6) or inside(PANEL, x, y, 1.2):
        continue
    s = rng.choice([rng.uniform(1.0, 2.2), rng.uniform(2.0, 3.6), rng.uniform(3.4, 5.2)])
    if any(math.hypot(x - px, y - py) < (s + ps) / 2 + 0.7 for px, py, ps in placed):
        continue
    placed.append((x, y, s))
    shapes.append(shape(rng.choice(KINDS), x, y, s, rng.uniform(0, 360), rng.choice(PALETTE)))

# QR modules as one path
qr = segno.make(URL, error="h", micro=False)
matrix = list(qr.matrix)
n = len(matrix)
mod = QR_SIZE / n
d = []
for r, row in enumerate(matrix):
    for c, v in enumerate(row):
        if v:
            d.append(f"M{qr_x + c*mod:.3f},{qr_y + r*mod:.3f}h{mod:.3f}v{mod:.3f}h{-mod:.3f}z")

px, py, pw, ph = plate
esc = html.escape
contact_lines = "\n".join(
    f'    <text x="{X0 + TRIM_W / 2:.2f}" y="{PANEL[1] + 19.6 + 3.4 * i:.2f}" font-size="2.3" text-anchor="middle">{esc(line)}</text>'
    for i, line in enumerate(CFG["lines"][:3]))
cx = X0 + TRIM_W / 2
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">
  <title>AR business card front (portrait 2 x 3.5 in, 3 mm bleed)</title>
  <style>
    text {{ font-family: Inter, 'Helvetica Neue', Arial, sans-serif; fill: {INK}; }}
  </style>
  <!-- Background (extends into bleed) -->
  <rect id="background" width="{W}" height="{H}" fill="{BG}"/>

  <!-- Tracking artwork: seeded random confetti, keeps the card unique for image tracking -->
  <g id="tracking-pattern">
    {chr(10).join('    ' + s for s in shapes)}
  </g>

  <!-- QR plate: the AR cube will stand on the QR code -->
  <g id="qr-plate">
    <rect x="{px:.2f}" y="{py:.2f}" width="{pw:.2f}" height="{ph:.2f}" rx="1.6" fill="#FFFFFF" stroke="{INK}" stroke-width="0.5"/>
    <path id="qr-code" d="{''.join(d)}" fill="{INK}"/>
    <text x="{cx:.2f}" y="{qr_y + QR_SIZE + 4.3:.2f}" font-size="2.2" font-weight="600" text-anchor="middle" letter-spacing="0.35">SCAN FOR AR</text>
  </g>

  <!-- Contact panel (text comes from card.json) -->
  <g id="contact-panel">
    <rect x="{PANEL[0]:.2f}" y="{PANEL[1]:.2f}" width="{PANEL[2]:.2f}" height="{PANEL[3]:.2f}" rx="1.6" fill="#FFFFFF" stroke="{INK}" stroke-width="0.5"/>
    <text x="{cx:.2f}" y="{PANEL[1] + 8.2:.2f}" font-size="5" font-weight="700" text-anchor="middle">{esc(CFG["name"])}</text>
    <text x="{cx:.2f}" y="{PANEL[1] + 12.6:.2f}" font-size="2.6" font-weight="500" text-anchor="middle" fill="#2F7F7A" style="fill:#2F7F7A">{esc(CFG["title"])}</text>
    <line x1="{cx-8:.2f}" y1="{PANEL[1]+15.4:.2f}" x2="{cx+8:.2f}" y2="{PANEL[1]+15.4:.2f}" stroke="#B5473A" stroke-width="0.4"/>
{contact_lines}
  </g>
</svg>
'''
open(OUT, "w").write(svg)
print("modules", n, "module mm", round(mod, 3), "shapes", len(shapes))
