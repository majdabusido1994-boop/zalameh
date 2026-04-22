"""Apply Zalameh audio tag to the start of all promo reels/teasers.

Tag is a 2s sting that plays at t=0, with the original audio ducked to ~55%
during the tag, then full volume after. Video is untouched.
"""
import os, subprocess, glob, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

TAG = "brand/audio-tag.mp3"
BACKUP_DIR = "_pre-tag-backup"
os.makedirs(BACKUP_DIR, exist_ok=True)

# Gather all promo videos
candidates = []
candidates += glob.glob("teasers/*.mp4")
candidates += glob.glob("toota/zalameh-*.mp4")

# Skip stuff that shouldn't get a tag
skip = {
    "teasers/stickers-animation.mp4",    # ambient loop, no audio to duck
    "teasers/stickers-loop-24s.mp4",     # ambient loop
    "toota/_tag-sample.mp4",             # the sample itself
}

targets = [c.replace("\\", "/") for c in candidates if c.replace("\\", "/") not in skip]
targets = [t for t in targets if not os.path.basename(t).startswith("_")]

print(f"{len(targets)} videos to tag\n")

success = 0
for i, src in enumerate(targets, 1):
    name = os.path.basename(src)
    print(f"[{i}/{len(targets)}] {name}")

    # Skip videos with no audio stream
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=codec_name", "-of", "default=nw=1:nk=1", src],
        capture_output=True, text=True,
    )
    if not r.stdout.strip():
        print("   (no audio — skipped)")
        continue

    # Get duration
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", src],
        capture_output=True, text=True,
    )
    dur = float(r.stdout.strip())

    # Backup original
    backup_path = os.path.join(BACKUP_DIR, name)
    if not os.path.isfile(backup_path):
        shutil.copy2(src, backup_path)

    tmp = src + ".tagged.mp4"
    # Layer tag over first 2s, song ducked to 55% during tag, normal after
    # Use volume with sendcmd-style time gating via enable on afade? simpler: sidechaincompress or just straight amix with tag clipped
    # Simpler approach: duck song for first 2.2s via volume filter with enable
    fc = (
        f"[0:a]volume=enable='between(t,0,2.2)':volume=0.55[duck];"
        f"[1:a]apad=whole_dur={dur}[tagpad];"
        f"[duck][tagpad]amix=inputs=2:duration=first:dropout_transition=0,"
        f"volume=1.4[aout]"
    )
    cmd = [
        "ffmpeg", "-y", "-i", src, "-i", TAG,
        "-filter_complex", fc,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        tmp,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("   ERROR:")
        print(r.stderr[-800:])
        if os.path.isfile(tmp):
            os.remove(tmp)
        continue

    # Replace original
    os.replace(tmp, src)
    sz = os.path.getsize(src) / 1024 / 1024
    print(f"   tagged. ({sz:.1f} MB)")
    success += 1

print(f"\nDONE. {success}/{len(targets)} videos tagged.")
print(f"Originals backed up to: {BACKUP_DIR}/")
