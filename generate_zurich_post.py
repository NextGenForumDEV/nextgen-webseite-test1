from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

# Brand colours
PRIMARY   = colors.HexColor("#0E4B94")
SECONDARY = colors.HexColor("#2CD9C3")
DARK_TEXT = colors.HexColor("#0e0e1b")
MID_GREY  = colors.HexColor("#6B7280")
LIGHT_BG  = colors.HexColor("#F4F7F6")
WHITE     = colors.white

PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm
INNER_W = PAGE_W - 2 * MARGIN

LOGO_PATH = "/home/user/nextgen-webseite-test1/src/images/zurich_uebereinander.png"
NG_LOGO   = "/home/user/nextgen-webseite-test1/src/images/logo.png"

OUTPUT = "/home/user/nextgen-webseite-test1/NextGenPartnerPost_Zurich.pdf"


# ── helpers ────────────────────────────────────────────────────────────────

def draw_gradient_bar(c, x, y, w, h=0.45*cm):
    """Horizontal gradient bar (primary → secondary)."""
    steps = 60
    for i in range(steps):
        t = i / steps
        r = PRIMARY.red   + t * (SECONDARY.red   - PRIMARY.red)
        g = PRIMARY.green + t * (SECONDARY.green - PRIMARY.green)
        b = PRIMARY.blue  + t * (SECONDARY.blue  - PRIMARY.blue)
        c.setFillColorRGB(r, g, b)
        c.rect(x + i * w / steps, y, w / steps + 1, h, stroke=0, fill=1)

def draw_footer(c, page_num, total=4):
    c.saveState()
    # gradient bar at bottom
    draw_gradient_bar(c, 0, 1.1*cm, PAGE_W, 0.22*cm)
    c.setFont("Helvetica", 7)
    c.setFillColor(MID_GREY)
    footer_text = "Vernetzung. Förderung. Zukunft."
    c.drawString(MARGIN, 0.65*cm, footer_text)
    c.drawRightString(PAGE_W - MARGIN, 0.65*cm, "nextgenforum.de")
    # slide counter top-right
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(PRIMARY)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.5*cm,
                      f"{page_num:02d} / {total:02d}")
    c.restoreState()

def stat_box(c, x, y, w, icon_char, label, value):
    """Small stat tile."""
    bh = 2.6*cm
    c.setFillColor(LIGHT_BG)
    c.roundRect(x, y, w, bh, 6, stroke=0, fill=1)
    c.setFillColor(SECONDARY)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(x + w/2, y + bh - 0.9*cm, icon_char)
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(x + w/2, y + bh - 1.55*cm, label)
    c.setFillColor(DARK_TEXT)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(x + w/2, y + 0.5*cm, value)


# ── PAGE 1 · Cover ─────────────────────────────────────────────────────────

def page1(c):
    # header gradient strip
    draw_gradient_bar(c, 0, PAGE_H - 2.0*cm, PAGE_W, 2.0*cm)

    # "Workshop 4" pill on top strip
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, PAGE_H - 1.25*cm, "Workshop 4  ·  Sommersemester 2026")

    # PARTNERVORSTELLUNG label
    c.setFillColor(SECONDARY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, PAGE_H - 3.2*cm, "PARTNERVORSTELLUNG")

    # Zurich logo centred
    try:
        img = ImageReader(LOGO_PATH)
        iw, ih = img.getSize()
        logo_h = 3.2*cm
        logo_w = logo_h * iw / ih
        c.drawImage(LOGO_PATH, (PAGE_W - logo_w) / 2, PAGE_H - 8.5*cm,
                    width=logo_w, height=logo_h, mask='auto')
    except Exception:
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(PRIMARY)
        c.drawCentredString(PAGE_W/2, PAGE_H - 7.5*cm, "ZURICH")

    # Tagline
    c.setFillColor(DARK_TEXT)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(PAGE_W/2, PAGE_H - 10.5*cm, "Globale Versicherungskompetenz.")
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(PAGE_W/2, PAGE_H - 11.5*cm, "Lokal verankert in Köln.")

    # divider
    draw_gradient_bar(c, MARGIN, PAGE_H - 13.0*cm, INNER_W, 0.12*cm)

    # Event info block
    info_y = PAGE_H - 14.8*cm
    box_w  = INNER_W / 3 - 0.3*cm

    def info_tile(bx, icon, line1, line2=""):
        c.setFillColor(LIGHT_BG)
        c.roundRect(bx, info_y, box_w, 2.4*cm, 6, stroke=0, fill=1)
        c.setFillColor(PRIMARY)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(bx + box_w/2, info_y + 1.65*cm, icon)
        c.setFillColor(DARK_TEXT)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(bx + box_w/2, info_y + 0.95*cm, line1)
        if line2:
            c.setFont("Helvetica", 8)
            c.setFillColor(MID_GREY)
            c.drawCentredString(bx + box_w/2, info_y + 0.38*cm, line2)

    info_tile(MARGIN,                       "📅", "MITTWOCH, 08.07.2026", "")
    info_tile(MARGIN + box_w + 0.3*cm,      "🕔", "17:00 UHR", "")
    info_tile(MARGIN + 2*(box_w + 0.3*cm),  "📍", "Zurich – Office Köln", "")

    draw_footer(c, 1)


# ── PAGE 2 · Das Unternehmen ────────────────────────────────────────────────

def page2(c):
    draw_gradient_bar(c, 0, PAGE_H - 0.9*cm, PAGE_W, 0.9*cm)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, PAGE_H - 0.62*cm, "Das Unternehmen")

    # Slide number hint top-right already in draw_footer

    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(MARGIN, PAGE_H - 2.8*cm, "Weltklasse. In Köln zu Hause.")

    draw_gradient_bar(c, MARGIN, PAGE_H - 3.15*cm, INNER_W, 0.10*cm)

    # Body text
    body = (
        "Die Zurich Insurance Group zählt zu den führenden Versicherern weltweit. "
        "In Deutschland ist Zurich seit über 100 Jahren aktiv und begleitet "
        "Privat- und Geschäftskunden mit ganzheitlichen Lösungen in Schaden-, "
        "Unfall- und Lebensversicherung – nachhaltig, digital und zukunftsorientiert."
    )
    text_obj = c.beginText(MARGIN, PAGE_H - 4.3*cm)
    text_obj.setFont("Helvetica", 11)
    text_obj.setFillColor(DARK_TEXT)
    text_obj.setLeading(17)

    # word-wrap manually
    words = body.split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if c.stringWidth(test, "Helvetica", 11) < INNER_W:
            line = test
        else:
            text_obj.textLine(line)
            line = w
    if line:
        text_obj.textLine(line)
    c.drawText(text_obj)

    # Stat boxes
    stat_y = PAGE_H - 10.5*cm
    sw = (INNER_W - 0.9*cm) / 4
    stat_box(c, MARGIN,                        stat_y, sw, "📅", "GEGRÜNDET",   "1872")
    stat_box(c, MARGIN + sw + 0.3*cm,           stat_y, sw, "👥", "MITARBEITENDE","~55.000")
    stat_box(c, MARGIN + 2*(sw+0.3*cm),         stat_y, sw, "📍", "HAUPTSITZ",   "Zürich / Köln")
    stat_box(c, MARGIN + 3*(sw+0.3*cm),         stat_y, sw, "📈", "SEGMENT",     "Schaden/Leben")

    # Schwerpunkte list
    focus_y = stat_y - 1.4*cm
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN, focus_y, "Schwerpunkte:")
    items = ["Schaden- & Unfallversicherung", "Lebensversicherung",
             "Industrieversicherung", "Nachhaltigkeit & Digitalisierung"]
    c.setFont("Helvetica", 10)
    c.setFillColor(DARK_TEXT)
    for i, item in enumerate(items):
        c.setFillColor(SECONDARY)
        c.circle(MARGIN + 0.15*cm, focus_y - 0.55*cm - i*0.55*cm + 0.05*cm, 0.08*cm, fill=1, stroke=0)
        c.setFillColor(DARK_TEXT)
        c.drawString(MARGIN + 0.4*cm, focus_y - 0.55*cm - i*0.55*cm, item)

    draw_footer(c, 2)


# ── PAGE 3 · Speaker ────────────────────────────────────────────────────────

def page3(c):
    draw_gradient_bar(c, 0, PAGE_H - 0.9*cm, PAGE_W, 0.9*cm)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, PAGE_H - 0.62*cm, "Die Speaker")

    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(MARGIN, PAGE_H - 2.8*cm, "Eure Speaker")

    draw_gradient_bar(c, MARGIN, PAGE_H - 3.15*cm, INNER_W, 0.10*cm)

    # Speaker placeholder cards
    card_w = (INNER_W - 0.5*cm) / 2
    card_h = 4.0*cm
    card_y = PAGE_H - 8.2*cm

    def speaker_card(cx, cy, initials, name, role):
        c.setFillColor(LIGHT_BG)
        c.roundRect(cx, cy, card_w, card_h, 8, stroke=0, fill=1)
        # avatar circle
        c.setFillColor(PRIMARY)
        c.circle(cx + 1.2*cm, cy + card_h - 1.1*cm, 0.7*cm, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(cx + 1.2*cm, cy + card_h - 1.35*cm, initials)
        # text
        c.setFillColor(DARK_TEXT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(cx + 2.6*cm, cy + card_h - 0.9*cm, name)
        c.setFillColor(MID_GREY)
        c.setFont("Helvetica", 9)
        c.drawString(cx + 2.6*cm, cy + card_h - 1.5*cm, role)
        c.setFillColor(SECONDARY)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(cx + 2.6*cm, cy + card_h - 2.0*cm, "📍 KÖLN")
        c.setFillColor(PRIMARY)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(cx + 2.6*cm, cy + card_h - 2.6*cm, "Zurich Insurance")

    speaker_card(MARGIN,                card_y, "NN", "[Vorname Nachname]", "[Funktion / Titel]")
    speaker_card(MARGIN + card_w + 0.5*cm, card_y, "NN", "[Vorname Nachname]", "[Funktion / Titel]")

    # HR-Kontakt placeholder
    hr_y = card_y - 1.8*cm
    c.setFillColor(LIGHT_BG)
    c.roundRect(MARGIN, hr_y, INNER_W, 1.3*cm, 6, stroke=0, fill=1)
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN + 0.4*cm, hr_y + 0.75*cm, "HR-Ansprechpartner:in Karriere ·  Zurich Insurance")
    c.setFillColor(MID_GREY)
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN + 0.4*cm, hr_y + 0.25*cm, "[Name folgt in Kürze]")

    # Thema / Format / Anschluss
    detail_y = hr_y - 2.8*cm
    rows = [
        ("💡", "THEMA",    "[Workshopthema folgt in Kürze]"),
        ("🗣",  "FORMAT",   "Interaktiver Workshop"),
        ("🍽",  "ANSCHLUSS","Networking-Dinner"),
    ]
    for icon, label, text in rows:
        c.setFillColor(SECONDARY)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN, detail_y + 0.15*cm, icon)
        c.setFillColor(PRIMARY)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN + 0.6*cm, detail_y + 0.15*cm, label)
        c.setFillColor(DARK_TEXT)
        c.setFont("Helvetica", 10)
        c.drawString(MARGIN + 2.8*cm, detail_y + 0.15*cm, text)
        detail_y -= 0.65*cm

    draw_footer(c, 3)


# ── PAGE 4 · CTA ────────────────────────────────────────────────────────────

def page4(c):
    # Full-bleed gradient background
    steps = 80
    for i in range(steps):
        t = i / steps
        r = PRIMARY.red   + t * (SECONDARY.red   - PRIMARY.red)
        g = PRIMARY.green + t * (SECONDARY.green - PRIMARY.green)
        b = PRIMARY.blue  + t * (SECONDARY.blue  - PRIMARY.blue)
        c.setFillColorRGB(r, g, b)
        c.rect(0, i * PAGE_H / steps, PAGE_W, PAGE_H / steps + 1, stroke=0, fill=1)

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, PAGE_H - 0.62*cm, "Jetzt anmelden")

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 40)
    c.drawString(MARGIN, PAGE_H - 4.0*cm, "Jetzt")
    c.setFont("Helvetica-Bold", 40)
    c.drawString(MARGIN, PAGE_H - 5.3*cm, "bewerben.")

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, PAGE_H - 7.0*cm, "BEREIT FÜR DEN WORKSHOP?")

    body = (
        "Sichere dir deinen Platz beim Workshop bei Zurich – "
        "begrenzte Plätze, Bewerbung in wenigen Minuten."
    )
    text_obj = c.beginText(MARGIN, PAGE_H - 8.0*cm)
    text_obj.setFont("Helvetica", 11)
    text_obj.setFillColor(colors.HexColor("#E0F2FE"))
    text_obj.setLeading(17)
    words = body.split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if c.stringWidth(test, "Helvetica", 11) < INNER_W:
            line = test
        else:
            text_obj.textLine(line)
            line = w
    if line:
        text_obj.textLine(line)
    c.drawText(text_obj)

    # Arrow + URL
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, PAGE_H - 10.2*cm, "→  nextgenforum.de/jetzt-bewerben")

    # Info pills
    pill_y = PAGE_H - 12.5*cm
    pill_data = [
        ("📅", "Mi · 08.07.2026 · 17:00 Uhr"),
        ("📍", "Zurich Office Köln"),
    ]
    px = MARGIN
    for icon, text in pill_data:
        pw = c.stringWidth(icon + "  " + text, "Helvetica-Bold", 10) + 1.0*cm
        c.setFillColor(colors.HexColor("#FFFFFF30"))
        c.roundRect(px, pill_y, pw, 0.7*cm, 6, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(px + 0.4*cm, pill_y + 0.18*cm, icon + "  " + text)
        px += pw + 0.3*cm

    # Footer on gradient – override colours
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor("#FFFFFFAA"))
    c.drawString(MARGIN, 0.65*cm, "Vernetzung. Förderung. Zukunft.")
    c.drawRightString(PAGE_W - MARGIN, 0.65*cm, "nextgenforum.de")
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 8)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.5*cm, "04 / 04")


# ── MAIN ────────────────────────────────────────────────────────────────────

c = canvas.Canvas(OUTPUT, pagesize=A4)
c.setTitle("Partnervorstellung – Zurich | NextGen Insurance Forum e.V.")
c.setAuthor("NextGen Insurance Forum e.V.")

page1(c); c.showPage()
page2(c); c.showPage()
page3(c); c.showPage()
page4(c); c.showPage()

c.save()
print(f"PDF saved → {OUTPUT}")
