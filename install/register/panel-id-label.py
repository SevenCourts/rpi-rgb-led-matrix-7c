#!/usr/bin/env python3
"""
panel-id-label.py

Generates a label strip PNG for a panel ID, suitable for Brother P-Touch 2730
(12mm TZe tape, 76px print height). Output is a 1-bit B/W PNG for use with
ptouch-print --image.

Layout:
  [WiFi setup: iOS <QR> Android <QR>] [panel_id x2 small] [panel_id x4 large]

Usage:
    python3 panel-id-label.py <PANEL_ID> <OUTPUT_PNG>

Example:
    python3 panel-id-label.py f03b3c53 /tmp/label.png
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont
import qrcode

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(SCRIPT_DIR, "Montserrat-Regular.ttf")

# Label dimensions
TAPE_HEIGHT = 76
PAD_LEFT = 20
GAP = 40
TEXT_GAP = 10
QR_SIZE = 72

# Font sizes
FONT_SIZE_LARGE = 82
FONT_SIZE_SMALL = 64
FONT_SIZE_INFO = 64

# Panel ID repetitions
SMALL_COUNT = 2
LARGE_COUNT = 4

# QR code URLs
IOS_APP_URL = "https://apps.apple.com/de/app/sevencourts-scoreboards-admin/id6760492447"
ANDROID_APP_URL = "https://play.google.com/store/apps/details?id=com.sevencourts.admin"


def make_qr(url):
    """Generate a 1-bit QR code image scaled to QR_SIZE."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=0,
    )
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("1")
    return qr_img.resize((QR_SIZE, QR_SIZE), Image.NEAREST)


def generate_label(panel_id, output_path):
    font_info = ImageFont.truetype(FONT_PATH, FONT_SIZE_INFO)
    font_large = ImageFont.truetype(FONT_PATH, FONT_SIZE_LARGE)
    font_small = ImageFont.truetype(FONT_PATH, FONT_SIZE_SMALL)

    qr_ios = make_qr(IOS_APP_URL)
    qr_android = make_qr(ANDROID_APP_URL)

    small_text = "  ".join([panel_id] * SMALL_COUNT)
    large_text = "  ".join([panel_id] * LARGE_COUNT)

    # Layout: info section (text + QR codes) + gap + small IDs + gap + large IDs
    # Info section items: text or None (QR placeholder)
    info_items = [
        ("WiFi setup:  iOS ", font_info),
        None,  # iOS QR
        ("  Android ", font_info),
        None,  # Android QR
    ]
    qr_images = [qr_ios, qr_android]

    draw_tmp = ImageDraw.Draw(Image.new("1", (1, 1)))

    # Calculate total width
    x = PAD_LEFT
    for item in info_items:
        if item is None:
            x += QR_SIZE + TEXT_GAP
        else:
            text, font = item
            bbox = draw_tmp.textbbox((0, 0), text, font=font)
            x += bbox[2] - bbox[0]

    x += GAP
    bbox_small = draw_tmp.textbbox((0, 0), small_text, font=font_small)
    x += bbox_small[2] - bbox_small[0]
    x += GAP
    bbox_large = draw_tmp.textbbox((0, 0), large_text, font=font_large)
    x += bbox_large[2] - bbox_large[0]
    total_width = x

    # Create image
    img = Image.new("1", (total_width, TAPE_HEIGHT), color=1)
    draw = ImageDraw.Draw(img)

    # Draw info section
    x = PAD_LEFT
    qr_idx = 0
    for item in info_items:
        if item is None:
            qr_y = (TAPE_HEIGHT - QR_SIZE) // 2
            img.paste(qr_images[qr_idx], (x, qr_y))
            x += QR_SIZE + TEXT_GAP
            qr_idx += 1
        else:
            text, font = item
            bbox = draw.textbbox((0, 0), text, font=font)
            text_h = bbox[3] - bbox[1]
            y = (TAPE_HEIGHT - text_h) // 2 - bbox[1]
            draw.text((x, y), text, font=font, fill=0)
            x += bbox[2] - bbox[0]

    x += GAP

    # Draw small panel IDs
    bbox = draw.textbbox((0, 0), small_text, font=font_small)
    text_h = bbox[3] - bbox[1]
    y = (TAPE_HEIGHT - text_h) // 2 - bbox[1]
    draw.text((x, y), small_text, font=font_small, fill=0)
    x += bbox[2] - bbox[0]
    x += GAP

    # Draw large panel IDs
    bbox = draw.textbbox((0, 0), large_text, font=font_large)
    text_h = bbox[3] - bbox[1]
    y = (TAPE_HEIGHT - text_h) // 2 - bbox[1]
    draw.text((x, y), large_text, font=font_large, fill=0)

    img.save(output_path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <PANEL_ID> <OUTPUT_PNG>", file=sys.stderr)
        sys.exit(1)

    generate_label(sys.argv[1], sys.argv[2])
