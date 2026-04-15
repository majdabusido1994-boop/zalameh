"""Print-ready artwork for the tee shop.

Outputs (artwork/print-ready/):
  pocket-print.png       — cat + ZALAMEH, transparent, 90mm @ 300dpi = 1063px wide
  back-print-on-black.png — big ZALAMEH in cream, for black tees, 280mm = 3307px
  back-print-on-cream.png — big ZALAMEH in ink, for cream tees
  README-print-specs.txt  — measurements, colors, placement
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

OUT = "artwork/print-ready"
os.makedirs(OUT, exist_ok=True)

DPI = 300
def mm2px(mm): return int(round(mm * DPI / 25.4))

CREAM = (247, 240, 227, 255)
INK   = (31, 27, 24, 255)
KRED  = (211, 47, 47, 255)

def find_font(names, size):
    fd = r"C:\Windows\Fonts"
    for n in names:
        p = os.path.join(fd, n)
        if os.path.isfile(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()


# ========== POCKET PRINT ==========
# The front design is TWO separate prints on the pocket area:
#
# (A) cat-peek.png — cat HEAD + TAIL only, printed ABOVE the pocket top edge on
#     the tee body (creates the "cat hiding in pocket" illusion)
# (B) pocket-text.png — "ZALAMEH" in red, printed on the pocket FACE itself

# --- A: cat-peek.png ---
cat_src = Image.open("artwork/stickers/sticker-cat-keffiyeh.png").convert("RGBA")
arr = np.array(cat_src)
alpha = arr[..., 3]
ys, xs = np.where(alpha > 10)
y0, y1 = ys.min(), ys.max()
# Keep top ~48% (head + keffiyeh + upper chest) + bring tail through its full height
head_cut = y0 + int((y1 - y0) * 0.48)
# Tail sits upper-right in the sticker. Keep anything right-of-center above mid-height.
head_region = arr[y0:head_cut, :, :].copy()

# Build peek canvas: pocket width ~90mm, but cat prints ABOVE the pocket
peek_w = mm2px(90)
peek_scale = peek_w / arr.shape[1]
cat_trim = Image.fromarray(head_region, "RGBA")
cat_trim = cat_trim.resize(
    (peek_w, int(head_region.shape[0] * peek_scale)), Image.LANCZOS
)
peek_canvas = Image.new("RGBA", cat_trim.size, (0, 0, 0, 0))
peek_canvas.paste(cat_trim, (0, 0), cat_trim)
peek_canvas.save(f"{OUT}/cat-peek.png", "PNG", optimize=True)
print(f"cat-peek.png  {peek_canvas.size[0]}x{peek_canvas.size[1]}px (prints ABOVE pocket top edge)")

# --- B: pocket-text.png ---
# Text sized to fit a standard patch pocket face (~100-110mm wide, ~120mm tall)
text_w = mm2px(90)
text_h = mm2px(30)
text_canvas = Image.new("RGBA", (text_w, text_h), (0, 0, 0, 0))
# Size font to fill width
lo, hi = 80, 500
best = None
while lo <= hi:
    mid = (lo + hi) // 2
    f = find_font(["impact.ttf", "arialbd.ttf"], mid)
    bb = f.getbbox("ZALAMEH")
    if bb[2] - bb[0] < text_w - 40:
        best = (mid, f, bb); lo = mid + 1
    else:
        hi = mid - 1
fsize, font_zal, bb = best
tw = bb[2] - bb[0]; th = bb[3] - bb[1]
d = ImageDraw.Draw(text_canvas)
d.text(((text_w - tw) // 2 - bb[0], (text_h - th) // 2 - bb[1]),
       "ZALAMEH", font=font_zal, fill=KRED)
text_canvas.save(f"{OUT}/pocket-text.png", "PNG", optimize=True)
print(f"pocket-text.png  {text_canvas.size[0]}x{text_canvas.size[1]}px (prints on pocket face)")


# ========== BACK PRINT ==========
back_w = mm2px(280)           # ~3307
back_h = mm2px(80)            # ~945 tall for ZALAMEH letterform

def make_back(fill_color, out_name):
    im = Image.new("RGBA", (back_w, back_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Fit ZALAMEH to nearly full width
    # Binary search font size
    lo, hi = 200, 2000
    best = None
    while lo <= hi:
        mid = (lo + hi) // 2
        f = find_font(["impact.ttf","arialbd.ttf"], mid)
        bb = f.getbbox("ZALAMEH")
        w = bb[2] - bb[0]
        if w < back_w - 80:
            best = (mid, f, bb); lo = mid + 1
        else:
            hi = mid - 1
    size, f, bb = best
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    x = (back_w - tw) // 2 - bb[0]
    y = (back_h - th) // 2 - bb[1]
    d.text((x, y), "ZALAMEH", font=f, fill=fill_color)
    im.save(f"{OUT}/{out_name}", "PNG", optimize=True)
    print(f"{out_name}  {im.size[0]}x{im.size[1]}px (~280mm wide @ 300dpi, font {size}pt)")

make_back(CREAM, "back-print-on-black.png")
make_back(INK,   "back-print-on-cream.png")


# ========== SPEC SHEET ==========
spec = f"""ZALAMEH — TEE PRINT SPECS
=========================

QUANTITY: 50 pcs total (mix sizes/colors as agreed)
SIZES: S / M / L / XL / XXL
COLORS: (1) Jet Black  (2) Natural / Cream (#F7F0E3)
BLANK: 100% cotton heavyweight tee, 180–220 gsm, with a LEFT-CHEST PATCH POCKET

--- FRONT PRINT (two separate prints — creates "cat in pocket" illusion) ---
The front uses TWO files printed in different spots:

(A) cat-peek.png
    Prints on the TEE FABRIC, just ABOVE the pocket top edge.
    Only the cat's head + keffiyeh show above the pocket — looks like
    the cat is sitting inside the pocket peeking out.
    Print width: 90 mm  (matches pocket width)
    Placement: bottom of this artwork aligns with the TOP EDGE of the pocket,
               centered horizontally over the pocket.

(B) pocket-text.png
    Prints on the POCKET FACE itself.
    "ZALAMEH" in red (#D32F2F).
    Print width: 90 mm, height ~30 mm
    Placement: centered on the pocket face, roughly vertically centered.

Method for both: DTF recommended (handles cat detail + red text cleanly).

--- BACK PRINT (upper back, full width) ---
Files:  back-print-on-black.png   — use for BLACK tees (cream ink)
        back-print-on-cream.png   — use for CREAM tees (black ink)
Print width: 280 mm  (file is at 300 DPI, 3307 px wide)
Placement: 200 mm (20 cm) below collar center, horizontally centered
Method: DTF or screen print
Single color per tee — no gradients, no outline

--- COLOR CODES ---
Cream / Natural: #F7F0E3
Ink / Black:     #1F1B18  (or pure black 000000 is fine)
Red:             #D32F2F  (pocket text)

--- NOTES ---
- Please wash the first sample and send photos before printing the full 50
- Keep the cat artwork crisp — no distortion from stretch or bleed
- Bag + tag each tee for shipping
- Contact: zalameh.cat@gmail.com  ·  @zalameh.69

Delivered files:
  cat-peek.png             (front — prints ABOVE pocket, same for both colors)
  pocket-text.png          (front — prints ON pocket face, same for both colors)
  back-print-on-black.png  (for black tees)
  back-print-on-cream.png  (for cream tees)
"""

with open(f"{OUT}/README-print-specs.txt", "w", encoding="utf-8") as f:
    f.write(spec)

print(f"\nAll files saved to: {OUT}/")
print("  cat-peek.png")
print("  pocket-text.png")
print("  back-print-on-black.png")
print("  back-print-on-cream.png")
print("  README-print-specs.txt")
