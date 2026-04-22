"""Generate Zalameh content pillar reference cards + calendar."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
os.makedirs("brand", exist_ok=True)

FONT_DIR = r"C:\Windows\Fonts"

def f(names, size):
    for n in names:
        p = os.path.join(FONT_DIR, n)
        if os.path.isfile(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

# Brand palette
CREAM = (247, 240, 227)
CREAM2 = (238, 228, 210)
INK = (31, 27, 24)
KRED = (211, 47, 47)
SUNSET = (243, 156, 62)
TEAL = (42, 94, 102)

PILLARS = [
    {
        "num": "01",
        "name": "MUSIC",
        "ar": "موسيقى",
        "emoji_icon": "▶",
        "accent": KRED,
        "bg": INK,
        "fg": CREAM,
        "rules": [
            "Singles · teasers · lyrics · studio",
            "Track name always visible",
            "Impact/logo font, RED + CREAM",
            "Audio tag at t=0",
            "9:16 reels · 1:1 covers",
        ],
        "qualifies": [
            "Song teaser",
            "Studio / recording BTS",
            "Lyric video or quote card",
            "Cover art drop",
            "Stream link post",
        ],
        "nope": [
            "Random content reels",
            "Cat memes (those are pillar 2)",
        ],
    },
    {
        "num": "02",
        "name": "CAT UNIVERSE",
        "ar": "الهريرة",
        "emoji_icon": "🐈",
        "accent": SUNSET,
        "bg": CREAM,
        "fg": INK,
        "rules": [
            "Keffiyeh cat is the star",
            "Flat / illustrated / sticker look",
            "CREAM + SUNSET palette",
            "Funny · cheeky · relatable",
            "1:1 grid · 9:16 reels",
        ],
        "qualifies": [
            "Cat sticker posts",
            "Cat comic strip",
            "AI / animated cat loops",
            "Memes with the mascot",
            "New sticker pack drop",
        ],
        "nope": [
            "Music drops (pillar 1)",
            "Anything without the cat",
        ],
    },
    {
        "num": "03",
        "name": "AMMAN",
        "ar": "عمّان",
        "emoji_icon": "▲",
        "accent": TEAL,
        "bg": CREAM2,
        "fg": INK,
        "rules": [
            "Street · stairs · stones · people",
            "Golden hour or grainy night",
            "Warm amber film look",
            "Location tagged always",
            "4:5 or 9:16",
        ],
        "qualifies": [
            "Neighborhood photo (Jabal / Weibdeh)",
            "Food stand / kaak cart / bread oven",
            "Sticker bomb drops on lamp posts",
            "Day-in-life vlog cut",
            "Random Amman moment with mascot",
        ],
        "nope": [
            "Indoor studio shots (pillar 1)",
            "Pure mascot art (pillar 2)",
        ],
    },
]


def make_card(p, path):
    W, H = 1080, 1350  # 4:5 IG post
    img = Image.new("RGB", (W, H), p["bg"])
    d = ImageDraw.Draw(img)
    fg = p["fg"]
    accent = p["accent"]

    # Top band with pillar num + name
    d.rectangle([0, 0, W, 220], fill=accent)
    f_num = f(["impact.ttf", "arialbd.ttf"], 150)
    f_name = f(["impact.ttf", "arialbd.ttf"], 100)
    f_ar = f(["tradbdo.ttf", "arabtype.ttf", "arialbd.ttf"], 60)

    d.text((50, 25), p["num"], font=f_num, fill=p["bg"])
    # Name to right of number
    bb = f_name.getbbox(p["name"])
    nw = bb[2] - bb[0]
    d.text((W - nw - 50 - bb[0], 60), p["name"], font=f_name, fill=p["bg"])

    # Big giant ICON (as text)
    f_icon = f(["impact.ttf", "arialbd.ttf"], 320)
    bb = f_icon.getbbox(p["emoji_icon"])
    iw = bb[2] - bb[0]
    d.text(((W - iw)//2 - bb[0], 260), p["emoji_icon"], font=f_icon, fill=accent)

    # Section: RULES
    f_head = f(["impact.ttf", "arialbd.ttf"], 48)
    f_body = f(["arialbd.ttf"], 32)
    f_body2 = f(["arial.ttf", "arialbd.ttf"], 30)

    y = 650
    d.text((60, y), "VISUAL RULES", font=f_head, fill=accent)
    y += 60
    for r in p["rules"]:
        d.text((80, y), "— " + r, font=f_body, fill=fg)
        y += 40

    # Section: QUALIFIES + NOT
    y += 20
    d.text((60, y), "POST HERE IF…", font=f_head, fill=accent)
    y += 55
    for q in p["qualifies"]:
        d.text((80, y), "+ " + q, font=f_body2, fill=fg)
        y += 36

    y += 15
    d.text((60, y), "SKIP IF…", font=f_head, fill=accent)
    y += 55
    for n in p["nope"]:
        d.text((80, y), "x " + n, font=f_body2, fill=(120, 120, 120))
        y += 36

    # Footer
    f_foot = f(["arialbd.ttf"], 26)
    d.text((60, H - 50), "ZALAMEH · CONTENT PILLAR " + p["num"], font=f_foot, fill=accent)

    img.save(path)
    print(f"  -> {path}")


# Overview grid mockup — shows what the 3x3 IG grid should look like
def make_grid_mock():
    W, H = 1080, 1080  # 1:1
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    pad = 6
    cell = (W - pad * 4) // 3
    # rotation: M C A / C A M / A M C — gives a diagonal-mixed pattern
    pattern = [
        ["M", "C", "A"],
        ["C", "A", "M"],
        ["A", "M", "C"],
    ]
    colors = {"M": (INK, KRED, "MUSIC"), "C": (CREAM, SUNSET, "CAT"), "A": (CREAM2, TEAL, "AMMAN")}
    f_cell = f(["impact.ttf", "arialbd.ttf"], 64)
    for r in range(3):
        for c in range(3):
            key = pattern[r][c]
            bg, acc, label = colors[key]
            x1 = pad + c * (cell + pad)
            y1 = pad + r * (cell + pad)
            x2 = x1 + cell
            y2 = y1 + cell
            d.rectangle([x1, y1, x2, y2], fill=bg)
            # accent bar
            d.rectangle([x1, y2 - 40, x2, y2], fill=acc)
            # label
            bb = f_cell.getbbox(label)
            lw = bb[2] - bb[0]
            fg = CREAM if bg == INK else INK
            d.text((x1 + (cell - lw)//2 - bb[0], y1 + cell//2 - 40), label, font=f_cell, fill=fg)
    img.save("brand/pillar-grid-mock.png")
    print("  -> brand/pillar-grid-mock.png")


for p in PILLARS:
    make_card(p, f"brand/pillar-{p['num']}-{p['name'].lower().split()[0]}.png")
make_grid_mock()
print("\nDONE.")
