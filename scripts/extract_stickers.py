"""Extract 5 stickers from sticker.png + build cover/logo stickers.

Strategy per character sticker:
  1. Window to a region containing exactly one sticker
  2. Mask = pixels that are NEITHER cream (bg) NOR near-white (original halo)
     -> isolates ONLY the colored artwork (the figure itself)
  3. Keep largest connected component, fill holes = solid figure silhouette
  4. Dilate silhouette by N px to draw a fresh UNIFORM white die-cut halo
  5. Outside halo = fully transparent. Inside silhouette = original pixels.
     Halo ring = solid white.
"""
import os
import numpy as np
from PIL import Image, ImageOps
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SRC = "sticker.png"
OUT_DIR = "artwork/stickers"
os.makedirs(OUT_DIR, exist_ok=True)

REGIONS = [
    ("sticker-cat-keffiyeh",   (   0,    0, 2048, 1650)),
    ("sticker-cat-dj",         (   0, 1550, 2000, 2800)),
]

CREAM = np.array([247, 240, 227])
HALO_PX = 55          # thickness of the white die-cut outline
INK_PX  = 6           # thin dark edge around the white halo

img = Image.open(SRC).convert("RGBA")
arr = np.array(img)
print(f"image: {arr.shape[1]}x{arr.shape[0]}")


def isolate_figure(region):
    """Return silhouette (figure + artwork bg) with original white halo stripped."""
    rgb = region[..., :3].astype(int)
    cream_dist = np.sqrt(((rgb - CREAM) ** 2).sum(-1))
    # Full non-cream mask INCLUDES the thin white halo ring
    not_cream = cream_dist > 18
    not_cream = ndimage.binary_closing(not_cream, iterations=2)
    # Erode by halo thickness to drop the thin white ring (but keep thick interior
    # regions like stone buildings intact), then dilate back.
    STRIP = 26
    core = ndimage.binary_erosion(not_cream, iterations=STRIP)
    # Keep the biggest colored core — this is "figure + bg art", no halo
    labels, n = ndimage.label(core)
    if n == 0:
        return None
    sizes = ndimage.sum(core, labels, range(1, n + 1))
    biggest = int(np.argmax(sizes)) + 1
    core = labels == biggest
    # Dilate back to restore true silhouette edge (where halo used to sit)
    silhouette = ndimage.binary_dilation(core, iterations=STRIP)
    silhouette = ndimage.binary_fill_holes(silhouette)
    silhouette = ndimage.binary_closing(silhouette, iterations=3)
    return silhouette


def render_diecut(region, silhouette):
    """Return RGBA crop with clean white die-cut halo around silhouette."""
    halo = ndimage.binary_dilation(silhouette, iterations=HALO_PX)
    ink  = ndimage.binary_dilation(halo, iterations=INK_PX)

    H, W = silhouette.shape
    out = np.zeros((H, W, 4), dtype=np.uint8)

    # outer dark edge
    out[ink] = [31, 27, 24, 255]
    # white halo
    out[halo] = [255, 255, 255, 255]
    # original pixels where silhouette — but replace near-cream pixels with white
    # so interior "holes" don't show the tan mat background.
    src_rgb = region[..., :3]
    cream_d = np.sqrt(((src_rgb.astype(int) - CREAM) ** 2).sum(-1))
    ys, xs = np.where(silhouette)
    pix = src_rgb[ys, xs].copy()
    near_cream = cream_d[ys, xs] < 28
    pix[near_cream] = [255, 255, 255]
    out[ys, xs, :3] = pix
    out[ys, xs, 3] = 255

    # Crop to ink bbox with small pad
    ys, xs = np.where(ink)
    pad = 10
    y0 = max(0, ys.min() - pad); y1 = min(H, ys.max() + pad + 1)
    x0 = max(0, xs.min() - pad); x1 = min(W, xs.max() + pad + 1)
    return out[y0:y1, x0:x1]


for name, (x0, y0, x1, y1) in REGIONS:
    region = arr[y0:y1, x0:x1].copy()
    sil = isolate_figure(region)
    if sil is None:
        print(f"{name}: no figure found")
        continue
    # Raw cutout: original sticker (baked white halo preserved), cream -> transparent.
    rgb = region[..., :3].astype(int)
    cream_d = np.sqrt(((rgb - CREAM) ** 2).sum(-1))
    fg = cream_d > 18
    fg = ndimage.binary_closing(fg, iterations=2)
    lbl, nn = ndimage.label(fg)
    if nn > 0:
        sz = ndimage.sum(fg, lbl, range(1, nn + 1))
        keep = lbl == (int(np.argmax(sz)) + 1)
        keep = ndimage.binary_fill_holes(keep)
        raw = region.copy()
        raw[..., 3] = (keep.astype(np.uint8) * 255)
        ys, xs = np.where(keep)
        pad = 20
        y0 = max(0, ys.min() - pad); y1 = min(raw.shape[0], ys.max() + pad + 1)
        x0 = max(0, xs.min() - pad); x1 = min(raw.shape[1], xs.max() + pad + 1)
        cutout = raw[y0:y1, x0:x1]
        cp = os.path.join(OUT_DIR, f"{name}.png")
        Image.fromarray(cutout, "RGBA").save(cp, "PNG", optimize=True)
        print(f"{name}  {cutout.shape[1]}x{cutout.shape[0]}  -> {cp}")


# ---- Cover stickers: square die-cut with uniform white halo + ink edge ----
def make_square_sticker(src_path, out_name, size=1500):
    im = Image.open(src_path).convert("RGB")
    im2 = im.copy()
    im2.thumbnail((size, size), Image.LANCZOS)
    sq = Image.new("RGB", (size, size), tuple(CREAM))
    sq.paste(im2, ((size - im2.width) // 2, (size - im2.height) // 2))
    framed = ImageOps.expand(sq, border=HALO_PX, fill=(255, 255, 255))
    framed = ImageOps.expand(framed, border=INK_PX, fill=(31, 27, 24))
    framed = framed.convert("RGBA")
    out = os.path.join(OUT_DIR, f"{out_name}.png")
    framed.save(out, "PNG", optimize=True)
    print(f"{out_name}  {framed.size[0]}x{framed.size[1]}  -> {out}")


make_square_sticker("artwork/covers/zan-zan-cover-3000.jpg",  "sticker-cover-zan-zan")
make_square_sticker("artwork/covers/zalameh-cover-3000.jpg",  "sticker-cover-abd-almajeed")
make_square_sticker("artwork/covers/cover-walking-3000.jpg",  "sticker-cover-khaliki")


# ---- Cat logo die-cut ----
def make_diecut_from_alpha(src_path, out_name, upscale_to=1600):
    im = Image.open(src_path).convert("RGBA")
    if max(im.size) < upscale_to:
        ratio = upscale_to / max(im.size)
        im = im.resize((int(im.size[0] * ratio), int(im.size[1] * ratio)), Image.LANCZOS)
    a = np.array(im)
    alpha = a[..., 3]
    shape = alpha > 20
    shape = ndimage.binary_fill_holes(shape)
    H, W = shape.shape
    # Canvas with room for halo
    pad = HALO_PX + INK_PX + 20
    canvas_H, canvas_W = H + 2 * pad, W + 2 * pad
    sil = np.zeros((canvas_H, canvas_W), dtype=bool)
    sil[pad:pad + H, pad:pad + W] = shape
    halo = ndimage.binary_dilation(sil, iterations=HALO_PX)
    ink  = ndimage.binary_dilation(halo, iterations=INK_PX)

    out = np.zeros((canvas_H, canvas_W, 4), dtype=np.uint8)
    out[ink] = [31, 27, 24, 255]
    out[halo] = [255, 255, 255, 255]
    ys, xs = np.where(sil)
    # map back to source coords
    src_ys = ys - pad
    src_xs = xs - pad
    out[ys, xs, :3] = a[src_ys, src_xs, :3]
    out[ys, xs, 3] = 255

    # Crop to ink bbox
    ys, xs = np.where(ink)
    y0, y1 = ys.min(), ys.max() + 1
    x0, x1 = xs.min(), xs.max() + 1
    out = out[y0:y1, x0:x1]
    out_path = os.path.join(OUT_DIR, f"{out_name}.png")
    Image.fromarray(out, "RGBA").save(out_path, "PNG", optimize=True)
    print(f"{out_name}  {out.shape[1]}x{out.shape[0]}  -> {out_path}")


print("DONE")
