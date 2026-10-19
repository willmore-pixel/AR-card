"""Build everything for one person's card from cards/<id>/card.json.

Usage (from the repo root): python3 tools/build_card.py <id> [print-output-dir]

Writes cards/<id>/target.png and cards/<id>/card.mind (served by the AR page) and the
print files (SVG, 600 dpi PNG, PDF with 3 mm bleed, preview) to the output dir.
Needs: python segno + Pillow, node with playwright, Chromium.
"""
import functools, http.server, os, subprocess, sys, threading
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
card_id = sys.argv[1]
out = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "print", card_id))
card_dir = os.path.join(ROOT, "cards", card_id)
os.makedirs(out, exist_ok=True)
env = dict(os.environ, NODE_PATH=os.environ.get("NODE_PATH") or subprocess.check_output(["npm", "root", "-g"], text=True).strip())

svg = os.path.join(out, "card-front.svg")
subprocess.check_call([sys.executable, os.path.join(ROOT, "tools/make_card.py"), os.path.join(card_dir, "card.json"), svg])
subprocess.check_call(["node", os.path.join(ROOT, "tools/render.js"), svg, out], env=env)

png = os.path.join(out, "card-front-print-600dpi.png")
im = Image.open(png).convert("RGB")
im.save(os.path.join(out, "card-front-print.pdf"), resolution=600)
mm = 600 / 25.4
b = round(3 * mm)
trim = im.crop((b, b, b + round(50.8 * mm), b + round(88.9 * mm)))
trim.resize((600, 1050), Image.LANCZOS).save(os.path.join(card_dir, "target.png"))

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
handler.log_message = lambda *a: None
server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
try:
    subprocess.check_call(["node", os.path.join(ROOT, "tools/compile_target.js"),
                           f"http://127.0.0.1:{server.server_port}", f"cards/{card_id}/target.png",
                           os.path.join(card_dir, "card.mind")], env=env)
finally:
    server.shutdown()
print(f"built {card_id}: tracking in {card_dir}, print files in {out}")
