"""MAGIC REEL V2 — 30s trailer with existing Zalameh teaser flashes spliced in.

Same 5-act arc, but with 6 video flashes from the teaser library punching
between acts: glitch intro, kaleidoscope, cat POV, VHS meltdown, stickers,
then a hero.mp4 outro over the final fade. Abd Almajeed soundtrack, tag t=0.
"""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

RAW = "jordan-series/magic_raw"
OUT = "jordan-series/reel-magic-v2.mp4"
TAG = "brand/audio-tag.mp3"
SONG = "tracks/abd-almajeed/abd-almajeed.mp3"
SONG_SS = 65

W, H, FPS = 1080, 1920, 30
DUR = 30.0

# Shot spec: (kind, path, ss_or_None, dur, motion_or_None)
#   kind = "img" -> image with ken burns motion
#          "vid" -> video flash, scale+crop, native motion
SHOTS = [
    # GLITCH INTRO
    ("vid", "teasers/wild-08-glitch-rgb.mp4",                                             15.0,  0.8, None),
    # ACT I — THE MYTH
    ("img", f"{RAW}/hf_20260422_082749_5f1a3336-a237-422b-9319-b8c5894c6df6.png",         None,  3.5, "push"),
    ("img", f"{RAW}/hf_20260422_083219_67714f9e-d806-4b1d-ac6b-8e6161d80c0b.png",         None,  1.3, "panright"),
    ("img", f"{RAW}/hf_20260422_083249_30c7b146-9784-45dd-8100-4ed7ac4f6ea7.png",         None,  1.2, "push"),
    ("img", f"{RAW}/hf_20260422_083333_201e77b3-49a5-4719-a7b2-8515c77f87a7.png",         None,  1.2, "push"),
    ("img", f"{RAW}/hf_20260422_083834_7d09dbba-2dd1-4195-8e69-6781c0cca997.png",         None,  1.3, "pullback"),
    # FLASH — KALEIDOSCOPE TRANSITION
    ("vid", "teasers/wild-02-mirror-kaleidoscope.mp4",                                    15.0,  0.5, None),
    # ACT II — THE STREETS
    ("img", f"{RAW}/hf_20260422_090612_1cdd70e6-18a7-428b-ae08-25835f0b0f8c.png",         None,  0.7, "pushfast"),
    ("img", f"{RAW}/hf_20260422_090956_d9da8f7e-5504-447b-a492-45d5d5c05fe6.png",         None,  0.6, "pushfast"),
    ("img", f"{RAW}/hf_20260422_090648_04e22abf-2593-423f-b6b4-86f96dfc6dc4.png",         None,  0.6, "push"),
    ("img", f"{RAW}/hf_20260422_090700_6f8bd24b-8c04-427b-8fa7-15b4cebdad6e.png",         None,  0.6, "panup"),
    ("img", f"{RAW}/hf_20260422_090748_c9fa0393-d4fa-4fb3-91a2-fc9dff8c7bde.png",         None,  0.7, "pullback"),
    # FLASH — CAT POV
    ("vid", "teasers/wild-06-cat-pov.mp4",                                                10.0,  0.5, None),
    # ACT III — THE LOVE
    ("img", f"{RAW}/hf_20260422_092751_b4aae3e3-1aa6-41a7-82e7-a5c1c7bb223a.png",         None,  1.0, "push"),
    ("img", f"{RAW}/hf_20260422_092827_866f67f2-9b4c-49d7-bc27-bece8a6c7d68.png",         None,  1.0, "hold"),
    ("img", f"{RAW}/hf_20260422_092906_7fe4980a-0516-4cc7-8e46-95413af8a9d7.png",         None,  1.0, "push"),
    ("img", f"{RAW}/hf_20260422_092945_1bcc1cd4-44c7-455a-be2c-ba72ad3653e9.png",         None,  1.0, "hold"),
    ("img", f"{RAW}/hf_20260422_093009_a8ebadf3-4d69-4d4b-a45c-73c6cf8fc804.png",         None,  0.9, "pullback"),
    # FLASH — VHS MELTDOWN
    ("vid", "teasers/wild-04-vhs-meltdown.mp4",                                           14.0,  0.4, None),
    # ACT IV — THE MEMORY (cartoon)
    ("img", f"{RAW}/hf_20260422_095519_dc9f90b2-f72a-41a6-b86a-7e9191882637.png",         None,  1.1, "push"),
    ("img", f"{RAW}/hf_20260422_095534_569791f7-c8ce-4c86-aede-82ae17ab3fa9.png",         None,  1.1, "push"),
    ("img", f"{RAW}/hf_20260422_095544_d9e08273-ac5d-44f5-a443-99d8621bb6a4.png",         None,  1.1, "panleft"),
    ("img", f"{RAW}/hf_20260422_095559_056531c0-3653-411d-9be8-89a529fa4bb5.png",         None,  1.1, "pullback"),
    # FLASH — STICKERS (levity)
    ("vid", "teasers/stickers-animation.mp4",                                              1.5,  0.3, None),
    # ACT V — THE PAYOFF
    ("img", f"{RAW}/hf_20260422_095041_19ea9ec4-7434-4cf0-b92d-69bb3537b960.png",         None,  1.5, "push"),    # match cut
    ("img", f"{RAW}/hf_20260422_095007_d2685645-acd5-4760-8f53-f39747d33582.png",         None,  1.2, "push"),
    ("img", f"{RAW}/hf_20260422_095058_5268ae75-398a-4d18-bdd0-a89305b0d884.png",         None,  2.5, "holdslow"),
    # OUTRO STINGER — hero.mp4
    ("vid", "toota/hero.mp4",                                                              5.0,  1.3, None),
]

total = sum(s[3] for s in SHOTS)
assert abs(total - DUR) < 0.05, f"bad total: {total}"
N = len(SHOTS)


def motion_filter(motion, dur):
    d_fr = int(dur * FPS)
    if motion == "push":
        speed = min(0.0025, 0.3 / d_fr)
        return (f"zoompan=z='min(1.0+on*{speed},1.22)':d={d_fr}:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
    elif motion == "pushfast":
        speed = 0.35 / d_fr
        return (f"zoompan=z='min(1.0+on*{speed},1.35)':d={d_fr}:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
    elif motion == "pullback":
        return (f"zoompan=z='if(lte(zoom,1.0),1.25,max(1.0,zoom-{0.25/d_fr}))':"
                f"d={d_fr}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
    elif motion == "panright":
        return (f"zoompan=z='1.15':d={d_fr}:"
                f"x='(iw-iw/zoom)*(on/{d_fr})':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
    elif motion == "panleft":
        return (f"zoompan=z='1.15':d={d_fr}:"
                f"x='(iw-iw/zoom)*(1-on/{d_fr})':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
    elif motion == "panup":
        return (f"zoompan=z='1.15':d={d_fr}:"
                f"x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/{d_fr})':s={W}x{H}:fps={FPS}")
    elif motion == "hold":
        return (f"zoompan=z='1.08':d={d_fr}:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
    elif motion == "holdslow":
        speed = 0.15 / d_fr
        return (f"zoompan=z='min(1.0+on*{speed},1.15)':d={d_fr}:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
    raise ValueError(motion)


# Fonts
IMPACT  = r"'C\:/Windows/Fonts/impact.ttf'"
ARIALBD = r"'C\:/Windows/Fonts/arialbd.ttf'"
ARIAL   = r"'C\:/Windows/Fonts/arial.ttf'"

# Timing map: title shows at beginning. glitch intro is 0-0.8s, so title
# should come in after the glitch: 0.8-3.2s, out by 3.6s.
TITLE_ALPHA = (
    "if(lt(t,0.9),0,"
    "if(lt(t,1.3),(t-0.9)/0.4,"
    "if(lt(t,3.2),1,"
    "if(lt(t,3.8),(3.8-t)/0.6,0))))"
)
# Socials appear after title, fade out before climax
SOC_ALPHA = (
    "if(lt(t,4.2),0,"
    "if(lt(t,5.0),(t-4.2)/0.8,"
    "if(lt(t,25.0),0.82,"
    "if(lt(t,26.2),0.82*(26.2-t)/1.2,0))))"
)

# Build video segments
img_pre = "scale=4320:7680,"
segs = []
for i, (kind, path, ss, dur, motion) in enumerate(SHOTS):
    if kind == "img":
        segs.append(
            f"[{i}:v]{img_pre}{motion_filter(motion, dur)},"
            f"trim=duration={dur},setpts=PTS-STARTPTS,"
            f"setsar=1,format=yuv420p[v{i}]"
        )
    else:  # video
        # Scale+crop to 1080x1920, force 30fps, trim duration
        segs.append(
            f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},fps={FPS},"
            f"trim=duration={dur},setpts=PTS-STARTPTS,"
            f"setsar=1,format=yuv420p[v{i}]"
        )

concat = "".join(f"[v{i}]" for i in range(N)) + f"concat=n={N}:v=1:a=0[vcat]"

drawtexts = ",".join([
    (f"drawtext=fontfile={IMPACT}:text='ZALAMEH'"
     f":fontcolor=white:fontsize=180:x=(w-text_w)/2:y=h*0.38"
     f":shadowcolor=black@0.55:shadowx=3:shadowy=5:alpha='{TITLE_ALPHA}'"),
    (f"drawtext=fontfile={ARIALBD}:text='JORDAN'"
     f":fontcolor=white:fontsize=42:x=(w-text_w)/2:y=h*0.38+200"
     f":shadowcolor=black@0.6:shadowx=2:shadowy=3:alpha='{TITLE_ALPHA}'"),
    (f"drawtext=fontfile={ARIALBD}:text='SPOTIFY   Zalameh'"
     f":fontcolor=white:fontsize=32:x=50:y=1680"
     f":shadowcolor=black@0.75:shadowx=2:shadowy=2:alpha='{SOC_ALPHA}'"),
    (f"drawtext=fontfile={ARIALBD}:text='INSTAGRAM   @zalameh.69'"
     f":fontcolor=white:fontsize=32:x=50:y=1732"
     f":shadowcolor=black@0.75:shadowx=2:shadowy=2:alpha='{SOC_ALPHA}'"),
    (f"drawtext=fontfile={ARIALBD}:text='YOUTUBE   @zalameh.69'"
     f":fontcolor=white:fontsize=32:x=50:y=1784"
     f":shadowcolor=black@0.75:shadowx=2:shadowy=2:alpha='{SOC_ALPHA}'"),
    (f"drawtext=fontfile={ARIAL}:text='zalameh.netlify.app'"
     f":fontcolor=white:fontsize=26:x=50:y=70"
     f":shadowcolor=black@0.7:shadowx=2:shadowy=2:alpha='{SOC_ALPHA}'"),
])

video_chain = (
    f"[vcat]{drawtexts},"
    f"vignette=angle=PI/5,"
    f"fade=t=out:st={DUR-0.8}:d=0.8[vout]"
)

audio = (
    f"[{N}:a]volume=enable='between(t,0,2.2)':volume=0.55[duck];"
    f"[{N+1}:a]apad=whole_dur={DUR}[tagpad];"
    f"[duck][tagpad]amix=inputs=2:duration=first:dropout_transition=0,"
    f"volume=1.4,afade=t=in:st=0:d=0.3,afade=t=out:st={DUR-2.0}:d=2.0[aout]"
)

fc = ";".join(segs) + ";" + concat + ";" + video_chain + ";" + audio

cmd = ["ffmpeg", "-y"]
for (kind, path, ss, dur, _) in SHOTS:
    if kind == "img":
        cmd += ["-loop", "1", "-t", str(dur), "-i", path]
    else:
        cmd += ["-ss", str(ss), "-t", str(dur), "-i", path]
cmd += ["-ss", str(SONG_SS), "-t", str(DUR), "-i", SONG]
cmd += ["-i", TAG]
cmd += [
    "-filter_complex", fc,
    "-map", "[vout]", "-map", "[aout]",
    "-t", str(DUR), "-r", str(FPS),
    "-c:v", "libx264", "-preset", "medium", "-crf", "19",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart",
    "-shortest",
    OUT,
]

print(f"Building MAGIC REEL v2 ({N} shots incl. 6 video flashes, {DUR}s)...")
r = subprocess.run(cmd, capture_output=True)
if r.returncode != 0:
    print("ERROR:\n" + r.stderr.decode("utf-8", errors="replace")[-3000:])
else:
    sz = os.path.getsize(OUT) / 1024 / 1024
    print(f"  -> {OUT}  ({sz:.1f} MB)")
    print("DONE.")
