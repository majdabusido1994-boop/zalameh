"""
Build a 20s Instagram Reel teaser for Zan Zan.
- 1080x1920 @ 30fps
- Cuts on every beat @ 140 BPM (0.4286s per shot, ~47 shots)
- Cycles through Zalameh artwork + Amman clips
- Audio: first 20s of zan-zan.mp3
"""
import os, subprocess, tempfile, shutil

BPM = 140
DUR_TOTAL = 20.0
BEAT = 60.0 / BPM           # 0.4286s
NUM_SHOTS = int(round(DUR_TOTAL / BEAT))   # 47
SHOT_DUR = DUR_TOTAL / NUM_SHOTS            # 0.4255s
W, H = 1080, 1920
FPS = 30
CREAM = "0xE3F0F7"  # ffmpeg uses 0xBBGGRR? actually 0xRRGGBB — so 247,240,227 -> F7F0E3
CREAM = "0xF7F0E3"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# Images only — strict mathematical flicker.
# Odd beats = prison-bars anchor. Even beats cycle through variants.
anchor = "artwork/covers/zan-zan-cover-3000-bars.jpg"
variants = [
    "artwork/covers/zan-zan-cover-3000.jpg",    # same cover, bars off → flicker
    "artwork/covers/cover-walking-3000.jpg",    # back view
    "artwork/covers/zalameh-cover-3000.jpg",    # walking duo
    "website/images/hooded-front.png",          # front view
    "website/images/zalameh-cat.png",           # cat face
    "website/images/hero-duo.jpg",              # rooftop
    "artwork/social/missing-zalameh-story.jpg", # flyer
    "artwork/brand/zalameh-logo-master.png",    # logo
    "website/images/hooded-walking.png",        # walking alt
]

shot_list = []
vi = 0
for i in range(NUM_SHOTS):
    if i % 2 == 0:
        shot_list.append(("img", anchor))
    else:
        shot_list.append(("img", variants[vi % len(variants)]))
        vi += 1

tmp = tempfile.mkdtemp(prefix="zanzan_")
print("temp:", tmp)

vf_img = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS}"
vf_vid = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS}"

parts = []
for idx, shot in enumerate(shot_list):
    out = os.path.join(tmp, f"s{idx:03d}.mp4")
    if shot[0] == "img":
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-t", f"{SHOT_DUR:.4f}",
            "-i", shot[1],
            "-vf", vf_img,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
            "-r", str(FPS), "-an", out,
        ]
    else:
        _, path, ss = shot
        cmd = [
            "ffmpeg", "-y", "-ss", f"{ss:.2f}", "-t", f"{SHOT_DUR:.4f}",
            "-i", path,
            "-vf", vf_vid,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
            "-r", str(FPS), "-an", out,
        ]
    subprocess.run(cmd, check=True, capture_output=True)
    parts.append(out)
    print(f"shot {idx+1}/{NUM_SHOTS}: {shot[1] if shot[0]=='img' else shot[1]}")

# concat list
listfile = os.path.join(tmp, "list.txt")
with open(listfile, "w") as f:
    for p in parts:
        f.write(f"file '{p}'\n")

silent_video = os.path.join(tmp, "silent.mp4")
subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile,
    "-c", "copy", silent_video,
], check=True, capture_output=True)

out_path = "teasers/zan-zan-teaser-reel.mp4"
subprocess.run([
    "ffmpeg", "-y",
    "-i", silent_video,
    "-ss", "60", "-t", f"{DUR_TOTAL}", "-i", "tracks/zan-zan/zan-zan.mp3",
    "-map", "0:v:0", "-map", "1:a:0",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart",
    "-shortest",
    out_path,
], check=True)

shutil.rmtree(tmp, ignore_errors=True)
print("SAVED:", out_path, os.path.getsize(out_path))
