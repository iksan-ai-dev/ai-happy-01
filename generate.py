# generate.py — draws the ai-happy-01 entry image with Pillow (build time only).
#
# Art direction: a golden retriever puppy sitting in warm autumn light,
# both front paws raised beside its cheeks, catching a falling maple leaf
# in a sunbeam. Flat illustration, big central subject, warm palette,
# no text, no human faces, no stock photos — every pixel is drawn here.
#
# The grading runtime is standard-library only (no Pillow), so this script
# runs here, at build time, and main.py only copies the finished PNG.
# Supersampled at 2048x2048, downscaled to 1024x1024 with LANCZOS.
#
# Usage: python3 generate.py  -> writes entry.png next to this file.

import math
from PIL import Image, ImageDraw, ImageFilter

S = 2048            # working canvas (supersample)
OUT = 1024          # final size

CREAM = (255, 243, 214)
APRICOT = (255, 196, 107)
ORANGE = (255, 138, 61)
SUN = (255, 223, 107)
GOLD = (232, 168, 92)       # puppy fur
GOLD_DARK = (201, 123, 46)  # ears / outline
FUR_LIGHT = (251, 227, 176)  # chest, muzzle
BROWN = (91, 58, 30)        # outlines, nose
TEAL = (46, 125, 107)
LEAF_RED = (232, 84, 47)
LEAF_GOLD = (245, 178, 60)
PINK = (242, 139, 130)


def vgrad(size, top, bottom):
    """Vertical linear gradient."""
    w, h = size
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    return img


def layer():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def blur(img, r):
    return img.filter(ImageFilter.GaussianBlur(r))


def paste_rotated(base, shape_img, cx, cy, angle):
    """Paste shape_img (RGBA) onto base, rotated around its centre at (cx, cy)."""
    rot = shape_img.rotate(angle, resample=Image.BICUBIC, expand=False)
    base.alpha_composite(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)))


def ellipse_layer(cx, cy, rx, ry, fill, blur_r=0):
    img = layer()
    d = ImageDraw.Draw(img)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill)
    return blur(img, blur_r) if blur_r else img


def maple_leaf(size, color, vein=(120, 40, 20, 255)):
    """A 5-lobed maple leaf, drawn pointing up, on its own RGBA tile."""
    w = h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = w / 2, h / 2
    # Lobes as a star-ish polygon, hand-tuned for a friendly maple shape.
    pts = []
    for ang_deg, r in [
        (-90, 0.50), (-72, 0.30), (-54, 0.46), (-36, 0.28), (-18, 0.44),
        (0, 0.26), (18, 0.40), (36, 0.24), (54, 0.34), (72, 0.20),
        (90, 0.30), (108, 0.20), (126, 0.34), (144, 0.24), (162, 0.40),
        (180, 0.26), (198, 0.44), (216, 0.28), (234, 0.46), (252, 0.30),
    ]:
        a = math.radians(ang_deg)
        pts.append((cx + r * w * math.cos(a), cy + r * h * math.sin(a)))
    d.polygon(pts, fill=color + (255,))
    # Stem + centre vein.
    d.line([(cx, cy + 0.28 * h), (cx, cy + 0.38 * h)], fill=vein, width=max(4, size // 40))
    d.line([(cx, cy - 0.42 * h), (cx, cy + 0.28 * h)], fill=vein, width=max(3, size // 60))
    return img


def simple_leaf(size, color):
    """A small lens-shaped leaf with a stem, pointing up."""
    w, h = size, int(size * 1.3)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Lens shape: two curved sides meeting at top and bottom points.
    pts = [(0.50, 0.02), (0.72, 0.18), (0.95, 0.45), (0.78, 0.72),
           (0.55, 0.96), (0.45, 0.96), (0.22, 0.72), (0.05, 0.45), (0.28, 0.18)]
    d.polygon([(x * w, y * h) for (x, y) in pts], fill=color + (255,))
    d.line([(w / 2, h * 0.08), (w / 2, h * 0.92)], fill=(120, 60, 20, 255), width=max(3, size // 30))
    d.line([(w / 2, h * 0.90), (w / 2, h)], fill=(120, 60, 20, 255), width=max(3, size // 30))
    return img


def sparkle(cx, cy, r, color=(255, 255, 255, 220)):
    img = layer()
    d = ImageDraw.Draw(img)
    d.polygon([(cx, cy - r), (cx + r * 0.22, cy - r * 0.22), (cx + r, cy),
               (cx + r * 0.22, cy + r * 0.22), (cx, cy + r),
               (cx - r * 0.22, cy + r * 0.22), (cx - r, cy),
               (cx - r * 0.22, cy - r * 0.22)], fill=color)
    return img


def build():
    # ---- sky ----
    img = vgrad((S, S), (255, 233, 168), (255, 178, 94)).convert("RGBA")

    # ---- sun glow + disc (top-left) ----
    img.alpha_composite(ellipse_layer(470, 400, 430, 430, (255, 214, 110, 90), blur_r=110))
    img.alpha_composite(ellipse_layer(470, 400, 240, 240, (255, 226, 130, 160), blur_r=40))
    d = ImageDraw.Draw(img)
    d.ellipse([470 - 210, 400 - 210, 470 + 210, 400 + 210], fill=SUN + (255,))
    d.ellipse([420 - 120, 350 - 120, 420 + 120, 350 + 120], fill=(255, 240, 170, 255))

    # ---- sunbeams fanning down-right ----
    beams = layer()
    bd = ImageDraw.Draw(beams)
    for (x0, x1, a) in [(650, 760, 26), (760, 900, 20), (900, 1080, 16)]:
        bd.polygon([(470, 400), (x0, 2048), (x1, 2048)], fill=(255, 240, 180, a))
    img.alpha_composite(blur(beams, 36))

    # ---- clouds ----
    for (cx, cy, rx, ry) in [(1520, 300, 260, 90), (1700, 560, 200, 70), (330, 920, 220, 80)]:
        img.alpha_composite(ellipse_layer(cx, cy, rx, ry, (255, 255, 255, 215), blur_r=28))
        img.alpha_composite(ellipse_layer(cx - 120, cy + 30, rx * 0.6, ry * 0.7, (255, 255, 255, 200), blur_r=24))

    # ---- birds (clear sky, away from sun and clouds) ----
    bd = ImageDraw.Draw(img)
    for (bx, by, s) in [(1000, 330, 46), (1150, 410, 36), (900, 470, 30)]:
        bd.arc([bx - s, by - s // 2, bx, by + s // 2], 200, 340, fill=BROWN + (220,), width=9)
        bd.arc([bx, by - s // 2, bx + s, by + s // 2], 200, 340, fill=BROWN + (220,), width=9)

    # ---- distant autumn trees + field band ----
    trees = layer()
    td = ImageDraw.Draw(trees)
    td.rectangle([0, 1330, S, 1560], fill=(201, 158, 92, 255))
    for (cx, cy, r, col, col2) in [
        (250, 1430, 190, (214, 96, 50), (232, 130, 70)),
        (640, 1390, 160, (240, 170, 60), (250, 200, 90)),
        (1750, 1410, 210, (196, 70, 44), (220, 100, 60)),
        (1450, 1460, 150, TEAL, (70, 150, 125)),
        (1050, 1410, 140, (232, 140, 70), (245, 175, 95)),
        (1950, 1480, 170, (214, 120, 60), (230, 150, 80)),
    ]:
        # Clustered canopy: three overlapping circles, two shades.
        td.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (255,))
        td.ellipse([cx - r * 0.9, cy - r * 0.7, cx - r * 0.1, cy + r * 0.1], fill=col2 + (255,))
        td.ellipse([cx + r * 0.1, cy - r * 0.6, cx + r * 0.8, cy + r * 0.2], fill=col2 + (255,))
        td.rectangle([cx - 14, cy + r * 0.3, cx + 14, 1560], fill=BROWN + (255,))
    img.alpha_composite(blur(trees, 6))

    # ---- ground: warm grass hill with a gently curved horizon ----
    ground = vgrad((S, 548), (247, 185, 92), (232, 147, 60)).convert("RGBA")
    hill_mask = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(hill_mask)
    top = [(x, int(1560 - 60 * math.sin(math.pi * x / S))) for x in range(0, S + 1, 64)]
    md.polygon(top + [(S, S), (0, S)], fill=255)
    img.paste(ground, (0, 1500), hill_mask.crop((0, 1500, S, S)))
    # soft hill shading
    img.alpha_composite(ellipse_layer(1024, 2050, 900, 180, (214, 120, 50, 70), blur_r=60))

    # ---- puppy shadow ----
    img.alpha_composite(ellipse_layer(1024, 1790, 430, 95, (120, 70, 30, 95), blur_r=42))

    # ---- puppy: tail (wagging, curving out to the left, visible past the body) ----
    tail = layer()
    tdraw = ImageDraw.Draw(tail)
    pts = [(720, 1520), (600, 1420), (510, 1300), (470, 1160)]
    tdraw.line(pts, fill=GOLD + (255,), width=150, joint="curve")
    for (px, py) in pts:
        tdraw.ellipse([px - 75, py - 75, px + 75, py + 75], fill=GOLD + (255,))
    tdraw.ellipse([470 - 80, 1160 - 80, 470 + 80, 1160 + 80], fill=FUR_LIGHT + (255,))
    img.alpha_composite(blur(tail, 4))
    # wag motion arcs
    md = ImageDraw.Draw(img)
    md.arc([330, 1000, 620, 1290], 250, 330, fill=(255, 255, 255, 130), width=12)
    md.arc([300, 1080, 580, 1340], 250, 330, fill=(255, 255, 255, 90), width=9)

    # ---- puppy: body (sitting) ----
    img.alpha_composite(ellipse_layer(1024, 1450, 392, 342, GOLD_DARK + (255,)))  # outline
    img.alpha_composite(ellipse_layer(1024, 1450, 378, 328, GOLD + (255,)))
    # haunches
    img.alpha_composite(ellipse_layer(762, 1560, 195, 205, GOLD + (255,)))
    img.alpha_composite(ellipse_layer(1286, 1560, 195, 205, GOLD + (255,)))
    # chest / belly patch
    img.alpha_composite(ellipse_layer(1024, 1520, 235, 265, FUR_LIGHT + (255,)))
    # hind paws
    img.alpha_composite(ellipse_layer(820, 1730, 135, 72, GOLD + (255,)))
    img.alpha_composite(ellipse_layer(1228, 1730, 135, 72, GOLD + (255,)))
    pd = ImageDraw.Draw(img)
    for cx in (820, 1228):
        for dx in (-45, 0, 45):
            pd.arc([cx + dx - 22, 1700, cx + dx + 22, 1760], 300, 60, fill=BROWN + (200,), width=7)

    # ---- puppy: raised front legs are drawn AFTER the head, below ----

    # ---- puppy: head ----
    img.alpha_composite(ellipse_layer(1024, 950, 312, 312, GOLD_DARK + (255,)))  # outline
    img.alpha_composite(ellipse_layer(1024, 950, 298, 298, GOLD + (255,)))
    # floppy ears
    ear_l = Image.new("RGBA", (340, 520), (0, 0, 0, 0))
    ed = ImageDraw.Draw(ear_l)
    ed.ellipse([20, 20, 320, 500], fill=GOLD_DARK + (255,))
    ed.ellipse([70, 90, 270, 430], fill=(214, 143, 66, 255))
    paste_rotated(img, ear_l, 742, 900, 24)
    ear_r = Image.new("RGBA", (340, 520), (0, 0, 0, 0))
    ed = ImageDraw.Draw(ear_r)
    ed.ellipse([20, 20, 320, 500], fill=GOLD_DARK + (255,))
    ed.ellipse([70, 90, 270, 430], fill=(214, 143, 66, 255))
    paste_rotated(img, ear_r, 1306, 880, -24)
    # forehead tuft
    fd = ImageDraw.Draw(img)
    fd.polygon([(990, 660), (1024, 580), (1058, 660)], fill=GOLD_DARK + (255,))
    fd.polygon([(1000, 660), (1024, 600), (1048, 660)], fill=GOLD + (255,))

    # ---- puppy: face ----
    img.alpha_composite(ellipse_layer(1024, 1075, 215, 155, FUR_LIGHT + (255,)))  # muzzle
    fd = ImageDraw.Draw(img)
    # nose
    fd.ellipse([1024 - 88, 985 - 58, 1024 + 88, 985 + 58], fill=BROWN + (255,))
    fd.ellipse([990 - 22, 962 - 14, 990 + 22, 962 + 14], fill=(255, 255, 255, 90))
    # smile
    fd.arc([930, 1040, 1120, 1180], 15, 165, fill=BROWN + (255,), width=15)
    # tongue
    fd.rounded_rectangle([1024 - 58, 1120, 1024 + 58, 1245], radius=55, fill=PINK + (255,))
    fd.line([(1024, 1135), (1024, 1230)], fill=(200, 90, 90, 255), width=7)
    # closed happy eyes (upward arcs) + lashes
    for cx in (872, 1176):
        fd.arc([cx - 62, 838, cx + 62, 950], 200, 340, fill=BROWN + (255,), width=17)
        fd.line([(cx - 62, 890), (cx - 86, 868)], fill=BROWN + (255,), width=10)
        fd.line([(cx + 62, 890), (cx + 86, 868)], fill=BROWN + (255,), width=10)
    # blush
    img.alpha_composite(ellipse_layer(812, 1010, 72, 46, (242, 139, 130, 120), blur_r=18))
    img.alpha_composite(ellipse_layer(1236, 1010, 72, 46, (242, 139, 130, 120), blur_r=18))

    # ---- puppy: raised front legs, drawn AFTER the head so the paws read ----
    # Paws up beside the cheeks (never across the face), reaching for the leaf.
    legs = layer()
    ld = ImageDraw.Draw(legs)
    ld.line([(800, 1480), (720, 1060)], fill=GOLD + (255,), width=150, joint="curve")
    ld.line([(1250, 1480), (1330, 1010)], fill=GOLD + (255,), width=150, joint="curve")
    for (px, py) in [(800, 1480), (720, 1060), (1250, 1480), (1330, 1010)]:
        ld.ellipse([px - 75, py - 75, px + 75, py + 75], fill=GOLD + (255,))
    img.alpha_composite(legs)
    # front paws with toe lines
    img.alpha_composite(ellipse_layer(720, 1010, 118, 92, GOLD + (255,)))
    img.alpha_composite(ellipse_layer(1330, 960, 118, 92, GOLD + (255,)))
    pd = ImageDraw.Draw(img)
    for (cx, cy) in [(720, 1010), (1330, 960)]:
        for dx in (-48, 0, 48):
            pd.arc([cx + dx - 20, cy - 30, cx + dx + 20, cy + 30], 300, 60, fill=BROWN + (200,), width=7)

    # ---- hero leaf, glowing, in the air above the paws ----
    img.alpha_composite(ellipse_layer(1210, 590, 200, 200, (255, 150, 80, 70), blur_r=60))
    hero = maple_leaf(380, LEAF_RED)
    paste_rotated(img, hero, 1210, 590, -25)
    # motion swoosh around the leaf
    md = ImageDraw.Draw(img)
    md.arc([1010, 370, 1430, 790], 300, 60, fill=(255, 255, 255, 150), width=12)
    md.arc([1050, 430, 1390, 740], 300, 60, fill=(255, 255, 255, 100), width=9)

    # ---- scattered falling leaves ----
    for (cx, cy, size, col, ang) in [
        (600, 620, 150, LEAF_GOLD, 40), (1620, 980, 130, LEAF_RED, -35),
        (420, 1300, 120, (232, 140, 70), 70), (1760, 520, 140, LEAF_GOLD, -60),
        (300, 1700, 110, LEAF_RED, 20),
    ]:
        paste_rotated(img, simple_leaf(size, col), cx, cy, ang)

    # ---- sparkles ----
    for (cx, cy, r) in [(700, 300, 34), (1500, 760, 26), (1560, 620, 20), (880, 560, 18)]:
        img.alpha_composite(sparkle(cx, cy, r))

    # ---- foreground daisies ----
    for (cx, cy) in [(180, 1900), (1880, 1930)]:
        for k in range(5):
            a = math.radians(k * 72 - 90)
            px, py = cx + 42 * math.cos(a), cy + 42 * math.sin(a)
            img.alpha_composite(ellipse_layer(int(px), int(py), 26, 40, (255, 255, 255, 235)))
        img.alpha_composite(ellipse_layer(cx, cy, 30, 30, (255, 200, 60, 255)))

    # ---- downscale + save ----
    out = img.convert("RGB").resize((OUT, OUT), Image.LANCZOS)
    out.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    build()
