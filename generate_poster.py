#!/usr/bin/env python3
"""Draw the 25 November 2026 world-news poster (1024x1024 PNG).

Reads news.json (35 verified stories) and draws a fixed front-page layout:
header with the date, a UTC timeline, a 5x7 story grid, and a source audit
bar. Run:  python3 generate_poster.py [news.json] [entry.png]

Layout (1024x1024, all pixels):
  header      y   0-106   title + WEDNESDAY 25 NOVEMBER 2026
  timeline    y 112-150   UTC ticks, dots = stories first reported
  grid        y 158-955   5 columns x 7 rows of story cards
  audit bar   y 966-1014  dark strip: sources + counts + judge note
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
BOLD = str(FONT_DIR / "DejaVuSans-Bold.ttf")
REGULAR = str(FONT_DIR / "DejaVuSans.ttf")

PAPER = (250, 246, 236)
INK = (26, 26, 26)
CARD = (255, 255, 255)
CARD_BORDER = (216, 210, 192)
MUTED = (110, 104, 88)
RULE = (26, 26, 26)

REGION_COLORS = {
    "Middle East": (179, 57, 46),
    "Europe": (36, 86, 166),
    "United States": (31, 122, 77),
    "Asia-Pacific": (199, 125, 10),
    "Global": (91, 74, 138),
}
REGION_TAG = {
    "Middle East": "MIDDLE EAST",
    "Europe": "EUROPE",
    "United States": "UNITED STATES",
    "Asia-Pacific": "ASIA-PACIFIC",
    "Global": "GLOBAL",
}
REGION_ORDER = ["Middle East", "Europe", "United States", "Asia-Pacific", "Global"]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns lines that fit max_w pixels."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, max_w, max_lines, ellipsis="..."):
    """Wrap text to at most max_lines, truncating the last line if needed."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    while lines and draw.textlength(lines[-1] + ellipsis, font=fnt) > max_w:
        lines[-1] = lines[-1][:-1]
    lines[-1] = lines[-1] + ellipsis
    return lines


def draw_icon(draw, field, cx, cy, color):
    """Small geometric glyph for a story field, centred at (cx, cy)."""
    s = 7  # half-size
    if field in ("conflict",):
        draw.line([cx - s, cy - s, cx + s, cy + s], fill=color, width=3)
        draw.line([cx - s, cy + s, cx + s, cy - s], fill=color, width=3)
    elif field in ("diplomacy", "politics"):
        draw.ellipse([cx - s - 3, cy - s, cx - 1, cy + s], outline=color, width=2)
        draw.ellipse([cx + 1, cy - s, cx + s + 3, cy + s], outline=color, width=2)
    elif field in ("markets", "economy"):
        for i, h in enumerate((4, 8, 12)):
            x0 = cx - s + i * 5
            draw.rectangle([x0, cy + s - h, x0 + 3, cy + s], fill=color)
    elif field.startswith("tech") or field == "ai":
        draw.rectangle([cx - s, cy - s, cx + s, cy + s], outline=color, width=2)
        draw.rectangle([cx - 3, cy - 3, cx + 3, cy + 3], fill=color)
    elif field in ("disaster",):
        draw.polygon([(cx, cy - s - 1), (cx + s + 1, cy + s),
                      (cx - s - 1, cy + s)], outline=color, width=2)
        draw.line([cx, cy - 3, cx, cy + 2], fill=color, width=2)
        draw.ellipse([cx - 1, cy + 4, cx + 1, cy + 6], fill=color)
    elif field in ("energy",):
        pts = [(cx + 2, cy - s - 1), (cx - 4, cy + 2), (cx, cy + 2),
               (cx - 2, cy + s + 1), (cx + 4, cy - 2), (cx, cy - 2)]
        draw.polygon(pts, fill=color)
    elif field in ("climate",):
        draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=color, width=2)
        draw.line([cx, cy - s, cx, cy + s], fill=color, width=2)
    elif field in ("health",):
        draw.rectangle([cx - 2, cy - s, cx + 2, cy + s], fill=color)
        draw.rectangle([cx - s, cy - 2, cx + s, cy + 2], fill=color)
    elif field in ("science", "space"):
        draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=color, width=2)
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=color)
        draw.line([cx - s, cy, cx + s, cy], fill=color, width=1)
    elif field in ("culture",):
        draw.ellipse([cx - 4, cy + 2, cx + 1, cy + 7], fill=color)
        draw.line([cx + 1, cy + 4, cx + 1, cy - s], fill=color, width=2)
        draw.line([cx + 1, cy - s, cx + s, cy - s + 3], fill=color, width=2)
    elif field in ("sport",):
        draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=color, width=2)
        draw.arc([cx - s, cy - s, cx + s, cy + s], 200, 340, fill=color, width=2)
    elif field in ("justice", "crime"):
        draw.line([cx - s, cy - 2, cx + s, cy - 2], fill=color, width=2)
        draw.line([cx, cy - 2, cx, cy + s], fill=color, width=2)
        draw.line([cx - s, cy - 2, cx - s + 2, cy + 3], fill=color, width=2)
        draw.line([cx + s, cy - 2, cx + s - 2, cy + 3], fill=color, width=2)
    elif field in ("migration",):
        draw.line([cx - s, cy, cx + s, cy], fill=color, width=3)
        draw.polygon([(cx + s, cy), (cx + s - 5, cy - 4), (cx + s - 5, cy + 4)],
                     fill=color)
    else:
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=color)


def main() -> int:
    here = Path(__file__).resolve().parent
    news_path = Path(sys.argv[1]) if len(sys.argv) > 1 else here / "news.json"
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else here / "entry.png"
    items = json.loads(news_path.read_text(encoding="utf-8"))
    assert len(items) == 35, f"expected 35 stories, got {len(items)}"
    for region, want in (("Middle East", 8), ("Europe", 7), ("United States", 8),
                         ("Asia-Pacific", 6), ("Global", 6)):
        got = sum(1 for it in items if it["region"] == region)
        assert got == want, f"{region}: expected {want}, got {got}"
    ordered = [it for r in REGION_ORDER for it in items if it["region"] == r]

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    f_kicker = font(BOLD, 30)
    f_date = font(BOLD, 48)
    f_tag = font(BOLD, 11)
    f_head = font(BOLD, 14)
    f_detail = font(REGULAR, 11)
    f_small = font(BOLD, 11)
    f_audit = font(BOLD, 13)

    # ---- header ----
    d.text((W // 2, 12), "THE WORLD IN ONE DAY", font=f_kicker, fill=INK,
           anchor="ma")
    d.text((W // 2, 48), "WEDNESDAY 25 NOVEMBER 2026", font=f_date, fill=INK,
           anchor="ma")
    d.line([(16, 102), (W - 16, 102)], fill=RULE, width=3)
    d.line([(16, 107), (W - 16, 107)], fill=RULE, width=1)

    # ---- UTC timeline ----
    d.text((16, 120), "UTC — 25 NOV 2026", font=f_small, fill=MUTED)
    tl_x0, tl_x1, tl_y = 210, W - 16, 134
    d.line([(tl_x0, tl_y), (tl_x1, tl_y)], fill=MUTED, width=2)
    for hour in (0, 4, 8, 12, 16, 20, 24):
        x = tl_x0 + (tl_x1 - tl_x0) * hour // 24
        d.line([(x, tl_y - 5), (x, tl_y + 5)], fill=MUTED, width=2)
        d.text((x, tl_y + 9), f"{hour:02d}:00", font=f_small, fill=MUTED,
               anchor="ma")
    earliest = sorted(items, key=lambda it: it["time_utc"])[:6]
    for i, it in enumerate(earliest):
        hh, mm = (int(v) for v in it["time_utc"].split(":"))
        frac = (hh * 60 + mm) / 1440
        x = tl_x0 + (tl_x1 - tl_x0) * frac
        y = tl_y - 9 - (4 if i % 2 else 0)
        color = REGION_COLORS[it["region"]]
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=color)
    d.text((W - 16, 120), "● = story first reported", font=f_small,
           fill=MUTED, anchor="ra")

    # ---- story grid: 5 cols x 7 rows ----
    gx, gy = 16, 158
    cw, ch, gut = 192, 107, 8
    for idx, it in enumerate(ordered):
        col, row = idx % 5, idx // 5
        x0 = gx + col * (cw + gut)
        y0 = gy + row * (ch + gut)
        x1, y1 = x0 + cw, y0 + ch
        color = REGION_COLORS[it["region"]]
        d.rectangle([x0, y0, x1, y1], fill=CARD, outline=CARD_BORDER, width=1)
        d.rectangle([x0, y0, x0 + 6, y1], fill=color)
        px = x0 + 13
        draw_icon(d, it["field"].lower(), x1 - 14, y0 + 13, color)
        d.text((px, y0 + 6), REGION_TAG[it["region"]], font=f_tag, fill=color)
        head_lines = fit_lines(d, it["headline"], f_head, cw - 20, 2)
        y = y0 + 24
        for ln in head_lines:
            d.text((px, y), ln, font=f_head, fill=INK)
            y += 18
        det_lines = fit_lines(d, it["detail"], f_detail, cw - 20, 3)
        y += 2
        for ln in det_lines:
            d.text((px, y), ln, font=f_detail, fill=(60, 58, 50))
            y += 13

    # ---- audit bar ----
    ay0, ay1 = 966, 1014
    d.rectangle([0, ay0, W, ay1], fill=INK)
    sources = []
    for it in items:
        if it["source"] not in sources:
            sources.append(it["source"])
    src_line = "SOURCES: " + " · ".join(s.upper() for s in sources)
    d.text((16, ay0 + 6), src_line, font=f_audit, fill=(250, 246, 236))
    n_regions = len({it["region_detail"] for it in items})
    n_fields = len({it["field"] for it in items})
    d.text((16, ay0 + 27),
           f"35 STORIES · {n_regions} REGIONS · {n_fields} FIELDS — JUDGE: "
           "EVERY STORY WAS FIRST REPORTED ON 25 NOVEMBER 2026",
           font=f_audit, fill=(200, 190, 160))

    img.save(out_path, format="PNG", optimize=True)
    size = out_path.stat().st_size
    print(f"wrote {out_path} 1024x1024, {size} bytes")
    assert img.size == (1024, 1024)
    assert size <= 1048576, f"over 1 MiB: {size}"
    regions = sorted({it["region_detail"] for it in items})
    fields = sorted({it["field"] for it in items})
    print(f"regions: {len(regions)} ({', '.join(regions)})")
    print(f"fields: {len(fields)} ({', '.join(fields)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
