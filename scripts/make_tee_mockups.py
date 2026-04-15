"""Flat T-shirt mockups — front & back, black & cream.

Front: small cat-keffiyeh sticker chest logo + "ZALAMEH" text + Arabic "زَلَمة" under
Back:  big Arabic "خَليكي" as statement print

Outputs: website/images/tee-{color}-{side}.png  (4 files)
Also: a spec sheet PNG for the print shop.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import arabic_reshaper
from bidi.algorithm import get_display

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

W, H = 1600, 1900  # mockup canvas

def find_font(names, size):
    fd = r"C:\Windows\Fonts"
    for n in names:
        p = os.path.join(fd, n)
        if os.path.isfile(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def ar(s): return get_display(arabic_reshaper.reshape(s))

COLORS = {
    "black": {"shirt": (22, 22, 22), "text_primary": (247, 240, 227), "text_accent": (243, 156, 62)},
    "cream": {"shirt": (247, 240, 227), "text_primary": (31, 27, 24),  "text_accent": (211, 47, 47)},
}

def draw_tee_shape(draw, fill, outline=(0,0,0,0)):
    """Simple flat tee silhouette, centered."""
    # Body
    body = [
        (340, 420),   # left shoulder inner
        (240, 340),   # left shoulder top
        (140, 380),   # left sleeve out
        (60,  540),   # left sleeve bottom out
        (240, 620),   # left sleeve bottom in
        (300, 640),
        (300, 1720),  # left hem
        (1300, 1720),
        (1300, 640),
        (1360, 620),
        (1540, 540),
        (1460, 380),
        (1360, 340),
        (1260, 420),
        (1100, 380),  # neckline right
        (900, 460),   # neck curve right
        (700, 460),   # neck curve left
        (500, 380),   # neckline left
    ]
    draw.polygon(body, fill=fill, outline=outline)
    # Neck rib
    neck_rib = [(560, 380), (700, 450), (900, 450), (1040, 380), (900, 405), (700, 405)]
    shade = tuple(max(0, c-15) for c in fill[:3]) + (fill[3],) if len(fill)==4 else tuple(max(0,c-15) for c in fill)
    draw.polygon(neck_rib, fill=shade)


def make_front(color):
    pal = COLORS[color]
    im = Image.new("RGBA", (W, H), (240, 240, 240, 255))  # grey backdrop
    d = ImageDraw.Draw(im, "RGBA")
    shirt_rgba = pal["shirt"] + (255,)
    draw_tee_shape(d, shirt_rgba)

    # Chest logo: small cat-keffiyeh sticker, left chest
    logo = Image.open("artwork/stickers/sticker-cat-keffiyeh.png").convert("RGBA")
    logo.thumbnail((220, 220), Image.LANCZOS)
    logo_x, logo_y = 780 - logo.width // 2, 640
    im.paste(logo, (logo_x, logo_y), logo)

    # "ZALAMEH" text centered under logo
    font_brand = find_font(["impact.ttf", "arialbd.ttf"], 78)
    font_ar    = find_font(["tradbdo.ttf", "arabtype.ttf", "arialbd.ttf"], 82)
    brand = "ZALAMEH"
    bb = font_brand.getbbox(brand)
    tw = bb[2] - bb[0]
    bx = (W - tw) // 2
    by = logo_y + logo.height + 30
    d.text((bx, by), brand, font=font_brand, fill=pal["text_primary"])

    # Arabic زَلَمة under
    txt = ar("زَلَمة")
    bb = font_ar.getbbox(txt)
    aw = bb[2] - bb[0]
    d.text(((W - aw) // 2, by + 90), txt, font=font_ar, fill=pal["text_accent"])

    # Small 'FRONT' label below tee
    font_tag = find_font(["arialbd.ttf"], 28)
    d.text((W // 2 - 60, H - 70), "FRONT", font=font_tag, fill=(120, 120, 120))
    return im


def make_back(color):
    pal = COLORS[color]
    im = Image.new("RGBA", (W, H), (240, 240, 240, 255))
    d = ImageDraw.Draw(im, "RGBA")
    draw_tee_shape(d, pal["shirt"] + (255,))

    # Big Arabic "خَليكي" centered back
    font_ar_huge = find_font(["tradbdo.ttf", "arabtype.ttf", "arialbd.ttf"], 340)
    txt = ar("خَليكي")
    bb = font_ar_huge.getbbox(txt)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    cx = (W - tw) // 2
    cy = 860
    d.text((cx, cy), txt, font=font_ar_huge, fill=pal["text_primary"])

    # "STAY WITH ME" in english under, small
    font_sub = find_font(["impact.ttf", "arialbd.ttf"], 52)
    sub = "— STAY WITH ME —"
    bb = font_sub.getbbox(sub)
    sw = bb[2] - bb[0]
    d.text(((W - sw) // 2, cy + th + 60), sub, font=font_sub, fill=pal["text_accent"])

    # Tiny ZALAMEH tag bottom hem
    font_tag = find_font(["arialbd.ttf"], 32)
    hem = "ZALAMEH · TRK 03 · @zalameh.69"
    bb = font_tag.getbbox(hem)
    d.text(((W - (bb[2]-bb[0])) // 2, 1640), hem, font=font_tag, fill=pal["text_accent"])

    font_back = find_font(["arialbd.ttf"], 28)
    d.text((W // 2 - 60, H - 70), "BACK", font=font_back, fill=(120, 120, 120))
    return im


os.makedirs("website/images", exist_ok=True)
for color in ("black", "cream"):
    make_front(color).convert("RGB").save(f"website/images/tee-{color}-front.jpg", "JPEG", quality=90)
    make_back(color).convert("RGB").save(f"website/images/tee-{color}-back.jpg",  "JPEG", quality=90)
    print(f"tee-{color}-front.jpg  tee-{color}-back.jpg")


# ---- Print shop spec sheet ----
def make_spec_sheet():
    SW, SH = 2000, 2800
    im = Image.new("RGB", (SW, SH), (255, 255, 255))
    d = ImageDraw.Draw(im)
    ftitle = find_font(["impact.ttf", "arialbd.ttf"], 100)
    fh = find_font(["arialbd.ttf"], 52)
    fp = find_font(["arial.ttf", "arialbd.ttf"], 40)
    far= find_font(["tradbdo.ttf", "arialbd.ttf"], 64)

    d.rectangle([0, 0, SW, 140], fill=(31, 27, 24))
    d.text((50, 30), "ZALAMEH · TEE PRINT SPEC", font=ftitle, fill=(247, 240, 227))

    y = 190
    sections = [
        ("GARMENT", [
            "Blank: 100% cotton 180-220gsm heavyweight tee",
            "Colors: (1) Jet Black   (2) Natural / Cream (#F7F0E3)",
            "Sizes: S / M / L / XL / XXL",
            "Quantity: 50 pcs (mix sizes/colors as agreed)",
        ]),
        ("FRONT PRINT — Left chest", [
            "Artwork: cat-keffiyeh sticker + 'ZALAMEH' text + Arabic زَلَمة below",
            "Print width: 90 mm",
            "Placement: 80 mm below collar, centered horizontally",
            "Colors on black: cream text (#F7F0E3), orange accent (#F39C3E)",
            "Colors on cream: ink text (#1F1B18), red accent (#D32F2F)",
            "Method: DTF or 4-color screen print",
        ]),
        ("BACK PRINT — Full back", [
            "Artwork: Arabic 'خَليكي' large + 'STAY WITH ME' + ZALAMEH hem tag",
            "Print width: 280 mm (edge-to-edge effect, centered)",
            "Placement: 200 mm below collar, centered",
            "Colors on black: cream (#F7F0E3) body + orange (#F39C3E) accent",
            "Colors on cream: ink (#1F1B18) body + red (#D32F2F) accent",
            "Method: DTF recommended for Arabic detail",
        ]),
        ("FILES PROVIDED", [
            "tee-black-front.jpg / tee-black-back.jpg",
            "tee-cream-front.jpg / tee-cream-back.jpg",
            "High-res PNGs available on request (send separately)",
        ]),
        ("NOTES", [
            "Keep Arabic glyphs crisp — no bleed, no distortion",
            "Zalameh approves each batch before shipment",
            "Contact: zalameh.cat@gmail.com · +962 7X XXX XXXX",
        ]),
    ]
    for h, lines in sections:
        d.rectangle([40, y, SW - 40, y + 70], fill=(243, 156, 62))
        d.text((60, y + 8), h, font=fh, fill=(31, 27, 24))
        y += 90
        for line in lines:
            d.text((80, y), "• " + line, font=fp, fill=(31, 27, 24))
            y += 60
        y += 30

    out = "artwork/tee-print-spec.jpg"
    im.save(out, "JPEG", quality=90)
    print("spec:", out)

make_spec_sheet()
