from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import os

W, H = 2560, 1440
CREAM = (247, 240, 227)
INK = (31, 27, 24)
KRED = (211, 47, 47)
SUNSET = (243, 156, 62)
TERRA = (196, 87, 42)

# Safe zone for all devices: center 1546x423
SAFE_W, SAFE_H = 1546, 423
SAFE_X = (W - SAFE_W) // 2   # 507
SAFE_Y = (H - SAFE_H) // 2   # 508

img = Image.new("RGB", (W, H), CREAM)
draw = ImageDraw.Draw(img)

# keffiyeh-style top + bottom bands
band_h = 20
for x in range(0, W, 40):
    draw.rectangle([x, 0, x+20, band_h], fill=KRED)
    draw.rectangle([x+20, 0, x+40, band_h], fill=CREAM)
    draw.rectangle([x, H-band_h, x+20, H], fill=KRED)
    draw.rectangle([x+20, H-band_h, x+40, H], fill=CREAM)
draw.rectangle([0, band_h, W, band_h+3], fill=INK)
draw.rectangle([0, H-band_h-3, W, H-band_h], fill=INK)

# Side decorative bands outside safe zone (visible on TV/desktop only)
draw.rectangle([0, 0, SAFE_X-40, H], fill=CREAM)
draw.rectangle([SAFE_X+SAFE_W+40, 0, W, H], fill=CREAM)

def find_font(names, size):
    font_dir = r"C:\Windows\Fonts"
    for n in names:
        p = os.path.join(font_dir, n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_big = find_font(["impact.ttf", "ariblk.ttf", "arialbd.ttf"], 180)
font_ar = find_font(["tradbdo.ttf", "arabtype.ttf", "segoeuib.ttf", "arialbd.ttf"], 90)
font_tag = find_font(["arialbd.ttf", "segoeuib.ttf"], 36)
font_small = find_font(["arialbd.ttf", "segoeuib.ttf"], 30)

# paste duo image inside safe zone, on the left
duo = Image.open("../artwork/brand/zalameh-logo-master.png").convert("RGBA")
duo_h = 520
ratio = duo_h / duo.height
duo_w = int(duo.width * ratio)
duo_resized = duo.resize((duo_w, duo_h), Image.LANCZOS)
duo_x = SAFE_X + 20
duo_y = SAFE_Y + (SAFE_H - duo_h) // 2
img.paste(duo_resized, (duo_x, duo_y), duo_resized)

# text column inside safe zone, to the right of duo
col_x = duo_x + duo_w + 60

# Accent chip above title
chip_w, chip_h = 540, 44
chipx = col_x
chipy = SAFE_Y + 20
draw.rectangle([chipx, chipy, chipx+chip_w, chipy+chip_h], fill=INK)
draw.text((chipx+16, chipy+6), "FROM THE HEART OF THE HILLS", font=font_small, fill=SUNSET)

# Title "ZALAMEH"
title = "ZALAMEH"
ty = chipy + chip_h + 15
draw.text((col_x+5, ty+5), title, font=font_big, fill=INK)
draw.text((col_x, ty), title, font=font_big, fill=KRED)

# Tagline + URL (bottom of safe zone)
tag_y = SAFE_Y + SAFE_H - 100
draw.text((col_x, tag_y), "Amman's smuggest cat", font=font_tag, fill=INK)
draw.text((col_x, tag_y + 48), "zalameh.netlify.app", font=font_tag, fill=TERRA)

# Arabic decoration OUTSIDE safe zone (right side, visible on desktop/TV)
font_ar_big = find_font(["tradbdo.ttf", "arabtype.ttf", "segoeuib.ttf", "arialbd.ttf"], 200)
ar_raw = "زَلَمة"
ar = get_display(arabic_reshaper.reshape(ar_raw))
ar_x, ar_y = 2130, 420
draw.text((ar_x+5, ar_y+5), ar, font=font_ar_big, fill=INK)
draw.text((ar_x, ar_y), ar, font=font_ar_big, fill=TERRA)

# Outer-zone decor (only visible on TV/desktop): EST stamp far left, socials far right
est_box = [120, 640, 440, 740]
draw.rectangle(est_box, outline=INK, width=5)
draw.text((est_box[0]+26, est_box[1]+24), "EST. 2026", font=find_font(["arialbd.ttf"], 52), fill=INK)

soc_font = find_font(["arialbd.ttf", "segoeuib.ttf"], 38)
draw.text((2130, 900), "@zalameh.69", font=soc_font, fill=INK)
draw.text((2130, 945), "Spotify · YouTube", font=soc_font, fill=TERRA)

out_path = "../artwork/brand/zalameh-youtube-banner.png"
img.save(out_path, quality=95)
print("saved:", out_path, "size:", os.path.getsize(out_path))
