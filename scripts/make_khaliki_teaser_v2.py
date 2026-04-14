"""
Khaliki teaser v2 — cinematic montage.

Creative direction (distinct from v1 "mixtape crew cards" and from Zan Zan):
  - Full-bleed content video clips with slow cross-dissolves.
  - Letterboxed 2.35:1 cinema bars, warm sepia grade, subtle grain.
  - Arabic title "خليكي" fades in over the last hold.
  - 75 BPM feel → 8 clips @ ~2.5s each with 0.35s crossfade.
"""
import os, subprocess, tempfile, shutil, glob, random
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

DUR_TOTAL = 20.0
W, H = 1080, 1920
FPS = 30
CLIP_DUR = 2.6
XFADE = 0.35
N = 8  # 8 clips: 8*2.6 - 7*0.35 = 20.8 - 2.45 = 18.35s, plus final hold ~1.6s

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
random.seed(11)

PICS = "pics for projects/videos for content"
all_clips = sorted(glob.glob(f"{PICS}/*.mp4"))
random.shuffle(all_clips)
selected = all_clips[:N]
print("selected:")
for s in selected: print(" ", s)

def find_font(names, size):
    fd = r"C:\Windows\Fonts"
    for n in names:
        p = os.path.join(fd, n)
        if os.path.isfile(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

# Build letterbox + title-hold overlay PNG (2.35:1 bars + Arabic title at end)
BAR_H = int((H - W / 2.35) / 2)  # letterbox bar height

tmp = tempfile.mkdtemp(prefix="khaliki2_")
print("tmp:", tmp)

# Warm sepia + letterbox filter
# Each input video: random start offset within clip; scale+crop to 1080x1920; color grade; letterbox bars
prepped = []
for i, src in enumerate(selected):
    # probe duration
    dur = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", src
    ]).strip())
    max_start = max(0.0, dur - CLIP_DUR - 0.1)
    ss = random.uniform(0.0, max_start) if max_start > 0 else 0.0
    out = os.path.join(tmp, f"c{i:02d}.mp4")
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},"
        f"eq=saturation=0.85:contrast=1.08:gamma=0.95,"
        f"colorbalance=rs=0.10:gs=0.02:bs=-0.08:rm=0.05:bm=-0.05,"
        f"drawbox=x=0:y=0:w={W}:h={BAR_H}:color=black:t=fill,"
        f"drawbox=x=0:y={H-BAR_H}:w={W}:h={BAR_H}:color=black:t=fill,"
        f"setsar=1,fps={FPS}"
    )
    subprocess.run([
        "ffmpeg", "-y", "-ss", f"{ss:.2f}", "-t", f"{CLIP_DUR:.3f}",
        "-i", src, "-vf", vf,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-r", str(FPS), "-an", out,
    ], check=True, capture_output=True)
    prepped.append(out)
    print(f"prep {i+1}/{N}")

# Build xfade chain
# Inputs 0..N-1. Output at each step.
cmd = ["ffmpeg", "-y"]
for p in prepped: cmd += ["-i", p]
filt = []
prev = "0:v"
offset = 0.0
for i in range(1, N):
    offset += CLIP_DUR - XFADE
    label = f"v{i}"
    filt.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.3f}[{label}]")
    prev = label
# final fade-out last 0.4s
filt.append(f"[{prev}]fade=t=out:st={DUR_TOTAL-0.5:.3f}:d=0.5[vout]")
cmd += ["-filter_complex", ";".join(filt), "-map", "[vout]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
        "-r", str(FPS), "-t", f"{DUR_TOTAL}",
        "-an", os.path.join(tmp, "video.mp4")]
subprocess.run(cmd, check=True)

# Title overlay PNG — Arabic "خليكي" centered, fades in at ~15s, holds to end
font_ar = find_font(["tradbdo.ttf", "arabtype.ttf", "arialbd.ttf"], 280)
font_lat= find_font(["impact.ttf", "arialbd.ttf"], 90)
font_tag= find_font(["arialbd.ttf"], 46)

title = Image.new("RGBA", (W, H), (0,0,0,0))
td = ImageDraw.Draw(title)
ar_txt = get_display(arabic_reshaper.reshape("خليكي"))
bb = font_ar.getbbox(ar_txt)
tw, th = bb[2]-bb[0], bb[3]-bb[1]
tx = (W - tw)//2; ty = (H - th)//2 - 60
# shadow
td.text((tx+8, ty+8), ar_txt, font=font_ar, fill=(0,0,0,220))
td.text((tx, ty), ar_txt, font=font_ar, fill=(247,240,227,255))
# latin subtitle
sub = "KHALIKI"
bb2 = font_lat.getbbox(sub)
td.text(((W-(bb2[2]-bb2[0]))//2, ty + th + 30), sub, font=font_lat, fill=(211,47,47,255))
tag = "ZALAMEH · NEW SINGLE"
bb3 = font_tag.getbbox(tag)
td.text(((W-(bb3[2]-bb3[0]))//2, ty + th + 150), tag, font=font_tag, fill=(247,240,227,255))
title_path = os.path.join(tmp, "title.png")
title.save(title_path, "PNG")

# Composite title with fade-in at 14s
final = "teasers/khaliki-teaser-reel-v2.mp4"
subprocess.run([
    "ffmpeg", "-y",
    "-i", os.path.join(tmp, "video.mp4"),
    "-loop", "1", "-t", f"{DUR_TOTAL}", "-i", title_path,
    "-ss", "0", "-t", f"{DUR_TOTAL}", "-i", "tracks/khaliki/khaliki.mp3",
    "-filter_complex",
        "[1:v]format=rgba,fade=t=in:st=14:d=1.2:alpha=1[tit];"
        "[0:v][tit]overlay=0:0[vout]",
    "-map", "[vout]", "-map", "2:a:0",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest",
    final,
], check=True)

shutil.rmtree(tmp, ignore_errors=True)
print("SAVED:", final, os.path.getsize(final))
