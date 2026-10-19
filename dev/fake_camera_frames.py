# Make fake camera frames: the card on a wood-ish table, tilting and turning.
import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
card = Image.open('/mnt/project-files/ar-page/target.png').convert('RGB')
W, H = 720, 1280
cw, ch = card.size
def solve(src, dst):
    A = []; B = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u*x, -u*y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v*x, -v*y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float))
rng = np.random.default_rng(1)
bg = Image.fromarray((np.clip(rng.normal(0, 12, (H, W, 1)) + [120, 62, 35], 0, 255)).astype('uint8')).filter(ImageFilter.GaussianBlur(1.5))
N = 180
for i in range(N):
    t = i / N * 2 * math.pi
    yaw = 0.6 * math.sin(t); tilt = 0.45 + 0.2 * math.cos(t)
    f, d = 1100.0, 6.0
    corners = []
    for (x, y) in [(-1, -1.75), (1, -1.75), (1, 1.75), (-1, 1.75)]:
        xr = x*math.cos(yaw) - y*math.sin(yaw); yr = x*math.sin(yaw) + y*math.cos(yaw)
        Y = yr*math.cos(tilt); Z = d + yr*math.sin(tilt)
        corners.append((W/2 + f*xr/Z, H/2 + f*Y/Z))
    src = [(0, 0), (cw, 0), (cw, ch), (0, ch)]
    coef = solve(corners, src)
    warped = card.transform((W, H), Image.PERSPECTIVE, tuple(coef), Image.BICUBIC)
    mask = Image.new('L', (W, H), 0); ImageDraw.Draw(mask).polygon(corners, fill=255)
    frame = bg.copy(); frame.paste(warped, (0, 0), mask)
    frame.save(f'/root/ar/test/frames/f{i:03d}.png')
