#!/usr/bin/env python3
"""The World Today - the world news of Tuesday 17 November 2026 in one image.

A newspaper front page drawn from scratch in pure Python (standard library
only): a 1024x1024 PNG with a masthead, six illustrated news panels and a
ticker of the day's other stories. Every pixel is computed from fixed
constants, so the program is fully deterministic: two runs write the same
bytes. No network, no clock, no randomness.

Stories, all reported on 17 November 2026 (checked against live reporting):
  1. Ukraine strikes the Kerch Bridge - a road span collapses, rail damaged.
  2. Iran fires drones at a US radar in Bahrain; the US hits back on Qeshm
     Island; tankers are hit in and near the Strait of Hormuz.
  3. Donald Trump lands in Manila for the ASEAN-US summit and Quad talks.
  4. Nvidia beats Q3 expectations: revenue $115.8bn, up 103%, and guides
     $130bn for Q4 - its first report since Jensen Huang resigned.
  5. ULA's first account of the Vulcan failure: its first stage faltered
     just after liftoff; 40 Amazon Leo satellites lost.
  6. A JPMorgan software bug slows transactions at US banks (reported
     Tuesday; the bank says it is not a cyberattack).
Ticker: Japan scrambles jets over Russian aircraft; the UK sanctions
settlement builders; Houthi forces advance in Yemen.

Usage: python3 main.py [output-path]
Default output is /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
"""

import math
import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
PAPER = (246, 241, 229)      # cream newsprint
CARD = (255, 253, 246)       # panel card
INK = (25, 25, 25)           # near-black ink
GREY = (90, 86, 76)          # caption grey
RED = (178, 35, 27)          # headline red / section tags
RULE = (25, 25, 25)
SKY = (168, 200, 224)
SKY2 = (203, 222, 235)
SEA = (46, 95, 138)
SEA2 = (30, 74, 112)
WHITE = (255, 255, 255)
SUN = (242, 196, 90)
ORANGE = (232, 116, 34)
FLAME = (244, 180, 44)
SMOKE = (120, 118, 112)
DARK = (52, 52, 52)
STEEL = (96, 104, 110)
GREEN = (34, 139, 76)
DGREEN = (18, 64, 38)
GOLD = (212, 175, 55)
TEAL = (38, 120, 124)


# ---------------------------------------------------------------------------
# 5x7 bitmap font (uppercase, digits, punctuation). Each glyph is 7 rows of
# 5 bits, most significant bit on the left. Written out by hand.
# ---------------------------------------------------------------------------
def _g(*rows):
    return rows


FONT = {
    "A": _g(0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": _g(0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": _g(0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": _g(0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": _g(0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": _g(0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": _g(0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": _g(0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": _g(0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": _g(0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": _g(0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": _g(0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": _g(0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": _g(0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": _g(0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": _g(0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": _g(0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": _g(0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": _g(0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": _g(0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": _g(0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": _g(0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": _g(0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": _g(0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": _g(0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": _g(0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": _g(0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": _g(0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": _g(0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": _g(0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": _g(0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": _g(0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": _g(0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": _g(0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": _g(0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": _g(0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": _g(0, 0, 0, 0, 0, 0, 0),
    ".": _g(0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": _g(0, 0, 0, 0, 0x0C, 0x04, 0x08),
    "'": _g(0x04, 0x04, 0x08, 0, 0, 0, 0),
    "!": _g(0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": _g(0x0E, 0x11, 0x01, 0x06, 0x04, 0, 0x04),
    "-": _g(0, 0, 0, 0x0E, 0, 0, 0),
    "/": _g(0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "(": _g(0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": _g(0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "%": _g(0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "&": _g(0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "$": _g(0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "+": _g(0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "=": _g(0, 0, 0x1F, 0, 0x1F, 0, 0),
    '"': _g(0x0A, 0x0A, 0, 0, 0, 0, 0),
    ":": _g(0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": _g(0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "*": _g(0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    ":": _g(0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    "_": _g(0, 0, 0, 0, 0, 0, 0x1F),
    "[": _g(0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    "]": _g(0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    "<": _g(0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    ">": _g(0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    "\u2022": _g(0, 0, 0, 0x0E, 0x0E, 0, 0),   # bullet
    "\u2014": _g(0, 0, 0, 0x1F, 0, 0, 0),   # em dash
    "\u2019": _g(0x04, 0x04, 0x08, 0, 0, 0, 0),
}

SPACE_W = 6  # glyph advance in font units (5 px glyph + 1 px gap)


def text_width(s, scale):
    """Width in pixels of string s rendered at scale."""
    return len(s) * SPACE_W * scale - scale


def wrap_text(s, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.buf), 3):
            self.buf[i] = r
            self.buf[i + 1] = g
            self.buf[i + 2] = b

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = c
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i] = r
                self.buf[i + 1] = g
                self.buf[i + 2] = b

    def hline(self, x, y, length, c):
        self.rect(x, y, length, 1, c)

    def vline(self, x, y, length, c):
        self.rect(x, y, 1, length, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self.hline(cx - dx, cy + dy, 2 * dx + 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * math.sqrt(max(0.0, t)))
            self.hline(cx - dx, cy + dy, 2 * dx + 1, c)

    def ring(self, cx, cy, r, thick, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            dx2 = int(math.sqrt(max(0, (r - thick) * (r - thick) - dy * dy))) \
                if abs(dy) < r - thick else 0
            self.hline(cx - dx, cy + dy, dx - dx2 + 1, c)
            self.hline(cx + dx2, cy + dy, dx - dx2 + 1, c)

    def polygon(self, pts, c):
        """Scanline fill of a simple polygon (list of (x, y))."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    if y1 != y0:
                        x = x0 + (y - y0) * (x1 - x0) / float(y1 - y0)
                        xs.append(x)
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.hline(int(xs[k]), y, int(xs[k + 1]) - int(xs[k]) + 1, c)

    def burst(self, cx, cy, r_outer, r_inner, spikes, c):
        """Star burst (explosion) with a fixed number of spikes."""
        pts = []
        for i in range(spikes * 2):
            ang = math.pi * i / spikes - math.pi / 2
            r = r_outer if i % 2 == 0 else r_inner
            pts.append((int(cx + r * math.cos(ang)),
                        int(cy + r * math.sin(ang))))
        self.polygon(pts, c)

    def text(self, x, y, s, scale, c):
        """Draw text at (x, y) top-left; returns width drawn."""
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                cx += SPACE_W * scale
                continue
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += SPACE_W * scale
        return cx - x

    def text_centred(self, cx, y, s, scale, c):
        w = text_width(s, scale)
        return self.text(cx - w // 2, y, s, scale, c)

# ---------------------------------------------------------------------------
# Scenes. Each draws into the box (x, y, w, h) on the canvas.
# ---------------------------------------------------------------------------

def _sky(cv, x, y, w, h, top, mid, bot):
    """Three flat sky bands (reads as a sky, compresses well)."""
    cv.rect(x, y, w, h // 3, top)
    cv.rect(x, y + h // 3, w, h // 3, mid)
    cv.rect(x, y + 2 * h // 3, w, h - 2 * h // 3, bot)


def _sea(cv, x, y, w, h, c1, c2):
    cv.rect(x, y, w, h // 2, c1)
    cv.rect(x, y + h // 2, w, h - h // 2, c2)


def _waves(cv, x, y, w, h, positions, c=WHITE):
    for (fx, fy, ln) in positions:
        cv.hline(x + int(w * fx), y + int(h * fy), ln, c)


def _label_strip(cv, x, y, w, s):
    """Dark location strip at the bottom of a scene."""
    cv.rect(x, y, w, 16, INK)
    cv.text(x + 6, y + 4, s, 2, WHITE)


def scene_kerch(cv, x, y, w, h, strip=True):
    _sky(cv, x, y, w, h, (168, 200, 224), (196, 216, 232), (224, 234, 240))
    hy = y + int(h * 0.62)
    _sea(cv, x, hy, w, y + h - hy, SEA, SEA2)
    # sun and clouds
    cv.circle(x + 52, y + 26, 15, SUN)
    cv.ellipse(x + 150, y + 22, 34, 9, WHITE)
    cv.ellipse(x + 170, y + 30, 26, 8, WHITE)
    cv.ellipse(x + w - 120, y + 16, 30, 8, WHITE)
    # bridge deck: left span, then the break, then a sagging right span
    dy = y + int(h * 0.44)
    bx = x + int(w * 0.58)
    cv.rect(x, dy, bx - x, 8, DARK)
    cv.rect(bx + 64, dy + 10, x + w - (bx + 64), 8, DARK)
    # arch over the left span
    ax, ar = x + int(w * 0.28), 36
    for deg in range(0, 181, 6):
        a = math.radians(180 - deg)
        px = int(ax + ar * math.cos(a))
        py = int(dy - ar * math.sin(a))
        cv.circle(px, py, 5, STEEL)
    # deck pylons down into the sea
    for fx in (0.12, 0.30, 0.46):
        px = x + int(w * fx)
        cv.rect(px - 3, dy + 8, 6, hy - dy - 8, STEEL)
    # collapsed span: a slab tipped down into the water at the break
    cv.polygon([(bx, dy), (bx + 58, dy + 12), (bx + 44, dy + 52),
                (bx - 4, dy + 34)], (64, 64, 64))
    cv.polygon([(bx + 44, dy + 52), (bx + 58, dy + 12), (bx + 66, dy + 20),
                (bx + 52, dy + 58)], (40, 40, 40))
    # splash where the span meets the water
    cv.circle(bx + 40, hy + 6, 12, WHITE)
    cv.circle(bx + 58, hy + 8, 9, WHITE)
    # explosion at the break
    cv.burst(bx + 8, dy - 8, 30, 16, 10, ORANGE)
    cv.burst(bx + 8, dy - 8, 19, 10, 8, FLAME)
    cv.circle(bx + 8, dy - 8, 8, (255, 236, 160))
    # smoke drifting up
    cv.circle(bx - 6, dy - 34, 12, SMOKE)
    cv.circle(bx + 14, dy - 44, 14, SMOKE)
    cv.circle(bx + 34, dy - 30, 10, SMOKE)
    _waves(cv, x, hy, w, y + h - hy,
           [(0.08, 0.35, 26), (0.30, 0.65, 34), (0.55, 0.30, 22),
            (0.72, 0.70, 30), (0.88, 0.40, 24)])
    if strip:
        _label_strip(cv, x, y + h - 16, w, "THE KERCH BRIDGE, CRIMEA")


def scene_manila(cv, x, y, w, h, strip=True):
    _sky(cv, x, y, w, h, (244, 176, 110), (248, 205, 150), (252, 228, 190))
    hy = y + int(h * 0.72)
    cv.circle(x + w - 46, y + 22, 13, (250, 120, 60))
    # skyline silhouette
    base = hy
    for (fx, fw, fh) in ((0.04, 0.10, 0.34), (0.16, 0.08, 0.48),
                         (0.26, 0.12, 0.30), (0.40, 0.09, 0.55),
                         (0.51, 0.11, 0.38), (0.64, 0.08, 0.50),
                         (0.74, 0.12, 0.32), (0.88, 0.09, 0.44)):
        cv.rect(x + int(w * fx), base - int(h * fh), int(w * fw),
                int(h * fh), (70, 60, 66))
    cv.rect(x, hy, w, y + h - hy, (52, 46, 52))
    # runway lights
    for fx in (0.10, 0.30, 0.50, 0.70, 0.90):
        cv.rect(x + int(w * fx), y + h - 8, 6, 3, FLAME)
    # plane coming in to land
    px, py = x + int(w * 0.52), y + int(h * 0.30)
    cv.ellipse(px, py, 30, 7, DARK)
    cv.ellipse(px, py, 28, 5, WHITE)
    cv.polygon([(px - 4, py), (px + 6, py - 12), (px + 12, py - 12),
                (px + 8, py)], WHITE)
    cv.polygon([(px + 18, py - 2), (px + 30, py - 10), (px + 30, py - 2)],
               WHITE)
    # flags on poles at the edges
    for (fx, flag) in ((0.02, "US"), (0.90, "PH")):
        fx0 = x + int(w * fx)
        cv.vline(fx0, y + 8, 26, INK)
        if flag == "US":
            for i in range(7):
                cv.rect(fx0 + 1, y + 8 + i * 2, 26, 2,
                        RED if i % 2 == 0 else WHITE)
            cv.rect(fx0 + 1, y + 8, 11, 8, (30, 60, 130))
        else:
            cv.rect(fx0 + 1, y + 8, 26, 7, (30, 90, 180))
            cv.rect(fx0 + 1, y + 15, 26, 7, (200, 40, 30))
            cv.polygon([(fx0 + 1, y + 8), (fx0 + 1, y + 22),
                        (fx0 + 13, y + 15)], WHITE)
            cv.circle(fx0 + 6, y + 15, 2, GOLD)
    if strip:
        _label_strip(cv, x, y + h - 16, w, "MANILA, PHILIPPINES")


def scene_nvidia(cv, x, y, w, h, strip=True):
    cv.rect(x, y, w, h, (10, 26, 20))
    # rising bars
    base = y + h - 6
    bars = [0.30, 0.42, 0.38, 0.60, 0.85]
    bw = 26
    for i, f in enumerate(bars):
        bh = int((h - 24) * f)
        bx = x + 14 + i * 38
        cv.rect(bx, base - bh, bw, bh, GREEN if i < 4 else (118, 200, 80))
    # trend arrow over the bars
    pts = [(x + 20, base - 14), (x + 58, base - 26), (x + 96, base - 20),
           (x + 134, base - 44), (x + 172, base - 62)]
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], FLAME)
    cv.polygon([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 12, pts[-1][1] + 2),
                (pts[-1][0] - 2, pts[-1][1] + 12)], FLAME)
    # chip
    cx, cy = x + w - 78, y + 12
    cv.rect(cx - 4, cy + 8, 52, 6, STEEL)
    cv.rect(cx - 4, cy + 22, 52, 6, STEEL)
    cv.rect(cx + 8, cy - 4, 6, 52, STEEL)
    cv.rect(cx + 22, cy - 4, 6, 52, STEEL)
    cv.rect(cx, cy, 44, 44, (24, 68, 44))
    cv.rect(cx + 8, cy + 8, 28, 28, (36, 110, 70))
    cv.text(cx + 14, cy + 18, "AI", 2, WHITE)


def scene_gulf(cv, x, y, w, h, strip=True):
    _sky(cv, x, y, w, h, (226, 198, 160), (236, 214, 180), (242, 228, 200))
    hy = y + int(h * 0.58)
    _sea(cv, x, hy, w, y + h - hy, (36, 110, 122), (24, 84, 100))
    cv.circle(x + w - 52, y + 24, 14, (250, 226, 170))
    # tanker: black hull, white superstructure, funnel
    hx, hw = x + 24, w - 48
    cv.polygon([(hx, hy + 6), (hx + hw, hy + 6), (hx + hw - 18, hy + 34),
                (hx + 14, hy + 34)], (22, 22, 22))
    cv.rect(hx + hw - 66, hy - 22, 40, 28, WHITE)
    cv.rect(hx + hw - 60, hy - 30, 28, 8, WHITE)
    cv.rect(hx + 26, hy - 16, 12, 22, (178, 35, 27))
    # funnel smoke
    cv.circle(hx + 32, hy - 26, 7, SMOKE)
    cv.circle(hx + 40, hy - 34, 9, SMOKE)
    # fire at the bow
    fx = hx + hw - 30
    cv.burst(fx, hy - 2, 26, 14, 9, ORANGE)
    cv.burst(fx, hy - 2, 15, 8, 7, FLAME)
    cv.circle(fx - 14, hy - 26, 11, SMOKE)
    cv.circle(fx + 4, hy - 38, 13, SMOKE)
    cv.circle(fx + 22, hy - 26, 9, SMOKE)
    # a naval mine in the water ahead of the ship
    mx, my = x + 30, hy + int((y + h - hy) * 0.62)
    cv.burst(mx, my, 11, 7, 8, DARK)
    cv.circle(mx, my, 6, DARK)
    # drone above the sea
    dx, dy = x + int(w * 0.62), y + 30
    cv.ellipse(dx, dy, 12, 3, DARK)
    cv.line(dx - 14, dy - 4, dx + 14, dy + 4, DARK)
    _waves(cv, x, hy, w, y + h - hy,
           [(0.10, 0.35, 24), (0.42, 0.65, 30), (0.70, 0.30, 22),
            (0.86, 0.70, 26)])
    if strip:
        _label_strip(cv, x, y + h - 16, w, "STRAIT OF HORMUZ")


def scene_vulcan(cv, x, y, w, h, strip=True):
    cv.rect(x, y, w, h, (16, 26, 52))
    cv.rect(x, y, w, int(h * 0.45), (22, 36, 68))
    # stars at fixed positions
    for (fx, fy, r) in ((0.08, 0.10, 2), (0.22, 0.06, 1), (0.36, 0.14, 2),
                        (0.62, 0.08, 1), (0.78, 0.12, 2), (0.90, 0.06, 1),
                        (0.15, 0.24, 1), (0.85, 0.22, 2), (0.48, 0.05, 1),
                        (0.70, 0.26, 1)):
        cv.circle(x + int(w * fx), y + int(h * fy), r, WHITE)
    # ground and pad
    gy = y + int(h * 0.86)
    cv.rect(x, gy, w, y + h - gy, (30, 30, 34))
    cv.rect(x + int(w * 0.38), gy - 6, int(w * 0.24), 6, STEEL)
    # rocket, climbing
    rx = x + w // 2
    cv.rect(rx - 9, y + 58, 18, 74, WHITE)
    cv.polygon([(rx - 9, y + 58), (rx + 9, y + 58), (rx, y + 34)], RED)
    cv.rect(rx - 9, y + 96, 18, 8, RED)
    cv.rect(rx - 14, y + 118, 5, 14, STEEL)
    cv.rect(rx + 9, y + 118, 5, 14, STEEL)
    # flame and smoke
    cv.burst(rx, y + 148, 20, 10, 8, ORANGE)
    cv.burst(rx, y + 148, 11, 6, 6, FLAME)
    cv.circle(rx - 26, gy - 14, 12, SMOKE)
    cv.circle(rx + 28, gy - 10, 14, SMOKE)
    cv.circle(rx - 8, gy - 20, 10, SMOKE)
    # satellites falling away, with dotted paths
    for (sx, sy, ex, ey) in ((0.16, 0.30, 0.06, 0.52),
                             (0.84, 0.34, 0.94, 0.56),
                             (0.72, 0.20, 0.82, 0.40)):
        x0, y0 = x + int(w * sx), y + int(h * sy)
        x1, y1 = x + int(w * ex), y + int(h * ey)
        for t in range(0, 11, 2):
            px = x0 + (x1 - x0) * t // 10
            py = y0 + (y1 - y0) * t // 10
            cv.px(px, py, WHITE)
            cv.px(px + 1, py, WHITE)
        cv.rect(x1 - 4, y1 - 4, 9, 9, GOLD)
        cv.rect(x1 - 8, y1 - 2, 4, 5, GOLD)
        cv.rect(x1 + 5, y1 - 2, 4, 5, GOLD)
    if strip:
        _label_strip(cv, x, y + h - 16, w, "CAPE CANAVERAL, FLORIDA")


def scene_bank(cv, x, y, w, h, strip=True):
    _sky(cv, x, y, w, h, (210, 220, 228), (228, 232, 236), (240, 240, 238))
    # bank facade: pediment, columns, steps (upper part of the scene)
    bx, bw = x + 22, w - 44
    by = y + int(h * 0.06)
    cv.polygon([(bx, by + 22), (bx + bw // 2, by), (bx + bw, by + 22)],
               (196, 184, 158))
    cv.rect(bx, by + 22, bw, 8, (216, 206, 184))
    top = by + 30
    bot = y + int(h * 0.52)
    cv.rect(bx, top, bw, bot - top, (216, 206, 184))
    for i in range(5):
        cx = bx + 12 + i * ((bw - 24) // 4)
        cv.rect(cx, top + 4, 12, bot - top - 4, (245, 240, 228))
    cv.rect(bx, bot, bw, 6, (180, 168, 140))
    cv.rect(bx - 6, bot + 6, bw + 12, 5, (160, 148, 122))
    # monitor in front showing a red alert (fits above the label strip)
    my = y + int(h * 0.60)
    mh = int(h * 0.28)
    mx, mw = x + w // 2 - 52, 104
    cv.rect(mx - 4, my - 4, mw + 8, mh + 8, DARK)
    cv.rect(mx, my, mw, mh, (143, 29, 22))
    cv.polygon([(mx + mw // 2, my + 4), (mx + mw // 2 - 18, my + 26),
                (mx + mw // 2 + 18, my + 26)], GOLD)
    cv.text(mx + mw // 2 - 3, my + 10, "!", 2, (143, 29, 22))
    cv.text(mx + 12, my + mh - 16, "BUG", 2, WHITE)
    if strip:
        _label_strip(cv, x, y + h - 16, w, "WALL STREET, NEW YORK")

# ---------------------------------------------------------------------------
# Page layout
# ---------------------------------------------------------------------------

def _card(cv, x, y, w, h):
    cv.rect(x, y, w, h, CARD)
    cv.rect(x, y, w, 2, RULE)
    cv.rect(x, y + h - 2, w, 2, RULE)
    cv.rect(x, y, 2, h, RULE)
    cv.rect(x + w - 2, y, 2, h, RULE)


def _tag(cv, x, y, s):
    cv.text(x, y, s, 2, RED)


def _headline(cv, x, y, lines, scale, color=INK, gap=None):
    if gap is None:
        gap = 2
    yy = y
    for ln in lines:
        cv.text(x, yy, ln, scale, color)
        yy += 7 * scale + gap
    return yy - gap  # no trailing gap after the last line


def _body(cv, x, y, lines, scale, color=GREY, gap=None):
    if gap is None:
        gap = 2
    yy = y
    for ln in lines:
        cv.text(x, yy, ln, scale, color)
        yy += 7 * scale + gap
    return yy - gap  # no trailing gap after the last line


def panel(cv, x, y, w, h, scene, tag, headline, captions, fact,
          scene_h, head_scale=3, cap_scale=2, strip=True):
    """One news panel: scene on top, tag, headline, captions, fact line."""
    _card(cv, x, y, w, h)
    ix = x + 12
    inner = w - 24
    sy = y + 8
    scene(cv, x + 10, sy, w - 20, scene_h, strip)
    yy = sy + scene_h + 6
    _tag(cv, ix, yy, tag)
    yy += 7 * 2 + 4
    yy = _headline(cv, ix, yy, headline, head_scale)
    yy += 4
    yy = _body(cv, ix, yy, captions, cap_scale)
    if fact:
        yy += 4
        cv.hline(ix, yy, inner, GREY)
        yy += 4
        cv.text(ix, yy, fact, 2, GREY)


def masthead(cv):
    cv.text_centred(W // 2, 18, "THE WORLD TODAY", 8, INK)
    cv.text_centred(W // 2, 84, "TUESDAY 17 NOVEMBER 2026", 3, RED)
    cv.hline(14, 112, W - 28, RULE)
    cv.hline(14, 116, W - 28, RULE)


def ticker(cv, x, y, w, h):
    _card(cv, x, y, w, h)
    ix = x + 14
    yy = y + 14
    cv.rect(ix, yy + 4, 16, 16, RED)
    cv.text(ix + 26, yy, "ALSO ON TUESDAY", 4, INK)
    yy += 7 * 4 + 12
    items = [
        "JAPAN SCRAMBLES JETS AFTER RUSSIAN AIRSPACE INCURSION",
        "HOUTHIS ADVANCE IN YEMEN AS GOVERNMENT TROOPS RETREAT",
        "UK SANCTIONS FIRMS BUILDING WEST BANK SETTLEMENTS",
    ]
    for it in items:
        cv.text(ix, yy, "\u2022", 3, RED)
        cv.text(ix + 26, yy, it, 3, INK)
        yy += 7 * 3 + 8
    yy += 4
    cv.hline(ix, yy, w - 28, RULE)
    yy += 10
    cv.text_centred(W // 2, yy, "THE DAY IN ONE IMAGE - TUESDAY 17 NOVEMBER 2026",
                    3, GREY)


def build():
    cv = Canvas(W, H, PAPER)
    masthead(cv)
    # Row A: lead story + two small panels on the right.
    panel(cv, 14, 130, 626, 326, scene_kerch, "WAR IN UKRAINE",
          ["UKRAINE CUTS THE", "KERCH BRIDGE"],
          ["DRONES AND MISSILES BRING DOWN A ROAD SPAN",
           "ZELENSKYY CALLS IT AN UNPRECEDENTED OPERATION"],
          "",
          scene_h=180, head_scale=4, cap_scale=2, strip=True)
    panel(cv, 652, 130, 358, 157, scene_manila, "MANILA - DIPLOMACY",
          ["TRUMP LANDS IN", "MANILA"],
          ["ASEAN SUMMIT AND QUAD TALKS"], "",
          scene_h=52, head_scale=3, cap_scale=2, strip=False)
    panel(cv, 652, 299, 358, 157, scene_nvidia, "NEW YORK - MARKETS",
          ["NVIDIA BEATS AND", "GUIDES $130BN"],
          ["REVENUE $115.8BN, UP 103%"], "",
          scene_h=52, head_scale=3, cap_scale=2, strip=False)
    # Row B: three panels.
    panel(cv, 14, 468, 324, 318, scene_gulf, "THE GULF",
          ["DRONES OVER", "BAHRAIN"],
          ["IRAN HITS US RADAR;", "MINES IN HORMUZ"],
          "TANKER ABLAZE, 1 MISSING",
          scene_h=160, head_scale=3, cap_scale=2, strip=True)
    panel(cv, 350, 468, 324, 318, scene_vulcan, "SPACE",
          ["VULCAN FAILS:", "40 SATELLITES", "LOST"],
          ["ULA: FIRST STAGE FALTERED"],
          "FIRST FAILURE SINCE 2006",
          scene_h=156, head_scale=3, cap_scale=2, strip=True)
    panel(cv, 686, 468, 324, 318, scene_bank, "MONEY",
          ["A BUG STALLS", "AMERICA'S BANKS"],
          ["CHASE BLAMES A BUG IN ITS", "ON-PREMISE SYSTEMS"],
          "REPORTED TUESDAY 17 NOV",
          scene_h=160, head_scale=3, cap_scale=2, strip=True)
    # Ticker of the day's other stories.
    ticker(cv, 14, 798, 996, 210)
    return cv


# ---------------------------------------------------------------------------
# PNG writer (pure stdlib: struct + zlib + binascii-free CRC via zlib)
# ---------------------------------------------------------------------------

def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, cv):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.buf[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main(argv):
    if len(argv) > 1:
        out = argv[1]
    else:
        base = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
        out = os.path.join(base, "entry.png")
    cv = build()
    n = write_png(out, cv)
    print("wrote %s (%d bytes, %dx%d)" % (out, n, cv.w, cv.h))


if __name__ == "__main__":
    main(sys.argv)
