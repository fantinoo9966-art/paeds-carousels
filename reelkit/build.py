"""Turn a Reel script (JSON) into a finished, Instagram-ready MP4 with original music.

python reelkit/build.py <script.json> <out.mp4> [--browser <chrome-headless-shell path>]

Steps: Remotion render (SFX inside) -> compose music (music.py, bright for parents, lo-fi for PG)
-> mix (SFX -17 LUFS, music -21) -> loudnorm -14 LUFS -> H.264 yuv420p crf 18 + faststart.
Also writes <out>.caption.txt (from the script's "caption") and prints the cover time in seconds.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd)[:300], flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip().split(",")[0])


def build(script_path: Path, out: Path, browser: str | None = None) -> None:
    script = json.loads(script_path.read_text(encoding="utf-8"))
    pg = script.get("audience") == "pg"
    seed = int(script.get("seed", 0))
    tmp = Path(tempfile.mkdtemp(prefix="reel-"))
    try:
        props = tmp / "props.json"
        # Invisible joiners (word joiner, zero-width space, BOM) have no glyph in Baloo/Nunito and render as boxes.
        clean = json.dumps(script, ensure_ascii=False)
        for ch in ("⁠", "​", "﻿", "‌", "‍"):
            clean = clean.replace(ch, "")
        props.write_text(clean, encoding="utf-8")
        raw = tmp / "raw.mp4"
        npx = shutil.which("npx") or shutil.which("npx.cmd") or "npx"
        cmd = [npx, "remotion", "render", "src/index.ts", "Reel", raw, f"--props={props}", "--codec", "h264", "--crf", "16", "--log=error"]
        if browser:
            cmd.append(f"--browser-executable={browser}")
        run(cmd, cwd=KIT)

        dur = duration(raw)
        music = tmp / "music.wav"
        transpose = [0, 2, -1, 3, -2, 1][seed % 6]
        run([sys.executable, KIT / "music.py", "lofi" if pg else "bright", f"{dur + 0.5:.1f}", music, seed + 3, transpose])

        fade = max(0.0, dur - 2)
        filt = (f"[0:a]loudnorm=I=-17:TP=-2[s];[1:a]atrim=0:{dur:.3f},afade=t=out:st={fade:.3f}:d=2,loudnorm=I=-21:TP=-2[m];"
                f"[s][m]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5[a]")
        out.parent.mkdir(parents=True, exist_ok=True)
        run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-i", music, "-filter_complex", filt, "-map", "0:v", "-map", "[a]",
             "-vf", "scale=in_range=full:out_range=tv,format=yuv420p", "-c:v", "libx264", "-crf", "18", "-profile:v", "high",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out])
        if script.get("caption"):
            out.with_suffix(".caption.txt").write_text(script["caption"].strip() + "\n", encoding="utf-8")
        print(f"Built {out} ({duration(out):.1f} s)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    browser = None
    if "--browser" in args:
        i = args.index("--browser")
        browser = args[i + 1]
        del args[i:i + 2]
    build(Path(args[0]).resolve(), Path(args[1]).resolve(), browser)
