"""Generate an AR business card front as SVG (mm units, 3 mm bleed) from a card.json config.

Usage: make_card.py cards/<id>/card.json out.svg [--shared-only]

--shared-only leaves out the QR code and the person's text, keeping only what every card
in a group shares. Group tracking (tracks/<group>.mind) is trained on that image so it
matches every member's card equally.
"""
import base64, html, json, math, os, random, re, sys
import segno

CFG = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
URL = CFG["url"]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TRIM_W, TRIM_H, BLEED = 50.8, 88.9, 3.0
W, H = TRIM_W + 2 * BLEED, TRIM_H + 2 * BLEED
X0, Y0 = BLEED, BLEED

# Optional "theme" in card.json restyles the card (a company look); the defaults are the original design.
# Panel and logo boxes are [x, y, w, h] in mm from the trimmed card's top-left corner.
THEME = {
    "bg": "#F4EEDF", "ink": "#1F2A2E", "palette": ["#2F7F7A", "#B5473A", "#D9A441", "#5E7F3A", "#1F2A2E"],
    "kinds": ["circle", "ring", "tri", "square", "bar", "half", "plus"], "count": 260,
    "panel": [3.5, 56.0, 43.8, 29.4], "plate_stroke": None, "panel_stroke": None,
    "font": "Inter, 'Helvetica Neue', Arial, sans-serif", "name_font": None,
    "name_size": 5, "name_weight": 700, "title_color": "#2F7F7A", "rule_color": "#B5473A",
    "name_y": 8.2, "title_y": 12.6, "rule_y": 15.4, "lines_y": 19.6, "line_step": 3.4, "line_size": 2.3,
    "logo": None, "scale": 1,
}
THEME.update(CFG.get("theme", {}))
BG, INK, PALETTE, KINDS = THEME["bg"], THEME["ink"], THEME["palette"], THEME["kinds"]

# QR placement (centered, near top as in the sketch)
QR_SIZE = 24.0
qr_x = X0 + (TRIM_W - QR_SIZE) / 2
qr_y = Y0 + 10.0
PLATE_PAD = 3.0
plate = (qr_x - PLATE_PAD, qr_y - PLATE_PAD, QR_SIZE + 2 * PLATE_PAD, QR_SIZE + 2 * PLATE_PAD + 4.5)

# Lower text panel, and an optional logo area kept clear of confetti
PANEL = (X0 + THEME["panel"][0], Y0 + THEME["panel"][1], THEME["panel"][2], THEME["panel"][3])
LOGO = None
if THEME["logo"]:
    lx, ly, lw, lh = THEME["logo"]["box"]
    LOGO = (X0 + lx, Y0 + ly, lw, lh)

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
    # Tailoring motifs for the Pacewing theme
    if kind == "button":
        r, h = s / 2, s * 0.09
        holes = "".join(f'<circle cx="{dx:.2f}" cy="{dy:.2f}" r="{h:.2f}" fill="{BG}"/>'
                        for dx, dy in ((-s*0.14, -s*0.14), (s*0.14, -s*0.14), (-s*0.14, s*0.14), (s*0.14, s*0.14)))
        return f'<g {t}><circle r="{r:.2f}" fill="{color}"/>{holes}</g>'
    if kind == "stitch":
        return (f'<line {t} x1="{-s/2:.2f}" y1="0" x2="{s/2:.2f}" y2="0" stroke="{color}" stroke-width="{max(0.25, s*0.09):.2f}" '
                f'stroke-dasharray="{s*0.16:.2f} {s*0.1:.2f}" stroke-linecap="round"/>')
    if kind == "cross":
        a, w = s * 0.4, max(0.25, s * 0.12)
        return (f'<path {t} d="M{-a:.2f},{-a:.2f}L{a:.2f},{a:.2f}M{a:.2f},{-a:.2f}L{-a:.2f},{a:.2f}" stroke="{color}" '
                f'stroke-width="{w:.2f}" stroke-linecap="round"/>')
    if kind == "needle":
        l, w = s * 0.75, s * 0.07
        return (f'<g {t}><path d="M{-l:.2f},0 L{l*0.7:.2f},{-w:.2f} Q{l:.2f},0 {l*0.7:.2f},{w:.2f} Z" fill="{color}"/>'
                f'<ellipse cx="{l*0.62:.2f}" cy="0" rx="{s*0.08:.2f}" ry="{w*0.45:.2f}" fill="{BG}"/></g>')
    # Baby motifs
    if kind == "heart":
        r = s / 2
        return (f'<path {t} d="M0,{r*0.75:.2f} C{-r*1.1:.2f},{-r*0.05:.2f} {-r*0.6:.2f},{-r*0.95:.2f} 0,{-r*0.4:.2f} '
                f'C{r*0.6:.2f},{-r*0.95:.2f} {r*1.1:.2f},{-r*0.05:.2f} 0,{r*0.75:.2f} Z" fill="{color}"/>')
    if kind == "star":
        pts = " ".join(f"{(s/2 if i % 2 == 0 else s/4.6)*math.sin(i*math.pi/5):.2f},{-(s/2 if i % 2 == 0 else s/4.6)*math.cos(i*math.pi/5):.2f}"
                       for i in range(10))
        return f'<polygon {t} points="{pts}" fill="{color}" stroke="{color}" stroke-width="{s*0.06:.2f}" stroke-linejoin="round"/>'
    if kind == "bottle":
        w, h = s * 0.42, s * 0.62
        return (f'<g {t}><rect x="{-w/2:.2f}" y="{-h*0.35:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{w*0.3:.2f}" fill="{color}"/>'
                f'<rect x="{-w*0.6:.2f}" y="{-h*0.5:.2f}" width="{w*1.2:.2f}" height="{h*0.18:.2f}" rx="{h*0.05:.2f}" fill="{color}"/>'
                f'<path d="M{-w*0.3:.2f},{-h*0.5:.2f} Q0,{-h*1.05:.2f} {w*0.3:.2f},{-h*0.5:.2f} Z" fill="{color}"/>'
                f'<rect x="{-w*0.28:.2f}" y="{-h*0.1:.2f}" width="{w*0.56:.2f}" height="{h*0.07:.2f}" fill="{BG}"/>'
                f'<rect x="{-w*0.28:.2f}" y="{h*0.12:.2f}" width="{w*0.56:.2f}" height="{h*0.07:.2f}" fill="{BG}"/></g>')
    if kind == "rattle":
        r = s * 0.26
        return (f'<g {t}><circle cx="0" cy="{-s*0.22:.2f}" r="{r:.2f}" fill="{color}"/>'
                f'<circle cx="0" cy="{-s*0.22:.2f}" r="{r*0.38:.2f}" fill="{BG}"/>'
                f'<rect x="{-s*0.06:.2f}" y="{-s*0.02:.2f}" width="{s*0.12:.2f}" height="{s*0.4:.2f}" fill="{color}"/>'
                f'<circle cx="0" cy="{s*0.42:.2f}" r="{s*0.1:.2f}" fill="{color}"/></g>')
    if kind == "pacifier":
        return (f'<g {t}><circle cx="0" cy="{-s*0.28:.2f}" r="{s*0.16:.2f}" fill="none" stroke="{color}" stroke-width="{s*0.08:.2f}"/>'
                f'<ellipse cx="0" cy="{s*0.02:.2f}" rx="{s*0.42:.2f}" ry="{s*0.14:.2f}" fill="{color}"/>'
                f'<ellipse cx="0" cy="{s*0.25:.2f}" rx="{s*0.13:.2f}" ry="{s*0.18:.2f}" fill="{color}"/></g>')
    # Floral motifs
    if kind == "flower":
        r = s / 2
        petals = "".join(f'<ellipse cx="0" cy="{-r*0.5:.2f}" rx="{r*0.33:.2f}" ry="{r*0.5:.2f}" transform="rotate({a})" fill="{color}"/>'
                         for a in range(0, 360, 72))
        return f'<g {t}>{petals}<circle r="{r*0.2:.2f}" fill="{BG}"/></g>'
    if kind == "leaf":
        r = s / 2
        return (f'<g {t}><path d="M{-r:.2f},0 Q0,{-r*0.75:.2f} {r:.2f},0 Q0,{r*0.75:.2f} {-r:.2f},0 Z" fill="{color}"/>'
                f'<path d="M{-r*0.8:.2f},0 L{r*0.75:.2f},0" stroke="{BG}" stroke-width="{s*0.04:.2f}"/></g>')
    if kind == "plus":
        a, b = s * 0.5, s * 0.14
        return (f'<path {t} d="M{-a:.2f},{-b:.2f}H{a:.2f}V{b:.2f}H{-a:.2f}Z M{-b:.2f},{-a:.2f}H{b:.2f}V{a:.2f}H{-b:.2f}Z" '
                f'fill="{color}"/>')
    raise ValueError(kind)



# Scatter non-repeating confetti with rejection sampling: irregular, high-contrast
# features give image trackers (MindAR) many distinct keypoints to lock onto.
placed = []
shapes = []
tries = 0
while len(shapes) < THEME["count"] and tries < 60000:
    tries += 1
    x, y = rng.uniform(0, W), rng.uniform(0, H)
    if inside(plate, x, y, 1.6) or inside(PANEL, x, y, 1.2) or (LOGO and inside(LOGO, x, y, 1.0)):
        continue
    s = rng.choice([rng.uniform(1.0, 2.2), rng.uniform(2.0, 3.6), rng.uniform(3.4, 5.2)]) * THEME["scale"]
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
T = THEME
contact_lines = "\n".join(
    f'    <text x="{X0 + TRIM_W / 2:.2f}" y="{PANEL[1] + T["lines_y"] + T["line_step"] * i:.2f}" font-size="{T["line_size"]}" text-anchor="middle">{esc(line)}</text>'
    for i, line in enumerate(CFG["lines"][:3]))
cx = X0 + TRIM_W / 2
plate_stroke = T["plate_stroke"] or INK
panel_stroke = T["panel_stroke"] or INK
name_font = f' style="font-family:{esc(T["name_font"])}"' if T["name_font"] else ""
logo_svg = ""
if LOGO:
    data = base64.b64encode(open(os.path.join(ROOT, T["logo"]["src"]), "rb").read()).decode()
    logo_svg = (f'\n  <!-- Company logo (shared by every card in the group) -->\n'
                f'  <image id="logo" x="{LOGO[0]:.2f}" y="{LOGO[1]:.2f}" width="{LOGO[2]:.2f}" height="{LOGO[3]:.2f}" '
                f'preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{data}"/>\n')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">
  <title>AR business card front (portrait 2 x 3.5 in, 3 mm bleed)</title>
  <style>
    text {{ font-family: {T["font"]}; fill: {INK}; }}
  </style>
  <!-- Background (extends into bleed) -->
  <rect id="background" width="{W}" height="{H}" fill="{BG}"/>

  <!-- Tracking artwork: seeded random confetti, keeps the card unique for image tracking -->
  <g id="tracking-pattern">
    {chr(10).join('    ' + s for s in shapes)}
  </g>
{logo_svg}
  <!-- QR plate: the AR cube will stand on the QR code -->
  <g id="qr-plate">
    <rect x="{px:.2f}" y="{py:.2f}" width="{pw:.2f}" height="{ph:.2f}" rx="1.6" fill="#FFFFFF" stroke="{plate_stroke}" stroke-width="0.5"/>
    <path id="qr-code" d="{''.join(d)}" fill="{INK}"/>
    <text x="{cx:.2f}" y="{qr_y + QR_SIZE + 4.3:.2f}" font-size="2.2" font-weight="600" text-anchor="middle" letter-spacing="0.35">SCAN FOR AR</text>
  </g>

  <!-- Contact panel (text comes from card.json) -->
  <g id="contact-panel">
    <rect x="{PANEL[0]:.2f}" y="{PANEL[1]:.2f}" width="{PANEL[2]:.2f}" height="{PANEL[3]:.2f}" rx="1.6" fill="#FFFFFF" stroke="{panel_stroke}" stroke-width="0.5"/>
    <text x="{cx:.2f}" y="{PANEL[1] + T["name_y"]:.2f}" font-size="{T["name_size"]}" font-weight="{T["name_weight"]}" text-anchor="middle"{name_font}>{esc(CFG["name"])}</text>
    <text x="{cx:.2f}" y="{PANEL[1] + T["title_y"]:.2f}" font-size="2.6" font-weight="500" text-anchor="middle" fill="{T["title_color"]}" style="fill:{T["title_color"]}">{esc(CFG["title"])}</text>
    <line x1="{cx-8:.2f}" y1="{PANEL[1]+T["rule_y"]:.2f}" x2="{cx+8:.2f}" y2="{PANEL[1]+T["rule_y"]:.2f}" stroke="{T["rule_color"]}" stroke-width="0.4"/>
{contact_lines}
  </g>
</svg>
'''
if "--shared-only" in sys.argv:
    svg = re.sub(r'\s*<path id="qr-code"[^>]*/>', "", svg)
    panel = svg[svg.index('<g id="contact-panel">'):]
    svg = svg.replace(panel, re.sub(r'\s*<text [^>]*>[^<]*</text>', "", panel))
open(OUT, "w").write(svg)
print("modules", n, "module mm", round(mod, 3), "shapes", len(shapes))
