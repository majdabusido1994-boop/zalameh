"""Compose all sticker artwork into a single reference collage for Higgsfield."""
import os, random
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

W, H = 1080, 1920
CREAM = (247, 240, 227)
INK = (31, 27, 24)
KRED = (211, 47, 47)
SUNSET = (243, 156, 62)
TERRA = (196, 87, 42)

random.seed(3)

def find_font(names, size):
    fd = r"C:\Windows\Fonts"
    for n in names:
        p = os.path.join(fd, n)
        if os.path.isfile(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

font_title = find_font(["impact.ttf","arialbd.ttf"], 110)
font_ar    = find_font(["tradbdo.ttf","arabtype.ttf","arialbd.ttf"], 90)
font_small = find_font(["arialbd.ttf"], 30)
font_tag   = find_font(["impact.ttf","arialbd.ttf"], 42)

def ar(s): return get_display(arabic_reshaper.reshape(s))

# Paper background with grain
bg = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(bg)
for _ in range(9000):
    x = random.randint(0,W-1); y = random.randint(0,H-1)
    v = random.randint(-10,4)
    d.point((x,y), fill=(max(0,min(255,CREAM[0]+v)),
                          max(0,min(255,CREAM[1]+v)),
                          max(0,min(255,CREAM[2]+v))))

# Diagonal keffiyeh accent stripes top corners
for i in range(30):
    c = KRED if i % 2 == 0 else INK
    d.line([(0, 60+i*8), (300 - i*10, 0)], fill=c, width=3)
    d.line([(W, 60+i*8), (W - 300 + i*10, 0)], fill=c, width=3)

# Title bar at top
d.rectangle([0, 90, W, 240], fill=INK)
d.text((40, 100), "ZALAMEH", font=font_title, fill=CREAM)
d.text((40, 200), "· THE COLLECTION · cassette era", font=font_small, fill=SUNSET)
ar_txt = ar("زَلَمة")
bb = font_ar.getbbox(ar_txt)
d.text((W - (bb[2]-bb[0]) - 40, 110), ar_txt, font=font_ar, fill=KRED)

STICK_DIR = "artwork/stickers"

def place(sticker_name, cx, cy, max_w, max_h, angle=0):
    p = os.path.join(STICK_DIR, sticker_name)
    im = Image.open(p).convert("RGBA")
    im.thumbnail((max_w, max_h), Image.LANCZOS)
    if angle != 0:
        im = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    bg.paste(im, (cx - im.width//2, cy - im.height//2), im)

# Layout tuned for 1080x1920 portrait
place("sticker-cat-keffiyeh.png", W//2, 620, 720, 720, angle=-4)
place("sticker-cat-dj.png",       W//2, 1150, 980, 720, angle=3)

# Bottom row: 3 covers
cover_size = 340
base_y = 1620
places = [
    ("sticker-cover-zan-zan.png",      220,     base_y, -6),
    ("sticker-cover-abd-almajeed.png", W//2,    base_y,  2),
    ("sticker-cover-khaliki.png",      W-220,   base_y, -3),
]
for fn, cx, cy, ang in places:
    place(fn, cx, cy, cover_size, cover_size, angle=ang)

# Bottom strip
d.rectangle([0, H-100, W, H-30], fill=INK)
d.text((40, H-88), "zalameh.netlify.app · @zalameh.69", font=font_small, fill=CREAM)
tag = "CASSETTE-CORE · AMMAN"
bb = font_tag.getbbox(tag)
d.text((W - (bb[2]-bb[0]) - 40, H-90), tag, font=font_tag, fill=SUNSET)

# Little red stamp in corner
d.rectangle([W-230, 280, W-40, 340], outline=KRED, width=5)
d.text((W-220, 290), "NEW DROP '26", font=font_small, fill=KRED)

out = "artwork/sticker-collage-reference-9x16.jpg"
bg.save(out, "JPEG", quality=92)
print("SAVED:", out, os.path.getsize(out))
