"""Animate the 4 Jordan series stills into 15s reels with music + audio tag.

Ken Burns motion: slow zoom/pan per scene, each one different.
Pair each scene with a song clip, add the Zalameh audio tag at t=0.
"""
import os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

TAG = "brand/audio-tag.mp3"
OUT = "jordan-series"

W, H = 1080, 1920
DUR = 15

# Scene list: (image, motion, song_path, song_ss, out_name)
# Motion recipes use zoompan:
#   - zoom_in: scale up progressively
#   - zoom_out: start zoomed in, pull back
#   - pan_left / pan_right / pan_up
SCENES = [
    {
        "name": "Jerash",
        "img": f"{OUT}/jerash.png",
        "motion": "zoom_in_center",
        "song": "tracks/khaliki/khaliki.mp3",
        "song_ss": 40,
        "out": f"{OUT}/reel-jerash.mp4",
    },
    {
        "name": "Dead Sea",
        "img": f"{OUT}/dead-sea.png",
        "motion": "pan_right",
        "song": "tracks/khaliki/khaliki.mp3",
        "song_ss": 70,
        "out": f"{OUT}/reel-dead-sea.mp4",
    },
    {
        "name": "Ajloun",
        "img": f"{OUT}/ajloun.png",
        "motion": "zoom_in_figure",
        "song": "tracks/abd-almajeed/abd-almajeed.mp3",
        "song_ss": 109,
        "out": f"{OUT}/reel-ajloun.mp4",
    },
    {
        "name": "Wadi Rum",
        "img": f"{OUT}/wadi-rum.png",
        "motion": "zoom_out",
        "song": "tracks/zan-zan/zan-zan.mp3",
        "song_ss": 30,
        "out": f"{OUT}/reel-wadi-rum.mp4",
    },
]

# Ken Burns zoompan recipes
# fps=30, total frames = DUR*30 = 450
FPS = 30
FRAMES = DUR * FPS  # 450

def zoompan_filter(motion):
    """Return the zoompan filter string for a given motion."""
    # We first scale the source way up to avoid zoompan blur, then apply motion.
    pre_scale = "scale=4320:7680,"  # 4x target
    if motion == "zoom_in_center":
        return (
            pre_scale +
            f"zoompan=z='min(zoom+0.0008,1.25)':d={FRAMES}:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"s={W}x{H}:fps={FPS}"
        )
    elif motion == "zoom_in_figure":
        # Zoom in slightly off-center (towards right where figure stands)
        return (
            pre_scale +
            f"zoompan=z='min(zoom+0.0009,1.3)':d={FRAMES}:"
            f"x='iw/2-(iw/zoom/2)+iw*0.05':y='ih/2-(ih/zoom/2)+ih*0.03':"
            f"s={W}x{H}:fps={FPS}"
        )
    elif motion == "zoom_out":
        # Start zoomed in, pull back — use reverse trick with decreasing zoom
        return (
            pre_scale +
            f"zoompan=z='if(lte(zoom,1.0),1.25,max(1.0,zoom-0.0006))':d={FRAMES}:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"s={W}x{H}:fps={FPS}"
        )
    elif motion == "pan_right":
        # Zoom slight + pan x from left to right
        return (
            pre_scale +
            f"zoompan=z='1.15':d={FRAMES}:"
            f"x='(iw-iw/zoom)*(on/{FRAMES})':y='ih/2-(ih/zoom/2)':"
            f"s={W}x{H}:fps={FPS}"
        )
    elif motion == "pan_left":
        return (
            pre_scale +
            f"zoompan=z='1.15':d={FRAMES}:"
            f"x='(iw-iw/zoom)*(1-on/{FRAMES})':y='ih/2-(ih/zoom/2)':"
            f"s={W}x{H}:fps={FPS}"
        )
    elif motion == "pan_up":
        return (
            pre_scale +
            f"zoompan=z='1.15':d={FRAMES}:"
            f"x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/{FRAMES})':"
            f"s={W}x{H}:fps={FPS}"
        )
    else:
        return (
            pre_scale +
            f"zoompan=z='1.1':d={FRAMES}:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"s={W}x{H}:fps={FPS}"
        )


def build(scene):
    print(f"\n=== {scene['name']} — {scene['motion']} ===")
    motion_fc = zoompan_filter(scene["motion"])
    # Audio: song clip + audio tag layered at t=0, song ducked for 2.2s
    # Inputs: 0=image loop (15s), 1=song, 2=tag
    fc = (
        f"[0:v]{motion_fc},setsar=1,format=yuv420p[vout];"
        f"[1:a]volume=enable='between(t,0,2.2)':volume=0.55[duck];"
        f"[2:a]apad=whole_dur={DUR}[tagpad];"
        f"[duck][tagpad]amix=inputs=2:duration=first:dropout_transition=0,"
        f"volume=1.4,afade=t=in:st=0:d=0.3,afade=t=out:st={DUR-1.5}:d=1.5[aout]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", str(DUR), "-i", scene["img"],
        "-ss", str(scene["song_ss"]), "-t", str(DUR), "-i", scene["song"],
        "-i", TAG,
        "-filter_complex", fc,
        "-map", "[vout]", "-map", "[aout]",
        "-t", str(DUR), "-r", str(FPS),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        scene["out"],
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERROR:")
        print(r.stderr[-1500:])
        return False
    sz = os.path.getsize(scene["out"]) / 1024 / 1024
    print(f"  -> {scene['out']}  ({sz:.1f} MB)")
    return True


for s in SCENES:
    build(s)
print("\nALL DONE.")
