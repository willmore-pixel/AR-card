"""Build everything for one person's card from cards/<id>/card.json.

Usage (from the repo root): python3 tools/build_card.py <id> [print-output-dir] [--retrain]

Writes cards/<id>/target.png and cards/<id>/card.mind (served by the AR page) and the
print files (SVG, 600 dpi PNG, PDF with 3 mm bleed, preview) to the output dir.
Needs: python segno + Pillow, node with playwright, Chromium.
"""
import functools, http.server, json, os, subprocess, sys, threading
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
card_id = sys.argv[1]
args = [a for a in sys.argv[2:] if not a.startswith("--")]
out = os.path.abspath(args[0] if args else os.path.join(ROOT, "print", card_id))
card_dir = os.path.join(ROOT, "cards", card_id)
os.makedirs(out, exist_ok=True)
env = dict(os.environ, NODE_PATH=os.environ.get("NODE_PATH") or subprocess.check_output(["npm", "root", "-g"], text=True).strip())

svg = os.path.join(out, "card-front.svg")
subprocess.check_call([sys.executable, os.path.join(ROOT, "tools/make_card.py"), os.path.join(card_dir, "card.json"), svg])
subprocess.check_call(["node", os.path.join(ROOT, "tools/render.js"), svg, out], env=env)

png = os.path.join(out, "card-front-print-600dpi.png")
Image.open(png).convert("RGB").save(os.path.join(out, "card-front-print.pdf"), resolution=600)


def save_target(print_png, dest):
    im = Image.open(print_png).convert("RGB")
    mm = 600 / 25.4
    b = round(3 * mm)
    trim = im.crop((b, b, b + round(50.8 * mm), b + round(88.9 * mm)))
    trim.resize((600, 1050), Image.LANCZOS).save(dest)


# Cards with "track": "<group>" share one tracking file trained on the group's common design
# (no QR, no personal text), so one company pattern works for everyone in the group.
group = json.load(open(os.path.join(card_dir, "card.json"))).get("track")
if group:
    track_dir = os.path.join(ROOT, "tracks")
    os.makedirs(track_dir, exist_ok=True)
    target_rel, mind_out = f"tracks/{group}.png", os.path.join(track_dir, f"{group}.mind")
    if os.path.exists(mind_out) and "--retrain" not in sys.argv:
        target_rel = None
    else:
        shared_dir = os.path.join(out, "shared")
        os.makedirs(shared_dir, exist_ok=True)
        shared_svg = os.path.join(shared_dir, "shared.svg")
        subprocess.check_call([sys.executable, os.path.join(ROOT, "tools/make_card.py"),
                               os.path.join(card_dir, "card.json"), shared_svg, "--shared-only"])
        subprocess.check_call(["node", os.path.join(ROOT, "tools/render.js"), shared_svg, shared_dir], env=env)
        save_target(os.path.join(shared_dir, "card-front-print-600dpi.png"), os.path.join(ROOT, target_rel))
else:
    target_rel, mind_out = f"cards/{card_id}/target.png", os.path.join(card_dir, "card.mind")
    save_target(png, os.path.join(ROOT, target_rel))

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
handler.log_message = lambda *a: None
server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
try:
    if target_rel:
        subprocess.check_call(["node", os.path.join(ROOT, "tools/compile_target.js"),
                               f"http://127.0.0.1:{server.server_port}", target_rel, mind_out], env=env)
finally:
    server.shutdown()
print(f"built {card_id}: tracking {mind_out}{' (reused)' if not target_rel else ''}, print files in {out}")
