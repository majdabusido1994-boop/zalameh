"""TOOTA TOOTA — YouTube full 2:04 + 4 × 31s reels from the 15s hero clip.

- Full YT: hero looped 8x @ 15s each, each loop gets a different visual treatment
- Reels:   each pulls a 31s window of the audio and applies its own look
"""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

OUT = "toota"
os.makedirs(OUT, exist_ok=True)
HERO = f"{OUT}/hero.mp4"
TRACK = f"{OUT}/toota.mp3"

W, H = 1080, 1920
FONT = "C:/Windows/Fonts/impact.ttf"
FONT_AR = "C:/Windows/Fonts/arialbd.ttf"
ARABTYPE = "C:/Windows/Fonts/arabtype.ttf" if os.path.exists("C:/Windows/Fonts/arabtype.ttf") else FONT_AR


def ar(s):
    return get_display(arabic_reshaper.reshape(s))


def find_font(candidates, size):
    for n in candidates:
        p = os.path.join(r"C:\Windows\Fonts", n)
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


# Normalize hero 496x864 -> 1080x1920 with blurred fill
def norm(idx, tag):
    return (
        f"[{idx}:v]split=2[{tag}bg][{tag}fg];"
        f"[{tag}bg]scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,boxblur=30:5,setsar=1[{tag}bg2];"
        f"[{tag}fg]scale=1080:1920:force_original_aspect_ratio=decrease,setsar=1[{tag}fg2];"
        f"[{tag}bg2][{tag}fg2]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30,format=yuv420p[{tag}]"
    )


def run(name, cmd, out):
    print(f"\n=== {name} ===")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG ERROR:")
        print(r.stderr[-1800:])
        raise SystemExit(1)
    print(f"  -> {out}  ({os.path.getsize(out)/1024/1024:.1f} MB)")


# =====================================================================
# 1) YOUTUBE FULL 2:04 — 8 loops of hero, each with different treatment
# =====================================================================
def make_youtube():
    # We'll feed 8 copies of the hero as separate -i inputs (each looped to 15.5s)
    # then apply a unique effect to each and concat. Hero runs from 0 each input.
    LOOPS = [
        ("normal",        "eq=contrast=1.1:saturation=1.1"),
        ("warm",          "eq=saturation=1.3,colorbalance=rm=0.15:gm=0.05:bm=-0.10"),
        ("zoom",          "zoompan=z='min(zoom+0.002,1.25)':d=450:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920"),
        ("mirror",        "hflip,eq=saturation=1.2"),
        ("teal",          "colorbalance=rm=-0.15:gm=0.05:bm=0.20,eq=contrast=1.2"),
        ("vhs",           "scale=720:1280,scale=1080:1920:flags=neighbor,noise=c0s=6:allf=t,rgbashift=rh=4:bh=-4,eq=saturation=0.85"),
        ("gold",          "hue=h=30:s=1.4,eq=brightness=0.02:contrast=1.15"),
        ("final",         "eq=contrast=1.2:saturation=1.3,colorbalance=rm=0.10:bm=-0.10"),
    ]
    DUR = 15.5
    n = len(LOOPS)

    cmd = ["ffmpeg", "-y"]
    for _ in range(n):
        cmd += ["-stream_loop", "-1", "-t", str(DUR), "-i", HERO]
    cmd += ["-i", TRACK]

    parts = []
    for i, (tag, eff) in enumerate(LOOPS):
        parts.append(norm(i, f"n{i}"))
        parts.append(f"[n{i}]trim=duration={DUR},setpts=PTS-STARTPTS,{eff},setsar=1,format=yuv420p[s{i}]")

    concat = "".join(f"[s{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[vraw]"
    parts.append(concat)

    # Text overlays — Zalameh brand only
    final = (
        "[vraw]"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=200:borderw=12:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=h/2-120:enable='between(t,0,3)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=200:borderw=12:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=h/2-120:enable='between(t,118,124)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':"
        "text='@zalameh.69':fontcolor=0xF39C3E:fontsize=60:"
        "x=(w-text_w)/2:y=h-260:enable='between(t,118,124)'"
        "[vout]"
    )
    parts.append(final)
    parts.append(f"[{n}:a]afade=t=in:st=0:d=0.4,afade=t=out:st=123:d=1.7[aout]")

    fc = ";".join(parts)
    out = f"{OUT}/toota-youtube-2m04.mp4"
    cmd += [
        "-filter_complex", fc,
        "-map", "[vout]", "-map", "[aout]",
        "-t", "124.7", "-r", "30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest", out,
    ]
    run("YOUTUBE 2:04", cmd, out)


# =====================================================================
# 2) REELS: 4 × 31s, each pulls a different audio window + different look
# =====================================================================
def make_reel(name, audio_ss, eff_chain, text_overlays, out_file):
    """Build one 31s reel from 2 loops of hero + audio window."""
    DUR = 15.5
    cmd = ["ffmpeg", "-y",
           "-stream_loop", "-1", "-t", str(DUR), "-i", HERO,
           "-stream_loop", "-1", "-t", str(DUR), "-i", HERO,
           "-ss", str(audio_ss), "-t", "31", "-i", TRACK]

    parts = [norm(0, "a"), norm(1, "b")]
    parts.append(f"[a]trim=duration={DUR},setpts=PTS-STARTPTS,{eff_chain[0]},setsar=1,format=yuv420p[s0]")
    parts.append(f"[b]trim=duration={DUR},setpts=PTS-STARTPTS,{eff_chain[1]},setsar=1,format=yuv420p[s1]")
    parts.append("[s0][s1]concat=n=2:v=1:a=0[vraw]")
    parts.append("[vraw]" + text_overlays + "[vout]")
    parts.append("[2:a]afade=t=in:st=0:d=0.3,afade=t=out:st=29.5:d=1.5[aout]")

    fc = ";".join(parts)
    cmd += [
        "-filter_complex", fc,
        "-map", "[vout]", "-map", "[aout]",
        "-t", "31", "-r", "30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest", out_file,
    ]
    run(name, cmd, out_file)


def make_reels():
    # Reel 1 — OPENING: first 31s of track, warm/normal build
    reel1_text = (
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=180:borderw=10:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=100:enable='between(t,0,31)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':"
        "text='@zalameh.69':fontcolor=0xF39C3E:fontsize=58:"
        "x=(w-text_w)/2:y=h-200:enable='between(t,26,31)'"
    )
    make_reel(
        "REEL 1 OPENING",
        audio_ss=0,
        eff_chain=[
            "eq=contrast=1.1:saturation=1.15",
            "eq=saturation=1.25,colorbalance=rm=0.12:bm=-0.08",
        ],
        text_overlays=reel1_text,
        out_file=f"{OUT}/toota-reel-1-opening.mp4",
    )

    # Reel 2 — VERSE: middle of track, mirror + teal
    reel2_text = (
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=160:borderw=10:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=100:enable='between(t,0,31)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='AMMAN':fontcolor=0xF39C3E:fontsize=180:borderw=10:bordercolor=0x000000:"
        "x=(w-text_w)/2:y=h-340:enable='between(t,5,10)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':"
        "text='@zalameh.69':fontcolor=0xF39C3E:fontsize=58:"
        "x=(w-text_w)/2:y=h-200:enable='between(t,26,31)'"
    )
    make_reel(
        "REEL 2 VERSE",
        audio_ss=30,
        eff_chain=[
            "hflip,eq=saturation=1.2:contrast=1.15",
            "colorbalance=rm=-0.12:gm=0.05:bm=0.18,eq=contrast=1.2",
        ],
        text_overlays=reel2_text,
        out_file=f"{OUT}/toota-reel-2-verse.mp4",
    )

    # Reel 3 — HOOK: mid-late, gold hue + zoom
    reel3_text = (
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=260:borderw=14:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=h/2-150:enable='between(t,0,4)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=140:borderw=8:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=100:enable='between(t,5,31)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':"
        "text='@zalameh.69':fontcolor=0xF39C3E:fontsize=58:"
        "x=(w-text_w)/2:y=h-200:enable='between(t,26,31)'"
    )
    make_reel(
        "REEL 3 HOOK",
        audio_ss=62,
        eff_chain=[
            "hue=h=25:s=1.4,eq=brightness=0.02:contrast=1.18",
            "zoompan=z='min(zoom+0.002,1.3)':d=450:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920,eq=saturation=1.25",
        ],
        text_overlays=reel3_text,
        out_file=f"{OUT}/toota-reel-3-hook.mp4",
    )

    # Reel 4 — OUTRO: last part of track, VHS decay
    reel4_text = (
        "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':"
        "text='PLAY     ZALAMEH':fontcolor=0xFFFFFF:fontsize=44:"
        "x=60:y=100:enable='between(t,0,31)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=220:borderw=14:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=h/2-120:enable='between(t,24,31)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':"
        "text='@zalameh.69':fontcolor=0xF39C3E:fontsize=58:"
        "x=(w-text_w)/2:y=h/2+100:enable='between(t,25,31)'"
    )
    make_reel(
        "REEL 4 OUTRO",
        audio_ss=93.7,
        eff_chain=[
            "scale=720:1280,scale=1080:1920:flags=neighbor,noise=c0s=7:allf=t,rgbashift=rh=5:bh=-5,eq=saturation=0.85",
            "eq=contrast=1.25:saturation=1.4,colorbalance=rm=0.15:bm=-0.12",
        ],
        text_overlays=reel4_text,
        out_file=f"{OUT}/toota-reel-4-outro.mp4",
    )


if __name__ == "__main__":
    make_youtube()
    make_reels()
    print("\n\nALL DONE.")
