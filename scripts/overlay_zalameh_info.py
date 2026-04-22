"""Overlay ZALAMEH wordmark (t=0 with audio tag) + socials (subtle, bottom-left).

Elegant rules:
- Title fades IN over 0.3s, holds to 2.0s, fades OUT by 2.4s (matches audio tag).
- Socials fade in at t=2.8s (after title leaves), hold to end, low-weight type
  with soft shadow — never fights the visuals.
"""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

OUT = "jordan-series"

# Fonts — ffmpeg on Windows needs forward slash + escaped colon inside filter
IMPACT  = r"'C\:/Windows/Fonts/impact.ttf'"
ARIALBD = r"'C\:/Windows/Fonts/arialbd.ttf'"
ARIAL   = r"'C\:/Windows/Fonts/arial.ttf'"

REELS = [
    "reel-jerash",
    "reel-dead-sea",
    "reel-ajloun",
    "reel-wadi-rum",
]

# Title alpha: fade in 0->0.3, hold to 2.0, fade out 2.0->2.4
TITLE_ALPHA = (
    "if(lt(t,0.3),t/0.3,"
    "if(lt(t,2.0),1,"
    "if(lt(t,2.4),(2.4-t)/0.4,0)))"
)

# Socials alpha: start invisible, fade in 2.8 -> 3.4, hold, fade out 14.4 -> 15.0
SOC_ALPHA = (
    "if(lt(t,2.8),0,"
    "if(lt(t,3.4),(t-2.8)/0.6,"
    "if(lt(t,14.4),0.85,"
    "if(lt(t,15.0),0.85*(15.0-t)/0.6,0))))"
)

def build(reel):
    src = f"{OUT}/{reel}.mp4"
    dst = f"{OUT}/{reel}-info.mp4"
    print(f"\n=== {reel} ===")

    # Title: ZALAMEH in heavy condensed, slightly above center, with soft shadow
    title = (
        f"drawtext=fontfile={IMPACT}"
        f":text='ZALAMEH'"
        f":fontcolor=white:fontsize=180"
        f":x=(w-text_w)/2:y=h*0.38"
        f":shadowcolor=black@0.55:shadowx=3:shadowy=5"
        f":alpha='{TITLE_ALPHA}'"
    )

    # Tagline under title: "AMMAN · JORDAN"
    tagline = (
        f"drawtext=fontfile={ARIALBD}"
        f":text='AMMAN  //  JORDAN'"
        f":fontcolor=white:fontsize=38"
        f":x=(w-text_w)/2:y=h*0.38+200"
        f":shadowcolor=black@0.6:shadowx=2:shadowy=3"
        f":alpha='{TITLE_ALPHA}'"
    )

    # Socials — bottom-left, three compact lines
    pad_x = 50
    base_y = 1680  # bottom area for 1920 tall
    line_h = 52
    soc_font = 32

    def soc_line(idx, txt):
        return (
            f"drawtext=fontfile={ARIALBD}"
            f":text='{txt}'"
            f":fontcolor=white:fontsize={soc_font}"
            f":x={pad_x}:y={base_y + idx*line_h}"
            f":shadowcolor=black@0.75:shadowx=2:shadowy=2"
            f":alpha='{SOC_ALPHA}'"
        )

    handle = soc_line(0, "SPOTIFY   Zalameh")
    ig     = soc_line(1, "INSTAGRAM   @zalameh.69")
    yt     = soc_line(2, "YOUTUBE   @zalameh.69")

    # Top-line site url (tiny, top-left, same fade as socials)
    site = (
        f"drawtext=fontfile={ARIAL}"
        f":text='zalameh.netlify.app'"
        f":fontcolor=white:fontsize=26"
        f":x={pad_x}:y=70"
        f":shadowcolor=black@0.7:shadowx=2:shadowy=2"
        f":alpha='{SOC_ALPHA}'"
    )

    vf = ",".join([title, tagline, handle, ig, yt, site])

    cmd = [
        "ffmpeg", "-y", "-i", src,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-movflags", "+faststart",
        dst,
    ]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", errors="replace")[-1500:]
        print("ERROR:\n" + err)
        return False
    sz = os.path.getsize(dst) / 1024 / 1024
    print(f"  -> {dst}  ({sz:.1f} MB)")
    return True

for r in REELS:
    build(r)

print("\nDONE.")
