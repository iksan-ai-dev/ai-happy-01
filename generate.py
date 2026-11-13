#!/usr/bin/env python3
"""Draw the ai-happy-01 entry image procedurally with Pillow.

A golden retriever puppy sits in an autumn field, both front paws raised
beside its cheeks, catching a falling red maple leaf in a sunbeam.
Rendered at 2048x2048 and downsampled to 1024x1024 (LANCZOS).

Run: python3 generate.py   (writes entry.png next to this file)
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

SS = 2048          # supersampled working size
OUT = 1024         # final size
HERE = Path(__file__).resolve().parent

# Warm palette
CREAM = (255, 243, 214)
APRICOT = (255, 196, 107)
SKY_ORANGE = (255, 158, 87)
SUN = (255, 217, 77)
SUN_CORE = (255, 243, 176)
DOG = (232, 168, 92)
DOG_DARK = (201, 123, 46)
DOG_LIGHT = (245, 205, 140)
MUZZLE = (255, 241, 205)
NOSE = (74, 46, 24)
LEAF_RED = (232, 64, 42)
LEAF_GOLD = (245, 176, 53)
LEAF_ORANGE = (240, 120, 40)
TEAL = (46, 125, 107)
BROWN = (91, 58, 30)
WHITE = (255, 255, 255)
PINK = (242, 125, 141)
GROUND_TOP = (247, 176, 74)
GROUND_BOTTOM = (232, 137, 42)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(w, h, stops):
    """Vertical gradient through color stops [(pos, rgb), ...]."""
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                px[0, y] = lerp(c0, c1, f)
                break
        else:
            px[0, y] = stops[-1][1]
    return img.resize((w, h))


def soft_disc(base, center, radius, color, blur, alpha=255):
    """Blurred glowing disc composited onto an RGBA image."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = center
    d.ellipse([x - radius, y - radius, x + radius, y + radius],
              fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


def lens_points(cx, cy, length, width, angle_deg):
    """Pointed-oval (lens) leaf outline, rotated by angle_deg."""
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    n = 24
    for i in range(n + 1):
        t = i / n
        x = -length / 2 + t * length
        y = -width / 2 * math.sin(math.pi * t) ** 0.9
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    for i in range(n, -1, -1):
        t = i / n
        x = -length / 2 + t * length
        y = width / 2 * math.sin(math.pi * t) ** 0.9
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return pts


def lens_leaf(draw, cx, cy, length, width, angle_deg, fill, vein=True):
    draw.polygon(lens_points(cx, cy, length, width, angle_deg), fill=fill)
    if vein:
        a = math.radians(angle_deg)
        x0 = cx - math.cos(a) * length / 2 * 0.92
        y0 = cy - math.sin(a) * length / 2 * 0.92
        x1 = cx + math.cos(a) * length / 2 * 0.92
        y1 = cy + math.sin(a) * length / 2 * 0.92
        draw.line([x0, y0, x1, y1], fill=BROWN, width=max(3, int(width * 0.06)))


def ellipse_poly(cx, cy, rx, ry, angle_deg, n=48):
    """Rotated ellipse outline as polygon points (for floppy ears)."""
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = rx * math.cos(t)
        y = ry * math.sin(t)
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return pts


MAPLE = [
    (0, -100), (22, -52), (62, -78), (48, -28), (92, -38),
    (58, 6), (88, 40), (34, 30), (26, 78), (8, 44),
    (0, 82), (-8, 44), (-26, 78), (-34, 30), (-88, 40),
    (-58, 6), (-92, -38), (-48, -28), (-62, -78), (-22, -52),
]


def maple_leaf(draw, cx, cy, size, angle_deg, fill=LEAF_RED):
    """Stylised five-lobed maple leaf, local coords scaled by size/100."""
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for (x, y) in MAPLE:
        x *= size / 100
        y *= size / 100
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    draw.polygon(pts, fill=fill)
    top = (cx - math.sin(a) * size * 0.95, cy - math.cos(a) * size * 0.95)
    bot = (cx + math.sin(a) * size * 0.82, cy + math.cos(a) * size * 0.82)
    stem = (cx + math.sin(a) * size * 1.02, cy + math.cos(a) * size * 1.02)
    draw.line([top, bot], fill=BROWN, width=max(4, int(size * 0.045)))
    draw.line([bot, stem], fill=BROWN, width=max(4, int(size * 0.04)))


def sparkle(draw, cx, cy, r, fill=WHITE):
    k = 0.16
    pts = [
        (cx, cy - r), (cx + r * k, cy - r * k), (cx + r, cy),
        (cx + r * k, cy + r * k), (cx, cy + r), (cx - r * k, cy + r * k),
        (cx - r, cy), (cx - r * k, cy - r * k),
    ]
    draw.polygon(pts, fill=fill)


def bird(draw, cx, cy, s, color=BROWN):
    w = max(4, int(s * 0.12))
    draw.arc([cx - s, cy - s * 0.5, cx, cy + s * 0.5], 180, 360,
             fill=color, width=w)
    draw.arc([cx, cy - s * 0.5, cx + s, cy + s * 0.5], 180, 360,
             fill=color, width=w)


def daisy(draw, cx, cy, r):
    for i in range(6):
        a = math.radians(i * 60)
        px = cx + math.cos(a) * r * 0.62
        py = cy + math.sin(a) * r * 0.62
        draw.ellipse([px - r * 0.42, py - r * 0.42,
                      px + r * 0.42, py + r * 0.42], fill=WHITE)
    draw.ellipse([cx - r * 0.38, cy - r * 0.38,
                  cx + r * 0.38, cy + r * 0.38], fill=(255, 205, 60))


def cloud(base, cx, cy, w, h, alpha=235):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - w, cy - h, cx + w, cy + h], fill=(255, 255, 255, alpha))
    d.ellipse([cx - w * 0.55, cy - h * 1.5, cx + w * 0.55, cy + h * 0.4],
              fill=(255, 255, 255, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(28))
    base.alpha_composite(layer)


def tree(draw, x, base_y, r, color, trunk=BROWN):
    draw.rectangle([x - 14, base_y - r * 1.1, x + 14, base_y + 80], fill=trunk)
    for (ox, oy, rr) in ((-r * 0.55, -r * 0.35, r * 0.62),
                         (r * 0.55, -r * 0.35, r * 0.62),
                         (0, -r * 0.85, r * 0.70)):
        draw.ellipse([x + ox - rr, base_y + oy - rr,
                      x + ox + rr, base_y + oy + rr], fill=color)


def horizon_y(x):
    """Top edge of the curved ground ellipse at column x."""
    return 2310 - 790 * math.sqrt(max(0.0, 1 - ((x - 1024) / 1724) ** 2))


def draw_background(img):
    # Sky: cream -> apricot -> soft orange.
    sky = vgrad(SS, SS, [(0.0, CREAM), (0.45, APRICOT), (0.75, SKY_ORANGE)])
    img.paste(sky, (0, 0))
    draw = ImageDraw.Draw(img, "RGBA")
    # Big sun, upper left, with a warm glow.
    soft_disc(img, (370, 380), 330, (255, 190, 90), 90, alpha=160)
    draw.ellipse([140, 150, 600, 610], fill=SUN)
    draw.ellipse([215, 225, 525, 535], fill=SUN_CORE)
    # Soft clouds on the right and low left, kept away from the birds.
    cloud(img, 1560, 330, 260, 70)
    cloud(img, 1620, 600, 210, 60)
    cloud(img, 330, 900, 230, 60)
    # Birds in clean sky, far from any cloud.
    bird(draw, 930, 330, 42)
    bird(draw, 1080, 450, 34)
    bird(draw, 800, 520, 30)
    # Autumn trees along the curved horizon.
    for (x, r, color) in ((150, 185, (214, 74, 44)),
                          (430, 140, (232, 120, 40)),
                          (660, 115, LEAF_GOLD),
                          (1400, 120, TEAL),
                          (1690, 175, (198, 60, 40)),
                          (1920, 150, (232, 120, 40))):
        tree(draw, x, horizon_y(x) + 10, r, color)


def draw_ground(img):
    grad = vgrad(SS, SS, [(0.0, GROUND_TOP), (1.0, GROUND_BOTTOM)]).convert("RGBA")
    mask = Image.new("L", (SS, SS), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([-700, 1520, 2748, 3100], fill=255)
    img.paste(grad, (0, 0), mask)


def draw_puppy(img):
    """Golden retriever puppy, sitting, front paws raised beside its cheeks."""
    draw = ImageDraw.Draw(img, "RGBA")

    # --- tail, wagging up to the left, cream tip + motion arcs ---
    draw.line([(760, 1580), (660, 1420), (575, 1280)], fill=DOG, width=140,
              joint="curve")
    draw.ellipse([705, 1495, 830, 1620], fill=DOG)
    draw.ellipse([510, 1170, 630, 1290], fill=MUZZLE)
    draw.arc([430, 1080, 640, 1290], 200, 320, fill=WHITE, width=12)
    draw.arc([395, 1140, 570, 1320], 200, 320, fill=WHITE, width=12)

    # --- body: sitting, rounded, cream belly ---
    draw.ellipse([690, 1220, 1358, 1800], fill=DOG)
    draw.ellipse([830, 1360, 1218, 1780], fill=MUZZLE)

    # --- hind paws with toe lines ---
    for px in (800, 1180):
        draw.ellipse([px - 115, 1660, px + 115, 1800], fill=DOG)
        for k in (-45, 0, 45):
            draw.arc([px + k - 18, 1705, px + k + 18, 1765], 300, 60,
                     fill=NOSE, width=10)

    # --- floppy ears, behind the head ---
    draw.polygon(ellipse_poly(725, 920, 135, 245, 25), fill=DOG_DARK)
    draw.polygon(ellipse_poly(725, 940, 85, 175, 25), fill=DOG)
    draw.polygon(ellipse_poly(1323, 920, 135, 245, -25), fill=DOG_DARK)
    draw.polygon(ellipse_poly(1323, 940, 85, 175, -25), fill=DOG)

    # --- head ---
    draw.ellipse([694, 650, 1354, 1330], fill=DOG)
    # tuft of fur on top
    draw.polygon([(1000, 640), (1024, 585), (1048, 640)], fill=DOG_DARK)

    # --- muzzle, nose, smile, tongue ---
    draw.ellipse([820, 1060, 1228, 1340], fill=MUZZLE)
    draw.ellipse([948, 1090, 1100, 1180], fill=NOSE)
    draw.ellipse([970, 1105, 1012, 1142], fill=WHITE)
    # rosy cheeks, soft
    soft_disc(img, (845, 1150), 55, PINK, 25, alpha=110)
    soft_disc(img, (1203, 1150), 55, PINK, 25, alpha=110)
    draw = ImageDraw.Draw(img, "RGBA")
    # tongue first, smile arc over its top edge
    draw.ellipse([982, 1225, 1066, 1325], fill=PINK)
    draw.line([1024, 1245, 1024, 1310], fill=(214, 90, 110), width=6)
    draw.arc([955, 1170, 1093, 1290], 15, 165, fill=NOSE, width=14)

    # --- closed happy eyes (arches) + tiny lashes ---
    draw.arc([830, 920, 940, 1030], 180, 360, fill=NOSE, width=16)
    draw.arc([1108, 920, 1218, 1030], 180, 360, fill=NOSE, width=16)
    draw.line([838, 935, 822, 918], fill=NOSE, width=10)
    draw.line([1210, 935, 1226, 918], fill=NOSE, width=10)

    # --- front legs raised: arms from the shoulders up beside the cheeks ---
    draw.line([(800, 1480), (722, 1150)], fill=DOG, width=150, joint="curve")
    draw.line([(1248, 1480), (1326, 1150)], fill=DOG, width=150, joint="curve")
    # paw blobs flanking the muzzle, below eye level so the face stays clear
    draw.ellipse([600, 990, 820, 1210], fill=DOG_LIGHT)
    draw.ellipse([1228, 990, 1448, 1210], fill=DOG_LIGHT)
    for (px, flip) in ((710, False), (1338, True)):
        for k in (-48, 0, 48):
            if flip:
                draw.arc([px + k - 16, 1040, px + k + 16, 1100], 120, 240,
                         fill=NOSE, width=10)
            else:
                draw.arc([px + k - 16, 1040, px + k + 16, 1100], 300, 60,
                         fill=NOSE, width=10)


def draw_extras(img):
    """Falling leaves, sparkles and daisies around the puppy."""
    draw = ImageDraw.Draw(img, "RGBA")
    # Red maple leaf falling above the head, with motion arcs.
    maple_leaf(draw, 1230, 430, 215, -18)
    draw.arc([1360, 330, 1560, 530], 300, 60, fill=WHITE, width=12)
    draw.arc([1395, 375, 1545, 525], 300, 60, fill=WHITE, width=12)
    # Small lens-shaped leaves drifting down.
    lens_leaf(draw, 480, 620, 150, 80, -30, LEAF_GOLD)
    lens_leaf(draw, 1560, 1010, 140, 75, 35, LEAF_RED)
    lens_leaf(draw, 330, 1450, 130, 70, 20, LEAF_ORANGE)
    lens_leaf(draw, 300, 1700, 120, 65, -15, LEAF_RED)
    lens_leaf(draw, 1700, 1750, 130, 70, 25, LEAF_GOLD)
    lens_leaf(draw, 430, 1330, 110, 60, -40, LEAF_ORANGE)
    # Sparkles in the sunbeam.
    sparkle(draw, 620, 320, 26)
    sparkle(draw, 1470, 830, 22)
    sparkle(draw, 560, 640, 18)
    sparkle(draw, 1430, 700, 16)
    # Daisies in the bottom corners.
    daisy(draw, 110, 1930, 55)
    daisy(draw, 1938, 1930, 55)


def build():
    img = Image.new("RGBA", (SS, SS))
    draw_background(img)
    draw_ground(img)
    # Soft contact shadow under the puppy.
    layer = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([690, 1730, 1360, 1870], fill=(120, 60, 10, 90))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(28)))
    draw_puppy(img)
    draw_extras(img)
    img = img.convert("RGB").resize((OUT, OUT), Image.LANCZOS)
    img.save(HERE / "entry.png", optimize=True)
    print("wrote", HERE / "entry.png", img.size)


if __name__ == "__main__":
    build()
