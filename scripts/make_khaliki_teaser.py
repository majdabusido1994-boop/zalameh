"""
Khaliki teaser — Reel.

Direction: gang roll-call. 14 UNIQUE animated gang members, each shown ONCE.
No hooded-one repeats between cards. Different colored frame per beat.
Slide transitions (left/up/right/down) cycle for motion. Final title slam.
"""
import os, subprocess, tempfile, shutil, glob, random
from PIL import Image, ImageDraw, ImageFont, ImageOps
import arabic_reshaper
from bidi.algorithm import get_display

DUR_TOTAL = 23.0
W, H = 1080, 1920
FPS = 30
AUDIO_START = 40.0  # song time where teaser audio begins

# Detected beats (sec) inside the 23s window starting at AUDIO_START. ~112 BPM.
BEATS_REL = [0.998, 1.533, 2.067, 2.601, 3.158, 3.692, 4.226, 4.783,
             5.317, 5.851, 6.316, 6.757, 7.291, 7.802, 8.359, 8.893,
             9.451, 9.985, 10.472, 10.937, 11.424, 11.958, 12.492, 13.026,
             13.56, 14.118, 14.652, 15.186, 15.72, 16.277, 16.811, 17.345,
             17.879, 18.46, 19.133, 19.691, 20.225, 20.759, 21.269, 21.827,
             22.384, 22.918]

# 14 gang cards + 2 reveal cards (hooded one, cat) + 1 title.
# Each gang card spans 2 beats; reveal cards span 2 beats each; title fills tail.
CUT_BEATS = [BEATS_REL[i] for i in range(2, 34, 2)]  # 16 cut points → 16 spans

CREAM = (247, 240, 227)
INK = (31, 27, 24)
KRED = (211, 47, 47)
SUNSET = (243, 156, 62)
TERRA = (196, 87, 42)
TEAL = (60, 130, 130)
FRAME_COLORS = [KRED, SUNSET, TERRA, INK, TEAL]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
random.seed(7)

PICS = "pics for projects"
gang = sorted(glob.glob(f"{PICS}/other animated gang members animated/*.png"))
random.shuffle(gang)
gang = gang[:14]
assert len(gang) == 14, f"need 14 gang, got {len(gang)}"
hero_hooded = "website/images/hooded-front.png"
hero_cat    = "website/images/zalameh-cat.png"
roster = list(gang) + [hero_hooded, hero_cat]   # 16 portrait shots

def find_font(names, size):
    fd = r"C:\Windows\Fonts"
    for n in names:
        p = os.path.join(fd, n)
        if os.path.isfile(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

font_num    = find_font(["impact.ttf", "ariblk.ttf", "arialbd.ttf"], 240)
font_label  = find_font(["arialbd.ttf"], 56)
font_small  = find_font(["arialbd.ttf"], 38)
font_ar_big = find_font(["tradbdo.ttf", "arabtype.ttf", "arialbd.ttf"], 320)
font_lat    = find_font(["impact.ttf", "arialbd.ttf"], 110)
font_tag    = find_font(["arialbd.ttf"], 50)

def ar(s):
    return get_display(arabic_reshaper.reshape(s))

def paper_bg(grain=4500):
    bg = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(bg)
    for _ in range(grain):
        x = random.randint(0, W-1); y = random.randint(0, H-1)
        v = random.randint(-9, 4)
        d.point((x, y), fill=(max(0,min(255,CREAM[0]+v)),
                              max(0,min(255,CREAM[1]+v)),
                              max(0,min(255,CREAM[2]+v))))
    return bg

def make_card(portrait_path, idx):
    bg = paper_bg()
    color = FRAME_COLORS[idx % len(FRAME_COLORS)]
    # Prep portrait — flatten, fit
    im = Image.open(portrait_path).convert("RGBA")
    base = Image.new("RGB", im.size, CREAM)
    base.paste(im, mask=im.split()[3] if im.mode=="RGBA" else None)
    im = base
    card_size = 880
    # FIT WITHOUT CROPPING — letterbox onto cream square
    im_fit = im.copy()
    im_fit.thumbnail((card_size, card_size), Image.LANCZOS)
    sq = Image.new("RGB", (card_size, card_size), CREAM)
    sq.paste(im_fit, ((card_size-im_fit.width)//2, (card_size-im_fit.height)//2))
    framed = ImageOps.expand(sq, border=22, fill=color)
    framed = ImageOps.expand(framed, border=8, fill=INK)
    cx, cy = W//2, H//2 + 40
    px, py = cx - framed.width//2, cy - framed.height//2
    bg.paste(framed, (px, py))

    d = ImageDraw.Draw(bg)
    # Big number on top-left of background (overlapping page, not card)
    n = f"{idx+1:02d}"
    d.text((50, 130), n, font=font_num, fill=color)
    # Vertical strip label on right
    d.text((W-260, 200), "GANG", font=font_label, fill=INK)
    d.text((W-260, 260), "#" + n, font=font_label, fill=color)
    # Bottom mixtape strip
    d.rectangle([0, H-130, W, H-50], fill=INK)
    d.text((50, H-115), "ZALAMEH · KHALIKI · TRK 03", font=font_small, fill=CREAM)
    d.text((W-260, H-115), "@zalameh.69", font=font_small, fill=SUNSET)
    return bg

def make_title():
    bg = paper_bg(grain=3000)
    d = ImageDraw.Draw(bg)
    txt = ar("خليكي")
    bb = font_ar_big.getbbox(txt)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    tx = (W - tw)//2; ty = (H - th)//2 - 100
    d.text((tx+10, ty+10), txt, font=font_ar_big, fill=INK)
    d.text((tx, ty), txt, font=font_ar_big, fill=KRED)
    sub = "KHALIKI"
    bb2 = font_lat.getbbox(sub)
    d.text(((W-(bb2[2]-bb2[0]))//2, ty + th + 60), sub, font=font_lat, fill=INK)
    tag = "ZALAMEH · NEW SINGLE · COMING SOON"
    bb3 = font_tag.getbbox(tag)
    d.text(((W-(bb3[2]-bb3[0]))//2, ty + th + 200), tag, font=font_tag, fill=TERRA)
    d.rectangle([0, H-130, W, H-50], fill=INK)
    d.text((50, H-115), "ZALAMEH · TRK 03 · KHALIKI", font=font_small, fill=CREAM)
    d.text((W-260, H-115), "@zalameh.69", font=font_small, fill=SUNSET)
    return bg

tmp = tempfile.mkdtemp(prefix="khaliki_")
print("tmp:", tmp)

# Build per-shot durations from beat positions: card N runs from prev_cut to next_cut.
prev = 0.0
card_durs = []
for cut in CUT_BEATS:
    card_durs.append(cut - prev)
    prev = cut
title_dur = DUR_TOTAL - prev
print("card_durs:", [round(d,3) for d in card_durs], "title:", round(title_dur,3))

clips = []
for i, pth in enumerate(roster):
    img = make_card(pth, i)
    fp = os.path.join(tmp, f"f{i:02d}.png")
    img.save(fp, "PNG")
    out = os.path.join(tmp, f"c{i:02d}.mp4")
    subprocess.run([
        "ffmpeg","-y","-loop","1","-t",f"{card_durs[i]:.4f}","-i",fp,
        "-vf",f"fps={FPS}",
        "-c:v","libx264","-pix_fmt","yuv420p","-preset","veryfast","-r",str(FPS),"-an",out
    ], check=True, capture_output=True)
    clips.append(out)
    print(f"card {i+1}/{len(roster)} ({card_durs[i]:.3f}s)")

img = make_title()
fp = os.path.join(tmp, "title.png")
img.save(fp, "PNG")
out = os.path.join(tmp, "title.mp4")
subprocess.run([
    "ffmpeg","-y","-loop","1","-t",f"{title_dur:.4f}","-i",fp,
    "-vf",f"fps={FPS}",
    "-c:v","libx264","-pix_fmt","yuv420p","-preset","veryfast","-r",str(FPS),"-an",out
], check=True, capture_output=True)
clips.append(out)

# Concat list (hard cuts on beats)
listfile = os.path.join(tmp, "list.txt")
with open(listfile, "w") as f:
    for p in clips: f.write(f"file '{p}'\n")

silent = os.path.join(tmp, "silent.mp4")
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",listfile,"-c","copy",silent],
               check=True, capture_output=True)

out_path = "teasers/khaliki-teaser-reel.mp4"
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
print("SAVED:", "teasers/khaliki-teaser-reel.mp4",
      os.path.getsize("teasers/khaliki-teaser-reel.mp4"))
