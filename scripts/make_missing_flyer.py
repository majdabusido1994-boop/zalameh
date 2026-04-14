from PIL import Image, ImageDraw, ImageFont, ImageOps
import arabic_reshaper
from bidi.algorithm import get_display
import os, random

W, H = 1080, 1920
CREAM = (247, 240, 227)
INK = (31, 27, 24)
KRED = (211, 47, 47)
SUNSET = (243, 156, 62)

img = Image.new("RGB", (W, H), CREAM)
draw = ImageDraw.Draw(img)

# subtle paper noise
random.seed(7)
for _ in range(2500):
    x = random.randint(0, W-1)
    y = random.randint(0, H-1)
    v = random.randint(-8, 4)
    r, g, b = CREAM
    draw.point((x, y), fill=(max(0, min(255, r+v)), max(0, min(255, g+v)), max(0, min(255, b+v))))

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

font_missing = find_font(["impact.ttf", "ariblk.ttf", "arialbd.ttf"], 150)
font_ar_huge = find_font(["tradbdo.ttf", "segoeuib.ttf", "arialbd.ttf"], 150)
font_label = find_font(["arialbd.ttf", "segoeuib.ttf"], 44)
font_ar_line = find_font(["tradbdo.ttf", "segoeuib.ttf"], 54)
font_small = find_font(["arialbd.ttf", "segoeuib.ttf"], 34)
font_handle = find_font(["arialbd.ttf", "impact.ttf"], 62)

def ar(s):
    return get_display(arabic_reshaper.reshape(s))

def draw_rotated_text(base, xy, text, font, fill, angle, pad=100):
    bbox = font.getbbox(text)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    txt_img = Image.new("RGBA", (tw+pad*2, th+pad*2), (0,0,0,0))
    td = ImageDraw.Draw(txt_img)
    td.text((pad, pad), text, font=font, fill=fill)
    rotated = txt_img.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.paste(rotated, (xy[0]-rotated.width//2, xy[1]-rotated.height//2), rotated)

# Top red caution band
draw.rectangle([0, 0, W, 18], fill=KRED)
draw.rectangle([0, H-18, W, H], fill=KRED)
for i in range(0, W+80, 80):
    draw.polygon([(i, 30), (i+40, 30), (i+20, 70), (i-20, 70)], fill=KRED)

# MISSING header
draw_rotated_text(img, (W//2, 250), "MISSING", font_missing, INK, 2)

# مفقود (Arabic) — bigger padding so descenders are not cut
draw_rotated_text(img, (W//2, 440), ar("مفقود"), font_ar_huge, KRED, -2, pad=140)

# Cover image — cat only
cover = Image.open("../website/images/zalameh-cat.png").convert("RGBA")
# flatten on cream
bg = Image.new("RGB", cover.size, CREAM)
bg.paste(cover, mask=cover.split()[3] if cover.mode == "RGBA" else None)
cover = bg
cover_size = 720
cover = cover.resize((cover_size, cover_size), Image.LANCZOS)
framed = ImageOps.expand(cover, border=10, fill=INK)
frame_x = (W - framed.width)//2
frame_y = 600
img.paste(framed, (frame_x, frame_y))

# Small forward-facing inset (cat face from zan-zan cover)
inset_src = Image.open("../artwork/covers/zan-zan-cover-3000.jpg").convert("RGB")
# Crop the cat on the shoulder (upper-right of the duo)
inset_crop = inset_src.crop((1720, 340, 2560, 1180))
inset_size = 220
inset = inset_crop.resize((inset_size, inset_size), Image.LANCZOS)
inset_framed = ImageOps.expand(inset, border=8, fill=INK)
# Place on bottom-right corner of main photo
ix = frame_x + framed.width - inset_framed.width - 20
iy = frame_y + framed.height - inset_framed.height - 20
img.paste(inset_framed, (ix, iy))

# Info lines
y = 1400
line_h = 62

draw.text((80, y), "NAME:", font=font_label, fill=INK)
draw.text((260, y), "ZALAMEH", font=font_label, fill=KRED)
y += line_h

draw.text((80, y), "LAST SEEN:", font=font_label, fill=INK)
draw.text((340, y), "rooftop, Jabal Amman", font=font_label, fill=INK)
y += line_h

draw.text((80, y), "Bites if his songs are skipped.", font=font_label, fill=INK)
y += line_h - 4

# Arabic bite line, right-aligned
arabic_bite = ar("بِعُضّ إذا فَشَقت أغانيه")
arb = draw.textbbox((0,0), arabic_bite, font=font_ar_line)
arw = arb[2]-arb[0]
draw.text((W - arw - 80, y), arabic_bite, font=font_ar_line, fill=INK)
y += line_h + 4

draw.text((80, y), "REWARD:", font=font_label, fill=INK)
draw.text((280, y), "a follow.", font=font_label, fill=KRED)

# PLEASE SHARE stamp at bottom
font_share = find_font(["impact.ttf", "ariblk.ttf", "arialbd.ttf"], 110)
draw_rotated_text(img, (W//2, 1820), "PLEASE SHARE", font_share, KRED, -3, pad=80)


out = "../artwork/social/missing-zalameh-story.jpg"
img.save(out, quality=94)
print("saved:", out, os.path.getsize(out))
