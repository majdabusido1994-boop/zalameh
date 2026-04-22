"""Patch: rebuild reels 04 (VHS — was 300MB, too noisy) and 08 (GLITCH — rgbashift rejected expression)."""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

Z1 = "pics for projects/videos for content/zaza (1).mp4"
Z2 = "pics for projects/videos for content/zaza (2).mp4"
Z3 = "pics for projects/videos for content/zaza (3).mp4"
Z4 = "pics for projects/videos for content/zaza (4).mp4"
A1 = "pics for projects/videos for content/abd.mp4"
ZN1 = "pics for projects/videos for content/znzn.mp4"
ZN2 = "pics for projects/videos for content/znzn2.mp4"
FX2 = "pics for projects/videos for content/foxx21.mp4"
MJ = "pics for projects/videos for content/majeed.mp4"

KHALIKI = "tracks/khaliki/khaliki.mp3"
ZANZAN = "tracks/zan-zan/zan-zan.mp3"
ABD = "tracks/abd-almajeed/abd-almajeed.mp3"


def norm_v(idx, tag):
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
        else:
            cmd += ["-i", i["path"]]
    cmd += audio_in
    cmd += [
        "-filter_complex", fc,
        "-map", "[vout]", "-map", "[aout]",
        "-t", "30", "-r", "30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest", out,
    ]
    print(f"\n=== {name} ===")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG ERROR:")
        print(r.stderr[-1500:])
        raise SystemExit(1)
    print(f"  -> {out}  ({os.path.getsize(out)/1024/1024:.1f} MB)")


# ========== 04 VHS MELTDOWN (fixed: lower noise, tighter crf) ==========
def reel_04_vhs():
    srcs = [Z3, A1, ZN1, FX2, MJ]
    inputs = [{"type":"video","path":p} for p in srcs]
    norms = [norm_v(i, f"c{i}") for i in range(len(srcs))]
    segs = []
    for i in range(len(srcs)):
        segs.append(
            f"[c{i}]trim=start=0:duration=6,setpts=PTS-STARTPTS,"
            f"scale=720:1280,scale=1080:1920:flags=neighbor,"
            f"rgbashift=rh=6:bh=-6,"
            f"noise=c0s=8:allf=t,"
            f"curves=all='0/0.08 0.5/0.5 1/0.92',"
            f"eq=saturation=0.75:contrast=1.08,"
            f"setsar=1,format=yuv420p[s{i}]"
        )
    concat = "".join(f"[s{i}]" for i in range(len(srcs))) + f"concat=n={len(srcs)}:v=1:a=0[vraw]"
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


# ========== 08 GLITCH RGB (fixed: static rgbashift per-clip) ==========
def reel_08_glitch():
    srcs = [Z2, A1, FX2, ZN2, MJ]
    inputs = [{"type":"video","path":p} for p in srcs]
    norms = [norm_v(i, f"c{i}") for i in range(len(srcs))]
    segs = []
    # vary the rgb shift per clip for different glitch flavor
    shifts = [(14, -14), (-10, 10), (18, -6), (-8, 16), (12, -12)]
    for i in range(len(srcs)):
        rh, bh = shifts[i]
        segs.append(
            f"[c{i}]trim=start=0:duration=6,setpts=PTS-STARTPTS,"
            f"rgbashift=rh={rh}:bh={bh},"
            f"noise=c0s=12:allf=t,"
            f"eq=saturation=1.5:contrast=1.3,"
            f"setsar=1,format=yuv420p[s{i}]"
        )
    concat = "".join(f"[s{i}]" for i in range(len(srcs))) + f"concat=n={len(srcs)}:v=1:a=0[vraw]"
    final = (
        "[vraw]"
        "drawtext=fontfile='C\\:/Windows/Fonts/impact.ttf':"
        "text='ZALAMEH':fontcolor=0xF7F0E3:fontsize=200:borderw=12:bordercolor=0xD32F2F:"
        "x='(w-text_w)/2+6*sin(2*t*PI*6)':y='h/2-120+6*cos(2*t*PI*6)':"
        "enable='between(t,0,3)+between(t,12,15)+between(t,27,30)',"
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


if __name__ == "__main__":
    reel_04_vhs()
    reel_08_glitch()
    print("\nPATCH DONE.")
