"""Loop the 4s sticker animation to 24s with Khaliki vocals (40s-64s window)."""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SRC   = "teasers/stickers-animation.mp4"
AUDIO = "tracks/khaliki/khaliki.mp3"
OUT   = "teasers/stickers-loop-24s.mp4"
AUDIO_START = 40.0
DUR = 24.0

subprocess.run([
    "ffmpeg","-y",
    "-stream_loop","-1","-i", SRC,
    "-ss", str(AUDIO_START), "-t", f"{DUR}", "-i", AUDIO,
    "-map","0:v:0","-map","1:a:0",
    "-t", f"{DUR}",
    "-c:v","libx264","-pix_fmt","yuv420p","-preset","medium","-crf","20",
    "-c:a","aac","-b:a","192k",
    "-movflags","+faststart","-shortest",
    OUT,
], check=True)

print("SAVED:", OUT, os.path.getsize(OUT))
