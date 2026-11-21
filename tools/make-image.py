# make-image.py — draw the 21 November 2026 front page for news-image-20261121.
#
# A single static PNG, 1024x1024, drawn with Pillow and Liberation Sans.
# No photograph, no image model, no network: every fact below was checked
# by hand against reporting published on 21 November 2026 (see SOURCES),
# and this script only turns that fixed list into pixels. Run from the
# entry root:
#   python3 tools/make-image.py
# It writes entry.png next to main.ts, deterministically.
#
# STORY LIST — Saturday 21 November 2026 (verified 21 Nov 2026)
#   Lead: Russia strikes Ukraine again overnight — in Kryvyi Rih a
#     seven-year-old boy and a 20-year-old paramedic are killed and 58
#     people are hurt; Kyiv drones injure two and cut water in five
#     districts — UNITED24 Media and kyiv24, 21 Nov 2026.
#   Markets: the S&P 500 falls 3.7% into correction; the Nasdaq drops
#     5.3% and wipes out all of its 2026 gains as the AI sell-off
#     deepens — Guardian / BBC / FT, 21 Nov 2026.
#   Myanmar: rights groups urge sanctions after the UN court's genocide
#     ruling (delivered 19 Nov); the Security Council will meet and the
#     UK expels Myanmar's defence attache — AP, 21 Nov 2026.
#   Summit: after the Shenzhen meeting, Trump calls Putin his friend;
#     Zelensky replies that Putin is a "killer" — BBC, 21 Nov 2026.
#   Riyadh: the Saudi-led coalition intercepts three Houthi missiles
#     aimed at Riyadh, the third night running — Al Jazeera, 21 Nov 2026.
#   COP31: climate talks run into overtime in Antalya, deadlocked over
#     a draft that drops fossil fuels — 21 Nov 2026 digests.
#   Peru: a 6.9-magnitude quake shakes the Andes overnight (00:09 UTC);
#     it is felt in Lima, with no casualties reported — USGS / Reuters,
#     21 Nov 2026.
#   Footer: Gen Z protests sweep 25 European countries (Reuters, 20 Nov,
#     reported 21 Nov); FBI criminal database reportedly hacked (One Turn,
#     21 Nov); Bayer pays $7.25bn to settle Roundup complaints
#     (Horizon, 21 Nov); Basra power plant fire kills at least four
#     (Horizon, 21 Nov); toxic alcohol kills 11 in India (Straits Times
#     via Horizon, 21 Nov).
#   Dropped after checking: the ICJ verdict itself (delivered 19 Nov, not
#     21 Nov — only its fallout belongs here), the daraxonrasib cancer
#     pill data (presented 19 Nov, not 21 Nov), and the Anthropic
#     mathematician's Riemann claim (unverified).
#
# SOURCES — all read 21 Nov 2026:
#   oneturn.news/day/2026-11-21, horizonapp.link/en/2026/11/21,
#   michaelbrunger.com/briefs/2026-11-21, europesays.com (Reuters wire),
#   kyiv24.com, tbsnews.net (AP wire), volcanodiscovery.com (USGS).
#
# Layout (pixels, canvas 1024x1024): cream page, navy masthead with a
# red tracked date line, a wide lead block with a navy picture square on
# the left, six panels in two rows of three, and a bold footer strip.

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent.parent
TARGET = HERE / "entry.png"

PAGE_W, PAGE_H = 1024, 1024
EDGE = 28

PAPER = (247, 241, 229)
INK = (28, 43, 74)
ALERT = (168, 42, 42)
AMBER = (217, 164, 65)
LEAF = (46, 125, 79)
RUST = (192, 90, 30)
PLUM = (91, 74, 138)
TEXT = (58, 58, 58)
SNOW = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/liberation"
FALLBACK_DIR = "/usr/share/fonts/truetype/dejavu"


def font(size, heavy=False):
    """Liberation Sans at the size asked for; DejaVu Sans if it is gone."""
    name = "LiberationSans-Bold.ttf" if heavy else "LiberationSans-Regular.ttf"
    try:
        return ImageFont.truetype(f"{FONT_DIR}/{name}", size)
    except OSError:
        name = "DejaVuSans-Bold.ttf" if heavy else "DejaVuSans.ttf"
        return ImageFont.truetype(f"{FALLBACK_DIR}/{name}", size)


def split_lines(canvas, text, face, width):
    """Greedy wrap of text into lines no wider than width pixels."""
    done, current = [], ""
    for piece in text.split():
        attempt = f"{current} {piece}".strip()
        if canvas.textlength(attempt, font=face) <= width or not current:
            current = attempt
        else:
            done.append(current)
            current = piece
    if current:
        done.append(current)
    return done


def spaced_centre(canvas, middle, top, text, face, colour, gap=9):
    """Centre text on middle, with extra space between its characters."""
    sizes = [canvas.textlength(ch, font=face) for ch in text]
    whole = sum(sizes) + gap * (len(text) - 1)
    pen = middle - whole / 2
    for ch, size in zip(text, sizes):
        canvas.text((pen, top), ch, font=face, fill=colour)
        pen += size + gap


def block(canvas, x, top, text, face, colour, width, step):
    """Draw a wrapped paragraph; return the y just under its last line."""
    for row in split_lines(canvas, text, face, width):
        canvas.text((x, top), row, font=face, fill=colour)
        top += step
    return top


# ---- small geometric pictures, drawn with plain Pillow shapes ----

def burst(canvas, cx, cy, r, colour):
    """An explosion: rays of alternating length out of a filled centre."""
    for i, angle in enumerate(range(0, 360, 30)):
        import math
        rad = math.radians(angle)
        reach = r if i % 2 == 0 else int(0.7 * r)
        x1 = cx + int(0.45 * r * math.cos(rad))
        y1 = cy + int(0.45 * r * math.sin(rad))
        x2 = cx + int(reach * math.cos(rad))
        y2 = cy + int(reach * math.sin(rad))
        canvas.line([x1, y1, x2, y2], fill=colour, width=6)
    canvas.ellipse([cx - r // 3, cy - r // 3, cx + r // 3, cy + r // 3],
                   fill=colour)


def falling_bars(canvas, cx, cy, r, colour):
    """Bars stepping down, crossed by a falling red arrow."""
    heights = [0.95, 0.75, 0.85, 0.55, 0.4]
    bar_w = r // 3
    left = cx - r
    for i, frac in enumerate(heights):
        top = cy + r // 2 - frac * r
        canvas.rectangle([left + i * (bar_w + 4), top,
                          left + i * (bar_w + 4) + bar_w, cy + r // 2],
                         fill=colour)
    canvas.line([left, cy - r // 2, left + len(heights) * (bar_w + 4),
                 cy + r // 3], fill=ALERT, width=5)


def scales(canvas, cx, cy, r, colour):
    """A balance: a post, a beam, and two hanging pans."""
    canvas.line([cx, cy - r, cx, cy + r // 2], fill=colour, width=5)
    canvas.line([cx - r, cy - r // 2, cx + r, cy - r // 2], fill=colour, width=5)
    for side in (-1, 1):
        px = cx + side * r
        canvas.line([px, cy - r // 2, px, cy], fill=colour, width=4)
        canvas.arc([px - r // 3, cy - r // 4, px + r // 3, cy + r // 4],
                   0, 180, fill=colour, width=4)


def quotes(canvas, cx, cy, r, colour):
    """Two big quotation marks, centred on the icon's middle."""
    mark = font(2 * r + 12, heavy=True)
    canvas.text((cx - r - 4, cy - r - 6), "\u201c", font=mark, fill=colour)
    canvas.text((cx + 2, cy - r - 6), "\u201d", font=mark, fill=colour)


def shield(canvas, cx, cy, r, colour):
    """A shield outline with a tick inside it."""
    canvas.polygon([(cx, cy - r), (cx + r, cy - r // 2), (cx + r, cy + r // 4),
                    (cx, cy + r), (cx - r, cy + r // 4), (cx - r, cy - r // 2)],
                   outline=colour, width=5)
    canvas.line([cx - r // 2, cy, cx - r // 6, cy + r // 3,
                 cx + r // 2, cy - r // 3], fill=colour, width=5)


def globe(canvas, cx, cy, r, colour):
    """A globe: an outline circle with equator and meridian lines."""
    canvas.ellipse([cx - r, cy - r, cx + r, cy + r], outline=colour, width=5)
    canvas.ellipse([cx - r, cy - r // 3, cx + r, cy + r // 3],
                   outline=colour, width=4)
    canvas.line([cx, cy - r, cx, cy + r], fill=colour, width=4)


def tremor(canvas, cx, cy, r, colour):
    """A seismic zigzag across the middle."""
    points = [(cx - r, cy), (cx - r // 2, cy - r // 2), (cx - r // 4, cy + r // 2),
              (cx, cy - r // 2), (cx + r // 4, cy + r // 2),
              (cx + r // 2, cy - r // 2), (cx + r, cy)]
    canvas.line(points, fill=colour, width=5, joint="curve")


STORIES = [
    dict(colour=ALERT, tag="NEW YORK · MARKETS", title="NASDAQ WIPES OUT 2026 GAINS",
         text="The S&P 500 falls 3.7% into correction; the Nasdaq drops 5.3%, "
              "erasing all of its 2026 gains.",
         art=falling_bars),
    dict(colour=INK, tag="THE HAGUE · JUSTICE", title="SANCTIONS SOUGHT OVER MYANMAR",
         text="Rights groups urge sanctions after the UN court's genocide "
              "ruling; the Security Council will meet.",
         art=scales),
    dict(colour=RUST, tag="SHENZHEN · SUMMIT", title="TRUMP CALLS PUTIN 'FRIEND'",
         text="After the Shenzhen summit, Trump calls Putin his friend; "
              "Zelensky replies: Putin is a \u201ckiller\u201d.",
         art=quotes),
    dict(colour=LEAF, tag="RIYADH · GULF", title="MISSILES AT RIYADH STOPPED",
         text="The Saudi-led coalition intercepts three Houthi missiles aimed "
              "at Riyadh, the third night running.",
         art=shield),
    dict(colour=PLUM, tag="ANTALYA · CLIMATE", title="COP31 STILL DEADLOCKED",
         text="Climate talks run into overtime in Antalya, deadlocked over a "
              "draft that drops fossil fuels.",
         art=globe),
    dict(colour=ALERT, tag="LIMA · EARTHQUAKE", title="PERU SHAKEN BY 6.9 QUAKE",
         text="A 6.9-magnitude quake shakes the Andes overnight; it is felt "
              "in Lima, with no casualties reported.",
         art=tremor),
]

LEAD_TEXT = ("Overnight strikes kill a seven-year-old boy and a paramedic in "
             "Kryvyi Rih, injure 58 people and hit Kyiv again, cutting water "
             "in five districts.")

FOOT_TEXT = ("ALSO ON 21 NOVEMBER: Gen Z protests sweep 25 countries \u00b7 FBI "
             "database \u2018reportedly hacked\u2019 \u00b7 Bayer pays $7.25bn over "
             "Roundup \u00b7 Basra plant fire kills 4 \u00b7 India toxic alcohol "
             "kills 11.")


def panel(canvas, x, top, width, height, story):
    """One white panel: coloured top bar, picture, tag, headline, body."""
    paint = story["colour"]
    canvas.rectangle([x, top, x + width, top + height], fill=SNOW,
                     outline=INK, width=2)
    canvas.rectangle([x, top, x + width, top + 10], fill=paint)
    mid = x + width // 2
    story["art"](canvas, mid, top + 48, 26, paint)
    tag_face = font(17, heavy=True)
    canvas.text((x + 14, top + 82), story["tag"], font=tag_face, fill=paint)
    head_face = font(27, heavy=True)
    head_y = top + 106
    for row in split_lines(canvas, story["title"], head_face, width - 28):
        canvas.text((x + 14, head_y), row, font=head_face, fill=INK)
        head_y += 32
    body_face = font(17)
    rows = split_lines(canvas, story["text"], body_face, width - 28)
    assert len(rows) <= 3, f"panel text too long: {story['title']}"
    block(canvas, x + 14, head_y + 6, story["text"], body_face, TEXT,
          width - 28, 22)


def build():
    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    canvas = ImageDraw.Draw(page)

    # Masthead.
    name_face = font(62, heavy=True)
    canvas.text((PAGE_W // 2, 22), "THE WORLD IN ONE DAY", font=name_face,
                fill=INK, anchor="ma")
    day_face = font(26, heavy=True)
    spaced_centre(canvas, PAGE_W // 2, 96, "SATURDAY \u00b7 21 NOVEMBER 2026",
                  day_face, ALERT, 9)
    canvas.line([EDGE, 132, PAGE_W - EDGE, 132], fill=INK, width=3)
    canvas.rectangle([EDGE, 140, PAGE_W - EDGE, 148], fill=ALERT)

    # Lead block: navy picture square left, story right.
    lead_top, lead_h = 158, 272
    square = 290
    canvas.rectangle([EDGE, lead_top, EDGE + square, lead_top + lead_h],
                     fill=INK)
    burst(canvas, EDGE + square // 2, lead_top + 118, 78, AMBER)
    city_face = font(26, heavy=True)
    canvas.text((EDGE + square // 2, lead_top + 218), "KRYVYI RIH",
                font=city_face, fill=SNOW, anchor="ma")
    text_x = EDGE + square + 22
    text_w = PAGE_W - EDGE - text_x
    kick_face = font(22, heavy=True)
    canvas.text((text_x, lead_top + 8), "RUSSIA-UKRAINE WAR", font=kick_face,
                fill=ALERT)
    lead_face = font(54, heavy=True)
    head_y = lead_top + 38
    for row in split_lines(canvas, "RUSSIA STRIKES AGAIN OVERNIGHT",
                           lead_face, text_w):
        canvas.text((text_x, head_y), row, font=lead_face, fill=INK)
        head_y += 60
    body_face = font(24)
    rows = split_lines(canvas, LEAD_TEXT, body_face, text_w)
    assert len(rows) <= 3, f"lead text wraps to {len(rows)} lines"
    block(canvas, text_x, head_y + 8, LEAD_TEXT, body_face, TEXT, text_w, 31)
    canvas.rectangle([EDGE, lead_top, PAGE_W - EDGE, lead_top + lead_h],
                     outline=INK, width=2)

    # Six panels, two rows of three.
    space = 16
    panel_w = (PAGE_W - 2 * EDGE - 2 * space) // 3
    panel_h = 246
    panel_top = lead_top + lead_h + 14
    for i, story in enumerate(STORIES):
        px = EDGE + (i % 3) * (panel_w + space)
        py = panel_top + (i // 3) * (panel_h + space)
        panel(canvas, px, py, panel_w, panel_h, story)

    # Footer strip.
    foot_top = panel_top + 2 * panel_h + space + 12
    canvas.line([EDGE, foot_top, PAGE_W - EDGE, foot_top], fill=INK, width=2)
    foot_face = font(19, heavy=True)
    rows = split_lines(canvas, FOOT_TEXT, foot_face, PAGE_W - 2 * EDGE)
    assert len(rows) <= 2, f"footer wraps to {len(rows)} lines"
    block(canvas, EDGE, foot_top + 10, FOOT_TEXT, foot_face, INK,
          PAGE_W - 2 * EDGE, 25)

    page.save(TARGET, "PNG")
    print(f"wrote {TARGET} ({TARGET.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
