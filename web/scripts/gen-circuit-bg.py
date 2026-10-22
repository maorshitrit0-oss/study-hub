"""Generate a seamless circuit-board SVG tile (orthogonal + 45° traces, pads, chips, glowing nodes)."""
import random, sys

W = H = 640
random.seed(7)
G = 16  # routing grid

def snap(v): return round(v / G) * G

traces, pads, glows = [], [], []
chips = [(96, 112, 128, 96), (400, 320, 144, 112), (208, 448, 80, 64), (480, 64, 96, 80)]

def inside_chip(x, y, m=8):
    return any(cx - m <= x <= cx + w + m and cy - m <= y <= cy + h + m for cx, cy, w, h in chips)

# Pins along chip edges with short leads
for cx, cy, w, h in chips:
    for x in range(cx + 8, cx + w - 4, 12):
        traces.append(f"M{x} {cy}v-10"); traces.append(f"M{x} {cy+h}v10")
    for y in range(cy + 8, cy + h - 4, 12):
        traces.append(f"M{cx} {y}h-10"); traces.append(f"M{cx+w} {y}h10")

# Random routed traces; draw each at offsets so the tile wraps seamlessly
for _ in range(70):
    x, y = snap(random.uniform(0, W)), snap(random.uniform(0, H))
    if inside_chip(x, y): continue
    d = [f"M{x} {y}"]
    for _ in range(random.randint(2, 5)):
        L = snap(random.uniform(32, 160)) or G
        kind = random.random()
        if kind < 0.4: x += random.choice((-1, 1)) * L; d.append(f"H{x}")
        elif kind < 0.8: y += random.choice((-1, 1)) * L; d.append(f"V{y}")
        else:
            sx, sy = random.choice((-1, 1)), random.choice((-1, 1)); s = L // 2
            x += sx * s; y += sy * s; d.append(f"L{x} {y}")
    traces.append("".join(d)); pads.append((x, y))
    if random.random() < 0.35: glows.append((x, y))

def wrap(path_or_pt, fn):
    return [fn(dx, dy) for dx in (-W, 0, W) for dy in (-H, 0, H)]

out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       '<defs><radialGradient id="g"><stop offset="0" stop-color="#bfe6ff"/><stop offset=".35" stop-color="#38b6ff" stop-opacity=".9"/>'
       '<stop offset="1" stop-color="#38b6ff" stop-opacity="0"/></radialGradient></defs>',
       '<g fill="none" stroke="#2f9be8" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" opacity=".55">']
for t in traces:
    for dx in (-W, 0, W):
        for dy in (-H, 0, H):
            out.append(f'<path transform="translate({dx} {dy})" d="{t}"/>')
out.append('</g><g fill="none" stroke="#5cc4ff" stroke-width="1.4" opacity=".7">')
for x, y in pads:
    for dx in (-W, 0, W):
        for dy in (-H, 0, H):
            out.append(f'<circle cx="{x+dx}" cy="{y+dy}" r="3.2"/>')
out.append('</g><g fill="#0d2a47" stroke="#3aa6f0" stroke-width="1.5" opacity=".75">')
for cx, cy, w, h in chips:
    out.append(f'<rect x="{cx}" y="{cy}" width="{w}" height="{h}" rx="4"/>')
    out.append(f'<rect x="{cx+10}" y="{cy+10}" width="{w-20}" height="{h-20}" rx="2" fill="none" opacity=".5"/>')
out.append('</g><g>')
for x, y in glows:
    for dx in (-W, 0, W):
        for dy in (-H, 0, H):
            out.append(f'<circle cx="{x+dx}" cy="{y+dy}" r="9" fill="url(#g)"/>')
out.append('</g></svg>')
open(sys.argv[1], "w").write("".join(out))
