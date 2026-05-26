"""
Zurich Partnervorstellungs-Post
Pixel-based approach: render CC pages → Gaussian background fill over CC elements
→ draw Zurich content using PIL → compile to PDF.
"""

import io, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

CC_PDF  = "/root/.claude/uploads/79e84717-110b-42c1-91d9-257057663432/f5ee3903-NextGenPartnerPostcrossconsulting.pdf"
ZU_LOGO = "/home/user/nextgen-webseite-test1/src/images/zurich_uebereinander.png"
OUTPUT  = "/home/user/nextgen-webseite-test1/NextGenPartnerPost_Zurich.pdf"

DPI   = 150
SCALE = DPI / 72.0   # ≈ 2.0833 px per PDF pt

FONT_REG  = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# Brand colours (RGB tuples)
PRIMARY = (14,  75, 148)
TEAL    = (44, 217, 195)
DARK    = (14,  14,  27)
MID     = (107, 114, 128)
WHITE   = (255, 255, 255)

# ── helpers ──────────────────────────────────────────────────────────────────

def p(pts):
    """PDF points → pixels."""
    return int(round(pts * SCALE))

def pdf_rect(pdf_x, pdf_y_bot, pdf_w, pdf_h, img_h):
    """PDF rect (y from bottom) → PIL pixel box (left,top,right,bottom)."""
    left   = p(pdf_x)
    top    = img_h - p(pdf_y_bot + pdf_h)
    right  = p(pdf_x + pdf_w)
    bottom = img_h - p(pdf_y_bot)
    return (max(0,left), max(0,top), right, bottom)

def gaussian_bg(arr, sigma_pts=265):
    """4-corner Gaussian blend background reconstruction."""
    h, w = arr.shape[:2]
    sig  = sigma_pts * SCALE
    tl   = arr[0,  0].astype(float)
    tr   = arr[0, -1].astype(float)
    bl   = arr[-1, 0].astype(float)
    br   = arr[-1,-1].astype(float)
    ys, xs = np.mgrid[0:h, 0:w]
    w_tl = np.exp(-((xs**2           + ys**2)           / (2*sig**2)))
    w_tr = np.exp(-(((w-1-xs)**2     + ys**2)           / (2*sig**2)))
    w_bl = np.exp(-((xs**2           + (h-1-ys)**2)     / (2*sig**2)))
    w_br = np.exp(-(((w-1-xs)**2     + (h-1-ys)**2)     / (2*sig**2)))
    tot  = w_tl + w_tr + w_bl + w_br
    bg   = (w_tl[...,None]*tl + w_tr[...,None]*tr +
            w_bl[...,None]*bl + w_br[...,None]*br) / tot[...,None]
    return bg.clip(0, 255).astype(np.uint8)

def erase(arr, bg, box):
    """Fill PIL box with reconstructed background."""
    l, t, r, b = box
    arr[t:b, l:r] = bg[t:b, l:r]

def font(bold=False, size_pt=14):
    path = FONT_BOLD if bold else FONT_REG
    return ImageFont.truetype(path, p(size_pt))

def draw_text_centered(draw, text, cx_pt, y_bot_pt, img_h, size_pt, bold=False,
                        color=DARK):
    f = font(bold, size_pt)
    bbox = f.getbbox(text)
    tw = bbox[2] - bbox[0]
    x  = p(cx_pt) - tw // 2
    y  = img_h - p(y_bot_pt) - p(size_pt)
    draw.text((x, y), text, font=f, fill=color)
    return tw

def draw_text_left(draw, text, x_pt, y_bot_pt, img_h, size_pt, bold=False,
                   color=DARK):
    f  = font(bold, size_pt)
    y  = img_h - p(y_bot_pt) - p(size_pt)
    draw.text((p(x_pt), y), text, font=f, fill=color)
    bbox = f.getbbox(text)
    return bbox[2] - bbox[0]

def text_width(text, size_pt, bold=False):
    f = font(bold, size_pt)
    bb = f.getbbox(text)
    return bb[2] - bb[0]

def draw_gradient_pill(draw, x_pt, y_bot_pt, w_pt, h_pt, img_h,
                        text, size_pt=13, r_pt=10):
    """Horizontal gradient pill: PRIMARY → TEAL, white centered text."""
    x0 = p(x_pt);  y0 = img_h - p(y_bot_pt + h_pt)
    x1 = p(x_pt + w_pt); y1 = img_h - p(y_bot_pt)
    steps = x1 - x0
    for i in range(steps):
        t = i / max(steps-1, 1)
        rc = int(PRIMARY[0] + t*(TEAL[0]-PRIMARY[0]))
        gc = int(PRIMARY[1] + t*(TEAL[1]-PRIMARY[1]))
        bc = int(PRIMARY[2] + t*(TEAL[2]-PRIMARY[2]))
        draw.line([(x0+i, y0), (x0+i, y1)], fill=(rc,gc,bc))
    # Round corners (simple mask)
    rp = p(r_pt)
    for cx, cy in [(x0+rp, y0+rp), (x1-rp, y0+rp),
                   (x0+rp, y1-rp), (x1-rp, y1-rp)]:
        for dy in range(rp):
            for dx in range(rp):
                if dx*dx + dy*dy > rp*rp:
                    pass  # keep as-is (gradient already filled)
    # Text
    f = font(True, size_pt)
    bbox = f.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = x0 + (x1-x0-tw)//2
    ty = y0 + (y1-y0-th)//2 - bbox[1]
    draw.text((tx, ty), text, font=f, fill=WHITE)

def draw_stat_box(draw, img, x_pt, y_bot_pt, w_pt, h_pt, img_h,
                  label, value_lines, accent=None):
    """White rounded-rect stat box with label + value."""
    x0 = p(x_pt);      y0 = img_h - p(y_bot_pt + h_pt)
    x1 = p(x_pt+w_pt); y1 = img_h - p(y_bot_pt)
    rp = p(12)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=rp,
                            fill=WHITE, outline=(226,234,240), width=1)
    cx = (x0+x1)//2
    # Label
    f_lbl = font(False, 10)
    bb = f_lbl.getbbox(label)
    lw = bb[2]-bb[0]
    draw.text((cx-lw//2, y0+p(14)), label, font=f_lbl, fill=MID)
    # Value(s)
    if isinstance(value_lines, str):
        value_lines = [value_lines]
    f_val = font(True, 22)
    total_h = len(value_lines) * p(28)
    vy = y0 + (y1-y0)//2 - total_h//2
    for vl in value_lines:
        bb2 = f_val.getbbox(vl)
        vw = bb2[2]-bb2[0]
        draw.text((cx-vw//2, vy), vl, font=f_val, fill=DARK)
        vy += p(28)

def draw_speaker_card(draw, x_pt, y_bot_pt, w_pt, h_pt, img_h,
                      initials, name, role):
    x0 = p(x_pt);      y0 = img_h - p(y_bot_pt + h_pt)
    x1 = p(x_pt+w_pt); y1 = img_h - p(y_bot_pt)
    rp = p(12)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=rp,
                            fill=WHITE, outline=(226,234,240), width=1)
    cx = (x0+x1)//2
    # Avatar circle
    av_r = p(34); av_cy = y0 + p(52)
    draw.ellipse([cx-av_r, av_cy-av_r, cx+av_r, av_cy+av_r],
                 fill=(214,234,242))
    f_init = font(True, 18)
    bb = f_init.getbbox(initials)
    draw.text((cx-(bb[2]-bb[0])//2, av_cy-p(12)), initials,
              font=f_init, fill=PRIMARY)
    # Name
    f_name = font(True, 14)
    bb = f_name.getbbox(name)
    draw.text((cx-(bb[2]-bb[0])//2, y0+p(100)), name, font=f_name, fill=DARK)
    # Role
    f_role = font(False, 11)
    bb = f_role.getbbox(role)
    draw.text((cx-(bb[2]-bb[0])//2, y0+p(120)), role, font=f_role, fill=MID)
    # Company
    f_co = font(True, 11)
    co = "Zurich Insurance"
    bb = f_co.getbbox(co)
    draw.text((cx-(bb[2]-bb[0])//2, y0+p(138)), co, font=f_co, fill=PRIMARY)

def wrap_text(draw, text, x_pt, y_bot_pt, max_w_pt, img_h, size_pt,
              bold=False, color=MID, leading_pt=22):
    f   = font(bold, size_pt)
    words = text.split()
    line  = ""
    y     = img_h - p(y_bot_pt) - p(size_pt)
    for w in words:
        test = (line + " " + w).strip()
        bb   = f.getbbox(test)
        if bb[2]-bb[0] <= p(max_w_pt):
            line = test
        else:
            if line:
                draw.text((p(x_pt), y), line, font=f, fill=color)
                y += p(leading_pt)
            line = w
    if line:
        draw.text((p(x_pt), y), line, font=f, fill=color)

# ── render CC pages ──────────────────────────────────────────────────────────

def render_cc_pages():
    subprocess.run(["pdftoppm", "-r", str(DPI), "-png", CC_PDF, "/tmp/zu_cc"],
                   check=True, capture_output=True)
    files = sorted(f for f in os.listdir("/tmp")
                   if f.startswith("zu_cc-") and f.endswith(".png"))
    return [np.array(Image.open(f"/tmp/{f}").convert("RGB")) for f in files]

# ── page builders ─────────────────────────────────────────────────────────────

def process_page1(arr, bg, img_h, img_w):
    draw_arr = arr.copy()

    # --- ERASE CC elements ---
    # Header counter (replace "Workshop 1" with "Workshop 4")
    # Header strip y_pdf=921-970 → at right side x_pdf=350-810
    box_ctr = pdf_rect(350, 921, 460, 49, img_h)
    # Fill with header gradient colours (match measured strip colours)
    l, t, r, b = box_ctr
    for row in range(t, b):
        progress = (row - t) / max(b - t - 1, 1)  # 0=top of strip, 1=bottom
        # top of strip (progress=0) = dark blue (59,86,141), bottom=teal (26,158,165)
        rc = int(59  + progress * (26  - 59))
        gc = int(86  + progress * (158 - 86))
        bc = int(141 + progress * (165 - 141))
        draw_arr[row, l:r] = [rc, gc, bc]

    # CC logo + tagline: y_pdf=500-720, x_pdf=68-742
    erase(draw_arr, bg, pdf_rect(68, 500, 674, 220, img_h))

    # Date text above pill: y_pdf=375-465, x_pdf=178-632
    erase(draw_arr, bg, pdf_rect(178, 375, 454, 90, img_h))

    # Gradient pill: y_pdf=282-385, x_pdf=24-786
    erase(draw_arr, bg, pdf_rect(24, 282, 762, 103, img_h))

    # --- DRAW Zurich content ---
    img = Image.fromarray(draw_arr)
    draw = ImageDraw.Draw(img)

    # Counter text: white "Workshop 4  ●  04 / 04" right-aligned
    ctr_txt = "Workshop 4  ●  04 / 04"
    f_ctr = font(False, 12)
    bb = f_ctr.getbbox(ctr_txt)
    cw = bb[2] - bb[0]
    cx_right = p(762)
    cy_ctr   = img_h - p(960) - p(12)
    draw.text((cx_right - cw, cy_ctr), ctr_txt, font=f_ctr, fill=WHITE)

    # Zurich logo
    zu = Image.open(ZU_LOGO).convert("RGBA")
    lh_pt = 140; lw_pt = lh_pt * zu.width / zu.height
    lh_px = p(lh_pt); lw_px = p(lw_pt)
    zu_rsz = zu.resize((lw_px, lh_px), Image.LANCZOS)
    lx = (img_w - lw_px) // 2
    ly = img_h - p(720) - lh_px   # logo top at pdf_y=860 from bottom
    img.paste(zu_rsz, (lx, ly), zu_rsz)
    draw = ImageDraw.Draw(img)

    # Taglines
    draw_text_centered(draw, "Globale Versicherungskompetenz.",
                       405, 548, img_h, 22, bold=False, color=DARK)
    draw_text_centered(draw, "Lokal verankert in Köln.",
                       405, 522, img_h, 22, bold=False, color=DARK)

    # Gradient pill (match CC pill at y_pdf=310-368, x=55-755, w=700)
    draw_gradient_pill(draw, 55, 310, 700, 58, img_h,
                       "MITTWOCH  |  08.07.2026  |  17:00 Uhr  |  Zurich – Office Köln",
                       size_pt=12)

    return np.array(img)


def process_page2(arr, bg, img_h, img_w):
    draw_arr = arr.copy()

    # Header counter
    box_ctr = pdf_rect(350, 921, 460, 49, img_h)
    l, t, r, b = box_ctr
    for row in range(t, b):
        prog = (row - t) / max(b - t - 1, 1)
        rc = int(59  + prog * (26  - 59))
        gc = int(86  + prog * (158 - 86))
        bc = int(141 + prog * (165 - 141))
        draw_arr[row, l:r] = [rc, gc, bc]

    # Headline: y_pdf=732-808, x=40-754
    erase(draw_arr, bg, pdf_rect(40, 732, 714, 76, img_h))

    # Body text: y_pdf=642-718, x=40-676
    erase(draw_arr, bg, pdf_rect(40, 642, 636, 76, img_h))

    # Stats area: y_pdf=282-575, x=40-772
    erase(draw_arr, bg, pdf_rect(40, 282, 732, 293, img_h))

    img  = Image.fromarray(draw_arr)
    draw = ImageDraw.Draw(img)

    # Counter
    ctr_txt = "Das Unternehmen  ●  02 / 04"
    f_ctr = font(False, 12)
    bb = f_ctr.getbbox(ctr_txt)
    draw.text((p(762)-bb[2]+bb[0], img_h-p(960)-p(12)),
              ctr_txt, font=f_ctr, fill=WHITE)

    # Headline: "Weltklasse trifft Köln."
    f_h = font(True, 54)
    part1 = "Weltklasse trifft "
    part2 = "Köln."
    w1 = text_width(part1, 54, bold=True)
    y_h = img_h - p(757) - p(54)
    draw.text((p(48), y_h), part1, font=f_h, fill=DARK)
    draw.text((p(48)+w1, y_h), part2, font=f_h,
              fill=(44,217,195))

    # Body text
    body = ("Die Zurich Insurance Group zählt zu den führenden Versicherern "
            "weltweit. In Deutschland begleitet Zurich seit über 100 Jahren "
            "Privat- und Geschäftskunden mit ganzheitlichen Lösungen in "
            "Schaden-, Unfall- und Lebensversicherung – nachhaltig, digital "
            "und zukunftsorientiert.")
    wrap_text(draw, body, 48, 700, 714, img_h, 15, color=MID)

    # 4 stat boxes (2×2 grid)
    bw = (714 - 20) / 2   # ≈ 347 pt
    bh = 130
    gx, gy = 48, 300
    gap = 20
    draw_stat_box(draw, img, gx,          gy+bh+gap, bw, bh, img_h,
                  "GEGRÜNDET",    "1872")
    draw_stat_box(draw, img, gx+bw+gap,   gy+bh+gap, bw, bh, img_h,
                  "MITARBEITENDE","~55.000")
    draw_stat_box(draw, img, gx,          gy,         bw, bh, img_h,
                  "HAUPTSITZ",    ["Zürich (CH)", "Köln (DE)"])
    draw_stat_box(draw, img, gx+bw+gap,   gy,         bw, bh, img_h,
                  "SCHWERPUNKTE", ["Schaden/Unfall", "Leben & Alters-", "vorsorge"])

    return np.array(img)


def process_page3(arr, bg, img_h, img_w):
    draw_arr = arr.copy()

    # Header counter
    box_ctr = pdf_rect(350, 921, 460, 49, img_h)
    l, t, r, b = box_ctr
    for row in range(t, b):
        prog = (row - t) / max(b - t - 1, 1)
        rc = int(59  + prog * (26  - 59))
        gc = int(86  + prog * (158 - 86))
        bc = int(141 + prog * (165 - 141))
        draw_arr[row, l:r] = [rc, gc, bc]

    # Speaker cards: y_pdf=490-714, x=112-766
    erase(draw_arr, bg, pdf_rect(112, 490, 654, 224, img_h))

    # HR row: y_pdf=466-502, x=186-626
    erase(draw_arr, bg, pdf_rect(186, 466, 440, 36, img_h))

    # Info bar: y_pdf=416-468, x=158-650
    erase(draw_arr, bg, pdf_rect(158, 416, 492, 52, img_h))

    img  = Image.fromarray(draw_arr)
    draw = ImageDraw.Draw(img)

    # Counter
    ctr_txt = "Die Speaker  ●  03 / 04"
    f_ctr = font(False, 12)
    bb = f_ctr.getbbox(ctr_txt)
    draw.text((p(762)-(bb[2]-bb[0]), img_h-p(960)-p(12)),
              ctr_txt, font=f_ctr, fill=WHITE)

    # Speaker cards (2 placeholder cards side by side)
    cw = (654 - 20) / 2   # ≈ 317 pt
    ch = 218
    draw_speaker_card(draw, 112,          490, cw, ch, img_h,
                      "NN", "[Vorname Nachname]", "[Funktion]")
    draw_speaker_card(draw, 112+cw+20,    490, cw, ch, img_h,
                      "NN", "[Vorname Nachname]", "[Funktion]")

    # HR row
    hr_x, hr_y, hr_w, hr_h = 186, 470, 438, 48
    x0=p(hr_x); y0=img_h-p(hr_y+hr_h); x1=p(hr_x+hr_w); y1=img_h-p(hr_y)
    draw.rounded_rectangle([x0,y0,x1,y1], radius=p(8),
                            fill=WHITE, outline=(226,234,240), width=1)
    av_r=p(18); av_cx=x0+p(26); av_cy=(y0+y1)//2
    draw.ellipse([av_cx-av_r, av_cy-av_r, av_cx+av_r, av_cy+av_r],
                 fill=(214,234,242))
    f_hr=font(True,9); draw.text((av_cx-p(5), av_cy-p(6)), "HR",
                                  font=f_hr, fill=PRIMARY)
    f_name=font(True,12)
    draw.text((av_cx+p(22), av_cy-p(10)), "[Ansprechpartner:in Karriere]",
              font=f_name, fill=DARK)
    f_sub=font(False,10)
    draw.text((av_cx+p(22), av_cy+p(4)), "Ansprechpartner:in Karriere · Zurich Insurance",
              font=f_sub, fill=MID)

    # Info bar (gradient)
    draw_gradient_pill(draw, 158, 418, 492, 44, img_h, "", size_pt=11, r_pt=8)
    cols = [("THEMA","[Thema folgt]"), ("FORMAT","Workshop"), ("ANSCHLUSS","Networking")]
    col_w = 492 / 3
    for i, (lbl, val) in enumerate(cols):
        cx_pt = 158 + col_w*(i+0.5)
        f_l = font(True, 9)
        f_v = font(True, 11)
        bb_l = f_l.getbbox(lbl); bb_v = f_v.getbbox(val)
        cx_px = p(cx_pt)
        draw.text((cx_px-(bb_l[2]-bb_l[0])//2, img_h-p(418+44)+p(6)),
                  lbl, font=f_l, fill=(200,235,235))
        draw.text((cx_px-(bb_v[2]-bb_v[0])//2, img_h-p(418+44)+p(22)),
                  val, font=f_v, fill=WHITE)

    return np.array(img)


def process_page4(arr, bg, img_h, img_w):
    draw_arr = arr.copy()

    # Header counter
    box_ctr = pdf_rect(350, 921, 460, 49, img_h)
    l, t, r, b = box_ctr
    for row in range(t, b):
        prog = (row - t) / max(b - t - 1, 1)
        rc = int(59  + prog * (26  - 59))
        gc = int(86  + prog * (158 - 86))
        bc = int(141 + prog * (165 - 141))
        draw_arr[row, l:r] = [rc, gc, bc]

    # Body text: y_pdf=393-485, x=146-665
    erase(draw_arr, bg, pdf_rect(146, 393, 519, 92, img_h))

    # Date bar: y_pdf=321-385, x=1-646
    erase(draw_arr, bg, pdf_rect(1, 321, 645, 64, img_h))

    img  = Image.fromarray(draw_arr)
    draw = ImageDraw.Draw(img)

    # Counter
    ctr_txt = "Jetzt anmelden  ●  04 / 04"
    f_ctr = font(False, 12)
    bb = f_ctr.getbbox(ctr_txt)
    draw.text((p(762)-(bb[2]-bb[0]), img_h-p(960)-p(12)),
              ctr_txt, font=f_ctr, fill=WHITE)

    # Body text (replace CC company name)
    draw_text_centered(draw, "Sichere dir deinen Platz beim Workshop bei",
                       405, 462, img_h, 16, color=DARK)
    # Line 2: "Zurich Insurance" bold + rest normal
    part1 = "Zurich Insurance"
    part2 = " – begrenzte Plätze, Bewerbung in wenigen Minuten."
    w1 = text_width(part1, 16, bold=True)
    w2 = text_width(part2, 16, bold=False)
    sx = p(405) - (w1+w2)//2
    y_l2 = img_h - p(438) - p(16)
    draw.text((sx,    y_l2), part1, font=font(True,  16), fill=DARK)
    draw.text((sx+w1, y_l2), part2, font=font(False, 16), fill=DARK)

    # Date bar (gradient pill)
    draw_gradient_pill(draw, 5, 323, 640, 58, img_h,
                       "Mi  ·  08.07.2026  ·  17:00 Uhr  ·  Zurich – Office Köln",
                       size_pt=13)

    return np.array(img)


# ── main ──────────────────────────────────────────────────────────────────────

print("Rendering CC pages…")
cc_pages = render_cc_pages()
print(f"  {len(cc_pages)} pages, {cc_pages[0].shape[1]}×{cc_pages[0].shape[0]} px")

print("Computing Gaussian backgrounds…")
bg_arrays = [gaussian_bg(p_arr) for p_arr in cc_pages]

img_h = cc_pages[0].shape[0]
img_w = cc_pages[0].shape[1]

processors = [process_page1, process_page2, process_page3, process_page4]
out_pages  = []
for i, (proc, pg, bg) in enumerate(zip(processors, cc_pages, bg_arrays)):
    print(f"  Processing page {i+1}…")
    out_pages.append(proc(pg, bg, img_h, img_w))

# ── compile to PDF ────────────────────────────────────────────────────────────

print("Compiling PDF…")
PW, PH = 810, 1013.04
buf = io.BytesIO()
c   = rl_canvas.Canvas(buf, pagesize=(PW, PH))

for i, page_arr in enumerate(out_pages):
    tmp = f"/tmp/zurich_out_{i+1}.png"
    Image.fromarray(page_arr).save(tmp, optimize=False)
    c.drawImage(tmp, 0, 0, width=PW, height=PH)
    c.showPage()

c.save()
with open(OUTPUT, "wb") as f:
    f.write(buf.getvalue())

print(f"✓  Gespeichert → {OUTPUT}")
