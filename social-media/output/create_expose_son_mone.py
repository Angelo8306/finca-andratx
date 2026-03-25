#!/usr/bin/env python3
"""
Expose PDF Generator - Finca Son Mone
6-seitiges luxurioeses Immobilien-Expose
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
from PIL import Image
import os

# ── Paths ──
IMG_DIR = "/Users/angelojuric/Documents/Cay Fingerle/Finca Cay Fingerle/images/"
OUTPUT = "/Users/angelojuric/Documents/Cay Fingerle/Finca Cay Fingerle/social-media/output/Expose_Finca_Son_Mone.pdf"

# ── Colors ──
CREAM = HexColor("#F5F0E8")
DEEP_BROWN = HexColor("#2C2420")
GOLD = HexColor("#C9A96E")
TERRACOTTA = HexColor("#C4754B")
LIGHT_CREAM = HexColor("#FAF8F3")
DARK_OVERLAY = Color(0.17, 0.14, 0.12, 0.55)
DARK_OVERLAY_HEAVY = Color(0.17, 0.14, 0.12, 0.70)

# ── Page dimensions ──
W, H = A4  # 210 x 297 mm
MARGIN = 15 * mm

def img(name):
    return os.path.join(IMG_DIR, name)

def draw_full_image(c, image_path, x, y, w, h, crop_top=0, crop_bottom=0):
    """Draw image filling the area, cropping to fit aspect ratio."""
    pil_img = Image.open(image_path)
    iw, ih = pil_img.size

    # Apply crop if specified (percentages from top/bottom)
    if crop_top > 0 or crop_bottom > 0:
        top_px = int(ih * crop_top)
        bottom_px = int(ih * (1 - crop_bottom))
        pil_img = pil_img.crop((0, top_px, iw, bottom_px))
        iw, ih = pil_img.size

    # Calculate aspect ratios
    target_ratio = w / h
    img_ratio = iw / ih

    if img_ratio > target_ratio:
        # Image is wider - crop sides
        new_w = int(ih * target_ratio)
        offset = (iw - new_w) // 2
        pil_img = pil_img.crop((offset, 0, offset + new_w, ih))
    else:
        # Image is taller - crop top/bottom
        new_h = int(iw / target_ratio)
        offset = (ih - new_h) // 2
        pil_img = pil_img.crop((0, offset, iw, offset + new_h))

    img_reader = ImageReader(pil_img)
    c.drawImage(img_reader, x, y, width=w, height=h)

def draw_overlay(c, x, y, w, h, color=DARK_OVERLAY):
    """Draw a semi-transparent overlay."""
    c.saveState()
    c.setFillColor(color)
    c.rect(x, y, w, h, fill=1, stroke=0)
    c.restoreState()

def draw_gold_line(c, x, y, width, thickness=0.5):
    """Draw a gold horizontal line."""
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(thickness)
    c.line(x, y, x + width, y)
    c.restoreState()

def draw_text_block(c, text, x, y, font="Helvetica", size=10, color=DEEP_BROWN, max_width=None, leading=None):
    """Draw text, returns the y position after drawing."""
    if leading is None:
        leading = size * 1.4
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(color)

    if max_width:
        lines = []
        words = text.split()
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, font, size) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        for line in lines:
            c.drawString(x, y, line)
            y -= leading
    else:
        c.drawString(x, y, text)
        y -= leading

    c.restoreState()
    return y

def draw_centered_text(c, text, y, font="Helvetica", size=10, color=DEEP_BROWN):
    """Draw centered text on the page."""
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(color)
    tw = c.stringWidth(text, font, size)
    c.drawString((W - tw) / 2, y, text)
    c.restoreState()

def draw_right_text(c, text, x, y, font="Helvetica", size=10, color=DEEP_BROWN):
    """Draw right-aligned text."""
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(color)
    tw = c.stringWidth(text, font, size)
    c.drawString(x - tw, y, text)
    c.restoreState()


# ═══════════════════════════════════════════════════════════════
# PAGE 1 — Cover
# ═══════════════════════════════════════════════════════════════
def page_cover(c):
    # Full-page facade image
    draw_full_image(c, img("01-facade.jpg"), 0, 0, W, H)

    # Dark gradient overlay at bottom
    draw_overlay(c, 0, 0, W, H * 0.50, Color(0.17, 0.14, 0.12, 0.75))
    draw_overlay(c, 0, H * 0.50, W, H * 0.50, Color(0.17, 0.14, 0.12, 0.25))

    # Top: Gold line accent
    draw_gold_line(c, W/2 - 40*mm, H - 30*mm, 80*mm, 0.8)

    # Top: Small label
    c.saveState()
    c.setFont("Helvetica", 7.5)
    c.setFillColor(GOLD)
    label = "E X K L U S I V E S   I M M O B I L I E N - E X P O S E"
    tw = c.stringWidth(label, "Helvetica", 7.5)
    c.drawString((W - tw)/2, H - 25*mm, label)
    c.restoreState()

    # Main title area - centered lower third
    y_center = H * 0.30

    # "SON MONE" - large title
    c.saveState()
    c.setFont("Helvetica", 52)
    c.setFillColor(white)
    title = "SON MONE"
    tw = c.stringWidth(title, "Helvetica", 52)
    c.drawString((W - tw)/2, y_center + 25*mm, title)
    c.restoreState()

    # Gold line under title
    draw_gold_line(c, W/2 - 30*mm, y_center + 20*mm, 60*mm, 1)

    # Subtitle
    c.saveState()
    c.setFont("Helvetica", 11)
    c.setFillColor(CREAM)
    sub = "Historisches Landgut  |  Andratx, Mallorca"
    tw = c.stringWidth(sub, "Helvetica", 11)
    c.drawString((W - tw)/2, y_center + 8*mm, sub)
    c.restoreState()

    # Tagline
    c.saveState()
    c.setFont("Helvetica-Oblique", 9.5)
    c.setFillColor(Color(0.79, 0.66, 0.43, 0.9))
    tag = "37 Jahre Lebenswerk eines Architekten"
    tw = c.stringWidth(tag, "Helvetica-Oblique", 9.5)
    c.drawString((W - tw)/2, y_center - 4*mm, tag)
    c.restoreState()

    # Bottom info bar
    c.saveState()
    c.setFont("Helvetica", 8)
    c.setFillColor(Color(1, 1, 1, 0.6))

    ref_text = "Ref: 2471C"
    c.drawString(MARGIN, 12*mm, ref_text)

    price = "1.800.000 EUR"
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(GOLD)
    tw = c.stringWidth(price, "Helvetica-Bold", 9)
    c.drawString(W - MARGIN - tw, 12*mm, price)
    c.restoreState()


# ═══════════════════════════════════════════════════════════════
# PAGE 2 — Die Geschichte / Story
# ═══════════════════════════════════════════════════════════════
def page_story(c):
    # Cream background
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Top image strip - exterior
    img_h = 95 * mm
    draw_full_image(c, img("02-exterior.jpg"), 0, H - img_h, W, img_h)
    draw_overlay(c, 0, H - img_h, W, img_h, Color(0.17, 0.14, 0.12, 0.20))

    # Gold label on image
    c.saveState()
    c.setFont("Helvetica", 7)
    c.setFillColor(GOLD)
    label = "D I E   G E S C H I C H T E"
    tw = c.stringWidth(label, "Helvetica", 7)
    c.drawString((W - tw)/2, H - 18*mm, label)
    c.restoreState()

    # Content area below image
    content_top = H - img_h - 12*mm
    left_col = MARGIN + 5*mm
    right_col = W/2 + 5*mm
    col_width = W/2 - MARGIN - 10*mm

    # Title
    c.saveState()
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(DEEP_BROWN)
    c.drawString(left_col, content_top, "Ein Lebenswerk")
    c.restoreState()

    draw_gold_line(c, left_col, content_top - 5*mm, 40*mm, 0.8)

    # Left column text
    y = content_top - 16*mm

    story_left = [
        "Kai ist Architekt. Spezialisiert auf High-End-Villen.",
        "Aber sein groessteswerk wurde keine Villa auf",
        "Bestellung. Es wurde sein eigenes Zuhause.",
        "",
        "Vor 37 Jahren entdeckte er Son Mone -- eine",
        "125 Jahre alte Ruine vor den Toren von Andratx.",
        "Waehrend andere abrissen und neu bauten, sah Kai",
        "etwas, das es zu bewahren galt.",
        "",
        "Sein Credo: Den Originalzustand erhalten.",
        "Jeden Stein respektieren. Jede Wand erzaehlen lassen.",
    ]

    c.saveState()
    c.setFont("Helvetica", 8.8)
    c.setFillColor(DEEP_BROWN)
    for line in story_left:
        if line == "":
            y -= 5*mm
        else:
            c.drawString(left_col, y, line)
            y -= 4.2*mm
    c.restoreState()

    # Right column text
    y = content_top - 16*mm

    story_right = [
        "37 Jahre lang hat er restauriert, Stein fuer Stein.",
        "Mit Sandstein und Naturstein. Mit Marmor- und",
        "Tonboeden, die schon Generationen vor ihm trugen.",
        "Mit antiken Holzbalken, die die Geschichte des",
        "Hauses in sich tragen.",
        "",
        "Die Eingangstuer aus massivem Olivenholz.",
        "Doppelverglaste Fenster fuer modernen Komfort.",
        "Doppelte Deckenhoehe, die den Raum atmen laesst.",
        "Ein offener Holzkamin als Herzstueck.",
        "",
        "Das Ergebnis: Ein Zuhause, das 125 Jahre",
        "Geschichte mit zeitgemaessem Luxus vereint.",
    ]

    c.saveState()
    c.setFont("Helvetica", 8.8)
    c.setFillColor(DEEP_BROWN)
    for line in story_right:
        if line == "":
            y -= 5*mm
        else:
            c.drawString(right_col, y, line)
            y -= 4.2*mm
    c.restoreState()

    # Gold accent quote at bottom
    quote_y = 28*mm
    draw_gold_line(c, W/2 - 50*mm, quote_y + 12*mm, 100*mm, 0.5)

    c.saveState()
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(TERRACOTTA)
    quote = "\"Jeder Stein hat eine Geschichte. Ich habe sie bewahrt.\""
    tw = c.stringWidth(quote, "Helvetica-Oblique", 10)
    c.drawString((W - tw)/2, quote_y + 2*mm, quote)
    c.restoreState()

    draw_gold_line(c, W/2 - 50*mm, quote_y - 2*mm, 100*mm, 0.5)

    # Page number
    draw_centered_text(c, "2", 8*mm, "Helvetica", 7, GOLD)


# ═══════════════════════════════════════════════════════════════
# PAGE 3 — Impressionen / Bildergalerie
# ═══════════════════════════════════════════════════════════════
def page_impressions(c):
    c.setFillColor(DEEP_BROWN)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Section label at top
    c.saveState()
    c.setFont("Helvetica", 7)
    c.setFillColor(GOLD)
    label = "I M P R E S S I O N E N"
    tw = c.stringWidth(label, "Helvetica", 7)
    c.drawString((W - tw)/2, H - 15*mm, label)
    c.restoreState()

    draw_gold_line(c, W/2 - 20*mm, H - 18*mm, 40*mm, 0.5)

    gap = 3 * mm
    top_y = H - 25*mm

    # Top row: 2 large images side by side
    img_w = (W - 2*MARGIN - gap) / 2
    img_h_large = 82 * mm

    draw_full_image(c, img("03-interior1.jpg"), MARGIN, top_y - img_h_large, img_w, img_h_large)
    draw_full_image(c, img("06-interior4.jpg"), MARGIN + img_w + gap, top_y - img_h_large, img_w, img_h_large)

    # Middle: full width image
    mid_y = top_y - img_h_large - gap
    mid_h = 72 * mm
    draw_full_image(c, img("08-interior6.jpg"), MARGIN, mid_y - mid_h, W - 2*MARGIN, mid_h)

    # Bottom row: 3 images
    bot_y = mid_y - mid_h - gap
    img_w3 = (W - 2*MARGIN - 2*gap) / 3
    img_h3 = 62 * mm

    draw_full_image(c, img("05-interior3.jpg"), MARGIN, bot_y - img_h3, img_w3, img_h3, crop_top=0.15, crop_bottom=0.15)
    draw_full_image(c, img("13-detail1.jpg"), MARGIN + img_w3 + gap, bot_y - img_h3, img_w3, img_h3)
    draw_full_image(c, img("09-view1.jpg"), MARGIN + 2*(img_w3 + gap), bot_y - img_h3, img_w3, img_h3)

    # Captions
    c.saveState()
    c.setFont("Helvetica", 6.5)
    c.setFillColor(Color(1,1,1,0.5))
    c.drawString(MARGIN, bot_y - img_h3 - 4*mm, "Wohnraum  |  Kueche  |  Details  |  Panoramablick Tramuntana")
    c.restoreState()

    # Page number
    draw_centered_text(c, "3", 8*mm, "Helvetica", 7, GOLD)


# ═══════════════════════════════════════════════════════════════
# PAGE 4 — Raumaufteilung & Technik
# ═══════════════════════════════════════════════════════════════
def page_details(c):
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Header
    c.saveState()
    c.setFont("Helvetica", 7)
    c.setFillColor(GOLD)
    label = "R A U M A U F T E I L U N G   &   T E C H N I K"
    tw = c.stringWidth(label, "Helvetica", 7)
    c.drawString((W - tw)/2, H - 15*mm, label)
    c.restoreState()

    draw_gold_line(c, W/2 - 30*mm, H - 18*mm, 60*mm, 0.5)

    # Left column - Floor plans
    left_x = MARGIN
    col_w = W/2 - MARGIN - 3*mm

    # Erdgeschoss title
    y = H - 28*mm
    c.saveState()
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(DEEP_BROWN)
    c.drawString(left_x, y, "Erdgeschoss")
    c.setFont("Helvetica", 9)
    c.setFillColor(TERRACOTTA)
    c.drawString(left_x + c.stringWidth("Erdgeschoss  ", "Helvetica-Bold", 13), y, "115,78 m2")
    c.restoreState()

    y -= 8*mm
    items_eg = [
        "Grosszuegiger Wohn- und Essraum",
        "Voll ausgestattete Kueche",
        "Doppelschlafzimmer",
        "Separates WC",
        "Duschbad",
    ]
    c.saveState()
    c.setFont("Helvetica", 8.5)
    c.setFillColor(DEEP_BROWN)
    for item in items_eg:
        c.setFillColor(GOLD)
        c.drawString(left_x + 2*mm, y + 0.5*mm, "—")
        c.setFillColor(DEEP_BROWN)
        c.drawString(left_x + 8*mm, y, item)
        y -= 5*mm
    c.restoreState()

    # Obergeschoss
    y -= 6*mm
    c.saveState()
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(DEEP_BROWN)
    c.drawString(left_x, y, "Obergeschoss")
    c.setFont("Helvetica", 9)
    c.setFillColor(TERRACOTTA)
    c.drawString(left_x + c.stringWidth("Obergeschoss  ", "Helvetica-Bold", 13), y, "115,78 m2")
    c.restoreState()

    y -= 8*mm
    items_og = [
        "Master-Schlafzimmer mit Bad en Suite",
        "Studio / Schlafzimmer",
        "Eigener Treppenaufgang",
    ]
    c.saveState()
    c.setFont("Helvetica", 8.5)
    c.setFillColor(DEEP_BROWN)
    for item in items_og:
        c.setFillColor(GOLD)
        c.drawString(left_x + 2*mm, y + 0.5*mm, "—")
        c.setFillColor(DEEP_BROWN)
        c.drawString(left_x + 8*mm, y, item)
        y -= 5*mm
    c.restoreState()

    # Aussen
    y -= 6*mm
    c.saveState()
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(DEEP_BROWN)
    c.drawString(left_x, y, "Aussenbereich")
    c.restoreState()

    y -= 8*mm
    items_out = [
        "Terrasse 134 m2 (Vordach 36,35 m2)",
        "Grundstueck 2.345 m2",
        "Suedwest-Ausrichtung",
        "Panoramablick Tramuntana-Gebirge",
        "Whirlpool",
        "Mandelbaeume",
        "Gemuese- und Obstanbau moeglich",
    ]
    c.saveState()
    c.setFont("Helvetica", 8.5)
    for item in items_out:
        c.setFillColor(GOLD)
        c.drawString(left_x + 2*mm, y + 0.5*mm, "—")
        c.setFillColor(DEEP_BROWN)
        c.drawString(left_x + 8*mm, y, item)
        y -= 5*mm
    c.restoreState()

    # Right column - Technik & Materialien
    right_x = W/2 + 5*mm
    y = H - 28*mm

    c.saveState()
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(DEEP_BROWN)
    c.drawString(right_x, y, "Materialien")
    c.restoreState()

    y -= 8*mm
    materials = [
        "Sandstein & Naturstein (Original)",
        "Marmor- und Tonboeden",
        "Antike Holzbalken",
        "Olivenholz-Eingangstuer",
        "Doppelverglasung",
        "Doppelte Deckenhoehe",
        "Offener Holzkamin",
    ]
    c.saveState()
    c.setFont("Helvetica", 8.5)
    for item in materials:
        c.setFillColor(GOLD)
        c.drawString(right_x + 2*mm, y + 0.5*mm, "—")
        c.setFillColor(DEEP_BROWN)
        c.drawString(right_x + 8*mm, y, item)
        y -= 5*mm
    c.restoreState()

    # Technik section
    y -= 8*mm
    c.saveState()
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(DEEP_BROWN)
    c.drawString(right_x, y, "Technik")
    c.restoreState()

    y -= 8*mm
    tech = [
        "Solaranlage",
        "Aerothermie (Waermepumpe)",
        "Fussbodenheizung",
        "Klimaanlage",
    ]
    c.saveState()
    c.setFont("Helvetica", 8.5)
    for item in tech:
        c.setFillColor(GOLD)
        c.drawString(right_x + 2*mm, y + 0.5*mm, "—")
        c.setFillColor(DEEP_BROWN)
        c.drawString(right_x + 8*mm, y, item)
        y -= 5*mm
    c.restoreState()

    # Floor plan image at bottom right
    plan_y = 18*mm
    plan_h = 75*mm
    plan_w = col_w

    # Light background for plan
    c.saveState()
    c.setFillColor(white)
    c.roundRect(right_x - 2*mm, plan_y, plan_w + 4*mm, plan_h + 4*mm, 2*mm, fill=1, stroke=0)
    c.restoreState()

    draw_full_image(c, img("plan1.jpg"), right_x, plan_y + 2*mm, plan_w, plan_h)

    c.saveState()
    c.setFont("Helvetica", 6.5)
    c.setFillColor(Color(0.5, 0.5, 0.5))
    c.drawString(right_x, plan_y - 3*mm, "Grundriss Erdgeschoss")
    c.restoreState()

    # Bottom image on left
    draw_full_image(c, img("09-view1.jpg"), left_x, 18*mm, col_w, 75*mm)
    draw_overlay(c, left_x, 18*mm, col_w, 20*mm, Color(0.17, 0.14, 0.12, 0.5))

    c.saveState()
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(white)
    c.drawString(left_x + 4*mm, 24*mm, "Blick auf die Tramuntana")
    c.restoreState()

    # Page number
    draw_centered_text(c, "4", 8*mm, "Helvetica", 7, GOLD)


# ═══════════════════════════════════════════════════════════════
# PAGE 5 — Lage & Eckdaten
# ═══════════════════════════════════════════════════════════════
def page_location(c):
    # Top half: View image
    top_h = H * 0.45
    draw_full_image(c, img("09-view1.jpg"), 0, H - top_h, W, top_h)
    draw_overlay(c, 0, H - top_h, W, top_h, Color(0.17, 0.14, 0.12, 0.30))

    # Label on image
    c.saveState()
    c.setFont("Helvetica", 7)
    c.setFillColor(GOLD)
    label = "L A G E   &   E C K D A T E N"
    tw = c.stringWidth(label, "Helvetica", 7)
    c.drawString((W - tw)/2, H - 18*mm, label)
    c.restoreState()

    # Title on image
    c.saveState()
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(white)
    title = "Andratx, Mallorca"
    tw = c.stringWidth(title, "Helvetica-Bold", 26)
    c.drawString((W - tw)/2, H - top_h + 30*mm, title)
    c.restoreState()

    c.saveState()
    c.setFont("Helvetica", 10)
    c.setFillColor(CREAM)
    sub = "Direkt ausserhalb des Dorfes  |  Suedwest-Ausrichtung"
    tw = c.stringWidth(sub, "Helvetica", 10)
    c.drawString((W - tw)/2, H - top_h + 18*mm, sub)
    c.restoreState()

    # Bottom half: Cream background with data
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H - top_h, fill=1, stroke=0)

    # Key facts in grid
    y_start = H - top_h - 18*mm
    col1_x = MARGIN + 10*mm
    col2_x = W/2 + 10*mm

    facts = [
        ("Wohnflaeche", "231,56 m2"),
        ("Grundstueck", "2.345 m2"),
        ("Terrasse", "134 m2"),
        ("Vordach", "36,35 m2"),
        ("Schlafzimmer", "3"),
        ("Baeder", "2 + WC"),
        ("Ausrichtung", "Suedwest"),
        ("Panoramablick", "Tramuntana"),
    ]

    y = y_start
    for i, (label, value) in enumerate(facts):
        x = col1_x if i % 2 == 0 else col2_x
        if i > 0 and i % 2 == 0:
            y -= 14*mm

        c.saveState()
        c.setFont("Helvetica", 7.5)
        c.setFillColor(GOLD)
        c.drawString(x, y + 4*mm, label.upper())
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(DEEP_BROWN)
        c.drawString(x, y - 4*mm, value)
        c.restoreState()

    y -= 14*mm
    draw_gold_line(c, MARGIN, y, W - 2*MARGIN, 0.5)

    # Location details
    y -= 10*mm
    c.saveState()
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(DEEP_BROWN)
    c.drawString(col1_x, y, "Entfernungen")
    c.restoreState()

    y -= 7*mm
    distances = [
        ("Dorfzentrum Andratx", "5 Min. zu Fuss"),
        ("Port d'Andratx", "10 Min."),
        ("Palma Flughafen", "30 Min."),
        ("Palma Zentrum", "25 Min."),
    ]

    c.saveState()
    for label, value in distances:
        c.setFont("Helvetica", 8.5)
        c.setFillColor(DEEP_BROWN)
        c.drawString(col1_x, y, label)
        c.setFont("Helvetica-Bold", 8.5)
        c.setFillColor(TERRACOTTA)
        c.drawString(col2_x, y, value)
        y -= 5.5*mm
    c.restoreState()

    # Page number
    draw_centered_text(c, "5", 8*mm, "Helvetica", 7, GOLD)


# ═══════════════════════════════════════════════════════════════
# PAGE 6 — Kontakt & Abschluss
# ═══════════════════════════════════════════════════════════════
def page_contact(c):
    # Full bleed exterior image
    draw_full_image(c, img("02-exterior.jpg"), 0, 0, W, H)
    draw_overlay(c, 0, 0, W, H, Color(0.17, 0.14, 0.12, 0.72))

    # Gold line at top
    draw_gold_line(c, W/2 - 40*mm, H - 30*mm, 80*mm, 0.8)

    # Label
    c.saveState()
    c.setFont("Helvetica", 7)
    c.setFillColor(GOLD)
    label = "I H R   N E U E S   Z U H A U S E"
    tw = c.stringWidth(label, "Helvetica", 7)
    c.drawString((W - tw)/2, H - 25*mm, label)
    c.restoreState()

    # Main text
    y = H * 0.62

    c.saveState()
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(white)
    title = "Son Mone"
    tw = c.stringWidth(title, "Helvetica-Bold", 32)
    c.drawString((W - tw)/2, y + 15*mm, title)
    c.restoreState()

    draw_gold_line(c, W/2 - 25*mm, y + 8*mm, 50*mm, 1)

    c.saveState()
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(CREAM)
    tag = "125 Jahre Geschichte. 37 Jahre Restauration. Bereit fuer Sie."
    tw = c.stringWidth(tag, "Helvetica-Oblique", 10)
    c.drawString((W - tw)/2, y - 3*mm, tag)
    c.restoreState()

    # Price
    y_price = H * 0.44

    c.saveState()
    c.setFont("Helvetica", 8)
    c.setFillColor(GOLD)
    plabel = "KAUFPREIS"
    tw = c.stringWidth(plabel, "Helvetica", 8)
    c.drawString((W - tw)/2, y_price + 8*mm, plabel)

    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(white)
    price = "1.800.000 EUR"
    tw = c.stringWidth(price, "Helvetica-Bold", 28)
    c.drawString((W - tw)/2, y_price - 6*mm, price)
    c.restoreState()

    draw_gold_line(c, W/2 - 45*mm, y_price - 15*mm, 90*mm, 0.5)

    # Contact info
    y_contact = H * 0.26

    c.saveState()
    c.setFont("Helvetica", 7.5)
    c.setFillColor(GOLD)
    clabel = "K O N T A K T"
    tw = c.stringWidth(clabel, "Helvetica", 7.5)
    c.drawString((W - tw)/2, y_contact + 12*mm, clabel)
    c.restoreState()

    contact_lines = [
        ("Helvetica-Bold", 10, "arquitecto@c-df.com"),
        ("Helvetica", 10, "+34 670 06 87 74"),
    ]

    y = y_contact
    for font, size, text in contact_lines:
        c.saveState()
        c.setFont(font, size)
        c.setFillColor(white)
        tw = c.stringWidth(text, font, size)
        c.drawString((W - tw)/2, y, text)
        c.restoreState()
        y -= 6*mm

    # Landing page
    y -= 4*mm
    c.saveState()
    c.setFont("Helvetica", 8)
    c.setFillColor(Color(0.79, 0.66, 0.43, 0.8))
    url = "angelo8306.github.io/finca-andratx"
    tw = c.stringWidth(url, "Helvetica", 8)
    c.drawString((W - tw)/2, y, url)
    c.restoreState()

    # Bottom: Ref
    c.saveState()
    c.setFont("Helvetica", 7)
    c.setFillColor(Color(1, 1, 1, 0.4))
    ref = "Ref: 2471C  |  Son Mone  |  Andratx, Mallorca"
    tw = c.stringWidth(ref, "Helvetica", 7)
    c.drawString((W - tw)/2, 12*mm, ref)
    c.restoreState()

    # Page number
    draw_centered_text(c, "6", 8*mm, "Helvetica", 7, GOLD)


# ═══════════════════════════════════════════════════════════════
# BUILD PDF
# ═══════════════════════════════════════════════════════════════
def build_pdf():
    c = canvas.Canvas(OUTPUT, pagesize=A4)
    c.setTitle("Son Mone - Exklusives Immobilien-Expose")
    c.setAuthor("Cay Fingerle Real Estate")
    c.setSubject("Historisches Landgut in Andratx, Mallorca")

    # Page 1 - Cover
    page_cover(c)
    c.showPage()

    # Page 2 - Story
    page_story(c)
    c.showPage()

    # Page 3 - Impressions
    page_impressions(c)
    c.showPage()

    # Page 4 - Details
    page_details(c)
    c.showPage()

    # Page 5 - Location
    page_location(c)
    c.showPage()

    # Page 6 - Contact
    page_contact(c)
    c.showPage()

    c.save()
    print(f"PDF erstellt: {OUTPUT}")
    print(f"Groesse: {os.path.getsize(OUTPUT) / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    build_pdf()
