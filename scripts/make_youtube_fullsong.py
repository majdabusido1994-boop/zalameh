"""
Full-song YouTube videos for Zalameh's 3 singles.

Direction: simple, always-in-sync.
  - 1920x1080 (YouTube standard)
  - Cover art centered on its own blurred copy as backdrop
  - Bottom: audio waveform visualization (generated live from the track
    itself → literally cannot drift, always in sync with the beat)
  - Top bar: ZALAMEH + song title
  - Full song length

Outputs:
  youtube-videos/zan-zan.mp4
  youtube-videos/abd-almajeed.mp4
  youtube-videos/khaliki.mp4
"""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
os.makedirs("youtube-videos", exist_ok=True)

W, H = 1920, 1080
FPS = 30
COVER_SIZE = 880                 # centered square cover
WAVE_H = 180                     # waveform strip height
CREAM = "0xF7F0E3"
INK   = "0x1F1B18"
KRED  = "0xD32F2F"
SUNSET= "0xF39C3E"

TRACKS = [
    # (id, title_display, arabic_title, cover_path, audio_path)
    ("zan-zan",      "ZAN ZAN",      "زن زن",
        "artwork/covers/zan-zan-cover-3000-bars.jpg",
        "tracks/zan-zan/zan-zan.mp3"),
    ("abd-almajeed", "ABD ALMAJEED", "عبد المجيد",
        "artwork/covers/zalameh-cover-3000.jpg",
        "tracks/abd-almajeed/abd-almajeed.mp3"),
    ("khaliki",      "KHALIKI",      "خليكي",
        "artwork/covers/cover-walking-3000.jpg",
        "tracks/khaliki/khaliki.mp3"),
]

def build(tid, title, ar_title, cover, audio):
    out = f"youtube-videos/{tid}.mp4"
    # Pre-render title PNG with Arabic via PIL (ffmpeg drawtext can't reshape Arabic)
    from PIL import Image, ImageDraw, ImageFont
    import arabic_reshaper
    from bidi.algorithm import get_display

    def find_font(names, size):
        fd = r"C:\Windows\Fonts"
        for n in names:
            p = os.path.join(fd, n)
            if os.path.isfile(p):
                try: return ImageFont.truetype(p, size)
                except: pass
        return ImageFont.load_default()

    bar_h = 110
    strip = Image.new("RGBA", (W, bar_h), (31, 27, 24, 230))
    d = ImageDraw.Draw(strip)
    font_en = find_font(["impact.ttf", "arialbd.ttf"], 58)
    font_ar = find_font(["tradbdo.ttf", "arabtype.ttf", "arialbd.ttf"], 62)
    font_handle = find_font(["arialbd.ttf"], 36)
    d.text((40, 22), "ZALAMEH", font=font_en, fill=(247, 240, 227, 255))
    d.text((320, 22), f"· {title}", font=font_en, fill=(211, 47, 47, 255))
    ar_shown = get_display(arabic_reshaper.reshape(ar_title))
    bb = font_ar.getbbox(ar_shown)
    d.text((W - (bb[2]-bb[0]) - 40, 18), ar_shown, font=font_ar, fill=(243, 156, 62, 255))
    d.text((40, bar_h-42), "@zalameh.69  ·  zalameh.netlify.app", font=font_handle, fill=(247, 240, 227, 200))
    strip_path = f"youtube-videos/_title_{tid}.png"
    strip.save(strip_path)

    cover_y = 120   # below title bar
    filter_complex = (
        # Blurred background from the cover
        f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"boxblur=30:2,eq=brightness=-0.08:saturation=0.9[bg];"
        # Sharp centered cover
        f"[0:v]scale={COVER_SIZE}:{COVER_SIZE}:force_original_aspect_ratio=decrease,"
        f"pad={COVER_SIZE}:{COVER_SIZE}:(ow-iw)/2:(oh-ih)/2:color={CREAM}[fg];"
        # Compose
        f"[bg][fg]overlay=(W-w)/2:{cover_y}[stage];"
        # Title strip
        f"[stage][2:v]overlay=0:0[titled];"
        # Live waveform (always in sync — derived from the actual audio)
        f"[1:a]showwaves=s={W}x{WAVE_H}:mode=cline:colors={KRED}|{CREAM}:rate={FPS}[wave];"
        f"[titled][wave]overlay=0:{H-WAVE_H}[v]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", cover,
        "-i", audio,
        "-loop", "1", "-i", strip_path,
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "256k",
        "-r", str(FPS),
        "-movflags", "+faststart",
        "-shortest",
        out,
    ]
    print(">>", tid)
    subprocess.run(cmd, check=True)
    size = os.path.getsize(out)
    print(f"SAVED: {out}  {size/1024/1024:.1f}MB")

for t in TRACKS:
    build(*t)

print("ALL DONE")
