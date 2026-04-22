"""GOD MODE teaser — 30s Zalameh hype reel.

Structure (30s total @ 1080x1920 9:16):
  0.0 - 3.0   Title card (cat sticker flies in, ZALAMEH text bursts)
  3.0 - 7.0   stickers-animation loop (4s)
  7.0 - 11.0  znzn with "خَليكي" text band
  11.0 - 14.0 foxx (blue beetle, 3s punch)
  14.0 - 18.0 abd with "عبد المجيد" text band
  18.0 - 21.0 majeed (3s)
  21.0 - 25.0 abd3 (rapid)
  25.0 - 28.0 tshirt demo with "MERCH OUT" text
  28.0 - 30.0 End card (CTA: STREAM NOW)

Audio spine: Khaliki 40-70s (30s drop section).

Outputs: teasers/zalameh-godmode-30s.mp4
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

W, H = 1080, 1920
FONT_DIR = r"C:\Windows\Fonts"

def find_font(names, size):
    for n in names:
        p = os.path.join(FONT_DIR, n)
        if os.path.isfile(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def ar(s): return get_display(arabic_reshaper.reshape(s))

# ---------- TITLE CARD ----------
title = Image.new("RGB", (W, H), (10, 10, 10))
d = ImageDraw.Draw(title)

# Soft radial-ish glow behind cat
for i, a in enumerate(range(30, 0, -3)):
    d.ellipse([W//2-300-i*8, H//2-150-i*8, W//2+300+i*8, H//2+150+i*8], fill=(a, a*0, a//2))

# Cat sticker
cat = Image.open("artwork/stickers/sticker-cat-keffiyeh.png").convert("RGBA")
cat.thumbnail((720, 720), Image.LANCZOS)
cat_y = H//2 - cat.height//2 - 160
title.paste(cat, (W//2 - cat.width//2, cat_y), cat)

# Big ZALAMEH below
f_big = find_font(["impact.ttf", "arialbd.ttf"], 220)
txt = "ZALAMEH"
bb = f_big.getbbox(txt)
tw = bb[2] - bb[0]
d.text(((W - tw)//2 - bb[0], cat_y + cat.height + 30), txt,
       font=f_big, fill=(247, 240, 227))

# Arabic زَلَمة
f_ar = find_font(["tradbdo.ttf", "arabtype.ttf", "arialbd.ttf"], 120)
atxt = ar("زَلَمة")
bb = f_ar.getbbox(atxt)
aw = bb[2] - bb[0]
d.text(((W - aw)//2 - bb[0], cat_y + cat.height + 30 + 250), atxt,
       font=f_ar, fill=(243, 156, 62))

# Subtitle
f_sub = find_font(["arialbd.ttf"], 46)
sub = "عمّان  ·  AMMAN"
bb = f_sub.getbbox(sub)
sw = bb[2] - bb[0]
d.text(((W - sw)//2, H - 220), sub, font=f_sub, fill=(200, 200, 200))

title.save("teasers/_title.png")


# ---------- END CARD ----------
end = Image.new("RGB", (W, H), (10, 10, 10))
d = ImageDraw.Draw(end)

# Red "OUT NOW" slash bar top
d.rectangle([0, 280, W, 560], fill=(211, 47, 47))
f_out = find_font(["impact.ttf", "arialbd.ttf"], 200)
out_txt = "OUT NOW"
bb = f_out.getbbox(out_txt)
tw = bb[2] - bb[0]
d.text(((W - tw)//2 - bb[0], 310), out_txt, font=f_out, fill=(247, 240, 227))

# 3 singles list
f_tr = find_font(["impact.ttf", "arialbd.ttf"], 110)
tracks = ["KHALIKI", "ZAN ZAN", "ABD ALMAJEED"]
y = 720
for t in tracks:
    bb = f_tr.getbbox(t)
    tw = bb[2] - bb[0]
    d.text(((W - tw)//2 - bb[0], y), t, font=f_tr, fill=(247, 240, 227))
    y += 130

# CTA
f_cta = find_font(["arialbd.ttf"], 60)
cta = "STREAM EVERYWHERE"
bb = f_cta.getbbox(cta)
cw = bb[2] - bb[0]
d.text(((W - cw)//2, y + 60), cta, font=f_cta, fill=(243, 156, 62))

# Handle
f_hand = find_font(["arialbd.ttf"], 52)
hand = "@zalameh.69  ·  zalameh.netlify.app"
bb = f_hand.getbbox(hand)
hw = bb[2] - bb[0]
d.text(((W - hw)//2, H - 260), hand, font=f_hand, fill=(200, 200, 200))

# Small cat bottom-right
cat2 = Image.open("artwork/stickers/sticker-cat-keffiyeh.png").convert("RGBA")
cat2.thumbnail((220, 220), Image.LANCZOS)
end.paste(cat2, (W//2 - cat2.width//2, H - 180 - cat2.height), cat2)

end.save("teasers/_end.png")

print("title + end cards generated")


# ---------- BUILD THE MONTAGE ----------
# Clip plan: (file, start_offset, duration)
clips = [
    ("teasers/_title.png",                                  0.0, 3.0,  "image"),
    ("teasers/stickers-animation.mp4",                      0.0, 4.0,  "video"),
    ("pics for projects/videos for content/znzn.mp4",       0.0, 4.0,  "video"),
    ("pics for projects/videos for content/foxx.mp4",       0.0, 3.0,  "video"),
    ("pics for projects/videos for content/abd.mp4",        0.0, 4.0,  "video"),
    ("pics for projects/videos for content/majeed.mp4",     0.0, 3.0,  "video"),
    ("pics for projects/videos for content/abd3.mp4",       0.0, 4.0,  "video"),
    ("tshirt/tshirt demo vid.mp4",                          0.0, 3.0,  "video"),
    ("teasers/_end.png",                                    0.0, 2.0,  "image"),
]

# Build input args + filter chain
in_args = []
filter_parts = []
concat_inputs = []

for idx, (path, start, dur, kind) in enumerate(clips):
    if kind == "image":
        in_args += ["-loop", "1", "-t", f"{dur}", "-i", path]
    else:
        in_args += ["-ss", f"{start}", "-t", f"{dur}", "-i", path]
    # Normalize to 1080x1920 with blurred background fill
    filter_parts.append(
        f"[{idx}:v]split=2[{idx}bg][{idx}fg];"
        f"[{idx}bg]scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,boxblur=30:5,setsar=1[{idx}bg2];"
        f"[{idx}fg]scale=1080:1920:force_original_aspect_ratio=decrease,setsar=1[{idx}fg2];"
        f"[{idx}bg2][{idx}fg2]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30[v{idx}]"
    )
    concat_inputs.append(f"[v{idx}]")

n = len(clips)
filter_parts.append(
    "".join(concat_inputs) + f"concat=n={n}:v=1:a=0[vraw]"
)
# Add drawtext overlays on top of concat output at specific timestamps
# timing:
# title card 0-3, KHALIKI text band appears 7-11 (during znzn),
# ABD ALMAJEED band 14-18 (during abd), MERCH OUT band 25-28 (tshirt)
filter_parts.append(
    "[vraw]drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
    "text='KHALIKI':fontcolor=0xF7F0E3:fontsize=120:borderw=6:bordercolor=0x000000:"
    "x=(w-text_w)/2:y=h-340:enable='between(t,7,11)',"
    "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
    "text='ABD ALMAJEED':fontcolor=0xF7F0E3:fontsize=100:borderw=6:bordercolor=0x000000:"
    "x=(w-text_w)/2:y=h-340:enable='between(t,14,18)',"
    "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
    "text='ZAN ZAN':fontcolor=0xF7F0E3:fontsize=120:borderw=6:bordercolor=0x000000:"
    "x=(w-text_w)/2:y=h-340:enable='between(t,18,21)',"
    "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
    "text='MERCH OUT':fontcolor=0xD32F2F:fontsize=130:borderw=8:bordercolor=0x000000:"
    "x=(w-text_w)/2:y=h-340:enable='between(t,25,28)'[vout]"
)

fc = ";".join(filter_parts)

# Audio: khaliki 40-70s with fade-in/out at edges
audio_in = ["-ss", "40", "-t", "30", "-i", "tracks/khaliki/khaliki.mp3"]
audio_filter = "[{}:a]afade=t=in:st=0:d=0.6,afade=t=out:st=28:d=2,volume=1.0[aout]".format(n)
fc = fc + ";" + audio_filter

cmd = [
    "ffmpeg", "-y",
    *in_args,
    *audio_in,
    "-filter_complex", fc,
    "-map", "[vout]",
    "-map", "[aout]",
    "-t", "30",
    "-r", "30",
    "-c:v", "libx264", "-pix_fmt", "yuv420p",
    "-preset", "medium", "-crf", "19",
    "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart",
    "-shortest",
    "teasers/zalameh-godmode-30s.mp4",
]

print(f"\nBuilding {n}-clip montage...")
subprocess.run(cmd, check=True)

size_mb = os.path.getsize("teasers/zalameh-godmode-30s.mp4") / 1024 / 1024
print(f"\nDONE. teasers/zalameh-godmode-30s.mp4  ({size_mb:.1f} MB, 30s, 1080x1920)")
