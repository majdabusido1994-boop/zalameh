"""Build the ABD ALMAJEED origin story reel (animated chars on real backgrounds).

15s total, 5 cuts of 3s each, slow emotional motion,
Abd Almajeed song + Zalameh audio tag at t=0,
ZALAMEH title overlay (0-2.4s) and socials overlay (2.8s-end).
"""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SRC_DIR = "jordan-series/abd_anim"
OUT = "jordan-series/reel-abd-anim.mp4"
TAG = "brand/audio-tag.mp3"
SONG = "tracks/abd-almajeed/abd-almajeed.mp3"
SONG_SS = 45

W, H, FPS = 1080, 1920, 30
SEG = 3.0
SEG_FR = int(SEG * FPS)  # 90
DUR = SEG * 5  # 15

MOTIONS = {
    "f1": f"zoompan=z='min(1.0+on*0.0022,1.2)':d={SEG_FR}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}",
    "f2": f"zoompan=z='min(1.0+on*0.0018,1.16)':d={SEG_FR}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}",
    "f3": f"zoompan=z='1.12':d={SEG_FR}:x='(iw-iw/zoom)*(1-on/{SEG_FR})':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}",
    "f4": f"zoompan=z='if(lte(zoom,1.0),1.25,max(1.0,zoom-0.0022))':d={SEG_FR}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}",
    "f5": f"zoompan=z='if(lte(zoom,1.0),1.2,max(1.0,zoom-0.0018))':d={SEG_FR}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}",
}

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

pre = "scale=4320:7680,"
segs = []
N = 5
for i in range(N):
    segs.append(
        f"[{i}:v]{pre}{MOTIONS[f'f{i+1}']},"
        f"trim=duration={SEG},setpts=PTS-STARTPTS,"
        f"setsar=1,format=yuv420p[v{i}]"
    )

concat = "".join(f"[v{i}]" for i in range(N)) + f"concat=n={N}:v=1:a=0[vcat]"

drawtexts = ",".join([
    (f"drawtext=fontfile={IMPACT}:text='ZALAMEH'"
     f":fontcolor=white:fontsize=180:x=(w-text_w)/2:y=h*0.38"
     f":shadowcolor=black@0.55:shadowx=3:shadowy=5:alpha='{TITLE_ALPHA}'"),
    (f"drawtext=fontfile={ARIALBD}:text='ABD ALMAJEED'"
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
    f"[{N}:a]volume=enable='between(t,0,2.2)':volume=0.55[duck];"
    f"[{N+1}:a]apad=whole_dur={DUR}[tagpad];"
    f"[duck][tagpad]amix=inputs=2:duration=first:dropout_transition=0,"
    f"volume=1.4,afade=t=in:st=0:d=0.3,afade=t=out:st={DUR-1.5}:d=1.5[aout]"
)

fc = ";".join(segs) + ";" + concat + f";[vcat]{drawtexts}[vout];" + audio

cmd = ["ffmpeg", "-y"]
for i in range(N):
    cmd += ["-loop", "1", "-t", str(SEG), "-i", f"{SRC_DIR}/f{i+1}.png"]
cmd += ["-ss", str(SONG_SS), "-t", str(DUR), "-i", SONG]
cmd += ["-i", TAG]
cmd += [
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

print("Building ABD ALMAJEED (animated) reel...")
r = subprocess.run(cmd, capture_output=True)
if r.returncode != 0:
    print("ERROR:\n" + r.stderr.decode("utf-8", errors="replace")[-2500:])
else:
    sz = os.path.getsize(OUT) / 1024 / 1024
    print(f"  -> {OUT}  ({sz:.1f} MB)")
    print("DONE.")
