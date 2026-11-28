#!/usr/bin/env python3
"""The ONLY command the gatesmith role may run (r10, security review of gatesmith.py): it inspects a render without
giving the agent a free ffmpeg/tesseract command line, so it cannot choose output paths or write anywhere.
Outputs go to a fixed per-user temp directory.
  gatesmith_probe.py info   <mp4>                          duration, size, fps
  gatesmith_probe.py frames <mp4> <t0> <t1> [fps=2] [crop=x:y:w:h]   PNGs into the fixed dir, prints their paths
  gatesmith_probe.py ocr    <png-from-that-dir> [psm=6]    tesseract text of one extracted frame"""
import json, re, subprocess, sys, tempfile
from pathlib import Path

OUT = Path(tempfile.gettempdir()) / "ttm_gatesmith_probe"


def main() -> int:
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "info":
        pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", args[0]],
                                       capture_output=True, text=True, check=True).stdout)
        v = next(s for s in pr["streams"] if s["codec_type"] == "video")
        print(json.dumps(dict(duration=float(pr["format"]["duration"]), w=v["width"], h=v["height"], fps=v["r_frame_rate"])))
    elif cmd == "frames":
        mp4, t0, t1 = args[0], float(args[1]), float(args[2])
        fps = float(args[3]) if len(args) > 3 else 2.0
        crop = args[4] if len(args) > 4 else ""
        if crop and not re.fullmatch(r"\d+:\d+:\d+:\d+", crop):
            sys.exit("crop must be x:y:w:h")
        OUT.mkdir(parents=True, exist_ok=True)
        for p in OUT.glob("f_*.png"):
            p.unlink()
        x, y, w, h = crop.split(":") if crop else ("", "", "", "")
        vf = f"fps={fps}" + (f",crop={w}:{h}:{x}:{y}" if crop else "")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-to", str(t1), "-i", mp4, "-vf", vf, str(OUT / "f_%04d.png")], check=True)
        for p in sorted(OUT.glob("f_*.png")):
            print(p)
    elif cmd == "ocr":
        png = Path(args[0]).resolve()
        if png.parent != OUT.resolve():
            sys.exit(f"ocr only reads frames extracted into {OUT}")
        psm = args[1] if len(args) > 1 else "6"
        if psm not in ("3", "6", "7", "11"):
            sys.exit("psm must be 3, 6, 7 or 11")
        print(subprocess.run(["tesseract", str(png), "-", "--psm", psm], capture_output=True, text=True).stdout)
    else:
        sys.exit(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
