"""ZAZA GLITCH — unexpected 30s edit using the 4 zaza clips.

Aggressive editing: speed ramps, reverse, invert flashes, split-screen,
freeze frames with text slams, chromatic shake, strobe cuts.
Audio spine: Zan Zan drop (30-60s).

Output: teasers/zaza-glitch-30s.mp4
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

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

Z1 = "pics for projects/videos for content/zaza (1).mp4"
Z2 = "pics for projects/videos for content/zaza (2).mp4"
Z3 = "pics for projects/videos for content/zaza (3).mp4"
Z4 = "pics for projects/videos for content/zaza (4).mp4"

# Opener slam card (black with red ZALAMEH slash)
op = Image.new("RGB", (W, H), (5, 5, 5))
d = ImageDraw.Draw(op)
d.rectangle([0, H//2 - 180, W, H//2 + 180], fill=(211, 47, 47))
f = find_font(["impact.ttf", "arialbd.ttf"], 260)
t = "ZALAMEH"
bb = f.getbbox(t); tw = bb[2]-bb[0]
d.text(((W-tw)//2 - bb[0], H//2 - 140), t, font=f, fill=(247, 240, 227))
op.save("teasers/_glitch_slam.png")

# End slam card
end = Image.new("RGB", (W, H), (5, 5, 5))
d = ImageDraw.Draw(end)
f = find_font(["impact.ttf", "arialbd.ttf"], 340)
t = "OUT"
bb = f.getbbox(t); tw = bb[2]-bb[0]
d.text(((W-tw)//2 - bb[0], 550), t, font=f, fill=(211, 47, 47))
t = "NOW"
bb = f.getbbox(t); tw = bb[2]-bb[0]
d.text(((W-tw)//2 - bb[0], 880), t, font=f, fill=(247, 240, 227))
f2 = find_font(["arialbd.ttf"], 58)
t = "@zalameh.69"
bb = f2.getbbox(t); tw = bb[2]-bb[0]
d.text(((W-tw)//2, 1400), t, font=f2, fill=(243, 156, 62))
end.save("teasers/_glitch_end.png")

print("slam cards generated")


# --- Build the beast ---
# inputs: 0=slam, 1=z1, 2=z2, 3=z3, 4=z4 (reused multiple times via splits),
#         5=end, 6=zanzan audio

# We'll prep a normalized 1080x1920 version for each raw input, then
# build many effect variations from them using splits.

# Normalizer: scale+pad to 1080x1920 with blurred bg, 30fps.
def norm(idx, tag):
    return (
        f"[{idx}:v]split=2[{tag}_bg][{tag}_fg];"
        f"[{tag}_bg]scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,boxblur=30:5,setsar=1[{tag}_bg2];"
        f"[{tag}_fg]scale=1080:1920:force_original_aspect_ratio=decrease,setsar=1[{tag}_fg2];"
        f"[{tag}_bg2][{tag}_fg2]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30,format=yuv420p[{tag}]"
    )

# Effect builders off a normalized stream [tag] -> produce [out]
def clip_from(tag, out, start, dur, effect=None):
    """Trim+seek from normalized source. effect applied after trim."""
    base = f"[{tag}]trim=start={start}:duration={dur},setpts=PTS-STARTPTS"
    if effect == "fast":
        base += ",setpts=0.5*PTS"  # 2x speed
    elif effect == "slow":
        base += ",setpts=1.8*PTS"  # slow-mo
    elif effect == "reverse":
        base += ",reverse"
    elif effect == "invert":
        base += ",negate"
    elif effect == "hue":
        base += ",hue=h=160:s=1.6"
    elif effect == "shake":
        base += ",crop=iw:ih:2*sin(2*t*PI*8):2*cos(2*t*PI*8)"
    elif effect == "zoom":
        base += ",zoompan=z='min(zoom+0.01,1.3)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920"
    elif effect == "strobe":
        base += ",eq=contrast=2:brightness=0.1,curves=all='0/0 0.5/1 1/1'"
    base += f"[{out}]"
    return base

parts = []
# normalize all 4 zaza clips (as inputs 1,2,3,4)
parts.append(norm(1, "z1n"))
parts.append(norm(2, "z2n"))
parts.append(norm(3, "z3n"))
parts.append(norm(4, "z4n"))

# normalize slam image (input 0) and end image (input 5)
parts.append(norm(0, "slamn"))
parts.append(norm(5, "endn"))

# Now create the sequence (30s total)
# We need to split each normalized source as many times as we reference it.
parts.append("[z1n]split=4[z1a][z1b][z1c][z1d]")
parts.append("[z2n]split=3[z2a][z2b][z2c]")
parts.append("[z3n]split=3[z3a][z3b][z3c]")
parts.append("[z4n]split=5[z4a][z4b][z4c][z4d][z4e]")

# ── Sequence build ──
# 00.0-01.0  Slam card (1.0s)
parts.append("[slamn]trim=start=0:duration=1.0,setpts=PTS-STARTPTS[seg01]")

# 01.0-01.3  Invert flash of z1 first 0.3s
parts.append(clip_from("z1a", "seg02", 0, 0.3, "invert"))

# 01.3-04.0  z1 with hue shift (2.7s)
parts.append(clip_from("z1b", "seg03", 0.3, 2.7, "hue"))

# 04.0-04.2  Black flash
parts.append("color=c=black:s=1080x1920:d=0.2:r=30,format=yuv420p[seg04]")

# 04.2-07.0  z2 with zoom pulse (2.8s)
parts.append(clip_from("z2a", "seg05", 0, 2.8, "zoom"))

# 07.0-08.0  Reverse of z3 middle (1s)
parts.append(clip_from("z3a", "seg06", 2.0, 1.0, "reverse"))

# 08.0-10.5  z3 forward with shake (2.5s)
parts.append(clip_from("z3b", "seg07", 0, 2.5, "shake"))

# 10.5-13.0  z4 opening sped up 2x (playing 5s of source in 2.5s)
parts.append(clip_from("z4a", "seg08", 0, 5.0, "fast"))

# 13.0-13.4  invert flash from z2
parts.append(clip_from("z2b", "seg09", 1.0, 0.4, "invert"))

# 13.4-15.0  z1 last 1.6s with strobe contrast
parts.append(clip_from("z1c", "seg10", 3.4, 1.6, "strobe"))

# 15.0-17.0  SPLIT SCREEN: z2 top + z3 bottom (2s)
parts.append(f"[z2c]trim=start=2:duration=2,setpts=PTS-STARTPTS,scale=1080:960,setsar=1[sp_top]")
parts.append(f"[z3c]trim=start=1:duration=2,setpts=PTS-STARTPTS,scale=1080:960,setsar=1[sp_bot]")
parts.append("[sp_top][sp_bot]vstack=inputs=2,setsar=1,format=yuv420p[seg11]")

# 17.0-20.0  z4 slow-mo middle (playing 1.7s at 1.8x = ~3s output)
parts.append(clip_from("z4b", "seg12", 3.0, 1.7, "slow"))

# 20.0-20.3  black flash
parts.append("color=c=black:s=1080x1920:d=0.3:r=30,format=yuv420p[seg13]")

# 20.3-23.0  z4 late section fast (2.7s output, sourcing 5.4s)
parts.append(clip_from("z4c", "seg14", 4.6, 5.4, "fast"))

# 23.0-23.5  inverted z4 tail
parts.append(clip_from("z4d", "seg15", 9.5, 0.5, "invert"))

# 23.5-26.0  z1 opening again but shaken + hue (2.5s)
parts.append(
    "[z1d]trim=start=0:duration=2.5,setpts=PTS-STARTPTS,"
    "hue=h=60:s=1.4,crop=iw:ih:3*sin(2*t*PI*10):3*cos(2*t*PI*10),setsar=1,format=yuv420p[seg16]"
)

# 26.0-28.5  z4e fast tail with punchy contrast (2.5s output from 5s source)
parts.append(
    "[z4e]trim=start=5:duration=5,setpts=PTS-STARTPTS,setpts=0.5*PTS,"
    "eq=contrast=1.8:saturation=1.4,setsar=1,format=yuv420p[seg17]"
)

# 28.5-30.0  End slam card (1.5s)
parts.append("[endn]trim=start=0:duration=1.5,setpts=PTS-STARTPTS[seg18]")

# Concat everything
# Our segments: seg01..seg18 (but z3c and seg17a have conflict — drop seg17a path, use seg17)
seg_labels = [
    "[seg01]", "[seg02]", "[seg03]", "[seg04]", "[seg05]", "[seg06]",
    "[seg07]", "[seg08]", "[seg09]", "[seg10]", "[seg11]", "[seg12]",
    "[seg13]", "[seg14]", "[seg15]", "[seg16]", "[seg17]", "[seg18]"
]
parts.append("".join(seg_labels) + f"concat=n={len(seg_labels)}:v=1:a=0[vraw]")

# Final: apply ZALAMEH/ZAZA text slams with RGB chromatic split vibe
parts.append(
    "[vraw]"
    "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
    "text='ZAN ZAN':fontcolor=0xF39C3E:fontsize=180:borderw=10:bordercolor=0x000000:"
    "x=(w-text_w)/2:y=h-380:enable='between(t,7,12)',"

    "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
    "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=160:borderw=10:bordercolor=0xD32F2F:"
    "x=(w-text_w)/2:y=120:enable='between(t,17,20)',"

    "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
    "text='STREAM NOW':fontcolor=0xF7F0E3:fontsize=110:borderw=6:bordercolor=0xD32F2F:"
    "x=(w-text_w)/2:y=h-260:enable='between(t,23,28)'"
    "[vout]"
)

# Audio (input 6 = zan zan)
parts.append(f"[6:a]afade=t=in:st=0:d=0.4,afade=t=out:st=28.5:d=1.5[aout]")

fc = ";".join(parts)

cmd = [
    "ffmpeg", "-y",
    "-loop", "1", "-t", "1.0", "-i", "teasers/_glitch_slam.png",   # 0
    "-i", Z1,                                                       # 1
    "-i", Z2,                                                       # 2
    "-i", Z3,                                                       # 3
    "-i", Z4,                                                       # 4
    "-loop", "1", "-t", "1.5", "-i", "teasers/_glitch_end.png",     # 5
    "-ss", "30", "-t", "30", "-i", "tracks/zan-zan/zan-zan.mp3",    # 6 audio
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
    "teasers/zaza-glitch-30s.mp4",
]

print("Building ZAZA GLITCH...")
subprocess.run(cmd, check=True)

sz = os.path.getsize("teasers/zaza-glitch-30s.mp4") / 1024 / 1024
print(f"\nDONE. teasers/zaza-glitch-30s.mp4 ({sz:.1f} MB)")
