"""
Zurich Partnervorstellungs-Post
Exaktes Layout-Replikat des CrossConsulting-Posts.
Nur Texte, Zahlen und Logo sind auf Zurich angepasst.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, urllib.request, tempfile

# ── Page dimensions (identical to CrossConsulting PDF) ──────────────────────
PW = 810
PH = 1013.04

# ── Brand colours ────────────────────────────────────────────────────────────
C_PRIMARY   = colors.HexColor("#0E4B94")   # dark blue
C_TEAL      = colors.HexColor("#2CD9C3")   # teal / secondary
C_DARK      = colors.HexColor("#0e0e1b")   # near-black text
C_MID       = colors.HexColor("#6B7280")   # mid grey
C_LIGHT_BG  = colors.HexColor("#EAF1F8")   # stat-box bg
C_WHITE     = colors.white
C_LABEL     = colors.HexColor("#4B9EAF")   # "PARTNERVORSTELLUNG" label colour

# ── Asset paths ───────────────────────────────────────────────────────────────
DIR      = "/home/user/nextgen-webseite-test1"
NG_LOGO  = f"{DIR}/src/images/logo.png"
ZU_LOGO  = f"{DIR}/src/images/zurich_uebereinander.png"
OUTPUT   = f"{DIR}/NextGenPartnerPost_Zurich.pdf"

# ── Helpers ───────────────────────────────────────────────────────────────────

def bg(c):
    """Soft diagonal gradient background (top-right light-teal → bottom-left white)."""
    steps = 80
    for i in range(steps):
        t = i / steps
        r = 1.0  - t * 0.06
        g = 1.0  - t * 0.02
        b = 1.0  + t * 0.00   # stays white-ish but slightly cooler top
        # top strip lighter / bottom slightly warmer white
        # Actually replicate: very light cyan tint at top, plain white at bottom
        r2 = 0.94 + (1 - t) * 0.06
        g2 = 0.96 + (1 - t) * 0.04
        b2 = 0.99 + (1 - t) * 0.01
        c.setFillColorRGB(r2, g2, b2)
        c.rect(0, PH * i / steps, PW, PH / steps + 1, stroke=0, fill=1)


def header(c, slide_num, slide_title):
    """Top header: NextGen logo left, separator line, slide counter right."""
    # logo
    logo_h = 38
    try:
        img = ImageReader(NG_LOGO)
        iw, ih = img.getSize()
        logo_w = logo_h * iw / ih
        c.drawImage(NG_LOGO, 48, PH - 62, width=logo_w, height=logo_h,
                    mask='auto', preserveAspectRatio=True)
    except Exception:
        pass
    # horizontal rule
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.setLineWidth(0.8)
    c.line(48, PH - 72, PW - 48, PH - 72)
    # slide counter
    c.setFillColor(C_MID)
    c.setFont("Helvetica", 11)
    counter = f"● {slide_num:02d} / 04 · {slide_title}"
    c.drawRightString(PW - 48, PH - 62, counter)


def footer(c):
    """Bottom separator line + footer text."""
    c.setStrokeColor(colors.HexColor("#CBD5E1"))
    c.setLineWidth(0.8)
    c.line(48, 52, PW - 48, 52)
    c.setFillColor(C_MID)
    c.setFont("Helvetica", 11)
    c.drawString(48, 32, "Vernetzung. Förderung. Zukunft.")
    c.drawRightString(PW - 48, 32, "nextgenforum.de")


def gradient_pill(c, x, y, w, h, text, font="Helvetica-Bold", fsize=13):
    """Rounded pill with horizontal gradient (primary→teal), white text."""
    steps = 60
    r_save = 8
    # clip to rounded rect
    p = c.beginPath()
    p.roundRect(x, y, w, h, r_save)
    c.saveState()
    c.clipPath(p, stroke=0, fill=0)
    for i in range(steps):
        t = i / steps
        r = C_PRIMARY.red   + t * (C_TEAL.red   - C_PRIMARY.red)
        g = C_PRIMARY.green + t * (C_TEAL.green - C_PRIMARY.green)
        b = C_PRIMARY.blue  + t * (C_TEAL.blue  - C_PRIMARY.blue)
        c.setFillColorRGB(r, g, b)
        c.rect(x + i * w / steps, y, w / steps + 1, h, stroke=0, fill=1)
    c.restoreState()
    c.setFillColor(C_WHITE)
    c.setFont(font, fsize)
    c.drawCentredString(x + w / 2, y + (h - fsize) / 2 + 2, text)


def gradient_word_approx(c, x, y, word, font="Helvetica-Bold", size=58):
    """Approximate gradient text: render in teal (visual stand-in for gradient)."""
    c.setFillColor(C_TEAL)
    c.setFont(font, size)
    c.drawString(x, y, word)
    return c.stringWidth(word, font, size)


def draw_icon(c, cx, cy, kind):
    """Draw a simple teal icon shape for stat boxes."""
    c.setFillColor(C_TEAL)
    c.setStrokeColor(C_TEAL)
    c.setLineWidth(1.5)
    if kind == "calendar":
        # Simple rectangle with top notch lines
        c.roundRect(cx - 9, cy - 9, 18, 18, 2, stroke=1, fill=0)
        c.line(cx - 9, cy + 3, cx + 9, cy + 3)
        c.line(cx - 3, cy + 9, cx - 3, cy + 12)
        c.line(cx + 3, cy + 9, cx + 3, cy + 12)
    elif kind == "people":
        # Head circle + body arc
        c.circle(cx, cy + 5, 5, stroke=1, fill=0)
        p = c.beginPath()
        p.arc(cx - 9, cy - 8, cx + 9, cy + 4, startAng=200, extent=140)
        c.drawPath(p, stroke=1, fill=0)
    elif kind == "location":
        # Pin: circle + triangle/tail
        c.circle(cx, cy + 5, 6, stroke=1, fill=0)
        c.setFillColor(C_TEAL)
        p = c.beginPath()
        p.moveTo(cx - 3, cy + 1)
        p.lineTo(cx + 3, cy + 1)
        p.lineTo(cx, cy - 9)
        p.close()
        c.drawPath(p, stroke=0, fill=1)
    elif kind == "trending":
        # Upward arrow line
        c.line(cx - 9, cy - 6, cx + 4, cy + 7)
        c.line(cx - 1, cy + 7, cx + 4, cy + 7)
        c.line(cx + 4, cy + 7, cx + 4, cy + 2)
    c.setLineWidth(0.5)


def stat_box(c, x, y, w, h, icon_kind, label, value_lines):
    """White rounded stat card."""
    c.setFillColor(C_WHITE)
    c.setStrokeColor(colors.HexColor("#E2EAF0"))
    c.setLineWidth(0.5)
    c.roundRect(x, y, w, h, 12, stroke=1, fill=1)
    # icon
    draw_icon(c, x + w / 2, y + h - 42, icon_kind)
    # label
    c.setFillColor(C_MID)
    c.setFont("Helvetica", 10)
    c.drawCentredString(x + w / 2, y + h - 66, label)
    # value
    c.setFillColor(C_DARK)
    c.setFont("Helvetica-Bold", 26)
    if isinstance(value_lines, list):
        line_h = 30
        start_y = y + h / 2 - (len(value_lines) - 1) * line_h / 2 - 6
        for i, vl in enumerate(value_lines):
            c.drawCentredString(x + w / 2, start_y + (len(value_lines) - 1 - i) * line_h, vl)
    else:
        c.drawCentredString(x + w / 2, y + h / 2 - 14, value_lines)


def wrap_text(c, text, x, y, max_w, font, size, leading, color=None):
    """Simple word-wrap, returns final y."""
    if color:
        c.setFillColor(color)
    c.setFont(font, size)
    words = text.split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if c.stringWidth(test, font, size) <= max_w:
            line = test
        else:
            c.drawString(x, y, line)
            y -= leading
            line = w
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y


# ── Page 1 · Cover ────────────────────────────────────────────────────────────

def page1(c):
    bg(c)
    header(c, 1, "Workshop 4")

    # "PARTNERVORSTELLUNG" label
    c.setFillColor(C_LABEL)
    c.setFont("Helvetica-Bold", 12)
    label = "PARTNERVORSTELLUNG"
    label_w = c.stringWidth(label, "Helvetica-Bold", 12)
    c.drawCentredString(PW / 2, PH - 175, label)

    # Zurich logo centred
    try:
        img = ImageReader(ZU_LOGO)
        iw, ih = img.getSize()
        logo_h = 160
        logo_w = logo_h * iw / ih
        c.drawImage(ZU_LOGO, (PW - logo_w) / 2, PH - 390,
                    width=logo_w, height=logo_h, mask='auto',
                    preserveAspectRatio=True)
    except Exception:
        c.setFillColor(C_PRIMARY)
        c.setFont("Helvetica-Bold", 64)
        c.drawCentredString(PW / 2, PH - 350, "ZURICH")

    # Tagline
    c.setFillColor(C_DARK)
    c.setFont("Helvetica", 24)
    c.drawCentredString(PW / 2, PH - 480, "Globale Versicherungskompetenz.")
    c.drawCentredString(PW / 2, PH - 510, "Lokal verankert in Köln.")

    # Gradient event pill
    pill_text = "MITTWOCH   08.07.2026  ·  17:00 Uhr  ·  Zurich – Office Köln"
    pill_w, pill_h = 680, 50
    pill_x = (PW - pill_w) / 2
    gradient_pill(c, pill_x, PH - 640, pill_w, pill_h, pill_text, fsize=14)

    footer(c)


# ── Page 2 · Das Unternehmen ──────────────────────────────────────────────────

def page2(c):
    bg(c)
    header(c, 2, "Das Unternehmen")

    # Headline: "Weltklasse trifft [Teal]Köln."
    c.setFillColor(C_DARK)
    c.setFont("Helvetica-Bold", 58)
    w1 = c.stringWidth("Weltklasse trifft ", "Helvetica-Bold", 58)
    c.drawString(48, PH - 185, "Weltklasse trifft ")
    gradient_word_approx(c, 48 + w1, PH - 185, "Köln.", "Helvetica-Bold", 58)

    # Body paragraph
    body = (
        "Die Zurich Insurance Group zählt zu den führenden Versicherern weltweit. "
        "In Deutschland ist Zurich seit über 100 Jahren aktiv und begleitet "
        "Privat- und Geschäftskunden mit ganzheitlichen Lösungen in Schaden-, "
        "Unfall- und Lebensversicherung – nachhaltig, digital und zukunftsorientiert."
    )
    wrap_text(c, body, 48, PH - 260, PW - 96, "Helvetica", 16, 24,
              color=C_MID)

    # 2×2 stat grid
    gx, gy = 48, PH - 700
    bw = (PW - 96 - 20) / 2
    bh = 180
    gap = 20

    stat_box(c, gx,             gy + bh + gap, bw, bh, "calendar", "GEGRÜNDET",    "1872")
    stat_box(c, gx + bw + gap, gy + bh + gap, bw, bh, "people",   "MITARBEITENDE", "~ 55.000")
    stat_box(c, gx,             gy,            bw, bh, "location", "HAUPTSITZ",
             ["Zürich (CH)", "Köln (DE)"])
    stat_box(c, gx + bw + gap, gy,            bw, bh, "trending",  "SCHWERPUNKTE",
             ["Schaden/Unfall", "Lebensversicherung", "Industrie"])

    footer(c)


# ── Page 3 · Die Speaker ──────────────────────────────────────────────────────

def page3(c):
    bg(c)
    header(c, 3, "Die Speaker")

    # Headline "Eure [Teal]Speaker"
    c.setFillColor(C_DARK)
    c.setFont("Helvetica-Bold", 58)
    w1 = c.stringWidth("Eure ", "Helvetica-Bold", 58)
    c.drawString(48, PH - 185, "Eure ")
    gradient_word_approx(c, 48 + w1, PH - 185, "Speaker", "Helvetica-Bold", 58)

    # ── Two speaker cards ──
    cw = (PW - 96 - 20) / 2
    ch = 230
    cy = PH - 460

    def speaker_card(cx, initials, name, role):
        c.setFillColor(C_WHITE)
        c.setStrokeColor(colors.HexColor("#E2EAF0"))
        c.setLineWidth(0.5)
        c.roundRect(cx, cy, cw, ch, 12, stroke=1, fill=1)
        # avatar circle
        av_r = 34
        av_cx = cx + cw / 2
        av_cy = cy + ch - 60
        c.setFillColor(colors.HexColor("#D6EAF2"))
        c.circle(av_cx, av_cy, av_r, fill=1, stroke=0)
        c.setFillColor(C_PRIMARY)
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(av_cx, av_cy - 8, initials)
        # Name
        c.setFillColor(C_DARK)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(cx + cw / 2, cy + ch - 118, name)
        # Role
        c.setFillColor(C_MID)
        c.setFont("Helvetica-Oblique", 12)
        c.drawCentredString(cx + cw / 2, cy + ch - 140, role)
        # Company
        c.setFillColor(C_TEAL)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(cx + cw / 2, cy + ch - 162, "Zurich Insurance")
        # Location
        # location pin + KÖLN
        pin_lbl = "KOLN"
        pin_w = c.stringWidth(pin_lbl, "Helvetica", 11) + 18
        pin_x = cx + cw / 2 - pin_w / 2
        c.saveState()
        c.setStrokeColor(C_MID); c.setFillColor(C_MID); c.setLineWidth(1.0)
        draw_icon(c, pin_x + 7, cy + ch - 179, "location")
        c.restoreState()
        c.setFillColor(C_MID)
        c.setFont("Helvetica", 11)
        c.drawString(pin_x + 18, cy + ch - 183, pin_lbl)

    speaker_card(48,          "NN", "[Vorname Nachname]", "[Funktion]")
    speaker_card(48 + cw + 20, "NN", "[Vorname Nachname]", "[Funktion]")

    # ── HR contact row ──
    hr_y = cy - 74
    hr_h = 54
    c.setFillColor(C_WHITE)
    c.setStrokeColor(colors.HexColor("#E2EAF0"))
    c.setLineWidth(0.5)
    c.roundRect(48, hr_y, PW - 96, hr_h, 10, stroke=1, fill=1)
    # HR avatar
    c.setFillColor(colors.HexColor("#D6EAF2"))
    c.circle(48 + 28, hr_y + hr_h / 2, 20, fill=1, stroke=0)
    c.setFillColor(C_PRIMARY)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(48 + 28, hr_y + hr_h / 2 - 4, "HR")
    # HR name + title
    c.setFillColor(C_DARK)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(48 + 58, hr_y + hr_h / 2 + 4, "[Ansprechpartner:in Karriere]")
    c.setFillColor(C_MID)
    c.setFont("Helvetica", 11)
    c.drawString(48 + 58, hr_y + hr_h / 2 - 14, "Ansprechpartner:in Karriere · Zurich Insurance")
    # HR badge right
    badge_w, badge_h = 36, 22
    badge_x = PW - 48 - badge_w - 12
    badge_y = hr_y + (hr_h - badge_h) / 2
    c.setFillColor(C_PRIMARY)
    c.roundRect(badge_x, badge_y, badge_w, badge_h, 5, stroke=0, fill=1)
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(badge_x + badge_w / 2, badge_y + 6, "HR")

    # ── Bottom info bar (gradient) ──
    bar_h = 52
    bar_y = hr_y - 72
    bar_w = PW - 96
    # gradient fill
    steps = 60
    p = c.beginPath()
    p.roundRect(48, bar_y, bar_w, bar_h, 10)
    c.saveState()
    c.clipPath(p, stroke=0, fill=0)
    for i in range(steps):
        t = i / steps
        r = C_PRIMARY.red   + t * (C_TEAL.red   - C_PRIMARY.red)
        g = C_PRIMARY.green + t * (C_TEAL.green - C_PRIMARY.green)
        b = C_PRIMARY.blue  + t * (C_TEAL.blue  - C_PRIMARY.blue)
        c.setFillColorRGB(r, g, b)
        c.rect(48 + i * bar_w / steps, bar_y, bar_w / steps + 1, bar_h, stroke=0, fill=1)
    c.restoreState()
    # three columns
    col_w = bar_w / 3
    col_icons   = ["trending", "people", "calendar"]
    col_labels  = ["THEMA", "FORMAT", "ANSCHLUSS"]
    col_values  = ["[Thema folgt in Kurze]", "Interaktiver Workshop", "Networking-Dinner"]
    for i in range(3):
        cx = 48 + i * col_w + col_w / 2
        c.setFillColor(colors.HexColor("#FFFFFFAA"))
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(cx, bar_y + bar_h - 18, col_labels[i])
        # small white icon drawn at bar_y+20
        c.saveState()
        c.setFillColor(C_WHITE)
        c.setStrokeColor(C_WHITE)
        c.setLineWidth(1.2)
        draw_icon(c, cx - c.stringWidth(col_values[i], "Helvetica-Bold", 12)/2 - 10,
                  bar_y + 16, col_icons[i])
        c.restoreState()
        c.setFillColor(C_WHITE)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(cx + 6, bar_y + 12, col_values[i])
    # vertical dividers
    c.setStrokeColor(colors.HexColor("#FFFFFF50"))
    c.setLineWidth(0.8)
    for i in [1, 2]:
        dx = 48 + i * col_w
        c.line(dx, bar_y + 8, dx, bar_y + bar_h - 8)

    footer(c)


# ── Page 4 · Jetzt anmelden ───────────────────────────────────────────────────

def page4(c):
    bg(c)
    header(c, 4, "Jetzt anmelden")

    # "BEREIT FÜR DEN WORKSHOP?"
    c.setFillColor(C_LABEL)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(PW / 2, PH - 195, "BEREIT FÜR DEN WORKSHOP?")

    # "Jetzt" plain dark
    c.setFillColor(C_DARK)
    c.setFont("Helvetica-Bold", 82)
    c.drawCentredString(PW / 2, PH - 298, "Jetzt")

    # "bewerben." in teal (gradient approximation)
    c.setFillColor(C_TEAL)
    c.setFont("Helvetica-Bold", 82)
    c.drawCentredString(PW / 2, PH - 390, "bewerben.")

    # Body text – two centred lines matching CrossConsulting layout
    c.setFillColor(C_DARK)
    c.setFont("Helvetica", 17)
    c.drawCentredString(PW / 2, PH - 488,
                        "Sichere dir deinen Platz beim Workshop bei")
    # bold company name inline
    line2_parts = [("Zurich", True), (" – begrenzte Platze, Bewerbung in wenigen Minuten.", False)]
    total = sum(c.stringWidth(t, "Helvetica-Bold" if b else "Helvetica", 17)
                for t, b in line2_parts)
    lx = PW / 2 - total / 2
    for txt, bold in line2_parts:
        fn = "Helvetica-Bold" if bold else "Helvetica"
        c.setFont(fn, 17)
        c.drawString(lx, PH - 516, txt)
        lx += c.stringWidth(txt, fn, 17)

    # CTA pill button
    gradient_pill(c, (PW - 480) / 2, PH - 640, 480, 56,
                  "→  nextgenforum.de/jetzt-bewerben", fsize=16)

    # Date + location row
    c.setFillColor(C_MID)
    c.setFont("Helvetica", 13)
    info = "Mi  08.07.2026  17:00 Uhr    Zurich Office Koln"
    row_y = PH - 730
    # draw two small icons + text
    full = "Mi · 08.07.2026 · 17:00 Uhr"
    loc  = "Zurich Office Koln"
    total_w = (c.stringWidth(full, "Helvetica", 13) + 28 +
               8 +
               c.stringWidth(loc,  "Helvetica", 13) + 28)
    sx = PW / 2 - total_w / 2
    # calendar icon
    c.saveState()
    c.setStrokeColor(C_MID); c.setFillColor(C_MID); c.setLineWidth(1.2)
    draw_icon(c, sx + 8, row_y + 5, "calendar")
    c.restoreState()
    c.setFillColor(C_MID)
    c.setFont("Helvetica", 13)
    c.drawString(sx + 22, row_y, full)
    sep_x = sx + 22 + c.stringWidth(full, "Helvetica", 13) + 12
    c.drawString(sep_x, row_y, "·")
    loc_x = sep_x + 16
    c.saveState()
    c.setStrokeColor(C_MID); c.setFillColor(C_MID); c.setLineWidth(1.2)
    draw_icon(c, loc_x + 8, row_y + 5, "location")
    c.restoreState()
    c.setFillColor(C_MID)
    c.drawString(loc_x + 22, row_y, loc)

    footer(c)


# ── Generate ──────────────────────────────────────────────────────────────────

cv = canvas.Canvas(OUTPUT, pagesize=(PW, PH))
cv.setTitle("Partnervorstellung – Zurich | NextGen Insurance Forum e.V.")
cv.setAuthor("NextGen Insurance Forum e.V.")

page1(cv); cv.showPage()
page2(cv); cv.showPage()
page3(cv); cv.showPage()
page4(cv); cv.showPage()

cv.save()
print(f"✓ PDF gespeichert → {OUTPUT}")
