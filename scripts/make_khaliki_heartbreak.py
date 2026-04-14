"""
Khaliki teaser — HEARTBREAK cut.

Concept:
  Slow, cool, lonely. Only Zalameh + the Hooded One.
  Story arc: together → cat looks away → hooded alone → empty frame
  → title slam "خليكي / stay with me 💔".

  Treatment differs from the gang roll-call: full-bleed cinematic,
  cool-blue grade, dark vignette, SLOW Ken Burns zoom on every
  shot (no static cards), film grain, letterbox cinema bars.

  Beat-synced cuts at ~112 BPM, every 2 beats, 23s total. Audio: 0:40-1:03.
"""
import os, subprocess, tempfile, shutil, glob, random
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

DUR_TOTAL = 23.0
W, H = 1080, 1920
FPS = 30
AUDIO_START = 40.0

# ~112 BPM detected. Cut every 2 beats.
BEATS_REL = [0.998, 1.533, 2.067, 2.601, 3.158, 3.692, 4.226, 4.783,
             5.317, 5.851, 6.316, 6.757, 7.291, 7.802, 8.359, 8.893,
             9.451, 9.985, 10.472, 10.937, 11.424, 11.958, 12.492, 13.026,
             13.56, 14.118, 14.652, 15.186, 15.72, 16.277, 16.811, 17.345,
             17.879, 18.46, 19.133, 19.691, 20.225, 20.759, 21.269, 21.827,
             22.384, 22.918]

# 16 photo shots + 1 title. Each photo spans 2 beats (~1.07s).
CUT_BEATS = [BEATS_REL[i] for i in range(2, 34, 2)]  # 16 cut points

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
random.seed(99)

# Hand-picked story arc — only hooded man + cat. No gang.
PROFILE = "pics for projects/zalameh and hooded man profile pics"
profile_pool = sorted(glob.glob(f"{PROFILE}/hf_*.png"))
random.shuffle(profile_pool)
extras = profile_pool[:8]  # 8 random profile shots to weave in

# Story arc (16 shots): together → cat alone → hooded alone → empty
shots = [
    # Together (4) — they had something
    ("artwork/covers/zalameh-cover-3000.jpg",         "in",  1.0),
    ("artwork/covers/cover-walking-3000.jpg",         "in",  1.0),
    ("website/images/hero-duo.jpg",                    "in",  1.0),
    ("artwork/covers/zan-zan-cover-3000.jpg",         "in",  1.0),
    # Cat starts to drift (3) — looks away, walks
    ("website/images/zalameh-cat.png",                "in",  1.05),
    ("website/images/zalameh-cat.png",                "out", 1.10),  # zoom out as if pulling away
    (extras[0],                                        "in",  1.0),
    # Hooded alone (4) — empty pockets, walking, cold
    ("website/images/hooded-front.png",               "out", 1.05),
    ("website/images/hooded-walking.png",             "in",  1.05),
    (extras[1],                                        "in",  1.0),
    (extras[2],                                        "out", 1.0),
    # Memory flashes (3) — fragments
    (extras[3],                                        "in",  1.0),
    ("artwork/covers/zalameh-cover-3000.jpg",         "out", 1.10),  # zoom out = leaving
    (extras[4],                                        "in",  1.0),
    # Final two — hooded standing alone
    ("website/images/hooded-front.png",               "in",  1.05),
    ("website/images/hooded-walking.png",             "out", 1.10),
]
assert len(shots) == 16

def find_font(names, size):
    fd = r"C:\Windows\Fonts"
    for n in names:
        p = os.path.join(fd, n)
        if os.path.isfile(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

font_ar_big = find_font(["tradbdo.ttf", "arabtype.ttf", "arialbd.ttf"], 320)
font_lat    = find_font(["impact.ttf", "arialbd.ttf"], 100)
font_tag    = find_font(["arialbd.ttf"], 50)
font_small  = find_font(["arialbd.ttf"], 36)

CREAM = (247, 240, 227)
INK = (15, 18, 28)        # darker for heartbreak
NIGHT = (12, 18, 38)
DEEP = (24, 32, 60)

def ar(s):
    return get_display(arabic_reshaper.reshape(s))

def make_title():
    bg = Image.new("RGB", (W, H), NIGHT)
    d = ImageDraw.Draw(bg)
    # subtle starfield grain
    for _ in range(3500):
        x = random.randint(0, W-1); y = random.randint(0, H-1)
        v = random.randint(-6, 18)
        c = (max(0,min(255, NIGHT[0]+v)),
             max(0,min(255, NIGHT[1]+v)),
             max(0,min(255, NIGHT[2]+v + 6)))
        d.point((x,y), fill=c)
    txt = ar("خليكي")
    bb = font_ar_big.getbbox(txt)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    tx = (W - tw)//2; ty = (H - th)//2 - 100
    d.text((tx+10, ty+10), txt, font=font_ar_big, fill=(0,0,0))
    d.text((tx, ty), txt, font=font_ar_big, fill=(247, 240, 227))
    sub = "stay with me"
    bb2 = font_lat.getbbox(sub)
    d.text(((W-(bb2[2]-bb2[0]))//2, ty + th + 60), sub, font=font_lat, fill=(211,47,47))
    tag = "ZALAMEH · KHALIKI · COMING SOON"
    bb3 = font_tag.getbbox(tag)
    d.text(((W-(bb3[2]-bb3[0]))//2, ty + th + 200), tag, font=font_tag, fill=(196,87,42))
    # bottom info
    d.rectangle([0, H-110, W, H-40], fill=(0,0,0))
    d.text((50, H-95), "ZALAMEH · KHALIKI", font=font_small, fill=(247,240,227))
    d.text((W-260, H-95), "@zalameh.69", font=font_small, fill=(243,156,62))
    return bg

# Per-shot durations from beat positions
prev = 0.0
durs = []
for cut in CUT_BEATS:
    durs.append(cut - prev)
    prev = cut
title_dur = DUR_TOTAL - prev
print("durs:", [round(d,3) for d in durs], "title:", round(title_dur,3))

tmp = tempfile.mkdtemp(prefix="khb_")
print("tmp:", tmp)
parts = []

# Cool-blue grade + cinema bars + slow Ken Burns + grain
BAR_H = 90  # subtle cinema bars top/bottom
GRADE = "eq=saturation=0.55:contrast=1.08:gamma=0.92,colorbalance=rs=-0.08:gs=-0.03:bs=0.18:rm=-0.05:bm=0.10"
GRAIN = "noise=alls=8:allf=t"
VIGN  = "vignette=PI/4"

for i, (src, direction, zoom_factor) in enumerate(shots):
    out = os.path.join(tmp, f"s{i:02d}.mp4")
    d = durs[i]
    frames = max(2, int(round(d * FPS)))
    if direction == "in":
        z_expr = f"zoom+0.0008*on"  # 0.0008 per frame; over 30 frames = 0.024 zoom-in
        z_init = "1.02"
    else:
        z_expr = f"zoom-0.0008*on"
        z_init = "1.18"

    # zoompan needs an image. We pre-scale with PIL to a square 1920x1920 cream-bg canvas
    # so the cat sticker doesn't sit on a transparent void.
    src_img = Image.open(src).convert("RGBA")
    canvas = Image.new("RGB", (max(src_img.width, src_img.height), max(src_img.width, src_img.height)), CREAM)
    cx = (canvas.width - src_img.width)//2
    cy = (canvas.height - src_img.height)//2
    canvas.paste(src_img, (cx, cy), src_img if src_img.mode == "RGBA" else None)
    prep = os.path.join(tmp, f"prep_{i:02d}.png")
    canvas.save(prep)

    vf = (
        f"scale=2160:-1:flags=lanczos,"
        f"zoompan=z='if(eq(on\\,0)\\,{z_init}\\,{z_expr})':d={frames}:s={W}x{H}:fps={FPS},"
        f"{GRADE},"
        f"{GRAIN},"
        f"{VIGN},"
        f"drawbox=x=0:y=0:w={W}:h={BAR_H}:color=black:t=fill,"
        f"drawbox=x=0:y={H-BAR_H}:w={W}:h={BAR_H}:color=black:t=fill,"
        f"setsar=1"
    )
    subprocess.run([
        "ffmpeg","-y","-loop","1","-t",f"{d:.4f}","-i",prep,
        "-vf", vf,
        "-c:v","libx264","-pix_fmt","yuv420p","-preset","veryfast","-r",str(FPS),"-an",out
    ], check=True, capture_output=True)
    parts.append(out)
    print(f"shot {i+1}/16  dir={direction}  dur={d:.3f}")

# Title (no Ken Burns, just hold + slight glow handled visually by the design)
title_img = make_title()
fp = os.path.join(tmp, "title.png")
title_img.save(fp, "PNG")
out = os.path.join(tmp, "title.mp4")
subprocess.run([
    "ffmpeg","-y","-loop","1","-t",f"{title_dur:.4f}","-i",fp,
    "-vf", f"fps={FPS},fade=t=in:st=0:d=0.4",
    "-c:v","libx264","-pix_fmt","yuv420p","-preset","veryfast","-r",str(FPS),"-an",out
], check=True, capture_output=True)
parts.append(out)

# Concat
listfile = os.path.join(tmp, "list.txt")
with open(listfile, "w") as f:
    for p in parts: f.write(f"file '{p}'\n")
silent = os.path.join(tmp, "silent.mp4")
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",listfile,"-c","copy",silent],
               check=True, capture_output=True)

out_path = "teasers/khaliki-teaser-heartbreak.mp4"
subprocess.run([
    "ffmpeg","-y",
    "-i", silent,
    "-ss", str(AUDIO_START), "-t", f"{DUR_TOTAL}", "-i", "tracks/khaliki/khaliki.mp3",
    "-map","0:v:0","-map","1:a:0",
    "-c:v","libx264","-pix_fmt","yuv420p","-preset","medium","-crf","20",
    "-c:a","aac","-b:a","192k","-movflags","+faststart","-shortest",
    out_path,
], check=True)

shutil.rmtree(tmp, ignore_errors=True)
print("SAVED:", out_path, os.path.getsize(out_path))
