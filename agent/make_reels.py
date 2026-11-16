"""Keep the Reel queue full (runs daily on GitHub, see .github/workflows/make-reels.yml).

For each audience (parents -> 8 AM slot, pg -> 8 PM slot): while fewer than AHEAD Reels are waiting, take the next
hand-written script in reels/scripts/<aud>/ that hasn't been used yet (sorted by file name); if there is none, ask
Gemini to write one (agent/reel_script.py). Then build it (reelkit/build.py) and queue it:
  video  -> reel-files branch (checked out in ./reel-files)
  folder -> reels/<id>/reel.json + caption.txt on main
python agent/make_reels.py [parents|pg|both] [--ahead N] [--dry-run]
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REELS = ROOT / "reels"
SCRIPTS = REELS / "scripts"
FILES = ROOT / "reel-files"
SLOT = {"parents": "reel_morning", "pg": "reel_evening"}


def git(*args, cwd=ROOT, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {r.stdout}{r.stderr}")
    return r


def waiting(aud: str) -> int:
    n = 0
    for meta in REELS.glob("*/reel.json"):
        if meta.parent.name.startswith("_") or (meta.parent / "published.json").exists():
            continue
        if json.loads(meta.read_text(encoding="utf-8")).get("slot") == SLOT[aud]:
            n += 1
    return n


def used_scripts() -> set[str]:
    out = set()
    for meta in REELS.glob("*/reel.json"):
        s = json.loads(meta.read_text(encoding="utf-8")).get("script")
        if s:
            out.add(s)
    return out


def next_script(aud: str) -> Path | None:
    used = used_scripts()
    for f in sorted((SCRIPTS / aud).glob("*.json")):
        if f.relative_to(ROOT).as_posix() not in used:
            return f
    return None


def push_main(msg: str, paths: list[str]) -> None:
    git("add", *paths)
    git("commit", "-q", "-m", msg)
    for _ in range(3):
        if git("pull", "-q", "--rebase", "origin", "main", check=False).returncode == 0 and \
           git("push", "-q", "origin", "HEAD:main", check=False).returncode == 0:
            return
    raise RuntimeError("could not push to main")


def push_video(video: Path, reel_id: str) -> None:
    for _ in range(3):
        git("fetch", "-q", "origin", "reel-files", cwd=FILES, check=False)
        git("reset", "-q", "--hard", "origin/reel-files", cwd=FILES, check=False)
        shutil.copy2(video, FILES / f"{reel_id}.mp4")
        git("add", f"{reel_id}.mp4", cwd=FILES)
        git("commit", "-q", "-m", f"Queue {reel_id}", cwd=FILES)
        if git("push", "-q", "origin", "HEAD:reel-files", cwd=FILES, check=False).returncode == 0:
            return
    raise RuntimeError("could not push the video to reel-files")


def make_one(aud: str, dry: bool) -> None:
    script = next_script(aud)
    if script is None:
        out = subprocess.run([sys.executable, str(ROOT / "agent" / "reel_script.py"), aud], capture_output=True, text=True)
        sys.stderr.write(out.stderr)
        if out.returncode:
            raise RuntimeError(f"Gemini could not write a {aud} script")
        script = ROOT / out.stdout.strip().splitlines()[-1]
        if not dry:
            push_main(f"Reel script (Gemini): {script.stem}", [script.relative_to(ROOT).as_posix()])
    data = json.loads(script.read_text(encoding="utf-8"))
    slug = re.sub(r"[^a-z0-9]+", "-", str(data.get("title") or data["topic"]).lower()).strip("-")[:50]
    reel_id = f"{datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))):%Y-%m-%d-%H%M%S}-{slug}"
    video = ROOT / "reelkit" / "out" / f"{reel_id}.mp4"
    subprocess.run([sys.executable, str(ROOT / "reelkit" / "build.py"), str(script), str(video)], check=True)
    print(f"Built {video.name} from {script.name}")
    if dry:
        return
    push_video(video, reel_id)
    folder = REELS / reel_id
    folder.mkdir(parents=True)
    (folder / "reel.json").write_text(json.dumps({
        "slot": SLOT[aud], "thumb_ms": int(float(data.get("cover_s", 2)) * 1000), "source": f"{data.get('title', slug)}.mp4",
        "script": script.relative_to(ROOT).as_posix(), "auto_script": bool(data.get("auto")),
        "queued_at": datetime.datetime.now().isoformat(timespec="seconds")}, indent=2), encoding="utf-8")
    (folder / "caption.txt").write_text(str(data.get("caption", data["topic"])).strip() + "\n", encoding="utf-8")
    push_main(f"Queue reel {reel_id}", [folder.relative_to(ROOT).as_posix()])
    print(f"Queued {reel_id} for {SLOT[aud]}")


def main() -> None:
    args = sys.argv[1:]
    dry = "--dry-run" in args
    ahead = int(args[args.index("--ahead") + 1]) if "--ahead" in args else int(os.environ.get("AHEAD", "2"))
    which = next((a for a in args if a in ("parents", "pg", "both")), "both")
    failed = []
    for aud in (["parents", "pg"] if which == "both" else [which]):
        have = waiting(aud)
        print(f"{aud}: {have} waiting, want {ahead}")
        for _ in range(max(0, ahead - have) if not dry else 1):
            try:
                make_one(aud, dry)
            except Exception as e:  # one bad Reel must not stop the other audience
                print(f"FAILED {aud}: {e}", file=sys.stderr)
                failed.append(aud)
                break
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
