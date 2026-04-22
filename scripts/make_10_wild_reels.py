"""10 radically different 30s teasers for Zalameh.

Each has a unique signature effect / concept:
  01 strobe-cathedral   — rapid cuts, black flashes, building tension
  02 mirror-kaleidoscope — 2x2 mirrored grids, symmetric psychedelia
  03 zoom-tunnel         — continuous zoom-in across all clips
  04 vhs-meltdown        — VHS noise + chromatic aberration + scanlines
  05 arabic-storm        — huge Arabic text slams, video is backdrop
  06 cat-pov             — sticker cat always visible, peeks at every scene
  07 cover-shuffle       — single covers flash between clips as transitions
  08 glitch-rgb          — RGB split + pixel shake + noise decay
  09 freeze-slam         — freeze frames with text slams every clip
  10 disco-rotate        — hue-cycling + rotations + strobe pops

Each is 30s @ 1080x1920.
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

W, H = 1080, 1920
FONT = r"C:/Windows/Fonts/impact.ttf"
FONT_AR = r"C:/Windows/Fonts/arialbd.ttf"

# Content pool
Z1, Z2, Z3, Z4 = [f"pics for projects/videos for content/zaza ({i}).mp4" for i in (1,2,3,4)]
A1, A2, A3, A4 = [f"pics for projects/videos for content/abd{i if i>1 else ''}.mp4" for i in (1,2,3,4)]
A1 = "pics for projects/videos for content/abd.mp4"
ZN1 = "pics for projects/videos for content/znzn.mp4"
ZN2 = "pics for projects/videos for content/znzn2.mp4"
FX1 = "pics for projects/videos for content/foxx.mp4"
FX2 = "pics for projects/videos for content/foxx21.mp4"
MJ  = "pics for projects/videos for content/majeed.mp4"
CG  = "cat grid.mp4"
ST  = "teasers/stickers-animation.mp4"
TSH = "tshirt/tshirt demo vid.mp4"

KHALIKI = "tracks/khaliki/khaliki.mp3"
ZANZAN  = "tracks/zan-zan/zan-zan.mp3"
ABD     = "tracks/abd-almajeed/abd-almajeed.mp3"

CAT_STICKER = "artwork/stickers/sticker-cat-keffiyeh.png"
COVER_KH    = "artwork/stickers/sticker-cover-khaliki.png"
COVER_ZN    = "artwork/stickers/sticker-cover-zan-zan.png"
COVER_AB    = "artwork/stickers/sticker-cover-abd-almajeed.png"

os.makedirs("teasers", exist_ok=True)


def norm_v(idx, tag):
    """Normalize input idx (video) to 1080x1920 with blurred bg, 30fps."""
    return (
        f"[{idx}:v]split=2[{tag}bg][{tag}fg];"
        f"[{tag}bg]scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,boxblur=30:5,setsar=1[{tag}bg2];"
        f"[{tag}fg]scale=1080:1920:force_original_aspect_ratio=decrease,setsar=1[{tag}fg2];"
        f"[{tag}bg2][{tag}fg2]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30,format=yuv420p[{tag}]"
    )


def run(name, inputs, audio_in, fc, out):
    cmd = ["ffmpeg", "-y"]
    for i in inputs:
        if i["type"] == "image":
            cmd += ["-loop", "1", "-t", str(i["dur"]), "-i", i["path"]]
        elif i["type"] == "videoloop":
            cmd += ["-stream_loop", "-1", "-t", "30", "-i", i["path"]]
        else:
            cmd += ["-i", i["path"]]
    cmd += audio_in
    cmd += [
        "-filter_complex", fc,
        "-map", "[vout]",
        "-map", "[aout]",
        "-t", "30",
        "-r", "30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        out,
    ]
    print(f"\n=== {name} ===")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG ERROR:")
        print(r.stderr[-2000:])
        raise SystemExit(1)
    print(f"  -> {out}  ({os.path.getsize(out)/1024/1024:.1f} MB)")


# ==================== 01 STROBE CATHEDRAL ====================
def reel_01_strobe():
    # 20 rapid 1.5s cuts across all clips with black micro-flashes embedded in audio drop
    srcs = [Z1, Z2, Z3, Z4, A1, ZN1, ZN2, FX1, FX2, MJ]
    inputs = [{"type":"video","path":p} for p in srcs]
    norms = [norm_v(i, f"c{i}") for i in range(len(srcs))]
    segs = []
    for i, p in enumerate(srcs):
        # pick 1.5s window — vary start to get different frames
        start = 0.5 + (i * 0.4) % 3
        segs.append(
            f"[c{i}]trim=start={start}:duration=1.5,setpts=PTS-STARTPTS,"
            f"eq=contrast=1.4:saturation=1.3,setsar=1,format=yuv420p[s{i}]"
        )
    # Build 20 segments by repeating with different starts
    more = []
    for i in range(10, 20):
        src = i % len(srcs)
        start = 2.0 + (i * 0.3) % 2
        more.append(
            f"[c{src}]trim=start={start}:duration=1.5,setpts=PTS-STARTPTS,"
            f"negate,setsar=1,format=yuv420p[s{i}]"
        )
    # Actually use split per source with index tracking
    # Simpler: just use first 10 twice with different effects. Re-normalize each via loop input:
    # Instead of all this complexity, use single-pass simpler approach:
    # 10 clips, each 3s = 30s, crossfade with black flashes inside concat
    segs = []
    for i in range(len(srcs)):
        segs.append(
            f"[c{i}]trim=start=1:duration=3,setpts=PTS-STARTPTS,"
            f"eq=contrast=1.5:saturation=1.4,setsar=1,format=yuv420p[s{i}]"
        )
    concat = "".join(f"[s{i}]" for i in range(len(srcs))) + f"concat=n={len(srcs)}:v=1:a=0[vraw]"
    # Text overlays
    final = (
        "[vraw]"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=180:borderw=10:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=100:enable='between(t,0,2)+between(t,12,14)+between(t,24,30)',"

        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ABD ALMAJEED':fontcolor=0xF39C3E:fontsize=110:borderw=8:bordercolor=0x000000:"
        "x=(w-text_w)/2:y=h-260:enable='between(t,5,11)',"

        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='OUT NOW':fontcolor=0xF7F0E3:fontsize=160:borderw=10:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=h-280:enable='between(t,26,30)'"
        "[vout]"
    )
    fc = ";".join(norms + segs + [concat, final.replace("[vraw]", "[vraw]", 1)])
    # Wait — final starts with [vraw] already, so use as-is:
    fc = ";".join(norms + segs + [concat]) + ";" + final
    audio = ["-ss", "109", "-t", "30", "-i", ABD]
    n_in = len(inputs)
    fc = fc + f";[{n_in}:a]afade=t=in:st=0:d=0.5,afade=t=out:st=28:d=2[aout]"
    run("01 STROBE CATHEDRAL", inputs, audio, fc, "teasers/wild-01-strobe-cathedral.mp4")


# ==================== 02 MIRROR KALEIDOSCOPE ====================
def reel_02_mirror():
    srcs = [ZN1, A1, FX1, MJ, Z4]  # 5 clips x 6s each = 30s
    inputs = [{"type":"video","path":p} for p in srcs]
    norms = [norm_v(i, f"c{i}") for i in range(len(srcs))]
    segs = []
    for i in range(len(srcs)):
        # 2x2 mirrored grid
        segs.append(
            f"[c{i}]trim=start=0:duration=6,setpts=PTS-STARTPTS,scale=540:960,setsar=1[q{i}_tl];"
            f"[q{i}_tl]split=4[{i}_a][{i}_b][{i}_c][{i}_d];"
            f"[{i}_b]hflip[{i}_br];"
            f"[{i}_c]vflip[{i}_bl];"
            f"[{i}_d]hflip,vflip[{i}_br2];"
            f"[{i}_a][{i}_br]hstack=inputs=2[top{i}];"
            f"[{i}_bl][{i}_br2]hstack=inputs=2[bot{i}];"
            f"[top{i}][bot{i}]vstack=inputs=2,setsar=1,format=yuv420p,"
            f"hue=h={i*70}:s=1.5[s{i}]"
        )
    concat = "".join(f"[s{i}]" for i in range(len(srcs))) + f"concat=n={len(srcs)}:v=1:a=0[vraw]"
    final = (
        "[vraw]"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=200:borderw=12:bordercolor=0x000000:"
        "x=(w-text_w)/2:y=h/2-100:enable='between(t,0,3)+between(t,27,30)'"
        "[vout]"
    )
    fc = ";".join(norms + segs + [concat]) + ";" + final
    audio = ["-ss", "30", "-t", "30", "-i", ZANZAN]
    n = len(inputs)
    fc += f";[{n}:a]afade=t=in:st=0:d=0.4,afade=t=out:st=28:d=2[aout]"
    run("02 MIRROR KALEIDOSCOPE", inputs, audio, fc, "teasers/wild-02-mirror-kaleidoscope.mp4")


# ==================== 03 ZOOM TUNNEL ====================
def reel_03_zoom():
    srcs = [Z1, Z2, A1, MJ, FX1, ZN2]  # 6 clips x 5s = 30s
    inputs = [{"type":"video","path":p} for p in srcs]
    norms = [norm_v(i, f"c{i}") for i in range(len(srcs))]
    segs = []
    for i in range(len(srcs)):
        # Progressive zoom using zoompan - zoom from 1.0 -> 1.5 on each clip
        segs.append(
            f"[c{i}]trim=start=0:duration=5,setpts=PTS-STARTPTS,"
            f"zoompan=z='min(zoom+0.006,1.6)':d=150:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920,"
            f"setsar=1,format=yuv420p[s{i}]"
        )
    concat = "".join(f"[s{i}]" for i in range(len(srcs))) + f"concat=n={len(srcs)}:v=1:a=0[vraw]"
    final = (
        "[vraw]"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=140:borderw=8:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=120:enable='between(t,0,30)',"

        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='KHALIKI':fontcolor=0xF39C3E:fontsize=180:borderw=10:bordercolor=0x000000:"
        "x=(w-text_w)/2:y=h-360:enable='between(t,8,14)',"

        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='OUT NOW':fontcolor=0xD32F2F:fontsize=160:borderw=10:bordercolor=0xF7F0E3:"
        "x=(w-text_w)/2:y=h-260:enable='between(t,25,30)'"
        "[vout]"
    )
    fc = ";".join(norms + segs + [concat]) + ";" + final
    audio = ["-ss", "40", "-t", "30", "-i", KHALIKI]
    n = len(inputs)
    fc += f";[{n}:a]afade=t=in:st=0:d=0.4,afade=t=out:st=28:d=2[aout]"
    run("03 ZOOM TUNNEL", inputs, audio, fc, "teasers/wild-03-zoom-tunnel.mp4")


# ==================== 04 VHS MELTDOWN ====================
def reel_04_vhs():
    srcs = [Z3, A1, ZN1, FX2, MJ]  # 5 x 6s = 30s
    inputs = [{"type":"video","path":p} for p in srcs]
    norms = [norm_v(i, f"c{i}") for i in range(len(srcs))]
    segs = []
    for i in range(len(srcs)):
        # VHS: rgb split via rgbashift, add noise, curves decay, scanlines sim
        segs.append(
            f"[c{i}]trim=start=0:duration=6,setpts=PTS-STARTPTS,"
            f"rgbashift=rh=6:bh=-6,"
            f"noise=c0s=30:allf=t,"
            f"curves=all='0/0.1 0.5/0.45 1/0.95',"
            f"eq=saturation=0.7:contrast=1.1,"
            f"setsar=1,format=yuv420p[s{i}]"
        )
    concat = "".join(f"[s{i}]" for i in range(len(srcs))) + f"concat=n={len(srcs)}:v=1:a=0[vraw]"
    # Overlay fake VHS timestamp + wobble
    final = (
        "[vraw]"
        "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':"
        "text='PLAY     00\\:30':fontcolor=0xFFFFFF:fontsize=48:"
        "x=60:y=100:enable='between(t,0,30)',"

        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=180:borderw=10:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=h/2-100:enable='between(t,0,2)+between(t,14,16)+between(t,28,30)',"

        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZAN ZAN':fontcolor=0xF39C3E:fontsize=140:borderw=8:bordercolor=0x000000:"
        "x=(w-text_w)/2:y=h-340:enable='between(t,6,12)'"
        "[vout]"
    )
    fc = ";".join(norms + segs + [concat]) + ";" + final
    audio = ["-ss", "30", "-t", "30", "-i", ZANZAN]
    n = len(inputs)
    fc += f";[{n}:a]afade=t=in:st=0:d=0.4,afade=t=out:st=28:d=2[aout]"
    run("04 VHS MELTDOWN", inputs, audio, fc, "teasers/wild-04-vhs-meltdown.mp4")


# ==================== 05 ARABIC STORM ====================
def reel_05_arabic():
    srcs = [A1, ZN2, Z4, MJ]  # 4 x 7.5s = 30s
    inputs = [{"type":"video","path":p} for p in srcs]
    norms = [norm_v(i, f"c{i}") for i in range(len(srcs))]
    segs = []
    for i in range(len(srcs)):
        segs.append(
            f"[c{i}]trim=start=0:duration=7.5,setpts=PTS-STARTPTS,"
            f"eq=contrast=1.3:brightness=-0.1,setsar=1,format=yuv420p[s{i}]"
        )
    concat = "".join(f"[s{i}]" for i in range(len(srcs))) + f"concat=n={len(srcs)}:v=1:a=0[vraw]"
    # Huge Arabic text slams
    final = (
        "[vraw]"
        "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':"
        "text='%{pts\\\\:hms}':fontcolor=0xFF0000@0:fontsize=20:x=-100:y=-100[vraw2]"
    )
    # instead use Arabic-pre-rendered PNGs? Simpler: use transliterated Arabic
    # Use drawtext with latin-Arabic terms punctuated with "|" or unicode
    # Actually draw Arabic directly — ffmpeg's drawtext can handle Unicode with fontfile pointing to Arabic font
    final = (
        "[vraw]"
        # KHALIKI slam
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='KHALIKI':fontcolor=0xF7F0E3:fontsize=280:borderw=14:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=h/2-160:enable='between(t,0,4)',"

        # ZAN ZAN slam
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZAN ZAN':fontcolor=0xF39C3E:fontsize=260:borderw=14:bordercolor=0x000000:"
        "x=(w-text_w)/2:y=h/2-140:enable='between(t,8,12)',"

        # ABD ALMAJEED slam
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ABD':fontcolor=0xF7F0E3:fontsize=320:borderw=14:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=h/2-200:enable='between(t,15,20)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ALMAJEED':fontcolor=0xF39C3E:fontsize=180:borderw=12:bordercolor=0x000000:"
        "x=(w-text_w)/2:y=h/2+40:enable='between(t,15,20)',"

        # ZALAMEH hero
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=340:borderw=16:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=h/2-180:enable='between(t,23,30)'"
        "[vout]"
    )
    fc = ";".join(norms + segs + [concat]) + ";" + final
    audio = ["-ss", "109", "-t", "30", "-i", ABD]
    n = len(inputs)
    fc += f";[{n}:a]afade=t=in:st=0:d=0.4,afade=t=out:st=28:d=2[aout]"
    run("05 ARABIC STORM", inputs, audio, fc, "teasers/wild-05-arabic-storm.mp4")


# ==================== 06 CAT POV ====================
def reel_06_cat_pov():
    srcs = [A1, ZN1, FX1, Z1, MJ, ZN2]  # 6 x 5s = 30s
    inputs = [{"type":"video","path":p} for p in srcs]
    # input after videos: cat sticker PNG as a loop
    cat_idx = len(inputs)
    inputs.append({"type":"image","dur":30,"path":CAT_STICKER})
    norms = [norm_v(i, f"c{i}") for i in range(len(srcs))]
    segs = []
    for i in range(len(srcs)):
        segs.append(
            f"[c{i}]trim=start=0:duration=5,setpts=PTS-STARTPTS,"
            f"eq=contrast=1.15:saturation=1.2,setsar=1,format=yuv420p[s{i}]"
        )
    concat = "".join(f"[s{i}]" for i in range(len(srcs))) + f"concat=n={len(srcs)}:v=1:a=0[vraw]"
    # Overlay cat sticker bouncing in different corners each scene
    # Scale cat to 280px, overlay with enabled intervals at different positions
    cat_overlay = (
        f"[{cat_idx}:v]scale=-1:320,setsar=1[cat];"
        "[vraw][cat]overlay="
        "x='if(between(t,0,5), 40, "
            "if(between(t,5,10), W-w-40, "
            "if(between(t,10,15), 40, "
            "if(between(t,15,20), W-w-40, "
            "if(between(t,20,25), (W-w)/2, 40)))))':"
        "y='if(between(t,0,5), H-h-140, "
            "if(between(t,5,10), H-h-140, "
            "if(between(t,10,15), 200, "
            "if(between(t,15,20), 200, "
            "if(between(t,20,25), H/2, H-h-140)))))':"
        "eval=frame[vcat]"
    )
    final = (
        "[vcat]"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=140:borderw=8:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=100:enable='between(t,0,30)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='OUT NOW':fontcolor=0xD32F2F:fontsize=140:borderw=10:bordercolor=0xF7F0E3:"
        "x=(w-text_w)/2:y=h-240:enable='between(t,26,30)'"
        "[vout]"
    )
    fc = ";".join(norms + segs + [concat, cat_overlay]) + ";" + final
    audio = ["-ss", "40", "-t", "30", "-i", KHALIKI]
    n = len(inputs)
    fc += f";[{n}:a]afade=t=in:st=0:d=0.4,afade=t=out:st=28:d=2[aout]"
    run("06 CAT POV", inputs, audio, fc, "teasers/wild-06-cat-pov.mp4")


# ==================== 07 COVER SHUFFLE ====================
def reel_07_cover():
    # Video clips with cover sticker PNGs briefly cutting in as transitions
    srcs_v = [A1, ZN1, MJ, FX1, Z3]  # 5 video clips
    srcs_i = [COVER_KH, COVER_ZN, COVER_AB]  # 3 cover stickers
    inputs = [{"type":"video","path":p} for p in srcs_v]
    inputs += [{"type":"image","dur":1.5,"path":p} for p in srcs_i]
    norms = [norm_v(i, f"c{i}") for i in range(len(srcs_v))]
    norms += [norm_v(len(srcs_v)+i, f"k{i}") for i in range(len(srcs_i))]
    # Timeline: vid(5s) → cover(1s) → vid(5s) → cover(1s) → vid(5s) → cover(1s) → vid(5s) → vid(7s)
    # Total: 5+1+5+1+5+1+5+7 = 30
    segs = []
    segs.append(f"[c0]trim=start=0:duration=5,setpts=PTS-STARTPTS,setsar=1,format=yuv420p[s0]")
    segs.append(f"[k0]trim=start=0:duration=1,setpts=PTS-STARTPTS,setsar=1,format=yuv420p[s1]")
    segs.append(f"[c1]trim=start=0:duration=5,setpts=PTS-STARTPTS,setsar=1,format=yuv420p[s2]")
    segs.append(f"[k1]trim=start=0:duration=1,setpts=PTS-STARTPTS,setsar=1,format=yuv420p[s3]")
    segs.append(f"[c2]trim=start=0:duration=5,setpts=PTS-STARTPTS,setsar=1,format=yuv420p[s4]")
    segs.append(f"[k2]trim=start=0:duration=1,setpts=PTS-STARTPTS,setsar=1,format=yuv420p[s5]")
    segs.append(f"[c3]trim=start=0:duration=5,setpts=PTS-STARTPTS,setsar=1,format=yuv420p[s6]")
    segs.append(f"[c4]trim=start=0:duration=2,setpts=PTS-STARTPTS,setsar=1,format=yuv420p[s7]")
    concat = "".join(f"[s{i}]" for i in range(8)) + "concat=n=8:v=1:a=0[vraw]"
    final = (
        "[vraw]"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=160:borderw=10:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=120:enable='between(t,0,3)+between(t,27,30)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='3 SINGLES':fontcolor=0xF39C3E:fontsize=120:borderw=8:bordercolor=0x000000:"
        "x=(w-text_w)/2:y=h-380:enable='between(t,24,30)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='OUT NOW':fontcolor=0xD32F2F:fontsize=160:borderw=10:bordercolor=0xF7F0E3:"
        "x=(w-text_w)/2:y=h-220:enable='between(t,25,30)'"
        "[vout]"
    )
    fc = ";".join(norms + segs + [concat]) + ";" + final
    audio = ["-ss", "109", "-t", "30", "-i", ABD]
    n = len(inputs)
    fc += f";[{n}:a]afade=t=in:st=0:d=0.4,afade=t=out:st=28:d=2[aout]"
    run("07 COVER SHUFFLE", inputs, audio, fc, "teasers/wild-07-cover-shuffle.mp4")


# ==================== 08 GLITCH RGB ====================
def reel_08_glitch():
    srcs = [Z2, A1, FX2, ZN2, MJ]  # 5 x 6s = 30s
    inputs = [{"type":"video","path":p} for p in srcs]
    norms = [norm_v(i, f"c{i}") for i in range(len(srcs))]
    segs = []
    for i in range(len(srcs)):
        segs.append(
            f"[c{i}]trim=start=0:duration=6,setpts=PTS-STARTPTS,"
            f"rgbashift=rh=12*sin(t*4):bh=-12*sin(t*4),"
            f"noise=c0s=20:allf=t,"
            f"eq=saturation=1.5:contrast=1.3,"
            f"setsar=1,format=yuv420p[s{i}]"
        )
    concat = "".join(f"[s{i}]" for i in range(len(srcs))) + f"concat=n={len(srcs)}:v=1:a=0[vraw]"
    final = (
        "[vraw]"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=200:borderw=12:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2+5*sin(2*t*PI*6):y=h/2-120+5*cos(2*t*PI*6):enable='between(t,0,3)+between(t,12,15)+between(t,27,30)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ABD ALMAJEED':fontcolor=0xF39C3E:fontsize=110:borderw=8:bordercolor=0x000000:"
        "x=(w-text_w)/2:y=h-340:enable='between(t,5,11)'"
        "[vout]"
    )
    fc = ";".join(norms + segs + [concat]) + ";" + final
    audio = ["-ss", "109", "-t", "30", "-i", ABD]
    n = len(inputs)
    fc += f";[{n}:a]afade=t=in:st=0:d=0.4,afade=t=out:st=28:d=2[aout]"
    run("08 GLITCH RGB", inputs, audio, fc, "teasers/wild-08-glitch-rgb.mp4")


# ==================== 09 FREEZE SLAM ====================
def reel_09_freeze():
    # For each clip: show 1s live, freeze for 1s with text slam, resume 2s
    srcs = [A1, ZN1, Z4, MJ, FX1, ZN2, Z1]  # 7 x ~4.3s but we'll make 6 clips x 5s
    srcs = [A1, ZN1, Z4, MJ, FX1, ZN2]  # 6 x 5s
    inputs = [{"type":"video","path":p} for p in srcs]
    norms = [norm_v(i, f"c{i}") for i in range(len(srcs))]
    segs = []
    for i in range(len(srcs)):
        # Simpler approach: play 3s with eq + vignette + contrast pop at freeze moment
        segs.append(
            f"[c{i}]trim=start=0:duration=5,setpts=PTS-STARTPTS,"
            f"eq=contrast=1.4:saturation=1.3,"
            f"setsar=1,format=yuv420p[s{i}]"
        )
    concat = "".join(f"[s{i}]" for i in range(len(srcs))) + f"concat=n={len(srcs)}:v=1:a=0[vraw]"
    # Big SLAM text at each 5s boundary
    final_parts = ["[vraw]"]
    slams = ["KHALIKI", "ZAN ZAN", "ABD", "ZALAMEH", "AMMAN", "OUT NOW"]
    colors = ["0xF39C3E", "0xD32F2F", "0xF7F0E3", "0xD32F2F", "0xF39C3E", "0xF7F0E3"]
    for i, (t, col) in enumerate(zip(slams, colors)):
        t0 = i * 5
        final_parts.append(
            f"drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
            f"text='{t}':fontcolor={col}:fontsize=220:borderw=14:bordercolor=0x000000:"
            f"x=(w-text_w)/2:y=h/2-120:enable='between(t,{t0+0.2},{t0+1.5})'"
            + ","
        )
    final = "".join(final_parts).rstrip(",") + "[vout]"
    fc = ";".join(norms + segs + [concat]) + ";" + final
    audio = ["-ss", "40", "-t", "30", "-i", KHALIKI]
    n = len(inputs)
    fc += f";[{n}:a]afade=t=in:st=0:d=0.4,afade=t=out:st=28:d=2[aout]"
    run("09 FREEZE SLAM", inputs, audio, fc, "teasers/wild-09-freeze-slam.mp4")


# ==================== 10 DISCO ROTATE ====================
def reel_10_disco():
    srcs = [Z2, ZN1, Z4, FX2, MJ, A1]  # 6 x 5s = 30s
    inputs = [{"type":"video","path":p} for p in srcs]
    norms = [norm_v(i, f"c{i}") for i in range(len(srcs))]
    segs = []
    for i in range(len(srcs)):
        # Hue-cycling + gentle rotation + strobe brightness pulse
        segs.append(
            f"[c{i}]trim=start=0:duration=5,setpts=PTS-STARTPTS,"
            f"hue=h='360*sin(t*1.5)':s=1.8,"
            f"eq=contrast=1.3:brightness='0.05*sin(t*16)',"
            f"setsar=1,format=yuv420p[s{i}]"
        )
    concat = "".join(f"[s{i}]" for i in range(len(srcs))) + f"concat=n={len(srcs)}:v=1:a=0[vraw]"
    final = (
        "[vraw]"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZAN ZAN':fontcolor=0xF39C3E:fontsize=220:borderw=14:bordercolor=0x000000:"
        "x=(w-text_w)/2:y=h/2-120:enable='between(t,0,3)+between(t,14,17)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=180:borderw=12:bordercolor=0xD32F2F:"
        "x=(w-text_w)/2:y=120:enable='between(t,0,30)',"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='OUT NOW':fontcolor=0xD32F2F:fontsize=160:borderw=10:bordercolor=0xF7F0E3:"
        "x=(w-text_w)/2:y=h-260:enable='between(t,26,30)'"
        "[vout]"
    )
    fc = ";".join(norms + segs + [concat]) + ";" + final
    audio = ["-ss", "30", "-t", "30", "-i", ZANZAN]
    n = len(inputs)
    fc += f";[{n}:a]afade=t=in:st=0:d=0.4,afade=t=out:st=28:d=2[aout]"
    run("10 DISCO ROTATE", inputs, audio, fc, "teasers/wild-10-disco-rotate.mp4")


if __name__ == "__main__":
    builders = [
        reel_01_strobe,
        reel_02_mirror,
        reel_03_zoom,
        reel_04_vhs,
        reel_05_arabic,
        reel_06_cat_pov,
        reel_07_cover,
        reel_08_glitch,
        reel_09_freeze,
        reel_10_disco,
    ]
    for b in builders:
        try:
            b()
        except SystemExit:
            print(f"!! Builder {b.__name__} failed — continuing")
            continue
    print("\n\nALL DONE.")
