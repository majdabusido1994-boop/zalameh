"""THE MAGIC REEL — 30s trailer of the Zalameh universe.

5-act arc: Myth -> Streets -> Love -> Memory -> Payoff.
22 shots, variable pacing, match-cut at the climax, socials fade before payoff.
Abd Almajeed soundtrack, Zalameh tag at t=0.
"""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

RAW = "jordan-series/magic_raw"
OUT = "jordan-series/reel-magic.mp4"
TAG = "brand/audio-tag.mp3"
SONG = "tracks/abd-almajeed/abd-almajeed.mp3"
SONG_SS = 65  # song builds to chorus at our climax

W, H, FPS = 1080, 1920, 30
DUR = 30.0

# Shot list: (image_filename, duration_seconds, motion_type)
# motion types: push, pushfast, pullback, panright, panleft, panup, hold
SHOTS = [
    # ACT I — THE MYTH (0 -> 9.5s)
    ("hf_20260422_082749_5f1a3336-a237-422b-9319-b8c5894c6df6.png", 3.5, "push"),      # Wadi Rum hero + ZALAMEH title
    ("hf_20260422_083219_67714f9e-d806-4b1d-ac6b-8e6161d80c0b.png", 1.5, "panright"),  # Dead Sea float
    ("hf_20260422_083249_30c7b146-9784-45dd-8100-4ed7ac4f6ea7.png", 1.5, "push"),      # Jerash columns standing
    ("hf_20260422_083333_201e77b3-49a5-4719-a7b2-8515c77f87a7.png", 1.5, "push"),      # Ajloun window
    ("hf_20260422_083834_7d09dbba-2dd1-4195-8e69-6781c0cca997.png", 1.5, "pullback"),  # Jerash walking
    # ACT II — THE STREETS (9.5 -> 13.7s)
    ("hf_20260422_090612_1cdd70e6-18a7-428b-ae08-25835f0b0f8c.png", 1.0, "pushfast"),  # pigeon
    ("hf_20260422_090956_d9da8f7e-5504-447b-a492-45d5d5c05fe6.png", 0.8, "pushfast"),  # cat bolting
    ("hf_20260422_090648_04e22abf-2593-423f-b6b4-86f96dfc6dc4.png", 0.8, "push"),      # cat leap
    ("hf_20260422_090700_6f8bd24b-8c04-427b-8fa7-15b4cebdad6e.png", 0.8, "panup"),     # hooded tea
    ("hf_20260422_090748_c9fa0393-d4fa-4fb3-91a2-fc9dff8c7bde.png", 0.8, "pullback"),  # sunset walk
    # ACT III — THE LOVE (13.7 -> 19.6s)
    ("hf_20260422_092751_b4aae3e3-1aa6-41a7-82e7-a5c1c7bb223a.png", 1.2, "push"),      # woman walking away
    ("hf_20260422_092827_866f67f2-9b4c-49d7-bc27-bece8a6c7d68.png", 1.1, "hold"),      # hooded w/ cat in alley
    ("hf_20260422_092906_7fe4980a-0516-4cc7-8e46-95413af8a9d7.png", 1.1, "push"),      # hand reaching
    ("hf_20260422_092945_1bcc1cd4-44c7-455a-be2c-ba72ad3653e9.png", 1.2, "hold"),      # she pauses
    ("hf_20260422_093009_a8ebadf3-4d69-4d4b-a45c-73c6cf8fc804.png", 1.3, "pullback"),  # face to face
    # ACT IV — THE MEMORY (19.6 -> 24.4s, cartoon)
    ("hf_20260422_095519_dc9f90b2-f72a-41a6-b86a-7e9191882637.png", 1.2, "push"),      # cartoon kitten rain
    ("hf_20260422_095534_569791f7-c8ce-4c86-aede-82ae17ab3fa9.png", 1.2, "push"),      # cartoon hands
    ("hf_20260422_095544_d9e08273-ac5d-44f5-a443-99d8621bb6a4.png", 1.2, "panleft"),   # cartoon wrapping
    ("hf_20260422_095559_056531c0-3653-411d-9be8-89a529fa4bb5.png", 1.2, "pullback"),  # cartoon cat doorway
    # ACT V — THE PAYOFF (24.4 -> 30s)
    ("hf_20260422_095041_19ea9ec4-7434-4cf0-b92d-69bb3537b960.png", 1.6, "push"),      # photo cat doorway (match cut!)
    ("hf_20260422_095007_d2685645-acd5-4760-8f53-f39747d33582.png", 1.4, "push"),      # man holding cat
    ("hf_20260422_095058_5268ae75-398a-4d18-bdd0-a89305b0d884.png", 2.6, "holdslow"),  # climax: three at tea
]

N = len(SHOTS)
assert abs(sum(d for _, d, _ in SHOTS) - DUR) < 0.05, f"Shot durations = {sum(d for _,d,_ in SHOTS)}"


def motion_filter(motion, dur):
    """Return zoompan filter body for a motion over a given duration."""
    d_fr = int(dur * FPS)
    if motion == "push":
        # gentle zoom in
        speed = min(0.0025, 0.3 / d_fr)
        return (f"zoompan=z='min(1.0+on*{speed},1.22)':d={d_fr}:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
    elif motion == "pushfast":
        speed = 0.35 / d_fr
        return (f"zoompan=z='min(1.0+on*{speed},1.35)':d={d_fr}:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
    elif motion == "pullback":
        # start zoomed, pull back to ~1.0
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
        # extremely slow push — for the climax
        speed = 0.15 / d_fr
        return (f"zoompan=z='min(1.0+on*{speed},1.15)':d={d_fr}:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
    raise ValueError(motion)


# Fonts
IMPACT  = r"'C\:/Windows/Fonts/impact.ttf'"
ARIALBD = r"'C\:/Windows/Fonts/arialbd.ttf'"
ARIAL   = r"'C\:/Windows/Fonts/arial.ttf'"

# Title appears with audio tag, fades with it
TITLE_ALPHA = (
    "if(lt(t,0.3),t/0.3,"
    "if(lt(t,2.0),1,"
    "if(lt(t,2.4),(2.4-t)/0.4,0)))"
)
# Socials: fade in at 3.0, hold, fade OUT at 25.5 so climax stays clean
SOC_ALPHA = (
    "if(lt(t,3.0),0,"
    "if(lt(t,3.8),(t-3.0)/0.8,"
    "if(lt(t,25.5),0.82,"
    "if(lt(t,26.5),0.82*(26.5-t)/1.0,0))))"
)

# Build video segments
pre = "scale=4320:7680,"
segs = []
for i, (img, dur, motion) in enumerate(SHOTS):
    segs.append(
        f"[{i}:v]{pre}{motion_filter(motion, dur)},"
        f"trim=duration={dur},setpts=PTS-STARTPTS,"
        f"setsar=1,format=yuv420p[v{i}]"
    )

concat = "".join(f"[v{i}]" for i in range(N)) + f"concat=n={N}:v=1:a=0[vcat]"

drawtexts = ",".join([
    # Title — centered upper-third, with audio tag
    (f"drawtext=fontfile={IMPACT}:text='ZALAMEH'"
     f":fontcolor=white:fontsize=180:x=(w-text_w)/2:y=h*0.38"
     f":shadowcolor=black@0.55:shadowx=3:shadowy=5:alpha='{TITLE_ALPHA}'"),
    (f"drawtext=fontfile={ARIALBD}:text='JORDAN'"
     f":fontcolor=white:fontsize=42:x=(w-text_w)/2:y=h*0.38+200"
     f":shadowcolor=black@0.6:shadowx=2:shadowy=3:alpha='{TITLE_ALPHA}'"),
    # Socials
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

# Video chain: overlays + global subtle vignette + fade to black at end
video_chain = (
    f"[vcat]{drawtexts},"
    f"vignette=angle=PI/5,"
    f"fade=t=out:st={DUR-0.8}:d=0.8[vout]"
)

# Audio: song duck under tag, layered, fade out
audio = (
    f"[{N}:a]volume=enable='between(t,0,2.2)':volume=0.55[duck];"
    f"[{N+1}:a]apad=whole_dur={DUR}[tagpad];"
    f"[duck][tagpad]amix=inputs=2:duration=first:dropout_transition=0,"
    f"volume=1.4,afade=t=in:st=0:d=0.3,afade=t=out:st={DUR-2.0}:d=2.0[aout]"
)

fc = ";".join(segs) + ";" + concat + ";" + video_chain + ";" + audio

# Command
cmd = ["ffmpeg", "-y"]
for (img, dur, _) in SHOTS:
    cmd += ["-loop", "1", "-t", str(dur), "-i", f"{RAW}/{img}"]
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

print(f"Building MAGIC reel ({N} shots, {DUR}s)...")
r = subprocess.run(cmd, capture_output=True)
if r.returncode != 0:
    print("ERROR:\n" + r.stderr.decode("utf-8", errors="replace")[-3000:])
else:
    sz = os.path.getsize(OUT) / 1024 / 1024
    print(f"  -> {OUT}  ({sz:.1f} MB)")
    print("DONE.")
