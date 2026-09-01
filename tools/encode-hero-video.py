#!/usr/bin/env python3
"""Cut a licensed stock clip down to a hero loop the page can actually afford.

Reference point: phariahealth.com ships its splash at 8.5MB and 7.7Mbps for
8.75 seconds. That is a fifth of a second of hero on a slow connection costing
more than the rest of the page put together. This targets 2MB for the mp4,
which on the same 8 seconds is roughly 2Mbps - still clean at hero scale,
because a backdrop sitting under a scrim is never inspected closely.

    python3 tools/encode-hero-video.py SOURCE.mov --name workshop
    python3 tools/encode-hero-video.py SOURCE.mov --name workshop \\
        --start 00:00:12 --duration 8 --tint 1C2B33 --saturation 0.35

--seamless N crossfades the last N seconds into the first N, so a clip whose
camera drifts (every Veo clip does, whatever the prompt says) loops without a
visible jump. The output is N seconds shorter than --duration.

Writes <name>.mp4 and <name>-poster.jpg under assets/hero (or --dest, e.g.
work/_assets/hero/roofing for a reference build). H.264 plays in every
browser; --webm adds a VP9 copy, which on Veo output came out *larger* than
the mp4 at matching quality and so is off by default. Audio is stripped
unconditionally - an autoplaying hero is muted by policy anyway, and the
track is dead weight.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEST = REPO / "assets" / "hero"

# 1920 is the widest the hero is ever painted at; a 4K source buys nothing once
# it sits behind a scrim at 90% opacity.
WIDTH = 1920
DURATION = 8
# CRF chosen so a 7-second Veo 1080p clip lands under 2MB (33 gave 1.78MB on
# the roofing pilot; 26, the first setting, gave 7.3MB). A backdrop under a
# scrim is never inspected closely. Grain-heavy or high-motion sources will
# still overshoot - the script says so rather than guessing.
H264_CRF = 33
VP9_CRF = 36
BUDGET_MB = 2.0
# Veo and most stock render at 24; a backdrop gains nothing from more.
LOOP_FPS = 24
# Hue offsets survive the trip to colorbalance small; without a multiplier a
# muted tint like 1C2B33 moves the midtones by a couple of percent and reads
# as no grade at all.
TINT_STRENGTH = 2.0


def run(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit("ffmpeg failed:\n%s" % proc.stderr[-2000:])
    return proc


def grade_filter(tint, saturation, width=WIDTH):
    """Pull toward a single hue, which is the whole trick behind the reference.

    Saturation comes down first, then colorbalance pushes the midtones toward
    the tint. Doing it in that order keeps skin from going magenta, which is
    what happens if you tint a fully saturated frame.
    """
    steps = ["scale=%d:-2:flags=lanczos" % width]
    if saturation is not None:
        steps.append("eq=saturation=%.3f" % saturation)
    if tint:
        r, g, b = (int(tint[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
        # Only the channels' offsets *from each other* carry hue. Measuring each
        # against neutral grey instead would push all three the same way on a
        # dark tint, which darkens the midtones rather than colouring them.
        mean = (r + g + b) / 3.0
        steps.append("colorbalance=rm=%.3f:gm=%.3f:bm=%.3f" % (
            (r - mean) * TINT_STRENGTH,
            (g - mean) * TINT_STRENGTH,
            (b - mean) * TINT_STRENGTH))
    return ",".join(steps)


def loop_filter(vf, duration, seamless):
    """Crossfade the tail into the head so the loop point disappears.

    A = seconds [seamless, duration) of the cut, B = seconds [0, seamless).
    xfade blends A's last `seamless` seconds into B, so the final frame is
    (nearly) the frame at t=seamless - which is exactly where A began.
    """
    body = duration - seamless
    # xfade refuses input it cannot prove is constant-rate, and trim strips
    # that proof - so fps is pinned *after* each trim, not before the split.
    return ("[0:v]%s,split[x][y];"
            "[x]trim=%f:%f,setpts=PTS-STARTPTS,fps=%d[a];"
            "[y]trim=0:%f,setpts=PTS-STARTPTS,fps=%d[b];"
            "[a][b]xfade=transition=fade:duration=%f:offset=%f[v]"
            % (vf, seamless, duration, LOOP_FPS, seamless, LOOP_FPS,
               seamless, body - seamless))


def encode(source, name, start, duration, vf, dest, seamless, h264_crf, vp9_crf,
           want_webm):
    dest.mkdir(parents=True, exist_ok=True)
    mp4 = dest / ("%s.mp4" % name)
    webm = dest / ("%s.webm" % name)
    poster = dest / ("%s-poster.jpg" % name)

    # -ss before -i seeks on keyframes, which is fast and accurate enough for a
    # backdrop; putting it after would decode everything up to the in point.
    cut = ["-ss", start, "-t", str(duration)]
    if seamless:
        picture = ["-filter_complex", loop_filter(vf, duration, seamless), "-map", "[v]"]
    else:
        picture = ["-vf", vf]

    run(["ffmpeg", "-v", "error", "-y", *cut, "-i", str(source),
         "-an", *picture, "-c:v", "libx264", "-profile:v", "high",
         "-crf", str(h264_crf), "-preset", "slow", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", str(mp4)])

    outputs = [mp4]
    if want_webm:
        run(["ffmpeg", "-v", "error", "-y", *cut, "-i", str(source),
             "-an", *picture, "-c:v", "libvpx-vp9", "-crf", str(vp9_crf),
             "-b:v", "0", "-row-mt", "1", "-deadline", "good", str(webm)])
        outputs.append(webm)

    # Poster is pulled from the graded mp4, not the source, so it matches the
    # first frame the visitor sees instead of flashing an ungraded plate.
    run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4),
         "-frames:v", "1", "-q:v", "6", str(poster)])

    return outputs + [poster]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    ap.add_argument("--name", required=True, help="output basename, e.g. workshop")
    ap.add_argument("--start", default="00:00:00")
    ap.add_argument("--duration", type=float, default=DURATION)
    ap.add_argument("--tint", help="6-digit hex to push midtones toward, e.g. 1C2B33")
    ap.add_argument("--saturation", type=float, default=None,
                    help="0 is greyscale, 1 leaves it alone. Try 0.3-0.5.")
    ap.add_argument("--dest", type=Path, default=DEST,
                    help="output folder (default assets/hero)")
    ap.add_argument("--seamless", type=float, default=0,
                    help="crossfade this many seconds of tail into head")
    ap.add_argument("--webm", action="store_true", help="also write a VP9 webm")
    ap.add_argument("--width", type=int, default=WIDTH,
                    help="output width; 1280 makes a phone cut of a 1920 hero")
    ap.add_argument("--h264-crf", type=int, default=H264_CRF)
    ap.add_argument("--vp9-crf", type=int, default=VP9_CRF)
    args = ap.parse_args()
    if args.seamless and args.seamless * 2 >= args.duration:
        sys.exit("--seamless must be under half of --duration")

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not on PATH: brew install ffmpeg")
    if not args.source.exists():
        sys.exit("no such source: %s" % args.source)
    if args.tint:
        args.tint = args.tint.lstrip("#")
        if len(args.tint) != 6:
            sys.exit("--tint wants 6 hex digits, got %r" % args.tint)

    vf = grade_filter(args.tint, args.saturation, args.width)
    print("filter: %s" % vf)
    outputs = encode(args.source, args.name, args.start, args.duration, vf,
                     args.dest.resolve(), args.seamless, args.h264_crf, args.vp9_crf,
                     args.webm)

    over = False
    for path in outputs:
        mb = path.stat().st_size / 1024 / 1024
        flag = ""
        if path.suffix in (".mp4", ".webm") and mb > BUDGET_MB:
            flag, over = "  OVER BUDGET", True
        shown = path.relative_to(REPO) if path.is_relative_to(REPO) else path
        print("%-42s %6.2f MB%s" % (shown, mb, flag))

    if over:
        print("\nRaise H264_CRF/VP9_CRF or shorten --duration. High-motion and "
              "grain-heavy sources are the usual cause; a slower, tighter shot "
              "encodes far smaller than a wide with a moving camera.")


if __name__ == "__main__":
    main()
