"""THE WORLD TODAY - Monday 23 November 2026 front page.

Pure-stdlib Python 3.13 program. Draws the day's world news as a
one-page newspaper front page and writes a deterministic 1024x1024
PNG to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Stories (all happened or first reported Mon 23 Nov 2026):
  LEAD  COP31 collapses in Antalya: no deal, text never names fossil fuels
  SEA   Russian corvette Merkury sinks at Benghazi after a drone attack
  US    Democrats win 258 House seats, largest majority since 1992
  GULF  Tankers ablaze near Hormuz; Iran says it downed a US drone
  UKR   Russian strike on flats in Dymer kills at least 10
  MKT   AI sell-off: Nikkei -5.06%, S&P 500 -3.7%
  IDN   Candy factory fire in Banten leaves dozens missing
  ALSO  Nepal PM in Delhi, Korea exports pass $1 trillion, sport

Text comes from bitmap glyphs in font_data.py (DejaVu Sans Book +
Bold, one 64px base size, only the glyphs this page uses), scaled at
runtime. PNG is encoded by hand with zlib. No network, no clock,
no randomness: two runs write identical bytes.
"""

import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from font_data import ASCENT, GLYPHS

W = 1024
H = 1024
BASE = 64.0

PAPER = (247, 243, 232)
INK = (20, 20, 20)
RED = (176, 32, 32)
BLUE = (31, 78, 121)
GREY = (102, 102, 102)
LIGHT = (226, 220, 205)
GOLD = (184, 134, 11)
GREEN = (34, 110, 60)


class Canvas:
    def __init__(self):
        self.px = bytearray(bytes(PAPER) * (W * H))

    def set(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, t=2):
        import math
        steps = max(24, r * 4)
        prev = None
        for i in range(steps + 1):
            a = 2 * math.pi * i / steps
            p = (cx + int(round(r * math.cos(a))),
                 cy + int(round(r * math.sin(a))))
            if prev is not None:
                self.line(prev[0], prev[1], p[0], p[1], c, t)
            prev = p

    def disc(self, cx, cy, r, c):
        import math
        for yy in range(cy - r, cy + r + 1):
            half = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
            self.hline(cx - half, yy, half * 2 + 1, c)

    def poly(self, pts, c):
        # scanline fill of a simple polygon
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.hline(int(xs[j]), y, max(1, int(xs[j + 1]) - int(xs[j])), c)

    def ellipse_arc(self, cx, cy, rx, ry, a0, a1, c, t=1):
        import math
        steps = 48
        prev = None
        for i in range(steps + 1):
            a = a0 + (a1 - a0) * i / steps
            p = (cx + int(round(rx * math.cos(a))),
                 cy + int(round(ry * math.sin(a))))
            if prev is not None:
                self.line(prev[0], prev[1], p[0], p[1], c, t)
            prev = p


# ---- text from bitmap glyphs -------------------------------------------

def _glyph(ch, bold):
    g = GLYPHS.get((ord(ch), 1 if bold else 0))
    if g is None and bold:
        g = GLYPHS.get((ord(ch), 0))
    return g


def text_width(s, size, bold=False):
    sc = size / BASE
    w = 0
    for ch in s:
        g = _glyph(ch, bold)
        if g is None:
            w += int(28 * sc)
        else:
            w += int(g[0] * sc)
    return w


def draw_text(cv, s, x, y, size, bold=False, color=INK):
    """Draw s with its top at y (top of the em box). Returns width."""
    sc = size / BASE
    baseline = y + int(ASCENT * sc)
    cx = x
    for ch in s:
        g = _glyph(ch, bold)
        if g is None:
            cx += int(28 * sc)
            continue
        adv, left, top, gw, gh, hx = g
        sw = -(-gw * size // 64)  # ceil
        sh = -(-gh * size // 64)
        if sw > 0 and sh > 0:
            data = bytes.fromhex(hx)
            gx = cx + int(left * sc)
            gy = baseline + int(top * sc)
            for dy in range(sh):
                sy = int(dy / sc) if sc else 0
                if sy >= gh:
                    sy = gh - 1
                for dx in range(sw):
                    sx = int(dx / sc) if sc else 0
                    if sx >= gw:
                        sx = gw - 1
                    # bits are one continuous row-major stream
                    bit = sy * gw + sx
                    if (data[bit // 8] >> (7 - bit % 8)) & 1:
                        cv.set(gx + dx, gy + dy, color)
        cx += int(adv * sc)
    return cx - x


def wrap(text, size, bold, maxw):
    lines, cur = [], ""
    for word in text.split(" "):
        t = (cur + " " + word) if cur else word
        if text_width(t, size, bold) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(cv, text, x, y, w, size, bold=False, color=INK, leading=None):
    ld = leading if leading is not None else int(size * 1.32)
    for ln in wrap(text, size, bold, w):
        draw_text(cv, ln, x, y, size, bold, color)
        y += ld
    return y


def centered(cv, s, y, size, bold=False, color=INK, cx=W // 2):
    w = text_width(s, size, bold)
    draw_text(cv, s, cx - w // 2, y, size, bold, color)


# ---- PNG encoding -------------------------------------------------------

def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def save_png(cv, path):
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += cv.px[y * W * 3:(y + 1) * W * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---- drawings -----------------------------------------------------------

def draw_globe(cv, cx, cy, r):
    cv.circle(cx, cy, r, BLUE, 3)
    cv.ellipse_arc(cx, cy, r, r // 3, -1.2, 1.2, BLUE, 2)
    cv.ellipse_arc(cx, cy, r, r // 3, 1.94, 4.34, BLUE, 2)
    cv.ellipse_arc(cx, cy, r // 3, r, -1.2, 1.2, BLUE, 2)
    cv.ellipse_arc(cx, cy, r // 3, r, 1.94, 4.34, BLUE, 2)
    cv.ellipse_arc(cx, cy, r // 2, r, 0.5, 2.6, BLUE, 1)
    # jagged crack across the globe
    crack = [(cx - r + 18, cy - 30), (cx - 42, cy - 8), (cx - 12, cy + 6),
             (cx - 34, cy + 26), (cx + 6, cy + 44), (cx - 8, cy + 62),
             (cx + 30, cy + r - 12)]
    for a, b in zip(crack, crack[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED, 3)
    # land masses, schematic
    cv.poly([(cx - 62, cy - 58), (cx - 20, cy - 66), (cx - 8, cy - 40),
             (cx - 34, cy - 22), (cx - 66, cy - 34)], GREEN)
    cv.poly([(cx + 22, cy + 8), (cx + 62, cy - 2), (cx + 70, cy + 30),
             (cx + 34, cy + 40), (cx + 14, cy + 24)], GREEN)
    cv.poly([(cx - 70, cy + 44), (cx - 44, cy + 38), (cx - 40, cy + 62),
             (cx - 64, cy + 70)], GREEN)


def draw_ship(cv, x, y, w):
    # waves
    for k in range(2):
        yy = y + 40 + k * 6
        for xx in range(x, x + w, 4):
            cv.set(xx, yy + (2 if (xx // 4) % 2 else 0), BLUE)
            cv.set(xx + 1, yy + (2 if (xx // 4) % 2 else 0), BLUE)
    # hull, listing to port
    cv.poly([(x + 8, y + 20), (x + w - 8, y + 14), (x + w - 26, y + 32),
             (x + 22, y + 36)], INK)
    cv.rect(x + w // 2 - 6, y + 2, 4, 14, INK)
    cv.line(x + w // 2 - 4, y + 2, x + w // 2 + 18, y + 8, RED, 2)
    cv.poly([(x + w // 2 + 18, y + 8), (x + w // 2 + 18, y + 14),
             (x + w // 2 + 4, y + 12)], RED)
    # smoke
    cv.disc(x + w // 2 + 26, y, 4, GREY)
    cv.disc(x + w // 2 + 38, y - 4, 3, GREY)


def draw_dome(cv, x, y, w):
    # US Capitol dome, schematic
    cv.rect(x + 8, y + 24, w - 16, 4, INK)
    for i in range(5):
        cv.rect(x + 14 + i * ((w - 28) // 5), y + 28, 3, 10, INK)
    cv.rect(x + 8, y + 38, w - 16, 4, INK)
    import math
    for a in range(0, 181, 6):
        px = x + w // 2 + int((w // 2 - 10) * math.cos(math.radians(a)))
        py = y + 24 - int(16 * math.sin(math.radians(a)))
        cv.set(px, py, INK)
        cv.set(px, py + 1, INK)
    cv.rect(x + w // 2 - 2, y, 4, 8, INK)
    cv.line(x + w // 2 + 2, y, x + w // 2 + 16, y + 5, RED, 2)


def draw_tanker(cv, x, y, w):
    for k in range(2):
        yy = y + 40 + k * 6
        for xx in range(x, x + w, 4):
            cv.set(xx, yy, BLUE)
            cv.set(xx + 1, yy, BLUE)
    cv.rect(x + 6, y + 20, w - 12, 14, INK)
    cv.rect(x + w - 34, y + 8, 24, 12, INK)
    cv.rect(x + 12, y + 12, 16, 8, RED)
    cv.rect(x + 32, y + 12, 16, 8, GOLD)
    cv.rect(x + 52, y + 12, 16, 8, BLUE)
    # flames
    for fx, fh in ((x + 16, 16), (x + 40, 22), (x + 62, 14)):
        cv.poly([(fx, y + 12), (fx + 7, y + 12 - fh), (fx + 14, y + 12)],
                RED)
        cv.poly([(fx + 4, y + 12), (fx + 7, y + 12 - fh // 2),
                 (fx + 10, y + 12)], GOLD)


# ---- the page -----------------------------------------------------------

def build():
    cv = Canvas()
    MX = 36
    RW = W - 2 * MX

    # masthead
    centered(cv, "THE WORLD TODAY", 22, 58, bold=True)
    cv.hline(MX, 92, RW, INK, 3)
    draw_text(cv, "MONDAY 23 NOVEMBER 2026", MX, 100, 21, bold=True)
    right = "ANTALYA  •  BENGHAZI  •  WASHINGTON"
    draw_text(cv, right, W - MX - text_width(right, 21, True), 100, 21,
              bold=True, color=GREY)
    cv.hline(MX, 128, RW, INK, 2)

    # lead kicker + headline + deck
    draw_text(cv, "CLIMATE SUMMIT  •  ANTALYA, TURKEY", MX, 140, 20,
              bold=True, color=RED)
    draw_text(cv, "COP31 COLLAPSES", MX, 164, 66, bold=True)
    para(cv, "No deal after two days of overtime: the EU and about 130 "
             "governments reject a text that never names fossil fuels.",
         MX, 236, RW, 22, leading=28)

    # lead body, left column
    y = 300
    y = para(cv, "The COP31 climate summit ended in Antalya on Sunday "
                 "with no overall agreement, after 18 days and two days "
                 "of overtime.", MX, y, 520, 20, leading=25)
    y += 8
    y = para(cv, "The draft text never named fossil fuels, oil, coal or "
                 "a phase-out. The European Union and about 130 other "
                 "parties refused it, and the talks collapsed.",
             MX, y, 520, 20, leading=25)
    y += 8
    y = para(cv, "The summit ended with no deal and no final text.",
             MX, y, 520, 20, leading=25)

    # lead art, right column: cracked globe + NO DEAL stamp
    gx, gy = 700, 388
    draw_globe(cv, gx, gy, 80)
    cv.rect(gx - 108, gy + 60, 216, 34, RED)
    centered(cv, "NO DEAL", gy + 64, 24, bold=True, color=PAPER, cx=gx)
    draw_text(cv, "The summit ended with no text at all.",
              580, 490, 16, bold=False, color=GREY)

    cv.hline(MX, 516, RW, INK, 2)

    # row 2: three stories, art band below the bodies
    cols = [MX, MX + 326, MX + 652]
    cw = 300
    # A: Merkury
    x = cols[0]
    draw_text(cv, "WAR AT SEA  •  BENGHAZI", x, 530, 16, bold=True, color=RED)
    y = para(cv, "MERKURY SINKS", x, 552, cw, 27, bold=True, leading=30)
    para(cv, "A Ukrainian naval drone attack sank the Russian corvette "
             "Merkury at Benghazi naval base in eastern Libya.",
         x, y + 4, cw, 17, leading=21)
    draw_ship(cv, x + 40, 706, 220)
    # B: Democrats
    x = cols[1]
    draw_text(cv, "WASHINGTON", x, 530, 16, bold=True, color=RED)
    y = para(cv, "DEMOCRATS WIN 258", x, 552, cw, 27, bold=True, leading=30)
    para(cv, "Democrats took 258 House seats, their largest majority "
             "since 1992, as Hubbard beat Foxx in a recount.",
         x, y + 4, cw, 17, leading=21)
    draw_dome(cv, x + 90, 706, 120)
    # C: Hormuz
    x = cols[2]
    draw_text(cv, "THE GULF  •  HORMUZ", x, 530, 16, bold=True, color=RED)
    y = para(cv, "TANKERS ABLAZE", x, 552, cw, 27, bold=True, leading=30)
    para(cv, "Iran said it downed a US MQ-9 drone over Hormuz. Two "
             "supertankers caught fire after hitting mines.",
         x, y + 4, cw, 17, leading=21)
    draw_tanker(cv, x + 40, 706, 220)

    cv.hline(MX, 758, RW, INK, 2)

    # row 3: three stories, no art (bodies carry it)
    x = cols[0]
    draw_text(cv, "UKRAINE  •  DYMER", x, 772, 16, bold=True, color=RED)
    y = para(cv, "TEN KILLED IN STRIKE ON FLATS", x, 794, cw, 24, bold=True,
             leading=28)
    para(cv, "A Russian strike on flats in Dymer killed at least 10 "
             "people. A boy of seven was pulled alive from the rubble.",
         x, y + 4, cw, 17, leading=21)
    x = cols[1]
    draw_text(cv, "MARKETS", x, 772, 16, bold=True, color=RED)
    y = para(cv, "AI ROUT HITS ASIA", x, 794, cw, 24, bold=True, leading=28)
    para(cv, "Japan's Nikkei fell 5.06% and Hong Kong stocks hit a "
             "19-month low as the AI sell-off spread. The S&P 500 fell "
             "3.7%.", x, y + 4, cw, 17, leading=21)
    x = cols[2]
    draw_text(cv, "INDONESIA  •  BANTEN", x, 772, 16, bold=True, color=RED)
    y = para(cv, "FACTORY FIRE: DOZENS MISSING", x, 794, cw, 24, bold=True,
             leading=28)
    para(cv, "Dozens are missing after a fire at a candy factory in "
             "Banten, Indonesia. Rescuers searched the burned-out plant "
             "on Monday.", x, y + 4, cw, 17, leading=21)

    cv.hline(MX, 946, RW, INK, 2)

    # also strip
    para(cv, "ALSO TODAY:  Nepal's PM Balen Shah welcomed by Modi in "
             "New Delhi  •  South Korea's exports pass $1 trillion  •  "
             "Bolsonaro in intensive care  •  Marquez takes an eighth "
             "MotoGP title  •  Alcaraz wins the ATP Finals",
         MX, 956, RW, 16, leading=20)
    centered(cv, "Sources: Reuters, AP, BBC, Al Jazeera, The Guardian — "
                 "every story happened or was first reported on Monday "
                 "23 November 2026.", 1000, 13, color=GREY)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    n = save_png(build(), path)
    print("wrote", path, n, "bytes")


if __name__ == "__main__":
    main()
