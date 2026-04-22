"""Build the CHASE narrative reel from 6 AI stills.

15s total, 6 cuts of 2.5s each, per-frame Ken Burns motion,
Zan Zan song + Zalameh audio tag at t=0,
ZALAMEH title overlay (0-2.4s) and socials overlay (2.8s-end).
"""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SRC_DIR = "jordan-series/chase"
OUT = "jordan-series/reel-chase.mp4"
TAG = "brand/audio-tag.mp3"
SONG = "tracks/zan-zan/zan-zan.mp3"
SONG_SS = 40  # seconds into song to start

W, H, FPS = 1080, 1920, 30
SEG = 2.5  # seconds per frame
SEG_FR = int(SEG * FPS)  # 75 frames
DUR = SEG * 6  # 15s

# Per-frame zoompan recipes
MOTIONS = {
    "f1": f"zoompan=z='min(1.0+on*0.004,1.3)':d={SEG_FR}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}",
    "f2": f"zoompan=z='min(1.0+on*0.0045,1.35)':d={SEG_FR}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}",
    "f3": f"zoompan=z='min(1.0+on*0.003,1.22)':d={SEG_FR}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}",
    "f4": f"zoompan=z='1.12':d={SEG_FR}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/{SEG_FR})':s={W}x{H}:fps={FPS}",
    "f5": f"zoompan=z='min(1.0+on*0.0018,1.13)':d={SEG_FR}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}",
    "f6": f"zoompan=z='if(lte(zoom,1.0),1.25,max(1.0,zoom-0.0032))':d={SEG_FR}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}",
}

# Fonts
IMPACT  = r"'C\:/Windows/Fonts/impact.ttf'"
ARIALBD = r"'C\:/Windows/Fonts/arialbd.ttf'"
ARIAL   = r"'C\:/Windows/Fonts/arial.ttf'"

TITLE_ALPHA = (
    "if(lt(t,0.3),t/0.3,"
    "if(lt(t,2.0),1,"
    "if(lt(t,2.4),(2.4-t)/0.4,0)))"
)
SOC_ALPHA = (
    "if(lt(t,2.8),0,"
    "if(lt(t,3.4),(t-2.8)/0.6,"
    f"if(lt(t,{DUR-0.6}),0.85,"
    f"if(lt(t,{DUR}),0.85*({DUR}-t)/0.6,0))))"
)

# Build the filter graph
# - 6 image inputs (loop, t=2.5 each), passed through pre_scale + zoompan
# - concat to a single video stream
# - song input trimmed
# - tag input padded
# - audio mix: duck song for 2.2s, layer tag, final volume boost
# - overlay drawtexts on the video

pre = "scale=4320:7680,"
segs = []
for i in range(6):
    segs.append(
        f"[{i}:v]{pre}{MOTIONS[f'f{i+1}']},"
        f"trim=duration={SEG},setpts=PTS-STARTPTS,"
        f"setsar=1,format=yuv420p[v{i}]"
    )

concat = "".join(f"[v{i}]" for i in range(6)) + f"concat=n=6:v=1:a=0[vcat]"

# Drawtexts chain
drawtexts = ",".join([
    (f"drawtext=fontfile={IMPACT}:text='ZALAMEH'"
     f":fontcolor=white:fontsize=180:x=(w-text_w)/2:y=h*0.38"
     f":shadowcolor=black@0.55:shadowx=3:shadowy=5:alpha='{TITLE_ALPHA}'"),
    (f"drawtext=fontfile={ARIALBD}:text='AMMAN  //  JORDAN'"
     f":fontcolor=white:fontsize=38:x=(w-text_w)/2:y=h*0.38+200"
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

audio = (
    f"[6:a]volume=enable='between(t,0,2.2)':volume=0.55[duck];"
    f"[7:a]apad=whole_dur={DUR}[tagpad];"
    f"[duck][tagpad]amix=inputs=2:duration=first:dropout_transition=0,"
    f"volume=1.4,afade=t=in:st=0:d=0.3,afade=t=out:st={DUR-1.5}:d=1.5[aout]"
)

fc = ";".join(segs) + ";" + concat + f";[vcat]{drawtexts}[vout];" + audio

cmd = [
    "ffmpeg", "-y",
    "-loop", "1", "-t", str(SEG), "-i", f"{SRC_DIR}/f1.png",
    "-loop", "1", "-t", str(SEG), "-i", f"{SRC_DIR}/f2.png",
    "-loop", "1", "-t", str(SEG), "-i", f"{SRC_DIR}/f3.png",
    "-loop", "1", "-t", str(SEG), "-i", f"{SRC_DIR}/f4.png",
    "-loop", "1", "-t", str(SEG), "-i", f"{SRC_DIR}/f5.png",
    "-loop", "1", "-t", str(SEG), "-i", f"{SRC_DIR}/f6.png",
    "-ss", str(SONG_SS), "-t", str(DUR), "-i", SONG,
    "-i", TAG,
    "-filter_complex", fc,
    "-map", "[vout]", "-map", "[aout]",
    "-t", str(DUR), "-r", str(FPS),
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart",
    "-shortest",
    OUT,
]

print("Building CHASE reel...")
r = subprocess.run(cmd, capture_output=True)
if r.returncode != 0:
    err = r.stderr.decode("utf-8", errors="replace")[-2500:]
    print("ERROR:\n" + err)
else:
    sz = os.path.getsize(OUT) / 1024 / 1024
    print(f"  -> {OUT}  ({sz:.1f} MB)")
    print("DONE.")
