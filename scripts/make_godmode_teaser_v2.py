"""GOD MODE teaser v2 — 30s Zalameh hype reel, new angle.

Different audio (Abd Almajeed drop), different clips, different title/end cards.

Structure (30s total @ 1080x1920 9:16):
  0.0 - 3.0   Title card v2 (red slash on black, bold ZALAMEH + تركب الراب)
  3.0 - 7.0   cat grid
  7.0 - 11.0  znzn2 (from 5s)
  11.0 - 14.0 foxx21 (from 7s)
  14.0 - 18.0 abd2
  18.0 - 21.0 abd4
  21.0 - 25.0 znzn (from 4s)
  25.0 - 28.0 stickers-loop-24s (from 5s)
  28.0 - 30.0 End card v2 (orange CTA)

Audio spine: Abd Almajeed 1:49-2:19 (109-139s).

Outputs: teasers/zalameh-godmode-v2-30s.mp4
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

# ---------- TITLE CARD V2 ----------
# Black background with angled red slash band
title = Image.new("RGB", (W, H), (8, 8, 8))
d = ImageDraw.Draw(title)

# Diagonal red slash across middle
from PIL import ImageChops
slash = Image.new("RGBA", (W * 2, 260), (211, 47, 47, 255))
slash = slash.rotate(-12, expand=True, resample=Image.BICUBIC)
title.paste(slash, ((W - slash.width)//2, (H - slash.height)//2 + 60), slash)

# Big ZALAMEH text on top of slash
f_big = find_font(["impact.ttf", "arialbd.ttf"], 260)
txt = "ZALAMEH"
bb = f_big.getbbox(txt)
tw = bb[2] - bb[0]
d.text(((W - tw)//2 - bb[0], H//2 - 110), txt, font=f_big, fill=(247, 240, 227))

# Arabic بعد الفاصلة
f_ar = find_font(["tradbdo.ttf", "arabtype.ttf", "arialbd.ttf"], 90)
atxt = ar("راب عمّاني")
bb = f_ar.getbbox(atxt)
aw = bb[2] - bb[0]
d.text(((W - aw)//2 - bb[0], H//2 + 210), atxt, font=f_ar, fill=(243, 156, 62))

# Small cat sticker top
cat = Image.open("artwork/stickers/sticker-cat-keffiyeh.png").convert("RGBA")
cat.thumbnail((420, 420), Image.LANCZOS)
title.paste(cat, (W//2 - cat.width//2, 180), cat)

# Bottom label
f_sub = find_function = find_font(["arialbd.ttf"], 40)
sub = "3 SINGLES · OUT NOW"
bb = f_sub.getbbox(sub)
sw = bb[2] - bb[0]
d.text(((W - sw)//2, H - 180), sub, font=f_sub, fill=(200, 200, 200))

title.save("teasers/_title_v2.png")


# ---------- END CARD V2 ----------
end = Image.new("RGB", (W, H), (247, 240, 227))  # cream background
d = ImageDraw.Draw(end)

# Top black band
d.rectangle([0, 0, W, 460], fill=(15, 15, 15))
f_top = find_font(["impact.ttf", "arialbd.ttf"], 140)
top_txt = "ZALAMEH"
bb = f_top.getbbox(top_txt)
tw = bb[2] - bb[0]
d.text(((W - tw)//2 - bb[0], 80), top_txt, font=f_top, fill=(247, 240, 227))

f_top2 = find_font(["arialbd.ttf"], 64)
top_ar = ar("خَليكي · زن زن · عبد المجيد")
bb = f_top2.getbbox(top_ar)
tw = bb[2] - bb[0]
d.text(((W - tw)//2 - bb[0], 240), top_ar, font=f_top2, fill=(243, 156, 62))

# Big central STREAM NOW
f_big = find_font(["impact.ttf", "arialbd.ttf"], 230)
b_txt = "STREAM"
bb = f_big.getbbox(b_txt)
tw = bb[2] - bb[0]
d.text(((W - tw)//2 - bb[0], 640), b_txt, font=f_big, fill=(31, 27, 24))

b_txt2 = "NOW"
bb = f_big.getbbox(b_txt2)
tw = bb[2] - bb[0]
d.text(((W - tw)//2 - bb[0], 870), b_txt2, font=f_big, fill=(211, 47, 47))

# Platforms
f_pl = find_font(["arialbd.ttf"], 54)
pl = "SPOTIFY  ·  APPLE MUSIC  ·  YOUTUBE"
bb = f_pl.getbbox(pl)
pw = bb[2] - bb[0]
d.text(((W - pw)//2, 1200), pl, font=f_pl, fill=(31, 27, 24))

# Handle / URL
f_hand = find_font(["arialbd.ttf"], 60)
hand = "@zalameh.69"
bb = f_hand.getbbox(hand)
hw = bb[2] - bb[0]
d.text(((W - hw)//2, 1400), hand, font=f_hand, fill=(211, 47, 47))

url = "zalameh.netlify.app"
bb = f_hand.getbbox(url)
uw = bb[2] - bb[0]
d.text(((W - uw)//2, 1490), url, font=f_hand, fill=(31, 27, 24))

# Small cat sticker at bottom
cat2 = Image.open("artwork/stickers/sticker-cat-keffiyeh.png").convert("RGBA")
cat2.thumbnail((260, 260), Image.LANCZOS)
end.paste(cat2, (W//2 - cat2.width//2, H - 240 - cat2.height), cat2)

end.save("teasers/_end_v2.png")

print("title v2 + end v2 cards generated")


# ---------- MONTAGE ----------
clips = [
    ("teasers/_title_v2.png",                                0.0, 3.0, "image"),
    ("cat grid.mp4",                                          0.0, 4.0, "video"),
    ("pics for projects/videos for content/znzn2.mp4",        5.0, 4.0, "video"),
    ("pics for projects/videos for content/foxx21.mp4",       7.0, 3.0, "video"),
    ("pics for projects/videos for content/abd2.mp4",         0.0, 4.0, "video"),
    ("pics for projects/videos for content/abd4.mp4",         0.0, 3.0, "video"),
    ("pics for projects/videos for content/znzn.mp4",         4.0, 4.0, "video"),
    ("teasers/stickers-loop-24s.mp4",                         5.0, 3.0, "video"),
    ("teasers/_end_v2.png",                                   0.0, 2.0, "image"),
]

in_args = []
filter_parts = []
concat_inputs = []

for idx, (path, start, dur, kind) in enumerate(clips):
    if kind == "image":
        in_args += ["-loop", "1", "-t", f"{dur}", "-i", path]
    else:
        in_args += ["-ss", f"{start}", "-t", f"{dur}", "-i", path]
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

# Text bands — different from v1
filter_parts.append(
    "[vraw]"
    "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
    "text='AMMAN':fontcolor=0xF7F0E3:fontsize=150:borderw=8:bordercolor=0x000000:"
    "x=(w-text_w)/2:y=180:enable='between(t,3,7)',"

    "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
    "text='ZAN ZAN':fontcolor=0xF7F0E3:fontsize=130:borderw=6:bordercolor=0x000000:"
    "x=(w-text_w)/2:y=h-340:enable='between(t,7,11)',"

    "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
    "text='ABD ALMAJEED':fontcolor=0xF39C3E:fontsize=100:borderw=6:bordercolor=0x000000:"
    "x=(w-text_w)/2:y=h-340:enable='between(t,14,21)',"

    "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
    "text='KHALIKI':fontcolor=0xD32F2F:fontsize=140:borderw=8:bordercolor=0x000000:"
    "x=(w-text_w)/2:y=h-340:enable='between(t,21,25)',"

    "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
    "text='ZALAMEH.NETLIFY.APP':fontcolor=0xFFFFFF:fontsize=50:borderw=4:bordercolor=0x000000:"
    "x=(w-text_w)/2:y=h-140:enable='between(t,25,28)'"
    "[vout]"
)

fc = ";".join(filter_parts)

# Audio: Abd Almajeed 1:49-2:19
audio_in = ["-ss", "109", "-t", "30", "-i", "tracks/abd-almajeed/abd-almajeed.mp3"]
fc += f";[{n}:a]afade=t=in:st=0:d=0.5,afade=t=out:st=28:d=2[aout]"

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
    "teasers/zalameh-godmode-v2-30s.mp4",
]

print(f"\nBuilding v2 montage ({n} clips, Abd Almajeed drop)...")
subprocess.run(cmd, check=True)

size_mb = os.path.getsize("teasers/zalameh-godmode-v2-30s.mp4") / 1024 / 1024
print(f"\nDONE. teasers/zalameh-godmode-v2-30s.mp4  ({size_mb:.1f} MB, 30s, 1080x1920)")
