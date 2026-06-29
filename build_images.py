"""
Generate logo and sheet-preview screenshots for the Personal Goal & Habit Tracker.
Outputs into personal-goal-habit-tracker/images/
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

IMAGES = Path("personal-goal-habit-tracker/images")
IMAGES.mkdir(parents=True, exist_ok=True)

FONT_BOLD   = "/usr/share/fonts/TTF/LiberationSans-Bold.ttf"
FONT_REG    = "/usr/share/fonts/TTF/LiberationSans-Regular.ttf"

# Brand palette
DARK_BLUE  = "#1A5276"
MID_BLUE   = "#2E86C1"
LIGHT_BLUE = "#D6EAF8"
DARK_GREEN = "#1E8449"
MID_GREEN  = "#27AE60"
LIGHT_GREEN= "#D5F5E3"
AMBER      = "#F39C12"
RED        = "#E74C3C"
GREY       = "#EAECEE"
WHITE      = "#FFFFFF"
TEXT_DARK  = "#1C2833"


# ── Helpers ────────────────────────────────────────────────────────────────────

def pil_color(hex_str):
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.ellipse([x0, y0, x0 + 2*radius, y0 + 2*radius], fill=fill)
    draw.ellipse([x1 - 2*radius, y0, x1, y0 + 2*radius], fill=fill)
    draw.ellipse([x0, y1 - 2*radius, x0 + 2*radius, y1], fill=fill)
    draw.ellipse([x1 - 2*radius, y1 - 2*radius, x1, y1], fill=fill)


# ═══════════════════════════════════════════════════════════════════════════════
# LOGO — square icon (512 × 512)
# ═══════════════════════════════════════════════════════════════════════════════
def build_icon():
    SIZE = 512
    img  = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background rounded rect
    bg_col = pil_color(DARK_BLUE)
    draw_rounded_rect(draw, (0, 0, SIZE - 1, SIZE - 1), 72, bg_col)

    # ── habit heatmap grid (top half) ─────────────────────────────────────────
    cols, rows = 7, 4
    cell_w, cell_h = 42, 36
    gap = 6
    grid_w = cols * cell_w + (cols - 1) * gap
    grid_h = rows * cell_h + (rows - 1) * gap
    ox = (SIZE - grid_w) // 2
    oy = 72

    greens = [
        pil_color("#D5F5E3"), pil_color("#82E0AA"),
        pil_color("#27AE60"), pil_color("#1E8449"),
    ]
    pattern = [
        [3, 3, 2, 3, 3, 2, 3],
        [2, 3, 3, 3, 2, 3, 3],
        [3, 2, 3, 3, 3, 3, 2],
        [3, 3, 3, 2, 3, 3, 3],
    ]
    for r in range(rows):
        for c in range(cols):
            x0 = ox + c * (cell_w + gap)
            y0 = oy + r * (cell_h + gap)
            shade = greens[pattern[r][c]]
            draw_rounded_rect(draw, (x0, y0, x0 + cell_w, y0 + cell_h), 6, shade)

    # ── bold checkmark (bottom half) ──────────────────────────────────────────
    ck_col = pil_color(MID_GREEN)
    # Circle behind check
    cx, cy, cr = SIZE // 2, 360, 96
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=pil_color(MID_BLUE))

    # Thick check mark via lines
    check_pts = [
        (cx - 48, cy + 0),
        (cx - 14, cy + 36),
        (cx + 52, cy - 46),
    ]
    draw.line(check_pts[:2], fill=pil_color(LIGHT_GREEN), width=20)
    draw.line(check_pts[1:], fill=pil_color(LIGHT_GREEN), width=20)

    # ── save ──────────────────────────────────────────────────────────────────
    # Crop to shape with anti-aliased mask
    mask = Image.new("L", (SIZE, SIZE), 0)
    m_draw = ImageDraw.Draw(mask)
    draw_rounded_rect(m_draw, (0, 0, SIZE - 1, SIZE - 1), 72, 255)
    img.putalpha(mask)

    out = IMAGES / "logo-icon.png"
    img.save(out, "PNG")
    print(f"  icon   → {out}")

    # Also save a 256 × 256 version
    small = img.resize((256, 256), Image.LANCZOS)
    small.save(IMAGES / "logo-icon-256.png", "PNG")

    return img


# ═══════════════════════════════════════════════════════════════════════════════
# LOGO — wide banner (1200 × 360)
# ═══════════════════════════════════════════════════════════════════════════════
def build_banner():
    W, H = 1600, 360
    # Start with solid dark-blue background
    img  = Image.new("RGB", (W, H), pil_color(DARK_BLUE))
    draw = ImageDraw.Draw(img)

    # Subtle top-to-bottom gradient — stay in the dark-blue family
    base   = pil_color(DARK_BLUE)   # (26, 82, 118)
    lighter = (38, 104, 148)         # slightly lighter dark blue at very top
    for y in range(H):
        frac = 1 - y / H
        row_col = tuple(int(base[i] + (lighter[i] - base[i]) * frac * 0.6) for i in range(3))
        draw.line([(0, y), (W, y)], fill=row_col)

    # ── mini heatmap (left panel) — no white cells ────────────────────────────
    cols, rows = 12, 5
    cw, ch, gap = 32, 24, 5
    ox, oy = 64, (H - (rows * ch + (rows - 1) * gap)) // 2
    # Only use mid-to-dark greens so cells are always visible on dark bg
    greens = [
        pil_color("#82E0AA"),   # medium-light
        pil_color("#52BE80"),   # medium
        pil_color(MID_GREEN),   # medium-dark
        pil_color(DARK_GREEN),  # dark
    ]
    rng = np.random.RandomState(7)
    for r in range(rows):
        for c in range(cols):
            shade = greens[rng.randint(0, 4)]
            x0 = ox + c * (cw + gap)
            y0 = oy + r * (ch + gap)
            draw_rounded_rect(draw, (x0, y0, x0 + cw, y0 + ch), 5, shade)

    # ── checkmark circle ──────────────────────────────────────────────────────
    icon_cx = ox + cols * (cw + gap) + 64
    icon_cy = H // 2
    ir = 54
    draw.ellipse([icon_cx - ir, icon_cy - ir, icon_cx + ir, icon_cy + ir],
                 fill=pil_color(MID_BLUE))
    pts = [
        (icon_cx - 28, icon_cy + 2),
        (icon_cx - 8,  icon_cy + 24),
        (icon_cx + 32, icon_cy - 26),
    ]
    draw.line(pts[:2], fill=pil_color(LIGHT_GREEN), width=12)
    draw.line(pts[1:], fill=pil_color(LIGHT_GREEN), width=12)

    # ── text ──────────────────────────────────────────────────────────────────
    tx = icon_cx + ir + 56
    try:
        f_title  = ImageFont.truetype(FONT_BOLD, 54)
        f_sub    = ImageFont.truetype(FONT_REG,  26)
        f_tag    = ImageFont.truetype(FONT_REG,  20)
    except Exception:
        f_title = f_sub = f_tag = ImageFont.load_default()

    draw.text((tx, H // 2 - 76), "Personal Goal &", font=f_title, fill=WHITE)
    draw.text((tx, H // 2 - 12), "Habit Tracker",   font=f_title, fill=pil_color(MID_GREEN))
    draw.text((tx, H // 2 + 58), "LibreOffice Calc Template · Free & Open Source",
              font=f_sub, fill=pil_color(LIGHT_BLUE))

    # Tag pills — single row, guaranteed to fit in remaining width
    tags    = ["Goals", "Daily Habits", "Weekly Review", "Milestones", "Year at a Glance"]
    pill_x  = tx
    pill_y  = H // 2 + 106
    pad_x, pad_y = 14, 7
    for tag in tags:
        bbox = draw.textbbox((0, 0), tag, font=f_tag)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        pw = tw + 2 * pad_x
        ph = th + 2 * pad_y
        draw_rounded_rect(draw, (pill_x, pill_y, pill_x + pw, pill_y + ph),
                          9, pil_color(MID_BLUE))
        draw.text((pill_x + pad_x, pill_y + pad_y), tag, font=f_tag, fill=WHITE)
        pill_x += pw + 12

    out = IMAGES / "logo-banner.png"
    img.save(out, "PNG")
    print(f"  banner → {out}")
    return img


# ═══════════════════════════════════════════════════════════════════════════════
# SCREENSHOT HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def hex_to_mpl(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

def save_fig(fig, name):
    path = IMAGES / name
    fig.savefig(path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  screenshot → {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# SCREENSHOT 1 — Goals Overview
# ═══════════════════════════════════════════════════════════════════════════════
def screenshot_goals_overview():
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor("#F4F6F7")
    ax.set_facecolor("#F4F6F7")
    ax.axis("off")

    # Title bar
    title_rect = FancyBboxPatch((0, 0.93), 1, 0.07,
                                boxstyle="square,pad=0", transform=ax.transAxes,
                                color=hex_to_mpl(DARK_BLUE), zorder=3)
    ax.add_patch(title_rect)
    ax.text(0.5, 0.965, "🎯  Personal Goal & Habit Tracker — Goals Overview",
            transform=ax.transAxes, ha="center", va="center",
            fontsize=13, fontweight="bold", color="white", zorder=4)

    # Table data
    columns = ["Goal", "Category", "Priority", "Target", "% Done", "Status"]
    rows_data = [
        ("Run a half-marathon",        "Health",   "High",   "Oct 2026", "45%",  "On Track"),
        ("Save $5,000 emergency fund", "Finance",  "High",   "Dec 2026", "62%",  "On Track"),
        ("Read 24 books this year",    "Learning", "Medium", "Dec 2026", "50%",  "On Track"),
        ("Learn conversational Spanish","Learning","Medium", "Sep 2026", "30%",  "At Risk"),
        ("Meditate daily for 90 days", "Health",   "Medium", "Sep 2026", "20%",  "At Risk"),
        ("Get promoted to Senior Dev", "Career",   "High",   "Dec 2026", "55%",  "On Track"),
        ("Declutter home — all rooms", "Personal", "Low",    "Aug 2026", "80%",  "On Track"),
        ("Reduce screen time < 2h/day","Health",   "Low",    "Jul 2026", "100%", "Achieved"),
        ("Complete online data course","Learning", "Medium", "Nov 2026", "10%",  "Paused"),
        ("Cook 3 new recipes/month",   "Personal", "Low",    "Dec 2026", "42%",  "On Track"),
    ]

    status_colors = {
        "On Track": hex_to_mpl(LIGHT_GREEN),
        "At Risk":  hex_to_mpl("#FDEBD0"),
        "Achieved": hex_to_mpl(LIGHT_BLUE),
        "Paused":   hex_to_mpl(GREY),
    }

    col_widths = [0.34, 0.12, 0.10, 0.10, 0.08, 0.10]
    col_x = [0.0]
    for w in col_widths[:-1]:
        col_x.append(col_x[-1] + w)

    row_h = 0.072
    header_y = 0.855

    # Header row
    header_bg = FancyBboxPatch((0, header_y), 1, row_h,
                               boxstyle="square,pad=0", transform=ax.transAxes,
                               color=hex_to_mpl(MID_BLUE), zorder=2)
    ax.add_patch(header_bg)
    for i, (col, cx) in enumerate(zip(columns, col_x)):
        ax.text(cx + col_widths[i] / 2, header_y + row_h / 2, col,
                transform=ax.transAxes, ha="center", va="center",
                fontsize=9, fontweight="bold", color="white", zorder=3)

    # Data rows
    for ri, row in enumerate(rows_data):
        y = header_y - (ri + 1) * row_h
        status = row[5]
        bg = status_colors.get(status, (1, 1, 1))
        bg_patch = FancyBboxPatch((0, y), 1, row_h,
                                  boxstyle="square,pad=0", transform=ax.transAxes,
                                  color=bg, zorder=1)
        ax.add_patch(bg_patch)
        for ci, (val, cx) in enumerate(zip(row, col_x)):
            ha = "left" if ci == 0 else "center"
            xpos = cx + 0.006 if ci == 0 else cx + col_widths[ci] / 2
            color = hex_to_mpl(DARK_GREEN) if status == "On Track" else \
                    hex_to_mpl(AMBER)       if status == "At Risk"  else \
                    hex_to_mpl(MID_BLUE)    if status == "Achieved" else \
                    hex_to_mpl("#7F8C8D")
            text_color = color if ci == 5 else hex_to_mpl(TEXT_DARK)
            fw = "bold" if ci == 5 else "normal"
            ax.text(xpos, y + row_h / 2, val,
                    transform=ax.transAxes, ha=ha, va="center",
                    fontsize=8, color=text_color, fontweight=fw)

        # Row separator
        ax.plot([0, 1], [y, y], color="#BDC3C7", linewidth=0.5,
                transform=ax.transAxes, zorder=2)

    # Legend
    legend_y = header_y - (len(rows_data) + 1) * row_h - 0.02
    for label, col in [("On Track", LIGHT_GREEN), ("At Risk", "#FDEBD0"),
                        ("Achieved", LIGHT_BLUE),  ("Paused", GREY)]:
        p = mpatches.Patch(color=hex_to_mpl(col), label=label)
        pass
    ax.legend(
        handles=[
            mpatches.Patch(color=hex_to_mpl(LIGHT_GREEN), label="On Track"),
            mpatches.Patch(color=hex_to_mpl("#FDEBD0"),   label="At Risk"),
            mpatches.Patch(color=hex_to_mpl(LIGHT_BLUE),  label="Achieved"),
            mpatches.Patch(color=hex_to_mpl(GREY),        label="Paused"),
        ],
        loc="lower right", fontsize=8, framealpha=0.9
    )

    fig.suptitle("Sheet 1 · Goals Overview", fontsize=10, color="#7F8C8D",
                 x=0.01, ha="left", y=0.01)
    save_fig(fig, "screenshot-01-goals-overview.png")


# ═══════════════════════════════════════════════════════════════════════════════
# SCREENSHOT 2 — Daily Habits
# ═══════════════════════════════════════════════════════════════════════════════
def screenshot_daily_habits():
    habits = [
        "Exercise 30 min",
        "Read 20 minutes",
        "Meditate 10 min",
        "No alcohol",
        "Drink 64 oz water",
        "8 hours sleep",
    ]
    completions = [
        [1,1,0,1,1,1,0,1,1,1,1,0,1,1,1,0,1,1,1,1,0,1,1,0,1,1,1,1,0],
        [1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1],
        [1,0,1,1,1,1,0,0,1,1,1,0,1,1,0,1,1,1,0,1,1,1,0,1,1,0,1,1,1],
        [1,1,1,1,0,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,1],
        [1,1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,0,1,1,1,1],
        [0,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,0,1,1],
    ]
    today = 29
    days  = list(range(1, 30))

    fig, ax = plt.subplots(figsize=(16, 5.5))
    fig.patch.set_facecolor("#F4F6F7")
    ax.set_facecolor("#F4F6F7")
    ax.axis("off")

    # Title bar
    tp = FancyBboxPatch((0, 0.91), 1, 0.09,
                        boxstyle="square,pad=0", transform=ax.transAxes,
                        color=hex_to_mpl(DARK_BLUE), zorder=3)
    ax.add_patch(tp)
    ax.text(0.5, 0.955, "📅  Daily Habits — June 2026",
            transform=ax.transAxes, ha="center", va="center",
            fontsize=12, fontweight="bold", color="white", zorder=4)

    n_habits = len(habits)
    n_days   = len(days)
    habit_col_w = 0.17
    day_col_w   = (1.0 - habit_col_w - 0.07) / n_days
    row_h       = 0.10
    header_y    = 0.80

    # Header
    hp = FancyBboxPatch((0, header_y), 1, row_h,
                        boxstyle="square,pad=0", transform=ax.transAxes,
                        color=hex_to_mpl(MID_BLUE), zorder=2)
    ax.add_patch(hp)
    ax.text(habit_col_w / 2, header_y + row_h / 2, "Habit",
            transform=ax.transAxes, ha="center", va="center",
            fontsize=8, fontweight="bold", color="white", zorder=3)
    for di, d in enumerate(days):
        cx = habit_col_w + di * day_col_w + day_col_w / 2
        ax.text(cx, header_y + row_h / 2, str(d),
                transform=ax.transAxes, ha="center", va="center",
                fontsize=6.5, fontweight="bold", color="white", zorder=3)
    ax.text(habit_col_w + n_days * day_col_w + 0.035, header_y + row_h / 2, "% Done",
            transform=ax.transAxes, ha="center", va="center",
            fontsize=7.5, fontweight="bold", color="white", zorder=3)

    # Habit rows
    for hi, (habit, comp) in enumerate(zip(habits, completions)):
        y = header_y - (hi + 1) * row_h
        # Habit name cell
        name_bg = FancyBboxPatch((0, y), habit_col_w, row_h,
                                 boxstyle="square,pad=0", transform=ax.transAxes,
                                 color=hex_to_mpl(LIGHT_BLUE), zorder=1)
        ax.add_patch(name_bg)
        ax.text(0.005, y + row_h / 2, habit,
                transform=ax.transAxes, ha="left", va="center",
                fontsize=7.5, fontweight="bold", color=hex_to_mpl(DARK_BLUE))

        done = 0
        for di, d in enumerate(days):
            val = comp[d - 1] if d - 1 < len(comp) else 0
            cx = habit_col_w + di * day_col_w
            bg = hex_to_mpl(LIGHT_GREEN) if val else hex_to_mpl("#FADBD8")
            cell_p = FancyBboxPatch((cx, y), day_col_w, row_h,
                                    boxstyle="square,pad=0", transform=ax.transAxes,
                                    color=bg, zorder=1)
            ax.add_patch(cell_p)
            if val:
                done += 1

        pct = done / today
        pct_col = hex_to_mpl(LIGHT_GREEN) if pct >= 0.8 else \
                  hex_to_mpl("#FDEBD0")   if pct >= 0.6 else \
                  hex_to_mpl("#FADBD8")
        pct_bg = FancyBboxPatch(
            (habit_col_w + n_days * day_col_w, y), 0.07, row_h,
            boxstyle="square,pad=0", transform=ax.transAxes,
            color=pct_col, zorder=1
        )
        ax.add_patch(pct_bg)
        ax.text(habit_col_w + n_days * day_col_w + 0.035, y + row_h / 2,
                f"{int(pct*100)}%",
                transform=ax.transAxes, ha="center", va="center",
                fontsize=8, fontweight="bold",
                color=hex_to_mpl(DARK_GREEN) if pct >= 0.8 else hex_to_mpl(RED))

        ax.plot([0, 1], [y, y], color="#BDC3C7", linewidth=0.4,
                transform=ax.transAxes, zorder=2)

    # Score row
    score_y = header_y - (n_habits + 1) * row_h
    sp = FancyBboxPatch((0, score_y), 1, row_h,
                        boxstyle="square,pad=0", transform=ax.transAxes,
                        color=hex_to_mpl(DARK_BLUE), zorder=1)
    ax.add_patch(sp)
    ax.text(habit_col_w / 2, score_y + row_h / 2, "Daily Score",
            transform=ax.transAxes, ha="center", va="center",
            fontsize=7.5, fontweight="bold", color="white", zorder=3)
    for di, d in enumerate(days):
        total = sum(comp[d - 1] for comp in completions if d - 1 < len(comp))
        cx = habit_col_w + di * day_col_w + day_col_w / 2
        frac = total / n_habits
        col = hex_to_mpl(LIGHT_GREEN) if frac >= 0.8 else \
              hex_to_mpl("#FDEBD0")   if frac >= 0.5 else \
              hex_to_mpl("#FADBD8")
        ax.text(cx, score_y + row_h / 2, f"{total}/{n_habits}",
                transform=ax.transAxes, ha="center", va="center",
                fontsize=5.5, fontweight="bold",
                color=hex_to_mpl(DARK_GREEN) if frac >= 0.8 else hex_to_mpl(RED), zorder=3)

    fig.suptitle("Sheet 2 · Daily Habits", fontsize=10, color="#7F8C8D",
                 x=0.01, ha="left", y=0.01)
    save_fig(fig, "screenshot-02-daily-habits.png")


# ═══════════════════════════════════════════════════════════════════════════════
# SCREENSHOT 3 — Weekly Review
# ═══════════════════════════════════════════════════════════════════════════════
def screenshot_weekly_review():
    weeks = [
        {
            "label": "Week 1 — 1 Jun to 7 Jun",
            "well":  "Maintained exercise streak all 7 days. Finished two book chapters ahead of schedule.",
            "challenge": "Struggled with meditation after late work nights.",
            "kept":  "Exercise, Reading, No Alcohol, Water intake",
            "missed":"Meditation (2 days). Late nights disrupted routine.",
            "focus": "Set a phone alarm at 9 pm as a meditation reminder.",
        },
        {
            "label": "Week 2 — 8 Jun to 14 Jun",
            "well":  "Completed first 6-mile run without stopping — biggest distance yet.",
            "challenge": "Spanish practice fell to zero; kept de-prioritising it.",
            "kept":  "Exercise, Reading, Water, Sleep",
            "missed":"Meditation (1 day), Spanish study (5 days).",
            "focus": "Block 20 min Spanish practice every weekday morning.",
        },
        {
            "label": "Week 3 — 15 Jun to 21 Jun",
            "well":  "Hit savings milestone: $3,000 saved. Decluttered the spare room.",
            "challenge": "Thursday social event caused one missed no-alcohol day.",
            "kept":  "Exercise, Reading, Meditation, Water, Sleep",
            "missed":"No Alcohol (1 day — planned social event).",
            "focus": "Plan for social events in advance — decide on limits beforehand.",
        },
        {
            "label": "Week 4 — 22 Jun to 28 Jun",
            "well":  "Spanish momentum returning: used the app 5 of 7 days. Sleep improving.",
            "challenge": "Exercise skipped Saturday due to injury scare (left knee).",
            "kept":  "Reading, Meditation, No Alcohol, Water, Sleep",
            "missed":"Exercise (1 day — knee rest). Monitoring closely.",
            "focus": "Substitute swimming for running while knee recovers.",
        },
    ]
    prompts = [
        ("What went well?",        "well"),
        ("What was challenging?",  "challenge"),
        ("Habits maintained",      "kept"),
        ("Habits missed & why",    "missed"),
        ("Focus for next week",    "focus"),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(18, 8))
    fig.patch.set_facecolor("#F4F6F7")

    for ax, week in zip(axes, weeks):
        ax.set_facecolor("#F4F6F7")
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        # Week header
        hp = FancyBboxPatch((0, 0.91), 1, 0.09,
                            boxstyle="square,pad=0", transform=ax.transAxes,
                            color=hex_to_mpl(MID_BLUE), zorder=2)
        ax.add_patch(hp)
        ax.text(0.5, 0.955, week["label"],
                transform=ax.transAxes, ha="center", va="center",
                fontsize=7.5, fontweight="bold", color="white", zorder=3)

        row_h = 0.155
        cur_y = 0.88
        for label, key in prompts:
            cur_y -= row_h
            lp = FancyBboxPatch((0, cur_y), 1, row_h,
                                boxstyle="square,pad=0", transform=ax.transAxes,
                                color=hex_to_mpl("#EBF5FB"), zorder=1)
            ax.add_patch(lp)
            ax.text(0.02, cur_y + row_h - 0.02, label,
                    transform=ax.transAxes, ha="left", va="top",
                    fontsize=6.5, fontweight="bold", color=hex_to_mpl(MID_BLUE))
            ax.text(0.02, cur_y + 0.01, week[key],
                    transform=ax.transAxes, ha="left", va="bottom",
                    fontsize=6, color=hex_to_mpl(TEXT_DARK),
                    wrap=True)
            ax.plot([0, 1], [cur_y, cur_y], color="#BDC3C7", linewidth=0.4,
                    transform=ax.transAxes, zorder=2)

    fig.suptitle("Sheet 3 · Weekly Review", fontsize=11, color="#7F8C8D",
                 x=0.01, ha="left")
    save_fig(fig, "screenshot-03-weekly-review.png")


# ═══════════════════════════════════════════════════════════════════════════════
# SCREENSHOT 4 — Milestones
# ═══════════════════════════════════════════════════════════════════════════════
def screenshot_milestones():
    milestones = [
        ("5 Jan",  "Set up tracker — 10 clear goals for 2026",    "All goals",      "Excited and a little nervous."),
        ("12 Feb", "Read 4th book of the year",                   "Read 24 books",  "Reading habit has genuinely stuck."),
        ("1 Mar",  "First month no missed exercise — 28/28",      "Half-marathon",  "Proud. Consistency is possible."),
        ("22 Mar", "Passed the $1,000 emergency fund threshold",  "Emergency fund", "Relieved. Real security building."),
        ("7 Apr",  "Completed 30-day meditation streak",          "Meditate 90d",   "Calm. Habit feels effortless."),
        ("19 Apr", "Ran 6 miles for the first time",              "Half-marathon",  "Euphoric. 4 months of progress."),
        ("3 May",  "Decluttered kitchen and living room",         "Declutter home", "Light. Space feels totally different."),
        ("20 May", "Screen time first week under 2 hours avg",    "Screen time",    "Surprised it worked."),
        ("1 Jun",  "Hit $3,000 in savings — 60% of goal",        "Emergency fund", "Motivated. On track for $5k Oct."),
        ("10 Jun", "Read book #12 — halfway to 24-book challenge","Read 24 books",  "The evening reading is non-negotiable."),
        ("15 Jun", "Best 6-mile time: 51:34 — new PR",           "Half-marathon",  "Emotional. Early mornings paid off."),
        ("21 Jun", "Decluttered spare room — 4 of 5 rooms done", "Declutter home", "One room to go — the garage."),
        ("28 Jun", "First Spanish conversation with native (10 min)","Spanish",     "Giddy. Awkward practice was worth it."),
    ]
    columns = ["Date", "Milestone", "Related Goal", "How I Felt"]

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor("#F4F6F7")
    ax.set_facecolor("#F4F6F7")
    ax.axis("off")

    tp = FancyBboxPatch((0, 0.93), 1, 0.07,
                        boxstyle="square,pad=0", transform=ax.transAxes,
                        color=hex_to_mpl(DARK_BLUE), zorder=3)
    ax.add_patch(tp)
    ax.text(0.5, 0.965, "🏆  Milestones & Achievements — 2026",
            transform=ax.transAxes, ha="center", va="center",
            fontsize=12, fontweight="bold", color="white", zorder=4)

    col_w = [0.07, 0.42, 0.20, 0.31]
    col_x = [0.0]
    for w in col_w[:-1]:
        col_x.append(col_x[-1] + w)
    row_h = 0.062
    header_y = 0.855

    hp = FancyBboxPatch((0, header_y), 1, row_h,
                        boxstyle="square,pad=0", transform=ax.transAxes,
                        color=hex_to_mpl(MID_BLUE), zorder=2)
    ax.add_patch(hp)
    for i, (col, cx) in enumerate(zip(columns, col_x)):
        ax.text(cx + col_w[i] / 2, header_y + row_h / 2, col,
                transform=ax.transAxes, ha="center", va="center",
                fontsize=9, fontweight="bold", color="white", zorder=3)

    for ri, row in enumerate(milestones):
        y = header_y - (ri + 1) * row_h
        bg = FancyBboxPatch((0, y), 1, row_h,
                            boxstyle="square,pad=0", transform=ax.transAxes,
                            color=hex_to_mpl(LIGHT_GREEN) if ri % 2 == 0 else (1, 1, 1), zorder=1)
        ax.add_patch(bg)
        for ci, (val, cx) in enumerate(zip(row, col_x)):
            ha = "center" if ci == 0 else "left"
            x  = cx + col_w[ci] / 2 if ci == 0 else cx + 0.005
            ax.text(x, y + row_h / 2, val,
                    transform=ax.transAxes, ha=ha, va="center",
                    fontsize=7.5 if ci != 1 else 7,
                    color=hex_to_mpl(DARK_BLUE) if ci == 0 else hex_to_mpl(TEXT_DARK),
                    fontweight="bold" if ci in (0, 2) else "normal")
        ax.plot([0, 1], [y, y], color="#BDC3C7", linewidth=0.4,
                transform=ax.transAxes, zorder=2)

    fig.suptitle("Sheet 4 · Milestones", fontsize=10, color="#7F8C8D",
                 x=0.01, ha="left", y=0.01)
    save_fig(fig, "screenshot-04-milestones.png")


# ═══════════════════════════════════════════════════════════════════════════════
# SCREENSHOT 5 — Year at a Glance (heatmap)
# ═══════════════════════════════════════════════════════════════════════════════
def screenshot_year_at_glance():
    import random
    random.seed(42)

    habits = [
        "Exercise 30 min",
        "Read 20 minutes",
        "Meditate 10 min",
        "No alcohol",
        "Drink 64 oz water",
        "8 hours sleep",
    ]
    n_habits = len(habits)
    n_weeks  = 52
    today_week = 26

    def week_score(h_idx, w):
        base  = 3.5 + (w / 52) * 2.0
        noise = random.gauss(0, 1.2)
        score = base + noise
        if h_idx == 2:
            score -= 0.8
        if w > today_week:
            return None
        return max(0, min(7, round(score)))

    data = np.full((n_habits, n_weeks), np.nan)
    for h in range(n_habits):
        for w in range(1, n_weeks + 1):
            s = week_score(h, w)
            if s is not None:
                data[h, w - 1] = s

    fig, ax = plt.subplots(figsize=(18, 4.5))
    fig.patch.set_facecolor("#F4F6F7")
    ax.set_facecolor("#F4F6F7")

    # Custom green colormap (white → dark green)
    from matplotlib.colors import LinearSegmentedColormap
    green_cmap = LinearSegmentedColormap.from_list(
        "habit_green",
        ["#FDFEFE", "#D5F5E3", "#82E0AA", "#27AE60", "#1E8449", "#145A32"],
        N=256
    )

    # Grey for future weeks
    masked = np.ma.masked_invalid(data)
    im = ax.imshow(masked, aspect="auto", cmap=green_cmap, vmin=0, vmax=7,
                   interpolation="nearest")

    # Overlay grey for future
    future_mask = np.zeros_like(data, dtype=float)
    for w in range(today_week, n_weeks):
        future_mask[:, w] = 1
    grey_cmap = matplotlib.colors.ListedColormap(["none", "#F2F3F4"])
    ax.imshow(future_mask, aspect="auto", cmap=grey_cmap, vmin=0, vmax=1,
              interpolation="nearest", alpha=0.9)

    # Axes
    ax.set_yticks(range(n_habits))
    ax.set_yticklabels(habits, fontsize=9)
    month_ticks = [int(m * 52 / 12) for m in range(12)]
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    ax.set_xticks(month_ticks)
    ax.set_xticklabels(months, fontsize=8)
    ax.set_xlim(-0.5, n_weeks - 0.5)

    # Title
    ax.set_title("📊  Year at a Glance — Habit Heatmap 2026   (darker = more consistent)",
                 fontsize=11, fontweight="bold", color=hex_to_mpl(DARK_BLUE), pad=10)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, orientation="vertical", pad=0.01, fraction=0.015)
    cbar.set_label("Days completed / week", fontsize=8)
    cbar.set_ticks([0, 1, 2, 3, 4, 5, 6, 7])

    # "Today" line
    ax.axvline(today_week - 0.5, color=hex_to_mpl(AMBER), linewidth=1.8,
               linestyle="--", label="Today (end of June)")
    ax.legend(fontsize=8, loc="upper left")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    fig.text(0.01, 0.01, "Sheet 5 · Year at a Glance", fontsize=9,
             color="#7F8C8D", ha="left")
    save_fig(fig, "screenshot-05-year-at-a-glance.png")


# ═══════════════════════════════════════════════════════════════════════════════
# COMPOSITE — all screenshots in one overview image
# ═══════════════════════════════════════════════════════════════════════════════
def build_composite():
    shot_files = [
        IMAGES / "screenshot-01-goals-overview.png",
        IMAGES / "screenshot-02-daily-habits.png",
        IMAGES / "screenshot-03-weekly-review.png",
        IMAGES / "screenshot-04-milestones.png",
        IMAGES / "screenshot-05-year-at-a-glance.png",
    ]
    imgs = [Image.open(f) for f in shot_files]

    # Scale each to the same width
    target_w = 1400
    scaled = []
    for img in imgs:
        ratio = target_w / img.width
        scaled.append(img.resize((target_w, int(img.height * ratio)), Image.LANCZOS))

    # Stack vertically with a header bar
    header_h = 80
    gap      = 16
    total_h  = header_h + sum(s.height for s in scaled) + gap * (len(scaled) + 1)
    composite = Image.new("RGB", (target_w, total_h), pil_color("#F4F6F7"))

    draw = ImageDraw.Draw(composite)
    draw_rounded_rect(draw, (0, 0, target_w, header_h), 0, pil_color(DARK_BLUE))
    try:
        f = ImageFont.truetype(FONT_BOLD, 32)
    except Exception:
        f = ImageFont.load_default()
    draw.text((target_w // 2, header_h // 2),
              "Personal Goal & Habit Tracker — Template Preview",
              font=f, fill=WHITE, anchor="mm")

    y = header_h + gap
    for s in scaled:
        composite.paste(s, (0, y))
        y += s.height + gap

    out = IMAGES / "preview-all-sheets.png"
    composite.save(out, "PNG")
    print(f"  composite → {out}")


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Building logos...")
    build_icon()
    build_banner()

    print("Building screenshots...")
    screenshot_goals_overview()
    screenshot_daily_habits()
    screenshot_weekly_review()
    screenshot_milestones()
    screenshot_year_at_glance()

    print("Building composite preview...")
    build_composite()

    print("\nDone. Files in:", IMAGES)
    for f in sorted(IMAGES.iterdir()):
        size = f.stat().st_size // 1024
        print(f"  {f.name:45s}  {size:4d} KB")
