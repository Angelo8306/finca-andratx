#!/usr/bin/env python3
"""
Professionelles Verkaufs-Expose fuer Finca in Andratx, Mallorca
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import qrcode
import io

# --- CONFIGURATION ---
OUTPUT_PATH = "/Users/angelojuric/Documents/Cay Fingerle/Finca Cay Fingerle/social-media/output/Expose_Finca_Andratx.pdf"
IMG_DIR = "/Users/angelojuric/Documents/Cay Fingerle/Finca Cay Fingerle/images"

# Colors
CREAM = HexColor("#F5F0E8")
BROWN = HexColor("#2C2420")
GOLD = HexColor("#C9A96E")
TERRACOTTA = HexColor("#C4754B")
WHITE = HexColor("#FFFFFF")
LIGHT_CREAM = HexColor("#FAF7F2")

# Page dimensions
W, H = A4  # 595.27 x 841.89 points
MARGIN = 25 * mm
CONTENT_W = W - 2 * MARGIN


def img_path(name):
    return os.path.join(IMG_DIR, name)


def draw_cream_bg(c):
    """Draw cream background on the full page."""
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def draw_gold_line(c, x, y, width, thickness=0.8):
    """Draw a gold horizontal line."""
    c.setStrokeColor(GOLD)
    c.setLineWidth(thickness)
    c.line(x, y, x + width, y)


def draw_image_cover(c, img_file, x, y, w, h):
    """Draw image with cover/crop behavior to fill the given rect."""
    try:
        pil_img = Image.open(img_file)
        img_w, img_h = pil_img.size

        # Calculate scale to cover the rect
        scale_w = w / img_w
        scale_h = h / img_h
        scale = max(scale_w, scale_h)

        new_w = img_w * scale
        new_h = img_h * scale

        # Center the image
        offset_x = x - (new_w - w) / 2
        offset_y = y - (new_h - h) / 2

        # Clip to rect
        c.saveState()
        p = c.beginPath()
        p.rect(x, y, w, h)
        c.clipPath(p, stroke=0)

        c.drawImage(ImageReader(pil_img), offset_x, offset_y, new_w, new_h, preserveAspectRatio=False)
        c.restoreState()
    except Exception as e:
        print(f"Warning: Could not load image {img_file}: {e}")
        c.setFillColor(HexColor("#DDD5C8"))
        c.rect(x, y, w, h, fill=1, stroke=0)


def draw_image_fit(c, img_file, x, y, w, h):
    """Draw image fitting inside the given rect (contain behavior)."""
    try:
        pil_img = Image.open(img_file)
        img_w, img_h = pil_img.size

        scale_w = w / img_w
        scale_h = h / img_h
        scale = min(scale_w, scale_h)

        new_w = img_w * scale
        new_h = img_h * scale

        offset_x = x + (w - new_w) / 2
        offset_y = y + (h - new_h) / 2

        c.drawImage(ImageReader(pil_img), offset_x, offset_y, new_w, new_h, preserveAspectRatio=False)
    except Exception as e:
        print(f"Warning: Could not load image {img_file}: {e}")


def draw_rounded_rect(c, x, y, w, h, radius=8, fill_color=None, stroke_color=None, stroke_width=0.5):
    """Draw a rounded rectangle."""
    c.saveState()
    if fill_color:
        c.setFillColor(fill_color)
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(stroke_width)

    p = c.beginPath()
    p.roundRect(x, y, w, h, radius)

    fill = 1 if fill_color else 0
    stroke = 1 if stroke_color else 0
    c.drawPath(p, fill=fill, stroke=stroke)
    c.restoreState()


def generate_qr_code(url):
    """Generate a QR code image for the given URL."""
    qr = qrcode.QRCode(version=1, box_size=10, border=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#2C2420", back_color="#F5F0E8")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return ImageReader(buf)


# ============================================================
# PAGE 1 - TITELSEITE
# ============================================================
def page_title(c):
    draw_cream_bg(c)

    # Top bar with gold accent
    c.setFillColor(BROWN)
    c.rect(0, H - 12 * mm, W, 12 * mm, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 7.5)
    c.drawString(MARGIN, H - 8 * mm, "IMMOBILIEN  |  MALLORCA  |  ANDRATX")
    c.drawRightString(W - MARGIN, H - 8 * mm, "REF: 2471C")

    # Hero image - large, full width
    hero_y = H - 12 * mm - 320
    draw_image_cover(c, img_path("01-facade.jpg"), 0, hero_y, W, 320)

    # Gradient overlay at bottom of image
    for i in range(80):
        alpha = i / 80.0 * 0.7
        c.setFillColor(Color(44/255, 36/255, 32/255, alpha))
        c.rect(0, hero_y + i, W, 1, fill=1, stroke=0)

    # Title area below image
    title_y = hero_y - 30

    # Main title
    c.setFillColor(BROWN)
    c.setFont("Times-Roman", 36)
    c.drawCentredString(W / 2, title_y, "FINCA IN ANDRATX")

    # Gold decorative line
    line_y = title_y - 15
    line_w = 80 * mm
    draw_gold_line(c, (W - line_w) / 2, line_y, line_w, 1.2)

    # Small gold diamonds
    diamond_y = line_y
    c.setFillColor(GOLD)
    for dx in [-42*mm, 0, 42*mm]:
        cx = W/2 + dx
        p = c.beginPath()
        p.moveTo(cx, diamond_y + 3)
        p.lineTo(cx + 3, diamond_y)
        p.lineTo(cx, diamond_y - 3)
        p.lineTo(cx - 3, diamond_y)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    # Subtitle
    sub_y = line_y - 28
    c.setFillColor(BROWN)
    c.setFont("Times-Italic", 14)
    c.drawCentredString(W / 2, sub_y, "Mallorquinisches Natursteinhaus")

    sub_y2 = sub_y - 20
    c.setFont("Helvetica", 10)
    c.setFillColor(GOLD)
    c.drawCentredString(W / 2, sub_y2, "Authentisch.  Renoviert.  Einzigartig.")

    # Price
    price_y = sub_y2 - 45
    c.setFillColor(TERRACOTTA)
    c.setFont("Times-Roman", 32)
    c.drawCentredString(W / 2, price_y, "1.800.000 EUR")

    # Property quick facts
    facts_y = price_y - 35
    c.setFillColor(BROWN)
    c.setFont("Helvetica", 9.5)
    facts_text = "172 m2   |   3 Schlafzimmer   |   2 Badezimmer   |   Nebengebaeude   |   Parkplatz"
    c.drawCentredString(W / 2, facts_y, facts_text)

    # Bottom contact bar
    bar_h = 28 * mm
    bar_y = 0
    c.setFillColor(BROWN)
    c.rect(0, bar_y, W, bar_h, fill=1, stroke=0)

    # Gold line at top of bar
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(0, bar_y + bar_h, W, bar_y + bar_h)

    # Contact info in bar
    mid_bar = bar_y + bar_h / 2
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, mid_bar + 8, "KONTAKT")

    c.setFillColor(WHITE)
    c.setFont("Helvetica", 10)
    c.drawCentredString(W / 2, mid_bar - 8, "arquitecto@c-df.com   |   +34 670 06 87 74")


# ============================================================
# PAGE 2 - UEBERSICHT & HIGHLIGHTS
# ============================================================
def page_overview(c):
    draw_cream_bg(c)

    y = H - MARGIN

    # Page header
    c.setFillColor(BROWN)
    c.setFont("Times-Roman", 28)
    c.drawString(MARGIN, y - 5, "Ihr neues Zuhause")
    y -= 10
    c.setFillColor(GOLD)
    c.setFont("Times-Italic", 28)
    c.drawString(MARGIN, y - 28, "auf Mallorca")
    y -= 40

    # Gold underline
    draw_gold_line(c, MARGIN, y, 60 * mm, 1.2)
    y -= 25

    # Description text
    c.setFillColor(BROWN)
    c.setFont("Helvetica", 10)

    desc_lines = [
        "Dieses liebevoll renovierte mallorquinische Natursteinhaus vereint",
        "traditionellen Charme mit modernem Komfort. Im Herzen von Andratx",
        "gelegen, bietet diese Finca ein unvergleichliches Wohnerlebnis auf 172 m2.",
        "",
        "Die sorgfaeltige Renovierung bewahrt den authentischen Charakter des",
        "Hauses und ergaenzt ihn um zeitgemaesse Annehmlichkeiten fuer hoechsten",
        "Wohnkomfort."
    ]

    for line in desc_lines:
        c.drawString(MARGIN, y, line)
        y -= 15

    y -= 10

    # Image - Wohnbereich
    img_h = 180
    draw_image_cover(c, img_path("05-interior3.jpg"), MARGIN, y - img_h, CONTENT_W, img_h)

    # Image caption overlay
    c.saveState()
    c.setFillColor(Color(44/255, 36/255, 32/255, 0.7))
    c.rect(MARGIN, y - img_h, CONTENT_W, 22, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN + 10, y - img_h + 7, "Wohnbereich mit doppelter Deckenhoehe")
    c.restoreState()

    y -= img_h + 20

    # Highlight box
    highlight_h = 30
    draw_rounded_rect(c, MARGIN, y - highlight_h, CONTENT_W, highlight_h,
                      radius=4, fill_color=TERRACOTTA)
    c.setFillColor(WHITE)
    c.setFont("Times-Roman", 13)
    c.drawCentredString(W / 2, y - highlight_h + 10, "Besonderes Highlight: Doppelte Deckenhoehe im Wohnbereich")
    y -= highlight_h + 20

    # Facts grid - 2 columns x 4 rows
    facts = [
        ("172 m2", "Wohnflaeche"),
        ("3", "Schlafzimmer"),
        ("2", "Badezimmer"),
        ("1", "Nebengebaeude"),
        ("1", "Eigener Parkplatz"),
        ("Ja", "Fussbodenheizung"),
        ("Ja", "Klimaanlage"),
        ("Ja", "Kamin"),
    ]

    col_w = CONTENT_W / 2
    box_h = 42
    box_margin = 5

    for i, (val, label) in enumerate(facts):
        col = i % 2
        row = i // 2

        bx = MARGIN + col * col_w + box_margin
        by = y - (row + 1) * (box_h + 6)
        bw = col_w - 2 * box_margin

        # Fact box
        draw_rounded_rect(c, bx, by, bw, box_h, radius=4,
                         fill_color=LIGHT_CREAM, stroke_color=GOLD, stroke_width=0.5)

        # Value
        c.setFillColor(TERRACOTTA)
        c.setFont("Times-Roman", 16)
        c.drawString(bx + 12, by + box_h - 18, val)

        # Label
        c.setFillColor(BROWN)
        c.setFont("Helvetica", 8.5)
        c.drawString(bx + 12, by + 8, label)

    # Footer line
    draw_gold_line(c, MARGIN, 18 * mm, CONTENT_W, 0.5)
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 7)
    c.drawCentredString(W / 2, 13 * mm, "Ref: 2471C  |  arquitecto@c-df.com  |  +34 670 06 87 74")


# ============================================================
# PAGE 3 - INNENRAEUME
# ============================================================
def page_interior(c):
    draw_cream_bg(c)

    y = H - MARGIN

    # Header
    c.setFillColor(BROWN)
    c.setFont("Times-Roman", 28)
    c.drawString(MARGIN, y - 5, "Innenraeume")
    y -= 10
    c.setFillColor(GOLD)
    c.setFont("Times-Italic", 28)
    c.drawString(MARGIN, y - 28, "mit Charakter")
    y -= 40

    draw_gold_line(c, MARGIN, y, 60 * mm, 1.2)
    y -= 22

    # Description
    c.setFillColor(BROWN)
    c.setFont("Helvetica", 10)
    desc2 = [
        "Jeder Raum erzaehlt seine eigene Geschichte. Naturstein, Holzbalken und",
        "handgefertigte Details treffen auf moderne Einbauten und hochwertige",
        "Materialien. Das Ergebnis ist ein Wohnambiente von zeitloser Eleganz."
    ]
    for line in desc2:
        c.drawString(MARGIN, y, line)
        y -= 14

    y -= 12

    # Image grid - 2 large on top, 3 smaller below
    gap = 6
    top_img_h = 180
    half_w = (CONTENT_W - gap) / 2

    # Row 1: Terrasse + Kueche
    draw_image_cover(c, img_path("03-interior1.jpg"), MARGIN, y - top_img_h, half_w, top_img_h)
    draw_image_cover(c, img_path("06-interior4.jpg"), MARGIN + half_w + gap, y - top_img_h, half_w, top_img_h)

    # Captions
    c.saveState()
    c.setFont("Helvetica", 7.5)
    c.setFillColor(Color(44/255, 36/255, 32/255, 0.65))
    c.rect(MARGIN, y - top_img_h, half_w, 18, fill=1, stroke=0)
    c.rect(MARGIN + half_w + gap, y - top_img_h, half_w, 18, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.drawString(MARGIN + 8, y - top_img_h + 5, "Terrasse")
    c.drawString(MARGIN + half_w + gap + 8, y - top_img_h + 5, "Kueche")
    c.restoreState()

    y -= top_img_h + gap

    # Row 2: 3 images
    third_w = (CONTENT_W - 2 * gap) / 3
    bottom_img_h = 155

    images_row2 = [
        (img_path("08-interior6.jpg"), "Schlafzimmer"),
        (img_path("09-view1.jpg"), "Master Bedroom"),
        (img_path("13-detail1.jpg"), "Badezimmer"),
    ]

    for i, (img, caption) in enumerate(images_row2):
        ix = MARGIN + i * (third_w + gap)
        draw_image_cover(c, img, ix, y - bottom_img_h, third_w, bottom_img_h)

        # Caption overlay
        c.saveState()
        c.setFillColor(Color(44/255, 36/255, 32/255, 0.65))
        c.rect(ix, y - bottom_img_h, third_w, 18, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica", 7.5)
        c.drawString(ix + 6, y - bottom_img_h + 5, caption)
        c.restoreState()

    y -= bottom_img_h + 20

    # Feature highlights
    features = [
        "Fussbodenheizung in allen Raeumen",
        "Klimaanlage fuer angenehme Temperaturen das ganze Jahr",
        "Offener Kamin fuer gemuetliche Winterabende",
        "Hochwertige Einbaukueche mit modernen Geraeten",
    ]

    c.setFont("Helvetica", 9)
    for feat in features:
        c.setFillColor(GOLD)
        c.drawString(MARGIN + 5, y, "—")
        c.setFillColor(BROWN)
        c.drawString(MARGIN + 20, y, feat)
        y -= 16

    # Footer
    draw_gold_line(c, MARGIN, 18 * mm, CONTENT_W, 0.5)
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 7)
    c.drawCentredString(W / 2, 13 * mm, "Ref: 2471C  |  arquitecto@c-df.com  |  +34 670 06 87 74")


# ============================================================
# PAGE 4 - LAGE & UMGEBUNG
# ============================================================
def page_location(c):
    draw_cream_bg(c)

    y = H - MARGIN

    # Header
    c.setFillColor(BROWN)
    c.setFont("Times-Roman", 28)
    c.drawString(MARGIN, y - 5, "Beste Lage")
    y -= 10
    c.setFillColor(GOLD)
    c.setFont("Times-Italic", 28)
    c.drawString(MARGIN, y - 28, "in Andratx")
    y -= 40

    draw_gold_line(c, MARGIN, y, 60 * mm, 1.2)
    y -= 25

    # Location description
    c.setFillColor(BROWN)
    c.setFont("Helvetica", 10)
    loc_text = [
        "Andratx gehoert zu den beliebtesten Gemeinden im Suedwesten",
        "Mallorcas. Das charmante Dorf bietet eine perfekte Mischung aus",
        "mallorquinischer Authentizitaet und internationalem Flair.",
        "",
        "Die Finca liegt zentral und dennoch ruhig — nur wenige Gehminuten",
        "vom Ortskern entfernt, mit seiner Auswahl an Restaurants, Cafes",
        "und Geschaeften."
    ]
    for line in loc_text:
        c.drawString(MARGIN, y, line)
        y -= 15

    y -= 10

    # Large image
    img_h = 200
    draw_image_cover(c, img_path("02-exterior.jpg"), MARGIN, y - img_h, CONTENT_W, img_h)
    y -= img_h + 20

    # Distance boxes
    distances = [
        ("5 Min.", "zu Fuss ins Dorf Andratx", "Restaurants, Cafes, Geschaefte"),
        ("10 Min.", "zum naechsten Strand", "Port d'Andratx & Sant Elm"),
        ("30 Min.", "nach Palma de Mallorca", "Flughafen, Altstadt, Shopping"),
    ]

    box_w = (CONTENT_W - 2 * 8) / 3
    box_h = 90

    for i, (time_val, dest, detail) in enumerate(distances):
        bx = MARGIN + i * (box_w + 8)
        by = y - box_h

        # Box background
        draw_rounded_rect(c, bx, by, box_w, box_h, radius=6,
                         fill_color=LIGHT_CREAM, stroke_color=GOLD, stroke_width=0.5)

        # Time value
        c.setFillColor(TERRACOTTA)
        c.setFont("Times-Roman", 24)
        c.drawCentredString(bx + box_w / 2, by + box_h - 30, time_val)

        # Destination
        c.setFillColor(BROWN)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(bx + box_w / 2, by + box_h - 50, dest)

        # Detail
        c.setFillColor(GOLD)
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(bx + box_w / 2, by + 12, detail)

    y -= box_h + 25

    # Additional location info
    c.setFillColor(BROWN)
    c.setFont("Helvetica", 9.5)
    more_info = [
        "Die Serra de Tramuntana, UNESCO-Welterbe, beginnt direkt vor der Haustuer.",
        "Wochenmarkt jeden Mittwoch im Ortszentrum von Andratx.",
        "Golfplaetze, Yachthaefen und Wanderwege in unmittelbarer Naehe.",
    ]
    for info in more_info:
        c.setFillColor(GOLD)
        c.drawString(MARGIN + 5, y, "—")
        c.setFillColor(BROWN)
        c.drawString(MARGIN + 20, y, info)
        y -= 16

    # Footer
    draw_gold_line(c, MARGIN, 18 * mm, CONTENT_W, 0.5)
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 7)
    c.drawCentredString(W / 2, 13 * mm, "Ref: 2471C  |  arquitecto@c-df.com  |  +34 670 06 87 74")


# ============================================================
# PAGE 5 - GRUNDRISSE
# ============================================================
def page_plans(c):
    draw_cream_bg(c)

    y = H - MARGIN

    # Header
    c.setFillColor(BROWN)
    c.setFont("Times-Roman", 28)
    c.drawString(MARGIN, y - 5, "Grundrisse")
    y -= 15

    draw_gold_line(c, MARGIN, y, 60 * mm, 1.2)
    y -= 15

    # Layout: 2 plans on top row, 2 on middle, 1 on bottom centered
    gap = 8
    plan_w = (CONTENT_W - gap) / 2
    plan_h = 195

    plans = ["plan1.jpg", "plan2.jpg", "plan3.jpg", "plan4.jpg", "plan5.jpg"]

    # Row 1
    draw_image_fit(c, img_path(plans[0]), MARGIN, y - plan_h, plan_w, plan_h)
    # Thin border
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.3)
    c.rect(MARGIN, y - plan_h, plan_w, plan_h, fill=0, stroke=1)

    draw_image_fit(c, img_path(plans[1]), MARGIN + plan_w + gap, y - plan_h, plan_w, plan_h)
    c.rect(MARGIN + plan_w + gap, y - plan_h, plan_w, plan_h, fill=0, stroke=1)

    y -= plan_h + gap

    # Row 2
    draw_image_fit(c, img_path(plans[2]), MARGIN, y - plan_h, plan_w, plan_h)
    c.rect(MARGIN, y - plan_h, plan_w, plan_h, fill=0, stroke=1)

    draw_image_fit(c, img_path(plans[3]), MARGIN + plan_w + gap, y - plan_h, plan_w, plan_h)
    c.rect(MARGIN + plan_w + gap, y - plan_h, plan_w, plan_h, fill=0, stroke=1)

    y -= plan_h + gap

    # Row 3 - centered
    small_plan_w = plan_w
    small_plan_h = plan_h - 20
    cx = (W - small_plan_w) / 2
    draw_image_fit(c, img_path(plans[4]), cx, y - small_plan_h, small_plan_w, small_plan_h)
    c.rect(cx, y - small_plan_h, small_plan_w, small_plan_h, fill=0, stroke=1)

    # Footer
    draw_gold_line(c, MARGIN, 18 * mm, CONTENT_W, 0.5)
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 7)
    c.drawCentredString(W / 2, 13 * mm, "Ref: 2471C  |  arquitecto@c-df.com  |  +34 670 06 87 74")


# ============================================================
# PAGE 6 - KONTAKT
# ============================================================
def page_contact(c):
    draw_cream_bg(c)

    y = H - MARGIN

    # Header
    c.setFillColor(BROWN)
    c.setFont("Times-Roman", 28)
    c.drawString(MARGIN, y - 5, "Interesse?")
    y -= 10
    c.setFillColor(GOLD)
    c.setFont("Times-Italic", 28)
    c.drawString(MARGIN, y - 28, "Kontaktieren Sie uns.")
    y -= 40

    draw_gold_line(c, MARGIN, y, 60 * mm, 1.2)
    y -= 35

    # Intro text
    c.setFillColor(BROWN)
    c.setFont("Helvetica", 10.5)
    intro = [
        "Wir freuen uns auf Ihre Anfrage. Vereinbaren Sie einen",
        "persoenlichen Besichtigungstermin oder fordern Sie weitere",
        "Informationen zu dieser einzigartigen Finca an.",
    ]
    for line in intro:
        c.drawString(MARGIN, y, line)
        y -= 15

    y -= 20

    # Contact card
    card_h = 140
    card_w = CONTENT_W
    draw_rounded_rect(c, MARGIN, y - card_h, card_w, card_h,
                     radius=8, fill_color=BROWN)

    # Gold border inside
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    inset = 6
    p = c.beginPath()
    p.roundRect(MARGIN + inset, y - card_h + inset, card_w - 2*inset, card_h - 2*inset, 6)
    c.drawPath(p, fill=0, stroke=1)

    # Contact details inside card
    cx = MARGIN + 30
    cy = y - 35

    c.setFillColor(GOLD)
    c.setFont("Helvetica", 8)
    c.drawString(cx, cy, "E-MAIL")
    c.setFillColor(WHITE)
    c.setFont("Times-Roman", 16)
    c.drawString(cx, cy - 20, "arquitecto@c-df.com")

    cy -= 50
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 8)
    c.drawString(cx, cy, "TELEFON")
    c.setFillColor(WHITE)
    c.setFont("Times-Roman", 16)
    c.drawString(cx, cy - 20, "+34 670 06 87 74")

    # Reference on right side
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 8)
    c.drawRightString(W - MARGIN - 30, y - 35, "REFERENZ")
    c.setFillColor(WHITE)
    c.setFont("Times-Roman", 22)
    c.drawRightString(W - MARGIN - 30, y - 58, "2471C")

    y -= card_h + 30

    # QR Code section
    c.setFillColor(BROWN)
    c.setFont("Times-Roman", 14)
    c.drawString(MARGIN, y, "Weitere Informationen online:")
    y -= 10

    c.setFillColor(GOLD)
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN, y - 8, "https://angelo8306.github.io/finca-andratx/")

    # QR Code
    qr_size = 80
    qr_img = generate_qr_code("https://angelo8306.github.io/finca-andratx/")
    qr_x = W - MARGIN - qr_size
    qr_y = y - qr_size + 10
    c.drawImage(qr_img, qr_x, qr_y, qr_size, qr_size)

    # Label under QR
    c.setFillColor(BROWN)
    c.setFont("Helvetica", 7)
    c.drawCentredString(qr_x + qr_size / 2, qr_y - 12, "QR-Code scannen")

    y -= qr_size + 30

    # Gold separator
    draw_gold_line(c, MARGIN, y, CONTENT_W, 0.8)
    y -= 25

    # Disclaimer
    c.setFillColor(BROWN)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(W / 2, y, "Alle Angaben ohne Gewaehr. Aenderungen vorbehalten.")
    c.drawCentredString(W / 2, y - 12, "Die angegebenen Flaechen sind ca.-Angaben. Irrtum und Zwischenverkauf vorbehalten.")

    # Bottom bar
    bar_h = 20 * mm
    c.setFillColor(BROWN)
    c.rect(0, 0, W, bar_h, fill=1, stroke=0)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.line(0, bar_h, W, bar_h)

    c.setFillColor(GOLD)
    c.setFont("Times-Italic", 10)
    c.drawCentredString(W / 2, bar_h / 2 + 3, "Finca in Andratx — Ihr Traum auf Mallorca")
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 7)
    c.drawCentredString(W / 2, bar_h / 2 - 10, "arquitecto@c-df.com  |  +34 670 06 87 74  |  Ref: 2471C")


# ============================================================
# MAIN - Build PDF
# ============================================================
def main():
    print("Erstelle Expose PDF...")

    c = canvas.Canvas(OUTPUT_PATH, pagesize=A4)
    c.setTitle("Finca in Andratx - Verkaufsexpose")
    c.setAuthor("C-DF Arquitectos")
    c.setSubject("Immobilien-Expose Finca Andratx, Mallorca")

    # Page 1 - Title
    page_title(c)
    c.showPage()

    # Page 2 - Overview
    page_overview(c)
    c.showPage()

    # Page 3 - Interior
    page_interior(c)
    c.showPage()

    # Page 4 - Location
    page_location(c)
    c.showPage()

    # Page 5 - Floor plans
    page_plans(c)
    c.showPage()

    # Page 6 - Contact
    page_contact(c)
    c.showPage()

    c.save()
    print(f"PDF gespeichert: {OUTPUT_PATH}")

    # Verify
    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"Dateigroesse: {file_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
