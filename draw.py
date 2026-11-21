#!/usr/bin/env python3
"""Draw 'The World Today — Friday 20 November 2026: 35 stories' (1024x1024).

One self-contained Pillow program: renders the whole front page at 2x and
downscales to 1024x1024 with LANCZOS. Every number, headline and date is
hard-coded from the brief; nothing is read from disk except fonts.
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SS = 2                      # supersample factor
W, H = 1024, 1024           # final size
CW, CH = W * SS, H * SS     # canvas size

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), int(round(size * SS)))

def F(name, size):
    try:
        return font(name, size)
    except OSError:
        return font("DejaVuSans.ttf", size)

SERIF  = lambda s: F("DejaVuSerif.ttf", s)
SERIFB = lambda s: F("DejaVuSerif-Bold.ttf", s)
SERIFI = lambda s: F("DejaVuSerif-Italic.ttf", s) if os.path.exists(
    os.path.join(FONT_DIR, "DejaVuSerif-Italic.ttf")) else SERIF(s)
SANS   = lambda s: F("DejaVuSans.ttf", s)
SANSB  = lambda s: F("DejaVuSans-Bold.ttf", s)

# ---------- palette ----------
PAPER_TOP = (248, 243, 230)
PAPER_BOT = (238, 229, 206)
RED       = (185, 28, 28)
RED_D     = (143, 22, 22)
INK       = (28, 26, 23)
MUTED     = (107, 100, 85)
RULE      = (198, 183, 152)
BAND_BG   = (238, 229, 205)
NAVY_TOP  = (24, 43, 66)
NAVY_BOT  = (13, 24, 40)
LAND      = (34, 62, 88)
COAST     = (58, 92, 124)
GOLD      = (201, 162, 39)

def sc(v):
    return int(round(v * SS))

def box(x0, y0, x1, y1):
    return (sc(x0), sc(y0), sc(x1), sc(y1))

def grad(d, x0, y0, x1, y1, c1, c2, vertical=True):
    """Fill rect with a two-colour gradient."""
    steps = sc(y1 - y0) if vertical else sc(x1 - x0)
    steps = max(steps, 1)
    for i in range(steps):
        t = i / steps
        c = tuple(int(round(c1[j] + (c2[j] - c1[j]) * t)) for j in range(3))
        if vertical:
            d.line([(sc(x0), sc(y0) + i), (sc(x1), sc(y0) + i)], fill=c)
        else:
            d.line([(sc(x0) + i, sc(y0)), (sc(x0) + i, sc(y1))], fill=c)

def rrect(d, x0, y0, x1, y1, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box(x0, y0, x1, y1), radius=sc(r),
                        fill=fill, outline=outline, width=sc(width))

def txt(d, x, y, s, f, fill, anchor="la"):
    d.text((sc(x), sc(y)), s, font=f, fill=fill, anchor=anchor)

def tw(d, s, f):
    """Text width in 1024-space."""
    return d.textlength(s, font=f) / SS

def wrap(d, s, f, width):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tw(d, trial, f) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def para(d, x, y, lines, f, fill, lh):
    for i, ln in enumerate(lines):
        txt(d, x, y + i * lh, ln, f, fill)
    return y + len(lines) * lh

def banner(d, x0, y, x1, text, f):
    """Red fact banner strip inside a picture."""
    h = 15
    d.rectangle(box(x0, y, x1, y + h), fill=RED)
    txt(d, x0 + 6, y + 2.5, text, f, (255, 255, 255))

def chip(d, x, y, text, f, fill=(16, 30, 48)):
    w = tw(d, text, f) + 10
    rrect(d, x, y, x + w, y + 13, 6, fill=fill)
    txt(d, x + 5, y + 1.5, text, f, (255, 255, 255))

# ---------- canvas ----------
img = Image.new("RGB", (CW, CH), PAPER_TOP)
d = ImageDraw.Draw(img, "RGBA")
grad(d, 0, 0, W, H, PAPER_TOP, PAPER_BOT)

MX = 28            # left margin
RX = 996           # right edge
CWID = RX - MX     # content width

# ---------- top ----------
txt(d, MX, 8, "35 STORIES  ·  7 REGIONS  ·  EVERY ONE DATED FRIDAY 20 NOVEMBER 2026",
    SANSB(10), RED, anchor="la")
d.line([(sc(MX), sc(24)), (sc(RX), sc(24))], fill=RULE, width=sc(1))
txt(d, W / 2, 29, "T H E   W O R L D   T O D A Y", SERIFB(17), RED, anchor="ma")
txt(d, W / 2, 50, "Friday 20 November 2026", SERIFB(40), INK, anchor="ma")
txt(d, W / 2, 100,
    "Russian missiles hit Kyiv's bridges  ·  Cyclone Akvan strikes India  ·  An AI sell-off sinks Asia's markets",
    SERIFI(12.5), (74, 68, 56), anchor="ma")
d.line([(sc(MX), sc(120)), (sc(RX), sc(120))], fill=RULE, width=sc(1))

# ---------- timeline strip ----------
TY, TH = 126, 26
rrect(d, MX, TY, RX, TY + TH, 4, fill=BAND_BG)
txt(d, MX + 8, TY + 7, "FRIDAY IN ORDER", SANSB(9), RED)
beats = [
    ("Overnight", "Kyiv bridges hit"),
    ("~08:00", "Akvan landfall, Gopalpur"),
    ("Morning", "Italy general strike"),
    ("Afternoon", "Taiex -6.2%, Nvidia -14%"),
    ("Evening", "ATP pay plan past $350m"),
    ("Night", "COP31 ends, no deal"),
]
bx = MX + 118
bw = (RX - 8 - bx) / 6
for i, (t, ev) in enumerate(beats):
    x = bx + i * bw
    txt(d, x, TY + 3.5, t, SANSB(8.5), RED_D)
    txt(d, x, TY + 13.5, ev, SANS(8.5), INK)
    if i:
        d.line([(sc(x - 4), sc(TY + 5)), (sc(x - 4), sc(TY + TH - 5))],
               fill=RULE, width=sc(1))

# ---------- number strip ----------
NY, NH = 158, 36
nums = [("3", "bridges hit in Kyiv"), ("300,000+", "evacuated before Akvan"),
        ("-6.2%", "Taiwan Taiex"), ("100,000", "youth visas a year UK–EU"),
        ("2.3%", "Japan inflation"), ("118", "Phillips")]
cw = CWID / 6
for i, (n, lab) in enumerate(nums):
    x = MX + i * cw
    txt(d, x + cw / 2, NY + 1, n, SERIFB(15), INK, anchor="ma")
    txt(d, x + cw / 2, NY + 20, lab, SANS(8), MUTED, anchor="ma")
    if i:
        d.line([(sc(x), sc(NY + 4)), (sc(x), sc(NY + NH - 4))], fill=RULE, width=sc(1))
d.line([(sc(MX), sc(NY + NH)), (sc(RX), sc(NY + NH))], fill=RULE, width=sc(1))

# ---------- region bar ----------
regions = [("EUROPE", 9, (185, 28, 28)), ("ASIA", 7, (30, 90, 140)),
           ("MIDDLE EAST", 4, (150, 110, 20)), ("AFRICA", 5, (40, 120, 70)),
           ("AMERICAS", 4, (110, 60, 130)), ("OCEANIA", 3, (20, 120, 130)),
           ("GLOBAL", 3, (100, 100, 100))]
RY = 200
rx = MX
for name, n, col in regions:
    wseg = CWID * n / 35
    d.rectangle(box(rx, RY, rx + wseg - 1, RY + 5), fill=col)
    rx += wseg
labels = "   ·   ".join(f"{name} {n}" for name, n, _ in regions)
txt(d, W / 2, RY + 8, labels, SANSB(8.5), INK, anchor="ma")

# ---------- hero pictures ----------
def hash01(i, k=0.0):
    return (math.sin(i * 12.9898 + k * 78.233) * 43758.5453) % 1.0

def kyiv_pic(x0, y0, x1, y1):
    grad(d, x0, y0, x1, y1, (13, 27, 46), (42, 74, 107))
    w, h = x1 - x0, y1 - y0
    for i in range(46):
        sx = x0 + hash01(i, 1) * w
        sy = y0 + hash01(i, 2) * h * 0.55
        r = 0.8 + hash01(i, 3) * 1.2
        d.ellipse(box(sx - r, sy - r, sx + r, sy + r),
                  fill=(255, 255, 255))
    d.ellipse(box(x1 - 42, y0 + 10, x1 - 18, y0 + 34), fill=(238, 230, 196))
    # skyline
    base = y1 - 26
    bx = x0
    i = 0
    while bx < x1:
        bw = 14 + hash01(i, 4) * 22
        bh = 18 + hash01(i, 5) * 42
        d.rectangle(box(bx, base - bh, bx + bw, base + 26), fill=(8, 17, 30))
        for wy in range(3):
            if hash01(i * 7 + wy, 6) > 0.55:
                d.rectangle(box(bx + 3 + wy * 5, base - bh + 5 + wy * 9,
                                bx + 5 + wy * 5, base - bh + 7 + wy * 9),
                            fill=(255, 205, 90))
        bx += bw + 3
        i += 1
    # river + bridges
    d.rectangle(box(x0, base, x1, y1), fill=(29, 58, 82))
    for k, ay in enumerate((base + 6, base + 12, base + 18)):
        d.arc(box(x0 + 12 + k * 8, ay - 14, x1 - 12 - k * 8, ay + 14),
              180, 360, fill=(200, 208, 216), width=sc(2))
    # missile trails
    for k, (tx, ty) in enumerate(((0.30, 0.12), (0.55, 0.05), (0.78, 0.18))):
        hx, hy = x0 + tx * w, y0 + ty * h
        d.line([(sc(hx), sc(hy)), (sc(hx - 52), sc(hy + 30))],
               fill=(255, 140, 40), width=sc(3))
        d.line([(sc(hx), sc(hy)), (sc(hx - 52), sc(hy + 30))],
               fill=(255, 220, 130), width=sc(1))
        d.ellipse(box(hx - 3, hy - 3, hx + 3, hy + 3), fill=(255, 240, 180))

def akvan_pic(x0, y0, x1, y1):
    grad(d, x0, y0, x1, y1, (30, 90, 122), (14, 58, 82))
    w, h = x1 - x0, y1 - y0
    # landmass (east coast)
    land = [(x0 + 0.66 * w, y0 + 0.02 * h), (x0 + 0.98 * w, y0 + 0.05 * h),
            (x0 + 0.97 * w, y0 + 0.55 * h), (x0 + 0.82 * w, y0 + 0.98 * h),
            (x0 + 0.70 * w, y0 + 0.70 * h), (x0 + 0.62 * w, y0 + 0.30 * h)]
    d.polygon([(sc(px), sc(py)) for px, py in land], fill=(201, 168, 106))
    d.line([(sc(px), sc(py)) for px, py in land] + [(sc(land[0][0]), sc(land[0][1]))],
           fill=(150, 118, 70), width=sc(1))
    # cyclone spiral
    cx, cy = x0 + 0.42 * w, y0 + 0.55 * h
    for k, r in enumerate((14, 24, 34, 44, 54)):
        a0 = k * 55
        d.arc(box(cx - r, cy - r, cx + r, cy + r), a0, a0 + 250,
              fill=(255, 255, 255), width=sc(3))
    d.ellipse(box(cx - 7, cy - 7, cx + 7, cy + 7), fill=(255, 255, 255))
    # rain streaks
    for i in range(26):
        rx = x0 + hash01(i, 7) * w * 0.6
        ry = y0 + hash01(i, 8) * h * 0.8
        d.line([(sc(rx), sc(ry)), (sc(rx - 6), sc(ry + 12))],
               fill=(200, 220, 235), width=sc(1))
    # landfall marker
    lx, ly = x0 + 0.66 * w, y0 + 0.38 * h
    d.ellipse(box(lx - 5, ly - 5, lx + 5, ly + 5), fill=RED,
              outline=(255, 255, 255), width=sc(2))

def market_pic(x0, y0, x1, y1):
    grad(d, x0, y0, x1, y1, (243, 237, 224), (230, 220, 196))
    w, h = x1 - x0, y1 - y0
    for gx in range(1, 8):
        d.line([(sc(x0 + gx * w / 8), sc(y0)), (sc(x0 + gx * w / 8), sc(y1))],
               fill=(216, 205, 178), width=sc(1))
    for gy in range(1, 5):
        d.line([(sc(x0), sc(y0 + gy * h / 5)), (sc(x1), sc(y0 + gy * h / 5))],
               fill=(216, 205, 178), width=sc(1))
    pts = [(x0 + 12, y0 + 16), (x0 + 0.18 * w, y0 + 0.30 * h),
           (x0 + 0.34 * w, y0 + 0.26 * h), (x0 + 0.48 * w, y0 + 0.52 * h),
           (x0 + 0.60 * w, y0 + 0.66 * h)]
    area = pts + [(pts[-1][0], y1 - 16), (pts[0][0], y1 - 16)]
    d.polygon([(sc(px), sc(py)) for px, py in area], fill=(226, 186, 176))
    d.line([(sc(px), sc(py)) for px, py in pts], fill=RED, width=sc(3), joint="curve")
    for px, py in pts:
        d.ellipse(box(px - 3, py - 3, px + 3, py + 3), fill=RED)
    # mini table
    tx0, ty0, tx1, ty1 = x1 - 108, y0 + 8, x1 - 8, y1 - 14
    rrect(d, tx0, ty0, tx1, ty1, 5, fill=(255, 255, 255))
    rows = [("Taipei", "-6.2%"), ("Seoul", "-5.2%"),
            ("Tokyo", "-5.1%"), ("Hong Kong", "-1.9%")]
    rh = (ty1 - ty0) / 4
    for i, (lab, val) in enumerate(rows):
        ry = ty0 + i * rh
        txt(d, tx0 + 7, ry + rh / 2 - 5, lab, SANS(8), INK, anchor="lm")
        txt(d, tx1 - 7, ry + rh / 2 - 5, val, SANSB(8.5), RED, anchor="rm")
        if i:
            d.line([(sc(tx0 + 5), sc(ry)), (sc(tx1 - 5), sc(ry))],
                   fill=(225, 215, 195), width=sc(1))

# ---------- heroes ----------
heroes = [
    dict(kicker="KYIV, UKRAINE · WAR", banner="3 BRIDGES HIT",
         chip="Officials' count", pic=kyiv_pic,
         headline="Russian missiles hit three Kyiv bridges overnight",
         body="~110 missiles and 400 drones; 9 killed across Ukraine, 3 in Kyiv; power and water cut. (Kyiv Independent, BBC)",
         foot="9 killed · 3 bridges hit · power cut"),
    dict(kicker="ODISHA, INDIA · CYCLONE", banner="300,000+ EVACUATED",
         chip="Weather office", pic=akvan_pic,
         headline="Cyclone Akvan slams Odisha coast at dawn",
         body="Landfall near Gopalpur ~8am; 300,000+ evacuated; 209mm rain in Ganjam; gusts 90 km/h; no deaths. (IMD, Deccan Herald)",
         foot="300,000+ evacuated · 209mm rain"),
    dict(kicker="ASIAN MARKETS · STOCKS", banner="TAIEX -6.2%",
         chip="Closing prices", pic=market_pic,
         headline="AI sell-off sinks Asia's markets",
         body="Taiwan -6.2%, worst week since 1991; Seoul -5.2%, Tokyo -5.1%, Hong Kong -1.9%, Nvidia -14%. (Al Jazeera, Anadolu)",
         foot="Taiex -6.2% · Kospi -5.2% · Nvidia -14% · S&P 500 -3.7%"),
]
HY, HPIC = 224, 114
HW = (CWID - 20) / 3
for ci, hero in enumerate(heroes):
    x0 = MX + ci * (HW + 10)
    x1 = x0 + HW
    hero["pic"](x0, HY, x1, HY + HPIC)
    rrect(d, x0, HY, x1, HY + HPIC, 6, outline=(60, 50, 40), width=1)
    banner(d, x0, HY + HPIC - 15, x1, hero["banner"], SANSB(8.5))
    chip(d, x0 + 6, HY + 6, hero["chip"], SANSB(7))
    txt(d, x0, HY + HPIC + 5, hero["kicker"], SANSB(8.5), RED)
    hl = wrap(d, hero["headline"], SERIFB(15), HW)
    para(d, x0, HY + HPIC + 19, hl, SERIFB(15), INK, 18)
    bl = wrap(d, hero["body"], SANS(10), HW)
    para(d, x0, HY + HPIC + 19 + len(hl) * 18 + 3, bl, SANS(10), (58, 52, 44), 12.5)
    fy = HY + HPIC + 19 + len(hl) * 18 + 3 + len(bl) * 12.5 + 5
    d.line([(sc(x0), sc(fy)), (sc(x1), sc(fy))], fill=RULE, width=sc(1))
    txt(d, x0, fy + 4, hero["foot"], SANSB(9), INK)

# ---------- small-card pictures ----------
def circ(x, y, r, fill, outline=None, width=1):
    d.ellipse(box(x - r, y - r, x + r, y + r), fill=fill,
              outline=outline, width=sc(width))

def brussels_pic(x0, y0, x1, y1):
    grad(d, x0, y0, x1, y1, (30, 58, 110), (47, 90, 158))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for k in range(12):
        a = math.radians(k * 30 - 90)
        circ(cx + 17 * math.cos(a), cy + 15 * math.sin(a), 2.2, GOLD)

def poland_pic(x0, y0, x1, y1):
    grad(d, x0, y0, x1, y1, (123, 160, 91), (74, 122, 58))
    d.line([(sc(x0 + 20), sc(y0 + 6)), (sc(x0 + 20), sc(y0 + 34))],
           fill=(90, 70, 50), width=sc(2))
    d.rectangle(box(x0 + 20, y0 + 6, x0 + 38, y0 + 14), fill=(255, 255, 255))
    d.rectangle(box(x0 + 20, y0 + 14, x0 + 38, y0 + 22), fill=RED)
    d.line([(sc(x1 - 30), sc(y0 + 8)), (sc(x1 - 62), sc(y0 + 34))],
           fill=(255, 140, 40), width=sc(3))
    circ(x1 - 62, y0 + 36, 6, (120, 120, 120))
    circ(x1 - 54, y0 + 30, 4, (150, 150, 150))

def antalya_pic(x0, y0, x1, y1):
    grad(d, x0, y0, x1, y1, (31, 122, 110), (15, 74, 68))
    circ(x0 + 24, y0 + 14, 9, (255, 210, 90))
    for k in range(3):
        yy = y1 - 16 + k * 6
        d.arc(box(x0 + 30, yy - 10, x1 - 20, yy + 10), 200, 340,
              fill=(220, 240, 235), width=sc(2))
    d.line([(sc(x1 - 46), sc(y0 + 8)), (sc(x1 - 16), sc(y0 + 38))],
           fill=RED, width=sc(3))

def mercury_pic(x0, y0, x1, y1):
    grad(d, x0, y0, x1, y1, (16, 16, 24), (42, 42, 58))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 2
    circ(cx, cy, 19, (168, 160, 148))
    circ(cx - 7, cy - 5, 4, (130, 122, 110))
    circ(cx + 6, cy + 6, 3, (140, 132, 120))
    circ(cx + 8, cy - 8, 2.5, (125, 118, 106))
    circ(x1 - 14, y0 + 10, 5, (255, 230, 160))
    for i in range(10):
        circ(x0 + hash01(i, 11) * (x1 - x0), y0 + hash01(i, 12) * (y1 - y0),
             0.9, (255, 255, 255))

def rome_pic(x0, y0, x1, y1):
    grad(d, x0, y0, x1, y1, (201, 123, 74), (138, 74, 40))
    for k in range(5):
        hx = x0 + 22 + k * 32
        circ(hx, y1 - 22, 6, (40, 26, 18))
        d.pieslice(box(hx - 11, y1 - 18, hx + 11, y1 + 6), 180, 360,
                   fill=(40, 26, 18))
    d.rectangle(box(x0 + 60, y0 + 8, x0 + 92, y0 + 20), fill=(250, 245, 230))
    d.line([(sc(x0 + 76), sc(y0 + 20)), (sc(x0 + 76), sc(y0 + 40))],
           fill=(60, 40, 24), width=sc(2))

def turkana_pic(x0, y0, x1, y1):
    grad(d, x0, y0, x1, y1, (217, 168, 92), (168, 116, 44))
    circ(x1 - 26, y0 + 12, 8, (255, 215, 120))
    d.line([(sc(x0 + 30), sc(y1 - 4)), (sc(x0 + 52), sc(y0 + 10))],
           fill=(60, 42, 22), width=sc(3))
    d.line([(sc(x0 + 74), sc(y1 - 4)), (sc(x0 + 52), sc(y0 + 10))],
           fill=(60, 42, 22), width=sc(3))
    d.line([(sc(x0 + 52), sc(y0 + 10)), (sc(x0 + 84), sc(y0 + 18))],
           fill=(60, 42, 22), width=sc(3))
    d.line([(sc(x0 + 30), sc(y1 - 12)), (sc(x0 + 74), sc(y1 - 12))],
           fill=(60, 42, 22), width=sc(2))

def sansalvador_pic(x0, y0, x1, y1):
    grad(d, x0, y0, x1, y1, (47, 106, 176), (30, 74, 128))
    cx = (x0 + x1) / 2
    d.polygon([(sc(cx - 8), sc(y0 + 6)), (sc(cx + 14), sc(y0 + 14)),
               (sc(cx + 6), sc(y0 + 24)), (sc(cx - 12), sc(y0 + 18))],
              fill=(250, 245, 230))
    rrect(d, cx - 26, y0 + 26, cx + 26, y1 - 4, 3, fill=(245, 240, 228))
    d.line([(sc(cx - 12), sc(y0 + 26)), (sc(cx + 12), sc(y0 + 26))],
           fill=(40, 40, 40), width=sc(2))

def cricket_pic(x0, y0, x1, y1):
    grad(d, x0, y0, x1, y1, (63, 138, 79), (31, 90, 46))
    for k in range(3):
        d.line([(sc(x0 + 26 + k * 6), sc(y1 - 22)), (sc(x0 + 26 + k * 6), sc(y1 - 6))],
               fill=(255, 220, 90), width=sc(2))
    d.polygon([(sc(x1 - 58), sc(y0 + 8)), (sc(x1 - 46), sc(y0 + 4)),
               (sc(x1 - 30), sc(y0 + 34)), (sc(x1 - 40), sc(y0 + 38))],
              fill=(150, 105, 60))
    circ(x1 - 24, y1 - 12, 6, (185, 40, 40), outline=(255, 255, 255), width=1)

def health_pic(x0, y0, x1, y1):
    grad(d, x0, y0, x1, y1, (238, 246, 242), (191, 224, 212))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d.ellipse(box(cx - 34, cy - 9, cx + 2, cy + 9), fill=(200, 60, 60))
    d.ellipse(box(cx - 2, cy - 9, cx + 34, cy + 9), fill=(250, 248, 244))
    d.ellipse(box(cx - 34, cy - 9, cx + 34, cy + 9), outline=(150, 60, 60), width=sc(1))
    for k, (px, py) in enumerate(((cx - 44, cy - 14), (cx + 40, cy + 12),
                                  (cx + 44, cy - 10))):
        circ(px, py, 2.5, (40, 140, 110))

def iraq_pic(x0, y0, x1, y1):
    grad(d, x0, y0, x1, y1, (217, 176, 106), (168, 126, 62))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d.polygon([(sc(cx), sc(cy - 18)), (sc(cx + 16), sc(cy - 10)),
               (sc(cx + 14), sc(cy + 12)), (sc(cx), sc(cy + 20)),
               (sc(cx - 14), sc(cy + 12)), (sc(cx - 16), sc(cy - 10))],
              outline=(90, 60, 30), width=sc(2))
    for k in range(5):
        a = math.radians(k * 72 - 90)
        a2 = math.radians(k * 72 - 90 + 36)
        d.line([(sc(cx), sc(cy)), (sc(cx + 8 * math.cos(a)), sc(cy + 8 * math.sin(a)))],
               fill=(90, 60, 30), width=sc(1))
    d.arc(box(x0 + 10, y1 - 16, x1 - 10, y1 + 6), 180, 360,
          fill=(150, 110, 55), width=sc(2))

cards = [
    (4, "BRUSSELS · DIPLOMACY", "UK and EU seal a 'reset' deal",
     "Food trade, youth visas, carbon link. (Reuters)",
     "RESET DEAL", "Reuters", brussels_pic),
    (5, "POLAND · SECURITY", "Russian missile lands in Polish field",
     "It fell in a field; two airports paused. (Reuters)",
     "FELL IN A FIELD", "Reuters", poland_pic),
    (6, "ANTALYA · CLIMATE", "COP31 ends last day with no deal",
     "The draft text leaves out fossil fuels. (UN News)",
     "NO DEAL", "UN News", antalya_pic),
    (7, "SPACE · MERCURY", "BepiColombo reaches Mercury after 8 years",
     "Orbit entry set for Saturday. (ESA, BBC)",
     "8 YEARS", "ESA · BBC", mercury_pic),
    (8, "ROME · LABOUR", "Italy hit by general strike",
     "Workers and students march. (CGIL)",
     "GENERAL STRIKE", "CGIL", rome_pic),
    (9, "TURKANA · ENERGY", "Kenya drills its first oil",
     "First crude due 1 December. (allAfrica)",
     "FIRST OIL", "allAfrica", turkana_pic),
    (10, "SAN SALVADOR · POLITICS", "Bukele files to run for third term",
     "The vote is on 28 February 2027. (AP)",
     "THIRD TERM", "AP", sansalvador_pic),
    (11, "CRICKET · OCEANIA", "Phillips hits 118 as NZ make 368",
     "NZ make 368 vs India. (ICC)",
     "118", "ICC", cricket_pic),
    (12, "HEALTH · TRIAL", "Cancer pill shrinks tumours in trial",
     "60.7% respond in trial. (Trial data)",
     "60.7% RESPOND", "Trial data", health_pic),
    (13, "CENTRAL IRAQ · SECURITY", "Iraqi army enters a militia stronghold",
     "Troops deploy to Jurf al-Sakhar. (Witnessed · Reuters)",
     "TROOPS DEPLOY", "Reuters", iraq_pic),
]

def num_badge(x, y, n, r=9):
    circ(x, y, r, RED, outline=(255, 255, 255), width=1)
    txt(d, x, y - 6.5, str(n), SANSB(8), (255, 255, 255), anchor="ma")

# number badges on hero pictures
for ci in range(3):
    hx1 = MX + ci * (HW + 10) + HW
    num_badge(hx1 - 14, HY + 14, ci + 1)

CARDR0, CARDR1 = 466, 580
CARDW = (CWID - 32) / 5
CARDH = 110
for idx, (n, kicker, headline, body, fact, src, painter) in enumerate(cards):
    row, col = divmod(idx, 5)
    cx0 = MX + col * (CARDW + 8)
    cy0 = CARDR0 if row == 0 else CARDR1
    cx1 = cx0 + CARDW
    painter(cx0, cy0, cx1, cy0 + 48)
    rrect(d, cx0, cy0, cx1, cy0 + 48, 5, outline=(60, 50, 40), width=1)
    banner(d, cx0, cy0 + 48 - 13, cx1, fact, SANSB(8))
    chip(d, cx0 + 5, cy0 + 5, src, SANSB(6.5))
    num_badge(cx1 - 12, cy0 + 12, n, r=8)
    txt(d, cx0, cy0 + 52, kicker, SANSB(7.5), RED)
    hl = wrap(d, headline, SERIFB(10.5), CARDW)
    by = para(d, cx0, cy0 + 62, hl, SERIFB(10.5), INK, 12.5)
    bl = wrap(d, body, SANS(8.5), CARDW)
    para(d, cx0, by + 2, bl, SANS(8.5), (58, 52, 44), 10.5)

# ---------- map + list ----------
MAPX0, MAPY0, MAPX1, MAPY1 = MX, 694, 608, 948
grad(d, MAPX0, MAPY0, MAPX1, MAPY1, NAVY_TOP, NAVY_BOT)
rrect(d, MAPX0, MAPY0, MAPX1, MAPY1, 6, outline=(60, 50, 40), width=1)
mw, mh = MAPX1 - MAPX0, MAPY1 - MAPY0
for gx in range(1, 5):
    d.line([(sc(MAPX0 + gx * mw / 5), sc(MAPY0)), (sc(MAPX0 + gx * mw / 5), sc(MAPY1))],
           fill=(28, 50, 74), width=sc(1))
for gy in range(1, 4):
    d.line([(sc(MAPX0), sc(MAPY0 + gy * mh / 4)), (sc(MAPX1), sc(MAPY0 + gy * mh / 4))],
           fill=(28, 50, 74), width=sc(1))
# Real world coastlines: Natural Earth 110m land, Douglas-Peucker simplified
# (tol 1.5 deg), equirectangular lon -180..180 -> panel width,
# lat 90..-60 -> panel height (Antarctica cropped). 93 polygons, 657 pts.
continents = [
    [(0.312, 0.959), (0.319, 0.965), (0.308, 0.970), (0.293, 0.952), (0.312, 0.959)],
    [(0.337, 0.941), (0.330, 0.946), (0.337, 0.941)],
    [(0.695, 0.931), (0.691, 0.924), (0.695, 0.931)],
    [(0.904, 0.872), (0.912, 0.873), (0.911, 0.888), (0.906, 0.890), (0.904, 0.872)],
    [(0.981, 0.873), (0.981, 0.892), (0.963, 0.908), (0.981, 0.873)],
    [(0.985, 0.841), (0.996, 0.851), (0.987, 0.878), (0.980, 0.830), (0.985, 0.841)],
    [(0.964, 0.748), (0.956, 0.734), (0.964, 0.748)],
    [(0.639, 0.690), (0.631, 0.766), (0.622, 0.767), (0.623, 0.708), (0.637, 0.680), (0.639, 0.690)],
    [(0.899, 0.692), (0.925, 0.774), (0.917, 0.850), (0.891, 0.853), (0.884, 0.829), (0.880, 0.835), (0.883, 0.819), (0.878, 0.833), (0.865, 0.810), (0.820, 0.828), (0.817, 0.745), (0.836, 0.731), (0.849, 0.695), (0.860, 0.700), (0.868, 0.674), (0.879, 0.679), (0.876, 0.700), (0.889, 0.718), (0.896, 0.671), (0.899, 0.692)],
    [(0.835, 0.668), (0.830, 0.664), (0.835, 0.668)],
    [(0.949, 0.664), (0.946, 0.655), (0.949, 0.664)],
    [(0.846, 0.668), (0.854, 0.656), (0.846, 0.668)],
    [(0.841, 0.654), (0.833, 0.659), (0.841, 0.654)],
    [(0.944, 0.656), (0.939, 0.649), (0.944, 0.656)],
    [(0.802, 0.645), (0.821, 0.656), (0.793, 0.646), (0.802, 0.645)],
    [(0.933, 0.645), (0.929, 0.634), (0.933, 0.645)],
    [(0.922, 0.637), (0.912, 0.638), (0.922, 0.637)],
    [(0.862, 0.621), (0.855, 0.623), (0.862, 0.621)],
    [(0.925, 0.630), (0.919, 0.618), (0.925, 0.630)],
    [(0.873, 0.608), (0.876, 0.622), (0.884, 0.611), (0.902, 0.626), (0.919, 0.671), (0.902, 0.651), (0.882, 0.656), (0.883, 0.636), (0.863, 0.606), (0.873, 0.608)],
    [(0.848, 0.591), (0.834, 0.598), (0.843, 0.604), (0.838, 0.613), (0.842, 0.636), (0.836, 0.618), (0.832, 0.636), (0.833, 0.596), (0.848, 0.591)],
    [(0.857, 0.592), (0.856, 0.606), (0.857, 0.592)],
    [(0.794, 0.639), (0.765, 0.563), (0.788, 0.599), (0.794, 0.639)],
    [(0.827, 0.588), (0.823, 0.627), (0.806, 0.620), (0.803, 0.603), (0.824, 0.554), (0.831, 0.564), (0.827, 0.588)],
    [(0.851, 0.544), (0.848, 0.563), (0.839, 0.552), (0.848, 0.535), (0.851, 0.544)],
    [(0.726, 0.559), (0.723, 0.535), (0.726, 0.559)],
    [(0.844, 0.531), (0.840, 0.535), (0.844, 0.531)],
    [(0.829, 0.538), (0.825, 0.544), (0.832, 0.524), (0.829, 0.538)],
    [(0.849, 0.519), (0.847, 0.532), (0.849, 0.519)],
    [(0.837, 0.477), (0.845, 0.516), (0.834, 0.500), (0.837, 0.477)],
    [(0.318, 0.478), (0.313, 0.478), (0.318, 0.478)],
    [(0.298, 0.468), (0.310, 0.476), (0.293, 0.478), (0.298, 0.468)],
    [(0.806, 0.475), (0.802, 0.471), (0.806, 0.475)],
    [(0.279, 0.448), (0.294, 0.465), (0.264, 0.454), (0.279, 0.448)],
    [(0.285, 0.442), (0.283, 0.432), (0.285, 0.442)],
    [(0.837, 0.448), (0.835, 0.454), (0.834, 0.443), (0.837, 0.431), (0.837, 0.448)],
    [(0.874, 0.372), (0.868, 0.380), (0.874, 0.372)],
    [(0.596, 0.362), (0.590, 0.366), (0.596, 0.362)],
    [(0.566, 0.362), (0.573, 0.365), (0.566, 0.362)],
    [(0.543, 0.345), (0.535, 0.349), (0.543, 0.345)],
    [(0.526, 0.325), (0.524, 0.341), (0.526, 0.325)],
    [(0.874, 0.372), (0.873, 0.379), (0.868, 0.380), (0.869, 0.373), (0.874, 0.372)],
    [(0.892, 0.352), (0.890, 0.366), (0.881, 0.369), (0.877, 0.377), (0.875, 0.369), (0.864, 0.374), (0.867, 0.379), (0.865, 0.390), (0.862, 0.391), (0.862, 0.385), (0.859, 0.378), (0.868, 0.364), (0.877, 0.363), (0.880, 0.351), (0.882, 0.354), (0.887, 0.345), (0.889, 0.330), (0.893, 0.324), (0.894, 0.339), (0.892, 0.352)],
    [(0.900, 0.306), (0.904, 0.304), (0.904, 0.312), (0.898, 0.320), (0.893, 0.315), (0.892, 0.323), (0.889, 0.323), (0.888, 0.316), (0.893, 0.311), (0.894, 0.296), (0.900, 0.306)],
    [(0.900, 0.306), (0.904, 0.312), (0.889, 0.323), (0.894, 0.296), (0.900, 0.306)],
    [(0.323, 0.290), (0.328, 0.290), (0.323, 0.290)],
    [(0.328, 0.273), (0.321, 0.268), (0.328, 0.273)],
    [(0.157, 0.277), (0.143, 0.262), (0.157, 0.277)],
    [(0.344, 0.262), (0.353, 0.289), (0.335, 0.283), (0.344, 0.262)],
    [(0.131, 0.240), (0.136, 0.252), (0.131, 0.240)],
    [(0.899, 0.262), (0.902, 0.273), (0.895, 0.294), (0.895, 0.238), (0.899, 0.262)],
    [(0.481, 0.252), (0.472, 0.255), (0.473, 0.241), (0.481, 0.232), (0.481, 0.252)],
    [(0.535, 0.229), (0.530, 0.228), (0.535, 0.229)],
    [(0.075, 0.219), (0.070, 0.217), (0.075, 0.219)],
    [(0.492, 0.209), (0.504, 0.258), (0.485, 0.267), (0.492, 0.240), (0.483, 0.221), (0.492, 0.209)],
    [(0.040, 0.201), (0.035, 0.199), (0.040, 0.201)],
    [(0.273, 0.182), (0.267, 0.184), (0.273, 0.182)],
    [(0.023, 0.175), (0.031, 0.178), (0.023, 0.175)],
    [(0.263, 0.162), (0.277, 0.175), (0.258, 0.176), (0.263, 0.162)],
    [(0.460, 0.157), (0.462, 0.166), (0.448, 0.177), (0.432, 0.163), (0.460, 0.157)],
    [(0.014, 0.156), (0.028, 0.160), (0.000, 0.167), (0.000, 0.140), (0.014, 0.156)],
    [(0.234, 0.139), (0.223, 0.137), (0.234, 0.139)],
    [(0.248, 0.137), (0.257, 0.152), (0.262, 0.134), (0.270, 0.136), (0.274, 0.149), (0.241, 0.187), (0.237, 0.207), (0.244, 0.219), (0.271, 0.232), (0.278, 0.259), (0.278, 0.236), (0.287, 0.223), (0.283, 0.185), (0.295, 0.184), (0.312, 0.212), (0.321, 0.198), (0.345, 0.252), (0.316, 0.265), (0.302, 0.288), (0.319, 0.272), (0.321, 0.292), (0.334, 0.294), (0.318, 0.310), (0.321, 0.298), (0.314, 0.299), (0.289, 0.352), (0.288, 0.339), (0.290, 0.363), (0.274, 0.390), (0.277, 0.432), (0.266, 0.399), (0.232, 0.411), (0.233, 0.471), (0.244, 0.475), (0.258, 0.456), (0.253, 0.494), (0.268, 0.498), (0.267, 0.526), (0.274, 0.541), (0.287, 0.542), (0.301, 0.517), (0.301, 0.540), (0.306, 0.519), (0.328, 0.529), (0.341, 0.560), (0.357, 0.572), (0.360, 0.601), (0.389, 0.619), (0.404, 0.649), (0.386, 0.746), (0.368, 0.766), (0.351, 0.829), (0.338, 0.826), (0.342, 0.846), (0.319, 0.874), (0.324, 0.884), (0.313, 0.904), (0.317, 0.921), (0.303, 0.959), (0.292, 0.948), (0.290, 0.911), (0.298, 0.883), (0.294, 0.888), (0.305, 0.732), (0.274, 0.641), (0.275, 0.607), (0.286, 0.574), (0.283, 0.545), (0.275, 0.552), (0.257, 0.511), (0.212, 0.478), (0.181, 0.388), (0.196, 0.445), (0.188, 0.435), (0.154, 0.331), (0.154, 0.279), (0.159, 0.286), (0.159, 0.273), (0.128, 0.213), (0.091, 0.194), (0.079, 0.206), (0.082, 0.191), (0.042, 0.237), (0.064, 0.207), (0.050, 0.209), (0.039, 0.190), (0.053, 0.168), (0.033, 0.162), (0.051, 0.159), (0.037, 0.144), (0.065, 0.124), (0.198, 0.151), (0.233, 0.151), (0.238, 0.140), (0.232, 0.133), (0.236, 0.121), (0.248, 0.137)],
    [(0.183, 0.113), (0.204, 0.113), (0.219, 0.136), (0.185, 0.143), (0.174, 0.134), (0.188, 0.131), (0.168, 0.123), (0.183, 0.113)],
    [(0.210, 0.111), (0.203, 0.110), (0.210, 0.111)],
    [(0.288, 0.113), (0.275, 0.111), (0.288, 0.113)],
    [(0.260, 0.112), (0.299, 0.123), (0.328, 0.154), (0.322, 0.167), (0.311, 0.158), (0.320, 0.177), (0.309, 0.175), (0.316, 0.187), (0.284, 0.172), (0.297, 0.148), (0.250, 0.125), (0.260, 0.112)],
    [(0.221, 0.108), (0.231, 0.122), (0.215, 0.117), (0.221, 0.108)],
    [(0.899, 0.112), (0.889, 0.111), (0.899, 0.112)],
    [(0.241, 0.115), (0.233, 0.110), (0.249, 0.108), (0.241, 0.115)],
    [(0.165, 0.124), (0.150, 0.121), (0.153, 0.105), (0.179, 0.110), (0.165, 0.124)],
    [(0.919, 0.099), (0.906, 0.099), (0.919, 0.099)],
    [(0.240, 0.100), (0.231, 0.100), (0.240, 0.100)],
    [(0.903, 0.096), (0.880, 0.098), (0.903, 0.096)],
    [(0.226, 0.089), (0.227, 0.100), (0.215, 0.096), (0.226, 0.089)],
    [(0.199, 0.092), (0.206, 0.097), (0.173, 0.099), (0.199, 0.092)],
    [(0.660, 0.129), (0.643, 0.120), (0.655, 0.099), (0.691, 0.090), (0.662, 0.105), (0.654, 0.118), (0.660, 0.129)],
    [(0.237, 0.086), (0.278, 0.101), (0.230, 0.088), (0.237, 0.086)],
    [(0.177, 0.082), (0.159, 0.093), (0.177, 0.082)],
    [(0.797, 0.087), (0.817, 0.094), (0.804, 0.105), (0.853, 0.110), (0.865, 0.128), (0.890, 0.114), (0.971, 0.142), (0.988, 0.134), (1.000, 0.140), (1.000, 0.167), (0.993, 0.169), (0.998, 0.185), (0.954, 0.201), (0.950, 0.234), (0.936, 0.260), (0.933, 0.222), (0.957, 0.183), (0.935, 0.190), (0.931, 0.206), (0.895, 0.206), (0.875, 0.235), (0.893, 0.252), (0.884, 0.291), (0.854, 0.335), (0.859, 0.366), (0.851, 0.371), (0.848, 0.336), (0.836, 0.341), (0.838, 0.327), (0.828, 0.339), (0.840, 0.350), (0.831, 0.367), (0.838, 0.412), (0.822, 0.448), (0.794, 0.468), (0.804, 0.510), (0.792, 0.543), (0.778, 0.511), (0.776, 0.538), (0.790, 0.591), (0.773, 0.548), (0.770, 0.487), (0.762, 0.493), (0.754, 0.448), (0.723, 0.494), (0.715, 0.547), (0.702, 0.458), (0.696, 0.461), (0.684, 0.430), (0.659, 0.428), (0.633, 0.400), (0.644, 0.440), (0.657, 0.424), (0.666, 0.451), (0.654, 0.485), (0.621, 0.516), (0.597, 0.403), (0.594, 0.416), (0.590, 0.401), (0.619, 0.522), (0.642, 0.529), (0.609, 0.631), (0.613, 0.698), (0.597, 0.732), (0.599, 0.758), (0.589, 0.792), (0.572, 0.826), (0.551, 0.828), (0.533, 0.720), (0.538, 0.672), (0.524, 0.607), (0.526, 0.575), (0.512, 0.558), (0.475, 0.568), (0.454, 0.519), (0.453, 0.454), (0.484, 0.362), (0.526, 0.351), (0.529, 0.375), (0.553, 0.398), (0.560, 0.381), (0.594, 0.394), (0.600, 0.356), (0.577, 0.356), (0.573, 0.337), (0.616, 0.320), (0.602, 0.298), (0.609, 0.285), (0.594, 0.304), (0.585, 0.289), (0.577, 0.316), (0.580, 0.326), (0.563, 0.332), (0.567, 0.349), (0.562, 0.357), (0.554, 0.322), (0.537, 0.295), (0.535, 0.306), (0.551, 0.332), (0.545, 0.347), (0.525, 0.304), (0.509, 0.313), (0.494, 0.356), (0.475, 0.354), (0.474, 0.313), (0.496, 0.307), (0.487, 0.275), (0.523, 0.243), (0.524, 0.219), (0.529, 0.215), (0.530, 0.240), (0.555, 0.237), (0.560, 0.217), (0.567, 0.220), (0.565, 0.205), (0.581, 0.200), (0.559, 0.195), (0.560, 0.179), (0.571, 0.166), (0.562, 0.162), (0.550, 0.182), (0.552, 0.199), (0.544, 0.226), (0.536, 0.231), (0.529, 0.204), (0.516, 0.209), (0.514, 0.187), (0.568, 0.126), (0.614, 0.150), (0.592, 0.156), (0.603, 0.174), (0.622, 0.160), (0.621, 0.143), (0.629, 0.156), (0.668, 0.134), (0.690, 0.146), (0.685, 0.126), (0.702, 0.115), (0.701, 0.159), (0.708, 0.148), (0.703, 0.124), (0.707, 0.114), (0.726, 0.122), (0.724, 0.109), (0.742, 0.099), (0.797, 0.087)],
    [(0.636, 0.325), (0.637, 0.349), (0.650, 0.354), (0.646, 0.333), (0.652, 0.327), (0.640, 0.303), (0.647, 0.288), (0.630, 0.303), (0.636, 0.325)],
    [(0.239, 0.083), (0.232, 0.081), (0.239, 0.083)],
    [(0.194, 0.082), (0.185, 0.082), (0.194, 0.082)],
    [(0.569, 0.081), (0.558, 0.082), (0.569, 0.081)],
    [(0.195, 0.076), (0.187, 0.077), (0.195, 0.076)],
    [(0.234, 0.080), (0.226, 0.074), (0.234, 0.080)],
    [(0.222, 0.078), (0.207, 0.071), (0.222, 0.078)],
    [(0.792, 0.078), (0.776, 0.081), (0.792, 0.078)],
    [(0.551, 0.069), (0.560, 0.074), (0.544, 0.088), (0.529, 0.069), (0.551, 0.069)],
    [(0.571, 0.064), (0.576, 0.066), (0.548, 0.065), (0.571, 0.064)],
    [(0.642, 0.063), (0.625, 0.063), (0.642, 0.063)],
    [(0.778, 0.074), (0.753, 0.064), (0.767, 0.058), (0.778, 0.074)],
    [(0.258, 0.069), (0.248, 0.079), (0.231, 0.066), (0.258, 0.069)],
    [(0.310, 0.046), (0.328, 0.049), (0.286, 0.071), (0.291, 0.076), (0.276, 0.092), (0.251, 0.090), (0.264, 0.083), (0.256, 0.078), (0.264, 0.071), (0.259, 0.065), (0.273, 0.064), (0.246, 0.054), (0.310, 0.046)],
    [(0.425, 0.043), (0.442, 0.048), (0.411, 0.052), (0.466, 0.058), (0.444, 0.065), (0.451, 0.066), (0.445, 0.075), (0.449, 0.087), (0.440, 0.089), (0.446, 0.105), (0.431, 0.118), (0.440, 0.129), (0.427, 0.132), (0.438, 0.132), (0.389, 0.164), (0.380, 0.199), (0.357, 0.176), (0.350, 0.152), (0.359, 0.134), (0.348, 0.136), (0.357, 0.130), (0.345, 0.122), (0.337, 0.097), (0.296, 0.080), (0.326, 0.055), (0.425, 0.043)],
]
for poly in continents:
    pts = [(MAPX0 + fx * mw, MAPY0 + fy * mh) for fx, fy in poly]
    d.polygon([(sc(px), sc(py)) for px, py in pts], fill=LAND)
    d.line([(sc(px), sc(py)) for px, py in pts] + [(sc(pts[0][0]), sc(pts[0][1]))],
           fill=COAST, width=sc(1))
txt(d, MAPX0 + 10, MAPY0 + 7, "WORLD MAP — ONE PIN PER STORY", SANSB(8),
    (220, 228, 238))
rrect(d, MAPX1 - 148, MAPY0 + 5, MAPX1 - 8, MAPY0 + 19, 6, fill=GOLD)
txt(d, MAPX1 - 78, MAPY0 + 7.5, "7 · SPACE — Mercury", SANSB(8), (20, 20, 20),
    anchor="ma")
# Pins by lat/lon (equirectangular, same projection as the coastlines);
# a few nudged a couple of px in dense clusters so numbers stay readable.
# 12 (health trial) has no fixed place and keeps its old spot.
pins = {1: (0.59, 0.264), 2: (0.736, 0.472), 3: (0.836, 0.44), 4: (0.517, 0.261),
        5: (0.564, 0.253), 6: (0.582, 0.354), 8: (0.54, 0.332), 9: (0.6, 0.58),
        10: (0.252, 0.505), 11: (0.987, 0.875), 12: (0.18, 0.16), 13: (0.623, 0.383),
        14: (0.888, 0.362), 15: (0.853, 0.35), 16: (0.823, 0.334),
        17: (0.537, 0.25), 18: (0.286, 0.341), 19: (0.63, 0.435),
        20: (0.569, 0.204), 21: (0.521, 0.54), 22: (0.918, 0.826),
        23: (0.591, 0.402), 24: (0.714, 0.409), 25: (0.338, 0.831),
        26: (0.9, 0.835), 27: (0.562, 0.299), 28: (0.604, 0.362),
        29: (0.579, 0.523), 30: (0.594, 0.693), 31: (0.489, 0.564),
        32: (0.18, 0.359), 33: (0.493, 0.257), 34: (0.891, 0.319),
        35: (0.519, 0.307)}
for n, (fx, fy) in sorted(pins.items()):
    px, py = MAPX0 + fx * mw, MAPY0 + fy * mh
    circ(px, py, 6, RED, outline=(255, 255, 255), width=1)
    txt(d, px, py - 5, str(n), SANSB(6.5), (255, 255, 255), anchor="ma")

# ---------- also-on-friday list ----------
LX = 620
txt(d, LX, 694, "ALSO ON FRIDAY 20 NOVEMBER — 22 MORE STORIES", SANSB(9.5), INK)
more = [
    (14, "Japan inflation 2.3%, core 2.2%; Dec rate rise in view. (Reuters)"),
    (15, "Seoul ruling party moves to impeach top judge. (Korea Herald)"),
    (16, "Beijing: China holds loan rates for an 18th month. (Xinhua)"),
    (17, "Berlin: School pupils strike against military service. (Al Jazeera)"),
    (18, "Washington: Democrats query law firm over free work. (Al Jazeera)"),
    (19, "Houthi missile damages Riyadh's tallest tower, no injuries."),
    (20, "Estonia to shut Russia border from 1 Dec, for at least 6 months."),
    (21, "Abuja: Court bars new evidence against Tinubu. (Channels TV)"),
    (22, "Sydney: Australian shares fall 1.8% in the sell-off. (Reuters)"),
    (23, "Gaza: Israeli strikes kill 6 despite truce."),
    (24, "Pakistani minister visits New Delhi, first since May 2025. (PTI)"),
    (25, "Argentina country risk jumps to 1,070, up 15%. (JPM)"),
    (26, 'Australia: Xi hails "full turnaround" in China ties.'),
    (27, "Lviv railway station strike kills 2. (BBC)"),
    (28, "Lebanon: Israeli strikes hit south and east. (Anadolu)"),
    (29, "Sudan army claims gains in West Kordofan."),
    (30, "Malawi fuel crisis brings night-long petrol queues. (Al Jazeera)"),
    (31, "AfDB: 22 African states near debt distress. (allAfrica)"),
    (32, "Russell fastest in wet Grand Prix practice. (Autosport)"),
    (33, "London: General says UK runs cyber attacks abroad. (Sky News)"),
    (34, "Tokyo: SoftBank shares fall 14% in a day. (Al Jazeera)"),
    (35, "Turin: ATP backs plan to lift player pay past $350m. (Anadolu)"),
]
cols = [(LX, 186, more[:11]), (812, 184, more[11:])]
for colx, colw, items in cols:
    y = 712
    for n, text in items:
        txt(d, colx, y, str(n), SANSB(8.5), RED)
        lines = wrap(d, text, SANS(8.5), colw - 18)
        para(d, colx + 18, y, lines, SANS(8.5), INK, 10.5)
        y += len(lines) * 10.5 + 1

# ---------- date check + footer ----------
DCY, DCH = 954, 37
rrect(d, MX, DCY, RX, DCY + DCH, 4, fill=(250, 247, 238),
      outline=RED, width=1)
dc_text = ("DATE CHECK — WHAT WE LEFT OUT.  Left out as Thursday 19 November's news: "
           "World Court's ruling on Myanmar · three-leader declaration in Shenzhen · "
           "Tonga drought emergency · Anthropic $83 IPO pricing · GTA VI's midnight launch · "
           "Senate's 48-51 Iran war-powers vote.  Older still: the $190.4m Van Gogh sale "
           "(Wed 18) · Voyager 1's one light-day confirmation.  Not yet happened, so not shown: "
           "BepiColombo's Mercury orbit entry · COP31 final text · ATP Finals final.")
dc_lines = wrap(d, dc_text, SANS(8.5), CWID - 16)
para(d, MX + 8, DCY + 2.5, dc_lines, SANS(8.5), INK, 11)
txt(d, W / 2, 995,
    "Every story here happened, or was first reported, on Friday 20 November 2026. "
    "Officials' counts are attributed.", SANS(8), MUTED, anchor="ma")
txt(d, W / 2, 1005,
    "Sources: Reuters, AP, AFP, BBC, Al Jazeera, Kyiv Independent, IMD, Deccan Herald, "
    "ESA, UN News — original vector drawings.", SANS(8), MUTED, anchor="ma")

# ---------- downscale, grain, save ----------
small = img.resize((W, H), Image.LANCZOS)
arr = np.asarray(small).astype(np.int16)
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
# smooth low-frequency mottle (compressible) + sparse fine grain
mottle = (np.sin(xs * 0.021 + ys * 0.017) * 5.0
          + np.sin(xs * 0.011 - ys * 0.023 + 1.7) * 4.0
          + np.sin(xs * 0.043 - ys * 0.031 + 0.6) * 3.0)
frac = (np.sin(xs * 12.9898 + ys * 78.233) * 43758.5453) % 1.0
h2 = (np.sin(xs * 26.651 + ys * 11.135) * 24634.6345) % 1.0
fine = np.where(h2 > 0.7, (frac - 0.5) * 4.0, 0.0)
noise = (mottle + fine).astype(np.int16)
arr = np.clip(arr + noise[:, :, None], 0, 255).astype(np.uint8)
out = Image.fromarray(arr, "RGB")
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
out.save(out_path, optimize=True)
print("saved", out_path, os.path.getsize(out_path), "bytes")
